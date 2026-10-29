"""See-through wardrobes and walk-in dressing rooms (29 Oct 2026, lessons UL120, UL125; docs/reference_details_20261029.md
R1, R31, R37, D4).

The user (29 Oct 2026, a bedroom with a full-height wardrobe behind black horizontal slat sliding doors, the shirts,
shelves and drawers showing through): "look at this dressing room solution see through why we are not using some
similar in our projects?"; on real06's dressing room (two drawn wardrobe runs facing each other across a 1.2 m aisle,
closed white panel doors): "this dressing could be a see through dressing room in the both sides argus should have
think of this". Our wardrobes had closed fronts only, and no garments.

What (pure, no ``bpy`` but ``build_mirrors``): ``plan(building, style)`` -> ``{piece id: front}`` of the wardrobes
that get a see-through front, ``apply(building, style)`` writes it into the pieces (``see_through``, the design's
``see_through`` kind) and builds them from the wardrobe module builder (``modules.plan_wardrobe_run``: sliding
see-through doors, or an open run, in front of real contents), keeping the fitted library model's record
(``see_through.replaced``) so the change is never silent.

- A walk-in dressing room (``walk_in``: a dressing room, ``door_states.is_dressing``, or any room whose wardrobe runs
  face each other across an aisle of ``AISLE_M``) is see-through on every side by default; its family picks the front
  (``WALK_IN_FRONTS``: horizontal black slat sliding doors ``slats``, smoked glass in black frames ``smoked_glass``, or
  an ``open`` run of hanging rails, shelves and shoe racks); the architect's ``wardrobe_fronts`` answer
  (``architect_rules`` D8, ``room["wardrobe_fronts"]``) can change it, ``closed`` included.
- The master bedroom's widest wardrobe run gets the family's see-through front where the style has one
  (``FRONTS``: the modern, Japandi, Scandinavian, minimal, contemporary and industrial families; the period families
  keep closed fronts). Every other wardrobe keeps its closed fronts. A front needs ``MIN_WIDTH_M`` (two sliding
  panels) and ``MIN_DEPTH_M`` (a hanger across).
- The contents (``modules.see_through_parts``): a hanging rail with garments (shirts, jackets, coats, dresses, knits:
  simple cloth shapes on hangers, varied colours of the muted ``GARMENT_COLOURS``), folded stacks on shelves, drawers
  or shoe racks, an LED strip under the top; the garments of one wardrobe are part of its one mesh.
- ``walk_in_extras(building, room)``: a bench (else a pouf) on a free wall where the walkway allows (``WALKWAY_M`` free
  in front of it, clear of the wardrobes' ``ACCESS_M`` and the doors' approaches and leaves), and a full-height mirror
  on a free wall stretch (``MIRROR_M``), each recorded with its reason or why it does not fit.
"""
from __future__ import annotations

import math
from typing import Optional

from wenart import geometry as G

WARDROBE_TYPES: tuple[str, ...] = ("wardrobe",)
FRONTS: dict[str, str] = {"modern": "slats", "japandi": "slats", "scandinavian": "slats",
                          "minimal": "smoked_glass", "modern minimal": "smoked_glass", "contemporary": "smoked_glass",
                          "industrial": "smoked_glass"}
WALK_IN_FRONTS: dict[str, str] = dict(FRONTS, industrial="open", classic="open", rustic="open", mediterranean="open",
                                      traditional="open")
WALK_IN_DEFAULT = "open"
FRONT_KINDS: tuple[str, ...] = ("slats", "smoked_glass", "open")
CHOICES: tuple[str, ...] = FRONT_KINDS + ("closed",)
FRONT_WHAT = {"slats": "horizontal black slat sliding doors", "smoked_glass": "smoked glass sliding doors in black "
              "frames", "open": "an open run (hanging rails, shelves and shoe racks)", "closed": "closed fronts"}
