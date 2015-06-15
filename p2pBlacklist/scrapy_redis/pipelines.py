import redis
import connection

from twisted.internet.threads import deferToThread
from scrapy.utils.serialize import ScrapyJSONEncoder
from p2pBlacklist.items import GubaPostListItem


class RedisPipeline(object):
    def __init__(self, server):
        self.server = server
        self.encoder = ScrapyJSONEncoder()

    @classmethod
    def from_settings(cls, settings):
        server = connection.from_settings(settings)
        return cls(server)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def process_item(self, item, spider):
        return deferToThread(self._process_item, item, spider)

    def _process_item(self, item, spider):
        if isinstance(item, GubaPostListItem):
            key = self.item_key(item, spider)
            self.server.rpush(key, item['url'])
        return item

    def item_key(self, item, spider):
        if spider.name == "guba_stock_list_realtime_redis_spider":
            key = "guba_stock_detail_realtime_redis_spider"
        if spider.name == "guba_stock_list_dateback_redis_spider":
            key = "guba_stock_detail_dateback_redis_spider"
        return "%s:start_urls" % key
