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
        'Referer': 'https://www.douban.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }
    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 3,
        'etag': False,
        'last_modified': False,
    }

    start_url = {0: "https://www.douban.com/", 1: "https://book.douban.com/", 2: "https://movie.douban.com/",
                 3: "https://music.douban.com/"}

    @every(minutes=24 * 60)
    def on_start(self):
        for k, v in self.start_url.items():
            self.crawl(
                v,
                callback=self.get_head_ads_content,
                fetch_type='js',
                force_update=True,
                save={'k': k}
            )

    def get_head_ads_content(self, response):
        a1 = []
        for div in response.doc('div').items():
            if response.save.get('k') == 0 and div.attr.id and (u'dale_anonymous' in div.attr.id):
                for a in div('a').items():
                    a1.append(a.attr.href)
            if response.save.get('k') == 1 and div.attr.id and (u'dale_book_home' in div.attr.id):
                for a in div('a').items():
                    a1.append(a.attr.href)
            if response.save.get('k') == 2 and div.attr.id and (u'dale_movie_home' in div.attr.id):
                for a in div('a').items():
                    a1.append(a.attr.href)
            if response.save.get('k') == 3 and div.attr.id and (u'dale_music_home' in div.attr.id):
                for a in div('a').items():
                    a1.append(a.attr.href)

        return {
            'content': str(a1),
            'url': response.url
        }
