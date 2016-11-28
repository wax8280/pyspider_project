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
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 10,

    }

    country = ["CN", "HW", "TW", "US", "JP", "KR", "UK", "RU", "MX", "FR", "BR", "VN", "SA", "IN", "ID", "TR", "EG"]

    base_url = 'https://itunes.apple.com/{}/app/id{}'

    # TODO
    # api_url = 'http://112.74.93.18:10265/api/product/app/ids?app_type=ios&start={}&end={}'
    #
    api_url = 'http://10.26.229.2:10265/api/product/app/ids?app_type=ios&start={}&end={}'

    def on_start(self):
        self.crawl(self.api_url.format(BEGIN, BEGIN + DIVIDE),
                   callback=self.list_page,
                   force_update=True,
                   save={'begin': BEGIN + DIVIDE}
                   )

    @config(priority=2)
    def list_page(self, response):
        text = response.text.strip()

        product_list = text.split('\n')

        if product_list and u'' not in product_list:
            self.crawl(
                self.api_url.format(response.save.get('begin'), response.save.get('begin') + DIVIDE),
                callback=self.list_page,
                save={'begin': response.save.get('begin') + DIVIDE}
            )

            for each_country in self.country:
                for each in product_list:
                    self.crawl(self.base_url.format(each_country, each),
                               callback=self.get_content,
                               proxy='localhost:3128',
                               validate_cert=False,
                               headers=self.default_headers,
                               )
    @config(priority=3)
    def get_content(self, response):
        return {
            'content': response.text,
            'url': response.url
        }
