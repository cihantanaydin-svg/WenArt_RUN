"""Stairs as one designed piece (28 Oct 2026, user on real04's stairs: "There should have been better indoor stair
solutions should be there I did not like this one"; the corridor view: steel rails at different angles crossing each
other near the well). CPU, pure.

The rules are general (wenart/blender/stair_rails.py): one continuous balustrade per open side with newels at its
turns and ends, the handrail 0.90 m over the nosing line (1.0 m on a level edge), a wall handrail where a flight is
wide or would hold none, nothing through a tread, a wall or the floor above, the floor guard above takes over over
that floor, infill gaps under 0.11 m, the look of the house's style family, a lighter structure in the light styles,
no spandrel panel over a floor opening; the model review's M18 finds rails that cross or stop short. The stairs here
are synthetic (a U stair with winders between walls, the same under a floor guard, straight stairs, a dog-leg, an L);
real04's stairs are the case that showed the problem.
"""
from __future__ import annotations

import math

import pytest

from wenart.agent import causes as CS
from wenart.audit import kinds as K
from wenart.blender import model_review as MR
from wenart.blender import parametric as P
from wenart.blender import shell as SH
from wenart.blender import stair_access as SA
from wenart.blender import stair_rails as SR


def _wall(wid, a, b, t=0.2, lid="L0"):
    return {"id": wid, "level_id": lid, "start": list(a), "end": list(b), "thickness": t}


# The U stair of test_details_and_terraces._u_stair: flight 1 along +x at y 0 (0.95 m wide), flight 2 back along -x
# at y 1.15, a 0.2 m well between them, the half landing x 1.4-2.67 turned into winders; walls on the outer sides.
U_WALLS = [_wall("ws", (-0.5, -0.575), (2.87, -0.575)), _wall("we", (2.77, -0.7), (2.77, 1.8)),
           _wall("wn", (-0.5, 1.725), (2.87, 1.725))]


def _u_piece(winders="auto"):
    flights = [{"start": [0.0, 0.0], "end": [1.4, 0.0], "width": 0.95, "lines": 6},
               {"start": [0.27, 1.15], "end": [1.39, 1.15], "width": 0.95, "lines": 5}]
    data = {"flights": flights, "landing": {"polygon": [[1.4, -0.475], [1.4, 1.625], [2.67, 1.625], [2.67, -0.475]]},
            "direction": [1.0, 0.0], "turn": "U"}
    if winders is not None:
        data["winders"] = winders
    return {"id": "st", "type": "stair", "footprint": {"center": [1.33, 0.57], "size": [2.67, 2.1], "rotation_deg": 0},
            "stair": data}


def _u_plan(walls=U_WALLS, arrives=True, **kw):
    """The U stair's plan; ``arrives``: it comes up through the floor opening of the level above (a whole building,
    ``shell.plan_stairs`` with the slab's opening: the rails run to the top); else under a capped shaft."""
    plan = P.stair_plan(_u_piece(**kw), 3.0, 2.85, walls=walls)
    if arrives:
        plan["rail_limit"] = plan["rise_m"] + P.STAIR_RAIL_HEIGHT + P.STAIR_CAP_CLEARANCE
        plan["cap_z"] = plan["rise_m"] - 0.005
    return plan


def _chain(guards, side):
    return [r for r in guards["rails"] if r["side"] == side and r["type"] == "balustrade"]


def _hull(plan):
    frames = [SR.flight_frame(f, plan["riser_m"]) for f in plan["flights"]]
    return SR._hull(plan, frames)


# --------------------------------------------------------------------------
# 1. The look follows the house's style family
# --------------------------------------------------------------------------

