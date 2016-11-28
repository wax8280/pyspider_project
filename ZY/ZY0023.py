#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-11-16 19:20:26
# Project: ZY0022

from pyspider.libs.base_handler import *
from copy import deepcopy

DIVIDE = 2
BEGIN = 1
SHOULD_TRY_TIME = 10


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
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Pragma': 'no-cache',
        'Referer': 'http://youxiputao.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 10,
    }

    url_list = ['http://youxiputao.com/article/index/page/1']

    @every(minutes=24 * 60)
    def on_start(self):
        for each in self.url_list:
            self.crawl(each,
                       callback=self.get_list,
                       force_update=True,
                       # etag=False,
                       # last_modified=False,
                       proxy='localhost:3128',
                       save={'try': 1}
                       )

    @config(priority=2)
    @catch_status_code_error
    def get_list(self, response):
        new_headers = deepcopy(self.default_headers)
        new_headers['Referer'] = response.url

        if response.status_code == 200:
            for i in response.doc('.news-box h4 a').items():
                if i.attr.href:
                    self.crawl(
                        i.attr.href,
                        callback=self.get_content,
                        headers=new_headers,
                        proxy='localhost:3128',
                    )

            # 翻页
            pages = list(response.doc('.pagination.hidden-xs > li > a').items())
            if len(pages)>1:
                if pages[-1].attr.href != u'javascript:void(0)':

                    if u'http://youxiputao.com' not in pages[-2].attr.href:
                        url = u'http://youxiputao.com' + pages[-2].attr.href.replace(u'http://', u'/')
                    else:
                        url = pages[-2].attr.href

                    self.crawl(
                        url,
                        callback=self.get_list,
                        headers=new_headers,
                        proxy='localhost:3128',
                        force_update=True,
                        # etag=False,
                        # last_modified=False,
                        save={'try': 1}
                    )

            # 重新爬取
            else:
                self.crawl(
                    response.url,
                    callback=self.get_list,
                    headers=new_headers,
                    proxy='localhost:3128',
                    save={'try': 1}
                )

        else:
            if response.save.get('try') < SHOULD_TRY_TIME:
                self.crawl(
                    response.url,
                    callback=self.get_list,
                    headers=self.default_headers,
                    proxy='localhost:3128',
                    force_update=True,
                    # etag=False,
                    # last_modified=False,
                    save={'try': response.save.get('try') + 1}
                )

    @config(priority=3)
    def get_content(self, response):
        return {
            'content': response.text,
            'url': response.url
        }
