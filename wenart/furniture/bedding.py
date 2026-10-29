"""The beds' bedding and the nightstands' decor at the decor stage (29 Oct 2026, lesson UL121; user, sending a photo of
a full, soft bed: "look how realistic the bed is looking full and nice I want this much detail in our models";
docs/reference_details_20261029.md R35, R36). The rules and the meshes are ``wenart.blender.bedding_parts`` (pure, the
build reads them too); this pass writes what the build makes:

- ``plan_beds``: every bed of a bedroom or a child's room gets its style family's set in ``bedding_layers`` (``set``:
  the duvet, the euro shams, the sleeping pillows, the accent cushions, the lumbar; ``expected``: what its width takes;
  ``sides``: each side free or blocked by a wall or a piece along the duvet's span, so the duvet hangs almost to the
  floor on a free side only), with the reason; every throw on a bed gets its family's ``weave`` (the woven pattern of
  the blanket, the fringed throw over it); a bed whose model is made up with its own bedding gets a throw too, built
  only when the build finds its bedding flat or poorer than ours and dresses it (``when_dressed``).
- ``nightstand_sets`` (R36): a round drum nightstand (``form: drum``, the rooms helper's R17) gets the photo's decor
  set (white faceted vases, a dried palm leaf in one, a black and white box: one ``vase`` item with ``set: bedside``,
  one mesh) on its round top where it fits beside what stands there, under the room over its top (the ceiling, a
  window's sill, a bedside pendant over it).

Every change is ``added_by_ai`` / ``method: rule`` with its reason; ``building["bedding"]`` records the beds' sets, the
sets placed and the notes. ``review`` (model review M30, Argus U34) is ``bedding_parts.review``.
"""
from __future__ import annotations

import math
from typing import Callable, Optional

from wenart.blender import bedding_parts as BP

RULE = BP.RULE
LESSON = BP.LESSON
BED_ROOM_TYPES: tuple[str, ...] = BP.BED_ROOM_TYPES
NIGHTSTAND_GAP_M = 0.03          # = tabletop.ITEM_GAP_M: the set keeps this from the other items on the drum's top
NIGHTSTAND_MARGIN_M = 0.03       # = tabletop.TOP_MARGIN_M
PENDANT_CLEAR_M = 0.05           # the set's top stays this far under a bedside pendant over the nightstand


def family_of(style: Optional[dict]) -> str:
    return str((style or {}).get("family") or "").lower()


def _rooms(building: dict) -> dict[str, dict]:
    return {r["id"]: r for r in building.get("rooms") or [] if r.get("id")}


def _evidence(text: str) -> list[dict]:
    return [{"file": "building.json", "method": "inferred", "rule": RULE, "confidence": 0.7, "text": text}]


def _beds(building: dict) -> list[dict]:
    rooms = _rooms(building)
    return [b for b in building.get("furniture") or [] if b.get("type") in BP.BED_TYPES and b.get("footprint")
            and b.get("build", True) is not False
            and (rooms.get(b.get("room_id")) or {}).get("room_type") in BED_ROOM_TYPES]


