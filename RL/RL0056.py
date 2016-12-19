# !/usr/bin/env python
# coding: utf-8

from pyspider.libs.base_handler import *
from copy import deepcopy
import re

BEGIN = 0
DIVIDE = 1


class Handler(BaseHandler):
    retry_delay = {
        1: 0,
        2: 2,
        3: 4,
        4: 8,
        5: 16
    }

    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

    api_url = 'http://120.77.12.100:10265/api/common/RL0056?start={}&end={}'
    search_url = 'https://www.so.com/s'

    def on_start(self):
        self.crawl(self.api_url.format(BEGIN, BEGIN + DIVIDE),
                   callback=self.list_page,
                   force_update=True,
                   save={
                       'now': BEGIN + DIVIDE,
                   }
                   )

    @config(priority=2)
    def list_page(self, response):
        text = response.text.strip()
        product_list = text.split('\n')

        for name in product_list:
            self.crawl(
                self.search_url,
                params={
                    'q': name + ' site:qichacha.com'
                },
                callback=self.get_list,
                validate_cert=False,
                headers=self.default_headers,
                proxy='localhost:3128',
            )

        if '' in product_list and len(product_list) <= 1:
            return

        self.crawl(
            self.api_url.format(response.save.get('now'), response.save.get('now') + DIVIDE),
            callback=self.list_page,
            headers=self.default_headers,
            save={
                'now': response.save.get('now') + DIVIDE,
            }
        )

    @config(priority=3)
    def get_list(self, response):

        new_headers = deepcopy(self.default_headers)
        new_headers.update({
            'Referer': response.url,
        })

        # 翻页
        for page in response.doc('#page a').items():
            self.crawl(
                page.attr.href,
                callback=self.get_list,
                validate_cert=False,
                headers=new_headers,
                proxy='localhost:3128',
            )

        for a in response.doc('a.m').items():
            self.crawl(
                a.attr.href,
                callback=self.get_link,
                validate_cert=False,
                headers=new_headers,
                proxy='localhost:3128',
            )

    @config(priority=4)
    def get_link(self, response):
        link_gen = re.search('window.location.replace\("(.*?)"\)', response.text)
        if link_gen:
            new_headers = deepcopy(self.default_headers)
            new_headers.update({
                'Referer': response.url,
            })

            self.crawl(
                link_gen.group(1),
                callback=self.get_content,
                headers=new_headers,
                validate_cert=False,
                proxy='localhost:3128',
            )

    @config(priority=5)
    def get_content(self, response):
        return {
            'content': response.text,
            'url': response.url,
        }
