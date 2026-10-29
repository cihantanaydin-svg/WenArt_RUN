"""The kitchen details of the user's reference photos (29 Oct 2026; lessons UL115, kitchen part, and UL118;
docs/reference_details_20261029.md, section "Kitchen (P5, P3)", rows K1-K15 and G3).

The user, showing professional kitchen renders: "look at all these details I want these details", "As much detail as
you can digest", "look at this beautiful kitchen". Our kitchens had real units, a hob with its hood and a modest
worktop (28 Oct 2026), but no tall-unit wall, no waterfall island, no island hood of a designer, plain uppers, no
styled worktop. Every detail below is a general rule for every project, by style family (``FAMILY_KITCHEN``, one
table); drawn kitchen runs, islands and appliances are fixed equipment (CLAUDE.md "Furniture rules": type, position,
orientation and footprint stay; their look, built-ins and decor change), and every change is recorded (``inferred``
with its reason) in the run's plan (``plan["details"]``), the scene manifest (``modules.module_record``) and the fit's
asset.

What (pure, no ``bpy``, no shapely: it runs inside Blender and in the CPU tests):

- K1 the tall-unit column: a counter run with room for it gets, at a free end (a wall end first, never a corner with
  another run, never in front of a window, a door or a pass-through, never under a wall cabinet), an oven tower (a
  built-in oven over drawers, a compact oven over it, a cupboard to the ceiling) and, when the kitchen has no fridge,
  a fridge column (an integrated fridge-freezer, a French-door fridge of 90 cm in a long run), their fronts to the
  ceiling (``column_spans``, ``tall_parts``). The fit decides where (``wenart.furniture.fit.kitchen_column``); with
  ovens in the tower the hob unit holds pot drawers. No end free: an under-counter fridge in the run (the 26 Oct unit).
- K2 / K15 waterfall ends: an island of a family that uses them gets its stone (or the worktop's own) top down both
  ends to the floor (``waterfall_spans``; the units stand between the panels; the plinth stays dark and recessed).
- K2 framed island fronts: the families that use framed (shaker) fronts have them on the island too
  (``wenart.blender.looks.KITCHEN_FAMILY_LOOKS``: modern classic, transitional, farmhouse added).
- G3 bar stools at an island overhang: an island whose stools stand on its back gets its worktop over them (base units
  0.60 m deep, the rest knee space, ``overhang_of``); the completion places the stools (groups.yaml).
- K3 the island hood: a hob on an island gets a ceiling hood, a steel cylinder hung from the ceiling in the modern
  families (``cylinder_hood_parts``), the 28 Oct box hood with its chimney in the classic ones, and a black open shelf
  frame hung from the ceiling round it with glass storage jars, a vase of dried grass and a small sculpture where the
  style allows and the ceiling is high enough (``shelf_frame_parts``).
- K4 fluted uppers: the wall units of the families with fluted fronts get vertical-rib fronts, handle-less where the
  family has push-to-open uppers (``upper_front_parts``).
- K5 / G3 the splashback: stone in the modern and classic families, white subway tiles in the industrial and
  farmhouse ones, the wet walls' tiles elsewhere (``splashback_look``; the shell's 0.60 m band, cut at every window:
  a window over the worktop is the splashback).
- K6 / K14 the worktop styling sets (``STYLING_TYPES``: storage jars, a stack of plates and bowls, a pot and a pan on
  the hob, cutting boards leaning on the splashback, oil bottles on a small tray, dried grass in a vase, a coffee
  station), placed by ``wenart.furniture.decor.kitchen_worktop_decor`` with the code checks, each set one mesh
  (``styling_parts``: vertex and face lists, no per-item operator); the build rests them on the known worktop line
  (``worktop_z``: no ray per item, lesson UL111).
- K7 the tap: a pull-down spray tap in the family's fixture finish (the handles' metal: black, steel, brass;
  ``tap_parts``).
- K8 under-cabinet light: the rig's LED strip under every wall cabinet (``wenart.blender.lighting``); a kitchen run is
  no single box for its collision test any more (``run_boxes``: the worktop and each hood or tall unit), so a strip
  over a run with a hood is no longer dropped (real06 run 20261029-100801-full lost the strip under its hood-side
  cabinet), and an open-plan living or dining room with a kitchen run gets the strips too.
- K11 the kitchen floor: a kitchen of the modern families takes large glossy porcelain tiles (``floor_look``) where
  the brief names no wet-safe floor.
- G3 the utensil rail: a rail on the splashback beside the hob with hanging utensils in the industrial, farmhouse,
  rustic and Mediterranean families (``rail_span``, ``rail_parts``).
- ``review(building, manifest, check)``: the model review's M27 and Argus U31 (the same rule): a kitchen missing what
  its family's rule gives it (a bare worktop beyond the 28 Oct U11, wall cabinets with no under-cabinet light, an
  island hob without a hood, a family detail not built, a kitchen with no fridge).

Not built here: K9 (linear pendants, square downlights: the lighting helper), K10 (set tables exist since 28 Oct), K12
(plants exist), K13 (the full slat wall behind the dining table: the rooms helper).

How: tables and pure functions; the module builders (``wenart.blender.modules``) call them while they plan and build a
kitchen run or a wall run, the fit gives the hints, the decor stage places the sets. Real product sizes are cited at
each constant (designer values where no product range applies are named so).
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart.blender import geom2d
from wenart.blender import parametric as P

Part = dict
CHECK = ("UL115", "UL118")

# --------------------------------------------------------------------------
# The family table (one row per style family; designer values read from the reference photos and kitchens of the
# family, each with its reason)
# --------------------------------------------------------------------------

# The worktop styling sets (decor types, wenart.furniture.decor.KITCHEN_DECOR_TYPES), in the order they are placed.
STYLING_TYPES: tuple[str, ...] = ("cookware", "storage_jars", "cutting_boards", "oil_bottles", "plate_stack",
                                  "dried_grass_vase", "coffee_station")
_FULL = STYLING_TYPES
_CALM = ("storage_jars", "cutting_boards", "plate_stack", "dried_grass_vase", "coffee_station")
_SPARSE = ("storage_jars", "dried_grass_vase", "plate_stack")

FAMILY_KITCHEN: dict[str, dict] = {
    "modern": {"upper_fronts": "fluted", "upper_handleless": True, "waterfall": True, "island_hood": "cylinder",
               "hood_metal": "steel", "shelf_frame": True, "splashback": "stone", "tall_column": True,
               "floor": "tiles_large_gloss", "rail": False, "styling": _FULL,
               "why": "a modern kitchen (the reference P5 / P8): slab fronts with fluted handle-less uppers, a tall-unit "
                      "wall, a stone waterfall island under a steel cylinder hood in a black open shelf frame, a stone "
                      "splashback, glossy large floor tiles, a styled worktop"},
    "contemporary": {"upper_fronts": "fluted", "upper_handleless": True, "waterfall": True, "island_hood": "cylinder",
                     "hood_metal": "steel", "shelf_frame": True, "splashback": "stone", "tall_column": True,
                     "floor": "tiles_large_gloss", "rail": False, "styling": _FULL,
                     "why": "a contemporary kitchen keeps the modern details"},
    "modern classic": {"upper_fronts": None, "upper_handleless": False, "waterfall": True, "island_hood": "cylinder",
                       "hood_metal": "steel", "shelf_frame": True, "splashback": "stone", "tall_column": True,
                       "floor": "tiles_large_gloss", "rail": False, "styling": _FULL,
                       "why": "a modern classic kitchen: framed fronts everywhere (the island too), a stone waterfall "
                              "island, a steel hood in an open shelf frame, a stone splashback, glossy tiles"},
    "transitional": {"upper_fronts": None, "upper_handleless": False, "waterfall": True, "island_hood": "cylinder",
                     "hood_metal": "steel", "shelf_frame": True, "splashback": "stone", "tall_column": True,
                     "floor": "tiles_large_gloss", "rail": False, "styling": _FULL,
                     "why": "a transitional kitchen: framed fronts with the modern island and hood"},
    "modern minimal": {"upper_fronts": None, "upper_handleless": True, "waterfall": True, "island_hood": "box",
                       "hood_metal": "handle", "shelf_frame": False, "splashback": "stone", "tall_column": True,
                       "floor": "tiles_large_gloss", "rail": False, "styling": _SPARSE,
                       "why": "a minimal kitchen: handle-less slab fronts, a waterfall island, a slim box hood, a few "
                              "objects on a clear worktop"},
    "minimal": {"upper_fronts": None, "upper_handleless": True, "waterfall": True, "island_hood": "box",
                "hood_metal": "handle", "shelf_frame": False, "splashback": "stone", "tall_column": True,
                "floor": "tiles_large_gloss", "rail": False, "styling": _SPARSE,
                "why": "a minimal kitchen: handle-less slab fronts, a waterfall island, a few objects"},
    "scandinavian": {"upper_fronts": None, "upper_handleless": False, "waterfall": True, "island_hood": "cylinder",
                     "hood_metal": "handle", "shelf_frame": False, "splashback": "tiles", "tall_column": True,
                     "floor": None, "rail": False, "styling": _FULL,
                     "why": "a Scandinavian kitchen: light slab fronts with slim handles, an oak waterfall island, a "
                            "round hood in the handles' black, white tiles, a lived-in worktop"},
    "japandi": {"upper_fronts": "fluted", "upper_handleless": True, "waterfall": True, "island_hood": "cylinder",
                "hood_metal": "handle", "shelf_frame": False, "splashback": "stone", "tall_column": True,
                "floor": None, "rail": False, "styling": _CALM,
                "why": "a Japandi kitchen: fluted handle-less uppers, a wood waterfall island, a calm styled worktop"},
    "industrial": {"upper_fronts": None, "upper_handleless": False, "waterfall": False, "island_hood": "box",
                   "hood_metal": "handle", "shelf_frame": True, "splashback": "subway", "tall_column": True,
                   "floor": None, "rail": True, "styling": _FULL,
                   "why": "an industrial kitchen (the reference G3): a black kitchen, white subway tiles, a utensil "
                          "rail, a black box hood with an open black shelf frame, bar stools at the island"},
    "farmhouse": {"upper_fronts": None, "upper_handleless": False, "waterfall": False, "island_hood": "box",
                  "hood_metal": "handle", "shelf_frame": False, "splashback": "subway", "tall_column": True,
                  "floor": None, "rail": True, "styling": _FULL,
                  "why": "a farmhouse kitchen: framed fronts, white subway tiles, a utensil rail, a full worktop"},
    "rustic": {"upper_fronts": None, "upper_handleless": False, "waterfall": False, "island_hood": "box",
               "hood_metal": "handle", "shelf_frame": False, "splashback": "subway", "tall_column": True,
               "floor": None, "rail": True, "styling": _FULL,
               "why": "a rustic kitchen: framed fronts, subway tiles, a utensil rail, a full worktop"},
    "mediterranean": {"upper_fronts": None, "upper_handleless": False, "waterfall": False, "island_hood": "box",
                      "hood_metal": "handle", "shelf_frame": False, "splashback": "tiles", "tall_column": True,
                      "floor": None, "rail": True, "styling": _FULL,
                      "why": "a Mediterranean kitchen: framed fronts, the wet walls' tiles, a utensil rail"},
    "classic": {"upper_fronts": None, "upper_handleless": False, "waterfall": True, "island_hood": "box",
                "hood_metal": "handle", "shelf_frame": False, "splashback": "stone", "tall_column": True,
                "floor": None, "rail": False, "styling": _CALM,
                "why": "a classic kitchen: framed fronts with brass, a marble waterfall island, a stone splashback"},
}
FAMILY_KITCHEN["default"] = dict(FAMILY_KITCHEN["modern"], upper_fronts=None, floor=None,
                                 why="no style family: the modern kitchen details without fluted uppers or a floor "
                                     "change")
SPLASHBACK_KINDS = ("stone", "subway", "tiles")
ISLAND_HOODS = ("cylinder", "box")


def family_rule(family: Optional[str]) -> dict:
    """The family's row of ``FAMILY_KITCHEN`` (an unknown family or none takes ``default``) with ``family``."""
    fam = str(family or "").lower().strip()
    return dict(FAMILY_KITCHEN.get(fam) or FAMILY_KITCHEN["default"], family=fam or "default")


