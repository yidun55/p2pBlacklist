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
    #download_delay=2
    name = 'pplist'
    start_urls = ['http://www.ppdai.com/blacklist/']
    allowed_domains = ['ppdai.com']
    myRedis = redis.StrictRedis(host='localhost',port=6379) #connected to redis
    def __inti__(self):
        pass

    def make_requests_from_url(self, url):
        return Request(url, callback=self.gettotal, dont_filter=True)

    def gettotal(self, response):
        """
        extract pages from different years
        """
        url = 'http://www.ppdai.com/blacklist/'
        years = xrange(2008,2016)
        urls = [url+str(year) for year in years]
        for url in urls[4:5]:
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
            for page in range(int(pages[0]))[0:1]:
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
        for url in urls[0:1]:
            self.__class__.myRedis.lpush(redis_key, url)

    # def getDetail(self, response):
    #     """
    #     extract detail info and store it in items
    #     """
    #     item = p2pBlacklistItem()
    #     print response.url, "this is the response url"
    #     sel = response.selector
    #     accPri = sel.xpath(u"//table[contains(@class, 'detail_table')]/tr[1]/td[1]/text()").re(ur"累计借入本金：([\S\s]*)")    #累计借入本金
    #     ovDate =  sel.xpath(u"//table[contains(@class, 'detail_table')]/tr[1]/td[2]/span/text()").extract()   #最大逾期天数
    #     liID   =  sel.xpath(u"//table[contains(@class, 'detail_table')]/tr[3]//tr[2]/td[1]/text()").extract()   #列表编号
    #     loNu   =   sel.xpath(u"//table[contains(@class, 'detail_table')]/tr[3]//tr[2]/td[2]/text()").extract()  #借款基数
    #     print loNu[0]
    #     loTime =  sel.xpath(u"//table[contains(@class, 'detail_table')]/tr[3]//tr[2]/td[3]/text()").extract()   #借款时间
    #     print loTime[0]
    #     ovDayNu =  sel.xpath(u"//table[contains(@class, 'detail_table')]/tr[3]//tr[2]/td[4]/text()").extract()   #逾期天数
    #     print ovDayNu[0]
    #     ovPri   =   sel.xpath(u"//table[contains(@class, 'detail_table')]/tr[3]//tr[2]/td[5]/text()").extract()  #逾期本息
    #     print ovPri
    #     prov   = sel.xpath(u"//div[contains(@class,'blacklist_detail_nav')]//li//strong/text()").re(ur"_([\w]*?)_")     #省
    #     print prov[0]
    #     usrNa  =  sel.xpath(u"//div[contains(@class,'blacklist_detail_nav')]//li").re(ur"用户名：([\w\W]*?)\n")    #用户名
    #     print usrNa[0]
    #     name   =  sel.xpath(u"//div[contains(@class,'blacklist_detail_nav')]//li").re(ur"姓名：([\w\W]*?)\n")    #姓名
    #     print name[0]
    #     phoneN =  sel.xpath(u"//div[contains(@class,'blacklist_detail_nav')]//li").re(ur"手机号：([\w\W]*?)\n")    #手机号
    #     print phoneN[0]
    #     ID     =   sel.xpath(u"//div[contains(@class,'blacklist_detail_nav')]//li").re(ur"身份证号：([\w\W]*?)\n")   #身份证号
    #     print ID

    #     try:
    #         info = accPri[0]+"\001"+ovDate[0]+"\001"+liID[0]+"\001"+loNu[0]+"\001"+loTime[0]+"\001"+ovDayNu[0]+"\001"+ovPri[0]+"\001"+prov[0]+"\001"+usrNa[0]+"\001"+name[0]+"\001"+phoneN[0]+"\001"+ID[0]
    #         item['content'] = info
    #         #print item['content'], 'item work'
    #     except Exception,e:
    #         #print e,"try 2"
    #         log.msg(response.url, level=log.ERROR)
    #         log.msg(e, level=log.ERROR)

    #     yield item

            











