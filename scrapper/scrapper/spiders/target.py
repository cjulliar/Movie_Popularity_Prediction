import scrapy
import json
from scrapper.items import BoxOfficeItem  

class TargetSpider(scrapy.Spider):
    name = "target"
    allowed_domains = ["www.allocine.fr"]

    def start_requests(self):
        # Charge le fichier JSON contenant les IDs des films
        with open('test.json', 'r') as file:
            data = json.load(file)
        
        # Génére les URLs et initier les requêtes Scrapy
        for item in data:
            url = f"https://www.allocine.fr/film/fichefilm-{item['href']}/box-office/"
            yield scrapy.Request(url=url, callback=self.parse_box_office, meta={'film_title': item['title']})

    def parse_box_office(self, response):
        # Tente d'extraire la première ligne du tableau qui contient les données de la première semaine
        rows = response.xpath('//tr[@class="responsive-table-row"]')
        
        # Vérifier si la page contient les données nécessaires
        if not rows:
            # Si aucune donnée n'est trouvée, logue un message et passe à l'URL suivante sans traiter cette réponse
            self.logger.info(f"Aucune donnée de box office trouvée pour {response.meta['film_title']}. Passage au suivant.")
            return
        
        # Si des données sont présentes, continue avec le traitement
        row_fr = rows[0]  # Utilise la première ligne du box office fr
        row_usa = rows[3]  # Utilise la première ligne du box office usa
        item = BoxOfficeItem()
        
        # Extrait et nettoye la donnée 'semaine'
        semaine_text = row_fr.xpath('.//td[@class="responsive-table-column first-col"]//text()').getall()
        semaine_clean = ''.join(semaine_text).strip()
        
        # Affecte les données extraites à l'item
        item['film_title'] = response.meta['film_title']
        item['semaine'] = semaine_clean
        item['entrees'] = row_fr.xpath('.//td[@data-heading="Entrées"]/text()').extract_first().strip()

        
        
        
        # Extrait et nettoye la donnée 'semaine'
        semaine_text = row_usa.xpath('.//td[@class="responsive-table-column first-col"]//text()').getall()
        semaine_clean = ''.join(semaine_text).strip()
        
        # Affecte les données extraites à l'item
        
        item['semaine_usa'] = semaine_clean
        item['entrees_usa'] = row_usa.xpath('.//td[@data-heading="Entrées"]/text()').extract_first().strip()
        
        
        # Renvoye l'item extrait
        yield item
