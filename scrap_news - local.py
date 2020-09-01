from scrapy.crawler import CrawlerProcess
from datetime import datetime

import scrapy
import json
import tempfile

TEMPORARY_FILE = tempfile.NamedTemporaryFile(delete=False, mode='w+t')
    
class NasdaqSpider(scrapy.Spider):
    def __init__(self, symbol="ibm"):
        self.start_urls = [f'https://www.nasdaq.com/market-activity/stocks/{symbol}/news-headlines']

    name = 'nasdaqspider'
    cycles = 0
    ID = 1
    
    # Elements
    news = ".quote-news-headlines__item a::attr(href)"
    follow = ".pagination__next"

    title = ".article-header__headline span::text"
    body = ".body__content p::text"
    date = ".timestamp__date::text"
    
    def parse(self, response):
        for new in response.css(self.news):
            yield response.follow(new, self.scrap)
                
        self.cycles += 1
            
        if self.cycles <= 10:
            yield response.follow(response.css(follow)[0], self.parse)

    def scrap(self, response):
        title_text = response.css(self.title).extract_first()
        body_text = response.css(self.body).extract()
        date_text = response.css(self.date).extract_first()
            
        TEMPORARY_FILE.writelines(f"{self.ID}|{title_text}|{body_text}|{date_text}\n")
        self.ID += 1
            
now = datetime.now()
TEMPORARY_FILE.writelines("id|title|text|date\n")
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})
process.crawl(NasdaqSpider, "ibm")
process.start()
TEMPORARY_FILE.seek(0)

with open("./datasets/scrap.csv", "w") as file:
    file.writelines(TEMPORARY_FILE.readlines())

TEMPORARY_FILE.close()