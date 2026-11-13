"""The common core of a building, completed (12 Nov 2026; the architect's audit of 8 buildings, user: "Make sense of
the building", "This is for all the projects").

What: ``apply(build, texts_by_level, party_by_level)`` runs in ``completion.complete`` after the storeys and the light
wells and before the windows; it changes the building in place and returns the record written to
``level_inference.core_rules``. Every change carries ``inferred`` or ``adjusted_by_ai`` (by code) with its reason.

1. **A stair the reading missed** (``stairs``, R08 with the misfire hunters' guards): a building of several storeys
   (levels read or inferred from the storey evidence) has a stair rising from every storey with a storey above. When a
   storey has none: a copy of a typical floor takes its floor's stair; else a stroke box the reading set aside as
   notation (``symbols`` of kind ``dimension_outline`` or ``unknown``, at least ``STAIR_BOX_M`` and
   ``STAIR_BOX_MIN_M2``) standing in a hall or a stair room, or touching a lift, is that stair only with stair strokes
   inside it (``stair_evidence``: a run of tread lines from the sheets stage, a tread-number run 1..N with N at least
   ``NUMBER_RUN_MIN``, or a riser tag; G3), never a box over a lift or holding a lift, shaft, void or light-well word
   (``from_documents``, typed by this rule, inferred and needs review). Else (the coordinator's decision of 12 Nov
   2026: a building of two or more storeys has a stair) a box the reader set aside, of stair size (``STAIR_SIZE_M``,
   about 2.0-3.2 by 3.5-6.5 m) beside the lift, the core or a hall, with a stair sign drawn in it (``stair_signs``: a
   well line along its long axis makes a U stair, a break diagonal a straight flight) is an inferred stair whose
   risers follow the storey height; it is listed in ``needs_review`` with the evidence strokes. With no such box no
   geometry is made: the storey is listed (``stairs_open``) with the box found without strokes, and the building gets a
   ``needs_review`` item (G2). Each stair gets its void in the slab above.
2. **Lift landing doors** (``lift_doors``, R19 with its guards; a lift is ``completion.is_lift``: a lift word, no
   machine-room, lobby or car-lift word, at most 8 m2 a car): the pieces of one landing door read in stacked parallel
   walls (``STACK_M`` apart, spans overlapping by half) are merged first, the widest (or the drawn one) kept; then a
   lift's openings onto a flat's room, onto a stair flight (its ``FRONT_ZONE_M`` front zone covering
   ``FRONT_FLIGHT_M2`` of a flight), windows in the shaft and pieces under ``PIECE_MIN_M`` are rejected when the reader
   derived or a rule inferred them (``derived``), and raise a review record when they are drawn symbols (R16 G6, a
   drawn door is never removed); a doorless opening between a lift and the common hall is the lift's landing door: a
   sliding door (the user on real10, C0034: "there should be a door for the elevator like sliding door ... a general
   rule"; ``adjusted_by_ai``, ``drawn_type`` kept); a lift left without an opening onto the common hall gets one
   inferred landing door on a face onto a hall, stair or common room of the core (never a shop's or a flat's room):
   where the storey above or below has its lift door, else away from a drawn counterweight; with no such face a review
   record and no geometry. Once a lift opens onto the core, its other derived openings into a room that is not the
   core go (drawn ones are review records: a through-car). Stacked landing pieces take the drawn jambs. A pit level
   (KUYU, BOŞLUK) gets no landing door. Only in a building of several flats (a house's own lift opens where its plan
   says), but a lift-door mark in no passenger lift's shaft wall is undone in every building (a flat's hinged door gets
   its drawn operation back; review MF6, S1-20a).
3. **Between a flat and the core** (``core_gaps``, R16 with its guards): the core is the lifts, the stair rooms, the
   lift's lobby, the rooms holding a core stair (never a shop's or a flat's room: their stair is their own) and the
   halls joined to them by virtual separators or, with common evidence, by doorless openings (never a flat's antre).
   An unclassified gap (type ``opening``, a derived opening) between the core and a flat's bathroom, WC, shower or
   bedroom is closed, unless it is the room's only link (a review record); one to a kitchen, living or dining room is
   closed only when that room still reaches the core without it and the gaps already closed (G4). A window drawn in a
   gap stays as that window; a closing that would cut a flat off the core is undone (review). Drawn doors are never
   removed (the RC14 check ``core_door`` asks about them). Only in a building of several flats.
4. **Entrances** (``entrances``, R09 brought forward on 13 Nov 2026): an entrance (``site.entrances``) whose far side
   holds a room label the reading lost is no entrance; in a building of several flats or with a common core an entrance
   from a wet room is refused; an outer door whose nearest size tag is a window's (P:120/150) is that window (R37) and
   a doorless outer gap into a hall or stair room (never a flat's antre) whose tags are doors' (K:100/210 and K:50/210:
   a double door) is the drawn building entrance with its record (``size_tags``, review S1-09b); the main entrance
   never opens into a bedroom, a wet room or a kitchen (nor a flat's room with a common core), and the best way in is
   the main one when the old main was a window. A building with a common core whose entrances reach no core room on any storey gets an
   inferred one on an entrance storey (an entrance word in its core, else a floor within ``ENTRANCE_LEVEL_M`` of the
   ground the reading knows, else the ground floor), where the core hall reaches a facade that is no party wall, with
   its ``site.entrances`` record (threshold, rise, steps); else an open point and a ``needs_review`` item. No core read:
   no question.

Why: real21's core held two lifts and a stair box the reader set aside as a dimension outline; its lifts opened into
bedrooms, a bedroom opened onto the stair hall, and no door led in from the street. real20's six "entrances" were inner
doors of rooms the reading lost; real10's lift opened into a WC and onto its stair. Every one is a general rule.

How: pure geometry on the building dict (``completion.Level`` probes, shapely); no AI. Every change passes
``rule_guards.blocked`` first (rule keys ``stair_*``, ``lift_door_*``, ``core_gap``, ``entrance_*``): a guard or a rule
switched off stops it, logged in ``level_inference.guarded``.
"""
from __future__ import annotations

import math
import re
from typing import Optional

from shapely.geometry import Point, Polygon

from wenart import building as B
from wenart import geometry as G
from wenart.ingest import completion as CP
from wenart.ingest import rule_guards as RG

# a flat's rooms (a storage room, a shelter or a laundry may be the building's own, reached from the core)
PRIVATE = ("bedroom", "living", "kitchen", "bathroom", "wc", "shower", "toilet", "dining", "office", "study")
# 13 Nov 2026 (FC-01): rooms that are never the common core whatever stands in them
NOT_CORE_TYPES = ("balcony", "terrace", "loggia", "garage", "dressing", "laundry", "storage", "utility")
WET = ("bathroom", "wc", "shower", "toilet")
STAIR_BOX_M = (0.8, 2.0)        # a stroke box at least this small side by this long side ... (R08 G10)
STAIR_BOX_MIN_M2 = 1.8          # ... and this large can hold a stair
STAIR_SYMBOL_KINDS = ("dimension_outline", "unknown", "untyped", "outline")
NUMBER_RUN_MIN = 8              # a tread-number run 1..N with N at least this says stair (R08 G3)
RISER_TAG_RE = re.compile(r"\b\d{1,2}\s*[x×*]\s*\d{1,2}(?:[.,]\d+)?\s*/\s*\d{2}\b|\bmer\s*[:.]\s*\d{1,2}\b"
                          r"|\bb\s*:\s*\d{2}\b.*\br\s*:\s*\d{2}\b")
NOT_STAIR_RE = re.compile(r"(?<![a-z])(?:asansor|lift|elevator|saft|shaft|bosluk|boslugu|isiklik|aydinlik|void)(?![a-z])")
LIFT_DOOR_MIN_M = 0.60          # an inferred lift landing door is at least this wide
LIFT_DOOR_M = (0.90, 2.10)      # an inferred lift landing door
PIECE_MIN_M = 0.50              # a lift opening narrower than this after the merge is a sliver (R19)
LIFT_DOOR_WIDE_M = 1.40         # a lift's opening onto the hall wider than this is narrowed to a lift door when retyped
STACK_M = 0.50                  # openings in stacked parallel walls this close across are one door read in pieces
FRONT_ZONE_M = 1.20             # the zone in front of a lift door ...
FRONT_FLIGHT_M2 = 0.50          # ... a stair flight covering this much of it: the opening is onto the flight
ENTRANCE_DOOR_M = (1.20, 2.20)
TREAD_M = 0.27
TREAD_RANGE_M = (0.26, 0.30)    # an inferred stair's tread ...
RISER_RANGE_M = (0.15, 0.19)    # ... and riser, the risers from the storey height
STOREY_H_M = 3.0                # the storey height when the levels give none
# a box of stair size: about 2.0-3.2 m by 3.5-6.5 m (the coordinator), 10 % either way
STAIR_SIZE_M = ((1.8, 3.15), (3.5, 7.15))
WELL_ANGLE_DEG = 5.0            # a well line runs along the box's long axis within this angle ...
WELL_SHARE = 0.5                # ... over at least this share of its length, near its middle
DIAG_DEG = (25.0, 65.0)         # a break diagonal: this angle to the long axis ...
DIAG_SHARE = 0.4                # ... at least this share of the box's width long
U_FLIGHT_M = 0.9                # a U stair needs two flights this wide side by side (the verified R08 tier b)
CAR_M = ((0.9, 2.2), (1.1, 2.8))  # a lift car: a closed rectangle this size (R19 b); it makes a box a lift, never a stair
# an opening a rule made: a reader-derived gap, or one inferred by a rule (R16 G6)
DERIVED_RULES = ("lift_door", "mirror_twin", "gap_behind_furniture", "inferred_door", "inferred_window",
                 "inferred_entrance", "balcony_door")
LABEL_REACH_M = 1.5             # a lost room label this close beyond an entrance is the room behind it
# 13 Nov 2026 (the stage-1 review): a unit's own use (its stair is the unit's: a shop's stair down to its store) ...
UNIT_USE_RE = re.compile(r"(?<![a-z])(?:dukkan|dukkani|magaza|magazasi|depo|deposu|ofis|buro|isyeri|atolye|shop|store|"
                         r"storage|office|boutique|laden|lager)(?![a-z])")
# ... and a flat's own hall (an antre): never the common core
FLAT_HALL_RE = re.compile(r"(?<![a-z])(?:antre|antresi|vestiyer|vestibule|diele|daire\s+girisi)(?![a-z])")
WINDOW_LAYER_RE = re.compile(r"pencere|penc|window|glass|glazing|(?<![a-z])cam(?![a-z])|fenster|fenetre|ventana")
WINDOW_TAG_RE = re.compile(r"^\s*p?\s*(\d{2,3})\s*/\s*(\d{2,3})\s*$")
GAP_WINDOW_MIN_M = 0.30         # a window drawn in a gap at least this wide is kept as a window when the gap closes
GAP_WINDOW_HEAD_M = 2.10        # ... its head, and its height without a tag (a high window between a wet room and the core)
GAP_WINDOW_H_M = 0.60
DOOR_TAG_H_M = 1.80             # a W/H tag this high or higher is a door's (100/210), lower a window's (150/50)
STACK_MATCH_M = 0.05            # a lift door on the storey above or below this close to a face is at the same place
JAMB_REACH_M = 0.80             # a lift door's drawn jambs: wall ends this far from its centre, on its wall line ...
JAMB_MIN_M = 0.10               # ... of a wall at least this long (a shorter stub is a panel or plaster stroke: FC-03)
ENTRANCE_LEVEL_M = 0.60         # an entrance storey's floor lies this close to the ground (R24: about one entrance flight)
ENTRANCE_WORD_RE = re.compile(r"(?<![a-z])(?:bina\s+girisi|bina\s+giris|giris\s+holu|apartman\s+girisi|main\s+entrance|"
                              r"entrance\s+hall|entrance\s+lobby|hauseingang|entree)(?![a-z])")
NOT_MAIN_TYPES = ("bedroom", "kitchen") + WET   # a main entrance never opens into one of these (R09)
ENTRANCE_ROOM_RE = re.compile(r"(?<![a-z])(?:ruzgarlik|ruzgarligi|bina\s+girisi|giris\s+holu|apartman\s+girisi|"
                              r"windfang|entrance\s+(?:hall|lobby)|lobby|lobi|sas\s+d.entree)(?![a-z])")


def _storey_below(b: dict, lid: str) -> Optional[str]:
    st = _storeys(b)
    ids = [lv["id"] for lv in st]
    return ids[ids.index(lid) - 1] if lid in ids and ids.index(lid) > 0 else None


def _rect(fp: dict) -> Polygon:
    return Polygon(G.rotated_rectangle(fp["center"], fp["size"], fp["rotation_deg"]))


def _storeys(b: dict) -> list:
    return sorted((lv for lv in b.get("levels") or [] if not lv.get("base_level_id")),
                  key=lambda lv: (lv.get("order") or 0, lv["id"]))


def several_flats(b: dict) -> bool:
    """A building of several flats (pure): two kitchens on one storey (a lift alone may be a house's own lift)."""
    for lv in _storeys(b):
        if sum(1 for r in b.get("rooms") or [] if r.get("level_id") == lv["id"] and r.get("room_type") == "kitchen") >= 2:
            return True
    return False


