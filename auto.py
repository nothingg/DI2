import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

#Download
import shutil
import os
import logging

#สร้าง Web Driver
options = webdriver.ChromeOptions()
options.add_experimental_option("detach",True)
driver = webdriver.Chrome(options=options)

#Download
driver.get("https://www.selenium.dev/selenium/web/downloads/download.html")
ahref = driver.find_element(By.CSS_SELECTOR,"a[href='file_1.txt']")

# Click the link (optional)
ahref.click()

# Configure logging
# logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

def move_files(source_dir, destination_dir):
    try:
        # Ensure the destination directory exists
        os.makedirs(destination_dir, exist_ok=True)

        # Get a list of all files in the source directory
        files = os.listdir(source_dir)

        # Move each file to the destination directory
        for file in files:
            source_path = os.path.join(source_dir, file)
            destination_path = os.path.join(destination_dir, file)
            shutil.move(source_path, destination_path)
            print(f"Moved '{file}' to '{destination_dir}'")

        # Delete all files in the source directory
        # for file in files:
        #     file_path = os.path.join(source_dir, file)
        #     os.remove(file_path)
        #     print(f"Deleted '{file}' from '{source_dir}'")

    except Exception as e:
        # Log the error
        print('error : ' + e)
        logging.error(f"An error occurred in function: {move_files.__name__}: {str(e)}")

# Set the source and destination directories
# source_dir = "C:/Downloads"
# destination_dir = "D:/_GHB/Python/DI2/download"

source_dir = "C:/Users/GHBservice/Downloads"
destination_dir = "E:/my_work_OLD/_Git/Python/DI2/download"

# Move files
move_files(source_dir, destination_dir)

#Login
#Open Website
# driver.get("https://www.selenium.dev/selenium/web/login.html")
# input_username = driver.find_element(By.ID,"username-field")
# input_password = driver.find_element(By.ID,"password-field")
# login_button = driver.find_element(By.ID,"login-form-submit")  # เปลี่ยนเป็น id ของปุ่ม login จริง
#
# time.sleep(3)
# input_username.send_keys("username")
# time.sleep(3)
# input_password.send_keys("password")
# time.sleep(3)
# login_button.click()


# driver.get("https://www.selenium.dev/selenium/web/web-form.html")
# element =  driver.find_element(By.ID,"my-text-id")
# element.send_keys("Username")
#
# elements = driver.find_elements(By.TAG_NAME,"label")
#
# for i in elements:
#     txt = i.text
#     print(txt)
#
# #Select
# dropdown = Select(driver.find_element(By.NAME, 'my-select'))
# dropdown.select_by_visible_text("One")
