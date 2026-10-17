"""Type inference for drawn pieces the documents leave unclear (docs/milestone11.md §6, CLAUDE.md furniture rules,
contract §17.2): an unknown footprint that holds other pieces is a rug or a group outline; one that matches a
type's size table, room and position rule gets that type, marked ``inferred``. Pure; owner: track B.

What: ``infer_types(building) -> [proposal]`` looks at every built drawn piece of type ``unknown``;
``apply_inferences(building, proposals) -> building`` returns a copy with them applied. A proposal is
``{"piece_id", "type", "reason", "confidence", "evidence": {...}, "front_deg"?: float, "build"?: false}``.

Why: CLAUDE.md (9 Oct 2026): "Footprint clear but type unclear -> the AI infers the type from size, room and
neighbours, marks it inferred and lists it in the report. It never stays an unexplained box." real02 had 56 built
unknown boxes (U17): rug and zone outlines read as one 13 m² piece (U9), pieces the two AI passes disagreed on.

How (deterministic; the agent may confirm or change the type later on the plan crop):

1. **Outline**: an unknown footprint whose polygon holds the centre of at least one other piece of its room is a rug
   or zone outline drawn around a group. The furniture schema has no rug type, so it is not built (``build:
   false``, proposal type ``rug``); the decor rules lay rugs under the groups (``decor.rugs_for_room``).
1b. **Detail**: an unknown footprint drawn >= 60 % inside a larger typed piece (a sink bowl in a counter leg) is a
   detail of that piece: not built (proposal type ``detail``).
2. **One type**: the types the footprint can be are those whose product size range fits it (size table, +15 %,
   either way), that the room type allows (``schemas.allowed_types``, plus stand-alone lamps, plants and side
   tables) and whose position rule holds (``schemas.ORIENTATION_RULES``: a back-to-wall type has a side on a wall;
   a free piece has a side on a wall or a group partner near). Exactly one -> that type (confidence 0.6).
1c. **Mark** (real03): an unknown footprint that fits no type and is smaller than ``MARK_SIDE_M`` both ways or
   thinner than ``MARK_THIN_M`` is a drawn mark (a tap, a valve, a threshold line): not built (type ``detail``).
3. **One named**: several fit, but exactly one of them was named by an AI pass (``type_candidates``) -> that type
   (confidence 0.55).
4. The front of an inferred type with a front: the side opposite the only side on a wall; a seat faces its nearest
   partner; else none (the builder's side, listed as assumed).

Nothing else is guessed: an unknown piece with no single answer stays unknown and is listed.

Milestone 13 (docs/milestone13.md §1.4, §3.0 K3, §5.2, §13.2; track T3; CLAUDE.md "an untyped drawn footprint is
typed by code first"): **code-first typing**, ``type_by_code(building, piece) -> {"type", "method": twin | level |
block | group_member, "evidence", "confidence"} | None``, runs before any AI typing (step 0 of ``infer_types``, so
the ingest's inference step and the completion get it; ``code_types`` applies it in rounds so a twin of a piece typed
by another level is typed too):

0a. **twin**: the same footprint (sizes within ``SAME_FOOTPRINT_M``, the mirrored centre within ``SAME_CENTRE_M``) in
    the room's twin (``rooms[].twin_of`` / ``twin_transform``, the ingest's mirror; a mirror about the rooms'
    midline when no transform is recorded) carries a type: that type, the mirrored front (``ingest.twins``).
0b. **level**: a typed drawn piece on another level whose footprint lies at the same plan position (polygons within
    ``SAME_FOOTPRINT_M``, mirrored or turned allowed): real04's bathtub f_L-1_056 types the ARC cluster f_L0_043 one
    level up; the front is copied.
0c. **block**: a word of the piece's block name (``evidence[].block``, ``type_raw``; ``groups.yaml`` ``block_words``,
    folded to ASCII: YATAK, masa, klozet, evye ...) names exactly one type whose product range fits the footprint
    (``sizes.fits``, ``BLOCK_SIZE_TOL``) and that the room may hold.
0d. **group_member**: the room's drawn groups miss a member (``groups.group_members``: "shower|bathtub" of a bath
    set, the nightstands of a bed, the chairs of a table, the fridge of a run) or the room kind misses its anchor
    (``program.room_kind``: a bedroom without a bed) and exactly one of those types fits the footprint (the nearest
    product when two alternatives of one role fit): that type.

Every proposal carries ``type_method`` (the method), ``inferred: true`` with the evidence (the source piece or
block, the rule, the confidence: twin / level ``CONF_TWIN``, block ``CONF_BLOCK``, group member ``CONF_GROUP``). The
AI types the rest (the existing path). ``apply_code_types(building, proposal=False)`` applies the proposals and
returns the new building with them; ``proposal=True`` (the completion path, after the locked source was written)
records a ``type_proposal`` with ``drawn_type`` and keeps the footprint and status, as ``locked.check`` requires.

Fix round after P4a (17 Oct 2026; pod P4a, real02). What: a **group member** type (rule 0d) is given only when the
group that misses it really takes the piece in: the piece typed on a copy of the building must lower that type's
count in the room's missing lists (``groups.group_members`` and the unbuilt drawn groups), i.e. it stands within
the role's reach of that group's anchor and no other anchor is nearer (``_adopted``); else code leaves it to the AI
(the plan crop). The room kind's missing anchor ("the bedroom misses its bed") is kept as it was. Why: the rule
ignored where the footprint stands, so every small square of a room was "the only missing member" of the same
group: P4a typed 7 coffee tables in each basement salon (the group named in the reason, seating.2 of the 1.30 m
"sofa" f_L-1_061, never took any of them: they joined the corner sofa's group or none, so the coffee table stayed
missing for every later footprint), 2-3 in each L1 play room. The check is made from the building on every call,
so it holds across the reading's code passes, ``infer_types`` and the completion; two nightstands of one bed or the
chairs of one table are still typed one by one (each lowers the count).

- **Nightstand symbols** (``nightstand_symbols``, run first in ``infer_types``): a drawn ``floor_lamp`` or
  ``side_table`` of a nightstand's size (``plausibility.size_range("nightstand")``) standing at a drawn bed's head
  end, beside the bed (from inside a bed block that holds it up to ``groups.yaml`` ``nightstand_gap`` outside the
  bed's long side), with no nightstand on that side yet, is that bed's nightstand: type ``nightstand``, the bed's
  front, ``inferred`` with the reason and ``adjusted_by_ai`` (``by: code``, ``drawn_type`` and the drawn footprint and
  front kept, the plan crop of the reading's question as evidence when the piece has one). Why: real02's YATAK blocks
  draw a nightstand with a table lamp on each side of the bed; both VLMs read the round lamp and answered
  ``floor_lamp``, the lamps then held the nightstand places and r_L0_e_yatak_odasi and _2 got no nightstand.
"""
from __future__ import annotations

