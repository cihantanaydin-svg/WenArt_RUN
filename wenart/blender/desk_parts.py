"""A desk's laptop and stationery (30 Oct 2026; user on real04 run 20261030-043021-full, two bedroom desks with bare tops:
"A laptop on this table could have even nice, also some stationary", "Same stationary and laptop here also"; lesson
UL164; user on run 20261030-112241-full: "laptop and stationary can be more detailed models they are too plain"; lesson
UL175).

What (pure: parts in the item's local frame, bottom on z = 0, the front towards -Y, the user's side):

- ``laptop_parts`` (the ``laptop`` decor item; ``parametric.work_set_parts`` builds it): an aluminium base with rounded
  corners (``LAPTOP["corner_m"]``), a dark keyboard well with single keycaps (a half-height function row, five rows of
  ``parametric.KEY_PITCH_M``, a space bar between the modifiers and an arrow cluster), speaker grilles beside it, a
  glass trackpad, a hinge barrel, the lid with rounded corners opened ``parametric.LAPTOP_OPEN_DEG``, a slim dark bezel
  with a camera dot, the screen, a desktop on it (``desktop_parts``) and a logo on the lid's back.
- ``desktop_parts``: what a switched-on screen shows (in the screen's own frame): a menu bar, a document window with
  lines of text, a picture window over it and a dock of app icons. The light parts take the key ``screen_ui``
  (``materials.screen_ui_material``: a faint light emission, never a lamp), the text and the icons darker keys; the
  layers stand off the screen by a tenth of a millimetre each. A monitor's screen shows it too.
- ``stationery_parts`` (the ``stationery`` decor item, one mesh): two closed notebooks lying stacked and a little turned
  (rounded cover boards over a cream page block, an elastic band and a ribbon marker on the lower one, a tan leather
  cover on the upper one with a phone and a pen lying on it), a pen pot (a ceramic tube with a wall, a floor and a
  rim) with pens (barrel, cap, clip, tip) and sharpened pencils (a hexagonal painted body, the bare wood cone, the
  graphite point) standing in it at slight angles.

Sizes are designer values of real products (assumed): A5 notebooks 21 x 14.8 cm, 1.4-1.8 cm thick; a pen pot 8 cm
across, 10 cm high, its wall 3.5 mm; pens 14 cm (9 mm across), pencils sharpened down to 15-16 cm (7 mm); a phone 14.7 x 7.1 x 0.78 cm.
Every part stays inside the item's box (``detail_parts.contain``). Material keys are the parametric ones
(``parametric.MATERIAL_KEYS``): ``dark`` (a black notebook, the keycaps, the bezel, the pen bodies), ``leather`` (the
upper notebook), ``terracotta`` (the elastic band, the ribbon, a pencil's paint), ``paper`` (the page blocks),
``ceramic`` (the pot), ``wood`` (the pencils' cones), ``steel`` (the aluminium shells, the clips and the tips),
``screen`` and ``screen_ui`` (the display).
"""
from __future__ import annotations

import math
from typing import Callable, Optional

Part = dict

STATIONERY_SIZE = (0.30, 0.22, 0.17)          # the item's box (w, d, h): the notebooks and the pot side by side
NOTEBOOK = (0.21, 0.148, 0.016)               # A5, lying: length, width, thickness
POT = (0.04, 0.10)                            # radius, height
POT_WALL_M = 0.0035
PEN_LEN, PENCIL_LEN = 0.14, 0.175
BOARD_M = 0.0018                              # a notebook's cover board
PHONE = (0.147, 0.071, 0.0078)                # length, width, thickness
# The laptop's details (designer values of a 14-15 inch laptop, assumed)
LAPTOP: dict[str, float] = {"corner_m": 0.009, "corner_seg": 4, "keys_share": 0.48, "pad_share": 0.28,
                            "keyboard_w_share": 0.86, "cap_share": 0.82, "cap_h": 0.0008, "well_h": 0.0003,
                            "grille_w": 0.010, "hinge_r_share": 0.40, "logo_r": 0.012, "camera_r": 0.0015}
