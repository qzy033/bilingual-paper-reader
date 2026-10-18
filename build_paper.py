"""
把 data/<slug>/*.json 组装成阅读器可加载的数据文件。

用法:
    python build_paper.py            # 构建全部论文 -> reader/papers/library.js
    python build_paper.py attention  # 只构建/校验某一篇

约定:
    data/<slug>/00-meta.json   论文元信息 + 术语表
    data/<slug>/NN-*.json      每一节一个文件，按文件名排序
    data/<slug>/img/*.png      插图；构建时复制到 reader/assets/<slug>/
"""
import json, glob, os, re, shutil, collections, sys

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
READER = os.path.join(BASE, "reader")
OUT_JS = os.path.join(READER, "papers", "library.js")
ASSETS = os.path.join(READER, "assets")


def load_paper(folder):
    slug = os.path.basename(folder)
    files = sorted(glob.glob(os.path.join(folder, "*.json")))
    files = [f for f in files if os.path.basename(f) != "terms.json"]
    if not files:
        raise SystemExit("找不到数据文件: " + folder)
    meta = json.load(open(files[0], encoding="utf-8"))
    meta.setdefault("id", slug)
    sections = []
    for f in files[1:]:
        sec = json.load(open(f, encoding="utf-8"))
        if "blocks" in sec:
            sections.append(sec)
    terms = {}
    tp = os.path.join(folder, "terms.json")
    if os.path.exists(tp):
        terms = json.load(open(tp, encoding="utf-8"))
    return slug, meta, sections, terms


def qa(slug, sections):
    problems, pairs, terms = [], 0, 0
    for sec in sections:
        if "id" not in sec:
            problems.append("%s: 章节缺少 id" % slug)
        for b in sec.get("blocks", []):
            if b.get("type") == "pair":
                pairs += 1
                if not b.get("en") or not b.get("zh"):
                    problems.append("[%s/%s] pair 缺少 en 或 zh" % (slug, sec.get("id")))
            for key in ("zh", "en", "lead", "html"):
                s = b.get(key)
                if not isinstance(s, str):
                    continue
                if s.count("[[") != s.count("]]"):
                    problems.append("[%s/%s] [[ ]] 不配对: %s" % (slug, sec.get("id"), s[:50]))
                terms += s.count("[[")
                for m in re.finditer(r"\[\[([^\]|]*)\|([^\]]*)\]\]", s):
                    if not m.group(1).strip() or not m.group(2).strip():
                        problems.append("[%s/%s] 空术语: %s" % (slug, sec.get("id"), m.group(0)[:40]))
                if key in ("zh", "lead") and '"' in s:
                    problems.append("[%s/%s] 中文里用了英文双引号，会破坏 data-tip，请改用 「」"
                                    % (slug, sec.get("id")))
    return problems, pairs, terms


def copy_assets(slug, folder):
    src = os.path.join(folder, "img")
    dst = os.path.join(ASSETS, slug)
    if not os.path.isdir(src):
        return 0
    os.makedirs(dst, exist_ok=True)
    n = 0
    for f in glob.glob(os.path.join(src, "*")):
        if os.path.isfile(f):
            shutil.copy2(f, os.path.join(dst, os.path.basename(f)))
            n += 1
    return n


def build_shelf(slug2id):
    """书架 = papers/manifest.json 里的条目（已译/待译）+ 未登记但已有译本的论文。"""
    mp = os.path.join(BASE, "papers", "manifest.json")
    manifest = {}
    if os.path.exists(mp):
        manifest = json.load(open(mp, encoding="utf-8"))
    items, listed = [], set()
    for it in manifest.get("items", []):
        arxiv = (it.get("arxiv") or "").strip()
        slug = it.get("slug") or ""
        pid = slug2id.get(slug)
        # PDF 文件名：优先用条目自带的 pdf 字段（非 arXiv 论文，如 GPT-2），否则用 arXiv 号
        pdfname = (it.get("pdf") or "").strip() or (arxiv + ".pdf" if arxiv else "")
        pdf = os.path.join(BASE, "papers", pdfname) if pdfname else ""
        has_pdf = bool(pdfname) and os.path.exists(pdf)
        if not pid and not has_pdf and it.get("optional"):
            continue
        if pid:
            listed.add(pid)
        items.append({
            "arxiv": arxiv,
            "id": pid or "",
            "slug": slug,
            "group": it.get("group") or "",
            "titleEn": it.get("titleEn") or "",
            "titleZh": it.get("titleZh") or "",
            "status": "ready" if pid else "todo",
            "pdf": ("../papers/" + pdfname) if has_pdf else "",
            "note": it.get("note") or "",
        })
    for slug, pid in sorted(slug2id.items()):
        if pid in listed:
            continue
        items.append({"arxiv": "", "id": pid, "slug": slug, "group": "",
                      "titleEn": "", "titleZh": "", "status": "ready", "pdf": "", "note": ""})
    return {"groups": manifest.get("groups", []), "items": items}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    public = "--public" in sys.argv
    only = args[0] if args else None
    folders = [f for f in sorted(glob.glob(os.path.join(DATA, "*"))) if os.path.isdir(f)]
    if only:
        folders = [f for f in folders if os.path.basename(f) == only]
    if public:
        # 只打包可公开的内容（示例论文）；论文正文与译文只留本地
        folders = [f for f in folders if os.path.basename(f) == "demo"]
    if not folders:
        raise SystemExit("data/ 下没有论文目录")

    papers, total_bad = [], 0
    slug2id, folder_of = {}, {}
    for folder in folders:
        slug, meta, sections, terms = load_paper(folder)
        problems, pairs, n_terms = qa(slug, sections)
        total_bad += len(problems)
        for p in problems:
            print("  ! " + p)
        n_img = copy_assets(meta["id"], folder)
        refs = meta.get("references", [])
        print("%-28s 章节 %2d · 对照段 %3d · 术语 %2d · 英译表 %2d · 文献 %2d · 图 %d"
              % (slug, len(sections), pairs, n_terms, len(terms), len(refs), n_img))
        slug2id[slug] = meta["id"]
        folder_of[meta["id"]] = slug
        papers.append({"id": meta["id"], "meta": meta["meta"],
                       "sections": sections, "glossary": meta.get("glossary", []),
                       "termEn": terms, "references": refs})

    shelf = build_shelf(slug2id)

    js = ("/* 双语论文阅读器 · 论文库\n"
          " * 由 build_paper.py 自动生成，请勿手改。\n"
          " * 数据格式见 reader/FORMAT.md\n"
          " */\nwindow.PAPERS = " + json.dumps(papers, ensure_ascii=False, indent=1) + ";\n"
          "\n/* 书架：papers/manifest.json + 已有的译本 */\n"
          "window.SHELF = " + json.dumps(shelf, ensure_ascii=False, indent=1) + ";\n")
    os.makedirs(os.path.dirname(OUT_JS), exist_ok=True)
    open(OUT_JS, "w", encoding="utf-8").write(js)
    print("已生成 %s（%.0f KB，共 %d 篇；书架 %d 本，其中已译 %d）"
          % (OUT_JS, os.path.getsize(OUT_JS) / 1024, len(papers), len(shelf["items"]),
             sum(1 for i in shelf["items"] if i["status"] == "ready")))
    if total_bad:
        print("注意：有 %d 处格式问题，已在上方标出" % total_bad)
        sys.exit(1)


if __name__ == "__main__":
    main()

