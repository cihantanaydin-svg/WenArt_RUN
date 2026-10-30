"""Argus, the lessons line: what the user taught us, measured by code on every project (28 Oct 2026, user: "All these
feedback needs to be understand by argus an Argus needs to be able to make these kind of corrections in the future
projects").

What (code, on the building as built and the scene manifest; one check per kind of problem the user pointed at, each
finding names its lesson in ``evidence.lesson`` and the fix Argus AI takes in ``fix``):

- U1 a site entrance (steps, a path, a canopy) at an opening that is no door (UL58: "Enterence to the window?");
- U2 an outdoor space under the building's roof that reaches over ``outdoor.SPACE["post_reach"]`` from the walls with
  no post under the roof's corner (UL57: "There is no column supporting the roof");
- U3 a drawn column built thicker than its outline on the column layer (UL57: "columns under is too thick");
- U4 a lower roof the roof plan draws over a space built flat (UL57: "no sloped roof next to the balcony");
- U5 a space's cover traced from its floor: no eaves past the posts, or a notch under 1 m in its outline (UL64: "This
  should not supposed to be 1 to one with what is under");
- U6 storage before a tall window (``group_checks.TALL_WINDOW_BLOCKERS`` within 0.30 m of a window whose sill is under
  0.45 m, over a quarter of its width; UL59: "If this is a full window this thing here closing the window"): the fix
  is the window's sill over the drawn piece (``raise_sill``), else the piece along its wall;
- U7 a door model that opens another way than drawn (``opening_models``; UL60: "This window / door should have been
  sliding as indicated in the plan");
- U8 a seat whose front faces a wall within 0.6 m (UL61: "Why this chair looking at the wall");
- U9 an indoor piece outdoors: a rug, a bed, a desk, upholstery or storage in an outdoor room or space (UL20: "makes
  no sense to have that table with the carpet outside");
- U10 a bathroom basin with no mirror over it ("Mirrors in the baths is missing sometimes"); 29 Oct 2026 (UL95: "this
  sink not making sense there") a basin under a window whose sill is under 1.25 m (``fixture_use.basins_under_windows``:
  no mirror can hang over it, its tap meets the sill), the placement rule the mirror rule (``decor_ai.basin_mirror``:
  over the basin on a solid wall, else beside it) and the architect's H2 share;
- U11 a kitchen worktop with no small appliance (kettle, microwave, coffee machine, toaster: "kettle in the kitchen
  microwave in the kitchen");
- U12 a dining table with nothing on it ("plates on tables for example");
- U13 a floor finish on a wall slot of the style (``exterior_checks.floor_texture``: "What kind of a kitchen is
  this");
- U14 a living room or bedroom with no accent wall in the scene: every wall one paint ("more stylish internal walls
  please better color");
- U15 the doors (``opening_models.door_variety_problems``): every door one model, an inside door model on the facade,
  no statement entrance ("I want better doors inside the house and the outside ... some variation is needed");
- U17 (29 Oct 2026; U16 is a Milestone 11 id of the reading) a desk or writing table (``tabletop.work_hosts``) with no
  work set on it, no laptop, monitor or keyboard (UL93: "Computer on the table would have been nice or a laptop"); a
  brief with decor off is not checked.
- U18 the door models as built (``opening_models.door_model_problems``, UL89: "Better door models needed"): more
  than a third of the house's doors parametric (naming the ones whose library model the build did not make), a door
  model named for another room ("bathroom door" on a bedroom).
- U21 / U22 (UL88) a gap between a light roof and the slab over the rest of its space; a thick post under a light roof.
- U24 (UL90, UL101) an inner window that makes no sense (``architect_rules.inner_window_reasons``).
- U25 (UL97) a wall read twice; a kitchen counter in a door's or a passage's approach.
- U26 (UL100) a house of two or more storeys left one render where its facade scheme clads the top storey.
- U28 (UL104) a window a stair's landing cuts across, or one over the stair's opening that starts far above the landing.
- U19 the rooms furnished for their use (``rooms_for_use``: the model review's M21, ``wenart.furniture.room_use``): a
  living room or the master bedroom without a TV ("There is no TV in the house"), an under-furnished living room ("a
  bit more furniture would be nice"), no bookshelf or a bookshelf without books ("no library and books"), a bathroom
  without storage ("bath is too empty"), a user-rejected model or a floor lamp at its plan symbol's size ("I did not
  like this light").
- U23 the professional bar of a living room or bedroom (``wenart.furniture.dressing.review``; UL106: "I want my renders
  to be as professional as these ones"): no feature panel on its accent wall where its style builds one, a wood floor
  not laid in its style's pattern, curtains in one layer, a bed's throw in one layer.
- U32 (UL113, UL115, UL119, 29 Oct 2026: "also take some inspiration from these photos", "look at all these details
  I want these details", "different solutions for different rooms"; ``wenart.furniture.room_schemes.review``, the
  model review's M28) two rooms of one type on a level with the same scheme, a hall with no console or wall niche, a
  bedroom with a bare bed wall.
- U16 a door or drawer front that cannot open, or an appliance that cannot be used (``fixture_use.blocked_fronts``: a
  washer, dishwasher, cooker, fridge or nightstand, or door-fronted storage, with less than its access depth free in
  front of it; UL92: "This washing machine would not open");
- U20 a piece whose back belongs on a wall standing parallel to it a drawing gap (0.055-0.15 m) off it
  (``fixture_use.back_gaps``; UL96: "There is a gap between wall and water faucet not looking good").
- U30 (UL114, UL123, UL124, 29 Oct 2026: the user's bathroom photos, "Look at the details in the toilet analyze
  implement into the projects") a wet room missing the set its style family gets (``wenart.furniture.bath_details.
  review``, the model review's M26): a WC without its paper holder or brush or not wall-hung in a wall-hung family, a
  basin without its mirror (of the family's kind) or, where the drawing has room, its vanity, a shower without its
  walk-in enclosure, a bathroom without a towel rail or a towel shelf or bar.
- U27 (UL109, 29 Oct 2026: "There are no chimneys there could be some chimney in the projects") a drawn fireplace,
  stove, flue or boiler room (``chimney.drawn_sources``) with no chimney on the roof (kind ``lost``); a house with a
  pitched roof whose style family usually has a chimney (``chimney.FAMILY_CHIMNEYS``) and no chimney in the scene.
- U33 (UL116, UL117, UL120, UL122, UL125, 29 Oct 2026: "not all the doors needs to be closed in default", "Not every
  single one of them with the same dimension", "Doors looks without frames they need frames", "this dressing could
  be a see through dressing room in the both sides argus should have think of this") the doors and the walk-ins as
  designed (``doors_as_designed``: the model review's M29): every inside door closed, all doors one size, an open
  leaf in a piece, a walk-in with closed fronts only (a design finding with the architect's D8 answer as its fix), a
  door without a frame and no frameless reason. Kind ``reference_missed`` (an open leaf in a piece: ``geometry``).
- U31 (UL115 kitchen part, UL118, 29 Oct 2026: "look at all these details I want these details") a kitchen missing what
  its style family's kitchen details give it (``wenart.blender.kitchen_details.review``, the model review's M27): a
  worktop bare beyond U11, a wall cabinet with no LED strip under it, an island hob without a hood, a family detail
  not built (a waterfall island, knee space for the stools), a kitchen with no fridge.
- U29 (UL112, 29 Oct 2026: "Also includes some power sockets and light on offs") the light switches and power sockets
  of the scene (``wall_plates.review``, the model review's M25 rule): a room with doors and no light switch at any of
  them, a bed with no socket beside it, a kitchen with no socket over its worktop, a plate on glass, inside an opening
  or behind a piece standing against its wall.
- U35 (UL134, UL139, 30 Oct 2026: "These things in front of a window needs fixing", "need to move the picture, TV
  hiding the picture not making sense") a wall item over an opening of its wall (with its frame and a margin), over
  another wall item, or behind a piece in front of its wall whose top reaches over its bottom (a TV on its unit), and a
  hung piece over an opening (``wenart.blender.wall_items.review``, the model review's M32). Kind ``no_sense``.
- U34 (UL121, 29 Oct 2026: "look how realistic the bed is looking full and nice I want this much detail in our
  models") a bed missing its style family's bedding (``wenart.blender.bedding_parts.review``, the model review's M30):
  fewer pillows than the family's set (shams, sleeping pillows, accent cushions, a lumbar), a free side whose duvet
  hangs short of the floor, an old dressing without the set, a made-up model measured poorer than ours left as it was,
  no throw, a throw without its woven pattern or its fringe. Kind ``taste``.
- U36 (UL131, UL140, 30 Oct 2026: "I did not like these sofa models", "I like this sofa but it needs more details,
  also the gaps need a rework") a library soft seat as built (``wenart.blender.soft_seats.review``, the model review's
  M33): in flat export colours (no fabric weave), with its parts apart, faceted (the file's smooth shading lost) or a
  poor model (a 256 px texture, flat, double-sided and coarse: the best that fitted). Kind ``taste`` (parts apart:
  ``detached``). A model the user rejected is U19's.
  no throw, a throw without its woven pattern or its fringe. Kind ``taste``. 30 Oct 2026 (UL136 "I did not like this
  bed", UL137 "head section of this bed needs a rework", UL146 the P14 bed): a lumpy duvet or blanket, a wavy hem
  (``bedding_parts.cover_smoothness`` as built), a gap between the mattress and the headboard left open.
- U38 (UL153, 30 Oct 2026, photo P16: "salon inspiration") a living or dining room missing what its style family takes
  from P16 (``wenart.furniture.salon_details.review``, the model review's M34): a sofa group or a dining set with no
  rug under it, a dining print under half the table's length, loose pendants over the table where the scheme asks one
  fixture, a dining table without its centrepiece set, a low wall-backed TV unit standing on the floor, a TV wall
  without its lit niches and no reason recorded, a near-square coffee table not a round drum. Kind ``taste``.

How: pure functions of the building (``inp.stage("build")`` or the final one) and the manifest; a check whose data is
missing is listed in ``checked`` as not run, never as clean. Every lesson without a code check is asked by Argus AI's
lesson walk (``lesson_questions``: its question on the floor's top-down view and the renders, check ``AI5``), so a new
lesson is asked from the day it is added; ``coverage()`` says which lessons each way covers.

Why: CLAUDE.md: "Every new request or correction of the user becomes a lesson"; a lesson only prevents the next
problem when something looks for it on every run and routes it to the fix that removes it.
"""
from __future__ import annotations