DESKTOP_LAYER_M = 0.00004                     # each desktop layer stands this far off the one under it (0.04 mm)
UI_KEY = "screen_ui"
ICON_KEYS: tuple[str, ...] = ("terracotta", "steel", "wood", "ceramic", "dark", "terracotta", "wood")


def _cuboid(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float, key: str, role: str) -> Part:
    from wenart.blender.book_parts import _cuboid as cuboid

    return cuboid(x0, x1, y0, y1, z0, z1, key, role)


def rounded_rect(w: float, d: float, r: float, seg: int = 4) -> list[tuple[float, float]]:
    """A rectangle ``w x d`` centred on the origin with corners rounded by ``r`` (counter-clockwise, convex)."""
    r = max(0.0, min(r, w / 2.0 - 1e-6, d / 2.0 - 1e-6))
    out: list[tuple[float, float]] = []
    for cx, cy, a0 in ((w / 2.0 - r, -d / 2.0 + r, -90.0), (w / 2.0 - r, d / 2.0 - r, 0.0),
                       (-w / 2.0 + r, d / 2.0 - r, 90.0), (-w / 2.0 + r, -d / 2.0 + r, 180.0)):
        for k in range(seg + 1):
            a = math.radians(a0 + 90.0 * k / seg)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def prism_z(poly, z0: float, z1: float, key: str, role: str, dx: float = 0.0, dy: float = 0.0) -> Part:
    """A counter-clockwise polygon ``poly`` (``[(x, y)]``) moved by ``(dx, dy)`` and extruded from ``z0`` to ``z1``,
    wound outwards."""
    n = len(poly)
    verts = [(x + dx, y + dy, z0) for x, y in poly] + [(x + dx, y + dy, z1) for x, y in poly]
    faces = [list(range(n - 1, -1, -1)), list(range(n, 2 * n))]
    faces += [[k, (k + 1) % n, n + (k + 1) % n, n + k] for k in range(n)]
    return {"verts": verts, "faces": faces, "key": key, "role": role}


def _frustum(r0: float, r1: float, z0: float, z1: float, key: str, role: str, n: int = 8) -> Part:
    """A closed cone frustum about the Z axis: radius ``r0`` at ``z0``, ``r1`` at ``z1``."""
    ring = [(math.cos(2.0 * math.pi * k / n), math.sin(2.0 * math.pi * k / n)) for k in range(n)]
    verts = [(c * r0, s * r0, z0) for c, s in ring] + [(c * r1, s * r1, z1) for c, s in ring]
    faces = [[k, (k + 1) % n, n + (k + 1) % n, n + k] for k in range(n)]
    faces += [list(range(n, 2 * n)), list(range(n - 1, -1, -1))]
    return {"verts": verts, "faces": faces, "key": key, "role": role}


def _tube(r_out: float, r_in: float, z0: float, z1: float, key: str, role: str, n: int = 24) -> Part:
    """A closed tube about the Z axis (an outer and an inner wall joined by the top and the bottom rings)."""
    ring = [(math.cos(2.0 * math.pi * k / n), math.sin(2.0 * math.pi * k / n)) for k in range(n)]
    verts = ([(c * r_out, s * r_out, z0) for c, s in ring] + [(c * r_out, s * r_out, z1) for c, s in ring]
             + [(c * r_in, s * r_in, z0) for c, s in ring] + [(c * r_in, s * r_in, z1) for c, s in ring])
    ob, ot, ib, it = 0, n, 2 * n, 3 * n
    faces = []
    for k in range(n):
        j = (k + 1) % n
        faces.append([ob + k, ob + j, ot + j, ot + k])            # the outer wall, outwards
        faces.append([ib + j, ib + k, it + k, it + j])            # the inner wall, towards the axis
        faces.append([ot + k, ot + j, it + j, it + k])            # the top ring, up
        faces.append([ob + j, ob + k, ib + k, ib + j])            # the bottom ring, down
    return {"verts": verts, "faces": faces, "key": key, "role": role}


def _apply(parts: list[Part], fn: Callable) -> list[Part]:
    for p in parts:
        p["verts"] = [fn(v) for v in p["verts"]]
    return parts


