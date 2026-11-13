# -*- coding: utf-8 -*-
"""这个文件放所有"可以随手改"的参数。

想调速度、调轮数、换 User-Agent，都在这里改，不用翻别的文件。
"""

# 项目名字和版本号，页面标题、启动横幅都用它
APP_NAME = "text-message-Bombing"
VERSION = "2.1.0"

# 接口数据里的占位符。发请求之前会被替换成真的手机号 / 随机 UA / 当前时间。
PHONE_FLAG = "__PHONE__"
UA_FLAG = "__UA__"
TIME_FLAG = "__TIMESTAMP__"

# 单条请求最多等几秒。网络慢可以调大，想快就调小。
TIMEOUT = 4

# 同时发多少条。开太大会被站点限流，30 左右比较稳。
WORKERS = 30

# 默认跑几轮（一轮就是把所有接口都打一遍）。
ROUNDS = 5

# 语音呼叫：一共打几次，每次之间隔几秒。
VOICE_TIMES = 10
VOICE_GAP = 5

# 随机挑一个当 User-Agent。
UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36",
]
