#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-01-12 17:42:57
# Project: RL0090

from pyspider.libs.base_handler import *
import re
import time
import json

BEGIN = 0
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
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

    crawl_config = {
        'itag': 'v1',
        'retries': 5,
    }

    search_url = 'http://r.zx.onlyou.com/datainfo/infoquery/searchEnterpise?keywords={}&infoQueryType=enterprise'
    content_url = 'http://r.zx.onlyou.com/riviews/datainfo/gsqyxxQuery/toEnterpriseInfo'

    # TODO
    # api_url = 'http://120.77.12.100:10265/api/common/RL0087?start={}&end={}'

    api_url = 'http://10.26.225.178:10265/api/common/RL_XM0001?start={}&end={}'

    def get_taskid(self, task):
        return md5string(task['url'] + json.dumps(task['fetch'].get('data', '')))

    def get_time(self):
        return str(int(time.time() * 1000))

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
        if cursor <= 0:
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
                # proxy='localhost:3128',
            )

    def get_search_list(self, response):
        regno = re.search('regno="(.*?)"', response.text).group(1)
        c = re.search('c="(.*?)"', response.text).group(1)
        ename = re.search('ename="(.*?)"', response.text).group(1)
        resstatus = re.search('reStatus="(.*?)"', response.text).group(1)

        self.crawl(
            self.content_url,
            params={
                'reg_no': regno,
                'name': ename,
                'c': c,
                'searchKeywords': ename,
                'reg_status': resstatus,
            },
            save={
                'name': ename,
            },
            proxy='localhost:3128',
            headers=self.default_headers,
            callback=self.get_content
        )

    def get_content(self, response):
        return {
            'content': response.text,
            'url': response.url
        }

