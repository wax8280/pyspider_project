# coding: utf-8
from pyspider.libs.base_handler import *
import re
from copy import deepcopy
from random import choice
import json
import time

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
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded',
        'Pragma': 'no-cache',
        'Referer': 'https://www.affplus.com/?q=&hPP=20&idx=offers&p={}&is_v=1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    crawl_config = {
        'itag': 'v1',
        'retries': 10,
    }

    url = 'https://zgzw7l3f7q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%203.13.1%3Binstantsearch.js%201.5.0&x-algolia-application-id=ZGZW7L3F7Q&x-algolia-api-key=91d5e884f7efc91df3d907e37c8145fd'
    base = '{"requests":[{"indexName":"offers","params":"query=&hitsPerPage=20&maxValuesPerFacet=500&page='
    after = '&facets=%5B%22network_name%22%2C%22price%22%2C%22mcates%22%2C%22payout_type%22%2C%22ocountries%22%5D&tagFilters="}]}'

    def get_taskid(self, task):
        if task['url'] == self.url:
            return md5string(task['url'] + json.dumps(task['fetch'].get('data', '')) + str(time.time()))
        else:
            return md5string(task['url'] + json.dumps(task['fetch'].get('data', '')))

    @every(minutes=24 * 60)
    def on_start(self):
        data = self.base + str(BEGIN) + self.after
        new_header = deepcopy(self.default_headers)
        new_header['Referer'] = new_header['Referer'].format(BEGIN)

        self.crawl(self.url,
                   callback=self.get_list,
                   method='POST',
                   data=data,
                   force_update=True,
                   etag=False,
                   last_modified=False,
                   headers=new_header,
                   # proxy='localhost:3128',
                   save={'page_num': BEGIN + 1, 'last': ''},
                   validate_cert=False,

                   )

    @config(priority=2)
    def get_list(self, response):
        last = re.search(u'"hits":\[\{"id":(.*?),', response.text)
        print response.save.get('last')
        if u'hits\":[]' not in response.text and last and last.groups()[0] != response.save.get('last'):
            data = self.base + str(response.save.get('page_num')) + self.after
            new_header = deepcopy(self.default_headers)
            new_header['Referer'] = new_header['Referer'].format(response.save.get('page_num'))

            self.crawl(
                self.url,
                callback=self.get_list,
                method='POST',
                data=data,
                force_update=True,
                etag=False,
                last_modified=False,
                headers=new_header,
                # proxy='localhost:3128',
                save={'page_num': response.save.get('page_num') + 1, 'last': last.groups()[0]},
                validate_cert=False,
            )

        return {
            'content': response.text
        }