def test_the_stair_design_follows_the_style_family_in_the_house_language():
    modern = SR.stair_design({"family": "modern"})
    assert (modern["structure"], modern["infill"], modern["rail"]["key"], modern["string_key"]) == \
        ("plate", "glass", "steel", "steel") and modern["kind"] == "glass_channel" and modern["posts_every"] is None
    scandi = SR.stair_design({"family": "scandinavian"})
    assert scandi["structure"] == "stringer" and scandi["infill"] == "glass" and scandi["posts_every"] and \
        scandi["rail"]["key"] == "timber"
    japandi = SR.stair_design({"family": "japandi"})
    assert (japandi["structure"], japandi["infill"], japandi["rail"]["key"]) == ("stringer", "slats", "timber")
    classic = SR.stair_design({"family": "classic"})
    assert (classic["structure"], classic["infill"], classic["string"]) == ("solid", "turned", False)
    # a railing slot that names balusters wins over the family's glass (details.balustrade_kind)
    assert SR.stair_design({"family": "modern", "railing": {"material": "black steel balusters"}})["infill"] == "bars"
    plain = SR.stair_design(None)
    assert (plain["structure"], plain["infill"], plain["rail"]["key"]) == ("solid", "bars", "steel")
    assert all(SR.stair_design({"family": f})["structure"] in SR.STRUCTURES for f in SR.FAMILY_DESIGN)


# --------------------------------------------------------------------------
# 2. One continuous balustrade per open side: newels at the turn, no crossing, the right heights
# --------------------------------------------------------------------------

def test_a_u_stair_with_winders_gets_one_balustrade_round_its_well():
    plan = _u_plan()
    sides = {s["side"]: s for s in plan["sides"]}
    assert sides["left"]["inner"] and [(leg["what"], leg["wall"]) for leg in sides["left"]["legs"]] == \
        [("flight", False), ("winders", False), ("flight", False)]
    assert all(leg["wall"] for leg in sides["right"]["legs"])                  # the outer side: the walls
    guards = SR.plan_guards(plan)
    chain = _chain(guards, "left")
    assert [r["what"] for r in chain] == ["flight", "winders", "flight"]
    # continuous: every rail ends in the newel the next one starts from
    assert all(a["posts"][1] == b["posts"][0] for a, b in zip(chain, chain[1:]))
    assert len(guards["posts"]) == 4 and not [r for r in guards["rails"] if r["type"] == "wall"]
    frames = {f["index"]: SR.flight_frame(f, plan["riser_m"]) for f in plan["flights"]}
    for r in chain:
        if r["what"] != "flight":
            continue
        fr = frames[r["flight"]]
        for p in r["path"]:                                     # 0.90 m over the nosing line (its pitch at the newels)
            s = SR._s_of(fr, p[:2])
            assert p[2] - (fr["base"] + fr["riser"] + s * fr["k"]) == pytest.approx(P.STAIR_RAIL_HEIGHT)
    well = chain[1]
    assert well["path"][0][2] == pytest.approx(well["path"][1][2])           # a short leg between two newels: level
    mid = SR._lerp(well["path"][0][:2], well["path"][1][:2], 0.5)
    assert well["path"][0][2] >= SR._winder_top(plan, mid) + P.STAIR_RAIL_HEIGHT - 1e-6
    # the newels at the turn rise over the rails that die into them; the starting newel stands on the first tread
    posts = {p["id"]: p for p in guards["posts"]}
    for a, b in zip(chain, chain[1:]):
        newel = posts[a["posts"][1]]
        assert newel["z1"] >= max(a["path"][-1][2], b["path"][0][2]) + SR.NEWEL_CAP_M - 1e-6
    start = posts[chain[0]["posts"][0]]
    s0 = SR._s_of(frames[0], start["at"])
    assert s0 - SR.NEWEL_M / 2.0 >= 0.0 and start["z0"] == pytest.approx(frames[0]["base"] + frames[0]["riser"])
    assert SR.review(guards, plan, plan["wall_rects"]) == []
    hull = _hull(plan)
    from wenart import geometry as G
    from wenart.blender import geom2d
    for r in guards["rails"]:
        for p in r["path"]:
            assert G.point_in_polygon(p[:2], hull) or geom2d.distance_to_polygon_edges(p[:2], hull) < 0.05


