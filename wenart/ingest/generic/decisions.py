"""The reader's decision records (5 Nov 2026, Milestone 14 track R3 step 1; user: "I want structure recognition to be
cumulatively better with the feedbacks I am giving").

What: every decision the reader makes of the kinds ``gap_kind`` (a gap in a wall run: door | window | opening | closed |
open, the answer of the rule cascade of ``openings.classify_gap``) and ``wall_or_notation`` (a pair of parallel face
lines the wall reader ``walls.face_pair_walls`` keeps as a wall piece or drops as the drawing's notation) becomes one
record: ``{kind, id, level_id, place [x, y] (building metres), axis, features {...}, rule, rule_answer,
rule_confidence, final_answer, decided_by}``. The features are a flat dict of numbers and booleans the rule code
computes anyway (the gap's width and wall thickness, the arcs and lines found, the size tag and labels around it, the
mirror twin's answer; a pair's length, width, layer role, neighbours, dimension chain, text beside it). The rule
confidence comes from ``RULE_CONFIDENCE``, a fixed table with its reasons. ``final_answer`` is the answer after every
later pass: what the built level holds at that place (the opening's type, a wall across the place, or nothing).
``decided_by`` is ``rule`` unless the ranker (``wenart.reading_check.ranker``, step 4) decided: then ``ranker`` with
its ``margin`` and ``scores``. The pipeline saves the records per level as ``reading_check/decisions_<level>.json``.

Why: a correction of the user used to become one hand-written rule and nothing measured whether it helped the other
projects. With one record per decision, the truth (``reading_check.truth``) labels every record (``ranker.label``),
a ranker learns where the rules were wrong, and a feature that no longer matters is a rule that can go. Recording
changes no decision: step 1 is instrumentation only, and the regression set must show no difference.

How: ``DecisionLog`` is created per level by ``core.extract`` and passed down to the wall reader and the gap
classifier; the records are built in the readers' own frames (page metres, the plan's aligned frame for the gaps) and
shifted to building metres in ``finalize``. Pure helpers, no AI, nothing silent: a gap the caller drops after
classification (a buried end without a drawn door) stays in the file with ``final_answer: dropped``.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Optional

KIND_GAP = "gap_kind"
KIND_WALL = "wall_or_notation"
GAP_CLASSES = ("door", "window", "opening", "closed", "open")
WALL_CLASSES = ("wall", "notation")
DECIDED_RULE = "rule"
DECIDED_RANKER = "ranker"
DROPPED = "dropped"                     # a candidate gap the caller discarded after classification (no element)

# The fixed rule confidences (docs/milestone14.md R3 step 1). The number says how often the rule's answer held when the
# user reviewed the readings of 3 and 4 Nov 2026, in round steps; it is the trust the ranker must beat (ranker.RULE_TRUST).
RULE_CONFIDENCE: dict[str, float] = {
    # gap_kind: the cascade of openings.classify_gap, in its order
    "door_swing_arc": 0.95,        # a swing arc hinged at a gap end with the gap's radius: a door is drawn as a door
    "door_named": 0.90,            # a door block (KAPI/DOOR) that opens without a swing (sliding, pocket, folding)
    "door_open_leaf": 0.80,        # a leaf standing open at 90 degrees without an arc (real10's entrance doors)
    "door_sliding_leaf": 0.70,     # one or two thin leaves parallel to the wall, shorter than the gap (no block name)
    "window_glass_3_lines": 0.90,  # three or more line offsets of the window's own, glass between the faces
    "window_2_lines": 0.60,        # two offsets only: a frame and one glass line, or two outlines (real03's 43 ghosts)
    "window_named": 0.85,          # a window block across the gap (real17's fm-win1)
    "window_sliding_sashes": 0.75, # 22 Nov 2026 (UL346, real10 C0085/C0091): sliding leaves on a window layer: sashes
    "window_grille": 0.80,         # 22 Nov 2026 (UL365, real10 C0089): equal bars across the gap at a fine pitch: a
                                   # fixed grille, never a door (``openings._grille_bars``)
    "window_layer_lines": 0.75,    # 23 Nov 2026 (UL368, real10's bathroom windows): lines on a window layer confined to
                                   # the gap that together span it (a frame in pieces round a sash)
    "window_raster": 0.60,         # a scan's traced lines (their ends and offsets carry the tracing's error)
    "closed_narrow": 0.95,         # a gap under GAP_MIN_M: a drawing crack, never an opening
    "closed_inside_wall": 0.90,    # other wall pieces cover the whole band: concrete, not an opening (real03's core)
    "closed_wall_faces": 0.80,     # both faces drawn on across the gap on a wall layer and no swing in it
    "open_wide": 0.90,             # a gap over GAP_MAX_M: two walls, topology decides
    "open_lined": 0.80,            # a thinner wall runs along one face: columns on that wall, not one wall with gaps
    "open_split": 0.70,            # a split run gap whose part holds no symbol: two walls on one line (real02)
    "open_box_fronts": 0.70,       # 24 Nov 2026: an empty gap between the fronts of two small boxes (ducts, shafts)
                                   # closed behind or ending with them: two walls on one line (openings.box_fronts_gap)
    "doorless": 0.50,              # nothing in the band and no door-like arc: a passage, or an undrawn door or window
    "unclassified": 0.20,          # strokes in the band that no rule reads: the weakest answer of the cascade
    "end_gap_open": 0.60,          # an end gap with no door or window drawn makes no element: the free end stays free
    # wall_or_notation: the face-pair wall reader of walls.face_pair_walls
    "notation_layer": 0.95,        # a text, dimension or axis layer never draws a wall (UL296)
    "axis_grid": 0.90,             # a layer whose pieces cross straight through each other is an axis grid (real10)
    "tread_run": 0.90,             # four or more parallel lines at an even tread pitch: a stair, slats or a hatch
    "wide_band": 0.80,             # three or more short strokes side by side wider than any wall: rails, a newel
    "flight": 0.80,                # a band crossed by three or more treads at an even pitch: a stair flight
    "hole": 0.85,                  # 24 Nov 2026: a band inside a hole of the layer's even-odd fill of its closed outlines
                                   # (a cavity, a duct, a shaft): no wall material (walls.drop_hole_pairs)
    "stair_edge": 0.75,            # 22 Nov 2026 (C0053): a thin band at whose one face a flight's treads end, as long
                                   # as the flight: its open side (stringer and balustrade)
    "stair_edge_part": 0.70,       # 22 Nov 2026 (S2): the part of a longer thin piece along a flight whose treads end at
                                   # its one face, parting nothing (its sides joined round it, no other room's label in
                                   # sight beyond it, walls.split_stair_edges): the piece is split
                                   # at the flight's ends, the parts beyond stay wall pieces
    "open_passage": 0.70,          # 22 Nov 2026 (UL363, C0053): a doorless gap with nothing drawn in it (no wall line,
                                   # leaf, swing, sill, jamb mark or lintel; ``openings.passage_marks``) in an inner
                                   # partition between two rooms, none wet: open up to the ceiling
                                   # (``twins.open_passages``)
    "wall_chosen_layer": 0.80,     # a primary pair on the layer the labels chose (walls.PAIR_CONFIDENCE)
    "wall_document_layer": 0.50,   # a primary pair on a layer taken from the document's other plans (too few labels)
    "secondary_pair": 0.40,        # a pair under PAIR_OVERLAP_M on a chosen layer that the network takes (as long as it
                                   # is thick and touching a wall piece, walls._network): a short wall piece
    "secondary_cap": 0.70,         # 6 Nov 2026 (review): a short pair on a chosen layer the network does not take
                                   # (shorter than it is thick, or touching no wall piece): a wall end's cap line
    "layer_not_chosen": 0.70,      # a pair on a layer that lost the label contest to the chosen one
    "layer_not_chosen_undecided": 0.50,   # ... when no layer closed in enough labels to decide
}
# a door or window size tag: ``wenart.ingest.tag_grammar.parse`` (27 Nov 2026, R09: one parser for the pipeline)
LABEL_RE = re.compile(r"[A-Za-zÇĞİÖŞÜçğıöşü]{3,}")
TAG_REACH_M = 2.0                  # a size tag counts up to this far from the gap (the nearest one is recorded)
OUTDOOR_REACH_M = 2.0              # a balcony / terrace label within this of the gap, outside the building
LABEL_REACH_M = 3.5                # a room label this far from the gap, on one side or the other
LABEL_HEIGHT_M = (0.08, 0.8)       # a text of this height (plan metres) can be a room label
TWIN_TOL_M = 0.30                  # the mirror twin of a gap: a gap whose centre lies this close to the mirrored centre
COVER_LATERAL_M = 0.15             # a built wall covers a place when the place lies this close to its centre line ...
COVER_END_M = 0.05                 # ... and inside its extent (grown by this)
ELEMENT_TOL_M = 0.50               # the built opening of a gap: centre within this of the gap's centre ...
ELEMENT_WIDTH_M = 0.30             # ... and width within this (the truth's own tolerances, ranker.label)
PAIR_OVERLAP_SHARE = 0.5           # a wall covers a pair when they overlap this share of the pair's length
ROUND = 4


def rule_confidence(rule: str) -> float:
    """The table's confidence of a rule (a rule missing from the table is a programming error, so KeyError)."""
    return RULE_CONFIDENCE[rule]


