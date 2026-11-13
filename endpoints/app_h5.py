# -*- coding: utf-8 -*-
"""App / H5 端的接口（后来补的 44 条）。

字段说明跟 miniapp.py 一样。
"""

ENDPOINTS = [
    {
        "name": "api.pencilnews.cn",
        "method": "POST",
        "url": "https://api.pencilnews.cn/sms/send",
        "headers": {
            "Host": "api.pencilnews.cn",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "sa-super-property": (
                "{\"manufacturer\":\"APPLE\",\"model\":\"iPhone12,1\",\"wifi\":true,\"screen_height\":\"812.000000\","
                "\"screen_width\":\"375.000000\",\"network_type\":\"\"}"
            ),
            "Accept": "*/*",
            "version": "2.9.9",
            "User-Agent": "PencilNews/2.9.9 (iPhone; iOS 18.7; Scale/2.00)",
            "Accept-Language": "zh-Hans-CN;q=1",
            "Accept-Encoding": "gzip, deflate, br",
        },
        "data": {"phone": "__PHONE__", "sms_type": "reg"},
    },
    {
        "name": "as.hypergryph.com",
        "method": "POST",
        "url": "https://as.hypergryph.com/general/v1/send_phone_code",
        "headers": {
            "Host": "as.hypergryph.com",
            "Accept": "*/*",
            "Sec-Fetch-Site": "same-site",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Fetch-Mode": "cors",
            "Content-Type": "application/json;charset=utf-8",
            "Origin": "https://www.hypergryph.com",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://www.hypergryph.com/",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Cookie": (
                "_ga=GA1.1.595367902.1770209761; _ga_V0ZVS049N5=GS2.1.s1770209760$o1$g1$t1770211278$j60$l0$h0; "
                "HMACCOUNT=49E6075557076A09; Hm_lpvt_24d8cd20e5a3728877d88996f22d3eaf=1770211278; "
                "Hm_lvt_24d8cd20e5a3728877d88996f22d3eaf=1770209760,1770211278"
            ),
        },
        "data": {"phone": "__PHONE__", "type": 2},
    },
    {
        "name": "gfwj168.com",
        "method": "GET",
        "url": "https://www.gfwj168.com/api/v1_1/UCenter/sendYzm?phone=__PHONE__",
        "headers": {
            "Host": "www.gfwj168.com",
            "Connection": "keep-alive",
            "token": "",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wxc8910655f8204472/105/page-frame.html",
        },
    },
    {
        "name": "h5-applets.77ircloud.com",
        "method": "GET",
        "url": (
            "https://h5-applets.77ircloud.com/tmini/authservice/sms-verifyCodes?checkPassPort=false&"
            "mobileOrEmail=__PHONE__&productScene=2&tenantId=3463567&type=6"
        ),
        "headers": {
            "Host": "h5-applets.77ircloud.com",
            "Connection": "keep-alive",
            "x-mini-org-id": "3463567",
            "ot": "3463567,9223090561878065152",
            "unCheckLoginMutex": "true",
            "content-type": "application/json",
            "Authorization": (
                "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIyMDUxMDIzOTA4MDcwODE2Iiwic3ViIjoie1widWlkXCI6MjA1MTAyMzkwODA3MDgxNix"
                "cInVzZXJOYW1lXCI6XCJcIixcInVzZXJUeXBlXCI6MSxcInNcIjpudWxsLFwidGJcIjpudWxsLFwiZGJpZFwiOjM0NjM1Njd9Iiw"
                "iZXhwIjoxNzcwODE2MzI2fQ.71A_cPBcK79uIezeZpzJMoW9ezX4_3lgyRhM4mcA8mg"
            ),
            "X-Open-Id": "o0l5a5BidFmFs5GehTKhqMGmLJSk",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wx00b50e862c9dd46c/53/page-frame.html",
        },
    },
    {
        "name": "oms.gdqyqx.com",
        "method": "POST",
        "url": "https://oms.gdqyqx.com/qyqx-oms-api/app/user/sendAuthCode",
        "headers": {
            "Host": "oms.gdqyqx.com",
            "Connection": "keep-alive",
            "accessToken": "",
            "content-type": "application/json",
            "terminal": "2",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wx317cf609e6eef82d/228/page-frame.html",
        },
        "data": {"type": 1, "userName": "__PHONE__"},
    },
    {
        "name": "mpapi.toybaba.com",
        "method": "POST",
        "url": "https://mpapi.toybaba.com/Code/Send",
        "headers": {
            "Host": "mpapi.toybaba.com",
            "Connection": "keep-alive",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wx8c07a51bbe5663c0/139/page-frame.html",
        },
        "data": {"phone": "__PHONE__", "type": 0, "token": ""},
    },
    {
        "name": "gateway.iskytrip.com",
        "method": "POST",
        "url": "https://gateway.iskytrip.com/api/user/usermanger/getPhoneVerify",
        "headers": {
            "Host": "gateway.iskytrip.com",
            "Connection": "keep-alive",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wx5e3a6a1c50ee7515/437/page-frame.html",
        },
        "data": {
            "header": {
                "appId": "60101",
                "channelSource": "100",
                "clientName": "在机场plus微信小程序",
                "clientVersion": "2.7.2.8",
                "customerData": "",
                "deviceType": "3",
                "timestamp": 1770213729122,
                "token": "",
                "uid": "",
                "deviceId": "980fc4c7-500c-4f65-8b42-fcf616148834",
                "version": "v1.0.0",
                "scene": "",
            },
            "request": "__PHONE__",
        },
    },
    {
        "name": "wj.cong.gsxetc.cn",
        "method": "POST",
        "url": "https://wj.cong.gsxetc.cn/index/common/send_code",
        "headers": {
            "Host": "wj.cong.gsxetc.cn",
            "Connection": "keep-alive",
            "content-type": "application/json",
            "authorization": "",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004433) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wx207c9f0330042ec0/22/page-frame.html",
        },
        "data": {"phone": "__PHONE__"},
    },
    {
        "name": "ride-platform.hellobike.com",
        "method": "POST",
        "url": "https://ride-platform.hellobike.com/api?saas.user.auth.sendCode",
        "headers": {
            "Host": "ride-platform.hellobike.com",
            "Connection": "keep-alive",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wxe6a2c6256e291dc9/22/page-frame.html",
        },
        "data": {
            "riskControlData": {},
            "version": "6.98.0",
            "releaseVersion": "6.98.0",
            "systemCode": "306",
            "appName": "AppHelloMiniBrand",
            "mobileModel": "iPhone 11<iPhone12,1>",
            "weChatVersion": "8.0.68",
            "mobileSystem": "iOS 18.7",
            "SDKVersion": "3.14.1",
            "systemPlatform": "ios",
            "from": "wechat",
            "mobile": "__PHONE__",
            "tenantId": "t_chn_xgddc",
            "source": "0",
            "challenge": "u9SX2n",
            "action": "saas.user.auth.sendCode",
            "h5Version": "6.98.0",
        },
    },
    {
        "name": "rentapi.topshopstv.com",
        "method": "GET",
        "url": (
            "https://rentapi.topshopstv.com/api/smsCode/bindMobileToMember?mobileNumber=__PHONE__&"
            "feiyurent_appid=3"
        ),
        "headers": {
            "Host": "rentapi.topshopstv.com",
            "Connection": "keep-alive",
            "feiyurent-useragent": (
                "feiyurent://5.7.0(iPhone 11<iPhone12,1>;iOS 18.7;zh_CN;ID:3-954a6aa452861b280027efa8b53a0743-3.14.1-"
                "wxapp)"
            ),
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wx3074d9061f89c695/353/page-frame.html",
        },
    },
    {
        "name": "api.chexiaoge.com",
        "method": "POST",
        "url": "https://api.chexiaoge.com/open-api/user/auth/sendLoginVerifyCode",
        "headers": {
            "Host": "api.chexiaoge.com",
            "Connection": "keep-alive",
            "channel": "WeChatApp",
            "systemType": "IOS",
            "content-type": "application/json",
            "version": "V3.2.28",
            "partySource": "WeChatApp",
            "x-Token": "",
            "chege-referer": "packageA/login/login",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004431) NetType/4G Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wxa660e396d4f0a8e9/479/page-frame.html",
        },
        "data": {"mobile": "__PHONE__"},
    },
    {
        "name": "zjappserver.xkw.com",
        "method": "POST",
        "url": "https://zjappserver.xkw.com/app-server/v1/user/sendSmsCode",
        "headers": {
            "Host": "zjappserver.xkw.com",
            "Accept": "*/*",
            "zjapp-check": (
                "1770261701||ios||1AC2A9D5-1767-466D-BB5F-294F84C48D64||zj.app||"
                "04F808DCD640757AEDADFB1AC914084899FD659FAC6FFB5619830032C38CB06C"
            ),
            "zjapp-version": "2.14.0",
            "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
            "zjapp-device-brand": "iPhone",
            "Accept-Language": "zh-Hans-CN;q=1.0",
            "zjapp-system-model": "iPhone 11",
            "zjapp-system-version": "18.7",
            "User-Agent": "ZuJuan/2.14.0 (com.xkw.zujuan; build:3; iOS 18.7.0) Alamofire/5.5.0",
            "zjapp-sub-system": "iOS",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Cookie": "acw_tc=76b20f8a17702616886488842ea2920a301fe3b6f0421660d534e90302ad0a",
        },
        "data": {"templateType": "LOGIN", "phone": "__PHONE__"},
    },
    {
        "name": "api.shentingedu.com",
        "method": "POST",
        "url": "https://api.shentingedu.com/index/authorize/sms_action",
        "headers": {
            "Host": "api.shentingedu.com",
            "system": "1",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Content-Type": "application/json",
            "currentTime": "1773450441838",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/44) uni-app"
            ),
            "Connection": "keep-alive",
            "systemType": "app",
        },
        "data": {"mobile": "__PHONE__"},
    },
    {
        "name": "api.gowithtommy.com",
        "method": "POST",
        "url": "https://api.gowithtommy.com/rest/user/register_by_phone/",
        "headers": {
            "Host": "api.gowithtommy.com",
            "Content-Type": "application/json",
            "Cookie": "sl-session=gSbAc0N+hWk+LukZ4omHPA==",
            "Connection": "keep-alive",
            "If-None-Match": "",
            "Accept": "*/*",
            "User-Agent": "mjttSwift/11.0.8 (com.Tommy.mjtt; build:1; iOS 18.7.0) Alamofire/4.7.3",
            "Accept-Language": "zh-Hans-CN;q=1.0",
            "Accept-Encoding": "gzip;q=1.0, compress;q=0.5",
        },
        "data": {"phone_num": "+86__PHONE__"},
    },
    {
        "name": "hudson-prod.localhome.cn",
        "method": "POST",
        "url": "https://hudson-prod.localhome.cn/user/auth-code/mobile",
        "headers": {
            "Host": "hudson-prod.localhome.cn",
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "APP_PLATFORM": "9",
            "channelId": "34",
            "content-type": "application/json; charset=UTF-8",
            "APP_BRAND": "iPhone",
            "APP_VERSION": "3.17.1",
            "appId": "wx847d6fc0bdcbf6c2",
            "APP_MODEL": "iPhone 11<iPhone12,1>",
            "APP_SOURCE": "1",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004431) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wx847d6fc0bdcbf6c2/110/page-frame.html",
        },
        "data": {"mobile": "__PHONE__", "areaCode": "86"},
    },
    {
        "name": "api.youzijianzhi.com",
        "method": "POST",
        "url": "https://api.youzijianzhi.com/api/v1/sms/code",
        "headers": {
            "Host": "api.youzijianzhi.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
            "Accept": "application/json",
            "User-Agent": "YouZiJianZhi/1.0.3 (com.zimi.YouZiJianZhi; build:10; iOS 18.7.0) Alamofire/5.11.0",
            "Accept-Language": "zh-Hans-CN;q=1.0",
            "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
        },
        "data": "mobile=__PHONE__&platform=1&send_key=LOGIN_CODE",
    },
    {
        "name": "v4.passport.sohu.com",
        "method": "GET",
        "url": (
            "https://v4.passport.sohu.com/i/smcode/mobile/v2/signin?captchaType=signin&mobile=__PHONE__&way=0&"
            "pagetoken=1773450441838&appid=116006&callback=passport4014_cb1773450441836&_=1773450441839"
        ),
        "headers": {
            "Host": "v4.passport.sohu.com",
            "Sec-Fetch-Dest": "script",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Version/18.7 Mobile/15E148 Safari/604.1"
            ),
            "Accept": "*/*",
            "Referer": (
                "https://m.sohu.com/login/normal?origin=1&r=https%3A%2F%2Fm.sohu.com%2F%3Fpvid%3D000115_3w_index%26ju"
                "mp%3Dfront&type=1"
            ),
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "no-cors",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Priority": "u=1, i",
            "Accept-Encoding": "gzip, deflate, br",
            "Cookie": (
                "t=1773450441836; vt_smwp_home=7; _dfp=IMe4nZZocUv2P+N+IHIjGcx681os1wyUSs9SDcR8yF4=; "
                "cld=20260205194215; clt=1773450441; reqtype=h5; SUV=1773450439836odinRzq0; "
                "gidinf=x09998010101193cceccef05400022fdbdcaa31c3330"
            ),
            "Connection": "keep-alive",
        },
    },
    {
        "name": "pai.yihaopingji.com",
        "method": "GET",
        "url": "https://pai.yihaopingji.com/index.php?act=index&op=getauthcode&mobile=__PHONE__",
        "headers": {
            "Host": "pai.yihaopingji.com",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Site": "same-origin",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Fetch-Mode": "cors",
            "Accept": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004431) NetType/4G Language/zh_CN"
            ),
            "Connection": "keep-alive",
            "Referer": "https://pai.yihaopingji.com/index.php?act=my&op=editinfo&type=mobile",
            "Cookie": "user_id=812775; PHPSESSID=o8p4fm7t5lp8v9nerfsuaaa1s6",
            "Sec-Fetch-Dest": "empty",
        },
    },
    {
        "name": "cms.sctvcloud.com:37443",
        "method": "POST",
        "url": "https://cms.sctvcloud.com:37443/api/oauth/client/anno/authcode",
        "headers": {
            "Host": "cms.sctvcloud.com:37443",
            "Authorization": "Basic c2N0dl91aTpzY3R2X3VpX3NlY3JldA==",
            "Accept": "*/*",
            "timestamp": "1773450441839",
            "appVersion": "7.2.0",
            "Accept-Encoding": "gzip, deflate, br",
            "tenant": "YzA3MDA=",
            "Accept-Language": "zh-Hans-CN;q=1",
            "Content-Type": "application/json",
            "User-Agent": "SCDistrict/7.2.0 (iPhone; iOS 18.7; Scale/2.00)",
            "Connection": "keep-alive",
        },
        "data": {"phone": "__PHONE__", "authCodeType": "register"},
    },
    {
        "name": "id.getkwai.com",
        "method": "POST",
        "url": "https://id.getkwai.com/pass/m2u/sms/code",
        "headers": {
            "Host": "id.getkwai.com",
            "Content-Type": "application/json",
            "Cookie": (
                "appver=4.72.0; did=IOS_39B1A8E4-C713-468C-AE12-4B55FDA4B537; idfa=; kpf=IPHONE; kpn=M2U; "
                "language=zh-CN; m2u.api.visitor_st=; m2u.api_st=; mod=iPhone12,"
                "1; net=4g; passToken=; sys=iOS_18.7; userId="
            ),
            "Connection": "keep-alive",
            "Accept": "*/*",
            "User-Agent": "1tianCam/4.72.0 (iPhone; iOS 18.7; Scale/2.00)",
            "Accept-Language": "zh-Hans-CN;q=1",
            "Accept-Encoding": "gzip, deflate, br",
        },
        "data": {"phone": "__PHONE__", "countryCode": "+86", "type": 400},
    },
    {
        "name": "starrypro.lastsurvivor.cn",
        "method": "POST",
        "url": "https://starrypro.lastsurvivor.cn/starry/fetchVerifyCode",
        "headers": {
            "Host": "starrypro.lastsurvivor.cn",
            "version": "ios|2.11.14|477",
            "Accept": "*/*",
            "channel": "iOS",
            "userid": "",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "token": "",
            "Content-Type": "application/x-www-form-urlencoded",
            "deviceid": "8A3DBB5F-4752-44B5-92A5-F8477922031A",
            "osmodel": "iPhone 11",
            "oaid": "",
            "Content-Length": "43",
            "User-Agent": "iPhone12,1(iOS/18.7) WeexGroup(",
            "distinctid": "34C2DC4D-01DF-46D9-9EF4-95FE199CC826_2",
            "osversion": "18.7",
            "Connection": "keep-alive",
        },
        "data": "data=%7B%22mobile%22%3A%22__PHONE__%22%7D",
    },
    {
        "name": "ai.growingth.com",
        "method": "POST",
        "url": "https://ai.growingth.com/rich/user/send-sms",
        "headers": {
            "Host": "ai.growingth.com",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "API-Version": "1",
            "Accept": "*/*",
            "User-Agent": "wang luo jian zhi/1.1 (iPhone; iOS 18.7; Scale/2.00)",
            "Accept-Language": "zh-Hans-CN;q=1",
            "Accept-Encoding": "gzip, deflate, br",
        },
        "data": {"appid": "videoCut02", "appVersion": "1", "phone": "__PHONE__"},
    },
    {
        "name": "ku.zrb.net",
        "method": "POST",
        "url": "https://ku.zrb.net/api/Jzk/JzkSendSmsNew",
        "headers": {
            "Host": "ku.zrb.net",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Accept": "*/*",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/44) uni-app"
            ),
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
        },
        "data": {
            "mobile": "__PHONE__",
            "account": "",
            "password": "",
            "version": 39,
            "channeltype": 120,
        },
    },
    {
        "name": "h3cservice.h3c.com",
        "method": "POST",
        "url": "https://h3cservice.h3c.com/Sms/SendCode",
        "headers": {
            "Host": "h3cservice.h3c.com",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Site": "same-origin",
            "Accept-Language": "zh-cn",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Fetch-Mode": "cors",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://h3cservice.h3c.com",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148"
            ),
            "Referer": "https://h3cservice.h3c.com/",
            "Cookie": "ASP.NET_SessionId=2r5oyngghmdzudflqq5r3tu3",
            "Sec-Fetch-Dest": "empty",
            "Connection": "keep-alive",
        },
        "data": "PhoneNumber=__PHONE__",
    },
    {
        "name": "mall.xyhljls.com",
        "method": "GET",
        "url": (
            "https://mall.xyhljls.com/api/member/msg_send?mobile=__PHONE__&type=check&app_key=1&"
            "request_id=1773450441839&MALL-SIGN=de%2BL4WZHbhDe%2FREgaPfK2us4mc7nBbn83IPtGyjIXWBwGQ20XQHI2NrYt%2BZ"
            "w2Ys3jLLe7YnZLkRDkXSdiJP9o2VTAo4JD%2B33CJWTOOZGxwOG70j5smUSvyDj2tGAo6%2BD"
        ),
        "headers": {
            "Host": "mall.xyhljls.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Applet-Authorization": "L1E/iDMNQJsThT1CE8Jr1g==",
            "Cookie": "SESSION=MmM5OGUzMWQtNzgyNC00NmFmLWEyMGUtMGY2NTNlOWQ4ZDhi",
            "Accept": "*/*",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/44) uni-app"
            ),
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        },
    },
    {
        "name": "api.jihuanshe.com",
        "method": "POST",
        "url": "https://api.jihuanshe.com/api/market/auth/send-sms",
        "headers": {
            "Host": "api.jihuanshe.com",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Connection": "keep-alive",
            "x-device-id": "3CB80B8B-579E-49DF-9090-EE9299DE31D7",
            "Accept": "*/*",
            "User-Agent": "jihuanshe_ios/3.35.0 (com.jihuanshe.app; build:75; iOS 18.7.0) Alamofire/5.4.4 iphone",
            "Accept-Language": "zh-Hans-CN;q=1.0",
            "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
        },
        "data": "check_phone_exists=0&phone=__PHONE__&region_code=%2B86",
    },
    {
        "name": "hsjapi.hulian120.com",
        "method": "POST",
        "url": "https://hsjapi.hulian120.com/userService/api/app/user/nurse/login/loginPhoneSendCode",
        "headers": {
            "Host": "hsjapi.hulian120.com",
            "businessSource": "1",
            "User-Env": "MiniProgram",
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Sec-Fetch-Site": "same-site",
            "requestId": "1773450441839",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Fetch-Mode": "cors",
            "terminalPlatform": "2",
            "Origin": "https://ai.hulian120.com",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004431) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://ai.hulian120.com/",
            "activity": "3248923489234",
            "loginType": "WEB_AI",
            "Sec-Fetch-Dest": "empty",
            "Connection": "keep-alive",
        },
        "data": {"loginType": "1", "phone": "__PHONE__"},
    },
    {
        "name": "api.chezhubei.com",
        "method": "POST",
        "url": "https://api.chezhubei.com/app/api/app/public/sendSmsCode",
        "headers": {
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 10; YAL-AL10 Build/HUAWEIYAL-AL10; wv) AppleWebKit/537.36 (KHTML,"
                " like Gecko) Version/4.0 Chrome/114.0.5735.196 Mobile Safari/537.36 uni-app Html5Plus/1.0 "
                "(Immersed/40.666668)"
            ),
            "Connection": "Keep-Alive",
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "Authorization": "",
            "X-Channel": "huawei",
            "X-Platform": "APP-ANDROID",
            "X-Version": "czb-app/1.0.13",
            "X-Oaid": "5a00c3cd-f243-4ef1-9cac-37e4311e83a1",
            "Content-Type": "application/json; charset=utf-8",
        },
        "data": {"phone": "__PHONE__"},
    },
    {
        "name": "job.sdjuliangnet.com",
        "method": "POST",
        "url": "https://job.sdjuliangnet.com/chaoapi.php/index/sendsms",
        "headers": {
            "Host": "job.sdjuliangnet.com",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Accept": "*/*",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/44) uni-app"
            ),
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
        },
        "data": {
            "type": 1,
            "tel": "__PHONE__",
            "app_id": 4,
            "channel": 55,
            "oaid": "uniapp",
            "userToken": "",
            "api_city": "广州",
            "api_ip_city": "广州",
            "loginType": 4,
            "api_ip": "120.235.13.255",
            "api_ua": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/44) uni-app"
            ),
            "idfa": "",
            "version": "130",
        },
    },
    {
        "name": "new-retail-weixin-gateway-prod.diwangxu.com",
        "method": "POST",
        "url": "https://new-retail-weixin-gateway-prod.diwangxu.com/sms/sendVerifyCode",
        "headers": {
            "Host": "new-retail-weixin-gateway-prod.diwangxu.com",
            "Connection": "keep-alive",
            "callSource": "https://new-retail-h5-prod.diwangxu.com",
            "Appkey": "APP",
            "sessionGenerateId": "",
            "content-type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004433) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wxb7250975c223d5b8/40/page-frame.html",
        },
        "data": {"stringParam": "+86__PHONE__"},
    },
    {
        "name": "jsyapi.evermecon.com",
        "method": "POST",
        "url": "https://jsyapi.evermecon.com/timelyapi/timelyvoice/auth/sendAuthCode",
        "headers": {
            "Host": "jsyapi.evermecon.com",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Connection": "keep-alive",
            "Accept": "*/*",
            "X-Device": (
                "eyJjb3JlX3ZlcnNpb24iOiIyIiwiZGV2aWNlX25hbWUiOiJpUGhvbmUgMTEiLCJzb2Z0X3ZlcnNpb24iOiIyLjMiLCJzeXN0ZW1f"
                "dmVyc2lvbiI6ImlvczE4LjcifQ=="
            ),
            "apiInfo": (
                "{\"osInfo\":\"18.7\",\"brand\":\"apple\",\"buildVersion\":\"5\",\"version\":\"2.3\",\"appKey\":\"1\",\"plat\":\"ios\","
                "\"model\":\"iPhone 11\",\"appId\":\"1\",\"channel\":\"100\"}"
            ),
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "User-Agent": "TimelyRemind/2 CFNetwork/3826.600.41 Darwin/24.6.0",
        },
        "data": "mobile=__PHONE__&type=1",
    },
    {
        "name": "ly.shandongtowngas.com.cn:8015",
        "method": "POST",
        "url": (
            "http://ly.shandongtowngas.com.cn:8015/BleDevicePayPlatform/app/jihua/getAuthCode.do?authCodeType=0&"
            "mobile=__PHONE__&version=1.4.6&timestamp=1773450441839"
        ),
        "headers": {
            "Host": "ly.shandongtowngas.com.cn:8015",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Proxy-Connection": "keep-alive",
            "Accept": "*/*",
            "User-Agent": "%E8%93%9D%E7%89%99%E5%85%85%E5%80%BC%E6%98%93/1 CFNetwork/3826.600.41 Darwin/24.6.0",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate",
        },
        "data": {"mobile": "__PHONE__", "authCodeType": "0"},
    },
    {
        "name": "mfapi.greenlr.com",
        "method": "POST",
        "url": "https://mfapi.greenlr.com/sendSms/getCheckCode",
        "headers": {
            "Host": "mfapi.greenlr.com",
            "Accept": "*/*",
            "appSecret": "akffas7239hrewoqriewqr",
            "source": "ios",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-Hans-CN;q=1",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "memberCash/9.10 (iPhone; iOS 18.7; Scale/2.00)",
            "appKey": "roiueqo9023jofjlajfdj",
            "Connection": "keep-alive",
            "sign": "DE8B45B8203F6A08391147A72BB45654",
        },
        "data": "phone=__PHONE__&type=1",
    },
    {
        "name": "m.94lives.com",
        "method": "POST",
        "url": "https://m.94lives.com/api/auth/sendPhoneCode",
        "headers": {
            "Host": "m.94lives.com",
            "deviceNumber": "BB976B03-70D7-4602-BD6F-2E8EF576A7B8",
            "Content-Type": "application/json;charset=UTF-8",
            "Authorization": "",
            "Accept": "*/*",
            "browserType": "iOS",
            "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
            "iOSVersion": "1.1.9",
            "cid": "",
            "Accept-Language": "zh-Hans-CN;q=1.0",
            "clientType": "iOS",
            "language": "0",
            "User-Agent": "94LIVES/1.1.9 (com.ninetyfour.cn; build:60; iOS 18.7.0) Alamofire/5.10.2",
            "currency": "23",
            "Cookie": "JSESSIONID=6AF60A037165361453056A2AC292ADBB",
            "qwer": (
                "eyJhZGRyZXNzIjoi5bm/5bee5biCLCDlub/kuJznnIEsIOS4reWbvSIsImxvbmdpdHVkZSI6MTEzLjQ3NzkwNDgwODkzMzU3LCJs"
                "YXRpdHVkZSI6MjMuNDMzNjIzMjI2MDMzNTk2fQ=="
            ),
            "Connection": "keep-alive",
        },
        "data": {
            "captchaVerification": "",
            "countryCode": "CN",
            "phone": "__PHONE__",
            "type": "2",
            "areaCode": "86",
        },
    },
    {
        "name": "app.bac365.com",
        "method": "POST",
        "url": "https://app.bac365.com/camel_wechat_mini_oil_server/sendVerifyMessage",
        "headers": {
            "Host": "app.bac365.com",
            "channel": "app",
            "Content-Type": "application/json",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Accept": "*/*",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/44) uni-app"
            ),
            "timestamp": "1773450441",
            "Authorization": "Bearer ",
            "Content-Length": "39",
        },
        "data": {"phone": "__PHONE__", "channel": "app"},
    },
    {
        "name": "api.mall.leyifan.cn",
        "method": "GET",
        "url": "https://api.mall.leyifan.cn/api/front/phone/sendSmsCode?phone=__PHONE__",
        "headers": {
            "Host": "api.mall.leyifan.cn",
            "system": "ios",
            "Accept": "*/*",
            "App-Version": "30822",
            "Clientid": "37a3cffb-f033-4267-b16d-e21fbbb759593",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "platform": "app",
            "Content-Type": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/44) uni-app"
            ),
            "lang": "chs",
            "Appplatform": "ios_cn",
            "Origin-channel": "ios_cn",
            "Cookie": "https_waf_cookie=d8f6cb86-1ef5-4babf2e02f144500a8071f58dc7448bb82cb",
            "UseDomain": "leyifan",
            "Connection": "keep-alive",
        },
    },
    {
        "name": "baojianstore.com",
        "method": "GET",
        "url": (
            "https://www.baojianstore.com/Appshop/AppShopHandler.ashx?action=VerficationPhoneOrEmail&"
            "value=__PHONE__"
        ),
        "headers": {
            "Host": "www.baojianstore.com",
            "Accept": "*/*",
            "Origin": "https://h5.baojian.com",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148"
            ),
            "Referer": "https://h5.baojian.com/",
            "Sec-Fetch-Dest": "empty",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        },
    },
    {
        "name": "d2m0k739byzwun.cloudfront.net",
        "method": "POST",
        "url": "https://d2m0k739byzwun.cloudfront.net/api/app/notification/captcha",
        "headers": {
            "User-Agent": (
                "DevID%3Dlld5a00c3cd-f243-4ef1-9cac-37e4311e83a1%3BDevType%3DHWYAL%3A29%3Aid%3DHUAWEIYAL-AL10%3BSysTy"
                "pe%3Dandroid%3BVer%3D1.3.1%3BBuildID%3Ddark.jaYec.msLgF%3BMac%3DD2%3ADF%3AB6%3AA2%3AB2%3A97%3BGlobal"
                "DevID%3Dnull"
            ),
            "Accept-Encoding": "*",
            "Content-Type": "application/json",
            "x-api-key": (
                "timestamp=1773450441;sign=8dd5664c04fb929be7ec5f69a3319af8a9c6adc8;nonce=61317618-95bb-45b2-9dc7-b1a"
                "c7135cca3"
            ),
            "device": "android",
            "authorization": (
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aW1lc3RhbXAiOjE3NzAyODQ4MzMwNzc5OTQ1MDAsInR5cGUiOjAsInVpZCI"
                "6NTQ2ODgyNjN9.jw5QCTHSA3X_1WOAT8o1lHiyILJDuUUP1tuYp8cDjHE"
            ),
            "api_version": "1.0.0",
            "content-type": "application/json;charset=UTF-8",
        },
        "data": {"type": 1, "mobile": "+86__PHONE__"},
    },
    {
        "name": "shanxiaobai.com",
        "method": "POST",
        "url": "https://www.shanxiaobai.com/app.html?is_api=1&act=sms",
        "headers": {
            "Host": "www.shanxiaobai.com",
            "X-DEVICE-OS-PRODUCT": "iPhone12,1",
            "X-Api-Ver": "36",
            "Cookie": "PHPSESSID=uvsicg4sm7ta7quuu9i4rm2l81",
            "User-Agent": "WhiteGoods/3.3.0 (iPhone; iOS 18.7; Scale/2.00)",
            "X-App-Name": "com.uping.white",
            "X-DEVICE-OS-VER": "18.7",
            "X-DEVICE-TYPE": "ios",
            "X-DEVICE-TOKEN": "612cd2033713ef86e7c19ab1a3b48e6d96f836265f8f1e8671c70282396485b4",
            "X-DEVICE-OS": "IOS",
            "X-App-Ver": "3.3.0",
            "Accept-Language": "zh-Hans-CN;q=1",
            "IDFV": "889E8142-68CF-42C3-875C-6F2B8386CD12",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-TOKEN": "",
            "Accept-Encoding": "gzip, deflate, br",
            "IDFA": "",
            "Connection": "keep-alive",
        },
        "data": "mobile=__PHONE__&type=login",
    },
    {
        "name": "api.daxianghome.com",
        "method": "GET",
        "url": "https://api.daxianghome.com/user/login?mobile=__PHONE__",
        "headers": {
            "Host": "api.daxianghome.com",
            "Content-Type": "application/json",
            "Accept": "*/*",
            "User-Agent": "DaXiang/1.7.1 (iPhone; iOS 18.7; Scale/2.00)",
            "Accept-Language": "zh-Hans-CN;q=1",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        },
    },
    {
        "name": "app.tuozhe8.com",
        "method": "POST",
        "url": "https://app.tuozhe8.com/v2/Login/alidayu_sms",
        "headers": {
            "Host": "app.tuozhe8.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
            "Accept": "*/*",
            "User-Agent": "TZDesignApp/202404131530 (iPhone; iOS 18.7; Scale/2.00)",
            "Accept-Language": "zh-Hans-CN;q=1",
            "Accept-Encoding": "gzip, deflate, br",
        },
        "data": "mobile=__PHONE__&validate=&version=3.5.1",
    },
    {
        "name": "agent.jieyoucloud.com",
        "method": "POST",
        "url": "https://agent.jieyoucloud.com/api/v1/sendSmsVerificationCode?phoneNumber=__PHONE__",
        "headers": {
            "Host": "agent.jieyoucloud.com",
            "Connection": "keep-alive",
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer ",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004433) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wx979378000669bc89/57/page-frame.html",
        },
    },
    {
        "name": "api.zhiguohulian.com",
        "method": "GET",
        "url": (
            "https://api.zhiguohulian.com/webapp/v1/user/code?phone=__PHONE__&package=xiaozhi&thirdparty=xiaozhi"
        ),
        "headers": {
            "Host": "api.zhiguohulian.com",
            "Connection": "keep-alive",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004432) NetType/4G Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wx96983c5aa4a177cb/20/page-frame.html",
        },
    },
    {
        "name": "tg-admin-api.916sy.com",
        "method": "POST",
        "url": "https://tg-admin-api.916sy.com/api/auth/register_get_phone",
        "headers": {
            "Host": "tg-admin-api.916sy.com",
            "Connection": "keep-alive",
            "From-Type": "wxMiNi",
            "content-type": "application/x-www-form-urlencoded",
            "Access-Token": "",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004433) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wxa46b3fcee3827fcb/1/page-frame.html",
        },
        "data": "phone=__PHONE__",
    },
]
