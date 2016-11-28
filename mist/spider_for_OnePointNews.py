# coding: utf-8

from pyspider.libs.base_handler import *
import re

DIVIDE = 9
BEGIN = 0


class Handler(BaseHandler):
    retry_delay = {
        1: 1,
        2: 5,
        3: 10,
        4: 30,
        5: 60
    }

    default_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'www.yidianzixun.com',
        # 'Referer': 'http://www.yidianzixun.com/home?page=channel&keyword=%E5%85%AC%E5%8F%B8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 5,
        # 'proxy': 'localhost:3128',
    }

    base_url = 'http://www.yidianzixun.com/api/q/?path=channel|news-list-for-keyword&display=%E5%85%AC%E5%8F%B8&word_type=token&fields=docid&fields=category&fields=date&fields=image&fields=image_urls&fields=like&fields=source&fields=title&fields=url&fields=comment_count&fields=summary&fields=up&cstart={}&cend={}&version=999999&infinite=true'
    detail_url = 'http://www.yidianzixun.com/home?page=article&id={}'

    @every(minutes=24 * 60 * 60)
    def on_start(self):
        self.crawl(self.base_url.format(BEGIN, BEGIN + DIVIDE), callback=self.get_summary,
                   force_update=True)

    @config(priority=2, age=12 * 60 * 60)
    def get_summary(self, response):
        result = response.json

        # get where is now by url
        now = int(re.search(r'cstart=(\d+)&cend=(\d+)', response.url).groups()[0])
        now += DIVIDE

        if len(result['result']) != 0:
            self.crawl(self.base_url.format(now, now + DIVIDE), callback=self.get_summary, force_update=True)

        for each in result['result']:
            if each["ctype"] == u'news':
                self.crawl(self.detail_url.format(each.get('itemid')), callback=self.get_content)

    @config(priority=3)
    def get_content(self, response):

        return {
            'url': response.url,
            'content': response.text,
            'path':re.findall('.*(id=.*)$',response.url)[0]
        }
