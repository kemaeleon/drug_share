import folium
import pandas as pd
import requests
import io
from datetime import timedelta, date
def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def go_back(end_date, days):
    for n in range(0,days):
        yield end_date - timedelta(n)

pd.set_option('display.max_columns', 50, 'display.max_rows', 500)

pop = pd.read_csv("pop_data.csv")[['CODE', '2020']]
pop['2020']= pop['2020'].str.replace(",","").astype(float)

m = folium.Map(location=(51.5,0))
state_geo = r"Counties_and_Unitary_Authorities__December_2017__Boundaries_UK.geojson"
print(state_geo)
url="https://coronavirus.data.gov.uk/downloads/csv/coronavirus-cases_latest.csv"
s=requests.get(url).content

virus = pd.read_csv(io.StringIO(s.decode('utf-8'))).drop_duplicates(subset=None, keep='first', inplace=False)
virus = virus.loc[virus['Area type'] == 'Upper tier local authority']
virus = virus.replace(to_replace = "Cornwall and Isles of Scilly", value="Cornwall")
virus = virus[['Area name', 'Specimen date', 'Daily lab-confirmed cases']]
virus_index = pd.pivot_table(virus, index='Area name', columns= ['Specimen date'], values = "Daily lab-confirmed cases").fillna(0).rename_axis(None, axis=1)
virus_index['Area name'] = virus_index.index
print(virus_index)
folium.Choropleth(
    geo_data=state_geo,
    name='choropleth',
    data=virus_index,
    columns=['Area name', '2020-06-04'],
    key_on='feature.properties.ctyua17nm',
    fill_color='YlGn',
    fill_opacity=0.7,
    line_opacity=0.2,
).add_to(m)

m.save('index.html')