def family_from(style: Optional[dict], hints: Optional[dict] = None, design: Optional[dict] = None
                ) -> Optional[str]:
    """The style family a kitchen plan follows (``"default"`` for a style without one), or None when nothing tells it
    (a plan made with no style at all keeps the plan of before: no details). The style's ``family``, else the hints'
    ``family``, else the design's ``style_family``."""
    if isinstance(hints, dict) and hints.get("family"):
        return str(hints["family"]).lower()
    if isinstance(style, dict):
        return str(style.get("family") or "default").lower()
    if isinstance(design, dict) and design.get("style_family"):
        return str(design["style_family"]).lower()
    return None


# --------------------------------------------------------------------------
# Real product sizes (metres)
# --------------------------------------------------------------------------

# K1: tall units (IKEA METOD high cabinets 60 x 60 x 200 / 220 / 240 cm, built-in ovens 59.5 cm high, compact ovens and
# combination microwaves 45.5 cm high in a 60 cm housing; integrated fridge-freezers in a 60 cm housing; built-in
# French-door fridges 36 in = 91 cm wide); the oven's bottom at eye-level ergonomics (the door's handle 1.3-1.5 m).
COLUMN: dict[str, float] = {
    "oven_w": 0.60, "fridge_w": 0.60, "french_w": 0.90, "french_from_run_m": 3.60,
    "rest_min_m": 1.20,          # at least this much counter stays beside the column (sink, hob and a landing)
    "clear_m": 0.10,             # off the sink or hob unit
    "scribe_m": 0.01,            # the column's top this far under the ceiling (a scribe strip)
    "top_default_m": 2.40, "top_max_m": 3.00, "top_min_m": 2.10,
    "oven_bottom_m": 0.80, "oven_h_m": 0.595, "compact_h_m": 0.455, "strip_m": 0.09, "compact_strip_m": 0.07,
    "freezer_top_m": 0.80, "fridge_top_m": 2.05,
}
COLUMN_KINDS: tuple[str, ...] = ("oven_tower", "fridge_column", "fridge_french")
# K2 / K15: a waterfall end is the worktop's own slab (the 40 mm top) down to the floor.
WATERFALL_T_M = 0.04
# G3: the island's knee space (NKBA: 15 in = 38 cm at counter height; 20-30 cm in compact kitchens; METOD 60 cm base
# under a deeper top); an overhang of more than 0.35 m wants legs or corbels: never more here.
OVERHANG = {"base_d": 0.60, "min_m": 0.20, "max_m": 0.35}
# K3: cylinder island hoods (37-45 cm diameter, 40-60 cm high, hung on a tube or cables; the bottom 0.65-0.75 m over
# the hob) and a ceiling-hung kitchen shelf (black steel, 20 mm tube, 100-160 x 40-50 cm, two tiers).
CYLINDER_HOOD = {"d_small": 0.40, "d_large": 0.45, "large_from_m": 0.80, "h": 0.50, "tube_r": 0.025,
                 "canopy_r": 0.10, "canopy_h": 0.03}
SHELF_FRAME = {"tube": 0.02, "w_min": 1.00, "w_extra": 0.70, "w_max": 1.60, "island_margin": 0.10, "d_extra": 0.10,
               "d_min": 0.40, "shelf_t": 0.012, "over_hood_bottom": 0.12, "tier": 0.38, "rod_r": 0.006,
               "ceiling_clear": 0.45, "plate_r": 0.03, "plate_h": 0.008}
# K4: a fluted front (vertical ribs on a backing, 18 mm in all as a slab front; rib pitch 2-3 cm, designer value).
FLUTE = {"rib_w": 0.022, "gap": 0.004, "rib_d": 0.008, "backing_t": 0.010, "bevel": 0.003}
# K7: a pull-down spray tap (a compact gooseneck: 29 cm high, 17 cm reach, a 3.4 cm spray head; real products 28-45 cm
# high with a 17-23 cm reach).
TAP = {"body_r": 0.016, "body_h": 0.19, "arc_r": 0.085, "tube": 0.022, "head_r": 0.017, "head_h": 0.07, "segments": 7}
# G3: a utensil rail (60-90 cm bar of 16 mm on two wall brackets, 45-50 cm over the worktop, hooks and utensils).
RAIL = {"len_max": 0.90, "len_min": 0.50, "r": 0.008, "z_over_worktop": 0.45, "standoff": 0.035, "hang": 0.24,
        "hob_clear": 0.10, "end_clear": 0.10, "pitch": 0.13}
# K11: the glossy large porcelain tile of the modern kitchens (60 x 120 cm, polished: roughness 0.06; designer value).
FLOOR_TILE_SLUG = "tiles_large_gloss"

P.BEVEL_BY_ROLE.setdefault("flute", FLUTE["bevel"])
P.BEVEL_BY_ROLE.setdefault("waterfall", 0.004)
P.BEVEL_BY_ROLE.setdefault("rail", 0.0)
P.BEVEL_BY_ROLE.setdefault("jar", 0.0)


# --------------------------------------------------------------------------
# Primitives (pure)
# --------------------------------------------------------------------------

def beam(p0: Sequence[float], p1: Sequence[float], t: float, key: str, role: str, t2: Optional[float] = None,
         side: Optional[Sequence[float]] = None) -> Part:
    """A box of square section ``t`` (``t x t2``) from ``p0`` to ``p1`` (a bent tube's segment, a tilted board):
    the ``geom2d.box`` turned by a right-handed frame, so its faces stay wound outwards; ``t`` runs along ``side``
    (a direction, made square to the axis) when given."""
    x0, y0, z0 = (float(v) for v in p0)
    x1, y1, z1 = (float(v) for v in p1)
    length = math.dist((x0, y0, z0), (x1, y1, z1))
    if length < 1e-9:
        length = 1e-6
    u = ((x1 - x0) / length, (y1 - y0) / length, (z1 - z0) / length)
    if side is not None:
        s = [float(v) for v in side]
        k = s[0] * u[0] + s[1] * u[1] + s[2] * u[2]
        v = _norm((s[0] - k * u[0], s[1] - k * u[1], s[2] - k * u[2]))
    else:
        ref = (0.0, 0.0, 1.0) if abs(u[2]) < 0.9 else (1.0, 0.0, 0.0)
        v = _norm(_cross(ref, u))
    w = _cross(u, v)
    verts, faces = geom2d.box((0.0, 0.0, 0.0), (length, t, t if t2 is None else t2), 0.0)
    mid = ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0)
    out = [(mid[0] + a * u[0] + b * v[0] + c * w[0], mid[1] + a * u[1] + b * v[1] + c * w[1],
            mid[2] + a * u[2] + b * v[2] + c * w[2]) for a, b, c in verts]
    return {"verts": out, "faces": faces, "key": key, "role": role}


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _norm(a):
    n = math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2) or 1.0
    return (a[0] / n, a[1] / n, a[2] / n)


