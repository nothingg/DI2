from __future__ import annotations

from datetime import date
from pathlib import Path

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from app.actions.browser_actions import click_after_hover
from app.actions.forms import click, fill_text
from app.actions.waits import wait_for_network_idle, wait_for_page_ready, wait_for_visible, wait_step_delay
from app.adapters.mpay import locators, schema
from app.browser.downloads import ensure_download_exists, save_download
from app.core.config import AppSettings
from app.core.errors import ConfigurationError, DownloadError, LoginError, ValidationError
from app.services.file_service import list_files

DEFAULT_TIMEOUT_MS = 10000
POPUP_TIMEOUT_MS = 5000
DOWNLOAD_TIMEOUT_MS = 15000


def pause(page: Page, settings: AppSettings, log, reason: str) -> None:
    seconds = settings.step_delay_seconds
    if seconds <= 0:
        return
    log(f"Waiting {seconds} second(s): {reason}")
    wait_step_delay(page, seconds)


def login(page: Page, settings: AppSettings, log) -> None:
    if not settings.mpay_username or not settings.mpay_password:
        raise ConfigurationError("Missing MPAY_USERNAME or MPAY_PASSWORD.")

    log("Opening mPay login page")
    page.goto(locators.LOGIN_URL, wait_until="domcontentloaded")
    wait_for_page_ready(page)

    try:
        wait_for_visible(page, locators.USERNAME_INPUT, timeout_ms=DEFAULT_TIMEOUT_MS)
        wait_for_visible(page, locators.PASSWORD_INPUT, timeout_ms=DEFAULT_TIMEOUT_MS)
        fill_text(page, locators.USERNAME_INPUT, settings.mpay_username)
        fill_text(page, locators.PASSWORD_INPUT, settings.mpay_password)
        click(page, locators.LOGIN_BUTTON)
        wait_for_network_idle(page)
        wait_for_visible(page, locators.POST_LOGIN_READY, timeout_ms=DEFAULT_TIMEOUT_MS)
        log("Login submitted")
        pause(page, settings, log, "after login")
    except Exception as exc:
        raise LoginError("Failed during mPay login flow.") from exc


def open_text_menu(page: Page, settings: AppSettings, log) -> None:
    log("Opening text report menu")
    wait_for_visible(page, locators.MAIN_MENU, timeout_ms=DEFAULT_TIMEOUT_MS)
    click_after_hover(page, locators.MAIN_MENU, locators.TEXT_MENU)
    wait_for_page_ready(page)
    pause(page, settings, log, "after opening text menu")


def download_text_report(page: Page, settings: AppSettings, run_date: date, temp_dir: Path, log) -> Path:
    file_name = schema.build_text_filename(run_date)
    log(f"Downloading text report: {file_name}")
    report_locator = f"a[href*='{file_name}']"
    try:
        open_text_menu(page, settings, log)
        wait_for_visible(page, report_locator, timeout_ms=DEFAULT_TIMEOUT_MS)
        with page.expect_download(timeout=DOWNLOAD_TIMEOUT_MS) as download_info:
            page.locator(report_locator).first.click()
        download = download_info.value
        path = save_download(download, temp_dir)
        ensure_download_exists(path)
        pause(page, settings, log, "after downloading text report")
        return path
    except Exception as exc:
        raise DownloadError(f"Failed to download text report: {file_name}") from exc


def open_xml_menu(page: Page, settings: AppSettings, log) -> None:
    log("Opening XML report menu")
    wait_for_visible(page, locators.MAIN_MENU, timeout_ms=DEFAULT_TIMEOUT_MS)
    click_after_hover(page, locators.MAIN_MENU, locators.XML_MENU)
    wait_for_page_ready(page)
    pause(page, settings, log, "after opening XML menu")


def open_xml_viewer(page: Page, settings: AppSettings, run_date: date, log) -> Page:
    file_name = schema.build_xml_filename(run_date)
    log(f"Opening XML viewer for: {file_name}")
    xml_view_selector = schema.build_xml_view_selector(run_date)
    try:
        open_xml_menu(page, settings, log)
        wait_for_visible(page, xml_view_selector, timeout_ms=DEFAULT_TIMEOUT_MS)
        xml_view_button = page.locator(xml_view_selector).first

        with page.expect_popup(timeout=POPUP_TIMEOUT_MS) as popup_info:
            xml_view_button.click()
        popup = popup_info.value
        popup.wait_for_load_state("domcontentloaded")
        log("mPay XML viewer opened in a popup window")
        pause(popup, settings, log, "after opening XML viewer")
        return popup
    except Exception as exc:
        raise DownloadError(f"Failed to open XML viewer for: {file_name}") from exc


def try_download_pdf_from_viewer(
    viewer_page: Page,
    settings: AppSettings,
    run_date: date,
    temp_dir: Path,
    log,
) -> Path | None:
    pdf_trigger_selector = locators.VIEWER_PDF_BUTTON
    xml_name = schema.build_xml_filename(run_date)

    try:
        wait_for_visible(viewer_page, pdf_trigger_selector, timeout_ms=DEFAULT_TIMEOUT_MS)
        log(f"Trying automatic PDF download from viewer for: {xml_name}")
        with viewer_page.expect_download(timeout=DOWNLOAD_TIMEOUT_MS) as download_info:
            viewer_page.locator(pdf_trigger_selector).first.click()
        download = download_info.value
        path = save_download(download, temp_dir)
        ensure_download_exists(path)
        pause(viewer_page, settings, log, "after downloading PDF from viewer")
        log(f"Automatic PDF download succeeded: {path.name}")
        return path
    except PlaywrightTimeoutError:
        log("Automatic PDF download did not trigger a browser download event")
        log("Leaving viewer tab open for manual PDF download")
        return None
    except Exception as exc:
        log(f"Automatic PDF download failed with a non-fatal error: {exc}")
        log("Leaving viewer tab open for manual PDF download")
        return None


def validate_downloads(temp_dir: Path, run_date: date) -> None:
    files = {path.name for path in list_files(temp_dir)}
    expected = {
        schema.build_text_filename(run_date),
    }
    missing = expected - files
    if missing:
        raise ValidationError(f"Missing expected downloaded files: {', '.join(sorted(missing))}")


def logout(page: Page, settings: AppSettings, log) -> None:
    try:
        wait_for_visible(page, locators.LOGOUT_LINK, timeout_ms=3000)
        log("Logging out from mPay")
        click(page, locators.LOGOUT_LINK)
        pause(page, settings, log, "after logout")
    except Exception as exc:
        # Logout is best-effort because some test runs intentionally keep the browser open.
        log(f"Skipping mPay logout due to a non-fatal error: {exc}")


def validate_downloads_with_servu(temp_dir: Path, run_date: date) -> None:
    files = {path.name for path in list_files(temp_dir)}
    expected = {
        schema.build_text_filename(run_date),
        schema.build_servu_filename(run_date),
    }
    missing = expected - files
    if missing:
        raise ValidationError(f"Missing expected downloaded files: {', '.join(sorted(missing))}")
