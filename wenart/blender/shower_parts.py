"""The walk-in shower as a real product (1 Nov 2026, lesson UL243; user on real04 run 20261031-194116-full, a bathroom:
"Give more details to shower models": a thin black slide rail with a hand shower, a stiff hose drawn as two straight
segments, a bare glass panel with one black bar; no mixer detail, no rain head worth the name, no drain, no niche or
shelf, no profiles, hinges or seals on the glass, no finish on the tray). Pure (no ``bpy``): vertex and face lists,
one mesh for the shower (lesson UL111). General for every project; real04 is only the test case.

The shower keeps its drawn footprint ``w x d`` (front -Y, the back wall +Y), its level access (UL201: the room's tiles
run in, laid to the drain's fall in the screed; ``look["level_access"]`` False: the low stone tray) and the glass on
every open side (``look["shower_sides"]``). Every part is a real product at its real size (designer values of common
products, assumed), in the family's fixture finish (``fixture_key``: matte black with a satin sheen, brushed brass,
brushed steel) and the family's stone (``stone_key``: the vanity's terrazzo, marble or dark stone):

- ``thermostat_parts``: a concealed thermostatic mixer: a rounded cover plate (250 x 100 mm, 10 mm proud), the
  temperature knob (knurled grip, its escutcheon and front cap, the 38 degree stop button) and the flow knob with its
  diverter lever (rain head or hand shower), a wall outlet with its elbow for the hose beside it.
- ``rain_head_parts``: a 25 or 30 cm rain head (square or round by family, ``FAMILY_BATH["rain_head"]``) 9 mm thick
  with a soft edge, a pattern of silicone nozzles on its face, on a 35-40 cm wall arm with its rosette and joint.
- ``slide_rail_parts``: the slide rail (24 mm) on two wall brackets (rosette, stand-off, end block), the slider with
  its lock button and the holder.
- ``hand_shower_parts``: the hand shower in the holder: a ribbed handle and a round spray face with a nozzle ring.
- ``hose_path`` / ``hose_parts``: a 1.25-2.0 m metal-wound hose hanging as one smooth curve from the hand shower to
  the outlet (both ends hang down), swept along the curve with a rib every few millimetres, its two cone nuts.
- ``glass_parts``: the glass (a fixed walk-in screen under 1 m with a wall profile, a stabiliser bar to the back wall
  and its clamp; from 1 m a fixed panel and a sliding door on a top rail with its wall brackets, round grooved rollers
  riding on the rail on their hanger plates, a bar pull, a floor guide and the closing profile), seal strips on the
  free and bottom edges, a fixed side panel on each open end with its clamps and rail.
- ``drain_parts``: a linear drain at the back wall: its frame, a grate of five long bars over a dark channel.
- ``tray_parts``: the low stone tray (a brief's choice) with a 1.5 % fall to the drain on both sides of it.
- ``niche_parts``: a niche on the back wall lined in the family's stone (a back, two sides, a top, a floor and a
  shelf, a metal edge trim, an LED strip under the top and the shelf), two pump bottles on its floor and a soap dish
  on its shelf, placed by the small-items rules (``bath_objects.placed``: a library model when the fit picked one).
  The niche box stands 10 cm proud of the tiles: a niche cut into the wall needs a cut in the shell's wall.
- a towel bar inside with a towel on it: on the back wall where it has room beside the niche and the mixer, else on
  a side wall of the shower (never on a glass side).

``layout`` places them on the back wall clear of each other (the mixer under the rain head, the rail and the hand
shower on the right, the niche on the left), ``products`` names them for the scene record.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart.blender import bath_objects as BO
from wenart.blender import bath_parts as BT
from wenart.blender import parametric as P
from wenart.blender import small_parts as SM
from wenart.blender import towel_parts as TP

Part = dict
LESSON = "UL243"
RULE = "shower_parts (1 Nov 2026)"

# the family's fixture finish -> the material key of the fittings (``bath_parts.FIXTURE_KEYS``: matte black with a
# satin sheen is the black lacquer, not the flat metallic black of the handles, whose black base gives no highlight)
FIXTURE_KEYS: dict[str, str] = BT.FIXTURE_KEYS
FINISH_WORDS: dict[str, str] = {"black": "matte black", "brass": "brushed brass", "chrome": "brushed steel"}
RAIN_SHAPES: tuple[str, ...] = ("square", "round")
SEAL_KEY = "frosted_glass"        # a clear PVC seal strip (the small items' frosted glass: translucent)
NOZZLE_KEY = "dark"               # black silicone nozzles
SHADOW_KEY = "glass_black"        # the drain's channel under its grate: darker than a matte black grate

MIXER = {"plate_m": (0.25, 0.10), "plate_t_m": 0.010, "knob_dx_m": 0.068, "knob_r_m": 0.024, "grip_m": 0.030,
         "ribs": 36, "rib_m": 0.0011, "outlet_gap_m": 0.045, "outlet_r_m": 0.025}
RAIN = {"sizes_m": (0.25, 0.30), "big_from_m": 0.80, "t_m": 0.009, "edge_m": 0.0025, "rosette_r_m": 0.032,
        "arm_r_m": 0.0105, "arm_m": 0.40, "drop_m": 0.030, "nozzle_r_m": 0.0016, "nozzle_h_m": 0.0015,
        "pitch_m": 0.026, "border_m": 0.022}
RAIL = {"r_m": 0.012, "standoff_m": 0.045, "bracket_r_m": 0.024, "end_m": 0.035, "slider_z_m": 1.55,
        "from_right_m": 0.18}
HAND = {"handle_m": 0.17, "head_r_m": 0.055, "head_t_m": 0.0265, "rib_m": 0.006, "out_m": 0.040}
HOSE = {"lengths_m": (1.25, 1.50, 1.60, 1.75, 2.00), "slack_m": 0.35, "min_z_m": 0.30, "bend_m": (0.05, 0.25),
        "lead_m": 0.06, "smooth": 60, "r_m": 0.0068,
        "rib_m": 0.0007, "pitch_m": 0.007, "bulge_m": 0.025, "sides": 8, "nut_m": 0.022}
DRAIN = {"w_m": 0.07, "frame_m": 0.006, "bars": 5, "bar_m": 0.0035, "end_gap_m": 0.05, "from_wall_m": 0.06}
FALL = 0.015                      # the tray's fall to the drain (1.5 %; a level floor's fall is in the screed)
TRAY_DRAIN_MIN_M = 0.008          # the tray's top at the drain at least this high
NICHE = {"w_m": 0.30, "min_w_m": 0.20, "h_m": 0.60, "z_m": 1.15, "d_m": 0.10, "t_m": 0.015, "back_m": 0.012,
         "side_gap_m": 0.10, "trim_m": 0.002, "min_d_m": 0.55}
GLASS_HW = {"profile_m": (0.022, 0.022), "post_m": 0.024, "rail_m": 0.030, "stab_r_m": 0.0095, "seal_m": 0.006,
            "wheel_r_m": 0.022, "wheel_w_m": 0.012}
TOWEL_BAR_MIN_M = 0.30            # a free stretch of the back wall at least this wide takes the towel bar


# --------------------------------------------------------------------------
# the family's finish and stone
# --------------------------------------------------------------------------

def _look(look) -> dict:
    return look if isinstance(look, dict) else {}


def _spec(look: dict) -> Optional[dict]:
    """The family row of a look that names its family (``bath_parts.spec_of``), else None."""
    return BT.spec_of(look["family"])[0] if look.get("family") else None


fixture_key = BT.fixture_key         # the fittings' key in the look's finish, ``handle`` without one


def stone_key(look: Optional[dict]) -> str:
    """The stone of the tray and the niche: the family's top (``FAMILY_BATH["top_key"]``: terrazzo, marble or dark
    stone), ``stone_light`` (marble) without a family."""
    look = _look(look)
    spec = _spec(look)
    key = look.get("shower_stone") or (spec or {}).get("top_key")
    return str(key) if key in ("terrazzo", "stone_light", "worktop") else "stone_light"


def rain_shape(look: Optional[dict]) -> str:
    look = _look(look)
    shape = look.get("rain_head") or (_spec(look) or {}).get("rain_head")
    return shape if shape in RAIN_SHAPES else "square"


def rounded(look: Optional[dict]) -> bool:
    return bool((_spec(_look(look)) or {}).get("rounded"))


# --------------------------------------------------------------------------
# mesh helpers
# --------------------------------------------------------------------------

def _rbox(cx: float, cy: float, z0: float, sx: float, sy: float, sz: float, rc: float, key: str, role: str,
          axis: str = "z", n: int = 3) -> Part:
    """A box ``sx x sy x sz`` (centre ``cx, cy``, from ``z0``) whose edges along ``axis`` are rounded by ``rc``."""
    half = {"x": sx / 2.0, "y": sy / 2.0, "z": sz / 2.0}
    c = {"x": cx, "y": cy, "z": z0 + sz / 2.0}
    u, v = {"x": ("y", "z"), "y": ("z", "x"), "z": ("x", "y")}[axis]       # cyclic: (u, v, axis) right-handed
    ring = SM.rounded_rect(half[u], half[v], min(rc, half[u] * 0.999, half[v] * 0.999), n)
    verts = []
    for s in (-half[axis], half[axis]):
        for a, b in ring:
            p = {axis: c[axis] + s, u: c[u] + a, v: c[v] + b}
            verts.append((p["x"], p["y"], p["z"]))
    m = len(ring)
    faces = [[i, (i + 1) % m, m + (i + 1) % m, m + i] for i in range(m)]
    faces += [list(range(m - 1, -1, -1)), list(range(m, 2 * m))]
    return SM.outward({"verts": verts, "faces": faces, "key": key, "role": role})


_rr_loft = BO.rr_loft               # a rounded-rectangle loft on a wall (the flush plate's helper)


def _flat_slab(cx: float, cy: float, z_top: float, a: float, b: float, r: float, rings: Sequence[tuple[float, float]],
               key: str, role: str, n: int = 6) -> Part:
    """A horizontal slab hanging from ``z_top`` (a rain head): rounded-rectangle rings ``(inset, drop)``, closed at its
    top and its bottom."""
    verts = []
    for inset, drop in rings:
        verts += [(cx + u, cy + v, z_top - drop) for u, v in BO.rounded_rect(a - inset, b - inset, r - inset, n)]
    m = 4 * (n + 1)
    faces = []
    for k in range(len(rings) - 1):
        p, q = k * m, (k + 1) * m
        faces += [[p + i, p + (i + 1) % m, q + (i + 1) % m, q + i] for i in range(m)]
    faces += [list(range(m)), [(len(rings) - 1) * m + i for i in reversed(range(m))]]
    return SM.outward({"verts": verts, "faces": faces, "key": key, "role": role})


def _sloped_slab(x0: float, x1: float, y0: float, y1: float, z_bottom: float, z_top0: float, z_top1: float, key: str,
                 role: str) -> Part:
    """A slab from ``z_bottom`` whose top falls from ``z_top0`` at ``y0`` to ``z_top1`` at ``y1`` (a tray's fall)."""
    verts = [(x0, y0, z_bottom), (x1, y0, z_bottom), (x1, y1, z_bottom), (x0, y1, z_bottom),
             (x0, y0, z_top0), (x1, y0, z_top0), (x1, y1, z_top1), (x0, y1, z_top1)]
    faces = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    return SM.outward({"verts": verts, "faces": faces, "key": key, "role": role})


def _unit(v):
    m = math.sqrt(sum(c * c for c in v)) or 1e-12
    return tuple(c / m for c in v)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def sweep(points: Sequence[Sequence[float]], radii, key: str, role: str, sides: int = 8, smooth: bool = True) -> Part:
    """A closed tube along the 3D polyline ``points`` (``radii`` one per point or one value) with rotation-minimising
    frames (each ring's frame is the one before it carried along the curve), so a path that turns from level to
    plumb (a hose, an elbow) never twists or pinches; both ends capped, wound outwards."""
    pts = [tuple(float(c) for c in p) for p in points]
    n = len(pts)
    rs = list(radii) if isinstance(radii, (list, tuple)) else [float(radii)] * n
    tangents = [_unit(tuple(pts[min(n - 1, k + 1)][i] - pts[max(0, k - 1)][i] for i in range(3))) for k in range(n)]
    e1 = SM._frame(tangents[0])[0]
    verts = []
    for k, (p, t) in enumerate(zip(pts, tangents)):
        if k:
            dot = sum(a * b for a, b in zip(e1, t))
            e1 = _unit(tuple(a - dot * b for a, b in zip(e1, t)))
        e2 = _cross(t, e1)
        r = max(float(rs[k]), 1e-4)
        for i in range(sides):
            ang = 2.0 * math.pi * i / sides
            ca, sa = math.cos(ang) * r, math.sin(ang) * r
            verts.append(tuple(p[j] + e1[j] * ca + e2[j] * sa for j in range(3)))
    faces = []
    for k in range(n - 1):
        a, b = k * sides, (k + 1) * sides
        faces += [[a + i, a + (i + 1) % sides, b + (i + 1) % sides, b + i] for i in range(sides)]
    faces += [list(range(sides - 1, -1, -1)), [(n - 1) * sides + i for i in range(sides)]]
    return SM.outward({"verts": verts, "faces": faces, "key": key, "role": role, "smooth": smooth})


def _studs(centres, direction, r: float, length: float, key: str, role: str, sides: int = 6) -> Optional[Part]:
    """Many small round studs (nozzles) from ``centres`` along the unit ``direction``, one part (each stud closed)."""
    verts, faces = [], []
    d = _unit(direction)
    e1, e2 = SM._frame(d)
    for c in centres:
        base = len(verts)
        for s in (0.0, length):
            for i in range(sides):
                ang = 2.0 * math.pi * i / sides
                verts.append(tuple(c[j] + d[j] * s + (e1[j] * math.cos(ang) + e2[j] * math.sin(ang)) * r
                                   for j in range(3)))
        faces += [[base + i, base + (i + 1) % sides, base + sides + (i + 1) % sides, base + sides + i]
                  for i in range(sides)]
        faces += [[base + i for i in range(sides - 1, -1, -1)], [base + sides + i for i in range(sides)]]
    if not verts:
        return None
    part = {"verts": verts, "faces": faces, "key": key, "role": role}
    # each stud is wound like the first: turn them all when the first points inwards
    first = {"verts": verts[:2 * sides], "faces": [[i for i in f] for f in faces[:sides + 2]]}
    if BO._signed_volume(first) < 0.0:
        part["faces"] = [list(reversed(f)) for f in faces]
    return part


def _smooth(part: Part) -> Part:
    part["smooth"] = True
    return part


# --------------------------------------------------------------------------
# the layout on the back wall
# --------------------------------------------------------------------------

def tray_top(y: float, d: float, drain_y: float) -> float:
    """The low tray's top at ``y`` in front of the drain: ``SHOWER_TRAY_T_M`` at the front edge, falling ``FALL`` to
    the drain (at least ``TRAY_DRAIN_MIN_M`` there)."""
    y_d = drain_y - DRAIN["w_m"] / 2.0
    run = max(1e-6, y_d + d / 2.0)
    z_d = max(TRAY_DRAIN_MIN_M, BT.SHOWER_TRAY_T_M - FALL * run)
    t = max(0.0, min(1.0, (y + d / 2.0) / run))
    return BT.SHOWER_TRAY_T_M + (z_d - BT.SHOWER_TRAY_T_M) * t


def layout(w: float, d: float, h: float, look: Optional[dict] = None) -> dict:
    """Where every fitting goes (the piece frame: x across, the back wall at ``y = d / 2``, z over the floor)."""
    look = _look(look)
    h = max(1.9, float(h or 2.0))
    back = d / 2.0
    sliding = w >= BT.SLIDING_MIN_W_M - 1e-9
    level = look.get("level_access", True) is not False
    gy = -d / 2.0 + BT.GLASS_T_M / 2.0 + (0.06 if sliding else 0.01)
    drain_y = back - DRAIN["from_wall_m"]
    base = 0.0 if level else tray_top(gy, d, drain_y)
    gh = min(h, 2.0) - base
    pw, ph = MIXER["plate_m"]
    mx, mz = 0.0, BT.MIXER_Z_M
    ox, oz = mx + pw / 2.0 + MIXER["outlet_gap_m"], mz
    xr = min(max(w / 2.0 - RAIL["from_right_m"], ox + 0.09), w / 2.0 - 0.07)
    if xr < ox + 0.09 - 1e-9:                       # a narrow shower: the outlet under the mixer
        ox, oz = mx, mz - ph / 2.0 - 0.07
        xr = max(mx + pw / 2.0 + 0.05, w / 2.0 - 0.12)
    z0r, z1r = BT.SLIDE_RAIL_Z_M[0], min(BT.SLIDE_RAIL_Z_M[1], h - 0.05)
    zs = min(RAIL["slider_z_m"], z1r - 0.22)
    z_hb = zs - 0.10                                # the hand shower's handle: bottom (the hose) ...
    y_h = back - RAIL["standoff_m"] - HAND["out_m"]
    size = RAIN["sizes_m"][1] if min(w, d) >= RAIN["big_from_m"] - 1e-9 else RAIN["sizes_m"][0]
    size = max(0.18, min(size, w - 0.10, d - 0.25))
    arm = max(size / 2.0 + 0.04, min(d * 0.45, RAIN["arm_m"], d - size / 2.0 - 0.03))
    hz = min(BT.RAIN_HEAD_Z_M, h + 0.15)
    # the niche on the left, clear of the hand shower's head on the right
    niche = None
    nx0 = -w / 2.0 + NICHE["side_gap_m"]
    nw = min(NICHE["w_m"], xr - HAND["head_r_m"] - 0.04 - nx0)
    nz0 = NICHE["z_m"] + base
    if nw >= NICHE["min_w_m"] - 1e-9 and d >= NICHE["min_d_m"] - 1e-9 and nz0 + NICHE["h_m"] <= h - 0.10:
        niche = {"x0": round(nx0, 5), "x1": round(nx0 + nw, 5), "z0": round(nz0, 5), "z1": round(nz0 + NICHE["h_m"], 5),
                 "depth": NICHE["d_m"]}
    # the towel bar inside: on the back wall beside the niche and the mixer, else on a side wall that is a wall
    left = (niche["x1"] + 0.05) if niche else (-w / 2.0 + 0.08)
    right = mx - pw / 2.0 - 0.04
    towel = None
    sides = look.get("shower_sides") if isinstance(look.get("shower_sides"), dict) else {}
    y0, y1 = gy + 0.12, back - 0.15                 # along a side wall: clear of the glass's profile and the niche
    if right - left >= TOWEL_BAR_MIN_M - 1e-9:
        towel = {"wall": "back", "at": round((left + right) / 2.0, 5),
                 "length": round(min(0.40, right - left - 0.02), 5), "z": BT.TOWEL_BAR_Z_M}
    elif y1 - y0 >= TOWEL_BAR_MIN_M - 1e-9:
        wall = next((k for k in ("left", "right") if sides.get(k) != "glass"), None)
        if wall is not None:
            towel = {"wall": wall, "at": round((y0 + y1) / 2.0, 5), "length": round(min(0.40, y1 - y0 - 0.02), 5),
                     "z": BT.TOWEL_BAR_Z_M}
    return {"w": w, "d": d, "h": h, "back": back, "sliding": sliding, "level": level, "gy": gy, "base": base,
            "gh": gh, "drain_y": drain_y, "drain_len": max(0.20, w - 2.0 * DRAIN["end_gap_m"]),
            "mixer": (mx, mz), "outlet": (ox, oz), "rail_x": xr, "rail_z": (z0r, z1r), "slider_z": zs,
            "hand": (xr, y_h, z_hb), "rain": {"size": size, "shape": rain_shape(look), "arm": arm, "z": hz},
            "niche": niche, "towel": towel}


# --------------------------------------------------------------------------
# the fittings
# --------------------------------------------------------------------------

def thermostat_parts(mx: float, back: float, mz: float, outlet, fk: str, soft: bool = False) -> list[Part]:
    """The concealed thermostatic mixer on the wall: the cover plate (role ``mixer``), the temperature and the flow
    knobs (role ``knob``: an escutcheon and a front cap each, the knurled grip between them role ``knurl``), the 38
    degree stop button, the diverter lever on the flow knob and the wall outlet with its elbow (role ``outlet``) at
    ``outlet``."""
    pw, ph = MIXER["plate_m"]
    t = MIXER["plate_t_m"]
    rc = 0.03 if soft else 0.008
    parts = [_rr_loft(mx, back, mz, [(pw / 2.0, ph / 2.0, rc, 0.0), (pw / 2.0, ph / 2.0, rc, t - 0.002),
                                     (pw / 2.0 - 0.002, ph / 2.0 - 0.002, rc - 0.002, t)], fk, "mixer")]
    r, grip = MIXER["knob_r_m"], MIXER["grip_m"]
    face = back - t
    for k, sx in enumerate((-1.0, 1.0)):
        kx = mx + sx * MIXER["knob_dx_m"]
        parts.append(SM.turned([(0.0005, 0.0), (r + 0.003, 0.0), (r + 0.003, 0.003), (r + 0.001, 0.0055),
                                (0.0005, 0.006)], fk, "knob", c=(kx, face, mz), axis="-y", n=24))
        grip_part = BO._ribbed(0.0, 0.0, 0.0, r, grip, MIXER["ribs"], MIXER["rib_m"], fk, "knurl")   # no bevel
        grip_part["verts"] = [(kx + x, face - 0.006 - z, mz + y) for x, y, z in grip_part["verts"]]
        parts.append(grip_part)
        front = face - 0.006 - grip
        parts.append(SM.turned([(0.0005, 0.0), (r - 0.0005, 0.0), (r - 0.0005, 0.0015), (r - 0.004, 0.0042),
                                (0.0005, 0.005)], fk, "knob", c=(kx, front, mz), axis="-y", n=24))
        if k == 0:              # the temperature knob's 38 degree stop button on its rim
            parts.append(_rbox(kx - r * 0.62, front - 0.003, mz + r * 0.35, 0.007, 0.006, 0.007, 0.002, fk, "stop",
                               axis="y"))
        else:                   # the flow knob's diverter lever: rain head or hand shower
            parts.append(_rbox(kx, front - 0.0055, mz - 0.003, 0.007, 0.007, r + 0.006, 0.0025, fk, "diverter"))
    ox, oz = outlet
    parts.append(SM.turned([(0.0005, 0.0), (MIXER["outlet_r_m"], 0.0), (MIXER["outlet_r_m"], 0.006),
                            (MIXER["outlet_r_m"] - 0.004, 0.010), (0.0005, 0.0105)], fk, "outlet", c=(ox, back, oz),
                           axis="-y", n=24))
    parts.append(sweep([(ox, back - 0.009, oz), (ox, back - 0.026, oz), (ox, back - 0.035, oz - 0.003),
                        (ox, back - 0.040, oz - 0.010), (ox, back - 0.042, oz - 0.018), (ox, back - 0.042, oz - 0.025)],
                       0.0085, fk, "outlet", sides=14))
    return parts


def outlet_end(outlet, back: float) -> tuple[float, float, float]:
    """The elbow's open end, where the hose's nut sits on (``thermostat_parts``)."""
    return (outlet[0], back - 0.042, outlet[1] - 0.025)


def rain_head_parts(back: float, lay_rain: dict, fk: str) -> list[Part]:
    """The rain head on its wall arm: the rosette (its top at ``lay_rain["z"]``), the arm, the joint, the head (role
    ``head``: 9 mm, a soft edge, square or round) and its nozzles on the face."""
    size, shape, arm, hz = lay_rain["size"], lay_rain["shape"], lay_rain["arm"], lay_rain["z"]
    rr = RAIN["rosette_r_m"]
    za = hz - rr
    parts = [SM.turned([(0.0005, 0.0), (rr, 0.0), (rr, 0.006), (rr - 0.004, 0.011), (0.0005, 0.0115)], fk, "rosette",
                       c=(0.0, back, za), axis="-y", n=28)]
    hy = back - arm
    if shape == "round":
        parts.append(sweep([(0.0, back - 0.010, za), (0.0, hy, za)], RAIN["arm_r_m"], fk, "arm", sides=16))
    else:
        parts.append(_rbox(0.0, (back - 0.010 + hy) / 2.0, za - 0.010, 0.020, arm - 0.010, 0.020, 0.004, fk, "arm",
                           axis="y"))
    drop = RAIN["drop_m"]
    parts.append(_smooth(P._cylinder_z(0.0, hy, za - drop, 0.012, 0.012, drop, fk, "joint", n=16)))
    parts.append(SM.turned([(0.0005, 0.0), (0.016, 0.0), (0.016, 0.006), (0.012, 0.010), (0.0005, 0.011)], fk, "joint",
                           c=(0.0, hy, za - drop - 0.004), n=16))
    zt = za - drop - 0.004
    a = size / 2.0
    r = a - 1e-4 if shape == "round" else 0.025
    t, e = RAIN["t_m"], RAIN["edge_m"]
    parts.append(_flat_slab(0.0, hy, zt, a, a, r, [(0.0, 0.0), (0.0, t - e), (e * 0.4, t - e * 0.3), (e, t)], fk,
                            "head", n=10 if shape == "round" else 4))
    zb = zt - t
    inner = a - RAIN["border_m"]
    pitch = RAIN["pitch_m"]
    centres = []
    if shape == "round":
        k = 1
        centres.append((0.0, hy, zb))
        while k * pitch <= inner + 1e-9:
            rad = k * pitch
            count = max(6, int(round(2.0 * math.pi * rad / pitch)))
            centres += [(rad * math.cos(2 * math.pi * (i + 0.5 * (k % 2)) / count), hy
                         + rad * math.sin(2 * math.pi * (i + 0.5 * (k % 2)) / count), zb) for i in range(count)]
            k += 1
    else:
        m = int(2.0 * inner / pitch)
        off = -(m * pitch) / 2.0
        centres = [(off + i * pitch, hy + off + j * pitch, zb) for i in range(m + 1) for j in range(m + 1)]
    studs = _studs(centres, (0.0, 0.0, -1.0), RAIN["nozzle_r_m"], RAIN["nozzle_h_m"], NOZZLE_KEY, "nozzles")
    if studs:
        studs["verts"] = [(x, y, z + 0.0002) for x, y, z in studs["verts"]]   # rooted in the face
        parts.append(studs)
    return parts


def slide_rail_parts(xr: float, back: float, z0: float, z1: float, fk: str, soft: bool = True) -> list[Part]:
    """The slide rail on two wall brackets (role ``bracket``: a rosette, a stand-off and an end block each) and the rail
    itself (role ``rail``) between them."""
    yr = back - RAIL["standoff_m"]
    r, rb, end = RAIL["r_m"], RAIL["bracket_r_m"], RAIL["end_m"]
    parts = []
    for zb in (z0, z1 - end):
        zc = zb + end / 2.0
        parts.append(SM.turned([(0.0005, 0.0), (rb, 0.0), (rb, 0.006), (rb - 0.004, 0.010), (0.0005, 0.0102)], fk,
                               "bracket", c=(xr, back, zc), n=24, axis="-y"))
        parts.append(sweep([(xr, back - 0.009, zc), (xr, yr, zc)], 0.008, fk, "bracket", sides=12))
        parts.append(SM.turned([(0.0005, 0.0), (r + 0.004, 0.0), (r + 0.0055, 0.003), (r + 0.0055, end - 0.003),
                                (r + 0.004, end), (0.0005, end)], fk, "bracket", c=(xr, yr, zb), n=20))
    if soft:
        parts.append(_smooth(P._cylinder_z(xr, yr, z0 + end, r, r, z1 - z0 - 2.0 * end, fk, "rail", n=20)))
    else:
        parts.append(_rbox(xr, yr, z0 + end, 2.0 * r, 2.0 * r, z1 - z0 - 2.0 * end, 0.004, fk, "rail"))
    return parts


def slider_parts(xr: float, back: float, zs: float, fk: str) -> list[Part]:
    """The slider on the rail at ``zs`` (role ``slider``): its sleeve, the lock button and the holder ring round the
    hand shower's handle."""
    yr = back - RAIL["standoff_m"]
    r = RAIL["r_m"]
    y_h = yr - HAND["out_m"]
    return [SM.turned([(0.0005, 0.0), (r + 0.005, 0.0), (r + 0.006, 0.004), (r + 0.006, 0.040), (r + 0.005, 0.044),
                       (0.0005, 0.044)], fk, "slider", c=(xr, yr, zs - 0.022), n=20),
            _rbox(xr, yr - r - 0.010, zs - 0.012, 0.016, 0.022, 0.024, 0.005, fk, "slider", axis="y"),
            SM.turned([(0.0005, 0.0), (0.0045, 0.0), (0.0045, 0.003), (0.0035, 0.0045), (0.0005, 0.005)], NOZZLE_KEY,
                      "slider", c=(xr - 0.012, yr - r - 0.006, zs), axis="x", n=12),
            SM.turned([(0.0165, 0.0), (0.0190, 0.0), (0.0190, 0.026), (0.0165, 0.026)], fk, "slider",
                      c=(xr, y_h, zs - 0.020), n=20, loop=True)]


def hand_shower_parts(x: float, y: float, z_bottom: float, fk: str) -> list[Part]:
    """The hand shower (role ``hand_shower``) standing in its holder: a ribbed handle from ``z_bottom`` and a round
    spray face looking into the shower (-Y), its nozzle ring (role ``nozzles``)."""
    L, rib = HAND["handle_m"], HAND["rib_m"]
    prof = [(0.0005, 0.0), (0.0105, 0.0), (0.0115, 0.004)]
    z = 0.008
    k = 0
    while z < L - 0.022:
        rad = 0.0118 + (0.0150 - 0.0118) * z / L
        prof += [(rad, z), (rad, z + rib * 0.55), (rad - 0.0009, z + rib * 0.70), (rad - 0.0009, z + rib * 0.90)]
        z += rib
        k += 1
    prof += [(0.0150, L - 0.014), (0.0135, L - 0.006), (0.0120, L), (0.0005, L)]
    parts = [SM.turned(prof, fk, "hand_shower", c=(x, y, z_bottom), n=18)]
    hr, ht = HAND["head_r_m"], HAND["head_t_m"]
    zc = z_bottom + L + hr * 0.87
    y_back = y + 0.006                              # the face in front of the handle, the handle in its back
    parts.append(SM.turned([(0.0005, 0.0), (0.020, 0.0), (0.040, 0.006), (hr - 0.003, 0.014), (hr, 0.020),
                            (hr - 0.001, 0.024), (hr - 0.005, ht), (0.0005, ht)], fk, "hand_shower",
                           c=(x, y_back, zc), axis="-y", n=32))
    face = y_back - ht
    centres = [(x, face, zc)]
    for rad, count in ((0.014, 6), (0.026, 10), (0.038, 14)):
        centres += [(x + rad * math.cos(2 * math.pi * i / count), face, zc + rad * math.sin(2 * math.pi * i / count))
                    for i in range(count)]
    studs = _studs(centres, (0.0, -1.0, 0.0), 0.0016, 0.0012, NOZZLE_KEY, "nozzles")
    if studs:
        studs["verts"] = [(vx, vy + 0.0002, vz) for vx, vy, vz in studs["verts"]]
        parts.append(studs)
    return parts


# --------------------------------------------------------------------------
# the hose: one smooth hanging curve
# --------------------------------------------------------------------------

def _loop(D: float, z_s: float, z_e: float, rho: float, zc: float):
    """The hanging loop in the vertical plane of the two ends (``h`` along the line from the start, ``h = 0``, to the
    end, ``h = D``; ``z`` up): a straight leg from each end tangent to a circle of radius ``rho`` centred at
    ``(D / 2, zc)`` and the arc under it between the two tangent points (a belt round a pulley: one smooth curve).
    Returns ``(pieces, length)``: ``("line", p, q)`` and ``("arc", start angle, end angle)`` pieces in order."""
    c = (D / 2.0, zc)
    pieces = []
    tangents = []
    for (h, z), side in (((0.0, z_s), 1.0), ((D, z_e), -1.0)):
        dh, dz = h - c[0], z - c[1]
        dist = max(math.hypot(dh, dz), rho * 1.0001)
        phi = math.atan2(dz, dh)
        beta = math.acos(rho / dist)
        ang = phi + side * beta                       # the start's leg on the left side, the end's on the right
        tangents.append(((h, z), ang, (c[0] + rho * math.cos(ang), c[1] + rho * math.sin(ang))))
    (p_s, a_s, t_s), (p_e, a_e, t_e) = tangents
    a_s %= 2.0 * math.pi
    a_e %= 2.0 * math.pi
    while a_e <= a_s:
        a_e += 2.0 * math.pi
    pieces = [("line", p_s, t_s), ("arc", a_s, a_e), ("line", t_e, p_e)]
    length = math.dist(p_s, t_s) + rho * (a_e - a_s) + math.dist(t_e, p_e)
    return pieces, length


def _loop_point(pieces, rho: float, centre, s: float):
    """The point at arc length ``s`` along a ``_loop``."""
    for k, (kind, a, b) in enumerate(pieces):
        seg = math.dist(a, b) if kind == "line" else rho * (b - a)
        if s <= seg or k == len(pieces) - 1:
            f = 0.0 if seg < 1e-12 else min(1.0, s / seg)
            if kind == "line":
                return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
            ang = a + (b - a) * f
            return (centre[0] + rho * math.cos(ang), centre[1] + rho * math.sin(ang))
        s -= seg
    return pieces[-1][2]


def hose_radius(start, end) -> float:
    """The loop's bending radius: half the ends' horizontal distance, within ``HOSE["bend_m"]`` (a hose bends no
    tighter than its own stiffness lets it, and a wide loop hangs as a wide U)."""
    D = math.hypot(end[0] - start[0], end[1] - start[1])
    return max(HOSE["bend_m"][0], min(HOSE["bend_m"][1], D / 2.0))


def _solve_loop(start, end, length: float):
    """``(D, rho, zc, pieces, lead)`` of a hose of ``length`` between the two ends: a vertical lead of
    ``HOSE["lead_m"]`` down from each end (the hose leaves its nuts straight down), then the ``_loop`` between the
    leads' feet whose arc height is found so the whole has the hose's length; a hose too short for so wide a loop bends
    tighter (down to its stiffness, ``HOSE["bend_m"]``)."""
    D = math.hypot(end[0] - start[0], end[1] - start[1])
    lead = HOSE["lead_m"]
    z_s, z_e = start[2] - lead, end[2] - lead
    target = max(0.05, length - 2.0 * lead)
    rho = hose_radius(start, end)
    while rho > HOSE["bend_m"][0] + 1e-9 and _loop(D, z_s, z_e, rho, min(z_s, z_e) - rho - 0.002)[1] > target:
        rho = max(HOSE["bend_m"][0], rho * 0.85)
    hi = min(z_s, z_e) - rho - 0.002                 # the highest arc: its legs at their shortest
    lo = hi - 2.0 * max(length, 0.1)
    for _ in range(50):
        zc = (lo + hi) / 2.0
        if _loop(D, z_s, z_e, rho, zc)[1] > target:
            lo = zc
        else:
            hi = zc
    zc = (lo + hi) / 2.0
    return D, rho, zc, _loop(D, z_s, z_e, rho, zc)[0], lead


def hose_low(start, end, length: float) -> float:
    """The lowest point of a hose of ``length`` hanging between the two ends (``_solve_loop``: its arc's bottom)."""
    _D, rho, zc, _pieces, _lead = _solve_loop(start, end, length)
    return zc - rho


def hose_length(start, end, min_z: float = HOSE["min_z_m"]) -> float:
    """The real hose length (``HOSE["lengths_m"]``) for the two ends: the shortest at least ``slack_m`` longer than
    their distance whose loop stays over ``min_z``, else the shortest that does (at least the distance)."""
    chord = math.dist(start, end)
    for slack in (HOSE["slack_m"], 0.05):
        for length in HOSE["lengths_m"]:
            if length >= chord + slack - 1e-9 and hose_low(start, end, length) >= min_z:
                return length
    return round(chord + 0.05, 3)                    # a short custom hose: the ends are too low for a standard one


def _resample(pts, n: int) -> list:
    cum = [0.0]
    for a, b in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.dist(a, b))
    out, j = [], 0
    for i in range(n + 1):
        s = cum[-1] * i / n
        while j < len(cum) - 2 and cum[j + 1] < s:
            j += 1
        seg = max(1e-12, cum[j + 1] - cum[j])
        f = (s - cum[j]) / seg
        out.append(tuple(pts[j][c] + (pts[j + 1][c] - pts[j][c]) * f for c in range(len(pts[0]))))
    return out