def _jar(x: float, y: float, z: float, r: float, h: float, fill: str, fill_share: float = 0.55) -> list[Part]:
    """A glass storage jar with its contents and a wooden lid (pure; bottom at ``z``)."""
    lid = min(0.02, h * 0.12)
    body = h - lid
    return [P._cylinder_z(x, y, z, r, r, body, "glass", "jar", n=16),
            P._cylinder_z(x, y, z + 0.004, r - 0.006, r - 0.006, body * fill_share, fill, "contents", n=12),
            P._cylinder_z(x, y, z + body, r + 0.002, r + 0.002, lid, "wood", "lid", n=16)]


# --------------------------------------------------------------------------
# K1 the tall-unit column (plan)
# --------------------------------------------------------------------------

def column_widths(kinds: Sequence[str]) -> list[tuple[str, float]]:
    """``[(kind, width)]`` of the column's units in order from the run's end (the fridge at the end, the oven tower
    beside it: the fridge's door opens against the wall)."""
    out = []
    for k in kinds:
        if k == "fridge_french":
            out.append((k, COLUMN["french_w"]))
        elif k == "fridge_column":
            out.append((k, COLUMN["fridge_w"]))
        elif k == "oven_tower":
            out.append((k, COLUMN["oven_w"]))
    return out


def column_spans(w: float, taken: Sequence[tuple[float, float, str]], hint: Optional[dict], island: bool = False
                 ) -> tuple[list[tuple[float, float, str]], list[str]]:
    """``(spans, notes)``: the tall units of the fit's ``column`` hint (``{"end": "left" | "right", "kinds": [...]}``)
    at that end of a run of width ``w`` (the run's frame), when they keep ``COLUMN["rest_min_m"]`` of counter and stay
    ``COLUMN["clear_m"]`` off every taken span (the sink and hob units, the gaps of drawn stoves); none on an island."""
    if not isinstance(hint, dict) or island:
        return [], []
    kinds = [k for k in hint.get("kinds") or [] if k in COLUMN_KINDS]
    widths = column_widths(kinds)
    if not widths:
        return [], []
    total = sum(wd for _k, wd in widths)
    if w - total < COLUMN["rest_min_m"] - 1e-9:
        return [], [f"no tall-unit column: {w - total:.2f} m of counter would stay beside it (less than "
                    f"{COLUMN['rest_min_m']:.2f} m)"]
    left = hint.get("end") == "left"
    spans, x = [], (-w / 2.0 if left else w / 2.0)
    for kind, wd in widths:
        span = (x, x + wd, kind) if left else (x - wd, x, kind)
        spans.append(span)
        x = span[1] if left else span[0]
    lo, hi = min(s[0] for s in spans), max(s[1] for s in spans)
    clear = COLUMN["clear_m"]
    for f0, f1, k in taken:
        if lo < f1 + clear - 1e-9 and hi > f0 - clear + 1e-9:
            return [], [f"no tall-unit column at the run's {hint.get('end')} end: it would meet the {k} unit or gap"]
    spans.sort()
    return spans, [f"a tall-unit column at the run's {hint.get('end')} end: "
                   + " + ".join(f"{k.replace('_', ' ')} {wd * 100:.0f} cm" for k, wd in widths)
                   + f", its fronts up to {column_top(hint):.2f} m (K1)"]


def column_top(hint: Optional[dict]) -> float:
    """The top of the tall units: the ceiling over the run less the scribe, within ``top_min_m`` .. ``top_max_m``."""
    top = (hint or {}).get("top_m")
    try:
        top = float(top) - COLUMN["scribe_m"]
    except (TypeError, ValueError):
        top = COLUMN["top_default_m"]
    return round(max(COLUMN["top_min_m"], min(COLUMN["top_max_m"], top)), 4)


def tall_module(span: tuple[float, float, str], d: float, top: float, plinth: float) -> dict:
    """The ``tall_unit`` module of one column unit (``modules._module`` shape)."""
    x0, x1, kind = span
    names = {"oven_tower": "oven tower (built-in oven, compact oven, drawers, a cupboard to the ceiling)",
             "fridge_column": "integrated fridge-freezer column", "fridge_french": "built-in French-door fridge"}
    return {"kind": "tall_unit", "size_m": [round(x1 - x0, 4), round(d, 4), round(top - plinth, 4)],
            "pos_m": [round((x0 + x1) / 2.0, 4), 0.0], "rot_deg": 0.0, "material": "front", "z_m": plinth,
            "front": kind, "holds": "fridge" if kind.startswith("fridge") else "oven", "column": True,
            "product": f"{names[kind]} {(x1 - x0) * 100:.0f} cm, {top * 100:.0f} cm high"}


# --------------------------------------------------------------------------
# K2 / K15 waterfall ends, G3 the overhang (plan)
# --------------------------------------------------------------------------

def waterfall_spans(w: float, gaps: Sequence[tuple[float, float, str]], island: bool, rule: Optional[dict]
                    ) -> tuple[list[tuple[float, float, str]], list[str]]:
    """``(spans, notes)``: the waterfall panels at both ends of an island whose family uses them (``rule``), each
    ``WATERFALL_T_M`` thick; none at an end where the gap of a drawn stove or sink reaches it."""
    if not island or not rule or not rule.get("waterfall"):
        return [], []
    t = WATERFALL_T_M
    out, notes = [], []
    for x0, x1 in ((-w / 2.0, -w / 2.0 + t), (w / 2.0 - t, w / 2.0)):
        if any(x0 < g1 + 1e-6 and x1 > g0 - 1e-6 for g0, g1, _k in gaps):
            notes.append("no waterfall end where the gap of a drawn piece reaches the island's end")
            continue
        out.append((round(x0, 4), round(x1, 4), "waterfall"))
    if out:
        notes.append(f"the worktop runs down {'both ends' if len(out) == 2 else 'one end'} of the island to the floor "
                     f"(a waterfall end, the {rule.get('family')} family; K2 / K15)")
    return out, notes


def overhang_of(d: float, island: bool, hints: dict) -> Optional[dict]:
    """G3: ``{"carcass_d", "carcass_y", "overhang", "side"}`` of an island whose stools stand on its back
    (``hints["seat_side"] == "back"``, the fit's), when the depth leaves ``OVERHANG["min_m"]`` of knee space behind
    0.60 m base units (at most ``OVERHANG["max_m"]``: the base units grow up to the rest); None otherwise."""
    if not island or (hints or {}).get("seat_side") != "back":
        return None
    over = d - OVERHANG["base_d"]
    if over < OVERHANG["min_m"] - 1e-9:
        return None
    over = min(over, OVERHANG["max_m"])
    cd = d - over
    return {"carcass_d": round(cd, 4), "carcass_y": round(-over / 2.0, 4), "overhang": round(over, 4), "side": "back"}


# --------------------------------------------------------------------------
# K3 the island hood, G3 the rail (plan)
# --------------------------------------------------------------------------

def island_hood_style(hood: dict, rule: Optional[dict], island_w: float, island_d: float) -> list[str]:
    """K3: the island hood's style on its module (``hood["style"]``: ``cylinder`` or ``box``, ``metal``) and the
    shelf frame round it (``hood["frame"]``: width, depth, tiers) where the family allows and the ceiling leaves room;
    returns the notes. A hood of another kind is left as it is."""
    if not rule or hood.get("hood") != "island":
        return []
    notes = []
    style = rule.get("island_hood") if rule.get("island_hood") in ISLAND_HOODS else "box"
    hood["style"] = style
    if style == "cylinder":
        hob_w = float(hood["size_m"][0])
        dia = CYLINDER_HOOD["d_large"] if hob_w >= CYLINDER_HOOD["large_from_m"] - 1e-9 else CYLINDER_HOOD["d_small"]
        hood["size_m"] = [dia, dia, hood["size_m"][2]]
        hood["material"] = "steel" if rule.get("hood_metal") == "steel" else "handle"
        hood["product"] = f"cylinder island hood {dia * 100:.0f} cm"
        notes.append(f"a {dia * 100:.0f} cm {'steel' if hood['material'] == 'steel' else 'metal'} cylinder hood hung "
                     "from the ceiling over the island's hob (K3)")
    if rule.get("shelf_frame"):
        top = float(hood.get("chimney_top_m") or 0.0)
        hd = float(hood["size_m"][1])
        z_lo = float(hood["z_m"]) + SHELF_FRAME["over_hood_bottom"]
        z_hi = z_lo + SHELF_FRAME["tier"]
        fw = min(SHELF_FRAME["w_max"], max(SHELF_FRAME["w_min"], float(hood["size_m"][0]) + SHELF_FRAME["w_extra"]),
                 island_w - SHELF_FRAME["island_margin"])
        fd = max(SHELF_FRAME["d_min"], hd + SHELF_FRAME["d_extra"])
        if top < z_hi + SHELF_FRAME["ceiling_clear"] - 1e-9:
            notes.append(f"no shelf frame round the island hood: the ceiling ({top:.2f} m) leaves no room over its top "
                         f"tier ({z_hi:.2f} m)")
        elif fw < float(hood["size_m"][0]) + 0.30 - 1e-9 or fd > island_d + 0.20:
            notes.append("no shelf frame round the island hood: the island is too small for one")
        else:
            hood["frame"] = {"w_m": round(fw, 4), "d_m": round(fd, 4), "z_lo_m": round(z_lo, 4),
                             "z_hi_m": round(z_hi, 4), "top_m": round(top, 4)}
            notes.append(f"a black open shelf frame {fw:.2f} x {fd:.2f} m hung from the ceiling round the hood, with "
                         "glass storage jars, dried grass in a vase and a small sculpture on its shelves (K3)")
    return notes


