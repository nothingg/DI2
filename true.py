from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from utils import create_web_driver,move_files
from library.config import source_dir,destination_dir,username,password,secret_code,WAIT_TIME,WAIT_INTERVAL

import time
import logging
import sys


# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(filename)s - %(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

# TODO : Test Exception & logging , timeout and other
def login(driver):
    try:
        # Perform login with provided credentials
        driver.get("https://pago.truecorp.co.th/tmnos-wdl/ghb")

        # Wait for the input fields to be clickable
        input_username = WebDriverWait(driver, WAIT_TIME).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='text' and @placeholder='Username' and @autocomplete='off']")))
        input_password = WebDriverWait(driver, WAIT_TIME).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='password' and @placeholder='Password' and @autocomplete='off']")))

        # Enter the username and password
        input_username.send_keys(username["true"])
        input_password.send_keys(password["true"])
        input_password.send_keys(Keys.ENTER)

        # Wait for 3 seconds (if needed, you can replace this with WebDriverWait as well)
        # WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password' and @placeholder='Password' and @autocomplete='off']")))
    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("True : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    except Exception as e:
        error_message = str(e)
        logging.error(f"True : An error occurred: {error_message}")
        sys.exit(1)  # Exit the program with an error code

def logout(driver):
    try :
        btn_logout = WebDriverWait(driver, WAIT_TIME).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "button-logout")))
        btn_logout.click()
    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("True : Timeout occurred while waiting for element to be clickable.", exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    except Exception as e:
        error_message = str(e)
        logging.error(f"True : An error occurred: {error_message}")
        sys.exit(1)  # Exit the program with an error code



def select_date(driver, input_date):
    try :
        input_date_obj = datetime.strptime(input_date, '%Y-%m-%d')
        input_date_Mdy = input_date_obj.strftime('%B %d, %Y')

        # input_calendar = WebDriverWait(driver, WAIT_TIME).until(
        #     EC.presence_of_element_located((By.XPATH, "//*[@id='root-route']/div/div/div[3]/div/section[1]/div/span/div/input")))
        input_calendar = WebDriverWait(driver, WAIT_TIME).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Select date']")))
        time.sleep(WAIT_TIME)
        input_calendar.click()

        # Check if input date is in the present month
        if input_date_obj.month != datetime.now().month:
            # Calculate the number of clicks needed to navigate to the previous month
            num_clicks = abs(input_date_obj.month - datetime.now().month)

            # Click on the 'Previous month' button 'num_clicks' times
            for _ in range(num_clicks):
                prev_month_button = WebDriverWait(driver, WAIT_TIME).until(EC.element_to_be_clickable((By.CLASS_NAME, "ant-calendar-prev-month-btn")))
                prev_month_button.click()

        # Locate and click on the calendar date element
        calendar_date = WebDriverWait(driver, WAIT_TIME).until(EC.element_to_be_clickable((By.XPATH, f"//td[@title='{input_date_Mdy}']")))
        calendar_date.click()

        # Click the search button
        btn_search = WebDriverWait(driver, WAIT_TIME).until(EC.element_to_be_clickable((By.CLASS_NAME, "primary")))
        btn_search.click()
    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("True : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    except Exception as e:
        error_message = str(e)
        logging.error(f"True : An error occurred: {error_message}")
        sys.exit(1)  # Exit the program with an error code

def download_file(driver, input_date):
    try :
        input_date_obj = datetime.strptime(input_date, '%Y-%m-%d')
        input_date_ymd = input_date_obj.strftime('%Y%m%d')
        file_names = [
            f"TRUE{input_date_ymd}01.txt",
            f"TMNGHBRPTEW_C101{input_date_ymd}.pdf",
            f"TMNGHBRPTEW_C102{input_date_ymd}.pdf",
            f"TMNGHBRPTTRM_C101{input_date_ymd}.pdf",
            f"TMNGHBRPTTRM_C102{input_date_ymd}.pdf"
        ]

        for file_name in file_names:
            file_xpath = f"//div[@class='name']/span[text()='{file_name}']"
            file_element = WebDriverWait(driver, WAIT_TIME).until(EC.element_to_be_clickable((By.XPATH, file_xpath)))
            file_element.click()

            time.sleep(WAIT_INTERVAL)
    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("True : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    except Exception as e:
        error_message = str(e)
        logging.error(f"True : An error occurred: {error_message}")
        sys.exit(1)  # Exit the program with an error code

def main():
    input_date = "2024-04-30"

    try:
        driver = create_web_driver()
        login(driver)
        select_date(driver, input_date)
        download_file(driver,input_date)
        logout(driver)
        move_files(source_dir["default"], destination_dir["true"])
    except Exception as e:
        print('error : ' + str(e))
        logging.error(f"An error occurred in TRUE function: {str(e)}")
        sys.exit(1)  # Exit the program with an error code
    # finally:
    #     driver.quit()

if __name__ == "__main__":
    main()
