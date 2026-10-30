"""Small kitchen appliances and a desk's organiser as real products (30 Oct 2026, lesson UL212; user on real06 run
20261029-100801-full: "Try to improve the plain small item models more maybe kitchen needs a kettle a coffee machine
etc, or study rooms requires some other items, model them as much detail as you can").

What the runs had: the decor stage set a microwave, a coffee machine (or a coffee station), a kettle and a toaster on
every kitchen run since 28 Oct (``wenart.furniture.decor.kitchen_worktop_decor``), but ``parametric`` built them from
four or five boxes and cylinders (a steel box with a dark slab for a microwave, a cylinder with two boxes for a kettle),
so the renders showed plain blocks the user did not read as appliances; desks held a laptop, notebooks and a lamp.

Pure (no ``bpy``): vertex and face lists in the item's own frame (bottom on z = 0, front -Y, centred), the parts of
``parametric`` (``verts``, ``faces``, ``key``, ``role``), every part inside the item's box. The details a close view
shows, at the sizes of real products (assumed: a 1.7 l cordless kettle 22 x 16 x 25 cm on a 360-degree base; a
single-boiler espresso machine 24-33 cm wide with a 58 mm group head and portafilter; a 2-slice toaster 28 x 17 x
19 cm; a 20 l microwave 46 x 36 x 27 cm with a 70 % door; a 5-knife block 12 x 20 x 33 cm; 20-22 cm mills):

- ``kettle``: a base with its cord, a turned body with a shoulder, a domed lid with a button, a spout, a flattened loop
  handle with the switch and its light at its foot, a water window in a frame;
- ``coffee_machine``: an espresso machine (a tower, a hood over the brew area with a pressure gauge and buttons, the
  group head and the portafilter with its handle and spouts, a steam wand and its knob, a drip tray with a grid, a cup
  on its saucer under the spouts, a cup warmer with a rail and cups on top, a water tank behind) or, in the families
  that take one (``FAMILY_FINISH`` ``coffee``), a bean-to-cup machine (a body with a dispensing bay, twin spouts, a
  drip tray and grid, a cup, a control panel with a display and buttons, the bean hopper's lid);
- ``toaster``: a body with rounded ends and edges, two slots with rims, the lever in its groove, the browning dial,
  two buttons with their light, the crumb tray and feet;
- ``microwave``: a case on feet, a door with its smoked window and a bar handle on stand-offs, a control panel with a
  display, a dial and buttons, the side vents;
- ``knife_block``: a wooden block leaning back with five knife handles (bolsters, rivets) in its slots;
- ``pepper_mills``: a salt and a pepper mill, turned, with their bands, caps and finials;
- ``desk_organiser``: a magazine file holder with folders in it, a stapler, a desk clock with its hands and ticks, a
  small succulent in its pot.

The finish follows the style family (``finish``): steel with black in the modern homes, matt black with steel in the
industrial and japandi ones, white with steel in the minimal ones, white with oak in the Scandinavian ones, cream with
chrome in the period families; the decor stage records it on the item (``appliance``).
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart.blender import parametric as P
from wenart.blender import small_parts as SM

Part = dict
LESSON = "UL212"
N = 24                            # turned parts' segments (round at a worktop's viewing distance; UL111's budget)
NS = 16                           # small turned parts (cups, knobs, finials, a gauge): under 6 cm across
# The style family's appliance finish: the body, the trim (stainless or black), the grips and, for a tinted body, its
# colour (``accent_ceramic`` takes the item's ``colour``); ``coffee``: the machine a kitchen of the family has.
FAMILY_FINISH: dict[str, dict] = {
    "modern": {"body": "steel", "trim": "dark", "grip": "dark", "coffee": "espresso", "mills": ("steel", "dark")},
    "contemporary": {"body": "steel", "trim": "dark", "grip": "dark", "coffee": "bean_to_cup",
                     "mills": ("steel", "dark")},
    "industrial": {"body": "dark", "trim": "steel", "grip": "dark", "coffee": "espresso", "mills": ("dark", "steel")},
    "minimal": {"body": "ceramic", "trim": "steel", "grip": "dark", "coffee": "bean_to_cup",
                "mills": ("ceramic", "dark")},
    "modern minimal": {"body": "ceramic", "trim": "steel", "grip": "dark", "coffee": "bean_to_cup",
                       "mills": ("ceramic", "dark")},
    "scandinavian": {"body": "ceramic", "trim": "steel", "grip": "wood", "coffee": "espresso",
                     "mills": ("wood", "wood")},
    "japandi": {"body": "dark", "trim": "steel", "grip": "wood", "coffee": "espresso", "mills": ("wood", "dark")},
    "classic": {"body": "accent_ceramic", "colour": "cream", "trim": "steel", "grip": "accent_ceramic",
                "coffee": "espresso", "mills": ("wood", "wood")},
}
for _fam in ("traditional", "rustic", "mediterranean"):
    FAMILY_FINISH[_fam] = dict(FAMILY_FINISH["classic"])
DEFAULT_FAMILY = "modern"
APPLIANCE_TYPES: tuple[str, ...] = ("kettle", "coffee_machine", "toaster", "microwave", "knife_block", "pepper_mills")
DESK_SET_TYPES: tuple[str, ...] = ("desk_organiser",)


def finish(family: Optional[str] = None, item: Optional[dict] = None) -> dict:
    """The finish of an appliance: the item's recorded ``appliance`` over its family's ``FAMILY_FINISH`` (the modern
    homes' when the family is unknown)."""
    rec = (item or {}).get("appliance") if isinstance((item or {}).get("appliance"), dict) else {}
    fam = str(rec.get("family") or family or DEFAULT_FAMILY).strip().lower()
    out = dict(FAMILY_FINISH.get(fam, FAMILY_FINISH[DEFAULT_FAMILY]))
    out.update({k: v for k, v in rec.items() if k in ("body", "trim", "grip", "coffee", "colour") and v})
    out["family"] = fam if fam in FAMILY_FINISH else DEFAULT_FAMILY
    return out


def record(family: Optional[str], dtype: str) -> dict:
    """The ``appliance`` record the decor stage writes on an item (its family's finish; pure)."""
    f = finish(family)
    rec = {"family": f["family"], "body": f["body"], "trim": f["trim"], "grip": f["grip"], "lesson": LESSON}
    if dtype == "coffee_machine":
        rec["coffee"] = f["coffee"]
    return rec


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def move(part: Part, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> Part:
    return dict(part, verts=[(x + dx, y + dy, z + dz) for x, y, z in part["verts"]])


def rot_z(part: Part, deg: float, about=(0.0, 0.0)) -> Part:
    """The part turned about the vertical through ``about`` (a rotation: the winding stays)."""
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    ax, ay = about
    return dict(part, verts=[(ax + (x - ax) * c - (y - ay) * s, ay + (x - ax) * s + (y - ay) * c, z)
                             for x, y, z in part["verts"]])


def block(a: float, b: float, rc: float, z0: float, z1: float, edge: float, key: str, role: str,
          cx: float = 0.0, cy: float = 0.0, n: int = 4) -> Part:
    """A block of half sizes ``a`` x ``b`` with corners rounded ``rc`` in plan and its top and bottom edges eased by
    ``edge`` (four rounded-rectangle rings, the end ones inset), centred on ``(cx, cy)`` from ``z0`` to ``z1``."""
    edge = max(0.0, min(edge, (z1 - z0) / 2.0 - 1e-4, a / 2.0, b / 2.0))
    rings = [(edge, z0), (0.0, z0 + edge), (0.0, z1 - edge), (edge, z1)] if edge > 1e-5 else [(0.0, z0), (0.0, z1)]
    verts, m = [], 0
    for inset, z in rings:
        ring = SM.rounded_rect(a - inset, b - inset, max(0.0005, rc - inset), n)
        m = len(ring)
        verts += [(cx + x, cy + y, z) for x, y in ring]
    k = len(rings)
    faces = [[r * m + i, r * m + (i + 1) % m, (r + 1) * m + (i + 1) % m, (r + 1) * m + i]
             for r in range(k - 1) for i in range(m)]
    faces.append(list(range(m - 1, -1, -1)))
    faces.append([(k - 1) * m + i for i in range(m)])
    return SM.outward({"verts": verts, "faces": faces, "key": key, "role": role})


def prism_x(profile_yz: Sequence[tuple[float, float]], x0: float, x1: float, key: str, role: str) -> Part:
    """A solid from the (y, z) polygon ``profile_yz`` (counter-clockwise seen from +X) extruded from ``x0`` to ``x1``."""
    n = len(profile_yz)
    verts = [(x0, y, z) for y, z in profile_yz] + [(x1, y, z) for y, z in profile_yz]
    faces = [list(range(n - 1, -1, -1)), list(range(n, 2 * n))]
    faces += [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    return SM.outward({"verts": verts, "faces": faces, "key": key, "role": role})


def disc_y(cx: float, y_face: float, cz: float, rings: Sequence[tuple[float, float]], key: str, role: str,
           n: int = NS) -> Part:
    """A turned part on a front face: the rings ``(r, t)`` out of the face at ``y_face`` towards -Y (a knob, a dial,
    a gauge's bezel)."""
    return SM.turned(rings, key, role, c=(cx, y_face, cz), axis="-y", n=n)


def _feet(xs: Sequence[float], ys: Sequence[float], h: float, r: float = 0.008) -> list[Part]:
    return [P._cylinder_z(x, y, 0.0, r, r, h, "dark", "foot", n=12) for x in xs for y in ys]


CORD_R_M = 0.0032


def _cord(p0, p1) -> Part:
    """A power cord from ``p0`` dropping onto the worktop at ``p1`` (never under it)."""
    lo = CORD_R_M + 0.0005
    q0 = (p0[0], p0[1], max(p0[2], lo))
    q1 = (p1[0], p1[1], max(p1[2], lo))
    mid = ((q0[0] + q1[0]) / 2.0, (q0[1] + q1[1]) / 2.0, max(lo, min(q0[2], q1[2])))
    return SM.tube([q0, mid, q1], CORD_R_M, "dark", "cord", sides=8)


def _cup(cx: float, cy: float, z0: float, r: float, hgt: float, key: str = "ceramic", saucer: bool = True,
         handle_dir: float = 0.0) -> list[Part]:
    """An espresso cup (a turned vessel with its loop handle), on its saucer."""
    parts = []
    z = z0
    if saucer:
        rs = r * 1.75
        parts.append(SM.turned([(0.0, z0), (rs * 0.55, z0), (rs * 0.62, z0 + 0.004), (rs, z0 + 0.008),
                                (rs * 0.97, z0 + 0.011), (rs * 0.6, z0 + 0.007), (0.0, z0 + 0.007)], key, "saucer",
                               c=(cx, cy, 0.0), n=NS))
        z = z0 + 0.007
    rings = [(r * 0.62, z), (r * 0.80, z + 0.004), (r * 0.95, z + hgt * 0.35), (r, z + hgt)]
    parts.append(SM._vessel(rings, 0.0025, z + 0.006, key, "cup", c=(cx, cy, 0.0), n=NS))
    a = math.radians(handle_dir)
    ux, uy = math.cos(a), math.sin(a)
    hp = [(cx + ux * r * 0.93, cy + uy * r * 0.93, z + hgt * 0.78),
          (cx + ux * (r + 0.012), cy + uy * (r + 0.012), z + hgt * 0.74),
          (cx + ux * (r + 0.014), cy + uy * (r + 0.014), z + hgt * 0.45),
          (cx + ux * r * 0.95, cy + uy * r * 0.95, z + hgt * 0.32)]
    parts.append(SM.tube(hp, 0.0025, key, "handle", sides=6))
    return parts


# --------------------------------------------------------------------------
# the kettle
# --------------------------------------------------------------------------

def kettle(w: float, d: float, h: float, fin: Optional[dict] = None) -> list[Part]:
    fin = fin or finish()
    body_k, trim_k, grip_k = fin["body"], fin["trim"], fin["grip"]
    rb = min(d / 2.0 - 0.003, 0.082)               # the base
    r = rb - 0.007                                  # the body's foot
    base_h = 0.022
    top = h - 0.036                                 # the lid's seat
    zb = base_h + 0.001
    parts = [SM.turned([(0.0, 0.0), (rb - 0.005, 0.0), (rb, 0.005), (rb, base_h - 0.005), (rb - 0.006, base_h),
                        (0.0, base_h)], "dark", "base", n=N),
             SM.turned([(rb - 0.004, base_h - 0.001), (rb - 0.0035, base_h - 0.0005), (rb * 0.5, base_h - 0.0005),
                        (rb * 0.5, base_h - 0.001)], trim_k, "ring", n=N),
             _cord((0.0, rb - 0.012, 0.007), (0.0, d / 2.0 - 0.004, 0.004))]
    prof = [(0.0, zb), (r - 0.010, zb), (r - 0.003, zb + 0.004), (r, zb + 0.014), (r + 0.001, zb + 0.06),
            (r * 0.97, zb + 0.11), (r * 0.91, top - 0.035), (r * 0.84, top - 0.012), (r * 0.78, top)]
    parts.append(SM.turned(prof, body_k, "body", n=N))      # capped under the lid: a closed shell
    lid_r = r * 0.80
    parts.append(SM.turned([(lid_r, top - 0.002), (lid_r, top + 0.003), (lid_r * 0.86, top + 0.011),
                            (lid_r * 0.5, top + 0.017), (0.0, top + 0.018)], trim_k if body_k != "steel" else body_k,
                           "lid", n=N))
    parts.append(SM.turned([(0.0, top + 0.016), (0.011, top + 0.016), (0.011, top + 0.027), (0.009, top + 0.031),
                            (0.0, top + 0.032)], grip_k, "button", n=NS))
    # the spout (-X), flared and open-looking (a dark mouth on its end)
    sx0 = -r * 0.80
    sp = [(sx0, 0.0, top - 0.034), (sx0 - 0.018, 0.0, top - 0.020), (sx0 - 0.032, 0.0, top - 0.006),
          (-w / 2.0 + 0.010, 0.0, top + 0.002)]
    parts.append(SM.tube(sp, [0.017, 0.013, 0.010, 0.009], body_k, "spout", sides=14, squash=0.8))
    parts.append(SM.tube([(-w / 2.0 + 0.011, 0.0, top + 0.0025), (-w / 2.0 + 0.0085, 0.0, top + 0.004)], 0.007,
                         "dark", "spout_mouth", sides=14, squash=0.8))
    # the handle (+X): a flattened loop from the shoulder down to the foot, the switch and its light at its foot
    hx = w / 2.0 - 0.014
    hp = [(r * 0.86, 0.0, top - 0.012), (r * 0.86 + 0.022, 0.0, top - 0.004), (hx, 0.0, top - 0.028),
          (hx + 0.002, 0.0, zb + 0.11), (hx - 0.004, 0.0, zb + 0.055), (r + 0.006, 0.0, zb + 0.032)]
    parts.append(SM.tube(hp, [0.010, 0.011, 0.011, 0.011, 0.011, 0.012], grip_k, "handle", sides=12, squash=0.62))
    parts.append(P._box(r + 0.012, 0.0, zb + 0.022, 0.016, 0.014, 0.010, "dark", "switch"))
    parts.append(P._box(r + 0.010, -0.0073, zb + 0.026, 0.004, 0.001, 0.003, "led", "led"))
    # the water window: a framed strip towards the front, by the handle (a level scale on its edge)
    az = -58.0
    rr = r + 0.0015
    frame = P._box(rr + 0.0015, 0.0, zb + 0.022, 0.003, 0.024, 0.115, "dark", "window_frame")
    glass = P._box(rr + 0.0032, 0.0, zb + 0.030, 0.0012, 0.015, 0.098, "glass", "window")
    parts += [rot_z(frame, az), rot_z(glass, az)]
    for k in range(5):                              # the level marks beside the glass
        tick = P._box(rr + 0.0034, 0.0098, zb + 0.040 + k * 0.018, 0.0008, 0.004, 0.0012, "dark", "mark")
        parts.append(rot_z(tick, az))
    return parts


# --------------------------------------------------------------------------
# the coffee machines
# --------------------------------------------------------------------------

def espresso(w: float, d: float, h: float, fin: Optional[dict] = None) -> list[Part]:
    """A single-boiler espresso machine (module docstring)."""
    fin = fin or finish()
    body_k, trim_k, grip_k = fin["body"], fin["trim"], fin["grip"]
    steel = "steel"
    yf, yb = -d / 2.0, d / 2.0
    tank_d = min(0.055, d * 0.16)
    tower_front = yf + min(0.105, d * 0.30)
    top = h - 0.042                                 # the cup warmer: the cups on it reach the box's top
    hood_z0 = top * 0.66
    parts = _feet((-w / 2.0 + 0.025, w / 2.0 - 0.025), (yf + 0.03, yb - 0.03), 0.010)
    parts.append(block(w / 2.0 - 0.002, (yb - tank_d - tower_front) / 2.0, 0.012, 0.010, top, 0.006, body_k,
                       "body", cy=(tower_front + yb - tank_d) / 2.0))
    # the water tank behind the tower and its lid
    tyc = yb - tank_d / 2.0 - 0.002
    parts.append(block(w / 2.0 - 0.012, tank_d / 2.0, 0.006, 0.030, top * 0.92, 0.002, "glass", "tank", cy=tyc))
    parts.append(block(w / 2.0 - 0.010, tank_d / 2.0 + 0.001, 0.006, top * 0.92, top * 0.92 + 0.012, 0.002, trim_k,
                       "tank_lid", cy=tyc))
    # the hood over the brew area and the plinth with the drip tray
    hood_d = tower_front - (yf + 0.028) + 0.01
    parts.append(block(w / 2.0 - 0.002, hood_d / 2.0, 0.010, hood_z0, top, 0.006, body_k, "hood",
                       cy=yf + 0.028 + hood_d / 2.0))
    plinth_d = tower_front - (yf + 0.004) + 0.01
    parts.append(block(w / 2.0 - 0.002, plinth_d / 2.0, 0.008, 0.010, 0.040, 0.004, trim_k, "plinth",
                       cy=yf + 0.004 + plinth_d / 2.0))
    gx0, gx1 = -w / 2.0 + 0.014, w / 2.0 - 0.014
    gy0, gy1 = yf + 0.010, tower_front - 0.006
    parts.append(P._box(0.0, (gy0 + gy1) / 2.0, 0.040, gx1 - gx0 + 0.006, gy1 - gy0 + 0.006, 0.006, steel, "tray"))
    k, y = 0, gy0 + 0.004
    while y < gy1 - 0.002:                          # the drip tray's grid bars
        parts.append(P._box(0.0, y, 0.046, gx1 - gx0, 0.0022, 0.0018, "dark" if k % 2 else steel, "grid"))
        y += 0.006
        k += 1
    # the group head and the portafilter with its spouts and handle
    gy = yf + 0.028 + hood_d * 0.45
    zg = hood_z0
    parts.append(SM.turned([(0.036, zg - 0.001), (0.036, zg - 0.010), (0.031, zg - 0.013), (0.031, zg - 0.024),
                            (0.0, zg - 0.024)], steel, "group_head", c=(0.0, gy, 0.0), n=N))
    zp = zg - 0.024
    parts.append(SM.turned([(0.0, zp), (0.035, zp), (0.035, zp - 0.006), (0.031, zp - 0.024), (0.016, zp - 0.032),
                            (0.0, zp - 0.032)], steel, "portafilter", c=(0.0, gy, 0.0), n=N))
    for sx in (-0.008, 0.008):
        parts.append(SM.tube([(sx, gy, zp - 0.030), (sx * 1.6, gy, zp - 0.044)], 0.0035, steel, "spout", sides=8))
    a = math.radians(-55.0)                         # the handle points forward and to the right
    ux, uy = math.cos(a), math.sin(a)
    reach = min(0.105, (gy - yf - 0.016) / abs(uy))
    hp = [(ux * 0.034, gy + uy * 0.034, zp - 0.010), (ux * 0.060, gy + uy * 0.060, zp - 0.011),
          (ux * reach, gy + uy * reach, zp - 0.018)]
    parts.append(SM.tube(hp, [0.008, 0.011, 0.013], grip_k, "portafilter_handle", sides=12))
    # the cup on its saucer under the spouts
    parts += _cup(0.0, gy, 0.0505, 0.026, 0.050, "ceramic", handle_dir=-30.0)
    # the steam wand and its knob on the side
    wx = w / 2.0 - 0.026
    wy = yf + 0.040
    parts.append(SM.tube([(wx, wy + 0.010, hood_z0 + 0.004), (wx + 0.004, wy, hood_z0 - 0.030),
                          (wx + 0.002, wy - 0.006, 0.130), (wx - 0.002, wy - 0.008, 0.112)],
                         [0.006, 0.0042, 0.0042, 0.0036], steel, "steam_wand", sides=10))
    parts.append(SM.turned([(0.0, 0.0), (0.016, 0.0), (0.016, 0.006), (0.013, 0.012), (0.0, 0.013)], grip_k,
                           "knob", c=(w / 2.0 - 0.013, tower_front + 0.03, h * 0.72), axis="x", n=NS))
    # the hood's front: the pressure gauge and the buttons
    yface = yf + 0.028
    gz = hood_z0 + (top - hood_z0) * 0.52
    parts.append(disc_y(-w * 0.20, yface + 0.004, gz, [(0.0, 0.0), (0.021, 0.0), (0.021, 0.006), (0.018, 0.007),
                                                        (0.0, 0.007)], steel, "gauge"))
    parts.append(disc_y(-w * 0.20, yface - 0.002, gz, [(0.0, 0.0), (0.017, 0.0), (0.017, 0.0012), (0.0, 0.0012)],
                        "ceramic", "gauge_face"))
    parts.append(P._box(-w * 0.20 + 0.004, yface - 0.0035, gz + 0.002, 0.012, 0.0006, 0.0012, "dark", "needle"))
    for k, bx in enumerate((w * 0.06, w * 0.16, w * 0.26)):
        parts.append(P._box(bx, yface + 0.002, gz - 0.007, 0.014, 0.007, 0.014, trim_k if k != 1 else "dark",
                            "button"))
        parts.append(P._box(bx, yface - 0.0016, gz + 0.010, 0.003, 0.0008, 0.002, "led", "led"))
    # the cup warmer: a plate and a rail on top, two cups upside down
    zt = top
    parts.append(P._box(0.0, (tower_front + yb - tank_d) / 2.0, zt, w - 0.03, yb - tank_d - tower_front - 0.02,
                        0.003, steel, "warmer"))
    xr, y0r, y1r = w / 2.0 - 0.012, tower_front + 0.006, yb - tank_d - 0.006
    rail = [(-xr, y0r, zt + 0.003), (-xr, y0r, zt + 0.011), (-xr, y1r, zt + 0.011), (xr, y1r, zt + 0.011),
            (xr, y0r, zt + 0.011), (xr, y0r, zt + 0.003)]
    parts.append(SM.tube(rail, 0.0022, steel, "rail", sides=6, smooth=False))
    for cx in (-w * 0.17, w * 0.13):
        cy = (tower_front + yb - tank_d) / 2.0 + 0.004
        parts.append(SM.turned([(0.0, zt + 0.003), (0.027, zt + 0.003), (0.026, zt + 0.020), (0.021, zt + 0.036),
                                (0.0, zt + 0.037)], "ceramic", "cup", c=(cx, cy, 0.0), n=NS))
    return parts


def bean_to_cup(w: float, d: float, h: float, fin: Optional[dict] = None) -> list[Part]:
    """A bean-to-cup machine (module docstring)."""
    fin = fin or finish()
    body_k, trim_k = fin["body"], fin["trim"]
    yf, yb = -d / 2.0, d / 2.0
    y0 = yf + 0.072                                 # the body's front; the tray and the spouts stand out of it
    parts = _feet((-w / 2.0 + 0.025, w / 2.0 - 0.025), (y0 + 0.02, yb - 0.03), 0.010)
    parts.append(block(w / 2.0 - 0.002, (yb - y0) / 2.0, 0.020, 0.010, h - 0.004, 0.008, body_k, "body",
                       cy=(y0 + yb) / 2.0))
    bay_w, bay_z1 = min(0.13, w * 0.55), h * 0.60
    parts.append(P._box(0.0, y0 - 0.001, 0.032, bay_w, 0.003, bay_z1 - 0.032, "dark", "bay"))
    # the twin spouts' unit at the top of the bay
    parts.append(block(0.030, 0.020, 0.008, bay_z1 - 0.036, bay_z1 - 0.008, 0.004, trim_k, "spout_unit",
                       cy=y0 - 0.018))
    for sx in (-0.011, 0.011):
        parts.append(SM.tube([(sx, y0 - 0.022, bay_z1 - 0.036), (sx, y0 - 0.022, bay_z1 - 0.050)], 0.0045, "steel",
                             "spout", sides=10))
    # the drip tray and its grid
    parts.append(block(bay_w / 2.0 + 0.006, 0.026, 0.008, 0.010, 0.034, 0.003, trim_k, "tray", cy=y0 - 0.006))
    for k in range(7):
        parts.append(P._box(0.0, y0 - 0.026 + k * 0.006, 0.034, bay_w - 0.004, 0.0022, 0.0016, "steel", "grid"))
    parts += _cup(0.0, y0 - 0.034, 0.0356, 0.028, 0.064, "ceramic", saucer=False, handle_dir=-130.0)
    # the control panel on the top front: a dark glass plate, a display and the buttons
    zt = h - 0.016
    parts.append(P._box(0.0, y0 + 0.055, zt, w - 0.04, 0.085, 0.002, "dark", "panel"))
    parts.append(P._box(0.0, y0 + 0.050, zt + 0.002, w * 0.30, 0.032, 0.0006, "screen", "display"))
    for k in range(4):
        bx = (-1.5 + k) * w * 0.17
        parts.append(P._cylinder_z(bx, y0 + 0.082, zt + 0.002, 0.0055, 0.0055, 0.0012, "steel", "button", n=16))
    # the bean hopper's lid at the back, the water tank's handle on the side
    parts.append(SM.turned([(0.0, zt), (0.052, zt), (0.052, zt + 0.004), (0.044, zt + 0.007), (0.0, zt + 0.008)],
                           "dark", "hopper_lid", c=(0.0, yb - 0.080, 0.0), n=N))
    parts.append(SM.turned([(0.0, zt + 0.007), (0.010, zt + 0.007), (0.010, zt + 0.014), (0.0, zt + 0.015)],
                           trim_k, "hopper_knob", c=(0.0, yb - 0.080, 0.0), n=16))
    parts.append(P._box(w / 2.0 - 0.0015, yb - 0.09, h * 0.55, 0.003, 0.10, 0.03, trim_k, "tank_handle"))
    return parts


def coffee_machine(w: float, d: float, h: float, fin: Optional[dict] = None) -> list[Part]:
    fin = fin or finish()
    return bean_to_cup(w, d, h, fin) if fin.get("coffee") == "bean_to_cup" else espresso(w, d, h, fin)


# --------------------------------------------------------------------------
# the toaster and the microwave
# --------------------------------------------------------------------------

def toaster(w: float, d: float, h: float, fin: Optional[dict] = None) -> list[Part]:
    fin = fin or finish()
    body_k, trim_k, grip_k = fin["body"], fin["trim"], fin["grip"]
    yf = -d / 2.0
    y0 = yf + 0.014                                 # the body's front; the lever and the dial stand out of it
    a, b = w / 2.0 - 0.002, b_half(d, y0)
    cy = (y0 + d / 2.0 - 0.002) / 2.0
    parts = _feet((-a + 0.03, a - 0.03), (cy - b + 0.02, cy + b - 0.02), 0.008, r=0.007)
    parts.append(block(a, b, min(b, 0.045), 0.008, h - 0.002, 0.012, body_k, "body", cy=cy, n=6))
    # the two slots with their rims (a dark well under a raised steel rim)
    for sy in (-0.022, 0.022):
        slot = SM.rounded_rect(0.072, 0.0135, 0.010, 3)
        rim_in = SM.rounded_rect(0.068, 0.0095, 0.008, 3)
        parts.append(SM.slab([(x, y + cy + sy) for x, y in slot], h - 0.0035, 0.0045, trim_k, "slot_rim",
                             hole=[(x, y + cy + sy) for x, y in rim_in]))
        parts.append(P._box(0.0, cy + sy, h - 0.0045, 0.136, 0.019, 0.0012, "dark", "slot"))
    # the lever in its groove, the dial and the buttons on the front
    lx = a - 0.055
    parts.append(P._box(lx, y0 - 0.0008, 0.045, 0.010, 0.0018, h - 0.075, "dark", "groove"))
    parts.append(block(0.016, 0.0065, 0.004, 0.105, 0.120, 0.003, grip_k, "lever", cx=lx, cy=y0 - 0.0065))
    dx = -a + 0.055
    parts.append(disc_y(dx, y0, h * 0.50, [(0.0, 0.0), (0.019, 0.0), (0.019, 0.0015), (0.0, 0.0015)], "dark",
                        "dial_ring"))
    parts.append(disc_y(dx, y0 - 0.0015, h * 0.50, [(0.0, 0.0), (0.0135, 0.0), (0.0135, 0.009), (0.011, 0.012),
                                                      (0.0, 0.0125)], trim_k, "dial"))
    parts.append(P._box(dx, y0 - 0.0141, h * 0.50 + 0.006, 0.0018, 0.0008, 0.007, "dark", "dial_mark"))
    for k, bz in enumerate((h * 0.30, h * 0.22)):
        parts.append(P._box(lx, y0 - 0.0022, bz, 0.018, 0.005, 0.009, "dark", "button"))
        parts.append(P._box(lx + 0.012, y0 - 0.0007, bz + 0.003, 0.003, 0.0012, 0.003, "led", "led"))
    # the crumb tray along the foot of the front, and the cord at the back
    parts.append(P._box(0.0, y0 - 0.0012, 0.010, w * 0.55, 0.0025, 0.010, trim_k, "crumb_tray"))
    parts.append(_cord((a - 0.03, d / 2.0 - 0.004, 0.012), (a - 0.06, d / 2.0 - 0.003, 0.004)))
    return parts


def b_half(d: float, y0: float) -> float:
    """The toaster body's half depth from its front ``y0`` to 2 mm off the box's back."""
    return (d / 2.0 - 0.002 - y0) / 2.0


def microwave(w: float, d: float, h: float, fin: Optional[dict] = None) -> list[Part]:
    fin = fin or finish()
    body_k, trim_k = fin["body"], fin["trim"]
    yf, yb = -d / 2.0, d / 2.0
    y0 = yf + 0.026                                 # the case's front; the door and the handle stand out of it
    parts = _feet((-w / 2.0 + 0.04, w / 2.0 - 0.04), (y0 + 0.03, yb - 0.03), 0.012, r=0.010)
    parts.append(block(w / 2.0 - 0.003, (yb - y0) / 2.0, 0.008, 0.012, h, 0.006, body_k, "body", cy=(y0 + yb) / 2.0))
    door_w = w * 0.70
    dx0 = -w / 2.0 + 0.006
    dcx = dx0 + door_w / 2.0
    parts.append(block(door_w / 2.0, 0.0035, 0.006, 0.020, h - 0.010, 0.002, "dark", "door", cx=dcx, cy=y0 - 0.0035))
    parts.append(P._box(dcx - 0.012, y0 - 0.0075, 0.055, door_w - 0.09, 0.0010, h - 0.11, "smoked_glass", "window"))
    # the bar handle on its two stand-offs at the door's right edge
    hx = dx0 + door_w - 0.022
    for hz in (0.055, h - 0.055):
        parts.append(SM.tube([(hx, y0 - 0.007, hz), (hx, yf + 0.008, hz)], 0.0045, "steel", "standoff", sides=8))
    parts.append(SM.tube([(hx, yf + 0.0075, 0.045), (hx, yf + 0.0075, h - 0.045)], 0.0062, "steel", "handle",
                         sides=12))
    # the control panel: a display, a dial and the buttons
    px0 = dx0 + door_w + 0.006
    pw = w / 2.0 - 0.006 - px0
    pcx = px0 + pw / 2.0
    parts.append(P._box(pcx, y0 - 0.0015, 0.020, pw, 0.003, h - 0.030, "dark", "panel"))
    parts.append(P._box(pcx, y0 - 0.0035, h - 0.060, pw * 0.72, 0.0012, 0.022, "screen", "display"))
    parts.append(disc_y(pcx, y0 - 0.003, h * 0.36, [(0.0, 0.0), (0.020, 0.0), (0.020, 0.010), (0.017, 0.014),
                                                      (0.0, 0.015)], trim_k if trim_k != "dark" else "steel", "dial"))
    for k in range(6):
        bx = pcx + (-0.5 + (k % 2)) * pw * 0.42
        bz = h - 0.095 - (k // 2) * 0.020
        parts.append(P._box(bx, y0 - 0.0045, bz, pw * 0.34, 0.0032, 0.011, "steel", "button"))
    # the vents on the right side, the cord at the back
    for k in range(9):
        parts.append(P._box(w / 2.0 - 0.0021, yb - 0.10 - k * 0.012, h - 0.075, 0.0012, 0.005, 0.045, "dark", "vent"))
    parts.append(_cord((w / 2.0 - 0.06, yb - 0.004, 0.03), (w / 2.0 - 0.09, yb - 0.003, 0.004)))
    return parts


# --------------------------------------------------------------------------
# the knife block and the mills
# --------------------------------------------------------------------------

def knife_block(w: float, d: float, h: float, fin: Optional[dict] = None) -> list[Part]:
    fin = fin or finish()
    grip_k = "dark" if fin["grip"] in ("dark", "wood") else fin["grip"]
    t = min(w - 0.01, 0.11) / 2.0
    lean = math.radians(19.0)
    yf, yb = -d / 2.0 + 0.004, d / 2.0 - 0.004
    front_len = min(0.20, (h - 0.12) / math.cos(lean))
    ft = (yf + front_len * math.sin(lean), front_len * math.cos(lean))       # the front face's top
    top_dir = (math.cos(lean), -math.sin(lean))
    bt_len = (yb - ft[0]) / top_dir[0]
    bt = (yb, ft[1] + top_dir[1] * bt_len)                                   # the back's top
    profile = [(yf, 0.0), (yb, 0.0), bt, ft]
    parts = [prism_x(profile, -t, t, "wood", "block")]
    u = (math.sin(lean), math.cos(lean))            # the knives go into the block along its lean
    slots = [(0.18, -0.030, 0.118), (0.40, 0.000, 0.110), (0.62, 0.030, 0.105), (0.30, -0.008, 0.096),
             (0.75, 0.020, 0.090)]
    for s, xoff, length in slots:
        sy, sz = ft[0] + top_dir[0] * bt_len * s, ft[1] + top_dir[1] * bt_len * s
        # the slot in the top
        parts.append(prism_x([(sy - 0.010, sz - 0.0005), (sy + 0.010, sz - 0.0005 - 0.0069),
                              (sy + 0.010, sz + 0.0005 - 0.0069), (sy - 0.010, sz + 0.0005)],
                             xoff - 0.0016, xoff + 0.0016, "dark", "slot"))
        p0 = (xoff, sy, sz)
        p = lambda k: (xoff, sy + u[0] * k, sz + u[1] * k)                   # noqa: E731
        parts.append(SM.tube([p(0.0), p(0.012)], [0.0085, 0.0095], "steel", "bolster", sides=12, squash=0.55))
        parts.append(SM.tube([p(0.012), p(0.03), p(length - 0.012), p(length)], [0.0095, 0.0105, 0.0105, 0.007],
                             grip_k, "knife_handle", sides=12, squash=0.55))
        for k in (0.045, length - 0.03):
            parts.append(SM.turned([(0.0024, -0.0062), (0.0024, 0.0062)], "steel", "rivet",
                                   c=(xoff, p(k)[1], p(k)[2]), axis="x", n=8))
        del p0
    return parts


def pepper_mills(w: float, d: float, h: float, fin: Optional[dict] = None) -> list[Part]:
    fin = fin or finish()
    keys = fin.get("mills") or ("wood", "wood")
    r = min(d / 2.0 - 0.002, 0.028)
    parts = []
    for k, (cx, hh) in enumerate(((-w / 4.0, h * 0.92), (w / 4.0, h))):
        body_k = keys[k]
        cap_k = "steel" if body_k != "steel" else "dark"
        body = [(0.0, 0.0), (r * 0.92, 0.0), (r, 0.006), (r, hh * 0.10), (r * 0.80, hh * 0.30), (r * 0.72, hh * 0.48),
                (r * 0.80, hh * 0.64), (r * 0.95, hh * 0.76), (r * 0.95, hh * 0.80), (0.0, hh * 0.80)]
        parts.append(SM.turned(body, body_k, "mill", c=(cx, 0.0, 0.0), n=N))
        parts.append(SM.turned([(0.0, hh * 0.10), (r * 1.005, hh * 0.10), (r * 1.005, hh * 0.13), (0.0, hh * 0.13)],
                               cap_k, "band",
                               c=(cx, 0.0, 0.0), n=N))
        parts.append(SM.turned([(0.0, hh * 0.80), (r * 0.97, hh * 0.80), (r * 0.97, hh * 0.86), (r * 0.80, hh * 0.90),
                                (0.0, hh * 0.905)], cap_k if body_k == "wood" else body_k, "cap", c=(cx, 0.0, 0.0),
                               n=N))
        parts.append(SM.turned([(0.0, hh * 0.90), (0.006, hh * 0.90), (0.006, hh * 0.94), (0.010, hh * 0.965),
                                (0.008, hh * 0.99), (0.0, hh)], cap_k, "finial", c=(cx, 0.0, 0.0), n=NS))
    return parts


# --------------------------------------------------------------------------
# the desk organiser
# --------------------------------------------------------------------------

FOLDER_KEYS: tuple[str, ...] = ("terracotta", "dark", "paper", "green", "fabric")


def desk_organiser(w: float, d: float, h: float, fin: Optional[dict] = None) -> list[Part]:
    """A magazine file holder with folders, a stapler, a desk clock and a succulent (module docstring); ``w x d``
    from about 0.30 x 0.22 m."""
    fin = fin or finish()
    holder_k = {"scandinavian": "wood", "japandi": "wood", "classic": "wood", "rustic": "wood",
                "traditional": "wood", "mediterranean": "wood"}.get(fin.get("family"), "dark")
    parts = []
    # the magazine file holder (left back), open with its folders in it
    hw = min(0.085, w * 0.30)
    hx0 = -w / 2.0 + 0.004
    hy0, hy1 = -d / 2.0 + 0.004, d / 2.0 - 0.004
    hh = min(h - 0.012, 0.29)
    wall = 0.003
    prof_out = [(hy0, 0.0), (hy1, 0.0), (hy1, hh), (hy1 - (hy1 - hy0) * 0.40, hh), (hy0, hh * 0.42)]
    parts.append(prism_x(prof_out, hx0, hx0 + wall, holder_k, "holder"))
    parts.append(prism_x(prof_out, hx0 + hw - wall, hx0 + hw, holder_k, "holder"))
    parts.append(prism_x([(hy1 - wall, 0.0), (hy1, 0.0), (hy1, hh), (hy1 - wall, hh)], hx0 + wall, hx0 + hw - wall,
                         holder_k, "holder"))
    parts.append(prism_x([(hy0, 0.0), (hy0 + wall, 0.0), (hy0 + wall, hh * 0.42), (hy0, hh * 0.42)], hx0 + wall,
                         hx0 + hw - wall, holder_k, "holder"))
    parts.append(P._box(hx0 + hw / 2.0, (hy0 + hy1) / 2.0, 0.0, hw - 2 * wall, hy1 - hy0 - 2 * wall, 0.003, holder_k,
                        "holder"))
    nf = 5
    for k in range(nf):
        fx = hx0 + wall + 0.004 + k * (hw - 2 * wall - 0.008) / (nf - 1)
        top = hh * (0.92 + 0.06 * ((k * 7) % 3) / 2.0)
        parts.append(prism_x([(hy0 + wall + 0.004, 0.003), (hy1 - wall - 0.003, 0.003), (hy1 - wall - 0.003,
                              min(h - 0.002, top + 0.012)), (hy0 + wall + 0.01, min(h - 0.002, top * 0.95))],
                             fx - 0.0012, fx + 0.0012, FOLDER_KEYS[k % len(FOLDER_KEYS)], "folder"))
    # the desk clock (right back): a turned case on a foot, its face, ticks and hands
    cr = min(0.05, (w - hw - 0.03) / 4.0, h * 0.2)
    cx, cy_face = w / 2.0 - 0.010 - cr, d / 2.0 - 0.030
    cz = cr + 0.012
    parts.append(P._box(cx, cy_face + 0.012, 0.0, cr * 0.9, 0.028, 0.008, fin["trim"], "clock_foot"))
    parts.append(disc_y(cx, cy_face + 0.022, cz, [(0.0, 0.0), (cr, 0.0), (cr, 0.018), (cr * 0.94, 0.022),
                                                    (0.0, 0.022)], fin["trim"], "clock"))
    parts.append(disc_y(cx, cy_face + 0.0005, cz, [(0.0, 0.0), (cr * 0.86, 0.0), (cr * 0.86, 0.0012), (0.0, 0.0012)],
                        "ceramic", "clock_face"))
    for k in range(12):
        a = math.radians(90.0 - 30.0 * k)
        tl = 0.008 if k % 3 == 0 else 0.004
        rr = cr * 0.74
        tick = P._box(0.0, 0.0, -tl / 2.0, 0.0018, 0.0008, tl, "dark", "tick")
        tick = dict(tick, verts=[(cx + rr * math.cos(a) + vx * math.sin(a) + vz * math.cos(a),
                                  cy_face - 0.0012 + vy,
                                  cz + rr * math.sin(a) - vx * math.cos(a) + vz * math.sin(a))
                                 for vx, vy, vz in tick["verts"]])
        parts.append(tick)
    for ang, ln, wd in ((60.0, cr * 0.48, 0.0030), (-20.0, cr * 0.68, 0.0020)):
        a = math.radians(ang)
        hand = P._box(0.0, 0.0, 0.0, wd, 0.0008, ln, "dark", "hand")
        hand = dict(hand, verts=[(cx + vx * math.sin(a) + vz * math.cos(a), cy_face - 0.0016 + vy,
                                  cz - vx * math.cos(a) + vz * math.sin(a)) for vx, vy, vz in hand["verts"]])
        parts.append(hand)
    # the stapler (front middle): a base, the magazine arm on its hinge, a steel anvil
    sx = hx0 + hw + 0.012 + 0.07
    sy = -d / 2.0 + 0.032
    parts.append(block(0.07, 0.019, 0.012, 0.0, 0.012, 0.003, "dark", "stapler", cx=sx, cy=sy))
    parts.append(block(0.064, 0.015, 0.012, 0.016, 0.034, 0.005, fin["trim"] if fin["trim"] != "dark" else "steel",
                       "stapler_arm", cx=sx + 0.004, cy=sy))
    parts.append(P._box(sx + 0.058, sy, 0.012, 0.014, 0.024, 0.006, "dark", "hinge"))
    parts.append(P._box(sx - 0.05, sy, 0.012, 0.016, 0.012, 0.0012, "steel", "anvil"))
    # the succulent (front right) in a small pot
    pr = 0.034
    px, py = w / 2.0 - 0.010 - pr, -d / 2.0 + 0.010 + pr
    pot = SM._vessel([(pr * 0.75, 0.0), (pr * 0.92, 0.012), (pr, 0.058)], 0.004, 0.006, "ceramic", "pot",
                     c=(px, py, 0.0), n=24)
    parts.append(pot)
    parts.append(P._cylinder_z(px, py, 0.040, pr - 0.004, pr - 0.004, 0.012, "dark", "soil", n=NS))
    for k in range(9):                              # a rosette of fleshy leaves
        a = math.radians(k * 40.0 + 10.0)
        ring = 0.4 + 0.6 * (k % 3) / 2.0
        p0 = (px + 0.006 * math.cos(a), py + 0.006 * math.sin(a), 0.050)
        p1 = (px + pr * 0.85 * ring * math.cos(a), py + pr * 0.85 * ring * math.sin(a), 0.062 + 0.012 * (1 - ring))
        p2 = (px + pr * 1.05 * ring * math.cos(a), py + pr * 1.05 * ring * math.sin(a), 0.075 + 0.02 * (1 - ring))
        parts.append(SM.tube([p0, p1, p2], [0.0045, 0.0055, 0.0015], "green", "leaf", sides=6, squash=0.55))
    return parts


# --------------------------------------------------------------------------
# the dispatcher
# --------------------------------------------------------------------------

BUILDERS = {"kettle": kettle, "coffee_machine": coffee_machine, "toaster": toaster, "microwave": microwave,
            "knife_block": knife_block, "pepper_mills": pepper_mills, "desk_organiser": desk_organiser}


def contain(parts_: list[Part], w: float, d: float, h: float) -> list[Part]:
    """The parts kept inside the box ``w x d x h`` on z = 0: scaled down about the box's foot only when they overrun
    it (a box far from the product's own size), then moved in (never up off the worktop)."""
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts_)
    s = min(1.0, w / max(x1 - x0, 1e-9), d / max(y1 - y0, 1e-9), h / max(z1 - z0, 1e-9))
    x0, y0, z0, x1, y1, z1 = (v * s for v in (x0, y0, z0, x1, y1, z1))
    dx = max(0.0, -w / 2.0 - x0) - max(0.0, x1 - w / 2.0)
    dy = max(0.0, -d / 2.0 - y0) - max(0.0, y1 - d / 2.0)
    return [dict(p, verts=[(vx * s + dx, vy * s + dy, vz * s - z0) for vx, vy, vz in p["verts"]]) for p in parts_]


def parts(dtype: str, w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """The parts of an appliance or the desk organiser of box ``w x d x h`` (``item``: its ``appliance`` finish),
    inside the box (``contain``)."""
    return contain(BUILDERS[dtype](w, d, h, finish(None, item)), w, d, h)
