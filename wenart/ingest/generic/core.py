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

import dataclasses
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


def _front_values(cand: dict) -> list[dict]:
    """``symbols.front_candidates`` (``[{"front_deg", "rule"}]``, or plain angles) as ``{"front_deg", "rule"}``
    dicts for ``recognition.symbols.decide``, which names the rule of a front it keeps as assumed."""
    out = []
    for c in cand.get("front_candidates") or []:
        v, rule = (c.get("front_deg"), c.get("rule")) if isinstance(c, dict) else (c, None)
        if v is not None:
            out.append({"front_deg": float(v), "rule": rule})
    return out


def _apply_front(item: FurnitureItem, front_deg: float) -> None:
    """Set a known front: an unrotated piece faces -Y, so rotation = front + 90; width stays across the front."""
    rotation = (front_deg + 90.0) % 360.0
    old = item.rotation_deg % 180.0
    if abs(((rotation % 180.0) - old + 90.0) % 180.0 - 90.0) > 1.0:
        item.size = (item.size[1], item.size[0])
    item.rotation_deg = round(rotation, 3)
    item.front_deg = round(front_deg % 360.0, 3)


def _apply_decision(item: FurnitureItem, result: dict, table: Optional[dict] = None) -> list[str]:
    """Apply ``recognition.symbols.decide``'s result to the candidate's piece. A front (agreed, or the drawn one kept
    as assumed when both passes answered none: ``details["front_assumed"]`` and ``details["front_rule"]``) sets
    rotation and width; a typed piece without a front is oriented by its type's width/depth convention
    (``symbols.oriented_size``), the front stays unknown (review ingest-6: the no-front rule's 'width = longer side'
    built real01's beds 90 deg off). Returns the warnings for what was assumed (never silent): the orientation by
    the type's convention (the result's own warnings already name an assumed front)."""
    from wenart.recognition import symbols as RS

    messages: list[str] = []
    item.type = result["type"]
    item.status = result["status"]
    item.type_method = result["type_method"]
    item.type_candidates = list(result["type_candidates"])
    item.extra_evidence = list(result["ai_evidence"])
    if result.get("front") is not None:
        _apply_front(item, float(result["front"]))
        if result.get("front_assumed"):
            item.details["front_assumed"] = True
            if result.get("front_rule"):
                item.details["front_rule"] = result["front_rule"]
    elif (result["type"] in SY.LONG_BACK_TYPES and item.details.get("corner_front") is not None
          and result.get("front_conflict") is None):
        # M11 (real02 wardrobes in a bedroom corner): no agreed front, but the piece stands in a corner with its long
        # side on a wall and its type has its back on the long side: that side is the back (drawing rule, assumed).
        rule = "corner: the long side against a wall is the back"
        _apply_front(item, float(item.details["corner_front"]))
        item.details["front_assumed"] = True
        item.details["front_rule"] = rule
        key = item.details.get("candidate_key") or item.entity
        messages.append(f"{key}: {result['type']} without an agreed front: front {item.front_deg:g} deg assumed "
                        f"({rule})")
    elif result["type"] != "unknown":
        size, rotation, swapped = RS.oriented_size(item.size, item.rotation_deg, result["type"], table)
        if swapped:
            item.size, item.rotation_deg = (round(size[0], 4), round(size[1], 4)), rotation
        turned = " (footprint turned 90 deg)" if swapped else ""
        if result["type"] in RS.FRONTLESS_TYPES:
            item.details["front_note"] = (f"{result['type']} has no front: width and depth follow its size "
                                          f"convention{turned}")
        else:
            item.details["front_note"] = (f"front unknown: width and depth follow the {result['type']} size "
                                          f"convention{turned}")
            key = item.details.get("candidate_key") or item.entity
            messages.append(f"{key}: {result['type']} without an agreed front: {item.details['front_note']}; the "
                            "side the builder faces is assumed")
    if result.get("confidence") is not None:
        item.details["type_confidence"] = result["confidence"]
    if result.get("build") is False:
        item.details["build"] = False
    if result.get("note"):
        item.details["note"] = result["note"]
    if result.get("conflict"):
        item.details["ai_conflict"] = dict(result["conflict"])
    if result.get("front_conflict"):
        item.details["front_conflict"] = dict(result["front_conflict"])
        if result.get("front_rule"):
            item.details["front_rule"] = result["front_rule"]
    return messages


