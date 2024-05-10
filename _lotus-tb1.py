from selenium import webdriver
from selenium.webdriver.common.by import By

# Assuming you already have a WebDriver instance called 'driver'
# Replace 'driver_path' with the path to your webdriver executable
driver = webdriver.Chrome(executable_path='driver_path')

# Load the webpage
driver.get("your_website_url")

# Find all rows in the table
rows = driver.find_elements(By.XPATH, "//table[@class='DATA']/tbody/tr")

# Iterate over each row
for row in rows:
    # Find the date cell in the row
    date_cell = row.find_element(By.XPATH, "./td[contains(text(), '02-May-2024')]")
    if date_cell:
        # Find the image with the title 'RTF' in the same row
        rtf_image = row.find_element(By.XPATH, "./td/img[@title='RTF']")
        if rtf_image:
            # Click the image
            rtf_image.click()
            break  # Stop iterating if found

# Close the WebDriver
driver.quit()
