"""Entrances that make sense (26 Oct 2026; user, on real06's ext_4 render: "these sections not making sense, the AI
inspector needs to make sense of this"). real06's garden door and small side door in the inner corner of its L each
got a landing and four risers; the two flights ran into each other and their handrails crossed in front of the small
door. General rules (wenart/blender/site.py ``entrance_layout``, wenart/levels/model.py ``main_entrance``,
wenart/blender/model_review.py M8), tested here on hand-made buildings and on real06's records (CPU)."""
import json
from pathlib import Path

import pytest

from wenart import geometry as G
from wenart.agent import causes as CS
from wenart.agent import inspector as INS
from wenart.blender import build as BB
from wenart.blender import geom2d
from wenart.blender import model_review as MR
from wenart.blender import site as S
from wenart.levels import model as M
from tests import _levels_fixture as F

ROOT = Path(__file__).resolve().parents[1]
P = M.level_params()


def _ent(did, centre, outward, width, rise=0.5, main=False, ramp=False, room="r_hall", top=0.0, half_t=0.1):
    """An entrance as ``site.record_entrances`` returns it, its record as ``levels.model`` writes it."""
    face = (centre[0] + outward[0] * half_t, centre[1] + outward[1] * half_t)
    st = M.steps_for(rise, width + P["landing_extra_width"], P)
    rec = {"door_id": did, "level_id": "L0", "room_id": room, "threshold_z": top, "ground_z": top - rise, "rise": rise,
           "centre": list(centre), "outward": list(outward), "face": list(face), "width": width, "half_t": half_t,
           "solution": ("steps_and_ramp" if ramp else "steps") if st else "none", "steps": st,
           "ramp": M.ramp_for(rise, P) if ramp else None, "main": main,
           "landing": {"width": width + P["landing_extra_width"], "depth": P["landing_depth"], "z": top} if st else None}
    return {"opening_id": did, "level_id": "L0", "centre": tuple(centre), "outward": tuple(outward),
            "axis": S.nearest_axis(outward), "width": width, "bottom": top, "ground_z": top - rise, "rise": rise,
            "half_t": half_t, "record": rec}


def _l_building(rise=0.5):
    """An L: the west wing's south wall (0, 4)-(5, 4) holds a 2.40 m sliding garden door into the living room, the
    east wing's west wall (5, 4)-(5, 0) a 0.90 m swing door into the hall: both in the inner corner (5, 4)."""
    b = F.building()
    b["project"]["brief"] = {"levels": {"ground_rise": rise}}
    b["walls"] = [F._wall("w_1", (0, 4), (5, 4)), F._wall("w_2", (5, 4), (5, 0)), F._wall("w_3", (5, 0), (10, 0)),
                  F._wall("w_4", (10, 0), (10, 8)), F._wall("w_5", (10, 8), (0, 8)), F._wall("w_6", (0, 8), (0, 4)),
                  F._wall("w_7", (5, 4), (10, 4), exterior=False)]
    b["openings"] = [dict(F._opening("d_garden", "door", "w_1", (3.0, 4.0), 2.4), operation="sliding"),
                     dict(F._opening("d_side", "door", "w_2", (5.0, 2.0), 0.9), operation="swing"),
                     F._opening("d_inner", "door", "w_7", (7.5, 4.0), 0.9),
                     F._opening("win_1", "window", "w_3", (7.5, 0.0), 1.2)]
    b["rooms"] = [F._room("r_living", [(0.1, 4.1), (9.9, 4.1), (9.9, 7.9), (0.1, 7.9)], "living", label="Salon"),
                  F._room("r_hall", [(5.1, 0.1), (9.9, 0.1), (9.9, 3.9), (5.1, 3.9)], "hall", label="Hol")]
    return b


def _zones(ents, shrink=0.0):
    return {e["opening_id"]: S.door_approach(e, shrink) for e in ents}


