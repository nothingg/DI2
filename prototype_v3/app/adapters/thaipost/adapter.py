from __future__ import annotations

from app.adapters.base import BillerAdapter
from app.adapters.thaipost import flows, schema
from app.core.config import AppSettings
from app.core.errors import NoDataError, PartialDataError
from app.core.models import JobContext
from app.services.artifact_service import save_failure_artifacts
from app.services.sftp_service import download_file as download_sftp_file


class ThaiPostAdapter(BillerAdapter):
    biller_name = "thaipost"

    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings

    def run(self, context: JobContext, log) -> None:
        try:
            download_result = flows.download_ftp_reports(
                self.settings,
                context.run_date,
                context.temp_dir,
                log,
            )

            if self.settings.thaipost_fetch_servu:
                for filename in schema.build_required_filenames(context.run_date):
                    log(f"Downloading Thai Post SFTP file: {filename}")
                    download_sftp_file(
                        settings=self.settings,
                        remote_dir=self.settings.thaipost_servu_path,
                        filename=filename,
                        local_dir=context.temp_dir,
                        rename_on_conflict=True,
                        log=log,
                    )
            else:
                log("Skipping Thai Post SFTP download because THAIPOST_FETCH_SERVU is disabled")

            if download_result.availability.required_missing:
                raise PartialDataError(
                    flows.build_partial_data_message(
                        context.run_date,
                        download_result.availability,
                    )
                )

            flows.validate_downloads(
                context.temp_dir,
                context.run_date,
                include_servu=self.settings.thaipost_fetch_servu,
            )
            log("Thai Post workflow completed")
        except (NoDataError, PartialDataError):
            raise
        except Exception:
            save_failure_artifacts(
                page=None,
                artifact_dir=context.artifact_dir,
                job_id=context.job_id,
                biller=context.biller,
                run_date=context.run_date.isoformat(),
                log_file=context.log_file,
                log=log,
            )
            raise
