from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait , Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

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
    input_password.send_keys(Keys.ENTER)
    # btn_login.click()

#TODO : Logout
def logout(driver) :
    try :
        driver.switch_to.default_content()
        WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.frame_to_be_available_and_switch_to_it("MENU"))

        # label_logout = driver.find_element(By.ID, "_MCELL0")
        label_logout = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.presence_of_element_located((By.ID, "_MCELL0")))
        label_logout.click()

        driver.switch_to.default_content()
        WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.frame_to_be_available_and_switch_to_it("APPL"))

        # btn_logout = driver.find_element(By.NAME, "A_L")
        btn_logout = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.presence_of_element_located((By.NAME, "A_L")))
        btn_logout.click()
    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("Lotus-tims : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    except Exception as e:
        error_message = str(e)
        logging.error(f"Lotus-time : An error occurred: {error_message}" , exc_info=True)
        sys.exit(1)  # Exit the program with an error code

def btn_press(driver):
    try :
        form_id = driver.find_element(By.ID,"Form")
        # href_lotus = driver.find_element(By.XPATH,"//a[@href='/TIMS/xihome']")
        href_lotus = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.presence_of_element_located((By.XPATH, "//a[@href='/TIMS/xihome']")))

        # Create an ActionChains object
        actions = ActionChains(driver)

        # Perform mouse hover action on the main UL element
        actions.move_to_element(form_id).perform()
        time.sleep(3)
        actions.move_to_element(href_lotus).perform()

        # btn_login = driver.find_element(By.CLASS_NAME, "MSGOK")
        btn_login = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.presence_of_element_located((By.CLASS_NAME, "MSGOK")))
        btn_login.click()

    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("Lotus-tims : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    except Exception as e:
        error_message = str(e)
        logging.error(f"Lotus-time : An error occurred: {error_message}" , exc_info=True)
        sys.exit(1)  # Exit the program with an error code

def menu_document(driver):
    try:
        driver.switch_to.default_content()
        WebDriverWait(driver, WAIT_TIMES["10"]).until(EC.frame_to_be_available_and_switch_to_it("MENU"))

        time.sleep(3)
        # label_doc = driver.find_element(By.ID, "_MCELL4")
        label_doc = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.presence_of_element_located((By.ID, "_MCELL4")))
        label_doc.click()

        # sub_label_doc = driver.find_element(By.XPATH,"//td[contains(text(), 'ใบแจ้งรายละเอียดการชำระเงิน')]")
        sub_label_doc = WebDriverWait(driver, WAIT_TIMES["10"]).until(
            EC.presence_of_element_located((By.XPATH,"//td[contains(text(), 'ใบแจ้งรายละเอียดการชำระเงิน')]")))
        sub_label_doc.click()
    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("Lotus-tims : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    except Exception as e:
        error_message = str(e)
        logging.error(f"Lotus-time : An error occurred: {error_message}" , exc_info=True)
        sys.exit(1)  # Exit the program with an error code

def search_data(driver) :
    try :
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

    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("Lotus-tims : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    except Exception as e:
        error_message = str(e)
        logging.error(f"Lotus-time : An error occurred: {error_message}" , exc_info=True)
        sys.exit(1)  # Exit the program with an error code

def download_file(driver , input_date):
    try :
        # Parse input date string into a datetime object
        input_date_obj = datetime.strptime(input_date, '%Y-%m-%d')

        # Get the month abbreviation in lowercase
        month_abbr_lower = input_date_obj.strftime('%b')

        # Convert the first character to uppercase and concatenate with the rest of the string
        month_abbr_upper = month_abbr_lower[0].upper() + month_abbr_lower[1:]

        # Format the datetime object into the desired output format with uppercase first character of month abbreviation
        input_date_dMMMy = input_date_obj.strftime('%d-' + month_abbr_upper + '-%Y')

        # Find all rows in the table
        rows = driver.find_elements(By.XPATH, "//table[@class='DATA']/tbody/tr")
        # Iterate over each row
        for row in rows:
            try :
                # Find the date cell in the row
                date_cell = row.find_element(By.XPATH, f"./td[contains(text(), '{input_date_dMMMy}')]")
                # date_cell = WebDriverWait(row, WAIT_TIMES["10"]).until(
                #     EC.presence_of_element_located((By.XPATH, f"./td[contains(text(), '{input_date_dMMMy}')]"))
                # )
                if date_cell:
                    # Find the image with the title 'RTF' in the same row
                    rtf_image = row.find_element(By.XPATH, "./td/img[@title='RTF']")
                    rtf_image = WebDriverWait(row, WAIT_TIMES["10"]).until(
                        EC.presence_of_element_located((By.XPATH, "./td/img[@title='RTF']"))
                    )
                    if rtf_image:
                        # Click the image
                        rtf_image.click()
                        # save_file = driver.find_element(By.XPATH, "/html/body/table/tbody/tr[2]/td[1]/form/table/tbody/tr/td/table/tbody/tr/td/div/table/tbody/tr[2]/td")
                        save_file = WebDriverWait(driver, WAIT_TIMES["10"]).until(
                            EC.presence_of_element_located((By.XPATH,
                                                            "/html/body/table/tbody/tr[2]/td[1]/form/table/tbody/tr/td/table/tbody/tr/td/div/table/tbody/tr[2]/td"))
                        )
                        save_file.click()

                        break  # Stop iterating if found
            except NoSuchElementException:
                # If the date cell is not found in the current row, continue to the next row
                continue
    except TimeoutException as t:
        # Handle TimeoutException
        logging.error("Lotus-tims : Timeout occurred while waiting for element to be clickable." , exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    except Exception as e:
        error_message = str(e)
        logging.error(f"Lotus-time : An error occurred: {error_message}" , exc_info=True)
        sys.exit(1)  # Exit the program with an error code

def main():
    input_date = "2024-05-07"
    try:
        driver = create_web_driver()
        login(driver)
        time.sleep(WAIT_TIMES["5"])

        btn_press(driver)
        menu_document(driver)
        search_data(driver)
        download_file(driver,input_date)
        time.sleep(WAIT_TIMES["5"])

        logout(driver)
        move_files(source_dir["default"], destination_dir["lotus-tims"])

    except Exception as e:
        print('error : ' + str(e))
        logging.error(f"An error occurred in Lotus function: {str(e)}" , exc_info=True)
        sys.exit(1)  # Exit the program with an error code
    # finally:
    #     driver.quit()

if __name__ == "__main__":
    main()