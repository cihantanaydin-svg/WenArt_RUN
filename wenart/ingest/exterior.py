"""Exterior per stretch of wall (12 Nov 2026; stage 2 of the building-sense audit: R14 as the misfire hunters amended
it, with the coordinator's decision on enclosed terraces).

What: ``apply(build, texts_by_level)`` runs in ``completion.complete`` after the light wells and before the windows;
it writes each wall's ``exterior_spans`` (``[{t0, t1, side, kind}]`` along the wall from its start, ``side`` +1/-1
the normal side of the exterior face, ``kind`` exterior | light_well | interior | free_standing | unknown) and sets
the wall's whole flag to "any span exterior" (wall records stay whole: 26 correction records and the truth's reader
ids point at wall ids). Each flag change keeps ``drawn_exterior`` (``adjusted_by_ai`` by code). Returns the record
for ``level_inference.exterior``.

- **Faces.** Both faces of a wall are probed every ``STEP_M`` by stepping out of the wall union (``END_SKIP_M``
  left out at each end). A face is *indoor* (a room), *outdoor* (a balcony or terrace room, a BALKON / TERAS / LOGGIA
  / VERANDA / SUNDURMA / AVLU label, a site outdoor space), a *light well* (only with a drawn light-well label or
  text inside the face, never a name the reader inferred), *outside* (beyond the outer ring of the level outline) or
  *unknown* (an enclosed face with no room, a wall band, a void).
- **Enclosed terraces** (the coordinator, 12 Nov 2026: synthetic truth stays): a terrace inside the outline closed by
  walls of the outer walls' thickness on its outer sides is an enclosed room (indoor); it is outdoor only when an
  outer side is open or a parapet / railing (a thin wall, a parapet flag, a korkuluk / railing / parapet layer or
  word), or when it lies outside the roof outline of its own storey (a roof terrace over the floor below).
- **Stretches** of at least ``MIN_STRETCH_M``: exterior when one face is indoor and the other outdoor or outside
  (light_well when it is a light well), interior when both are indoor, free-standing when neither is, else unknown
  (the flag stays, no inferred opening). A stretch whose outward probe reaches an unplaced room-name label within
  ``LABEL_REACH_M`` through no wall is unknown, never exterior (a room the reading lost lies there).
- **Levels that qualify** (``qualifies``): rooms, room area at least ``ROOM_SHARE_MIN`` of the outline, at most
  ``UNPLACED_SHARE_MAX`` of the room labels in no face, no paper room (RC14), not read with low confidence. Only they
  change flags and take inferred windows (``completion.window_decision``); the spans are written on every level.

Why: real21's ~105 m of partitions between flats flagged exterior, real02's fins, real20's walls facing lost rooms:
the whole-wall flag from touching the outline is wrong where a wall is partly outside and partly between rooms.

How: pure geometry on the building dict (``completion.Level`` probes, the wall union from ``crossdoc.wall_polygon``).
Every change passes ``rule_guards.blocked`` (rule key ``exterior_flag``).
"""
from __future__ import annotations

import math
import re
from typing import Optional

from shapely.geometry import LineString, Point
from shapely.ops import unary_union
from shapely.prepared import prep

from wenart import building as B
from wenart.ingest import completion as CP
from wenart.ingest import rule_guards as RG

STEP_M = 0.10
END_SKIP_M = 0.15
MIN_STRETCH_M = 0.5
PROBE_MAX_M = 0.6               # a face probe steps out of the wall union up to this far
LABEL_REACH_M = 8.0
ROOM_SHARE_MIN = 0.60
UNPLACED_SHARE_MAX = 0.20
OUTER_THICK_SHARE = 0.8         # an enclosing wall is at least this share of the outer walls' thickness
OUTER_SIDE_M = 0.5              # a terrace side this close to the outline's outer ring is an outer side
OUTDOOR_WORDS = re.compile(r"(?<![a-z])(?:balkon|teras|terrace|loggia|lodjia|veranda|sundurma|avlu|balcony)")
RAILING_WORDS = re.compile(r"korkuluk|railing|parapet|guard|handrail|kupeste")
NOT_ROOM_WORDS = ("brut", "net", "oturum", "normal", "kat", "mahal", "kotu", "kot", "toplam", "alan")


