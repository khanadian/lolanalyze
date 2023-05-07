from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import csv
import time

def open_url(url, d, writer):
    d.get(url)

    #now we need to load the div by scrolling down
    body = d.find_element(By.CSS_SELECTOR, 'body')
    for i in range(4):
        body.send_keys(Keys.PAGE_DOWN)

    classname = "PanelSet_data__nAnQM"
    WebDriverWait(d, 10).until(EC.presence_of_element_located(\
        (By.CLASS_NAME, classname)))

    champName = d.title.split("Build")[0][:-1]
    itemData = d.find_element(By.CLASS_NAME, classname)
    itemSets = itemData.find_elements(By.CLASS_NAME, "CellSet_wrapper__bbETk")
    for itemSet in itemSets:
        pr = itemSet.find_element(By.CLASS_NAME,"CellSet_pick__6I6VT").text
        if(float(pr) >= 1):
            items = itemSet.find_elements(By.CLASS_NAME,"Item_item48br__H8miU")
            i = []
            for item in items:
                i = i+[item.get_attribute("alt")]
            if "Mejai's Soulstealer" not in i: #TODO add a boots check
                numbers = itemSet.text.split("\n")
                if isinstance(numbers[2],str): #games has a comma
                    numbers[2] = int(numbers[2].replace(',',''))
                
                writer.writerow([champName, numbers[0], numbers[1], numbers[2],\
                                 i[0], i[1], i[2]])

driver = webdriver.Chrome()
driver.set_window_position(2000, 100)
url = "https://lolalytics.com/lol/tierlist/"

file = open("TierlistPatch13.9.csv", 'w', newline='')
file2 = open("builds13.9.csv", 'w', newline='')
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

#we need to make a seperate list where the links are saved
hrefs2 = []
for href in hrefs:
    hrefs2 = hrefs2 + [href.get_attribute("href")]

writer = csv.writer(file2)
writer.writerow(['Champion Name', 'Win rate', 'Pick Rate', 'Games', 'Item 1', 'Item 2', 'Item 3'])
for href in hrefs2:
    open_url(href, driver, writer)

#TODO sort the CSV once written (or before writing)


driver.close()
driver.quit()
file.close()
file2.close()