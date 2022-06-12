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

st.subheader('Обработаем data frame через pandas и построим для каждой теннисистки отдельный график.')


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
gdf1
gdften=gdf1.sjoin(gdfnew,predicate="intersects",how='inner')
gdften
num=gdften['index_right'].value_counts()
d=gdf1.merge(num,left_index=True,right_index=True)
st.set_option('deprecation.showPyplotGlobalUse', False)
d.plot(column='index_right', cmap='PuRd', legend=True)
st.pyplot(d)
