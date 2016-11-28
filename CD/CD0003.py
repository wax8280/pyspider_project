# coding: utf-8
from pyspider.libs.base_handler import *
import re


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
        'Referer': 'http://www.163.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }
    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 10,
    }

    url = u'http://sports.163.com/'

    @every(minutes=24 * 60 / 5)
    def on_start(self):
        self.crawl(self.url, callback=self.get_list, fetch_type='js', force_update=True)

    @every(minutes=24 * 60 / 5)
    def on_start(self):
        self.crawl(self.url, callback=self.get_list, fetch_type='js', force_update=True)

    def get_list(self, response):
        """
        遍历网页中的广告
        """
        for each_iframe in response.doc('iframe').items():
            style = each_iframe.attr.style
            if style:
                continue
            else:
                self.crawl(each_iframe.attr.src,
                           callback=self.get_frame,
                           validate_cert=False,
                           save={'width': each_iframe.attr.width,
                                 'height': each_iframe.attr.height},
                           force_update=True,
                           fetch_type='js')

    def get_frame(self, response):
        """
        访问iframe，并提取真实的广告地址
        """

        if list(response.doc('a').items()):
            for each_iframe in response.doc('a').items():
                self.crawl(each_iframe.attr.href, callback=self.get_target_content, validate_cert=False,
                           save={'width': response.save.get('width'),
                                 'height': response.save.get('height')}, force_update=True)
        else:
            url = re.search(u'href="(.+?)"', response.text)
            if url:
                for each in url.groups():
                    # 过滤google
                    if u'googlesyndication' in each:
                        continue
                    self.crawl(each, callback=self.get_target_content, validate_cert=False,
                               save={'width': response.save.get('width'),
                                     'height': response.save.get('height')}, force_update=True)
            else:
                url = re.search(u'src="(.+?)"', response.text)
                if url:
                    for each in url.groups():

                        # 过滤google
                        if u'googlesyndication' in each:
                            continue
                        self.crawl(each, callback=self.get_target_content, validate_cert=False,
                                   save={'width': response.save.get('width'),
                                         'height': response.save.get('height')}, force_update=True)

    def get_target_content(self, response):
        return {'url': response.url,
                'contnet':
                    u'width:' + response.save.get('width') + u'\n' +
                    u'height:' + response.save.get('height') + u'\n' +
                    u'url:' + response.url
                }
