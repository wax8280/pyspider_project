#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-11-25 19:14:29
# Project: ZY0039

from pyspider.libs.base_handler import *
import re
from copy import deepcopy
from random import choice
import json

BEGIN = 0
DIVIDE = 20

the_proxy = (
    "nbt_spider:nbt_spider@23.91.11.91:8888",
    "nbt_spider:nbt_spider@216.99.157.151:8888",
    "nbt_spider:nbt_spider@198.13.96.92:8888",
    "nbt_spider:nbt_spider@198.13.96.82:8888",
    "nbt_spider:nbt_spider@198.13.110.91:8888",
    "nbt_spider:nbt_spider@216.99.146.202:8888",
    "nbt_spider:nbt_spider@192.210.60.227:8888",
    "nbt_spider:nbt_spider@192.210.60.228:8888",
    "nbt_spider:nbt_spider@45.34.106.179:8888",
    "nbt_spider:nbt_spider@192.210.61.43:8888",
    "nbt_spider:nbt_spider@192.210.60.238:8888",
    "nbt_spider:nbt_spider@108.171.254.12:8888",
    "nbt_spider:nbt_spider@198.13.96.84:8888",
    "nbt_spider:nbt_spider@198.13.107.199:8888",
    "nbt_spider:nbt_spider@216.99.157.149:8888",
    "nbt_spider:nbt_spider@108.171.252.139:8888",
    "nbt_spider:nbt_spider@192.210.55.76:8888",
    "nbt_spider:nbt_spider@104.217.5.43:8888",
    "nbt_spider:nbt_spider@216.99.146.205:8888",
    "nbt_spider:nbt_spider@216.99.157.154:8888",
    "nbt_spider:nbt_spider@192.210.55.72:8888",
    "nbt_spider:nbt_spider@216.99.157.150:8888",
    "nbt_spider:nbt_spider@192.210.61.45:8888",
    "nbt_spider:nbt_spider@23.91.8.109:8888",
    "nbt_spider:nbt_spider@23.91.11.123:8888",
    "nbt_spider:nbt_spider@23.91.8.107:8888",
    "nbt_spider:nbt_spider@104.217.5.41:8888",
    "nbt_spider:nbt_spider@45.34.86.61:8888",
    "nbt_spider:nbt_spider@23.91.11.87:8888",
    "nbt_spider:nbt_spider@192.210.60.230:8888",
    "nbt_spider:nbt_spider@216.99.157.147:8888",
    "nbt_spider:nbt_spider@192.210.55.70:8888",
    "nbt_spider:nbt_spider@45.34.113.40:8888",
    "nbt_spider:nbt_spider@23.91.8.104:8888",
    "nbt_spider:nbt_spider@108.171.252.142:8888",
    "nbt_spider:nbt_spider@192.210.61.41:8888",
    "nbt_spider:nbt_spider@198.13.110.84:8888",
    "nbt_spider:nbt_spider@198.13.96.85:8888",
    "nbt_spider:nbt_spider@198.13.110.89:8888",
    "nbt_spider:nbt_spider@216.99.157.155:8888",
    "nbt_spider:nbt_spider@23.91.11.92:8888",
    "nbt_spider:nbt_spider@198.13.107.202:8888",
    "nbt_spider:nbt_spider@198.13.107.200:8888",
    "nbt_spider:nbt_spider@192.210.55.77:8888",
    "nbt_spider:nbt_spider@192.210.61.39:8888",
    "nbt_spider:nbt_spider@23.91.11.117:8888",
    "nbt_spider:nbt_spider@192.210.60.229:8888",
    "nbt_spider:nbt_spider@23.91.11.89:8888",
    "nbt_spider:nbt_spider@104.217.5.42:8888",
    "nbt_spider:nbt_spider@198.13.110.87:8888",
)

