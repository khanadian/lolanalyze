from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv

driver = webdriver.Chrome()
driver.set_window_position(2000, 100)
url = "https://lolalytics.com/lol/tierlist/"




file = open("TierlistPatch13.8.csv", 'w', newline='')
writer = csv.writer(file)

#write header rows
writer.writerow(['Champion Name', 'Win rate', 'Pick Rate'])

driver.get(url)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "TierList_list__j33gd")))

#List of attributes that are getting scrapped.
name=[]
winRate=[]
pickRate=[]

content = driver.page_source
soup = BeautifulSoup(content, features="html.parser")

cn = ""
r = soup.find('div', 'TierList_list__j33gd').find_all('div', recursive=False)
for row in r:
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
    cn = columns[1]['class'][0]
    writer.writerow([name, wr, pr])

h = self.get_hrefs(cn)
print(h)

driver.close()
file.close()

def get_hrefs(cn):
    hrefs = driver.find_elements(By.CSS_SELECTOR, "."+cn+" a")
    for href in hrefs:
        h = h + href.get_attribute("href") #href of each champ
    return h    

