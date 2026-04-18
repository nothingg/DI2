from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import Page, Response, TimeoutError as PlaywrightTimeoutError

from app.actions.forms import click, fill_text
from app.actions.waits import wait_for_network_idle, wait_for_page_ready, wait_for_visible
from app.adapters.counter_service import locators, schema
from app.browser.downloads import ensure_download_exists, save_download
from app.core.config import AppSettings
from app.core.errors import ConfigurationError, DownloadError, LoginError, NoDataError, PartialDataError, ValidationError
from app.services.file_service import list_files

DEFAULT_TIMEOUT_MS = 10000
DOWNLOAD_TIMEOUT_MS = 15000


@dataclass(slots=True)
class CounterServiceAvailability:
    required_available: list[str]
    required_missing: list[str]
    optional_available: list[str]
    optional_missing: list[str]


@dataclass(slots=True)
class CounterServiceDownloadResult:
    availability: CounterServiceAvailability
    downloaded_files: list[Path]


def summarize_visible_download_entries(page: Page) -> list[str]:
    entries: list[str] = []
    locator = page.locator(locators.DOWNLOAD_LINKS)
    count = min(locator.count(), 10)
    for index in range(count):
        href = (locator.nth(index).get_attribute("href") or "").strip()
        text = locator.nth(index).inner_text().strip()
        label = text or href or "<empty>"
        if href and text and href not in text:
            label = f"{text} ({href})"
        entries.append(label)
    return entries


def save_response_file(response: Response, target_path: Path) -> Path:
    target_path.write_bytes(response.body())
    return target_path


def download_via_authenticated_request(page: Page, href: str, file_name: str, temp_dir: Path) -> Path:
    absolute_url = urljoin(page.url, href)
    response = page.context.request.get(absolute_url, fail_on_status_code=False)
    if not response.ok:
        raise DownloadError(
            "Counter Service direct file request failed for "
            f"{file_name} with status {response.status}"
        )
    target_path = temp_dir / file_name
    return save_response_file(response, target_path)


def pause(page: Page, settings: AppSettings, log, reason: str) -> None:
    seconds = settings.step_delay_seconds
    if seconds <= 0:
        return
    log(f"Waiting {seconds} second(s): {reason}")
    page.wait_for_timeout(seconds * 1000)


def login(page: Page, settings: AppSettings, log) -> None:
    if not settings.counter_service_username or not settings.counter_service_password:
        raise ConfigurationError("Missing COUNTER_SERVICE_USERNAME or COUNTER_SERVICE_PASSWORD.")

    log("Opening Counter Service login page")
    page.goto(locators.LOGIN_URL, wait_until="domcontentloaded")
    wait_for_page_ready(page)

    try:
        wait_for_visible(page, locators.USERNAME_INPUT, timeout_ms=DEFAULT_TIMEOUT_MS)
        wait_for_visible(page, locators.PASSWORD_INPUT, timeout_ms=DEFAULT_TIMEOUT_MS)
        fill_text(page, locators.USERNAME_INPUT, settings.counter_service_username)
        fill_text(page, locators.PASSWORD_INPUT, settings.counter_service_password)
        click(page, locators.LOGIN_BUTTON)
        wait_for_network_idle(page)
        error_locator = page.locator(locators.LOGIN_ERROR_MESSAGE)
        if error_locator.count() > 0 and error_locator.first.is_visible():
            message = error_locator.first.inner_text().strip()
            raise LoginError(
                "Counter Service rejected the username or password"
                f"{': ' + message if message else '.'}"
            )

        wait_for_visible(page, locators.POST_LOGIN_READY, timeout_ms=DEFAULT_TIMEOUT_MS)
        log("Login submitted")
        pause(page, settings, log, "after login")
    except Exception as exc:
        if isinstance(exc, LoginError):
            raise
        raise LoginError("Failed during Counter Service login flow.") from exc


def inspect_availability(page: Page, run_date: date) -> CounterServiceAvailability:
    required_available: list[str] = []
    required_missing: list[str] = []
    optional_available: list[str] = []
    optional_missing: list[str] = []

    for file_name in schema.build_required_web_filenames(run_date):
        fragments = schema.build_download_fragments(file_name)
        xpath = locators.build_download_xpath(fragments)
        if page.locator(f"xpath={xpath}").count() > 0:
            required_available.append(file_name)
        else:
            required_missing.append(file_name)

    for file_name in schema.build_optional_web_filenames(run_date):
        fragments = schema.build_download_fragments(file_name)
        xpath = locators.build_download_xpath(fragments)
        if page.locator(f"xpath={xpath}").count() > 0:
            optional_available.append(file_name)
        else:
            optional_missing.append(file_name)

    return CounterServiceAvailability(
        required_available=required_available,
        required_missing=required_missing,
        optional_available=optional_available,
        optional_missing=optional_missing,
    )


