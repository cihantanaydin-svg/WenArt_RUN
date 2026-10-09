"""A stair drawn on the top level of a whole building (docs/milestone10.md §3.2 items 1 and 2; pods F1b, F2).

A plan cut above a stair shows its flights from above: real02's attic plan (ÇATI KAT PLANI) inserts the same
``merdiven`` block at the same place as the ground floor ("stairs aligned"), and synthetic-07's MERDIVEN sits at
the same place on every plan. With no level above, the build read it as a new flight rising ceiling + slab and
capped a shaft above the ceiling: real02's attic stairs reached z 7.05 m over a 6.79 m ridge, synthetic-07's
7.27 m over 7.11 m. Now (``shell.top_level_stair``):

- a top-level stair over a stair of the level below is that stair's drawn upper end (``shell.stair_arrival``):
  not built again (``not_built`` with ``arrives_from`` and ``slab_opening``), no ceiling opening, no shaft; the
  floor keeps the slab's opening;
- any other top-level stair stops under the roof underside (assumed, a warning), no opening, no shaft; with no
  headroom it is not built (a warning);
- pre-M10 buildings (no slabs, roof or variants: real01, synthetic-01..06) keep the M7 rise.

The CPU tests are pure; the Blender test builds a small two-level house under a gable roof."""
import copy
import json
from pathlib import Path

import jsonschema
import pytest

from wenart import geometry as G
from wenart.blender import build as B
from wenart.blender import cli, geom2d, lighting, schemas, shell
from wenart.blender import parametric as P
from wenart.blender import roof as R

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = json.loads((ROOT / "docs" / "examples" / "building_m10.example.json").read_text(encoding="utf-8"))
SYNTHETIC07 = ROOT / "projects" / "synthetic-07" / "truth" / "building.json"
REAL02 = ROOT / "results" / "furniture" / "real02" / "building_final.json"
ALT = "l-1b-acik-mutfak"
NOT_BUILT_ITEM = schemas.SCENE_MANIFEST["properties"]["furniture"]["properties"]["not_built"]["items"]
BLENDER = cli.find_blender()
needs_blender = pytest.mark.skipif(BLENDER is None, reason="no Blender binary (WENART_BLENDER, "
                                                           "/workspace/tools/blender, /opt/wenart/blender, PATH)")


def _level(building: dict, level_id: str) -> dict:
    return next(lv for lv in building["levels"] if lv["id"] == level_id)


def _with_attic_stair(dx: float = 0.0) -> dict:
    """The M10 example with its ground-floor stair f_L0_001 drawn again on the attic plan (L1, the hall) as
    f_L1_001, shifted ``dx`` metres along x (0: right over it, as real02 and synthetic-07 draw it)."""
    b = copy.deepcopy(EXAMPLE)
    top = copy.deepcopy(next(f for f in b["furniture"] if f["id"] == "f_L0_001"))
    top.update(id="f_L1_001", level_id="L1", room_id="r_L1_hol")
    top["evidence"] = [dict(e, entity="INSERT:f_L1_001", region_id="r5") for e in top["evidence"]]
    top["footprint"]["center"][0] += dx
    for f in top["stair"]["flights"]:
        f["start"][0] += dx
        f["end"][0] += dx
    b["furniture"].append(top)
    return b


def _corners(piece: dict) -> list:
    fp = piece["footprint"]
    return G.rotated_rectangle(fp["center"], fp["size"], float(fp["rotation_deg"]))


# --------------------------------------------------------------------------
# Case A: the drawn upper end of the stair below
# --------------------------------------------------------------------------

def test_a_top_level_stair_over_the_stair_below_is_its_upper_end():
    vb = B.prepare(_with_attic_stair(), "base")["building"]
    attic = _level(vb, "L1")
    [item] = shell.plan_stairs(vb, attic)
    # was: a 2.55 m flight (ceiling 2.40 + the assumed 0.15 m slab) with a ceiling opening and a shaft to 5.90 m
    assert item["plan"] is None
    assert item["arrival"] == {"from": "f_L0_001", "from_level": "L0", "share": 1.0, "opening": "sv_L1_001",
                               "slabs": True}
    assert item["reason"].startswith("arrives from f_L0_001 (L0 -> L1): the drawn upper end") and not item["warnings"]
    assert lighting.stair_openings(vb, attic) == []          # no ceiling opening left for the attic lights
    # The stair below is planned as without the attic piece: floor to floor through the opening of sl_L1.
    plain = B.prepare(copy.deepcopy(EXAMPLE), "base")["building"]
    assert shell.plan_stairs(vb, _level(vb, "L0"), slab_void=True) == \
        shell.plan_stairs(plain, _level(plain, "L0"), slab_void=True)
    slabs = shell.slab_plan(vb, vb["levels"])
    assert [(s["id"], s["stairs"], len(s["voids"])) for s in slabs["slabs"]][-1] == ("sl_L1", ["f_L0_001"], 1)
    assert not slabs["warnings"]


