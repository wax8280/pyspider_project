from pyspider.libs.base_handler import *

class Handler(BaseHandler):
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

    start_url = 'http://www.qichacha.com/firm_9cce0780ab7644008b73bc2120479d31.shtml'

    def on_start(self):
        self.crawl(self.start_url,
                   callback=self.list_page,
                   force_update=True,
                   headers=self.default_headers,
                   proxy='localhost:3128',
                   )

    @config(priority=2)
    def list_page(self, response):
        for a in response.doc('ul .list-group.no-bg.auto .list-group-item').items():
            if u'firm_' in a.attr.href:
                self.crawl(
                    a.attr.href,
                    headers=self.default_headers,
                    callback=self.list_page,
                    proxy='localhost:3128',
                )

        return {
            'content': response.content,
            'url': response.url,
        }