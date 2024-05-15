from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait , Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from utils import create_web_driver,move_files,servu_download
from library.config import source_dir,destination_dir,username,password,secret_code,WAIT_TIMES,SERV_U_PATH

import time
import logging
import sys

# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

def login(driver):
    try :
        # Perform login with provided credentials
        driver.get("https://mpaystation.ais.co.th/AISPayStationGenWeb/authenUser?command=start")

        input_username = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.element_to_be_clickable((By.NAME, "username")))
        input_password = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.element_to_be_clickable((By.NAME, "password")))
        login_button = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.element_to_be_clickable((By.NAME, "login")))

        input_username.send_keys(username["mpay"])
        input_password.send_keys(password["mpay"])

        login_button.click()

    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("mPay : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    except Exception as e:
        logging.error(f"mPay Service: An error occurred: {str(e)}", exc_info=True)
        sys.exit(1)  # Exit the program with an error code

def logout(driver):
    try :
        # Logout from the system
        logout_link = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/AISPayStationGenWeb/index.jsp']")))
        logout_link.click()
    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("mPay : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    except Exception as e:
        logging.error(f"mPay Service: An error occurred: {str(e)}", exc_info=True)
        sys.exit(1)  # Exit the program with an error code

def download_xmlfile(driver, input_date):
    try :
        input_date_obj = datetime.strptime(input_date, '%Y-%m-%d')
        txt_dated = input_date_obj.strftime("%Y%m%d")

        main_menu = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.element_to_be_clickable((By.XPATH, "//a[@href='#']")))

        # Create an ActionChains object
        actions = ActionChains(driver)

        # Perform mouse hover action on the main UL element
        actions.move_to_element(main_menu).perform()
        time.sleep(WAIT_TIMES["5"])

        xml_menu = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/AISPayStationGenWeb/report']")))
        xml_menu.click()
        time.sleep(WAIT_TIMES["5"])

        xml_link = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.element_to_be_clickable((By.XPATH, f"//input[contains(@onclick, 'AIS{txt_dated}.xml')]")))
        xml_link.click()
        time.sleep(WAIT_TIMES["5"])

        # TODO : PDF file can't donwload , it's download manual
        # Switch to the new tab
        driver.switch_to.window(driver.window_handles[1])

        pdf_link = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(@onclick, 'AIS{txt_dated}.xml')]")))
        pdf_link.click()
        time.sleep(WAIT_TIMES["5"])

        driver.switch_to.window(driver.window_handles[0])

    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("mPay : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    except Exception as e:
        logging.error(f"mPay Service: An error occurred: {str(e)}", exc_info=True)
        sys.exit(1)  # Exit the program with an error code

def download_servu_mpay(input_date):

    input_date_obj = datetime.strptime(input_date, '%Y-%m-%d')
    input_date_ymd = input_date_obj.strftime("%Y%m%d")
    filename = f"INDCR0000000003300000221{input_date_ymd}001.TXT"
    servu_download(SERV_U_PATH["counter_service"],filename )

def download_txtfile(driver,input_date):
    try :
        input_date_obj = datetime.strptime(input_date, '%Y-%m-%d')
        txt_dated = input_date_obj.strftime("%Y%m%d")

        main_menu = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.element_to_be_clickable((By.XPATH, "//a[@href='#']")))

        # Create an ActionChains object
        actions = ActionChains(driver)

        # Perform mouse hover action on the main UL element
        actions.move_to_element(main_menu).perform()

        txt_menu = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/AISPayStationGenWeb/text']")))
        txt_menu.click()

        # Download files using WebDriver
        xpath_expression = f"//a[contains(@href, 'AIS{txt_dated}.log')]"
        txt_link = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.element_to_be_clickable((By.XPATH, xpath_expression)))
        txt_link.click()

    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("mPay : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    except Exception as e:
        logging.error(f"mPay Service: An error occurred: {str(e)}", exc_info=True)
        sys.exit(1)  # Exit the program with an error code

def main():
    input_date = "2024-05-14"
    try:
        driver = create_web_driver()
        login(driver)
        time.sleep(WAIT_TIMES["5"])

        download_txtfile(driver,input_date)
        time.sleep(WAIT_TIMES["5"])

        download_xmlfile(driver,input_date)
        time.sleep(WAIT_TIMES["5"])

        logout(driver)
        download_servu_mpay(input_date)
        move_files(source_dir["default"], destination_dir(input_date, "mpay"))

    except Exception as e:
        print('error : ' + str(e))
        logging.error(f"An error occurred in mPay function: {str(e)}", exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    # ไม่ต้องมี finally เนื่องจาก load pdf ไม่ได้ ต้อง manual load
    # finally:
    #     driver.quit()

if __name__ == "__main__":
    main()