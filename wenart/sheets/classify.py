"""Region classes (docs/milestone10.md §3.1 item 2): the title first, then geometry; AI only proposes.

What: ``by_title(region)`` (the region's own title through ``titles``), ``features(region, mpu)`` (what the
geometry shows) and ``by_geometry(region, features, frames)``; ``use_of(region)`` says what the pipeline does with
a region (``read`` a plan, ``heights`` from a section, ``exterior`` evidence, ``ignored``).

Why: trust order: the title text decides; geometry decides untitled regions; AI never makes a plan.

How (geometry rules, first that holds):
- ``title_block``: a lone rectangle with texts (a title box: real02's ``PLANLAR``), or a region at the frame edge
  with >= 4 short texts and no room names;
- ``section``: >= 2 slab bands across the building width and a roof line or a level mark (``heights.read_section``);
- ``elevation``: no slab bands, a ground line and >= 3 window-like rectangles in rows;
- ``site_plan``: a north arrow or street words with a closed outline inside a larger one;
- ``floor_plan``: >= 2 room names and a wall structure (M7's cheap wall test, or >= 4 wall face pairs
  0.05-0.6 m apart);
- otherwise no class (``other``, ``class_method none``, unverified).
"""
from __future__ import annotations

import dataclasses
import re
from typing import Optional

from wenart import building as B
from wenart.ingest.generic import labels as GL
from wenart.ingest.generic.model import TextRun
from wenart.sheets import heights as H
from wenart.sheets import titles as T
from wenart.sheets import units_check as UC
from wenart.sheets.model import Region

PLAN_CLASSES = ("floor_plan", "alternative_floor_plan", "furniture_plan")
TITLE_CONFIDENCE = 0.99
LEVEL_ONLY_CONFIDENCE = 0.7
GEOMETRY_CONFIDENCE = {"title_block": 0.9, "section": 0.85, "elevation": 0.7, "site_plan": 0.7, "floor_plan": 0.7,
                       "roof_plan": 0.6}
STREET_WORDS = re.compile(r"\b(SOKAK|SOK|CADDE|CAD|BULVAR|YOL|PARSEL|ADA|STREET|ROAD|AVENUE|STRASSE|RUE|AVENUE)\b")
WINDOW_M = ((0.4, 3.0), (0.4, 2.6))
EDGE_GAPS = 2.0
IGNORED_REASON = {"title_block": "title block", "legend": "legend", "detail": "detail drawing", "3d_view": "3D view",
                  "other": "no class"}


def text_runs(region: Region) -> list[TextRun]:
    return [TextRun(id=t.id, text=t.text, box=t.box, height=t.height, rotation_deg=t.rotation_deg,
                    evidence=[dict(t.evidence)] if t.evidence else []) for t in region.texts]


def by_title(region: Region) -> bool:
    """Class from the region's own title (``title`` keywords); True when a title decided."""
    t = T.pick_title(region.texts, region.geometry_box)
    if t is None:
        return False
    hit = T.class_of(t.text)
    level = T.level_of(t.text)
    language = hit[2] if hit else (level.language if level else None)
    words = hit[1] if hit else ([level.word] if level else [])
    alt = T.alternative_of(t.text)
    if alt and alt[1] == "bracket":
        words = words + [f"({alt[0]})"]
    region.title = {"text": t.text, "entity": t.id, "box": [round(v, 3) for v in t.box], "language": language,
                    "keywords": words}
    region.title_txt = t
    ev = dict(t.evidence)
    ev.update({"method": "vector" if ev.get("method", "vector") == "vector" else ev["method"], "confidence": 1.0,
               "rule": "title_keyword", "text": t.text})
    region.evidence.append(ev)
    if hit:
        region.cls, region.class_confidence = hit[0], TITLE_CONFIDENCE
    else:
        region.cls, region.class_confidence = "floor_plan", LEVEL_ONLY_CONFIDENCE     # a level word alone
    region.class_method, region.status = "title", "verified"
    return True


def _wall_test(region: Region) -> Optional[str]:
    from wenart.ingest.classify import wall_structure

    page = region.sheet.generic_page
    if page is None:
        return None
    b = region.geometry_box
    sub = dataclasses.replace(page, strokes=region.strokes(), texts=[], dimensions=[],
                              size=(b[2] - b[0], b[3] - b[1]))
    try:
        return wall_structure(sub)
    except Exception:  # noqa: BLE001 - a failed cheap test is no wall evidence
        return None


