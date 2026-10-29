"""A different solution for each room (29 Oct 2026; user, sending seven professional interior renders: "also take some
inspiration from these photos", "look at all these details I want these details", "As much detail as you can digest",
"different solutions for different rooms"; lessons UL113, UL115 (hall part), UL119; docs/reference_details_20261029.md
V1, R13, R16, R17, R25, R26, R27, R32-R34, H7, R14, K13, G5).

What the runs had: every bedroom of a house looked the same (the same accent wall, the same fluted panel behind the bed,
the same standing nightstands, a TV on a unit, a freestanding desk). The photos show a designer giving each room its
own solution: one room painted a deep colour all round with a TV flat on the wall and a floating corner desk (P9), one
in a limewash finish with a wide timber headboard panel and floating nightstands (P10), one with slat panels (P2), one
with a fluted wall behind the bed (P1).

What (pure, deterministic; the decor stage calls ``plan`` through ``wenart.furniture.room_details.dress_details``, the
model review M28 and Argus U32 call ``review``):

- ``scheme_kind``: the rooms that get a scheme: living rooms, bedrooms, halls, dining rooms (and a kitchen with a
  dining table: only its dining wall), a home office (a room read as other with a desk and no bed).
- ``POOLS``: each kind's named bundles (a designer's coherent set of choices), each with its colours
  (``DEEP_COLOURS``, ``LIMEWASH_COLOURS``, ``ACCENT_COLOURS`` per style family): the scheme is the pair (bundle,
  colour). A bedroom's bundles: ``panel`` (one accent wall, the family's fluted panel behind the bed, standing
  nightstands, the TV on a unit), ``deep`` (all walls a deep colour, R25; an art pair over the bed, R16; round drum
  nightstands, R17; the TV flat on the wall, R26; a floating corner desk with shelves and wall cabinets, R27; ceiling
  track lights, R14), ``limewash`` (a limewash texture all round, R34; a wide timber headboard panel with a large art
  piece above it, R32; floating nightstands, R33; the TV on the wall), ``slats`` (one accent wall, full-height wood
  slats behind the bed, R13; a floating desk; track lights). A living room's: ``panel``, ``limewash``, ``slats`` (a
  slat wall behind the sofa; the TV on the wall), ``gallery`` (the TV on the wall, a lit niche, H1); its dining wall a
  full slat wall (K13) or a large art piece. A hall's: ``console`` (a console with a round mirror and its decor, H4,
  a round rug, H6), ``niche`` (a lit wall niche with floating shelves, H1, a runner), ``gallery`` (a console with art,
  a runner). Every bundle also names its living models (G5: a glass coffee table, a rattan lounge chair) and its extra
  details (a large leaning art frame, R5; a round wall mirror, R10; a floor vase with pampas grass, H5).
- ``plan``: each room's scheme, in level order, the rooms of one kind of a level in id order. The first candidate
  is the bundle the room's id hashes to (``_stable``, sha256: the same project gives the same schemes on every run);
  then the pool in order: the first bundle no other room of the kind on the level has and no room of the house has with
  that colour, else the first bundle new on the level, else the first (bundle, colour) new on the level; no two rooms
  of one kind on a level share a scheme while the pool lasts. A room whose reference photos show no panelling
  (``no_panel``: ``dressing.finish_decisions``) takes no bundle with a panel; a twin or a ``same_as`` room
  (``partners``) takes its partner's scheme (its decor is the partner's copy). Every choice carries its reason.
- ``resolve``: the bundle's values for the room's style family (``FAMILY_FEATURE``: a classic home's slats are a
  wainscot, a rustic home's fluted panel is a board wall; the floating and drum nightstands, the floating desk and
  the track lights only in the families that use them).
- ``record``: ``building["room_schemes"]`` (the full records) and ``room["scheme"]`` (what the build reads: the
  walls' finish and colour, the feature wall kind, the lighting; ``wenart.blender.looks``, ``feature_walls``).
- ``review``: two rooms of one kind on a level with the same scheme; a hall with no console or niche; a bedroom whose
  bed wall is bare (no panel, no headboard panel, no art or mirror over the bed): findings of U32 / M28.

Why: the user's photos; one treatment for every room reads as a template, not a designed house.
"""
from __future__ import annotations

