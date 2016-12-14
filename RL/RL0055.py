#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-12-05 17:36:14
# Project: RL0037

from pyspider.libs.base_handler import *
from copy import deepcopy
import re

BEGIN = 1
DIVIDE = 5
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

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 10,
    }
    url = 'http://jobs.51job.com/all/co{}.html'

    def on_start(self):
        self.crawl(
            self.url.format(BEGIN),
            save={
                'now': BEGIN,
                'try_time': 0
            },
            callback=self.list_page,
            force_update=True,
            headers=self.default_headers,
        )

    @catch_status_code_error
    def list_page(self, response):

        if response.status_code == 200 and u'tCompany_full' in response.text:

            if response.save['now'] >= 4163642:
                return

            for i in range(response.save['now'] + 1, response.save['now'] + DIVIDE):
                self.crawl(
                    self.url.format(i),
                    save={
                        'now': i,
                        'try_time': 0
                    },
                    callback=self.list_page,
                    headers=self.default_headers,
                )

            hidTotal = re.search('<input type="hidden" id="hidTotal" name="hidTotal" value="(.*?)">', response.text)

            if hidTotal:
                hidTotal = int(hidTotal.group(1))
                print hidTotal
                now = 1
                new_headers = deepcopy(self.default_headers)
                new_headers['Referer'] = self.url.format(response.save['now'])

                self.crawl(
                    self.url.format(response.save['now']),
                    save={
                        'hidTotal': hidTotal,
                        'now': now,
                        'Referer': self.url.format(response.save['now']),
                        'try_time': 0,
                    },
                    method='POST',
                    data={'hidTotal': hidTotal, 'pageno': now},
                    callback=self.get_list,
                    headers=new_headers,
                )

            return {
                'content': response.text,
                'url': response.url,
            }

        elif response.save['try_time'] < TRY_TIME:
            self.crawl(
                self.url.format(response.save['now']),
                save={
                    'now': response.save['now'],
                    'try_time': response.save['try_time'] + 1
                },
                callback=self.list_page,
                headers=self.default_headers,
            )

    @config(priority=2)
    @catch_status_code_error
    def get_list(self, response):

        if response.status_code == 200 and u'd' in response.text:
            now = response.save['now']
            hidTotal = response.save['hidTotal']
            Referer = response.save['Referer']
            new_headers = deepcopy(self.default_headers)
            new_headers['Referer'] = Referer

            for i in response.doc('.t1 a').items():
                self.crawl(
                    i.attr.href,
                    callback=self.get_content,
                    headers=new_headers,
                )

            if now * 20 < int(hidTotal):
                now += 1

                self.crawl(
                    Referer,
                    save={
                        'hidTotal': hidTotal,
                        'now': now,
                        'Referer': Referer,
                        'try_time': 0,
                    },
                    method='POST',
                    data={'hidTotal': hidTotal, 'pageno': now},
                    callback=self.get_list,
                    headers=new_headers,
                )

        elif response.save['try_time'] < TRY_TIME:
            hidTotal = response.save['hidTotal']
            now = response.save['now']

            new_headers = deepcopy(self.default_headers)
            new_headers['Referer'] = self.url.format(response.save['now'])

            self.crawl(
                self.url.format(response.save['now']),
                save={
                    'hidTotal': hidTotal,
                    'now': now,
                    'Referer': self.url.format(response.save['now']),
                    'try_time': response.save['try_time'] + 1,
                },
                method='POST',
                data={'hidTotal': hidTotal, 'pageno': now},
                callback=self.get_list,
                headers=new_headers,
            )

    @config(priority=3)
    @catch_status_code_error
    def get_content(self, response):
        if response.status_code == 200 and u'd' in response.text:

            return {
                'content': response.text,
                'url': response.url
            }

        elif response.save['try_time'] < TRY_TIME:
            Referer = response.save['Referer']
            now = response.save['now']
            hidTotal = response.save['hidTotal']

            new_headers = deepcopy(self.default_headers)
            new_headers['Referer'] = Referer

            self.crawl(
                Referer,
                save={
                    'hidTotal': hidTotal,
                    'now': now,
                    'Referer': Referer,
                    'try_time': response.save['try_time'] + 1,
                },
                method='POST',
                data={'hidTotal': hidTotal, 'pageno': now},
                callback=self.get_list,
                headers=new_headers,
            )