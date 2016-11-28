# !/usr/bin/env python
# coding: utf-8
from pyspider.libs.base_handler import *


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
        'Referer': 'http://www.xinhuanet.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }
    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 3,
        'etag': False,
        'last_modified': False,
    }

    ad_url = ["http://www.xinhuanet.com/", "http://www.news.cn/politics/", "http://www.news.cn/local/index.htm",
              "http://www.news.cn/legal/index.htm", "http://www.xinhuanet.com/politics/rs.htm",
              "http://www.news.cn/world/index.htm", "http://www.news.cn/tw/index.htm",
              "http://www.news.cn/overseas/index.htm", "http://www.news.cn/fortune/", "http://education.news.cn/",
              "http://www.news.cn/tech/index.htm", "http://www.news.cn/energy/index.htm", "http://ent.news.cn/",
              "http://www.news.cn/fashion/index.htm", "http://www.news.cn/food/index.htm", "http://travel.news.cn/", ]

    @every(minutes=24 * 60 / 10)
    def on_start(self):
        self.crawl(
            self.ad_url[0],
            callback=self.get_head_ads_content,
            fetch_type='js',
            force_update=True
        )

    def get_head_ads_content(self, response):
        iframe_src = [i.attr.src for i in response.doc('.wloadIframeAD').items()]

        a_href = ''
        for i in response.doc("#CoupletDiv116112410082525").items():
            a_href = i.attr.href

        for i in self.ad_url[1:]:
            self.crawl(
                i,
                callback=self.get_sub_ads_content,
                fetch_type='js',
                force_update=True
            )

        print iframe_src
        print a_href

        return {
            'content': str(iframe_src) + a_href,
            'url': response.url
        }

    def get_sub_ads_content(self, response):
        pc_ad = [i.attr.href for i in response.doc('#pc_ad1 a').items()]
        pc_ad.extend([i.attr.href for i in response.doc('#pc_ad2 a').items()])

        return {
            'content': str(pc_ad),
            'url': response.url
        }
