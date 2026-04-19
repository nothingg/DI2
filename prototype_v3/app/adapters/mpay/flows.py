from __future__ import annotations

from datetime import date
from pathlib import Path
import re
from time import monotonic

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from app.actions.browser_actions import click_after_hover
from app.actions.forms import click, fill_text
from app.actions.waits import wait_for_network_idle, wait_for_page_ready, wait_for_visible, wait_step_delay
from app.adapters.mpay import locators, schema
from app.browser.downloads import ensure_download_exists, save_download
from app.core.config import AppSettings
from app.core.errors import ConfigurationError, DownloadError, LoginError, NoDataError, PartialDataError, ValidationError
from app.services.file_service import list_files

DEFAULT_TIMEOUT_MS = 10000
POPUP_TIMEOUT_MS = 5000
DOWNLOAD_TIMEOUT_MS = 15000
TEXT_DATE_PATTERN = re.compile(r"AIS(\d{8})\.log", re.IGNORECASE)
XML_DATE_PATTERN = re.compile(r"AIS(\d{8})\.xml", re.IGNORECASE)
LOGIN_POLL_MS = 250
LOGIN_ERROR_MARKERS = (
    "invalid",
    "incorrect",
    "wrong",
    "fail",
    "try again",
    "not match",
    "not valid",
)
LOGIN_AUTHORIZATION_MARKERS = (
    "authorization",
    "ไม่มี authorization",
)


def pause(page: Page, settings: AppSettings, log, reason: str) -> None:
    seconds = settings.step_delay_seconds
    if seconds <= 0:
        return
    log(f"Waiting {seconds} second(s): {reason}")
    wait_step_delay(page, seconds)


def _save_login_transition_artifacts(
    artifact_dir: Path,
    screenshot_bytes: bytes | None,
    html_content: str | None,
    url: str | None,
    log,
) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)

    if screenshot_bytes is not None:
        screenshot_path = artifact_dir / "login-transition-screenshot.png"
        screenshot_path.write_bytes(screenshot_bytes)
        log(f"Saved mPay login transition screenshot: {screenshot_path}")

    if html_content is not None:
        html_path = artifact_dir / "login-transition-page.html"
        html_path.write_text(html_content, encoding="utf-8")
        log(f"Saved mPay login transition HTML snapshot: {html_path}")

    if url is not None:
        meta_path = artifact_dir / "login-transition-meta.txt"
        meta_path.write_text(f"url={url}\n", encoding="utf-8")
        log(f"Saved mPay login transition metadata: {meta_path}")


def _capture_login_transition(page: Page) -> tuple[bytes | None, str | None, str | None]:
    screenshot_bytes: bytes | None = None
    html_content: str | None = None
    url: str | None = None

    try:
        screenshot_bytes = page.screenshot(full_page=True)
    except Exception:
        screenshot_bytes = None

    try:
        html_content = page.content()
    except Exception:
        html_content = None

    try:
        url = page.url
    except Exception:
        url = None

    return screenshot_bytes, html_content, url


def summarize_available_text_dates(page: Page) -> str:
    dates: list[str] = []
    links = page.locator("a[href*='AIS'][href*='.log']")
    for index in range(links.count()):
        href = links.nth(index).get_attribute("href") or ""
        match = TEXT_DATE_PATTERN.search(href)
        if not match:
            continue
        token = match.group(1)
        iso_date = f"{token[0:4]}-{token[4:6]}-{token[6:8]}"
        if iso_date not in dates:
            dates.append(iso_date)

    if not dates:
        return "No visible mPay text report dates were detected on screen."

    preview = ", ".join(dates[:5])
    if len(dates) > 5:
        return f"Available mPay text report dates on screen: {preview}, ..."
    return f"Available mPay text report dates on screen: {preview}"


def summarize_available_xml_dates(page: Page) -> str:
    dates: list[str] = []
    xml_buttons = page.locator("input[onclick*='viewReport('][onclick*='.xml']")
    for index in range(xml_buttons.count()):
        onclick = xml_buttons.nth(index).get_attribute("onclick") or ""
        match = XML_DATE_PATTERN.search(onclick)
        if not match:
            continue
        token = match.group(1)
        iso_date = f"{token[0:4]}-{token[4:6]}-{token[6:8]}"
        if iso_date not in dates:
            dates.append(iso_date)

    if not dates:
        return "No visible mPay XML report dates were detected on screen."

    preview = ", ".join(dates[:5])
    if len(dates) > 5:
        return f"Available mPay XML report dates on screen: {preview}, ..."
    return f"Available mPay XML report dates on screen: {preview}"


def build_no_data_message(run_date: date, missing_items: list[str], details: list[str]) -> str:
    missing_label = ", ".join(missing_items)
    base_message = (
        "No mPay data was found for "
        f"run date {run_date.isoformat()}. Missing: {missing_label}. "
        "This usually means the selected date is wrong or the source has not published data yet."
    )
    extra_details = " ".join(detail for detail in details if detail)
    if extra_details:
        return f"{base_message} {extra_details}"
    return base_message


