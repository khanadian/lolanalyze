from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time

driver = webdriver.Chrome()
url = "https://lolalytics.com/lol/tierlist/"

file = open("TierlistPatch13.8.csv", 'w', newline='')
writer = csv.writer(file)

#write header rows
writer.writerow(['Champion Name', 'Win rate', 'Pick Rate'])

driver.get(url)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "ListRow_name__b5btO")))

#List of attributes that are getting scrapped.
name=[]
winRate=[]
pickRate=[]

content = driver.page_source
soup = BeautifulSoup(content, features="html.parser")

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

classname = columns[1]['class'][0]
hrefs = driver.find_elements(By.CSS_SELECTOR, "."+classname+" a")
for href in hrefs:
    print(href.get_attribute("href"))
    
driver.close()
file.close()

