"""The parametric products of the reference details (29 Oct 2026; user, sending seven professional interior renders:
"look at all these details I want these details", "As much detail as you can digest"; lessons UL113, UL115, UL119;
docs/reference_details_20261029.md H1, H2, H4-H7, R5, R10, R14, R17, R20, R26, R27, R29, R33).

What (pure: parts in the item's or the piece's local frame, bottom on z = 0, the front towards -Y, the back on the
wall at +Y; ``parametric.decor_parts`` and the furniture builders call these; one item is one mesh, its shelves,
LEDs and objects together, so the build makes one object per detail: lesson UL111):

- ``niche_parts`` (``wall_niche``, H1): a shallow built-out niche: a painted frame and a closed base with two doors, a
  wood board on the base, floating wood shelves each with an LED strip under its front edge (``led``: a low emission,
  ``led_strip_material``), styled objects on every board (books standing and lying, a vase, a ceramic bowl, a small
  sculpture, a bud vase of dried pampas grass).
- ``floor_vase_parts`` (``floor_vase``, H5): a big stone (or glazed terracotta) floor vase with a fan of dried pampas
  stems and plumes (``pampas``).
- ``vase_with_stems`` (a ``vase`` with ``stems: pampas``, H4): a tabletop vase with pampas, inside its item box.
- ``art_leaning_parts`` (``art_leaning``, R5): a large frame leaning on the floor against the wall, its lean set so
  its top rests on the wall; a canvas with a simple abstract composition (the item's colour).
- ``bag_parts`` (``bag``, R29): a weekend holdall (UL160: ``wenart.blender.holdall``: leather handles, tabs,
  piping, zips, a front pocket, a shoulder strap).
- ``desk_wall_unit_parts`` (``desk_wall_unit``, R27): a floating shelf with books and a small plant, wall cabinets
  with flat push-open doors over it and an LED strip under them.
- ``intercom_parts`` (``intercom``, H2): a video door station's indoor monitor: a dark glass screen, a camera, two
  buttons, a speaker grille.
- ``wall_tv_parts`` (a ``tv`` with ``tv.mount: wall``, R26): the flat panel on its wall bracket, no pedestal.
- ``round_mirror_parts`` (a ``mirror`` with ``shape: round``, R10, H4): a round mirror in a thick frame;
  ``arch_mirror_parts`` (``shape: arch``, R19): an arched mirror over a bedroom's dressing table.
- ``round_rug_parts`` (a ``rug`` with ``shape: round``, H6).
- ``track_parts`` (a ``ceiling_light`` with ``fixture: track``, H7, R14): a black ceiling rail with three spots.
- ``styled_book_set`` (a ``book_set`` with ``styled``, R20): books on part of the board and a small object beside them.
- ``drum_nightstand`` / ``floating_nightstand`` (a nightstand's ``form``, R17, R33) and ``floating_desk`` (a desk's
  ``form``, R27): the furniture products of a room's scheme (``wenart.furniture.room_schemes``), by design.
- 30 Oct 2026 (photo P16, lesson UL153): the living-dining room's products (``wenart.blender.salon_parts``): a tall
  black-lined lit niche beside the TV (a ``wall_niche`` with ``niche.style: tv_side``), a ``panel_wall`` of
  handle-less full-height fronts with a lit niche, ``wall_discs``, a linear pendant and a track with mini pendants over
  the dining table, the table's centrepiece set, a round rug with concentric stripes, the floating TV console and the
  round travertine drum coffee table (the forms of a ``tv_unit`` and a ``table_coffee``).

Sizes are designer values of real products (assumed). Every part stays inside its box (``contain``).
"""
from __future__ import annotations

import math
from typing import Optional

from wenart.blender import salon_parts as SP
from wenart.blender.parametric import (_box, _cylinder_y, _cylinder_z, _frustum_z, _superellipsoid,
                                       piece_design)

Part = dict

LED_STRENGTH = 2.5               # an LED strip's emission: a glow on the shelf below it, never a light source
LED_RGB = (1.0, 0.80, 0.58)      # 2700-3000 K
LED_MATERIAL = "wenart_led_strip"
PAMPAS_COLOUR = "cream"
BOOK_KEYS: tuple[str, ...] = ("dark", "painted", "terracotta", "wood", "colour_fabric")
FLOAT_NIGHTSTAND_H_M = 0.22      # a floating nightstand's box under its top (R33)
DRAWER_GROOVE_M = 0.004
# (the bevel radii of the roles these parts use: ``parametric.BEVEL_BY_ROLE``)


# --------------------------------------------------------------------------
# primitives
# --------------------------------------------------------------------------

