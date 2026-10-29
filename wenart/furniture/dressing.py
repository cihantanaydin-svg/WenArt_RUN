"""The professional dressing of bedrooms and living rooms (29 Oct 2026, lesson UL106; user, showing a professional bedroom
render: "look at this renders I want my renders to be as professional as these ones").

What the reference shows that our renders lacked, and what this pass (pure; ``decor_ai.apply`` calls ``dress`` after
the lights, before the host frames) gives every project of the fitting style families:

- ``finish_decisions``: per living room and bedroom, whether its accent wall gets the family's panel (fluted oak, a
  classic wainscot: ``wenart.blender.feature_walls``) and its wood floor the family's pattern (herringbone, chevron:
  ``wenart.blender.parquet``), read from the room's reference recipe (UL42: ``wall_panelling`` in at least
  ``recipe.OFTEN_SHARE`` of the photos of the space and style; photos that show none keep the painted accent), the
  family's table where no photo was read. Written to ``building["dressing"]["rooms"]``; the build follows it.
- ``dress_curtains``: the curtains of those rooms in two layers (``layers`` sheer + drape: a white sheer behind the
  drape, ``parametric.curtain_parts``), and in the families that hang them so (``TRACK_FAMILIES``) a floor-length
  curtain on a ceiling track (``track: ceiling``, its top ``TRACK_CLEAR_M`` under a flat ceiling over it; a sloped
  ceiling keeps the rod).
- ``layer_bedding``: a double bed's bedding in layers: two euro shams behind the sleeping pillows where the bed model
  is dressed by us (``bedding_layers`` on the bed: ``textiles.euro_shams``, only against a real headboard), and its
  throw in two layers (``layers`` 2: a second, narrower blanket across the foot in a contrasting colour,
  ``accent_colour``); a bed whose throw slot the AI left empty gets the throw by rule (``decor_ai.throw_item``) when
  its model has no made bedding (``decor.takes_throw``).
- ``accent_lights``: the light plan's own fixtures in the professional roles, never more of them and never closer
  together (the spacing and the count stay ``ceiling_lights``'): the light over a bed or a single light over a dining
  table becomes the room's statement fixture (``fixture: statement``: the refit takes a chandelier or multi-globe
  model, ``fit.fixture_pool``; a flush light there becomes a pendant where the ceiling leaves its drop), the general
  lights of the lumen method (the rule's lights with no zone anchor) become small recessed downlights
  (``fixture: downlight``, ``parametric.downlight_parts``) in the families that use them, and a double bed whose
  nightstands carry no table lamp gets a slim pendant hanging low over each of them (``fixture: bedside``) when no
  other ceiling fixture of the room is within ``FIXTURE_GAP_M``.

Every change is ``added_by_ai`` / ``method: rule`` with its reason; ``review(built, manifest)`` (Argus U23 and the
model review's M23) lists what a built room still lacks against this bar.
"""
from __future__ import annotations

import math
from typing import Callable, Optional

from wenart import geometry as G

DRESS_ROOM_TYPES: tuple[str, ...] = ("living", "bedroom")
RULE = "dressing.ul106"
LESSON = "UL106"
# curtains
NO_LAYER_FAMILIES: tuple[str, ...] = ("industrial",)        # blinds and plain panels there
TRACK_FAMILIES: tuple[str, ...] = ("modern", "contemporary", "modern minimal", "minimal", "scandinavian", "japandi")
TRACK_CLEAR_M = 0.01             # the track's top under the ceiling
LAYERED_DEPTH_M = 0.14           # a layered curtain's box (sheer and drape, each with its pleats)
FLOOR_LENGTH_M = 0.05            # = furniture.FLOOR_LENGTH_M: a curtain whose bottom is this low reaches the floor
# bedding
SHAM_BEDS: tuple[str, ...] = ("bed_double",)
THROW_BEDS: tuple[str, ...] = ("bed_double", "bed_single")
# the second blanket's colour by family where the brief names no throw colours (designer values)
FAMILY_BLANKET: dict[str, str] = {"scandinavian": "charcoal", "modern": "charcoal", "contemporary": "greige",
                                  "modern minimal": "greige", "minimal": "greige", "japandi": "olive",
                                  "classic": "navy", "mediterranean": "terracotta", "rustic": "rust",
                                  "industrial": "charcoal"}