def _rail_in_zones(st, zones, own=()):
    return sum(S.segment_in_convex(a, b, z) for a, b in st.get("rails") or [] for i, z in zones.items()
               if i not in own)


# --------------------------------------------------------------------------
# Rule 1: doors whose steps would meet share one platform and one flight
# --------------------------------------------------------------------------

def test_the_l_corner_doors_get_one_platform_one_flight_and_no_rail_across_a_door():
    n = M.infer_levels(_l_building())
    recs = {e["door_id"]: e for e in n["site"]["entrances"]}
    assert recs["d_side"]["main"] and "hall" in recs["d_side"]["main_reason"]          # rule 3: not the garden door
    prep = BB.prepare(n, "base", None)
    inf = prep["site"]["inferred"]
    outline = prep["ground_outline"]
    steps = inf["steps"]
    assert len(steps) == 1 and inf["entrance_groups"] == [["d_side", "d_garden"]]
    st = steps[0]
    assert st["opening_id"] == "d_side" and st["members"] == ["d_garden"]
    top = st["platform"]["z"]
    plat = [b["polygon"] for b in st["blocks"] if abs(b["z_top"] - top) < 1e-9]
    flight = [b for b in st["blocks"] if b["z_top"] < top - 1e-9]
    assert plat and len(flight) == st["count"] == 3 and st["risers"] == 4
    assert not any(S.inside_outline(p, outline) for p in plat)                     # never into the building
    ents = inf["entrances"]
    for e in ents:                                                                 # both doors open onto it
        zone = S.door_approach(e, 0.05)
        assert all(any(G.point_in_polygon(q, p) for p in plat) for q in zone)
    assert st["flight"]["dir"] == [-1.0, 0.0] and "free edge" in st["flight"]["placement"]   # the lead's way out
    assert len(st["rails"]) == 2 and _rail_in_zones(st, _zones(ents)) == 0.0     # rails along the flight only
    for a, b in st["rails"]:
        assert not any(G.point_in_polygon(q[:2], p) and geom2d.distance_to_polygon_edges(q[:2], p) > 1e-6
                       for q in (a, b) for p in plat)                              # never over the platform
    paths = [p for p in inf["paths"]]
    assert len(paths) == 1 and set(paths[0]["opening_ids"]) == {"d_side", "d_garden"}
    assert any(a["field"].startswith("entrance_platform:") for a in prep["site"]["assumed"])
    rec = MR.review(prep["building"], None, prep)
    assert rec["checks"]["M8"]["status"] == "ok" and rec["checks"]["M8"]["checked"] == 2
    assert not [f for f in rec["findings"] if f["check"] == "M8"]
    # the exterior check X3 counts the member door as reached (the platform's steps)
    from wenart.blender import exterior_checks as EC
    out: list = []
    EC._x3(prep["building"], prep, out)
    assert not [v for v in out if v["target"] in ("d_side", "d_garden") and "no steps" in v["message"]]
    # the layout of before (each door its own landing and flight): M8 finds the clash and the crossing rail
    old = [s for s in (S.entrance_steps(e) for e in S.record_entrances(n, M.base_levels(n))) if s["blocks"]]
    got, _n = MR.entrances_make_sense(prep["building"], dict(inf, steps=old))
    kinds = {(f["severity"], f["target"], "overlap" in f["message"]) for f in got}
    assert ("critical", "d_side", False) in kinds                                  # the garden flight's rail
    assert any(f["severity"] == "critical" and "overlap" in f["message"] for f in got)


