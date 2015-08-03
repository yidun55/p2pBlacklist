# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os

os.chdir("/root/dyh/data/blacklist")   #linux only
# os.chdir("E:/DLdata/blacklist")      #my desktop
class p2pBlacklistPipeline(object):
    def process_item(self, item, spider):
        # print "pipline work"
        f = open(spider.writeInFile, "a")
        f.write(item['content']+'\n')
        f.close()
