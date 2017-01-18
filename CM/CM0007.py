# !/usr/bin/env python
# coding: utf-8
from pyspider.libs.base_handler import *
import re
import time
import json

DIVIDE = 100
BEGIN = 0


def cdtp(source_url):
    result_url = 'http://www.{}.{}'
    chinese_pattern = u'www\.(.+)\.(.+)'
    gen = re.search(chinese_pattern, source_url)
    if gen:
        _ = []
        for i in gen.groups():
            if re.search(u'[\u4e00-\u9fa5]', i):
                _.append(u'xn--' + i.encode('punycode'))
            else:
                _.append(i)

        return result_url.format(_[0], _[1])


class Handler(BaseHandler):
    retry_delay = {
        0: 0,
        1: 0,
        2: 2,
        3: 4,
        4: 8,
        5: 16
    }

    seo_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh-TW;q=0.4',
        'Referer': 'http://seo.chinaz.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

    crawl_config = {
        'itag': 'v2',
        'retries': 5,
    }

    api_url = 'http://10.26.225.178:10265/api/common/CM0007?start={}&end={}'

    def get_taskid(self, task):
        return md5string(task['url'] + json.dumps(task['fetch'].get('data', '')))

    def get_time(self):
        return str(int(time.time() * 1000))

    def on_start(self):
        self.crawl(
            'http://10.26.225.178:10265/api/common/CM0007?start={}&end={}'.format(BEGIN, DIVIDE),
            callback=self.get_list,
            force_update=True,
            save={'cursor': BEGIN + DIVIDE}
        )

    @config(priority=2)
    def get_list(self, response):
        ll = response.text.split('\n')

        # ---------------------------------
        l = [i.split(',') for i in ll]
        # 以前的
        if len(l) > len(ll):
            return
        # -------------------------------

        print ll
        print len(ll)
        print len(l)
        if len(ll) < DIVIDE:
            time.sleep(5)
            self.crawl(
                self.api_url.format(response.save['cursor'] - DIVIDE, response.save['cursor']),
                callback=self.get_list,
                save={'cursor': response.save['cursor']}
            )
            return

        else:
            self.crawl(
                self.api_url.format(response.save['cursor'], response.save['cursor'] + DIVIDE),
                callback=self.get_list,
                save={'cursor': response.save['cursor'] + DIVIDE}
            )

        for url in ll:
            # url 中有中文
            if re.search(u'[\u4e00-\u9fa5]', url):
                url = cdtp(url)

            self.crawl(
                'http://seo.chinaz.com/',
                params={
                    'q': url
                },
                save={
                    'name': i[0],
                    'url': url
                },
                proxy='localhost:3128',
                headers=self.seo_headers,
                callback=self.get_seo
            )

    @config(priority=4)
    def get_seo(self, response):
        name = response.save['name']
        url = response.save['url']
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
                'name': name,
                'url': url
            },
            proxy='localhost:3128',
            headers=self.seo_headers,
            cookies=response.cookies,
            callback=self.ajax_page
        )

        self.crawl(
            'http://other.tool.chinaz.com/gettime.ashx?action=gettime&enkey=' + dekey + '&host=' + hostd + '&callback=jQuery111306677427094990258_' + self.get_time() + '&_=' + self.get_time(),
            save={
                'name': name,
                'url': url
            },
            proxy='localhost:3128',
            cookies=response.cookies,
            headers=self.seo_headers,
            callback=self.ajax_page
        )

        self.crawl(
            'http://seo.chinaz.com/ajaxseo.aspx?t=alexa&enkey={}&host={}&callback=jQuery111305605408249994359_{}&_={}'.format(
                dekey, hostd, self.get_time(), self.get_time()),
            save={
                'name': name,
                'url': url
            },
            proxy='localhost:3128',
            cookies=response.cookies,
            headers=self.seo_headers,
            callback=self.ajax_page,
        )

        return {
            "content": name + ' ' + url + '\n' + response.text,
        }

    @config(priority=10)
    def ajax_page(self, response):
        name = response.save['name']
        url = response.save['url']
        return {
            "content": name + ' ' + url + '\n' + response.text,
        }