def _hose_2d(start, end, length: float) -> tuple[float, list]:
    """``(D, points (h, z))`` of the hose's smoothed curve in the vertical plane of its ends (``hose_path``)."""
    D, rho, zc, pieces, lead = _solve_loop(start, end, length)
    ds = 0.005
    loop_len = sum(math.dist(a, b) if k == "line" else rho * (b - a) for k, a, b in pieces)
    m = max(2, int(lead / ds))
    pts = [(0.0, start[2] - lead * i / m) for i in range(m)]
    k_loop = max(8, int(loop_len / ds))
    pts += [_loop_point(pieces, rho, (D / 2.0, zc), loop_len * i / k_loop) for i in range(k_loop + 1)]
    pts += [(D, end[2] - lead + lead * i / m) for i in range(1, m + 1)]
    keep = max(2, int(0.5 * lead / ds))              # the leads' upper halves stay plumb under their nuts
    for _ in range(HOSE["smooth"]):
        pts = pts[:keep] + [((pts[i - 1][0] + 2.0 * pts[i][0] + pts[i + 1][0]) / 4.0,
                             (pts[i - 1][1] + 2.0 * pts[i][1] + pts[i + 1][1]) / 4.0)
                            for i in range(keep, len(pts) - keep)] + pts[len(pts) - keep:]
    return D, pts


