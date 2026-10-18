#!/usr/bin/env python3
"""
把 data/<slug>/ 里的英文内容交给大模型翻译成中文，并可自动加术语标记、生成术语表。

用法:
    export OPENAI_API_KEY=sk-...                       # 或 Azure / 兼容网关的 key
    export OPENAI_BASE_URL=https://api.openai.com/v1   # 可选，任何 OpenAI 兼容端点
    export MODEL=gpt-4o-mini                           # 可选

    python tools/translate.py --slug my-paper                  # 翻译（只填空着的字段）
    python tools/translate.py --slug my-paper --force          # 重译
    python tools/translate.py --slug my-paper --annotate       # 再给译文加 [[术语|解释]] 标记
    python tools/translate.py --slug my-paper --with-terms     # 由标记反查英文，生成 terms.json
    python tools/translate.py --slug my-paper --dry-run        # 只统计，不发请求

翻译哪些字段：
    section.title   小节标题（抽出来的 PDF 原本是英文，会一并译成中文）
    section.lead    每节导读（空着才翻，手写过的不动）
    pair.zh         中英对照的右栏正文           ← 主要工作量
    sub.zh          子小节标题（如 3.2.1）
    fig.zh          图注（有 fig.en 时才翻）
不翻译：en 原文、表格 html 里的数字、参考文献、note 块（脚注/译者注通常手写）。
"""
import argparse
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {"00-meta.json", "terms.json"}
CJK = re.compile(r"[\u4e00-\u9fff]")

SYSTEM = (
    "你是一名技术论文译者，把英文学术论文逐段译成简体中文。要求：\n"
    "1. 忠实、通顺，面向非专业读者；不添加原文没有的内容，不省略信息。\n"
    "2. 专业术语首次出现时在中文后用括号保留英文，例如：注意力机制（attention）。\n"
    "3. 保留所有编号引用（如 [12]、[3, 5]）、公式符号、数字、单位、变量名，原样不动。\n"
    "4. 不翻译人名、机构名、模型名、数据集名。\n"
    "5. 只输出一个 JSON 数组，元素是与输入逐条对应的译文，不要任何解释或 Markdown 代码块。"
)

ANNOTATE_SYSTEM = (
    "你在为一份中英对照读物做术语标注。给你一段中文译文，"
    "请挑出 2-5 个值得解释的专业术语，用 [[术语|解释]] 的形式就地包起来。要求：\n"
    "1. 术语必须是译文里**原样出现的连续子串**；解释 1-2 句、面向非专业读者，可用「」引号和逗号，不要用英文双引号。\n"
    "2. 只加标记，不要改写、增删、调序任何原文；不要加 Markdown、不要加解释性句子。\n"
    "3. 不要标记人名、机构名、模型名、数字。\n"
    "4. 直接输出加好标记的整段文字，不要任何前后缀。"
)

TERM_SYSTEM = (
    "你正在为一个中英对照阅读器整理术语表。给定若干组「英文原句 / 中文译文」，"
    "找出其中值得解释的专业术语，输出一个 JSON 对象：键是中文术语（与译文中的写法完全一致），"
    "值是该术语在原句里对应的英文原文（必须是原句中连续出现的字符串，大小写随意）。"
    "每条只取 3-6 个最重要的术语；不要输出解释，不要输出任何额外文字。"
)


# ---------------------------------------------------------------- HTTP
def chat(messages, args, temperature=0.2, timeout=180):
    url = args.api_base.rstrip("/") + "/chat/completions"
    payload = {"model": args.model, "temperature": temperature, "messages": messages}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + args.api_key},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def parse_json_block(text):
    t = text.strip()
    t = re.sub(r"^```[a-zA-Z]*\s*", "", t)
    t = re.sub(r"\s*```$", "", t)
    try:
        return json.loads(t)
    except Exception:
        pass
    m = re.search(r"(\[.*\]|\{.*\})", t, re.S)
    if m:
        return json.loads(m.group(1))
    raise ValueError("模型没有返回可解析的 JSON：" + text[:200])


def with_retry(fn, tries=3, wait=3):
    last = None
    for i in range(tries):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            last = e
            if i < tries - 1:
                time.sleep(wait * (i + 1))
    raise last


# ---------------------------------------------------------------- 数据
def load_sections(slug):
    folder = os.path.join(BASE, "data", slug)
    if not os.path.isdir(folder):
        sys.exit("找不到 data/%s" % slug)
    out = []
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".json") or name in SKIP:
            continue
        path = os.path.join(folder, name)
        out.append((path, json.load(io.open(path, encoding="utf-8"))))
    if not out:
        sys.exit("data/%s 里没有节文件" % slug)
    return out


