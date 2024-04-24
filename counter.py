import time
import logging
import shutil
import os

from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

#สร้าง Web Driver
options = webdriver.ChromeOptions()
options.add_experimental_option("detach",True)
driver = webdriver.Chrome(options=options)

#Login
driver.get("https://counterservice.co.th/ticketnet/clients/login_ftp.asp")
input_username = driver.find_element(By.NAME,"username")
input_password = driver.find_element(By.NAME,"password")
login_button = driver.find_element(By.NAME,"B1")

time.sleep(3)
input_username.send_keys("ghb")
time.sleep(3)
input_password.send_keys("ghbwyq444444")
time.sleep(3)
login_button.click()

time.sleep(3)
#Download
current_time = time.time()  # Get current time in seconds since epoch
formatted_date = time.strftime("%m%d", time.localtime(current_time))

# Get today's date
today = datetime.now()

# Calculate yesterday's date
yesterday = today - timedelta(days=1)

# Format yesterday's date as "dd-MM-YYYY"
gco_formatted_yesterday = yesterday.strftime("%Y%m%d")

rp_formatted_yesterday = yesterday.strftime("%d%m%y")

ahref = driver.find_element(By.XPATH, "//a[@href='downloadclientfile.asp?file=GHB\\261"+formatted_date+"%2Ezip']")
ahref.click()
time.sleep(3)

gco_link = driver.find_element(By.XPATH, "//a[@href='downloadclientfile.asp?file=GHB\\INDCR0000000003300000264"+gco_formatted_yesterday+"001%2Etxt']")
gco_link.click()
time.sleep(3)

report_link = driver.find_element(By.XPATH, "//a[@href='downloadclientfile.asp?file=GHB\\Report%5FGHB%5F"+rp_formatted_yesterday+"%2Ezip']")
report_link.click()
time.sleep(3)

logout_link = driver.find_element(By.XPATH, "//a[@href='/ticketnet/clients/logout.asp']")
logout_link.click()
time.sleep(3)

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

source_dir = "C:/Users/GHBservice/Downloads"
destination_dir = "E:/my_work_OLD/_Git/Python/DI2/download"

# Move files
move_files(source_dir, destination_dir)