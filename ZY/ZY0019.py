# coding: utf-8
from pyspider.libs.base_handler import *
from copy import deepcopy

DIVIDE = 2
BEGIN = 0


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
    names = None

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 10,
    }

    txt_url = 'http://tungee-static.oss-cn-shenzhen.aliyuncs.com/spider/ZY0019/URLApplestore.txt'

    def on_start(self):
        self.crawl(self.txt_url,
                   callback=self.list_page,
                   force_update=True,
                   save={'now': BEGIN})

    @config(priority=2)
    def list_page(self, response):
        if not self.names:
            self.names = response.text.split('\n')
            self.url_list_length = len(self.names)

        now_list = self.names[response.save.get('now'):min(response.save.get('now') + DIVIDE, self.url_list_length)]

        for each in now_list:
            self.crawl(each.strip(),
                       callback=self.get_content_to_dev,
                       proxy='localhost:3128',
                       validate_cert=False,
                       )

        if min(response.save.get('now') + DIVIDE, self.url_list_length) != self.url_list_length:
            now = min(response.save.get('now') + DIVIDE, self.url_list_length)

            self.crawl(self.txt_url + '?now=' + str(now),
                       callback=self.list_page,
                       force_update=True,
                       save={'now': now})

    @config(priority=3)
    def get_content_to_dev(self, response):
        """
        获取app页面的详细信息，并得到其公司的连接入口，然后callback get_company
        """
        for dev_a in response.doc('a.view-more').items():
            dev_url = dev_a.attr.href

        new_header = deepcopy(self.default_headers)
        new_header['Referer'] = response.url

        if dev_url:
            self.crawl(dev_url, callback=self.get_dev_app,
                       headers=new_header,
                       proxy='localhost:3128',
                       validate_cert=False,
                       save={'num': '0'})

        return {'content': response.text}

    @config(priority=4)
    def get_dev_app(self, response):
        """
        从js代码中寻找出要post的数据，然后模拟翻页与遍历当前页面的所有app
        """

        new_header = deepcopy(self.default_headers)
        new_header['Referer'] = response.url

        # 遍历当前的所有app
        for a in response.doc('#content > div > div:nth-child(2) > div:nth-child(2) a.name').items():
            self.crawl(a.attr.href,
                       callback=self.get_content,
                       headers=new_header,
                       proxy='localhost:3128',
                       validate_cert=False,
                       )
        # 翻页
        li = list(response.doc('#content > div > div:nth-child(2) > div:nth-child(2) > ul > li').items())
        if li:
            next_page = None
            for i in li:
                if i.find('a').attr.class_ == u'paginate-more':
                    next_page = i.find('a')
                    break

            if next_page:
                self.crawl(next_page.attr.href,
                           callback=self.get_dev_app,
                           headers=new_header,
                           proxy='localhost:3128',
                           validate_cert=False,
                           )

    @config(priority=5)
    def get_content(self, response):
        return {'content': response.text}