def test_the_upper_end_is_listed_not_built_with_where_it_arrives_from():
    vb = B.prepare(_with_attic_stair(), "base")["building"]
    attic = _level(vb, "L1")
    [item] = shell.plan_stairs(vb, attic)
    record, notes = shell.stair_not_built(item, attic)
    assert record == {"id": "f_L1_001", "type": "stair", "reason": item["reason"], "arrives_from": "f_L0_001",
                      "slab_opening": "sv_L1_001"}
    jsonschema.validate(record, NOT_BUILT_ITEM)
    [note] = notes
    jsonschema.validate(note, schemas.ASSUMED_ENTRY)
    assert (note["object"], note["parent"], note["kind"], note["field"], note["value"]) == \
        ("f_L1_001", "f_L1_001", "stair_arrival", "stair", "arrives from f_L0_001")
    assert "no level above L1" in note["reason"] and "100%" in note["reason"] and "sv_L1_001" in note["reason"]
    # a build: false stair keeps the Milestone 7 record and adds nothing
    off = {"piece": dict(item["piece"], build=False), "plan": None, "reason": shell.STAIR_NOT_BUILT_REASON}
    assert shell.stair_not_built(off, attic) == ({"id": "f_L1_001", "type": "stair",
                                                  "reason": shell.STAIR_NOT_BUILT_REASON}, [])


def test_real02_attic_stairs_are_the_upper_ends_of_the_ground_floor_twins():
    building = json.loads(REAL02.read_text(encoding="utf-8"))
    for variant in ("base", ALT):
        prep = B.prepare(copy.deepcopy(building), variant)
        vb = prep["building"]
        attic = _level(vb, "L1")
        items = {i["piece"]["id"]: i for i in shell.plan_stairs(vb, attic)}
        assert set(items) == {"f_L1_001", "f_L1_002"} and all(i["plan"] is None for i in items.values())
        assert {k: (i["arrival"]["from"], i["arrival"]["opening"], i["arrival"]["share"]) for k, i in items.items()} \
            == {"f_L1_001": ("f_L0_002", "sv_L1_002", 1.0), "f_L1_002": ("f_L0_001", "sv_L1_001", 1.0)}
        assert lighting.stair_openings(vb, attic) == []
        # the ground floor stairs still run floor to floor (3.15 m) through the openings of sl_L1, no warning
        ground = _level(vb, "L0")
        above = prep["slabs"]["by_level"]["L0"]["above"]
        assert above["id"] == "sl_L1" and len(above["voids"]) == 2
        for low in shell.plan_stairs(vb, ground, slab_void=True):
            assert low["plan"]["rise_m"] == pytest.approx(3.15)
            assert not shell.stair_arrivals(low["plan"], above["voids"])


def test_synthetic07_attic_stair_without_slabs_is_the_upper_end_with_a_warning():
    # The truth has variants (a whole building) but no slabs and no roof (the assumed flat roof).
    building = json.loads(SYNTHETIC07.read_text(encoding="utf-8"))
    assert not building.get("slabs") and building.get("roof") is None and building.get("variants")
    for variant in ("base", ALT):
        vb = B.prepare(copy.deepcopy(building), variant)["building"]
        attic = _level(vb, "L1")
        [item] = shell.plan_stairs(vb, attic)
        assert item["plan"] is None
        assert item["arrival"] == {"from": "f_L0_005", "from_level": "L0", "share": 1.0, "opening": None,
                                   "slabs": False}
        assert item["warnings"] == [("arrives from f_L0_005, but the building has no slabs: the floor of L1 is not "
                                     "cut over it")]
        record, notes = shell.stair_not_built(item, attic)
        assert record["arrives_from"] == "f_L0_005" and record["slab_opening"] is None
        assert "the building has no slabs" in notes[0]["reason"]
        # the ground floor stair keeps its floor-to-floor flight capped under the attic floor
        [low] = shell.plan_stairs(vb, _level(vb, "L0"))
        assert low["plan"]["rise_m"] == pytest.approx(3.0) and low["plan"]["cap_z"] < 3.0


