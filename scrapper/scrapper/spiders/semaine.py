import scrapy
from scrapper.items import ImdbscrapperItem
import re
# faire le jeudi à 12h00 dans films_hist
class BygenreSpider(scrapy.Spider):
    name = "semaine"
    allowed_domains = ["www.allocine.fr"]
    #start_urls = ['https://www.allocine.fr/film/sorties-semaine/'] #+ se diriger vers le lien précedent et effectuer le bordel
    start_urls = ['https://www.allocine.fr/film/agenda/sem-2024-04-10/'] #+ se diriger vers le lien précedent et effectuer le bordel
    
    film_ids = []

    '''def parse_start_page(self, response):
        base_url = 'https://www.allocine.fr'
        
        

        
        prev_link = response.xpath('//section[@class="section section-wrap gd-2-cols gd-gap-30"]/div[@class="pagination"]//span[@class="button-left"]/@href').get()

        print('*****************************************************')
        print(prev_link)
        
        if prev_link:
            prev_url = base_url + prev_link
            yield scrapy.Request(prev_url, callback=self.parse)'''


    def parse(self, response):
            base_url = "https://www.allocine.fr"
            section = response.xpath('//section[contains(@class, "section section-wrap")]//ul')
            
            for movie in section.xpath('.//li[@class="mdl"]'):
                movie_url = movie.xpath('.//a[@class="meta-title-link"]/@href').get()
                if movie_url:
                    full_movie_url = base_url + movie_url if not movie_url.startswith('http') else movie_url
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

        film_id_match = re.search(r'cfilm=(\d+)\.html', response.url)
        
        
        if film_id_match:
            film_id = film_id_match.group(1)
            box_office_url = f"https://www.allocine.fr/film/fichefilm-{film_id}/box-office/"
            request = response.follow(box_office_url, callback=self.parse_box_office, meta={'item': item, 'dont_redirect' : True}, errback=self.handle_error)
            request.meta['handle_httpstatus_all'] = True
            yield request
        else:
            item['error'] = 'Film ID not found, unable to construct box office URL'
            yield item
            
        
        

    def parse_box_office(self, response):
        item = response.meta['item']
        if response.status != 200:
            item['error'] = f'Unexpected status code: {response.status}'
            yield item
        else:
        

        # Tentative d'extraction des données du box office français
            france_section = response.xpath('//section[contains(.//h2/text(), "Box Office France")]')
            if france_section:
                last_entries_fr = france_section.xpath('.//tr[1]/td[@data-heading="Entrées"]/text()').get()
                if last_entries_fr:
                    last_entries_fr = int(last_entries_fr.replace(' ', '').replace('\xa0', ''))
                    item['entrees_fr_allo'] = last_entries_fr
                else:
                    self.logger.debug("No entries found for FR box office.")
            else:
                self.logger.debug("FR box office section not found.")

            # Tentative d'extraction des données du box office américain
            usa_section = response.xpath('//section[contains(.//h2, "Box Office US")]')

            # Tentative d'extraction de la première date sous "Semaine" en utilisant le correct XPath pour <span>
            if usa_section:
                last_week_usa = usa_section.xpath('.//tbody/tr[1]/td[@data-heading="Semaine"]/span/text()').get()

                if last_week_usa:
                    last_week_usa = last_week_usa.strip()
                                            
                    last_entries_usa = usa_section.xpath('.//tr[1]/td[@data-heading="Entrées"]/text()').get()
                    if last_entries_usa:
                        last_entries_usa = int(last_entries_usa.replace(' ', '').replace('\xa0', ''))
                        item['semaine_usa_allo'] = last_week_usa if last_week_usa else None
                        item['entrees_usa_allo'] = last_entries_usa
                else:
                    self.logger.debug("No entries found for USA box office.")
            else:
                self.logger.debug("USA box office section not found.")

            yield item
    
    def handle_error(self, failure):
        # This method handles errors when accessing the box office URL
        self.logger.error(f'Request failed with error {failure.value.response.status} at {failure.request.url}')
        item = failure.request.meta['item']
        item['error'] = f'Failed to access box office URL: {failure.value.response.status}'
        yield item