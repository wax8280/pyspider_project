# coding: utf-8

from pyspider.libs.base_handler import *
import re
from copy import deepcopy
from itertools import combinations
from pyquery import PyQuery as pq
import time
from urllib import urlencode

BEGIN = 0
DIVIDE = 20


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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'http://sbcx.saic.gov.cn:9080/tmois/wszhcx_getZhcx.xhtml',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',

    }

    tungee_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 10,
        'etag': False,
        'last_modified': False,
        'connect_timeout': 60,
        'timeout': 360
    }

    url = u'http://sbcx.saic.gov.cn:9080/tmois/wszhcx_pageZhcxMain.xhtml?type=cn&intcls=&{}&cnNameFlag=0&paiType=0'
    url_2 = u'http://sbcx.saic.gov.cn:9080/tmois/wszhcx_getLikeCondition.xhtml?{}&intCls=&paiType=0'

    # TODO
    api_url = u'http://112.74.93.18:10265/api/names?start={}&end={}'

    # 正式
    # api_url = u'http://10.26.229.2:10265/api/names?start={}&end={}'

    def on_start(self):
        self.crawl(self.api_url.format(BEGIN, BEGIN + DIVIDE),
                   save={
                       'end': BEGIN + DIVIDE
                   },
                   callback=self.list_page,
                   force_update=True,
                   headers=self.tungee_header
                   )

    @config(age=365 * 24 * 60 * 60)
    def list_page(self, response):
        names = response.text.split('\n')
        now = response.save['end']
        # if len(names) > 1:
        #     self.crawl(self.api_url.format(now, now + DIVIDE),
        #                save={
        #                    'end': now + DIVIDE
        #                },
        #                callback=self.list_page,
        #                headers=self.tungee_header
        #                )

        for name in names:
            if len(name.strip()):
                url_ = urlencode({'appCnName': u'腾讯'.encode('utf-8')}).replace('%', '%25')
                print url_
                self.crawl(self.url.format(url_),
                           callback=self.get_list,
                           # proxy='localhost:3128',
                           )

    @config(priority=2)
    def get_list(self, response):
        new_headers = deepcopy(self.default_headers)
        new_headers['Referer'] = response.url

        for i in response.doc('.import_hpb_list a').items():
            if i.attr.href:
                src = re.search("appCnName=(.*?)&", i.attr.href)
                if src:
                    _ = src.groups()[0]
                    url_ = self.url_2.format(urlencode({'appCnName': _.encode('utf-8')}).replace('%', '%25')).replace('%28','(').replace('%29',')')
                    self.crawl(
                        url_,
                        callback=self.get_content,
                        # proxy='localhost:3128',
                    )

    @config(priority=3)
    def get_content(self, response):
        return {
            'content': response.text,
            'url': response.url
        }