def common_core(b: dict) -> Optional[str]:
    """The evidence that the building has a common core (pure; R16 guard G2), or None: a passenger lift
    (``completion.is_lift``), a lift-named face larger than a car (the whole core), or a room whose drawn label (not an
    inferred one) holds a common-hall word (``common_areas.COMMON_ROOM_WORDS``: KAT HOLÜ, BİNA GİRİŞİ, MERDİVEN HOLÜ
    ...). A house pair with a stair each has none: its stair halls are the houses' own."""
    from wenart import common_areas as CA

    for r in b.get("rooms") or []:
        if CP.is_lift(r):
            return f"the lift {r['id']}"
        label = CP._fold(r.get("label_raw") or ("" if r.get("label_inferred") else r.get("label")))
        p = CP._poly(r.get("polygon"))
        if CP.LIFT_RE.search(label) and p is not None and p.area > CP.LIFT_MAX_M2:
            return f"the core {r['id']} (a lift-named face of {p.area:.1f} m2)"
        words = " " + " ".join(B.fold_ascii(label).upper().split()) + " "
        if any(f" {w} " in words for w in CA.COMMON_ROOM_WORDS):
            return f"the common hall {r['id']} '{r.get('label_raw') or r.get('label')}'"
    return None


def flat_core(b: dict) -> bool:
    """A building of several flats with a common core (``several_flats`` and ``common_core``): where a flat meets the
    core only through its entrance door (R16 G1, G2)."""
    return several_flats(b) and common_core(b) is not None


def needs_stair(b: dict) -> bool:
    """A building that needs a stair (pure): a lift, several flats (``several_flats``) or several storeys."""
    return any(CP.is_lift(r) for r in b.get("rooms") or []) or several_flats(b) or len(_storeys(b)) >= 2


def stairs_on(b: dict, lid: str) -> list:
    return ([f for f in b.get("furniture") or [] if f.get("level_id") == lid and f.get("type") == "stair"]
            + [r for r in b.get("rooms") or [] if r.get("level_id") == lid and r.get("room_type") == "stair"])


# ------------------------------------------------------------------------------------------------------- 1. stairs
def risers_for(rise: float) -> int:
    """The riser count of a stair climbing ``rise`` metres: risers in ``RISER_RANGE_M`` (pure)."""
    n = max(2, math.ceil(rise / RISER_RANGE_M[1] - 1e-9))
    return n - 1 if n > 2 and rise / n < RISER_RANGE_M[0] else n


def stair_dict(fp: dict, reason: str, turn: str = "U", rise: Optional[float] = None) -> dict:
    """A stair in the footprint ``fp`` (pure): a dog-leg (U) with two flights side by side along its long side and a
    half landing at the far end, or (``turn`` straight) one flight along the long side. With ``rise`` (the storey
    height) the flights carry the riser count of ``risers_for`` (one riser a tread line) at a tread in
    ``TREAD_RANGE_M`` where the footprint allows; else the lines fill the footprint at ``TREAD_M``.

    13 Nov 2026 (review S1F-POD-P01: real21's inferred U stair left 1.05 m open between its first flight and its half
    landing): a flight runs from riser line to riser line (the convention of the numbered stairs,
    ``wenart.ingest.generic.stair_numbers``, and of ``parametric.stair_plan``: ``lines`` riser lines, the first at
    ``start``, the last at ``end``, ``spacing`` apart). Both flights of a U stand on the landing's near edge (flight 1's
    last riser line and flight 2's first); what the footprint has left over is floor at the stair's foot."""
    if turn == "straight":
        return _straight_stair(fp, reason, rise)
    (cx, cy), (w, d), rot = fp["center"], fp["size"], math.radians(fp["rotation_deg"])
    # the long side along the footprint's own axis
    if d >= w:
        u, n, length, width = (-math.sin(rot), math.cos(rot)), (math.cos(rot), math.sin(rot)), d, w
    else:
        u, n, length, width = (math.cos(rot), math.sin(rot)), (-math.sin(rot), math.cos(rot)), w, d
    fw = width / 2.0
    ld = max(min(fw, 1.4), 1.0)
    lines = max(3, min(10, int((length - ld - 0.3) / TREAD_M)))
    per, spacing = [lines, lines], TREAD_M
    if rise:
        nr = risers_for(rise)
        per = [math.ceil(nr / 2), nr - math.ceil(nr / 2)]
        spacing = max(TREAD_RANGE_M[0], min(TREAD_RANGE_M[1], (length - ld) / max(per[0] - 1, 1)))
    edge = length / 2.0 - ld                      # the landing's near edge

    def at(s, t):
        return [round(cx + u[0] * s + n[0] * t, 4), round(cy + u[1] * s + n[1] * t, 4)]

    flights = [{"start": at(edge - (per[0] - 1) * spacing, -fw / 2.0), "end": at(edge, -fw / 2.0),
                "width": round(fw, 3), "lines": per[0], "spacing": round(spacing, 3)},
               {"start": at(edge, fw / 2.0), "end": at(edge - (per[1] - 1) * spacing, fw / 2.0),
                "width": round(fw, 3), "lines": per[1], "spacing": round(spacing, 3)}]
    landing = [at(length / 2.0 - ld, -width / 2.0), at(length / 2.0, -width / 2.0), at(length / 2.0, width / 2.0),
               at(length / 2.0 - ld, width / 2.0)]
    return {"flights": flights, "landing": {"polygon": landing, "depth": round(ld, 3)},
            "direction": [round(u[0], 4), round(u[1], 4)], "direction_assumed": True, "turn": "U",
            "turn_assumed": True, "void_assumed": True, "riser_m": None, "riser_source": None,
            "risers": sum(per) if rise else None, "reason": reason}


def _long_axis(fp: dict) -> tuple:
    """``(u, n, length, width)`` of a footprint: its long axis, the normal, the long and the short side (pure)."""
    (w, d), rot = fp["size"], math.radians(fp["rotation_deg"])
    if d >= w:
        return (-math.sin(rot), math.cos(rot)), (math.cos(rot), math.sin(rot)), d, w
    return (math.cos(rot), math.sin(rot)), (-math.sin(rot), math.cos(rot)), w, d


def _straight_stair(fp: dict, reason: str, rise: Optional[float]) -> dict:
    """One straight flight along the footprint's long side (pure; ``stair_dict``), from riser line to riser line."""
    (cx, cy) = fp["center"]
    u, n, length, width = _long_axis(fp)
    lines = risers_for(rise) if rise else max(3, int((length - 0.6) / TREAD_M) + 1)
    spacing = max(TREAD_RANGE_M[0], min(TREAD_RANGE_M[1], (length - 0.6) / max(lines - 1, 1))) if rise else TREAD_M
    s0 = -length / 2.0 + 0.3

    def at(s, t):
        return [round(cx + u[0] * s + n[0] * t, 4), round(cy + u[1] * s + n[1] * t, 4)]

    return {"flights": [{"start": at(s0, 0.0), "end": at(s0 + (lines - 1) * spacing, 0.0), "width": round(width, 3),
                         "lines": lines, "spacing": round(spacing, 3)}],
            "landing": None, "direction": [round(u[0], 4), round(u[1], 4)], "direction_assumed": True,
            "turn": "straight", "turn_assumed": True, "void_assumed": True, "riser_m": None, "riser_source": None,
            "risers": lines if rise else None, "reason": reason}


def derived(o: dict) -> bool:
    """An opening the reader derived (an unclassified gap, a gap read from breaks in the walls) or a rule inferred: one a
    rule may reject. A drawn door or window symbol (an arc with its leaf, a door block, a size tag) never is: a rule
    raises a review record on it instead (R16 G6)."""
    if o.get("type") == "opening" or o.get("inferred"):
        return True
    ev = (o.get("evidence") or [{}])[0] or {}
    rule = str(ev.get("rule") or "")
    return ev.get("method") in ("derived", "inferred") or rule in DERIVED_RULES or "mirror_twin" in rule


def stair_evidence(p: Polygon, strokes: list, texts: list) -> Optional[str]:
    """What in a box says stair (R08 G3; pure), or None: a run of tread lines of the sheets stage (``strokes``: dicts
    with a ``polygon`` in building metres, at least half of it inside the box), a tread-number run 1..N with N at least
    ``NUMBER_RUN_MIN``, or a riser tag ('16x18/28', 'MER: 16', 'B:25 R:18'). Diagonals, an X or an outline never do."""
    box = p.buffer(0.1)
    for run in strokes or []:
        q = run.get("polygon")
        if q is not None and q.area > 0 and box.intersection(q).area >= 0.5 * q.area:
            return f"{run['lines']} tread lines {run['pitch_m']:.2f} m apart"
    nums = set()
    for t in texts or []:
        if not box.contains(Point(t["x"], t["y"])):
            continue
        txt = str(t["text"]).strip()
        if re.fullmatch(r"[0-9]{1,2}", txt) and 1 <= int(txt) <= 40:      # never a superscript or circled digit
            nums.add(int(txt))
        elif RISER_TAG_RE.search(CP._fold(txt)):
            return f"the riser tag '{txt}'"
    run = 0
    while run + 1 in nums:
        run += 1
    return f"the tread numbers 1-{run}" if run >= NUMBER_RUN_MIN else None


def stair_signs(fp: dict, segments: list) -> tuple:
    """``(turn, signs)`` (pure; the coordinator's decision of 12 Nov 2026): a well line (a segment along the box's long
    axis, at least ``WELL_SHARE`` of its length, within a third of its width of the middle and clear of its sides)
    makes a U stair; else a break diagonal (``DIAG_DEG`` to the long axis, at least ``DIAG_SHARE`` of the width) makes a
    straight flight; two diagonals crossing each other (an X: a lift or a void) are no sign. ``(None, [])`` without a
    sign."""
    u, n, length, width = _long_axis(fp)
    c = fp["center"]
    well, diag = [], []
    for sg in segments:
        a, b2 = sg["a"], sg["b"]
        v = (b2[0] - a[0], b2[1] - a[1])
        ln = math.hypot(*v)
        if ln < 0.3:
            continue
        cos = abs(v[0] * u[0] + v[1] * u[1]) / ln
        mid = ((a[0] + b2[0]) / 2.0, (a[1] + b2[1]) / 2.0)
        off = abs((mid[0] - c[0]) * n[0] + (mid[1] - c[1]) * n[1])
        if cos >= math.cos(math.radians(WELL_ANGLE_DEG)):
            if ln >= WELL_SHARE * length and off <= width / 3.0 and width / 2.0 - off >= 0.15:
                well.append(sg)
        elif math.cos(math.radians(DIAG_DEG[1])) <= cos <= math.cos(math.radians(DIAG_DEG[0])) and \
                ln >= DIAG_SHARE * width:
            diag.append(sg)
    from shapely.geometry import LineString
    crossing = {i for i, x in enumerate(diag) for j, y in enumerate(diag) if i < j
                and LineString([x["a"], x["b"]]).intersects(LineString([y["a"], y["b"]]))
                and LineString([x["a"], x["b"]]).intersection(LineString([y["a"], y["b"]])).distance(
                    Point((x["a"][0] + x["b"][0]) / 2.0, (x["a"][1] + x["b"][1]) / 2.0)) <= 0.25 * x["length"]}
    crossing |= {j for i, x in enumerate(diag) for j, y in enumerate(diag) if i in crossing and i != j
                 and LineString([x["a"], x["b"]]).intersects(LineString([y["a"], y["b"]]))}
    diag = [d for k, d in enumerate(diag) if k not in crossing]
    if well:
        return "U", well[:1] + diag[:2]
    if diag:
        return "straight", diag[:2]
    return None, []


def strong_storeys(b: dict) -> Optional[str]:
    """The strong storey evidence tier b needs (the verified R08; pure): a passenger lift and a typical floor (a copy of
    a typical floor, or the area table's typical floor); else None."""
    lift = next((r for r in b.get("rooms") or [] if CP.is_lift(r)), None)
    if lift is None:
        return None
    st = (b.get("level_inference") or {}).get("storeys") or {}
    typical = any(lv.get("typical_of") for lv in b.get("levels") or []) or \
        bool(((st.get("areas") or {}).get("typical") or {}).get("value"))
    return f"the lift {lift['id']} and a typical floor" if typical else None


def _sign_box(b: dict, level: "CP.Level", drawn, texts: list) -> Optional[dict]:
    """The one box the reader set aside, of stair size (``STAIR_SIZE_M``) beside the lift, the core or a hall, with a
    stair sign drawn in it (``stair_signs``) and no lift car in it (``CAR_M``), in a building with strong storey
    evidence (``strong_storeys``); None without one, and ``{"several": [...]}`` when more than one box qualifies (the
    verified R08 tier b: exactly one walled core box)."""
    if drawn is None or strong_storeys(b) is None:
        return None
    lifts = [level.polys[r["id"]] for r in level.rooms if CP.is_lift(r)]
    core = core_rooms(b, level)
    found, seen = [], set()
    for s in b.get("symbols") or []:
        fp = s.get("footprint") or {}
        kind = str(s.get("kind"))
        if s.get("level_id") != level.lid or not fp.get("size") or \
                (kind not in STAIR_SYMBOL_KINDS and "stair" not in kind):
            continue
        key = (round(fp["center"][0], 2), round(fp["center"][1], 2))
        if key in seen:
            continue                                   # the same box read more than once is one box
        seen.add(key)
        small, long_ = sorted(float(v) for v in fp["size"])
        if not (STAIR_SIZE_M[0][0] <= small <= STAIR_SIZE_M[0][1] and STAIR_SIZE_M[1][0] <= long_ <= STAIR_SIZE_M[1][1]):
            continue
        p = _rect(fp)
        if any(p.intersection(q).area > 0.3 * p.area for q in lifts) or any(
                p.buffer(-0.05).contains(Point(t["x"], t["y"])) and NOT_STAIR_RE.search(CP._fold(t["text"]))
                for t in texts or []):
            continue
        room = level.room_at((p.centroid.x, p.centroid.y))
        beside = (room is not None and (room.get("room_type") in ("hall", "stair") or room["id"] in core)) or \
            any(p.distance(q) <= 0.4 for q in lifts) or \
            any(p.distance(level.polys[i]) <= 0.3 for i in core if i in level.polys)
        if not beside:
            continue
        cars = [r for r in drawn.rectangles(p.buffer(0.05)) if CAR_M[0][0] <= r["size"][0] <= CAR_M[0][1]
                and CAR_M[1][0] <= r["size"][1] <= CAR_M[1][1]]
        if cars:
            continue                                   # a lift car drawn in it: a lift, not a stair
        turn, signs = stair_signs(fp, drawn.segments(p.buffer(0.05)))
        if turn == "U" and small < 2 * U_FLIGHT_M - 1e-6:
            turn = "straight"                          # two flights do not fit: one flight along the band
        if turn:
            found.append({"symbol": s, "footprint": fp, "room": room, "turn": turn, "signs": signs})
    if len(found) > 1:
        return {"several": [f["symbol"]["id"] for f in found]}
    return found[0] if found else None


