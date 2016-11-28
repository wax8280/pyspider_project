# !/usr/bin/env python
# coding: utf-8

from pyspider.libs.base_handler import *
import re
from copy import deepcopy
from urllib import urlencode
import random

SESSION_NUM = 5


class Handler(BaseHandler):
    get_session_url = 'http://www.miitbeian.gov.cn/publish/query/indexFirst.action'
    get_verify_code_url = 'http://www.miitbeian.gov.cn/getVerifyCode?'
    get_result_url = 'http://www.miitbeian.gov.cn/icp/publish/query/icpMemoInfo_searchExecute.action'

    post_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Pragma': 'no-cache',
        'Referer': 'http://www.miitbeian.gov.cn/icp/publish/query/icpMemoInfo_showPage.action',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    }

    def on_start(self):
        self.crawl(
            self.get_session_url,
            callback=self.get_session,
            save={'to_search': u'广州探迹科技有限公司'}
        )

    def get_session(self, response):
        self.crawl(
            self.get_session_url,
            callback=self.get_verify_code,
            save={'to_search': response.save.get('to_search')}
        )

    def get_verify_code(self, response):

        self.crawl(
            self.get_verify_code_url + str(random.randint(0, 100)),
            cookies=response.cookies,
            save={'to_search': response.save.get('to_search')}

        )

    def get_verify_result(self, response):
        self.crawl(
            'http://112.74.93.18:14067/api/model/recognition/SINA',
            callback=self.get_result,
            method='POST',
            files={'file': ('a.png', response.content, 'image/png')},
            save={
                'cookies': response.cookies,
            }
        )

    def get_result(self, response):

        result = response.json

        # 这里post验证码
        if result.get('result'):
            yzm = result.get('result')

            data = urlencode({
                'siteName': '',
                'siteDomain': '',
                'siteUrl': '',
                'condition': '3',
                'mainLicense': response.save.get('to_search').encode('gbk'),
                'siteIp': '',
                'unitName': '',
                'mainUnitNature': '-1',
                'certType': '-1',
                'mainUnitCertNo': '',
                'verifyCode': yzm
            })

            self.crawl(
                self.get_result_url,
                callback=self.get_detail,
                # proxy='localhost:3128',
                cookies=response.save.get('cookies'),
                method='POST',
                data=data,
                headers=self.post_headers,
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
