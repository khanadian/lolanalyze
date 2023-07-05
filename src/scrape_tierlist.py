from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime
import math

start_time = time.time()
print(datetime.now())
URL_P = "https://lolalytics.com/lol/tierlist/"
URL_M = "https://lolalytics.com/lol/tierlist/?tier=master_plus"
URL_Supp = "https://lolalytics.com/lol/tierlist/?lane=support&tier=master_plus"


#starting parameters

mode = "2 items"
url = URL_M
patch = '13.13'

rank = ''
if url == URL_P:
    rank = "_Platinum+"
elif url == URL_M:
    rank = "_Master+"
elif url == URL_Supp:
    rank = "_Supp_M+"

rank_array = ['Item 1', 'Item 2']
if mode=="2 items":
    dataID = "5"
elif mode=="3 items":
    dataID = "6"
    rank_array.append('Item 3')
elif mode=="4 items":
    dataID = "7"
    rank_array.append('Item 3')
    rank_array.append('Item 4')
elif mode=="support":
    print("support") #TODO add "support"

itemID = { #items missing an alt value
  "4644": "Crown of the Shattered Queen",
  "4645": "Shadowflame",
  "3161": "Spear of Shojin",
  "3119": "Winter's Approach",
  "8001": "Anathema's Chains",
  "6696": "Axiom Arc",
  "8020": "Abyssal Mask",
  "6620": "Echoes of Helia"
}

def open_url(url, d, writer):
    d.get(url)
    classname = "PanelSet_data__nAnQM"
    buttonHeading = "ItemSetSelector_setheadings__9mUvH"

    WebDriverWait(d, 20).until(EC.presence_of_element_located(\
        (By.CLASS_NAME, "ItemSets_placeholder__QROSH")))
    #now we need to load the div by scrolling down
    body = d.find_element(By.CSS_SELECTOR, 'body')
    for i in range(4):
        body.send_keys(Keys.PAGE_DOWN)

    #grab champ name and role
    WebDriverWait(d, 10).until(EC.presence_of_element_located(\
        (By.CLASS_NAME, classname)))
    champName = d.title.split("Build")[0][:-1]
    role = d.find_element(By.CLASS_NAME, "NavChamp_wrapper__bc-VX").text
    if role == "support" and rank != "_Supp_M+":
        return

    #select dataset
    buttons = d.find_elements(By.CLASS_NAME, buttonHeading)[0].find_elements(\
        By.CSS_SELECTOR, "div")
    for div in buttons:
        if div.get_attribute("data-id") == dataID:
            button = div
    button.click()
    
    #populate csv
    itemData = d.find_element(By.CLASS_NAME, classname)
    itemSets = itemData.find_elements(By.CLASS_NAME, "CellSet_wrapper__bbETk")
    for itemSet in itemSets:
        pr = itemSet.find_element(By.CLASS_NAME,"CellSet_pick__6I6VT").text
        if(float(pr) >= 0):
            items = itemSet.find_elements(By.CLASS_NAME,"Item_item48br__H8miU")
            i = []
            for item in items:
                itemName = item.get_attribute("alt")
                if len(itemName) < 1:
                    itemName = itemID.get(item.get_attribute("data-id"))
                    if itemName is None:
                        print(item.get_attribute("data-id"))
                        itemName = ""
                elif itemName == "Abyssal Mask" and item.get_attribute("data-id") == "3001": #for some reason this is misnamed
                    itemName = "Evenshroud"
                elif itemName == "Sanguine Blade" and item.get_attribute("data-id") == "3181":
                    itemName = "Hullbreaker"
                i = i+[itemName]
            if "Mejai's Soulstealer" not in i:
                numbers = itemSet.text.split("\n")
                if isinstance(numbers[2],str): #games has a comma
                    numbers[2] = int(numbers[2].replace(',',''))
                weighted_wr = (float(numbers[0])*float(numbers[2])/(float(numbers[2])+5))-50 #discourage winrates below 50%
                weighted_pr = math.log(float(numbers[1])+1, 2)
                weighted_games = math.log(float(numbers[2])+1, 2)
                weight = round(weighted_wr * weighted_pr * weighted_games*100)
                toWrite = [champName, role]+i+numbers+[str(weight)]
                writer.writerow(toWrite)


driver = webdriver.Chrome()
driver.set_window_position(2000, 100)


    
file = open("Tierlist"+patch+rank+".csv", 'w', newline='')
file2 = open("builds"+patch+rank+".csv", 'w', newline='')
writer = csv.writer(file)

#write header rows
writer.writerow(['Champion Name', 'Win rate', 'Pick Rate'])


driver.get(url)
WebDriverWait(driver, 10).until(EC.presence_of_element_located(\
    (By.CLASS_NAME, "ListRow_name__b5btO")))

#List of attributes that are getting scraped.
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

    writer.writerow([name, wr, pr])

classname = columns[1]['class'][0]
hrefs = driver.find_elements(By.CSS_SELECTOR, "."+classname+" a")

#we need to make a seperate list where the links are saved
hrefs2 = []
for href in hrefs:
    hrefs2 = hrefs2 + [href.get_attribute("href")]

writer = csv.writer(file2)

writer.writerow(['Name', 'Role'] + rank_array + ['Win rate', 'Pick Rate', 'Games', 'Weight','last run:', datetime.now()]) 
for href in hrefs2:
    open_url(href, driver, writer)

driver.close()
driver.quit()
file.close()
file2.close()

print("--- %s seconds ---" % round(time.time() - start_time))

#TODO sort the CSV once written (or before writing)
#TODO combine this sheet with one which considers the same build, but extrapolated
#TODO standard requests module
#TODO timestamp and other info on sheet
