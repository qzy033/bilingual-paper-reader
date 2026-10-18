# 论文数据目录

每一篇论文是一个子目录，比如 `data/demo/`。每个子目录里的文件：

```
00-meta.json      元信息 + 术语表 + 参考文献数组
01-….json         第 0 节（按文件名顺序拼接）
02-….json         第 1 节
terms.json        中文术语 → 英文原文（点中文时高亮原文用，可省）
img/              插图（fig 块的 src 写 assets/<id>/文件名）
```

生成方式见仓库根目录的 `README.md`，字段说明见 `../reader/FORMAT.md`。

## 这个目录里为什么只有 demo

`.gitignore` 里写了：

```
data/*
!data/demo/
!data/README.md
```

也就是说：**你后来加的论文默认不会进 git**。这是有意的。

把一篇已发表论文的全文译文公开上传，涉及复制权与翻译权；arXiv 默认的
[非独占分发许可](https://arxiv.org/licenses/nonexclusive-distrib/1.0/) 并不授权转载或翻译。
具体判断依据写在仓库根目录的 [NOTICE.md](../NOTICE.md)。

所以推荐的工作方式是：

1. 在自己电脑上用 `tools/pdf_to_json.py` 抽取；
2. 翻译、构建、阅读——都在本地；
3. 只有当论文明确是 CC BY / CC0 / 公有领域时，才考虑把它提交到公开仓库
   （提交前把 `.gitignore` 里对应的一行放开）。

想备份自己的译本？可以另建一个**私有**仓库，或者用别的私有方式存。
