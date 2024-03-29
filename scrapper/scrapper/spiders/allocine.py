import scrapy
import re
from scrapper.items import scrapperItem

class AllocineSpider(scrapy.Spider):
    name = "allocine"
    allowed_domains = ["www.allocine.fr"]
    start_urls = ["https://www.allocine.fr/films/decennie-2020/"]

    def parse(self, response):
        bloc_films = response.xpath('//div[@class="gd-col-middle"]//ul/li')
        
        for film in bloc_films:
            title = film.xpath('.//h2[@class="meta-title"]/a/text()').extract_first()
            href = film.xpath('.//h2[@class="meta-title"]/a/@href').extract_first()
            
            if href:
                match = re.search(r'cfilm=(\d+).html', href)
                if match:
                    href = match.group(1)

            if title and href:
                film_item = scrapperItem()
                film_item['title'] = title
                film_item['href'] = href
                yield film_item  
        
        # Gestion de la pagination
        current_page = response.meta.get('current_page', 1)
        next_page = current_page + 1

        if next_page <= 975:
            next_page_url = f"https://www.allocine.fr/films/decennie-2020/?page={next_page}"
            yield scrapy.Request(next_page_url, callback=self.parse, meta={'current_page': next_page})