def _rod(p0, p1, r: float, key: str, role: str, n: int = 6) -> Part:
    """A cylinder of radius ``r`` from ``p0`` to ``p1`` (3D points), wound outwards."""
    (x0, y0, z0), (x1, y1, z1) = p0, p1
    dx, dy, dz = x1 - x0, y1 - y0, z1 - z0
    length = math.sqrt(dx * dx + dy * dy + dz * dz) or 1e-6
    ux, uy, uz = dx / length, dy / length, dz / length
    ax = (1.0, 0.0, 0.0) if abs(ux) < 0.9 else (0.0, 1.0, 0.0)
    # e1 = ax x u, e2 = u x e1
    e1 = (ax[1] * uz - ax[2] * uy, ax[2] * ux - ax[0] * uz, ax[0] * uy - ax[1] * ux)
    m = math.sqrt(sum(c * c for c in e1)) or 1e-9
    e1 = tuple(c / m for c in e1)
    e2 = (uy * e1[2] - uz * e1[1], uz * e1[0] - ux * e1[2], ux * e1[1] - uy * e1[0])
    ring = []
    for k in range(n):
        a = 2.0 * math.pi * k / n
        ring.append((math.cos(a) * r, math.sin(a) * r))
    verts = [(x0 + e1[0] * c + e2[0] * s, y0 + e1[1] * c + e2[1] * s, z0 + e1[2] * c + e2[2] * s) for c, s in ring]
    verts += [(x1 + e1[0] * c + e2[0] * s, y1 + e1[1] * c + e2[1] * s, z1 + e1[2] * c + e2[2] * s) for c, s in ring]
    faces = [[k, (k + 1) % n, n + (k + 1) % n, n + k] for k in range(n)]
    faces.append(list(range(n, 2 * n)))
    faces.append(list(range(n - 1, -1, -1)))
    return {"verts": verts, "faces": faces, "key": key, "role": role}


def _oriented_plume(base, direction, length: float, radius: float, key: str = "pampas") -> Part:
    """A soft plume (an elongated superellipsoid) from ``base`` along the unit ``direction``."""
    part = _superellipsoid(0.0, 0.0, 0.0, radius * 2.0, radius * 2.0, length, 0.7, 1.0, key, "plume", n_eta=8, n_om=8)
    ux, uy, uz = direction
    # rotate +Z onto direction (Rodrigues about z x u)
    kx, ky = -uy, ux
    s = math.sqrt(kx * kx + ky * ky)
    c = uz
    out = []
    for x, y, z in part["verts"]:
        if s < 1e-9:
            rx, ry, rz = x, y, z if c > 0 else -z
        else:
            kx_, ky_ = kx / s, ky / s
            dot = kx_ * x + ky_ * y
            # v_rot = v c + (k x v) s + k (k.v)(1 - c), k = (kx_, ky_, 0)
            cx, cy, cz = ky_ * z, -kx_ * z, kx_ * y - ky_ * x
            rx = x * c + cx * s + kx_ * dot * (1.0 - c)
            ry = y * c + cy * s + ky_ * dot * (1.0 - c)
            rz = z * c + cz * s
        out.append((base[0] + rx, base[1] + ry, base[2] + rz))
    part["verts"] = out
    part["smooth"] = True
    return part


def bbox(parts) -> tuple[float, float, float, float, float, float]:
    xs = [v[0] for p in parts for v in p["verts"]]
    ys = [v[1] for p in parts for v in p["verts"]]
    zs = [v[2] for p in parts for v in p["verts"]]
    return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)


def contain(parts: list[Part], w: float, d: float, h: float, floor: bool = True) -> list[Part]:
    """The parts kept inside the box ``w x d x h`` (in place, returned): scaled down uniformly about the box's
    centre line where they reach out of it, and (``floor``) their bottom set on z = 0."""
    if not parts:
        return parts
    x0, y0, z0, x1, y1, z1 = bbox(parts)
    sx = min(1.0, (w / 2.0) / max(abs(x0), abs(x1), 1e-9))
    sy = min(1.0, (d / 2.0) / max(abs(y0), abs(y1), 1e-9))
    sz = min(1.0, h / max(z1 - (z0 if floor else 0.0), 1e-9))
    k = min(sx, sy, sz)
    shift = -z0 if floor else 0.0
    for p in parts:
        p["verts"] = [(x * k, y * k, (z + shift) * k) for x, y, z in p["verts"]]
    if floor:
        lo = min(v[2] for p in parts for v in p["verts"])
        if abs(lo) > 0.0:
            for p in parts:
                p["verts"] = [(x, y, z - lo) for x, y, z in p["verts"]]
    return parts


def books_upright(x0: float, x1: float, y: float, z: float, depth: float, max_h: float, seed: int = 0
                  ) -> list[Part]:
    """A row of standing books from ``x0`` to ``x1`` at ``y`` on a board at ``z`` (heights 70-100 % of ``max_h``)."""
    out = []
    if x1 - x0 < 0.03 or max_h < 0.04:
        return out
    n = max(2, min(12, int((x1 - x0) / 0.032)))
    bw = (x1 - x0) / n
    for k in range(n):
        f = 0.72 + 0.28 * (((k + seed) * 7) % 5) / 4.0
        out.append(_box(x0 + bw * (k + 0.5), y, z, bw - 0.003, depth * (0.85 + 0.15 * ((k + seed) % 2)), max_h * f,
                        BOOK_KEYS[(k + seed) % len(BOOK_KEYS)], "book"))
    return out


def books_lying(cx: float, cy: float, z: float, w: float, d: float, max_h: float, n: int = 3) -> list[Part]:
    out, zz = [], z
    t = min(0.035, max_h / max(1, n))
    for k in range(n):
        s = 1.0 - 0.07 * k
        out.append(_box(cx + 0.006 * (k % 2), cy, zz, w * s, d * s, t - 0.002, BOOK_KEYS[k % 4], "book"))
        zz += t
    return out


