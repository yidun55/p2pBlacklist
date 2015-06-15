# -*- coding:utf-8 -*-

"""使用scrapy_redis的guba_stock_detail_redis_spider(实时更新)"""

import re
import json
import math
import urllib2
from scrapy import log
from scrapy.http import Request
from scrapy.conf import settings
from scrapy.spider import Spider
# from BeautifulSoup import BeautifulSoup
from p2pBlacklist.items import *
from p2pBlacklist.middlewares import UnknownResponseError
from p2pBlacklist.scrapy_redis.spiders import RedisSpiderFast

HOST_URL = "http://www.p2pzxw.com/"

class p2pBlacklistRedis(RedisSpiderFast):
    """usage: scrapy crawl guba_stock_detail_dateback_redis_spider --loglevel=INFO
              爬取股吧中帖子页数据
    """
    name = 'p2p_zxw_redis_spider'
    redis_key = 'p2p_zxw_redis_spider:start_urls'

    def parse(self, response):
        """
        extract detail element from response
        """
        sel = response.selector
        name = sel.xpath(u"//div[@class='yqsj_kk']\
    //div[contains(text(),'姓名：')]/font/text()").extract()
        try:
            names = ''
            names = [names+str(i) for i in name]
        except Exception, e:
            log.msg('ERROR:{url}'.format(url=response.url),\
                level=log.ERROR)
        item['content'] = names
        return item

