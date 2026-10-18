# 翻译工作流（WORKFLOW.md）——给接手的 AI

这份文件是**操作手册**：怎么把 `papers/` 里的一篇 PDF 变成书架上一本「中英对照精读」。
数据格式本身见 `FORMAT.md`；这里讲流程、范围、验收标准和红线。

成品标准 = 已有的 `data/attention/`、`data/chinchilla/`、`data/llama/`。
动手前请至少通读其中一篇（推荐 `data/chinchilla/05-scaling.json`，看密度和语气）。

---

## 1. 范围：一篇论文要译到什么程度

| 级别 | 判据 | 要求 |
|---|---|---|
| **A（≤ 35 页）** | 如 RoPE、DPO、Mixtral、vLLM、YaRN、DeepSeekMoE | **全文逐句**：摘要→结论→附录，一节不落；参考文献条目保持英文原样但建 `references` 数组 |
| **B（> 35 页）** | Llama 3（92 页）、DeepSeek-R1（86 页）、InstructGPT（68 页）、FlashAttention（34 页，按 A 做） | **主文逐句**（摘要到结论/讨论）+ **附录结构化**：每张表重建成 HTML（表题、表头中英、数字照抄）、每段附录文字给 1–3 句中文摘要、建一页「附录索引」导航；不要逐字翻译几十页的 prompt 原文 |

判断依据是**信息密度**不是页数：附录若全是表格与 prompt，用表格 + 索引比逐字翻译有用得多。
做不到全文时，**在 `00-meta.json` 的 `note` 里写清楚哪部分做了摘要**——不要假装译完了。

---

## 2. 工作循环（每篇照做）

```bash
cd out/attention-zh

# ① 渲染页面图（每页一张 PNG + 一份同页文本）
python tools/pdf_pages.py papers/2305.18290.pdf dpo 130

# ② 逐页看图翻译。先读 p01.png 确认标题/作者/摘要，再按节推进：
#    读图 → 抄英文（逐字）→ 写中文 → 立刻落盘成 data/dpo/NN-xxx.json

# ③ 每写完 2–3 节自查一次
python tools/check_paper.py dpo

# ④ 全部写完，0 个 E 才算完成
```

**为什么看图**：双栏 + 公式 + 表格用 `get_text()` 抽出来会串行、公式变碎片。
页面图里位置、上下标、表头都在，抄写和翻译不会错。

写文件用 `write`/`edit` 工具（UTF-8，`ensure_ascii=False` 风格的中文原文即可，JSON 直接写中文）。
一次写一节，**不要**先攒一大段再落盘——中途失败会白干。

---

## 3. 文件规划

```
data/dpo/
├─ 00-meta.json        封面 + glossary + references（先写，它是全篇的定译表）
├─ 01-abstract.json    摘要（num 可为 "0" 或 ""）
├─ 02-intro.json       …
├─ 03-method.json      …
├─ 90-appendix-a.json  附录放 90+，与正文分开
├─ 99-references.json  {"blocks":[{"type":"refs"}]}
├─ terms.json          中文术语 → 英文原串
└─ img/fig1.png        图（crop.py 裁出）
```

- section 的 `id` 用 `s1`、`s2`…（唯一即可）；`num` 用论文章节号；`lead` 必写。
- `page` 写**印刷页码**（图上页脚那个数字），没有就用 PDF 页序，写成 `"原文 p.3"`。
- 附录多时每节拆开（`90-appendix-a`、`91-appendix-b`），别塞进一个巨型文件。

---

## 4. 精细写法（这是「精读」和「机翻」的区别）

### 4.1 `pair`：一句一行，中英同指一事

- 英文栏**逐字照抄**（可修正 PDF 断词 `-` 与多余空格；**不许**改写、缩写、合并句子）。
- 一句一对最稳。长句（> 45 词）允许拆成 2 行，但两栏必须在同一处断开，
  即 `en` 前半对 `zh` 前半、`en` 后半对 `zh` 后半。
- 原文的列表（`(1) … (2) …`、`•`）逐条做成 pair，不要压成一段。
- 引用编号 `[13]`、`[38, 24, 15]` 原样保留，阅读器会自己变链接。
- 中文里不要出现英文双引号 `"`（会截断 `data-tip`），一律用「」。

### 4.2 `[[术语|解释]]`：全篇最重要的密度控制

- **只标首次出现**，一节 3–8 个，全篇 25–60 个；宁可少标。
- 解释 1–3 句，**先比方后定义**，能独立读懂，不写「见 3.2 节」。
- 解释里可用 `<b>`：`[[对比学习|把「相似的放近、不相似的推远」……]]`。
- 同一概念换说法时，挑最自然的中文做键，并在 `terms.json` 里给出英文原串。

### 4.3 `eq`：公式照抄，再讲人话

- 用 `eq` 块照抄公式（`html` 里属性一律单引号；分式 `.frac > .q/.d`；变量 `<span class='var'>`）。
- **每个关键公式后面跟一个 `raw` 白话框**：

```json
{"type":"raw","html":"<div class='lead'><b>这个公式在说什么</b>它把……换句话说，……</div>"}
```