def test_side_by_side_doors_share_one_platform_and_a_far_door_keeps_its_steps():
    outline = [(0.0, 0.0), (12.0, 0.0), (12.0, 8.0), (0.0, 8.0)]
    a = _ent("d_a", (6.3, 0.1), (0.0, -1.0), 0.9)                 # landing x 5.55-7.05
    b = _ent("d_b", (8.0, 0.1), (0.0, -1.0), 1.0)                 # landing x 7.20-8.80: 0.15 m apart
    c = _ent("d_c", (2.0, 0.1), (0.0, -1.0), 0.9)                 # 2.8 m away
    ents = [a, b, c]
    lay = S.entrance_layout(ents, outline)
    assert lay["groups"] == [["d_b", "d_a"]] and lay["members"] == {"d_a": "d_b"}       # lead: the wider door
    assert "d_a" not in lay["steps"] and lay["steps"]["d_c"] == S.entrance_steps(c)    # a single keeps its steps
    st = lay["steps"]["d_b"]
    plat = [p["polygon"] for p in st["blocks"] if p["z_top"] == 0.0]
    xs = [q[0] for p in plat for q in p]
    ys = [q[1] for p in plat for q in p]
    assert min(xs) == pytest.approx(5.55) and max(xs) == pytest.approx(8.8) and min(ys) == pytest.approx(-1.2)
    fx = [q[0] for q in st["flight"]["footprint"]]
    assert (min(fx) + max(fx)) / 2.0 == pytest.approx(8.0)                        # centred on the lead door
    assert st["flight"]["dir"] == [0.0, -1.0] and len(st["rails"]) == 2
    assert all(q[1] <= -1.2 + 1e-9 for r in st["rails"] for q in r)               # from the platform's edge out
    assert _rail_in_zones(st, _zones(ents)) == 0.0
    paths = S.entrance_paths([e for e in ents if e["opening_id"] not in lay["members"]], lay["steps"],
                             S.inferred_plot(outline))
    assert sorted(tuple(p["opening_ids"]) for p in paths) == [("d_b", "d_a"), ("d_c",)]
    assert any(x["field"] == "entrance_platform:d_b,d_a" for x in lay["assumed"])
    # landings at other heights are not one platform
    hi = _ent("d_hi", (6.3, 0.1), (0.0, -1.0), 0.9, top=0.3, rise=0.8)
    assert S.entrance_layout([hi, b], outline)["groups"] == []


# --------------------------------------------------------------------------
# Rule 2: a ramp never passes in front of another door
# --------------------------------------------------------------------------

def test_a_ramp_keeps_clear_of_the_other_doors():
    outline = [(0.0, 0.0), (14.0, 0.0), (14.0, 8.0), (0.0, 8.0)]
    a = _ent("d_a", (5.0, 0.1), (0.0, -1.0), 0.9, main=True, ramp=True)
    alone = S.entrance_layout([a], outline)["steps"]["d_a"]["ramp"]
    assert alone["placement"] == S.RAMP_PLACES[0] and alone["reason"] == ""     # as before: along the facade, +u
    length = a["record"]["ramp"]["length"]
    assert [round(x, 6) for x in alone["s"]] == [0.75, round(0.75 + length, 6)] and alone["d"] == [0.0, 1.2]
    b = _ent("d_b", (9.0, 0.1), (0.0, -1.0), 0.9, rise=0.0)          # at grade, 3.5 m along the +u side
    lay = S.entrance_layout([a, b], outline)
    r = lay["steps"]["d_a"]["ramp"]
    assert r["placement"] == S.RAMP_PLACES[1] and max(q[0] for q in r["polygon"]) <= 4.25 + 1e-9
    assert any(x["field"] == "ramp:d_a" and "in front of another door" in x["reason"] for x in lay["assumed"])
    c = _ent("d_c", (2.0, 0.1), (0.0, -1.0), 0.9, rise=0.0)          # and on the -u side: straight out
    lay = S.entrance_layout([a, b, c], outline)
    st = lay["steps"]["d_a"]
    assert st["ramp"]["placement"] == S.RAMP_PLACES[2]
    assert min(q[1] for q in st["ramp"]["polygon"]) == pytest.approx(-1.2 - length)
    assert len([x for x in st["blocks"] if x["z_top"] == 0.0]) == 2               # the landing widened to the ramp
    zones = _zones([b, c])
    assert not any(S.convex_overlap(st["ramp"]["polygon"], z, 0.01) for z in zones.values())
    assert _rail_in_zones(st, zones) == 0.0
    # nothing clear: the first place, flagged for review
    huge = [(-50.0, -50.0), (50.0, -50.0), (50.0, -0.05), (-50.0, -0.05)]
    st = S.entrance_steps(a, keep_out=[huge])
    assert st["ramp"]["placement"] == S.RAMP_PLACES[0] and not st["ramp"]["clear"]
    assert "to review" in st["ramp"]["reason"]
    # M8 sees the ramp of before in front of d_b (major) and its handrails across d_b's way out (critical)
    old = S.entrance_steps(a)
    got, _n = MR.entrances_make_sense({"rooms": []}, {"entrances": [a, b], "steps": [old]})
    assert sorted((f["severity"], f["target"], "ramp" in f["message"]) for f in got) == [
        ("critical", "d_b", False), ("major", "d_b", True)]
    new = S.entrance_layout([a, b], outline)["steps"]
    assert MR.entrances_make_sense({"rooms": []}, {"entrances": [a, b], "steps": list(new.values())})[0] == []


