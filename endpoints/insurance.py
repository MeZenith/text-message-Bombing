# -*- coding: utf-8 -*-
"""保险类的预约 / 留资接口。

字段说明跟 miniapp.py 一样，只是这些站点的请求体大多是表单字符串，
还带了一堆抓包下来的 cookie。
"""

ENDPOINTS = [
    {
        "name": "m.zhongmin.cn",
        "method": "POST",
        "url": "https://m.zhongmin.cn/Topic/AddYuyueNew",
        "headers": {
            "Host": "m.zhongmin.cn",
            "Connection": "keep-alive",
            "sec-ch-ua-platform": "\"Android\"",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "__UA__",
            "Accept": "*/*",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Android WebView\";v=\"138\"",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua-mobile": "?1",
            "Origin": "https://m.zhongmin.cn",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": (
                "https://m.zhongmin.cn/benefitGuarantee/Index?&miniprogram=1&isarticle=0&miniphone=&cityid=&"
                "openid=o_-GO4k4GF7wKK1edUGK-e3YKxtI&areaCode="
            ),
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        },
        "data": "name=救赎&phone=__PHONE__&sex=0&type=1306&des=惠民保障预约",
        "cookies": {
            "ASP.NET_SessionId": "xbg1wz02h2ebhydki1uwcpdg",
            "cookieUserName": "cookie0F4D39BF5852DA4D2376B66403A635D9",
            "areaCodeOut": "Code%3D",
            "Hm_lvt_6c7f533b7cc67b6f40de81580fec468e": "1754308837",
            "HMACCOUNT": "28B89CEFEC2F563F",
            "userId": "14808934",
            "tokenZM": "57315b3f242c460cb55c76402220baa0",
            "referrer": "",
            "UVTOKEN": "M7c786431bbe94da89ffa67683c4df869",
            "miniprogram": "1",
            "Hm_lpvt_6c7f533b7cc67b6f40de81580fec468e": "1754373078",
            "areaCode": "HMBGDW04202",
            "isFirstLogin": "true",
        },
    },
    {
        "name": "xiaoyusan.com",
        "method": "POST",
        "url": "https://www.xiaoyusan.com/Phonecrm/createOuterActNoLogin",
        "headers": {
            "Host": "www.xiaoyusan.com",
            "Connection": "keep-alive",
            "sec-ch-ua-platform": "\"Android\"",
            "X-Requested-Sh-Traceid": "936e759279edc705dfdf4c3dab890cec",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Android WebView\";v=\"138\"",
            "sec-ch-ua-mobile": "?1",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "__UA__",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.xiaoyusan.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": (
                "https://www.xiaoyusan.com/shk/wkpage/index/38376d_2023000830.1.html?eva=2023000830&"
                "chn=mlxm-gzh-jbpyl-xxsj-zhengweiqiang-1v1zx-h5-xys-01-cp-008&wkpushstate=1754377971445"
            ),
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        },
        "data": (
            "chn=mlxm-gzh-jbpyl-xxsj-zhengweiqiang-1v1zx-h5-xys-01-cp-008&eva=2023000830&name=救赎&mobile=__PHONE__&"
            "cbs=&biztype=&act_name=cal_insure_no_verify&outer_act_link=https%3A%2F%2Fwww.xiaoyusan.com%2Fshk%2Fw"
            "kpage%2Findex%2F38376d_2023000830.1.html%3Feva%3D2023000830%26chn%3Dmlxm-gzh-jbpyl-xxsj-zhengweiqian"
            "g-1v1zx-h5-xys-01-cp-008%26wkpushstate%3D1754377971445&"
            "remark=%E4%B8%BA%E8%B0%81%E5%AE%9A%E5%88%B6%EF%BC%9A%E8%87%AA%E5%B7%B1%2C%E8%B4%AD%E4%B9%B0%E9%99%A9"
            "%E7%A7%8D%EF%BC%9A%E9%87%8D%E7%96%BE%E9%99%A9"
        ),
        "cookies": {
            "acw_tc": "0a0011e917543779705586941e5a05034d5f35d8fc1bf2cbdaaf1ab34504fe",
            "PHPSESSID": "d593e37a75386f616c013f451ad09d58",
            "touchurl": "http%3A%2F%2Fwww.xiaoyusan.com%2Factivity%2FbasicActActionV2%2FgetActUserInfo",
            "_xys_fd_id": "d593e37a75386f616c013f451ad09d58",
            "_xys_s_id": "xbehat7atj7m0u3ry1f8605fwkqs1qwb",
            "Hm_lvt_8dd2422e78fa31be4e5f5469ebe50589": "1754377971",
            "Hm_lpvt_8dd2422e78fa31be4e5f5469ebe50589": "1754377971",
            "HMACCOUNT": "28B89CEFEC2F563F",
            "_ga": "GA1.2.1558367497.1754377974",
            "_gid": "GA1.2.1201782440.1754377974",
            "_gat_gtag_UA_118701918_1": "1",
            "SERVERID": "0eb4557f6237e94d9e97f8fbc080f699|1754377978|1754377970",
            "SERVERCORSID": "0eb4557f6237e94d9e97f8fbc080f699|1754377978|1754377970",
        },
    },
    {
        "name": "cps.qixin18.com",
        "method": "POST",
        "url": "https://cps.qixin18.com/v3/m/api/common/sendReservatSmsCode?md=0.4350888810127329",
        "headers": {
            "Host": "cps.qixin18.com",
            "Connection": "keep-alive",
            "traceparent": "00-ec6e919fb633d89b0cfe89478947868c-600925b4aada7870-01",
            "sec-ch-ua-platform": "\"Android\"",
            "User-Agent": "__UA__",
            "Accept": "application/json, text/plain, */*",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Android WebView\";v=\"138\"",
            "Content-Type": "application/json;charset=UTF-8",
            "sec-ch-ua-mobile": "?1",
            "Origin": "https://cps.qixin18.com",
            "X-Requested-With": "com.tencent.mm",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": (
                "https://cps.qixin18.com/m/apps/cps/bxn1096837/product/detail?prodId=104994&planId=130301&tenantId=0&"
                "createTime=1737170298565&beidouWxDistinctId=1754393057537-3919538-085c85ad06848e-55739345&"
                "beidouWxLoginId="
            ),
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        },
        "data": {
            "telephone": "__PHONE__",
            "nvcData": (
                "%7B%22a%22%3A%22FFFF000000000176F978%22%2C%22c%22%3A%221754393074418%3A0.11043106819183113%22%2C%22d"
                "%22%3A%22nvc_message_h5%22%2C%22h%22%3A%7B%22key1%22%3A%22code0%22%2C%22nvcCode%22%3A400%2C%22umidTo"
                "ken%22%3A%22T2gAS31uagM2X-E0z2j2JuoQ9YfSR0ti-jqcPAZIthsx8iZBAl1Z7vDTZfx5_2e30Ok%3D%22%7D%2C%22j%22%3"
                "A%7B%22test%22%3A1%7D%2C%22b%22%3A%22140%23j5ToaOeezzPXyQo2FxBQA3SoYtkr1PCOldd96z9Jk1L06PJD5Csanhp61"
                "jGBhxAOoVmS%2FihPGjWXxp1L25stjOCDyzldmtrj7u2yz%2BDQzPgflp1zzXE62m9NBQzxOmHK9pJjzzrb22U3l61x0b2IV2VjU"
                "QDa2DcR0uG8zbzeP183l6TzDDrbnxEl6gfa2Pc3Vtg2zFzB2ws9lUWLz8riE2h%2F8brzHs83K3JjzFzb2LDZlQ5xOPFbciCqlQz"
                "z2nH%2BV31QFQzXHO83l6TzH8rb8Og%2FxF%2Bx2PD3VtCfzxfS2dAWl3MzzDxiVOGl3lbzzyc4Vpg%2FzdrI2osYPfSzMrMiV2E"
                "%2FlMTx2Pp%2BN3lqoF%2B4211WlplJzPKvV2TcxQ4d2P4JhoMTzTbi2U5pl4Qo5fzI2z6HkHmijDapVrMn%2F2I4jearIkM%2BI"
                "XKnqdqAtmQLHluyyuI%2FLigLnFwu90YKzhKsb4MDX2%2Fj3fxaTvyx2GBaAp5hxz5FTZvsc5b9yd3BvpPfvycy8%2BU8kSOYW1P"
                "u0POhXQZtYobTZuDZ6%2FhIWU2ok8qzwNyRoBa7J0%2F5uBUFxw5aUEzMw%2FHintdyKouRJHkIIDm9e6uDyY6hgi%2BmDMY%2BD"
                "xS03%2F6TRMqlrLnIKxrYLShpPGwIbvhA7bssFKsXax2qHT8RFT8QieM55h3b5be%2FYoEHt0XcJzgvBtq5JGRo8DD1lUjpOlxOk"
                "ZU3N78niCXLo8VlzZaxVXRCuOcKqiNLCMG%2F5sd9MOt3ChJC36pNbGoKkxCGNduPxPqZXFyHJSfsebfJICy%2BbT1xqiIJacOtb"
                "d4%2FWF6o2JgslXqz3Dc3Kp1zilUb2d2ZioK5KDnJP5bHcLtXNxRVR%2BrR4Msg8v82no70sAg2O3qjfuqW3LFamluYz47%2BjwW"
                "U82KW5ucAUQtcsIm436iZ3%2F1%2B4Xc%2FvBJ3ngE3%2FtH6SWNjM5k4wKuYLhCgUgmqDB1z3LUcVMDwNYGD0zDSZrdyVY3jraU"
                "a4X4A2hbU0dVLcQm2LCy9OuQtFpV9S0wu6pSgtx8JN41%3D%22%2C%22e%22%3A%22cbFWvt9kexwpfxCybnUZIeRXz45AI-bGe5"
                "8D_qNbcmaHrS9W8frU1RtVpWNk_x6OKmDiaOmCDj54dYR_DJ9RspqEIDdNHNK5HUMU627XqqmfOR8E5TFJv32bOkU5rsK0uL94kY"
                "14W-TIhbX0kuKFAPh88DLPh6d509g_3Yca4XtnK9A4GT4Z9fixZrARvDomK9ichTMCJ4brC9lV3KiLNhZwuR_Njcgb3lv1fLasHE"
                "j3mIXbaXIS8qXt8wPlkyGQqBQtPXt9KBZtGtiogryxFUug5sRl8IKnUhzHY1aq4lbgL_dJz7qe5eBpCK0VEI0X0TZk9CYUEg01YT"
                "uvCMKFMuIknevhmPdD8bHW918-lSpCiNImoKrKVCuZjzOta_aLZ6AvmqZYXV2p-2jwyK3k5-MAVa2XVLqq6mUb2LMtaCGzFnEPsh"
                "o4Dj5ALMo32aVsOoLGymA9GsWPL4xkgVjHZ-Ll5Zvf59cs6ikTIPkaRQ0%22%2C%22i%22%3Atrue%7D"
            ),
        },
        "cookies": {
            "nodejs_sid": "s%3AJe330pDnPvmMafrtsgLGXZubqQg7Plv7.FB9kbFV89DrYQBJkYRb0UkaPNwzEQm5Trgd0yUlseOk",
            "fed-env": "production",
            "_qxc_token_": "eb81b40d-43f9-4bcf-8b57-bd165da4fad7",
            "hz_guest_key": "3x9a97LHUHZ4y3XPekPH_1754097046804_1_1015544_38625430",
            "_bl_uid": "j5mjkd0XtbvkC138scUCkhstU8yy",
            "merakApiSessionId": "ebb083327198781a0976uqPJu53NwsTZ",
            "MERAK_DEVICE_ID": "54826bc105b8826c0935c7ef9cb76101",
            "MERAK_RECALL_ID": "98b083327198781a0b76EQOm7F0i9Itv",
            "MERAK_SESSIONID_ID": "0ab083327198781a0b77ccweQE49Inxl",
            "token": "4de2157f-751a-4fef-9629-56be19d9366c",
            "acw_tc": "ac11000117543930671605244e17564aa24627b1ad4373f6c54dee62ac49a4",
            "beidou_mini_cross_state": (
                "%7B%22_beidouWxDistinctId%22%3A%221754393057537-3919538-085c85ad06848e-55739345%22%2C%22_beidouWxLog"
                "inId%22%3A%22%22%7D"
            ),
            "beidou_jssdk_session_id": "1754393069461-7502498-0eb149ad9e396b8-95476587",
            "beidoudata2015jssdkcross": (
                "%7B%22distinct_id%22%3A%221754393057537-3919538-085c85ad06848e-55739345%22%2C%22first_id%22%3A%22198"
                "6854db025b8-049c104f343d668-622e2a12-430320-1986854db03495%22%2C%22props%22%3A%7B%22%24search_keywor"
                "d%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24lates"
                "t_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%"
                "22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_"
                "referrer%22%3A%22%22%7D%2C%22session_id%22%3A%22%22%2C%22%24page_visit_id%22%3A%221754393057537-3919"
                "538-085c85ad06848e-55739345-1754393069466%22%2C%22%24device_id%22%3A%221986854db025b8-049c104f343d66"
                "8-622e2a12-430320-1986854db03495%22%2C%22sdk_injection%22%3A%22INJECTED%22%2C%22login_id%22%3A%22%22"
                "%2C%22login_Id%22%3A%22%22%7D"
            ),
            "MERAK_ENTER_PAGE_TIME": "1754393069682",
            "tfstk": (
                "g2om8HgG-vC00-sfodqXlxXJRhgMkoZ_UfIT6lFwz7PSD5FxQl-ihj4T3Gkasfc8NrF2llHa_7l_6iE25OugBRWV7GPVabDsBSnT"
                "HIwZZXGhXKgx6tgS9vSxDEZOjoZTbBdpvHBjhlZwz2sbHsNzIJtObSPacurhifEBvHHj3nDCGFxKXld0aRFabrz4UuP7I15q_rzP"
                "z7w_QsyN0LDzN7yN7-rw48ybp5PZ_lJoU7wab5lauLDzNRra_QcPuSN4M0Ri_aAKquQK2-40TxPqUXnzB6et37SOQ4y0otH4ZGSZ"
                "4VxVqnNw46Vs4fqUo0JOSWq7ZR2mmdQQ12eiQJqFpGkogbo380d5X5Szoa7EgnS_93D15Na4F8Vdpza-0R2e7OJkEwW_u8wr2Lvl"
                "5Na4F8VpELb3hry7U0C.."
            ),
        },
    },
    {
        "name": "mobilev2.atomychina.com.cn",
        "method": "POST",
        "url": "https://mobilev2.atomychina.com.cn/api/user/web/login/login-send-sms-code",
        "headers": {
            "Host": "mobilev2.atomychina.com.cn",
            "Connection": "keep-alive",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "Accept": "application/json",
            "x-requested-with": "XMLHttpRequest",
            "design-site-locale": "zh-CN",
            "Accept-Language": "zh-CN",
            "X-HTTP-REQUEST-DOMAIN": "mobilev2.atomychina.com.cn",
            "content-type": "application/json",
            "charset": "utf-8",
            "Referer": "https://servicewechat.com/wx74d705d9fabf5b77/171/page-frame.html",
            "User-Agent": "__UA__",
            "Accept-Encoding": "gzip, deflate, br",
        },
        "data": {"mobile": "__PHONE__", "captcha": "1111", "token": "1111", "prefix": 86},
        "cookies": {
            "acw_tc": "0b6e704217543973526363742e7228ce87cdcab16e6e1ce0c22c775c0bf455",
            "guestId": "f67b8c82-f6f4-4a2d-b857-70223098c12c",
            "guestId.sig": "cf36A-025BEBDTEeSi1ADFHYAHI",
        },
    },
    {
        "name": "wx.hy021.net",
        "method": "POST",
        "url": "https://wx.hy021.net/api/mb1001/guahao",
        "headers": {
            "Host": "wx.hy021.net",
            "Connection": "keep-alive",
            "appid": "1282a884-bde3-11ef-801e-b8cef617a30e",
            "content-type": "application/json",
            "charset": "utf-8",
            "Referer": "https://servicewechat.com/wx7ac8f33f519ebaa2/1/page-frame.html",
            "User-Agent": "__UA__",
            "Accept-Encoding": "gzip, deflate, br",
        },
        "data": {
            "data": {
                "type": 2,
                "name": "救赎",
                "age": "35",
                "phone": "__PHONE__",
                "detail": "脑子不正常好像是脑残了",
                "gender": "男",
                "sex": 1,
                "doctor": "牛玉权",
            },
            "appid": "1282a884-bde3-11ef-801e-b8cef617a30e",
        },
    },
    {
        "name": "blue.planplus.cn",
        "method": "POST",
        "url": "https://blue.planplus.cn/account/api/account/v1/member/sms/sendCode?mobile=__PHONE__",
        "headers": {
            "Host": "blue.planplus.cn",
            "Connection": "keep-alive",
            "x-user-token": (
                "TrpusLsAnnNeyJhbGciOiJIUzUxMiJ9.eyJleHAiOjE3NTQ1Mjk3NzAsInRva2VuIjoie1wiZnJvbVwiOlwicGxhdGZvcm1cIixc"
                "Im9wZW5pZFwiOlwib3lLN3UwQXJMVGYybjRNR2oyc0tJYVBTX0hKd1wiLFwidW5pb25pZFwiOlwib0hlQ2NzLUFwSU05N1V2anc1"
                "a3prY1E1T3N0b1wifSJ9.o1o4upLSYY2tuiNcrJIG2r-F4DoUcw6YOana759BhzLPLmpRFXDrHKOvNPBDhijD1GKvu7vnc1MyL4B"
                "Hk0iEhA"
            ),
            "content-type": "application/json",
            "charset": "utf-8",
            "Referer": "https://servicewechat.com/wxd4c6c416bdab4315/51/page-frame.html",
            "User-Agent": "__UA__",
            "Accept-Encoding": "gzip, deflate, br",
        },
    },
    {
        "name": "shop.hfmsq.com",
        "method": "GET",
        "url": "https://shop.hfmsq.com/prod-api/sendMsg?phoneNumber=__PHONE__",
        "headers": {
            "Host": "shop.hfmsq.com",
            "User-Agent": "__UA__",
            "Referer": "https://servicewechat.com/wx848613725517fc02/2/page-frame.html",
        },
    },
]
