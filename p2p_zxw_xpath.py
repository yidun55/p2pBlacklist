#!usr/bin/env python
#encoding: utf-8
"""
用来测试网贷黑名单的xpath表达式
"""
import os
from scrapy import Selector
from scrapy import log
os.chdir("C:/Users/LENOVO/Desktop")

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

f = open("xpath.txt")
html = f.read()
html = bytes(html)
hxs = Selector(text=html, type='html')

def for_ominated_data(info_list,i_list):
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

blocks = hxs.xpath(u"//div[@class='yqsj_kk']")
for block in blocks:
    info = []
    name = block.xpath(u".//div[contains(text(),'姓名：')]\
        /font/text()").extract()   #姓名
    info = for_ominated_data(info_list=info, i_list=name)
    ID = block.xpath(u".//div[contains(text(),'证件号：')]\
        /font/text()").extract()   #证件号
    info = for_ominated_data(info, ID)
    sex = block.xpath(u".//div[contains(text(),'性别：')]\
        /text()").re(u"性别：([\w]*)")   #性别
    info = for_ominated_data(info, sex)
    IDAddr = block.xpath(u".//div[contains(text(),'身份证地址：')]\
        /text()").re(u"身份证地址：([\w]*)")   #身份证地址
    info = for_ominated_data(info, IDAddr)
    FDddr = block.xpath(u".//div[contains(text(),'家庭地址：')]\
        /text()").re(u"家庭地址：([\w]*)")   #家庭地址
    info = for_ominated_data(info, FDddr)
    Tel = block.xpath(u".//div[contains(text(),'联系电话：')]\
        /text()").re(u"联系电话：([\w]*)")   #联系电话
    info = for_ominated_data(info, Tel)
    balDue = block.xpath(u".//div[contains(text(),'欠款本息总额：￥')]\
        /font/text()").extract()   #欠款本息总额
    info = for_ominated_data(info, balDue)
    dInterest = block.xpath(u".//div[contains(text(),'逾期总罚息：')]\
        /text()").re(u"逾期总罚息：([\w\W]*)")   #逾期总罚息
    info = for_ominated_data(info, dInterest)
    YQBX = block.xpath(u".//div[contains(text(),'逾期笔数：')]\
        /text()").re(u"逾期笔数：([\w\W]*)")   #逾期笔数
    info = for_ominated_data(info, YQBX)
    WZDH = block.xpath(u".//div[contains(text(),'网站代还笔数：')]\
        /text()").re(u"网站代还笔数：([\w\W]*)")   #网站代还笔数
    info = for_ominated_data(info, WZDH)
    ZCYJ = block.xpath(u".//div[contains(text(),'最长逾期天数：')]\
        /text()").re(u"最长逾期天数：([\w\W]*)")   #最长逾期天数
    info = for_ominated_data(info,ZCYJ)
    GXSJ = block.xpath(u".//div[contains(text(),'更新时间：')]\
        /text()").re(u"更新时间：([\w\W]*)")   #更新时间
    info = for_ominated_data(info,GXSJ)
    print "\001".join(info)
    # info = []




    




# te = hxs.xpath(u"//div[@class='yqsj_kk']\
#     //div[contains(text(),'姓名：')]/font/text()").extract()



