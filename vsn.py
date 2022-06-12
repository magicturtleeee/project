import pandas as pd
import streamlit as st
import plotly.express as px
import requests
import folium
import re
import json
import requests
import geopandas as gpd
import streamlit_folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

st.title('Финальный проект.')
st.subheader('Проанализируем статистику топ-20 теннисисток из WTA. Данные я скачивала с помощью библиотеки selenium и сохранила в файл wta.csv. Это можно увидеть в tennis data.py.')
a=pd.read_csv('wta.csv')
st.write(a)

st.write('Сейчас давайте займемся визуализацией данных. Для этого используем библиотеку plotly.express. У вас есть возможность выбрать, в каком формате вы хотите видеть игрока (номер в рейтинге WTA или имя), выбрать, хотите ли видеть один параметр или несколько.')
xpar=st.selectbox('In what format do you want to see the player?', a.columns[:2])
ypar=st.selectbox('Select a parameter.', a.columns[2::])

fig=px.bar(a, x=xpar, y=ypar, title='Data on WTA top 20 players',
            labels=dict(index='player'+xpar, value=ypar))
st.plotly_chart(fig)

st.write('Покажем, что если у игрока рейтинг выше, необязательно у него больше эйсов, меньше двойных и т.д. Сейчас вы можете выиграть несколько параметров, которые вы увидите на графике.')

c=st.multiselect('What data do you want to plot?', a.columns[2:5])
fig1=px.line(a, x=xpar, y=c)
st.plotly_chart(fig1)

st.write('Сейчас посмотрим на параметры, которые мы измеряем в процентах.')
c1=c=st.multiselect('What data do you want to plot?', a.columns[5::])
fig2=px.line(a, x=xpar, y=c1)
st.plotly_chart(fig2)

st.subheader('Применим машинное обучение и математику в python.')
st.markdown('Сейчас, используя машинное обучение, попробуем предсказать процент выигранных мячей с первых подач. Для этого используем линейную регрессию.')
st.markdown('Но сначала нам нужно привести данные с процентом к виду чисел в долях. Для этого используем регулярные выражения и математические операции над numpy array-ми.')

fs=list(a['first serve %'])
fs=[float(x[:-1]) for x in fs]
fs=np.array(fs)/100
fs=fs.reshape(-1, 1)
fsp=list(a['first serve points %'])
fsp=[float(x[:-1]) for x in fsp]
fsp=np.array(fsp)/100
model = LinearRegression()
model.fit(fs, fsp)
st.write('Получаем коэффициент модели', model.coef_[0], 'и константу', model.intercept_)
st.write('Сейчас вы можете написать число % попадания первых подач (целое число) , и программа предскажет, какая доля(в процентах) из этих мячей выиграна.')
number=st.number_input('Insert a number.')
st.subheader(model.predict(pd.DataFrame([[number/100]], columns=["first serve %"]))[0]*100,'%')
st.write('То есть, те, кто попадает меньше первых подач, скорее всего подают первую острее (больше целятся в угол, скорость быстрее и т.д.), поэтому логично, что они больше выигрывают мячей с первой подачи. Аналогично, те, кто более аккуратно подают первую, получают более острый ответ противника, и им сложнее выиграть очко.')
st.markdown('Используя возможности numpy, посчитаем матрицы корреляций между другими параметрами.')
rat=np.array(a['rating'])
mp=np.array(a['matches played'])
aces=np.array(a['aces'])
c1=st.multiselect('Между какими двумя параметрами рассчитаем матрицу корреляций.', a.columns[2:5])
st.subheader(corrcoef(np.array(a[c1[0]]),np.array(a[c1[1]])))


st.subheader('Вспомнив про теннис, сразу захотелось пойти поиграть. Где же в Москве есть корты?')
st.subheader("Сейчас, используя api ключ с сайта data.mos, получим данные в формате geojson. Покажем это на карте с помощью folium.")

l=pd.read_csv('courts.csv')
gdf = gpd.GeoDataFrame(l, geometry=gpd.points_from_xy(l['lon'], l['lat']))
st.write(gdf)
m = folium.Map([55.75364, 37.648280], zoom_start=10)
for ind, row in gdf.iterrows():
    folium.Marker([row.lon, row.lat],
                      radius=12, fill_color='red').add_to(m)
map=st_folium(m)

gdfnew = gpd.GeoDataFrame(l, geometry=gpd.points_from_xy(l['lat'], l['lon']))
gdf2=pd.read_csv('moscow.csv')
gdf2['poly']=gpd.GeoSeries.from_wkt(gdf2['poly'])
gdf1=gpd.GeoDataFrame(gdf2, geometry='poly')
gdf1.crs = "EPSG:4326"
gdften=gdf1.sjoin(gdfnew,predicate="intersects",how='inner')
num=gdften['name_left'].value_counts()
an=gdf1.set_index('name').assign(num=num)
an.crs = "EPSG:4326"
an=an.reset_index()
an=an.fillna(0)
an['num'].astype('int')
an['name'].astype('str')

m1 = folium.Map([55.75364, 37.648280], zoom_start=10)
gdfjson=gdf1.to_json()
gdfjson=json.loads(gdfjson)

choropleth=folium.Choropleth(geo_data=gdfjson, data=an, columns=['name','num'],
                      key_on='feature.properties.name',
                      fill_color='PuRd',
                      fill_opacity=0.7,
                      line_opacity=0.2,
                      legend_name='num',
                      highlight=True,
                      reset=True).add_to(m1)
choropleth.geojson.add_child(folium.features.GeoJsonTooltip(['name'],labels=False))
map1=st_folium(m1)
