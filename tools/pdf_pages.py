"""
把 PDF 每页渲染成 PNG（配一份纯文本），供「看图翻译」用。

用法:
    python tools/pdf_pages.py papers/2305.18290.pdf dpo [dpi]

产物:
    data/<slug>/_pages/p01.png …   每页一张图（默认 130 dpi，约 1075×1390）
    data/<slug>/_pages/p01.txt …   同页文本（帮你在图里搜词、核对数字）

为什么要有这个：双栏 + 公式 + 表格的 PDF，纯文本抽取会把版面顺序打乱、
把公式拆成碎片。直接看页面图来抄写和翻译，位置、上下标、表头都不会错。

注意：_pages/ 只是工作目录，构建不会打包它；确认无误后可删。
"""
import os
import sys

try:
    import pymupdf
except ImportError:
    sys.exit("需要 pymupdf：pip install pymupdf")


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    pdf_path, slug = sys.argv[1], sys.argv[2]
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 130
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outdir = os.path.join(base, "data", slug, "_pages")
    os.makedirs(outdir, exist_ok=True)

    doc = pymupdf.open(pdf_path)
    for pno, page in enumerate(doc, start=1):
        pix = page.get_pixmap(dpi=dpi)
        png = os.path.join(outdir, "p%02d.png" % pno)
        pix.save(png)
        txt = os.path.join(outdir, "p%02d.txt" % pno)
        with open(txt, "w", encoding="utf-8") as f:
            f.write(page.get_text("text"))
    print("%s：%d 页 → %s（%d dpi，每页 %.0f KB）"
          % (os.path.basename(pdf_path), len(doc), outdir, dpi,
             os.path.getsize(os.path.join(outdir, "p01.png")) / 1024))


if __name__ == "__main__":
    main()
