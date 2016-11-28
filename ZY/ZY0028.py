# coding: utf-8
# !/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-11-18 11:19:50
# Project: ZY0030

from pyspider.libs.base_handler import *
from copy import deepcopy
import datetime

BEGIN = 1
DIVIDE = 5
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
        'content-type': 'application/x-www-form-urlencoded',
        'Pragma': 'no-cache',
        'Referer': 'http://www.youxichaguan.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    crawl_config = {
        'itag': 'v1',
        'retries': 10,
    }

    url = u'http://www.youxichaguan.com/game_{}.html'

    @every(minutes=24 * 60)
    def on_start(self):
        now_date = unicode((datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
        self.crawl(self.url.format(BEGIN),
                   callback=self.get_list,
                   itag=now_date,
                   force_update=True,
                   etag=False,
                   last_modified=False,
                   headers=self.default_headers,
                   # proxy='localhost:3128',
                   validate_cert=False,
                   save={'now': BEGIN, 'now_date': now_date}
                   )

    @config(priority=2)
    def get_list(self, response):

        new_headers2 = deepcopy(self.default_headers)
        new_headers2['Referer'] = self.url.format(response.save.get('now'))

        if u'class="col-sm-4 col-md-4"' in response.text:

            for i in range(1, DIVIDE + 1):
                new_url = self.url.format(response.save.get('now') + i)
                new_headers = deepcopy(self.default_headers)
                new_headers['Referer'] = self.url.format(response.save.get('now') + i - 1)

                # 翻页
                self.crawl(
                    new_url,
                    callback=self.get_list,
                    headers=new_headers,
                    itag=response.save.get('now_date'),
                    # proxy='localhost:3128',
                    save={'now': response.save.get('now') + i},
                    validate_cert=False,
                )

            for i in response.doc('.gamelib a').items():
                if u'www.youxichaguan.com/game/' in i.attr.href:
                    url = i.attr.href if u'youxichaguan.com' in i.attr.href else u'http://www.youxichaguan.com' + i.attr.href
                    self.crawl(
                        url,
                        callback=self.get_content,
                        headers=new_headers2,
                        # proxy='localhost:3128',
                        validate_cert=False,
                    )

    @config(priority=3)
    def get_content(self, response):
        return {
            'content': response.text,
            'url': response.url
        }