def ranker_enabled() -> bool:
    """The ranker decides unless ``WENART_RANKER=0`` (the rules alone; the regression comparison of step 1 and a
    reading the user wants without it). A missing model file means the rules alone too (``ranker.decide``)."""
    import os
    return os.environ.get("WENART_RANKER", "1") != "0"


def _num(v) -> float | int | bool:
    """A feature value as JSON-safe number: bool stays bool, floats are rounded, None is 0."""
    if v is None:
        return 0
    if isinstance(v, bool):
        return v
    if isinstance(v, int):
        return v
    return round(float(v), ROUND)


def _rot(p, deg: float) -> tuple[float, float]:
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


def _dist(a, b) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


# --- texts around a place (page metres) ---------------------------------------------------------------------------

@dataclass
class _Text:
    at: tuple[float, float]
    text: str
    height: float
    size_tag: Optional[tuple[float, float]] = None    # (width, height) metres
    tag_widths: tuple = ()                             # every width reading (a glued 'K290/210': 0.90 and 2.90; TAGS-1)
    outdoor: bool = False
    label: bool = False


def _classify_text(t) -> Optional[_Text]:
    text = (getattr(t, "text", None) or "").strip()
    if not text:
        return None
    box = t.box
    at = ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)
    out = _Text(at=at, text=text, height=float(getattr(t, "height", 0.0) or 0.0))
    from wenart.ingest import tag_grammar as TG
    tg = TG.parse(text)
    if tg is not None:
        out.size_tag, out.tag_widths = (tg.w, tg.h), tg.widths
        return out
    if LABEL_RE.search(text) and LABEL_HEIGHT_M[0] <= out.height <= LABEL_HEIGHT_M[1]:
        out.label = True
        try:
            from wenart.levels import outdoor as OD
            out.outdoor = OD.space_kind(text) is not None
        except Exception:  # noqa: BLE001 - the outdoor word list is a feature, never a reason to stop a reading
            out.outdoor = False
    return out


