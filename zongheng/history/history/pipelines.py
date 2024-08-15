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
            item["data"] = self.process_data(item["data"])
            item["intro"] = self.process_intro(item["intro"])
            self.items.append(dict(item))
            print(item)
            return item

      
    def open_spider(self, spider):
        self.file = open('zongheng-' + time.strftime("%Y-%m-%d") + ".json", mode="w", encoding='utf-8')
      
    def close_spider(self, spider):
        self.file.write(json.dumps(self.items))
        self.file.close()
      
    def process_intro(self, intro):
        intro_lines = []
        for line in intro:
            if line.find("读者") < 0:
                intro_lines.append('    ' + line.strip())
        s = '\n'.join(intro_lines)
        return s
      
    def process_data(self, data):
        obj = {}
        keys = ["total_recommend", "total_click", "week_recommend"]
        for i in range(3):
            num = data[i + 1]
            if num.find("万") < 0:
                obj[keys[i]] = int(num)
            else:
                obj[keys[i]] = int(float(num[0:len(num)-1]) * 10000)
        return obj
