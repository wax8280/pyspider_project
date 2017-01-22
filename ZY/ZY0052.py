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

DIVIDE = 25


class Handler(BaseHandler):
    retry_delay = {
        0: 0,
        1: 0,
        2: 2,
        3: 4,
        4: 8,
        5: 16,
        6: 8,
        7: 8,
        8: 8,
        9: 8,
        10: 8,
        11: 8,
        12: 8,
        13: 8,
        14: 8,
        15: 8,
        16: 8,
        17: 8,
        18: 8,
        19: 8,
        20: 8,
    }
    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

    crawl_config = {
        'itag': 'v2',
        'retries': 5,
    }

    def on_start(self):
        self.crawl(
            'http://www.sohojoy.com/',
            callback=self.get_search_list,
            force_update=True,
            headers=self.default_headers,
            # proxy='localhost:3128',
        )

    def get_search_list(self, response):
        for a in response.doc('.menunavi.cls h4 a').items():
            self.crawl(
                a.attr.href,
                callback=self.get_list,
                headers=self.default_headers,
                # proxy='localhost:3128',
            )

    @config(priority=9)
    @catch_status_code_error
    def get_list(self, response):
        if response.status_code == 200:
            next_url = response.doc('a.next').attr.href if response.doc('a.next').attr.href != 'javascript:;' else None

            if next_url:
                self.crawl(
                    next_url,
                    callback=self.get_list,
                    headers=self.default_headers,
                    # proxy='localhost:3128',
                )
            # 重试
            if len(list(response.doc('ul.prolist.listhover.cls p.ptit a').items())) < 1:
                self.crawl(
                    response.url,
                    callback=self.get_list,
                    force_update=True,
                    headers=self.default_headers,
                    # proxy='localhost:3128',
                )

                return

            headers = deepcopy(self.default_headers)
            headers.update({'Referer': response.url})
            for a in response.doc('ul.prolist.listhover.cls p.ptit a').items():
                self.crawl(
                    a.attr.href,
                    callback=self.get_content,
                    save={'headers': headers},
                    headers=headers,
                    # proxy='localhost:3128',
                )
        else:
            self.crawl(
                response.url,
                callback=self.get_list,
                force_update=True,
                headers=self.default_headers,
                # proxy='localhost:3128',
            )

    @config(priority=10)
    def get_content(self, response):
        if u'sohojoy' not in response.text:
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
