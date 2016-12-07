#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pyspider.libs.base_handler import *
from copy import deepcopy
import re

BEGIN = 0
DIVIDE = 2
TRY_TIME = 10


class Handler(BaseHandler):
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
        'retries': 10,
    }

    url = u'http://www.jobui.com/cmp?keyword={}'
    api_url = u'http://10.26.225.178:10265/api/names/zhaopin/zhiyou?start={}&end={}'

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
                           proxy='localhost:3128',
                           headers=self.default_headers,
                           save={
                               'company_name': name.strip(),
                               'p': 1,
                               'last_url': self.url.format(name.strip()),
                               'try_time': 0
                           }
                           )

    @config(priority=2)
    @catch_status_code_error
    def get_list(self, response):
        if response.status_code == 200 and u'职友' in response.text:

            for i in response.doc('.atn-li .atn-content h2 a').items():
                if i.attr.href:
                    new_headers = deepcopy(self.default_headers)
                    new_headers.update({'Referer': response.url})

                    self.crawl(
                        i.attr.href,
                        callback=self.get_comnapy,
                        headers=new_headers,
                        proxy='localhost:3128',
                        save={
                            'try_time': 0,
                            'last_url': i.attr.href,
                            'headers': new_headers

                        }
                    )

        elif response.save['try_time'] < TRY_TIME:
            self.crawl(response.save['last_url'],
                       callback=self.get_list,
                       proxy='localhost:3128',
                       headers=self.default_headers,
                       save={
                           'company_name': response.save['company_name'],
                           'p': response.save['p'],
                           'last_url': response.save['last_url'],
                           'try_time': response.save['try_time'] + 1,
                       }
                       )

    @config(priority=3)
    @catch_status_code_error
    def get_comnapy(self, response):
        if response.status_code == 200 and u'职友' in response.text:

            new_headers = deepcopy(self.default_headers)
            new_headers.update({'Referer': response.url})

            self.crawl(
                response.url + u'jobs/p1/',
                callback=self.get_position,
                headers=new_headers,
                proxy='localhost:3128',
                save={
                    'p': 1,
                    'try_time': 0,
                    'last_url': response.url + u'jobs/p1/',
                    'headers': new_headers,
                }
            )

            return {
                'content': response.text,
                'url': response.url
            }

        elif response.save['try_time'] < TRY_TIME:

            self.crawl(
                response.save['last_url'],
                callback=self.get_comnapy,
                headers=response.save['headers'],
                proxy='localhost:3128',
                save={
                    'try_time': response.save['try_time'] + 1,
                    'last_url': response.save['last_url'],
                    'headers': response.save['headers'],
                }
            )

    @config(priority=4)
    @catch_status_code_error
    def get_position(self, response):
        if response.status_code == 200 and u'职友' in response.text:

            if u'该公司暂无招聘职位' not in response.text and u'最近无' not in response.text:

                new_headers = deepcopy(self.default_headers)
                new_headers.update({'Referer': response.url})

                for i in response.doc('.col-title410 a').items():
                    self.crawl(
                        i.attr.href,
                        callback=self.get_content,
                        headers=new_headers,
                        proxy='localhost:3128',
                        save={
                            'try_time': 0,
                            'last_url': i.attr.href,
                            'headers': new_headers,
                        }
                    )

                url = re.sub(u'p\d+', u'p' + unicode(response.save.get('p') + 1), response.url)

                self.crawl(
                    url,
                    callback=self.get_position,
                    headers=new_headers,
                    proxy='localhost:3128',
                    save={
                        'p': response.save.get('p') + 1,
                        'try_time': 0,
                        'headers': new_headers,
                        'last_url': url,

                    }
                )

        elif response.save['try_time'] < TRY_TIME:
            self.crawl(
                response.save['last_url'],
                callback=self.get_position,
                headers=response.save['headers'],
                proxy='localhost:3128',
                save={
                    'p': response.save['p'],
                    'try_time': response.save['try_time'],
                    'last_url': response.save['last_url'],
                    'headers': response.save['headers']
                }
            )

    @config(priority=5)
    @catch_status_code_error
    def get_content(self, response):
        if response.status_code == 200 and u'职友' in response.text:
            return {
                'content': response.text,
                'url': response.url
            }

        elif response.save['try_time'] < TRY_TIME:
            self.crawl(
                response.save['last_url'],
                callback=self.get_content,
                headers=response.save['headers'],
                proxy='localhost:3128',
                save={
                    'try_time': response.save['try_time'] + 1,
                    'last_url': response.save['last_url'],
                    'headers': response.save['headers'],
                }
            )