import hashlib
from typing import Optional

RULE = "room_schemes"
LESSONS: tuple[str, ...] = ("UL113", "UL115", "UL119")
LESSON = "UL119"
REVIEW_CHECKS: tuple[str, ...] = ("U32", "M28")
SCHEME_ROOM_TYPES: tuple[str, ...] = ("living", "bedroom", "dining", "hall")
KINDS: tuple[str, ...] = ("bedroom", "living", "dining", "hall", "office")
HALL_STAIR_SHARE = 0.6           # = groups.yaml stair_cover: a hall whose stair covers more is a landing (no scheme)

# The families that use a detail (designer tables; the reference photos are modern, Scandinavian and japandi homes).
FLOATING_NIGHTSTAND_FAMILIES: tuple[str, ...] = ("modern", "contemporary", "modern minimal", "minimal", "japandi",
                                                 "scandinavian")
DRUM_NIGHTSTAND_FAMILIES: tuple[str, ...] = ("modern", "contemporary", "modern minimal", "minimal", "scandinavian",
                                             "japandi", "mediterranean")
FLOATING_DESK_FAMILIES: tuple[str, ...] = ("modern", "contemporary", "modern minimal", "minimal", "scandinavian",
                                           "japandi", "industrial")
TRACK_FAMILIES: tuple[str, ...] = ("modern", "contemporary", "modern minimal", "minimal", "industrial")    # H7, R14
GLASS_TABLE_FAMILIES: tuple[str, ...] = ("modern", "contemporary", "modern minimal", "minimal")           # G5
RATTAN_FAMILIES: tuple[str, ...] = ("scandinavian", "japandi", "mediterranean", "rustic", "contemporary")  # G5
# The panel a family builds for a scheme's feature (``resolve``): fluted = the family's UL106 panel
# (feature_walls.FAMILY_FEATURE_WALLS: fluted, or a wainscot in a classic home); a family without one builds vertical
# boards (slats); a classic home's slat wall is its wainscot.
FAMILY_FEATURE: dict[str, dict[str, str]] = {
    "classic": {"fluted": "wainscot", "slats": "wainscot"},
    "rustic": {"fluted": "slats"}, "mediterranean": {"fluted": "slats"}, "industrial": {"fluted": "slats"},
}
FLUTED_FAMILIES: tuple[str, ...] = ("modern", "contemporary", "modern minimal", "minimal", "scandinavian", "japandi")
PANEL_FEATURES: tuple[str, ...] = ("fluted", "slats", "headboard_panel", "wainscot")
# Colours (designer values, ``wenart.style.colours`` phrases): deep wall colours of linear luminance 0.15-0.26 (P9's dark
# green walls read deep, not black, under daylight), limewash colours 0.3-0.6 (P10's warm limewash), accent paints
# (the family's accent first: looks.FAMILY_ACCENTS).
DEEP_COLOURS: dict[str, tuple[str, ...]] = {
    "scandinavian": ("dark sage", "muted dusty blue", "dark taupe"),
    "japandi": ("muted olive", "dark taupe", "muted terracotta"),
    "modern": ("dark sage", "muted teal", "muted dusty blue"),
    "contemporary": ("muted teal", "dark sage", "dark taupe"),
    "modern minimal": ("dark taupe", "muted dusty blue", "dark sage"),
    "minimal": ("dark taupe", "muted dusty blue", "dark sage"),
    "industrial": ("muted teal", "muted olive", "dark taupe"),
    "mediterranean": ("muted terracotta", "muted dusty blue", "muted ochre"),
    "classic": ("muted dusty blue", "dark sage", "muted emerald"),
    "rustic": ("muted olive", "muted terracotta", "dark sage"),
}
LIMEWASH_COLOURS: dict[str, tuple[str, ...]] = {
    "scandinavian": ("warm greige", "pale muted sage", "muted sand"),
    "japandi": ("pale taupe", "muted sand", "warm greige"),
    "modern": ("warm greige", "pale taupe", "muted camel"),
    "contemporary": ("pale taupe", "warm greige", "muted camel"),
    "modern minimal": ("warm greige", "pale taupe", "muted sand"),
    "minimal": ("warm greige", "pale taupe", "muted sand"),
    "industrial": ("warm greige", "pale taupe", "muted camel"),
    "mediterranean": ("muted sand", "muted camel", "muted dusty pink"),
    "classic": ("warm greige", "pale taupe", "muted sand"),
    "rustic": ("muted sand", "warm greige", "muted camel"),
}
ACCENT_COLOURS: dict[str, tuple[str, ...]] = {
    "scandinavian": ("pale muted sage", "pale dusty blue", "pale taupe"),
    "japandi": ("pale taupe", "pale muted sage", "warm greige"),
    "modern": ("pale dusty blue", "pale muted sage", "warm greige"),
    "contemporary": ("pale taupe", "pale dusty blue", "pale muted sage"),
    "modern minimal": ("greige", "pale taupe", "pale dusty blue"),
    "minimal": ("greige", "pale taupe", "pale dusty blue"),
    "industrial": ("light charcoal", "pale taupe", "pale dusty blue"),
    "mediterranean": ("pale terracotta", "pale dusty blue", "muted sand"),
    "classic": ("pale dusty blue", "pale muted sage", "pale taupe"),
    "rustic": ("pale taupe", "pale muted sage", "muted sand"),
}
DEFAULT_FAMILY = "modern"
NEUTRAL_COLOURS: tuple[str, ...] = ("warm greige", "pale taupe", "greige")     # a hall's rug and vase tones
# The bundles (module docstring). Keys: walls (accent | deep_colour | limewash | plain), feature (the anchor wall:
# fluted | slats | headboard_panel | art_pair | art | none), tv (unit | wall), desk (freestanding | floating),
# nightstand (standing | drum | floating), lighting (downlights | track), dining_wall (slats | art | None), hall
# (console | niche | gallery), rug (round | runner), living models (coffee_table glass | wood, lounge_chair rattan |
# upholstered), extras (round_mirror, leaning_art, floor_vase, niche). Order: a bundle-major pool.
POOLS: dict[str, dict[str, dict]] = {
    "bedroom": {
        "panel": {"walls": "accent", "feature": "fluted", "nightstand": "standing", "tv": "unit",
                  "desk": "freestanding", "lighting": "downlights", "extras": ("round_mirror",)},
        "deep": {"walls": "deep_colour", "feature": "art_pair", "nightstand": "drum", "tv": "wall", "desk": "floating",
                 "lighting": "track", "extras": ("leaning_art",)},
        "limewash": {"walls": "limewash", "feature": "headboard_panel", "nightstand": "floating", "tv": "wall",
                     "desk": "freestanding", "lighting": "downlights", "extras": ("round_mirror",)},
        "slats": {"walls": "accent", "feature": "slats", "nightstand": "standing", "tv": "unit", "desk": "floating",
                  "lighting": "track", "extras": ("leaning_art",)},
    },
    "living": {
        "panel": {"walls": "accent", "feature": "fluted", "tv": "unit", "dining_wall": "art", "lighting": "downlights",
                  "coffee_table": "wood", "lounge_chair": "upholstered", "extras": ("leaning_art", "floor_vase")},
        "limewash": {"walls": "limewash", "feature": "art", "tv": "unit", "dining_wall": "slats",
                     "lighting": "downlights", "coffee_table": "glass", "lounge_chair": "rattan",
                     "extras": ("round_mirror", "floor_vase")},
        "slats": {"walls": "accent", "feature": "slats", "tv": "wall", "dining_wall": "art", "lighting": "track",
                  "coffee_table": "glass", "lounge_chair": "upholstered", "extras": ("floor_vase",)},
        "gallery": {"walls": "accent", "feature": "art", "tv": "wall", "dining_wall": "slats", "lighting": "track",
                    "coffee_table": "wood", "lounge_chair": "rattan", "extras": ("niche", "leaning_art",
                                                                                "floor_vase")},
    },
    "dining": {
        "slats": {"walls": "plain", "dining_wall": "slats", "lighting": "downlights", "extras": ()},
        "art": {"walls": "plain", "dining_wall": "art", "lighting": "downlights", "extras": ("floor_vase",)},
    },
    "hall": {
        "console": {"walls": "plain", "hall": "console", "rug": "round", "lighting": "downlights",
                    "extras": ("floor_vase",)},
        "niche": {"walls": "plain", "hall": "niche", "rug": "runner", "lighting": "track", "extras": ("floor_vase",)},
        "gallery": {"walls": "plain", "hall": "gallery", "rug": "runner", "lighting": "downlights", "extras": ()},
    },
    "office": {
        "floating": {"walls": "accent", "desk": "floating", "lighting": "track", "extras": ("leaning_art",)},
        "deep": {"walls": "deep_colour", "desk": "freestanding", "lighting": "downlights", "extras": ("floor_vase",)},
    },
}
WHY: dict[str, str] = {
    "accent": "one accent wall in a pale paint (UL106)",
    "deep_colour": "every wall of the room in a deep colour, white skirting and ceiling (R25)",
    "limewash": "a limewash texture on every wall (R34)",
    "plain": "the house's wall finish",
    "fluted": "a fluted panel on the anchor wall (UL106)",
    "slats": "full-height vertical wood slats on the anchor wall (R13, K13)",
    "headboard_panel": "a wide timber headboard panel, wider than the bed, a large art piece above it (R32)",
    "wainscot": "a painted wainscot on the anchor wall",
    "art_pair": "two framed prints over the headboard (R16)",
    "art": "a large art piece over the anchor piece",
    "none": "no feature on the anchor wall",
    "unit": "the TV on a TV unit (UL99)",
    "wall": "the TV mounted flat on the wall, no unit (R26)",
    "freestanding": "a freestanding desk",
    "floating": "a floating corner desk with shelves and wall cabinets over it, LED under them (R27)",
    "standing": "standing nightstands",
    "drum": "round drum nightstands (R17)",
    "floating_nightstand": "floating wall-mounted nightstands (R33)",
    "downlights": "recessed downlights (UL106)",
    "track": "black ceiling track lights (H7, R14)",
    "console": "a console with a round mirror over it and its decor (H4, R10), a round rug (H6)",
    "niche": "a lit wall niche with floating shelves and styled objects (H1), a runner",
    "gallery": "a console with art over it, a runner",
    "round": "a round rug (H6)",
    "runner": "a runner along the hall",
}


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def family_of(style: Optional[dict]) -> str:
    return str((style or {}).get("family") or "").lower()


