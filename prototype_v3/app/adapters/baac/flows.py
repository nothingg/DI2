from __future__ import annotations

from datetime import date
from pathlib import Path
import re

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from app.actions.waits import wait_for_page_ready, wait_for_visible
from app.adapters.baac import locators, schema
from app.browser.downloads import ensure_download_exists, save_download
from app.core.config import AppSettings
from app.core.errors import ConfigurationError, DownloadError, LoginError, NoDataError, PartialDataError, ValidationError
from app.services.file_service import list_files

DEFAULT_TIMEOUT_MS = 10000
DOWNLOAD_TIMEOUT_MS = 15000
ITEM_TOKEN_PATTERN = re.compile(r"^item-(.+)$")


def pause(page: Page, settings: AppSettings, log, reason: str) -> None:
    seconds = settings.step_delay_seconds
    if seconds <= 0:
        return
    log(f"Waiting {seconds} second(s): {reason}")
    page.wait_for_timeout(seconds * 1000)


def build_partial_data_message(run_date: date, available_items: list[str], missing_items: list[str]) -> str:
    return (
        "BAAC returned partial data for "
        f"run date {run_date.isoformat()}. "
        f"Available: {', '.join(available_items)}. Missing: {', '.join(missing_items)}."
    )


def _login_form_visible(page: Page) -> bool:
    username = page.locator(locators.USERNAME_INPUT)
    password = page.locator(locators.PASSWORD_INPUT)
    return (
        username.count() > 0
        and password.count() > 0
        and username.first.is_visible()
        and password.first.is_visible()
    )


def _is_logged_in(page: Page) -> bool:
    marker = page.locator(locators.POST_LOGIN_READY)
    if marker.count() == 0 or not marker.first.is_visible():
        return False
    try:
        marker_text = marker.first.inner_text().strip().lower()
    except Exception:
        return False
    return "not logged in" not in marker_text


def summarize_available_dates(page: Page) -> str:
    visible_labels: list[str] = []
    items = page.locator(locators.ITEM_ID_PREFIX)
    for index in range(items.count()):
        item_id = items.nth(index).get_attribute("id") or ""
        match = ITEM_TOKEN_PATTERN.match(item_id)
        if not match:
            continue
        token = match.group(1)
        if token not in visible_labels:
            visible_labels.append(token)

    if not visible_labels:
        return "No visible BAAC items were detected on screen."

    preview = ", ".join(visible_labels[:5])
    if len(visible_labels) > 5:
        return f"Available BAAC items on screen: {preview}, ..."
    return f"Available BAAC items on screen: {preview}"


def login(page: Page, settings: AppSettings, log) -> None:
    if not settings.baac_username or not settings.baac_password:
        raise ConfigurationError("Missing BAAC_USERNAME or BAAC_PASSWORD.")

    log("Opening BAAC login page")
    page.goto(locators.LOGIN_URL, wait_until="domcontentloaded")
    wait_for_page_ready(page)
    pause(page, settings, log, "after opening BAAC login page")

    try:
        wait_for_visible(page, locators.USERNAME_INPUT, timeout_ms=DEFAULT_TIMEOUT_MS)
        wait_for_visible(page, locators.PASSWORD_INPUT, timeout_ms=DEFAULT_TIMEOUT_MS)
        page.locator(locators.USERNAME_INPUT).fill(settings.baac_username)
        password_input = page.locator(locators.PASSWORD_INPUT)
        password_input.fill(settings.baac_password)
        page.locator(locators.LOGIN_BUTTON).click()
        try:
            page.wait_for_function(
                """
                () => {
                    const marker = document.querySelector('#logging_string');
                    if (!marker || !(marker instanceof HTMLElement)) {
                        return false;
                    }
                    const text = (marker.innerText || '').toLowerCase();
                    return text && !text.includes('not logged in');
                }
                """,
                timeout=DEFAULT_TIMEOUT_MS,
            )
        except Exception as exc:
            if _login_form_visible(page):
                raise LoginError(
                    "BAAC login did not reach the post-login page. "
                    "Please verify BAAC_USERNAME and BAAC_PASSWORD."
                ) from exc
            raise
        if not _is_logged_in(page):
            raise LoginError(
                "BAAC login did not reach the post-login page. "
                "Please verify BAAC_USERNAME and BAAC_PASSWORD."
            )
        log("Login submitted")
        pause(page, settings, log, "after login")
    except Exception as exc:
        if isinstance(exc, LoginError):
            raise
        raise LoginError("Failed during BAAC login flow.") from exc


