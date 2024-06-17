import geopandas as gpd
import pandas as pd

# Load the shapefile
shapefile_path = './data/tl_2023_us_county.shp'
gdf = gpd.read_file(shapefile_path)

# Calculate the centroids
gdf['centroid'] = gdf.geometry.centroid

# Extract the longitude and latitude of the centroids
gdf['lon'] = gdf.centroid.x
gdf['lat'] = gdf.centroid.y

# Select relevant columns
centroid_df = gdf[['GEOID', 'NAME', 'STATEFP', 'lon', 'lat']]

# Export to CSV
centroid_df.to_csv('./data/us_county_centroids.csv', index=False)

print("CSV file with county centroids has been created.")
