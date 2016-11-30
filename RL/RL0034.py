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

    ad_url = ["http://www.ifeng.com/", "http://news.ifeng.com/", "http://v.ifeng.com/", "http://tech.ifeng.com/",
              "http://finance.ifeng.com/", "http://ent.ifeng.com/", "http://sports.ifeng.com/",
              "http://young.ifeng.com/", "http://fashion.ifeng.com/", "http://auto.ifeng.com/",
              "http://house.ifeng.com/", "http://tech.ifeng.com/", "http://pit.ifeng.com/", "http://games.ifeng.com/",
              "http://cp.ifeng.com/?aid=44", "http://yc.ifeng.com/?_bookch=top", "http://fo.ifeng.com/",
              "http://photo.ifeng.com/", "http://news.ifeng.com/mil/", "http://news.ifeng.com/history/",
              "http://news.ifeng.com/opinion/", "http://finance.ifeng.com/stock/", "http://finance.ifeng.com/money/",
              "http://www.fengjr.com/", "http://digi.ifeng.com/mobile/", "http://tech.ifeng.com/product/",
              "http://home.ifeng.com/", "http://book.ifeng.com/", "http://culture.ifeng.com/",
              "http://guoxue.ifeng.com/", "http://jiu.ifeng.com/", "http://travel.ifeng.com/",
              "http://fashion.ifeng.com/health/", "http://gongyi.ifeng.com/", "http://gz.ifeng.com/",
              "http://yue.ifeng.com/", "http://talk.ifeng.com/", "http://i.audi-future.ifeng.com/",
              "http://innovation.ifeng.com/", "http://diantai.ifeng.com/", ]

    @every(minutes=24 * 60 / 20)
    def on_start(self):
        self.crawl(
            self.ad_url[0],
            callback=self.get_head_ads_content,
            fetch_type='js',
            force_update=True
        )

    def get_head_ads_content(self, response):
        href = [i.attr.href for i in response.doc('a').items() if i.attr.href if
                u'dol.deliver.ifeng.com' in i.attr.href]
        print len(href)
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
        href = [i.attr.href for i in response.doc('a').items() if i.attr.href if
                u'dol.deliver.ifeng.com' in i.attr.href]

        return {
            'content': str(href),
            'url': response.url
        }
