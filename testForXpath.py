#!usr/bin/env python
#encoding: utf-8

import os
from scrapy import Selector
os.chdir("C:/Users/LENOVO/Desktop")

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

f = open("xpath.txt")
html = f.read()
html = bytes(html)
hxs = Selector(text=html, type='html')

te = hxs.xpath(u"count(//div[@class='table_nav']//tr)").extract()
trI = 2
bef = u"//table[contains(@class, \
'detail_table')]/tr[3]//tr["
aft = u"]/td[1]/text()"
ass = bef + str(trI) + aft
liID   =  hxs.xpath(ass).extract()   #列表编号
prov   = hxs.xpath(u"//div[contains(@class,\
            'blacklist_detail_nav')]//li//strong/text()").re(ur"_([\w]*?)_['男|女']")     #省
accPri = hxs.xpath(u"//table[contains(@class, \
    'detail_table')]/tr[1]/td[1]/text()").re(ur"累计借入本金：([\S\s]*)")    #累计借入本金

ovDate =  hxs.xpath(u"//table[contains(@class, \
'detail_table')]/tr[1]/td[2]/span/text()").extract()   #最大逾期天数
print "i work", ovDate[0]