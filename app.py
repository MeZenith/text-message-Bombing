# -*- coding: utf-8 -*-
"""Flask 应用：把接口挂上去，再把前端页面放出去。

真正干活的两个地方：
    api.py      所有 /api/... 接口
    static/     前端页面（index.html + style.css + app.js）

部署到服务器时，由 gunicorn（Linux）或 waitress（Windows）调用 create_app()，
不要用 app.run()，那是给本地开发用的。
"""

from flask import Flask, jsonify, send_from_directory

import api
import settings
import task as task_store


def create_app():
    """建一个 Flask 应用。main.py 和部署时的 gunicorn 都会调这个函数。"""
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    app.register_blueprint(api.api)

    @app.get("/")
    def home():
        """打开根路径就直接给前端页面。"""
        return send_from_directory("static", "index.html")

    @app.get("/favicon.ico")
    def favicon():
        """没有图标，返回 204，浏览器就不会一直报 404。"""
        return "", 204

    @app.get("/healthz")
    def healthz():
        """健康检查。nginx、监控、systemd 都用得上。"""
        return jsonify(
            {
                "ok": True,
                "app": settings.APP_NAME,
                "version": settings.VERSION,
                "tasks": len(task_store.list_tasks()),
            }
        )

    return app
