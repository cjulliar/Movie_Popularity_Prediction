import scrapy
import csv
from urllib.parse import quote_plus
from scrapper.items import ImdbscrapperItem

class ImdbSpider(scrapy.Spider):
    name = 'imdbid'
    allowed_domains = ['imdb.com']
    
    def start_requests(self):
        csv_file_path = 'allocine.csv' 
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                titre = row['titre']
                search_url = f"https://www.imdb.com/find?q={quote_plus(titre)}&ref_=nv_sr_sm"
                yield scrapy.Request(search_url, self.parse, meta={'title': titre})
    
    def parse(self, response):
        item = ImdbscrapperItem()
        item['titre'] = response.meta['titre']
        href_selector = "//section[contains(@class, 'ipc-page-section')]//a[contains(@class, 'ipc-metadata-list-summary-item__t')]/@href"
        item['movie_id'] = response.xpath(href_selector).get()
        
        # Vérifiez si movie_id est disponible
        if item['movie_id']:
            # Construisez l'URL de la page de détails du film
            movie_id = item['movie_id'].split('/')[2]  # Extraire l'identifiant unique du film
            detail_page_url = f"https://www.imdb.com/title/{movie_id}/"
            
            # Effectuez une demande pour la page de détails du film
            yield scrapy.Request(detail_page_url, callback=self.parse_detail_page, meta={'item': item})
        else:
            self.logger.warning(f"Movie ID not found for {item['title']}")

    def parse_detail_page(self, response):
        self.logger.info(f'Parsing detail page: {response.url}')
        
        # Récupérez l'objet Item transmis à travers la méta
        item = ImdbscrapperItem()
        item['titre'] = response.xpath("//h1[@data-testid='hero__pageTitle']/span/text()").get() or 'Titre non trouvé'
        item['score'] = response.xpath('//div[contains(@data-testid, "hero-rating-bar__aggregate-rating__score")]/span/text()').get() or "0"
        item['nombre_vote'] = response.xpath('//div[@data-testid="hero-rating-bar__aggregate-rating__score"]/following-sibling::div[2]/text()').get() or "0"
        item['genres'] = response.xpath('//div[@data-testid="genres"]//div//a/span/text()').getall() or ["No kind"]
        item['langue'] = response.xpath('//li[contains(@data-testid, "title-details-languages")]//a/text()').getall() or ["No Language"]
        item['pays'] = response.xpath('//li[contains(@data-testid, "title-details-origin")]//a/text()').getall() or ["No Country"]
        item['pegi'] = response.xpath('//h1/following-sibling::ul[1]/li[2]//text()').get() or "No Pegi"
        item['duree'] = response.xpath('//h1/following-sibling::ul[1]/li[3]//text()').get() or "0"
        item['annee'] = response.xpath('//h1/following-sibling::ul[1]/li[1]//text()').get() or "0"
        item['popularite_score'] = response.xpath('//div[@data-testid="hero-rating-bar__popularity__score"]/text()').get() or ["No Popularity Score"]
        item['director'] = response.xpath('//li[@data-testid="title-pc-principal-credit"]//a/text()').get() or ["No Director"]
        item['scenaristes'] = response.xpath('//li[@data-testid="title-pc-principal-credit"]//a/text()').get() or ["No Writers"]
        item['casting_principal'] = response.xpath('//li[@data-testid="title-pc-principal-credit"]//a/text()').getall()[:3] or ["No Casting"]
        item['casting_complet'] = response.xpath('//div[@data-testid="title-cast-item"]//a[@data-testid="title-cast-item__actor"]/text()').extract() or ["No Casting"]
        item['budget'] = response.xpath('//li[@data-testid="title-boxoffice-budget"]//div//span/text()').get() or ["No budget"]
        
        yield item
