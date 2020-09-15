from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import requests
from lxml import html
from pprint import pprint

from pymongo import MongoClient


headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"}
mongo_client = MongoClient("127.0.0.1", 27017)
data_base = mongo_client["news_database"]


def save_news(db, doc, collection):
    if db[collection].count_documents({"title": doc["title"],
                                       "date_of_pub": doc["date_of_pub"]}) == 0:
        db[collection].insert_one(doc)
        return 1
    else:
        return 0


"""============PARSE FROM LENTA======================"""


lenta_link = "https://lenta.ru"
response = requests.get(lenta_link, headers=headers)
dom = html.fromstring(response.text)

news = dom.xpath('//div[@class="span4"]/div[contains(@class, "item")]//a/time/..')

counter = 0
for item in news:
    document = dict()
    document["title"] = item.xpath('text()')[0].replace("\xa0", " ")
    document["link"] = lenta_link + item.xpath('@href')[0]
    day_of_pub = item.xpath('time/@title')[0].split(" ")[0]
    month_of_pub = item.xpath('time/@title')[0].split(" ")[1]
    year_of_pub = item.xpath('time/@title')[0].split(" ")[2]
    replace_month = {"января": 1, "февраля": 2, "марта": 3,
                     "апреля": 4, "мая": 5, "июня": 6,
                     "июля": 7, "августа": 8, "сентября": 9,
                     "октября": 10, "ноября": 11, "декабря": 12}
    document["date_of_pub"] = date(int(year_of_pub), replace_month[month_of_pub], int(day_of_pub)).isoformat()
    document["source"] = "lenta.ru"
    counter += save_news(data_base, document, "lenta")
print(f"Have parsed '{counter}' news from lenta.ru")


"""============PARSE FROM MAIL======================"""

mail_link = "https://news.mail.ru"
response = requests.get(mail_link, headers=headers)
dom = html.fromstring(response.text)

news_1 = dom.xpath('//div[contains(@class, "daynews__item")]')
counter = 0
for new in news_1:
    document = dict()
    document["title"] = new.xpath('.//span[contains(@class, "photo__title photo__title_new")]/text()')[0]
    inner_link = new.xpath('./a/@href')[0]
    if "https://" in inner_link:
        document["link"] = inner_link
    else:
        document["link"] = mail_link + inner_link
    interim_response = requests.get(document["link"], headers=headers)
    interim_dom = html.fromstring(interim_response.text)
    document["source"] = interim_dom.xpath('//a[@class="link color_gray breadcrumbs__link"]/'
                                           'span[@class="link__text"]/text()')[0]
    publication = interim_dom.xpath('//span[@class="breadcrumbs__item"]'
                                    '//span[@class="note__text breadcrumbs__text js-ago"]/@datetime')[0].split("T")[0]
    year_of_pub = publication.split("-")[0]
    month_of_pub = publication.split("-")[1]
    day_of_pub = publication.split("-")[2]
    document["date_of_pub"] = date(int(year_of_pub),
                                   int(month_of_pub),
                                   int(day_of_pub)).isoformat()
    counter += save_news(data_base, document, "mail")
print(f"Have parsed '{counter}' news from mail.ru")


"""============PARSE FROM YANDEX======================"""

yandex_link = "https://yandex.ru/news"
response = requests.get(yandex_link, headers=headers)
dom = html.fromstring(response.text)

news = dom.xpath('//a[@class="news-card__link"]')

counter = 0
for new in news:
    document = dict()
    document["title"] = new.xpath('h2[@class="news-card__title"]/text()')[0]
    document["link"] = new.xpath('@href')
    document["source"] = new.xpath('../../..//div[@class="mg-card-footer__left"]'
                                   '/div[@class="mg-card-source news-card__source"]'
                                   '/span[@class="mg-card-source__source"]/a/text()')[0]
    date_of_pub = new.xpath('../../..//div[@class="mg-card-footer__left"]'
                            '/div[@class="mg-card-source news-card__source"]'
                            '/span[@class="mg-card-source__time"]/text()')[0]
    if "вчера" in date_of_pub:
        document["date_of_pub"] = (datetime.now().date() + relativedelta(days=-1)).isoformat()
    else:
        document["date_of_pub"] = (datetime.now().date()).isoformat()
    counter += save_news(data_base, document, "yandex")
print(f"Have parsed '{counter}' news from yandex.ru")

