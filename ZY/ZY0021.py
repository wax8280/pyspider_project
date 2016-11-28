#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-11-15 17:05:44
# Project: ZY0021

from pyspider.libs.base_handler import *
from copy import deepcopy

DIVIDE = 2
BEGIN = 1


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
        'Accept': 'image/webp,image/*,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 10,
    }

    url = 'http://www.baijingapp.com/article/page-{}'

    @config(age=24 * 60)
    def on_start(self):
        self.crawl(self.url.format(BEGIN),
                   callback=self.get_list,
                   force_update=True,
                   etag=False,
                   last_modified=False,
                   proxy='localhost:3128',
                   )

    @config(priority=2)
    def get_list(self, response):
        new_headers = deepcopy(self.default_headers)
        new_headers['Referer'] = response.url

        for i in response.doc('.aw-article-list h3 a').items():
            if i.attr.href:
                self.crawl(
                    i.attr.href,
                    callback=self.get_content,
                    headers=new_headers,
                    proxy='localhost:3128',
                )

        pages = list(response.doc('.pagination li a').items())
        active = list(response.doc('.active a').items())

        if pages and active:
            # 翻页
            if pages[-1].attr.href != active[-1].attr.href:
                self.crawl(
                    pages[-2].attr.href,
                    callback=self.get_list,
                    headers=new_headers,
                    proxy='localhost:3128',
                    force_update=True,
                    etag=False,
                    last_modified=False,
                )
        else:
            self.crawl(
                response.url,
                callback=self.get_list,
                headers=new_headers,
                proxy='localhost:3128',
                force_update=True,
                etag=False,
                last_modified=False,
            )

    @config(priority=3)
    def get_content(self, response):
        return {
            'content': response.text,
            'url': response.url
        }