DIVIDE = 20


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
        'Referer': 'https://play.google.com/store',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }
    names = None

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 3,
    }

    api_url = 'http://112.74.93.18:10265/api/product/app/developer/ids?dev_type=googlePlay&start={}&end={}'

    # api_url = 'http://10.26.225.178:10265/api/product/app/developer/ids?dev_type=googlePlay&start={}&end={}'

    dev_url = u"https://play.google.com/store/apps/dev?id={}"

    developer_url = u'https://play.google.com/store/apps/developer?id={}'

    dev_post_url = u'https://play.google.com/store/xhr/searchcontent?authuser=0'

    developer_post = {'start': '0',
                      'num': '24',
                      'numChildren': '0',
                      'cctcss': 'square-cover',
                      'cllayout': 'NORMAL',
                      'ipf': '1',
                      'xhr': '1',
                      }

    dev_post = {
        'pageNum': 1,
        'sp': '',
        'pagTok': '',
        'xhr': 1,
    }

    def get_taskid(self, task):
        return md5string(task['url'] + json.dumps(task['fetch'].get('data', '')))

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

        for each in product_list:
            url = self.dev_url.format(each) if each.isdigit() else self.developer_url.format(each)
            self.crawl(url,
                       callback=self.get_comapny,
                       proxy=choice(the_proxy),
                       fetch_type='requests',
                       validate_cert=False,
                       headers=self.default_headers,
                       save={'had_meet': '', 'first': True, 'id': each}
                       )

    @config(priority=4)
    def get_comapny(self, response):
        """
        从js代码中寻找出要post的数据，然后模拟翻页与遍历当前页面的所有app
        """

        # developer get next page
        # or developer(authuser) get next page
        if u'developer?id' in response.url:
            url = response.url if u'&authuser=0' in response.url else response.url + u'&authuser=0'

            # find pagTok in js codes
            nbp = re.findall(u"var nbp='(.+?)'", response.text)
            if nbp:
                got = None
                print nbp
                print nbp[-1].replace(u'[', u'').replace(u']', u'').split(u',')
                for _ in nbp:
                    nbp_list = _.replace(u'[', u'').replace(u']', u'').split(u',')
                    for each in nbp_list:
                        if each.startswith(u'\\x22') and each.endswith(u'\\x22') and u'S' in each:
                            got = each
                            break

                if got:
                    pagTok = got.replace(u'\\x22', u'').decode("unicode-escape")
                    if pagTok:
                        post_data = deepcopy(self.developer_post)
                        post_data.update({'pagTok': pagTok})
                        print post_data

                        # get last href,in order to prevent repeat
                        for a in list(response.doc('a').items())[:-1]:
                            if a.attr.class_ == u'title':
                                last = a.attr.href
                                break

                        new_header = deepcopy(self.default_headers)
                        new_header['Referer'] = response.url

                        pageNum = response.save.get('pageNum') if response.save.get('pageNum') else 0
                        print last
                        # if this page as same as last page,means that is end


                        if last not in response.save.get('had_meet'):
                            had_meet = response.save.get('had_meet') + last
                            self.crawl(
                                url,
                                callback=self.get_comapny,
                                method='POST',
                                data=post_data,
                                headers=new_header,
                                proxy=choice(the_proxy),
                                fetch_type='requests',
                                # proxy=localproxy,
                                validate_cert=False,
                                force_update=True,
                                save={'had_meet': had_meet, 'first': False, 'pageNum': pageNum + 1}
                            )

        # dev get next page
        # or self.dev_post_url get next page
        elif u'dev?id=' in response.url or response.url == self.dev_post_url:
            # if so,not the first time
            if response.save.get('sp'):

                pagTok = re.search(u',"([\w\:]*?)"', response.text)

                if pagTok:
                    pagTok = pagTok.groups()[0]

                    post_data = deepcopy(self.dev_post)
                    post_data['sp'] = response.save.get('sp')
                    post_data['pageNum'] = response.save.get('pageNum') + 1
                    post_data['pagTok'] = pagTok

                    new_header = deepcopy(self.default_headers)
                    new_header['Referer'] = response.save.get('refer_url')

                    self.crawl(
                        self.dev_post_url,
                        callback=self.get_comapny,
                        method='POST',
                        data=post_data,
                        proxy=choice(the_proxy),
                        fetch_type='requests',
                        validate_cert=False,
                        force_update=True,
                        save={
                            'first': False,
                            'sp': response.save.get('sp'),
                            'refer_url': response.save.get('refer_url'),
                            'pageNum': post_data['pageNum']}
                    )

            # first time
            else:
                sp = re.search(u'data-load-more-suggest-params="(.*?)"', response.text)
                pagTok = re.search(u'data-load-more-first-continuation-token="(.*?)"', response.text)

                if sp and pagTok:
                    sp = sp.groups()[0]
                    pagTok = pagTok.groups()[0]

                    post_data = deepcopy(self.dev_post)
                    post_data['sp'], post_data['pagTok'] = sp, pagTok

                    new_header = deepcopy(self.default_headers)
                    new_header['Referer'] = response.url

                    self.crawl(
                        self.dev_post_url,
                        callback=self.get_comapny,
                        method='POST',
                        data=post_data,
                        headers=new_header,
                        proxy=choice(the_proxy),
                        fetch_type='requests',
                        # proxy=localproxy,
                        validate_cert=False,
                        force_update=True,
                        save={
                            'first': False,
                            'sp': sp,
                            'refer_url': response.url,
                            'pageNum': post_data['pageNum']
                        }
                    )

        if u'dev?id=' in response.url:
            return {
                'content': response.text,
                'url': response.url
            }

        elif u'developer?id=' in response.url:
            if response.save.get('pageNum'):
                return {
                    'content': response.text,
                    'url': response.url + 'pageNum=' + str(response.save.get('pageNum'))
                }
            else:
                return {
                    'content': response.text,
                    'url': response.url
                }


        elif response.url == self.dev_post_url:
            if response.save.get('pageNum'):
                return {
                    'content': response.text,
                    'url': response.save.get('refer_url') + 'pageNum=' + str(response.save.get('pageNum'))
                }
            else:
                return {
                    'content': response.text,
                    'url': response.url
                }
