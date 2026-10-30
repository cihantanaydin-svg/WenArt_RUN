"""UL205 (30 Oct 2026): "Nice inspiration for toilet solution" (the user's photo of a WC: a half-height installation wall
behind the wall-hung WC and the basin with lit niches along its top, a long thin backlit mirror over it, a matt black
vessel basin on an oak trestle bench with a black wall mixer, a brush and a roll holder beside the WC). Every wall-hung
WC in a WC, or on a bathroom wall without the family's fluted wall, hangs on an installation wall; a WC's basin on the
same wall stands on its face; the families that like it put a WC's basin on the bench. Pure tests on hand-made rooms
(tests/_m11_room.py) and, when the main repository holds it, real04's bathrooms of run 20261030-112241-full."""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

import _m11_room as M
import test_bathroom_details_20261029 as T
from wenart.blender import bath_parts as BT
from wenart.blender import furniture as BF
from wenart.blender import modules as MOD
from wenart.blender import parametric as P
from wenart.furniture import bath_details as BD

ROOM = M.ROOM_ID
REAL04 = Path("/home/user/WenArt_RUN/runs/20261030-112241-full/results/furniture/real04/building_final.json")


def wc_room(family: str, wc_d: float = 0.69, basin_size=(0.8, 0.55)) -> tuple[dict, dict]:
    """A 2.2 x 1.5 m WC: the WC (0.5 wide) and the basin on the north wall facing south, the door on the south wall."""
    t = M.fp("t1", "toilet", (1.55, 1.5 - wc_d / 2.0), (0.5, wc_d), rotation=0.0)
    w = M.fp("w1", "washbasin", (0.6, 1.5 - basin_size[1] / 2.0), basin_size, rotation=0.0)
    b = M.building(w=2.2, h=1.5, room_type="wc", window=None, furniture=[t, w], door_x=1.6)
    b["rooms"][0]["label"] = "WC"
    st = T.style_of(family)
    BD.plan_building(b, st)
    return b, st


def mirror(x: float = 0.6) -> dict:
    return {"id": "dec_L0_090", "kind": "decor", "type": "mirror", "level_id": "L0", "room_id": ROOM,
            "anchor_ids": ["w1"], "center": [x, 1.48], "wall_point": [x, 1.5], "rotation_deg": 0.0,
            "size": [0.54, 0.04], "asset": None, "bottom_m": 1.3, "max_height_m": 1.2}


def _world(item: dict, x: float, y: float = 0.0) -> tuple[float, float]:
    r = math.radians(float(item["rotation_deg"]))
    c = item["center"]
    return c[0] + x * math.cos(r) - y * math.sin(r), c[1] + x * math.sin(r) + y * math.cos(r)


# --------------------------------------------------------------------------
# The parts
# --------------------------------------------------------------------------

def test_the_niches_keep_clear_of_the_flush_plate_and_the_basins_mixer():
    nich = BT.install_niches(2.2, 0.45, [-0.5])
    clear, post = BT.INSTALL_NICHE["clear"], BT.INSTALL_NICHE["post"]
    assert len(nich) == 3
    for a, b in nich:
        assert b - a >= BT.INSTALL_NICHE["min_w"] - 1e-9 and b - a <= BT.INSTALL_NICHE["w"] + 1e-9
        assert -1.1 + post - 1e-9 <= a and b <= 1.1 - post + 1e-9
        for x in (0.45, -0.5):
            assert b <= x - clear + 1e-9 or a >= x + clear - 1e-9          # never behind the plate or the mixer
    narrow = BT.install_niches(0.8, 0.098)                                   # real04's bathrooms: one narrow niche
    assert len(narrow) == 1 and narrow[0][1] - narrow[0][0] >= BT.INSTALL_NICHE["min_w"] - 1e-9
    assert BT.install_niches(0.6, 0.0) == []                                 # a plain ledge with its cap


