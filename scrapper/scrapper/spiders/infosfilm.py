import scrapy
import json, re
from scrapper.items import InfosMovies

class InfosfilmSpider(scrapy.Spider):
    name = "infosfilm"
    allowed_domains = ["www.allocine.fr"]
    start_urls = ["https://www.allocine.fr/film/fichefilm_gen_cfilm=278742.html"]
    

    def start_requests(self):
            # Charge le fichier JSON contenant les IDs des films
            with open('idAllocine.json', 'r') as file:
                data = json.load(file)
            
            # Génére les URLs et initier les requêtes Scrapy
            for item in data:
                url = f"https://www.allocine.fr/film/fichefilm_gen_cfilm={item['href']}.html"
                yield scrapy.Request(url=url, callback=self.parse, meta={'film_title': item['title']})

    def parse(self, response):
        image_url = response.xpath('//img[@class="thumbnail-img"]/@src').get()
        title = response.xpath('//div[@class="titlebar-title titlebar-title-xl"]/text()').get()
        
        # Timing extraction seems correct; cleaning is done afterwards.
        timing = response.xpath('//div[@class="meta-body-item meta-body-info"]/span[@class="spacer"]/following-sibling::text()[1]').get()
        
        # Extraction du réalisateur en utilisant XPath
        director_xpath = "//div[contains(@class, 'meta-body-item') and contains(@class, 'meta-body-direction')]/span/text()"
        director = response.xpath(director_xpath).getall()

        # Extraction des acteurs en utilisant XPath
        actors_xpath = "//div[contains(@class, 'meta-body-item') and contains(@class, 'meta-body-actor')]/span/text()"
        actors = response.xpath(actors_xpath).getall()

        # Extraction du nombre de la nationalité
        nationalite =  response.css('section.ovw-technical .item span.nationality::text').get()

        # Extraction du studio 
        studio =  response.css('section.ovw-technical .item span.blue-link::text').get()
        
        # titre original 
        titre_original_xpath = "//div[@class='meta-body-item']/span[@class='light']/following-sibling::text()"
        titre_original = response.xpath(titre_original_xpath).get()
        titre_original = titre_original.strip() if titre_original else None
                


        
        
        
        # Nettoyage de la durée si nécessaire.
        if timing:
            timing = timing.replace('\n', '').strip()
        
        # Création et renvoi de l'objet avec les informations collectées.
        if title:
            yield InfosMovies(image_urls=[image_url], title=title, timing=timing, director=director, actors=actors, nationalite=nationalite, studio=studio, titre_original=titre_original)
        
        
        else:
            self.logger.error(f"Missing data in {response.url}")

    