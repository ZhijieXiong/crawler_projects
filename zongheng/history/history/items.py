# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    intro = scrapy.Field()
    labels = scrapy.Field()
    data = scrapy.Field()
    detail_url = scrapy.Field()
    author = scrapy.Field()
    comment_number = scrapy.Field()
    book_id = scrapy.Field()