MIN_WIDTH_M = 1.0
MIN_DEPTH_M = 0.50
AISLE_M = (0.70, 1.80)            # two runs facing each other this far apart (front to front) make a walk-in
FACING_DEG = 25.0
OVERLAP_SHARE = 0.4               # ... and overlapping along their runs by this share of the shorter one
ACCESS_M = 0.45                   # free floor in front of a sliding or open wardrobe front
WALKWAY_M = 0.60                  # free floor in front of an added bench or pouf
BENCH_M = (1.0, 0.40, 0.45)       # schemas.SIZE_OPTIONS bench, the ottoman's (pouf) 0.5 x 0.5
POUF_M = (0.50, 0.50, 0.45)
MIRROR_M = (0.60, 1.80, 0.15)     # a full-height mirror: width, height, bottom over the floor
MIRROR_FRAME_M = 0.025
MIRROR_DEPTH_M = 0.03
OPENING_MARGIN_M = 0.10
# muted garment colours (wenart/style/colours.py names), cycled by the wardrobe's own seed
GARMENT_COLOURS: tuple[str, ...] = ("white", "light grey", "navy", "charcoal", "beige", "sky blue", "sage", "camel",
                                    "taupe", "off white", "dusty blue", "olive", "black", "greige")


def family_of(style) -> str:
    if isinstance(style, str):
        return style.strip().lower()
    return str((style or {}).get("family") or "").strip().lower()


def is_see_through(piece: dict) -> bool:
    """A wardrobe built with a see-through or open front (``see_through.kind`` one of ``FRONT_KINDS``)."""
    rec = piece.get("see_through") if isinstance(piece.get("see_through"), dict) else {}
    design = piece.get("design") if isinstance(piece.get("design"), dict) else {}
    return rec.get("kind") in FRONT_KINDS or design.get("see_through") in FRONT_KINDS


def _area(room: dict) -> float:
    try:
        return abs(G.polygon_area(room.get("polygon") or []))
    except (TypeError, ValueError):
        return 0.0


def _size(piece: dict) -> tuple[float, float]:
    fp = piece.get("footprint") or {}
    s = list(fp.get("size") or [0.0, 0.0])
    return float(s[0]), float(s[1])


def front_dir(piece: dict) -> Optional[tuple[float, float]]:
    """The unit plan direction a piece's front faces (``front_deg``: 0 = +X, counter-clockwise), None without one."""
    deg = piece.get("front_deg")
    if not isinstance(deg, (int, float)) or isinstance(deg, bool):
        return None
    a = math.radians(float(deg))
    return math.cos(a), math.sin(a)


def _front_line(piece: dict) -> Optional[tuple[tuple[float, float], tuple[float, float], float]]:
    """``(front centre, front direction, half length along the front)`` of a piece."""
    d = front_dir(piece)
    fp = piece.get("footprint") or {}
    if d is None or not fp.get("center"):
        return None
    w, dep = _size(piece)
    rot = math.radians(float(fp.get("rotation_deg") or 0.0))
    ux, uy = math.cos(rot), math.sin(rot)               # the footprint's width axis
    along = abs(ux * d[0] + uy * d[1])
    half_depth, half_len = (w / 2.0, dep / 2.0) if along > 0.7 else (dep / 2.0, w / 2.0)
    c = fp["center"]
    return (float(c[0]) + d[0] * half_depth, float(c[1]) + d[1] * half_depth), d, half_len