def test_no_rail_crosses_another_and_none_runs_through_a_tread():
    for kw in ({}, {"winders": None}):                     # with winders and with the flat half landing
        plan = _u_plan(**kw)
        guards = SR.plan_guards(plan)
        segs = [(r, a, b) for r in guards["rails"] for a, b in zip(r["path"], r["path"][1:])]
        for i, (ra, a0, a1) in enumerate(segs):
            for rb, b0, b1 in segs[i + 1:]:
                if ra["id"] == rb["id"] or set(ra["posts"]) & set(rb["posts"]):
                    continue
                assert SR.seg_dist3(a0, a1, b0, b1) >= ra["r"] + rb["r"] + 0.01
        for r in guards["rails"]:
            for a, b in zip(r["path"], r["path"][1:]):
                for k in range(1, 20):
                    p = SR._lerp(a, b, k / 20.0)
                    z = SR.surface_z(plan, p[:2])
                    if z is not None:
                        assert p[2] - 2 * r["r"] > z
    # the flat half landing's well edge is a level guard, 1.0 m over the landing
    flat_plan = _u_plan(winders=None)
    well = [r for r in SR.plan_guards(flat_plan)["rails"] if r["what"] == "landing"]
    assert well and all(p[2] == pytest.approx(flat_plan["landing"]["z"] + SR.LEVEL_GUARD_M) for p in well[0]["path"])


def test_the_infill_has_no_gap_a_child_passes_and_follows_the_rail():
    plan = _u_plan()
    for family in (None, "japandi", "classic", "mediterranean", "modern", "scandinavian"):
        plan["design"] = SR.stair_design({"family": family} if family else None)
        guards = SR.plan_guards(plan)
        assert guards["max_gap_m"] < SR.GAP_MAX_M, family
        bal = [p for p in guards["infill"] if p["type"] == "baluster"]
        glass = [p for p in guards["infill"] if p["type"] == "glass"]
        assert bal or glass, family
        rails = _chain(guards, "left")
        for b in bal:                                          # every baluster reaches the rail over its leg
            mine = [r for r in rails if r["leg"] == b["leg"]]
            if not mine:
                continue
            near = mine[0]
            a0, a1 = near["path"][0], near["path"][-1]
            t = SR._dot(SR._sub(b["at"], a0[:2]), SR._unit(SR._sub(a1[:2], a0[:2])))
            t /= max(SR.G.distance(a0[:2], a1[:2]), 1e-9)
            if not 0.0 <= t <= 1.0:
                continue
            top = a0[2] + (a1[2] - a0[2]) * t
            assert b["z1"] == pytest.approx(top - 2 * near["r"] + 0.004, abs=1e-3)
        parts = SR.guard_parts(guards) + SR.string_parts(guards)
        assert all(len(p["faces"]) >= 4 for p in parts)
        slots = P.stair_face_slots(parts)
        assert len(slots) == sum(len(p["faces"]) for p in parts)
        if family in ("japandi", "classic"):
            assert 4 in slots                                   # the timber slot (STAIR_SLOTS)


# --------------------------------------------------------------------------
# 3. The floor guard of the level above takes over; nothing through the floor above
# --------------------------------------------------------------------------

def _under_floor_guard():
    """The U stair under a floor whose opening is the second flight and the landing only (the first flight and the
    well under the slab), its guard 0.08 m back along the second flight's inner side."""
    plan = _u_plan()
    plan["rail_limit"] = plan["rise_m"] + P.STAIR_RAIL_HEIGHT + P.STAIR_CAP_CLEARANCE     # it arrives through it
    plan["cap_z"] = plan["rise_m"] - 0.005
    opening = [(0.0, 0.673), (1.398, 0.673), (1.398, -0.477), (2.672, -0.477), (2.672, 1.627), (0.0, 1.627)]
    guard = [((0.0, 0.593), (1.318, 0.593))]
    plan["upper_wall_rects"] = list(plan["wall_rects"])                    # the stair core's walls go on up
    return plan, [opening], guard


