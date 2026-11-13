# -*- coding: utf-8 -*-
"""哈希、RC4、Base64 这些"算签名"用的小工具。

老版本里这些函数的名字是一串乱码（像 r77d51986dcf44955e359a8c19bf72837），
根本看不出来干什么。这里统一改了名，对应关系如下：

    乱码名字                             现在的名字
    r77d51986dcf44955e359a8c19bf72837   sha1_text
    d8556af1cbf9e4f0e1068c38bd6fedb14   sha256_text
    oba392eaed8208d36ddbeb7fe66fd5637   md5_text
    l9871472f620c6f46c93728e92d1349a9   rc4_text
    r7589ac6513307d1fa97b2b8a73755751   rc4_bytes
    i7c6fb3134c356bf9fbdd691a378d51dc   text_to_hex
    d5fd39c2a334d0204425bf97bbcb28876   hex_to_bytes
    y7d70291d2190fbf7b67ecb87e278aa4e   base64_encode
    j33fc4a568bf04579668abcde95784917   base64_decode
    r5be224d49f6cdd36b448a304e14ca7ac   base64_encode（可以传自己的字母表）

注意：现在的接口清单没用到这里的东西，是留着以后遇到"要自己算 sign 参数"
的接口时能直接拿来用的。
"""

import hashlib
import struct

# Base64 的字母表，也可以换成 URL 安全版
BASE64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

# python 的整数是无限位的，做 32 位运算时要用它把多余的高位切掉
MASK32 = 0xFFFFFFFF


def _to_bytes(data):
    """字符串先转成 bytes，bytes 就原样返回。"""
    if isinstance(data, str):
        return data.encode("utf-8")
    return data


# ------------------------------------------------------------------ MD5
def md5_text(text):
    """算 MD5，返回 32 个字符的十六进制字符串。"""
    return hashlib.md5(_to_bytes(text)).hexdigest()


# ------------------------------------------------------------------ SHA-1
def _rotate_left(value, bits):
    """32 位循环左移。"""
    return ((value << bits) | (value >> (32 - bits))) & MASK32


def _pad_for_sha1(message):
    """按 SHA-1 的规则补位：先补 0x80，再补 0，最后补消息长度。"""
    length = len(message)
    message = message + b"\x80"
    message = message + b"\x00" * ((56 - (length + 1) % 64) % 64)
    message = message + struct.pack(">Q", length * 8)
    return message


def sha1_text(data):
    """算 SHA-1，返回 40 个字符的十六进制字符串。

    没用 hashlib，是自己按算法写的。好处是想改成带盐/魔改的版本时
    直接在这里动手就行。
    """
    h0, h1, h2, h3, h4 = 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0
    message = _pad_for_sha1(_to_bytes(data))

    # 一次处理 64 字节（一个块）
    for start in range(0, len(message), 64):
        block = message[start:start + 64]
        words = list(struct.unpack(">16I", block))
        # 16 个字扩展成 80 个字
        for i in range(16, 80):
            words.append(
                _rotate_left(words[i - 3] ^ words[i - 8] ^ words[i - 14] ^ words[i - 16], 1)
            )

        a, b, c, d, e = h0, h1, h2, h3, h4
        for i in range(80):
            if i < 20:
                f = (b & c) | ((~b) & d)
                k = 0x5A827999
            elif i < 40:
                f = b ^ c ^ d
                k = 0x6ED9EBA1
            elif i < 60:
                f = (b & c) | (b & d) | (c & d)
                k = 0x8F1BBCDC
            else:
                f = b ^ c ^ d
                k = 0xCA62C1D6

            temp = (_rotate_left(a, 5) + f + e + k + words[i]) & MASK32
            e = d
            d = c
            c = _rotate_left(b, 30)
            b = a
            a = temp

        h0 = (h0 + a) & MASK32
        h1 = (h1 + b) & MASK32
        h2 = (h2 + c) & MASK32
        h3 = (h3 + d) & MASK32
        h4 = (h4 + e) & MASK32

    return "%08x%08x%08x%08x%08x" % (h0, h1, h2, h3, h4)


# ------------------------------------------------------------------ SHA-256
def _rotate_right(value, bits):
    """32 位循环右移。"""
    return ((value >> bits) | (value << (32 - bits))) & MASK32


def _pad_for_sha256(message):
    """按 SHA-256 的规则补位。"""
    length = len(message)
    message = message + b"\x80"
    message = message + b"\x00" * ((64 - (length + 9) % 64) % 64)
    message = message + struct.pack(">Q", length * 8)
    return message


# 8 个初始值和 64 个常量，都是按算法规定写死的数字
SHA256_H = [
    0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
    0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19,
]

