"""A storey that reuses another storey's plan is checked against the section (27 Nov 2026, audit fix round 5b, rule R22).

What: ``apply(build)`` runs at the end of the reading (``wenart.ingest.pipeline.run_project``). A copied storey is one the
documents do not draw: the typical plan stands for it (``typical.inferred`` of the sheets' levels, the ground floor of
``ground_from_typical``, the storeys ``storeys.inferred`` counts). For each, the section the heights were read from
(``heights.section_evidence``, ``wenart.sheets.section_evidence``) is compared with the same section at a drawn storey of
the same plan:

1. a double-height space: a stretch of at least ``GAP_MIN_M`` where the copy's floor slab is not drawn but the drawn
   storey's is, and the slab above the copy is drawn (a space closed above, not the sky): the rooms of the copy the cut
   line crosses there (at least ``ROOM_INSIDE_SHARE`` of their chord on the cut inside the stretch) are not built:
   their floor becomes a void of the slab under the copy (kind ``void``, the room below gets the double height: the build
   cuts the ceiling under it and guards the free edges), their furniture and fixed equipment go, and so do the openings
   on their walls (a door would open onto the drop, a window onto the hall);
2. a stair of the copy that the cut line crosses, where the section draws no stair in the copy's storey
   (``STAIR_EMPTY_SHARE`` of the strokes the drawn storeys draw there, at least ``STAIR_STROKES_MIN`` of them), is not
   built (``build: false``): its drawn flights start on a higher floor.

Everything is logged (warnings, a listed conflict per storey, ``level_inference.typical_checks``). It acts only where the
section clearly says so: a known cut line (its place and the way it is seen), a section width that fits the building at
the cut within ``WIDTH_TOL_M``, bands at the two storeys' floors. Otherwise it records why it did not check.

Why: real10 (finding F02): its ground floor reuses the typical plan; section A-A draws the +2.50 slab stopping at the core
landing, a double-height entrance hall south of it up to the +5.50 slab, and the escape stair starting on +5.50; the
model built the escape stair from the ground floor, a slab over the hall, a 2.55 m facade window and two kitchen windows.

How: pure geometry (shapely) on the building JSON and the section evidence; no AI.
"""
from __future__ import annotations

from typing import Optional

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

GAP_MIN_M = 2.0              # a missing slab stretch shorter than this is a stair well, a duct or a drawing gap
SLAB_PIECE_MIN_M = 0.6       # a line piece shorter than this on a band's line is a lintel, an edge or a canopy, no slab
ROOM_INSIDE_SHARE = 0.7      # a room is over the double-height space when this share of its chord on the cut is inside
ABOVE_COVER_SHARE = 0.8      # the slab above the copy covers this share of the stretch (a space closed above)
BAND_Z_TOL_M = 0.20          # a band is a storey's floor when its top lies this close to the storey's floor
WIDTH_TOL_M = 1.5            # the section's width and the building's extent at the cut agree within this (or 10 %)
OPENING_REACH_M = 0.40       # an opening this close to a dropped room's outline is one of its walls'
STAIR_STROKES_MIN = 8        # the drawn storeys draw at least this many strokes where the stair is cut ...
STAIR_EMPTY_SHARE = 0.2      # ... and the copy's storey at most this share of them: no stair drawn there
RULE = "typical_vs_section"
# 27 Nov 2026 (round 5b; the score gate: real10's ground floor copies the typical plan, and a correction of the user of
# 4 Nov asks for the fire escape stair and its door on that storey, where the section draws a double-height hall): what
# the section says against a copied storey is listed for the user and the architect, not carried out, until the user
# decides which wins (``ACT``; ``check(..., act=True)`` carries it out)
ACT = False


def _union(spans: list) -> list:
    out: list = []
    for a, b in sorted((float(a), float(b)) for a, b in spans if b > a):
        if out and a <= out[-1][1] + 1e-9:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def gaps(band: dict, width: float) -> list:
    """The stretches of ``[0, width]`` neither line of ``band`` covers (pure)."""
    cov = [c for c in _union(list(band.get("cover_top") or []) + list(band.get("cover_bottom") or []))
           if c[1] - c[0] >= SLAB_PIECE_MIN_M]
    out, at = [], 0.0
    for a, b in cov:
        if a > at:
            out.append([at, min(a, width)])
        at = max(at, b)
    if at < width:
        out.append([at, width])
    return [[a, b] for a, b in out if b > a]


