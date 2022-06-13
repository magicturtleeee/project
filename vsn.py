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
import networkx as nx
import pydot
from networkx.drawing.nx_pydot import graphviz_layout
import graphviz
#import pandas as pd
#from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.common.by import By
#from selenium.webdriver.chrome.service import Service
#from webdriver_manager.chrome import ChromeDriverManager
#import requests
#import re
#import sqlite3

with st.echo(code_location='below'):
            st.title('Финальный проект.')
            st.subheader('Проанализируем статистику топ-20 теннисисток из WTA. Данные я скачивала с помощью библиотеки selenium, используя регулярные выражение, и сохранила в файл wta.csv. Это можно увидеть в tennis data.py. На всякий случай, продублирую в конце кода.')
            a=pd.read_csv('wta.csv')
            showdat=st.expander('Посмотреть данные.')
            with showdat:
                        st.write(a)

            st.subheader('Сейчас давайте займемся визуализацией данных. Для этого используем библиотеку plotly.express. У вас есть возможность выбрать, в каком формате вы хотите видеть игрока (номер в рейтинге WTA или имя), выбрать, хотите ли видеть один параметр или несколько.')
            xpar=st.selectbox('В каком формате вы хотите увидеть игрока?', a.columns[:2])
            ypar=st.selectbox('Выберете параметр.', a.columns[2::])

            fig=px.bar(a, x=xpar, y=ypar, title='Data on WTA top 20 players',
                        labels=dict(index='player'+xpar, value=ypar))
            st.plotly_chart(fig)

            st.write('Покажем, что если у игрока рейтинг выше, необязательно у него больше эйсов, меньше двойных и т.д. Сейчас вы можете выиграть несколько параметров, которые вы увидите на графике.')

            c=st.multiselect('Какие данные вы хотите увидеть? Можно выбрать несколько параметров.', a.columns[2:5])
            fig1=px.line(a, x=xpar, y=c)
            st.plotly_chart(fig1)

            st.write('Сейчас посмотрим на параметры, которые мы измеряем в процентах.')
            c1=c=st.multiselect('Какие данные вы хотите увидеть? Можно выбрать несколько параметров.', a.columns[5::])
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
            st.subheader('Используя возможности numpy, посчитаем матрицы корреляций между другими параметрами.')

            c1=st.multiselect('Между какими двумя параметрами рассчитаем матрицу корреляций. Выводится матрица будет, только если выбрано 2 параметра.', a.columns[1:5])
            if len(c1)==2:
                        st.write(np.corrcoef(np.array(a[c1[0]]),np.array(a[c1[1]])))

            st.subheader('Сейчас давайте посмотрим на один из турниров большого шлема, например, Australian Open. В основной сетке WTA 128 человек. Играют на вылет. Такую сетку удобно представить в форме графа с помощью библиотеки networkx.В центре победительница турнира, справа и слева от нее она и другая участница финала и т.д.')
            T = nx.generators.balanced_tree(2, 7)
            nx.draw(T)
            fig, ax = plt.subplots()
            pos = nx.kamada_kawai_layout(T,)
            nx.draw(T,pos, with_labels=False)
            st.pyplot(fig)

            st.markdown('Кстати, идея сделать граф похожим на турнирную сетку, пришла ко мне, когда я работала с таблицей в SQL в Питоне с помощью sqlite3. Код прикрепляю ниже и в tennis data.py')
            st.markdown('Я как раз нашла, что в нашем турнире 128 участниц, что победительницей является Ashleigh Barty. К сожалению, подключить SQL к Streamlit у меня не получилось, но я выведу скачанный из SQL csv файл, где указаны все матчи именно Australian Open (изначально в таблицы были все турниры).')
            df11=pd.read_csv('aus2022.csv')
            st.write(df11.head())
            st.subheader('Вспомнив про теннис, сразу захотелось пойти поиграть. Где же в Москве есть корты?')
            st.markdown("Используя api ключ с сайта data.mos, я получила данные в формате geojson. Так как streamlit не смог открыть российский сайт, я преобразовала данные в дата фрейм, сохранила в формате csv.")

            l=pd.read_csv('courts.csv')
            gdf = gpd.GeoDataFrame(l, geometry=gpd.points_from_xy(l['lon'], l['lat']))
            showdata=st.expander('Посмотреть данные.')
            with showdata:
                        st.write(gdf)
            st.subheader('Сейчас покажем все теннисные корты Москвы на карте с помощью folium.')
            m = folium.Map([55.75364, 37.648280], zoom_start=10)
            for ind, row in gdf.iterrows():
                        folium.Marker([row.lon, row.lat],
                                      radius=12, fill_color='red').add_to(m)
            map=st_folium(m)

            st.subheader("Мне захотелось сделать красивую розовую визуализацию, поэтому давайте закрасим районы Москвы, в зависимости от того, сколько там теннисных кортов.")
            gdfnew = gpd.GeoDataFrame(l, geometry=gpd.points_from_xy(l['lat'], l['lon']))
            gdf2=pd.read_csv('moscow.csv')
            gdf2['poly']=gpd.GeoSeries.from_wkt(gdf2['poly']) 
            gdf1=gpd.GeoDataFrame(gdf2, geometry='poly')
            gdf1.crs = "EPSG:4326"
            gdften=gdf1.sjoin(gdfnew,predicate="intersects",how='inner') #обрабатываем дата фреймы, считаем знасения, меняем индекс и т.д (продвинутый пандас)
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

            #программа скачивания данных tennis_data.py

            # используя селениум, получаем данные про топ теннисисток из wta
            #driver = webdriver.Chrome('/Users/annagushchina/Downloads/chromedriver')
            #driver.get('https://www.wtatennis.com/stats')
            #firstname=driver.find_elements(by=By.CLASS_NAME, value='player-name__container')
            #matches=driver.find_elements(by=By.CSS_SELECTOR, value='td.stats-list__cell.stats-list__cell--matches.stats-list__cell--fixed-width')
            #aces=driver.find_elements(by=By.XPATH, value='//td[@data-stat="Aces"]')
            #dfs=driver.find_elements(by=By.XPATH, value='//td[@data-stat="Double_Faults"]')
            #fserves=driver.find_elements(by=By.XPATH, value='//td[@data-stat="first_serve_percent"]')
            #fsp=driver.find_elements(by=By.XPATH, value='//td[@data-stat="first_serve_won_percent"]')
            #ssp=driver.find_elements(by=By.XPATH, value='//td[@data-stat="second_serve_won_percent"]')
            #servicepoints=driver.find_elements(by=By.XPATH, value='//td[@data-stat="service_points_won_percent"]')
            #bp=driver.find_elements(by=By.XPATH, value='//td[@data-stat="breakpoint_saved_percent"]')
            #sg=driver.find_elements(by=By.XPATH, value='//td[@data-stat="service_games_won_percent"]')
            #names=[]
            #rat=[]
            #mat=[]
            #ace=[]
            #df=[]
            #fs=[]
            #fspoints=[]
            #sspoints=[]
            #servpoints=[]
            #bpsaved=[]
            #sgames=[]
            #for i in range (len(firstname)):
                        #a=firstname[i].text
                        #names.append(re.sub('\n', ' ', a)) #используя регулярные выражение, находим из кода страницы имя и фамилию теннисистки (без них найти сложнее)
                        #rat.append(i+1)
                        #mat.append(matches[i].text)
                        #ace.append(aces[i].text)
                        #df.append(dfs[i].text)
                        #fs.append(fserves[i].text)
                        #fspoints.append(fsp[i].text)
                        #sspoints.append(ssp[i].text)
                        #servpoints.append(servicepoints[i].text)
                        #bpsaved.append(bp[i].text)
                        #sgames.append(sg[i].text)
            # сейчас создаем из полученных данных дата фрейм и сохраняем его в csv формате, чтобы использовать для визуализации в streamlit
            #df=pd.DataFrame({'name':names,'rating':rat,'matches played':mat,'aces':ace,'double faults':df, 'first serve %':fs,'first serve points %':fspoints,'second serve points %':sspoints, 'service points won %':servpoints, 'breakpoints saved %':bpsaved,'service games won %':sgames})
            #df.to_csv('wta.csv', index=False)

            # получаем данные с сайта Москвы в json формате, используя api key.
            #response = requests.get('https://apidata.mos.ru/v1/datasets/2135/features?api_key=15a39b704af4f427f3b82578923edec8')
            #r=response.json()
            # создаем из полученных данных дата фрейм и сохраняем его в csv формате, чтобы использовать в streamlit.
            #lon=[]
            #lat=[]
            #name=[]
            #ad=[]
            #mail=[]
            #web=[]
            #phone=[]
            #for i in range (len(r['features'])):
                        #lon.append(r['features'][i]['geometry']['coordinates'][1])
                        #lat.append(r['features'][i]['geometry']['coordinates'][0])
                        #name.append(r['features'][i]['properties']['Attributes']['ObjectName_en'])
                        #ad.append(r['features'][i]['properties']['Attributes']['Address_en'])
                        #mail.append(r['features'][i]['properties']['Attributes']['Email_en'])
                        #web.append(r['features'][i]['properties']['Attributes']['WebSite_en'])
                        #phone.append(r['features'][i]['properties']['Attributes']['HelpPhone_en'])
            #dfcourts=pd.DataFrame({'name':name,'address':ad, 'email':mail, 'website':web, 'phone': phone, 'lat':lat, 'lon':lon})
            #dfcourts.to_csv('courts.csv', index=False)

            #сейчас используем SQL для обработки данных с турниров. Сначала загрузим данные в базу.
            #df10=pd.read_csv('wta_matches_2022.csv')
            #conn=sqlite3.connect("database.sqlite")
            #c=conn.cursor()
            #df10.to_sql("wta", conn) #сейчас наша таблица есть в базе данных
            #c.execute(
            #"""
            #SELECT match_num FROM wta
            #WHERE tourney_name='Australian Open'
            #""").fetchall().   #узнавли, что номера матчей Australian open с 100 по 226 в таблице, найдем победительницу
            #win=c.execute(
            #"""
            #SELECT winner_name FROM wta
            #WHERE tourney_name='Australian Open' and match_num='226'
            #""").fetchall() # нашли победительницу 'Ashleigh Barty'
            #num=c.execute(
            #"""
            #SELECT COUNT (DISTINCT loser_name) AS number FROM wta 
            #WHERE tourney_name='Australian Open'
            #""").fetchall() #мы нашли, что проигравших 127, значит участников 127+победительница=128. Будем строить граф с матчами.
            #df11=pd.read_sql("""
            #SELECT * FROM wta 
            #WHERE tourney_name='Australian Open'
            #""", conn)
            #df11.to_csv("aus2022.csv") #нашли все данные про нужный нам турнир и сохранили в csv
            
            '''
            Таким образом, в проекте использовались следующие технологии:
            * обработка данных с помощью pandas;
            * веп-скреппинг, используя selenium;
            * работа с API (JSON) с использованием api key;
            * визуализация данных (цветная карта, графики по статистическим показателям wta);
            * numpy (арифметические операции с массивами, построение матрицу коэффициентов корреляции);
            * streamlit;
            * SQL (создание и использование базы данных с теннисными турнирами);
            * регулярные выражения для облегчения поиска в коде страницы;
            * работа с геоданными (geopandas, folium);
            * построение графа с помощью networkx;
            * машинное обучение (модель линейной регрессии);
            * больше 120 строк.
            '''
