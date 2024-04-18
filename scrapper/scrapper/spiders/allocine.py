import scrapy
import json, re
from scrapper.items import ImdbscrapperItem

class InfosfilmSpider(scrapy.Spider):
    name = "allocine"
    allowed_domains = ["www.allocine.fr"]
    start_urls = ["https://www.allocine.fr/film/agenda/"]
    
    custom_settings = {
    'FEEDS' : {
        'allocinedata.csv' : {'format' : 'csv', 'overwrite' : True},
    }
    }

    def parse(self, response):
        # Log info pour signaler le début de l'analyse
        self.logger.info("Début de l'analyse de la page principale: %s", response.url)

        # Sélectionne la table contenant les films
        movies_list = response.xpath("/html/body/div/main/section/div/ul")

        for movie in movies_list.xpath('./li'):
            movie = ImdbscrapperItem()

            movie['titre'] = response.xpath('//h2/text()').get()
            movie['titre'].strip().lower()
            movie['synopsis'] = response.xpath('//div[@class="synopsis"]//text()').get()
            movie['salles_fr'] = response.xpath('//div[@class="button-holder"]//text()').get()
 

    


    def parse_box_office(self, response):

        item = ImdbscrapperItem()
        item['titre'] = response.meta['titre']

        # trouve la section du box office fr si le titre du h2 comporte 'Box Office France'
        section = response.xpath('//section[@class="section"]//h2/text()').get()

        if section == "Box Office France":

            # Tente d'extraire la première ligne du tableau qui contient les données de la première semaine
            rows = response.xpath('//tr[@class="responsive-table-row"]')
            
            # Vérifier si la page contient les données nécessaires
            if not rows:
                # Si aucune donnée n'est trouvée, logue un message et passe à l'URL suivante sans traiter cette réponse
                self.logger.info(f"Aucune donnée de box office trouvée pour {response.meta['titre']}. Passage au suivant.")
                return
            
            # Si des données sont présentes, continue avec le traitement
            row_fr = rows[0]  # Utilise la première ligne du box office fr
            # Extrait et nettoye la donnée 'semaine'
            semaine_text = row_fr.xpath('.//td[@class="responsive-table-column first-col"]//text()').getall()
            semaine_clean = ''.join(semaine_text).strip()
            
            # Affecte les données extraites à l'item
            item['titre'] = response.meta['titre']
            item['semaine_fr'] = semaine_clean
            item['entrees_fr'] = row_fr.xpath('.//td[@data-heading="Entrées"]/text()').extract_first().strip()

        elif section == "Box Office US":
            # Tente d'extraire la première ligne du tableau qui contient les données de la première semaine
            rows = response.xpath('//tr[@class="responsive-table-row"]')
            
            # Vérifier si la page contient les données nécessaires
            if not rows:
                # Si aucune donnée n'est trouvée, logue un message et passe à l'URL suivante sans traiter cette réponse
                self.logger.info(f"Aucune donnée de box office trouvée pour {response.meta['titre']}. Passage au suivant.")
                return
            
            # Si des données sont présentes, continue avec le traitement
            row_fr = rows[0]  # Utilise la première ligne du box office fr
            
            # Extrait et nettoye la donnée 'semaine'
            semaine_text = row_fr.xpath('.//td[@class="responsive-table-column first-col"]//text()').getall()
            semaine_clean = ''.join(semaine_text).strip()
            
            # Affecte les données extraites à l'item
            item['titre'] = response.meta['titre']
            item['semaine_fr'] = semaine_clean
            item['entrees_fr'] = row_fr.xpath('.//td[@data-heading="Entrées"]/text()').extract_first().strip()
        
        
        
           
        if section:
                # Des données du box office ont été trouvées, continuer avec les informations générales
                yield scrapy.Request(url=response.meta['general_info_url'], callback=self.parse_general_info, meta={'item' : item})
                

            

         



    def parse_general_info(self, response):
        item = response.meta['item']

        #item['image_urls'] = response.xpath('//img[@class="thumbnail-img"]/@src').get()
        item['titre'] = response.xpath('//div[@class="titlebar-title titlebar-title-xl"]/text()').get()
        
        # duree extraction seems correct; cleaning is done afterwards.
        item['duree'] = response.xpath('//div[@class="meta-body-item meta-body-info"]/span[@class="spacer"]/following-sibling::text()[1]').get()
        
        # Extraction du réalisateur en utilisant XPath
        item['director'] = response.xpath("//div[contains(@class, 'meta-body-item') and contains(@class, 'meta-body-direction')]/span/text()").getall()
        

        # Extraction des acteurs en utilisant XPath
        item['casting_complet'] = response.xpath("//div[contains(@class, 'meta-body-item') and contains(@class, 'meta-body-actor')]/span/text()").getall()
        

        # Extraction du nombre de la nationalité
        item['nationalite'] =  response.css('section.ovw-technical .item span.nationality::text').get()

        # Extraction du studio 
        item['studio'] =  response.css('section.ovw-technical .item span.blue-link::text').get()
          
        
        
        yield item
        
        
        


    
   