"""Cross-document findings RC8-RC12 (wenart.reading_check.crossdoc) and the elevation's line-assembled rectangles
(wenart.sheets.exterior.frame_rects), 4 Nov 2026 (Milestone 14 R5; user: "some AI or something else to give the
feedbacks by itself instead of me"). Hand-made building and sheets dicts: one hit and one clean case per check."""
from __future__ import annotations

import copy

from wenart.ingest.generic.model import Stroke
from wenart.reading_check import crossdoc as CD
from wenart.sheets import exterior as EX
from wenart.sheets.model import Ent, Region


# ------------------------------------------------------------------------------------------------------- fixtures
def _box_walls(lid: str, w: float = 10.0, d: float = 8.0, t: float = 0.2) -> list[dict]:
    pts = [(0.0, 0.0), (w, 0.0), (w, d), (0.0, d)]
    out = []
    for k in range(4):
        a, b = pts[k], pts[(k + 1) % 4]
        out.append({"id": f"w_{lid}_{k}", "level_id": lid, "start": list(a), "end": list(b), "thickness": t,
                    "height": 2.7, "exterior": True})
    return out


def _window(lid: str, n: int, x: float, wall: str = None, width: float = 1.2, kind: str = "window") -> dict:
    return {"id": f"o_{lid}_{n}", "type": kind, "level_id": lid, "wall_id": wall or f"w_{lid}_0", "center": [x, 0.0],
            "width": width, "height": 1.4 if kind == "window" else 2.1, "sill_height": 0.9 if kind == "window" else 0.0}


