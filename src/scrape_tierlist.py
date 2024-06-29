from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from tkinter import *
import pandas as pd
import time
from datetime import datetime
import math
import concurrent.futures
import xlsxwriter as xls


BASE_URL = "https://www.lolalytics.com/lol/tierlist/?"

#lane options
L_ALL = ['top', 'jungle', 'middle', 'bottom', 'support']

#tiers
TIER = ['tier=emerald_plus',"tier=d2_plus","tier=grandmaster_plus"]

#items missing an alt value
itemID = { 
  #"4644": "crown of the Shattered Queen",
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
  "6698": "profane hydra",
  #S14 S2
  "2503": "blackfire torch",
  "3032": "yun tal wildarrows",
  "2501": "overlords bloodmail"
}

def main(lanes, tiers, patch, numItems):
    
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.set_window_position(2000, 100)
    driver.maximize_window()
##
##    all_data = []
##    for lane in lanes:
##        url = BASE_URL+"lane="+lane+"&"+tier
##        all_data = all_data + extract_data_role(url, driver)

    all_data = {}
    for t in tiers:
        
        tiered_data = []
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        futures = []
        for lane in lanes:
            url = BASE_URL+"lane="+lane+"&"+t
            futures.append(executor.submit(extract_data_role, url, numItems, driver))
        for future in concurrent.futures.as_completed(futures):
            tiered_data = future.result() + tiered_data 
        all_data[t] = tiered_data
    write_to_file(patch, all_data, numItems)
    driver.close()
    driver.quit()

def write_to_file(patch, all_data, numItems):

    workbook  = xls.Workbook("builds"+patch+".xlsx")
    
    rank_array = ['Item 1', 'Item 2', 'Item 3', 'Item 4']
    for tier in all_data:
        dict = {}
        if tier == TIER[1]:
            rank = "_D2+"
        elif tier == TIER[2]:
            rank = "_GM+"
        else:
            rank = "_Emerald+"
        for champ in all_data[tier]:
            for builds in champ:
                num = builds[0]
                for build in builds[1:]:
                    if num in dict:
                        dict[num].append(build)
                    else:
                        dict[num] = [build]
        for num in dict:
            name = patch+rank+"_"+num+"items"
            worksheet = workbook.add_worksheet(name)
            n = int(num)
            arr1 = ['Name', 'Role']
            arr2 = rank_array[0:n]
            arr3 = ['Win rate', 'Pick Rate', 'Games', 'Weight','last run:', datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' EST'] 
            arr1 = arr1 + arr2 + arr3
            worksheet.write_row(0,0,arr1)
            counter = 1
            for build in dict[num]:
                build[n+2] = float(build[n+2])
                build[n+3] = float(build[n+3])
                build[n+4] = float(build[n+4])
                build[n+5] = float(build[n+5])
                worksheet.write_row(counter, 0, build)
                counter+=1
    workbook.close()

def extract_data_role(url, numItems, driver):
    
##    driver = webdriver.Chrome(ChromeDriverManager().install())
##    driver.set_window_position(2000, 100)
##    driver.maximize_window()
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(\
    (By.XPATH, "/html/body/main/div[6]/div[3]")))
    
    body = driver.find_element(By.CSS_SELECTOR, 'body')
    for i in range(6):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)
    
    hrefs = []
    role_data =[]
    #2 loops because otherwise the hrefs are lost after going into the first link
    for element in driver.find_elements(By.XPATH, "//a[@href]")[13:-1]:
        build_link = element.get_attribute("href")
        if build_link not in hrefs and "/build/" in build_link:
            hrefs.append(build_link)
        
    for href in hrefs:
        try:
            champ_data = extract_data_champ(href, driver, numItems)
            role_data.append(champ_data)
        except Exception as error:
            print(href)
            print(error)
            
##    driver.close()
##    driver.quit()
    return role_data

    
