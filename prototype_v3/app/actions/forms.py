from playwright.sync_api import Page


def fill_text(page: Page, selector: str, value: str) -> None:
    page.locator(selector).fill(value)


def click(page: Page, selector: str) -> None:
    page.locator(selector).click()
