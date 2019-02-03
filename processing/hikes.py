import json
import pandas as pd
import numpy as np

import xml.etree.cElementTree as ET

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

# df = pd.read_csv('data/hiking.csv')
df = df_to_geoframe(df, 'lon', 'lat', 'epsg:3035', 'epsg:3857', False)
df['lat'] = df.apply(getPointCoords, geom='geometry', coord_type='x', axis=1)
df['lon'] = df.apply(getPointCoords, geom='geometry', coord_type='y', axis=1)
p_df = df.drop('geometry', axis=1).copy()
df = df.drop('geometry', axis=1).copy()


tree = ET.ElementTree(file='data/Friluftsliv_0000_Norge_3035_TurOgFriluftsruter_GML.gml')
tr = tree.getroot()
tull = '{http://skjema.geonorge.no/SOSI/produktspesifikasjon/TurOgFriluftsruter/20171210}'
tull2 = '{http://www.opengis.net/gml/3.2}'
trackstrings = []
for element in tr.findall('{http://www.opengis.net/gml/3.2}featureMember'):
    for feature in element:
        for meh in feature:
            for geom in meh.findall(tull2+'LineString'):
                
                for coord in geom:
                    trackstrings.append(coord.text)
tracks = []

for track in trackstrings:
    tmp = np.array(track.split())
    tracks.append(np.reshape(tmp, (int(len(tmp)/2), 2)))

dfs = []
for track in tracks:
    lat = []
    lon = []
    name = []
    unique = uuid.uuid4()
    for coord in track:
        lat.append(float(coord[0]))
        lon.append(float(coord[1]))
        name.append(unique)
    dfs.append(pd.DataFrame({'lat':lat, 'lon':lon, 'name':name}))
df = pd.concat(dfs)



#Getting GML data to pandas somehow - Doesnt work properly
def records(file):  
    import gdal
    from osgeo import ogr
    # generator 
    reader = ogr.Open(file)
    layer = reader.GetLayer()
    all_recs = []
    print(reader.keys())
    print(layer.GetFeatureCount())
    for i in range(layer.GetFeatureCount()):
        feature = layer.GetFeature(i)
        
        
        all_recs.append(json.loads(feature.ExportToJson()))
    return all_recs

def gml_to_df(file):
    dfs = []
    for a in records(file):
        lon = []
        lat = []
        gml_id = []
#         print(a['properties']['vedlikeholdsansvarlig'])
        #for trace in a['geometry']['coordinates']:
        #    lon.append(trace[0])
        #    lat.append(trace[1])
        gml_id.append(a['properties']['gml_id'])
        df = pd.DataFrame({'name':gml_id})
        dfs.append(df)
    df = pd.concat(dfs)
    return df