def rail_span(w: float, d: float, fixed: Sequence[tuple[float, float, str]], blocked: Sequence[tuple[float, float]],
              rule: Optional[dict], island: bool) -> Optional[tuple[float, float]]:
    """G3: the span of a utensil rail on the wall behind a counter run of a family that has one: beside the hob (the
    side with more free wall first), ``RAIL["hob_clear"]`` off it, off the run's ends, the sink, the tall units and the
    windows behind the run (``blocked``, the run's frame), ``RAIL["len_min"]`` to ``RAIL["len_max"]`` long; None."""
    if island or not rule or not rule.get("rail"):
        return None
    hob = next(((f0, f1) for f0, f1, k in fixed if k == "hob"), None)
    if hob is None:
        return None
    stops = sorted([(f0, f1) for f0, f1, k in fixed if k != "hob"] + [tuple(b) for b in blocked])
    lo, hi = -w / 2.0 + RAIL["end_clear"], w / 2.0 - RAIL["end_clear"]
    best = None
    for side in (-1, 1):
        a, b = (lo, hob[0] - RAIL["hob_clear"]) if side < 0 else (hob[1] + RAIL["hob_clear"], hi)
        for s0, s1 in stops:
            if s1 <= a or s0 >= b:
                continue
            if side < 0:
                a = max(a, s1 + RAIL["end_clear"])
            else:
                b = min(b, s0 - RAIL["end_clear"])
        if b - a < RAIL["len_min"] - 1e-9:
            continue
        length = min(RAIL["len_max"], b - a)
        span = (b - length, b) if side < 0 else (a, a + length)
        if best is None or length > best[1] - best[0] + 1e-9:
            best = span
    return None if best is None else (round(best[0], 4), round(best[1], 4))


# --------------------------------------------------------------------------
# Parts (pure)
# --------------------------------------------------------------------------

def _steel_door(x: float, fw: float, y_back: float, z0: float, z1: float, handle_x: float, parts: list) -> None:
    """A steel appliance door with a long vertical bar handle on two posts (the fridge's)."""
    t = P.FRONT_THICKNESS
    parts.append(P._box(x, y_back - t / 2.0, z0, fw, t, z1 - z0, "steel", "front"))
    hl = min(0.9, (z1 - z0) * 0.6)
    hz = z0 + (z1 - z0 - hl) / 2.0
    parts.append(P._box(handle_x, y_back - t - 0.03, hz, 0.016, 0.014, hl, "steel", "handle"))
    for sz in (hz + 0.02, hz + hl - 0.032):
        parts.append(P._box(handle_x, y_back - t - 0.0125, sz, 0.012, 0.023, 0.012, "steel", "handle"))


def _oven_front(x: float, fw: float, y_back: float, z0: float, h: float, strip: float, parts: list) -> None:
    """A built-in oven front ``h`` high from ``z0``: a steel control strip with two knobs over a black glass door
    with its window and a bar handle on two posts."""
    t = P.FRONT_THICKNESS
    strip_z = z0 + h - strip
    parts.append(P._box(x, y_back - t / 2.0, strip_z, fw, t, strip - 0.003, "steel", "front"))
    for sx in (-1.0, 1.0):
        parts.append(P._cylinder_y(x + sx * fw * 0.32, y_back - t - 0.022, strip_z + strip / 2.0, 0.016, 0.016,
                                   0.022, "dark", "knob", n=16))
    door_h = strip_z - z0 - 0.003
    parts.append(P._box(x, y_back - t / 2.0, z0, fw, t, door_h, "dark", "front"))
    parts.append(P._box(x, y_back - t - 0.0025, z0 + door_h * 0.22, fw * 0.7, 0.003, door_h * 0.45, "glass", "window"))
    parts.append(P._box(x, y_back - t - 0.03, z0 + door_h - 0.055, fw * 0.8, 0.014, 0.016, "steel", "handle"))
    for sx in (-1.0, 1.0):
        parts.append(P._box(x + sx * fw * 0.38, y_back - t - 0.0125, z0 + door_h - 0.053, 0.012, 0.023, 0.012,
                            "steel", "handle"))


def tall_parts(m: dict, design: dict, d_run: float, plinth_recess: float) -> list[Part]:
    """K1: one tall unit of the column (``tall_module``): its recessed plinth, the carcass up to its top and its
    fronts: ``oven_tower`` (two drawers, the 59.5 cm oven at ``COLUMN["oven_bottom_m"]``, the 45.5 cm compact oven
    over it, a cupboard door to the top), ``fridge_column`` (the steel freezer and fridge doors, a cupboard door over
    them), ``fridge_french`` (a steel freezer drawer, two French doors, a cupboard door over them)."""
    w, d, h = m["size_m"]
    x = float(m["pos_m"][0])
    z0 = float(m.get("z_m") or 0.0)
    top = z0 + h
    inset = P.FRONT_GAP + P.FRONT_THICKNESS
    face = -d_run / 2.0 + inset
    y_back = face - P.FRONT_GAP
    gap = 0.003
    fw = w - 0.004
    parts = [P._box(x, plinth_recess / 2.0, 0.0, w - 0.002, d - plinth_recess, z0, "dark", "plinth"),
             P._box(x, inset / 2.0, z0, w - 0.002, d_run - inset, h, "painted", "body")]
    kind = m.get("front")

    def cupboard(z_a: float, z_b: float) -> None:
        if z_b - z_a > 0.10:
            fronts = P.cabinet_fronts(fw, face, z_a + gap, z_b - gap, 1, 1 if w < 0.80 - 1e-9 else 2, design,
                                      handle_at="bottom")
            parts.extend(dict(p, verts=[(vx + x, vy, vz) for vx, vy, vz in p["verts"]]) for p in fronts)

    if kind == "oven_tower":
        ob = max(z0 + 0.30, COLUMN["oven_bottom_m"])
        drawers = P.cabinet_fronts(fw, face, z0 + gap, ob - gap, 2, 1, design, doors=False)
        parts.extend(dict(p, verts=[(vx + x, vy, vz) for vx, vy, vz in p["verts"]]) for p in drawers)
        _oven_front(x, fw, y_back, ob, COLUMN["oven_h_m"], COLUMN["strip_m"], parts)
        cz = ob + COLUMN["oven_h_m"] + gap
        _oven_front(x, fw, y_back, cz, COLUMN["compact_h_m"], COLUMN["compact_strip_m"], parts)
        cupboard(cz + COLUMN["compact_h_m"], top)
    elif kind == "fridge_french":
        ft = COLUMN["freezer_top_m"]
        parts.append(P._box(x, y_back - P.FRONT_THICKNESS / 2.0, z0 + gap, fw, P.FRONT_THICKNESS, ft - z0 - 2 * gap,
                            "steel", "front"))
        parts.append(P._box(x, y_back - P.FRONT_THICKNESS - 0.03, ft - 0.09, fw * 0.6, 0.014, 0.016, "steel",
                            "handle"))
        for sx in (-1.0, 1.0):
            parts.append(P._box(x + sx * fw * 0.28, y_back - P.FRONT_THICKNESS - 0.0125, ft - 0.088, 0.012, 0.023,
                                0.012, "steel", "handle"))
        door_top = min(COLUMN["fridge_top_m"], top - gap)
        half = fw / 2.0 - gap / 2.0
        for sx in (-1.0, 1.0):
            _steel_door(x + sx * (half / 2.0 + gap / 2.0), half, y_back, ft + gap, door_top, x + sx * 0.04, parts)
        cupboard(door_top, top)
    else:                                                  # fridge_column: the freezer under the fridge door
        ft = z0 + COLUMN["freezer_top_m"] - 0.10
        door_top = min(COLUMN["fridge_top_m"], top - gap)
        hx = x + fw / 2.0 - 0.06
        _steel_door(x, fw, y_back, z0 + gap, ft - gap / 2.0, hx, parts)
        _steel_door(x, fw, y_back, ft + gap / 2.0, door_top, hx, parts)
        cupboard(door_top, top)
    return parts


def waterfall_parts(span: tuple[float, float, str], d: float, worktop_z: float) -> list[Part]:
    """K2 / K15: a waterfall end panel (the worktop's slab) from the floor up to the worktop's underside."""
    x0, x1, _k = span
    return [P._box((x0 + x1) / 2.0, 0.0, 0.0, x1 - x0, d, worktop_z - 0.04, "worktop", "waterfall")]


def cylinder_hood_parts(m: dict) -> list[Part]:
    """K3: the cylinder island hood (``island_hood_style``): the cylinder, its dark filter disc, a steel tube up to a
    ceiling canopy at ``chimney_top_m``; and the shelf frame round it when ``m["frame"]``."""
    dia = float(m["size_m"][0])
    x, y = (float(v) for v in m["pos_m"])
    z0 = float(m.get("z_m") or 0.0)
    key = m.get("material") or "handle"
    r = dia / 2.0
    h = CYLINDER_HOOD["h"]
    top = float(m.get("chimney_top_m") or (z0 + h + 0.5))
    parts = [P._cylinder_z(x, y, z0, r, r, h, key, "hood", n=40),
             P._cylinder_z(x, y, z0 - 0.002, r - 0.02, r - 0.02, 0.002, "dark", "filter", n=32)]
    ch = CYLINDER_HOOD["canopy_h"]
    tube = top - ch - (z0 + h)
    if tube > 0.01:
        parts.append(P._cylinder_z(x, y, z0 + h, CYLINDER_HOOD["tube_r"], CYLINDER_HOOD["tube_r"], tube, key,
                                   "chimney", n=16))
    parts.append(P._cylinder_z(x, y, top - ch, CYLINDER_HOOD["canopy_r"], CYLINDER_HOOD["canopy_r"], ch, key,
                               "chimney", n=24))
    return parts


