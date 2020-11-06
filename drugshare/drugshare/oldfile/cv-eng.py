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

''' Population Data '''
pop = pd.read_csv("pop_data.csv")[['AREA', '2020']]
pop['2020']= pop['2020'].str.replace(",","").astype(float)


''' Empty Folium Map'''

m = folium.Map(location=(51.5,0))

''' Load simplified geometry file '''
state_geo = r"test.json"

'''Calculate lookup for centroids of Lower Tier Local Authories  '''
from shapely.geometry import shape
import json

lookup_cog = {}
with open('test.json') as json_file:
    collection = json.load(json_file)
    features = collection["features"]
    for feature in features:
        s = shape(feature["geometry"])
        l = feature["properties"]["lad19nm"]
        lookup_cog[l]=s.centroid


'''Get Covid 19 government data file'''
virus = pd.read_csv("coronavirus-cases_latest.csv").drop_duplicates(subset=None, keep='first', inplace=False)

''' Select lower tier LA data '''
virus = virus.loc[virus['Area type'] == 'Lower tier local authority']
virus = virus.replace(to_replace = "Cornwall and Isles of Scilly", value="Cornwall")
virus = virus[['Area name', 'Specimen date', 'Daily lab-confirmed cases']]
virus_index = pd.pivot_table(virus, index='Area name', columns= ['Specimen date'], values = "Daily lab-confirmed cases").fillna(0).rename_axis(None, axis=1)
virus_index['Area nm'] = virus_index.index

''' Merge with Population data '''
covid_uk = virus_index.merge(pop, how='inner', left_on='Area nm', right_on='AREA')
covid_uk = covid_uk.fillna(0)


start_date = date(2020, 3, 1)
end_date = date.today()-timedelta(6)

''' Calculate sum of weekly cases and differences of sums of weekly cases, sds, sdsnorm '''
(sds, sdsnorm, rsds, delta_sdsnorm) = (covid_uk.copy(deep=True) for i in range(4))

th = 0
for single_date in daterange(start_date, end_date):
    date = single_date.strftime("%Y-%m-%d")
    sds[date] = 0
    for days in go_back(single_date,7):
        back_day = days.strftime("%Y-%m-%d")
        sds[date] += covid_uk[back_day]
    sdsnorm[date]=np.sqrt(sds[date]/(sds['2020']/100000))    
    th = max(th, sdsnorm[date].max())
bins = [0,0.00001,1,2,3,4,7,th]


for single_date in daterange(start_date, end_date):
    date = single_date.strftime("%Y-%m-%d")
    show = str(single_date)
    print(show, sum(covid_uk[date]))
    m = folium.Map(location=(51.5,0))
    lname = "week up to: " + show + ", sqrt (weekly confirmed cases / 100k people)"
    folium.Choropleth(
        tiles='cartodbpositron',
        geo_data=state_geo,
        name='choropleth',
        data=sdsnorm,
        fill_color='YlOrRd',
        legend_name = lname,
        columns=['Area nm', show],
        key_on='feature.properties.lad19nm',
        fill_opacity=0.7,
        line_opacity=0.2,
        bins = bins,
    ).add_to(m)

    for day in ref_back(single_date, 7):
        back_day = day.strftime("%Y-%m-%d")
        rsds[date] = sds[date]-sds[back_day]
        delta_sdsnorm[date] = sdsnorm[date]-sdsnorm[back_day]
        for index, row in rsds.iterrows():
            l1 = "Local Authority: " + str(row['AREA']) + "\n" 
            l2 = "Population: " + str(row['2020']) + "\n" 
            l3 = "Cases: " + str(sds[date][index]) + "\n" 
            l4 = "Change from last week: " + str(row[date])
            popup_str = l1 + l2 + l3+ l4
            normpt = float(delta_sdsnorm[date][index])
            if normpt > 0:
                colstring='red'
            else:
                colstring='green'
            old = str(sds[back_day][index])
            pt = lookup_cog[row['AREA']]
            if np.square(normpt) > 3 :
                pt = lookup_cog[row['AREA']],
                folium.Marker(
                location = [pt[0].coords[0][1], pt[0].coords[0][0]],
                popup= popup_str,
                icon=folium.Icon(color=colstring, icon='info-sign'),
                ).add_to(m)
    title_html = '''
    <h3 align="center" style="font-size:20px"><b>Density of weekly Covid-19 Cases in England LAs</b></h3>
    <h3 align="center" style="font-size:20px"><b>Maps Released Under MIT Licence</b></h3>
    <h6 align="center" style="font-size:20px"><b>Please modifiy the date in the URL for a different set of results</b></h6>

             '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    m.save(show + '.html')
