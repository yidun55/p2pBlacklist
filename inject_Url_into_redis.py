#!usr/bin/env python
#encoding: utf-8

import redis

def injectUrl(key, values_list):
    """
    inject url into list of redis
    """
    assert type(values_list)==list, 'values_list\
            must be list'
    myRedis = redis.StrictRedis(host='localhost',\
            port=6379)
    for value in values_list:
        myRedis.lpush(key, value)


baseUrl = 'http://www.p2pzxw.com/index.asp?Page='
urls = [baseUrl+str(i) for i in xrange(1,383)]
key = 'p2p_zxw_redis_spider:start_urls'

injectUrl(key, urls)
