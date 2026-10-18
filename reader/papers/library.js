/* 双语论文阅读器 · 论文库
 * 由 build_paper.py 自动生成，请勿手改。
 * 数据格式见 reader/FORMAT.md
 */
window.PAPERS = [
 {
  "id": "demo-attention-primer",
  "meta": {
   "title": "How Attention Works: A One-Page Primer",
   "titleZh": "注意力是怎么工作的：一页入门",
   "authors": "Demo Author (this repository)",
   "affil": "示例论文 · 全部文字由本项目原创撰写",
   "venue": "演示文档，非真实论文 · 2026",
   "blurb": "<b>这是示例书：</b>正文、译文、术语解释、引用浮窗全部可交互，用来演示阅读器的每一项功能；内容为本项目原创，可直接 fork 修改。",
   "chips": [
    "示例 / demo",
    "注意力机制",
    "12 段对照",
    "CC0 内容"
   ],
   "source": "原创演示文本（非任何已发表论文）",
   "note": "本示例的文字与插图由本项目原创，以 CC0-1.0 释出，可自由使用；其中提到的两篇论文仅为书目引用。"
  },
  "sections": [
   {
    "id": "s0",
    "num": "0",
    "title": "摘要",
    "titleEn": "Abstract",
    "page": "示例 p.1",
    "lead": "这是一本示例书：正文、译文、术语、文献浮窗都是真的，只是内容由本项目原创，用来演示阅读器怎么用。",
    "blocks": [
     {
      "type": "pair",
      "en": "An attention layer lets every token in a sentence look at every other token, score how relevant each one is, and pull in a weighted mixture of their information. This note explains the idea with as little notation as possible.",
      "zh": "注意力层让句子里的每个[[词元|token：模型处理的最小单位，可能是一个词、一个子词片段，甚至一个字符。]]都能「看」到其他所有词元，给每个词元的相关程度打分，再按权重把它们的信息混合进来。这篇短文用尽量少的数学符号把这个想法讲清楚。"
     },
     {
      "type": "pair",
      "en": "Nothing here is new: the mechanism described below is scaled dot-product attention, introduced for machine translation in 2017 [1]. Every sentence in this note was written for this demo.",
      "zh": "这里没有提出任何新东西：下面描述的机制就是 2017 年为机器翻译提出的缩放点积注意力[1]。本文的每一句话都是为这个演示专门写的。"
     }
    ]
   },
   {
    "id": "s1",
    "num": "1",
    "title": "给每个词打分",
    "titleEn": "Scoring Tokens",
    "page": "示例 p.1",
    "lead": "这一节只有三句话，是全文的骨架：三个角色、一个分数、一次加权求和。",
    "blocks": [
     {
      "type": "pair",
      "en": "Each token is first projected into three vectors: a query, a key and a value. Think of the query as a question, the key as the label on a drawer, and the value as what is inside the drawer.",
      "zh": "每个词元先被[[投影|projected：乘一个矩阵，把向量变换到另一个空间，相当于换一套坐标描述同一件事。]]成三个向量：[[查询|query：这个位置「想找什么」。]]、[[键|key：这个位置「有什么」。]]和[[值|value：这个位置真正交出去的内容。]]。可以把查询想成一个问题，键想成抽屉上的标签，值想成抽屉里的东西。"
     },
     {
      "type": "pair",
      "en": "The score between two tokens is the dot product of one token's query with the other token's key. A higher score means the two are more relevant to each other under the current projection.",
      "zh": "两个词元之间的分数，就是一个词元的查询与另一个词元的键的[[点积|dot product：对应分量相乘再相加，得到一个数，衡量两个向量有多「合拍」。]]。分数越高，说明在当前投影下两者越相关。"
     },
     {
      "type": "pair",
      "en": "A softmax over the row turns the scores into weights that sum to one, and the output for a token is the weighted sum of all the values.",
      "zh": "对这一行分数做 [[softmax|把一串任意大小的分数变成加起来等于 1 的权重，分数越高占比越大。]]，就得到加起来等于 1 的权重；某个词元的输出，就是所有值的加权和。"
     },
     {
      "type": "eq",
      "no": "(1)",
      "html": "Attention(Q, K, V) = softmax( <span class='frac'><span class='q'>QK<sup>T</sup></span><span class='d'>√<span class='var'>d</span><sub>k</sub></span></span> ) V"
     },
     {
      "type": "raw",
      "html": "<div class=\"lead\"><b>这个公式在说什么</b>QK<sup>T</sup> 是「每个词和每个词有多像」的分数表；除以 √d<sub>k</sub> 防止分数过大；softmax 把每一行变成权重；乘 V 就是按权重把信息取回来。一句话：每个词的新表示 = 所有词的信息，按相关程度加权平均。</div>"
     },
     {
      "type": "pair",
      "en": "The same layer appears in three places in a translation model. In the encoder it is self-attention: queries, keys and values all come from the same sequence, so every position can look at every other position [1].",
      "zh": "在翻译模型里，同一个层会出现在三个地方。在编码器中它是[[自注意力|self-attention：查询、键、值都来自同一条序列，所以每个位置都能看到其他所有位置。]]：查询、键、值都来自同一条序列，所以每个位置都能看到其他所有位置[1]。"
     },
     {
      "type": "pair",
      "en": "In the decoder it is masked self-attention: a position may only look at positions up to and including itself, so a prediction never sees the token it is supposed to produce.",
      "zh": "在解码器中它是[[带掩码|masked：把不该看的位置在 softmax 之前设成 −∞，权重就变成 0，相当于看不见。]]的自注意力：某个位置只能看到「直到并包括它自己」的位置，这样预测时永远不会偷看到它该生成的那个词。"
     }
    ]
   },
   {
    "id": "s2",
    "num": "2",
    "title": "一张图看完",
    "titleEn": "The Whole Layer at a Glance",
    "page": "示例 p.2",
    "lead": "把前两节的三句话画成图，就是一个注意力层的全部；Transformer 里剩下的都是重复和搬运。",
    "blocks": [
     {
      "type": "fig",
      "src": "assets/demo-attention-primer/attention-flow.svg",
      "size": "m",
      "label": "图 1",
      "alt": "Scaled dot-product attention flow",
      "zh": "缩放点积注意力的数据流：查询与键先做矩阵乘法得到分数表，除以 √d<sub>k</sub> 缩放，softmax 变成权重，最后与值相乘得到输出。",
      "en": "Figure 1: Scaled dot-product attention, drawn for this demo.",
      "labels": [
       [
        "Q / K / V",
        "查询 / 键 / 值"
       ],
       [
        "MatMul",
        "矩阵乘法"
       ],
       [
        "Scale 1/√d_k",
        "缩放：除以 √d_k"
       ],
       [
        "Softmax",
        "归一化成权重"
       ],
       [
        "Weighted sum",
        "加权求和，得到输出"
       ]
      ]
     },
     {
      "type": "pair",
      "en": "Queries and keys meet in a matrix product, the scores are scaled and normalised with softmax, and the resulting weights are applied to the values. Everything else in a Transformer is repetition and bookkeeping.",
      "zh": "查询与键先做矩阵乘法，分数经过缩放、再由 softmax 归一化，得到的权重作用在值上。Transformer 里其余的部分，都是重复和搬运。"
     },
     {
      "type": "pair",
      "en": "When the layer sits between encoder and decoder, the queries come from the decoder while keys and values come from the encoder, so each output position can pick information from the whole input sentence [2].",
      "zh": "当这一层夹在编码器和解码器之间时，查询来自解码器，而键和值来自编码器——这样每个输出位置都能从整句输入里取信息[2]。"
     },
     {
      "type": "note",
      "label": "演示注",
      "html": "图里的方框顺序就是公式 (1) 的求值顺序：先乘、再缩放、再 softmax、最后与值相乘。数值没有画出来，因为真正的矩阵通常有几千列。",
      "en": "The order of the boxes is exactly the order of the operations in Equation (1)."
     }
    ]
   },
   {
    "id": "s3",
    "num": "3",
    "title": "为什么用多头",
    "titleEn": "Why Several Heads",
    "page": "示例 p.2",
    "lead": "一个头只能表达一种「加权方式」，而句子里的关系不止一种。这一节用一张小表说明多头为什么不加价。",
    "blocks": [
     {
      "type": "pair",
      "en": "One head can only produce one averaging pattern. Running several heads in parallel lets the layer attend to several relations at once: one head may follow the previous token, another may connect a pronoun to the noun it refers to.",
      "zh": "一个头只能给出一种加权方式。并行跑几个[[多头|multi-head：并排做多组注意力，每组关注不同的关系，最后拼接。]]，就能同时关注好几种关系：某个头盯着前一个词，另一个头把代词和它指的名词连起来。"
     },
     {
      "type": "pair",
      "en": "Each head is narrower than the full model, so the cost of many heads stays close to the cost of one wide head.",
      "zh": "每个头的维度都比整个模型窄，所以「很多个头」的总开销，和「一个很宽的头」差不多。"
     },
     {
      "type": "table",
      "caption": "",
      "html": "<caption><b>表 1</b> 固定 d<sub>model</sub> = 512 时，头数与每头维度的关系（示意值，只为说明「宽度被摊薄」）。</caption><table><thead><tr><th>头数 h</th><th>每头维度 d<sub>k</sub> = 512 / h</th><th>说明</th></tr></thead><tbody><tr><td>1</td><td>512</td><td>单个宽头，只能表达一种加权模式</td></tr><tr><td>4</td><td>128</td><td>开始能分工</td></tr><tr><td>8</td><td>64</td><td>常见的默认设置</td></tr><tr><td>16</td><td>32</td><td>头太多，每个都太窄，效果反而下降</td></tr></tbody></table>"
     },
     {
      "type": "pair",
      "en": "The outputs of the heads are concatenated and projected once more, which lets the model mix what the individual heads found.",
      "zh": "各个头的输出会被[[拼接|concatenate：把几个向量首尾接成一个更长的向量。]]起来，再投影一次，让模型把各头找到的东西混合起来。"
     }
    ]
   },
   {
    "id": "sR",
    "num": "R",
    "title": "参考文献",
    "titleEn": "References",
    "page": "示例 p.2",
    "lead": "两条书目引用，用来演示正文里的 [1]、[2] 悬停浮窗。它们只是事实性的书目信息，不是本文内容的一部分。",
    "blocks": [
     {
      "type": "pair",
      "en": "References are kept in their original form so that they can be looked up directly by title.",
      "zh": "文献条目保留原样，方便按标题检索。正文里凡是 [1] 这样的编号，悬停就会弹出这个小窗。"
     },
     {
      "type": "refs"
     }
    ]
   }
  ],
  "glossary": [
   [
    "token",
    "词元",
    "模型处理的最小单位。可能是一个词、一个子词片段，甚至一个字符。"
   ],
   [
    "query / key / value",
    "查询 / 键 / 值",
    "三种角色：查询是「我想找什么」，键是「我这里有什么」，值是「我实际给出的内容」。"
   ],
   [
    "dot product",
    "点积",
    "两个向量对应分量相乘再相加，得到一个数，用来衡量方向有多一致。"
   ],
   [
    "softmax",
    "归一化指数函数",
    "把一串任意大小的分数变成加起来等于 1 的权重。"
   ],
   [
    "masked attention",
    "带掩码的注意力",
    "把未来位置遮住（权重设成 0），使解码器只能用已经生成的内容做预测。"
   ],
   [
    "multi-head",
    "多头",
    "并行做多组注意力，每组关注不同的关系模式，最后拼接起来。"
   ],
   [
    "self-attention",
    "自注意力",
    "查询、键、值都来自同一条序列的注意力。"
   ],
   [
    "encoder-decoder attention",
    "编码器-解码器注意力",
    "查询来自解码器、键和值来自编码器输出的注意力。"
   ]
  ],
  "termEn": {
   "词元": "token",
   "投影": "projected",
   "查询": "query",
   "键": "key",
   "值": "value",
   "点积": "dot product",
   "softmax": "softmax",
   "自注意力": "self-attention",
   "带掩码": "masked",
   "注意力": "attention",
   "多头": "heads",
   "拼接": "concatenated"
  },
  "references": [
   {
    "n": 1,
    "text": "Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, and Illia Polosukhin. Attention is all you need. In NIPS, 2017.",
    "url": "https://arxiv.org/abs/1706.03762"
   },
   {
    "n": 2,
    "text": "Dzmitry Bahdanau, Kyunghyun Cho, and Yoshua Bengio. Neural machine translation by jointly learning to align and translate. CoRR, abs/1409.0473, 2014.",
    "url": "https://arxiv.org/abs/1409.0473"
   }
  ]
 },
 {
  "id": "llama",
  "meta": {
   "title": "LLaMA: Open and Efficient Foundation Language Models",
   "titleZh": "LLaMA：开放高效的基础语言模型",
   "authors": "Hugo Touvron, Thibaut Lavril, Gautier Izacard, Xavier Martinet, Marie-Anne Lachaux, Timothée Lacroix, Baptiste Rozière, Naman Goyal, Eric Hambro, Faisal Azhar, Aurelien Rodriguez, Armand Joulin, Edouard Grave, Guillaume Lample",
   "affil": "Meta AI",
   "venue": "arXiv:2302.13971v1 · 2023 年 2 月 27 日",
   "blurb": "<b>一句话：</b>不用任何专有数据，只用公开语料，就把模型训到「体积只有 GPT-3 的十分之一、却在多数基准上更强」——LLaMA 让开放权重的大模型第一次真正追上了闭源模型。",
   "chips": [
    "2023 · Meta AI",
    "开放权重",
    "7B / 13B / 33B / 65B",
    "训练 1.0–1.4T 词元"
   ],
   "source": "arXiv:2302.13971v1",
   "arxiv": "2302.13971",
   "group": "开源模型",
   "note": "本文为非官方中文译本，仅供学习；原文版权归原作者所有。表格数字与公式按原文录入，未做改动；原文中前后不一致或表述含糊处另加「译者注」。"
  },
  "sections": [
   {
    "id": "s0",
    "num": "0",
    "title": "摘要",
    "titleEn": "Abstract",
    "page": "原文 p.1",
    "lead": "摘要四句话，把这篇论文的赌注讲完了：只用公开数据、把模型做小、把数据拉长，然后放出来给所有人。",
    "blocks": [
     {
      "type": "pair",
      "en": "We introduce LLaMA, a collection of foundation language models ranging from 7B to 65B parameters.",
      "zh": "我们发布 LLaMA——一组[[基础语言模型|foundation model：先在海量通用语料上预训练、再迁移到各种下游任务的模型。]]，参数量从 70 亿到 650 亿。"
     },
     {
      "type": "pair",
      "en": "We train our models on trillions of tokens, and show that it is possible to train state-of-the-art models using publicly available datasets exclusively, without resorting to proprietary and inaccessible datasets.",
      "zh": "我们用数万亿个[[词元|token：模型处理文本的最小单位，可能是一个词、一个子词片段，甚至一个字节。]]来训练，并证明：只用公开可获取的数据集、不碰任何专有且外人拿不到的数据，也能训出[[当前最佳|state of the art，公开基准上最好的成绩。]]水平的模型。"
     },
     {
      "type": "pair",
      "en": "In particular, LLaMA-13B outperforms GPT-3 (175B) on most benchmarks, and LLaMA-65B is competitive with the best models, Chinchilla-70B and PaLM-540B.",
      "zh": "具体来说，LLaMA-13B 在多数[[基准|benchmark：一套固定的题目与评分方式，用来横向比较不同模型的能力。]]上超过了 1750 亿参数的 GPT-3；而 LLaMA-65B 与当时最好的几个模型——Chinchilla-70B、PaLM-540B——不相上下。"
     },
     {
      "type": "pair",
      "en": "We release all our models to the research community.",
      "zh": "我们把全部模型开放给研究社区。"
     },
     {
      "type": "note",
      "label": "脚注",
      "html": "原文脚注：「同等贡献。通讯作者：{htouvron, thibautlav, gizacard, egrave, glample}@meta.com」；另一条脚注给出模型下载地址 <code>https://github.com/facebookresearch/llama</code>。<br><b>译者注：</b>这里说的「开放」是<strong>开放权重</strong>（可以下载参数用于研究），并不是开源训练数据与训练代码的完整复现包——这一点在 2023 年引发过不少讨论。",
      "en": "∗Equal contribution. Correspondence: {htouvron, thibautlav,gizacard,egrave,glample}@meta.com  1https://github.com/facebookresearch/llama"
     }
    ]
   },
   {
    "id": "s1",
    "num": "1",
    "title": "引言",
    "titleEn": "Introduction",
    "page": "原文 p.1–2",
    "lead": "这一节其实在反驳一个流行假设：既然规模法则说「越大越好」，那是不是越大就越好？作者的回答是——看你把预算花在训练上，还是花在推理上。",
    "blocks": [
     {
      "type": "pair",
      "en": "Large Languages Models (LLMs) trained on massive corpora of texts have shown their ability to perform new tasks from textual instructions or from a few examples (Brown et al., 2020). These few-shot properties first appeared when scaling models to a sufficient size (Kaplan et al., 2020), resulting in a line of work that focuses on further scaling these models (Chowdhery et al., 2022; Rae et al., 2021).",
      "zh": "在海量文本上训练的大语言模型（LLM），已经展现出这样的能力：给一段文字指令，或者给几个例子，它就能完成新任务（Brown 等，2020）。这种[[少样本|few-shot：只给几个示例，模型就能照着做，不需要重新训练。]]能力，是模型规模大到一定程度后才出现的（Kaplan 等，2020），于是有一批工作专门研究怎么继续把模型做大（Chowdhery 等，2022；Rae 等，2021）。"
     },
     {
      "type": "pair",
      "en": "These efforts are based on the assumption that more parameters will lead to better performance. However, recent work from Hoffmann et al. (2022) shows that, for a given compute budget, the best performances are not achieved by the largest models, but by smaller models trained on more data.",
      "zh": "这些努力背后有一个假设：参数越多，效果越好。但 Hoffmann 等（2022）最近的工作表明，在固定的[[算力预算|compute budget：训练时允许消耗的总计算量，通常用浮点运算次数或 GPU 天数衡量。]]下，效果最好的并不是最大的模型，而是**用更多数据训练的较小模型**。"
     },
     {
      "type": "pair",
      "en": "The objective of the scaling laws from Hoffmann et al. (2022) is to determine how to best scale the dataset and model sizes for a particular training compute budget. However, this objective disregards the inference budget, which becomes critical when serving a language model at scale.",
      "zh": "Hoffmann 等人的[[规模法则|scaling law：用幂律描述「参数量、数据量、算力」与损失之间关系的经验规律。]]要回答的是：给定训练算力预算，数据量和模型大小该怎么配。但这个目标忽略了[[推理预算|inference budget：模型上线后回答一次要花的时间和显存。]]——而模型真正大规模服务时，推理预算才是关键。"
     },
     {
      "type": "pair",
      "en": "In this context, given a target level of performance, the preferred model is not the fastest to train but the fastest at inference, and although it may be cheaper to train a large model to reach a certain level of performance, a smaller one trained longer will ultimately be cheaper at inference.",
      "zh": "在这个意义上，要到达同样的效果，首选不是「训练最快」的模型，而是「推理最快」的模型：把大模型训到某个水平也许更便宜，但小模型多训一会儿，最终在推理上更划算。"
     },
     {
      "type": "pair",
      "en": "For instance, although Hoffmann et al. (2022) recommends training a 10B model on 200B tokens, we find that the performance of a 7B model continues to improve even after 1T tokens.",
      "zh": "举个例子：Hoffmann 等人建议用 2000 亿词元训练一个 100 亿参数的模型，而我们发现，70 亿参数的模型即使训练到 1 万亿词元，效果仍在继续提升。"
     },
     {
      "type": "pair",
      "en": "The focus of this work is to train a series of language models that achieve the best possible performance at various inference budgets, by training on more tokens than what is typically used. The resulting models, called LLaMA, ranges from 7B to 65B parameters with competitive performance compared to the best existing LLMs.",
      "zh": "本文的目标就是：用比常规更多的词元训练一组模型，让它们在不同推理预算下都尽可能好。这组模型叫 LLaMA，参数从 70 亿到 650 亿，效果能与当时最好的 LLM 相比。"
     },
     {
      "type": "pair",
      "en": "For instance, LLaMA-13B outperforms GPT-3 on most benchmarks, despite being 10× smaller. We believe that this model will help democratize the access and study of LLMs, since it can be run on a single GPU.",
      "zh": "例如 LLaMA-13B 在多数基准上超过 GPT-3，体积却只有它的十分之一——这意味着它能跑在单张 [[GPU|图形处理器：原本为图形计算设计，因为擅长大规模并行运算，成了训练和运行大模型的标配硬件。]]上。我们相信，这有助于让更多人接触和研究大模型。"
     },
     {
      "type": "pair",
      "en": "At the higher-end of the scale, our 65B-parameter model is also competitive with the best large language models such as Chinchilla or PaLM-540B.",
      "zh": "往大的一端看，650 亿参数的版本也能与 Chinchilla、PaLM-540B 这样的顶级模型一较高下。"
     },
     {
      "type": "pair",
      "en": "Unlike Chinchilla, PaLM, or GPT-3, we only use publicly available data, making our work compatible with open-sourcing, while most existing models rely on data which is either not publicly available or undocumented (e.g. \"Books – 2TB\" or \"Social media conversations\").",
      "zh": "与 Chinchilla、PaLM、GPT-3 不同，我们只使用公开可获取的数据，因此这份工作与开源是相容的；而现有的大多数模型，依赖的数据要么不公开，要么来路不明（论文里就写着「书籍 2TB」「社交媒体对话」这种）。"
     },
     {
      "type": "pair",
      "en": "There exist some exceptions, notably OPT (Zhang et al., 2022), GPT-NeoX (Black et al., 2022), BLOOM (Scao et al., 2022) and GLM (Zeng et al., 2022), but none that are competitive with PaLM-62B or Chinchilla.",
      "zh": "也有例外，比如 OPT（Zhang 等，2022）、GPT-NeoX（Black 等，2022）、BLOOM（Scao 等，2022）和 GLM（Zeng 等，2022），但它们的水平都还够不到 PaLM-62B 或 Chinchilla。"
     },
     {
      "type": "pair",
      "en": "In the rest of this paper, we present an overview of the modifications we made to the transformer architecture (Vaswani et al., 2017), as well as our training method. We then report the performance of our models and compare with others LLMs on a set of standard benchmarks.",
      "zh": "接下来，我们先概述对 [[Transformer 架构|Vaswani 等 2017 年提出的、完全基于注意力的序列模型，今天几乎所有大模型都以它为骨架。]]（Vaswani 等，2017）所做的改动以及训练方法；然后在一组标准基准上报告效果，并与其他 LLM 比较。"
     },
     {
      "type": "pair",
      "en": "Finally, we expose some of the biases and toxicity encoded in our models, using some of the most recent benchmarks from the responsible AI community.",
      "zh": "最后，我们用负责任 AI 领域最新的几个基准，把模型里学到的[[偏见与毒性|bias / toxicity：模型从数据里继承的刻板印象、歧视性表达或有害内容。]]摆出来看。"
     }
    ]
   },
   {
    "id": "s2",
    "num": "2",
    "title": "方法",
    "titleEn": "Approach",
    "page": "原文 p.2–3",
    "lead": "这一节讲两件事：数据从哪来（只用公开语料），模型长什么样（在 Transformer 上做了四处改动）。",
    "blocks": [
     {
      "type": "pair",
      "en": "Our training approach is similar to the methods described in previous work (Brown et al., 2020; Chowdhery et al., 2022), and is inspired by the Chinchilla scaling laws (Hoffmann et al., 2022). We train large transformers on a large quantity of textual data using a standard optimizer.",
      "zh": "我们的训练方法与已有工作（Brown 等，2020；Chowdhery 等，2022）类似，并受到 Chinchilla [[规模法则|scaling law：给定算力时，参数量与数据量应当同比例增长。]]（Hoffmann 等，2022）的启发：用标准优化器，在海量文本上训练大型 Transformer。"
     },
     {
      "type": "sub",
      "num": "2.1",
      "id": "s21",
      "zh": "预训练数据",
      "en": "Pre-training Data"
     },
     {
      "type": "pair",
      "en": "Our training dataset is a mixture of several sources, reported in Table 1, that cover a diverse set of domains. For the most part, we reuse data sources that have been leveraged to train other LLMs, with the restriction of only using data that is publicly available, and compatible with open sourcing. This leads to the following mixture of data and the percentage they represent in the training set:",
      "zh": "我们的训练集由多个来源混合而成（见表 1），覆盖的领域相当分散。大部分来源沿用其他 LLM 用过的那批，但加了一条硬约束：只用公开可获取、且与开源相容的数据。最终的数据配比与占比是："
     },
     {
      "type": "pair",
      "en": "English CommonCrawl [67%]. We preprocess five CommonCrawl dumps, ranging from 2017 to 2020, with the CCNet pipeline (Wenzek et al., 2020). This process deduplicates the data at the line level, performs language identification with a fastText linear classifier to remove non-English pages and filters low quality content with an ngram language model.",
      "zh": "**英文 CommonCrawl［67%］**　我们用 CCNet 流程（Wenzek 等，2020）预处理 2017–2020 年的五份 CommonCrawl 快照：先按行[[去重|deduplicate：同一段文字在语料里出现多次，只保留一份，否则模型会把重复内容背下来。]]，再用 fastText 线性分类器做语言识别、剔掉非英文网页，最后用一个 n-gram 语言模型过滤低质量内容。"
     },
     {
      "type": "pair",
      "en": "In addition, we trained a linear model to classify pages used as references in Wikipedia v.s. randomly sampled pages, and discarded pages not classified as references.",
      "zh": "此外，我们还训了一个线性分类器，用来区分「被维基百科引用过的网页」和「随机抽的网页」，没被判定为「参考文献级」的网页一律丢掉。"
     },
     {
      "type": "pair",
      "en": "C4 [15%]. During exploratory experiments, we observed that using diverse pre-processed CommonCrawl datasets improves performance. We thus included the publicly available C4 dataset (Raffel et al., 2020) in our data. The preprocessing of C4 also contains deduplication and language identification steps: the main difference with CCNet is the quality filtering, which mostly relies on heuristics such as presence of punctuation marks or the number of words and sentences in a webpage.",
      "zh": "**C4［15%］**　在探索性实验里我们注意到，混用几种预处理方式不同的 CommonCrawl 数据集，效果会更好，于是把公开的 C4 数据集（Raffel 等，2020）也加了进来。C4 的预处理同样包含去重和语言识别，与 CCNet 的主要差别在质量过滤：C4 更多靠[[启发式规则|heuristic：不追求原理，只按经验规则判断，比如「句子有没有标点」。]]，例如网页里有没有标点、词数和句数够不够。"
     },
     {
      "type": "pair",
      "en": "Github [4.5%]. We use the public GitHub dataset available on Google BigQuery. We only kept projects that are distributed under the Apache, BSD and MIT licenses. Additionally, we filtered low quality files with heuristics based on the line length or proportion of alphanumeric characters, and removed boilerplate, such as headers, with regular expressions. Finally, we deduplicate the resulting dataset at the file level, with exact matches.",
      "zh": "**GitHub［4.5%］**　用的是 Google BigQuery 上的公开 GitHub 数据集，只保留以 Apache、BSD、MIT 许可发布的项目。接着按行长度、字母数字字符占比等规则过滤低质量文件，用正则去掉文件头之类的[[样板内容|boilerplate：每个文件都有、但不含信息的固定格式内容，比如许可证头和 import 段。]]，最后在文件级做精确去重。"
     },
     {
      "type": "pair",
      "en": "Wikipedia [4.5%]. We add Wikipedia dumps from the June–August 2022 period, covering 20 languages, which use either the Latin or Cyrillic scripts: bg, ca, cs, da, de, en, es, fr, hr, hu, it, nl, pl, pt, ro, ru, sl, sr, sv, uk. We process the data to remove hyperlinks, comments and other formatting boilerplate.",
      "zh": "**维基百科［4.5%］**　加入 2022 年 6–8 月的维基百科快照，覆盖 20 种语言（拉丁字母或西里尔字母）：保加利亚语、加泰罗尼亚语、捷克语、丹麦语、德语、英语、西班牙语、法语、克罗地亚语、匈牙利语、意大利语、荷兰语、波兰语、葡萄牙语、罗马尼亚语、俄语、斯洛文尼亚语、塞尔维亚语、瑞典语、乌克兰语。处理时去掉超链接、注释和其它排版格式。"
     },
     {
      "type": "pair",
      "en": "Gutenberg and Books3 [4.5%]. We include two book corpora in our training dataset: the Gutenberg Project, which contains books that are in the public domain, and the Books3 section of ThePile (Gao et al., 2020), a publicly available dataset for training large language models. We perform deduplication at the book level, removing books with more than 90% content overlap.",
      "zh": "**古登堡计划与 Books3［4.5%］**　训练集里有两批书：古登堡计划（版权已过期的公版书）和 ThePile 数据集（Gao 等，2020）中的 Books3 部分。我们在「整本书」这一级去重：内容重合超过 90% 的书会被剔掉。"
     },
     {
      "type": "pair",
      "en": "ArXiv [2.5%]. We process arXiv Latex files to add scientific data to our dataset. Following Lewkowycz et al. (2022), we removed everything before the first section, as well as the bibliography. We also removed the comments from the .tex files, and inline-expanded definitions and macros written by users to increase consistency across papers.",
      "zh": "**arXiv［2.5%］**　我们处理 arXiv 的 LaTeX 源码，为训练集补上科学文献。按照 Lewkowycz 等（2022）的做法，删掉正文第一节之前的所有内容以及参考文献；同时去掉 .tex 里的注释，并把作者自定义的宏和定义就地展开，让不同论文的写法尽量统一。"
     },
     {
      "type": "pair",
      "en": "Stack Exchange [2%]. We include a dump of Stack Exchange, a website of high quality questions and answers that covers a diverse set of domains, ranging from computer science to chemistry. We kept the data from the 28 largest websites, removed the HTML tags from text and sorted the answers by score (from highest to lowest).",
      "zh": "**Stack Exchange［2%］**　加入 Stack Exchange 的数据快照——这是一个高质量问答站点，领域从计算机科学一直铺到化学。我们保留最大的 28 个站点的数据，去掉文本里的 HTML 标签，并按得分从高到低排列答案。"
     },
     {
      "type": "pair",
      "en": "Tokenizer. We tokenize the data with the bytepair encoding (BPE) algorithm (Sennrich et al., 2015), using the implementation from SentencePiece (Kudo and Richardson, 2018). Notably, we split all numbers into individual digits, and fallback to bytes to decompose unknown UTF-8 characters.",
      "zh": "**分词器**　我们用 [[BPE|byte-pair encoding：从字符开始，反复把最常相邻出现的两个片段合并成一个新单元，最终得到常用子词表。]]算法（Sennrich 等，2015）分词，实现来自 SentencePiece（Kudo 和 Richardson，2018）。有两个特别处理：所有数字都拆成单个数字（「2023」变成「2」「0」「2」「3」）；遇到词表里没有的 UTF-8 字符时，退回到字节级切分。"
     },
     {
      "type": "raw",
      "html": "<div class=\"lead\"><b>为什么要拆数字、退回字节</b>拆开数字能减少组合爆炸（否则「2023」和「2024」是两个不同词元），也让模型学会按位计算；退回字节则保证<b>任何</b>字符都能编码，不会出现「不认识的字符直接报错」。</div>"
     },
     {
      "type": "table",
      "caption": "",
      "html": "<caption><b>表 1</b> 预训练数据。每个子集给出采样比例、训练 1.4T 词元时在该子集上跑的轮数（Epochs），以及磁盘大小。训练 1T 词元时采用相同的采样比例。</caption><table><thead><tr><th>数据集</th><th>采样比例</th><th>轮数 Epochs</th><th>磁盘大小</th></tr></thead><tbody><tr><td>CommonCrawl</td><td>67.0%</td><td>1.10</td><td>3.3 TB</td></tr><tr><td>C4</td><td>15.0%</td><td>1.06</td><td>783 GB</td></tr><tr><td>GitHub</td><td>4.5%</td><td>0.64</td><td>328 GB</td></tr><tr><td>Wikipedia</td><td>4.5%</td><td>2.45</td><td>83 GB</td></tr><tr><td>Books</td><td>4.5%</td><td>2.23</td><td>85 GB</td></tr><tr><td>ArXiv</td><td>2.5%</td><td>1.06</td><td>92 GB</td></tr><tr><td>StackExchange</td><td>2.0%</td><td>1.03</td><td>78 GB</td></tr></tbody></table>"
     },
     {
      "type": "pair",
      "en": "Overall, our entire training dataset contains roughly 1.4T tokens after tokenization. For most of our training data, each token is used only once during training, with the exception of the Wikipedia and Books domains, over which we perform approximately two epochs.",
      "zh": "整体来看，分词之后整个训练集约含 1.4 万亿词元。绝大部分数据只被「看」一遍，只有维基百科和书籍两类各跑了约两轮——这也解释了表 1 里那两行的轮数大于 1。"
     },
     {
      "type": "sub",
      "num": "2.2",
      "id": "s22",
      "zh": "架构",
      "en": "Architecture"
     },
     {
      "type": "pair",
      "en": "Following recent work on large language models, our network is based on the transformer architecture (Vaswani et al., 2017). We leverage various improvements that were subsequently proposed, and used in different models such as PaLM. Here are the main difference with the original architecture, and where we were found the inspiration for this change (in bracket):",
      "zh": "沿着近期大语言模型的做法，我们的网络基于 [[Transformer|Vaswani 等 2017 年的论文，用堆叠的自注意力 + 前馈层取代循环结构。]]架构（Vaswani 等，2017），并吸收了此后提出的若干改进（其中一些已在 PaLM 等模型里用过）。与原始架构相比，主要差别如下，方括号里标出改动的出处："
     },
     {
      "type": "pair",
      "en": "Pre-normalization [GPT3]. To improve the training stability, we normalize the input of each transformer sub-layer, instead of normalizing the output. We use the RMSNorm normalizing function, introduced by Zhang and Sennrich (2019).",
      "zh": "**预归一化［GPT-3］**　为了训练更稳定，我们在每个子层的**输入**上做归一化，而不是在输出上做（原始 Transformer 是后者，即 post-LN）。归一化函数用 Zhang 和 Sennrich（2019）提出的 [[RMSNorm|均方根归一化：只除以均方根、不减均值，比 LayerNorm 少一次均值计算。]]。"
     },
     {
      "type": "pair",
      "en": "SwiGLU activation function [PaLM]. We replace the ReLU non-linearity by the SwiGLU activation function, introduced by Shazeer (2020) to improve the performance. We use a dimension of 2/3·4d instead of 4d as in PaLM.",
      "zh": "**SwiGLU 激活函数［PaLM］**　把 ReLU 换成 SwiGLU（Shazeer，2020），效果更好。前馈层的中间维度取 <i>2/3·4d</i>，而不是 PaLM 用的 <i>4d</i>——这样在参数量上与标准前馈层大致对齐。"
     },
     {
      "type": "pair",
      "en": "Rotary Embeddings [GPTNeo]. We remove the absolute positional embeddings, and instead, add rotary positional embeddings (RoPE), introduced by Su et al. (2021), at each layer of the network.",
      "zh": "**旋转位置编码［GPT-Neo］**　去掉绝对[[位置编码|positional embedding：把「第几个词」编成一个向量加到词向量上。]]，改用 Su 等（2021）提出的旋转位置编码（RoPE），并在网络的每一层都施加。"
     },
     {
      "type": "pair",
      "en": "The details of the hyper-parameters for our different models are given in Table 2.",
      "zh": "各模型的超参数细节见表 2。"
     },
     {
      "type": "table",
      "caption": "",
      "html": "<caption><b>表 2</b> 模型规模、架构与优化超参数。</caption><table><thead><tr><th>参数量</th><th>维度 d<sub>model</sub></th><th>头数</th><th>层数</th><th>学习率</th><th>batch size</th><th>训练词元</th></tr></thead><tbody><tr><td>6.7B</td><td>4096</td><td>32</td><td>32</td><td>3.0e−4</td><td>4M</td><td>1.0T</td></tr><tr><td>13.0B</td><td>5120</td><td>40</td><td>40</td><td>3.0e−4</td><td>4M</td><td>1.0T</td></tr><tr><td>32.5B</td><td>6656</td><td>52</td><td>60</td><td>1.5e−4</td><td>4M</td><td>1.4T</td></tr><tr><td>65.2B</td><td>8192</td><td>64</td><td>80</td><td>1.5e−4</td><td>4M</td><td>1.4T</td></tr></tbody></table>"
     },
     {
      "type": "note",
      "label": "译者注",
      "html": "原文这里写的是「2 34d」，是排版把 <i>2/3·4d</i> 拆坏了（下一页紧接着写「instead of 4d as in PaLM」）。译文中按 <i>2/3·4d</i> 录入。另外，LLaMA 的 33B 模型在表 2 里写作 32.5B，后文也常简称 33B，二者是同一个模型。"
     }
    ]
   }
  ],
  "glossary": [
   [
    "foundation model",
    "基础模型",
    "先在海量通用语料上预训练、再迁移到各种下游任务的模型，LLaMA、GPT 都属于这一类。"
   ],
   [
    "few-shot",
    "少样本",
    "只给几个示例（甚至只给一句指令），模型就能照着完成新任务，不需要重新训练。"
   ],
   [
    "compute budget",
    "算力预算",
    "训练时允许消耗的总计算量，通常用 FLOPs 或 GPU 天数衡量。"
   ],
   [
    "inference budget",
    "推理预算",
    "模型上线后回答一次要花的时间和显存。训练便宜不等于用起来便宜。"
   ],
   [
    "scaling law",
    "规模法则",
    "用幂律描述「参数量、数据量、算力」与损失关系的经验规律，用来决定钱该花在哪。"
   ],
   [
    "BPE",
    "字节对编码",
    "把词拆成高频子词片段的切分方法，既覆盖生僻词，又缩小词表。"
   ],
   [
    "RMSNorm",
    "均方根归一化",
    "LayerNorm 的简化版：只除以均方根、不减均值，计算更省。"
   ],
   [
    "RoPE",
    "旋转位置编码",
    "用旋转的方式把位置信息编进 query/key，使注意力天然带相对位置。"
   ],
   [
    "SwiGLU",
    "门控线性单元变体",
    "把前馈层的激活换成「门控 + SiLU」，在同等参数下效果更好。"
   ],
   [
    "benchmark",
    "基准测试",
    "一套固定的题目与评分方式，用来横向比较不同模型的能力。"
   ]
  ],
  "termEn": {
   "基础语言模型": "foundation language models",
   "词元": "tokens",
   "当前最佳": "state-of-the-art",
   "基准": "benchmarks",
   "少样本": "few-shot",
   "算力预算": "compute budget",
   "规模法则": "scaling laws",
   "推理预算": "inference budget",
   "GPU": "GPU",
   "Transformer 架构": "transformer architecture",
   "偏见与毒性": "biases and toxicity",
   "去重": "deduplicates",
   "启发式规则": "heuristics",
   "样板内容": "boilerplate",
   "BPE": "bytepair encoding",
   "位置编码": "positional embeddings",
   "RMSNorm": "RMSNorm"
  },
  "references": []
 }
];

