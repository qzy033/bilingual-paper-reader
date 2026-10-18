#!/usr/bin/env python3
"""
把 data/<slug>/ 里空着的 "zh" 字段交给大模型翻译，并可选地生成术语表。

用法:
    export OPENAI_API_KEY=sk-...                       # 或 Azure/兼容网关的 key
    export OPENAI_BASE_URL=https://api.openai.com/v1   # 可选，任何 OpenAI 兼容端点
    export MODEL=gpt-4o-mini                           # 可选

    python tools/translate.py --slug my-paper                  # 只填充空的 zh
    python tools/translate.py --slug my-paper --force          # 重译已有译文
    python tools/translate.py --slug my-paper --with-terms     # 同时生成 terms.json
    python tools/translate.py --slug my-paper --dry-run        # 只统计，不发请求

设计上的几条约束：
  * 逐段翻译，严格保持与 en 一一对应（行内不能合并、不能拆开）；
  * 编号引用 [12]、公式、单位、数字一律原样保留；
  * 术语默认不硬塞进译文，需要时用 --with-terms 单独生成映射表，
    且**只有在英文原句里找得到**的才写入 terms.json（否则读者点词会高亮不到）。
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

SYSTEM = (
    "你是一名技术论文译者，把英文学术论文逐段译成简体中文。要求：\n"
    "1. 忠实、通顺，面向高中及以上读者；不添加原文没有的内容，不省略信息。\n"
    "2. 专业术语首次出现时在中文后用括号保留英文，例如：注意力机制（attention）。\n"
    "3. 保留所有编号引用（如 [12]、[3, 5]）、公式符号、数字、单位、变量名，原样不动。\n"
    "4. 不翻译人名、机构名、模型名、数据集名。\n"
    "5. 只输出一个 JSON 数组，元素是与输入逐条对应的译文，不要任何解释或 Markdown 代码块。"
)

TERM_SYSTEM = (
    "你正在为一个中英对照阅读器整理术语表。给定若干组「英文原句 / 中文译文」，"
    "找出其中值得解释的专业术语，输出一个 JSON 对象：键是中文术语（与译文中的写法完全一致），"
    "值是该术语在原句里对应的英文原文（必须是原句中连续出现的字符串，大小写随意）。"
    "每条只取 3-6 个最重要的术语；不要输出解释，不要输出任何额外文字。"
)


# ---------------------------------------------------------------- HTTP
def chat(messages, model, api_base, api_key, temperature=0.2, timeout=180):
    url = api_base.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "temperature": temperature,
        "messages": messages,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def parse_json_block(text):
    """从模型输出里抠出 JSON（容忍 ```json 代码块和前后废话）。"""
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
        json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    )


def clean_translation(s):
    """去掉模型偶尔加上的「译文：」前缀和多余引号。"""
    s = str(s).strip()
    s = re.sub(r"^(译文|中文|翻译)\s*[:：]\s*", "", s)
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"“”":
        s = s[1:-1]
    return s.strip()


def translate_texts(texts, args):
    numbered = "\n".join("%d. %s" % (i + 1, t) for i, t in enumerate(texts))
    user = "把下面 %d 段英文逐条译成中文，输出长度为 %d 的 JSON 数组：\n\n%s" % (
        len(texts), len(texts), numbered)
    raw = with_retry(lambda: chat(
        [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
        args.model, args.api_base, args.api_key, args.temperature))
    arr = parse_json_block(raw)
    if not isinstance(arr, list) or len(arr) != len(texts):
        raise ValueError("返回条数不符：期望 %d，得到 %s" % (
            len(texts), len(arr) if isinstance(arr, list) else type(arr).__name__))
    return [clean_translation(x) for x in arr]


# ---------------------------------------------------------------- 主流程
def collect(slug, force):
    sections = load_sections(slug)
    jobs = []  # (path, section, block_key, block, index)
    for path, sec in sections:
        if sec.get("lead") is not None and not sec.get("lead"):
            jobs.append((path, sec, "lead", sec, None))
        for i, b in enumerate(sec.get("blocks", [])):
            if b.get("type") != "pair":
                continue
            if force or not b.get("zh"):
                jobs.append((path, sec, "zh", b, i))
    return sections, jobs


def run_translate(slug, args):
    sections, jobs = collect(slug, args.force)
    print("待译 %d 段（批量 %d）" % (len(jobs), args.batch))
    if args.dry_run or not jobs:
        return sections

    done = 0
    for start in range(0, len(jobs), args.batch):
        chunk = jobs[start:start + args.batch]
        texts = [j[3]["en"] if j[2] == "zh" else j[3]["lead"] for j in chunk]
        # 空 en 跳过
        idx = [k for k, t in enumerate(texts) if t and t.strip()]
        if not idx:
            continue
        try:
            outs = translate_texts([texts[k] for k in idx], args)
        except Exception as e:  # noqa: BLE001
            print("  [批量失败，改为逐条] %s" % e)
            outs = []
            for k in idx:
                try:
                    outs.append(translate_texts([texts[k]], args)[0])
                except Exception as e2:  # noqa: BLE001
                    print("  [跳过] %s: %s" % (texts[k][:40], e2))
                    outs.append("")
        for pos, k in enumerate(idx):
            path, sec, key, block, _ = chunk[k]
            if key == "lead":
                sec["lead"] = outs[pos]
            else:
                block["zh"] = outs[pos]
            done += 1
        for path in sorted({j[0] for j in chunk}):
            sec = [s for p, s in sections if p == path][0]
            save(path, sec)
        print("  完成 %d/%d" % (done, len(jobs)))
    return sections


def build_terms(slug, sections, args):
    """从译文里的 [[术语|解释]] 反查英文，只保留能在同段 en 中找到的。"""
    pairs = []
    for _, sec in sections:
        for b in sec.get("blocks", []):
            if b.get("type") != "pair":
                continue
            labels = re.findall(r"\[\[([^\]|]+)\|", b.get("zh", ""))
            if labels:
                pairs.append((b.get("en", ""), b.get("zh", ""), labels))
    if not pairs:
        print("译文里没有 [[术语|解释]] 标记，跳过术语表")
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
                 {"role": "user", "content": user}],
                args.model, args.api_base, args.api_key, 0))
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
            # 校验：这个中文标签确实出现在某段译文里，英文确实出现在对应原句里
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
    print("术语表：%d 条（新增 %d）→ %s" % (len(old), len(terms), path))
    return old


def main():
    ap = argparse.ArgumentParser(description="用大模型翻译 data/<slug> 下的论文数据")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--model", default=os.environ.get("MODEL", "gpt-4o-mini"))
    ap.add_argument("--api-base", default=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    ap.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", ""))
    ap.add_argument("--batch", type=int, default=6)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--force", action="store_true", help="重译已有译文")
    ap.add_argument("--with-terms", action="store_true", help="同时生成 terms.json")
    ap.add_argument("--dry-run", action="store_true", help="只统计待译段落")
    args = ap.parse_args()

    if not args.dry_run and not args.api_key:
        sys.exit("缺少 OPENAI_API_KEY；先用 --dry-run 看要翻多少段")

    sections = run_translate(args.slug, args)
    if args.with_terms and not args.dry_run:
        build_terms(args.slug, sections, args)
    print("完成。下一步：python build_paper.py")


if __name__ == "__main__":
    main()