import math
from typing import Optional

from wenart.audit import kinds as K

LINE = "lessons"
WALL_FACE_M = 0.6              # U8: a seat's front this close to a wall faces it
TALL_SILL_M = 0.45             # U6: = group_checks.TALL_WINDOW_SILL_M
WINDOW_DEPTH_M = 0.30          # U6: the window's band into the room (= G12)
COVER_SHARE = 0.25             # U6: = group_checks.TALL_WINDOW_COVER_MAX
NOTCH_M = 1.0                  # U5: a notch narrower than this in a cover's outline is traced, not designed
CORE_TOL_M = 0.05              # U3
OUTDOOR_ROOM_TYPES = ("terrace", "balcony", "veranda", "porch", "loggia", "deck", "patio", "garden")
INDOOR_ONLY = ("rug", "bed", "bed_double", "bed_single", "desk", "office_chair", "wardrobe", "dresser", "bookcase",
               "tv_unit", "nightstand", "sofa", "sofa_l", "armchair", "chest_of_drawers", "sideboard")
OUTDOOR_WORDS = ("outdoor", "garden", "patio", "teak", "rattan", "wicker", "metal", "aluminium", "aluminum")
SEATS = ("armchair", "sofa", "sofa_l", "lounge_chair", "accent_chair", "chaise_longue", "bench")
SMALL_APPLIANCES = ("kettle", "microwave", "coffee_machine", "toaster", "espresso_machine")
TABLE_DECOR_TYPES = ("plate", "plates", "table_setting", "place_setting", "bowl", "fruit_bowl", "vase", "runner",
                     "table_runner", "candle", "candles", "tray", "glass", "glasses", "centrepiece")
DINING_TABLES = ("table_dining", "dining_table")
WORK_PIECES = ("laptop", "monitor", "keyboard")       # U17: a desk's work set (tabletop.WORK_TYPES but the mouse)
BASINS = ("washbasin", "vanity", "basin")
WET_TYPES = ("bathroom", "wc", "toilet", "shower_room", "ensuite")


def _f(check: str, severity: str, target, message: str, lesson: str, fix: str, **evidence) -> dict:
    return K.finding(LINE, check, severity, target, message, evidence=dict(evidence, lesson=lesson), fix=fix)


def _poly(piece: dict):
    from wenart.furniture import fixture_seat as FS
    from shapely.geometry import Polygon

    fp = piece.get("footprint") or {}
    if not fp.get("center") or not fp.get("size"):
        return None
    return Polygon(FS.footprint_rect(fp))


def _rooms(building: dict) -> dict:
    return {r["id"]: r for r in building.get("rooms") or [] if r.get("id")}


def _built(building: dict) -> list[dict]:
    return [f for f in building.get("furniture") or [] if f.get("build") is not False and f.get("footprint")]


# ----------------------------------------------------------------------------------------------------- the site
def entrances_at_windows(building: dict) -> list[dict]:
    """U1."""
    ops = {o["id"]: o for o in building.get("openings") or [] if o.get("id")}
    out = []
    for e in (building.get("site") or {}).get("entrances") or []:
        oid = e.get("door_id") or e.get("opening_id")
        o = ops.get(oid)
        if o is not None and o.get("type") != "door":
            out.append(_f("U1", "major", oid, f"an entrance (steps, path, canopy) at {oid}, which is a {o.get('type')}",
                          "UL58", "rerun_stage site (record_entrances keeps doors only)", opening=oid))
    return out


def _spaces(building: dict) -> list[dict]:
    return [s for s in (building.get("site") or {}).get("outdoor_spaces") or [] if isinstance(s, dict)]


def roofs_without_posts(building: dict) -> list[dict]:
    """U2."""
    from shapely.geometry import Point, Polygon
    from wenart.levels import outdoor as O

    walls = {}
    for w in building.get("walls") or []:
        walls.setdefault(w.get("level_id"), []).append(w)
    out = []
    for sp in _spaces(building):
        if sp.get("cover_source") != "building_roof" or len(sp.get("polygon") or []) < 3:
            continue
        if any("roof" in str(q.get("carries")) for q in sp.get("posts") or []) or sp.get("columns"):
            continue
        from shapely.geometry import LineString
        lines = [LineString([w["start"], w["end"]]) for w in walls.get(sp.get("level_id")) or []
                 if w.get("start") and w.get("end")]
        if not lines:
            continue
        far = [p for p in Polygon(sp["polygon"]).exterior.coords
               if min(ln.distance(Point(p)) for ln in lines) > O.SPACE["post_reach"]]
        if far:
            out.append(_f("U2", "major", sp["id"], f"the building's roof reaches {len(far)} corner(s) of {sp['id']} "
                          f"over {O.SPACE['post_reach']:g} m from the walls with no post under it", "UL57",
                          "architect cover_space (posts at the far corners)", corners=[list(p) for p in far]))
    return out


def thick_columns(building: dict) -> list[dict]:
    """U3: a drawn column built bigger than its own column-layer outline."""
    from wenart.levels import outdoor as O

    out = []
    items = list((building.get("site") or {}).get("decor") or [])
    for sp in _spaces(building):
        items += [c for c in sp.get("columns") or [] if isinstance(c, dict)]
    seen = set()
    for c in items:
        if c.get("inferred_as") not in (None, "column") or not c.get("evidence"):
            continue
        core = O.core_box(c)
        if core is None or c.get("id") in seen:
            continue
        seen.add(c.get("id"))
        built = float(c.get("size_m") or O.column_look(c)["size_m"])
        want = max(float(x) for x in core["size"])
        if built > want + CORE_TOL_M:
            out.append(_f("U3", "major", c.get("id"), f"column {c.get('id')} built {built:.2f} m, its outline on the "
                          f"column layer is {want:.2f} m", "UL57", "rerun_stage levels (outdoor.column_look)",
                          built_m=built, core_m=want))
    return out


def flat_drawn_roofs(building: dict) -> list[dict]:
    """U4."""
    out = []
    for sp in _spaces(building):
        r = sp.get("roof") or {}
        if r.get("drawn") and r.get("kind") != "pitched" and "would slope only" not in str(r.get("reason")):
            out.append(_f("U4", "major", sp["id"], f"the roof plan draws a lower roof over {sp['id']}; it was built "
                          f"as a {r.get('kind')}", "UL57", "rerun_stage levels (outdoor.roof_plan pitched)"))
    return out


