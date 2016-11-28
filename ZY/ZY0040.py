#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-11-25 17:41:37
# Project: ZY0040

from pyspider.libs.base_handler import *
from copy import deepcopy

BEGIN = 0
DIVIDE = 10


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
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 3,

    }

    country = ["CN", "HW", "TW", "US", "JP", "KR", "UK", "RU", "MX", "FR", "BR", "VN", "SA", "IN", "ID", "TR", "EG"]

    base_url = 'https://itunes.apple.com/{}/developer/{}'

    # TODO
    #api_url = 'http://112.74.93.18:10265/api/product/app/developer/ids?dev_type=appStore&start={}&end={}'

    api_url = 'http://10.26.225.178:10265/api/product/app/developer/ids?dev_type=appStore&start={}&end={}'


    def on_start(self):
        self.crawl(self.api_url.format(BEGIN, BEGIN + DIVIDE),
                   callback=self.list_page,
                   force_update=True,
                   save={'begin': BEGIN + DIVIDE}
                   )

    @config(priority=2)
    def list_page(self, response):
        text = response.text.strip()
        product_list = text.split('\n')

        if product_list and u'' not in product_list:
            self.crawl(
                self.api_url.format(response.save.get('begin'), response.save.get('begin') + DIVIDE),
                callback=self.list_page,
                save={'begin': response.save.get('begin') + DIVIDE}
            )

            for each_country in self.country:
                for each in product_list:
                    self.crawl(self.base_url.format(each_country, each),
                               callback=self.get_dev_app,
                               # proxy='localhost:3128',
                               validate_cert=False,
                               headers=self.default_headers,
                               save={'urls': set()}
                               )

    @config(priority=3)
    def get_dev_app(self, response):
        """
        模拟翻页与遍历当前页面的所有app
        """

        new_header = deepcopy(self.default_headers)
        new_header['Referer'] = response.url

        # 遍历当前的所有app
        iphone_app_url = [a.attr.href for a in
                          response.doc('#content > div > div:nth-child(2) > div:nth-child(2) a.name').items() if
                          a.attr.href]

        ipad_app_url = [a.attr.href for a in
                        response.doc('#content > div > div.center-stack > div:nth-child(2) > div a.name').items() if
                        a.attr.href]
        # app翻页
        diff = set(i.attr.href for i in response.doc('.list.paginate a').items() if i.attr.href) - \
               eval(response.save.get('urls'))
        sum_ = set(i.attr.href for i in response.doc('.list.paginate a').items() if i.attr.href) | \
               eval(response.save.get('urls'))

        print diff
        print sum_
        if diff:
            for page_url in diff:
                self.crawl(page_url,
                           callback=self.get_dev_app,
                           headers=new_header,
                           # proxy='localhost:3128',
                           validate_cert=False,
                           save={'urls': sum_}
                           )

        iphone_app_url.extend(ipad_app_url)

        return {
            'content': iphone_app_url,
            'url': response.url
        }
