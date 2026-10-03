"""The generic plan core: one ``GenericPage`` -> ``LevelExtraction`` (docs/milestone7.md §1.2, §1.5, §2).

What: ``extract(page, level_id, file_rel, answers=None, no_ai=False, rec_dir=None)`` wires the text side
(``labels``, ``scale``: G1) and the geometry side (``walls``, ``openings``, ``topology``, ``symbols``: G2) of the
generic core in the order of §1.2:

1. texts -> the page's unit system (``labels.page_unit_system``);
2. dimensions (``scale.find_dimensions``) -> provisional scale (``scale.provisional_scale``); without one the page
   returns early with ``scale = None`` (the pipeline stops with ``needs_review`` as before);
3. wall primitives and mask -> wall rectangles (``walls``) -> gaps and openings on all walls (``openings``);
4. label blocks (``labels.merge_label_blocks``) -> plot and building (``topology.split_plot``; plot walls, exterior
   areas and their openings go to ``site``) -> the outer loop must close (else ``needs_review``);
5. furniture clusters, rule types and AI candidates (``symbols.furniture``) -> virtual separators (they need the
   stairs) -> faces with their names and types -> the room checks of the furniture rules;
6. the scale is confirmed with the room-size labels (``scale.confirm_scale``); a provisional scale that the labels
   do not corroborate drops the page's scale (``needs_review``, "scale not corroborated: ...");
7. AI candidates get their two crops and questions (``recognition.crops``, ``recognition.symbols.question``); the
   answers, when given, are applied by the two-pass rule (``recognition.symbols.decide``);
8. everything is shifted to the building frame: ``transform_to_building = [s, 0, -ox, 0, s, -oy]`` with ``s`` the
   page scale and ``(ox, oy)`` the min corner of the building walls in page metres.

All core functions work in page metres (``to_metres``: page units x ``s``, y up, no offset). Boxes stay in page
units for the debug image. What the pipeline needs beyond the ``LevelExtraction`` fields of the old extractors is in
``ex.report`` (dimensions with ratios, size-label checks, gaps, separators, wall info, the wall mask, the
recognition questions and the keys still waiting for answers) and ``ex.review`` (``needs_review`` reasons).

Room names travel as ``TextItem``s whose ``block`` is the ``labels.LabelBlock`` (anchor = centre of the name lines,
in page units like every text): ``rooms.derive_rooms`` names, types and size-checks the faces from them. Exterior
blocks (Parking, Garden) are passed too, so a face named only by them is never a room.

Answers (§1.4): ``answers`` is None, a recognition folder (``<out>/recognition``: answers are loaded for this page's
questions, key and ``input_sha256`` must match) or the dict ``recognition.answers.load`` returns. ``rec_dir`` is
where the crops are written (``<rec_dir>/crops``); without it the input hashes are computed from the canonical crop
description alone (no files). ``no_ai`` only changes the report: unanswered candidates stay ``unknown`` /
``unverified`` either way, and nothing is pending.
"""
from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Optional

from shapely.geometry import Point

from wenart import building as B
from wenart import units as U
from wenart.ingest.generic import labels as LB
from wenart.ingest.generic import openings as O
from wenart.ingest.generic import scale as SC
from wenart.ingest.generic import symbols as SY
from wenart.ingest.generic import topology as TP
from wenart.ingest.generic import walls as W
from wenart.ingest.generic.model import GenericPage, Stroke, TextRun
from wenart.ingest.model import DimensionItem, FurnitureItem, LevelExtraction, OpeningItem, TextItem, WallItem
from wenart.ingest.model import page_class_for, parse_scale_text

ROUND = 4                          # building-frame coordinates: 0.1 mm
UNLABELLED_TURKISH = "Oda"         # §1.3: placeholder label of an unlabelled face on a Turkish page ...
UNLABELLED_ENGLISH = "Room"        # ... and on an English one


# --------------------------------------------------------------------------
# Page metres
# --------------------------------------------------------------------------

