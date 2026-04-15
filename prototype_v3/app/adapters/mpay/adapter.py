from __future__ import annotations

from app.adapters.base import BillerAdapter
from app.adapters.mpay import flows
from app.browser.manager import BrowserManager
from app.core.config import AppSettings
from app.core.models import JobContext
from app.services.artifact_service import save_failure_artifacts
from app.services.sftp_service import download_file as download_sftp_file


class MpayAdapter(BillerAdapter):
    biller_name = "mpay"

    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.browser_manager = BrowserManager(settings=settings)

    def run(self, context: JobContext, log) -> None:
        session = None
        viewer_page = None
        try:
            session = self.browser_manager.open_session(context, log)
            flows.login(session.page, self.settings, log)
            flows.download_text_report(session.page, self.settings, context.run_date, context.temp_dir, log)
            viewer_page = flows.open_xml_viewer(session.page, self.settings, context.run_date, log)
            flows.try_download_pdf_from_viewer(
                viewer_page,
                self.settings,
                context.run_date,
                context.temp_dir,
                log,
            )
            session.page.bring_to_front()
            flows.logout(session.page, self.settings, log)

            if self.settings.mpay_fetch_servu:
                servu_filename = flows.schema.build_servu_filename(context.run_date)
                log(f"Downloading mPay SFTP file: {servu_filename}")
                download_sftp_file(
                    settings=self.settings,
                    remote_dir=self.settings.mpay_servu_path,
                    filename=servu_filename,
                    local_dir=context.temp_dir,
                )
                flows.validate_downloads_with_servu(context.temp_dir, context.run_date)
            else:
                log("Skipping mPay SFTP download because MPAY_FETCH_SERVU is disabled")
                flows.validate_downloads(context.temp_dir, context.run_date)

            log("mPay workflow completed")
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