def _ask_and_apply(ex: LevelExtraction, page: GenericPage, cands: list[dict], wall_polys: list, others: list, answers,
                   no_ai: bool, rec_dir: Optional[Path], level_id: str, raster=None,
                   evidence_only: bool = False) -> None:
    """Crops and questions for every candidate; the two-pass rule where answers exist (§3.3). Raster candidates are
    pixel crops of the rectified page (``raster.image``, context ``{image, to_px}``, §3.1); an evidence-only raster
    page asks nothing (§0).

    The question carries the item's facts (``recognition.symbols.question_facts``, prep pod finding P5): on vector
    pages also the room's printed label and type (``room_label``/``room_type``) and the neighbours among this page's
    candidates of the same face (``room_index``; ``symbols.neighbour_facts``). Raster questions carry neither: their
    names and clusters may change with the label answers of the same round, and the hash must not."""
    if not cands:
        ex.report["questions"], ex.report["pending"] = [], []
        return
    is_raster = page.source_kind.startswith("raster")
    if is_raster and (raster is None or evidence_only):
        why = "evidence-only raster page: no AI questions (§0)" if evidence_only else \
            "no rectified page image to crop from"
        ex.notes.append(f"{page.file} p{page.page}: {len(cands)} raster furniture candidates not asked ({why}); "
                        f"they stay unknown, unverified")
        ex.report["questions"], ex.report["pending"] = [], []
        return
    from wenart.recognition import answers as A
    from wenart.recognition import crops as CR
    from wenart.recognition import symbols as RS

    raster_context = None
    if is_raster:
        s = float(ex.report["units_to_m"])
        raster_context = {"image": raster.image, "to_px": [1.0 / s, 0.0, 0.0, 0.0, -1.0 / s, float(page.size[1])]}
        neighbours = {}
    else:
        neighbours = RS.neighbour_facts([{"key": c["key"], "footprint": c["footprint"],
                                          "room_index": c.get("room_index")} for c in cands])
    items = []
    for cand in cands:
        crop_cand = {"key": cand["key"], "footprint": cand["footprint"], "strokes": cand["strokes"],
                     "bbox": cand["bbox"], "_ids": cand["_ids"]}
        if raster_context is None:
            crop_cand.update(room_label=cand.get("room_label"), room_type=cand.get("room_type"),
                             room_index=cand.get("room_index"), neighbours=neighbours.get(cand["key"]))
        context = raster_context if raster_context is not None else _crop_context(crop_cand, wall_polys, others)
        crop_cand.pop("_ids")
        if rec_dir is not None:
            crops = CR.render_pair(crop_cand, context, Path(rec_dir) / A.CROPS_DIR, cand["key"])
        else:
            desc = (CR.raster_crops(crop_cand, context)[0] if raster_context is not None
                    else CR.vector_description(crop_cand, context))
            names = CR.crop_names(cand["key"])
            crops = {"ctx_png": names[0], "iso_png": names[1], "input_sha256": CR.canonical_sha256(desc),
                     "crop": dict({k: desc[k] for k in ("object_box", "ctx_box", "iso_box")}, kind=desc["kind"]),
                     "question": desc["question"]["facts"]}
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
              "file": page.file, "page": _evidence_page(page), "front_candidates": _front_values(cand),
              "wall_fronts": list(cand.get("wall_fronts") or [])}
        result = RS.decide(dc, got, table, cand.get("room_type"))
        assumed = _apply_decision(cand["item"], result, table)
        ex.warnings.extend(result.get("warnings") or [])
        ex.warnings.extend(assumed)
        decided += 1
    ex.report["questions"] = items
    ex.report["pending"] = [] if no_ai else pending
    ex.report["answers_applied"] = decided
    if pending:
        ex.notes.append(f"{len(pending)} of {len(cands)} furniture candidates have no complete pair of answers"
                        + (" (--no-ai: they stay unknown, unverified)" if no_ai else ""))


# --------------------------------------------------------------------------
# Raster pages (area S, §3.4, §4)
# --------------------------------------------------------------------------

def _face_px(poly, s: float, height: float) -> list[tuple[float, float]]:
    """A face polygon in page metres -> rectified image pixels (pixel-corner coordinates, y down)."""
    return [(x / s, height - y / s) for x, y in list(poly.exterior.coords)[:-1]]


def _box_m_from_px(box_px, s: float, height: float) -> tuple[float, float, float, float]:
    x0, y0, x1, y1 = box_px
    return (x0 * s, (height - y1) * s, x1 * s, (height - y0) * s)


AI_BOX_TEXT_H = 4.0                # an accepted VLM label box blanks ink only when <= 4 text heights across ...
AI_BOX_CHAR_W = 1.2                # ... <= (characters + 2) x 1.2 text heights long ...
AI_GLYPH_TEXT_H = 1.6              # ... and every stroke it would blank is letter-sized (sides <= 1.6 text heights)


