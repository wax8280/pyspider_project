#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pyspider.libs.base_handler import *
import re
from copy import deepcopy
import datetime

BEGIN = 0
DIVIDE = 1
N_PAGE = 3 - 1


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
        'Pragma': 'no-cache',
        'Referer': 'http://www.baidu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    tungee_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 10,
    }

    url = u'http://www.baidu.com/s?wd={key_word}'

    # TODO
    api_url = u'http://112.74.93.18:12580/api/names/short?start={}&end={}&time={}'

    @every(minutes=24 * 60)
    def on_start(self):
        now_date = unicode((datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
        self.crawl(self.api_url.format(BEGIN, BEGIN + DIVIDE, now_date),
                   save={
                       'end': BEGIN + DIVIDE,
                       'now_date': now_date
                   },
                   callback=self.list_page,
                   force_update=True,
                   headers=self.tungee_header,
                   itag=now_date
                   )

    def list_page(self, response):
        """
        获取公司列表
        """
        now = int(response.save['end'])
        result = response.json
        names = result['name']

        if len(names) > 0:
            self.crawl(
                self.api_url.format(now, now + DIVIDE, response.save.get('now_date')),
                save={
                    'end': now + DIVIDE,
                    'now_date': response.save.get('now_date')
                },
                callback=self.list_page,
                headers=self.tungee_header,
                validate_cert=False,
                itag=response.save.get('now_date')
            )

        # 开始搜索
        for name in names:
            if len(name.strip()):
                self.crawl(
                    # 替换空格为'+'
                    self.url.format(key_word=name.strip()).replace(u' ', u'+'),
                    callback=self.get_n_page,
                    save={
                        'first': True,
                        'company_name': name.strip(),
                        'now_date': response.save.get('now_date')
                        # 'type': 'normal'
                    },
                    validate_cert=False,
                    itag=response.save.get('now_date'),
                    proxy='localhost:3128',
                )

    @config(priority=2)
    def get_n_page(self, response):
        """
        获取前n页搜索结果
        """

        # 重新设置headers
        content_headers = deepcopy(self.default_headers)
        content_headers['Referer'] = response.url

        # 获取每一页的搜索结果
        for each in response.doc('.c-container').items():
            self.crawl(
                each('.t a').attr.href,
                callback=self.get_content,
                headers=content_headers,
                save={
                    'company_name': response.save['company_name'],
                    # 'type': response.save['type'],
                    'cookies': response.cookies,
                    'now_date': response.save.get('now_date')
                    # 'highlight': each('em').text()
                },
                cookies=response.cookies,
                validate_cert=False,
                itag=response.save.get('now_date'),
                proxy='localhost:3128',
            )

        # 获取下一页
        if response.save.get('first'):
            for each in list(response.doc('#page a').items())[:N_PAGE]:
                self.crawl(
                    each.attr.href,
                    callback=self.get_n_page,
                    save={
                        'first': False,
                        'company_name': response.save['company_name'],
                        'now_date': response.save.get('now_date')
                        # 'type': response.save['type']
                    },
                    validate_cert=False,
                    itag=response.save.get('now_date'),
                    proxy='localhost:3128',
                )

    @config(priority=3)
    def get_content(self, response):
        """
        获取详情页
        """

        search_result = re.search(u"<noscript>.*URL=\'(.+)\'.*</noscript>", response.text)
        # 对于有跳转的情况
        if search_result:
            redirected_url = search_result.groups()[0]

            content_headers = deepcopy(self.default_headers)
            content_headers['Referer'] = response.url

            # 重新callback
            self.crawl(
                redirected_url,
                callback=self.get_content,
                headers=content_headers,
                save={
                    'company_name': response.save['company_name'],
                    'now_date': response.save.get('now_date')
                    # 'type': response.save['type'],
                    # 'highlight': response.save['highlight']
                },
                cookies=response.save['cookies'],
                validate_cert=False,
                itag=response.save.get('now_date'),
                proxy='localhost:3128',
            )

        # 返回结果
        else:
            return {
                'content': response.save['company_name'] + u'\n' + response.text
            }
