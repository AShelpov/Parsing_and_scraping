import scrapy
from scrapy.http import HtmlResponse
from leroy_merlin_scraper.items import LeroyMerlinScraperItem
from scrapy.loader import ItemLoader


class LmSpider(scrapy.Spider):
    name = 'lm'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, params):
        self.start_urls = [f'https://leroymerlin.ru/search/?q={params[0]}']

    def parse(self, response: HtmlResponse):
        item_links = response.xpath("//product-card/uc-plp-item-new/@href")
        for link in item_links:
            yield response.follow(link, callback=self.parse_item)
        next_page = response.xpath('//div[@class="next-paginator-button-wrapper"]/a/@href').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_item(self, item_response: HtmlResponse):
        loader = ItemLoader(item=LeroyMerlinScraperItem(), response=item_response)


        loader.add_xpath("name_of_features", '//dl[@class="def-list"]/div/dt/text()')
        loader.add_xpath("item_photos", '//img[@slot="thumbs"]/@src')
        loader.add_xpath("item_features", '//dl[@class="def-list"]/div/dd/text()')
        loader.add_xpath("item_name", '//h1/text()')
        loader.add_value("item_url", item_response.url)
        loader.add_xpath("item_price", '//uc-pdp-price-view//meta[@itemprop="price"]/@content')
        loader.add_xpath("item_unit_price", '//uc-pdp-price-view//span[@slot="unit"]/text()')
        loader.add_xpath("item_unit_price_2", '//uc-pdp-price-view[@slot="second-price"]//span[@slot="unit"]/text()')
        loader.add_xpath("item_price_2", '//uc-pdp-price-view[@slot="second-price"]//span[@slot="price"]/text()')
        yield loader.load_item()

