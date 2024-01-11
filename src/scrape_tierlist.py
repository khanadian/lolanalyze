from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from tkinter import *
import csv
import time
from datetime import datetime
import math


BASE_URL = "https://lolalytics.com/lol/tierlist/?"

#lane options
L_ALL = ['top', 'jungle', 'middle', 'bottom', 'support']

#tiers
TIER = ['',"tier=master_plus","tier=challenger"]

first_item = "/html/body/div/div[6]/div[10]/div[13]/div[2]"

#items missing an alt value
itemID = { 
  "4644": "crown of the Shattered Queen",
  "4645": "shadowflame",
  "3161": "spear of Shojin",
  "3119": "winter's Approach",
  "8001": "anathema's Chains",
  "6696": "axiom Arc",
  "8020": "abyssal Mask",
  "6620": "echoes of Helia",
  #S14 items
  #"": "",
  "6610": "sundered sky",
  "3073": "experimental hexplate",
  "3302": "terminus",
  "6699": "voltaic cyclosword",
  "4646": "stormsurge",
  "3137": "cryptbloom",
  "3118": "malignance",
  "6701": "opportunity",
  "6697": "hubris",
  "3002": "trailblazer",
  "3876": "solstice sleigh",
  "3869": "celestial opposition",
  "2502": "unending despair",
  "3877": "bloodsong",
  "2504": "kaenic rookern",
  "3870": "dream maker",
  "3871": "zazzaks realmspike",
  "6621": "dawncore",
  "6698": "profane hydra"
}

def main(lanes, tier, patch):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.set_window_position(2000, 100)
    driver.maximize_window()

    all_data = []
    for lane in lanes:
        url = BASE_URL+"lane="+lane+"&"+tier
        all_data = all_data + extract_data_role(url, driver)

    driver.close()
    driver.quit()

    write_to_file(patch, tier, all_data)

def write_to_file(patch, tier, all_data):
    if tier == TIER[1]:
        rank = "_Master+"
    elif tier == TIER[2]:
        rank = "_Chall"
    else:
        rank = "_Emerald+"

    file = open("builds"+patch+rank+"_"+str(number_items)+"_items.csv", 'w', newline='')
    writer = csv.writer(file)
    
    rank_array = ['Item 1']
    if number_items >1:
        rank_array.append('Item 2')
    if number_items >2:
        rank_array.append('Item 3')
    if number_items >3:
        rank_array.append('Item 4')
    
    writer.writerow(['Name', 'Role'] + rank_array + ['Win rate', 'Pick Rate', 'Games', 'Weight','last run:', datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' EST'])
    for champ in all_data:
        for build in champ:
            writer.writerow(build)

    file.close()

def extract_data_role(url, driver):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(\
    (By.CLASS_NAME, "ListRow_name__b5btO")))
    
    hrefs = []
    role_data =[]
    #2 loops because otherwise the hrefs are lost after going into the first link
    for href in driver.find_elements(By.CSS_SELECTOR, ".ListRow_name__b5btO a"):
        hrefs = hrefs + [href.get_attribute("href")]

        
    for href in hrefs:
        if number_items == 1:
            champ_data = extract_data_one_item(href, driver)
        else:
            champ_data = extract_data_champ(href, driver)
        role_data = role_data + [champ_data]
    return role_data

