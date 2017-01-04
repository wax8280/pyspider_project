#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-12-28 19:35:02
# Project: ZY0054

from pyspider.libs.base_handler import *
import re
from copy import deepcopy
import hashlib
import json

BEGIN = 0
DIVIDE = 5


def get_md5_value(src):
    src = src.encode('utf-8')
    myMd5 = hashlib.md5()
    myMd5.update(src)
    myMd5_Digest = myMd5.hexdigest()
    return myMd5_Digest


class Handler(BaseHandler):
    retry_delay = {
        0: 1,
        1: 1,
        2: 1,
        3: 1,
        4: 1,
        5: 1,
        6: 1,
        7: 1,
        8: 1,
        9: 1,
        10: 1,
        11: 1,
        12: 2,
        13: 8,
        14: 16,
        15: 32,
        16: 64,
        17: 128,
        18: 256,
        19: 512,
        20: 1024
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
        'itag': 'v1',
        'retries': 3,
        'last_modified': False,
        'etag': False,
    }

    url = u'http://www.baidu.com/s?wd={key_word}'
    api_url = u'http://10.26.225.178:10265/api/common/ZY0054?start={}&end={}'

    def on_start(self):
        self.crawl(self.api_url.format(BEGIN, BEGIN + DIVIDE),
                   save={
                       'end': BEGIN + DIVIDE
                   },
                   callback=self.list_page,
                   force_update=True,
                   headers=self.tungee_header
                   )

    def list_page(self, response):
        names = response.text.split('\n')
        now = response.save['end']
        if len(names) > 1:
            self.crawl(self.api_url.format(now, now + DIVIDE),
                       save={
                           'end': now + DIVIDE
                       },
                       force_update=True,
                       callback=self.list_page,
                       headers=self.tungee_header,
                       retries=20
                       )

        for name in names:
            if len(name.strip()):
                self.crawl(self.url.format(key_word=(name.strip())),
                           proxy='localhost:3128',
                           callback=self.get_ten_page,
                           save={
                               'first': True,
                               'company_name': name.strip(),
                               'type': 'normal',
                               'request_url': self.url.format(key_word=(name.strip())),
                           },
                           headers=self.default_headers,
                           )

    @config(priority=2)
    @catch_status_code_error
    def get_ten_page(self, response):
        request_url = response.save['request_url']
        if response.status_code >= 400 or (response.status_code == 200 and len(response.doc('#content_left')) == 0):
            print 'hhhh'
            self.crawl(request_url,
                       proxy='localhost:3128',
                       callback=self.get_ten_page,
                       force_update=True,
                       save=response.save)
            return

        content_headers = deepcopy(self.default_headers)
        content_headers['Referer'] = response.url

        save = {'company': response.save['company_name']}
        content = []

        for each in response.doc('.c-container').items():
            if response.save['company_name'] in each('em').text() or response.save['company_name'] in each(
                    '.t a').text():

                temp = {}
                try:
                    text = each('.t a').text().replace(' ', '') + ' ' + each('.c-abstract').text().replace(' ', '')
                    url = each('.f13 a.c-showurl').text()

                    temp = {'content': text, 'url': url}
                    content.append(temp)
                except Exception as e:
                    pass

        save.update({'content': content})

        if response.save.get('first'):
            for each in list(response.doc('#page a').items())[:2]:
                self.crawl(each.attr.href,
                           proxy='localhost:3128',
                           callback=self.get_ten_page,
                           save={'first': False, 'company_name': response.save['company_name'],
                                 'type': response.save['type']},
                           headers=self.default_headers,
                           )
        for i in save:
            print i

        return {
            'content': json.dumps(save)
        }
