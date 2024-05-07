from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait , Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from utils import create_web_driver,move_files
from library.config import source_dir,destination_dir,username,password,secret_code,WAIT_TIMES

import time
import logging
import sys

# Configure logging
logging.basicConfig(filename='error.log', format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

def login(driver):
    try :
        # Perform login with provided credentials
        driver.get("https://counterservice.co.th/ticketnet/clients/login_ftp.asp")

        input_username = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.element_to_be_clickable((By.NAME, "username")))
        input_password = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.element_to_be_clickable((By.NAME, "password")))
        login_button = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.element_to_be_clickable((By.NAME, "B1")))

        input_username.send_keys(username["counter_service"])
        input_password.send_keys(password["counter_service"])

        login_button.click()

    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("Couter Service : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    except Exception as e:
        logging.error(f"Couter Service: An error occurred: {str(e)}", exc_info=True)
        sys.exit(1)  # Exit the program with an error code

def logout(driver):
    # Logout from the system
    try :
        logout_link = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/ticketnet/clients/logout.asp']")))
        logout_link.click()

    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("Couter Service : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    except Exception as e:
        logging.error(f"Couter Service: An error occurred: {str(e)}", exc_info=True)
        sys.exit(1)  # Exit the program with an error code

def download_files(driver, input_date):
    try :
        # Convert input_date to a datetime object
        input_date_obj = datetime.strptime(input_date, '%Y-%m-%d')
        yesterday = input_date_obj - timedelta(days=1)
        input_date_md = input_date_obj.strftime("%m%d")
        gco_formatted_yesterday = yesterday.strftime("%Y%m%d")
        rp_formatted_yesterday = yesterday.strftime("%d%m%y")

        # Download files using WebDriver
        ahref = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.presence_of_element_located(
            (By.XPATH, f"//a[@href='downloadclientfile.asp?file=GHB\\261{input_date_md}%2Ezip']")))
        ahref.click()
        time.sleep(WAIT_TIMES["5"])

        indcr_link = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.presence_of_element_located((By.XPATH,
                                                              f"//a[@href='downloadclientfile.asp?file=GHB\\INDCR0000000003300000264{gco_formatted_yesterday}001%2Etxt']")))
        indcr_link.click()
        time.sleep(WAIT_TIMES["5"])

        # Try to find and download the GCO file, log a warning if not found
        try:
            gco_link = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.element_to_be_clickable(
                (By.XPATH, f"//a[@href='downloadclientfile.asp?file=GHB\\gco261{input_date_md}%2Ezip']")))
            gco_link.click()
            time.sleep(WAIT_TIMES["5"])
        except TimeoutException:
            logger = logging.getLogger()
            logger.setLevel(logging.WARNING)
            logger.warning(f"Couter Service ({input_date_obj}) : can't find gco file")

        report_link = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.element_to_be_clickable(
            (By.XPATH, f"//a[@href='downloadclientfile.asp?file=GHB\\Report%5FGHB%5F{rp_formatted_yesterday}%2Ezip']")))
        report_link.click()
        time.sleep(WAIT_TIMES["5"])

    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("Couter Service : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    except Exception as e:
        logging.error(f"Couter Service: An error occurred: {str(e)}", exc_info=True)
        sys.exit(1)  # Exit the program with an error code

def main():
    input_date = "2024-05-01"

    try:
        driver = create_web_driver()
        login(driver)
        time.sleep(WAIT_TIMES["5"])
        download_files(driver,input_date)
        logout(driver)
        move_files(source_dir["default"], destination_dir["counter_service"])

    except Exception as e:
        print('error : ' + str(e))
        logging.error(f"An error occurred in counter_service function: {str(e)}", exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    finally:
        driver.quit()

if __name__ == "__main__":
    main()