import copy
import math
import re
from typing import Optional

from shapely.geometry import Point

from wenart import geometry as G
from wenart.furniture import groups as GR
from wenart.furniture import placer, plausibility as PL, schemas

# Milestone 13 (T3): code-first typing.
CODE_TYPE_METHODS = ("twin", "level", "block", "group_member")
SAME_FOOTPRINT_M = 0.01          # the same footprint: sizes (and, on another level, the polygon) within 1 cm
SAME_CENTRE_M = 0.02             # a twin's mirrored centre within this (ingest.twins.TOL: the transform is rounded)
CONF_TWIN = 0.8
CONF_BLOCK = 0.7
CONF_GROUP = 0.6
BLOCK_SIZE_TOL = 0.40            # a block-named type must fit the footprint within this (a misread YATAK block is 27 % out)
CODE_ROUNDS = 3                  # chains: a twin of a piece typed by another level

# Fix round after P4a (module docstring): a drawn lamp or side table of a nightstand's size at a bed's head is the
# bed's nightstand (a nightstand with its table lamp drawn from above).
NIGHTSTAND_METHOD = "nightstand_symbol"
NIGHTSTAND_SYMBOL_TYPES = ("floor_lamp", "side_table")
CONF_NIGHTSTAND = 0.7
NIGHTSTAND_SIDE_IN_M = 0.05       # the symbol's outer side reaches at least this close to the bed's side line
RECOGNITION_CROP = "recognition/crops/{key}_ctx.png"     # the reading's plan crop of a question (reading.CROP_DIR)

OUTLINE_TYPE = "rug"              # what an outline holding other pieces is (a decor type, not a furniture type)
WALL_SIDE_M = 0.10                # a side this close to the room outline stands on a wall
CONF_ONE = 0.6
CONF_NAMED = 0.55
CONF_OUTLINE = 0.7
SKIP_TYPES = ("stair", "unknown", "wall_cabinet")


OUTLINE_MIN_M2 = 1.0              # an outline (rug, zone) is at least this large ...
HELD_INSIDE = 0.5                 # ... and holds >= half of each smaller piece it is drawn around


def outline_holds(poly, mates: list[dict]) -> list[str]:
    """Ids of the pieces an outline ``poly`` is drawn around: smaller pieces whose centre lies in it with at least
    ``HELD_INSIDE`` of their area (none when the outline is smaller than ``OUTLINE_MIN_M2``)."""
    if poly.area < OUTLINE_MIN_M2:
        return []
    out = []
    for f in mates:
        try:
            other = placer.drawn_piece(f).polygon()
        except (KeyError, TypeError, ValueError):
            continue
        if other.area >= poly.area or not poly.contains(Point(f["footprint"]["center"])):
            continue
        if other.intersection(poly).area >= HELD_INSIDE * other.area:
            out.append(f["id"])
    return sorted(out)


DETAIL_TYPE = "detail"            # a drawn part inside a typed piece (not a furniture type: not built)
# real03 (10 Oct 2026): a symbol smaller than this both ways (a tap, a valve) or thinner than MARK_THIN_M (a
# threshold, a shelf line) that fits no type is a drawn mark, not a piece: not built (rule 1c).
MARK_SIDE_M = 0.30
MARK_THIN_M = 0.20
DETAIL_INSIDE = 0.6


def _host_of(poly, mates: list[dict]) -> Optional[dict]:
    """The built, typed (larger) piece that holds >= ``DETAIL_INSIDE`` of ``poly`` (real02: the sink bowls inside
    the counter legs, typed bar stools by one AI pass), else None."""
    for f in mates:
        if f.get("type") in ("unknown", "stair") or f.get("build") is False:
            continue
        try:
            other = placer.drawn_piece(f).polygon()
        except (KeyError, TypeError, ValueError):
            continue
        if other.area > poly.area and poly.intersection(other).area >= DETAIL_INSIDE * poly.area:
            return f
    return None


def _rooms(building: dict) -> dict[str, dict]:
    return {r["id"]: r for r in building.get("rooms") or [] if len(r.get("polygon") or []) >= 3}


def _sides(poly) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    c = list(poly.exterior.coords)
    return [(c[i], c[i + 1]) for i in range(len(c) - 1)]


def _wall_sides(piece: placer.Piece, ring) -> list[int]:
    """Indices of the footprint's sides (local order: front, right, back, left) within ``WALL_SIDE_M`` of the room
    outline along most of their length."""
    out = []
    for k, (a, b) in enumerate(_sides(piece.polygon())):
        pts = [((a[0] * (1 - t) + b[0] * t), (a[1] * (1 - t) + b[1] * t)) for t in (0.2, 0.5, 0.8)]
        if all(ring.distance(Point(p)) <= WALL_SIDE_M for p in pts):
            out.append(k)
    return out


def _outward_deg(piece: placer.Piece, side: tuple) -> float:
    mid = ((side[0][0] + side[1][0]) / 2.0, (side[0][1] + side[1][1]) / 2.0)
    return math.degrees(math.atan2(mid[1] - piece.center[1], mid[0] - piece.center[0]))


