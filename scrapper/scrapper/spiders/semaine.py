import scrapy
from scrapper.items import ImdbscrapperItem
import re

class BygenreSpider(scrapy.Spider):
    name = "semaine"
    allowed_domains = ["www.allocine.fr"]
    start_urls = ['https://www.allocine.fr/film/sorties-semaine/']

    def parse(self, response):
        # Define the base URL
        base_url = "https://www.allocine.fr"
        section = response.xpath('//section[contains(@class, "section section-wrap")]//ul')
        
        for movie in section.xpath('.//li[@class="mdl"]'):
            # Correct XPath to target the actual class of the anchor
            movie_url = movie.xpath('.//a[@class="meta-title-link"]/@href').get()
            
            # Check if movie_url is None to avoid errors
            if movie_url is None:
                continue  # Skip this movie if no URL is found
            
            # Handle cases where the URL might already be absolute
            full_movie_url = movie_url if movie_url.startswith('http') else base_url + movie_url
            print(full_movie_url)  # Debug print to check the URL

            
            # Transmit the image URL via meta
            yield response.follow(full_movie_url, self.parse_detail_page)

    def parse_detail_page(self, response):
        self.logger.info(f'Parsing detail page: {response.url}')
        item = ImdbscrapperItem()
        item['semaine_fr_allo'] = response.xpath("//div[@class='meta-body-item meta-body-info']/span[1]/text()").get()
        item['image_url'] = response.xpath('//div[@class="card entity-card entity-card-list cf entity-card-player-ovw"]//img/@src').get()
        item['titre'] = response.xpath("//div[@class='titlebar-title titlebar-title-xl']/text()").get()
        item['genres_allo'] = response.css('div.meta-body-item.meta-body-info span::text').getall()
        item['duree_allo'] = response.xpath("//div[@class='meta-body-item meta-body-info']/text()").getall()
        item['realisateur_allo'] =  response.css('div.meta-body-item.meta-body-direction span::text').getall()
        item['producteur_allo'] =  response.css('div.meta-body-item.meta-body-direction span::text').getall() 
        item['casting_complet_allo'] = response.css('div.meta-body-item.meta-body-actor span::text').getall()
        item['synopsis'] = response.xpath('//section[@id="synopsis-details"]//p[@class="bo-p"]/text()').get()
        item['pays_allo'] =  response.css('section.ovw-technical .item span.nationality::text').get()
        item['studio_allo'] = response.css('section.ovw-technical .item span.blue-link::text').get()
        item['pegi_fr_allo'] = response.xpath('//section[@id="synopsis-details"]//span[@class="certificate-text"]/text()').get()
        item['salles_fr_allo'] = response.css('.buttons-holder .button.button-sm.button-inverse-full .txt::text').get()

        

        
        yield item
