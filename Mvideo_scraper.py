import time
import json
from datetime import datetime
from pprint import pprint

from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

mongo_client = MongoClient("127.0.0.1", 27017)
db = mongo_client["mvideo_hit_of_sales"]


def save_good(data_base, collec, doc):
    if data_base[collec].count_documents({"_id": doc["_id"]}) == 0:
        data_base[collec].insert_one(doc)
        return 1
    else:
        return 0


browser_options = Options()
browser_options.add_argument("start-maximized")

browser = webdriver.Chrome("./chromedriver.exe", options=browser_options)
browser.get("https://www.mvideo.ru/")

wait_time = WebDriverWait(browser, 10).\
    until(EC.presence_of_element_located((By.XPATH, '//li[@class="gallery-list-item height-ready"]')))

elements = browser.find_elements_by_xpath('//div[@class="section"]')
for i, el in enumerate(elements):
    try:
        locator = el.find_element_by_xpath(f'(//div[@class="h2 u-mb-0 u-ml-xs-20 u-font-normal"])[{i}]')
        if locator.text == "Хиты продаж":
            locator = el
            break
        else:
            continue
    except:
        continue

next_button = locator.find_element_by_class_name("next-btn")
for i in range(3):
    next_button.click()
    time.sleep(3)


goods = locator.find_elements_by_class_name("gallery-list-item")
counter = 0
for good in goods:
    document = {}
    good_info = good.find_element_by_tag_name("a").get_attribute("data-product-info")
    good_info = json.loads(good_info)
    link = good.find_element_by_tag_name("a").get_attribute("href")
    document["_id"] = int(good_info["productId"])
    document["name"] = good_info["productName"]
    document["category"] = good_info["productCategoryName"]
    document["producer"] = good_info["productVendorName"]
    document["price"] = float(good_info["productPriceLocal"])
    document["link"] = good.find_element_by_tag_name("a").get_attribute("href")
    collection = f"{datetime.now().day}.{datetime.now().month:0>2d}.{datetime.now().year}"
    counter += save_good(db, collection, document)

print(f"Have saved '{counter}' goods in database")

cursor = db[f"{datetime.now().day}.{datetime.now().month:0>2d}.{datetime.now().year}"].find({})

for i in cursor:
    pprint(i)