def hose_path(start, end, length: float, bulge: float = HOSE["bulge_m"], n: int = 64
              ) -> list[tuple[float, float, float]]:
    """The centre line of a hose of ``length`` hanging between ``start`` (under the hand shower) and ``end`` (under the
    outlet): straight down from each end, then one loop (``_solve_loop``: legs tangent to an arc of at least
    ``HOSE["bend_m"][0]`` radius), the bends between the leads and the legs smoothed out (the smoothing's few
    millimetres given back to the loop), bowed ``bulge`` into the room (-Y) in its middle; ``n + 1`` points evenly
    spaced along it."""
    dx, dy = end[0] - start[0], end[1] - start[1]
    D, pts = _hose_2d(start, end, length)
    got = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    if abs(got - length) > 0.002:
        D, pts = _hose_2d(start, end, length + (length - got))
    u = (dx / D, dy / D) if D > 1e-6 else (1.0, 0.0)
    out = []
    for i, (h, z) in enumerate(_resample(pts, n)):
        y_off = bulge * math.sin(math.pi * i / n) ** 2
        out.append((start[0] + u[0] * h, start[1] + u[1] * h - y_off, z))
    out[0], out[-1] = tuple(start), tuple(end)
    return out


def hose_parts(start, end, fk: str, length: Optional[float] = None) -> list[Part]:
    """The metal-wound hose (role ``hose``): its curve (``hose_path``) swept with a rib every ``pitch_m`` and its two
    cone nuts, the one at ``start`` under the hand shower and the one at ``end`` under the outlet's elbow."""
    nut = HOSE["nut_m"]
    s = (start[0], start[1], start[2] - nut)
    e = (end[0], end[1], end[2] - nut)
    length = length or hose_length(s, e)
    n = max(8, int(round(length / HOSE["pitch_m"])))
    pts = hose_path(s, e, length, n=n)
    radii = [HOSE["r_m"] - (HOSE["rib_m"] if k % 2 else 0.0) for k in range(len(pts))]
    radii[0] = radii[-1] = HOSE["r_m"]
    parts = [sweep(pts, radii, fk, "hose", sides=HOSE["sides"])]
    cone = [(0.0005, 0.0), (0.0085, 0.0), (0.0115, 0.008), (0.0115, nut), (0.0005, nut)]
    for p in (s, e):
        parts.append(SM.turned(cone, fk, "hose", c=p, n=16))
    return parts