def test_beside_the_floor_guard_above_the_handrail_stops_and_the_infill_closes_up_to_that_floor():
    plan, openings, guard = _under_floor_guard()
    guards = SR.plan_guards(plan, openings, guard)
    rise = plan["rise_m"]
    upper = [r for r in _chain(guards, "left") if r["flight"] == 1]
    ctx = SR._context(plan, openings, guard)
    for r in upper:                                            # never above that floor beside its guard
        for p in r["path"]:
            if SR.taken_over(ctx, p[:2], (1.0, 0.0)):
                assert p[2] <= rise - SR.CLEAR_M + 1e-6
    assert any("floor guard" in c["why"] for c in guards["cuts"])
    tops = [z for g in guards["infill"] if g["leg"] == 2 and g["side"] == "left" for z in
            ([g["z1"]] if g["type"] == "baluster" else [t[1] for t in g["top"]])]
    assert tops and max(tops) <= rise - SR.INFILL_CLEAR_M + 1e-6 and max(tops) > rise - 0.1     # up to the floor
    # the second flight holds its handrail on the wall (the outer side), continuous round the winders
    walls = [r for r in guards["rails"] if r["type"] == "wall"]
    assert len(walls) == 1 and walls[0]["side"] == "right" and len(walls[0]["returns"]) == 2
    zs = [p[2] for p in walls[0]["path"]]
    assert zs == sorted(zs) and zs[-1] > rise                  # it climbs with the stair, up beside the wall above
    assert not [f for f in SR.review(guards, plan, plan["wall_rects"], openings, guard)
                if f["rule"] in ("beside_guard", "cross", "no_handrail", "through_floor_above")]
    # the rails built before 28 Oct 2026: one straight rail per open flight side, up beside the floor guard
    old = SR.legacy_guards(plan, plan["rails"], "bars")
    rules = {f["rule"] for f in SR.review(old, plan, plan["wall_rects"], openings, guard)}
    assert {"beside_guard", "stops_short"} <= rules


def test_under_the_slab_and_under_a_shaft_cap_nothing_reaches_over_the_limit():
    plan, openings, guard = _under_floor_guard()
    guards = SR.plan_guards(plan, openings, guard)
    ctx = SR._context(plan, openings, guard)
    for part in SR.guard_parts(guards):
        for v in part["verts"]:
            cap, _why = SR.cap_at(ctx, v[:2], None, "infill")
            assert v[2] <= max(cap, ctx["top_open"]) + 0.03
    # a capped shaft (no floor above built): every rail, newel and baluster under the cap, the infill ends with
    # the rail (no baluster over the last newel)
    shaft = _u_plan(arrives=False)
    shaft["design"] = SR.stair_design({"family": "classic"})
    g = SR.plan_guards(shaft)
    limit = shaft["cap_z"] - P.STAIR_CAP_CLEARANCE
    assert max(v[2] for p in SR.guard_parts(g) for v in p["verts"]) <= limit + 1e-6
    fr = SR.flight_frame(shaft["flights"][1], shaft["riser_m"])
    railed = [SR._s_of(fr, p[:2]) for r in _chain(g, "left") if r["flight"] == 1 for p in r["path"]]
    end = max(railed) if railed else -1.0
    beyond = [b for b in g["infill"]
              if b["type"] == "baluster" and b["leg"] == 2 and SR._s_of(fr, b["at"]) > end + 0.05]
    assert not beyond


# --------------------------------------------------------------------------
# 4. Straight stairs, a dog-leg, an L: the wall rail, the newel on the divider, the corner
# --------------------------------------------------------------------------

