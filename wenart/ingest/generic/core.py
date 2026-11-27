"""The generic plan core: one ``GenericPage`` -> ``LevelExtraction`` (docs/milestone7.md §1.2, §1.5, §2).

What: ``extract(page, level_id, file_rel, answers=None, no_ai=False, rec_dir=None)`` wires the text side
(``labels``, ``scale``: G1) and the geometry side (``walls``, ``openings``, ``topology``, ``symbols``: G2) of the
generic core in the order of §1.2:

0. a sheet frame inserted as one block with its title block (``frame.frame_blocks``) is no plan geometry: its strokes
   are dropped (noted; its texts stay);
1. texts -> the page's unit system (``labels.page_unit_system``);
2. dimensions (``scale.find_dimensions``) -> provisional scale (``scale.provisional_scale``); without one the page
   returns early with ``scale = None`` (the pipeline stops with ``needs_review`` as before);
3. wall primitives and mask -> wall rectangles (``walls``) -> gaps and openings on all walls (``openings``);
4. label blocks (``labels.merge_label_blocks``) -> plot and building (``topology.split_plot``; plot walls, exterior
   areas and their openings go to ``site``) -> the outer loop must close; when the drawn walls do not close
   (or are absent) but the rooms are drawn as labelled closed outlines, the walls are inferred along them
   (``outlines``: evidence method ``inferred``, status ``unverified``, Milestone 11) and the loop is checked again;
   else ``needs_review``;
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

Milestone 12 (docs/milestone12.md §4.1, track R): the never-asked unknown pieces that fit a type and the unknown
parts of re-read clusters are asked as extra questions (content keys ``sym_<level>_x<hash>``, appended after the
core's candidates, so the keys and hashes of earlier rounds do not move); a candidate still unknown after its
answers is re-read (``_reread_unknowns``) and replaced by its parts; a block name only the M12 words read types its
candidate after the answers (``_m12_named``); the symbols found are passed in ``ex.report["symbols"]`` to
``reading.read_furniture``.

Fix round after P6a (22 Oct 2026; pod P6a, real04, and real02's P4a answers replayed in this session). What: a
candidate still ``unknown`` after its answers whose whole part is a coat closet (``symbols.hanging_rail``) or a table
with chairs on a rug outline (``symbols.rug_outline``) is read as such (``symbols.split_table_chairs`` /
``table_chair_items``) before the re-read, which cuts the part by block instance and so took real02's hanger inserts
out of the closet. ``split_override_text`` counts the chairs from the split and names a rug split.

Fix round after P6b (23 Oct 2026; pod P6b, real03). What: a wall that ``openings`` read apart where a thinner wall
lines its gaps (real03's shear walls on the hall-living partition) carries a ``corrected_by_ai`` label with the wall
it was before (an attribute of the ``WallItem``, for the wall's dict in the building; the reason is in the wall's
evidence note too); ``_shift_wall`` moves that ``before`` into the building frame with the wall. ``gap_rule_notes``
lists in the page notes (the ingest report's Notes) every gap the fix round's openings rules decided (lined gaps, gaps
inside wall material, walls drawn across a gap on a wall layer, gaps without glass), in building metres, and every
wall marked ``corrected_by_ai`` with its reason. Review finding of the fix round after P6a (same round): the P6a
whole-part read is also reached by a candidate the passes typed as a table; it now keeps the passes' type as
``ai_overridden`` (a type_disagreement conflict in the report) when the drawing types the piece otherwise (a coat
closet both passes called a coffee table) and notes ``split_override_text``'s line, not "still unknown after its
answers" (said only of an ``unknown`` piece).

Milestone 13 final pass (23 Oct 2026; pod P6c, real02, verify:agent:0). What: ``_ask_and_apply`` records the keys of
its questions without a full pair of answers in ``report["unanswered"]`` (``reading.UNANSWERED_KEY``) in every mode,
also with ``--no-ai`` where ``pending`` stays []; ``reading.answered_keys`` subtracts them, so "asked and answered in
this round" needs real answers. Why: P6c's first ``pipeline_final`` ran with ``--answers --no-ai``; with ``pending``
[] and answers applied, every question of the page counted as answered, the code-typed questions round 1 had withdrawn
were kept and listed, the late pass answered them from the M11 seeds and the AI types won (the drawn 3-seat sofas
f_L-1b_041 / 042 built as kitchen islands, about 20 other pieces of P4a's code types). The pipeline's
``_write_questions`` later rewrites the same key with the same rule, less the withdrawn questions.
"""
from __future__ import annotations

import dataclasses
import math
import re
from pathlib import Path
from typing import Optional

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from wenart import building as B
from wenart import units as U
from wenart.ingest.generic import frame as FR
from wenart.ingest.generic import labels as LB
from wenart.ingest.generic import openings as O
from wenart.ingest.generic import outlines as OL
from wenart.ingest.generic import scale as SC
from wenart.ingest.generic import symbols as SY
from wenart.ingest.generic import topology as TP
from wenart.ingest.generic import walls as W
from wenart.ingest.generic.model import GenericPage, Stroke, TextRun
from wenart.ingest.generic.reading import UNANSWERED_KEY
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
    label = getattr(w, "corrected_by_ai", None) or {}
    for rec in [label] + list(label.get("also") or []):
        before = rec.get("before") if isinstance(rec, dict) else None
        if not before:
            continue
        if "start" in before and "end" in before:
            # Fix round after P6b (23 Oct 2026): the wall a lined gap split (``openings._mark_lined``) as it was before.
            before["start"], before["end"] = list(sh.p(before["start"])), list(sh.p(before["end"]))
        if "center" in before:
            # 12 Nov 2026 (round-2 review, F5 / G7): the gap a wall's face lines run through, as it was before
            before["center"] = list(sh.p(before["center"]))


GAP_RULE_TEXT = {"lined_gap": "lined by a thinner wall along one face: open, the thick pieces are walls of their own",
                 "inside_wall": "inside wall material of another piece: closed, no opening",
                 "wall_faces": "both faces drawn on across it on a wall layer: closed, the wall continues",
                 "no_glass": "without glass between the faces: no window (a run gap stays an unverified opening; "
                             "an end gap or a stretch of a continuous wall gets none)"}


def gap_rule_notes(gap_log: list[dict], walls: list[WallItem], origin: tuple[float, float]) -> list[str]:
    """Fix round after P6b (23 Oct 2026): one page note per openings rule of the fix round (``openings.GAP_RULES``,
    the gap log's ``rule``) with the gaps it decided (building metres: the gap log is in page metres, ``origin`` is
    the frame origin), and one per wall a lined gap split (``corrected_by_ai``, its reason). CLAUDE.md: nothing
    changes silently; the ingest report lists the page notes."""
    ox, oy = origin

    def pt(p) -> str:
        return f"({p[0] - ox:.2f}, {p[1] - oy:.2f})"

    by_rule: dict[str, list[str]] = {}
    for e in gap_log:
        if e.get("rule") and e.get("p0") and e.get("p1"):
            by_rule.setdefault(e["rule"], []).append(f"{pt(e['p0'])}-{pt(e['p1'])} {e['width']:.2f} m")
    notes = [f"{len(spans)} gap(s) {GAP_RULE_TEXT.get(rule, rule)} (fix round after P6b): " + "; ".join(spans)
             for rule, spans in by_rule.items()]
    for w in walls:
        label = getattr(w, "corrected_by_ai", None)
        if label:
            notes.append(f"wall ({w.start[0]:.2f}, {w.start[1]:.2f})-({w.end[0]:.2f}, {w.end[1]:.2f}) "
                         f"{w.thickness:.2f} m corrected_by_ai ({label.get('rule')}): {label.get('reason')}")
    return notes


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
        curved = stair.get("curved")                 # 6 Nov 2026: a curved stair's centre (stair_numbers)
        if curved and curved.get("centre") is not None:
            curved["centre"] = list(sh.p(curved["centre"]))
        # 13 Nov 2026 (review B3-FC03-DRAWN / B3-REG-03: the stair rule's reading kept as drawn_stair stayed in page
        # metres while the piece moved to the building frame): the kept drawn values move with the piece
        drawn = stair.get("drawn_stair")
        if isinstance(drawn, dict):
            for flight in drawn.get("flights") or []:
                for key in ("start", "end"):
                    if flight.get(key) is not None:
                        flight[key] = list(sh.p(flight[key]))
            dl = drawn.get("landing")
            if isinstance(dl, dict) and dl.get("polygon"):
                dl["polygon"] = sh.pts(dl["polygon"])
            fp = drawn.get("footprint")
            if isinstance(fp, dict) and fp.get("center") is not None:
                fp["center"] = list(sh.p(fp["center"]))


OUTDOOR_TWIN_REACH_M = 1.5      # 20 Nov 2026 (R09-1): an outdoor space's mirror this close to a closed mirror twin


def _outdoor_outlines(ex, where: str, site: dict, strokes: list, outline, walls: Optional[list] = None,
                      blocks: Optional[list] = None) -> None:
    """The outline of every labelled outdoor space without a closed face, closed from the drawn strokes around its
    label (page metres; ``wenart.levels.outdoor.read_outline``), as ``outline_inferred`` on its site area; never
    silent (a note per space). 3 Nov 2026 (real09, user: "are you showing the balkons here?"; the drafter named the
    balcony of one flat only): on a plan of two mirrored halves (``facade.mirror_axis`` of ``walls``) a read outdoor
    space with no label at its mirror gets a twin there, read from the strokes around the mirrored anchor the same
    way (its label the twin's, ``label_inferred``)."""
    import copy as _copy

    from wenart.levels import outdoor as OD

    areas = [a for a in site.get("areas") or [] if not a.get("polygon")
             and OD.space_kind(a.get("label_raw") or a.get("label")) is not None]
    if not areas:
        return
    lines = [{"id": st.id, "pts": [tuple(p) for p in st.pts], "layer": st.layer, "closed": st.closed}
             for st in strokes if st.pts and len(st.pts) >= 2]
    facade = outline if outline is not None and not outline.is_empty else None
    for a in areas:
        rec = OD.read_outline(a, lines, facade)
        ex.notes.append(f"{where}: outdoor space '{a.get('label')}': " + (
            rec["reason"] + (f"; {rec['steps']['reason']}" if rec.get("steps") else "") if rec is not None else
            "no drawn outline closes around the label (the level inference infers one)"))
    axis = _halves(ex, walls, blocks=blocks or (), by="outdoor outlines") if walls else None
    # 20 Nov 2026 (R09-1, C0008: real09's left balcony): on a plan whose halves held only at the mirror-label share,
    # the outdoor spaces beside a mirror twin closed by ``_glazed_facades`` get their twins too
    near_twins = None
    if axis is None and (ex.report.get("mirror_twins") or {}).get("faces"):
        mt = ex.report["mirror_twins"]
        axis = tuple(mt["axis"])
        near_twins = unary_union([Polygon(f) for f in mt["faces"]]).buffer(OUTDOOR_TWIN_REACH_M)
    if axis is None:
        return
    anchors = [tuple(a["anchor"]) for a in site.get("areas") or [] if a.get("anchor")]
    for a in list(areas):
        if not a.get("anchor"):
            continue
        x, y = a["anchor"]
        q = (2.0 * axis[1] - x, y) if axis[0] == "x" else (x, 2.0 * axis[1] - y)
        if any(math.dist(q, b) <= 1.5 for b in anchors):
            continue                                        # a label of its own stands there
        if near_twins is not None and not near_twins.contains(Point(q)):
            continue                                        # no mirror twin closed beside it
        twin = _copy.deepcopy(a)
        twin.pop("outline_inferred", None)
        twin["anchor"] = [round(q[0], 4), round(q[1], 4)]
        twin["id"] = f"{a.get('id') or 'sa'}_mirror"
        twin["label_raw"] = None
        twin["label_inferred"] = {"method": "mirror", "of": a.get("id"), "axis": [axis[0], round(axis[1], 4)]}
        twin["note"] = (f"the mirror twin of outdoor space {a.get('id')} across the plan's axis ({axis[0]} = "
                        f"{axis[1]:.2f}): the drawing names one of the two mirrored halves only")
        twin["label_raw"] = a.get("label_raw") or a.get("label")
        rec = OD.read_outline(twin, lines, facade) if a.get("outline_inferred") else None
        twin["label_raw"] = None
        if a.get("outline_inferred") and rec is None:
            continue                                        # its twin closed from the strokes, the mirror does not
        # 3 Nov 2026 (real10, user: "the building is missing some sections", "Don't forget the mirror rule"): a space
        # whose outline the level inference infers (none closes from the strokes) gets its twin too; the inference
        # builds both alike
        twin.setdefault("label", a.get("label") or a.get("label_raw"))
        site.setdefault("areas", []).append(twin)
        anchors.append(q)
        ex.notes.append(f"{where}: outdoor space '{a.get('label')}' mirrored for the other half (no label there): "
                        + (rec["reason"] if rec else "its outline inferred by the level inference like its twin's"))


def _shift_site(site: dict, sh: _Shift) -> None:
    from wenart.ingest.generic import voids as VD

    VD.shift(site.get("voids"), sh.p)
    for w in site.get("boundary_walls", []):
        w["start"], w["end"] = list(sh.p(w["start"])), list(sh.p(w["end"]))
    for a in site.get("areas", []):
        if a.get("polygon"):
            a["polygon"] = sh.pts(a["polygon"])
        if a.get("anchor"):
            a["anchor"] = list(sh.p(a["anchor"]))
        rec = a.get("outline_inferred")
        if isinstance(rec, dict) and rec.get("polygon"):
            rec["polygon"] = [[round(x, 4), round(y, 4)] for x, y in sh.pts(rec["polygon"])]
            steps = rec.get("steps")
            if isinstance(steps, dict) and steps.get("edge"):
                steps["edge"] = [[round(x, 4), round(y, 4)] for x, y in sh.pts(steps["edge"])]
    for d in site.get("decor", []):
        d["center"] = list(sh.p(d["center"]))
    for o in site.get("openings", []):
        o["center"] = list(sh.p(o["center"]))
    for r in site.get("ramp_outlines") or []:           # 12 Nov 2026 (A2-FC9): the drawn ramp symbols
        r["polygon"] = [[round(x, 4), round(y, 4)] for x, y in sh.pts(r["polygon"])]
        r["apex"] = [round(v, 4) for v in sh.p(r["apex"])]


# --------------------------------------------------------------------------
# Faces
# --------------------------------------------------------------------------

CAVITY_WIDTH_M = 0.24      # real10: an unlabelled face no 24 cm strip fits into is a cavity between two walls


def face_table(face_polys: list, blocks: list, walls: list, openings: list, stairs: list, texts: list = (),
               notes: Optional[list] = None) -> list[dict]:
    """One row per face (page metres): ``{"polygon", "names" (indoor blocks), "exterior" (only exterior blocks),
    "room_type", "label", "reason"}``; unlabelled faces are typed by ``topology.unlabelled_face_type``. real10
    (1 Nov 2026): an unlabelled face narrower than ``CAVITY_WIDTH_M`` everywhere (it vanishes when shrunk by half of
    it: the 3-4 cm slits between a masonry wall and the plaster wall drawn beside it, 0.01-0.1 m2) is no room. 24 Nov
    2026: an unlabelled face ``topology.unlabelled_face_type`` types ``VOID`` (a duct: under 0.5 m2, no opening reaches
    it, no word in it; ``texts``: ``[(text, (x, y))]`` in page metres, as the pipeline's room typing gets them) is no
    room either; each one goes to ``notes``."""
    rows = []
    for poly in face_polys:
        if poly.buffer(-CAVITY_WIDTH_M / 2.0, join_style=2).is_empty and \
                not any(poly.contains(Point(b.anchor)) for b in blocks):
            continue
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
            x0, y0, x1, y1 = poly.bounds
            near = [(t, q) for t, q in texts if x0 - 0.1 <= q[0] <= x1 + 0.1 and y0 - 0.1 <= q[1] <= y1 + 0.1]
            row["room_type"], row["reason"] = TP.unlabelled_face_type(poly, walls, openings, stairs, texts=near)
            row["label"] = None
            if row["room_type"] == TP.VOID:
                if notes is not None:     # 24 Nov 2026: a duct or shaft in the walls, never a room (never silent)
                    c = poly.representative_point()
                    notes.append(f"face at ({c.x:.2f}, {c.y:.2f}) is no room: {row['reason']}")
                continue
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
                   evidence_only: bool = False, base: Optional[list] = None) -> None:
    """Crops and questions for every candidate; the two-pass rule where answers exist (§3.3). Raster candidates are
    pixel crops of the rectified page (``raster.image``, context ``{image, to_px}``, §3.1); an evidence-only raster
    page asks nothing (§0).

    The question carries the item's facts (``recognition.symbols.question_facts``, prep pod finding P5): on vector
    pages also the room's printed label and type (``room_label``/``room_type``) and the neighbours among this page's
    candidates of the same face (``room_index``; ``symbols.neighbour_facts``). Raster questions carry neither: their
    names and clusters may change with the label answers of the same round, and the hash must not.

    Milestone 12 (track R): ``base`` (the core's own candidates) marks ``cands`` as the extra candidates of the
    re-read: each one's neighbours are counted among ``base`` and itself only (so they do not depend on what else a
    round re-reads), and the questions and pending keys are added to the report's."""
    append = base is not None
    if not cands:
        if not append:
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
    elif append:
        def facts(c):
            return {"key": c["key"], "footprint": c["footprint"], "room_index": c.get("room_index")}
        neighbours = {c["key"]: RS.neighbour_facts([facts(b) for b in base] + [facts(c)]).get(c["key"])
                      for c in cands}
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
    # Milestone 13 final pass (23 Oct 2026; module docstring): the keys without a full pair of answers, in every mode
    # (``pending`` is [] under --no-ai: nothing waits for them, but they were not answered).
    if append:
        ex.report["questions"] = list(ex.report.get("questions") or []) + items
        ex.report["pending"] = list(ex.report.get("pending") or []) + ([] if no_ai else pending)
        ex.report[UNANSWERED_KEY] = list(ex.report.get(UNANSWERED_KEY) or []) + pending
        ex.report["answers_applied"] = int(ex.report.get("answers_applied") or 0) + decided
    else:
        ex.report["questions"] = items
        ex.report["pending"] = [] if no_ai else pending
        ex.report[UNANSWERED_KEY] = list(pending)
        ex.report["answers_applied"] = decided
    if pending:
        ex.notes.append(f"{len(pending)} of {len(cands)} furniture candidates have no complete pair of answers"
                        + (" (--no-ai: they stay unknown, unverified)" if no_ai else ""))


def _room_fields(cand: dict, rows: list[dict]) -> None:
    pt = Point(cand["footprint"]["center"])
    index = next((k for k, r in enumerate(rows) if r["polygon"].contains(pt)), None)
    row = rows[index] if index is not None else None
    cand["room_type"] = row["room_type"] if row else None
    cand["room_label"] = row["label"] if row else None
    cand["room_index"] = index
    cand["_ids"] = _expand_ids(cand["item"].evidence.get("entity"))


def _m12_named(part, ctx, raster: bool, table: dict, wall_polys: list):
    """The piece a candidate's block name gives by the Milestone 12 words alone (``symbols.BLOCK_KEYWORDS_M12``), when
    its footprint fits that type; None otherwise (no name, or a name the earlier words already read)."""
    chain = SY._block_chain(part)
    if chain is None:
        return None
    names = list(reversed(chain.split("/")))
    fp = SY.footprint([p for s in part.segs for p in s.pts], ctx.theta)
    if SY.block_type(names, (fp[1], fp[2]), table, extended=False) is not None:
        return None
    item = SY._block_item(part, fp, ctx, raster, table, None, wall_polys, [])
    if item is None or not SY.fits(table, item.type, (fp[1], fp[2])):
        return None
    return item


def split_override_text(split: dict, key: str, ai_type: str, n_made: int) -> tuple[str, str]:
    """``(ai_overridden reason, extraction note)`` of a ``symbols.split_table_chairs`` split that outranks the AI
    passes' type. Integration of the fix round after P5: a coat closet (``split["wardrobe"]``: a hanging rail with
    hangers) is one wardrobe, not "a table with chairs drawn around it" (real04 f_L1_021..026). Fix round after P6a
    (22 Oct 2026): the chairs are counted from the split (a rug split also makes the rug mark,
    ``symbols.rug_mark_item``) and a rug split says so."""
    if split.get("wardrobe"):
        return ("a coat closet: hanging rail with hangers (vector geometry outranks the AI passes)",
                f"{key}: typed {ai_type} by the AI passes, but drawn as a coat closet (hanging rail with hangers): one "
                f"wardrobe (fix round after P5)")
    chairs = len(split["chairs"]) if split.get("chairs") is not None else n_made - 1
    if split.get("rug"):
        return ("a table with chairs drawn on a rug outline (vector geometry outranks the AI passes)",
                f"{key}: typed {ai_type} by the AI passes, but drawn as a table with {chairs} chairs on a rug outline: "
                f"split, the outline a rug mark (fix round after P6a)")
    return ("a table with chairs drawn around it (vector geometry outranks the AI passes)",
            f"{key}: typed {ai_type} by the AI passes, but drawn as a table with {chairs} chairs: split (M12)")


def _reread_unknowns(ex: LevelExtraction, cands: list[dict], extras: list[dict], symbols: list[dict], walls: list,
                     openings: list, texts_m: list, rows: list[dict], level_id: str, file_rel: str,
                     page_no: Optional[int], s: float, no_ai: bool, raster: bool,
                     strokes_m: Optional[list] = None) -> tuple[dict, list]:
    """Milestone 12 (docs/milestone12.md §4.1, track R): an AI candidate still ``unknown`` after its answers (the
    passes disagree or say unknown) is re-read (``symbols.reread``): its symbol strokes out, one part per block
    instance and stroke group, each typed on its own. Its question stays as it was (same key and hash: the answers of
    every round still apply); only the piece is replaced, when the re-read found more than the one unknown piece. A
    candidate without answers keeps its piece (only a block name the M12 words read types it, ``_m12_named``). Returns ``({candidate key: replacement items}, unknown pieces that fit no type)``; the replacement's unknown parts
    that fit a type are added to ``extras`` (asked under content keys), its symbols to ``symbols``."""
    pending = set(ex.report.get("pending") or [])
    # A round with answers for this page waits for none of its questions (one without answers was not in that round).
    waiting = not no_ai and not ex.report.get("answers_applied")
    table, _src = SY.load_size_table()
    ctx = SY._Ctx(file_rel, page_no, s, SY._dominant(walls), level_id)
    wall_polys = [TP.wall_polygon(w) for w in walls]
    known = {c["key"] for c in cands + extras}
    containers = None
    replaced: dict[str, list] = {}
    loose: list = []
    for cand in cands:
        item, part = cand["item"], cand.get("_part")
        if part is None or item.details.get("build") is False or item.details.get("symbol") or \
                item.details.get("not_furniture"):
            continue
        if waiting and (cand["key"] in pending or not item.type_candidates):
            continue                                # a round without answers: it waits for them
        named = _m12_named(part, ctx, raster, table, wall_polys)
        if named is not None:
            # A block name only the Milestone 12 words read (the candidate was asked before they existed): the name
            # outranks the AI passes; the question stays as it was.
            named.details["reread_of"] = cand["key"]
            if item.type not in ("unknown", named.type):
                named.details["ai_overridden"] = {"type": item.type, "type_candidates": list(item.type_candidates),
                                                  "reason": f"the block name says {named.type}"}
            replaced[cand["key"]] = [named]
            ex.notes.append(f"{cand['key']}: typed {named.type} by its block name {named.type_raw} (M12 words)")
            continue
        if item.type not in ("unknown",) + SY.TABLE_TYPES:
            # Context before AI (§4.1): chairs drawn around a rectangle are a dining set, whatever the passes said
            # (real03: two passes called the drawn 0.9 x 1.4 m table with its chairs a sofa).
            split = SY.split_table_chairs(part, table, ctx.theta)
            # 26 Oct 2026 (symbols module docstring): a seat drawn as its cushion with its arms and back is no table
            # with chairs; the AI passes' type stands (it is never overridden by "one seat").
            if split is not None and not split.get("seat"):
                made = SY.table_chair_items(split, ctx, raster, table)
                for it in made:
                    it.details["reread_of"] = cand["key"]
                reason, note = split_override_text(split, cand["key"], item.type, len(made))
                made[0].details["ai_overridden"] = {"type": item.type, "type_candidates": list(item.type_candidates),
                                                    "reason": reason}
                replaced[cand["key"]] = made
                ex.notes.append(note)
            continue
        if not item.type_candidates:
            # Not answered (``--no-ai``, or a question whose answers no longer apply): its question stays open and the
            # piece stays as asked (unknown), so twins drawn differently stay alike (real02's L1 corridors).
            continue
        whole = SY.split_table_chairs(part, table, ctx.theta)
        if whole is not None and (whole.get("wardrobe") or whole.get("rug")):
            # Fix round after P6a (22 Oct 2026): a group the drawing alone decides on the whole part (a coat closet:
            # its rail with hangers; a table with chairs on a rug outline) is read before the re-read, which cuts the
            # part by block instance: real02's first corridor closet (passes unknown / bench) lost its hanger inserts
            # to two not-built "details" and stayed a coffee table with two chairs, unlike its twin. The question
            # stays as it was (same key and hash).
            # Fix round after P6b (23 Oct 2026; review finding of the fix round after P6a): this branch is also reached
            # by a candidate the passes typed as a table (``SY.TABLE_TYPES``). Such a candidate is not "still
            # unknown": the drawing outranks a typed answer here as in the branch above (``split_override_text``'s
            # note), and the AI's type is kept as ``ai_overridden`` (``reading.log_overrides``: a type_disagreement
            # conflict in the report) whenever the drawing gives the piece another type (a coat closet the passes
            # called a coffee table). A rug-set table that keeps the passes' table type is no type disagreement (as
            # the M12 re-read of a table answer with its chairs never was), so it records none.
            made = SY.table_chair_items(whole, ctx, raster, table)
            for it in made:
                it.details["reread_of"] = cand["key"]
            replaced[cand["key"]] = made
            if item.type == "unknown":
                ex.notes.append(f"{cand['key']}: still unknown after its answers, but drawn as "
                                + (f"a coat closet ({whole['wardrobe']['note']}): one wardrobe"
                                   if whole.get("wardrobe")
                                   else f"a table with {len(whole['chairs'])} chairs on a rug outline: split, the "
                                        f"outline a rug mark") + " (fix round after P6a)")
                continue
            reason, note = split_override_text(whole, cand["key"], item.type, len(made))
            if made[0].type != item.type:
                made[0].details["ai_overridden"] = {"type": item.type, "type_candidates": list(item.type_candidates),
                                                    "reason": reason}
            ex.notes.append(note)
            continue
        if containers is None:
            containers = SY.containers_of(strokes_m or [])
        got = SY.reread(part, ctx, table, walls, openings, wall_polys, texts_m, ex.notes, raster,
                        why="AI candidate still unknown after its answers", containers=containers)
        typed = [it for it in got["items"] if it.type != "unknown"]
        if not (typed or got["symbols"] or len(got["items"]) > 1):
            continue
        out = []
        for it in got["items"]:
            it.details["reread_of"] = cand["key"]
            if it.type != "unknown" or it.details.get("not_furniture"):
                out.append(it)              # typed, or a column the reading step keeps as a not-built obstacle
                continue
            sub = SY.Cluster([sg for sid in SY.expand_ids(it.evidence.get("entity")) for sg in part.segs
                              if sg.stroke.id == sid])
            fp = SY.footprint([p for sg in sub.segs for p in sg.pts], ctx.theta) if sub.segs else None
            if fp is None or not SY.fitting_types(table, (fp[1], fp[2]), "L" if it.details.get("l_outline") else None):
                loose.append(it)
                continue
            extra = SY.extra_candidate(sub, fp, it, ctx, raster, [], wall_polys, table)
            if extra["key"] in known:
                continue
            known.add(extra["key"])
            _room_fields(extra, rows)
            extras.append(extra)
        symbols.extend(got["symbols"])
        replaced[cand["key"]] = out
        ex.notes.append(f"{cand['key']}: still unknown after its answers, re-read (M12): {len(got['items'])} pieces "
                        f"({len(typed)} typed), {len(got['symbols'])} symbols")
    return replaced, loose


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
# Walls inferred from labelled room outlines (Milestone 11)
# --------------------------------------------------------------------------

def _unclosed(warnings: list) -> int:
    """The labels a plan's walls leave in no closed face ('outer walls do not close' review reasons)."""
    return sum(1 for w in warnings if w.startswith(TP.REVIEW_PREFIX) and "outer walls do not close" in w)


def _face_lines(strokes_m: list) -> list:
    """19 Nov 2026 (review A4): ``[(a, b, layer)]``, the straight pieces (over 5 cm) of the strokes on a wall, plaster or
    structure layer (``layer_names``), page metres: the drawn wall faces a lift's shaft is read from."""
    from wenart.ingest.generic import layer_names as LN

    out = []
    for st in strokes_m:
        if st.arc is not None or len(st.pts) < 2 or LN.layer_role(st.layer) not in ("wall", "plaster", "structure"):
            continue
        pts = list(st.pts) + ([st.pts[0]] if st.closed else [])
        out += [(tuple(a), tuple(b), st.layer) for a, b in zip(pts, pts[1:]) if math.dist(a, b) > 0.05]
    return out


DETAIL_LINE_M = (0.05, 2.0)      # 19 Nov 2026 (review A4, SW-A4-02 / POD-A4-02): a drawn detail line this long ...
DETAIL_SKIP_ROLES = ("wall", "plaster", "structure", "dimension", "hatch")   # ... on a layer of none of these roles


def _detail_lines(strokes_m: list) -> list:
    """19 Nov 2026 (review A4, SW-A4-02 / POD-A4-02: real17's lift block draws its landing door's frame on 'ince' and
    real20's on DOT inside wall faces drawn through): ``[(a, b, layer)]``, the straight pieces ``DETAIL_LINE_M`` long of
    the strokes on no wall, plaster, structure, dimension or hatch layer, page metres: the frames and panels a lift's
    landing door is read from (``twins.lift_doors``)."""
    from wenart.ingest.generic import layer_names as LN

    out = []
    lo, hi = DETAIL_LINE_M
    for st in strokes_m:
        if st.arc is not None or st.fill is not None or len(st.pts) < 2 or LN.layer_role(st.layer) in DETAIL_SKIP_ROLES:
            continue
        pts = list(st.pts) + ([st.pts[0]] if st.closed else [])
        out += [(tuple(a), tuple(b), st.layer) for a, b in zip(pts, pts[1:]) if lo < math.dist(a, b) <= hi]
    return out


BRIDGE_PARALLEL_M = 0.60        # 19 Nov 2026 (review A3, OA3-05): a corner run-on bridge this close to a drawn wall ...
BRIDGE_PARALLEL_SHARE = 0.5     # ... along this share of its length runs beside that wall (a sliver room between)
BRIDGE_PIECE_ROLES = ("furniture", "sanitary")   # a bridge never runs through drawn furniture or sanitary ware ...
BRIDGE_PIECE_END_M = 0.30       # ... along its middle (this far from its jambs)


def _labels_in_faces(bwalls: list, b_openings: list, labels: list) -> int:
    """23 Nov 2026 (UL374): how many indoor room labels lie in a closed face of the building walls."""
    faces = TP.faces(bwalls, b_openings)
    return sum(1 for lb in labels if not getattr(lb, "exterior", False)
               and any(TP._label_in(f, lb) for f in faces))


