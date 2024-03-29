import scrapy
import json

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
                yield scrapy.Request(url=url, callback=self.parse_box_office, meta={'film_title': item['title']})

    def parse_box_office(self, response):
         pass