def facing_runs(building: dict, room: dict) -> list[tuple[str, str, float]]:
    """``[(id a, id b, aisle m)]``: the wardrobe runs of ``room`` whose fronts face each other across an aisle of
    ``AISLE_M`` (pure; front directions opposite within ``FACING_DEG``, overlapping along their runs by
    ``OVERLAP_SHARE``)."""
    robes = [f for f in building.get("furniture") or [] if f.get("room_id") == room.get("id")
             and str(f.get("type")) in WARDROBE_TYPES and f.get("build", True) is not False]
    out = []
    for i, a in enumerate(robes):
        la = _front_line(a)
        for b in robes[i + 1:]:
            lb = _front_line(b)
            if la is None or lb is None:
                continue
            (pa, da, ha), (pb, db, hb) = la, lb
            if da[0] * db[0] + da[1] * db[1] > -math.cos(math.radians(FACING_DEG)):
                continue
            gap = (pb[0] - pa[0]) * da[0] + (pb[1] - pa[1]) * da[1]
            if not AISLE_M[0] - 1e-9 <= gap <= AISLE_M[1] + 1e-9:
                continue
            t = (-da[1], da[0])
            sa, sb = pa[0] * t[0] + pa[1] * t[1], pb[0] * t[0] + pb[1] * t[1]
            ov = min(sa + ha, sb + hb) - max(sa - ha, sb - hb)
            if ov >= OVERLAP_SHARE * min(2 * ha, 2 * hb) - 1e-9:
                out.append((str(a["id"]), str(b["id"]), round(gap, 3)))
    return out


def walk_in(building: dict, room: Optional[dict]) -> Optional[str]:
    """Why ``room`` is a walk-in dressing room (a dressing room, or wardrobe runs facing each other), else None."""
    from wenart.blender import door_states as DS

    if room is None:
        return None
    if DS.is_dressing(building, room):
        return "a dressing room"
    pairs = facing_runs(building, room)
    if pairs:
        a, b, gap = pairs[0]
        return f"wardrobe runs {a} and {b} face each other across a {gap:.2f} m aisle"
    return None


def walk_in_front(building: dict, room: dict, style) -> tuple[str, str]:
    """``(kind, why)`` of a walk-in's fronts: the architect's answer (``room["wardrobe_fronts"]``), else the family's
    (``WALK_IN_FRONTS``)."""
    ans = room.get("wardrobe_fronts") if isinstance(room.get("wardrobe_fronts"), dict) else {}
    if ans.get("kind") in CHOICES:
        return ans["kind"], f"the architect's answer ({ans.get('by') or 'architect'}: {ans.get('reason') or ''})"
    fam = family_of(style)
    kind = WALK_IN_FRONTS.get(fam, WALK_IN_DEFAULT)
    return kind, f"the {fam or 'house'} family's walk-in front"


# = media_wall.MASTER_WORDS / MASTER_MIN_M2 (the furniture package needs shapely; Blender loads this module alone)
MASTER_WORDS: tuple[str, ...] = ("ebeveyn", "master", "parent", "parents", "suite", "principal", "eltern",
                                 "matrimonial", "matrimoniale", "hoofdslaapkamer", "e yatak")
MASTER_MIN_M2 = 12.0


def master_bedroom(rooms) -> Optional[dict]:
    """The master bedroom: the bedroom whose label names it (``MASTER_WORDS``, Turkish folded to ASCII), else the
    largest bedroom of at least ``MASTER_MIN_M2`` that is no child's room (as ``media_wall`` picks it)."""
    from wenart import building as B

    beds = [r for r in rooms if str(r.get("room_type") or "") == "bedroom" and r.get("room_subtype") != "child"]
    for r in sorted(beds, key=lambda r: str(r.get("id"))):
        words = " " + " ".join(B.fold_ascii(str(r.get("label") or "")).lower().replace(".", " ").split()) + " "
        if any(f" {w} " in words or words.strip().startswith(w) for w in MASTER_WORDS):
            return r
    big = sorted((r for r in beds if _area(r) >= MASTER_MIN_M2 - 1e-9), key=lambda r: (-_area(r), str(r.get("id"))))
    return big[0] if big else None


