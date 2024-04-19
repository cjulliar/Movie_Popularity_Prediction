import scrapy
import json, re
from scrapper.items import JpboxItem

class InfosfilmSpider(scrapy.Spider):
    name = "jpbox_3"
    allowed_domains = ["www.jpbox-office.com"]
    start_urls = ["https://www.jpbox-office.com/v9_demarrage.php?view=2"]

    def parse(self, response):
        films_links = response.xpath('//div[@id="content"]/table//h3//a')
        for film_link in films_links:
            films_url = film_link.xpath('.//a/@href').get()
            yield response.follow(films_url, callback=self.parse_films)
        # for page_number in range(2,49):
        #    next_page_url = f'https://scrapeme.live/shop/page/%7Bpage_number%7D'
        #    yield response.follow(next_page_url, callback=self.parse)
    

    def parse_films(self, response):
        films = response.xpath('//table[@class="tablesmall tablesmall5"]/tbody/tr')
        for film in films:
            item = JpboxItem()
            item['title'] = film.xpath('.//td[@class="col_poster_titre"]/h3/a/text()').get()
            item['genre'] = film.xpath('.//td[@class="col_poster_titre"]/a/text()').get()
            item['first_week_entries'] = film.xpath('.//td[@class="col_poster_contenu"]/text()').get()
            response.xpath("//table[contains(@class, 'tablesmall') and contains(@class, 'tablesmall5')]/tr[2]/td[contains(@class, 'col_poster_contenu_majeur')]/text()").getall()
            yield item
    