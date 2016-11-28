# coding: utf-8

from pyspider.libs.base_handler import *
import re
from copy import deepcopy
from pyquery import PyQuery as pq
import time

BEGIN = 0
DIVIDE = 5

ShouldTry = 10


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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',

    }

    get_yzm_headers = {
        'Accept': 'image/webp,image/*,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'http://s.weibo.com/user/%E8%85%BE%E8%AE%AF',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 10,
        'etag': False,
        'last_modified': False,

    }

    url = u'http://s.weibo.com/user/{key_word}'

    # TODO
    api_url = u'http://112.74.93.18:10265/api/names?start={}&end={}'
    yzm_base_url = u'http://s.weibo.com/ajax/pincode/pin?type=sass{}'
    verify_base_url = u'http://s.weibo.com/ajax/pincode/verified?__rnd={}'

    # 正式
    # api_url = u'http://10.26.229.2:10265/api/names?start={}&end={}'

    def on_start(self):
        self.crawl(self.api_url.format(BEGIN, BEGIN + DIVIDE),
                   save={
                       'end': BEGIN + DIVIDE
                   },
                   callback=self.list_page,
                   force_update=True,
                   headers=self.tungee_header)

    def list_page(self, response):
        '''
        从API中获取公司名，并callback get_detail 去爬取微博搜索首页
        '''

        names = response.text.split('\n')
        now = response.save['end']
        if len(names) > 1:
            self.crawl(self.api_url.format(now, now + DIVIDE),
                       save={
                           'end': now + DIVIDE
                       },
                       callback=self.list_page,
                       headers=self.tungee_header)

        for name in names:
            if len(name.strip()):
                self.crawl(self.url.format(key_word=name.strip()),
                           callback=self.get_detail,
                           # proxy='localhost:3128',
                           save={'try_time': 1, 'company_name': name.strip()})

    @config(priority=2)
    def get_detail(self, response):
        '''
        判断首页有无结果，无结果返回；有结果就根据认证，性别，年龄 的组合 callback result_page
        '''

        # 被ban

        print response.url
        print response.headers
        print response.text

        fxxk_yzm = False
        if response.save.get('Referer'):
            url = response.save.get('Referer')
            result = response.json
            if result:
                code = result.get('code')

                if code == '1000000':
                    fxxk_yzm = True
        else:
            url = response.url

        header = deepcopy(self.get_yzm_headers)
        header['Referer'] = url

        if u'\\u9a8c\\u8bc1\\u7801' in response.text or not fxxk_yzm:
            # 从js中提取
            get_time = re.search(u'type=sass&ts=(\d+)\\\\\" node-type=\\\\\"yzm_img\\\\\">', response.text)
            if get_time:
                yzm_num = int(get_time.groups()[0] + u'0000')
            else:
                yzm_num = unicode(int(time.time())) + u'000'

            # 获取验证码
            self.crawl(self.yzm_base_url.format(unicode(yzm_num)),
                       callback=self.get_yzm,
                       headers=header,
                       # proxy='localhost:3128',
                       save={'company_name': response.save.get('company_name'), 'yzm_num': yzm_num,
                             'Referer': url},
                       force_update=True,
                       cookies=response.cookies)
            return

        else:

            # 首页啥都没有的公司
            if u'noresult_tit' in response.text:
                return

            # 认证，性别，年龄 的组合
            url_list = [url + u'&' + u'&'.join(each_detail) for each_detail in self.catalogue]

            for each_url in url_list:
                self.crawl(each_url,
                           callback=self.result_page,
                           headers=header,
                           # save header 用于下次被ban的时候重试
                           save={'header': header, 'try_time': 1, 'company_name': response.save.get('company_name')},
                           # proxy='localhost:3128',
                           cookies=response.cookies)

    @config(priority=10)
    def get_yzm(self, response):
        """
        识别验证码
        :param response:
        :return:
        """
        print response.save.get('Referer')
        self.crawl('http://112.74.93.18:14067/api/model/recognition/SINA',
                   callback=self.get_yzm_result,
                   method='POST',
                   files={'file': ('a.png', response.content, 'image/png')},
                   save={'cookies': response.cookies, 'company_name': response.save.get('company_name'),
                         'yzm_num': response.save.get('yzm_num'), 'Referer': response.save.get('Referer')})

    @config(priority=11)
    def get_yzm_result(self, response):
        """
        根据得到的识别结果，模拟验证
        :param response:
        :return:
        """

        result = response.json
        print result
        header = deepcopy(self.get_yzm_headers)
        header['Referer'] = response.save.get('Referer')

        # 这里post验证码给新浪
        if result.get('result'):
            yzm = result.get('result')
            data = {'secode': yzm, 'type': 'sass', 'pageid': 'user', '_t': '0'}

            self.crawl(self.verify_base_url.format(unicode(response.save.get('yzm_num')) + u'50'),
                       callback=self.get_detail,
                       # proxy='localhost:3128',
                       cookies=response.save.get('cookies'),
                       method='POST',
                       data=data,
                       headers=header,
                       save={'company_name': response.save.get('company_name'), 'Referer': response.save.get('Referer')}
                       )

        # 如果识别失败继续获得验证码
        else:

            self.crawl(self.yzm_base_url.format(unicode(int(response.save.get('yzm_num')) + 1)),
                       callback=self.get_yzm,
                       save={'company_name': response.save.get('company_name'),
                             'Referer': response.save.get('Referer'),
                             'yzm_num': response.save.get('yzm_num'),
                             'cookies': response.cookies,
                             },
                       headers=header,
                       cookies=response.save.get('cookies')
                       )

    @config(priority=3)
    def result_page(self, response):
        """
        每种不同的组合
        :param response:
        :return:
        """

        # 被ban
        if u'\\u9a8c\\u8bc1\\u7801' in response.text:
            # 从js中提取
            time = re.search(u'type=sass&ts=(\d+)\\\\\" node-type=\\\\\"yzm_img\\\\\">', response.text)
            if time:
                yzm_num = int(time.groups()[0] + u'0000')
            else:
                yzm_num = unicode(int(time.time())) + u'000'

            # 获取验证码
            self.crawl(self.yzm_base_url.format(unicode(yzm_num)),
                       callback=self.get_yzm,
                       # proxy='localhost:3128',
                       save={'company_name': response.save.get('company_name'), 'yzm_num': yzm_num},
                       force_update=True,
                       cookies=response.cookies)
            return

        # 提取js里面的url
        # url_list = [i.replace(u'\\', u'').replace(u'"', u'')
        #             for i in
        #             set(re.findall(u'http:\\\\/\\\\/weibo\.com\\\\/[^/]+?\?refer_flag=.*?\\\\"', response.text))]

        raw_html = re.findall(ur'"html":"(.*?)\\n\\n"}', response.text)

        # 提取js里面的url
        url_list = []
        if raw_html:
            html = raw_html[0].replace(u'\\"', u'"').replace(u'\\/', u'/').replace(u'\\n', u'\n'). \
                replace(u'\\t', u'\t').decode("unicode-escape")

            fxxk = pq(html)

            for _ in fxxk('.list_person').items():
                for i in _('.person_addr a').items():
                    url = i.attr('href')
                for j in _('.person_card').items():
                    text = j.text()

                if response.save.get('company_name') in text:
                    url_list.append(url)

        header = deepcopy(self.default_headers)
        header['Referer'] = response.url
        header['User-Agent'] = 'Sosoimagespider+(+http://help.soso.com/soso-image-spider.htm)'

        for each_url in url_list:
            self.crawl(each_url,
                       callback=self.get_content,
                       headers=header,
                       cookies=response.cookies,
                       # proxy='localhost:3128',
                       # save 用于获取用户页的时候，出现重定向的重试
                       save={'header': header, 'url': each_url, 'try_time': 1, 'cookies': response.cookies}
                       )

    @config(priority=4)
    def get_content(self, response):
        """
        获取微博详情页
        :param response:
        :return:
        """

        # 被ban
        # 被redirect到登录页面,重试
        if u'passport.weibo.com' in response.url:
            if response.save.get('try_time') < ShouldTry:
                self.crawl(response.save.get('url'),
                           callback=self.get_content,
                           headers=response.save.get('header'),
                           cookies=response.save.get('cookies'),
                           # proxy='localhost:3128',
                           save={'header': response.save.get('header'), 'url': response.save.get('url'),
                                 'try_time': response.save.get('try_time') + 1, 'cookies': response.cookies},
                           force_update=True)
            return

        return {
            'content': response.text,
            'url': response.url
        }