def text_features(texts: list[_Text], centre, normal, width: float) -> dict:
    """The size tag, outdoor label and room labels around a place (the gap's centre ``centre`` and the unit vector
    ``normal`` across its wall, both in the frame of ``texts``): the nearest tag's distance, its width over the gap's
    and whether it names a door-high piece; a balcony or terrace label within ``OUTDOOR_REACH_M``; room labels on one
    or both sides within ``LABEL_REACH_M`` (pure)."""
    tag_d, tag_w, tag_h = TAG_REACH_M, 0.0, 0.0
    outdoor = False
    sides = {1: False, -1: False}
    for t in texts:
        d = _dist(t.at, centre)
        if t.size_tag is not None:
            if d < tag_d:
                # TAGS-1: the reading of a glued tag nearest the gap's width
                tw = min(t.tag_widths or (t.size_tag[0],), key=lambda x: abs(x - width))
                tag_d, tag_w, tag_h = d, tw, t.size_tag[1]
            continue
        if t.outdoor and d <= OUTDOOR_REACH_M:
            outdoor = True
        if t.label and d <= LABEL_REACH_M:
            s = (t.at[0] - centre[0]) * normal[0] + (t.at[1] - centre[1]) * normal[1]
            if abs(s) > 0.05:
                sides[1 if s > 0 else -1] = True
    return {"tag_distance": round(tag_d, ROUND), "tag_width_ratio": round(tag_w / width, ROUND) if width > 0 else 0.0,
            "tag_height": round(tag_h, ROUND), "tag_door_like": bool(tag_h >= 2.0),
            "outdoor_within_2m": outdoor, "labels_both_sides": sides[1] and sides[-1],
            "labels_one_side": sides[1] != sides[-1]}


