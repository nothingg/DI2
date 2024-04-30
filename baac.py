from selenium.webdriver.common.by import By
from utils import create_web_driver , move_files
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, timedelta

import time
import logging

# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

def login(driver, username, password):
    # Perform login with provided credentials
    driver.get("https://unicorn.baac.or.th/")

    time.sleep(5)

    input_username = driver.find_element(By.NAME, "userid")
    input_password = driver.find_element(By.NAME, "password")

    input_username.send_keys(username)
    input_password.send_keys(password)
    time.sleep(3)

    input_password.send_keys(Keys.ENTER)

def logout(driver):
    # Logout from the system
    main_menu = driver.find_element(By.ID,"logging_string") #driver.find_element(By.XPATH, "//a[@href='#']")

    # Create an ActionChains object
    actions = ActionChains(driver)

    # Perform mouse hover action on the main UL element
    actions.move_to_element(main_menu).perform()
    time.sleep(3)

    logout_link = driver.find_element(By.ID, "action_instance_logout")
    logout_link.click()
    time.sleep(3)

def payment_l001_new(driver):
    # https://unicorn.baac.or.th/ws-payment-l001/2024/04/29
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    today_ymd = today.strftime("%Y/%m/%d")

# Page Zip
    url_date_ym = "https://unicorn.baac.or.th/ws-payment-l001/" + yesterday.strftime("%Y/%m")
    driver.get(url_date_ym)
    time.sleep(30)

    # Find the element you want to click
    span_payment = driver.find_element(By.XPATH, f"//span[@class='text_label' and contains(text(), '{today_ymd}')]")

    # Scroll the webpage to bring the element into view
    driver.execute_script("arguments[0].scrollIntoView();", span_payment)

    # Click on the element using JavaScript
    driver.execute_script("arguments[0].click();", span_payment)

    css_download_zip = driver.find_element(By.ID, "download_button")
    css_download_zip.click()

# Page Detail

    url_date_ymd = "https://unicorn.baac.or.th/ws-payment-l001/" + yesterday.strftime("%Y/%m/%d")
    driver.get(url_date_ymd)
    time.sleep(30)

    file_ymd = yesterday.strftime("%Y%m%d")
    css_download = driver.find_element(By.ID, "download_button_label")
    css_id_row_dc106 = "item-" + file_ymd + "dc106l001" + file_ymd + "pdf"
    css_row_dc106 = driver.find_element(By.ID, css_id_row_dc106)
    css_row_dc106.click()
    css_download.click()

    time.sleep(5)

    css_id_row_dc105 = "item-" + file_ymd + "dc105l001" + file_ymd + "pdf"
    css_row_dc105 = driver.find_element(By.ID, css_id_row_dc105)
    css_row_dc105.click()
    css_download.click()

    time.sleep(5)

def statement_ghb(driver):
    # https://unicorn.baac.or.th/ws-statement-GHB1/2024/04/29
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    today_ymd = today.strftime("%Y/%m/%d")

    url_date_ym = "https://unicorn.baac.or.th/ws-statement-GHB1/" + yesterday.strftime("%Y/%m/%d")
    driver.get(url_date_ym)
    time.sleep(30)

    css_content = driver.find_element(By.ID, "content_pane")
    css_content.click()
    time.sleep(3)


    # Find the element you want to click
    span_payment = driver.find_element(By.XPATH, f"//span[@class='text_label' and contains(text(), '{today_ymd}')]")
    span_payment.click()

    css_download = driver.find_element(By.ID, "download_button_label")
    css_download.click()



def payment_l001(driver):

    current_time = time.time()
    this_year = formatted_date = time.strftime("%Y", time.localtime(current_time))
    this_ym = formatted_date = time.strftime("%Y%m", time.localtime(current_time))

    today = datetime.now()
    yesterday = today - timedelta(days=1)
    this_ymd = yesterday.strftime("%Y%m%d")

    time.sleep(5)
    menu = driver.find_element(By.ID, "repo_chooser")  # driver.find_element(By.XPATH, "//a[@href='#']")

    # Create an ActionChains object
    actions = ActionChains(driver)

    # Perform mouse hover action on the main UL element
    actions.move_to_element(menu).perform()
    time.sleep(5)

    # Find the span element containing the text "payment[L001]"
    span_payment = driver.find_element(By.XPATH, "//span[text()='payment[L001]']")
    span_payment.click()

    time.sleep(15)

    # TODO : Click year month day , and download file
    css_id_row_year = "item-" + this_year
    css_row_year = driver.find_element(By.ID, css_id_row_year)
    actions.double_click(css_row_year).perform()

    time.sleep(10)

    css_id_row_ym = "item-" + this_ym
    css_row_ym = driver.find_element(By.ID, css_id_row_ym)
    actions.double_click(css_row_ym).perform()

    time.sleep(10)

    # vertical_splitter
    # content_pane
    # Option 2: Scroll to the element before clicking

#TODO : connot find id css
    # Find the span element with class "text_label" containing the text "2024/04/02"
    span_payment = driver.find_element(By.XPATH, "//span[@class='text_label' and contains(text(), '2024/04/02')]")
    span_payment.click()
    time.sleep(3)
    actions.double_click(span_payment).perform()

    css_id_row_ymd = "item-"+this_ymd
    css_row_ymd = driver.find_element(By.ID, css_id_row_ymd)
    # driver.execute_script("arguments[0].scrollIntoView();", css_row_ymd)
    # time.sleep(3)
    # css_row_ymd.click()
    time.sleep(3)
    actions.double_click(css_row_ymd).perform()

    time.sleep(10)
    css_download = driver.find_element(By.ID, "download_button_label")

    css_id_row_dc106 = "item-" + this_ymd + "dc106l001" + this_ymd +"pdf"
    css_row_dc106 = driver.find_element(By.ID, css_id_row_dc106)
    css_row_dc106.click()
    css_download.click()

    time.sleep(5)

    css_id_row_dc105 = "item-" + this_ymd + "dc105l001" + this_ymd + "pdf"
    css_row_dc105 = driver.find_element(By.ID, css_id_row_dc105)
    css_row_dc105.click()
    css_download.click()


def main():
    username = "ghb"
    password = "Ghb@12345"

    try:
        driver = create_web_driver()
        login(driver, username, password)
        time.sleep(5)

        payment_l001_new(driver)
        statement_ghb(driver)
        # time.sleep(3)

        #logout(driver)

    except Exception as e:
        print('error : ' + str(e))
        logging.error(f"An error occurred in BAAC function: {str(e)}")
    # finally:
    #     driver.quit()

if __name__ == "__main__":
    main()