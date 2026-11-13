# -*- coding: utf-8 -*-
"""网页版的启动器：解析参数、打印地址、起 Flask。

平时由 main.py 调过来：

    python main.py web-serve
    python main.py web-serve --port 8080
    python main.py web-serve --host 0.0.0.0 --no-browser
"""

import argparse
import threading
import webbrowser

import settings
from app import create_app
from printer import color


def parse_args(argv=None):
    """网页版自己的参数。终端版的参数在 cli.py 里。"""
    parser = argparse.ArgumentParser(
        prog="python main.py web-serve",
        description="%s 网页版" % settings.APP_NAME,
    )
    parser.add_argument("--host", default="127.0.0.1", help="监听地址，默认 %(default)s")
    parser.add_argument("--port", type=int, default=5000, help="端口，默认 %(default)s")
    parser.add_argument("--no-browser", action="store_true", help="不要自动打开浏览器")
    return parser.parse_args(argv)


def run(argv=None):
    """起服务，一直跑到用户按 Ctrl+C。"""
    args = parse_args(argv)
    url = "http://%s:%d" % (args.host, args.port)

    app = create_app()

    line = "=" * 46
    print(color(line, "cyan"))
    print(color("  %s  v%s" % (settings.APP_NAME, settings.VERSION), "blue"))
    print("  打开这个地址：%s" % url)
    print("  按 Ctrl+C 停止服务")
    print(color(line, "cyan"))

    if not args.no_browser:
        # 等一秒再开浏览器，免得服务还没起来页面就报错
        threading.Timer(1.0, webbrowser.open, args=(url,)).start()

    app.run(host=args.host, port=args.port, threaded=True)
    return 0
