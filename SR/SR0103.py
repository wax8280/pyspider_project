# coding: utf-8

from pyspider.libs.base_handler import *
import re
from copy import deepcopy
from itertools import combinations
from pyquery import PyQuery as pq
import time

BEGIN = 0
DIVIDE = 20

class Handler(BaseHandler):
    retry_delay = {
        1: 1,
        2: 2,
        3: 8,
        4: 16,
        5: 32,
        6: 64,
        7: 128,
        8: 256,
        9: 512,
        10: 1024
    }

    default_headers = {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Accept': 'text / html, application / xhtml + xml, application / xml;q = 0.9, image / webp, * / *;q = 0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN, zh;q = 0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',

    }

    tungee_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 10,
        'etag': False,
        'last_modified': False,
    }

    url = u'http://www.beianbeian.com/s?keytype=2&q={}'

    # TODO
    api_url = u'http://112.74.93.18:10265/api/names?start={}&end={}'

    # 正式
    # api_url = u'http://10.26.229.2:10265/api/names?start={}&end={}'

    def on_start(self):
        self.crawl(self.api_url.format(BEGIN, BEGIN + DIVIDE),
                   save={
                       'end': BEGIN + DIVIDE
                   },
                   callback=self.list_page,
                   force_update=True,
                   headers=self.tungee_header
                   )

    @config(age=365 * 24 * 60 * 60)
    def list_page(self, response):
        names = response.text.split('\n')
        now = response.save['end']
        if len(names) > 1:
            self.crawl(self.api_url.format(now, now + DIVIDE),
                       save={
                           'end': now + DIVIDE
                       },
                       callback=self.list_page,
                       headers=self.tungee_header
                       )

        for name in names:
            if len(name.strip()):
                self.crawl(self.url.format(name.strip()),
                           callback=self.get_content,
                           proxy='localhost:3128',
                           )

    @config(priority=2)
    def get_content(self, response):
        return {
            'content': response.text,
            'url': response.url
        }
