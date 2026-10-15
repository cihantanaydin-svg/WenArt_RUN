"""Module builders (Milestone 13, track T2; docs/milestone13.md §3.0 K1, §12 D4, §13.2): a drawn anchor the library
cannot fit is built from real product modules, never left out and never a grey box.

What: ``module_plan(piece, style=None)`` (pure, no ``bpy``) turns a drawn piece into a plan of real modules
(``{builder, modules: [{kind, size_m, pos_m, rot_deg, material}], footprint_m, height_m, products}``), or None when
no module builder exists for its type or the modules cannot match the drawn footprint within ``MODULE_FIT_TOL``
(then the parametric family of ``wenart.blender.parametric`` builds the exact footprint). ``module_parts(plan)``
makes the parts (``parametric`` part dicts: ``verts``, ``faces``, ``key``, ``role``) in the piece frame (width X,
depth Y, front -Y, Z up from the floor); ``build_module(plan, piece, materials)`` makes the Blender object (``bpy``
inside) with one material slot per part key, the Bevel modifier of ``furniture.add_bevel`` and
``wenart_method = "module"``.

Builders (``MODULE_BUILDERS``: furniture type -> builder):

- ``wardrobe_run`` (wardrobe): frames of 0.50 / 0.75 / 1.00 m composed to the drawn run with end fillers, a plinth,
  a top panel, doors in the design's front style with bar handles at the meeting edges;
- ``table_long`` (table_dining): a top of real thickness on four tapered legs with an apron, or on two trestles
  for runs of 2.2 m and more; a drawn footprint deeper than a real table (``TABLE_DEPTH_MAX_M``) includes its
  chairs (CLAUDE.md: "a table footprint that includes its chairs"): it is split into the table and the chairs
  along both long sides, recorded in ``plan["split"]`` so the fit logs the piece ``adjusted_by_ai``;
- ``sofa_l`` (sofa_corner, or a ``sofa`` with ``shape: L``): straight seat modules of 0.90-1.10 m with an arm at the far
  end, and a chaise module 0.90 wide and 1.60-1.80 m deep on ``chaise_side`` (the rectangles of
  ``parametric.l_parts``), seat and back cushions, a base on short legs;
- ``kitchen_run`` (kitchen_counter, kitchen_island): base units 0.60 m deep in real widths, a 0.04 m worktop at
  0.90 m, a recessed plinth, fronts and handles, a sink cutout and a hob at the drawn or inferred places
  (``piece["module_hints"]``: ``sink_x_m`` / ``sink_pos_m`` / ``window_pos_m`` for the sink under the window,
  ``hob_x_m`` / ``hob_pos_m``; without a hint no cutout is made, because the drawn sink and stove are their own
  pieces), wall units 0.35 m deep from 1.40 to 2.10 m when ``module_hints.wall_units`` is true;
- ``bath_set`` (washbasin at least 0.45 m deep: a wall-hung vanity with drawer fronts, a ceramic top with one or
  two inset basins and taps and a framed mirror above; shower: a tray of a real product size with the glass
  screen and shower set of ``parametric._shower``). The toilet stays with the parametric family.

Why: the three real projects left 43 (real04), 46 and 25 drawn pieces unbuilt or as plain boxes because the
library has no model near the drawn size (docs/milestone13.md §1.3: 3.35 m tables, 2.57 and 3.11 m wardrobe runs,
a 4.38 x 1.97 m corner sofa, kitchen runs). The user's decision D4 ("yes, but we need a good model") asks for
fallbacks that look like real products: real module sizes, real proportions and PBR material slots.

How: every size comes from a real product range, cited at the constant; module widths are composed by
``compose_run`` (a small dynamic programme over the real widths, the remainder as end fillers within
``WARDROBE_FILLER_MAX_M`` / ``KITCHEN_FILLER_MAX_M``, as fitters do on site); the plan keeps the drawn footprint
exactly where the modules can, and records the deviation in ``plan["fit"]``. The parts reuse the primitives and
the cabinet fronts of ``wenart.blender.parametric`` (boxes, cylinders, frustums, superellipsoid cushions,
``cabinet_fronts`` in the design's front style). Material keys are the ``parametric.MATERIAL_KEYS`` the style
fills (``wood``, ``front``, ``handle``, ``dark``, ``worktop``, ``fabric``, ``steel``, ``ceramic``, ``glass``,
``mirror``, ``painted``), so every object has several real material slots.

Sources of the module sizes (checked 12 Oct 2026; ikea.com is blocked by this session's proxy, so the IKEA product
records were read through the GitHub mirror felixrinker/floor-planner @408e3d7c, ``daten/cache/*.json`` and
``preisvergleich_at_sk.csv``, which carry the ikea.com/at/de product URLs and ``sizeText`` of each article; on
15 Oct 2026 that repository answered 404 and ikea.com stayed blocked, so the PAX and METOD numbers keep their
12 Oct provenance and the track report flags them; the US cabinet numbers were re-read on 15 Oct from the utariga
file named below, the tables, chairs, trays, basins and wardrobe depths come from the project's own size table):

- IKEA PAX wardrobe frames ("Korpus Kleiderschrank"): 50x58x236 (art. 904.582.21), 75x58x236 (904.582.35),
  100x58x236 (804.582.07); combinations 150 / 175 / 200 / 250 / 375 x 58 x 201 or 236 cm; a 35 cm deep variant
  (53x35x201 corner element) -> frame widths 0.50 / 0.75 / 1.00 m, depths 0.35 / 0.58 m, heights 2.01 / 2.36 m.
- IKEA METOD kitchen carcasses ("Unterschrank" base 40x37x80, 60x60x80, 80x60x80, corner 88x60x80 cm;
  "Wandschrank" wall 60x37x100, 80x37x100, 40x100 cm; ikea.com/at/de/p/metod-...-50205626 / -20205538 / -90205530)
  -> base widths 0.40 / 0.60 / 0.80 m, base depth 0.60 m, wall depth 0.37 m, wall widths 0.40 / 0.60 / 0.80 m.
- US cabinetry nominal sizes (chrisrogers3d/utariga @da8dbfad, docs/research/kitchen/layout-rules-and-dimensions.md,
  compiled from bobvila.com and sebringdesignbuild.com cabinet guides and the NKBA planning guidelines): base
  widths in 3 in steps 9-48 in (0.30 / 0.45 / 0.90 m = 12 / 18 / 36 in), base box depth 610 mm, counter height
  36 in = 914 mm, toe kick 76 mm deep, upper cabinets 305 mm deep, sink base 762 / 914 mm, cooktop cutout
  699-749 x 508-533 mm (30 in class), fillers 51-76 mm.
- the project's own size table ``wenart/recognition/size_table.yaml`` (product rows: kitchen base units 0.6 deep
  with the worktop at 0.85-0.95 m, wall units 0.3-1.2 x 0.3-0.37, wardrobes 0.5-0.7 deep, shower trays
  0.80-1.20 x 0.80-0.90, washbasins 0.45-0.80 x 0.35-0.50, chairs 0.45 x 0.45, chaises 0.55-0.95 x 1.30-2.00,
  dining tables 0.80-3.00 x 0.70-1.20 with the 10-seat 3.35 x 1.00 of real02).
- docs/milestone13.md §13.1 (the lead's contract): straight sofa modules 0.90-1.10 m, chaise 1.60-1.80 m deep,
  worktop 0.04 m at 0.90 m, wall units 0.35 m deep at 1.40-2.10 m, vanity 0.60 x 0.46-0.60 m. The chaise depths
  are the size table's chaise products (0.65 x 1.60, 0.75 x 1.70, 0.85 x 1.80 m); the straight module is one and
  a half seats of the size table's sofa products (2-seat 130 / 160, 3-seat 200 / 220: 0.65-0.73 m per seat).
- seat pitch 0.60 m per cover: Neufert's 60 cm per place as quoted by the secondary compilations read in the
  Milestone 13 placement research (docs/milestone13.md §2.4; jhkim0759/SceneConductor scene_norms.yaml,
  interaeronav/TokenEfficiencyEngine 19_interior_design/06).
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart.blender import parametric as P
from wenart.blender.proxies import proxy_height

Part = dict

# --------------------------------------------------------------------------
# Real module sizes (metres), each with its source (module docstring)
# --------------------------------------------------------------------------

MODULE_FIT_TOL = 0.10                 # the plan's footprint may differ from the drawn one by this share (per side)
MODULE_METHOD = "module"              # asset.method of a piece built here (docs/milestone13.md §13.2)

# Wardrobe runs: IKEA PAX frames (mirror of ikea.com/at/de, module docstring).
WARDROBE_FRAME_WIDTHS_M: tuple[float, ...] = (0.50, 0.75, 1.00)
WARDROBE_FRAME_DEPTHS_M: tuple[float, ...] = (0.35, 0.58)
WARDROBE_FRAME_HEIGHTS_M: tuple[float, ...] = (2.01, 2.36)
WARDROBE_FILLER_MAX_M = 0.13          # the remainder of a 0.25 m grid split on both ends (fitters' scribe panels)
WARDROBE_PLINTH_M = 0.08              # PAX frames stand on the floor; a built-in run gets a recessed plinth (D4 look)
WARDROBE_TOP_M = 0.02
WARDROBE_DOOR_MAX_M = 0.50            # PAX hinged doors are 50 cm wide: a 100 frame takes two, a 50 / 75 one
WARDROBE_DEPTH_RANGE_M = (0.35, 0.80)

# Kitchen runs: IKEA METOD (0.40 / 0.60 / 0.80) and the US 3 in series (0.30 / 0.45 / 0.90 = 12 / 18 / 36 in).
KITCHEN_BASE_WIDTHS_M: tuple[float, ...] = (0.30, 0.40, 0.45, 0.60, 0.80, 0.90)
KITCHEN_BASE_DEPTH_M = 0.60           # METOD 60 deep; US 24 in = 610 mm
KITCHEN_WORKTOP_HEIGHT_M = 0.90       # the contract; METOD 80 carcass + 8 legs + worktop; US 36 in = 914 mm
KITCHEN_WORKTOP_RANGE_M = (0.80, 1.20) # a drawn height in this range is a counter height and is kept (size table:
                                      # kitchen_counter 0.85-0.95, kitchen_island 0.85-1.10 bar height); outside it
                                      # the contract's 0.90 m, noted in the plan (reviewer fix 15 Oct 2026: a drawn
                                      # 0.85 m was silently made 0.90 m, a drawn 1.40 m became a 1.40 m counter)
KITCHEN_WORKTOP_M = 0.04              # the contract (docs/milestone13.md §13.1)
KITCHEN_PLINTH_M = 0.10               # METOD legs 8 cm, plinth 8-10 cm; US toe kick 76 mm deep
KITCHEN_PLINTH_RECESS_M = 0.06
KITCHEN_FILLER_MAX_M = 0.08           # NKBA / US guides: fillers 51-76 mm (module docstring)
KITCHEN_END_SHIFT_MAX_M = 0.10        # a sink or hob unit this close to the run's end moves to the wall (no slit
                                      # thinner than a filler); a wider slit beside it becomes a filler panel
KITCHEN_SINK_UNIT_WIDTHS_M: tuple[float, ...] = (0.60, 0.80, 0.90)   # METOD 60 sink base; US 30 / 36 in sink bases
KITCHEN_HOB_UNIT_WIDTHS_M: tuple[float, ...] = (0.60, 0.90)          # 60 cm hob class (size table stove 0.60); 36 in
KITCHEN_HOB_PLATE_M = (0.58, 0.51)    # a 60 cm class hob plate on the worktop (US 30 in cutout 699-749 x 508-533 mm
                                      # per the utariga compilation; the 60 cm class is the contract's EU size)
KITCHEN_WALL_WIDTHS_M: tuple[float, ...] = (0.40, 0.60, 0.80)        # METOD wall carcasses 40 / 60 / 80
KITCHEN_WALL_DEPTH_M = 0.35           # the contract (METOD 37, US 12 in = 305 mm)
KITCHEN_WALL_BOTTOM_M = 1.40          # the contract: wall units from 1.40 to 2.10 m
KITCHEN_WALL_TOP_M = 2.10
KITCHEN_DRAWER_UNIT_W_M = 0.60        # a 60 unit takes three drawers (METOD / MAXIMERA); wider ones two doors

# Tables: wenart/recognition/size_table.yaml (table_dining depth 0.70-1.20; chair 0.45 x 0.45).
TABLE_DEPTH_MAX_M = 1.20              # a drawn footprint deeper than this includes its chairs
TABLE_DEPTH_RANGE_M = (0.80, 1.10)    # the table left after the split
TABLE_TOP_M = 0.04
TABLE_TRESTLE_FROM_M = 2.20           # tables this long stand on two trestles (slab legs) instead of four legs
CHAIR_SIZE_M = (0.45, 0.45)           # the size table's chair product
CHAIR_PITCH_M = 0.60                  # Neufert's 60 cm per cover (secondary compilations, module docstring)
CHAIR_TUCK_M = 0.05                   # a chair's seat slides this far under the table edge
CHAIR_ZONE_M = 0.50                   # the band a tucked chair needs beyond the table edge

# L sofas: the contract's module ranges; the chaise width of parametric.l_parts (schemas.L_CHAISE_WIDTH_M).
SOFA_MODULE_RANGE_M = (0.90, 1.10)
SOFA_CHAISE_DEPTH_RANGE_M = (1.60, 1.80)
SOFA_CHAISE_WIDTHS_M: tuple[float, ...] = (0.85, 0.90, 0.95, 1.00)
SOFA_ARM_WIDTHS_M: tuple[float, ...] = (0.15, 0.20, 0.25)
SOFA_BACK_M = 0.22
SOFA_SEAT_DEPTH_M = P.L_SEAT_DEPTH_M  # the main seat rectangle of l_parts (incl. the back)
SOFA_LEG_M = 0.10
SOFA_CUSHION_M = 0.14

# Bath set: the size table's products (shower trays, washbasins) and the contract's vanity depth.
SHOWER_TRAYS_M: tuple[tuple[float, float], ...] = ((0.90, 0.90), (0.80, 0.80), (1.00, 0.80), (1.20, 0.80), (1.20, 0.90))
VANITY_DEPTH_RANGE_M = (0.45, 0.60)   # the contract 0.46-0.60; looks.VANITY_MIN_DEPTH_M = 0.45 decides the vanity look
VANITY_WIDTH_RANGE_M = (0.45, 1.60)
VANITY_DOUBLE_FROM_M = 1.10           # two basins from this width (assumed, noted in the plan)
VANITY_BOTTOM_M = 0.30                # wall-hung: free floor under the cabinet (parametric._vanity)
VANITY_CABINET_MIN_H_M = 0.25         # the smallest vanity cabinet (one drawer front); a washbasin drawn lower than
                                      # VANITY_BOTTOM_M + top + this (0.58 m; the size table allows 0.10 m: a counter
                                      # bowl) is not a vanity and stays with the parametric family (reviewer fix
                                      # 15 Oct 2026: it got a cabinet of negative height)
VANITY_MIRROR_H_M = 0.80
VANITY_MIRROR_BOTTOM_MIN_M = 1.15
VANITY_MIRROR_DEPTH_M = 0.03
BASIN_M = (0.50, 0.36, 0.14)          # bowl width, depth, basin depth (parametric._vanity)

MODULE_BUILDERS: dict[str, str] = {
    "wardrobe": "wardrobe_run",
    "table_dining": "table_long",
    "sofa_corner": "sofa_l",
    "kitchen_counter": "kitchen_run",
    "kitchen_island": "kitchen_run",
    "washbasin": "bath_set",
    "shower": "bath_set",
}


# --------------------------------------------------------------------------
# Pure helpers
# --------------------------------------------------------------------------

def _mm(v: float) -> int:
    return int(round(float(v) * 1000.0))


def compose_run(width: float, sizes: Sequence[float], max_filler: float) -> Optional[dict]:
    """Compose ``width`` from the real module ``sizes`` (metres): the combination whose sum is the largest not
    above ``width`` (ties: fewer modules, then the larger ones first), the remainder split as two end fillers.
    Returns ``{"widths": [..], "filler_m": per end, "sum_m"}`` or None when the width is below the smallest module
    or the fillers would exceed ``max_filler`` (pure dynamic programme over millimetres)."""
    target = _mm(width)
    steps = sorted({_mm(s) for s in sizes}, reverse=True)
    if not steps or target < min(steps):
        return None
    best: dict[int, tuple[int, list[int]]] = {0: (0, [])}            # sum -> (count, widths)
    for total in range(1, target + 1):
        for s in steps:
            prev = best.get(total - s)
            if prev is None:
                continue
            cand = (prev[0] + 1, sorted(prev[1] + [s], reverse=True))
            cur = best.get(total)
            if cur is None or cand[0] < cur[0] or (cand[0] == cur[0] and cand[1] > cur[1]):
                best[total] = cand
    reach = max(t for t in best if t <= target)
    count, widths = best[reach]
    filler = (target - reach) / 2000.0
    if filler > max_filler + 1e-9:
        return None
    return {"widths": [w / 1000.0 for w in widths], "filler_m": round(filler, 4), "sum_m": reach / 1000.0}


def nearest(value: float, options: Sequence[float]) -> float:
    return min(options, key=lambda o: abs(o - value))


def _fit_record(drawn: Sequence[float], built: Sequence[float], tol: float = MODULE_FIT_TOL) -> dict:
    dw, dd = float(built[0]) - float(drawn[0]), float(built[1]) - float(drawn[1])
    rel = max(abs(dw) / max(float(drawn[0]), 1e-6), abs(dd) / max(float(drawn[1]), 1e-6))
    return {"dw_m": round(dw, 4), "dd_m": round(dd, 4), "rel": round(rel, 4), "tol": tol, "within_cap": rel <= tol + 1e-9}


def _hints(piece: dict) -> dict:
    hints = piece.get("module_hints")
    return hints if isinstance(hints, dict) else {}


def _local_x(piece: dict, pos) -> Optional[float]:
    """A world point's x in the piece frame (along the run), or None."""
    if not pos or len(pos) < 2:
        return None
    fp = piece.get("footprint") or {}
    c = fp.get("center") or [0.0, 0.0]
    rot = math.radians(float(fp.get("rotation_deg") or 0.0))
    dx, dy = float(pos[0]) - float(c[0]), float(pos[1]) - float(c[1])
    return math.cos(rot) * dx + math.sin(rot) * dy


