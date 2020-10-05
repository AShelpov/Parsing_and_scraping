# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LeroyMerlinScraperItem(scrapy.Item):
    # define the fields for your item here like:
    name_of_features = scrapy.Field()
    item_photos = scrapy.Field()
    item_features = scrapy.Field()
    item_url = scrapy.Field()
    item_name = scrapy.Field()
    item_price = scrapy.Field()
    item_unit_price = scrapy.Field()
    item_unit_price_2 = scrapy.Field()
    item_price_2 = scrapy.Field()

