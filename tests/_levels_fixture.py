"""A small hand-made building for the level tests (Milestone 12, track L): one level, two rooms, a front door, an
inner door and a window. Walls on the centre-line rectangle (0, 0)-(10, 8), 0.2 m thick (outer faces at -0.1 and
10.1 / 8.1); a living room west of the inner wall at x = 6, a hall east of it; the front door on the south wall at
x = 8 (the hall), the inner door at (6, 4), a window on the south wall at x = 3."""
from __future__ import annotations

import copy

EV = {"file": "t.dxf", "page": None, "layer": "DUVAR", "entity": "LINE:1", "method": "vector", "confidence": 1.0}


def _wall(wid, a, b, exterior=True, level="L0", t=0.2):
    return {"id": wid, "level_id": level, "start": list(a), "end": list(b), "thickness": t, "height": None,
            "exterior": exterior, "status": "verified", "evidence": [dict(EV, entity=f"LINE:{wid}")]}


def _room(rid, poly, rtype, level="L0", label=None):
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return {"id": rid, "level_id": level, "label": label or rtype.title(), "label_raw": label or rtype.upper(),
            "room_type": rtype, "polygon": [list(p) for p in poly],
            "area_computed": round((max(xs) - min(xs)) * (max(ys) - min(ys)), 3), "area_label": None,
            "has_documented_furniture": False, "status": "verified", "evidence": [dict(EV, entity=f"room:{rid}")]}


def _opening(oid, kind, wall, centre, width, level="L0"):
    return {"id": oid, "type": kind, "level_id": level, "wall_id": wall, "center": list(centre), "width": width,
            "height": None, "sill_height": None, "swing_side": None, "status": "verified",
            "evidence": [dict(EV, entity=f"INSERT:{oid}")]}


def building(label: str = "Zemin Kat", order=0, elevation: float = 0.0) -> dict:
    """The single-level building (no slabs, roof or site)."""
    return copy.deepcopy({
        "schema_version": "0.1",
        "project": {"id": "levels-test", "source_folder": "projects/levels-test", "created_utc": "2026-10-10T00:00:00Z",
                    "pipeline_commit": "test", "brief": {}},
        "status": "ok", "documents": [{"id": "doc_1", "file": "t.dxf", "format": "dxf", "pages": []}],
        "levels": [{"id": "L0", "label": label, "order": order, "elevation": elevation, "ceiling_height": 2.7,
                    "ceiling_height_source": "assumed_default", "evidence": [dict(EV)]}],
        "walls": [_wall("w_1", (0, 0), (10, 0)), _wall("w_2", (10, 0), (10, 8)), _wall("w_3", (10, 8), (0, 8)),
                  _wall("w_4", (0, 8), (0, 0)), _wall("w_5", (6, 0), (6, 8), exterior=False)],
        "openings": [_opening("d_front", "door", "w_1", (8.0, 0.0), 1.0),
                     _opening("d_inner", "door", "w_5", (6.0, 4.0), 0.9),
                     _opening("win_1", "window", "w_1", (3.0, 0.0), 1.5)],
        "rooms": [_room("r_living", [(0.1, 0.1), (5.9, 0.1), (5.9, 7.9), (0.1, 7.9)], "living", label="Salon"),
                  _room("r_hall", [(6.1, 0.1), (9.9, 0.1), (9.9, 7.9), (6.1, 7.9)], "hall", label="Hol")],
        "furniture": [], "conflicts": [], "unverified": [], "warnings": [], "site": None,
    })


def mark(mid: str, value: float, kind=None, point=None, room_id=None, level="L0", relative=True, absolute=None,
         note=False, raw=None, method="vector", placement=None, **extra) -> dict:
    """A level mark record as ``wenart.levels.read`` writes it (building z = value)."""
    rec = {"id": mid, "value": value, "relative": relative, "absolute": absolute, "kind": kind,
           "point": list(point) if point is not None else None, "level_id": level, "room_id": room_id, "side": None,
           "raw": raw or f"{value:+.2f}", "used_for": [], "status": "verified" if method == "vector" else "unverified",
           "evidence": [dict(EV, method=method, entity=f"TEXT:{mid}", text=raw or f"{value:+.2f}")], "note": note,
           "placement": placement or ("note" if note else "spot"), "z": value}
    rec.update(extra)
    return rec
