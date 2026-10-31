"""Scene checks S1–S6 on the built Blender scene (docs/milestone12.md §4.6, §4.7, contract §13.2; owner: track S).

Contract (frozen 10 Oct 2026):

- ``CHECKS``: ``("S1", ..., "S6")``; ``TOLERANCES``: the numbers of §4.6/§4.7 (metres, degrees).
- ``run_scene_checks(building: dict, scene_objects: dict, out_path) -> dict``: runs inside Blender after the
  furniture and decor are built (``build.py`` calls it once per level); ``scene_objects``: ``{piece or decor id:
  bpy object}``; writes ``checks/scene.json`` (``out_path``) and returns ``{"violations": [Violation],
  "counts": {...}, "measured": {id: {...}}}``. A decor item that fails S5 after one re-placement is not built
  (``decor_not_rested``); a built item that fails S5 fails the build.
- ``measure_pure(meshes: dict, building: dict) -> dict``: the same measurements on plain triangle meshes (pure
  Python ray caster) for the CPU tests.

What (the checks, §4.6):

| Check | Rule | Tolerance |
|---|---|---|
| S1 | a floor piece's lowest vertex - its room's floor (``shell.room_floor_z``: level elevation + ``floor_offset_m``) | -0.005 .. +0.010 m |
| S2 | no piece cuts a wall (the building's wall boxes) or another piece (sample points of one inside the other, ray parity; depth = shortest axis ray) | <= 0.010 m |
| S3 | the built front (``front_deg`` the builder records on the object, else the footprint's) vs the planned ``front_deg`` | <= 10 degrees |
| S4 | the built box in the piece frame vs ``wenart.furniture.sizes.real_range`` of its type | +-15 % per axis (height when the table has one) |
| S5 | decor rests on its host (``rest.measure_rest``: gap, penetration hard / soft host, support share) or on the floor; a leaning item on its back (``rest.measure_back``), a cloth with nothing poking through or torn (``rest.measure_cloth``), a hung light up to the ceiling (``hang_gap``) | §4.7; 28 Oct 2026 |
| S6 | every built piece is a usable library model (``catalog.usable`` of its asset) or a by-design parametric type (``catalog.by_design_parametric``); never ``unknown`` | none |

Exceptions (documented, §4.6): wall-hung pieces (``wall_cabinet``, any ``mount_bottom_m``) skip S1 and the wall part
of S2; the members of a kitchen run (counter, island, sink, hob, fridge, wall cabinet, washing machine) may overlap
each other (the drawn sink and hob are inside the drawn counter run).

Fix round after P3 (16-17 Oct 2026): a floor-standing member (``KITCHEN_RUN_MEMBERS``: sink, stove, fridge, washing
machine) is no longer silently allowed INSIDE a counter or island. What: for such a pair, the share of the member's
drawn box (footprint x built height, a grid of points inside it) that lies inside the run's mesh (``buried_share``);
at ``TOLERANCES["kitchen_buried_share"]`` (0.25) or more the member is buried in the run: an S2 violation on the
member. Why: pod P3 built every drawn sink and stove of real04 inside full-depth base units under an uncut worktop,
and S2 said nothing. How: a drawn sink inside a run is now built into it (no object of its own:
``furniture.built_in_ids``) and a drawn stove stands in a gap of the run (``modules.plan_kitchen_run``), so neither
is measured as buried; a member that only meets the run (a fridge at the run's end, a stove beside its gap) keeps
the old allowance. Two runs, two members or a wall cabinet stay exempt. Part 2 (17 Oct 2026): the violation carries
``depth_m`` (``buried_depth``: ``inside_share`` x the member's smaller drawn side, the depth of its buried part), so
the M13 metric "S2 > 3 cm" (``metrics13``, ``depth_m`` > 0.03) and the agent's cause (``causes``) count it as the
deep cut it is; without it a buried sink counted only under "S2 all". The mesh penetration of the other pairs is no
measure here: a member wholly inside a run has its vertices on the run's module faces (a buried sink measured
3.6 cm).

Fix round after P6a, part I2 (22-23 Oct 2026; D_decor's ask, the look finding "two drawn floor lamps overlap" in
real04's r_L-1_salon, f_L-1_063 / f_L-1_064 and the mirrored f_L-1_065 / f_L-1_066): two floor lamps
(``LAMP_SHADE_TYPES``) whose shades overlap are an S2 violation. What: the shade is the part of the lamp in the top
``LAMP_SHADE_SHARE`` of its height (``shade_disc``: the circle inside the XY box of those vertices); two shades at
heights that meet overlap by ``r_a + r_b - distance`` (``shade_overlap``), judged with the pair's tolerance. Why: P6a's
S2 reported none of these pairs (the agent log shows only the plausibility F9 of a tried move) while the renders
showed two shades through each other; a shade is an open drum or cone (the parametric lamp's fabric drum, most
library shades) whose vertices the ray-parity test of the pair need not find inside the other. Every other pair keeps
the mesh test, and a lamp pair whose shades do not overlap still gets it.

Fix round after P6b (23 Oct 2026; the agent track's ask, verify:agent:0): a piece that passes right through a wall is
an S2 violation. What: when no sampled vertex lies deeper in a wall box than the piece's tolerance, the wall boxes
its bounding box meets are tested edge by edge (``through_wall``): an edge with one end at or beyond each long face
whose crossing of the wall's middle plane lies inside the wall's length and height means the piece runs through the
whole wall; the violation's depth is the wall's thickness, ``metrics.through`` is true and the message says "passes
through wall". Why: ``depth_in_wall`` measures vertices (the deepest is half the thickness from a face), and a box
whose corners stand on both sides of a wall has none inside it: P6b's wardrobe f_L0_098, moved 0.28 m through the
front outer wall, had no S2 at all (only the plan's F9). A cut from one side keeps the vertex measure.

Milestone 13 (docs/milestone13.md §1.4, §3.0 K3, §13.2; track T3): S2 tolerances by class. 16 of real04's 17 S2
findings were 1.2-2.5 cm cuts of drawn toilets, armchair / ottoman pairs and wardrobes (noise the agent chased with
39 edits). ``TOLERANCES["overlap_fixture"]`` (0.03 m) applies to fixed equipment and kitchen appliances
(``S2_CLASSES["fixture"]``), ``TOLERANCES["overlap_soft"]`` (0.05 m) to soft seating (``S2_CLASSES["soft"]``: sofas,
armchairs, chaises, ottomans, poufs: their cushions give); the 0.010 m default stays for everything else. A pair of
pieces takes the larger of their two tolerances (``overlap_tolerance``); a piece against a wall takes its own class.

28 Oct 2026 (user on real04 run 20261028-005318-full: "still flying pillows all around", "More flying pillows", "I did
not like this bed", "Light is flying in the air needs to be connected to ceiling"): S5 also fails decor that is not
attached to what holds it. What: a cushion on a back or a headboard whose upper part has a gap behind it over
``decor_back_gap_m`` (or nothing behind; ``rest.measure_back``, the host's footprint back edge counting as the wall);
a throw the host pokes through (``decor_cloth_poke_m``) or whose drape tore (``decor_cloth_edge_m``;
``rest.measure_cloth``); a pendant or ceiling light whose top (cord and canopy included) is more than
``decor_hang_gap_m`` under the ceiling over it (``hang_gap``; before, hung decor was not measured). Why: both sofas'
cushions stood at the seat's front edge some 0.3 m in front of the backrest and passed (one touching point under them);
a cream throw over a bed model's own bedding showed its grey blanket through it and was 1.35 m deep for a 0.5 m cloth;
the salon's dining pendant hung 0.99 m under the ceiling with no cord.

How: a mesh is ``{"verts", "faces"}`` in world coordinates plus optional fields the builder records on the
object: ``front_deg`` (built front), ``method`` (``library`` / ``parametric``), ``rest_footprint`` (the decor
item's resting footprint ``{center, size, rotation_deg}``), ``support``. ``run_scene_checks`` reads the evaluated
objects (modifiers applied) into that form and measures with Blender's BVH caster; ``measure_pure`` uses the numpy
caster of ``wenart.blender.rest``: the same code path, so the CPU tests cover the pod's checks. Output:
``{"violations": [Violation], "counts": {S1..S6: {"checked", "failed"}, "failed_build": bool}, "measured":
{id: {...}}}``; ``Violation = {check, severity, target, room_id, message, metrics}`` (the M11 format).
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Callable, Optional

import numpy as np

from wenart.blender.rest import REST_TOLERANCES

CHECKS: tuple[str, ...] = ("S1", "S2", "S3", "S4", "S5", "S6")
TOLERANCES: dict[str, float] = {"floor_gap_m": 0.010, "floor_sink_m": 0.005, "overlap_m": 0.010, "front_deg": 10.0,
                                "size_rel": 0.15, **REST_TOLERANCES,
                                # Milestone 13 (§13.2): S2 by class (the module docstring).
                                "overlap_fixture": 0.03, "overlap_soft": 0.05,
                                # fix round after P3: a kitchen-run member with this share of its box inside a
                                # run is buried in it (a quarter of a 0.6 m appliance is 15 cm deep: no drawing slip)
                                "kitchen_buried_share": 0.25}
S2_CLASSES: dict[str, tuple[str, ...]] = {
    "fixture": ("toilet", "washbasin", "shower", "bathtub", "washing_machine", "sink_kitchen", "stove", "fridge",
                "kitchen_counter", "kitchen_island", "tall_cabinet"),
    "soft": ("sofa", "sofa_corner", "armchair", "chaise", "ottoman", "pouf"),
}


def s2_class(ftype: Optional[str]) -> str:
    """``fixture`` | ``soft`` | ``default``: the S2 class of a piece type."""
    for name, types in S2_CLASSES.items():
        if ftype in types:
            return name
    return "default"


def overlap_tolerance(*types: Optional[str]) -> float:
    """The S2 tolerance of one piece (against a wall) or of a pair: the larger of their class tolerances
    (``overlap_fixture`` 0.03, ``overlap_soft`` 0.05, else ``overlap_m`` 0.010)."""
    key = {"fixture": "overlap_fixture", "soft": "overlap_soft", "default": "overlap_m"}
    return max(float(TOLERANCES[key[s2_class(t)]]) for t in (types or (None,)))
SEVERITY: dict[str, str] = {"S1": "major", "S2": "major", "S3": "major", "S4": "minor", "S5": "critical",
                            "S6": "major"}
WALL_HUNG_TYPES: tuple[str, ...] = ("wall_cabinet",)
# Hosts that give under a cushion or a pillow (the soft tolerance of S5 applies on their seat, back or mattress).
SOFT_HOST_TYPES: tuple[str, ...] = ("sofa", "sofa_corner", "armchair", "chaise", "ottoman", "bed_single",
                                    "bed_double", "bunk_bed", "crib")
SOFT_SUPPORTS: tuple[str, ...] = ("seat", "mattress", "back", "headboard")
FLOOR_DECOR: tuple[str, ...] = ("rug", "plant", "plant_large", "basket", "sculpture",
                                 "toilet_brush",             # 29 Oct 2026 (UL114 B2): on the floor beside the WC
                                 # 29 Oct 2026 (UL113, UL115): the details standing on the floor (room_details)
                                 "wall_niche", "floor_vase", "art_leaning", "bag",
                                 "panel_wall")               # 30 Oct 2026 (P16, UL153): the panel wall stands
UNMEASURED_DECOR: tuple[str, ...] = ("wall_art", "mirror", "clock", "curtain", "blind",
                                     # 29 Oct 2026 (UL114, UL123, UL124): the bathroom's wall details
                                     "toilet_paper_holder", "towel_rail", "towel_shelf", "towel_bar", "feature_panel",
                                     "cove_light", "install_wall",      # 30 Oct 2026 (UL205)
                                     "intercom", "desk_wall_unit",      # 29 Oct 2026 (UL113, UL115): on a wall
                                     "wall_discs")                      # 30 Oct 2026 (P16, UL153): on a wall
# 29 Oct 2026 (lesson UL119, R33): a floating nightstand hangs on the wall (its box under its top, nothing to the floor);
# 30 Oct 2026 (P16, UL153, R45): so does the floating TV console
HUNG_FORMS: dict[str, tuple[str, ...]] = {"nightstand": ("floating",), "tv_unit": ("floating",)}
# 28 Oct 2026 (module docstring): hung decor is measured against the ceiling over it
HUNG_DECOR: tuple[str, ...] = ("pendant_light", "ceiling_light")
LEANING_SUPPORTS: tuple[str, ...] = ("back", "headboard")
KITCHEN_RUN_TYPES: tuple[str, ...] = ("kitchen_counter", "kitchen_island", "sink_kitchen", "stove", "fridge",
                                      "wall_cabinet", "washing_machine")
# Fix round after P3 (module docstring): the runs, and the floor-standing members that must not stand inside one.
KITCHEN_RUN_HOSTS: tuple[str, ...] = ("kitchen_counter", "kitchen_island")
KITCHEN_RUN_MEMBERS: tuple[str, ...] = ("sink_kitchen", "stove", "fridge", "washing_machine")
MAX_PAIR_SAMPLES = 200
# Fix round after P6a, part I2 (module docstring): floor lamps whose shades overlap.
LAMP_SHADE_TYPES: tuple[str, ...] = ("floor_lamp",)
LAMP_SHADE_SHARE = 0.35            # the shade: the vertices in the top 35 % of the lamp's height


def shade_disc(verts) -> Optional[tuple[float, float, float, float, float]]:
    """``(cx, cy, r, z0, z1)`` of a floor lamp's shade (pure; fix round after P6a): the vertices in the top
    ``LAMP_SHADE_SHARE`` of the lamp's height; the centre of their XY box and the radius of the circle inside it (the
    smaller half side, so a round shade is never made bigger than it is); None without vertices."""
    pts = [(float(v[0]), float(v[1]), float(v[2])) for v in verts or ()]
    if not pts:
        return None
    zmin, zmax = min(p[2] for p in pts), max(p[2] for p in pts)
    z0 = zmax - LAMP_SHADE_SHARE * (zmax - zmin)
    top = [p for p in pts if p[2] >= z0 - 1e-9]
    xs, ys = [p[0] for p in top], [p[1] for p in top]
    r = min(max(xs) - min(xs), max(ys) - min(ys)) / 2.0
    return ((max(xs) + min(xs)) / 2.0, (max(ys) + min(ys)) / 2.0, r, z0, zmax)


def shade_overlap(verts_a, verts_b) -> float:
    """How far the shades of two floor lamps overlap (metres; pure; fix round after P6a): ``r_a + r_b - distance``
    of their ``shade_disc`` circles when the shades' heights meet, else 0 (never negative)."""
    a, b = shade_disc(verts_a), shade_disc(verts_b)
    if a is None or b is None or a[3] > b[4] or b[3] > a[4]:
        return 0.0
    return max(0.0, a[2] + b[2] - math.hypot(a[0] - b[0], a[1] - b[1]))


