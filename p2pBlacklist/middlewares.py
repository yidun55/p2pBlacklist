# -*- coding: utf-8 -*-

import os
import re
import time
import socket
import base64
import random
from scrapy import log
from guba.utils import _default_redis, get_pid, get_ip
from scrapy.exceptions import CloseSpider, IgnoreRequest
from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
        ConnectionRefusedError, ConnectionDone, ConnectError, \
        ConnectionLost, TCPTimedOutError
from scrapy.xlib.tx import ResponseFailed

BUFFER_SIZE = 100
RESET_TIME_CHECK = 60
SLEEP_TIME_CHECK = 10


class ForbbidenResponseError(Exception):
    """forbbiden response error
    """
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        if self.value:
            return repr(self.value)
        else:
            return 'ForbbidenResponseError'

class UnknownResponseError(Exception):
    """未处理的错误"""
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        if self.value:
            return repr(self.value)
        else:
            return 'UnknownResponseError'


class ShouldNotEmptyError(Exception):
    """返回不应该为空，但是为空了，在spider里抛出"""
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        if self.value:
            return repr(self.value)
        else:
            return 'ShouldNotEmptyError'

class RetryForeverMiddleware(object):
    # IOError is raised by the HttpCompression middleware when trying to
    # decompress an empty response
    EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError,
            ConnectionRefusedError, ConnectionDone, ConnectError,
            ConnectionLost, TCPTimedOutError, ResponseFailed,
            IOError, UnknownResponseError, ForbbidenResponseError)

    def __init__(self, retry_init_wait, retry_stable_times, retry_add_wait):
        self.retry_init_wait = retry_init_wait
        self.retry_stable_times = retry_stable_times
        self.retry_add_wait = retry_add_wait
        self.retry_exceptions = self.EXCEPTIONS_TO_RETRY
        self.pid = get_pid()
        self.ip = get_ip()

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        retry_init_wait = settings.get('RETRY_INIT_WAIT', 1)
        retry_stable_times = settings.get('RETRY_STABLE_TIMES', 100)
        retry_add_wait = settings.get('RETRY_STABLE_TIMES', 100)
        return cls(retry_init_wait, retry_stable_times, retry_add_wait)

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0)
        if retries == 0:
            retry_wait = self.retry_init_wait
        elif retries >= self.retry_stable_times:
            retry_wait = self.retry_init_wait + self.retry_stable_times * self.retry_add_wait
        else:
            retry_wait = self.retry_init_wait + retries * self.retry_add_wait

        time.sleep(retry_wait)

        retries += 1
        log.msg(format="Retrying %(request)s (failed %(retries)d times): %(reason)s, current ip: %(ip)s, current pid: %(pid)s",
                level=log.WARNING, spider=spider, request=request, retries=retries, reason=reason, ip=self.ip, pid=self.pid)
        retryreq = request.copy()
        retryreq.meta['retry_times'] = retries
        retryreq.dont_filter = True

        return retryreq

    def process_spider_exception(self, response, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
                and not response.request.meta.get('dont_retry', False):
            return [self._retry(response.request, exception, spider)]


class RetryErrorResponseMiddleware(object):
    def __init__(self, retry_times):
        self.retry_times = retry_times
        self.pid = get_pid()
        self.ip = get_ip()

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        retry_times = settings.get('RETRY_TIMES', 3)
        return cls(retry_times)

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0)
        if retries < self.retry_times:
            log.msg(format="Retrying %(request)s (failed %(retries)d times): %(reason)s, current ip: %(ip)s, current pid: %(pid)s",
                    level=log.WARNING, spider=spider, request=request, retries=retries, reason=reason, ip=self.ip, pid=self.pid)
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            return retryreq
        else:
            log.msg(format="Gave up retrying %(request)s (failed %(retries)d times): %(reason)s, current ip: %(ip)s, current pid: %(pid)s",
                    level=log.ERROR, spider=spider, request=request, retries=retries, reason=reason, ip=self.ip, pid=self.pid)

    def process_spider_exception(self, response, exception, spider):
        if 'dont_retry' not in response.request.meta and isinstance(exception, UnknownResponseError):
            return [self._retry(response.request, exception, spider)]

