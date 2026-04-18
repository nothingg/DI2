from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from app.actions.waits import wait_for_page_ready, wait_for_visible
from app.adapters.baac_stmt import locators, schema
from app.browser.downloads import ensure_download_exists, save_download
from app.core.config import AppSettings
from app.core.errors import ConfigurationError, DownloadError, LoginError, NoDataError, PartialDataError, ValidationError
from app.services.artifact_service import save_page_artifacts
from app.services.file_service import list_files

DEFAULT_TIMEOUT_MS = 10000
DOWNLOAD_TIMEOUT_MS = 15000
WORKSPACE_REFRESH_RETRIES = 2
ITEM_TOKEN_PATTERN = re.compile(r"^item-(.+?)(?:-cont)?$")


def pause(page: Page, settings: AppSettings, log, reason: str) -> None:
    seconds = settings.step_delay_seconds
    if seconds <= 0:
        return
    log(f"Waiting {seconds} second(s): {reason}")
    page.wait_for_timeout(seconds * 1000)


def build_no_data_message(selected_date: date, statement_date: date, scope: str, extra: str = "") -> str:
    message = (
        f"No BAAC statement {scope} was found for selected run date {selected_date.isoformat()} "
        f"(statement date {statement_date.isoformat()})."
    )
    if extra:
        return f"{message} {extra}"
    return message


def build_partial_data_message(selected_date: date, statement_date: date, available_items: list[str], missing_items: list[str]) -> str:
    return (
        "BAAC Statement returned partial data for "
        f"selected run date {selected_date.isoformat()} "
        f"(statement date {statement_date.isoformat()}). "
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
        return "No visible BAAC Statement items were detected on screen."

    preview = ", ".join(visible_labels[:8])
    if len(visible_labels) > 8:
        return f"Available BAAC Statement items on screen: {preview}, ..."
    return f"Available BAAC Statement items on screen: {preview}"


def _save_workspace_refresh_debug_artifacts(
    page: Page,
    artifact_dir: Path,
    selected_date: date,
    statement_date: date,
    log,
) -> None:
    save_page_artifacts(
        page=page,
        artifact_dir=artifact_dir,
        prefix="workspace-refresh",
        log=log,
        extra_meta_lines=[
            f"selected_run_date={selected_date.isoformat()}",
            f"statement_date={statement_date.isoformat()}",
            f"visible_items_summary={summarize_available_dates(page)}",
        ],
    )


def login(page: Page, settings: AppSettings, log) -> None:
    if not settings.baac_username or not settings.baac_password:
        raise ConfigurationError("Missing BAAC_USERNAME or BAAC_PASSWORD for BAAC Statement.")

    log("Opening BAAC Statement login page")
    page.goto(locators.LOGIN_URL, wait_until="domcontentloaded")
    wait_for_page_ready(page)
    pause(page, settings, log, "after opening BAAC Statement login page")

    try:
        wait_for_visible(page, locators.USERNAME_INPUT, timeout_ms=DEFAULT_TIMEOUT_MS)
        wait_for_visible(page, locators.PASSWORD_INPUT, timeout_ms=DEFAULT_TIMEOUT_MS)
        page.locator(locators.USERNAME_INPUT).fill(settings.baac_username)
        page.locator(locators.PASSWORD_INPUT).fill(settings.baac_password)
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
                    "BAAC Statement login did not reach the post-login page. "
                    "Please verify BAAC_USERNAME and BAAC_PASSWORD."
                ) from exc
            raise
        if not _is_logged_in(page):
            raise LoginError(
                "BAAC Statement login did not reach the post-login page. "
                "Please verify BAAC_USERNAME and BAAC_PASSWORD."
            )
        log("Login submitted")
        pause(page, settings, log, "after login")
    except Exception as exc:
        if isinstance(exc, LoginError):
            raise
        raise LoginError("Failed during BAAC Statement login flow.") from exc