def _open_workspace(page: Page, settings: AppSettings, log) -> None:
    target_url = schema.build_workspace_url()
    log(f"Opening BAAC payment workspace: {target_url}")
    page.goto(target_url, wait_until="domcontentloaded")
    wait_for_page_ready(page)
    pause(page, settings, log, "after opening BAAC payment workspace")
    if _login_form_visible(page):
        raise LoginError(
            "BAAC session returned to the login page before the payment workspace opened. "
            "Please verify BAAC credentials and browser mode."
        )
    wait_for_visible(page, locators.WORKSPACE_ROOT, timeout_ms=DEFAULT_TIMEOUT_MS)


def _open_item(page: Page, item_id: str, label: str, settings: AppSettings, log) -> None:
    selector = locators.build_item_selector(item_id)
    wait_for_visible(page, selector, timeout_ms=DEFAULT_TIMEOUT_MS)
    log(f"Opening BAAC {label}: {item_id}")
    page.locator(selector).first.click()
    pause(page, settings, log, f"after selecting BAAC {label}")
    page.locator(selector).first.dblclick()
    pause(page, settings, log, f"after opening BAAC {label}")


def _open_year(page: Page, settings: AppSettings, run_date: date, log) -> None:
    item_id = schema.build_year_item_id(run_date)
    try:
        wait_for_visible(page, locators.build_item_selector(item_id), timeout_ms=DEFAULT_TIMEOUT_MS)
    except Exception:
        raise NoDataError(
            "No BAAC year entry was found for "
            f"run date {run_date.isoformat()}. "
            f"{summarize_available_dates(page)}"
        )
    _open_item(page, item_id, "year", settings, log)


def _open_month(page: Page, settings: AppSettings, run_date: date, log) -> None:
    item_id = schema.build_month_item_id(run_date)
    try:
        wait_for_visible(page, locators.build_item_selector(item_id), timeout_ms=DEFAULT_TIMEOUT_MS)
    except Exception:
        raise NoDataError(
            "No BAAC month entry was found for "
            f"run date {run_date.isoformat()}. "
            f"{summarize_available_dates(page)}"
        )
    _open_item(page, item_id, "month", settings, log)


def _open_day(page: Page, settings: AppSettings, run_date: date, log) -> None:
    item_id = schema.build_day_item_id(run_date)
    try:
        wait_for_visible(page, locators.build_item_selector(item_id), timeout_ms=DEFAULT_TIMEOUT_MS)
    except Exception:
        raise NoDataError(
            "No BAAC day entry was found for "
            f"run date {run_date.isoformat()}. "
            "This usually means the selected date is wrong or the source has not published data yet. "
            f"{summarize_available_dates(page)}"
        )
    _open_item(page, item_id, "day", settings, log)


def _save_download_to_temp(download, temp_dir: Path) -> Path:
    path = save_download(download, temp_dir)
    ensure_download_exists(path)
    return path


def inspect_file_availability(page: Page, run_date: date) -> tuple[list[str], list[str]]:
    available: list[str] = []
    missing: list[str] = []
    required_rows = {
        schema.build_expected_pdf_filename(run_date, "DC106"): schema.build_pdf_row_id(run_date, "DC106"),
        schema.build_expected_pdf_filename(run_date, "DC105"): schema.build_pdf_row_id(run_date, "DC105"),
        schema.build_redcr_filename(run_date): schema.build_file_row_id(run_date, schema.build_redcr_filename(run_date)),
    }
    for file_name, row_id in required_rows.items():
        selector = locators.build_item_selector(row_id)
        if page.locator(selector).count() > 0:
            available.append(file_name)
        else:
            missing.append(file_name)
    return available, missing


