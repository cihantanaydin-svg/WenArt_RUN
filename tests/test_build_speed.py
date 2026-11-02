"""The build's prepare on a large building (2 Nov 2026, real10 run 20261101-233829-full: a 9-floor apartment block whose
build was still in the architect's default search after three hours): the typical floors' defaults in units, the
refused defaults found by halving, and the geometry helpers that ran per round made fast with the same results."""
import random

from wenart import geometry as G
from wenart.blender import build as BD
from wenart.blender import geom2d


def _block(levels=("L0", "L1", "L2")):
    b = {"levels": [{"id": "L0"}] + [{"id": lv, "typical_of": "L0"} for lv in levels[1:]],
         "walls": [], "openings": [], "rooms": [], "furniture": []}
    for lv in levels:
        b["openings"].append({"id": f"d_{lv}_024", "level_id": lv, "center": [16.74, 17.115]})
        b["furniture"].append({"id": f"f_{lv}_003", "level_id": lv,
                               "footprint": {"center": [3.65, 5.55] if lv != "L2" else [6.0, 5.55]}})
    return b


def test_typical_units_join_copies_at_the_same_place():
    b = _block()
    keys = ["E1:d_L0_024", "E1:d_L1_024", "E1:d_L2_024", "H1:f_L0_003", "H1:f_L1_003", "H1:f_L2_003",
            "W9:L1", "W9:L0"]
    units = BD.typical_units(b, keys)
    assert units["E1:d_L0_024"] == ["E1:d_L0_024", "E1:d_L1_024", "E1:d_L2_024"]
    # the L2 piece stands elsewhere (placed on its own): its own unit
    assert units["H1:f_L0_003"] == ["H1:f_L0_003", "H1:f_L1_003"]
    assert units["H1:f_L2_003"] == ["H1:f_L2_003"]
    assert units["W9:L0"] == ["W9:L0", "W9:L1"]
    assert sorted(k for ks in units.values() for k in ks) == sorted(keys)


def test_typical_units_without_typical_floors_are_single_keys():
    b = {"levels": [{"id": "L0"}, {"id": "L1"}], "openings": [{"id": "d_L1_001", "center": [0, 0]}]}
    assert BD.typical_units(b, ["E1:d_L1_001", "E1:d_L0_001"]) == {"E1:d_L0_001": ["E1:d_L0_001"],
                                                                  "E1:d_L1_001": ["E1:d_L1_001"]}


def test_refused_units_finds_the_bad_units_by_halving():
    bad = {"u07": {"X:1"}, "u31": {"Y:2"}}
    names = [f"u{i:02d}" for i in range(40)]
    calls = []

    def opens(group):
        calls.append(len(group))
        return set().union(*(bad.get(u, set()) for u in group))

    got = BD.refused_units(names, opens, opens(names))
    assert got == bad
    assert len(calls) < 30                     # one at a time would be 40 plans

    calls.clear()
    assert BD.refused_units(names, opens, set()) == {}
    assert calls == []                         # all kept: nothing asked again


def test_rect_union_outline_large_grid_unchanged():
    """The covered cells by bisection give the same loops as the cell-by-box test (a floor of thin wall boxes)."""
    random.seed(5)
    rects = []
    for _ in range(120):
        x, y = random.randint(0, 60) * 0.25, random.randint(0, 60) * 0.25
        if random.random() < 0.5:
            rects.append((x, y, x + random.randint(2, 30) * 0.25, y + 0.2))
        else:
            rects.append((x, y, x + 0.2, y + random.randint(2, 30) * 0.25))
    loops = geom2d.rect_union_outline(rects)

    xs = sorted({v for r in rects for v in (r[0], r[2])})
    ys = sorted({v for r in rects for v in (r[1], r[3])})
    cells = {(i, j) for i in range(len(xs) - 1) for j in range(len(ys) - 1)
             if any(r[0] < (xs[i] + xs[i + 1]) / 2 < r[2] and r[1] < (ys[j] + ys[j + 1]) / 2 < r[3] for r in rects)}
    area = sum((xs[i + 1] - xs[i]) * (ys[j + 1] - ys[j]) for i, j in cells)
    assert abs(sum(G.polygon_signed_area(lp) for lp in loops) - area) < 1e-6


def test_wall_outline_cache_returns_copies():
    walls = [{"start": [0, 0], "end": [5, 0], "thickness": 0.2}, {"start": [5, 0], "end": [5, 4], "thickness": 0.2},
             {"start": [5, 4], "end": [0, 4], "thickness": 0.2}, {"start": [0, 4], "end": [0, 0], "thickness": 0.2}]
    a, method = geom2d.wall_outline(walls)
    a.append((99.0, 99.0))
    b, method2 = geom2d.wall_outline(walls)
    assert (99.0, 99.0) not in b and method == method2 == "wall_union"
    assert len(b) == 4


def test_drop_collinear_keeps_corners_in_order():
    pts = [(0, 0)] + [(x * 0.1, 0.0) for x in range(1, 50)] + [(5, 0), (5, 3), (2.5, 3), (0, 3), (0, 1.5)]
    assert geom2d._drop_collinear(pts) == [(0, 0), (5, 0), (5, 3), (0, 3)]


