# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst

class LeroyMerlinScraperItem(scrapy.Item):
    # define the fields for your item here like:
    name_of_features = scrapy.Field(input_processor=MapCompose(lambda x: x.replace(" ", "_"),
                                                               lambda x: x.replace(",", "-"),
                                                               lambda x: x.replace(".", "-")))
    item_photos = scrapy.Field()
    item_features = scrapy.Field(input_processor=MapCompose(lambda x: x.strip()))
    item_url = scrapy.Field(output_processor=TakeFirst())
    item_name = scrapy.Field(output_processor=TakeFirst())
    item_price = scrapy.Field(input_processor=MapCompose(lambda x: x.replace(" ", ""), float),
                              output_processor=TakeFirst())
    item_unit_price = scrapy.Field(input_processor=MapCompose(lambda x: x.replace(".", "")),
                                   output_processor=TakeFirst())
    item_unit_price_2 = scrapy.Field(output_processor=TakeFirst())
    item_price_2 = scrapy.Field(input_processor=MapCompose(lambda x: x.replace(" ", ""), float),
                                output_processor=TakeFirst())

