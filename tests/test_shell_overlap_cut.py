"""An opening cuts every wall that overlaps it (pod P5, 11 Oct 2026, ``shell.foreign_cuts``).

real03's facade line ``w_L0_002`` (0.15 m, y 0.075, x 16.65-30.05) runs along the outer face of ``w_L0_005``
(0.45 m, y 0.225, x 13.05-19.56). The window ``win_L0_002`` (2.55 m at x 18.08) was cut out of its own wall only, so
the thin wall closed it: from inside a dark recess, from outside a sill without glass, and the bedroom behind it
(daylight window, so no ceiling light) rendered black. Now the opening is cut through both walls.

CPU: the cutter of the overlapping wall (centre, depth) on the real03 numbers; parallel walls side by side, a cross
wall and a wall that misses the opening get none. Blender (``WENART_BLENDER``): a small building with the same
overlap (the thin wall running past both ends of the thick one, which the overlap trim leaves whole); a ray through
the window passes both walls, one under the sill and one beside the window hits them."""
from __future__ import annotations

import json
import textwrap

import pytest

from wenart.blender import cli, shell

BLENDER = cli.find_blender()
needs_blender = pytest.mark.skipif(BLENDER is None, reason="no Blender binary (WENART_BLENDER)")
EV = [{"file": "sheet.dxf", "page": 1, "method": "vector", "confidence": 1.0}]


def wall(wid, start, end, thickness, exterior=True, level="L0"):
    return {"id": wid, "level_id": level, "start": start, "end": end, "thickness": thickness, "height": 2.7,
            "exterior": exterior, "status": "verified", "evidence": EV}


def window(oid, wall_id, center, width):
    return {"id": oid, "type": "window", "level_id": "L0", "wall_id": wall_id, "center": center, "width": width,
            "height": 1.2, "sill_height": 0.9, "status": "verified", "evidence": EV}


def test_the_real03_facade_line_is_cut_at_the_bedroom_window():
    w5 = wall("w_L0_005", [13.054, 0.225], [19.563, 0.225], 0.45)
    w2 = wall("w_L0_002", [16.654, 0.075], [30.054, 0.075], 0.15)
    win1 = window("win_L0_001", "w_L0_005", [15.2039, 0.2253], 2.9)
    win2 = window("win_L0_002", "w_L0_005", [18.0789, 0.2253], 2.55)
    walls = {w["id"]: w for w in (w5, w2)}
    cuts = shell.foreign_cuts(w2, walls, [win1, win2])
    assert [o["id"] for o, _c, _d in cuts] == ["win_L0_002"]       # win_L0_001 (x 13.75-16.65) misses w_L0_002
    _o, (cx, cy), depth = cuts[0]
    assert cx == pytest.approx(18.0789, abs=1e-4)
    # across both: the thick wall spans y 0.0-0.45, the thin one 0.0-0.15: centre y 0.225, depth 0.45
    assert cy == pytest.approx(0.225, abs=1e-4) and depth == pytest.approx(0.45, abs=1e-4)
    assert shell.foreign_cuts(w5, walls, [win1, win2]) == []      # its own openings are cut the usual way


def test_walls_side_by_side_across_or_apart_get_no_cut():
    host = wall("w_a", [0.0, 0.0], [6.0, 0.0], 0.2)
    win = window("win_a", "w_a", [3.0, 0.0], 1.0)
    beside = wall("w_b", [0.0, 0.3], [6.0, 0.3], 0.2)              # parallel, 0.1 m gap: not overlapping
    across = wall("w_c", [3.0, -1.0], [3.0, 1.0], 0.2)              # a cross wall through the window
    apart = wall("w_d", [4.0, 0.05], [9.0, 0.05], 0.1)              # overlapping wall that starts past the window
    walls = {w["id"]: w for w in (host, beside, across, apart)}
    for w in (beside, across, apart):
        assert shell.foreign_cuts(w, walls, [win]) == [], w["id"]
    partial = wall("w_e", [3.4, 0.05], [9.0, 0.05], 0.1)            # overlaps the window's last 0.1 m
    walls["w_e"] = partial
    (_o, (cx, cy), depth), = shell.foreign_cuts(partial, walls, [win])
    assert (cx, cy) == pytest.approx((3.0, 0.0), abs=1e-9) and depth == pytest.approx(0.2)