def _wall_faces(level, w: dict, union, t: float, side: int):
    """The probe point of wall ``w`` at ``t`` on ``side``: stepped out of the wall union (pure)."""
    a, u, _ = CP._axis(w)
    n = (-u[1], u[0])
    c = (a[0] + u[0] * t, a[1] + u[1] * t)
    d = float(w.get("thickness") or 0.15) / 2.0 + 0.05
    while d <= PROBE_MAX_M:
        q = (c[0] + side * n[0] * d, c[1] + side * n[1] * d)
        if union is None or not union.contains(Point(q)):
            return q
        d += 0.05
    return None


def _outer_thickness(level) -> float:
    """The outer walls' thickness (pure): the length-weighted median of the walls on the outline's outer ring that
    border no open-air room (a terrace's own parapets never set it); 0.2 m without such walls."""
    if level.outline is None:
        return 0.2
    ring = level.outline.exterior
    air = [level.polys[r["id"]] for r in level.rooms
           if str(r.get("room_type") or "") in CP.OPEN_AIR or OUTDOOR_WORDS.search(CP._fold(r.get("label")))]
    rows = []
    for w in level.walls.values():
        t = float(w.get("thickness") or 0.0)
        line = LineString([tuple(w["start"][:2]), tuple(w["end"][:2])])
        if t <= 0 or line.length < 0.3 or line.distance(ring) > t / 2.0 + 0.05:
            continue
        if any(line.distance(p) <= t / 2.0 + 0.15 for p in air):
            continue
        rows.append((t, line.length))
    if not rows:
        return 0.2
    rows.sort()
    half, acc = sum(ln for _, ln in rows) / 2.0, 0.0
    for t, ln in rows:
        acc += ln
        if acc >= half:
            return t
    return rows[-1][0]


def enclosed_terraces(b: dict, level, union) -> set:
    """The open-air rooms of a level inside its outline that are enclosed rooms for the exterior flags (pure; the
    module docstring): walls of the outer walls' thickness on every outer side, none a parapet or railing, and inside
    the roof outline of its own storey when the roof is over it."""
    if level.outline is None:
        return set()
    ring = level.outline.exterior
    thick = _outer_thickness(level) * OUTER_THICK_SHARE
    roof = b.get("roof") or {}
    roof_poly = CP._poly(roof.get("outline")) if roof.get("over_level_id") == level.lid else None
    out = set()
    for r in level.rooms:
        label = CP._fold(r.get("label") or r.get("label_raw"))
        if str(r.get("room_type") or "") not in CP.OPEN_AIR and not OUTDOOR_WORDS.search(label):
            continue
        p = level.polys[r["id"]]
        if roof_poly is not None and p.intersection(roof_poly).area < 0.5 * p.area:
            continue                                   # a roof terrace over the floor below: outdoor
        if _closed_outer_sides(level, p, ring, thick):
            out.add(r["id"])
    return out


def _closed_outer_sides(level, p, ring, thick: float) -> bool:
    """True when every outer side of a terrace (an edge whose middle lies within ``OUTER_SIDE_M`` plus the outer walls'
    thickness of the outline's outer ring) is covered over at least 80 % by walls along it of at least ``thick``, none
    a parapet or railing (pure)."""
    pts = list(p.exterior.coords)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        el = math.hypot(x1 - x0, y1 - y0)
        if el < 0.3 or ring.distance(Point((x0 + x1) / 2.0, (y0 + y1) / 2.0)) > OUTER_SIDE_M + thick / OUTER_THICK_SHARE:
            continue
        eu = ((x1 - x0) / el, (y1 - y0) / el)
        covered = 0.0
        for w in level.walls.values():
            a, u, length = CP._axis(w)
            if length < 0.1 or abs(u[0] * eu[1] - u[1] * eu[0]) > CP.PARALLEL_SIN:
                continue
            off = abs((a[0] - x0) * -eu[1] + (a[1] - y0) * eu[0])
            if off > float(w.get("thickness") or 0.15) / 2.0 + 0.2:
                continue
            ts = sorted(((q[0] - x0) * eu[0] + (q[1] - y0) * eu[1]) for q in (w["start"], w["end"]))
            ov = min(el, ts[1]) - max(0.0, ts[0])
            if ov <= 0.05:
                continue
            ev = " ".join(str(e.get("layer") or "") + " " + str(e.get("note") or "") for e in w.get("evidence") or []
                          if isinstance(e, dict)).lower()
            if float(w.get("thickness") or 0.0) < thick or w.get("parapet") or RAILING_WORDS.search(ev):
                return False                          # a parapet or railing on an outer side: open
            covered += ov
        if covered < 0.8 * el:
            return False                              # an open outer side
    return True