def _refresh_workspace_listing(
    page: Page,
    settings: AppSettings,
    selected_date: date,
    statement_date: date,
    artifact_dir: Path,
    log,
) -> None:
    wait_for_visible(page, locators.WORKSPACE_REFRESH, timeout_ms=DEFAULT_TIMEOUT_MS)
    last_error: Exception | None = None
    for attempt in range(1, WORKSPACE_REFRESH_RETRIES + 1):
        log(
            "Refreshing BAAC Statement workspace listing "
            f"(attempt {attempt}/{WORKSPACE_REFRESH_RETRIES})"
        )
        page.locator(locators.WORKSPACE_REFRESH).first.click()
        pause(page, settings, log, "after refreshing BAAC Statement workspace")
        try:
            page.wait_for_function(
                """
                () => document.querySelectorAll('#selectable_div-5 [id^="item-"]').length > 0
                """,
                timeout=DEFAULT_TIMEOUT_MS,
            )
            return
        except Exception as exc:
            last_error = exc
            if attempt < WORKSPACE_REFRESH_RETRIES:
                log("BAAC Statement workspace listing did not load yet. Retrying refresh once more.")

    _save_workspace_refresh_debug_artifacts(page, artifact_dir, selected_date, statement_date, log)
    raise DownloadError(
        "BAAC Statement workspace opened but the folder listing did not load after refresh retries. "
        "Debug artifacts were saved."
    ) from last_error


def _open_workspace(
    page: Page,
    settings: AppSettings,
    selected_date: date,
    statement_date: date,
    artifact_dir: Path,
    log,
) -> None:
    target_url = schema.build_workspace_url()
    log(f"Opening BAAC Statement workspace: {target_url}")
    page.goto(target_url, wait_until="domcontentloaded")
    wait_for_page_ready(page)
    pause(page, settings, log, "after opening BAAC Statement workspace")
    if _login_form_visible(page):
        raise LoginError(
            "BAAC Statement session returned to the login page before the workspace opened. "
            "Please verify BAAC credentials and browser mode."
        )
    wait_for_visible(page, locators.WORKSPACE_ROOT, timeout_ms=DEFAULT_TIMEOUT_MS)
    _refresh_workspace_listing(page, settings, selected_date, statement_date, artifact_dir, log)


def _open_item(page: Page, item_id: str, label: str, settings: AppSettings, log) -> None:
    selector = locators.build_item_selector(item_id)
    wait_for_visible(page, selector, timeout_ms=DEFAULT_TIMEOUT_MS)
    log(f"Opening BAAC Statement {label}: {item_id}")
    page.locator(selector).first.click()
    pause(page, settings, log, f"after selecting BAAC Statement {label}")
    page.locator(selector).first.dblclick()
    pause(page, settings, log, f"after opening BAAC Statement {label}")


def _open_year(page: Page, settings: AppSettings, selected_date: date, statement_date: date, log) -> None:
    item_id = schema.build_year_item_id(statement_date)
    try:
        wait_for_visible(page, locators.build_item_selector(item_id), timeout_ms=DEFAULT_TIMEOUT_MS)
    except Exception:
        raise NoDataError(
            build_no_data_message(selected_date, statement_date, "year entry", summarize_available_dates(page))
        )
    _open_item(page, item_id, "year", settings, log)


def _open_month(page: Page, settings: AppSettings, selected_date: date, statement_date: date, log) -> None:
    item_id = schema.build_month_item_id(statement_date)
    try:
        wait_for_visible(page, locators.build_item_selector(item_id), timeout_ms=DEFAULT_TIMEOUT_MS)
    except Exception:
        raise NoDataError(
            build_no_data_message(selected_date, statement_date, "month entry", summarize_available_dates(page))
        )
    _open_item(page, item_id, "month", settings, log)


def _open_day(page: Page, settings: AppSettings, selected_date: date, statement_date: date, log) -> None:
    item_id = schema.build_day_item_id(statement_date)
    try:
        wait_for_visible(page, locators.build_item_selector(item_id), timeout_ms=DEFAULT_TIMEOUT_MS)
    except Exception:
        raise NoDataError(
            build_no_data_message(
                selected_date,
                statement_date,
                "day entry",
                summarize_available_dates(page),
            )
        )
    _open_item(page, item_id, "day", settings, log)


def _save_download_to_temp(download, temp_dir: Path) -> Path:
    path = save_download(download, temp_dir)
    ensure_download_exists(path)
    return path


