import re
import time
import redis
from pymisc.web.browser import Browser

def extract_urls(content):
    url_re = re.compile(r'\b(([\w-]+://?|www[.])[^\s()<>]+(?:\([\w\d]+\)|([^[:punct:]\s]|/)))')
    for match in url_re.finditer(content):
        yield match.group(0)

class PyScrapper(object):
    
    def __init__(self, initial_urls, follow_urls=[], landing_urls=[], redis_config={}, browser_class=Browser):
        self.redis = redis.StrictRedis(host=redis_config.get('host', 'localhost'), 
            port=redis_config.get('port', 6379), 
            db=redis_config.get('db', 0))
        self.queue_key = "%s" % redis_config.get('namespace', 'pyscrapper')
        self.prefix_key = "%s" % redis_config.get('prefix', 'pyscrapper')
        self.browser = browser_class()
        self.set_initial_urls(initial_urls if isinstance(initial_urls, list) else [initial_urls])
        self.follow_urls = follow_urls
        self.landing_urls = landing_urls

    def set_initial_urls(self, initial_urls):
        for url in initial_urls:
            if not self.redis.get('%s-%s' % (self.prefix_key, url)):
                self.redis.rpush(self.queue_key, url)

    def add_landing_url(self, url, callback):
        self.landing_urls.append((url, callback))

    def add_follow_url(self, url):
        self.follow_urls.append(url)

    def _land_url(self, url, content):
        for landing_url, callback in self.landing_urls:
            if re.match(landing_url, url):
                callback(url, content)

    def _can_follow(self, url):
        for follow_url in self.follow_urls:
            if re.match(follow_url, url):
                return True
        return False

    def _follow_url(self, content):
        for url in extract_urls(content):
            if self._can_follow(url):
                self.redis.rpush(self.queue_key, url)

    def iterate(self):
        url = self.redis.lpop(self.queue_key)
        print(url)
        if not url:
            return False
        content = self.browser.get(url)
        self._land_url(url, content)
        self._follow_url(content)
        self.redis.set('%s-%s' % (self.prefix_key, url), True)
        return True

    def run(self):
        while True:
            if not self.iterate():
                break
            time.sleep(1)

