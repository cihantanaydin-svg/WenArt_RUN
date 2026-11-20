"""The basements a document lists that no plan draws (20 Nov 2026; pre-pod review R03-01, coordinator: "an inferred
basement with no plan is the footprint with the core (stair, lifts), no windows, not a copy of the ground floor's flats,
entrance or windbreak, marked inferred").

What: ``apply(build, rec, slab_default) -> list`` builds each basement of ``rec["basements_inferred"]`` (the storeys
record of ``wenart/sheets/storeys.py``: '1BK+ZK+12K' in real03's DWG lists one basement no plan draws) under the ground
floor: its outer walls along the ground floor's footprint (the outline of the ground floor's walls, the walls' axis half
the outer wall thickness inside), no window and no outside door; the ground floor's common core (``core_rules.
core_rooms``: lifts, stair rooms, the lift lobby, the halls joined to them, and a lobby whose doors join two core rooms,
a fire stair's lobby) with its walls, its stairs (copied: each rises from the basement to the ground floor), its lift
landing doors and the doors between core rooms; the rest of the footprint one room per piece (a basement store, room
type ``storage``), reached by one of the core's doors into it. Every element is ``inferred`` with the rule, the reason
and the element of the ground floor it repeats (``basement_of``); the level is ``kind: basement`` with ``reading_
confidence: low`` and its reasons. The slab under the ground floor gets the basement stairs' openings; a slab under the
basement is added. Returns one record per basement.

Why: real03's DWG says 1 basement + ground + 12 floors; the reading built no basement, and copying the ground floor
down would put flats, a windbreak and windows under the ground.

How: pure geometry on the building (shapely); no AI; rule key ``basement_footprint`` (``rule_guards``).
"""
from __future__ import annotations

import re
from statistics import median
from typing import Optional

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

RULE = "basement_footprint"
MIN_ROOM_M2 = 4.0               # a piece of the footprint smaller than this is no room (a wall corner, a notch)
NOTCH_M = 0.3                   # notches of the footprint narrower than this are closed
WALL_ON_ROOM_M = 0.08           # a wall's axis this far (beyond half its thickness) from a core room's edge bounds it
WALL_ON_SHARE = 0.6             # ... along at least this share of its length
OUTER_T_M = 0.25                # the outer wall's thickness when the ground floor gives none


def _fold(text) -> str:
    from wenart import building as B
    return " ".join(B.fold_ascii(str(text or "")).upper().split())


def _ev(rule_text: str, file: str) -> dict:
    return {"file": file, "page": None, "layer": None, "entity": None, "method": "inferred", "confidence": 0.5,
            "rule": RULE, "text": rule_text}


def _moved(oid: str, lid: str, new: str) -> str:
    """A ground-floor id on the basement ('w_L0_050' -> 'w_L-1_050', 'd_L0_015' -> 'd_L-1_015'; else '<id>_<new>')."""
    tag = f"_{lid}_"
    return oid.replace(tag, f"_{new}_", 1) if tag in oid else f"{oid}_{new}"


def core_of(b: dict, level) -> set:
    """The ground floor's common core (``core_rules.core_rooms``) and every hall or lobby whose doors join two core
    rooms (a fire stair's lobby between the floor hall and the fire stair; pure)."""
    from wenart.ingest import core_rules as CR

    core = set(CR.core_rooms(b, level))
    rooms = {r["id"]: r for r in level.rooms}
    links = CR._links(level)
    for rid, r in rooms.items():
        if rid in core or r.get("room_type") not in ("hall", "corridor", "other", None):
            continue
        if CR.FLAT_HALL_RE.search(CR._label(r)) or CR.UNIT_USE_RE.search(CR._label(r)):
            continue
        joined = {c if a == rid else a for a, c, _o in links if rid in (a, c)} & core
        if len(joined) >= 2:
            core.add(rid)
    return core


def _bounds_core(w: dict, polys: list) -> bool:
    line = LineString([tuple(w["start"]), tuple(w["end"])])
    if line.length <= 1e-6:
        return False
    reach = float(w.get("thickness") or 0.15) / 2.0 + WALL_ON_ROOM_M
    return any(line.intersection(p.exterior.buffer(reach)).length >= WALL_ON_SHARE * line.length for p in polys)


