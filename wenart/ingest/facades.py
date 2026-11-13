"""The facades of each storey (12 Nov 2026; stage 2 of the building-sense audit: R45, R24 with the misfire hunters'
evidence order, R46's plot-line trigger and internal party wall).

What: ``read(b, level, lv, texts, side_points, levels_texts)`` returns the level's outline facades (its outer ring's
edges of at least ``EDGE_MIN_M``), each a dict:

- **notes** (R45): a margin text outside the outline, at most ``MARGIN_M`` from that facade's line with its foot
  within the facade, belongs to the nearest such facade: ``street`` (CAD., SOKAĞI, YOL ...), ``party`` (a whole-label
  bitişik), ``garden`` (BAHÇE, AVLU, TERAS, OTOPARK, GİRİŞ), ``front`` (ÖN / ARKA CEPHE), ``free`` (AYRIK).
- **ground** (R24 as verified, decided per facade, never from the level's name or kind), in this order: (a) a soil
  label on the level's own plan beyond the facade (TOPRAK, SIKIŞTIRILMIŞ TOPRAK; never TOPRAK TEMASLI DÖŞEME or a
  bare DOLGU) buries it; (b) a drawn outside door, glazing over ``GLAZED_SHARE`` of the facade, a shop or
  building-entrance label, or a ±0.00 mark at a door frees it; (c) else the terrain (level marks beyond it) buries it
  where the ground is within ``NEXT_FLOOR_M`` of the next floor or above, leaves it partly buried between the sill
  and there, frees it below, but never on the entrance storey (``entrance_storey``) and never when it would bury
  more than one storey (a terrain rejected for that side: a finding); (d) else a level under the entrance storey is
  ``unknown`` (nothing inferred: the user's "underground floors will have no window" until evidence frees it), any
  other level exposed. ``buried``, ``partly`` and ``unknown`` facades take no inferred window; drawn windows always
  stay.
- **plot** (R46 b): a facade within ``PLOT_TOL_M`` of a registered plot edge (``site.plot``) over ``PLOT_SHARE`` of its
  length, with a neighbour parcel behind that edge (a parcel number or a KOMŞU text beyond it within
  ``PLOT_REACH_M``, no street text) is a party facade.

``internal_party(b)`` (R46, an internal party wall): a wall on the same line on every base storey, interior on both
faces, at least ``INTERNAL_DEPTH`` of the outline's depth long, no door or opening through it on any storey, with its
own kitchen, wet room and outer door on each side (and its own stair wholly on each side of a multi-storey house).

Why: real21's attached sides, real20's street fronts, basements with a garden side, a house pair with one party wall:
the facade, not the level, is what is buried, attached or on a street.

How: pure on the building dict and the level's texts (``completion.Level``, ``levels.marks.read_mark``).
"""
from __future__ import annotations

import math
import re
from typing import Optional

from shapely.geometry import LineString, Point

from wenart.ingest import completion as CP

EDGE_MIN_M = 0.5
MARGIN_M = 3.0
ALONG_M = 0.3
NEXT_FLOOR_M = 0.3              # a ground within this of the next floor counts as above the ceiling (R24)
PLOT_TOL_M = 0.10
PLOT_SHARE = 0.8
PLOT_REACH_M = 10.0
INTERNAL_DEPTH = 0.9
GLAZED_SHARE = 0.6
SILL_M = 0.9
SOIL_RE = re.compile(r"(?<![a-z])(?:sikistirilmis\s+)?toprak(?!\s+temasli)(?![a-z])|(?<![a-z])(?:soil|earth|backfill)"
                     r"(?![a-z])")
ENTRANCE_REACH_M = 3.0
TERRAIN_REACH_M = 6.0            # a ground point this far beyond a facade is that facade's ground (R24 (c))
ENTRANCE_RE = re.compile(r"(?<![a-z])(?:(?:bina|apt\.?|apartman)\s+giris\w*|giris\s+holu|(?:dukkan|magaza)\s+giris\w*|"
                         r"entrance)(?![a-z])")
