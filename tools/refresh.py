#!/usr/bin/env python3
"""从 x.ai 官方 Bot Marketplace 抓取模板目录，合并中文译名，生成 assets/data.js。

用法:
    python3 tools/refresh.py            # 联网抓取并重新生成
    python3 tools/refresh.py --check    # 只校验现有 data.js 里的链接是否仍然可用

数据来源只有一个：https://x.ai/bot/marketplace 页面内嵌的 RSC 负载。
脚本不会凭空编造任何模板或链接；官方目录里没有的条目不会出现在站点上。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MARKETPLACE_URL = "https://x.ai/bot/marketplace"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)

ROOT = Path(__file__).resolve().parent.parent
ZH_PATH = ROOT / "tools" / "zh.json"
OUT_PATH = ROOT / "assets" / "data.js"


def fetch(url: str, timeout: int = 40) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def head_status(url: str, timeout: int = 25) -> int:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception:
        return 0


def rsc_payload(html: str) -> str:
    """页面把 React Server Component 负载切成多段 self.__next_f.push 调用，这里拼回来。"""
    chunks = re.findall(r'self\.__next_f\.push\(\[1,(".*?")\]\)', html, re.S)
    return "".join(json.loads(c) for c in chunks)


def extract_array(payload: str, key: str) -> list:
    """从负载里按括号配对切出一个 JSON 数组（负载整体不是合法 JSON，只能局部解析）。"""
    marker = f'"{key}":['
    start = payload.find(marker)
    if start < 0:
        raise SystemExit(f"未在官方页面里找到 {key} 数组，页面结构可能变了。")
    start += len(marker) - 1

    depth = 0
    in_str = False
    escaped = False
    for i in range(start, len(payload)):
        ch = payload[i]
        if in_str:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return json.loads(payload[start : i + 1])
    raise SystemExit(f"{key} 数组没有正常闭合。")


def build() -> list[dict]:
    zh = json.loads(ZH_PATH.read_text(encoding="utf-8"))
    zh_templates = zh["templates"]
    zh_categories = zh["_categories"]

    raw = extract_array(rsc_payload(fetch(MARKETPLACE_URL)), "templates")
    print(f"官方目录抓到 {len(raw)} 条模板")

    out = []
    missing = []
    for item in raw:
        slug = item["id"]
        token_match = re.search(r"id=([A-Za-z0-9_\-]+)", item.get("addHref") or "")
        if not token_match:
            print(f"  跳过 {slug}：没有安装链接", file=sys.stderr)
            continue
        token = token_match.group(1)

        zh_entry = zh_templates.get(slug)
        if not zh_entry:
            missing.append(slug)

        cats = item.get("categories") or []
        out.append(
            {
                "slug": slug,
                "name": item["name"],
                "nameZh": (zh_entry or {}).get("name") or item["name"],
                "descZh": (zh_entry or {}).get("desc") or "",
                "desc": (item.get("description") or "").strip(),
                "creator": item.get("creatorName") or "",
                "handle": item.get("handle") or "",
                "cats": cats,
                "catsZh": [zh_categories.get(c, c) for c in cats],
                # 官方模板预览页，页面上的「Add to Grok Bot」是 grokbot:// 深链
                "install": f"https://x.ai/bot/{token}",
                # 官方市场里的详情页
                "detail": f"https://x.ai/bot/marketplace/bots/{slug}",
            }
        )

    if missing:
        print(f"提示：{len(missing)} 条缺中文译名，先回退英文：{', '.join(missing)}")
    return out


def write(records: list[dict]) -> None:
    zh = json.loads(ZH_PATH.read_text(encoding="utf-8"))
    payload = {
        "source": MARKETPLACE_URL,
        "categories": zh["_categories"],
        "templates": records,
    }
    body = json.dumps(payload, ensure_ascii=False, indent=1)
    OUT_PATH.write_text(
        "// 本文件由 tools/refresh.py 生成，请勿手改。\n"
        "// 数据源：x.ai 官方 Bot Marketplace。中文译名维护在 tools/zh.json。\n"
        f"window.GROK_BOT_TEMPLATES = {body};\n",
        encoding="utf-8",
    )
    print(f"已写入 {OUT_PATH.relative_to(ROOT)}（{len(records)} 条）")


def check() -> int:
    text = OUT_PATH.read_text(encoding="utf-8")
    data = json.loads(text[text.index("=") + 1 :].rstrip().rstrip(";"))
    urls = [t["install"] for t in data["templates"]] + [
        t["detail"] for t in data["templates"]
    ]
    bad = []
    with ThreadPoolExecutor(8) as pool:
        for url, status in zip(urls, pool.map(head_status, urls)):
            if status != 200:
                bad.append((url, status))
    print(f"检查 {len(urls)} 个链接，异常 {len(bad)} 个")
    for url, status in bad:
        print(f"  {status}  {url}")
    return 1 if bad else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="只校验链接可用性")
    args = parser.parse_args()
    if args.check:
        raise SystemExit(check())
    write(build())
