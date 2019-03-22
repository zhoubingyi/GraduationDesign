import requests
from bs4 import BeautifulSoup
# from os import path
# from wordcloud import WordCloud, ImageColorGenerator
# import jieba.analyse
# import matplotlib.pyplot as plt
# from scipy.misc import imread
import time
from pymongo import MongoClient



class HouseSpider:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.zfdb = self.client.zfdb

    session = requests.Session()
    baseUrl = "http://dl.zu.fang.com"

    # 每个区域的url
    urlDir = {
        "不限": "/house/",
        "中山": "/house-a0256/",
        "西港": "/house-a0255/",
        "沙口子": "/house-a0257/",
        "甘井子": "/house-a0258/",
        "高新园区": "/house-a011193/",
        "开发区": "/house-a0261/",
        "旅顺口": "/house-a0259/",
        "瓦房店": "/house-a01121/",
        "普兰店": "/house-a01122/",
        "庄河": "/house-a01124/",
    }

    region = "不限"
    page = 100
    # 通过名字获取 url 地址
    def getRegionUrl(self, name="中山", page=10):
        urlList = []
        for index in range(page):
            if index == 0:
                urlList.append(self.baseUrl + self.urlDir[name])
            else:
                urlList.append(self.baseUrl + self.urlDir[name] + "i3" + str(index + 1) + "/")
        return urlList


    # MongoDB 存储数据结构
    def getRentMsg(self, title, rooms, area, price, address, traffic, region, direction):
        return {
            "title": title,  # 标题
            "rooms": rooms,  # 房间数
            "area": area,  # 平方数
            "price": price,  # 价格
            "address": address,  # 地址
            "traffic": traffic,  # 交通描述
            "region": region,  # 区、（福田区、南山区）
            "direction": direction,  # 房子朝向（朝南、朝南北）
        }

    # 获取数据库 collection
    def getCollection(self, name):
        zfdb = self.zfdb
        if name == "不限":
            return zfdb.rent
        if name == "中山":
            return zfdb.zhongshan
        if name == "西港":
            return zfdb.xigang
        if name == "沙口子":
            return zfdb.shakouzi
        if name == "甘井子":
            return zfdb.ganjingzi
        if name == "高新园区":
            return zfdb.gaoxingyuanqu
        if name == "开发区":
            return zfdb.kaifaqu
        if name == "旅顺口":
            return zfdb.lvshunkou
        if name == "瓦房店":
            return zfdb.wafangdian
        if name == "普兰店":
            return zfdb.pulandian
        if name == "庄河":
            return zfdb.zhuanghe

    #
    def getAreaList(self):
        return [
            "不限",
            "中山",
            "西港",
            "沙口子",
            "甘井子",
            "高新园区",
            "开发区",
            "旅顺口",
            "瓦房店",
            "普兰店",
            "庄河",
        ]

    def getOnePageData(self, pageUrl, reginon="不限"):
        rent = self.getCollection(self.region)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'})
        res = self.session.get(
            pageUrl
        )
        soup = BeautifulSoup(res.text, "html.parser")
        # 获取需要爬取得 div
        divs = soup.find_all("dd", attrs={"class": "info rel"})

        for div in divs:
            ps = div.find_all("p")
            try:  # 捕获异常，因为页面中有些数据没有被填写完整，或者被插入了一条广告，则会没有相应的标签，所以会报错
                for index, p in enumerate(ps):  # 从源码中可以看出，每一条 p 标签都有我们想要的信息，故在此遍历 p 标签，
                    text = p.text.strip()
                    print(text)  # 输出看看是否为我们想要的信息
                print("===================================")
                # 爬取并存进 MongoDB 数据库
                roomMsg = ps[1].text.split("|")
                # rentMsg 这样处理是因为有些信息未填写完整，导致对象报空
                area = roomMsg[2].strip()[:len(roomMsg[2]) - 2]
                # 标题 房间数 平方数 价格 地址 交通描述 区 房子朝向
                rentMsg = self.getRentMsg(
                    ps[0].text.strip(),
                    roomMsg[1].strip(),
                    int(float(area)),
                    int(ps[len(ps) - 1].text.strip()[:len(ps[len(ps) - 1].text.strip()) - 3]),
                    ps[2].text.strip(),
                    ps[3].text.strip(),
                    ps[2].text.strip()[:2],
                    roomMsg[3],
                )
                # 插入到数据库中
                rent.insert(rentMsg)
            except:
                continue

    # 设置区域
    def setRegion(self, region):
        self.region = region

    # 设置页数
    def setPage(self, page):
        self.page = page

    def startSpicder(self):
        for url in self.getRegionUrl(self.region, self.page):
            self.getOnePageData(url, self.region)
            print("*" * 30 + "one page 分割线" + "*" * 30)
            time.sleep(1)


spider = HouseSpider()
spider.setPage(50)# 设置爬取页数
for i in range(0,11):
    spider.setRegion(spider.getAreaList()[i]) # 设置爬取区域
    spider.startSpicder()# 开启爬虫
