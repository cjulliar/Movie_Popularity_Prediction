import scrapy, time, re, csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from imdbscrapper.items import ImdbscrapperItem
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from scrapy.http import HtmlResponse

class BygenreSpider(scrapy.Spider):
    name = "release_date_imdb"
    allowed_domains = ["www.imdb.com"]
    #start_urls = ["https://www.imdb.com/feature/genre/?ref_=nv_ch_gr"]
    #start_urls = ["https://www.imdb.com/search/title/?title_type=feature"]
    
    def __init__(self):
       
        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")  # Utiliser le disque au lieu de /dev/shm pour le stockage temporaire
        chrome_options.add_argument("--no-sandbox")  # Désactiver le mode sandbox pour Chrome
        chrome_options.add_argument("--disable-gpu")  # Désactiver l'accélération matérielle

        chrome_service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    
    
    def start_requests(self):
        # Emplacement de votre fichier CSV
        csv_file_path = 'parse_detail_page.csv'
        # Lire les IDs de film à partir du fichier CSV
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                film_id = row['film_id']
                url = f'https://www.imdb.com/title/{film_id}/releaseinfo/?ref_=tt_dt_rdat'
                item = ImdbscrapperItem()
                item['film_id'] = film_id
                yield scrapy.Request(url, callback=self.parse_date_sortie, meta={'item': item})
    
    def parse_date_sortie(self, response):
        item = response.meta['item']
        self.driver.get(response.url)
        wait = WebDriverWait(self.driver, 5)

        # Handle cookie acceptance
        try:
            accept_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Accept")]')))
            accept_button.click()
        except (NoSuchElementException, TimeoutException):
            self.logger.info("Accept button not found or not clickable.")
        
        try:
            while True:
                # Attente pour que le bouton soit cliquable
                button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, '/html/body/div[2]/main/div/section/div/section/div/div[1]/section[1]/div[2]/ul/div/span[1]/button')))
                
                # Amélioration du défilement pour s'assurer que le bouton est dans une position cliquable
                
                self.driver.execute_script("arguments[0].click();", button)
        except TimeoutException:
            self.logger.info("Plus de boutons 'Voir plus' à cliquer.")


        # Extract the release date using Selenium
        try:
            france_release_date_element = self.driver.find_element(By.XPATH, "//a[@aria-label='France']/following-sibling::div/ul/li/span[@class='ipc-metadata-list-item__list-content-item']")
            france_release_date = france_release_date_element.text
        except NoSuchElementException:
            france_release_date = "No date found"
            self.logger.info("Release date in France not found.")

        item['date_sortie'] = france_release_date
        

        self.logger.info(f"Release date in France: {france_release_date}")
        yield item
    

    def close(self, reason):
        self.driver.quit()
        super(BygenreSpider, self).close(self, reason)