def _rise(b: dict, lid: str, above: str) -> float:
    """The storey height from ``lid`` to ``above`` (their elevations), else ``STOREY_H_M`` (pure)."""
    lv = {x["id"]: x for x in b.get("levels") or []}
    e0, e1 = (lv.get(lid) or {}).get("elevation"), (lv.get(above) or {}).get("elevation")
    if isinstance(e0, (int, float)) and isinstance(e1, (int, float)) and 2.2 <= e1 - e0 <= 6.0:
        return float(e1 - e0)
    return STOREY_H_M


def _stair_box(b: dict, level: "CP.Level", strokes: list, texts: list) -> tuple:
    """``(box, candidate)`` (pure): the stroke box of a storey that holds its stair with stair strokes inside it (R08
    G3), and the first box in the core without them (a question, no geometry; G2)."""
    lifts = [level.polys[r["id"]] for r in level.rooms if CP.is_lift(r)]
    seen, candidate = set(), None
    for s in b.get("symbols") or []:
        fp = s.get("footprint") or {}
        if s.get("level_id") != level.lid or str(s.get("kind")) not in STAIR_SYMBOL_KINDS or not fp.get("size"):
            continue
        key = (round(fp["center"][0], 2), round(fp["center"][1], 2))
        if key in seen:
            continue
        seen.add(key)
        small, long_ = sorted(float(v) for v in fp["size"])
        if small < STAIR_BOX_M[0] or long_ < STAIR_BOX_M[1] or small * long_ < STAIR_BOX_MIN_M2:
            continue
        p = _rect(fp)
        # a lift (pair) with its diagonals, a shaft, a void or a light well is never the stair
        if any(p.intersection(q).area > 0.3 * p.area for q in lifts) or any(
                p.buffer(-0.05).contains(Point(t["x"], t["y"])) and NOT_STAIR_RE.search(CP._fold(t["text"]))
                for t in texts or []):
            continue
        room = level.room_at((p.centroid.x, p.centroid.y))
        in_core = room is not None and room.get("room_type") in ("hall", "stair")
        if not (in_core or any(p.distance(q) <= 0.4 for q in lifts)):
            continue
        why = stair_evidence(p, strokes, texts)
        if why:
            return {"symbol": s, "footprint": fp, "room": room, "evidence": why}, None
        candidate = candidate or {"symbol": s, "footprint": fp, "room": room}
    return None, candidate


def infer_stairs(b: dict, next_id, texts_by_level: dict, strokes_by_level: Optional[dict] = None,
                 drawn_by_level: Optional[dict] = None) -> tuple:
    """Rule 1 (the module docstring); returns ``(stairs, open)``: the records ``[{level_id, stair, how, reason}]`` of the
    stairs added, and ``[{level_id, candidate, reason}]`` of the storeys left without one (no geometry: a question)."""
    out, open_ = [], []
    if not needs_stair(b):
        return out, open_
    storeys = _storeys(b)
    for k, lv in enumerate(storeys[:-1]):
        lid = lv["id"]
        if stairs_on(b, lid) or not any(r.get("level_id") == lid for r in b.get("rooms") or []):
            continue
        level = CP.Level(b, lid, texts_by_level.get(lid))
        box, candidate = _stair_box(b, level, (strokes_by_level or {}).get(lid) or [], texts_by_level.get(lid) or [])
        base = [f for f in b.get("furniture") or [] if lv.get("typical_of") and f.get("type") == "stair"
                and f.get("level_id") == lv["typical_of"]]
        if base and box is None:
            # a copy of a typical floor takes its floor's stair (drawn or inferred), at the same place
            mode, fp = "typical copy", dict(base[0]["footprint"])
            room = level.room_at(tuple(fp["center"]))
            how = f"{lid} copies the typical floor {lv['typical_of']}: its stair {base[0]['id']} stands here too"
            evidence, source = base[0].get("evidence") or [], base[0].get("source") or "added_by_ai"
        elif box is not None:
            mode, fp, room = "stroke box", box["footprint"], box["room"]
            how = (f"the stroke box {box['symbol']['id']} ({fp['size'][0]:.2f} x {fp['size'][1]:.2f} m, set aside as "
                   f"'{box['symbol'].get('kind')}') in {room['id'] if room else 'the core'} holds {box['evidence']}: "
                   f"the building needs a stair and the reading has none on {lid}")
            evidence, source = box["symbol"].get("evidence") or [], "from_documents"
        elif (sign := _sign_box(b, level, (drawn_by_level or {}).get(lid), texts_by_level.get(lid) or [])) is not None \
                and "several" not in sign:
            mode, fp, room, turn = "stair signs", sign["footprint"], sign["room"], sign["turn"]
            ids = sorted({sg["id"] for sg in sign["signs"]})
            what = "a well line along its long axis (a U stair)" if turn == "U" else "a break diagonal (a straight flight)"
            how = (f"the box {sign['symbol']['id']} ({fp['size'][0]:.2f} x {fp['size'][1]:.2f} m, set aside as "
                   f"'{sign['symbol'].get('kind')}') in {room['id'] if room else 'the core'} holds {what} "
                   f"({', '.join(ids)}): a building of {len(storeys)} storeys has a stair, and none is drawn otherwise on "
                   f"{lid}; its risers follow the storey height")
            evidence = list(sign["symbol"].get("evidence") or [])[:1] + [
                {"file": CP._ev_file(b, lid), "method": "vector", "entity": ",".join(ids), "rule": "stair_signs",
                 "confidence": 0.5}]
            source = "from_documents"
        else:
            cand = (candidate or {}).get("symbol") or {}
            croom = (candidate or {}).get("room") or {}
            several = (sign or {}).get("several") if isinstance(sign, dict) else None
            reason = (f"no stair is drawn or read on {lid}, and the building needs one to reach {storeys[k + 1]['id']}"
                      + (f"; the boxes {', '.join(several)} each hold a stair sign: which is the stair?" if several else
                         f"; the box {cand.get('id')} in {croom.get('id') or 'the core'} has no stair strokes (no tread "
                         f"lines, tread numbers or riser tag): is it the stair?" if cand else "")
                      + " (a question: no stair is built without drawn evidence, R08)")
            open_.append({"level_id": lid, "candidate": cand.get("id"), "reason": reason})
            continue
        kind = {"typical copy": "stair_typical_copy", "stroke box": "stair_box", "stair signs": "stair_signs"}[mode]
        if RG.blocked(kind, b, {"level_id": lid, "symbol": (box or {}).get("symbol", {}).get("id"),
                                "room": (room or {}).get("id"), "why": how}):
            continue
        reason = how + " (inferred; needs review)"
        piece = {"id": next_id("furniture", lid), "level_id": lid, "room_id": (room or {}).get("id"), "type": "stair",
                 "type_raw": None, "source": source,
                 "footprint": {"center": list(fp["center"]), "size": list(fp["size"]),
                               "rotation_deg": fp["rotation_deg"]},
                 "front_deg": None, "height": None, "asset": None, "status": "unverified", "type_method": "inferred",
                 "type_candidates": [], "build": True, "inferred": True,
                 "adjusted_by_ai": {"by": "code", "rule": "stair_missing", "reason": reason},
                 "stair": (stair_dict(fp, reason, sign["turn"], _rise(b, lid, storeys[k + 1]["id"]))
                           if mode == "stair signs" else
                           dict(base[0]["stair"], reason=reason) if mode == "typical copy" and base[0].get("stair")
                           else stair_dict(fp, reason)),
                 "evidence": (list(evidence)[:2] + [{"file": CP._ev_file(b, lid), "method": "inferred",
                                                     "confidence": 0.4, "rule": "stair_missing", "text": reason}])}
        b.setdefault("furniture", []).append(piece)
        above = storeys[k + 1]["id"]
        for sl in b.get("slabs") or []:
            if sl.get("below_level_id") == lid and sl.get("above_level_id") == above:
                sl.setdefault("openings", []).append(
                    {"id": f"sv_{above}_st_{len(sl['openings']) + 1:02d}", "kind": "stair_void",
                     "furniture_id": piece["id"],
                     "polygon": [[round(x, 4), round(y, 4)] for x, y in G.rotated_rectangle(
                         fp["center"], fp["size"], fp["rotation_deg"])], "source": "derived"})
        out.append({"level_id": lid, "stair": piece["id"], "reason": reason, "how": mode})
        if mode == "stair signs":
            b.setdefault("needs_review", []).append(
                {"id": piece["id"], "kind": "stair_inferred", "reason": reason, "crop": None,
                 "room_id": piece["room_id"], "level_id": lid})
    return out, open_


# ------------------------------------------------------------------------------------- the core and the openings
def _sides(level: "CP.Level", o: dict) -> list:
    """The two things on either side of an opening: ``(kind, room or None)`` per side (``Level.kind_at``)."""
    w = level.walls.get(o.get("wall_id"))
    if w is None or not o.get("center"):
        return []
    a, u, _ = CP._axis(w)
    n = (-u[1], u[0])
    reach = float(w.get("thickness") or 0.15) / 2.0 + CP.PROBE_M
    c = o["center"]
    out = []
    for k in (1, -1):
        q = (c[0] + k * n[0] * reach, c[1] + k * n[1] * reach)
        out.append((level.kind_at(q, ""), level.room_at(q), q))
    return out


def _label(r: dict) -> str:
    return CP._fold(r.get("label_raw") or ("" if r.get("label_inferred") else r.get("label")))


def _flat_hall(hall: dict, rooms: dict, links: list) -> bool:
    """A flat's own hall (pure; CS1-02), never grown into the core: its label names an antre, or it holds the doors of
    two or more bedrooms or wet rooms, or the only link of one."""
    if FLAT_HALL_RE.search(_label(hall)):
        return True
    doors = set()
    for a, c, o in links:
        if hall["id"] in (a, c) and o.get("type") == "door" and not o.get("lift_door") and not o.get("virtual"):
            other = c if a == hall["id"] else a
            if (rooms.get(other) or {}).get("room_type") in ("bedroom",) + WET:
                doors.add(other)
    if len(doors) >= 2:
        return True
    return any(sum(1 for a, c, _o in links if rid in (a, c)) == 1 for rid in doors)


def _common_evidence(hall: dict, rooms: dict, links: list, core: set) -> bool:
    """A hall with common evidence (pure; R16 G2): a drawn common-hall word, or two or more flat entrance doors start in
    it (doors to rooms out of the core that are not a flat's bedroom, kitchen or wet room)."""
    from wenart import common_areas as CA

    words = " " + " ".join(B.fold_ascii(_label(hall)).upper().split()) + " "
    if any(f" {w} " in words for w in CA.COMMON_ROOM_WORDS) or hall.get("entrance_hall"):
        return True                     # (an entrance hall the ground-floor rule made: R43, ground_floor.py)
    entrances = {c if a == hall["id"] else a for a, c, o in links if hall["id"] in (a, c) and o.get("type") == "door"
                 and not o.get("virtual") and not o.get("lift_door")}
    entrances = {x for x in entrances if x not in core and (rooms.get(x) or {}).get("room_type") not in
                 ("bedroom", "kitchen") + WET and not CP.is_lift(rooms.get(x) or {})}
    return len(entrances) >= 2


def _core_stair_room(r: dict, level: "CP.Level", near: list, common: bool = False) -> bool:
    """A room holding a stair is the core's only when the stair is the core's (pure; MF3, MF4, REG-01): a stair room, a
    hall or a drawn common room, or a face beside a lift or its lobby (``near``), or one two or more flats' entrance
    doors start in (``common``: ``_common_evidence``), whatever its label or type (13 Nov 2026, review FC-01: real19's
    stair hall took the label of a small shaft drawn in its corner, 'Şaft', and the core collapsed to the lift); never a
    flat's room (``PRIVATE``, an antre) nor a unit's own use (a shop, a store, an office: their stair is the unit's
    own)."""
    from wenart import common_areas as CA

    rtype = r.get("room_type")
    if rtype == "stair":
        return True
    if rtype in PRIVATE + NOT_CORE_TYPES or UNIT_USE_RE.search(_label(r)) or FLAT_HALL_RE.search(_label(r)):
        return False
    if rtype == "hall" or CA.is_common_room(r) or common:
        return True
    p = level.polys.get(r["id"])
    return p is not None and any(p.distance(q) <= 0.4 for q in near)


