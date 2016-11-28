# coding: utf-8

from pyspider.libs.base_handler import *
import re
import time
import hashlib

BEGIN = 0


def get_md5_value(src):
    myMd5 = hashlib.md5()
    myMd5.update(src)
    myMd5_Digest = myMd5.hexdigest()
    return myMd5_Digest


class Handler(BaseHandler):
    retry_delay = {
        1: 1,
        2: 5,
        3: 10,
        4: 30,
        5: 60
    }

    default_headers = {
        'Host': 'www.toutiao.com',
        'Referer': 'http://www.toutiao.com/search/?keyword=%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 5,
        'proxy': 'localhost:3128',
    }

    base_url = 'http://www.toutiao.com/search_content/?offset={offset}&format=json&keyword=%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8&autoload=true&count=20&_={timestamp}'
    detail_url = 'http://www.toutiao.com/group/{}/'

    @every(minutes=24 * 60 * 60)
    def on_start(self):
        self.crawl(self.base_url.format(offset=BEGIN, timestamp=int(time.time() * 1000)), callback=self.get_url,
                   force_update=True)

    @config(priority=2, age=12 * 60 * 60)
    def get_url(self, response):
        result = response.json
        # get where is now by url
        now = int(re.findall(r'offset=(\d+)&format=json', response.url)[0])

        if 'data' in result.keys() and len(result['data']) != 0:
            self.crawl(self.base_url.format(offset=now + 20, timestamp=int(time.time() * 1000)), callback=self.get_url)

            for each in result['data']:
                try:
                    item_id = re.findall('/(\d+)/', each.get('source_url'))[0]
                    self.crawl(self.detail_url.format(item_id), callback=self.get_content)
                except:
                    pass

    @config(priority=3)
    def get_content(self, response):

        return {
            'url': response.url,
            'content': response.text,
            'path': get_md5_value(re.findall('.*?//.*?/(.*)/$', response.url)[0])
        }
