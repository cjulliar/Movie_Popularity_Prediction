# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


   
class ImdbscrapperItem(scrapy.Item):
    titre = scrapy.Field()
    date = scrapy.Field()
    budget = scrapy.Field()
    genres = scrapy.Field()
    pays = scrapy.Field()
    nationalite = scrapy.Field()
    duree = scrapy.Field()
    franchise = scrapy.Field()
    remake = scrapy.Field()
    popularite_score = scrapy.Field()
    score = scrapy.Field()
    nombre_vote = scrapy.Field()
    semaine_fr = scrapy.Field()
    semaine_usa= scrapy.Field()
    entrees_fr = scrapy.Field()
    entrees_usa = scrapy.Field()
    langue = scrapy.Field()
    pegi_fr = scrapy.Field()
    pegi_usa = scrapy.Field()
    annee = scrapy.Field()
    director = scrapy.Field()
    scenaristes = scrapy.Field()
    casting_principal = scrapy.Field()
    casting_complet = scrapy.Field()
    actors = scrapy.Field()
    studio = scrapy.Field()
    titre_original = scrapy.Field()
    url = scrapy.Field()
    release_link = scrapy.Field()
    image_urls = scrapy.Field()
    producteur = scrapy.Field()
    acteurs = scrapy.Field()


class JpboxofficeItem(scrapy.Item):
    url = scrapy.Field()
    titre = scrapy.Field()
    realisateur = scrapy.Field()
    pays = scrapy.Field()
    date_sortie_fr = scrapy.Field()
    genres = scrapy.Field()
    studio = scrapy.Field()
    franchise = scrapy.Field()
    entrees_fr = scrapy.Field()
    duree = scrapy.Field()
    pegi_fr = scrapy.Field()
    salle_fr = scrapy.Field()
    acteurs = scrapy.Field()
    producteur = scrapy.Field()
    compositeur = scrapy.Field()
    budget = scrapy.Field()
    pegi_us = scrapy.Field()
    date_sortie_us = scrapy.Field()
    entrees_usa = scrapy.Field()