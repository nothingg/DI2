import os

# Get the username of the current user
user = os.getlogin()

# Construct the default download path
source_dir = {
    "default": f"C:/Users/{user}/Downloads"
}


# Example usage in your script
print(source_dir["default"])

#
#
#
#
# import tkinter as tk
# from tkinter import ttk, messagebox
# from tkcalendar import Calendar
# import importlib
# import logging
# import threading
#
# # Your script files mapped to their respective main functions
# scripts = {
#     'baac': 'baac',
#     'counter_service': 'counter_service',
#     'lotus': 'lotus',
#     'lotus_tims': 'lotus_tims',
#     'mpay': 'mpay',
#     'thaipost': 'thaipost',
#     'true': 'true'
# }
#
# # Add "All" option to run all scripts
# scripts['All'] = 'all'
#
#
# # Main GUI application class
# class App(tk.Tk):
#     def __init__(self):
#         super().__init__()
#         self.title("Script Runner")
#
#         # Dropdown menu
#         self.label_script = tk.Label(self, text="Select Script:")
#         self.label_script.pack(pady=10)
#
#         self.script_var = tk.StringVar()
#         self.script_menu = ttk.Combobox(self, textvariable=self.script_var)
#         self.script_menu['values'] = list(scripts.keys())
#         self.script_menu.pack(pady=10)
#
#         # Calendar
#         self.label_date = tk.Label(self, text="Select Date:")
#         self.label_date.pack(pady=10)
#
#         self.calendar = Calendar(self, selectmode='day', date_pattern='yyyy-mm-dd')
#         self.calendar.pack(pady=10)
#
#         # Run button
#         self.run_button = tk.Button(self, text="Run Script", command=self.run_script)
#         self.run_button.pack(pady=10)
#
#         # Run BAAC Stmt button
#         self.run_baac_stmt_button = tk.Button(self, text="Run BAAC Stmt", command=self.run_baac_stmt)
#         self.run_baac_stmt_button.pack(pady=10)
#
#         # Reset button
#         self.reset_button = tk.Button(self, text="Reset", command=self.reset_values)
#         self.reset_button.pack(pady=10)
#
#         # Result frame
#         self.result_frame = tk.Frame(self)
#         self.result_frame.pack(pady=20)
#
#         # Status label
#         self.status_var = tk.StringVar()
#         self.status_label = tk.Label(self, textvariable=self.status_var)
#         self.status_label.pack(pady=10)
#
#     def run_script(self):
#         selected_script = self.script_var.get()
#         selected_date = self.calendar.get_date()
#
#         # Clear previous results
#         for widget in self.result_frame.winfo_children():
#             widget.destroy()
#
#         if selected_script and selected_date:
#             self.status_var.set("Running...")
#             self.run_button.config(state=tk.DISABLED)
#             self.run_baac_stmt_button.config(state=tk.DISABLED)
#             self.reset_button.config(state=tk.DISABLED)
#             self.script_menu.config(state=tk.DISABLED)
#             self.calendar.config(state=tk.DISABLED)
#             threading.Thread(target=self.execute_scripts, args=(selected_script, selected_date)).start()
#         else:
#             messagebox.showwarning("Input Error", "Please select both script and date")
#
#     def run_baac_stmt(self):
#         selected_date = self.calendar.get_date()
#
#         # Clear previous results
#         for widget in self.result_frame.winfo_children():
#             widget.destroy()
#
#         if selected_date:
#             self.status_var.set("Running...")
#             self.run_button.config(state=tk.DISABLED)
#             self.run_baac_stmt_button.config(state=tk.DISABLED)
#             self.reset_button.config(state=tk.DISABLED)
#             self.script_menu.config(state=tk.DISABLED)
#             self.calendar.config(state=tk.DISABLED)
#             threading.Thread(target=self.execute_scripts, args=('baac_stmt', selected_date)).start()
#         else:
#             messagebox.showwarning("Input Error", "Please select a date")
#
#     def execute_scripts(self, selected_script, selected_date):
#         if selected_script == 'All':
#             self.run_all_scripts(selected_date)
#         else:
#             self.run_single_script(selected_script, selected_date)
#
#         self.status_var.set("Finished")
#         self.run_button.config(state=tk.NORMAL)
#         self.run_baac_stmt_button.config(state=tk.NORMAL)
#         self.reset_button.config(state=tk.NORMAL)
#         self.script_menu.config(state=tk.NORMAL)
#         self.calendar.config(state=tk.NORMAL)
#
#     def run_single_script(self, script_name, input_date):
#         script_module_name = scripts.get(script_name, script_name)  # Handle baac_stmt
#         try:
#             script_module = importlib.import_module(script_module_name)
#             script_module.main(input_date=input_date)
#             result = f"{script_name}: success"
#             # Add result label for success
#             label = tk.Label(self.result_frame, text=result)
#             label.pack(anchor='w')
#         except Exception as e:
#             logging.error(f"Failed to run script {script_name}: {str(e)}", exc_info=True)
#             result = f"{script_name}: Failed to run script {script_name}: {str(e)}"
#             # Show error message in a default message box
#             messagebox.showerror("Error", result)
#
#     def run_all_scripts(self, input_date):
#         errors = []
#         for script_name in scripts:
#             if script_name != 'All':
#                 try:
#                     script_module = importlib.import_module(scripts[script_name])
#                     script_module.main(input_date=input_date)
#                     result = f"{script_name}: success"
#                     # Add result label for success
#                     label = tk.Label(self.result_frame, text=result)
#                     label.pack(anchor='w')
#                 except Exception as e:
#                     logging.error(f"Failed to run script {script_name}: {str(e)}", exc_info=True)
#                     errors.append(f"{script_name}: {str(e)}")
#
#         if errors:
#             error_messages = "\n".join(errors)
#             messagebox.showerror("Error", f"Some scripts failed to run:\n{error_messages}")
#         else:
#             messagebox.showinfo("Success", f"All scripts ran successfully with date {input_date}")
#
#     def reset_values(self):
#         self.script_var.set('')
#         self.calendar.selection_clear()
#         self.status_var.set('')
#         for widget in self.result_frame.winfo_children():
#             widget.destroy()
#
#
# if __name__ == "__main__":
#     app = App()
#     app.mainloop()
#
#
#
#
# import time
#
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import Select
#
# #Download
# import shutil
# import os
# import logging
#
# #สร้าง Web Driver
# options = webdriver.ChromeOptions()
# options.add_experimental_option("detach",True)
# driver = webdriver.Chrome(options=options)
#
# #Download
# driver.get("https://www.selenium.dev/selenium/web/downloads/download.html")
# ahref = driver.find_element(By.CSS_SELECTOR,"a[href='file_1.txt']")
#
# # Click the link (optional)
# ahref.click()
#
#
# driver.get("https://www.selenium.dev/selenium/web/clicks.html")
#
# # Configure logging
# # logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
#
# def move_files(source_dir, destination_dir):
#     try:
#         # Ensure the destination directory exists
#         os.makedirs(destination_dir, exist_ok=True)
#
#         # Get a list of all files in the source directory
#         files = os.listdir(source_dir)
#
#         # Move each file to the destination directory
#         for file in files:
#             source_path = os.path.join(source_dir, file)
#             destination_path = os.path.join(destination_dir, file)
#             shutil.move(source_path, destination_path)
#             print(f"Moved '{file}' to '{destination_dir}'")
#
#         # Delete all files in the source directory
#         # for file in files:
#         #     file_path = os.path.join(source_dir, file)
#         #     os.remove(file_path)
#         #     print(f"Deleted '{file}' from '{source_dir}'")
#
#     except Exception as e:
#         # Log the error
#         print('error : ' + e)
#         logging.error(f"An error occurred in function: {move_files.__name__}: {str(e)}")

# Set the source and destination directories
# source_dir = "C:/Downloads"
# destination_dir = "D:/_GHB/Python/DI2/download"

# source_dir = "C:/Users/GHBservice/Downloads"
# destination_dir = "E:/my_work_OLD/_Git/Python/DI2/download"
#
# # Move files
# move_files(source_dir, destination_dir)

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
