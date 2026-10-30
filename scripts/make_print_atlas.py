#!/usr/bin/env python3
"""Draw the printed-lettering atlas (30 Oct 2026, lesson UL199): ``assets/print/print_atlas.png``, 2048 x 2048
RGBA, laid out by ``wenart.blender.print_labels`` (the spine strips with their invented titles and authors, the paper
labels with their kitchen words and invented wine labels). Run once on a machine with Pillow and the open fonts
(Caladea, Liberation Serif, Inter: SIL Open Font License); the PNG is committed, the build only reads it.

    python3 scripts/make_print_atlas.py [--out assets/print/print_atlas.png]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from wenart.blender import print_labels as PL  # noqa: E402

FONTS = {
    "serif_bold": ("/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf",
                   "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
    "serif": ("/usr/share/fonts/truetype/crosextra/Caladea-Regular.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
    "sans_semibold": ("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
                      "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                      "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    "sans": ("/usr/share/fonts/opentype/inter/Inter-Regular.otf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
}
PAPER = (241, 234, 218, 255)        # a cream label paper
PAPER_WHITE = (247, 245, 240, 255)
INK = (30, 28, 30, 255)
RULE = (120, 96, 60, 255)


def font(family: str, size: int):
    for path in FONTS[family]:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def fit_font(draw, text: str, family: str, size: int, max_w: int):
    f = font(family, size)
    while size > 8 and draw.textlength(text, font=f) > max_w:
        size -= 1
        f = font(family, size)
    return f


def spaced(text: str, case: str) -> str:
    if case == "upper":
        return " ".join(text.upper()).replace("   ", "  ")
    return text


def draw_strip(img: Image.Image, k: int) -> None:
    info = PL.strip_text(k)
    x0, y0, x1, y1 = PL.strip_box_px(k)
    w, h = x1 - x0, y1 - y0
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    colour = (*info["colour"], 255)
    title = spaced(info["title"], info["case"]) if info["case"] == "upper" else info["title"]
    author = info["author"].upper() if info["case"] == "upper" else info["author"]
    margin = 12
    af = fit_font(d, author, "sans" if info["family"].startswith("sans") else "serif", 17, 130)
    aw = int(d.textlength(author, font=af))
    mark_w = 14
    tf = fit_font(d, title, info["family"], 30 if info["case"] == "upper" else 34, w - 2 * margin - aw - mark_w - 40)
    tb = d.textbbox((0, 0), title, font=tf)
    ty = (h - (tb[3] - tb[1])) // 2 - tb[1]
    d.text((margin + 6, ty), title, font=tf, fill=colour)
    ab = d.textbbox((0, 0), author, font=af)
    ay = (h - (ab[3] - ab[1])) // 2 - ab[1]
    ax = w - margin - mark_w - 14 - aw
    d.text((ax, ay), author, font=af, fill=colour)
    # the publisher's mark: a small ring at the foot of the spine
    cx, cy, r = w - margin - mark_w // 2, h // 2, 5
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=colour, width=2)
    img.alpha_composite(layer, (x0, y0))


def draw_word_label(img: Image.Image, name: str, word: str, small: str) -> None:
    x0, y0, x1, y1 = PL.label_box_px(name)
    w, h = x1 - x0, y1 - y0
    layer = Image.new("RGBA", (w, h), PAPER)
    d = ImageDraw.Draw(layer)
    d.rectangle((10, 10, w - 11, h - 11), outline=RULE, width=2)
    d.rectangle((16, 16, w - 17, h - 17), outline=RULE, width=1)
    wf = fit_font(d, word, "serif_bold", 54, w - 50)
    wb = d.textbbox((0, 0), word, font=wf)
    d.text(((w - (wb[2] - wb[0])) // 2 - wb[0], h * 0.40 - (wb[3] - wb[1]) / 2 - wb[1]), word, font=wf, fill=INK)
    sf = fit_font(d, small, "serif", 26, w - 60)
    sb = d.textbbox((0, 0), small, font=sf)
    d.text(((w - (sb[2] - sb[0])) // 2 - sb[0], h * 0.66 - sb[1]), small, font=sf, fill=RULE)
    d.line((w * 0.3, h * 0.58, w * 0.7, h * 0.58), fill=RULE, width=2)
    img.alpha_composite(layer, (x0, y0))


def draw_wine_label(img: Image.Image, name: str, winery: str, year: str, kind: str) -> None:
    x0, y0, x1, y1 = PL.label_box_px(name)
    w, h = x1 - x0, y1 - y0
    layer = Image.new("RGBA", (w, h), PAPER_WHITE)
    d = ImageDraw.Draw(layer)
    d.rectangle((8, 8, w - 9, h - 9), outline=INK, width=1)
    # a small drawn crest: a ring and a line
    d.ellipse((w // 2 - 22, 26, w // 2 + 22, 70), outline=INK, width=2)
    d.line((w // 2 - 12, 48, w // 2 + 12, 48), fill=INK, width=2)
    wf = fit_font(d, winery.upper(), "serif_bold", 34, w - 36)
    wb = d.textbbox((0, 0), winery.upper(), font=wf)
    d.text(((w - (wb[2] - wb[0])) // 2 - wb[0], 92 - wb[1]), winery.upper(), font=wf, fill=INK)
    yf = font("serif", 40)
    yb = d.textbbox((0, 0), year, font=yf)
    d.text(((w - (yb[2] - yb[0])) // 2 - yb[0], 140 - yb[1]), year, font=yf, fill=(120, 30, 40, 255))
    kf = fit_font(d, kind, "serif", 26, w - 40)
    kb = d.textbbox((0, 0), kind, font=kf)
    d.text(((w - (kb[2] - kb[0])) // 2 - kb[0], 198 - kb[1]), kind, font=kf, fill=INK)
    img.alpha_composite(layer, (x0, y0))


def make(out: Path) -> Path:
    img = Image.new("RGBA", (PL.ATLAS_PX, PL.ATLAS_PX), (0, 0, 0, 0))
    for k in range(PL.STRIPS):
        draw_strip(img, k)
    for name, word, small in PL.WORD_LABELS:
        draw_word_label(img, name, word, small)
    for name, winery, year, kind in PL.WINE_LABELS:
        draw_wine_label(img, name, winery, year, kind)
    # the transparent corner every unprinted face samples
    cx, cy = PL.CLEAR_PX
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if 0 <= cx + dx < PL.ATLAS_PX and 0 <= cy + dy < PL.ATLAS_PX:
                img.putpixel((cx + dx, cy + dy), (0, 0, 0, 0))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, optimize=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(PL.ATLAS_PATH))
    args = ap.parse_args()
    path = make(Path(args.out))
    print(f"print atlas: {path} ({path.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
