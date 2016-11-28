# coding: utf-8
from pyspider.libs.base_handler import *
import re
from copy import deepcopy
from random import choice
import json

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

url_list = ["https://play.google.com/store/apps/developer?id=%D8%A5%D8%B4%D8%B1%D8%A7%D9%82+%D8%B3%D9%88%D9%81%D8%AA",
            "https://play.google.com/store/apps/developer?id=360+Mobile+Security+Limited",
            "https://play.google.com/store/apps/dev?id=8339838690752454700",
            "https://play.google.com/store/apps/developer?id=Akhbary+News",
            "https://play.google.com/store/apps/developer?id=Amber+Widgets+Dev+Team",
            "https://play.google.com/store/apps/dev?id=7269704759597705101",
            "https://play.google.com/store/apps/developer?id=APUS+APPS",
            "https://play.google.com/store/apps/developer?id=APUS-Group",
            "https://play.google.com/store/apps/dev?id=4946022439885210717",
            "https://play.google.com/store/apps/developer?id=BIGO+TECHNOLOGY+PTE.+LTD.",
            "https://play.google.com/store/apps/developer?id=Blue+City+Holdings+Co.,+Ltd.",
            "https://play.google.com/store/apps/dev?id=6370183851577139979",
            "https://play.google.com/store/apps/dev?id=7495131674787494593",
            "https://play.google.com/store/apps/developer?id=DewMobile,+Inc.",
            "https://play.google.com/store/apps/dev?id=6599001017670379452",
            "https://play.google.com/store/apps/dev?id=6316943423134249549",
            "https://play.google.com/store/apps/developer?id=Douban",
            "https://play.google.com/store/apps/developer?id=Eachpal+LLC",
            "https://play.google.com/store/apps/developer?id=Fotoable,Inc.",
            "https://play.google.com/store/apps/dev?id=9100920795539921067",
            "https://play.google.com/store/apps/developer?id=gameone",
            "https://play.google.com/store/apps/dev?id=8510354798619325021",
            "https://play.google.com/store/apps/dev?id=8821041580638508880",
            "https://play.google.com/store/apps/dev?id=6628972054788109461",
            "https://play.google.com/store/apps/dev?id=5770823124985252086",
            "https://play.google.com/store/apps/developer?id=iDailybread.org",
            "https://play.google.com/store/apps/dev?id=7892913269075721495",
            "https://play.google.com/store/apps/dev?id=6055027427763974132",
            "https://play.google.com/store/apps/developer?id=KloudPeak+Networks+Limited",
            "https://play.google.com/store/apps/developer?id=LinkDesks+Inc.",
            "https://play.google.com/store/apps/developer?id=LIONMOBI",
            "https://play.google.com/store/apps/developer?id=Lonfun",
            "https://play.google.com/store/apps/dev?id=4693243250505878987",
            "https://play.google.com/store/apps/developer?id=m.jollychic",
            "https://play.google.com/store/apps/developer?id=NECTEC",
            "https://play.google.com/store/apps/developer?id=NIP",
            "https://play.google.com/store/apps/developer?id=NQ+Mobile+Security+(NYSE:NQ)",
            "https://play.google.com/store/apps/developer?id=NQ+Mobile+US",
            "https://play.google.com/store/apps/developer?id=Panli%E4%BB%A3%E8%B4%AD",
            "https://play.google.com/store/apps/dev?id=7074450904720558835",
            "https://play.google.com/store/apps/developer?id=Pink+Themes+for+Hola+Launcher",
            "https://play.google.com/store/apps/developer?id=Pop+Star+Games",
            "https://play.google.com/store/apps/developer?id=PTeam",
            "https://play.google.com/store/apps/dev?id=8937379671344331084",
            "https://play.google.com/store/apps/developer?id=Samitivej+Public+Company+Limited",
            "https://play.google.com/store/apps/dev?id=8854450600049889113",
            "https://play.google.com/store/apps/developer?id=Themes+for+phone",
            "https://play.google.com/store/apps/dev?id=8366355937984342588",
            "https://play.google.com/store/apps/dev?id=6091442766932589829",
            "https://play.google.com/store/apps/dev?id=8321696171123618246",
            "https://play.google.com/store/apps/dev?id=4614371506383368969",
            "https://play.google.com/store/apps/developer?id=Wahoo+Fitness",
            "https://play.google.com/store/apps/developer?id=Weather+Widget+Theme+Dev+Team",
            "https://play.google.com/store/apps/developer?id=XMan",
            "https://play.google.com/store/apps/developer?id=ZUI",
            "https://play.google.com/store/apps/developer?id=ZUI+Locker",
            "https://play.google.com/store/apps/developer?id=%E6%B7%98%E5%AE%9D",
            "https://play.google.com/store/apps/developer?id=%E6%B7%98%E5%AE%9D%E6%95%B0%E5%AD%97%E4%BA%A7%E5%93%81%E4%B8%9A%E5%8A%A1%E9%83%A8",
            "https://play.google.com/store/apps/developer?id=%E6%B7%98%E5%AE%9D%E6%97%A0%E7%BA%BF"]

DIVIDE = 2
localproxy = '127.0.0.1:56823'


