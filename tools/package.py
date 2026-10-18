#!/usr/bin/env python3
"""
把「阅读器 + 示例论文 + 工具链」打成一个可分发的 zip。

用法:
    python tools/package.py                 # 版本号取 VERSION 文件，缺省 0.1.0
    python tools/package.py --version 0.2.0
    python tools/package.py --out D:/tmp

产物: dist/bilingual-paper-reader-<version>.zip
解压后双击 index.html 即可使用，不需要 Python，也不需要联网。
"""
import argparse
import os
import sys
import zipfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "bilingual-paper-reader"

INCLUDE_FILES = [
    "index.html", "README.md", "LICENSE", "NOTICE.md",
    "build_paper.py", "make.ps1", "make.sh", "VERSION",
    "data/README.md",
    os.path.join("papers", "manifest.json"),
]
INCLUDE_DIRS = ["reader", "tools", "docs", os.path.join("data", "demo")]

SKIP_DIRS = {".git", "dist", "__pycache__", ".idea", ".vscode", "node_modules"}
SKIP_EXT = {".pyc", ".pyo", ".log", ".tmp"}
SKIP_PREFIX = ("_", ".")


def want(path, rel):
    parts = rel.replace("\\", "/").split("/")
    if any(p in SKIP_DIRS for p in parts):
        return False
    if os.path.splitext(path)[1].lower() in SKIP_EXT:
        return False
    if os.path.basename(path).startswith(SKIP_PREFIX):
        return False
    return True


def collect():
    files = []
    for rel in INCLUDE_FILES:
        p = os.path.join(BASE, rel)
        if os.path.isfile(p):
            files.append(p)
    for rel in INCLUDE_DIRS:
        root = os.path.join(BASE, rel)
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                p = os.path.join(dirpath, fn)
                if want(p, os.path.relpath(p, BASE)):
                    files.append(p)
    return sorted(set(files))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default=None)
    ap.add_argument("--out", default=os.path.join(BASE, "dist"))
    args = ap.parse_args()

    ver = args.version
    if not ver:
        vfile = os.path.join(BASE, "VERSION")
        ver = io_open(vfile).strip() if os.path.exists(vfile) else "0.1.0"

    files = collect()
    if not files:
        sys.exit("没有可打包的文件")

    os.makedirs(args.out, exist_ok=True)
    target = os.path.join(args.out, "%s-%s.zip" % (NAME, ver))
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in files:
            rel = os.path.relpath(p, BASE).replace("\\", "/")
            z.write(p, NAME + "/" + rel)
    size = os.path.getsize(target) / 1024
    print("打包 %d 个文件 → %s (%.0f KB)" % (len(files), target, size))
    for p in files:
        print("  + " + os.path.relpath(p, BASE).replace("\\", "/"))


def io_open(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    main()