def _ocr_text_height_px(raster) -> float:
    """Median height (rectified pixels) of the page's OCR texts read with confidence >= 0.6; 0 without any."""
    heights = []
    for it in getattr(raster, "texts", None) or []:
        if float(it.get("confidence") or 0) < 0.6:
            continue
        x0, y0, x1, y1 = it["box"]
        heights.append((x1 - x0) if it.get("rotation") == 90 else (y1 - y0))
    heights.sort()
    if not heights:
        return 0.0
    m = len(heights) // 2
    return float(heights[m]) if len(heights) % 2 else (heights[m - 1] + heights[m]) / 2.0


def _words(text) -> list[str]:
    """The words of a normalised label (``room_labels.norm_value``), letters and digits only (marks dropped)."""
    from wenart.recognition import room_labels as RL
    words = ("".join(ch for ch in w if ch.isalnum()) for w in (RL.norm_value(text) or "").split())
    return [w for w in words if w]


def _ocr_agrees(ai: str, ocr: str) -> bool:
    """Whether a name the passes agree on and a name Tesseract read in the same face say the same thing: the same
    letters ('Bath*' read for 'Bath+', 'Bed Room' for 'Bedroom'), or the words of one run on inside the other (OCR
    read a stray mark beside the name, 'Drawing Room MI', or only part of it). Different words are a conflict."""
    a, o = _words(ai), _words(ocr)
    if not a or not o:
        return False
    if "".join(a) == "".join(o):
        return True
    short, long_ = (a, o) if len(a) <= len(o) else (o, a)
    return any(long_[i:i + len(short)] == short for i in range(len(long_) - len(short) + 1))


def _agreed_box_px(decision: dict) -> Optional[list[float]]:
    """Where the accepted label is printed (rectified pixels): the Tesseract box on the Tesseract path; on the
    two-pass path the intersection of both passes' boxes (keep what agrees: both must give a box and they must
    overlap). None otherwise. Read before the evidence boxes are mapped to the original image."""
    field = decision["fields"]["label"]
    if field["path"] == "tesseract":
        match = field.get("tesseract_match") or {}
        return [float(v) for v in match["box"]] if match.get("box") else None
    if field["path"] != "two_pass":
        return None
    boxes = [e.get("pixel_box") for e in decision["evidence"] if e.get("method") == "ai"]
    if len(boxes) < 2 or any(not b for b in boxes):
        return None
    x0, y0 = max(b[0] for b in boxes), max(b[1] for b in boxes)
    x1, y1 = min(b[2] for b in boxes), min(b[3] for b in boxes)
    return [float(x0), float(y0), float(x1), float(y1)] if x1 > x0 and y1 > y0 else None


def _ai_block(label: str, decision: dict, key: str, poly, s: float, height: float, page: GenericPage,
              box_px: Optional[list[float]] = None) -> "LB.LabelBlock":
    """A label block for a room name the passes accepted but no Tesseract block of the face carries (§3.4). The
    anchor is the centre of the agreed box (``_agreed_box_px``) when it lies in the face, else a point inside the
    face; no extent is invented: without an agreed box the block's box is its anchor point."""
    box = None
    if box_px:
        box = _box_m_from_px(box_px, s, height)
        anchor = ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)
        if not poly.contains(Point(anchor)):
            box = None
    if box is None:
        pt = poly.representative_point()
        anchor = (pt.x, pt.y)
        box = (anchor[0], anchor[1], anchor[0], anchor[1])
    ev = [e for e in decision.get("evidence") or [] if e.get("method") == "ai"]
    run = TextRun(id=f"ai:{key}", text=label, box=box, height=max(box[3] - box[1], 1e-6), source="ai",
                  evidence=[dict(e) for e in ev])
    area, aspect = _face_aspect(poly)
    room_type, exterior = LB.room_type_for(label, area, aspect)
    size_text = decision.get("size_text")
    area_text = decision.get("area_text")
    size = U.parse_size_pair(size_text) if size_text else None
    parsed_area = U.parse_area(area_text) if area_text else None
    return LB.LabelBlock(name=label, name_runs=[run], size_text=size_text, area_text=area_text, anchor=anchor,
                         room_type=room_type, exterior=exterior, evidence=[dict(e) for e in ev], size=size,
                         area_m2=parsed_area[0] if parsed_area else None, box=box, runs=[run])