def _stable(text: str) -> int:
    """A stable integer of a text (sha256; Python's ``hash`` changes per process)."""
    return int(hashlib.sha256(str(text).encode("utf-8")).hexdigest()[:12], 16)


def _pieces(building: dict, room_id: str, types=None) -> list[dict]:
    return [f for f in building.get("furniture") or [] if f.get("room_id") == room_id and f.get("footprint")
            and f.get("build", True) is not False and (types is None or f.get("type") in types)]


def _area(room: dict) -> float:
    pts = [tuple(p[:2]) for p in room.get("polygon") or []]
    if len(pts) < 3:
        return 0.0
    s = 0.0
    for i in range(len(pts)):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
        s += x0 * y1 - x1 * y0
    return abs(s) / 2.0


def _stair_share(building: dict, room: dict) -> float:
    area = _area(room)
    if area <= 1e-9:
        return 0.0
    stairs = sum(float(f["footprint"]["size"][0]) * float(f["footprint"]["size"][1])
                 for f in _pieces(building, room["id"], ("stair",)))
    return stairs / area


def scheme_kind(building: dict, room: dict) -> Optional[str]:
    """The scheme kind of a room (module docstring), None for a room without one (a wet room, a store, a landing)."""
    rt = room.get("room_type")
    if rt == "bedroom":
        return "bedroom"
    if rt == "living":
        return "living"
    if rt == "dining":
        return "dining"
    if rt == "kitchen":
        return "dining" if _pieces(building, room["id"], ("table_dining",)) else None
    if rt == "hall":
        return None if _stair_share(building, room) > HALL_STAIR_SHARE else "hall"
    if rt in ("other", "unknown"):
        pieces = _pieces(building, room["id"])
        types = {f.get("type") for f in pieces}
        if "desk" in types and not types & {"bed_double", "bed_single", "bunk_bed", "sofa", "sofa_corner"}:
            return "office"
    return None


