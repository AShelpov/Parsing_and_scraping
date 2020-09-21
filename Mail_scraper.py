from pprint import pprint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient

from logs_for_enter import logs_for_enter_mail

browser_options = Options()
browser_options.add_argument("start-maximized")
browser = webdriver.Chrome("./chromedriver.exe", options=browser_options)
browser.get("https://mail.ru/")

mongo_client = MongoClient("127.0.0.1", 27017)
db = mongo_client["mail_scraper"]


def save_document(data_base, coll, doc):
    if data_base[coll].count_documents({"sender": doc["sender"],
                                        "subject": doc["subject"],
                                        "send_time": doc["send_time"]}) == 0:
        data_base[coll].insert_one(doc)
        return 1
    else:
        return 0


login_input = browser.find_element_by_xpath('//input[@id="mailbox:login-input"]')
login_input.send_keys(logs_for_enter_mail()[0])

domain_input = browser.find_element_by_xpath('//select[@id="mailbox:domain"]')
select_domain = Select(domain_input)
select_domain.select_by_visible_text("@mail.ru")

remember_check = browser.find_element_by_id("mailbox:saveauth")
remember_check.click()

pass_input = browser.find_element_by_xpath('//input[@value="Ввести пароль"]')
pass_input.click()

pass_input = browser.find_element_by_id("mailbox:password-input")
pass_input.send_keys(logs_for_enter_mail()[1])
pass_input.send_keys(Keys.ENTER)


wait_time = WebDriverWait(browser, 10).\
    until(EC.presence_of_element_located((By.CLASS_NAME, "dataset__items")))
messages = browser.find_elements_by_xpath('//a[contains(@class, "llc")]')

counter = 0
while True:
    for message in messages:
        document = {}
        document["sender"] = message.find_element_by_xpath('.//span[@class="ll-crpt"]').get_attribute("title")
        document["subject"] = message.find_element_by_xpath('.//span[@class="ll-sj__normal"]').text
        document["short_text"] = message.find_element_by_xpath('.//span[@class="llc__snippet"]').text
        document["send_time"] = message.find_element_by_xpath('//div[contains(@class, "llc__item_date")]').\
                                            get_attribute("title")
        link = message.get_attribute("href")
        browser.execute_script(f"window.open('{link}')")
        default_window = browser.window_handles[0]
        message_window = browser.window_handles[1]
        browser.switch_to.window(message_window)
        wait_time_message = WebDriverWait(browser, 10).\
            until(EC.presence_of_element_located((By.XPATH, '//div[@class="html-expander"]')))
        document["message_body"] = browser.find_element_by_xpath('//div[@class="html-expander"]').text
        browser.close()
        browser.switch_to.window(default_window)
        counter += save_document(db, "mail.ru", document)

    scroll = ActionChains(browser)
    scroll.move_to_element(messages[-1])
    scroll.perform()
    updated_messages = browser.find_elements_by_xpath('//a[contains(@class, "llc")]')
    if updated_messages[-1] == messages[-1]:
        break
    else:
        messages = updated_messages

print(f"Have saved '{counter}' messages in database")

cursor = db["mail.ru"].find({})
for i in cursor:
    pprint(i)
    print("="*100)
