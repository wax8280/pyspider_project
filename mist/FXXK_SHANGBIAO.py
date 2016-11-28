# coding: utf-8

from pyspider.libs.base_handler import *
from copy import deepcopy

name = u'探迹'


class Handler(BaseHandler):
    crawl_config = {
    }
    post_headers = {

        'Accept': 'text/plain, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Referer': '',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',

    }
    get_headers = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': '',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
    }

    referer_url = u'http://www.itaotm.com/search.php?seat=%E4%B8%8D%E9%99%90%E6%9D%A1%E4%BB%B6&searchKey={}'
    post_url = u'http://www.itaotm.com/search!ajaxSearch.php'
    get_url = u'http://www.itaotm.com/search!page.php?pageNo=1&l={}&gjfls={}gjfl=0&seat=%E4%B8%8D%E9%99%90%E6%9D%A1%E4%BB%B6&searchKey={}'
    post_things = u'pageNo=1&l=&gjfls=0&gjfl=0&seat=%E4%B8%8D%E9%99%90%E6%9D%A1%E4%BB%B6&searchKey={}'

    def on_start(self):
        self.crawl(
            self.referer_url.format(name),
            callback=self.post_1,
            proxy='localhost:3128',
        )

    @config(priority=2)
    def post_1(self, response):
        new_header = deepcopy(self.post_headers)
        new_header['Referer'] = self.referer_url.format(name)

        self.crawl(self.post_url,
                   callback=self.get_1,
                   method='POST',
                   headers=new_header,
                   data=self.post_things.format(name),
                   save={'kw': name, 'referer': new_header['Referer']},
                   cookies=response.cookies,
                   proxy='localhost:3128',
                   )

    @config(priority=2)
    def get_1(self, response):
        r = response.text.split(u':')
        print r
        if r[0] == u'SUCCESS':
            new_header = deepcopy(self.get_headers)
            new_header['Referer'] = response.save.get('referer')

            r[2] = r[2].replace(u';', u'%3B')
            url = self.get_url.format(r[1], r[2], response.save.get('kw'))

            self.crawl(url,
                       callback=self.get_content,
                       headers=new_header,
                       cookies=response.cookies,
                       proxy='localhost:3128',
                       )

    def get_content(self, response):
        pass
