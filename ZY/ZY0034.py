# coding: utf-8
from pyspider.libs.base_handler import *
from copy import deepcopy
import HTMLParser
import re

html_parser = HTMLParser.HTMLParser()

DIVIDE = 2
BEGIN = 1
SHOULD_TRY_TIME = 10


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
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'http://www.apple.com/rss/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 10,
    }

    url_list = ["http://ax.itunes.apple.com/WebObjects/MZStore.woa/wpa/MRSS/justadded/limit=200/rss.xml",
                "http://ax.itunes.apple.com/WebObjects/MZStore.woa/wpa/MRSS/featuredalbums/limit=200/rss.xml",
                "http://ax.itunes.apple.com/WebObjects/MZStoreServices.woa/ws/RSS/toppaidapplications/limit=200/xml",
                "http://ax.itunes.apple.com/WebObjects/MZStoreServices.woa/ws/RSS/topfreeapplications/limit=200/xml", ]

    @every(minutes=24 * 60)
    def on_start(self):
        for each in self.url_list:
            self.crawl(each,
                       callback=self.get_gzh,
                       force_update=True,
                       etag=False,
                       last_modified=False,
                       headers=self.default_headers,
                       proxy='localhost:3128',
                       )

    def get_content(self, response):
        return {
            'content': response.text,
            'url': response.url
        }
