#coding:utf-8

"""
  从拍拍贷上爬取网贷黑名单
  author: 邓友辉
  email:heshang1203@sina.com
  date:2015/06/10
"""

from scrapy.spider import Spider
from scrapy.http import Request
from scrapy import log
import redis

from p2pBlacklist.items import *

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

class p2pBlacklist(Spider):
    download_delay=2
    name = 'pplist'
    start_urls = ['http://www.ppdai.com/blacklist/']
    allowed_domains = ['ppdai.com']
    myRedis = redis.StrictRedis(host='localhost',port=6379) #connected to redis
    def __init__(self):
        """
        将已下载数据的用户名加入redis set中以备下一步的
        url去重
        """
        file_path = "/home/dyh/data/blacklist/\
        ppai_blacklist1/ppai_blacklist"
        f = open(file_path, "r")
        self.dup_ppai_key = "ppai_dup_redis"
        for line in f:
            self.myRedis.sadd(self.dup_ppai_key,line.splite("\001")[8])


    def make_requests_from_url(self, url):
        return Request(url, callback=self.gettotal, dont_filter=True)

    def gettotal(self, response):
        """
        extract pages from different years
        """
        url = 'http://www.ppdai.com/blacklist/'
        years = xrange(2008,2016)
        urls = [url+str(year) for year in years]
        for url in urls:
            # print url, "year url"
            yield Request(url, callback=self.extract, dont_filter=True)

    def extract(self, response):
        """
        extract pages and then Request those pages sequecely
        """
        # print response.url,"extract response url"
        sel = response.selector
        pages = []
        try:
            # print "pages work"
            pages = sel.xpath("//div[contains(@class,'fen_ye_nav')]//td/text()").re(u"共([\d]{1,3})页")
            # print pages
        except Exception, e:
            print e,"error pages"
            log.msg(e, level=log.ERROR)
            log.msg(response.url, level=log.ERROR)

        if len(pages) == 0:
            self.getUserName(response)  #only one page
        else:
            for page in range(int(pages[0])+1)[1:]:
                url = response.url+"_m0_p"+str(page)
                yield Request(url, callback=self.getUserName,dont_filter=True)

    def getUserName(self, response):
        """
        get user name from xtml
        """
        sel = response.selector
        blackTr = sel.xpath(u"//table[contains(@class,'black_table')]/tr[position()>1]//p[contains(text(),'真实姓名')]/a/@href").extract()
        url = 'http://www.ppdai.com'
        urls = [url+i for i in blackTr]
        redis_key = 'ppai_blacklist_redis_spider:start_urls' 
        #redis_key是根据redisPpdaiScrapy.py中的redis_key设定的

        for url in urls:
            #如果redis set ppai_dup_redis没有则插入并返回1，否则
            #返回0
            isinserted = self.myRedis.sadd(self.dup_ppai_key,url.splite("/")[-1])
            if isinserted:
                self.__class__.myRedis.lpush(redis_key, url)



            











