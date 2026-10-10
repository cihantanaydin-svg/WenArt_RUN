"""CPU tests of the build side of the levels (docs/milestone12.md §3.4; Blender is not needed: the geometry is in
pure functions): entrances from site.entrances (landing, flights, intermediate landings, ramp, handrails, cheek
walls), the raised plinth, the flat_cut roof and its parapet, the exterior views of a single drawn ground floor, room
floors at their offsets, door frames from the threshold, inner steps, the exterior check X3 on site.entrances and the
report's ground levels (B9)."""
import copy

import pytest

from wenart import geometry as G
from wenart.blender import build as BB
from wenart.blender import exterior as E
from wenart.blender import facade as FA
from wenart.blender import roof as R
from wenart.blender import shell as SH
from wenart.blender import site as S
from wenart.levels import model as M
from tests import _levels_fixture as F


def _whole(**brief):
    b = F.building()
    if brief:
        b["project"]["brief"] = {"levels": brief}
    return M.infer_levels(b)


def test_prepare_builds_a_single_ground_floor_whole_with_its_site_and_steps():
    b = _whole()
    prep = BB.prepare(b, "base", None)
    assert prep["whole"] and prep["site"] is not None and prep["roof"]["kind"] == "flat_cut"
    inf = prep["site"]["inferred"]
    assert [e["opening_id"] for e in inf["entrances"]] == ["d_front"]
    st = inf["steps"][0]
    assert st["risers"] == 1 and st["count"] == 0 and st["solution"] == "steps"
    assert st["blocks"][0]["z_top"] == 0.0                                         # the landing at the threshold
    assert prep["site"]["terrain"]["z"]["-y"] == -0.15                            # D3a


def test_record_steps_flights_landings_ramp_handrails_and_cheek_walls():
    b = _whole(ground_rise=2.0, door_into_air=3.0, accessible_entrance=True)
    rec = b["site"]["entrances"][0]
    assert rec["steps"]["count"] == 14 and rec["steps"]["flights"] == [12, 2] and rec["solution"] == "steps_and_ramp"
    e = S.record_entrances(b, M.base_levels(b))[0]
    st = S.entrance_steps(e)
    tops = [round(blk["z_top"], 4) for blk in st["blocks"]]
    r = rec["steps"]["riser"]
    assert tops[0] == 0.0 and len(tops) == 14                                      # landing + 13 blocks
    assert tops[-1] == pytest.approx(-2.0 + r, abs=1e-6)                          # the last tread one riser up
    assert st["intermediate_landings"] == 1
    depth = [G.distance(blk["polygon"][0], blk["polygon"][3]) for blk in st["blocks"]]
    assert depth[12] == pytest.approx(1.2) and depth[1] == pytest.approx(rec["steps"]["tread"])
    assert st["end"] == pytest.approx(1.2 + rec["steps"]["run"])
    assert len(st["rails"]) == 2 * 2 + 2 and st["cheeks"] and st["ramp"]["length"] == rec["ramp"]["length"]
    meshes = {m["kind"]: m for m in S.entrance_meshes(st, S.terrain_model(b, BB.prepare(b)["ground_outline"]))}
    assert set(meshes) == {"site_steps", "site_ramp", "site_handrail"}
    ramp = meshes["site_ramp"]
    assert max(v[2] for v in ramp["verts"]) == pytest.approx(0.0) and len(ramp["faces"]) == 6
    v, f = S.bar((0, 0, 0), (0, 0, 1), 0.05, 0.05)                                 # a vertical post: a box
    assert len(v) == 8 and max(p[2] for p in v) - min(p[2] for p in v) == pytest.approx(1.05)


def test_old_buildings_keep_the_m11_steps():
    b = _whole()
    b["site"].pop("entrances")
    assert S.record_entrances(b, M.base_levels(b)) is None
    ents = S.entrances(b, M.base_levels(b), S.terrain_model(b, BB.prepare(b)["ground_outline"]),
                       BB.prepare(b)["ground_outline"])
    assert ents and "record" not in ents[0] and S.entrance_steps(ents[0])["count"] == 0     # 0.15 m: one 0.15 riser


def test_the_plinth_is_a_raised_base_from_the_ground_to_the_floor():
    b = _whole(ground_rise=0.45)
    prep = BB.prepare(b)
    plan = FA.articulation_plan(b, b["levels"], prep["outlines"], prep["ground_outline"], prep["site"]["terrain"],
                                prep["roof"], {}, {}, prep["site"]["wells"])
    plinth = [x for x in plan["boxes"] if x["kind"] == "plinth"]
    assert plinth
    for x in plinth:
        z0, z1 = x["center"][2] - x["size"][2] / 2.0, x["center"][2] + x["size"][2] / 2.0
        assert z0 == pytest.approx(-0.5) and z1 == pytest.approx(0.0)              # ground - 0.05 .. the floor
        assert x["size"][1] == pytest.approx(FA.DIMENSIONS["proud"] + FA.PLINTH_BASE_DEPTH)
    # the front door does not cut the base (its bottom is at the floor), M11's 0.45 m band would have been cut
    assert FA.plinth_top({"top_z": 0.0, "min": 0.15, "floors": [-3.0, 0.0]}, -3.0) == -2.85
    assert FA.plinth_top({"top_z": 0.0, "min": 0.15, "floors": [-3.0, 0.0]}, -0.45) == 0.0
    old = copy.deepcopy(b)
    old["site"].pop("plinth")
    assert FA.plinth_rule(old) is None


