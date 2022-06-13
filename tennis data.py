import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
import re
import sqlite3

# используя селениум, получаем данные про топ теннисисток из wta
driver = webdriver.Chrome('/Users/annagushchina/Downloads/chromedriver')
driver.get('https://www.wtatennis.com/stats')
firstname=driver.find_elements(by=By.CLASS_NAME, value='player-name__container')
matches=driver.find_elements(by=By.CSS_SELECTOR, value='td.stats-list__cell.stats-list__cell--matches.stats-list__cell--fixed-width')
aces=driver.find_elements(by=By.XPATH, value='//td[@data-stat="Aces"]')
dfs=driver.find_elements(by=By.XPATH, value='//td[@data-stat="Double_Faults"]')
fserves=driver.find_elements(by=By.XPATH, value='//td[@data-stat="first_serve_percent"]')
fsp=driver.find_elements(by=By.XPATH, value='//td[@data-stat="first_serve_won_percent"]')
ssp=driver.find_elements(by=By.XPATH, value='//td[@data-stat="second_serve_won_percent"]')
servicepoints=driver.find_elements(by=By.XPATH, value='//td[@data-stat="service_points_won_percent"]')
bp=driver.find_elements(by=By.XPATH, value='//td[@data-stat="breakpoint_saved_percent"]')
sg=driver.find_elements(by=By.XPATH, value='//td[@data-stat="service_games_won_percent"]')
names=[]
rat=[]
mat=[]
ace=[]
df=[]
fs=[]
fspoints=[]
sspoints=[]
servpoints=[]
bpsaved=[]
sgames=[]
for i in range (len(firstname)):
    a=firstname[i].text
    names.append(re.sub('\n', ' ', a)) #используя регулярные выражение, находим из кода страницы имя и фамилию теннисистки (без них найти сложнее)
    rat.append(i+1)
    mat.append(matches[i].text)
    ace.append(aces[i].text)
    df.append(dfs[i].text)
    fs.append(fserves[i].text)
    fspoints.append(fsp[i].text)
    sspoints.append(ssp[i].text)
    servpoints.append(servicepoints[i].text)
    bpsaved.append(bp[i].text)
    sgames.append(sg[i].text)
# сейчас создаем из полученных данных дата фрейм и сохраняем его в csv формате, чтобы использовать для визуализации в streamlit
df=pd.DataFrame({'name':names,'rating':rat,'matches played':mat,'aces':ace,'double faults':df, 'first serve %':fs,'first serve points %':fspoints,'second serve points %':sspoints, 'service points won %':servpoints, 'breakpoints saved %':bpsaved,'service games won %':sgames})
df.to_csv('wta.csv', index=False)

# получаем данные с сайта Москвы в json формате, используя api key.
response = requests.get('https://apidata.mos.ru/v1/datasets/2135/features?api_key=15a39b704af4f427f3b82578923edec8')
r=response.json()
# создаем из полученных данных дата фрейм и сохраняем его в csv формате, чтобы использовать в streamlit.
lon=[]
lat=[]
name=[]
ad=[]
mail=[]
web=[]
phone=[]
for i in range (len(r['features'])):
    lon.append(r['features'][i]['geometry']['coordinates'][1])
    lat.append(r['features'][i]['geometry']['coordinates'][0])
    name.append(r['features'][i]['properties']['Attributes']['ObjectName_en'])
    ad.append(r['features'][i]['properties']['Attributes']['Address_en'])
    mail.append(r['features'][i]['properties']['Attributes']['Email_en'])
    web.append(r['features'][i]['properties']['Attributes']['WebSite_en'])
    phone.append(r['features'][i]['properties']['Attributes']['HelpPhone_en'])
dfcourts=pd.DataFrame({'name':name,'address':ad, 'email':mail, 'website':web, 'phone': phone, 'lat':lat, 'lon':lon})
dfcourts.to_csv('courts.csv', index=False)

#сейчас используем SQL для обработки данных с турниров. Сначала загрузим данные в базу.
df10=pd.read_csv('wta_matches_2022.csv')
conn=sqlite3.connect("database.sqlite")
c=conn.cursor()
df10.to_sql("wta", conn) #сейчас наша таблица есть в базе данных
c.execute(
"""
SELECT match_num FROM wta
WHERE tourney_name='Australian Open'
""").fetchall().   #узнавли, что номера матчей Australian open с 100 по 226 в таблице, найдем победительницу
win=c.execute(
"""
SELECT winner_name FROM wta
WHERE tourney_name='Australian Open' and match_num='226'
""").fetchall() # нашли победительницу 'Ashleigh Barty'
num=c.execute(
"""
SELECT COUNT (DISTINCT loser_name) AS number FROM wta 
WHERE tourney_name='Australian Open'
""").fetchall() #мы нашли, что проигравших 127, значит участников 127+победительница=128. Будем строить граф с матчами.
df11=pd.read_sql("""
SELECT * FROM wta 
WHERE tourney_name='Australian Open'
""", conn)
df11.to_csv("aus2022.csv") #нашли все данные про нужный нам турнир и сохранили в csv
