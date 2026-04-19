LOGIN_URL = "https://pago.truecorp.co.th/tmnos-wdl/ghb"

USERNAME_INPUT = "input[type='text'][placeholder='Username'][autocomplete='off']"
PASSWORD_INPUT = "input[type='password'][placeholder='Password'][autocomplete='off']"
LOGIN_BUTTON = "button"
LOGIN_ERROR_MESSAGE = ".error-message"
POST_LOGIN_READY = ".button-logout"

DATE_INPUT = "input[placeholder='Select date']"
PREVIOUS_MONTH_BUTTON = ".ant-calendar-prev-month-btn"
NEXT_MONTH_BUTTON = ".ant-calendar-next-month-btn"
SEARCH_BUTTON = ".primary"
LOGOUT_BUTTON = ".button-logout"


def build_calendar_day_selector(title: str) -> str:
    return f"td[title='{title}']"


def build_download_row_selector(file_name: str) -> str:
    return f"//div[@class='name']/span[text()='{file_name}']"
