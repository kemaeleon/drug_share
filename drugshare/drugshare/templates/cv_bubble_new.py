import folium
from folium import IFrame
import folium.plugins as plugins
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import requests
import io
import os
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
state_geo = r"map.json"

'''Calculate lookup for centroids of Lower Tier Local Authories  '''
from shapely.geometry import shape
import json

lookup_cog = {}
with open('map.json') as json_file:
    collection = json.load(json_file)
    features = collection["features"]
    for feature in features:
        s = shape(feature["geometry"])
        l = feature["properties"]["lad19nm"]
        lookup_cog[l]=s.centroid


'''Get Covid 19 government data file'''
url="https://coronavirus.data.gov.uk/downloads/csv/coronavirus-cases_latest.csv"
s=requests.get(url).content
virus = pd.read_csv(io.StringIO(s.decode('utf-8'))).drop_duplicates(subset=None, keep='first', inplace=False)
virus = virus.replace(to_replace="Hackney and City of London", value="Hackney")
''' Select lower tier LA data '''
virus = virus.loc[virus['Area type'] == 'ltla']
virus = virus.replace(to_replace = "Cornwall and Isles of Scilly", value="Cornwall")
virus = virus[['Area name', 'Specimen date', 'Daily lab-confirmed cases']]
virus_index = pd.pivot_table(virus, index='Area name', columns= ['Specimen date'], values = "Daily lab-confirmed cases").fillna(0).rename_axis(None, axis=1)
virus_index['Area nm'] = virus_index.index

''' Merge with Population data '''
covid_uk = virus_index.merge(pop, how='inner', left_on='Area nm', right_on='AREA')
covid_uk = covid_uk.fillna(0)


start_date = date(2020, 3,12)
end_date = date.today()-timedelta(2)

''' Calculate sum of weekly cases and differences of sums of weekly cases, sds, sdsnorm '''
(sds, sdsnorm, rsds, delta_sdsnorm,ratio,barplots) = (covid_uk.copy(deep=True) for i in range(6))

barplots = barplots.set_index('AREA')
barplots = barplots.drop(columns=['2020','Area nm'])
for index, row in barplots.iterrows():
    label = str(index).replace(" ","_")
    tmp = barplots.T[index]
    tmp.plot(figsize=(3.0,3.0))
    plt.xticks(rotation='45')
    plt.ylabel("Daily cases")
    plt.tight_layout()
    plt.savefig(os.path.join(os.getcwd(),'static',label + '.png'))
    plt.close()


th = 0
for single_date in daterange(start_date, end_date):
    date = single_date.strftime("%Y-%m-%d")
    sds[date] = 0
    for days in go_back(single_date,7):
        back_day = days.strftime("%Y-%m-%d")
        sds[date] += covid_uk[back_day]
    sdsnorm[date]=np.sqrt(sds[date]/(sds['2020']/100000))    
    th = max(th, sdsnorm[date].max())
bins = [0,0.00001,1,4,7,14,20,th]


