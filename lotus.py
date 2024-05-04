from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils import create_web_driver,move_files
from library.config import source_dir,destination_dir
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import logging


def login(driver, username, password, secret_code):
    driver.get("https://easypay.lotuss.com/")
    time.sleep(5)

    # Switch to the frame
    frame = driver.find_element(By.ID, "mainFrame")
    driver.switch_to.frame(frame)

    input_username =  driver.find_element(By.XPATH, "//input[@name='formLogin:j_id_jsp_177548282_4']")
    input_password = driver.find_element(By.XPATH, "//input[@name='formLogin:j_id_jsp_177548282_5']")
    input_secret_code = driver.find_element(By.XPATH, "//input[@name='formLogin:j_id_jsp_177548282_6']")

    input_username.send_keys(username)
    input_password.send_keys(password)
    input_secret_code.send_keys(secret_code)

    input_secret_code.send_keys(Keys.ENTER)

def download_zip(driver, input_date):

    input_date_obj = datetime.strptime(input_date, '%Y-%m-%d')
    input_date_dmy = input_date_obj.strftime('%d%m%y')

    menu_link = driver.find_element(By.XPATH, "//img[@src='images/icon_report.png']")
    menu_link.click()
    time.sleep(3)

    zip_download =  driver.find_element(By.XPATH, f"//a[text()='TES_GHB_ALL_{input_date_dmy}_{input_date_dmy}.zip']")
    zip_download.click()

def main():
    username = "GHB0001"
    password = "pASSWORD@36"
    secret_code = "3520000101"
    input_date = "2024-04-30"

    try:
        driver = create_web_driver()
        login(driver, username, password, secret_code)
        time.sleep(10)

        download_zip(driver, input_date)
        # logout(driver)


        # move_files(source_dir["default"], destination_dir["true"])

    except Exception as e:
        print('error : ' + str(e))
        logging.error(f"An error occurred in TRUE function: {str(e)}")
    # finally:
    #     driver.quit()

if __name__ == "__main__":
    main()