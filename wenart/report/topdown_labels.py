"""Room names on the top-down level views (``wenart/blender/topdown.py``; user request of 25 Oct 2026).

``python -m wenart.report.topdown_labels <building.json> <dir> [--out DIR]``: for every ``top_<level>.png`` with its
``.frame.json`` in ``dir`` writes ``top_<level>_plan.jpg`` with each room's name and type at its middle floor point
(projected through the view's frame for an angled view) and a title bar (level, floor height, the view)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MAX_SIDE = 1400


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
        if "right" in fr:                                  # the angled view: project the floor point
            p = (x - fr["target"][0], y - fr["target"][1], float(fr["elevation"]) + 0.05 - fr["target"][2])
            u = sum(a * b for a, b in zip(p, fr["right"]))
            v = sum(a * b for a, b in zip(p, fr["up"]))
            span = max(fr["umax"] - fr["umin"], fr["vmax"] - fr["vmin"])
            uc, vc = (fr["umin"] + fr["umax"]) / 2.0, (fr["vmin"] + fr["vmax"]) / 2.0
            scale = max(w, h) / span
            return w / 2.0 + (u - uc) * scale, h / 2.0 - (v - vc) * scale
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
    view = (f"seen from the south, {float(fr['tilt_deg']):g} deg from above" if fr.get("tilt_deg")
            else "north up")
    dr.text((12, 6), f"{level_id}  floor {floor:+.2f} m  (ceilings off, {view})", font=big, fill=(255, 255, 255))
    if max(w, h) > MAX_SIDE:                       # the results copy keeps previews under 300 KB
        k = MAX_SIDE / max(w, h)
        im = im.resize((int(w * k), int(h * k)), Image.LANCZOS)
    im.save(out, quality=82)
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
        print(label(building, lid, png, dst / f"top_{lid}_plan.jpg"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
