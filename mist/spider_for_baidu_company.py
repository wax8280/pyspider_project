#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-11-03 14:55:21
# Project: BAIDU_HOMEPAGE

from pyspider.libs.base_handler import *
import re
from copy import deepcopy

# from sys import path

# path.append('/home/spider/tsparrow')
# from tsparrow import predict_official_website

BEGIN = 0
DIVIDE = 3


class Handler(BaseHandler):
    retry_delay = {
        1: 1,
        2: 2,
        3: 8,
        4: 16,
        5: 32,
        6: 64,
        7: 128,
        8: 256,
        9: 512,
        10: 1024
    }

    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'http://www.baidu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    tungee_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
    }

    crawl_config = {
        'itag': 'v11',
        'headers': default_headers,
        'retries': 10,
    }

    url = u'http://www.baidu.com/s?wd={key_word}'
    # TODO
    api_url = u'http://112.74.93.18:10265/api/names?start={}&end={}'

    def on_start(self):
        self.crawl(self.api_url.format(BEGIN, BEGIN + DIVIDE),
                   save={
                       'end': BEGIN + DIVIDE
                   },
                   callback=self.list_page, force_update=True, headers=self.tungee_header)

    @config(age=365 * 24 * 60 * 60)
    def list_page(self, response):
        names = response.text.split('\n')
        now = response.save['end']
        if len(names) > 1:
            self.crawl(self.api_url.format(now, now + DIVIDE),
                       save={
                           'end': now + DIVIDE
                       },
                       callback=self.list_page, headers=self.tungee_header)

        for name in names:
            if len(name.strip()):
                self.crawl(self.url.format(key_word=name.strip()), callback=self.get_ten_page,
                           save={'first': True, 'company_name': name.strip(), 'type': 'normal'})

                self.crawl(self.url.format(key_word=(name.strip() + u' 简称')), callback=self.get_ten_page,
                           save={'first': True, 'company_name': name.strip(), 'type': 'short'})

    @config(priority=2)
    def get_ten_page(self, response):
        content_headers = deepcopy(self.default_headers)
        content_headers['Referer'] = response.url

        for each in response.doc('.c-container').items():
            self.crawl(each('.t a').attr.href, callback=self.get_content, headers=content_headers,
                       save={'company_name': response.save['company_name'],
                             'type': response.save['type'], 'cookies': response.cookies,
                             'highlight': each('em').text()},
                       cookies=response.cookies)

        if response.save.get('first'):
            for each in list(response.doc('#page a').items())[:2]:
                self.crawl(each.attr.href, callback=self.get_ten_page,
                           save={'first': False, 'company_name': response.save['company_name'],
                                 'type': response.save['type']})

    @config(priority=3)
    def get_content(self, response):

        search_result = re.search(u"<noscript>.*URL=\'(.+)\'.*</noscript>", response.text)

        if search_result:
            redirected_url = search_result.groups()[0]

            content_headers = deepcopy(self.default_headers)
            content_headers['Referer'] = response.url

            self.crawl(redirected_url, callback=self.get_content, headers=content_headers,
                       save={'company_name': response.save['company_name'], 'type': response.save['type'],
                             'highlight': response.save['highlight']}, cookies=response.save['cookies'])


        else:
            type = u' 简称' if response.save['type'] == 'short' else u''
            return {
                'content': response.save['company_name'] + type + u'\n' + response.save['highlight']
                           + u'\n' + response.text,
            }