def minus(spans: list, cut: list) -> list:
    """``spans`` without ``cut`` (pure; both lists of [a, b])."""
    out = [list(s) for s in spans]
    for c0, c1 in cut:
        nxt = []
        for a, b in out:
            if c1 <= a or c0 >= b:
                nxt.append([a, b])
                continue
            if c0 > a:
                nxt.append([a, c0])
            if c1 < b:
                nxt.append([c1, b])
        out = nxt
    return out


def covered_share(band: dict, a: float, b: float) -> float:
    cov = _union(list(band.get("cover_top") or []) + list(band.get("cover_bottom") or []))
    hit = sum(max(0.0, min(b, y) - max(a, x)) for x, y in cov)
    return hit / (b - a) if b > a else 0.0


def copied_levels(sheets: dict) -> dict:
    """``{copy level id: drawn level id of the same plan}`` (pure): the storeys no plan draws and the nearest drawn storey
    (above first) the same plan stands for."""
    levels = sheets.get("levels") or []
    order = {lv["id"]: lv.get("order") for lv in levels}
    out = {}
    for lv in levels:
        typ = lv.get("typical") or {}
        group = list(typ.get("levels") or typ.get("ids") or [])
        inferred = set(typ.get("inferred") or [])
        drawn = [x for x in group if x not in inferred]
        for c in inferred:
            if c in order and drawn:
                out[c] = min(drawn, key=lambda d: (abs((order.get(d) or 0) - (order.get(c) or 0)),
                                                   (order.get(d) or 0) < (order.get(c) or 0)))
    for rec in (sheets.get("storeys") or {}).get("inferred") or []:
        c = rec.get("level_id")
        region = rec.get("copy_of_region")
        if not c or c in out:
            continue
        drawn = [lv["id"] for lv in levels if lv.get("base_region") == region and lv["id"] != c
                 and c not in set((lv.get("typical") or {}).get("inferred") or [])]
        if drawn:
            out[c] = min(drawn, key=lambda d: abs((order.get(d) or 0) - (order.get(c) or 0)))
    return out


def _poly(points) -> Optional[Polygon]:
    if not points or len(points) < 3:
        return None
    p = Polygon(points)
    p = p if p.is_valid else p.buffer(0)
    return p if not p.is_empty and p.area > 0 else None


def _outline_extent(b: dict, axis: str, across: float) -> Optional[tuple]:
    """The building's extent along ``axis`` on the line ``across`` (every level's outline), or None."""
    from wenart.levels import model as LMO
    polys = []
    for lv in b.get("levels") or []:
        p = _poly(LMO.level_outline(b, lv["id"]))
        if p is not None:
            polys.append(p)
    if not polys:
        return None
    u = unary_union(polys)
    big = 1e4
    line = LineString([(across, -big), (across, big)]) if axis == "y" else LineString([(-big, across), (big, across)])
    hit = u.intersection(line)
    if hit.is_empty:
        return None
    k = 1 if axis == "y" else 0
    vals = [c[k] for c in getattr(hit, "coords", [])] if hit.geom_type == "LineString" else \
        [c[k] for g in getattr(hit, "geoms", []) for c in getattr(g, "coords", [])]
    return (min(vals), max(vals)) if vals else None


def _band_at(ev: dict, z: float) -> Optional[dict]:
    best = min(ev.get("bands") or [], key=lambda bd: abs(float(bd["z"]) - z), default=None)
    return best if best is not None and abs(float(best["z"]) - z) <= BAND_Z_TOL_M else None


def _storey_at(ev: dict, z: float) -> Optional[dict]:
    best = min(ev.get("storeys") or [], key=lambda st: abs(float(st["z_floor"]) - z), default=None)
    return best if best is not None and abs(float(best["z_floor"]) - z) <= BAND_Z_TOL_M else None