# --- the log -------------------------------------------------------------------------------------------------------

@dataclass
class DecisionLog:
    """The decision records of one level while it is read (``core.extract`` makes one and passes it down)."""
    level_id: str
    texts: list = field(default_factory=list)             # TextRun, page metres
    dimension_ids: frozenset = frozenset()
    units_to_m: Optional[float] = None
    ranker: bool = True                                   # step 4: the ranker may decide (False: the rules alone)
    raster: bool = False                                  # a scan's traced lines (``gaps_and_openings`` sets it)
    gap_records: list = field(default_factory=list)       # [(record, gap)]
    wall_records: list = field(default_factory=list)      # [record]
    wall_counts: list = field(default_factory=list)       # [{layer, rule, pairs, without_record}] (``count_wall``)
    _texts: list = field(default_factory=list)            # _Text, page metres
    _theta: float = 0.0
    _aligned: Optional[list] = None                       # the texts in the gaps' aligned frame (cached per theta)

    def __post_init__(self) -> None:
        self._texts = [x for x in (_classify_text(t) for t in self.texts or []) if x is not None]

    # -- gaps (the aligned frame of openings.gaps_and_openings) --
    def begin_gaps(self, theta: float) -> None:
        self._theta = theta
        self._aligned = None

    def texts_aligned(self) -> list[_Text]:
        """The texts in the aligned frame of the gaps (rotated by -theta), computed once per level."""
        if self._aligned is None:
            self._aligned = [_Text(at=_rot(t.at, -self._theta), text=t.text, height=t.height, size_tag=t.size_tag,
                                   tag_widths=t.tag_widths, outdoor=t.outdoor, label=t.label) for t in self._texts]
        return self._aligned

    def add_gap(self, g, record: dict) -> dict:
        record.setdefault("kind", KIND_GAP)
        record.setdefault("level_id", self.level_id)
        record.setdefault("decided_by", DECIDED_RULE)
        self.gap_records.append((record, g))
        g.decision = record
        return record

    def fill_gap_context(self, gaps: list, exterior, theta: float, mirror_axis) -> None:
        """Once every gap of the level is classified and the walls are merged (before the openings are built): the
        place in page metres, the exterior test and the mirror twin's cascade answer go into every record. The ranker
        decides after this (``openings._apply_ranker``), so it sees the same features the labels are made from."""
        kept = {id(g) for g in gaps}
        by_centre = []
        for rec, g in self.gap_records:
            mid = (g.a + g.b) / 2.0
            centre = _rot(g.point(mid), theta)
            rec["place_page"] = [round(centre[0], ROUND), round(centre[1], ROUND)]
            rec["axis"] = round(((0.0 if g.axis == "h" else 90.0) + theta) % 180.0, 2)
            corners = [_rot(p, theta) for p in (g.point(g.a, -g.t / 2), g.point(g.b, -g.t / 2),
                                                 g.point(g.b, g.t / 2), g.point(g.a, g.t / 2))]
            rec["features"]["exterior"] = bool(exterior(corners)) if exterior is not None else False
            if id(g) in kept:
                by_centre.append((centre, rec))
        for rec, g in self.gap_records:
            twin = None
            if mirror_axis is not None and id(g) in kept:
                axis, v = mirror_axis
                c = rec["place_page"]
                m = (2 * v - c[0], c[1]) if axis == "x" else (c[0], 2 * v - c[1])
                best = min(((_dist(m, c2), r2) for c2, r2 in by_centre if r2 is not rec), key=lambda x: x[0],
                           default=None)
                if best is not None and best[0] <= TWIN_TOL_M:
                    twin = best[1]["rule_answer"]
            f = rec["features"]
            f["twin_known"] = twin is not None
            for cls in ("door", "window", "opening"):
                f[f"twin_{cls}"] = twin == cls
            # (no "typical floor's answer" feature: a level that a typical floor plan stands for reads that plan's
            # extraction again (pipeline, ``typical_of``), so its answer for the same gap is this record's own answer,
            # a leak and no second opinion; it can come back when two storeys are read from independent drawings)

    def finish_gaps(self, gaps: list) -> None:
        """At the end of ``gaps_and_openings``: the gap-stage answer (``gaps_answer``: the class after the caller's own
        rules, lining, inside-wall, two-walls, and the ranker), the caller's rule where it decided, and a record whose
        gap the caller dropped is marked."""
        kept = {id(g) for g in gaps}
        for rec, g in self.gap_records:
            rec["gaps_answer"] = gap_answer(g) if id(g) in kept else DROPPED
            if id(g) not in kept:
                continue
            caller = caller_rule(g)
            if caller is not None and (rec["rule"] != caller or rec["rule_answer"] != rec["gaps_answer"]):
                # the caller's own rule decided after the cascade (wall material across the gap, a lining wall, two
                # walls on one line, a free end with nothing drawn): that is the reader's rule answer; the cascade's
                # stays on the record, and a ranker decision it overrode goes back to the rule
                rec["cascade_rule"], rec["cascade_answer"] = rec["rule"], rec["rule_answer"]
                rec["rule"], rec["rule_answer"] = caller, rec["gaps_answer"]
                rec["rule_confidence"] = rule_confidence(caller)
                if rec.get("decided_by") == DECIDED_RANKER:
                    rec["decided_by"] = DECIDED_RULE
                    rec["ranker_overridden_by"] = caller

    # -- walls (page metres) --
    def add_wall(self, record: dict) -> dict:
        record.setdefault("kind", KIND_WALL)
        record.setdefault("level_id", self.level_id)
        record.setdefault("decided_by", DECIDED_RULE)
        self.wall_records.append(record)
        return record

    def count_wall(self, layer: str, rule: str, n: int, left_out: int) -> None:
        """The pairs a layer's rule decided and how many of them have no record (``walls.PAIR_RECORD_CAP``)."""
        self.wall_counts.append({"layer": layer, "rule": rule, "pairs": n, "without_record": left_out})

    def summary(self) -> dict:
        """What the level's records hold (the per-level file's ``summary``): counts per kind, rule and answer, the
        pairs left without a record, the ranker's decisions and the low-confidence places."""
        out = summary([r for r, _g in self.gap_records] + self.wall_records)
        out["wall_pairs_per_layer_rule"] = list(self.wall_counts)
        out["pairs_without_record"] = sum(c["without_record"] for c in self.wall_counts)
        return out

    # -- the end of the level --
    def finalize(self, origin: tuple[float, float], walls: list, openings: list) -> list[dict]:
        """The records in building metres with their ``final_answer`` read off the built level: for a gap the type of
        the opening at its place (``ELEMENT_TOL_M``, ``ELEMENT_WIDTH_M``), else ``closed`` when a built wall covers the
        place, else ``open``; for a pair ``wall`` when a built wall covers its centre line, else ``notation``.
        ``walls`` and ``openings`` are the level's final items in building metres (``WallItem``, ``OpeningItem``)."""
        ox, oy = float(origin[0]), float(origin[1])
        segs = [((float(w.start[0]), float(w.start[1])), (float(w.end[0]), float(w.end[1])), float(w.thickness))
                for w in walls]
        ops = [(tuple(o.center), float(o.width), o.kind) for o in openings if getattr(o, "virtual", False) is False]
        out = []
        for rec, _g in self.gap_records:
            pp = rec.pop("place_page", None)
            place = [round(pp[0] - ox, ROUND), round(pp[1] - oy, ROUND)] if pp else None
            rec["place"] = place
            if rec.get("gaps_answer") == DROPPED or place is None:
                rec["final_answer"] = DROPPED
            else:
                rec["final_answer"] = _final_gap_answer(place, rec["features"].get("width", 0.0), ops, segs)
            out.append(rec)
        wall_model = None
        if self.ranker and self.wall_records:
            from wenart.reading_check import ranker as RK
            wall_model = RK.load_model(KIND_WALL)
        for rec in self.wall_records:
            pp = rec.pop("place_page", None)
            line = rec.pop("line_page", None)
            rec["place"] = [round(pp[0] - ox, ROUND), round(pp[1] - oy, ROUND)] if pp else None
            if line:
                a, b = ((line[0][0] - ox, line[0][1] - oy), (line[1][0] - ox, line[1][1] - oy))
                rec["line"] = [[round(a[0], ROUND), round(a[1], ROUND)], [round(b[0], ROUND), round(b[1], ROUND)]]
                rec["final_answer"] = "wall" if any(covers_segment(a, b, s) for s in segs) else "notation"
            else:
                rec["final_answer"] = "notation"
            if wall_model is not None:
                # 5 Nov 2026 (R3 step 4): the wall ranker advises only. Moving a pair into or out of the wall network
                # is geometry the network rules build (joins, columns, the mask), so its answer is recorded and
                # counted (``ranker_advice``), never applied; decided_by stays rule.
                answer, by, margin, scores = RK.decide(KIND_WALL, rec["features"], rec["rule_answer"],
                                                       rec["rule_confidence"], allowed=RK.allowed_answers(rec),
                                                       model=wall_model, rule=rec.get("rule"))
                rec["scores"], rec["margin"] = scores, margin
                if by == RK.DECIDED_RANKER and answer != rec["rule_answer"]:
                    rec["ranker_advice"] = answer
            out.append(rec)
        return out



