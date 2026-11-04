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
    before = (getattr(w, "corrected_by_ai", None) or {}).get("before")
    if before:
        # Fix round after P6b (23 Oct 2026): the wall a lined gap split (``openings._mark_lined``) as it was before.
        before["start"], before["end"] = list(sh.p(before["start"])), list(sh.p(before["end"]))


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


def _outdoor_outlines(ex, where: str, site: dict, strokes: list, outline, walls: Optional[list] = None) -> None:
    """The outline of every labelled outdoor space without a closed face, closed from the drawn strokes around its
    label (page metres; ``wenart.levels.outdoor.read_outline``), as ``outline_inferred`` on its site area; never
    silent (a note per space). 3 Nov 2026 (real09, user: "are you showing the balkons here?"; the drafter named the
    balcony of one flat only): on a plan of two mirrored halves (``facade.mirror_axis`` of ``walls``) a read outdoor
    space with no label at its mirror gets a twin there, read from the strokes around the mirrored anchor the same
    way (its label the twin's, ``label_inferred``)."""
    import copy as _copy

    from wenart.ingest.generic import facade as FC
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
    axis = FC.mirror_axis(walls, FC.MIRROR_FIX_SHARE) if walls else None
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


# --------------------------------------------------------------------------
# Faces
# --------------------------------------------------------------------------

CAVITY_WIDTH_M = 0.24      # real10: an unlabelled face no 24 cm strip fits into is a cavity between two walls


def face_table(face_polys: list, blocks: list, walls: list, openings: list, stairs: list) -> list[dict]:
    """One row per face (page metres): ``{"polygon", "names" (indoor blocks), "exterior" (only exterior blocks),
    "room_type", "label", "reason"}``; unlabelled faces are typed by ``topology.unlabelled_face_type``. real10
    (1 Nov 2026): an unlabelled face narrower than ``CAVITY_WIDTH_M`` everywhere (it vanishes when shrunk by half of
    it: the 3-4 cm slits between a masonry wall and the plaster wall drawn beside it, 0.01-0.1 m2) is no room."""
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


def _outer_gaps(ex, where: str, walls2: list, openings: list, blocks: list, level_id, site_warnings: list,
                problem: Optional[str] = None, strokes: Optional[list] = None):
    """The wide gaps of the outer ring bridged (``wide_gaps``): the candidate bridges on the bridged building's
    outline are kept when the walls then close, or close in more labelled rooms; None when nothing improves."""
    from wenart.ingest.generic import wide_gaps as WG

    cands = WG.bridges(walls2)
    # 3 Nov 2026: the glazed runs (``joinery_bridges``) are left to the facade closure that follows (``facade``): its
    # walls follow the frames and carry the windows and doors drawn on them, where a run's bridge was a hole
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


def _runs_on(w, d, p) -> bool:
    """A wall running straight on past point ``p`` in direction ``d`` (parallel within about 5 degrees, reaching ahead
    of ``p``): the end at ``p`` is a joint inside one wall run, not a corner."""
    (x0, y0), (x1, y1) = tuple(w.start), tuple(w.end)
    L = math.hypot(x1 - x0, y1 - y0)
    if L <= 1e-9 or abs((x1 - x0) / L * d[1] - (y1 - y0) / L * d[0]) >= 0.09:
        return False
    return max((q[0] - p[0]) * d[0] + (q[1] - p[1]) * d[1] for q in ((x0, y0), (x1, y1))) > JOIN_TOUCH_M


def ring_ends(walls2: list, bwalls: list, b_openings: list) -> list:
    """Every end of a building wall on the outer ring (within ``CLOSURE_END_TOL_M`` of ``topology.building_outline``'s
    boundary): ``(wall index, "start"/"end", point, outward unit direction, half thickness, free)``. ``free`` when no
    other wall touches the end (``JOIN_TOUCH_M``); else a *corner end*: the walls it touches turn away from it, none
    runs straight on past it (``_runs_on``: that end would be a joint inside one wall run). A corner end matters where
    a facade is drawn without walls (real11: the kitchen's glazed front runs from the shaft wall's corner to the
    salon wall's corner): the wall may run on past the corner along what is drawn."""
    polys = [TP.wall_polygon(w) for w in walls2]
    building = {id(w) for w in bwalls}
    outline = TP.building_outline(bwalls, b_openings)
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


