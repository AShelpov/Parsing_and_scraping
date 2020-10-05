# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os as os
import re as re
import os as os
import shutil as shutil
import scrapy
from itemadapter import ItemAdapter
from scrapy.spiders import Spider
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
from leroy_merlin_scraper.runner import request_item


class LeroyMerlinScraperPipeline:

    def __init__(self):
        client = MongoClient("localhost", 27017)
        self.data_base = client["LeroyMerlinDB"]


    def process_item(self, item, spider: Spider):
        good = dict()
        good["item_url"] = item["item_url"]
        good["good_features"] = self.features_parse(item)
        good["name"] = item["item_name"]
        good["price"] = {item["item_unit_price"]: item["item_price"],
                         item["item_unit_price_2"]: item["item_price_2"]}
        if self.data_base[request_item].count_documents({"item_url": good["item_url"]}) == 0:
            self.data_base[request_item].insert_one(good)


    def features_parse(self, item):
        if len(item["name_of_features"]) == len(item["item_features"]):
            names = item["name_of_features"]
            features = item["item_features"]
            total_features = {feat[0]: feat[1] for feat in zip(names, features)}
            return total_features


class LeroyMerlinPhotosPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        if item["item_photos"]:
            for img in item["item_photos"]:
                try:
                    img = re.sub(r"w_\d+,h_\d+,", "w_1200,h_1200,", img)
                except Exception as e:
                    print(e)
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            path_new = os.path.join(os.getcwd(), "item_photos", item["item_name"])
            os.mkdir(path_new)
            for photo in results:
                if photo[0]:
                    path_old = os.path.join(os.getcwd(), "item_photos", photo[1]["path"])
                    shutil.move(path_old, path_new)
        return item


