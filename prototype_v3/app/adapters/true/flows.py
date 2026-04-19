from __future__ import annotations

from datetime import date
from pathlib import Path

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from app.actions.forms import click, fill_text
from app.actions.waits import wait_for_any_visible, wait_for_network_idle, wait_for_page_ready, wait_for_visible
from app.adapters.true import locators, schema
from app.browser.downloads import ensure_download_exists, save_download
from app.core.config import AppSettings
from app.core.errors import ConfigurationError, DownloadError, LoginError, NoDataError, PartialDataError, ValidationError
from app.services.file_service import list_files

DEFAULT_TIMEOUT_MS = 10000
DOWNLOAD_TIMEOUT_MS = 15000


def pause(page: Page, settings: AppSettings, log, reason: str) -> None:
    seconds = settings.step_delay_seconds
    if seconds <= 0:
        return
    log(f"Waiting {seconds} second(s): {reason}")
    page.wait_for_timeout(seconds * 1000)


def login(page: Page, settings: AppSettings, log) -> None:
    if not settings.true_username or not settings.true_password:
        raise ConfigurationError("Missing TRUE_USERNAME or TRUE_PASSWORD.")

    log("Opening True login page")
    page.goto(locators.LOGIN_URL, wait_until="domcontentloaded")
    wait_for_page_ready(page)

    try:
        wait_for_visible(page, locators.USERNAME_INPUT, timeout_ms=DEFAULT_TIMEOUT_MS)
        wait_for_visible(page, locators.PASSWORD_INPUT, timeout_ms=DEFAULT_TIMEOUT_MS)
        fill_text(page, locators.USERNAME_INPUT, settings.true_username)
        password_input = page.locator(locators.PASSWORD_INPUT)
        password_input.fill(settings.true_password)
        click(page, locators.LOGIN_BUTTON)
        try:
            visible_selector = wait_for_any_visible(
                page,
                [
                    locators.POST_LOGIN_READY,
                    locators.LOGIN_ERROR_MESSAGE,
                    locators.USERNAME_INPUT,
                ],
                timeout_ms=DEFAULT_TIMEOUT_MS,
            )
        except Exception as exc:
            raise
        if visible_selector == locators.LOGIN_ERROR_MESSAGE:
            message = page.locator(locators.LOGIN_ERROR_MESSAGE).first.inner_text().strip()
            raise LoginError(
                "True rejected the username or password"
                f"{': ' + message if message else '.'}"
            )
        if visible_selector == locators.USERNAME_INPUT:
            password_input = page.locator(locators.PASSWORD_INPUT)
            if password_input.count() > 0 and password_input.first.is_visible():
                raise LoginError(
                    "True login did not reach the post-login page. "
                    "Please verify TRUE_USERNAME and TRUE_PASSWORD."
                )
        log("Login submitted")
        pause(page, settings, log, "after login")
    except Exception as exc:
        if isinstance(exc, LoginError):
            raise
        raise LoginError("Failed during True login flow.") from exc


def _month_index(value: date) -> int:
    return (value.year * 12) + value.month


def select_run_date(page: Page, settings: AppSettings, run_date: date, log) -> None:
    calendar_title = schema.build_calendar_title(run_date)
    log(f"Selecting run date on True portal: {run_date.isoformat()}")
    wait_for_visible(page, locators.DATE_INPUT, timeout_ms=DEFAULT_TIMEOUT_MS)
    click(page, locators.DATE_INPUT)
    pause(page, settings, log, "after opening date picker")

    today = date.today()
    month_delta = _month_index(run_date) - _month_index(today)
    if month_delta < 0:
        for _ in range(abs(month_delta)):
            click(page, locators.PREVIOUS_MONTH_BUTTON)
    elif month_delta > 0:
        for _ in range(month_delta):
            click(page, locators.NEXT_MONTH_BUTTON)

    day_selector = locators.build_calendar_day_selector(calendar_title)
    try:
        wait_for_visible(page, day_selector, timeout_ms=DEFAULT_TIMEOUT_MS)
        click(page, day_selector)
        click(page, locators.SEARCH_BUTTON)
        wait_for_network_idle(page)
        pause(page, settings, log, "after searching by date")
    except Exception as exc:
        raise DownloadError(f"Failed to select True run date: {run_date.isoformat()}") from exc


def _detect_available_files(page: Page, expected_names: list[str]) -> list[str]:
    available: list[str] = []
    for file_name in expected_names:
        selector = locators.build_download_row_selector(file_name)
        if page.locator(f"xpath={selector}").count() > 0:
            available.append(file_name)
    return available


def download_web_reports(
    page: Page,
    settings: AppSettings,
    run_date: date,
    temp_dir: Path,
    log,
) -> list[Path]:
    expected_files = schema.build_web_filenames(run_date)
    available_files = _detect_available_files(page, expected_files)
    if not available_files:
        raise NoDataError(
            "No True portal files were found for "
            f"run date {run_date.isoformat()}. "
            "This usually means the selected date is wrong or the source has not published data yet."
        )

    missing_files = [name for name in expected_files if name not in available_files]
    if missing_files:
        raise PartialDataError(
            "True portal returned partial data. "
            f"Missing expected files: {', '.join(missing_files)}"
        )

    downloaded: list[Path] = []
    for file_name in expected_files:
        selector = locators.build_download_row_selector(file_name)
        log(f"Downloading True portal file: {file_name}")
        try:
            with page.expect_download(timeout=DOWNLOAD_TIMEOUT_MS) as download_info:
                page.locator(f"xpath={selector}").click()
            download = download_info.value
            path = save_download(download, temp_dir)
            ensure_download_exists(path)
            downloaded.append(path)
            pause(page, settings, log, f"after downloading {file_name}")
        except PlaywrightTimeoutError as exc:
            raise DownloadError(f"Timed out downloading True portal file: {file_name}") from exc
        except Exception as exc:
            raise DownloadError(f"Failed to download True portal file: {file_name}") from exc

    return downloaded


def logout(page: Page, settings: AppSettings, log) -> None:
    try:
        wait_for_visible(page, locators.LOGOUT_BUTTON, timeout_ms=DEFAULT_TIMEOUT_MS)
        log("Logging out from True portal")
        click(page, locators.LOGOUT_BUTTON)
        pause(page, settings, log, "after logout")
    except Exception as exc:
        log(f"Skipping True logout due to a non-fatal error: {exc}")


def validate_downloads(temp_dir: Path, run_date: date, include_servu: bool) -> None:
    files = {path.name for path in list_files(temp_dir)}
    expected = set(schema.build_web_filenames(run_date))
    if include_servu:
        expected.update(schema.build_servu_filenames(run_date))
    missing = expected - files
    if missing:
        if files:
            raise PartialDataError(
                "True workflow returned partial data. "
                f"Missing expected downloaded files: {', '.join(sorted(missing))}"
            )
        raise ValidationError(f"Missing expected downloaded files: {', '.join(sorted(missing))}")