def _blank_run(label: str, key: str, box_px: Optional[list[float]], poly, s: float, height: float, strokes: list,
               text_h_px: float, evidence: list) -> tuple[Optional[TextRun], Optional[str]]:
    """The text run whose box blanks an accepted VLM label's glyph strokes before the final clustering (§3.4,
    §4.2), or ``(None, why)``. An AI box is checked against the page before it removes anything (AI proposes, the
    source decides): clipped to its face, at most ``AI_BOX_TEXT_H`` text heights across and (characters + 2) x
    ``AI_BOX_CHAR_W`` text heights long, and every stroke it would blank (a segment inside the box grown like
    ``symbols``' text boxes) letter-sized. A box that fails blanks nothing; the reason is reported."""
    from shapely.geometry import LineString, box as sbox

    if not box_px:
        return None, None
    if text_h_px <= 0:
        return None, "no OCR text height on the page to check the box against"
    clipped = sbox(*_box_m_from_px(box_px, s, height)).intersection(poly)
    if clipped.is_empty or clipped.area <= 0:
        return None, "the box lies outside its room face"
    x0, y0, x1, y1 = clipped.bounds
    th = text_h_px * s
    short, long_ = sorted((x1 - x0, y1 - y0))
    if short > AI_BOX_TEXT_H * th or long_ > (len(label.strip()) + 2) * AI_BOX_CHAR_W * th:
        return None, (f"the box ({x1 - x0:.2f} x {y1 - y0:.2f} m) is larger than the label's text (text height "
                      f"{th:.2f} m)")
    gx, gy = (x1 - x0) * SY.TEXT_GROW / 2.0, (y1 - y0) * SY.TEXT_GROW / 2.0
    grown = sbox(x0 - gx, y0 - gy, x1 + gx, y1 + gy)
    big, inside = [], 0
    for st in strokes:
        pts = [tuple(p) for p in st.pts or []]
        if not pts:
            continue
        parts = [LineString([a, b]) for a, b in zip(pts, pts[1:]) if a != b] or [Point(pts[0])]
        if not any(grown.contains(g) for g in parts):
            continue
        inside += 1
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        if max(max(xs) - min(xs), max(ys) - min(ys)) > AI_GLYPH_TEXT_H * th:
            big.append(st.id)
    if big:
        return None, (f"it would remove {len(big)} drawn strokes larger than a letter "
                      f"({', '.join(big[:6])}{', ...' if len(big) > 6 else ''})")
    if not inside:
        return None, None
    return TextRun(id=f"ai:{key}", text=label, box=(x0, y0, x1, y1), height=y1 - y0, source="ai",
                   evidence=[dict(e) for e in evidence]), None


def _to_original_evidence(evidence: list, page: GenericPage, height: float) -> None:
    """Room-label evidence boxes come from ``room_labels.decide`` in rectified pixels (pixel corners, y down); the
    building JSON points at the original image (§4.1). Mapped in place (``ai``/``ocr`` evidence: the geometry-only
    ``_raster_evidence_boxes`` never maps them again)."""
    if not page.to_original:
        return
    for e in evidence:
        box = e.get("pixel_box")
        if not box or e.get("_original"):
            continue
        x0, y0, x1, y1 = box
        e["pixel_box"] = _raster_box(page, (x0, height - y1, x1, height - y0))


