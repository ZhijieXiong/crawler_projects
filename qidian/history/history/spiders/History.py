# -*- coding: utf-8 -*-
import scrapy
import re
import os
import requests
from fontTools.ttLib import TTFont
from history.items import BookItem

# 获取下一页的url：list(response.xpath('//a[@class="lbf-pagination-next "]/@href').get())
# 每本书的详细信息：
# 书名：list(map(lambda e: e.get(), list(response.xpath('//div[@class="all-book-list"]//li[@data-rid]//h2/a/text()'))))
# 标签：list(map(lambda e: e.get(), list(response.xpath('//div[@class="all-book-list"]//li[@data-rid]//p[@class="author"]/a[@class="go-sub-type"]/text()'))))
# 详细内容链接：list(map(lambda e: e.get(), list(response.xpath('//div[@class="all-book-list"]//li[@data-rid]//h2/a/@href'))))
# 简介：list(map(lambda e: e.get(), list(response.xpath('//div[@class="all-book-list"]//li[@data-rid]//p[@class="intro"]/text()'))))

cur_path = os.path.abspath(".")
font_file_path = os.path.join(cur_path, "qidian.woff")


class HistorySpider(scrapy.Spider):
    # 爬虫的名字
    name = "History"
    # 允许请求的域名
    # allowed_domains = ["www.qidian.com", "book.qidian.com"]
    # 最开始请求的url地址，会交给parse
    # start_urls = ["https://www.qidian.com/all/chanId5/"]
    # 代理网站：https://www.zdaye.com/shanghai_ip.html#Free
    proxy = "http://106.54.141.54:3128"
    https_proxy = "http://120.42.46.226:6666"

    def start_requests(self):
        urls = ["https://www.qidian.com/all/chanId5/"] + [f"https://www.qidian.com/all/chanId5-page{n}/" for n in range(2, 6)]
        for url in urls:
            yield scrapy.Request(url, callback=self.parse, meta={"proxy": self.https_proxy})

    def parse(self, response):
        book_list = response.xpath('//li[@data-rid]//div[@class="book-mid-info"]/h2/a')
        for book in book_list:
            detail_url = "https:" + book.attrib["href"]
            name = book.xpath("text()").get()
            yield scrapy.Request(
                url=detail_url,
                callback=self.parse_detail,
                dont_filter=True,
                meta={"name": name, "proxy": self.https_proxy},
            )

    def parse_detail(self, response):
        # 获取包含字体文件链接的style标签内容
        style = response.xpath('//div[@class="book-info "]//style/text()')[0].extract()
        # 字体文件是随机的，每次使用的字体文件不一样，所以必须动态处理
        # link1 = re.search("https:\/\/([\w.]+\/?)\S*eot", content).group()
        # link2 = re.search("https:\/\/([\w.]+\/?)\S*woff", content).group()
        link3 = re.search("https:\/\/([\w.]+\/?)\S*ttf", style).group()
        # 获取字体文件，并保存到本地
        font_content = requests.get(
            url=link3, proxies={"https": self.https_proxy}, verify=False
        ).content
        with open(font_file_path, "wb") as f:
            f.write(font_content)
        font = TTFont(font_file_path)
        font_dic1 = font.getBestCmap()
        font_dic2 = {
            "period": ".",
            "zero": "0",
            "one": "1",
            "two": "2",
            "three": "3",
            "four": "4",
            "five": "5",
            "six": "6",
            "seven": "7",
            "eight": "8",
            "nine": "9",
        }
        # 数字的编码，需要用字体文件解码
        target = list(
            re.findall(
                re.compile(
                    r'<div class="book-info ">.*?<p>.*?<span class=".*?">(.*?)</span>.*?<span class=".*?">(.*?)</span>.*?<span class=".*?">(.*?)</span>.*?<span class=".*?">(.*?)</span>',
                    re.S,
                ),
                response.text,
            )[0]
        )
        units_10000 = list(
            re.findall(
                re.compile(
                    r'<div class="book-info ">.*?<p>.*?<cite>(.*?)</cite>.*?<cite>(.*?)</cite>.*?<cite>(.*?)</cite>.*?<cite>(.*?)</cite>.*?<cite>(.*?)</cite>',
                    re.S,
                ),
                response.text,
            )[0]
        )
        
        # 判断对应数据是否以万为单位
        units_10000 = units_10000[0:1] + units_10000[3:5]
        for i in range(len(units_10000)):
            units_10000[i] = units_10000[i][0] == '万'

        # 解码 
        del target[1]
        data = []
        for e in target:
            l = e.split(";")
            l = l[0 : len(l) - 1]
            l = list(map(lambda s: int(s.replace("&#", "")), l))
            l = list(map(lambda n: font_dic2[font_dic1[n]], l))
            data.append("".join(l))

        item = BookItem()
        item["monthly_ticket_ranking"] = response.xpath('//*[@id="ticket-wrap"]/div[1]/p[3]/text()').getall()[0]
        
        item["data"] = data
        item['data_10000_units'] = units_10000
        item["name"] = response.meta["name"]
        item["detail_url"] = response.url
        item["intro"] = response.xpath(
            '//div[@class="book-intro"]/p/text()'
        ).getall()
        item["labels"] = response.xpath('//p[@class="tag"]/a/text()').getall()
        item["author"] = response.xpath('//span/a[@class="writer"]/text()').get()
        yield item