def _colours(kind_walls: str, family: str) -> tuple[str, ...]:
    if kind_walls == "deep_colour":
        return DEEP_COLOURS.get(family) or DEEP_COLOURS[DEFAULT_FAMILY]
    if kind_walls == "limewash":
        return LIMEWASH_COLOURS.get(family) or LIMEWASH_COLOURS[DEFAULT_FAMILY]
    if kind_walls == "accent":
        return ACCENT_COLOURS.get(family) or ACCENT_COLOURS[DEFAULT_FAMILY]
    return NEUTRAL_COLOURS


def pool(kind: str, family: str) -> list[tuple[str, str]]:
    """The (bundle, colour) pairs of a kind for a family, bundle-major (the first colour of every bundle first)."""
    bundles = POOLS.get(kind) or {}
    lists = {name: _colours(spec.get("walls", "plain"), family) for name, spec in bundles.items()}
    depth = max((len(v) for v in lists.values()), default=0)
    out = []
    for k in range(depth):
        for name in bundles:
            cols = lists[name]
            if k < len(cols):
                out.append((name, cols[k]))
    return out


def feature_kind(family: str, feature: Optional[str]) -> Optional[str]:
    """The panel kind a family builds for a scheme's feature (``FAMILY_FEATURE``); the art and none features build no
    panel (None)."""
    if feature not in PANEL_FEATURES:
        return None
    sub = FAMILY_FEATURE.get(family, {})
    if feature == "fluted" and family not in FLUTED_FAMILIES and family not in FAMILY_FEATURE:
        return "slats"
    return sub.get(feature, feature)