def _labelled_both_sides(b: dict, t: float, faces: list, labels: list) -> bool:
    """23 Nov 2026 (UL374): the two faces a bridge stands between (probes ``t / 2 + 0.05`` m off its middle) are two
    faces and each holds a room label (indoor or outdoor): the drawing separates two rooms there."""
    (x0, y0), (x1, y1) = b["start"], b["end"]
    L = math.hypot(x1 - x0, y1 - y0)
    if L <= 1e-9:
        return False
    nx, ny = -(y1 - y0) / L, (x1 - x0) / L
    mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    found = []
    for s_ in (1.0, -1.0):
        q = Point(mx + s_ * nx * (t / 2.0 + 0.05), my + s_ * ny * (t / 2.0 + 0.05))
        f = next((k for k, fc in enumerate(faces) if fc.contains(q)), None)
        if f is None or not any(TP._label_in(faces[f], lb) for lb in labels):
            return False
        found.append(f)
    return found[0] != found[1]


def _sound_bridges(ex, where: str, walls2: list, cands: list, strokes: list, labels: Optional[list] = None) -> list:
    """19 Nov 2026 (review A3, OA3-05: real13's salons were cut along the column axis by wide-gap walls through the
    dining table and the sofa, 2.3 m inside their glazed facade, and a sliver room 0.34 m wide was left beside a drawn
    wall): a candidate bridge (``wide_gaps.bridges``) is dropped when its band crosses a line drawn on a furniture or
    sanitary layer (an outer wall never runs through a piece), or when it runs on from a corner (no free end) beside a
    drawn wall within ``BRIDGE_PARALLEL_M`` for ``BRIDGE_PARALLEL_SHARE`` of its length. Each drop is noted; the facade
    closure that follows may close the room on its frames."""
    from shapely.strtree import STRtree

    from wenart.ingest.generic import layer_names as LN

    if not cands:
        return cands
    pieces = []
    for st in strokes:
        if st.arc is None and len(st.pts) >= 2 and LN.layer_role(st.layer) in BRIDGE_PIECE_ROLES:
            pieces.append(LineString(st.pts))
    tree = STRtree(pieces) if pieces else None
    out, dropped = [], []
    faces = None
    for b in cands:
        w = walls2[b["wall"]]
        t = float(w.thickness)
        axis = LineString([b["start"], b["end"]])
        # (its middle: a piece standing against a jamb is no piece the bridge runs through; real15's facade units)
        L0_ = axis.length
        mid_axis = axis if L0_ <= 2 * BRIDGE_PIECE_END_M + 0.1 else LineString(
            [axis.interpolate(BRIDGE_PIECE_END_M), axis.interpolate(L0_ - BRIDGE_PIECE_END_M)])
        band = mid_axis.buffer(t / 2.0, cap_style=2).buffer(-0.02)
        if tree is not None and not band.is_empty and any(pieces[int(i)].intersects(band)
                                                         for i in tree.query(band, predicate="intersects")):
            dropped.append(f"{b['width']:.2f} m bridge from {b['start']}: it runs through drawn furniture")
            continue
        # 23 Nov 2026 (UL374, the dataset bench's long invented walls: bridges across open passages and open sides of
        # loggias): a wide gap with nothing drawn across it is open, not an opening whose kind the drawing leaves out;
        # it is marked here and ``_outer_gaps`` keeps it only where the rooms need it to close
        if b.get("rule") in (None, "wide_gap"):
            from wenart.ingest.generic import wide_gaps as WG
            drawn, why = WG.gap_drawn(b["start"], b["end"], t, strokes)
            if not drawn:
                if faces is None:                            # the faces with every candidate bridge, for the labels
                    faces = TP.faces(WG.apply(walls2, [], cands)[0])
                if _labelled_both_sides(b, t, faces, labels or []):
                    ex.notes.append(f"{where}: the {b['width']:.2f} m bridge from {b['start']} spans an empty gap "
                                    f"({why}) but stands between two labelled rooms: kept")
                else:
                    b = dict(b, empty_gap=why)
        if not b.get("from_free_end"):
            L = axis.length
            (x0, y0), (x1, y1) = axis.coords[0], axis.coords[-1]
            ux, uy = (x1 - x0) / max(L, 1e-9), (y1 - y0) / max(L, 1e-9)
            beside = False
            for k, o in enumerate(walls2):
                if k in (b["wall"], b.get("to")):
                    continue
                (a0, a1), (c0, c1) = tuple(o.start), tuple(o.end)
                lo_ = math.hypot(c0 - a0, c1 - a1)
                if lo_ <= 1e-9 or abs(((c0 - a0) * uy - (c1 - a1) * ux) / lo_) > 0.1:
                    continue                                    # not parallel
                off_ = abs(-(a0 - x0) * uy + (a1 - y0) * ux)
                if off_ > BRIDGE_PARALLEL_M + (t + float(o.thickness)) / 2.0 or off_ < (t + float(o.thickness)) / 2.0:
                    continue
                s0, s1 = sorted(((a0 - x0) * ux + (a1 - y0) * uy, (c0 - x0) * ux + (c1 - y0) * uy))
                if min(L, s1) - max(0.0, s0) >= BRIDGE_PARALLEL_SHARE * L:
                    beside = True
                    break
            if beside:
                dropped.append(f"{b['width']:.2f} m bridge from {b['start']}: it runs on from a corner beside a drawn "
                               f"wall within {BRIDGE_PARALLEL_M:.2f} m (a sliver between)")
                continue
        out.append(b)
    if dropped:
        ex.notes.append(f"{where}: wide-gap bridges left out: " + "; ".join(dropped[:8]))
    return out


def _outer_gaps(ex, where: str, walls2: list, openings: list, blocks: list, level_id, site_warnings: list,
                problem: Optional[str] = None, strokes: Optional[list] = None):
    """The wide gaps of the outer ring bridged (``wide_gaps``): the candidate bridges on the bridged building's
    outline are kept when the walls then close, or close in more labelled rooms; None when nothing improves."""
    from wenart.ingest.generic import wide_gaps as WG

    cands = WG.bridges(walls2)
    # 3 Nov 2026: the glazed runs (``joinery_bridges``) are left to the facade closure that follows (``facade``): its
    # walls follow the frames and carry the windows and doors drawn on them, where a run's bridge was a hole
    cands = _sound_bridges(ex, where, walls2, cands, strokes or [], labels=blocks)
    if not cands:
        return None
    w3, o3 = WG.apply(walls2, openings, cands)
    bw3, site3, _ = TP.split_plot(w3, o3, blocks, level_id=level_id)
    idx3 = {o["index"] for o in site3["openings"]}
    outline3 = TP.building_outline(bw3, [o for k, o in enumerate(o3) if k not in idx3])
    kept = [b for b in cands if WG.on_outline(b, outline3)]
    if not kept:
        return None
    w4, o4 = WG.apply(walls2, openings, kept)
    bw4, site4, sw4 = TP.split_plot(w4, o4, blocks, level_id=level_id)
    idx4 = {o["index"] for o in site4["openings"]}
    b_open4 = [o for k, o in enumerate(o4) if k not in idx4]
    problem4 = TP.outer_loop_problem(bw4, b_open4)
    before, after = _unclosed(site_warnings), _unclosed(sw4)
    if not (after < before or (problem is not None and problem4 is None and after <= before)):
        return None                                        # nothing closes: the drawn walls stay as they are
    # 23 Nov 2026 (UL374): a bridge over an empty gap stays only where the rooms need it to close (the longest tried
    # first); the others are open passages and open sides (no wall, no opening)
    held4 = _labels_in_faces(bw4, b_open4, blocks) if any(b.get("empty_gap") for b in kept) else 0
    for b in sorted([b for b in kept if b.get("empty_gap")], key=lambda b: (-b["width"], b["start"])):
        trial = [x for x in kept if x is not b]
        if not trial:
            break
        w5, o5 = WG.apply(walls2, openings, trial)
        bw5, site5, sw5 = TP.split_plot(w5, o5, blocks, level_id=level_id)
        idx5 = {o["index"] for o in site5["openings"]}
        b_open5 = [o for k, o in enumerate(o5) if k not in idx5]
        problem5 = TP.outer_loop_problem(bw5, b_open5)
        held5 = _labels_in_faces(bw5, b_open5, blocks)
        # (and no drawn wall leaves the building with it: swiss-b2294, a wing of thin walls the closure holds in)
        if _unclosed(sw5) <= after and held5 >= held4 and len(bw5) >= len(bw4) - 1 and \
                (problem5 is None or problem4 is not None):
            held4 = held5
            ex.notes.append(f"{where}: the {b['width']:.2f} m bridge from {b['start']} left out: an empty gap "
                            f"({b['empty_gap']}) the rooms close without, an open passage")
            kept = trial
            w4, o4, bw4, site4, sw4, b_open4, problem4 = w5, o5, bw5, site5, sw5, b_open5, problem5
            after = _unclosed(sw5)
    ex.notes.append(f"{where}: {len(kept)} wide gap(s) in the outer walls bridged by inferred walls with unverified "
                    f"openings (rule wide_gap: a sliding door, a garage door or an entrance the drawing gives no "
                    f"symbol the openings reader knows; rule glazed_run: a glazed run on a window, door or glass "
                    f"layer between two walls): "
                    + ", ".join(f"{b['width']:.2f} m ({b.get('rule') or 'wide_gap'})" for b in kept)
                    + f"; labels in no closed face {before} -> {after}")
    return w4, o4, bw4, site4, sw4, b_open4, problem4


JOIN_MAX_M = 0.40               # 4 Nov 2026: a free wall end this close to a wall on its own line joins it ...
JOIN_MIN_M = 0.02               # ... (closer is the slit the wall union closes anyway)
JOIN_TOUCH_M = 0.05             # an end with another wall this close is no free end
CORNER_MAX_M = 0.60             # two free ends whose lines cross this close ahead of both meet in that corner
CORNER_MIN_SIN = 0.5            # ... when the two walls turn by at least 30 degrees
JOIN_OPENING_CLEAR_M = 0.30     # no join runs through or beside a drawn door or window
JOINT_MAX_M = 0.15              # a crack or slit this narrow between two drawn walls, at the end of one, is filled ...
JOINT_MAX_M2 = 0.10             # ... when the fill is this small (no cavity between two parallel walls)


def _free_ends(walls2: list, polys: list) -> list:
    """(wall index, "start"/"end", end point, outward unit direction, half thickness) of every wall end that touches
    no other wall."""
    ends = []
    for k, w in enumerate(walls2):
        (x0, y0), (x1, y1) = tuple(w.start), tuple(w.end)
        L = math.hypot(x1 - x0, y1 - y0)
        if L <= 0:
            continue
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        nx, ny = -uy, ux
        h = float(w.thickness) / 2.0
        for which, (px, py), (dx, dy) in (("start", (x0, y0), (-ux, -uy)), ("end", (x1, y1), (ux, uy))):
            face = LineString([(px + nx * h, py + ny * h), (px - nx * h, py - ny * h)])
            if not any(j != k and polys[j].distance(face) <= JOIN_TOUCH_M for j in range(len(polys))):
                ends.append((k, which, (px, py), (dx, dy), h))
    return ends


def _join_clear(p, q, openings: list) -> bool:
    """True when no drawn door or window lies on or beside the stretch from ``p`` to ``q``."""
    seg = LineString([p, q])
    return not any(seg.distance(Point(tuple(o.center))) <= JOIN_OPENING_CLEAR_M + float(o.width) / 2.0
                   for o in openings if not getattr(o, "virtual", False))


def _joints(walls: list, openings: list) -> list:
    """Fill walls (``WallItem``) for the cracks and slits of at most ``JOINT_MAX_M`` between two drawn walls next to
    the end of one of them (real17 L0: a stair wall's corner 9 mm off the facade wall's corner; a 12 cm slit between a
    wall end and its column), each the smallest rectangle over the closed gap; none over a door or window."""
    from shapely.strtree import STRtree

    from wenart.ingest.model import WallItem

    polys = [TP.wall_polygon(w) for w in walls]
    opolys = [q for q in (TP.opening_polygon(o, walls) for o in openings) if q is not None]
    tree = STRtree(polys)
    r = JOINT_MAX_M / 2.0 + 0.01
    out = []
    for i, pi in enumerate(polys):
        for j in sorted(int(x) for x in tree.query(pi.buffer(JOINT_MAX_M))):
            if j <= i or not 1e-6 < pi.distance(polys[j]) <= JOINT_MAX_M:
                continue
            pair = unary_union([pi, polys[j]])
            fill = pair.buffer(r).buffer(-r).difference(pair)          # round: diagonal cracks too
            ends = [(Point(tuple(walls[k].start)), Point(tuple(walls[k].end)), float(walls[k].thickness) / 2.0)
                    for k in (i, j)]
            for g in getattr(fill, "geoms", [fill]):
                if g.area <= 1e-6 or g.area > JOINT_MAX_M2 or g.distance(pi) > 1e-3 or g.distance(polys[j]) > 1e-3:
                    continue
                if not any(g.distance(e) <= h + JOINT_MAX_M for a, b, h in ends for e in (a, b)):
                    continue
                rect = g.minimum_rotated_rectangle
                if any(rect.intersects(q) for q in opolys):
                    continue
                cs = list(rect.exterior.coords)[:4]
                e1, e2 = math.dist(cs[0], cs[1]), math.dist(cs[1], cs[2])
                if e1 >= e2:
                    a, b, t = ((cs[1][0] + cs[2][0]) / 2, (cs[1][1] + cs[2][1]) / 2), \
                        ((cs[0][0] + cs[3][0]) / 2, (cs[0][1] + cs[3][1]) / 2), e2
                else:
                    a, b, t = ((cs[0][0] + cs[1][0]) / 2, (cs[0][1] + cs[1][1]) / 2), \
                        ((cs[2][0] + cs[3][0]) / 2, (cs[2][1] + cs[3][1]) / 2), e1
                if math.dist(a, b) < 0.01:
                    continue
                w = walls[i]
                ev = dict(w.evidence or {})
                ev.update(method="inferred", confidence=0.8, rule="joint",
                          reason=f"a {pi.distance(polys[j]):.3f} m crack between the drawn walls {w.entity} and "
                                 f"{walls[j].entity}, at the end of one of them, left the room open: filled")
                out.append(WallItem(start=(round(a[0], 4), round(a[1], 4)), end=(round(b[0], 4), round(b[1], 4)),
                                    thickness=round(max(t, 0.02) + 0.01, 3), box=list(w.box),
                                    entity=f"joint:{w.entity.split(',')[0]}+{walls[j].entity.split(',')[0]}",
                                    evidence=ev, exterior=bool(w.exterior), status="unverified", inferred=True))
    return out


def _short_joins(ex, where: str, walls2: list, openings: list, blocks: list, level_id, site_warnings: list,
                 problem: Optional[str] = None):
    """4 Nov 2026 (real17 L0, user: "Those walls already drawed, all open ones needs to be walls these sections could
    be full windows glass"; then "There are no walls here why are you imagining these?"): drawn walls stopping a few
    cm short of the wall or column they belong to left the outer ring open. Only drawn walls are lengthened, no wall
    is added where the drawing has none:
    - a free wall end whose own band (its thickness, along its axis) meets another wall within ``JOIN_MAX_M`` is
      extended onto it;
    - two free ends whose lines cross within ``CORNER_MAX_M`` ahead of both (a corner, often with its drawn column)
      are both extended to the corner.
    No join runs past a drawn door or window. Kept when the walls then close, or close in more labelled rooms; never
    silent."""
    polys = [TP.wall_polygon(w) for w in walls2]
    ends = _free_ends(walls2, polys)
    ext: dict = {}                                                  # (k, which) -> (new point, length added)
    for k, which, (px, py), (dx, dy), h in ends:
        nx, ny = -dy, dx
        band = Polygon([(px + nx * h, py + ny * h), (px - nx * h, py - ny * h),
                        (px - nx * h + dx * JOIN_MAX_M, py - ny * h + dy * JOIN_MAX_M),
                        (px + nx * h + dx * JOIN_MAX_M, py + ny * h + dy * JOIN_MAX_M)])
        best = None
        for j, g in enumerate(polys):
            if j == k or not g.intersects(band):
                continue
            part = g.intersection(band)
            if part.area <= 1e-5:
                continue
            d = min(((qx - px) * dx + (qy - py) * dy) for qx, qy in
                    (c for gg in getattr(part, "geoms", [part]) if hasattr(gg, "exterior") for c in gg.exterior.coords))
            if JOIN_MIN_M <= d <= JOIN_MAX_M and (best is None or d < best):
                best = d
        if best is None:
            continue
        q = (round(px + dx * (best + 0.01), 4), round(py + dy * (best + 0.01), 4))
        if _join_clear((px, py), q, openings):
            ext[(k, which)] = (q, best)
    corners = []
    for i, (ka, wa, pa, da, ha) in enumerate(ends):
        for kb, wb, pb, db, hb in ends[i + 1:]:
            if ka == kb or (ka, wa) in ext or (kb, wb) in ext:
                continue
            cross = da[0] * db[1] - da[1] * db[0]
            if abs(cross) < CORNER_MIN_SIN:
                continue
            rx, ry = pb[0] - pa[0], pb[1] - pa[1]
            ta = (rx * db[1] - ry * db[0]) / cross                # pa + ta * da == pb + tb * db
            tb = (rx * da[1] - ry * da[0]) / cross
            if not (-JOIN_TOUCH_M <= ta <= CORNER_MAX_M and -JOIN_TOUCH_M <= tb <= CORNER_MAX_M) \
                    or max(ta, tb) < JOIN_MIN_M:
                continue
            corners.append((ta + tb, ka, wa, pa, da, ta + hb, kb, wb, pb, db, tb + ha))
    used: set = set()
    for _, ka, wa, pa, da, la, kb, wb, pb, db, lb in sorted(corners):
        if (ka, wa) in used or (kb, wb) in used:
            continue
        qa = (round(pa[0] + da[0] * la, 4), round(pa[1] + da[1] * la, 4))
        qb = (round(pb[0] + db[0] * lb, 4), round(pb[1] + db[1] * lb, 4))
        if not (_join_clear(pa, qa, openings) and _join_clear(pb, qb, openings)):
            continue
        used |= {(ka, wa), (kb, wb)}
        if la > 0:
            ext[(ka, wa)] = (qa, la)
        if lb > 0:
            ext[(kb, wb)] = (qb, lb)
    new = list(walls2)
    for (k, which), (q, _) in ext.items():
        new[k] = dataclasses.replace(new[k], **{which: q})
    joints = _joints(new, openings)
    if not ext and not joints:
        return None

    def check(ws):
        bw, site, sw = TP.split_plot(ws, openings, blocks, level_id=level_id)
        idx = {o["index"] for o in site["openings"]}
        b_open = [o for j, o in enumerate(openings) if j not in idx]
        return bw, site, sw, b_open, TP.outer_loop_problem(bw, b_open)

    before = _unclosed(site_warnings)
    bw, site, sw, b_open, prob = check(new + joints)
    after = _unclosed(sw)
    if not (after < before or (problem is not None and prob is None and after <= before)):
        return None
    for jt in list(joints):                                   # only the joints the closing needs stay
        rest = [x for x in joints if x is not jt]
        r2 = check(new + rest)
        if _unclosed(r2[2]) <= after and (r2[4] is None or prob is not None):
            joints = rest
            bw, site, sw, b_open, prob = r2
    moved = sorted(ext.items())
    ex.notes.append(f"{where}: {len(moved)} wall end(s) stopping just short of a wall, a column or a shared corner "
                    f"joined to it (" + ", ".join(f"{walls2[k].entity} {which} +{d:.2f} m"
                                                  for (k, which), (_, d) in moved[:8])
                    + f"), {len(joints)} crack(s) up to {JOINT_MAX_M:.2f} m between drawn walls filled ("
                    + ", ".join(j.entity for j in joints[:6]) + f"); labels in no closed face {before} -> {_unclosed(sw)}")
    return new + joints, openings, bw, site, sw, b_open, prob


# --------------------------------------------------------------------------
# The outline closure: the last closure pass (Milestone 14 R2, 4 Nov 2026)
# --------------------------------------------------------------------------

OUTLINE_CLOSURE_RULE = "outline_closure"   # the evidence rule (``reading_check.CLOSURE_RULE`` is the same word)
CLOSURE_CONFIDENCE = 0.3        # every wall this pass infers carries this: a guess along the outline, to be checked
CLOSURE_MAX_M = 8.0             # a gap of the outer ring is bridged up to this long (a wide shopfront)
CLOSURE_ROUNDS = 3              # free ends are bridged again after a round closed some (a chain of gaps)
CLOSURE_GROW_M = 0.75           # the drawn outline: strokes >= CLOSURE_STROKE_MIN_M grown by this, merged, holes ...
CLOSURE_STROKE_MIN_M = 0.5      # ... filled, shrunk back (sheets.register.outline: GROW_M, SEGMENT_MIN_M)
CLOSURE_OUTLINE_TOL_M = 0.75    # a bridge lies inside the drawn outline grown by this: never past what is drawn
CLOSURE_OUTDOOR_CLEAR_M = 0.5   # no bridge this close to a balcony or terrace label, none enclosing one
CLOSURE_END_TOL_M = 0.3         # a free end is on the outer ring when this close to the building outline's boundary
CLOSURE_OUTLINE_ROLES = ("dimension", "axis", "text", "section", "hatch", "site")   # strokes no outline is made of
CLOSURE_MIN_SEGMENT_M = 0.05
CLOSURE_SUPPORT_MIN = 0.5       # a bridge from a corner end needs drawn lines along this share of it ...
CLOSURE_SUPPORT_TOL_M = 0.15    # ... within half its thickness plus this (a frame line on the wall face)
CLOSURE_SUPPORT_LINE_M = 0.15   # ... each line at least this long (no hinge ticks)
CLOSURE_UNLABELLED_MAX_M2 = 6.0 # a corner bridge closing an unlabelled space over this is refused
CLOSURE_ON_OUTLINE_M = 2.0      # a corner bridge runs along the drawn outline: its mean distance to the boundary at most
CLOSURE_OUTDOOR_AREA_TOL = 0.10 # a closed face within this share of an outdoor space's area text (10.00 m2) is that space
# 5 Nov 2026 (review of real18 L0): a wall part smaller than this is a fragment (listed, never bridged); a bridge
# parallel to an accepted one within this many thicknesses over this share is a double line, not a second wall;
# the layers whose lines never support a corner bridge (the building's own layers and unnamed layers do)
CLOSURE_FRAGMENT_LEN_M = 0.5
CLOSURE_FRAGMENT_M2 = 0.1
CLOSURE_PARALLEL_T = 2.0
CLOSURE_PARALLEL_SHARE = 0.5
CLOSURE_NO_SUPPORT_ROLES = ("furniture", "dimension", "hatch", "section", "site", "text", "stair", "finish",
                            "sanitary", "axis")


def outdoor_guard(blocks: list, walls: list, axis="halves") -> dict:
    """What no inferred wall may close into a room (5 Nov 2026, real11 L0: the glazed-facade pass closed the left
    kitchen along its balcony's railing and the balcony became kitchen floor; the right half, closed by the outline
    closure along the facade, kept its balcony): ``points`` = the anchors of the balcony, terrace, porch ... labels
    (``topology._outdoor_label``) and, when the plan has two mirrored halves (``facade.mirror_axis``), their mirror
    images (the drafter names one half only; a balcony on one half protects its twin on the other);
    ``areas`` = the area texts of those labels in m2 (``10.00 m2``); ``axis`` = the mirror axis or None (the level's
    decision ``_halves`` passed by the caller; by default ``mirror.halves_axis`` of ``walls`` and ``blocks``)."""
    from wenart.ingest.generic import mirror as MR

    outdoor = [b for b in blocks if TP._outdoor_label(b)]
    points = [(Point(b.anchor), False, b.name) for b in outdoor]
    if axis == "halves":
        axis = MR.halves_axis(walls, labels=blocks)[0] if walls else None
    if axis is not None:
        for b in outdoor:
            x, y = b.anchor
            q = (2.0 * axis[1] - x, y) if axis[0] == "x" else (x, 2.0 * axis[1] - y)
            points.append((Point(q), True, b.name))
    areas = [(float(b.area_m2), b.name) for b in outdoor if getattr(b, "area_m2", None)]
    indoor = [Point(b.anchor) for b in blocks if not getattr(b, "exterior", False) and not TP._outdoor_label(b)]
    return {"points": points, "areas": areas, "axis": axis, "indoor": indoor}


def outdoor_enclosure(face, guard: dict) -> Optional[str]:
    """Why a face an inferred wall would close is no room, or None: it holds an outdoor-space label, or the mirror
    image of one on the plan's twin half, or (a face with no room label in it) its area is within
    ``CLOSURE_OUTDOOR_AREA_TOL`` of an outdoor space's area text on the level (the balcony's ``10.00 m2`` ringed by
    its railing). A face holding a room label is that room whatever its area (real11 L5: the 10.98 m2 kitchen is no
    10.00 m2 balcony)."""
    for pt, mirrored, name in guard["points"]:
        if face.contains(pt):
            return (f"it would close the mirror image of the '{name}' label (the plan's twin half names the balcony "
                    f"or terrace there) into a room" if mirrored else
                    f"it would close the '{name}' label (a balcony, terrace or porch) into a room")
    if any(face.contains(q) for q in guard.get("indoor") or []):
        return None
    for a, name in guard["areas"]:
        if abs(face.area - a) <= CLOSURE_OUTDOOR_AREA_TOL * a:
            return (f"it would close an area of {face.area:.2f} m2 into the building, within "
                    f"{CLOSURE_OUTDOOR_AREA_TOL:.0%} of the '{name}' label's area text {a:.2f} m2 (that outdoor space)")
    return None


def drawn_outline(strokes_m: list, walls: list, exclude: set = frozenset()):
    """The plan's drawn outline (page metres), as ``sheets.register.outline`` finds a region's: the wall rectangles
    and every drawn line of at least ``CLOSURE_STROKE_MIN_M`` (no dimension, axis, text, section, hatch or site layer,
    no arc, none of ``exclude``: the dimension strokes) grown by ``CLOSURE_GROW_M`` (square ends, mitred), merged, the
    largest part's holes filled, shrunk back. None when nothing is drawn."""
    from wenart.ingest.generic import layer_names as LN

    geoms = [TP.wall_polygon(w) for w in walls]
    for st in strokes_m:
        pts = [tuple(p) for p in (getattr(st, "pts", None) or [])]
        if len(pts) < 2 or st.id in exclude or getattr(st, "arc", None) \
                or LN.layer_role(getattr(st, "layer", None)) in CLOSURE_OUTLINE_ROLES:
            continue
        line = LineString(pts + ([pts[0]] if getattr(st, "closed", False) else []))
        if line.length >= CLOSURE_STROKE_MIN_M:
            geoms.append(line)
    if not geoms:
        return None
    grown = unary_union([g.buffer(CLOSURE_GROW_M, cap_style=3, join_style=2) for g in geoms])
    parts = [p for p in getattr(grown, "geoms", [grown]) if not p.is_empty]
    if not parts:
        return None
    best = max(parts, key=lambda p: p.area)
    filled = Polygon(best.exterior).buffer(-CLOSURE_GROW_M, join_style=2)
    parts = [p for p in getattr(filled, "geoms", [filled]) if not p.is_empty]
    return max(parts, key=lambda p: p.area) if parts else None


def _outer_thickness(bwalls: list, b_openings: list) -> tuple[float, str]:
    """The median thickness of the walls on the building outline (the outer walls), else of every building wall,
    else the outer default (``outlines.OUTER_DEFAULT_M``); with how it was found."""
    import statistics

    outline = TP.building_outline(bwalls, b_openings)
    outer = [w for w in bwalls if not outline.is_empty and TP.wall_polygon(w).distance(outline.boundary) <= 0.05]
    if outer:
        return round(statistics.median(float(w.thickness) for w in outer), 3), f"median of {len(outer)} outer wall(s)"
    if bwalls:
        return round(statistics.median(float(w.thickness) for w in bwalls), 3), f"median of {len(bwalls)} wall(s)"
    return OL.OUTER_DEFAULT_M, "the outer default (no wall read)"


def _same_split_wall(wa, wb, da, pa, pb) -> bool:
    """Two facing free ends of one wall split in two (``_open_recesses``, ``_open_recess_chains`` keep the entity):
    a gap the reading opened on purpose, never closed again."""
    if wa.entity != wb.entity:
        return False
    (x0, y0), (x1, y1) = tuple(wb.start), tuple(wb.end)
    L = math.hypot(x1 - x0, y1 - y0)
    if L <= 1e-9:
        return False
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    return abs(ux * da[1] - uy * da[0]) < 0.09 and abs((pb[0] - pa[0]) * da[1] - (pb[1] - pa[1]) * da[0]) <= 0.1


def wall_fragments(walls2: list, bwalls: list, b_openings: list) -> tuple[set, list]:
    """The building-wall parts smaller than a real wall (5 Nov 2026, review of real18 L0: a detached 0.26 m piece of
    a line read as a wall forced a 6.45 m bridge parallel to the real one): a part of the bridged union shorter than
    ``CLOSURE_FRAGMENT_LEN_M`` or under ``CLOSURE_FRAGMENT_M2``. Returns the ``id``s of the walls in such parts (never
    a ring end, never a bridge's target, never a part the ring must reach) and one line per fragment for the report."""
    building = [w for w in bwalls]
    if not building:
        return set(), []
    parts = TP._parts(TP.bridged_union(building, b_openings))
    polys = [TP.wall_polygon(w) for w in building]
    ids: set = set()
    lines = []
    for part in parts:
        rect = part.minimum_rotated_rectangle
        cs = list(getattr(rect, "exterior", rect).coords)[:4] if hasattr(rect, "exterior") else []
        longest = max((math.dist(cs[i], cs[(i + 1) % 4]) for i in range(len(cs))), default=0.0)
        if part.area >= CLOSURE_FRAGMENT_M2 and longest >= CLOSURE_FRAGMENT_LEN_M:
            continue
        members = [w for w, g in zip(building, polys) if g.intersects(part) and g.intersection(part).area > 1e-6]
        if not members:
            continue
        ids.update(id(w) for w in members)
        lines.append(f"{', '.join(w.entity.split(',')[0] for w in members[:3])}: {longest:.2f} m, "
                     f"{part.area:.3f} m2 at ({part.centroid.x:.2f}, {part.centroid.y:.2f})")
    return ids, lines


def _runs_on(w, d, p) -> bool:
    """A wall running straight on past point ``p`` in direction ``d`` (parallel within about 5 degrees, reaching ahead
    of ``p``): the end at ``p`` is a joint inside one wall run, not a corner."""
    (x0, y0), (x1, y1) = tuple(w.start), tuple(w.end)
    L = math.hypot(x1 - x0, y1 - y0)
    if L <= 1e-9 or abs((x1 - x0) / L * d[1] - (y1 - y0) / L * d[0]) >= 0.09:
        return False
    return max((q[0] - p[0]) * d[0] + (q[1] - p[1]) * d[1] for q in ((x0, y0), (x1, y1))) > JOIN_TOUCH_M


def ring_ends(walls2: list, bwalls: list, b_openings: list, fragments: Optional[set] = None) -> list:
    """Every end of a building wall on the outer ring (within ``CLOSURE_END_TOL_M`` of ``topology.building_outline``'s
    boundary): ``(wall index, "start"/"end", point, outward unit direction, half thickness, free)``. ``free`` when no
    other wall touches the end (``JOIN_TOUCH_M``); else a *corner end*: the walls it touches turn away from it, none
    runs straight on past it (``_runs_on``: that end would be a joint inside one wall run). A corner end matters where
    a facade is drawn without walls (real11: the kitchen's glazed front runs from the shaft wall's corner to the
    salon wall's corner): the wall may run on past the corner along what is drawn. The walls of ``fragments``
    (``wall_fragments``) have no ring end."""
    polys = [TP.wall_polygon(w) for w in walls2]
    building = {id(w) for w in bwalls} - set(fragments or ())
    outline = TP.building_outline([w for w in bwalls if id(w) in building], b_openings)
    if outline.is_empty:
        return []
    ring = outline.boundary
    out = []
    for k, w in enumerate(walls2):
        if id(w) not in building:
            continue
        (x0, y0), (x1, y1) = tuple(w.start), tuple(w.end)
        L = math.hypot(x1 - x0, y1 - y0)
        if L <= 0:
            continue
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        nx, ny = -uy, ux
        h = float(w.thickness) / 2.0
        for which, (px, py), (dx, dy) in (("start", (x0, y0), (-ux, -uy)), ("end", (x1, y1), (ux, uy))):
            if ring.distance(Point(px, py)) > CLOSURE_END_TOL_M:
                continue
            face = LineString([(px + nx * h, py + ny * h), (px - nx * h, py - ny * h)])
            touching = [j for j in range(len(polys)) if j != k and polys[j].distance(face) <= JOIN_TOUCH_M]
            if any(_runs_on(walls2[j], (dx, dy), (px, py)) for j in touching):
                continue
            out.append((k, which, (px, py), (dx, dy), h, not touching))
    return out