def _turn(dx: float, dy: float, dz: float, turn_deg: float = 0.0, tilt_deg: float = 0.0,
          tilt_dir_deg: float = 0.0) -> Callable:
    """A proper rotation (a tilt of ``tilt_deg`` from +Z towards ``tilt_dir_deg``, then a turn ``turn_deg`` about Z)
    and a move: the parts keep their outward winding."""
    t, d, a = math.radians(tilt_deg), math.radians(tilt_dir_deg), math.radians(turn_deg)
    ct, st, cd, sd, ca, sa = math.cos(t), math.sin(t), math.cos(d), math.sin(d), math.cos(a), math.sin(a)

    def fn(v):
        x, y, z = v
        x, y = x * cd + y * sd, -x * sd + y * cd             # into the tilt's frame
        x, z = x * ct + z * st, -x * st + z * ct              # tilt about its Y
        x, y = x * cd - y * sd, x * sd + y * cd               # back
        x, y = x * ca - y * sa, x * sa + y * ca
        return (x + dx, y + dy, z + dz)
    return fn


# ------------------------------------------------------------------------------------------------- the screen
def desktop_parts(sw: float, sh: float, t_front: float) -> list[Part]:
    """What a switched-on screen ``sw`` wide and ``sh`` high shows, in the screen's frame (x across from the middle,
    y = t through the screen, positive behind it, z = s up from its lower edge; the screen's face at ``t_front``): a
    menu bar, a document window with text lines, a picture window over it and a dock with icons, each layer
    ``DESKTOP_LAYER_M`` nearer the viewer than the one under it."""
    parts: list[Part] = []

    def rect(u0: float, u1: float, v0: float, v1: float, layer: int, key: str) -> None:
        t1 = t_front - DESKTOP_LAYER_M * (layer - 1)
        parts.append(_cuboid(-sw / 2.0 + sw * u0, -sw / 2.0 + sw * u1, t1 - DESKTOP_LAYER_M, t1, sh * v0, sh * v1,
                             key, "screen_ui"))

    rect(0.0, 1.0, 0.962, 1.0, 1, UI_KEY)                     # the menu bar
    rect(0.05, 0.60, 0.20, 0.86, 1, UI_KEY)                   # a document window
    rect(0.05, 0.60, 0.815, 0.86, 2, "steel")                 # its title bar
    for k, length in enumerate((0.40, 0.46, 0.32, 0.44, 0.38, 0.22, 0.42)):
        v = 0.75 - 0.07 * k
        rect(0.09, 0.09 + length, v, v + 0.018, 2, "dark")    # its lines of text
    rect(0.52, 0.93, 0.34, 0.76, 3, UI_KEY)                   # a picture window over it
    rect(0.55, 0.90, 0.40, 0.70, 4, "terracotta")             # its picture: a warm photo ...
    rect(0.55, 0.90, 0.40, 0.50, 5, "wood")                   # ... with its lower band
    rect(0.30, 0.70, 0.025, 0.105, 1, UI_KEY)                 # the dock
    n = len(ICON_KEYS)
    for k, key in enumerate(ICON_KEYS):
        u = 0.32 + (0.36 / n) * (k + 0.15)
        rect(u, u + 0.36 / n * 0.7, 0.04, 0.09, 2, key)       # its app icons
    return parts


