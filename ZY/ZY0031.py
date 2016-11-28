#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-11-18 15:57:55
# Project: ZY0031_2

from pyspider.libs.base_handler import *
from copy import deepcopy
import datetime

BEGIN = 1
DIVIDE = 4


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
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded',
        'Pragma': 'no-cache',
        'Referer': 'http://odigger.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    crawl_config = {
        'itag': 'v1',
        'retries': 10,
    }

    url = u'http://odigger.com/?_qf__search_number=&bcp=&is=1&s=&post_type=affiliate_offer&nw_id=&ca_id=&co_id=&pt_id=&num=100&payouts%5Bcpc%5D=1&payouts%5Bcpm%5D=1&payouts%5Bcps%5D=1&payouts%5Bcpl%5D=1&payouts%5Bcpa%5D=1&payouts%5Brevshare%5D=1&fields%5Btitle%5D=1&fields%5Bnetwork%5D=1&fields%5Bcategories%5D=1&fields%5Bdescription%5D=1&_qf__search_filter=&orderBy=created_at&direction=DESC&page={}'

    # def get_taskid(self, task):
    #     return md5string(task['url'] + json.dumps(task['fetch'].get('data', '')) + str(time.time()))

    @every(minutes=24 * 60)
    def on_start(self):
        now_date = unicode((datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
        self.crawl(self.url.format(BEGIN),
                   callback=self.get_list,
                   force_update=True,
                   etag=False,
                   last_modified=False,
                   headers=self.default_headers,
                   proxy='localhost:3128',
                   validate_cert=False,
                   itag=now_date,
                   save={'now': BEGIN, 'now_date': now_date}
                   )

    @config(priority=2)
    def get_list(self, response):

        if u'No Results Found For' not in response.text:

            for i in range(1, DIVIDE + 1):
                new_url = self.url.format(response.save.get('now') + i)
                self.crawl(
                    new_url,
                    callback=self.get_list,
                    force_update=True,
                    etag=False,
                    last_modified=False,
                    headers=self.default_headers,
                    itag=response.save.get('now_date'),
                    proxy='localhost:3128',
                    save={'now': response.save.get('now') + DIVIDE,
                          'now_date': response.save.get('now_date')},
                    validate_cert=False,
                )

            new_headers = deepcopy(self.default_headers)
            new_headers['Referer'] = response.url

            for i in response.doc('.affiliate_offer-results-table .title a').items():
                if u'odigger.com/affiliate-offer' in i.attr.href:
                    self.crawl(
                        i.attr.href,
                        callback=self.get_content,
                        headers=new_headers,
                        validate_cert=False,
                    )

            return {
                'content': response.text,
                'url': response.url
            }

    @config(priority=3)
    def get_content(self, response):
        return {
            'content': response.text,
            'url': response.url
        }