def extract_data_champ(href, d, numItems):
    first_item = "/html/body/main/div[6]/div[1]/div[16]/div[2]/div"
    
    d.get(href)
    WebDriverWait(d, 20).until(EC.presence_of_element_located(\
        (By.CLASS_NAME, "_wrapper_hthxe_1")))
    #now we need to load the div by scrolling down
    body = d.find_element(By.CSS_SELECTOR, 'body')
    for i in range(3):
        body.send_keys(Keys.PAGE_DOWN)
    #grab champ name and role
    role = d.title.split("for ")[1].split()[0]
    champName = d.title.split(role + " ")[1]
    
    #select dataset
    all_data = []
    for num in numItems:
        champ_data = []
        if num == 1:
            WebDriverWait(d, 10).until(EC.presence_of_element_located(\
        (By.XPATH, first_item)))
            itemData = d.find_element(By.XPATH, first_item)
            items = itemData.find_elements(By.CSS_SELECTOR,"div")
            i = []
            for item in items:
                try:
                    i_n = item.find_element(By.CSS_SELECTOR, "a span img")
                except:
                    continue
                itemName = i_n.get_attribute("alt")
                if len(itemName) < 1:
                    if i_n.get_attribute("data-id") is None:
                        print("no data id?")
                        continue
                    itemName = itemID.get(i_n.get_attribute("data-id")[2:])
                    if itemName is None:
                        print(i_n.get_attribute("data-id"))
                        itemName = ""
                if itemName == "Mejai's Soulstealer":
                    break
                elif itemName == "Abyssal Mask" and i_n.get_attribute("data-id") == "3001": #for some reason this is misnamed
                    itemName = "ABABBABABAB"
                elif itemName == "Sanguine Blade" and i_n.get_attribute("data-id") == "3181":
                    itemName = "hullbreaker"
                elif itemName == "Luden's Tempest" and i_n.get_attribute("data-id") == "6655":
                    itemName = "ludens companion"
                elif itemName == "Liandry's Anguish" and i_n.get_attribute("data-id") == "6653":
                    itemName = "liandrys torment"
                elif itemName == "Turbo Chemtank" and i_n.get_attribute("data-id") == "6664":
                    itemName = "hollow radiance"
                numbers = item.text.split("\n")
                if len(numbers) == 4:
                    del numbers[3]
                if isinstance(numbers[2],str): # might contain comma, must be removed
                    numbers[2] = int(numbers[2].replace(',',''))
                weighted_wr = (float(numbers[0])*float(numbers[2])/(float(numbers[2])+5))-50 #discourage winrates below 50%
                weighted_pr = math.log(float(numbers[1])+1, 2)
                weighted_games = math.log(float(numbers[2])+1, 2)
                weight = round(weighted_wr * weighted_pr * weighted_games*100)
                champ_data.append([champName, role]+[itemName]+numbers+[str(weight)])
        else:
            while(1):
                try:
                    button = d.find_element(By.XPATH, "//div[@data-type='a_"+str(num)+"']")
                    button.click()
                    break
                except:
                    print(champName)
                    d.execute_script('window.scrollBy(0, -100)')
                    time.sleep(1)
            #time.sleep(2) #TODO find a proper fix
            #grab data
            found = False
            while not found:
                try:
                    itemData = d.find_elements(By.XPATH, "//div[@class='cursor-grab overflow-x-scroll']")[1]
                    itemData = itemData.find_element(By.CSS_SELECTOR, "div")
                    found = True
                except:
                    print(champName)
                    time.sleep(1)
            try:
                itemSets = itemData.find_elements(By.CSS_SELECTOR, "div")
            except:
                print("error finding itemsets")
            for itemSet in itemSets:
                while(1):
                    try:
                        items = itemSet.find_elements(By.CSS_SELECTOR, "span img")
                        break
                    except:
                        print("error getting item")
                        time.sleep(1)
                if len(items) == 0:
                    continue
                i = []
                
                for item in items:
                    itemName = item.get_attribute("alt")
                    try:
                        dataID = item.get_attribute("data-id")
                        if len(itemName) < 1:
                            if dataID is None:
                                print("no data id?")
                                continue
                            itemName = itemID.get(item.get_attribute("data-id")[2:])
                            if itemName is None:
                                print(champName)
                                print(item.get_attribute("data-id"))
                                itemName = ""
                        elif itemName == "Abyssal Mask" and item.get_attribute("data-id") == "3001": #for some reason this is misnamed
                            itemName = "ABABABBABAB"
                        elif itemName == "Sanguine Blade" and item.get_attribute("data-id") == "3181":
                            itemName = "hullbreaker"
                        elif itemName == "Luden's Tempest" and item.get_attribute("data-id") == "6655":
                            itemName = "ludens companion"
                        elif itemName == "Liandry's Anguish" and item.get_attribute("data-id") == "6653":
                            itemName = "liandrys torment"
                    except:
                        print("no dataID?")
                        if len(itemName) < 1:
                            itemName = "unknown"
                    #print(itemName)
                    i = i+[itemName]
                numbers = itemSet.text.split("\n")
                if isinstance(numbers[2],str): # might contain comma, must be removed
                    numbers[2] = int(numbers[2].replace(',',''))
                weighted_wr = (float(numbers[0])*float(numbers[2])/(float(numbers[2])+5))-50 #discourage winrates below 50%
                weighted_pr = math.log(float(numbers[1])+1, 2)
                weighted_games = math.log(float(numbers[2])+1, 2)
                weight = round(weighted_wr * weighted_pr * weighted_games*100)
                champ_data.append([champName, role]+i+numbers+[str(weight)])
        all_data.append([str(num)]+champ_data)
    print(champName)
    return all_data