/* 书架：papers/manifest.json + 已有的译本 */
window.SHELF = {
 "groups": [
  "基础架构",
  "规模与训练",
  "开源模型",
  "对齐与推理",
  "系统与效率",
  "示例"
 ],
 "items": [
  {
   "arxiv": "1706.03762",
   "id": "",
   "slug": "attention",
   "group": "基础架构",
   "titleEn": "Attention Is All You Need",
   "titleZh": "注意力就是你所需要的一切",
   "status": "todo",
   "pdf": "../papers/1706.03762.pdf",
   "note": "Transformer 原始论文"
  },
  {
   "arxiv": "2104.09864",
   "id": "",
   "slug": "",
   "group": "基础架构",
   "titleEn": "RoFormer: Enhanced Transformer with Rotary Position Embedding",
   "titleZh": "RoFormer：旋转位置编码（RoPE）",
   "status": "todo",
   "pdf": "../papers/2104.09864.pdf",
   "note": "位置编码，几乎所有开源 LLM 都在用"
  },
  {
   "arxiv": "2309.00071",
   "id": "",
   "slug": "",
   "group": "基础架构",
   "titleEn": "YaRN: Efficient Context Window Extension of Large Language Models",
   "titleZh": "YaRN：上下文窗口的高效扩展",
   "status": "todo",
   "pdf": "../papers/2309.00071.pdf",
   "note": "长上下文 / RoPE 外推"
  },
  {
   "arxiv": "2001.08361",
   "id": "",
   "slug": "",
   "group": "规模与训练",
   "titleEn": "Scaling Laws for Neural Language Models",
   "titleZh": "神经语言模型的规模法则",
   "status": "todo",
   "pdf": "../papers/2001.08361.pdf",
   "note": "参数、数据、算力三者的幂律"
  },
  {
   "arxiv": "2203.15556",
   "id": "",
   "slug": "",
   "group": "规模与训练",
   "titleEn": "Training Compute-Optimal Large Language Models",
   "titleZh": "训练计算最优的大语言模型（Chinchilla）",
   "status": "todo",
   "pdf": "../papers/2203.15556.pdf",
   "note": "同样的算力，数据该给多少"
  },
  {
   "arxiv": "2302.13971",
   "id": "",
   "slug": "",
   "group": "开源模型",
   "titleEn": "LLaMA: Open and Efficient Foundation Language Models",
   "titleZh": "LLaMA：开放高效的基础语言模型",
   "status": "todo",
   "pdf": "../papers/2302.13971.pdf",
   "note": "开源模型的分水岭"
  },
  {
   "arxiv": "2401.04088",
   "id": "",
   "slug": "",
   "group": "开源模型",
   "titleEn": "Mixtral of Experts",
   "titleZh": "Mixtral 混合专家模型",
   "status": "todo",
   "pdf": "../papers/2401.04088.pdf",
   "note": "稀疏 MoE 的工程样本"
  },
  {
   "arxiv": "2401.06066",
   "id": "",
   "slug": "",
   "group": "开源模型",
   "titleEn": "DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models",
   "titleZh": "DeepSeekMoE：专家极致专业化的混合专家模型",
   "status": "todo",
   "pdf": "../papers/2401.06066.pdf",
   "note": "细粒度专家 + 共享专家"
  },
  {
   "arxiv": "2407.21783",
   "id": "",
   "slug": "",
   "group": "开源模型",
   "titleEn": "The Llama 3 Herd of Models",
   "titleZh": "Llama 3 模型家族",
   "status": "todo",
   "pdf": "../papers/2407.21783.pdf",
   "note": "从数据到后训练的完整报告"
  },
  {
   "arxiv": "2203.02155",
   "id": "",
   "slug": "",
   "group": "对齐与推理",
   "titleEn": "Training language models to follow instructions with human feedback",
   "titleZh": "用人类反馈训练语言模型遵循指令（InstructGPT）",
   "status": "todo",
   "pdf": "../papers/2203.02155.pdf",
   "note": "RLHF 的三步流程"
  },
  {
   "arxiv": "2305.18290",
   "id": "",
   "slug": "",
   "group": "对齐与推理",
   "titleEn": "Direct Preference Optimization: Your Language Model is Secretly a Reward Model",
   "titleZh": "直接偏好优化（DPO）",
   "status": "todo",
   "pdf": "../papers/2305.18290.pdf",
   "note": "把 RLHF 化简成一个分类损失"
  },
  {
   "arxiv": "2501.12948",
   "id": "",
   "slug": "",
   "group": "对齐与推理",
   "titleEn": "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning",
   "titleZh": "DeepSeek-R1：用强化学习激发出推理能力",
   "status": "todo",
   "pdf": "../papers/2501.12948.pdf",
   "note": "纯 RL 训出长思维链"
  },
  {
   "arxiv": "2309.06180",
   "id": "",
   "slug": "",
   "group": "系统与效率",
   "titleEn": "Efficient Memory Management for Large Language Model Serving with PagedAttention",
   "titleZh": "用 PagedAttention 高效管理大模型服务的内存（vLLM）",
   "status": "todo",
   "pdf": "../papers/2309.06180.pdf",
   "note": "KV cache 分页，吞吐翻倍"
  },
  {
   "arxiv": "2205.14135",
   "id": "",
   "slug": "",
   "group": "系统与效率",
   "titleEn": "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness",
   "titleZh": "FlashAttention：IO 感知的精确注意力",
   "status": "todo",
   "pdf": "../papers/2205.14135.pdf",
   "note": "把注意力算成带宽问题"
  },
  {
   "arxiv": "",
   "id": "demo-attention-primer",
   "slug": "demo",
   "group": "示例",
   "titleEn": "How Attention Works: A One-Page Primer",
   "titleZh": "注意力是怎么工作的：一页入门",
   "status": "ready",
   "pdf": "",
   "note": "原创示例，演示阅读器全部功能"
  },
  {
   "arxiv": "",
   "id": "llama",
   "slug": "llama",
   "group": "未分组",
   "titleEn": "",
   "titleZh": "",
   "status": "ready",
   "pdf": "",
   "note": ""
  }
 ]
};