def test_the_largest_shared_footprint_wins():
    """Twin stairs side by side below; an attic stair over 60 % of one and 40 % of the other is the upper end of
    the first; under the arrival share it is no upper end."""
    def stair(pid, level_id, x):
        return {"id": pid, "level_id": level_id, "type": "stair",
                "footprint": {"center": [x, 2.0], "size": [1.0, 3.0], "rotation_deg": 0.0}}

    levels = [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.6},
              {"id": "L1", "elevation": 2.9, "ceiling_height": 2.4}]
    building = {"levels": levels, "walls": [], "rooms": [], "openings": [], "slabs": [
        {"id": "sl_L1", "above_level_id": "L1", "openings": [
            {"id": "sv_a", "furniture_id": "f_a", "polygon": [[0.5, 0.5], [1.5, 0.5], [1.5, 3.5], [0.5, 3.5]]},
            {"id": "sv_drawn", "polygon": [[1.5, 0.5], [2.5, 0.5], [2.5, 3.5], [1.5, 3.5]]}]}],
        "furniture": [stair("f_a", "L0", 1.0), stair("f_b", "L0", 2.0)]}
    top = stair("f_top", "L1", 1.4)
    assert shell.stair_arrival(building, levels[1], top) == {"from": "f_a", "from_level": "L0", "share": 0.6,
                                                             "opening": "sv_a", "slabs": True}
    # over f_b mostly: its opening is the one drawn over it (no furniture_id)
    assert shell.stair_arrival(building, levels[1], stair("f_top", "L1", 1.8))["opening"] == "sv_drawn"
    assert shell.stair_arrival(building, levels[1], stair("f_top", "L1", 3.6)) is None      # 40 % of f_b
    assert shell.stair_arrival(building, levels[0], stair("f_x", "L0", 1.0)) is None        # a level above


# --------------------------------------------------------------------------
# Case B: a top-level stair over no stair stops under the roof
# --------------------------------------------------------------------------

def test_a_top_level_stair_over_no_stair_stops_under_the_roof():
    vb = B.prepare(_with_attic_stair(dx=-2.475), "base")["building"]        # x 6.5-7.5: off the stair below
    attic = _level(vb, "L1")
    floor_z = float(attic["elevation"])
    [item] = shell.plan_stairs(vb, attic)
    plan = item["plan"]
    assert item["arrival"] is None and plan is not None
    under = min(geom2d.surface_z(attic["ceiling_planes"], x, y) for x, y in _corners(item["piece"]))
    top = under - floor_z - shell.STAIR_UPPER_FLOOR_GAP
    assert plan["rise_m"] == plan["ceiling_z"] == plan["cap_z"] == pytest.approx(top)
    assert top < float(attic["ceiling_height"])                            # the roof underside is the lower one
    # no ceiling opening, no shaft through the roof; every part under the roof underside over the footprint
    assert plan["void"] == [] and P.void_shaft(plan) == ([], [])
    verts = shell.stair_mesh(plan, floor_z)[0]
    assert max(v[2] for v in verts) <= under
    assert lighting.stair_openings(vb, attic) == []
    tops = [a for a in plan["assumed"] if a["kind"] == "stair_top"]
    assert tops == [{"field": "rise_m", "kind": "stair_top", "value": round(top, 4), "reason": tops[0]["reason"]}]
    assert "no roof opening is drawn, none is cut" in tops[0]["reason"]
    assert any("roof access is not drawn" in w for w in plan["warnings"])
    assert not any("shaft cap" in n for n in plan["notes"])


def test_a_top_level_stair_without_headroom_is_not_built():
    vb = B.prepare(_with_attic_stair(dx=-2.475), "base")["building"]
    for low in (0.20, 0.0, -0.3):                                           # the roof underside at the eaves
        attic = dict(_level(vb, "L1"), ceiling_planes=[[0.0, 0.0, 3.0 + low]])
        [item] = shell.plan_stairs(vb, attic)                              # was: a ZeroDivisionError at 0 m
        assert item["plan"] is None and "no headroom" in item["reason"]
        assert any("no room for a flight" in w for w in item["warnings"])
        assert shell.stair_not_built(item, attic)[1] == []
    # without the roof planes (a roof that is not convex): under the level's ceiling
    attic = {k: v for k, v in _level(vb, "L1").items() if k != "ceiling_planes"}
    [item] = shell.plan_stairs(vb, attic)
    assert item["plan"]["rise_m"] == pytest.approx(2.4 - shell.STAIR_UPPER_FLOOR_GAP) and item["plan"]["void"] == []


