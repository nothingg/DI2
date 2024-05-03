from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils import create_web_driver
from datetime import datetime, timedelta

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

    time.sleep(2)
    btn_search = driver.find_element(By.CLASS_NAME, "primary")
    btn_search.click()

    # input_date_dmy = input_date_obj.strftime("%d/%m/%Y")
    #
    # input_calendar = driver.find_element(By.XPATH,"//input[@placeholder='Select date']")
    # btn_search = driver.find_element(By.CLASS_NAME,"primary")
    # # btn_search = driver.find_element(By.XPATH, "//button[@class='button primary')]")
    #
    # input_calendar.click()
    # # driver.execute_script("arguments[0].value = '30/04/2024';", input_calendar)
    # # input_calendar.send_keys(input_date_dmy)
    #
    # new_date = "30/04/2024"
    # driver.execute_script("arguments[0].value = arguments[1];", input_calendar, input_date_dmy)
    #
    # # Press the Enter key to trigger the change
    # input_calendar.send_keys(Keys.RETURN)
    #
    # # Wait for the page to update (if necessary)
    # time.sleep(2)
    #
    # btn_search.click()

def main():
    username = "ghbadmin"
    password = "ghbpassword"
    input_date = "2024-04-30"

    try:
        driver = create_web_driver()
        login(driver, username, password)
        time.sleep(10)

        select_date(driver, input_date)

        # time.sleep(3)

        # logout(driver)

    except Exception as e:
        print('error : ' + str(e))
        logging.error(f"An error occurred in BAAC function: {str(e)}")
    # finally:
    #     driver.quit()

if __name__ == "__main__":
    main()
