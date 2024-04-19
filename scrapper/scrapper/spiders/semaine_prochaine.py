import scrapy
from scrapper.items import ImdbscrapperItem
# faire le lundi à 7h00 dans predict_films
class BygenreSpider(scrapy.Spider):
    name = "semaine_prochaine"
    allowed_domains = ["www.imdb.com"]
    start_urls = ['https://www.imdb.com/calendar/?ref_=rlm&region=FR&type=MOVIE']

    def parse(self, response):
        # Sélection de la première section seulement
        section = response.xpath('//article[@data-testid="calendar-section"]')[0]
        
        if section:
            release_date = section.xpath('.//h3[contains(@class, "ipc-title__text")]/text()').get()
            
            for movie in section.xpath('.//li[contains(@data-testid, "coming-soon-entry")]'):
                movie_url = movie.xpath('.//a[contains(@href, "/title/")]/@href').get()
                full_movie_url = response.urljoin(movie_url)
                image_url = movie.xpath('.//img/@src').get()

                # Transmission de l'URL de l'image via meta
                yield response.follow(full_movie_url, self.parse_detail_page, meta={'release_date': release_date, 'image_url': image_url})

    def parse_detail_page(self, response):
        self.logger.info(f'Parsing detail page: {response.url}')
        item = ImdbscrapperItem()
        item['semaine_fr'] = response.meta.get('release_date')
        item['image_url'] = response.meta['image_url'] 
        item['titre'] = response.xpath("//h1[@data-testid='hero__pageTitle']/span/text()").get()
        item['genres'] =  response.xpath('//div[@data-testid="genres"]//div//a/span/text()').getall()
        item['budget'] = response.xpath('//li[@data-testid="title-boxoffice-budget"]//div//span/text()').get()
        item['pays'] = response.xpath('//li[contains(@data-testid, "title-details-origin")]//a/text()').getall()
        item['studio'] = response.xpath("//li[@data-testid='title-details-companies']//ul[@role='presentation']/li/a[@role='button']/text()").extract()  
        details = response.xpath("//h1/following-sibling::ul[1]/li")
        

        for detail in details:
            text = detail.xpath(".//text()").get()
            if 'h' in text:
                item['duree'] = text
            elif text.isdigit():
                item['annee'] = text
            else:
                item['pegi_fr'] = text if text else "No Pegi"
        
        item['producteur'] =  response.xpath('//li[@data-testid="title-pc-principal-credit"]//a/text()').get()
        item['casting_complet'] = response.xpath('//div[@data-testid="title-cast-item"]//a[@data-testid="title-cast-item__actor"]/text()').extract()
        
        yield item