def kitchen_host_member(pa: dict, pb: dict) -> tuple[Optional[dict], Optional[dict]]:
    """``(run, member)`` of a pair of kitchen-run pieces when one is a counter or island (``KITCHEN_RUN_HOSTS``) and
    the other a floor-standing member (``KITCHEN_RUN_MEMBERS``), else ``(None, None)`` (fix round after P3)."""
    for run, member in ((pa, pb), (pb, pa)):
        if run.get("type") in KITCHEN_RUN_HOSTS and member.get("type") in KITCHEN_RUN_MEMBERS and not wall_hung(member):
            return run, member
    return None, None


BURIED_GRID = 5                  # buried_share: a 5 x 5 x 5 grid in the member's drawn box ...
BURIED_INSET = 0.10              # ... 10 % in from each side (never on a face, where ray parity is unsure)


def buried_share(caster, piece: dict, z_range: tuple[float, float]) -> float:
    """The share of the member's drawn box (its footprint, rotated, from ``z_range[0]`` to ``z_range[1]``: its
    built height) that lies inside the mesh of ``caster`` (fix round after P3): a ``BURIED_GRID`` cube of points
    ``BURIED_INSET`` in from each side, each tested by ray parity (``rest.is_inside``). A sink or stove built inside
    full-depth base units fills most of it; one that only meets the run, or stands in a gap of it, almost none."""
    from wenart.blender import rest as R

    fp = piece["footprint"]
    cx, cy = (float(v) for v in fp["center"][:2])
    w, d = (float(v) for v in fp["size"][:2])
    rad = math.radians(float(fp.get("rotation_deg") or 0.0))
    c, s = math.cos(rad), math.sin(rad)
    z0, z1 = float(z_range[0]), float(z_range[1])
    steps = [-0.5 + BURIED_INSET + (1.0 - 2.0 * BURIED_INSET) * i / (BURIED_GRID - 1) for i in range(BURIED_GRID)]
    lo, hi = caster.bounds
    inside = total = 0
    for fx in steps:
        for fy in steps:
            x, y = fx * w, fy * d
            wx, wy = cx + c * x - s * y, cy + s * x + c * y
            for fz in steps:
                point = (wx, wy, z0 + (fz + 0.5) * (z1 - z0))
                total += 1
                if all(float(lo[i]) - 1e-9 <= point[i] <= float(hi[i]) + 1e-9 for i in range(3)) \
                        and R.is_inside(caster, point):
                    inside += 1
    return inside / total if total else 0.0