def _wall_poly(w: dict):
    from wenart.reading_check.crossdoc import wall_polygon
    p = wall_polygon(w)
    return list(p.exterior.coords) if p is not None and not p.is_empty else None


def face_kind(level, q, enclosed: set, wells: set) -> str:
    """indoor | outdoor | light_well | outside | unknown at probe point ``q`` (pure)."""
    if q is None:
        return "unknown"
    k = level.kind_at(q, "")
    r = level.room_at(q)
    if k == "balcony":
        return "indoor" if r is not None and r["id"] in enclosed else "outdoor"
    if k in ("room", "own"):
        if r is not None and r["id"] in wells:
            return "light_well"
        return "indoor"
    if k == "light_well":
        return "light_well" if r is not None and r["id"] in wells else "indoor"
    if k == "outside":
        return "outside"
    return "unknown"


def drawn_wells(level, texts: Optional[list]) -> set:
    """The light wells with a drawn label or text inside them (never a name the reader inferred; pure)."""
    out = set()
    for r in level.rooms:
        if r.get("label_inferred") and not r.get("label_raw"):
            continue
        raw = CP._fold(r.get("label_raw"))
        if CP.LIGHT_WELL_RE.search(raw):
            out.add(r["id"])
            continue
        p = level.polys[r["id"]]
        if any(CP.LIGHT_WELL_RE.search(CP._fold(t["text"])) and p.buffer(0.05).contains(Point(t["x"], t["y"]))
               for t in texts or []):
            out.add(r["id"])
    return out


def qualifies(b: dict, level, lv: dict, texts: Optional[list]) -> tuple:
    """``(ok, reasons)`` for a level (pure; R14 guard 5): rooms, room area against the outline, labels placed, no
    paper room, not read with low confidence. A copy of a typical floor is judged by its floor."""
    levels = {x["id"]: x for x in b.get("levels") or []}
    base = levels.get(lv.get("typical_of")) if lv.get("typical_of") else None
    judge = base or lv
    why = []
    if not level.rooms:
        why.append("no rooms")
    if level.outline is None:
        why.append("no closed outline")
    elif level.rooms:
        area = sum(level.polys[r["id"]].area for r in level.rooms)
        if area < ROOM_SHARE_MIN * level.outline.area:
            why.append(f"rooms cover {area / level.outline.area * 100:.0f} % of the outline (under "
                       f"{ROOM_SHARE_MIN * 100:.0f} %)")
    lost = [p for p in judge.get("reading_places") or [] if p.get("kind") == "unplaced_label"]
    named = len(level.rooms) + len(lost)
    if named and len(lost) > UNPLACED_SHARE_MAX * named:
        why.append(f"{len(lost)} of {named} room labels stand in no face")
    if judge.get("reading_confidence") == "low":
        why.append("read with low confidence")
    from wenart.reading_check import is_closure_wall
    if any(is_closure_wall(w) for w in level.walls.values()):
        why.append("its outline is closed by inferred walls (outline closure)")
    try:
        from wenart.reading_check import sense as SN
        paper = [f for f in SN.frame_walls_and_paper_rooms(b, None) if f.get("level_id") == judge["id"]]
    except Exception:  # noqa: BLE001 - the check is advisory; a failure leaves the level qualified
        paper = []
    if paper:
        why.append("a paper room or frame walls (RC14)")
    return not why, why