def _snap_quarter(deg: float, rotation: float) -> float:
    """``deg`` snapped to the nearest of the footprint's four side normals."""
    base = G.front_direction_deg(rotation)
    k = round(G.normalise_angle(deg - base) / 90.0) % 4
    return round(G.normalise_angle(base + 90.0 * k), 3)


def _front_for(ftype: str, piece: placer.Piece, ring, partners: list[placer.Piece]) -> Optional[float]:
    if ftype in schemas.FRONTLESS_TYPES:
        return None
    rule = schemas.orientation_rule(ftype)
    if rule["back"] == "free" and partners:
        host = min(partners, key=lambda h: (round(h.polygon().distance(piece.polygon()), 6), h.index))
        target = host.polygon().centroid
        return _snap_quarter(math.degrees(math.atan2(target.y - piece.center[1], target.x - piece.center[0])),
                             piece.rotation_deg)
    sides = _sides(piece.polygon())
    near = _wall_sides(piece, ring)
    if len(near) == 1:
        return _snap_quarter(_outward_deg(piece, sides[near[0]]) + 180.0, piece.rotation_deg)
    return None


SQUARE_TYPES = ("potted_plant", "side_table", "floor_lamp", "bar_stool", "chair", "office_chair")
PARTNER_ONLY = ("chair", "bar_stool", "office_chair")   # a seat is placed by its table, never by a wall alone
SQUARE_ASPECT = 1.3               # these are about as wide as deep (a 1.03 x 0.69 m outline is no plant)


def _shape_ok(ftype: str, size) -> bool:
    a, b = sorted(float(v) for v in size)
    return ftype not in SQUARE_TYPES or b <= SQUARE_ASPECT * a + 1e-9


def _position_ok(ftype: str, piece: placer.Piece, on_wall: bool, others: list[tuple[str, placer.Piece]]) -> bool:
    rule = schemas.orientation_rule(ftype)
    if rule["back"] in ("wall", "wall_or_group"):
        return on_wall
    if rule["back"] == "free" and rule["partners"]:
        poly = piece.polygon()
        near = any(t in rule["partners"] and o.polygon().distance(poly) <= rule["partner_m"] for t, o in others)
        return near if ftype in PARTNER_ONLY else (on_wall or near)
    return True


def _evidence(item: dict, reason: str, confidence: float) -> dict:
    src = (item.get("evidence") or [{}])[0]
    ev = {"file": src.get("file") or "building.json", "method": "inferred", "confidence": confidence,
          "rule": "furniture.infer", "text": reason}
    for k in ("page", "entity", "region_id"):
        if src.get(k) is not None:
            ev[k] = src[k]
    return ev


# --------------------------------------------------------------------------
# Milestone 13 (T3): code-first typing (twin, level, block name, missing group member)
# --------------------------------------------------------------------------

def untyped_drawn(piece: dict) -> bool:
    """A drawn footprint code may type: ``unknown``, not recorded as something else (a rug outline, a detail, a
    column, not furniture) and either built or left unbuilt only because it is untyped."""
    if piece.get("type") != "unknown" or piece.get("source") != "from_documents" or not piece.get("footprint"):
        return False
    if piece.get("inferred_as") or piece.get("not_furniture"):
        return False
    if piece.get("build") is False and not str(piece.get("not_built_reason") or "").lower().startswith("untyped"):
        return False
    return True


def _typed_drawn(piece: dict) -> bool:
    """A drawn piece whose type code may copy: typed, with a footprint, not a mark and not marked not furniture."""
    return (piece.get("source") == "from_documents" and piece.get("type") not in (None, "unknown", "stair")
            and bool(piece.get("footprint")) and not piece.get("inferred_as") and not piece.get("not_furniture")
            and piece.get("build") is not False)


def _sorted_size(piece: dict) -> tuple[float, float]:
    a, b = sorted(float(v) for v in piece["footprint"]["size"])
    return a, b


def _same_size(a: dict, b: dict, tol: float = SAME_FOOTPRINT_M) -> bool:
    return all(abs(u - v) <= tol + 1e-9 for u, v in zip(_sorted_size(a), _sorted_size(b)))


def _mirror_affine_of(a: dict, b: dict) -> list[float]:
    """A mirror between two twin rooms without a recorded transform: about the vertical or horizontal line between
    their centroids (``ingest.twins.mirror_affine``)."""
    from shapely.geometry import Polygon

    from wenart.ingest import twins as TW

    ca, cb = Polygon(a["polygon"]).centroid, Polygon(b["polygon"]).centroid
    if abs(cb.x - ca.x) >= abs(cb.y - ca.y):
        return TW.mirror_affine(("x", (ca.x + cb.x) / 2.0))
    return TW.mirror_affine(("y", (ca.y + cb.y) / 2.0))


def _twin_rooms(building: dict, room: dict) -> list[tuple[dict, list[float]]]:
    """``(twin room, transform)`` pairs of a room (a mirror is its own inverse, so one transform serves both ways)."""
    rooms = _rooms(building)
    out = []
    first = rooms.get(room.get("twin_of") or "")
    if first is not None:
        t = room.get("twin_transform") or first.get("twin_transform") or _mirror_affine_of(first, room)
        out.append((first, list(t)))
    for r in rooms.values():
        if r.get("twin_of") == room.get("id") and r["id"] != room["id"]:
            t = r.get("twin_transform") or room.get("twin_transform") or _mirror_affine_of(room, r)
            out.append((r, list(t)))
    return out


def _evidence_code(item: dict, method: str, text: str, confidence: float, **extra) -> dict:
    ev = _evidence(item, text, confidence)
    ev["rule"] = f"furniture.infer.type_by_code:{method}"
    ev.update(extra)
    return ev


