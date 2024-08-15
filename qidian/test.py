# 测试解析动态反爬文字（应对情况：使用css3的font-face进行反爬）
import requests
from lxml import etree
import re
import os
from fontTools.ttLib import TTFont

# http连接太多没有关闭导致Max retries exceeded with url
# s = requests.session()
# s.keep_alive = False
# requests.adapters.DEFAULT_RETRIES = 5

# 使用代理：https://www.zdaye.com/shanghai_ip.html#Free
# s = requests.session()
# s.proxies = {
#   "https": "106.15.49.80:7890"
# }


cur_path = os.path.abspath(".")
font_file_path = os.path.join(cur_path, "qidian.woff")
url = "https://book.qidian.com/info/1028520538/"
header = {
    "authority": "book.qidian.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://www.qidian.com/",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cookie": "e1=%7B%22pid%22%3A%22qd_P_xiangqing%22%2C%22eid%22%3A%22%22%2C%22l1%22%3A2%7D; e2=%7B%22pid%22%3A%22qd_P_xiangqing%22%2C%22eid%22%3A%22%22%2C%22l1%22%3A2%7D; _yep_uuid=c447f999-d27a-49cd-5a1f-396b8bab6a10; _csrfToken=oWJeTvkoOwpyH5bUuzzwXma8tVERnPNHgyAgZW7m; newstatisticUUID=1641699146_1104576035; _ga_FZMMH98S83=GS1.1.1642567721.6.1.1642567728.0; _ga_PFYW0QLV3P=GS1.1.1642567721.6.1.1642567728.0; _ga=GA1.2.1105950373.1641699156; _gid=GA1.2.1694419802.1642567730; canShowGift=2022/1/19; giftToFly=1",
}
proxy = {"https": "114.88.242.234:55443"}


# 获取网页内容
res = requests.get(url, headers=header, proxies=proxy)
tree = etree.HTML(res.text)
# 获取包含字体文件链接的style标签内容
content = tree.xpath('//div[@class="book-info "]//style/text()')[0]
# 获取目标数字的编码（注意，这里不能用xpath提取，只能用正则表达式提取编码）
target = re.findall(
    re.compile(
        r'<div class="book-info ">.*?<p>.*?<span class=".*?">(.*?)</span>.*?<span class=".*?">(.*?)</span>.*?<span class=".*?">(.*?)</span>.*?<span class=".*?">(.*?)</span>',
        # r'<p>.*?<em>.*?<style>.*?</style>.*?<span class=".*?">(.*?)</span>',
        re.S,
    ),
    res.text,
)[0]
# 字体文件是随机的，每次使用的字体文件不一样，所以必须动态处理
# print(target)
# (
#     "&#100417;&#100410;&#100410;&#100414;&#100418;&#100413;",
#     "&#100418;",
#     "&#100416;&#100415;&#100414;&#100413;&#100409;",
#     "&#100411;&#100409;&#100413;&#100418;",
# )


# 获取字体文件链接
link1 = re.search("https:\/\/([\w.]+\/?)\S*eot", content).group()
link2 = re.search("https:\/\/([\w.]+\/?)\S*woff", content).group()
link3 = re.search("https:\/\/([\w.]+\/?)\S*ttf", content).group()
# 获取字体文件
font_content = requests.get(link3, headers=header, proxies=proxy).content
with open(font_file_path, "wb") as f:
    f.write(font_content)
font = TTFont(font_file_path)
# print(font.getGlyphOrder())
# ['.notdef', 'period', 'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
# print(font.getBestCmap())
# {
#     100407: "two",
#     100409: "four",
#     100410: "seven",
#     100411: "six",
#     100412: "three",
#     100413: "five",
#     100414: "period",
#     100415: "nine",
#     100416: "eight",
#     100417: "one",
#     100418: "zero",
# }
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


# 处理编码，把编码转换成数字
target = list(target)
del target[1]
data = []
for e in target:
    l = e.split(";")
    l = l[0 : len(l) - 1]
    l = list(map(lambda s: int(s.replace("&#", "")), l))
    l = list(map(lambda n: font_dic2[font_dic1[n]], l))
    data.append("".join(l))
print(data)
# ['177.05', '89.54', '6450']

