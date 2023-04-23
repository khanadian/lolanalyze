from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv

driver = webdriver.Chrome()
url = "https://lolalytics.com/lol/tierlist/"

file = open("TierlistPatch13.8.csv", 'w', newline='')
writer = csv.writer(file)

#write header rows
writer.writerow(['Champion Name', 'Win rate', 'Pick Rate'])

driver.get(url)
print("start")
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "TierList_list__j33gd")))


#List of attributes that are getting scrapped.
name=[]
winRate=[]
pickRate=[]

content = driver.page_source
soup = BeautifulSoup(content)

for row in soup.find('div', 'TierList_list__j33gd').find_all('div', recursive=False):
    columns = row.find_all('div')
    a = columns[0].text #icon?
    name = columns[1].text
    tier = columns[2].text
    lane_percent = columns[3].text #lane percentage
    d = columns[4].text  #lane icon?
    wr = columns[6].text #wr
    wrDelta = columns[7].text #wr delta
    pr = columns[8].text #pick rate
    br = columns[9].text #ban rate
    games = columns[10].text #games

    #print(f'{e} - {f} - {g} - {h}')
    writer.writerow([name, wr, pr])
    
driver.close()
file.close()
print("done")