def plan_beds(building: dict, style: Optional[dict], new_id: Optional[Callable[[str], str]] = None) -> list[str]:
    """Each bed's family set, its free sides and its throws' weave (module docstring; in place). Returns notes."""
    from wenart.furniture import decor as D

    fam = family_of(style)
    spec, why = BP.family_spec(fam)
    decor = building.setdefault("decor", [])
    notes, beds = [], {}
    for bed in _beds(building):
        _c, _r, (w, d) = BP.bed_frame(bed)
        sides = BP.bed_sides(bed, building)
        layers = dict(bed.get("bedding_layers") or {}) if isinstance(bed.get("bedding_layers"), dict) else {}
        want = BP.counts(spec, w)
        layers.update(family=spec["family"], set=spec, set_why=why, expected=want, sides=sides, bedding_rule=RULE,
                      bedding_why=(f"the {spec['family']} bedding set (UL121, R35): {want['euro_shams']} euro "
                                   f"sham(s), {want['pillows']} pillow(s), {want['accent']} accent cushion(s), "
                                   f"{want['lumbar']} lumbar; the duvet hangs almost to the floor on the free "
                                   f"side(s) {', '.join(s for s in BP.SIDES if sides[s]['free']) or '(none)'}"))
        bed["bedding_layers"] = layers
        beds[bed["id"]] = {"expected": want, "sides": {s: dict(v) for s, v in sides.items()}}
        blocked = [f"{s} by {v['by']} ({v['clear_m']:.2f} m)" for s, v in sides.items() if not v["free"]]
        notes.append(f"{bed.get('room_id')}: {bed['id']} the {spec['family']} bedding set"
                     + (f"; no overhang on {', '.join(blocked)}" if blocked else ""))
        throws = [t for t in decor if t.get("type") == "throw" and (t.get("host_id") == bed["id"]
                                                                   or str(t.get("slot") or "") == f"{bed['id']}.throw")]
        if not throws and new_id is not None and not D.takes_throw(bed):
            from wenart.furniture import dressing as DR
            from wenart.furniture.decor_ai import throw_item

            t = throw_item(bed)
            if t is not None:
                text = ("a throw across the foot of the bed, built only when the build finds the model's own bedding "
                        "flat or poorer than ours and dresses it (UL121)")
                t.update(id=new_id(bed["level_id"]), kind="decor", level_id=bed["level_id"], room_id=bed["room_id"],
                         asset=None, host_id=bed["id"], source="added_by_ai", method="rule", rule=RULE,
                         slot=f"{bed['id']}.throw", colour=None, confidence=0.7, status="verified",
                         evidence=_evidence(text), reason=text, when_dressed=True, layers=2,
                         accent_colour=DR.blanket_colour(style, None))
                decor.append(t)
                throws = [t]
                notes.append(f"{bed.get('room_id')}: throw {t['id']} on {bed['id']} (built when dressed)")
        for t in throws:
            if not isinstance(t.get("weave"), dict):
                t["weave"] = BP.throw_weave(fam)
                # its fringe hangs over the bed's free sides only (never into a wall or a piece beside the bed)
                t["weave"]["fringe_ends"] = [s for s in ("left", "right") if sides[s]["free"]]
                t["reason"] = f"{t.get('reason') or 'throw'}; {t['weave']['why']}"
    record = building.setdefault("bedding", {})
    record.update(rule=RULE, lesson=LESSON, family=spec["family"], beds=beds)
    return notes


# --------------------------------------------------------------------------
# R36: the round drum nightstand's decor set
# --------------------------------------------------------------------------

def _room_over(building: dict, room: dict, stand: dict) -> Optional[float]:
    """The height over a nightstand's top its room leaves (the ceiling and a window's sill: ``decor_ai.top_room``),
    and under a bedside pendant hung over it (``dressing``'s ``fixture: bedside`` anchored to it)."""
    from wenart.blender import parametric as P

    try:
        from wenart.furniture import decor_ai as DA
        ceiling_room, sill_room = DA.top_room(stand, room, building)
        room_over = min(v for v in (ceiling_room, sill_room) if v is not None)
    except Exception:  # noqa: BLE001 - no heights: the set is not added
        return None
    top = float(P.piece_bbox(stand)[2])
    for d in building.get("decor") or []:
        if d.get("type") == "pendant_light" and stand["id"] in (d.get("anchor_ids") or []) and d.get("center"):
            bottom = float(d["center"][2]) if len(d["center"]) > 2 else None
            if bottom is not None:
                room_over = min(room_over, bottom - top - PENDANT_CLEAR_M)
    return room_over


def _spot(stand: dict, items: list[dict], size) -> Optional[tuple[float, float]]:
    """A free spot for a ``size`` box on a drum's round top (pure): inside its circle (``NIGHTSTAND_MARGIN_M``), its
    half diagonal ``NIGHTSTAND_GAP_M`` clear of every item there (``room_details._onto_drum``'s rule); the farthest
    from them, the back first."""
    from wenart.furniture import tabletop as TT

    fp = stand["footprint"]
    r = min(float(v) for v in fp["size"][:2]) / 2.0 - NIGHTSTAND_MARGIN_M
    half = math.hypot(float(size[0]), float(size[1])) / 2.0
    if half > r:
        return None
    taken = []
    for it in items:
        lx, ly, w, d = TT.local_box(stand, it)
        taken.append((lx, ly, math.hypot(w, d) / 2.0))
    best, best_key = None, None
    step = 0.02
    n = int((r - half) / step) + 1
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x, y = i * step, j * step
            if math.hypot(x, y) + half > r + 1e-9:
                continue
            room = min([math.hypot(x - tx, y - ty) - half - th for tx, ty, th in taken] or [1.0])
            if room < NIGHTSTAND_GAP_M - 1e-9:
                continue
            key = (round(room, 3), y, -abs(x))
            if best_key is None or key > best_key:
                best, best_key = (x, y), key
    return best


