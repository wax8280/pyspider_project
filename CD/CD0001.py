# coding: utf-8
from pyspider.libs.base_handler import *
import re
from itertools import combinations

temp = ['param1=00001', 'param1=00002', 'param1=00003', 'param1=00004', 'param1=00005', 'param1=00006', 'param1=00007',
        'param1=00008', 'param1=00009', 'param1=00010', 'param1=00011', 'param1=00012', 'param1=00013', 'param1=00014',
        'param1=00015', 'param1=00016', 'param1=00017', 'param1=00018', 'param1=00019', 'param1=00020', 'param1=00021',
        'param2=0', 'param2=1', 'param2=2', 'param2=3', 'param2=4', 'param2=5', 'param2=6', 'param2=7', 'param2=8',
        'param2=9',
        'param3=2010/2011', 'param3=2011/2012', 'param3=2012/2013', 'param3=2013/2014', 'param3=2014/2015',
        'param3=2015/2016',
        'param4=%E5%8C%97%E4%BA%AC', 'param4=%E4%B8%8A%E6%B5%B7', 'param4=%E5%A4%A9%E6%B4%A5',
        'param4=%E5%B9%BF%E4%B8%9C', 'param4=%E6%B5%99%E6%B1%9F',
        'param4=%E6%B1%9F%E8%8B%8F', 'param4=%E5%B1%B1%E4%B8%9C', 'param4=%E7%A6%8F%E5%BB%BA',
        'param5=0', 'param5=1', 'param5=2', 'param5=3', 'param5=4', 'param5=5', 'param5=6',
        ]


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
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'http://www.chinaventure.com.cn/event/list.shtml',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 10,
    }

    base_url = u'http://www.chinaventure.com.cn/event/searchInvestList/{param1}/{param2}/{param3}/{param4}/{param5}/0-16.shtml'

    detail_base_url = u'http://www.chinaventure.com.cn/cvmodule/enterprise/detail/{}.shtml'

    all_url = [(base_url.format(
        param1=_[0].replace('param1=', ''),
        param2=_[1].replace('param2=', ''),
        param3='-1/-1',
        param4=_[2].replace('param4=', ''),
        param5='-1',
    ), _[0].replace('param1=', ''), _[1].replace('param2=', ''), _[2].replace('param4=', ''))
               for _ in combinations(temp, 3)
               if 'param1' in _[0]
               and 'param2' in _[1]
               and 'param4' in _[2]
               ]

    def on_start(self):
        self.crawl(self.all_url[0][0],
                   callback=self.get_list,
                   force_update=True,
                   etag=False,
                   last_modified=False,
                   proxy='localhost:3128',
                   save={'param1': self.all_url[0][1], 'param2': self.all_url[0][2], 'param4': self.all_url[0][3],
                         'first': True}
                   )

    @config(priority=2)
    def get_list(self, respnose):
        result = respnose.json

        if len(result['data']) == 16:
            if u'/-1/' in respnose.url:
                # 这里遍历其他param
                param1 = respnose.save.get('param1')
                param2 = respnose.save.get('param2')
                param4 = respnose.save.get('param4')

                if param1 and param2 and param4:
                    for i in combinations(temp, 2):
                        if 'param3' in i[0] and 'param5' in i[1]:
                            url = self.base_url.format(
                                param1=param1,
                                param2=param2,
                                param3=i[0].replace('param3=', ''),
                                param4=param4,
                                param5=i[1].replace('param5=', '')
                            )
                            self.crawl(
                                url,
                                callback=self.get_list,
                                proxy='localhost:3128',
                                save={}
                            )
                return

            else:
                # 翻页
                _1, _2 = re.search(u'/(\d+)-(\d+).shtml', respnose.url).groups()
                new_url = re.sub('/(\d+)-(\d+).shtml', '/{}-{}.shtml'.format(int(_1) + 15, _2), respnose.url)
                self.crawl(
                    new_url,
                    callback=self.get_list,
                    # proxy='localhost:3128',
                    save={}
                )

        # 对于长度不满的，不论是否是-1，都一律用得上，走下一步；对于满的就不用说了
        for each in result['data']:
            detail_url = self.detail_base_url.format(each['targetEnterprise']['id'])
            self.crawl(
                detail_url,
                callback=self.get_content,
                proxy='localhost:3128',
            )

        if respnose.save.get('first'):
            for _ in self.all_url:
                self.crawl(_[0],
                           callback=self.get_list,
                           force_update=True,
                           etag=False,
                           last_modified=False,
                           proxy='localhost:3128',
                           save={'param1': _[1], 'param2': _[2], 'param4': _[3], }
                           )

    @config(priority=3)
    def get_content(self, response):
        return {
            'content': response.text,
            'url': response.url
        }