def core_rooms(b: dict, level: "CP.Level") -> set:
    """The common core of a storey (pure): its lifts and stair rooms, the hall a lift touches (its lobby, never a
    flat's antre), the rooms holding a core stair (``_core_stair_room``), and the halls joined to them by virtual
    separators, or by doorless openings when the hall shows common evidence (``_common_evidence``); never a flat's
    own hall (``_flat_hall``)."""
    rooms = {r["id"]: r for r in level.rooms}
    links = _links(level)
    core = {r["id"] for r in level.rooms if CP.is_lift(r) or r.get("room_type") == "stair"
            or (CP.LIFT_RE.search(CP._fold(r.get("label") or r.get("label_raw")))
                and level.polys[r["id"]].area > CP.LIFT_MAX_M2)}
    lifts = [r for r in level.rooms if CP.is_lift(r)]
    lobbies = []
    # a lift's lobby: the hall the lift touches along the longest stretch, never a flat's antre
    for lift in lifts:
        lp = level.polys[lift["id"]].buffer(0.4)
        touch = [(lp.intersection(level.polys[r["id"]].exterior.buffer(0.05)).area, r) for r in level.rooms
                 if r.get("room_type") == "hall" and r["id"] != lift["id"] and not FLAT_HALL_RE.search(_label(r))]
        touch = [t for t in touch if t[0] > 0.05]
        if touch:
            lobby = max(touch, key=lambda t: t[0])[1]
            core.add(lobby["id"])
            lobbies.append(level.polys[lobby["id"]])
    # 13 Nov 2026 (review FC-02): the room a lift's drawn landing door, or the one put on the face its storey above or
    # below uses (``landing_stacked``), opens into is its lobby, whatever its label or type (real17: the BİNA GİRİŞİ
    # hall read as a shaft); never a flat's room, an antre or a unit's own use
    lift_ids = {r["id"] for r in lifts}
    for a, c, o in links:
        if not o.get("lift_door") or (derived(o) and not o.get("landing_stacked")):
            continue
        for x, y in ((a, c), (c, a)):
            hall = rooms.get(y) or {}
            if x in lift_ids and hall and y not in lift_ids and hall.get("room_type") not in PRIVATE + NOT_CORE_TYPES \
                    and not UNIT_USE_RE.search(_label(hall)) and not FLAT_HALL_RE.search(_label(hall)):
                core.add(y)
                lobbies.append(level.polys[y])
    near = [level.polys[r["id"]] for r in lifts] + lobbies
    below = _storey_below(b, level.lid)
    for f in b.get("furniture") or []:
        # the room holding a core stair, and the hall a stair of the storey below arrives in
        if f.get("level_id") in (level.lid, below) and f.get("type") == "stair" and f.get("footprint"):
            r = level.room_at(tuple(f["footprint"]["center"]))
            if r is None:
                continue
            if f.get("level_id") == level.lid and _core_stair_room(r, level, near,
                                                                   _common_evidence(r, rooms, links, core)):
                core.add(r["id"])
            elif f.get("level_id") != level.lid and r.get("room_type") == "hall" and not _flat_hall(r, rooms, links):
                core.add(r["id"])
    grew = True
    while grew:
        grew = False
        for a, c, o in links:
            if o.get("type") == "door" and not o.get("virtual"):
                continue                                    # a door is where a flat starts
            for x, y in ((a, c), (c, a)):
                hall = rooms.get(y) or {}
                if x in core and y not in core and hall.get("room_type") == "hall" and \
                        not _flat_hall(hall, rooms, links) and \
                        (o.get("virtual") or _common_evidence(hall, rooms, links, core)):
                    core.add(y)
                    grew = True
    return core



def _lift_of(level: "CP.Level", o: dict, lifts: list) -> tuple:
    """``(lift, other room or None, probe point)`` when the opening is in a lift's shaft wall (the lift on one side),
    else ``(None, None, None)`` (pure)."""
    sides = _sides(level, o)
    ids = [x[1]["id"] if x[1] is not None else None for x in sides]
    lift = next((r for r in lifts if r["id"] in ids), None)
    if lift is None:
        return None, None, None
    _kind, other, q = sides[1 - ids.index(lift["id"])]
    return lift, other, q


def _stacked(level: "CP.Level", pieces: list, above: Optional[list] = None) -> list:
    """``[(kept, [others])]`` (pure): openings in stacked parallel walls (centres at most ``STACK_M`` apart across the
    walls, spans overlapping by at least half the shorter): one door read in pieces. The piece matching a lift door on
    the storey above or below (``above``: its openings, centres within ``STACK_MATCH_M`` across and a quarter of a width
    along) is kept, else the drawn one, else the widest (CL-05)."""
    out, used = [], set()
    for i, o in enumerate(pieces):
        wo = level.walls.get(o.get("wall_id"))
        if o["id"] in used or wo is None or not o.get("center"):
            continue
        _a, u, _l = CP._axis(wo)
        n = (-u[1], u[0])
        grp = [o]
        for q in pieces[i + 1:]:
            wq = level.walls.get(q.get("wall_id"))
            if q["id"] in used or wq is None or not q.get("center"):
                continue
            _b, uq, _m = CP._axis(wq)
            if abs(u[0] * uq[1] - u[1] * uq[0]) > CP.PARALLEL_SIN:
                continue
            d = (q["center"][0] - o["center"][0], q["center"][1] - o["center"][1])
            if abs(d[0] * n[0] + d[1] * n[1]) > STACK_M:
                continue
            along = d[0] * u[0] + d[1] * u[1]
            wa, wb = float(o.get("width") or 0.0), float(q.get("width") or 0.0)
            overlap = min(wa / 2.0, along + wb / 2.0) - max(-wa / 2.0, along - wb / 2.0)
            if overlap >= 0.5 * min(wa, wb) > 0:
                grp.append(q)
        if len(grp) > 1:
            def matches(x):
                for y in above or []:
                    d = (x["center"][0] - y["center"][0], x["center"][1] - y["center"][1])
                    if abs(d[0] * n[0] + d[1] * n[1]) <= STACK_MATCH_M + STACK_M and \
                            abs(d[0] * u[0] + d[1] * u[1]) <= 0.25 * float(y.get("width") or 0.9) and \
                            abs(float(x.get("width") or 0) - float(y.get("width") or 0)) <= 0.1:
                        return True
                return False
            kept = next((x for x in grp if matches(x)), None) or next((x for x in grp if not derived(x)), None) or \
                max(grp, key=lambda x: float(x.get("width") or 0))
            used |= {x["id"] for x in grp}
            out.append((kept, [x for x in grp if x is not kept]))
    return out


def _jambs(level: "CP.Level", o: dict) -> Optional[tuple]:
    """``(t0, t1)`` along the opening's wall: the drawn jambs around it (the nearest faces of the walls and piers that
    cross or end on its wall line within ``JAMB_REACH_M`` of its centre), or None (pure; CL-05)."""
    w = level.walls.get(o.get("wall_id"))
    if w is None or not o.get("center"):
        return None
    a, u, _l = CP._axis(w)
    n = (-u[1], u[0])
    c = o["center"]
    tc = (c[0] - a[0]) * u[0] + (c[1] - a[1]) * u[1]
    half = float(w.get("thickness") or 0.15) / 2.0 + 0.05
    left, right = None, None
    for w2 in level.walls.values():
        if w2["id"] == w["id"]:
            continue
        b2, u2, l2 = CP._axis(w2)
        t2 = float(w2.get("thickness") or 0.15) / 2.0
        # 13 Nov 2026 (review FC-03: real10's 3.5 cm plaster stub, read from the door's own panel strokes, was taken
        # for a jamb): a stub shorter than ``JAMB_MIN_M`` or a plaster or panel line (under 6 cm thick) is no jamb
        if l2 < JAMB_MIN_M or 2.0 * t2 < 0.06:
            continue
        if abs(u[0] * u2[1] - u[1] * u2[0]) <= CP.PARALLEL_SIN:
            # a wall on the same line ending at the gap: its end is a jamb
            off = (b2[0] - a[0]) * n[0] + (b2[1] - a[1]) * n[1]
            if abs(off) > half:
                continue
            ends = sorted(((p[0] - a[0]) * u[0] + (p[1] - a[1]) * u[1]) for p in (w2["start"], w2["end"]))
            faces = [ends[1]] if ends[1] <= tc else [ends[0]] if ends[0] >= tc else []
        else:
            # a pier or a cross wall touching the wall line: its two faces
            pts = [(w2["start"][0], w2["start"][1]), (w2["end"][0], w2["end"][1])]
            offs = [(p[0] - a[0]) * n[0] + (p[1] - a[1]) * n[1] for p in pts]
            if min(offs) > half or max(offs) < -half:
                continue
            k = 0.0 if abs(offs[1] - offs[0]) < 1e-9 else max(0.0, min(1.0, -offs[0] / (offs[1] - offs[0])))
            px = pts[0][0] + (pts[1][0] - pts[0][0]) * k
            py = pts[0][1] + (pts[1][1] - pts[0][1]) * k
            t = (px - a[0]) * u[0] + (py - a[1]) * u[1]
            faces = [t + t2] if t <= tc else [t - t2]
        for f in faces:
            if f <= tc and tc - f <= JAMB_REACH_M and (left is None or f > left):
                left = f
            elif f > tc and f - tc <= JAMB_REACH_M and (right is None or f < right):
                right = f
    if left is None or right is None or right - left < LIFT_DOOR_MIN_M:
        return None
    return left, right



def _front_zone(level: "CP.Level", o: dict, q) -> Optional[Polygon]:
    """The ``FRONT_ZONE_M`` deep zone in front of an opening, on the side of probe point ``q`` (pure)."""
    w = level.walls.get(o.get("wall_id"))
    if w is None or not o.get("center") or q is None:
        return None
    _a, u, _l = CP._axis(w)
    c, n = o["center"][:2], (-u[1], u[0])
    side = 1.0 if (q[0] - c[0]) * n[0] + (q[1] - c[1]) * n[1] > 0 else -1.0
    half, t = float(o.get("width") or 0.0) / 2.0, float(w.get("thickness") or 0.15) / 2.0
    pts = [(c[0] + u[0] * a + n[0] * side * d, c[1] + u[1] * a + n[1] * side * d)
           for a, d in ((-half, t), (half, t), (half, t + FRONT_ZONE_M), (-half, t + FRONT_ZONE_M))]
    return Polygon(pts)


def _unmark(b: dict, level: "CP.Level", lifts: list, rec: dict) -> None:
    """Step 0 of rule 2 on one level (every level, every building: an error correction; MF6, S1-20a): a lift-door mark
    on an opening in no passenger lift's shaft wall is undone. A derived gap is an opening again; a drawn door gets its
    drawn operation back (a hinged flat door is never a lift door); a lift door a rule inferred into a flat's room is
    removed. On a lift-named face larger than a car (the whole core) only a drawn door whose far side is a flat's room
    or antre is unmarked (a flat's entrance); the others are review records (a real landing door in a merged face)."""
    lid = level.lid
    drop = set()
    for o in level.openings:
        if not o.get("lift_door") or o.get("virtual") or _lift_of(level, o, lifts)[0] is not None:
            continue
        sides = [s[1] for s in _sides(level, o)]
        named = next((r for r in sides if r is not None and CP.LIFT_RE.search(CP._fold(r.get("label")
                                                                                     or r.get("label_raw")))), None)
        far = next((r for r in sides if r is not None and r is not named), None)
        flat_side = far is not None and (far.get("room_type") in PRIVATE or FLAT_HALL_RE.search(_label(far)) is not None)
        first = (o.get("evidence") or [{}])[0] or {}
        made = first.get("method") == "inferred" or bool(o.get("inferred"))
        if made and flat_side and far.get("room_type") in PRIVATE:
            why = (f"{o['id']} is a lift door a rule inferred into {far['id']} '{far.get('label')}' "
                   f"({far.get('room_type')}), a flat's room, and lies in no passenger lift's shaft wall: removed")
            if not RG.blocked("lift_door_remove", b, {"level_id": lid, "opening": o["id"], "room": far["id"],
                                                     "why": why}):
                drop.add(o["id"])
                rec["removed"].append({"opening": o["id"], "level_id": lid, "reason": why + " (adjusted_by_ai)"})
            continue
        if named is not None and level.polys[named["id"]].area > CP.LIFT_MAX_M2 and CP.is_lift(dict(named, polygon=None)) \
                and not (flat_side and not made):
            rec["review"].append({"opening": o["id"], "level_id": lid,
                                  "reason": f"{o['id']} is marked the landing door of the lift-named face {named['id']} "
                                            f"({level.polys[named['id']].area:.1f} m2, larger than a car: the whole "
                                            f"core?): kept; review whether it is the lift's door"})
            continue
        if RG.blocked("lift_door_unmark", b, {"level_id": lid, "opening": o["id"]}):
            continue
        reason = (f"{o['id']} is marked a lift's landing door but lies in no passenger lift's shaft wall: the mark is "
                  f"undone" + (" (a derived gap again)" if first.get("method") == "derived" else
                               " (its drawn operation back)" if not derived(o) else ""))
        changed = {"lift_door": True, "operation": o.get("operation")}
        o["lift_door"] = False
        if first.get("method") == "derived":
            o.update(type="opening", operation=None, operation_source=None)
        elif not derived(o) and o.get("type") == "door":
            # a drawn door: its drawn operation (kept by the rule that made it sliding), else a swing (null)
            o["operation"] = o.pop("drawn_operation", None)
            o["operation_source"] = o.pop("drawn_operation_source", None)
            if "drawn_swing_side" in o:
                o["swing_side"] = o.pop("drawn_swing_side")
            if flat_side:
                o["flat_entrance"] = True
        o["adjusted_by_ai"] = {"by": "code", "rule": "lift_door_unmark", "reason": reason, "changed": changed}
        rec["unmarked"].append({"opening": o["id"], "level_id": lid, "reason": reason + " (adjusted_by_ai)"})
    if drop:
        b["openings"] = [o for o in b["openings"] if o["id"] not in drop]
        level.openings = [o for o in level.openings if o["id"] not in drop]


def _neighbour_lift_doors(b: dict, lid: str) -> list:
    """The lift doors (``lift_door``) of the storeys right above and below ``lid`` (pure)."""
    ids = [lv["id"] for lv in _storeys(b)]
    k = ids.index(lid) if lid in ids else -1
    near = {ids[j] for j in (k - 1, k + 1) if 0 <= j < len(ids)} if k >= 0 else set()
    return [o for o in b.get("openings") or [] if o.get("level_id") in near and o.get("lift_door") and o.get("center")]


