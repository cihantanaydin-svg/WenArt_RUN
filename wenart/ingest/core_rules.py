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
   (``from_documents``, typed by this rule, inferred and needs review). With no such box no geometry is made: the
   storey is listed (``stairs_open``) with the box found without strokes, and the building gets a ``needs_review``
   item (G2). Each stair gets its void in the slab above.
2. **Lift landing doors** (``lift_doors``, R19 with its guards; a lift is ``completion.is_lift``: a lift word, no
   machine-room, lobby or car-lift word, at most 8 m2 a car): the pieces of one landing door read in stacked parallel
   walls (``STACK_M`` apart, spans overlapping by half) are merged first, the widest (or the drawn one) kept; then a
   lift's openings onto a flat's room, onto a stair flight (its ``FRONT_ZONE_M`` front zone covering
   ``FRONT_FLIGHT_M2`` of a flight), windows in the shaft and pieces under ``PIECE_MIN_M`` are rejected when the reader
   derived or a rule inferred them (``derived``), and raise a review record when they are drawn symbols (R16 G6, a
   drawn door is never removed); a doorless opening between a lift and the common hall is the lift's landing door: a
   sliding door (the user on real10, C0034: "there should be a door for the elevator like sliding door ... a general
   rule"; ``adjusted_by_ai``, ``drawn_type`` kept); a lift left without an opening onto the common hall gets one
   inferred landing door on the face to the hall, away from a drawn counterweight. A pit level (KUYU, BOŞLUK) gets no
   landing door. Only in a building of several flats (a house's own lift opens where its plan says).
3. **Between a flat and the core** (``core_gaps``, R16 with its guards): an unclassified gap (type ``opening``, a
   derived opening) between the common core (the lifts, the stairs and the halls joined to them by doorless openings)
   and a flat's bathroom, WC, shower or bedroom is closed; one to a kitchen, living or dining room is closed only when
   that room still reaches the core without it (it is not the flat's only, open-plan, entrance: G4). Drawn doors are
   never removed (the RC14 check ``core_door`` asks about them). Only in a building of several flats (a house's stair
   hall may be open to its rooms).
4. **Entrances** (``entrances``): an entrance (``site.entrances``) whose far side holds a room label the reading lost
   is no entrance (the room behind it is missing); in a building of several flats an entrance from a wet room is
   refused (a flat's garden or terrace door stays an outer door); a building of several flats without an
   entrance into the core gets an inferred one where the core hall reaches a facade that is no party wall, else an open
   point (the passage from the street to the core is not drawn).

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
# an opening a rule made: a reader-derived gap, or one inferred by a rule (R16 G6)
DERIVED_RULES = ("lift_door", "mirror_twin", "gap_behind_furniture", "inferred_door", "inferred_window",
                 "inferred_entrance", "balcony_door")
LABEL_REACH_M = 1.5             # a lost room label this close beyond an entrance is the room behind it


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
def stair_dict(fp: dict, reason: str) -> dict:
    """A dog-leg (U) stair in the footprint ``fp`` (pure): two flights side by side along its long side, a half
    landing at the far end; the direction and the turn assumed (the shape the stair rule writes)."""
    (cx, cy), (w, d), rot = fp["center"], fp["size"], math.radians(fp["rotation_deg"])
    # the long side along the footprint's own axis
    if d >= w:
        u, n, length, width = (-math.sin(rot), math.cos(rot)), (math.cos(rot), math.sin(rot)), d, w
    else:
        u, n, length, width = (math.cos(rot), math.sin(rot)), (-math.sin(rot), math.cos(rot)), w, d
    fw = width / 2.0
    ld = max(min(fw, 1.4), 1.0)
    lines = max(3, min(10, int((length - ld - 0.3) / TREAD_M)))
    fl = lines * TREAD_M

    def at(s, t):
        return [round(cx + u[0] * s + n[0] * t, 4), round(cy + u[1] * s + n[1] * t, 4)]

    s0 = -length / 2.0 + 0.3
    flights = [{"start": at(s0, -fw / 2.0), "end": at(s0 + fl, -fw / 2.0), "width": round(fw, 3), "lines": lines,
                "spacing": TREAD_M},
               {"start": at(length / 2.0 - ld, fw / 2.0), "end": at(length / 2.0 - ld - fl, fw / 2.0),
                "width": round(fw, 3), "lines": lines, "spacing": TREAD_M}]
    landing = [at(length / 2.0 - ld, -width / 2.0), at(length / 2.0, -width / 2.0), at(length / 2.0, width / 2.0),
               at(length / 2.0 - ld, width / 2.0)]
    return {"flights": flights, "landing": {"polygon": landing, "depth": round(ld, 3)},
            "direction": [round(u[0], 4), round(u[1], 4)], "direction_assumed": True, "turn": "U",
            "turn_assumed": True, "void_assumed": True, "riser_m": None, "riser_source": None, "reason": reason}


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
        if txt.isdigit() and 1 <= int(txt) <= 40:
            nums.add(int(txt))
        elif RISER_TAG_RE.search(CP._fold(txt)):
            return f"the riser tag '{txt}'"
    run = 0
    while run + 1 in nums:
        run += 1
    return f"the tread numbers 1-{run}" if run >= NUMBER_RUN_MIN else None


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


def infer_stairs(b: dict, next_id, texts_by_level: dict, strokes_by_level: Optional[dict] = None) -> tuple:
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
        else:
            cand = (candidate or {}).get("symbol") or {}
            croom = (candidate or {}).get("room") or {}
            reason = (f"no stair is drawn or read on {lid}, and the building needs one to reach {storeys[k + 1]['id']}"
                      + (f"; the box {cand.get('id')} in {croom.get('id') or 'the core'} has no stair strokes (no tread "
                         f"lines, tread numbers or riser tag): is it the stair?" if cand else "")
                      + " (a question: no stair is built without drawn evidence, R08)")
            open_.append({"level_id": lid, "candidate": cand.get("id"), "reason": reason})
            continue
        kind = {"typical copy": "stair_typical_copy", "stroke box": "stair_box"}[mode]
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
                 "stair": stair_dict(fp, reason),
                 "evidence": (list(evidence)[:1] + [{"file": CP._ev_file(b, lid), "method": "inferred",
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


def core_rooms(b: dict, level: "CP.Level") -> set:
    """The common core of a storey (pure): its lifts, its stair rooms and the rooms holding a stair, and the halls joined
    to them by doorless openings or virtual separators (a landing in front of the lifts; never a flat's hall behind its
    door)."""
    core = {r["id"] for r in level.rooms if CP.is_lift(r) or r.get("room_type") == "stair"
            or (CP.LIFT_RE.search(CP._fold(r.get("label") or r.get("label_raw")))
                and level.polys[r["id"]].area > CP.LIFT_MAX_M2)}
    below = _storey_below(b, level.lid)
    for f in b.get("furniture") or []:
        # the room holding a stair, and the room a stair of the storey below arrives in
        if f.get("level_id") in (level.lid, below) and f.get("type") == "stair" and f.get("footprint"):
            r = level.room_at(tuple(f["footprint"]["center"]))
            if r is not None and (f.get("level_id") == level.lid or r.get("room_type") == "hall"):
                core.add(r["id"])
    # a lift's lobby: the hall the lift touches along the longest stretch
    for lift in [r for r in level.rooms if CP.is_lift(r)]:
        lp = level.polys[lift["id"]].buffer(0.4)
        touch = [(lp.intersection(level.polys[r["id"]].exterior.buffer(0.05)).area, r) for r in level.rooms
                 if r.get("room_type") == "hall" and r["id"] != lift["id"]]
        touch = [t for t in touch if t[0] > 0.05]
        if touch:
            core.add(max(touch, key=lambda t: t[0])[1]["id"])
    rooms = {r["id"]: r for r in level.rooms}
    links = []
    for o in level.openings:
        if o.get("type") != "opening" and not o.get("virtual"):
            continue
        if o.get("virtual"):
            line = o.get("line") or []
            if len(line) != 2:
                continue
            mid = ((line[0][0] + line[1][0]) / 2.0, (line[0][1] + line[1][1]) / 2.0)
            near = [r["id"] for r in level.rooms if level.polys[r["id"]].distance(Point(mid)) <= 0.15]
        else:
            near = [s[1]["id"] for s in _sides(level, o) if s[1] is not None]
        if len(near) == 2:
            links.append(tuple(near))
    grew = True
    while grew:
        grew = False
        for a, c in links:
            for x, y in ((a, c), (c, a)):
                if x in core and y not in core and rooms.get(y, {}).get("room_type") == "hall":
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


def _stacked(level: "CP.Level", pieces: list) -> list:
    """``[(kept, [others])]`` (pure): openings in stacked parallel walls (centres at most ``STACK_M`` apart across the
    walls, spans overlapping by at least half the shorter): one door read in pieces. The drawn one is kept, else the
    widest."""
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
            kept = next((x for x in grp if not derived(x)), None) or max(grp, key=lambda x: float(x.get("width") or 0))
            used |= {x["id"] for x in grp}
            out.append((kept, [x for x in grp if x is not kept]))
    return out


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


def fix_lift_doors(b: dict, next_id) -> dict:
    """Rule 2 (the module docstring); returns ``{"merged", "removed", "review", "retyped", "added"}``."""
    rec = {"unmarked": [], "merged": [], "removed": [], "review": [], "retyped": [], "added": []}
    for lv in b.get("levels") or []:
        lid = lv["id"]
        level = CP.Level(b, lid)
        lifts = [r for r in level.rooms if CP.is_lift(r)]
        if not lifts or level.outline is None:
            continue
        # 0. a lift-door mark on an opening that is not in a lift's shaft wall is undone (R19: a landing door lies on
        # the shaft edge; R16: an opening marked lift_door outside the shaft wall is wrong): a derived gap is an
        # opening again, a drawn door keeps its type
        for o in level.openings:
            if not o.get("lift_door") or o.get("virtual") or _lift_of(level, o, lifts)[0] is not None:
                continue
            if RG.blocked("lift_door_unmark", b, {"level_id": lid, "opening": o["id"]}):
                continue
            first = (o.get("evidence") or [{}])[0] or {}
            reason = (f"{o['id']} is marked a lift's landing door but lies in no lift's shaft wall: the mark is undone"
                      + (" (a derived gap again)" if first.get("method") == "derived" else ""))
            o["lift_door"] = False
            if first.get("method") == "derived":
                o.update(type="opening", operation=None, operation_source=None)
            o["adjusted_by_ai"] = {"by": "code", "rule": "lift_door_unmark", "reason": reason}
            rec["unmarked"].append({"opening": o["id"], "level_id": lid, "reason": reason + " (adjusted_by_ai)"})
        core = core_rooms(b, level)
        stairs = [_rect(f["footprint"]) for f in b.get("furniture") or []
                  if f.get("level_id") == lid and f.get("type") == "stair" and f.get("footprint")
                  and f.get("build") is not False]
        drop = set()
        # 1. one landing door read in pieces in stacked parallel walls: merged first (R19)
        for lift in lifts:
            pieces = [o for o in level.openings if o.get("type") in ("door", "opening") and not o.get("virtual")
                      and _lift_of(level, o, lifts)[0] is lift]
            for kept, others in _stacked(level, pieces):
                for o in others:
                    why = (f"{o['id']} ({float(o.get('width') or 0):.2f} m) is a piece of the landing door {kept['id']} "
                           f"of the lift {lift['id']}, read in a stacked wall")
                    if derived(o) and not RG.blocked("lift_door_merge", b, {"level_id": lid, "opening": o["id"],
                                                                          "kept": kept["id"], "lift": lift["id"]}):
                        drop.add(o["id"])
                        rec["merged"].append({"opening": o["id"], "kept": kept["id"], "level_id": lid,
                                              "reason": why + " (adjusted_by_ai: merged)"})
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
            served = False
            for o in level.openings:
                sides = _sides(level, o) if o.get("type") in ("door", "opening") else []
                ids = [x[1]["id"] if x[1] is not None else None for x in sides]
                if lift["id"] in ids:
                    other = sides[1 - ids.index(lift["id"])][1]
                    if other is not None and (other["id"] in core or other.get("room_type") == "hall"):
                        served = True
                        break
            if served:
                continue
            faces = [f for f in _hall_faces(level, lift, core)]
            if not faces:
                continue
            # the landing door faces away from the counterweight when the drawing shows one (a narrow piece in the
            # shaft beside the car), else the longest stretch onto the hall
            cw = _counterweight(b, level, lift)
            lc = level.polys[lift["id"]].centroid

            def score(x, cw=cw, lc=lc):
                f, p0, p1 = x
                mid = level.at(f["wall_id"], (p0 + p1) / 2.0)
                if cw is None:
                    return (False, p1 - p0)
                v1, v2 = (mid[0] - lc.x, mid[1] - lc.y), (cw[0] - lc.x, cw[1] - lc.y)
                n1, n2 = math.hypot(*v1), math.hypot(*v2)
                cos = (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2) if n1 > 1e-9 and n2 > 1e-9 else 0.0
                return (cos < -0.5, p1 - p0)            # clearly on the far side from the counterweight

            f, p0, p1 = max(faces, key=score)
            width = min(LIFT_DOOR_M[0], p1 - p0)
            if width < LIFT_DOOR_MIN_M or RG.blocked("lift_door_add", b, {"level_id": lid, "lift": lift["id"],
                                                                           "wall": f["wall_id"], "room": f["hall"]}):
                continue
            reason = (f"the lift {lift['id']} has no landing door onto the common hall: one inferred on {f['wall_id']} "
                      f"facing {f['hall']}")
            o = CP._new_opening("door", next_id("door", lid), level, f["wall_id"], (p0 + p1) / 2.0, width,
                                LIFT_DOOR_M[1], None, reason, lift, {"kind": "hall"}, CP._ev_file(b, lid),
                                lv.get("region_id"), "default lift door")
            o["operation"], o["lift_door"] = "sliding", True
            o["inference"]["rule"] = "lift_door"
            b["openings"].append(o)
            level.openings.append(o)
            rec["added"].append({"opening": o["id"], "level_id": lid, "reason": reason + " (inferred)"})
    return rec


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


def _hall_faces(level: "CP.Level", lift: dict, core: set) -> list:
    """``[(face, t0, t1)]``: the stretches of the lift's walls with a common hall on the other side, free of openings."""
    p = level.polys[lift["id"]]
    x0, y0, x1, y1 = p.bounds
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
                if other is not None and other["id"] != lift["id"] and (other["id"] in core and not CP.is_lift(other)):
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


def _reaches(level: "CP.Level", start: set, target: str, skip: str) -> bool:
    """True when room ``target`` is reached from the rooms ``start`` through the level's doors and openings without the
    opening ``skip`` (pure)."""
    links: dict = {}
    for o in level.openings:
        if o["id"] == skip or o.get("type") not in ("door", "opening"):
            continue
        near = [x[1]["id"] for x in _sides(level, o) if x[1] is not None] if not o.get("virtual") else []
        if len(near) == 2:
            links.setdefault(near[0], set()).add(near[1])
            links.setdefault(near[1], set()).add(near[0])
    seen, todo = set(start), list(start)
    while todo:
        for y in links.get(todo.pop(), ()):
            if y not in seen:
                seen.add(y)
                todo.append(y)
    return target in seen


def close_core_gaps(b: dict) -> list:
    """Rule 3 (the module docstring); returns the records of the closed gaps."""
    out = []
    for lv in b.get("levels") or []:
        level = CP.Level(b, lv["id"])
        core = core_rooms(b, level)
        if not core:
            continue
        drop = []
        for o in level.openings:
            if o.get("type") != "opening" or o.get("virtual"):
                continue
            rooms = [x[1] for x in _sides(level, o) if x[1] is not None]
            if len(rooms) != 2:
                continue
            a, c = rooms
            if (a["id"] in core) == (c["id"] in core):
                continue
            flat = c if a["id"] in core else a
            rtype = flat.get("room_type")
            if rtype in WET + ("bedroom",):
                why = "a bathroom, WC, shower or bedroom never opens onto the common core"
            elif rtype in PRIVATE and _reaches(level, core, flat["id"], o["id"]):
                why = "the room reaches the core through its flat's entrance as well: this gap is a second link"
            else:
                continue                        # a kitchen or living room's only link: an open-plan flat's entrance
            if RG.blocked("core_gap", b, {"level_id": lv["id"], "opening": o["id"], "room": flat["id"],
                                          "core_room": (a if flat is c else c)["id"]}):
                continue
            drop.append(o["id"])
            out.append({"opening": o["id"], "level_id": lv["id"],
                        "reason": f"the unclassified gap {o['id']} ({float(o.get('width') or 0):.2f} m) joins "
                                  f"{flat['id']} '{flat.get('label')}' ({rtype}) to the common core: {why}; a flat "
                                  f"meets the core only through its entrance door (adjusted_by_ai: closed)"})
        if drop:
            b["openings"] = [o for o in b["openings"] if o["id"] not in drop]
    return out


# --------------------------------------------------------------------------------------------------- 4. entrances
def fix_entrances(b: dict, next_id, party_by_level: dict) -> dict:
    """Rule 4 (the module docstring); returns ``{"refused": [...], "added": [...], "open": ...}``."""
    rec = {"refused": [], "added": [], "open": None}
    site = b.get("site") or {}
    rooms = {r["id"]: r for r in b.get("rooms") or []}
    flats = several_flats(b)
    levels = {lv["id"]: lv for lv in b.get("levels") or []}
    keep = []
    for e in site.get("entrances") or []:
        why = None
        lv = levels.get(e.get("level_id")) or {}
        lost = [p for p in lv.get("reading_places") or [] if p.get("kind") == "unplaced_label" and p.get("at")]
        face, out_ = e.get("face") or e.get("centre"), e.get("outward") or [0.0, 0.0]
        if face and lost:
            q = (face[0] + out_[0] * 0.6, face[1] + out_[1] * 0.6)
            near = [p for p in lost if math.dist(q, p["at"][:2]) <= LABEL_REACH_M + 1.0]
            if near:
                why = (f"the far side of {e.get('door_id')} holds the room label '{near[0].get('text')}' the reading "
                       f"lost: a room behind it, not the outside")
        room = rooms.get(e.get("room_id")) or {}
        if why is None and flats and room.get("room_type") in WET:
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
    if not flats or common_core(b) is None:
        return rec
    storeys = _storeys(b)
    ground = next((lv for lv in storeys if (lv.get("order") or 0) == 0), None)
    if ground is None:
        return rec
    level = CP.Level(b, ground["id"])
    core = core_rooms(b, level)
    if any(e.get("level_id") == ground["id"] and (e.get("room_id") in core) for e in keep):
        return rec
    if any(o.get("inference", {}).get("rule") == "inferred_entrance" for o in b.get("openings") or []):
        return rec
    party = party_by_level.get(ground["id"]) or {}
    halls = [rooms[i] for i in core if rooms.get(i, {}).get("room_type") in ("hall", "stair")]
    best = None
    for hall in halls:
        for f in level.faces(hall):
            if f["kind"] != "outside" or f["wall_id"] in party:
                continue
            for p0, p1 in level.free(f):
                if p1 - p0 >= ENTRANCE_DOOR_M[0] and (best is None or p1 - p0 > best[3] - best[2]):
                    best = (hall, f, p0, p1)
    if best is not None and RG.blocked("entrance_add", b, {"level_id": ground["id"], "room": best[0]["id"],
                                                           "wall": best[1]["wall_id"]}):
        return rec
    if best is not None:
        hall, f, p0, p1 = best
        reason = (f"the building entrance: the common hall {hall['id']} '{hall.get('label')}' reaches the facade on "
                  f"{f['wall_id']}; no entrance into the core is drawn or read")
        o = CP._new_opening("door", next_id("door", ground["id"]), level, f["wall_id"], (p0 + p1) / 2.0,
                            ENTRANCE_DOOR_M[0], ENTRANCE_DOOR_M[1], None, reason, hall, f, CP._ev_file(b, ground["id"]),
                            ground.get("region_id"), "default entrance door")
        o["inference"]["rule"] = "inferred_entrance"
        b["openings"].append(o)
        rec["added"].append({"door": o["id"], "level_id": ground["id"], "reason": reason + " (inferred)"})
    else:
        names = ", ".join(sorted(core)) or "no core read"
        rec["open"] = (f"the common core ({names}) reaches no facade of {ground['id']}: the passage from the street to "
                       f"the core is not drawn (open point: a corridor through the street-side flat is a design "
                       f"decision)")
    return rec


def apply(build, texts_by_level: dict, party_by_level: dict, strokes_by_level: Optional[dict] = None) -> dict:
    """The four rules in order (the module docstring); the record for ``level_inference.core_rules``."""
    b = build.building
    stairs, open_ = infer_stairs(b, build.ids.next, texts_by_level, strokes_by_level)
    rec = {"stairs": stairs, "stairs_open": open_}
    # the common core is a building of several flats' with a common core (a house's, or a house pair's, own stair hall
    # or lift opens where its plan says)
    flats = flat_core(b)
    rec["lift_doors"] = fix_lift_doors(b, build.ids.next) if flats else \
        {"unmarked": [], "merged": [], "removed": [], "review": [], "retyped": [], "added": []}
    rec["core_gaps"] = close_core_gaps(b) if flats else []
    rec["entrances"] = fix_entrances(b, build.ids.next, party_by_level)
    if open_:
        b.setdefault("needs_review", []).append(
            {"id": "stair:" + ",".join(x["level_id"] for x in open_), "kind": "stair_not_drawn",
             "reason": open_[0]["reason"] + (f" (also on {', '.join(x['level_id'] for x in open_[1:])})"
                                             if len(open_) > 1 else ""),
             "crop": None, "room_id": None, "level_id": open_[0]["level_id"]})
    for s in rec["stairs"]:
        build.warn(f"stair: {s['reason']}")
    for s in open_:
        build.warn(f"stair: {s['reason']}")
    lift = rec["lift_doors"]
    for x in (lift["unmarked"] + lift["merged"] + lift["removed"] + lift["review"] + lift["retyped"] + lift["added"]
              + rec["core_gaps"]):
        build.warn(f"core: {x['reason']}")
    for x in rec["entrances"]["refused"] + rec["entrances"]["added"]:
        build.warn(f"entrance: {x['reason']}")
    if rec["entrances"]["open"]:
        build.warn(f"entrance: {rec['entrances']['open']}")
    return rec


