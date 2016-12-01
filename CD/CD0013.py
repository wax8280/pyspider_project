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
        'Referer': 'http://www.people.com.cn/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }
    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 3,
        'etag': False,
        'last_modified': False,
    }

    start_url = "http://www.people.com.cn/"
    url_dict = {0: "http://news.people.com.cn/",
                1: "http://politics.people.com.cn/",
                2: "http://finance.people.com.cn/",
                }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl(
            self.start_url,
            callback=self.get_head_ads_content,
            fetch_type='js',
            force_update=True
        )

    def get_head_ads_content(self, response):
        a1 = [_.attr.href for _ in response.doc('.banner a').items()]
        a2 = [_.attr.href for _ in response.doc('.w1000.zh_banner.clearfix a').items()]
        a3 = [_.attr.href for _ in response.doc('.ad_left.clearfix a').items()]
        a4 = [_.attr.onclick for _ in response.doc('div').items() if _.attr.onclick]



        print a1
        print a2
        print a3
        print a4

        a1.extend(a2)
        a1.extend(a3)
        a1.extend(a4)


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
            a1 = [_.attr.src for _ in response.doc('.ad_m.fl.ml5 iframe').items()]
            a2 = [_.attr.src for _ in response.doc('.box.mt10.ad_img iframe').items()]

            print a1
            print a2

            a1.extend(a2)

        elif response.save.get('type') == 1:
            a1 = [_.attr.src for _ in response.doc('.ad01.clear.w1000 iframe').items()]

            print a1


        elif response.save.get('type') == 2:
            a1 = [_.attr.href for _ in response.doc('.ad01 a').items()]
            a2 = [_.attr.href for _ in response.doc('.w980.pt20.clear a').items()]

            print a1
            print a2

            a1.extend(a2)

        return {
            'content': str(a1),
            'url': response.url
        }
