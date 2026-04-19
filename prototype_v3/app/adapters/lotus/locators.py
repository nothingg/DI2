LOGIN_URL = "https://easypay.lotuss.com/TescoBPBiller/logon.jsf"
BILLER_BASE_URL = "https://easypay.lotuss.com/TescoBPBiller/jsp/biller"
REPORT_URL = f"{BILLER_BASE_URL}/biller40.jsf"
SUMMARY_URL = f"{BILLER_BASE_URL}/biller01.jsf"
EXPORT_URL = f"{BILLER_BASE_URL}/biller80.jsf"

USERNAME_INPUT = "input[name='formLogin:j_id_jsp_177548282_5']"
PASSWORD_INPUT = "input[name='formLogin:j_id_jsp_177548282_6']"
SECRET_CODE_INPUT = "input[name='formLogin:j_id_jsp_177548282_7']"
AGREEMENT_CHECKBOX = "input[type='checkbox']"
LOGIN_BUTTON = (
    "xpath=//input[(@type='submit' or @type='button') and contains(@value,'เข้า')]"
    " | //button[contains(normalize-space(.),'เข้า')]"
)

POST_LOGIN_READY = "xpath=//img[contains(@src,'icon_logout.png')]"
REPORT_MENU = "xpath=//img[contains(@src,'icon_report.png')]"
REPORT_LINK = "a[href='biller40.jsf']"
HOME_BUTTON = "xpath=//img[contains(@src,'icon_home.png')]"
SUMMARY_MENU = "xpath=//img[contains(@src,'icon_store_summary.png')]"
SUMMARY_LINK = "a[href='biller01.jsf']"
EXPORT_LINK = "a[href='biller80.jsf']"
REPORT_TYPE_SELECT = "select[name='frmBillerMonitor:j_id_jsp_108231391_10']"
START_DATE_INPUT = "[id='frmBillerMonitor:selectStartDateInputDate']"
END_DATE_INPUT = "[id='frmBillerMonitor:selectEndDateInputDate']"
SEARCH_BUTTON = "xpath=//img[contains(@src,'cmd_search_mout.gif')]"
EXPORT_BUTTON = "xpath=//img[contains(@src,'icon_export.png')]"
EXPORT_SEARCH_BUTTON = "xpath=//img[@id='frmBillerMonitor:btnSearch']/ancestor::a[1]"
LOGOUT_BUTTON = POST_LOGIN_READY


def build_zip_link_xpath(short_token: str, long_token: str) -> str:
    return (
        "//a[contains(translate(normalize-space(.), 'ZIP', 'zip'), '.zip') and "
        f"(contains(normalize-space(.), '{short_token}') or contains(normalize-space(.), '{long_token}'))]"
    )
