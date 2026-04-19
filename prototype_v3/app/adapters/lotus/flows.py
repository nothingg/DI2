from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from time import monotonic

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from app.actions.waits import wait_for_visible
from app.adapters.lotus import locators, schema
from app.browser.downloads import ensure_download_exists, save_download
from app.core.config import AppSettings
from app.core.errors import ConfigurationError, DownloadError, LoginError, NoDataError, PartialDataError, ValidationError
from app.services.file_service import list_files

DEFAULT_TIMEOUT_MS = 10000
DOWNLOAD_TIMEOUT_MS = 15000
SECURITY_WAIT_TIMEOUT_MS = 60000
SECURITY_POLL_MS = 500
POST_LOGIN_WAIT_TIMEOUT_MS = 90000
MANUAL_ASSISTED_WAIT_TIMEOUT_MS = 180000
MANUAL_LOGIN_WAIT_TIMEOUT_MS = 300000
SECURITY_MARKERS = (
    "cloudflare",
    "attention required",
    "checking your browser",
    "verify you are human",
    "captcha",
    "just a moment",
)
LOGIN_FAILURE_MARKERS = (
    "invalid",
    "incorrect",
    "ชื่อผู้ใช้",
    "รหัสผ่าน",
    "secret code",
)
RELOGIN_REQUIRED_MARKERS = (
    "ไม่สามารถทำรายการได้ในขณะนี้",
    "กรุณาปิดบราวเซอร์และทำการล็อคอินใหม่อีกครั้ง",
)


@dataclass(slots=True)
class LotusAvailability:
    required_available: list[str]
    required_missing: list[str]


@dataclass(slots=True)
class LotusDownloadResult:
    availability: LotusAvailability
    downloaded_files: list[Path]


def pause(page: Page, settings: AppSettings, log, reason: str) -> None:
    seconds = settings.step_delay_seconds
    if seconds <= 0:
        return
    log(f"Waiting {seconds} second(s): {reason}")
    page.wait_for_timeout(seconds * 1000)


def _current_body_text(page: Page) -> str:
    try:
        return (page.locator("body").inner_text() or "").strip()
    except PlaywrightError:
        return ""
    except Exception:
        return ""


def _looks_like_security_checkpoint(body_text: str) -> bool:
    lowered = body_text.lower()
    return any(marker in lowered for marker in SECURITY_MARKERS)


def _looks_like_relogin_required(body_text: str) -> bool:
    return any(marker in body_text for marker in RELOGIN_REQUIRED_MARKERS)


def _is_execution_context_reset(exc: Exception) -> bool:
    return "Execution context was destroyed" in str(exc)


def _login_form_is_visible(page: Page) -> bool:
    try:
        username = page.locator(locators.USERNAME_INPUT)
        password = page.locator(locators.PASSWORD_INPUT)
        secret_code = page.locator(locators.SECRET_CODE_INPUT)
        return (
            username.count() > 0
            and password.count() > 0
            and secret_code.count() > 0
            and username.first.is_visible()
            and password.first.is_visible()
            and secret_code.first.is_visible()
        )
    except PlaywrightError as exc:
        if _is_execution_context_reset(exc):
            return False
        raise


def _security_wait_timeout_ms(settings: AppSettings) -> int:
    if settings.resolve_browser_mode("lotus") in {"manual_assisted", "real_profile"}:
        return MANUAL_ASSISTED_WAIT_TIMEOUT_MS
    return SECURITY_WAIT_TIMEOUT_MS


def _wait_for_login_form(page: Page, settings: AppSettings, log) -> None:
    deadline = monotonic() + (_security_wait_timeout_ms(settings) / 1000)
    challenge_logged = False

    while monotonic() < deadline:
        try:
            if _login_form_is_visible(page):
                return

            body_text = _current_body_text(page)
            if _looks_like_relogin_required(body_text):
                raise LoginError(
                    "Lotus rejected the current login attempt and asked to close the browser and log in again. "
                    "Close all Chrome windows that use the Lotus profile, then retry."
                )
            if _looks_like_security_checkpoint(body_text):
                if settings.resolve_browser_mode("lotus") == "managed":
                    raise LoginError(
                        "Lotus appears to be showing an anti-bot or Cloudflare checkpoint in managed mode. "
                        "Please use LOTUS_BROWSER_MODE=manual_assisted or LOTUS_BROWSER_MODE=real_profile."
                    )
                if not challenge_logged:
                    log(
                        "Lotus appears to be waiting at a security checkpoint. "
                        "Complete the manual verification in the browser window and let the flow continue."
                    )
                    challenge_logged = True
        except PlaywrightError as exc:
            if not _is_execution_context_reset(exc):
                raise

        page.wait_for_timeout(SECURITY_POLL_MS)

    raise LoginError(
        "Lotus login form did not become ready. "
        "The site may still be waiting on a Cloudflare or anti-bot checkpoint. "
        "Use manual-assisted mode and complete the verification in the browser window."
    )


