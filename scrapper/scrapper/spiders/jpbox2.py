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
        'moviedata.json' : {'format' : 'json', 'overwrite' : True},
        }
    }

    def parse(self, response):
        films = response.css('td.col_poster_titre')
        for film in films:
            next_url = film.xpath('//*[@id="content"]//td[3]/h3/a/@href').get()
            # print("Relative URL:", relative_url)
            film_url = 'https://www.jpbox-office.com/' + next_url
            if film_url in self.urls_vues:
                continue
            else:
                self.urls_vues.add(film_url)
            yield response.follow(film_url, callback=self.parse_movie)
        page = response.meta.get('current_page', 0)
        page_suivante = page + 30 # 30 films par pages
        if page_suivante < 10000: # Un peu moins de 10 000 pages au total
            url_page_suivante = f"https://www.jpbox-office.com/v9_demarrage.php?view=2&filtre=classg&limite={page_suivante}&infla=0&variable=0&tri=champ0&order=DESC&limit5=0"
            yield scrapy.Request(url_page_suivante, callback=self.parse, meta={'current_page': page_suivante})


    def parse_movie(self, response):
        movie_item = JpboxItem()
        movie_item['url'] = response.url
        movie_item['title'] = response.xpath('//h1/text()').get()
        movie_item['director'] = response.css('table.table_2022titre h4 a::text').get()
        movie_item['country'] = response.css('table.table_2022titre h3 a::text').get()
        movie_item['genre'] = response.css('table.table_2022titre h3 a:nth-of-type(2)::text').get()
        movie_item['date'] = response.xpath('//table[@class="tablelarge1"]//div//p//a/text()').get()
        movie_item['studio'] = response.xpath('//h3[text()="Distribué par"]/following-sibling::text()[1]').get()
        movie_item['first_week_entries'] = response.xpath("//table[contains(@class, 'tablesmall') and contains(@class, 'tablesmall2')]/tr[9]/td[contains(@class, 'col_poster_contenu_majeur')]/text()").get()
        movie_item['first_week_weight'] = response.xpath("//table[contains(@class, 'tablesmall') and contains(@class, 'tablesmall2')]/tr[9]/td[3]/text()").get()
        movie_item['copies'] = response.xpath("//table[contains(@class, 'tablesmall') and contains(@class, 'tablesmall5')]/tr[3]/td[6]/text()").get()
        movie_item['casting'] = response.xpath('//div[5]/div[1]/ul/li[6]/a/text()')[1].extract().strip()
        movie_item['franchise'] = response.xpath('//div[@id="nav2"]//ul//a[contains(text(), "Franchise")]/text()').get()
        movie_item['remake'] = response.xpath('//div[@id="nav2"]//ul//a[contains(text(), "Remake")]/text()').get()
        
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
            yield response.follow(casting_url, callback=self.parse_casting, meta={'movie_item': movie_item})


    def parse_casting(self, response):
        movie_item = response.meta['movie_item']
        movie_item['actors'] = response.xpath('//tr[@valign="top"]/td[contains(@class, "col_poster_titre")]/h3/a[@itemprop="name"]/text()').getall()
        movie_item['producer'] = response.xpath('//tr/td[contains(@class, "col_poster_titre") and @itemprop="producer"]/h3/a[@itemprop="name"]/text()').get()
        movie_item['composer'] = response.xpath('//tr/td[contains(@class, "col_poster_titre") and @itemprop="compositor"]/h3/a[@itemprop="name"]/text()').get()
        yield movie_item