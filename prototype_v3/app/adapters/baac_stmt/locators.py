LOGIN_URL = "https://unicorn.baac.or.th/"

LOGIN_FORM = "#login_form"
USERNAME_INPUT = "#login_form input[name='userid']"
PASSWORD_INPUT = "#login_form input[name='password']"
LOGIN_BUTTON = "#login_form input[type='submit'][name='ok']"
POST_LOGIN_READY = "#logging_string"

WORKSPACE_REFRESH = ".ajxp-goto-refresh"
WORKSPACE_ROOT = "#content_pane, #selectable_div-5, .ajxp-goto-refresh"
ITEM_ID_PREFIX = "[id^='item-']"
CONTENT_ROWS = "#selectable_div-5 [id^='item-']"
DOWNLOAD_BUTTON = "#download_button"

LOGOUT_MENU = "#logging_string"
LOGOUT_LINK = "#action_instance_logout"


def build_item_selector(item_id: str) -> str:
    return f"#{item_id}"
