from __future__ import annotations

from app.adapters.base import BillerAdapter
from app.adapters.lotus import flows, schema
from app.browser.manager import BrowserManager
from app.core.config import AppSettings
from app.core.errors import NoDataError, PartialDataError
from app.core.models import JobContext
from app.services.artifact_service import save_failure_artifacts
from app.services.sftp_service import download_file as download_sftp_file


class LotusAdapter(BillerAdapter):
    biller_name = "lotus"

    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.browser_manager = BrowserManager(settings=settings)

    def run(self, context: JobContext, log) -> None:
        session = None
        logout_attempted = False

        def attempt_logout() -> None:
            nonlocal logout_attempted
            if session is None or logout_attempted:
                return
            logout_attempted = True
            flows.logout(session.page, self.settings, log)

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
            attempt_logout()

            if self.settings.lotus_fetch_servu:
                for filename in schema.build_servu_filenames(context.run_date):
                    log(f"Downloading Lotus SFTP file: {filename}")
                    download_sftp_file(
                        settings=self.settings,
                        remote_dir=self.settings.lotus_servu_path,
                        filename=filename,
                        local_dir=context.temp_dir,
                    )
            else:
                log("Skipping Lotus SFTP download because LOTUS_FETCH_SERVU is disabled")

            if download_result.availability.required_missing:
                raise PartialDataError(
                    flows.build_partial_data_message(
                        context.run_date,
                        download_result.availability.required_available,
                        download_result.availability.required_missing,
                        [],
                    )
                )

            flows.validate_downloads(
                context.temp_dir,
                [path.name for path in download_result.downloaded_files],
                include_servu=self.settings.lotus_fetch_servu,
                run_date=context.run_date,
            )
            log("Lotus workflow completed")
        except (NoDataError, PartialDataError):
            attempt_logout()
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
            attempt_logout()
            raise
        finally:
            if session is not None:
                if self.settings.keep_browser_open:
                    self.browser_manager.preserve_session(session, log)
                else:
                    session.close()