def plan(building: dict, style) -> dict:
    """``{piece id: {"kind", "room_id", "reason", "walk_in"}}`` of the wardrobes that get a see-through or open front
    (module docstring)."""
    fam = family_of(style)
    if not fam:
        return {}
    rooms = {r.get("id"): r for r in building.get("rooms") or []}
    robes = [f for f in building.get("furniture") or [] if str(f.get("type")) in WARDROBE_TYPES
             and f.get("build", True) is not False and f.get("room_id") in rooms]
    out: dict = {}

    def fits(f) -> Optional[str]:
        w, d = _size(f)
        if w < MIN_WIDTH_M - 1e-9:
            return f"{w:.2f} m wide: under the {MIN_WIDTH_M:.2f} m of two sliding panels"
        if d < MIN_DEPTH_M - 1e-9:
            return f"{d:.2f} m deep: no hanger fits across"
        return None

    walk = {rid: walk_in(building, r) for rid, r in rooms.items() if any(f["room_id"] == rid for f in robes)}
    for f in robes:
        room = rooms[f["room_id"]]
        why = walk.get(room["id"])
        if why is None or fits(f) is not None:
            continue
        kind, src = walk_in_front(building, room, style)
        if kind == "closed":
            continue
        out[f["id"]] = {"kind": kind, "room_id": room["id"], "walk_in": True,
                        "reason": f"a walk-in ({why}), see-through on every side: {FRONT_WHAT[kind]} with real "
                                  f"contents and a light inside ({src}; UL120, UL125)"}
    kind = FRONTS.get(fam)
    if kind is not None:
        master = master_bedroom(rooms.values())
        for master in [master] if master is not None else []:
            if walk.get(master["id"]):
                continue
            cands = sorted((f for f in robes if f["room_id"] == master["id"] and fits(f) is None),
                           key=lambda f: (-_size(f)[0], str(f.get("id"))))
            if cands and cands[0]["id"] not in out:
                out[cands[0]["id"]] = {"kind": kind, "room_id": master["id"], "walk_in": False,
                                       "reason": f"the master bedroom's wardrobe run ({fam} style): {FRONT_WHAT[kind]} "
                                                 "with its garments and an LED strip showing through (UL120)"}
    return out


def apply(building: dict, style) -> tuple[dict, list[dict]]:
    """Write ``plan`` into the pieces (in place): ``(plan, assumed entries)``. The piece is built by the wardrobe
    module builder (``asset.method: module``); the fitted library model it replaces stays in ``see_through.replaced``."""
    chosen = plan(building, style)
    assumed = []
    for f in building.get("furniture") or []:
        rec = chosen.get(f.get("id"))
        if rec is None:
            continue
        old = f.get("asset") if isinstance(f.get("asset"), dict) else {}
        replaced = {k: old.get(k) for k in ("asset_id", "library", "method", "licence") if old.get(k) is not None}
        f["see_through"] = dict(rec, replaced=replaced or None)
        design = dict(f.get("design") or {})
        design["see_through"] = rec["kind"]
        f["design"] = design
        w, d = _size(f)
        h = f.get("height")
        f["asset"] = {"library": "module", "method": "module", "asset_id": f"module:{f['type']}:wardrobe_run",
                      "bbox_m": [round(w, 4), round(d, 4), round(float(h), 4) if isinstance(h, (int, float)) else None],
                      "see_through": rec["kind"], "replaced": replaced or None, "reason": rec["reason"]}
        assumed.append({"object": f"furn_{f['id']}", "field": "see_through", "value": rec["kind"],
                        "reason": rec["reason"] + (f"; replaces the library model {replaced.get('asset_id')}"
                                                   if replaced.get("asset_id") else ""),
                        "parent": f["id"], "kind": "see_through_front"})
    return chosen, assumed


# ---------------------------------------------------------------------------------------- walk-in bench and mirror

def _edges(room: dict) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    poly = [tuple(p[:2]) for p in room.get("polygon") or []]
    if len(poly) > 1 and G.distance(poly[0], poly[-1]) < 1e-9:
        poly = poly[:-1]
    if G.polygon_area(poly) < 0:
        poly = poly[::-1]                                 # counter-clockwise: the inward normal is the left one
    return [(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))]


