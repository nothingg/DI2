from __future__ import annotations

from app.adapters.baac import flows, schema
from app.adapters.base import BillerAdapter
from app.browser.manager import BrowserManager
from app.core.config import AppSettings
from app.core.errors import NoDataError, PartialDataError
from app.core.models import JobContext
from app.services.artifact_service import save_failure_artifacts
from app.services.sftp_service import download_file as download_sftp_file


class BaacAdapter(BillerAdapter):
    biller_name = "baac"

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
            flows.download_web_reports(
                session.page,
                self.settings,
                context.run_date,
                context.temp_dir,
                log,
            )
            attempt_logout()

            if self.settings.baac_fetch_servu:
                filename = schema.build_servu_filename(context.run_date)
                log(f"Downloading BAAC SFTP file: {filename}")
                try:
                    download_sftp_file(
                        settings=self.settings,
                        remote_dir=self.settings.baac_servu_path,
                        filename=filename,
                        local_dir=context.temp_dir,
                        log=log,
                    )
                except Exception as exc:
                    raise PartialDataError(
                        "BAAC web files were downloaded but the SFTP file could not be downloaded: "
                        f"{filename}"
                    ) from exc
            else:
                log("Skipping BAAC SFTP download because BAAC_FETCH_SERVU is disabled")

            flows.validate_downloads(
                context.temp_dir,
                context.run_date,
                include_servu=self.settings.baac_fetch_servu,
            )
            log("BAAC workflow completed")
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
