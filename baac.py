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
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

def login(driver):
    try :
        driver.get("https://unicorn.baac.or.th/")
        time.sleep(WAIT_TIMES["10"])

        input_username = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.visibility_of_element_located((By.NAME, "userid")))
        input_password = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.visibility_of_element_located((By.NAME, "password")))

        input_username.send_keys(username["baac"])
        input_password.send_keys(password["baac"])
        input_password.send_keys(Keys.ENTER)

    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("BAAC : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    except Exception as e:
        logging.error(f"BAAC: An error occurred: {str(e)}", exc_info=True)
        sys.exit(1)  # Exit the program with an error code

def logout(driver):
    try :
        main_menu = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.presence_of_element_located((By.ID, "logging_string")))

        # Create an ActionChains object
        actions = ActionChains(driver)

        # Perform mouse hover action on the main UL element
        actions.move_to_element(main_menu).perform()

        logout_link = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.element_to_be_clickable((By.ID, "action_instance_logout")))
        logout_link.click()

    except TimeoutException as t:
        logging.error("BAAC : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    except Exception as e:
        logging.error(f"BAAC: An error occurred: {str(e)}", exc_info=True)
        sys.exit(1)  # Exit the program with an error code


def payment_l001_new(driver, input_date):
    try :
        input_date_obj = datetime.strptime(input_date, '%Y-%m-%d')
        yesterday = input_date_obj - timedelta(days=1)
        input_date_ymd = input_date_obj.strftime("%Y/%m/%d")

        # Page Zip
        url_date_ym = "https://unicorn.baac.or.th/ws-payment-l001/" + yesterday.strftime("%Y/%m")
        driver.get(url_date_ym)

        # Wait for the element to be clickable and then click
        span_payment = WebDriverWait(driver, WAIT_TIMES["30"]).until(
            EC.presence_of_element_located((By.XPATH, f"//span[@class='text_label' and contains(text(), '{input_date_ymd}')]")))

        # Scroll the webpage to bring the element into view
        driver.execute_script("arguments[0].scrollIntoView();", span_payment)

        # Click on the element using JavaScript
        driver.execute_script("arguments[0].click();", span_payment)
        # span_payment.click()

        # Wait for the download button to be clickable and then click
        css_download_zip = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.element_to_be_clickable((By.ID, "download_button")))
        css_download_zip.click()

        # Page Detail
        # Perform a double click on the element using JavaScript
        driver.execute_script(
            "arguments[0].dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true }));", span_payment)
        time.sleep(WAIT_TIMES["10"])

        file_ymd = yesterday.strftime("%Y%m%d")
        css_download = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.presence_of_element_located((By.ID, "download_button_label")))

        css_id_row_dc106 = "item-" + file_ymd + "dc106l001" + file_ymd + "pdf"
        css_row_dc106 = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.element_to_be_clickable((By.ID, css_id_row_dc106)))
        css_row_dc106.click()
        css_download.click()
        time.sleep(WAIT_TIMES["5"])

        css_id_row_dc105 = "item-" + file_ymd + "dc105l001" + file_ymd + "pdf"
        css_row_dc105 = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.element_to_be_clickable((By.ID, css_id_row_dc105)))
        css_row_dc105.click()
        css_download.click()

    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("BAAC : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    except Exception as e:
        logging.error(f"BAAC: An error occurred: {str(e)}", exc_info=True)
        sys.exit(1)  # Exit the program with an error code

def statement_ghb(driver, input_date):
    try :
        # Convert input_date to a datetime object
        input_date_obj = datetime.strptime(input_date, '%Y-%m-%d')
        yesterday = input_date_obj - timedelta(days=1)

        url_date_ym = "https://unicorn.baac.or.th/ws-statement-GHB1/" + yesterday.strftime("%Y/%m/%d")
        driver.get(url_date_ym)
        time.sleep(WAIT_TIMES["30"])

        # Wait for the content pane to be clickable and then click
        css_content = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.element_to_be_clickable((By.ID, "content_pane")))
        css_content.click()

        # Wait for the download button label to be clickable and then click
        css_download = WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.element_to_be_clickable((By.ID, "download_button_label")))
        css_download.click()

    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("BAAC : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    except Exception as e:
        logging.error(f"BAAC: An error occurred: {str(e)}", exc_info=True)
        sys.exit(1)  # Exit the program with an error code

def main():
    input_date = "2024-04-30"

    try:
        driver = create_web_driver()
        login(driver)

        #ที่ต้องใส่ delet เพราะว่า BOT เรียก URL เร็วเกินไป
        time.sleep(WAIT_TIMES["10"])
        payment_l001_new(driver,input_date)
        statement_ghb(driver,input_date)
        time.sleep(WAIT_TIMES["5"])
        logout(driver)
        move_files(source_dir["default"], destination_dir["counter_service"])

    except Exception as e:
        print('error : ' + str(e))
        logging.error(f"An error occurred in BAAC function: {str(e)}")
        sys.exit(1)  # Exit the program with an error code
    finally:
        driver.quit()

if __name__ == "__main__":
    main()