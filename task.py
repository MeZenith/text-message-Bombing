# -*- coding: utf-8 -*-
"""任务管理：一个"任务"就是"给某个号码把所有接口打 N 轮"。

网页上点"开始发送"就会建一个 Task，它在后台线程里跑，
网页每隔半秒来问一次进度，这样页面不用一直等着。

任务存在内存里（TASKS 这个字典），所以服务一重启，历史任务就没了，
这对我们够用，不需要数据库。
"""

import threading
import time
import uuid

from printer import fail as print_fail
from sender import send_all, send_voice
from stats import Stats

# 日志和明细各留多少条，太多会把网页撑爆
MAX_LOGS = 120
MAX_RECENT = 40

# 内存里最多留几个任务，多了把最老的删掉
MAX_TASKS = 30

# 任务状态，网页直接显示这几个字
STATUS_WAITING = "等待中"
STATUS_RUNNING = "发送中"
STATUS_STOPPED = "已停止"
STATUS_DONE = "已完成"
STATUS_ERROR = "出错了"


def mask_phone(phone):
    """手机号打码再给网页，免得截图时把号码漏出去。"""
    if len(phone) != 11:
        return phone
    return phone[:3] + "****" + phone[-4:]


class Task:
    """一个发送任务。所有字段都简单直白，网页把它转成 JSON 就能显示。"""

    def __init__(self, phone, items, rounds, workers, timeout, with_voice, voice_times, voice_gap):
        self.id = uuid.uuid4().hex[:12]
        self.phone = phone
        self.items = items          # 这一轮要打的接口（可能被筛选过）
        self.rounds = rounds
        self.workers = workers
        self.timeout = timeout
        self.with_voice = with_voice
        self.voice_times = voice_times
        self.voice_gap = voice_gap

        self.status = STATUS_WAITING
        self.round = 0
        self.done = 0               # 已经发出去多少条
        self.total = len(items) * rounds + (voice_times if with_voice else 0)

        self.stats = Stats("任务")
        self.started_at = time.time()
        self.finished_at = None

        self.logs = []              # [{"time": "...", "text": "...", "level": "..."}]
        self.recent = []            # 最近的单条结果，给表格用

        self.stop_flag = threading.Event()   # 点"停止"时 set 它
        self.lock = threading.Lock()          # 多个线程一起改数据，加把锁

    # ------------------------------------------------------------ 给网页看
    def to_dict(self):
        """把当前进度整理成字典，网页拿到就能直接画。"""
        with self.lock:
            if self.finished_at is not None:
                cost = self.finished_at - self.started_at
            else:
                cost = time.time() - self.started_at

            data = self.stats.to_dict()
            return {
                "id": self.id,
                "phone": mask_phone(self.phone),
                "status": self.status,
                "round": self.round,
                "rounds": self.rounds,
                "done": self.done,
                "total": self.total,
                "percent": round(self.done * 100.0 / self.total, 1) if self.total else 0,
                "success": data["success"],
                "failed": data["failed"],
                "status_count": data["status"],
                "error_count": data["errors"],
                "elapsed": round(cost, 1),
                "logs": list(self.logs),
                "recent": list(self.recent),
            }

    # ------------------------------------------------------------ 内部记东西
    def _write_log(self, text, level="info"):
        """记一条日志。调用前要已经拿到锁。"""
        line = {
            "time": time.strftime("%H:%M:%S"),
            "text": text,
            "level": level,
        }
        self.logs.append(line)
        if len(self.logs) > MAX_LOGS:
            del self.logs[0]

    def log(self, text, level="info"):
        """记一条日志（会自己加锁）。"""
        with self.lock:
            self._write_log(text, level)

    def add_result(self, result):
        """一条接口发完了：更新计数、记日志、放进最近结果。"""
        with self.lock:
            self.done += 1
            self.stats.add(result)

            if result["ok"]:
                # 2xx 算正常，4xx/5xx 也能发出去，只是被对方挡了，显示成黄色
                level = "ok" if result["status"] < 400 else "warn"
                self._write_log(
                    "%s %s  %.2fs" % (result["status"], result["name"], result["cost"]), level
                )
            else:
                self._write_log("%s  %s" % (result["name"], result["error"]), "fail")

            self.recent.append(
                {
                    "name": result["name"],
                    "ok": result["ok"],
                    "status": result["status"],
                    "cost": round(result["cost"], 2),
                    "error": result["error"],
                }
            )
            if len(self.recent) > MAX_RECENT:
                del self.recent[0]

    def stop(self):
        """网页上点"停止"。正在跑的请求不会被打断，但不再往队列里塞新的。"""
        self.stop_flag.set()
        self.log("收到停止指令，等当前这批发完就停", "warn")

    # ------------------------------------------------------------ 真正干活
    def run(self):
        """后台线程里跑的就是这个：一轮一轮发，最后再打语音。"""
        self.status = STATUS_RUNNING
        self.log("开始发送，共 %d 条接口 × %d 轮" % (len(self.items), self.rounds))

        try:
            for round_no in range(1, self.rounds + 1):
                if self.stop_flag.is_set():
                    break

                with self.lock:
                    self.round = round_no
                self.log("第 %d/%d 轮开始" % (round_no, self.rounds), "warn")

                send_all(
                    self.items,
                    self.phone,
                    workers=self.workers,
                    timeout=self.timeout,
                    on_result=self.add_result,
                    stop_flag=self.stop_flag,
                    show_bar=False,          # 网页版不要控制台进度条
                )

            if self.with_voice and not self.stop_flag.is_set():
                from endpoints.voice import ENDPOINT

                self.log("开始语音呼叫：%d 次" % self.voice_times, "warn")
                send_voice(
                    ENDPOINT,
                    self.phone,
                    times=self.voice_times,
                    gap=self.voice_gap,
                    on_result=self.add_result,
                    stop_flag=self.stop_flag,
                    show_bar=False,
                )

            if self.stop_flag.is_set():
                self.status = STATUS_STOPPED
                self.log("已停止，共发出 %d 条" % self.done, "warn")
            else:
                self.status = STATUS_DONE
                self.log("全部发完，共 %d 条" % self.done, "ok")

        except Exception as exc:  # 兜底，任务不能把整个服务搞挂
            self.status = STATUS_ERROR
            self.log("任务出错：%s" % exc, "fail")
            print_fail("任务 %s 出错：%s" % (self.id, exc))

        finally:
            self.finished_at = time.time()