def test_the_installation_wall_builds_into_its_box_with_a_lit_styled_niche_each():
    w, d, h = 2.2, BT.INSTALL_WALL_D_M, BT.INSTALL_WALL_H_M
    item = {"wc_x": 0.45, "keep_x": [-0.5], "body_key": "dark", "cap_key": "wood"}
    parts = P.decor_parts("install_wall", w, d, h, item)
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    assert x1 - x0 <= w + 1e-9 and y1 - y0 <= d + 1e-9 and z1 - z0 <= h + 1e-9 and z0 == pytest.approx(0.0)
    assert all(T.volume(p) > -1e-9 for p in parts)
    leds = [p for p in parts if p["role"] == "led"]
    assert len(leds) == len(BT.install_niches(w, 0.45, [-0.5])) == 3
    assert {p["key"] for p in parts if p["role"] == "body"} == {"dark"}
    assert {p["key"] for p in parts if p["role"] == "ledge"} == {"wood"}                # its cap
    roles = {p["role"] for p in parts}
    assert roles - {"body", "ledge", "led"}                                  # the toiletries in the niches
    assert sum(len(p["verts"]) for p in parts) < 20000
    plain = P.decor_parts("install_wall", 0.6, d, h, {"wc_x": 0.0})
    assert {p["role"] for p in plain} == {"body", "ledge"}
    assert "install_wall" in BT.BATH_DECOR_TYPES and "install_wall" in P.LARGE_DECOR_TYPES


def test_the_wc_hangs_on_the_installation_walls_face_with_its_pan_and_plate():
    w, d = 0.5, 0.69
    parts = BT.wall_hung_wc_parts(w, d, 0.4, BT.INSTALL_WALL_D_M)
    ys = [y for p in parts for _x, y, _z in p["verts"]]
    assert max(ys) <= d / 2.0 - BT.INSTALL_WALL_D_M + 0.01 + 1e-9            # on the face, not in the pre-wall
    assert min(ys) >= -d / 2.0 - 1e-9                                        # inside the drawn footprint
    bowl = [y for p in parts if p["role"] == "bowl" for _x, y, _z in p["verts"]]
    assert max(bowl) - min(bowl) >= BT.WC_PAN_MIN_D_M - 0.05
    plate = [z for p in parts if p["role"] == "plate" for _x, _y, z in p["verts"]] or \
        [z for p in parts if p["key"] == "handle" and p["role"] != "hinge" for _x, _y, z in p["verts"]]
    assert max(plate) <= BT.INSTALL_WALL_H_M                                 # the flush plate under its top


def test_the_bench_vanity_stands_on_the_floor_with_a_vessel_and_a_wall_mixer():
    look = {"vanity": "bench", "basin": "vessel_wall", "top_key": "wood", "top_m": 0.85, "made_to_measure": True}
    w, d = 0.8, 0.55
    for off in (0.0, BT.INSTALL_WALL_D_M):
        parts = BT.vanity_parts(w, d, 0.85, dict(look, wall_offset_m=off))
        roles = {p["role"] for p in parts}
        assert {"top", "leg", "foot", "shelf", "basin", "spout", "rosette"} <= roles
        assert min(z for p in parts for _x, _y, z in p["verts"]) == pytest.approx(0.0, abs=1e-6)   # on the floor
        assert all(-w / 2.0 - 1e-6 <= x <= w / 2.0 + 1e-6 and -d / 2.0 - 1e-6 <= y <= d / 2.0 - off + 1e-6
                   for p in parts for x, y, _z in p["verts"])
        assert {p["key"] for p in parts if p["role"] == "top"} == {"wood"}
        assert {p["key"] for p in parts if p["role"] == "basin"} == {"dark"}           # the matt black vessel
        assert any(p["key"] == "rattan" for p in parts)                                 # the woven basket
        assert all(T.volume(p) > -1e-9 for p in parts)
        rosette = [y for p in parts if p["role"] == "rosette" for _x, y, _z in p["verts"]]
        assert max(rosette) == pytest.approx(d / 2.0 - off, abs=1e-6)                  # on the wall (its face)
    assert "an oak trestle bench" in BT.vanity_items(w, d, 0.85, look)
    assert BT.vanity_layout(w, d, 0.85, "bench", "vessel_wall")["bottom_m"] == 0.0


# --------------------------------------------------------------------------
# The plan (the layout stage) and the dressing (the decor stage)
# --------------------------------------------------------------------------

