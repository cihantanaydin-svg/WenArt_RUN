"""The parametric products of the P16 living-dining room (30 Oct 2026; user, sending photo P16: "salon inspiration";
lesson UL153; docs/reference_details_20261029.md rows R39-R49).

What (pure: parts in the item's or the piece's local frame, bottom on z = 0, the front towards -Y, the back on the
wall at +Y; ``detail_parts`` dispatches to these; one item is one mesh, its boards, LEDs and objects together, so the
build makes one object per detail: lesson UL111):

- ``tv_niche_parts`` (a ``wall_niche`` with ``niche.style: tv_side``, R45): a tall narrow built-out niche beside the
  TV: a frame in the wall's paint, a black lining (sides, top, back), a closed base with a flat push-to-open front,
  black boards with an LED strip under the front edge of each board above, books, vases and a bowl on the boards.
- ``panel_wall_parts`` (``panel_wall``, R39): full-height handle-less flat panels (push-to-open fronts with 4 mm
  shadow gaps, a recessed plinth) on a carcass, an inset black-lined niche across two modules with an LED strip under
  its top and books, a vase and a bowl on its floor.
- ``wall_discs_parts`` (``wall_discs``, R44): two black round wall discs (a large one higher, a small one lower,
  offset).
- ``floating_console`` (a ``tv_unit``'s ``form: floating``, R45): a low wall-hung wood console under the TV (a box
  ``CONSOLE_BOX_M`` high hung under the unit's top, nothing to the floor), flat drawer fronts and a black fluted strip
  across the middle third of its front, a hidden cleat at its back.
- ``drum_table`` (a ``table_coffee``'s ``form: drum``, R48): a round travertine drum (the diameter the footprint's
  smaller side) on a recessed plinth, a shadow groove under its top.
- ``linear_pendant_parts`` (a ``pendant_light`` with ``fixture: linear_pendant``, R42): a slim black bar with an LED
  diffuser under it on two thin cables from two small ceiling canopies.
- ``track_pendants_parts`` (a ``pendant_light`` with ``fixture: track_pendants``, R42): a black surface ceiling track
  over the table, black mini cylinder pendants hanging from it on cords (``track.offsets``), a spot at each end.
- ``centrepiece_parts`` (a ``vase`` with ``set: centrepiece``, R43): a clear glass vase with dried pampas grass, two
  concrete candle holders of two heights with their candles, a low ceramic bowl.
- ``ring_rug_parts`` (a ``rug`` with ``shape: round`` and ``pattern: rings``, R48): a round rug with concentric
  stripes.

Sizes are designer values of real products (assumed). Every part stays inside its box (``contain``).
"""
from __future__ import annotations

from typing import Optional

from wenart.blender.parametric import _box, _cylinder_y, _cylinder_z, _frustum_z, _superellipsoid

Part = dict

TAG = "30 Oct 2026, photo P16, user: \"salon inspiration\" (UL153)"
LINING_M = 0.008                 # a niche's black lining
FRAME_M = 0.03                   # a niche's outer frame in the wall's paint
SHADOW_GAP_M = 0.004             # the gap between two handle-less fronts
PLINTH_M = 0.07                  # a panel wall's recessed plinth
PLINTH_SET_BACK_M = 0.05
FRONT_T_M = 0.019
CONSOLE_BOX_M = 0.28             # a floating console's box under its top (P16: a low console, its underside free)
CONSOLE_TOP_T_M = 0.022
FLUTE_PITCH_M = 0.025            # the black fluted strip's ribs
DRUM_PLINTH_SHARE = 0.86         # a drum table's plinth radius as a share of its radius
PENDANT_SHADE_R_M = 0.055        # a mini pendant's black cylinder shade (11 cm)
PENDANT_SHADE_H_M = 0.16
TRACK_RAIL_M = 0.035             # a surface track's square section
BAR_H_M = 0.05                   # a linear pendant's bar
CORD_R_M = 0.003
CANOPY_R_M = 0.04
CANOPY_H_M = 0.02


def contain(parts: list[Part], w: float, d: float, h: float, floor: bool = True) -> list[Part]:
    from wenart.blender import detail_parts as DP

    return DP.contain(parts, w, d, h, floor)


