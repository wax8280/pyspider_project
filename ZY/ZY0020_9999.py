#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-11-22 14:30:11
# Project: ZY0020_999

from pyspider.libs.base_handler import *
from copy import deepcopy
import re

PW = '123456'
BEGIN = 1
DIVIDE = 1

user_list = ['emsln9es@163.com',
             'd2ffli8yd@163.com',
             'x9l4l96p0g4aas7@163.com',
             'ujvqdyqb01tx0y@163.com',
             'wst0cebr7n2@163.com']

MAX_USER = len(user_list)


class Handler(BaseHandler):
    default_headers = {
        'Accept': 'image/webp,image/*,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    login_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'http://www.baijingapp.com/login/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    get_headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': '',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    login_url = 'http://www.baijingapp.com/account/ajax/login_process/'

    login_data = 'return_url=&user_name={}&password={}&net_auto_login=1&_post_type=ajax'

    cont_url = 'http://www.baijingapp.com/people/ajax/get_tel/?company_id={}'
    referer_url = 'http://www.baijingapp.com/people/{}'

    url = 'http://www.baijingapp.com/company/page-{}'

    def on_start(self):

        self.crawl(
            self.url.format(BEGIN),
            callback=self.get_list,
            force_update=True,
            etag=False,
            last_modified=False,
            headers=self.default_headers,
            save={'is_login': False, 'now': BEGIN, 'user_count': 0}
        )

    @config(priority=2)
    def get_list(self, response):

        if response.save.get('is_login'):
            if response.save.get('use_time') < 90:

                if u'crr-if"' in response.text:

                    for i in response.doc('.list h2 a').items():
                        company_id = re.search(u'(\d*)$', i.attr.href).groups()[0]
                        self.crawl(
                            self.cont_url.format(company_id),
                            callback=self.get_content,
                            headers=self.default_headers,
                            # proxy='localhost:3128',
                            validate_cert=False,
                            cookies=response.save.get('cookies')
                        )

                    for i in range(1, DIVIDE + 1):
                        new_url = self.url.format(response.save.get('now') + i)
                        new_headers = deepcopy(self.default_headers)
                        new_headers['Referer'] = self.url.format(response.save.get('now') + i - 1)

                        # 翻页
                        self.crawl(
                            new_url,
                            callback=self.get_list,
                            headers=new_headers,
                            # proxy='localhost:3128',
                            save={'is_login': True, 'use_time': response.save.get('use_time') + 10,
                                  'user_name': response.save.get('user_name'),
                                  'now': response.save.get('now') + DIVIDE, 'cookies': response.save.get('cookies'),
                                  'user_count': response.save.get('user_count')},
                            validate_cert=False,
                        )
            else:
                user_name = user_list[response.save.get('user_count')]
                self.crawl(
                    self.login_url,
                    callback=self.login,
                    headers=self.login_headers,
                    method='POST',
                    data=self.login_data.format(user_name, PW),
                    save={'is_login': True, 'use_time': 0, 'user_name': user_name, 'last_url': response.url,
                          'now': response.save.get('now'), 'user_count': response.save.get('user_count') + 1}
                )

        else:
            user_name = user_list[response.save.get('user_count')]
            self.crawl(
                self.login_url,
                callback=self.login,
                headers=self.login_headers,
                method='POST',
                force_update=True,
                etag=False,
                last_modified=False,
                data=self.login_data.format(user_name, PW),
                save={'is_login': True, 'use_time': 0, 'user_name': user_name, 'last_url': response.url,
                      'now': response.save.get('now'), 'user_count': response.save.get('user_count') + 1}
            )

    @config(priority=2)
    def login(self, response):

        if u'first_login-TRUE' in response.text and u'"errno":"1"' in response.text:
            print u'登陆成功！'
            self.crawl(
                response.save.get('last_url'),
                callback=self.get_list,
                headers=self.default_headers,
                force_update=True,
                etag=False,
                last_modified=False,
                save={'is_login': response.save.get('is_login'), 'use_time': response.save.get('use_time'),
                      'user_name': response.save.get('user_name'), 'cookies': response.cookies,
                      'now': response.save.get('now'), 'user_count': response.save.get('user_count')}
            )

    @config(priority=4)
    def get_content(self, respnose):
        return {
            'content': respnose.text,
            'url': respnose.url
        }