class Frame:
    """Section s (metres from its left outer wall) <-> the building axis along the cut (centre-anchored, flipped)."""

    def __init__(self, axis: str, flipped: bool, width: float, extent: tuple, ends: Optional[list], at: float):
        self.axis, self.flipped, self.width = axis, bool(flipped), float(width)
        self.u_c = (extent[0] + extent[1]) / 2.0
        self.ends, self.at = ends, float(at)

    def u(self, s: float) -> float:
        d = float(s) - self.width / 2.0
        return self.u_c - d if self.flipped else self.u_c + d

    def s(self, u: float) -> float:
        d = float(u) - self.u_c
        return self.width / 2.0 - d if self.flipped else self.width / 2.0 + d

    def across(self, u: float) -> float:
        """The cut's place across the axis at ``u`` (a jogged cut: the place of its mark on that side)."""
        if not self.ends:
            return self.at
        return min(self.ends, key=lambda e: abs(float(e[0]) - u))[1]

    def line(self, u0: float, u1: float) -> LineString:
        x = self.across((u0 + u1) / 2.0)
        return LineString([(x, u0), (x, u1)]) if self.axis == "y" else LineString([(u0, x), (u1, x)])


def frame_of(b: dict, ev: dict, shift: tuple) -> tuple[Optional[Frame], str]:
    """The section's frame in the building (``Frame``) and a note, or (None, why not)."""
    cut = ev.get("cut") or {}
    if cut.get("axis") not in ("x", "y") or cut.get("at") is None or cut.get("flipped") is None:
        return None, "no cut line with a known way of seeing it on the plans"
    k = 0 if cut["axis"] == "y" else 1                       # the across coordinate's index
    at = float(cut["at"]) - float(shift[k])
    ends = None
    if cut.get("ends"):
        ends = [[float(e[0]) - float(shift[1 - k]), float(e[1]) - float(shift[k])] for e in cut["ends"]]
    ext = _outline_extent(b, cut["axis"], at)
    if ext is None:
        return None, f"the cut line at {at:.2f} m crosses no level outline"
    width = float(ev.get("s_width") or 0.0)
    length = ext[1] - ext[0]
    if abs(length - width) > max(WIDTH_TOL_M, 0.1 * length):
        return None, (f"the section is {width:.2f} m wide, the building {length:.2f} m along the cut: the section's "
                      f"stretches cannot be placed")
    return Frame(cut["axis"], cut["flipped"], width, ext, ends, at), (
        f"cut along {cut['axis']} at {at:.2f} m" + (" (jogged)" if ends else "") + f", seen "
        f"{'flipped' if cut['flipped'] else 'as drawn'}; section {width:.2f} m, building {length:.2f} m at the cut")


def _chord_share(room: Polygon, fr: Frame, u0: float, u1: float) -> float:
    big = 1e4
    x = fr.across((u0 + u1) / 2.0)
    full = LineString([(x, -big), (x, big)]) if fr.axis == "y" else LineString([(-big, x), (big, x)])
    chord = room.intersection(full)
    if chord.is_empty or chord.length <= 0:
        return 0.0
    return chord.intersection(fr.line(u0, u1).buffer(1e-6)).length / chord.length