def _scale_stroke(st: Stroke, s: float) -> Stroke:
    arc = None
    if st.arc:
        arc = dict(st.arc, center=(st.arc["center"][0] * s, st.arc["center"][1] * s), radius=st.arc["radius"] * s)
    return Stroke(id=st.id, kind=st.kind, pts=[(x * s, y * s) for x, y in st.pts], closed=st.closed, colour=st.colour,
                  fill=st.fill, width=st.width * s, layer=st.layer, block=st.block, arc=arc, source=st.source)


def to_metres(page: GenericPage, units_to_m: float) -> tuple[list[Stroke], list[TextRun]]:
    """The page's strokes and texts in page metres (page units x ``units_to_m``, y up, no offset); ids, colours,
    layers, block chains and evidence are kept."""
    s = float(units_to_m)
    strokes = [_scale_stroke(st, s) for st in page.strokes]
    texts = [TextRun(id=t.id, text=t.text, box=tuple(v * s for v in t.box), height=t.height * s,
                     rotation_deg=t.rotation_deg, source=t.source, evidence=[dict(e) for e in t.evidence])
             for t in page.texts]
    return strokes, texts


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def _evidence_page(page: GenericPage) -> Optional[int]:
    """Evidence ``page``: 1-based for PDFs and rasters, null for DXF (one model space)."""
    return None if page.source_kind == "dxf" else page.page


def _text_evidence(page: GenericPage, run: TextRun) -> dict:
    if run.evidence:
        return dict(run.evidence[0])
    method = "ocr" if run.source == "ocr" else ("ai" if run.source == "ai" else "vector")
    return B.evidence(page.file, method, 1.0 if method == "vector" else 0.5, page=_evidence_page(page),
                      entity=run.id, text=run.text)


def _role(text: str, dim_ids: set, label_ids: set, run_id: str) -> str:
    if run_id in dim_ids:
        return "dimension"
    if run_id in label_ids:
        return "room_label"
    if SC.note_ratio(text) or parse_scale_text(text):
        return "scale"
    if page_class_for(text) is not None or B.normalise_level_label(text) is not None:
        return "title"
    return "other"


def _expand_ids(entity: Optional[str]) -> set[str]:
    """``symbols.id_ranges`` back to ids: ``path:3-5,curve:9`` -> {path:3, path:4, path:5, curve:9}."""
    out: set[str] = set()
    for part in (entity or "").split(","):
        head, _, tail = part.partition(":")
        match = re.fullmatch(r"(\d+)-(\d+)", tail)
        if match:
            out.update(f"{head}:{n}" for n in range(int(match.group(1)), int(match.group(2)) + 1))
        elif part:
            out.add(part)
    return out


def _face_aspect(poly) -> tuple[float, float]:
    """(area, aspect = long / short side of the minimum rectangle) of a face polygon."""
    a, b, _ = LB.clear_size(poly)
    short = min(a, b)
    return poly.area, (max(a, b) / short if short > 0 else math.inf)


def _snap(p) -> tuple[float, float]:
    return (round(float(p[0]), ROUND) + 0.0, round(float(p[1]), ROUND) + 0.0)


class _Shift:
    """Page metres -> building metres (translation by the min corner of the building walls)."""

    def __init__(self, ox: float, oy: float):
        self.ox, self.oy = ox, oy

    def p(self, pt) -> tuple[float, float]:
        return _snap((pt[0] - self.ox, pt[1] - self.oy))

    def pts(self, pts) -> list[list[float]]:
        return [list(self.p(q)) for q in pts]


def _shift_wall(w: WallItem, sh: _Shift) -> None:
    w.start, w.end = sh.p(w.start), sh.p(w.end)


def _shift_opening(o: OpeningItem, sh: _Shift) -> None:
    o.center = sh.p(o.center)
    if o.swing_point is not None:
        o.swing_point = sh.p(o.swing_point)
    if o.line:
        o.line = (sh.p(o.line[0]), sh.p(o.line[1]))


