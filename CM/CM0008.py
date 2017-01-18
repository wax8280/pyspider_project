#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-01-12 11:14:39
# Project: CM0008

from pyspider.libs.base_handler import *
import re
import time
import json

DIVIDE = 100
BEGIN = 0


def cdtp(source_url):
    result_url = 'http://www.{}.{}'
    chinese_pattern = u'www\.(.+)\.(.+)'
    gen = re.search(chinese_pattern, source_url)
    if gen:
        _ = []
        for i in gen.groups():
            if re.search(u'[\u4e00-\u9fa5]', i):
                _.append(u'xn--' + i.encode('punycode'))
            else:
                _.append(i)

        return result_url.format(_[0], _[1])


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
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh-TW;q=0.4',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 2,
    }

    api_url = 'http://10.26.225.178:10265/api/common/CM0008?start={}&end={}'

    def on_start(self):
        self.crawl(
            'http://10.26.225.178:10265/api/common/CM0008?start={}&end={}'.format(BEGIN, BEGIN + DIVIDE),
            callback=self.get_list,
            force_update=True,
            save={'cursor': BEGIN + DIVIDE}
        )

    @config(priority=2)
    def get_list(self, response):
        ll = response.text.split('\n')

        # ---------------------------------
        l = [i.split(',') for i in ll]
        # 以前的
        if len(l) > len(ll):
            return
        # -------------------------------

        print ll
        print len(ll)
        print len(l)
        if len(ll) < DIVIDE:
            time.sleep(5)
            self.crawl(
                self.api_url.format(response.save['cursor'] - DIVIDE, response.save['cursor']),
                callback=self.get_list,
                save={'cursor': response.save['cursor']}
            )
            return

        else:
            self.crawl(
                self.api_url.format(response.save['cursor'], response.save['cursor'] + DIVIDE),
                callback=self.get_list,
                save={'cursor': response.save['cursor'] + DIVIDE}
            )

        for url in ll:
            # url 中有中文
            if re.search(u'[\u4e00-\u9fa5]', url):
                url = cdtp(url)

            self.crawl(
                'http://' + url,
                callback=self.get_content,
                headers=self.default_headers,
                save={
                    'url': url
                }
            )

    @config(priority=4)
    def get_content(self, resposne):
        return {
            'content': resposne.save['url'] + '\n' + resposne.text,
            'url': resposne.url
        }