def fix_lift_doors(b: dict, next_id, flats: bool = True) -> dict:
    """Rule 2 (the module docstring); returns ``{"unmarked", "merged", "removed", "review", "retyped", "added"}``.
    Step 0 (``_unmark``) runs on every level of every building; the others only in a building of several flats with a
    common core (``flats``)."""
    rec = {"unmarked": [], "merged": [], "removed": [], "review": [], "retyped": [], "added": []}
    for lv in b.get("levels") or []:
        lid = lv["id"]
        level = CP.Level(b, lid)
        lifts = [r for r in level.rooms if CP.is_lift(r)]
        _unmark(b, level, lifts, rec)
        if not flats or not lifts or level.outline is None:
            continue
        level = CP.Level(b, lid)
        core = core_rooms(b, level)
        stairs = [_rect(f["footprint"]) for f in b.get("furniture") or []
                  if f.get("level_id") == lid and f.get("type") == "stair" and f.get("footprint")
                  and f.get("build") is not False]
        neighbours = _neighbour_lift_doors(b, lid)
        drop = set()
        # 1. one landing door read in pieces in stacked parallel walls: merged first (R19); the kept piece takes the
        # span of the drawn jambs (CL-05)
        for lift in lifts:
            pieces = [o for o in level.openings if o.get("type") in ("door", "opening") and not o.get("virtual")
                      and _lift_of(level, o, lifts)[0] is lift]
            for kept, others in _stacked(level, pieces, neighbours):
                merged = []
                for o in others:
                    why = (f"{o['id']} ({float(o.get('width') or 0):.2f} m) is a piece of the landing door {kept['id']} "
                           f"of the lift {lift['id']}, read in a stacked wall")
                    if derived(o) and not RG.blocked("lift_door_merge", b, {"level_id": lid, "opening": o["id"],
                                                                          "kept": kept["id"], "lift": lift["id"]}):
                        drop.add(o["id"])
                        merged.append(o)
                        rec["merged"].append({"opening": o["id"], "kept": kept["id"], "level_id": lid,
                                              "reason": why + " (adjusted_by_ai: merged)"})
                # (FC-03) a kept piece where the storey above or below has the same door is not re-spanned
                ka, ku, _kl = CP._axis(level.walls[kept["wall_id"]])
                same = any(abs((y["center"][0] - kept["center"][0]) * ku[0] + (y["center"][1] - kept["center"][1]) * ku[1])
                           <= 0.03 and abs((y["center"][0] - kept["center"][0]) * -ku[1]
                                           + (y["center"][1] - kept["center"][1]) * ku[0]) <= STACK_M
                           and abs(float(kept.get("width") or 0) - float(y.get("width") or 0)) <= 0.03
                           for y in neighbours)
                jambs = _jambs(level, kept) if merged and not same else None
                if jambs is not None and derived(kept):
                    w = level.walls[kept["wall_id"]]
                    a, u, _l = CP._axis(w)
                    t0, t1 = jambs
                    ext = [((x["center"][0] - a[0]) * u[0] + (x["center"][1] - a[1]) * u[1]) + s * float(x.get("width")
                                                                                                   or 0) / 2.0
                           for x in [kept] + merged for s in (-1, 1)]
                    if t1 - t0 > LIFT_DOOR_WIDE_M or t0 < min(ext) - 0.1 or t1 > max(ext) + 0.1:
                        continue                # the shaft's own walls, not the door's jambs

                    old = float(kept.get("width") or 0.0)
                    if abs((t1 - t0) - old) > 0.02 or abs(((t0 + t1) / 2.0) - ((kept["center"][0] - a[0]) * u[0]
                                                                                + (kept["center"][1] - a[1]) * u[1])) > 0.02:
                        kept.setdefault("drawn_width", old)
                        kept.setdefault("drawn_center", list(kept["center"]))
                        kept["width"] = round(t1 - t0, 3)
                        kept["center"] = level.at(kept["wall_id"], (t0 + t1) / 2.0)
                        rec["merged"].append({"opening": kept["id"], "kept": kept["id"], "level_id": lid,
                                              "reason": f"{kept['id']} spans the drawn jambs of the lift {lift['id']}'s "
                                                        f"landing door ({t1 - t0:.2f} m, read {old:.2f} m; "
                                                        f"adjusted_by_ai)"})
        # 2. what a lift never opens onto: rejected when derived or inferred, a review record when drawn (R16 G6)
        for o in level.openings:
            if o["id"] in drop or o.get("virtual") or o.get("type") not in ("door", "opening", "window"):
                continue
            width = float(o.get("width") or 0.0)
            lift, other, q = _lift_of(level, o, lifts)
            if lift is None and width < PIECE_MIN_M and o.get("center"):
                # a sliver of a 'door' in the shaft wall between two lifts or at a lift's corner is the lift's
                near = [r for r in lifts if level.polys[r["id"]].distance(Point(o["center"][:2])) <= 0.45]
                lift = near[0] if near else None
            if lift is None:
                continue
            why = None
            if width < PIECE_MIN_M:
                why = f"{o['id']} ({width:.2f} m) is a sliver in the lift shaft {lift['id']} (under {PIECE_MIN_M} m)"
            elif other is not None and other.get("room_type") in PRIVATE and other["id"] not in core:
                why = (f"{o['id']} opens the lift {lift['id']} into {other['id']} '{other.get('label')}' "
                       f"({other.get('room_type')}), a flat's room: a lift opens only onto the common hall")
            elif o.get("type") == "window":
                why = f"{o['id']} is a window in the lift shaft {lift['id']}"
            else:
                zone = _front_zone(level, o, q)
                cover = sum(zone.intersection(st).area for st in stairs) if zone is not None else 0.0
                if cover >= FRONT_FLIGHT_M2:
                    why = (f"{o['id']} opens the lift {lift['id']} onto a stair flight (its {FRONT_ZONE_M} m front zone "
                           f"covers {cover:.2f} m2 of it): a lift opens onto the common hall")
            if why is None:
                continue
            if not derived(o):
                rec["review"].append({"opening": o["id"], "level_id": lid,
                                      "reason": why + " (a drawn symbol: kept; review the room type or the door)"})
                continue
            if RG.blocked("lift_door_remove", b, {"level_id": lid, "opening": o["id"], "lift": lift["id"],
                                                 "room": (other or {}).get("id"), "why": why}):
                continue
            drop.add(o["id"])
            rec["removed"].append({"opening": o["id"], "level_id": lid, "reason": why + " (adjusted_by_ai)"})
        if drop:
            b["openings"] = [o for o in b["openings"] if o["id"] not in drop]
            level = CP.Level(b, lid)
            core = core_rooms(b, level)
        served_lifts = [r for r in lifts if not CP.is_pit(r)]       # a pit level gets no landing door
        rec["retyped"] += _landing_doors(b, level, served_lifts, core)
        for lift in served_lifts:
            if _core_door(level, lift, core) is None:
                n_added = len(rec["added"])
                _add_landing_door(b, level, lv, lift, core, neighbours, next_id, rec)
                if len(rec["added"]) > n_added:
                    core = core_rooms(b, level)          # the room the stacked door opens into is the lobby (FC-02)
            # 4. once the lift opens onto the core, its other derived or inferred openings into a room that is not
            # the core nor a hall (an unread room, the outside) go; drawn ones are review records (a through-car)
            door = _core_door(level, lift, core)
            if door is None:
                # 13 Nov 2026 (review FC-01, FC-02): a served lift is never left without a landing door unasked
                if not any(_lift_of(level, o, [lift])[0] is lift for o in level.openings
                           if o.get("type") in ("door", "opening") and not o.get("virtual")):
                    b.setdefault("needs_review", []).append({
                        "id": f"lift:{lid}:{lift['id']}", "kind": "lift_no_landing_door", "crop": None,
                        "room_id": lift["id"], "level_id": lid,
                        "reason": f"the lift {lift['id']} on {lid} has no landing door and no face the rules may "
                                  f"put one on (the landing hall not read?): to review"})
                continue
            gone = set()
            seen = {r["opening"] for r in rec["review"] if r.get("level_id") == lid}
            for o in level.openings:
                if o is door or o.get("virtual") or o.get("type") not in ("door", "opening") or o["id"] in seen:
                    continue
                lift2, other, _q = _lift_of(level, o, [lift])
                if lift2 is None or (other is not None and (other["id"] in core or other.get("room_type") == "hall"
                                                            or CP.is_lift(other))):
                    continue
                where = (f"{other['id']} '{other.get('label')}' ({other.get('room_type')})" if other is not None else
                         "no room (the outside or an unread room)")
                why = (f"the lift {lift['id']} opens onto the common hall through {door['id']}; {o['id']} opens it into "
                       f"{where}, not the core: a second landing door")
                if not derived(o):
                    rec["review"].append({"opening": o["id"], "level_id": lid,
                                          "reason": why + " (a drawn symbol: kept; a through-car or a misread room?)"})
                    continue
                if RG.blocked("lift_door_remove", b, {"level_id": lid, "opening": o["id"], "lift": lift["id"],
                                                     "room": (other or {}).get("id"), "why": why}):
                    continue
                gone.add(o["id"])
                rec["removed"].append({"opening": o["id"], "level_id": lid, "reason": why + " (adjusted_by_ai)"})
            if gone:
                b["openings"] = [o for o in b["openings"] if o["id"] not in gone]
                level.openings = [o for o in level.openings if o["id"] not in gone]
    return rec


def _core_door(level: "CP.Level", lift: dict, core: set) -> Optional[dict]:
    """The lift's door or opening onto the core or a hall, or None (pure)."""
    for o in level.openings:
        sides = _sides(level, o) if o.get("type") in ("door", "opening") and not o.get("virtual") else []
        ids = [x[1]["id"] if x[1] is not None else None for x in sides]
        if lift["id"] in ids:
            other = sides[1 - ids.index(lift["id"])][1]
            if other is not None and not CP.is_lift(other) and (other["id"] in core or other.get("room_type") == "hall"):
                return o
    return None


def _add_landing_door(b: dict, level: "CP.Level", lv: dict, lift: dict, core: set, neighbours: list, next_id,
                      rec: dict) -> None:
    """Step 3 of rule 2: a lift with no opening onto the common hall gets one inferred landing door, on the face where
    the storey above or below has its lift door (``STACK_MATCH_M``), else on the face away from a drawn counterweight,
    else on the longest face onto a common hall or stair room; no face (or none away from the counterweight): a review
    record, no geometry (REG-01, MF3)."""
    lid = level.lid
    faces = list(_hall_faces(level, lift, core))
    lc = level.polys[lift["id"]].centroid

    def stacked(x):
        """The along-wall position of a lift door above or below on this face, or None."""
        f, p0, p1 = x
        w = level.walls[f["wall_id"]]
        a, u, _l = CP._axis(w)
        half = float(w.get("thickness") or 0.15) / 2.0
        for o in neighbours:
            c = o["center"]
            off = abs((c[0] - a[0]) * -u[1] + (c[1] - a[1]) * u[0])
            t = (c[0] - a[0]) * u[0] + (c[1] - a[1]) * u[1]
            if off <= half + STACK_MATCH_M and p0 - STACK_MATCH_M <= t <= p1 + STACK_MATCH_M:
                return t
        return None

    # 13 Nov 2026 (review FC-02): the face the storey above or below uses comes first, whatever the room behind it is
    # read as (real17: the entrance hall read as a shaft), never a flat's room or a unit's own use
    found = [(x, stacked(x)) for x in faces + [x for x in _hall_faces(level, lift, core, any_room=True)
                                               if x not in faces]]
    found = [(x, t) for x, t in found if t is not None]
    how = None
    if not found and not faces:
        rec["review"].append({"opening": None, "level_id": lid, "lift": lift["id"],
                              "reason": f"the lift {lift['id']} has no landing door, no face onto the common core and "
                                        f"no face where the storey above or below has its door (the landing hall not "
                                        f"read?): no door inferred, to review"})
        return
    stacked_face = False
    if found:
        (f, p0, p1), t = found[0]
        width = min(LIFT_DOOR_M[0], p1 - p0)
        t = max(p0 + width / 2.0, min(p1 - width / 2.0, t))
        how = "where the storey above or below has the lift's door"
        stacked_face = True
        if f["hall"] not in core:
            r = next((x for x in level.rooms if x["id"] == f["hall"]), {})
            rec["review"].append({"opening": None, "level_id": lid, "lift": lift["id"], "room": f["hall"],
                                  "reason": f"the lift {lift['id']}'s landing door is put on the face its storey above "
                                            f"or below uses, onto {f['hall']} '{r.get('label')}' ({r.get('room_type')}), "
                                            f"a room not read as the common hall: review its type"})
    else:
        cw = _counterweight(b, level, lift)
        if cw is not None:
            def away(x):
                f, p0, p1 = x
                mid = level.at(f["wall_id"], (p0 + p1) / 2.0)
                v1, v2 = (mid[0] - lc.x, mid[1] - lc.y), (cw[0] - lc.x, cw[1] - lc.y)
                n1, n2 = math.hypot(*v1), math.hypot(*v2)
                return (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2) < -0.5 if n1 > 1e-9 and n2 > 1e-9 else False
            faces = [x for x in faces if away(x)]
            if not faces:
                rec["review"].append({"opening": None, "level_id": lid, "lift": lift["id"],
                                      "reason": f"the lift {lift['id']} has no landing door and no face onto the common "
                                                f"hall opposite its drawn counterweight: no door inferred, to review "
                                                f"(the landing hall not read?)"})
                return
            how = "on the face away from the drawn counterweight"
        f, p0, p1 = max(faces, key=lambda x: x[2] - x[1])
        width = min(LIFT_DOOR_M[0], p1 - p0)
        t = (p0 + p1) / 2.0
        how = how or "on the longest face onto the common hall"
    if width < LIFT_DOOR_MIN_M or RG.blocked("lift_door_add", b, {"level_id": lid, "lift": lift["id"],
                                                                   "wall": f["wall_id"], "room": f["hall"]}):
        return
    reason = (f"the lift {lift['id']} has no landing door onto the common hall: one inferred on {f['wall_id']} facing "
              f"{f['hall']}, {how}")
    o = CP._new_opening("door", next_id("door", lid), level, f["wall_id"], t, width, LIFT_DOOR_M[1], None, reason, lift,
                        {"kind": "hall"}, CP._ev_file(b, lid), lv.get("region_id"), "default lift door")
    o["operation"], o["lift_door"] = "sliding", True
    o["inference"]["rule"] = "lift_door"
    if stacked_face:
        o["landing_stacked"] = True
    b["openings"].append(o)
    level.openings.append(o)
    rec["added"].append({"opening": o["id"], "level_id": lid, "reason": reason + " (inferred)"})



