from selenium.webdriver.common.action_chains import ActionChains
from utils import create_web_driver , move_files
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import time
import logging

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

def login(driver, username, password):
    # Perform login with provided credentials
    driver.get("https://mpaystation.ais.co.th/AISPayStationGenWeb/authenUser")

    input_username = driver.find_element(By.NAME, "username")
    input_password = driver.find_element(By.NAME, "password")
    login_button = driver.find_element(By.NAME, "login")

    input_username.send_keys(username)
    input_password.send_keys(password)
    time.sleep(3)

    login_button.click()

def logout(driver):
    # Logout from the system
    logout_link = driver.find_element(By.XPATH, "//a[@href='/AISPayStationGenWeb/index.jsp']")
    logout_link.click()
    time.sleep(3)

def download_xmlfile(driver):
    href = "/AISPayStationGenWeb/report"
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    txt_dated_yesterday = yesterday.strftime("%Y%m%d")

    main_menu = driver.find_element(By.XPATH, "//a[@href='#']")

    # Create an ActionChains object
    actions = ActionChains(driver)

    # Perform mouse hover action on the main UL element
    actions.move_to_element(main_menu).perform()
    time.sleep(3)

    xml_menu = driver.find_element(By.XPATH, "//a[@href='/AISPayStationGenWeb/report']")
    xml_menu.click()
    time.sleep(10)

    xml_link = driver.find_element(By.XPATH, f"//input[contains(@onclick, 'AIS{txt_dated_yesterday}.xml')]")
    xml_link.click()
    time.sleep(10)

#TODO : find element PDF
    pdf_link = driver.find_element(By.XPATH, f"//a[contains(@onclick, 'AIS{txt_dated_yesterday}.xml')]")
    pdf_link.click()
    time.sleep(3)

def download_txtfile(driver):

    today = datetime.now()
    yesterday = today - timedelta(days=1)
    txt_dated_yesterday = yesterday.strftime("%Y%m%d")


    main_menu = driver.find_element(By.XPATH, "//a[@href='#']")

    # Create an ActionChains object
    actions = ActionChains(driver)

    # Perform mouse hover action on the main UL element
    actions.move_to_element(main_menu).perform()
    time.sleep(3)

    txt_menu = driver.find_element(By.XPATH, "//a[@href='/AISPayStationGenWeb/text']")
    txt_menu.click()
    time.sleep(3)

    # Download files using WebDriver

    # txt_link = driver.find_element(By.XPATH, f"//a[@href='javascript:loadFile(\'AIS{txt_dated_yesterday}.log\');']")
    xpath_expression = f"//a[contains(@href, 'AIS{txt_dated_yesterday}.log')]"
    txt_link = driver.find_element(By.XPATH, xpath_expression)
    txt_link.click()
    time.sleep(3)

def main():
    username = "govebank"
    password = "G0veB@nK"

    try:
        driver = create_web_driver()
        login(driver, username, password)
        time.sleep(3)

        download_txtfile(driver)
        time.sleep(3)

        download_xmlfile(driver)
        time.sleep(3)

        # logout(driver)

    except Exception as e:
        print('error : ' + str(e))
        logging.error(f"An error occurred in mPay function: {str(e)}")
    # finally:
    #     driver.quit()

if __name__ == "__main__":
    main()