def _lost_labels(lv: dict, levels: dict) -> list:
    base = levels.get(lv.get("typical_of")) if lv.get("typical_of") else None
    out = []
    for p in (base or lv).get("reading_places") or []:
        if p.get("kind") != "unplaced_label" or not p.get("at"):
            continue
        text = CP._fold(p.get("text"))
        if not text or any(w == text or text.startswith(w + " ") for w in NOT_ROOM_WORDS):
            continue
        if B.room_type_for(str(p.get("text"))) in ("other", "unknown", None):
            continue
        out.append(p)
    return out


def wall_spans(level, w: dict, union, enclosed: set, wells: set, lost: list, walls_union_lines) -> list:
    """The stretches of one wall (pure; the module docstring)."""
    a, u, length = CP._axis(w)
    if length < MIN_STRETCH_M:
        return []
    samples = []
    t = END_SKIP_M
    while t <= length - END_SKIP_M + 1e-9:
        qs = [_wall_faces(level, w, union, t, s) for s in (1, -1)]
        kinds = [face_kind(level, q, enclosed, wells) for q in qs]
        if kinds == ["indoor", "indoor"]:
            r1, r2 = (level.room_at(q) for q in qs)
            if r1 is not None and r2 is not None and r1["id"] == r2["id"]:
                kinds = ["unknown", "unknown"]          # one room on both faces: its polygon spans the wall (real15)
        samples.append((t, kinds))
        t += STEP_M
    if not samples:
        return []

    def klass(kinds):
        k1, k2 = kinds
        if "indoor" in kinds:
            other = k2 if k1 == "indoor" else k1
            side = 1 if k2 == "indoor" else -1           # the exterior face is the non-indoor one
            if k1 == k2 == "indoor":
                return "interior", 0
            if other in ("outdoor", "outside"):
                return "exterior", side
            if other == "light_well":
                return "light_well", side
            return "unknown", 0
        if all(k in ("outdoor", "outside", "light_well") for k in kinds):
            return "free_standing", 0
        return "unknown", 0

    runs = []
    for t, kinds in samples:
        k, side = klass(kinds)
        if runs and runs[-1]["kind"] == k and runs[-1]["side"] == side:
            runs[-1]["t1"] = t
        else:
            runs.append({"t0": t, "t1": t, "kind": k, "side": side})
    out = []
    for r in runs:
        r0, r1 = max(0.0, r["t0"] - STEP_M / 2.0), min(length, r["t1"] + STEP_M / 2.0)
        if r1 - r0 < MIN_STRETCH_M:
            continue
        span = {"t0": round(r0, 3), "t1": round(r1, 3), "side": r["side"], "kind": r["kind"]}
        if span["kind"] == "exterior" and lost:
            # a room the reading lost lies beyond: unknown, never exterior
            n = (-u[1], u[0])
            mid = (a[0] + u[0] * (r0 + r1) / 2.0, a[1] + u[1] * (r0 + r1) / 2.0)
            for p in lost:
                v = (p["at"][0] - mid[0], p["at"][1] - mid[1])
                depth = (v[0] * n[0] + v[1] * n[1]) * r["side"]
                lateral = abs(v[0] * u[0] + v[1] * u[1])
                if 0.0 < depth <= LABEL_REACH_M and lateral <= (r1 - r0) / 2.0 + 0.5:
                    ray = LineString([(mid[0] + n[0] * r["side"] * 0.3, mid[1] + n[1] * r["side"] * 0.3),
                                      tuple(p["at"][:2])])
                    if walls_union_lines is None or not walls_union_lines.intersects(ray):
                        span["kind"], span["label"] = "unknown", str(p.get("text"))
                        break
        out.append(span)
    return out


def allows(w: dict, t0: float, t1: float) -> bool:
    """True when an inferred opening may stand on ``w`` between ``t0`` and ``t1`` (pure): no spans recorded, or a span
    of kind exterior or light_well overlapping that stretch by at least ``MIN_STRETCH_M`` (or the whole stretch)."""
    spans = w.get("exterior_spans")
    if spans is None:
        return True
    for s in spans:
        if s["kind"] in ("exterior", "light_well"):
            ov = min(t1, s["t1"]) - max(t0, s["t0"])
            if ov >= min(MIN_STRETCH_M, t1 - t0) - 1e-6:
                return True
    return False


