"""The reading self-check: the model the reading made, checked against the drawing, before any pod run (2 Nov 2026).

What: ``check(out_dir)`` reads a pipeline output (``building.json``, ``sheets.json`` and the converted DXF of each
CAD document) and returns the findings, each with its check, severity, level and place:

- RC1 a level left out of the model (critical);
- RC2 floors that do not stack: the shared axis grid's axes (the labelled bubbles) and the core's stair (the same
  concentric arcs) of each level against the reference level's, in the building frame (critical over 0.30 m, major
  over ``STACK_TOL_M``);
- RC3 a room whose area differs from the drawing's own area text in it (``220.60 m2``; major over 5 % and 1 m2);
- RC4 drawn wall lines the model does not build (the strokes of the layers whose name means wall, plaster or column,
  ``generic.layer_names``; major over ``MISSING_MAJOR_M`` of wall face per level);
- RC5 model walls on no drawn wall line (major; inferred walls are listed apart);
- RC6 the reading's own review reasons (needs review) and the labels it found outside the building (major).

``verdict``: ``ready`` without a critical finding, else ``fix before a pod run``. ``write(out_dir, result)`` writes
``reading_check/reading_check.json`` and ``.md``; ``wenart.reading_check.sheets`` draws the comparison sheets (the
drawing, the model in the drawing's orientation, the model's walls over the drawing, the findings marked).

Why: real10 (user: "We need to improve this initial project reading part currently it is requiring a lot of fixing",
"go ahead with all 4"): the floors did not stack, the 2nd basement was left out and the axis lines were read as walls,
and nothing saw it until a pod had rendered the model ($10+, 5 h). The check runs here, on the CPU, in minutes.

How: pure reading of the files; the drawing's strokes come from the same DXF reader as the reading
(``ingest.dxf_generic``), mapped by each level's page transform from ``building.json`` (what the model used).
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Optional

STACK_TOL_M = 0.05
STACK_CRITICAL_M = 0.30
AREA_TOL_SHARE = 0.05
AREA_TOL_M2 = 1.0
WALL_NEAR_M = 0.12            # a drawn face line this far beyond a model wall's half thickness still counts as built
MISSING_MAJOR_M = 3.0         # a level's drawn wall face the model lacks, in metres, before it is a major finding
MISSING_PIECE_M = 1.0         # pieces shorter than this are not listed one by one
DRAWN_SHARE_MIN = 0.5         # a model wall with less than this share of its length along drawn lines is not drawn
SEGMENT_MIN_M = 0.3
AREA_RE = re.compile(r"(\d{1,4}[.,]\d{1,2})\s*(?:M2|M²|M\^2)\b", re.IGNORECASE)
CHECKS = {"RC1": "level left out", "RC2": "floors do not stack", "RC3": "room area against the drawing's area text",
          "RC4": "drawn walls the model does not build", "RC5": "model walls on no drawn wall line",
          "RC6": "the reading's own review reasons"}


def _finding(check: str, severity: str, level: Optional[str], message: str, **extra) -> dict:
    return dict({"check": check, "name": CHECKS[check], "severity": severity, "level_id": level,
                 "message": message}, **extra)


def _apply(tf, p):
    return (tf[0] * p[0] + tf[1] * p[1] + tf[2], tf[3] * p[0] + tf[4] * p[1] + tf[5])


def level_pages(building: dict) -> dict:
    """``{level_id: {"region", "file", "tf"}}`` of the levels read from a CAD region (the page transform the model
    used); a typical floor's copies are left out (their plan is the typical floor's)."""
    levels = {lv["id"]: lv for lv in building.get("levels") or []}
    out = {}
    for doc in building.get("documents") or []:
        for pg in doc.get("pages") or []:
            lid, tf = pg.get("level_id"), pg.get("transform_to_building")
            if not lid or not tf or lid in out:
                continue
            if (levels.get(lid) or {}).get("typical_of"):
                continue
            out[lid] = {"region": pg.get("region_id"), "file": doc.get("file"), "tf": tf}
    return out


def source_dxf(out_dir: Path, file_rel: Optional[str]) -> Optional[Path]:
    """The converted DXF of a CAD document in the pipeline output (``converted/<stem>.dxf``), else the DXF itself."""
    if not file_rel:
        return None
    stem = Path(file_rel).stem
    cand = Path(out_dir) / "converted" / f"{stem}.dxf"
    if cand.is_file():
        return cand
    return None


def read_level_page(out_dir: Path, sheets: dict, page: dict):
    """The generic page of a level's region (the strokes and texts, source units), or None."""
    from wenart.ingest import dxf_generic

    regions = {r["id"]: r for r in sheets.get("regions") or []}
    reg = regions.get(page.get("region"))
    dxf = source_dxf(out_dir, page.get("file"))
    if reg is None or dxf is None:
        return None
    return dxf_generic.read_page(str(dxf), page["file"], region_box=tuple(reg["box"]),
                                 units_to_m_override=reg.get("metres_per_unit"))


