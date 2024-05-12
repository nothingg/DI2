import time
import os
import shutil
import logging
import paramiko

from selenium import webdriver


# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

def create_web_driver():
    # Create and return a configured WebDriver instance
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    return webdriver.Chrome(options=options)

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
        print('error : ' + str(e))
        logging.error(f"An error occurred in function: move_files: {str(e)}")


def servu_download(input_date, server_path, local_path,biller):
    # Server details
    ip_server = "test.rebex.net"
    username = "demo"
    password = "password"
    port = 22
    filename_IN = "mail"
    # server_path = "DCR/Counter/IN/"
    # filename = "20240509_counter.txt"
    #
    # # Local path (ensure it exists)
    # local_path = "D:/Counter/20240509/"
    try:
        # Create SSH transport
        transport = paramiko.Transport((ip_server, port))
        transport.connect(username=username, password=password)

        # Create SFTP client
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Change directory to the server path
        sftp.chdir(server_path)

        # List files in the directory
        files = sftp.listdir()

        # Filter files based on the pattern
        files_to_download = [file for file in files if file.startswith("INDCRxxxxxx" + input_date ) and file.endswith(".txt")]

        # Download each file
        for filename in files_to_download:
            # Remote file path
            remote_file = server_path + filename

            # Local file path (including filename)
            local_file = local_path + filename

            # Download the file
            sftp.get(remote_file, local_file)

            print(f"File downloaded successfully: {local_file}")

        if(biller == "lotus"):
            true_files_to_download = [file for file in files if file.startswith("REDCRxxxxxx" + input_date) and file.endswith(".zip")]
            for filename_zip in true_files_to_download:
                remote_file_zip = server_path + filename_zip
                local_file_zip = local_path + filename_zip
                sftp.get(remote_file_zip, local_file_zip)

                print(f"File Zip downloaded successfully: {local_file_zip}")

        # Close connections
        sftp.close()
        transport.close()

    except Exception as e:
        print('error : ' + str(e))
        logging.error(f"An error occurred in function: servu_download: {str(e)}")