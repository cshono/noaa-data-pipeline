import requests
import json
import pandas as pd

# Your NOAA API token
with open('secrets.json','r') as f:
    secrets = json.load(f)
token = secrets['noaa_api_key']

# Parameters
dataset_id = 'GHCND'  # Example dataset ID
location_id = 'FIPS:06075'  # Example FIPS code for San Francisco County, CA
datatype_id = 'WDF2'  # Example datatype ID for average temperature
base_url = 'https://www.ncei.noaa.gov/cdo-web/api/v2/data'

# Function to fetch the earliest available date for the given parameters
def fetch_earliest_date(dataset_id, location_id, datatype_id):
    params = {
        'datasetid': dataset_id,
        #'locationid': location_id,
        'datatypeid': datatype_id,
        'startdate': '1993-01-01',
        'enddate': '1993-12-31',
        'limit': 1,
        'sortfield': 'date',
        'sortorder': 'asc'
    }
    headers = {
        'token': token
    }
    response = requests.get(base_url, headers=headers, params=params)
    return response
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            return results[0]['date']
        else:
            print('No data found for the given parameters.')
            return None
    else:
        print(f'Failed to retrieve data: {response.status_code}')
        return None
response = fetch_earliest_date(dataset_id, location_id, datatype_id)

'''
# Fetch the earliest date
earliest_date = fetch_earliest_date(dataset_id, location_id, datatype_id)

if earliest_date:
    print(f'The earliest available date for dataset {dataset_id}, location {location_id}, and datatype {datatype_id} is {earliest_date}.')
'''