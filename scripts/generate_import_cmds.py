#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从「目录文本」批量导入章节到 RZCode 学习知识库。

设计说明：
  1. 零第三方依赖：脚本只用 Python 标准库生成 curl 命令列表，再由 sh 执行，
     因此无需安装 requests，也便于在任何机器上直接运行。
  2. 路由与 tools/*.tool.json 的 endpoint 字段保持一致：
       创建书籍  POST /books/{title}                 body: {authors, edition}
       创建章节  POST /books/{book}/chapters/{title} body: {level, order, summary, parent_title}

用法：
    python3 generate_import_cmds.py toc.txt --book "书名" \
        --author "张三" --author "李四" --edition "xx出版社 2005 · ISBN xxx" \
        --out /tmp/import_cmds.sh
    sh /tmp/import_cmds.sh          # 每行输出 "<状态码> <- <章节>"

toc.txt 每行一个目录条目，形如（末尾页码可省略）：
    第1章 绪论 1
    1.1 现代测试技术的内容和任务 1
    1.1.1 产品开发和性能试验 2
    参考文献 336
也可用两个空格缩进表达层级（编号无法判层级时使用）。
"""
import argparse
import json
import re
import urllib.parse

NUMERIC_CODE = re.compile(r"^\d+(?:\.\d+)+$")
CHAPTER_CODE = re.compile(r"^第[0-9一二三四五六七八九十百]+[章节篇]$")


def parse_toc(lines):
    entries = []
    for raw in lines:
        line = raw.rstrip("\n").rstrip()
        if not line.strip():
            continue
        indent = (len(line) - len(line.lstrip())) // 2
        tokens = line.split()

        page = None
        if tokens and tokens[-1].isdigit():
            page = int(tokens[-1])
            tokens = tokens[:-1]
        if not tokens:
            continue

        num = tokens[0]
        title = " ".join(tokens[1:]) if len(tokens) > 1 else num
        # 标题里可能是 "第1章 绪论" 这种 num 本身就是 "第1章" 的形式
        if not title:
            title = num

        if NUMERIC_CODE.match(num):
            level = num.count(".") + 1
        elif CHAPTER_CODE.match(num):
            level = 1
        else:
            level = max(indent, 0) + 1

        entries.append((num, title, page, level))
    return entries


def build_commands(book, authors, edition, entries, api_key, host):
    base = host.rstrip("/") + "/api/study"
    enc_book = urllib.parse.quote(book, safe="")
    cmds = []

    def add(method, path, payload, label):
        body = json.dumps(payload, ensure_ascii=False).replace("'", "'\\''")
        cmds.append(
            "curl -s -o /dev/null -w '%{{http_code}}' -X {m} '{u}' "
            "-H \"X-API-Key: {k}\" -H 'Content-Type: application/json' "
            "-d '{b}'\necho ' <- {l}'\n".format(
                m=method, u=base + path, k=api_key, b=body, l=label
            )
        )

    # 1) 书籍
    book_payload = {}
    if authors:
        book_payload["authors"] = authors
    if edition:
        book_payload["edition"] = edition
    add("POST", "/books/" + enc_book, book_payload, f"BOOK {book}")

    # 2) 章节：按栈维护父节点，order 按「同父同级」递增
    stack = {}
    counters = {}
    for num, title, page, level in entries:
        parent = None
        for lv in range(level - 1, 0, -1):
            if lv in stack:
                parent = stack[lv]
                break
        key = (parent, level)
        order = counters.get(key, 0) + 1
        counters[key] = order

        display = f"{num} {title}" if title != num else title
        payload = {"level": level, "order": order}
        if page is not None:
            payload["summary"] = f"第 {page} 页"
        if parent:
            payload["parent_title"] = parent

        path = "/books/{}/chapters/{}".format(
            enc_book, urllib.parse.quote(display, safe="")
        )
        add("POST", path, payload, f"CH [{len(cmds)}] {display}")

        stack[level] = display
        for lv in [lv for lv in stack if lv > level]:
            del stack[lv]

    return cmds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("toc_file")
    ap.add_argument("--book", required=True)
    ap.add_argument("--author", action="append", default=[])
    ap.add_argument("--edition", default=None)
    ap.add_argument("--out", default="/tmp/import_cmds.sh")
    ap.add_argument("--config", default="~/.rzcode/config.json")
    a = ap.parse_args()

    import os

    cfg = json.load(open(os.path.expanduser(a.config)))
    with open(a.toc_file, encoding="utf-8") as f:
        entries = parse_toc(f.readlines())

    cmds = build_commands(
        a.book, a.author, a.edition, entries, cfg["api_key"], cfg["api_host"]
    )
    with open(a.out, "w", encoding="utf-8") as f:
        f.writelines(cmds)
    print(f"解析条目 {len(entries)} 条 → 生成请求 {len(cmds)} 条 → {a.out}")
    print("执行: sh " + a.out)


if __name__ == "__main__":
    main()