def _openings_on(building: dict, room: dict, a, b) -> list[tuple[float, float]]:
    """``[(t0, t1)]`` along the edge ``a`` -> ``b`` taken by the doors, windows and openings on it (with margins)."""
    length = G.distance(a, b)
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    out = []
    for o in building.get("openings") or []:
        if o.get("level_id") != room.get("level_id") or not o.get("center"):
            continue
        c = o["center"]
        if G.point_segment_distance(c, a, b) > 0.35:
            continue
        t = (float(c[0]) - a[0]) * ux + (float(c[1]) - a[1]) * uy
        h = float(o.get("width") or 0.0) / 2.0 + OPENING_MARGIN_M
        out.append((t - h, t + h))
    return out


def _free_stretches(building: dict, room: dict, a, b, pieces, depth: float) -> list[tuple[float, float]]:
    """The stretches of the edge ``a`` -> ``b`` with no opening and no piece within ``depth`` of the wall."""
    length = G.distance(a, b)
    if length < 0.3:
        return []
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    nx, ny = -uy, ux
    taken = list(_openings_on(building, room, a, b))
    for _pid, _t, poly in pieces:
        ts = [((p[0] - a[0]) * ux + (p[1] - a[1]) * uy, (p[0] - a[0]) * nx + (p[1] - a[1]) * ny) for p in poly]
        if min(off for _t2, off in ts) <= depth:
            taken.append((min(t for t, _o in ts), max(t for t, _o in ts)))
    taken.sort()
    out, cur = [], 0.0
    for t0, t1 in taken:
        if t0 > cur:
            out.append((cur, min(t0, length)))
        cur = max(cur, t1)
    if cur < length:
        out.append((cur, length))
    return [(max(0.0, x0), min(length, x1)) for x0, x1 in out if min(length, x1) - max(0.0, x0) > 1e-6]