GIRIS_RE = re.compile(r"(?<![a-z])giris(?![a-z])")
NOT_ENTRANCE_RE = re.compile(r"daire\s+giris|gir\.?\s*hol|giris\s+sacak|izdusum|otopark|arac|siginak|garaj|rampa")
EXPOSED_RE = re.compile(r"(?<![a-z])(?:bahce|avlu|teras|otopark|kuranglez|ingiliz\s+avlusu|garden|courtyard|areaway|"
                        r"parking)(?![a-z])")
FRONT_RE = re.compile(r"(?<![a-z])(on|arka)\s+(?:cephe|gorunus)")
FREE_RE = re.compile(r"(?<![a-z])ayrik(?![a-z])")
STREET_RE = re.compile(r"(?<![a-z])(?:sokagi|sokak|sok|sk|caddesi|cadde|cad|bulvari|bulvar|yolu|yol|yanyol|street|"
                       r"road|avenue)(?![a-z])")
NOT_STREET_RE = re.compile(r"yol\s+kotu|kacis\s+yolu")         # a road level mark, an escape route
PARCEL_RE = re.compile(r"(?<![a-z])(?:parsel|parseli|ada|komsu|p\s*[:.]\s*\d+)(?![a-z])|^\d{1,5}$")


def edges_of(level) -> list:
    """The outer ring's edges of a level's outline (pure)."""
    if level.outline is None:
        return []
    ring = list(level.outline.exterior.coords)
    return [(tuple(ring[i][:2]), tuple(ring[i + 1][:2])) for i in range(len(ring) - 1)
            if math.dist(ring[i], ring[i + 1]) >= EDGE_MIN_M]


def facing(level, edges: list, q, reach: float = MARGIN_M) -> Optional[int]:
    """The index of the facade a point outside the outline faces (at most ``reach`` from its line, its foot within
    it, the nearest such), or None (pure)."""
    pt = Point(q)
    if level.outline is None or level.outline.buffer(-1e-6).contains(pt):
        return None
    best = None
    for i, ((x0, y0), (x1, y1)) in enumerate(edges):
        el = math.hypot(x1 - x0, y1 - y0)
        t = ((pt.x - x0) * (x1 - x0) + (pt.y - y0) * (y1 - y0)) / el
        d = LineString([(x0, y0), (x1, y1)]).distance(pt)
        if -ALONG_M <= t <= el + ALONG_M and d <= reach and (best is None or d < best[0]):
            best = (d, i)
    return best[1] if best else None


def notes(level, edges: list, texts: Optional[list], side_points: Optional[list]) -> list:
    """Per facade the margin notes (R45; pure): ``[{street, party, garden, front, free}]`` (the first text each)."""
    out = [{} for _ in edges]
    items = [(sp.get("text"), sp.get("at")) for sp in side_points or [] if sp.get("at")]
    items += [(t.get("text"), (t["x"], t["y"])) for t in texts or []]
    for text, at in items:
        folded = CP._fold(text)
        if not folded:
            continue
        i = facing(level, edges, at)
        if i is None:
            continue
        kind = ("party" if re.search(r"(?<![a-z])bitisik(?![a-z])", folded) and len(folded.split()) <= 4 else
                "street" if STREET_RE.search(folded) and not NOT_STREET_RE.search(folded) else
                "front" if FRONT_RE.search(folded) else "free" if FREE_RE.search(folded) else
                "neighbour" if re.search(r"(?<![a-z])komsu(?![a-z])", folded) else
                "garden" if EXPOSED_RE.search(folded) else None)
        if kind and kind not in out[i]:
            out[i][kind] = str(text).strip()
    return out


def _next_floor(b: dict, lv: dict) -> Optional[float]:
    base = sorted((x for x in b.get("levels") or [] if not x.get("base_level_id")),
                  key=lambda x: (x.get("order") or 0, x["id"]))
    up = [x for x in base if (x.get("order") or 0) > (lv.get("order") or 0)
          and isinstance(x.get("elevation"), (int, float))]
    if up:
        return float(up[0]["elevation"])
    if isinstance(lv.get("elevation"), (int, float)):
        return float(lv["elevation"]) + float(lv.get("ceiling_height") or 2.7) + 0.2
    return None