def _wait_for_post_login(page: Page, settings: AppSettings, log) -> None:
    deadline = monotonic() + (max(POST_LOGIN_WAIT_TIMEOUT_MS, _security_wait_timeout_ms(settings)) / 1000)
    challenge_logged = False

    while monotonic() < deadline:
        try:
            post_login_ready = page.locator(locators.POST_LOGIN_READY)
            if post_login_ready.count() > 0 and post_login_ready.first.is_visible():
                return

            body_text = _current_body_text(page)
            if _looks_like_relogin_required(body_text):
                raise LoginError(
                    "Lotus rejected the current login attempt and asked to close the browser and log in again. "
                    "Close all Chrome windows that use the Lotus profile, then retry."
                )
            if _looks_like_security_checkpoint(body_text):
                if settings.resolve_browser_mode("lotus") == "managed":
                    raise LoginError(
                        "Lotus appears to be showing an anti-bot or Cloudflare checkpoint after login submit in managed mode. "
                        "Please use LOTUS_BROWSER_MODE=manual_assisted or LOTUS_BROWSER_MODE=real_profile."
                    )
                if not challenge_logged:
                    log(
                        "Lotus is waiting at a post-login security checkpoint. "
                        "Complete the manual verification in the browser window and let the flow continue."
                    )
                    challenge_logged = True

            if _login_form_is_visible(page):
                lowered = body_text.lower()
                if any(marker in lowered for marker in LOGIN_FAILURE_MARKERS):
                    raise LoginError(
                        "Lotus returned to the login page after submit and appears to be rejecting the credentials or secret code."
                    )
        except PlaywrightError as exc:
            if not _is_execution_context_reset(exc):
                raise

        page.wait_for_timeout(SECURITY_POLL_MS)

    raise LoginError(
        "Lotus did not reach the post-login page after submit. "
        "The site may still be waiting on Cloudflare or another security checkpoint. "
        "Use manual-assisted mode and complete the verification in the browser window."
    )


def _wait_for_manual_login(page: Page, settings: AppSettings, log) -> None:
    log(
        "Lotus manual login is enabled. "
        "Complete the login in the browser window and let the flow continue after the post-login page appears."
    )
    deadline = monotonic() + (MANUAL_LOGIN_WAIT_TIMEOUT_MS / 1000)
    challenge_logged = False

    while monotonic() < deadline:
        try:
            post_login_ready = page.locator(locators.POST_LOGIN_READY)
            if post_login_ready.count() > 0 and post_login_ready.first.is_visible():
                log("Manual Lotus login completed")
                pause(page, settings, log, "after manual login")
                return

            body_text = _current_body_text(page)
            if _looks_like_relogin_required(body_text):
                raise LoginError(
                    "Lotus asked to close the browser and log in again during manual login. "
                    "Close all Chrome windows that use the Lotus profile, then retry."
                )
            if _looks_like_security_checkpoint(body_text) and not challenge_logged:
                log(
                    "Lotus is still at a security checkpoint. "
                    "Complete the verification in the browser window and continue manual login."
                )
                challenge_logged = True
        except PlaywrightError as exc:
            if not _is_execution_context_reset(exc):
                raise

        page.wait_for_timeout(SECURITY_POLL_MS)

    raise LoginError("Timed out waiting for manual Lotus login to reach the post-login page.")


