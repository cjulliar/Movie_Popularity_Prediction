import scrapy


class ImdbIdSpider(scrapy.Spider):
    name = "imdb_id"
    allowed_domains = ["www.imdb.com"]
    start_urls = ["https://www.imdb.com/search/title/?title_type=feature"]

    def parse(self, response):
        pass