# --- the end of the pipeline (6 Nov 2026, review): the answers and the places from the built level --------------------

def final_answers_from_building(records: list[dict], walls: list[dict], openings: list[dict]) -> int:
    """Every record's ``final_answer`` read again from the FINAL building (pure apart from the records it updates):
    ``walls`` and ``openings`` are the level's building dicts after every pipeline pass (underground closing, twin
    walls, facade gaps, lift doors, gaps behind furniture ...). The core's provisional answer is kept as
    ``core_final_answer`` where it differs; a dropped candidate stays dropped. Returns how many answers changed."""
    segs = [((float(w["start"][0]), float(w["start"][1])), (float(w["end"][0]), float(w["end"][1])),
             float(w.get("thickness") or 0.0)) for w in walls if w.get("start") and w.get("end")]
    ops = [(tuple(o["center"]), float(o["width"]), o.get("type")) for o in openings
           if not o.get("virtual") and o.get("center") and o.get("width") is not None]
    changed = 0
    for rec in records:
        if rec.get("final_answer") == DROPPED or not rec.get("place"):
            continue
        if rec.get("kind") == KIND_GAP:
            new = _final_gap_answer(rec["place"], float(rec["features"].get("width") or 0.0), ops, segs)
        elif rec.get("line"):
            a, b = rec["line"]
            new = "wall" if any(covers_segment(a, b, s) for s in segs) else "notation"
        else:
            continue
        if new != rec.get("final_answer"):
            rec["core_final_answer"] = rec.get("final_answer")
            rec["final_answer"] = new
            changed += 1
    return changed


