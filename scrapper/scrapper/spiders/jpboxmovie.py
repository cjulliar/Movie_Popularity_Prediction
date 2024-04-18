import scrapy

from scrapper.items import JpboxofficeItem


class JpspiderSpider(scrapy.Spider):
    name = "jpspider"
    allowed_domains = ["jpbox-office.com"]
    start_urls = ["https://www.jpbox-office.com/v9_demarrage.php?view=2"]
    urls_vues = set()
    
    
    
    def parse(self, response):
        # Log info pour signaler le début de l'analyse
        self.logger.info("Début de l'analyse de la page principale: %s", response.url)

        # Sélectionne la table contenant les films
        movies = response.xpath("/html/body/div[5]/table[2]")

        # Base URL pour les films
        url_base = "https://www.jpbox-office.com/"

        for movie in movies:
            # Extraction de l'URL du film
            movie_url = movie.xpath('.//h3/a/@href').getall()
 
            self.logger.info("URLs des films extraites : %s", movie_url)

            # Vérifie s'il y a des URLs de film extraites
            if movie_url:
                for url in movie_url:
                    # Construit l'URL complète du film
                    movie_full_url = url_base + url
                    self.logger.info("URL complète du film : %s", movie_full_url)

                    # Vérifie si l'URL a déjà été visitée
                    if movie_full_url in self.urls_vues:
                        continue  # Passe à la prochaine URL
                        
                    # Ajoute l'URL à l'ensemble des URL visitées
                    else:
                        self.urls_vues.add(movie_full_url)


                    # Envoie une requête pour analyser la page du film
                    yield scrapy.Request(movie_full_url, callback=self.parse_movie_page)
            self.logger.warning("Aucune URL de film trouvée dans la ligne : %s", movie.extract())


        current_page = response.meta.get('current_page', 0)
        next_page = current_page + 30

        if next_page < 10000:
            next_page_url = f"https://www.jpbox-office.com/v9_demarrage.php?view=2&filtre=classg&limite={next_page}&infla=0&variable=0&tri=champ0&order=DESC&limit5=0"
            yield scrapy.Request(next_page_url, callback=self.parse, meta={'current_page': next_page})


    def parse_movie_page(self, response):
        # Log info pour signaler le début de l'analyse d'une page de film
        self.logger.info("Début de l'analyse de la page du film: %s", response.url)
        movie_item = JpboxofficeItem()


        movie_item['url'] = response.url
        movie_item['titre'] = response.xpath('//h1/text()').get()
        movie_item['realisateur'] = response.css('table.table_2022titre h4 a::text').get()
        movie_item['pays'] = response.css('table.table_2022titre h3 a::text').get()
        movie_item['date_sortie_fr'] = response.xpath('//table[@class="tablelarge1"]//div//p//a/text()').get()
        movie_item['genres'] = response.css('table.table_2022titre h3 a:nth-of-type(2)::text').get()
        movie_item['studio'] = response.xpath('//h3[text()="Distribué par"]/following-sibling::text()[1]')[-1].get()
        movie_item['franchise'] = response.xpath('//div[@id="nav2"]//ul//a[contains(text(), "Franchise")]/text()').get()
        movie_item['entrees_fr'] = response.css('table.tablesmall.tablesmall2 tr:last-child  td.col_poster_contenu_majeur::text').get()
        movie_item['duree'] = response.xpath('//*[@id="content"]//td[2]/h3/text()[4]').get()
        movie_item['pegi_fr'] = response.css('.tablelarge1 .bloc_infos_center.tablesmall1:last-child::text').get()

        a_p = response.xpath('normalize-space(//table[@class="tablesmall tablesmall5"]//tr//td[@class="col_poster_contenu_majeur"]//strong/text())').get()
        first_week = response.xpath('normalize-space(//table[@class="tablesmall tablesmall5"]//tr//td[@class="col_poster_contenu_majeur"]//strong/a/text())').get()

        if "A-p" in a_p:
            movie_item['salle_fr'] = response.xpath('//table[@class="tablesmall tablesmall5"]//tr[3]//td[6]/text()').get()
        elif "1" in first_week:
            movie_item['salle_fr'] = response.xpath('//table[@class="tablesmall tablesmall5"]//tr[2]//td[6]/text()').get() 
        
        
        recettes_us = response.xpath('//*[@id="nav2"]/ul/li[4]/ul/li/a/@href').get()
        yield response.follow(recettes_us, callback=self.parse_pegi, meta={'movie_item': movie_item})

        
        li5_text = response.xpath('//*[@id="nav2"]/ul/li[5]/a/text()')
        if li5_text:
            li5_text = li5_text.getall()[-1]
        else:
            li5_text = ""

        li6_text = response.xpath('//*[@id="nav2"]/ul/li[6]/a/text()')
        if li6_text:
            li6_text = li6_text.getall()[-1]
        else:
            li6_text = ""

        casting_url = None
        if "Casting" in li5_text:
            casting_url = response.xpath('//*[@id="nav2"]/ul/li[5]/a/@href').get()
            li6_text = ""
        elif "Casting" in li6_text:
            casting_url = response.xpath('//*[@id="nav2"]/ul/li[6]/a/@href').get()
            li5_text = ""

        if casting_url:
            yield response.follow(casting_url, callback=self.parse_casting, meta={'movie_item': movie_item})


        budget_url = response.xpath('//*[@id="nav2"]/ul/li[1]/a/@href').get()
        yield response.follow(budget_url, callback=self.parse_budget, meta={'movie_item' : movie_item})
 

    def parse_casting(self, response):
        # Log info pour signaler le début de l'analyse de la page de casting
        self.logger.info("Début de l'analyse de la page de casting: %s", response.url)

        #'response.meta' pour accéder aux métadonnées transmises
        movie_item = response.meta['movie_item']
        movie_item['acteurs'] = response.xpath('//tr[@valign="top"]/td[contains(@class, "col_poster_titre")]/h3/a[@itemprop="name"]/text()').getall()
        movie_item['producteur'] = response.xpath('//tr/td[contains(@class, "col_poster_titre") and @itemprop="producer"]/h3/a[@itemprop="name"]/text()').get()
        movie_item['compositeur'] = response.xpath('//tr/td[contains(@class, "col_poster_titre") and @itemprop="compositor"]/h3/a[@itemprop="name"]/text()').get()
        yield movie_item

    def parse_budget(self, response):
        # Log info pour signaler le début de l'analyse de la page de budget
        self.logger.info("Début de l'analyse de la page de budget: %s", response.url)

        movie_item = response.meta['movie_item']
        movie_item['budget'] = response.css('table.tablesmall.tablesmall1b tr td div strong::text').get()
        
        yield movie_item

    def parse_pegi(self, response):
        self.logger.info("Début de l'analyse pegi US :  %s", response.url)
        
        movie_item = response.meta['movie_item']

        movie_item['pegi_us'] = response.css('.tablelarge1 .bloc_infos_center.tablesmall1:last-child').get()
        movie_item['date_sortie_us'] = response.xpath('//table[@class="tablelarge1"]//a/text()').get()
        # movie_item['recette_premier_wk_US'] = response.xpath('//div[@align="center"]//tr[13]/td[@class="col_poster_contenu_majeur"]/text()').get()
        movie_item['entrees_usa'] = response.xpath('//td[@class="col_poster_titre" and h4[contains(text(), "Week-End")]]/following-sibling::td[@class="col_poster_contenu_majeur"]/text()').get()
        yield movie_item
