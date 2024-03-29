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

        # trouve la section du box office fr si le titre du h2 comporte 'Box Office France'
        sections = response.xpath('//section[@class="section"]//h2/text()').getall()
        print(sections)
        
        for section in sections:

            if section == "Box Office France":

                # Tente d'extraire la première ligne du tableau qui contient les données de la première semaine
                table_fr = response.xpath('//table[@class="box-office-table table-3-cell responsive-table responsive-table-lined"]')[0]
                
                # Vérifier si la page contient les données nécessaires
                if not table_fr:
                    # Si aucune donnée n'est trouvée, logue un message et passe à l'URL suivante sans traiter cette réponse
                    self.logger.info(f"Aucune donnée de box office trouvée pour {response.meta['film_title']}. Passage au suivant.")
                    return
                
                
                item = BoxOfficeItem()
                # Extrait et nettoye la donnée 'semaine'
                semaine_text_fr = table_fr.xpath('.//tr[1]//td[@data-heading="Semaine"]//text()').getall()
                semaine_clean = ''.join(semaine_text_fr).strip()
                
                # Affecte les données extraites à l'item
                item['film_title'] = response.meta['film_title']
                item['semaine_fr'] = semaine_clean
                item['entrees_fr'] = table_fr.xpath('.//td[@data-heading="Entrées"]/text()').get().strip()

            elif section == "Box Office US":
               # Tente d'extraire la première ligne du tableau qui contient les données de la première semaine
                table_usa = response.xpath('//table[@class="box-office-table table-3-cell responsive-table responsive-table-lined"]')[1]
                
                # Vérifier si la page contient les données nécessaires
                if not table_usa:
                    # Si aucune donnée n'est trouvée, logue un message et passe à l'URL suivante sans traiter cette réponse
                    self.logger.info(f"Aucune donnée de box office trouvée pour {response.meta['film_title']}. Passage au suivant.")
                    return
                
                
               
                # Extrait et nettoye la donnée 'semaine'
                semaine_text_usa = table_usa.xpath('.//tr[1]//td[@data-heading="Semaine"]//text()').getall()
                semaine_clean = ''.join(semaine_text_usa).strip()
                
                # Affecte les données extraites à l'item
                item['film_title'] = response.meta['film_title']
                item['semaine_usa'] = semaine_clean
                item['entrees_usa'] = table_usa.xpath('.//td[@data-heading="Entrées"]/text()').get().strip()
            
            
            
        # Renvoye l'item extrait
        yield item
