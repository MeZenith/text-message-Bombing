# -*- coding: utf-8 -*-
"""真正往外发请求的地方。

一共三个函数：
    build_request()  把一条接口配置整理成能直接发的请求
    send_one()       发一条，成功失败都会返回一个字典，不会抛异常
    send_all()       一堆接口一起发，带进度条
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

import settings
from printer import progress
from utils import fill_flags, random_ua


def build_request(item, phone):
    """把接口字典里的占位符换成真值，拼成发请求要用的参数。

    返回一个字典，里面是：
        name      接口名字，日志用
        method    GET / POST / PUT
        url       把 __PHONE__ 换成手机号之后的地址
        headers   把 __UA__ / __TIMESTAMP__ 替换过的请求头
        cookies   需要就带
        json_body 请求体是字典时放这里（用 json= 发）
        data_body 请求体是字符串时放这里（用 data= 原样发）
    """
    user_agent = random_ua()
    timestamp = str(int(time.time()))

    # 整个接口配置（url、headers、data 全在里面）递归替换一遍
    data = fill_flags(item, phone, user_agent, timestamp)

    request = {
        "name": data.get("name") or data.get("url", ""),
        "method": data["method"].upper(),
        "url": data["url"],
        "headers": data.get("headers") or {},
        "cookies": data.get("cookies"),
        "json_body": None,
        "data_body": None,
    }

    # 请求体有两种写法，看数据里是字典还是字符串
    body = data.get("data")
    if isinstance(body, dict):
        request["json_body"] = body
    elif isinstance(body, str):
        request["data_body"] = body

    return request


def send_one(item, phone, timeout=settings.TIMEOUT):
    """发一条接口。

    返回：
        name    接口名字
        ok      True 表示请求发出去了（不看对方返回什么内容）
        status  HTTP 状态码
        error   出错时的原因
        cost    花了多少秒
    """
    result = {
        "name": item.get("name", "?"),
        "ok": False,
        "status": None,
        "error": None,
        "cost": 0.0,
    }

    # 第一步：整理请求。数据写错也要能继续跑，所以这里也要 try
    try:
        request = build_request(item, phone)
    except Exception as exc:
        result["error"] = "接口配置有问题：%s" % exc
        return result

    result["name"] = request["name"]

    # 第二步：组装 requests 的参数，没有的就别传，省得它乱猜
    params = {"headers": request["headers"], "timeout": timeout}
    if request["cookies"]:
        params["cookies"] = request["cookies"]
    if request["json_body"] is not None:
        params["json"] = request["json_body"]
    elif request["data_body"] is not None:
        params["data"] = request["data_body"]

    # 第三步：发。超时、连不上、域名解析失败都算失败，但不影响别的接口
    start = time.time()
    try:
        response = requests.request(request["method"], request["url"], **params)
    except Exception as exc:
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
        result["cost"] = time.time() - start
        return result

    result["ok"] = True
    result["status"] = response.status_code
    result["cost"] = time.time() - start
    return result


def send_all(
    items,
    phone,
    workers=settings.WORKERS,
    timeout=settings.TIMEOUT,
    on_result=None,
    stop_flag=None,
    show_bar=True,
):
    """把一批接口并发发完，返回结果列表（顺序不保证，跟完成时间有关）。

    几个可选参数：
        on_result  每发完一条就调一下，网页版用它实时更新进度
        stop_flag  一个 threading.Event，被 set 了就不再继续发（网页上点"停止"用）
        show_bar   True 会在控制台画进度条，网页版不需要，传 False
    """
    results = []
    if not items:
        return results

    bar = progress(len(items), "发送中") if show_bar else None
    success = 0

    # 线程池：每个接口丢一个任务进去，谁先回来先处理谁
    with ThreadPoolExecutor(max_workers=workers) as pool:
        tasks = []
        for item in items:
            tasks.append(pool.submit(send_one, item, phone, timeout))

        for task in as_completed(tasks):
            # 点过"停止"就不用管剩下的了，已经提交的会自己跑完
            if stop_flag is not None and stop_flag.is_set():
                break

            result = task.result()
            results.append(result)
            if result["ok"]:
                success += 1

            if bar is not None:
                bar.update(1)
                bar.set_postfix("成功 %d / 已发 %d" % (success, len(results)))

            if on_result is not None:
                on_result(result)

    if bar is not None:
        bar.close()
    return results


def send_voice(
    item,
    phone,
    times=settings.VOICE_TIMES,
    gap=settings.VOICE_GAP,
    on_result=None,
    stop_flag=None,
    show_bar=True,
):
    """语音接口：一次一次慢慢打，每次中间隔一会儿。

    这个接口如果并发，很容易被对方拦，所以单独一个函数、串行发。
    """
    results = []
    bar = progress(times, "语音呼叫") if show_bar else None

    for index in range(times):
        if stop_flag is not None and stop_flag.is_set():
            break

        result = send_one(item, phone)
        results.append(result)

        if bar is not None:
            bar.update(1)
        if on_result is not None:
            on_result(result)

        if index < times - 1:  # 最后一次不用再等了
            time.sleep(gap)

    if bar is not None:
        bar.close()
    return results