def _raster_labels(ex: LevelExtraction, page: GenericPage, raster, rows: list[dict], blocks: list, s: float,
                   level_id: str, answers, no_ai: bool, rec_dir: Optional[Path], evidence_only: bool,
                   strokes: Optional[list] = None):
    """§3.4 on a raster page: one ``room_label`` question per room face (crop of the rectified page grown by 0.5 m),
    decided by ``room_labels.decide`` (two passes agree, or one pass equals a Tesseract text read inside the face).

    Returns ``(blocks, scale_blocks, items, pending, report, blank_runs)``: the label blocks after the decisions (an
    accepted label replaces the other names Tesseract read in its face, listed as ``dropped``; a label accepted
    without a Tesseract block becomes an ``ai`` block), the blocks whose printed size may corroborate the scale (only
    sizes accepted by the same rule, §3.4), the request items, the keys still waiting for answers, one report row per
    face and the checked VLM label boxes whose glyph strokes are blanked before the final clustering
    (``_blank_run``; ``strokes`` = the non-wall strokes, page metres).

    OCR outranks AI (CLAUDE.md): a name both passes agree on that differs from every name Tesseract read in the
    face is not accepted: Tesseract's names stay (unconfirmed, the room ``unverified``) and the row carries a
    ``conflict`` for the pipeline. Names with the same letters or words (``_ocr_agrees``) agree. Evidence boxes
    point at the original image. Without answers (or with ``--no-ai``) every Tesseract name stays, unconfirmed: the
    pipeline marks such rooms ``unverified``. Evidence-only pages ask nothing (§0)."""
    import tempfile

    from wenart.recognition import answers as A
    from wenart.recognition import room_labels as RL

    height = float(page.size[1])
    ocr_items = [it for it in (getattr(raster, "texts", None) or []) if float(it.get("confidence") or 0) >= 0.6]
    text_h_px = _ocr_text_height_px(raster)
    image = raster.image
    loaded: dict = {}
    items, pending, report, blank_runs = [], [], [], []
    faces = []
    for k, row in enumerate(rows):
        if row["exterior"]:
            continue
        poly_px = _face_px(row["polygon"], s, height)
        tess = RL.items_inside(ocr_items, poly_px)
        faces.append((k, row, poly_px, tess, f"lbl_{level_id}_{len(faces) + 1}"))
    if not evidence_only:
        with tempfile.TemporaryDirectory() as tmp:
            crop_dir = Path(rec_dir) / A.CROPS_DIR if rec_dir is not None else Path(tmp)
            built = []
            for k, row, poly_px, tess, key in faces:
                xs = [p[0] for p in poly_px]
                ys = [p[1] for p in poly_px]
                crop = RL.render_crop(image, [min(xs), min(ys), max(xs), max(ys)], 1.0 / s, crop_dir, key)
                face = {"key": key, "file": page.file, "page": _evidence_page(page), "level": level_id,
                        "room_id": None, "crop": crop}
                items.append(RL.question(face))
                built.append(face)
        if isinstance(answers, (str, Path)):
            loaded = A.load(Path(answers), items)
        elif isinstance(answers, dict):
            loaded = answers
        face_dicts = {f["key"]: f for f in built}
    else:
        face_dicts = {}
    new_blocks = [b for b in blocks if not any(b in row["names"] for _, row, _, _, _ in faces)]
    scale_blocks = list(new_blocks)
    for k, row, poly_px, tess, key in faces:
        got = loaded.get(key) or {}
        if items and not all(got.get(m) is not None for m in A.MODEL_KEYS):
            pending.append(key)
        face = face_dicts.get(key) or {"key": key, "file": page.file, "page": _evidence_page(page),
                                       "level": level_id, "room_id": None}
        decision = RL.decide(face, got, tesseract=tess) if not evidence_only else None
        label = decision["label"] if decision else None
        path = decision["fields"]["label"]["path"] if decision else None
        box_px = _agreed_box_px(decision) if label else None
        if decision:
            _to_original_evidence(decision["evidence"], page, height)
        names = row["names"]
        entry = {"key": key, "face": k, "tesseract": [t["text"] for t in tess], "label": label, "path": path,
                 "status": "verified" if label else "unverified",
                 "names": [b.name for b in names],
                 "candidates": decision["fields"]["label"]["candidates"] if decision else [],
                 "evidence": decision["evidence"] if decision else [],
                 "size_text": decision.get("size_text") if decision else None}
        keep = source = None
        if label:
            source = next((b for b in names if RL.norm_value(b.name) == RL.norm_value(label)), None)
            keep = source
            if source is None and names and path == "two_pass":
                source = next((b for b in names if _ocr_agrees(label, b.name)), None)
                if source is not None:
                    # Tesseract read the same words with other marks, a stray mark beside them or part of them:
                    # the passes' spelling, Tesseract's block (its glyph boxes) and evidence.
                    keep = dataclasses.replace(source, name=label)
                    entry["ocr_spelling"] = source.name
                else:
                    # OCR outranks AI: the agreed name is not accepted against what Tesseract read in the face.
                    for e in decision["evidence"]:
                        if e.get("method") == "ai":
                            e["confidence"] = RL.UNACCEPTED_CONFIDENCE
                    entry["conflict"] = {"ai": label, "ocr": [b.name for b in names],
                                         "ocr_evidence": [dict(b.evidence[0]) for b in names if b.evidence]}
                    entry.update(label=None, status="unverified")
                    label = None
        if label:
            if keep is None:
                keep = _ai_block(label, decision, key, row["polygon"], s, height, page, box_px)
                ai_ev = [e for e in decision["evidence"] if e.get("method") == "ai"]
                run, why = _blank_run(label, key, box_px, row["polygon"], s, height, strokes or [], text_h_px, ai_ev)
                if run is not None:
                    blank_runs.append(run)
                    entry["blank_box_m"] = [round(v, 4) for v in run.box]
                elif why:
                    entry["blank_refused"] = why
                    ex.warnings.append(f"{page.file} p{page.page}: {key} '{label}': the agreed VLM label box is not "
                                       f"blanked ({why}); the drawn strokes stay")
            else:
                keep.evidence = list(keep.evidence) + [dict(e) for e in decision["evidence"]
                                                        if e.get("method") == "ai"]
            entry["dropped"] = [b.name for b in names if b is not source]
            accepted_size = decision["fields"]["size_text"]["path"] is not None
            parsed = U.parse_size_pair(decision["size_text"]) if accepted_size and decision.get("size_text") else None
            if parsed is not None and keep.size_text != decision["size_text"]:
                # The accepted printed size replaces what Tesseract read (or missed) under the name.
                keep = dataclasses.replace(keep, size_text=decision["size_text"], size=parsed)
            new_blocks.append(keep)
            scale_blocks.append(keep if accepted_size else dataclasses.replace(keep, size=None))
            pt = Point(keep.anchor)
            entry["anchor"] = [round(pt.x / s, 2), round(pt.y / s, 2)]
        else:
            for b in names:
                new_blocks.append(b)
                # Tesseract alone never confirms a printed size for the scale (§3.4).
                scale_blocks.append(dataclasses.replace(b, size=None))
            entry["anchor"] = [round(b.anchor[0] / s, 2) for b in names[:1]] + \
                [round(b.anchor[1] / s, 2) for b in names[:1]]
        report.append(entry)
    return new_blocks, scale_blocks, items, pending, report, blank_runs


