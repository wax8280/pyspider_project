#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-01-21 11:45:55
# Project: RL0094_2

from pyspider.libs.base_handler import *
import re
import time
import json
from copy import deepcopy
from urllib import urlencode

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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

    get_content_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

    crawl_config = {
        'itag': 'v2',
        'retries': 5,
    }

    api_url = 'http://120.77.12.100:10265/api/common/RL0094?start={}&end={}'

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
            param = urlencode({'q': name.encode('utf8')})
            # 异步，真实的API
            headers = deepcopy(self.get_content_headers)
            headers.update({'Referer': 'http://www.telecredit.cn/result?' + param})

            param2 = urlencode({
                'searchKey': name.encode('utf8'),
                'page': '1',
                'registerCapitals': '0',
                'formed': '0',
                'provice': '%E5%85%A8%E9%83%A8'
            })

            self.crawl(
                'http://www.telecredit.cn/search/searchData?' + param2,
                callback=self.get_search_list,
                headers=headers,
                # proxy='localhost:3128',
                # 保存url，以便设置Referer
                save={'name': name,
                      'search_url': 'http://www.telecredit.cn/result?' + param,
                      'last_headers': headers}
            )

    @config(priority=3)
    def get_search_list(self, response):
        try:
            result = json.loads(response.text)
        except:
            self.crawl(
                response.url,
                callback=self.get_search_list,
                headers=response.save['last_headers'],
                # proxy='localhost:3128',
                save=response.save
            )
            return

        for item in result['list']:
            gen = re.search(u'(.*?)\.信用\.信息', item['uname'])

            if gen:
                name = gen.group(1)

                headers = deepcopy(self.default_headers)
                headers.update({
                    'Referer': response.save['search_url']
                })

                self.crawl(
                    cdtp(name),
                    callback=self.get_company_page,
                    headers=headers,
                    # proxy='localhost:3128',
                    save={'name': name,
                          'last_headers': headers}
                )

    @config(priority=5)
    def get_company_page(self, response):
        if response.save['name'] not in response.text:
            self.crawl(
                response.url,
                headers=response.save['last_heasers'],
                callback=self.get_company_page,
                save=response.save,
            )
            return

        gen = re.search('id="companyId" value="([\d]+)"', response.text)
        if gen:
            headers = deepcopy(self.get_content_headers)
            headers.update({'Referer': response.url})

            # 异步加载一部分
            self.crawl(
                response.url + u'companyInfo/basicInformation?companyId={}&companyName={}'.
                format(gen.group(1), response.save['name']),
                headers=headers,
                callback=self.get_content,
                save={
                    'name': response.save['name'],
                    'last_headers': headers
                },
                # proxy='localhost:3128',
            )

        # 同步加载一部分
        return {
            'content': response.save['name'] + '\n' + response.text,
            'url': response.url
        }

    @config(priority=10)
    def get_content(self, response):
        try:
            json.loads(response.text)
        except:
            self.crawl(
                response.url,
                headers=response.save['last_headers'],
                callback=self.get_content,
                save=response.save,
                # proxy='localhost:3128',
            )
            return

        return {
            'content': response.save['name'] + '\n' + response.text,
            'url': response.url
        }