def _shift_piece(f: FurnitureItem, sh: _Shift) -> None:
    f.center = sh.p(f.center)
    stair = f.details.get("stair")
    if stair:
        for flight in stair.get("flights") or []:
            for key in ("start", "end"):
                if flight.get(key) is not None:
                    flight[key] = list(sh.p(flight[key]))
        landing = stair.get("landing")
        if landing and landing.get("polygon"):
            landing["polygon"] = sh.pts(landing["polygon"])


def _shift_site(site: dict, sh: _Shift) -> None:
    for w in site.get("boundary_walls", []):
        w["start"], w["end"] = list(sh.p(w["start"])), list(sh.p(w["end"]))
    for a in site.get("areas", []):
        if a.get("polygon"):
            a["polygon"] = sh.pts(a["polygon"])
        if a.get("anchor"):
            a["anchor"] = list(sh.p(a["anchor"]))
    for d in site.get("decor", []):
        d["center"] = list(sh.p(d["center"]))
    for o in site.get("openings", []):
        o["center"] = list(sh.p(o["center"]))


# --------------------------------------------------------------------------
# Faces
# --------------------------------------------------------------------------

def face_table(face_polys: list, blocks: list, walls: list, openings: list, stairs: list) -> list[dict]:
    """One row per face (page metres): ``{"polygon", "names" (indoor blocks), "exterior" (only exterior blocks),
    "room_type", "label", "reason"}``; unlabelled faces are typed by ``topology.unlabelled_face_type``."""
    rows = []
    for poly in face_polys:
        names = [b for b in blocks if not b.exterior and poly.contains(Point(b.anchor))]
        outside = [b for b in blocks if b.exterior and poly.contains(Point(b.anchor))]
        area, aspect = _face_aspect(poly)
        row = {"polygon": poly, "names": names, "exterior": bool(outside) and not names, "reason": None}
        if names:
            row["room_type"] = LB.room_type_for(names[0].name, area, aspect)[0]
            row["label"] = names[0].name
        elif outside:
            row["room_type"], row["label"] = None, outside[0].name
        else:
            row["room_type"], row["reason"] = TP.unlabelled_face_type(poly, walls, openings, stairs)
            row["label"] = None
        rows.append(row)
    return rows


# --------------------------------------------------------------------------
# AI candidates (§3)
# --------------------------------------------------------------------------

def _crop_context(cand: dict, wall_polys: list, others: list[tuple[set, tuple, list]]) -> dict:
    """Walls (page metres) and the other strokes whose box meets the context square of ``cand``."""
    from wenart.recognition import crops as CR

    ctx = [v / 1000.0 for v in CR.crop_squares(cand)["ctx_box"]]
    own = cand["_ids"]
    near = [pts for ids, box, pts in others
            if not (ids & own) and box[2] >= ctx[0] and box[0] <= ctx[2] and box[3] >= ctx[1] and box[1] <= ctx[3]]
    return {"walls": wall_polys, "others": near}


def _front_values(cand: dict) -> list[float]:
    """``symbols.front_candidates`` gives ``[{"front_deg", "rule"}]``; ``recognition.symbols.decide`` reads plain
    angles."""
    out = []
    for c in cand.get("front_candidates") or []:
        v = c.get("front_deg") if isinstance(c, dict) else c
        if v is not None:
            out.append(float(v))
    return out


def _apply_front(item: FurnitureItem, front_deg: float) -> None:
    """Set a known front: an unrotated piece faces -Y, so rotation = front + 90; width stays across the front."""
    rotation = (front_deg + 90.0) % 360.0
    old = item.rotation_deg % 180.0
    if abs(((rotation % 180.0) - old + 90.0) % 180.0 - 90.0) > 1.0:
        item.size = (item.size[1], item.size[0])
    item.rotation_deg = round(rotation, 3)
    item.front_deg = round(front_deg % 360.0, 3)


