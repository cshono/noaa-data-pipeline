import requests
import json
import pandas as pd

# Your NOAA API token
with open('secrets.json','r') as f:
    secrets = json.load(f)
token = secrets['noaa_api_key']

# Parameters
dataset_id = 'GHCND'  # Global Summary of the Year
#location_id = 'FIPS:06075'  # Example FIPS code for San Francisco County, CA
start_date = '2010-01-01'
end_date = '2010-12-31'
units = 'metric'
base_url = 'https://www.ncei.noaa.gov/cdo-web/api/v2/data'

# Function to fetch data for a given year
def fetch_annual_summary(start_date, end_date):
    params = {
        'datasetid': dataset_id,
        'datatypeid': ["WDF2"], #["UGRD"], #["AWND","UGRD", "VGRD"],
        #'locationid': location_id,
        'startdate': start_date,
        'enddate': end_date,
        'units': units,
        'limit': 1000  # Max limit per request, adjust as needed
    }
    headers = {
        'token': token
    }
    response = requests.get(base_url, headers=headers, params=params)
    if response.status_code == 200:
        return response
    else:
        print(f'Failed to retrieve data: {response.status_code}')
        return []

# Fetch annual summary data for the specified year
response = fetch_annual_summary(start_date, end_date)
data_1990 = response.json().get('results', [])

# Convert to DataFrame
df = pd.DataFrame(data_1990)

# Save to CSV
df.to_csv('annual_summary_1990.csv', index=False)

print('Data saved to annual_summary_1990.csv')
