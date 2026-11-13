# -*- coding: utf-8 -*-
"""统计发送结果，最后打一张小报告。

用法：建一个 Stats，把 send_one() 返回的字典一条条 add 进去，
最后 show() 一下就行。
"""

from printer import say


class Stats:
    """一份统计。想统计哪一段，就单独建一个。"""

    def __init__(self, title="统计"):
        self.title = title
        self.total = 0       # 一共发了多少次
        self.success = 0     # 成功几次
        self.failed = 0      # 失败几次
        self.status_count = {}   # 状态码 -> 次数
        self.error_count = {}    # 错误类型 -> 次数

    def add(self, result):
        """把一条结果算进来。"""
        self.total += 1

        if result["ok"]:
            self.success += 1
            code = result["status"]
            self.status_count[code] = self.status_count.get(code, 0) + 1
        else:
            self.failed += 1
            # 错误信息一般长这样 "Timeout: xxx"，取冒号前面那段当类型
            reason = (result["error"] or "未知错误").split(":")[0].strip()
            self.error_count[reason] = self.error_count.get(reason, 0) + 1

    def add_many(self, results):
        """一次算一批。"""
        for result in results:
            self.add(result)
        return self

    def merge(self, other):
        """把另一份统计并进来。"""
        self.total += other.total
        self.success += other.success
        self.failed += other.failed

        for code, count in other.status_count.items():
            self.status_count[code] = self.status_count.get(code, 0) + count
        for reason, count in other.error_count.items():
            self.error_count[reason] = self.error_count.get(reason, 0) + count
        return self

    def to_dict(self):
        """给网页用：把统计变成可以直接转成 JSON 的字典。"""
        return {
            "total": self.total,
            "success": self.success,
            "failed": self.failed,
            "status": dict(self.status_count),
            "errors": dict(self.error_count),
        }

    def show(self):
        """打印出来。"""
        if self.total == 0:
            say("%s：一条都没发" % self.title)
            return

        rate = self.success * 100.0 / self.total
        say(
            "%s：共 %d 次，成功 %d，失败 %d，成功率 %.1f%%"
            % (self.title, self.total, self.success, self.failed, rate),
            "cyan",
        )

        # 状态码分布，次数多的排前面
        if self.status_count:
            parts = []
            for code, count in sorted(self.status_count.items(), key=lambda x: -x[1]):
                parts.append("%s×%d" % (code, count))
            say("  HTTP 状态：" + "，".join(parts), "white")

        # 失败原因，只列最多的 5 种
        if self.error_count:
            sorted_errors = sorted(self.error_count.items(), key=lambda x: -x[1])[:5]
            parts = []
            for reason, count in sorted_errors:
                parts.append("%s×%d" % (reason, count))
            say("  失败原因：" + "，".join(parts), "white")
