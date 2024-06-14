import requests
import json

# Your NOAA API token
with open('secrets.json','r') as f:
    secrets = json.load(f)
token = secrets['noaa_api_key']

# Base URL for datatypes endpoint
base_url = 'https://www.ncei.noaa.gov/cdo-web/api/v2/datatypes'
start_date = '2020-01-01'
end_date = '2020-12-31'

# Parameters
params = {
    'datasetid': 'GHCND',
    'locationid': 'FIPS:06075',
    'startdate': start_date,
    'enddate': end_date,
    'limit': 1000  # Adjust limit if necessary
}

# Headers
headers = {
    'token': token
}

# Make the request
response = requests.get(base_url, headers=headers, params=params)

# Check response status
if response.status_code == 200:
    datatypes = response.json().get('results', [])
    for datatype in datatypes:
        print(f"ID: {datatype['id']}, Name: {datatype['name']}")
else:
    print(f'Failed to retrieve datatypes: {response.status_code}')
