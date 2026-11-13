# -*- coding: utf-8 -*-
"""终端版。默认就是它，直接 python main.py 即可。

    python main.py                     # 会提示输入手机号
    python main.py 13800000000         # 号码直接跟在后面
    python main.py 13800000000 -r 3    # 只跑 3 轮
    python main.py --dry-run           # 只看看会请求哪些接口，不发

想用网页版：python main.py web-serve
"""

import argparse
import sys
import time

import settings
from endpoints import ALL_ENDPOINTS
from endpoints.voice import ENDPOINT as VOICE_ENDPOINT
from printer import fail, note, say, show_logo, warn
from sender import send_all, send_voice
from stats import Stats
from utils import clean_phone


def parse_args(argv=None):
    """读命令行参数。全都有默认值，直接 python cli.py 也能跑。"""
    parser = argparse.ArgumentParser(
        prog="python main.py",
        description="%s %s（终端版）" % (settings.APP_NAME, settings.VERSION),
    )
    parser.add_argument("phone", nargs="?", help="手机号，不填就运行时提示输入")
    parser.add_argument(
        "-r", "--rounds", type=int, default=settings.ROUNDS,
        help="跑几轮，默认 %(default)s",
    )
    parser.add_argument(
        "-w", "--workers", type=int, default=settings.WORKERS,
        help="同时发几条，默认 %(default)s",
    )
    parser.add_argument(
        "-t", "--timeout", type=float, default=settings.TIMEOUT,
        help="单条最多等几秒，默认 %(default)s",
    )
    parser.add_argument(
        "-i", "--interval", type=float, default=0,
        help="两轮之间歇几秒，默认 %(default)s",
    )
    parser.add_argument("-k", "--filter", default="", help="只发名字或网址里带这个字的接口")
    parser.add_argument("-n", "--limit", type=int, default=0, help="最多发前几条，0 表示全部")
    parser.add_argument(
        "--voice-times", type=int, default=settings.VOICE_TIMES,
        help="语音呼叫打几次，默认 %(default)s",
    )
    parser.add_argument(
        "--voice-gap", type=float, default=settings.VOICE_GAP,
        help="语音呼叫每次隔几秒，默认 %(default)s",
    )
    parser.add_argument("--no-voice", action="store_true", help="跳过语音呼叫")
    parser.add_argument("--no-banner", action="store_true", help="不打印开场 LOGO")
    parser.add_argument("--dry-run", action="store_true", help="只列接口，不发请求")
    return parser.parse_args(argv)


def ask_phone():
    """提示用户输入手机号，最多试 3 次。"""
    for _ in range(3):
        text = input("请输入手机号码: ").strip()
        phone = clean_phone(text)
        if phone:
            return phone
        fail("号码不对，要 11 位、1 开头，比如 13800000000")
    return None


def pick_items(keyword, limit):
    """从全部接口里挑一部分出来，方便小范围测试。"""
    items = ALL_ENDPOINTS

    if keyword:
        keyword = keyword.lower()
        picked = []
        for item in items:
            name = str(item.get("name", "")).lower()
            url = str(item.get("url", "")).lower()
            if keyword in name or keyword in url:
                picked.append(item)
        items = picked

    if limit > 0:
        items = items[:limit]

    return items


def show_items(items):
    """--dry-run 时用：把要请求的接口列出来。"""
    note("一共 %d 条接口：" % len(items))
    for index, item in enumerate(items, start=1):
        method = str(item.get("method", "?")).upper()
        name = str(item.get("name", "?"))
        url = str(item.get("url", ""))
        print("  %3d. %-4s %-32s %s" % (index, method, name, url))


def run_rounds(phone, items, args):
    """按轮数循环发送，每轮结束打一次小结，最后返回总统计。"""
    total_stats = Stats("全部任务")

    for round_no in range(1, args.rounds + 1):
        say()
        say("========== 第 %d/%d 轮 ==========" % (round_no, args.rounds), "magenta")

        results = send_all(items, phone, workers=args.workers, timeout=args.timeout)

        round_stats = Stats("第 %d 轮" % round_no)
        round_stats.add_many(results)
        round_stats.show()

        total_stats.add_many(results)

        if round_no < args.rounds and args.interval > 0:
            time.sleep(args.interval)

    return total_stats


def main(argv=None):
    """命令行版从这里开始。"""
    args = parse_args(argv)

    if args.rounds < 1:
        fail("轮数至少要是 1")
        return 2
    if args.workers < 1:
        fail("线程数至少要是 1")
        return 2
    if args.timeout <= 0:
        fail("超时时间要大于 0")
        return 2

    if not args.no_banner:
        show_logo(animated=sys.stdout.isatty())

    items = pick_items(args.filter, args.limit)
    if not items:
        fail("没挑到接口，看看 --filter / --limit 是不是写错了")
        return 2

    if args.dry_run:
        show_items(items)
        return 0

    phone = clean_phone(args.phone) or ask_phone()
    if not phone:
        fail("没拿到有效手机号，退出")
        return 2

    note(
        "目标号码 %s｜接口 %d 条｜%d 轮｜并发 %d｜超时 %s 秒"
        % (phone, len(items), args.rounds, args.workers, args.timeout)
    )

    stats = run_rounds(phone, items, args)

    if not args.no_voice:
        say()
        note("开始语音呼叫：%d 次，每次隔 %s 秒" % (args.voice_times, args.voice_gap))
        voice_results = send_voice(
            VOICE_ENDPOINT, phone, times=args.voice_times, gap=args.voice_gap
        )
        voice_stats = Stats("语音呼叫")
        voice_stats.add_many(voice_results)
        voice_stats.show()
        stats.merge(voice_stats)

    say()
    stats.show()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        warn("被你中断了")
        sys.exit(130)