NO_PANEL_FEATURE: dict[str, str] = {"bedroom": "art_pair", "living": "art", "office": "art"}


def has_panel(kind: str, bundle: str) -> bool:
    spec = (POOLS.get(kind) or {}).get(bundle) or {}
    return spec.get("feature") in PANEL_FEATURES or spec.get("dining_wall") == "slats"


def resolve(kind: str, bundle: str, colour: str, family: str, no_panel: bool = False) -> dict:
    """The scheme's values for the room's family (module docstring) and the reason of each; ``no_panel`` (the
    room's reference photos show no wall panelling, UL106): the bundle's panel becomes its art."""
    spec = dict((POOLS.get(kind) or {}).get(bundle) or {})
    fam = family or DEFAULT_FAMILY
    out: dict = {"kind": kind, "bundle": bundle, "colour": colour, "key": f"{bundle}:{colour}", "family": family or None}
    why: dict[str, str] = {}
    if no_panel and spec.get("feature") in PANEL_FEATURES:
        spec["feature"] = NO_PANEL_FEATURE.get(kind, "art")
        why["no_panel"] = (f"the reference photos of the space show no wall panelling: {WHY[spec['feature']]} in "
                           f"place of the bundle's panel")
    if no_panel and spec.get("dining_wall") == "slats":
        spec["dining_wall"] = "art"
    walls = spec.get("walls", "plain")
    out["walls"] = walls
    out["wall_colour"] = colour if walls in ("accent", "deep_colour", "limewash") else None
    why["walls"] = WHY[walls] + (f" ({colour})" if out["wall_colour"] else "")
    feat = spec.get("feature")
    if feat is not None:
        out["feature"] = feat
        out["feature_kind"] = feature_kind(fam, feat)
        why["feature"] = WHY[feat] + (f"; built as the {fam} home's {out['feature_kind'].replace('_', ' ')}"
                                      if out["feature_kind"] not in (None, feat) else "")
    if "tv" in spec:
        out["tv"] = spec["tv"]
        why["tv"] = WHY[spec["tv"]]
    if "desk" in spec:
        desk = spec["desk"]
        if desk == "floating" and fam not in FLOATING_DESK_FAMILIES:
            desk = "freestanding"
            why["desk"] = f"{WHY['freestanding']} (a {fam} home has no floating desk)"
        else:
            why["desk"] = WHY[desk]
        out["desk"] = desk
    if "nightstand" in spec:
        ns = spec["nightstand"]
        if ns == "floating" and fam not in FLOATING_NIGHTSTAND_FAMILIES or \
                ns == "drum" and fam not in DRUM_NIGHTSTAND_FAMILIES:
            why["nightstand"] = f"{WHY['standing']} (a {fam} home has no {ns} nightstand)"
            ns = "standing"
        else:
            why["nightstand"] = WHY["floating_nightstand" if ns == "floating" else ns]
        out["nightstand"] = ns
    light = spec.get("lighting", "downlights")
    if light == "track" and fam not in TRACK_FAMILIES:
        why["lighting"] = f"{WHY['downlights']} (track lights are an option of the modern families)"
        light = "downlights"
    else:
        why["lighting"] = WHY[light]
    out["lighting"] = light
    if "dining_wall" in spec:
        out["dining_wall"] = spec["dining_wall"]
        dw = spec["dining_wall"]
        if dw == "slats" and feature_kind(fam, "slats") != "slats":
            out["dining_wall"] = "art"
            why["dining_wall"] = f"{WHY['art']} on the dining wall (a {fam} home builds no slat wall)"
        elif dw:
            why["dining_wall"] = (WHY["slats"] if dw == "slats" else WHY["art"]) + " (the dining wall)"
    for key in ("hall", "rug"):
        if key in spec:
            out[key] = spec[key]
            why[key] = WHY[spec[key]]
    if "coffee_table" in spec:
        ct = spec["coffee_table"]
        if ct == "glass" and fam not in GLASS_TABLE_FAMILIES:
            ct = "wood"
        out["coffee_table"] = ct
        why["coffee_table"] = f"a {ct} coffee table (G5)"
    if "lounge_chair" in spec:
        lc = spec["lounge_chair"]
        if lc == "rattan" and fam not in RATTAN_FAMILIES:
            lc = "upholstered"
        out["lounge_chair"] = lc
        why["lounge_chair"] = f"a {lc} lounge chair (G5)"
    out["extras"] = list(spec.get("extras") or ())
    out["why"] = why
    return out


