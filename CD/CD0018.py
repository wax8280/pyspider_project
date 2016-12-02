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
        'Referer': 'http://www.autohome.com.cn/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }
    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 3,
        'etag': False,
        'last_modified': False,
    }

    start_url = "http://www.autohome.com.cn/"

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl(
            self.start_url,
            callback=self.get_head_ads_content,
            fetch_type='js',
            force_update=True
        )

    def get_head_ads_content(self, response):
        a1 = []
        for a in response.doc('#ad_fbanner_00 a').items():
            a1.append(a.attr.href)
        for a in response.doc('#ad_fbutton_00 a').items():
            a1.append(a.attr.href)
        for a in response.doc('#ad_990_tm a').items():
            a1.append(a.attr.href)

        for a in response.doc('#focus-1 a').items():
            if a.attr.id and u'ad' in a.attr.id:
                a1.append(a.attr.href)

        for div in response.doc('div').items():
            if div.attr.class_ and (u'monkey monkey_box' in div.attr.class_ or u'advbox pa-b20' in div.attr.class_):
                for iframe in div('iframe').items():
                    a1.append(iframe.attr.src)

        return {
            'content': str(a1),
            'url': response.url
        }