def features(region: Region, mpu: Optional[float]) -> dict:
    """Geometry evidence of a region (``features`` of ``sheets.json``)."""
    f: dict = {"entities": len(region.ents), "texts": len(region.texts)}
    if region.kind == "box":
        f["title_box"] = True
        if region.texts and region.title is None:
            t = max(region.texts, key=lambda t: (t.height, -t.point[1]))
            region.title = {"text": t.text, "entity": t.id, "box": [round(v, 3) for v in t.box],
                            "language": T.language_of(t.text), "keywords": []}
            region.title_txt = t
        return f
    if region.kind == "text":
        f["texts_only"] = True
        return f
    runs = text_runs(region)
    f["room_labels"] = len(GL.room_name_runs(runs))
    if f["room_labels"] >= 2:
        f["wall_test"] = _wall_test(region)
    f["area_labels"] = len(UC.area_label_texts(region.texts))
    sec = H.read_section(region, mpu)
    if region.cls not in PLAN_CLASSES or region.class_method != "title":
        f.update(sec.features())                         # section evidence (not reported for titled plans)
    region._section = sec                                # reused by the heights
    b = region.geometry_box
    diag = ((b[2] - b[0]) ** 2 + (b[3] - b[1]) ** 2) ** 0.5
    pairs = UC.face_pair_distances(region.strokes(), diag)
    if mpu:
        f["wall_pairs"] = sum(1 for d in pairs if 0.05 <= d * mpu <= 0.6)
    f["closed_rectangles"] = sum(1 for e in region.ents if e.rect is not None)
    if region.cls not in PLAN_CLASSES or region.class_method != "title":
        f["window_rows"] = _window_rows(region, mpu)
    big = largest_polyline(region, mpu)
    if big is not None:
        f["largest_polyline"] = big
    words = " ".join(T.fold(t.text) for t in region.texts)
    f["street_words"] = bool(STREET_WORDS.search(words))
    f["north_arrow"] = any(T.fold(t.text) in ("N", "K", "KUZEY", "NORTH", "NORD") for t in region.texts)
    f["stairs"] = len(stairs_of(region))
    f["columns"] = len(columns_of(region, mpu))
    return f


def _window_rows(region: Region, mpu: Optional[float]) -> int:
    """Rows of >= 3 window-sized closed rectangles at the same height (elevations)."""
    if not mpu:
        return 0
    rects = []
    for e in region.ents:
        for st in e.strokes:
            box = st.bbox()
            w, h = (box[2] - box[0]) * mpu, (box[3] - box[1]) * mpu
            if st.closed and len(st.pts) == 4 and WINDOW_M[0][0] <= w <= WINDOW_M[0][1] \
                    and WINDOW_M[1][0] <= h <= WINDOW_M[1][1]:
                rects.append(box)
    rows: dict[tuple, int] = {}
    for b in rects:
        rows[(round(b[1] * mpu, 1), round(b[3] * mpu, 1))] = rows.get((round(b[1] * mpu, 1), round(b[3] * mpu, 1)),
                                                                       0) + 1
    return sum(1 for n in rows.values() if n >= 3)


def largest_polyline(region: Region, mpu: Optional[float]) -> Optional[dict]:
    """The polyline with the largest box (>= 4 vertices; the drawn outline of a dwelling on real02), as
    ``{entity, layer, size_m, closed, ends_m}``; reported, never used to change anything."""
    best = None
    for e in region.ents:
        if len(e.strokes) != 1 or e.kind not in ("LWPOLYLINE", "POLYLINE", "path") or len(e.strokes[0].pts) < 4:
            continue
        b = e.box
        area = (b[2] - b[0]) * (b[3] - b[1])
        if (b[2] - b[0]) >= 0.98 * (region.geometry_box[2] - region.geometry_box[0]) and e.rect is not None:
            continue                                     # the region's own border (roof outline)
        if best is None or area > best[0]:
            best = (area, e)
    if best is None:
        return None
    e = best[1]
    st = e.strokes[0]
    s = mpu or 1.0
    return {"entity": e.id, "layer": e.layer, "size_m" if mpu else "size_units":
            [round((e.box[2] - e.box[0]) * s, 3), round((e.box[3] - e.box[1]) * s, 3)], "closed": bool(st.closed),
            "ends_m" if mpu else "ends_units": round(((st.pts[0][0] - st.pts[-1][0]) ** 2 +
                                                      (st.pts[0][1] - st.pts[-1][1]) ** 2) ** 0.5 * s, 3)}


