import scrapy
import re

class ImdbIdSpider(scrapy.Spider):
    name = "imdb_id"
    allowed_domains = ["www.imdb.com"]
    start_urls = ["https://www.imdb.com/search/title/?title_type=feature"]

    def parse(self, response):
        li_selector = "//div[contains(@class, 'ipc-page-grid ipc-page-grid--bias-left ipc-page-grid__item ipc-page-grid__item--span-2')]//ul[contains(@class, 'ipc-metadata-list ipc-metadata-list--dividers-between sc-748571c8-0 jmWPOZ detailed-list-view ipc-metadata-list--base')]//li"
        for li in response.xpath(li_selector):
            # Extraire l'URL de l'élément <a>
            href = li.xpath(".//a[contains(@class, 'ipc-title-link-wrapper')]/@href").get()
            # Utiliser une expression régulière pour extraire l'ID IMDb des chiffres
            imdb_id = re.search(r'tt(\d+)', href).group(1) if href else None
            
            # Extraire le texte du <h3> qui suit le <li>
            
            h3_text = li.xpath("following::h3[1]/text()").get() 
            
            yield {
                'imdb_id': imdb_id,
                'h3_text': h3_text  
            }
        