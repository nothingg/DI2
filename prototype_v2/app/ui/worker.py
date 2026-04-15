from __future__ import annotations

from PySide6.QtCore import QThread, Signal

from app.core.config import AppSettings
from app.core.models import JobRequest, JobResult
from app.core.runner import JobRunner


class JobWorker(QThread):
    log_emitted = Signal(str)
    finished_with_result = Signal(object)

    def __init__(self, settings: AppSettings, request: JobRequest) -> None:
        super().__init__()
        self.settings = settings
        self.request = request

    def run(self) -> None:
        runner = JobRunner(settings=self.settings)
        result = runner.run(self.request, self.log_emitted.emit)
        self.finished_with_result.emit(result)
