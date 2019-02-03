import gpxpy
import pandas as pd
import numpy as np
import glob
import uuid
import geopandas as gpd
from fitparse import FitFile

def collect_gpx_files(path):
    gpxfiles = []
    for gpxfile in glob.glob(path+'/*.gpx'):
    
        with open(gpxfile, 'r') as f:
            p = gpxpy.parse(f)
            gpxfiles.append(p)
    return gpxfiles

def gpfx_files_to_df(gpxfiles):
    dfs = []
    for gpx in gpxfiles:
        for track in gpx.tracks:
            name=[]
            for segment in track.segments:
                lat = []
                lon = []
                date = []
                for point in segment.points:
                    date.append(point.time)
                    lat.append(point.latitude)
                    lon.append(point.longitude)
                    name.append(track.name)
                df = pd.DataFrame({'name':name, 'lat':lat, 'lon':lon, 'date':date})
                dfs.append(df)
    return pd.concat(dfs)

def fit_files_to_df(path):
    
    dfs = []
    for fitfile_path in glob.glob(path+'/*.fit'):
        fitfile = FitFile(fitfile_path)
        lat = []
        lon = []
        name = []
        date = []
        unique = uuid.uuid4().hex
        # Get all data messages that are of type record
        for record in fitfile.get_messages('record'):
            
            for record_data in record:
                
                # Print the records name and value (and units if it has any)
                if record_data.units:
                    if 'position_lat' in record_data.name:
                        
                        if record_data.value is not None:
                            lat.append(record_data.value*(180/(2**31)))
                        else:
                            lat.append(record_data.value)
                    if 'position_long' in record_data.name:
                        if record_data.value is not None:
                            lon.append(record_data.value*(180/(2**31)))
                        else:
                            lon.append(record_data.value)
                        name.append(unique)
                else:
                    if 'time' in record_data.name:
                        date.append(record_data.value)
                        
        if len(lat) == len(lon) == len(name) == len(date):
            df = pd.DataFrame({'name':name, 'lat':lat, 'lon':lon, 'date':date})
            dfs.append(df)
    return pd.concat(dfs)

def df_to_geoframe(df, lon_col, lat_col, input_crs, output_crs, drop_na=True):
    data = df.copy()
    if drop_na:
        data = data.dropna()
    geometry = [Point(xy) for xy in zip(data[lon_col], data[lat_col])]
    tmp_df = data.drop([lon_col, lat_col], axis=1)
    crs = {'init': input_crs}
    gdf = GeoDataFrame(data, crs=crs, geometry=geometry)
    gdf = gdf.to_crs({'init': output_crs})
    return gdf

def getPointCoords(row, geom, coord_type):
    """Calculates coordinates ('x' or 'y') of a Point geometry"""
    if coord_type == 'x':
        return row[geom].x
    elif coord_type == 'y':
        return row[geom].y

gpxfiles = collect_gpx_files('data/strava/activities')
df_gpx = gpx_files_to_df(gpxfiles)
df_fit = fit_files_to_df('data/strava/activities')
gdf_gpx = df_to_geoframe(df_gpx, 'lon', 'lat', 'epsg:4326', 'epsg:3857')
gdf_fit = df_to_geoframe(df_fit, 'lon', 'lat', 'epsg:4326', 'epsg:3857')
df = pd.concat([gdf_fit, gdf_gpx])
df.to_parquet('data/strava.parq')