def test_a_wc_gets_the_installation_wall_behind_its_wc_and_basin_and_the_bench():
    b, st = wc_room("japandi")
    rec = b["bath_details"]["rooms"][ROOM]
    by = {f["id"]: f for f in b["furniture"]}
    assert len(rec["install_walls"]) == 1
    iw = rec["install_walls"][0]
    assert iw["anchors"] == ["t1", "w1"] and iw["width"] == pytest.approx(2.2) and iw["niches"] >= 2
    assert (iw["body_key"], iw["cap_key"]) == BT.FAMILY_BATH["japandi"]["install_wall"]
    assert rec["feature"] is None and "feature_panel" not in rec        # the pre-wall, not the fluted wall (B24)
    wc, basin = by["t1"]["bath_look"], by["w1"]["bath_look"]
    assert wc["wall_offset_m"] == BT.INSTALL_WALL_D_M and wc["install_wall"] and "UL205" in wc["reason"]
    assert basin["vanity"] == "bench" and basin["basin"] == "vessel_wall" and basin["install_wall"]
    assert by["t1"]["footprint"]["size"] == [0.5, 0.69] and by["w1"]["footprint"]["size"] == [0.8, 0.55]   # as drawn
    # the WC's flush plate is clear of every niche (its centre along the wall)
    wc_x = iw["wc_x"]
    item = {"center": iw["center"], "rotation_deg": iw["rotation_deg"]}
    assert _world(item, wc_x)[0] == pytest.approx(by["t1"]["footprint"]["center"][0], abs=1e-3)
    for a, bb in BT.install_niches(iw["width"], wc_x, iw["keep_x"]):
        assert bb <= wc_x - BT.FLUSH_PLATE_M[0] / 2.0 or a >= wc_x + BT.FLUSH_PLATE_M[0] / 2.0
    plan = MOD.plan_bath_made(by["w1"])
    assert plan["variant"] == "bench" and "oak trestle bench" in plan["products"][0]
    assert any("installation wall" in x for x in plan["products"])
    # the decor stage: the wall, the long backlit mirror over it, the holder and the brush off it
    b["decor"] = [mirror()]
    BD.dress(b, st, T.new_ids())
    items = {d["type"]: d for d in b["decor"]}
    wall = items["install_wall"]
    assert wall["size"] == [2.2, BT.INSTALL_WALL_D_M, BT.INSTALL_WALL_H_M] and wall["anchor_ids"] == ["t1", "w1"]
    assert wall["wc_x"] == pytest.approx(wc_x) and wall["source"] == "added_by_ai" and "UL205" in wall["reason"]
    m = items["mirror"]
    assert m["fixture"] == "backlit_mirror" and m["long"] and m["max_height_m"] == BT.LONG_MIRROR_H_M
    assert m["min_bottom_m"] == pytest.approx(BT.INSTALL_WALL_H_M + BT.LONG_MIRROR_GAP_M)
    assert m["size"][0] == pytest.approx(min(BT.LONG_MIRROR_MAX_W, 2.2 - 0.10))
    assert BF.mirror_box(m)[2] == pytest.approx(BT.LONG_MIRROR_H_M)
    box = BD._item_box(wall)
    for dtype in ("toilet_paper_holder", "toilet_brush"):
        assert dtype in items and not BD._item_box(items[dtype]).intersection(box).area > 1e-6, dtype
    found = {f["missing"] for f in BD.review(b)[0]}
    assert not found & {"toilet_paper_holder", "toilet_brush", "mirror", "mirror_kind", "vanity"}, found
    count = len(b["decor"])
    BD.dress(b, st, T.new_ids())                                                 # idempotent
    assert len(b["decor"]) == count


def test_the_families_choose_the_bench_and_the_finish_and_a_classic_wc_keeps_its_cistern():
    for fam in ("modern", "minimal", "industrial", "scandinavian", "organic modern"):
        b, _st = wc_room(fam)
        rec = b["bath_details"]["rooms"][ROOM]
        basin = next(f for f in b["furniture"] if f["id"] == "w1")["bath_look"]
        spec = BT.spec_of(fam)[0]
        assert rec["install_walls"] and (rec["install_walls"][0]["body_key"],
                                         rec["install_walls"][0]["cap_key"]) == tuple(spec["install_wall"]), fam
        assert basin["vanity"] == (spec["vanity_wc"] or spec["vanity"]), fam
    b, _st = wc_room("classic")
    rec = b["bath_details"]["rooms"][ROOM]
    assert rec["install_walls"] == [] and next(f for f in b["furniture"] if f["id"] == "t1")["bath_look"]["wc"] \
        == "close_coupled"
    b, _st = wc_room("rustic")                                                  # its oak bench, its own WC
    assert next(f for f in b["furniture"] if f["id"] == "w1")["bath_look"]["vanity"] == "bench"


