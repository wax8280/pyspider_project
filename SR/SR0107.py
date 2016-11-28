# coding: utf-8
from pyspider.libs.base_handler import *
from random import choice

BEGIN = 0
DIVIDE = 10

the_proxy = (
    "nbt_spider:nbt_spider@23.91.11.91:8888",
    "nbt_spider:nbt_spider@216.99.157.151:8888",
    "nbt_spider:nbt_spider@198.13.96.92:8888",
    "nbt_spider:nbt_spider@198.13.96.82:8888",
    "nbt_spider:nbt_spider@198.13.110.91:8888",
    "nbt_spider:nbt_spider@216.99.146.202:8888",
    "nbt_spider:nbt_spider@192.210.60.227:8888",
    "nbt_spider:nbt_spider@192.210.60.228:8888",
    "nbt_spider:nbt_spider@45.34.106.179:8888",
    "nbt_spider:nbt_spider@192.210.61.43:8888",
    "nbt_spider:nbt_spider@192.210.60.238:8888",
    "nbt_spider:nbt_spider@108.171.254.12:8888",
    "nbt_spider:nbt_spider@198.13.96.84:8888",
    "nbt_spider:nbt_spider@198.13.107.199:8888",
    "nbt_spider:nbt_spider@216.99.157.149:8888",
    "nbt_spider:nbt_spider@108.171.252.139:8888",
    "nbt_spider:nbt_spider@192.210.55.76:8888",
    "nbt_spider:nbt_spider@104.217.5.43:8888",
    "nbt_spider:nbt_spider@216.99.146.205:8888",
    "nbt_spider:nbt_spider@216.99.157.154:8888",
    "nbt_spider:nbt_spider@192.210.55.72:8888",
    "nbt_spider:nbt_spider@216.99.157.150:8888",
    "nbt_spider:nbt_spider@192.210.61.45:8888",
    "nbt_spider:nbt_spider@23.91.8.109:8888",
    "nbt_spider:nbt_spider@23.91.11.123:8888",
    "nbt_spider:nbt_spider@23.91.8.107:8888",
    "nbt_spider:nbt_spider@104.217.5.41:8888",
    "nbt_spider:nbt_spider@45.34.86.61:8888",
    "nbt_spider:nbt_spider@23.91.11.87:8888",
    "nbt_spider:nbt_spider@192.210.60.230:8888",
    "nbt_spider:nbt_spider@216.99.157.147:8888",
    "nbt_spider:nbt_spider@192.210.55.70:8888",
    "nbt_spider:nbt_spider@45.34.113.40:8888",
    "nbt_spider:nbt_spider@23.91.8.104:8888",
    "nbt_spider:nbt_spider@108.171.252.142:8888",
    "nbt_spider:nbt_spider@192.210.61.41:8888",
    "nbt_spider:nbt_spider@198.13.110.84:8888",
    "nbt_spider:nbt_spider@198.13.96.85:8888",
    "nbt_spider:nbt_spider@198.13.110.89:8888",
    "nbt_spider:nbt_spider@216.99.157.155:8888",
    "nbt_spider:nbt_spider@23.91.11.92:8888",
    "nbt_spider:nbt_spider@198.13.107.202:8888",
    "nbt_spider:nbt_spider@198.13.107.200:8888",
    "nbt_spider:nbt_spider@192.210.55.77:8888",
    "nbt_spider:nbt_spider@192.210.61.39:8888",
    "nbt_spider:nbt_spider@23.91.11.117:8888",
    "nbt_spider:nbt_spider@192.210.60.229:8888",
    "nbt_spider:nbt_spider@23.91.11.89:8888",
    "nbt_spider:nbt_spider@104.217.5.42:8888",
    "nbt_spider:nbt_spider@198.13.110.87:8888",
)


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
        'Referer': 'https://play.google.com/store',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 10,

    }

    base_url = 'https://play.google.com/store/apps/details?id={}'

    # TODO
    api_url = 'http://112.74.93.18:10265/api/product/app/ids?app_type=android&start={}&end={}'

    # api_url = 'http://10.26.225.178:10265/api/product/app/ids?app_type=android&start={}&end={}'

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

            for each in product_list:
                self.crawl(self.base_url.format(each),
                           callback=self.get_content,
                           proxy=choice(the_proxy),
                           fetch_type='requests',
                           validate_cert=False,
                           headers=self.default_headers,
                           )

    def get_content(self, response):
        return {
            'content': response.text,
            'url': response.url
        }