STAIR_RE = re.compile(r"MERDIVEN|STAIR|TREPPE|ESCALIER|BASAMAK")


def stairs_of(region: Region) -> list:
    """Boxes of the stairs drawn as blocks or on stair layers (``merdiven``, ``stair``, ``treppe``, ``escalier``)."""
    out = []
    for e in region.ents:
        name = T.fold(" ".join(x for x in (e.block or "", e.layer or "") if x))
        if STAIR_RE.search(name):
            out.append(e.box)
    return out


def columns_of(region: Region, mpu: Optional[float]) -> list[tuple[float, float]]:
    """Centres of the columns: closed squares 0.15-0.8 m (sides within 10 % of each other)."""
    if not mpu:
        return []
    out = []
    for e in region.ents:
        if e.rect is None:
            continue
        w, h = (e.rect[2] - e.rect[0]) * mpu, (e.rect[3] - e.rect[1]) * mpu
        if 0.15 <= w <= 0.8 and 0.15 <= h <= 0.8 and abs(w - h) <= 0.1 * max(w, h):
            out.append(e.centre)
    return out


def by_geometry(region: Region, f: dict, frames: list, gap: float) -> bool:
    """Class from geometry for an untitled region; True when a rule decided."""
    rule = None
    cls = None
    if f.get("title_box"):
        cls, rule = "title_block", "lone_rectangle_with_texts" if region.texts else "lone_rectangle"
    elif _at_frame_edge(region, frames, gap) and len(region.texts) >= 4 and not f.get("room_labels") \
            and all(len(t.text.split()) <= 4 for t in region.texts):
        cls, rule = "title_block", "frame_edge_short_texts"
    elif f.get("slab_bands", 0) >= 2 and (f.get("roof_lines", 0) >= 1 or f.get("level_marks", 0) >= 1):
        cls, rule = "section", "slab_bands"
    elif not f.get("slab_bands") and f.get("ground_lines") and f.get("window_rows", 0) >= 1:
        cls, rule = "elevation", "window_rows"
    elif (f.get("north_arrow") or f.get("street_words")) and f.get("closed_rectangles", 0) >= 2 \
            and not f.get("room_labels"):
        cls, rule = "site_plan", "north_arrow_or_street_words"
    elif f.get("room_labels", 0) >= 2 and (f.get("wall_test") or f.get("wall_pairs", 0) >= 4):
        cls, rule = "floor_plan", "room_labels_and_walls"
    if cls is None:
        return False
    region.cls, region.class_method, region.status = cls, "geometry", "verified"
    region.class_confidence = GEOMETRY_CONFIDENCE.get(cls, 0.6)
    region.evidence.append({"file": region.file, "page": region.sheet.page, "layer": None,
                            "entity": region.ents[0].id if region.ents else None, "method": "vector",
                            "confidence": region.class_confidence, "rule": rule,
                            "text": ", ".join(f"{k} {v}" for k, v in f.items() if v and k not in
                                              ("entities", "texts"))})
    return True


def _at_frame_edge(region: Region, frames: list, gap: float) -> bool:
    b = region.geometry_box
    for fr in frames:
        fb = fr["box"]
        if any(abs(v) <= EDGE_GAPS * gap for v in (b[0] - fb[0], fb[2] - b[2], b[1] - fb[1], fb[3] - b[3])):
            return True
    return False


def use_of(region: Region) -> None:
    """``use`` and ``ignored_reason`` from the class and how it was decided."""
    if region.class_method == "ai":
        region.use = "ignored"
        region.ignored_reason = "AI-only class: unverified, never read as a drawing (AI proposes, title and geometry " \
                                "decide)"
        return
    if region.class_method == "none":
        region.use = "ignored"
        region.ignored_reason = "no title and no geometry rule gives a class"
        return
    if region.cls in PLAN_CLASSES:
        region.use, region.ignored_reason = "read", None
    elif region.cls == "section":
        region.use, region.ignored_reason = "heights", None
    elif region.cls in ("elevation", "roof_plan", "site_plan"):
        region.use, region.ignored_reason = "exterior", None
    else:
        region.use, region.ignored_reason = "ignored", IGNORED_REASON.get(region.cls, region.cls.replace("_", " "))


def room_subtype(label: str) -> Optional[str]:
    """``child`` for a child's room (Çocuk, child, kid, nursery, bebek); None otherwise."""
    folded = B.fold_ascii(label).lower()
    if re.search(r"\b(cocuk|child|children|kid|kids|nursery|bebek|baby)\b", folded):
        return "child"
    return None
