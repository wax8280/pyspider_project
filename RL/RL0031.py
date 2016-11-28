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
        'Referer': 'http://news.sina.com.cn/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 3,
    }

    urls = ["http://roll.news.sina.com.cn/s/channel.php?ch=01", "http://news.sina.com.cn/live/",
            "http://survey.news.sina.com.cn/", "http://news.sina.com.cn/hotnews/", "http://news.sina.com.cn/china/",
            "http://news.sina.com.cn/world/", "http://news.sina.com.cn/society/", "http://mil.news.sina.com.cn/",
            "http://news.sina.com.cn/opinion/", "http://news.sina.com.cn/zhiku/", "http://news.sina.com.cn/gov/",
            "http://news.sina.com.cn/hangpai/", "http://news.sina.com.cn/vr/", "http://photo.sina.com.cn/",
            "http://video.sina.com.cn/news/", "http://sports.sina.com.cn/", "http://ent.sina.com.cn/",
            "http://finance.sina.com.cn/", "http://tech.sina.com.cn/", "http://news.sina.com.cn/zt/"]

    @every(minutes=24 * 60 / 10)
    def on_start(self):
        self.crawl(
            self.urls[0],
            callback=self.get_list,
            fetch_type='js',
            force_update=True,
            save={'first': True}
        )

    @config(priority=2)
    def get_list(self, response):
        href_list = [i.attr.href for i in response.doc('ins a').items() if i.attr.href]

        if response.save.get('first'):
            for each_url in self.urls[1:]:
                self.crawl(
                    each_url,
                    callback=self.get_list,
                    fetch_type='js',
                    force_update=True,
                    save={'first': False}
                )

        return {
            'content': href_list,
            'url': response.url
        }
