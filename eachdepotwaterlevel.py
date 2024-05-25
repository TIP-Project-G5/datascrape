from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import pandas as pd

website = 'http://111.93.109.166/CMWSSB-web/onlineMonitoringSystem/waterLevel'

driver = webdriver.Chrome()

driver.get(website)

# refresh the entire page
driver.refresh()

# wait for the webpage to fully load after refresh
WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, 'category')))

# disable the video
video = driver.find_element(By.TAG_NAME, "video")
driver.execute_script("arguments[0].autoplay = false;", video)

# select dropdown and select element inside by visible text
category_dropdown = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'category')))
category_dropdown = Select(category_dropdown)
category_dropdown.select_by_visible_text('Ground Water level')

# select area dropdown and select element inside by option value
area_dropdown = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'areaId')))
area_dropdown = Select(area_dropdown)

# Create an empty DataFrame to store the scraped data
scraped_data = pd.DataFrame()

# Define the start and end dates
start_date = datetime(2021, 1, 1)
end_date = datetime(2024, 5, 15)

# add start date to the DataFrame
scraped_data['Time'] = pd.date_range(start_date, end_date, freq='D')

# define the dictionary of months
months = {'1': 'Jan', '2': 'Feb', '3': 'Mar', '4': 'Apr', '5': 'May', '6': 'Jun', '7': 'Jul', '8': 'Aug', '9': 'Sep',
          '10': 'Oct', '11': 'Nov', '12': 'Dec'}

for area in area_dropdown.options:
    # Extract value attribute of the option
    area_option_value = area.get_attribute("value")

    # Skip the option if it is '0'
    if area_option_value == '0':
        continue

    # Select the specific area option
    area_dropdown.select_by_value(area_option_value)

    # select depot dropdown and select element inside by option value
    location_dropdown = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'deptId')))
    location_dropdown = Select(location_dropdown)


    # Iterate through each depot option and select it
    for location in location_dropdown.options:
        # Extract value attribute of the option
        option_value = location.get_attribute("value")

        # Select the option
        location_dropdown.select_by_value(option_value)


        # define a list to store the data for a specific location
        area2data = []

        current_date = start_date

        # Iterate through each year, month, and day
        while current_date <= end_date:

            # Extract year, month, and day from the current date
            year = current_date.year
            month = current_date.month
            month = months.get(str(month))
            day = current_date.day

            # select date picker and select element inside date picker
            date_picker = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//section[@class='content']//label[@class='input-group-text']")))
            date_picker.click()

            # Select the year range
            yearRange_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@class='datetimepicker-days']//th[@class='switch']"))
            )
            yearRange_element.click()

            # Select the year specific range
            yearspecific_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@class='datetimepicker-months']//th[@class='switch']"))
            )
            yearspecific_element.click()

            # Select the year
            year_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//div[@class='datetimepicker-years']//span[text()='{year}']"))
            )
            year_element.click()

            # Select the month
            month_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//div[@class='datetimepicker-months']//span[text()='{month}']"))
            )
            month_element.click()

            # Select the day
            day_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//div[@class='datetimepicker-days']//td[@class='day' and text()='{day}']"))
            )
            day_element.click()

            # select button by ID
            rainfall_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'checkWaterLevel')))
            rainfall_button.click()

            # select element in the table
            match = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'inputLevelDiv1')))

            # add the data to the list and error handling
            try:
                # Attempt to convert match.text to float and append to area2data
                area2data.append(float(match.text))
            except ValueError:
                # If conversion fails, skip this iteration and continue with the next match
                current_date += timedelta(days=1)
                continue

            # Move to the next date
            current_date += timedelta(days=1)

        # Create a DataFrame with the data from this iteration
        df_iteration = pd.DataFrame({f"Depot{option_value}": area2data})

        # Append the DataFrame for this iteration to the main DataFrame
        scraped_data = pd.concat([scraped_data, df_iteration], axis=1)

# Export to CSV (Excel)
scraped_data.to_csv('trydepotnew.csv', index=False)

# print(rainfalldata)

#quit drive we opened in the beginning
driver.quit()