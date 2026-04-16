from __future__ import annotations

import logging
from collections.abc import Callable

from app.adapters.base import BillerAdapter
from app.adapters.lotus_tims.adapter import LotusTimsAdapter
from app.adapters.mpay.adapter import MpayAdapter
from app.core.config import AppSettings
from app.core.errors import NoDataError
from app.core.models import JobContext, JobRequest, JobResult, JobStatus, build_job_id
from app.services.file_service import ensure_dir, list_files, move_to_output, require_files
from app.services.log_service import JobLogger


LogFn = Callable[[str], None]


class JobRunner:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.logger = logging.getLogger(self.__class__.__name__)
        self.adapters: dict[str, BillerAdapter] = {
            "lotus_tims": LotusTimsAdapter(settings=settings),
            "mpay": MpayAdapter(settings=settings),
        }

    def run(self, request: JobRequest, log: LogFn) -> JobResult:
        context = self._build_context(request)
        adapter = self._get_adapter(request.biller)
        job_logger = JobLogger(context.log_file, log)

        ensure_dir(context.temp_dir)
        ensure_dir(context.artifact_dir)
        ensure_dir(context.output_dir.parent)
        ensure_dir(context.log_file.parent)

        job_logger.emit(f"Job created: {context.job_id}")
        job_logger.emit(f"Temp dir: {context.temp_dir}")
        job_logger.emit(f"Artifact dir: {context.artifact_dir}")
        job_logger.emit(f"Output dir: {context.output_dir}")
        job_logger.emit(f"Log file: {context.log_file}")
        job_logger.emit(f"Browser mode: {context.browser_mode}")

        try:
            adapter.run(context, job_logger.emit)
            files = list_files(context.temp_dir)
            require_files(files)
            output_files = move_to_output(context.temp_dir, context.output_dir)
            job_logger.emit(f"Moved {len(output_files)} file(s) to output")
            return JobResult(
                status=JobStatus.SUCCESS,
                job_id=context.job_id,
                biller=context.biller,
                run_date=context.run_date,
                output_dir=context.output_dir,
                log_file=context.log_file,
                files=output_files,
            )
        except NoDataError as exc:
            job_logger.emit(f"No data: {exc}")
            return JobResult(
                status=JobStatus.NO_DATA,
                job_id=context.job_id,
                biller=context.biller,
                run_date=context.run_date,
                output_dir=context.output_dir,
                log_file=context.log_file,
                error=str(exc),
            )
        except Exception as exc:
            self.logger.exception("Job failed: %s", context.job_id)
            job_logger.emit_exception("Job failed", exc)
            return JobResult(
                status=JobStatus.FAILED,
                job_id=context.job_id,
                biller=context.biller,
                run_date=context.run_date,
                output_dir=context.output_dir,
                log_file=context.log_file,
                error=str(exc),
            )

    def _build_context(self, request: JobRequest) -> JobContext:
        job_id = build_job_id(request.biller, request.run_date)
        job_root = self.settings.run_root / job_id
        return JobContext(
            biller=request.biller,
            run_date=request.run_date,
            job_id=job_id,
            temp_dir=job_root / "temp",
            artifact_dir=job_root / "artifacts",
            output_dir=self.settings.output_root / request.biller / request.run_date.isoformat(),
            log_file=self.settings.base_dir / "logs" / f"{job_id}.log",
            browser_mode=self.settings.resolve_browser_mode(request.biller),
        )

    def _get_adapter(self, biller: str) -> BillerAdapter:
        return self.adapters[biller]