# --------------------------------------------------------------------------
# the floor: the drain and the tray
# --------------------------------------------------------------------------

def drain_parts(cy: float, length: float, z_top: float, fk: str) -> list[Part]:
    """A linear drain (role ``drain``) with its top at ``z_top``: the dark channel floor, the frame and a grate of
    ``DRAIN["bars"]`` long bars over it."""
    W, f, t = DRAIN["w_m"], DRAIN["frame_m"], BT.DRAIN_T_M
    z0 = z_top - t
    iw, il = W - 2.0 * f, length - 2.0 * f
    parts = [P._box(0.0, cy, z0 + 0.0002, il, iw, 0.0005, SHADOW_KEY, "drain")]
    for sy in (-1.0, 1.0):
        parts.append(P._box(0.0, cy + sy * (W / 2.0 - f / 2.0), z0, length, f, t, fk, "drain"))
    for sx in (-1.0, 1.0):
        parts.append(P._box(sx * (length / 2.0 - f / 2.0), cy, z0, f, iw, t, fk, "drain"))
    nb, bw = DRAIN["bars"], DRAIN["bar_m"]
    gap = (iw - nb * bw) / (nb + 1)
    for k in range(nb):
        y = cy - iw / 2.0 + gap * (k + 1) + bw * (k + 0.5)
        parts.append(P._box(0.0, y, z0 + 0.0008, il, bw, t - 0.0010, fk, "drain"))
    return parts


