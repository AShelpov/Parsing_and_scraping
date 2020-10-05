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
        name_of_features = item_response.xpath('//dl[@class="def-list"]/div/dt/text()').extract()
        item_photos = item_response.xpath('//img[@slot="thumbs"]/@src').extract()
        item_features = item_response.xpath('//dl[@class="def-list"]/div/dd/text()').extract()
        item_name = item_response.xpath('//h1/text()').extract_first()
        item_url = item_response.url
        item_price = item_response.xpath('//uc-pdp-price-view//meta[@itemprop="price"]/@content').extract_first()
        item_unit_price = item_response.xpath('//uc-pdp-price-view//span[@slot="unit"]/text()').extract_first()
        item_unit_price_2 = \
            item_response.xpath('//uc-pdp-price-view[@slot="second-price"]//span[@slot="unit"]/text()').extract_first()
        item_price_2 = \
            item_response.xpath('//uc-pdp-price-view[@slot="second-price"]//span[@slot="price"]/text()').extract_first()
        return LeroyMerlinScraperItem(name_of_features=name_of_features,
                                      item_photos=item_photos,
                                      item_features=item_features,
                                      item_url=item_url,
                                      item_name=item_name,
                                      item_price=item_price,
                                      item_unit_price=item_unit_price,
                                      item_unit_price_2=item_unit_price_2,
                                      item_price_2=item_price_2)