def _landing_doors(b: dict, level: "CP.Level", lifts: list, core: set) -> list:
    """A doorless opening between a lift and the common hall is the lift's landing door: retyped to a sliding door in
    place (R19, C0034); one wider than ``LIFT_DOOR_WIDE_M`` is narrowed to a lift door about its centre
    (``drawn_width`` kept). Returns the records."""
    out = []
    for o in level.openings:
        if o.get("type") != "opening" or o.get("virtual"):
            continue
        lift, other, _q = _lift_of(level, o, lifts)
        if lift is None or other is None or CP.is_lift(other) or \
                not (other["id"] in core or other.get("room_type") == "hall"):
            continue
        if RG.blocked("lift_door_retype", b, {"level_id": level.lid, "opening": o["id"], "lift": lift["id"],
                                              "room": other["id"]}):
            continue
        width = float(o.get("width") or 0.0)
        reason = (f"the doorless opening {o['id']} ({width:.2f} m) between the lift {lift['id']} and the common hall "
                  f"{other['id']} is the lift's landing door: a sliding door")
        o.update(drawn_type="opening", type="door", operation="sliding", operation_source="assumed", sill_height=None,
                 lift_door=True, height=max(float(o.get("height") or 0.0), LIFT_DOOR_M[1]),
                 adjusted_by_ai={"by": "code", "rule": "lift_door", "reason": reason,
                                 "changed": {"type": "opening", "width": width}})
        if width > LIFT_DOOR_WIDE_M:
            o["drawn_width"], o["width"] = width, LIFT_DOOR_M[0]
        out.append({"opening": o["id"], "level_id": level.lid, "reason": reason + " (adjusted_by_ai)"})
    return out


def _counterweight(b: dict, level: "CP.Level", lift: dict) -> Optional[tuple]:
    """The centre of a lift's counterweight (a piece in the shaft at most 0.5 m wide and under 0.6 m2), or None."""
    p = level.polys[lift["id"]]
    for f in b.get("furniture") or []:
        fp = f.get("footprint") or {}
        if f.get("level_id") != level.lid or not fp.get("size") or f.get("type") == "stair":
            continue
        w, d = sorted(float(v) for v in fp["size"])
        if w <= 0.5 and w * d < 0.6 and p.contains(Point(fp["center"][:2])):
            return tuple(fp["center"][:2])
    return None


def _hall_faces(level: "CP.Level", lift: dict, core: set, any_room: bool = False) -> list:
    """``[(face, t0, t1)]``: the stretches of the lift's walls with a room of the core on the other side (a common hall,
    a stair room, a common room, the room holding the core stair whatever its label: FC-01), free of openings; never a
    room with a unit's or a flat's use (REG-01, MF4). ``any_room``: any room but those, core or not (FC-02: the face the
    storey above or below uses, whatever the room behind is read as)."""
    p = level.polys[lift["id"]]
    x0, y0, x1, y1 = p.bounds

    def landing(r) -> bool:
        return (any_room or r["id"] in core) and not CP.is_lift(r) and not UNIT_USE_RE.search(_label(r)) and \
            r.get("room_type") not in PRIVATE + NOT_CORE_TYPES and not FLAT_HALL_RE.search(_label(r))
    out = []
    for w in level.walls.values():
        xs, ys = (w["start"][0], w["end"][0]), (w["start"][1], w["end"][1])
        if max(xs) < x0 - 0.5 or min(xs) > x1 + 0.5 or max(ys) < y0 - 0.5 or min(ys) > y1 + 0.5:
            continue
        a, u, length = CP._axis(w)
        if length < LIFT_DOOR_MIN_M:
            continue
        n = (-u[1], u[0])
        reach = float(w.get("thickness") or 0.15) / 2.0 + CP.PROBE_M
        steps = max(1, int(length / CP.SAMPLE_M))
        cur = None
        for k in range(steps + 1):
            t = length * k / steps
            c = (a[0] + u[0] * t, a[1] + u[1] * t)
            sides = [level.room_at((c[0] + s * n[0] * reach, c[1] + s * n[1] * reach)) for s in (1, -1)]
            ids = [r["id"] if r else None for r in sides]
            hall = None
            if lift["id"] in ids:
                other = sides[1 - ids.index(lift["id"])]
                if other is not None and other["id"] != lift["id"] and landing(other):
                    hall = other["id"]
            if hall and cur is not None and cur["hall"] == hall:
                cur["t1"] = t
            elif hall:
                cur = {"wall_id": w["id"], "t0": t, "t1": t, "hall": hall, "kind": "hall"}
                out.append(cur)
            else:
                cur = None
    res = []
    for f in out:
        if f["t1"] - f["t0"] < LIFT_DOOR_MIN_M:
            continue
        for p0, p1 in level.free(f):
            res.append((f, p0, p1))
    return res



def _links(level: "CP.Level", skip=()) -> list:
    """``[(room a, room b, opening)]`` (pure): the rooms each door, opening or virtual separator joins (a separator: the
    two rooms within 0.15 m of its line's midpoint), without the openings in ``skip``."""
    out = []
    for o in level.openings:
        if o["id"] in skip:
            continue
        if o.get("virtual"):
            line = o.get("line") or []
            if len(line) != 2:
                continue
            mid = Point((line[0][0] + line[1][0]) / 2.0, (line[0][1] + line[1][1]) / 2.0)
            near = [r["id"] for r in level.rooms if level.polys[r["id"]].distance(mid) <= 0.15]
        elif o.get("type") in ("door", "opening"):
            near = [s[1]["id"] for s in _sides(level, o) if s[1] is not None]
        else:
            continue
        if len(near) == 2 and near[0] != near[1]:
            out.append((near[0], near[1], o))
    return out


def _reaches(level: "CP.Level", start: set, target: str, skip=()) -> bool:
    """True when room ``target`` is reached from the rooms ``start`` through the level's doors, openings and virtual
    separators without the openings ``skip`` (an id or a set of ids; pure)."""
    skip = {skip} if isinstance(skip, str) else set(skip or ())
    adj: dict = {}
    for a, c, _o in _links(level, skip):
        adj.setdefault(a, set()).add(c)
        adj.setdefault(c, set()).add(a)
    seen, todo = set(start), list(start)
    while todo:
        for y in adj.get(todo.pop(), ()):
            if y not in seen:
                seen.add(y)
                todo.append(y)
    return target in seen



def _gap_window(level: "CP.Level", o: dict, drawn, texts: list) -> Optional[dict]:
    """A window drawn in a gap (pure but for the drawing's query; CL-01, MF9): two or more strokes on a window layer
    along the wall inside the gap, or a window size tag (``P150/50``, ``150/50``) in it; ``{t0, t1, height, strokes,
    tag}`` along the wall, or None."""
    w = level.walls.get(o.get("wall_id"))
    if w is None or not o.get("center"):
        return None
    a, u, _l = CP._axis(w)
    n = (-u[1], u[0])
    c = o["center"]
    tc = (c[0] - a[0]) * u[0] + (c[1] - a[1]) * u[1]
    half, th = float(o.get("width") or 0.0) / 2.0, float(w.get("thickness") or 0.15) / 2.0 + 0.1

    def pt(t, s):
        return (a[0] + u[0] * t + n[0] * s, a[1] + u[1] * t + n[1] * s)
    box = Polygon([pt(tc - half, -th), pt(tc + half, -th), pt(tc + half, th), pt(tc - half, th)])
    lines = []
    if drawn is not None:
        for s in drawn.segments(box):
            if not WINDOW_LAYER_RE.search(B.fold_ascii(str(s.get("layer") or "")).lower()):
                continue
            d = (s["b"][0] - s["a"][0], s["b"][1] - s["a"][1])
            if s["length"] > 0.05 and abs(d[0] * n[0] + d[1] * n[1]) <= 0.1 * s["length"]:
                lines.append(s)
    tag = None
    for t in texts or []:
        m = WINDOW_TAG_RE.match(str(t.get("text") or ""))
        if m and box.buffer(0.6).contains(Point(t["x"], t["y"])):
            tag = (int(m.group(1)) / 100.0, int(m.group(2)) / 100.0, str(t["text"]).strip())
            break
    if tag is not None and tag[1] >= DOOR_TAG_H_M:
        return {"door_tag": tag[2]}         # a door's size tag (100/210): a door the reading did not read
    if len(lines) >= 2:
        ts = [((p[0] - a[0]) * u[0] + (p[1] - a[1]) * u[1]) for s in lines for p in (s["a"], s["b"])]
        t0, t1 = max(min(ts), tc - half), min(max(ts), tc + half)
    elif tag is not None and tag[0] < 2 * half:
        t0, t1 = tc - tag[0] / 2.0, tc + tag[0] / 2.0
    else:
        return None
    if t1 - t0 < GAP_WINDOW_MIN_M:
        return None
    return {"t0": t0, "t1": t1, "height": tag[1] if tag else GAP_WINDOW_H_M, "tag": tag[2] if tag else None,
            "strokes": sorted({s["id"] for s in lines})[:6]}


def close_core_gaps(b: dict, drawn_by_level: Optional[dict] = None, texts_by_level: Optional[dict] = None) -> dict:
    """Rule 3 (the module docstring); returns ``{"closed", "windows", "review"}``. Each gap is judged against the
    openings still left (MF5, CS1-01, CL-03); a bedroom's or wet room's gap that is its only link is a review record
    (CS1-02); a window drawn in a gap stays as that window, the rest of the gap closed (CL-01, MF9); a closing that
    would leave a room that reached the core unreached is undone and listed for review (CL-06)."""
    out = {"closed": [], "windows": [], "review": []}
    for lv in b.get("levels") or []:
        lid = lv["id"]
        level = CP.Level(b, lid)
        core = core_rooms(b, level)
        if not core:
            continue
        before = {r["id"] for r in level.rooms if r.get("room_type") in PRIVATE and r["id"] not in core
                  and _reaches(level, core, r["id"])}
        links = _links(level)
        drawn = (drawn_by_level or {}).get(lid)
        texts = (texts_by_level or {}).get(lid) or []
        drop, cand = [], {}
        for o in level.openings:
            if o.get("type") != "opening" or o.get("virtual"):
                continue
            pair = [x[1] for x in _sides(level, o) if x[1] is not None]
            if len(pair) != 2:
                continue
            a, c = pair
            if (a["id"] in core) == (c["id"] in core):
                continue
            flat = c if a["id"] in core else a
            rtype = flat.get("room_type")
            if rtype in WET + ("bedroom",):
                if not any(flat["id"] in (x, y) and oo["id"] != o["id"] for x, y, oo in links):
                    out["review"].append({"opening": o["id"], "level_id": lid, "room": flat["id"],
                                          "reason": f"the unclassified gap {o['id']} joins {flat['id']} "
                                                    f"'{flat.get('label')}' ({rtype}) to the common core and is the "
                                                    f"room's only link: kept, to review (a misread room or door?)"})
                    continue
                why = "a bathroom, WC, shower or bedroom never opens onto the common core"
            elif rtype in PRIVATE and _reaches(level, core, flat["id"], set(drop) | {o["id"]}):
                why = "the room reaches the core through its flat's entrance as well: this gap is a second link"
            else:
                continue                        # a kitchen or living room's only link: an open-plan flat's entrance
            tagged = (_gap_window(level, o, drawn, texts) or {}).get("door_tag")
            if tagged:
                out["review"].append({"opening": o["id"], "level_id": lid, "room": flat["id"],
                                      "reason": f"the unclassified gap {o['id']} joins {flat['id']} "
                                                f"'{flat.get('label')}' ({rtype}) to the common core, but the door's "
                                                f"size tag '{tagged}' is drawn in it: a door the reading did not read "
                                                f"(a flat's entrance?): kept, to review"})
                continue
            if RG.blocked("core_gap", b, {"level_id": lid, "opening": o["id"], "room": flat["id"],
                                          "core_room": (a if flat is c else c)["id"]}):
                continue
            drop.append(o["id"])
            cand[o["id"]] = (o, flat, why)
        # never cut a room off the core (CL-06): a closing that leaves a room unreached is undone, last first
        lost = {rid for rid in before if not _reaches(level, core, rid, set(drop))}
        for oid in list(reversed(drop)):
            if not lost:
                break
            trial = [x for x in drop if x != oid]
            now = {rid for rid in before if not _reaches(level, core, rid, set(trial))}
            if len(now) < len(lost):
                drop, lost = trial, now
                o, flat, _why = cand[oid]
                out["review"].append({"opening": oid, "level_id": lid, "room": flat["id"],
                                      "reason": f"closing the gap {oid} would cut {flat['id']} '{flat.get('label')}' "
                                                f"and its flat off the core (no other way in is read): kept, to review "
                                                f"(the flat's entrance door is not read?)"})
        if not drop:
            continue
        gone = set()
        for oid in drop:
            o, flat, why = cand[oid]
            width = float(o.get("width") or 0)
            win = _gap_window(level, o, drawn, texts)
            text = (f"the unclassified gap {oid} ({width:.2f} m) joins {flat['id']} '{flat.get('label')}' "
                    f"({flat.get('room_type')}) to the common core: {why}; a flat meets the core only through its "
                    f"entrance door")
            if win is not None:
                t0, t1, h = win["t0"], win["t1"], float(win["height"])
                sill = max(0.0, GAP_WINDOW_HEAD_M - h)
                what = (f"the window tag '{win['tag']}'" if win["tag"] else "") + \
                    (" and " if win["tag"] and win["strokes"] else "") + \
                    (f"window strokes {', '.join(win['strokes'])}" if win["strokes"] else "")
                o.update(drawn_type="opening", drawn_width=width, drawn_center=list(o["center"]), type="window",
                         width=round(t1 - t0, 3), center=level.at(o["wall_id"], (t0 + t1) / 2.0),
                         sill_height=round(sill, 3), height=round(h, 3), operation=None, operation_source=None,
                         adjusted_by_ai={"by": "code", "rule": "core_gap_window",
                                         "reason": text + f"; {what} drawn in it: the window stays "
                                                          f"({t1 - t0:.2f} m), the rest of the gap is closed",
                                         "changed": {"type": "opening", "width": width}})
                out["windows"].append({"opening": oid, "level_id": lid,
                                       "reason": text + f"; {what} drawn in it: kept as a {t1 - t0:.2f} m window, the "
                                                        f"rest closed (adjusted_by_ai)"})
                continue
            gone.add(oid)
            out["closed"].append({"opening": oid, "level_id": lid, "reason": text + " (adjusted_by_ai: closed)"})
        if gone:
            b["openings"] = [o for o in b["openings"] if o["id"] not in gone]
    return out