def inspect_file_availability(page: Page, statement_date: date) -> tuple[list[str], list[str]]:
    expected_name = schema.build_expected_filename(statement_date)
    selector = locators.build_item_selector(schema.build_file_row_id(statement_date))
    if page.locator(selector).count() > 0:
        return [expected_name], []

    available: list[str] = []
    rows = page.locator(locators.CONTENT_ROWS)
    for index in range(rows.count()):
        text = rows.nth(index).inner_text().strip()
        if text:
            available.append(text.splitlines()[0].strip())
    return available, [expected_name]


def _download_statement_report(page: Page, settings: AppSettings, statement_date: date, temp_dir: Path, log) -> Path:
    file_name = schema.build_expected_filename(statement_date)
    selector = locators.build_item_selector(schema.build_file_row_id(statement_date))
    log(f"Downloading BAAC Statement file: {file_name}")
    wait_for_visible(page, selector, timeout_ms=DEFAULT_TIMEOUT_MS)
    page.locator(selector).first.click()
    pause(page, settings, log, f"after selecting {file_name}")
    wait_for_visible(page, locators.DOWNLOAD_BUTTON, timeout_ms=DEFAULT_TIMEOUT_MS)
    with page.expect_download(timeout=DOWNLOAD_TIMEOUT_MS) as download_info:
        page.locator(locators.DOWNLOAD_BUTTON).first.click()
    path = _save_download_to_temp(download_info.value, temp_dir)
    pause(page, settings, log, f"after downloading {path.name}")
    return path


def download_web_reports(
    page: Page,
    settings: AppSettings,
    run_date: date,
    temp_dir: Path,
    artifact_dir: Path,
    log,
) -> list[Path]:
    statement_date = schema.adjust_to_business_date(run_date)
    log(
        "BAAC Statement business date mapping: "
        f"selected run date={run_date.isoformat()}, "
        f"statement date={statement_date.isoformat()}"
    )

    _open_workspace(page, settings, run_date, statement_date, artifact_dir, log)
    _open_year(page, settings, run_date, statement_date, log)
    _open_month(page, settings, run_date, statement_date, log)
    _open_day(page, settings, run_date, statement_date, log)

    try:
        wait_for_visible(page, locators.CONTENT_ROWS, timeout_ms=DEFAULT_TIMEOUT_MS)
    except PlaywrightTimeoutError as exc:
        raise NoDataError(
            build_no_data_message(
                run_date,
                statement_date,
                "file list",
                "The day folder opened but did not show any statement files.",
            )
        ) from exc

    available_files, missing_files = inspect_file_availability(page, statement_date)
    if missing_files:
        if available_files:
            raise PartialDataError(
                build_partial_data_message(run_date, statement_date, available_files, missing_files)
            )
        raise NoDataError(
            build_no_data_message(
                run_date,
                statement_date,
                "statement file",
                summarize_available_dates(page),
            )
        )

    return [_download_statement_report(page, settings, statement_date, temp_dir, log)]


def logout(page: Page, settings: AppSettings, log) -> None:
    try:
        wait_for_visible(page, locators.LOGOUT_MENU, timeout_ms=DEFAULT_TIMEOUT_MS)
        log("Logging out from BAAC Statement")
        page.locator(locators.LOGOUT_MENU).hover()
        wait_for_visible(page, locators.LOGOUT_LINK, timeout_ms=DEFAULT_TIMEOUT_MS)
        page.locator(locators.LOGOUT_LINK).click()
        pause(page, settings, log, "after logout")
    except Exception as exc:
        log(f"Skipping BAAC Statement logout due to a non-fatal error: {exc}")


def validate_downloads(temp_dir: Path, run_date: date) -> None:
    statement_date = schema.adjust_to_business_date(run_date)
    expected_file = schema.build_expected_filename(statement_date)
    files = {path.name for path in list_files(temp_dir)}

    if expected_file in files:
        return
    if files:
        raise PartialDataError(
            "BAAC Statement workflow returned partial data. "
            f"Missing expected downloaded file: {expected_file}"
        )
    raise ValidationError(f"Missing expected downloaded file: {expected_file}")
