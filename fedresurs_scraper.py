import time
from pprint import pprint

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from pymongo import MongoClient

begin_date = "18.09.2020"
end_date = "18.09.2020"

mongo_client = MongoClient("127.0.0.1", 27017)
db = mongo_client["fedresurs_scraper"]


def save_document(data_base, coll, doc):
    if data_base[coll].count_documents({"_id": doc["_id"]}) == 0:
        data_base[coll].insert_one(doc)
        return 1
    else:
        return 0


browser_options = Options()
browser_options.add_argument("start-maximized")
browser = webdriver.Chrome("./chromedriver.exe", options=browser_options)
browser.get("https://bankrot.fedresurs.ru/Messages.aspx")


message = browser.find_element_by_id("ctl00_cphBody_mdsMessageType_tbSelectedText").click()
time.sleep(2)
frame = browser.find_elements_by_tag_name("iframe")[0]
browser.switch_to.frame(frame)
browser.find_element_by_xpath("//div[@class='rtTop']/span[@class='rtIn']").click()
time.sleep(1)
browser.switch_to.default_content()


select = Select(browser.find_element_by_id("ctl00_cphBody_ddlCourtDecisionType"))
select.select_by_value("7")


browser.find_element_by_id("ctl00_cphBody_cldrBeginDate_tbSelectedDate").clear()
browser.find_element_by_id("ctl00_cphBody_cldrBeginDate_tbSelectedDate").send_keys("18.09.2020")
browser.find_element_by_id("ctl00_cphBody_cldrEndDate_tbSelectedDate").clear()
browser.find_element_by_id("ctl00_cphBody_cldrEndDate_tbSelectedDate").send_keys("18.09.2020")
browser.find_element_by_id("ctl00_cphBody_ibMessagesSearch").click()
time.sleep(2)


messages = browser.find_elements_by_xpath('//table[@class="bank"]//a[contains(@onclick, "Сообщение")]')

counter = 0
for message in messages:
    message.click()
    time.sleep(1)

    default_window = browser.window_handles[0]
    message_window = browser.window_handles[1]

    browser.switch_to.window(message_window)
    elements = browser.find_elements_by_xpath('//table[@class="headInfo"]//td[not(contains(@class, "primary"))]')
    document = {}
    document["_id"] = int(elements[1].text)
    document["message"] = elements[0].text
    document["mess_num"] = elements[1].text
    document["mess_date"] = elements[2].text
    document["debtor"] = elements[3].text
    document["deb_adr"] = elements[4].text
    document["deb_ind_num"] = elements[5].text
    document["deb_tax_num"] = elements[6].text
    document["bancr_case"] = elements[7].text
    document["bancr_manager"] = elements[8].text
    document["bancr_manager_adr"] = elements[9].text
    document["bancr_manager_association"] = elements[10].text
    document["bm_association_adr"] = elements[11].text

    browser.close()
    browser.switch_to.window(default_window)
    counter += save_document(db, "buncrupcy_cases", document)

print(f"Have saved '{counter}' messages in database")

cursor = db["buncrupcy_cases"].find({})

for i in cursor:
    pprint(i)






