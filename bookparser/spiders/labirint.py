import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/донцова/?stype=0']

    def parse(self, response: HtmlResponse):
        book_links = response.xpath('//a[@class="cover"]/@href').extract()
        for link in book_links:
            yield response.follow(link, callback=self.parse_book)

        next_page = response.xpath('//div[@class="pagination-next"]/a/@href').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, book_response: HtmlResponse):
        book_link = book_response.url
        book_title = book_response.xpath("//h1/text()").extract_first()
        book_author = book_response.xpath('//div[@class="authors" and contains(text(), "Автор: ")]/a/text()').extract()
        book_total_price = book_response.xpath('//div[@class="buying-priceold-val"]/span/text()').extract_first()
        book_action_price = book_response.xpath('//span[@class="buying-pricenew-val-number"]/text()').extract_first()
        book_rating = book_response.xpath('//div[@id="rate"]/text()').extract_first()
        return BookparserItem(book_link=book_link, book_title=book_title, book_author=book_author,
                              book_total_price=book_total_price, book_action_price=book_action_price,
                              book_rating=book_rating)
