from datetime import datetime, timedelta

from library.utils import move_files, sftp_servu, ftp_download, delete_all_files
from library.config import source_dir,destination_dir, SERV_U_PATH,FTP_THAIPOST_PATH

import logging


def download_ftp(input_date):
    try:
        input_date_obj = datetime.strptime(input_date, '%Y-%m-%d')
        input_date_ymd = input_date_obj.strftime("%Y%m%d")
        filename_txt = f"INDCR0000000003300000256{input_date_ymd}001.TXT"
        filename_zip = f"REDCR0000000003300000256{input_date_ymd}001.zip"
        filename_zip2 = f"REDCR0000000003300000256{input_date_ymd}002.zip"

        ftp_download(FTP_THAIPOST_PATH,filename_txt)
        ftp_download(FTP_THAIPOST_PATH, filename_zip)
        ftp_download(FTP_THAIPOST_PATH, filename_zip2)
    except Exception as e:
        logging.error(f"ThaiPost Service: An error occurred: {str(e)}", exc_info=True)
        raise  # Raise the exception to be caught by the main function

def download_servu(input_date):
    try :
        input_date_obj = datetime.strptime(input_date, '%Y-%m-%d')
        input_date_ymd = input_date_obj.strftime("%Y%m%d")
        filename_txt = f"INDCR0000000003300000256{input_date_ymd}001.TXT"
        filename_zip = f"REDCR0000000003300000256{input_date_ymd}001.zip"
        filename_zip2 = f"REDCR0000000003300000256{input_date_ymd}002.zip"

        sftp_servu(SERV_U_PATH["thaipost"], filename_txt ,"thaipost")
        sftp_servu(SERV_U_PATH["thaipost"], filename_zip, "thaipost")
        sftp_servu(SERV_U_PATH["thaipost"], filename_zip2, "thaipost")

    except Exception as e:
        logging.error(f"ThaiPost Service: An error occurred: {str(e)}", exc_info=True)
        raise  # Raise the exception to be caught by the main function

def main(input_date = None):
    # input_date = "2024-05-14"
    if input_date is None:
        input_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        download_ftp(input_date)
        download_servu(input_date)
        move_files(source_dir["default"], destination_dir(input_date, "thaipost"))


    except Exception as e:
        delete_all_files(source_dir["default"])
        logging.error(f"An error occurred in counter_service function: {str(e)}", exc_info=True)
        raise  # Raise the exception to be caught by the main function
    # finally:
    #     driver.quit()

if __name__ == "__main__":
    main()