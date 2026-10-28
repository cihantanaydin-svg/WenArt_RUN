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
- U10 a bathroom basin with no mirror over it ("Mirrors in the baths is missing sometimes");
- U11 a kitchen worktop with no small appliance (kettle, microwave, coffee machine, toaster: "kettle in the kitchen
  microwave in the kitchen");
- U12 a dining table with nothing on it ("plates on tables for example");
- U13 a floor finish on a wall slot of the style (``exterior_checks.floor_texture``: "What kind of a kitchen is
  this");
- U14 a living room or bedroom with no accent wall in the scene: every wall one paint ("more stylish internal walls
  please better color");
- U15 the doors (``opening_models.door_variety_problems``): every door one model, an inside door model on the facade,
  no statement entrance ("I want better doors inside the house and the outside ... some variation is needed").

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
    return out


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


BUILDING_CHECKS = (("U1", entrances_at_windows), ("U2", roofs_without_posts), ("U3", thick_columns),
                   ("U4", flat_drawn_roofs), ("U5", traced_covers), ("U6", storage_before_tall_windows),
                   ("U8", seats_facing_walls), ("U9", indoor_pieces_outdoors), ("U10", basins_without_mirrors),
                   ("U11", bare_worktops), ("U12", bare_dining_tables))
# the lessons each code check measures (``coverage``)
CHECK_LESSONS = {"U1": ("UL58",), "U2": ("UL57", "UL48"), "U3": ("UL57",), "U4": ("UL57",), "U5": ("UL64",),
                 "U6": ("UL59", "UL56"), "U7": ("UL60",), "U8": ("UL61",), "U9": ("UL20",), "U10": ("UL66",),
                 "U11": ("UL66",), "U12": ("UL66", "UL17"), "U13": ("UL66",), "U14": ("UL66",), "U15": ("UL65", "UL32")}


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
                    ("U14", lambda: plain_walls(building, manifest)), ("U15", lambda: door_variety(manifest))):
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
    return {"findings": findings, "checked": checked}


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
