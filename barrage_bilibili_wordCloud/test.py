import requests
import wordcloud
import jieba
from lxml import etree


def getUrl(url_oid):
    '''
    获取网页url
    :param url_oid: B站视频的oid/cid，用于获取弹幕xml文件的url
    :return: 返回弹幕文件的链接
    '''
    url1 = "https://comment.bilibili.com/"
    url3 = ".xml"
    url = url1 + url_oid + url3
    return url


def getBulletScreen(url):
    '''
    获取弹幕的数据
    :param url: 弹幕文件的链接
    :return: 返回弹幕数据，为列表
    '''
    response = requests.get(url)
    html = etree.HTML(response.content)
    data_list = html.xpath('//d//text()')
    return data_list


def removeDoubleBarrage(data_list):
    '''
    数据去重
    :param data_list: 数据，要求为列表
    :return:
        double_barrage: 重复弹幕的集合
        results：去重后的弹幕
        barrage：每种弹幕内容都存储一遍（只出现了一次的弹幕不会存到里面）
    '''
    double_barrage = []
    results = []
    barrage = set()
    for result in data_list:
        if result not in results:
            results.append(result)
        else:
            double_barrage.append(result)
            barrage.add(result)
    return double_barrage, results, barrage


def makeWordCould(data_list):
    '''
    根据数据（列表）生成词云
    :param data_list: 数据，要求为列表
    :return:无
    '''
    double_barrages, results, barrages = removeDoubleBarrage(data_list)

    # 重词计数，结果写进txt文件
    with open('./barrages.txt', 'w') as f:
        for barrage in barrages:
            # 数量的统计
            amount = double_barrages.count(barrage)
            f.write(barrage + ':' + str(amount + 1) + '\n')

    frequencies = {}
    for line in open("./barrages.txt"):
        arr = line.split(":")
        frequencies[arr[0]] = float(arr[1])

    # 设置停用词
    # stop_words = ['【', '】', ',', '.', '?', '!', '。']
    # words = []
    # if results:
    #     for result in results:
    #         for stop in stop_words:
    #             # 去除上面的停用词，再拼接成字符串
    #             result = ''.join(result.split(stop))
    #         words.append(result)
    #     words = ''.join(words)
    #     words = jieba.cut(words)
    #     words = ''.join(words)

    w = wordcloud.WordCloud(font_path='./华文行楷.ttf', background_color='white', width=1600, height=1600, max_words=50)
    w.generate_from_frequencies(frequencies)  # 根据词频生成词云
    w.to_file('./词云.jpg')


def main():
    url_oid = input("请输入cid：")
    url = getUrl(url_oid)
    bullet_screen_list = getBulletScreen(url)
    makeWordCould(bullet_screen_list)


if __name__ == "__main__":
    main()