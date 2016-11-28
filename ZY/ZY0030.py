#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-11-18 11:19:50
# Project: ZY0030

from pyspider.libs.base_handler import *

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
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded',
        'Pragma': 'no-cache',
        'Referer': 'http://www.offervault.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    crawl_config = {
        'itag': 'v1',
        'retries': 10,
    }

    url = u'http://www.offervault.com/?perPage=100&page={}'

    # def get_taskid(self, task):
    #     return md5string(task['url'] + json.dumps(task['fetch'].get('data', '')) + str(time.time()))

    @every(minutes=24 * 60)
    @config(age=20 * 60)
    def on_start(self):
        self.crawl(self.url.format(BEGIN),
                   callback=self.get_list,
                   force_update=True,
                   etag=False,
                   last_modified=False,
                   headers=self.default_headers,
                   # proxy='localhost:3128',
                   validate_cert=False,
                   save={'now': BEGIN + 1, 'last_url': self.url.format(BEGIN)}
                   )

    @config(priority=2)
    def get_list(self, response):
        if response.save.get('last_url') == response.url:
            new_url = self.url.format(response.save.get('now'))
            self.crawl(
                new_url,
                callback=self.get_list,
                force_update=True,
                etag=False,
                last_modified=False,
                headers=self.default_headers,
                # proxy='localhost:3128',
                save={'now': response.save.get('now') + 1, 'last_url': new_url},
                validate_cert=False,
            )

        return {
            'content': response.text,
            'url': response.url
        }