def _objects_on_boards(floors: list[float], ceilings: list[float], x_l: float, x_r: float, y: float, dd: float,
                       seed: int = 0) -> list[Part]:
    """Styled objects on boards (the H1 niche's rule, ``detail_parts.niche_parts``): books standing, a vase, books
    lying with a bowl and a small sculpture, a bud vase with pampas grass, by turns."""
    from wenart.blender import detail_parts as DP

    parts: list[Part] = []
    inner = x_r - x_l
    for k, (z, top) in enumerate(zip(floors, ceilings)):
        room = top - z - 0.03
        if room < 0.06 or inner < 0.12:
            continue
        g = (k + seed) % 3
        if g == 0:
            parts += DP.books_upright(x_l, x_l + inner * 0.55, y, z, dd, min(0.26, room), seed=k + seed)
            r = min(0.05, inner * 0.12, dd / 2.0)
            parts += DP.small_vase(x_r - r - 0.02, y, z, r, min(0.24, room), "accent_ceramic")
        elif g == 1:
            parts += DP.books_lying(x_l + inner * 0.3, y, z, min(0.22, inner * 0.45), dd, min(0.1, room * 0.5))
            sr = min(0.04, inner * 0.08, dd / 2.0)
            parts.append(_superellipsoid(x_r - sr - 0.02, y, z, sr * 2.0, sr * 2.0, min(0.18, room * 0.8), 0.8, 0.9,
                                         "dark", "object", n_eta=8, n_om=16))
        else:
            vr = min(0.03, dd / 3.0, inner / 8.0)
            vh = min(0.14, room * 0.45)
            parts += DP.small_vase(x_l + vr + 0.03, y, z, vr, vh, "accent_ceramic")
            parts += DP.pampas(x_l + vr + 0.03, y, z + vh * 0.9, min(top - 0.03, z + room), min(0.06, inner * 0.1),
                               n=5, seed=k + seed)
            br = min(0.07, inner * 0.18, dd / 2.0)
            parts.append(_frustum_z(x_r - br - 0.02, y, z, br * 0.55, br * 0.55, br, br, min(0.05, room * 0.3),
                                    "ceramic", "object", n=24))
    return parts


# --------------------------------------------------------------------------
# decor
# --------------------------------------------------------------------------