def entrance_storey(b: dict, texts_by_level: dict) -> Optional[str]:
    """The entrance storey (R24 (5); pure): the lowest base storey whose own plan carries a building-entrance phrase
    (BİNA / APT. / APARTMAN GİRİŞİ, GİRİŞ HOLÜ, DÜKKAN / MAĞAZA GİRİŞİ, ENTRANCE, or a bare GİRİŞ within
    ``ENTRANCE_REACH_M`` of an outer door), never DAİRE GİRİŞİ, GİR. HOL., a canopy or projection, a vehicle or shelter
    entrance, nor a copy of a typical floor; else None (the caller keeps the ground floor by order)."""
    ops = {o["id"]: o for o in b.get("openings") or []}
    base = sorted((lv for lv in b.get("levels") or [] if not lv.get("base_level_id") and not lv.get("typical_of")),
                  key=lambda lv: (lv.get("order") or 0, lv["id"]))
    for lv in base:
        doors = [ops[i]["center"] for i in CP.outer_doors(b, lv["id"]) if ops.get(i, {}).get("center")]
        for t in texts_by_level.get(lv["id"]) or []:
            folded = CP._fold(t["text"])
            if NOT_ENTRANCE_RE.search(folded):
                continue
            if ENTRANCE_RE.search(folded) or (GIRIS_RE.search(folded) and any(
                    math.dist((t["x"], t["y"]), c[:2]) <= ENTRANCE_REACH_M for c in doors)):
                return lv["id"]
    return None


def ground(b: dict, level, lv: dict, edges: list, texts: Optional[list], notes_: list,
           entrance: Optional[str] = None) -> list:
    """Per facade ``{buried, rung, why}`` (R24 as verified; pure): soil labels, then exposure, then a sane terrain,
    then the level's place under or over the entrance storey (the module docstring). ``buried`` is True, False,
    ``"partly"`` or ``"unknown"``."""
    from wenart.ingest import core_rules as CR
    from wenart.levels import marks as LM

    soil, entrance_label, marks, zeros = ({} for _ in range(4))
    for t in texts or []:
        i = facing(level, edges, (t["x"], t["y"]))
        if i is None:
            continue
        folded = CP._fold(t["text"])
        if SOIL_RE.search(folded):
            soil.setdefault(i, t["text"])
        elif ENTRANCE_RE.search(folded) and not NOT_ENTRANCE_RE.search(folded):
            entrance_label.setdefault(i, t["text"])
        m = LM.read_mark(str(t["text"]))
        if m is not None and isinstance(m.get("value"), (int, float)):
            zeros.setdefault(i, []).append((float(m["value"]), t["text"], (t["x"], t["y"])))
    # the terrain (R24 (c), after R04): the ground points the levels model read (site.ground.points), never a bare
    # level mark beside the facade (a terrace's or a landing's floor mark is no ground: real11)
    for gp in ((b.get("site") or {}).get("ground") or {}).get("points") or []:
        if not isinstance(gp, dict) or not isinstance(gp.get("z"), (int, float)):
            continue
        i = facing(level, edges, (float(gp["x"]), float(gp["y"])), TERRAIN_REACH_M)
        if i is not None:
            marks.setdefault(i, []).append((float(gp["z"]), f"ground point {float(gp['z']):+.2f}",
                                            (float(gp["x"]), float(gp["y"]))))
    outer = set(CP.outer_doors(b, level.lid))
    doors, glass = {}, {}
    for o in b.get("openings") or []:
        if o.get("level_id") != level.lid or CR.derived(o) or o.get("wall_id") not in level.walls:
            continue
        if o.get("type") == "door" and o["id"] in outer:
            doors.setdefault(o["wall_id"], []).append(o)
        elif o.get("type") == "window":
            glass.setdefault(o["wall_id"], []).append(o)
    levels = {x["id"]: x for x in b.get("levels") or []}
    order = {x["id"]: x.get("order") or 0 for x in b.get("levels") or []}
    entrance_order = order.get(entrance, 0) if entrance else 0
    top = _next_floor(b, lv)
    above = levels.get(next((x["id"] for x in sorted(levels.values(), key=lambda x: x.get("order") or 0)
                             if not x.get("base_level_id") and (x.get("order") or 0) == (lv.get("order") or 0) + 1),
                            None)) or {}
    top2 = _next_floor(b, above) if above else None
    floor = float(lv["elevation"]) if isinstance(lv.get("elevation"), (int, float)) else None
    out = []
    for i, edge in enumerate(edges):
        walls = [w for w in level.walls.values() if CP._on_side(w, edge)]
        outside = [o for w in walls for o in doors.get(w["id"]) or []]
        el = math.dist(edge[0], edge[1])
        glazed = sum(float(o.get("width") or 0.0) for w in walls for o in glass.get(w["id"]) or [])
        zero = [m for m in zeros.get(i) or [] if abs(m[0]) < 1e-6 and any(
            math.dist(m[2], (o.get("center") or [1e9, 1e9])[:2]) <= 1.5 for o in outside)]
        if i in soil:
            out.append({"buried": True, "rung": "soil", "why": f"the soil label '{soil[i]}' beyond it"})
        elif outside or glazed >= GLAZED_SHARE * el or i in entrance_label or zero:
            what = (f"the drawn outside door {outside[0]['id']}" if outside else
                    f"glazing over {glazed / el * 100:.0f} % of it" if glazed >= GLAZED_SHARE * el else
                    f"the label '{entrance_label[i]}'" if i in entrance_label else "a ±0.00 mark at its door")
            out.append({"buried": False, "rung": "exposure", "why": what})
        elif i in marks and top is not None:
            z, text, _at = max(marks[i])
            if level.lid == entrance or (lv.get("order") or 0) == entrance_order:
                out.append({"buried": False, "rung": "terrain_rejected",
                            "why": f"the ground mark '{text}' would bury the entrance storey: rejected (a finding for "
                                   f"the terrain)"})
            elif top2 is not None and z >= top2 - NEXT_FLOOR_M:
                out.append({"buried": "unknown", "rung": "terrain_rejected",
                            "why": f"the ground mark '{text}' ({z:+.2f} m) would bury more than one storey: rejected "
                                   f"(a finding for the terrain)"})
            elif z >= top - NEXT_FLOOR_M:
                out.append({"buried": True, "rung": "terrain",
                            "why": f"the ground mark '{text}' ({z:+.2f} m) is within {NEXT_FLOOR_M} m of the next floor "
                                   f"({top:+.2f} m) or above"})
            elif floor is not None and z > floor + SILL_M:
                out.append({"buried": "partly", "rung": "terrain",
                            "why": f"the ground mark '{text}' ({z:+.2f} m) lies between the sill and the soffit"})
            else:
                out.append({"buried": False, "rung": "terrain",
                            "why": f"the ground mark '{text}' ({z:+.2f} m) lies below the sill"})
        elif (lv.get("order") or 0) < entrance_order:
            out.append({"buried": "unknown", "rung": "level",
                        "why": "no evidence on this side of a level under the entrance storey: unknown, nothing "
                               "inferred"})
        else:
            out.append({"buried": False, "rung": "level", "why": "no evidence: above ground"})
    return out