# 所有任务都放这里：id -> Task
TASKS = {}
TASKS_LOCK = threading.Lock()


def create_task(phone, items, rounds, workers, timeout, with_voice, voice_times, voice_gap):
    """建一个任务，扔到后台线程里跑，马上把任务对象还给调用方。"""
    task = Task(phone, items, rounds, workers, timeout, with_voice, voice_times, voice_gap)

    with TASKS_LOCK:
        TASKS[task.id] = task
        clean_old_tasks()

    thread = threading.Thread(target=task.run, daemon=True)
    thread.start()
    return task


def clean_old_tasks():
    """任务太多了就把最早那些已经结束的删掉，防止内存一直涨。"""
    if len(TASKS) <= MAX_TASKS:
        return

    finished = []
    for task in TASKS.values():
        if task.status in (STATUS_DONE, STATUS_STOPPED, STATUS_ERROR):
            finished.append(task)

    finished.sort(key=lambda item: item.started_at)
    for task in finished[: len(TASKS) - MAX_TASKS]:
        TASKS.pop(task.id, None)


def get_task(task_id):
    """按 id 找任务，没有就返回 None。"""
    with TASKS_LOCK:
        return TASKS.get(task_id)


def list_tasks():
    """任务列表，新任务排前面。"""
    with TASKS_LOCK:
        tasks = list(TASKS.values())

    tasks.sort(key=lambda item: item.started_at, reverse=True)
    return tasks
