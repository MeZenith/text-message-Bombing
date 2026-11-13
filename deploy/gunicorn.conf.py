# -*- coding: utf-8 -*-
"""gunicorn 的配置（Linux 生产用）。

启动方式：
    gunicorn -c deploy/gunicorn.conf.py "app:create_app()"

⚠️ 注意 workers 必须是 1。
任务（进度、日志）都存在内存的字典里，多进程的话前端轮询 GET /api/tasks/<id>
可能打到另一个进程，那边没有这个任务，直接返回 404。
所以这里用「单进程 + 多线程」：一个进程管一份任务表，线程数给足够并发。
"""

bind = "127.0.0.1:5000"  # 只监听本机，外面走 nginx 反代

workers = 1  # 必须 1，原因见上面
threads = 16  # 一个进程里开 16 条线程，够网页轮流询了

timeout = 120  # 发请求有 4 秒超时，单个 HTTP 请求不会太久
graceful_timeout = 30
keepalive = 5

# 日志交给 systemd（journalctl 看），这里打到 stderr 就行
accesslog = "-"
errorlog = "-"
loglevel = "info"

proc_name = "text-message-Bombing"

# 让 gunicorn 别把每个请求的 headers 都记下来，日志干净点
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s %(D)sus'