# --------------------------------------------------------------------------------------------------- 4. entrances
def ground_zs(b: dict) -> list:
    """The ground heights the reading knows around the building (``site.ground``: its level marks and its flat surface;
    pure)."""
    g = (b.get("site") or {}).get("ground") or {}
    zs = [float((x.get("z") or {}).get("value")) for x in g.get("levels") or []
          if isinstance(x, dict) and isinstance((x.get("z") or {}).get("value"), (int, float))]
    flat = (g.get("surface") or {}).get("flat_z")
    if isinstance(flat, (int, float)):
        zs.append(float(flat))
    return zs


def entrance_storeys(b: dict, texts_by_level: Optional[dict] = None) -> list:
    """``[(level, why)]``: the storeys a building entrance may be on (pure; R09, R24 item 4): a storey with an entrance
    word in its core first, then the base storeys whose floor lies within ``ENTRANCE_LEVEL_M`` of a ground height the
    reading knows; the order-0 storey only when no ground is read."""
    storeys = _storeys(b)
    out, seen = [], set()
    for lv in storeys:
        for t in (texts_by_level or {}).get(lv["id"]) or []:
            if ENTRANCE_WORD_RE.search(CP._fold(t.get("text"))):
                level = CP.Level(b, lv["id"])
                r = level.room_at((t["x"], t["y"]))
                if r is not None and r["id"] in core_rooms(b, level) and lv["id"] not in seen:
                    out.append((lv, f"the entrance word '{t['text']}' in its core"))
                    seen.add(lv["id"])
    zs = ground_zs(b)
    for lv in storeys:
        if lv["id"] in seen or not isinstance(lv.get("elevation"), (int, float)):
            continue
        near = [z for z in zs if abs(float(lv["elevation"]) - z) <= ENTRANCE_LEVEL_M]
        if near:
            out.append((lv, f"its floor {float(lv['elevation']):+.2f} m lies within {ENTRANCE_LEVEL_M} m of the ground "
                            f"{min(near, key=lambda z: abs(float(lv['elevation']) - z)):+.2f} m"))
            seen.add(lv["id"])
    if not zs:
        ground = next((lv for lv in storeys if (lv.get("order") or 0) == 0), None)
        if ground is not None and ground["id"] not in seen:
            out.append((ground, "the ground floor (no ground height read)"))
    return out


def _entrance_record(b: dict, o: dict, level: "CP.Level", lv: dict, hall: dict, face: dict, reason: str) -> dict:
    """The ``site.entrances`` record of an inferred building entrance (CS1-05), with the levels model's step rules: the
    hall's floor, the ground the reading knows (else at the floor), the rise, the steps and landing."""
    from wenart.blender import site as S
    from wenart.levels import model as LM
    from wenart.levels.rules import level_params, steps_for

    params = level_params((b.get("project") or {}).get("brief"))
    w = level.walls[face["wall_id"]]
    _a, u, _l = CP._axis(w)
    n = (-u[1], u[0])
    side = 1.0 if face.get("side", 1) >= 0 else -1.0
    outward = (-n[0] * side, -n[1] * side)
    ht = float(w.get("thickness") or 0.15) / 2.0
    cx, cy = o["center"][:2]
    threshold = LM.room_floor_z(b, hall)
    zs = ground_zs(b)
    gz = min(zs, key=lambda z: abs(threshold - z)) if zs else threshold
    rise = max(threshold - gz, 0.0)
    width = float(o.get("width") or ENTRANCE_DOOR_M[0])
    steps = steps_for(rise, width + float(params["landing_extra_width"]), params)
    north, known = LM._north(b)
    o["threshold_z"] = round(threshold, 3)
    return {"door_id": o["id"], "level_id": lv["id"], "room_id": hall["id"], "threshold_z": round(threshold, 3),
            "ground_z": round(gz, 3), "rise": round(rise, 3),
            "ground_source": "the ground the reading knows" if zs else "no ground read: at the floor (assumed)",
            "centre": [round(cx, 4), round(cy, 4)], "outward": [round(outward[0], 6), round(outward[1], 6)],
            "face": [round(cx + outward[0] * ht, 4), round(cy + outward[1] * ht, 4)], "width": round(width, 3),
            "half_t": round(ht, 4), "side": S.side_of(outward, north, known),
            "solution": "steps" if steps else "none", "steps": steps, "ramp": None,
            "landing": ({"width": round(width + float(params["landing_extra_width"]), 3),
                         "depth": round(float(params["landing_depth"]), 3), "z": round(threshold, 3)} if steps else None),
            "main": False, "drawn": False, "inferred": True, "into_air": False, "upper_floor": False,
            "below_ground": False, "terrain_lowered": False, "reason": reason + " (inferred)",
            "evidence": [{"file": CP._ev_file(b, lv["id"]), "method": "inferred", "confidence": 0.4,
                          "rule": "inferred_entrance", "text": reason}]}


SIZE_TAG_RE = re.compile(r"^\s*([kp])\s*[:.]?\s*(\d{2,3})\s*/\s*(\d{2,3})\s*$")
TAG_REACH_M = 0.9               # a size tag this far beyond an opening's half width is that opening's
DOOR_TAG_MIN_H_M = 1.80         # a K/P tag this high is a door's; lower a window's (P:120/150)


def _tag_of(o: dict, texts: list) -> Optional[tuple]:
    """``(kind 'door' | 'window', width, height, text, distance)``: the nearest K:/P: size tag at an opening (within
    its half width and ``TAG_REACH_M``), or None (pure)."""
    c = o.get("center")
    if not c:
        return None
    reach = float(o.get("width") or 0.0) / 2.0 + TAG_REACH_M
    best = None
    for t in texts or []:
        m = SIZE_TAG_RE.match(B.fold_ascii(str(t.get("text") or "")).lower())
        if not m:
            continue
        d = math.dist((t["x"], t["y"]), c[:2])
        if d <= reach and (best is None or d < best[4]):
            w, h = int(m.group(2)) / 100.0, int(m.group(3)) / 100.0
            kind = "door" if m.group(1) == "k" and h >= DOOR_TAG_MIN_H_M else "window"
            best = (kind, w, h, str(t["text"]).strip(), d)
    return best


def size_tags(b: dict, texts_by_level: Optional[dict]) -> dict:
    """R37 and the drawn building entrance (13 Nov 2026, review S1-09b; in place): an outer door into a room that is no
    hall whose nearest size tag is a window's (P:120/150) is that window, its entrance record dropped; a doorless outer
    gap into a hall or stair room whose nearest tags are doors' (K:100/210, K:50/210: a pair is a double door) is that
    door, with its ``site.entrances`` record. Returns ``{"windows": [...], "doors": [...]}``."""
    out = {"windows": [], "doors": []}
    site = b.get("site") if isinstance(b.get("site"), dict) else None
    if site is None or not texts_by_level:
        return out
    levels = {lv["id"]: lv for lv in b.get("levels") or []}
    gone = set()
    for lid, texts in sorted(texts_by_level.items()):
        lv = levels.get(lid)
        if lv is None:
            continue
        level = CP.Level(b, lid)
        if level.outline is None:
            continue
        for o in list(level.openings):
            if o.get("virtual") or o.get("type") not in ("door", "opening") or o.get("lift_door"):
                continue
            sides = _sides(level, o)
            if [s[0] for s in sides].count("outside") != 1:
                continue
            room = next((s[1] for s in sides if s[1] is not None), None)
            tag = _tag_of(o, texts)
            if room is None or tag is None:
                continue
            kind, tw, th, text, _d = tag
            if o["type"] == "door" and kind == "window" and room.get("room_type") not in ("hall", "stair"):
                why = (f"{o['id']} ({o.get('width')} m) opens from {room['id']} '{room.get('label')}' to the outside and "
                       f"its size tag '{text}' is a window's: a window (R37)")
                if RG.blocked("entrance_tags", b, {"level_id": lid, "opening": o["id"], "why": why}):
                    continue
                o.update(drawn_type="door", type="window", width=round(tw, 3) if abs(tw - float(o.get("width") or 0))
                         <= 0.3 else o.get("width"), height=round(th, 3), sill_height=round(max(0.0, 2.2 - th), 3),
                         operation=None, operation_source=None, swing_side=None,
                         adjusted_by_ai={"by": "code", "rule": "window_tag", "reason": why,
                                         "changed": {"type": "door", "width": o.get("width")}})
                gone.add(o["id"])
                out["windows"].append({"opening": o["id"], "level_id": lid, "reason": why + " (adjusted_by_ai)"})
            elif o["type"] == "opening" and kind == "door" and room.get("room_type") in ("hall", "stair") and \
                    not FLAT_HALL_RE.search(CP._fold(f"{room.get('label_raw') or ''} {room.get('label') or ''}")):
                pair = [t for t in texts or [] if (SIZE_TAG_RE.match(B.fold_ascii(str(t.get("text") or "")).lower())
                                                   or [""])[0][:1] == "k"
                        and math.dist((t["x"], t["y"]), o["center"][:2]) <= float(o.get("width") or 0) / 2.0
                        + TAG_REACH_M]
                widths = sorted(int(SIZE_TAG_RE.match(B.fold_ascii(str(t["text"])).lower()).group(2)) / 100.0
                                for t in pair if SIZE_TAG_RE.match(B.fold_ascii(str(t["text"])).lower()).group(1) == "k")
                double = len(widths) >= 2 and abs(sum(widths[:2]) - float(o.get("width") or 0)) <= 0.2
                why = (f"the doorless gap {o['id']} ({o.get('width')} m) in the outer wall of {room['id']} "
                       f"'{room.get('label')}' carries the door tag(s) {', '.join(t['text'] for t in pair) or text}: "
                       f"the building's {'double ' if double else ''}entrance door (S1-09b)")
                if RG.blocked("entrance_tags", b, {"level_id": lid, "opening": o["id"], "why": why}):
                    continue
                o.update(drawn_type="opening", type="door", operation="double" if double else "swing",
                         operation_source="assumed", height=max(float(o.get("height") or 0.0), th),
                         sill_height=None, door_tags=[t["text"] for t in pair],
                         adjusted_by_ai={"by": "code", "rule": "door_tag", "reason": why,
                                         "changed": {"type": "opening"}})
                side = 1 if (sides[0][1] or {}).get("id") == room["id"] else -1
                ent = _entrance_record(b, o, level, lv, room, {"wall_id": o["wall_id"], "side": side}, why)
                ent["drawn"] = True
                site.setdefault("entrances", []).append(ent)
                out["doors"].append({"opening": o["id"], "level_id": lid, "reason": why + " (adjusted_by_ai)"})
    if gone:
        site["entrances"] = [e for e in site.get("entrances") or [] if e.get("door_id") not in gone]
    return out


def lost_behind(lv: dict, e: dict) -> Optional[str]:
    """Why an entrance record is no way in (pure): the far side of its door holds a room label the reading lost (a
    room behind it, not the outside); None otherwise."""
    lost = [p for p in lv.get("reading_places") or [] if p.get("kind") == "unplaced_label" and p.get("at")]
    face, out_ = e.get("face") or e.get("centre"), e.get("outward") or [0.0, 0.0]
    if not face or not lost:
        return None
    q = (face[0] + out_[0] * 0.6, face[1] + out_[1] * 0.6)
    near = [p for p in lost if math.dist(q, p["at"][:2]) <= LABEL_REACH_M + 1.0]
    if not near:
        return None
    return (f"the far side of {e.get('door_id')} holds the room label '{near[0].get('text')}' the reading lost: a room "
            f"behind it, not the outside")


def _leads_to_core(b: dict, e: dict, core: set) -> bool:
    """An entrance into the core, or into a wind lobby, an entrance hall or a corridor that reaches the core through
    rooms that are not a flat's (review S1-03b: real03's drawn door into its Rüzgarlık; pure)."""
    rid = e.get("room_id")
    if not rid or not core:
        return False
    if rid in core:
        return True
    level = CP.Level(b, e.get("level_id"))
    r = next((x for x in level.rooms if x["id"] == rid), None)
    if r is not None and ENTRANCE_ROOM_RE.search(_label(r)) and not FLAT_HALL_RE.search(_label(r)):
        return True             # a wind lobby or an entrance hall: the building's way in (real03's Rüzgarlık)
    rooms = {r["id"]: r for r in level.rooms}

    def common_way(r: dict) -> bool:
        return r.get("room_type") not in PRIVATE and not FLAT_HALL_RE.search(_label(r)) and not CP.is_lift(r)
    if rid not in rooms or not common_way(rooms[rid]):
        return False
    adj: dict = {}
    for a, c, _o in _links(level):
        adj.setdefault(a, set()).add(c)
        adj.setdefault(c, set()).add(a)
    seen, todo = {rid}, [rid]
    while todo:
        for y in adj.get(todo.pop(), ()):
            if y in core:
                return True
            if y not in seen and y in rooms and common_way(rooms[y]):
                seen.add(y)
                todo.append(y)
    return False


