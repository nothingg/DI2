from __future__ import annotations

from datetime import date
from pathlib import Path

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from app.adapters.base import BillerAdapter, LogFn
from app.core.config import AppSettings
from app.core.errors import ConfigurationError, DownloadError, LoginError
from app.core.models import BrowserMode, JobContext
from app.infra.files import ensure_dir, list_files


class MpayAdapter(BillerAdapter):
    biller_name = "mpay"

    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings

    def run(self, context: JobContext, log: LogFn) -> None:
        if not self.settings.mpay_username or not self.settings.mpay_password:
            raise ConfigurationError("Missing MPAY_USERNAME or MPAY_PASSWORD in environment.")

        ensure_dir(context.temp_dir)
        log("Starting Playwright session")
        with sync_playwright() as playwright:
            browser, browser_context = self._open_context(playwright, context, log)
            page: Page | None = None
            try:
                page = browser_context.new_page()
                self._login(page, log)
                self._download_text_report(page, context.run_date, context.temp_dir, log)
                self._download_xml_report(page, context.run_date, context.temp_dir, log)
                self._validate_downloads(context.temp_dir)
                log("mPay workflow completed")
            except Exception:
                self._capture_debug_artifacts(page, context, log)
                raise
            finally:
                browser_context.close()
                if browser is not None:
                    browser.close()

    def _open_context(
        self,
        playwright: Playwright,
        context: JobContext,
        log: LogFn,
    ) -> tuple[Browser | None, BrowserContext]:
        if context.browser_mode == BrowserMode.REAL_PROFILE:
            user_data_dir = context.temp_dir / "chrome-profile"
            ensure_dir(user_data_dir)
            log("Opening persistent Chrome profile for manual-assisted mode")
            launch_kwargs = {
                "channel": "chrome",
                "headless": False,
                "accept_downloads": True,
                "downloads_path": str(context.temp_dir),
                "slow_mo": self.settings.playwright_slow_mo_ms,
            }
            if self.settings.real_chrome_executable:
                launch_kwargs["executable_path"] = self.settings.real_chrome_executable
            persistent_context = playwright.chromium.launch_persistent_context(
                str(user_data_dir),
                **launch_kwargs,
            )
            return None, persistent_context

        browser = playwright.chromium.launch(
            channel="chrome",
            headless=self.settings.headless,
            slow_mo=self.settings.playwright_slow_mo_ms,
        )
        browser_context = browser.new_context(
            accept_downloads=True,
            base_url="https://mpaystation.ais.co.th",
        )
        return browser, browser_context

    def _login(self, page: Page, log: LogFn) -> None:
        log("Opening mPay login page")
        page.goto(
            "https://mpaystation.ais.co.th/AISPayStationGenWeb/authenUser?command=start",
            wait_until="domcontentloaded",
        )

        try:
            page.locator("input[name='username']").fill(self.settings.mpay_username or "")
            page.locator("input[name='password']").fill(self.settings.mpay_password or "")
            page.locator("input[name='login']").click()
            page.wait_for_load_state("networkidle")
            log("Login submitted")
        except Exception as exc:
            raise LoginError("Failed during mPay login flow.") from exc

    def _download_text_report(
        self,
        page: Page,
        run_date: date,
        temp_dir: Path,
        log: LogFn,
    ) -> None:
        dated_token = run_date.strftime("%Y%m%d")
        log(f"Downloading text report for {dated_token}")
        try:
            page.locator("a[href='#']").first.hover()
            page.locator("a[href='/AISPayStationGenWeb/text']").click()
            with page.expect_download() as download_info:
                page.locator(f"a[href*='AIS{dated_token}.log']").click()
            download = download_info.value
            download.save_as(str(temp_dir / download.suggested_filename))
        except Exception as exc:
            raise DownloadError(f"Failed to download mPay text report for {dated_token}.") from exc

    def _download_xml_report(
        self,
        page: Page,
        run_date: date,
        temp_dir: Path,
        log: LogFn,
    ) -> None:
        dated_token = run_date.strftime("%Y%m%d")
        log(f"Downloading XML report for {dated_token}")
        try:
            page.locator("a[href='#']").first.hover()
            page.locator("a[href='/AISPayStationGenWeb/report']").click()
            with page.expect_download() as download_info:
                page.locator(f"input[onclick*='AIS{dated_token}.xml']").click()
            download = download_info.value
            download.save_as(str(temp_dir / download.suggested_filename))
        except Exception as exc:
            raise DownloadError(f"Failed to download mPay XML report for {dated_token}.") from exc

    def _validate_downloads(self, temp_dir: Path) -> None:
        files = list_files(temp_dir)
        if not files:
            raise DownloadError("mPay finished without downloaded files.")

    def _capture_debug_artifacts(self, page: Page | None, context: JobContext, log: LogFn) -> None:
        if page is None:
            meta_path = context.artifact_dir / "failure-meta.txt"
            meta_path.write_text(
                "\n".join(
                    [
                        f"job_id={context.job_id}",
                        f"biller={context.biller}",
                        f"run_date={context.run_date.isoformat()}",
                        "url=<page_not_created>",
                    ]
                ),
                encoding="utf-8",
            )
            log(f"Saved failure metadata: {meta_path}")
            return

        screenshot_path = context.artifact_dir / "failure-screenshot.png"
        html_path = context.artifact_dir / "failure-page.html"
        meta_path = context.artifact_dir / "failure-meta.txt"

        try:
            page.screenshot(path=str(screenshot_path), full_page=True)
            log(f"Saved screenshot: {screenshot_path}")
        except Exception as exc:
            log(f"Failed to save screenshot: {exc}")

        try:
            html_path.write_text(page.content(), encoding="utf-8")
            log(f"Saved HTML snapshot: {html_path}")
        except Exception as exc:
            log(f"Failed to save HTML snapshot: {exc}")

        try:
            meta_path.write_text(
                "\n".join(
                    [
                        f"job_id={context.job_id}",
                        f"biller={context.biller}",
                        f"run_date={context.run_date.isoformat()}",
                        f"url={page.url}",
                    ]
                ),
                encoding="utf-8",
            )
            log(f"Saved failure metadata: {meta_path}")
        except Exception as exc:
            log(f"Failed to save failure metadata: {exc}")
