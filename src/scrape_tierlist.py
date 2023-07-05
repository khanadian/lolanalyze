from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import csv
import time
from datetime import datetime
import math

BASE_URL = "https://lolalytics.com/lol/tierlist/?"

#lane options
L_ALL = ['top', 'jungle', 'middle', 'bottom', 'support']
L_MAJOR = ['top', 'jungle', 'middle', 'bottom']
L_SUPPORT = ['support']

#tiers
T_P_PLUS = ''
T_M_PLUS = "tier=master_plus"
T_CH = "tier=challenger"

#items missing an alt value
itemID = { 
  "4644": "Crown of the Shattered Queen",
  "4645": "Shadowflame",
  "3161": "Spear of Shojin",
  "3119": "Winter's Approach",
  "8001": "Anathema's Chains",
  "6696": "Axiom Arc",
  "8020": "Abyssal Mask",
  "6620": "Echoes of Helia"
}


def main(lanes, tier, patch):
    driver = webdriver.Chrome()
    driver.set_window_position(2000, 100)
    driver.maximize_window()

    all_data = []
    for lane in lanes:
        url = BASE_URL+"lane="+lane+"&"+tier
        all_data = all_data + extract_data_role(url, lane, driver)

    driver.close()
    driver.quit()

    if tier == T_M_PLUS:
        rank = "_Master+"
    else:
        rank = "_Plat+"
    
    file = open("builds"+patch+rank+".csv", 'w', newline='')
    writer = csv.writer(file)
    
    rank_array = ['Item 1', 'Item 2']
    if mode=="3 items":
        rank_array.append('Item 3')
    elif mode=="4 items":
        rank_array.append('Item 3')
        rank_array.append('Item 4')
    
    writer.writerow(['Name', 'Role'] + rank_array + ['Win rate', 'Pick Rate', 'Games', 'Weight','last run:', datetime.now()])
    for champ in all_data:
        for build in champ:
            writer.writerow(build)

    file.close()


def extract_data_role(url, lane, driver):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(\
    (By.CLASS_NAME, "ListRow_name__b5btO")))
    
    hrefs = []
    role_data =[]
    #2 loops because otherwise the hrefs are lost after going into the first link
    for href in driver.find_elements(By.CSS_SELECTOR, ".ListRow_name__b5btO a"):
        hrefs = hrefs + [href.get_attribute("href")]
        
    for href in hrefs:
        champ_data = extract_data_champ(href, driver)
        role_data = role_data + [champ_data]
    return role_data
    
def extract_data_champ(href, d):
    d.get(href)
    classname = "PanelSet_data__nAnQM"
    buttonHeading = "ItemSetSelector_setheadings__9mUvH"
    WebDriverWait(d, 20).until(EC.presence_of_element_located(\
        (By.CLASS_NAME, "ItemSets_placeholder__QROSH")))
    #now we need to load the div by scrolling down
    body = d.find_element(By.CSS_SELECTOR, 'body')
    for i in range(3):
        body.send_keys(Keys.PAGE_DOWN)

    #grab champ name and role
    WebDriverWait(d, 10).until(EC.presence_of_element_located(\
        (By.CLASS_NAME, classname)))
    champName = d.title.split("Build")[0][:-1]
    role = d.find_element(By.CLASS_NAME, "NavChamp_wrapper__bc-VX").text

    #select dataset
    dataID = str(int(mode[0])+3)
    buttons = d.find_elements(By.CLASS_NAME, buttonHeading)[0].find_elements(\
        By.CSS_SELECTOR, "div")
    for div in buttons:
        if div.get_attribute("data-id") == dataID:
            button = div
    button.click()

    champ_data = []
    #grab data
    itemData = d.find_element(By.CLASS_NAME, classname)
    itemSets = itemData.find_elements(By.CLASS_NAME, "CellSet_wrapper__bbETk")
    for itemSet in itemSets:
        pr = itemSet.find_element(By.CLASS_NAME,"CellSet_pick__6I6VT").text
        if(float(pr) >= 0):#may be needed in future
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
            numbers = itemSet.text.split("\n")
            if isinstance(numbers[2],str): # might contain comma, must be removed
                numbers[2] = int(numbers[2].replace(',',''))
            weighted_wr = (float(numbers[0])*float(numbers[2])/(float(numbers[2])+5))-50 #discourage winrates below 50%
            weighted_pr = math.log(float(numbers[1])+1, 2)
            weighted_games = math.log(float(numbers[2])+1, 2)
            weight = round(weighted_wr * weighted_pr * weighted_games*100)
            champ_data = champ_data +[[champName, role]+i+numbers+[str(weight)]]
        else:
            return champ_data
    return champ_data

if __name__ == "__main__":
    start_time = time.time()
    print(datetime.now())
    global mode
    lanes = L_MAJOR
    tier = T_P_PLUS
    mode = "2 items"
    patch = "_13.13"
    

    main(lanes, tier, patch)
    print("--- %s seconds ---" % (time.time() - start_time))
    
