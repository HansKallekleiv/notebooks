import geopandas as gpd
import pandas as pd
def getPointCoords(row, geom, coord_type):
    """Calculates coordinates ('x' or 'y') of a Point geometry"""
    if coord_type == 'x':
        return row[geom].x
    elif coord_type == 'y':
        return row[geom].y
df = gpd.read_file('data/Skred_Skredhendelse.geojson')
df = df.to_crs({'init': 'epsg:3395'})
df['lat'] = df.apply(getPointCoords, geom='geometry', coord_type='x', axis=1)
df['lon'] = df.apply(getPointCoords, geom='geometry', coord_type='y', axis=1)
df = df.drop('geometry', axis=1).copy()
df.to_csv('data/skred.csv', index=False)
