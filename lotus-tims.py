from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
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

    driver.get("https://tims.lotuss.com/TIMS/")

    # all_frames = driver.find_elements(By.TAG_NAME, "frame")
    # for frame in all_frames:
    #     print(frame.get_attribute("name"))
    # Switch to the frame
    # WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.frame_to_be_available_and_switch_to_it("HEAD"))
    # WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.frame_to_be_available_and_switch_to_it((By.NAME ,"APPL")))
    WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.frame_to_be_available_and_switch_to_it("APPL"))

    # Find the username, password, and secret code input fields
    input_username = WebDriverWait(driver, WAIT_TIMES["10"]).until(
        EC.presence_of_element_located((By.XPATH, "//input[@name='LOGUSER']")))
    input_password = WebDriverWait(driver, WAIT_TIMES["10"]).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@name='LOGPASS']")))
    btn_login = WebDriverWait(driver, WAIT_TIMES["10"]).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@name='A_L']")))

    # Send keys to all input fields
    input_username.send_keys(username["lotus-tims"])
    input_password.send_keys(password["lotus-tims"])
    btn_login.click()

#TODO : ต้อง hover area สักที่ก่อน ปุ่มถึงจะขึ้น
def btn_press(driver):

    form_id = driver.find_element(By.ID,"Form")
    href_lotus = driver.find_element(By.XPATH,"//a[@href='/TIMS/xihome']")


    # Create an ActionChains object
    actions = ActionChains(driver)

    # Perform mouse hover action on the main UL element
    actions.move_to_element(form_id).perform()
    time.sleep(3)
    actions.move_to_element(href_lotus).perform()

    btn_login = driver.find_element(By.CLASS_NAME, "MSGOK")
    btn_login.click()

def menu_document(driver):

    driver.switch_to.default_content()
    WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.frame_to_be_available_and_switch_to_it("MENU"))

    time.sleep(3)
    label_doc = driver.find_element(By.ID, "_MCELL4")
    label_doc.click()

    sub_label_doc = driver.find_element(By.XPATH,"//td[contains(text(), 'ใบแจ้งรายละเอียดการชำระเงิน')]")
    sub_label_doc.click()

    # Create an ActionChains object
    #actions = ActionChains(driver)

    # Perform mouse hover action on the main UL element
    #actions.move_to_element(label_doc).perform()

def search_data(driver) :

    driver.switch_to.default_content()
    WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.frame_to_be_available_and_switch_to_it("APPL"))

    # Select Report in dropdownlist
    dropdown = WebDriverWait(driver, WAIT_TIMES["10"]).until(
        EC.element_to_be_clickable((By.NAME, "V_RAH_IND1")))
    # Create a Select object
    select = Select(dropdown)
    # Select the option by its value
    select.select_by_value("")

    btn_search = WebDriverWait(driver, WAIT_TIMES["10"]).until(
        EC.element_to_be_clickable((By.ID, "btnSelect")))
    btn_search.click()

#TODO : Can't click icon download
def download_file(driver):

    # Find the table
    # table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//table[@class='DATA']")))
    table = driver.find_elements(By.XPATH, "//table[@class='DATA']")

    # Find the rows
    rows = table.find_element(By.XPATH,"//tr[@class='DATAHILI']")

    # Find the row with '02-May-2024'
    for row in rows:
        if '08-May-2024' in row.text:
            row_index = rows.index(row)
            break

    # Find the image with title 'RTF'
    image = table.find_element(By.XPATH,f".//tr[{row_index}]/td[4]/img[@title='RTF']")

    # Click the image
    image.click()

    # If no matching row is found

    ####################################################

    # Find the row containing the date
    row1 = driver.find_element(By.XPATH, "//tr[contains(td, '08-May-2024')]")

    # Find the image with the title 'RTF' in the same row
    rtf_image = row1.find_element(By.XPATH, ".//img[@title='RTF']")

    # Click the image
    rtf_image.click()

    s1 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr[2]/td[1]/form/table/tbody/tr/td/table/tbody/tr/td/div/table/tbody/tr[2]/td")
    # save_file = driver.find_element(By.XPATH, "//tr[contains(td, 'บันทึก')]")

    # save_file = driver.find_elements(By.XPATH, "//td[contains(text(), 'บันทึก')]")
    s1.click()
    # save_file.click()

    # Find all rows in the table
    # rows = driver.find_elements(By.XPATH, "//table[@class='DATA']/tbody/tr")
    # # Iterate over each row
    # for row in rows:
    #     # Find the date cell in the row
    #     date_cell = row.find_element(By.XPATH, "./td[contains(text(), '09-May-2024')]")
    #     if date_cell:
    #         # Find the image with the title 'RTF' in the same row
    #         rtf_image = row.find_element(By.XPATH, "./td/img[@title='RTF']")
    #         if rtf_image:
    #             # Click the image
    #             rtf_image.click()
    #             save_file = driver.find_elements(By.XPATH, "//td[contains(text(), 'บันทึก')]")
    #             save_file.click()
    #
    #             break  # Stop iterating if found


def main():
    input_date = "2024-05-08"
    try:
        driver = create_web_driver()
        login(driver)
        time.sleep(WAIT_TIMES["5"])
        btn_press(driver)

        menu_document(driver)
        search_data(driver)

        download_file(driver)

    except Exception as e:
        print('error : ' + str(e))
        logging.error(f"An error occurred in Lotus function: {str(e)}" , exc_info=True)
        # sys.exit(1)  # Exit the program with an error code
    # finally:
    #     driver.quit()

if __name__ == "__main__":
    main()