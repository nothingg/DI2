from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError


def wait_for_network_idle(page: Page, timeout_ms: int = 10000) -> None:
    page.wait_for_load_state("networkidle", timeout=timeout_ms)


def wait_for_page_ready(page: Page, timeout_ms: int = 10000) -> None:
    page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)


def wait_for_visible(page: Page, selector: str, timeout_ms: int = 10000) -> None:
    page.locator(selector).first.wait_for(state="visible", timeout=timeout_ms)


def wait_for_any_visible(page: Page, selectors: list[str], timeout_ms: int = 10000) -> str:
    last_error: Exception | None = None
    for selector in selectors:
        try:
            wait_for_visible(page, selector, timeout_ms=timeout_ms)
            return selector
        except PlaywrightTimeoutError as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    raise PlaywrightTimeoutError("No selectors were provided to wait_for_any_visible.")


def wait_step_delay(page: Page, seconds: int) -> None:
    if seconds <= 0:
        return
    page.wait_for_timeout(seconds * 1000)
