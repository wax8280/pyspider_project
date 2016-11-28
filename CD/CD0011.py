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
        'Referer': 'http://v.qq.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }
    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 3,
        'etag': False,
        'last_modified': False,
    }

    ad_url = ["http://v.qq.com/", "http://v.qq.com/tv/", "http://v.qq.com/variety/", "http://v.qq.com/movie/",
              "http://film.qq.com/x/2016/", "http://v.qq.com/cartoon/", "http://v.qq.com/child/",
              "http://v.qq.com/ent/", "http://v.qq.com/music/", "http://v.qq.com/livemusic/",
              "http://v.qq.com/tv/yingmei/", "http://v.qq.com/tv/korea/", "http://v.qq.com/doco/",
              "http://v.qq.com/dv/", "http://v.qq.com/news/", "http://v.qq.com/sports/",
              "http://sports.qq.com/nbavideo/", "http://v.qq.com/fun/", "http://v.qq.com/games/", ]

    @every(minutes=24 * 60 / 20)
    def on_start(self):
        self.crawl(
            self.ad_url[0],
            callback=self.get_head_ads_content,
            fetch_type='js',
            force_update=True
        )

    def get_head_ads_content(self, response):
        href = [i.attr.href for i in response.doc('.absolute.a_cover a').items()]

        for i in self.ad_url[1:]:
            self.crawl(
                i,
                callback=self.get_sub_ads_content,
                fetch_type='js',
                force_update=True
            )

        return {
            'content': href,
            'url': response.url
        }

    def get_sub_ads_content(self, response):
        href = [i.attr.href for i in response.doc('.absolute.a_cover a').items()]
        return {
            'content': href,
            'url': response.url
        }