def test_a_bathroom_gets_it_on_the_wc_side_only_and_keeps_its_feature_walls():
    b, st = T.full("modern")
    rec = b["bath_details"]["rooms"][ROOM]
    assert len(rec["install_walls"]) == 1 and rec["install_walls"][0]["anchors"] == ["t1"]
    assert rec["feature"] == "vanity_panel"                                     # B13 stays behind the vanity
    by = {f["id"]: f for f in b["furniture"]}
    assert "wall_offset_m" not in by["w1"]["bath_look"] and by["w1"]["bath_look"]["vanity"] == "fluted"
    iw = rec["install_walls"][0]
    # the WC on the east wall (its back at x = 3.0): the wall's frame puts wc_x on the WC's centre
    assert _world({"center": iw["center"], "rotation_deg": iw["rotation_deg"]}, iw["wc_x"])[1] == \
        pytest.approx(by["t1"]["footprint"]["center"][1], abs=1e-3)
    assert iw["center"][0] == pytest.approx(3.0 - BT.INSTALL_WALL_D_M / 2.0, abs=1e-3)
    BD.dress(b, st, T.new_ids())
    walls = [d for d in b["decor"] if d["type"] == "install_wall"]
    assert len(walls) == 1
    towels = [d for d in b["decor"] if d["type"] in ("towel_rail", "towel_shelf", "towel_bar")]
    assert towels and not any(BD._item_box(t).intersects(BD._item_box(walls[0])) for t in towels)
    b2, _st2 = T.full("japandi")                                               # B24: the fluted wall stays
    rec2 = b2["bath_details"]["rooms"][ROOM]
    assert rec2["install_walls"] == [] and rec2["feature"] == "wc_fluted"


def test_a_short_wc_or_one_without_room_beside_it_gets_none():
    b, _st = wc_room("modern", wc_d=0.58)
    rec = b["bath_details"]["rooms"][ROOM]
    assert rec["install_walls"] == [] and "deep" in rec["install_why"]
    assert "wall_offset_m" not in next(f for f in b["furniture"] if f["id"] == "t1")["bath_look"]
    # a WC squeezed between two pieces on its wall: no stretch beside it
    t = M.fp("t1", "toilet", (1.55, 1.5 - 0.345), (0.5, 0.69), rotation=0.0)
    c1 = M.fp("c1", "tall_cabinet", (1.1, 1.5 - 0.175), (0.4, 0.35), rotation=0.0, height=1.8)
    c2 = M.fp("c2", "tall_cabinet", (2.0, 1.5 - 0.175), (0.4, 0.35), rotation=0.0, height=1.8)
    b = M.building(w=2.2, h=1.5, room_type="wc", window=None, furniture=[t, c1, c2], door_x=0.6)
    BD.plan_building(b, T.style_of("modern"))
    rec = b["bath_details"]["rooms"][ROOM]
    assert rec["install_walls"] == [] and "no free wall stretch" in rec["install_why"]


@pytest.mark.skipif(not REAL04.exists(), reason="real04's run 20261030-112241-full is not in the main repository")
def test_real04_bathrooms_get_their_installation_walls_on_the_wc_side():
    b = json.loads(REAL04.read_text(encoding="utf-8"))
    BD.plan_building(b, {"family": "modern"})
    rooms = b["bath_details"]["rooms"]
    walls = [iw for rec in rooms.values() for iw in rec.get("install_walls") or []]
    assert len(walls) >= 8
    by = {f["id"]: f for f in b["furniture"]}
    for iw in walls:
        assert len(iw["anchors"]) == 1 and by[iw["anchors"][0]]["type"] == "toilet"   # bathrooms: the WC side only
        assert iw["width"] >= 0.5 + BT.INSTALL_MIN_EXTRA_M - 1e-9
        assert by[iw["anchors"][0]]["bath_look"]["wall_offset_m"] == BT.INSTALL_WALL_D_M
    assert all(rec["feature"] == "vanity_panel" for rec in rooms.values())       # B13 kept everywhere