# --------------------------------------------------------------------------
# the plan
# --------------------------------------------------------------------------

def _level_order(building: dict) -> dict:
    return {lv.get("id"): (float(lv.get("elevation") or 0.0), str(lv.get("id"))) for lv in building.get("levels") or []}


def plan(building: dict, style: Optional[dict], no_panel=(), partners: Optional[dict] = None) -> dict[str, dict]:
    """``{room id: scheme}`` of every room with a scheme kind (module docstring); ``no_panel``: the rooms whose
    reference photos show no panelling (no bundle with a panel); ``partners``: ``{room id: partner id}`` of the rooms
    whose decor is their partner's copy (they take the partner's scheme)."""
    fam = family_of(style)
    order = _level_order(building)
    partners = dict(partners or {})
    no_panel = set(no_panel or ())
    rooms = []
    for room in building.get("rooms") or []:
        kind = scheme_kind(building, room)
        if kind is not None and room.get("id"):
            rooms.append((order.get(room.get("level_id"), (0.0, "")), kind, str(room["id"]), room))
    rooms.sort(key=lambda r: (r[0], KINDS.index(r[1]), r[2]))
    out: dict[str, dict] = {}
    used_level: dict[tuple, set] = {}           # (level, kind) -> {bundle}
    keys_level: dict[tuple, set] = {}           # (level, kind) -> {(bundle, colour)}
    keys_house: dict[str, set] = {}             # kind -> {(bundle, colour)}
    for _lv, kind, rid, room in rooms:
        if rid in partners:
            continue                            # after the others: the partner's scheme
        cands = pool(kind, fam)
        bundles = list((POOLS.get(kind) or {}).keys())
        notes = []
        if not cands:
            continue
        first = _stable(rid) % len(bundles)
        bare = rid in no_panel

        def colour_index(c):
            cols = _colours(POOLS[kind][c[0]].get("walls", "plain"), fam)
            return cols.index(c[1]) if c[1] in cols else 0
        # the pool from the bundle the room's id hashes to: every bundle in its first colour, then in its second, ...;
        # a room whose photos show no panelling tries the bundles without a panel first
        ring = sorted(cands, key=lambda c: (colour_index(c), bare and has_panel(kind, c[0]),
                                            (bundles.index(c[0]) - first) % len(bundles)))
        if bare:
            notes.append("the reference photos of the space show no wall panelling: the bundles without a panel "
                         "first, a panel replaced by art")
        lk = (room.get("level_id"), kind)
        lv_b, lv_k, house = used_level.setdefault(lk, set()), keys_level.setdefault(lk, set()), \
            keys_house.setdefault(kind, set())
        pick, how = None, ""
        for test, text in ((lambda c: c[0] not in lv_b and c not in house,
                            "the first bundle no other room of its kind on the level has"),
                           (lambda c: c[0] not in lv_b, "the first bundle new on its level"),
                           (lambda c: c not in lv_k, "the first bundle and colour new on its level"),
                           (lambda c: True, "the pool is used up on its level: the bundle its id hashes to")):
            pick = next((c for c in ring if test(c)), None)
            if pick is not None:
                how = text
                break
        bundle, colour = pick
        lv_b.add(bundle)
        lv_k.add(pick)
        house.add(pick)
        rec = resolve(kind, bundle, colour, fam, no_panel=bare)
        rec.update(room_id=rid, level_id=room.get("level_id"), room_type=room.get("room_type"), rule=RULE,
                   lesson=LESSON, copied_from=None, notes=notes,
                   reason=(f"{kind} scheme '{bundle}' in {colour} from the {fam or 'house'} pool of "
                           f"{len(cands)} ({how}; the pool starts at the bundle its id hashes to: a different solution "
                           f"for each room, V1)"))
        out[rid] = rec
    for _lv, kind, rid, room in rooms:
        pid = partners.get(rid)
        if pid is None:
            continue
        src = out.get(pid)
        if src is None:
            continue
        rec = dict(src, room_id=rid, level_id=room.get("level_id"), room_type=room.get("room_type"), copied_from=pid,
                   why=dict(src.get("why") or {}), extras=list(src.get("extras") or ()), notes=[],
                   reason=f"the scheme of its partner {pid} (its decor is the partner's copy)")
        out[rid] = rec
    return out


