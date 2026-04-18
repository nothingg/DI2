LOGIN_URL = "https://counterservice.co.th/ticketnet/clients/login_ftp.asp"

USERNAME_INPUT = "input[name='username']"
PASSWORD_INPUT = "input[name='password']"
LOGIN_BUTTON = "input[name='B1']"
POST_LOGIN_READY = "a[href='/ticketnet/clients/logout.asp']"
LOGOUT_LINK = POST_LOGIN_READY
DOWNLOAD_LINKS = "a[href*='downloadclientfile.asp']"
LOGIN_ERROR_MESSAGE = "text=USER NAME หรือ PASSWORD"


def build_download_xpath(fragments: list[str]) -> str:
    conditions = " and ".join(f"contains(@href,\"{fragment}\")" for fragment in fragments)
    return f"//a[{conditions}]"