def buried_depth(piece: dict, share: float) -> float:
    """The depth (metres) of a kitchen-run member's buried part (fix round after P3, part 2): ``share`` (its
    ``buried_share``) times the smaller side of its drawn footprint; 0 without a usable footprint. A sink 0.5 m deep
    wholly inside a run is 0.5 m deep in it, one with a quarter of its box inside 0.125 m."""
    try:
        side = min(float(v) for v in piece["footprint"]["size"][:2])
    except (KeyError, TypeError, ValueError):
        return 0.0
    return max(0.0, float(share)) * max(0.0, side)


def _violation(check: str, target: str, room_id, message: str, metrics: dict) -> dict:
    return {"check": check, "severity": SEVERITY[check], "target": target, "room_id": room_id, "message": message,
            "metrics": metrics}


def floor_z_of(building: dict, piece: dict) -> float:
    """The floor a piece or floor decor item stands on: the builder's ``furniture.piece_floor_z`` (track L's
    ``shell.room_floor_z`` of its room: the level's elevation + ``floor_offset_m``; the room by id or by outline), so
    S1 and S5 measure against the floor the builder placed it on."""
    from wenart.blender.furniture import piece_floor_z

    level = next((lv for lv in building.get("levels") or [] if lv.get("id") == piece.get("level_id")), None)
    return piece_floor_z(building, dict(level or {}, elevation=float((level or {}).get("elevation") or 0.0)), piece)


