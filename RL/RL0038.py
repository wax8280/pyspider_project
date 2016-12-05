#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pyspider.libs.base_handler import *
from copy import deepcopy
import re
import json
import time

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

    post_headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 3,
    }

    search_url = u'https://www.lagou.com/jobs/list_{}?labelWords=&fromSearch=true&suginput='
    api_url = u'http://112.74.93.18:10265/api/names/zhaopin?start={}&end={}'

    job_url = u'https://www.lagou.com/jobs/{}.html'

    post_url = u'https://www.lagou.com/gongsi/searchPosition.json'

    def get_taskid(self, task):
        return md5string(task['url'] + json.dumps(task['fetch'].get('data', '')) + str(time.time()))

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
                self.crawl(self.search_url.format(name.strip()),
                           callback=self.get_list,
                           headers=self.default_headers,
                           validate_cert=False,
                           proxy='localhost:3128',
                           )

    @config(priority=2)
    def get_list(self, response):

        for i in response.doc('.company-card h2 a').items():
            if i.attr.href:
                new_headers = deepcopy(self.default_headers)
                new_headers.update({'Referer': response.url})

                self.crawl(
                    i.attr.href,
                    callback=self.get_comnapy,
                    headers=new_headers,
                    validate_cert=False,
                    proxy='localhost:3128',
                )

    @config(priority=3)
    def get_comnapy(self, response):
        new_headers = deepcopy(self.post_headers)
        new_headers.update({'Referer': response.url})
        companyid = re.search(u'(\d+)', response.url).groups()[0]

        data = {'companyId': companyid, 'positionFirstType': u'全部', 'pageNo': 1, 'pageSize': 10}

        self.crawl(
            self.post_url,
            method='POST',
            data=data,
            callback=self.get_position,
            headers=new_headers,
            validate_cert=False,
            proxy='localhost:3128',
            save={'p': 1, 'companyId': companyid, 'headers': new_headers}
        )

        return {
            'content': response.text,
            'url': response.url
        }

    @config(priority=4)
    def get_position(self, response):
        result = response.json

        the_result = result['content']['data']['page']['result']
        if not len(the_result) < 10:
            data = {'companyId': response.save.get('companyId'), 'positionFirstType': u'全部',
                    'pageNo': response.save.get('p') + 1, 'pageSize': 10}

            self.crawl(
                self.post_url,
                method='POST',
                data=data,
                callback=self.get_position,
                headers=response.save.get('headers'),
                validate_cert=False,
                proxy='localhost:3128',
                save={'p': response.save.get('p') + 1, 'companyId': response.save.get('companyId'),
                      'headers': response.save.get('headers')}
            )

        for each in the_result:
            self.crawl(
                self.job_url.format(each['positionId']),
                headers=response.save.get('headers'),
                callback=self.get_content,
                validate_cert=False,
                proxy='localhost:3128',
            )

    @config(priority=5)
    def get_content(self, response):
        return {
            'content': response.text,
            'url': response.url
        }