DEFAULT_BLANKET = "greige"
# lights
STATEMENT_FAMILIES: tuple[str, ...] = ("modern", "contemporary", "scandinavian", "classic", "mediterranean",
                                       "modern minimal", "minimal", "rustic", "industrial")
DOWNLIGHT_FAMILIES: tuple[str, ...] = ("modern", "contemporary", "modern minimal", "minimal", "scandinavian",
                                       "japandi")
BEDSIDE_FAMILIES: tuple[str, ...] = ("modern", "contemporary", "scandinavian", "modern minimal", "minimal",
                                     "japandi")
LIGHT_TYPES: tuple[str, ...] = ("pendant_light", "ceiling_light")
FIXTURE_GAP_M = 1.2              # the lights plan's spacing (no two ceiling fixtures closer): never broken here
STATEMENT_SIZE = (0.60, 0.60)
STATEMENT_BOTTOM_M = 2.0         # = decor_ai.PENDANT_MIN_BOTTOM_M: a pendant not over a table stays above the head
PENDANT_MIN_DROP_M = 0.45        # a flush light becomes a statement pendant only with this much drop
DOWNLIGHT_SIZE = (0.09, 0.09, 0.012)     # = parametric.DOWNLIGHT_SIZE
BEDSIDE_SIZE = (0.18, 0.18)
BEDSIDE_OVER_TOP_M = 0.55        # a bedside pendant's bottom this far over its nightstand's top
NIGHTSTAND_REACH_M = 0.9         # a nightstand this close to a bed's head corner is that bed's
# review
REVIEW_CHECKS = ("U23", "M23")


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def family_of(style: Optional[dict]) -> str:
    return str((style or {}).get("family") or "").lower()


def _rooms(building: dict) -> dict[str, dict]:
    return {r["id"]: r for r in building.get("rooms") or [] if r.get("id")}


def _level(building: dict, level_id) -> dict:
    return next((lv for lv in building.get("levels") or [] if lv.get("id") == level_id), {})


def _pieces(building: dict, room_id: str, types=None) -> list[dict]:
    return [f for f in building.get("furniture") or [] if f.get("room_id") == room_id and f.get("footprint")
            and f.get("build", True) is not False and (types is None or f.get("type") in types)]


def _ceiling_over(building: dict, item: dict, size) -> tuple[float, float]:
    """``(ceiling over the item, the level's flat ceiling)``, heights over the level's floor."""
    level = _level(building, item.get("level_id"))
    flat = float(level.get("ceiling_height") or 2.7)
    try:
        from wenart.furniture import decor as D
        planes = D.ceiling_planes(building, item.get("level_id"))
        if planes:
            here = D.ceiling_over(building, item.get("level_id"), item["center"][:2], size,
                                  float(item.get("rotation_deg") or 0.0), planes=planes)
            return min(flat, float(here)), flat
    except Exception:  # noqa: BLE001 - without the roof's planes the flat ceiling
        pass
    return flat, flat


def _note(item: dict, text: str) -> None:
    item["dressing"] = list(item.get("dressing") or []) + [text]


def _evidence(text: str) -> list[dict]:
    return [{"file": "building.json", "method": "rule", "confidence": 0.7, "model": "rule", "pass": 1, "text": text}]


# --------------------------------------------------------------------------
# finishes (the build follows these)
# --------------------------------------------------------------------------

def finish_decisions(building: dict, style: Optional[dict], recipe_of: Optional[Callable] = None) -> dict:
    """``{room id: {"feature_wall": bool, "feature_wall_why", "floor_pattern": bool, "floor_pattern_why"}}`` of the
    living rooms and bedrooms (module docstring); ``recipe_of(room)`` gives the room's recipe (``decor_ai.room_recipe``)."""
    try:
        from wenart.style import recipe as RC
        often = float(RC.OFTEN_SHARE)
    except ImportError:
        often = 0.3
    out = {}
    for rid, room in sorted(_rooms(building).items()):
        if room.get("room_type") not in DRESS_ROOM_TYPES:
            continue
        rec = recipe_of(room) if recipe_of else None
        rec = rec if isinstance(rec, dict) else {}
        photos = rec.get("source") != "default" and int(rec.get("n") or 0) > 0
        share = ((rec.get("layers") or {}).get("wall_panelling") or {}).get("share")
        dec = {}
        if photos and isinstance(share, (int, float)):
            n = int(rec.get("n") or 0)
            if float(share) >= often - 1e-9:
                dec.update(feature_wall=True, feature_wall_why=(
                    f"wall panelling in {float(share):.0%} of {n} reference photos of the space and style"))
            else:
                dec.update(feature_wall=False, feature_wall_why=(
                    f"the {n} reference photos of the space and style show wall panelling in only "
                    f"{float(share):.0%}: the painted accent stays"))
        floor = ((rec.get("palette") or {}).get("floor") or {}).get("value") if photos else None
        if floor and floor not in ("light_wood", "mid_wood", "dark_wood"):
            dec.update(floor_pattern=False, floor_pattern_why=f"the reference photos show a {floor} floor")
        if dec:
            out[rid] = dec
    return out


