"""Room names on the top-down level views (``wenart/blender/topdown.py``; user request of 25 Oct 2026).

``python -m wenart.report.topdown_labels <building.json> <dir> [--out DIR]``: for every ``top_<level>.png`` with its
``.frame.json`` in ``dir`` writes ``top_<level>_plan.jpg`` with each room's name and type at its middle floor point
(projected through the view's frame for an angled view), every window as a blue line with its id at the top of the
cut walls (25 Oct 2026: the walls are cut at half the earlier height, below most sills) and a title bar (level, floor
height, where the view comes from)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MAX_SIDE = 1400
MAX_BYTES = 280 * 1024          # under the results copy's 300 KiB (wenart.run.copy.MAX_JPEG_BYTES)
WINDOW_RGB = (40, 120, 230)
COMPASS = ("north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west")


def seen_from(azimuth_deg: float) -> str:
    """The compass side the camera stands on: the view looks toward ``azimuth_deg`` (0 = north, clockwise)."""
    return COMPASS[int(round(((float(azimuth_deg) + 180.0) % 360.0) / 45.0)) % 8]


def window_lines(building: dict, level_id: str) -> list[tuple[str, tuple, tuple]]:
    """``[(id, (x0, y0), (x1, y1))]``: each window of the level along its wall (pure)."""
    from wenart.blender.shell import opening_centre_on_wall
    from wenart.geometry import distance

    walls = {w["id"]: w for w in building.get("walls") or []}
    out = []
    for o in building.get("openings") or []:
        w = walls.get(o.get("wall_id"))
        if o.get("type") != "window" or o.get("level_id") != level_id or w is None:
            continue
        cx, cy, _ = opening_centre_on_wall(o, w)
        length = distance(w["start"], w["end"]) or 1.0
        ux, uy = (w["end"][0] - w["start"][0]) / length, (w["end"][1] - w["start"][1]) / length
        half = float(o.get("width") or 0.0) / 2.0
        out.append((str(o["id"]), (cx - ux * half, cy - uy * half), (cx + ux * half, cy + uy * half)))
    return out


def as_built(building: dict, architect_json=None) -> dict:
    """``building`` with the openings the architect's answers moved, resized or added as the build made them
    (``scene/architect.json`` ``openings_changed``); unchanged without the file."""
    if not architect_json or not Path(architect_json).is_file():
        return building
    changed = json.loads(Path(architect_json).read_text(encoding="utf-8")).get("openings_changed") or []
    if not changed:
        return building
    by = {o["id"]: o for o in changed}
    out = dict(building)
    out["openings"] = [by.pop(o["id"], o) for o in building.get("openings") or []] + list(by.values())
    return out


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

    def px(x, y, z=0.05):
        if "right" in fr:                                  # the angled view: project the point (z over the floor)
            p = (x - fr["target"][0], y - fr["target"][1], float(fr["elevation"]) + z - fr["target"][2])
            u = sum(a * b for a, b in zip(p, fr["right"]))
            v = sum(a * b for a, b in zip(p, fr["up"]))
            span = max(fr["umax"] - fr["umin"], fr["vmax"] - fr["vmin"])
            uc, vc = (fr["umin"] + fr["umax"]) / 2.0, (fr["vmin"] + fr["vmax"]) / 2.0
            scale = max(w, h) / span
            return w / 2.0 + (u - uc) * scale, h / 2.0 - (v - vc) * scale
        return (x - fr["x0"]) / (fr["x1"] - fr["x0"]) * w, (fr["y1"] - y) / (fr["y1"] - fr["y0"]) * h

    small = font
    try:
        small = ImageFont.truetype(FONT, max(10, w // 120))
    except OSError:
        pass
    top = float(fr.get("wall_cut_m") or 0.6) if fr.get("tilt_deg") else 0.05
    for wid, a, b in window_lines(building, level_id):
        pa, pb = px(*a, z=top), px(*b, z=top)
        dr.line((pa, pb), fill=WINDOW_RGB, width=max(3, w // 300))
        mid = ((pa[0] + pb[0]) / 2.0, (pa[1] + pb[1]) / 2.0 - max(8, w // 150))
        dr.text(mid, wid.replace(f"win_{level_id}_", "w"), font=small, fill=WINDOW_RGB, anchor="mm",
                stroke_width=2, stroke_fill=(255, 255, 255))
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
    view = (f"ceilings off, seen from the {seen_from(fr.get('azimuth_deg') or 0.0)}, {float(fr['tilt_deg']):g} deg "
            f"from above, walls cut at {float(fr.get('wall_cut_m') or 0.6):.1f} m, windows in blue"
            if fr.get("tilt_deg") else "ceilings off, north up")
    line = int(w / 30) + 6
    dr.rectangle((0, 0, w, line + int(w / 55) + 12), fill=(30, 30, 30))
    dr.text((12, 6), f"{level_id}  floor {floor:+.2f} m", font=big, fill=(255, 255, 255))
    dr.text((12, line + 4), view, font=font, fill=(225, 225, 225))
    if max(w, h) > MAX_SIDE:                       # the results copy keeps previews under 300 KB
        k = MAX_SIDE / max(w, h)
        im = im.resize((int(w * k), int(h * k)), Image.LANCZOS)
    # 25 Oct 2026: a view with more labels came out over the copy's 300 KiB and the pod's results kept an older
    # copy; the quality steps down until the file is under MAX_BYTES
    for quality in (82, 76, 70, 64, 58, 52):
        im.save(out, quality=quality)
        if Path(out).stat().st_size <= MAX_BYTES:
            break
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("building")
    ap.add_argument("dir")
    ap.add_argument("--out", default=None)
    ap.add_argument("--architect", default=None, help="the scene's architect.json (the openings as built)")
    a = ap.parse_args(argv)
    building = as_built(json.loads(Path(a.building).read_text(encoding="utf-8")), a.architect)
    src = Path(a.dir)
    dst = Path(a.out or a.dir)
    dst.mkdir(parents=True, exist_ok=True)
    for png in sorted(src.glob("top_*.png")):
        lid = png.stem[len("top_"):]
        print(label(building, lid, png, dst / f"top_{lid}_plan.jpg"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
