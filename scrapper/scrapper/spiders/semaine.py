import scrapy
from scrapper.items import ImdbscrapperItem

class BygenreSpider(scrapy.Spider):
    name = "semaine"
    allowed_domains = ["www.imdb.com"]
    start_urls = ['https://www.imdb.com/calendar/?ref_=rlm&region=FR&type=MOVIE']

    def parse(self, response):
        for section in response.xpath('//article[@data-testid="calendar-section"]'):
            release_date = section.xpath('.//h3[contains(@class, "ipc-title__text")]/text()').get()
            
            # Créer un nouvel objet item pour chaque film
            
            
            # Ajouter les URL des images à l'objet item
            for movie in section.xpath('.//li[contains(@data-testid, "coming-soon-entry")]'):
                movie_url = movie.xpath('.//a[contains(@href, "/title/")]/@href').get()
                full_movie_url = response.urljoin(movie_url)
                
                yield response.follow(full_movie_url, self.parse_detail_page, meta={'release_date': release_date})


    def parse_detail_page(self, response):
        self.logger.info(f'Parsing detail page: {response.url}')
        item = ImdbscrapperItem()
        
        item['semaine_fr'] = response.meta.get('release_date')
        item['titre'] = response.xpath("//h1[@data-testid='hero__pageTitle']/span/text()").get() or 'Titre non trouvé'
        item['genres'] =  response.xpath('//div[@data-testid="genres"]//div//a/span/text()').getall()
        item['pays'] = response.xpath('//li[contains(@data-testid, "title-details-origin")]//a/text()').getall()
        details = response.xpath("//h1/following-sibling::ul[1]/li")
        item['image_urls'] = response.xpath('//div[@data-testid="hero-media__poster"]//img/@src').getall()


        for detail in details:
            text = detail.xpath(".//text()").get()
            if 'h' in text:
                item['duree'] = text
            elif text.isdigit():
                item['annee'] = text
            else:
                item['pegi_fr'] = text if text else "No Pegi"
        
        item['producteur'] =  response.xpath('//li[@data-testid="title-pc-principal-credit"]//a/text()').get() or "No Director"
        item['casting_complet'] = response.xpath('//div[@data-testid="title-cast-item"]//a[@data-testid="title-cast-item__actor"]/text()').extract() or "No Casting"
        item['budget'] = response.xpath('//li[@data-testid="title-boxoffice-budget"]//div//span/text()').get() or 0
        yield item

