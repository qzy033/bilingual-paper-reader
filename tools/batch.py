#!/usr/bin/env python3
"""
按书架清单批量翻译 papers/ 里的论文：抽取 → 翻译 → 术语 → 构建。

用法:
    python tools/batch.py --dry-run          # 看看还差几篇
    python tools/batch.py                    # 把没译的都译了
    python tools/batch.py --only 2302.13971  # 只译一篇
    python tools/batch.py --limit 2          # 先来两篇
    python tools/batch.py --no-terms         # 跳过术语标注与映射表

需要 OPENAI_API_KEY（见 docs/USAGE.md §3.1）。每篇处理完就落盘，
中途失败不会影响已完成的部分，重跑会自动跳过已译的。
"""
import argparse
import io
import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_manifest():
    p = os.path.join(BASE, "papers", "manifest.json")
    if not os.path.exists(p):
        sys.exit("找不到 papers/manifest.json")
    return json.load(io.open(p, encoding="utf-8"))


def pending_items(manifest, only=None, limit=None):
    out = []
    for it in manifest.get("items", []):
        arxiv = (it.get("arxiv") or "").strip()
        slug = (it.get("slug") or "").strip()
        if not arxiv:
            continue
        if only and arxiv != only:
            continue
        if slug and os.path.isdir(os.path.join(BASE, "data", slug)):
            continue
        if not os.path.exists(os.path.join(BASE, "papers", arxiv + ".pdf")):
            print("  [跳过] %s 没有 PDF" % arxiv)
            continue
        out.append((arxiv, slug or arxiv.replace(".", "-"), it))
        if limit and len(out) >= limit:
            break
    return out


def run(cmd, label):
    print("  · " + label)
    r = subprocess.run(cmd, cwd=BASE)
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="只处理某个 arXiv 号")
    ap.add_argument("--limit", type=int, help="最多处理几篇")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-terms", action="store_true", help="跳过 --annotate / --with-terms")
    ap.add_argument("--force", action="store_true", help="重译已有译文")
    ap.add_argument("--batch-size", type=int, default=6)
    args = ap.parse_args()

    manifest = load_manifest()
    todo = pending_items(manifest, args.only, args.limit)
    total = len([i for i in manifest.get("items", []) if i.get("arxiv")])
    print("书架 %d 篇，待译 %d 篇" % (total, len(todo)))
    for arxiv, slug, it in todo:
        print("   - %s  %s  → data/%s" % (arxiv, (it.get("titleZh") or it.get("titleEn") or "")[:40], slug))
    if args.dry_run or not todo:
        return

    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("缺少 OPENAI_API_KEY；先 --dry-run，或参考 docs/USAGE.md §3.1 配置")

    ok, fail = [], []
    for i, (arxiv, slug, it) in enumerate(todo, start=1):
        print("\n[%d/%d] %s %s" % (i, len(todo), arxiv, it.get("titleZh") or ""))
        if not run([sys.executable, "tools/pdf_to_json.py",
                    os.path.join("papers", arxiv + ".pdf"), slug], "抽取 PDF"):
            fail.append((arxiv, "抽取失败"))
            continue
        # 抽取器不知道中文标题/分组，把 manifest 里的元信息补进 meta
        meta_path = os.path.join(BASE, "data", slug, "00-meta.json")
        if os.path.exists(meta_path):
            meta = json.load(io.open(meta_path, encoding="utf-8"))
            meta["meta"]["title"] = it.get("titleEn") or meta["meta"].get("title", "")
            meta["meta"]["titleZh"] = it.get("titleZh") or ""
            meta["meta"]["source"] = "arXiv:%s" % arxiv
            meta["meta"]["arxiv"] = arxiv
            meta["meta"]["group"] = it.get("group") or ""
            meta["meta"]["note"] = "非官方中文译本，仅供学习；原文版权归原作者所有。"
            io.open(meta_path, "w", encoding="utf-8").write(
                json.dumps(meta, ensure_ascii=False, indent=2) + "\n")

        tl = [sys.executable, "tools/translate.py", "--slug", slug,
              "--batch", str(args.batch_size)]
        if not args.no_terms:
            tl += ["--annotate", "--with-terms"]
        if args.force:
            tl.append("--force")
        if not run(tl, "翻译"):
            fail.append((arxiv, "翻译失败"))
            continue
        if not run([sys.executable, "build_paper.py"], "构建"):
            fail.append((arxiv, "构建失败"))
            continue
        ok.append(arxiv)

    print("\n完成 %d 篇，失败 %d 篇" % (len(ok), len(fail)))
    for a, why in fail:
        print("  ✗ %s  %s" % (a, why))
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
