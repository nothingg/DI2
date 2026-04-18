LOGIN_URL = "https://unicorn.baac.or.th/"

LOGIN_FORM = "#login_form"
USERNAME_INPUT = "#login_form input[name='userid']"
PASSWORD_INPUT = "#login_form input[name='password']"
LOGIN_BUTTON = "#login_form input[type='submit'][name='ok']"
POST_LOGIN_READY = "#logging_string"
WORKSPACE_ROOT = "#item-2024, #item-2025, #item-2026, #folder_pane, #content_pane"

ZIP_DOWNLOAD_BUTTON = "#download_button"
DETAIL_DOWNLOAD_BUTTON = "#download_button_label"
LOGOUT_MENU = "#logging_string"
LOGOUT_LINK = "#action_instance_logout"
ITEM_ID_PREFIX = "[id^='item-']"
CONTENT_ROWS = "#content_pane tr[id^='item-']"


def build_item_selector(item_id: str) -> str:
    return f"#{item_id}"