def small_vase(cx: float, cy: float, z: float, r: float, h: float, key: str = "ceramic") -> list[Part]:
    return [_cylinder_z(cx, cy, z, r, r, h * 0.7, key, "object", n=20),
            _frustum_z(cx, cy, z + h * 0.7, r, r, r * 0.55, r * 0.55, h * 0.3, key, "object", n=20)]


def pampas(cx: float, cy: float, z0: float, top: float, spread: float, n: int = 7, seed: int = 0) -> list[Part]:
    """A fan of ``n`` dried pampas stems from ``(cx, cy, z0)``: thin stems up to plumes whose tips reach ``top``, the
    plumes leaning out up to ``spread`` sideways."""
    out = []
    height = top - z0
    if height <= 0.05:
        return out
    for k in range(n):
        a = 2.0 * math.pi * (k + 0.37 * seed) / n
        lean = spread * (0.45 + 0.55 * ((k * 3 + seed) % 4) / 3.0)
        plume = min(0.30, height * 0.38) * (0.8 + 0.2 * (k % 3) / 2.0)
        tip = (cx + math.cos(a) * lean, cy + math.sin(a) * lean, top - height * 0.06 * (k % 3))
        dx, dy, dz = tip[0] - cx, tip[1] - cy, tip[2] - z0
        L = math.sqrt(dx * dx + dy * dy + dz * dz)
        u = (dx / L, dy / L, dz / L)
        base = (tip[0] - u[0] * plume, tip[1] - u[1] * plume, tip[2] - u[2] * plume)
        out.append(_rod((cx, cy, z0), base, 0.0022, "rattan", "stem", n=5))
        out.append(_oriented_plume(base, u, plume, min(0.035, plume * 0.16)))
    return out


# --------------------------------------------------------------------------
# decor
# --------------------------------------------------------------------------

