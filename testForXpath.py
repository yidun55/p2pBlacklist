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

liID   =  hxs.xpath(u"//table[contains(@class, \
            'detail_table')]/tr[3]//tr[3]/td[1]/text()").extract()
print liID
