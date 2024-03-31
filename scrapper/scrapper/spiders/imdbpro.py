import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urlparse, parse_qs
import re
from scrapper.items import imdbproItem

class ImdbproSpider(CrawlSpider):
    name = "imdbpro"
    handle_httpstatus_list = [503]
    allowed_domains = ["www.imdb.com"]
    start_urls = ["https://www.imdb.com/chart/top/?ref_=nv_mv_250"]
    urls_vues = set()
    rules = (
        Rule(LinkExtractor(allow=(r'/title/tt\d+/'), deny=(r'/title/tt\d+/[a-z]+')), callback="parse_film", follow=True),
    )

    

    def parse_film(self, response):
        # Vérification pour exclure les pages liées à des séries
        if response.xpath('//a[contains(@data-testid, "series-episode")]'):
            self.logger.info(f"Skipping series related page: {response.url}")
            return  # Cette page est liée à une série, donc on l'ignore
        
        if response.xpath('//a[contains(@data-testid, "series")]'):
            self.logger.info(f"Skipping series related page: {response.url}")
            return  # Cette page est liée à une série, donc on l'ignore

        url = response.url

        if re.search(r'ref_=tt_sims_tt_[it]_\d{1,2}', response.url):
            self.logger.info(f"URL exclue à cause des paramètres de requête spécifiques : {response.url}")
            return  # Ignore cette page si elle contient les paramètres spécifiés

        if response.url in self.urls_vues:
            self.logger.info(f"URL déjà visitée : {response.url}")
            return

        self.urls_vues.add(response.url)

        

        # Suite du traitement pour les films
        title = response.xpath('//h1[@data-testid="hero__pageTitle"]//span/text()').get() or "No Title"

        score = response.xpath('//div[contains(@data-testid, "hero-rating-bar__aggregate-rating__score")]/span/text()').get() or "0"

        nbre_vote = response.xpath('//div[@data-testid="hero-rating-bar__aggregate-rating__score"]/following-sibling::div[2]/text()').get() or "0"

        genre = response.xpath('//div[@data-testid="genres"]//div//a/span/text()').getall() or ["No kind"]

        
        langue = response.xpath('//li[contains(@data-testid, "title-details-languages")]//a/text()').getall() or ["No Language"]

        pays = response.xpath('//li[contains(@data-testid, "title-details-origin")]//a/text()').getall() or ["No Country"]

        pegi = response.xpath('//h1/following-sibling::ul[1]/li[2]//text()').get() or "No Pegi"

        duree = response.xpath('//h1/following-sibling::ul[1]/li[3]//text()').get() or "0"

        annee = response.xpath('//h1/following-sibling::ul[1]/li[1]//text()').get() or "0"
        interdits = ["TV Movie", "Video Game", "Video", "TV Special"]
        for mot in interdits:
            if mot in annee:
                self.logger.info(f"Skipping TV movie page: {response.url}")
                return  # Cette page concerne un téléfilm, donc on l'ignore 
        
        image_urls = response.xpath('//img[@class="ipc-image"]/@src').getall()
        
        popularite_score = response.xpath('//div[@data-testid="hero-rating-bar__popularity__score"]/text()').get() or ["No Popularity Score"]
        
        director = response.xpath('//li[@data-testid="title-pc-principal-credit"]//a/text()').get() or ["No Director"]
        
        scenaristes = response.xpath('//li[@data-testid="title-pc-principal-credit"]//a/text()').get() or ["No Writers"]

        casting_principal = response.xpath('//li[@data-testid="title-pc-principal-credit"]//a/text()').getall()[:3] or ["No Casting"]

        budget = response.xpath('//li[@data-testid="title-boxoffice-budget"]//div//span/text()').get() or ["No budget"]

        # Extraire le lien vers la page de release
        release_link = response.xpath('//a[contains(@class, "ipc-metadata-list-item__label") and contains(@href, "releaseinfo")]/@href').get()
        if release_link:
            release_link = response.urljoin(release_link)
        else:
            release_link = "No release info link"
        


        if image_urls and title:
            yield imdbproItem(image_urls=image_urls,url=url,title=title, genre=genre, pegi=pegi,duree=duree,annee=annee,score=score,nombre_vote=nbre_vote, casting_principal=casting_principal,langue=langue,pays=pays,popularite_score=popularite_score,director=director,scenaristes=scenaristes,budget=budget,release_link=release_link)


    