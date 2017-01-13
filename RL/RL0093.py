#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-01-13 14:15:40
# Project: RL0093

from pyspider.libs.base_handler import *
import re
import time
import json
from copy import deepcopy

BEGIN = 5080000
END = 6350000
DIVIDE = 100


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
        'Referer': 'http://www.laipigo.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

    crawl_config = {
        'itag': 'v1',
        'retries': 5,
    }

    search_url = 'http://www.laipigo.com/query/search?search_val={}'

    api_url = 'http://10.26.225.178:10265/api/common/RL0093?start={}&end={}'

    def on_start(self):
        self.crawl(
            self.api_url.format(BEGIN, BEGIN + DIVIDE),
            save={
                'cursor': BEGIN + DIVIDE
            },
            callback=self.get_list,
            force_update=True,
        )

    @config(priority=2)
    def get_list(self, response):
        names = response.text.split('\n')
        cursor = response.save['cursor']
        if cursor >= END:
            return

        if len(names) > 1:
            self.crawl(self.api_url.format(cursor, cursor + DIVIDE),
                       save={
                           'cursor': cursor + DIVIDE
                       },
                       callback=self.get_list,
                       )

        for name in names:
            self.crawl(
                self.search_url.format(name),
                callback=self.get_content,
                headers=self.default_headers,
                proxy='localhost:3128',
                save={'name': name}
            )

    @config(priority=3)
    def get_content(self, response):
        if response.save['name'] not in response.text:
            response.raise_for_status()
            return

        return {
            'content': response.text,
            'url': response.url
        }
