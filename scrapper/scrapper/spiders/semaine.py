import scrapy
from scrapper.items import ImdbscrapperItem

class BygenreSpider(scrapy.Spider):
    name = "semaine"
    allowed_domains = ["www.imdb.com"]
    start_urls = ['https://www.imdb.com/calendar/?ref_=rlm&region=FR&type=MOVIE']

    def parse(self, response):
        # Corrected XPath for selecting movie items
        movies = response.xpath('.//article[@data-testid="calendar-section"][1]//li')
        
        for movie in movies:
            movie_url = movie.xpath('.//a/@href').get()
            url = "https://www.imdb.com/"
            movie_full_url = f"{url}{movie_url}"
            yield response.follow(movie_full_url, self.parse_detail_page)

    def parse_detail_page(self, response):
        self.logger.info(f'Parsing detail page: {response.url}')
        item = ImdbscrapperItem()
        
        # Correctly extracting and assigning values with improved error handling
        item['titre'] = response.xpath("//h1[@data-testid='hero__pageTitle']/span/text()").get() or 'Titre non trouvé'
        item['score'] = response.xpath('//div[contains(@data-testid, "hero-rating-bar__aggregate-rating__score")]/span/text()').get(default="0")
        item['nbre_vote'] = response.xpath('//div[@data-testid="hero-rating-bar__aggregate-rating__score"]/following-sibling::div[2]/text()').get()
        item['genres'] = response.xpath('//div[@data-testid="genres"]//div//a/span/text()').getall() or []
        item['langue'] = response.xpath('//li[contains(@data-testid, "title-details-languages")]//a/text()').getall() or []
        item['pays'] = response.xpath('//li[contains(@data-testid, "title-details-origin")]//a/text()').getall() or []
        details = response.xpath("//h1/following-sibling::ul[1]/li")
        for detail in details:
            text = detail.xpath(".//text()").get()
            if 'h' in text:
                item['duree'] = text
            elif text.isdigit():
                item['annee'] = text
            else:
                item['pegi'] = text if text else "No Pegi"
        item['annee'] = response.xpath('//h1/following-sibling::ul[1]/li[1]//text()').get() or "0"
        item['popularite_score'] = response.xpath('//div[@data-testid="hero-rating-bar__popularity__score"]/text()').get(default="0")
        item['director'] = response.xpath('//li[@data-testid="title-pc-principal-credit"]//a/text()').get() or ["No Director"]
        item['scenaristes'] = response.xpath('//li[@data-testid="title-pc-principal-credit"]//a/text()').get() or ["No Writers"]
        item['casting_principal'] = response.xpath('//li[@data-testid="title-pc-principal-credit"]//a/text()').getall()[:3] or ["No Casting"]
        item['casting_complet'] = response.xpath('//div[@data-testid="title-cast-item"]//a[@data-testid="title-cast-item__actor"]/text()').extract() or ["No Casting"]
        item['budget'] = response.xpath('//li[@data-testid="title-boxoffice-budget"]//div//span/text()').get() or ["No budget"]
        yield item

