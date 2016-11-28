#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-11-25 17:41:37
# Project: ZY0040

from pyspider.libs.base_handler import *
import datetime

BEGIN = 0
DIVIDE = 20


class Handler(BaseHandler):
    retry_delay = {
        1: 1,
        2: 2,
        3: 8,

    }

    default_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Pragma': 'no-cache',
        'Referer': 'http://www.cqaso.com/toplist?type=top1500',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
        'x-auth-token': 'false',
    }

    crawl_config = {
        'itag': 'v1',
        'headers': default_headers,
        'retries': 3,

    }

    country = ["US", "HK", "TW", "JP", "TH", "KR", "ID", "MY", "IN", "RU", "BR", "VN", "KH", "PH"]

    cats = ["36", "6000", "6001", "6002", "6003", "6004", "6005", "6006", "6007", "6008", "6009", "6010", "6011",
            "6012", "6013", "6014", "6015", "6016", "6017", "6018", "6019", "6020", "6021", "6022", "6023", "6024",
            "6025"]
    rating = ["27", "30", "38"]

    # start is 0 to 1470
    base_url = 'http://backend.cqaso.com/topList/{cats}/{rating}?limit=70&offset={start}&country={country}'
    update_time_url = 'http://backend.cqaso.com/topList/36/27/status?country={}'

    def on_start(self):
        now_date = unicode((datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
        self.crawl('http://www.cqaso.com/',
                   callback=self.get_update_time,
                   force_update=True,
                   proxy='localhost:3128',
                   headers=self.default_headers,
                   itag=now_date,
                   save={'itag': now_date}
                   )

    def get_update_time(self, response):
        for url, country_name in [(self.update_time_url.format(j), j) for j in self.country]:
            self.crawl(
                url,
                itag=response.save.get('itag'),
                proxy='localhost:3128',
                callback=self.list_page,
                headers=self.default_headers,
                save={'country': country_name, 'itag': response.save.get('itag')},
            )

    @config(priority=2)
    def list_page(self, response):
        for each_cats in self.cats:
            for each_rating in self.rating:
                for count_ in range(0, 1470 + 1, 70):
                    self.crawl(
                        self.base_url.format(country=response.save.get('country'),
                                             cats=each_cats,
                                             rating=each_rating,
                                             start=count_),
                        proxy='localhost:3128',
                        itag=response.save.get('itag'),
                        force_update=True,
                        callback=self.get_conent,
                        headers=self.default_headers,
                        save={'update_time': response.text}
                    )

    @config(priority=3)
    def get_conent(self, response):
        return {
            'content': 'update_time:' + response.save.get('update_time') + response.text,
            'url': response.url
        }
