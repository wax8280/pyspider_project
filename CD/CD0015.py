# !/usr/bin/env python
# coding: utf-8
from pyspider.libs.base_handler import *


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
        'Pragma': 'no-cache',
        'Referer': 'http://www.onlylady.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }
    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 3,
        'etag': False,
        'last_modified': False,
    }

    start_url = "http://www.onlylady.com/"
    url_dict = {0: "http://trends.onlylady.com/",
                1: "http://beauty.onlylady.com/", }

    @every(minutes=24 * 60 / 10)
    def on_start(self):
        self.crawl(
            self.start_url,
            callback=self.get_head_ads_content,
            fetch_type='js',
            force_update=True
        )

    def get_head_ads_content(self, response):
        a1 = [_.attr.href for _ in response.doc('.w1180.ad a').items()]
        a2 = [_.attr.href for _ in response.doc('.todayArea .partB.fRight.ad a').items()]
        a3 = [_.attr.href for _ in response.doc('.ad.ad_320x100 a').items()]

        print a1
        print a2
        print a3

        a1.extend(a2)
        a1.extend(a3)

        for k, v in self.url_dict.items():
            self.crawl(
                v,
                callback=self.get_sub_ads_content,
                fetch_type='js',
                force_update=True,
                save={'type': k}
            )

        return {
            'content': str(a1),
            'url': response.url
        }

    def get_sub_ads_content(self, response):
        if response.save.get('type') == 0:
            a1 = [_.html() for _ in response.doc('.ad_1000x100.f_ad_clearance noscript').items()]
            a2 = [_.html() for _ in response.doc('.ad_300x440 noscript').items()]

            print a1
            print a2

            a1.extend(a2)

        elif response.save.get('type') == 1:
            a1 = [_.attr.href for _ in response.doc('.ad_1000x100.f_ad_clearance a').items()]
            if not a1:
                a1 = [_.attr.href for _ in list(response.doc('.wrap a').items())[:1]]
            a2 = [_.attr.href for _ in response.doc('.ad_300x440 a').items()]

            print a1
            print a2

            a1.extend(a2)

        return {
            'content': str(a1),
            'url': response.url
        }
