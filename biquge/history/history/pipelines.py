# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import time
import json
from history.items import BookItem


class HistoryPipeline(object):
    def __init__(self):
        self.items = []
        pass
      
    def process_item(self, item, spider):
        if isinstance(item, BookItem):
            print(item)
            self.items.append(dict(item))
            return item

      
    def open_spider(self, spider):
        self.file = open('biquge-' + time.strftime("%Y-%m-%d") + ".json", mode="w", encoding='utf-8')
      
    def close_spider(self, spider):
        self.file.write(json.dumps(self.items))
        self.file.close()
      
   
     

