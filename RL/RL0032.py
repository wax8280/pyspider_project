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
        'Referer': 'http://www.sohu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }
    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 3,
        'etag': False,
        'last_modified': False,
    }

    ad_url = ["http://news.qq.com/", "http://news.qq.com/photo.shtml", "http://mil.qq.com/mil_index.htm",
              "http://finance.qq.com/", "http://stock.qq.com/", "http://money.qq.com/", "http://v.qq.com/",
              "http://v.qq.com/tv/", "http://v.qq.com/variety/", "http://sports.qq.com/", "http://sports.qq.com/nba/",
              "http://sports.qq.com/csocce/csl/", "http://ent.qq.com/", "http://ent.qq.com/star/",
              "http://ent.qq.com/movie/", "http://fashion.qq.com/", "http://health.qq.com/", "http://baby.qq.com/",
              "http://auto.qq.com/", "http://data.auto.qq.com/car_brand/index.shtml", "http://house.qq.com/",
              "http://www.jia360.com/", "http://digi.tech.qq.com/hea/", "http://tech.qq.com/",
              "http://digi.tech.qq.com/", "http://digi.tech.qq.com/mobile/", "http://games.qq.com/",
              "http://kid.qq.com/", "http://astro.fashion.qq.com/", "http://edu.qq.com/", "http://class.qq.com/",
              "http://edu.qq.com/abroad/", "http://cul.qq.com/", "http://dajia.qq.com/", "http://book.qq.com/",
              "http://gongyi.qq.com/", "http://foxue.qq.com/", "http://paike.qq.com/"]

    @every(minutes=24 * 60 / 20)
    def on_start(self):
        self.crawl(
            self.ad_url[0],
            callback=self.get_head_ads_content,
            fetch_type='js',
            force_update=True
        )

    def get_head_ads_content(self, response):
        href = []

        for a in response.doc('a').items():
            if a.attr.class_ == u'absolute a_cover':
                href.append(a.attr.href)

        for i in self.ad_url[1:]:
            self.crawl(
                i,
                callback=self.get_sub_ads_content,
                fetch_type='js',
                force_update=True
            )

        return {
            'content': str(href),
            'url': response.url
        }

    def get_sub_ads_content(self, response):
        href = []

        for a in response.doc('a').items():
            if a.attr.class_ == u'absolute a_cover':
                href.append(a.attr.href)

        return {
            'content': str(href),
            'url': response.url
        }
