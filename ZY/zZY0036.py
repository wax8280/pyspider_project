# coding: utf-8

from pyspider.libs.base_handler import *
import re
from copy import deepcopy
from random import choice
import json

the_proxy = ('nbt_spider:nbt_spider@45.35.236.206:8888', 'nbt_spider:nbt_spider@172.106.64.215:8888',
             'nbt_spider:nbt_spider@45.35.226.202:8888', 'nbt_spider:nbt_spider@172.106.63.110:8888',
             'nbt_spider:nbt_spider@172.106.68.104:8888', 'nbt_spider:nbt_spider@172.106.46.78:8888',
             'nbt_spider:nbt_spider@172.106.68.103:8888', 'nbt_spider:nbt_spider@45.34.13.137:8888',
             'nbt_spider:nbt_spider@172.107.13.164:8888', 'nbt_spider:nbt_spider@172.106.63.107:8888',
             'nbt_spider:nbt_spider@104.217.249.173:8888', 'nbt_spider:nbt_spider@107.160.73.98:8888',
             'nbt_spider:nbt_spider@107.160.125.157:8888', 'nbt_spider:nbt_spider@107.160.125.146:8888',
             'nbt_spider:nbt_spider@104.217.249.184:8888', 'nbt_spider:nbt_spider@107.160.73.108:8888',
             'nbt_spider:nbt_spider@104.217.249.190:8888', 'nbt_spider:nbt_spider@104.217.249.174:8888',
             'nbt_spider:nbt_spider@172.106.46.70:8888', 'nbt_spider:nbt_spider@172.106.240.147:8888',
             'nbt_spider:nbt_spider@45.35.226.204:8888', 'nbt_spider:nbt_spider@107.160.73.99:8888',
             'nbt_spider:nbt_spider@45.34.13.138:8888', 'nbt_spider:nbt_spider@45.35.234.237:8888',
             'nbt_spider:nbt_spider@104.217.249.164:8888', 'nbt_spider:nbt_spider@172.106.64.212:8888',
             'nbt_spider:nbt_spider@172.106.63.106:8888', 'nbt_spider:nbt_spider@172.107.13.162:8888',
             'nbt_spider:nbt_spider@104.217.249.171:8888', 'nbt_spider:nbt_spider@172.106.68.98:8888',
             'nbt_spider:nbt_spider@172.106.62.5:8888', 'nbt_spider:nbt_spider@172.106.63.104:8888',
             'nbt_spider:nbt_spider@172.106.62.14:8888', 'nbt_spider:nbt_spider@107.160.125.154:8888',
             'nbt_spider:nbt_spider@45.35.175.235:8888', 'nbt_spider:nbt_spider@107.160.125.151:8888',
             'nbt_spider:nbt_spider@45.35.234.234:8888', 'nbt_spider:nbt_spider@45.35.234.230:8888',
             'nbt_spider:nbt_spider@172.106.96.69:8888', 'nbt_spider:nbt_spider@172.106.46.77:8888',
             'nbt_spider:nbt_spider@172.106.240.157:8888', 'nbt_spider:nbt_spider@45.35.234.231:8888',
             'nbt_spider:nbt_spider@172.106.64.218:8888', 'nbt_spider:nbt_spider@45.35.236.201:8888',
             'nbt_spider:nbt_spider@172.106.64.222:8888', 'nbt_spider:nbt_spider@45.35.236.198:8888',
             'nbt_spider:nbt_spider@172.106.46.66:8888', 'nbt_spider:nbt_spider@45.35.175.228:8888',
             'nbt_spider:nbt_spider@45.35.226.206:8888', 'nbt_spider:nbt_spider@172.106.68.108:8888')

DIVIDE = 2
localproxy = '127.0.0.1:56823'


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
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Pragma': 'no-cache',
        'Referer': 'https://play.google.com/store',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }
    names = None

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 10,
        'last_modified': False,
        'etag': False,
    }

    url_list = ['https://play.google.com/store/apps/collection/topselling_free',
                'https://play.google.com/store/apps/category/GAME/collection/topselling_free']

    def get_taskid(self, task):
        return md5string(task['url'] + json.dumps(task['fetch'].get('data', '')))

    @every(minutes=24 * 60)
    def on_start(self):
        for i in self.url_list:
            new_header = deepcopy(self.default_headers)
            new_header['Referer'] = i
            self.crawl(i,
                       callback=self.get_list,
                       force_update=True,
                       save={'start': 60, 'headers': new_header},
                       etag=False,
                       last_modified=False,
                       proxy=localproxy,
                       validate_cert=False,
                       )

    def get_list(self, response):
        url = response.url + u'?authuser=0' if u'authuser' not in response.url else response.url

        if response.save.get('start') < 540:
            data = {
                'start': response.save.get('start'),
                'num': 60,
                'numChildren': 0,
                'cctcss': 'square-cover',
                'cllayout': 'NORMAL',
                'ipf': 1,
                'xhr': 1,
            }

            self.crawl(
                url,
                callback=self.get_list,
                method='POST',
                data=data,
                force_update=True,
                etag=False,
                last_modified=False,
                proxy=localproxy,
                validate_cert=False,
                headers=response.save.get('headers'),
                save={'start': response.save.get('start') + 60, 'headers': response.save.get('headers')}
            )

        return {
            'content': response.text
        }