def _twin_type(building: dict, piece: dict, room: dict) -> Optional[dict]:
    from wenart.ingest import twins as TW

    furniture = building.get("furniture") or []
    for other, t in _twin_rooms(building, room):
        mapped = TW._apply(t, piece["footprint"]["center"])
        for f in furniture:
            if f.get("room_id") != other["id"] or not _typed_drawn(f) or f["id"] == piece["id"]:
                continue
            if G.distance(mapped, tuple(f["footprint"]["center"])) > SAME_CENTRE_M + 1e-9 or not _same_size(piece, f):
                continue
            fp, front = TW._mirror_footprint(f, piece, t)
            text = (f"{f['type']}: the same footprint ({_sorted_size(f)[1]:.2f} x {_sorted_size(f)[0]:.2f} m) as "
                    f"{f['id']} in the twin room {other['id']} (mirrored centre within {SAME_CENTRE_M:.2f} m)")
            return {"type": f["type"], "method": "twin", "confidence": CONF_TWIN, "reason": text,
                    "evidence": _evidence_code(piece, "twin", text, CONF_TWIN, source_id=f["id"], room_id=other["id"]),
                    "front_deg": front, "footprint": fp, "source_status": f.get("status")}
    return None


def _level_type(building: dict, piece: dict, room: Optional[dict]) -> Optional[dict]:
    furniture = building.get("furniture") or []
    rooms = _rooms(building)
    try:
        poly = placer.drawn_piece(piece).polygon()
    except (KeyError, TypeError, ValueError):
        return None
    hits = []
    for f in furniture:
        if f.get("level_id") == piece.get("level_id") or not _typed_drawn(f) or not _same_size(piece, f):
            continue
        if G.distance(tuple(piece["footprint"]["center"]), tuple(f["footprint"]["center"])) > SAME_CENTRE_M + 1e-9:
            continue
        try:
            other = placer.drawn_piece(f).polygon()
        except (KeyError, TypeError, ValueError):
            continue
        if poly.hausdorff_distance(other) > SAME_FOOTPRINT_M + 1e-9:
            continue
        r2 = rooms.get(f.get("room_id") or "")
        same_kind = 0 if room is not None and r2 is not None and r2.get("room_type") == room.get("room_type") else 1
        hits.append((same_kind, f.get("level_id") or "", f["id"], f))
    if not hits:
        return None
    hits.sort(key=lambda h: h[:3])
    f = hits[0][3]
    text = (f"{f['type']}: the same footprint ({_sorted_size(f)[1]:.2f} x {_sorted_size(f)[0]:.2f} m) at the same "
            f"plan position as {f['id']} on level {f.get('level_id')} (within {SAME_FOOTPRINT_M:.2f} m)")
    out = {"type": f["type"], "method": "level", "confidence": CONF_TWIN, "reason": text,
           "evidence": _evidence_code(piece, "level", text, CONF_TWIN, source_id=f["id"], level_id=f.get("level_id")),
           "source_status": f.get("status")}
    if f.get("front_deg") is not None and piece.get("front_deg") is None:
        out["front_deg"] = float(f["front_deg"])
    return out


def _block_names(piece: dict) -> list[str]:
    names = []
    for ev in piece.get("evidence") or []:
        for key in ("block", "block_name"):
            if ev.get(key):
                names.append(str(ev[key]))
    for key in ("type_raw", "block", "block_name"):
        if piece.get(key):
            names.append(str(piece[key]))
    return names


def _block_type(building: dict, piece: dict, room: Optional[dict]) -> Optional[dict]:
    from wenart import building as B
    from wenart.furniture import sizes as SZ

    names = _block_names(piece)
    if not names:
        return None
    words = []
    for name in names:
        words += [w for w in re.split(r"[^a-z0-9]+", B.fold_ascii(name)) if w]
    if not words:
        return None
    text = " " + " ".join(words) + " "
    hits = []
    for ftype, keys in GR.block_words().items():
        for key in keys:
            parts = key.split()
            if (len(parts) > 1 and f" {' '.join(parts)} " in text) or (len(parts) == 1 and any(
                    w.startswith(parts[0]) for w in words)):
                hits.append((ftype, key))
                break
    if not hits:
        return None
    size = [float(v) for v in piece["footprint"]["size"]]
    allowed = None
    if room is not None and not any(t in ("other", "unknown") for t in PL.room_types(building, room)):
        allowed = PL.allowed_in(building, room)
    fits = [(t, k) for t, k in hits if SZ.fits(t, size, BLOCK_SIZE_TOL) and (allowed is None or t in allowed)]
    if len(fits) != 1:
        return None
    ftype, key = fits[0]
    text = (f"{ftype}: the block name '{names[0]}' holds the word '{key}' (groups.yaml block_words) and the type's "
            f"product range fits {size[0]:.2f} x {size[1]:.2f} m within {BLOCK_SIZE_TOL:.0%}")
    return {"type": ftype, "method": "block", "confidence": CONF_BLOCK, "reason": text,
            "evidence": _evidence_code(piece, "block", text, CONF_BLOCK, block=names[0], word=key)}


def _product_distance(ftype: str, size) -> float:
    from wenart.furniture import sizes as SZ

    rng = SZ.real_range(ftype) or {}
    product = rng.get("product")
    if not product:
        return 9.0
    w, d = sorted(float(v) for v in size)
    pw, pd = sorted(float(v) for v in product[:2])
    return max(abs(math.log(max(w, 1e-3) / pw)), abs(math.log(max(d, 1e-3) / pd)))


def _group_wants(building: dict, room: dict) -> dict[str, list[str]]:
    """type -> one line per missing member of that type in the room's groups (``groups.group_members``) and in its
    unbuilt drawn groups (``groups.drawn_groups``, whose built anchor's group is in the first list already)."""
    wanted: dict[str, list[str]] = {}
    for g in GR.group_members(building, room["id"]):
        for miss in g.get("missing") or []:
            for t in str(miss).split("|"):
                wanted.setdefault(t, []).append(f"{g['group_id']} (anchor {g.get('anchor_id')}) misses {miss}")
    by_id = {f["id"]: f for f in building.get("furniture") or []}
    for g in GR.drawn_groups(building, room["id"]):        # drawn groups, built or not (an unbuilt sofa too)
        if g["built"].get(g["anchor_id"]):
            continue                                     # a built anchor's group is in group_members already
        anchor = by_id.get(g["anchor_id"])
        members = [by_id[m] for m in g["members"] if m in by_id]
        for miss in GR._expected_missing(g["template"], anchor, members, room, building):
            for t in str(miss).split("|"):
                wanted.setdefault(t, []).append(f"the drawn {g['template']} group of {g['anchor_id']} misses {miss}")
    return wanted


