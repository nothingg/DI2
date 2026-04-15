from __future__ import annotations

from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.config import AppSettings
from app.core.models import JobRequest, JobResult, JobStatus
from app.infra.logging_setup import configure_logging
from app.ui.worker import JobWorker


class MainWindow(QMainWindow):
    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self.settings = settings
        self.worker: JobWorker | None = None
        self.setWindowTitle(settings.app_name)
        self.resize(760, 520)

        self.biller_combo = QComboBox()
        self.biller_combo.addItems(["mpay"])

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate().addDays(-1))
        self.date_edit.setDisplayFormat("yyyy-MM-dd")

        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self._start_job)

        self.status_label = QLabel("Idle")
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)

        form = QFormLayout()
        form.addRow("Biller", self.biller_combo)
        form.addRow("Run Date", self.date_edit)

        button_row = QHBoxLayout()
        button_row.addWidget(self.run_button)
        button_row.addWidget(self.status_label)
        button_row.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(button_row)
        layout.addWidget(self.log_output)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _start_job(self) -> None:
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Busy", "A job is already running.")
            return

        run_date = self.date_edit.date().toPython()
        request = JobRequest(
            biller=self.biller_combo.currentText(),
            run_date=run_date,
        )

        self.log_output.clear()
        self._append_log(
            f"Preparing job for biller={request.biller}, date={request.run_date.isoformat()}"
        )
        self.status_label.setText("Running")
        self.run_button.setEnabled(False)

        self.worker = JobWorker(settings=self.settings, request=request)
        self.worker.log_emitted.connect(self._append_log)
        self.worker.finished_with_result.connect(self._finish_job)
        self.worker.start()

    def _finish_job(self, result: JobResult) -> None:
        self.run_button.setEnabled(True)
        if result.status == JobStatus.SUCCESS:
            self.status_label.setText("Success")
            self._append_log(f"Completed job {result.job_id}")
            self._append_log(f"Output: {result.output_dir}")
            if result.artifacts:
                for artifact in result.artifacts:
                    self._append_log(f"File: {artifact.path}")
        else:
            self.status_label.setText("Failed")
            self._append_log(f"Job failed: {result.error}")
            QMessageBox.critical(self, "Job Failed", result.error or "Unknown error")

    def _append_log(self, message: str) -> None:
        self.log_output.appendPlainText(message)


def run_app() -> None:
    settings = AppSettings.load()
    configure_logging(settings.base_dir / "logs")
    app = QApplication([])
    window = MainWindow(settings=settings)
    window.show()
    app.exec()
