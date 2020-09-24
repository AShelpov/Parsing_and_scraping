import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/search/?q=донцова']

    def parse(self, response: HtmlResponse):
        book_links = response.xpath('//div[@class="book__image-block"]/a/@href').extract()
        for link in book_links:
            yield response.follow(link, callback=self.book_parse)
        next_page = response.xpath('//div[@class="catalog-pagination__list"]//a[contains(@class, '
                                   '"catalog-pagination__item")]/@href').extract()[-1]
        if next_page:
            yield response.follow(next_page, callback=self.parse)


    def book_parse(self, book_response: HtmlResponse):
        book_link = book_response.url
        book_title = book_response.xpath('//h1/text()').extract_first()
        book_author = book_response.xpath('//a[@class="item-tab__chars-link"]/text()').extract()[0]
        book_total_price = book_response.xpath('//div[@class="item-actions__price-old"]/text()').extract_first()
        book_action_price = book_response.xpath('//div[@class="item-actions__price"]/b/text()').extract_first()
        book_rating = book_response.xpath('//span[@class="rating__rate-value"]/text()').extract_first()
        return BookparserItem(book_link=book_link, book_title=book_title, book_author=book_author,
                              book_total_price=book_total_price, book_action_price=book_action_price,
                              book_rating=book_rating)




