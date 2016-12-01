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
        'Referer': 'http://www.xinhuanet.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }
    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 3,
        'etag': False,
        'last_modified': False,
    }

    start_url = "http://www.yoka.com/"
    url_dict = {0: "http://www.yoka.com/fashion/",
                1: "http://www.yoka.com/luxury/",
                2: "http://www.yoka.com/star/",
                3: "http://www.yoka.com/beauty/"}

    @every(minutes=24 * 60 / 10)
    def on_start(self):
        self.crawl(
            self.start_url,
            callback=self.get_head_ads_content,
            fetch_type='js',
            force_update=True
        )

    def get_head_ads_content(self, response):
        a1 = [_.attr.href for _ in response.doc('.ad_360_250 a').items()]
        a2 = [_.attr.href for _ in response.doc('.g-focus.ad_switch a').items()]
        a3 = [_.attr.href for _ in response.doc('#list-focus2 a').items() if _.attr.target == u'_blank']

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
            a1 = [_.attr.href for _ in response.doc('.ad_first a').items()]
            a2 = [_.attr.href for _ in response.doc('body > .clearfix > div > div > a').items()]

            print a1
            print a2

            a1.extend(a2)

        elif response.save.get('type') == 1:
            a1 = [i.attr.href for _ in response.doc('div').items() if
                  _.attr.style == u'width:1160px;height:110px;border:none;padding:0px;margin:0px;overflow:hidden;position:relative;'
                  for i in _('a').items()]
            a2 = [_.attr.href for _ in response.doc('.adsame-banner-box a').items()]

            print a1
            print a2

            a1.extend(a2)

        elif response.save.get('type') == 2:
            a1 = [_.attr.href for _ in response.doc('.ad_first_r a').items()]
            a2 = [_.attr.href for _ in response.doc('.g-ads-three clearfix a').items()]
            a3 = [_.attr.href for _ in response.doc('body > div.g-box.clearfix > div:nth-child(6) > div > a').items()]

            print a1
            print a2
            print a3

            a1.extend(a2)
            a1.extend(a3)

        elif response.save.get('type') == 3:
            a1 = [_.attr.href for _ in response.doc('.list-focus a').items() if _.attr.target == u'_blank']
            a2 = [_.attr.href for _ in response.doc(
                'body > div.g-box.clearfix > div.g-content.clearfix.m-first > div > div.g-side.fright a').items()]
            a3 = [_.attr.href for _ in response.doc('.g-content.clearfix.m-2 .g-focus.pics_focus_skin a').items() if
                  _.attr.target == u'_blank']

            print a1
            print a2
            print a3

            a1.extend(a2)
            a1.extend(a3)

        return {
            'content': str(a1),
            'url': response.url
        }
