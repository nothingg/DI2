from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from time import sleep
from urllib.parse import urlparse
from urllib.request import urlopen

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from app.core.config import AppSettings
from app.core.errors import BrowserError
from app.core.models import JobContext
from app.services.file_service import ensure_dir

_PRESERVED_SESSIONS: list["BrowserSession"] = []
_MANUAL_START_URLS = {
    "lotus": "https://easypay.lotuss.com/TescoBPBiller/logon.jsf",
}


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
                try:
                    return self._connect_manual_browser(playwright, cdp_url, log)
                except Exception as exc:
                    if self.settings.resolve_user_data_dir(job.biller) is None:
                        raise
                    log(
                        "Manual Chrome CDP connection failed; "
                        f"trying to open Chrome with the configured profile: {exc}"
                    )
                    try:
                        self._launch_manual_chrome_for_cdp(job, cdp_url, log)
                        return self._connect_manual_browser(playwright, cdp_url, log)
                    except Exception as launch_exc:
                        log(
                            "Could not open and attach to manual Chrome via CDP; "
                            f"falling back to the configured Chrome profile: {launch_exc}"
                        )
                        return self._open_real_profile(playwright, job, log)
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

    def _chrome_executable(self) -> str:
        if self.settings.real_chrome_executable:
            return self.settings.real_chrome_executable

        executable = shutil.which("chrome") or shutil.which("chrome.exe")
        if executable:
            return executable

        candidates = [
            Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
            Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)

        raise BrowserError("Chrome executable was not found. Set REAL_CHROME_EXECUTABLE to the Chrome path.")

    @staticmethod
    def _cdp_port(cdp_url: str) -> int:
        parsed = urlparse(cdp_url)
        if parsed.port:
            return parsed.port
        raise BrowserError(f"Manual Chrome CDP URL must include a port: {cdp_url}")

    def _launch_manual_chrome_for_cdp(self, job: JobContext, cdp_url: str, log) -> None:
        user_data_dir = self.settings.resolve_user_data_dir(job.biller)
        if user_data_dir is None:
            raise BrowserError(f"No Chrome user data dir is configured for {job.biller}.")

        ensure_dir(user_data_dir)
        port = self._cdp_port(cdp_url)
        chrome_executable = self._chrome_executable()
        start_url = _MANUAL_START_URLS.get(job.biller, "about:blank")
        log(f"Opening manual Chrome with remote debugging on port {port}")
        log(f"Chrome user data dir: {user_data_dir}")
        subprocess.Popen(
            [
                chrome_executable,
                f"--remote-debugging-port={port}",
                f"--user-data-dir={user_data_dir}",
                "--no-first-run",
                "--no-default-browser-check",
                "--new-window",
                start_url,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        for attempt in range(1, 11):
            try:
                with urlopen(f"{cdp_url.rstrip('/')}/json/version", timeout=1):
                    pass
                return
            except Exception:
                if attempt == 10:
                    raise
                sleep(1)

    def _connect_manual_browser(self, playwright: Playwright, cdp_url: str, log) -> BrowserSession:
        log(f"Connecting to manual Chrome via CDP: {cdp_url}")
        browser = playwright.chromium.connect_over_cdp(cdp_url)
        if not browser.contexts:
            raise BrowserError("Manual Chrome did not expose any browser contexts.")
        context = browser.contexts[0]
        pages = context.pages
        page = next((candidate for candidate in pages if "easypay.lotuss.com" in candidate.url), None)
        blank_page = next((candidate for candidate in reversed(pages) if candidate.url == "about:blank"), None)
        if page is None:
            page = blank_page
        if page is None:
            page = pages[-1] if pages else context.new_page()
        page.bring_to_front()
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
