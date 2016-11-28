from pyspider.libs.base_handler import *
import datetime

BEGIN = 0
MAX = 41


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
        'Referer': 'https://itunes.apple.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 10,
        'last_modified': False,
        'etag': False,
    }

    url_list = 'http://tungee-static.oss-cn-shenzhen.aliyuncs.com/spider/ZY0037/url_{}.txt'

    @every(minutes=24 * 60)
    def on_start(self):
        now_date = unicode((datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
        self.crawl(self.url_list.format(BEGIN),
                   callback=self.list_page,
                   force_update=True,
                   etag=False,
                   last_modified=False,
                   itag=now_date,
                   save={'now': BEGIN, 'now_date': now_date})

    @config(priority=2)
    def list_page(self, response):
        urls = response.text.strip().split('\n')

        for each in urls:
            self.crawl(each.strip(),
                       callback=self.get_content,
                       # proxy=localproxy,
                       validate_cert=False,
                       force_update=True,
                       itag=response.save.get('now_date'),
                       headers=self.default_headers,
                           )

        if int(response.save.get('now')) < MAX:
            self.crawl(self.url_list.format(response.save.get('now') + 1),
                       callback=self.list_page,
                       itag=response.save.get('now_date'),
                       force_update=True,
                       etag=False,
                       last_modified=False,
                       save={'now': response.save.get('now') + 1, 'now_date': response.save.get('now_date')})

    @config(priority=3)
    def get_content(self, response):
        return {
            'content': response.text,
            'url': response.url
        }