# --------------------------------------------------------------------------
# curtains
# --------------------------------------------------------------------------

def dress_curtains(building: dict, style: Optional[dict]) -> list[str]:
    """Layer the curtains of the living rooms and bedrooms and hang the floor-length ones on a ceiling track (module
    docstring; in place). Returns notes."""
    fam = family_of(style)
    if fam in NO_LAYER_FAMILIES:
        return []
    rooms = _rooms(building)
    notes = []
    for item in building.get("decor") or []:
        room = rooms.get(item.get("room_id"))
        if item.get("type") != "curtain" or room is None or room.get("room_type") not in DRESS_ROOM_TYPES:
            continue
        if not item.get("center") or len(item.get("size") or []) < 3 or item.get("layers"):
            continue
        item["layers"] = ["sheer", "drape"]
        size = [float(v) for v in item["size"]]
        size[1] = max(size[1], LAYERED_DEPTH_M)
        bottom = float(item["center"][2]) if len(item["center"]) > 2 else 0.0
        what = "a white sheer behind the drape"
        if fam in TRACK_FAMILIES and bottom <= FLOOR_LENGTH_M + 1e-9:
            here, flat = _ceiling_over(building, item, size[:2])
            if here >= flat - 1e-6:
                top = flat - TRACK_CLEAR_M
                if top - bottom > size[2] + 1e-6:
                    size[2] = round(top - bottom, 3)
                    item["track"] = "ceiling"
                    what += f", full height on a ceiling track ({top:.2f} m)"
        item["size"] = [round(v, 3) for v in size]
        item["reason"] = f"{item.get('reason') or 'curtains'}; layered: {what} (UL106)"
        _note(item, f"layered curtain: {what}")
        notes.append(f"{item.get('room_id')}: curtain {item.get('id')} layered ({what})")
    return notes


# --------------------------------------------------------------------------
# bedding
# --------------------------------------------------------------------------

def blanket_colour(style: Optional[dict], throw_colour: Optional[str]) -> str:
    """The second blanket's colour: the brief's second throw colour (another than the throw's), else the family's
    contrast (``FAMILY_BLANKET``)."""
    decor = (style or {}).get("decor") if isinstance((style or {}).get("decor"), dict) else {}
    for c in decor.get("throw_colours") or []:
        if c and c != throw_colour:
            return str(c)
    return FAMILY_BLANKET.get(family_of(style), DEFAULT_BLANKET)


