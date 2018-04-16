# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


import scrapy


class DouBanMovieItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    ranking = scrapy.Field()

    movie_name = scrapy.Field()

    score = scrapy.Field()

    score_num = scrapy.Field()


class BaiKeItem(scrapy.Item):
    name = scrapy.Field()

    descrip = scrapy.Field()

    infobox = scrapy.Field()

    tag = scrapy.Field()
    
    oid=scrapy.Field()

    infolink = scrapy.Field()


    polysemy = scrapy.Field()
    #
    # polysemy_href = scrapy.Field()
    # #多义词表
