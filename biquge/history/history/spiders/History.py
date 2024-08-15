# -*- coding: utf-8 -*-
import scrapy
from history.items import BookItem


class HistorySpider(scrapy.Spider):
    name = "History"
    proxy = "http://124.204.33.162:8000"
    # allowed_domains = ['www.gebiqu.com']
    # start_urls = ['http://www.gebiqu.com/']

    def start_requests(self):
        urls = [f"http://www.gebiqu.com/lishijunshi/{n}.html" for n in range(1, 389)]
        for url in urls:
            yield scrapy.Request(
                url=url, callback=self.parse, meta={"proxy": self.proxy}
            )

    def parse(self, response):
        book_list = response.xpath('//div[@class="l"]//span[@class="s2"]//a')
        for book in book_list:
            detail_url = "http://www.gebiqu.com" + book.attrib["href"]
            name = book.xpath("text()").get()
            yield scrapy.Request(
                url=detail_url,
                callback=self.parse_detail,
                meta={"name": name, "proxy": self.proxy},
            )

    def parse_detail(self, response):
        item = BookItem()
        item["name"] = response.meta["name"]
        item["intro"] = response.xpath('//div[@id="intro"]/p/text()').get()
        yield item
