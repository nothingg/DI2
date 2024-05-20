from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait , Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from utils import create_web_driver, move_files, sftp_servu
from library.config import source_dir, destination_dir, username, password, secret_code, WAIT_TIMES, SERV_U_PATH

from baac import login,logout

import time
import logging
import sys


def adjust_to_friday(date_str):
    # Parse the input date string
    dt = datetime.strptime(date_str, '%Y-%m-%d')

    # Check if the date is a Saturday (5) or Sunday (6)
    if dt.weekday() == 5:  # Saturday
        dt -= timedelta(days=1)  # Go back 1 day to Friday
    elif dt.weekday() == 6:  # Sunday
        dt -= timedelta(days=2)  # Go back 2 days to Friday

    return dt.strftime('%Y-%m-%d')

def statement_ghb(driver, input_date):
    try :
        # Convert input_date to a datetime object
        input_date = adjust_to_friday(input_date)
        input_date_obj = datetime.strptime(input_date, '%Y-%m-%d')
        input_date_ymd = input_date_obj.strftime("%Y%m%d")
        input_date_ym = input_date_obj.strftime("%Y%m")
        input_date_y = input_date_obj.strftime("%Y")

        url_date_ym = "https://unicorn.baac.or.th/ws-statement-GHB1/"
        driver.get(url_date_ym)
        time.sleep(WAIT_TIMES["30"])

        css_row_y = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.element_to_be_clickable((By.ID, f"item-{input_date_y}-cont")))
        driver.execute_script("arguments[0].click();", css_row_y)
        driver.execute_script(
            "arguments[0].dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true }));",
            css_row_y)
        time.sleep(WAIT_TIMES["5"])

        css_row_ym = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.element_to_be_clickable((By.ID, f"item-{input_date_ym}-cont")))
        # Scroll the webpage to bring the element into view
        driver.execute_script("arguments[0].scrollIntoView();", css_row_ym)
        driver.execute_script("arguments[0].click();", css_row_ym)
        driver.execute_script(
            "arguments[0].dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true }));",
            css_row_ym)
        time.sleep(WAIT_TIMES["5"])


        css_row_ymd = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.presence_of_element_located((By.ID, f"item-{input_date_ymd}-cont")))
        # Scroll the webpage to bring the element into view
        driver.execute_script("arguments[0].scrollIntoView();", css_row_ymd)
        driver.execute_script("arguments[0].click();", css_row_ymd)
        driver.execute_script(
            "arguments[0].dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true }));",
            css_row_ymd)
        time.sleep(WAIT_TIMES["5"])

        # Wait for the content pane to be clickable and then click
        css_content = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.element_to_be_clickable((By.ID, "content_pane")))
        css_content.click()

        # Wait for the download button label to be clickable and then click
        css_download = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.element_to_be_clickable((By.ID, "download_button_label")))
        css_download.click()

    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("BAAC_STMT : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        raise  # Raise the exception to be caught by the main function
    except Exception as e:
        logging.error(f"BAAC_STMT: An error occurred: {str(e)}", exc_info=True)
        raise  # Raise the exception to be caught by the main function


def main(input_date = None):
    # input_date = "2024-05-19"
    if input_date is None:
        input_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        driver = create_web_driver()
        login(driver)

        #ที่ต้องใส่ deley เพราะว่า BOT เรียก URL เร็วเกินไป
        time.sleep(WAIT_TIMES["10"])

        statement_ghb(driver,input_date)
        time.sleep(WAIT_TIMES["5"])

        logout(driver)
        move_files(source_dir["default"], destination_dir(input_date, "baac"))
        driver.quit()
    except Exception as e:
        print('error : ' + str(e))
        logging.error(f"An error occurred in BAAC_STMT function: {str(e)}" , exc_info=True )
        raise  # Raise the exception to be caught by the main function
    # finally:
    #     driver.quit()

if __name__ == "__main__":
    main()