def layer_bedding(building: dict, style: Optional[dict], new_id: Optional[Callable[[str], str]] = None) -> list[str]:
    """Euro shams on the double beds and a second blanket over every bed's throw (module docstring; in place).
    Returns notes."""
    from wenart.furniture import decor as D

    rooms = _rooms(building)
    decor = building.setdefault("decor", [])
    notes = []
    for bed in building.get("furniture") or []:
        room = rooms.get(bed.get("room_id"))
        if bed.get("type") not in THROW_BEDS or room is None or room.get("room_type") not in ("bedroom", "child") \
                or not bed.get("footprint") or bed.get("build", True) is False:
            continue
        if bed["type"] in SHAM_BEDS:
            bed["bedding_layers"] = {"euro_shams": 2, "rule": RULE,
                                     "why": "two euro shams behind the sleeping pillows (UL106; built where the bed is "
                                            "dressed by us and has a headboard)"}
        throws = [d for d in decor if d.get("type") == "throw" and (d.get("host_id") == bed["id"]
                                                                     or str(d.get("slot") or "") == f"{bed['id']}.throw")]
        if not throws and new_id is not None and D.takes_throw(bed):
            from wenart.furniture.decor_ai import throw_item

            t = throw_item(bed)
            if t is not None:
                why = "a throw across the foot of the bed (UL106: layered bedding)"
                t.update(id=new_id(bed["level_id"]), kind="decor", level_id=bed["level_id"], room_id=bed["room_id"],
                         asset=None, host_id=bed["id"], source="added_by_ai", method="rule", rule=RULE,
                         slot=f"{bed['id']}.throw", colour=None, confidence=0.7, status="verified",
                         evidence=_evidence(why), reason=why)
                decor.append(t)
                throws = [t]
                notes.append(f"{bed['room_id']}: throw {t['id']} added on {bed['id']} (layered bedding)")
        for t in throws:
            if int(t.get("layers") or 1) >= 2:
                continue
            t["layers"] = 2
            t["accent_colour"] = blanket_colour(style, t.get("colour"))
            _note(t, f"a second blanket in {t['accent_colour']} across the foot (UL106)")
            notes.append(f"{bed['room_id']}: throw {t.get('id')} in two layers ({t['accent_colour']} blanket)")
    return notes


# --------------------------------------------------------------------------
# lights
# --------------------------------------------------------------------------

def _xy(item: dict) -> tuple[float, float]:
    c = item.get("center") or [0.0, 0.0]
    return float(c[0]), float(c[1])


def _inside(piece: dict, p) -> bool:
    fp = piece["footprint"]
    poly = G.rotated_rectangle(fp["center"], fp["size"][:2], float(fp.get("rotation_deg") or 0.0))
    return G.point_in_polygon(p, poly)


def _room_lights(building: dict, room_id: str) -> list[dict]:
    return [d for d in building.get("decor") or [] if d.get("room_id") == room_id and d.get("type") in LIGHT_TYPES
            and d.get("center")]


def _head_corners(bed: dict) -> list[tuple[float, float]]:
    try:
        from wenart.blender import looks as F
        found = F.piece_back_mid(bed)
    except ImportError:
        found = None
    if found is None:
        return []
    (bx, by), (dx, dy) = found
    fp = bed["footprint"]
    rot = float(fp.get("rotation_deg") or 0.0)
    front = float(bed.get("front_deg") or 0.0)
    local = (front - rot) % 360.0
    width = float(fp["size"][0]) if min(abs(local - 270.0), abs(local - 90.0)) < 45.0 else float(fp["size"][1])
    sx, sy = -dy, dx
    return [(bx + sx * width / 2.0, by + sy * width / 2.0), (bx - sx * width / 2.0, by - sy * width / 2.0)]


