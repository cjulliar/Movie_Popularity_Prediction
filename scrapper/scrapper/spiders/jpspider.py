import scrapy

from scrapper.items import JpboxofficeItem


class JpspiderSpider(scrapy.Spider):
    name = "jpspider"
    allowed_domains = ["jpbox-office.com"]
    start_urls = ["https://www.jpbox-office.com/v9_demarrage.php?view=2"]
    urls_vues = set()
    
    custom_settings = {
    'FEEDS' : {
        'moviesdata.csv' : {'format' : 'csv', 'overwrite' : True},
    }
    }
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
            # entrees_premiere_semaine = response.css('table.tablesmall.tablesmall5 tr td.col_poster_contenu_majeur::text').get()
            # salles_premiere_semaine = response.css('table.tablesmall.tablesmall5 tr:nth-child(2) td:nth-child(7)::text').get()
            # movie_item['entrees_premiere_semaine'] = entrees_premiere_semaine
            # movie_item['salles_premiere_semaine'] = salles_premiere_semaine   
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

        # entrees_premiere_semaine = response.meta.get('entrees_premiere_semaine')
        # salles_premiere_semaine = response.meta.get('salles_premiere_semaine')


        movie_item['url'] = response.url
        movie_item['titre'] = response.xpath('//h1/text()').get()
        movie_item['realisateur'] = response.css('table.table_2022titre h4 a::text').get()
        movie_item['pays'] = response.css('table.table_2022titre h3 a::text').get()
        movie_item['date'] = response.xpath('//table[@class="tablelarge1"]//div//p//a/text()').get()
        movie_item['genre'] = response.css('table.table_2022titre h3 a:nth-of-type(2)::text').get()
        movie_item['studio'] = response.xpath('//h3[text()="Distribué par"]/following-sibling::text()[1]')[-1].get()
        movie_item['franchise'] = response.xpath('//div[@id="nav2"]//ul//a[contains(text(), "Franchise")]/text()').get()
        movie_item['remake'] = response.xpath('//div[@id="nav2"]//ul//a[contains(text(), "Remake")]/text()').get()
        movie_item['entrees_premiere_semaine'] = response.css('table.tablesmall.tablesmall2 tr:last-child  td.col_poster_contenu_majeur::text').get()
        movie_item['duree'] = response.xpath('//*[@id="content"]//td[2]/h3/text()[4]').get()
        # movie_item['salles_premiere_semaine'] = salles_premiere_semaine        
        
        li5_text = response.xpath('//*[@id="nav2"]/ul/li[5]/a/text()')[-1].extract()
        li6_text = response.xpath('//*[@id="nav2"]/ul/li[6]/a/text()')[-1].extract()

        if "Casting" in li5_text:
            casting_url = response.xpath('//*[@id="nav2"]/ul/li[5]/a/@href').get()
        elif "Casting" in li6_text:
            casting_url = response.xpath('//*[@id="nav2"]/ul/li[6]/a/@href').get()
        else:
            casting_url = None

        if casting_url:
            yield response.follow(casting_url, callback=self.parse_casting, meta={'movie_item': movie_item})


        budget_url = response.xpath('//*[@id="nav2"]/ul/li[1]/a/@href').get()
        yield response.follow(budget_url, callback=self.parse_budget, meta={'movie_item' : movie_item})

        # if casting_url:
        #     request = scrapy.Request(response.urljoin(casting_url), callback=self.parse_casting, meta={'movie_item': movie_item})
        #     request.meta['budget_url'] = budget_url  # Stockez l'URL AKA pour l'utiliser plus tard
        #     yield request
        # elif budget_url:  # Si la date de sortie n'est pas nécessaire ou absente
        #     yield scrapy.Request(response.urljoin(budget_url), callback=self.parse_budget, meta={'movie_item': movie_item})
        # else:
        # yield movie_item
 

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