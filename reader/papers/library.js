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
 }
];
