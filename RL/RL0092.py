#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-01-13 10:56:36
# Project: RL0092

from pyspider.libs.base_handler import *
import re
import time
import json
from copy import deepcopy

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
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Referer': 'http://8.askci.com/icinfo/search/{}/all/',
        'Content-Type': 'application/json;charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

    crawl_config = {
        'itag': 'v1',
        'retries': 5,
    }

    search_url = 'http://8.askci.com/icinfo/icinfo/searchIcinfoByUrl.do'

    # TODO
    api_url = 'http://10.26.225.178:10265/api/common/RL_XM0001?start={}&end={}'

    def get_taskid(self, task):
        return md5string(task['url'] + json.dumps(task['fetch'].get('data', '')))

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
            headers = deepcopy(self.default_headers)
            headers['Referer'] = headers['Referer'].format(name)

            self.crawl(
                self.search_url,
                method='POST',
                data=u'{"pageNumber": 1, "pageSize": 10, "totalNumber": 0, "keyWord": ' + name + u', "searchType": "all"}',
                callback=self.get_content,
                headers=headers,
                proxy='localhost:3128',
                save={'name': name}
            )

    @config(priority=3)
    def get_content(self, response):
        try:
            json.loads(response.text)
        except:
            response.raise_for_status()

        return {
            'content': response.text,
            'url': response.url
        }
