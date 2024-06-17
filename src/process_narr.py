import xarray as xr
import pandas as pd
import numpy as np
import json

def read_nc_datasets(variables):
    datasets = {}
    for variable in variables:
        file_path = f'./data/{variable}.10m.mon.mean.nc'
        datasets[variable] = xr.open_dataset(file_path) 
    return datasets

def read_county_centroids():
    return pd.read_csv("./data/us_county_centroids.csv")

def select_ds_lon_lat(ds, variable, longitude, latitude):
    # Find the nearest indices for the specified longitude and latitude
    latitudes = ds['lat'].values
    longitudes = ds['lon'].values
    
    # Calculate the distance to the target point (latitude, longitude)
    distance = np.sqrt((latitudes - latitude)**2 + (longitudes - longitude)**2)
    
    # Find the indices of the minimum distance
    y_index, x_index = np.unravel_index(np.argmin(distance), distance.shape)
    min_distance = np.min(distance) 
    
    # Select the variable and extract the time series for the specified indices
    variable_data = ds[variable].isel(y=y_index, x=x_index)

    # Convert the extracted data to a pandas DataFrame
    df = variable_data.to_dataframe().reset_index()
    
    return df, min_distance

def process_narr_data(df, distance, variable_name):
    df = df.rename(columns={
        "time": "year_end",
        "lat": "narr_nearest_lat",
        "lon": "narr_nearest_lon",
        variable_name: f"avg_{variable_name}"
    })
    df['year_end'] = pd.to_datetime(df['year_end'])
    df = df.set_index("year_end")
    df = df.resample("Y").mean()
    df['year'] = df.index.year 
    df['fips_narr_distance'] = distance
    df = df.drop(["x","y"], axis=1) 
    return df

def lookup_county_lon_lat(geoid, county_df):
    county_lookup_df = county_df.set_index("GEOID")
    return county_lookup_df.loc[geoid, ["lon","lat"]]
    

def process_county(geoid, county_df, datasets):
    """_summary_

    Args:
        geoid (_type_): _description_
        county_df (_type_): _description_
        datasets (_type_): _description_
    """
    vars_df = None
    lon, lat = lookup_county_lon_lat(geoid, county_df)
    
    for variable, ds in datasets.items():
        var_df, distance = select_ds_lon_lat(ds, variable, lon, lat) 
        var_df = process_narr_data(var_df, distance, variable)
        if vars_df is None:
            vars_df = var_df.copy()
            continue 
        vars_df[f"avg_{variable}"] = var_df[f"avg_{variable}"] 
        vars_df[f"{variable}_narr_nearest_lon"] = var_df["narr_nearest_lon"].copy()
        vars_df[f"{variable}_narr_nearest_lat"] = var_df["narr_nearest_lat"].copy() 
        vars_df[f"{variable}_fips_narr_distance"] = var_df["fips_narr_distance"].copy()
        
    vars_df["fips"] = geoid
    vars_df["fips_lon"] = lon
    vars_df["fips_lat"] = lat 
    return vars_df  

def check_vars_df(vars_df):
    col_pairs = [
        ["fips_narr_distance", "uwnd_fips_narr_distance"],
        ["fips_narr_distance", "vwnd_fips_narr_distance"],
        ["narr_nearest_lat", "uwnd_narr_nearest_lat"],
        ["narr_nearest_lon", "uwnd_narr_nearest_lon"],
        ["narr_nearest_lat", "vwnd_narr_nearest_lat"],
        ["narr_nearest_lon", "vwnd_narr_nearest_lon"],
    ]
    
    for col_pair in col_pairs:
        assert all(vars_df[col_pair[0]] == vars_df[col_pair[1]]) 
        vars_df = vars_df.drop(col_pair[1], axis=1) 
        
    return vars_df 
    
        
    
# PARAMS
variables = ['wspd','uwnd','vwnd']
output_cols = ["fips","year","avg_wspd","avg_uwnd","avg_vwnd",
               "narr_nearest_lon","narr_nearest_lat","fips_lon","fips_lat"]
#geoids = [31039, 54099, 31109] 
output_df = pd.DataFrame() 
error_logs = {} 

 # Read in data 
datasets = read_nc_datasets(variables) 
county_df = read_county_centroids() 

for geoid in county_df['GEOID'].unique():
    try: 
        # Lookup lon/lat and aggregate
        vars_df = process_county(geoid, county_df, datasets)
        vars_df = check_vars_df(vars_df)
        output_df = pd.concat([output_df, vars_df], axis=0) 
    except:
        error_logs[geoid] = "failed to process county or check vars"
        print(f"Failed: {geoid}")
        
    print(f"Success: {geoid}")

    
    
output_df = output_df.reset_index()[output_cols]
output_df.to_csv("./data/county_wind_data.csv", index=False) 

with open("./data/error_logs.json","w") as f:
    json.dump(error_logs, f) 