def tray_parts(w: float, d: float, drain_y: float, drain_len: float, key: str) -> list[Part]:
    """The low stone tray (role ``tray``) on the whole footprint: its top falling ``FALL`` from the front edge and from
    the wall to the drain, the drain's bed under it."""
    W = DRAIN["w_m"]
    y0, y1 = drain_y - W / 2.0, drain_y + W / 2.0
    z_d = tray_top(y0, d, drain_y)
    z_wall = z_d + FALL * (d / 2.0 - y1)
    parts = [_sloped_slab(-w / 2.0, w / 2.0, -d / 2.0, y0, 0.0, BT.SHOWER_TRAY_T_M, z_d, key, "tray"),
             _sloped_slab(-w / 2.0, w / 2.0, y1, d / 2.0, 0.0, z_d, z_wall, key, "tray"),
             P._box(0.0, drain_y, 0.0, drain_len, W, z_d - BT.DRAIN_T_M, key, "tray")]
    for sx in (-1.0, 1.0):                      # the tray's top beside the drain's ends
        span = (w - drain_len) / 2.0
        if span > 1e-4:
            parts.append(P._box(sx * (drain_len / 2.0 + span / 2.0), drain_y, 0.0, span, W, z_d, key, "tray"))
    return parts


# --------------------------------------------------------------------------
# the glass and its hardware
# --------------------------------------------------------------------------

