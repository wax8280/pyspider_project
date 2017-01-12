# !/usr/bin/env python
# coding: utf-8
import re

def cdtp(source_url):
    result_url = 'http://www.{}.{}'
    chinese_pattern = u'www\.(.+)\.(.+)'
    gen = re.search(chinese_pattern, source_url)
    if gen:
        _ = []
        for i in gen.groups():
            if re.search(u'[\u4e00-\u9fa5]', i):
                _.append(u'xn--' + i.encode('punycode'))
            else:
                _.append(i)

        return result_url.format(_[0], _[1])


print cdtp(u'www.nihao.中国')

