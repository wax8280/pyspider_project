#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-01-13 14:46:22
# Project: RL0094

from pyspider.libs.base_handler import *
import re
import time
import json
from copy import deepcopy

BEGIN = 6350000
END = 7620000
DIVIDE = 10


def cdtp(source):
    return u'http://xn--' + source.replace(u'(', u'').replace(u')', u'').encode(
        'punycode') + u'.xn--vuqs22g.xn--vuq861b/'


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

    get_content_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'

    }

    crawl_config = {
        'itag': 'v2',
        'retries': 5,
    }

    api_url = 'http://10.26.225.178:10265/api/common/RL0094?start={}&end={}'

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
                cdtp(name),
                callback=self.get_search_list,
                headers=self.default_headers,
                proxy='localhost:3128',
                save={'name': name, 'url': cdtp(name)}
            )

    @config(priority=3)
    def get_search_list(self, response):
        if response.save['name'] not in response.text:
            self.crawl(
                cdtp(response.save['name']),
                callback=self.get_content,
                headers=self.default_headers,
                proxy='localhost:3128',
                save={'name': response.save['name'], 'url': cdtp(response.save['name'])}
            )
            return

        if u'请确认输入的企业名称是否正确' in response.text:
            return

        gen = re.search('id="companyId" value="([\d]+)"', response.text)
        if gen:
            headers = deepcopy(self.get_content_headers)
            headers.update({'Referer': response.save['url']})
            response.save.update({'headers': headers})
            self.crawl(
                response.save['url'] + 'companyInfo/basicInformation?companyId={}&companyName={}'.
                format(gen.group(1), response.save['name']),
                headers=headers,
                callback=self.get_content,
                save=response.save,
                proxy='localhost:3128',
            )

        return {
            'content': response.save['name'] + '\n' + response.text,
            'url': response.url
        }

    @config(priority=4)
    def get_content(self, response):
        try:
            json.loads(response.text)
        except:
            self.crawl(
                response.url,
                headers=response.save['headers'],
                callback=self.get_content,
                save=response.save,
                proxy='localhost:3128',
            )
            return

        return {
            'content': response.save['name'] + '\n' + response.text,
            'url': response.url
        }
