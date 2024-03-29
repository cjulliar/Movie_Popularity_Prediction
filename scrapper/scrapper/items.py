# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class scrapperItem(scrapy.Item):
    title = scrapy.Field()
    href = scrapy.Field()


class BoxOfficeItem(scrapy.Item):
    
    film_title = scrapy.Field()
    semaine_fr = scrapy.Field()
    entrees_fr = scrapy.Field()
    semaine_usa = scrapy.Field()
    entrees_usa = scrapy.Field()
    
    
class InfosMovies(scrapy.Item):
    image_urls = scrapy.Field()  
    title = scrapy.Field()
    timing = scrapy.Field()
