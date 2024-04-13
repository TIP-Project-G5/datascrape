@ -1,8 +1,9 @@
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

website = 'http://111.93.109.166/CMWSSB-web/onlineMonitoringSystem/waterLevel'

@ -10,32 +11,48 @@ driver = webdriver.Chrome()

driver.get(website)

# refresh the entire page
driver.refresh()

# wait for the webpage to fully load after refresh
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'category')))

# disable the video
video = driver.find_element(By.TAG_NAME, "video")
driver.execute_script("arguments[0].autoplay = false;", video)

# select dropdown and select element inside by visible text
category_dropdown = Select(driver.find_element(By.ID, 'category'))
category_dropdown = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'category')))
category_dropdown = Select(category_dropdown)
category_dropdown.select_by_visible_text('Rainfall')

# select another dropdown and select element inside by visible text
location_dropdown = Select(driver.find_element(By.ID, 'areaLocationId'))
location_dropdown = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'areaLocationId')))
location_dropdown = Select(location_dropdown)
location_dropdown.select_by_value('1')

# select date picker and select element inside date picker
date_picker = driver.find_element(By.ID, 'dateTimePicker')
date_picker = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, 'dateTimePicker')))
date_picker.click()

date_element = driver.find_element(By.XPATH, '//td[@class="day"][text()="2"]')
date_element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//td[@class="day"][text()="2"]')))
date_element.click()

# select button by ID
rainfall_button = driver.find_element(By.ID, 'checkWaterLevel')
rainfall_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, 'checkWaterLevel')))
rainfall_button.click()

# implicit wait for 5 seconds
time.sleep(5)

# select elements in the table
match = driver.find_element(By.ID, 'inputLevelDiv2')
match = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'inputLevelDiv2')))

print(match.text)

#quit drive we opened in the beginning
driver.quit()

driver.quit()