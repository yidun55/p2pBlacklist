#coding:utf-8

"""
  从贷联盟上爬取网贷黑名单,并测试redis
  author: 邓友辉
  email:heshang1203@sina.com
  date:2015/06/18
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
    writeInFile = 'dailianmeng_blacklist'  #item 写入的文件名
    name = 'dai_lian_meng_redis_spider2' #for test
    redis_key = 'dai_lian_meng_redis_spider:start_urls'

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
            # print "your".join(info_list)
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
        try:
            te = sel.xpath(u"//div[contains(text(), '发证地点')]/text()").extract()
            all_info = []
            info = []
            for i in te[0].split("，"):
                all_info.append(i.split("：")[1].rstrip())
            ID = []
            ID.append(all_info[0])  
            info = self.for_ominated_data(info, ID)   #身份证号
            sex = []
            sex.append(all_info[1])
            info = self.for_ominated_data(info, sex)  #性别
            birthday = []
            birthday.append(all_info[2])
            info = self.for_ominated_data(info, birthday)  #生日
            old = []
            old.append(all_info[3])
            info = self.for_ominated_data(info, old)   #岁数
            IdAdrr = []
            IdAdrr.append(all_info[4])
            info = self.for_ominated_data(info, IdAdrr)  #发证地点
        except Exception, e:
            log.msg(e, level=log.ERROR)
            log.msg('first ERROR:{url}'.format(url=response.url),\
                level=log.ERROR)

        Tel = sel.xpath(u"//th[text()='手机号']/following-sibling::*/\
            text()").extract()   #手机号
        info = self.for_ominated_data(info, Tel)
        Email = sel.xpath(u"//th[text()='邮箱地址']/following-sibling::*/\
            text()").extract()   #邮箱地址
        info = self.for_ominated_data(info, Email)
        qq = sel.xpath(u"//th[text()='QQ号']/following-sibling::*/\
            text()").extract()   #QQ号
        info = self.for_ominated_data(info, qq)
        name = sel.xpath(u"//th[text()='姓名']/following-sibling::*/\
            text()").extract()   #姓名
        info = self.for_ominated_data(info, name)
        principle = sel.xpath(u"//th[text()='本金/本息']/following-sibling::*/\
            text()").extract()   #本金/本息
        info = self.for_ominated_data(info, principle)
        YHJE = sel.xpath(u"//th[text()='已还金额']/following-sibling::*/\
            text()").extract()   #已还金额
        info = self.for_ominated_data(info, YHJE)
        WHFX = sel.xpath(u"//th[text()='未还/罚息']/following-sibling::*/\
            text()").extract()   #未还/罚息
        info = self.for_ominated_data(info, WHFX)
        JKSJ = sel.xpath(u"//th[text()='借款时间']/following-sibling::*/\
            text()").extract()   #借款时间
        info = self.for_ominated_data(info, JKSJ)
        JKQS = sel.xpath(u"//th[text()='借款期数']/following-sibling::*/\
            text()").extract()   #借款期数
        info = self.for_ominated_data(info, JKQS)
        GSMC = sel.xpath(u"//th[text()='公司名称']/following-sibling::*/\
            text()").extract()   #公司名称
        info = self.for_ominated_data(info, GSMC)
        GSDH = sel.xpath(u"//th[text()='公司电话']/following-sibling::*/\
            text()").extract()   #公司电话
        info = self.for_ominated_data(info, GSDH)
        GSDZ = sel.xpath(u"//th[text()='公司地址']/following-sibling::*/\
            text()").extract()   #公司地址
        info = self.for_ominated_data(info, GSDZ)
        JZDH = sel.xpath(u"//th[text()='居住电话']/following-sibling::*/\
            text()").extract()   #居住电话
        info = self.for_ominated_data(info, JZDH)
        JZDZ = sel.xpath(u"//th[text()='居住地址']/following-sibling::*/\
            text()").extract()   #居住地址
        info = self.for_ominated_data(info, JZDZ)
        ZJDZ = sel.xpath(u"//th[text()='证件地址']/following-sibling::*/\
            text()").extract()   #证件地址
        info = self.for_ominated_data(info, ZJDZ)
        ZJDZ = sel.xpath(u"//th[text()='证件地址']/following-sibling::*/\
            text()").extract()   #证件地址
        info = self.for_ominated_data(info, ZJDZ)

        try:
            info = '\001'.join(info)
            item['content'] = info
            yield item
        except Exception, e:
            log.msg('ERROR:{url}'.format(url=response.url),\
                level=log.ERROR)













