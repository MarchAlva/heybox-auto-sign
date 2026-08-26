#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫描小黑盒 App 数据归档（xhh_data.tar）或解包目录，提取 pkey / x_xhh_tokenid 写入 cookie.txt。
设计用途：手机 KernelSU 终端以 root 把含 token 的文件 tar 到 /sdcard 后，
          电脑侧 adb pull 下来，用本脚本解析，全程不重新登录、不顶号。

输入：
  - 默认 ./xhh_data.tar
  - 或指定 tar 路径：python scan_token.py path.tar
  - 或指定已解包目录：python scan_token.py some_dir/
"""
import os
import re
import sqlite3
import sys
import tarfile
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = ["pkey", "user_pkey", "x_xhh_tokenid", "user_heybox_id", "tokenid", "heybox_id"]


def try_sqlite_cookies(file_path: str, found: dict) -> bool:
    """如果 file_path 是 Chrome/WebView Cookies SQLite，直接查 cookies 表。"""
    try:
        conn = sqlite3.connect(file_path)
        cur = conn.cursor()
        # 取 cookies 表中 name 匹配的项，优先 .xiaoheihe.cn（跨域主 cookie）
        cur.execute(
            "SELECT name, value, host_key FROM cookies WHERE name IN (?, ?, ?, ?, ?, ?)",
            KEYS,
        )
        rows = cur.fetchall()
        conn.close()
    except Exception:
        return False

    if not rows:
        return False

    # 优先级：.xiaoheihe.cn > api.xiaoheihe.cn > 其他
    def host_priority(host):
        if host == ".xiaoheihe.cn":
            return 0
        if host.endswith("xiaoheihe.cn"):
            return 1
        return 2

    rows.sort(key=lambda r: host_priority(r[2]))
    for name, value, _ in rows:
        if name in KEYS and name not in found:
            found[name] = value
    return True


def build_value_pattern(key_bytes: bytes) -> "re.Pattern":
    q = rb"[\x27\x22]"                       # 单引号或双引号
    val = rb"([^\x3c\x27\x22\s]+)"           # 取值：排除 < ' " 与空白（加捕获组）
    return re.compile(
        rb"(?:name=" + q + rb"?" + re.escape(key_bytes) + q + rb"?\s*>"
        rb"|" + q + re.escape(key_bytes) + q + rb"\s*[:=]\s*" + q + rb")"
        + val
    )


def iter_files(path, tmpdir=None):
    """yield (name, file_path, bytes_data)
    对 tar 包会解包到 tmpdir；对目录直接遍历。"""
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for f in files:
                p = os.path.join(root, f)
                try:
                    yield p, p, open(p, "rb").read()
                except Exception:
                    continue
    else:
        extract_dir = tmpdir or tempfile.mkdtemp(prefix="xhh_scan_")
        with tarfile.open(path) as tf:
            # Python 3.12+ 安全过滤
            tf.extractall(extract_dir, filter="data")
        for root, _, files in os.walk(extract_dir):
            for f in files:
                p = os.path.join(root, f)
                rel = os.path.relpath(p, extract_dir)
                try:
                    yield rel, p, open(p, "rb").read()
                except Exception:
                    continue


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "xhh_data.tar")
    if not os.path.exists(src):
        print("[!] 找不到", src)
        raise SystemExit(1)

    tmpdir = None if os.path.isdir(src) else tempfile.mkdtemp(prefix="xhh_scan_")
    found = {}
    try:
        for name, file_path, data in iter_files(src, tmpdir):
            # 优先尝试 SQLite Cookies 表（WebView Cookie 通常存在这里）
            if os.path.getsize(file_path) < 50 * 1024 * 1024:  # 只处理 < 50MB 的文件
                try_sqlite_cookies(file_path, found)

            # 正则兜底（SharedPreferences XML / JSON 等）
            for key in KEYS:
                if key in found:
                    continue
                kb = key.encode()
                if kb in data:
                    m = build_value_pattern(kb).search(data)
                    if m:
                        found[key] = m.group(1).decode("utf-8", "replace")
    finally:
        if tmpdir and os.path.exists(tmpdir):
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

    print("=== 扫描到的字段 ===")
    for k, v in found.items():
        print(f"  {k} = {v[:60]}{'...' if len(v) > 60 else ''}")

    pkey = found.get("pkey") or found.get("user_pkey")
    token = found.get("x_xhh_tokenid")
    if pkey and token:
        cookie = f"pkey={pkey};x_xhh_tokenid={token};"
        with open(os.path.join(HERE, "cookie.txt"), "w", encoding="ascii") as fh:
            fh.write(cookie + "\n")
        print("\n[+] 已写入 cookie.txt：")
        print("  ", cookie)
        print("    直接运行 run_sign.bat 即可。")
    else:
        print("[!] 未同时拿到 pkey 与 x_xhh_tokenid。")
        print("    token 可能加密存储（grep 命中文件但值非明文），请改用 Reqable 抓包方案。")


if __name__ == "__main__":
    main()