def test_a_top_level_stair_in_a_roof_terrace_is_a_warning():
    # x 6.5-7.5, y 1.5-4.5: into the example's roof terrace opening over r_L1_teras (y 0.25-4.075)
    b = _with_attic_stair(dx=-2.475)
    top = b["furniture"][-1]
    top["footprint"]["center"][1] -= 3.0
    for f in top["stair"]["flights"]:
        f["start"][1] -= 3.0
        f["end"][1] -= 3.0
    vb = B.prepare(b, "base")["building"]
    [item] = shell.plan_stairs(vb, _level(vb, "L1"))
    assert any("roof opening" in w and "may lead out onto the roof" in w for w in item["plan"]["warnings"])


# --------------------------------------------------------------------------
# Pre-M10 buildings keep the Milestone 7 stair
# --------------------------------------------------------------------------

def test_pre_m10_top_stair_keeps_the_m7_rise():
    from test_blender_geometry import HALL, HALL_WALLS, LEVEL0, real01_stair_piece

    upper = {"id": "L1", "label": "First floor", "elevation": 3.0, "ceiling_height": 2.7,
             "ceiling_height_source": "section"}
    walls = HALL_WALLS + [dict(w, id=w["id"].replace("L0", "L1"), level_id="L1") for w in HALL_WALLS]
    stacked = dict(real01_stair_piece(), id="f_L1_019", level_id="L1", room_id="r_L1_hall")
    building = {"levels": [LEVEL0, upper], "walls": walls, "rooms": [HALL], "openings": [],
                "furniture": [real01_stair_piece(), stacked]}
    assert not shell.whole_building(building) and shell.stair_arrival(building, upper, stacked) is None
    [item] = shell.plan_stairs(building, upper)
    expected = P.stair_plan(stacked, 2.7 + P.STAIR_SLAB_M, 2.7, 2.7 + P.STAIR_SHAFT_CAP_M, walls[4:],
                            "derived from the documented ceiling and assumed slab")
    assert item["plan"] == expected and item["plan"]["void"] and "arrival" not in item
    # the single-level real01 stair: the Milestone 7 plan (rise ceiling + slab, its capped opening)
    single = {"levels": [LEVEL0], "walls": HALL_WALLS, "rooms": [HALL], "openings": [],
              "furniture": [real01_stair_piece()]}
    [item] = shell.plan_stairs(single, LEVEL0)
    assert item["plan"] == P.stair_plan(real01_stair_piece(), 2.85, 2.7, 3.2, HALL_WALLS, P.STAIR_RISER_SOURCE)
    assert P.void_shaft(item["plan"])[1]


# --------------------------------------------------------------------------
# Blender: a two-level house under a gable roof
# --------------------------------------------------------------------------