def nightstand_sets(building: dict, style: Optional[dict], new_id: Callable[[str], str]) -> list[str]:
    """R36 (module docstring): the decor set on every round drum nightstand of a bedroom with room for it (in place;
    items with ids). Returns notes."""
    from wenart.furniture import tabletop as TT

    rooms = _rooms(building)
    decor = building.setdefault("decor", [])
    notes, placed = [], []
    for stand in building.get("furniture") or []:
        room = rooms.get(stand.get("room_id"))
        if stand.get("type") != "nightstand" or stand.get("form") != "drum" or room is None \
                or room.get("room_type") not in BED_ROOM_TYPES or stand.get("build", True) is False:
            continue
        on = [d for d in decor if d.get("host_id") == stand["id"] and d.get("center")]
        if any(d.get("set") == "bedside" for d in on):
            continue
        room_over = _room_over(building, room, stand)
        if room_over is None or room_over < BP.BEDSIDE_SET_MIN_H_M:
            notes.append(f"{room['id']}: no decor set on the drum {stand['id']}: "
                         f"{'no room over its top' if room_over is not None else 'its heights are unknown'}")
            continue
        h = round(min(BP.BEDSIDE_SET_H_M, room_over - 0.02), 3)
        for size in BP.BEDSIDE_SET_SIZES:
            spot = _spot(stand, on, size)
            if spot is None:
                continue
            text = ("the reference photo's nightstand set on the round drum nightstand (R36): white faceted vases, a "
                    "dried palm leaf in one, a small black and white box")
            it = {"kind": "decor", "type": "vase", "level_id": stand["level_id"], "room_id": stand["room_id"],
                  "asset": None, "host_id": stand["id"], "source": "added_by_ai", "method": "rule",
                  "rule": f"{RULE}.bedside_set", "slot": f"{stand['id']}.bedside_set", "colour": "white",
                  "confidence": 0.7, "status": "verified", "set": "bedside", "stems": "palm",
                  "center": TT._world(stand, *spot), "rotation_deg": float(stand["footprint"]["rotation_deg"]),
                  "size": [size[0], size[1], h], "evidence": _evidence(text), "reason": f"{text} ({BP.TAG})"}
            it["id"] = new_id(stand["level_id"])
            decor.append(it)
            placed.append(it["id"])
            notes.append(f"{room['id']}: the R36 decor set {it['id']} on the drum {stand['id']}")
            break
        else:
            notes.append(f"{room['id']}: no decor set on the drum {stand['id']}: its round top is full")
    record = building.setdefault("bedding", {})
    record["nightstand_sets"] = placed
    return notes


def dress_beds(building: dict, style: Optional[dict], new_id: Callable[[str], str]) -> tuple[dict, list[str]]:
    """The whole pass (module docstring; in place): ``(building, notes)``. A failure is a note and a warning, never the
    decor stage's end."""
    notes = []
    for step, args in ((plan_beds, (building, style, new_id)), (nightstand_sets, (building, style, new_id))):
        try:
            notes += step(*args)
        except Exception as exc:  # noqa: BLE001 - one helper's failure never ends the decor stage
            why = f"bedding ({step.__name__}) failed: {type(exc).__name__}: {exc}"[:240]
            notes.append(why)
            building["warnings"] = list(building.get("warnings") or []) + [why]
    building.setdefault("bedding", {})["notes"] = notes
    return building, notes


def review(built: dict, manifest: Optional[dict] = None, check: str = "U34") -> tuple[list[dict], int]:
    """= ``bedding_parts.review`` (the model review's M30, Argus U34)."""
    return BP.review(built, manifest, check=check)

