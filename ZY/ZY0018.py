# coding: utf-8
from pyspider.libs.base_handler import *
import re
from copy import deepcopy
from random import choice
import json

the_proxy = ('nbt_spider:nbt_spider@45.35.236.206:8888', 'nbt_spider:nbt_spider@172.106.64.215:8888',
             'nbt_spider:nbt_spider@45.35.226.202:8888', 'nbt_spider:nbt_spider@172.106.63.110:8888',
             'nbt_spider:nbt_spider@172.106.68.104:8888', 'nbt_spider:nbt_spider@172.106.46.78:8888',
             'nbt_spider:nbt_spider@172.106.68.103:8888', 'nbt_spider:nbt_spider@45.34.13.137:8888',
             'nbt_spider:nbt_spider@172.107.13.164:8888', 'nbt_spider:nbt_spider@172.106.63.107:8888',
             'nbt_spider:nbt_spider@104.217.249.173:8888', 'nbt_spider:nbt_spider@107.160.73.98:8888',
             'nbt_spider:nbt_spider@107.160.125.157:8888', 'nbt_spider:nbt_spider@107.160.125.146:8888',
             'nbt_spider:nbt_spider@104.217.249.184:8888', 'nbt_spider:nbt_spider@107.160.73.108:8888',
             'nbt_spider:nbt_spider@104.217.249.190:8888', 'nbt_spider:nbt_spider@104.217.249.174:8888',
             'nbt_spider:nbt_spider@172.106.46.70:8888', 'nbt_spider:nbt_spider@172.106.240.147:8888',
             'nbt_spider:nbt_spider@45.35.226.204:8888', 'nbt_spider:nbt_spider@107.160.73.99:8888',
             'nbt_spider:nbt_spider@45.34.13.138:8888', 'nbt_spider:nbt_spider@45.35.234.237:8888',
             'nbt_spider:nbt_spider@104.217.249.164:8888', 'nbt_spider:nbt_spider@172.106.64.212:8888',
             'nbt_spider:nbt_spider@172.106.63.106:8888', 'nbt_spider:nbt_spider@172.107.13.162:8888',
             'nbt_spider:nbt_spider@104.217.249.171:8888', 'nbt_spider:nbt_spider@172.106.68.98:8888',
             'nbt_spider:nbt_spider@172.106.62.5:8888', 'nbt_spider:nbt_spider@172.106.63.104:8888',
             'nbt_spider:nbt_spider@172.106.62.14:8888', 'nbt_spider:nbt_spider@107.160.125.154:8888',
             'nbt_spider:nbt_spider@45.35.175.235:8888', 'nbt_spider:nbt_spider@107.160.125.151:8888',
             'nbt_spider:nbt_spider@45.35.234.234:8888', 'nbt_spider:nbt_spider@45.35.234.230:8888',
             'nbt_spider:nbt_spider@172.106.96.69:8888', 'nbt_spider:nbt_spider@172.106.46.77:8888',
             'nbt_spider:nbt_spider@172.106.240.157:8888', 'nbt_spider:nbt_spider@45.35.234.231:8888',
             'nbt_spider:nbt_spider@172.106.64.218:8888', 'nbt_spider:nbt_spider@45.35.236.201:8888',
             'nbt_spider:nbt_spider@172.106.64.222:8888', 'nbt_spider:nbt_spider@45.35.236.198:8888',
             'nbt_spider:nbt_spider@172.106.46.66:8888', 'nbt_spider:nbt_spider@45.35.175.228:8888',
             'nbt_spider:nbt_spider@45.35.226.206:8888', 'nbt_spider:nbt_spider@172.106.68.108:8888')