def apply(build, texts_by_level: dict) -> dict:
    """The module docstring; the record for ``level_inference.exterior``."""
    from wenart.reading_check.crossdoc import wall_polygon

    b = build.building
    levels = {lv["id"]: lv for lv in b.get("levels") or []}
    rec = {"levels": {}, "changed": [], "not_qualified": {}}
    for lv in b.get("levels") or []:
        lid = lv["id"]
        texts = texts_by_level.get(lid)
        level = CP.Level(b, lid, texts)
        if level.outline is None:
            rec["not_qualified"][lid] = ["no closed outline"]
            continue
        polys = [p for p in (wall_polygon(w) for w in level.walls.values()) if p is not None and not p.is_empty]
        union = prep(unary_union(polys)) if polys else None
        lines = unary_union([LineString([tuple(w["start"][:2]), tuple(w["end"][:2])]) for w in level.walls.values()]) \
            if level.walls else None
        enclosed = enclosed_terraces(b, level, union)
        wells = drawn_wells(level, texts)
        lost = _lost_labels(lv, levels)
        ok, why = qualifies(b, level, lv, texts)
        lv_rec = {"qualified": ok, "enclosed_terraces": sorted(enclosed), "light_wells": sorted(wells),
                  "metres": {}}
        if not ok:
            rec["not_qualified"][lid] = why
        for w in b.get("walls") or []:
            if w.get("level_id") != lid or w["id"] not in level.walls:
                continue
            spans = wall_spans(level, level.walls[w["id"]], union, enclosed, wells, lost, lines)
            w["exterior_spans"] = spans
            for s in spans:
                lv_rec["metres"][s["kind"]] = round(lv_rec["metres"].get(s["kind"], 0.0) + s["t1"] - s["t0"], 2)
            if not ok or not spans or all(s["kind"] == "unknown" for s in spans):
                continue                                # the drawn flag stays
            flag = any(s["kind"] in ("exterior", "light_well") for s in spans)
            if bool(w.get("exterior")) == flag:
                continue
            if any(s["kind"] == "unknown" for s in spans) and not flag:
                continue                                # unknown stretches never clear an exterior flag
            if RG.blocked("exterior_flag", b, {"level_id": lid, "wall": w["id"], "exterior": flag}):
                continue
            kinds = ", ".join(f"{s['kind']} {s['t0']:.2f}-{s['t1']:.2f}" for s in spans)
            reason = (f"{w['id']}: {'an exterior stretch' if flag else 'no exterior stretch'} by its faces ({kinds}): "
                      f"{'exterior' if flag else 'interior'} (drawn flag {bool(w.get('exterior'))}; R14, the wall "
                      f"record whole, its stretches in exterior_spans)")
            w["drawn_exterior"] = bool(w.get("exterior"))
            w["exterior"] = flag
            w["adjusted_by_ai"] = {"by": "code", "rule": "exterior_spans", "reason": reason,
                                   "changed": {"exterior": w["drawn_exterior"]}}
            rec["changed"].append({"wall": w["id"], "level_id": lid, "exterior": flag, "reason": reason})
        rec["levels"][lid] = lv_rec
    if rec["changed"]:
        build.warn(f"exterior spans: {len(rec['changed'])} wall flag(s) set from the walls' faces "
                   f"({sum(1 for x in rec['changed'] if not x['exterior'])} interior, "
                   f"{sum(1 for x in rec['changed'] if x['exterior'])} exterior)")
    for lid, why in rec["not_qualified"].items():
        build.warn(f"exterior spans: {lid} does not qualify ({'; '.join(why)}): its flags stay and no window is "
                   f"inferred on it (R14)")
    return rec


def level_ok(b: dict, lid: str) -> tuple:
    """``(ok, reasons)`` from the record (pure): True when no record says the level does not qualify."""
    why = ((b.get("level_inference") or {}).get("exterior") or {}).get("not_qualified", {}).get(lid)
    return (not why, why or [])
