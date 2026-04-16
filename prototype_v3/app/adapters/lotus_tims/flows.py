from __future__ import annotations

from pathlib import Path
import re
from time import monotonic

from playwright.sync_api import Frame, Page

from app.adapters.lotus_tims import locators, schema
from app.browser.downloads import ensure_download_exists, save_download
from app.core.config import AppSettings
from app.core.errors import ConfigurationError, DownloadError, LoginError, NoDataError

DEFAULT_TIMEOUT_MS = 10000
DOWNLOAD_TIMEOUT_MS = 15000
FRAME_POLL_MS = 250
DATE_PATTERN = re.compile(r"\b\d{2}-[A-Za-z]{3}-\d{4}\b")


def pause(page: Page, settings: AppSettings, log, reason: str) -> None:
    seconds = settings.step_delay_seconds
    if seconds <= 0:
        return
    log(f"Waiting {seconds} second(s): {reason}")
    page.wait_for_timeout(seconds * 1000)


def summarize_available_dates(row_summaries: list[str]) -> str:
    dates: list[str] = []
    for row_text in row_summaries:
        for value in DATE_PATTERN.findall(row_text):
            if value not in dates:
                dates.append(value)
    if not dates:
        return "No visible document dates were detected on screen."
    preview = ", ".join(dates[:5])
    if len(dates) > 5:
        return f"Available document dates on screen: {preview}, ..."
    return f"Available document dates on screen: {preview}"


def wait_for_frame(page: Page, frame_name: str, timeout_ms: int = DEFAULT_TIMEOUT_MS) -> Frame:
    deadline = monotonic() + (timeout_ms / 1000)
    while monotonic() < deadline:
        frame = page.frame(name=frame_name)
        if frame is not None:
            return frame
        page.wait_for_timeout(FRAME_POLL_MS)
    raise DownloadError(f"Frame was not available: {frame_name}")


def login(page: Page, settings: AppSettings, log) -> None:
    if not settings.lotus_tims_username or not settings.lotus_tims_password:
        raise ConfigurationError("Missing LOTUS_TIMS_USERNAME or LOTUS_TIMS_PASSWORD.")

    log("Opening Lotus TIMS login page")
    page.goto(locators.LOGIN_URL, wait_until="domcontentloaded")
    appl_frame = wait_for_frame(page, locators.APPL_FRAME)

    try:
        appl_frame.locator(locators.USERNAME_INPUT).wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        appl_frame.locator(locators.PASSWORD_INPUT).wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        appl_frame.locator(locators.USERNAME_INPUT).fill(settings.lotus_tims_username)
        password_input = appl_frame.locator(locators.PASSWORD_INPUT)
        password_input.fill(settings.lotus_tims_password)
        password_input.press("Enter")
        appl_frame.locator(locators.POST_LOGIN_OK_BUTTON).wait_for(
            state="visible",
            timeout=DEFAULT_TIMEOUT_MS,
        )
        log("Login submitted")
        pause(page, settings, log, "after login")
    except Exception as exc:
        raise LoginError("Failed during Lotus TIMS login flow.") from exc


def accept_post_login_prompt(page: Page, settings: AppSettings, log) -> None:
    log("Accepting Lotus TIMS post-login prompt")
    appl_frame = wait_for_frame(page, locators.APPL_FRAME)
    appl_frame.locator(locators.POST_LOGIN_FORM).hover()
    appl_frame.locator(locators.HOME_LINK).hover()
    appl_frame.locator(locators.POST_LOGIN_OK_BUTTON).click()
    pause(page, settings, log, "after acknowledging post-login prompt")