COMPACT_KEYS: tuple[str, ...] = ("kind", "bundle", "key", "walls", "wall_colour", "feature", "feature_kind", "tv",
                                 "desk", "nightstand", "lighting", "dining_wall", "hall", "rug", "copied_from")


def compact(rec: dict) -> dict:
    """The part of a scheme the build reads (``room["scheme"]``)."""
    out = {k: rec[k] for k in COMPACT_KEYS if k in rec}
    out["rule"] = RULE
    out["reason"] = rec.get("reason")
    return out


def record(building: dict, schemes: dict, style: Optional[dict], notes: Optional[list] = None) -> dict:
    """``building["room_schemes"]`` and every scheme room's ``scheme`` (in place); returns the record."""
    rooms = {r.get("id"): r for r in building.get("rooms") or []}
    for rid, room in rooms.items():
        if rid in schemes:
            room["scheme"] = compact(schemes[rid])
        else:
            room.pop("scheme", None)
    rec = {"rule": RULE, "lessons": list(LESSONS), "family": family_of(style) or None, "rooms": schemes,
           "notes": list(notes or [])}
    building["room_schemes"] = rec
    return rec


def scheme_of(building: dict, room_id: Optional[str]) -> dict:
    """A room's scheme: the full record of ``building["room_schemes"]``, else the room's compact ``scheme``, else {}."""
    rec = ((building.get("room_schemes") or {}).get("rooms") or {}).get(room_id)
    if isinstance(rec, dict):
        return rec
    room = next((r for r in building.get("rooms") or [] if r.get("id") == room_id), None)
    return dict((room or {}).get("scheme") or {})


# --------------------------------------------------------------------------
# the review (U32 / M28)
# --------------------------------------------------------------------------

CONSOLE_TYPES: tuple[str, ...] = ("console_table", "shoe_cabinet", "dresser", "sideboard")
BED_TYPES: tuple[str, ...] = ("bed_double", "bed_single")
BED_WALL_DECOR: tuple[str, ...] = ("wall_art", "mirror")