def _building(levels: list[tuple[str, float]], openings: list[dict], region: str = None) -> dict:
    walls, lvs = [], []
    for lid, z in levels:
        walls += _box_walls(lid)
        lvs.append({"id": lid, "label": lid, "order": int(z // 3), "elevation": z, "ceiling_height": 2.7,
                    "floor_to_floor": {"value": 3.0}, "base_level_id": None, "region_id": region or f"r_{lid}"})
    return {"levels": lvs, "walls": walls, "openings": openings, "rooms": [], "conflicts": [], "site": {}}


def _elevation(xs_by_floor: dict, side: str = "front") -> dict:
    pos = []
    for z, xs in xs_by_floor.items():
        for x in xs:
            pos.append({"kind": "window", "x": x, "x_left": x - 0.6, "width": 1.2, "sill": z + 0.9, "head": z + 2.3})
    return {"region_id": "r_el", "title": "ÖN CEPHE", "side": side, "windows": len(pos), "doors": 0,
            "positions_m": pos, "plan_check": {"matched": 0}}


# ---------------------------------------------------------------------------------------------------------------- RC8
def test_rc8_names_the_window_the_plan_lacks_per_floor():
    # plan: front windows at x 2 and 5 on L0, none on L1; the facade's left end is the outer face at x -0.1
    b = _building([("L0", 0.0), ("L1", 3.0)], [_window("L0", 1, 2.0), _window("L0", 2, 5.0)])
    b["facade"] = {"elevations": [_elevation({0.0: [2.1, 5.1, 8.1], 3.0: [2.1, 5.1]})]}
    found = [f for f in CD.rc8(b, {}) if f["check"] == "RC8" and f["severity"] != "info"]
    l0 = [f for f in found if f["level_id"] == "L0"]
    l1 = [f for f in found if f["level_id"] == "L1"]
    assert len(l0) == 1 and l0[0]["severity"] == "minor"
    assert "at x 8.10 m" in l0[0]["message"] and l0[0]["levels_missing"] == ["L0"]
    assert abs(l0[0]["place"]["x"] - 8.0) < 0.05 and abs(l0[0]["place"]["y"] + 0.1) < 0.05
    assert len(l1) == 1 and l1[0]["severity"] == "major"          # the plan has none where the elevation shows two
    assert l1[0]["sources"][0].startswith("elevation r_el")


def _column_case(side: str = "front"):
    lv = [("L0", 0.0), ("L1", 3.0), ("L2", 6.0), ("L3", 9.0)]
    ops = [_window(lid, k, x) for lid, _ in lv for k, x in ((1, 2.0), (2, 5.0))] + [_window("L0", 3, 8.0)]
    b = _building(lv, ops)
    b["facade"] = {"elevations": [_elevation({z: [2.1, 5.1, 8.1] for _, z in lv}, side=side)]}
    return b


def test_rc8_one_finding_per_column():
    # a window column at x 8.1 drawn on all four floors, missing on the plans of L1-L3: one major finding
    b = _column_case()
    found = [f for f in CD.rc8(b, {}) if f["severity"] != "info"]
    assert len(found) == 1 and found[0]["severity"] == "major"
    assert found[0]["levels_shown"] == ["L0", "L1", "L2", "L3"] and found[0]["levels_missing"] == ["L1", "L2", "L3"]
    # drawn on two floors only: minor
    b["facade"] = {"elevations": [_elevation({0.0: [2.1, 5.1, 8.1], 3.0: [2.1, 5.1, 8.1], 6.0: [2.1, 5.1],
                                              9.0: [2.1, 5.1]})]}
    found = [f for f in CD.rc8(b, {}) if f["severity"] != "info"]
    assert [f["severity"] for f in found] == ["minor"]


def test_rc8_drops_small_frames_and_glazed_strips():
    b = _building([("L0", 0.0), ("L1", 3.0)], [_window("L0", 1, 2.0), _window("L1", 1, 2.0)])
    el = _elevation({0.0: [2.1], 3.0: [2.1]})
    el["positions_m"] += [{"kind": "window", "x": 6.1, "width": 1.0, "sill": z, "head": z + 2.05}
                          for z in (0.5, 2.6, 4.7)]                       # a stair shaft's cells, 5 cm apart
    el["positions_m"].append({"kind": "window", "x": 8.0, "width": 0.4, "sill": 1.5, "head": 1.9})   # a vent
    b["facade"] = {"elevations": [el]}
    found = CD.rc8(b, {})
    assert [f for f in found if f["severity"] != "info"] == []
    info = [f for f in found if f.get("dropped")]
    assert info and info[0]["dropped"] == 4 and "glazed strip" in info[0]["message"]


def test_rc8_weak_north_fit_caps_severity(monkeypatch):
    b = _column_case(side="south")
    found = CD.rc8(b, {})
    info = next(f for f in found if "placed by fit" in f["message"])
    assert "margin" in info["message"] and info["north_margin"] >= CD.NORTH_MARGIN_MIN
    assert any(f["severity"] == "major" for f in found)
    monkeypatch.setattr(CD, "NORTH_MARGIN_MIN", 1.01)                     # every fit is weak now
    found = CD.rc8(b, {})
    assert not any(f["severity"] == "major" for f in found)
    assert any("weak fit" in f["message"] for f in found if f["severity"] == "minor")


def test_rc8_clean_when_the_elevation_matches_the_plan():
    b = _building([("L0", 0.0)], [_window("L0", 1, 2.0), _window("L0", 2, 5.0)])
    b["facade"] = {"elevations": [_elevation({0.0: [2.3, 5.3]})]}          # 0.2 m off: within the alignment
    assert [f for f in CD.rc8(b, {}) if f["severity"] != "info"] == []


def test_rc8_no_north_is_one_info_finding():
    b = _building([("L0", 0.0)], [_window("L0", 1, 2.0)])
    b["facade"] = {"elevations": [_elevation({0.0: [2.1]}, side="south")]}
    b["walls"] = [w for w in b["walls"] if w["id"] != "w_L0_0"]           # nothing fits any axis
    found = CD.rc8(b, {})
    assert [f["severity"] for f in found] == ["info"] and "north" in found[0]["message"]


def test_rc8_north_inferred_by_fit():
    b = _building([("L0", 0.0)], [_window("L0", 1, 2.0), _window("L0", 2, 5.0)])
    b["facade"] = {"elevations": [_elevation({0.0: [2.1, 5.1, 8.1]}, side="south")]}
    found = CD.rc8(b, {})
    assert any(f["severity"] == "info" and "placed by fit" in f["message"] for f in found)
    hit = [f for f in found if f["severity"] == "minor"]
    assert hit and hit[0]["north_inferred_deg"] == 0.0


def test_rc8_stacked_window_on_one_floor_of_a_typical_plan():
    # UL303 (real10): the bedroom window on L0 only; L1 and L2 are drawn by the same plan
    b = _building([("L0", 0.0), ("L1", 3.0), ("L2", 6.0)],
                  [_window("L0", 1, 2.0), _window("L1", 1, 2.0), _window("L2", 1, 2.0), _window("L0", 2, 5.0)],
                  region="r8")
    found = CD.rc8_stacked(b)
    assert len(found) == 1 and found[0]["severity"] == "major" and found[0]["missing_levels"] == ["L1", "L2"]
    b["openings"] += [_window("L1", 2, 5.0), _window("L2", 2, 5.1)]
    assert CD.rc8_stacked(b) == []


# ---------------------------------------------------------------------------------------------------------------- RC9
def test_rc9_storey_out_of_range_and_ground_too_low():
    b = _building([("L0", 0.0), ("L1", 3.0), ("L2", 12.0)], [])
    sheets = {"heights": {"section_regions": ["r1"], "ground": [{"side": "all", "z": {"value": -7.0}}]}}
    found = CD.rc9(b, sheets)
    msgs = " | ".join(f["message"] for f in found)
    assert any(f["level_id"] == "L1" and "9.00 m" in f["message"] and f["severity"] == "major" for f in found), msgs
    assert any("ground line at -7.00" in f["message"] and f["severity"] == "major" for f in found), msgs


def test_rc9_clean_and_conflicts_surface():
    b = _building([("L0", 0.0), ("L1", 3.0)], [])
    sheets = {"heights": {"section_regions": ["r1"], "ground": [{"side": "all", "z": {"value": -0.15}}],
                          "levels": [{"level_id": "L0", "floor_z": {"value": 0.0, "method": "vector"}},
                                     {"level_id": "L1", "floor_z": {"value": 3.0, "method": "vector"}}]}}
    assert CD.rc9(b, sheets, {0: "Zemin Kat", 1: "1. Kat"}, {0: 2.5, 1: 5.5}) == []
    b["conflicts"] = [{"id": "c_1", "kind": "other", "element_ids": ["r1"],
                       "description": "sheets.json sc_002: section r1 draws 9 slab bands, the plans 10 levels"}]
    found = CD.rc9(b, sheets)
    assert len(found) == 1 and found[0]["severity"] == "major" and found[0]["conflict"] == "c_1"


def test_rc9_doors_under_the_ground_and_storey_marks():
    # UL308 (real10): the ground read high, the basement's terrace doors under it
    b = _building([("L-1", -3.0), ("L0", 0.0)], [_window("L-1", 1, 2.0, kind="door"), _window("L-1", 2, 5.0, kind="door")])
    sheets = {"heights": {"section_regions": ["r1"], "ground": [{"side": "all", "z": {"value": -0.15}}],
                          "datum": {"value": 2.5}}}
    found = CD.rc9(b, sheets, {-1: "1. Bodrum Kat", 0: "Zemin Kat", 3: "3. Kat"}, {-1: -0.5, 0: 2.6})
    msgs = [f["message"] for f in found]
    assert any("2 door(s) in its outer walls end under" in m for m in msgs), msgs
    assert any("names 3. Kat (order 3)" in m for m in msgs), msgs
    assert any("L0: section r1 marks its storey at +2.60" in m for m in msgs), msgs


# --------------------------------------------------------------------------------------------------------------- RC10
def test_rc10_two_blocks_one_building_and_a_spaced_pool_label():
    b = _building([("L0", 0.0)], [])
    texts = ["YERLEŞİM PLANI", "A BLOK", "B BLOK", "H A V U Z"]
    found = CD.rc10(b, {"exterior": {"site": {"region": "r1", "registered": True}}}, texts)
    major = [f for f in found if f["severity"] == "major"]
    assert len(major) == 1 and "names 2 buildings" in major[0]["message"]
    assert any(f["severity"] == "minor" and "pool" in f["message"] for f in found)
    assert CD.named_buildings(["2 ADET VİLLA"])[0] == 2
    # real07: the pool label is written in two overlapping letter-spaced texts
    assert CD.interleaved_labels([{"text": "H   V   Z", "box": [0.0, 0.0, 0.8, 0.1]},
                                  {"text": "A   U", "box": [0.0, 0.01, 0.6, 0.09]}]) == ["HAVUZ"]


def test_rc10_clean_and_plot_check():
    b = _building([("L0", 0.0)], [])
    b["site"] = {"plot": {"polygon": [[-5, -5], [20, -5], [20, 20], [-5, 20]]}, "pools": []}
    assert CD.rc10(b, {}, ["A BLOK", "BAHÇE"]) == []
    b["site"]["plot"]["polygon"] = [[-5, -5], [6, -5], [6, 20], [-5, 20]]
    found = CD.rc10(b, {}, [])
    assert len(found) == 1 and found[0]["severity"] == "major" and "outside" in found[0]["message"]


# --------------------------------------------------------------------------------------------------------------- RC11
def test_rc11_tag_with_no_opening_of_its_width():
    # UL321 (real07): the heating room's 80/210 door read as a 1.56 m gap
    walls = _box_walls("L0")
    gap = dict(_window("L0", 1, 4.0, width=1.56, kind="opening"), type_raw="gap")
    tags = CD.size_tags([{"text": "80/210", "x": 4.2, "y": 0.4, "layer": "DOĞRAMA", "entity": "TEXT:1"},
                         {"text": "30/60", "x": 4.2, "y": 0.4, "layer": "KOLON", "entity": "TEXT:2"}])
    assert len(tags) == 1 and tags[0]["w"] == 0.8
    found = CD.rc11("L0", tags, walls, [gap])
    assert len(found) == 1 and found[0]["severity"] == "minor"
    assert "1.56 m wide" in found[0]["message"] and found[0]["element_ids"] == ["o_L0_1"]
    door = _window("L0", 1, 4.0, width=0.8, kind="door")
    assert CD.rc11("L0", tags, walls, [door]) == []
    tags3 = [dict(tags[0], x=x) for x in (2.0, 5.0, 8.0)]
    assert {f["severity"] for f in CD.rc11("L0", tags3, walls, [])} == {"major"}


# --------------------------------------------------------------------------------------------------------------- RC12
def _twin_building(windows_b: int) -> dict:
    b = _building([("L0", 0.0)], [])
    b["walls"].append({"id": "w_L0_mid", "level_id": "L0", "start": [5.0, 0.0], "end": [5.0, 8.0], "thickness": 0.2,
                       "exterior": False})
    a_poly = [[0.1, 0.1], [4.9, 0.1], [4.9, 7.9], [0.1, 7.9]]
    b_poly = [[5.1, 0.1], [9.9, 0.1], [9.9, 7.9], [5.1, 7.9]]
    b["rooms"] = [{"id": "r_a", "level_id": "L0", "label": "Oda", "polygon": a_poly, "area_computed": 37.44},
                  {"id": "r_b", "level_id": "L0", "label": "Oda", "polygon": b_poly, "area_computed": 37.44,
                   "twin_of": "r_a", "twin_transform": [-1, 0, 10, 0, 1, 0], "twin_residual_m": 0.01}]
    b["openings"] = [_window("L0", 1, 1.5), _window("L0", 2, 3.5)] + \
        [_window("L0", 3 + k, 8.5 - 2 * k) for k in range(windows_b)]
    return b


def test_rc12_twin_pair_differing_in_windows():
    found = CD.rc12(_twin_building(1))
    assert len(found) == 1 and found[0]["severity"] == "major" and "1 windows / 2" in found[0]["message"]
    assert CD.rc12(_twin_building(2)) == []


def test_rc12_typical_copy_counts():
    b = _building([("L0", 0.0), ("L1", 3.0)], [_window("L0", 1, 2.0), _window("L1", 1, 2.0), _window("L0", 2, 5.0)])
    b["levels"][1]["typical_of"] = "L0"
    found = CD.rc12(b)
    assert len(found) == 1 and found[0]["severity"] == "major" and "windows 2 on L0 / 1 on L1" in found[0]["message"]
    c = copy.deepcopy(b)
    c["walls"] = [w for w in c["walls"] if w["level_id"] != "L1"]
    c["openings"] = [o for o in c["openings"] if o["level_id"] != "L1"]
    assert [f["severity"] for f in CD.rc12(c)] == ["info"]


# ----------------------------------------------------------------------------------- the elevation's rectangles
def _lines(ents: list, box, layer: str = "0", sides=(True, True, True, True)):
    x0, y0, x1, y1 = box
    edges = [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]
    for k, (a, b) in enumerate(edges):
        if sides[k]:
            n = len(ents)
            st = Stroke(id=f"ent:{n}", kind="line", pts=[a, b], layer=layer)
            ents.append(Ent(id=f"LINE:{n}", kind="LINE", layer=layer, box=st.bbox(), strokes=[st]))


def _line(ents, a, b, layer="0"):
    n = len(ents)
    st = Stroke(id=f"ent:{n}", kind="line", pts=[a, b], layer=layer)
    ents.append(Ent(id=f"LINE:{n}", kind="LINE", layer=layer, box=st.bbox(), strokes=[st]))


def test_frame_rects_from_loose_lines_and_nested_frames():
    ents: list = []
    _line(ents, (-1.0, 0.0), (20.0, 0.0))                              # the ground line
    _line(ents, (0.0, 0.0), (0.0, 3.0))                                # the facade's left wall line, on the ground
    # a window drawn as three nested rectangles of loose LINEs with a mullion, its sill a long band line (T joints)
    _lines(ents, (2.0, 1.0, 3.4, 2.4), sides=(False, True, True, True))
    _line(ents, (1.0, 1.0), (6.0, 1.0), layer="PENCERE")
    _lines(ents, (2.05, 1.05, 3.35, 2.35))
    _lines(ents, (2.1, 1.1, 3.3, 2.3))
    _line(ents, (2.7, 1.1), (2.7, 2.3))
    # a door at the ground with its leaf
    _lines(ents, (8.0, 0.0, 9.0, 2.1))
    _lines(ents, (8.05, 0.0, 8.95, 2.05))
    # a plain balcony panel (no inner line): no window
    _lines(ents, (12.0, 1.0, 13.2, 1.9))
    rects = EX.frame_rects(ents, 1.0)
    framed = [r for r in rects if r["framed"]]
    assert any(abs(r["box"][0] - 2.0) < 1e-6 and abs(r["box"][3] - 2.4) < 1e-6 for r in framed)
    assert not any(abs(r["box"][0] - 12.0) < 1e-6 and r["framed"] for r in rects)
    region = Region(id="r_el", file="x.dxf", sheet=None, box=(-1.0, 0.0, 20.0, 2.4), geometry_box=(-1.0, 0.0, 20.0, 2.4),
                    ents=ents, title={"text": "ÖN CEPHE"})
    region.metres_per_unit = 1.0
    _, seen = EX.facade_of(region, None, None, [])
    assert seen["windows"] == 1 and seen["doors"] == 1
    # a door drawn as one open three-sided polyline standing on the ground line counts without an inner frame
    st = Stroke(id="ent:door3", kind="polyline", pts=[(15.0, 0.0), (15.0, 2.1), (16.0, 2.1), (16.0, 0.0)], layer="0")
    ents.append(Ent(id="LWPOLYLINE:9", kind="LWPOLYLINE", layer="0", box=st.bbox(), strokes=[st]))
    _, seen = EX.facade_of(region, None, None, [])
    assert seen["windows"] == 1 and seen["doors"] == 2
    win = next(p for p in seen["positions_m"] if p["kind"] == "window")
    assert abs(win["width"] - 1.4) < 1e-6 and abs(win["sill"] - 1.0) < 1e-6 and abs(win["x"] - 2.7) < 1e-6
