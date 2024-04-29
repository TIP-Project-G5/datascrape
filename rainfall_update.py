from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import pandas as pd
import mysql.connector

website = 'http://111.93.109.166/CMWSSB-web/onlineMonitoringSystem/waterLevel'

driver = webdriver.Chrome()

driver.get(website)

# refresh the entire page
driver.refresh()

# wait for the webpage to fully load after refresh
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'category')))

# disable the video
video = driver.find_element(By.TAG_NAME, "video")
driver.execute_script("arguments[0].autoplay = false;", video)

# select dropdown and select element inside by visible text
category_dropdown = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'category')))
category_dropdown = Select(category_dropdown)
category_dropdown.select_by_visible_text('Rainfall')

# select another dropdown and select element inside by visible text
location_dropdown = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'areaLocationId')))
location_dropdown = Select(location_dropdown)

# Create an empty DataFrame to store the scraped data
scraped_data = pd.DataFrame()

# make query to AWS RDS to get the data
# Connect to the MySQL database
db_connection = mysql.connector.connect(
    host="database-1.c1w22ggiyvsu.ap-southeast-2.rds.amazonaws.com",
    user="admin",
    password="tipflood",
    database="tip-flood-db"
)

# Create a cursor object to execute queries
cursor = db_connection.cursor()

# Example: Execute a SELECT query
get_query = "SELECT MAX(timestamp) AS last_rainfall_date FROM RAINFALL"
cursor.execute(get_query)

# Fetch the result
result = cursor.fetchone()
latest_date = result[0]

# get current date
current_date_time = datetime.now().date()

# calculate the date before current date
current_date_time = current_date_time - timedelta(days=1)

if latest_date < current_date_time:
    # Define the start and end dates
    # calculate the date after latest date
    start_date = latest_date + timedelta(days=1)
    end_date = current_date_time

    # add start date to the DataFrame
    scraped_data['Time'] = pd.date_range(start_date, end_date, freq='D')

    # define the dictionary of months
    months = {'1': 'Jan', '2': 'Feb', '3': 'Mar', '4': 'Apr', '5': 'May', '6': 'Jun', '7': 'Jul', '8': 'Aug', '9': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'}

    for location in location_dropdown.options:
        # Extract value attribute of the option
        option_value = location.get_attribute("value")

        # Skip the option if it is '0'
        if option_value == '0':
            continue

        # Select the option
        location_dropdown.select_by_value(option_value)

        # define a list to store the data for a specific area
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
                EC.presence_of_element_located((By.ID, 'inputLevelDiv2')))

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
        df_iteration = pd.DataFrame({f"Area{option_value}": area2data})

        # Append the DataFrame for this iteration to the main DataFrame
        scraped_data = pd.concat([scraped_data, df_iteration], axis=1)

#quit drive we opened in the beginning
driver.quit()