def _drop_room(b: dict, room: dict, slab: Optional[dict], reason: str, evidence: dict) -> dict:
    """Removes ``room`` and what stands in it or on its walls (in place); its outline becomes a void of ``slab``."""
    lid = room["level_id"]
    poly = _poly(room.get("polygon"))
    gone_f = [f["id"] for f in b.get("furniture") or [] if f.get("level_id") == lid and (
        f.get("room_id") == room["id"] or (poly is not None and (f.get("footprint") or {}).get("center") is not None
                                           and poly.contains(Point(f["footprint"]["center"]))))]
    reach = poly.buffer(OPENING_REACH_M) if poly is not None else None
    gone_o = [o["id"] for o in b.get("openings") or [] if o.get("level_id") == lid and reach is not None
              and o.get("center") is not None and reach.contains(Point(o["center"][:2]))]
    inner = poly.buffer(-0.05) if poly is not None else None
    gone_w = [w["id"] for w in b.get("walls") or [] if w.get("level_id") == lid and inner is not None
              and not inner.is_empty and w.get("start") and w.get("end")
              and inner.contains(Point(w["start"][:2])) and inner.contains(Point(w["end"][:2]))]
    b["furniture"] = [f for f in b.get("furniture") or [] if f["id"] not in set(gone_f)]
    b["openings"] = [o for o in b.get("openings") or [] if o["id"] not in set(gone_o)]
    b["walls"] = [w for w in b.get("walls") or [] if w["id"] not in set(gone_w)]
    b["rooms"] = [r for r in b.get("rooms") or [] if r["id"] != room["id"]]
    void = None
    if slab is not None and poly is not None:
        clip = poly
        out = _poly(slab.get("outline"))
        if out is not None:
            clip = poly.intersection(out)
        if clip.geom_type == "Polygon" and clip.area > 0.05:
            pts = [[round(x, 4) + 0.0, round(y, 4) + 0.0] for x, y in list(clip.exterior.coords)[:-1]]
            void = {"id": f"sv_{slab['id'][3:]}_{len(slab.get('openings') or []) + 1:03d}", "kind": "void",
                    "room_id": None, "polygon": pts, "source": "derived", "reason": reason,
                    "entity": evidence.get("region_id"), "rule": RULE}
            slab.setdefault("openings", []).append(void)
    return {"room": room["id"], "label": room.get("label"), "furniture": gone_f, "openings": gone_o, "walls": gone_w,
            "void": void["id"] if void else None, "void_m2": round(_poly(void["polygon"]).area, 2) if void else 0.0}


