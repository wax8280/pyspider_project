#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pyspider.libs.base_handler import *
from urllib import urlencode
from copy import deepcopy

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

    url = u'http://sou.zhaopin.com/jobs/searchresult.ashx?'
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
                data = urlencode(
                    {u'jl': u'%E9%80%89%E6%8B%A9%E5%9C%B0%E5%8C%BA', u'kw': name.strip().encode('utf-8'), u'p': 1})

                self.crawl(self.url + data,
                           callback=self.get_list,
                           save={'company_name': name.strip(), 'p': 1}
                           )

    @config(priority=2)
    def get_list(self, response):

        if u'对不起，暂时无符合您条件的职位' not in response.text:
            data = urlencode(
                {u'jl': u'%E9%80%89%E6%8B%A9%E5%9C%B0%E5%8C%BA',
                 u'kw': response.save.get('company_name').encode('utf-8'), u'p': int(response.save.get('p')) + 1})

            self.crawl(self.url + data,
                       callback=self.get_list,
                       save={'company_name': response.save.get('company_name'),
                             'p': int(response.save.get('p')) + 1}
                       )

        new_headers = deepcopy(self.default_headers)
        new_headers.update({'Referer': response.url})
        # get position
        for each in response.doc('#newlist_list_content_table .zwmc a').items():
            self.crawl(
                each.attr.href,
                callback=self.get_content,
                headers=new_headers,
            )

        # get company
        for each in response.doc('#newlist_list_content_table .gsmc a').items():
            self.crawl(
                each.attr.href,
                callback=self.get_content,
                headers=new_headers,
            )

    def get_content(self, response):
        return {
            'content': response.text,
            'url': response.url
        }
