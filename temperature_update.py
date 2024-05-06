import pandas as pd
import requests
import time
import sqlite3
from datetime import datetime, timedelta

# set up area coordinates dataframe
# Define the data
coordinates_data = {
    'areaID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    'Latitude': [13.15202524, 13.17262101, 13.15119447, 13.12339742, 13.11416046,
                 13.11126115, 13.08639463, 13.08532326, 13.03316477, 13.04169033,
                 13.0419716, 13.00571456, 13.02899838, 12.98040224, 12.90125466],
    'Longitude': [80.3028678, 80.25677016, 80.23866637, 80.26009935, 80.2885777,
                  80.24848458, 80.18617769, 80.20240682, 80.25840872, 80.23838672,
                  80.16476616, 80.20253394, 80.23071804, 80.25291808, 80.22387146]
}

# Create a DataFrame
co_df = pd.DataFrame(coordinates_data)

# get current date
current_date_time = datetime.now().date()

# calculate the date before current date
current_date_time = current_date_time - timedelta(days=1)

# Connect to the database
conn = sqlite3.connect('db.sqlite3')

# Create a cursor object
cursor = conn.cursor()

# Execute a query to fetch the latest timestamp from the TEMP table
cursor.execute("SELECT MAX(tp_timestamp) FROM TEMP")

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

    # create two lists to store the minimum and maximum temperature
    mini_temp = []
    max_temp = []
    # create one list to store the area id
    area_id = []
    # create one list to store the date
    date = []

    # Loop through 15 areas
    for id in range(0, 15):
        # get the latitude and longitude of the area
        latitude = co_df.loc[id, 'Latitude']
        longitude = co_df.loc[id, 'Longitude']

        # Iterate over dates from start_date to the day before today
        current_date = start_date
        while current_date <= end_date:

            # get the area id
            area_id.append(co_df['areaID'][id])

            # get the date
            date.append(current_date)

            # Define the URL of the API endpoint you want to request
            historical_url = f'https://api.weatherstack.com/historical?access_key=8d95e3320888902c919001974be5f6b6&query={latitude},{longitude}&historical_date={current_date}&hourly=0'

            # Make a GET request
            response = requests.get(historical_url)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Extract the JSON data from the response
                data = response.json()

                mini_temperature = data['historical'][f'{current_date}']['mintemp']
                mini_temp.append(mini_temperature)
                max_temperature = data['historical'][f'{current_date}']['maxtemp']
                max_temp.append(max_temperature)

            current_date += timedelta(days=1)
            time.sleep(0.5)

    # Create a DataFrame with the data
    df_iteration_mini = pd.DataFrame({'min_temperature': mini_temp})
    df_iteration_max = pd.DataFrame({'max_temperature': max_temp})
    df_iteration_area = pd.DataFrame({'area_id': area_id})
    df_iteration_date = pd.DataFrame({'date': date})
    df_combine = pd.concat([df_iteration_area['area_id'], df_iteration_date['date'], df_iteration_mini['min_temperature'], df_iteration_max['max_temperature']], axis=1)

    # Insert into sqlite3 database row by row and iterate over each row in the DataFrame
    for index, row in df_combine.iterrows():
        # Insert the row into the database
        cursor.execute("INSERT INTO TEMP (tp_area_id, tp_timestamp, tp_min, tp_max) VALUES (?, ?, ?, ?)", (row['area_id'], row['date'], row['min_temperature'], row['max_temperature']))

    # Commit the transaction
    conn.commit()

# Close the connection
conn.close()
