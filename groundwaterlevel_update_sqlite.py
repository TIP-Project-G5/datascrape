from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import pandas as pd
import sqlite3

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

# get current date
current_date_time = datetime.now().date()

# calculate the date before current date
current_date_time = current_date_time - timedelta(days=1)

# Connect to the database
conn = sqlite3.connect('db.sqlite3')

# Create a cursor object
cursor = conn.cursor()

# Execute a query to fetch the latest timestamp from the TEMP table
cursor.execute("SELECT MAX(gw_timestamp) FROM GROUNDWATER")

# Fetch the result
latest_timestamp_str = cursor.fetchone()[0]

# Convert the string to a datetime object
latest_timestamp = datetime.strptime(latest_timestamp_str, '%Y-%m-%d')

# Extract date part from latest_timestamp
latest_date = latest_timestamp.date()

if latest_date < current_date_time:
    # Define the start and end dates
    # calculate the date after latest date
    start_date = latest_date + timedelta(days=1)
    end_date = current_date_time

    # define a list to store the groundwater level data for a specific depot
    area2data = []
    # create one list to store the area id
    depot_id = []
    # create one list to store the date
    date = []

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
                    date.append(current_date)
                    depot_id.append(option_value)
                except ValueError:
                    # If conversion fails, skip this iteration and continue with the next match
                    current_date += timedelta(days=1)
                    continue

                # Move to the next date
                current_date += timedelta(days=1)

    # Create a DataFrame with the data from this iteration
    df_iteration_groundwater = pd.DataFrame({"groundwater_value": area2data})
    df_iteration_date = pd.DataFrame({"date": date})
    df_iteration_id = pd.DataFrame({"depot_id": depot_id})
    # Append the DataFrame for this iteration to the main DataFrame
    combined_data = pd.concat([df_iteration_date['date'], df_iteration_groundwater['groundwater_value'], df_iteration_id['depot_id']], axis=1)

    # # execute the query to insert the data into the database
    # # Iterate over the rows of the DataFrame
    # for index, row in scraped_data.iterrows():
    #     # Extract values from the DataFrame row
    #     timestamp = row['Time']
    #     # Number of areas
    #     num_depots = 200
    #     # execute the query to insert the data into the database within the loop
    #     for i in range(1, num_depots + 1):
    #         # Execute INSERT query for each depot
    #         cursor.execute(
    #             f'INSERT INTO GROUNDWATER (gw_timestamp, gw_depot_no, groundwater_value) VALUES (%s, %s, %s)',
    #             (timestamp, i, row[f'Depot{i}']))
    #
    # # Commit the changes to the database
    # db_connection.commit()

    # execute the query to insert the data into the database
    # Iterate over the rows of the DataFrame
    for index, row in combined_data.iterrows():
        # Insert the row into the database
        cursor.execute("INSERT INTO GROUNDWATER (gw_timestamp, groundwater_value, gw_depot_no) VALUES (?, ?, ?)",
                       (row['date'], row['groundwater_value'], row['depot_id']))

    # Commit the transaction
    conn.commit()

#quit drive opened in the beginning
driver.quit()

# Close the connection
conn.close()