def build_partial_data_message(run_date: date, available_items: list[str], missing_items: list[str], details: list[str]) -> str:
    available_label = ", ".join(available_items)
    missing_label = ", ".join(missing_items)
    base_message = (
        "mPay returned partial data for "
        f"run date {run_date.isoformat()}. "
        f"Available: {available_label}. Missing: {missing_label}."
    )
    extra_details = " ".join(detail for detail in details if detail)
    if extra_details:
        return f"{base_message} {extra_details}"
    return base_message


def login(page: Page, settings: AppSettings, log, artifact_dir: Path | None = None) -> None:
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
        transition_screenshot: bytes | None = None
        transition_html: str | None = None
        transition_url: str | None = None
        deadline = monotonic() + (DEFAULT_TIMEOUT_MS / 1000)
        username_input = page.locator(locators.USERNAME_INPUT)
        password_input = page.locator(locators.PASSWORD_INPUT)
        post_login_ready = page.locator(locators.POST_LOGIN_READY)

        while monotonic() < deadline:
            if post_login_ready.count() > 0 and post_login_ready.first.is_visible():
                wait_for_network_idle(page)
                log("Login submitted")
                pause(page, settings, log, "after login")
                return

            form_visible = (
                username_input.count() > 0
                and password_input.count() > 0
                and username_input.first.is_visible()
                and password_input.first.is_visible()
            )

            if not form_visible:
                if transition_html is None and artifact_dir is not None:
                    transition_screenshot, transition_html, transition_url = _capture_login_transition(page)

                try:
                    body_text = (page.locator("body").inner_text() or "").lower()
                except Exception:
                    body_text = ""

                if any(marker in body_text for marker in LOGIN_AUTHORIZATION_MARKERS):
                    if artifact_dir is not None:
                        _save_login_transition_artifacts(
                            artifact_dir,
                            transition_screenshot,
                            transition_html,
                            transition_url,
                            log,
                        )
                    raise LoginError(
                        "mPay showed a transient authorization error page after submit and then returned to login. "
                        "Please verify MPAY_USERNAME and MPAY_PASSWORD."
                    )

                if any(marker in body_text for marker in LOGIN_ERROR_MARKERS):
                    if artifact_dir is not None:
                        _save_login_transition_artifacts(
                            artifact_dir,
                            transition_screenshot,
                            transition_html,
                            transition_url,
                            log,
                        )
                    raise LoginError(
                        "mPay showed a login failure page after submit. "
                        "Please verify MPAY_USERNAME and MPAY_PASSWORD."
                    )
            elif transition_html is not None:
                if artifact_dir is not None:
                    _save_login_transition_artifacts(
                        artifact_dir,
                        transition_screenshot,
                        transition_html,
                        transition_url,
                        log,
                    )
                raise LoginError(
                    "mPay returned to the login page after showing a transient login response. "
                    "Please verify MPAY_USERNAME and MPAY_PASSWORD."
                )

            page.wait_for_timeout(LOGIN_POLL_MS)

        if transition_html is not None and artifact_dir is not None:
            _save_login_transition_artifacts(
                artifact_dir,
                transition_screenshot,
                transition_html,
                transition_url,
                log,
            )
        raise LoginError(
            "mPay login did not reach the post-login page. "
            "Please verify MPAY_USERNAME and MPAY_PASSWORD."
        )
    except Exception as exc:
        if isinstance(exc, LoginError):
            raise
        raise LoginError("Failed during mPay login flow.") from exc


def open_text_menu(page: Page, settings: AppSettings, log) -> None:
    log("Opening text report menu")
    wait_for_visible(page, locators.MAIN_MENU, timeout_ms=DEFAULT_TIMEOUT_MS)
    click_after_hover(page, locators.MAIN_MENU, locators.TEXT_MENU)
    wait_for_page_ready(page)
    pause(page, settings, log, "after opening text menu")


def download_text_report(page: Page, settings: AppSettings, run_date: date, temp_dir: Path, log) -> Path | None:
    file_name = schema.build_text_filename(run_date)
    log(f"Downloading text report: {file_name}")
    report_locator = f"a[href*='{file_name}']"
    open_text_menu(page, settings, log)
    report_links = page.locator(report_locator)
    if report_links.count() == 0:
        log(f"No mPay text report entry found for {file_name}")
        return None
    try:
        wait_for_visible(page, report_locator, timeout_ms=DEFAULT_TIMEOUT_MS)
        report_link = report_links.first
        with page.expect_download(timeout=DOWNLOAD_TIMEOUT_MS) as download_info:
            report_link.click()
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


def open_xml_viewer(page: Page, settings: AppSettings, run_date: date, log) -> Page | None:
    file_name = schema.build_xml_filename(run_date)
    log(f"Opening XML viewer for: {file_name}")
    xml_view_selector = schema.build_xml_view_selector(run_date)
    open_xml_menu(page, settings, log)
    xml_view_buttons = page.locator(xml_view_selector)
    if xml_view_buttons.count() == 0:
        log(f"No mPay XML viewer entry found for {file_name}")
        return None
    try:
        wait_for_visible(page, xml_view_selector, timeout_ms=DEFAULT_TIMEOUT_MS)
        xml_view_button = xml_view_buttons.first

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