def _straight(width=1.0, walls=True):
    piece = {"id": "s", "type": "stair", "footprint": {"center": [width / 2, 1.5], "size": [width, 3.0],
                                                       "rotation_deg": 0.0},
             "stair": {"flights": [{"start": [width / 2, 0.0], "end": [width / 2, 2.8], "width": width, "lines": 15}],
                       "landing": None, "direction": [0.0, 1.0]}}
    ws = [_wall("wl", (-0.1, -1.0), (-0.1, 4.0)), _wall("wr", (width + 0.1, -1.0), (width + 0.1, 4.0))] if walls else []
    return P.stair_plan(piece, 2.85, 2.70, walls=ws)


def test_straight_stairs_open_walled_and_wide():
    open_ = SR.plan_guards(_straight(walls=False))
    assert {r["side"] for r in open_["rails"]} == {"left", "right"} and len(open_["posts"]) == 4
    walled = SR.plan_guards(_straight())
    (rail,) = walled["rails"]
    assert rail["type"] == "wall" and rail["side"] == "right" and len(rail["returns"]) == 2
    for start, end in rail["returns"]:                          # back into the wall face
        assert end[0] == pytest.approx(1.0, abs=1e-6)
    assert sum(1 for p in SR.guard_parts(walled) if p["role"] == "bracket") >= 4
    wide = SR.plan_guards(_straight(width=1.2))
    assert sorted(r["side"] for r in wide["rails"] if r["type"] == "wall") == ["left", "right"]
    assert SR.review(wide, _straight(width=1.2), _straight(width=1.2)["wall_rects"]) == []


def test_a_dog_leg_stair_shares_one_newel_on_the_divider():
    flights = [{"start": [0.5, 0.0], "end": [0.5, 2.25], "width": 1.0, "lines": 10},
               {"start": [1.5, 0.0], "end": [1.5, 2.25], "width": 1.0, "lines": 10}]
    piece = {"id": "d", "type": "stair", "footprint": {"center": [1.0, 1.6], "size": [2.0, 3.25], "rotation_deg": 0},
             "stair": {"flights": flights, "landing": {"polygon": [[0, 2.25], [2, 2.25], [2, 3.25], [0, 3.25]]},
                       "direction": [0.0, 1.0], "turn": "U"}}
    walls = [_wall("w", (-0.1, -0.5), (-0.1, 3.45)), _wall("e", (2.1, -0.5), (2.1, 3.45)),
             _wall("n", (-0.2, 3.35), (2.2, 3.35))]
    plan = P.stair_plan(piece, 3.6, 3.4, walls=walls)
    g = SR.plan_guards(plan)
    inner = _chain(g, "right")
    assert [r["what"] for r in inner] == ["flight", "flight"] and inner[0]["posts"][1] == inner[1]["posts"][0]
    newel = next(p for p in g["posts"] if p["id"] == inner[0]["posts"][1])
    assert newel["at"][0] == pytest.approx(1.0) and newel["size"][1] > 2 * (SR.LINE_IN_M + inner[0]["r"])
    assert SR.review(g, plan, plan["wall_rects"]) == []


def _l_plan(w=1.0):
    """An L stair (flight 1 up +y, a quarter landing turned into winders, flight 2 along +x), ``w`` wide, walls on the
    outer side (west and north)."""
    x0, y1 = 1.0 - w / 2.0, 2.25 + w
    flights = [{"start": [1.0, 1.0], "end": [1.0, 2.25], "width": w, "lines": 6},
               {"start": [1.0 + w / 2.0, 2.25 + w / 2.0], "end": [2.25 + w / 2.0, 2.25 + w / 2.0], "width": w,
                "lines": 6}]
    piece = {"id": "L", "type": "stair", "footprint": {"center": [1.6, 2.1], "size": [2.5, 2.5], "rotation_deg": 0},
             "stair": {"flights": flights, "landing": {"polygon": [[x0, 2.25], [x0 + w, 2.25], [x0 + w, y1],
                                                                   [x0, y1]]},
                       "direction": [0.0, 1.0], "turn": "L", "winders": "auto"}}
    walls = [_wall("w1", (x0 - 0.1, 0.0), (x0 - 0.1, y1 + 0.15)), _wall("w2", (x0 - 0.2, y1 + 0.1), (3.5, y1 + 0.1))]
    return P.stair_plan(piece, 3.0, 2.85, walls=walls)