def test_simple_polygon_sweep():
    assert geom2d.simple_polygon([(0, 0), (4, 0), (4, 3), (0, 3)])
    assert not geom2d.simple_polygon([(0, 0), (4, 3), (4, 0), (0, 3)])            # a bow tie
    assert not geom2d.simple_polygon([(0, 0), (4, 0), (4, 3), (2, 0), (0, 3)])    # a vertex on an edge
    comb = [(0, 0), (20, 0), (20, 1)] + [p for k in range(19, 0, -1) for p in ((k + 0.5, 1), (k + 0.5, 3), (k, 3),
                                                                            (k, 1))] + [(0, 1)]
    assert geom2d.simple_polygon(comb)


def test_point_in_polygon_edges_still_count():
    sq = [(0, 0), (2, 0), (2, 2), (0, 2)]
    assert G.point_in_polygon((1, 0), sq) and G.point_in_polygon((2, 2), sq) and G.point_in_polygon((1, 1), sq)
    assert not G.point_in_polygon((2.000001, 1), sq) and not G.point_in_polygon((-1, 1), sq)


def _furnished_block():
    from copy import deepcopy
    b = {"levels": [{"id": "L0", "elevation": 0.0}, {"id": "L1", "elevation": 3.0, "typical_of": "L0"}],
         "rooms": [{"id": "r_L0_salon", "level_id": "L0", "polygon": [[0, 0], [4, 0], [4, 4]]},
                   {"id": "r_L1_salon", "level_id": "L1", "polygon": [[0, 0], [4, 0], [4, 4]]}],
         "walls": [{"id": "w_L0_001", "level_id": "L0", "start": [0, 0], "end": [4, 0], "thickness": 0.2},
                   {"id": "w_L1_001", "level_id": "L1", "start": [0, 0], "end": [4, 0], "thickness": 0.2}],
         "furniture": [{"id": "f_L0_001", "level_id": "L0", "room_id": "r_L0_salon", "type": "sofa",
                        "asset": {"asset_id": "hssd_a", "role_set": {"group_id": "r_L0_salon:seating"}},
                        "evidence": [{"entity": "sym_L0_004", "file": "x.dxf"}],
                        "footprint": {"center": [2, 1], "size": [2, 0.9], "rotation_deg": 0}},
                       {"id": "f_L1_007", "level_id": "L1", "room_id": "r_L1_salon", "type": "armchair",
                        "footprint": {"center": [1, 3], "size": [0.8, 0.8], "rotation_deg": 0}}],
         "decor": [{"id": "dec_L0_001", "level_id": "L0", "room_id": "r_L0_salon", "host_id": "f_L0_001",
                    "slot": "f_L0_001:seat", "floor_z": 0.0, "center": [2, 1]}]}
    return b, deepcopy(b)


def test_furnish_typical_copies_moves_ids_and_references():
    from wenart.blender.typical_copies import furnish_typical_copies
    b, before = _furnished_block()
    recs = furnish_typical_copies(b)
    assert [r["object"] for r in recs] == ["level_L1"] and recs[0]["counts"]["furniture"] == {"was": 1, "now": 1}
    f1 = [f for f in b["furniture"] if f["level_id"] == "L1"]
    assert [f["id"] for f in f1] == ["f_L1_001"] and f1[0]["room_id"] == "r_L1_salon"
    assert f1[0]["typical_copy_of"] == "f_L0_001" and f1[0]["type"] == "sofa"
    assert f1[0]["asset"]["role_set"]["group_id"] == "r_L1_salon:seating"
    assert f1[0]["evidence"] == [{"entity": "sym_L0_004", "file": "x.dxf"}]          # the real source stays
    d1 = [d for d in b["decor"] if d["level_id"] == "L1"][0]
    assert (d1["id"], d1["host_id"], d1["slot"], d1["floor_z"]) == ("dec_L1_001", "f_L1_001", "f_L1_001:seat", 3.0)
    assert [f for f in b["furniture"] if f["level_id"] == "L0"] == [f for f in before["furniture"]
                                                                    if f["level_id"] == "L0"]


def test_copy_entries_and_summary():
    from wenart.blender import typical_copies as TC
    entries = [{"name": "furn_f_L0_001", "wenart_id": "f_L0_001", "level_id": "L0", "room_id": "r_L0_salon",
                "center": [2, 1, 0.4], "box3d": {"center": [2, 1, 0.4]}, "file": "lib/f_L0_x.glb"},
               {"name": "not_copied", "wenart_id": "x"}]
    got = TC.copy_entries(entries, {"furn_f_L0_001": "furn_f_L1_001"}, "L0", "L1", 3.0)
    assert len(got) == 1
    e = got[0]
    assert (e["name"], e["wenart_id"], e["level_id"], e["room_id"]) == ("furn_f_L1_001", "f_L1_001", "L1", "r_L1_salon")
    assert e["center"] == [2, 1, 3.4] and e["box3d"]["center"] == [2, 1, 3.4] and e["file"] == "lib/f_L0_x.glb"
    assert e["typical_copy_of"] == "furn_f_L0_001" and entries[0]["center"] == [2, 1, 0.4]
    s = TC.copy_summary({"pieces": 1, "objects": {"f_L0_001": object()}, "slowest": [1],
                         "not_built": [{"id": "f_L0_009"}]}, "L0", "L1", {"f_L1_001": None})
    assert s["not_built"] == [{"id": "f_L1_009"}] and "slowest" not in s and s["objects"] == {"f_L1_001": None}
    name_of, id_of = TC.renamer("L0", "L1")
    assert name_of("decor_dec_L0_003") == "decor_dec_L1_003" and name_of("4364 > root") == "4364 > root@L1"
    assert id_of("f_L0_001") == "f_L1_001" and id_of(5) == 5
