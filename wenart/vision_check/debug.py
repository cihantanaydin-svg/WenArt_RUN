"""Debug images of the vision check (docs/milestone5.md §5.7).

``check/<cam>_<kind>_check.jpg`` (<= 300 KB, ``:`` in the kind becomes ``-``):
the checked image with every asked element's expected box coloured by its
combined result (ok green, missing/changed red, disputed orange,
unverified grey dashed, not computed grey dotted), the decoy box (magenta
dashed; "SEEN" when a pass accepted it), the confirmed extras (blue) and
``id type source`` labels. Pillow is imported inside the functions.
"""
from __future__ import annotations

from pathlib import Path

from wenart import geometry as G
from wenart.recognition.vlm_client import norm1000_to_pixels
from wenart.vision_check.plan_crop import save_jpeg

MAX_WIDTH = 1280
RESULT_COLOURS = {
    "ok": (0, 170, 0),
    "missing": (220, 20, 20), "changed": (220, 20, 20), "missing_or_changed": (220, 20, 20),
    "disputed": (240, 140, 0),
    "unverified": (150, 150, 150),
    "not_computed": (110, 110, 110),
}
DECOY_COLOUR = (200, 0, 200)
EXTRA_COLOUR = (30, 90, 220)


def _dashed_rect(draw, box, fill, width: int, dash: float = 10.0, gap: float = 6.0) -> None:
    x0, y0, x1, y1 = box
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    for a, b in zip(corners[:-1], corners[1:]):
        length = G.distance(a, b)
        pos = 0.0
        while pos < length:
            end = min(pos + dash, length)
            draw.line([G.point_at_distance(a, b, pos), G.point_at_distance(a, b, end)], fill=fill, width=width)
            pos = end + gap


def draw_check(image_path: Path, entry: dict, camera: str, kind: str):
    """The annotated PIL image of one check entry (full size; ``write_check_image`` downsizes)."""
    from PIL import Image, ImageDraw

    from wenart.vision_check.plan_crop import _font

    with Image.open(image_path) as im:
        base = im.convert("RGB")
    W, H = base.size
    draw = ImageDraw.Draw(base)
    font = _font(max(10, W // 90))
    fs = int(getattr(font, "size", 11))
    lw = max(2, W // 640)
    for eid, e in sorted(entry.get("elements", {}).items(), key=lambda kv: kv[1]["label"]):
        box = norm1000_to_pixels(e["box_1000"], W, H)
        colour = RESULT_COLOURS.get(e["result"], (110, 110, 110))
        if e["result"] in ("unverified", "not_computed"):
            _dashed_rect(draw, box, colour, lw, *((10.0, 6.0) if e["result"] == "unverified" else (3.0, 5.0)))
        else:
            draw.rectangle(box, outline=colour, width=lw + (1 if e["role"] == "required" else 0))
        label = f"{e['label']} {eid} {e['type']} {e.get('source') or '-'}: {e['result']}"
        draw.text((box[0] + 3, box[1] + 2), label, fill=colour, font=font)
    decoy = entry.get("decoy")
    if decoy:
        box = norm1000_to_pixels(decoy["box_1000"], W, H)
        _dashed_rect(draw, box, DECOY_COLOUR, lw)
        seen = f" SEEN by {', '.join(decoy['accepted_by'])}" if decoy.get("accepted_by") else ""
        draw.text((box[0] + 3, box[1] + 2), f"{decoy['label']} decoy {decoy['type']}{seen}", fill=DECOY_COLOUR,
                  font=font)
    for x in entry.get("extras") or []:
        if not x.get("confirmed"):
            continue
        cats = "/".join(sorted(set(x["categories"].values())))
        draw.rectangle(x["box_px"], outline=EXTRA_COLOUR, width=lw)
        draw.text((x["box_px"][0] + 3, x["box_px"][3] - fs - 4), f"extra {x['class']} {cats}", fill=EXTRA_COLOUR,
                  font=font)
    note = f"{camera} | {kind} | verdict {entry.get('verdict')}"
    if entry.get("unreliable"):
        note += f" | unreliable: {', '.join(entry['unreliable'])}"
    if entry.get("not_computed"):
        note += f" | not computed: {', '.join(entry['not_computed'])}"
    draw.rectangle([0, 0, W, fs + 10], fill=(255, 255, 255))
    draw.text((6, 4), note, fill=(0, 0, 0), font=font)
    return base


def write_check_image(image_path: Path, entry: dict, camera: str, kind: str, out_path: Path) -> Path:
    """Draw, downscale to <= ``MAX_WIDTH`` px wide and save as a JPEG <= 300 KB."""
    from PIL import Image

    img = draw_check(image_path, entry, camera, kind)
    if img.width > MAX_WIDTH:
        img = img.resize((MAX_WIDTH, max(1, round(img.height * MAX_WIDTH / img.width))), Image.LANCZOS)
    return save_jpeg(img, out_path)
