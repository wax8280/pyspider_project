#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-01-10 09:37:19
# Project: verycd_1


from pyspider.libs.base_handler import *
import re
import time

RESULT_PATH = './result/verycd/china_result/'


class Handler(BaseHandler):
    retry_delay = {
        0: 1,
        1: 1,
        2: 1,
        3: 1,

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

    data = {
        'username': 'wax8280@163.com',
        'password': '5588612',
        'save_cookie': '1',
    }

    url = 'http://www.verycd.com/archives/music/china/{}.html'

    def on_start(self):
        self.crawl('http://www.verycd.com/',
                   callback=self.get_cookies,
                   force_update=True,
                   headers=self.default_headers,
                   save={'now': 1}
                   )

    def get_cookies(self, response):

        self.crawl('http://secure.verycd.com/signin',
                   method='POST',
                   priority=1,
                   # cookies=response.cookies,
                   data=self.data,
                   headers=self.post_headers,
                   allow_redirects=False,
                   force_update=True,
                   save={'now': response.save['now']},
                   callback=self.login,
                   )

    def login(self, response):
        if 'ok' not in response.text:
            self.crawl('http://secure.verycd.com/signin',
                       method='POST',
                       priority=1,
                       data=self.data,
                       headers=self.post_headers,
                       allow_redirects=False,
                       force_update=True,
                       save={'now': response.save['now']},
                       callback=self.get_list,
                       )
            return

        self.crawl(
            self.url.format(str(response.save['now']).zfill(5)),
            priority=2,
            headers=self.default_headers,
            allow_redirects=False,
            force_update=True,
            cookies=response.cookies,
            save={'now': response.save['now']},
            callback=self.get_list,
        )

    def get_list(self, response):

        for a in response.doc('.archiveResourceList a').items():
            self.crawl(
                a.attr.href,
                callback=self.get_content,
                headers=self.default_headers,
                priority=3,
                allow_redirects=False,
                cookies=response.cookies,
            )

        self.crawl('http://secure.verycd.com/signin',
                   method='POST',
                   priority=1,
                   # cookies=response.cookies,
                   data=self.data,
                   headers=self.post_headers,
                   allow_redirects=False,
                   force_update=True,
                   save={'now': response.save['now'] + 1},
                   callback=self.login,
                   )

    def get_content(self, response):
        if u'该内容尚未提供权利证明' in response.text:
            self.crawl(
                'http://www.verycd.com/',
                headers=self.default_headers,
                priority=4,
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
