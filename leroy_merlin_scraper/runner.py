from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from leroy_merlin_scraper.spiders.lm import LmSpider
from leroy_merlin_scraper import settings


request_item = input("Enter search item for request: ")
crawler_settings = Settings()
crawler_settings.setmodule(settings)
process = CrawlerProcess(settings=crawler_settings)
process.crawl(LmSpider, params=[request_item])
process.start()

