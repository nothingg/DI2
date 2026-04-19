from __future__ import annotations

from app.adapters.base import BillerAdapter
from app.adapters.lotus_tims import flows, schema
from app.browser.manager import BrowserManager
from app.core.config import AppSettings
from app.core.errors import NoDataError
from app.core.models import JobContext
from app.services.artifact_service import save_failure_artifacts


class LotusTimsAdapter(BillerAdapter):
    biller_name = "lotus_tims"

    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.browser_manager = BrowserManager(settings=settings)

    def run(self, context: JobContext, log) -> None:
        session = None
        logout_attempted = False
        lookup_date = schema.build_lookup_date(context.run_date)

        def attempt_logout() -> None:
            nonlocal logout_attempted
            if session is None or logout_attempted:
                return
            logout_attempted = True
            flows.logout(session.page, self.settings, log)

        try:
            log(
                "Lotus TIMS business date mapping: "
                f"selected run date={context.run_date.isoformat()}, "
                f"document lookup date={lookup_date.isoformat()}"
            )
            session = self.browser_manager.open_session(context, log)
            flows.login(session.page, self.settings, log)
            flows.accept_post_login_prompt(session.page, self.settings, log)
            flows.open_payment_detail_menu(session.page, self.settings, log)
            flows.search_documents(session.page, self.settings, log)
            download_path = flows.download_report(
                session.page,
                self.settings,
                context.run_date,
                context.temp_dir,
                log,
            )
            attempt_logout()
            log(f"Lotus TIMS workflow completed: {download_path.name}")
        except NoDataError:
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