# ------------------------------------------------------------------------------------------------- the laptop
def laptop_parts(w: float, d: float, h: float) -> list[Part]:
    """The open laptop in its box ``w x d x h`` (module docstring; the base the largest that fits the box, as
    ``parametric.laptop_box`` sizes it)."""
    from wenart.blender import detail_parts as DP
    from wenart.blender import parametric as P

    lean = math.radians(P.LAPTOP_OPEN_DEG - 90.0)
    su, cu = math.sin(lean), math.cos(lean)
    bt = min(P.LAPTOP_BASE_T, h * 0.08)
    bd = max(0.02, min((d - P.LAPTOP_LID_T * cu) / (1.0 + su), (h - bt - P.LAPTOP_FACE_T * su) / cu))
    depth = bd * (1.0 + su) + P.LAPTOP_LID_T * cu
    y0 = -depth / 2.0                             # the front edge of the base, the box centred on the item
    hinge = (y0 + bd, bt)
    seg = int(LAPTOP["corner_seg"])
    corner = min(LAPTOP["corner_m"], w * 0.05, bd * 0.08)
    parts = [prism_z(rounded_rect(w, bd, corner, seg), 0.0, bt, "steel", "base", dy=y0 + bd / 2.0)]
    # the keyboard well and its keys: a half-height function row, five rows, the space bar and the arrow cluster
    kw, keys_d = w * LAPTOP["keyboard_w_share"], bd * LAPTOP["keys_share"]
    k_back = hinge[0] - bd * 0.05
    k_front = k_back - keys_d
    parts.append(_cuboid(-kw / 2.0, kw / 2.0, k_front, k_back, bt, bt + LAPTOP["well_h"], "dark", "keys"))
    pitch_x = kw / max(1, int(kw / P.KEY_PITCH_M))
    cols = int(round(kw / pitch_x))
    pitch_y = keys_d / 5.55
    cap = LAPTOP["cap_share"]
    zc0, zc1 = bt + LAPTOP["well_h"], bt + LAPTOP["well_h"] + LAPTOP["cap_h"]
    rows = [(k_back - pitch_y * 0.55, k_back, "fn")] + [
        (k_back - pitch_y * (0.55 + r + 1), k_back - pitch_y * (0.55 + r), "row" if r < 4 else "front")
        for r in range(5)]
    for ya, yb, kind in rows:
        gy = (yb - ya) * (1.0 - cap) / 2.0
        if kind == "front" and cols >= 10:
            # the modifiers, the space bar (five keys wide), the arrows (half-height pairs in the middle)
            x = -kw / 2.0
            for k in range(cols):
                if 3 <= k < 3 + 5:
                    if k == 3:
                        x0, x1 = x + pitch_x * 3 + pitch_x * (1.0 - cap) / 2.0, x + pitch_x * 8 - pitch_x * (1.0 - cap) / 2.0
                        parts.append(_cuboid(x0, x1, ya + gy, yb - gy, zc0, zc1, "dark", "space_bar"))
                    continue
                gx = pitch_x * (1.0 - cap) / 2.0
                xa, xb = x + pitch_x * k + gx, x + pitch_x * (k + 1) - gx
                if k == cols - 2:                                     # the up and down arrows share a key's place
                    mid = (ya + yb) / 2.0
                    parts.append(_cuboid(xa, xb, ya + gy, mid - gy / 2.0, zc0, zc1, "dark", "key"))
                    parts.append(_cuboid(xa, xb, mid + gy / 2.0, yb - gy, zc0, zc1, "dark", "key"))
                else:
                    parts.append(_cuboid(xa, xb, ya + gy, yb - gy, zc0, zc1, "dark", "key"))
            continue
        for k in range(cols):
            gx = pitch_x * (1.0 - cap) / 2.0
            x0 = -kw / 2.0 + pitch_x * k
            parts.append(_cuboid(x0 + gx, x0 + pitch_x - gx, ya + gy, yb - gy, zc0, zc1, "dark", "key"))
    # the speaker grilles beside the keyboard and the glass trackpad under it
    gw = min(LAPTOP["grille_w"], (w - kw) / 2.0 * 0.6)
    gx = (kw / 2.0 + w / 2.0) / 2.0
    for s in (-1.0, 1.0):
        parts.append(_cuboid(s * gx - gw / 2.0, s * gx + gw / 2.0, k_front, k_back, bt, bt + 0.0002, "dark",
                             "grille"))
    pad_d = bd * LAPTOP["pad_share"]
    p_back = k_front - bd * 0.05
    parts.append(prism_z(rounded_rect(w * 0.36, pad_d, 0.004, 3), bt, bt + 0.0004, "dark", "trackpad",
                         dy=p_back - pad_d / 2.0))
    # the hinge barrel along the base's back edge
    hr = bt * LAPTOP["hinge_r_share"]
    parts.append(DP._rod((-w * 0.38, hinge[0] - hr * 0.6, bt - hr * 0.2), (w * 0.38, hinge[0] - hr * 0.6,
                                                                         bt - hr * 0.2), hr, "dark", "hinge", n=10))

    def lid(v):
        x, t, s = v                               # across, through the lid (behind the screen > 0), along it
        return (x, hinge[0] + t * cu + s * su, hinge[1] - t * su + s * cu)

    face = P.LAPTOP_FACE_T
    sb, tb, bb = (min(v, w * 0.08, bd * 0.12) for v in P.LAPTOP_BEZEL_M)
    lid_parts = [DP._prism_y([(x, s + bd / 2.0) for x, s in rounded_rect(w, bd, corner, seg)], 0.0, P.LAPTOP_LID_T,
                             "steel", "lid"),
                 DP._prism_y([(x, s + bd / 2.0) for x, s in rounded_rect(w - 0.002, bd - 0.001, corner, seg)],
                             -face * 0.6, 0.0, "dark", "bezel"),
                 _cuboid(-(w - 2.0 * sb) / 2.0, (w - 2.0 * sb) / 2.0, -face * 0.85, -face * 0.6, bb, bd - tb,
                         "screen", "screen")]
    cam = LAPTOP["camera_r"]
    lid_parts.append(_cuboid(-cam, cam, -face * 0.7, -face * 0.6 + 1e-5, bd - tb / 2.0 - cam, bd - tb / 2.0 + cam,
                             "steel", "camera"))
    ui = desktop_parts(w - 2.0 * sb, bd - bb - tb, -face * 0.85)
    lid_parts += _apply(ui, lambda v: (v[0], v[1], v[2] + bb))
    lr = min(LAPTOP["logo_r"], w * 0.05)
    logo = DP._prism_y([(lr * math.cos(2.0 * math.pi * k / 16), bd * 0.55 + lr * math.sin(2.0 * math.pi * k / 16))
                        for k in range(16)], P.LAPTOP_LID_T, P.LAPTOP_LID_T + 0.0002, "dark", "logo")
    lid_parts.append(logo)
    return parts + _apply(lid_parts, lid)


