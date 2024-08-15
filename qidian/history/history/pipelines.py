# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import time
import json
from history.items import BookItem
import re


class HistoryPipeline(object):
    def __init__(self):
        self.items = []
        self.count = 1
        pass

    def process_item(self, item, spider):
        if isinstance(item, BookItem):
            item["data"] = self.process_data(item["data"], item["data_10000_units"])
            item["intro"] = self.process_intro(item["intro"])
            item["monthly_ticket_ranking"] = int(re.search("\d+", item["monthly_ticket_ranking"]).group())
            self.items.append(dict(item))
            print(self.count,item)
            self.count += 1
            return item

    def open_spider(self, spider):
        self.file = open(
            "qidian-" + time.strftime("%Y-%m-%d") + ".json",
            mode="w",
            encoding="utf-8",
        )
        pass

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

    def process_data(self, data, units):
        obj = {}
        keys = ["total_words", "total_recommend", "week_recommend"]
        for i in range(3):
            num = data[i]
            if units[i]:
                obj[keys[i]] = int(float(num[0 : len(num) - 1]) * 10000)
            else:
                obj[keys[i]] = int(num)
        return obj
    
