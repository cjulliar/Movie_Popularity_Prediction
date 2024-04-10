# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class scrapperItem(scrapy.Item):
    titre = scrapy.Field()
    href = scrapy.Field()


   
class ImdbscrapperItem(scrapy.Item):
    titre = scrapy.Field()
    score = scrapy.Field()
    nbre_vote = scrapy.Field()
    genres = scrapy.Field()
    langue = scrapy.Field()
    pays = scrapy.Field()
    pegi = scrapy.Field()
    duree = scrapy.Field()
    annee = scrapy.Field()
    popularite_score = scrapy.Field()
    director = scrapy.Field()
    scenaristes = scrapy.Field()
    casting_principal = scrapy.Field()
    casting_complet = scrapy.Field()
    budget = scrapy.Field()
    
class InfosMovies(scrapy.Item):
    image_urls = scrapy.Field()  
    titre = scrapy.Field()
    timing = scrapy.Field()
    director = scrapy.Field()
    actors = scrapy.Field()
    nationalite = scrapy.Field()
    studio = scrapy.Field()
    titre_original = scrapy.Field()
    semaine_fr = scrapy.Field()
    entrees_fr = scrapy.Field()
    semaine_usa = scrapy.Field()
    entrees_usa = scrapy.Field()


class ImdbItem(scrapy.Item):
    titre = scrapy.Field()
    score = scrapy.Field()
    nbre_vote = scrapy.Field()
    genre = scrapy.Field()
    langue = scrapy.Field()
    pays = scrapy.Field()
    pegi = scrapy.Field()
    duree = scrapy.Field()
    annee = scrapy.Field()
    image_urls = scrapy.Field()
    popularite_score = scrapy.Field()
    director = scrapy.Field()
    scenaristes = scrapy.Field()
    casting_principal = scrapy.Field()
    budget = scrapy.Field()
    release_link = scrapy.Field()
    release_link_full = scrapy.Field()
    release_date_france = scrapy.Field()
    url = scrapy.Field()
    nombre_vote = scrapy.Field()


class ImdbproItem(scrapy.Item):
    titre = scrapy.Field()

class Imdbpro2Item(scrapy.Item):
    titre = scrapy.Field()
    year_and_classification = scrapy.Field()
    year = scrapy.Field()
    duration = scrapy.Field()
    genres = scrapy.Field()
    director = scrapy.Field()
    writer = scrapy.Field()
    budget = scrapy.Field()
    release_date = scrapy.Field()

