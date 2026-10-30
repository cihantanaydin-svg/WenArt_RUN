"""Every pool with a ladder into the water and a place to sit on its deck (30 Oct 2026, lesson UL143; user on real04
run 20261029-201533-full: "Pool can use some seating furniture also a ladder to the pool as always").

What (pure; ``site.build_pool_extras`` makes the objects):

- ``plan(site)``: per built pool ``{"pool_id", "deck_id", "deck_z", "ladder", "seating", "notes"}``:
  - the ladder: a stainless steel pool ladder (two handrails curving over the coping, ``LADDER["treads"]`` treads in
    the water) on a long side of the pool whose deck strip holds it, ``LADDER["corner_m"]`` from the corner nearest the
    house (the end people come from; the documents give no shallow end), clear of the flights and the guards;
  - the seating, along a long side first, facing the water, ``WALKWAY_M`` of free deck kept along the pool's coping:
    two sun loungers with a small side table between them where the deck is deep enough (``SETS["loungers"]``), else a
    pair of outdoor lounge chairs with a side table (``SETS["chairs"]``), each piece inside the deck ``INSET_M`` from
    its edge, clear of the flights' footprints and landings, the ladder, the house and the other pools. None (with the
    reason) where the deck has no room.
- ``ladder_meshes(ladder)`` / ``seat_meshes(piece)``: the parametric ladder (round tubes, real proportions) and the
  parametric outdoor pieces (a teak frame on brushed steel with outdoor cushions) used when no audited library model
  is made for outside (``library_seat``: the catalogue's ``chaise`` / ``side_table`` / ``armchair`` models that
  ``outdoor.outdoor_ready`` accepts, audit keep or fix).
- ``review(site, manifest)``: rule G11 of the model review's M15: a built pool without a ladder, or a deck with room for
  seating and none built.

Every piece is ``inferred`` and ``added_by_ai`` with its reason; the documents draw the pool, not its furniture.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart import geometry as G
from wenart.blender import geom2d

LADDER = {"rail_gap": 0.50, "tube_r": 0.021, "rise": 0.88, "anchor": 0.40, "over": 0.10, "in_wall": 0.12,
          "down": 1.05, "treads": 3, "tread_pitch": 0.27, "tread_d": 0.09, "tread_t": 0.035, "first_tread": 0.30,
          "corner_m": 0.8, "deck_min_m": 0.6, "clear_m": 0.6}
WALKWAY_M = 1.0                   # free deck along the pool's coping
INSET_M = 0.25                    # every piece this far inside the deck's edge
CLEAR_M = 0.3                     # from the flights' footprints, the house, the ladder
LANDING_CLEAR_M = 1.0             # the foot of a flight stays free this far out
SLIDE_M = 0.25                    # positions tried along an edge
GAP_M = 0.10                      # between the pieces of a set
# set -> [(type, (width along the edge, depth across it), height)]; the pieces stand side by side along the edge
SETS = {"loungers": [("sun_lounger", (0.70, 1.95), 0.85), ("side_table", (0.45, 0.45), 0.45),
                     ("sun_lounger", (0.70, 1.95), 0.85)],
        "chairs": [("lounge_chair", (0.75, 0.85), 0.80), ("side_table", (0.45, 0.45), 0.45),
                   ("lounge_chair", (0.75, 0.85), 0.80)]}
SET_ORDER = ("loungers", "chairs")
MATERIALS = {"frame": "wood_veneer_teak", "metal": "steel_brushed", "cushion": "fabric_cotton"}
CHECK_RULE = "G11"


def _deck(site: dict, pool: dict) -> Optional[dict]:
    pid = pool.get("id")
    return next((pf for pf in site.get("platforms") or [] if pid in (pf.get("pools") or [])), None)


def _strip(a, b, n, d0: float, d1: float, s0: float, s1: float) -> list[tuple[float, float]]:
    """The rectangle along the edge ``a``-``b`` from ``s0`` to ``s1`` along it and ``d0`` to ``d1`` out (``n``)."""
    length = G.distance(a, b)
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    return geom2d.ccw([(a[0] + ux * s + n[0] * d, a[1] + uy * s + n[1] * d)
                       for s, d in ((s0, d0), (s1, d0), (s1, d1), (s0, d1))])


def _on_deck(poly, deck: dict, keep: Sequence, inset: float = 0.0, clear: float = CLEAR_M) -> bool:
    """Whether a convex zone, grown by ``inset``, lies on the deck (outside its holes) and, grown by ``clear``, touches
    no keep-out (pure)."""
    from wenart.blender import site as S

    grown = geom2d.offset_polygon(poly, -inset) if inset else poly
    holes = [h for h in deck.get("holes") or [] if len(h) >= 3]
    probe = list(grown) + [G.polygon_centroid(grown)]
    if not all(G.point_in_polygon(p, deck["polygon"]) and not any(G.point_in_polygon(p, h) for h in holes)
               for p in probe):
        return False                                     # a corner off the deck: no need to sample the rest
    if S.area_share(grown, deck["polygon"], holes, step=0.15) < 0.999:
        return False
    wide = geom2d.offset_polygon(poly, -clear) if clear else poly
    wx0, wy0, wx1, wy1 = G.bbox(wide)
    for k in keep:
        kx0, ky0, kx1, ky1 = G.bbox([tuple(q[:2]) for q in k])
        if kx1 < wx0 or kx0 > wx1 or ky1 < wy0 or ky0 > wy1:
            continue
        if S.area_share(wide, k, step=0.15) > 0.0:
            return False
    return True


def keep_outs(site: dict, deck: dict) -> list:
    """What a pool's furniture keeps clear of (pure): the flights of every platform (their footprints and
    ``LANDING_CLEAR_M`` past their foot), the house and the other buildings, the other pools; grown by ``CLEAR_M``."""
    from wenart.blender import architect as AR
    from wenart.blender import grading as GR
    from wenart.blender import site as S

    keep = [geom2d.ccw(fp) for fp in AR.flight_footprints(site)]
    terrain = site.get("terrain")
    if terrain:
        gz = (lambda x, y: S.ground_z(terrain, x, y))
        for pf in site.get("platforms") or []:
            fl = GR.down_flight(pf, gz) if pf.get("steps_dir") != "up" else None
            if fl is not None:
                o = fl["out"]
                keep.append(GR._rect(fl["mid"], o, -LANDING_CLEAR_M, 0.0, float(fl["half_w"]) + 0.3))
            up = pf.get("flight")
            if isinstance(up, dict) and up.get("mid") and up.get("out"):
                # the flight up out of a sunken deck starts on the deck: its foot stays free
                # (UL162: an inward flight's foot lies its length in from the edge)
                foot = LANDING_CLEAR_M + (float(up.get("length") or 0.0) if up.get("inward") else 0.0)
                keep.append(GR._rect(up["mid"], up["out"], -foot, 0.0, float(up.get("half_w") or 0.6) + 0.3))
    for poly in [site.get("outline") or []] + list(site.get("copy_holes") or []):
        if len(poly) >= 3:
            keep.append(geom2d.ccw(poly))
    return [k for k in keep if len(k) >= 3]


def _edges_by_length(poly) -> list[int]:
    n = len(poly)
    lens = [G.distance(poly[i], poly[(i + 1) % n]) for i in range(n)]
    longest = max(lens) if lens else 0.0
    order = sorted(range(n), key=lambda i: -lens[i])
    return [i for i in order if lens[i] >= 0.5 * longest and lens[i] >= 1.5]


def _house_point(site: dict, near=None):
    """The centre of the house (or, with ``near``, of the building nearest that point: the copies count)."""
    polys = [p for p in [site.get("outline") or []] + list(site.get("copy_holes") or []) if len(p) >= 3]
    if not polys:
        return None
    cents = [G.polygon_centroid([tuple(map(float, q[:2])) for q in p]) for p in polys]
    if near is None:
        return cents[0]
    return min(cents, key=lambda c: G.distance(c, near))


def plan_ladder(pool: dict, deck: dict, keep: Sequence, house=None) -> Optional[dict]:
    """The ladder of one pool (pure; module docstring), or None when no long side has the deck for it."""
    from wenart.blender import site as S

    poly = geom2d.ccw([(float(p[0]), float(p[1])) for p in pool["polygon"]])
    n = len(poly)
    cop = S.POOL_COPING_M
    longs = _edges_by_length(poly)
    # a long side first; a short side (an end) when no long side has the deck for it
    for i in longs + sorted((j for j in range(n) if j not in longs),
                            key=lambda j: -G.distance(poly[j], poly[(j + 1) % n])):
        a, b = poly[i], poly[(i + 1) % n]
        length = G.distance(a, b)
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        out = (uy, -ux)                                   # counter-clockwise pool: the right side is the deck
        ends = [LADDER["corner_m"], length - LADDER["corner_m"]]
        if house is not None:
            ends.sort(key=lambda s: G.distance((a[0] + ux * s, a[1] + uy * s), house))
        for s in ends + [length / 2.0]:
            half = LADDER["rail_gap"] / 2.0 + 0.1
            if s - half < 0.2 or s + half > length - 0.2:
                continue
            zone = _strip(a, b, out, 0.0, cop + LADDER["deck_min_m"], s - half, s + half)
            if not _on_deck(zone, {"polygon": deck["polygon"], "holes": [h for h in deck.get("holes") or []
                                                                          if not _same(h, poly)]}, keep):
                continue
            at = (a[0] + ux * s, a[1] + uy * s)
            return {"pool_id": pool["id"], "edge": i, "at": [round(at[0], 4), round(at[1], 4)],
                    "out": [round(out[0], 6), round(out[1], 6)], "along": [round(ux, 6), round(uy, 6)],
                    "deck_z": float(deck["z"]), "zone": [list(q) for q in zone],
                    "long_side": i in longs,
                    "reason": f"a stainless steel pool ladder on the {'long side' if i in longs else 'end'} (edge "
                              f"{i}) of {pool['id']}, "
                              f"{min(s, length - s):.1f} m from the corner nearest the house (the documents draw "
                              f"the pool, not its ladder; lesson UL143; inferred)"}
    return None


def _same(a, b, tol: float = 1e-3) -> bool:
    if len(a) != len(b):
        return False
    return all(min(G.distance(tuple(p[:2]), tuple(q[:2])) for q in b) < tol for p in a)


def plan_seating(pool: dict, deck: dict, keep: Sequence, ladder: Optional[dict] = None) -> tuple[Optional[dict], str]:
    """The seating of one pool's deck (pure; module docstring): ``(seating, reason)``; ``seating`` is
    ``{"set", "edge", "pieces": [{"type", "center", "size", "height", "rotation_deg", "front_deg"}], "reason"}`` or
    None (the reason says why)."""
    from wenart.blender import site as S

    poly = geom2d.ccw([(float(p[0]), float(p[1])) for p in pool["polygon"]])
    n = len(poly)
    d0 = S.POOL_COPING_M + WALKWAY_M
    keep = list(keep) + ([ladder["zone"]] if ladder else [])
    deck_in = {"polygon": deck["polygon"], "holes": list(deck.get("holes") or [])}
    order = _edges_by_length(poly) + [i for i in range(n) if i not in _edges_by_length(poly)]
    for name in SET_ORDER:
        pieces = SETS[name]
        width = sum(w for _t, (w, _d), _h in pieces) + GAP_M * (len(pieces) - 1)
        depth = max(d for _t, (_w, d), _h in pieces)
        for i in order:
            a, b = poly[i], poly[(i + 1) % n]
            length = G.distance(a, b)
            if length < 0.5:
                continue
            ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            out = (uy, -ux)
            k = int((length + 2.0) / SLIDE_M)
            mids = sorted((length / 2.0 + SLIDE_M * (j - k // 2) for j in range(k + 1)), key=lambda s: abs(s - length / 2.0))
            for s in mids:
                zone = _strip(a, b, out, d0, d0 + depth, s - width / 2.0, s + width / 2.0)
                if not _on_deck(zone, deck_in, keep, inset=INSET_M):
                    continue
                # facing the water: the front of each piece toward the pool (-out)
                front = math.degrees(math.atan2(-out[1], -out[0]))
                rot = front - 270.0            # the piece frame's front is -Y: rotation that turns -Y to `front`
                placed, x = [], s - width / 2.0
                for typ, (w, d), h in pieces:
                    # a side table stands by the seats' backs (in reach of someone lying or sitting there)
                    c_s = x + w / 2.0
                    c_d = d0 + (max(d / 2.0, depth - d / 2.0 - 0.3) if typ == "side_table" else d / 2.0)
                    cx, cy = a[0] + ux * c_s + out[0] * c_d, a[1] + uy * c_s + out[1] * c_d
                    placed.append({"type": typ, "center": [round(cx, 4), round(cy, 4)], "size": [w, d],
                                   "height": h, "rotation_deg": round(rot % 360.0, 3),
                                   "front_deg": round(front % 360.0, 3)})
                    x += w + GAP_M
                why = (f"{'two sun loungers' if name == 'loungers' else 'a pair of outdoor lounge chairs'} and a side "
                       f"table along edge {i} of {pool['id']}, facing the water, {WALKWAY_M:.1f} m of deck kept free "
                       f"along the coping (lesson UL143; added_by_ai; inferred)")
                return {"set": name, "edge": i, "pieces": placed, "zone": [list(q) for q in zone], "reason": why}, why
    return None, (f"the deck of {pool['id']} has no strip of {WALKWAY_M:.1f} m walkway plus a lounge chair's depth "
                  f"clear of its flights, guards and the house: no seating (lesson UL143)")


def plan(site: dict) -> list[dict]:
    """The ladder and seating of every built pool of a site plan (pure; module docstring)."""
    out = []
    for pool in site.get("pools") or []:
        if len(pool.get("polygon") or []) < 3:
            continue
        house = _house_point(site, G.polygon_centroid([tuple(map(float, q[:2])) for q in pool["polygon"]]))
        deck = _deck(site, pool)
        if deck is None:
            out.append({"pool_id": pool["id"], "deck_id": None, "deck_z": None, "ladder": None, "seating": None,
                        "notes": ["no deck platform around the pool: no ladder or seating placed"]})
            continue
        keep = keep_outs(site, deck)
        ladder = plan_ladder(pool, deck, keep, house)
        seating, why = plan_seating(pool, deck, keep, ladder)
        notes = [] if ladder else [f"no long side of {pool['id']} has {LADDER['deck_min_m']:.1f} m of deck for a "
                                   f"ladder clear of the flights"]
        if seating is None:
            notes.append(why)
        out.append({"pool_id": pool["id"], "deck_id": deck["id"], "deck_z": float(deck["z"]), "ladder": ladder,
                    "seating": seating, "notes": notes})
    return out


# --------------------------------------------------------------------------
# Meshes (pure)
# --------------------------------------------------------------------------

def tube(p: Sequence[float], q: Sequence[float], r: float, sides: int = 10) -> tuple[list, list]:
    """A round tube of radius ``r`` from ``p`` to ``q`` (3D; pure): ``sides`` faces around, open ends capped."""
    d = [q[k] - p[k] for k in range(3)]
    length = math.sqrt(sum(v * v for v in d))
    if length < 1e-9:
        return [], []
    w = [v / length for v in d]
    a = (0.0, 0.0, 1.0) if abs(w[2]) < 0.9 else (1.0, 0.0, 0.0)
    u = [a[1] * w[2] - a[2] * w[1], a[2] * w[0] - a[0] * w[2], a[0] * w[1] - a[1] * w[0]]
    lu = math.sqrt(sum(v * v for v in u))
    u = [v / lu for v in u]
    v2 = [w[1] * u[2] - w[2] * u[1], w[2] * u[0] - w[0] * u[2], w[0] * u[1] - w[1] * u[0]]
    verts = []
    for c in (p, q):
        for k in range(sides):
            ang = 2.0 * math.pi * k / sides
            verts.append(tuple(c[m] + r * (math.cos(ang) * u[m] + math.sin(ang) * v2[m]) for m in range(3)))
    faces = [[k, (k + 1) % sides, sides + (k + 1) % sides, sides + k] for k in range(sides)]
    faces.append(list(reversed(range(sides))))
    faces.append(list(range(sides, 2 * sides)))
    return verts, faces


def rail_profile(deck_z: float) -> list[tuple[float, float]]:
    """A ladder handrail in its plane (pure): ``(d, z)`` with ``d`` out from the pool's inner wall onto the deck
    (negative over the water): the deck anchor ``anchor`` back, up to ``rise`` over the deck, the bend over the
    coping, down into the water ``in_wall`` off the wall to ``down`` under the deck, and back to a bumper on the wall."""
    L = LADDER
    top = deck_z + L["rise"]
    rad = (L["anchor"] + L["in_wall"]) / 2.0               # the bend: a half circle over the coping
    cx, zc = (L["anchor"] - L["in_wall"]) / 2.0, top - rad
    pts = [(L["anchor"], deck_z)]
    for k in range(0, 9):
        ang = math.pi * k / 8.0
        pts.append((cx + rad * math.cos(ang), zc + rad * math.sin(ang)))
    pts.append((-L["in_wall"], deck_z - L["down"]))
    pts.append((-0.02, deck_z - L["down"] - 0.05))       # the bumper on the pool's wall
    return pts


def ladder_meshes(ladder: dict) -> dict:
    """``{"rails": [(verts, faces)], "treads": [(verts, faces)]}`` of a planned ladder (pure): two round handrails
    ``rail_gap`` apart along the pool's side following ``rail_profile`` and ``treads`` flat treads between them in the
    water, ``tread_pitch`` apart from ``first_tread`` under the deck."""
    L = LADDER
    at, out, along = ladder["at"], ladder["out"], ladder["along"]
    z = float(ladder["deck_z"])
    prof = rail_profile(z)
    rails, treads = [], []
    for sg in (-1.0, 1.0):
        off = sg * L["rail_gap"] / 2.0
        pts = [(at[0] + along[0] * off + out[0] * d, at[1] + along[1] * off + out[1] * d, zz) for d, zz in prof]
        for p, q in zip(pts, pts[1:]):
            v, f = tube(p, q, L["tube_r"])
            if f:
                rails.append((v, f))
    for k in range(L["treads"]):
        zt = z - L["first_tread"] - k * L["tread_pitch"]
        d = -L["in_wall"]
        c = (at[0] + out[0] * (d + L["tread_d"] / 2.0 - 0.02), at[1] + out[1] * (d + L["tread_d"] / 2.0 - 0.02))
        ang = math.degrees(math.atan2(along[1], along[0]))
        treads.append(geom2d.box((c[0], c[1], zt - L["tread_t"] / 2.0), (L["rail_gap"], L["tread_d"], L["tread_t"]),
                                 ang))
    return {"rails": rails, "treads": treads}


def _local_box(c, rot: float, x: float, y: float, z0: float, w: float, d: float, h: float, tilt_to=None):
    """A box ``w`` x ``d`` x ``h`` at ``(x, y)`` of a piece's frame (front -Y) placed at ``c`` turned ``rot``."""
    r = math.radians(rot)
    cx = c[0] + math.cos(r) * x - math.sin(r) * y
    cy = c[1] + math.sin(r) * x + math.cos(r) * y
    return geom2d.box((cx, cy, z0 + h / 2.0), (w, d, h), rot)


