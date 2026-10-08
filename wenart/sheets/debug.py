"""Debug image per sheet (docs/milestone10.md §3.1 item 9): ``<out>/sheets_debug/<file>_<sheet>.png``.

What: the sheet drawn in light grey, every region boxed and labelled with its id, class, level and variant (and its
registration residual), coloured by how its class was decided (title green, geometry blue, AI orange, none red;
thinner and lighter for a lower confidence), frames dashed, strays circled (a stray outside the picture is drawn at
the picture's edge with its distance).

Why: CLAUDE.md asks for a debug image per page with what was detected drawn over the original.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wenart.ingest.debug_image import _dashed_line, _font

METHOD_COLOURS = {"title": (0, 150, 0), "geometry": (30, 90, 220), "ai": (235, 130, 0), "none": (220, 20, 20)}
STRAY_COLOUR = (200, 0, 200)
MAX_PX = 2000


def sheet_image(sheet, regions: list, strays: list, out_path: Path, max_px: int = MAX_PX) -> Path:
    boxes = [r.box for r in regions] + [f["box"] for f in sheet.frames]
    if sheet.box:
        boxes.append(sheet.box)
    x0 = min(b[0] for b in boxes)
    y0 = min(b[1] for b in boxes)
    x1 = max(b[2] for b in boxes)
    y1 = max(b[3] for b in boxes)
    w, h = max(x1 - x0, 1e-9), max(y1 - y0, 1e-9)
    margin = 40
    scale = (max_px - 2 * margin) / max(w, h)
    size = (int(w * scale) + 2 * margin, int(h * scale) + 2 * margin + 60)
    img = Image.new("RGB", size, (255, 255, 255))
    draw = ImageDraw.Draw(img)

    def px(p):
        return ((p[0] - x0) * scale + margin, (y1 - p[1]) * scale + margin)

    for r in regions:
        for e in r.ents:
            for st in e.strokes:
                pts = [px(p) for p in st.pts]
                if len(pts) >= 2:
                    draw.line(pts + ([pts[0]] if st.closed and len(pts) > 2 else []), fill=(185, 185, 185), width=1)
    for f in sheet.frames:
        b = f["box"]
        corners = [px((b[0], b[1])), px((b[2], b[1])), px((b[2], b[3])), px((b[0], b[3]))]
        for a, c in zip(corners, corners[1:] + corners[:1]):
            _dashed_line(draw, a, c, (90, 90, 90), 2)
    font = _font(15)
    for r in regions:
        colour = METHOD_COLOURS.get(r.class_method, METHOD_COLOURS["none"])
        width = 4 if r.class_confidence >= 0.9 else 3 if r.class_confidence >= 0.7 else 2
        if r.status == "unverified":
            colour = METHOD_COLOURS["none"]
        b = r.box
        p0, p1 = px((b[0], b[3])), px((b[2], b[1]))
        draw.rectangle([p0, p1], outline=colour, width=width)
        label = f"{r.id} {r.cls}"
        if r.level:
            label += f" {r.level['id']}"
        if r.variant and r.variant != "base":
            label += f" [{r.variant}]"
        if r.registration and r.registration.get("residual_m") is not None and r.registration["method"] != "reference":
            label += f" res {r.registration['residual_m']:.3f} m"
        label += f" ({r.class_method}, {r.use})"
        draw.text((p0[0] + 4, p0[1] + 4), label, fill=colour, font=font)
    for c, dist, entity in strays:
        b = c
        cx, cy = px(((b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0))
        cx = min(max(cx, 12), size[0] - 12)
        cy = min(max(cy, 12), size[1] - 72)
        draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], outline=STRAY_COLOUR, width=3)
        draw.text((cx + 12, cy - 8), f"stray {entity} ({dist:.0f} m)", fill=STRAY_COLOUR, font=font)
    note = (f"{sheet.file} {sheet.id} ({sheet.space}): {len(regions)} regions, {len(strays)} strays, gap "
            f"{(sheet.gap or 0):.4g} units | class by title green, geometry blue, AI orange, none / unverified red")
    draw.text((margin, size[1] - 40), note, fill=(0, 0, 0), font=font)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="PNG")
    return out_path