def _stroke_lines(strokes: list) -> list:
    """The drawn lines (no arcs, at least ``CLOSURE_SUPPORT_LINE_M`` long) a bridge may run along."""
    out = []
    for st in strokes or ():
        pts = [tuple(p) for p in (getattr(st, "pts", None) or [])]
        if len(pts) < 2 or getattr(st, "arc", None):
            continue
        line = LineString(pts)
        if line.length >= CLOSURE_SUPPORT_LINE_M:
            out.append(line)
    return out


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
                       ends: Optional[list] = None, outline=None) -> list[dict]:
    """The bridges the outer ring's ends suggest (pure; page metres), from every wall end on the building outline
    (``ring_ends``: free ends, and corner ends where the wall may run on past the corner):

    - *straight*: the wall run on along its own axis, in a band of its thickness, to the first building wall it meets
      within ``CLOSURE_MAX_M`` (the end of the wall across the gap, or the side of a wall: the end and the outline),
      beyond what ``_short_joins`` joins (``JOIN_MAX_M``);
    - *corner*: two ends whose axes cross ahead of both within ``CLOSURE_MAX_M`` (a glazed corner: both walls run on
      to the corner) when the walls turn by at least 30 degrees (``CORNER_MIN_SIN``) and the corner is farther than
      ``CORNER_MAX_M`` from one of them (nearer corners are ``_short_joins``' work).

    Each candidate: ``{"kind", "ends": [(wall index, which)], "src": [the walls], "segments": [(a, b)], "length",
    "free": every end free, "support": the share of its length drawn lines run along (``support_share``, within half
    the ``thickness`` + ``CLOSURE_SUPPORT_TOL_M``), "outline_dist": how far it runs inside the drawn ``outline`` (the
    length-weighted mean distance of its ends and middles to the outline's boundary; 0 without one), "from", "to"}``,
    the free-end candidates first, then the ones nearest the drawn outline (a facade before a counter line), the
    shortest first. None between the two pieces of one split wall (``_same_split_wall``: a recess opened on
    purpose)."""
    from shapely.strtree import STRtree

    polys = [TP.wall_polygon(w) for w in walls2]
    building = {id(w) for w in bwalls}
    if ends is None:
        ends = ring_ends(walls2, bwalls, b_openings)
    if not ends:
        return []
    lines = _stroke_lines(strokes)
    tree = STRtree(lines) if lines else None
    tol = thickness / 2.0 + CLOSURE_SUPPORT_TOL_M

    def support(segs) -> float:                       # length-weighted over the segments (a door jamb's segment is short)
        total = sum(math.dist(a, b) for a, b in segs)
        if tree is None or total <= 1e-9:
            return 0.0
        return sum(support_share(s, lines, tree, tol) * math.dist(*s) for s in segs) / total

    ring_d = outline.boundary if outline is not None and not outline.is_empty else None

    def inside(segs) -> float:                        # length-weighted mean distance to the drawn outline's boundary
        total = sum(math.dist(a, b) for a, b in segs)
        if ring_d is None or total <= 1e-9:
            return 0.0
        return sum(sum(ring_d.distance(Point(q)) for q in (a, b, ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0))) / 3.0
                   * math.dist(a, b) for a, b in segs) / total

    def name(k, which, p) -> str:
        return f"{walls2[k].entity.split(',')[0]} {which} at ({p[0]:.2f}, {p[1]:.2f})"

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
            if d > JOIN_MAX_M and (best is None or d < best[0]):
                best = (d, j)
        if best is None:
            continue
        d, j = best
        if _same_split_wall(walls2[k], walls2[j], (dx, dy), (px, py), tuple(walls2[j].start)):
            continue
        q = (round(px + dx * (d + 0.01), 4), round(py + dy * (d + 0.01), 4))
        segs = [((px, py), q)]
        out.append({"kind": "straight", "ends": [(k, which)], "src": [walls2[k]], "segments": segs, "length": d,
                    "free": free, "support": support(segs), "outline_dist": inside(segs),
                    "from": name(k, which, (px, py)),
                    "to": f"{walls2[j].entity.split(',')[0]} ({d:.2f} m along the wall's axis)"})
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
            out.append({"kind": "corner", "ends": [(ka, wa), (kb, wb)], "src": [walls2[ka], walls2[kb]],
                        "segments": segs, "length": max(ta, 0.0) + max(tb, 0.0), "free": fa and fb,
                        "support": support(segs), "outline_dist": inside(segs), "from": name(ka, wa, pa),
                        "to": f"{name(kb, wb, pb)}; corner at ({corner[0]:.2f}, {corner[1]:.2f})"})
    return sorted(out, key=lambda c: (0 if c["free"] else 1, round(c["outline_dist"], 1), c["length"]))


