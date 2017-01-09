#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-01-09 18:58:39
# Project: allitebook

from pyspider.libs.base_handler import *
import re

RESULT_PATH = './result/allitebook/result/'


class Handler(BaseHandler):
    retry_delay = {
        0: 1,
        1: 1,
        2: 1,
        3: 1,
        4: 1,
        5: 1,
        6: 1,
        7: 1,
        8: 1,
        9: 1,
        10: 1,
        11: 1,
        12: 2,
        13: 8,
        14: 16,
        15: 32,
        16: 64,
        17: 128,
        18: 256,
        19: 512,
        20: 1024
    }

    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'http://www.allitebooks.com/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
    }

    crawl_config = {
        'itag': 'v1',
        'retries': 10,
    }

    url_page = 'http://www.allitebooks.com/page/{}/'

    def on_start(self):
        self.crawl('http://www.allitebooks.com',
                   callback=self.get_list,
                   force_update=True,
                   headers=self.default_headers,
                   save={'now': 1},
                   allow_redirects=False,
                   )

    def get_list(self, response):
        now = response.save['now']

        if 'No Posts Found' in response.text:
            return

        # 翻页
        self.crawl(
            self.url_page.format(now + 1),
            save={'now': now + 1},
            callback=self.get_list,
            force_update=True,
            headers=self.default_headers,
            allow_redirects=False,
        )

        for a in response.doc('#main-content article .entry-thumbnail a').items():
            self.crawl(
                a.attr.href,
                callback=self.get_content,
                headers=self.default_headers,
                allow_redirects=False,
            )

    def get_content(self, response):
        name = re.search('http://www.allitebooks.com/(.*?)/$', response.url).group(1)
        with open(RESULT_PATH + name, 'wb') as f:
            f.write(response.text.encode('utf-8'))
