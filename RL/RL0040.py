#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pyspider.libs.base_handler import *
from copy import deepcopy
import re

BEGIN = 0
DIVIDE = 2


class Handler(BaseHandler):
    retry_delay = {
        1: 1,
        2: 2,
        3: 8,
    }

    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    tungee_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 3,
    }

    url = u'http://s.hc360.com/?w={}&mc=enterprise'
    # TODO
    api_url = u'http://10.116.16.180:10265/api/names/zhaopin?start={}&end={}'

    def on_start(self):
        self.crawl(self.api_url.format(BEGIN, BEGIN + DIVIDE),
                   save={
                       'end': BEGIN + DIVIDE
                   },
                   callback=self.list_page, force_update=True, headers=self.tungee_header)

    def list_page(self, response):
        names = response.text.split('\n')
        now = response.save['end']
        if len(names) > 1:
            self.crawl(self.api_url.format(now, now + DIVIDE),
                       save={
                           'end': now + DIVIDE
                       },
                       callback=self.list_page,
                       headers=self.tungee_header
                       )

        for name in names:
            if len(name.strip()):
                self.crawl(self.url.format(name.strip()),
                           callback=self.get_list,
                           proxy='localhost:3128',
                           headers=self.default_headers,
                           save={'company_name': name.strip(), 'p': 1}
                           )

    @config(priority=2)
    def get_list(self, response):
        new_headers = deepcopy(self.default_headers)
        new_headers.update({'Referer': response.url})

        try:
            i = list(response.doc('.contbox').items())[0]
        except:
            i = []

        if i:
            for j in i('h3 span').items():
                print j.text()

                if response.save.get('company_name') in j.text():
                    for k in i('h3 a').items():
                        if k.attr.href and u'b2b.hc360.com' in k.attr.href:
                            self.crawl(
                                k.attr.href + u'shop/show.html',
                                callback=self.get_content,
                                headers=new_headers,
                                proxy='localhost:3128',
                            )

    @config(priority=5)
    def get_content(self, response):
        return {
            'content': response.text,
            'url': response.url
        }