# --------------------------------------------------------------------------
# Rule 3: the main entrance
# --------------------------------------------------------------------------

def _main(doors, marks=()):
    b = {"openings": [{"id": d, "operation": op} for d, op, *_ in doors],
         "rooms": [{"id": f"r_{d}", "room_type": rt, "label": lab} for d, _op, _w, rt, lab, _o in doors]}
    usable = [{"door_id": d, "width": w, "outward": list(o), "room_id": f"r_{d}"} for d, _op, w, _rt, _l, o in doors]
    main, why = M.main_entrance(b, usable, list(marks))
    return main["door_id"], why


def test_the_main_entrance_is_the_door_a_visitor_uses():
    garden = ("d_garden", "sliding", 2.95, "living", "Salon", (0, -1))
    hall = ("d_hall", "swing", 0.9, "hall", "Hol", (-1, 0))
    room = ("d_room", "swing", 0.8, "living", "Salon", (-1, 0))
    assert _main([garden, hall])[0] == "d_hall"
    door, why = _main([garden, room])
    assert door == "d_room" and "no entrance door into a hall" in why
    assert _main([garden, ("d_slide", "sliding", 2.15, "living", "Salon", (0, -1))])[0] == "d_garden"  # only wide
    assert _main([garden, hall], [{"kind": "entrance", "used_for": ["entrance:d_garden"]}])[0] == "d_garden"
    garage = ("d_garage", "swing", 0.9, "other", "Garaj", (0, -1))
    assert _main([garage, room])[0] == "d_room"                                    # a garage door is no front door
    double = ("d_double", "double", 1.4, "hall", "Hol", (0, 1))                   # synthetic-07's front door
    assert _main([("d_bed", "swing", 0.9, "bedroom", "Yatak Odası", (0, -1)), double])[0] == "d_double"
    assert _main([("d_0", None, 0.88, "hall", "Antre", (0, 1))])[0] == "d_0"        # operation null = swing


def test_real06_main_entrance_is_the_small_swing_door_not_the_garden_door():
    fx = json.loads((ROOT / "tests" / "fixtures" / "real06_entrances_20261026.json").read_text(encoding="utf-8"))
    usable = [e for e in fx["site"]["entrances"] if not e.get("into_air") and not e.get("below_ground")]
    main, why = M.main_entrance(fx, usable, [])
    assert main["door_id"] == "d_L0_004" and "swing" in why                       # was d_L0_006 (2.95 m sliding)


# --------------------------------------------------------------------------
# Rule 4: the model review's M8 on real06's records
# --------------------------------------------------------------------------

