# 论文数据格式说明（FORMAT.md）

这份文件写给**人**，也写给**以后要接手翻译的 AI**。
照着它，就能把一个 PDF 论文变成这个阅读器里「左原文、右译文、术语可点」的读物。

---

## 0. 一分钟看懂

- **阅读器**：`reader/index.html`，纯静态单文件，双击即可用，不需要服务器。
- **一篇论文** = `data/<目录名>/` 下的一堆 JSON（一节一个文件）。
- **行内术语** = `[[术语|解释]]`，渲染成带虚线的词，悬停/点击弹出解释。
- **构建** = `python build_paper.py`，把 `data/` 下所有论文打包成 `reader/papers/library.js`。

```
out/attention-zh/
├─ reader/
│  ├─ index.html                阅读器本体（样式 + 渲染 + 交互）
│  ├─ FORMAT.md                 本文件
│  ├─ papers/library.js         构建产物：所有论文的 JSON（自动生成，勿手改）
│  └─ assets/<论文id>/*.png     构建产物：插图（自动复制）
├─ data/
│  └─ attention/                一篇论文
│     ├─ 00-meta.json           元信息 + 术语表
│     ├─ 01-abstract.json       第 0 节（摘要）
│     ├─ 02-intro.json          …按文件名顺序拼接
│     ├─ …
│     ├─ terms.json             中文术语 → 英文原文（点译文时高亮原文用，可省）
│     └─ img/*.png              插图源文件
├─ tools/pdf_to_json.py         把 PDF 抽成待翻译的骨架
└─ build_paper.py               构建 + 校验
```

---

## 1. 加一篇新论文（三步）

```bash
# 1) 抽取 PDF 文本，生成待翻译骨架（会自动分节）
python tools/pdf_to_json.py "C:\path\to\paper.pdf" my-paper

# 2) 翻译：把 data/my-paper/*.json 里每个 "zh": "" 填上中文
#    术语用 [[术语|解释]]，导读写在 section 的 "lead"

# 3) 构建（会顺带校验格式问题）
python build_paper.py
```

然后刷新 `reader/index.html`，左侧「论文库」里就会多出一本。

> 只想临时看一篇？也可以把单篇 JSON 直接**拖进浏览器窗口**，或点左侧「导入论文数据」，
> 阅读器会用 localStorage 记住它（不写入磁盘）。

---

## 2. 顶层结构

`00-meta.json` 决定这一篇的「封面」和术语表；其余每个 JSON 是一个 section。

```json
{
  "id": "attention-is-all-you-need",
  "meta": {
    "title": "Attention Is All You Need",
    "titleZh": "注意力就是你所需要的一切",
    "authors": "Ashish Vaswani, Noam Shazeer, …",
    "affil": "Google Brain · Google Research · University of Toronto",
    "venue": "第 31 届神经信息处理系统大会（NIPS 2017）· arXiv:1706.03762v7",
    "blurb": "<b>一句话：</b>不用循环、不用卷积……",
    "chips": ["2017 · NIPS", "机器翻译", "Transformer"],
    "source": "arXiv:1706.03762v7",
    "note": "译本说明（可省，会显示在文末版权区）"
  },
  "glossary": [
    ["attention", "注意力机制", "解释文字，可含 [[术语|解释]] 吗？—— 这里不要再嵌套。"]
  ],
  "references": [
    { "n": 38, "text": "Yonghui Wu, … Google's neural machine translation system …, 2016.",
      "url": "https://arxiv.org/abs/1609.08144" }
  ]
}
```

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | ✅ | 唯一标识，用于 localStorage（阅读进度、生词本）。建议等于目录名 |
| `meta.title` | ✅ | 英文标题 |
| `meta.titleZh` | | 中文标题 |
| `meta.authors` `meta.affil` `meta.venue` | | 封面信息，纯文本 |
| `meta.blurb` | | 封面的一句话介绍，**允许 HTML**（如 `<b>`） |
| `meta.chips` | | 封面小标签，字符串数组 |
| `meta.source` `meta.note` | | 文末出处与译本说明 |
| `glossary` | | `[英文, 中文, 解释]` 三元组数组，出现在文末「术语表」和侧栏抽屉里 |
| `references` | | 文献数组，见下 |