def _adopted(building: dict, piece: dict, room: dict, ftype: str, before: int) -> bool:
    """Fix round after P4a (module docstring): True when ``piece`` typed ``ftype`` (on a copy) lowers the count of
    ``ftype`` in the room's missing lists below ``before``: a group really takes it in."""
    trial_piece = dict(piece, type=ftype, type_method="group_member")
    if trial_piece.get("build") is False:
        trial_piece["build"] = True                     # untyped and unbuilt: built once typed (_apply_code_type)
        trial_piece.pop("not_built_reason", None)
    trial = dict(building, furniture=[trial_piece if f.get("id") == piece["id"] else f
                                      for f in building.get("furniture") or []])
    return len(_group_wants(trial, room).get(ftype, [])) < before


def _group_member_type(building: dict, piece: dict, room: dict) -> Optional[dict]:
    from wenart.furniture import program as PR
    from wenart.furniture import sizes as SZ

    wanted = _group_wants(building, room)
    by_group = {t: len(v) for t, v in wanted.items()}   # fix round after P4a: the groups' own count per type
    kind = PR.room_kind(building, room)
    present = {f.get("type") for f in building.get("furniture") or [] if f.get("room_id") == room["id"]
               and f.get("type") not in (None, "unknown") and f.get("build") is not False}
    required = {g for g, req, _opts in PR._rows(kind, PR._area(room), placer.room_context(building, room).polygon,
                                                 building, room, room.get("room_subtype")) if req}
    for name, template in GR.load_groups().items():
        # Only the anchor of a group the room kind requires (a bedroom's bed, a living room's sofa): an optional
        # group's anchor (a dining table in a living room) is no evidence for a lone footprint.
        if name not in required or template["layout"] != "anchored":
            continue
        for t in template["anchor"]["types"]:
            if t not in present and not (set(template["anchor"]["types"]) & present):
                wanted.setdefault(t, []).append(f"the {kind} room misses its {name} anchor ({t})")
    if not wanted:
        return None
    size = [float(v) for v in piece["footprint"]["size"]]
    allowed = PL.allowed_in(building, room) | set(schemas.allowed_types(kind, room.get("room_subtype")))
    fits = sorted(t for t in wanted if t in allowed and SZ.fits(t, size, 0.15))
    if not fits:
        return None
    # An AI pass named another type that fits the size and the shape (real02's sofa / kitchen_island): the plan
    # crop decides, not the group rule.
    answers = {c.get("type") for c in piece.get("type_candidates") or [] if c.get("type")}
    if any(a not in fits and a in schemas.SIZE_OPTIONS and SZ.fits(a, size, 0.15) and _shape_ok(a, size)
           for a in answers):
        return None
    if len(fits) > 1:
        ranked = sorted(fits, key=lambda t: (round(_product_distance(t, size), 4), t))
        best, second = ranked[0], ranked[1]
        if _product_distance(second, size) - _product_distance(best, size) < 0.15:
            return None                         # two members fit about equally: the plan crop decides (AI)
        fits = [best]
    ftype = fits[0]
    if by_group.get(ftype) and not _adopted(building, piece, room, ftype, by_group[ftype]):
        # fix round after P4a (module docstring): no group takes this footprint in (too far from the anchor that
        # misses the type, or nearer another one): the plan crop decides (AI), never one more member of that type
        return None
    text = (f"{ftype}: {'; '.join(wanted[ftype][:2])}, and the type's product range fits {size[0]:.2f} x "
            f"{size[1]:.2f} m (the only missing member of that size)")
    return {"type": ftype, "method": "group_member", "confidence": CONF_GROUP, "reason": text,
            "evidence": _evidence_code(piece, "group_member", text, CONF_GROUP, missing=wanted[ftype][:3])}


def type_by_code(building: dict, piece: dict) -> Optional[dict]:
    """Milestone 13 (§13.2): ``{"type", "method": twin | level | block | group_member, "evidence", "confidence",
    "reason", "front_deg"?, "footprint"?}`` for an untyped drawn footprint, or None when code cannot tell (the AI
    types it from the plan crop). The methods are tried in that order (the module docstring)."""
    if not untyped_drawn(piece):
        return None
    room = _rooms(building).get(piece.get("room_id") or "")
    if room is not None:
        found = _twin_type(building, piece, room)
        if found is not None:
            return found
    found = _level_type(building, piece, room)
    if found is not None:
        return found
    # An outline drawn around other pieces (a rug, a zone, a counter run) or a part inside a typed piece is no
    # furniture of its own: rules 1 and 1b of ``infer_types`` decide those, not a block word or a missing member.
    try:
        poly = placer.drawn_piece(piece).polygon()
    except (KeyError, TypeError, ValueError):
        return None
    mates = [f for f in building.get("furniture") or [] if f.get("room_id") == piece.get("room_id")
             and f["id"] != piece["id"]]
    if outline_holds(poly, mates) or _host_of(poly, mates) is not None:
        return None
    found = _block_type(building, piece, room)
    if found is None and room is not None:
        found = _group_member_type(building, piece, room)
    if found is None:
        return None
    if room is not None and piece.get("front_deg") is None and len(room.get("polygon") or []) >= 3:
        # The front as rule 4 gives it: the side opposite the only wall side, or towards the nearest partner.
        others = [(f["type"], placer.drawn_piece(f, k)) for k, f in enumerate(mates)
                  if f.get("type") != "unknown" and f.get("build") is not False and f.get("footprint")]
        partners = [o for t, o in others if t in schemas.orientation_rule(found["type"])["partners"]]
        front = _front_for(found["type"], placer.drawn_piece(piece), _room_ring(room), partners)
        if front is not None:
            found["front_deg"] = front
    return found


