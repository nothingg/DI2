from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils import create_web_driver
from datetime import datetime, timedelta
from library.config import source_dir,destination_dir

import time
import logging

def login(driver, username, password):
    # Perform login with provided credentials
    driver.get("https://pago.truecorp.co.th/tmnos-wdl/ghb")

    time.sleep(5)


    input_username = driver.find_element(By.XPATH,"//input[@type='text' and @placeholder='Username' and @autocomplete='off']")
    input_password = driver.find_element(By.XPATH,"//input[@type='password' and @placeholder='Password' and @autocomplete='off']")

    input_username.send_keys(username)
    input_password.send_keys(password)
    time.sleep(3)

    input_password.send_keys(Keys.ENTER)



def logout(driver):

    logout_link = driver.find_element(By.CLASS_NAME, "button-logout")
    logout_link.click()

def select_date(driver, input_date):

    input_date_obj = datetime.strptime(input_date, '%Y-%m-%d')
    input_date_Mdy = input_date_obj.strftime('%B %d, %Y')

    input_calendar = driver.find_element(By.XPATH, "//input[@placeholder='Select date']")
    input_calendar.click()

    # Check if input date is in the present month
    if input_date_obj.month == datetime.now().month:
        # Locate and click on the calendar date element
        calendar_date = driver.find_element(By.XPATH, f"//td[@title='{input_date_Mdy}']")
        calendar_date.click()
    else:
        # Calculate the number of clicks needed to navigate to the previous month
        num_clicks = abs(input_date_obj.month - datetime.now().month)

        # Click on the 'Previous month' button 'num_clicks' times
        for _ in range(num_clicks):
            prev_month_button = driver.find_element(By.CLASS_NAME, "ant-calendar-prev-month-btn")
            prev_month_button.click()

        # Locate and click on the calendar date element
        calendar_date = driver.find_element(By.XPATH, f"//td[@title='{input_date_Mdy}']")
        calendar_date.click()

    time.sleep(5)
    btn_search = driver.find_element(By.CLASS_NAME, "primary")
    btn_search.click()


def download_file(driver , input_date):
    input_date_obj = datetime.strptime(input_date, '%Y-%m-%d')
    input_date_ymd = input_date_obj.strftime('%Y%m%d')

    txt_file = driver.find_element(By.XPATH, f"//div[@class='name']/span[text()='TRUE{input_date_ymd}01.txt']")
    txt_file.click()
    time.sleep(3)

    driver.find_element(By.XPATH, f"//div[@class='name']/span[text()='TMNGHBRPTEW_C101{input_date_ymd}.pdf']").click()
    time.sleep(3)
    driver.find_element(By.XPATH, f"//div[@class='name']/span[text()='TMNGHBRPTEW_C102{input_date_ymd}.pdf']").click()
    time.sleep(3)
    driver.find_element(By.XPATH, f"//div[@class='name']/span[text()='TMNGHBRPTTRM_C101{input_date_ymd}.pdf']").click()
    time.sleep(3)
    driver.find_element(By.XPATH, f"//div[@class='name']/span[text()='TMNGHBRPTTRM_C102{input_date_ymd}.pdf']").click()

def main():
    username = "ghbadmin"
    password = "ghbpassword"
    input_date = "2024-04-30"

    try:
        driver = create_web_driver()
        login(driver, username, password)
        time.sleep(10)

        select_date(driver, input_date)
        time.sleep(10)

        download_file(driver,input_date)
        time.sleep(10)

        logout(driver)

        #TODO Move file

    except Exception as e:
        print('error : ' + str(e))
        logging.error(f"An error occurred in TRUE function: {str(e)}")
    # finally:
    #     driver.quit()

if __name__ == "__main__":
    main()