### 2.1 `references`：正文 `[n]` 的浮窗数据

```json
{ "n": 13,
  "text": "Sepp Hochreiter and Jürgen Schmidhuber. Long short-term memory. Neural computation, 9(8):1735–1780, 1997.",
  "url": "" }
```

- `n` 是正文里 `[13]` 的编号（整数，或能直接对应 `data-ref` 的字符串）；
- `text` 直接显示在浮窗里，也是「Google 学术」的检索词；建议**照原文录入**，不要改写成中文；
- `url` 可留空：有 arXiv/DOI 就填，浮窗里会出现「打开原文 ↗」；空则只给学术搜索；
- 正文里凡是 `[13]`、`[38, 24, 15]` 这种写法，**中英文两栏都会自动变成链接**，
  悬停出浮窗、点击固定，无需在文本里手写链接；
- 文末的文献列表由 `refs` 块自动生成（见 4.8），并从 `references` 取数据。

> 编号必须与正文一致；`[i]`、`[a]` 之类非数字、或编号不在 `references` 里的方括号会被原样保留。
> 自己写 `[1]` 时必须确认它真的是文献引用，否则会被误连。

---

## 3. Section（每一节一个文件）

文件名决定顺序（`01-`、`02-`…），`id` 是锚点。

```json
{
  "id": "s32",
  "num": "3.2",
  "title": "注意力机制",
  "titleEn": "Attention",
  "page": "原文 p.3–5",
  "lead": "导读：一两句话告诉读者这一节要干什么、要注意什么。",
  "blocks": [ … ]
}
```

| 字段 | 说明 |
|---|---|
| `num` | 章节号，显示成左侧大数字（可以是 `"3.2"`、`"A"`、`"R"`） |
| `title` / `titleEn` | 中英标题 |
| `page` | 原文页码，方便对照 PDF（可省） |
| `lead` | 节前的「导读」框，用高中能懂的话写 1–3 句 |

---

## 4. Block 类型（`blocks` 数组里的元素）

### 4.1 `pair` — 对照段落（主力，占 90%）

```json
{ "type": "pair",
  "en": "The dominant sequence transduction models are based on …",
  "zh": "目前占主导地位的[[序列转换模型|把一条序列整体变换成另一条序列的任务统称。]]，都建立在……" }
```

- 左栏 `en`、右栏 `zh`，逐句/短段对齐，**一行一事**：不要把整节塞进一个 pair。
- 两栏都支持行内术语标记与基本 HTML（`<b>` `<i>` `<sub>` `<sup>`）。
- 一个字符串里用**空行**（JSON 里的 `\n\n`）分隔多个自然段。
- 若字符串以 `<ul`、`<ol`、`<div`、`<p`、`<table`、`<blockquote` 开头，会被原样当作 HTML 块插入。

### 4.2 `sub` — 小节标题（3.2.1 这种）

```json
{ "type": "sub", "num": "3.2.1", "id": "s321",
  "zh": "缩放点积注意力", "en": "Scaled Dot-Product Attention" }
```

会同时出现在左侧目录里（缩进一级）。

### 4.3 `eq` — 公式（等宽高亮块）

```json
{ "type": "eq", "no": "(1)",
  "html": "Attention(Q, K, V) = softmax( <span class='frac'><span class='q'>QK<sup>T</sup></span><span class='d'>√<span class='var'>d</span><sub>k</sub></span></span> ) V" }
```

- `html` 里**属性一律用单引号**（JSON 字符串里的双引号会被转义，容易出错）。
- 分式用 `.frac > .q / .d`；变量用 `<span class='var'>` 表示斜体。
- 公式块不接受行内术语标记。

### 4.4 `fig` — 插图

```json
{ "type": "fig", "src": "assets/attention-is-all-you-need/fig1.png",
  "size": "s", "label": "图 1", "alt": "Transformer model architecture",
  "zh": "中文图注（可含 [[术语|解释]]）",
  "en": "Figure 1: The Transformer - model architecture.",
  "labels": [["Inputs", "输入（源语言句子）"], ["Add & Norm", "残差相加 + 层归一化"]] }
```