def _apply_decision(item: FurnitureItem, result: dict) -> None:
    item.type = result["type"]
    item.status = result["status"]
    item.type_method = result["type_method"]
    item.type_candidates = list(result["type_candidates"])
    item.extra_evidence = list(result["ai_evidence"])
    if result.get("front") is not None:
        _apply_front(item, float(result["front"]))
    if result.get("confidence") is not None:
        item.details["type_confidence"] = result["confidence"]
    if result.get("build") is False:
        item.details["build"] = False
    if result.get("note"):
        item.details["note"] = result["note"]
    if result.get("conflict"):
        item.details["ai_conflict"] = dict(result["conflict"])


def _ask_and_apply(ex: LevelExtraction, page: GenericPage, cands: list[dict], wall_polys: list, others: list, answers,
                   no_ai: bool, rec_dir: Optional[Path], level_id: str) -> None:
    """Crops and questions for every candidate; the two-pass rule where answers exist (§3.3)."""
    if not cands:
        ex.report["questions"], ex.report["pending"] = [], []
        return
    if page.source_kind.startswith("raster"):
        # Raster candidates are pixel crops of the rectified page (area S, wave 2): no questions yet.
        ex.warnings.append(f"{page.file} p{page.page}: {len(cands)} raster furniture candidates not asked (raster "
                           f"crops need the rectified page image); they stay unknown, unverified")
        ex.report["questions"], ex.report["pending"] = [], []
        return
    from wenart.recognition import answers as A
    from wenart.recognition import crops as CR
    from wenart.recognition import symbols as RS

    items = []
    for cand in cands:
        crop_cand = {"key": cand["key"], "footprint": cand["footprint"], "strokes": cand["strokes"],
                     "bbox": cand["bbox"], "_ids": cand["_ids"]}
        context = _crop_context(crop_cand, wall_polys, others)
        crop_cand.pop("_ids")
        if rec_dir is not None:
            crops = CR.render_pair(crop_cand, context, Path(rec_dir) / A.CROPS_DIR, cand["key"])
        else:
            desc = CR.vector_description(crop_cand, context)
            names = CR.crop_names(cand["key"])
            crops = {"ctx_png": names[0], "iso_png": names[1], "input_sha256": CR.canonical_sha256(desc),
                     "crop": {k: desc[k] for k in ("object_box", "ctx_box", "iso_box")}}
        question = dict(crop_cand, file=page.file, page=_evidence_page(page), level=level_id,
                        room_type=cand.get("room_type"))
        item = RS.question(question, crops)
        cand["request"] = item
        items.append(item)
    loaded: dict = {}
    if isinstance(answers, (str, Path)):
        loaded = A.load(Path(answers), items)
    elif isinstance(answers, dict):
        loaded = answers
    table = RS.load_size_table()
    pending = []
    decided = 0
    for cand in cands:
        got = loaded.get(cand["key"]) or {}
        if not all(got.get(k) is not None for k in A.MODEL_KEYS):
            pending.append(cand["key"])
        if not any(v is not None for v in got.values()):
            continue
        dc = {"key": cand["key"], "footprint": cand["footprint"], "strokes": cand["strokes"], "bbox": cand["bbox"],
              "file": page.file, "page": _evidence_page(page), "front_candidates": _front_values(cand)}
        result = RS.decide(dc, got, table, cand.get("room_type"))
        _apply_decision(cand["item"], result)
        ex.warnings.extend(result.get("warnings") or [])
        decided += 1
    ex.report["questions"] = items
    ex.report["pending"] = [] if no_ai else pending
    ex.report["answers_applied"] = decided
    if pending:
        ex.notes.append(f"{len(pending)} of {len(cands)} furniture candidates have no complete pair of answers"
                        + (" (--no-ai: they stay unknown, unverified)" if no_ai else ""))


# --------------------------------------------------------------------------
# Report data
# --------------------------------------------------------------------------