def code_types(building: dict) -> list[dict]:
    """Every untyped drawn piece code can type (``type_by_code``), as proposals ``{"piece_id", "type",
    "type_method", "reason", "confidence", "evidence", ...}``; applied in rounds on a working copy so chains resolve
    (a twin of a piece typed by another level). The building is unchanged."""
    work = copy.deepcopy(building)
    out: list[dict] = []
    for _round in range(CODE_ROUNDS):
        found = 0
        for f in work.get("furniture") or []:
            if not untyped_drawn(f):
                continue
            prop = type_by_code(work, f)
            if prop is None:
                continue
            prop = dict(prop, piece_id=f["id"], type_method=prop["method"])
            _apply_code_type(f, prop, proposal=False)     # at once: a missing member is missing only once
            out.append(prop)
            found += 1
        if not found:
            break
    return out


def _apply_code_type(item: dict, prop: dict, proposal: bool) -> None:
    item["type"] = prop["type"]
    item["type_method"] = prop["type_method"]
    item["inferred"] = True
    item["inferred_reason"] = prop["reason"]
    item.setdefault("evidence", []).append(dict(prop["evidence"]))
    if item.get("build") is False and str(item.get("not_built_reason") or "").lower().startswith("untyped"):
        item["build"] = True
        item.pop("not_built_reason", None)
    if item.get("height") is None and schemas.HEIGHTS.get(prop["type"]) is not None:
        item["height"] = schemas.HEIGHTS[prop["type"]]
    if proposal:
        # The completion path: the locked check allows a typed unknown piece with its drawn footprint and status
        # as a validated change (``adjusted_by_ai`` with the reason and ``drawn_type``, ``locked._agent_problems``:
        # "a drawn unknown that was not built may be typed"); ``type_proposal`` keeps the Milestone 10 rule too.
        item["type_proposal"] = True
        if item.get("drawn_type") is None:
            item["drawn_type"] = "unknown"
        item["adjusted_by_ai"] = {"by": "code", "stage": "layout", "typed_by_code": prop["type_method"],
                                  "reason": f"typed {prop['type']} by code ({prop['type_method']}): {prop['reason']}"}
        return
    if prop["type_method"] in ("twin", "level") and prop.get("source_status"):
        item["status"] = prop["source_status"]      # the same drawing as an agreed piece: its status
    if prop.get("footprint"):
        item["footprint"] = dict(prop["footprint"])
    if prop.get("front_deg") is not None and item.get("front_deg") is None:
        if prop.get("footprint"):
            item["front_deg"] = round(float(prop["front_deg"]), 3)
        else:
            set_front(item, float(prop["front_deg"]))


def apply_code_types(building: dict, proposal: bool = False) -> tuple[dict, list[dict]]:
    """A copy of the building with ``code_types`` applied (``type_method`` the method, ``inferred`` with the
    evidence) and the proposals; ``proposal=True`` for the completion path (see the module docstring)."""
    props = code_types(building)
    b = copy.deepcopy(building)
    by_id = {f["id"]: f for f in b.get("furniture") or []}
    for prop in props:
        if prop["piece_id"] in by_id:
            _apply_code_type(by_id[prop["piece_id"]], prop, proposal)
    return b, props


