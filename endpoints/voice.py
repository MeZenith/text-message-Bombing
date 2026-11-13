# -*- coding: utf-8 -*-
"""语音呼叫接口，只有一条。

它跟普通短信不一样：是打电话过去念验证码，所以单独放一个文件，
程序里也只单独、慢慢地调它。
"""

ENDPOINT = {
    "name": "sdjuliangnet 语音呼叫",
    "method": "POST",
    "url": "https://job.sdjuliangnet.com/mengpinapiv2.php/index/sendvmsv2",
    "headers": {
        "Host": "job.sdjuliangnet.com",
        "Connection": "keep-alive",
        "charset": "utf-8",
        "User-Agent": "mmm",
        "content-type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wx71ca15a0ba7a5d0d/11/page-frame.html",
    },
    # ticket / randstr 会过期：重新抓包后只改这两处即可
    "data": (
        '{"type":1,"tel":"__PHONE__","ticket":"'
        "tr03iCvK4_tx9j01lj2Gmisv-F4Aj3K3gHN3TTvkHU3MF5ttlw_995xyRTDxi7GFtAdNlbIWULh6Ot5FY6KgzLsWvXljJVnnQD71mRJhKQ4FkPlJ_mV5Hk0Gj0bQIryrokNYFXNAjscydkxJtQTadyR12A**"
        '","randstr":"@oHt","sendSource":2,"userToken":null,"loginType":3,'
        '"channel":102,"app_id":7,"oaid":"uniapp","api_city":"","api_ip_city":""}'
    ),
}