def _gable_house() -> dict:
    """A 6 x 4 m house: the ground floor (L0, 2.70 m) with a straight stair along +y at x 1.0 (16 risers), the
    attic (L1 at 3.00 m, 2.40 m) under a 35-degree gable roof (ridge along x at y 2.0, eaves at z 3.90 on the
    outline 0.5 m outside the walls). The attic plan draws the stair again over the one below (f_L1_001) and a
    second stair at x 4.5 over no stair (f_L1_002: the roof access, not drawn). The slab under the attic has the
    stair opening sv_L1_001 of f_L0_001."""
    ev = [{"file": "x.dxf", "method": "vector", "confidence": 1.0}]

    def walls(level_id):
        def wall(wid, start, end):
            return {"id": f"w_{level_id}_{wid}", "level_id": level_id, "start": start, "end": end, "thickness": 0.2,
                    "exterior": True, "status": "verified", "evidence": ev}

        return [wall("s", [-0.2, -0.1], [6.2, -0.1]), wall("n", [-0.2, 4.1], [6.2, 4.1]),
                wall("w", [-0.1, -0.2], [-0.1, 4.2]), wall("e", [6.1, -0.2], [6.1, 4.2])]

    def room(level_id, rid, room_type):
        return {"id": rid, "level_id": level_id, "label": "Hall", "room_type": room_type,
                "polygon": [[0.0, 0.0], [6.0, 0.0], [6.0, 4.0], [0.0, 4.0]], "area_computed": 24.0,
                "status": "verified", "evidence": ev}

    def stair(pid, level_id, room_id, x, length, lines):
        y0 = 2.0 - length / 2.0
        return {"id": pid, "level_id": level_id, "room_id": room_id, "type": "stair", "source": "from_documents",
                "status": "verified", "front_deg": None, "height": None, "asset": None, "evidence": ev,
                "footprint": {"center": [x, 2.0], "size": [1.0, length], "rotation_deg": 0.0},
                "stair": {"flights": [{"start": [x, y0], "end": [x, y0 + length], "width": 1.0, "lines": lines}],
                          "landing": None, "direction": [0.0, 1.0], "direction_assumed": False,
                          "turn": "straight", "turn_assumed": False, "void_assumed": True}}

    outline = [[-0.2, -0.2], [6.2, -0.2], [6.2, 4.2], [-0.2, 4.2]]
    return {"schema_version": "0.1", "status": "ok", "project": {"id": "gable", "brief": {}}, "documents": [],
            "levels": [{"id": "L0", "label": "L0", "order": 0, "elevation": 0.0, "ceiling_height": 2.7,
                        "ceiling_height_source": "section", "evidence": ev},
                       {"id": "L1", "label": "L1", "order": 1, "elevation": 3.0, "ceiling_height": 2.4,
                        "ceiling_height_source": "section", "evidence": ev}],
            "walls": walls("L0") + walls("L1"), "openings": [],
            "rooms": [room("L0", "r_L0_hall", "hall"), room("L1", "r_L1_attic", "hall")],
            "furniture": [stair("f_L0_001", "L0", "r_L0_hall", 1.0, 3.0, 16),
                          stair("f_L1_001", "L1", "r_L1_attic", 1.0, 3.0, 16),
                          stair("f_L1_002", "L1", "r_L1_attic", 4.5, 2.0, 8)],
            "decor": [], "conflicts": [], "unverified": [], "warnings": [],
            "slabs": [{"id": "sl_L0", "above_level_id": "L0", "below_level_id": None, "z_top": 0.0, "thickness": 0.2,
                       "outline": outline, "openings": [], "status": "verified", "evidence": ev},
                      {"id": "sl_L1", "above_level_id": "L1", "below_level_id": "L0", "z_top": 3.0, "thickness": 0.2,
                       "outline": outline, "status": "verified", "evidence": ev,
                       "openings": [{"id": "sv_L1_001", "kind": "stair_void", "furniture_id": "f_L0_001",
                                     "polygon": [[0.45, 0.45], [1.55, 0.45], [1.55, 3.55], [0.45, 3.55]]}]}],
            "roof": {"type": "gable", "type_source": "section", "over_level_id": "L1",
                     "outline": [[-0.5, -0.5], [6.5, -0.5], [6.5, 4.5], [-0.5, 4.5]],
                     "ridge_lines": [[[-0.5, 2.0], [6.5, 2.0]]], "eaves_height": {"value": 3.9, "method": "vector"},
                     "pitches_deg": [{"value": 35.0, "method": "vector"}], "planes": [], "evidence": []}}


def test_the_gable_house_plans():
    """The pure plans the Blender test builds (also guards the house itself)."""
    b = _gable_house()
    prep = B.prepare(copy.deepcopy(b), "base")
    vb = prep["building"]
    attic = _level(vb, "L1")
    items = {i["piece"]["id"]: i for i in shell.plan_stairs(vb, attic)}
    assert items["f_L1_001"]["plan"] is None and items["f_L1_001"]["arrival"]["opening"] == "sv_L1_001"
    plan = items["f_L1_002"]["plan"]
    under = min(geom2d.surface_z(attic["ceiling_planes"], x, y) for x, y in _corners(items["f_L1_002"]["piece"]))
    assert plan["rise_m"] == pytest.approx(under - 3.0 - shell.STAIR_UPPER_FLOOR_GAP) and plan["void"] == []
    assert 1.0 < plan["rise_m"] < 2.0
    [low] = shell.plan_stairs(vb, _level(vb, "L0"), slab_void=True)
    assert low["plan"]["rise_m"] == pytest.approx(3.0) and not low["plan"]["warnings"]
    roof = prep["roof"]
    assert roof["ridge_z"] == pytest.approx(3.9 + 2.5 * 0.70021, abs=1e-3)