# ---------------------------------------------------------------------------------------------------- anchors (RC2)
def page_axes(page, tf) -> dict:
    """``{label: ("v", x) | ("h", y)}`` in building metres: the labelled bubbles of the axis grid (two of a label
    along one line)."""
    from wenart.ingest.generic import axes as AX

    bub = AX.bubbles(page.strokes, page.texts)
    if not bub:
        return {}
    pts: dict = {}
    for t in page.texts:
        label = " ".join(str(t.text or "").upper().split())
        if not AX.GRID_LABEL_RE.match(label):
            continue
        c = ((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0)
        for cx, cy, r in bub:
            if math.dist(c, (cx, cy)) <= 0.6 * r:
                pts.setdefault(label, []).append(_apply(tf, (cx, cy)))
                break
    out = {}
    for label, ps in pts.items():
        if len(ps) < 2:
            continue
        xs, ys = [p[0] for p in ps], [p[1] for p in ps]
        if max(xs) - min(xs) <= 0.10 and max(ys) - min(ys) >= 3.0:
            out[label] = ("v", sum(xs) / len(xs))
        elif max(ys) - min(ys) <= 0.10 and max(xs) - min(xs) >= 3.0:
            out[label] = ("h", sum(ys) / len(ys))
    return out


def page_stairs(page, tf) -> list:
    """``[((x, y), radii)]`` in building metres: sets of concentric arcs (a spiral stair's eye, a newel) with at
    least three radii."""
    s = math.hypot(tf[0], tf[3])
    groups: dict = {}
    for st in page.strokes:
        arc = getattr(st, "arc", None)
        if not arc:
            continue
        r = float(arc["radius"]) * s
        if not (0.05 <= r <= 1.5):
            continue
        c = _apply(tf, arc["center"])
        key = (round(c[0], 2), round(c[1], 2))
        g = groups.setdefault(key, {"radii": set(), "pts": []})
        g["radii"].add(round(r, 2))
        g["pts"].append(c)
    return [((sum(p[0] for p in g["pts"]) / len(g["pts"]), sum(p[1] for p in g["pts"]) / len(g["pts"])), g["radii"])
            for g in groups.values() if len(g["radii"]) >= 3]


def stacking(anchors: dict, reference: str) -> list:
    """RC2 findings: each level's axes and stairs against the reference level's (``anchors``: ``{level: {"axes",
    "stairs"}}``)."""
    out = []
    ref = anchors.get(reference) or {}
    for lid, a in anchors.items():
        if lid == reference:
            continue
        gaps = []
        for label, (o, c) in (a.get("axes") or {}).items():
            ro = (ref.get("axes") or {}).get(label)
            if ro and ro[0] == o:
                gaps.append((abs(c - ro[1]), f"axis {label}"))
        # each arc set against the nearest set of the same radii on the reference (fixtures repeat their arcs)
        for c0, r0 in a.get("stairs") or []:
            near = [math.dist(c0, c1) for c1, r1 in ref.get("stairs") or [] if len(r0 & r1) >= 3]
            if near:
                gaps.append((min(near), "the arc sets (stair, fixtures)"))
        if not gaps:
            continue
        ds = sorted(g[0] for g in gaps)
        typical = ds[len(ds) // 2]                       # the median: one moved fixture does not move the level
        if typical > STACK_TOL_M:
            sev = "critical" if typical > STACK_CRITICAL_M else "major"
            axis_off = [g for g in gaps if g[1].startswith("axis") and g[0] > STACK_TOL_M]
            out.append(_finding("RC2", sev, lid, f"{lid} does not stack on {reference}: its anchors are {typical:.2f} m "
                                f"off (median of {len(gaps)}: {len(axis_off)} axes, "
                                f"{sum(1 for g in gaps if not g[1].startswith('axis'))} arc sets)",
                                offset_m=round(typical, 3)))
    return out


# ------------------------------------------------------------------------------------------------- areas (RC3)
def area_findings(page, tf, rooms: list, level: str) -> list:
    from shapely.geometry import Point, Polygon

    out = []
    polys = [(r, Polygon(r["polygon"])) for r in rooms if r.get("polygon") and len(r["polygon"]) >= 3]
    for t in page.texts:
        m = AREA_RE.search(str(t.text or ""))
        if not m:
            continue
        drawn = float(m.group(1).replace(",", "."))
        p = _apply(tf, ((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0))
        room = next((r for r, poly in polys if poly.contains(Point(p))), None)
        if room is None:
            continue
        model = float(room.get("area_computed") or Polygon(room["polygon"]).area)
        if abs(model - drawn) > max(AREA_TOL_SHARE * drawn, AREA_TOL_M2):
            out.append(_finding("RC3", "major", level, f"{room.get('label') or room['id']} ({room['id']}): the drawing "
                                f"says {drawn:.2f} m2, the model has {model:.1f} m2", room_id=room["id"],
                                drawn_m2=drawn, model_m2=round(model, 2), at=[round(p[0], 2), round(p[1], 2)]))
    return out


# ------------------------------------------------------------------------------------------------- walls (RC4, RC5)
def drawn_wall_segments(page, tf) -> list:
    """The straight strokes (building metres) of the layers whose name means wall, plaster or column, the axis lines
    left out."""
    from wenart.ingest.generic import axes as AX
    from wenart.ingest.generic import layer_names as LN

    axis = AX.axis_line_ids(page.strokes, page.texts)
    out = []
    for st in page.strokes:
        if st.id in axis or getattr(st, "arc", None) or not LN.draws_walls(getattr(st, "layer", None)):
            continue
        pts = [_apply(tf, p) for p in st.pts] + ([_apply(tf, st.pts[0])] if st.closed else [])
        for a, b in zip(pts, pts[1:]):
            if math.dist(a, b) >= SEGMENT_MIN_M:
                out.append((a, b))
    return out


PAIR_GAP_M = (0.05, 0.60)     # a wall face has a parallel partner this far away (the other face)
PAIR_OVERLAP_M = 0.3


def paired(segs: list) -> list:
    """The segments with a parallel partner ``PAIR_GAP_M`` away, overlapping it by ``PAIR_OVERLAP_M``: wall faces; a
    lone line (a spiral stair's tread, a hatch edge, a leader) is no wall face (pure)."""
    from shapely.geometry import LineString
    from shapely.strtree import STRtree

    if not segs:
        return []
    lines = [LineString(s) for s in segs]
    tree = STRtree(lines)
    keep = []
    for i, (a, b) in enumerate(segs):
        L = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        for j in tree.query(lines[i].buffer(PAIR_GAP_M[1])):
            if j == i:
                continue
            c, d = segs[j]
            L2 = math.dist(c, d)
            vx, vy = (d[0] - c[0]) / L2, (d[1] - c[1]) / L2
            if abs(ux * vy - uy * vx) > 0.02:             # not parallel (about 1 degree)
                continue
            gap = abs((c[0] - a[0]) * uy - (c[1] - a[1]) * ux)
            if not (PAIR_GAP_M[0] <= gap <= PAIR_GAP_M[1]):
                continue
            s0, s1 = sorted(((c[0] - a[0]) * ux + (c[1] - a[1]) * uy, (d[0] - a[0]) * ux + (d[1] - a[1]) * uy))
            if min(L, s1) - max(0.0, s0) >= PAIR_OVERLAP_M:
                keep.append((a, b))
                break
    return keep


def wall_findings(segs: list, walls: list, level: str, built: list = ()) -> list:
    """RC4 on the paired drawn faces (``paired``), RC5 on every drawn wall line (one face is enough)."""
    from shapely.geometry import LineString, Point
    from shapely.ops import unary_union

    if not segs:
        return []
    every = unary_union([LineString([a, b]) for a, b in segs])
    segs = paired(segs)
    if not segs:
        segs = []
    out = []
    model = [w for w in walls if w.get("start") and w.get("end")]
    bands = unary_union([LineString([tuple(w["start"]), tuple(w["end"])]).buffer(
        float(w.get("thickness") or 0.2) / 2.0 + WALL_NEAR_M, cap_style=2) for w in model] + list(built)) \
        if model or built else None
    drawn = unary_union([LineString([a, b]) for a, b in segs]) if segs else LineString()
    missing = drawn.difference(bands) if bands is not None else drawn
    pieces = [g for g in getattr(missing, "geoms", [missing]) if g.length >= MISSING_PIECE_M]   # no jamb scraps
    total = sum(g.length for g in pieces)
    if total > MISSING_MAJOR_M:
        big = sorted(pieces, key=lambda g: -g.length)
        out.append(_finding("RC4", "major", level, f"{total:.1f} m of drawn wall face the model does not build "
                            f"({len(big)} piece(s) of {MISSING_PIECE_M:g} m or more)", missing_m=round(total, 1),
                            pieces=[[[round(c, 2) for c in g.coords[0]], [round(c, 2) for c in g.coords[-1]]]
                                    for g in big[:20]]))
    for w in model:
        line = LineString([tuple(w["start"]), tuple(w["end"])])
        if line.length < 0.5:
            continue
        band = every.intersection(line.buffer(float(w.get("thickness") or 0.2) / 2.0 + WALL_NEAR_M, cap_style=2))
        covered = 0.0
        for g in getattr(band, "geoms", [band]):
            if g.length > 0:
                proj = [line.project(Point(c)) for c in g.coords]
                covered += max(proj) - min(proj)
        share = min(1.0, covered / line.length)
        if share < DRAWN_SHARE_MIN:
            inferred = bool(w.get("inferred"))
            out.append(_finding("RC5", "minor" if inferred else "major", level,
                                f"wall {w.get('id')} ({line.length:.2f} m) lies on drawn wall lines for "
                                f"{share:.0%} of its length" + (" (an inferred wall)" if inferred else ""),
                                wall_id=w.get("id"), share=round(share, 2), inferred=inferred))
    return out


def built_elsewhere(building: dict, level: str) -> list:
    """Shapes (building metres) where drawn wall faces are built as something else than a wall of the building: the
    site's boundary walls of the level (a balcony's parapet), its outdoor spaces (balconies, terraces), its stairs."""
    from shapely.geometry import LineString, Polygon

    out = []
    site = building.get("site") or {}
    for w in site.get("boundary_walls") or []:
        if w.get("level_id") == level and w.get("start") and w.get("end"):
            out.append(LineString([tuple(w["start"]), tuple(w["end"])]).buffer(
                float(w.get("thickness") or 0.2) / 2.0 + WALL_NEAR_M, cap_style=2))
    for sp in site.get("outdoor_spaces") or []:
        if sp.get("level_id") == level and sp.get("polygon") and len(sp["polygon"]) >= 3:
            out.append(Polygon(sp["polygon"]).buffer(WALL_NEAR_M + 0.3, join_style=2))
    for f in building.get("furniture") or []:
        fp = f.get("footprint") or {}
        if f.get("level_id") == level and f.get("type") == "stair" and fp.get("center"):
            cx, cy = fp["center"][:2]
            w, d = fp["size"][:2]
            r = math.radians(float(fp.get("rotation_deg") or 0.0))
            pts = [(cx + sx * w / 2 * math.cos(r) - sy * d / 2 * math.sin(r),
                    cy + sx * w / 2 * math.sin(r) + sy * d / 2 * math.cos(r)) for sx, sy in ((-1, -1), (1, -1), (1, 1),
                                                                                            (-1, 1))]
            out.append(Polygon(pts).buffer(0.1))
    return out


# ------------------------------------------------------------------------------------------------------- the check
def check(out_dir, reference: Optional[str] = None) -> dict:
    """The findings of a pipeline output (the module docstring)."""
    out_dir = Path(out_dir)
    building = json.loads((out_dir / "building.json").read_text(encoding="utf-8"))
    sheets_path = out_dir / "sheets.json"
    sheets = json.loads(sheets_path.read_text(encoding="utf-8")) if sheets_path.is_file() else {}
    findings = []
    for lo in building.get("levels_left_out") or []:
        findings.append(_finding("RC1", "critical", f"order {lo.get('order')}", f"level {lo.get('label')} left out "
                                 f"of the model: {lo.get('reason')}", region=lo.get("region_id")))
    for w in building.get("warnings") or []:
        if "lies outside the building" in w or "outer walls do not close" in w:
            findings.append(_finding("RC6", "major", None, w[:300]))
    pages = level_pages(building)
    anchors, checked, notes = {}, [], []
    conv = {"layers": {}, "levels": {}}
    for lid, pg in pages.items():
        page = read_level_page(out_dir, sheets, pg)
        if page is None:
            notes.append(f"{lid}: no CAD source to check against (a PDF or a raster page)")
            continue
        tf = pg["tf"]
        checked.append(lid)
        anchors[lid] = {"axes": page_axes(page, tf), "stairs": page_stairs(page, tf)}
        _note_conventions(conv, lid, page, anchors[lid], sheets, pg, building)
        rooms = [r for r in building.get("rooms") or [] if r.get("level_id") == lid]
        walls = [w for w in building.get("walls") or [] if w.get("level_id") == lid]
        findings += area_findings(page, tf, rooms, lid)
        segs = drawn_wall_segments(page, tf)
        if segs:
            findings += wall_findings(segs, walls, lid, built_elsewhere(building, lid))
        else:
            notes.append(f"{lid}: no layer named wall, plaster or column: walls not compared")
    ref = reference or next((lid for lid in ("L0", "L1") if lid in anchors), next(iter(anchors), None))
    if ref:
        findings += stacking(anchors, ref)
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in ("critical", "major", "minor")}
    return {"project": (building.get("project") or {}).get("id"), "levels_checked": checked, "reference": ref,
            "conventions": conv,
            "findings": findings, "counts": counts, "notes": notes,
            "verdict": "ready" if not counts["critical"] else "fix before a pod run",
            "levels": [lv["id"] for lv in building.get("levels") or []],
            "levels_left_out": [lo.get("label") for lo in building.get("levels_left_out") or []]}


def _note_conventions(conv: dict, lid: str, page, anchors: dict, sheets: dict, pg: dict, building: dict) -> None:
    """What the reading understood about a level's drawing (2 Nov 2026, the conventions record): every layer with its
    meaning by name (``generic.layer_names``), its linetypes and strokes, the axis lines; the grid's axes, the core's
    arc sets, how the level was placed (``sheets.json`` registration) and whether it lies fully below ground."""
    from wenart.ingest.generic import axes as AX
    from wenart.ingest.generic import layer_names as LN

    axis = AX.axis_line_ids(page.strokes, page.texts)
    for st in page.strokes:
        name = getattr(st, "layer", None) or "0"
        row = conv["layers"].setdefault(name, {"role": LN.layer_role(name), "strokes": 0, "linetypes": [],
                                               "axis_lines": 0, "levels": []})
        row["strokes"] += 1
        lt = getattr(st, "linetype", None)
        if lt and lt not in row["linetypes"]:
            row["linetypes"].append(lt)
        if st.id in axis:
            row["axis_lines"] += 1
        if lid not in row["levels"]:
            row["levels"].append(lid)
    reg = next((r for r in sheets.get("regions") or [] if r.get("id") == pg.get("region")), {}) or {}
    under = any("fully below ground" in w and f"({lid})" in w for w in building.get("warnings") or [])
    conv["levels"][lid] = {"region": pg.get("region"), "axes": len(anchors.get("axes") or {}),
                           "arc_sets": len(anchors.get("stairs") or []), "axis_lines": len(axis),
                           "placed_by": (reg.get("registration") or {}).get("method"),
                           "placement_note": (reg.get("registration") or {}).get("note"), "underground": under}


def write(out_dir, result: dict) -> Path:
    """``reading_check/reading_check.json`` and ``.md`` in the pipeline output."""
    d = Path(out_dir) / "reading_check"
    d.mkdir(parents=True, exist_ok=True)
    (d / "reading_check.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    lines = [f"# Reading check: {result.get('project')}", "",
             f"Verdict: **{result['verdict']}** ({result['counts']['critical']} critical, {result['counts']['major']} "
             f"major, {result['counts']['minor']} minor). Levels checked against the drawing: "
             f"{', '.join(result['levels_checked']) or 'none'}; reference {result.get('reference')}.", "",
             "| check | severity | level | finding |", "|---|---|---|---|"]
    order = {"critical": 0, "major": 1, "minor": 2}
    for f in sorted(result["findings"], key=lambda f: (order[f["severity"]], f["check"], str(f.get("level_id")))):
        lines.append(f"| {f['check']} {f['name']} | {f['severity']} | {f.get('level_id') or '-'} | "
                     f"{f['message'].replace('|', '/')} |")
    if result.get("notes"):
        lines += ["", "Notes:"] + [f"- {n}" for n in result["notes"]]
    conv = result.get("conventions") or {}
    if conv.get("levels"):
        lines += ["", "## What the reading understood about the drawing", "",
                  "| level | placed by | axes | arc sets | axis lines left out | fully below ground |",
                  "|---|---|---|---|---|---|"]
        for lid, c in conv["levels"].items():
            lines.append(f"| {lid} | {c.get('placed_by') or '-'} | {c['axes']} | {c['arc_sets']} | {c['axis_lines']} | "
                         f"{'yes' if c['underground'] else 'no'} |")
        lines += ["", "| layer | meaning (by its name) | linetypes | strokes | axis lines |", "|---|---|---|---|---|"]
        for name, c in sorted(conv["layers"].items(), key=lambda kv: -kv[1]["strokes"])[:40]:
            lines.append(f"| {name} | {c['role'] or '-'} | {', '.join(c['linetypes']) or '-'} | {c['strokes']} | "
                         f"{c['axis_lines']} |")
        (d / "conventions.json").write_text(json.dumps(conv, ensure_ascii=False, indent=1), encoding="utf-8")
    (d / "reading_check.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return d
