from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait , Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from library.utils import create_web_driver, move_files, sftp_servu
from library.config import source_dir, destination_dir, username, password, secret_code, WAIT_TIMES, SERV_U_PATH

import logging

# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

def login(driver):
    try :
        driver.get("https://easypay.lotuss.com/")

        # Switch to the frame
        WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.frame_to_be_available_and_switch_to_it("mainFrame"))

        # Find the username, password, and secret code input fields
        input_username = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='formLogin:j_id_jsp_177548282_4']")))
        input_password = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='formLogin:j_id_jsp_177548282_5']")))
        input_secret_code = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='formLogin:j_id_jsp_177548282_6']")))

        # Send keys to all input fields
        input_username.send_keys(username["lotus"])
        input_password.send_keys(password["lotus"])
        input_secret_code.send_keys(secret_code["lotus"])

        # Submit the form by pressing Enter on the secret code field
        input_secret_code.send_keys(Keys.ENTER)

    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("Lotus : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        raise  # Raise the exception to be caught by the main function
    except Exception as e:
        error_message = str(e)
        logging.error(f"Lotus : An error occurred: {error_message}", exc_info=True)
        raise  # Raise the exception to be caught by the main function

def logout(driver):
    try :
        btn_logout = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.element_to_be_clickable((By.XPATH, "//img[@src='images/icon_logout.png']")))
        btn_logout.click()

    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("Lotus : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        raise  # Raise the exception to be caught by the main function
    except Exception as e:
        error_message = str(e)
        logging.error(f"Lotus : An error occurred: {error_message}", exc_info=True)
        raise  # Raise the exception to be caught by the main function

def download_zip(driver, input_date):
    try :
        input_date_obj = datetime.strptime(input_date, '%Y-%m-%d')
        input_date_dmy = input_date_obj.strftime('%d%m%y')

        menu_link = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.element_to_be_clickable((By.XPATH, "//img[@src='images/icon_report.png']")))
        menu_link.click()

        zip_download = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[text()='TES_GHB_ALL_{input_date_dmy}_{input_date_dmy}.zip']")))
        zip_download.click()

    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("Lotus : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        raise  # Raise the exception to be caught by the main function
    except Exception as e:
        error_message = str(e)
        logging.error(f"Lotus : An error occurred: {error_message}", exc_info=True)
        raise  # Raise the exception to be caught by the main function
def download_summary(driver, input_date):
    try :
        input_date_obj = datetime.strptime(input_date, '%Y-%m-%d')
        input_date_dmy = input_date_obj.strftime('%d/%m/%Y')

        home_link = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.element_to_be_clickable((By.XPATH, "//img[@src='images/icon_home.png']")))
        home_link.click()

        summary_link = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.element_to_be_clickable((By.XPATH, "//img[@src='images/icon_store_summary.png']")))
        summary_link.click()

        # Select Report in dropdownlist
        dropdown = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.element_to_be_clickable((By.NAME, "frmBillerMonitor:j_id_jsp_108231391_10")))

        # Create a Select object
        select = Select(dropdown)

        # Select the option by its value
        select.select_by_value("RPTHO019")

        start_date = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.presence_of_element_located((By.ID,"frmBillerMonitor:selectStartDate")))

        end_date = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.presence_of_element_located((By.ID, "frmBillerMonitor:selectEndDate")))

        btn_search = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.element_to_be_clickable((By.XPATH, "//img[@src='images/cmd_search_mout.gif']")))

        start_date.clear()
        end_date.clear()
        start_date.send_keys(input_date_dmy)
        end_date.send_keys(input_date_dmy)
        btn_search.click()

        #ที่เอาไว้ตรงนี้เพราะต้องกด btn serach ก่อนแล้วหน้าจะ refresh แล้วค่อยค้นหา btn export
        btn_export = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.element_to_be_clickable((By.XPATH, "//img[@src='images/icon_export.png']")))
        btn_export.click()

    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("Lotus : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        raise  # Raise the exception to be caught by the main function
    except Exception as e:
        error_message = str(e)
        logging.error(f"Lotus : An error occurred: {error_message}" , exc_info=True)
        raise  # Raise the exception to be caught by the main function

def download_servu(input_date):
    try :
        input_date_obj = datetime.strptime(input_date, '%Y-%m-%d')
        input_date_ymd = input_date_obj.strftime("%Y%m%d")
        filename_txt = f"INDCR0000000003300000230{input_date_ymd}001.TXT"
        filename_zip = f"REDCR0000000003300000230{input_date_ymd}001.zip"

        sftp_servu(SERV_U_PATH["lotus"], filename_txt)
        sftp_servu(SERV_U_PATH["lotus"], filename_zip)

    except Exception as e:
        logging.error(f"Lotus Service: An error occurred: {str(e)}", exc_info=True)
        raise  # Raise the exception to be caught by the main function

def main(input_date = None):
    # input_date = "2024-05-25"
    if input_date is None:
        input_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        driver = create_web_driver()
        login(driver)
        download_zip(driver, input_date)
        download_summary(driver,input_date)
        logout(driver)
        download_servu(input_date)
        move_files(source_dir["default"], destination_dir(input_date, "lotus"))
        driver.quit()

    except Exception as e:
        print('error : ' + str(e))
        logging.error(f"An error occurred in Lotus function: {str(e)}" , exc_info=True)
        raise  # Raise the exception to be caught by the main function
    # finally:
    #     driver.quit()

if __name__ == "__main__":
    main()