def infer_types(building: dict) -> list[dict]:
    """``[{"piece_id", "type", "reason", "confidence", "evidence": {...}}]`` (proposals; the building is unchanged).
    Milestone 13: the code-typed pieces (``code_types``: ``type_method`` twin / level / block / group_member) come
    first; the rules below see the building with them applied."""
    coded = code_types(building)
    out = list(coded)
    if coded:
        building = apply_code_types(building)[0]
    done = {p["piece_id"] for p in coded}
    rooms = _rooms(building)
    furniture = building.get("furniture") or []
    for item in furniture:
        if item["id"] in done:
            continue
        if item.get("type") != "unknown" or item.get("source") != "from_documents" or item.get("build") is False:
            continue
        room = rooms.get(item.get("room_id"))
        if room is None:
            continue
        piece = placer.drawn_piece(item)
        poly = piece.polygon()
        mates = [f for f in furniture if f.get("room_id") == room["id"] and f["id"] != item["id"]]
        held = outline_holds(poly, mates)
        if held and not any(f["type"] in schemas.FIXED_TYPES for f in mates if f["id"] in held):
            reason = (f"outline {piece.size[0]:.2f} x {piece.size[1]:.2f} m around {len(held)} other piece(s) "
                      f"({', '.join(held[:6])}): a rug or zone outline, not a piece (not built; the decor rules lay "
                      f"rugs under the groups)")
            out.append({"piece_id": item["id"], "type": OUTLINE_TYPE, "build": False, "reason": reason,
                        "confidence": CONF_OUTLINE, "evidence": _evidence(item, reason, CONF_OUTLINE)})
            continue
        ring = _room_ring(room)
        on_wall = bool(_wall_sides(piece, ring))
        others = [(f["type"], placer.drawn_piece(f, k)) for k, f in enumerate(mates)
                  if f.get("type") != "unknown" and f.get("build") is not False]
        if held:
            continue                       # an outline around fixed equipment: a counter run (split at ingest)
        host = _host_of(poly, mates)
        if host is not None:
            reason = (f"drawn inside {host['type']} {host['id']} ({DETAIL_INSIDE:.0%} or more of it): a detail of that "
                      f"piece (a sink bowl, an appliance front), not a piece of its own (not built)")
            out.append({"piece_id": item["id"], "type": DETAIL_TYPE, "build": False, "reason": reason,
                        "confidence": CONF_OUTLINE, "evidence": _evidence(item, reason, CONF_OUTLINE)})
            continue
        size_now = sorted(float(v) for v in item["footprint"]["size"])
        if (size_now[1] < MARK_SIDE_M or size_now[0] < MARK_THIN_M) and not any(
                PL._fits(t, size_now) for t in PL._size_table() if t not in SKIP_TYPES):
            reason = (f"{size_now[1]:.2f} x {size_now[0]:.2f} m fits no type and is "
                      + (f"smaller than {MARK_SIDE_M} m both ways" if size_now[1] < MARK_SIDE_M
                         else f"thinner than {MARK_THIN_M} m")
                      + ": a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built)")
            out.append({"piece_id": item["id"], "type": DETAIL_TYPE, "build": False, "reason": reason,
                        "confidence": CONF_OUTLINE, "evidence": _evidence(item, reason, CONF_OUTLINE)})
            continue
        types = PL.room_types(building, room)
        rtype = " + ".join(types)
        if any(t in ("other", "unknown") for t in types):
            # A room of no known purpose (real02's play and rest room is "other") says nothing about its pieces: the
            # room rule does not narrow the types there.
            allowed = {t for t in schemas.SIZE_OPTIONS if t not in schemas.CHILD_ONLY_TYPES}
        else:
            allowed = PL.allowed_in(building, room)
        size = [float(v) for v in item["footprint"]["size"]]
        sized = [t for t in allowed if t not in SKIP_TYPES and t in PL._size_table() and PL._fits(t, size)
                 and _shape_ok(t, size)]
        fits = sorted(t for t in sized if _position_ok(t, piece, on_wall, others))
        answers = {c.get("type") for c in item.get("type_candidates") or []}
        named = sorted(answers & set(fits))
        # An AI pass named another type that fits the size and the room: the piece is ambiguous (real02's sofas in
        # the open kitchen: kitchen_island / sofa); the agent decides on the plan crop, nothing is inferred.
        rivals = sorted((answers & set(sized)) - set(fits[:1] if len(fits) == 1 else named[:1]))
        if rivals:
            continue
        if len(fits) == 1:
            ftype, conf = fits[0], CONF_ONE
            reason = (f"{ftype}: the only type whose size range fits {size[0]:.2f} x {size[1]:.2f} m, that a "
                      f"{rtype} room holds and whose position rule holds here")
        elif len(named) == 1:
            ftype, conf = named[0], CONF_NAMED
            reason = (f"{ftype}: named by an AI pass and the only named type that fits the size ({size[0]:.2f} x "
                      f"{size[1]:.2f} m), the {rtype} room and the position (others fitting: "
                      f"{', '.join(t for t in fits if t != ftype)})")
        else:
            continue
        partners = [o for t, o in others if t in schemas.orientation_rule(ftype)["partners"]]
        prop = {"piece_id": item["id"], "type": ftype, "reason": reason, "confidence": conf,
                "evidence": _evidence(item, reason, conf)}
        if item.get("front_deg") is None:
            front = _front_for(ftype, piece, ring, partners)
            if front is not None:
                prop["front_deg"] = front
        out.append(prop)
    # fix round after P4a: the drawn nightstand-with-lamp symbols at a bed's head (module docstring)
    out += nightstand_symbols(building)
    return out


def _nightstand_size(size) -> bool:
    rng = PL.size_range("nightstand")
    if rng is None:
        return False
    (w0, w1), (d0, d1) = rng
    w, d = (float(v) for v in size)
    return (w0 <= w <= w1 and d0 <= d <= d1) or (w0 <= d <= w1 and d0 <= w <= d1)


def _crop_of(item: dict) -> Optional[str]:
    """The reading's plan crop of the piece's question (an AI evidence entry ``recognition:<key>``), else None."""
    for e in item.get("evidence") or []:
        entity = str((e or {}).get("entity") or "") if isinstance(e, dict) else ""
        if entity.startswith("recognition:") and len(entity) > len("recognition:"):
            return RECOGNITION_CROP.format(key=entity.split(":", 1)[1])
    return None


def nightstand_symbols(building: dict) -> list[dict]:
    """Fix round after P4a (module docstring): proposals ``{"piece_id", "type": "nightstand", "type_method":
    NIGHTSTAND_METHOD, "reason", "confidence", "evidence", "front_deg", "drawn_type", "bed_id", "side", "crop"}``
    for the drawn ``floor_lamp`` / ``side_table`` pieces of a nightstand's size standing beside a drawn bed's head
    (``group_checks.nightstand_place``: the back within ``nightstand_gap`` of the headboard line; the symbol from inside
    the bed block up to ``nightstand_gap`` outside the long side), one per free side and at most the bed's
    nightstands (``schemas.NIGHTSTANDS_PER_BED``); nearest first. Pure; the building is unchanged."""
    from wenart.furniture import group_checks as GC

    gap_max = float(GR.rule("nightstand_gap")["max"])
    furniture = building.get("furniture") or []
    out: list[dict] = []
    taken: set = set()
    for room in building.get("rooms") or []:
        items = [f for f in furniture if f.get("room_id") == room.get("id") and f.get("source") == "from_documents"
                 and f.get("build") is not False and f.get("footprint")]
        beds = sorted((f for f in items if schemas.NIGHTSTANDS_PER_BED.get(f.get("type"), 0) > 0),
                      key=lambda f: str(f["id"]))
        cands = [f for f in items if f.get("type") in NIGHTSTAND_SYMBOL_TYPES
                 and _nightstand_size(f["footprint"]["size"])]
        if not beds or not cands:
            continue
        stands = [f for f in items if f.get("type") == "nightstand"]
        for bed in beds:
            try:
                bp = placer.drawn_piece(bed)
            except (KeyError, TypeError, ValueError):
                continue
            half = bp.size[0] / 2.0

            def beside(f) -> Optional[dict]:
                try:
                    piece = placer.drawn_piece(f)
                except (KeyError, TypeError, ValueError):
                    return None
                xs = [abs(GC.to_local(bp, c)[0]) for c in piece.polygon().exterior.coords]
                if max(xs) < half - NIGHTSTAND_SIDE_IN_M or min(xs) > half + gap_max + 1e-9:
                    return None                     # not at the bed's long side (the middle of the bed, or too far)
                place = GC.nightstand_place(bp, piece)
                return place if place["head_offset_m"] <= gap_max + 1e-9 else None

            have = {pl["side"] for pl in (beside(f) for f in stands) if pl is not None}
            best: dict[str, tuple] = {}
            for f in cands:
                if f["id"] in taken:
                    continue
                pl = beside(f)
                if pl is None or pl["side"] in have:
                    continue
                key = (round(pl["head_offset_m"] + abs(pl["side_gap_m"]), 4), str(f["id"]))
                if pl["side"] not in best or key < best[pl["side"]][0]:
                    best[pl["side"]] = (key, f, pl)
            want = schemas.NIGHTSTANDS_PER_BED[bed["type"]] - len(have)
            front = bed.get("front_deg")
            if front is None:
                front = G.front_direction_deg(bp.rotation_deg)
            for side, (_key, f, pl) in sorted(best.items(), key=lambda kv: kv[1][0])[:max(0, want)]:
                taken.add(f["id"])
                w, d = (float(v) for v in f["footprint"]["size"])
                crop = _crop_of(f)
                text = (f"nightstand: a drawn {f['type']} of a nightstand's size ({w:.2f} x {d:.2f} m) at the {side} "
                        f"side of the drawn {bed['type']} {bed['id']}'s head (back {pl['head_offset_m']:.2f} m from "
                        f"the headboard line, {pl['side_gap_m']:.2f} m from the bed side; nightstand_gap "
                        f"{gap_max:.2f} m): the bed's nightstand drawn with its table lamp, not a floor lamp"
                        + (f" (plan crop {crop})" if crop else ""))
                ev = _evidence_code(f, NIGHTSTAND_METHOD, text, CONF_NIGHTSTAND, bed=bed["id"], side=side,
                                    drawn_type=f["type"])
                ev["rule"] = "furniture.infer.nightstand_symbols"
                if crop:
                    ev["crop"] = crop
                out.append({"piece_id": f["id"], "type": "nightstand", "type_method": NIGHTSTAND_METHOD,
                            "reason": text, "confidence": CONF_NIGHTSTAND, "evidence": ev,
                            "front_deg": round(float(front) % 360.0, 3), "drawn_type": f["type"], "bed_id": bed["id"],
                            "side": side, "crop": crop})
    return out