def reapply_entrances(b: dict, old: list) -> None:
    """The completion's entrance decisions after the levels model rebuilt ``site.entrances`` (13 Nov 2026, review
    CODE-01: an accepted agent level edit re-runs ``wenart.levels.model.infer_levels``, which brought back refused
    doors with steps and picked a new main entrance; the same merge as the levels model's records, CS1-04). Once the
    completion has run (``level_inference.core_rules.entrances``): a door it refused (``entrance_refused``) has no
    record, the records it inferred (rule ``inferred_entrance``) stay as written, and the main entrance is the one it
    left in ``old`` (the records before the rebuild), or none when it left none. Mutates ``b``."""
    import copy

    if not isinstance(((b.get("level_inference") or {}).get("core_rules") or {}).get("entrances"), dict):
        return                                    # the reading's own first run: the completion has not decided yet
    site = b.get("site")
    if not isinstance(site, dict):
        return
    doors = {o["id"]: o for o in b.get("openings") or [] if o.get("type") == "door"}
    ents = [e for e in site.get("entrances") or [] if e.get("door_id") in doors
            and not doors[e["door_id"]].get("entrance_refused")]
    have = {e.get("door_id") for e in ents}
    for e in old or []:
        if any((ev or {}).get("rule") == "inferred_entrance" for ev in e.get("evidence") or []) and \
                e.get("door_id") in doors and e.get("door_id") not in have:
            ents.append(copy.deepcopy(e))
            have.add(e.get("door_id"))
    main = next((e for e in old or [] if e.get("main") and e.get("door_id") in have), None)
    for e in ents:
        if main is not None and e.get("door_id") == main.get("door_id"):
            e["main"], e["main_reason"] = True, main.get("main_reason") or e.get("main_reason")
        elif e.get("main"):
            e["main"] = False
            e.pop("main_reason", None)
    site["entrances"] = ents


def fix_entrances(b: dict, next_id, party_by_level: dict, texts_by_level: Optional[dict] = None) -> dict:
    """Rule 4 (the module docstring); returns ``{"refused", "added", "main", "open"}`` (R09 brought forward, 13 Nov
    2026): one main entrance, never into a bedroom, a wet room or a kitchen (nor a flat's room in a building with a
    common core); an entrance into the core on any storey answers the building's entrance; an inferred one only on an
    entrance storey (``entrance_storeys``), into its core hall on a facade that is no party wall, with its
    ``site.entrances`` record; no core read: no question (a core-reading finding)."""
    rec = {"refused": [], "added": [], "main": None, "open": None}
    site = b.get("site") if isinstance(b.get("site"), dict) else {}
    rooms = {r["id"]: r for r in b.get("rooms") or []}
    flats = several_flats(b)
    common = common_core(b)
    levels = {lv["id"]: lv for lv in b.get("levels") or []}
    keep = []
    for e in site.get("entrances") or []:
        why = lost_behind(levels.get(e.get("level_id")) or {}, e)
        room = rooms.get(e.get("room_id")) or {}
        if why is None and (flats or common) and room.get("room_type") in WET:
            # a garden or terrace door of a ground-floor flat stays an outer door; a bathroom is never a way in
            why = (f"{e.get('door_id')} opens from {room.get('id')} '{room.get('label')}' ({room.get('room_type')}): a "
                   f"wet room is never a way into the building")
        if why and RG.blocked("entrance_refuse", b, {"level_id": e.get("level_id"), "opening": e.get("door_id"),
                                                    "room": e.get("room_id"), "why": why}):
            why = None
        if why:
            rec["refused"].append({"door": e.get("door_id"), "level_id": e.get("level_id"),
                                   "reason": why + " (adjusted_by_ai: no entrance, no steps)"})
            for o in b.get("openings") or []:
                if o["id"] == e.get("door_id"):
                    o["entrance_refused"] = why
            continue
        keep.append(e)
    if rec["refused"]:
        site["entrances"] = keep
    # R37 and the drawn entrance (S1-09b): an outer 'door' tagged as a window is a window; a doorless outer gap tagged
    # as a door into a hall or stair room is that door, a way in
    tags = size_tags(b, texts_by_level)
    rec["windows"], rec["tagged"] = tags["windows"], tags["doors"]
    keep = site.get("entrances") or []
    cores = {}

    def core_of(lid):
        if lid not in cores:
            cores[lid] = core_rooms(b, CP.Level(b, lid)) if lid in levels else set()
        return cores[lid]
    # one main entrance, never into a bedroom, a wet room or a kitchen (nor a flat's room with a common core)
    usable = [e for e in keep if not e.get("into_air") and not e.get("below_ground") and not e.get("upper_floor")]

    def bad(e):
        r = rooms.get(e.get("room_id")) or {}
        return r.get("room_type") in NOT_MAIN_TYPES or (common is not None and r.get("room_type") in PRIVATE
                                                        and r.get("id") not in core_of(e.get("level_id")))
    main = next((e for e in keep if e.get("main")), None)
    if main is None and (rec["windows"] or rec["tagged"]):
        # the main entrance was a window (R37) or a drawn entrance was found: the best way in is the main one
        best = sorted((e for e in usable if not bad(e)),
                      key=lambda e: (not _leads_to_core(b, e, core_of(e.get("level_id"))),
                                     (rooms.get(e.get("room_id")) or {}).get("room_type") not in ("hall", "stair"),
                                     float(e.get("rise") or 0.0), str(e.get("door_id"))))
        if best:
            best[0]["main"] = True
            best[0]["main_reason"] = (f"the main entrance: {best[0].get('door_id')} into "
                                      f"{best[0].get('room_id')} (the outer doors tagged as windows are no way in; "
                                      f"adjusted_by_ai)")
            rec["main"] = {"was": None, "now": best[0].get("door_id"), "reason": best[0]["main_reason"]}
    if main is not None and bad(main) and not RG.blocked("entrance_refuse", b, {"level_id": main.get("level_id"),
                                                                                "opening": main.get("door_id"),
                                                                                "why": "main into a flat's room"}):
        r = rooms.get(main.get("room_id")) or {}
        main["main"] = False
        better = sorted((e for e in usable if not bad(e)),
                        key=lambda e: (e.get("room_id") not in core_of(e.get("level_id")),
                                       (rooms.get(e.get("room_id")) or {}).get("room_type") not in ("hall", "stair"),
                                       float(e.get("rise") or 0.0), str(e.get("door_id"))))
        why = (f"{main.get('door_id')} opens into {r.get('id')} '{r.get('label')}' ({r.get('room_type')}): a main "
               f"entrance never opens into a bedroom, a wet room or a kitchen" +
               (" (nor a flat's room in a building with a common core)" if common is not None else ""))
        if better:
            better[0]["main"] = True
            better[0]["main_reason"] = why + f"; {better[0].get('door_id')} is the main entrance instead (inferred)"
        rec["main"] = {"was": main.get("door_id"), "now": better[0].get("door_id") if better else None,
                       "reason": why + (f": {better[0].get('door_id')} instead" if better else ": no other door")
                       + " (adjusted_by_ai)"}
        if not better:
            rec["open"] = (why + ", and no other outer door leads into a hall or the core: which door is the main "
                                 "entrance? (open point)")
    if common is None:
        return rec
    # an entrance into the core on any storey answers the building's entrance (real10: the main door on the 1st
    # basement at the street's level)
    if any(_leads_to_core(b, e, core_of(e.get("level_id"))) for e in usable):
        return rec
    if any(o.get("inference", {}).get("rule") == "inferred_entrance" for o in b.get("openings") or []):
        return rec
    cands = [(lv, why, True) for lv, why in entrance_storeys(b, texts_by_level)]
    if not cands:
        # no storey lies at the ground: the ground floor is asked about, never given a door metres over the ground
        ground = next((lv for lv in _storeys(b) if (lv.get("order") or 0) == 0), None)
        cands = [(ground, "the ground floor, over the ground the reading knows", False)] if ground is not None else []
    any_core = False
    for lv, why_storey, may_add in cands:
        level = CP.Level(b, lv["id"])
        core = core_of(lv["id"])
        if not core or level.outline is None:
            continue
        any_core = True
        if not may_add:
            continue
        party = party_by_level.get(lv["id"]) or {}
        halls = [rooms[i] for i in core if rooms.get(i, {}).get("room_type") in ("hall", "stair")]
        best = None
        for hall in halls:
            for f in level.faces(hall):
                if f["kind"] != "outside" or f["wall_id"] in party or \
                        isinstance(level.walls[f["wall_id"]].get("party_wall"), dict):
                    continue
                for p0, p1 in level.free(f):
                    if p1 - p0 >= ENTRANCE_DOOR_M[0] and (best is None or p1 - p0 > best[3] - best[2]):
                        best = (hall, f, p0, p1)
        if best is None:
            continue
        if RG.blocked("entrance_add", b, {"level_id": lv["id"], "room": best[0]["id"], "wall": best[1]["wall_id"]}):
            return rec
        hall, f, p0, p1 = best
        reason = (f"the building entrance: the common hall {hall['id']} '{hall.get('label')}' on {lv['id']} ({why_storey}) "
                  f"reaches the facade on {f['wall_id']}; no entrance into the core is drawn or read")
        o = CP._new_opening("door", next_id("door", lv["id"]), level, f["wall_id"], (p0 + p1) / 2.0,
                            ENTRANCE_DOOR_M[0], ENTRANCE_DOOR_M[1], None, reason, hall, f, CP._ev_file(b, lv["id"]),
                            lv.get("region_id"), "default entrance door")
        o["inference"]["rule"] = "inferred_entrance"
        b["openings"].append(o)
        ent = _entrance_record(b, o, level, lv, hall, f, reason)
        if not any(e.get("main") for e in site.get("entrances") or []):
            ent["main"], ent["main_reason"] = True, "the only entrance into the common core (inferred)"
            rec["open"] = None
        if isinstance(b.get("site"), dict):
            b["site"].setdefault("entrances", []).append(ent)
        rec["added"].append({"door": o["id"], "level_id": lv["id"], "reason": reason + " (inferred)"})
        return rec
    if any_core:
        names = ", ".join(f"{lv['id']}" for lv, _w, _a in cands) or "-"
        rec["open"] = (f"the common core reaches no free facade on the entrance storey(s) ({names}): the passage from "
                       f"the street to the core is not drawn (open point: a corridor through the street-side flat is a "
                       f"design decision)")
    return rec



def apply(build, texts_by_level: dict, party_by_level: dict, strokes_by_level: Optional[dict] = None,
          drawn_by_level: Optional[dict] = None) -> dict:
    """The four rules in order (the module docstring); the record for ``level_inference.core_rules``."""
    b = build.building
    stairs, open_ = infer_stairs(b, build.ids.next, texts_by_level, strokes_by_level, drawn_by_level)
    rec = {"stairs": stairs, "stairs_open": open_}
    # the common core is a building of several flats' with a common core (a house's, or a house pair's, own stair hall
    # or lift opens where its plan says); the lift-door marks in no lift's shaft are undone in every building
    flats = flat_core(b)
    rec["lift_doors"] = fix_lift_doors(b, build.ids.next, flats)
    gaps = close_core_gaps(b, drawn_by_level, texts_by_level) if flats else {"closed": [], "windows": [], "review": []}
    rec["core_gaps"], rec["core_gap_windows"], rec["core_gap_review"] = gaps["closed"], gaps["windows"], gaps["review"]
    rec["entrances"] = fix_entrances(b, build.ids.next, party_by_level, texts_by_level)
    if open_:
        b.setdefault("needs_review", []).append(
            {"id": "stair:" + ",".join(x["level_id"] for x in open_), "kind": "stair_not_drawn",
             "reason": open_[0]["reason"] + (f" (also on {', '.join(x['level_id'] for x in open_[1:])})"
                                             if len(open_) > 1 else ""),
             "crop": None, "room_id": None, "level_id": open_[0]["level_id"]})
    if rec["entrances"]["open"]:
        b.setdefault("needs_review", []).append(
            {"id": "entrance:building", "kind": "entrance_not_drawn", "reason": rec["entrances"]["open"], "crop": None,
             "room_id": None, "level_id": None})
    for x in gaps["review"]:
        b.setdefault("needs_review", []).append(
            {"id": f"core_gap:{x['opening']}", "kind": "core_gap", "reason": x["reason"], "crop": None,
             "room_id": x.get("room"), "level_id": x["level_id"]})
    for s in rec["stairs"]:
        build.warn(f"stair: {s['reason']}")
    for s in open_:
        build.warn(f"stair: {s['reason']}")
    lift = rec["lift_doors"]
    for x in (lift["unmarked"] + lift["merged"] + lift["removed"] + lift["review"] + lift["retyped"] + lift["added"]
              + gaps["closed"] + gaps["windows"] + gaps["review"]):
        build.warn(f"core: {x['reason']}")
    for x in rec["entrances"]["refused"] + rec["entrances"]["added"] + rec["entrances"].get("windows", []) + \
            rec["entrances"].get("tagged", []):
        build.warn(f"entrance: {x['reason']}")
    if rec["entrances"]["main"]:
        build.warn(f"entrance: {rec['entrances']['main']['reason']}")
    if rec["entrances"]["open"]:
        build.warn(f"entrance: {rec['entrances']['open']}")
    return rec



