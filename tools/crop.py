"""
裁图 / 找图：把 PDF 里的插图裁成 PNG，供 data/<slug>/img/ 使用。

用法:
    # 1) 先看某页有哪些图形区域（矢量图 + 位图），打印坐标
    python tools/crop.py find papers/2305.18290.pdf 6

    # 2) 按坐标裁（坐标是 PDF 点，原点在左上角；用 find 打印的值）
    python tools/crop.py crop papers/2305.18290.pdf 6 100,80,510,300 data/dpo/img/fig1.png [zoom]

    # 留白太多就往里收一点；裁进来多余正文就往里缩，宁可小一点也别带正文。
    # 默认 zoom=3（约 216 dpi），线稿会很清楚；照片类图 zoom=2 即可。

说明:
    find 会把「位图 + 矢量绘图」按纵向间隔聚成若干块，给出每块的包围盒和尺寸，
    通常一块就是一个图/一张表；块太碎时也可以用 pymupdf 的文本块坐标自行估算。
"""
import sys

try:
    import pymupdf
except ImportError:
    sys.exit("需要 pymupdf：pip install pymupdf")


def clusters(rects, gap=14):
    """把纵向相距很近的矩形合并成块。"""
    rects = [r for r in rects if r.width > 3 and r.height > 3]
    if not rects:
        return []
    rects.sort(key=lambda r: (r.y0, r.x0))
    out = []
    for r in rects:
        if out and r.y0 - out[-1].y1 < gap and not (r.x1 < out[-1].x0 or r.x0 > out[-1].x1):
            out[-1] = out[-1] | r
        else:
            out.append(pymupdf.Rect(r))
    # 再合并一次，处理「先合并又和后面的块挨上」的情况
    merged = True
    while merged:
        merged = False
        for i in range(len(out) - 1):
            a, b = out[i], out[i + 1]
            if b.y0 - a.y1 < gap and not (b.x1 < a.x0 or b.x0 > a.x1):
                out[i] = a | b
                del out[i + 1]
                merged = True
                break
    return out


def cmd_find(pdf, pages):
    doc = pymupdf.open(pdf)
    for pno in pages:
        pg = doc[pno - 1]
        rects = []
        for info in pg.get_image_info():
            rects.append(pymupdf.Rect(info["bbox"]))
        for d in pg.get_drawings():
            r = d.get("rect")
            if r is not None:
                # 细长的横线/竖线多是表格线、页眉分隔线，先留着由聚类判断
                rects.append(pymupdf.Rect(r))
        print("== p%d  (页面 %.0f×%.0f pt)" % (pno, pg.rect.width, pg.rect.height))
        for i, r in enumerate(clusters(rects), start=1):
            print("  [%d] rect=%.0f,%.0f,%.0f,%.0f   %.0f×%.0f pt"
                  % (i, r.x0, r.y0, r.x1, r.y1, r.width, r.height))
        print("  文本块 y 范围: %s"
              % ", ".join("%.0f-%.0f" % (b[1], b[3]) for b in pg.get_text("blocks")[:12]))


def cmd_crop(pdf, pno, box, out, zoom=3.0):
    x0, y0, x1, y1 = [float(v) for v in box.split(",")]
    doc = pymupdf.open(pdf)
    pg = doc[pno - 1]
    clip = pymupdf.Rect(x0, y0, x1, y1) & pg.rect
    pix = pg.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip, alpha=False)
    import os
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    pix.save(out)
    print("%s  %d×%d px  %.0f KB" % (out, pix.width, pix.height, os.path.getsize(out) / 1024))


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    mode = sys.argv[1]
    if mode == "find":
        cmd_find(sys.argv[2], [int(x) for x in sys.argv[3:]])
    elif mode == "crop":
        zoom = float(sys.argv[7]) if len(sys.argv) > 7 else 3.0
        cmd_crop(sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5], zoom)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
