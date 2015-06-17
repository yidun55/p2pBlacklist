#coding:utf-8

"""
  从拍拍贷上爬取网贷黑名单,并测试redis
  author: 邓友辉
  email:heshang1203@sina.com
  date:2015/06/10
"""

from scrapy import log
from scrapy.http import Request
from scrapy.conf import settings
from scrapy.spider import Spider
from p2pBlacklist.items import *
#from p2pBlacklist.middlewares import UnknownResponseError
from p2pBlacklist.scrapy_redis.spiders import RedisSpider

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

class p2pBlacklist(RedisSpider):
    #download_delay=2
    writeInFile = 'ppai_blacklist'  #item 写入的文件名
    name = 'ppai_blacklist_redis_spider2' #for test
    redis_key = 'ppai_blacklist_redis_spider:start_urls'

    def for_ominated_data(self,info_list,i_list):
        """
        some elements are ominated, set the ominated elements
        as "" 
        """
        try:
            if len(i_list) == 0:
                i_list.append("")
            else:
                pass
            assert len(i_list) == 1, "the element must be unique"
            info_list.extend(i_list)
            # print 'you work'
            return info_list
        except Exception, e:
            print 'i work'
            log.msg(e, level=log.ERROR)


    def parse(self, response):
        """
        extract detail info and store it in items
        """
        item = p2pBlacklistItem()
        sel = response.selector
        total = sel.xpath(u"count(//div[@class='table_nav']\
            //tr)").extract()   #借款的笔数
        total = int(total[0][0])
        for trI in xrange(2, total+1):
            """
            有的用户有多笔的借款
            trI是不同笔借款所在表格的行数
            """
            info = []
            accPri = sel.xpath(u"//table[contains(@class, \
                'detail_table')]/tr[1]/td[1]/text()").re(ur"累计\
                借入本金：([\S\s]*)")    #累计借入本金
            info = self.for_ominated_data(info, accPri)
            ovDate =  sel.xpath(u"//table[contains(@class, \
            'detail_table')]/tr[1]/td[2]/span/text()").extract()   #最大逾期天数
            info = self.for_ominated_data(info, ovDate)
            liID   =  sel.xpath(u"//table[contains(@class, \
            'detail_table')]/tr[3]//tr[trI]/td[1]/text()").extract()   #列表编号
            info = self.for_ominated_data(info, liID)
            loNu   =   sel.xpath(u"//table[contains(@class, \
            'detail_table')]/tr[3]//tr[trI]/td[2]/text()").extract()  #借款期数
            info = self.for_ominated_data(info, loNu)
            loTime =  sel.xpath(u"//table[contains(@class, \
            'detail_table')]/tr[3]//tr[trI]/td[3]/text()").extract()   #借款时间
            info = self.for_ominated_data(info, loTime)
            ovDayNu =  sel.xpath(u"//table[contains(@class, \
            'detail_table')]/tr[3]//tr[trI]/td[4]/text()").extract()   #逾期天数
            info = self.for_ominated_data(info, ovDayNu)
            ovPri   =   sel.xpath(u"//table[contains(@class, \
            'detail_table')]/tr[3]//tr[trI]/td[5]/text()").extract()  #逾期本息
            info = self.for_ominated_data(info, ovPri)
            prov   = sel.xpath(u"//div[contains(@class,\
            'blacklist_detail_nav')]//li//strong/text()").re(ur"_([\w]*?)_")     #省
            info = self.for_ominated_data(info, prov)
            usrNa  =  sel.xpath(u"//div[contains(@class,\
            'blacklist_detail_nav')]//li").re(ur"用户名：([\w\W]*?)\n")    #用户名
            info = self.for_ominated_data(info, usrNa)
            name   =  sel.xpath(u"//div[contains(@class,\
            'blacklist_detail_nav')]//li").re(ur"姓名：([\w\W]*?)\n")    #姓名
            info = self.for_ominated_data(info, name)
            phoneN =  sel.xpath(u"//div[contains(@class,\
            'blacklist_detail_nav')]//li").re(ur"手机号：([\w\W]*?)\n")    #手机号
            info = self.for_ominated_data(info, phoneN)
            ID     =   sel.xpath(u"//div[contains(@class,\
            'blacklist_detail_nav')]//li").re(ur"身份证号：([\w\W]*?)\n")   #身份证号
            info = self.for_ominated_data(info, ID)

            try:
                info = '\001'.join(info)
                item['content'] = info
                yield item
            except Exception, e:
                log.msg('ERROR:{url}'.format(url=response.url),\
                    level=log.ERROR)













