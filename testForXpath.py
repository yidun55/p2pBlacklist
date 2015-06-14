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

urls = hxs.xpath(u"//tbody/tr//a[contains\
    (text(),'查看详情')]/@href").extract()


idNum = hxs.xpath(u"//table[contains(@id,'yw0')]//\
    th[contains(text(),'身份证号')]/following-sibling::*\
    /text()").extract()  #身份证号

phone = hxs.xpath(u"//table[contains(@id,'yw0')]//\
    th[contains(text(),'手机号')]/following-sibling::*\
    /text()").extract()  #身份证号

print phone