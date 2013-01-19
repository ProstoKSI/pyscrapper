import re
import time
import urllib2

import redis

from pymisc.web.browser import Browser
from pymisc.utils.urls import extract_urls

class PyScrapper(object):
    
    def __init__(self, initial_urls, follow_urls=[], landing_urls=[], 
            redis_config={}, browser_class=Browser, clear_history=False, timeout=1, logger=None):
        self.redis = redis.StrictRedis(host=redis_config.get('host', 'localhost'), 
            port=redis_config.get('port', 6379), 
            db=redis_config.get('db', 0))
        self.queue_key = "%s" % redis_config.get('namespace', 'pyscrapper')
        self.prefix_key = "%s" % redis_config.get('prefix', 'pyscrapper')
        self.browser = browser_class()
        if clear_history:
            self.clear_history()
        self.timeout = timeout
        self.set_initial_urls(initial_urls)
        self.follow_urls = [re.compile(url) for url in follow_urls]
        self.landing_urls = [(re.compile(url), callback) for url, callback in landing_urls]
        self.logger = logger

    def clear_history(self):
        for key in self.redis.keys('%s-*' % self.prefix_key):
            self.redis.delete(key)
        while self.redis.lpop(self.queue_key) is not None:
            pass

    def set_initial_urls(self, initial_urls):
        initial_urls = initial_urls if isinstance(initial_urls, list) else [initial_urls]
        for url in initial_urls:
            if not self.redis.get('%s-%s' % (self.prefix_key, url)):
                self.redis.rpush(self.queue_key, url)

    def add_landing_url(self, url, callback):
        self.landing_urls.append((re.compile(url), callback))

    def add_follow_url(self, url):
        self.follow_urls.append(re.compile(url))

    def _land_url(self, url, content):
        for landing_url, callback in self.landing_urls:
            if landing_url.match(url):
                if self.logger:
                    self.logger.info("Callback for url %s" % url)
                callback(url, content)

    def _can_follow(self, url):
        for follow_url in self.follow_urls:
            if follow_url.match(url):
                return True
        return False

    def _follow_url(self, origin_url, content):
        for url in extract_urls(content, origin_url):
            if self._can_follow(url):
                self.redis.rpush(self.queue_key, url)

    def iterate(self):
        url = self.redis.lpop(self.queue_key)
        if self.logger:
            self.logger.info("Downloading url %s" % url)
        if not url:
            return False
        try:
            content = self.browser.get(url)
        except urllib2.HTTPError:
            return True
        except KeyboardInterrupt:
            return False
        self._land_url(url, content)
        self._follow_url(url, content)
        self.redis.set('%s-%s' % (self.prefix_key, url), True)
        return True

    def run(self):
        while True:
            try:
               if not self.iterate():
                    break
                time.sleep(self.timeout)
            except KeyboardInterrupt:
                break

