# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.spiders import Spider

class BookparserPipeline:
    def __init__(self):
        mongo_client = MongoClient("localhost", 27017)
        self.data_base = mongo_client["book_database"]

    def process_item(self, item, spider: Spider):
        book = dict(item)
        book["book_total_price"] = self.parce_price(book["book_total_price"])
        book["book_action_price"] = self.parce_price(book["book_action_price"])
        book["book_total_price"], book["book_action_price"] = self.total_price(book["book_total_price"],
                                                                               book["book_action_price"])
        if self.data_base[spider.name].count_documents({"book_title": book["book_title"],
                                                        "book_author": book["book_author"],
                                                        "book_total_price": book["book_total_price"],
                                                        "book_action_price": book["book_action_price"]
                                                        }) == 0:
            self.data_base[spider.name].insert_one(book)

    def parce_price(self, price: str):
        if price:
            price = price.split(" ")
            if len(price) == 3:
                price = price[0] + price[1]
            price = price[0]
            try:
                price = float(price)
            except ValueError:
                pass
        return price

    def total_price(self, total, action):
        if (total is None) and (action is not None):
            return action, None
        return total, action


