from __future__ import annotations

from dataclasses import dataclass
from time import sleep

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from app.core.config import AppSettings
from app.core.errors import BrowserError
from app.core.models import JobContext
from app.services.file_service import ensure_dir

_PRESERVED_SESSIONS: list["BrowserSession"] = []


@dataclass(slots=True)
class BrowserSession:
    playwright: Playwright
    browser: Browser | None
    context: BrowserContext
    page: Page
    external_browser: bool = False

    def close(self) -> None:
        if not self.external_browser:
            self.context.close()
            if self.browser is not None:
                self.browser.close()
        self.playwright.stop()


class BrowserManager:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings

    def open_session(self, job: JobContext, log) -> BrowserSession:
        playwright = sync_playwright().start()
        try:
            cdp_url = self.settings.resolve_cdp_url(job.biller)
            if job.browser_mode == "manual_assisted" and cdp_url:
                return self._connect_manual_browser(playwright, cdp_url, log)
            if job.browser_mode in {"real_profile", "manual_assisted"}:
                return self._open_real_profile(playwright, job, log)
            return self._open_managed(playwright, job, log)
        except Exception as exc:
            log(f"Browser session creation failed: {exc}")
            playwright.stop()
            raise BrowserError("Failed to create browser session.") from exc

    def _open_managed(self, playwright: Playwright, job: JobContext, log) -> BrowserSession:
        log("Opening managed browser session")
        browser = playwright.chromium.launch(
            channel=self.settings.chrome_channel,
            headless=self.settings.headless,
            slow_mo=self.settings.playwright_slow_mo_ms,
        )
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        return BrowserSession(playwright=playwright, browser=browser, context=context, page=page)

    def _open_real_profile(self, playwright: Playwright, job: JobContext, log) -> BrowserSession:
        user_data_dir = self.settings.resolve_user_data_dir(job.biller) or job.temp_dir / "chrome-profile"
        ensure_dir(user_data_dir)
        if job.browser_mode == "manual_assisted":
            log("Opening manual-assisted browser session with a real Chrome profile")
        else:
            log("Opening real-profile browser session")
        log(f"Chrome user data dir: {user_data_dir}")
        launch_kwargs = {
            "channel": self.settings.chrome_channel,
            "headless": False,
            "accept_downloads": True,
            "downloads_path": str(job.temp_dir),
            "slow_mo": self.settings.playwright_slow_mo_ms,
        }
        if self.settings.real_chrome_executable:
            launch_kwargs["executable_path"] = self.settings.real_chrome_executable

        context = None
        for attempt in range(1, 4):
            try:
                context = playwright.chromium.launch_persistent_context(str(user_data_dir), **launch_kwargs)
                break
            except Exception as exc:
                if "Browser.getWindowForTarget" not in str(exc) or attempt == 3:
                    raise
                log(f"Chrome window was not ready after launch; retrying browser startup ({attempt}/3)")
                sleep(2)

        if context is None:
            raise BrowserError("Failed to create real-profile browser context.")
        page = context.new_page()
        return BrowserSession(playwright=playwright, browser=None, context=context, page=page)

    def _connect_manual_browser(self, playwright: Playwright, cdp_url: str, log) -> BrowserSession:
        log(f"Connecting to manual Chrome via CDP: {cdp_url}")
        browser = playwright.chromium.connect_over_cdp(cdp_url)
        if not browser.contexts:
            raise BrowserError("Manual Chrome did not expose any browser contexts.")
        context = browser.contexts[0]
        pages = context.pages
        page = next((candidate for candidate in pages if "easypay.lotuss.com" in candidate.url), None)
        if page is None:
            page = pages[0] if pages else context.new_page()
        return BrowserSession(
            playwright=playwright,
            browser=browser,
            context=context,
            page=page,
            external_browser=True,
        )

    def preserve_session(self, session: BrowserSession, log) -> None:
        _PRESERVED_SESSIONS.append(session)
        log("Keeping browser open for manual review/logout")