def plot_party(b: dict, level, edges: list, levels_texts: list) -> dict:
    """R46 (b) (pure): ``{facade index: evidence}`` for the facades on a registered plot edge with a neighbour parcel
    behind it (the module docstring)."""
    plot = CP._poly(((b.get("site") or {}).get("plot") or {}).get("polygon"))
    if plot is None:
        return {}
    ring = list(plot.exterior.coords)
    plot_edges = [(ring[k][:2], ring[k + 1][:2]) for k in range(len(ring) - 1)]
    out = {}
    for i, (p, q) in enumerate(edges):
        fl = LineString([p, q])
        for a, c in plot_edges:
            pl = LineString([a, c])
            near = fl.intersection(pl.buffer(PLOT_TOL_M + 0.15))
            if near.is_empty or near.length < PLOT_SHARE * fl.length:
                continue
            # a neighbour parcel behind the plot edge: a parcel number or KOMŞU beyond it (outside the plot, its foot
            # within that edge), no street text
            el = math.dist(a, c)

            def behind(t, a=a, c=c, el=el, pl=pl):
                q = Point(t["x"], t["y"])
                s = ((q.x - a[0]) * (c[0] - a[0]) + (q.y - a[1]) * (c[1] - a[1])) / el if el > 0 else -1
                return not plot.contains(q) and 0.0 <= s <= el and pl.distance(q) <= PLOT_REACH_M

            beyond = [t for t in levels_texts if behind(t)]
            street = [t for t in beyond if STREET_RE.search(CP._fold(t["text"]))]
            parcel = [t for t in beyond if PARCEL_RE.search(CP._fold(t["text"]))]
            if parcel and not street:
                out[i] = {"text": parcel[0]["text"], "rule": "plot_line",
                          "side": [[round(p[0], 2), round(p[1], 2)], [round(q[0], 2), round(q[1], 2)]]}
                break
    return out


