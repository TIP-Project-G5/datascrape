from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import pandas as pd
import time

website = 'http://111.93.109.166/CMWSSB-web/onlineMonitoringSystem/waterLevel'

driver = webdriver.Chrome()

driver.get(website)

# select dropdown and select element inside by visible text
category_dropdown = Select(driver.find_element(By.ID, 'category'))
category_dropdown.select_by_visible_text('Rainfall')

# select another dropdown and select element inside by visible text
location_dropdown = Select(driver.find_element(By.ID, 'areaLocationId'))
location_dropdown.select_by_value('1')

# select date picker and select element inside date picker
date_picker = driver.find_element(By.ID, 'dateTimePicker')
date_picker.click()

date_element = driver.find_element(By.XPATH, '//td[@class="day"][text()="2"]')
date_element.click()

# select button by ID
rainfall_button = driver.find_element(By.ID, 'checkWaterLevel')
rainfall_button.click()

# implicit wait for 5 seconds
time.sleep(5)
# select elements in the table
match = driver.find_element(By.ID, 'inputLevelDiv2')

print(match.text)

#quit drive we opened in the beginning
driver.quit()