def places_from_records(records: list[dict]) -> list[dict]:
    """The undecided gaps of a level as ``reading_places`` (pure; 6 Nov 2026, review): a gap whose rule is weak while
    the ranker is weak or untrusted there, and only while the built level still holds that weak decision's own outcome
    (``final_answer`` equal to the rule's answer). A gap a later pass resolved (a facade gap's window, an opening to the
    soil removed, a recess opened, a tagged window, a mirrored door) is no place. The text is what the level holds."""
    out = []
    for rec in records:
        if rec.get("kind") != KIND_GAP or not rec.get("low_confidence") or not rec.get("place"):
            continue
        if rec.get("final_answer") != rec.get("rule_answer"):
            continue
        out.append({"kind": "undecided_gap", "text": rec["final_answer"], "at": list(rec["place"]),
                    "note": rec["low_confidence"]})
    return out


def _answer_of_class(cls: str) -> str:
    """The decision answer of a gap class (``empty`` and ``unclassified`` both become an opening element)."""
    return {"empty": "opening", "unclassified": "opening"}.get(cls, cls)


def gap_answer(g) -> str:
    """The reader's answer for a gap at the end of ``gaps_and_openings``: an end gap left empty or unclassified makes
    no element (``open``: the free end stays free); every other class as ``_answer_of_class``."""
    if g.kind == "end" and g.cls in ("empty", "unclassified"):
        return "open"
    return _answer_of_class(g.cls)


