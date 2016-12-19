# !/usr/bin/env python
# coding: utf-8
from pyspider.libs.base_handler import *
import re
import time
import json

BEGIN = 0
DIVIDE = 1 * 100


class Handler(BaseHandler):
    retry_delay = {
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

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 5,
        'last_modified': False,
        'etag': False,
    }

    START = 0
    DELTA = 5

    api_url = 'http://120.77.12.100:10265/api/host/zhanzhanggongju/batch?start={}&end={}'

    def get_taskid(self, task):
        return md5string(task['url'] + json.dumps(task['fetch'].get('data', '')))

    def get_time(self):
        return str(int(time.time() * 1000))

    def on_start(self):
        self.crawl(
            self.api_url.format(BEGIN, BEGIN + DIVIDE),
            save={
                'end': BEGIN + DIVIDE
            },
            callback=self.get_list,
            force_update=True
        )

    @config(priority=2)
    def get_list(self, response):
        urls = response.text.split('\n')
        now = response.save['end']
        if len(urls) > 1:
            self.crawl(self.api_url.format(now, now + DIVIDE),
                       save={
                           'end': now + DIVIDE
                       },
                       callback=self.get_list,
                       )

        for i in range(0, DIVIDE, 100):
            try:
                _ = urls[i:i + 100]
            except:
                _ = urls[i:]
            url = '\r\n'.join(_)

            data = {
                'urls': url,
                'btn_search': '查询',
            }

            self.crawl(
                'http://icp.chinaz.com/searchs',
                method='POST',
                data=data,
                callback=self.get_icp,
                headers=self.icp_headers,
                proxy='localhost:3128',
                save={
                }
            )

    @config(priority=2)
    def get_icp(self, response):
        for table in response.doc('.Tool-batchTable').items():
            for tr in table('tr').items():
                url = []
                name = ''
                name = tr('td:first').text()

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
                        proxy='localhost:3128',
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

    @config(priority=3)
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
            proxy='localhost:3128',
            headers=self.seo_headers,
            cookies=response.cookies,
            callback=self.ajax_page
        )

        self.crawl(
            'http://other.tool.chinaz.com/gettime.ashx?action=gettime&enkey=' + dekey + '&host=' + hostd + '&callback=jQuery111306677427094990258_' + self.get_time() + '&_=' + self.get_time(),
            save={
                'name': name
            },
            proxy='localhost:3128',
            cookies=response.cookies,
            headers=self.seo_headers,
            callback=self.ajax_page
        )

        return {
            "content": name + '\n' + response.text,
        }

    @config(priority=3)
    def ajax_page(self, response):
        name = response.save['name']
        return {
            "content": name + '\n' + response.text,
        }

    @config(priority=3)
    @catch_status_code_error
    def official_web(self, response):
        content = response.save['name'] + '\n' + response.text

        return {
            'content': content,
            'path': 'official_web/' + md5string(content),
        }