def wall_hung(piece: dict) -> bool:
    mb = piece.get("mount_bottom_m")
    if piece.get("form") in HUNG_FORMS.get(str(piece.get("type")), ()):
        return True                      # 29 Oct 2026 (R33): a floating nightstand
    return piece.get("type") in WALL_HUNG_TYPES or (isinstance(mb, (int, float)) and not isinstance(mb, bool)
                                                    and mb > 0)


def built_z_range(entry: dict) -> tuple[float, float]:
    """``(bottom, top)`` in world z of a scene manifest entry as built (pure; 30 Oct 2026, real04 run
    20261029-201533-full): the built mesh's world box (``box3d``, every furniture and decor entry has one); without it
    the entry's box from its bottom (``center - size / 2``) up to ``top_m`` over its floor (a piece's built top: a
    floating nightstand's, a vanity's) or up to the bottom plus the mesh's height (``bbox_m``). Why: the GPU test
    took a floating nightstand's top for its box's bottom plus the mesh's 0.22 m (0.22 m), while its box hangs at
    0.28-0.50 m and the table lamp on it stood on 0.50 m (``decor_f_L0_041_7``: "0.5 m off its host")."""
    box = entry.get("box3d")
    if isinstance(box, dict) and box.get("center") and box.get("size"):
        cz, h = float(box["center"][2]), float(box["size"][2])
        return cz - h / 2.0, cz + h / 2.0
    bottom = float(entry["center"][2]) - float(entry["size"][2]) / 2.0
    top_m = entry.get("top_m")
    if isinstance(top_m, (int, float)) and not isinstance(top_m, bool):
        floor = bottom - float(entry.get("mount_bottom_m") or 0.0)
        return bottom, floor + float(top_m)
    return bottom, bottom + float((entry.get("bbox_m") or entry["size"])[2])


def _bbox(verts) -> tuple[list[float], list[float]]:
    xs, ys, zs = zip(*((float(v[0]), float(v[1]), float(v[2])) for v in verts))
    return [min(xs), min(ys), min(zs)], [max(xs), max(ys), max(zs)]


def _boxes_overlap(a, b, margin: float) -> bool:
    return all(a[0][i] < b[1][i] - margin and b[0][i] < a[1][i] - margin for i in range(3))


def _angle_diff(a: float, b: float) -> float:
    return abs((float(a) - float(b) + 180.0) % 360.0 - 180.0)


def built_size(verts, footprint: dict) -> list[float]:
    """The built box ``[w, d, h]`` of a piece in its own frame (turned back by the footprint's rotation)."""
    r = math.radians(-float(footprint.get("rotation_deg") or 0.0))
    c, s = math.cos(r), math.sin(r)
    cx, cy = (float(v) for v in footprint["center"][:2])
    xs, ys, zs = [], [], []
    for v in verts:
        dx, dy = float(v[0]) - cx, float(v[1]) - cy
        xs.append(c * dx - s * dy)
        ys.append(s * dx + c * dy)
        zs.append(float(v[2]))
    return [max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)]


def size_failures(ftype: str, size, tol: float = TOLERANCES["size_rel"]) -> list[str]:
    """S4: the axes of a built box outside the type's real range by more than ``tol`` (``sizes.real_range``)."""
    from wenart.furniture import sizes

    real = sizes.real_range(ftype)
    if not real:
        return []
    out = []
    for axis, value, rng in (("width", size[0], real.get("width")), ("depth", size[1], real.get("depth")),
                             ("height", size[2], real.get("height"))):
        if not rng:
            continue
        lo, hi = float(rng[0]), float(rng[1])
        if value < lo / (1.0 + tol) - 1e-9 or value > hi * (1.0 + tol) + 1e-9:
            out.append(f"{axis} {value:.2f} m outside {lo:.2f}-{hi:.2f} m (+-{tol:.0%})")
    return out