def _footprint(level) -> Optional[Polygon]:
    out = level.outline
    if out is None or out.is_empty:
        return None
    if out.geom_type != "Polygon":
        out = max(getattr(out, "geoms", [out]), key=lambda g: g.area)
    out = out.buffer(NOTCH_M / 2.0, join_style=2).buffer(-NOTCH_M / 2.0, join_style=2)
    if out.geom_type != "Polygon":
        out = max(out.geoms, key=lambda g: g.area)
    return Polygon(out.exterior).simplify(0.03)


def _level_label(ground: dict, k: int) -> str:
    if re.search(r"\bKAT\b", _fold(ground.get("label"))):
        return f"{k}. Bodrum Kat"
    return "Basement" if k == 1 else f"Basement {k}"


def apply(build, rec: dict, slab_default: float = 0.20) -> list:
    """The module docstring."""
    from wenart.ingest import completion as CP
    from wenart.ingest import core_rules as CR
    from wenart.ingest import rule_guards as RG

    b = build.building
    items = list(rec.get("basements_inferred") or [])
    levels = b.get("levels") or []
    ground = next((lv for lv in levels if lv.get("order") == 0 and not lv.get("base_level_id")
                   and not lv.get("typical_of")), None)
    if not items or ground is None or any((lv.get("order") or 0) < 0 for lv in levels):
        return []
    gl = CP.Level(b, ground["id"])
    foot = _footprint(gl)
    if foot is None or foot.area < MIN_ROOM_M2:
        return []
    file = (ground.get("evidence") or [{}])[0].get("file") if isinstance(ground.get("evidence"), list) else ""
    outer = [float(w.get("thickness") or 0) for w in gl.walls.values() if w.get("exterior") and w.get("thickness")]
    t_out = round(median(outer), 3) if outer else OUTER_T_M
    core = core_of(b, gl)
    rooms = {r["id"]: r for r in gl.rooms}
    core_polys = [gl.polys[i] for i in core]
    out = []
    above = ground
    for item in sorted(items, key=lambda i: -int(i["order"])):
        lid, k = item["level_id"], -int(item["order"])
        why = item.get("reason") or "a basement no plan draws"
        if RG.blocked("basement_footprint", b, {"level_id": lid, "why": why}):
            continue
        floor = float(item["floor_m"])
        ceiling = round(float(above.get("elevation") or 0.0) - floor - slab_default, 3)
        ev_text = f"{why} (inferred: the ground floor's footprint and core, no plan of its own)"
        new_lv = {"id": lid, "label": _level_label(ground, k), "order": -k, "elevation": round(floor, 3),
                  "ceiling_height": ceiling, "ceiling_height_source": "assumed_default", "kind": "basement",
                  "elevation_source": "section" if item.get("floor_marked") else "assumed_default",
                  "floor_to_floor": None, "variant_group": ground.get("variant_group"), "variant": "base",
                  "variant_slug": "base", "base_level_id": None, "region_id": None,
                  "evidence": [_ev(ev_text, file)] + [dict(e, method="inferred", file=file, confidence=0.5)
                                                      for e in item.get("evidence") or []],
                  "storey_inference": {"inferred": True, "rule": item.get("rule"), "confidence": item.get("confidence"),
                                       "guess": False, "reason": why},
                  "basement_inferred": {"rule": RULE, "from_level": ground["id"], "reason": ev_text},
                  "reading_confidence": "low",
                  "reading_review": [f"basement inferred ({item.get('rule')}): no plan draws it; built as the ground "
                                     f"floor's footprint with its core (stairs, lifts)"]}
        tag = {"inferred": True, "inference": {"rule": RULE, "reason": ev_text}}
        walls, ops, new_rooms, furn = [], [], [], []
        wall_map = {}
        # the outer walls: the footprint's ring, their axis half the thickness inside
        ring = foot.buffer(-t_out / 2.0, join_style=2)
        if ring.is_empty:
            continue
        if ring.geom_type != "Polygon":
            ring = max(ring.geoms, key=lambda g: g.area)
        pts = list(ring.exterior.coords)[:-1]
        for n, (p, q) in enumerate(zip(pts, pts[1:] + pts[:1]), start=1):
            if LineString([p, q]).length < 0.05:
                continue
            walls.append(dict(tag, id=f"w_{lid}_b{n:03d}", level_id=lid, start=[round(p[0], 4), round(p[1], 4)],
                              end=[round(q[0], 4), round(q[1], 4)], thickness=t_out, height=ceiling, exterior=True,
                              status="unverified", evidence=[_ev(f"outer wall along {ground['id']}'s footprint "
                                                                 f"(inferred)", file)]))
        # the core's walls (inner walls of the ground floor bounding a core room)
        for w in gl.walls.values():
            if w.get("exterior") or not _bounds_core(w, core_polys):
                continue
            nid = _moved(w['id'], ground['id'], lid)
            wall_map[w["id"]] = nid
            walls.append(dict({kk: v for kk, v in w.items() if kk not in ("id", "level_id", "evidence", "height")},
                              **tag, id=nid, level_id=lid, height=ceiling, basement_of=w["id"], status="unverified",
                              evidence=[_ev(f"{w['id']} of {ground['id']} repeated: a wall of the core", file)]))
        # the core's rooms, and the rest of the footprint as stores
        room_map = {}
        for rid in sorted(core):
            r = rooms[rid]
            nid = _moved(rid, ground['id'], lid)
            room_map[rid] = nid
            new_rooms.append(dict({kk: v for kk, v in r.items() if kk not in ("id", "level_id", "evidence")}, **tag,
                                  id=nid, level_id=lid, basement_of=rid, status="unverified",
                                  has_documented_furniture=False,
                                  evidence=[_ev(f"{rid} '{r.get('label')}' of {ground['id']} repeated: the core", file)]))
        inner = foot.buffer(-t_out, join_style=2)
        rest = inner.difference(unary_union([p.buffer(0.08, join_style=2) for p in core_polys])) if core_polys else inner
        pieces = [g for g in getattr(rest, "geoms", [rest]) if g.geom_type == "Polygon" and g.area >= MIN_ROOM_M2]
        store_label = "Bodrum" if new_lv["label"].endswith("Bodrum Kat") else "Basement store"
        stores = []
        for n, g in enumerate(sorted(pieces, key=lambda g: -g.area), start=1):
            sid = f"r_{lid}_store_{n}"
            poly = [[round(x, 4), round(y, 4)] for x, y in list(g.simplify(0.02).exterior.coords)[:-1]]
            stores.append((sid, g))
            new_rooms.append(dict(tag, id=sid, level_id=lid, label=store_label, label_raw=None,
                                  label_inferred={"method": RULE, "reason": "a basement store (no plan)"},
                                  room_type="storage", polygon=poly, area_computed=round(g.area, 3), area_label=None,
                                  floor_offset_m=0.0, floor_source="level", floor_evidence=[],
                                  has_documented_furniture=False, style_override=None, status="unverified",
                                  evidence=[_ev(f"the footprint of {ground['id']} outside its core: a basement store "
                                                f"(inferred)", file)]))
        # the openings: lift landing doors and the doors between core rooms; one way into each store; no window, no
        # outside door
        reached = set()
        for o in sorted(gl.openings, key=lambda o: (o.get("type") != "door", o["id"])):
            if o.get("wall_id") not in wall_map or o.get("type") not in ("door", "opening"):
                continue
            sides = CR._sides(gl, o)
            ids = [s[1]["id"] if s[1] is not None else None for s in sides]
            if len(ids) != 2 or not any(i in core for i in ids):
                continue
            other = [i for i in ids if i not in core]
            if other:
                q = next((s[2] for s in sides if (s[1] or {}).get("id") not in core), None)
                store = next((sid for sid, g in stores if q is not None and g.buffer(0.15).contains(Point(q))), None)
                if store is None or store in reached:
                    continue
                reached.add(store)
            elif None in ids:
                continue
            nid = _moved(o['id'], ground['id'], lid)
            ops.append(dict({kk: v for kk, v in o.items() if kk not in ("id", "level_id", "wall_id", "evidence")},
                            **tag, id=nid, level_id=lid, wall_id=wall_map[o["wall_id"]], basement_of=o["id"],
                            status="unverified",
                            evidence=[_ev(f"{o['id']} of {ground['id']} repeated: "
                                          + ("a lift landing door" if o.get("lift_door") else "a door of the core"),
                                          file)]))
        # the core's stairs: each rises from the basement to the ground floor
        for f in b.get("furniture") or []:
            if f.get("level_id") != ground["id"] or f.get("type") != "stair" or f.get("room_id") not in core:
                continue
            nid = _moved(f['id'], ground['id'], lid)
            st = dict(f.get("stair") or {})
            if st:
                st["reason"] = (st.get("reason") or "") + f"; repeated from {f['id']} on the inferred basement {lid}"
            furn.append(dict({kk: v for kk, v in f.items() if kk not in ("id", "level_id", "room_id", "evidence")},
                             **tag, id=nid, level_id=lid, room_id=room_map.get(f.get("room_id")), basement_of=f["id"],
                             source="added_by_ai", status="unverified", stair=st or f.get("stair"),
                             evidence=[_ev(f"the stair {f['id']} of {ground['id']} goes on down to the basement "
                                           f"(inferred)", file)]))
        for x in walls + new_rooms + ops + furn:
            if x.get("basement_of") is None:
                x.pop("basement_of", None)
        b["levels"].append(new_lv)
        b["levels"].sort(key=lambda lv: (lv.get("order") or 0, str(lv.get("id"))))
        b.setdefault("walls", []).extend(walls)
        b.setdefault("rooms", []).extend(new_rooms)
        b.setdefault("openings", []).extend(ops)
        b.setdefault("furniture", []).extend(furn)
        _slabs(build, b, new_lv, above, slab_default, file)
        rec_out = {"level_id": lid, "elevation": new_lv["elevation"], "ceiling_height": ceiling,
                   "walls": len(walls), "rooms": len(new_rooms), "openings": len(ops), "stairs": len(furn),
                   "core": sorted(core), "stores": [s for s, _g in stores], "reason": ev_text}
        out.append(rec_out)
        build.warn(f"{lid}: basement inferred ({item.get('rule')}): the footprint of {ground['id']} with its core "
                   f"({', '.join(sorted(core))}), {len(furn)} stair(s), {len(ops)} door(s), no window (inferred)")
        above = new_lv
    return out


