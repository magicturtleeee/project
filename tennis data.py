import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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
    names.append(a.replace('\n', ' '))
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
print (names)
print (rat)
print(mat)
print(ace)
print(df)
print(fs)
print(fspoints)
print(sspoints)
print(servpoints)
print(bpsaved)
print(sgames)
df=pd.DataFrame({'name':names,'rating':rat,'matches played':mat,'aces':ace,'double faults':df, 'first serve %':fs,'first serve points %':fspoints,'second serve points %':sspoints, 'service points won %':servpoints, 'breakpoints saved %':bpsaved,'service games won %':sgames})
df.to_csv(r'\Users\annagushchina\Downloads\pythonProject1\wta.csv', index=False)