def accent_lights(building: dict, style: Optional[dict], new_id: Optional[Callable[[str], str]] = None) -> list[str]:
    """The statement fixture, the downlights and the bedside pendants (module docstring; in place). Returns notes."""
    from wenart.furniture import ceiling_lights as CL

    fam = family_of(style)
    rooms = _rooms(building)
    decor = building.setdefault("decor", [])
    notes = []
    for rid, room in sorted(rooms.items()):
        lights = _room_lights(building, rid)
        # 1. the statement fixture over the bed (bedrooms) or a single light over the dining table
        if fam in STATEMENT_FAMILIES:
            hosts = (_pieces(building, rid, ("bed_double",)) if room.get("room_type") == "bedroom" else
                     _pieces(building, rid, ("table_dining",)) if room.get("room_type") in ("living", "dining")
                     else [])
            # one statement fixture per room: over its largest bed or table
            hosts = sorted(hosts, key=lambda p: (-float(p["footprint"]["size"][0]) * float(p["footprint"]["size"][1]),
                                                 p["id"]))[:1]
            for host in hosts:
                over = [d for d in lights if host["id"] in (d.get("anchor_ids") or []) or _inside(host, _xy(d))]
                if len(over) != 1 or over[0].get("fixture"):
                    continue                             # a row of pendants stays a row
                d = over[0]
                d["fixture"] = "statement"
                what = "the statement fixture"
                if d["type"] == "ceiling_light" and host["type"] != "table_dining":
                    here, flat = _ceiling_over(building, d, STATEMENT_SIZE)
                    if here >= flat - 1e-6 and here - STATEMENT_BOTTOM_M >= PENDANT_MIN_DROP_M - 1e-9:
                        d.update(type="pendant_light", size=[*STATEMENT_SIZE, round(here - STATEMENT_BOTTOM_M, 3)],
                                 center=[*_xy(d), STATEMENT_BOTTOM_M])
                        what += " (a pendant in place of the flush light)"
                d["reason"] = f"{d.get('reason') or 'light'}; {what} over {host['type'].replace('_', ' ')} " \
                              f"{host['id']} (UL106)"
                _note(d, what)
                notes.append(f"{rid}: {d.get('id')} is {what} over {host['id']}")
        # 2. the general lights as recessed downlights
        if fam in DOWNLIGHT_FAMILIES and room.get("room_type") in DRESS_ROOM_TYPES + ("dining", "hall", "office"):
            for d in lights:
                if d.get("type") != "ceiling_light" or d.get("fixture") or d.get("anchor_ids") \
                        or d.get("rule") != getattr(CL, "RULE", "decor.ceiling_lights"):
                    continue
                here, flat = _ceiling_over(building, d, DOWNLIGHT_SIZE[:2])
                if here < flat - 1e-6:
                    continue                             # a light on the slope keeps its fixture
                d.update(fixture="downlight", size=list(DOWNLIGHT_SIZE),
                         center=[*_xy(d), round(flat - DOWNLIGHT_SIZE[2], 3)])
                d["reason"] = f"{d.get('reason') or 'light'}; as a recessed downlight (UL106)"
                _note(d, "recessed downlight")
                notes.append(f"{rid}: {d.get('id')} a recessed downlight")
        # 3. slim pendants over the nightstands of a double bed
        if fam in BEDSIDE_FAMILIES and room.get("room_type") == "bedroom" and new_id is not None:
            notes += _bedside_pendants(building, room, decor, new_id)
    return notes


def _bedside_pendants(building: dict, room: dict, decor: list[dict], new_id) -> list[str]:
    from wenart.blender import parametric as P

    notes = []
    stands = _pieces(building, room["id"], ("nightstand",))
    for bed in _pieces(building, room["id"], ("bed_double",)):
        corners = _head_corners(bed)
        mine = []
        for c in corners:
            s = min(stands, default=None, key=lambda p: G.distance(p["footprint"]["center"][:2], c))
            if s is not None and G.distance(s["footprint"]["center"][:2], c) <= NIGHTSTAND_REACH_M and s not in mine:
                mine.append(s)
        if len(mine) != 2:
            continue                                     # a pair, or none (symmetry)
        lamps = [d for d in decor if d.get("type") == "table_lamp" and d.get("host_id") in {s["id"] for s in mine}]
        if lamps:
            continue                                     # the table lamps are the bedside lights
        lights = _room_lights(building, room["id"])
        spots = [(float(s["footprint"]["center"][0]), float(s["footprint"]["center"][1])) for s in mine]
        if G.distance(*spots) < FIXTURE_GAP_M or any(G.distance(p, _xy(d)) < FIXTURE_GAP_M for p in spots
                                                    for d in lights):
            notes.append(f"{room['id']}: no bedside pendants at {bed['id']}: another ceiling fixture within "
                         f"{FIXTURE_GAP_M:g} m (the lights plan's spacing)")
            continue
        for s, p in zip(mine, spots):
            top = float(P.piece_bbox(s)[2])
            bottom = round(top + BEDSIDE_OVER_TOP_M, 3)
            here, flat = _ceiling_over(building, {"level_id": s["level_id"], "center": list(p), "rotation_deg": 0.0},
                                       BEDSIDE_SIZE)
            if here - bottom < 0.3:
                continue
            why = (f"a slim pendant hanging low over the nightstand {s['id']} beside the bed {bed['id']} "
                   f"(UL106: the professional reference's bedside lights)")
            decor.append({"id": new_id(s["level_id"]), "kind": "decor", "type": "pendant_light",
                          "level_id": s["level_id"], "room_id": room["id"], "asset": None, "host_id": None,
                          "anchor_ids": [s["id"]], "source": "added_by_ai", "method": "rule", "rule": RULE,
                          "slot": f"ceiling:bedside_{s['id']}", "colour": None, "confidence": 0.7, "status": "verified",
                          "fixture": "bedside", "evidence": _evidence(why), "reason": why,
                          "center": [round(p[0], 3), round(p[1], 3), bottom], "rotation_deg": 0.0,
                          "size": [*BEDSIDE_SIZE, round(here - bottom, 3)], "light_on": False})
            notes.append(f"{room['id']}: bedside pendant over {s['id']}")
    return notes


