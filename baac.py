from selenium.webdriver.common.by import By
from utils import create_web_driver , move_files
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

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

def payment_l001(driver):
    menu = driver.find_element(By.ID, "repo_chooser")  # driver.find_element(By.XPATH, "//a[@href='#']")

    # Create an ActionChains object
    actions = ActionChains(driver)

    # Perform mouse hover action on the main UL element
    actions.move_to_element(menu).perform()
    time.sleep(5)

    # Find the span element containing the text "payment[GHB1]"
    span_payment = driver.find_element(By.XPATH, "//span[text()='payment[L001]']")
    span_payment.click()

#TODO : Click year month day , and download file

def main():
    username = "ghb"
    password = "Ghb@12345"

    try:
        driver = create_web_driver()
        login(driver, username, password)
        time.sleep(5)

        payment_l001(driver)
        # download_txtfile(driver)
        # time.sleep(3)

        #logout(driver)

    except Exception as e:
        print('error : ' + str(e))
        logging.error(f"An error occurred in BAAC function: {str(e)}")
    # finally:
    #     driver.quit()

if __name__ == "__main__":
    main()