@pytest.fixture(scope="module")
def gable_build(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("gable")
    path = tmp / "gable.json"
    path.write_text(json.dumps(_gable_house()), encoding="utf-8")
    manifest = cli.build(path, tmp / "scene", no_textures=True, preview_samples=1)
    return json.loads(manifest.read_text(encoding="utf-8"))


@needs_blender
def test_no_stair_or_shaft_rises_out_of_the_roof(gable_build):
    m = gable_build
    schemas.validate_scene_manifest(m)
    objects = {o["name"]: o for o in m["objects"]}
    # the attic stair over the ground floor stair is not built again; the roof access stops under the roof
    assert "furn_f_L1_001" not in objects and "f_L1_001_void" not in objects and "f_L1_002_void" not in objects
    assert {"furn_f_L0_001", "furn_f_L1_002"} <= set(objects) and "f_L0_001_void" not in objects
    assert m["furniture"]["stairs"] == ["f_L0_001", "f_L1_002"]
    [nb] = [n for n in m["furniture"]["not_built"] if n["id"] == "f_L1_001"]
    assert (nb["arrives_from"], nb["slab_opening"]) == ("f_L0_001", "sv_L1_001")
    assert objects["furn_f_L0_001"]["stair"]["upper_end"] == "f_L1_001"
    assert objects["furn_f_L0_001"]["stair"]["arrives"].startswith("through the opening of the slab above")
    # every stair part under the roof underside over its footprint (and under the ridge)
    b = _gable_house()
    model = R.roof_model(b["roof"], b)
    planes = R.ceiling_planes(model, b["levels"][1])
    piece = next(f for f in b["furniture"] if f["id"] == "f_L1_002")
    under = min(geom2d.surface_z(planes, x, y) for x, y in _corners(piece))
    box = objects["furn_f_L1_002"]["box3d"]
    assert box["center"][2] + box["size"][2] / 2.0 <= under + 1e-3
    for o in m["objects"]:
        if o.get("type") == "stair" or o["name"].endswith("_void"):
            assert o["box3d"]["center"][2] + o["box3d"]["size"][2] / 2.0 <= model["ridge_z"], o["name"]
    # the slab keeps the opening and the attic floor keeps it; the attic ceiling is not cut
    [slab] = [o for o in m["objects"] if o["name"] == "sl_L1"]
    assert slab["openings"] == 1 and slab["stairs"] == ["f_L0_001"]
    assert objects["r_L1_attic_floor"]["stair_void"].startswith("1 opening(s) of the slab under the level")
    assert "stair_void" not in objects["r_L1_attic_ceiling"]
    # what was assumed and warned
    kinds = {(a["object"], a.get("kind")) for a in m["assumed"]}
    assert {("f_L1_001", "stair_arrival"), ("furn_f_L1_002", "stair_top")} <= kinds
    assert any(w.startswith("f_L1_002: stair on the top level") and "roof access is not drawn" in w
               for w in m["warnings"])
    assert not [w for w in m["warnings"] if w.startswith("f_L1_001:")]


def test_the_camera_model_leaves_out_a_stair_the_builder_does_not_build():
    """The ray model of camsearch follows the builder: the attic's upper end of the stair below is neither a
    solid nor a box (before: a box over the stairwell); the ground-floor stair stays its built parts."""
    from wenart.blender import camsearch
    vb = B.prepare(_with_attic_stair(), "base")["building"]
    hall = next(r for r in vb["rooms"] if r["id"] == "r_L1_hol")
    model = camsearch.RoomModel(hall, vb, _level(vb, "L1"))
    codes = {camsearch.FIRST_ELEMENT + len(model.elements) - len(model.pieces) + k: f["id"]
             for k, f in enumerate(model.pieces)}
    modelled = {codes.get(b[0]) for b in model.boxes} | {codes.get(s[0]) for s in model.solids}
    assert "f_L1_001" in {f["id"] for f in model.pieces} and "f_L1_001" not in modelled
    ground = next(r for r in vb["rooms"] if r["id"] == next(f for f in vb["furniture"] if f["id"] == "f_L0_001")["room_id"])
    model0 = camsearch.RoomModel(ground, vb, _level(vb, "L0"))
    codes0 = {camsearch.FIRST_ELEMENT + len(model0.elements) - len(model0.pieces) + k: f["id"]
              for k, f in enumerate(model0.pieces)}
    assert "f_L0_001" in {codes0.get(s[0]) for s in model0.solids}
