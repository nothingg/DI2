from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from pathlib import Path


class JobStatus(str, Enum):
    SUCCESS = "success"
    NO_DATA = "no_data"
    FAILED = "failed"


@dataclass(slots=True)
class JobRequest:
    biller: str
    run_date: date


@dataclass(slots=True)
class JobContext:
    biller: str
    run_date: date
    job_id: str
    temp_dir: Path
    artifact_dir: Path
    output_dir: Path
    log_file: Path
    browser_mode: str


@dataclass(slots=True)
class OutputFile:
    path: Path
    name: str


@dataclass(slots=True)
class JobResult:
    status: JobStatus
    job_id: str
    biller: str
    run_date: date
    output_dir: Path
    log_file: Path
    files: list[OutputFile] = field(default_factory=list)
    error: str | None = None


def build_job_id(biller: str, run_date: date) -> str:
    timestamp = datetime.now().strftime("%H%M%S")
    return f"{biller}_{run_date.isoformat()}_{timestamp}"
