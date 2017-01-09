#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-01-09 11:34:52
# Project: ZY0060

from pyspider.libs.base_handler import *
import re
import time
import json

BEGIN = 16493298
DIVIDE = 10


class Handler(BaseHandler):
    retry_delay = {
        0: 0,
        1: 0,
        2: 2,
        3: 4,
        4: 8,
        5: 16
    }
    default_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh-TW;q=0.4',
        'Referer': 'http://seo.chinaz.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

    seo_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh-TW;q=0.4',
        'Referer': 'http://seo.chinaz.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

    icp_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh-TW;q=0.4',
        'Referer': 'http://icp.chinaz.com/searchs',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

    baidu_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'http://www.baidu.com/gaoji/advanced.html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 5,
        'last_modified': False,
        'etag': False,
    }

    START = 0
    DELTA = 5

    baidu_url = 'http://www.baidu.com/s?q1={}&q2=&q3=&q4=%E6%8B%9B%E8%81%98+%E5%A4%A7%E8%A1%97%E7%BD%91+%E8%81%8C%E5%8F%8B%E9%9B%86+%E7%99%BE%E7%A7%91+%E9%A2%86%E8%8B%B1&rn=50&lm=0&ct=0&ft=&q5=&q6=&tn=baiduadv'
    api_url = 'http://10.26.225.178:10265/api/common/RL_XM0001?start={}&end={}'

    def get_taskid(self, task):
        return md5string(task['url'] + json.dumps(task['fetch'].get('data', '')))

    def get_time(self):
        return str(int(time.time() * 1000))

    def on_start(self):
        self.crawl(
            self.api_url.format(BEGIN - DIVIDE, BEGIN),
            save={
                'cursor': BEGIN - DIVIDE
            },
            callback=self.get_list,
            force_update=True,
        )

    @config(priority=2)
    def get_list(self, response):
        names = response.text.split('\n')
        cursor = response.save['cursor']
        if cursor <= 0:
            return

        if len(names) > 1:
            self.crawl(self.api_url.format(max(cursor - DIVIDE, 0), cursor),
                       save={
                           'cursor': cursor - DIVIDE
                       },
                       callback=self.get_list,
                       )

        for name in names:
            self.crawl(
                self.baidu_url.format(name + u'+官网'),
                callback=self.get_baidu,
                headers=self.baidu_headers,
                # proxy='localhost:3128',
                save={
                    'request_url': self.baidu_url.format(name),
                    'name': name,
                }
            )

    @config(priority=4)
    @catch_status_code_error
    def get_baidu(self, response):
        request_url = response.save['request_url']
        if response.status_code >= 400 or (response.status_code == 200 and len(response.doc('#content_left')) == 0):
            if not ('很抱歉，没有找到' in response.text and response.save['name'] in response.text):
                self.crawl(request_url,
                           # proxy='localhost:3128',
                           callback=self.get_baidu,
                           force_update=True,
                           headers=self.baidu_headers,
                           save=response.save)
            return

        urls = [url.text() for url in response.doc('#content_left .f13 a.c-showurl').items()]

        for index, url in enumerate(urls):
            if '...' in url:
                if '/' in url:
                    urls[index] = re.sub('/(.*)', '', url)
                else:
                    urls.pop(index)

        url_string = '\r\n'.join(urls)

        data = {
            'urls': url_string,
            'btn_search': '查询',
        }

        self.crawl(
            'http://icp.chinaz.com/searchs',
            method='POST',
            data=data,
            callback=self.get_icp,
            headers=self.icp_headers,
            # proxy='localhost:3128',
            save=response.save,
        )

    @config(priority=6)
    def get_icp(self, response):

        for table in response.doc('.Tool-batchTable').items():
            for tr in table('tr').items():
                url = []
                name = ''
                name = tr('td:first').text()
                
                co_type=tr('td.tc:first').text()

                for a in tr('a').items():
                    if a.attr.href and 'http' in a.attr.href:
                        url.append(a.attr.href)

                for a in url:
                    self.crawl(
                        'http://seo.chinaz.com/',
                        params={
                            'q': a
                        },
                        save={
                            'name': name + ' ' + a,
                        },
                        # proxy='localhost:3128',
                        headers=self.seo_headers,
                        callback=self.get_seo
                    )

                    self.crawl(
                        a,
                        callback=self.official_web,
                        headers=self.default_headers,
                        save={
                            'name': name + ' ' + a,
                        }
                    )

    @config(priority=8)
    def get_seo(self, response):
        name = response.save['name']
        hostv = re.search('var hostv=\'([^\']*)\'', response.text).group(1)
        dekey = re.search('var dekey=\'([^\']*)\'', response.text).group(1)
        hostd = re.search('var hostd=\'([^\']*)\'', response.text).group(1)

        self.crawl(
            'http://outlink.chinaz.com/oc.ashx',
            params={
                'enkey': dekey,
                'h': hostv
            },
            save={
                'name': name
            },
            # proxy='localhost:3128',
            headers=self.seo_headers,
            cookies=response.cookies,
            callback=self.ajax_page
        )

        self.crawl(
            'http://other.tool.chinaz.com/gettime.ashx?action=gettime&enkey=' + dekey + '&host=' + hostd + '&callback=jQuery111306677427094990258_' + self.get_time() + '&_=' + self.get_time(),
            save={
                'name': name
            },
            # proxy='localhost:3128',
            cookies=response.cookies,
            headers=self.seo_headers,
            callback=self.ajax_page
        )

        return {
            "content": name + '\n' + response.text,
        }

    @config(priority=10)
    def ajax_page(self, response):
        name = response.save['name']
        return {
            "content": name + '\n' + response.text,
        }

    @config(priority=12)
    @catch_status_code_error
    def official_web(self, response):
        content = response.save['name'] + '\n' + response.text

        return {
            'content': content,
            'path': 'official_web/' + md5string(content),
        }
