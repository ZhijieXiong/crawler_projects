# -*- coding: utf-8 -*-
import scrapy
import re
import requests
import json
import random


from history.items import BookItem


class HistorySpider(scrapy.Spider):
    name = "History"
    # allowed_domains = ["book.zongheng.com"]
    # start_urls = [
    #     "http://book.zongheng.com/store/c6/c1062/b0/u1/p1/v9/s9/t0/u0/i0/ALL.html/"
    # ]
    proxy = "http://106.54.141.54:3128"
    https_proxy = "http://120.42.46.226:6666"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36",
        "Host": "forum.zongheng.com",
        "Referer": "http://book.zongheng.com/",
    }

    def start_requests(self):
        urls = [
            f"http://book.zongheng.com/store/c6/c1062/b0/u1/p{n}/v9/s9/t0/u0/i0/ALL.html/"
            for n in range(1, 27)
        ]
        for url in urls:
            yield scrapy.Request(
                url=url, callback=self.parse, meta={"proxy": self.proxy}
            )

    def parse(self, response):
        book_list = response.xpath('//span[@class="bookname"]//a')
        for book in book_list:
            detail_url = book.attrib["href"]
            name = book.xpath("text()").get()
            yield scrapy.Request(
                url=detail_url,
                callback=self.parse_detail,
                dont_filter=True,
                meta={
                    "name": name,
                    "proxy": self.proxy,
                },
            )

    def parse_detail(self, response):
        book_id = response.xpath("body").attrib["bookid"]
        item = BookItem()
        item["book_id"] = book_id
        item["name"] = response.meta["name"].strip()
        item["detail_url"] = response.url
        item["data"] = response.xpath('//div[@class="nums"]//i/text()').getall()
        item["intro"] = response.xpath(
            '//div[@class="book-dec Jbook-dec hide"]//p/text()'
        ).getall()
        item["labels"] = response.xpath(
            '//div[@class="book-label"]/span/a/text()'
        ).getall()
        item["author"] = (
            response.xpath('//div[@class="au-name"]/a/text()').get().strip()
        )

        yield scrapy.Request(
            url="https://forum.zongheng.com/api/forums/postlist?bookId={}&forumType=4".format(
                book_id
            ),
            headers=self.headers,
            callback=self.parse_comment_number,
            dont_filter=True,
            meta={"item": item, "proxy": self.https_proxy, "book_id": book_id},
        )

    def parse_comment_number(self, response):
        item = response.meta["item"]
        comment_number = re.findall('"threadNum":(\d*)', response.text)[0]
        if comment_number == None:
            item["comment_number"] = 0
        else:
            item["comment_number"] = int(comment_number)
        yield item