RASTER_JOINT_PX = 1.5              # raster wall joints: an end this close (pixels) to another wall's face is joined


def _close_raster_joints(walls: list, tol: float) -> list[str]:
    """Raster pages: a wall end that stops short of another (not parallel) wall's face by at most ``tol`` (page
    metres; ``RASTER_JOINT_PX`` pixels, the measuring precision of the mask) is moved onto that face, so the room
    faces close as on a vector page (real01's scan: the bath wall 5 mm short of the bath's west wall, the bath and
    the hall one face; synthetic-01's scan: joints 14-16 mm open). Ends touching a wall already and wider gaps
    (doors, passages, a wall beside a parallel one) stay. Returns one line per moved end (``WallItem``s in place)."""
    from shapely.geometry import LineString, Polygon as SPolygon

    polys = [TP.wall_polygon(w) for w in walls]
    moved = []
    for i, w in enumerate(walls):
        (x0, y0), (x1, y1) = w.start, w.end
        length = math.hypot(x1 - x0, y1 - y0)
        if length <= 0 or w.thickness <= 0:
            continue
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        half = w.thickness / 2.0
        for which in ("start", "end"):
            px, py = (w.start if which == "start" else w.end)
            dx, dy = (-ux, -uy) if which == "start" else (ux, uy)
            a, b = (px - uy * half, py + ux * half), (px + uy * half, py - ux * half)
            cap = LineString([a, b])
            others = [(j, q) for j, q in enumerate(polys) if j != i]
            if any(cap.distance(q) <= 1e-9 for _, q in others):
                continue                                     # joined already
            strip = SPolygon([a, b, (b[0] + dx * tol, b[1] + dy * tol), (a[0] + dx * tol, a[1] + dy * tol)])
            hits = []
            for j, q in others:
                v = walls[j]
                vx, vy = v.end[0] - v.start[0], v.end[1] - v.start[1]
                vlen = math.hypot(vx, vy)
                if vlen <= 0 or abs(ux * vx + uy * vy) / vlen > math.cos(math.radians(30.0)):
                    continue                                 # parallel: a run gap, not a joint
                if strip.intersects(q):
                    hits.append((cap.distance(q), j))
            if not hits:
                continue
            gap, j = min(hits)
            if not 0.0 < gap <= tol:
                continue
            new = (px + dx * gap, py + dy * gap)
            if which == "start":
                w.start = new
            else:
                w.end = new
            polys[i] = TP.wall_polygon(w)
            moved.append(f"wall {i} {which} +{gap * 1000:.0f} mm")
    return moved


def _raster_box(page: GenericPage, box) -> list[float]:
    """A page-unit box (y up) -> the box of its corners in the original image (pixel-corner coordinates)."""
    h = page.to_original
    x0, y0, x1, y1 = box
    pts = []
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        w = h[2][0] * x + h[2][1] * y + h[2][2]
        pts.append(((h[0][0] * x + h[0][1] * y + h[0][2]) / w + 0.5, (h[1][0] * x + h[1][1] * y + h[1][2]) / w + 0.5))
    return [round(min(p[0] for p in pts), 1), round(min(p[1] for p in pts), 1), round(max(p[0] for p in pts), 1),
            round(max(p[1] for p in pts), 1)]