def open_payment_detail_menu(page: Page, settings: AppSettings, log) -> None:
    log("Opening Lotus TIMS payment detail menu")
    menu_frame = wait_for_frame(page, locators.MENU_FRAME)
    payment_detail_container = menu_frame.locator(locators.PAYMENT_DETAIL_MENU_CONTAINER)
    payment_detail_menu = menu_frame.locator(locators.PAYMENT_DETAIL_MENU)

    menu_frame.locator(locators.DOCUMENT_MENU).wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)

    # This legacy menu is driven by inline JavaScript. Pointer interactions are brittle
    # because the popup menu can intercept the mouse, so we trigger the same JS path
    # that the menu uses in the page itself.
    menu_frame.evaluate(
        """
        () => {
            const menuRoot = document.getElementById('_MCELL4');
            if (!menuRoot) {
                throw new Error('Lotus TIMS document menu root was not found');
            }
            menuRoot.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
            if (typeof invoke === 'function') {
                invoke('FLRAHeadTh');
                return;
            }
            const item = Array.from(document.querySelectorAll('#_MENU_0 td'))
                .find((cell) => cell.textContent && cell.textContent.includes('ใบแจ้งรายละเอียดการชำระเงิน'));
            if (!item) {
                throw new Error('Lotus TIMS payment detail submenu item was not found');
            }
            item.click();
        }
        """
    )

    payment_detail_container.wait_for(state="attached", timeout=DEFAULT_TIMEOUT_MS)
    payment_detail_menu.wait_for(state="attached", timeout=DEFAULT_TIMEOUT_MS)
    pause(page, settings, log, "after opening document menu")


def search_documents(page: Page, settings: AppSettings, log) -> None:
    log("Searching Lotus TIMS documents")
    appl_frame = wait_for_frame(page, locators.APPL_FRAME)
    appl_frame.locator(locators.REPORT_TYPE_SELECT).wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
    appl_frame.locator(locators.REPORT_TYPE_SELECT).select_option(value="")
    appl_frame.locator(locators.SEARCH_BUTTON).click()
    appl_frame.locator(locators.REPORT_ROWS).first.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
    pause(page, settings, log, "after searching documents")


def download_report(page: Page, settings: AppSettings, run_date, temp_dir: Path, log) -> Path:
    lookup_label = schema.build_lookup_label(run_date)
    log(f"Downloading Lotus TIMS report for document date: {lookup_label}")
    appl_frame = wait_for_frame(page, locators.APPL_FRAME)
    rows = appl_frame.locator(locators.REPORT_ROWS)
    row_count = rows.count()

    matching_row = None
    row_summaries: list[str] = []
    for index in range(row_count):
        row = rows.nth(index)
        row_text = " ".join((row.text_content() or "").split())
        if row_text:
            row_summaries.append(row_text)
        if lookup_label in row_text:
            matching_row = row
            break

    if matching_row is None:
        available_dates = summarize_available_dates(row_summaries)
        raise NoDataError(
            "No Lotus TIMS report was found for "
            f"document date {lookup_label} "
            f"(selected run date {run_date.isoformat()}). "
            "This usually means the selected date is wrong or the source has not published data yet. "
            f"{available_dates}"
        )

    try:
        with page.expect_download(timeout=DOWNLOAD_TIMEOUT_MS) as download_info:
            matching_row.locator(locators.ROW_RTF_ICON).click()
            appl_frame.locator(locators.SAVE_FILE_CELL).wait_for(
                state="visible",
                timeout=DEFAULT_TIMEOUT_MS,
            )
            appl_frame.locator(locators.SAVE_FILE_CELL).click()
        download = download_info.value
        path = save_download(download, temp_dir)
        ensure_download_exists(path)
        pause(page, settings, log, "after downloading report")
        return path
    except Exception as exc:
        raise DownloadError(f"Failed to download Lotus TIMS report for {lookup_label}") from exc


def logout(page: Page, settings: AppSettings, log) -> None:
    try:
        log("Logging out from Lotus TIMS")
        menu_frame = wait_for_frame(page, locators.MENU_FRAME)
        menu_frame.locator(locators.LOGOUT_MENU).wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        menu_frame.evaluate(
            """
            () => {
                if (typeof invoke === 'function') {
                    invoke('FDLogout');
                    return;
                }
                const logoutItem = document.querySelector('#_MCELL0');
                if (!logoutItem) {
                    throw new Error('Lotus TIMS logout menu item was not found');
                }
                logoutItem.click();
            }
            """
        )
        appl_frame = wait_for_frame(page, locators.APPL_FRAME)
        appl_frame.locator(locators.CONFIRM_LOGOUT_BUTTON).wait_for(
            state="visible",
            timeout=DEFAULT_TIMEOUT_MS,
        )
        appl_frame.locator(locators.CONFIRM_LOGOUT_BUTTON).click(force=True)
        pause(page, settings, log, "after logout")
    except Exception as exc:
        log(f"Skipping Lotus TIMS logout due to a non-fatal error: {exc}")
