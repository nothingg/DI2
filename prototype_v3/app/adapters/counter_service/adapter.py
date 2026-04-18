from __future__ import annotations

from app.adapters.base import BillerAdapter
from app.adapters.counter_service import flows, schema
from app.browser.manager import BrowserManager
from app.core.config import AppSettings
from app.core.errors import NoDataError, PartialDataError
from app.core.models import JobContext
from app.services.artifact_service import save_failure_artifacts
from app.services.sftp_service import download_file as download_sftp_file


class CounterServiceAdapter(BillerAdapter):
    biller_name = "counter_service"

    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.browser_manager = BrowserManager(settings=settings)

    def run(self, context: JobContext, log) -> None:
        session = None
        try:
            session = self.browser_manager.open_session(context, log)
            flows.login(session.page, self.settings, log)
            download_result = flows.download_web_reports(
                session.page,
                self.settings,
                context.run_date,
                context.temp_dir,
                log,
            )
            flows.logout(session.page, self.settings, log)

            if self.settings.counter_service_fetch_servu:
                filename = schema.build_indcr_filename(context.run_date)
                log(f"Downloading Counter Service SFTP file: {filename}")
                download_sftp_file(
                    settings=self.settings,
                    remote_dir=self.settings.counter_service_servu_path,
                    filename=filename,
                    local_dir=context.temp_dir,
                    rename_on_conflict=True,
                )
            else:
                log("Skipping Counter Service SFTP download because COUNTER_SERVICE_FETCH_SERVU is disabled")

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
                include_servu=self.settings.counter_service_fetch_servu,
            )
            log("Counter Service workflow completed")
        except (NoDataError, PartialDataError):
            if session is not None:
                flows.logout(session.page, self.settings, log)
            raise
        except Exception:
            save_failure_artifacts(
                page=session.page if session else None,
                artifact_dir=context.artifact_dir,
                job_id=context.job_id,
                biller=context.biller,
                run_date=context.run_date.isoformat(),
                log_file=context.log_file,
                log=log,
            )
            raise
        finally:
            if session is not None:
                if self.settings.keep_browser_open:
                    self.browser_manager.preserve_session(session, log)
                else:
                    session.close()
