# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

# 这里写预先定义的数据格式
class BookItem(scrapy.Item):
    name = scrapy.Field()
    intro = scrapy.Field()
    labels = scrapy.Field()
    data = scrapy.Field()
    detail_url = scrapy.Field()
    data_10000_units = scrapy.Field()
    monthly_ticket_ranking = scrapy.Field()
    author = scrapy.Field()
