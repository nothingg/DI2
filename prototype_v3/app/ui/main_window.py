from __future__ import annotations

import logging

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
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.adapters.lotus_tims import schema as lotus_tims_schema
from app.core.config import AppSettings
from app.core.models import JobRequest, JobResult, JobStatus
from app.ui.worker import JobWorker


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class MainWindow(QMainWindow):
    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self.settings = settings
        self.worker: JobWorker | None = None

        self.setWindowTitle(settings.app_name)
        self.resize(760, 520)

        self.biller_combo = QComboBox()
        self.biller_combo.addItems(["mpay", "lotus_tims"])

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate().addDays(-1))
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.dateChanged.connect(self._refresh_date_hint)

        self.date_hint_label = QLabel()
        self.date_hint_label.setWordWrap(True)

        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self._start_job)

        self.status_label = QLabel("Idle")
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)

        form = QFormLayout()
        form.addRow("Biller", self.biller_combo)
        form.addRow("Run Date", self.date_edit)
        form.addRow("", self.date_hint_label)

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

        self.biller_combo.currentTextChanged.connect(self._refresh_date_hint)
        self._refresh_date_hint()

    def _start_job(self) -> None:
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Busy", "A job is already running.")
            return

        request = JobRequest(
            biller=self.biller_combo.currentText(),
            run_date=self.date_edit.date().toPython(),
        )
        self.log_output.clear()
        self._append_log(
            f"Preparing job for biller={request.biller}, date={request.run_date.isoformat()}"
        )
        if request.biller == "lotus_tims":
            lookup_date = lotus_tims_schema.build_lookup_date(request.run_date)
            self._append_log(
                "Lotus TIMS business date mapping: "
                f"selected run date={request.run_date.isoformat()}, "
                f"document lookup date={lookup_date.isoformat()}"
            )
        self.status_label.setText("Running")
        self.run_button.setEnabled(False)

        self.worker = JobWorker(self.settings, request)
        self.worker.log_emitted.connect(self._append_log)
        self.worker.finished_with_result.connect(self._finish_job)
        self.worker.start()

    def _finish_job(self, result: JobResult) -> None:
        self.run_button.setEnabled(True)
        if result.status == JobStatus.SUCCESS:
            self.status_label.setText("Success")
            self._append_log(f"Completed job {result.job_id}")
            self._append_log(f"Output: {result.output_dir}")
            self._append_log(f"Log file: {result.log_file}")
            for output_file in result.files:
                self._append_log(f"File: {output_file.path}")
        elif result.status == JobStatus.NO_DATA:
            self.status_label.setText("No Data")
            self._append_log(f"Log file: {result.log_file}")
            QMessageBox.information(self, "No Data", result.error or "No data was found.")
        else:
            self.status_label.setText("Failed")
            self._append_log(f"Job failed: {result.error}")
            self._append_log(f"Log file: {result.log_file}")
            QMessageBox.critical(self, "Job Failed", result.error or "Unknown error")

    def _append_log(self, message: str) -> None:
        self.log_output.appendPlainText(message)

    def _refresh_date_hint(self) -> None:
        biller = self.biller_combo.currentText()
        run_date = self.date_edit.date().toPython()

        if biller == "lotus_tims":
            lookup_date = lotus_tims_schema.build_lookup_date(run_date)
            self.date_hint_label.setText(
                "Lotus TIMS uses the selected date as the business date and searches "
                f"for the document dated {lookup_date.isoformat()} (next day). "
                "If no row exists for that document date, the run will return No Data."
            )
            return

        self.date_hint_label.setText(
            "Run Date is the date that will be used for this biller."
        )


def run_app() -> None:
    configure_logging()
    settings = AppSettings.load()
    app = QApplication([])
    window = MainWindow(settings=settings)
    window.show()
    app.exec()
