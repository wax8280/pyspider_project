#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-01-22 11:32:27
# Project: SR0121


from pyspider.libs.base_handler import *
import re
import time
import json
from copy import deepcopy
from urllib import urlencode
import random

DIVIDE = 5


class Handler(BaseHandler):
    retry_delay = {
        0: 0,
        1: 0,
        2: 2,
        3: 4,
        4: 8,
        5: 16
    }
    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

    crawl_config = {
        'itag': 'v1',
        'retries': 5,
    }

    api_url = 'http://so.365zhaosheng.com/school.asp?query=&p=&c=&bt=&s=&page={}'

    def on_start(self):
        self.crawl(
            self.api_url.format(1),
            save={
                'cursor': 1,
                'first': True,
                'max_page': 0,
            },
            callback=self.get_list,
            force_update=True,
            headers=self.default_headers,
            # proxy='localhost:3128',
        )

    @config(priority=random.randint(9, 11))
    def get_list(self, response):
        if response.save['max_page'] == 0:
            mp = int(max(re.findall('query=&p=&c=&bt=&s=&page=(\d)*', response.text)))
        else:
            mp = response.save['max_page']
        cursor = response.save['cursor']

        # 翻页
        if response.save['first'] and cursor < mp:
            for j in range(cursor, min(cursor + DIVIDE, mp)):
                if j == min(cursor + DIVIDE, mp) - 1:
                    is_first = True
                else:
                    is_first = False
                self.crawl(
                    self.api_url.format(j),
                    save={
                        'cursor': cursor + j,
                        'first': is_first,
                        'max_page': mp
                    },
                    callback=self.get_list,
                    headers=self.default_headers,
                    # proxy='localhost:3128',
                )

        # 重试
        if len(list(response.doc('div.column2 table a.tl').items())) < 1:
            self.crawl(
                self.api_url.format(cursor),
                save={
                    'cursor': cursor,
                    'first': response.save['is_first']
                },
                callback=self.get_list,
                force_update=True,
                headers=self.default_headers,
                # proxy='localhost:3128',
            )

            return

        headers = deepcopy(self.default_headers)
        headers.update({'Referer': response.url})
        for a in response.doc('div.column2 table a.tl').items():
            self.crawl(
                a.attr.href,
                callback=self.get_content,
                save={'headers': headers},
                headers=headers,
                # proxy='localhost:3128',
            )

    @config(priority=10)
    def get_content(self, response):
        if u'天天招生' not in response.text:
            self.crawl(
                response.url,
                callback=self.get_content,
                headers=response.save['headers'],
                # proxy='localhost:3128',
            )
            return

        return {
            'content': response.text,
            'url': response.url
        }
