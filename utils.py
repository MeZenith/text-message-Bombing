# -*- coding: utf-8 -*-
"""零碎的小工具：检查手机号、替换占位符、读写设备号。"""

import os
import random
import re
import uuid

import settings


def clean_phone(text):
    """把用户输入整理成 11 位手机号，不合格返回 None。

    能容忍这些写法：空格、横杠、+86 开头、138-0000-0000。
    """
    digits = re.sub(r"\D", "", text or "")  # 只留数字

    # +8613800000000 这种，去掉前面的 86
    if len(digits) == 13 and digits.startswith("86"):
        digits = digits[2:]

    if re.match(r"^1[3-9]\d{9}$", digits):
        return digits
    return None


def random_ua():
    """从 settings.UA_LIST 里随机拿一个。"""
    return random.choice(settings.UA_LIST)


def fill_flags(value, phone, user_agent, timestamp):
    """把接口数据里的占位符换成真实值。

    数据可能是字典、列表，里面还套着字典，所以要一层层往里走。
    返回的是新对象，不会改掉原来的接口清单。
    """
    if isinstance(value, str):
        value = value.replace(settings.PHONE_FLAG, phone)
        value = value.replace(settings.UA_FLAG, user_agent)
        value = value.replace(settings.TIME_FLAG, timestamp)
        return value

    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            new_key = fill_flags(key, phone, user_agent, timestamp)
            result[new_key] = fill_flags(item, phone, user_agent, timestamp)
        return result

    if isinstance(value, list):
        result = []
        for item in value:
            result.append(fill_flags(item, phone, user_agent, timestamp))
        return result

    return value


def load_device_id(path=".imei"):
    """读设备号。文件不存在就生成一个（UUID）并存起来，下次接着用。"""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            device_id = file.read().strip()
        if device_id:
            return device_id

    device_id = str(uuid.uuid1())
    with open(path, "w", encoding="utf-8") as file:
        file.write(device_id)
    return device_id
