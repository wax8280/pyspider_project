# !/usr/bin/env python
# coding: utf-8
from pyspider.libs.base_handler import *
import time


class Handler(BaseHandler):
    retry_delay = {
        1: 1,
        2: 2,
        3: 8,
    }

    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'http://www.fx168.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }
    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 3,
        'etag': False,
        'last_modified': False,
    }

    start_url = ["http://www.fx168.com/", "http://news.fx168.com/", "http://t.news.fx168.com/",
                 "http://news.fx168.com/top/"]

    @every(minutes=24 * 60 / 10)
    def on_start(self):
        for each in self.start_url:
            self.crawl(
                each,
                callback=self.get_head_ads_content,
                fetch_type='js',
                force_update=True
            )

    def get_head_ads_content(self, response):
        a1 = []
        for div in response.doc('div').items():
            if div.attr.id and (u'Banner' in div.attr.id or u'duilian' in div.attr.id):
                for a in div('a').items():
                    a1.append(a.attr.href)

        return {
            'content': str(a1),
            'url': response.url
        }