def login(page: Page, settings: AppSettings, log) -> None:
    if not settings.lotus_manual_login and (
        not settings.lotus_username or not settings.lotus_password or not settings.lotus_secret_code
    ):
        raise ConfigurationError("Missing LOTUS_USERNAME, LOTUS_PASSWORD, or LOTUS_SECRET_CODE.")

    post_login_ready = page.locator(locators.POST_LOGIN_READY)
    if post_login_ready.count() > 0 and post_login_ready.first.is_visible():
        log("Lotus session is already on the post-login page")
        return

    log("Opening Lotus login page")
    page.goto(locators.LOGIN_URL, wait_until="domcontentloaded")

    _wait_for_login_form(page, settings, log)

    if settings.lotus_manual_login and settings.resolve_browser_mode("lotus") == "manual_assisted":
        _wait_for_manual_login(page, settings, log)
        return

    try:
        page.locator(locators.USERNAME_INPUT).fill(settings.lotus_username)
        page.locator(locators.PASSWORD_INPUT).fill(settings.lotus_password)
        secret_code_input = page.locator(locators.SECRET_CODE_INPUT)
        secret_code_input.fill(settings.lotus_secret_code)

        agreement = page.locator(locators.AGREEMENT_CHECKBOX)
        if agreement.count() > 0 and agreement.first.is_visible() and not agreement.first.is_checked():
            agreement.first.check()

        login_button = page.locator(locators.LOGIN_BUTTON)
        if login_button.count() > 0 and login_button.first.is_visible():
            login_button.first.click()
        else:
            secret_code_input.press("Enter")

        _wait_for_post_login(page, settings, log)
        log("Login submitted")
        pause(page, settings, log, "after login")
    except Exception as exc:
        body_text = _current_body_text(page)
        if _looks_like_relogin_required(body_text):
            raise LoginError(
                "Lotus rejected the current login attempt and asked to close the browser and log in again. "
                "Close all Chrome windows that use the Lotus profile, then retry."
            ) from exc
        if _login_form_is_visible(page):
            raise LoginError(
                "Lotus login did not reach the post-login page. "
                "Please verify LOTUS_USERNAME, LOTUS_PASSWORD, and LOTUS_SECRET_CODE."
            ) from exc
        raise LoginError("Failed during Lotus login flow.") from exc


def build_no_data_message(run_date: date, missing_items: list[str], details: list[str]) -> str:
    missing_label = ", ".join(missing_items)
    base_message = (
        "No Lotus data was found for "
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
        "Lotus returned partial data for "
        f"run date {run_date.isoformat()}. "
        f"Available: {available_label}. Missing: {missing_label}."
    )
    extra_details = " ".join(detail for detail in details if detail)
    if extra_details:
        return f"{base_message} {extra_details}"
    return base_message


def _save_download_to_temp(download, temp_dir: Path) -> Path:
    path = save_download(download, temp_dir)
    ensure_download_exists(path)
    return path


def _set_readonly_input_value(page: Page, selector: str, value: str) -> None:
    locator = page.locator(selector).first
    locator.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
    locator.evaluate(
        """(element, value) => {
            element.removeAttribute('readonly');
            element.value = value;
            element.dispatchEvent(new Event('input', { bubbles: true }));
            element.dispatchEvent(new Event('change', { bubbles: true }));
            element.dispatchEvent(new Event('blur', { bubbles: true }));
        }""",
        value,
    )


def _visible_zip_entry_names(page: Page, limit: int = 10) -> list[str]:
    entries: list[str] = []
    links = page.locator("xpath=//a[contains(translate(normalize-space(.), 'ZIP', 'zip'), '.zip')]")
    for index in range(min(links.count(), limit)):
        text = links.nth(index).inner_text().strip()
        if text:
            entries.append(text)
    return entries


def download_transaction_zip(page: Page, settings: AppSettings, run_date: date, temp_dir: Path, log) -> Path | None:
    log("Opening Lotus ZIP report menu")
    report_link = page.locator(locators.REPORT_LINK)
    if report_link.count() > 0:
        report_link.first.click()
    else:
        page.goto(locators.REPORT_URL, wait_until="domcontentloaded")
    pause(page, settings, log, "after opening Lotus ZIP report menu")

    short_token = schema.build_short_date_token(run_date)
    long_token = schema.build_long_date_token(run_date)
    zip_selector = f"xpath={locators.build_zip_link_xpath(short_token, long_token)}"
    zip_links = page.locator(zip_selector)
    if zip_links.count() == 0:
        log(f"No Lotus ZIP report entry found for date tokens {short_token} / {long_token}")
        visible_zip_entries = _visible_zip_entry_names(page)
        if visible_zip_entries:
            log(f"Visible Lotus ZIP entries: {', '.join(visible_zip_entries)}")
        else:
            log("No visible Lotus ZIP entries were found on the ZIP report page")
        return None

    log("Downloading Lotus ZIP report")
    with page.expect_download(timeout=DOWNLOAD_TIMEOUT_MS) as download_info:
        zip_links.first.click()
    path = _save_download_to_temp(download_info.value, temp_dir)
    pause(page, settings, log, f"after downloading {path.name}")
    return path


