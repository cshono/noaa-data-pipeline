import json
import requests 
from datetime import datetime
import pandas as pd

def get_secrets():
    with open('secrets.json','r') as f:
        secrets = json.load(f)
    return secrets

def get_data(fips, year):
    url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
    secrets = get_secrets()
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31" 
    headers = {
        "token": secrets["noaa_api_key"]
    } 
    querystring = {
        "datasetid": "GHCND",
        "datatypeid": ["AWND","UGRD", "VGRD"],
        "locationid": fips,
        "startdate": start_date,
        "enddate": end_date,
        "limit": 1000
    } 
    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        return response.json().get('results', [])
    
    print("Failed to retrieve data:", response.status_code)
    return None
    

if __name__ == "__main__":
    fips_list = ['FIPS:06075', 'FIPS:37183']
    current_year = datetime.now().year 
    years = [2010, 2020, 2023] 
    all_data = [] 
    
    for fips in fips_list:
        for year in years:
            print(f"Getting: {fips}, {year}")
            fip_year_data = get_data(fips, year) 
            all_data.extend(fip_year_data) 
        
    df = pd.DataFrame(all_data) 
    df.to_csv("./data/raw.csv", index=False) 
    
    print("Data saved to ./data/raw.csv") 
    