def test_an_l_stair_turns_its_balustrade_at_the_corner_and_its_wall_rail_round_the_winders():
    plan = _l_plan()
    # the winders are in the stair's ceiling opening (they climb towards the ceiling)
    from shapely.geometry import Point, Polygon
    assert Polygon(plan["void_raw"][0]).contains(Point(1.0, 2.75))
    plan["design"] = SR.stair_design({"family": "classic"})
    g = SR.plan_guards(plan)
    inner = _chain(g, "right")
    assert inner[0]["posts"][1] == inner[1]["posts"][0]               # one newel at the inner corner
    corner = next(p for p in g["posts"] if p["id"] == inner[0]["posts"][1])
    assert corner["at"] == pytest.approx((1.5 - SR.LINE_IN_M, 2.25 + SR.LINE_IN_M))
    assert {b["shape"] for b in g["infill"]} == {"turned"}
    # a wide L stair: a wall rail too, climbing round the winders on the outer walls without a step
    wide = _l_plan(1.2)
    g2 = SR.plan_guards(wide)
    wall = [r for r in g2["rails"] if r["type"] == "wall"]
    assert len(wall) == 1 and wall[0]["side"] == "left" and len(wall[0]["returns"]) == 2
    zs = [p[2] for p in wall[0]["path"]]
    assert zs == sorted(zs) and len(zs) > 4
    pitch = max(SR.flight_frame(f, wide["riser_m"])["k"] for f in wide["flights"])
    for a, b in zip(wall[0]["path"], wall[0]["path"][1:]):    # no step: never steeper than the flights (and a bit)
        assert b[2] - a[2] <= pitch * SR.G.distance(a[:2], b[:2]) * 1.25 + 0.02
    assert not [f for f in SR.review(g2, wide, wide["wall_rects"]) if f["rule"] != "no_handrail"]


# --------------------------------------------------------------------------
# 5. A lighter structure in the light styles; no spandrel panel over a floor opening
# --------------------------------------------------------------------------

def test_light_styles_get_a_thin_soffit_and_strings_and_the_panels_close_up_to_it():
    plan = _u_plan()
    f = plan["flights"][0]
    k, solid = SR.flight_waist(plan, f)
    assert solid == pytest.approx(P.STAIR_WAIST_M * math.sqrt(1 + k * k))
    plan["design"] = SR.stair_design({"family": "modern"})
    _k, plate = SR.flight_waist(plan, f)
    plan2 = dict(plan, design=SR.stair_design({"family": "scandinavian"}))
    _k, stringer = SR.flight_waist(plan2, f)
    assert plate < stringer < solid and plate == pytest.approx(SR.PLATE_M * math.sqrt(1 + k * k))
    parts = P.stair_parts(plan)
    step = [p for p in parts if p["role"] == "step" and p["flight"] == 0]
    deepest = min(min(v[2] - (f["base_z"] + SR._s_of(SR.flight_frame(f, plan["riser_m"]), v[:2]) * k)
                      for v in p["verts"] if v[2] > 1e-6) for p in step[1:])
    assert deepest == pytest.approx(-plate, abs=1e-6)                     # the soffit: the plate under the steps
    strings = [p for p in parts if p["role"] == "string"]
    assert strings and all(p["key"] == "steel" for p in strings)
    frames = {x["index"]: SR.flight_frame(x, plan["riser_m"]) for x in plan["flights"]}
    for s in SR.plan_guards(plan)["strings"]:
        if s["flight"] is not None:                             # the string's top over the nosing line
            fr = frames[s["flight"]]
            top = max(p[1] for p in s["profile"] if p[0] < 0.01)
            assert top == pytest.approx(SR.nose(fr, 0.0) + SR.STRING_UP_M, abs=1e-4)
    # the spandrel panels under the low part close up to the thin soffit, as built
    under = SA.under_stair(plan, U_WALLS)
    flight_panels = [p for p in under["panels"] if p["of"] == "flight 1" and p["zq"] > 0]
    for p in flight_panels:
        s = SR._s_of(frames[0], p["q"])
        assert p["zq"] == pytest.approx(max(0.0, frames[0]["base"] + s * k - plate), abs=1e-3)


