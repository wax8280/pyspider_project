#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pyspider.libs.base_handler import *
from urllib import urlencode

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

    url = u'http://zhaopin.baidu.com/api/async?'
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
                    {u'query': name.encode('utf-8'), u'salary': u'', u'welfare': u'', u'education': u'', u'sort_key': u'', u'city': u'',
                     u'district': u'', u'experience': u'', u'employertype': u'', u'jobfirstclass': u'',
                     u'jobsecondclass': u'', u'jobthirdclass': u'', u'date': u'', u'detailmode': u'close', u'rn': 0,
                     u'pn': 30})

                self.crawl(self.url + data,
                           callback=self.get_list,
                           save={'first': True, 'company_name': name.strip(), 'rn': 0}
                           )

    @config(priority=2)
    def get_list(self, response):
        result = response.json
        if not result['data']['data'].has_key('disp_data'):
            return

        if not len(result['data']['data']['disp_data']) < 30:
            data = urlencode(
                {u'query': response.save.get('company_name').encode('utf-8'), u'salary': u'', u'welfare': u'', u'education': u'',
                 u'sort_key': u'', u'city': u'',
                 u'district': u'', u'experience': u'', u'employertype': u'', u'jobfirstclass': u'',
                 u'jobsecondclass': u'', u'jobthirdclass': u'', u'date': u'', u'detailmode': u'close',
                 u'rn': response.save.get('rn'),
                 u'pn': int(response.save.get('rn')) + 30})

            self.crawl(self.url + data,
                       callback=self.get_list,
                       save={'first': True, 'company_name': response.save.get('company_name'),
                             'rn': int(response.save.get('rn')) + 30}
                       )

        for each in result['data']['data']['disp_data']:
            self.crawl(
                each['url'],
                callback=self.get_content,
            )

    def get_content(self, response):
        return {
            'content': response.text,
            'url': response.url
        }