def shelf_frame_parts(m: dict) -> list[Part]:
    """K3: the black open shelf frame hung from the ceiling round an island hood (``m["frame"]``): four posts, the
    long rails and two tiers of shelves left and right of the hood, four rods with ceiling plates, glass storage jars
    on the lower tier, a vase of dried grass and a small sculpture on the upper one. One part list (one mesh)."""
    f = m.get("frame")
    if not isinstance(f, dict):
        return []
    x, y = (float(v) for v in m["pos_m"])
    fw, fd = float(f["w_m"]), float(f["d_m"])
    z_lo, z_hi, top = float(f["z_lo_m"]), float(f["z_hi_m"]), float(f["top_m"])
    t = SHELF_FRAME["tube"]
    st = SHELF_FRAME["shelf_t"]
    r_h = float(m["size_m"][0]) / 2.0                      # the hood's half width (a cylinder's radius)
    parts: list[Part] = []
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            px, py = x + sx * (fw / 2.0 - t / 2.0), y + sy * (fd / 2.0 - t / 2.0)
            parts.append(P._box(px, py, z_lo, t, t, z_hi + t - z_lo, "dark", "frame"))
            rr = SHELF_FRAME["rod_r"]
            parts.append(P._cylinder_z(px, py, z_hi + t, rr, rr, top - SHELF_FRAME["plate_h"] - z_hi - t, "dark",
                                       "rod", n=8))
            parts.append(P._cylinder_z(px, py, top - SHELF_FRAME["plate_h"], SHELF_FRAME["plate_r"],
                                       SHELF_FRAME["plate_r"], SHELF_FRAME["plate_h"], "dark", "rod", n=12))
    for z in (z_lo, z_hi):
        for sy in (-1.0, 1.0):                             # the long rails, clear of the hood
            parts.append(P._box(x, y + sy * (fd / 2.0 - t / 2.0), z, fw - 2 * t, t, t, "dark", "frame"))
    side_w = fw / 2.0 - t - r_h - 0.03
    shelves = []
    if side_w > 0.12:
        for sx in (-1.0, 1.0):
            cx = x + sx * (fw / 2.0 - t - side_w / 2.0)
            for z in (z_lo, z_hi):
                parts.append(P._box(cx, y, z + t - st, side_w, fd - 2 * t, st, "dark", "shelf"))
                shelves.append((cx, z + t, sx, z == z_lo))
    for cx, zs, sx, lower in shelves:
        if lower:                                           # three glass jars of different heights
            for k, (h, fill) in enumerate(((0.20, "rattan"), (0.16, "dark"), (0.22, "ceramic"))):
                jx = cx + (k - 1) * min(0.11, side_w / 3.2)
                parts += _jar(jx, y, zs, 0.042, h, fill)
        elif sx < 0:                                        # a vase with dried grass
            parts += _grass_vase(cx, y, zs, 0.16, min(0.40, top - zs - 0.08))
        else:                                               # a small sculpture and two books
            parts.append(P._box(cx + 0.05, y, zs, 0.16, 0.12, 0.03, "terracotta", "book"))
            parts.append(P._box(cx + 0.05, y, zs + 0.03, 0.15, 0.11, 0.025, "painted", "book"))
            parts.append(P._superellipsoid(cx - 0.07, y, zs, 0.08, 0.08, 0.14, 0.7, 0.9, "ceramic", "form",
                                           n_eta=6, n_om=14))
    return parts


def _grass_vase(cx: float, cy: float, z: float, w: float, h: float) -> list[Part]:
    """A vase with dried pampas grass stems and their plumes in a box ``w`` wide and ``h`` high from ``z``."""
    vh = min(0.22, h * 0.42)
    vr = w * 0.42
    parts = [P._frustum_z(cx, cy, z, vr * 0.75, vr * 0.75, vr, vr, vh * 0.55, "ceramic", "vase", n=20),
             P._frustum_z(cx, cy, z + vh * 0.55, vr, vr, vr * 0.45, vr * 0.45, vh * 0.45, "ceramic", "vase", n=20)]
    stems = 7
    plume_h = min(0.14, h * 0.28)
    reach = max(0.0, w / 2.0 - 0.025)
    for k in range(stems):
        ang = 2.0 * math.pi * k / stems
        spread = reach * (0.55 + 0.45 * ((k * 3) % 4) / 3.0)
        tx, ty = cx + math.cos(ang) * spread, cy + math.sin(ang) * spread * 0.6
        tz = z + h - plume_h - 0.01 * ((k * 5) % 3)
        parts.append(beam((cx, cy, z + vh * 0.6), (tx, ty, tz), 0.005, "wood", "stem"))
        parts.append(P._superellipsoid(tx, ty, tz, 0.035, 0.035, plume_h, 0.8, 1.0, "fabric", "plume",
                                       n_eta=5, n_om=8))
    return parts


def upper_front_parts(w: float, y_face: float, z0: float, z1: float, cols: int, design: dict, rule: Optional[dict]
                      ) -> Optional[list[Part]]:
    """K4: the fronts of a wall unit (centred on x 0, as ``parametric.cabinet_fronts``) when the family's uppers
    differ from the base fronts: fluted (vertical ribs on a backing, ``FLUTE``) and / or handle-less (push to open);
    None when the family keeps the design's own fronts."""
    if not rule or (rule.get("upper_fronts") != "fluted" and not rule.get("upper_handleless")):
        return None
    gap = 0.003
    cw = w / cols
    parts: list[Part] = []
    for c in range(cols):
        cx = -w / 2.0 + cw * (c + 0.5)
        fw, fh = cw - gap, (z1 - z0) - gap
        fz = z0 + gap / 2.0
        if rule.get("upper_fronts") == "fluted":
            parts += fluted_front(cx, y_face, fz, fw, fh)
        else:
            parts += P._front_panel(cx, y_face, fz, fw, fh, P.front_style_of(design))
        if not rule.get("upper_handleless"):
            side = 1.0 if c % 2 == 0 or cols == 1 else -1.0
            hz = fz + 0.1 + P.HANDLE_BAR[1] / 2.0
            parts.append(P._handle(cx + side * (fw / 2.0 - 0.04), y_face, hz, vertical=True))
    return parts


