from playwright.sync_api import Page


def hover(page: Page, selector: str) -> None:
    page.locator(selector).hover()


def click_after_hover(page: Page, hover_selector: str, click_selector: str) -> None:
    hover(page, hover_selector)
    page.locator(click_selector).click()