SHA256_K = [
    0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5, 0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5,
    0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3, 0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174,
    0xE49B69C1, 0xEFBE4786, 0x0FC19DC6, 0x240CA1CC, 0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA,
    0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7, 0xC6E00BF3, 0xD5A79147, 0x06CA6351, 0x14292967,
    0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13, 0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85,
    0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3, 0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070,
    0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5, 0x391C0CB3, 0x4ED8AA4A, 0x5B9CCA4F, 0x682E6FF3,
    0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208, 0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2,
]


def sha256_text(data):
    """算 SHA-256，返回 64 个字符的十六进制字符串。"""
    h = list(SHA256_H)
    message = _pad_for_sha256(_to_bytes(data))

    for start in range(0, len(message), 64):
        block = message[start:start + 64]
        words = list(struct.unpack(">16I", block))
        for i in range(16, 64):
            s0 = (
                _rotate_right(words[i - 15], 7)
                ^ _rotate_right(words[i - 15], 18)
                ^ (words[i - 15] >> 3)
            )
            s1 = (
                _rotate_right(words[i - 2], 17)
                ^ _rotate_right(words[i - 2], 19)
                ^ (words[i - 2] >> 10)
            )
            words.append((words[i - 16] + s0 + words[i - 7] + s1) & MASK32)

        a, b, c, d, e, f, g, hh = h
        for i in range(64):
            s1 = _rotate_right(e, 6) ^ _rotate_right(e, 11) ^ _rotate_right(e, 25)
            ch = (e & f) ^ ((~e) & g)
            temp1 = (hh + s1 + ch + SHA256_K[i] + words[i]) & MASK32
            s0 = _rotate_right(a, 2) ^ _rotate_right(a, 13) ^ _rotate_right(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (s0 + maj) & MASK32

            hh = g
            g = f
            f = e
            e = (d + temp1) & MASK32
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & MASK32

        h[0] = (h[0] + a) & MASK32
        h[1] = (h[1] + b) & MASK32
        h[2] = (h[2] + c) & MASK32
        h[3] = (h[3] + d) & MASK32
        h[4] = (h[4] + e) & MASK32
        h[5] = (h[5] + f) & MASK32
        h[6] = (h[6] + g) & MASK32
        h[7] = (h[7] + hh) & MASK32

    return "".join("%08x" % value for value in h)


# ------------------------------------------------------------------ RC4
def _rc4_stream(key, length):
    """RC4 的密钥流：先打乱 0~255，再按规则一个个吐字节。"""
    table = list(range(256))
    j = 0
    for i in range(256):
        j = (j + table[i] + key[i % len(key)]) % 256
        table[i], table[j] = table[j], table[i]

    stream = bytearray()
    i = 0
    j = 0
    for _ in range(length):
        i = (i + 1) % 256
        j = (j + table[i]) % 256
        table[i], table[j] = table[j], table[i]
        stream.append(table[(table[i] + table[j]) % 256])
    return bytes(stream)


def rc4_bytes(data, key):
    """RC4 加密/解密，返回 bytes（加密解密是同一个操作）。"""
    data = _to_bytes(data)
    key = _to_bytes(key)
    stream = _rc4_stream(key, len(data))
    result = bytearray()
    for i in range(len(data)):
        result.append(data[i] ^ stream[i])
    return bytes(result)


def rc4_text(data, key):
    """RC4 加密/解密，结果当 UTF-8 字符串返回。"""
    return rc4_bytes(data, key).decode("utf-8")


# ------------------------------------------------------------------ 十六进制
def text_to_hex(data):
    """变成小写十六进制字符串。"""
    return _to_bytes(data).hex()


def hex_to_bytes(hex_string):
    """十六进制字符串变回 bytes。"""
    return bytes.fromhex(hex_string)


# ------------------------------------------------------------------ Base64
def base64_encode(data, chars=BASE64_CHARS):
    """Base64 编码。chars 可以换成别的 64 个字符的字母表。"""
    if len(chars) != 64:
        raise ValueError("字母表必须是 64 个字符")

    # 每 8 位拆成 6 位一段，再按字母表换成字符
    bits = ""
    for byte in _to_bytes(data):
        bits += format(byte, "08b")

    result = ""
    for i in range(0, len(bits), 6):
        piece = bits[i:i + 6]
        if len(piece) < 6:
            piece = piece + "0" * (6 - len(piece))
        result += chars[int(piece, 2)]

    # 不够 4 的倍数就补等号
    while len(result) % 4 != 0:
        result += "="
    return result


def base64_decode(text, chars=BASE64_CHARS):
    """Base64 解码，返回字符串。"""
    # 先把字符换回数字，再拼成二进制串
    bits = ""
    for char in text.rstrip("="):
        if char in chars:
            bits += format(chars.index(char), "06b")

    data = bytearray()
    for i in range(0, len(bits) - 7, 8):
        data.append(int(bits[i:i + 8], 2))
    return data.decode("utf-8")