def wall_boxes(building: dict, level_id: str) -> list[dict]:
    """The walls of a level as oriented boxes ``{id, a, b, thickness, z0, z1}`` (openings not cut: a piece in a
    door reveal counts as in the wall). Milestone 12: a wall beside a sunken room starts at that room's floor, as
    the shell builds it (``shell.wall_base_drop``)."""
    from wenart.blender.shell import wall_base_drop

    level = next((lv for lv in building.get("levels") or [] if lv.get("id") == level_id), {})
    z0 = float(level.get("elevation") or 0.0)
    rooms = [r for r in building.get("rooms") or [] if r.get("level_id") == level_id]
    out = []
    for w in building.get("walls") or []:
        if w.get("level_id") != level_id or not w.get("start") or not w.get("end"):
            continue
        h = w.get("height")
        h = float(h.get("value") if isinstance(h, dict) else h) if h else float(level.get("ceiling_height") or 2.7)
        drop = wall_base_drop({"start": w["start"], "end": w["end"], "thickness": float(w.get("thickness") or 0.1)},
                              rooms)
        out.append({"id": w["id"], "a": tuple(map(float, w["start"][:2])), "b": tuple(map(float, w["end"][:2])),
                    "thickness": float(w.get("thickness") or 0.1), "z0": z0 + drop, "z1": z0 + h})
    return out


def depth_in_wall(point, wall: dict) -> float:
    """How far a point is inside a wall box (0 outside): the distance to the nearer long face."""
    ax, ay = wall["a"]
    bx, by = wall["b"]
    length = math.hypot(bx - ax, by - ay)
    if length < 1e-9 or not wall["z0"] - 1e-9 <= point[2] <= wall["z1"] + 1e-9:
        return 0.0
    ux, uy = (bx - ax) / length, (by - ay) / length
    s = (point[0] - ax) * ux + (point[1] - ay) * uy
    n = -(point[0] - ax) * uy + (point[1] - ay) * ux
    half = wall["thickness"] / 2.0
    if not (0.0 < s < length) or abs(n) >= half:
        return 0.0
    return min(half - abs(n), s, length - s)


def wall_bbox(wall: dict) -> tuple[list[float], list[float]]:
    """Fix round after P6b: the axis-aligned box of a wall box (``wall_boxes``), its half thickness around the line."""
    half = wall["thickness"] / 2.0
    (ax, ay), (bx, by) = wall["a"], wall["b"]
    return ([min(ax, bx) - half, min(ay, by) - half, wall["z0"]], [max(ax, bx) + half, max(ay, by) + half, wall["z1"]])


def through_wall(verts, faces, wall: dict) -> float:
    """Fix round after P6b (module docstring): the wall's thickness when an edge of the mesh runs through the whole
    wall box (one end at or beyond each long face, its crossing of the wall's middle plane inside the wall's length
    and height), else 0.0. ``depth_in_wall`` measures vertices, so a piece through the wall with every vertex on
    either side of it measured 0 (P6b's wardrobe f_L0_098, 0.28 m through the front outer wall)."""
    ax, ay = wall["a"]
    bx, by = wall["b"]
    length = math.hypot(bx - ax, by - ay)
    if length < 1e-9 or not faces:
        return 0.0
    ux, uy = (bx - ax) / length, (by - ay) / length
    half = wall["thickness"] / 2.0
    arr = np.asarray(verts, dtype=np.float64).reshape(-1, 3)
    s = (arr[:, 0] - ax) * ux + (arr[:, 1] - ay) * uy
    n = -(arr[:, 0] - ax) * uy + (arr[:, 1] - ay) * ux
    if n.min() > -half or n.max() < half:
        return 0.0                                   # the mesh does not reach both faces of the wall
    pairs = {(min(int(a), int(b)), max(int(a), int(b))) for f in faces for a, b in zip(f, list(f[1:]) + [f[0]])
             if int(a) != int(b)}
    if not pairs:
        return 0.0
    e = np.asarray(sorted(pairs), dtype=np.int64)
    n0, n1 = n[e[:, 0]], n[e[:, 1]]
    cross = ((n0 <= -half) & (n1 >= half)) | ((n1 <= -half) & (n0 >= half))
    if not cross.any():
        return 0.0
    e, n0, n1 = e[cross], n0[cross], n1[cross]
    t = -n0 / (n1 - n0)
    sm = s[e[:, 0]] + t * (s[e[:, 1]] - s[e[:, 0]])
    zm = arr[e[:, 0], 2] + t * (arr[e[:, 1], 2] - arr[e[:, 0], 2])
    inside = (sm > 0.0) & (sm < length) & (zm >= wall["z0"] - 1e-9) & (zm <= wall["z1"] + 1e-9)
    return float(wall["thickness"]) if inside.any() else 0.0


def usable_asset(asset: Optional[dict]) -> bool:
    from wenart.furniture import catalog as C

    # Milestone 13 (§13.2 T1): usable in the run's licence mode (the fitted asset carries ``licence_mode``).
    return bool(asset) and C.usable(asset, asset.get("licence_mode") or "commercial")