def walk_in_extras(building: dict, room: dict, levels: Optional[dict] = None) -> dict:
    """``{"bench": piece | None, "mirror": record | None, "notes": [...]}`` of a walk-in dressing room (pure; module
    docstring). The bench (else a pouf) stands with its back on a free wall stretch, inside the room, clear of every
    piece, of the wardrobes' ``ACCESS_M``, of the doors' approaches and open leaves, with ``WALKWAY_M`` free in front;
    the mirror hangs on another free stretch at least ``MIRROR_M`` wide where no piece stands against the wall."""
    from wenart.blender import door_states as DS

    lid = room.get("level_id")
    pieces = [p for p in DS.piece_polys(building, lid)]
    blocks = list(pieces)
    for f in building.get("furniture") or []:                    # the wardrobes' access strips
        if f.get("room_id") != room.get("id") or str(f.get("type")) not in WARDROBE_TYPES:
            continue
        line = _front_line(f)
        if line is None:
            continue
        (fx, fy), d, half = line
        t = (-d[1], d[0])
        blocks.append((f"{f['id']}:access", "access", [
            (fx + t[0] * half, fy + t[1] * half), (fx - t[0] * half, fy - t[1] * half),
            (fx - t[0] * half + d[0] * ACCESS_M, fy - t[1] * half + d[1] * ACCESS_M),
            (fx + t[0] * half + d[0] * ACCESS_M, fy + t[1] * half + d[1] * ACCESS_M)]))
    walls = {w["id"]: w for w in building.get("walls") or []}
    for o in building.get("openings") or []:                      # the doors' approaches and open leaves
        w = walls.get(o.get("wall_id"))
        if o.get("level_id") != lid or w is None or o.get("type") not in ("door", "opening") or not o.get("center"):
            continue
        fr = DS.leaf_frame(o, w)
        for s in (1.0, -1.0):
            blocks.append((f"{o['id']}:approach", "door", DS._strip(fr["c"][0], fr["c"][1], fr["u"], fr["n"],
                                                                    fr["w"] / 2.0 + 0.05, 0.75, s, fr["T"] / 2.0)))
        for poly in (o.get("leaf_state") or {}).get("leaf_polys") or []:
            blocks.append((f"{o['id']}:leaf", "door", [tuple(p) for p in poly]))
        for poly in (o.get("leaf_state") or {}).get("sweeps") or []:
            blocks.append((f"{o['id']}:sweep", "door", [tuple(p) for p in poly]))
    notes: list[str] = []
    bench = None
    edges = _edges(room)
    stretches = []
    for a, b in edges:
        for t0, t1 in _free_stretches(building, room, a, b, pieces, 0.35):
            stretches.append((t1 - t0, a, b, t0, t1))
    stretches.sort(key=lambda s: -s[0])
    used = None
    for size, ftype in ((BENCH_M, "bench"), (POUF_M, "ottoman")):
        for _len, a, b, t0, t1 in stretches:
            w, dep, h = size
            if t1 - t0 < w + 0.02:
                continue
            length = G.distance(a, b)
            ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            nx, ny = -uy, ux
            tm = (t0 + t1) / 2.0
            cx = a[0] + ux * tm + nx * (dep / 2.0 + 0.01)
            cy = a[1] + uy * tm + ny * (dep / 2.0 + 0.01)
            rot = math.degrees(math.atan2(uy, ux)) + 180.0      # the piece's front (local -Y) into the room
            poly = [tuple(p) for p in G.rotated_rectangle((cx, cy), (w, dep), rot)]
            if not all(G.point_in_polygon(p, room["polygon"]) for p in poly):
                continue
            hit = [pid for pid, _t, pp in blocks if DS.overlap(poly, pp) > DS.HIT_M2]
            if hit:
                notes.append(f"a {ftype} on the free wall at {tm:.2f} m: {', '.join(hit[:3])} in the way")
                continue
            front = (cx + nx * dep / 2.0, cy + ny * dep / 2.0)
            free = DS._ray_exit(front, (nx, ny), room["polygon"])
            for _pid, _t, pp in pieces:
                free = min(free, DS._ray_exit(front, (nx, ny), pp) if not G.point_in_polygon(front, pp) else 0.0)
            if free < WALKWAY_M - 1e-9:
                notes.append(f"a {ftype} on the free wall at {tm:.2f} m: {free:.2f} m free in front of it "
                             f"(walkway {WALKWAY_M:.2f} m)")
                continue
            bench = {"id": f"{room['id']}__walkin_{ftype}", "type": ftype, "level_id": lid, "room_id": room["id"],
                     "source": "added_by_ai", "completes_room": True, "status": "assumed",
                     "footprint": {"center": [round(cx, 4), round(cy, 4)], "size": [w, dep],
                                   "rotation_deg": round((rot) % 360.0, 3)},
                     "front_deg": round(math.degrees(math.atan2(ny, nx)) % 360.0, 3), "height": h,
                     "asset": None, "evidence": [{"file": "wardrobe_fronts", "method": "inferred", "confidence": 0.6,
                                                  "text": "walk-in dressing room: a seat to dress"}],
                     "added_by_ai": {"by": "code", "rule": "walk-in dressing room (UL125)",
                                     "reason": f"a {ftype} on the free wall, {free:.2f} m free in front of it, clear "
                                               "of the wardrobes and the doors"}}
            used = (a, b, t0, t1)
            break
        if bench is not None:
            break
    if bench is None:
        notes.append("no bench or pouf: the aisle and the free walls leave no place with the walkway free")
    mirror = None
    mw, mh, mb = MIRROR_M
    for _len, a, b, t0, t1 in stretches:
        if (a, b, t0, t1) == used and t1 - t0 < mw + BENCH_M[0] + 0.1:
            continue
        if t1 - t0 < mw + 0.04:
            continue
        length = G.distance(a, b)
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        nx, ny = -uy, ux
        tm = (t0 + t1) / 2.0 if (a, b, t0, t1) != used else t1 - mw / 2.0 - 0.02
        level = (levels or {}).get(lid) or next((lv for lv in building.get("levels") or [] if lv.get("id") == lid), {})
        top = float(level.get("ceiling_height") or 2.5) - 0.05
        mirror = {"room_id": room["id"], "level_id": lid, "centre": [round(a[0] + ux * tm + nx * MIRROR_DEPTH_M / 2.0, 4),
                                                                     round(a[1] + uy * tm + ny * MIRROR_DEPTH_M / 2.0, 4)],
                  "rotation_deg": round((math.degrees(math.atan2(uy, ux)) + 180.0) % 360.0, 3), "width": mw,
                  "height": round(min(mh, top - mb), 3), "bottom": mb,
                  "reason": "a full-height mirror on a free wall of the walk-in dressing room (UL125)"}
        break
    if mirror is None:
        notes.append(f"no full-height mirror: no free wall stretch of {mw + 0.04:.2f} m")
    return {"bench": bench, "mirror": mirror, "notes": notes}