DIVIDE = 2
localproxy = '127.0.0.1:56823'


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
    names = None

    crawl_config = {
        'itag': 'v7',
        'headers': default_headers,
        'retries': 10,
        'last_modified': False,
        'etag': False,
    }

    def get_taskid(self, task):
        return md5string(task['url'] + json.dumps(task['fetch'].get('data', '')))

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://tungee-static.oss-cn-shenzhen.aliyuncs.com/spider/ZY0018/URLgoogleplay.txt?now=b-1',
                   callback=self.list_page,
                   force_update=True,
                   save={'now': 0})

    @config(priority=2)
    def list_page(self, response):
        if not self.names:
            self.names = response.text.split('\n')

        now = self.names[response.save.get('now'):(response.save.get('now') + DIVIDE)]

        for each in now:
            self.crawl(each.strip(),
                       callback=self.get_content_to_company,
                       proxy=choice(the_proxy),
                       fetch_type='requests',
                       # proxy=localproxy,
                       validate_cert=False,
                       headers=self.default_headers,
                       )
        if int(response.save.get('now')) < 4120:
            self.crawl('http://tungee-static.oss-cn-shenzhen.aliyuncs.com/spider/ZY0018/URLgoogleplay.txt?now=b' + str(
                response.save.get('now') + DIVIDE),
                       callback=self.list_page,
                       force_update=True,
                       save={'now': response.save.get('now') + DIVIDE})

    @config(priority=3)
    def get_content_to_company(self, response):
        """
        获取app页面的详细信息，并得到其公司的连接入口，然后callback get_company
        """

        url = re.search(u'document-subtitle primary" href="(.*?)"', response.text)
        if url:
            url = url.groups()
        if url:
            post_data = {
                'ipf': '1',
                'xhr': '1'
            }

            url = u'https://play.google.com' + url[0]

            new_header = deepcopy(self.default_headers)
            new_header['Referer'] = url

            url = url + u'&authuser=0'

            self.crawl(url, callback=self.get_comapny,
                       method='POST',
                       data=post_data,
                       headers=new_header,
                       proxy=choice(the_proxy),
                       fetch_type='requests',
                       # proxy=localproxy,
                       validate_cert=False,
                       save={'num': '0'})

        return {'content': response.text}

    @config(priority=4)
    def get_comapny(self, response):
        """
        从js代码中寻找出要post的数据，然后模拟翻页与遍历当前页面的所有app
        """
        url = response.url

        new_header = deepcopy(self.default_headers)
        new_header['Referer'] = response.url.replace(u'&authuser=0', u'')

        # 从js代码中寻找出pagTok
        nbp = re.findall(u"var nbp='(.+?)'", response.text)
        if nbp:
            got = None
            print nbp
            print nbp[-1]
            print nbp[-1].replace(u'[', u'').replace(u']', u'').split(u',')
            for _ in nbp:
                nbp_list = _.replace(u'[', u'').replace(u']', u'').split(u',')
                for each in nbp_list:
                    if each.startswith(u'\\x22') and each.endswith(u'\\x22') and u'S' in each:
                        got = each
                        break

            if got:
                print got
                print response.save
                pagTok = got.replace(u'\\x22', u'').decode("unicode-escape")
                if pagTok:
                    post_data = {'start': '0',
                                 'num': str(24),
                                 'numChildren': '0',
                                 'cctcss': 'square-cover',
                                 'cllayout': 'NORMAL',
                                 'ipf': '1',
                                 'xhr': '1',
                                 }

                    post_data.update({'pagTok': pagTok})

                    print post_data
                    # 模拟翻页，继续寻找app

                    # 防止重复
                    for a in list(response.doc('a').items())[:-1]:
                        if a.attr.class_ == u'title':
                            last = a.attr.href
                            break

                    new_header_2 = deepcopy(self.default_headers)
                    new_header_2['Referer'] = response.url
                    print new_header_2

                    print {'last': last}
                    print response.save.get('last')
                    if response.save.get('last') != last:
                        self.crawl(url, callback=self.get_comapny,
                                   method='POST',
                                   data=post_data,
                                   headers=new_header_2,
                                   proxy=choice(the_proxy),
                                   fetch_type='requests',
                                   # proxy=localproxy,
                                   validate_cert=False,
                                   force_update=True,
                                   save={'num': post_data['num'], 'last': last})

        # 遍历当前的所有app
        for a in response.doc('a').items():
            if a.attr.class_ == u'title':
                self.crawl(a.attr.href,
                           callback=self.get_content,
                           headers=new_header,
                           proxy=choice(the_proxy),
                           fetch_type='requests',
                           # proxy=localproxy,
                           validate_cert=False,
                           )

    @config(priority=5)
    def get_content(self, response):

        return {'content': response.text}