def _stroke_lines(strokes: list) -> tuple[list, list]:
    """The drawn lines a bridge may run along (no arcs, at least ``CLOSURE_SUPPORT_LINE_M`` long) and, for each,
    whether it is a wall line. 5 Nov 2026 (review): only the lines of the building's own layers count - wall, plaster,
    column, window, door and glass (``layer_names``) - and lines of layers the reader does not know (a PDF has no
    layers, real11's kitchen fronts sit on an unnamed layer); never furniture, dimension, hatch, section, site, text,
    stair, finish, sanitary or axis layers, nor a balcony or terrace layer (``outdoor.SPACE_LAYER_RE``)."""
    from wenart.ingest.generic import layer_names as LN
    from wenart.levels import outdoor as OD

    out, wall_flags = [], []
    for st in strokes or ():
        pts = [tuple(p) for p in (getattr(st, "pts", None) or [])]
        if len(pts) < 2 or getattr(st, "arc", None):
            continue
        layer = getattr(st, "layer", None)
        role = LN.layer_role(layer)
        if role in CLOSURE_NO_SUPPORT_ROLES or (role is None and layer and OD.SPACE_LAYER_RE.search(
                B.fold_ascii(str(layer)).upper())):
            continue
        line = LineString(pts)
        if line.length >= CLOSURE_SUPPORT_LINE_M:
            out.append(line)
            wall_flags.append(role in ("wall", "plaster", "structure"))
    return out, wall_flags


def support_share(seg, lines: list, tree, tol: float) -> float:
    """The share of a bridge's length (``seg`` = (a, b)) that drawn ``lines`` run along: pieces within ``tol`` of
    it, parallel within about 10 degrees, their spans on the bridge merged (pure)."""
    a, b = seg
    L = math.dist(a, b)
    if L <= 1e-9 or not lines:
        return 0.0
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    axis = LineString([a, b])
    spans = []
    for i in tree.query(axis.buffer(tol, cap_style=2)):
        c = list(lines[int(i)].coords)
        for p, q in zip(c, c[1:]):
            vl = math.dist(p, q)
            if vl < 1e-9 or abs((q[0] - p[0]) / vl * uy - (q[1] - p[1]) / vl * ux) > 0.17:
                continue
            if LineString([p, q]).distance(axis) > tol:
                continue
            s0, s1 = sorted(((p[0] - a[0]) * ux + (p[1] - a[1]) * uy, (q[0] - a[0]) * ux + (q[1] - a[1]) * uy))
            s0, s1 = max(0.0, s0), min(L, s1)
            if s1 > s0:
                spans.append((s0, s1))
    covered, cur = 0.0, None
    for s0, s1 in sorted(spans):
        if cur is None or s0 > cur[1]:
            covered += (cur[1] - cur[0]) if cur else 0.0
            cur = [s0, s1]
        else:
            cur[1] = max(cur[1], s1)
    covered += (cur[1] - cur[0]) if cur else 0.0
    return min(1.0, covered / L)


def closure_candidates(walls2: list, bwalls: list, b_openings: list, strokes: list = (), thickness: float = 0.25,
                       ends: Optional[list] = None, outline=None, fragments: Optional[set] = None) -> list[dict]:
    """The bridges the outer ring's ends suggest (pure; page metres), from every wall end on the building outline
    (``ring_ends``: free ends, and corner ends where the wall may run on past the corner):

    - *straight*: the wall run on along its own axis, in a band of its thickness, to the **first** building wall the
      band meets beyond ``JOIN_TOUCH_M`` (the end of the wall across the gap, or the side of a wall). A wall met within
      ``JOIN_MAX_M`` is ``_short_joins``' case: the candidate is marked ``short`` and the caller refuses it, never
      bridging through that wall to the next one (5 Nov 2026, review);
    - *corner*: two ends whose axes cross ahead of both within ``CLOSURE_MAX_M`` (a glazed corner: both walls run on
      to the corner) when the walls turn by at least 30 degrees (``CORNER_MIN_SIN``) and the corner is farther than
      ``CORNER_MAX_M`` from one of them (nearer corners are ``_short_joins``' work).

    Each candidate: ``{"kind", "ends": [(wall index, which)], "src": [the walls], "segments": [(a, b)], "length",
    "free": every end free, "short", "support": the share of its length the building's drawn lines run along
    (``support_share`` over ``_stroke_lines``, within half the ``thickness`` + ``CLOSURE_SUPPORT_TOL_M``),
    "wall_support": the same share over the wall-layer lines only (what RC5 compares), "outline_dist": how far it
    runs inside the drawn ``outline`` (the length-weighted mean distance of its ends and middles to the outline's
    boundary; 0 without one), "from", "to"}``, the free-end candidates first, then the ones nearest the drawn outline
    (a facade before a counter line), the shortest first. None between the two pieces of one split wall
    (``_same_split_wall``: a recess opened on purpose); the walls of ``fragments`` are neither ends nor targets."""
    from shapely.strtree import STRtree

    polys = [TP.wall_polygon(w) for w in walls2]
    building = {id(w) for w in bwalls} - set(fragments or ())
    if ends is None:
        ends = ring_ends(walls2, bwalls, b_openings, fragments)
    if not ends:
        return []
    lines, wall_flags = _stroke_lines(strokes)
    tree = STRtree(lines) if lines else None
    wall_lines = [ln for ln, f in zip(lines, wall_flags) if f]
    wall_tree = STRtree(wall_lines) if wall_lines else None
    tol = thickness / 2.0 + CLOSURE_SUPPORT_TOL_M

    def share(segs, ls, tr) -> float:                 # length-weighted over the segments (a door jamb's segment is short)
        total = sum(math.dist(a, b) for a, b in segs)
        if tr is None or total <= 1e-9:
            return 0.0
        return sum(support_share(s, ls, tr, tol) * math.dist(*s) for s in segs) / total

    ring_d = outline.boundary if outline is not None and not outline.is_empty else None

    def inside(segs) -> float:                        # length-weighted mean distance to the drawn outline's boundary
        total = sum(math.dist(a, b) for a, b in segs)
        if ring_d is None or total <= 1e-9:
            return 0.0
        return sum(sum(ring_d.distance(Point(q)) for q in (a, b, ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0))) / 3.0
                   * math.dist(a, b) for a, b in segs) / total

    def name(k, which, p) -> str:
        return f"{walls2[k].entity.split(',')[0]} {which} at ({p[0]:.2f}, {p[1]:.2f})"

    def make(kind, end_list, segs, length, free, short=False, **extra) -> dict:
        return dict({"kind": kind, "ends": end_list, "src": [walls2[k] for k, _ in end_list], "segments": segs,
                     "length": length, "free": free, "short": short, "support": share(segs, lines, tree),
                     "wall_support": share(segs, wall_lines, wall_tree), "outline_dist": inside(segs)}, **extra)

    out: list[dict] = []
    for k, which, (px, py), (dx, dy), h, free in ends:
        nx, ny = -dy, dx
        far = (px + dx * CLOSURE_MAX_M, py + dy * CLOSURE_MAX_M)
        band = Polygon([(px + nx * h, py + ny * h), (px - nx * h, py - ny * h),
                        (far[0] - nx * h, far[1] - ny * h), (far[0] + nx * h, far[1] + ny * h)])
        best = None
        for j, g in enumerate(polys):
            if j == k or id(walls2[j]) not in building or not g.intersects(band):
                continue
            part = g.intersection(band)
            if part.area <= 1e-5:
                continue
            d = min(((qx - px) * dx + (qy - py) * dy) for qx, qy in
                    (c for gg in getattr(part, "geoms", [part]) if hasattr(gg, "exterior") for c in gg.exterior.coords))
            if d > JOIN_TOUCH_M and (best is None or d < best[0]):
                best = (d, j)                           # the first wall the band meets, whatever the gap
        if best is None:
            continue
        d, j = best
        if _same_split_wall(walls2[k], walls2[j], (dx, dy), (px, py), tuple(walls2[j].start)):
            continue
        q = (round(px + dx * (d + 0.01), 4), round(py + dy * (d + 0.01), 4))
        out.append(make("straight", [(k, which)], [((px, py), q)], d, free, short=d <= JOIN_MAX_M,
                        **{"from": name(k, which, (px, py)),
                           "to": f"{walls2[j].entity.split(',')[0]} ({d:.2f} m along the wall's axis)"}))
    for i, (ka, wa, pa, da, ha, fa) in enumerate(ends):
        for kb, wb, pb, db, hb, fb in ends[i + 1:]:
            if ka == kb:
                continue
            cross = da[0] * db[1] - da[1] * db[0]
            if abs(cross) < CORNER_MIN_SIN:
                continue
            rx, ry = pb[0] - pa[0], pb[1] - pa[1]
            ta = (rx * db[1] - ry * db[0]) / cross                # pa + ta * da == pb + tb * db
            tb = (rx * da[1] - ry * da[0]) / cross
            if not (-JOIN_TOUCH_M <= ta <= CLOSURE_MAX_M and -JOIN_TOUCH_M <= tb <= CLOSURE_MAX_M) \
                    or max(ta, tb) <= CORNER_MAX_M:
                continue
            corner = (round(pa[0] + da[0] * ta, 4), round(pa[1] + da[1] * ta, 4))
            segs = [(p, corner) for p, t in ((pa, ta), (pb, tb)) if t > CLOSURE_MIN_SEGMENT_M]
            if not segs:
                continue
            out.append(make("corner", [(ka, wa), (kb, wb)], segs, max(ta, 0.0) + max(tb, 0.0), fa and fb,
                            **{"from": name(ka, wa, pa),
                               "to": f"{name(kb, wb, pb)}; corner at ({corner[0]:.2f}, {corner[1]:.2f})"}))
    return sorted(out, key=lambda c: (0 if c["free"] else 1, round(c["outline_dist"], 1), c["length"]))


def _parallel_to(seg, others: list, thickness: float) -> Optional[tuple]:
    """The accepted bridge segment ``seg`` runs parallel to (within ``CLOSURE_PARALLEL_T`` thicknesses, parallel within
    about 10 degrees) over more than ``CLOSURE_PARALLEL_SHARE`` of its length, as ``(other, overlap share)``, or None."""
    a, b = seg
    L = math.dist(a, b)
    if L <= 1e-9:
        return None
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    for c, d in others:
        vl = math.dist(c, d)
        if vl <= 1e-9 or abs((d[0] - c[0]) / vl * uy - (d[1] - c[1]) / vl * ux) > 0.17:
            continue
        lateral = abs((c[0] - a[0]) * uy - (c[1] - a[1]) * ux)
        if lateral > CLOSURE_PARALLEL_T * thickness:
            continue
        s0, s1 = sorted(((c[0] - a[0]) * ux + (c[1] - a[1]) * uy, (d[0] - a[0]) * ux + (d[1] - a[1]) * uy))
        overlap = max(0.0, min(L, s1) - max(0.0, s0)) / L
        if overlap > CLOSURE_PARALLEL_SHARE:
            return (c, d), overlap
    return None


def _open_labelled_parts(bwalls: list, b_openings: list, blocks: list, fragments: set) -> int:
    """How many building parts hold a room label (inside the part's hull) but close no face around any: the measure
    a bridge set must lower to be kept (5 Nov 2026, review: joining two closed blocks into one is no closure)."""
    walls = [w for w in bwalls if id(w) not in fragments]
    if not walls:
        return 0
    indoor = [Point(b.anchor) for b in blocks if not getattr(b, "exterior", False) and not TP._outdoor_label(b)]
    n = 0
    for part in TP._parts(TP.bridged_union(walls, b_openings)):
        hull = part.convex_hull
        held = [q for q in indoor if hull.contains(q)]
        if held and not any(Polygon(r).contains(q) for r in part.interiors for q in held):
            n += 1
    return n


def _dedupe_openings(items: list, hosts: list) -> tuple[list, int]:
    """The openings read onto the bridges, made unverified at the bridges' confidence, and merged where two symbols
    overlap on one bridge (5 Nov 2026, review): the first keeps its kind, the span is the union."""
    for o in items:
        o.status = "unverified"
        ev = o.evidence if isinstance(o.evidence, dict) else {}
        ev["confidence"] = min(float(ev.get("confidence", 1.0) or 1.0), CLOSURE_CONFIDENCE)
        o.evidence = ev
    by_host: dict = {}
    for o in items:
        k = TP.host_wall(o, hosts)
        by_host.setdefault(k, []).append(o)
    out, merged = [], 0
    for k, group in by_host.items():
        if k is None or len(group) < 2:
            out += group
            continue
        w = hosts[k]
        (x0, y0), (x1, y1) = tuple(w.start), tuple(w.end)
        L = math.hypot(x1 - x0, y1 - y0) or 1.0
        ux, uy = (x1 - x0) / L, (y1 - y0) / L

        def pos(o):
            return (o.center[0] - x0) * ux + (o.center[1] - y0) * uy

        group.sort(key=lambda o: (0 if o.kind == "door" else 1, pos(o)))
        kept: list = []
        for o in sorted(group, key=pos):
            prev = kept[-1] if kept else None
            if prev is not None and abs(pos(o) - pos(prev)) < (o.width + prev.width) / 2.0:
                lo = min(pos(prev) - prev.width / 2.0, pos(o) - o.width / 2.0)
                hi = max(pos(prev) + prev.width / 2.0, pos(o) + o.width / 2.0)
                first = prev if (prev.kind == "door" or o.kind != "door") else o
                first.width = round(hi - lo, 3)
                first.center = (round(x0 + ux * (lo + hi) / 2.0, 4), round(y0 + uy * (lo + hi) / 2.0, 4))
                kept[-1] = first
                merged += 1
            else:
                kept.append(o)
        out += kept
    return out, merged


def _closure_walls(cands: list[dict], thickness: float, file_rel: str, page_no, problem) -> list:
    """The inferred ``WallItem``s of the chosen candidates: the median outer thickness, evidence method ``inferred``,
    confidence ``CLOSURE_CONFIDENCE``, rule ``OUTLINE_CLOSURE_RULE``, a note naming the two wall ends, the gap and the
    drawn lines along it, ``inferred`` and status ``unverified`` (the schema's wall status has no third word;
    ``inferred: true`` says it)."""
    out = []
    for n, c in enumerate(cands, start=1):
        src = c["src"][0]
        ents = "+".join(w.entity.split(",")[0] for w in c["src"])
        for m, (a, b) in enumerate(c["segments"], start=1):
            ev = B.evidence(file_rel, "inferred", CLOSURE_CONFIDENCE, page=page_no, entity=f"closure:{ents}",
                            rule=OUTLINE_CLOSURE_RULE)
            ev["note"] = (f"the outer ring did not close ({problem or 'a room label in no closed face'}): a "
                          f"{c['length']:.2f} m gap from {c['from']} to {c['to']} bridged along the outline "
                          f"({c['kind']}, segment {m} of {len(c['segments'])}; drawn wall lines along "
                          f"{c.get('wall_support', 0.0):.0%} of it, frames and other building lines along "
                          f"{c['support']:.0%}); thickness {thickness:.2f} m (the median outer wall); confidence "
                          f"{CLOSURE_CONFIDENCE:g}: check it on the comparison sheet")
            out.append(WallItem(start=(round(a[0], 4), round(a[1], 4)), end=(round(b[0], 4), round(b[1], 4)),
                                thickness=thickness, box=list(src.box), entity=f"closure:{ents}:{n}.{m}",
                                evidence=ev, exterior=True, status="unverified", inferred=True))
    return out