- 图片放在 `data/<目录>/img/`，构建时复制到 `reader/assets/<meta.id>/`，
  所以 `src` 写 `assets/<meta.id>/文件名.png`。
- `size`：`s`（小图，约 340px）/ `m`（中图 700px）/ `full`（满宽）。默认 `full`。
- `labels` 是可选的「图中英文 → 中文」对照表，**对翻译的图特别有用**。

### 4.5 `table` — 表格

```json
{ "type": "table",
  "html": "<caption><b>表 1</b> 说明文字。</caption><table><thead><tr><th>…</th></tr></thead><tbody>…</tbody></table>" }
```

- 整张表用 HTML 写，`<caption>` 里放中英表题。
- 属性用单引号；表头可写成「中文 English」双语。
- 表格样式（斑马纹、数字对齐）由阅读器统一提供。

### 4.6 `note` — 脚注 / 作者注 / 译者注

```json
{ "type": "note", "label": "脚注 4",
  "html": "中文译文……",
  "en": "To illustrate why the dot products get large, …" }
```

- `en` 可选，会以灰色斜体显示在下方，保留原文。
- 标签自己定：`作者注 ∗`、`脚注 5`、`译者注`。
- 原文内部有矛盾、单位不一致、明显笔误时，**用「译者注」标出来**，不要悄悄改数字。

### 4.7 `raw` — 任意 HTML 块（兜底）

```json
{ "type": "raw", "html": "<div class='lead'><b>这个公式在说什么</b>……</div>" }
```

用来放「白话解读」框（`class="lead"`）、参考文献列表等不想走对照排版的内容。

### 4.8 `refs` — 参考文献列表

```json
{ "type": "refs" }
```

- 从 `references`（见 2.1）自动生成 `<ol>`，每条带 `id="ref-38"` 与「arXiv ↗」外链；
- 正文里的 `[38]` 点「文献列表」即可跳到这里并高亮该条；
- 若论文没有 `references` 数据，可在块里给 `"html"`，会原样渲染。

---

## 5. 行内语法 `[[术语|解释]]`

```
…用[[注意力机制|让模型回头「看」上下文所有位置，按相关程度加权取信息。]]把编码器和解码器连起来。
```

规则（踩过坑，务必遵守）：

1. 术语里**不能有** `|`，解释里**不能有** `]]`。
2. 解释里可以放 `<b>` `<i>` `<sub>` `<sup>` `<br>` 等 HTML；**不要用英文双引号**
   （会截断 `data-tip` 属性），中文引号用 `「」`。
3. 若解释以 `<b>` 开头，阅读器不再自动加术语名；否则会**自动补上术语名**作为标题。
4. 解释卡右下角有「＋ 加入生词本」，所以解释要**能独立读懂**，别只写「见 3.2 节」。
5. 同一个术语不必每次都标；**首次出现**标一次，重复出现交给文末术语表。
6. 点中文术语时，阅读器会去**左边的英文原文里把对应英文词高亮**。对应关系来自同目录的
   `terms.json`（见第 5.1 节）；没有对应项时不报错，只是不高亮。

### 5.1 `terms.json`：中文术语 → 英文原文

```json
{
  "注意力机制": "attention mechanism",
  "多头注意力": "Multi-head attention||multi-head attention",
  "当前最佳": "state of the art||state-of-the-art"
}
```

- 键 = `[[` 后面那个中文词（**必须逐字相同**）；
- 值 = 该中文词在**同一段英文原文里实际出现的字符串**（大小写不敏感）；
  多种写法用 `||` 分隔，命中第一个就停；
- 匹配时会自动加词边界（`attention` 不会命中 `attention-weighted` 里的片段）；
- 同一段里找不到时，会往上找 2 段再试；仍找不到就静默跳过。

写这个映射的粗暴但有效的办法：先猜英文，再跑一遍校验——把每个中文词所在 pair 的 `en`
和映射值对比，命中率应接近 100%。本项目 71 处术语中 70 处命中，剩下 1 处在参考文献的
中文按语里（那段没有对应英文），属正常。

---

## 6. 翻译写作规范

这些不是格式要求，是这个项目「好读」的原因，续写时请保持：

