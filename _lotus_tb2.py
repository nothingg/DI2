from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def find_and_click_rtf(driver, date_str, title):
  """Finds the row containing the specified date and clicks the image with the given title.

  Args:
      driver (WebDriver): The Selenium WebDriver instance.
      date_str (str): The date string to search for (e.g., "02-May-2024").
      title (str): The title attribute value of the image to click (e.g., "RTF").
  """

  # Wait for the table to be present
  WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "DATA")))

  # Find all table rows
  rows = driver.find_elements(By.TAG_NAME, "tr")

  for row in rows:
    # Find the date cell within the row
    date_cell = row.find_element(By.XPATH, ".//td[text()='" + date_str + "']")

    if date_cell:  # Check if the date cell is found
      # Find the image with the specified title
      image_to_click = row.find_element(By.XPATH, ".//img[@title='" + title + "']")
      image_to_click.click()
      return  # Exit the loop after clicking the desired image

  # If no matching row is found
  print(f"Row containing '{date_str}' not found.")

# Example usage
driver = webdriver.Chrome()  # Replace with your preferred WebDriver
driver.get("your_table_url")

find_and_click_rtf(driver, "02-May-2024", "RTF")

driver.quit()