def _raster_evidence_boxes(ex: LevelExtraction, page: GenericPage) -> None:
    """Raster geometry evidence carries its box in page units (``walls``/``openings``/``symbols``); the building
    JSON points at the original image instead (§4.1: every ``pixel_box`` is checkable in the file as given)."""
    if not page.to_original:
        return
    seen: set[int] = set()

    def fix(ev) -> None:
        if not isinstance(ev, dict) or id(ev) in seen:
            return
        seen.add(id(ev))
        if ev.get("method") == "raster" and ev.get("pixel_box") and not ev.get("_original"):
            ev["pixel_box"] = _raster_box(page, ev["pixel_box"])

    for item in list(ex.walls) + list(ex.openings) + list(ex.separators) + list(ex.furniture):
        fix(item.evidence)
        for e in getattr(item, "extra_evidence", []) or []:
            fix(e)
    site = ex.site or {}
    for key in ("boundary_walls", "areas", "decor", "openings"):
        for el in site.get(key, []):
            for e in el.get("evidence", []) if isinstance(el.get("evidence"), list) else [el.get("evidence")]:
                fix(e)


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
            rec_dir: Optional[str | Path] = None, raster=None, evidence_only: bool = False,
            origin: Optional[tuple[float, float]] = None) -> LevelExtraction:
    """One generic page -> ``LevelExtraction`` in the building frame (see the module docstring).

    Milestone 10: ``origin`` (page metres) replaces the min corner of the building walls as the frame origin: the
    registered frame of the sheets stage (``sheets.json`` ``transform_to_building`` of the region, rotation 0), so
    every level of a sheet lands in one building frame.

    Raster pages (area S): ``raster`` is the adapter's ``raster.RasterPage`` (rectified image, OCR items, review
    reasons); the AI candidates get pixel crops of the rectified page, every room face a ``room_label`` question
    (§3.4), and every raster ``pixel_box`` is mapped to the original image. ``evidence_only`` (a raster page of a
    level that has a better page) asks nothing."""
    ex = LevelExtraction(file=file_rel, page=page.page, level_id=level_id, units=page.units,
                         page_size=[float(page.size[0]), float(page.size[1])], source_kind=page.source_kind)
    ex.report = {}
    where = f"{file_rel} p{page.page}" if page.source_kind != "dxf" else file_rel
    ex.warnings.extend(page.warnings)
    page_no = _evidence_page(page)
    is_raster = page.source_kind.startswith("raster")
    if is_raster:
        ex.report["raster"] = {"evidence_only": evidence_only, "labels": []}
        if raster is not None:
            ex.review.extend(f"{where}: {r}" for r in raster.review)
            ex.notes.extend(f"{where}: {n}" for n in raster.notes)

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
        if is_raster:
            # §4.3: a raster scale needs dimension texts OCR can read; VLM texts never make one. Dimensions that
            # were read but give no scale say why (the review must name the disagreement, not "none readable").
            ex.review.append(f"{where}: no dimension readable on the raster page" if not dims else
                             f"{where}: the {len(dims)} dimension texts read on the raster page give no scale "
                             f"({reasons[-1] if reasons else 'they do not agree'})")
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
    for e in gap_log:
        if e.get("kind") == "wall_piece":
            # A door leaf fused to a wall face (the run's faces kept; also in the wall's evidence note) or a frame or
            # nub at a wall end (no wall end of its own): never silent (CLAUDE.md).
            ex.notes.append(f"{where}: wall {e['wall']}: {e['note']}")
    if is_raster:
        joined = _close_raster_joints(walls2, RASTER_JOINT_PX * s)
        if joined:
            ex.notes.append(f"{where}: {len(joined)} raster wall ends moved onto the wall face they stop short of "
                            f"by <= {RASTER_JOINT_PX:g} px: " + ", ".join(joined))
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
        index = next((k for k, r in enumerate(rows) if r["polygon"].contains(pt)), None)
        row = rows[index] if index is not None else None
        cand["room_type"] = row["room_type"] if row else None
        # The symbol question names the face's printed label and groups neighbours by face (vector pages, P5).
        cand["room_label"] = row["label"] if row else None
        cand["room_index"] = index
        cand["_ids"] = _expand_ids(cand["item"].evidence.get("entity"))
    ex.report["gaps"] = gap_log
    ex.report["separators"] = sep_log
    ex.report["size_labels"] = _size_label_rows(rows)
    ex.report["owned"] = sorted(owned)

    # Raster pages: room labels by §3.4 (two passes, or one pass + Tesseract); only accepted printed sizes may
    # corroborate the scale.
    scale_blocks = blocks
    label_items, label_pending = [], []
    if is_raster:
        face_polys = [r["polygon"] for r in rows]
        dim_ids = SY._dimension_ids(dims)
        glyph_strokes = [st for st in non_wall if st.id not in owned and st.id not in dim_ids]
        blocks, scale_blocks, label_items, label_pending, label_report, ai_runs = _raster_labels(
            ex, page, raster, rows, blocks, s, level_id, answers, no_ai,
            Path(rec_dir) if rec_dir is not None else None, evidence_only, strokes=glyph_strokes)
        ex.report["raster"]["labels"] = label_report
        rows = face_table(face_polys, blocks, bwalls, b_openings, stairs)
        if ai_runs:
            # Accepted VLM label boxes, checked against the page (``_blank_run``: inside the face, text-sized, only
            # letter-sized strokes inside), are blanked before the final clustering (§3.4): those glyph strokes are
            # no furniture.
            pieces, cands, decor = SY.furniture(non_wall, owned, bwalls, b_openings, texts_m + ai_runs, dims, outline,
                                                [], wall_strokes=wall_strokes, site_walls=site["boundary_walls"],
                                                level_id=level_id, file_rel=file_rel, page_no=page_no,
                                                units_to_m=s, notes=ex.notes)
            site["decor"] = decor
            SY.apply_room_checks(pieces, cands, [{"polygon": r["polygon"], "room_type": r["room_type"],
                                                  "label": r["label"]} for r in rows], ex.notes)
        for cand in cands:
            pt = Point(cand["footprint"]["center"])
            row = next((r for r in rows if r["polygon"].contains(pt)), None)
            cand["room_type"] = row["room_type"] if row else None
            cand["_ids"] = _expand_ids(cand["item"].evidence.get("entity"))
        ex.report["size_labels"] = _size_label_rows(rows)
        scale_rows = face_table(face_polys, scale_blocks, bwalls, b_openings, stairs)
    else:
        scale_rows = rows

    # 6. Confirm the scale with the room-size labels.
    faces_m = [(r["polygon"], r["names"][0] if r["names"] else None) for r in scale_rows]
    confirmed, scale_conflicts, scale_warnings = SC.confirm_scale(sc, dims, scale_blocks, faces_m)
    ex.report["scale_reasons"].extend(scale_warnings)
    if confirmed is None:
        reason = next((w for w in reversed(scale_warnings) if w.startswith("scale not corroborated")),
                      "scale not corroborated")
        ex.review.append(f"{where}: {reason}")
        ex.warnings.append(f"{where}: {reason}")
        ex.texts = _text_items(page, dim_text_ids, {r.id for b in blocks for r in b.runs})
        if label_items:
            # The printed room sizes that could corroborate the scale wait for their label answers (§3.4): the
            # questions are written now; the run with the answers decides. §1.4 has one round of questions, so
            # the furniture candidates are asked now as well, at the provisional scale: the confirmed scale keeps
            # its metres per unit, so the crops and their input hashes are the same in the run with the answers.
            # (Raster candidates are pixel crops of the rectified page: no wall or stroke context needed.)
            _ask_and_apply(ex, page, cands, [], [], answers, no_ai, Path(rec_dir) if rec_dir is not None else None,
                           level_id, raster=raster, evidence_only=evidence_only)
            ex.report["questions"] = list(ex.report.get("questions") or []) + list(label_items)
            ex.report["pending"] = [] if no_ai else list(ex.report.get("pending") or []) + list(label_pending)
            ex.report["review_awaits_answers"] = bool(label_pending) and not no_ai
            if label_pending:
                ex.notes.append(f"{len(label_pending)} of {len(label_items)} raster room faces have no complete pair "
                                f"of label answers" + (" (--no-ai: Tesseract names stay unconfirmed)" if no_ai else
                                                       " (the scale waits for them)"))
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
                   level_id, raster=raster, evidence_only=evidence_only)
    if label_items:
        ex.report["questions"] = list(ex.report.get("questions") or []) + label_items
        if not no_ai:
            ex.report["pending"] = list(ex.report.get("pending") or []) + label_pending
        if label_pending:
            ex.notes.append(f"{len(label_pending)} of {len(label_items)} raster room faces have no complete pair of "
                            f"label answers" + (" (--no-ai: Tesseract names stay unconfirmed)" if no_ai else ""))

    # 8. The building frame.
    if origin is not None:
        ox, oy = float(origin[0]), float(origin[1])
    elif bwalls:
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
    if is_raster:
        _raster_evidence_boxes(ex, page)

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