def _u_profile(x_wall: float, sg: float, cy: float, z0: float, height: float, fk: str) -> Part:
    """A wall profile (role ``profile``) taking a glass edge: 22 x 22 mm on the wall at ``x_wall``, ``sg`` the side the
    glass comes from (+1: the glass lies at larger x)."""
    a, b = GLASS_HW["profile_m"]
    return _rbox(x_wall + sg * a / 2.0, cy, z0, a, b, height, 0.002, fk, "profile")


def glass_parts(lay: dict, look: dict, fk: str) -> list[Part]:
    """The glass of the shower (role ``glass``) and its hardware in the fixture finish; see the module docstring."""
    w, back = lay["w"], lay["back"]
    gy, base, gh = lay["gy"], lay["base"], lay["gh"]
    GT = BT.GLASS_T_M
    sides = look.get("shower_sides") if isinstance(look.get("shower_sides"), dict) else {}
    left_glass, right_glass = sides.get("left") == "glass", sides.get("right") == "glass"
    rail_z = base + gh - 0.04
    rh = GLASS_HW["rail_m"]
    post = GLASS_HW["post_m"]
    seal = GLASS_HW["seal_m"]
    parts: list[Part] = []
    if lay["sliding"]:
        half = w / 2.0
        sx0 = w / 4.0 - 0.03                                 # the sliding door's centre (closed, on the right)
        ys = gy - 0.022                                       # ... and its plane, in front of the fixed panel
        parts.append(P._box(-w / 4.0, gy, base, half, GT, gh - 0.04, "glass", "glass"))
        parts.append(P._box(sx0, ys, base + 0.01, half, GT, gh - 0.06, "glass", "glass"))
        # the top rail over both panels (30 x 30 mm, rounded), its wall brackets at a wall end
        parts.append(_rbox(0.0, gy - 0.011, rail_z, w, rh, rh, 0.004, fk, "rail", axis="x"))
        for sg, is_glass in ((-1.0, left_glass), (1.0, right_glass)):
            if not is_glass:
                parts.append(_rbox(sg * (w / 2.0 - 0.012), gy - 0.011, rail_z - 0.0075, 0.024, rh + 0.015, rh + 0.015,
                                   0.006, fk, "rail_bracket"))
        # two grooved rollers riding on the rail, each on a hanger plate on the door's face
        wr, ww = GLASS_HW["wheel_r_m"], GLASS_HW["wheel_w_m"]
        wz = rail_z + rh + wr - 0.003                         # the wheel's groove rests on the rail
        face = ys - GT / 2.0                                  # the door's front face (= the rail's front face)
        wheel_front = gy - 0.011 - ww / 2.0
        for rx in (sx0 - half / 2.0 + 0.08, sx0 + half / 2.0 - 0.08):
            parts.append(SM.turned([(0.0005, 0.0), (wr - 0.004, 0.0), (wr, 0.002), (wr - 0.003, ww / 2.0),
                                    (wr, ww - 0.002), (wr - 0.004, ww), (0.0005, ww)], fk, "roller",
                                   c=(rx, gy - 0.011 + ww / 2.0, wz), axis="-y", n=28))
            plate_top = wz + 0.012
            plate_bottom = rail_z - 0.065
            parts.append(_rr_loft(rx, face, (plate_top + plate_bottom) / 2.0,
                                  [(0.026, (plate_top - plate_bottom) / 2.0, 0.010, 0.0),
                                   (0.026, (plate_top - plate_bottom) / 2.0, 0.010, 0.0045),
                                   (0.0245, (plate_top - plate_bottom) / 2.0 - 0.0015, 0.0085, 0.006)], fk, "hanger"))
            axle = wheel_front - (face - 0.006) + 0.0005      # from the wheel's face through the plate
            parts.append(SM.turned([(0.0005, 0.0), (0.006, 0.0), (0.006, axle), (0.0005, axle)], fk, "hanger",
                                   c=(rx, wheel_front + 0.0005, wz), axis="-y", n=12))
            parts.append(SM.turned([(0.0005, 0.0), (0.010, 0.0), (0.010, 0.002), (0.007, 0.0045), (0.0005, 0.005)],
                                   fk, "hanger", c=(rx, face - 0.006, wz), axis="-y", n=20))
            parts.append(SM.turned([(0.0005, 0.0), (0.008, 0.0), (0.008, 0.0015), (0.0055, 0.0035), (0.0005, 0.004)],
                                   fk, "hanger", c=(rx, face - 0.006, rail_z - 0.040), axis="-y", n=16))
        # the bar pull on two stand-offs (UL201) on the door's leading edge
        px = sx0 - half / 2.0 + 0.07
        parts += [_smooth(P._cylinder_z(px, gy - 0.050, base + 0.85, 0.010, 0.010, 0.40, fk, "handle", n=20)),
                  _smooth(P._cylinder_y(px, gy - 0.044, base + 0.89, 0.006, 0.006, 0.018, fk, "handle", n=14)),
                  _smooth(P._cylinder_y(px, gy - 0.044, base + 1.21, 0.006, 0.006, 0.018, fk, "handle", n=14))]
        # the seals: the door's overlap seal between the two glasses, its drip seal at the bottom
        parts.append(P._box(sx0 - half / 2.0 + 0.004, ys + GT / 2.0 + 0.004, base + 0.02, seal, 0.006, gh - 0.11,
                            SEAL_KEY, "seal"))
        parts.append(P._box(sx0, ys, base + 0.002, half - 0.012, GT + 0.004, 0.010, SEAL_KEY, "seal"))
        # the floor guide at the fixed panel's free corner, the door running in its slot
        parts.append(_rbox(-0.02, gy - 0.012, base, 0.030, 0.036, 0.018, 0.005, fk, "guide"))
        # the fixed panel's wall profile (or the corner post of a side panel); the door closes into a profile
        if left_glass:
            parts.append(_rbox(-w / 2.0 + 0.016, gy, base, post, post, gh - 0.04, 0.004, fk, "profile"))
        else:
            parts.append(_u_profile(-w / 2.0, 1.0, gy, base, gh - 0.045, fk))
        if right_glass:
            parts.append(_rbox(w / 2.0 - 0.016, gy, base, post, post, gh - 0.04, 0.004, fk, "profile"))
        else:
            parts.append(_u_profile(w / 2.0, -1.0, ys, base + 0.01, gh - 0.065, fk))
            parts.append(P._box(w / 2.0 - 0.030 - seal / 2.0 + 0.002, ys, base + 0.02, seal, GT + 0.006, gh - 0.11,
                                SEAL_KEY, "seal"))
    else:
        sw = max(0.3, w * 0.7)
        x_free = -w / 2.0 + sw
        parts.append(P._box(-w / 2.0 + sw / 2.0, gy, base, sw, GT, gh, "glass", "glass"))
        if left_glass:
            parts.append(_rbox(-w / 2.0 + 0.016, gy, base, post, post, gh - 0.04, 0.004, fk, "profile"))
        else:
            parts.append(_u_profile(-w / 2.0, 1.0, gy, base, gh - 0.005, fk))
        # the seals on the free edge and under the glass
        parts.append(P._box(x_free + seal / 2.0 - 0.002, gy, base + 0.005, seal, GT + 0.004, gh - 0.01, SEAL_KEY,
                            "seal"))
        parts.append(P._box(-w / 2.0 + sw / 2.0, gy, base, sw - 0.01, GT + 0.004, 0.008, SEAL_KEY, "seal"))
        # the stabiliser bar from the glass's top to the back wall, clear of the rain head
        head_half = lay["rain"]["size"] / 2.0
        xs = x_free - 0.12
        if abs(xs) < head_half + 0.03 and -(head_half + 0.03) >= -w / 2.0 + 0.06:
            xs = -(head_half + 0.03)
        zs = base + gh - 0.06
        r = GLASS_HW["stab_r_m"]
        parts.append(_rbox(xs, gy, zs - 0.02, 0.030, 0.026, 0.040, 0.006, fk, "glass_clamp"))
        y_a = gy + 0.013
        parts.append(_smooth(P._cylinder_y(xs, y_a, zs, r, r, back - 0.010 - y_a, fk, "stabiliser", n=16)))
        parts.append(SM.turned([(0.0005, 0.0), (0.020, 0.0), (0.020, 0.007), (0.016, 0.011), (0.0005, 0.0115)], fk,
                               "stabiliser", c=(xs, back, zs), axis="-y", n=20))
    # a fixed side panel on each open end, the rail over it, its wall clamps and its bottom seal
    for sg, is_glass in ((-1.0, left_glass), (1.0, right_glass)):
        if not is_glass:
            continue
        sx = sg * (w / 2.0 - 0.016)
        y0, y1 = gy + 0.01, back - 0.005
        parts.append(P._box(sx, (y0 + y1) / 2.0, base, GT, y1 - y0, gh - 0.04, "glass", "glass"))
        r0 = gy - 0.011 if lay["sliding"] else y0             # the front rail turns the corner over it
        parts.append(_rbox(sx, (r0 + y1) / 2.0, rail_z, rh, y1 - r0, rh, 0.004, fk, "rail", axis="y"))
        for cz in (0.30, gh - 0.30):
            parts.append(_rbox(sx, back - 0.017, base + cz - 0.025, 0.030, 0.032, 0.050, 0.006, fk, "clamp"))
        parts.append(P._box(sx, (y0 + y1) / 2.0, base, GT + 0.004, y1 - y0 - 0.01, 0.008, SEAL_KEY, "seal"))
    return parts


