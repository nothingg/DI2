import time
import os
import shutil
import logging
import paramiko
from ftplib import FTP
from library.config import source_dir,destination_dir,username,password,secret_code,WAIT_TIMES,SERV_U_PATH,FTP_THAIPOST_CONFIG

from selenium import webdriver
from library.config import SERV_U_CONFIG , source_dir

from selenium.webdriver.chrome.service import Service

# Configure logging
logging.basicConfig(filename='../error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')


def create_web_driver():
    # Get the directory of the current script
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Construct the full path to the chromedriver
    driver_path = os.path.join(base_path, "driver", "chromedriver-win64", "chromedriver.exe")

    if not os.path.exists(driver_path):
        raise FileNotFoundError(f"ChromeDriver not found at path: {driver_path}")

    service = Service(driver_path)
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    return webdriver.Chrome(service=service, options=options)

def move_files(source_dir, destination_dir):
    # Move files from source directory to destination directory
    try:
        os.makedirs(destination_dir, exist_ok=True)
        files = os.listdir(source_dir)
        for file in files:
            source_path = os.path.join(source_dir, file)
            destination_path = os.path.join(destination_dir, file)
            shutil.move(source_path, destination_path)
            print(f"Moved '{file}' to '{destination_dir}'")
    except Exception as e:
        # print('error : ' + str(e))
        logging.error(f"An error occurred in function: move_files: {str(e)}")

def delete_all_files(source_dir):
    for filename in os.listdir(source_dir):
        filepath = os.path.join(source_dir, filename)
        try:
            if os.path.isfile(filepath):
                os.remove(filepath)  # Delete the file
        except Exception as e:
            logging.error(f"An error occurred in function: delete_all_files: {str(e)}", exc_info=True)
            raise  # Raise the exception to be caught by the calling function

def sftp_servu(server_path,filename,biller = None):

    try:
        ip = SERV_U_CONFIG["ip"]
        port = int(SERV_U_CONFIG["port"])

        # Establish a transport connection
        transport = paramiko.Transport(ip, port)
        transport.connect(username=SERV_U_CONFIG["username"], password=SERV_U_CONFIG["password"])

        # Create SFTP client
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Change directory to the server path
        sftp.chdir(server_path)

        # Remote file path
        remote_file = server_path + filename

        # Local file path (including filename)
        local_file = source_dir["default"] + "/" + filename

        if biller == "counter_service" or biller == "thaipost" :
            # Check if the file already exists and rename it with a sequence number if it does
            if os.path.exists(local_file):
                base, ext = os.path.splitext(local_file)
                seq = 1
                while os.path.exists(f"{base}_{seq}{ext}"):
                    seq += 1
                local_file = f"{base}_{seq}{ext}"

        # Download the file
        sftp.get(remote_file, local_file)

        # Close connections
        sftp.close()
        transport.close()

    except Exception as e:
        # print('error : ' + str(e))
        logging.error(f"An error occurred in function: servu_download: {str(e)}", exc_info=True)
        raise  # Raise the exception to be caught by the calling function


def ftp_download(server_path, filename):
    ftp = FTP()
    ftp.connect(FTP_THAIPOST_CONFIG["ip"], int(FTP_THAIPOST_CONFIG["port"]))
    ftp.login(user=FTP_THAIPOST_CONFIG["username"], passwd=FTP_THAIPOST_CONFIG["password"])

    # Change directory to the server path
    ftp.cwd(server_path)

    # Remote file path
    remote_file = server_path + filename

    # Local file path (including filename)
    local_file = os.path.join(source_dir["default"], filename)

    # Download the file
    with open(local_file, 'wb') as f:
        ftp.retrbinary(f'RETR {filename}', f.write)

    # Close connections
    ftp.quit()