def traced_covers(building: dict) -> list[dict]:
    """U5: a cover with no eaves past its floor, or a notch narrower than ``NOTCH_M`` in its outline."""
    from shapely.geometry import Polygon

    out = []
    for sp in _spaces(building):
        r = sp.get("roof") or {}
        if r.get("kind") not in ("light_roof", "glass_roof", "pergola") or len(r.get("polygon") or []) < 3:
            continue
        roof = Polygon(r["polygon"])
        why = []
        if float(r.get("roof_area_m2") or roof.area) <= float(r.get("area_m2") or 0.0) + 0.05:
            why.append("no eaves past the posts")
        closed = roof.buffer(NOTCH_M / 2.0, join_style=2).buffer(-NOTCH_M / 2.0, join_style=2)
        if closed.area - roof.area > 0.02:
            why.append(f"{closed.area - roof.area:.2f} m² of notches under {NOTCH_M:g} m in its outline")
        if why:
            out.append(_f("U5", "major", sp["id"], f"the roof of {sp['id']} is traced from its floor: "
                          + "; ".join(why), "UL64", "rerun_stage levels (outdoor.cover_shape)"))
    return out


# ------------------------------------------------------------------------------------------------- the rooms
def storage_before_tall_windows(building: dict) -> list[dict]:
    """U6."""
    from shapely.geometry import LineString
    from wenart.furniture import group_checks as GC

    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("id")}
    out = []
    pieces = [f for f in _built(building) if str(f.get("type")) in GC.TALL_WINDOW_BLOCKERS]
    for o in building.get("openings") or []:
        if o.get("type") != "window" or not o.get("center"):
            continue
        sill = o.get("sill_height", o.get("sill"))
        if sill is None or float(sill) >= TALL_SILL_M:
            continue
        w = walls.get(o.get("wall_id"))
        if w is None:
            continue
        dx, dy = w["end"][0] - w["start"][0], w["end"][1] - w["start"][1]
        ln = math.hypot(dx, dy) or 1.0
        ux, uy = dx / ln, dy / ln
        half = float(o.get("width") or 0.0) / 2.0
        c = o["center"]
        seg = LineString([(c[0] - ux * half, c[1] - uy * half), (c[0] + ux * half, c[1] + uy * half)])
        band = seg.buffer(WINDOW_DEPTH_M + float(w.get("thickness") or 0.2) / 2.0, cap_style=2)
        for f in pieces:
            if f.get("level_id") != o.get("level_id"):
                continue
            poly = _poly(f)
            if poly is None or not poly.intersects(band):
                continue
            proj = [(x - c[0]) * ux + (y - c[1]) * uy for x, y in poly.exterior.coords]
            cover = max(0.0, min(max(proj), half) - max(min(proj), -half))
            if half > 0 and cover / (2 * half) >= COVER_SHARE:
                out.append(_f("U6", "major", o["id"], f"{f['id']} ({f.get('type')}) closes {cover / (2 * half):.0%} "
                              f"of the tall window {o['id']} (sill {float(sill):.2f} m)", "UL59",
                              f"architect raise_sill {o['id']} (the sill over the drawn piece), else move_piece "
                              f"{f['id']} along its wall", piece=f["id"]))
    return out


def door_operations(building: dict, manifest: Optional[dict]) -> list[dict]:
    """U7."""
    from wenart.blender import opening_models as OM

    if not manifest:
        return []
    ops = {o["id"]: o for o in building.get("openings") or [] if o.get("id")}
    out = []
    for ob in manifest.get("objects") or []:
        lm = ob.get("library_model") if isinstance(ob.get("library_model"), dict) else None
        o = ops.get(ob.get("element_id"))
        if lm is None or o is None or o.get("type") != "door":
            continue
        want = OM.opening_operation(o)
        got = OM.model_operation(lm)
        if want and got and want != got:
            out.append(_f("U7", "major", o["id"], f"{o['id']} is drawn {want}; its model {lm.get('title')!r} is "
                          f"{got}", "UL60", "rerun_stage build (opening_models.operation_fit)",
                          model=lm.get("asset_id")))
    return out


def seats_facing_walls(building: dict) -> list[dict]:
    """U8."""
    from shapely.geometry import LineString, Point
    from wenart.furniture import group_checks as GC
    from wenart.furniture import placer

    out = []
    rooms = _rooms(building)
    for f in _built(building):
        if str(f.get("type")) not in SEATS or f.get("front_deg") is None:
            continue
        room = rooms.get(f.get("room_id"))
        if room is None or len(room.get("polygon") or []) < 3:
            continue
        piece = placer.drawn_piece(f)
        fx, fy = GC.front_vec(piece)
        depth = float(f["footprint"]["size"][1]) / 2.0
        c = f["footprint"]["center"]
        front = (c[0] + fx * depth, c[1] + fy * depth)
        ray = LineString([front, (front[0] + fx * WALL_FACE_M, front[1] + fy * WALL_FACE_M)])
        ring = LineString(list(room["polygon"]) + [room["polygon"][0]])
        if ring.intersects(ray):
            d = ring.distance(Point(front))
            out.append(_f("U8", "major", f["id"], f"{f['id']} ({f.get('type')}) faces a wall {d:.2f} m in front of it",
                          "UL61", f"rotate_piece {f['id']} (into the room, towards its partner)"))
    return out


def indoor_pieces_outdoors(building: dict) -> list[dict]:
    """U9."""
    out = []
    rooms = _rooms(building)
    outdoor_rooms = {rid for rid, r in rooms.items() if str(r.get("room_type")) in OUTDOOR_ROOM_TYPES}
    for f in list(_built(building)) + [d for d in building.get("decor") or [] if d.get("type") == "rug"]:
        if f.get("room_id") not in outdoor_rooms or str(f.get("type")) not in INDOOR_ONLY:
            continue
        title = str(((f.get("asset") or {}) if isinstance(f.get("asset"), dict) else {}).get("title") or "").lower()
        if any(w in title for w in OUTDOOR_WORDS):
            continue
        fid = f.get("id")
        out.append(_f("U9", "major", fid, f"{fid} ({f.get('type')}) is an indoor piece in the outdoor room "
                      f"{f.get('room_id')}", "UL20", f"remove_piece {fid} (or swap_model to an outdoor model)"))
    return out


def _decor_by_room(building: dict) -> dict:
    out: dict = {}
    for d in building.get("decor") or []:
        out.setdefault(d.get("room_id"), []).append(d)
    return out


def basins_without_mirrors(building: dict) -> list[dict]:
    """U10."""
    rooms = _rooms(building)
    decor = _decor_by_room(building)
    out = []
    for rid, r in rooms.items():
        if str(r.get("room_type")) not in WET_TYPES:
            continue
        here = [f for f in _built(building) if f.get("room_id") == rid]
        if not any(str(f.get("type")) in BASINS for f in here):
            continue
        if any(str(x.get("type")) == "mirror" for x in here + decor.get(rid, [])):
            continue
        out.append(_f("U10", "major", rid, f"{rid} has a basin and no mirror over it", "UL66",
                      f"complete_group {rid} (a mirror over the basin)"))
    # 29 Oct 2026 (UL95, user on real06: "this sink not making sense there"): a basin under a low window has no wall
    # for its mirror and its tap meets the sill; the architect's H2 moves it (at most 0.5 m) or raises the sill
    from wenart.furniture import fixture_use as FU

    for r in FU.basins_under_windows(building):
        out.append(_f("U10", "major", r["piece"], r["message"], "UL95",
                      f"architect clear_basin {r['piece']} (at most 0.5 m to a solid wall), else basin_sill "
                      f"{r['window']} (its sill to {FU.BASIN_SILL_M:.2f} m where the documents do not give it)",
                      window=r["window"], sill_m=r["sill_m"]))
    return out


def blocked_fronts(building: dict) -> list[dict]:
    """U16 (29 Oct 2026, UL92: "This washing machine would not open"): ``fixture_use.blocked_fronts``."""
    from wenart.furniture import fixture_use as FU

    return [_f("U16", r["problem"]["severity"], r["piece"], r["message"], "UL92",
               f"rotate_piece {r['piece']} (to its free side, its back on a wall), else move what stands in front of "
               f"it ({', '.join(r['problem']['blockers'][:3]) or 'the wall'})", free_m=r["problem"]["free_m"],
               blockers=r["problem"]["blockers"])
            for r in FU.blocked_fronts(building)]