def test_over_a_floor_opening_no_panel_stands_and_light_winders_are_thin():
    plan = _u_plan()
    plan["design"] = SR.stair_design({"family": "modern"})
    void = [(-0.1, -0.6), (2.8, -0.6), (2.8, 1.75), (-0.1, 1.75)]           # the stair over the stairwell below
    closed = SA.under_stair(plan, U_WALLS)
    free = SA.under_stair(plan, U_WALLS, [void])
    assert closed["panels"] and not free["panels"] and not free["posts"]
    plan["floor_voids"] = [void]
    assert SR.light_winders(plan, [void]) and not SR.light_winders(dict(plan, design=SR.stair_design(None)), [void])
    parts = P.stair_parts(plan)
    winders = [p for p in parts if p["role"] == "winder"]
    assert winders and all(max(v[2] for v in p["verts"]) - min(v[2] for v in p["verts"]) ==
                           pytest.approx(SR.WINDER_PLATE_M) for p in winders)
    risers = [p for p in parts if p["role"] == "riser" and p.get("winder") is not None]
    assert len(risers) >= len(winders) - 2                       # a riser plate on every shared edge


# --------------------------------------------------------------------------
# 6. The model review's M18 and its kind for Argus
# --------------------------------------------------------------------------

def _house():
    from test_stair_access_20261027 import _house as house
    b = house()
    SA.fix_arrivals(b)
    return b


def test_m15_finds_the_old_per_flight_rails_and_passes_the_new_balustrade():
    b = _house()
    level = b["levels"][0]
    walls = [w for w in b["walls"] if w["level_id"] == "L0"]
    item = next(i for i in SH.plan_stairs(b, level, slab_void=True) if i["plan"])
    plan = SH.stair_build_plan(item["plan"], walls)
    old = {"objects": [{"element_id": "st0", "kind": "furniture", "type": "stair",
                        "stair": {"rails": plan["rails"], "structure": "solid"}}]}
    found, n = MR.stair_rails_review(b, old)
    assert n == 1 and found and all(f["check"] == "M18" for f in found)
    rules = {f["metrics"]["rule"] for f in found}
    assert "stops_short" in rules and all(f["metrics"]["legacy"] for f in found)
    f = next(x for x in found if x["metrics"]["rule"] == "stops_short")
    assert K.kind_of(f) == "no_sense" and CS.cause_of(f) == "stair_rails" and CS.REPORT_TO["stair_rails"] == "build"
    assert "stair_rails" in CS.NO_TOOL_REASON and "M18" in MR.CHECKS and K.CHECK_KIND["M18"] == "no_sense"
    # as built now
    openings = SH.slab_openings_above(b, level)
    guards = SH.stair_guard_plan(b, level, plan, {"family": "modern"}, [], openings)
    new = {"objects": [{"element_id": "st0", "kind": "furniture", "type": "stair",
                        "stair": {"rails": plan["rails"], "structure": SR.structure_of(plan),
                                  "guards": SR.summary(guards)}}]}
    assert MR.stair_rails_review(b, new) == ([], 1)
    rec = MR.review(b, old, prep={})
    assert rec["checks"]["M18"]["checked"] == 1 and rec["checks"]["M18"]["failed"] == len(found)
    assert any(a["kind"] == "stair_balustrade" for a in plan["assumed"])
    assert any(a["kind"] == "stair_structure" and "folded-plate" in a["value"] for a in plan["assumed"])
