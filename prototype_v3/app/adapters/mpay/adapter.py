from __future__ import annotations

from app.adapters.base import BillerAdapter
from app.adapters.mpay import flows
from app.browser.manager import BrowserManager
from app.core.config import AppSettings
from app.core.errors import NoDataError, PartialDataError
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
        logout_attempted = False

        def attempt_logout() -> None:
            nonlocal logout_attempted
            if session is None or logout_attempted:
                return
            logout_attempted = True
            flows.logout(session.page, self.settings, log)

        try:
            session = self.browser_manager.open_session(context, log)
            flows.login(session.page, self.settings, log, context.artifact_dir)
            missing_items: list[str] = []
            available_items: list[str] = []
            no_data_details: list[str] = []

            text_report_path = flows.download_text_report(
                session.page,
                self.settings,
                context.run_date,
                context.temp_dir,
                log,
            )
            if text_report_path is None:
                missing_items.append("text report")
                no_data_details.append(flows.summarize_available_text_dates(session.page))
            else:
                available_items.append("text report")

            viewer_page = flows.open_xml_viewer(session.page, self.settings, context.run_date, log)
            if viewer_page is None:
                missing_items.append("xml report")
                no_data_details.append(flows.summarize_available_xml_dates(session.page))
            else:
                available_items.append("xml report")
                flows.try_download_pdf_from_viewer(
                    viewer_page,
                    self.settings,
                    context.run_date,
                    context.temp_dir,
                    log,
                )
                session.page.bring_to_front()

            attempt_logout()

            if missing_items and not available_items:
                raise NoDataError(
                    flows.build_no_data_message(
                        run_date=context.run_date,
                        missing_items=missing_items,
                        details=no_data_details,
                    )
                )
            if missing_items and available_items:
                raise PartialDataError(
                    flows.build_partial_data_message(
                        run_date=context.run_date,
                        available_items=available_items,
                        missing_items=missing_items,
                        details=no_data_details,
                    )
                )

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
        except NoDataError:
            attempt_logout()
            raise
        except PartialDataError:
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
