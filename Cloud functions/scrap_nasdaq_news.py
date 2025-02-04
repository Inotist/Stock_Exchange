# Función sin implementar debido a que al final no he podido extraer datos suficientes para entrenar a un modelo que utilice estos datos.

from google.cloud import storage
from scrapy.crawler import CrawlerProcess
from datetime import datetime

import scrapy
import tempfile

TEMPORARY_FILE = tempfile.NamedTemporaryFile(delete=False, mode='w+t')

def upload_file_to_bucket(bucket_name, blob_file, destination_file_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_file_name)
    blob.upload_from_filename(blob_file.name, content_type='text/csv')
    
class NasdaqSpider(scrapy.Spider):
    def __init__(self, symbol="ibm"):
        self.start_urls = [f'https://www.nasdaq.com/market-activity/stocks/{symbol}/news-headlines']

    name = 'nasdaqspider'
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

    def scrap(self, response):
        title_text = response.css(self.title).extract_first()
        body_text = response.css(self.body).extract()
        date_text = response.css(self.date).extract_first()
            
        TEMPORARY_FILE.writelines(f"{self.ID}|{title_text}|{body_text}|{date_text}\n")
        self.ID += 1
            
def activate(request):
    request_json = request.get_json()
    if request.args and "symbol" in request.args:
        symbol = request.args.get("symbol")
    elif request_json and "symbol" in request_json:
        symbol = request_json["symbol"]
    else:
        return f"Symbol hasn't been specified"

    now = datetime.now()
    BUCKET_NAME = 'sep_files'
    DESTINATION_FILE_NAME = f"datasets/news/{symbol}-{now.strftime('%Y-%m-%d')}.csv"
    TEMPORARY_FILE.writelines("id|title|text|date\n")
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(NasdaqSpider, symbol)
    process.start()
    upload_file_to_bucket(BUCKET_NAME, TEMPORARY_FILE, DESTINATION_FILE_NAME)
    TEMPORARY_FILE.close()
    
    return "Sinvergüenza!"