def hang_gap(verts, building: dict, item: dict) -> Optional[dict]:
    """How far a hung light's top is under the ceiling over it (28 Oct 2026, module docstring; pure): the top of its
    mesh (its cord and canopy are part of it) at the plan point of its top (``furniture.top_point``) against the
    level's ceiling there (``furniture.ceiling_above``: flat, or the sloped ceiling under a roof). None without its
    level."""
    from wenart.blender.furniture import ceiling_above, top_point

    level = next((lv for lv in building.get("levels") or [] if lv.get("id") == item.get("level_id")), None)
    if level is None or not verts:
        return None
    top = max(float(v[2]) for v in verts)
    xy = top_point(verts)
    ceiling = float(level.get("elevation") or 0.0) + float(ceiling_above(level, xy, (0.0, 0.0))[0])
    return {"hang_gap_m": round(ceiling - top, 4), "top_z": round(top, 4), "ceiling_z": round(ceiling, 4)}


def _decor_support(item: dict, host: Optional[dict]) -> str:
    from wenart.blender import rest as R             # not wenart.furniture.decor: Blender's Python has no shapely

    return R.item_support(item, host)


def measure(meshes: dict, building: dict, caster_factory: Callable) -> dict:
    """The measurements and violations of S1-S6 for every id of ``meshes`` (the module docstring)."""
    from wenart import geometry as G
    from wenart.blender import rest as R
    from wenart.furniture import catalog as C

    tol = TOLERANCES
    pieces = {p["id"]: p for p in building.get("furniture") or []}
    decor = {d["id"]: d for d in building.get("decor") or [] if d.get("id")}
    counts = {c: {"checked": 0, "failed": 0} for c in CHECKS}
    measured: dict[str, dict] = {}
    violations: list[dict] = []
    casters: dict[str, object] = {}

    def caster(mid: str):
        if mid not in casters:
            casters[mid] = caster_factory(meshes[mid]["verts"], meshes[mid]["faces"])
        return casters[mid]

    def fail(check: str, target: str, room_id, message: str, metrics: dict) -> None:
        counts[check]["failed"] += 1
        violations.append(_violation(check, target, room_id, message, metrics))

    piece_ids = sorted(i for i in meshes if i in pieces)
    boxes = {i: _bbox(meshes[i]["verts"]) for i in piece_ids}
    walls_by_level: dict[str, list] = {}
    for pid in piece_ids:
        piece, mesh = pieces[pid], meshes[pid]
        m = measured.setdefault(pid, {"type": piece["type"]})
        room = piece.get("room_id")
        # S1 floor contact
        if not wall_hung(piece):
            counts["S1"]["checked"] += 1
            gap = boxes[pid][0][2] - floor_z_of(building, piece)
            m["floor_gap_m"] = round(gap, 4)
            if gap < -tol["floor_sink_m"] - 1e-9 or gap > tol["floor_gap_m"] + 1e-9:
                fail("S1", pid, room, f"{piece['type']} {pid}: lowest point {gap:+.3f} m from its floor "
                                      f"(allowed -{tol['floor_sink_m']} .. +{tol['floor_gap_m']} m)",
                     {"floor_gap_m": round(gap, 4)})
        # S2 walls
        if not wall_hung(piece):
            walls = walls_by_level.setdefault(piece.get("level_id"), wall_boxes(building, piece.get("level_id")))
            pts = R.sample_points(mesh["verts"], MAX_PAIR_SAMPLES)
            worst = (0.0, None)
            through: Optional[str] = None
            wall_tol = overlap_tolerance(piece["type"])
            for w in walls:
                d = max((depth_in_wall(p, w) for p in pts), default=0.0)
                full = 0.0
                if d <= wall_tol + 1e-9 and _boxes_overlap(boxes[pid], wall_bbox(w), 0.0):
                    # fix round after P6b (module docstring): a piece through the whole wall has no vertex inside it
                    full = through_wall(mesh["verts"], mesh["faces"], w)
                if max(d, full) > worst[0]:
                    worst = (float(max(d, full)), w["id"])
                    through = w["id"] if full > d else None
            counts["S2"]["checked"] += 1
            m["wall_depth_m"] = round(worst[0], 4)
            m["s2_tolerance_m"] = wall_tol
            if worst[0] > wall_tol + 1e-9:
                passes = through is not None
                if passes:
                    m["wall_through"] = through
                what = (f"passes through wall {worst[1]} ({worst[0]:.3f} m thick: no vertex inside it)" if passes
                        else f"cuts wall {worst[1]} by {worst[0]:.3f} m")
                fail("S2", pid, room, f"{piece['type']} {pid} {what} (allowed {wall_tol:.3f} m for a "
                                      f"{s2_class(piece['type'])} piece)",
                     dict({"depth_m": round(worst[0], 4), "wall_id": worst[1], "tolerance_m": wall_tol,
                           "class": s2_class(piece["type"])}, **({"through": True} if passes else {})))
        # S3 front
        if piece.get("front_deg") is not None:
            counts["S3"]["checked"] += 1
            built = mesh.get("front_deg")
            if built is None:
                built = G.front_direction_deg(float(piece["footprint"]["rotation_deg"]))
            diff = _angle_diff(built, piece["front_deg"])
            m["front_diff_deg"] = round(diff, 2)
            if diff > tol["front_deg"] + 1e-9:
                fail("S3", pid, room, f"{piece['type']} {pid}: built front {built:.0f} deg, planned "
                                      f"{float(piece['front_deg']):.0f} deg ({diff:.0f} deg off)",
                     {"built_front_deg": round(float(built), 2), "planned_front_deg": float(piece["front_deg"])})
        # S4 real size
        size = built_size(mesh["verts"], piece["footprint"])
        m["built_size_m"] = [round(v, 3) for v in size]
        if piece["type"] not in C.BY_DESIGN_PARAMETRIC_TYPES and \
                piece.get("form") not in HUNG_FORMS.get(str(piece["type"]), ()):     # a floating box is its form
            counts["S4"]["checked"] += 1
            bad = size_failures(piece["type"], size)
            if bad:
                fail("S4", pid, room, f"{piece['type']} {pid}: {'; '.join(bad)}",
                     {"built_size_m": [round(v, 3) for v in size]})
        # S6 typed and audited, or by-design parametric
        counts["S6"]["checked"] += 1
        method = mesh.get("method") or (piece.get("asset") or {}).get("method")
        ok, why = True, ""
        if piece["type"] == "unknown":
            ok, why = False, "an untyped (unknown) piece is built"
        elif method == "library":
            if not usable_asset(piece.get("asset")):
                ok, why = False, "its library model is not usable (audit removed, or an NC/SA/ND licence)"
        elif not C.by_design_parametric(piece):
            # Milestone 13 (§13.2 T1, D4 ladder): a module or parametric piece built below the library level
            # because no audited model fits is the contract (its ``library_gap`` names the step; the fit reports
            # it), not a violation.
            gap = (piece.get("asset") or {}).get("library_gap") or piece.get("library_gap")
            if method in ("module", "parametric") and isinstance(gap, dict) and gap.get("step") in ("module",
                                                                                                    "parametric"):
                m["s6_library_gap"] = gap.get("step")
            else:
                ok, why = False, (f"a parametric {piece['type']} (parametric only for "
                                  f"{', '.join(C.BY_DESIGN_PARAMETRIC_TYPES)})")
        m["s6"] = "ok" if ok else why
        if not ok:
            fail("S6", pid, room, f"{piece['type']} {pid}: {why}", {"method": method})
    # S2 between pieces
    for i, a in enumerate(piece_ids):
        for b in piece_ids[i + 1:]:
            pa, pb = pieces[a], pieces[b]
            if pa.get("level_id") != pb.get("level_id"):
                continue
            if pa["type"] in KITCHEN_RUN_TYPES and pb["type"] in KITCHEN_RUN_TYPES:
                run, member = kitchen_host_member(pa, pb)
                if run is None or not _boxes_overlap(boxes[run["id"]], boxes[member["id"]], 0.0):
                    continue                    # two runs, two members, a wall cabinet, or apart: may overlap
                mb = boxes[member["id"]]
                share = buried_share(caster(run["id"]), member, (mb[0][2], mb[1][2]))
                counts["S2"]["checked"] += 1
                limit = float(tol["kitchen_buried_share"])
                depth = buried_depth(member, share)     # fix round after P3, part 2: metrics13 and causes read it
                measured[member["id"]]["kitchen_run"] = {"run": run["id"], "inside_share": round(share, 3),
                                                         "depth_m": round(depth, 4)}
                if share >= limit - 1e-9:
                    fail("S2", member["id"], member.get("room_id"),
                         f"{member['type']} {member['id']} is buried in the {run['type']} {run['id']}: "
                         f"{share:.0%} of its box is inside the run, {depth:.2f} m deep (allowed under {limit:.0%}; "
                         "a drawn sink inside a run is built into it, a drawn stove stands in a gap of it"
                         # 31 Oct 2026 (wenart.blender.fridge_rule): the fit's guard should have caught it
                         + ("; a fridge never stands in a run: the tall-unit column holds it or the run ends at it "
                            "and continues past it, fridge rule of 31 Oct 2026)" if member["type"] == "fridge"
                            else ")"),
                         {"inside_share": round(share, 3), "depth_m": round(depth, 4),
                          "depth_from": "inside_share x the smaller drawn side", "other": run["id"],
                          "kitchen_run": True})
                continue
            pair_tol = overlap_tolerance(pa["type"], pb["type"])
            if not _boxes_overlap(boxes[a], boxes[b], pair_tol):
                continue
            if pa["type"] in LAMP_SHADE_TYPES and pb["type"] in LAMP_SHADE_TYPES:
                # fix round after P6a: open shades through each other (the mesh test need not find a point inside)
                shade = shade_overlap(meshes[a]["verts"], meshes[b]["verts"])
                if shade > pair_tol + 1e-9:
                    counts["S2"]["checked"] += 1
                    fail("S2", a, pa.get("room_id"), f"{pa['type']} {a} and {pb['type']} {b}: their shades overlap by "
                                                     f"{shade:.3f} m (allowed {pair_tol:.3f} m)",
                         {"depth_m": round(shade, 4), "other": b, "tolerance_m": pair_tol, "shade": True})
                    measured[a].setdefault("cuts", []).append({"id": b, "depth_m": round(shade, 4), "shade": True})
                    continue
            depth = float(max(R.penetration(caster(b), R.sample_points(meshes[a]["verts"], MAX_PAIR_SAMPLES)),
                              R.penetration(caster(a), R.sample_points(meshes[b]["verts"], MAX_PAIR_SAMPLES))))
            counts["S2"]["checked"] += 1
            if depth > pair_tol + 1e-9:
                fail("S2", a, pa.get("room_id"), f"{pa['type']} {a} and {pb['type']} {b} cut each other by "
                                                 f"{depth:.3f} m (allowed {pair_tol:.3f} m)",
                     {"depth_m": round(depth, 4), "other": b, "tolerance_m": pair_tol})
                measured[a].setdefault("cuts", []).append({"id": b, "depth_m": round(depth, 4)})
    # S5 decor
    for did in sorted(i for i in meshes if i in decor):
        item, mesh = decor[did], meshes[did]
        host = pieces.get(item.get("host_id")) if item.get("host_id") else None
        dtype = item.get("type")
        m = measured.setdefault(did, {"type": dtype})
        if dtype in UNMEASURED_DECOR:
            m["s5"] = "not measured (hangs on a wall)"
            continue
        if dtype in HUNG_DECOR:
            # 28 Oct 2026: a hung light's top (its cord and canopy are part of its mesh) on the ceiling over it
            rh = hang_gap(mesh["verts"], building, item)
            if rh is None:
                m["s5"] = "not measured (no level for the ceiling)"
                continue
            counts["S5"]["checked"] += 1
            m.update(rh)
            ok = rh["hang_gap_m"] <= tol["decor_hang_gap_m"] + 1e-9
            m["s5"] = "ok" if ok else (f"its top {rh['hang_gap_m']:.3f} m under the ceiling over it with nothing up "
                                       f"to it > {tol['decor_hang_gap_m']} m")
            if not ok:
                fail("S5", did, item.get("room_id"), f"{dtype} {did}: {m['s5']} (it hangs in the air: a cord or rod "
                                                     "and a canopy must reach the ceiling)", rh)
            continue
        if host is None:
            if dtype not in FLOOR_DECOR:
                m["s5"] = "not measured (no host)"
                continue
            rm = R.floor_rest(mesh["verts"], floor_z_of(building, item))      # the room's floor (track L)
        else:
            host_ids = [hid for hid in (host["id"], f"{host['id']}#dressing") if hid in meshes]
            if not host_ids:
                m["s5"] = f"not measured (host {host['id']} not built)"
                continue
            host_caster = R.MultiCaster([caster(h) for h in host_ids]) if len(host_ids) > 1 else caster(host_ids[0])
            support = _decor_support(item, host)
            soft = host["type"] in SOFT_HOST_TYPES and support in SOFT_SUPPORTS
            fp = mesh.get("rest_footprint") or {"center": list(item["center"][:2]),
                                                "size": list((item.get("size") or [0.3, 0.3])[:2]),
                                                "rotation_deg": float(item.get("rotation_deg") or 0.0)}
            rm = R.measure_rest(mesh["verts"], mesh["faces"], host_caster, fp, soft)
            if dtype == "throw":                    # 27 Oct 2026: a thin cloth shows the host through it
                rm["cloth"] = True
                rm.update(R.measure_cloth(mesh["verts"], mesh["faces"], host_caster, fp))   # 28 Oct 2026
            elif support in LEANING_SUPPORTS:
                # 28 Oct 2026: a leaning item leans on its back in its upper part (the wall: the host's back edge)
                rm.update(R.measure_back(mesh["verts"], mesh["faces"], host_caster, fp, wall=host["footprint"]))
        counts["S5"]["checked"] += 1
        ok, why = R.rest_ok(rm)
        m.update(rm)
        m["s5"] = "ok" if ok else "; ".join(why)
        if not ok:
            fail("S5", did, item.get("room_id"), f"{dtype} {did}" + (f" on {host['type']} {host['id']}" if host
                                                                       else " on the floor")
                 + f": {'; '.join(why)}", rm)
    counts["failed_build"] = counts["S5"]["failed"] > 0
    return {"violations": violations, "counts": counts, "measured": measured}