for single_date in daterange(start_date, end_date):
    growing = 0
    shrinking = 0
    same = 0
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
        #delta_sdsnorm[date] = sdsnorm[date]-sdsnorm[back_day]
        delta_sdsnorm[date] = sdsnorm[date]
        ratio[date] = sds[date]/sds[back_day].replace(np.inf, 5)
        ratio[date] = ratio[date].fillna(1)
        for index, row in rsds.iterrows():
            ly=str(row['AREA'])
            if ly == 'Hackney':
                ly = "Hackney and City of London"   
            l1 = "LA: " + ly + "<br>" 
            l2 = "Pop: " + str(row['2020']) + "<br>" 
            l3 = "Week to " +  str(date) + ", new cases: "  + str(sds[date][index]) + "<br>" 
            l4 = "Change prev week: " + str(row[date]) + "<br>"
            LA = str(row['AREA']).replace(" ","_")
            im = '<img src="https://data.kemaeleon.com/static/' + LA + '.png">'
            popup_str = "<p style=font-family:'sans-serif' font-weight:300>" + l1 + l2 + l3+ l4 + str(im) + "</p>"
            iframe = IFrame(html=popup_str, width=600, height=400)
            normpt = float(delta_sdsnorm[date][index])
            ratio_pt = float(ratio[date][index])
            bubblestring='lightgrey'
            if ratio_pt == np.inf:
                ratio_pt = 1
                growing +=1
                bubblestring = 'blue'
            elif ratio_pt > 1.0:
                bubblestring = 'red'
                growing += 1
            elif ratio_pt < 1.0:
                bubblestring = 'green'
                shrinking += 1
                ratio_pt = 1.0
            elif ratio_pt == 1:
                same += 1
                bubblestring = 'blue'
            pt = lookup_cog[row['AREA']]    
            folium.Circle(
            location = [pt.coords[0][1], pt.coords[0][0]],
            popup=folium.Popup(iframe, max_width=350),
            radius=ratio_pt*200,
            fill_opacity=0.3,
            fill_color=bubblestring,
            color=bubblestring,
            fill=False,
            ).add_to(m)
            '''
            if normpt > 0:
                colstring='red'
            else:
                colstring='green'
            old = str(sds[back_day][index])
            pt = lookup_cog[row['AREA']]
            if np.square(normpt) > 10 :
                pt = lookup_cog[row['AREA']],
                folium.Marker(
                location = [pt[0].coords[0][1], pt[0].coords[0][0]],
                popup= popup_str,
                icon=folium.Icon(color=colstring, icon='info-sign'),
                ).add_to(m)
                '''
    title_html = '''
    <h3 align="center" style="font-size:20px"><b>Density of weekly tier 1 and tier 2 Covid-19 Cases in England LAs</b></h3>
    <h6 align="center" style="font-size:20px"> code at: https://github.com/kemaeleon/drug_share/blob/master/drugshare/drugshare/templates/cv_bubble_new.py, MIT Licence</h6>
             '''
    top_of_page = '''
    <body>
    <div class="container">
 <div class="row">
                <div class="col-sm-4"></div>
                <div id="logo" class="col-sm-4">
                <img src="/static/kemaeleon.png"" alt="Kemaeleon">
                </div>
                <div class="col-sm-4"></div>
        </div>
        </div>
          <link href="https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/themes/smoothness/jquery-ui.css" rel="stylesheet"/>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
<script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js"></script>

<script type="text/javascript">
     $(function(){

    $('.thedate').datepicker({
        dateFormat: 'yy-mm-dd',//2017-01-29
    });

});

    function goToPage() {
        var page = document.getElementById('id-end').value;
        window.location = "/" +  page + ".html";
    }
</script>
Select 7-day sum of cases up to the folllowing date:
<input type="text" id="id-end" class="thedate" />
<input type="submit" value="submit" onclick="goToPage();" />
<h6 align="left" style="font-size:12px"><b>size of bubbles reflect change in case numbers from previous week</b></h6>
<h6 align="left" style="font-size:12px"><b>red: increase, green: decrease, grey: no change, blue bubble: new from zero</b></h6>


        '''
    style =""" 
    <style>
    .leaflet-popup-pane{margin-top: 100px;}
    #logo img{margin: 10px;
          max-height: 90px}
    #ui-datepicker-div {z-index: 1000 !important;}
    .leaflet-right .leaflet-control{background: white !important;}
    </style>
    """
    head = """
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous"> """
    m.get_root().header.add_child(folium.Element(head)) 
    m.get_root().header.add_child(folium.Element(style))         
    m.get_root().html.add_child(folium.Element(top_of_page))
    with open(show + '.html', 'w') as file:
        file.write("{% load static %}")
    m.save(show + '._dump_html','a')
    with open(show + '.html', 'a') as file:
        file.write(title_html)
    print("GROWSHRINK", show, growing, same, shrinking, growing+shrinking+same)