def _module(kind: str, size, pos, material: str, rot_deg: float = 0.0, **extra) -> dict:
    rec = {"kind": kind, "size_m": [round(float(v), 4) for v in size], "pos_m": [round(float(v), 4) for v in pos],
           "rot_deg": float(rot_deg), "material": material}
    rec.update(extra)
    return rec


def _piece_size(piece: dict) -> tuple[float, float, float]:
    fp = piece["footprint"]
    w, d = float(fp["size"][0]), float(fp["size"][1])
    h, _assumed = proxy_height(piece["type"], piece.get("height"))
    return w, d, float(h)


# --------------------------------------------------------------------------
# Plans
# --------------------------------------------------------------------------

def plan_wardrobe_run(piece: dict, style: Optional[dict] = None) -> Optional[dict]:
    """PAX-style frames composed to the drawn run (end fillers), a plinth, a top, doors with handles."""
    w, d, h = _piece_size(piece)
    if not (WARDROBE_DEPTH_RANGE_M[0] - 1e-9 <= d <= WARDROBE_DEPTH_RANGE_M[1] + 1e-9):
        return None
    run = compose_run(w, WARDROBE_FRAME_WIDTHS_M, WARDROBE_FILLER_MAX_M)
    if run is None:
        return None
    given = piece.get("height")
    if isinstance(given, (int, float)) and not isinstance(given, bool) and given > 1.0:
        frame_h = float(given) - WARDROBE_PLINTH_M                     # the drawn height is kept
    else:
        frame_h = nearest(h - WARDROBE_PLINTH_M, WARDROBE_FRAME_HEIGHTS_M)
    height = frame_h + WARDROBE_PLINTH_M
    depth_product = nearest(d, WARDROBE_FRAME_DEPTHS_M)
    modules = [_module("plinth", (w - 2 * 0.0, d - 0.04, WARDROBE_PLINTH_M), (0.0, 0.02), "dark")]
    x = -w / 2.0 + run["filler_m"]
    products: list[str] = []
    for i, fw in enumerate(run["widths"]):
        doors = 2 if fw > WARDROBE_DOOR_MAX_M + 1e-9 and fw >= 1.0 - 1e-9 else 1
        modules.append(_module("frame", (fw, d, frame_h), (x + fw / 2.0, 0.0), "front", z_m=WARDROBE_PLINTH_M,
                               doors=doors, hinge="left" if i % 2 == 0 else "right",
                               product=f"PAX frame {fw * 100:.0f}x{depth_product * 100:.0f}x{frame_h * 100:.0f} cm"))
        products.append(modules[-1]["product"])
        x += fw
    if run["filler_m"] > 1e-9:
        for sx in (-1, 1):
            modules.append(_module("filler", (run["filler_m"], d, frame_h),
                                   (sx * (w / 2.0 - run["filler_m"] / 2.0), 0.0), "front", z_m=WARDROBE_PLINTH_M))
    modules.append(_module("top", (w, d, WARDROBE_TOP_M), (0.0, 0.0), "wood", z_m=height - WARDROBE_TOP_M))
    notes = [f"frames {' + '.join(f'{v:.2f}' for v in run['widths'])} m" + (
        f" with {run['filler_m'] * 100:.1f} cm fillers at both ends" if run["filler_m"] > 1e-9 else " (no filler)")]
    if abs(d - depth_product) > 0.02:
        notes.append(f"depth {d:.2f} m made to measure (nearest PAX depth {depth_product:.2f} m)")
    return {"builder": "wardrobe_run", "type": piece["type"], "modules": modules, "footprint_m": [w, d],
            "height_m": round(height, 4), "drawn_m": [w, d], "fit": _fit_record((w, d), (w, d)),
            "products": sorted(set(products), key=products.index), "notes": notes,
            "design": P.piece_design(piece)}