- **先直觉，后定义**。解释先打一个生活化的比方（查字典、时钟、抄写），再给严谨说法。
- **一屏 1–2 条解释**。术语太密集会打断阅读；宁可少标、留给术语表。
- **首次出现给英文原文**，例如「注意力机制（attention）」，后文只用中文。
- **数字、公式、表格数据一律照原文**；单位、编号不要「顺手改漂亮」。
- **导读**写「这一节要解决什么、读的时候注意什么」，不要复述内容。
- 原文有口误/笔误（本论文 6.1 节的 41.0 与摘要的 41.8 就是），加**译者注**，保留原文。
- 参考文献保持英文原文，便于按标题检索。

---

## 7. 校验

`python build_paper.py` 会检查并打印：

```
attention    章节 14 · 对照段 122 · 术语 72 · 英译表 64 · 图 5
已生成 …/reader/papers/library.js（108 KB，共 1 篇）
```

出现 `!` 行说明有问题（`[[ ]]` 不配对、pair 缺 `en`/`zh`、中文里混入英文双引号等），
脚本会以退出码 1 结束，建议修完再交付。

---

## 8. 给 AI 的提示词模板

> 你在为一个「中英对照论文阅读器」准备数据。请阅读 `reader/FORMAT.md`，然后：
>
> 1. 用 `tools/pdf_to_json.py <pdf> <slug>` 生成骨架；
> 2. 逐节翻译 `data/<slug>/*.json` 里的 `"zh"` 字段，保持**逐句对齐**（一句原文一行 pair，
>    长段落拆成 2–4 行，行内中英必须同指一事）；
> 3. 对每个**首次出现的专业术语**加 `[[术语|解释]]`，解释要让没有背景的读者也能懂：先比方、再定义，
>    1–3 句，不写「见某节」；
> 4. 同时写 `data/<slug>/terms.json`：中文术语 → 该词在英文原句里的**实际字符串**，
>    多个写法用 `||` 分隔；写完逐条核对能在这段 `en` 里找到（命中率应接近 100%），
>    这样读者点中文词时原文才会亮；
> 5. 建 `references` 数组（`n` / `text` / `url`）并照录原文；正文里的 `[n]` **不要手写链接**，
>    阅读器会自动把中英两栏的方括号编号变成可悬停的引用；
> 6. 每节写 1–2 句 `lead` 导读；公式后加 `raw` 的「这个公式在说什么」白话解读；
> 7. 表格用 HTML 写进 `table` 块，表头双语；插图用 `fig` 块，附 `labels` 中英对照；
> 8. 原文有矛盾或笔误时加 `note` 块「译者注」，不要私自改数字；
> 9. 文献小节放一个 `{"type":"refs"}` 块即可；
> 10. 跑 `python build_paper.py`，把 `!` 全部修掉。
>
> 风格参照 `data/attention/`（Attention Is All You Need 的成稿）。

---

## 9. 常见问题

| 现象 | 原因 / 处理 |
|---|---|
| 插图不显示 | `src` 必须写成 `assets/<meta.id>/xxx.png`，且图片放在 `data/<目录>/img/`；改完重跑构建 |
| 左侧没有新论文 | 没跑 `build_paper.py`，或 `index.html` 里引用的不是 `papers/library.js` |
| 术语悬停没反应 | 检查 `[[` `]]` 是否配对、解释里是否混进了英文双引号 |
| 点中文术语，原文没高亮 | 该词不在 `terms.json` 里，或值在该段 `en` 中找不到（大小写/单复数/连字符要一致） |
| 正文 `[12]` 没有变成链接 | 编号不在 `references` 里，或写成了全角 `［12］` |
| 浮窗里没有「打开原文」 | 该条 `url` 为空；补上 DOI/arXiv 链接即可，其余条目仍可用学术搜索 |
| 文献列表为空 | 没有 `{"type":"refs"}` 块，或 `references` 数组为空 |
| 中文变方块 | 系统缺 `Noto Serif SC`，回退到宋体；Windows 自带宋体，一般没问题 |
| 打印排版乱 | 打印时侧栏/工具条自动隐藏，正文按两栏输出；如需 A4 请用 Chrome 打印 |
| 生词本丢了 | 清浏览器数据会清空；重要内容用「导出为 Markdown」保存 |
