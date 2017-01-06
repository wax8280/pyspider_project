#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-01-05 17:54:22
# Project: 162wp

from pyspider.libs.base_handler import *
import re

ROOT_PATH = './162wp'
LIST_PATH = './162wp/list/'
RESULT_PATH = './162wp/result/'


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

    url_page = 'http://www.162wp.com/dianyingziyuan/index_{}.html'

    def on_start(self):
        self.crawl('http://www.162wp.com/dianyingziyuan',
                   callback=self.get_list,
                   force_update=True,
                   headers=self.default_headers,
                   save={'now': 1}
                   )

    def get_list(self, response):
        now = response.save['now']
        # 写文件
        with open(LIST_PATH + str(now), 'wb') as f:
            f.write(response.text.encode('utf-8'))

        # 翻页
        self.crawl(
            self.url_page.format(now + 1),
            save={'now': now + 1},
            callback=self.get_list,
            headers=self.default_headers,
        )

        for table in response.doc('table').items():
            if table.attr.bordercolor == '#8BACE2':
                for a in table('table div a').items():
                    self.crawl(
                        a.attr.href,
                        callback=self.get_content,
                        headers=self.default_headers,
                        save={'now': now},
                    )

    def get_content(self, response):
        num = re.search('/[\d]+.html', response.url).group(0)
        with open(RESULT_PATH + str(response.save['now']) + '_' + str(num), 'wb') as f:
            f.write(response.text.encode('utf-8'))