def fluted_front(cx: float, y_face: float, z0: float, fw: float, fh: float) -> list[Part]:
    """K4: one fluted front in front of the carcass face at ``y_face`` (the 18 mm of a slab front): a backing panel
    and vertical ribs at the ``FLUTE`` pitch over its width, all in the front's material (role ``flute`` bevels the
    ribs round)."""
    y0 = y_face - P.FRONT_GAP
    bt, rd = FLUTE["backing_t"], FLUTE["rib_d"]
    parts = [P._box(cx, y0 - bt / 2.0, z0, fw, bt, fh, "front", "front")]
    n = max(1, int((fw + FLUTE["gap"]) // (FLUTE["rib_w"] + FLUTE["gap"])))
    rw = (fw - (n - 1) * FLUTE["gap"]) / n
    for i in range(n):
        x = cx - fw / 2.0 + rw / 2.0 + i * (rw + FLUTE["gap"])
        parts.append(P._box(x, y0 - bt - rd / 2.0, z0, rw, rd, fh, "front", "flute"))
    return parts


def tap_parts(x: float, y: float, z: float, key: str = "handle") -> list[Part]:
    """K7: a pull-down spray tap at ``(x, y)`` on the worktop ``z``: the body, a gooseneck arching towards -Y (over the
    bowl) of ``TAP`` segments, the spray head hanging from its end and the lever on the body's side; every part in the
    family's fixture finish (``key``: the handles' metal) with role ``tap``."""
    br, bh = TAP["body_r"], TAP["body_h"]
    parts = [P._cylinder_z(x, y, z, br * 1.4, br * 1.4, 0.012, key, "tap", n=16),
             P._cylinder_z(x, y, z + 0.012, br, br, bh - 0.012, key, "tap", n=16)]
    r = TAP["arc_r"]
    cy, cz = y - r, z + bh
    pts = [(x, cy + r * math.cos(math.pi * k / TAP["segments"]), cz + r * math.sin(math.pi * k / TAP["segments"]))
           for k in range(TAP["segments"] + 1)]
    for a, b in zip(pts, pts[1:]):
        parts.append(beam(a, b, TAP["tube"], key, "tap"))
    hx, hy, hz = pts[-1]
    parts.append(P._cylinder_z(hx, hy, hz - TAP["head_h"], TAP["head_r"], TAP["head_r"], TAP["head_h"], key, "tap",
                               n=16))
    parts.append(P._box(x + br + 0.025, y, z + bh * 0.6, 0.05, 0.012, 0.012, key, "tap"))
    return parts


def rail_parts(span: tuple[float, float], d: float, worktop_z: float) -> list[Part]:
    """G3: the utensil rail on the wall behind a counter run (``rail_span``): the bar in the family's metal
    (``handle``) on two brackets to the wall, S-hooks and the utensils hanging from it (a ladle, a spatula, a whisk,
    a slotted spoon, tongs: steel heads on wooden handles). One part list (one mesh)."""
    x0, x1 = span
    yb = d / 2.0                                          # the run's back edge (the wall)
    yr = yb - RAIL["standoff"]
    zr = worktop_z + RAIL["z_over_worktop"]
    r = RAIL["r"]
    parts = [P._cylinder_x(x0, yr, zr, r, r, x1 - x0, "handle", "rail", n=12)]
    for bx in (x0 + 0.04, x1 - 0.04):
        parts.append(P._box(bx, (yr + yb) / 2.0, zr - 0.008, 0.012, yb - yr, 0.016, "handle", "rail"))
    n = max(2, int((x1 - x0 - 0.10) / RAIL["pitch"]) + 1)
    step = (x1 - x0 - 0.10) / max(1, n - 1)
    hang = RAIL["hang"]
    for k in range(n):
        ux = x0 + 0.05 + k * step
        parts.append(P._box(ux, yr, zr - 0.035, 0.004, 0.004, 0.035, "steel", "hook"))
        top = zr - 0.035
        kind = k % 5
        handle_l = hang * (0.55 if kind != 2 else 0.5)
        parts.append(P._box(ux, yr, top - handle_l, 0.014, 0.008, handle_l, "wood", "utensil"))
        zt = top - handle_l
        if kind == 0:                                     # a ladle
            parts.append(P._superellipsoid(ux, yr - 0.02, zt - 0.06, 0.08, 0.06, 0.06, 1.0, 1.0, "steel",
                                           "utensil", n_eta=5, n_om=10))
        elif kind == 1:                                   # a spatula
            parts.append(P._box(ux, yr, zt - 0.09, 0.07, 0.004, 0.09, "steel", "utensil"))
        elif kind == 2:                                   # a whisk
            parts.append(P._frustum_z(ux, yr - 0.01, zt - 0.11, 0.028, 0.028, 0.006, 0.006, 0.11, "steel", "utensil",
                                      n=10))
        elif kind == 3:                                   # a slotted spoon
            parts.append(P._superellipsoid(ux, yr, zt - 0.08, 0.06, 0.02, 0.08, 1.0, 1.0, "steel", "utensil",
                                           n_eta=5, n_om=10))
        else:                                             # tongs
            for sx in (-1.0, 1.0):
                parts.append(beam((ux, yr, zt), (ux + sx * 0.015, yr, zt - 0.12), 0.008, "steel", "utensil"))
    return parts


def run_detail_parts(plan: dict) -> list[Part]:
    """The parts of the details a kitchen run's plan records (``plan["details"]``): the rail; the waterfall panels
    and the tall units are modules of the plan, the cylinder hood and its frame the hood module's."""
    det = plan.get("details") if isinstance(plan.get("details"), dict) else {}
    parts: list[Part] = []
    if det.get("rail_m"):
        parts += rail_parts(tuple(det["rail_m"]), float(plan["footprint_m"][1]), float(plan.get("worktop_m") or 0.9))
    return parts


# --------------------------------------------------------------------------
# K6 / K14 the worktop styling sets (decor parts, one mesh per set; bottom on z = 0, front -Y)
# --------------------------------------------------------------------------

# Real products (width, depth, height): three 1-1.5 l glass storage jars (Ø 9 cm, 14-24 cm high), a stack of 27 cm
# dinner plates with two bowls, a 20 cm pot and a 24-28 cm pan, two cutting boards (40 x 30 and 30 x 25 cm, 2 cm),
# oil and vinegar bottles (0.5 l, 26 / 22 cm) and a salt pot on a 22 x 12 cm board, a vase of dried pampas grass,
# a coffee station (an espresso machine 26 x 30 x 36 cm, cups and saucers, a small plate stack on a wooden board).
STYLING_SIZES: dict[str, tuple[float, float, float]] = {
    "storage_jars": (0.30, 0.12, 0.24), "plate_stack": (0.27, 0.27, 0.14), "cookware": (0.55, 0.30, 0.18),
    "cutting_boards": (0.42, 0.10, 0.45), "oil_bottles": (0.22, 0.12, 0.30), "dried_grass_vase": (0.20, 0.20, 0.55),
    "coffee_station": (0.50, 0.38, 0.38)}
STYLING_REASONS: dict[str, str] = {
    "storage_jars": "glass storage jars with wooden lids against the splashback",
    "plate_stack": "a stack of plates and bowls on a free stretch",
    "cookware": "a pot and a pan on the hob",
    "cutting_boards": "cutting boards leaning on the splashback beside the hob",
    "oil_bottles": "oil and vinegar bottles with a salt pot on a small board beside the hob",
    "dried_grass_vase": "dried grass in a vase where no wall unit hangs over it",
    "coffee_station": "a coffee station at a corner of the worktop: the machine, cups and a stack of plates"}
BOARD_LEAN_DEG = 8.0              # the cutting boards lean back on the splashback


def styling_parts(dtype: str, w: float, d: float, h: float) -> list[Part]:
    """The parametric styling set of ``dtype`` in its box ``w x d x h`` (bottom on z = 0, front -Y), PBR keys of
    ``parametric.MATERIAL_KEYS`` (glass, wood, ceramic, steel, dark, terracotta, rattan, fabric, green)."""
    if dtype == "storage_jars":
        r = max(0.02, min(d / 2.0, w / 6.0) - 0.004)
        parts: list[Part] = []
        for k, (share, fill) in enumerate(((0.82, "rattan"), (1.0, "ceramic"), (0.62, "dark"))):
            parts += _jar(-w / 2.0 + r + 0.002 + k * (w - 2 * r - 0.004) / 2.0, 0.0, 0.0, r, h * share, fill)
        return parts
    if dtype == "plate_stack":
        r = min(w, d) / 2.0
        parts = []
        n = 5
        pt = 0.012
        for k in range(n):
            parts.append(P._cylinder_z(0.0, 0.0, k * (pt + 0.002), r * 0.6, r * 0.6, 0.004, "ceramic", "plate", n=24))
            parts.append(P._frustum_z(0.0, 0.0, k * (pt + 0.002) + 0.004, r * 0.6, r * 0.6, r, r, pt - 0.004,
                                      "ceramic", "plate", n=24))
        zb = n * (pt + 0.002)
        bh = max(0.02, (h - zb) / 2.0)
        for k, key in enumerate(("ceramic", "terracotta")):
            parts.append(P._frustum_z(0.0, 0.0, zb + k * bh, r * 0.32, r * 0.32, r * 0.55, r * 0.55, bh, key, "bowl",
                                      n=20))
        return parts
    if dtype == "cookware":
        pot_r = min(d / 2.0 - 0.01, w * 0.19)
        pot_x = -w / 2.0 + pot_r + 0.02
        ph = min(h - 0.03, 0.14)
        parts = [P._cylinder_z(pot_x, 0.0, 0.0, pot_r, pot_r, ph, "steel", "pot", n=24),
                 P._cylinder_z(pot_x, 0.0, ph, pot_r + 0.002, pot_r + 0.002, 0.008, "steel", "lid", n=24),
                 P._cylinder_z(pot_x, 0.0, ph + 0.008, 0.015, 0.015, min(0.02, h - ph - 0.008), "dark", "knob",
                               n=10)]
        for sx in (-1.0, 1.0):
            parts.append(P._box(pot_x + sx * (pot_r + 0.008), 0.0, ph * 0.75, 0.016, 0.04, 0.012, "dark", "handle"))
        handle = 0.08                                     # the pan's handle, inside the set's box
        pan_r = min(d / 2.0 - 0.005, (w - 2.0 * pot_r - 0.05 - handle) / 2.0, 0.13)
        pan_x = pot_x + pot_r + 0.03 + pan_r
        handle = max(0.03, min(handle, w / 2.0 - (pan_x + pan_r)))
        parts.append(P._cylinder_z(pan_x, 0.0, 0.0, pan_r, pan_r, 0.006, "dark", "pan", n=28))
        parts.append(P._frustum_z(pan_x, 0.0, 0.006, pan_r, pan_r, pan_r * 1.0, pan_r * 1.0, 0.04, "dark", "pan",
                                  n=28))
        parts.append(P._box(pan_x + pan_r + handle / 2.0, 0.0, 0.03, handle, 0.024, 0.014, "wood", "handle"))
        return parts
    if dtype == "cutting_boards":
        lean = math.radians(BOARD_LEAN_DEG)
        t = 0.02
        parts = []
        for k, (bw, bh) in enumerate(((w, h), (w * 0.72, h * 0.8))):
            yb = d / 2.0 - t / 2.0 - bh * math.sin(lean) - k * 0.026
            yt = yb + bh * math.sin(lean)
            zb, zt = t * math.sin(lean) / 2.0 + 0.0, bh * math.cos(lean)
            bx = -w / 2.0 + bw / 2.0 + k * 0.04
            part = beam((bx, yb, zb), (bx, yt, zt), bw, "wood", "board", t2=t, side=(1.0, 0.0, 0.0))
            # the board's lowest edge on z = 0 (the worktop)
            low = min(v[2] for v in part["verts"])
            part["verts"] = [(vx, vy, vz - low) for vx, vy, vz in part["verts"]]
            parts.append(part)
        return _fit_box(parts, w, d, h)
    if dtype == "oil_bottles":
        parts = [P._box(0.0, 0.0, 0.0, w, d, 0.015, "wood", "tray")]
        z = 0.015
        br = min(d / 2.0 - 0.012, 0.03)
        for k, (bx, bh, fill) in enumerate(((-w / 2.0 + br + 0.01, h - z, "green"), (0.0, (h - z) * 0.85, "dark"))):
            body = bh * 0.68
            parts.append(P._cylinder_z(bx, 0.0, z, br, br, body, "glass", "bottle", n=16))
            parts.append(P._cylinder_z(bx, 0.0, z + 0.004, br - 0.005, br - 0.005, body * 0.8, fill, "contents",
                                       n=12))
            parts.append(P._frustum_z(bx, 0.0, z + body, br, br, br * 0.35, br * 0.35, bh * 0.22, "glass", "bottle",
                                      n=16))
            parts.append(P._cylinder_z(bx, 0.0, z + body + bh * 0.22, br * 0.36, br * 0.36, bh * 0.10, "wood", "cork",
                                       n=10))
        sr = min(0.032, d / 2.0 - 0.01)
        parts.append(P._cylinder_z(w / 2.0 - sr - 0.008, 0.0, z, sr, sr, 0.07, "ceramic", "salt", n=16))
        return parts
    if dtype == "dried_grass_vase":
        return _grass_vase(0.0, 0.0, 0.0, min(w, d), h)
    if dtype == "coffee_station":
        bt = 0.015
        parts = [P._box(0.0, 0.0, 0.0, w, d, bt, "wood", "board")]
        mw, md = min(0.26, w * 0.52), min(0.30, d - 0.04)
        mh = h - bt
        mx = -w / 2.0 + mw / 2.0 + 0.01
        my = d / 2.0 - md / 2.0 - 0.01
        parts += [P._box(mx, my + 0.03, bt, mw, md - 0.06, mh, "dark", "body"),
                  P._box(mx, my - md / 2.0 + 0.035, bt, mw * 0.85, 0.07, 0.015, "steel", "tray"),
                  P._box(mx, my - md / 2.0 + 0.05, bt + mh * 0.55, mw * 0.6, 0.10, mh * 0.12, "steel", "head"),
                  P._cylinder_z(mx, my - md / 2.0 + 0.045, bt + 0.015, 0.032, 0.032, 0.065, "ceramic", "cup", n=16)]
        cx = w / 2.0 - 0.07
        for k in range(max(1, min(3, int((h - bt) / 0.068)))):     # stacked cups on their saucers
            zc = bt + k * 0.068
            parts.append(P._cylinder_z(cx, -d / 2.0 + 0.08, zc, 0.06, 0.06, 0.008, "ceramic", "saucer", n=20))
            parts.append(P._cylinder_z(cx, -d / 2.0 + 0.08, zc + 0.008, 0.04, 0.04, 0.058, "ceramic", "cup", n=16))
        for k in range(4):                                # a small stack of plates behind them
            parts.append(P._cylinder_z(cx, d / 2.0 - 0.09, bt + k * 0.014, 0.065, 0.065, 0.012, "ceramic", "plate",
                                       n=20))
        return parts
    raise KeyError(f"no styling set builder for {dtype!r}")


def _fit_box(parts: list[Part], w: float, d: float, h: float) -> list[Part]:
    """The parts moved (never scaled) so their box stays inside ``w x d x h`` on z = 0 (a leaning board's corners)."""
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    dx = max(0.0, -w / 2.0 - x0) - max(0.0, x1 - w / 2.0)
    dy = max(0.0, -d / 2.0 - y0) - max(0.0, y1 - d / 2.0)
    return [dict(p, verts=[(vx + dx, vy + dy, vz - z0) for vx, vy, vz in p["verts"]]) for p in parts]


# --------------------------------------------------------------------------
# The build: the worktop line of a run, its boxes for the light rig
# --------------------------------------------------------------------------

def _plan_of(piece: Optional[dict]) -> dict:
    asset = (piece or {}).get("asset") if isinstance((piece or {}).get("asset"), dict) else {}
    plan = asset.get("module_plan") if isinstance(asset.get("module_plan"), dict) else {}
    return plan if plan.get("builder") == "kitchen_run" and plan.get("modules") else {}


def _local(piece: dict, point) -> tuple[float, float]:
    fp = piece["footprint"]
    c = fp["center"]
    rot = math.radians(float(fp.get("rotation_deg") or 0.0))
    dx, dy = float(point[0]) - float(c[0]), float(point[1]) - float(c[1])
    return math.cos(rot) * dx + math.sin(rot) * dy, -math.sin(rot) * dx + math.cos(rot) * dy


def worktop_z(item: dict, host: Optional[dict]) -> Optional[float]:
    """The height over the host's floor where a worktop item (``parametric.KITCHEN_DECOR_TYPES``) rests on a kitchen
    run built from modules (the plan's ``worktop_m``; on the hob plate's rings for a set standing on the hob), so the
    build places it with no ray (lesson UL111); None when the host has no such plan or the item's centre is not over
    a worktop stretch (a gap, a tall unit, off the run): then the rays decide as before."""
    plan = _plan_of(host)
    top = plan.get("worktop_m")
    if top is None or not item.get("center"):
        return None
    try:
        lx, ly = _local(host, item["center"])
    except (KeyError, TypeError, ValueError, IndexError):
        return None
    w, d = (float(v) for v in plan["footprint_m"][:2])
    if abs(ly) > d / 2.0 + 1e-6 or abs(lx) > w / 2.0 + 1e-6:
        return None
    on_top = False
    for m in plan["modules"]:
        if m.get("kind") != "worktop":
            continue
        x0 = float(m["pos_m"][0]) - float(m["size_m"][0]) / 2.0
        x1 = float(m["pos_m"][0]) + float(m["size_m"][0]) / 2.0
        if x0 - 1e-6 <= lx <= x1 + 1e-6:
            on_top = True
            for c in m.get("cutouts") or []:
                if c.get("kind") == "hob" and abs(lx - float(c["x_m"])) <= float(c["w_m"]) / 2.0 \
                        and item.get("type") == "cookware":
                    return round(float(top) + 0.0065, 4)       # the hob plate (5 mm) and its rings (1.5 mm)
    if not on_top:
        return None
    for m in plan["modules"]:
        if m.get("kind") == "tall_unit":
            x0 = float(m["pos_m"][0]) - float(m["size_m"][0]) / 2.0
            x1 = float(m["pos_m"][0]) + float(m["size_m"][0]) / 2.0
            if x0 - 1e-6 <= lx <= x1 + 1e-6:
                return None
    return round(float(top), 4)


def item_blocked(item: dict, host: Optional[dict]) -> Optional[str]:
    """Why a worktop item cannot stand where it is on its run as planned (the decor stage may have placed it before
    the refit added a tall unit or a rail): over a tall unit of the plan, under the plan's rail lower than its top
    (pure); None when it may stand."""
    plan = _plan_of(host)
    if not plan or not item.get("center"):
        return None
    try:
        lx, ly = _local(host, item["center"])
    except (KeyError, TypeError, ValueError, IndexError):
        return None
    iw = float((item.get("size") or [0.2, 0.2, 0.2])[0])
    ih = float((item.get("size") or [0.2, 0.2, 0.2])[2]) if len(item.get("size") or []) > 2 else 0.3
    for m in plan["modules"]:
        if m.get("kind") == "tall_unit":
            x0 = float(m["pos_m"][0]) - float(m["size_m"][0]) / 2.0
            x1 = float(m["pos_m"][0]) + float(m["size_m"][0]) / 2.0
            if lx + iw / 2.0 > x0 + 1e-6 and lx - iw / 2.0 < x1 - 1e-6:
                return f"it would stand in the tall unit of {host.get('id')} ({m.get('front')})"
    det = plan.get("details") if isinstance(plan.get("details"), dict) else {}
    if det.get("rail_m"):
        r0, r1 = det["rail_m"]
        clear = RAIL["z_over_worktop"] - 0.035 - RAIL["hang"] - 0.02
        idp = float((item.get("size") or [0.2, 0.2])[1])
        d = float(plan["footprint_m"][1])
        if lx + iw / 2.0 > r0 and lx - iw / 2.0 < r1 and ly + idp / 2.0 > d / 2.0 - RAIL["standoff"] - 0.06 \
                and ih > clear:
            return f"it would stand under the utensil rail of {host.get('id')} and reach its utensils"
    return None


def tall_unit_rects(piece: dict) -> list[tuple[tuple[float, float], tuple[float, float], float]]:
    """K1: ``[(centre, size, rotation_deg)]`` of the tall units of a kitchen run's plan in the world (pure): the
    completion's wall cabinets stop at them (``complete.wall_cabinets_for``)."""
    plan = _plan_of(piece)
    if not plan:
        return []
    fp = piece["footprint"]
    c = (float(fp["center"][0]), float(fp["center"][1]))
    rot = float(fp.get("rotation_deg") or 0.0)
    r = math.radians(rot)
    out = []
    for m in plan["modules"]:
        if m.get("kind") != "tall_unit":
            continue
        x, y = float(m["pos_m"][0]), float(m["pos_m"][1])
        out.append(((c[0] + math.cos(r) * x - math.sin(r) * y, c[1] + math.sin(r) * x + math.cos(r) * y),
                    (float(m["size_m"][0]), float(m["size_m"][1])), rot))
    return out


def run_boxes(piece: dict, floor_z: float) -> Optional[list[dict]]:
    """K8: the built boxes of a kitchen run from modules for a collision test (pure; world frame, as
    ``lighting.piece_box``): the run up to its worktop line and every module above it (a hood, a tall unit, the shelf
    frame) on its own; None for another piece (one box: ``lighting.piece_box``). A strip under a wall cabinet over a
    run with a hood was dropped because the run's one box reached the ceiling."""
    plan = _plan_of(piece)
    if not plan or plan.get("worktop_m") is None:
        return None
    fp = piece["footprint"]
    c = (float(fp["center"][0]), float(fp["center"][1]))
    rot = float(fp.get("rotation_deg") or 0.0)
    r = math.radians(rot)
    w, d = (float(v) for v in plan["footprint_m"][:2])
    top = float(plan["worktop_m"])

    def world(x, y):
        return [c[0] + math.cos(r) * x - math.sin(r) * y, c[1] + math.sin(r) * x + math.cos(r) * y]

    out = [{"id": piece.get("id"), "type": piece.get("type"), "center": [c[0], c[1], float(floor_z) + top / 2.0],
            "size": [w, d, top], "rotation_deg": rot}]
    for m in plan["modules"]:
        if m.get("kind") not in ("hood", "tall_unit"):
            continue
        mw, md, mh = (float(v) for v in m["size_m"])
        z0 = float(m.get("z_m") or 0.0)
        if m.get("kind") == "tall_unit":
            z0, mh = 0.0, z0 + mh
        else:
            mh = float(m.get("chimney_top_m") or (z0 + mh)) - z0
            if isinstance(m.get("frame"), dict):
                mw, md = max(mw, float(m["frame"]["w_m"])), max(md, float(m["frame"]["d_m"]))
        cxy = world(float(m["pos_m"][0]), float(m["pos_m"][1]))
        out.append({"id": piece.get("id"), "type": piece.get("type"),
                    "center": [cxy[0], cxy[1], float(floor_z) + z0 + mh / 2.0], "size": [mw, md, mh],
                    "rotation_deg": rot})
    return out


# --------------------------------------------------------------------------
# The shell: the splashback's look (K5, G3), the kitchen floor (K11)
# --------------------------------------------------------------------------

STONE_WORKTOPS = ("stone", "terrazzo")


def splashback_look(family: Optional[str], designs: Sequence[dict] = ()) -> Optional[dict]:
    """K5 / G3: the look of a kitchen's splashback band by its family (``FAMILY_KITCHEN[...]["splashback"]``):
    ``stone`` = the worktop's own stone where the run's design has a stone or terrazzo top (``designs``: the runs'
    designs), else a white marble slab; ``subway`` = white subway tiles; ``tiles`` = None (the wet walls' tiles, the
    rule of before). ``{"material", "colour", "reason"}``."""
    rule = family_rule(family)
    kind = rule.get("splashback")
    if kind == "subway":
        return {"material": "tiles_subway", "colour": "white",
                "reason": f"white subway tiles: the {rule['family']} family's splashback (G3)"}
    if kind != "stone":
        return None
    top = next((d.get("worktop") for d in designs if isinstance(d, dict) and d.get("worktop")), None)
    if top in STONE_WORKTOPS:
        try:
            from wenart.style import finishes as FIN
            slug = FIN.CABINET_WORKTOPS[top]
        except (ImportError, KeyError):
            slug = "marble_slab"
        return {"material": slug, "colour": None,
                "reason": f"the worktop's stone up the wall: the {rule['family']} family's stone splashback (K5)"}
    return {"material": "marble_slab", "colour": None,
            "reason": f"a white marble splashback: the {rule['family']} family's stone splashback over a "
                      f"{top or 'non-stone'} worktop (K5)"}


def floor_look(family: Optional[str]) -> Optional[dict]:
    """K11: the kitchen floor of the family (``FAMILY_KITCHEN[...]["floor"]``): large glossy porcelain tiles in the
    modern families, None elsewhere (the rule of before: the brief's wet-safe floor or the wet floor)."""
    rule = family_rule(family)
    if rule.get("floor") != FLOOR_TILE_SLUG:
        return None
    return {"material": FLOOR_TILE_SLUG, "colour": "off white",
            "reason": f"large glossy porcelain tiles: the {rule['family']} family's kitchen floor (K11)"}


# --------------------------------------------------------------------------
# M27 / U31: the review
# --------------------------------------------------------------------------

RUN_TYPES = ("kitchen_counter", "kitchen_island")
STYLING_MIN = 2                  # a kitchen with room for them holds at least this many styling sets ...
STYLING_FREE_M = 1.20            # ... when this much worktop is free of the sink, the hob and the tall units
STYLING_FULL = 6                 # a worktop with this many items in all is dressed, styling sets or not
FRIDGE_TYPES = ("fridge",)


def _built(f: dict) -> bool:
    return isinstance(f, dict) and f.get("build", True) is not False and isinstance(f.get("footprint"), dict)


def _family_of(building: dict, pieces: list) -> Optional[str]:
    for p in pieces:
        fam = ((p.get("asset") or {}).get("style_family") if isinstance(p.get("asset"), dict) else None) \
            or (p.get("design") or {}).get("style_family")
        if fam:
            return str(fam)
    return None


def _free_worktop(plan: dict) -> float:
    w = float(plan["footprint_m"][0])
    used = sum(float(m["size_m"][0]) for m in plan["modules"]
               if m.get("kind") == "tall_unit" or (m.get("kind") == "base_unit" and m.get("holds") in ("sink", "hob")))
    used += sum(float(g.get("w_m") or 0.0) for g in plan.get("gaps") or [])
    return max(0.0, w - used)


def review(building: Optional[dict], manifest: Optional[dict] = None, check: str = "M27") -> tuple[list[dict], int]:
    """M27 / U31 (module docstring): ``(findings, kitchens checked)``; each finding ``{"check", "severity", "target",
    "room_id", "message", "problem", "lesson"}``. Per kitchen (a room with a built kitchen run from modules): (a) a
    bare worktop beyond U11: fewer than ``STYLING_MIN`` styling sets of its family while ``STYLING_FREE_M`` is free
    (minor); (b) a wall cabinet with no LED strip under it (the scene's light rig: a strip dropped, with its reason;
    major) and a run's own wall units with none (minor); (c) an island hob without a hood (major); (d) a family detail
    not built: a run planned before the rule (no ``details`` record), an island of a waterfall family without its
    waterfall ends, an island with its stools on its back and no knee space (minor); (e) a kitchen with no fridge (no
    fridge piece, no fridge built into a run, no fridge column; major)."""
    b = building or {}
    pieces = [f for f in b.get("furniture") or [] if _built(f)]
    decor = [x for x in b.get("decor") or [] if isinstance(x, dict)]
    family = _family_of(b, pieces)
    rule = family_rule(family)
    rooms: dict[str, list] = {}
    for f in pieces:
        if f.get("type") in RUN_TYPES and _plan_of(f):
            rooms.setdefault(str(f.get("room_id")), []).append(f)
    out: list[dict] = []

    def add(sev, target, room_id, problem, message):
        out.append({"check": check, "severity": sev, "target": target, "room_id": room_id, "problem": problem,
                    "message": message, "lesson": "UL118" if problem in ("styling", "waterfall", "column", "fridge")
                    else "UL115", "family": rule["family"]})

    rig_rooms = (((manifest or {}).get("lighting") or {}).get("rig") or {}).get("rooms") or {}
    for rid, runs in sorted(rooms.items()):
        run_ids = {r["id"] for r in runs}
        here = [x for x in decor if x.get("host_id") in run_ids]
        sets = [x for x in here if x.get("type") in STYLING_TYPES]
        free = sum(_free_worktop(_plan_of(r)) for r in runs)
        need = min(STYLING_MIN, len(rule.get("styling") or ()))
        # a worktop that holds STYLING_FULL items or more is dressed (windows down to the worktop leave no more room)
        if need and len(sets) < need and len(here) < STYLING_FULL and free >= STYLING_FREE_M - 1e-9:
            add("minor", rid, rid, "styling",
                f"the kitchen worktop of {rid} holds {len(sets)} styling set(s) ({free:.1f} m free): the "
                f"{rule['family']} family's kitchen shows {', '.join(t.replace('_', ' ') for t in rule['styling'][:4])}"
                " (beyond the small appliances of U11)")
        for r in runs:
            plan = _plan_of(r)
            if not isinstance(plan.get("details"), dict):
                add("minor", r["id"], rid, "details",
                    f"the kitchen run {r['id']} was planned before the kitchen details of 29 Oct 2026 (no details "
                    "record): rerun the refit")
                continue
            det = plan["details"]
            island = r.get("type") == "kitchen_island"
            hob = any(m.get("holds") == "hob" for m in plan["modules"])
            if island and hob and not any(m.get("kind") == "hood" for m in plan["modules"]):
                add("major", r["id"], rid, "island_hood", f"the island {r['id']} holds a hob with no hood over it")
            if island and rule.get("waterfall") and not any(m.get("kind") == "waterfall" for m in plan["modules"]) \
                    and not plan.get("gaps"):
                add("minor", r["id"], rid, "waterfall",
                    f"the island {r['id']} of a {rule['family']} kitchen has no waterfall ends")
            if island and det.get("seat_side") == "back" and not det.get("overhang_m") \
                    and float(plan["footprint_m"][1]) - OVERHANG["base_d"] >= OVERHANG["min_m"] - 1e-9:
                add("minor", r["id"], rid, "overhang",
                    f"the stools at the island {r['id']} have no knee space under its worktop")
            if any(m.get("kind") == "wall_unit" for m in plan["modules"]):
                add("minor", r["id"], rid, "led",
                    f"the wall units of the run {r['id']} have no LED strip under them (the light rig lights the "
                    "wall cabinets only)")
        room_pieces = [f for f in pieces if str(f.get("room_id")) == rid]
        fridge = any(f.get("type") in FRIDGE_TYPES for f in room_pieces) or any(
            m.get("holds") == "fridge" or str(m.get("front") or "").startswith("fridge")
            for r in runs for m in _plan_of(r)["modules"])
        if not fridge:
            add("major", rid, rid, "fridge",
                f"the kitchen {rid} has no fridge: no fridge piece, no fridge built into a run, no fridge column (K1)")
        rig = rig_rooms.get(rid) if isinstance(rig_rooms, dict) else None
        if isinstance(rig, dict):
            for dr in rig.get("dropped") or []:
                if isinstance(dr, dict) and dr.get("kind") == "strip":
                    add("major", rid, rid, "led", f"no LED strip under a wall cabinet of {rid}: {dr.get('reason')}")
    return out, len(rooms)