def save(path, data):
    io.open(path, "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def clean_translation(s):
    s = str(s).strip()
    s = re.sub(r"^(译文|中文|翻译)\s*[:：]\s*", "", s)
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"“”":
        s = s[1:-1]
    return s.strip()


def strip_marks(s):
    """把 [[术语|解释]] 还原成「术语」，用于校验模型没有改写内容。"""
    return re.sub(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", r"\1", s or "")


# ---------------------------------------------------------------- 收集任务
def collect(slug, force):
    sections = load_sections(slug)
    jobs = []  # (path, sec, kind, block, en_text)

    def need(cur):
        return force or not cur

    for path, sec in sections:
        title = sec.get("title") or ""
        if title and not CJK.search(title):        # 还是英文标题
            jobs.append((path, sec, "title", sec, title))
        for b in sec.get("blocks", []):
            t = b.get("type")
            if t == "pair" and need(b.get("zh")):
                jobs.append((path, sec, "pair", b, b.get("en", "")))
            elif t == "sub" and b.get("en") and need(b.get("zh")):
                jobs.append((path, sec, "sub", b, b["en"]))
            elif t == "fig" and b.get("en") and need(b.get("zh")):
                jobs.append((path, sec, "fig", b, b["en"]))
    return sections, jobs


# ---------------------------------------------------------------- 翻译
LEAD_SYSTEM = (
    "你在为一篇中英对照的论文读物写「导读」。给定一节的小标题和开头几句英文，"
    "用 1-2 句中文告诉读者：这一节要解决什么、读的时候该注意什么。\n"
    "要求：不超过 60 字；不要复述原文；不要用英文双引号（用「」）；不要任何前后缀。"
)


def translate_batch(texts, args):
    numbered = "\n".join("%d. %s" % (i + 1, t) for i, t in enumerate(texts))
    user = "把下面 %d 段英文逐条译成中文，输出长度为 %d 的 JSON 数组：\n\n%s" % (
        len(texts), len(texts), numbered)
    raw = with_retry(lambda: chat(
        [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}], args))
    arr = parse_json_block(raw)
    if not isinstance(arr, list) or len(arr) != len(texts):
        raise ValueError("返回条数不符：期望 %d，得到 %s" % (
            len(texts), len(arr) if isinstance(arr, list) else type(arr).__name__))
    return [clean_translation(x) for x in arr]


def write_lead(sec, args):
    opening = [b.get("en", "") for b in sec.get("blocks", [])
               if b.get("type") == "pair" and b.get("en")]
    ctx = "\n\n".join(opening[:2])[:1200]
    user = "小标题：%s\n开头原文：\n%s" % (sec.get("title") or sec.get("titleEn") or "", ctx)
    raw = with_retry(lambda: chat(
        [{"role": "system", "content": LEAD_SYSTEM}, {"role": "user", "content": user}], args, 0.4))
    return clean_translation(raw.replace("```", "").strip())


def run_translate(slug, args):
    sections, jobs = collect(slug, args.force)
    counts = {}
    for j in jobs:
        counts[j[2]] = counts.get(j[2], 0) + 1
    leads = [s for _, s in sections if not s.get("lead")]
    counts["lead"] = len(leads)
    print("待处理 %d 项：%s" % (
        len(jobs) + len(leads), "、".join("%s %d" % kv for kv in sorted(counts.items())) or "无"))
    if args.dry_run:
        return sections

    done = 0
    for start in range(0, len(jobs), args.batch):
        chunk = [j for j in jobs[start:start + args.batch] if j[4] and j[4].strip()]
        if not chunk:
            continue
        outs = {}
        idx = list(range(len(chunk)))
        try:
            outs = dict(zip(idx, translate_batch([j[4] for j in chunk], args)))
        except Exception as e:  # noqa: BLE001
            print("  [批量失败，改为逐条] %s" % e)
            for k, j in enumerate(chunk):
                try:
                    outs[k] = translate_batch([j[4]], args)[0]
                except Exception as e2:  # noqa: BLE001
                    print("  [跳过] %s: %s" % (j[4][:40], e2))
                    outs[k] = ""
        for k, j in enumerate(chunk):
            path, sec, kind, block, _en = j
            zh = outs.get(k, "")
            if kind == "title":
                sec["titleEn"] = sec.get("titleEn") or sec.get("title")
                sec["title"] = zh or sec["title"]
            else:
                block["zh"] = zh
            done += 1
        for path in sorted({j[0] for j in chunk}):
            sec = [s for p, s in sections if p == path][0]
            save(path, sec)
        print("  进度 %d/%d" % (done, len(jobs)))

    if leads:
        print("写导读 %d 节" % len(leads))
        for sec in leads:
            try:
                sec["lead"] = write_lead(sec, args)
            except Exception as e:  # noqa: BLE001
                print("  [导读跳过] %s" % e)
                continue
            for path, s in sections:
                if s is sec:
                    save(path, sec)
    return sections


# ---------------------------------------------------------------- 术语标记
def annotate(sections, args):
    """给译文插入 [[术语|解释]]，并用「去掉标记后内容不变」来拒绝模型改写。"""
    targets = []
    for path, sec in sections:
        for b in sec.get("blocks", []):
            if b.get("type") == "pair" and b.get("zh") and "[[" not in b["zh"]:
                targets.append((path, sec, b))
    print("待标注 %d 段" % len(targets))
    if args.dry_run or not targets:
        return 0

    ok = 0
    for i, (path, sec, b) in enumerate(targets):
        user = "原句（英文）：%s\n\n待标注的译文（中文）：\n%s" % (b.get("en", "")[:800], b["zh"])
        try:
            raw = with_retry(lambda: chat(
                [{"role": "system", "content": ANNOTATE_SYSTEM},
                 {"role": "user", "content": user}], args, 0.3), tries=2)
        except Exception as e:  # noqa: BLE001
            print("  [标注失败] %s" % e)
            continue
        cand = raw.strip()
        cand = re.sub(r"^```[a-zA-Z]*\s*", "", cand)
        cand = re.sub(r"\s*```$", "", cand).strip()
        # 校验：去掉标记后必须与原文一致，且至少 1 个合法标记
        if not cand or "[[" not in cand:
            continue
        if re.sub(r"\s+", "", strip_marks(cand)) != re.sub(r"\s+", "", b["zh"]):
            continue
        if not re.search(r"\[\[[^\[\]|]+\|[^\]]+\]\]", cand):
            continue
        b["zh"] = cand
        save(path, sec)
        ok += 1
        if (i + 1) % 5 == 0:
            print("  已标注 %d/%d" % (i + 1, len(targets)))
    print("标注成功 %d/%d" % (ok, len(targets)))
    return ok


# ---------------------------------------------------------------- 术语表
def build_terms(slug, sections, args):
    pairs = []
    for _, sec in sections:
        for b in sec.get("blocks", []):
            if b.get("type") != "pair":
                continue
            labels = re.findall(r"\[\[([^\]|]+)\|", b.get("zh", ""))
            if labels:
                pairs.append((b.get("en", ""), b.get("zh", ""), labels))
    if not pairs:
        print("译文里没有 [[术语|解释]] 标记；先跑 --annotate")
        return {}
    if args.dry_run:
        print("待建术语表的段落 %d 段" % len(pairs))
        return {}

    terms = {}
    chunk_size = 6
    for start in range(0, len(pairs), chunk_size):
        chunk = pairs[start:start + chunk_size]
        body = "\n\n".join(
            "【%d】\nEN: %s\nZH: %s\n候选中文术语: %s" % (
                i + 1, en[:1200], zh[:1200], "、".join(sorted(set(labels))))
            for i, (en, zh, labels) in enumerate(chunk))
        user = "为下面每组找出候选术语对应的英文原文：\n\n" + body + \
               "\n\n输出 JSON 对象（中文术语 → 英文原文）。"
        try:
            raw = with_retry(lambda: chat(
                [{"role": "system", "content": TERM_SYSTEM},
                 {"role": "user", "content": user}], args, 0), tries=2)
            obj = parse_json_block(raw)
        except Exception as e:  # noqa: BLE001
            print("  [术语跳过] %s" % e)
            continue
        if not isinstance(obj, dict):
            continue
        for zh_label, en_text in obj.items():
            if not isinstance(en_text, str):
                continue
            zh_label, en_text = zh_label.strip(), en_text.strip()
            for en, zh, labels in chunk:
                if zh_label in labels and en_text.lower() in en.lower():
                    terms.setdefault(zh_label, en_text)
                    break

    path = os.path.join(BASE, "data", slug, "terms.json")
    old = {}
    if os.path.exists(path):
        old = json.load(io.open(path, encoding="utf-8"))
    old.update(terms)
    io.open(path, "w", encoding="utf-8").write(
        json.dumps(old, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print("术语表：%d 条（新增 %d）→ data/%s/terms.json" % (len(old), len(terms), slug))
    return old


def main():
    ap = argparse.ArgumentParser(description="用大模型翻译 data/<slug> 下的论文数据")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--model", default=os.environ.get("MODEL", "gpt-4o-mini"))
    ap.add_argument("--api-base", default=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    ap.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", ""))
    ap.add_argument("--batch", type=int, default=6, help="每次请求带几段（默认 6）")
    ap.add_argument("--force", action="store_true", help="重译已有译文")
    ap.add_argument("--annotate", action="store_true", help="给译文加 [[术语|解释]] 标记")
    ap.add_argument("--with-terms", action="store_true", help="由标记生成 terms.json")
    ap.add_argument("--dry-run", action="store_true", help="只统计，不发请求")
    args = ap.parse_args()

    if not args.dry_run and not args.api_key:
        sys.exit("缺少 OPENAI_API_KEY；先用 --dry-run 看要翻多少段")

    sections = run_translate(args.slug, args)
    if args.annotate:
        annotate(sections, args)
    if args.with_terms:
        build_terms(args.slug, sections, args)
    print("完成。下一步：python build_paper.py" + ("" if args.with_terms else "（想要术语表再加 --with-terms）"))


if __name__ == "__main__":
    main()