def test_flat_cut_roof_has_a_parapet_and_no_aerial_view():
    b = _whole()
    prep = BB.prepare(b)
    roof = prep["roof"]
    assert roof["kind"] == "flat_cut" and roof["parapet"] == pytest.approx(0.30)
    ring = R.parapet_ring(roof)
    assert len(ring) == 4
    top = max(v[2] for verts, _ in ring for v in verts)
    assert top == pytest.approx(roof["eaves_z"] + 0.30)
    verts, faces, slots = R.roof_solid(roof)
    assert max(v[2] for v in verts) == pytest.approx(top)
    model = E.build_model(prep["building"], prep["building"]["levels"], roof, prep["site"])
    plans, dropped = E.plan_exterior(model, prep["building"], prep["building"]["levels"],
                                     prep["site"]["plot"] or [], variant="base")
    assert any(d["name"] == "ext_5" and "flat_cut" in d["dropped_reason"] for d in dropped)
    assert not any(p["view"] == "aerial" for p in plans)
    ent = [p for p in plans + dropped if p.get("view") == "entrance"]
    assert ent and ent[0]["entrance"] == "d_front"
    for p in plans:
        if p["view"] in ("corner", "frontal", "entrance"):
            assert p["position"][2] == pytest.approx(-0.15 + E.EYE_HEIGHT)          # eye level over the ground


def test_room_floors_thresholds_wall_bases_and_inner_steps():
    b = F.building()
    b["level_marks"] = [F.mark("lm_001", -0.30, kind="floor", point=(3.0, 4.0), room_id="r_living")]
    b = M.infer_levels(b)
    level = b["levels"][0]
    living = next(r for r in b["rooms"] if r["id"] == "r_living")
    assert SH.room_floor_z(living, level) == -0.3
    inner = next(o for o in b["openings"] if o["id"] == "d_inner")
    bottom, top, _ = SH.opening_vertical(inner, level, False)
    assert bottom == 0.0 and inner["threshold_z"] == 0.0
    shifted = dict(inner, threshold_z=0.15)
    assert SH.opening_vertical(shifted, level, False)[0] == 0.15                  # the frame starts at the threshold
    walls = {w["id"]: w for w in b["walls"]}
    assert SH.wall_base_drop(walls["w_5"], b["rooms"]) == -0.3                     # beside the sunken living room
    assert SH.wall_base_drop(walls["w_2"], b["rooms"]) == 0.0                      # the hall's east wall
    step = SH.inner_step(inner, walls["w_5"], b["rooms"], level)
    assert step["rise"] == 0.3 and step["low_room"] == "r_living" and step["z0"] == -0.3 and step["z1"] == 0.0
    from wenart.blender import cameras as CAM
    plans = CAM.plan_cameras(b, "L0")
    living_cams = [p for p in plans if p.get("room_id") == "r_living"]
    hall_cams = [p for p in plans if p.get("room_id") == "r_hall"]
    assert living_cams and hall_cams
    assert living_cams[0]["position"][2] == pytest.approx(hall_cams[0]["position"][2] - 0.3)


def test_unknown_and_unfitted_pieces_are_not_built():
    """Lead note of 10 Oct 2026: a piece of type unknown or with asset.method none is treated like build: false
    (cameras, the camera search's obstacles, the unverified list)."""
    from wenart.blender import camsearch as CS
    base = {"id": "f1", "room_id": "r_living", "type": "sofa", "footprint": {"center": [3, 4], "size": [2, 1],
                                                                             "rotation_deg": 0}, "status": "unverified"}
    assert SH.piece_built(base)
    assert not SH.piece_built(dict(base, type="unknown"))
    assert not SH.piece_built(dict(base, asset={"method": "none"}))
    assert not SH.piece_built(dict(base, build=False))
    assert SH.piece_built(dict(base, asset={"method": "library"})) and SH.piece_built(dict(base, asset=None))
    b = F.building()
    b["furniture"] = [base, dict(base, id="f2", type="unknown"), dict(base, id="f3", asset={"method": "none"})]
    room = next(r for r in b["rooms"] if r["id"] == "r_living")
    assert [f["id"] for f in CS.shown_pieces(room, b)] == ["f1"]
    assert [u["id"] for u in BB.unverified_items(b) if u["kind"] == "furniture"] == ["f1"]


def test_x3_reads_site_entrances_and_every_rise():
    from wenart.blender import exterior_checks as XC
    b = _whole()
    assert not [v for v in XC.check_exterior(b)["violations"] if v["check"] == "X3" and v["target"] == "d_front"]
    b["site"]["entrances"][0].update(solution="none", steps=None, landing=None)
    assert any(v["check"] == "X3" and v["target"] == "d_front" and v["severity"] == "major"
               for v in XC.check_exterior(b)["violations"])
    b["site"]["entrances"][0].update(ground_z=-2.0, rise=2.0, into_air=True)
    assert any(v["check"] == "X3" and v["severity"] == "critical" and "into the air" in v["message"]
               for v in XC.check_exterior(b)["violations"])


def test_report_prints_the_ground_level_numbers_b9():
    from wenart.report import m10 as RM
    b = _whole()
    block = RM.building_block(b)
    assert block["site"]["ground"] == [{"side": "all", "z": -0.15, "state": "assumed"}]
    text = "\n".join(RM.building_lines(block))
    assert "ground levels: all -0.15 m (assumed)" in text and "all -," not in text
    assert "Levels and ground (Milestone 12)" in text and "| d_front | 0.00 m | -0.15 m | 0.15 m | steps (1 x 0.150 m)" \
        in text
    assert "ground from: D3a" in text and "Flagged:" in text
