#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小黑盒 App Token 导出工具（已 root 安卓 + adb）-- 优化版
思路：先取得 root 上下文 -> 在设备内用 grep 定位含 token 的文件 ->
      仅 pull 命中的少量文件 -> 扫描明文 token -> 写入 cookie.txt。
全程不重新登录、不抓包、不装证书 -> 不会顶号。

前置（关键）：
  1) 手机开 USB 调试并连电脑（adb devices 能看到 218a59f8 这类设备）
  2) KernelSU：在管理器里开启「Root authorization for ADB」（设置页），
     使 `adb root` 可用。开启后本脚本即可自动以 root 运行。
  3) platform-tools 已装，ADB 路径见下方 ADB 常量。

用法：
  python dump_token.py
成功后直接：run_sign.bat
"""
import os
import re
import subprocess
import time

PKG = "com.max.xiaoheihe"                         # 小黑盒包名（已确认）
ADB = r"D:\Desktop\Tools\platform-tools\adb.exe"  # 本机已定位的 adb；换机器请改
HERE = os.path.dirname(os.path.abspath(__file__))
EXTRACT_DIR = os.path.join(HERE, "token_dump")

# 要找的字段（命中其一即可，优先 pkey + x_xhh_tokenid）
KEYS = ["pkey", "user_pkey", "x_xhh_tokenid", "user_heybox_id", "tokenid", "heybox_id"]


def run(cmd, timeout=90):
    print(">>", " ".join(cmd))
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        print(f"[!] 找不到可执行文件：{cmd[0]}")
        print("    请确认 ADB 路径正确，或 platform-tools 已加入 PATH。")
        raise SystemExit(1)


def build_value_pattern(key_bytes: bytes) -> "re.Pattern":
    q = rb"[\x27\x22]"                       # 单引号或双引号
    val = rb"[^\x3c\x27\x22\s]+"             # 取值：排除 < ' " 与空白
    # XML 分支: name="key">value   /  name='key'>value
    # JSON 分支: "key":"value"     /  'key':'value'
    pat = (
        rb"(?:name=" + q + rb"?" + re.escape(key_bytes) + q + rb"?\s*>"
        rb"|" + q + re.escape(key_bytes) + q + rb"\s*[:=]\s*" + q + rb")"
        + val
    )
    return re.compile(pat)


def main():
    os.makedirs(EXTRACT_DIR, exist_ok=True)

    # 1) 取得 root 上下文
    r = run([ADB, "root"])
    time.sleep(2)
    if r.returncode != 0:
        print("[!] adb root 失败：", (r.stderr or r.stdout).strip())
        print("    请确认 KernelSU 已在管理器开启「Root authorization for ADB」。")
        return
    who = run([ADB, "shell", "id"]).stdout.strip()
    print("[+] root 上下文:", who or "(空)")

    base = f"/data/data/{PKG}"

    # 2) 设备内定位含关键字的文件（toybox grep 支持 -rIl 与 BRE 的 \| 或）
    pattern = "\\|".join(KEYS)  # BRE 中用 \| 表示或
    find_cmd = f'grep -rIl "{pattern}" {base} 2>/dev/null'
    r = run([ADB, "shell", find_cmd], timeout=120)
    files = [l.strip() for l in r.stdout.splitlines() if l.strip()]
    if not files:
        print("[!] 在 App 私有数据里没找到这些关键字 -> token 可能加密存储。")
        print("    请改用 Reqable 抓包方案（同样需要 KernelSU root 装系统 CA）。")
        return
    print(f"[+] 命中文件 {len(files)} 个：")
    for f in files[:30]:
        print("   ", f)

    # 3) 仅 pull 命中文件并扫描
    found = {}
    for f in files:
        local = os.path.join(EXTRACT_DIR, f.lstrip("/").replace("/", "_"))
        rp = run([ADB, "pull", f, local], timeout=120)
        if rp.returncode != 0 or not os.path.exists(local):
            continue
        data = open(local, "rb").read()
        for key in KEYS:
            if key in found:
                continue
            kb = key.encode()
            if kb in data:
                m = build_value_pattern(kb).search(data)
                if m:
                    found[key] = m.group(1).decode("utf-8", "replace")

    print("\n=== 扫描到的字段 ===")
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
        print("[!] 未同时拿到 pkey 与 x_xhh_tokenid，请手动检查 token_dump/ 目录。")


if __name__ == "__main__":
    main()
