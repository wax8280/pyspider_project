#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-01-22 16:04:09
# Project: ZY0055


from pyspider.libs.base_handler import *
import re
import time
import json
from copy import deepcopy
from urllib import urlencode
import random


class Handler(BaseHandler):
    retry_delay = {
        0: 0,
        1: 0,
        2: 2,
        3: 4,
        4: 8,
        5: 16,
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

    def on_start(self):
        self.crawl(
            'http://www.cntrades.com/',
            callback=self.get_search_list,
            force_update=True,
            headers=self.default_headers,
        )

    @config(priority=1)
    def get_search_list(self, response):
        for a in response.doc('.ct-5 dt i a').items():
            self.crawl(
                a.attr.href,
                callback=self.get_search_detail_list,
                headers=self.default_headers,
                proxy='localhost:3128',
            )

    @config(priority=2)
    def get_search_detail_list(self, response):
        for a in response.doc('.class-name-item a').items():
            self.crawl(
                a.attr.href,
                callback=self.get_list,
                headers=self.default_headers,
                proxy='localhost:3128',
            )

    @config(priority=9)
    @catch_status_code_error
    def get_list(self, response):
        if response.status_code == 200:
            next_url = response.doc('#destoon_next').attr.value \
                if re.search('\d+-\d+', response.doc('#destoon_next').attr.value) else None

            if next_url:
                self.crawl(
                    next_url,
                    callback=self.get_list,
                    headers=self.default_headers,
                    proxy='localhost:3128',
                )
            # 重试
            if len(list(response.doc('div.list li a').items())) < 1:
                self.crawl(
                    response.url,
                    callback=self.get_list,
                    force_update=True,
                    headers=self.default_headers,
                    proxy='localhost:3128',
                )

                return

            headers = deepcopy(self.default_headers)
            headers.update({'Referer': response.url})

            for a in response.doc('div.list li a').items():
                if 'itemid' in a.attr.href:
                    base_url = re.sub('sell/.*$', '', a.attr.href)
                    self.crawl(
                        base_url + 'introduce',
                        callback=self.get_content,
                        save={'headers': headers},
                        headers=headers,
                        proxy='localhost:3128',
                    )
                    self.crawl(
                        base_url + 'contact',
                        callback=self.get_content,
                        save={'headers': headers},
                        headers=headers,
                        proxy='localhost:3128',
                    )
        else:
            self.crawl(
                response.url,
                callback=self.get_list,
                force_update=True,
                headers=self.default_headers,
                proxy='localhost:3128',
            )

    @config(priority=10)
    def get_content(self, response):
        if 'cntrades' not in response.text:
            self.crawl(
                response.url,
                callback=self.get_content,
                headers=response.save['headers'],
                proxy='localhost:3128',
            )
            return
        else:
            return {
                'content': response.text,
                'url': response.url
            }