def select_all():
    lb.select_set(0, END)
def clear_all():
    lb.selection_clear(0, END)
def select_all2():
    lb2.select_set(0, END)
def clear_all2():
    lb2.selection_clear(0, END)
def select_all3():
    lb3.select_set(0, END)
def clear_all3():
    lb3.selection_clear(0, END)

def man(url):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.set_window_position(2000, 100)
    driver.maximize_window()
    driver.get(url)

    WebDriverWait(driver, 20).until(EC.presence_of_element_located(\
        (By.XPATH, "//a[@href]")))

    dupe = False
    for element in driver.find_elements(By.XPATH, "//a[@href]")[13:-1]:
        if not dupe:
            print(element.get_attribute("href"))
        dupe = not dupe
        
    driver.close()
    driver.quit()
    
if __name__ == "__main__":
    start_time = time.time()
    print(datetime.now())
    lanes = []
    tiers = []
    numItems = []

    #popup window
    popup = Tk()
    t = []
    
    Label(popup, text="Lane").pack()
    lb = Listbox(popup, selectmode=MULTIPLE, height=len(L_ALL),exportselection = False)
    for i in range(len(L_ALL)):
        lb.insert(i, L_ALL[i])
    lb.pack()
    Button(popup, text='select all', command=select_all).pack()
    Button(popup, text='clear', command=clear_all).pack()
    

    Label(popup, text="Tier").pack()
    
    lb2 = Listbox(popup, selectmode=MULTIPLE, height=len(TIER),exportselection = False)
    for i in range(len(TIER)):
        lb2.insert(i, TIER[i][5:])
    lb2.pack()
    Button(popup, text='select all', command=select_all2).pack()
    Button(popup, text='clear', command=clear_all2).pack()
    
    Label(popup, text="Patch").pack()
    ent = Entry(popup)
    ent.insert(0, "14.13")
    ent.pack()

    Label(popup, text="# Items").pack()
    lb3 = Listbox(popup, selectmode=MULTIPLE, height=3,exportselection = False)
    for i in range(3):
        lb3.insert(END, i+1)
    lb3.pack()
    Button(popup, text='select all', command=select_all3).pack()
    Button(popup, text='clear', command=clear_all3).pack()
    #this is an improper way of allowing the entry text without saving it
    ok = Button(popup, text='OK', command = popup.quit)
    ok.pack()
    popup.mainloop()
    
    for i in lb.curselection():
        lanes.append(lb.get(i))

    for i in lb2.curselection():
        tiers.append("tier="+lb2.get(i))

    for i in lb3.curselection():
        numItems.append(lb3.get(i))


    patch = "_"+ent.get()
    BASE_URL = BASE_URL + "patch=" + ent.get()+"&"
    popup.destroy()
    print(lanes)
    print(patch)
    print(tiers)
    print(numItems)
    main(lanes, tiers, patch, numItems)
    
    print("--- %s seconds ---" % (time.time() - start_time))
    