def back_gaps(building: dict) -> list[dict]:
    """U20 (29 Oct 2026, UL96: "There is a gap between wall and water faucet not looking good"):
    ``fixture_use.back_gaps``."""
    from wenart.furniture import fixture_use as FU

    return [_f("U20", "major", r["piece"], r["message"], "UL96",
               f"move_piece {r['piece']} with snap_wall_id (its back onto its wall)", gap_m=r["gap_m"])
            for r in FU.back_gaps(building)]


def bare_worktops(building: dict) -> list[dict]:
    """U11."""
    rooms = _rooms(building)
    decor = _decor_by_room(building)
    out = []
    for rid, r in rooms.items():
        here = [f for f in _built(building) if f.get("room_id") == rid]
        if not any(str(f.get("type")) == "kitchen_counter" for f in here):
            continue
        if any(str(x.get("type")) in SMALL_APPLIANCES for x in here + decor.get(rid, [])):
            continue
        out.append(_f("U11", "minor", rid, f"the kitchen worktop of {rid} holds no small appliance (kettle, "
                      f"microwave, coffee machine)", "UL66", "agent_round (dress the kitchen worktop)"))
    return out


def bare_dining_tables(building: dict) -> list[dict]:
    """U12."""
    hosted = {d.get("host_id") for d in building.get("decor") or [] if str(d.get("type")) in TABLE_DECOR_TYPES}
    out = []
    for f in _built(building):
        if str(f.get("type")) in DINING_TABLES and f.get("id") not in hosted:
            out.append(_f("U12", "minor", f["id"], f"the dining table {f['id']} has nothing on it (no plates, bowl or "
                          f"vase)", "UL66", f"agent_round (a table setting on {f['id']})"))
    return out


def bare_desks(building: dict) -> list[dict]:
    """U17 (29 Oct 2026, lesson UL93): every desk and writing table of the decor rule (``tabletop.work_hosts``: a desk,
    a table with an office chair at it, a home office's table) that holds no work piece (``WORK_PIECES``)."""
    from wenart.furniture import decor_ai as DA
    from wenart.furniture import tabletop as TT

    if DA.decor_mode(building) == "off":
        return []
    hosted = {d.get("host_id") for d in building.get("decor") or [] if str(d.get("type")) in WORK_PIECES}
    by_room: dict = {}
    for f in _built(building):
        by_room.setdefault(f.get("room_id"), []).append(f)
    out = []
    for rid, room in _rooms(building).items():
        for host in TT.work_hosts(room, by_room.get(rid, [])):
            if host.get("id") in hosted:
                continue
            seat = TT.seat_at(host, by_room.get(rid, []))
            out.append(_f("U17", "minor", host["id"], f"the {host.get('type')} {host['id']} in {rid} has no laptop or "
                          f"computer on it" + (f" (its seat {seat[0]['id']} faces nothing)" if seat else ""), "UL93",
                          f"agent_round (the work set of {host['id']}: a laptop on it facing its seat, "
                          f"tabletop.work_set)", seat=seat[0]["id"] if seat else None))
    return out


def _profile_slots(manifest: Optional[dict]) -> dict:
    """``{slot: look}`` of the scene's style profile: the interior slots and the exterior ones (``exterior``)."""
    sp = (manifest or {}).get("style_profile") if isinstance((manifest or {}).get("style_profile"), dict) else {}
    out = {k: v for k, v in sp.items() if isinstance(v, dict) and ("material" in v or "asset" in v)}
    for k, v in (sp.get("exterior") or {}).items():
        if isinstance(v, dict):
            out[k] = v
    return out


def floor_finish_on_walls(manifest: Optional[dict]) -> list[dict]:
    """U13: the style's upright slots against a floor texture (``exterior_checks.floor_texture``)."""
    from wenart.blender import exterior_checks as X

    out = []
    for slot, look in _profile_slots(manifest).items():
        if slot in X.UPRIGHT_SLOTS and X.floor_texture(look):
            out.append(_f("U13", "major", slot, f"the {slot} slot is clad in a floor finish ({look.get('material')}, "
                          f"{look.get('asset')})", "UL66", f"set_material {slot} (a wall finish of the style)"))
    return out


def plain_walls(building: dict, manifest: Optional[dict]) -> list[dict]:
    """U14: a living room or bedroom with no accent wall in the scene (the manifest marks accent faces: ``accent``,
    ``room_ids``; ``looks.accent_walls`` paints one per such room, the style family's colour when the brief names
    none)."""
    if not (manifest or {}).get("objects"):
        return []
    marked = {rid for o in manifest["objects"] if o.get("kind") == "wall" and o.get("accent")
              for rid in o.get("room_ids") or []}
    out = []
    for r in building.get("rooms") or []:
        if r.get("room_type") in ("living", "bedroom") and r.get("id") not in marked:
            out.append(_f("U14", "minor", r["id"], f"{r['id']} ({r.get('room_type')}) has no accent wall: every wall "
                          f"one paint", "UL66", "set_material wall_accent (the style family's accent colour)"))
    return out


def door_variety(manifest: Optional[dict]) -> list[dict]:
    """U15: the doors of the house as a designer chooses them (``opening_models.door_variety_problems``: every door
    one model, an inside door model on the facade, no statement entrance; user: "I want better doors inside the house
    and the outside ... some variation is needed")."""
    from wenart.blender import opening_models as OM

    if not (manifest or {}).get("objects"):
        return []
    return [_f("U15", p.get("severity") or "major", p.get("target") or "doors", str(p.get("message")), "UL65",
               "rerun_stage build (opening_models: families by role)", problem=p.get("kind"))
            for p in OM.door_variety_problems(manifest)]