def _dimension_rows(dims: list, mpu: Optional[float]) -> list[dict]:
    rows = []
    for d in dims:
        row = {"text": d.text, "text_id": d.text_id, "printed_m": round(d.length.metres, 4), "system": d.length.system,
               "measured_units": round(d.measured_units, 3), "ratio": d.ratio, "how": d.how,
               "end_marks": list(d.end_marks), "p1": list(d.p1), "p2": list(d.p2)}
        if mpu:
            row["measured_m"] = round(d.measured_units * mpu, 4)
            row["off_pct"] = round((d.ratio - mpu) / mpu * 100.0, 3)
        rows.append(row)
    return rows


def _size_label_rows(rows: list[dict]) -> list[dict]:
    out = []
    for row in rows:
        for b in row["names"][:1]:
            check = LB.check_label_size(b, row["polygon"]) if b.size else None
            if check is not None:
                out.append({"name": b.name, **check})
    return out


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def extract(page: GenericPage, level_id: str, file_rel: str, answers=None, no_ai: bool = False,
            rec_dir: Optional[str | Path] = None) -> LevelExtraction:
    """One generic page -> ``LevelExtraction`` in the building frame (see the module docstring)."""
    ex = LevelExtraction(file=file_rel, page=page.page, level_id=level_id, units=page.units,
                         page_size=[float(page.size[0]), float(page.size[1])], source_kind=page.source_kind)
    ex.report = {}
    where = f"{file_rel} p{page.page}" if page.source_kind != "dxf" else file_rel
    ex.warnings.extend(page.warnings)
    page_no = _evidence_page(page)

    # 1. Texts and the unit system.
    ex.units_system = LB.page_unit_system(page.texts)
    turkish = LB.page_is_turkish(page.texts)
    ex.report["turkish"] = turkish
    ex.report["unlabelled_label"] = UNLABELLED_TURKISH if turkish else UNLABELLED_ENGLISH

    # 2. Dimensions and the provisional scale.
    dims = SC.find_dimensions(page)
    sc, reasons = SC.provisional_scale(page, dims)
    ex.report["scale_reasons"] = list(reasons)
    ex.report["dimensions"] = _dimension_rows(dims, sc["metres_per_unit"] if sc else None)
    ex.report["dims_page"] = dims
    dim_text_ids = {d.text_id for d in dims}
    if sc is None:
        ex.texts = _text_items(page, dim_text_ids, set())
        ex.warnings.append(f"{where}: no scale source ({reasons[-1] if reasons else 'no scale note, no dimensions'})")
        return ex
    s = float(sc["metres_per_unit"])
    strokes_m, texts_m = to_metres(page, s)

    # 3. Walls and openings (G2's order, tests/_real01_page.py g2_chain).
    prims = W.wall_primitives(page, s)
    mask = W.wall_mask(page, prims, s)
    prim_ids = {i for p in prims for i in p.stroke_ids}
    walls, wall_info = W.walls_from_mask(mask, [st for st in strokes_m if st.id not in prim_ids], file_rel, page_no,
                                         units_to_m=s)
    ex.warnings.extend(f"{where}: {w}" for w in wall_info.get("warnings", []))
    wall_strokes = prim_ids - set(wall_info.get("dropped_strokes", []))
    non_wall = [st for st in strokes_m if st.id not in wall_strokes]
    walls2, openings, gap_log, owned = O.gaps_and_openings(walls, non_wall, file_rel, page_no, units_to_m=s)
    ex.report["wall_info"] = {k: v for k, v in wall_info.items() if k != "dropped_strokes"}
    ex.report["mask"] = mask
    ex.report["units_to_m"] = s

    # 4. Label blocks, plot and building.
    blocks = LB.merge_label_blocks(texts_m, file_rel, page_no)
    bwalls, site, site_warnings = TP.split_plot(walls2, openings, blocks, level_id=level_id)
    for w in site_warnings:
        if w.startswith(TP.REVIEW_PREFIX):
            ex.review.append(f"{where}: {w[len(TP.REVIEW_PREFIX):]}")
        else:
            ex.warnings.append(f"{where}: {w}")
    site_idx = {o["index"] for o in site["openings"]}
    b_openings = [o for k, o in enumerate(openings) if k not in site_idx]
    if not bwalls:
        ex.review.append(f"{where}: no building walls found")
    problem = TP.outer_loop_problem(bwalls, b_openings)
    if problem is not None:
        ex.review.append(f"{where}: outer walls do not close ({problem})")
    outline = TP.building_outline(bwalls, b_openings)

    # 5. Furniture, separators, faces.
    pieces, cands, decor = SY.furniture(non_wall, owned, bwalls, b_openings, texts_m, dims, outline, [],
                                        wall_strokes=wall_strokes, site_walls=site["boundary_walls"],
                                        level_id=level_id, file_rel=file_rel, page_no=page_no, units_to_m=s,
                                        notes=ex.notes)
    site["decor"] = decor
    stairs = [p for p in pieces if p.type == "stair"]
    seps, sep_log = TP.separators(bwalls, b_openings, gap_log, blocks, stairs, units_to_m=s)
    rows = face_table(TP.faces(bwalls, b_openings, seps), blocks, bwalls, b_openings, stairs)
    SY.apply_room_checks(pieces, cands, [{"polygon": r["polygon"], "room_type": r["room_type"], "label": r["label"]}
                                         for r in rows], ex.notes)
    for cand in cands:
        pt = Point(cand["footprint"]["center"])
        row = next((r for r in rows if r["polygon"].contains(pt)), None)
        cand["room_type"] = row["room_type"] if row else None
        cand["_ids"] = _expand_ids(cand["item"].evidence.get("entity"))
    ex.report["gaps"] = gap_log
    ex.report["separators"] = sep_log
    ex.report["size_labels"] = _size_label_rows(rows)
    ex.report["owned"] = sorted(owned)

    # 6. Confirm the scale with the room-size labels.
    faces_m = [(r["polygon"], r["names"][0] if r["names"] else None) for r in rows]
    confirmed, scale_conflicts, scale_warnings = SC.confirm_scale(sc, dims, blocks, faces_m)
    ex.report["scale_reasons"].extend(scale_warnings)
    if confirmed is None:
        reason = next((w for w in reversed(scale_warnings) if w.startswith("scale not corroborated")),
                      "scale not corroborated")
        ex.review.append(f"{where}: {reason}")
        ex.warnings.append(f"{where}: {reason}")
        ex.texts = _text_items(page, dim_text_ids, {r.id for b in blocks for r in b.runs})
        return ex
    ex.scale = confirmed
    for w in scale_warnings:
        if not w.startswith("scale not corroborated"):
            ex.warnings.append(f"{where}: {w}")
    # One conflict per dimension: the pipeline's dimension_vs_measured check covers every dimension text; only a
    # disputed scale note (kept against the dimensions) is a scale_disagreement of its own, as in pdf_extract.
    if confirmed["method"] == "pdf_scale_text" and confirmed["confidence"] < 1.0 and scale_conflicts:
        note = next((r for r in reasons if "scale note kept" in r), None)
        ex.conflicts.append({"kind": "scale_disagreement", "element_ids": [],
                             "description": note or f"{where}: the scale note disagrees with the dimension texts",
                             "resolution": "scale note kept (drawn standard scale); every dimension text is checked "
                                           "against the length measured at that scale"})

    # 7. AI candidates: crops, questions, answers.
    wall_polys = [TP.wall_polygon(w) for w in bwalls]
    others = []
    for st in non_wall:
        if not st.pts:
            continue
        xs = [p[0] for p in st.pts]
        ys = [p[1] for p in st.pts]
        others.append(({st.id}, (min(xs), min(ys), max(xs), max(ys)), st.pts))
    _ask_and_apply(ex, page, cands, wall_polys, others, answers, no_ai, Path(rec_dir) if rec_dir is not None else None,
                   level_id)

    # 8. The building frame.
    if bwalls:
        union = TP.bridged_union(bwalls)
        ox, oy = union.bounds[0], union.bounds[1]
    else:
        ox, oy = 0.0, 0.0
    sh = _Shift(ox, oy)
    ex.transform_to_building = [s, 0.0, -ox, 0.0, s, -oy]
    for w in bwalls:
        _shift_wall(w, sh)
    for o in b_openings + seps:
        _shift_opening(o, sh)
    furniture = pieces + [c["item"] for c in cands]
    for f in furniture:
        _shift_piece(f, sh)
    _shift_site(site, sh)
    for row in sep_log:
        if row.get("line"):
            row["line_building"] = [list(sh.p(q)) for q in row["line"]]
    ex.walls = bwalls
    ex.openings = b_openings
    ex.separators = seps
    ex.furniture = furniture
    ex.site = site
    # The candidates as asked (page metres, the crop and hash inputs); their FurnitureItems are in ex.furniture.
    ex.candidates = [{k: v for k, v in c.items() if k not in ("item", "_ids")} for c in cands]
    ex.report["origin_m"] = [ox, oy]

    # Texts, labels and dimensions (page units; the pipeline maps them with transform_to_building).
    label_run_ids = {r.id for b in blocks for r in b.runs}
    ex.texts = _text_items(page, dim_text_ids, label_run_ids)
    for b in blocks:
        first = b.name_runs[0]
        box = b.box or first.box
        ev = b.evidence[0] if b.evidence else _text_evidence(page, first)
        ex.labels.append(TextItem(text=b.name, start=(b.anchor[0] / s, b.anchor[1] / s),
                                  box=[round(v / s, 3) for v in box], rotation_deg=first.rotation_deg,
                                  entity=first.id, height=first.height / s, role="room_label",
                                  evidence=ev, block=b, turkish=turkish))
    for d in dims:
        p1, p2 = sh.p((d.p1[0] * s, d.p1[1] * s)), sh.p((d.p2[0] * s, d.p2[1] * s))
        if p2 < p1:
            p1, p2 = p2, p1
        run = next((t for t in page.texts if t.id == d.text_id), None)
        box = [round(v, 3) for v in run.box] if run is not None else [min(d.p1[0], d.p2[0]), min(d.p1[1], d.p2[1]),
                                                                      max(d.p1[0], d.p2[0]), max(d.p1[1], d.p2[1])]
        ev = _text_evidence(page, run) if run is not None else B.evidence(file_rel, "vector", 1.0, page=page_no,
                                                                          entity=d.text_id, text=d.text)
        ex.dimensions.append(DimensionItem(p1=p1, p2=p2, measured=round(math.dist(p1, p2), 4), printed=d.text,
                                           printed_value=round(d.length.metres, 6), box=box, entity=d.text_id,
                                           evidence=ev, tick_count=sum(1 for m in d.end_marks if m == "tick")))
    return ex


def _text_items(page: GenericPage, dim_ids: set, label_ids: set) -> list[TextItem]:
    """Every text run of the page as a ``TextItem`` (page units) with its role."""
    out = []
    for run in page.texts:
        if not run.text or not run.text.strip():
            continue
        out.append(TextItem(text=run.text.strip(), start=(run.box[0], run.box[1]), box=[round(v, 3) for v in run.box],
                            rotation_deg=run.rotation_deg, entity=run.id, height=run.height,
                            role=_role(run.text, dim_ids, label_ids, run.id), evidence=_text_evidence(page, run)))
    return out


def unit_text(metres: float, system: Optional[str]) -> str:
    """A length for reports: imperial ``11' 3" (3.43 m)``; metric ``3,43 m``."""
    if system == "imperial":
        return f"{U.format_length(metres, 'imperial')} ({metres:.2f} m)"
    return U.format_length(metres, "metric")
