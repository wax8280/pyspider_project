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
        'Referer': 'http://www.iqiyi.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }
    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 3,
        'etag': False,
        'last_modified': False,
    }

    start_url = "http://www.iqiyi.com/"

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl(
            self.start_url,
            callback=self.get_head_ads_content,
            fetch_type='js',
            js_script='''
                       function() {
                           window.scrollTo(500,1000);
                           return 123;
                       }
                       ''',
            force_update=True
        )

    def get_head_ads_content(self, response):
        #time.sleep(20)
        a1 = [_.attr.href for _ in response.doc('.theatre-container a').items()]

        print a1

        return {
            'content': str(a1),
            'url': response.url
        }

