#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pyspider.libs.base_handler import *
from copy import deepcopy
import re

BEGIN = 0
DIVIDE = 2


class Handler(BaseHandler):
    retry_delay = {
        1: 1,
        2: 2,
        3: 8,
    }

    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    tungee_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 3,
    }

    url = u'http://www.jobui.com/cmp?keyword={}'
    api_url = u'http://112.74.93.18:10265/api/names/zhaopin?start={}&end={}'

    def on_start(self):
        self.crawl(self.api_url.format(BEGIN, BEGIN + DIVIDE),
                   save={
                       'end': BEGIN + DIVIDE
                   },
                   callback=self.list_page, force_update=True, headers=self.tungee_header)

    def list_page(self, response):
        names = response.text.split('\n')
        now = response.save['end']
        if len(names) > 1:
            self.crawl(self.api_url.format(now, now + DIVIDE),
                       save={
                           'end': now + DIVIDE
                       },
                       callback=self.list_page,
                       headers=self.tungee_header
                       )

        for name in names:
            if len(name.strip()):
                self.crawl(self.url.format(name.strip()),
                           callback=self.get_list,
                           save={'company_name': name.strip(), 'p': 1}
                           )

    @config(priority=2)
    def get_list(self, response):

        for i in response.doc('.atn-li .atn-content h2 a').items():
            if i.attr.href:
                new_headers = deepcopy(self.default_headers)
                new_headers.update({'Referer': response.url})

                self.crawl(
                    i.attr.href,
                    callback=self.get_comnapy,
                    headers=new_headers,
                )

    def get_comnapy(self, response):
        new_headers = deepcopy(self.default_headers)
        new_headers.update({'Referer': response.url})

        self.crawl(
            response.url + u'jobs/p1/',
            callback=self.get_position,
            headers=new_headers,
            save={'p': 1}
        )

        return {
            'content': response.text,
            'url': response.url
        }

    def get_position(self, response):
        if u'该公司暂无招聘职位' not in response.text:

            new_headers = deepcopy(self.default_headers)
            new_headers.update({'Referer': response.url})

            for i in response.doc('.col-title410 a').items():
                self.crawl(
                    i.attr.href,
                    callback=self.get_content,
                    headers=new_headers,
                )

            url = re.sub(u'p\d+', u'p' + unicode(response.save.get('p') + 1), response.url)

            self.crawl(
                url,
                callback=self.get_position,
                headers=new_headers,
                save={'p': response.save.get('p') + 1}
            )


    def get_content(self, response):
        return {
            'content': response.text,
            'url': response.url
        }