- 符号第一次出现时用 `note` 说明（如「σ 是 logistic 函数，把任意实数压到 0–1」）。

### 4.4 `table`：重建，别截图

```json
{"type":"table","html":"<caption><b>表 2</b> 不同 β 下的胜率（Win rate %）。</caption>
<table><thead><tr><th>数据集 Dataset</th><th>β=0.1</th></tr></thead><tbody><tr><td>……</td><td>…</td></tr></tbody></table>"}
```

- 数字**逐格照抄**，单位留在表头；不确定的格子写 `—`，不要猜。
- 表题中英双语；表头「中文 English」。
- 表后加 `note`（label 写「读表提示」）说明这张表该看哪一列、结论是什么。
  这是「精读」的加分项，别省。
- 超过 25 行的长表：全表照录，但只翻译表头与关键列，并在 `note` 里说明取舍。

### 4.5 `fig`：裁图 + 中英标签

```bash
python tools/crop.py find papers/2305.18290.pdf 4      # 看这页有哪些图形块与坐标
python tools/crop.py crop papers/2305.18290.pdf 4 100,80,510,300 data/dpo/img/fig1.png 3
```

```json
{"type":"fig","src":"assets/dpo/fig1.png","size":"m","label":"图 1",
 "alt":"…","zh":"图 1：中文图注。","en":"Figure 1: …",
 "labels":[["English label","中文"],["…","…"]]}
```

- 先 `find` 再 `crop`；裁完用 `read_image` 看一眼，别把正文裁进去。
- `labels` 是图上英文单词的中文对照，**对翻译的图特别有用**，尽量给全。
- 相片类图 zoom 用 2，线稿/架构图用 3–4。

### 4.6 `note`：脚注、作者注、译者注

- 原文脚注 → `{"type":"note","label":"脚注 3","html":"译文…","en":"原文…"}`。
- 原文**自相矛盾**（数字对不上、口径含糊、明显笔误）→ `label` 写「译者注」，
  说明矛盾在哪、为什么、按哪个理解读。**绝不悄悄改数字**。

### 4.7 `sub` / `refs` / 参考文献

- 3.2.1 这类小节用 `sub` 块（会进左侧目录）。
- 文末一个 `{"type":"refs"}` 块，条目来自 `00-meta.json` 的 `references`。
- `references` 至少覆盖正文出现过的编号；`text` 照原文录英文，`url` 有 arXiv/DOI 就填。

---

## 5. 语言与体例

- 中文用全角标点；英文词与中文之间加空格（`使用 Transformer 架构`）。
- 数字、单位、模型名、数据集名**保持原文**（`7B`、`GSM8k`、`pass@1`）。
- 语气：讲清楚「为什么这么做、这数说明什么」，少用「众所周知」。
- 全篇译名统一，靠 `00-meta.json` 的 `glossary` 定死（先写它）。

---

## 6. 红线和禁令

1. **不要跑 `python build_paper.py`**——它会重写全库 `reader/papers/library.js`，
   多篇同时跑会互相覆盖。构建由主控在汇总时统一做。
2. 只改自己那一个 `data/<slug>/` 目录；不要动别的论文、`reader/`、`tools/`、`PROGRESS.md`。
3. 不要 `git` 任何操作。
4. `en` 栏不许改写原文；不确定的英文词宁可留原文，也不要「顺手修正」。
5. 表格/数字不许编造；缺数据写 `—` 并在 `note` 里说明。
6. 不要删 `_pages/`（主控最后统一清理），也不要把它写进 meta。

---

## 7. 验收清单

```bash
python tools/check_paper.py <slug>     # 必须 0 个 E
```

逐项确认：

- [ ] `00-meta.json`：title/titleZh/authors/affil/venue/blurb/chips 齐全；`glossary` ≥ 8 条；`references` 齐
- [ ] 每一节都有 `lead`（一句话导读，不复述正文）
- [ ] `pair` 无空 `zh`；中英一一对应；无英文双引号
- [ ] 术语 ≥ 25 处（长文），解释能独立读懂
- [ ] `terms.json` 命中率 ≥ 90%（checker 会打印）
- [ ] 每张表都重建了，且有「读表提示」
- [ ] 每张图都裁了，`src` 是 `assets/<id>/…`，有 `labels`
- [ ] 公式有白话解读；符号有说明
- [ ] 原文矛盾处有「译者注」
- [ ] 附录按第 1 节的范围要求处理，缺口写进 `meta.note`
- [ ] **没有**动 `build_paper.py`、`git`、其他目录

---

## 8. 交回给主控的报告（简短即可）

```
论文：Direct Preference Optimization（2305.18290）
目录：data/dpo/   级别：A（全文）
统计：12 节 · 96 对照段 · 6 表 · 2 图 · 5 公式 · 41 术语 · 英 4200 词 / 中 6100 字
check：0 E / 2 W（W：terms.json 2 处映射找不到，已注明）
缺口：附录 C 的推导只给了结论（公式 12–15 未逐行展开）
```

不要贴大段译文进来——文件就在磁盘上，主控会自己看。