def mirror_parts(width: float, height: float) -> list[dict]:
    """A full-height mirror in its own frame (pure; width X, depth Y, front -Y, Z up from its bottom): a slim black
    frame (``dark``) round the mirror glass (``mirror``)."""
    from wenart.blender import parametric as P

    f, d = MIRROR_FRAME_M, MIRROR_DEPTH_M
    return [P._box(-(width / 2.0 - f / 2.0), 0.0, 0.0, f, d, height, "dark", "frame"),
            P._box(width / 2.0 - f / 2.0, 0.0, 0.0, f, d, height, "dark", "frame"),
            P._box(0.0, 0.0, 0.0, width - 2 * f, d, f, "dark", "frame"),
            P._box(0.0, 0.0, height - f, width - 2 * f, d, f, "dark", "frame"),
            P._box(0.0, -d / 2.0 + 0.004, f, width - 2 * f, 0.006, height - 2 * f, "mirror", "glass"),
            P._box(0.0, d / 4.0, f, width - 2 * f, d / 2.0, height - 2 * f, "dark", "back")]


def build_mirrors(mirrors: list[dict], level: dict, collection, mats, manifest_objects: list, assumed: list) -> list:
    """The walk-in mirrors of a level (``bpy``): one mesh object per mirror (its boxes), material keys through the
    furniture materials ``mats`` (``furniture._Materials``), a design detail (status assumed, its room the parent)."""
    from wenart.blender import common
    from wenart.blender import parametric as P

    made = []
    for m in mirrors:
        if m.get("level_id") != level["id"]:
            continue
        parts = mirror_parts(float(m["width"]), float(m["height"]))
        verts, faces, keys = P.world_mesh(parts, m["centre"], float(m["rotation_deg"]),
                                          float(level["elevation"]) + float(m["bottom"]))
        used = sorted(set(keys), key=keys.index)
        slots = [mats.get(k) for k in used]
        name = f"{m['room_id']}__walkin_mirror"
        ob = common.new_mesh_object(name, verts, faces, collection=collection, wenart_id=name, kind="decor",
                                    status="assumed", materials=slots, face_material_indices=[used.index(k) for k in keys])
        made.append(ob)
        manifest_objects.append({"name": name, "wenart_id": name, "element_id": name, "kind": "decor",
                                 "type": "mirror", "level_id": level["id"], "room_id": m["room_id"],
                                 "status": "assumed", "parent": m["room_id"], "evidence": [], "host_id": None,
                                 "source": "added_by_ai", "decor_method": "rule", "method": "walk_in",
                                 "material": slots[0].name if slots else None, "textured": False, "pass_index": None,
                                 "materials": [s.name for s in slots], "size": [m["width"], MIRROR_DEPTH_M,
                                                                                m["height"]],
                                 "assumed": {"detail": "walk_in_mirror", "reason": m["reason"]}})
        assumed.append({"object": name, "field": "walk_in_mirror", "value": f"{m['width']} x {m['height']} m",
                        "reason": m["reason"], "parent": m["room_id"], "kind": "walk_in_mirror"})
    return made
