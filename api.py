# -*- coding: utf-8 -*-
"""所有接口（HTTP API）都写在这个文件里。

前端页面就是调这些接口干活的：

    GET  /api/options              拿默认参数、接口总数（页面一打开就调）
    GET  /api/endpoints            接口清单（只给名字/方法/网址，不给 headers）
    POST /api/tasks                新建一个发送任务，body 是参数
    GET  /api/tasks                最近的任务列表
    GET  /api/tasks/<id>           某个任务当前进度（页面每 0.6 秒调一次）
    POST /api/tasks/<id>/stop      停止某个任务
"""

import settings
import task as task_store
from endpoints import ALL_ENDPOINTS
from flask import Blueprint, jsonify, request
from utils import clean_phone

api = Blueprint("api", __name__, url_prefix="/api")

# 参数允许的范围：前端传超了就直接改正，不报错，省得用户困惑
LIMITS = {
    "rounds": (1, 50),
    "workers": (1, 100),
    "timeout": (1, 30),
    "limit": (0, len(ALL_ENDPOINTS)),
    "voice_times": (1, 50),
    "voice_gap": (0, 60),
}


def read_number(data, key, default):
    """从请求里读一个数字，顺便卡在允许范围内。"""
    try:
        value = int(float(data.get(key, default)))
    except (TypeError, ValueError):
        value = default

    low, high = LIMITS[key]
    return max(low, min(high, value))


@api.get("/options")
def get_options():
    """页面打开时先拿这些默认值，把输入框填好。"""
    return jsonify(
        {
            "rounds": settings.ROUNDS,
            "workers": settings.WORKERS,
            "timeout": settings.TIMEOUT,
            "voice_times": settings.VOICE_TIMES,
            "voice_gap": settings.VOICE_GAP,
            "total_endpoints": len(ALL_ENDPOINTS),
        }
    )


@api.get("/endpoints")
def get_endpoints():
    """接口清单。支持 ?filter=关键字 和 ?limit=条数。"""
    keyword = (request.args.get("filter") or "").lower()
    items = ALL_ENDPOINTS

    if keyword:
        picked = []
        for item in items:
            name = str(item.get("name", "")).lower()
            url = str(item.get("url", "")).lower()
            if keyword in name or keyword in url:
                picked.append(item)
        items = picked

    limit = request.args.get("limit", type=int) or 0
    if limit > 0:
        items = items[:limit]

    # 只把名字、方法、网址给前端，请求头和 cookie 没必要暴露
    result = []
    for item in items:
        result.append(
            {
                "name": item.get("name", ""),
                "method": str(item.get("method", "")).upper(),
                "url": item.get("url", ""),
            }
        )

    return jsonify({"total": len(result), "items": result})


@api.post("/tasks")
def start_task():
    """新建任务。前端点"开始发送"就是调它。"""
    data = request.get_json(silent=True) or {}

    phone = clean_phone(data.get("phone"))
    if not phone:
        return jsonify({"error": "手机号不对，要 11 位、1 开头，比如 13800000000"}), 400

    # 先按关键字挑接口，再按条数截断
    keyword = (str(data.get("filter") or "")).strip().lower()
    items = ALL_ENDPOINTS
    if keyword:
        picked = []
        for item in items:
            name = str(item.get("name", "")).lower()
            url = str(item.get("url", "")).lower()
            if keyword in name or keyword in url:
                picked.append(item)
        items = picked

    limit = read_number(data, "limit", 0)
    if limit > 0:
        items = items[:limit]

    if not items:
        return jsonify({"error": "按这个关键字没找到接口，换个词试试"}), 400

    task = task_store.create_task(
        phone=phone,
        items=items,
        rounds=read_number(data, "rounds", settings.ROUNDS),
        workers=read_number(data, "workers", settings.WORKERS),
        timeout=read_number(data, "timeout", settings.TIMEOUT),
        with_voice=bool(data.get("voice", True)),
        voice_times=read_number(data, "voice_times", settings.VOICE_TIMES),
        voice_gap=read_number(data, "voice_gap", settings.VOICE_GAP),
    )

    return jsonify(task.to_dict()), 201


@api.get("/tasks")
def get_tasks():
    """最近的任务，前端刷新页面时可以用它恢复上次的进度。"""
    result = []
    for task in task_store.list_tasks()[:10]:
        data = task.to_dict()
        # 列表里不需要日志和明细，省点流量
        result.append(
            {
                "id": data["id"],
                "phone": data["phone"],
                "status": data["status"],
                "done": data["done"],
                "total": data["total"],
                "success": data["success"],
                "failed": data["failed"],
            }
        )
    return jsonify({"items": result})


@api.get("/tasks/<task_id>")
def get_task(task_id):
    """查任务进度。前端每 0.6 秒调一次，就是靠它刷新页面。"""
    task = task_store.get_task(task_id)
    if task is None:
        return jsonify({"error": "任务不存在，可能是服务重启过"}), 404
    return jsonify(task.to_dict())


@api.post("/tasks/<task_id>/stop")
def stop_task(task_id):
    """停止任务。"""
    task = task_store.get_task(task_id)
    if task is None:
        return jsonify({"error": "任务不存在"}), 404

    task.stop()
    return jsonify({"ok": True, "id": task_id})
