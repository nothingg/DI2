from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from pathlib import Path
import traceback

from app.services.file_service import ensure_dir


LogFn = Callable[[str], None]


class JobLogger:
    def __init__(self, log_file: Path, emit_ui_log: LogFn) -> None:
        self.log_file = log_file
        self.emit_ui_log = emit_ui_log
        ensure_dir(log_file.parent)
        self.log_file.write_text("", encoding="utf-8")

    def emit(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"{timestamp} {message}"
        with self.log_file.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        self.emit_ui_log(line)

    def emit_exception(self, prefix: str, exc: Exception) -> None:
        self.emit(f"{prefix}: {exc}")
        stack = traceback.format_exc().rstrip()
        if not stack:
            stack = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)).rstrip()
        with self.log_file.open("a", encoding="utf-8") as handle:
            handle.write(stack + "\n")
