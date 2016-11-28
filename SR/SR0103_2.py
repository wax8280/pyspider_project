# coding: utf-8

from pyspider.libs.base_handler import *

BEGIN = 0
DIVIDE = 10


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
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Accept': 'text / html, application / xhtml + xml, application / xml;q = 0.9, image / webp, * / *;q = 0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN, zh;q = 0.8',
        'Referer': 'http://www.beianbeian.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',

    }

    tungee_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 10,
        'etag': False,
        'last_modified': False,
    }

    url = u'http://www.beianbeian.com/s?keytype=1&q={}'

    base_key_word = u'粤ICP备14{}号'

    def on_start(self):
        self.crawl(self.url.format(self.base_key_word.format(unicode(BEGIN).zfill(6))),
                   save={
                       'now': BEGIN, 'failed': 0
                   },
                   callback=self.list_page,
                   force_update=True,
                   # proxy='localhost:3128',
                   headers=self.default_headers
                   )

    @config(age=365 * 24 * 60 * 60)
    def list_page(self, response):
        failed = response.save.get('failed') + 1 if u'没有符合条件的记录' in response.text else 0

        if response.save.get('failed') <= 1000:
            for i in range(response.save.get('now'), response.save.get('now') + DIVIDE):
                self.crawl(self.url.format(self.base_key_word.format(unicode(response.save.get('now') + i).zfill(6))),
                           callback=self.list_page,
                           # proxy='localhost:3128',
                           headers=self.default_headers,
                           save={
                               'now': response.save.get('now') + DIVIDE,
                               'failed': failed,
                           }
                           )

            return {
                'content': response.text,
                'url': response.url
            }