def download_summary_export(page: Page, settings: AppSettings, run_date: date, temp_dir: Path, log) -> Path | None:
    log("Opening Lotus summary report page")
    summary_link = page.locator(locators.SUMMARY_LINK)
    if summary_link.count() > 0:
        summary_link.first.click()
    else:
        page.goto(locators.SUMMARY_URL, wait_until="domcontentloaded")

    wait_for_visible(page, locators.REPORT_TYPE_SELECT, timeout_ms=DEFAULT_TIMEOUT_MS)
    page.locator(locators.REPORT_TYPE_SELECT).select_option(value="RPTHO019")

    input_date = schema.build_summary_input_date(run_date)
    _set_readonly_input_value(page, locators.START_DATE_INPUT, input_date)
    _set_readonly_input_value(page, locators.END_DATE_INPUT, input_date)
    page.locator(locators.SEARCH_BUTTON).click()
    pause(page, settings, log, "after searching Lotus summary report")

    log("Opening Lotus export page")
    export_link = page.locator(locators.EXPORT_LINK)
    if export_link.count() > 0:
        export_link.first.click()
    else:
        page.goto(locators.EXPORT_URL, wait_until="domcontentloaded")

    wait_for_visible(page, locators.START_DATE_INPUT, timeout_ms=DEFAULT_TIMEOUT_MS)
    _set_readonly_input_value(page, locators.START_DATE_INPUT, input_date)
    _set_readonly_input_value(page, locators.END_DATE_INPUT, input_date)

    export_search_button = page.locator(locators.EXPORT_SEARCH_BUTTON)
    if export_search_button.count() == 0 or not export_search_button.first.is_visible():
        log("No Lotus export search button was visible after opening export page")
        return None

    log("Downloading Lotus summary export")
    try:
        with page.expect_download(timeout=DOWNLOAD_TIMEOUT_MS) as download_info:
            export_search_button.first.click()
        path = _save_download_to_temp(download_info.value, temp_dir)
        pause(page, settings, log, f"after downloading {path.name}")
        return path
    except PlaywrightTimeoutError:
        raise DownloadError("Timed out downloading Lotus summary export.")
    except Exception as exc:
        raise DownloadError("Failed to download Lotus summary export.") from exc


def download_web_reports(
    page: Page,
    settings: AppSettings,
    run_date: date,
    temp_dir: Path,
    log,
) -> LotusDownloadResult:
    available_items: list[str] = []
    missing_items: list[str] = []
    details: list[str] = []
    downloaded_files: list[Path] = []

    zip_path = download_transaction_zip(page, settings, run_date, temp_dir, log)
    if zip_path is None:
        missing_items.append("zip report")
    else:
        available_items.append("zip report")
        downloaded_files.append(zip_path)

    summary_path = download_summary_export(page, settings, run_date, temp_dir, log)
    if summary_path is None:
        missing_items.append("summary export")
    else:
        available_items.append("summary export")
        downloaded_files.append(summary_path)

    if missing_items and not available_items:
        raise NoDataError(build_no_data_message(run_date, missing_items, details))

    return LotusDownloadResult(
        availability=LotusAvailability(
            required_available=available_items,
            required_missing=missing_items,
        ),
        downloaded_files=downloaded_files,
    )


def logout(page: Page, settings: AppSettings, log) -> None:
    try:
        wait_for_visible(page, locators.LOGOUT_BUTTON, timeout_ms=DEFAULT_TIMEOUT_MS)
        log("Logging out from Lotus")
        page.locator(locators.LOGOUT_BUTTON).click()
        pause(page, settings, log, "after logout")
    except Exception as exc:
        log(f"Skipping Lotus logout due to a non-fatal error: {exc}")


def validate_downloads(temp_dir: Path, required_web_names: list[str], include_servu: bool, run_date: date) -> None:
    files = {path.name for path in list_files(temp_dir)}
    missing: list[str] = []

    for file_name in required_web_names:
        if file_name not in files:
            missing.append(file_name)

    if include_servu:
        for file_name in schema.build_servu_filenames(run_date):
            if file_name not in files:
                missing.append(file_name)

    if missing:
        if files:
            raise PartialDataError(
                "Lotus workflow returned partial data. "
                f"Missing expected downloaded files: {', '.join(missing)}"
            )
        raise ValidationError(f"Missing expected downloaded files: {', '.join(missing)}")
