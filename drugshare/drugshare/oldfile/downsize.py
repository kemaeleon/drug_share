import folium
import pandas as pd
import geopandas as gpd
import requests
import io
from shapely.wkt import loads
import re
pd.set_option('display.max_columns', 50, 'display.max_rows', 500)
simpledec = re.compile(r"\d*\.\d+")
def mround(match):
    return "{:.3f}".format(float(match.group()))

state_geo = gpd.read_file("Local_Authority_Districts__December_2019__Boundaries_UK_BFC.geojson").round(decimals=2)
print(state_geo)