# execute the query to insert the data into the database
# Iterate over the rows of the DataFrame
for index, row in scraped_data.iterrows():
    # Extract values from the DataFrame row
    timestamp = row['Time']
    area_1_value = row['Area1']
    area_2_value = row['Area2']
    area_3_value = row['Area3']
    area_4_value = row['Area4']
    area_5_value = row['Area5']
    area_6_value = row['Area6']
    area_7_value = row['Area7']
    area_8_value = row['Area8']
    area_9_value = row['Area9']
    area_10_value = row['Area10']
    area_11_value = row['Area11']
    area_12_value = row['Area12']
    area_13_value = row['Area13']
    area_14_value = row['Area14']
    area_15_value = row['Area15']
    # Replace 'rf_area_id' with the actual ID of the area corresponding to 'area_1'
    rf_area_id_1 = 1
    # Replace 'rf_area_id' with the actual ID of the area corresponding to 'area_2'
    rf_area_id_2 = 2
    # Replace 'rf_area_id' with the actual ID of the area corresponding to 'area_3'
    rf_area_id_3 = 3
    # Replace 'rf_area_id' with the actual ID of the area corresponding to 'area_4'
    rf_area_id_4 = 4
    # Replace 'rf_area_id' with the actual ID of the area corresponding to 'area_5'
    rf_area_id_5 = 5
    # Replace 'rf_area_id' with the actual ID of the area corresponding to 'area_6'
    rf_area_id_6 = 6
    # Replace 'rf_area_id' with the actual ID of the area corresponding to 'area_7'
    rf_area_id_7 = 7
    # Replace 'rf_area_id' with the actual ID of the area corresponding to 'area_8'
    rf_area_id_8 = 8
    # Replace 'rf_area_id' with the actual ID of the area corresponding to 'area_9'
    rf_area_id_9 = 9
    # Replace 'rf_area_id' with the actual ID of the area corresponding to 'area_10'
    rf_area_id_10 = 10
    # Replace 'rf_area_id' with the actual ID of the area corresponding to 'area_11'
    rf_area_id_11 = 11
    # Replace 'rf_area_id' with the actual ID of the area corresponding to 'area_12'
    rf_area_id_12 = 12
    # Replace 'rf_area_id' with the actual ID of the area corresponding to 'area_13'
    rf_area_id_13 = 13
    # Replace 'rf_area_id' with the actual ID of the area corresponding to 'area_14'
    rf_area_id_14 = 14
    # Replace 'rf_area_id' with the actual ID of the area corresponding to 'area_15'
    rf_area_id_15 = 15

    # Execute INSERT query for area_1
    query_area_1 = "INSERT INTO RAINFALL (timestamp, rf_area_id, rainfall_value) VALUES (%s, %s, %s)"
    cursor.execute(query_area_1, (timestamp, rf_area_id_1, area_1_value))

    # Execute INSERT query for area_2
    query_area_2 = "INSERT INTO RAINFALL (timestamp, rf_area_id, rainfall_value) VALUES (%s, %s, %s)"
    cursor.execute(query_area_2, (timestamp, rf_area_id_2, area_2_value))

    # Execute INSERT query for area_3
    query_area_3 = "INSERT INTO RAINFALL (timestamp, rf_area_id, rainfall_value) VALUES (%s, %s, %s)"
    cursor.execute(query_area_3, (timestamp, rf_area_id_3, area_3_value))

    # Execute INSERT query for area_4
    query_area_4 = "INSERT INTO RAINFALL (timestamp, rf_area_id, rainfall_value) VALUES (%s, %s, %s)"
    cursor.execute(query_area_4, (timestamp, rf_area_id_4, area_4_value))

    # Execute INSERT query for area_5
    query_area_5 = "INSERT INTO RAINFALL (timestamp, rf_area_id, rainfall_value) VALUES (%s, %s, %s)"
    cursor.execute(query_area_5, (timestamp, rf_area_id_5, area_5_value))

    # Execute INSERT query for area_6
    query_area_6 = "INSERT INTO RAINFALL (timestamp, rf_area_id, rainfall_value) VALUES (%s, %s, %s)"
    cursor.execute(query_area_6, (timestamp, rf_area_id_6, area_6_value))

    # Execute INSERT query for area_7
    query_area_7 = "INSERT INTO RAINFALL (timestamp, rf_area_id, rainfall_value) VALUES (%s, %s, %s)"
    cursor.execute(query_area_7, (timestamp, rf_area_id_7, area_7_value))

    # Execute INSERT query for area_8
    query_area_8 = "INSERT INTO RAINFALL (timestamp, rf_area_id, rainfall_value) VALUES (%s, %s, %s)"
    cursor.execute(query_area_8, (timestamp, rf_area_id_8, area_8_value))

    # Execute INSERT query for area_9
    query_area_9 = "INSERT INTO RAINFALL (timestamp, rf_area_id, rainfall_value) VALUES (%s, %s, %s)"
    cursor.execute(query_area_9, (timestamp, rf_area_id_9, area_9_value))

    # Execute INSERT query for area_10
    query_area_10 = "INSERT INTO RAINFALL (timestamp, rf_area_id, rainfall_value) VALUES (%s, %s, %s)"
    cursor.execute(query_area_10, (timestamp, rf_area_id_10, area_10_value))

    # Execute INSERT query for area_11
    query_area_11 = "INSERT INTO RAINFALL (timestamp, rf_area_id, rainfall_value) VALUES (%s, %s, %s)"
    cursor.execute(query_area_11, (timestamp, rf_area_id_11, area_11_value))

    # Execute INSERT query for area_12
    query_area_12 = "INSERT INTO RAINFALL (timestamp, rf_area_id, rainfall_value) VALUES (%s, %s, %s)"
    cursor.execute(query_area_12, (timestamp, rf_area_id_12, area_12_value))

    # Execute INSERT query for area_13
    query_area_13 = "INSERT INTO RAINFALL (timestamp, rf_area_id, rainfall_value) VALUES (%s, %s, %s)"
    cursor.execute(query_area_13, (timestamp, rf_area_id_13, area_13_value))

    # Execute INSERT query for area_14
    query_area_14 = "INSERT INTO RAINFALL (timestamp, rf_area_id, rainfall_value) VALUES (%s, %s, %s)"
    cursor.execute(query_area_14, (timestamp, rf_area_id_14, area_14_value))

    # Execute INSERT query for area_15
    query_area_15 = "INSERT INTO RAINFALL (timestamp, rf_area_id, rainfall_value) VALUES (%s, %s, %s)"
    cursor.execute(query_area_15, (timestamp, rf_area_id_15, area_15_value))


# Commit the changes to the database
db_connection.commit()

# Close the cursor and database connection
cursor.close()
db_connection.close()