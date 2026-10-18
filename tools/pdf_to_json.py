"""
把英文论文 PDF 抽成「待翻译」的数据骨架，供 reader 使用。

用法:
    python tools/pdf_to_json.py paper.pdf my-paper

产物:
    data/my-paper/00-meta.json     元信息（titleZh 等需要人工/AI 填）
    data/my-paper/01-....json      按检测到的章节切分，每段一个 pair，zh 为空
    data/my-paper/img/*.png        论文里的位图

之后：把每个 "zh": "" 翻译成中文（术语用 [[术语|解释]]），再跑 build_paper.py。

已知限制：双栏 PDF 已做列序修正，但表格与公式往往会被拆碎，需要人工重整；
矢量图不会导出（需自行截图后放进 img/）。
"""
import os
import re
import sys
import json

try:
    import pymupdf
except ImportError:
    sys.exit("需要 pymupdf：pip install pymupdf")

NUM_HEAD = re.compile(r"^(\d{1,2}(?:\.\d{1,2}){0,3})\.?\s+([A-Z][^.]{2,70})$")
KNOWN = ("Abstract", "Introduction", "Background", "Conclusion", "References",
         "Acknowledgements", "Appendix", "Related Work", "Experiments", "Results",
         "Discussion", "Training", "Model Architecture", "Attention Visualizations")


def page_blocks(page):
    """按阅读顺序返回段落：先判断是否双栏，再按 (列, y) 排序。"""
    blocks = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        lines, maxsz, bold = [], 0.0, False
        for line in b.get("lines", []):
            lines.append("".join(s["text"] for s in line["spans"]))
            for s in line["spans"]:
                maxsz = max(maxsz, s["size"])
                bold = bold or ("Bold" in s["font"] or "Semibold" in s["font"])
        text = " ".join(lines)
        text = re.sub(r"-\s+", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) < 2:
            continue
        blocks.append({"text": text, "size": round(maxsz, 1), "bold": bold,
                       "x0": b["bbox"][0], "y0": b["bbox"][1]})

    mid = page.rect.width / 2
    left = [b for b in blocks if b["x0"] < mid - 20]
    right = [b for b in blocks if b["x0"] >= mid - 20]
    two_col = len(right) >= 3 and len(left) >= 3 and \
        max((b["x0"] for b in left), default=0) < mid and min((b["x0"] for b in right), default=1e9) > mid - 20
    if two_col:
        blocks.sort(key=lambda b: (0 if b["x0"] < mid else 1, b["y0"]))
    else:
        blocks.sort(key=lambda b: b["y0"])
    return blocks


def detect(pdf_path):
    doc = pymupdf.open(pdf_path)
    per_page = [page_blocks(p) for p in doc]
    sizes = {}
    for blocks in per_page:
        for b in blocks:
            sizes[b["size"]] = sizes.get(b["size"], 0) + len(b["text"])
    body = max(sizes, key=sizes.get) if sizes else 10.0
    return per_page, body


def heading_of(b, body):
    t = b["text"]
    if len(t) > 90:
        return None
    m = NUM_HEAD.match(t)
    if m:
        return m.group(1), m.group(2).strip()
    if t.strip() in KNOWN:
        return "", t.strip()
    if b["size"] >= body * 1.25 and not b["bold"] and len(t) < 80:
        return "", t
    if b["size"] >= body * 1.45 and len(t) < 120:
        return "", t
    return None


def build(pdf_path):
    per_page, body = detect(pdf_path)
    sections, cur = [], None
    for pno, blocks in enumerate(per_page, start=1):
        for b in blocks:
            h = heading_of(b, body)
            if h is not None:
                num, title = h
                cur = {"id": "s%d" % (len(sections) + 1), "num": num, "title": title,
                       "titleEn": title, "page": "原文 p.%d" % pno, "lead": "", "blocks": []}
                sections.append(cur)
                continue
            if cur is None:
                cur = {"id": "s0", "num": "", "title": "front matter", "titleEn": "",
                       "page": "原文 p.%d" % pno, "lead": "", "blocks": []}
                sections.append(cur)
            cur["blocks"].append({"type": "pair", "en": b["text"], "zh": ""})
    return sections, body


def slugify(title, fallback):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", title).strip("-").lower()
    return (s[:28] or fallback)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    pdf_path, slug = sys.argv[1], sys.argv[2]
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outdir = os.path.join(base, "data", slug)
    os.makedirs(os.path.join(outdir, "img"), exist_ok=True)

    sections, body = build(pdf_path)
    meta = {
        "id": slug,
        "meta": {
            "title": os.path.splitext(os.path.basename(pdf_path))[0],
            "titleZh": "", "authors": "", "affil": "", "venue": "",
            "blurb": "", "chips": [],
            "source": os.path.basename(pdf_path),
            "note": "本文为非官方中文译本，仅供学习。"
        },
        "glossary": []
    }
    with open(os.path.join(outdir, "00-meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    for i, sec in enumerate(sections):
        name = "%02d-%s.json" % (i + 1, slugify(sec["title"], "section"))
        with open(os.path.join(outdir, name), "w", encoding="utf-8") as f:
            json.dump(sec, f, ensure_ascii=False, indent=2)

    doc = pymupdf.open(pdf_path)
    n = 0
    for pno, page in enumerate(doc, start=1):
        for img in page.get_images(full=True):
            try:
                pix = pymupdf.Pixmap(doc, img[0])
                if pix.width < 160 or pix.height < 90:
                    continue
                n += 1
                pix.save(os.path.join(outdir, "img", "fig-%02d-%d.png" % (pno, n)))
            except Exception:
                pass

    words = sum(len(b.get("en", "").split()) for s in sections for b in s["blocks"])
    print("生成 %d 节 / %d 段 / 约 %d 词 → %s" % (len(sections), sum(len(s["blocks"]) for s in sections), words, outdir))
    print("正文基准字号 %.1f，导出位图 %d 张" % (body, n))
    print("下一步：翻译每个 zh 字段（术语用 [[词|解释]]），然后 python build_paper.py %s" % slug)


if __name__ == "__main__":
    main()
