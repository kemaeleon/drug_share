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


pd.set_option('display.max_columns', 50, 'display.max_rows', 500)

''' Population Data '''
pop = pd.read_csv("pop_data.csv")[['AREA', '2020']]
pop['2020']= pop['2020'].str.replace(",","").astype(float)
'''pop = pd.read_csv("poptn.csv")[['Name','All']]'''
print(pop)


virus = pd.read_csv("virus.csv").drop_duplicates(subset=None, keep='first', inplace=False)
print(virus)

covid_uk = virus.merge(pop,how="inner", left_on='WHERE', right_on='AREA')
print(covid_uk)
covid_uk['A']=covid_uk['2020']*covid_uk['TW']
covid_uk['B']=covid_uk['2020']*covid_uk['LW']
print(covid_uk['A'].sum()/100000,covid_uk['B'].sum()/100000)
