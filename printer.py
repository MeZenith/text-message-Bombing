# -*- coding: utf-8 -*-
"""屏幕上要显示的东西都放这里：彩色字、进度条、开场横幅。

colorama 和 tqdm 是可选依赖：装了更好看，没装程序照样能跑。
"""

import os
import sys
import time

import settings

try:
    import colorama

    colorama.init()  # 让老版 Windows 控制台也能显示颜色
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


# 颜色名 -> 终端用的数字代码
COLORS = {
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "white": 37,
    "muted": 90,  # 灰色，用来写副标题
}


def color(text, name=None, bold=False):
    """给文字加颜色。终端不支持颜色时就原样返回。"""
    if not name or not HAS_COLOR:
        return text
    # 输出重定向到文件时不要颜色，不然文件里全是乱码
    if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
        return text

    code = COLORS.get(name)
    if not code:
        return text
    if bold:
        return "\033[1;%dm%s\033[0m" % (code, text)
    return "\033[%dm%s\033[0m" % (code, text)


def say(text="", name=None):
    """打印一行。"""
    print(color(text, name))


def note(text):
    """普通提示，[ * ] 开头。"""
    say("[*] " + text, "cyan")


def ok(text):
    """做成了什么，[ + ] 开头。"""
    say("[+] " + text, "green")


def warn(text):
    """警告，[ ! ] 开头。"""
    say("[!] " + text, "yellow")


def fail(text):
    """出错，[ - ] 开头。"""
    say("[-] " + text, "red")


def progress(total, title="处理中"):
    """拿一个进度条。

    有 tqdm 就用 tqdm，没有就用下面这个假进度条，保证调用方式一样。
    """
    if tqdm is not None:
        return _TqdmBar(total, title)
    return _SimpleBar(total, title)


class _SimpleBar:
    """没装 tqdm 时的替代品：什么也不画，只记数。"""

    def __init__(self, total, title):
        self.total = total
        self.title = title
        self.now = 0

    def update(self, step=1):
        self.now += step

    def set_postfix(self, text):
        """tqdm 有这个接口，这里用不上，留个空函数防止报错。"""

    def close(self):
        """收尾。"""


class _TqdmBar:
    """tqdm 的简单包装，顺手把长度、单位设好。"""

    def __init__(self, total, title):
        self.bar = tqdm(
            total=total,
            desc=title,
            unit="条",
            ncols=88,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
        )

    def update(self, step=1):
        self.bar.update(step)

    def set_postfix(self, text):
        self.bar.set_postfix_str(text, refresh=False)

    def close(self):
        self.bar.close()


# 开场横幅：一行一个 (颜色, 内容)。想换标题改这里就行。
LOGO_LINES = [
    ("cyan", "=================================================="),
    ("blue", "  %s  v%s" % (settings.APP_NAME, settings.VERSION)),
    ("muted", "  concurrent sms sender"),
    ("cyan", "=================================================="),
]


def show_logo(animated=False):
    """打印开场 LOGO。

    animated=True 时一个字一个字地打出来（打字机效果）。
    输出到文件、或者用户加了 --no-banner 时，直接整块打印。
    """
    if not animated:
        for name, line in LOGO_LINES:
            print(color(line, name))
        return

    for name, line in LOGO_LINES:
        for char in line:
            print(color(char, name), end="", flush=True)
            time.sleep(0.02)
        print()
        time.sleep(0.1)