def niche_parts(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """H1 (module docstring): the built-out lit niche in its box (back on +Y)."""
    spec = (item or {}).get("niche") if isinstance((item or {}).get("niche"), dict) else {}
    t = min(0.03, w / 10.0, h / 10.0)
    base_h = min(0.42, h * 0.22)
    inner = w - 2.0 * t
    parts = [_box(-w / 2.0 + t / 2.0, 0.0, 0.0, t, d, h, "painted", "side"),
             _box(w / 2.0 - t / 2.0, 0.0, 0.0, t, d, h, "painted", "side"),
             _box(0.0, 0.0, h - t, inner - 0.001, d, t, "painted", "top"),
             _box(0.0, d / 2.0 - 0.006, base_h, inner - 0.001, 0.012, h - t - base_h, "painted", "back"),
             _box(0.0, 0.006, 0.0, inner - 0.001, d - 0.012, base_h - 0.004, "painted", "body")]
    gap = 0.003
    dw = (inner - 3.0 * gap) / 2.0
    for sx in (-1.0, 1.0):                                   # the base's two flat doors, a groove between them
        parts.append(_box(sx * (gap / 2.0 + dw / 2.0), -d / 2.0 + 0.009, 0.06, dw, 0.018, base_h - 0.064, "front",
                          "front"))
    board = min(0.03, (h - base_h) / 20.0)
    parts.append(_box(0.0, -0.002, base_h - 0.004, inner - 0.002, d - 0.016, board, "wood", "shelf"))
    n = max(2, int(spec.get("shelves") or 4))
    usable = h - t - base_h - board
    pitch = usable / n
    floors = [base_h - 0.004 + board]
    for k in range(1, n):
        z = base_h + k * pitch
        parts.append(_box(0.0, -0.004, z, inner - 0.002, d - 0.024, board, "wood", "shelf"))
        floors.append(z + board)
    ceilings = [f + pitch - board for f in floors]
    ceilings[-1] = h - t
    led_d = min(0.012, d / 10.0)
    for top in ceilings:                                      # an LED strip under the front edge of every board above
        parts.append(_box(0.0, -d / 2.0 + 0.03, top - 0.008, inner - 0.04, led_d, 0.006, "led", "led"))
    if spec.get("objects", True):
        for k, (z, top) in enumerate(zip(floors, ceilings)):
            room = top - z - 0.03
            if room < 0.06:
                continue
            x_l, x_r = -inner / 2.0 + 0.03, inner / 2.0 - 0.03
            y = 0.02
            dd = min(0.16, d - 0.08)
            g = k % 3
            if g == 0:
                parts += books_upright(x_l, x_l + inner * 0.42, y, z, dd, min(0.26, room), seed=k)
                r = min(0.06, inner * 0.08, dd / 2.0)
                parts += small_vase(x_r - r - 0.04, y, z, r, min(0.24, room), "accent_ceramic")
            elif g == 1:
                parts += books_lying(x_l + inner * 0.18, y, z, min(0.24, inner * 0.3), dd, min(0.1, room * 0.5))
                br = min(0.09, inner * 0.1, dd / 2.0)
                parts.append(_cylinder_z(0.05, y, z, br * 0.55, br * 0.55, min(0.03, room * 0.2), "ceramic", "object",
                                         n=20))
                parts.append(_frustum_z(0.05, y, z + min(0.03, room * 0.2), br * 0.6, br * 0.6, br, br,
                                        min(0.05, room * 0.3), "ceramic", "object", n=24))
                sr = min(0.05, inner * 0.06, dd / 2.0)
                parts.append(_superellipsoid(x_r - sr - 0.04, y, z, sr * 2.0, sr * 2.0, min(0.2, room * 0.8), 0.8, 0.9,
                                             "dark", "object", n_eta=8, n_om=16))
            else:
                vr = min(0.035, dd / 3.0)
                vh = min(0.14, room * 0.45)
                parts += small_vase(x_l + 0.08, y, z, vr, vh, "accent_ceramic")
                parts += pampas(x_l + 0.08, y, z + vh * 0.9, min(top - 0.03, z + room), min(0.08, inner * 0.08),
                                n=5, seed=k)
                parts += books_upright(x_r - inner * 0.38, x_r, y, z, dd, min(0.24, room), seed=k + 2)
    return contain(parts, w, d, h)


def floor_vase_parts(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """H5: a big floor vase with dried pampas grass (stone by default, glazed in the item's colour with
    ``finish: glazed``)."""
    r = min(w, d) / 2.0
    vh = min(0.6, h * 0.45)
    key = "accent_ceramic" if (item or {}).get("finish") == "glazed" else "marble"
    rs = (0.55, 0.85, 0.95, 0.62, 0.48)
    zs = (0.0, 0.18, 0.62, 0.88, 1.0)
    parts = []
    for k in range(4):
        parts.append(_frustum_z(0.0, 0.0, vh * zs[k], r * rs[k], r * rs[k], r * rs[k + 1], r * rs[k + 1],
                                vh * (zs[k + 1] - zs[k]), key, "body", n=32))
    parts += pampas(0.0, 0.0, vh * 0.95, h, r * 0.95, n=9)
    return contain(parts, w, d, h)


def vase_with_stems(w: float, d: float, h: float) -> list[Part]:
    """H4: a tabletop vase with dried pampas grass in its box (the vase the lower 40 %)."""
    r = min(w, d) / 2.0
    vh = h * 0.4
    parts = [_cylinder_z(0.0, 0.0, 0.0, r * 0.75, r * 0.75, vh * 0.75, "accent_ceramic", "body", n=24),
             _frustum_z(0.0, 0.0, vh * 0.75, r * 0.75, r * 0.75, r * 0.42, r * 0.42, vh * 0.25, "accent_ceramic",
                        "neck", n=24)]
    parts += pampas(0.0, 0.0, vh * 0.95, h, r * 0.95, n=6)
    return contain(parts, w, d, h)


def art_leaning_parts(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """R5: a large frame leaning on the floor against the wall (+Y): its lean makes its top touch the wall at the
    box's back."""
    fd = min(0.03, d * 0.25)                                  # the frame's depth
    ft = min(0.035, w / 12.0, h / 12.0)                       # its width
    y_front = -d / 2.0 + 0.005
    lean = math.atan2(max(0.0, d - 0.01 - fd), h)             # the back's top on the wall
    L = h / math.cos(lean)
    frame_key = "dark" if (item or {}).get("frame") == "dark" else "wood"
    up = []                                                   # upright, bottom front edge on y = 0, z = 0
    up.append(_box(-w / 2.0 + ft / 2.0, fd / 2.0, 0.0, ft, fd, L, frame_key, "frame"))
    up.append(_box(w / 2.0 - ft / 2.0, fd / 2.0, 0.0, ft, fd, L, frame_key, "frame"))
    up.append(_box(0.0, fd / 2.0, 0.0, w - 2.0 * ft - 0.001, fd, ft, frame_key, "frame"))
    up.append(_box(0.0, fd / 2.0, L - ft, w - 2.0 * ft - 0.001, fd, ft, frame_key, "frame"))
    cw, ch = w - 2.0 * ft, L - 2.0 * ft
    up.append(_box(0.0, fd * 0.6, ft, cw - 0.002, fd * 0.4, ch, "painted", "canvas"))
    # a simple abstract composition: a large disc and a band in the item's colour, a thin dark line
    disc = min(cw, ch) * 0.32
    up.append(_cylinder_y(-cw * 0.12, fd * 0.6 - 0.002, ft + ch * 0.58, disc, disc, 0.002, "colour_painted", "canvas",
                          n=40))
    up.append(_box(cw * 0.12, fd * 0.6 - 0.003, ft + ch * 0.12, cw * 0.38, 0.002, ch * 0.36, "terracotta", "canvas"))
    up.append(_box(cw * 0.3, fd * 0.6 - 0.004, ft + ch * 0.05, 0.006, 0.002, ch * 0.8, "dark", "canvas"))
    c, s = math.cos(lean), math.sin(lean)
    for p in up:                                              # turn back about the bottom front edge
        p["verts"] = [(x, y_front + y * c + z * s, -y * s + z * c + 0.0) for x, y, z in p["verts"]]
    lo = min(v[2] for p in up for v in p["verts"])
    for p in up:
        p["verts"] = [(x, y, z - lo) for x, y, z in p["verts"]]
    return contain(up, w, d, h)


def bag_parts(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """R29: a weekend holdall lying on the floor (30 Oct 2026, UL160: ``holdall.holdall_parts``: a soft barrel body
    with a leather base, piped end panels, a top zip with its pull and garage tabs, rolled leather handles on riveted
    tabs held by a wrap, a front pocket, a shoulder strap clipped to D-rings and lying on the floor, base studs)."""
    from wenart.blender import holdall as HD

    return contain(HD.holdall_parts(w, d, h, item), w, d, h)


def desk_wall_unit_parts(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """R27: a floating shelf (bottom) and wall cabinets (top) with an LED strip under them, books and a small plant on
    the shelf."""
    shelf_t = min(0.03, h / 15.0)
    shelf_d = min(0.24, d * 0.75)
    ch = min(0.36, h * 0.55)
    parts = [_box(0.0, d / 2.0 - shelf_d / 2.0, 0.0, w, shelf_d, shelf_t, "wood", "shelf"),
             _box(0.0, 0.006, h - ch, w, d - 0.012, ch, "painted", "body")]
    n = max(2, int(round(w / 0.4)))
    gap = 0.003
    fw = (w - (n + 1) * gap) / n
    for k in range(n):
        x = -w / 2.0 + gap + fw / 2.0 + k * (fw + gap)
        parts.append(_box(x, -d / 2.0 + 0.009, h - ch + 0.004, fw, 0.018, ch - 0.008, "front", "front"))
    parts.append(_box(0.0, -d / 2.0 + 0.05, h - ch - 0.007, w - 0.04, min(0.012, d / 10.0), 0.006, "led", "led"))
    room = h - ch - shelf_t - 0.04
    if room > 0.06:
        y = d / 2.0 - shelf_d / 2.0
        parts += books_upright(-w / 2.0 + 0.03, -w / 2.0 + 0.03 + min(0.35, w * 0.35), y, shelf_t,
                               min(0.17, shelf_d - 0.04), min(0.24, room), seed=1)
        pr = min(0.06, shelf_d / 3.0)
        ph = min(0.12, room * 0.45)
        parts.append(_cylinder_z(w / 2.0 - 0.12, y, shelf_t, pr, pr, ph, "accent_ceramic", "object", n=20))
        parts.append(_superellipsoid(w / 2.0 - 0.12, y, shelf_t + ph * 0.9, pr * 2.4, pr * 2.4, min(room - ph, 0.16),
                                     0.7, 0.8, "green", "object", n_eta=8, n_om=16))
    return contain(parts, w, d, h)


def intercom_parts(w: float, d: float, h: float) -> list[Part]:
    """H2: a video door station's indoor monitor on the wall."""
    parts = [_box(0.0, 0.002, 0.0, w, d - 0.004, h, "steel", "body"),
             _box(0.0, -d / 2.0 + 0.001, h * 0.42, w * 0.84, 0.002, h * 0.5, "screen", "screen"),
             _cylinder_y(0.0, -d / 2.0, h * 0.95, min(0.004, w / 20.0), min(0.004, w / 20.0), 0.002, "dark", "lens",
                         n=12)]
    for sx in (-1.0, 1.0):
        parts.append(_box(sx * w * 0.22, -d / 2.0 + 0.0015, h * 0.2, w * 0.28, 0.003, h * 0.1, "dark", "button"))
    for k in range(4):
        parts.append(_box(0.0, -d / 2.0 + 0.0015, h * (0.06 + 0.025 * k), w * 0.4, 0.003, 0.003, "dark", "grille"))
    return contain(parts, w, d, h)


def wall_tv_parts(w: float, d: float, h: float, panel_t: float = 0.03, bezel: float = 0.01) -> list[Part]:
    """R26: the flat TV on its wall bracket (the box's back on the wall)."""
    bt = min(0.025, d / 3.0)
    t = min(panel_t, d - bt)
    y_panel = d / 2.0 - bt - t / 2.0
    b = min(bezel, w / 20.0, h / 20.0)
    return contain([_box(0.0, d / 2.0 - bt / 2.0, h * 0.3, w * 0.4, bt, h * 0.4, "dark", "bracket"),
                    _box(0.0, y_panel, 0.0, w, t, h, "dark", "panel"),
                    _box(0.0, y_panel - t / 2.0 - 0.001, b, w - 2.0 * b, 0.002, h - 2.0 * b, "screen", "screen")],
                   w, d, h)


def round_mirror_parts(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """R10 / H4: a round mirror in a thick frame (the glass on the front, -Y)."""
    r = min(w, h) / 2.0
    f = min(0.045, r / 5.0)
    g = min(0.004, d / 4.0)
    key = "dark" if (item or {}).get("frame") == "dark" else "accent_wood"
    return contain([_cylinder_y(0.0, -d / 2.0 + g, r, r, r, d - g, key, "frame", n=56),
                    _cylinder_y(0.0, -d / 2.0, r, r - f, r - f, g + 0.0005, "mirror", "glass", n=56)], w, d, h)


def _prism_y(profile, y0: float, y1: float, key: str, role: str) -> Part:
    """A convex polygon ``profile`` (``[(x, z)]``, counter-clockwise seen from -Y) extruded from ``y0`` to ``y1``."""
    n = len(profile)
    verts = [(x, y0, z) for x, z in profile] + [(x, y1, z) for x, z in profile]
    faces = [list(range(n)), list(range(2 * n - 1, n - 1, -1))]
    faces += [[k, n + k, n + (k + 1) % n, (k + 1) % n] for k in range(n)]
    part = {"verts": verts, "faces": faces, "key": key, "role": role}
    cx = sum(v[0] for v in verts) / len(verts)
    cy = sum(v[1] for v in verts) / len(verts)
    cz = sum(v[2] for v in verts) / len(verts)
    fixed = []
    for f in faces:                                  # wound outwards whatever the profile's turn
        a, b, c = (verts[i] for i in f[:3])
        nx = (b[1] - a[1]) * (c[2] - a[2]) - (b[2] - a[2]) * (c[1] - a[1])
        ny = (b[2] - a[2]) * (c[0] - a[0]) - (b[0] - a[0]) * (c[2] - a[2])
        nz = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        fc = [sum(verts[i][k] for i in f) / len(f) for k in range(3)]
        fixed.append(f if nx * (fc[0] - cx) + ny * (fc[1] - cy) + nz * (fc[2] - cz) >= 0 else list(reversed(f)))
    part["faces"] = fixed
    return part


def arch_profile(w: float, h: float, inset: float = 0.0, steps: int = 16) -> list[tuple[float, float]]:
    """The outline of an arch-topped panel ``w`` wide, ``h`` high (``[(x, z)]``; a half circle of radius ``w / 2``
    on a rectangle), shrunk by ``inset``."""
    r = w / 2.0 - inset
    zc = h - w / 2.0
    pts = [(-r, inset), (r, inset)]
    for k in range(steps + 1):
        a = math.pi * k / steps
        pts.append((r * math.cos(a), zc + r * math.sin(a)))
    pts.append((-r, inset))
    return [p for i, p in enumerate(pts[:-1]) if i == 0 or (abs(p[0] - pts[i - 1][0]) > 1e-9
                                                            or abs(p[1] - pts[i - 1][1]) > 1e-9)]


def arch_mirror_parts(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """R19: an arched mirror over a dressing table: a thin frame (black or wood), the glass on its front."""
    h = max(h, w * 0.75)
    f = min(0.025, w / 12.0)
    g = min(0.004, d / 4.0)
    key = "dark" if (item or {}).get("frame") == "dark" else "accent_wood"
    return contain([_prism_y(arch_profile(w, h), -d / 2.0 + g, d / 2.0, key, "frame"),
                    _prism_y(arch_profile(w, h, f), -d / 2.0, -d / 2.0 + g + 0.0005, "mirror", "glass")], w, d, h)


def round_rug_parts(w: float, d: float, h: float) -> list[Part]:
    return [_cylinder_z(0.0, 0.0, 0.0, w / 2.0, d / 2.0, h, "fabric", "rug", n=64)]


def track_parts(w: float, d: float, h: float) -> list[Part]:
    """H7 / R14: a black ceiling rail (its top on the ceiling at h) with three spots."""
    rail = min(0.035, h / 3.0, d)
    stem = min(0.03, h / 4.0)
    head_h = max(0.01, h - rail - stem)
    hr = min(0.03, d / 2.0, w / 8.0)
    parts = [_box(0.0, 0.0, h - rail, w, min(d, rail), rail, "dark", "rail")]
    for k in (-1, 0, 1):
        x = k * w / 3.0
        parts.append(_cylinder_z(x, 0.0, h - rail - stem, 0.007, 0.007, stem, "dark", "stem", n=8))
        parts.append(_cylinder_z(x, 0.0, 0.004, hr, hr, head_h - 0.004, "dark", "head", n=20))   # only its lens glows
        parts.append(_cylinder_z(x, 0.0, 0.0, hr * 0.7, hr * 0.7, 0.004, "bulb", "bulb", n=16))
    return contain(parts, w, d, h)


def styled_book_set(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """R20: books standing on ``books_share`` of the set's width, a small object beside them (vase, sculpture or
    bowl)."""
    spec = (item or {}).get("styled") if isinstance((item or {}).get("styled"), dict) else {}
    share = min(0.85, max(0.4, float(spec.get("books_share") or 0.62)))
    split = -w / 2.0 + w * share
    parts = books_upright(-w / 2.0 + 0.002, split - 0.01, 0.0, 0.0, d, h, seed=3)
    room_w = w / 2.0 - split - 0.01
    cx = split + 0.01 + room_w / 2.0
    r = max(0.01, min(room_w / 2.0, d / 2.0) - 0.002)
    what = spec.get("object") or "vase"
    if what == "sculpture":
        parts.append(_superellipsoid(cx, 0.0, 0.0, r * 2.0, r * 2.0, h * 0.8, 0.8, 0.9, "dark", "object", n_eta=8,
                                     n_om=16))
    elif what == "bowl":
        parts.append(_frustum_z(cx, 0.0, 0.0, r * 0.55, r * 0.55, r, r, min(h, r * 0.9), "accent_ceramic", "object",
                                n=24))
    else:
        parts += small_vase(cx, 0.0, 0.0, r * 0.8, h * 0.85, "accent_ceramic")
    return contain(parts, w, d, h)


# --------------------------------------------------------------------------
# furniture forms (a room's scheme)
# --------------------------------------------------------------------------

def drum_nightstand(w: float, d: float, h: float, piece: Optional[dict] = None) -> list[Part]:
    """R17: a round drum nightstand with two drawers (grooves) and small knobs, on a recessed plinth (the diameter
    the footprint's smaller side)."""
    design = piece_design(piece)
    r = min(w, d) / 2.0
    body_key = "front" if design.get("colour") else "wood"
    plinth = min(0.04, h * 0.08)
    top_t = min(0.02, h * 0.05)
    parts = [_cylinder_z(0.0, 0.0, 0.0, r * 0.82, r * 0.82, plinth, "dark", "plinth", n=40),
             _cylinder_z(0.0, 0.0, plinth, r, r, h - plinth - top_t, body_key, "body", n=48),
             _cylinder_z(0.0, 0.0, h - top_t, r, r, top_t, "wood", "top", n=48)]
    span = h - plinth - top_t
    for k in (1, 2):
        z = plinth + span * k / 3.0
        parts.append(_cylinder_z(0.0, 0.0, z - DRAWER_GROOVE_M / 2.0, r + 0.0006, r + 0.0006, DRAWER_GROOVE_M, "dark",
                                 "groove", n=48))
    for k in (0, 1):
        zc = plinth + span * (k + 0.5) / 3.0 + span / 6.0
        parts.append(_cylinder_y(0.0, -r - 0.008, zc, 0.011, 0.011, 0.010, "handle", "handle", n=12))
    return parts


def floating_nightstand(w: float, d: float, h: float, piece: Optional[dict] = None) -> list[Part]:
    """R33: a box hung on the wall (its top at the type's height), a drawer with a finger groove, a hidden cleat at
    its back; nothing under it to the floor."""
    box_h = min(FLOAT_NIGHTSTAND_H_M, h * 0.6)
    z0 = max(0.0, h - box_h)
    top_t = min(0.02, box_h * 0.12)
    parts = [_box(0.0, 0.006, z0, w, d - 0.012, box_h - top_t, "front" if piece_design(piece).get("colour") else
                  "painted", "body"),
             _box(0.0, 0.0, h - top_t, w, d, top_t, "wood", "top"),
             _box(0.0, -d / 2.0 + 0.009, z0 + 0.006, w - 0.008, 0.018, box_h - top_t - 0.04, "front", "front"),
             _box(0.0, -d / 2.0 - 0.0005, z0 + box_h - top_t - 0.03, w * 0.6, 0.002, 0.012, "dark", "groove"),
             _box(0.0, d / 2.0 - 0.009, z0 + 0.03, w * 0.7, 0.018, box_h - 0.08, "dark", "cleat")]
    return parts


def floating_desk(w: float, d: float, h: float, piece: Optional[dict] = None) -> list[Part]:
    """R27: a wall-hung desk top (a wood top, a cleat along the wall under its back) carried at its free end by an
    open black shelf unit with books (``form_detail.support``: the side of the free end, ``shelf_unit_w``), or by a
    full-depth wood end panel where the desk is too narrow for the unit."""
    det = (piece or {}).get("form_detail") if isinstance((piece or {}).get("form_detail"), dict) else {}
    sgn = -1.0 if det.get("support") == "-x" else 1.0
    s = float(det.get("shelf_unit_w") if det.get("shelf_unit_w") is not None else 0.4)
    s = min(s, w * 0.45)
    top_t = min(0.035, h * 0.06)
    parts = [_box(0.0, 0.0, h - top_t, w, d, top_t, "wood", "top"),
             _box(0.0, d / 2.0 - 0.015, h - top_t - 0.05, w - 0.1, 0.03, 0.0499, "wood", "apron")]
    if s < 0.2:
        parts.append(_box(sgn * (w / 2.0 - 0.0125), 0.0, 0.0, 0.025, d, h - top_t - 0.0005, "wood", "side"))
        return parts
    xc = sgn * (w / 2.0 - s / 2.0)
    sd = d - 0.04
    sh = h - top_t - 0.001
    parts += [_box(xc - s / 2.0 + 0.0125, 0.0, 0.0, 0.025, sd, sh, "dark", "side"),
              _box(xc + s / 2.0 - 0.0125, 0.0, 0.0, 0.025, sd, sh, "dark", "side"),
              _box(xc, 0.0, 0.0, s - 0.051, sd, 0.03, "dark", "bottom")]
    boards = (sh * 0.36, sh * 0.70)
    for z in boards:
        parts.append(_box(xc, 0.0, z, s - 0.051, sd - 0.01, 0.02, "dark", "shelf"))
    for k, z in enumerate((0.03, boards[0] + 0.02)):
        room = (boards[k] if k == 0 else boards[1]) - z - 0.02
        parts += books_upright(xc - s / 2.0 + 0.03, xc + s / 2.0 - 0.06, 0.0, z, min(0.18, sd - 0.04),
                               min(0.24, room), seed=k)
    return parts


# --------------------------------------------------------------------------
# dispatch and the LED material
# --------------------------------------------------------------------------

DETAIL_DECOR_TYPES: tuple[str, ...] = ("wall_niche", "intercom", "floor_vase", "art_leaning", "bag", "desk_wall_unit")
DETAIL_DEFAULT_HEIGHT: dict[str, float] = {"wall_niche": 2.2, "intercom": 0.22, "floor_vase": 1.3,
                                           "art_leaning": 1.4, "bag": 0.30, "desk_wall_unit": 0.68}
LARGE_DETAIL_TYPES: tuple[str, ...] = ("wall_niche", "floor_vase", "art_leaning", "desk_wall_unit")
# 30 Oct 2026 (photo P16, UL153): the living-dining room's own detail types (wenart.blender.salon_parts)
DETAIL_DECOR_TYPES = DETAIL_DECOR_TYPES + SP.DECOR_TYPES
DETAIL_DEFAULT_HEIGHT.update(SP.DEFAULT_HEIGHT)
LARGE_DETAIL_TYPES = LARGE_DETAIL_TYPES + SP.LARGE_TYPES


def detail_parts(dtype: str, w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """The parts of a detail decor type (``DETAIL_DECOR_TYPES``)."""
    if dtype in SP.DECOR_TYPES:                              # 30 Oct 2026 (P16, UL153): a panel wall, wall discs
        return SP.decor_parts(dtype, w, d, h, item)
    salon = SP.variant_parts(dtype, w, d, h, item)          # 30 Oct 2026 (R45): a black-lined niche beside the TV
    if salon is not None:
        return salon
    if dtype == "wall_niche":
        return niche_parts(w, d, h, item)
    if dtype == "intercom":
        return intercom_parts(w, d, h)
    if dtype == "floor_vase":
        return floor_vase_parts(w, d, h, item)
    if dtype == "art_leaning":
        return art_leaning_parts(w, d, h, item)
    if dtype == "bag":
        return bag_parts(w, d, h, item)
    if dtype == "desk_wall_unit":
        return desk_wall_unit_parts(w, d, h, item)
    raise KeyError(f"no detail builder for {dtype!r}")


def variant_parts(dtype: str, w: float, d: float, h: float, item: Optional[dict]) -> Optional[list[Part]]:
    """The parts of a detail variant of an older decor type (a round mirror or rug, a track light, a wall TV, a vase
    with pampas, a styled book set), None for the plain type."""
    it = item or {}
    salon = SP.variant_parts(dtype, w, d, h, it)            # 30 Oct 2026 (P16, UL153): the living-dining variants
    if salon is not None:
        return salon
    if dtype == "mirror" and it.get("shape") == "round":
        return round_mirror_parts(w, d, h, it)
    if dtype == "mirror" and it.get("shape") == "arch":
        return arch_mirror_parts(w, d, h, it)
    if dtype == "rug" and it.get("shape") == "round":
        return round_rug_parts(w, d, h)
    if dtype == "ceiling_light" and it.get("fixture") == "track":
        return track_parts(w, d, h)
    if dtype == "tv" and ((it.get("tv") or {}).get("mount") == "wall"):
        return wall_tv_parts(w, d, h)
    if dtype == "vase" and it.get("set") == "bedside":
        from wenart.blender import bedding_parts as BP      # 29 Oct 2026 (UL121, R36): the nightstand's decor set
        return BP.bedside_set_parts(w, d, h, it)
    if dtype == "vase" and it.get("stems") == "pampas":
        return vase_with_stems(w, d, h)
    if dtype == "book_set" and isinstance(it.get("styled"), dict):
        return styled_book_set(w, d, h, it)
    return None


FORM_BUILDERS = {("nightstand", "drum"): drum_nightstand, ("nightstand", "floating"): floating_nightstand,
                 ("desk", "floating"): floating_desk}
FORM_BUILDERS.update(SP.FORMS)          # 30 Oct 2026 (P16, UL153): the floating TV console, the drum coffee table


def form_parts(ftype: str, w: float, d: float, h: float, piece: Optional[dict]) -> Optional[list[Part]]:
    """The parts of a piece's scheme form (``FORM_BUILDERS``), None without one."""
    fn = FORM_BUILDERS.get((ftype, (piece or {}).get("form")))
    return fn(w, d, h, piece) if fn else None


def led_strip_material(name: str = LED_MATERIAL):
    """The material of an LED strip (bpy): ``materials.led_material``, the one LED strip material of the scene (the
    bathroom's, the kitchen's and these details' strips; 29 Oct 2026: two helpers had one name and two strengths)."""
    from wenart.blender import materials as M

    return M.led_material(name)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    for n in list(nodes):
        if n.bl_idname == "ShaderNodeBsdfPrincipled":
            nodes.remove(n)
    emit = nodes.new("ShaderNodeEmission")
    emit.inputs["Color"].default_value = (*LED_RGB, 1.0)
    emit.inputs["Strength"].default_value = float(LED_STRENGTH)
    links.new(emit.outputs["Emission"], nodes.get("Material Output").inputs["Surface"])
    mat["wenart_led"] = float(LED_STRENGTH)
    return mat