def plan_table_long(piece: dict, style: Optional[dict] = None) -> Optional[dict]:
    """A long table on legs or trestles; a footprint deeper than a real table is split into table and chairs."""
    w, d, h = _piece_size(piece)
    if w < 0.80 - 1e-9 or d < 0.60 - 1e-9:
        return None
    split = None
    table_d = d
    if d > TABLE_DEPTH_MAX_M + 1e-9:
        table_d = min(TABLE_DEPTH_RANGE_M[1], max(TABLE_DEPTH_RANGE_M[0], d - 2 * CHAIR_ZONE_M))
        split = {"table_m": [w, round(table_d, 4)], "reason": (f"the drawn footprint is {d:.2f} m deep, more than a "
                                                               f"real table ({TABLE_DEPTH_MAX_M} m): it includes the "
                                                               "chairs along both long sides (CLAUDE.md)")}
    legs = "trestles" if w >= TABLE_TRESTLE_FROM_M - 1e-9 else "legs"
    modules = [_module("top", (w, table_d, TABLE_TOP_M), (0.0, 0.0), "wood", z_m=h - TABLE_TOP_M, support=legs)]
    if legs == "trestles":
        tw = min(0.10, w * 0.05)
        for sx in (-1, 1):
            modules.append(_module("trestle", (tw, table_d - 0.30, h - TABLE_TOP_M),
                                   (sx * (w / 2.0 - 0.45), 0.0), "wood"))
    else:
        leg = min(0.07, w * 0.05, table_d * 0.08)
        inset = min(0.08, w * 0.06, table_d * 0.06)
        for sx in (-1, 1):
            for sy in (-1, 1):
                modules.append(_module("leg", (leg, leg, h - TABLE_TOP_M),
                                       (sx * (w / 2.0 - inset - leg / 2.0), sy * (table_d / 2.0 - inset - leg / 2.0)),
                                       "wood"))
    seats = 0
    if split is not None:
        per_side = max(1, int((w - 0.30 + 1e-9) // CHAIR_PITCH_M))
        pitch = (w - 0.30) / per_side
        cy = table_d / 2.0 + CHAIR_SIZE_M[1] / 2.0 - CHAIR_TUCK_M
        for k in range(per_side):
            cx = -w / 2.0 + 0.15 + pitch * (k + 0.5)
            # the chair's front (-Y in its own frame) faces the table: the -Y side chairs turn 180 degrees
            modules.append(_module("chair", (CHAIR_SIZE_M[0], CHAIR_SIZE_M[1], 0.90), (cx, -cy), "wood", rot_deg=180.0))
            modules.append(_module("chair", (CHAIR_SIZE_M[0], CHAIR_SIZE_M[1], 0.90), (cx, cy), "wood", rot_deg=0.0))
        seats = 2 * per_side
        split["chairs"] = seats
        split["chair_m"] = list(CHAIR_SIZE_M)
    built_d = d if split is None else max(d, 2 * cy + CHAIR_SIZE_M[1])
    fit = _fit_record((w, d), (w, built_d))
    if not fit["within_cap"]:
        return None
    products = [f"dining table {w:.2f} x {table_d:.2f} m on {legs}" + (f" with {seats} chairs" if seats else "")]
    return {"builder": "table_long", "type": piece["type"], "modules": modules, "footprint_m": [w, round(built_d, 4)],
            "height_m": round(h, 4), "drawn_m": [w, d], "fit": fit, "products": products, "split": split,
            "seats": seats, "notes": [f"{legs}: {'two trestles' if legs == 'trestles' else 'four tapered legs'}"],
            "design": P.piece_design(piece)}


def _sofa_modules(w: float) -> Optional[tuple[float, float, list[float]]]:
    """``(arm width, chaise width, straight module widths)`` whose sum is exactly ``w`` with every module inside
    ``SOFA_MODULE_RANGE_M`` (the arm and chaise widths are searched over their product options); None when no
    combination keeps the modules in range."""
    lo, hi = SOFA_MODULE_RANGE_M
    best = None
    for arm in SOFA_ARM_WIDTHS_M:
        for cw in SOFA_CHAISE_WIDTHS_M:
            run = w - arm - cw
            if run < lo - 1e-9:
                continue
            n = max(1, int(round(run / ((lo + hi) / 2.0))))
            for count in (n, n + 1, max(1, n - 1)):
                mw = run / count
                if lo - 1e-9 <= mw <= hi + 1e-9:
                    score = (abs(mw - 1.0), abs(arm - 0.20), abs(cw - P.L_CHAISE_WIDTH_M))
                    if best is None or score < best[0]:
                        best = (score, arm, cw, [mw] * count)
    return None if best is None else (best[1], best[2], best[3])


def plan_sofa_l(piece: dict, style: Optional[dict] = None) -> Optional[dict]:
    """Straight seat modules with an arm at the far end and a chaise module on ``chaise_side``."""
    w, d, h = _piece_size(piece)
    if piece.get("type") != "sofa_corner" and str(piece.get("shape") or "").upper() != "L":
        return None
    got = _sofa_modules(w)
    if got is None:
        return None
    arm, cw, widths = got
    side = piece.get("chaise_side") if piece.get("chaise_side") in ("left", "right") else "right"
    chaise_seat = min(SOFA_CHAISE_DEPTH_RANGE_M[1], max(SOFA_CHAISE_DEPTH_RANGE_M[0], d - SOFA_BACK_M))
    depth = chaise_seat + SOFA_BACK_M
    fit = _fit_record((w, d), (w, depth))
    if not fit["within_cap"]:
        return None
    main, chaise = P.l_parts((w, depth), side, depth, SOFA_SEAT_DEPTH_M, cw)
    mx0, mx1, my0, my1 = main
    cx0, cx1, cy0, cy1 = chaise
    seat_y = (my0 + my1) / 2.0
    modules = [_module("back", (w, SOFA_BACK_M, h), (0.0, depth / 2.0 - SOFA_BACK_M / 2.0), "fabric")]
    sign = -1.0 if side == "right" else 1.0            # the arm at the end away from the chaise
    x = sign * (w / 2.0) - sign * arm / 2.0
    modules.append(_module("arm", (arm, my1 - my0 - SOFA_BACK_M, min(0.65, h * 0.78)),
                           (x, seat_y - SOFA_BACK_M / 2.0), "fabric"))
    x = sign * (w / 2.0 - arm)
    for mw in widths:
        x_c = x - sign * mw / 2.0
        modules.append(_module("seat_module", (mw, my1 - my0 - SOFA_BACK_M, h), (x_c, seat_y - SOFA_BACK_M / 2.0),
                               "fabric", product=f"sofa module {mw:.2f} m"))
        x -= sign * mw
    modules.append(_module("chaise_module", (cx1 - cx0, cy1 - cy0 - SOFA_BACK_M, h),
                           ((cx0 + cx1) / 2.0, (cy0 + cy1 - SOFA_BACK_M) / 2.0), "fabric",
                           product=f"chaise module {cx1 - cx0:.2f} x {chaise_seat:.2f} m"))
    products = [m["product"] for m in modules if m.get("product")]
    return {"builder": "sofa_l", "type": piece["type"], "modules": modules, "footprint_m": [w, round(depth, 4)],
            "height_m": round(h, 4), "drawn_m": [w, d], "fit": fit, "products": sorted(set(products), key=products.index),
            "chaise_side": side, "chaise_side_assumed": piece.get("chaise_side") not in ("left", "right"),
            "rectangles": [[round(v, 4) for v in main], [round(v, 4) for v in chaise]],
            "notes": [f"arm {arm:.2f} m, {len(widths)} straight module(s) of {widths[0]:.2f} m, chaise {cw:.2f} x "
                      f"{chaise_seat:.2f} m on the {side}"], "design": P.piece_design(piece)}


def _place_fixed(w: float, x: Optional[float], unit_w: float) -> Optional[tuple[float, float]]:
    """``(x0, x1)`` of a fixed unit centred near ``x`` (piece frame), kept inside the run."""
    if x is None:
        return None
    x0 = min(max(x - unit_w / 2.0, -w / 2.0), w / 2.0 - unit_w)
    return (x0, x0 + unit_w)


def plan_kitchen_run(piece: dict, style: Optional[dict] = None) -> Optional[dict]:
    """Base units composed to the run (fixed sink and hob units first), the worktop with its cutouts, plinth, fronts
    and handles; wall units above when the hints ask for them."""
    w, d, h = _piece_size(piece)
    if w < min(KITCHEN_BASE_WIDTHS_M) - 1e-9 or d < 0.45 - 1e-9:
        return None
    hints = _hints(piece)
    island = piece.get("type") == "kitchen_island"
    given = piece.get("height")
    drawn_h = float(given) if isinstance(given, (int, float)) and not isinstance(given, bool) and given > 0 else None
    in_range = drawn_h is not None and KITCHEN_WORKTOP_RANGE_M[0] - 1e-9 <= drawn_h <= KITCHEN_WORKTOP_RANGE_M[1] + 1e-9
    worktop_z = drawn_h if in_range else KITCHEN_WORKTOP_HEIGHT_M
    fixed: list[tuple[float, float, str]] = []
    sink_x = hints.get("sink_x_m")
    if sink_x is None:
        sink_x = _local_x(piece, hints.get("sink_pos_m")) if hints.get("sink_pos_m") else _local_x(piece, hints.get("window_pos_m"))
    hob_x = hints.get("hob_x_m")
    if hob_x is None and hints.get("hob_pos_m"):
        hob_x = _local_x(piece, hints["hob_pos_m"])
    if sink_x is not None:
        sw = nearest(float(hints.get("sink_w_m") or KITCHEN_SINK_UNIT_WIDTHS_M[0]), KITCHEN_SINK_UNIT_WIDTHS_M)
        span = _place_fixed(w, float(sink_x), min(sw, w))
        if span is not None:
            fixed.append((span[0], span[1], "sink"))
    if hob_x is not None:
        hw = nearest(float(hints.get("hob_w_m") or KITCHEN_HOB_UNIT_WIDTHS_M[0]), KITCHEN_HOB_UNIT_WIDTHS_M)
        span = _place_fixed(w, float(hob_x), min(hw, w))
        if span is not None and not any(span[0] < f[1] - 1e-9 and span[1] > f[0] + 1e-9 for f in fixed):
            fixed.append((span[0], span[1], "hob"))
    fixed.sort()
    # a fixed unit near an end of the run moves to the wall when the slit left there is narrower than the
    # smallest unit (KITCHEN_END_SHIFT_MAX_M): a sink unit against the wall, not a 20 cm panel beside it
    if fixed:
        f0, f1, kind = fixed[0]
        if 1e-6 < f0 + w / 2.0 <= KITCHEN_END_SHIFT_MAX_M:
            fixed[0] = (-w / 2.0, -w / 2.0 + (f1 - f0), kind)
        f0, f1, kind = fixed[-1]
        if 1e-6 < w / 2.0 - f1 <= KITCHEN_END_SHIFT_MAX_M:
            fixed[-1] = (w / 2.0 - (f1 - f0), w / 2.0, kind)
    segments: list[tuple[float, float]] = []
    x = -w / 2.0
    for f0, f1, _kind in fixed:
        if f0 - x > 1e-6:
            segments.append((x, f0))
        x = f1
    if w / 2.0 - x > 1e-6:
        segments.append((x, w / 2.0))
    base_h = worktop_z - KITCHEN_WORKTOP_M - KITCHEN_PLINTH_M
    modules = [_module("plinth", (w - (2 * KITCHEN_PLINTH_RECESS_M if island else 0.0),
                                  d - KITCHEN_PLINTH_RECESS_M * (2 if island else 1), KITCHEN_PLINTH_M),
                       (0.0, 0.0 if island else KITCHEN_PLINTH_RECESS_M / 2.0), "dark")]
    units: list[dict] = []
    for x0, x1 in segments:
        seg_w = x1 - x0
        run = compose_run(seg_w, KITCHEN_BASE_WIDTHS_M, KITCHEN_FILLER_MAX_M)
        if run is None:                                   # a slit narrower than the smallest unit: a filler panel
            units.append(_module("filler", (seg_w, d, base_h), ((x0 + x1) / 2.0, 0.0), "front", z_m=KITCHEN_PLINTH_M))
            continue
        # fillers at the run's outer ends only; inside the run the remainder sits next to the fixed unit
        at_left_end = abs(x0 + w / 2.0) < 1e-6
        at_right_end = abs(x1 - w / 2.0) < 1e-6
        rem = seg_w - run["sum_m"]
        left_f = rem / 2.0 if (at_left_end and at_right_end) else (rem if at_left_end else 0.0)
        right_f = rem - left_f
        if left_f > 1e-9:
            units.append(_module("filler", (left_f, d, base_h), (x0 + left_f / 2.0, 0.0), "front", z_m=KITCHEN_PLINTH_M))
        xx = x0 + left_f
        for uw in run["widths"]:
            front = "drawers" if abs(uw - KITCHEN_DRAWER_UNIT_W_M) < 1e-9 else ("doors" if uw >= 0.80 - 1e-9 else "door")
            units.append(_module("base_unit", (uw, d, base_h), (xx + uw / 2.0, 0.0), "front", z_m=KITCHEN_PLINTH_M,
                                 front=front, product=f"base unit {uw * 100:.0f}x{KITCHEN_BASE_DEPTH_M * 100:.0f} cm"))
            xx += uw
        if right_f > 1e-9:
            units.append(_module("filler", (right_f, d, base_h), (xx + right_f / 2.0, 0.0), "front", z_m=KITCHEN_PLINTH_M))
    for f0, f1, kind in fixed:
        units.append(_module("base_unit", (f1 - f0, d, base_h), ((f0 + f1) / 2.0, 0.0), "front", z_m=KITCHEN_PLINTH_M,
                             front="door" if f1 - f0 < 0.80 - 1e-9 else "doors", holds=kind,
                             product=f"{kind} base unit {(f1 - f0) * 100:.0f}x{KITCHEN_BASE_DEPTH_M * 100:.0f} cm"))
    units.sort(key=lambda m: m["pos_m"][0])
    modules += units
    modules.append(_module("worktop", (w, d, KITCHEN_WORKTOP_M), (0.0, 0.0), "worktop", z_m=worktop_z - KITCHEN_WORKTOP_M,
                           cutouts=[{"kind": k, "x_m": round((f0 + f1) / 2.0, 4), "w_m": round(f1 - f0, 4)}
                                    for f0, f1, k in fixed]))
    height = worktop_z
    if hints.get("wall_units") and not island:
        wall = compose_run(w, KITCHEN_WALL_WIDTHS_M, KITCHEN_FILLER_MAX_M)
        if wall is not None:
            xx = -w / 2.0 + wall["filler_m"]
            for uw in wall["widths"]:
                modules.append(_module("wall_unit", (uw, KITCHEN_WALL_DEPTH_M, KITCHEN_WALL_TOP_M - KITCHEN_WALL_BOTTOM_M),
                                       (xx + uw / 2.0, d / 2.0 - KITCHEN_WALL_DEPTH_M / 2.0), "front",
                                       z_m=KITCHEN_WALL_BOTTOM_M, product=f"wall unit {uw * 100:.0f}x"
                                                                          f"{KITCHEN_WALL_DEPTH_M * 100:.0f} cm"))
                xx += uw
            height = KITCHEN_WALL_TOP_M
    products = [m["product"] for m in modules if m.get("product")]
    notes = [f"{len([m for m in modules if m['kind'] == 'base_unit'])} base units, worktop {KITCHEN_WORKTOP_M} m at "
             f"{worktop_z:.2f} m"]
    if not fixed:
        notes.append("no sink or hob cutout: no place given (module_hints); the drawn sink and stove are their own pieces")
    if drawn_h is not None and abs(drawn_h - worktop_z) > 0.01:
        notes.append(f"the drawn height {drawn_h:.2f} m is not a counter height ({KITCHEN_WORKTOP_RANGE_M[0]:.2f}-"
                     f"{KITCHEN_WORKTOP_RANGE_M[1]:.2f} m): worktop at {worktop_z:.2f} m")
    return {"builder": "kitchen_run", "type": piece["type"], "modules": modules, "footprint_m": [w, d],
            "height_m": round(height, 4), "drawn_m": [w, d], "fit": _fit_record((w, d), (w, d)),
            "products": sorted(set(products), key=products.index), "island": island,
            "cutouts": [k for _f0, _f1, k in fixed], "notes": notes, "design": P.piece_design(piece)}


def plan_bath_set(piece: dict, style: Optional[dict] = None) -> Optional[dict]:
    """A vanity with basin(s) and a mirror (washbasin at least 0.45 m deep) or a shower tray with its screen."""
    w, d, h = _piece_size(piece)
    ftype = piece.get("type")
    if ftype == "shower":
        tray = nearest_tray(w, d)
        if tray is None:
            return None
        tw, td = tray
        fit = _fit_record((w, d), (tw, td))
        if not fit["within_cap"]:
            return None
        modules = [_module("tray", (tw, td, P.SHOWER_TRAY_M), (0.0, 0.0), "ceramic", product=f"shower tray {tw * 100:.0f}x{td * 100:.0f} cm"),
                   _module("screen", (tw, td, h - P.SHOWER_TRAY_M), (0.0, 0.0), "glass", z_m=P.SHOWER_TRAY_M)]
        return {"builder": "bath_set", "type": ftype, "modules": modules, "footprint_m": [tw, td], "height_m": round(h, 4),
                "drawn_m": [w, d], "fit": fit, "products": [modules[0]["product"], "glass screen with a door, shower set"],
                "notes": [f"tray {tw:.2f} x {td:.2f} m (size table product nearest the drawn {w:.2f} x {d:.2f} m)"],
                "design": P.piece_design(piece)}
    if ftype != "washbasin":
        return None
    if d < VANITY_DEPTH_RANGE_M[0] - 1e-9 or not (VANITY_WIDTH_RANGE_M[0] - 1e-9 <= w <= VANITY_WIDTH_RANGE_M[1] + 1e-9):
        return None
    cab_d = min(d, VANITY_DEPTH_RANGE_M[1])
    fit = _fit_record((w, d), (w, cab_d))
    if not fit["within_cap"]:
        return None
    basins = 2 if w >= VANITY_DOUBLE_FROM_M - 1e-9 else 1
    top_t = 0.03
    cab_h = h - top_t - VANITY_BOTTOM_M
    if cab_h < VANITY_CABINET_MIN_H_M - 1e-9:
        return None
    modules = [_module("vanity", (w, cab_d, cab_h), (0.0, 0.0), "front", z_m=VANITY_BOTTOM_M,
                       drawers=2 if cab_h >= 0.40 else 1, product=f"vanity unit {w * 100:.0f}x{cab_d * 100:.0f} cm"),
               _module("top", (w, cab_d, top_t), (0.0, 0.0), "ceramic", z_m=h - top_t, basins=basins)]
    for k in range(basins):
        bx = 0.0 if basins == 1 else (-1 if k == 0 else 1) * w / 4.0
        bw = min(BASIN_M[0], w / basins - 0.12)
        modules.append(_module("basin", (bw, min(BASIN_M[1], cab_d - 0.12), BASIN_M[2]), (bx, 0.0), "ceramic",
                               z_m=h - BASIN_M[2]))
    mirror_bottom = max(VANITY_MIRROR_BOTTOM_MIN_M, h + 0.25)
    modules.append(_module("mirror", (w - 0.10, VANITY_MIRROR_DEPTH_M, VANITY_MIRROR_H_M),
                           (0.0, cab_d / 2.0 - VANITY_MIRROR_DEPTH_M / 2.0), "mirror", z_m=mirror_bottom))
    products = [modules[0]["product"], f"{basins} inset basin(s) with taps", f"framed mirror {w - 0.10:.2f} x {VANITY_MIRROR_H_M:.2f} m"]
    notes = [f"wall-hung vanity, {basins} basin(s)" + (" (double vanity from 1.10 m, assumed)" if basins == 2 else "")]
    return {"builder": "bath_set", "type": ftype, "modules": modules, "footprint_m": [w, cab_d],
            "height_m": round(mirror_bottom + VANITY_MIRROR_H_M, 4), "drawn_m": [w, d], "fit": fit, "products": products,
            "basins": basins, "notes": notes, "design": P.piece_design(piece)}


def nearest_tray(w: float, d: float) -> Optional[tuple[float, float]]:
    """The shower tray product nearest the drawn size (either orientation of the drawn box is tried, the tray's
    width stays along the piece's front)."""
    best = None
    for tw, td in SHOWER_TRAYS_M:
        for a, b in ((tw, td), (td, tw)):
            err = max(abs(a - w) / w, abs(b - d) / d)
            if best is None or err < best[0]:
                best = (err, (a, b))
    return None if best is None else best[1]


_PLANNERS = {"wardrobe_run": plan_wardrobe_run, "table_long": plan_table_long, "sofa_l": plan_sofa_l,
             "kitchen_run": plan_kitchen_run, "bath_set": plan_bath_set}


def gap_types() -> list[str]:
    """The furniture types built below the library level by neither a module builder nor a v2 family (the
    report's gap list, docs/milestone13.md §13.1 T2): every parametric type minus ``MODULE_BUILDERS`` and
    ``parametric.FAMILY_TYPES``. They keep their Milestone 4-12 builders (the by-design fixtures of
    ``catalog.BY_DESIGN_PARAMETRIC_TYPES`` among them)."""
    return sorted(t for t in P.PARAMETRIC_TYPES if t not in MODULE_BUILDERS and t not in P.FAMILY_TYPES)


def module_plan(piece: dict, style: Optional[dict] = None) -> Optional[dict]:
    """The module plan of a drawn piece (docs/milestone13.md §13.2; pure): ``{builder, modules: [{kind, size_m:
    [w, d, h], pos_m: [x, y], rot_deg, material}], footprint_m, height_m, products}`` plus ``drawn_m``, ``fit``
    (the deviation from the drawn footprint, ``within_cap`` at ``MODULE_FIT_TOL``), ``notes`` and the builder's own
    records (``split`` of a table with chairs, ``cutouts`` of a kitchen run, ``chaise_side`` of an L sofa). None
    when the type has no builder (``MODULE_BUILDERS``), the piece has no usable footprint, or the modules cannot
    match the drawn footprint within the cap (then the parametric family builds it)."""
    fp = piece.get("footprint") if isinstance(piece, dict) else None
    builder = MODULE_BUILDERS.get(str((piece or {}).get("type")))
    if builder is None and isinstance(piece, dict) and piece.get("type") == "sofa" \
            and str(piece.get("shape") or "").upper() == "L":
        builder = "sofa_l"                        # a sofa drawn as an L (shape: L) is built like a corner sofa
    if builder is None or not isinstance(fp, dict) or len(fp.get("size") or []) < 2:
        return None
    try:
        w, d = float(fp["size"][0]), float(fp["size"][1])
    except (TypeError, ValueError):
        return None
    if not (w > 0 and d > 0):
        return None
    plan = _PLANNERS[builder](piece, style)
    if plan is None or not plan.get("fit", {}).get("within_cap", True):
        return None
    plan["method"] = MODULE_METHOD
    return plan


# --------------------------------------------------------------------------
# Parts (pure) from a plan
# --------------------------------------------------------------------------

def _rotate_parts(parts: list[Part], dx: float, dy: float, rot_deg: float) -> list[Part]:
    """Parts turned about Z by ``rot_deg`` and moved by ``(dx, dy)`` in the piece frame."""
    rad = math.radians(rot_deg)
    c, s = math.cos(rad), math.sin(rad)
    out = []
    for p in parts:
        verts = [(dx + c * x - s * y, dy + s * x + c * y, z) for x, y, z in p["verts"]]
        out.append(dict(p, verts=verts))
    return out


def _frame_parts(m: dict, design: dict, frame_top: float) -> list[Part]:
    """One wardrobe frame: a carcass box with its door(s) in the design's front style and vertical handles."""
    w, d, _h = m["size_m"]
    x, _y = m["pos_m"]
    z0 = float(m.get("z_m") or 0.0)
    inset = P.FRONT_GAP + P.FRONT_THICKNESS
    parts = [P._box(x, inset / 2.0, z0, w - 0.002, d - inset, frame_top - z0, "wood", "body")]
    face = -d / 2.0 + inset
    doors = int(m.get("doors") or 1)
    style = P.front_style_of(design)
    gap = 0.003
    dw = (w - gap * (doors + 1)) / doors
    for k in range(doors):
        cx = x - w / 2.0 + gap + dw / 2.0 + k * (dw + gap)
        parts += P._front_panel(cx, face, z0 + gap, dw, frame_top - z0 - 2 * gap, style)
        # the handle near the opening edge: a pair of doors opens in the middle, a single door on its hinge's far side
        if doors == 2:
            hx = cx + (dw / 2.0 - 0.05) * (1.0 if k == 0 else -1.0)
        else:
            hx = cx + (dw / 2.0 - 0.05) * (1.0 if m.get("hinge") == "left" else -1.0)
        parts.append(P._handle(hx, face, z0 + (frame_top - z0) * 0.5, vertical=True))
    return parts


def _wardrobe_parts(plan: dict) -> list[Part]:
    design = plan.get("design") or {}
    parts: list[Part] = []
    top_z = plan["height_m"] - WARDROBE_TOP_M
    for m in plan["modules"]:
        w, d, h = m["size_m"]
        x, y = m["pos_m"]
        z0 = float(m.get("z_m") or 0.0)
        if m["kind"] == "plinth":
            parts.append(P._box(x, y, 0.0, w, d, h, "dark", "plinth"))
        elif m["kind"] == "frame":
            parts += _frame_parts(m, design, top_z)
        elif m["kind"] == "filler":
            parts.append(P._box(x, 0.0, z0, w, d, top_z - z0, "front", "front"))
        elif m["kind"] == "top":
            parts.append(P._box(x, y, z0, w, d, h, "wood", "top"))
    return parts


def _table_parts(plan: dict) -> list[Part]:
    design = plan.get("design") or {}
    tags = design.get("material_tags") or ()
    top_key = next((P.TOP_TAG_KEYS[t] for t in tags if t in P.TOP_TAG_KEYS), "wood")
    leg_key = "steel" if "metal" in tags else "wood"
    parts: list[Part] = []
    for m in plan["modules"]:
        w, d, h = m["size_m"]
        x, y = m["pos_m"]
        z0 = float(m.get("z_m") or 0.0)
        if m["kind"] == "top":
            parts.append(P._box(x, y, z0, w, d, h, top_key, "top"))
            # an apron under the top for legged tables (slab-legged trestle tables take a stretcher instead);
            # FRONT_GAP (1 mm) under the top: no two parts share a face plane
            if m.get("support") == "legs":
                a = 0.08 - P.FRONT_GAP
                for sy in (-1, 1):
                    parts.append(P._box(x, y + sy * (d / 2.0 - 0.09), z0 - 0.08, w - 0.24, 0.03, a, leg_key, "apron"))
                for sx in (-1, 1):
                    parts.append(P._box(x + sx * (w / 2.0 - 0.09), y, z0 - 0.08, 0.03, d - 0.24, a, leg_key, "apron"))
            else:
                parts.append(P._box(x, y, z0 - 0.16, w - 1.0, 0.06, 0.10, leg_key, "stretcher"))
        elif m["kind"] == "leg":
            foot = 0.015
            parts.append(P._box(x, y, 0.0, w, d, foot, "steel", "foot"))
            parts.append(P._frustum_z(x, y, foot + P.FRONT_GAP, w * 0.35, d * 0.35, w / 2.0, d / 2.0,
                                      h - foot - 2 * P.FRONT_GAP, leg_key, "leg", n=16))
        elif m["kind"] == "trestle":
            foot = P.TABLE_FOOT_M
            parts.append(P._box(x, y, 0.0, w + 0.02, d, foot, "steel", "foot"))          # adjustable steel feet
            parts.append(P._box(x, y, foot + P.FRONT_GAP, w, d, h - foot - 2 * P.FRONT_GAP, leg_key, "trestle"))
        elif m["kind"] == "chair":
            chair = P.build_parts("chair", w, d, h)
            parts += _rotate_parts(chair, x, y, m["rot_deg"])
    return parts


def _cushion(cx: float, cy: float, z0: float, w: float, d: float, t: float, role: str = "cushion",
             tilt: float = 0.0) -> Part:
    return P._superellipsoid(cx, cy, z0, w, d, t, 0.25, 0.22, "fabric", role, n_eta=10, n_om=32, tilt_deg=tilt)


def _sofa_l_parts(plan: dict) -> list[Part]:
    h = plan["height_m"]
    seat_h = P.sofa_seat_height(h)
    parts: list[Part] = []
    leg = SOFA_LEG_M
    for m in plan["modules"]:
        w, d, mh = m["size_m"]
        x, y = m["pos_m"]
        if m["kind"] == "back":
            parts.append(P._box(x, y, leg, w, d, h - leg - 0.10, "fabric", "back"))
        elif m["kind"] == "arm":
            parts.append(P._box(x, y, leg, w, d, mh - leg, "fabric", "arm"))
        elif m["kind"] in ("seat_module", "chaise_module"):
            parts.append(P._box(x, y, leg, w, d, seat_h - SOFA_CUSHION_M - leg, "fabric", "body"))
            for sx in (-1, 1):
                for sy in (-1, 1):
                    parts.append(P._frustum_z(x + sx * (w / 2.0 - 0.06), y + sy * (d / 2.0 - 0.06), 0.0, 0.02, 0.02,
                                              0.03, 0.03, leg - P.FRONT_GAP, "wood", "leg", n=12))
            parts.append(_cushion(x, y, seat_h - SOFA_CUSHION_M, w - 0.02, d - 0.03, SOFA_CUSHION_M))
            # the leaning back cushion's box turns with it: its height is chosen so the top meets h exactly
            lean = math.radians(P.BACK_CUSHION_LEAN_DEG)
            bt = P.BACK_CUSHION_T_M
            bh = max(0.10, (h - seat_h + 0.02 - bt * math.sin(lean)) / math.cos(lean))
            parts.append(_cushion(x, y + d / 2.0 - bt / 2.0 + 0.01, seat_h - 0.02, w - 0.04, bt, bh, "back_cushion",
                                  tilt=-P.BACK_CUSHION_LEAN_DEG))
    return parts


def _base_unit_parts(m: dict, design: dict, d_run: float) -> list[Part]:
    """One kitchen base unit: carcass, fronts (door, pair of doors or three drawers) with handles."""
    w, d, h = m["size_m"]
    x, _y = m["pos_m"]
    z0 = float(m.get("z_m") or 0.0)
    inset = P.FRONT_GAP + P.FRONT_THICKNESS + 0.015          # the worktop overhangs the fronts by 15 mm
    face = -d_run / 2.0 + inset
    parts = [P._box(x, inset / 2.0, z0, w - 0.002, d_run - inset, h, "painted", "body")]
    kind = m.get("front") or "door"
    if kind == "drawers":
        fronts = P.cabinet_fronts(w - 0.004, face, z0 + 0.003, z0 + h - 0.003, 3, 1, design, doors=False)
    else:
        fronts = P.cabinet_fronts(w - 0.004, face, z0 + 0.003, z0 + h - 0.003, 1, 2 if kind == "doors" else 1, design)
    parts += _rotate_parts(fronts, x, 0.0, 0.0)
    return parts


def _kitchen_parts(plan: dict) -> list[Part]:
    design = plan.get("design") or {}
    parts: list[Part] = []
    w_run, d_run = plan["footprint_m"]
    island = bool(plan.get("island"))
    for m in plan["modules"]:
        w, d, h = m["size_m"]
        x, y = m["pos_m"]
        z0 = float(m.get("z_m") or 0.0)
        if m["kind"] == "plinth":
            parts.append(P._box(x, y, 0.0, w, d, h, "dark", "plinth"))
        elif m["kind"] == "base_unit":
            parts += _base_unit_parts(m, design, d_run)
        elif m["kind"] == "filler":
            parts.append(P._box(x, 0.0, z0, w, d - 0.015, h, "front", "front"))
        elif m["kind"] == "worktop":
            parts += _worktop_parts(m, w_run, d_run)
        elif m["kind"] == "wall_unit":
            inset = P.FRONT_GAP + P.FRONT_THICKNESS
            parts.append(P._box(x, y + inset / 2.0, z0, w - 0.002, d - inset, h, "painted", "body"))
            face = y - d / 2.0 + inset
            fronts = P.cabinet_fronts(w - 0.004, face, z0 + 0.003, z0 + h - 0.003, 1, 1 if w < 0.60 - 1e-9 else 2,
                                      design, handle_at="bottom")
            parts += _rotate_parts(fronts, x, 0.0, 0.0)
    if island:                                                # the back of an island shows a panel, not a carcass
        base_h = KITCHEN_WORKTOP_HEIGHT_M - KITCHEN_WORKTOP_M - KITCHEN_PLINTH_M
        parts.append(P._box(0.0, d_run / 2.0 - 0.009, KITCHEN_PLINTH_M, w_run, 0.018, base_h, "front", "panel"))
    return parts


def _worktop_parts(m: dict, w_run: float, d_run: float) -> list[Part]:
    """The worktop slab with the sink bowl (steel basin and tap) and the hob plate at its cutouts."""
    w, d, t = m["size_m"]
    z0 = float(m.get("z_m") or 0.0)
    cutouts = m.get("cutouts") or []
    parts: list[Part] = []
    sink = next((c for c in cutouts if c["kind"] == "sink"), None)
    if sink is None:
        parts.append(P._box(0.0, 0.0, z0, w, d, t, "worktop", "top"))
    else:
        bw, bd = min(0.70, sink["w_m"] - 0.10), min(0.42, d - 0.16)
        sx = float(sink["x_m"])
        left, right = sx - bw / 2.0, sx + bw / 2.0
        strip = (d - bd) / 2.0
        parts += [P._box((-w / 2.0 + left) / 2.0, 0.0, z0, left + w / 2.0, d, t, "worktop", "top"),
                  P._box((right + w / 2.0) / 2.0, 0.0, z0, w / 2.0 - right, d, t, "worktop", "top"),
                  P._box(sx, -d / 2.0 + strip / 2.0, z0, bw, strip, t, "worktop", "top"),
                  P._box(sx, d / 2.0 - strip / 2.0, z0, bw, strip, t, "worktop", "top")]
        parts += P._basin(sx, 0.0, z0 + t - 0.18, bw, bd, 0.18, 0.008, "steel")
        parts.append(P._cylinder_z(sx, bd / 2.0 + 0.05, z0 + t, 0.015, 0.015, 0.28, "steel", "tap", n=12))
        parts.append(P._cylinder_y(sx, bd / 2.0 + 0.05 - 0.18, z0 + t + 0.27, 0.01, 0.01, 0.18, "steel", "tap", n=10))
    hob = next((c for c in cutouts if c["kind"] == "hob"), None)
    if hob is not None:
        hw, hd = KITCHEN_HOB_PLATE_M
        hw = min(hw, hob["w_m"] - 0.02)
        parts.append(P._box(float(hob["x_m"]), 0.0, z0 + t, hw, min(hd, d - 0.08), 0.005, "dark", "hob"))
        r = min(hw, hd) * 0.17
        for sx_ in (-1, 1):
            for sy_ in (-1, 1):
                parts.append(P._cylinder_z(float(hob["x_m"]) + sx_ * hw / 4.0, sy_ * hd / 4.0, z0 + t + 0.005, r, r,
                                           0.0015, "steel", "ring", n=20))
    return parts


def _bath_parts(plan: dict) -> list[Part]:
    design = plan.get("design") or {}
    parts: list[Part] = []
    w, d = plan["footprint_m"]
    if plan["type"] == "shower":
        return P._shower(w, d, plan["height_m"])
    for m in plan["modules"]:
        mw, md, mh = m["size_m"]
        x, y = m["pos_m"]
        z0 = float(m.get("z_m") or 0.0)
        if m["kind"] == "vanity":
            body, face = P._carcass(mw, md, z0, mh)
            parts += [body, P._box(0.0, md / 2.0 - 0.01, 0.0, mw * 0.3, 0.02, z0, "dark", "back")]
            parts += P.cabinet_fronts(mw - 0.004, face, z0 + 0.003, z0 + mh - 0.003, int(m.get("drawers") or 1), 1,
                                      design, doors=False)
        elif m["kind"] == "top":
            basins = [b for b in plan["modules"] if b["kind"] == "basin"]
            if not basins:
                parts.append(P._box(x, y, z0, mw, md, mh, "ceramic", "top"))
                continue
            # the top as strips around every bowl: front and back strips over the full width, side strips between
            bd = basins[0]["size_m"][1]
            strip = (md - bd) / 2.0
            parts += [P._box(0.0, -md / 2.0 + strip / 2.0, z0, mw, strip, mh, "ceramic", "top"),
                      P._box(0.0, md / 2.0 - strip / 2.0, z0, mw, strip, mh, "ceramic", "top")]
            edges = [-mw / 2.0] + sorted(v for b in basins for v in (b["pos_m"][0] - b["size_m"][0] / 2.0,
                                                                     b["pos_m"][0] + b["size_m"][0] / 2.0)) + [mw / 2.0]
            for k in range(0, len(edges) - 1, 2):
                x0, x1 = edges[k], edges[k + 1]
                if x1 - x0 > 1e-6:
                    parts.append(P._box((x0 + x1) / 2.0, 0.0, z0, x1 - x0, bd, mh, "ceramic", "top"))
        elif m["kind"] == "basin":
            parts += P._basin(x, y, z0, mw, md, mh, 0.012, "ceramic")
            parts.append(P._cylinder_z(x, md / 2.0 + 0.04, plan["modules"][1]["z_m"] + plan["modules"][1]["size_m"][2],
                                       0.012, 0.012, 0.15, "steel", "tap", n=12))
        elif m["kind"] == "mirror":
            f = 0.025
            parts.append(P._box(x, y + 0.002, z0, mw, md - 0.004, mh, "wood", "frame"))
            parts.append(P._box(x, y - md / 2.0 + 0.002, z0 + f, mw - 2 * f, 0.004, mh - 2 * f, "mirror", "glass"))
    return parts


_PART_BUILDERS = {"wardrobe_run": _wardrobe_parts, "table_long": _table_parts, "sofa_l": _sofa_l_parts,
                  "kitchen_run": _kitchen_parts, "bath_set": _bath_parts}


def module_parts(plan: dict) -> list[Part]:
    """The parts of a module plan in the piece frame (pure): ``parametric`` part dicts with their material keys
    (``MATERIAL_KEYS``) and roles; ``KeyError`` for an unknown builder."""
    try:
        builder = _PART_BUILDERS[plan["builder"]]
    except KeyError:
        raise KeyError(f"no module builder {plan.get('builder')!r}") from None
    return builder(plan)


def plan_bbox(plan: dict) -> tuple[float, float, float]:
    """``(width, depth, height)`` of the plan's parts (the real box the planners read)."""
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(module_parts(plan))
    return (x1 - x0, y1 - y0, z1 - z0)


def material_keys(plan: dict) -> list[str]:
    """The distinct material keys of a plan's parts, in order of first use (the object's material slots)."""
    keys = [p["key"] for p in module_parts(plan)]
    return sorted(set(keys), key=keys.index)


def module_record(plan: dict) -> dict:
    """The compact record of a plan for the scene manifest (no parts)."""
    return {"builder": plan["builder"], "modules": len(plan["modules"]), "kinds": sorted({m["kind"] for m in plan["modules"]}),
            "products": list(plan.get("products") or []), "footprint_m": list(plan["footprint_m"]),
            "height_m": plan["height_m"], "drawn_m": list(plan.get("drawn_m") or plan["footprint_m"]),
            "fit": dict(plan.get("fit") or {}), "notes": list(plan.get("notes") or []),
            **({"split": plan["split"]} if plan.get("split") else {}),
            **({"cutouts": plan["cutouts"]} if plan.get("cutouts") else {})}


# --------------------------------------------------------------------------
# Blender
# --------------------------------------------------------------------------

class ModuleMaterials:
    """What ``build_module`` needs besides the plan and the piece: ``get(key)`` -> a Blender material for a part
    key (``furniture._Materials.get`` with the piece's design overrides), and where the object goes: ``collection``,
    ``floor_z`` (the room's floor), ``name``, ``status``. ``furniture.create_furniture`` fills it; a plain mapping
    ``{key: material}`` works too (scene collection, floor 0, name ``furn_<id>``)."""

    def __init__(self, get, collection=None, floor_z: float = 0.0, name: Optional[str] = None,
                 status: str = "verified", slugs=None):
        self._get = get
        self.collection = collection
        self.floor_z = float(floor_z)
        self.name = name
        self.status = status
        self._slugs = slugs

    def get(self, key: str):
        return self._get(key)

    def slug(self, key: str) -> Optional[str]:
        return self._slugs(key) if self._slugs else None


def build_module(plan: dict, piece: dict, materials):
    """Build the object of a module plan (``bpy``): the parts of ``module_parts`` placed on the drawn footprint
    (``piece["footprint"]``: centre, rotation) on ``materials.floor_z``, one material slot per part key from
    ``materials.get(key)`` (a ``ModuleMaterials`` or a mapping), the Bevel modifier of ``furniture.add_bevel``,
    smooth cushions, and the custom properties ``wenart_method = "module"``, ``wenart_module`` (the builder) and
    ``wenart_type``. Returns the object; its ``["wenart_module_record"]`` holds ``module_record(plan)`` as JSON."""
    import json

    import bpy

    from wenart.blender import furniture as F

    parts = module_parts(plan)
    fp = piece["footprint"]
    if isinstance(materials, dict):
        get = materials.__getitem__
        collection, floor_z, name, status = None, 0.0, None, piece.get("status") or "verified"
    else:
        get = materials.get
        collection = getattr(materials, "collection", None)
        floor_z = float(getattr(materials, "floor_z", 0.0) or 0.0)
        name = getattr(materials, "name", None)
        status = getattr(materials, "status", None) or piece.get("status") or "verified"
    collection = collection or bpy.context.scene.collection
    name = name or f"furn_{piece['id']}"
    verts, faces, keys = P.world_mesh(parts, fp["center"], float(fp.get("rotation_deg") or 0.0), floor_z)
    used = sorted(set(keys), key=keys.index)
    slots = [get(k) for k in used]
    ob = F._mesh_object(name, verts, faces, slots, [used.index(k) for k in keys], collection, piece["id"],
                        "furniture", status)
    bevel = F.add_bevel(ob, parts)
    ob["wenart_method"] = MODULE_METHOD
    ob["wenart_module"] = plan["builder"]
    ob["wenart_type"] = piece.get("type") or plan.get("type") or ""
    ob["wenart_module_record"] = json.dumps(module_record(plan))
    ob["wenart_bevel"] = json.dumps(bevel or {})
    return ob
