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

te = hxs.xpath(u"//div[@class='yqsj_kk']\
    //div[contains(text(),'姓名：')]/font/text()").extract()

