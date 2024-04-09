import scrapy
import json, re
from scrapper.items import JpboxItem

class JpspiderSpider(scrapy.Spider):
    name = "jpbox2"
    allowed_domains = ["www.jpbox-office.com"]
    start_urls = ["https://www.jpbox-office.com/v9_demarrage.php?view=2"]
    urls_vues = set()
    custom_settings = {
    'FEEDS' : {
        'jpboxoffice.json' : {'format' : 'json', 'overwrite' : True},
        }
    }

    def parse(self, response):
        self.logger.info("Analyse de la page principale du film : %s", response.url)
        films = response.xpath('/html/body/div[5]/table[2]')
        url_socle = "https://www.jpbox-office.com/"
        first_week_entries = response.css('table.tablesmall.tablesmall5 tr td.col_poster_contenu_majeur::text').get()
        copies = response.css('table.tablesmall.tablesmall5 tr:nth-child(2) td:nth-child(7)::text').get()
        for film in films:
            film_url = film.xpath('//h3/a/@href').getall()
            if film_url:
                for url in film_url:
                    full_url = url_socle + url
                    if full_url in self.urls_vues:
                        continue
                    else:
                        self.urls_vues.add(full_url)
                    yield scrapy.Request(full_url, callback=self.parse_movie,meta={'first_week_entries' : first_week_entries, 'copies' : copies})
            else:
                self.logger.warning("Aucune URL de film trouvée dans la ligne : %s", film.extract())

        current_page = response.meta.get('current_page', 0)
        page_suivante = current_page + 30 # 30 films par pages
        if page_suivante < 10000: # Un peu moins de 10 000 pages au total
            url_page_suivante = f"https://www.jpbox-office.com/v9_demarrage.php?view=2&filtre=classg&limite={page_suivante}&infla=0&variable=0&tri=champ0&order=DESC&limit5=0"
            yield scrapy.Request(url_page_suivante, callback=self.parse, meta={'current_page': page_suivante})


    def parse_movie(self, response):
        item = JpboxItem()
        first_week_entries = response.meta.get('first_week_entries')
        copies = response.meta.get('copies')

        item['url'] = response.url
        item['title'] = response.xpath('//h1/text()').get()
        item['director'] = response.css('table.table_2022titre h4 a::text').get()
        item['country'] = response.css('table.table_2022titre h3 a::text').get()
        item['genre'] = response.css('table.table_2022titre h3 a:nth-of-type(2)::text').get()
        item['date'] = response.xpath('//table[@class="tablelarge1"]//div//p//a/text()').get()
        item['studio'] = response.xpath('//h3[text()="Distribué par"]/following-sibling::text()[1]')[-1].get()
        item['first_week_entries'] = first_week_entries
        item['copies'] = copies
        item['casting'] = response.xpath('//div[5]/div[1]/ul/li[6]/a/text()')[1].extract().strip()
        item['franchise'] = response.xpath('//div[@id="nav2"]//ul//a[contains(text(), "Franchise")]/text()').get()
        item['remake'] = response.xpath('//div[@id="nav2"]//ul//a[contains(text(), "Remake")]/text()').get()
        
        # Contournement de la disposition des cases Casting (5e ou 6e position sur la fiche film)
        box5 = response.xpath('//*[@id="nav2"]/ul/li[5]/a/text()')[-1].extract()
        box6 = response.xpath('//*[@id="nav2"]/ul/li[6]/a/text()')[-1].extract()
        if "Casting" in box5 :
            casting_url = response.xpath('//*[@id="nav2"]/ul/li[5]/a/@href').get()
        elif "Casting" in box6 :
            casting_url = response.xpath('//*[@id="nav2"]/ul/li[6]/a/@href').get()
        else:
            casting_url = None
        if casting_url:
            yield response.follow(casting_url, callback=self.parse_casting, meta={'item': item})

        budget_url = response.xpath('//*[@id="nav2"]/ul/li[1]/a/@href').get()
        yield response.follow(budget_url, callback=self.parse_budget, meta={'item' : item})

        if casting_url:
            request = scrapy.Request(response.urljoin(casting_url), callback=self.parse_casting, meta={'item': item})
            request.meta['budget_url'] = budget_url
            yield request
        elif budget_url:  # Si la date de sortie n'est pas nécessaire ou absente
            yield scrapy.Request(response.urljoin(budget_url), callback=self.parse_budget, meta={'item': item})
        else:
            yield item

    def parse_casting(self, response):
        self.logger.info("Analyse de la page du casting: %s", response.url)
        item = response.meta['item']
        item['actors'] = response.xpath('//tr[@valign="top"]/td[contains(@class, "col_poster_titre")]/h3/a[@itemprop="name"]/text()').getall()
        item['producer'] = response.xpath('//tr/td[contains(@class, "col_poster_titre") and @itemprop="producer"]/h3/a[@itemprop="name"]/text()').get()
        item['compositor'] = response.xpath('//tr/td[contains(@class, "col_poster_titre") and @itemprop="compositor"]/h3/a[@itemprop="name"]/text()').get()
        yield item

    def parse_budget(self, response):
        self.logger.info("Analyse de la page du budget : %s", response.url)
        item = response.meta['item']
        item['budget'] = response.css('table.tablesmall.tablesmall1b tr td div strong::text').get()
        yield item