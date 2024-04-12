import scrapy
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urlparse, parse_qs
import re, time
from scrapper.items import ImdbItem
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class ImdbproSpider(CrawlSpider):
    name = "imdb"
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
        titre = response.xpath('//h1[@data-testid="hero__pageTitle"]//span/text()').get() or "No Title"

        score = response.xpath('//div[contains(@data-testid, "hero-rating-bar__aggregate-rating__score")]/span/text()').get() or "0"

        nombre_vote = response.xpath('//div[@data-testid="hero-rating-bar__aggregate-rating__score"]/following-sibling::div[2]/text()').get() or "0"

        genre = response.xpath('//div[@data-testid="genres"]//div//a/span/text()').getall() or ["No kind"]

        
        langue = response.xpath('//li[contains(@data-testid, "title-details-languages")]//a/text()').getall() or ["No Language"]

        pays = response.xpath('//li[contains(@data-testid, "title-details-origin")]//a/text()').getall() or ["No Country"]

        pegi = response.xpath('//h1/following-sibling::ul[1]/li[2]//text()').get() or "No Pegi"

        duree = response.xpath('//h1/following-sibling::ul[1]/li[3]//text()').get() or "0"

        annee = response.xpath('//h1/following-sibling::ul[1]/li[1]//text()').get() or "0"
        
        
        image_urls = response.xpath('//img[@class="ipc-image"]/@src').getall()
        
        popularite_score = response.xpath('//div[@data-testid="hero-rating-bar__popularity__score"]/text()').get() or ["No Popularity Score"]
        
        director = response.xpath('//li[@data-testid="title-pc-principal-credit"]//a/text()').get() or ["No Director"]
        
        scenaristes = response.xpath('//li[@data-testid="title-pc-principal-credit"]//a/text()').get() or ["No Writers"]

        casting_principal = response.xpath('//li[@data-testid="title-pc-principal-credit"]//a/text()').getall()[:3] or ["No Casting"]

        budget = response.xpath('//li[@data-testid="title-boxoffice-budget"]//div//span/text()').get() or ["No budget"]

        # Extraire le lien vers la page de release
        release_link_full = None
        release_link = response.xpath('//a[contains(@class, "ipc-metadata-list-item__label") and contains(@href, "releaseinfo")]/@href').get()
        if release_link:
            release_link_full = response.urljoin(release_link)
        else:
            release_link = "No release info link"
        

        if release_link_full:
            if image_urls and titre:
                item = ImdbItem(image_urls=image_urls,url=url,titre=titre, genre=genre, pegi=pegi,duree=duree,annee=annee,score=score,nombre_vote=nombre_vote, casting_principal=casting_principal,langue=langue,pays=pays,popularite_score=popularite_score,director=director,scenaristes=scenaristes,budget=budget,release_link=release_link_full)

                # Passer les données initiales et l'URL de releaseinfo à une nouvelle requête
                request = scrapy.Request(release_link_full, callback=self.parse_release_info)
                request.meta['item'] = item  # Passer l'item existant pour le compléter plus tard
                yield request
        else:
            self.logger.error(f"No release link found for {response.url}. Skipping.")


    def parse_release_info(self, response):
        item = response.meta['item']  # Récupérer l'item passé

        options = Options()
        options.headless = True  # Option pour rendre le navigateur invisible lors de l'exécution
        driver = webdriver.Chrome(options=options)

        try:
            driver.get(response.url)

            # Accepter les cookies
            try:
                accept_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="accept-button"]'))
                )
                accept_button.click()
            except (NoSuchElementException, TimeoutException):
                pass  # Si le bouton d'acceptation des cookies n'est pas trouvé, continuer sans action

            found_france = False
            more_button_clicked = False

            # Boucle tant que l'information sur la France n'est pas trouvée
            while not found_france:
                # Rechercher la date de sortie pour la France
                try:
                    france_release_date_element = driver.find_element(By.XPATH, '//li[.//a[contains(@aria-label, "France")]]//span[@class="ipc-metadata-list-item__list-content-item"]')
                    release_date_france = france_release_date_element.text
                    found_france = True
                    item['release_date_france'] = release_date_france
                    break  # Sortir de la boucle si l'information est trouvée
                except NoSuchElementException:
                    # Si l'information n'est pas trouvée, essayer de cliquer sur "More"
                    try:
                        more_button = WebDriverWait(driver, 2).until(
                            EC.visibility_of_element_located((By.XPATH, '//button[contains(@class, "ipc-see-more__button") and .//span[contains(text(), "more")]]'))
                        )
                        more_button.click()
                        more_button_clicked = True
                        time.sleep(2)  # Attendre que le contenu supplémentaire soit chargé
                    except (NoSuchElementException, TimeoutException):
                        # S'il n'y a plus de bouton "More", arrêter la boucle
                        if not more_button_clicked:
                            # Si le bouton "More" n'a jamais été cliqué, cela signifie qu'il n'y avait aucun dès le début
                            self.logger.info(f"No more 'More' button or France info not found: {response.url}")
                            break
                        more_button_clicked = False  # Réinitialiser pour la prochaine itération

            if not found_france:
                self.logger.info(f"France release date not found: {response.url}")
        finally:
            driver.quit()

        yield item