def check(b: dict, sheets: dict, shift: tuple = (0.0, 0.0), act: bool = True) -> dict:
    """The checks of every copied storey (module docstring; changes ``b`` in place when ``act``, else it only lists what
    the section says: ``"acted": False``). Returns ``{"checked": [...], "dropped": [...], "stairs": [...], "notes":
    [...], "acted"}``."""
    rec = {"checked": [], "dropped": [], "stairs": [], "notes": [], "acted": bool(act)}
    copies = copied_levels(sheets)
    if not copies:
        return rec
    ev = (sheets.get("heights") or {}).get("section_evidence")
    if not ev:
        rec["notes"].append("no section evidence: the copied storeys " + ", ".join(sorted(copies)) + " are not "
                            "checked against a section")
        return rec
    fr, note = frame_of(b, ev, shift)
    if fr is None:
        rec["notes"].append(f"section {ev.get('region_id')}: {note}: the copied storeys "
                            + ", ".join(sorted(copies)) + " are not checked against it")
        return rec
    levels = {lv["id"]: lv for lv in b.get("levels") or []}
    by_z = sorted(levels.values(), key=lambda lv: float(lv.get("elevation") or 0.0))
    # the section's marks may point at the finished floor and its band tops at the structure: one shift for all
    diffs = sorted(float(lv.get("elevation") or 0.0) - float(bd["z"]) for lv in by_z for bd in
                   [min(ev.get("bands") or [], key=lambda x: abs(float(x["z"]) - float(lv.get("elevation") or 0.0)),
                        default=None)] if bd is not None and abs(float(bd["z"]) - float(lv.get("elevation") or 0.0)) <= 0.6)
    dz = diffs[len(diffs) // 2] if diffs else 0.0
    if dz:
        ev = dict(ev, bands=[dict(bd, z=float(bd["z"]) + dz) for bd in ev.get("bands") or []],
                  storeys=[dict(st, z_floor=float(st["z_floor"]) + dz, z_ceiling=float(st["z_ceiling"]) + dz)
                           for st in ev.get("storeys") or []])
    width = fr.width
    for cid, rid in sorted(copies.items()):
        c, r = levels.get(cid), levels.get(rid)
        if c is None or r is None:
            continue
        bc, br = _band_at(ev, float(c["elevation"])), _band_at(ev, float(r["elevation"]))
        i = by_z.index(c)
        above = by_z[i + 1] if i + 1 < len(by_z) else None
        ba = _band_at(ev, float(above["elevation"])) if above is not None else None
        item = {"level_id": cid, "drawn_level_id": rid, "section": ev.get("region_id"), "frame": note,
                "double_height": [], "stairs": []}
        rec["checked"].append(item)
        if bc is None or br is None:
            item["note"] = "no slab band at the copy's or the drawn storey's floor"
            continue
        new = [g for g in minus(gaps(bc, width), gaps(br, width)) if g[1] - g[0] >= GAP_MIN_M]
        slab = next((s for s in b.get("slabs") or [] if s.get("above_level_id") == cid and not s.get("variants")), None)
        for s0, s1 in new:
            if ba is None or covered_share(ba, s0, s1) < ABOVE_COVER_SHARE:
                item["double_height"].append({"s": [round(s0, 2), round(s1, 2)], "used": False,
                                              "why": "the slab above is not drawn over it (open to the sky?)"})
                continue
            u0, u1 = sorted((fr.u(s0), fr.u(s1)))
            entry = {"s": [round(s0, 2), round(s1, 2)], "along": [round(u0, 2), round(u1, 2)], "used": True,
                     "rooms": []}
            item["double_height"].append(entry)
            for room in [x for x in b.get("rooms") or [] if x.get("level_id") == cid]:
                poly = _poly(room.get("polygon"))
                if poly is None:
                    continue
                share = _chord_share(poly, fr, u0, u1)
                if share < ROOM_INSIDE_SHARE:
                    continue
                reason = (f"section {ev.get('region_id')} draws no floor slab at {cid} ({c.get('label')}) over "
                          f"{fr.axis} {u0:.2f}-{u1:.2f} m at the cut, while it draws {rid}'s slab there and the slab "
                          f"above: a double-height space; {cid} copies the plan of {rid}, so its room "
                          f"{room['id']} '{room.get('label')}' ({share * 100:.0f} % of it on the cut inside) is not "
                          f"built: its floor is a void over the storey below (rule {RULE})")
                if act:
                    done = _drop_room(b, room, slab, reason, {"region_id": ev.get("region_id")})
                else:
                    done = {"room": room["id"], "label": room.get("label"), "furniture": [], "openings": [],
                            "walls": [], "void": None, "void_m2": 0.0}
                done.update(level_id=cid, share=round(share, 2), reason=reason)
                entry["rooms"].append(room["id"])
                rec["dropped"].append(done)
        # 2. stairs the section does not draw in the copy's storey
        sc = _storey_at(ev, float(c["elevation"]))
        group = [rid]
        for lv in sheets.get("levels") or []:
            typ = lv.get("typical") or {}
            if cid in (typ.get("levels") or []):
                group = [x for x in typ.get("levels") or [] if x not in set(typ.get("inferred") or [])] or group
        drawn_storeys = [st for st in (_storey_at(ev, float(levels[d]["elevation"])) for d in group if d in levels)
                         if st]
        if sc is None or not drawn_storeys:
            continue
        for f in b.get("furniture") or []:
            if f.get("level_id") != cid or f.get("type") != "stair" or f.get("build") is False:
                continue
            fp = f.get("footprint") or {}
            try:
                from wenart import geometry as G
                fpoly = _poly(G.rotated_rectangle(fp["center"], fp["size"], float(fp.get("rotation_deg") or 0.0)))
            except (KeyError, TypeError, ValueError):
                fpoly = None
            if fpoly is None:
                continue
            big = 1e4
            x = fr.across(fp["center"][1] if fr.axis == "y" else fp["center"][0])
            full = LineString([(x, -big), (x, big)]) if fr.axis == "y" else LineString([(-big, x), (big, x)])
            chord = fpoly.intersection(full)
            if chord.is_empty or chord.length < 0.5:
                continue
            k = 1 if fr.axis == "y" else 0
            us = [cc[k] for cc in chord.coords] if chord.geom_type == "LineString" else \
                [cc[k] for g in chord.geoms for cc in g.coords]
            s_lo, s_hi = sorted((fr.s(min(us)), fr.s(max(us))))
            bm = float(ev.get("bin_m") or 0.25)
            keys = [str(n) for n in range(int(max(0.0, s_lo) / bm), int(min(width, s_hi) / bm) + 1)]
            mine = sum(int(sc["strokes"].get(kk, 0)) for kk in keys)
            theirs = sorted(sum(int(st["strokes"].get(kk, 0)) for kk in keys) for st in drawn_storeys)
            med = theirs[len(theirs) // 2]
            if med < STAIR_STROKES_MIN or mine > STAIR_EMPTY_SHARE * med:
                continue
            if act:
                f["build"] = False
            why = (f"section {ev.get('region_id')} draws no stair in {cid}'s storey where the cut crosses {f['id']} "
                   f"({mine} strokes against {med} in the drawn storeys of the same plan): its drawn flights start on "
                   f"a higher floor; {cid} copies that plan, the stair is not built here (rule {RULE})")
            if act:
                f.setdefault("evidence", []).append({"file": (c.get("evidence") or [{}])[0].get("file", ""),
                                                     "method": "inferred", "confidence": 0.8, "entity": f["id"],
                                                     "region_id": ev.get("region_id"), "rule": RULE, "text": why})
            item["stairs"].append(f["id"])
            rec["stairs"].append({"level_id": cid, "stair": f["id"], "strokes": mine, "drawn": med, "reason": why})
    # a stair not built here cuts no slab above it
    gone = {f for d in rec["dropped"] for f in d["furniture"]} | {s_["stair"] for s_ in rec["stairs"]}
    rec["voids_removed"] = []
    for slab in (b.get("slabs") or []) if act else []:
        keep = []
        for o in slab.get("openings") or []:
            if o.get("kind") == "stair_void" and o.get("furniture_id") in gone:
                rec["voids_removed"].append({"slab": slab.get("id"), "opening": o.get("id"),
                                             "stair": o.get("furniture_id")})
            else:
                keep.append(o)
        slab["openings"] = keep
    return rec


def apply(build) -> dict:
    """``check`` on the pipeline's building (module docstring), logged: a warning per change, a listed conflict per
    copied storey changed, the record in ``level_inference.typical_checks``."""
    b, sheets = build.building, build.sheets
    if not sheets:
        return {}
    try:
        rec = check(b, sheets, tuple(getattr(build, "frame_shift", (0.0, 0.0)) or (0.0, 0.0)), act=ACT)
    except Exception as exc:  # noqa: BLE001 - logged: the copies stay as read
        build.warn(f"copied storeys not checked against the section ({type(exc).__name__}: {exc})")
        return {}
    for n in rec["notes"]:
        build.warn(f"copied storeys: {n}")
    held = "" if rec["acted"] else " (listed, not carried out: the user decides first)"
    for d in rec["dropped"]:
        build.warn(f"copied storey {d['level_id']}: {d['reason']}{held}" + (
            f"; gone with it: furniture {', '.join(d['furniture']) or '-'}, openings {', '.join(d['openings']) or '-'}, "
            f"walls {', '.join(d['walls']) or '-'}; void {d['void'] or '-'} ({d['void_m2']:.2f} m2)" if rec["acted"]
            else ""))
    for s in rec["stairs"]:
        build.warn(f"copied storey {s['level_id']}: {s['reason']}{held}")
    for v in rec.get("voids_removed") or []:
        build.warn(f"copied storeys: the opening {v['opening']} of {v['slab']} over the stair {v['stair']} is not cut "
                   f"(the stair is not built)")
    for item in rec["checked"]:
        ids = [d["room"] for d in rec["dropped"] if d["level_id"] == item["level_id"]] + list(item["stairs"])
        if ids:
            build.conflict("other", ids, f"{item['level_id']} copies the plan of {item['drawn_level_id']}; section "
                                         f"{item['section']} draws it otherwise ({item['frame']})",
                           (f"the section wins where it clearly differs: rooms over a double-height space and stairs "
                            f"the section does not draw are not built (rule {RULE})") if rec["acted"] else
                           (f"listed, not carried out (rule {RULE}): the rooms over the double-height space and the "
                            f"stairs the section does not draw stay as the copied plan draws them until the user "
                            f"decides which wins"))
    if rec["checked"] or rec["notes"]:
        b.setdefault("level_inference", {})["typical_checks"] = rec
    return rec