def measure_pure(meshes: dict, building: dict) -> dict:
    """``measure`` with the numpy ray caster (``rest.MeshCaster``): the CPU tests' scene checks."""
    from wenart.blender import rest as R

    return measure(meshes, building, R.MeshCaster)


# --------------------------------------------------------------------------
# Blender
# --------------------------------------------------------------------------

def object_mesh(ob, depsgraph=None) -> dict:
    """World-space ``{"verts", "faces"}`` of an object's evaluated mesh (modifiers applied), plus the fields the
    builder recorded on it (``wenart_front_deg``, ``wenart_method``, ``wenart_rest_footprint``)."""
    import bpy

    depsgraph = depsgraph or bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(depsgraph)
    me = ev.to_mesh()
    try:
        mw = ob.matrix_world
        verts = [tuple(mw @ v.co) for v in me.vertices]
        faces = [list(p.vertices) for p in me.polygons]
    finally:
        ev.to_mesh_clear()
    out = {"verts": verts, "faces": faces}
    if "wenart_front_deg" in ob.keys():
        out["front_deg"] = float(ob["wenart_front_deg"])
    if "wenart_method" in ob.keys():
        out["method"] = str(ob["wenart_method"])
    if "wenart_rest_footprint" in ob.keys():
        try:
            out["rest_footprint"] = json.loads(str(ob["wenart_rest_footprint"]))
        except ValueError:
            pass
    return out