def _slabs(build, b: dict, lv: dict, above: dict, slab_default: float, file: str) -> None:
    """The slab under the basement, and the basement stairs' openings in the slab over it (``to_building._slab``)."""
    from wenart.levels import model as LMO
    from wenart.sheets import to_building as TB

    def outline(lid):
        pts = LMO.level_outline(b, lid)
        return Polygon(pts) if pts and len(pts) >= 3 and Polygon(pts).is_valid else None

    fall = {x: p for x in (lv["id"], above["id"]) for p in [outline(x)] if p is not None}
    if lv["id"] not in fall:
        return
    slabs = b.setdefault("slabs", [])
    under = TB._slab(lv, None, fall, b.get("furniture") or [], None, slab_default, f"sl_{lv['id']}", b.get("rooms"),
                     None)
    if under is not None:
        under.update(inferred=True, status="assumed", evidence=[_ev(f"the slab under the inferred basement {lv['id']}: "
                                                                    f"its outer walls' outline (inferred)", file)])
        slabs.append(under)
    over = next((s for s in slabs if s.get("id") == f"sl_{above['id']}" and not s.get("variants")), None)
    cut = TB._slab(above, lv, fall, b.get("furniture") or [], None, slab_default, f"sl_{above['id']}", b.get("rooms"),
                   None) if above["id"] in fall else None
    if over is None and cut is not None:
        cut.update(inferred=True, status="assumed")
        slabs.append(cut)
    elif over is not None:
        over["below_level_id"] = lv["id"]
        have = {o.get("furniture_id") for o in over.get("openings") or []}
        for o in (cut or {}).get("openings") or []:
            if o.get("furniture_id") not in have:
                over.setdefault("openings", []).append(dict(o, id=f"sv_{above['id']}_b{len(over['openings']) + 1:03d}"))
