"""
严格校验一篇论文的数据（比 build_paper.py 的检查更细），给翻译的人自查用。

用法:
    python tools/check_paper.py <slug>

只读，不改任何文件。退出码 0 = 全部通过；1 = 有 E（必须修）；有 W 不影响构建但建议看。
"""
import glob
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

TERM = re.compile(r"\[\[([^\]|]*)\|([^\]]*)\]\]")
CJK = re.compile(r"[\u4e00-\u9fff]")


def cjk_count(s):
    return len(CJK.findall(s))


def ascii_ratio(s):
    letters = [c for c in s if c.isalpha() or c == " "]
    if not letters:
        return 0.0
    return sum(1 for c in letters if ord(c) < 128) / len(letters)


def strip_marks(s):
    return TERM.sub(lambda m: m.group(1), s)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    slug = sys.argv[1]
    folder = os.path.join(DATA, slug)
    if not os.path.isdir(folder):
        sys.exit("没有目录: " + folder)

    E, W, I = [], [], []
    files = sorted(glob.glob(os.path.join(folder, "*.json")))
    files = [f for f in files if os.path.basename(f) != "terms.json"]
    if len(files) < 2:
        sys.exit("E 只有 %d 个 JSON，至少要有 00-meta.json + 1 个 section" % len(files))

    meta = json.load(open(files[0], encoding="utf-8"))
    m = meta.get("meta", {})
    if not meta.get("id"):
        E.append("00-meta.json 缺 id")
    if meta.get("id") != slug:
        W.append("meta.id=%r 与目录名 %r 不一致（构建时以 id 为准，localStorage 也按 id 存）"
                 % (meta.get("id"), slug))
    for k in ("title", "titleZh", "authors", "affil", "venue", "blurb"):
        if not (m.get(k) or "").strip():
            E.append("meta.%s 为空" % k)
    if len(m.get("chips") or []) < 2:
        W.append("meta.chips 少于 2 个")
    gl = meta.get("glossary") or []
    if len(gl) < 6:
        W.append("glossary 只有 %d 条（建议 ≥ 8）" % len(gl))
    for g in gl:
        if not (isinstance(g, list) and len(g) == 3 and all(isinstance(x, str) and x.strip() for x in g)):
            E.append("glossary 条目格式不对: %r" % (g,))
    refs = meta.get("references") or []
    refs_missing = False
    if refs:
        nums = set()
        for r in refs:
            if not isinstance(r.get("n"), int):
                E.append("references 的 n 必须是整数: %r" % (r,))
            elif r["n"] in nums:
                E.append("references 编号重复: %r" % r["n"])
            else:
                nums.add(r["n"])
            if not (r.get("text") or "").strip():
                E.append("references[%r].text 为空" % r.get("n"))
    else:
        refs_missing = True

    sections, ids, pairs, notes, tables, figs, eqs, terms_all = [], set(), 0, 0, 0, 0, 0, 0
    zh_chars, en_words = 0, 0
    for f in files[1:]:
        name = os.path.basename(f)
        try:
            sec = json.load(open(f, encoding="utf-8"))
        except Exception as e:
            E.append("%s 不是合法 JSON: %s" % (name, e))
            continue
        if "blocks" not in sec:
            E.append("%s 没有 blocks" % name)
            continue
        sid = sec.get("id") or ""
        if not sid:
            E.append("%s 缺 id" % name)
        elif sid in ids:
            E.append("%s 的 id 重复: %s" % (name, sid))
        else:
            ids.add(sid)
        if not (sec.get("title") or "").strip():
            E.append("%s 缺 title" % name)
        if not (sec.get("titleEn") or "").strip():
            W.append("%s 缺 titleEn" % name)
        if not (sec.get("num") or "").strip():
            W.append("%s 缺 num" % name)
        lead = sec.get("lead") or ""
        if len(lead) < 12:
            E.append("%s 的 lead 太短/为空（导读至少一句话）" % name)
        elif '"' in lead:
            E.append("%s 的 lead 里有英文双引号，请用 「」" % name)
        if "page" not in sec:
            W.append("%s 缺 page（原文页码）" % name)
        sections.append((name, sec))

        for bi, b in enumerate(sec["blocks"]):
            t = b.get("type")
            where = "%s#%d(%s)" % (name, bi, t)
            if t == "pair":
                pairs += 1
                en, zh = b.get("en") or "", b.get("zh") or ""
                if not en.strip():
                    E.append("%s 缺 en" % where)
                if not zh.strip():
                    E.append("%s 缺 zh（没翻译）" % where)
                    continue
                if en.count("[[") != en.count("]]") or zh.count("[[") != zh.count("]]"):
                    E.append("%s [[ ]] 不配对" % where)
                for mm in TERM.finditer(zh):
                    terms_all += 1
                    if not mm.group(1).strip() or not mm.group(2).strip():
                        E.append("%s 空术语: %s" % (where, mm.group(0)[:40]))
                    if '"' in mm.group(2):
                        E.append("%s 术语解释里用了英文双引号（会截断 data-tip）: %s"
                                 % (where, mm.group(1)))
                    if "]]" in mm.group(2):
                        E.append("%s 术语解释里出现 ]]（会提前截断）: %s" % (where, mm.group(1)))
                if '"' in zh:
                    E.append("%s zh 里有英文双引号，请用 「」" % where)
                body = strip_marks(zh)
                n_en, n_zh = len(en.split()), cjk_count(body)
                zh_chars += n_zh
                en_words += n_en
                if n_en >= 6 and n_zh < n_en * 0.45:
                    E.append("%s 中文明显过短（英 %d 词 / 中 %d 字），像是没译完或漏译"
                             % (where, n_en, n_zh))
                if n_zh >= 40 and ascii_ratio(body) > 0.68:
                    E.append("%s 中文里英文占比过高（%.0f%%），像原文没译"
                             % (where, ascii_ratio(body) * 100))
                if re.search(r"[a-z]{4,} [a-z]{4,} [a-z]{4,} [a-z]{4,} [a-z]{4,}", body) and n_zh < 20:
                    E.append("%s 像是整段英文留在 zh 里" % where)
            elif t == "note":
                notes += 1
                if not (b.get("html") or "").strip():
                    E.append("%s 缺 html" % where)
            elif t == "table":
                tables += 1
                h = b.get("html") or ""
                if "<table" not in h:
                    E.append("%s 缺 <table>" % where)
                if "<caption" not in h:
                    W.append("%s 缺 <caption>（中英表题）" % where)
                if '"' in h:
                    W.append("%s 表格 HTML 里用了双引号，建议单引号" % where)
            elif t == "fig":
                figs += 1
                src = b.get("src") or ""
                if not src.startswith("assets/%s/" % meta.get("id")):
                    E.append("%s src 必须是 assets/%s/xxx.png，实际 %r" % (where, meta.get("id"), src))
                img = os.path.join(folder, "img", os.path.basename(src))
                if not os.path.exists(img):
                    E.append("%s 图片不存在: %s" % (where, img))
                if not (b.get("zh") or "").strip():
                    E.append("%s 缺中文图注" % where)
            elif t == "eq":
                eqs += 1
                h = b.get("html") or ""
                if not h.strip():
                    E.append("%s 缺 html" % where)
                if '"' in h:
                    E.append("%s 公式 html 里用了双引号，改成单引号" % where)
            elif t == "sub":
                pass
            elif t in ("refs", "raw"):
                pass
            else:
                E.append("%s 未知 block 类型" % where)

    # 只有正文真的用了 [n] 编号引用，才要求 references（作者-年份制论文不需要）
    if refs_missing:
        cited = [b for _name, sec in sections for b in sec["blocks"]
                 if re.search(r"\[\d+(?:\s*,\s*\d+)*\]", b.get("en") or "")]
        if cited:
            W.append("正文有 %d 处 [n] 引用但没有 references 数组（不会变链接）" % len(cited))

    # terms.json 命中率
    terms = {}
    tp = os.path.join(folder, "terms.json")
    if os.path.exists(tp):
        terms = json.load(open(tp, encoding="utf-8"))
    elif terms_all:
        W.append("有 %d 处术语但没有 terms.json（点中文不会高亮原文）" % terms_all)
    if terms:
        seen = set()
        for name, sec in sections:
            for b in sec["blocks"]:
                zh, en = b.get("zh") or "", (b.get("en") or "")
                for mm in TERM.finditer(zh):
                    seen.add(mm.group(1).strip())
        missing = sorted(k for k in terms if k not in seen)
        if missing:
            W.append("terms.json 里这些键没在 [[…]] 出现过: %s" % "、".join(missing[:8]))
        hit = miss = 0
        miss_list = []
        for name, sec in sections:
            blocks = sec["blocks"]
            for bi, b in enumerate(blocks):
                zh = b.get("zh") or ""
                # 与 reader 的查找规则一致：本段优先，找不到时往上找 2 段
                window = " ".join((blocks[j].get("en") or "")
                                  for j in range(max(0, bi - 2), bi + 1))
                for mm in TERM.finditer(zh):
                    key = mm.group(1).strip()
                    val = terms.get(key)
                    if not val:
                        miss += 1
                        miss_list.append("%s(无映射)" % name)
                        continue
                    found = False
                    for cand in str(val).split("||"):
                        if cand.strip() and cand.strip().lower() in window.lower():
                            found = True
                            break
                    if found:
                        hit += 1
                    else:
                        miss += 1
                        miss_list.append("%s/%s" % (name, key))
        total = hit + miss
        if total:
            rate = hit / total
            I.append("terms.json 原文命中率 %.0f%%（%d/%d）" % (rate * 100, hit, total))
            if rate < 0.9:
                W.append("命中率偏低，这些没在本段英文里找到: %s" % "、".join(miss_list[:10]))

    I.append("%d 节 · %d 对照段 · %d 注 · %d 表 · %d 图 · %d 公式 · %d 术语 · 英 %d 词 / 中 %d 字"
             % (len(sections), pairs, notes, tables, figs, eqs, terms_all, en_words, zh_chars))

    for line in E:
        print("E " + line)
    for line in W:
        print("W " + line)
    for line in I:
        print("· " + line)
    if E:
        print("\n共 %d 个 E（必须修）、%d 个 W" % (len(E), len(W)))
        sys.exit(1)
    print("\n通过：0 个 E、%d 个 W" % len(W))


if __name__ == "__main__":
    main()
