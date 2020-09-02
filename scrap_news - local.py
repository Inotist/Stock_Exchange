from scrapy.crawler import CrawlerProcess
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep

import scrapy
import tempfile

TEMPORARY_FILE = tempfile.NamedTemporaryFile(delete=False, mode='w+t')
    
class NasdaqSpider(scrapy.Spider):
    name = 'nasdaqspider'
    ID = 1

    def __init__(self, symbol="ibm"):
        self.symbol = symbol
        self.driver = webdriver.Firefox()
    
    # Elements
    news = ".quote-news-headlines__item a::attr(href)"
    follow = ".pagination__next"

    title = ".article-header__headline span::text"
    body = ".body__content p::text"
    date = ".timestamp__date::text"
    
    def parse(self, response):
        self.driver.get(f"https://www.nasdaq.com/market-activity/stocks/{self.symbol}/news-headlines")

        for i in range(len(10)):
            sleep(1)
            news = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.news))
            )
            for new in news:
                yield Request("https://www.nasdaq.com"+new.text, self.scrap)
                
            follow = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.follow))
            )
            follow.click()

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

with open("./datasets/scrap2.csv", "w") as file:
    file.writelines(TEMPORARY_FILE.readlines())

TEMPORARY_FILE.close()