# ------------------------------------------------------------------------------------------------- the stationery
def _notebook(cx: float, cy: float, z0: float, L: float, W: float, T: float, turn_deg: float, cover: str,
              band: Optional[str], ribbon: Optional[str]) -> list[Part]:
    """A closed notebook lying flat: two cover boards with rounded corners over a page block inset on three sides, its
    spine on -X; an elastic band across it near the fore-edge (``band``: its key) and a ribbon marker hanging out of
    its foot (``ribbon``); turned ``turn_deg`` about its centre."""
    b = min(BOARD_M, T * 0.15)
    o = 0.003
    r = min(0.008, W * 0.06)
    board = rounded_rect(L, W, r, 3)
    parts = [prism_z(board, 0.0, b, cover, "book"), prism_z(board, T - b, T, cover, "book"),
             _cuboid(-L / 2.0, -L / 2.0 + 0.008, -W / 2.0 + 0.0005, W / 2.0 - 0.0005, b, T - b, cover, "book"),
             prism_z(rounded_rect(L - o, W - 2.0 * o, max(0.0, r - o), 3), b, T - b, "paper", "pages", dx=o / 2.0)]
    if band:
        parts.append(_cuboid(L / 2.0 - 0.033, L / 2.0 - 0.027, -W / 2.0 - 0.0006, W / 2.0 + 0.0006, 0.0, T + 0.0006,
                             band, "strap"))
    if ribbon:
        parts.append(_cuboid(-0.012, -0.006, -W / 2.0 - 0.025, -W / 2.0 + 0.004, b * 0.5, b * 0.5 + 0.0004, ribbon,
                             "strap"))
    return _apply(parts, _turn(cx, cy, z0, turn_deg))