def extract_data_one_item(href, d):
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
    
    champ_data = []
    #grab data
    itemData = d.find_elements(By.XPATH, first_item)
    items = itemData[0].find_elements(By.CLASS_NAME,"Cell_cell__383UV")
    i = []
    for item in items:
        i_n = item.find_element(By.CLASS_NAME, "Item_item48br__H8miU")
        itemName = i_n.get_attribute("alt")
        if len(itemName) < 1:
            itemName = itemID.get(i_n.get_attribute("data-id"))
            if itemName is None:
                print(i_n.get_attribute("data-id"))
                itemName = ""
        elif itemName == "Abyssal Mask" and i_n.get_attribute("data-id") == "3001": #for some reason this is misnamed
            itemName = "evenshroud"
        elif itemName == "Sanguine Blade" and i_n.get_attribute("data-id") == "3181":
            itemName = "hullbreaker"
        elif itemName == "Luden's Tempest" and i_n.get_attribute("data-id") == "6655":
            itemName = "ludens companion"
        elif itemName == "Liandry's Anguish" and i_n.get_attribute("data-id") == "6653":
            itemName = "liandrys torment"

        numbers = item.text.split("\n")
        del numbers[3]
        if isinstance(numbers[2],str): # might contain comma, must be removed
            numbers[2] = int(numbers[2].replace(',',''))
        weighted_wr = (float(numbers[0])*float(numbers[2])/(float(numbers[2])+5))-50 #discourage winrates below 50%
        weighted_pr = math.log(float(numbers[1])+1, 2)
        weighted_games = math.log(float(numbers[2])+1, 2)
        weight = round(weighted_wr * weighted_pr * weighted_games*100)
        champ_data = champ_data +[[champName, role]+[itemName]+numbers+[str(weight)]]

    return champ_data
    
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
    dataID = str(number_items+3)
    buttons = d.find_elements(By.CLASS_NAME, buttonHeading)[0].find_elements(\
        By.CSS_SELECTOR, "div")
    for div in buttons:
        if div.get_attribute("data-id") == dataID:
            button = div
    while(1):
        try:
            button.click()
            break
        except:
            print(champName)
            time.sleep(1)

    champ_data = []
    #grab data
    found = False
    while not found:
        try:
            itemData = d.find_element(By.CLASS_NAME, classname)
            found = True
        except NoSuchElementException:
            print(champName)
            time.sleep(1)
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
                        print(champName)
                        print(item.get_attribute("data-id"))
                        itemName = ""
                elif itemName == "Abyssal Mask" and item.get_attribute("data-id") == "3001": #for some reason this is misnamed
                    itemName = "evenshroud"
                elif itemName == "Sanguine Blade" and item.get_attribute("data-id") == "3181":
                    itemName = "hullbreaker"
                elif itemName == "Luden's Tempest" and item.get_attribute("data-id") == "6655":
                    itemName = "ludens companion"
                elif itemName == "Liandry's Anguish" and item.get_attribute("data-id") == "6653":
                    itemName = "liandrys torment"
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
    global number_items
    lanes = []

    #popup window
    popup = Tk()
    varList = []
    t = []
    Label(popup, text="Lane").pack()
    for index in range(0,len(L_ALL)):
        varList = varList+[IntVar()]
        t = t + [Checkbutton(popup, text=L_ALL[index], variable=varList[index], onvalue=1, offvalue=0)]
        t[index].pack()

    varList = varList + [IntVar()]
    Label(popup, text="tier").pack()
    Radiobutton(text="Emerald+", variable = varList[5], value = 0).pack()
    Radiobutton(text="Master+", variable = varList[5], value = 1).pack()
    Radiobutton(text="Challenger", variable = varList[5], value = 2).pack()
    
    Label(popup, text="patch").pack()
    ent = Entry(popup)
    ent.insert(0, "14.1")
    ent.pack()

    varList = varList + [IntVar()] 
    Label(popup, text="Items").pack()
    Radiobutton(text="2", variable = varList[6], value = 0).pack()
    Radiobutton(text="3", variable = varList[6], value = 1).pack()
    #this is an improper way of allowing the entry text without saving it
    ok = Button(popup, text='OK', command = popup.quit)
    ok.pack()
    popup.mainloop()

    for index in range(0, 5):
        if varList[index].get() > 0:
            lanes = lanes + [L_ALL[index]]


    patch = "_"+ent.get()
    tier = TIER[varList[5].get()]
    BASE_URL = BASE_URL + "patch=" + ent.get()+"&"
    number_items = varList[6].get() + 2 #done this way to ensure default value is 2
    popup.destroy()
    print(lanes)
    print(tier)
    print(patch)
    print(number_items)
    main(lanes, tier, patch)
    print("--- %s seconds ---" % (time.time() - start_time))
    
