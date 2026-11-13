# -*- coding: utf-8 -*-
"""后面单独补的两个接口。

字段说明跟 miniapp.py 一样。
"""

ENDPOINTS = [
    {
        "name": "customer-apply-diversion.teddymobile.cn",
        "method": "POST",
        "url": "https://customer-apply-diversion.teddymobile.cn/api/v1/auth/sendSms",
        "headers": {
            "host": "customer-apply-diversion.teddymobile.cn",
            "xweb_xhr": "1",
            "user-agent": "__UA__",
            "content-type": "application/json",
            "accept": "*/*",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://servicewechat.com/wxf123c0cb425589de/5/page-frame.html",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "priority": "u=1, i",
        },
        "data": {"phone": "__PHONE__"},
    },
    {
        "name": "yiqilai.net.cn",
        "method": "POST",
        "url": "https://yiqilai.net.cn/authorization/auth/sendValidateMsg",
        "headers": {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Host": "yiqilai.net.cn",
            "PROJECT-CODE": "72014",
            "Referer": "https://servicewechat.com/wxd354b6655f7d129a/10/page-frame.html",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "SunnyNetHTTPClient": "true",
            "User-Agent": "__UA__",
            "xweb_xhr": "1",
        },
        "data": {"phone": "__PHONE__"},
    },
]