class Handler(BaseHandler):
    retry_delay = {
        1: 1,
        2: 2,
        3: 8,
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
        'itag': 'v1',
        'headers': default_headers,
        'retries': 3,
    }

    dev_url = u"https://play.google.com/store/apps/dev?id={}"

    developer_url = u'https://play.google.com/store/apps/developer?id={}'

    dev_post_url = u'https://play.google.com/store/xhr/searchcontent?authuser=0'

    developer_post = {'start': '0',
                      'num': '24',
                      'numChildren': '0',
                      'cctcss': 'square-cover',
                      'cllayout': 'NORMAL',
                      'ipf': '1',
                      'xhr': '1',
                      }

    dev_post = {
        'pageNum': 1,
        'sp': '',
        'pagTok': '',
        'xhr': 1,
    }

    def get_taskid(self, task):
        return md5string(task['url'] + json.dumps(task['fetch'].get('data', '')))

    def on_start(self):
        self.crawl('https://play.google.com/store',
                   fetch_type='requests',
                   callback=self.list_page,
                   proxy=choice(the_proxy),
                   force_update=True
                   )

    @config(priority=2)
    def list_page(self, response):
        for each in url_list:
            self.crawl(self.developer_url.format(each),
                       callback=self.get_comapny,
                       proxy=choice(the_proxy),
                       fetch_type='requests',
                       validate_cert=False,
                       headers=self.default_headers,
                       save={'last': u'', 'first': True, 'id': each}
                       )

    @config(priority=4)
    @catch_status_code_error
    def get_comapny(self, response):
        """
        从js代码中寻找出要post的数据，然后模拟翻页与遍历当前页面的所有app
        """

        if response.status_code == 200:

            # developer get next page
            # or developer(authuser) get next page
            if u'developer?id' in response.url:
                url = response.url if u'&authuser=0' in response.url else response.url + u'&authuser=0'

                # find pagTok in js codes
                nbp = re.findall(u"var nbp='(.+?)'", response.text)
                if nbp:
                    got = None
                    print nbp
                    print nbp[-1].replace(u'[', u'').replace(u']', u'').split(u',')
                    for _ in nbp:
                        nbp_list = _.replace(u'[', u'').replace(u']', u'').split(u',')
                        for each in nbp_list:
                            if each.startswith(u'\\x22') and each.endswith(u'\\x22') and u'S' in each:
                                got = each
                                break

                    if got:
                        pagTok = got.replace(u'\\x22', u'').decode("unicode-escape")
                        if pagTok:
                            post_data = deepcopy(self.developer_post)
                            post_data.update({'pagTok': pagTok})
                            print post_data

                            # get last href,in order to prevent repeat
                            for a in list(response.doc('a').items())[:-1]:
                                if a.attr.class_ == u'title':
                                    last = a.attr.href
                                    break

                            new_header = deepcopy(self.default_headers)
                            new_header['Referer'] = response.url

                            # if this page as same as last page,means that is end
                            if response.save.get('last') != last:
                                self.crawl(
                                    url,
                                    callback=self.get_comapny,
                                    method='POST',
                                    data=post_data,
                                    headers=new_header,
                                    proxy=choice(the_proxy),
                                    fetch_type='requests',
                                    # proxy=localproxy,
                                    validate_cert=False,
                                    force_update=True,
                                    save={'last': last, 'first': False}
                                )

            # dev get next page
            # or self.dev_post_url get next page
            elif u'dev?id=' in response.url or response.url == self.dev_post_url:
                # if so,not the first time
                if response.save.get('sp'):

                    pagTok = re.search(u',"([\w\:]*?)"', response.text)

                    if pagTok:
                        pagTok = pagTok.group(0)

                        post_data = deepcopy(self.dev_post)
                        post_data['sp'] = response.save.get('sp')
                        post_data['pageNum'] = response.save.get('pageNum') + 1
                        post_data['pagTok'] = pagTok

                        new_header = deepcopy(self.default_headers)
                        new_header['Referer'] = response.save.get('refer_url')

                        self.crawl(
                            self.dev_post_url,
                            callback=self.get_comapny,
                            method='POST',
                            data=post_data,
                            proxy=choice(the_proxy),
                            fetch_type='requests',
                            validate_cert=False,
                            force_update=True,
                            save={
                                'first': False,
                                'sp': response.save.get('sp'),
                                'refer_url': response.save.get('refer_url'),
                                'pageNum': post_data['pageNum']}
                        )

                # first time
                else:
                    sp = re.search(u'data-load-more-suggest-params="(.*?)"', response.text)
                    pagTok = re.search(u'data-load-more-first-continuation-token="(.*?)"', response.text)

                    if sp and pagTok:
                        sp = sp.group(0)
                        pagTok = pagTok.group(0)

                        post_data = deepcopy(self.dev_post)
                        post_data['sp'], post_data['pagTok'] = sp, pagTok

                        new_header = deepcopy(self.default_headers)
                        new_header['Referer'] = response.url

                        self.crawl(
                            self.dev_post_url,
                            callback=self.get_comapny,
                            method='POST',
                            data=post_data,
                            headers=new_header,
                            proxy=choice(the_proxy),
                            fetch_type='requests',
                            # proxy=localproxy,
                            validate_cert=False,
                            force_update=True,
                            save={
                                'first': False,
                                'sp': sp,
                                'refer_url': response.url,
                                'pageNum': post_data['pageNum']
                            }
                        )

            return {
                'content': response.text
            }

        # developer not work,use  dev
        elif response.status_code == 404 and u'developer?id=' in response.url and response.save.get('first'):
            self.crawl(
                self.dev_url.format(response.save.get('id')),
                callback=self.get_comapny,
                proxy=choice(the_proxy),
                fetch_type='requests',
                validate_cert=False,
                headers=self.default_headers,
                save={'last': u'', 'first': False}
            )

        else:
            response.raise_for_status()
