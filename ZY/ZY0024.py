# coding: utf-8

from pyspider.libs.base_handler import *
from copy import deepcopy
import HTMLParser
import re

html_parser = HTMLParser.HTMLParser()

DIVIDE = 2
BEGIN = 1
SHOULD_TRY_TIME = 10


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
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 10,
    }

    url_list = [
        'http://weixin.sogou.com/weixin?type=1&query=%E6%B5%B7%E5%A4%96%E6%B8%B8%E6%88%8F%E5%B0%8F%E7%8B%90%E7%8B%B8']

    @every(minutes=24 * 60)
    def on_start(self):
        for each in self.url_list:
            self.crawl(each,
                       callback=self.get_gzh,
                       force_update=True,
                       # etag=False,
                       # last_modified=False,
                       headers=self.default_headers,
                       proxy='localhost:3128',
                       )

    @config(priority=2)
    def get_gzh(self, response):
        new_headers = deepcopy(self.default_headers)
        new_headers['Referer'] = response.url

        if len(list(response.doc('._item').items())) > 0:
            for i in response.doc('._item').items():
                if i.attr.target == u'_blank':
                    self.crawl(
                        i.attr.href,
                        callback=self.get_list,
                        headers=new_headers,
                        proxy='localhost:3128',
                    )
        else:
            self.crawl(response.url,
                       callback=self.get_gzh,
                       force_update=True,
                       etag=False,
                       last_modified=False,
                       headers=self.default_headers,
                       proxy='localhost:3128',
                       )

    @config(priority=3)
    def get_list(self, response):
        some_text = html_parser.unescape(re.search(u"msgList = '(.*?)]}';", response.text).groups()[0])
        url = re.findall(u'"content_url":"(.*?)"', some_text)
        new_headers = deepcopy(self.default_headers)
        new_headers['Referer'] = response.url

        for i in url:
            the_url = u'http://mp.weixin.qq.com' + html_parser.unescape(i).replace(u'\\\\', u'')
            self.crawl(
                the_url,
                callback=self.get_content,
                headers=new_headers,
                proxy='localhost:3128',
            )

    @config(priority=4)
    def get_content(self, response):
        return {
            'content': response.text,
            'url': response.url
        }