# --------------------------------------------------------------------------
# the niche and the towel bar
# --------------------------------------------------------------------------

def niche_parts(niche: dict, back: float, sk: str, fk: str, picks=None) -> list[Part]:
    """The niche on the back wall (role ``niche``, the family's stone ``sk``): back, sides, top, floor and the shelf in
    its middle (role ``shelf``), a metal edge trim (role ``trim``), an LED strip under the top and under the shelf,
    two pump bottles on its floor and a soap dish on the shelf (``bath_objects.placed``: a library slot when ``picks``
    hold a model of that kind)."""
    picks = BO.picks_of(picks)
    x0, x1, z0, z1, D = niche["x0"], niche["x1"], niche["z0"], niche["z1"], niche["depth"]
    t, bt, tr = NICHE["t_m"], NICHE["back_m"], NICHE["trim_m"]
    nw, nh = x1 - x0, z1 - z0
    cx, cy = (x0 + x1) / 2.0, back - D / 2.0
    iw = nw - 2.0 * t
    front = back - D
    parts = [P._box(cx, back - bt / 2.0, z0, nw, bt, nh, sk, "niche"),
             P._box(x0 + t / 2.0, cy, z0, t, D, nh, sk, "niche"),
             P._box(x1 - t / 2.0, cy, z0, t, D, nh, sk, "niche"),
             P._box(cx, cy, z0, iw, D, t, sk, "niche"),
             P._box(cx, cy, z1 - t, iw, D, t, sk, "niche")]
    zf, zc = z0 + t, z1 - t
    z_shelf = (zf + zc) / 2.0 - t / 2.0
    parts.append(P._box(cx, (back - bt + front) / 2.0 - 0.002, z_shelf, iw, D - bt - 0.004, t, sk, "shelf"))
    # the metal edge trim round its opening
    parts += [P._box(x0 + t / 2.0, front - tr / 2.0, z0, t + 0.002, tr, nh, fk, "trim"),
              P._box(x1 - t / 2.0, front - tr / 2.0, z0, t + 0.002, tr, nh, fk, "trim"),
              P._box(cx, front - tr / 2.0, z0, iw, tr, t + 0.002, fk, "trim"),
              P._box(cx, front - tr / 2.0, z1 - t - 0.002, iw, tr, t + 0.002, fk, "trim")]
    for top in (zc, z_shelf):
        parts.append(P._box(cx, front + 0.022, top - BT.LED_STRIP_M[1], iw - 0.02, BT.LED_STRIP_M[0],
                            BT.LED_STRIP_M[1], "led", "led"))
    # two pump bottles (shampoo, body wash) on its floor, a soap dish on the shelf
    comp_h = z_shelf - zf - BT.LED_STRIP_M[1]
    r = min(0.028, iw / 5.0)
    bh = min(0.19, comp_h - 0.03)
    by = (back - bt + front) / 2.0 + 0.004
    if bh >= 0.10:
        for k, (key, head) in enumerate((("amber", "dark"), ("frosted", "dark"))):
            bx = cx + (k - 0.5) * (2.0 * r + 0.014)
            parts += BO.placed("pump_bottle", BO.pump_bottle(bx, by, zf, r, bh, key, head), picks)
    dr = min(0.042, (iw - 0.03) / 2.6, (D - bt - 0.02) / 1.9)
    if dr >= 0.025:
        parts += BO.placed("soap_dish", BO.soap_dish(cx, by, z_shelf + t, dr), picks)
    return parts


