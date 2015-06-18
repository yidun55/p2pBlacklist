#coding:utf-8

"""
  从贷联盟上爬取网贷黑名单详细信息的url
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
    #download_delay=2
    name = 'dai_list'
    start_urls = ['http://www.dailianmeng.com/p2pblacklist/index.html']
    allowed_domains = ['dailianmeng.com']
    myRedis = redis.StrictRedis(host='localhost',port=6379) #connected to redis
    def __inti__(self):
        pass

    def make_requests_from_url(self, url):
        return Request(url, callback=self.gettotal, dont_filter=True)

    def gettotal(self, response):
        """
        extract pages from different years
        """
        sel = response.selector
        total_pages = sel.xpath(u"//a[contains(text(),'末页')]\
            /@href").re(u"page=([\d]*)")
        url = 'http://www.dailianmeng.com/p2pblacklist/index.html?P2pBlacklist_page='
        urls = [url+str(page) for page in xrange(1,(int(total_pages)+1))]
        for url in urls[1:2]:
            # print url, "year url"
            yield Request(url, callback=self.detail_url, dont_filter=True)

    def detail_url(self, response):
        """
        extract url for detail information and store it into 
        redis
        """
        sel = response.selector
        detail_url = sel.xpath(u"//a[contains(text(),'查看详情')]/@href").extract()
        url = 'http://www.dailianmeng.com'
        urls = [url+i for i in detail_url]
        redis_key = 'dai_lian_meng_redis_spider:start_urls' 
        #redis_key是根据redisPpdaiScrapy.py中的redis_key设定的
        for url in urls:
            self.__class__.myRedis.lpush(redis_key, url)