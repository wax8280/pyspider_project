#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pyspider.libs.base_handler import *
import json
import re

# 末页
END = 155109
# 始页
BEGIN = 6
# 每组长度
DIVIDE = 20


class Handler(BaseHandler):
    retry_delay = {
        0: 1,
        1: 1,
        2: 5,
        3: 10,
        4: 30,
        5: 60
    }
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 5,
        'proxy': 'localhost:3128',
    }
    base_company_url = 'https://www.lagou.com/gongsi/{}.html'
    position_url = 'https://www.lagou.com/gongsi/searchPosition.json'

    def get_taskid(self, task):
        return md5string(task['url'] + json.dumps(task['fetch'].get('data', '')))

    # @every(minutes=24 * 60 * 60)
    def on_start(self):
        self.crawl(
            self.base_company_url.format(str(BEGIN)),
            callback=self.comnapy_detail_page,
            force_update=True,
            validate_cert=False,
            save={'now': BEGIN}
        )

    @config(priority=3)
    @catch_status_code_error
    def comnapy_detail_page(self, response):

        if (response.save['now'] - BEGIN + 1) % DIVIDE == 1 and response.save['now'] < END:
            for i in range(response.save['now'], min(response.save['now'] + DIVIDE, END)):
                self.crawl(
                    self.base_company_url.format(str(i + 1)),
                    callback=self.comnapy_detail_page,
                    force_update=False,
                    validate_cert=False,
                    save={'now': i + 1}
                )

        if response.ok:
            self.crawl(
                self.position_url,
                callback=self.position_detail_page,
                       force_update=False,
                validate_cert=False,
                method='POST',
                       data={
                           'companyId': unicode(response.save['now']),
                           'positionFirstType': u'全部',
                           'pageNo': u'1',
                             'pageSize': u'10', },
                save={'now': response.save['now']}
            )

            return {
                'content': response.text,
                'url': response.url
            }

    @config(priority=4)
    def position_detail_page(self, response):
        result = response.json
        result.update({u'companyId': unicode(response.save['now'])})

        if len(result[u'content'][u'data'][u'page'][u'result']) != 0:
            self.crawl(
                self.position_url,
                callback=self.position_detail_page,
                       force_update=False,
                validate_cert=False,
                method='POST',
                       data={
                           'companyId': unicode(response.save['now']),
                           'positionFirstType': u'全部',
                             'pageNo': int(result[u'content'][u'data'][u'page'][u'pageNo']) + 1,
                             'pageSize': u'10', },
                save={'now': response.save['now']})
            return {
                'content': response.text,
                'path': re.match('.*?//(.*)$', response.url).groups()[0] + '&companyId_' + str(response.save['now']) +
                        '&pageNo_' + str(result[u'content'][u'data'][u'page'][u'pageNo']),
                'url': response.url
            }