def internal_party(b: dict) -> list:
    """R46 (7) (pure): the internal party walls of a house pair (the module docstring): ``[{line, walls, reason}]``."""
    from wenart.ingest import core_rules as CR

    base = sorted((lv for lv in b.get("levels") or [] if not lv.get("base_level_id")),
                  key=lambda lv: (lv.get("order") or 0, lv["id"]))
    if not base:
        return []
    per = []
    for lv in base:
        level = CP.Level(b, lv["id"])
        if level.outline is None:
            return []
        cands = []
        for w in level.walls.values():
            spans = w.get("exterior_spans") or []
            if not spans or any(s["kind"] != "interior" for s in spans):
                continue
            a, u, length = CP._axis(w)
            # the outline's depth along the wall's direction
            proj = [(x - a[0]) * u[0] + (y - a[1]) * u[1] for x, y in level.outline.exterior.coords]
            depth = max(proj) - min(proj)
            if depth > 0 and length >= INTERNAL_DEPTH * depth:
                cands.append(w)
        per.append((lv, level, cands))
    lv0, level0, cands0 = per[0]
    out = []
    for w in cands0:
        line = LineString([tuple(w["start"][:2]), tuple(w["end"][:2])])
        same = [w]
        for lv, level, cands in per[1:]:
            twin = next((c for c in cands if LineString([tuple(c["start"][:2]), tuple(c["end"][:2])]).hausdorff_distance(
                line) <= 0.15), None)
            if twin is None:
                break
            same.append(twin)
        if len(same) != len(per):
            continue
        ids = {x["id"] for x in same}
        if any(o.get("wall_id") in ids and o.get("type") in ("door", "opening") for o in b.get("openings") or []):
            continue
        # each side its own dwelling: a kitchen, a wet room and an outer door (and its own stair when multi-storey)
        a, u, _ = CP._axis(w)
        n = (-u[1], u[0])

        def side_of(x, y):
            return 1 if (x - a[0]) * n[0] + (y - a[1]) * n[1] > 0 else -1

        sides = {1: {"kitchen": False, "wet": False, "door": False, "stair": False},
                 -1: {"kitchen": False, "wet": False, "door": False, "stair": False}}
        for r in b.get("rooms") or []:
            p = CP._poly(r.get("polygon"))
            if p is None:
                continue
            s = side_of(p.centroid.x, p.centroid.y)
            if r.get("room_type") == "kitchen":
                sides[s]["kitchen"] = True
            if r.get("room_type") in CR.WET:
                sides[s]["wet"] = True
        ops = {o["id"]: o for o in b.get("openings") or []}
        for lv in base:
            for oid in CP.outer_doors(b, lv["id"]):
                c = (ops.get(oid) or {}).get("center")
                if c:
                    sides[side_of(c[0], c[1])]["door"] = True
        stairs = [f for f in b.get("furniture") or [] if f.get("type") == "stair" and f.get("footprint")]
        for f in stairs:
            corners = CR._rect(f["footprint"]).exterior.coords
            ss = {side_of(x, y) for x, y in corners}
            if len(ss) == 1:
                sides[ss.pop()]["stair"] = True
        need_stair = len(base) >= 2
        if all(v["kitchen"] and v["wet"] and v["door"] and (v["stair"] or not need_stair) for v in sides.values()):
            out.append({"walls": sorted(ids), "line": [list(w["start"][:2]), list(w["end"][:2])],
                        "reason": f"{w['id']} runs the building's depth on every storey with no opening through it, "
                                  f"and each side has its own kitchen, wet room, outer door"
                                  + (" and stair" if need_stair else "") + ": an internal party wall (inferred)"})
    return out