def caller_rule(g) -> Optional[str]:
    """The rule of ``gaps_and_openings`` itself that decided a gap after the cascade (pure): wall material of other
    pieces across it (``closed_inside_wall``), a thinner wall along its face (``open_lined``), a split run whose part
    holds no symbol (``open_split``), or an end gap with no door or window drawn (``end_gap_open``: the free end stays
    free, no element). None when the cascade's answer stood."""
    found = g.found or {}
    if found.get("inside"):
        return "closed_inside_wall"
    if found.get("lining"):
        return "open_lined"
    if found.get("box_fronts"):
        return "open_box_fronts"
    if found.get("split_reason"):
        return "open_split"
    if g.kind == "end" and g.cls in ("empty", "unclassified"):
        return "end_gap_open"
    return None


def covers_point(p, seg) -> bool:
    """A wall segment ``((x0, y0), (x1, y1), thickness)`` covers a point: within ``COVER_LATERAL_M`` of its centre
    line (or inside its band) and inside its extent grown by ``COVER_END_M``."""
    (x0, y0), (x1, y1), t = seg
    dx, dy = x1 - x0, y1 - y0
    n = math.hypot(dx, dy)
    if n < 1e-9:
        return False
    ux, uy = dx / n, dy / n
    px, py = p[0] - x0, p[1] - y0
    along = px * ux + py * uy
    lateral = abs(px * uy - py * ux)
    return -COVER_END_M <= along <= n + COVER_END_M and lateral <= max(COVER_LATERAL_M, t / 2.0)


def covers_segment(a, b, seg) -> bool:
    """A wall segment covers a candidate segment ``a``-``b``: both ends within ``COVER_LATERAL_M`` of its line (or in
    its band) and the overlap along it at least ``PAIR_OVERLAP_SHARE`` of the candidate's length."""
    (x0, y0), (x1, y1), t = seg
    dx, dy = x1 - x0, y1 - y0
    n = math.hypot(dx, dy)
    la = _dist(a, b)
    if n < 1e-9 or la < 1e-9:
        return False
    ux, uy = dx / n, dy / n
    alongs = []
    for p in (a, b):
        px, py = p[0] - x0, p[1] - y0
        if abs(px * uy - py * ux) > max(COVER_LATERAL_M, t / 2.0):
            return False
        alongs.append(px * ux + py * uy)
    overlap = min(n, max(alongs)) - max(0.0, min(alongs))
    return overlap >= PAIR_OVERLAP_SHARE * la


def _final_gap_answer(place, width: float, openings: list, segs: list) -> str:
    best = None
    for centre, w, kind in openings:
        d = _dist(centre, place)
        if d <= ELEMENT_TOL_M and abs(w - width) <= ELEMENT_WIDTH_M and (best is None or d < best[0]):
            best = (d, kind)
    if best is not None:
        return _answer_of_class(best[1])
    return "closed" if any(covers_point(place, s) for s in segs) else "open"


def summary(records: list[dict]) -> dict:
    """Counts per kind, rule answer, final answer and decider (the report's table; pure)."""
    out: dict = {}
    for r in records:
        k = out.setdefault(r["kind"], {"n": 0, "rule_answer": {}, "final_answer": {}, "decided_by": {},
                                       "changed_after_rule": 0, "ranker_advice": 0, "low_confidence": 0})
        k["n"] += 1
        for key in ("rule_answer", "final_answer", "decided_by"):
            v = str(r.get(key))
            k[key][v] = k[key].get(v, 0) + 1
        if r.get("final_answer") not in (r.get("rule_answer"), DROPPED):
            k["changed_after_rule"] += 1
        k["ranker_advice"] += 1 if r.get("ranker_advice") else 0
        k["low_confidence"] += 1 if r.get("low_confidence") else 0
    return out