def _outline_closure(ex, where: str, walls2: list, openings: list, blocks: list, level_id, site_warnings: list,
                     problem: Optional[str], bwalls: list, b_openings: list, strokes: list, exclude: set,
                     file_rel: str, page_no, units_to_m: Optional[float] = None, owned: Optional[set] = None):
    """The last closure pass (4 Nov 2026, Milestone 14 R2; the plan's words: "never leave a level out; carry
    confidence instead"; the user's request behind it: "I want structure recognition to be cumulatively better with
    the feedbacks I am giving").

    What: when the outer ring still does not close, or a room label still lies in no closed face, after every other
    pass (outlines, wide gaps, short joins, glazed facades, recesses, the mirror, the size tags), the gaps of the outer
    ring are bridged by inferred walls at confidence ``CLOSURE_CONFIDENCE`` (0.3): from every wall end on the
    building outline (a free end, or a corner the wall may run on past) the wall runs on along its own axis to the
    first wall it meets (*straight*), or two ends run on to the corner where their axes cross (*corner*: a glazed
    corner) (``closure_candidates``), up to ``CLOSURE_MAX_M``, in up to ``CLOSURE_ROUNDS`` rounds (a chain of gaps).
    Every bridge gets the median outer wall thickness (``_outer_thickness``), evidence method ``inferred``, rule
    ``outline_closure`` and a note naming the two wall ends, the gap length and the drawn lines along it; the door and
    window symbols drawn across the bridges are read onto them (``openings.openings_on_walls``), frames running along
    them give unverified windows (``facade.frame_windows``), all unverified at the bridges' confidence and merged
    where symbols overlap (``_dedupe_openings``): nothing is invented.

    The outline: ``drawn_outline`` finds the plan's drawn outline as ``sheets.register.outline`` does (the long
    strokes grown by 0.75 m, merged, the holes filled, shrunk back). It is the guard, not the generator: a grow-and-
    shrink outline cuts a glazed corner (two walls stopping short of a corner leave a notch that no closing fills)
    and bulges over a balcony's railing, so the walls' own axes give the bridges and the drawn outline says where no
    bridge may go: none beyond the drawn outline grown by ``CLOSURE_OUTLINE_TOL_M`` (nothing is built past what is
    drawn). ``topology.building_outline`` of the walls says which ends are on the outer ring. A bridge from a corner
    end needs the drawing's support: the building's drawn lines (``_stroke_lines``: wall, column, plaster, window,
    door, glass or unnamed layers; never furniture, dimensions, hatches, sections or balcony lines) along at least
    ``CLOSURE_SUPPORT_MIN`` of its length, it runs along the drawn outline (every point within
    ``CLOSURE_ON_OUTLINE_M`` of its boundary: real11's kitchen counter line, 1.9 m inside the facade, had lines along
    all of it and is no facade), and it may not close an unlabelled space over ``CLOSURE_UNLABELLED_MAX_M2`` (a
    courtyard, a terrace, a niche) into the building; a free end is an evident gap and needs none of these.

    Never: through a wall the band meets within ``JOIN_MAX_M`` (``_short_joins``' case, which it left: the closure
    says so and never bridges on to the next wall); across or beside a drawn door or window already read
    (``_join_clear``); beside or enclosing a balcony or terrace label, its mirror image on the plan's twin half, or
    an unlabelled area matching an outdoor space's area text (``outdoor_guard``); between the two pieces of a wall the
    recess passes split on purpose; through a wall end another bridge already uses; parallel to an accepted bridge
    within ``CLOSURE_PARALLEL_T`` thicknesses over more than half its length (a double line is one wall); from or to
    a wall fragment (``wall_fragments``: a part under 0.5 m or 0.1 m2 is listed, never bridged, never a reason).
    Each candidate is judged on the faces it makes on its own, in order (5 Nov 2026, review). Kept only when more
    labelled rooms close, or a part that holds labels and closed no face gets one (``_open_labelled_parts``):
    joining two closed blocks is no closure (a note, no wall); then every bridge not needed for that is dropped again.
    Never silent: ``ex.notes`` (one line per bridge), ``ex.warnings`` (the summary) and ``ex.report["outline_closure"]``
    (every candidate, kept or refused, with the reason, the fragments, the drawn outline and the mirror axis; the
    pipeline writes it to ``reading_check/outline_closure.json``). Returns the 7-tuple of the other passes, or None
    when nothing closes (the level is then built marked under ``failed_levels: build_marked``)."""
    from wenart.ingest.generic import facade as FC

    report: dict = {"problem": problem, "unclosed_before": _unclosed(site_warnings), "kept": [], "refused": [],
                    "fragments": []}
    ex.report["outline_closure"] = report
    outline = drawn_outline(strokes, walls2, exclude)
    guard = outline.buffer(CLOSURE_OUTLINE_TOL_M, join_style=2) if outline is not None else None
    if outline is not None:                           # the debug image and the report show what guarded the bridges
        report["outline"] = [[round(x, 3), round(y, 3)] for x, y in outline.simplify(0.05).exterior.coords]
    og = outdoor_guard(blocks, walls2, _halves(ex, walls2, openings, blocks, level_id, "outline closure"))
    indoor = [Point(b.anchor) for b in blocks if not getattr(b, "exterior", False) and not TP._outdoor_label(b)]
    if og["axis"] is not None:
        report["mirror_axis"] = [og["axis"][0], round(og["axis"][1], 3)]
    thickness, how = _outer_thickness(bwalls, b_openings)
    report["thickness"] = {"m": thickness, "how": how}
    fragments, frag_lines = wall_fragments(walls2, bwalls, b_openings)
    report["fragments"] = frag_lines
    for line in frag_lines:
        ex.notes.append(f"{where}: outline closure: wall fragment {line}: smaller than a wall, never bridged")

    def check(ws):
        bw, site, sw = TP.split_plot(ws, openings, blocks, level_id=level_id)
        idx = {o["index"] for o in site["openings"]}
        b_open = [o for j, o in enumerate(openings) if j not in idx]
        solid = [w for w in bw if id(w) not in fragments]
        return bw, site, sw, b_open, TP.outer_loop_problem(solid, b_open), _open_labelled_parts(bw, b_open, blocks,
                                                                                                fragments)

    refused_keys: set = set()

    def refuse(c, why):
        key = (c["kind"], c["from"], c["to"], why)
        if key in refused_keys:
            return                                        # the same candidate comes back every round: listed once
        refused_keys.add(key)
        report["refused"].append({"kind": c["kind"], "from": c["from"], "to": c["to"], "length_m": round(c["length"], 3),
                                  "support": round(c["support"], 2), "wall_support": round(c.get("wall_support", 0), 2),
                                  "free": c["free"], "outline_dist": round(c["outline_dist"], 2),
                                  "segments": [[list(a), list(b)] for a, b in c["segments"]], "why": why})

    before = _unclosed(site_warnings)
    open_before = _open_labelled_parts(bwalls, b_openings, blocks, fragments)
    report["open_labelled_parts_before"] = open_before
    chosen: list[dict] = []
    cur_walls, cur_b, cur_bo = list(walls2), list(bwalls), list(b_openings)
    for _round in range(CLOSURE_ROUNDS):
        used: set = set()
        added: list[dict] = []
        added_walls: list = []                            # the walls of this round's accepted bridges so far
        without = TP.faces(cur_walls, openings)           # the faces before the next candidate
        accepted_segs = [s for c in chosen + added for s in c["segments"]]
        for c in closure_candidates(cur_walls, cur_b, cur_bo, strokes, thickness, outline=outline, fragments=fragments):
            if any(e in used for e in c["ends"]):
                refuse(c, "a bridge of this round uses that wall end already")
                continue
            if c.get("short"):
                refuse(c, f"a {c['length']:.2f} m gap to the wall ahead: the short-join pass's case, which it left (a "
                          f"drawn door or window beside it, or no room closes with it); never bridged through that "
                          f"wall to the next one")
                continue
            if not c["free"] and c["support"] < CLOSURE_SUPPORT_MIN:
                refuse(c, f"it runs on past a corner with the building's drawn lines along {c['support']:.0%} of it "
                          f"only (a free end is an evident gap; a corner needs the drawing's support)")
                continue
            if not all(_join_clear(a, b, openings) for a, b in c["segments"]):
                refuse(c, "a drawn door or window lies on or beside it")
                continue
            if guard is not None and not all(guard.contains(Point((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0))
                                             for a, b in c["segments"]):
                refuse(c, f"beyond the drawn outline (more than {CLOSURE_OUTLINE_TOL_M:g} m past what is drawn)")
                continue
            if not c["free"] and c["outline_dist"] > CLOSURE_ON_OUTLINE_M:
                refuse(c, f"it runs on past a corner {c['outline_dist']:.1f} m inside the drawn outline (more than "
                          f"{CLOSURE_ON_OUTLINE_M:g} m: a counter or furniture line, not the facade)")
                continue
            beside = next((n for pt, m, n in og["points"] for a, b in c["segments"]
                           if LineString([a, b]).distance(pt) <= CLOSURE_OUTDOOR_CLEAR_M), None)
            if beside is not None:
                refuse(c, f"the '{beside}' label (a balcony or terrace, or its mirror image on the plan's twin half) "
                          f"stands beside it: an outdoor space, not a room")
                continue
            par = next((p for s in c["segments"] for p in [_parallel_to(s, accepted_segs, thickness)] if p), None)
            if par is not None:
                (pc, pd), share_ = par
                refuse(c, f"it runs parallel to an accepted bridge (({pc[0]:.2f}, {pc[1]:.2f})-({pd[0]:.2f}, "
                          f"{pd[1]:.2f})) within {CLOSURE_PARALLEL_T:g} wall thicknesses over {share_:.0%} of its "
                          f"length: a double line, not a second wall")
                continue
            cw = _closure_walls([c], thickness, file_rel, page_no, problem)
            with_c = TP.faces(cur_walls + added_walls + cw, openings)
            made = [f for f in with_c if not any(g.contains(f.representative_point())
                                                 and abs(g.area - f.area) <= 0.02 * g.area + 0.01 for g in without)]
            why = next((w for f in made for w in [outdoor_enclosure(f, og)] if w), None)
            if why:
                refuse(c, why)
                continue
            if not c["free"] and any(f.area > CLOSURE_UNLABELLED_MAX_M2 and not any(f.contains(q) for q in indoor)
                                     for f in made):
                refuse(c, f"it would close an unlabelled space over {CLOSURE_UNLABELLED_MAX_M2:g} m2 into the building")
                continue
            used.update(c["ends"])
            added.append(c)
            added_walls += cw
            accepted_segs += c["segments"]
            without = with_c
        if not added:
            break
        trial = cur_walls + added_walls
        bw, site, sw, b_open, prob, open_parts = check(trial)
        chosen += added
        cur_walls, cur_b, cur_bo = trial, bw, b_open
        if prob is None and _unclosed(sw) == 0 and open_parts == 0:
            break
    if not chosen:
        ex.notes.append(f"{where}: outline closure: no bridge for the open outer ring "
                        f"({problem or 'labels in no closed face'}); {len(report['refused'])} candidate(s) refused")
        return None
    bw, site, sw, b_open, prob, open_after = check(walls2 + _closure_walls(chosen, thickness, file_rel, page_no,
                                                                          problem))
    after = _unclosed(sw)
    if not (after < before or open_after < open_before):
        for c in chosen:
            refuse(c, f"it closes no labelled room and no labelled part (labels in no closed face {before} -> {after}, "
                      f"labelled parts without a face {open_before} -> {open_after}): joining blocks is no closure")
        ex.notes.append(f"{where}: outline closure: {len(chosen)} bridge(s) tried along the outline; none closes a "
                        f"labelled room or a labelled part (labels in no closed face {before} -> {after}, labelled "
                        f"parts without a face {open_before} -> {open_after}; {prob or 'the ring would close'}): not "
                        f"used; detached blocks stay detached")
        return None
    # only the bridges the closing needs stay: the ones farthest inside the drawn outline dropped first (a counter line
    # closes a kitchen as well as its facade does; the facade is kept), then the longest
    for c in sorted(list(chosen), key=lambda c: (-round(c["outline_dist"], 1), -c["length"])):
        rest = [x for x in chosen if x is not c]
        if not rest:
            break
        r2 = check(walls2 + _closure_walls(rest, thickness, file_rel, page_no, problem))
        if _unclosed(r2[2]) <= after and r2[5] <= open_after:
            refuse(c, "not needed: the walls close as well without it")
            chosen = rest
            bw, site, sw, b_open, prob, open_after = r2
    new_walls = _closure_walls(chosen, thickness, file_rel, page_no, problem)
    # the door and window symbols drawn across the bridges, and the frames running along them (nothing invented)
    taken = set(owned) if owned is not None else set()
    read = FC.swing_doors(new_walls, list(strokes),
                          O.openings_on_walls(new_walls, list(strokes), file_rel, page_no, units_to_m=units_to_m,
                                              owned=taken))
    framed = FC.frame_windows(new_walls, list(strokes), read, walls2)
    if owned is not None:
        owned.update(taken)
    on_bridges, merged = _dedupe_openings(read + framed, new_walls)
    all_walls, all_open = walls2 + new_walls, list(openings) + on_bridges
    bw, site, sw = TP.split_plot(all_walls, all_open, blocks, level_id=level_id)
    idx = {o["index"] for o in site["openings"]}
    b_open = [o for j, o in enumerate(all_open) if j not in idx]
    prob = TP.outer_loop_problem([w for w in bw if id(w) not in fragments], b_open)
    for c in chosen:
        report["kept"].append({"kind": c["kind"], "from": c["from"], "to": c["to"], "length_m": round(c["length"], 3),
                               "support": round(c["support"], 2), "wall_support": round(c.get("wall_support", 0), 2),
                               "free": c["free"], "outline_dist": round(c["outline_dist"], 2),
                               "segments": [[list(a), list(b)] for a, b in c["segments"]]})
        ex.notes.append(f"{where}: outline closure ({c['kind']}, confidence {CLOSURE_CONFIDENCE:g}): a {c['length']:.2f} m "
                        f"gap of the outer ring from {c['from']} to {c['to']} bridged by {len(c['segments'])} inferred "
                        f"wall(s) of {thickness:.2f} m ({how}); drawn wall lines along {c.get('wall_support', 0):.0%}, "
                        f"frames and other building lines along {c['support']:.0%} of it"
                        + ("" if c["free"] else "; the wall runs on past a corner"))
    report.update(unclosed_after=_unclosed(sw), problem_after=prob, open_labelled_parts_after=open_after,
                  openings_read=len(read), windows_framed=len(framed), openings_merged=merged)
    ex.warnings.append(f"{where}: the outer ring did not close ({problem or 'room label(s) in no closed face'}): "
                       f"{len(new_walls)} inferred wall(s) bridge {len(chosen)} gap(s) along the outline at confidence "
                       f"{CLOSURE_CONFIDENCE:g} (rule {OUTLINE_CLOSURE_RULE}; {len(read)} drawn opening(s) read on them, "
                       f"{len(framed)} unverified window(s) where frames run along them, {merged} merged, all at "
                       f"confidence {CLOSURE_CONFIDENCE:g}; labels in no closed face {before} -> {_unclosed(sw)}, "
                       f"labelled parts without a face {open_before} -> {open_after}): check them on the comparison "
                       f"sheets (reading check RC7)")
    return all_walls, all_open, bw, site, sw, b_open, prob


SIZE_TAG_RE = re.compile(r"^\s*(\d{2,3})\s*/\s*(\d{2,3})\s*$")   # a window's size tag: width/height in cm
TAG_REACH_M = 0.8               # a size tag stands this close to the wall of its window ...
TAG_ANGLE_DEG = 15.0            # ... written along it
TAG_ACROSS_FACE_M = 0.3         # 20 Nov 2026 (R10-P3): or written across it this close to its face
TAG_SHIFT_M = 0.35              # the tagged window moves at most this far to clear a column, a wall end or a door
TAG_COLLINEAR_M = 0.08          # a wall piece on the host's line (this close to its axis) is the same wall run
FULL_GLASS_M = 2.0              # a tagged window this high starts at the floor (a shop window: full glass) ...
WINDOW_HEAD_M = 2.2             # ... a lower one has its head at the usual lintel height (its sill assumed from it)
PARAPET_RE = re.compile(r"PARAPET\s*[:=]?\s*(\d{2,3})\s*CM")   # 19 Nov 2026 (OA3-01): 'PARAPET:90CM' beside a tag ...
PARAPET_REACH_M = 1.5           # ... this close to it gives its window's sill


PAIR_TAG_RE = re.compile(r"^\s*(\d{2,3})\s*$")   # 20 Nov 2026 (pre-pod R10-P3): one number of a W/H tag written as two
PAIR_ALONG = 0.6                # texts: their centres this many text heights apart along the text ...
PAIR_ACROSS = (0.8, 2.2)        # ... and this many across it (one line over the other: the width over the height)
PAIR_ANGLE_DEG = 5.0
PAIR_HEIGHT_TOL = 0.25
PLAIN_TAG_FRAME_SHARE = 0.5     # a tag on a plain text layer is a window's when window frame lines run along its wall
PLAIN_TAG_BAND_M = 0.15         # ... (within the wall's band grown by this) for this share of its width
PLAIN_TAG_MAX_W_CM = 300
PLAIN_TAG_GAP_MIN_H_M = 1.0     # a plain-layer tag this high or more may type a gap as its window (a lower one is a
#                                 transom or a vent over a door or passage)
PAIR_MIN_CM = 30                # the two numbers of a size are at least this (a stair's step numbers '15' over '16' are not)


def paired_size_tags(texts_m: list) -> list:
    """20 Nov 2026 (pre-pod check R10-P3 / R10-P6 / R10-P1, real10: every window size is written as two texts, '150'
    over '150', '70' over '150', '60' over '60', so no tag rule read them and the windows became sliding doors, holes or
    wall): two number-only texts (``PAIR_TAG_RE``) on one layer that is no dimension or axis layer, of one rotation and
    height, one over the other (``PAIR_ALONG``, ``PAIR_ACROSS`` text heights) are one 'W/H' tag: the upper line is the
    width, the lower the height (pure). Each text joins one pair at most (the nearest)."""
    from wenart.ingest.generic import layer_names as LN

    nums = []
    for t in texts_m or []:
        m = PAIR_TAG_RE.match(str(t.text or ""))
        layer = t.evidence[0].get("layer") if t.evidence else None
        if m and int(m.group(1)) >= PAIR_MIN_CM and LN.layer_role(layer) not in ("dimension", "axis") \
                and float(t.height or 0) > 0:
            nums.append((t, int(m.group(1)), layer))
    cands = []
    for i, (a, va, la) in enumerate(nums):
        for b, vb, lb in nums[i + 1:]:
            if la != lb or abs(((a.rotation_deg or 0.0) - (b.rotation_deg or 0.0) + 180.0) % 360.0 - 180.0) > PAIR_ANGLE_DEG:
                continue
            h = max(float(a.height), float(b.height))
            if abs(float(a.height) - float(b.height)) > PAIR_HEIGHT_TOL * h:
                continue
            r = math.radians(a.rotation_deg or 0.0)
            ux, uy, nx, ny = math.cos(r), math.sin(r), -math.sin(r), math.cos(r)
            ca = ((a.box[0] + a.box[2]) / 2.0, (a.box[1] + a.box[3]) / 2.0)
            cb = ((b.box[0] + b.box[2]) / 2.0, (b.box[1] + b.box[3]) / 2.0)
            dx, dy = cb[0] - ca[0], cb[1] - ca[1]
            along, across = dx * ux + dy * uy, dx * nx + dy * ny
            if abs(along) <= PAIR_ALONG * h and PAIR_ACROSS[0] * h <= abs(across) <= PAIR_ACROSS[1] * h:
                top, bot = ((b, vb), (a, va)) if across > 0 else ((a, va), (b, vb))
                cands.append((math.hypot(dx, dy), top, bot))
    used, out = set(), []
    for _d, (top, w), (bot, hh) in sorted(cands, key=lambda c: c[0]):
        if id(top) in used or id(bot) in used:
            continue
        used.update((id(top), id(bot)))
        ev = [dict(top.evidence[0], entity=f"{top.id}+{bot.id}", text=f"{w}/{hh}")] if top.evidence else []
        out.append(TextRun(id=f"{top.id}+{bot.id}", text=f"{w}/{hh}",
                           box=(min(top.box[0], bot.box[0]), min(top.box[1], bot.box[1]),
                                max(top.box[2], bot.box[2]), max(top.box[3], bot.box[3])),
                           height=float(top.height), rotation_deg=float(top.rotation_deg or 0.0), source=top.source,
                           evidence=ev))
    return out


def _frame_cover(strokes: list, x0, y0, ux, uy, half: float, lo: float, hi: float) -> float:
    """The share of [lo, hi] along a wall (origin x0, y0, direction ux, uy, half thickness ``half``) that window or
    glass layer lines (no arc) run along within its band grown by ``PLAIN_TAG_BAND_M``."""
    from wenart.ingest.generic import layer_names as LN

    spans = []
    for st in strokes or []:
        pts = getattr(st, "pts", None) or []
        if getattr(st, "arc", None) or len(pts) < 2 or LN.layer_role(getattr(st, "layer", None)) not in ("window",
                                                                                                          "glass"):
            continue
        for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
            oa = abs(-(ax - x0) * uy + (ay - y0) * ux)
            ob = abs(-(bx - x0) * uy + (by - y0) * ux)
            if max(oa, ob) > half + PLAIN_TAG_BAND_M:
                continue
            ta, tb = sorted(((ax - x0) * ux + (ay - y0) * uy, (bx - x0) * ux + (by - y0) * uy))
            if tb - ta < 0.05:
                continue
            a, b = max(ta, lo), min(tb, hi)
            if b > a:
                spans.append((a, b))
    covered, end = 0.0, None
    for a, b in sorted(spans):
        if end is None or a > end:
            covered += b - a
            end = b
        elif b > end:
            covered += b - end
            end = b
    return covered / (hi - lo) if hi > lo else 0.0


FRAMED_MIN_M = 0.4              # 20 Nov 2026 (pre-pod R10-P2): window frame lines this long along a wall, inside its band
FRAMED_LINES_MIN = 2            # ... on at least this many distinct lines (a frame and its sash) ...
FRAMED_BAND_TOL_M = 0.02        # ... within the wall's faces (this slack) ...
FRAMED_ANGLE = 0.05             # ... parallel to it (sine of the angle) are a window there
FRAMED_JAMB_M = 0.12            # a wall-layer line across the band this close to a frame end is the window's jamb
LEADER_TAG_M = 0.15             # a leader line ends this close to its tag's box ...
LEADER_REACH_M = 0.10           # ... and this close to the window's span inside the band
FRAMED_TAG_TOL_M = 0.15         # the tag's width within this (or this share) of the jamb-to-jamb width is its tag
FRAMED_TAG_TOL = 0.10
FRAMED_RIM_M = 0.30             # the facade's walls: within this of the building outline
FRAMED_NEAR_M = 0.35            # an opening read this far off the wall's axis (on a wall piece beside it) is its own


def covered_share(lo: float, hi: float, spans: list) -> float:
    """The share of ``[lo, hi]`` the union of ``spans`` (``[(a, b)]``) covers (pure; 21 Nov 2026)."""
    if hi - lo <= 1e-9:
        return 0.0
    parts = sorted((max(lo, a), min(hi, b)) for a, b in spans if min(hi, b) > max(lo, a))
    total, cur = 0.0, None
    for a, b in parts:
        if cur is not None and a <= cur[1]:
            cur = (cur[0], max(cur[1], b))
        else:
            if cur is not None:
                total += cur[1] - cur[0]
            cur = (a, b)
    if cur is not None:
        total += cur[1] - cur[0]
    return total / (hi - lo)


def framed_spans(x0, y0, ux, uy, half: float, segs: list) -> list:
    """``[(lo, hi, lines)]`` along a wall (origin x0, y0, direction ux, uy, half thickness ``half``): the stretches the
    window or glass layer segments ``segs`` (``[((ax, ay), (bx, by))]``) parallel to the wall and inside its band
    (``FRAMED_BAND_TOL_M``) cover, each with the number of distinct lines (offsets 1 cm apart) over it; only
    stretches of ``FRAMED_MIN_M`` or more on ``FRAMED_LINES_MIN`` or more lines (pure; R10-P2)."""
    rows = []
    for (ax, ay), (bx, by) in segs:
        L = math.hypot(bx - ax, by - ay)
        if L < 0.05 or abs((bx - ax) * uy - (by - ay) * ux) / L > FRAMED_ANGLE:
            continue
        oa = -(ax - x0) * uy + (ay - y0) * ux
        ob = -(bx - x0) * uy + (by - y0) * ux
        if max(abs(oa), abs(ob)) > half + FRAMED_BAND_TOL_M:
            continue
        ta, tb = sorted(((ax - x0) * ux + (ay - y0) * uy, (bx - x0) * ux + (by - y0) * uy))
        rows.append((ta, tb, round((oa + ob) / 2.0, 2)))
    out, cur = [], None
    for ta, tb, off in sorted(rows):
        if cur is not None and ta <= cur[1] + 0.02:
            cur = (cur[0], max(cur[1], tb), cur[2] | {off})
        else:
            if cur is not None:
                out.append(cur)
            cur = (ta, tb, {off})
    if cur is not None:
        out.append(cur)
    return [(lo, hi, len(offs)) for lo, hi, offs in out if hi - lo >= FRAMED_MIN_M and len(offs) >= FRAMED_LINES_MIN]


def _segments(strokes: list, roles: tuple) -> list:
    out = []
    for st in strokes or []:
        pts = getattr(st, "pts", None) or []
        if getattr(st, "arc", None) or len(pts) < 2:
            continue
        from wenart.ingest.generic import layer_names as LN
        if LN.layer_role(getattr(st, "layer", None)) not in roles:
            continue
        pts = list(pts) + ([pts[0]] if getattr(st, "closed", False) else [])
        out += [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for a, b in zip(pts, pts[1:])]
    return out


def _framed_windows(ex, where: str, walls2: list, openings: list, strokes: list, texts_m: list, units_to_m: float):
    """20 Nov 2026 (pre-pod check R10-P2, real10 L0-L6: both kitchens' windows on the street facade, their frame and
    sash lines drawn between two wall-layer jambs, a '165' over '210' tag joined to them by a leader line, were never
    read: two plaster lines ran straight across each bay and overlapping wall pieces covered it): window or glass lines
    inside a wall's band (``framed_spans``) where no opening is read are a window across the band, between the jambs
    drawn across the band at its ends (``FRAMED_JAMB_M``), else the frames' extent; sized by a tag a leader line joins to
    it (``LEADER_TAG_M``, ``LEADER_REACH_M``), else the default window. The plaster lines across the bay do not close it;
    the build cuts the window through every overlapping wall piece. Returns the new openings or None."""
    from wenart.ingest.model import OpeningItem

    frames = _segments(strokes, ("window", "glass"))
    if not frames or not walls2:
        return None
    jambs = _segments(strokes, ("wall", "column"))
    tags = []
    for t in list(texts_m) + paired_size_tags(texts_m):
        m = SIZE_TAG_RE.match(str(t.text or ""))
        if m:
            tags.append((t, int(m.group(1)) / 100.0, int(m.group(2)) / 100.0))
    others = [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for st in strokes or []
              if not getattr(st, "arc", None) and len(getattr(st, "pts", None) or []) == 2
              for a, b in [st.pts] if 0.2 <= math.dist(a, b) <= 3.0]
    out, made = list(openings), []
    outline = TP.building_outline(walls2, [o for o in openings if not o.virtual])
    rim = outline.boundary if outline is not None and not outline.is_empty else None
    for w in walls2:
        (x0, y0), (x1, y1) = tuple(w.start), tuple(w.end)
        L = math.hypot(x1 - x0, y1 - y0)
        if L < 0.6 or rim is None or TP.wall_polygon(w).distance(rim) > FRAMED_RIM_M:
            continue                                       # only the facade's walls (inner glazing stays as read)
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        half = float(w.thickness) / 2.0
        for lo, hi, n in framed_spans(x0, y0, ux, uy, half, frames):
            def along(q):
                return (q[0] - x0) * ux + (q[1] - y0) * uy

            def off(q):
                return -(q[0] - x0) * uy + (q[1] - y0) * ux
            # 21 Nov 2026 (the RC18 fix round, real17 L1: a double casement window read as two 0.77 m windows in the
            # band, each covering less than half of the 1.8 m sill lines drawn outside the wall, got a third 1.8 m
            # window centred 0.29 m off the wall's axis): the openings read there together cover the frames' span
            if covered_share(lo, hi, [(along(o.center) - o.width / 2.0, along(o.center) + o.width / 2.0)
                                      for o in out if not o.virtual and abs(off(o.center)) <= half + FRAMED_NEAR_M]) \
                    >= 0.5:
                continue                                   # openings are read there (or on a wall piece beside it)
            if any(math.dist(c, (x0 + ux * (lo + hi) / 2.0, y0 + uy * (lo + hi) / 2.0)) <= 0.3 for c in made):
                continue                                   # the same frames in an overlapping wall piece
            # the jambs: wall lines across the band near the frames' ends
            ends = []
            for a, b in jambs:
                la = math.dist(a, b)
                if la < 0.05 or abs((b[0] - a[0]) * ux + (b[1] - a[1]) * uy) / la > FRAMED_ANGLE:
                    continue
                ta = (along(a) + along(b)) / 2.0
                if min(abs(off(a)), abs(off(b))) <= half + FRAMED_BAND_TOL_M:
                    ends.append(ta)
            j0 = min((t for t in ends if abs(t - lo) <= FRAMED_JAMB_M), key=lambda t: abs(t - lo), default=lo)
            j1 = min((t for t in ends if abs(t - hi) <= FRAMED_JAMB_M), key=lambda t: abs(t - hi), default=hi)
            a0, a1 = min(j0, j1), max(j0, j1)
            # a tag joined by a leader line
            size, tag_text = None, None
            for t, tw, th in tags:
                if abs(tw - (a1 - a0)) > max(FRAMED_TAG_TOL_M, FRAMED_TAG_TOL * (a1 - a0)):
                    continue                               # another opening's tag
                box = Polygon([(t.box[0], t.box[1]), (t.box[2], t.box[1]), (t.box[2], t.box[3]), (t.box[0], t.box[3])])
                for a, b in others:
                    for p, q in ((a, b), (b, a)):
                        if box.distance(Point(p)) <= LEADER_TAG_M and abs(off(q)) <= half + LEADER_REACH_M \
                                and a0 - LEADER_REACH_M <= along(q) <= a1 + LEADER_REACH_M:
                            size, tag_text = (tw, th), t.text
                if size:
                    break
            width = a1 - a0
            height = size[1] if size else O.WINDOW_HEIGHT_M
            full = height >= FULL_GLASS_M
            # a door's size (door-high, door-wide: ``_door_like_tag``'s bounds) on frames: a glazed door
            kind = "door" if size and size[1] * 100 >= DOOR_TAG_MIN_H_CM and size[0] * 100 <= 120 else "window"
            mid = (a0 + a1) / 2.0
            ev = dict(w.evidence or {})
            ev.update(method="vector", confidence=0.8, rule="framed_window",
                      reason=(f"window frame lines ({n} lines) drawn inside the wall's band"
                              + (" between its jambs" if (j0, j1) != (lo, hi) else "")
                              + (f", sized by the tag '{tag_text}' its leader line joins" if size else "")
                              + ": a window across the wall (the plaster lines across the bay do not close it)"))
            out.append(OpeningItem(kind=kind, width=round(width, 3),
                                   center=(round(x0 + ux * mid, 4), round(y0 + uy * mid, 4)),
                                   rotation_deg=math.degrees(math.atan2(uy, ux)), box=list(w.box),
                                   entity=f"framed:{w.entity}", evidence=ev, height=round(height, 2),
                                   sill=None if kind == "door" else 0.0 if full else
                                   round(max(0.0, WINDOW_HEAD_M - height), 2),
                                   assumed=[] if size else ["height", "sill_height"],
                                   type_raw="window frame lines inside the wall" + (f", tag {tag_text}" if size else "")))
            made.append((x0 + ux * mid, y0 + uy * mid))
    if not made:
        return None
    ex.notes.append(f"{where}: {len(made)} window(s) read from frame lines drawn inside a wall's band (rule "
                    f"framed_window)")
    return out


def _window_tags(ex, where: str, walls2: list, openings: list, texts_m: list, units_to_m: float,
                 strokes: list = ()):
    """4 Nov 2026 (real17 L0, user: "these sections could be full windows glass, check it"): a window size tag ("470/240",
    width/height in cm, on a window text layer) written along a wall within ``TAG_REACH_M`` is that wall's window: one
    window of that width and height, centred at the tag and moved up to ``TAG_SHIFT_M`` to clear the columns, the run's
    ends and the doors; the windows read inside its span are replaced (a frame read as wall, a frame split into small
    windows). A window ``FULL_GLASS_M`` or higher starts at the floor, a lower one ends at ``WINDOW_HEAD_M`` (its sill
    assumed). Returns the new openings or None.

    19 Nov 2026 (review A3, OA3-01: real11's '80/150' and '50/50' on its door layer KAPI were left to no rule once a tag
    under a door's height made no door; the gaps' three-line window symbols became 1.02 m sliding doors on L0-L6): a size
    tag lower than a door (``DOOR_TAG_LOW_H_CM``) on a door layer is a window's or a vent's tag: its window replaces a
    door read from leaf lines alone in its span; a 'PARAPET: nn CM' text beside the tag gives the sill."""
    from wenart.ingest.generic import layer_names as LN
    from wenart.ingest.model import OpeningItem

    tags = []
    plain = set()
    # the sizes written as two texts on a plain text layer (20 Nov 2026, R10-P3; gate: on real07's joinery layer, where
    # every size is one 'W/H' text, the two-text pairs joined numbers of different tags)
    pairs = [t for t in paired_size_tags(texts_m)
             if LN.layer_role(t.evidence[0].get("layer") if t.evidence else None) in DOOR_TAG_TEXT_ROLES]
    for t in list(texts_m) + pairs:
        m = SIZE_TAG_RE.match(t.text or "")
        layer = (t.evidence[0].get("layer") if t.evidence else None)
        if m and LN.layer_role(layer) in ("window", "glass") \
                and not _door_like_tag(t, int(m.group(1)), int(m.group(2)), openings):
            tags.append((t, int(m.group(1)) / 100.0, int(m.group(2)) / 100.0))
        elif m and LN.layer_role(layer) == "door" and int(m.group(2)) < DOOR_TAG_LOW_H_CM:
            tags.append((t, int(m.group(1)) / 100.0, int(m.group(2)) / 100.0))
        elif m and LN.layer_role(layer) in DOOR_TAG_TEXT_ROLES and strokes and int(m.group(1)) <= PLAIN_TAG_MAX_W_CM \
                and int(m.group(2)) < DOOR_TAG_LOW_H_CM:
            # 20 Nov 2026 (pre-pod R10-P3, real10: '150' over '150' on the text layer TEXT beside a PENCERE window read
            # as a sliding door): a window-high tag (under a door's height) on a plain text layer is a window's where
            # window frame lines run along its wall (checked below, ``PLAIN_TAG_FRAME_SHARE``); a door-high one stays
            # the door tags' (``_door_tags``)
            tags.append((t, int(m.group(1)) / 100.0, int(m.group(2)) / 100.0))
            plain.add(id(t))
    if not tags or not walls2:
        return None
    parapets = []
    for t in texts_m:
        pm = PARAPET_RE.search(B.fold_ascii(str(t.text or "")).upper())
        if pm:
            parapets.append((((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0), int(pm.group(1)) / 100.0))
    polys = [TP.wall_polygon(w) for w in walls2]
    out = list(openings)
    done, skipped = [], []
    for t, width, height in tags:
        cx, cy = (t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0
        r = math.radians(t.rotation_deg or 0.0)
        td = (math.cos(r), math.sin(r))
        best = None
        across = None
        for k, w in enumerate(walls2):
            (x0, y0), (x1, y1) = tuple(w.start), tuple(w.end)
            L = math.hypot(x1 - x0, y1 - y0)
            if L < 0.3:
                continue
            ux, uy = (x1 - x0) / L, (y1 - y0) / L
            s_ = (cx - x0) * ux + (cy - y0) * uy
            d = abs(-(cx - x0) * uy + (cy - y0) * ux)
            sin_a = abs(td[0] * uy - td[1] * ux)
            if sin_a > math.sin(math.radians(TAG_ANGLE_DEG)):
                # 20 Nov 2026 (pre-pod R10-P3, real10: every tag written across its wall, just outside its face): a tag
                # across the wall within ``TAG_ACROSS_FACE_M`` of its face, when no wall runs along it
                if sin_a >= math.cos(math.radians(TAG_ANGLE_DEG)) and d <= float(w.thickness) / 2.0 + TAG_ACROSS_FACE_M \
                        and 0.0 <= s_ <= L and (across is None or d < across[0]):
                    across = (d, k, (x0, y0), (ux, uy), s_)
                continue
            if d <= TAG_REACH_M and -0.1 <= s_ <= L + 0.1 and (best is None or d < best[0]):
                best = (d, k, (x0, y0), (ux, uy), s_)
        via_across = best is None and across is not None
        best = best or across
        if best is None:
            skipped.append(f"{t.text}: no wall along it within {TAG_REACH_M:.1f} m")
            continue
        _, k, (x0, y0), (ux, uy), s_ = best
        nx, ny = -uy, ux
        host = walls2[k]
        h = float(host.thickness) / 2.0

        def along(q):
            return (q[0] - x0) * ux + (q[1] - y0) * uy

        def off(q):
            return (q[0] - x0) * nx + (q[1] - y0) * ny

        run = [along(host.start), along(host.end)]
        blocked = []
        band = Polygon([(x0 + nx * h - ux * 50, y0 + ny * h - uy * 50), (x0 + nx * h + ux * 50, y0 + ny * h + uy * 50),
                        (x0 - nx * h + ux * 50, y0 - ny * h + uy * 50), (x0 - nx * h - ux * 50, y0 - ny * h - uy * 50)])
        for j, g in enumerate(polys):
            if j == k or not g.intersects(band):
                continue
            w = walls2[j]
            wl = math.dist(tuple(w.start), tuple(w.end))
            par = wl > 0 and abs(((w.end[0] - w.start[0]) * uy - (w.end[1] - w.start[1]) * ux) / wl) < 0.1
            if par and max(abs(off(w.start)), abs(off(w.end))) <= TAG_COLLINEAR_M \
                    and float(w.thickness) <= float(host.thickness) + 0.05:
                run += [along(w.start), along(w.end)]                    # the same wall run (a thicker piece: a column)
                continue
            part = g.intersection(band)
            if part.area <= 1e-5:
                continue
            ps = [along(c) for gg in getattr(part, "geoms", [part]) if hasattr(gg, "exterior")
                  for c in gg.exterior.coords]
            blocked.append((min(ps), max(ps)))
        if (id(t) in plain or via_across) and _frame_cover(strokes, x0, y0, ux, uy, h, s_ - width / 2.0,
                                                           s_ + width / 2.0) < PLAIN_TAG_FRAME_SHARE:
            # (20 Nov 2026, gate: real07's '350' over '70' beside the garage stood 0.29 m from the end of a cross wall
            # and made a 3.5 m window there; the garage door went to it) a tag across a wall, like a plain-layer tag,
            # is that wall's window only where window frames run along it
            skipped.append(f"{t.text}: a {'plain-layer ' if id(t) in plain else ''}tag "
                           f"{'across its wall ' if via_across else ''}with no window frames along its wall")
            continue
        # a window's lines read as leaves give way to the tag (19 Nov 2026, OA3-01: a door layer's low tag; 20 Nov
        # 2026, R10-P3: a plain-layer tag over window frames)
        low = id(t) in plain or height * 100.0 < DOOR_TAG_LOW_H_CM and LN.layer_role(
            (t.evidence[0].get("layer") if t.evidence else None)) == "door"
        for j, o in enumerate(out):
            if o.kind == "door" and abs(off(o.center)) <= h + 0.05:
                a = along(o.center)
                if low and _leaf_line_door(o) and abs(a - s_) <= float(o.width) / 2.0 + TAG_SHIFT_M:
                    continue                    # 19 Nov 2026 (OA3-01): the window symbol's lines read as leaves
                blocked.append((a - float(o.width) / 2.0, a + float(o.width) / 2.0))
        # the free stretch of the run around the tag
        lo, hi = min(run), max(run)
        for a, b in blocked:
            if b <= s_:
                lo = max(lo, b)
            elif a >= s_:
                hi = min(hi, a)
            else:
                lo = hi = s_                                             # the tag stands on a column or a door
        if hi - lo < width - 2 * TAG_SHIFT_M or hi - lo < 0.3:
            skipped.append(f"{t.text}: only {max(0.0, hi - lo):.2f} m free on its wall")
            continue
        a0 = min(max(s_ - width / 2.0, lo), max(lo, hi - width))
        a1 = min(a0 + width, hi)
        if abs((a0 + a1) / 2.0 - s_) > TAG_SHIFT_M + max(0.0, width - (hi - lo)) / 2.0:
            skipped.append(f"{t.text}: its window would move more than {TAG_SHIFT_M:.2f} m off the tag")
            continue
        gone = [o for o in out if o.kind in ("window", "opening") and not o.virtual
                and abs(off(o.center)) <= h + 0.05 and a0 - 0.05 <= along(o.center) <= a1 + 0.05
                and (o.kind == "window" or a0 - 0.05 <= along(o.center) - float(o.width) / 2.0
                     and along(o.center) + float(o.width) / 2.0 <= a1 + 0.05)]   # a gap only when wholly inside
        # 19 Nov 2026 (review A3, OA3-02: real11's façade, a wall with its 120/120 window and two 50/50 shower windows
        # between the bathrooms' wall ends, stayed one 5.91 m wide-gap 'opening' once no lift rule closed it): a wide
        # gap whose kind the drawing did not say (``wide_gaps``) holding a tagged window is that wall with its windows
        gone += [o for o in out if o.kind == "opening" and not o.virtual
                 and (o.evidence if isinstance(o.evidence, dict) else {}).get("rule") == "wide_gap"
                 and all(o is not g for g in gone) and abs(off(o.center)) <= h + 0.05
                 and abs(along(o.center) - (a0 + a1) / 2.0) <= float(o.width) / 2.0]
        if low:
            # (as a door-layer tag's door did: the gap it stands in takes its size, the rest of the gap is wall)
            gone += [o for o in out if (_leaf_line_door(o) or (o.kind == "opening" and not o.virtual))
                     and all(o is not g for g in gone) and abs(off(o.center)) <= h + 0.05
                     and abs(along(o.center) - (a0 + a1) / 2.0) <= float(o.width) / 2.0]
        if id(t) in plain and height < PLAIN_TAG_GAP_MIN_H_M and any(o.kind == "opening" for o in gone):
            # 20 Nov 2026 (gate: real07's '350/70' over the garage's 3.41 m gap, C0045 a garage door): a plain-layer tag
            # lower than a window over a gap is a transom or a vent above the door or passage: the gap stays
            skipped.append(f"{t.text}: a {height:.2f} m high window over a gap (a transom or a vent): the gap kept")
            continue
        out = [o for o in out if all(o is not g for g in gone)]
        mid = (a0 + a1) / 2.0
        ev = dict(t.evidence[0]) if t.evidence else {}
        ev.update(method="vector", confidence=0.9, rule="size_tag",
                  reason=f"the window size tag '{t.text}' (width/height in cm) beside the wall")
        full = height >= FULL_GLASS_M
        tc = (cx, cy)
        sill_m = next((v for q, v in sorted(parapets, key=lambda pq: math.dist(pq[0], tc))
                       if math.dist(q, tc) <= PARAPET_REACH_M), None)
        if sill_m is not None and not full:
            ev["note"] = f"sill {sill_m:.2f} m from the parapet text beside the tag"
        out.append(OpeningItem(kind="window", width=round(a1 - a0, 3),
                               center=(round(x0 + ux * mid, 4), round(y0 + uy * mid, 4)),
                               rotation_deg=math.degrees(math.atan2(uy, ux)),
                               box=[v / units_to_m for v in t.box], entity=t.id, evidence=ev, height=height,
                               sill=0.0 if full else (round(sill_m, 2) if sill_m is not None
                                                      else round(max(0.0, WINDOW_HEAD_M - height), 2)),
                               assumed=[] if full or sill_m is not None else ["sill_height"],
                               type_raw=f"window size tag {t.text.strip()}"))
        done.append(f"{t.text.strip()} ({len(gone)} read window(s) replaced"
                    + (f", {a1 - a0:.2f} m free" if a1 - a0 < width - 1e-3 else "") + ")")
    if done:
        ex.notes.append(f"{where}: {len(done)} window(s) set by their size tags: " + ", ".join(done[:12]))
    if skipped:
        ex.notes.append(f"{where}: window size tags not used: " + "; ".join(skipped[:8]))
    return out if done else None


DOOR_TAG_LOW_H_CM = 180        # 12 Nov 2026: a door size tag is at least this high (a lower one is a window or vent)
DOOR_TAG_REACH_M = 1.2          # 4 Nov 2026 (UL321): a door size tag stands this close to its door's gap
DOOR_TAG_KINDS = ("opening", "window", "door")


NOT_LIVED_IN_TYPES = ("other", "shaft", "balcony", "terrace")   # 12 Nov 2026: room types no label of a lived-in room has
DOOR_TAG_MIN_H_CM = 200        # 6 Nov 2026: a size tag this high is a door's (on a plain text layer: ``_door_tags``)
DOOR_TAG_MAX_W_CM = 300        # 12 Nov 2026: ... and no wider than a door product (a garage door; review B-OPN-08)
DOOR_TAG_TEXT_ROLES = (None, "text")
DOOR_TAG_WINDOW_WIDTH_M = 0.25   # 6 Nov 2026: a door-layer door tag takes a drawn window this close to its width
DOOR_TAG_SAME_M = 0.05           # 12 Nov 2026: a door this close to the tag's width is the tag's door (used up) ...
DOOR_TAG_DOOR_W_M = 0.30         # ... a drawn door within this of it may take its size (a leaf drawn without frames,
#                                  openings.DOOR_FRAME_M + 5 cm); a door further off is another door, never resized
DOOR_TAG_GAP_SHARE = 2.0         # a gap wider than this many tag widths holds more than one such door: not the tag's
DOOR_TAG_COINCIDENT_M = 0.05     # doors this close (centres) are one spot: it takes one tag at most
DOOR_TAG_SIDE_M = 0.30           # an opening is in an outer wall when a point this far past its face lies outside
DOOR_TAG_LEAF_M = 0.15           # 12 Nov 2026 (review B2 FC-05): a tag this near a door's drawn leaf or swing is its
DOOR_TAG_TIE_M = 0.01            # ... pairs this near the tag's nearest are equally near (one edge read on two copies)
DOOR_TAG_PLAIN_MIN_H_CM = 205    # review B2-GEN-02: 200 is a mattress's length ('160/200'); every plain-layer door tag of
#                                  the drawings read is 210 or more


def _door_like_tag(t, w_cm: int, h_cm: int, openings: list, max_w_cm: int = 120) -> bool:
    """4 Nov 2026 (real07: every size tag, doors' and windows', on the joinery layer DOĞRAMA): a tag on a window or joinery
    layer is a door's when it is door-high (>= 200 cm) and door-wide (<= 120 cm) and the nearest opening within
    ``DOOR_TAG_REACH_M`` is a door or a gap, not a window."""
    if h_cm < DOOR_TAG_MIN_H_CM or w_cm > max_w_cm:
        return False
    c = ((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0)
    near = [(math.dist(c, tuple(o.center)), o) for o in openings if not o.virtual]
    near = [x for x in near if x[0] <= DOOR_TAG_REACH_M]
    if not near:
        return False
    o = min(near, key=lambda x: x[0])[1]
    return o.kind in ("door", "opening") or "gap" in str(o.type_raw or "")


def _span(o) -> LineString:
    """The opening's span along its wall (its centre +- half its width at its rotation)."""
    r = math.radians(float(o.rotation_deg or 0.0))
    dx, dy = math.cos(r) * float(o.width) / 2.0, math.sin(r) * float(o.width) / 2.0
    cx, cy = float(o.center[0]), float(o.center[1])
    return LineString([(cx - dx, cy - dy), (cx + dx, cy + dy)])


def _outer_opening(o, outline) -> bool:
    """The opening stands in an outer wall: a point ``DOOR_TAG_SIDE_M`` past either face (0.3 m off the centre line
    plus half a thick wall) lies outside the building's filled outline."""
    if outline is None or outline.is_empty:
        return False
    r = math.radians(float(o.rotation_deg or 0.0))
    nx, ny = -math.sin(r), math.cos(r)
    off = 0.25 + DOOR_TAG_SIDE_M
    cx, cy = float(o.center[0]), float(o.center[1])
    return any(not outline.contains(Point(cx + sg * nx * off, cy + sg * ny * off)) for sg in (-1.0, 1.0))


def _window_content(o) -> bool:
    """A gap holding lines along it (its unclassified content noted 'no_glass': two or more lines spanning it, a
    window's frame drawn without glass the reader could confirm)."""
    ev = o.evidence if isinstance(o.evidence, dict) else {}
    return ev.get("rule") == "no_glass"


def _leaf_distance(c, o, strokes: dict) -> float:
    """The distance from point ``c`` to the drawn strokes of door ``o`` (its swing and leaf, its evidence's entities),
    inf when none is known."""
    ev = o.evidence if isinstance(o.evidence, dict) else {}
    best = float("inf")
    for e in str(ev.get("entity") or o.entity or "").split(","):
        st = strokes.get(e.strip())
        if st is not None and len(st.pts) >= 2:
            best = min(best, LineString(st.pts).distance(c))
    return best


K_TAG_RE = re.compile(r"^\s*K\s*\d{0,2}\s*[:\-]\s*(\d{2,3})\s*/\s*(\d{2,3})\s*$", re.IGNORECASE)   # 'K1: 90/210'
CUT_SPAN_WIDTH_TOL_M = 0.12     # rule cut_span_door: two jamb lines this close to the tag's width apart frame its door
CUT_SPAN_BLOCK_W_M = (0.6, 2.4)  # ... (a door block with no tag: jambs this far apart)
CUT_SPAN_JAMB_DEG = 5.0          # a jamb line runs across the wall within this angle of square
CUT_SPAN_JAMB_COVER = 0.8        # ... over this share of the wall's thickness
CUT_SPAN_TAG_SHIFT_M = 0.4       # the jambs' centre within half the width plus this of the tag (along the wall)
CUT_SPAN_BLOCK_REACH_M = 0.3     # a door block stands this close to the wall band
CUT_SPAN_BLOCK_MIN_M = 0.5       # a door block this large at least (a door's symbol; a handle or a frame detail is not)
CUT_SPAN_BLOCK_TOL_M = 0.15      # ... and its jambs this close to its size apart
CUT_SPAN_OWN_DOOR_M = 0.10       # a door within the tag's reach this close to its width is the tag's own door


def _door_evidence(texts_m: list, strokes: list, unit_m: float = 1.0) -> list:
    """``[(point, width or None, height or None, what, evidence)]``: the door size tags (W/H with H >= 1.80 m on a
    door layer, a door-high one on a plain text layer, or the 'K:' form) and the door block inserts (a block whose name
    or layer means door, ``layer_names``) of a page (pure); ``unit_m``: metres per unit of the points (a block's
    ``size_m`` and its size test are in metres)."""
    from wenart.ingest.generic import layer_names as LN

    out = []
    for t in texts_m:
        text = str(t.text or "")
        layer = (t.evidence[0].get("layer") if t.evidence else None)
        role = LN.layer_role(layer)
        m, k = SIZE_TAG_RE.match(text), K_TAG_RE.match(text)
        if not (m or k):
            continue
        w_cm, h_cm = (int(g) for g in (k or m).groups())
        if w_cm > DOOR_TAG_MAX_W_CM or h_cm < DOOR_TAG_LOW_H_CM:
            continue
        if not (k or role == "door" or (role in DOOR_TAG_TEXT_ROLES and h_cm >= DOOR_TAG_PLAIN_MIN_H_CM)):
            continue
        c = ((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0)
        ev = dict(t.evidence[0]) if t.evidence else {}
        out.append((c, w_cm / 100.0, h_cm / 100.0, f"the door size tag '{text.strip()}'", ev))
    groups: dict = {}
    for st in strokes:
        if not st.block or "/" not in str(st.id):
            continue
        names = [st.layer] + str(st.block).split("/")
        if any(LN.layer_role(n) == "door" for n in names):
            groups.setdefault(str(st.id).split("/")[0], []).append(st)
    for key, sts in sorted(groups.items()):
        xs = [p[0] for st in sts for p in st.pts]
        ys = [p[1] for st in sts for p in st.pts]
        if not xs:
            continue
        size = max(max(xs) - min(xs), max(ys) - min(ys)) * float(unit_m)
        if size < CUT_SPAN_BLOCK_MIN_M:
            continue                            # a handle or a frame detail, not a door's symbol
        c = ((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0)
        out.append((c, None, None, f"the door block '{sts[0].block}' ({key})",
                    {"entity": key, "layer": sts[0].layer, "block": sts[0].block, "size_m": round(size, 3)}))
    return out


def doors_in_cut_spans(walls2: list, openings: list, strokes: list, texts_m: list, units_to_m: float) -> Optional[list]:
    """20 Nov 2026 (rule ``cut_span_door``, ``rule_guards``; real20's kitchen-to-balcony door, tagged '120/210', whose
    gap the wall's cut lines closed and whose door block carries no swing arc): a door size tag or a door block
    standing at a wall where no opening is read, between two jamb lines that run square across the wall's whole
    thickness that far apart (the tag's width, ``CUT_SPAN_WIDTH_TOL_M``; a block: its size), makes the span a door:
    the lines along it are the wall's section edge at the opening (cut or hatch lines), not a solid wall. The jambs are
    lines of the wall's drawing (never a door layer's frame profile), so a wall whose faces run on unbroken, with no
    jamb lines across it, is never opened, whatever text stands beside it. Returns the openings with the new doors added (sized by the jambs, the tag's height), or
    None when there is none (pure)."""
    from wenart.ingest import rule_guards as RG
    from wenart.ingest.generic import layer_names as LN

    if not RG.active("cut_span_door"):
        return None
    evidence = _door_evidence(texts_m, strokes)
    if not evidence:
        return None
    segs = []                                   # the straight pieces of the wall drawing (page metres): jamb lines
    for st in strokes:
        names = [st.layer] + (str(st.block).split("/") if st.block else [])
        if st.arc or len(st.pts) < 2 or any(LN.layer_role(n) in ("door", "window") for n in names):
            continue                            # a door's frame profile or a window's lines are no jamb of the wall
        segs.extend(zip(st.pts, st.pts[1:]))
    out = list(openings)
    added = []
    for c, width, height, what, ev in evidence:
        if width is not None and any(
                not o.virtual and o.kind in ("door", "opening") and abs(float(o.width) - width) <= CUT_SPAN_OWN_DOOR_M
                and math.dist(o.center, c) <= DOOR_TAG_REACH_M + float(o.width) / 2.0 for o in out + added):
            continue                            # the tag's own door is read (the size tags step sizes it)
        best = None
        for wall in walls2:
            length = math.dist(wall.start, wall.end)
            if length <= 1e-9:
                continue
            ux, uy = (wall.end[0] - wall.start[0]) / length, (wall.end[1] - wall.start[1]) / length
            half = float(wall.thickness) / 2.0
            ca = (c[0] - wall.start[0]) * ux + (c[1] - wall.start[1]) * uy
            cc = -(c[0] - wall.start[0]) * uy + (c[1] - wall.start[1]) * ux
            reach = DOOR_TAG_REACH_M if width is not None else half + CUT_SPAN_BLOCK_REACH_M
            if abs(cc) > reach or not (-0.3 <= ca <= length + 0.3):
                continue
            jambs = []
            for a, b in segs:
                d = math.dist(a, b)
                if d <= 1e-9:
                    continue
                cos = abs(((b[0] - a[0]) * ux + (b[1] - a[1]) * uy) / d)
                if cos > math.sin(math.radians(CUT_SPAN_JAMB_DEG)):
                    continue                    # not square across the wall
                pa = ((a[0] + b[0]) / 2.0 - wall.start[0]) * ux + ((a[1] + b[1]) / 2.0 - wall.start[1]) * uy
                c0 = -(a[0] - wall.start[0]) * uy + (a[1] - wall.start[1]) * ux
                c1 = -(b[0] - wall.start[0]) * uy + (b[1] - wall.start[1]) * ux
                lo, hi = max(min(c0, c1), -half), min(max(c0, c1), half)
                if hi - lo >= CUT_SPAN_JAMB_COVER * 2.0 * half and 0.0 <= pa <= length:
                    jambs.append(pa)
            jambs = sorted(set(round(j, 3) for j in jambs))
            for i, a1 in enumerate(jambs):
                for a2 in jambs[i + 1:]:
                    span = a2 - a1
                    if width is not None:
                        if abs(span - width) > CUT_SPAN_WIDTH_TOL_M or abs((a1 + a2) / 2.0 - ca) > \
                                width / 2.0 + CUT_SPAN_TAG_SHIFT_M:
                            continue
                    elif not (CUT_SPAN_BLOCK_W_M[0] <= span <= CUT_SPAN_BLOCK_W_M[1] and a1 - 0.05 <= ca <= a2 + 0.05
                              and abs(span - float(ev.get("size_m") or 0.0)) <= CUT_SPAN_BLOCK_TOL_M):
                        continue
                    mid = (a1 + a2) / 2.0
                    centre = (wall.start[0] + ux * mid, wall.start[1] + uy * mid)
                    # nothing read there yet: no opening on this wall line overlapping the span
                    if any(not o.virtual and abs(-(o.center[0] - wall.start[0]) * uy + (o.center[1] - wall.start[1])
                                                 * ux) <= half + 0.05
                           and abs(((o.center[0] - wall.start[0]) * ux + (o.center[1] - wall.start[1]) * uy) - mid)
                           < (float(o.width) + span) / 2.0 for o in out + added):
                        continue
                    score = abs(mid - ca) + abs(cc) * 0.1
                    if best is None or score < best[0]:
                        best = (score, wall, centre, span, ux, uy)
        if best is None:
            continue
        _score, wall, centre, span, ux, uy = best
        e = dict(ev)
        e.update(method="vector", confidence=0.8, rule="cut_span_door",
                 reason=f"{what} at a span of {span:.2f} m between two jamb lines across the wall, the lines along it "
                        f"the wall's section edge at the opening (no gap read): a door")
        hw = span / 2.0
        corners = [(centre[0] - ux * hw, centre[1] - uy * hw), (centre[0] + ux * hw, centre[1] + uy * hw)]
        box = [min(p[0] for p in corners), min(p[1] for p in corners), max(p[0] for p in corners),
               max(p[1] for p in corners)]
        if units_to_m:
            box = [v / units_to_m for v in box]
        added.append(OpeningItem(kind="door", width=round(span, 3), center=(round(centre[0], 4), round(centre[1], 4)),
                                 rotation_deg=round(math.degrees(math.atan2(uy, ux)) % 360.0, 3),
                                 box=[round(v, 3) for v in box], entity=str(e.get("entity") or "cut_span"),
                                 evidence=e, height=height, assumed=[] if height else ["height"],
                                 type_raw=what))
    return out + added if added else None


def _door_tags(ex, where: str, walls2: list, openings: list, texts_m: list, units_to_m: float,
               keep_width: bool = False, outline=None, strokes=()):
    """4 Nov 2026 (real07, user: "the entrance to the room is wrong door not recognized properly", "where is the
    entrance to the bus wc you missed the door"; lesson UL321): a door size tag ("80/210", width/height in cm; written
    along the leaf, so at any angle) is the door of the opening it labels within ``DOOR_TAG_REACH_M``: a door of that
    width and height, centred where the gap is; a gap read wider than the door keeps the rest as wall.

    Which tags: one on a door layer; one on a window or joinery layer that is door-like (``_door_like_tag``); and
    (6 Nov 2026, real10 C0035: the fire stair's '140/230' on the plain layer TEXT) a door-high one (>=
    ``DOOR_TAG_MIN_H_CM``, at most ``DOOR_TAG_MAX_W_CM`` wide) on a plain text layer.

    Which openings (12 Nov 2026, review B-OPN-01/02/04/08, B-r10-tag*, B-T1): the tags of a level are matched to the
    openings all at once, nearest pairs first (the distance from the tag to the opening's span), never in text order;
    one opening per tag and one tag per spot (doors within ``DOOR_TAG_COINCIDENT_M`` are one spot: two symbols there
    are logged, not both resized). A door of the tag's width uses the tag up; a door within ``DOOR_TAG_DOOR_W_M`` of it
    takes its size; a door further off is another door (real10's 0.43 m shaft boxes beside a '90/210'). A gap takes the
    tag unless it holds more than one such door (wider than ``DOOR_TAG_GAP_SHARE`` tag widths; a gap read narrower
    than its door keeps the tag: real07's 0.52 m gap of an '80/210'). A tag on a plain text layer decides door only where the drawing does not say window: never a gap holding
    a window's frame lines (``_window_content``) and never a gap in an outer wall (``_outer_opening``, the building's
    filled ``outline``: real18's 2.75 m facade window beside an '80/210', real10's '165/210' kitchen windows), where a
    door-high opening may be a window; the width alone decides nothing. A door-high tag on a door layer may take a
    drawn window of about its width (real16's shower doors read as windows), but only as the best match: the tag's own
    door, when read, is nearer. Returns the new openings or None."""
    from wenart.ingest.generic import layer_names as LN

    tags = []
    for t in texts_m:
        m = SIZE_TAG_RE.match(t.text or "")
        layer = (t.evidence[0].get("layer") if t.evidence else None)
        if not m:
            continue
        role = LN.layer_role(layer)
        w_cm, h_cm = int(m.group(1)), int(m.group(2))
        if h_cm < DOOR_TAG_LOW_H_CM:
            # 12 Nov 2026 (round-2 review, F6: real11's vent size '75/45' on a door layer made a 0.45 m high door): a
            # size under a door's height is a window's or a vent's, never a door's
            continue
        plain = role in DOOR_TAG_TEXT_ROLES
        if role == "door" or (role == "window" and _door_like_tag(t, w_cm, h_cm, openings)) \
                or (plain and h_cm >= DOOR_TAG_PLAIN_MIN_H_CM and w_cm <= DOOR_TAG_MAX_W_CM):
            # 6 Nov 2026 (real16 L1: the four shower rooms' '80/220' doors read as 0.68 m windows, their leaves' lines
            # in the wall taken for glass): a door-high tag on a door layer may take a drawn window of about its width
            over = role == "door" and h_cm >= DOOR_TAG_MIN_H_CM
            tags.append((t, w_cm / 100.0, h_cm / 100.0, over, plain))
    if not tags:
        return None
    by_id = {st.id: st for st in strokes or ()}
    pairs = []
    for ti, (t, width, height, over, plain) in enumerate(tags):
        c = Point((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0)
        for j, o in enumerate(openings):
            if o.virtual or o.kind not in DOOR_TAG_KINDS:
                continue
            w = float(o.width)
            gap = o.kind == "opening" or (o.kind == "window" and "gap" in str(o.type_raw or ""))
            if o.kind == "door":
                # 13 Nov 2026 (review REGX-1: real16's two '100/220' doors, read from their leaf lines alone as 1.78
                # and 1.67 m sliding doors, could no longer take their tags): a door narrower than the tag by more than
                # DOOR_TAG_DOOR_W_M is another door (real10's 0.43 m shaft boxes); a wider one only when it was read
                # from leaf lines without a swing (its width is the leaves', not the jambs')
                if w < width - DOOR_TAG_DOOR_W_M or (w > width + DOOR_TAG_DOOR_W_M and not _leaf_line_door(o)):
                    continue                                   # another door, not this tag's
            elif gap:
                if w > DOOR_TAG_GAP_SHARE * width:
                    continue                                   # it holds more than one such door
                if plain and w < width - DOOR_TAG_SAME_M:
                    # review B2-GEN-02 / B3C-06 (13 Nov 2026: up to 0.30 m was still let through): a plain tag widens
                    # no gap past its jambs, beyond a measuring tolerance
                    continue
                if plain and (_window_content(o) or _outer_opening(o, outline)):
                    continue                                   # the drawing may say window there
            elif not (over and abs(w - width) <= DOOR_TAG_WINDOW_WIDTH_M):
                continue                                       # a drawn window keeps its kind
            d = c.distance(_span(o))
            if d <= DOOR_TAG_REACH_M:
                # 12 Nov 2026 (real07 C0047, the user's correction: the '80/210' stood as near the Kat Kal. door's
                # span as the 1.56 m gap read over it, and the gap won by its place in the list): equally near, a
                # drawn door before a gap before a drawn window, then the nearer width. Review B2 FC-05 (real10's right
                # half: each tag written along its own door's leaf, nearer another door's span): a tag by a door's
                # drawn leaf or swing belongs to that door first
                rank = 0 if o.kind == "door" else (1 if gap else 2)
                leaf = _leaf_distance(c, o, by_id) if o.kind == "door" and by_id else float("inf")
                pairs.append([leaf <= DOOR_TAG_LEAF_M, leaf, d, rank, round(abs(w - width), 4), ti, j])
    # review B2 CB-6: 'equally near' is within DOOR_TAG_TIE_M of the tag's nearest pair, not a rounding bucket
    best: dict = {}
    for pr in pairs:
        if not pr[0]:
            best[pr[5]] = min(best.get(pr[5], float("inf")), pr[2])
    keyed = []
    for by_leaf, leaf, d, rank, wdiff, ti, j in pairs:
        if by_leaf:
            keyed.append((0, leaf, 0, wdiff, d, ti, j))
        else:
            near = best[ti] if d <= best[ti] + DOOR_TAG_TIE_M else d
            keyed.append((1, near, rank, wdiff, d, ti, j))
    pairs = sorted(keyed)
    out = list(openings)
    used_tags: set = set()
    taken: set = set()
    spots: list = []
    done, clashes = [], []
    for *_key, ti, j in pairs:
        if ti in used_tags or j in taken:
            continue
        t, width, height, over, plain = tags[ti]
        o = openings[j]
        spot = next((sp for sp in spots if math.dist(sp[0], tuple(o.center)) <= DOOR_TAG_COINCIDENT_M), None)
        if spot is not None:
            # (review B2 CB-4: a door symbol drawn twice does not use up the tag; it may still reach its own opening)
            clashes.append(f"{t.text.strip()} at the spot of {spot[1]} ({o.center[0]:.2f}, {o.center[1]:.2f}): "
                           f"two door symbols on one spot")
            continue
        used_tags.add(ti)
        taken.add(j)
        spots.append((tuple(o.center), t.text.strip()))
        if o.kind == "door" and abs(float(o.width) - width) <= DOOR_TAG_SAME_M + 1e-6:
            continue                                           # the tag's own door: used up
        ev = dict(t.evidence[0]) if t.evidence else {}
        ev.update(method="vector", confidence=0.9, rule="size_tag",
                  reason=f"the door size tag '{t.text.strip()}' (width/height in cm) beside the gap")
        new_w = float(o.width) if keep_width and float(o.width) > width and not _leaf_line_door(o) else width
        centre = tuple(o.center)
        assumed = [a for a in (o.assumed or []) if a != "height"]
        if o.kind != "door" and float(o.width) - new_w > DOOR_TAG_SAME_M:
            # 12 Nov 2026 (real07 C0047, the user's correction: the 80/210 door of Kat Kal. was put in the middle of
            # the 1.56 m gap read over it, 0.38 m off its jambs): a door in a gap wider than itself is hung at a jamb,
            # the one nearer its tag; with the tag over the gap's middle third it stays in the middle. The drawing
            # does not say where: the place is inferred (review B2-GEN-04)
            a, b = list(_span(o).coords)
            tc = ((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0)
            length = max(math.dist(a, b), 1e-9)
            along = ((tc[0] - a[0]) * (b[0] - a[0]) + (tc[1] - a[1]) * (b[1] - a[1])) / length / length
            if not 1.0 / 3.0 <= along <= 2.0 / 3.0:
                end, other = (a, b) if along < 0.5 else (b, a)
                f = new_w / 2.0 / length
                centre = (round(end[0] + (other[0] - end[0]) * f, 4), round(end[1] + (other[1] - end[1]) * f, 4))
                where_ = "hung at the jamb nearer the tag"
            else:
                where_ = "left in the middle (the tag stands over the gap's middle)"
            ev.update(method="inferred", confidence=0.6, rule="size_tag_jamb",
                      note=f"{where_}: the drawing does not show where in the {float(o.width):.2f} m gap the "
                           f"{new_w:.2f} m door hangs (the rest of the gap is wall)")
            assumed = assumed + ["position"]
        if o.kind == "door" and _leaf_line_door(o) and float(o.width) - new_w > DOOR_TAG_DOOR_W_M:
            ev.update(method="inferred", confidence=0.6, rule="size_tag_leaf_door",
                      note=f"read {float(o.width):.2f} m wide from its leaf lines; the tag gives {new_w:.2f} m, the "
                           f"door left at the middle of its leaves (the rest is wall)")
            assumed = assumed + ["position"]
        # 27 Nov 2026 (audit O2: real10's salon door d_L0_028, read from its swing ARC:14F743 and re-sized by its
        # '110/230', lost its drawn evidence here, so the door check took it for a door the tag placed and moved it into
        # a solid wall): a drawn door keeps its own symbol's evidence after the tag's
        extra = list(o.extra_evidence or [])
        if o.kind == "door" and isinstance(o.evidence, dict) and o.evidence.get("method") in ("vector", "raster") \
                and not o.evidence.get("rule") and o.evidence.get("entity"):
            extra = [dict(o.evidence)] + extra
        out[j] = dataclasses.replace(o, kind="door", width=round(new_w, 3), height=height, evidence=ev, center=centre,
                                     type_raw=f"door size tag {t.text.strip()}", assumed=assumed, extra_evidence=extra)
        done.append(f"{t.text.strip()} ({o.kind} {float(o.width):.2f} m -> door {new_w:.2f} m)")
    if clashes:
        ex.notes.append(f"{where}: door size tags on a spot that already took a tag: " + "; ".join(clashes[:8]))
    if done:
        ex.notes.append(f"{where}: {len(done)} door(s) set by their size tags: " + ", ".join(done[:12]))
        return out
    return None


STAIR_LINE_WALL_SHARE = 0.5      # 13 Nov 2026: a wall this much inside a stair's walking area is the stair's drawing ...
STAIR_LINE_WALL_SLACK_M = 0.10   # ... when it is no longer than the stair's footprint (plus this)
INTEGRITY_ENTER_M = 0.03         # ... and a wall along its treads entering it deeper than this loses that part
STAIR_LINE_BOX_M = 0.05          # ... its lines within the stair's footprint grown by this


def _tread_layers(f, strokes) -> set:
    """The layers a stair's tread lines are drawn on (pure): lines square to one of its flights (within 15 degrees),
    about the flight's width long, their middle inside that flight's band."""
    out = set()
    for fl in ((f.details or {}).get("stair") or {}).get("flights") or []:
        try:
            (sx, sy), (ex, ey), w = fl["start"][:2], fl["end"][:2], float(fl["width"])
        except (KeyError, TypeError, ValueError):
            continue
        n = math.hypot(ex - sx, ey - sy)
        if n < 1e-6:
            continue
        u = ((ex - sx) / n, (ey - sy) / n)
        band = LineString([(sx, sy), (ex, ey)]).buffer(w / 2.0, cap_style=2)
        for st in strokes or ():
            pts = list(getattr(st, "pts", []) or [])
            if len(pts) != 2:
                continue
            (ax, ay), (bx, by) = pts
            ln = math.hypot(bx - ax, by - ay)
            if not 0.5 * w <= ln <= 1.5 * w + 0.3 or abs(((bx - ax) * u[0] + (by - ay) * u[1]) / ln) > 0.26:
                continue
            if band.contains(Point((ax + bx) / 2.0, (ay + by) / 2.0)):
                out.add(st.layer)
    return out


def _piece_box(f):
    """The footprint rectangle of a piece (page metres; pure)."""
    cx, cy = f.center
    w, d = f.size[:2]
    a = math.radians(float(f.rotation_deg or 0.0))
    c, sn = math.cos(a), math.sin(a)
    return Polygon([(cx + x * c - y * sn, cy + x * sn + y * c)
                    for x, y in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2))])


def _stair_walk_area(f):
    """The walking area of a stair piece (page metres): its flights' bands from first to last riser line, the flight's
    width wide, and its landing; None without flights (pure)."""
    from shapely.geometry import LineString as _L
    from shapely.geometry import Polygon as _P
    st = (f.details or {}).get("stair") or {}
    parts = []
    for fl in st.get("flights") or []:
        try:
            line = _L([tuple(fl["start"][:2]), tuple(fl["end"][:2])])
            if line.length > 1e-6:
                parts.append(line.buffer(float(fl["width"]) / 2.0, cap_style=2))
        except (KeyError, TypeError, ValueError):
            continue
    land = st.get("landing")
    poly = land.get("polygon") if isinstance(land, dict) else land
    if isinstance(poly, (list, tuple)) and len(poly) >= 3:
        try:
            parts.append(_P([tuple(q[:2]) for q in poly]).buffer(0))
        except (TypeError, ValueError):
            pass
    return unary_union(parts) if parts else None


def _stair_line_walls(walls: list, stairs: list, openings: list, notes: list, where: str, strokes=()) -> list:
    """``walls`` without those a stair's drawing made (13 Nov 2026, coordinator after review B3: on real10 the tread,
    flight-side and well lines of the stairs, drawn on the plaster layer, were paired into walls standing in the
    flights): a wall at least ``STAIR_LINE_WALL_SHARE`` of whose rectangle lies in a stair's walking area
    (``_stair_walk_area``), no longer than the stair's footprint plus ``STAIR_LINE_WALL_SLACK_M``, holding no opening and
    no exterior wall, is dropped, one note each. A drawn wall cannot stand in a walking surface. Only a wall made of the
    stair's own lines: every line it was read from lies in the stair's footprint and on a layer the stair's own lines
    are drawn on (real11, real15, real18: a stair read across a real wall on another layer keeps that wall)."""
    by_id = {st.id: st for st in strokes or ()}
    areas = []
    for f in stairs:
        a = _stair_walk_area(f)
        if a is None or a.is_empty:
            continue
        ev = f.evidence if isinstance(f.evidence, dict) else {}
        layers = {by_id[i].layer for i in _expand_ids(ev.get("entity")) if i in by_id} | _tread_layers(f, strokes)
        box = _piece_box(f).buffer(STAIR_LINE_BOX_M, join_style=2)
        areas.append((f, a, max(float(v) for v in f.size[:2]) + STAIR_LINE_WALL_SLACK_M, layers, box))
    if not areas:
        return walls

    def own_lines(w, layers, box, every: bool = True) -> bool:
        ids = [i for i in _expand_ids(w.entity) if i in by_id and len(by_id[i].pts) >= 2]
        if not ids or not all(by_id[i].layer in layers for i in ids):
            return False
        inside = [box.contains(LineString(by_id[i].pts)) for i in ids]
        return all(inside) if every else any(inside)
    out, dropped, cut = [], [], []
    for w in walls:
        length = math.dist(w.start, w.end)
        keep = True
        if length > 1e-6 and not getattr(w, "exterior", False):
            rect = TP.wall_polygon(w)
            for f, area, longest, layers, box in areas:
                if rect.area <= 0 or not own_lines(w, layers, box, every=False):
                    continue
                if length > longest or not own_lines(w, layers, box) \
                        or rect.intersection(area).area < STAIR_LINE_WALL_SHARE * rect.area:
                    # a wall running along a flight's treads into the flight: the part in the stair is its tread lines
                    rest = _along_treads_rest(w, f, area)
                    if rest is not None:
                        cut.append(f"{w.entity} ({length:.2f} -> {math.dist(*rest):.2f} m)")
                        w.start, w.end = rest
                    continue
                if any(TP.wall_polygon(w).buffer(0.02).contains(Point(o.center)) for o in openings
                       if not getattr(o, "virtual", False)):
                    continue
                keep = False
                dropped.append(f"{w.entity} ({length:.2f} m, {float(w.thickness):.2f} m thick)")
                break
        if keep:
            out.append(w)
    if dropped:
        notes.append(f"{where}: {len(dropped)} wall(s) made of a stair's own lines (treads, flight sides, well) "
                     f"dropped: " + ", ".join(dropped[:12]))
    if cut:
        notes.append(f"{where}: {len(cut)} wall(s) running along a stair's treads into its flight shortened to the "
                     f"stair's edge: " + ", ".join(cut[:12]))
    return out


def _along_treads_rest(w, f, area):
    """The wall ``w``'s centre line without its part inside the stair's walking ``area``, as ``(start, end)``, when
    the wall runs along one of the stair's treads (square to a flight, within 10 degrees) and enters the area deeper
    than ``INTEGRITY_ENTER_M``; None otherwise (pure)."""
    from shapely.geometry import LineString as _L
    st = (f.details or {}).get("stair") or {}
    u = (w.end[0] - w.start[0], w.end[1] - w.start[1])
    n = math.hypot(*u)
    if n < 1e-6:
        return None
    u = (u[0] / n, u[1] / n)
    square = False
    for fl in st.get("flights") or []:
        try:
            a = (fl["end"][0] - fl["start"][0], fl["end"][1] - fl["start"][1])
        except (KeyError, TypeError):
            continue
        m = math.hypot(*a)
        if m > 1e-6 and abs(u[0] * a[0] / m + u[1] * a[1] / m) <= math.sin(math.radians(10.0)):
            square = True
    if not square:
        return None
    line = _L([tuple(w.start), tuple(w.end)])
    inside = line.intersection(area).length
    if inside <= INTEGRITY_ENTER_M:
        return None
    rest = line.difference(area)
    pieces = [g for g in getattr(rest, "geoms", [rest]) if g.geom_type == "LineString" and g.length >= 0.1]
    if not pieces:
        return None
    best = max(pieces, key=lambda g: g.length)
    (ax, ay), (bx, by) = best.coords[0], best.coords[-1]
    return (round(ax, 4), round(ay, 4)), (round(bx, 4), round(by, 4))


def _leaf_line_door(o) -> bool:
    """A door read from leaf lines drawn parallel to its wall without a swing arc (a sliding door by its geometry)."""
    note = str((o.evidence or {}).get("note") or "") if isinstance(o.evidence, dict) else ""
    return o.kind == "door" and o.operation == "sliding" and ("without a swing" in note
                                                              or o.operation_source == "geometry")


RECESS_MAX_M2 = 15.0
FACE_THROUGH_TOL_M = 0.03       # 12 Nov 2026: a wall-layer line this close to a gap's wall face runs along that face ...
FACE_THROUGH_ANGLE = 0.02       # ... parallel to the wall (sine of the angle) ...
FACE_THROUGH_END_M = 0.02       # ... and covering the gap to this much of its ends, on both faces: the gap is a wall
FACE_THROUGH_CROSS = 0.5        # 19 Nov 2026 (review A3, M6): a line ending on a face at this sine of angle or more crosses
#                                 it (a cross wall's face at a T-junction, a stair's line): the face may break there for
#                                 at most the host wall's thickness and still run through the gap


DOOR_ARC_R_M = (0.5, 1.3)       # 12 Nov 2026: a door leaf's swing radius ...
DOOR_ARC_REACH_M = 0.15         # ... its hinge (the arc's centre) this close to the gap's wall band ...
DOOR_CHORD_TOL_M = 0.05         # ... and its chord (hinge to the closed leaf's tip, along the wall) inside the gap
DOOR_WINDOW_SWEEP = (80.0, 100.0)   # on a door-and-window layer only a swing of about 90 degrees is a door's ...
DOOR_WINDOW_MIN_R = 0.6         # ... of a door's size (a 35-degree sash of 0.5 m is a casement window)
WINDOW_WORDS = ("PENCERE", "PENC", "WINDOW", "FENSTER", "FENETRE", "DOGRAMA", "VENTANA", "FINESTRA")
WINDOW_TAG_RE = re.compile(r"^\s*[PW]\s*\d{0,2}\s*[:\-]?\s*\d{2,3}\s*/\s*\d{2,3}\s*$", re.IGNORECASE)


def _door_window_name(names) -> bool:
    """A layer or block named for doors and windows together ('kapı-pencere', 'DOOR_WINDOW')."""
    folded = " ".join(B.fold_ascii(str(n or "")).upper() for n in names)
    return any(w in folded for w in WINDOW_WORDS)


def _swing(st, x0, y0, ux, uy, h):
    """``(s_hinge, s_tip)`` along a wall (origin x0, y0, direction ux, uy, half thickness h) of a door swing: the arc's
    centre and the end of the arc that lies on the wall (the closed leaf's tip); None when either is off the wall."""
    a = st.arc
    cx, cy = a["center"][:2]
    r = float(a["radius"])
    if abs(-(cx - x0) * uy + (cy - y0) * ux) > h + DOOR_ARC_REACH_M:
        return None
    ends = []
    for deg in (a.get("start_deg"), a.get("end_deg")):
        if deg is None:
            continue
        ex_, ey_ = cx + r * math.cos(math.radians(float(deg))), cy + r * math.sin(math.radians(float(deg)))
        ends.append((abs(-(ex_ - x0) * uy + (ey_ - y0) * ux), (ex_ - x0) * ux + (ey_ - y0) * uy))
    ends = [e for e in ends if e[0] <= h + DOOR_ARC_REACH_M]
    if not ends:
        return None
    s_h = (cx - x0) * ux + (cy - y0) * uy
    s_t = min(ends)[1]
    return (s_h, s_t) if abs(abs(s_t - s_h) - r) <= 0.2 * r else None


def _door_blocks_in_gaps(ex, where: str, walls2: list, openings: list, strokes_m: list, owned=(),
                         texts_m=(), file_rel: str = "", page_no=None, units_to_m: Optional[float] = None) -> list:
    """12 Nov 2026 (reviews of the reader targets; real15 F1: the kitchen door block's leaf and swing read as
    unclassified gap content, then as windows; round 2: borrowed swings made false doors on real21, real06, real09,
    real11): a door from a door leaf's swing in an unclassified gap, only when

    - no door already read stands in the gap (the gap stays as it is: the later steps decide between the two; real06's
      kitchen pass-through, its counter lines read as a sliding door, stays an opening);
    - the arc (``DOOR_ARC_R_M``, on a door layer or in a door block: ``layer_names`` role door) belongs to no opening
      already read (``owned``) and serves one gap only;
    - on a door-and-window layer it sweeps about 90 degrees with a door's radius (a sash is a window);
    - no window size tag (P / W and W/H) of its own stands by the gap (a tag speaks for its nearest opening);
    - its chord, from the hinge to the closed leaf's tip along the wall, lies inside the gap.

    The door is put on that chord (two chords meeting in the gap make one double door); the rest of the gap is read
    again from its lines (``openings.doors_in_gaps``: wall, window or an open rest). Never silent."""
    from wenart.ingest.generic import layer_names as LN

    arcs = []
    for st in strokes_m:
        a = st.arc
        if not a or not (DOOR_ARC_R_M[0] <= float(a.get("radius") or 0.0) <= DOOR_ARC_R_M[1]) or st.id in owned:
            continue
        names = [st.layer] + (str(st.block).split("/") if st.block else [])
        if not any(LN.layer_role(n) == "door" for n in names):
            continue
        if _door_window_name(names):
            # 19 Nov 2026 (review A3, A3C-5): counter-clockwise from start to end, so a quarter stored 270 -> 0 is 90
            sweep = (float(a.get("end_deg") or 0.0) - float(a.get("start_deg") or 0.0)) % 360.0
            if float(a["radius"]) < DOOR_WINDOW_MIN_R or not (DOOR_WINDOW_SWEEP[0] <= sweep <= DOOR_WINDOW_SWEEP[1]):
                continue
        arcs.append(st)
    tags = [((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0) for t in texts_m
            if WINDOW_TAG_RE.match(str(getattr(t, "text", "") or ""))]
    doors = [o for o in openings if o.kind == "door" and not getattr(o, "virtual", False)]
    # 13 Nov 2026 (round 3: real15's kitchen door lost its swing to the tag of the window beside it): a window size tag
    # speaks for the opening nearest to it only
    real = [o for o in openings if not getattr(o, "virtual", False)]

    def tag_reach(q, op) -> float:
        rot = math.radians(op.rotation_deg)
        ex_, ey_ = math.cos(rot), math.sin(rot)
        dx, dy = q[0] - op.center[0], q[1] - op.center[1]
        t = max(-float(op.width) / 2.0, min(float(op.width) / 2.0, dx * ex_ + dy * ey_))
        return math.hypot(dx - ex_ * t, dy - ey_ * t)

    owner = [min(real, key=lambda op: tag_reach(q, op)) if real else None for q in tags]
    used: set = set()
    out = []
    for o in openings:
        if o.kind != "opening" or getattr(o, "virtual", False) or getattr(o, "type_raw", None) != UNCLASSIFIED:
            out.append(o)
            continue
        hk = TP.host_wall(o, walls2)
        if hk is None:
            out.append(o)
            continue
        w = walls2[hk]
        (x0, y0), (x1, y1) = tuple(w.start), tuple(w.end)
        L = math.hypot(x1 - x0, y1 - y0)
        if L <= 0:
            out.append(o)
            continue
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        h = float(w.thickness) / 2.0
        c = (o.center[0] - x0) * ux + (o.center[1] - y0) * uy
        g0, g1 = c - float(o.width) / 2.0, c + float(o.width) / 2.0

        def along(q):
            return (q[0] - x0) * ux + (q[1] - y0) * uy

        def on_wall(q):
            return abs(-(q[0] - x0) * uy + (q[1] - y0) * ux) <= h + 0.05

        cover = 0.0
        for d in doors:
            if on_wall(d.center):
                a0, a1 = along(d.center) - float(d.width) / 2.0, along(d.center) + float(d.width) / 2.0
                cover += max(0.0, min(a1, g1) - max(a0, g0))
        if cover > 0:
            out.append(o)                               # a door already read in it: never a second door
            continue
        if any(owner[k] is o and math.dist(q, o.center) <= 1.2 for k, q in enumerate(tags)):
            out.append(o)                               # its own window size tag beside it: a window, not a door
            continue
        chords = []
        for st in arcs:
            if st.id in used:
                continue
            sw = _swing(st, x0, y0, ux, uy, h)
            if sw is None:
                continue
            a0, a1 = min(sw), max(sw)
            if a0 >= g0 - DOOR_CHORD_TOL_M and a1 <= g1 + DOOR_CHORD_TOL_M:
                chords.append((a0, a1, st))
        if not chords:
            out.append(o)
            continue
        chords.sort(key=lambda t: t[0])
        pick = [chords[0]]
        for ch in chords[1:]:                           # two leaves meeting in the gap: one double door
            if abs(ch[0] - pick[-1][1]) <= 0.15 and len(pick) < 2:
                pick.append(ch)
        d0, d1 = max(g0, pick[0][0]), min(g1, pick[-1][1])
        for _a0, _a1, st in pick:
            used.add(st.id)
        mid = (d0 + d1) / 2.0
        ids = ", ".join(st.id for _a, _b, st in pick)
        ev = dict(o.evidence) if isinstance(o.evidence, dict) else {}
        ev.update(rule="door_block_in_gap", confidence=0.8,
                  reason=f"door leaf swing(s) {ids} on a door layer, hinged in the gap: the door on the leaf's chord")
        door = dataclasses.replace(o, kind="door", width=round(d1 - d0, 3),
                                   center=(round(x0 + ux * mid, 4), round(y0 + uy * mid, 4)), evidence=ev,
                                   status="verified", type_raw=f"door block in gap ({ids})")
        door.operation, door.operation_source = ("double" if len(pick) == 2 else "swing"), "geometry"
        # 13 Nov 2026 (merge with reader B, the coordinator: one gap mechanism): the door takes its part of the gap and
        # the rest is read again from the lines over it (``openings.doors_in_gaps``: wall faces make wall, glass or a
        # sill a window, else an open rest marked ``rest_of``)
        pair = O.doors_in_gaps(walls2, [door, o], strokes_m, file_rel, page_no, units_to_m=units_to_m)
        got = pair if pair is not None else [door]
        out += got
        rest = [x for x in got if x is not door]
        ex.notes.append(f"{where}: gap {o.entity[:80]} ({float(o.width):.2f} m) holds the swing(s) {ids} hinged in it:"
                        f" a {d1 - d0:.2f} m {'double ' if len(pick) == 2 else ''}door on the leaf's chord; the rest of "
                        f"the gap read again from its lines: "
                        + (", ".join(f"{x.kind} {float(x.width):.2f} m" for x in rest) if rest else "wall"))
    return out


def _solid_linetype(name: Optional[str]) -> bool:
    """A stroke drawn solid: no linetype read (PDF, raster), or CONTINUOUS / BYLAYER / BYBLOCK / an empty name."""
    return not name or str(name).strip().upper() in ("CONTINUOUS", "BYLAYER", "BYBLOCK", "SOLID", "STANDARD")


FACE_THROUGH_IN_M = (0.04, 0.06)  # 19 Nov 2026 (review A4, POD-A4-03): a face line may lie this far inside the face ...
FACE_THROUGH_IN_SHARE = 0.6       # ... at most this share of the half-thickness in (the masonry under a plaster coat)


def _on_face(d: float, h: float) -> bool:
    """19 Nov 2026 (review A4, POD-A4-03: real09 L2's masonry line, 3 cm inside the plaster face, stood 0.0301 m off the
    face and the gap stayed while L0's, at 0.0299 m, closed): a line ``d`` from the wall's axis towards one face (the
    face at ``h``) runs along that face when it lies within ``FACE_THROUGH_TOL_M`` outside it or inside the wall by up
    to its plaster coat and masonry face (``FACE_THROUGH_IN_M``, ``FACE_THROUGH_IN_SHARE`` of ``h``): a band whose edges
    are far from the usual 3 cm coat, so a sub-millimetre shift of the axis changes nothing (pure)."""
    inner = max(FACE_THROUGH_IN_M[0], min(FACE_THROUGH_IN_M[1], FACE_THROUGH_IN_SHARE * h))
    return h - inner <= d <= h + FACE_THROUGH_TOL_M


def _faces_through_gaps(ex, where: str, walls2: list, openings: list, strokes_m: list) -> tuple[list, list]:
    """12 Nov 2026 (review of the reader targets, real15 F2: the solid wall between the living room and the bathroom,
    drawn as two unbroken lines on its masonry and its plaster layer, became a 2.0 m gap holding the bath's block): an
    unclassified or empty gap (no door, no window, not inferred) across which solid straight lines of a wall or
    plaster layer (``layer_names.layer_role``; not a structure layer, whose beam lines may cross an opening) run along
    both faces of its wall (``FACE_THROUGH_TOL_M``) and cover it end to end is no gap: a wall piece of its host's
    thickness fills it (real10 L0: the fire stair's lines touching the hall wall cut it). Never silent.

    19 Nov 2026 (review A3, M6: real15 L0's 1.17 m gap between the kitchen and the stair foot, its bottom face broken
    only at the T-junction of the kitchen's cross wall and its top face only where the stair's diagonal meets it): a
    face still runs through across a break no longer than the host wall's thickness where a line crossing the face
    (``FACE_THROUGH_CROSS``: a cross wall's face, a stair's line, on any layer) ends on it."""
    from wenart.ingest.generic import layer_names as LN

    crossing = []                    # (a, b) of every straight piece that may end on a face (any layer)
    for st in strokes_m:
        if st.arc is None and len(st.pts) >= 2:
            pts = list(st.pts) + ([st.pts[0]] if st.closed else [])
            crossing += [(a, b) for a, b in zip(pts, pts[1:]) if math.dist(a, b) > 0.05]
    segs = []
    for st in strokes_m:
        # the masonry and plaster face lines, drawn solid (a beam or lintel over an opening is drawn on a structure
        # layer or dashed: never a reason to close the opening)
        if st.arc is not None or len(st.pts) < 2 or LN.layer_role(st.layer) not in ("wall", "plaster") \
                or not _solid_linetype(getattr(st, "linetype", None)):
            continue
        pts = list(st.pts) + ([st.pts[0]] if st.closed else [])
        segs += [(a, b, st) for a, b in zip(pts, pts[1:]) if math.dist(a, b) > 0.05]
    if not segs:
        return walls2, openings
    filled, keep = [], []
    cross_tree = None                # built on the first gap that needs it
    for o in openings:
        ev = o.evidence if isinstance(o.evidence, dict) else {}
        if o.kind != "opening" or getattr(o, "virtual", False) or ev.get("method") == "inferred" or \
                ev.get("rule") in ("wide_gap", "glazed_run", "glazed_facade", "mirror_twin", "no_glass"):
            keep.append(o)
            continue
        hk = TP.host_wall(o, walls2)
        if hk is None:
            keep.append(o)
            continue
        w = walls2[hk]
        (x0, y0), (x1, y1) = tuple(w.start), tuple(w.end)
        L = math.hypot(x1 - x0, y1 - y0)
        if L <= 0:
            keep.append(o)
            continue
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        nx, ny = -uy, ux
        c = (o.center[0] - x0) * ux + (o.center[1] - y0) * uy
        g0, g1 = c - float(o.width) / 2.0 + FACE_THROUGH_END_M, c + float(o.width) / 2.0 - FACE_THROUGH_END_M
        h = float(w.thickness) / 2.0
        covered, face_ids = {}, []
        for side in (1.0, -1.0):
            spans = []
            for a, b, st in segs:
                da = (a[0] - x0) * nx + (a[1] - y0) * ny
                db = (b[0] - x0) * nx + (b[1] - y0) * ny
                lab = math.dist(a, b)
                cross = abs(((b[0] - a[0]) * nx + (b[1] - a[1]) * ny) / lab)
                if cross > FACE_THROUGH_ANGLE or not _on_face(side * (da + db) / 2.0, h):
                    continue
                sa = (a[0] - x0) * ux + (a[1] - y0) * uy
                sb = (b[0] - x0) * ux + (b[1] - y0) * uy
                spans.append((min(sa, sb), max(sa, sb)))
                if min(sa, sb) < g1 and max(sa, sb) > g0:
                    face_ids.append(f"{st.id} ({st.layer})")
            # 19 Nov 2026 (review A3, M6): where crossing lines end on this face inside the gap
            ends = []
            if cross_tree is None:
                from shapely import STRtree
                from shapely.geometry import LineString as _LS
                cross_tree = STRtree([_LS([a, b]) for a, b in crossing]) if crossing else False
            near_gap = []
            if cross_tree:
                pa = (x0 + ux * (g0 - 2 * h) + nx * side * h, y0 + uy * (g0 - 2 * h) + ny * side * h)
                pb = (x0 + ux * (g1 + 2 * h) + nx * side * h, y0 + uy * (g1 + 2 * h) + ny * side * h)
                from shapely.geometry import LineString as _LS
                near_gap = [crossing[i] for i in cross_tree.query(_LS([pa, pb]).buffer(FACE_THROUGH_TOL_M))]
            for a, b in near_gap:
                lab = math.dist(a, b)
                if abs(((b[0] - a[0]) * nx + (b[1] - a[1]) * ny) / lab) < FACE_THROUGH_CROSS:
                    continue
                for q in (a, b):
                    dq = (q[0] - x0) * nx + (q[1] - y0) * ny
                    sq = (q[0] - x0) * ux + (q[1] - y0) * uy
                    if _on_face(side * dq, h) and g0 - 2 * h <= sq <= g1 + 2 * h:
                        ends.append(sq)
            at = g0
            for s0, s1 in sorted(spans):
                if s0 <= at + 0.005 or (s0 - at <= 2 * h + 1e-6 and s1 > at
                                        and any(at - FACE_THROUGH_TOL_M <= e <= s0 + FACE_THROUGH_TOL_M for e in ends)):
                    at = max(at, s1)
            covered[side] = at >= g1
        if all(covered.values()) and g1 > g0:
            ca, cb = c - float(o.width) / 2.0, c + float(o.width) / 2.0
            spans_gap = ca >= -1e-6 and cb <= L + 1e-6          # the host's run already covers the gap
            if not spans_gap:
                filled.append(dataclasses.replace(w, start=(round(x0 + ux * ca, 4), round(y0 + uy * ca, 4)),
                                                  end=(round(x0 + ux * cb, 4), round(y0 + uy * cb, 4))))
            # 12 Nov 2026 (round-2 review, F5 / G7): the wall carries the correction: the rule, the reason, the face lines
            # and the gap it closed (the run's wall already spans the gap: no second piece over it)
            label = {"by": "code", "stage": "reading", "rule": "faces_through_gap",
                     "reason": "the wall's solid masonry and plaster face lines run through the gap on both faces: a "
                               "wall, not an opening",
                     "evidence": sorted(set(face_ids))[:12],
                     "before": {"opening": o.entity, "center": [round(v, 4) for v in o.center],
                                "width": round(float(o.width), 3)}}
            prev = getattr(w, "corrected_by_ai", None)
            if isinstance(prev, dict):
                label = dict(prev, also=list(prev.get("also") or []) + [label])
            w.corrected_by_ai = label
            ex.notes.append(f"{where}: gap {o.entity[:80]} ({float(o.width):.2f} m) at "
                            f"({o.center[0]:.2f}, {o.center[1]:.2f}) has its wall's face lines running through it on "
                            f"both faces ({', '.join(sorted(set(face_ids))[:4])}): a wall, not an opening "
                            f"(corrected_by_ai, faces_through_gap)")
            continue
        keep.append(o)
    return walls2 + filled, keep




def _empty_gap(o) -> bool:
    """An opening the openings reader found nothing in (no door, no window): a plain ``opening`` of a wall run's gap
    (real09: one recess's gap noted 'unclassified gap content', its mirror twin's not), never one of the bridges the
    reading inferred (wide gaps, glazed runs, facades, mirror twins)."""
    ev = o.evidence if isinstance(o.evidence, dict) else {}
    return o.kind == "opening" and not getattr(o, "virtual", False) and ev.get("method") != "inferred" \
        and ev.get("rule") not in ("wide_gap", "glazed_run", "glazed_facade", "mirror_twin")


def _open_twin(face, out_pt, axis, faces, outline) -> Optional[str]:
    """The mirror axis (``"x = 12.34"``) when ``face`` lies on one side of the plan's mirror ``axis`` and its mirror
    image is open air: no face covers more than a fifth of it and the mirror of the outside point is outside too;
    else None."""
    if axis is None:
        return None
    from shapely import affinity

    kind, v = axis
    lo, hi = (face.bounds[0], face.bounds[2]) if kind == "x" else (face.bounds[1], face.bounds[3])
    if lo < v < hi:
        return None                                   # it straddles the axis: no twin of its own
    mf = affinity.scale(face, xfact=-1.0 if kind == "x" else 1.0, yfact=-1.0 if kind == "y" else 1.0,
                        origin=(v, 0.0) if kind == "x" else (0.0, v))
    if any(f.intersection(mf).area > 0.2 * face.area for f in faces):
        return None
    q = Point(2.0 * v - out_pt.x, out_pt.y) if kind == "x" else Point(out_pt.x, 2.0 * v - out_pt.y)
    if outline.contains(q):
        return None
    return f"{kind} = {v:.2f}"


def _open_recesses(ex, where: str, walls2: list, openings: list, blocks: list, level_id):
    """3 Nov 2026 (real09, user: "wait a light well is not correct, there is not wall in the purple section"): an empty
    gap (``_empty_gap``) in a wall that the outside reaches on one side and, on the other, a face with no label, no
    other door or opening, at most ``RECESS_MAX_M2``, that windows of other rooms open onto: a recess of the facade
    (the bathroom's and the WC's windows face the open air). The wall is split at the gap, the gap is no opening, the
    recess is outside. Never silent: each one is noted with the gap's entities."""
    import math as _m

    faces = TP.faces(walls2, openings)
    if not faces:
        return None
    outline = TP.building_outline(walls2, openings)
    anchors = [Point(b.anchor) for b in blocks]
    # 3 Nov 2026 (real10, user: "this section is still wrong should be similar as the mirror"): on a plan of two
    # mirrored halves, the recess's twin decides when its own window could not be read
    axis = _halves(ex, walls2, openings, blocks, level_id, "recess twins")
    splits, pending, opened = [], [], []
    for k, o in enumerate(openings):
        if not _empty_gap(o):
            continue
        hk = TP.host_wall(o, walls2)
        if hk is None:
            continue
        w = walls2[hk]
        (x0, y0), (x1, y1) = tuple(w.start), tuple(w.end)
        L = _m.hypot(x1 - x0, y1 - y0)
        if L <= 0:
            continue
        nx, ny = -(y1 - y0) / L, (x1 - x0) / L
        d = float(w.thickness) / 2.0 + 0.15
        sides = [Point(o.center[0] + nx * d, o.center[1] + ny * d), Point(o.center[0] - nx * d, o.center[1] - ny * d)]
        inner = [next((f for f in faces if f.contains(q)), None) for q in sides]
        if sum(1 for f in inner if f is not None) != 1:
            continue
        face = next(f for f in inner if f is not None)
        out_pt = sides[inner.index(None)]
        if outline.contains(out_pt) or face.area > RECESS_MAX_M2 or any(face.contains(a) for a in anchors):
            continue
        others = [p for j, p in enumerate(openings) if j != k and not getattr(p, "virtual", False)]
        near = [p for p in others if (TP.opening_polygon(p, walls2) or Point(p.center).buffer(0.01)).distance(face) <= 0.02]
        if any(p.kind != "window" for p in near) or not any(p.kind == "window" for p in near):
            if axis is not None and not any(p.kind == "door" for p in near):
                pending.append((k, hk, o, face, out_pt, sum(1 for p in near if p.kind == "window")))
            continue
        splits.append((k, hk, o, face.area, sum(1 for p in near if p.kind == "window"), None))
        opened.append(face)
    # the twins' pass: a recess whose own windows could not be read opens when its mirror twin is open air, the twins
    # this pass opened counting as open (both are closed faces before it)
    shut = [f for f in faces if not any(f.equals(g) for g in opened)]
    for k, hk, o, face, out_pt, nwin in pending:
        twin = _open_twin(face, out_pt, axis, shut, outline)
        if twin is not None:
            splits.append((k, hk, o, face.area, nwin, twin))
    if not splits:
        return None
    new_walls, drop = list(walls2), set()
    for k, hk, o, area, nwin, twin in splits:
        w = new_walls[hk]
        (x0, y0), (x1, y1) = tuple(w.start), tuple(w.end)
        L = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        t = (o.center[0] - x0) * ux + (o.center[1] - y0) * uy
        a, b = t - o.width / 2.0, t + o.width / 2.0
        pieces = []
        for s0, s1 in ((0.0, a), (b, L)):
            if s1 - s0 >= 0.02:
                piece = dataclasses.replace(w, start=(round(x0 + ux * s0, 4), round(y0 + uy * s0, 4)),
                                            end=(round(x0 + ux * s1, 4), round(y0 + uy * s1, 4)))
                pieces.append(piece)
        new_walls[hk] = pieces[0] if pieces else None
        new_walls += pieces[1:]
        drop.add(k)
        why = (f"{nwin} window(s) of other rooms open onto it" if twin is None else
               f"its mirror twin about {twin} is open air (the mirrored half reads the recess open)")
        ex.notes.append(f"{where}: the {o.width:.2f} m gap {o.entity} in an outer wall holds no door or window and the "
                        f"{area:.2f} m2 space behind it has no door and {why}: a recess of the facade, open air (the "
                        f"wall is split there, no opening; corrected_by_ai)")
    new_walls = [w for w in new_walls if w is not None]
    new_open = [o for j, o in enumerate(openings) if j not in drop]
    bw, site, sw = TP.split_plot(new_walls, new_open, blocks, level_id=level_id)
    idx = {o["index"] for o in site["openings"]}
    b_open = [o for j, o in enumerate(new_open) if j not in idx]
    return new_walls, new_open, bw, site, sw, b_open, TP.outer_loop_problem(bw, b_open)


RECESS_CHAIN_MAX_M2 = 15.0      # 4 Nov 2026: a recess of several faces together at most this large ...
RECESS_MAX_WIDTH_M = 3.0        # ... each face at most this wide (a slot or light well, not a room)
RECESS_WINDOW_MAX_M = 2.0       # a gap from a labelled room onto it this narrow, with lines in it, is a window
UNCLASSIFIED = "unclassified gap content"
RECESS_STACK_M = 0.05           # gaps of walls stacked this close (a slit the wall union closes) touch each other
RECESS_CONTENT_MIN_M = 0.2      # a drawn line this long inside a face is content ...
RECESS_CONTENT_MAX = 4          # ... and this many of them make a face no recess ...
RECESS_CONTENT_INSET_M = 0.25   # ... counted this far in from its edge (fixtures and treads stand in it, frames at it)


def _gap_fixture(p, by_id: dict) -> Optional[str]:
    """12 Nov 2026 (review of the reader targets, real15 F1 / F2: a door block's leaf and swing, and a bath's block,
    in two gaps were made 'windows onto the open recess'): why an unclassified gap's content is no window: a piece of a
    door layer or block (its leaf, its swing), or only fixtures (sanitary or furniture pieces, or an arc) with no
    window or glass line among them (``layer_names.layer_role``; real10's slot windows hold a counter's edge beside
    their frame lines and stay windows); None when it may be a window's lines (the ids its note lists)."""
    from wenart.ingest.generic import layer_names as LN

    note = str((p.evidence if isinstance(p.evidence, dict) else {}).get("note") or "")
    if not note.startswith(UNCLASSIFIED):
        return None
    ids = [t.strip() for t in note[len(UNCLASSIFIED) + 1:].split("(")[0].replace(" ...", "").split(",") if t.strip()]
    fixture, glazed = None, False
    for i in ids:
        st = by_id.get(i)
        if st is None:
            if i.startswith("ARC:"):
                fixture = fixture or f"an arc ({i})"
            continue
        roles = {LN.layer_role(n) for n in [st.layer] + (str(st.block).split("/") if st.block else [])}
        if "door" in roles:
            return f"a door piece ({i})"
        if roles & {"window", "glass"}:
            glazed = True
        elif roles & {"sanitary", "furniture"}:
            fixture = fixture or f"a {sorted(roles & {'sanitary', 'furniture'})[0]} piece ({i})"
        elif st.arc is not None:
            fixture = fixture or f"an arc ({i})"
    return None if glazed else fixture


def _gap_faces(o, walls2: list, faces: list):
    """The faces on both sides of an opening's wall (None outside every face), or None without a host wall."""
    hk = TP.host_wall(o, walls2)
    if hk is None:
        return None
    w = walls2[hk]
    (x0, y0), (x1, y1) = tuple(w.start), tuple(w.end)
    L = math.hypot(x1 - x0, y1 - y0)
    if L <= 0:
        return None
    nx, ny = -(y1 - y0) / L, (x1 - x0) / L
    d = float(w.thickness) / 2.0 + 0.12
    pts = [Point(o.center[0] + nx * d, o.center[1] + ny * d), Point(o.center[0] - nx * d, o.center[1] - ny * d)]
    return hk, pts, [next((f for f in faces if f.contains(q)), None) for q in pts]


def _open_recess_chains(ex, where: str, walls2: list, openings: list, blocks: list, level_id, strokes: list = ()):
    """4 Nov 2026 (lesson UL313, real10: "These 2 oda should not exist and that 2 area should be outside"): a slot in
    the facade between two flats' rooms, 1.80 x 5.40 m, open to the sky; the rooms' walls on its two sides line up, so
    each line was read as one wall across the slot with a 1.80 m gap, and the slot as a chain of closed faces; the
    shower rooms' windows onto it held lines no window rule read. From a plain gap in an outer wall, the faces reached
    through plain gaps are a recess when each has no label and no door and is at most ``RECESS_MAX_WIDTH_M`` wide, all
    together at most ``RECESS_CHAIN_MAX_M2``, and every other opening onto them comes from a labelled room as a window
    or a gap with lines in it (an empty gap from a room is a doorway: no recess) - at least one. The walls are split
    at the chain's gaps (no openings) and the rooms' gaps onto it are windows. Never silent."""
    faces = TP.faces(walls2, openings)
    if not faces:
        return None
    outline = TP.building_outline(walls2, openings)
    anchors = [Point(b.anchor) for b in blocks]

    def labelled(f) -> bool:
        return any(f.contains(a) for a in anchors)

    # a recess holds nothing drawn but the notation (real10's fire stair below its flight: treads and a landing behind a
    # facade gap, no door, no label, is no recess)
    from wenart.ingest.generic import axes as AX
    notation = AX.notation_ids(list(strokes)) if strokes else set()
    marks = []
    for st in strokes or []:
        if st.id in notation or not st.pts or len(st.pts) < 2:
            continue
        xs, ys = [q[0] for q in st.pts], [q[1] for q in st.pts]
        if max(max(xs) - min(xs), max(ys) - min(ys)) >= RECESS_CONTENT_MIN_M:
            marks.append(Point((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0))

    def drawn_in(f) -> bool:
        inner = f.buffer(-RECESS_CONTENT_INSET_M)            # window frames at its edge are no content
        return not inner.is_empty and sum(1 for m in marks if inner.contains(m)) >= RECESS_CONTENT_MAX

    def narrow(f) -> bool:
        r = f.minimum_rotated_rectangle
        if r.geom_type != "Polygon":
            return True
        c = list(r.exterior.coords)
        return min(math.dist(c[0], c[1]), math.dist(c[1], c[2])) <= RECESS_MAX_WIDTH_M

    by_id = {st.id: st for st in strokes or []}

    polys = {}
    for j, p in enumerate(openings):
        if not getattr(p, "virtual", False):
            polys[j] = TP.opening_polygon(p, walls2) or Point(p.center).buffer(0.05)
    rim = outline.exterior if hasattr(outline, "exterior") else outline.boundary
    done_gaps: set = set()
    chains = []
    for k, o in enumerate(openings):
        if k in done_gaps or k not in polys or not _empty_gap(o) or polys[k].distance(rim) > 0.05:
            continue
        # the graph of gaps and faces that touch (stacked walls a few cm apart: their gaps touch each other)
        chain, gaps, windows, ok, why = [], {k}, set(), True, ""

        queue = [("g", k)]
        while queue and ok:
            kind, x = queue.pop()
            if kind == "g":
                gp = polys[x]
                for f in faces:
                    if f.distance(gp) > 0.02 or any(f.equals(c) for c in chain):
                        continue
                    if labelled(f) or f.area > RECESS_MAX_M2 or drawn_in(f):     # a room (its fixtures drawn)
                        p = openings[x]
                        fixture = _gap_fixture(p, by_id) if p.kind != "window" else None
                        if p.kind == "window" or (getattr(p, "type_raw", None) == UNCLASSIFIED
                                                  and p.width <= RECESS_WINDOW_MAX_M and fixture is None):
                            windows.add(x)
                            gaps.discard(x)
                            continue
                        ok, why = False, f"room {f.area:.2f} gap {x} {openings[x].kind} {getattr(openings[x], 'type_raw', None)} w {openings[x].width:.2f}"
                        break
                    if not narrow(f):
                        ok, why = False, f"face {f.area:.2f} narrow {narrow(f)} drawn {drawn_in(f)} at {[round(v, 2) for v in f.bounds]} n {sum(1 for m in marks if f.buffer(-0.05).contains(m))}"
                        break
                    chain.append(f)
                    queue.append(("f", f))
                if not ok:
                    break
                for j, q in polys.items():
                    if j not in gaps and j not in windows and _empty_gap(openings[j]) and q.distance(gp) <= RECESS_STACK_M:
                        gaps.add(j)
                        queue.append(("g", j))
            else:
                for j, q in polys.items():
                    if j in gaps or j in windows or q.distance(x) > 0.02:
                        continue
                    p = openings[j]
                    if p.kind == "door":
                        ok, why = False, f"door {j}"
                        break
                    if p.kind == "window" or _empty_gap(p):
                        gaps.add(j)
                        queue.append(("g", j))
        bad = [j for j in gaps if not _empty_gap(openings[j])]
        if not ok or bad or not windows or not chain or sum(f.area for f in chain) > RECESS_CHAIN_MAX_M2:
            continue
        done_gaps |= gaps
        chains.append((chain, gaps, windows))
    if not chains:
        return None
    # split every wall at the chain's gaps
    cuts: dict = {}
    for _chain, gaps, _w in chains:
        for j in gaps:
            hk = TP.host_wall(openings[j], walls2)
            if hk is not None:
                cuts.setdefault(hk, []).append(openings[j])
    new_walls = list(walls2)
    for hk, ops in cuts.items():
        w = walls2[hk]
        (x0, y0), (x1, y1) = tuple(w.start), tuple(w.end)
        L = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        spans = sorted(((o.center[0] - x0) * ux + (o.center[1] - y0) * uy - o.width / 2.0,
                        (o.center[0] - x0) * ux + (o.center[1] - y0) * uy + o.width / 2.0) for o in ops)
        pieces, at = [], 0.0
        for a, b in spans + [(L, L)]:
            if a - at >= 0.02:
                pieces.append(dataclasses.replace(w, start=(round(x0 + ux * at, 4), round(y0 + uy * at, 4)),
                                                  end=(round(x0 + ux * a, 4), round(y0 + uy * a, 4))))
            at = max(at, b)
        new_walls[hk] = pieces[0] if pieces else None
        new_walls += pieces[1:]
    drop = set().union(*(g for _c, g, _w in chains))
    for chain, gaps, windows in chains:
        for j in windows:
            p = openings[j]
            if p.kind != "window":
                p.kind = "window"
                if isinstance(p.evidence, dict):
                    p.evidence = dict(p.evidence, note=(str(p.evidence.get("note") or "") + "; a window onto the open "
                                                        "recess (UL313)").lstrip("; "))
        ex.notes.append(f"{where}: {len(chain)} face(s) of {sum(f.area for f in chain):.2f} m2 reached from the facade "
                        f"through {len(gaps)} plain gap(s) ({', '.join(openings[j].entity for j in sorted(gaps))[:200]}) "
                        f"have no label and no door and {len(windows)} window(s) of rooms open onto them: a recess of "
                        f"the facade, open air (the walls are split at the gaps, no openings; corrected_by_ai, UL313)")
    new_walls = [w for w in new_walls if w is not None]
    new_open = [o for j, o in enumerate(openings) if j not in drop]
    bw, site, sw = TP.split_plot(new_walls, new_open, blocks, level_id=level_id)
    idx = {o["index"] for o in site["openings"]}
    b_open = [o for j, o in enumerate(new_open) if j not in idx]
    return new_walls, new_open, bw, site, sw, b_open, TP.outer_loop_problem(bw, b_open)


MIRROR_MAX_NEW_WALLS = 3        # mirror twins differ by at most this many walls the other half draws
CORE_KEEP_OUT_M = 3.0           # no mirror fix within this of a lift label (the core: lift and stair, not mirrored)


def _halves(ex, walls: list, openings: list = (), blocks: list = (), level_id=None, by: str = "",
            min_share: Optional[float] = None) -> Optional[tuple]:
    """Whether the plan is two mirrored halves (``mirror.halves``, the one decision every mirror rule uses: outdoor
    outlines and guard, recess twins, mirror seeds, the mirror fixes, the separators), made on the walls the asking
    rule applies it to, with the openings and labels it has. 5 Nov 2026 (review: a decision made on the first rule's
    walls, before the facade closure, the recesses and the outline closure, was stale at the mirror step): the cache is
    per identical input (the walls' entities, ends and thicknesses, the labels' texts and points, the openings' kinds,
    centres and widths); every decision is listed in ``ex.report["mirror"]``. Without labels the label rule is
    skipped, and the note says so. Returns the axis or None. ``min_share``: the walls' overlap the decision needs
    (``mirror.halves``; default ``facade.MIRROR_FIX_SHARE``), part of the cache key."""
    import hashlib

    from wenart.ingest.generic import mirror as MR

    key = hashlib.sha1(repr((
        [(str(w.entity), round(float(w.start[0]), 3), round(float(w.start[1]), 3), round(float(w.end[0]), 3),
          round(float(w.end[1]), 3), round(float(w.thickness), 3)) for w in walls],
        sorted((str(getattr(b, "name", "")), round(float(b.anchor[0]), 3), round(float(b.anchor[1]), 3))
               for b in blocks or ()),
        sorted((str(o.kind), round(float(o.center[0]), 3), round(float(o.center[1]), 3), round(float(o.width), 3))
               for o in openings or ()), min_share)).encode()).hexdigest()
    cache = ex.report.setdefault("mirror_cache", {})
    if key not in cache:
        h = MR.halves(walls, list(openings or []), list(blocks or []), level_id, min_share) if walls else {
            "axis": None, "note": None}
        cache[key] = list(h["axis"]) if h.get("axis") else None
        row = dict(h, axis=cache[key], by=by, walls=len(walls))
        if not blocks:
            row["labels"] = "not given: the label rule was skipped"
        ex.report.setdefault("mirror", []).append(row)
        if h.get("note"):
            ex.notes.append(f"mirror check ({by or 'a rule'}, {len(walls)} walls"
                            + ("" if blocks else ", no labels: the label rule skipped") + f"): {h['note']}")
    return tuple(cache[key]) if cache[key] else None


def _mirror_consistency(ex, where: str, walls2: list, openings: list, blocks: list, level_id, site_warnings: list,
                        problem: Optional[str], strokes: Optional[list] = None):
    """The mirror fixes of a plan of two mirrored halves (``mirror.consistency``), step by step (thickness, inferred
    walls, missing walls, openings): a step that changes a drawn wall (thickness, an inferred wall onto its twin's
    line) is kept when more rooms pair as mirror images, one that copies a missing wall or an opening of the twin when
    no fewer pair; always with no labelled room left open, the outer walls closed and at most
    ``MIRROR_MAX_NEW_WALLS`` walls copied. 3 Nov 2026 (real10's 1st basement: six walls read 0.5-0.9 m
    thick on one half, a missing wall and seven openings; together they paired one room fewer and none was kept)."""
    from wenart.ingest.generic import mirror as MR

    # 5 Nov 2026: the mirror decision on the walls the fixes apply to (``_halves``: the layout inside the shell is
    # mirrored too); ``strokes`` (the page's lines) let the openings step see drawn solid wall
    axis = _halves(ex, walls2, openings, blocks, level_id, "mirror fixes")
    if axis is None:
        return None
    before = MR.mirrored_face_pairs(walls2, openings, axis)
    base_unclosed = _unclosed(site_warnings)
    # 3 Nov 2026 (real10, user: "core stairs and elevators and that section is shaft usually": the lift shaft's wall
    # was copied into the stair beside it): the core around a lift label is not mirrored
    keep_out = MR.core_keep_out(blocks)
    kept_steps: list = []
    best = None
    notes = []
    for step in MR.STEPS:
        res = MR.consistency(walls2, openings, axis, steps=tuple(kept_steps + [step]), keep_out=keep_out,
                             strokes=strokes)
        if res is None:
            continue
        w5, o5, log = res
        # this step's own lines (the log holds the kept steps' lines too): only refusals keep nothing
        own = [e for e in log if e not in (best[7] if best else [])]
        refused = [e for e in own if str(e).startswith("refused")]
        if len(refused) == len(own):
            notes.extend(r for r in refused if r not in notes)
            continue
        # 3 Nov 2026 (the regression set: real03, a block of different flat types (1+1 A1, A2, B, 2+1) in a symmetric
        # shell, got 16 walls and 7 doors copied from one flat type into the other): mirror twins differ by a few
        # slips (real09: at most one wall); halves that need more walls copied are different layouts
        new_walls = sum(1 for e in log if str(e).startswith("wall inferred:mirror_twin"))
        if new_walls > MIRROR_MAX_NEW_WALLS:
            notes.append(f"{step}: the halves differ by {new_walls} walls (over {MIRROR_MAX_NEW_WALLS}): different "
                         f"layouts, not mirror twins")
            if step == "missing":
                ex.notes.append(f"{where}: mirror check about {axis[0]} = {axis[1]:.2f}: " + "; ".join(notes) +
                                "; no fix kept")
                return None
            continue
        after = MR.mirrored_face_pairs(w5, o5, axis)
        bw5, site5, sw5 = TP.split_plot(w5, o5, blocks, level_id=level_id)
        idx5 = {o["index"] for o in site5["openings"]}
        b_open5 = [o for k, o in enumerate(o5) if k not in idx5]
        problem5 = TP.outer_loop_problem(bw5, b_open5)
        floor = best[-1] if best else before
        # changing a drawn wall's line or thickness must pair more rooms; copying a missing wall or an opening of the
        # twin must pair no fewer
        worse = after <= floor if step in ("thickness", "inferred") else after < floor
        if worse or _unclosed(sw5) > base_unclosed or (problem is None and problem5 is not None):
            notes.append(f"{step} not kept (rooms in mirror pairs {floor} -> {after})")
            continue
        kept_steps.append(step)
        best = (w5, o5, bw5, site5, sw5, b_open5, problem5, log, after)
    if best is None:
        ex.notes.append(f"{where}: mirror check about {axis[0]} = {axis[1]:.2f}: no fix kept"
                        + (f" ({'; '.join(notes)})" if notes else ""))
        return None
    w5, o5, bw5, site5, sw5, b_open5, problem5, log, after = best
    ex.notes.append(f"{where}: mirror check about {axis[0]} = {axis[1]:.2f} (the plan's two halves are mirror images):"
                    f" steps kept {', '.join(kept_steps)}; rooms in mirror pairs {before} -> {after}; " + "; ".join(log)
                    + (f" (not kept: {'; '.join(notes)})" if notes else ""))
    return w5, o5, bw5, site5, sw5, b_open5, problem5


def _shared_outdoor(walls: list, openings: list, blocks: list) -> list:
    """19 Nov 2026 (review A4, A4FC-4): the anchors of the indoor room labels whose closed face also holds a balcony or
    another outdoor label (a kitchen and its balcony in one face, a railing line closing them)."""
    outdoor = [Point(b.anchor) for b in blocks if getattr(b, "exterior", False)
               or getattr(b, "room_type", None) == "balcony"]
    if not outdoor:
        return []
    out = []
    for f in TP.faces(walls, openings):
        if not any(f.contains(p) for p in outdoor):
            continue
        out += [tuple(b.anchor) for b in blocks if not getattr(b, "exterior", False)
                and getattr(b, "room_type", None) != "balcony" and f.contains(Point(b.anchor))]
    return out


def _open_anchors(walls: list, openings: list, blocks: list) -> list:
    """The anchors of the indoor room labels (no balcony) that stand in no closed face of the walls."""
    faces = TP.faces(walls, openings)
    out = []
    for b in blocks:
        if getattr(b, "exterior", False) or getattr(b, "room_type", None) == "balcony":
            continue
        pt = Point(b.anchor)
        if not any(f.contains(pt) for f in faces):
            out.append(tuple(b.anchor))
    return out


TWIN_FACE_IOU = 0.6             # 20 Nov 2026 (R09-1): a face closed at a twin seed mirrors its labelled twin's face this
                                # well (intersection over union; real09 L2: the left kitchen is drawn 2.44 m wide, its
                                # twin 1.84 m, 70 %) ...
TWIN_TAG_REACH_M = 1.0          # ... and shows the drawing's own sign of a room there: a size tag this close to it ...
TWIN_DOOR_REACH_M = 0.35        # ... a drawn door this close to its outline ...
TWIN_FRAME_MIN_M = 1.0          # ... or this much of window and door frames along its outline
TWIN_SAME_AREA = 0.02           # 21 Nov 2026: a closed unlabelled face within this share of its twin's area is named by
                                # ``twins.mirror_labels`` (its 2 %), not by ``_closed_mirror_twins``
# an opening's size tag: an optional kind letter and number ('P:220/150', 'K:80/240', 'D1-90/210', 'W 120/150'), then
# width/height in cm
OPENING_TAG_RE = re.compile(r"^\s*(?:[A-Z]{1,2}\s*\d{0,2}\s*[:\-.]?\s*)?(\d{2,3})\s*/\s*(\d{2,3})\s*$", re.IGNORECASE)


def _mirror_point(q, axis) -> tuple:
    return (2.0 * axis[1] - q[0], q[1]) if axis[0] == "x" else (q[0], 2.0 * axis[1] - q[1])


def _mirror_poly(poly, axis):
    from shapely import affinity

    return affinity.scale(poly, xfact=-1.0 if axis[0] == "x" else 1.0, yfact=-1.0 if axis[0] == "y" else 1.0,
                          origin=(axis[1], 0.0) if axis[0] == "x" else (0.0, axis[1]))


def twin_evidence(face, twin_face, axis, texts_m: list, openings: list, strokes: list, walls: list,
                  others: list) -> tuple[Optional[str], list]:
    """20 Nov 2026 (R09-1, real09 L0-L2: the left flat's salon, its facade drawn as frames tagged 'P:220/150',
    'P:150/150' and a 'K:80/240' balcony door, stayed open because the missing salon itself made the shell 89 %
    symmetric, under ``facade.MIRROR_FIX_SHARE``): whether a face closed at the mirror of a labelled room is that room's
    twin (pure). ``(None, evidence)`` when its mirror overlaps the twin's face by ``TWIN_FACE_IOU`` and the drawing
    marks a room there: opening size tags (``OPENING_TAG_RE``) within ``TWIN_TAG_REACH_M`` of it and in no other
    closed face (``others``), drawn doors within ``TWIN_DOOR_REACH_M`` of its outline, or ``TWIN_FRAME_MIN_M`` of
    window and door frames along it; else ``(why not, [])``."""
    from wenart.ingest.generic import facade as FC

    if twin_face is None or twin_face.is_empty:
        return "its labelled twin has no closed face to compare", []
    m = _mirror_poly(face, axis)
    union = m.union(twin_face).area
    iou = m.intersection(twin_face).area / union if union > 0 else 0.0
    if iou < TWIN_FACE_IOU:
        return f"its mirror overlaps the twin's face by {iou:.0%} (< {TWIN_FACE_IOU:.0%})", []
    ev = []
    near = face.buffer(TWIN_TAG_REACH_M, join_style=2)
    tags = []
    for t in texts_m or []:
        if not OPENING_TAG_RE.match(str(getattr(t, "text", "") or "")):
            continue
        c = Point((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0)
        if near.contains(c) and not any(o.contains(c) for o in others):
            tags.append(str(t.text).strip())
    if tags:
        ev.append(f"size tags {', '.join(sorted(set(tags))[:6])}")
    ring = face.exterior
    doors = [o for o in openings or [] if not getattr(o, "virtual", False) and o.kind in ("door", "opening")
             and ring.distance(Point(tuple(o.center))) <= TWIN_DOOR_REACH_M]
    if doors:
        ev.append(f"{len(doors)} drawn door(s) on its outline")
    theta = O.dominant_angle(walls) if walls else None
    drawn = unary_union([TP.wall_polygon(w) for w in walls]).buffer(FC.ON_WALL_M) if walls else None
    band = ring.buffer(FC.BAND_M, cap_style=2, join_style=2)
    frames = 0.0
    for ln in FC.joinery_lines(strokes, theta):
        part = ln.intersection(band)
        if drawn is not None and not part.is_empty:
            part = part.difference(drawn)
        frames += part.length
    if frames >= TWIN_FRAME_MIN_M:
        ev.append(f"{frames:.1f} m of window and door frames along its outline")
    if not ev:
        return "the drawing marks no room there (no size tag, door or frames)", []
    return None, [f"its mirror overlaps the twin's face by {iou:.0%}"] + ev


def _closed_mirror_twins(cands: list, pool: list, blocks: list, labelled: list, axis, texts_m: list, openings: list,
                         strokes: list, walls: list) -> list:
    """21 Nov 2026 (real09 L2: once the wall union kept the light wells open, the plan was two mirrored halves at
    ``facade.MIRROR_FIX_SHARE``; the left kitchen, drawn 2.44 m wide against its twin's 1.84 m, was closed at a mirror
    seed and lost the 'Mutfak' the loose-axis twin seed gave it on 20 Nov, R09-1, because ``twins.mirror_labels`` wants
    the same area): the faces of ``cands`` (closed already, or closed at the mirror seeds of the strict axis) with no
    label of their own at a labelled room's mirror place across ``axis`` whose area differs from the twin's face (in
    ``pool``) and that pass ``twin_evidence`` (pure). Each is ``{"label", "of", "seed", "evidence"}`` in page metres, as
    the loose-axis twins: a twin's label never depends on which step closed its face. Geometry is not changed."""
    out = []
    pts = [Point(a) for a in labelled]
    for a in labelled:
        q = _mirror_point(a, axis)
        if math.dist(q, a) < 1e-6:
            continue
        face = next((f for f in cands if f.contains(Point(q))), None)
        twin_face = next((f for f in pool if f.contains(Point(a))), None)
        if face is None or twin_face is None or face is twin_face or any(face.contains(p) for p in pts):
            continue
        if abs(face.area - twin_face.area) <= TWIN_SAME_AREA * twin_face.area:
            continue                        # the same size: ``twins.mirror_labels`` names it
        others = [f for f in pool if f is not face]
        why, ev = twin_evidence(face, twin_face, axis, texts_m, openings, strokes, walls, others)
        if why:
            continue
        name = next((str(b.name) for b in blocks if math.dist(tuple(b.anchor), a) <= 1e-6), "?")
        out.append({"label": name, "of": [round(a[0], 4), round(a[1], 4)], "seed": [round(q[0], 4), round(q[1], 4)],
                    "evidence": ev})
    return out


def _glazed_facades(ex, where: str, walls2: list, openings: list, blocks: list, level_id, site_warnings: list,
                    problem: Optional[str], strokes: list, file_rel: str, page_no, s: float, owned: set,
                    texts_m: list = ()):
    """The open rooms closed along their facades of window and door frames (``facade``): the inferred walls carry
    the windows and doors drawn across them (``openings.openings_on_walls``), and an unverified window where frames
    run along a wall and no symbol reads; kept when they close in more labelled rooms (or close the outer loop).

    20 Nov 2026 (R09-1, real09 L0-L2: the left flat's salon and the L2 left kitchen were never built, a 5 x 5 m notch
    in three storeys, because the missing rooms made the shell 89 % symmetric, under the 90 % the mirror fixes need):
    when the plan is no two mirrored halves at ``facade.MIRROR_FIX_SHARE`` but is at ``facade.MIRROR_SHARE`` (the
    mirror-label rule's), the labelled rooms' mirror places in open areas are tried as twin seeds too; a face closed
    there is kept only when it mirrors its twin's face and the drawing marks a room there (``twin_evidence``: size
    tags, a drawn door, frames along it). Its walls name the twin, the axis and the evidence; the plan's outdoor
    spaces next to it get their mirror twins (``_outdoor_outlines``, ``ex.report["mirror_twins"]``).
    21 Nov 2026: a face closed already, or at a mirror seed of the strict axis, with no label of its own at a labelled
    room's mirror place and of another size than its twin is named the same way (``_closed_mirror_twins``): a twin's
    label never depends on which step closed its face."""
    from wenart.ingest.generic import facade as FC

    anchors = _open_anchors(walls2, openings, blocks)
    if not anchors:
        return None
    # the mirrored twins of the labelled rooms where the drafter named one flat only (real09)
    faces_now = TP.faces(walls2, openings)
    hull = unary_union([TP.wall_polygon(w) for w in walls2]).convex_hull
    labelled = [tuple(b.anchor) for b in blocks if not getattr(b, "exterior", False)
                and getattr(b, "room_type", None) != "balcony"]

    def open_test(q):
        return hull.contains(Point(q)) and not any(f.contains(Point(q)) for f in faces_now)

    axis = _halves(ex, walls2, openings, blocks, level_id, "mirror seeds")
    seeds = FC.mirror_seeds(walls2, labelled, open_test, axis=axis)
    loose, twin_seeds = None, []
    if axis is None:
        loose = _halves(ex, walls2, openings, blocks, level_id, "mirror twins (R09-1)", min_share=FC.MIRROR_SHARE)
        twin_seeds = FC.mirror_seeds(walls2, labelled, open_test, axis=loose) if loose else []
    tw_axis = axis if axis is not None else loose
    closed_twins = _closed_mirror_twins(faces_now, faces_now, blocks, labelled, tw_axis, texts_m, openings, strokes,
                                        walls2) if tw_axis else []
    if closed_twins:
        # page metres; the pipeline gives those rooms their twins' labels (``pipeline._mirror_twin_rooms``)
        ex.report["mirror_twins"] = {"axis": [tw_axis[0], round(tw_axis[1], 4)], "faces": [], "rooms": closed_twins}
        for tw in closed_twins:
            ex.notes.append(f"{where}: the closed face at ({tw['seed'][0]:.2f}, {tw['seed'][1]:.2f}) m, no label of its "
                            f"own, is the mirror twin of '{tw['label']}' across {tw_axis[0]} = {tw_axis[1]:.2f} "
                            f"(inferred, rule mirror_twin): {'; '.join(tw['evidence'])}")
    tried = anchors + seeds + twin_seeds
    faces, links = FC.close_rooms(walls2, strokes, tried)
    if not faces:
        return None
    twins = {}
    if twin_seeds:
        first = len(anchors) + len(seeds)
        for k in [k for k in faces if k >= first]:
            q = tried[k]
            a = _mirror_point(q, loose)
            ka = next((i for i, p in enumerate(anchors) if math.dist(p, a) <= 1e-6), None)
            twin_face = faces.get(ka) if ka is not None else next(
                (f for f in faces_now if f.contains(Point(a))), None)
            others = list(faces_now) + [f for i, f in faces.items() if i != k]
            name = next((str(b.name) for b in blocks if math.dist(tuple(b.anchor), a) <= 1e-6), "?")
            why, ev = twin_evidence(faces[k], twin_face, loose, texts_m, openings, strokes, walls2, others)
            if why:
                ex.notes.append(f"{where}: mirror twin of '{name}' at ({q[0]:.2f}, {q[1]:.2f}) m not closed: {why}")
                faces.pop(k)
                continue
            twins[k] = {"label": name, "of": [round(a[0], 4), round(a[1], 4)], "seed": [round(q[0], 4), round(q[1], 4)],
                        "evidence": ev}
        if not faces:
            return None
    # 5 Nov 2026 (real11 L0: the left kitchen's face ran along the balcony's railing and took the 'BALKON 10.00 m2'
    # in): a face holding an outdoor-space label, the mirror image of one, or matching an outdoor area text is no
    # room; it is not closed here (the outline closure may close the room along its facade, under the same guard)
    guard = outdoor_guard(blocks, walls2, _halves(ex, walls2, openings, blocks, level_id, "glazed facades") or (
        loose if twins else None))
    kept_faces = {}
    for k, face in faces.items():
        why = outdoor_enclosure(face, guard)
        if why:
            ex.notes.append(f"{where}: glazed facade: the face closed around the label at ({tried[k][0]:.2f}, "
                            f"{tried[k][1]:.2f}) m is no room: {why}; not closed along those frames")
        else:
            kept_faces[k] = face
    faces = kept_faces
    twins = {k: v for k, v in twins.items() if k in faces}
    if not faces:
        return None

    def told(mid, t):
        # 20 Nov 2026 (R09-1): a wall of a mirror twin's face names the twin, the axis and the drawing's evidence
        k = min(faces, key=lambda i: faces[i].exterior.distance(Point(mid)))
        if k not in twins or faces[k].exterior.distance(Point(mid)) > t:
            return None
        tw = twins[k]
        return (f"the mirror twin of '{tw['label']}' across the plan's axis ({loose[0]} = {loose[1]:.2f}; the drafter "
                f"named one of the two mirrored halves only): its walls did not close, the wall is inferred where its "
                f"frames stand (thickness {t:.2f} m); evidence: {'; '.join(tw['evidence'])}", None)

    new_walls = FC.facade_wall_items(walls2, list(faces.values()), openings, file_rel, page_no, units_to_m=s,
                                     why=told if twins else None)
    # 21 Nov 2026 (the RC18 fix round; real09 L3: the depot's face, closed on the drawn facade line, met a 3 cm crack
    # between two drawn walls at its corner that its inferred walls did not seal, and the room stayed open): a face whose
    # walls leave its label in no closed face is closed again with the frames' own bands (``close_rooms(snap=False)``,
    # the rule before the facade line): the facade line where it closes the room, the old closure where it does not
    if new_walls and FC.FACADE_LINE_SNAP:
        closed = TP.faces(list(walls2) + new_walls, openings)
        lost = [k for k in faces if not any(f.contains(Point(tried[k])) for f in closed)]
        if lost:
            old_faces, old_links = FC.close_rooms(walls2, strokes, [tried[k] for k in lost], snap=False)
            for j, k in enumerate(lost):
                if j in old_faces:
                    faces[k] = old_faces[j]
            links += old_links
            ex.notes.append(f"{where}: glazed facade: {len(lost)} face(s) closed on the drawn facade line left their "
                            f"label open (a crack between drawn walls): closed with the frames' own bands instead")
            new_walls = FC.facade_wall_items(walls2, list(faces.values()), openings, file_rel, page_no, units_to_m=s,
                                             why=told if twins else None)
    if not new_walls:
        return None
    taken = set(owned)
    read = FC.swing_doors(new_walls, strokes,
                          O.openings_on_walls(new_walls, strokes, file_rel, page_no, units_to_m=s, owned=taken))
    framed = FC.frame_windows(new_walls, strokes, read, walls2)
    w4, o4 = list(walls2) + new_walls, list(openings) + read + framed
    bw4, site4, sw4 = TP.split_plot(w4, o4, [b for b in blocks], level_id=level_id)
    idx4 = {o["index"] for o in site4["openings"]}
    b_open4 = [o for k, o in enumerate(o4) if k not in idx4]
    problem4 = TP.outer_loop_problem(bw4, b_open4)
    before, after = _unclosed(site_warnings), _unclosed(sw4)
    if not (after < before or (problem is not None and problem4 is None and after <= before)):
        return None
    owned.update(taken)
    if seeds:
        ex.notes.append(f"{where}: {len(seeds)} mirrored twin(s) of labelled rooms tried at the plan's mirror axis "
                        f"(the drafter named one half only): {sum(1 for k in faces if k >= len(anchors))} closed")
    seed_faces = [faces[k] for k in faces if len(anchors) <= k < len(anchors) + len(seeds)]
    seed_twins = _closed_mirror_twins(seed_faces, list(faces_now) + list(faces.values()), blocks, labelled, axis,
                                      texts_m, openings, strokes, walls2) if seed_faces and axis else []
    if seed_twins and not twins:
        ex.report["mirror_twins"] = {"axis": [axis[0], round(axis[1], 4)], "faces": [],
                                     "rooms": closed_twins + seed_twins}
        for tw in seed_twins:
            ex.notes.append(f"{where}: the face closed at the mirror seed ({tw['seed'][0]:.2f}, {tw['seed'][1]:.2f}) m "
                            f"is the mirror twin of '{tw['label']}' across {axis[0]} = {axis[1]:.2f}, drawn another size "
                            f"(inferred, rule mirror_twin): {'; '.join(tw['evidence'])}")
    if twins:
        # page metres; the pipeline gives the rooms closed there their twins' labels (``pipeline._mirror_twin_rooms``)
        ex.report["mirror_twins"] = {"axis": [loose[0], round(loose[1], 4)],
                                     "faces": [[[round(x, 4), round(y, 4)] for x, y in faces[k].exterior.coords]
                                               for k in twins],
                                     "rooms": closed_twins + [dict(tw) for tw in twins.values()]}
        for tw in twins.values():
            ex.notes.append(f"{where}: the mirror twin of '{tw['label']}' (at {tw['of'][0]:.2f}, {tw['of'][1]:.2f} m) "
                            f"closed across the axis {loose[0]} = {loose[1]:.2f} (inferred, rule mirror_twin: the "
                            f"plan is two mirrored halves at {FC.MIRROR_SHARE:.0%}, not at {FC.MIRROR_FIX_SHARE:.0%}, "
                            f"because the twin is missing): {'; '.join(tw['evidence'])}")
    ex.notes.append(f"{where}: {len(faces)} room(s) closed along facades of window and door frames (rule glazed_facade):"
                    f" {len(new_walls)} inferred wall(s), {len(links)} gap link(s) up to {FC.LINK_M:g} m, "
                    f"{len(read)} drawn opening(s) read on them, {len(framed)} unverified window(s) where frames run "
                    f"along them; labels in no closed face {before} -> {after}")
    return w4, o4, bw4, site4, sw4, b_open4, problem4


OPEN_OUTLINE_ON_WALLS = 0.5      # 19 Nov 2026 (review A3, OA3-06): a room outline this much along drawn walls ...
OPEN_OUTLINE_MIN_M2 = 1.5        # ... and this large is the room its label names, its missing sides inferred


OPEN_OUTLINE_RULE = "room_outline_closure"     # 19 Nov 2026 (review A4, A4FC-5): the evidence rule of its walls


def _open_room_outlines(ex, where: str, walls2: list, openings: list, blocks: list, level_id, site_warnings: list,
                        problem: Optional[str], strokes: list, file_rel: str, page_no, s: float, owned: set):
    """19 Nov 2026 (review A3, OA3-06: real18 L1-L3's north kitchen, its wall towards the balcony drawn as jamb stubs,
    an 80/210 door and a 100/140 window block, was never built: kitchen and balcony became one outdoor space and the
    MUTFAK label stood in no face): an indoor room label in no closed face whose own drawn closed outline holds it
    alone (``outlines.labelled_outlines``: its area text matched when printed), at least ``OPEN_OUTLINE_MIN_M2`` and
    along drawn walls for ``OPEN_OUTLINE_ON_WALLS`` of its boundary, is that room: walls are inferred along its sides
    where none stand (``facade.facade_wall_items``) and the door and window symbols drawn across them are read
    (``openings.openings_on_walls``); kept when they close in more labelled rooms."""
    from wenart.ingest.generic import facade as FC

    # 19 Nov 2026 (review A4, A4FC-4: real18's south kitchen shared one face with its balcony, split by a virtual
    # separator, while its north twin was closed): an indoor label whose face also holds a balcony label too
    anchors = set(_open_anchors(walls2, openings, blocks)) | set(_shared_outdoor(walls2, openings, blocks))
    if not anchors:
        return None
    outs = [o for o in OL.labelled_outlines(strokes, blocks) if tuple(o.block.anchor) in anchors
            and o.polygon.area >= OPEN_OUTLINE_MIN_M2]
    if not outs:
        return None
    drawn = unary_union([TP.wall_polygon(w) for w in walls2]).buffer(0.4)
    faces = [o.polygon for o in outs
             if o.polygon.exterior.intersection(drawn).length >= OPEN_OUTLINE_ON_WALLS * o.polygon.exterior.length]
    if not faces:
        return None
    used = [o for o in outs if any(o.polygon is f for f in faces)]

    def why(mid, t):
        # 19 Nov 2026 (review A4, A4FC-5): the wall names the room's outline that made it
        o = min(used, key=lambda x: x.polygon.exterior.distance(Point(mid)))
        return (f"the room '{o.block.name}' closed along its own drawn outline ({o.stroke.id}): its walls did not "
                f"close, the wall is inferred on the outline's side where none is drawn (thickness {t:.2f} m, the "
                f"median of the drawn walls it touches); the door and window symbols drawn across it are read",
                o.stroke.id)

    new_walls = FC.facade_wall_items(walls2, faces, openings, file_rel, page_no, units_to_m=s,
                                     rule=OPEN_OUTLINE_RULE, why=why)
    if not new_walls:
        return None
    taken = set(owned)
    read = FC.swing_doors(new_walls, strokes,
                          O.openings_on_walls(new_walls, strokes, file_rel, page_no, units_to_m=s, owned=taken))
    framed = FC.frame_windows(new_walls, strokes, read, walls2)
    w4, o4 = list(walls2) + new_walls, list(openings) + read + framed
    bw4, site4, sw4 = TP.split_plot(w4, o4, [b for b in blocks], level_id=level_id)
    idx4 = {o["index"] for o in site4["openings"]}
    b_open4 = [o for k, o in enumerate(o4) if k not in idx4]
    problem4 = TP.outer_loop_problem(bw4, b_open4)
    before, after = _unclosed(site_warnings), _unclosed(sw4)
    shared0, shared1 = len(_shared_outdoor(walls2, openings, blocks)), len(_shared_outdoor(w4, o4, blocks))
    if not (after < before or (problem is not None and problem4 is None and after <= before)
            or (shared1 < shared0 and after <= before)):
        return None
    owned.update(taken)
    ex.notes.append(f"{where}: {len(faces)} room(s) whose label stood in no closed face closed along their own drawn "
                    f"outlines ({', '.join(o.block.name for o in outs[:6])}): {len(new_walls)} inferred wall(s), "
                    f"{len(read)} drawn opening(s) read on them, {len(framed)} unverified window(s); labels in no "
                    f"closed face {before} -> {after}")
    return w4, o4, bw4, site4, sw4, b_open4, problem4


def _walls_from_outlines(ex: LevelExtraction, where: str, problem: str, strokes_m: list, blocks: list, walls: list,
                         openings: list, owned: set, gap_log: list, file_rel: str, page_no: Optional[int], s: float):
    """When the drawn walls do not close (``problem``), infer them along the labelled room outlines
    (``outlines.labelled_outlines`` / ``infer_walls``). Returns ``(walls, openings, outline stroke ids)`` when the
    inferred walls close the outer loop, else None (the drawn walls stay; the review reason stands). Every inferred
    wall, the outlines used and the rooms left without a door are reported (never silent)."""
    outlines = OL.labelled_outlines(strokes_m, blocks)
    if len(outlines) < OL.MIN_OUTLINES:
        return None
    inf = OL.infer_walls(outlines, walls, strokes_m, file_rel, page_no, units_to_m=s, owned=owned)
    if inf is None or not inf.inferred:
        return None
    kept_ids = {id(w) for w in inf.kept}
    new_walls = list(inf.kept) + inf.inferred + [w for w in walls if id(w) not in kept_ids]
    new_openings = list(openings) + list(inf.openings)
    still = TP.outer_loop_problem(new_walls, new_openings)
    report = {"problem": problem, "outlines": [OL.outline_line(o) for o in outlines], "inferred": len(inf.inferred),
              "kept_drawn": len(inf.kept), "outer_thickness": inf.outer_thickness,
              "thickness_source": inf.thickness_source, "openings": len(inf.openings), "closed": still is None}
    ex.report["walls_from_outlines"] = report
    if still is not None:
        ex.notes.append(f"{where}: walls inferred from {len(outlines)} labelled room outlines do not close either "
                        f"({still}); not used")
        return None
    owned.update(inf.owned)
    for o in inf.openings:
        gap_log.append({"kind": "continuous", "class": o.kind, "center": list(o.center), "width": o.width,
                        "entity": o.entity, "on": "inferred wall"})
    ex.warnings.append(f"{where}: the drawn walls do not close ({problem}): {OL.summary(inf)}")
    ex.notes.append(f"{where}: room outlines used for the inferred walls: " +
                    "; ".join(OL.outline_line(o) for o in outlines))
    ex.notes.extend(f"{where}: inferred walls: {n}" for n in inf.notes)
    ex.warnings.extend(f"{where}: inferred walls: {w}" for w in inf.warnings)
    if inf.openings:
        ex.notes.append(f"{where}: {len(inf.openings)} drawn door/window symbols read on the inferred walls")
    for name in OL.doorless_rooms(outlines, new_walls, new_openings):
        ex.warnings.append(f"{where}: room '{name}' (walls inferred from its outline) has no door in the documents; "
                           f"none invented (the agent may add one)")
    return new_walls, new_openings, {o.stroke.id for o in outlines}


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
    frames = FR.frame_blocks(page)
    if frames:
        # A sheet frame inserted as one block with its title block (real03's legend block): drawing furniture of
        # the sheet, never walls, openings or furniture of the plan (its texts stay for the titles).
        drop = {i for f in frames for i in f["stroke_ids"]}
        page = dataclasses.replace(page, strokes=[st for st in page.strokes if st.id not in drop])
        for f in frames:
            ex.notes.append(f"{where}: sheet frame block {f['entity']} ({f['block'] or 'block'}, layer "
                            f"{f['layer'] or '-'}): {f['strokes']} strokes (frame and title block at the frame edge) "
                            f"are not plan geometry")
        ex.report["sheet_frames"] = [{k: v for k, v in f.items() if k != "stroke_ids"} for f in frames]
    ex.report["page_strokes"] = page.strokes      # 12 Nov 2026: the completion rules read the drawing (drawn_strokes)
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
    # 5 Nov 2026 (Milestone 14 R3; user: "I want structure recognition to be cumulatively better with the feedbacks I
    # am giving"): the level's decision log; the wall reader and the gap classifier write one record per decision into
    # it, the end of this function writes them to ``ex.report["decisions"]`` (the pipeline: reading_check/decisions_*)
    from wenart.ingest.generic import decisions as DEC
    dim_stroke_ids = frozenset(i for d in dims if d.how != "dimension_entity" for i in d.stroke_ids)
    decisions = DEC.DecisionLog(level_id, texts=texts_m, dimension_ids=dim_stroke_ids, units_to_m=s,
                                ranker=DEC.ranker_enabled())

    # 3. Walls and openings (G2's order, tests/_real01_page.py g2_chain).
    prims = W.wall_primitives(page, s, dim_stroke_ids, decisions=decisions)
    mask = W.wall_mask(page, prims, s)
    prim_ids = {i for p in prims for i in p.stroke_ids}
    walls, wall_info = W.walls_from_mask(mask, [st for st in strokes_m if st.id not in prim_ids], file_rel, page_no,
                                         units_to_m=s)
    ex.warnings.extend(f"{where}: {w}" for w in wall_info.get("warnings", []))
    wall_strokes = prim_ids - set(wall_info.get("dropped_strokes", []))
    non_wall = [st for st in strokes_m if st.id not in wall_strokes]
    # (the dimension finder's strokes are not passed: its "two parallel lines around a number" also takes a window's
    # frame lines beside its size tag; the notation is read from the layers, UL296)
    # 6 Nov 2026: the wall primitives' strokes go along, so a door leaf the wall mask read as a thin wall goes back to
    # its door (``openings.leaf_walls``)
    # 12 Nov 2026 (review B-OPN-03): the outdoor-space labels (balcony, terrace, courtyard) mark the closed spaces open
    # to the sky, so a window on their walls is no inner wall's
    # 12 Nov 2026 (review B2-GEN-01): the labels of rooms one lives in mark closed spaces that are never open to the sky
    # (a living room whose entrance gap the reading left unclassified is no light well)
    from wenart.levels import outdoor as OD
    outdoor_points, room_points = [], []
    for t in texts_m:
        if not t.text:
            continue
        at = ((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0)
        if OD.space_kind(t.text):
            outdoor_points.append(at)
        elif B.room_type_for(t.text) not in NOT_LIVED_IN_TYPES:
            room_points.append(at)
    walls2, openings, gap_log, owned = O.gaps_and_openings(walls, non_wall, file_rel, page_no, units_to_m=s,
                                                           wall_strokes=[st for st in strokes_m
                                                                         if st.id in wall_strokes],
                                                           outdoor_points=outdoor_points, room_points=room_points,
                                                           decisions=decisions,
                                                           linetypes={st.id: st.linetype for st in page.strokes
                                                                      if getattr(st, "linetype", None)})
    walls2, openings = _faces_through_gaps(ex, where, walls2, openings, strokes_m)
    openings = _door_blocks_in_gaps(ex, where, walls2, openings, strokes_m, owned, texts_m, file_rel, page_no, s)
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
    # 19 Nov 2026 (review A4, POD-A4-02 / A4FC-1: lift shafts from the drawn enclosure): the page's drawn wall faces
    # (straight pieces on a wall, plaster or structure layer, page metres), kept on the extraction for the lift rules
    # (``twins.drawn_enclosure``); not written anywhere
    ex.face_lines_m = _face_lines(strokes_m)
    ex.detail_lines_m = _detail_lines(strokes_m)

    # 4. Label blocks, plot and building. 6 Nov 2026 (target 4, real14): a room schedule (a list of room words under a
    # header such as MAHAL, or outside every wall's hull) is no label (``labels.schedules``); never silent.
    hull = unary_union([TP.wall_polygon(w) for w in walls2]).convex_hull if walls2 else None
    found_schedules: list = []
    blocks = LB.merge_label_blocks(texts_m, file_rel, page_no, hull=hull, schedules_out=found_schedules)
    for sc_ in found_schedules:
        ex.notes.append(f"{where}: a room schedule ({sc_['axis']}, {len(sc_['room_words'])} room words: "
                        f"{', '.join(sc_['room_words'][:6])}{' ...' if len(sc_['room_words']) > 6 else ''}; "
                        f"{sc_['why']}) is a list, not room labels")
    if found_schedules:
        ex.report["schedules"] = [{k: v for k, v in sc_.items() if k != "box"} | {"box_m": [round(v, 3) for v in
                                                                                          sc_["box"]]}
                                  for sc_ in found_schedules]
    bwalls, site, site_warnings = TP.split_plot(walls2, openings, blocks, level_id=level_id)
    site_idx = {o["index"] for o in site["openings"]}
    b_openings = [o for k, o in enumerate(openings) if k not in site_idx]
    problem = TP.outer_loop_problem(bwalls, b_openings)
    if problem is not None and not is_raster:
        # Milestone 11 (CLAUDE.md: open outer walls -> infer first): the drawn walls do not close, but the rooms may
        # be drawn as labelled closed outlines: the walls are inferred along them (``outlines``).
        inferred = _walls_from_outlines(ex, where, problem, non_wall, blocks, walls2, openings, owned, gap_log,
                                        file_rel, page_no, s)
        if inferred is not None:
            walls2, openings, outline_ids = inferred
            wall_strokes = wall_strokes | outline_ids
            non_wall = [st for st in non_wall if st.id not in outline_ids]
            bwalls, site, site_warnings = TP.split_plot(walls2, openings, blocks, level_id=level_id)
            site_idx = {o["index"] for o in site["openings"]}
            b_openings = [o for k, o in enumerate(openings) if k not in site_idx]
            problem = TP.outer_loop_problem(bwalls, b_openings)
    if (problem is not None or _unclosed(site_warnings)) and not is_raster:
        # 2 Nov 2026 (real07: a sliding door, a garage door and an entrance without a symbol the openings reader
        # knows): wide gaps between two free wall ends in the outer ring are inferred openings (``wide_gaps``)
        bridged = _outer_gaps(ex, where, walls2, openings, blocks, level_id, site_warnings, problem, non_wall)
        if bridged is not None:
            walls2, openings, bwalls, site, site_warnings, b_openings, problem = bridged
    if (problem is not None or _unclosed(site_warnings)) and not is_raster:
        # 4 Nov 2026 (real17 L0, user: "Those walls already drawed, all open ones needs to be walls"): a wall end
        # stopping just short of a column or wall on its own line joins it (``_short_joins``)
        joined = _short_joins(ex, where, walls2, openings, blocks, level_id, site_warnings, problem)
        if joined is not None:
            walls2, openings, bwalls, site, site_warnings, b_openings, problem = joined
    if (problem is not None or _unclosed(site_warnings)) and not is_raster:
        # 3 Nov 2026 (user: "go ahead with the glazed facades"; real09, real11, real13, real14): the facades of window
        # and door frames are closed around the rooms still open (``facade``); the openings drawn across them are read
        glazed = _glazed_facades(ex, where, walls2, openings, blocks, level_id, site_warnings, problem, non_wall,
                                 file_rel, page_no, s, owned, texts_m)
        if glazed is not None:
            walls2, openings, bwalls, site, site_warnings, b_openings, problem = glazed
    if (problem is not None or _unclosed(site_warnings)) and not is_raster:
        # 19 Nov 2026 (review A3, OA3-06: real18's north kitchen): a label in no closed face closed along its own drawn
        # room outline (``_open_room_outlines``)
        outlined = _open_room_outlines(ex, where, walls2, openings, blocks, level_id, site_warnings, problem, non_wall,
                                       file_rel, page_no, s, owned)
        if outlined is not None:
            walls2, openings, bwalls, site, site_warnings, b_openings, problem = outlined
    if not is_raster:
        # 3 Nov 2026 (real09, user: "wait a light well is not correct, there is not wall in the purple section"): an
        # empty gap in an outer wall into a doorless recess is open air, not an opening (``_open_recesses``)
        opened = _open_recesses(ex, where, walls2, openings, blocks, level_id)
        if opened is not None:
            walls2, openings, bwalls, site, site_warnings, b_openings, problem = opened
        # 4 Nov 2026 (real10, user: "These 2 oda should not exist and that 2 area should be outside"): a recess reached
        # through a chain of gaps (``_open_recess_chains``)
        chained = _open_recess_chains(ex, where, walls2, openings, blocks, level_id, non_wall)
        if chained is not None:
            walls2, openings, bwalls, site, site_warnings, b_openings, problem = chained
    if not is_raster:
        # 3 Nov 2026 (user: "Most of these drawings are mirrored it can help to fix the issues"): the two mirrored
        # halves of a plan check each other (``mirror``)
        mirrored = _mirror_consistency(ex, where, walls2, openings, blocks, level_id, site_warnings, problem, strokes_m)
        if mirrored is not None:
            walls2, openings, bwalls, site, site_warnings, b_openings, problem = mirrored
    if not is_raster:
        # 4 Nov 2026 (real17, user: "these sections could be full windows glass, check it"): a window size tag sets its
        # window (``_window_tags``)
        tag_outline = TP.building_outline(bwalls, b_openings) if bwalls else None
        for keep_width in (False, True):
            doored = _door_tags(ex, where, walls2, openings, texts_m, s, keep_width=keep_width, outline=tag_outline,
                                strokes=non_wall)
            if doored is None:
                break
            bw_d, site_d, sw_d = TP.split_plot(walls2, doored, blocks, level_id=level_id)
            idx = {o["index"] for o in site_d["openings"]}
            b_open_d = [o for j, o in enumerate(doored) if j not in idx]
            prob_d = TP.outer_loop_problem(bw_d, b_open_d)
            if _unclosed(sw_d) <= _unclosed(site_warnings) and (prob_d is None or problem is not None):
                openings, bwalls, site, site_warnings, b_openings, problem = doored, bw_d, site_d, sw_d, b_open_d, prob_d
                break
            ex.notes.append(f"{where}: the doors of the size tags at their own widths would open the walls"
                            + ("" if keep_width else ": they keep their gaps' widths"))
        # 12 Nov 2026 (review B2 FC-06 / REG-3): every drawn door in a gap of its own wall takes its part of the gap, the
        # rest read from the drawing (``openings.doors_in_gaps``)
        trimmed = O.doors_in_gaps(walls2, openings, non_wall + [st for st in strokes_m if st.id in wall_strokes],
                                  file_rel, page_no, units_to_m=s)
        if trimmed is not None:
            bw_g, site_g, sw_g = TP.split_plot(walls2, trimmed, blocks, level_id=level_id)
            idx = {o["index"] for o in site_g["openings"]}
            b_open_g = [o for j, o in enumerate(trimmed) if j not in idx]
            prob_g = TP.outer_loop_problem(bw_g, b_open_g)
            if _unclosed(sw_g) <= _unclosed(site_warnings) and (prob_g is None or problem is not None):
                openings, bwalls, site, site_warnings, b_openings, problem = trimmed, bw_g, site_g, sw_g, b_open_g, \
                    prob_g
            else:
                ex.notes.append(f"{where}: the doors' parts of the gaps they stand in left as read: the rests would "
                                f"open the walls")
        # 20 Nov 2026 (rule ``cut_span_door``, after the size tags took their own doors): a drawn door whose gap the
        # wall's cut lines close is read as its door
        spanned = doors_in_cut_spans(walls2, openings, strokes_m, texts_m, s)
        if spanned is not None:
            bw_c, site_c, sw_c = TP.split_plot(walls2, spanned, blocks, level_id=level_id)
            idx = {o["index"] for o in site_c["openings"]}
            b_open_c = [o for j, o in enumerate(spanned) if j not in idx]
            prob_c = TP.outer_loop_problem(bw_c, b_open_c)
            if _unclosed(sw_c) <= _unclosed(site_warnings) and (prob_c is None or problem is not None):
                openings, bwalls, site, site_warnings, b_openings, problem = spanned, bw_c, site_c, sw_c, b_open_c, \
                    prob_c
            else:
                ex.notes.append(f"{where}: the doors in the cut-line spans left out: they would open the walls")
        tagged = _window_tags(ex, where, walls2, openings, texts_m, s, non_wall)
        if tagged is not None:
            bw_t, site_t, sw_t = TP.split_plot(walls2, tagged, blocks, level_id=level_id)
            idx = {o["index"] for o in site_t["openings"]}
            b_open_t = [o for j, o in enumerate(tagged) if j not in idx]
            prob_t = TP.outer_loop_problem(bw_t, b_open_t)
            if _unclosed(sw_t) <= _unclosed(site_warnings) and (prob_t is None or problem is not None):
                openings, bwalls, site, site_warnings, b_openings, problem = tagged, bw_t, site_t, sw_t, b_open_t, prob_t
            else:
                ex.notes.append(f"{where}: the windows of the size tags left out: they would open the walls")
        framed = _framed_windows(ex, where, walls2, openings, non_wall, texts_m, s)
        if framed is not None:
            bw_f, site_f, sw_f = TP.split_plot(walls2, framed, blocks, level_id=level_id)
            idx = {o["index"] for o in site_f["openings"]}
            b_open_f = [o for j, o in enumerate(framed) if j not in idx]
            prob_f = TP.outer_loop_problem(bw_f, b_open_f)
            if _unclosed(sw_f) <= _unclosed(site_warnings) and (prob_f is None or problem is not None):
                openings, bwalls, site, site_warnings, b_openings, problem = framed, bw_f, site_f, sw_f, b_open_f, \
                    prob_f
            else:
                ex.notes.append(f"{where}: the windows read from frame lines left out: they would open the walls")
        # 13 Nov 2026 (review S1-03c: real03's 2.90 m window was built over its double entrance doors): a door keeps its
        # stretch of a window read over it on the same wall line (``openings.windows_off_doors``)
        cut, cut_notes = O.windows_off_doors(openings)
        if cut_notes:
            bw_w, site_w, sw_w = TP.split_plot(walls2, cut, blocks, level_id=level_id)
            idx = {o["index"] for o in site_w["openings"]}
            b_open_w = [o for j, o in enumerate(cut) if j not in idx]
            prob_w = TP.outer_loop_problem(bw_w, b_open_w)
            if _unclosed(sw_w) <= _unclosed(site_warnings) and (prob_w is None or problem is not None):
                openings, bwalls, site, site_warnings, b_openings, problem = cut, bw_w, site_w, sw_w, b_open_w, prob_w
                ex.notes.append(f"{where}: " + "; ".join(cut_notes))
    if (problem is not None or _unclosed(site_warnings)) and not is_raster:
        # 4 Nov 2026 (Milestone 14 R2, "never leave a level out; carry confidence instead"): the last pass bridges the
        # gaps of the outer ring along the outline at confidence 0.3 (``_outline_closure``); what stays open marks the
        # level low-confidence in the pipeline (failed_levels: build_marked) instead of leaving it out
        closed = _outline_closure(ex, where, walls2, openings, blocks, level_id, site_warnings, problem, bwalls,
                                  b_openings, non_wall, SY._dimension_ids(dims), file_rel, page_no, units_to_m=s,
                                  owned=owned)
        if closed is not None:
            walls2, openings, bwalls, site, site_warnings, b_openings, problem = closed
    for w in site_warnings:
        if w.startswith(TP.REVIEW_PREFIX):
            ex.review.append(f"{where}: {w[len(TP.REVIEW_PREFIX):]}")
        else:
            ex.warnings.append(f"{where}: {w}")
    if not bwalls:
        ex.review.append(f"{where}: no building walls found")
    if problem is not None:
        ex.review.append(f"{where}: outer walls do not close ({problem})")
    outline = TP.building_outline(bwalls, b_openings)
    # 26 Oct 2026 (real06's VERANDA and BALKON: no walls around them, nothing built): a labelled outdoor space without
    # a closed face is closed from the drawn strokes around its label (wenart.levels.outdoor.read_outline)
    _outdoor_outlines(ex, where, site, non_wall, outline, bwalls, blocks)
    # 3 Nov 2026 (real09, user: "each duplex flat has its inner stair and a 'galeri' void over the floor below"): the
    # voids the plan labels (galeri, boşluk, void, open to below ...) with their drawn outlines (generic.voids)
    from wenart.ingest.generic import voids as VD
    site["voids"] = VD.read_voids(texts_m, strokes_m)
    # 12 Nov 2026 (round-2 review, A2-FC9: a garage drive inferred in front of a drawn ramp): the drawn ramp symbols
    # outside the building (``levels.read.ramp_outlines``); the levels give an outside door the one at its face
    if not is_raster:
        from wenart.levels import read as LRD

        site["ramp_outlines"] = LRD.ramp_outlines(strokes_m, outline)
        for r in site["ramp_outlines"]:
            ex.notes.append(f"{where}: a drawn ramp symbol {r['length']:.2f} x {r['width']:.2f} m outside the building "
                            f"({', '.join(r['entities'][:5])})")
    for v in site["voids"]:
        ex.notes.append(f"{where}: void '{v['label']}': {v['reason']}")
    if site["voids"]:
        blocks, void_notes = VD.room_labels(blocks, site["voids"], TP.faces(bwalls, b_openings))
        ex.notes.extend(f"{where}: {n}" for n in void_notes)

    # 5. Furniture, separators, faces. Milestone 12 (track R): the re-read's extra candidates and its symbols.
    extras: list[dict] = []
    symbols: list[dict] = []
    pieces, cands, decor = SY.furniture(non_wall, owned, bwalls, b_openings, texts_m, dims, outline, [],
                                        wall_strokes=wall_strokes, site_walls=site["boundary_walls"],
                                        level_id=level_id, file_rel=file_rel, page_no=page_no, units_to_m=s,
                                        notes=ex.notes, extra_out=extras, symbols_out=symbols)
    site["decor"] = decor
    if not is_raster:
        # 3 Nov 2026 (real09, user: "each duplex flat has its inner stair (winders 1-17)"): stairs whose treads are
        # numbered, read from the numbers where the stair rule found none (generic.stair_numbers)
        from wenart.ingest.generic import stair_numbers as SN
        pieces, cands, sn_polys = SN.apply(pieces, cands, texts_m, non_wall, s, file_rel, page_no, ex.notes)
        # 27 Nov 2026 (audit fix round 4, R24): the stair formula text in or next to a stair ('(19X17.36Rh=330/27)')
        from wenart.ingest.generic import stair_formula as SF
        SF.attach(pieces, texts_m, ex.notes)
        # 13 Nov 2026 (coordinator; review A2-FC5): a rule stair with nothing of a stair written by it is none
        pieces = SY.check_rule_stairs(pieces, texts_m, non_wall, TP.faces(bwalls, b_openings), ex.notes)
        if sn_polys:
            extras = [e for e in extras if not any(q.buffer(-0.05).contains(Point(e["footprint"]["center"]))
                                                   for q in sn_polys)]
    stairs = [p for p in pieces if p.type == "stair"]
    # 13 Nov 2026 (coordinator after review B3 / RC16 on real10: walls the reader built from a stair's tread, side and
    # well lines stood in its flights on every floor): a wall lying mostly in a stair's walking area is the stair's
    # drawing, not a wall (``_stair_line_walls``)
    bwalls = _stair_line_walls(bwalls, stairs, b_openings, ex.notes, where, strokes_m)
    from wenart.ingest.generic import facade as FC_
    # 12 Nov 2026 (review B-r03-hol): the labelled rooms' own outlines (their printed area matched) separate the names
    # the walls leave in one face
    seps, sep_log = TP.separators(bwalls, b_openings, gap_log, blocks, stairs, units_to_m=s,
                                  axis=_halves(ex, bwalls, b_openings, blocks, level_id),
                                  outlines=lambda: [o.polygon for o in OL.labelled_outlines(non_wall, blocks)
                                                    if o.area_off is not None])
    face_texts = [(t.text, ((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0)) for t in texts_m
                  if getattr(t, "text", None) and str(t.text).strip() and getattr(t, "box", None)]
    rows = face_table(TP.faces(bwalls, b_openings, seps), blocks, bwalls, b_openings, stairs, face_texts, ex.notes)
    SY.apply_room_checks(pieces, cands + extras, [{"polygon": r["polygon"], "room_type": r["room_type"],
                                                   "label": r["label"]} for r in rows], ex.notes)
    for cand in cands + extras:
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
        rows = face_table(face_polys, blocks, bwalls, b_openings, stairs, face_texts)
        if ai_runs:
            # Accepted VLM label boxes, checked against the page (``_blank_run``: inside the face, text-sized, only
            # letter-sized strokes inside), are blanked before the final clustering (§3.4): those glyph strokes are
            # no furniture.
            extras, symbols = [], []
            pieces, cands, decor = SY.furniture(non_wall, owned, bwalls, b_openings, texts_m + ai_runs, dims, outline,
                                                [], wall_strokes=wall_strokes, site_walls=site["boundary_walls"],
                                                level_id=level_id, file_rel=file_rel, page_no=page_no,
                                                units_to_m=s, notes=ex.notes, extra_out=extras, symbols_out=symbols)
            site["decor"] = decor
            SY.apply_room_checks(pieces, cands + extras, [{"polygon": r["polygon"], "room_type": r["room_type"],
                                                           "label": r["label"]} for r in rows], ex.notes)
        for cand in cands + extras:
            pt = Point(cand["footprint"]["center"])
            row = next((r for r in rows if r["polygon"].contains(pt)), None)
            cand["room_type"] = row["room_type"] if row else None
            cand["_ids"] = _expand_ids(cand["item"].evidence.get("entity"))
        ex.report["size_labels"] = _size_label_rows(rows)
        scale_rows = face_table(face_polys, scale_blocks, bwalls, b_openings, stairs, face_texts)
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
    # Milestone 12 (track R): candidates still unknown after their answers are re-read; the extra candidates (the
    # re-read's parts that fit a type) are asked after the core's own, under content keys.
    replaced, loose = _reread_unknowns(ex, cands, extras, symbols, bwalls, b_openings, texts_m, rows, level_id,
                                       file_rel, page_no, s, no_ai, is_raster, non_wall)
    _ask_and_apply(ex, page, extras, wall_polys, others, answers, no_ai, Path(rec_dir) if rec_dir is not None else None,
                   level_id, raster=raster, evidence_only=evidence_only, base=cands)
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
    # 5 Nov 2026 (review): every room label inside the building's hull but in no closed face is a place to check
    # (``reading_places``, building metres): the pipeline carries it on a low-confidence level, RC7 numbers it
    if bwalls:
        faces_now = TP.faces(bwalls, b_openings)
        hull_now = unary_union([TP.wall_polygon(w) for w in bwalls]).convex_hull
        for b in blocks:
            if getattr(b, "exterior", False) or TP._outdoor_label(b):
                continue
            q = Point(b.anchor)
            if hull_now.contains(q) and not any(f.contains(q) for f in faces_now):
                ex.reading_places.append({"kind": "unplaced_label", "text": b.name,
                                          "at": [round(b.anchor[0] - ox, 4), round(b.anchor[1] - oy, 4)],
                                          "note": "a room label inside the walls' hull but in no closed face"})
    for w in bwalls:
        _shift_wall(w, sh)
    # Fix round after P6b: the walls and gaps the openings rules corrected, in the building frame (never silent).
    ex.notes.extend(f"{where}: {n}" for n in gap_rule_notes(gap_log, bwalls, (ox, oy)))
    for o in b_openings + seps:
        _shift_opening(o, sh)
    furniture = list(pieces)
    for c in cands:
        furniture.extend(replaced.get(c["key"], [c["item"]]))
    furniture += loose + [c["item"] for c in extras]
    for f in furniture:
        _shift_piece(f, sh)
    _shift_site(site, sh)
    for sym in symbols:
        sym["center"] = [round(sym["center"][0] - ox, ROUND), round(sym["center"][1] - oy, ROUND)]
        sym["level_id"] = level_id
    ex.report["symbols"] = symbols
    # 5 Nov 2026 (Milestone 14 R3): the decision records in building metres with a provisional final answer read off
    # this level; every ranker decision is a page note. 6 Nov 2026 (review): the final answers and the undecided places
    # are made again from the built level at the end of the pipeline (``pipeline._finish_decisions``), after the passes
    # that still change openings and walls
    ex.report["decisions"] = decisions.finalize((ox, oy), bwalls, b_openings)
    ex.report["decisions_summary"] = decisions.summary()
    for rec in ex.report["decisions"]:
        if rec.get("decided_by") == DEC.DECIDED_RANKER and rec.get("ranker_answer"):
            ex.notes.append(f"{where}: gap at ({rec['place'][0]:.2f}, {rec['place'][1]:.2f}) m: the ranker decided "
                            f"{rec['ranker_answer']} (margin {rec.get('margin', 0):.2f}) over the rule's "
                            f"{rec['rule_answer']} ({rec['rule']} {rec['rule_confidence']:.2f})")
    for row in sep_log:
        if row.get("line"):
            row["line_building"] = [list(sh.p(q)) for q in row["line"]]
    ex.walls = bwalls
    ex.openings = b_openings
    ex.separators = seps
    ex.furniture = furniture
    ex.site = site
    # The candidates as asked (page metres, the crop and hash inputs); their FurnitureItems are in ex.furniture.
    ex.candidates = [{k: v for k, v in c.items() if k not in ("item", "_ids", "_part")} for c in cands + extras]
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
