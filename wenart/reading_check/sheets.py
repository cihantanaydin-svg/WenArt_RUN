"""The reading check's comparison sheets (2 Nov 2026; user: "Give those together also model and what came from the
pod", "go ahead with all 4").

What: ``draw(out_dir, result)`` writes, per level read from a CAD region (a typical floor's copies share its sheet),
``reading_check/compare_<level>.jpg``: 1 the source drawing (the region of the converted DXF), 2 the model's plan in the
drawing's orientation (rooms, walls, doors green, windows blue, stairs purple), 3 the model's walls (red) over the
drawing (grey) with the findings marked (drawn wall faces the model lacks orange, model walls on no drawn line
magenta, area mismatches with their numbers), 4 the pod's top-down render when ``renders`` holds ``top_<level>_plan.jpg``.

How: the model is mapped into the drawing's units by the inverse of each level's page transform (what the model used);
the drawing is drawn by ezdxf's matplotlib backend (white background, black lines).
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Optional

from wenart import reading_check as RC


def _inverse(t):
    a, b, c, d, e, f = t
    det = a * e - b * d
    return lambda x, y: ((e * (x - c) - b * (y - f)) / det, (-d * (x - c) + a * (y - f)) / det)


def _entities(doc, box):
    out = []
    for e in doc.modelspace():
        try:
            t = e.dxftype()
            if t == "LINE":
                p = (e.dxf.start.x, e.dxf.start.y)
            elif t in ("INSERT", "TEXT", "MTEXT"):
                p = (e.dxf.insert.x, e.dxf.insert.y)
            elif t in ("CIRCLE", "ARC"):
                p = (e.dxf.center.x, e.dxf.center.y)
            elif t == "LWPOLYLINE":
                p = tuple(next(iter(e.get_points("xy")))[:2])
            elif t == "DIMENSION":
                p = (e.dxf.defpoint.x, e.dxf.defpoint.y)
            else:
                continue
        except Exception:  # noqa: BLE001 - an entity without the point: left out of the drawing
            continue
        if box[0] <= p[0] <= box[2] and box[1] <= p[1] <= box[3]:
            out.append(e)
        elif t == "INSERT" and _overlaps(e, box):
            out.append(e)                     # real03: the whole plan is one block inserted away from its points
    return out


def _overlaps(insert, box) -> bool:
    from ezdxf import bbox

    try:
        ext = bbox.extents([insert], fast=True)
    except Exception:  # noqa: BLE001 - a block without extents: left out
        return False
    if not ext.has_data:
        return False
    return not (ext.extmax.x < box[0] or ext.extmin.x > box[2] or ext.extmax.y < box[1] or ext.extmin.y > box[3])


def _draw_drawing(ax, doc, ents, box, grey: bool = False):
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.config import BackgroundPolicy, ColorPolicy, Configuration
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

    cfg = Configuration(background_policy=BackgroundPolicy.WHITE,
                        color_policy=ColorPolicy.CUSTOM if grey else ColorPolicy.BLACK,
                        custom_fg_color="#b4b4b4", lineweight_scaling=0.4 if grey else 0.5)
    Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_entities(ents)
    _frame(ax, box)


def _frame(ax, box):
    ax.set_xlim(box[0], box[2])
    ax.set_ylim(box[1], box[3])
    ax.set_aspect("equal")
    ax.axis("off")


def _draw_model(ax, building, level, tf, box, colour=True, labels=True):
    from shapely.geometry import Polygon

    inv = _inverse(tf)
    scale = 1.0 / math.hypot(tf[0], tf[3])
    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") == level}
    for room in building.get("rooms") or []:
        if room.get("level_id") != level or not room.get("polygon"):
            continue
        pts = [inv(*p) for p in room["polygon"]]
        xs, ys = zip(*(pts + pts[:1]))
        if colour:
            ax.fill(xs, ys, color="#fff3c4", alpha=0.6, lw=0)
        ax.plot(xs, ys, color="#c9a227", lw=0.5)
        if labels:
            c = Polygon(pts).representative_point()
            ax.text(c.x, c.y, f"{room.get('label') or ''}\n({room.get('room_type') or '?'})", fontsize=4.5,
                    ha="center", va="center", color="#6b4f00", clip_on=True)
    # 3 Nov 2026 (user: "are you showing the balkons here?"): the level's balconies and terraces, green
    for osp in (building.get("site") or {}).get("outdoor_spaces") or []:
        if osp.get("level_id") != level or not osp.get("polygon"):
            continue
        pts = [inv(*p) for p in osp["polygon"]]
        xs, ys = zip(*(pts + pts[:1]))
        if colour:
            ax.fill(xs, ys, color="#c8e6c9", alpha=0.8, lw=0)
        ax.plot(xs, ys, color="#2e7d32", lw=0.8, ls="-" if colour else "--")
        if labels:
            c = Polygon(pts).representative_point()
            ax.text(c.x, c.y, f"{osp.get('label') or ''}\n({osp.get('kind') or ''})", fontsize=4.5, ha="center",
                    va="center", color="#1b5e20", clip_on=True)
    for w in walls.values():
        (x0, y0), (x1, y1) = inv(*w["start"]), inv(*w["end"])
        lw = max(0.6, min(4.5, float(w.get("thickness") or 0.2) * scale * 3000))
        # 3 Nov 2026 (user: "use my vision and understanding to reinforce the decision"): what the reading inferred
        # (no drawn wall there) is orange, so the user can check every inference against the drawing
        col = INFERRED_COLOUR if _inferred(w) else ("#222222" if colour else "#c62828")
        ax.plot([x0, x1], [y0, y1], color=col, lw=lw, solid_capstyle="butt")
    for o in building.get("openings") or []:
        w = walls.get(o.get("wall_id"))
        if o.get("level_id") != level or not w or not o.get("center"):
            continue
        dx, dy = w["end"][0] - w["start"][0], w["end"][1] - w["start"][1]
        n = math.hypot(dx, dy) or 1.0
        half = float(o.get("width") or 0.9) / 2.0
        cx, cy = o["center"]
        p0, p1 = inv(cx - dx / n * half, cy - dy / n * half), inv(cx + dx / n * half, cy + dy / n * half)
        col = {"window": "#1565c0", "door": "#2e7d32"}.get(o.get("type"), "#8e24aa")
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=col, lw=3.2, solid_capstyle="butt",
                ls=(0, (2, 1)) if _inferred(o) else "-")
    _frame(ax, box)


INFERRED_COLOUR = "#ef6c00"


def _inferred(item: dict) -> bool:
    """A wall or opening the reading inferred (evidence method ``inferred``): drawn orange / dashed."""
    return bool(item.get("inferred")) or any(isinstance(e, dict) and e.get("method") == "inferred"
                                             for e in item.get("evidence") or [])


def _mark_findings(ax, findings, building, level, tf):
    inv = _inverse(tf)
    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") == level}
    for f in findings:
        if f.get("level_id") != level:
            continue
        if f["check"] == "RC4":
            for a, b in f.get("pieces") or []:
                p0, p1 = inv(*a), inv(*b)
                ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color="#fdd835", lw=3.0, alpha=0.9)
        elif f["check"] == "RC5" and f.get("wall_id") in walls:
            w = walls[f["wall_id"]]
            p0, p1 = inv(*w["start"]), inv(*w["end"])
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color="#d500f9", lw=4.0, alpha=0.9)
        elif f["check"] == "RC3" and f.get("at"):
            p = inv(*f["at"])
            ax.text(p[0], p[1], f"drawn {f['drawn_m2']:.1f} / model {f['model_m2']:.1f} m2", fontsize=6,
                    color="#b71c1c", ha="center", bbox={"facecolor": "white", "alpha": 0.8, "lw": 0})


def _model_box(building, level, tf, margin: float = 0.08):
    """A one-plan document (no sheet region, 2 Nov 2026): the box of the level's walls and rooms in the drawing's
    units, with a margin."""
    inv = _inverse(tf)
    pts = [inv(*p) for w in building.get("walls") or [] if w.get("level_id") == level for p in (w["start"], w["end"])]
    pts += [inv(*p) for r in building.get("rooms") or [] if r.get("level_id") == level for p in r.get("polygon") or []]
    if not pts:
        return None
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    m = margin * max(max(xs) - min(xs), max(ys) - min(ys))
    return [min(xs) - m, min(ys) - m, max(xs) + m, max(ys) + m]


def _combine(paths, titles, dest, header):
    from PIL import Image, ImageDraw, ImageFont

    ims = [Image.open(p).convert("RGB") for p in paths]
    w = 1200
    ims = [im.resize((w, int(im.height * w / im.width))) for im in ims]
    h = max(im.height for im in ims)
    sheet = Image.new("RGB", (w * 2 + 30, (h + 40) * ((len(ims) + 1) // 2) + 60), "white")
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 26)
        small = ImageFont.truetype("DejaVuSans.ttf", 22)
    except OSError:
        font = small = ImageFont.load_default()
    d.text((10, 12), header, fill="black", font=font)
    for k, (im, t) in enumerate(zip(ims, titles)):
        x, y = (k % 2) * (w + 30), 60 + (k // 2) * (h + 40)
        d.text((x + 5, y), t, fill="#333333", font=small)
        sheet.paste(im, (x, y + 30))
    sheet.save(dest, quality=88)


def draw(out_dir, result: Optional[dict] = None, renders: Optional[str] = None) -> list:
    """The comparison sheets (the module docstring); returns their paths."""
    import ezdxf
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir = Path(out_dir)
    building = json.loads((out_dir / "building.json").read_text(encoding="utf-8"))
    sp = out_dir / "sheets.json"
    sheets = json.loads(sp.read_text(encoding="utf-8")) if sp.is_file() else {}
    result = result or RC.check(out_dir)
    regions = {r["id"]: r for r in sheets.get("regions") or []}
    levels = {lv["id"]: lv for lv in building.get("levels") or []}
    d = out_dir / "reading_check"
    d.mkdir(parents=True, exist_ok=True)
    docs: dict = {}
    made = []
    for lid, pg in RC.level_pages(building).items():
        reg = regions.get(pg.get("region"))
        dxf = RC.source_dxf(out_dir, pg["file"])
        if dxf is None or (reg is None and pg.get("region")):
            continue
        if dxf not in docs:
            docs[dxf] = ezdxf.readfile(str(dxf))
        doc = docs[dxf]
        box = reg["box"] if reg is not None else _model_box(building, lid, pg["tf"])
        if box is None:
            continue
        ents = _entities(doc, box)
        title = (((reg or {}).get("title") or {}).get("text") or (reg or {}).get("id") or pg["file"]).strip()
        panels = []
        for k, (name, fn) in enumerate((
                ("1 the source drawing", lambda ax: _draw_drawing(ax, doc, ents, box)),
                ("2 the model's plan (rooms yellow, balconies and terraces green; walls black, inferred walls orange; "
                 "doors green, windows blue, other openings purple, inferred openings dashed)",
                 lambda ax: _draw_model(ax, building, lid, pg["tf"], box)),
                ("3 the model's walls over the drawing (grey): drawn red, inferred orange; findings: drawn walls the "
                 "model lacks yellow, walls on no drawn line magenta",
                 lambda ax: (_draw_drawing(ax, doc, ents, box, grey=True),
                             _draw_model(ax, building, lid, pg["tf"], box, colour=False, labels=False),
                             _mark_findings(ax, result["findings"], building, lid, pg["tf"]))))):
            fig, ax = plt.subplots(figsize=(9, 9))
            fn(ax)
            p = d / f"_{lid}_{k + 1}.png"
            fig.savefig(p, dpi=200, bbox_inches="tight", facecolor="white")
            plt.close(fig)
            panels.append((p, name))
        top = Path(renders) / f"top_{lid}_plan.jpg" if renders else None
        if top is not None and top.is_file():
            panels.append((top, "4 the pod's top-down render"))
        copies = [k for k, lv in levels.items() if lv.get("typical_of") == lid]
        n = sum(1 for f in result["findings"] if f.get("level_id") == lid)
        header = (f"{building.get('project', {}).get('id')} {lid}: {title}"
                  + (f" (also {', '.join(copies)})" if copies else "") + f": {n} finding(s)")
        dest = d / f"compare_{lid}.jpg"
        _combine([p for p, _ in panels], [t for _, t in panels], dest, header)
        for p, _ in panels:
            if p.parent == d and p.name.startswith("_"):
                p.unlink()
        made.append(dest)
    return made