def _building() -> dict:
    room = {"id": "r_L0_bed", "level_id": "L0", "label": "Bed", "room_type": "bedroom",
            "polygon": [[0.45, 0.45], [5.55, 0.45], [5.55, 4.0], [0.45, 4.0]], "area_computed": 18.1,
            "status": "verified", "evidence": EV}
    return {"schema_version": "0.1", "status": "ok", "project": {"id": "overlap", "brief": {}}, "documents": [],
            "levels": [{"id": "L0", "label": "Zemin", "order": 0, "elevation": 0.0, "ceiling_height": 2.7,
                        "evidence": EV}],
            # w_2 runs past both ends of w_5: no end lies inside it, so trim_wall_overlaps leaves it whole (real03's
            # w_L0_002 was not trimmed either: its end edge lies 0.1 mm outside w_L0_005)
            "walls": [wall("w_5", [0.0, 0.225], [6.0, 0.225], 0.45), wall("w_2", [-1.0, 0.075], [8.0, 0.075], 0.15),
                      wall("w_w", [0.225, 0.45], [0.225, 4.1], 0.45), wall("w_e", [5.775, 0.45], [5.775, 4.1], 0.45),
                      wall("w_n", [0.0, 4.075], [6.0, 4.075], 0.15)],
            "openings": [window("win_1", "w_5", [4.0, 0.225], 1.2)],
            "rooms": [room], "furniture": [], "decor": [], "conflicts": [], "unverified": [], "warnings": []}


DUMP = textwrap.dedent("""
    import bpy, json, sys
    from mathutils import Vector
    out = sys.argv[sys.argv.index("--") + 1]
    rows = {}
    for ob in bpy.data.objects:
        if ob.type != "MESH" or ob.get("wenart_kind") != "wall" or str(ob.get("wenart_id")) not in ("w_5", "w_2"):
            continue
        hits = {}
        for name, (x, z) in {"window": (4.0, 1.5), "under_sill": (4.0, 0.5), "beside": (2.5, 1.5)}.items():
            hits[name] = bool(ob.ray_cast(ob.matrix_world.inverted() @ Vector((x, -2.0, z)),
                                          Vector((0.0, 1.0, 0.0)))[0])
        rows[str(ob.get("wenart_id"))] = hits
    json.dump(rows, open(out, "w"))
""")


@needs_blender
def test_a_window_passes_through_an_overlapping_facade_wall(tmp_path):
    path = tmp_path / "overlap.json"
    path.write_text(json.dumps(_building()), encoding="utf-8")
    manifest_path = cli.build(path, tmp_path / "scene", no_textures=True, preview_samples=1)
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    (tmp_path / "dump.py").write_text(DUMP, encoding="utf-8")
    dump = tmp_path / "walls.json"
    cli.run_blender(tmp_path / "dump.py", [str(dump)], blend=str(manifest_path.parent / "scene.blend"))
    hits = json.loads(dump.read_text(encoding="utf-8"))
    assert hits["w_5"] == {"window": False, "under_sill": True, "beside": True}
    assert hits["w_2"] == {"window": False, "under_sill": True, "beside": True}
    entry = next(o for o in m["objects"] if o["kind"] == "wall" and o["wenart_id"] == "w_2")
    assert entry["cut_through"] == ["win_1"] and "problems" not in (entry.get("after_cuts") or {})
    assert any(a.get("field") == "cut_through" and a["object"] == "w_2" for a in m["assumed"])
