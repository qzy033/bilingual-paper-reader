"""
从 PDF 末尾的参考文献列表自动生成 data/<slug>/00-meta.json 的 references 数组。

用法:
    python tools/refs_from_pdf.py <pdf> <slug> [--dry]

做什么:
    1. 全文扫描「行首 [1] …」或「行首 1. Author…」，按编号 1,2,3… 连成最长的一段；
    2. 把折行拼回一条（保留连字符，压缩空白）；
    3. 条目里出现 arXiv:2104.09864 或 doi:… 的，顺手生成 url；
    4. 合并进 00-meta.json（已有编号不覆盖，只补缺）。

为什么值得做：正文里的 [13]、[38, 24, 15] 会自动变成可悬停的引用浮窗，
但前提是 references 里有对应编号。手抄几十条太费事，这个脚本能一次补齐。

注意：作者-年份制（如 LLaMA、Chinchilla 的 (Brown et al., 2020)）没有编号，
脚本会直接报「没找到」，这是正常的——那类论文本来就不该有 [n] 链接。
"""
import json
import os
import re
import sys

try:
    import pymupdf
except ImportError:
    sys.exit("需要 pymupdf：pip install pymupdf")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRACKET = re.compile(r"^\s*\[(\d{1,3})\]\s*(.*)$")
PLAIN = re.compile(r"^\s*(\d{1,3})\.\s+(.{10,})$")
ARXIV = re.compile(r"arXiv[:\s]*(\d{4}\.\d{4,5})(v\d+)?", re.I)
DOI = re.compile(r"(?:doi[:\s]*|https?://doi\.org/)(10\.\d{4,9}/[^\s,;]+)", re.I)


def runs(lines, rx):
    """把「行首编号 1,2,3…」的连续段找出来，返回最长的那个。"""
    best, cur = [], []
    for line in lines:
        m = rx.match(line)
        if m and int(m.group(1)) == len(cur) + 1:
            cur.append([int(m.group(1)), m.group(2).strip()])
        elif m and int(m.group(1)) == 1:
            if len(cur) > len(best):
                best = cur
            cur = [[1, m.group(2).strip()]]
        elif cur:
            # 续行：拼到上一条；遇到明显的章节标题就断
            s = line.strip()
            if not s:
                continue
            if re.match(r"^(Appendix|A\s+[A-Z][a-z]+|[A-Z]\s+[A-Z])", s) and len(cur[-1][1]) > 60:
                if len(cur) > len(best):
                    best = cur
                cur = []
                continue
            cur[-1][1] += " " + s
        else:
            continue
    if len(cur) > len(best):
        best = cur
    return best


def clean(entries):
    out = []
    for n, t in entries:
        t = re.sub(r"\s+", " ", t).strip()
        t = re.sub(r"-\s+(?=[a-z])", "-", t)
        if len(t) < 12:
            continue
        out.append((n, t))
    return out


def looks_like_refs(entries):
    """参考文献条目几乎都带年份；表格里的「1. xxx」不会。"""
    if not entries:
        return False
    with_year = sum(1 for _, t in entries if re.search(r"\b(19|20)\d{2}\b", t))
    return with_year >= max(3, len(entries) * 0.6)


def url_of(t):
    m = ARXIV.search(t)
    if m:
        return "https://arxiv.org/abs/" + m.group(1) + (m.group(2) or "")
    m = DOI.search(t)
    if m:
        return "https://doi.org/" + m.group(1).rstrip(".")
    return ""


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    pdf, slug = sys.argv[1], sys.argv[2]
    dry = "--dry" in sys.argv
    meta_path = os.path.join(BASE, "data", slug, "00-meta.json")
    if not os.path.exists(meta_path):
        sys.exit("没有 %s（先建好 meta 再补文献）" % meta_path)

    doc = pymupdf.open(pdf)
    lines = []
    for page in doc:
        lines.extend(page.get_text("text").splitlines())

    entries = clean(runs(lines, BRACKET))
    if len(entries) < 8 or not looks_like_refs(entries):
        alt = clean(runs(lines, PLAIN))
        if len(alt) > len(entries) and looks_like_refs(alt):
            entries = alt
    if len(entries) < 5 or not looks_like_refs(entries):
        sys.exit("没找到成串的编号参考文献（%d 条）——这个 PDF 可能是作者-年份制，跳过即可"
                 % len(entries))

    meta = json.load(open(meta_path, encoding="utf-8"))
    have = {r["n"] for r in meta.get("references", []) if isinstance(r.get("n"), int)}
    added = [{"n": n, "text": t, "url": url_of(t)} for n, t in entries if n not in have]
    refs = meta.get("references", []) + added
    refs.sort(key=lambda r: r["n"])
    meta["references"] = refs

    print("%s：解析到 %d 条，新增 %d 条，共 %d 条（带链接 %d 条）"
          % (slug, len(entries), len(added), len(refs), sum(1 for r in refs if r.get("url"))))
    for r in added[:3]:
        print("  [%d] %s%s" % (r["n"], r["text"][:90], ("  → " + r["url"]) if r["url"] else ""))
    if len(added) > 3:
        print("  … 其余略")
    if not dry:
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("已写入 " + meta_path)


if __name__ == "__main__":
    main()
