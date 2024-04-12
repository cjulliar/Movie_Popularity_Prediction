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
    pegi = scrapy.Field()
    annee = scrapy.Field()
    director = scrapy.Field()
    scenaristes = scrapy.Field()
    casting_principal = scrapy.Field()
    casting_complet = scrapy.Field()
    
  

