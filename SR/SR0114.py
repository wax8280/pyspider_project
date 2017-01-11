#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-01-09 11:34:52
# Project: ZY0060

from pyspider.libs.base_handler import *
import time
import json

DIVIDE = 4


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
        'headers': default_headers,
        'retries': 5,
    }

    l = ["http://www.beianhao.net/d/icpbeianindex/A/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/B/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/C/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/D/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/E/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/F/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/G/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/H/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/I/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/J/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/K/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/L/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/M/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/N/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/O/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/P/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/Q/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/R/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/S/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/T/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/U/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/V/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/W/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/X/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/Y/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/Z/list-{}.phone.html",
         "http://www.beianhao.net/d/icpbeianindex/Other/list-{}.phone.html"]

    START = 0
    DELTA = 5

    def get_taskid(self, task):
        return md5string(task['url'] + json.dumps(task['fetch'].get('data', '')))

    def get_time(self):
        return str(int(time.time() * 1000))

    def on_start(self):

        for index, i in enumerate(self.l):
            self.crawl(
                i.format(1),
                save={
                    'cursor': 1,
                    'index': index,
                },
                callback=self.get_list,
                force_update=True,
                proxy='localhost:3128',

            )

    @config(priority=2)
    def get_list(self, response):
        index = response.save['index']
        cursor = response.save['cursor']

        if response.doc('.pageNumbers a:last').attr.class_ != 'current':
            for i in range(1, DIVIDE):
                self.crawl(
                    self.l[index].format(cursor + i),
                    save={
                        'cursor': cursor + i,
                        'index': index,
                    },
                    callback=self.get_list,
                    proxy='localhost:3128',

                )

        for a in response.doc('.subjects h3 a').items():
            self.crawl(
                a.attr.href,
                headers=self.default_headers,
                callback=self.get_content,
                proxy='localhost:3128',

            )

    @config(priority=3)
    def get_content(self, response):
        if 'beianhao' in response.text:
            return {
                'content': response.text,
                'url': response.url,
            }
        else:
            response.raise_for_status()
