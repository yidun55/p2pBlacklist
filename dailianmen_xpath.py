#!usr/bin/env python
#coding: utf-8

"""
测试贷联盟上xpath的元素提取表达式
"""
from scrapy import Selector
from scrapy import log
import os
os.chdir("C:/Users/LENOVO/Desktop")

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

f = open("xpath.txt")
html = f.read()
html = bytes(html)
sel = Selector(text=html, type='html')

te = sel.xpath(u"//a[contains(text(),'查看详情')]/@href").extract()

te = sel.xpath(u"//div[contains(text(), '发证地点')]/text()").extract()
all_info = []
for i in te[0].split("，"):
    all_info.append(i.split("：")[1].rstrip())

te = sel.xpath(u"//th[text()='手机号']/following-sibling::*/\
    text()").extract()   #手机号
te = sel.xpath(u"//th[text()='邮箱地址']/following-sibling::*/\
        text()").extract()   #邮箱地址

print te[0]