def build_no_data_message(run_date: date, availability: CounterServiceAvailability) -> str:
    visible = availability.required_available + availability.optional_available
    if visible:
        return (
            "No Counter Service data was found for "
            f"run date {run_date.isoformat()}. "
            f"Only unexpected/optional entries were visible: {', '.join(visible)}"
        )
    return (
        "No Counter Service data was found for "
        f"run date {run_date.isoformat()}. "
        "This usually means the selected date is wrong or the source has not published data yet."
    )


def build_partial_data_message(run_date: date, availability: CounterServiceAvailability) -> str:
    available = availability.required_available + availability.optional_available
    missing = availability.required_missing
    return (
        "Counter Service returned partial data for "
        f"run date {run_date.isoformat()}. "
        f"Available: {', '.join(available)}. Missing required files: {', '.join(missing)}."
    )


def download_web_reports(
    page: Page,
    settings: AppSettings,
    run_date: date,
    temp_dir: Path,
    log,
) -> CounterServiceDownloadResult:
    try:
        page.wait_for_selector(locators.DOWNLOAD_LINKS, timeout=DEFAULT_TIMEOUT_MS)
    except PlaywrightTimeoutError:
        log("Counter Service download links were not detected before inspection")

    log(f"Counter Service page URL before inspection: {page.url}")
    visible_entries = summarize_visible_download_entries(page)
    if visible_entries:
        log("Visible Counter Service download entries: " + " | ".join(visible_entries))
    else:
        log("Visible Counter Service download entries: <none>")

    availability = inspect_availability(page, run_date)
    if not availability.required_available and not availability.optional_available:
        raise NoDataError(build_no_data_message(run_date, availability))

    downloaded: list[Path] = []
    for file_name in availability.required_available + availability.optional_available:
        fragments = schema.build_download_fragments(file_name)
        xpath = locators.build_download_xpath(fragments)
        locator = page.locator(f"xpath={xpath}").first
        log(f"Downloading Counter Service file: {file_name}")
        try:
            with page.expect_download(timeout=DOWNLOAD_TIMEOUT_MS) as download_info:
                locator.click()
            download = download_info.value
            path = save_download(download, temp_dir)
            ensure_download_exists(path)
            downloaded.append(path)
            pause(page, settings, log, f"after downloading {file_name}")
        except PlaywrightTimeoutError as exc:
            href = locator.get_attribute("href")
            if not href:
                raise DownloadError(f"Timed out downloading Counter Service file: {file_name}") from exc
            log(
                "Counter Service download event did not fire; "
                f"falling back to authenticated request for {file_name}"
            )
            path = download_via_authenticated_request(page, href, file_name, temp_dir)
            ensure_download_exists(path)
            downloaded.append(path)
            pause(page, settings, log, f"after downloading {file_name}")
        except Exception as exc:
            href = locator.get_attribute("href")
            if href:
                log(
                    "Counter Service click-based download failed; "
                    f"falling back to authenticated request for {file_name}"
                )
                path = download_via_authenticated_request(page, href, file_name, temp_dir)
                ensure_download_exists(path)
                downloaded.append(path)
                pause(page, settings, log, f"after downloading {file_name}")
                continue
            raise DownloadError(f"Failed to download Counter Service file: {file_name}") from exc

    if availability.optional_missing:
        log(
            "Counter Service optional files not found: "
            f"{', '.join(availability.optional_missing)}"
        )
    return CounterServiceDownloadResult(
        availability=availability,
        downloaded_files=downloaded,
    )


def logout(page: Page, settings: AppSettings, log) -> None:
    try:
        wait_for_visible(page, locators.LOGOUT_LINK, timeout_ms=DEFAULT_TIMEOUT_MS)
        log("Logging out from Counter Service")
        click(page, locators.LOGOUT_LINK)
        pause(page, settings, log, "after logout")
    except Exception as exc:
        log(f"Skipping Counter Service logout due to a non-fatal error: {exc}")


def validate_downloads(temp_dir: Path, run_date: date, include_servu: bool) -> None:
    files = {path.name for path in list_files(temp_dir)}
    required = set(schema.build_required_web_filenames(run_date))
    missing_required = required - files
    if missing_required:
        raise ValidationError(f"Missing required downloaded files: {', '.join(sorted(missing_required))}")

    optional = set(schema.build_optional_web_filenames(run_date))
    if optional and optional.isdisjoint(files):
        # Optional files are allowed to be missing.
        pass

    if include_servu:
        base_name = schema.build_indcr_filename(run_date)
        matching = [
            name for name in files
            if name == base_name or name.startswith(f"{Path(base_name).stem}_")
        ]
        if len(matching) < 2:
            raise ValidationError(
                "Expected both web and SFTP Counter Service INDCR files, "
                f"but found {len(matching)} matching file(s): {', '.join(sorted(matching)) or '<none>'}"
            )
