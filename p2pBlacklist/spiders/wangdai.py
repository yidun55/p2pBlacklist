#coding:utf-8

"""
  从网贷上爬取网贷黑名单
  author: 邓友辉
  email:heshang1203@sina.com
  date:2015/06/14
"""

from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy import log

from p2pBlacklist.items import *

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

class p2pBlacklist(BaseSpider):
    #download_delay=2
    name = 'wangdailist'
    start_urls = ['http://www.dailianmeng.com/p2pblacklist/index.html\
    ?P2pBlacklist_page='+str(i) for i in xrange(1,173)]
    allowed_domains = ['dailianmeng.com']
    def __inti__(self):
        pass

    def parse(self, response):
        """
        Request the pages contain url for the detail 
        information of usrs
        """
        # print response.url,"extract response url"
        sel = response.selector
        urls = hxs.xpath(u"//tbody/tr//a[contains\
            (text(),'查看详情')]/@href").extract()
        url = 'http://www.dailianmeng.com'
        try:
            urls = [url+i for i in urls]
            for url in urls:
                yield Request(url, callback=self.getDetail,\
                    dont_filter=True)
        except Exception,e:
            log.msg(e, level=log.ERROR)
            log.msg("wrongeurl:"+response.url, level=log.ERROR)


    def getDetail(self, response):
        """
        extract detail info and store it in items
        """
        item = p2pBlacklistItem()
        
            











