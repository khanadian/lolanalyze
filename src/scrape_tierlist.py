from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import csv
import time

def open_url(url, d):
    print(url)
    d.get(url)

    #now we need to load the div by scrolling down
    body = d.find_element(By.CSS_SELECTOR, 'body')
    for i in range(4):
        body.send_keys(Keys.PAGE_DOWN)

    
    classname = "ItemSetSelector_panel__l6y-U"
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(\
        (By.CLASS_NAME, classname)))
    print("found")

    
    
    first_items = driver.find_element(By.CLASS_NAME, classname)
    print(classname)

    divs = first_items.find_elements(By.CSS_SELECTOR, "div")
    for div in divs:
        print(div.get_attribute("class"))
        print("div found")

driver = webdriver.Chrome()
driver.set_window_position(2000, 100)
url = "https://lolalytics.com/lol/tierlist/"

file = open("TierlistPatch13.8.csv", 'w', newline='')
writer = csv.writer(file)

#write header rows
writer.writerow(['Champion Name', 'Win rate', 'Pick Rate'])

driver.get(url)
WebDriverWait(driver, 10).until(EC.presence_of_element_located(\
    (By.CLASS_NAME, "ListRow_name__b5btO")))

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
    open_url(href.get_attribute("href"), driver)
    break
    
driver.close()
driver.quit()
file.close()


