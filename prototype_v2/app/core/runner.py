from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime

from app.adapters.base import BillerAdapter
from app.adapters.mpay import MpayAdapter
from app.core.config import AppSettings
from app.core.models import BrowserMode, JobContext, JobRequest, JobResult, JobStatus, build_job_id
from app.infra.files import ensure_dir, list_files, move_to_output, require_files


LogFn = Callable[[str], None]


class JobRunner:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.logger = logging.getLogger(self.__class__.__name__)
        self.adapters: dict[str, BillerAdapter] = {
            "mpay": MpayAdapter(settings=settings),
        }

    def run(self, request: JobRequest, log: LogFn) -> JobResult:
        adapter = self.adapters[request.biller]
        job_id = build_job_id(request.biller, request.run_date)
        job_root = self.settings.run_root / job_id
        temp_dir = job_root / "temp"
        artifact_dir = job_root / "artifacts"
        output_dir = self.settings.output_root / request.biller / request.run_date.isoformat()
        context = JobContext(
            biller=request.biller,
            run_date=request.run_date,
            job_id=job_id,
            temp_dir=temp_dir,
            artifact_dir=artifact_dir,
            output_dir=output_dir,
            browser_mode=self.settings.browser_mode,
        )

        ensure_dir(temp_dir)
        ensure_dir(artifact_dir)
        ensure_dir(output_dir.parent)

        self.logger.info("Job started: %s", job_id)
        log(f"Job created: {job_id}")
        log(f"Temp dir: {temp_dir}")
        log(f"Artifact dir: {artifact_dir}")
        log(f"Output dir: {output_dir}")

        try:
            adapter.run(context, log)
            log("Validating downloaded files")
            files = list_files(temp_dir)
            require_files(files)
            artifacts = move_to_output(temp_dir, output_dir)
            log(f"Moved {len(artifacts)} file(s) to output")
            result = JobResult(
                status=JobStatus.SUCCESS,
                job_id=job_id,
                biller=request.biller,
                run_date=request.run_date,
                output_dir=output_dir,
                artifacts=artifacts,
            )
            self.logger.info("Job succeeded: %s", job_id)
            return result
        except Exception as exc:
            self.logger.exception("Job failed: %s", job_id)
            return JobResult(
                status=JobStatus.FAILED,
                job_id=job_id,
                biller=request.biller,
                run_date=request.run_date,
                output_dir=output_dir,
                error=str(exc),
            )