def _real06():
    fx = json.loads((ROOT / "tests" / "fixtures" / "real06_entrances_20261026.json").read_text(encoding="utf-8"))
    ents = S.record_entrances(fx, fx["levels"])
    outline = geom2d.wall_outline(fx["walls"])[0]
    return fx, ents, outline


def test_m8_finds_real06s_crossing_and_nothing_after_the_merge():
    fx, ents, outline = _real06()
    old = [st for st in (S.entrance_steps(e) for e in ents) if st["blocks"]]
    got, n = MR.entrances_make_sense(fx, {"entrances": ents, "steps": old})
    assert n == 4
    crit = [f for f in got if f["severity"] == "critical"]
    assert any("overlap" in f["message"] and set(f["metrics"]["doors"]) == {"d_L0_004", "d_L0_006"} for f in crit)
    rail = [f for f in crit if f["target"] == "d_L0_004" and "handrail" in f["message"]]
    assert rail and rail[0]["metrics"]["steps_of"] == ["d_L0_006"] and rail[0]["metrics"]["rail_m"] > 0.3
    for main in ("d_L0_006", "d_L0_004"):              # the records as written, and with the new main entrance
        for e in ents:
            e["record"]["main"] = e["opening_id"] == main
        lay = S.entrance_layout(ents, outline)
        assert lay["groups"] == [[main, ({"d_L0_006", "d_L0_004"} - {main}).pop()]]
        steps = [s for s in lay["steps"].values() if s["blocks"]]
        assert MR.entrances_make_sense(fx, {"entrances": ents, "steps": steps})[0] == []
        st = lay["steps"][main]
        assert st["platform"]["z"] == 0.0 and sorted(st["platform"]["size_m"]) == [3.0, 4.15]
        assert len(st["rails"]) == 2 and st["risers"] == 4
        plat = [b["polygon"] for b in st["blocks"] if b["z_top"] == 0.0]
        assert not any(S.inside_outline(p, outline) for p in plat)
    assert st["flight"]["dir"] == [-1.0, 0.0]          # d_L0_004 leads: the flight goes out west, beside the corner


def test_m8_flags_steps_in_front_of_a_garage_door_and_is_reported_to_the_site_stage():
    g = _ent("d_gar", (3.0, 0.1), (0.0, -1.0), 0.9, room="r_garaj")
    built = {"rooms": [{"id": "r_garaj", "room_type": "other", "label": "Garaj", "label_raw": "GARAJ"}]}
    got, _n = MR.entrances_make_sense(built, {"entrances": [g], "steps": [S.entrance_steps(g)]})
    assert [(f["check"], f["severity"], f["target"]) for f in got] == [("M8", "major", "d_gar")]
    assert S.room_role(built["rooms"][0]) == "garage" and S.room_role({"room_type": "hall"}) == "hall"
    assert S.room_role({"room_type": "other", "label": "Giriş"}) == "hall" and S.room_role(None) is None
    f = dict(got[0], source="code")
    assert CS.cause_of(f) == "entrance_layout" and CS.CAUSE_TOOLS["entrance_layout"] == ()
    assert CS.REPORT_TO["entrance_layout"] == "site" and "site stage" in CS.NO_TOOL_REASON["entrance_layout"]
    assert INS._row(f, set(), set())["outcome"].startswith("handed to the site stage")
    assert "M8" in MR.CHECKS
    rec = {"round": 4, "counts": {"seen": 0, "visitor": 0, "fixed": 0, "handed": 1, "open": 0, "dropped": 0,
                                  "architect_open": 0, "architect_open_major": 0},
           "vision": [], "code": [INS._row(f, set(), set())], "dropped": [], "architect_open": [],
           "model_review": {"checks": {"M8": {"checked": 1, "failed": 1, "status": "ok"}}, "findings": got}}
    md = INS.report_md(rec, "t")
    assert "M8 entrances that make sense" in md and "d_gar" in md