def merge_meshes(meshes: list[dict]) -> dict:
    verts, faces = [], []
    out = {}
    for m in meshes:
        off = len(verts)
        verts.extend(m["verts"])
        faces.extend([[i + off for i in f] for f in m["faces"]])
        for k in ("front_deg", "method", "rest_footprint"):
            if k in m and k not in out:
                out[k] = m[k]
    out.update(verts=verts, faces=faces)
    return out


def run_scene_checks(building: dict, scene_objects: dict, out_path) -> dict:
    """S1-S6 of the objects of one level (``{piece or decor id: object or [objects]}``; a piece's bedding the build
    added is registered as ``<id>#dressing``) with Blender's BVH caster; writes the report to ``out_path``."""
    import bpy

    from wenart.blender import rest as R

    depsgraph = bpy.context.evaluated_depsgraph_get()
    meshes = {}
    for oid, obs in sorted(scene_objects.items()):
        obs = obs if isinstance(obs, (list, tuple)) else [obs]
        parts = [object_mesh(ob, depsgraph) for ob in obs if ob is not None and getattr(ob, "type", "") == "MESH"]
        parts = [p for p in parts if p["verts"] and p["faces"]]
        if parts:
            meshes[oid] = merge_meshes(parts)
    report = measure(meshes, building, R.BVHCaster)
    write_report(report, out_path)
    return report


def write_report(report: dict, out_path) -> None:
    if out_path is None:
        return
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n", encoding="utf-8")
