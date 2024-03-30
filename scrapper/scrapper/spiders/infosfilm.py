import scrapy
import json
from scrapper.items import InfosMovies

class InfosfilmSpider(scrapy.Spider):
    name = "infosfilm"
    allowed_domains = ["www.allocine.fr"]
    start_urls = ["https://www.allocine.fr/film/fichefilm_gen_cfilm=278742.html"]
    

    def start_requests(self):
            # Charge le fichier JSON contenant les IDs des films
            with open('test.json', 'r') as file:
                data = json.load(file)
            
            # Génére les URLs et initier les requêtes Scrapy
            for item in data:
                url = f"https://www.allocine.fr/film/fichefilm_gen_cfilm={item['href']}.html"
                yield scrapy.Request(url=url, callback=self.parse, meta={'film_title': item['title']})

    def parse(self, response):
        image_url = response.xpath('//img[@class="thumbnail-img"]/@src').get()
        title = response.xpath('//div[@class="titlebar-title titlebar-title-xl"]/text()').get()
        timing = response.xpath('//div[@class="meta-body-item meta-body-info"]/span[@class="spacer"]/following-sibling::text()[1]').get()
        director = response.xpath('//div[@class="meta-body-item meta-body-direction meta-body-oneline"]/span[@class="light"]/following-sibling::a/text()').get()




        
        if timing:
            timing = timing.replace('\n', '').strip()

        if image_url and title:
            yield InfosMovies(image_urls=[image_url], title=title, timing=timing, director=director)
        else:
            self.logger.error(f"Missing data in {response.url}")
