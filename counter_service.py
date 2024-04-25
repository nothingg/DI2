from utils import create_web_driver , move_files
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import time
import logging


# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

def login(driver, username, password):
    # Perform login with provided credentials
    driver.get("https://counterservice.co.th/ticketnet/clients/login_ftp.asp")
    input_username = driver.find_element(By.NAME, "username")
    input_password = driver.find_element(By.NAME, "password")
    login_button = driver.find_element(By.NAME, "B1")

    input_username.send_keys(username)
    input_password.send_keys(password)
    time.sleep(3)

    login_button.click()

def logout(driver):
    # Logout from the system
    logout_link = driver.find_element(By.XPATH, "//a[@href='/ticketnet/clients/logout.asp']")
    logout_link.click()
    time.sleep(3)

def download_files(driver):

    current_time = time.time()
    formatted_date = time.strftime("%m%d", time.localtime(current_time))
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    gco_formatted_yesterday = yesterday.strftime("%Y%m%d")
    rp_formatted_yesterday = yesterday.strftime("%d%m%y")

    # Download files using WebDriver
    ahref = driver.find_element(By.XPATH, f"//a[@href='downloadclientfile.asp?file=GHB\\261{formatted_date}%2Ezip']")
    ahref.click()
    time.sleep(3)

    indcr_link = driver.find_element(By.XPATH, f"//a[@href='downloadclientfile.asp?file=GHB\\INDCR0000000003300000264{gco_formatted_yesterday}001%2Etxt']")
    indcr_link.click()
    time.sleep(3)

    gco_link = driver.find_element(By.XPATH,f"//a[@href='downloadclientfile.asp?file=GHB\\gco261{formatted_date}%2Ezip']")
    gco_link.click()
    time.sleep(3)

    report_link = driver.find_element(By.XPATH, f"//a[@href='downloadclientfile.asp?file=GHB\\Report%5FGHB%5F{rp_formatted_yesterday}%2Ezip']")
    report_link.click()
    time.sleep(3)

def main():
    username = "ghb"
    password = "ghbwyq444444"
    source_dir = "C:/Users/GHBservice/Downloads"
    destination_dir = "E:/my_work_OLD/_Git/Python/DI2/download"

    try:
        driver = create_web_driver()
        login(driver, username, password)
        time.sleep(3)

        download_files(driver)
        logout(driver)
        move_files(source_dir, destination_dir)

    except Exception as e:
        print('error : ' + str(e))
        logging.error(f"An error occurred in counter_service_main function: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()