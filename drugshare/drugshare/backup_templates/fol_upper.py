import folium
import folium.plugins as plugins
import pandas as pd
import geopandas as gpd
import requests
import io
import numpy as np
from datetime import timedelta, date
def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def go_back(end_date, days):
    for n in range(0,days):
        yield end_date - timedelta(n)

def ref_back(end_date, days):
    yield end_date - timedelta(days)


pd.set_option('display.max_columns', 50, 'display.max_rows', 500)

pop = pd.read_csv("pop_data.csv")[['AREA', '2020']]
pop['2020']= pop['2020'].str.replace(",","").astype(float)

m = folium.Map(location=(51.5,0))
state_geo = r"test.json"
print(state_geo)

from shapely.geometry import shape
import json

lookup_cog = {}
with open('test.json') as json_file:
    collection = json.load(json_file)
    features = collection["features"]
    for feature in features:
        s = shape(feature["geometry"])
        l = feature["properties"]["lad19nm"]
       # print(l)
       # print(s.centroid)

        lookup_cog[l]=s.centroid
        print(l,lookup_cog[l])

url="https://coronavirus.data.gov.uk/downloads/csv/coronavirus-cases_latest.csv"
s=requests.get(url).content

virus = pd.read_csv(io.StringIO(s.decode('utf-8'))).drop_duplicates(subset=None, keep='first', inplace=False)
virus = virus.loc[virus['Area type'] == 'Lower tier local authority']
virus = virus.replace(to_replace = "Cornwall and Isles of Scilly", value="Cornwall")
virus = virus[['Area name', 'Specimen date', 'Daily lab-confirmed cases']]
virus_index = pd.pivot_table(virus, index='Area name', columns= ['Specimen date'], values = "Daily lab-confirmed cases").fillna(0).rename_axis(None, axis=1)
virus_index['Area nm'] = virus_index.index
print(virus_index)
covid_uk = virus_index.merge(pop, how='inner', left_on='Area nm', right_on='AREA')
covid_uk = covid_uk.fillna(0)


start_date = date(2020, 3, 1)
end_date = date.today()-timedelta(1)
sds =  covid_uk.copy(deep=True)
for single_date in daterange(start_date, end_date):
    date = single_date.strftime("%Y-%m-%d")
    sds[date] = 0
    for days in go_back(single_date,7):
        back_day = days.strftime("%Y-%m-%d")
        sds[date] += covid_uk[back_day]
    sds[date]=np.sqrt(sds[date]/covid_uk['2020']*100000.0)
    th = sds[date].max()
bins = [0,1,2,3,4,7,20]

print(sds)
rsds= sds.copy(deep = True)

for single_date in daterange(start_date, end_date):
    date = single_date.strftime("%Y-%m-%d")
    show = str(single_date)
    m = folium.Map(location=(51.5,0))

    folium.Choropleth(
        tiles='cartodbpositron',
        geo_data=state_geo,
        name='choropleth',
        data=sds,
        fill_color='YlOrRd',
        columns=['Area nm', show],
        key_on='feature.properties.lad19nm',
        fill_opacity=0.7,
        line_opacity=0.2,
        bins= bins,
    ).add_to(m)

    for day in ref_back(single_date, 7):
        back_day = day.strftime("%Y-%m-%d")
        rsds[date] = sds[date]-sds[back_day]
        for index, row in rsds.iterrows():
            if float(row[date]) > np.sqrt(3):
                pt = lookup_cog[row['AREA']],
                folium.Marker(
                location = [pt[0].coords[0][1], pt[0].coords[0][0]],
                popup='Increased by ' + str(row[date]) + "/100k ppl",
                icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(m)
            if float(row[date]) < -(np.sqrt(3)):
                pt = lookup_cog[row['AREA']],
                print(pt[0].coords[0][0], pt[0].coords[0][1])
                folium.Marker(
                location = [pt[0].coords[0][1], pt[0].coords[0][0]],
                popup='Decreased by ' + str(row[date]*-1) + "/100k ppl",
                icon=folium.Icon(color='green', icon='info-sign')
                ).add_to(m)    

    m.save(show + '.html')
