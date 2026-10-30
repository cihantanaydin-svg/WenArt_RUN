"""A stair is one coherent piece (30 Oct 2026, lesson UL192, user on real04 run 20261030-112241-full, the corridor
view cam_r_L0_koridor_1: "Something wrong with the stairs needs fixing"). CPU, pure.

What the view showed and what was measured: the risers, the soffit and the spandrels were slatted like the hall's
feature wall (the stair's structure slot copied the walls' procedural wood_slat); a grey bar floated across the first
flight at mid height with a block at its foot (the glass guard of the floor opening under the stair, the opening the
stair of the level below comes up through, ran across the stair's own first flight: its top rail and its shoe; the
glass is invisible); a stair rail ran level across the end of the well over the climbing winders; the twin stair's last
flight held a handrail over less than half its run (cut beside the floor guard above, no wall rail: the build counted
the newel's few cm as handrail, the review did not).

The rules are general (every stair of every project): a feature wall finish is never the stair's structure (the plain
plaster paint, ``shell.stair_structure_slot``); a floor opening's guard keeps out of the footprint of the stairs its
level builds (``shell.own_stair_footprints``, ``details.void_guard_runs(keep_out=)``), never out of the drawn upper end
of the stair below; over winders the balustrade rail follows their climb (``stair_rails._rail_line``); a flight's
handrail cover is measured between its first and last nosing in the build as in the review (``stair_rails._held``);
the pure envelope check ``stair_rails.envelope_review`` flags a stair part off its stair, under its floor, over its top
or floating over its steps and any other part in its walking zone; the scene manifest's ``stair.envelope`` carries it
and the model review's M18 reports it (for an older scene from the level's floor guards).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from test_stair_access_20261027 import _house
from test_stair_rails_20261028 import _chain, _l_plan, _straight, _u_plan

from wenart import geometry as G
from wenart.blender import details as D
from wenart.blender import model_review as MR
from wenart.blender import parametric as P
from wenart.blender import shell as SH
from wenart.blender import stair_access as SA
from wenart.blender import stair_rails as SR

ROOT = Path(__file__).resolve().parents[1]
REAL06 = ROOT / "tests" / "fixtures" / "real06_building_20261025.json"


def _stair_house():
    """The two-level house of test_stair_access (a U stair st0 on L0, its drawn upper end st1 on the L1 plan) and a
    floor opening of L0 (the stair of a level below would come up through it) whose north part lies under st0: its
    south edge y 2.6 crosses both flights of st0."""
    b = _house(upper_stair=True)
    SA.fix_arrivals(b)
    void = [(0.1, 2.6), (3.0, 2.6), (3.0, 4.0), (0.1, 4.0)]
    return b, void


def _built_plan(b, level, voids):
    walls = [w for w in b["walls"] if w["level_id"] == level["id"]]
    item = next(i for i in SH.plan_stairs(b, level, slab_void=True) if i["plan"])
    plan = SH.stair_build_plan(item["plan"], walls)
    SH.stair_guard_plan(b, level, plan, {"family": "modern"}, voids, SH.slab_openings_above(b, level))
    return plan


# --------------------------------------------------------------------------
# 1. The structure: never the walls' feature finish
# --------------------------------------------------------------------------

def test_a_feature_wall_finish_never_dresses_the_stair_structure():
    plain = SH.stair_structure_slot({"material": "plaster_white"})
    assert plain["material"] == SH.STAIR_STRUCTURE_PAINT
    for feature in ("wood_slat", "stone_wall_ledgestone"):
        assert SH.stair_feature_finish(feature)
        assert SH.stair_structure_slot({"material": feature}) == plain          # the plain plaster paint, no slats
    # the walls' colour phrase stays (the stair in the walls' colour), only the finish goes
    tinted = SH.stair_structure_slot({"material": "wood_slat", "colour": "warm greige"})
    assert tinted == {"material": SH.STAIR_STRUCTURE_PAINT, "colour": "warm greige"}
    # plain plaster and paint walls are the structure's look as before
    assert not SH.stair_feature_finish("plaster_white") and not SH.stair_feature_finish("paint")
    assert SH.stair_structure_slot({"material": "paint", "colour": "sage green"}) == \
        {"material": "paint", "colour": "sage green"}
    # the risers, steps and strings take the structure slot, the treads the tread slot
    plan = _u_plan()
    parts = P.stair_parts(plan)
    slots = P.stair_face_slots(parts)
    k = 0
    for p in parts:
        mine = slots[k:k + len(p["faces"])]
        k += len(p["faces"])
        if p["role"] in ("riser", "step"):
            assert P.STAIR_SLOTS.index("structure") in mine, p["role"]


# --------------------------------------------------------------------------
# 2. The floor opening's guard keeps out of the level's own stair
# --------------------------------------------------------------------------

def test_the_floor_opening_guard_keeps_out_of_the_stair_its_level_builds():
    b, void = _stair_house()
    l0, l1 = b["levels"]
    own = SH.own_stair_footprints(b, l0)
    assert len(own) == 1
    piece = next(f for f in b["furniture"] if f["id"] == "st0")
    rect = G.rotated_rectangle(piece["footprint"]["center"], piece["footprint"]["size"], 0.0)
    for p in rect:                                           # grown by the margin round the stair's footprint
        assert G.point_in_polygon((p[0] + 0.01 * (1 if p[0] > 1.2 else -1), p[1]), own[0])
    # the drawn upper end of the stair below (st1 on the top level, not built again) is not a stair of L1
    assert SH.own_stair_footprints(b, l1) == []
    walls = [w for w in b["walls"] if w["level_id"] == "L0"]
    bare = D.void_guard_runs(void, walls, [])
    across = [(p, q) for p, q in bare if abs(p[1] - q[1]) < 1e-9 and p[1] < 3.0]
    assert across and min(min(p[0], q[0]) for p, q in across) < 1.0          # before: across both flights
    (g,) = SH.floor_void_guards(b, l0, [void])
    assert g["keep_out"] == own and g["runs"]
    for p, q in g["runs"]:                                    # now: only the edges off the stair are guarded
        for t in (0.0, 0.25, 0.5, 0.75, 1.0):
            x = (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
            assert not G.point_in_polygon(x, own[0]) or SH.geom2d.distance_to_polygon_edges(x, own[0]) < 1e-3
    assert g["length_m"] < sum(G.distance(p, q) for p, q in bare)
    # the meshes follow the same runs
    metal, glass, runs = D.void_guards(g["polygon"], walls, g["arrivals"], 0.0, "glass_channel", keep_out=own)
    assert runs == g["runs"] and metal


def test_a_gallery_void_and_the_stair_void_of_the_floor_above_keep_their_guards():
    # a level with no stair keeps every free edge guarded (the keep-out is empty)
    assert len(D.void_guard_runs([(0, 0), (3, 0), (3, 2), (0, 2)], [], [], keep_out=[])) == 4
    # real06: the upper floor guards the opening its stair comes up through (the stair drawn on the L1 plan is the
    # drawn upper end of the L0 stair, not a stair of L1)
    if not REAL06.is_file():
        pytest.skip("no committed real06 building")
    from wenart.blender import build as BU
    prep = BU.prepare(json.loads(REAL06.read_text(encoding="utf-8")), "base", None, style_family="scandinavian")
    vb = prep["building"]
    l1 = next(lv for lv in vb["levels"] if lv["id"] == "L1")
    assert SH.own_stair_footprints(vb, l1) == []
    assert SH.floor_void_guards(vb, l1, prep["slabs"]["by_level"]["L1"]["under"]["voids"])


# --------------------------------------------------------------------------
# 3. The rails: over winders they climb; a flight's cover is measured on its run
# --------------------------------------------------------------------------

def test_the_rail_over_the_winders_climbs_with_them_and_stays_a_rail_height_over_them():
    # the U stair's well end (0.27 m between two newels) over seven winders; with and without the walls round it
    for plan in (_u_plan(), _u_plan(walls=[])):
        guards = SR.plan_guards(plan)
        winders = [r for r in guards["rails"] if r["what"] == "winders" and r["type"] == "balustrade"]
        assert winders
        for rl in winders:
            zs = [p[2] for p in rl["path"]]
            assert zs[-1] > zs[0]                                # it climbs, never a level bar over climbing steps
            for k in range(1, 10):
                p = SR._lerp(rl["path"][0], rl["path"][-1], k / 10.0)
                over = p[2] - SR._winder_top(plan, p[:2])
                assert P.STAIR_RAIL_HEIGHT - 1e-6 <= over <= SR.WINDER_RAIL_MAX_M + 1e-6
        assert not [f for f in SR.review(guards, plan, plan["wall_rects"]) if f["rule"] == "height"]


def test_the_review_finds_a_rail_floating_far_over_the_winders():
    plan = _u_plan()
    guards = SR.plan_guards(plan)
    well = next(r for r in _chain(guards, "left") if r["what"] == "winders")
    lifted = json.loads(json.dumps(guards))
    for rl in lifted["rails"]:
        if rl["id"] == well["id"]:
            rl["path"] = [[p[0], p[1], p[2] + 0.5] for p in rl["path"]]
    found = [f for f in SR.review(lifted, plan, plan["wall_rects"]) if f["rule"] == "height"]
    assert found and "over a winder" in found[0]["message"]
    # the envelope check finds its parts floating over the steps too
    lifted_plan = dict(plan, guards=lifted)
    rules = {f["rule"] for f in SR.envelope_review(lifted_plan, SR.guard_parts(lifted))}
    assert "floating" in rules


def test_a_flight_cut_beside_the_floor_guard_above_gets_a_wall_rail_when_half_its_run_is_open():
    from test_stair_rails_20261028 import _under_floor_guard
    plan, openings, guard = _under_floor_guard()
    guards = SR.plan_guards(plan, openings, guard)
    ctx = SR._context(plan, openings, guard)
    held = SR._held(plan, ctx, guards["rails"])
    for fr in ctx["frames"]:                               # the cover never counts past the flight's nosings
        assert held.get(fr["index"], 0.0) <= fr["L"] + 1e-6
    assert not [f for f in SR.review(guards, plan, plan["wall_rects"], openings, guard) if f["rule"] == "no_handrail"]


# --------------------------------------------------------------------------
# 4. The envelope check (pure) and its record for the model review's M18
# --------------------------------------------------------------------------

def test_every_designed_stair_lies_in_its_envelope():
    plans = [_u_plan(), _u_plan(winders=None), _u_plan(arrives=False), _straight(), _straight(walls=False),
             _straight(width=1.2), _l_plan(), _l_plan(1.2)]
    for plan in plans:
        for family in (None, "modern", "scandinavian", "japandi", "classic"):
            plan["design"] = SR.stair_design({"family": family} if family else None)
            plan["guards"] = SR.plan_guards(plan)
            assert SR.envelope_review(plan, P.stair_parts(plan)) == [], family


def test_the_envelope_check_flags_parts_off_the_stair_under_its_floor_or_over_its_top():
    plan = _u_plan()
    plan["guards"] = SR.plan_guards(plan)
    box = lambda x, y, z0, z1: {"role": "string", "verts": [(x, y, z0), (x + 0.05, y, z0), (x, y, z1), (x + 0.05, y, z1)],
                                "faces": [(0, 1, 3, 2)]}
    off = SR.envelope_review(plan, [box(5.0, 5.0, 0.0, 0.5)])                       # 4 m off the stair
    under = SR.envelope_review(plan, [box(0.5, 0.0, -0.4, 0.2)])                     # under the floor
    over = SR.envelope_review(plan, [box(0.5, 0.0, 0.2, plan["rise_m"] + 1.5)])      # over the top
    for found in (off, under, over):
        assert [f["rule"] for f in found][:1] == ["outside_envelope"] and found[0]["severity"] == "major"
    assert all(r in SR.ENVELOPE_RULES for f in off + under + over for r in [f["rule"]])


def test_the_envelope_check_finds_a_guard_across_the_flight_and_the_build_records_none():
    b, void = _stair_house()
    l0 = b["levels"][0]
    walls = [w for w in b["walls"] if w["level_id"] == "L0"]
    plan = _built_plan(b, l0, [void])
    parts = P.stair_parts(plan)
    before = [{"id": "void_guard_L0_0", "segments": SR.guard_run_segments(D.void_guard_runs(void, walls, []))}]
    (f,) = SR.envelope_review(plan, parts, before)
    assert f["rule"] == "crosses_walking_line" and f["severity"] == "critical"
    assert f["metrics"]["part"] == "void_guard_L0_0" and 0.0 < f["metrics"]["over_m"] < SR.WALK_HEADROOM_M
    # a foreign mesh (faces) is read the same way
    metal, _glass, _runs = D.void_guards(void, walls, [], 0.0, "glass_channel")
    mesh = [{"id": f"guard_{i}", "verts": v, "faces": fc} for i, (v, fc) in enumerate(metal)]
    assert any(x["rule"] == "crosses_walking_line" for x in SR.envelope_review(plan, (), mesh))
    # as built now: the guard keeps out of the stair, nothing in its walking zone, the record carries the check
    foreign = SH.level_guard_segments(b, l0, [void])
    assert foreign and SR.envelope_review(plan, parts, foreign) == []
    assert SH.stair_record(plan, parts, foreign)["envelope"] == []
    # a guard that stands off the stair (beside its foot, outside its run) is no obstacle
    beside = [{"id": "g", "segments": SR.guard_run_segments([((2.5, 2.2), (3.0, 2.2))])}]
    assert SR.envelope_review(plan, parts, beside) == []


def test_m18_reports_the_envelope_of_the_scene_and_of_an_older_scene():
    b, void = _stair_house()
    l0 = b["levels"][0]
    walls = [w for w in b["walls"] if w["level_id"] == "L0"]
    plan = _built_plan(b, l0, [void])
    rec = {"rails": plan["rails"], "structure": SR.structure_of(plan), "guards": SR.summary(plan["guards"])}
    guard_old = {"name": "void_guard_L0_0", "level_id": "L0", "kind": "railing",
                 "assumed": {"detail": "void_guard", "balustrade": "glass_channel",
                             "runs": [[list(p), list(q)] for p, q in D.void_guard_runs(void, walls, [])]}}
    stair = {"element_id": "st0", "kind": "furniture", "type": "stair", "level_id": "L0", "stair": rec}
    found, n = MR.stair_rails_review(b, {"objects": [stair, guard_old]})
    walk = [f for f in found if f["metrics"]["rule"] == "crosses_walking_line"]
    assert n == 1 and walk and walk[0]["check"] == "M18" and walk[0]["severity"] == "critical"
    assert walk[0]["fix"] == MR.FIX_ENVELOPE and walk[0]["owner"] == "build"
    # a scene built now carries its envelope: an empty one reports nothing
    stair_new = dict(stair, stair=dict(rec, envelope=[]))
    found, n = MR.stair_rails_review(b, {"objects": [stair_new, guard_old]})
    assert n == 1 and not [f for f in found if f["metrics"]["rule"] in SR.ENVELOPE_RULES]