def tv_niche_parts(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """R45: the tall narrow black-lined lit niche beside the TV (module docstring), in its box (back on +Y)."""
    spec = (item or {}).get("niche") if isinstance((item or {}).get("niche"), dict) else {}
    t = min(FRAME_M, w / 8.0, h / 10.0)
    base_h = min(float(spec.get("base_m") or 0.42), h * 0.25)
    inner = w - 2.0 * t
    lin = LINING_M
    parts = [_box(-w / 2.0 + t / 2.0, 0.0, 0.0, t, d, h, "painted", "side"),
             _box(w / 2.0 - t / 2.0, 0.0, 0.0, t, d, h, "painted", "side"),
             _box(0.0, 0.0, h - t, inner - 0.001, d, t, "painted", "top"),
             # the base: a closed box with one flat push-to-open front (a groove under its top edge)
             _box(0.0, 0.006, 0.0, inner - 0.001, d - 0.012, base_h - 0.004, "painted", "body"),
             _box(0.0, -d / 2.0 + 0.009, 0.05, inner - 0.006, 0.018, base_h - 0.054, "front", "front"),
             # the black lining of the open part: its back, its sides, its top
             _box(0.0, d / 2.0 - 0.006 - lin / 2.0, base_h, inner - 0.002, lin, h - t - base_h, "dark", "lining"),
             _box(-inner / 2.0 + lin / 2.0 + 0.0005, 0.0, base_h, lin, d - 0.014, h - t - base_h, "dark", "lining"),
             _box(inner / 2.0 - lin / 2.0 - 0.0005, 0.0, base_h, lin, d - 0.014, h - t - base_h, "dark", "lining"),
             _box(0.0, 0.0, h - t - lin, inner - 2.0 * lin - 0.002, d - 0.014, lin, "dark", "lining")]
    open_w = inner - 2.0 * lin - 0.004
    board = min(0.022, (h - base_h) / 25.0)
    parts.append(_box(0.0, -0.002, base_h, open_w, d - 0.02, board, "dark", "shelf"))
    n = max(2, min(6, int(spec.get("shelves") or int((h - base_h - t) / 0.40))))
    usable = h - t - lin - base_h - board
    pitch = usable / n
    floors = [base_h + board]
    for k in range(1, n):
        z = base_h + k * pitch
        parts.append(_box(0.0, -0.004, z, open_w, d - 0.026, board, "dark", "shelf"))
        floors.append(z + board)
    ceilings = [f + pitch - board for f in floors]
    ceilings[-1] = h - t - lin
    led_d = min(0.012, d / 10.0)
    for top in ceilings:                                      # an LED strip under the front edge of every board above
        parts.append(_box(0.0, -d / 2.0 + 0.03, top - 0.008, open_w - 0.03, led_d, 0.006, "led", "led"))
    if spec.get("objects", True):
        parts += _objects_on_boards(floors, ceilings, -open_w / 2.0 + 0.02, open_w / 2.0 - 0.02, 0.01,
                                    min(0.16, d - 0.08), seed=int(spec.get("seed") or 0))
    return contain(parts, w, d, h)


def panel_layout(w: float, module_m: float = 0.55) -> tuple[int, float]:
    """``(modules, module width)`` of a panel wall ``w`` wide: whole fronts of about ``module_m`` (pure)."""
    n = max(2, int(round(w / module_m)))
    return n, w / n


def panel_wall_parts(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """R39: full-height handle-less flat panels with an inset black-lined lit niche (module docstring)."""
    spec = (item or {}).get("panel") if isinstance((item or {}).get("panel"), dict) else {}
    n, mw = panel_layout(w, float(spec.get("module_m") or 0.55))
    carcass_d = d - FRONT_T_M
    y_front = -d / 2.0 + FRONT_T_M / 2.0
    yc_body = FRONT_T_M / 2.0
    parts = [_box(0.0, yc_body + PLINTH_SET_BACK_M / 2.0, 0.0, w - 0.002, carcass_d - PLINTH_SET_BACK_M, PLINTH_M,
                  "dark", "plinth")]
    niche = spec.get("niche", True)
    k0 = max(0, n // 2 - 1) if niche and n >= 3 else (0 if niche else -1)
    k1 = k0 + (2 if n >= 3 else 1) - 1 if niche else -2
    z_n0 = float(spec.get("niche_bottom_m") or 0.95)
    z_n1 = min(h - 0.4, z_n0 + float(spec.get("niche_h_m") or 0.50))
    if z_n1 - z_n0 < 0.25:
        k0, k1 = -1, -2                                       # too low a wall: no niche
    lin = LINING_M
    depth = carcass_d - 0.04                                  # the niche is cut into the carcass this deep
    if k1 >= k0 >= 0:
        # the carcass around the niche: under it, over it, beside it and behind it (never across its opening)
        x0 = -w / 2.0 + mw * k0 + SHADOW_GAP_M / 2.0
        x1 = -w / 2.0 + mw * (k1 + 1) - SHADOW_GAP_M / 2.0
        lo, hi = z_n0 - lin, z_n1 + lin
        parts += [_box(0.0, yc_body, PLINTH_M, w, carcass_d, lo - PLINTH_M, "painted", "body"),
                  _box(0.0, yc_body, hi, w, carcass_d, h - hi, "painted", "body"),
                  _box((-w / 2.0 + x0) / 2.0, yc_body, lo, x0 + w / 2.0, carcass_d, hi - lo, "painted", "body"),
                  _box((x1 + w / 2.0) / 2.0, yc_body, lo, w / 2.0 - x1, carcass_d, hi - lo, "painted", "body"),
                  _box((x0 + x1) / 2.0, (-d / 2.0 + depth + d / 2.0) / 2.0, lo, x1 - x0, d / 2.0 - (-d / 2.0 + depth),
                       hi - lo, "painted", "body")]
    else:
        parts.append(_box(0.0, yc_body, PLINTH_M, w, carcass_d, h - PLINTH_M, "painted", "body"))
    top_h = h - PLINTH_M
    for k in range(n):
        x = -w / 2.0 + mw * (k + 0.5)
        fw = mw - SHADOW_GAP_M
        if k0 <= k <= k1:
            parts.append(_box(x, y_front, PLINTH_M, fw, FRONT_T_M, z_n0 - PLINTH_M - SHADOW_GAP_M, "front", "front"))
            parts.append(_box(x, y_front, z_n1 + SHADOW_GAP_M, fw, FRONT_T_M, h - z_n1 - SHADOW_GAP_M - 0.002,
                              "front", "front"))
        else:
            parts.append(_box(x, y_front, PLINTH_M, fw, FRONT_T_M, top_h - 0.002, "front", "front"))
    if k1 >= k0 >= 0:
        cx, nw = (x0 + x1) / 2.0, x1 - x0
        yc = -d / 2.0 + depth / 2.0 - 0.001
        parts += [_box(cx, yc, z_n0 - lin, nw, depth, lin, "dark", "lining"),             # floor
                  _box(cx, yc, z_n1, nw, depth, lin, "dark", "lining"),                   # top
                  _box(cx, -d / 2.0 + depth - lin / 2.0, z_n0, nw, lin, z_n1 - z_n0, "dark", "lining"),   # back
                  _box(x0 + lin / 2.0, yc, z_n0, lin, depth, z_n1 - z_n0, "dark", "lining"),
                  _box(x1 - lin / 2.0, yc, z_n0, lin, depth, z_n1 - z_n0, "dark", "lining"),
                  _box(cx, -d / 2.0 + 0.03, z_n1 - 0.008, nw - 0.04, min(0.012, depth / 10.0), 0.006, "led", "led")]
        parts += _objects_on_boards([z_n0], [z_n1], x0 + 0.04, x1 - 0.04, -d / 2.0 + depth / 2.0,
                                    min(0.16, depth - 0.06), seed=int(spec.get("seed") or 0))
    return contain(parts, w, d, h)


def wall_discs_parts(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """R44: two black round wall discs, a large one up to the left, a small one down to the right (module docstring)."""
    big = min(h, w * 0.6)
    small = big * 0.62
    t = min(d - 0.006, 0.03)
    y0 = d / 2.0 - t - 0.005                                  # on a hidden bracket 5 mm off the wall
    parts = [_cylinder_y(-w / 2.0 + big / 2.0, y0, h - big / 2.0, big / 2.0, big / 2.0, t, "dark", "disc", n=48),
             _cylinder_y(w / 2.0 - small / 2.0, y0, small / 2.0, small / 2.0, small / 2.0, t, "dark", "disc", n=40)]
    return contain(parts, w, d, h)


def linear_pendant_parts(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """R42: a slim black linear pendant (module docstring): its bar at the bottom, the cables up to the ceiling."""
    bar_d = min(d, 0.06)
    bar_h = min(BAR_H_M, h * 0.3)
    parts = [_box(0.0, 0.0, 0.006, w, bar_d, bar_h - 0.006, "dark", "bar"),
             _box(0.0, 0.0, 0.0, w - 0.03, bar_d * 0.6, 0.006, "bulb", "bulb")]
    for sx in (-0.4, 0.4):
        x = sx * w
        parts.append(_cylinder_z(x, 0.0, bar_h, CORD_R_M, CORD_R_M, h - bar_h - CANOPY_H_M, "dark", "cord", n=6))
        parts.append(_cylinder_z(x, 0.0, h - CANOPY_H_M, min(CANOPY_R_M, d / 2.0), min(CANOPY_R_M, d / 2.0),
                                 CANOPY_H_M, "dark", "canopy", n=16))
    return contain(parts, w, d, h)


def track_offsets(w: float, item: Optional[dict] = None) -> list[float]:
    """The mini pendants' places along the track (local x; ``track.offsets`` of the item, else ``track.pendants``
    spread evenly 0.3 m in from the ends)."""
    spec = (item or {}).get("track") if isinstance((item or {}).get("track"), dict) else {}
    offs = [float(v) for v in spec.get("offsets") or [] if isinstance(v, (int, float))]
    if offs:
        return [max(-w / 2.0 + 0.1, min(w / 2.0 - 0.1, o)) for o in offs]
    n = max(1, int(spec.get("pendants") or 3))
    if n == 1:
        return [0.0]
    span = max(0.0, w - 0.6)
    return [-span / 2.0 + span * k / (n - 1) for k in range(n)]


def track_pendants_parts(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """R42: a black surface track on the ceiling with black mini pendants on cords and a spot at each end (module
    docstring)."""
    rail = min(TRACK_RAIL_M, h / 4.0, d)
    sr = min(PENDANT_SHADE_R_M, d / 2.0)
    sh = min(PENDANT_SHADE_H_M, h * 0.4)
    parts = [_box(0.0, 0.0, h - rail, w, min(d, rail), rail, "dark", "rail")]
    for x in track_offsets(w, item):
        parts.append(_cylinder_z(x, 0.0, sh, CORD_R_M, CORD_R_M, h - rail - sh, "dark", "cord", n=6))
        parts.append(_cylinder_z(x, 0.0, 0.004, sr, sr, sh - 0.004, "dark", "shade", n=24))
        parts.append(_cylinder_z(x, 0.0, 0.0, sr * 0.8, sr * 0.8, 0.004, "bulb", "bulb", n=20))
    spot_r = min(0.03, d / 2.0)
    for sx in (-1.0, 1.0):
        x = sx * (w / 2.0 - 0.06)
        parts.append(_cylinder_z(x, 0.0, h - rail - 0.13, spot_r, spot_r, 0.13, "dark", "head", n=16))
        parts.append(_cylinder_z(x, 0.0, h - rail - 0.134, spot_r * 0.7, spot_r * 0.7, 0.004, "bulb", "lens", n=16))
    return contain(parts, w, d, h)


def centrepiece_parts(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """R43: the dining table's centrepiece (module docstring): a glass vase with pampas at one end, two concrete
    candle holders in the middle, a low bowl at the other end."""
    from wenart.blender import detail_parts as DP

    vr = min(0.055, d / 2.0 - 0.005, w / 8.0)
    vh = min(0.26, h * 0.45)
    spread = max(0.02, min(0.08, d / 2.0 - 0.04, w / 6.0))
    xv = -w / 2.0 + spread + 0.04
    parts = [_cylinder_z(xv, 0.0, 0.0, vr, vr, vh, "glass", "object", n=24)]
    parts += DP.pampas(xv, 0.0, vh * 0.85, h, spread, n=7, seed=3)
    for k, (dx, ch) in enumerate(((-0.02, 0.12), (0.085, 0.08))):
        r = min(0.04, d / 2.0 - 0.01)
        x = -0.02 + dx
        parts.append(_cylinder_z(x, (-1) ** k * min(0.02, d / 6.0), 0.0, r, r, min(ch, h * 0.3), "terrazzo",
                                 "object", n=24))
        parts.append(_cylinder_z(x, (-1) ** k * min(0.02, d / 6.0), min(ch, h * 0.3), r * 0.55, r * 0.55,
                                 min(0.07, h * 0.15), "ceramic", "candle", n=16))
    br = min(0.11, d / 2.0 - 0.005, w / 5.0)
    xb = w / 2.0 - br - 0.01
    parts.append(_frustum_z(xb, 0.0, 0.0, br * 0.5, br * 0.5, br, br, min(0.07, h * 0.2), "accent_ceramic", "object",
                            n=32))
    return contain(parts, w, d, h)


def ring_rug_parts(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """R48: a round rug with concentric stripes (a light ground, three rings in the rug's colour, each a hair over
    the ground so it shows)."""
    rx, ry = w / 2.0, d / 2.0
    lift = 0.0004
    ground = max(0.004, h - 6.0 * lift)
    parts = [_cylinder_z(0.0, 0.0, 0.0, rx, ry, ground, "pampas", "rug", n=72)]
    z = ground
    for share, band in ((0.92, 0.035), (0.70, 0.02), (0.45, 0.03)):
        # a ring is a thin band: a disc in the rug's colour, the ground's disc over it again inside the band
        parts.append(_cylinder_z(0.0, 0.0, z, rx * share, ry * share, lift, "accent_fabric", "stripe", n=72))
        parts.append(_cylinder_z(0.0, 0.0, z + lift, max(0.01, rx * share - band), max(0.01, ry * share - band), lift,
                                 "pampas", "rug", n=72))
        z += 2.0 * lift
    return contain(parts, w, d, h)


# --------------------------------------------------------------------------
# furniture forms
# --------------------------------------------------------------------------

def floating_console(w: float, d: float, h: float, piece: Optional[dict] = None) -> list[Part]:
    """R45: the low floating TV console (module docstring): a box hung under the unit's top at ``h``."""
    box_h = min(CONSOLE_BOX_M, h * 0.7)
    z0 = max(0.0, h - box_h)
    top_t = min(CONSOLE_TOP_T_M, box_h * 0.12)
    parts = [_box(0.0, 0.009, z0, w, d - 0.018, box_h - top_t, "wood", "body"),
             _box(0.0, 0.0, h - top_t, w, d, top_t, "wood", "top"),
             _box(0.0, d / 2.0 - 0.009, z0 + 0.03, w * 0.8, 0.018, box_h - 0.08, "dark", "cleat")]
    third = w / 3.0
    fh = box_h - top_t - 0.008
    for sx in (-1.0, 1.0):                                   # flat wood fronts, a finger groove under each top edge
        cx = sx * third
        parts.append(_box(cx, -d / 2.0 + 0.009, z0 + 0.004, third - SHADOW_GAP_M, 0.018, fh, "wood", "front"))
        parts.append(_box(cx, -d / 2.0 - 0.0005, z0 + fh - 0.012, (third - SHADOW_GAP_M) * 0.6, 0.002, 0.008, "dark",
                          "groove"))
    parts.append(_box(0.0, -d / 2.0 + 0.012, z0 + 0.004, third - SHADOW_GAP_M, 0.012, fh, "dark", "panel"))
    n = max(4, int((third - 0.01) / FLUTE_PITCH_M))
    pitch = (third - 0.01) / n
    r = pitch * 0.45
    for k in range(n):                                       # the black fluted strip: half-round vertical ribs
        x = -third / 2.0 + 0.005 + pitch * (k + 0.5)
        parts.append(_cylinder_z(x, -d / 2.0 + 0.006, z0 + 0.006, r, min(r, 0.006), fh - 0.004, "dark", "rib", n=8))
    return parts


def drum_table(w: float, d: float, h: float, piece: Optional[dict] = None) -> list[Part]:
    """R48: the round travertine drum coffee table (module docstring)."""
    r = min(w, d) / 2.0
    plinth = min(0.03, h * 0.08)
    top_t = min(0.03, h * 0.08)
    return [_cylinder_z(0.0, 0.0, 0.0, r * DRUM_PLINTH_SHARE, r * DRUM_PLINTH_SHARE, plinth, "stone_light", "plinth",
                        n=48),
            _cylinder_z(0.0, 0.0, plinth, r, r, h - plinth - top_t - 0.004, "stone_light", "body", n=64),
            _cylinder_z(0.0, 0.0, h - top_t - 0.004, r - 0.004, r - 0.004, 0.004, "dark", "groove", n=64),
            _cylinder_z(0.0, 0.0, h - top_t, r, r, top_t, "stone_light", "top", n=64)]


# --------------------------------------------------------------------------
# dispatch (``detail_parts``)
# --------------------------------------------------------------------------

DECOR_TYPES: tuple[str, ...] = ("panel_wall", "wall_discs")
DEFAULT_HEIGHT: dict[str, float] = {"panel_wall": 2.6, "wall_discs": 0.72}
LARGE_TYPES: tuple[str, ...] = ("panel_wall", "wall_discs")
FORMS: dict[tuple[str, str], object] = {("tv_unit", "floating"): floating_console, ("table_coffee", "drum"): drum_table}
PENDANT_FIXTURES: tuple[str, ...] = ("linear_pendant", "track_pendants")


def decor_parts(dtype: str, w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    if dtype == "panel_wall":
        return panel_wall_parts(w, d, h, item)
    if dtype == "wall_discs":
        return wall_discs_parts(w, d, h, item)
    raise KeyError(f"no salon builder for {dtype!r}")


def variant_parts(dtype: str, w: float, d: float, h: float, item: Optional[dict]) -> Optional[list[Part]]:
    """The parts of a P16 variant of an older decor type (module docstring), None for others."""
    it = item or {}
    if dtype == "wall_niche" and isinstance(it.get("niche"), dict) and it["niche"].get("style") == "tv_side":
        return tv_niche_parts(w, d, h, it)
    if dtype == "pendant_light" and it.get("fixture") == "linear_pendant":
        return linear_pendant_parts(w, d, h, it)
    if dtype == "pendant_light" and it.get("fixture") == "track_pendants":
        return track_pendants_parts(w, d, h, it)
    if dtype == "vase" and it.get("set") == "centrepiece":
        return centrepiece_parts(w, d, h, it)
    if dtype == "rug" and it.get("shape") == "round" and it.get("pattern") == "rings":
        return ring_rug_parts(w, d, h, it)
    return None
