#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-11-18 11:19:50
# Project: ZY0030

from pyspider.libs.base_handler import *
from copy import deepcopy
import datetime

BEGIN = 1
DIVIDE = 10
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
        'content-type': 'application/x-www-form-urlencoded',
        'Pragma': 'no-cache',
        'Referer': 'http://www.baijingapp.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    crawl_config = {
        'itag': 'v1',
        'retries': 10,
    }

    url = u'http://www.baijingapp.com/product/download-0__page-{}'

    @every(minutes=24 * 60)
    def on_start(self):
        now_date = unicode((datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
        self.crawl(self.url.format(BEGIN),
                   callback=self.get_list,
                   itag=now_date,
                   force_update=True,
                   etag=False,
                   last_modified=False,
                   headers=self.default_headers,
                   proxy='localhost:3128',
                   validate_cert=False,
                   save={'now': BEGIN, 'try_time': 1, 'now_date': now_date}
                   )

    @config(priority=2)
    @catch_status_code_error
    def get_list(self, response):
        if response.status_code == 200:

            if u'company_main' in response.text:

                for i in range(1, DIVIDE + 1):
                    new_url = self.url.format(response.save.get('now') + i)
                    new_headers = deepcopy(self.default_headers)
                    new_headers['Referer'] = self.url.format(response.save.get('now') + i - 1)

                    self.crawl(
                        new_url,
                        callback=self.get_list,
                        headers=new_headers,
                        itag=response.save.get('now_date'),
                        proxy='localhost:3128',
                        save={'now': response.save.get('now') + DIVIDE, 'try_time': 1},
                        validate_cert=False,
                    )

                new_headers2 = deepcopy(self.default_headers)
                new_headers2['Referer'] = self.url.format(response.save.get('now') + i - 1)

                for i in response.doc('.company_main h4 a').items():
                    self.crawl(
                        i.attr.href,
                        callback=self.get_content,
                        headers=new_headers2,
                        proxy='localhost:3128',
                        validate_cert=False,
                    )

        else:
            if response.save.get('try_time') < SHOULD_TRY_TIME:
                self.crawl(
                    response.url,
                    callback=self.get_list,
                    itag=response.save.get('now_date'),
                    headers=self.default_headers,
                    proxy='localhost:3128',
                    save={'now': response.save.get('now'), 'try_time': response.save.get('try_time') + 1},
                    validate_cert=False,
                )

    @config(priority=3)
    def get_content(self, response):
        # new_headers = deepcopy(self.default_headers)
        # new_headers['Referer'] = response.url
        #
        # for i in response.doc('iframe').items():
        #     if i.attr.src:
        #         url = u'http://open.qichacha.com/open?key=' + re.search(u'key=(.*)$', i.attr.src).groups()[0]
        #         self.crawl(
        #             url,
        #             callback=self.get_qichacha,
        #             headers=new_headers,
        #             # proxy='localhost:3128',
        #             save={'content': response.text, 'url': response.url}
        #         )
        return {
            'content': response.text,
            'url': response.url
        }


        # @config(priority=4)
        # @catch_status_code_error
        # def get_qichacha(self, response):
        #     # 起查查挂了，如果行就加上起查查的数据，不行直接返回产品的数据
        #     if response.status_code == 200:
        #         return {
        #             'content': response.text + u'\n' + response.save.get('content'),
        #             'url': response.save.get('url')
        #         }
        #     else:
        #         return {
        #             'content': response.save.get('content'),
        #             'url': response.save.get('url')
        #         }
