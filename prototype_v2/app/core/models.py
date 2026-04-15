from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from pathlib import Path


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_FOR_USER = "waiting_for_user"
    VALIDATING = "validating"
    SUCCESS = "success"
    FAILED = "failed"


class BrowserMode(str, Enum):
    MANAGED = "managed"
    REAL_PROFILE = "real_profile"


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
    browser_mode: BrowserMode


@dataclass(slots=True)
class DownloadArtifact:
    name: str
    path: Path


@dataclass(slots=True)
class JobResult:
    status: JobStatus
    job_id: str
    biller: str
    run_date: date
    output_dir: Path
    artifacts: list[DownloadArtifact] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    error: str | None = None


def build_job_id(biller: str, run_date: date) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{biller}_{run_date.isoformat()}"