def _download_row(page: Page, selector: str, file_name: str, settings: AppSettings, temp_dir: Path, log) -> Path:
    log(f"Downloading BAAC file: {file_name}")
    wait_for_visible(page, selector, timeout_ms=DEFAULT_TIMEOUT_MS)
    page.locator(selector).first.click()
    wait_for_visible(page, locators.ZIP_DOWNLOAD_BUTTON, timeout_ms=DEFAULT_TIMEOUT_MS)
    with page.expect_download(timeout=DOWNLOAD_TIMEOUT_MS) as download_info:
        page.locator(locators.ZIP_DOWNLOAD_BUTTON).first.click()
    path = _save_download_to_temp(download_info.value, temp_dir)
    pause(page, settings, log, f"after downloading {path.name}")
    return path


def _download_pdf_report(page: Page, settings: AppSettings, run_date: date, report_code: str, temp_dir: Path, log) -> Path:
    row_id = schema.build_pdf_row_id(run_date, report_code)
    selector = locators.build_item_selector(row_id)
    label = schema.build_expected_pdf_filename(run_date, report_code)
    return _download_row(page, selector, label, settings, temp_dir, log)


def _download_redcr_report(page: Page, settings: AppSettings, run_date: date, temp_dir: Path, log) -> Path:
    file_name = schema.build_redcr_filename(run_date)
    row_id = schema.build_file_row_id(run_date, file_name)
    selector = locators.build_item_selector(row_id)
    return _download_row(page, selector, file_name, settings, temp_dir, log)


def download_web_reports(
    page: Page,
    settings: AppSettings,
    run_date: date,
    temp_dir: Path,
    log,
) -> list[Path]:
    _open_workspace(page, settings, log)
    _open_year(page, settings, run_date, log)
    _open_month(page, settings, run_date, log)
    _open_day(page, settings, run_date, log)

    downloaded: list[Path] = []
    try:
        wait_for_visible(page, locators.CONTENT_ROWS, timeout_ms=DEFAULT_TIMEOUT_MS)
    except PlaywrightTimeoutError as exc:
        raise DownloadError("Timed out opening the BAAC day file list.") from exc

    available_files, missing_files = inspect_file_availability(page, run_date)
    if missing_files:
        available_items = available_files or ["BAAC day file list"]
        raise PartialDataError(build_partial_data_message(run_date, available_items, missing_files))
    downloaded.append(_download_redcr_report(page, settings, run_date, temp_dir, log))
    downloaded.append(_download_pdf_report(page, settings, run_date, "DC106", temp_dir, log))
    downloaded.append(_download_pdf_report(page, settings, run_date, "DC105", temp_dir, log))
    return downloaded


def logout(page: Page, settings: AppSettings, log) -> None:
    try:
        wait_for_visible(page, locators.LOGOUT_MENU, timeout_ms=DEFAULT_TIMEOUT_MS)
        log("Logging out from BAAC")
        page.locator(locators.LOGOUT_MENU).hover()
        wait_for_visible(page, locators.LOGOUT_LINK, timeout_ms=DEFAULT_TIMEOUT_MS)
        page.locator(locators.LOGOUT_LINK).click()
        pause(page, settings, log, "after logout")
    except Exception as exc:
        log(f"Skipping BAAC logout due to a non-fatal error: {exc}")


def validate_downloads(temp_dir: Path, run_date: date, include_servu: bool) -> None:
    files = {path.name for path in list_files(temp_dir)}
    missing: list[str] = []

    expected_zip = schema.build_redcr_filename(run_date)
    if expected_zip not in files:
        missing.append(expected_zip)

    for report_code in ("DC106", "DC105"):
        expected_pdf = schema.build_expected_pdf_filename(run_date, report_code)
        if expected_pdf not in files:
            missing.append(expected_pdf)

    if include_servu:
        expected_servu = schema.build_servu_filename(run_date)
        if expected_servu not in files:
            missing.append(expected_servu)

    if missing:
        if files:
            raise PartialDataError(
                "BAAC workflow returned partial data. "
                f"Missing expected downloaded files: {', '.join(missing)}"
            )
        raise ValidationError(f"Missing expected downloaded files: {', '.join(missing)}")