def towel_bar_parts(towel: dict, back: float, fk: str, w: float = 0.0) -> list[Part]:
    """The towel bar inside the shower (role ``towel_bar`` and its two ``bracket``s) with a towel hanging on it, on the
    back wall (``towel["wall"]`` ``back``, centred at ``towel["at"]`` across) or on a side wall (``left`` / ``right``
    at ``x = -/+ w / 2``, centred at ``towel["at"]`` along the depth)."""
    at, length, z = towel["at"], towel["length"], towel["z"]
    parts = [_smooth(P._cylinder_x(-length / 2.0, -0.05, z, 0.009, 0.009, length, fk, "towel_bar", n=14))]
    for sx in (-1.0, 1.0):
        parts.append(_smooth(P._cylinder_y(sx * (length / 2.0 - 0.02), -0.05, z, 0.007, 0.007, 0.05, fk, "bracket",
                                           n=10)))
        parts.append(SM.turned([(0.0005, 0.0), (0.018, 0.0), (0.018, 0.005), (0.014, 0.008), (0.0005, 0.0085)], fk,
                               "bracket", c=(sx * (length / 2.0 - 0.02), 0.0, z), axis="-y", n=16))
    parts += TP.draped_towel(0.0, -0.05, z, 0.009, min(0.30, length - 0.06), 0.40, "towel")    # UL138
    # built on a wall at y = 0 (local x along it), then turned onto its wall (rotations: the faces stay outwards)
    wall = towel.get("wall", "back")

    def move(x: float, y: float) -> tuple[float, float]:
        if wall == "left":
            return -w / 2.0 - y, at + x
        if wall == "right":
            return w / 2.0 + y, at - x
        return at + x, back + y

    return [dict(p, verts=[(*move(x, y), vz) for x, y, vz in p["verts"]]) for p in parts]


# --------------------------------------------------------------------------
# the shower
# --------------------------------------------------------------------------

def walk_in_shower_parts(w: float, d: float, h: float, look: Optional[dict] = None, picks=None) -> list[Part]:
    """B16 / UL201 / UL243: the walk-in shower in its drawn footprint ``w x d`` (front -Y, the back wall +Y); see the
    module docstring. ``picks``: the small-items record of the fit (the niche's bottles and soap dish)."""
    look = _look(look)
    lay = layout(w, d, h, look)
    fk, sk = fixture_key(look), stone_key(look)
    back = lay["back"]
    parts: list[Part] = []
    if lay["level"]:
        parts += drain_parts(lay["drain_y"], lay["drain_len"], BT.DRAIN_T_M, fk)
    else:
        parts += tray_parts(w, d, lay["drain_y"], lay["drain_len"], sk)
        z_d = tray_top(lay["drain_y"] - DRAIN["w_m"] / 2.0, d, lay["drain_y"])
        parts += drain_parts(lay["drain_y"], lay["drain_len"], z_d, fk)
    parts += glass_parts(lay, look, fk)
    parts += rain_head_parts(back, lay["rain"], fk)
    mx, mz = lay["mixer"]
    parts += thermostat_parts(mx, back, mz, lay["outlet"], fk, rounded(look))
    z0r, z1r = lay["rail_z"]
    parts += slide_rail_parts(lay["rail_x"], back, z0r, z1r, fk, rain_shape(look) == "round" or rounded(look))
    parts += slider_parts(lay["rail_x"], back, lay["slider_z"], fk)
    hx, hy, hz = lay["hand"]
    parts += hand_shower_parts(hx, hy, hz, fk)
    parts += hose_parts((hx, hy, hz), outlet_end(lay["outlet"], back), fk)
    if lay["niche"]:
        parts += niche_parts(lay["niche"], back, sk, fk, picks)
    if lay["towel"]:
        parts += towel_bar_parts(lay["towel"], back, fk, w)
    return parts


def products(w: float, d: float, h: float, look: Optional[dict] = None) -> str:
    """The shower's products in words (the module plan's record)."""
    look = _look(look)
    lay = layout(w, d, h, look)
    finish = FINISH_WORDS.get(str(look.get("finish") or ""), "black")
    rain = lay["rain"]
    words = ["walk-in shower: " + (f"sliding glass on a {finish} top rail with round rollers, a bar pull and a floor "
                                   "guide" if lay["sliding"] else "fixed glass with a wall profile and a stabiliser "
                                                                  "bar")]
    words += [f"a fixed glass panel on its {k} end" for k in ("left", "right")
              if (look.get("shower_sides") or {}).get(k) == "glass"]
    words.append("seal strips")
    words.append("level access (the room's tiles running in)" if lay["level"] else
                 f"low stone tray with a {FALL * 100:.1f} % fall")
    words.append("thermostatic mixer (two knurled knobs, a diverter) with a wall outlet")
    words.append(f"{rain['size'] * 100:.0f} cm {rain['shape']} rain head on a wall arm")
    words.append("hand shower with a ribbed handle on a slide rail with a slider and wall brackets")
    words.append("metal-wound hose")
    words.append("linear drain with a slotted grate")
    if lay["niche"]:
        words.append("stone-lined niche with a shelf, two bottles and a soap dish")
    if lay["towel"]:
        words.append("towel bar")
    return ", ".join(words)