# --------------------------------------------------------------------------
# the pass and its review
# --------------------------------------------------------------------------

def dress(building: dict, style: Optional[dict], recipe_of: Optional[Callable] = None,
          new_id: Optional[Callable[[str], str]] = None) -> tuple[dict, list[str]]:
    """The whole pass (module docstring; in place): ``(building, notes)``; ``building["dressing"]`` records the
    rooms' finish decisions and the notes."""
    notes = []
    decisions = finish_decisions(building, style, recipe_of)
    notes += dress_curtains(building, style)
    notes += layer_bedding(building, style, new_id)
    notes += accent_lights(building, style, new_id)
    building["dressing"] = {"rule": RULE, "lesson": LESSON, "family": family_of(style) or None, "rooms": decisions,
                            "notes": notes}
    return building, notes


def review(built: dict, manifest: Optional[dict] = None, check: str = "U23") -> tuple[list[dict], int]:
    """What each built living room and bedroom of a fitting family still lacks against the professional bar
    (``(findings, rooms checked)``; pure): no feature panel where the family builds one and the decor stage did not
    turn it off, a wood floor not laid in the family's pattern (these two only on a built scene: ``manifest``, and
    the building as built), curtains in one layer, a bed whose throw lies in one layer. A finding: ``{check,
    severity, target, room_id, message, missing}``."""
    from wenart.blender import feature_walls as FW
    from wenart.blender import parquet as PQ

    style = {}
    if isinstance((manifest or {}).get("style_profile"), dict):
        style = manifest["style_profile"]
    fam = str(((built.get("dressing") or {}).get("family")) or style.get("family") or "").lower()
    if not fam:
        return [], 0
    decisions = (built.get("dressing") or {}).get("rooms") or {}
    panels = {o.get("room_id") for o in (manifest or {}).get("objects") or [] if o.get("detail") == "feature_wall"}
    pattern, _why = PQ.family_pattern(dict(style, family=fam)) if style else (PQ.FAMILY_FLOOR_PATTERNS.get(fam), "")
    out, n = [], 0
    for room in built.get("rooms") or []:
        rid, rt = room.get("id"), room.get("room_type")
        if rt not in DRESS_ROOM_TYPES:
            continue
        n += 1
        missing = []
        dec = decisions.get(rid) if isinstance(decisions.get(rid), dict) else {}
        spec, _w = FW.family_spec(dict(style, family=fam), rt)
        if spec is not None and dec.get("feature_wall", True) and manifest is not None and rid not in panels \
                and not room.get("feature_wall_skipped"):
            missing.append(f"no {spec['kind']} panel on the accent wall")
        if pattern and manifest is not None and rt in PQ.PATTERN_ROOM_TYPES and dec.get("floor_pattern", True) \
                and "floor_pattern" not in room \
                and (style.get("floor") or {}).get("material", "wood_oak_light") in PQ.PLANK_FLOOR_SLUGS:
            missing.append(f"the wood floor is not laid in {pattern}")
        curtains = [d for d in built.get("decor") or [] if d.get("room_id") == rid and d.get("type") == "curtain"]
        if fam not in NO_LAYER_FAMILIES and curtains and not any("sheer" in (d.get("layers") or ()) for d in curtains):
            missing.append("the curtains hang in one layer (no sheer)")
        beds = [f for f in built.get("furniture") or [] if f.get("room_id") == rid and f.get("type") in THROW_BEDS]
        for bed in beds:
            throws = [d for d in built.get("decor") or [] if d.get("type") == "throw" and d.get("host_id") == bed["id"]]
            if throws and not any(int(t.get("layers") or 1) >= 2 for t in throws):
                missing.append(f"the bed {bed['id']} has its throw in one layer")
        if missing:
            out.append({"check": check, "severity": "minor", "target": rid, "room_id": rid,
                        "message": f"{rid} ({rt}) falls short of the professional bar (UL106): " + "; ".join(missing),
                        "missing": missing, "lesson": LESSON})
    return out, n
