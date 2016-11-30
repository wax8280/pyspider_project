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

    ad_url = ["http://news.sohu.com/", "http://mil.sohu.com/", "http://cul.sohu.com/", "http://history.sohu.com/",
              "http://book.sohu.com/", "http://star.news.sohu.com/", "http://sports.sohu.com/",
              "http://sports.sohu.com/nba.shtml", "http://cbachina.sports.sohu.com/",
              "http://sports.sohu.com/zhongchao.shtml", "http://golf.sports.sohu.com/", "http://business.sohu.com/",
              "http://money.sohu.com/", "http://stock.sohu.com/", "http://fund.sohu.com/", "http://it.sohu.com/",
              "http://digi.it.sohu.com/", "http://digi.it.sohu.com/mobile.shtml", "http://chuangke.sohu.com/",
              "http://auto.sohu.com/", "http://2sc.sohu.com/gd-jiangmen/", "http://fashion.sohu.com/",
              "http://health.sohu.com/", "http://travel.sohu.com/", "http://learning.sohu.com/",
              "http://learning.sohu.com/liuxueedu/", "http://learning.sohu.com/gaokaoedu/", "http://baobao.sohu.com/",
              "http://chihe.sohu.com/", "http://astro.women.sohu.com/", "http://gongyi.sohu.com/",
              "http://tv.sohu.com/ugc/", "http://yule.sohu.com/", "http://tv.sohu.com/drama/us/",
              "http://music.yule.sohu.com/", "http://mgame.sohu.com/", "http://www.focus.cn/",
              "http://esf.focus.cn/search/", "http://home.focus.cn/", "http://caipiao.sohu.com/",
              "http://city.sohu.com/"]

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

        for div in response.doc('div').items():
            if div.attr.id:
                if u'beans_' in div.attr.id:
                    for a in div('a').items():
                        if a.attr.href:
                            if u'http://www.iac-i.org/privacy' not in a.attr.href:
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

        for div in response.doc('div').items():
            if div.attr.id:
                if u'beans_' in div.attr.id:
                    for a in div('a').items():
                        if a.attr.href:
                            if u'http://www.iac-i.org/privacy' not in a.attr.href:
                                href.append(a.attr.href)

        return {
            'content': str(href),
            'url': response.url
        }
