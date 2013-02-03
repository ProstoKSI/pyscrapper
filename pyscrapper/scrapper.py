import re
import sys
import time
import urllib2
import logging

import redis

from pymisc.web.browser import Browser
from pymisc.utils.urls import extract_urls

class PyScrapper(object):
    
    def __init__(self, initial_urls, follow_urls=[], landing_urls=[], 
            redis_config={}, browser_class=Browser, clear_history=False, timeout=1, logger=None, custom_can_follow=None):
        self.redis = redis.StrictRedis(host=redis_config.get('host', 'localhost'), 
            port=redis_config.get('port', 6379), 
            db=redis_config.get('db', 0))
        self.queue_key = "%s" % redis_config.get('namespace', 'pyscrapper')
        self.prefix_key = "%s" % redis_config.get('prefix', 'pyscrapper')
        self.browser = browser_class()
        self.logger = logger
        if clear_history:
            self.clear_history()
        self.timeout = timeout
        self.set_initial_urls(initial_urls)
        self.follow_urls = [re.compile(url) for url in follow_urls]
        self.landing_urls = [(re.compile(url), callback) for url, callback in landing_urls]
        self.custom_can_follow = custom_can_follow

    def _log(self, message):
        if self.logger:
            self.logger.info(message)

    def clear_history(self):
        self._log("Cleaning history and queue")
        for key in self.redis.keys('%s-*' % self.prefix_key):
            self.redis.delete(key)
        while self.redis.lpop(self.queue_key) is not None:
            pass

    def _is_visited_url(self, url):
       return self.redis.get('%s-%s' % (self.prefix_key, url))

    def set_initial_urls(self, initial_urls):
        initial_urls = initial_urls if isinstance(initial_urls, list) else [initial_urls]
        for url in initial_urls:
            if not self._is_visited_url(url):
                self.redis.rpush(self.queue_key, url)

    def add_landing_url(self, url, callback):
        self.landing_urls.append((re.compile(url), callback))

    def add_follow_url(self, url):
        self.follow_urls.append(re.compile(url))

    def _land_url(self, url, content):
        for landing_url, callback in self.landing_urls:
            if landing_url.match(url):
                self._log("Callback for url %s" % url)
                callback(url, content)

    def _can_follow(self, url):
        if self._is_visited_url(url):
            return False
        if self.custom_can_follow is not None and not self.custom_can_follow(url):
            return False
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
        if not url:
            return False
        self._log("Downloading url %s" % url)
        try:
            content = self.browser.get(url)
        except urllib2.HTTPError:
            return True
        self.redis.set('%s-%s' % (self.prefix_key, url), True)
        self._land_url(url, content)
        self._follow_url(url, content)
        return True

    def run(self):
        while True:
            try:
                if not self.iterate():
                    self._log("Url queue is empty - scrapper's task is finished.")
                    break
                time.sleep(self.timeout)
            except KeyboardInterrupt:
                self._log("Scrapper was interrupted. It will continue from interrupted page if `clear_history` flag is not True")
                break

def run_scrapper(config, enable_logging=True):
    if enable_logging:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        config['logger'] = logging
    scrapper = PyScrapper(**config)
    scrapper.run()

