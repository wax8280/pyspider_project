#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-01-05 14:01:00
# Project: verycd_detail

from pyspider.libs.base_handler import *
import re
import subprocess
import time

DIVIDE = 100
URL_PATH = './occident'
RESULT_PATH = './occident_result/'


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

    post_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'http://www.verycd.com/',
        'X-Requested-With': 'XMLHttpRequest'
    }

    crawl_config = {
        'itag': 'v1',
        'retries': 10,
    }

    url = 'http://www.verycd.com/topics/{}'

    @staticmethod
    def read_last_lines(file_path, start, end):
        command_ = 'sed -n "{start},{end}p" {file_path}'.format(start=start, end=end, file_path=file_path)
        fh = subprocess.Popen(command_, stdout=subprocess.PIPE, shell=True)
        return list(fh.stdout.readlines())

    def on_start(self):
        self.crawl('http://www.verycd.com/',
                   callback=self.login,
                   force_update=True,
                   headers=self.default_headers,
                   save={'now': 1}
                   )

    def login(self, response):
        data = {
            'username': 'wax8280@163.com',
            'password': '5588612',
            'save_cookie': '1',
        }

        self.crawl('http://secure.verycd.com/signin',
                   method='POST',
                   priority=2,
                   cookies=response.cookies,
                   data=data,
                   headers=self.post_headers,
                   allow_redirects=False,
                   force_update=True,
                   save={'now': response.save['now']},
                   callback=self.get_list,
                   )

    def get_list(self, response):
        if 'ok' not in response.text:
            data = {
                'username': 'wax8280@163.com',
                'password': '5588612',
                'save_cookie': '1',
            }

            self.crawl('http://secure.verycd.com/signin',
                       method='POST',
                       priority=1,
                       data=data,
                       headers=self.post_headers,
                       allow_redirects=False,
                       force_update=True,
                       save={'now': response.save['now']},
                       callback=self.get_list,
                       )
            return

        now = response.save['now']
        l = self.read_last_lines(URL_PATH, now, now + DIVIDE)

        for index, each in enumerate(l):
            if each.strip():
                self.crawl(
                    'http://www.verycd.com/topics/{}/'.format(each.strip()),
                    cookies=response.cookies,
                    headers=self.default_headers,
                    priority=3,
                    save={'now': now + index},
                    callback=self.get_content,
                    allow_redirects=False,
                )

        data = {
            'username': 'wax8280@163.com',
            'password': '5588612',
            'save_cookie': '1',
        }

        self.crawl('http://secure.verycd.com/signin',
                   method='POST',
                   priority=1,
                   data=data,
                   headers=self.post_headers,
                   allow_redirects=False,
                   force_update=True,
                   save={'now': response.save['now'] + DIVIDE},
                   callback=self.get_list,
                   )

    def get_content(self, response):
        if u'该内容尚未提供权利证明' in response.text:
            self.crawl(
                'http://www.verycd.com/',
                headers=self.default_headers,
                priority=2,
                save={'now': response.save['now']},
                callback=self.login,
                force_update=True,
                allow_redirects=False,
            )
            response.raise_for_status()
        else:
            gen = re.search('(\d+)', response.url)
            if gen:
                name = gen.group(0)
            else:
                name = str(time.time())

            with open(RESULT_PATH + str(name), 'wb') as f:
                f.write(response.text.encode('utf-8'))
