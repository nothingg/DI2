import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import paramiko
from utils import create_web_driver,move_files, servu_download


# Server details
ip_server = "test.rebex.net"
username = "demo"
password = "password"
port = 22
server_path = "/pub/example/"
filename = "imap-console-client.png"

# Local path (ensure it exists)
local_path = "C:/Downloads/"


servu_download("20250501",server_path,local_path,"MEA")
#
# try:
#     # Create SSH transport
#     transport = paramiko.Transport((ip_server, port))
#     transport.connect(username=username, password=password)
#
#     # Create SFTP client
#     sftp = paramiko.SFTPClient.from_transport(transport)
#
#     # Remote file path
#     remote_file = server_path + filename
#
#     # Local file path (including filename)
#     local_file = local_path + filename
#
#     # Download the file
#     sftp.get(remote_file, local_file)
#
#     # Close connections
#     sftp.close()
#     transport.close()
#
#     print(f"File downloaded successfully: {local_file}")
# except Exception as e:
#     print(f"An error occurred: {e}")

#
# #สร้าง Web Driver
# options = webdriver.ChromeOptions()
# options.add_experimental_option("detach",True)
# driver = webdriver.Chrome(options=options)
#
# #Download
# driver.get("file:///E:/my_work_OLD/_Git/Python/DI2/html/Counter%20Service%20Co.,Ltd.html")
# current_time = time.time()  # Get current time in seconds since epoch
# # formatted_date = '261' + time.strftime("%m%d", time.localtime(current_time))
# formatted_date = time.strftime("%m%d", time.localtime(current_time))
#
# filezip = "downloadclientfile.asp?file=GHB\\"+formatted_date + '%2Ezip'
# a_txt = "a[href='"+filezip+"']"
#

# Find the anchor tag using CSS selector (recommended)
# link_to_click = driver.find_element(By.CSS_SELECTOR, "a[href='https://counterservice.co.th/ticketnet/clients/downloadclientfile.asp?file=GHB\\2610405%2Ezip']")

# link_to_click = driver.find_element(By.XPATH, "//a[@href='https://counterservice.co.th/ticketnet/clients/downloadclientfile.asp?file=GHB\\2610405%2Ezip']")
# link_to_click = driver.find_element(By.XPATH, "//a[@href='https://counterservice.co.th/ticketnet/clients/downloadclientfile.asp?file=GHB\\261"+formatted_date+"%2Ezip']")

# Click the link
#link_to_click.click()

# current_time = time.time()  # Get current time in seconds since epoch
# formatted_date = '261' + time.strftime("%m%d", time.localtime(current_time))
#
# filezip = "downloadclientfile.asp?file=GHB\\"+formatted_date + '%2Ezip'
# a_txt = "a[href='"+filezip+"']"
#
# print( a_txt )

# https://counterservice.co.th/ticketnet/clients/downloadclientfile.asp?file=GHB\2610406%2Ezip
# from urllib.parse import quote
#
# encoded_text = quote('end to&end')
#
# print(encoded_text)