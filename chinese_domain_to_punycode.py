# !/usr/bin/env python
# coding: utf-8
import re


def cdtp(source):
    try:
        return u'http://xn--' + source.replace(u'(', u'').replace(u')', u'').encode(
            'punycode').encode('idna') + u'.xn--vuqs22g.xn--vuq861b/'
    except:
        pass


print cdtp(u'邵阳市赛恩思化学合成科技发展有限公司(长沙分公司)')