def _apply_nightstand(item: dict, prop: dict) -> None:
    """A nightstand symbol (``nightstand_symbols``): the type, the bed's front, ``inferred`` with the reason and
    ``adjusted_by_ai`` (``by: code``) with the drawn values kept (CLAUDE.md: every change keeps ``drawn_type``,
    ``drawn_footprint``, ``drawn_front_deg``, ``drawn_height`` and is labelled with the reason)."""
    item.setdefault("drawn_type", item.get("type"))
    item.setdefault("drawn_footprint", copy.deepcopy(item.get("footprint")))
    item.setdefault("drawn_front_deg", item.get("front_deg"))
    item.setdefault("drawn_height", item.get("height"))
    changed = {"type": item.get("type"), "front_deg": item.get("front_deg")}
    item["type"] = prop["type"]
    item["type_method"] = prop["type_method"]
    item["inferred"] = True
    item["inferred_reason"] = prop["reason"]
    item.setdefault("evidence", []).append(dict(prop["evidence"]))
    if prop.get("front_deg") is not None and (item.get("front_deg") is None or G.angle_difference_deg(
            float(item["front_deg"]), float(prop["front_deg"])) > 1.0):
        set_front(item, float(prop["front_deg"]))
    if isinstance(item.get("assumed"), list) and item.get("front_deg") is not None:
        item["assumed"] = [a for a in item["assumed"] if a != "front_deg"]
    label = {"by": "code", "stage": "reading", "rule": prop["type_method"], "reason": prop["reason"],
             "changed": changed}
    if prop.get("crop"):
        label["crop"] = prop["crop"]
    item["adjusted_by_ai"] = label


def _room_ring(room: dict):
    """The room outline as a shapely ring (CCW)."""
    from shapely.geometry import Polygon
    from shapely.geometry.polygon import orient

    poly = orient(Polygon(room["polygon"]), 1.0)
    return (poly if poly.is_valid else poly.buffer(0)).exterior


def set_front(item: dict, front_deg: float) -> None:
    """Give a piece a front: the footprint turned by whole quarter turns so its local -Y faces ``front_deg``
    (``placer.front_frame``: same rectangle, size swapped on an odd turn)."""
    rot, size = placer.front_frame(item["footprint"], front_deg)
    item["footprint"] = dict(item["footprint"], rotation_deg=round(rot, 3), size=[round(size[0], 4),
                                                                                   round(size[1], 4)])
    item["front_deg"] = round(G.normalise_angle(front_deg), 3)


def apply_inferences(building: dict, proposals: list[dict]) -> dict:
    """A copy of the building with the proposals applied (``inferred: true``, evidence method ``inferred``)."""
    b = copy.deepcopy(building)
    by_id = {f["id"]: f for f in b.get("furniture") or []}
    for prop in proposals:
        item = by_id.get(prop["piece_id"])
        if item is None:
            continue
        if prop.get("type_method") in CODE_TYPE_METHODS:          # Milestone 13: typed by code
            _apply_code_type(item, prop, proposal=False)
            continue
        if prop.get("type_method") == NIGHTSTAND_METHOD:          # fix round after P4a: a nightstand symbol
            _apply_nightstand(item, prop)
            continue
        ev = dict(prop.get("evidence") or _evidence(item, prop["reason"], float(prop.get("confidence", 0.5))))
        item.setdefault("evidence", []).append(ev)
        item["inferred"] = True
        item["inferred_reason"] = prop["reason"]
        if prop.get("build") is False or prop["type"] not in schemas.SIZE_OPTIONS:
            item["build"] = False
            item["inferred_as"] = prop["type"]
            continue
        item["type"] = prop["type"]
        if prop.get("front_deg") is not None and item.get("front_deg") is None:
            set_front(item, float(prop["front_deg"]))
    return b