# ------------------------------------------------------------------------------- 29 Oct 2026 (the user's real06 review)
def roof_gaps(building: dict) -> list[dict]:
    """U21: a covered outdoor space with part of its floor left open between its own roof and the slab or roof over the
    rest ("there is a gap between balcony and small roof there should not be a gap"): the floor under neither its
    roof, a space above nor a floor above, wider than ``outdoor.SLIVER_M``."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    from wenart.levels import outdoor as O

    spaces = _spaces(building)
    out = []
    for sp in spaces:
        roof = sp.get("roof") if isinstance(sp.get("roof"), dict) else None
        if roof is None or len(roof.get("polygon") or []) < 3 or len(sp.get("polygon") or []) < 3:
            continue
        floor = Polygon(sp["polygon"]).buffer(0)
        over = [Polygon(roof["polygon"]).buffer(0)]
        over += [Polygon(u["polygon"]).buffer(0) for u in spaces if u is not sp and len(u.get("polygon") or []) >= 3
                 and float(u.get("z") or 0.0) > float(sp.get("z") or 0.0) + 1.0]
        rest = floor.difference(unary_union(over))
        rest = rest.buffer(-O.SLIVER_M / 2.0, join_style=2).buffer(O.SLIVER_M / 2.0, join_style=2)
        if rest.is_empty or rest.area < 0.5:
            continue
        others = [u["id"] for u in spaces if u is not sp and len(u.get("polygon") or []) >= 3
                  and float(u.get("z") or 0.0) > float(sp.get("z") or 0.0) + 1.0
                  and Polygon(u["polygon"]).buffer(0.3).intersects(rest)]
        if others:
            out.append(_f("U21", "major", sp["id"], f"{rest.area:.1f} m² of {sp['id']} lie open between its roof and "
                          f"the slab of {', '.join(others)} over the rest (a gap)", "UL88",
                          "rerun_stage levels (outdoor.roof_plan: the space's roof runs on to the slab it meets)",
                          gap_m2=round(rest.area, 2), above=others))
    return out


def thick_light_posts(building: dict) -> list[dict]:
    """U22: an inferred post that carries only a light or lower roof, thicker than ``outdoor.LIGHT_POST_M`` ("columns
    are too thick")."""
    from wenart.levels import outdoor as O

    out = []
    for sp in _spaces(building):
        for q in sp.get("posts") or []:
            if q.get("source") != "inferred" or not str(q.get("carries") or "").startswith("the roof of"):
                continue
            size = float(q.get("size_m") or 0.0)
            if size > O.LIGHT_POST_M + 0.02:
                out.append(_f("U22", "major", sp["id"], f"a post of {sp['id']}'s light roof is {size:.2f} m across "
                              f"(a light roof's post is at most {O.LIGHT_POST_M:.2f} m)", "UL88",
                              "rerun_stage levels (outdoor.light_post_look)", center=q.get("center"), size_m=size))
    return out


def senseless_inner_windows(building: dict) -> list[dict]:
    """U24: a window between two rooms that makes no sense (``architect_rules.inner_window_problems``: a wet room
    behind it, a door beside it, a tall piece against it, a bedroom lit from both sides; "these windows are not making
    sense", "This window and dolap is not making sense"); a serving hatch over a counter is none."""
    from wenart.blender import architect_actions as AA
    from wenart.blender import architect_rules as AR

    plan = AA.Plan(building)
    out, glass = [], {}
    for o in plan.openings.values():
        if o.get("type") != "window" or (o.get("interior_glazing") or {}).get("kind") == "pass_through":
            continue
        sides = AA.window_sides(plan, o)
        if len(sides) != 2 or any(r is None or AA.Plan.is_outside(r) for r in sides):
            continue
        reasons = AR.inner_window_reasons(plan, o, sides[0], sides[1], glass)
        why = [] if AR.inner_window_soft(plan, reasons, sides[0], sides[1], glass) else [t for _k, t in reasons]
        if why:
            out.append(_f("U24", "major", o["id"], f"{o['id']} between {sides[0]['id']} and {sides[1]['id']}: "
                          + "; ".join(why), "UL90", "architect close_window", rooms=[sides[0]["id"], sides[1]["id"]]))
    return out


def read_twice_and_blocked_passages(building: dict) -> list[dict]:
    """U25: a wall read twice (``ingest.generic.twin_walls``) and a kitchen counter across a door or an open passage
    (``reading.passage_zone``; "I am not understanding this scene is there a door behind it?")."""
    from wenart.ingest.generic import reading as RD
    from wenart.ingest.generic import twin_walls as TW

    out = []
    walls = [w for w in building.get("walls") or [] if w.get("id") and w.get("start") and w.get("end")]
    for i, a in enumerate(walls):
        for c in walls[i + 1:]:
            if TW.twin_of(a, c):
                keep, dup = (a, c) if TW._rank(a) >= TW._rank(c) else (c, a)
                if TW._axis(dup)[2] >= TW.MIN_COPY_M and \
                        float(dup.get("thickness") or 0.0) <= float(keep.get("thickness") or 0.0) + TW.THICKER_TOL_M:
                    out.append(_f("U25", "major", dup["id"], f"{dup['id']} lies in {keep['id']}: one wall read twice",
                                  "UL97", "rerun_stage reading (twin_walls.merge_twin_walls)", kept=keep["id"]))
    zones: dict = {}
    for f in _built(building):
        if f.get("type") not in ("kitchen_counter", "kitchen_island", "sink_kitchen"):
            continue
        lv = f.get("level_id")
        if lv not in zones:
            zones[lv] = RD.passage_zone(building, lv, reach=0.0)      # a counter ending at the jamb is no block
        zone, poly = zones[lv], _poly(f)
        if zone is None or poly is None or zone.is_empty:
            continue
        inter = poly.intersection(zone).area
        if inter > 0.05:
            out.append(_f("U25", "major", f["id"], f"{f['id']} ({f.get('type')}) stands across a door's or a passage's "
                          f"approach ({inter:.2f} m²)", "UL97",
                          "rerun_stage reading (kitchen_outlines: a leg stops short of a door)", overlap_m2=round(inter, 2)))
    return out


def stair_windows(building: dict) -> list[dict]:
    """U28: a window a stair's half landing or winders cut across, or a window over the stair's opening that starts far
    above the landing (``architect_rules.stair_window_findings``; "If there is a window here it needs to alight with
    the stairs")."""
    from wenart.blender import architect_actions as AA
    from wenart.blender import architect_rules as AR

    return [_f("U28", "major" if f["kind"] == "cut" else "minor", f["window"], f"{f['window']}: {f['why']}", "UL104",
               "architect W6 (stair_window / close_stair_window)", stair=f.get("stair"), level=f.get("level_id"))
            for f in AR.stair_window_findings(AA.Plan(building))]


def one_render_facades(building: Optional[dict], manifest: Optional[dict]) -> list[dict]:
    """U26: a house of two or more storeys whose facade scheme (the style family's default; no drawing or brief names
    the facade) has an upper-storey cladding that the build did not put on ("Outside wall texture can be changed")."""
    import re

    from wenart.blender import facade as FA

    assumed = [a for a in (manifest or {}).get("assumed") or [] if isinstance(a, dict)]
    look = next((a for a in assumed if a.get("object") == "exterior" and a.get("field") == "facade"), None)
    fam = re.match(r"facade scheme \(([^)]*)\)", str((look or {}).get("reason") or ""))
    if fam is None or (building or {}).get("facade", {}).get("faces"):
        return []                                  # the drawings or the brief name the facade
    top = FA.upper_level(FA.scheme_of({"family": fam.group(1)}), (building or {}).get("levels") or [])
    if top is None or any(a.get("field") == "facade_scheme" and a.get("object") == top["id"] for a in assumed):
        return []
    sch = FA.scheme_of({"family": fam.group(1)})
    return [_f("U26", "major", top["id"], f"every storey of the house is one {look.get('value')}: the top storey "
               f"{top['id']} has no {sch['upper']} ({sch['family']} facade scheme)", "UL100",
               "rerun_stage build (facade.scheme_faces: the top storey's cladding)")]


def _family_of(manifest: Optional[dict]) -> Optional[str]:
    """The style family of a scene (its style profile, else its facade scheme's reason, else its chimney plan)."""
    import re

    m = manifest or {}
    fam = (m.get("style_profile") or {}).get("family") if isinstance(m.get("style_profile"), dict) else None
    if fam:
        return str(fam)
    for a in m.get("assumed") or []:
        hit = re.match(r"facade scheme \(([^)]*)\)", str(a.get("reason") or "")) if isinstance(a, dict) else None
        if hit:
            return hit.group(1)
    return ((m.get("whole_building") or {}).get("chimneys") or {}).get("family")


def missing_chimneys(building: Optional[dict], manifest: Optional[dict]) -> list[dict]:
    """U27 (lesson UL109, user on real06 run 20261028-154514-full: "There are no chimneys there could be some chimney
    in the projects"): a drawn fireplace, stove, flue or boiler room (``chimney.merged_sources``) that no chimney of the
    scene serves (its id in a chimney's sources, else a chimney within reach of it; kind ``lost``); a house with a
    pitched roof whose style family usually has a chimney (``chimney.family_rule``) and no chimney on the roof."""
    from wenart import geometry as G
    from wenart.blender import chimney as CH

    objs = [o for o in (manifest or {}).get("objects") or [] if isinstance(o, dict) and o.get("detail") == "chimney"]
    built = [o.get("chimney") or {} for o in objs]
    served = {str(s.get("id")) for c in built for s in c.get("sources") or [] if s.get("id")}
    reach = CH.CHIMNEY["snap_m"] + CH.CHIMNEY["nudge_m"][-1] + CH.CHIMNEY["merge_m"]
    out = []
    for group in CH.merged_sources(building or {}):
        s = group[0]
        if any(str(x.get("id")) in served for x in group if x.get("id")):
            continue
        if s.get("center") and any(c.get("center") and G.distance(c["center"], s["center"]) <= reach for c in built):
            continue
        what = s["kind"].replace("_", " ")
        out.append(K.finding(LINE, "U27", "major", s.get("id") or s.get("room_id") or "roof",
                             f"the drawn {what} {s.get('id')} ({s.get('text')!r}, {s.get('what')} on "
                             f"{s.get('level_id')}) has no chimney on the roof",
                             evidence={"lesson": "UL109", "source": s.get("id"), "kind": s["kind"]},
                             fix="rerun_stage build (chimney.plan: a drawn fireplace or flue gets its stack through "
                                 "the roof)", kind="lost"))
    if built or out:
        return out
    roof = (building or {}).get("roof") if isinstance((building or {}).get("roof"), dict) else {}
    built_roof = ((manifest or {}).get("whole_building") or {}).get("roof") or {}
    rtype = built_roof.get("type") or roof.get("type")
    if rtype in (None, "flat") or roof.get("kind") == "flat_cut":
        return out
    fam = CH.family_rule(_family_of(manifest))
    if not fam["chimney"]:
        return out
    return [_f("U27", "major", "roof", f"a {rtype} roof on a {fam['family']} house with no chimney ({fam['why']}): "
               "nothing on the roof says fire or flue", "UL109",
               "rerun_stage build (chimney.plan: the family's inferred chimney over the living room's fireplace wall)",
               family=fam["family"], roof=rtype)]


PLATE_NO_SENSE = ("on_glass", "in_opening", "behind_piece", "off_wall")


def wall_plates(building: Optional[dict], manifest: Optional[dict]) -> list[dict]:
    """U29 (lesson UL112, user on real06 run 20261029-100801-full: "Also includes some power sockets and light on
    offs"): the scene's light switches and power sockets (its objects of detail ``wall_plates``) against the building
    as built, by the model review's M25 rule (``wall_plates.review``): a room with doors and no switch, a bed with no
    socket beside it, a kitchen with no socket over its worktop (kind ``taste``); a plate on glass, inside an opening or
    behind a piece against its wall (kind ``no_sense``)."""
    from wenart.blender import wall_plates as WP

    problems, _n = WP.review(building or {}, WP.plates_of(manifest))
    out = []
    for p in problems:
        nums = {k: v for k, v in p.items() if k not in ("problem", "severity", "message", "target", "room_id")}
        out.append(K.finding(LINE, "U29", p["severity"], p["target"], p["message"],
                             evidence=dict(nums, lesson="UL112", problem=p["problem"], room=p.get("room_id")),
                             fix="rerun_stage build (wall_plates.plan_level: a switch on the latch side of every room "
                                 "door, sockets beside the beds, at the desk and the TV, over the worktop, by the "
                                 "bathroom mirror)",
                             kind="no_sense" if p["problem"] in PLATE_NO_SENSE else None))
    return out


def door_models(building: Optional[dict], manifest: Optional[dict]) -> list[dict]:
    """U18: the door models as built (``opening_models.door_model_problems``; lesson UL89, user: "Better door models
    needed"): more than a third of the house's doors parametric (real06 run 20261028-154514-full: the build refused
    the HSSD doors the plan chose), a door named for another room ("bathroom door" on the bedrooms of real04)."""
    from wenart.blender import opening_models as OM

    if not (manifest or {}).get("objects"):
        return []
    return [_f("U18", p.get("severity") or "major", p.get("target") or "doors", str(p.get("message")), "UL89",
               "rerun_stage build (opening_models: the audited library doors for every role)", problem=p.get("kind"))
            for p in OM.door_model_problems(manifest, building)]


def rooms_for_use(building: dict) -> list[dict]:
    """U19 (29 Oct 2026, the user's review of real06 run 154514: "There is no TV in the house", "a bit more furniture
    would be nice", "no library and books in the house", "bath is too empty there should be some dolaps", "I did not
    like this light"): the model review's M21 (``wenart.furniture.room_use``) on the building as built, each finding
    with its own lesson and the stage that fixes it."""
    from wenart.furniture import room_use as RU

    fixes = {"media_wall": "rerun_stage layout (media_wall: a TV unit and its TV facing the main seat)",
             "user_rejected": "swap_model (the fit never takes a user-rejected model: catalog.user_rejection)",
             "symbol_size": "rerun_stage refit (fit.apply_size_snap: the plan symbol at its real product size)"}
    out = []
    for f in RU.review(building)[0]:
        m = f.get("metrics") or {}
        rule = str(m.get("rule") or "")
        fix = fixes.get(rule) or ("rerun_stage decor (tabletop.shelf_books)" if rule.endswith(".books")
                                  else "rerun_stage layout (room_fill)")
        out.append(_f("U19", f["severity"], f.get("target"), f["message"], str(m.get("lesson") or "UL98"), fix,
                      rule=rule, room=f.get("room_id")))
    return out


def bathroom_sets(building: dict) -> list[dict]:
    """U30 (29 Oct 2026, lessons UL114, UL123, UL124): ``wenart.furniture.bath_details.review`` on the building as
    built, each finding with the stage that adds what is missing."""
    from wenart.furniture import bath_details as BD

    fixes = {"toilet_paper_holder": "rerun_stage decor (bath_details.dress: the paper holder beside the WC)",
             "toilet_brush": "rerun_stage decor (bath_details.dress: the brush beside the WC)",
             "towel_rail": "rerun_stage decor (bath_details.dress: a towel rail on a free wall)",
             "towel_shelf": "rerun_stage decor (bath_details.dress: a towel shelf beside the rail, towel bars)",
             "mirror": "complete_group (a mirror over the basin), else rerun_stage decor",
             "mirror_kind": "rerun_stage decor (bath_details.dress: the family's mirror)"}
    return [_f("U30", g["severity"], g["target"], g["message"], "UL114",
               fixes.get(g["missing"], "rerun_stage layout (bath_details.plan_building: the family's fixtures)"),
               missing=g["missing"], room=g["room_id"])
            for g in BD.review(building, check="U30")[0]]


BUILDING_CHECKS = (("U1", entrances_at_windows), ("U2", roofs_without_posts), ("U3", thick_columns),
                   ("U4", flat_drawn_roofs), ("U5", traced_covers), ("U6", storage_before_tall_windows),
                   ("U8", seats_facing_walls), ("U9", indoor_pieces_outdoors), ("U10", basins_without_mirrors),
                   ("U11", bare_worktops), ("U12", bare_dining_tables),
                   ("U21", roof_gaps), ("U22", thick_light_posts), ("U24", senseless_inner_windows),
                   ("U25", read_twice_and_blocked_passages), ("U17", bare_desks), ("U19", rooms_for_use),
                   ("U28", stair_windows), ("U16", blocked_fronts), ("U20", back_gaps))
# the lessons each code check measures (``coverage``)
CHECK_LESSONS = {"U1": ("UL58",), "U2": ("UL57", "UL48"), "U3": ("UL57",), "U4": ("UL57",), "U5": ("UL64",),
                 "U6": ("UL59", "UL56"), "U7": ("UL60",), "U8": ("UL61",), "U9": ("UL20",), "U10": ("UL66", "UL95"),
                 "U11": ("UL66",), "U12": ("UL66", "UL17"), "U13": ("UL66",), "U14": ("UL66",), "U15": ("UL65", "UL32"),
                 "U21": ("UL88",), "U22": ("UL88",), "U24": ("UL90", "UL101"), "U25": ("UL97",),
                 "U18": ("UL89", "UL65"), "U17": ("UL93",), "U26": ("UL100",), "U28": ("UL104",),
                 "U19": ("UL94", "UL98", "UL99", "UL102", "UL103", "UL107"),
                 "U16": ("UL92",), "U20": ("UL96",), "U27": ("UL109",), "U29": ("UL112",)}
CHECK_LESSONS["U23"] = ("UL106",)          # 29 Oct 2026: the professional bar (professional_bar)
CHECK_LESSONS["U33"] = ("UL116", "UL117", "UL120", "UL122", "UL125", "UL126", "UL127")    # 29 Oct 2026: doors_as_designed
U33_LESSONS = {"all_closed": "UL116", "leaf_in_piece": "UL116", "view_closed_doors": "UL126", "one_size": "UL117",
               "dressing_closed_fronts": "UL125", "no_frame": "UL122", "no_architrave": "UL122"}
U33_FIX = {"all_closed": "rerun_stage build (door_states.apply_states: an inside door stands open by default)",
           "leaf_in_piece": "move_piece (the piece out of the open leaf), else rerun_stage build (door_states closes "
                            "a leaf that hits a piece)",
           "view_closed_doors": "rerun_stage build (door_states.revise_for_cameras: a door a view sees into a room worth "
                                "showing opens, its leaf out of the view)",
           "one_size": "rerun_stage build (door_states.apply_sizes: the entrance taller and wider, day-room doors to the "
                       "ceiling in the modern families, product widths)",
           "no_frame": "rerun_stage build (opening_build._door_frame, parametric.door_frame_parts: every door framed)",
           "no_architrave": "rerun_stage build (the architrave on the door's indoor faces)"}


def doors_as_designed(building: dict, manifest: Optional[dict]) -> list[dict]:
    """U33 (29 Oct 2026; lessons UL116 "not all the doors needs to be closed in default", UL117 "Not every single one of
    them with the same dimension", UL120 / UL125 "this dressing could be a see through dressing room in the both sides
    argus should have think of this", UL122 "Doors looks without frames they need frames"): the model review's M29
    (``door_states.state_problems``, ``frame_problems``) as Argus' own findings, each with the fix that removes it: a
    walk-in with closed fronts only is a design finding carrying the architect's D8 answer
    (``architect_answer D8:<room> wardrobe_fronts:<kind>``), so a missed reference solution is found as well as a
    fault."""
    from wenart.blender import door_states as DS

    probs = DS.state_problems(building, manifest)
    if manifest and manifest.get("objects"):
        probs += DS.frame_problems(manifest)
    out = []
    for p in probs:
        fix = U33_FIX.get(p["kind"], "rerun_stage build")
        if p["kind"] == "dressing_closed_fronts":
            fix = (f"architect_answer D8:{p['target']} {p.get('fix_choice') or 'wardrobe_fronts:slats'} (a see-through "
                   "walk-in on every side), then rerun_stage build")
        f = _f("U33", p["severity"], p["target"], p["message"], U33_LESSONS.get(p["kind"], "UL116"), fix,
               problem=p["kind"])
        if p["kind"] == "leaf_in_piece":
            f["kind"] = "geometry"
        out.append(f)
    return out


BUILDING_CHECKS = BUILDING_CHECKS + (("U30", bathroom_sets),)     # 29 Oct 2026: the bathroom's set (UL114)
CHECK_LESSONS["U30"] = ("UL114", "UL123", "UL124")     # the bathroom photos P4, P12, P13
CHECK_LESSONS["U32"] = ("UL113", "UL115", "UL119")     # 29 Oct 2026: a different solution for each room (room_schemes)


def room_schemes_check(building: dict, manifest: Optional[dict]) -> list[dict]:
    """U32 (module docstring): the rooms' schemes and the photos' details (``room_schemes.review``, the same rule as
    the model review's M28); the fix names the stage that adds what is missing."""
    from wenart.furniture import room_schemes as RSC

    got, _n = RSC.review(building, manifest, check="U32")
    return [_f("U32", g["severity"], g["target"], g["message"], g.get("lesson") or "UL119",
               "rerun_stage decor (wenart.furniture.room_details: the room schemes and details) and build "
               "(feature_walls)", problem=g["problem"]) for g in got]


def professional_bar(building: dict, manifest: Optional[dict]) -> list[dict]:
    """U23 (module docstring): the living rooms and bedrooms against the professional reference (``dressing.review``,
    the same rule as the model review's M23); the fix names the stage that adds what is missing."""
    from wenart.furniture import dressing as DR

    got, _n = DR.review(building, manifest, check="U23")
    return [_f("U23", g["severity"], g["target"], g["message"], "UL106",
               "rerun_stage decor (wenart.furniture.dressing) and build (feature_walls, parquet)",
               missing=g["missing"]) for g in got]


def audit(building: Optional[dict], manifest: Optional[dict] = None) -> dict:
    """``{"findings", "checked"}`` of every U check (module docstring)."""
    findings, checked = [], {}
    if not building:
        return {"findings": [], "checked": {"building": "missing: not run"}}
    for cid, fn in BUILDING_CHECKS:
        try:
            got = fn(building)
        except Exception as exc:  # noqa: BLE001 - a check that fails is listed, the others still run
            checked[cid] = f"failed: {type(exc).__name__}: {exc}"[:200]
            continue
        findings += got
        checked[cid] = len(got)
    for cid, fn in (("U7", lambda: door_operations(building, manifest)), ("U13", lambda: floor_finish_on_walls(manifest)),
                    ("U14", lambda: plain_walls(building, manifest)), ("U15", lambda: door_variety(manifest)),
                    ("U18", lambda: door_models(building, manifest)),
                    ("U26", lambda: one_render_facades(building, manifest)),
                    ("U27", lambda: missing_chimneys(building, manifest)),
                    ("U29", lambda: wall_plates(building, manifest))):
        if not manifest:
            checked[cid] = "no scene manifest: not run"
            continue
        try:
            got = fn()
        except Exception as exc:  # noqa: BLE001
            checked[cid] = f"failed: {type(exc).__name__}: {exc}"[:200]
            continue
        findings += got
        checked[cid] = len(got)
    # 29 Oct 2026 (UL113, UL115, UL119): a different solution for each room, a hall's console or niche, a dressed bed
    # wall (on the building; the scene's panels when there is a manifest)
    try:
        got = room_schemes_check(building, manifest)
        findings += got
        checked["U32"] = len(got)
    except Exception as exc:  # noqa: BLE001 - a check that fails is listed, the others still run
        checked["U32"] = f"failed: {type(exc).__name__}: {exc}"[:200]
    # 29 Oct 2026 (UL106): the professional bar of the living rooms and bedrooms (on the built scene)
    if not manifest:
        checked["U23"] = "no scene manifest: not run"
    else:
        try:
            got = professional_bar(building, manifest)
            findings += got
            checked["U23"] = len(got)
        except Exception as exc:  # noqa: BLE001 - a check that fails is listed, the others still run
            checked["U23"] = f"failed: {type(exc).__name__}: {exc}"[:200]
    # 29 Oct 2026 (UL116, UL117, UL120, UL122, UL125): the doors and the walk-ins as designed (the frames need the scene)
    try:
        got = doors_as_designed(building, manifest)
        findings += got
        checked["U33"] = len(got) if manifest else f"{len(got)} (no scene manifest: the frames not checked)"
    except Exception as exc:  # noqa: BLE001 - a check that fails is listed, the others still run
        checked["U33"] = f"failed: {type(exc).__name__}: {exc}"[:200]
    # 29 Oct 2026 (UL115, UL118): the kitchens against their family's kitchen details (the rig's strips with a manifest)
    try:
        got = kitchen_details(building, manifest)
        findings += got
        checked["U31"] = len(got)
    except Exception as exc:  # noqa: BLE001
        checked["U31"] = f"failed: {type(exc).__name__}: {exc}"[:200]
    # 29 Oct 2026 (UL121): every bed in its family's bedding (the dressing as built with a manifest, else the plan)
    try:
        got = bed_realism(building, manifest)
        findings += got
        checked["U34"] = len(got)
    except Exception as exc:  # noqa: BLE001
        checked["U34"] = f"failed: {type(exc).__name__}: {exc}"[:200]
    # 30 Oct 2026 (UL131, UL140): the library soft seats as built (the scene's objects)
    if not manifest:
        checked["U36"] = "no scene manifest: not run"
    else:
        try:
            got = soft_seats(building, manifest)
            findings += got
            checked["U36"] = len(got)
        except Exception as exc:  # noqa: BLE001
            checked["U36"] = f"failed: {type(exc).__name__}: {exc}"[:200]
    # 30 Oct 2026 (UL134, UL139): every wall item clear of its wall's openings, the other wall items and what stands in
    # front of it (on the building as built)
    try:
        got = wall_items_clear(building, manifest)
        findings += got
        checked["U35"] = len(got)
    except Exception as exc:  # noqa: BLE001
        checked["U35"] = f"failed: {type(exc).__name__}: {exc}"[:200]
    # 30 Oct 2026 (UL153, photo P16 "salon inspiration"): the living-dining rooms against P16 by their family
    try:
        got = salon_check(building, manifest)
        findings += got
        checked["U38"] = len(got)
    except Exception as exc:  # noqa: BLE001
        checked["U38"] = f"failed: {type(exc).__name__}: {exc}"[:200]
    return {"findings": findings, "checked": checked}


BEDDING_FIXES = {
    "too_few_pillows": "rerun_stage build (textiles.bedding_set: the family's shams, pillows, accent cushions, lumbar)",
    "no_overhang": "rerun_stage build (textiles.bedding_set: the duvet hangs almost to the floor on each free side)",
    "flat_bedding": "rerun_stage build (furniture._bedding_test: a model's flat bedding is dressed by us)",
    "no_throw": "rerun_stage decor (wenart.furniture.bedding.plan_beds / dressing.layer_bedding: a throw pair)",
    "throw_pattern": "rerun_stage decor (wenart.furniture.bedding.plan_beds: the throw pair's weave), then build",
    "throw_fringe": "rerun_stage decor (wenart.furniture.bedding.plan_beds: the throw pair's weave), then build"}


def bed_realism(building: dict, manifest: Optional[dict] = None) -> list[dict]:
    """U34 (29 Oct 2026, lesson UL121; module docstring): ``bedding_parts.review`` (the same rule as the model review's
    M30); the fix names the stage that adds what is missing."""
    from wenart.blender import bedding_parts as BP

    got, _n = BP.review(building, manifest, check="U34")
    return [_f("U34", g["severity"], g["target"], g["message"], g["lesson"],
               BEDDING_FIXES.get(g["problem"], "rerun_stage decor (wenart.furniture.bedding), then build"),
               problem=g["problem"], family=g.get("family"), room=g.get("room_id")) for g in got]


# 29 Oct 2026: a full, realistic bed (bedding_parts.review); 30 Oct 2026: a real made bed (UL136: a lumpy duvet, a
# wavy hem; UL137: the head's gap left open; UL146: the P14 layers' blanket)
CHECK_LESSONS["U34"] = ("UL121", "UL136", "UL137", "UL146")


WALL_ITEM_FIXES = {
    "opening": "rerun_stage build (wall_items.resolve: the item moves along its wall or to another free wall, else it "
               "is left out; the decor stage runs it too)",
    "overlap": "rerun_stage build (wall_items.resolve: the later item moves off the other one)",
    "covered": "rerun_stage build (wall_items.resolve: the item is raised 0.15-0.25 m over what stands in front of its "
               "wall, else moved, else left out)"}


def wall_items_clear(building: dict, manifest: Optional[dict] = None) -> list[dict]:
    """U35 (30 Oct 2026, lessons UL134 "These things in front of a window needs fixing" and UL139 "need to move the
    picture, TV hiding the picture not making sense"): ``wall_items.review`` (the same rule as the model review's M32):
    a wall item over a door, a window or a frame of its wall, over another wall item, or behind a piece standing in
    front of its wall whose top (a TV on its unit included) reaches over its bottom; a hung piece of the drawing over
    an opening. The fix names the pass that raises, moves or leaves out the item."""
    from wenart.blender import wall_items as WI

    got, _n = WI.review(building, check="U35")
    return [_f("U35", g["severity"], g["target"], g["message"], g["lesson"],
               WALL_ITEM_FIXES.get(g["kind"], "rerun_stage build (wall_items.resolve)") if g.get("source") == "decor"
               else "the layout stage or the architect: a hung piece of the drawing over an opening",
               problem=g["kind"], other=g.get("other"), room=g.get("room_id")) for g in got]


CHECK_LESSONS["U35"] = ("UL134", "UL139")     # 30 Oct 2026: wall items clear of openings, each other, what stands below
CHECK_LESSONS["U38"] = ("UL153",)        # 30 Oct 2026: the P16 living-dining room (salon_details.review)
SALON_FIXES = {
    "seating_rug": "rerun_stage decor (salon_details.seating_rug: a rug under the sofa group)",
    "dining_rug": "rerun_stage decor (salon_details.dining_rug: a rug under the dining set)",
    "dining_art_small": "rerun_stage decor (room_details.dining_wall: the print at 2/3 of the table, "
                        "salon_details.dining_art_width)",
    "dining_light": "rerun_stage decor (salon_details.dining_light: one fixture over the table), then build",
    "centrepiece": "rerun_stage decor (salon_details.centrepiece: the table's set), then build",
    "tv_console": "rerun_stage decor (salon_details.console_form: the floating console), then refit and build",
    "tv_niches": "rerun_stage decor (salon_details.tv_niches: the lit niches beside the TV), then build",
    "drum_table": "rerun_stage decor (salon_details.drum_tables: the travertine drum), then refit and build"}


def salon_check(building: dict, manifest: Optional[dict] = None) -> list[dict]:
    """U38 (30 Oct 2026, lesson UL153, photo P16; module docstring): ``salon_details.review`` (the same rule as the
    model review's M34); the fix names the step that adds what is missing."""
    from wenart.furniture import salon_details as SDT

    got, _n = SDT.review(building, manifest, check="U38")
    return [_f("U38", g["severity"], g["target"], g["message"], g["lesson"],
               SALON_FIXES.get(g["problem"], "rerun_stage decor (wenart.furniture.salon_details), then build"),
               problem=g["problem"], room=g.get("room_id")) for g in got]


def kitchen_details(building: dict, manifest: Optional[dict] = None) -> list[dict]:
    """U31 (29 Oct 2026, lessons UL115, kitchen part, and UL118; the user's reference kitchens: "look at all these
    details I want these details", "look at this beautiful kitchen"): ``kitchen_details.review`` (the same rule as the
    model review's M27): a worktop bare beyond U11, wall cabinets with no LED strip, an island hob without a hood, a
    family detail not built, a kitchen with no fridge; the fix names the stage that adds what is missing."""
    from wenart.blender import kitchen_details as KD

    fixes = {"styling": "rerun_stage decor (decor.kitchen_worktop_decor: the family's styling sets)",
             "led": "rerun_stage build (lighting.rig_plan: a strip under every wall cabinet; kitchen_details.run_boxes)",
             "island_hood": "rerun_stage refit (modules.plan_kitchen_run: every hob gets its hood)",
             "fridge": "rerun_stage refit (fit.kitchen_details_hints: a fridge column or an under-counter fridge)",
             "dishwasher": "rerun_stage refit (modules.plan_kitchen_run: the dishwasher beside the sink unit, K16)"}
    got, _n = KD.review(building, manifest, check="U31")
    return [_f("U31", g["severity"], g["target"], g["message"], g["lesson"],
               fixes.get(g["problem"], "rerun_stage refit (kitchen_details: the family's kitchen details)"),
               problem=g["problem"], family=g.get("family"), room=g.get("room_id")) for g in got]


CHECK_LESSONS["U31"] = ("UL115", "UL118")     # 29 Oct 2026: the kitchen details (kitchen_details.review)


def soft_seats(building: Optional[dict], manifest: Optional[dict]) -> list[dict]:
    """U36 (30 Oct 2026, lessons UL131 "I did not like these sofa models" and UL140 "I like this sofa but it needs
    more details, also the gaps need a rework"): ``soft_seats.review`` on the scene (the same rule as the model
    review's M33): a library soft seat in flat export colours, with its parts apart, faceted or a poor model; the fix
    names the build's step or the swap."""
    from wenart.blender import soft_seats as SS

    got, _n = SS.review(manifest, check="U36")
    out = []
    for g in got:
        f = _f("U36", g["severity"], g["target"], g["message"], g["lesson"], g["fix"], problem=g["problem"],
               room=g.get("room_id"), **g["metrics"])
        if g["problem"] in ("parts_apart", "rest_apart"):      # 30 Oct 2026 (UL167): a back apart from the seat
            f["kind"] = "detached"
        out.append(f)
    return out


CHECK_LESSONS["U36"] = ("UL131", "UL140")     # 30 Oct 2026: soft seats as soft, well-made products (soft_seats)


def run(inp) -> dict:
    """The line for ``report.LINE_MODULES``: the building as built (the scene's), else the final one."""
    return audit(inp.stage("build") or inp.final, inp.manifest)


# ------------------------------------------------------------------------------------------ the lesson walk
INTERIOR_AREAS = ("furniture", "decor", "details", "lighting", "materials", "plan", "openings", "access", "daylight",
                  "library", "other")
EXTERIOR_AREAS = ("facade", "roof", "site", "terrace", "openings", "access", "materials", "views")
WALK_STATUSES = ("rule", "built", "open")


def lesson_questions(where: str, lessons: Optional[list] = None) -> list[dict]:
    """The lessons' questions for Argus AI's lesson walk (pure): ``where`` ``interior`` (asked per floor on its
    top-down view and renders) or ``exterior`` (asked on the exterior views); every lesson of a matching area with a
    question and a status of ``WALK_STATUSES`` (a process lesson is about how we work, not about the house).
    ``[{"id": "lesson:<id>", "lesson": id, "ask"}]``."""
    from wenart.blender import architect_lessons as L

    areas = INTERIOR_AREAS if where == "interior" else EXTERIOR_AREAS
    out = []
    for x in lessons if lessons is not None else L.lessons():
        if x.get("status") in WALK_STATUSES and x.get("area") in areas:
            out.append({"id": f"lesson:{x['id']}", "lesson": x["id"], "ask": ask_of(x)})
    return out


def ask_of(lesson: dict) -> str:
    """A lesson's question; a lesson stored without one (added with no model) is asked in the user's own words."""
    if lesson.get("question"):
        return str(lesson["question"])
    return (f"The user once said about another house: {str(lesson.get('request') or lesson.get('lesson'))!r}. Does "
            f"this house repeat that problem?")


def coverage(lessons: Optional[list] = None) -> dict:
    """``{lesson id: {"code": [U checks], "walk": [interior|exterior]}}`` for every lesson that is not a process one:
    how Argus finds what each lesson says (pure)."""
    from wenart.blender import architect_lessons as L

    rows = {}
    for x in lessons if lessons is not None else L.lessons():
        if x.get("status") == "process":
            continue
        code = sorted((c for c, ls in CHECK_LESSONS.items() if x["id"] in ls), key=lambda c: int(c[1:]))
        walk = [w for w, areas in (("interior", INTERIOR_AREAS), ("exterior", EXTERIOR_AREAS))
                if x.get("area") in areas and x.get("status") in WALK_STATUSES]
        rows[x["id"]] = {"code": code, "walk": walk}
    return rows
