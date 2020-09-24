# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookparserItem(scrapy.Item):
    # define the fields for your item here like:
    book_link = scrapy.Field()
    book_title = scrapy.Field()
    book_author = scrapy.Field()
    book_total_price = scrapy.Field()
    book_action_price = scrapy.Field()
    book_rating = scrapy.Field()

    pass