def _pen(length: float) -> list[Part]:
    """A pen standing on its tip end (z = 0) along +Z: a barrel, a steel cone tip at the bottom, a cap at the top with
    a clip."""
    r = 0.0045
    tip = length * 0.08
    parts = [_frustum(0.0008, r * 0.8, 0.0, tip, "steel", "rod", n=8),
             _frustum(r, r, tip, length * 0.62, "dark", "rod", n=10),
             _frustum(r * 1.12, r * 1.12, length * 0.62, length - 0.003, "dark", "rod", n=10),
             _frustum(r * 1.12, r * 0.7, length - 0.003, length, "dark", "rod", n=10),
             _cuboid(r * 1.05, r * 1.05 + 0.0012, -0.0015, 0.0015, length * 0.68, length - 0.006, "steel", "clip")]
    return parts


def _pencil(length: float, paint: str) -> list[Part]:
    """A sharpened pencil standing on its end (z = 0) along +Z: a hexagonal painted body, the bare wood cone, the
    graphite point."""
    r = 0.0035
    cone = 0.018
    return [_frustum(r, r, 0.0, length - cone, paint, "rod", n=6),
            _frustum(r, r * 0.22, length - cone, length - 0.003, "wood", "rod", n=6),
            _frustum(r * 0.22, 0.0003, length - 0.003, length, "dark", "rod", n=6)]


def _phone(cx: float, cy: float, z0: float, turn_deg: float) -> list[Part]:
    """A phone lying face up: a rounded aluminium frame and its dark glass face."""
    L, W, T = PHONE
    r = 0.009
    parts = [prism_z(rounded_rect(L, W, r, 4), 0.0, T - 0.0006, "steel", "phone"),
             prism_z(rounded_rect(L - 0.0012, W - 0.0012, r - 0.0006, 4), T - 0.0006, T, "dark", "phone")]
    return _apply(parts, _turn(cx, cy, z0, turn_deg))


def stationery_parts(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """The stationery set in the box ``w x d x h`` (module docstring): the notebooks on the left of the box with the
    phone and a pen on them, the pen pot on its right."""
    from wenart.blender.detail_parts import contain

    L, W, T = NOTEBOOK
    nx = -w / 2.0 + W / 2.0 + 0.01               # the notebooks lie turned a quarter: their width along X
    parts = _notebook(nx, 0.0, 0.0, L, W, T, 92.0, "dark", band="terracotta", ribbon="terracotta")
    t2 = T * 0.85
    parts += _notebook(nx + 0.006, 0.003, T, L * 0.96, W * 0.96, t2, 84.0, "leather", band=None, ribbon=None)
    top = T + t2
    parts += _phone(nx + 0.026, 0.004, top, 91.0)                                    # lying on the top one ...
    parts += _apply(_pen(PEN_LEN), _turn(nx - 0.045, -PEN_LEN / 2.0, top + 0.005, 0.0, 90.0, 92.0))   # ... by a pen
    r, ph = POT
    px, py = w / 2.0 - r - 0.012, 0.035
    pot = [_tube(r, r - POT_WALL_M, 0.0, ph, "ceramic", "pot", n=32),
           _frustum(r - POT_WALL_M, r - POT_WALL_M, 0.0, 0.008, "ceramic", "pot", n=32),        # its floor
           _tube(r + 0.001, r - POT_WALL_M - 0.0005, ph - 0.004, ph, "ceramic", "pot", n=32)]   # a rolled rim
    parts += _apply(pot, _turn(px, py, 0.0))
    sticks = ((_pen(PEN_LEN), 8.0, 30.0), (_pencil(PENCIL_LEN * 0.9, "terracotta"), 11.0, 150.0),
              (_pen(PEN_LEN * 1.02), 6.0, 260.0), (_pencil(PENCIL_LEN * 0.86, "dark"), 13.0, 200.0),
              (_pen(PEN_LEN * 0.97), 9.0, 330.0))
    for stick, tilt, ang in sticks:
        a = math.radians(ang)
        sx, sy = px + math.cos(a) * r * 0.45, py + math.sin(a) * r * 0.45
        parts += _apply(stick, _turn(sx, sy, 0.008, 0.0, tilt, ang))
    return contain(parts, w, d, h)
