import time
import os
import shutil
import logging
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