def seat_meshes(piece: dict, z: float) -> dict:
    """``{"frame", "metal", "cushion"}`` mesh lists of a parametric outdoor piece on the deck at ``z`` (pure; real
    proportions): a sun lounger (a teak slatted bed 0.32 m high on four legs, its back raised at the head, a 6 cm
    cushion), a lounge chair (a teak frame, low seat and back cushions), a side table (a teak top on steel legs)."""
    c, rot = piece["center"], float(piece["rotation_deg"])
    w, d = piece["size"]
    out = {"frame": [], "metal": [], "cushion": []}
    if piece["type"] == "sun_lounger":
        leg = 0.05
        for sx in (-1, 1):
            for sy in (-1, 1):
                out["metal"].append(_local_box(c, rot, sx * (w / 2 - 0.06), sy * (d / 2 - 0.08), z, leg, leg, 0.27))
        # the bed: the front (foot, -Y) part flat, the head (+Y) part raised
        flat = d * 0.62
        out["frame"].append(_local_box(c, rot, 0.0, -d / 2 + flat / 2, z + 0.27, w, flat, 0.05))
        out["cushion"].append(_local_box(c, rot, 0.0, -d / 2 + flat / 2, z + 0.32, w - 0.04, flat - 0.02, 0.06))
        # the back rest: a box tilted by raising its far vertices (a sloped prism)
        y0, y1 = -d / 2 + flat, d / 2
        for part, zb, th, inset in (("frame", z + 0.27, 0.05, 0.0), ("cushion", z + 0.32, 0.06, 0.02)):
            corners = [(-w / 2 + inset, y0), (w / 2 - inset, y0), (w / 2 - inset, y1 - 0.02), (-w / 2 + inset, y1 - 0.02)]
            r = math.radians(rot)
            xy = [(c[0] + math.cos(r) * x - math.sin(r) * y, c[1] + math.sin(r) * x + math.cos(r) * y)
                  for x, y in corners]
            rise = [0.0, 0.0, 0.40, 0.40]
            verts = [(p[0], p[1], zb + dz) for p, dz in zip(xy, rise)] + \
                    [(p[0], p[1], zb + dz + th) for p, dz in zip(xy, rise)]
            faces = [[3, 2, 1, 0], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
            out[part].append((verts, faces))
    elif piece["type"] == "lounge_chair":
        for sx in (-1, 1):
            out["frame"].append(_local_box(c, rot, sx * (w / 2 - 0.04), 0.0, z, 0.08, d, 0.58))     # the arms
        out["frame"].append(_local_box(c, rot, 0.0, 0.0, z + 0.18, w - 0.16, d - 0.04, 0.06))        # the seat frame
        out["frame"].append(_local_box(c, rot, 0.0, d / 2 - 0.05, z + 0.18, w - 0.16, 0.08, 0.58))   # the back frame
        out["cushion"].append(_local_box(c, rot, 0.0, -0.04, z + 0.24, w - 0.18, d - 0.14, 0.12))
        out["cushion"].append(_local_box(c, rot, 0.0, d / 2 - 0.16, z + 0.36, w - 0.18, 0.14, 0.40))
    else:                                                   # side table
        for sx in (-1, 1):
            for sy in (-1, 1):
                out["metal"].append(_local_box(c, rot, sx * (w / 2 - 0.04), sy * (d / 2 - 0.04), z, 0.03, 0.03,
                                               piece["height"] - 0.03))
        out["frame"].append(_local_box(c, rot, 0.0, 0.0, z + piece["height"] - 0.03, w, d, 0.03))
    return out


# --------------------------------------------------------------------------
# Library models made for outside (pure)
# --------------------------------------------------------------------------

LIBRARY_TYPES = {"sun_lounger": ("chaise",), "lounge_chair": ("armchair",), "side_table": ("side_table",)}
FIT_RATIO = {"side_table": 1.5}   # a small garden stool serves as the loungers' side table
_CATALOGUE: dict = {}


def library_entries() -> list[dict]:
    """The catalogue's entries of the pool pieces' library types (``LIBRARY_TYPES``; read once; [] without it)."""
    if "entries" not in _CATALOGUE:
        import json
        from pathlib import Path

        types = {t for ts in LIBRARY_TYPES.values() for t in ts}
        try:
            data = json.loads((Path(__file__).resolve().parents[1] / "furniture" / "catalog_library.json")
                              .read_text(encoding="utf-8"))
            _CATALOGUE["entries"] = [e for key in ("entries", "decor", "extras") for e in data.get(key) or []
                                     if isinstance(e, dict) and e.get("type") in types]
        except (OSError, ValueError):
            _CATALOGUE["entries"] = []
    return list(_CATALOGUE["entries"])


def library_seat(piece_type: str, entries: Sequence[dict], mode: str = "relaxed") -> Optional[dict]:
    """The audited library model made for outside for a pool piece (pure): an entry of the piece's library types
    (``LIBRARY_TYPES``) that ``site_models.usable`` keeps and ``outdoor.outdoor_ready`` accepts, whose box fits the
    piece's size within 35 %; the best fit first, then the id. None: the parametric piece (a library gap)."""
    from wenart.blender import outdoor as OD
    from wenart.blender import site_models as SM

    want = {t: s for t, (_n, s, _h) in ((p[0], p) for p in SETS["loungers"] + SETS["chairs"])}
    size = want.get(piece_type)
    best = None
    for e in entries:
        if e.get("type") not in LIBRARY_TYPES.get(piece_type, ()) or not SM.usable(e, mode) or not e.get("textured"):
            continue
        ok, _why = OD.outdoor_ready(e, e.get("type"))
        box = e.get("bbox_m") or []
        if not ok or len(box) < 3 or size is None:
            continue
        w, d = float(box[0]), float(box[1])
        err = max(abs(math.log(w / size[0])), abs(math.log(d / size[1]))) if min(w, d) > 0 else 9.0
        if err > math.log(FIT_RATIO.get(piece_type, 1.35)):
            continue
        key = (round(err, 4), str(e.get("id")))
        if best is None or key < best[0]:
            best = (key, e)
    return best[1] if best else None


# --------------------------------------------------------------------------
# Review: rule G11 of the model review's M15
# --------------------------------------------------------------------------

def review(site: Optional[dict], manifest: Optional[dict] = None) -> tuple[list[dict], int]:
    """G11 (pure): every built pool has a ladder, and a deck with room for seating has some; on the scene manifest's
    objects when there is one (``site_part`` ``pool_ladder`` / ``pool_seat`` with their ``pool_id``), else on the
    plan. ``(findings, checked)``."""
    from wenart.blender import grading as GR

    if not site:
        return [], 0
    plans = plan(site)
    objs = (manifest or {}).get("objects") if manifest else None
    findings, checked = [], 0
    for rec in plans:
        if rec["deck_id"] is None:
            continue
        checked += 1
        pid = rec["pool_id"]
        if objs is not None:
            has_ladder = any(o.get("site_part") == "pool_ladder" and o.get("pool_id") == pid for o in objs)
            has_seat = any(o.get("site_part") == "pool_seat" and o.get("pool_id") == pid for o in objs)
        else:
            has_ladder, has_seat = rec["ladder"] is not None, rec["seating"] is not None
        if not has_ladder:
            findings.append(GR._f("major", pid, f"pool {pid} has no ladder into the water (every pool gets a "
                                  f"stainless steel ladder on a long side near the house)", CHECK_RULE, "no_sense",
                                  lesson="UL143"))
        if not has_seat and rec["seating"] is not None:
            findings.append(GR._f("minor", pid, f"the deck {rec['deck_id']} of pool {pid} has room for "
                                  f"{'two sun loungers' if rec['seating']['set'] == 'loungers' else 'two lounge chairs'}"
                                  f" and a side table facing the water, and has no seating", CHECK_RULE, "taste",
                                  lesson="UL143"))
    return findings, checked