def _bed_wall_dressed(building: dict, room: dict, manifest: Optional[dict]) -> tuple[bool, str]:
    """Whether a bedroom's bed wall shows something (pure): a feature panel built on it (the build's
    ``room["feature_wall"]`` record or the scene's feature-wall object), or wall art or a mirror anchored over a bed."""
    rid = room["id"]
    if isinstance(room.get("feature_wall"), dict):
        return True, f"a {room['feature_wall'].get('kind', 'feature')} panel"
    if any(o.get("detail") == "feature_wall" and o.get("room_id") == rid for o in (manifest or {}).get("objects") or []
           if isinstance(o, dict)):
        return True, "a feature panel"
    beds = {f["id"] for f in _pieces(building, rid, BED_TYPES)}
    for d in building.get("decor") or []:
        if d.get("room_id") == rid and d.get("type") in BED_WALL_DECOR and set(d.get("anchor_ids") or ()) & beds:
            return True, f"{d.get('type')} {d.get('id')} over the bed"
    if manifest is not None and (manifest.get("objects") or []):
        hung = {o.get("decor_id") for o in manifest["objects"] if isinstance(o, dict) and o.get("kind") == "decor"
                and o.get("type") in BED_WALL_DECOR}
        if any(d.get("id") in hung for d in building.get("decor") or [] if d.get("room_id") == rid
               and d.get("type") in BED_WALL_DECOR and set(d.get("anchor_ids") or ()) & beds):
            return True, "art over the bed"
    return False, ""


def review(building: dict, manifest: Optional[dict] = None, check: str = "U32") -> tuple[list[dict], int]:
    """``(findings, rooms checked)`` (module docstring; pure). A finding: ``{check, severity, target, room_id, message,
    problem, lesson}``; ``problem`` same_scheme | hall_bare | bed_wall_bare | no_scheme."""
    out: list[dict] = []
    schemes = ((building.get("room_schemes") or {}).get("rooms") or {})
    rooms = [r for r in building.get("rooms") or [] if r.get("id")]
    n = 0
    seen: dict[tuple, str] = {}
    for room in sorted(rooms, key=lambda r: str(r["id"])):
        kind = scheme_kind(building, room)
        if kind is None:
            continue
        n += 1
        rid = room["id"]
        rec = schemes.get(rid) if isinstance(schemes.get(rid), dict) else (room.get("scheme") or {})
        if not rec and kind in ("bedroom", "living"):
            out.append({"check": check, "severity": "minor", "target": rid, "room_id": rid, "problem": "no_scheme",
                        "lesson": LESSON, "message": f"{rid} ({kind}) has no room scheme: it takes the house's one "
                                                    "treatment (V1: a different solution for each room)"})
        if rec and not rec.get("copied_from"):
            k = (room.get("level_id"), kind, rec.get("key"))
            if k in seen:
                out.append({"check": check, "severity": "major", "target": rid, "room_id": rid,
                            "problem": "same_scheme", "lesson": LESSON, "other": seen[k],
                            "message": f"{rid} and {seen[k]} ({kind}s on {room.get('level_id')}) share the scheme "
                                       f"{rec.get('key')!r}: no two rooms of one type on a level the same (V1)"})
            else:
                seen[k] = rid
        if kind == "hall":
            consoles = _pieces(building, rid, CONSOLE_TYPES)
            niche = [d for d in building.get("decor") or [] if d.get("room_id") == rid and d.get("type") == "wall_niche"]
            if not consoles and not niche:
                area = _area(room)
                out.append({"check": check, "severity": "minor" if area < 4.0 else "major", "target": rid,
                            "room_id": rid, "problem": "hall_bare", "lesson": "UL115",
                            "message": f"{rid} (hall, {area:.1f} m²) has no console and no wall niche (H1, H4)"})
        if kind == "bedroom" and _pieces(building, rid, BED_TYPES):
            ok, _what = _bed_wall_dressed(building, room, manifest)
            if not ok:
                out.append({"check": check, "severity": "minor", "target": rid, "room_id": rid,
                            "problem": "bed_wall_bare", "lesson": "UL113",
                            "message": f"{rid} (bedroom): the wall behind the bed is bare (no panel, headboard panel, "
                                       f"art or mirror over the bed; R16, R32, UL106)"})
    return out, n
