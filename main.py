# -*- coding: utf-8 -*-
"""text-message-Bombing —— 主入口。

两种用法，看清楚再敲：

    python main.py                 # 终端版：提示输入手机号，跑完打印统计
    python main.py web-serve       # 网页版：起一个本地服务，浏览器里点点就发

网页版还能带参数：

    python main.py web-serve --port 8080
    python main.py web-serve --host 0.0.0.0
    python main.py web-serve --no-browser

文件分工：
    main.py        就干一件事：看第一个参数是 web-serve 还是别的，分给下面两个
    server.py      网页版启动器（解析端口、开浏览器、起 Flask）
    app.py         Flask 应用，把 /api 接口和 static 页面挂上去
    cli.py         终端版（参数解析、打印、多轮循环）
    task.py        网页版的任务对象 + 后台线程
    sender.py      真正发请求
    stats.py       统计成功失败
    printer.py     终端彩色字、进度条、开场横幅
    utils.py       手机号检查、占位符替换、设备号
    crypto.py      哈希 / 加密 / 编码小工具
    endpoints/     接口清单，一条一个字典
"""

import sys

# 网页版的子命令，写死在这里，方便找
WEB_COMMAND = "web-serve"


def main():
    """看第一个参数决定干什么，返回退出码。"""
    args = sys.argv[1:]

    if args and args[0] == WEB_COMMAND:
        # 把 web-serve 后面的参数原样交给启动器
        import server

        return server.run(args[1:])

    # 其它情况一律当终端版，--help 这些也交给它自己的参数解析
    import cli

    return cli.main(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        from printer import warn

        warn("被你中断了")
        raise SystemExit(130)