def _closure_walls(cands: list[dict], thickness: float, file_rel: str, page_no, problem) -> list:
    """The inferred ``WallItem``s of the chosen candidates: the median outer thickness, evidence method ``inferred``,
    confidence ``CLOSURE_CONFIDENCE``, rule ``OUTLINE_CLOSURE_RULE``, a note naming the two wall ends and the gap,
    ``inferred`` and status ``unverified`` (the schema's wall status has no third word; ``inferred: true`` says it)."""
    out = []
    for n, c in enumerate(cands, start=1):
        src = c["src"][0]
        ents = "+".join(w.entity.split(",")[0] for w in c["src"])
        for m, (a, b) in enumerate(c["segments"], start=1):
            ev = B.evidence(file_rel, "inferred", CLOSURE_CONFIDENCE, page=page_no, entity=f"closure:{ents}",
                            rule=OUTLINE_CLOSURE_RULE)
            ev["note"] = (f"the outer ring did not close ({problem or 'a room label in no closed face'}): a "
                          f"{c['length']:.2f} m gap from {c['from']} to {c['to']} bridged along the outline "
                          f"({c['kind']}, segment {m} of {len(c['segments'])}, drawn lines along {c['support']:.0%} of "
                          f"it); thickness {thickness:.2f} m (the median outer wall); confidence {CLOSURE_CONFIDENCE:g}:"
                          f" check it on the comparison sheet")
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
    wall across the gap or the wall it meets sideways (*straight*), or two ends run on to the corner where their axes
    cross (*corner*: a glazed corner) (``closure_candidates``), up to ``CLOSURE_MAX_M``, in up to ``CLOSURE_ROUNDS``
    rounds (a chain of gaps). Every bridge gets the median outer wall thickness (``_outer_thickness``), evidence
    method ``inferred``, rule ``outline_closure`` and a note naming the two wall ends and the gap length; the door and
    window symbols drawn across the bridges are read onto them (``openings.openings_on_walls``), frames running along
    them give unverified windows (``facade.frame_windows``): nothing is invented.

    The outline: ``drawn_outline`` finds the plan's drawn outline as ``sheets.register.outline`` does (the long
    strokes grown by 0.75 m, merged, the holes filled, shrunk back). It is the guard, not the generator: a grow-and-
    shrink outline cuts a glazed corner (two walls stopping short of a corner leave a notch that no closing fills)
    and bulges over a balcony's railing, so the walls' own axes give the bridges and the drawn outline says where no
    bridge may go: none beyond the drawn outline grown by ``CLOSURE_OUTLINE_TOL_M`` (nothing is built past what is
    drawn). ``topology.building_outline`` of the walls says which ends are on the outer ring. A bridge from a corner
    end needs the drawing's support: drawn lines (frames, a glazed run) along at least ``CLOSURE_SUPPORT_MIN`` of its
    length, it runs along the drawn outline (every point within ``CLOSURE_ON_OUTLINE_M`` of its boundary: real11's
    kitchen counter line, 1.9 m inside the facade, had lines along all of it and is no facade), and it may not close
    an unlabelled space over ``CLOSURE_UNLABELLED_MAX_M2`` (a courtyard, a terrace, a niche) into the building; a
    free end is an evident gap and needs none of these.

    Never: across or beside a drawn door or window already read (``_join_clear``); within ``CLOSURE_OUTDOOR_CLEAR_M``
    of a balcony or terrace label, or enclosing one (a drawn balcony outline stays outside; the plot split keeps the
    site); between the two pieces of a wall the recess passes split on purpose; through a wall end another bridge of
    the round already uses. Kept only when the ring then closes, or more labelled rooms close (the rule of
    ``_short_joins``); then every bridge not needed for that is dropped again (the longest first). Never silent:
    ``ex.notes`` (one line per bridge), ``ex.warnings`` (the summary) and ``ex.report["outline_closure"]`` (every
    candidate, kept or refused, with the reason). Returns the 7-tuple of the other passes, or None when nothing
    closes (the level is then built marked under ``failed_levels: build_marked``, its reasons on the level)."""
    from wenart.ingest.generic import facade as FC

    report: dict = {"problem": problem, "unclosed_before": _unclosed(site_warnings), "kept": [], "refused": []}
    ex.report["outline_closure"] = report
    outline = drawn_outline(strokes, walls2, exclude)
    guard = outline.buffer(CLOSURE_OUTLINE_TOL_M, join_style=2) if outline is not None else None
    if outline is not None:                           # the debug image and the report show what guarded the bridges
        report["outline"] = [[round(x, 3), round(y, 3)] for x, y in outline.simplify(0.05).exterior.coords]
    outdoor = [Point(b.anchor) for b in blocks if TP._outdoor_label(b)]
    indoor = [Point(b.anchor) for b in blocks if not getattr(b, "exterior", False) and not TP._outdoor_label(b)]
    thickness, how = _outer_thickness(bwalls, b_openings)
    report["thickness"] = {"m": thickness, "how": how}

    def check(ws):
        bw, site, sw = TP.split_plot(ws, openings, blocks, level_id=level_id)
        idx = {o["index"] for o in site["openings"]}
        b_open = [o for j, o in enumerate(openings) if j not in idx]
        return bw, site, sw, b_open, TP.outer_loop_problem(bw, b_open)

    def refuse(c, why):
        report["refused"].append({"kind": c["kind"], "from": c["from"], "to": c["to"], "length_m": round(c["length"], 3),
                                  "support": round(c["support"], 2), "free": c["free"],
                                  "outline_dist": round(c["outline_dist"], 2), "why": why})

    def touches(c, faces) -> bool:
        return any(LineString([a, b]).distance(f) <= 0.05 for a, b in c["segments"] for f in faces)

    before = _unclosed(site_warnings)
    chosen: list[dict] = []
    cur_walls, cur_b, cur_bo = list(walls2), list(bwalls), list(b_openings)
    faces_before = TP.faces(bwalls, b_openings)
    for _round in range(CLOSURE_ROUNDS):
        used: set = set()
        added = []
        for c in closure_candidates(cur_walls, cur_b, cur_bo, strokes, thickness, outline=outline):
            if any(e in used for e in c["ends"]):
                refuse(c, "a bridge of this round uses that wall end already")
                continue
            if not c["free"] and c["support"] < CLOSURE_SUPPORT_MIN:
                refuse(c, f"it runs on past a corner with drawn lines along {c['support']:.0%} of it only (a free "
                          f"end is an evident gap; a corner needs the drawing's support)")
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
            if any(LineString([a, b]).distance(q) <= CLOSURE_OUTDOOR_CLEAR_M for a, b in c["segments"] for q in outdoor):
                refuse(c, "a balcony or terrace label stands beside it (an outdoor space, not a room)")
                continue
            used.update(c["ends"])
            added.append(c)
        if not added:
            break
        trial = cur_walls + _closure_walls(added, thickness, file_rel, page_no, problem)
        bw, site, sw, b_open, prob = check(trial)
        # a bridge that closes a balcony or terrace label into a new face encloses an outdoor space; one from a corner
        # that closes an unlabelled space (a courtyard, a niche) into the building has no drawing behind it: dropped
        new_faces = [f for f in TP.faces(bw, b_open) if not any(g.contains(f.representative_point()) for g in faces_before)]
        bad = [f for f in new_faces if any(f.contains(q) for q in outdoor)]
        blank = [f for f in new_faces if f.area > CLOSURE_UNLABELLED_MAX_M2 and not any(f.contains(q) for q in indoor)]
        keep = []
        for c in added:
            if touches(c, bad):
                refuse(c, "it would close a balcony or terrace label into a room")
            elif not c["free"] and touches(c, blank):
                refuse(c, f"it would close an unlabelled space over {CLOSURE_UNLABELLED_MAX_M2:g} m2 into the building")
            else:
                keep.append(c)
        if len(keep) != len(added):
            added = keep
            if not added:
                break
            trial = cur_walls + _closure_walls(added, thickness, file_rel, page_no, problem)
            bw, site, sw, b_open, prob = check(trial)
        chosen += added
        cur_walls, cur_b, cur_bo = trial, bw, b_open
        if prob is None and _unclosed(sw) == 0:
            break
    if not chosen:
        ex.notes.append(f"{where}: outline closure: no bridge for the open outer ring "
                        f"({problem or 'labels in no closed face'}); {len(report['refused'])} candidate(s) refused")
        return None
    bw, site, sw, b_open, prob = check(walls2 + _closure_walls(chosen, thickness, file_rel, page_no, problem))
    after = _unclosed(sw)
    if not (after < before or (problem is not None and prob is None and after <= before)):
        for c in chosen:
            refuse(c, f"the walls do not close with it either (labels in no closed face {before} -> {after}, "
                      f"{prob or 'the ring closes'})")
        ex.notes.append(f"{where}: outline closure: {len(chosen)} bridge(s) tried along the outline, the walls do not "
                        f"close with them (labels in no closed face {before} -> {after}; {prob or 'the ring closes'}):"
                        f" not used")
        return None
    # only the bridges the closing needs stay: the ones farthest inside the drawn outline dropped first (a counter line
    # closes a kitchen as well as its facade does; the facade is kept), then the longest
    for c in sorted(list(chosen), key=lambda c: (-round(c["outline_dist"], 1), -c["length"])):
        rest = [x for x in chosen if x is not c]
        if not rest:
            break
        r2 = check(walls2 + _closure_walls(rest, thickness, file_rel, page_no, problem))
        if _unclosed(r2[2]) <= after and (r2[4] is None or prob is not None):
            refuse(c, "not needed: the walls close as well without it")
            chosen = rest
            bw, site, sw, b_open, prob = r2
    new_walls = _closure_walls(chosen, thickness, file_rel, page_no, problem)
    # the door and window symbols drawn across the bridges, and the frames running along them (nothing invented)
    taken = set(owned) if owned is not None else set()
    read = O.openings_on_walls(new_walls, list(strokes), file_rel, page_no, units_to_m=units_to_m, owned=taken)
    framed = FC.frame_windows(new_walls, list(strokes), read, walls2)
    if owned is not None:
        owned.update(taken)
    all_walls, all_open = walls2 + new_walls, list(openings) + read + framed
    bw, site, sw = TP.split_plot(all_walls, all_open, blocks, level_id=level_id)
    idx = {o["index"] for o in site["openings"]}
    b_open = [o for j, o in enumerate(all_open) if j not in idx]
    prob = TP.outer_loop_problem(bw, b_open)
    for c in chosen:
        report["kept"].append({"kind": c["kind"], "from": c["from"], "to": c["to"], "length_m": round(c["length"], 3),
                               "support": round(c["support"], 2), "free": c["free"],
                               "outline_dist": round(c["outline_dist"], 2),
                               "segments": [[list(a), list(b)] for a, b in c["segments"]]})
        ex.notes.append(f"{where}: outline closure ({c['kind']}, confidence {CLOSURE_CONFIDENCE:g}): a {c['length']:.2f} m "
                        f"gap of the outer ring from {c['from']} to {c['to']} bridged by {len(c['segments'])} inferred "
                        f"wall(s) of {thickness:.2f} m ({how}); drawn lines along {c['support']:.0%} of it"
                        + ("" if c["free"] else "; the wall runs on past a corner"))
    report.update(unclosed_after=_unclosed(sw), problem_after=prob, openings_read=len(read), windows_framed=len(framed))
    ex.warnings.append(f"{where}: the outer ring did not close ({problem or 'room label(s) in no closed face'}): "
                       f"{len(new_walls)} inferred wall(s) bridge {len(chosen)} gap(s) along the outline at confidence "
                       f"{CLOSURE_CONFIDENCE:g} (rule {OUTLINE_CLOSURE_RULE}; {len(read)} drawn opening(s) read on them, "
                       f"{len(framed)} unverified window(s) where frames run along them; labels in no closed face "
                       f"{before} -> {_unclosed(sw)}): check them on the comparison sheets (reading check RC7)")
    return all_walls, all_open, bw, site, sw, b_open, prob


SIZE_TAG_RE = re.compile(r"^\s*(\d{2,3})\s*/\s*(\d{2,3})\s*$")   # a window's size tag: width/height in cm
TAG_REACH_M = 0.8               # a size tag stands this close to the wall of its window ...
TAG_ANGLE_DEG = 15.0            # ... written along it
TAG_SHIFT_M = 0.35              # the tagged window moves at most this far to clear a column, a wall end or a door
TAG_COLLINEAR_M = 0.08          # a wall piece on the host's line (this close to its axis) is the same wall run
FULL_GLASS_M = 2.0              # a tagged window this high starts at the floor (a shop window: full glass) ...
WINDOW_HEAD_M = 2.2             # ... a lower one has its head at the usual lintel height (its sill assumed from it)


def _window_tags(ex, where: str, walls2: list, openings: list, texts_m: list, units_to_m: float):
    """4 Nov 2026 (real17 L0, user: "these sections could be full windows glass, check it"): a window size tag ("470/240",
    width/height in cm, on a window text layer) written along a wall within ``TAG_REACH_M`` is that wall's window: one
    window of that width and height, centred at the tag and moved up to ``TAG_SHIFT_M`` to clear the columns, the run's
    ends and the doors; the windows read inside its span are replaced (a frame read as wall, a frame split into small
    windows). A window ``FULL_GLASS_M`` or higher starts at the floor, a lower one ends at ``WINDOW_HEAD_M`` (its sill
    assumed). Returns the new openings or None."""
    from wenart.ingest.generic import layer_names as LN
    from wenart.ingest.model import OpeningItem

    tags = []
    for t in texts_m:
        m = SIZE_TAG_RE.match(t.text or "")
        layer = (t.evidence[0].get("layer") if t.evidence else None)
        if m and LN.layer_role(layer) in ("window", "glass") \
                and not _door_like_tag(t, int(m.group(1)), int(m.group(2)), openings):
            tags.append((t, int(m.group(1)) / 100.0, int(m.group(2)) / 100.0))
    if not tags or not walls2:
        return None
    polys = [TP.wall_polygon(w) for w in walls2]
    out = list(openings)
    done, skipped = [], []
    for t, width, height in tags:
        cx, cy = (t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0
        r = math.radians(t.rotation_deg or 0.0)
        td = (math.cos(r), math.sin(r))
        best = None
        for k, w in enumerate(walls2):
            (x0, y0), (x1, y1) = tuple(w.start), tuple(w.end)
            L = math.hypot(x1 - x0, y1 - y0)
            if L < 0.3:
                continue
            ux, uy = (x1 - x0) / L, (y1 - y0) / L
            if abs(td[0] * uy - td[1] * ux) > math.sin(math.radians(TAG_ANGLE_DEG)):
                continue
            s_ = (cx - x0) * ux + (cy - y0) * uy
            d = abs(-(cx - x0) * uy + (cy - y0) * ux)
            if d <= TAG_REACH_M and -0.1 <= s_ <= L + 0.1 and (best is None or d < best[0]):
                best = (d, k, (x0, y0), (ux, uy), s_)
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
        for j, o in enumerate(out):
            if o.kind == "door" and abs(off(o.center)) <= h + 0.05:
                a = along(o.center)
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
        out = [o for o in out if all(o is not g for g in gone)]
        mid = (a0 + a1) / 2.0
        ev = dict(t.evidence[0]) if t.evidence else {}
        ev.update(method="vector", confidence=0.9, rule="size_tag",
                  reason=f"the window size tag '{t.text}' (width/height in cm) beside the wall")
        full = height >= FULL_GLASS_M
        out.append(OpeningItem(kind="window", width=round(a1 - a0, 3),
                               center=(round(x0 + ux * mid, 4), round(y0 + uy * mid, 4)),
                               rotation_deg=math.degrees(math.atan2(uy, ux)),
                               box=[v / units_to_m for v in t.box], entity=t.id, evidence=ev, height=height,
                               sill=0.0 if full else round(max(0.0, WINDOW_HEAD_M - height), 2),
                               assumed=[] if full else ["sill_height"],
                               type_raw=f"window size tag {t.text.strip()}"))
        done.append(f"{t.text.strip()} ({len(gone)} read window(s) replaced"
                    + (f", {a1 - a0:.2f} m free" if a1 - a0 < width - 1e-3 else "") + ")")
    if done:
        ex.notes.append(f"{where}: {len(done)} window(s) set by their size tags: " + ", ".join(done[:12]))
    if skipped:
        ex.notes.append(f"{where}: window size tags not used: " + "; ".join(skipped[:8]))
    return out if done else None


DOOR_TAG_REACH_M = 1.2          # 4 Nov 2026 (UL321): a door size tag stands this close to its door's gap
DOOR_TAG_KINDS = ("opening", "window", "door")


def _door_like_tag(t, w_cm: int, h_cm: int, openings: list) -> bool:
    """4 Nov 2026 (real07: every size tag, doors' and windows', on the joinery layer DOĞRAMA): a tag on a window or joinery
    layer is a door's when it is door-high (>= 200 cm) and door-wide (<= 120 cm) and the nearest opening within
    ``DOOR_TAG_REACH_M`` is a door or a gap, not a window."""
    if h_cm < 200 or w_cm > 120:
        return False
    c = ((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0)
    near = [(math.dist(c, tuple(o.center)), o) for o in openings if not o.virtual]
    near = [x for x in near if x[0] <= DOOR_TAG_REACH_M]
    if not near:
        return False
    o = min(near, key=lambda x: x[0])[1]
    return o.kind in ("door", "opening") or "gap" in str(o.type_raw or "")


def _door_tags(ex, where: str, walls2: list, openings: list, texts_m: list, units_to_m: float,
               keep_width: bool = False):
    """4 Nov 2026 (real07, user: "the entrance to the room is wrong door not recognized properly", "where is the
    entrance to the bus wc you missed the door"; lesson UL321): a door size tag ("80/210", width/height in cm, on a door
    text layer; written along the leaf, so at any angle) is the door of the nearest unclassified gap, window-typed gap
    or door within ``DOOR_TAG_REACH_M``: a door of that width and height, centred where the gap is; a gap read wider
    than the door keeps the rest as wall. Returns the new openings or None."""
    from wenart.ingest.generic import layer_names as LN
    from wenart.ingest.model import OpeningItem

    tags = []
    for t in texts_m:
        m = SIZE_TAG_RE.match(t.text or "")
        layer = (t.evidence[0].get("layer") if t.evidence else None)
        if m and (LN.layer_role(layer) == "door" or (LN.layer_role(layer) == "window"
                                                     and _door_like_tag(t, int(m.group(1)), int(m.group(2)), openings))):
            tags.append((t, int(m.group(1)) / 100.0, int(m.group(2)) / 100.0))
    if not tags:
        return None
    out = list(openings)
    taken: set = set()
    done = []
    for t, width, height in tags:
        c = ((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0)
        best = None
        for j, o in enumerate(out):
            if j in taken or o.virtual or o.kind not in DOOR_TAG_KINDS:
                continue
            if o.kind == "window" and "gap" not in str(o.type_raw or ""):
                continue                                       # a drawn window keeps its kind
            if o.kind == "door" and abs(float(o.width) - width) <= 0.05:
                continue                                       # already the tagged door
            d = math.dist(c, tuple(o.center))
            if d <= DOOR_TAG_REACH_M and (best is None or d < best[0]):
                best = (d, j)
        if best is None:
            continue
        j = best[1]
        o = out[j]
        ev = dict(t.evidence[0]) if t.evidence else {}
        ev.update(method="vector", confidence=0.9, rule="size_tag",
                  reason=f"the door size tag '{t.text.strip()}' (width/height in cm) beside the gap")
        new_w = float(o.width) if keep_width and float(o.width) > width else width
        out[j] = dataclasses.replace(o, kind="door", width=round(new_w, 3), height=height, evidence=ev,
                                     type_raw=f"door size tag {t.text.strip()}",
                                     assumed=[a for a in (o.assumed or []) if a != "height"])
        taken.add(j)
        done.append(f"{t.text.strip()} ({o.kind} {float(o.width):.2f} m -> door {new_w:.2f} m)")
    if done:
        ex.notes.append(f"{where}: {len(done)} door(s) set by their size tags: " + ", ".join(done[:12]))
        return out
    return None


RECESS_MAX_M2 = 15.0


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

    from wenart.ingest.generic import facade as FC

    faces = TP.faces(walls2, openings)
    if not faces:
        return None
    outline = TP.building_outline(walls2, openings)
    anchors = [Point(b.anchor) for b in blocks]
    # 3 Nov 2026 (real10, user: "this section is still wrong should be similar as the mirror"): on a plan of two
    # mirrored halves, the recess's twin decides when its own window could not be read
    axis = FC.mirror_axis(walls2, FC.MIRROR_FIX_SHARE)
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
                        if p.kind == "window" or (getattr(p, "type_raw", None) == UNCLASSIFIED
                                                  and p.width <= RECESS_WINDOW_MAX_M):
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


def _mirror_consistency(ex, where: str, walls2: list, openings: list, blocks: list, level_id, site_warnings: list,
                        problem: Optional[str]):
    """The mirror fixes of a plan of two mirrored halves (``mirror.consistency``), step by step (thickness, inferred
    walls, missing walls, openings): a step that changes a drawn wall (thickness, an inferred wall onto its twin's
    line) is kept when more rooms pair as mirror images, one that copies a missing wall or an opening of the twin when
    no fewer pair; always with no labelled room left open, the outer walls closed and at most
    ``MIRROR_MAX_NEW_WALLS`` walls copied. 3 Nov 2026 (real10's 1st basement: six walls read 0.5-0.9 m
    thick on one half, a missing wall and seven openings; together they paired one room fewer and none was kept)."""
    from wenart.ingest.generic import facade as FC
    from wenart.ingest.generic import mirror as MR

    axis = FC.mirror_axis(walls2, FC.MIRROR_FIX_SHARE)
    if axis is None:
        return None
    before = MR.mirrored_face_pairs(walls2, openings, axis)
    base_unclosed = _unclosed(site_warnings)
    # 3 Nov 2026 (real10, user: "core stairs and elevators and that section is shaft usually": the lift shaft's wall
    # was copied into the stair beside it): the core around a lift label is not mirrored
    from wenart.sheets import register as RG_
    from wenart.sheets import titles as TI_
    lifts = [Point(b.anchor).buffer(CORE_KEEP_OUT_M) for b in blocks
             if RG_.LIFT_RE.search(TI_.fold(str(getattr(b, "name", "") or "")))]
    keep_out = unary_union(lifts) if lifts else None
    kept_steps: list = []
    best = None
    notes = []
    for step in MR.STEPS:
        res = MR.consistency(walls2, openings, axis, steps=tuple(kept_steps + [step]), keep_out=keep_out)
        if res is None:
            continue
        w5, o5, log = res
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


def _glazed_facades(ex, where: str, walls2: list, openings: list, blocks: list, level_id, site_warnings: list,
                    problem: Optional[str], strokes: list, file_rel: str, page_no, s: float, owned: set):
    """The open rooms closed along their facades of window and door frames (``facade``): the inferred walls carry
    the windows and doors drawn across them (``openings.openings_on_walls``), and an unverified window where frames
    run along a wall and no symbol reads; kept when they close in more labelled rooms (or close the outer loop)."""
    from wenart.ingest.generic import facade as FC

    anchors = _open_anchors(walls2, openings, blocks)
    if not anchors:
        return None
    # the mirrored twins of the labelled rooms where the drafter named one flat only (real09)
    faces_now = TP.faces(walls2, openings)
    hull = unary_union([TP.wall_polygon(w) for w in walls2]).convex_hull
    labelled = [tuple(b.anchor) for b in blocks if not getattr(b, "exterior", False)
                and getattr(b, "room_type", None) != "balcony"]
    seeds = FC.mirror_seeds(walls2, labelled, lambda q: hull.contains(Point(q))
                            and not any(f.contains(Point(q)) for f in faces_now))
    faces, links = FC.close_rooms(walls2, strokes, anchors + seeds)
    if not faces:
        return None
    new_walls = FC.facade_wall_items(walls2, list(faces.values()), openings, file_rel, page_no, units_to_m=s)
    if not new_walls:
        return None
    taken = set(owned)
    read = O.openings_on_walls(new_walls, strokes, file_rel, page_no, units_to_m=s, owned=taken)
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
    ex.notes.append(f"{where}: {len(faces)} room(s) closed along facades of window and door frames (rule glazed_facade):"
                    f" {len(new_walls)} inferred wall(s), {len(links)} gap link(s) up to {FC.LINK_M:g} m, "
                    f"{len(read)} drawn opening(s) read on them, {len(framed)} unverified window(s) where frames run "
                    f"along them; labels in no closed face {before} -> {after}")
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
    prims = W.wall_primitives(page, s, frozenset(i for d in dims if d.how != "dimension_entity" for i in d.stroke_ids))
    mask = W.wall_mask(page, prims, s)
    prim_ids = {i for p in prims for i in p.stroke_ids}
    walls, wall_info = W.walls_from_mask(mask, [st for st in strokes_m if st.id not in prim_ids], file_rel, page_no,
                                         units_to_m=s)
    ex.warnings.extend(f"{where}: {w}" for w in wall_info.get("warnings", []))
    wall_strokes = prim_ids - set(wall_info.get("dropped_strokes", []))
    non_wall = [st for st in strokes_m if st.id not in wall_strokes]
    # (the dimension finder's strokes are not passed: its "two parallel lines around a number" also takes a window's
    # frame lines beside its size tag; the notation is read from the layers, UL296)
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
                                 file_rel, page_no, s, owned)
        if glazed is not None:
            walls2, openings, bwalls, site, site_warnings, b_openings, problem = glazed
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
        mirrored = _mirror_consistency(ex, where, walls2, openings, blocks, level_id, site_warnings, problem)
        if mirrored is not None:
            walls2, openings, bwalls, site, site_warnings, b_openings, problem = mirrored
    if not is_raster:
        # 4 Nov 2026 (real17, user: "these sections could be full windows glass, check it"): a window size tag sets its
        # window (``_window_tags``)
        for keep_width in (False, True):
            doored = _door_tags(ex, where, walls2, openings, texts_m, s, keep_width=keep_width)
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
        tagged = _window_tags(ex, where, walls2, openings, texts_m, s)
        if tagged is not None:
            bw_t, site_t, sw_t = TP.split_plot(walls2, tagged, blocks, level_id=level_id)
            idx = {o["index"] for o in site_t["openings"]}
            b_open_t = [o for j, o in enumerate(tagged) if j not in idx]
            prob_t = TP.outer_loop_problem(bw_t, b_open_t)
            if _unclosed(sw_t) <= _unclosed(site_warnings) and (prob_t is None or problem is not None):
                openings, bwalls, site, site_warnings, b_openings, problem = tagged, bw_t, site_t, sw_t, b_open_t, prob_t
            else:
                ex.notes.append(f"{where}: the windows of the size tags left out: they would open the walls")
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
    _outdoor_outlines(ex, where, site, non_wall, outline, bwalls)
    # 3 Nov 2026 (real09, user: "each duplex flat has its inner stair and a 'galeri' void over the floor below"): the
    # voids the plan labels (galeri, boşluk, void, open to below ...) with their drawn outlines (generic.voids)
    from wenart.ingest.generic import voids as VD
    site["voids"] = VD.read_voids(texts_m, strokes_m)
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
        if sn_polys:
            extras = [e for e in extras if not any(q.buffer(-0.05).contains(Point(e["footprint"]["center"]))
                                                   for q in sn_polys)]
    stairs = [p for p in pieces if p.type == "stair"]
    from wenart.ingest.generic import facade as FC_
    seps, sep_log = TP.separators(bwalls, b_openings, gap_log, blocks, stairs, units_to_m=s,
                                  axis=FC_.mirror_axis(bwalls, FC_.MIRROR_FIX_SHARE))
    rows = face_table(TP.faces(bwalls, b_openings, seps), blocks, bwalls, b_openings, stairs)
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
        rows = face_table(face_polys, blocks, bwalls, b_openings, stairs)
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