class ProxyMiddleware(object):
    # overwrite process request
    def __init__(self, proxy_ip_file, proxy_from_redis, proxy_ip_redis_key, proxy_redis_host, proxy_redis_port):
        self.proxy_from_redis = proxy_from_redis
        if not proxy_from_redis:
            with open(proxy_ip_file) as f:
                self.proxy_ips = []
                for line in f:
                    self.proxy_ips.append(line.strip())
                self.proxy_ips_length = len(self.proxy_ips)
        else:
            self.redis = _default_redis(proxy_redis_host, proxy_redis_port)
            self.proxy_redis_key = proxy_ip_redis_key

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        proxy_ip_file = settings.get('PROXY_IP_FILE', None)
        proxy_from_redis = settings.get('PROXY_FROM_REDIS', None)
        proxy_ip_redis_key = settings.get('PROXY_IP_REDIS_KEY', None)
        proxy_redis_host = settings.get('REDIS_HOST', None)
        proxy_redis_port = settings.get('REDIS_PORT', None)
        return cls(proxy_ip_file, proxy_from_redis, proxy_ip_redis_key, proxy_redis_host, proxy_redis_port)

    def process_request(self, request, spider):
        if self.proxy_from_redis:
            # 从效果最好的20个IP中随即选取一个IP
            rs = self.redis.zrange(self.proxy_redis_key, 0, 19)
            rs_length = len(rs)
            if rs_length:
                randomidx = random.randint(0, rs_length - 1)
                proxy_ip_port = rs[randomidx]
            else:
                proxy_ip_port = "http://111.13.12.202"
            # 每访问一次，该ip的计数器+1
            self.redis.zincrby(self.proxy_redis_key, proxy_ip_port, amount=1)
        else:
            # Set the location of the proxy
            randomidx = random.randint(0, self.proxy_ips_length-1)
            proxy_ip_port = self.proxy_ips[randomidx]  # "http://111.13.12.202" # "http://218.108.242.124:8080"
        request.meta['proxy'] = proxy_ip_port

        # Use the following lines if your proxy requires authentication
        # proxy_user_pass = "USERNAME:PASSWORD"

        # setup basic authentication for the proxy
        # encoded_user_pass = base64.encodestring(proxy_user_pass)
        # request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass


class IgnoreHttpError(IgnoreRequest):
    """A non-200 response was filtered
    """
    def __init__(self, response, *args, **kwargs):
        self.response = response
        super(IgnoreHttpError, self).__init__(*args, **kwargs)

class Redirect302Middleware(object):
    """处理302帖子被删除的情况
    """
    def __init__(self):
        self.pid = get_pid()
        self.ip = get_ip()

    def process_spider_input(self, response, spider):
        if response.status == 302:
            raise IgnoreHttpError(response, '302 post deleted, Ignoring 302 response')

    def process_spider_exception(self, response, exception, spider):
        if isinstance(exception, IgnoreHttpError):
            log.msg(
                    format="Ignoring response %(response)r: 302 deleted, current ip: %(ip)s, current pid: %(pid)s",
                    level=log.WARNING,
                    spider=spider,
                    response=response,
                    ip=self.ip,
                    pid=self.pid
            )

            return []


class Forbbiden403Middleware(object):
    """处理403 ip被封的情况
    """
    def process_spider_input(self, response, spider):
        if response.status == 403:
            raise ForbbidenResponseError('403 forbbiden, retrying...')


class DownloadTimeoutRetryMiddleware(object):
    EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError,
            ConnectionRefusedError, ConnectionDone, ConnectError,
            ConnectionLost, TCPTimedOutError, ResponseFailed,
            IOError)

    def __init__(self, retry_init_wait, retry_stable_times, retry_add_wait, \
            proxy_ip_redis_key, proxy_redis_host, proxy_redis_port, proxy_ip_punish):
        self.retry_init_wait = retry_init_wait
        self.retry_stable_times = retry_stable_times
        self.retry_add_wait = retry_add_wait
        self.redis = _default_redis(proxy_redis_host, proxy_redis_port)
        self.proxy_redis_key = proxy_ip_redis_key
        self.proxy_ip_punish = proxy_ip_punish
        self.pid = get_pid()
        self.ip = get_ip()

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        retry_init_wait = settings.get('RETRY_INIT_WAIT', 1)
        retry_stable_times = settings.get('RETRY_STABLE_TIMES', 100)
        retry_add_wait = settings.get('RETRY_STABLE_TIMES', 100)
        proxy_ip_redis_key = settings.get('PROXY_IP_REDIS_KEY', None)
        proxy_redis_host = settings.get('REDIS_HOST', None)
        proxy_redis_port = settings.get('REDIS_PORT', None)
        proxy_ip_punish = settings.get('PROXY_IP_PUNISH', None)
        return cls(retry_init_wait, retry_stable_times, retry_add_wait, \
                proxy_ip_redis_key, proxy_redis_host, proxy_redis_port, \
                proxy_ip_punish)

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0)
        if retries == 0:
            retry_wait = self.retry_init_wait
        elif retries >= self.retry_stable_times:
            retry_wait = self.retry_init_wait + self.retry_stable_times * self.retry_add_wait
        else:
            retry_wait = self.retry_init_wait + retries * self.retry_add_wait

        time.sleep(retry_wait)

        retries += 1
        log.msg(format="Retrying %(request)s (failed %(retries)d times): %(reason)s, current ip: %(ip)s, current pid: %(pid)s",
                level=log.WARNING, spider=spider, request=request, retries=retries, reason=reason, ip=self.ip, pid=self.pid)
        retryreq = request.copy()
        retryreq.meta['retry_times'] = retries
        retryreq.dont_filter = True

        return retryreq

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
                and 'dont_retry' not in request.meta:
            proxy_ip = request.meta['proxy']

            # 在保证网络通畅的情况下发现不能用的ip，写到文件
            #with open('./guba/tools/ip_forbid.txt', 'a') as fw:
            #    fw.write('%s\n' % proxy_ip)

            self.redis.zincrby(self.proxy_redis_key, proxy_ip, amount=self.proxy_ip_punish)
            return self._retry(request, exception, spider)
