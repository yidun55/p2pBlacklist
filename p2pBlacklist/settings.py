# -*- coding: utf-8 -*-

# Scrapy settings for p2pBlacklist project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'p2pBlacklist'

SPIDER_MODULES = ['p2pBlacklist.spiders']
NEWSPIDER_MODULE = 'p2pBlacklist.spiders'

DEFAULT_ITEM_CLASS='p2pBlacklist.items.p2pBlacklistItem'
ITEM_PIPELINES=['p2pBlacklist.pipelines.p2pBlacklistPipeline']

LOG_FILE="/root/dyh/data/blacklist/log"  #linux only
# LOG_FILE = "E:/DLdata/logging/log"      #my desktop

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'p2pBlacklist (+http://www.yourdomain.com)'
