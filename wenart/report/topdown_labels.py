"""Room names on the top-down level views (``wenart/blender/topdown.py``; user request of 25 Oct 2026).

``python -m wenart.report.topdown_labels <building.json> <dir> [--out DIR]``: for every ``top_<level>.png`` with its
``.frame.json`` in ``dir`` writes ``top_<level>.jpg`` with each room's name and type at its middle and a title bar
(level, floor height, "ceilings off, north up")."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def label(building: dict, level_id: str, image: Path, out: Path) -> Path:
    from PIL import Image, ImageDraw, ImageFont

    fr = json.loads(Path(str(image) + ".frame.json").read_text(encoding="utf-8"))
    im = Image.open(image).convert("RGB")
    w, h = im.size
    dr = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype(FONT, max(14, w // 80))
        big = ImageFont.truetype(FONT, max(20, w // 45))
    except OSError:
        font = big = ImageFont.load_default()

    def px(x, y):
        return (x - fr["x0"]) / (fr["x1"] - fr["x0"]) * w, (fr["y1"] - y) / (fr["y1"] - fr["y0"]) * h

    for r in building.get("rooms") or []:
        poly = r.get("polygon") or []
        if r.get("level_id") != level_id or len(poly) < 3:
            continue
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        name = str(r.get("name") or r["id"]).replace(f"r_{level_id}_", "").replace("_", " ")
        text = f"{name}\n({r.get('room_type')})"
        x, y = px(cx, cy)
        box = dr.multiline_textbbox((x, y), text, font=font, anchor="mm", align="center")
        dr.rectangle((box[0] - 4, box[1] - 3, box[2] + 4, box[3] + 3), fill=(255, 255, 255))
        dr.multiline_text((x, y), text, font=font, fill=(20, 20, 20), anchor="mm", align="center")
    level = next((lv for lv in building.get("levels") or [] if lv["id"] == level_id), None)
    floor = float(level["elevation"]) if level else float(fr.get("elevation") or 0.0)
    dr.rectangle((0, 0, w, int(w / 30) + 10), fill=(30, 30, 30))
    dr.text((12, 6), f"{level_id}  floor {floor:+.2f} m  (ceilings off, north up)", font=big, fill=(255, 255, 255))
    im.save(out, quality=88)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("building")
    ap.add_argument("dir")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    building = json.loads(Path(a.building).read_text(encoding="utf-8"))
    src = Path(a.dir)
    dst = Path(a.out or a.dir)
    dst.mkdir(parents=True, exist_ok=True)
    for png in sorted(src.glob("top_*.png")):
        lid = png.stem[len("top_"):]
        print(label(building, lid, png, dst / f"top_{lid}.jpg"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
