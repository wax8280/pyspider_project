#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-01-06 09:55:16
# Project: dytt8

from pyspider.libs.base_handler import *
import re
from bs4 import BeautifulSoup

RESULT_PATH = './result/dytt8/'


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
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
    }

    crawl_config = {
        'itag': 'v1',
        'retries': 10,
    }

    all_url = {
        'oumei_url': 'http://www.dytt8.net/html/gndy/oumei/list_7_{}.html',
        'rihan_url': 'http://www.dytt8.net/html/gndy/rihan/list_6_{}.html',
        'guonei_url': 'http://www.dytt8.net/html/gndy/china/list_4_{}.html',
        'zuixin_url': 'http://www.dytt8.net/html/gndy/dyzz/list_23_{}.html',
        'zhonghe_url': 'http://www.dytt8.net/html/gndy/jddy/list_63_{}.html',
    }

    def on_start(self):
        for k, v in self.all_url.items():
            self.crawl(v.format(1),
                       callback=self.get_list,
                       force_update=True,
                       headers=self.default_headers,
                       save={'now': 1, 'type': k}
                       )

    def get_list(self, response):
        soup = BeautifulSoup(response.text)

        a = soup.find_all('a', attrs={'class': 'ulink'}, href=re.compile('[\d]+.html'))
        for i in a:
            self.crawl(
                'http://www.dytt8.net' + i['href'],
                callback=self.get_content,
                headers=self.default_headers,
                save={'now': response.save['now'], 'type': response.save['type']}
            )

        # 下一页
        if u'您要访问的页面已被删除或不存在' not in response.text:
            self.crawl(
                self.all_url[response.save['type']].format(response.save['now'] + 1),
                callback=self.get_list,
                headers=self.default_headers,
                save={'now': response.save['now'] + 1, 'type': response.save['type']}
            )

    def get_content(self, response):
        num = re.search('/([\d]*).html', response.url).group(1)
        name = response.save['type'] + '_' + str(response.save['now']) + '_' + num

        with open(RESULT_PATH + str(name), 'wb') as f:
            f.write(response.text.encode('utf-8'))
