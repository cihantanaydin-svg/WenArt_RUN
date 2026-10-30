"""See-through wardrobes in every bedroom, up to the ceiling, with glass sections (30 Oct 2026, lesson UL182, user on
real04 run 20261030-112241-full: "These kind of wardrobes can be used in other rooms also, it can go all the way to the
ceiling it can have glass sections I did gave an inspiration before"). CPU, pure.

The rules are general (``wenart/blender/wardrobe_fronts.py``, ``modules.py``, ``room_schemes.py``): in the families
that use a see-through front every bedroom's widest run gets one, each bedroom its own (the master the family's,
the others by their room scheme, a front no other bedroom has, a twin its partner's); every see-through run goes up to
the ceiling with a top box (the tallest frames when no height is drawn; a window beside it keeps its height, a ceiling
light over it slides off); doors of slats and glass in turn, smoked or reeded glass; the period families keep closed
fronts.
"""
from __future__ import annotations

import copy

from wenart.blender import modules as MOD
from wenart.blender import parametric as P
from wenart.blender import wardrobe_fronts as WF
from wenart.furniture import room_schemes as RS

MODERN = {"family": "modern"}


def _bed(rid, x0, label="Yatak", bundle=None, copied=None):
    room = {"id": rid, "level_id": "L0", "room_type": "bedroom", "label": label,
            "polygon": [[x0, 0], [x0 + 4, 0], [x0 + 4, 4], [x0, 4]]}
    if bundle:
        room["scheme"] = {"kind": "bedroom", "bundle": bundle, "copied_from": copied}
    return room


def _robe(fid, rid, x, width=1.5, height=None):
    return {"id": fid, "type": "wardrobe", "level_id": "L0", "room_id": rid, "front_deg": 90.0, "height": height,
            "footprint": {"center": [x, 0.3], "size": [width, 0.6], "rotation_deg": 0.0}}


def _house():
    rooms = [_bed("r_m", 0, "Master bedroom", "deep"), _bed("r_a", 4, bundle="slats"),
             _bed("r_b", 8, bundle="limewash"), _bed("r_c", 12, bundle="slats", copied="r_a")]
    robes = [_robe("f_m", "r_m", 2.0, 2.5), _robe("f_a", "r_a", 6.0), _robe("f_b", "r_b", 10.0),
             _robe("f_c", "r_c", 14.0)]
    return {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.8}], "rooms": rooms, "walls": [],
            "openings": [], "furniture": robes, "decor": []}


def test_every_bedroom_gets_its_own_see_through_front_and_period_homes_keep_closed_ones():
    b = _house()
    got = WF.plan(b, MODERN)
    kinds = {pid: rec["kind"] for pid, rec in got.items()}
    assert kinds["f_m"] == WF.FRONTS["modern"] == WF.BEDROOM_FRONTS["modern"][0]          # the master: the family's
    assert kinds["f_b"] == "reeded_glass"                                                  # its scheme's (limewash)
    assert kinds["f_a"] not in (kinds["f_m"], kinds["f_b"])                                 # slats taken: another
    assert kinds["f_c"] == kinds["f_a"] and "twin" in got["f_c"]["reason"]                 # a twin: its partner's
    assert all(k in WF.FRONT_KINDS for k in kinds.values()) and all("UL182" in r["reason"] for r in got.values())
    for fam in ("classic", "rustic", "mediterranean"):
        assert WF.plan(b, {"family": fam}) == {}
    # every family's own front first; the scheme's bundles name a front the build knows (= room_schemes)
    for fam, opts in WF.BEDROOM_FRONTS.items():
        assert opts[0] == WF.FRONTS[fam] and set(opts) <= set(WF.FRONT_KINDS)
    for bundle, spec in RS.POOLS["bedroom"].items():
        assert spec["wardrobe"] == WF.SCHEME_FRONTS[bundle]
        assert RS.resolve("bedroom", bundle, "warm greige", "modern")["wardrobe_front"] == spec["wardrobe"]
    assert "wardrobe_front" in RS.COMPACT_KEYS
    # the architect's answer wins, closed included
    b["rooms"][2]["wardrobe_fronts"] = {"kind": "closed", "by": "user"}
    assert "f_b" not in WF.plan(b, MODERN)


def test_the_run_goes_up_to_the_ceiling_with_a_top_box_and_full_height_doors():
    b = _house()
    chosen, assumed = WF.apply(b, MODERN)
    for f in b["furniture"]:
        st = f["see_through"]
        assert st["ceiling_m"] == 2.8 - WF.CEILING_GAP_M
        plan = MOD.module_plan(f)
        assert plan["height_m"] == st["ceiling_m"] and plan["carcass_m"] == 2.44     # the tallest PAX frames
        assert f["asset"]["bbox_m"][2] == plan["height_m"]
        parts = MOD.module_parts(plan)
        roles = {p["role"] for p in parts}
        assert {"box", "led", "track", "panel_frame", "garment"} <= roles
        top = max(v[2] for p in parts for v in p["verts"])
        assert plan["height_m"] - 0.01 <= top <= plan["height_m"] + 1e-6              # up to the ceiling, not over
        # the bay lights stay under the frames' top (the carcass), the doors reach the top box
        assert all(li["center"][2] < plan["carcass_m"] for li in MOD.bay_lights(plan))
        assert max(v[2] for p in parts if p["role"] == "panel_frame" for v in p["verts"]) > plan["carcass_m"] + 0.3
        keys = {p["key"] for p in parts if not p["key"].startswith(("cloth:", "lit:"))}
        assert keys <= set(P.MATERIAL_KEYS)
    assert {a["kind"] for a in assumed} == {"see_through_front"}
    # a drawn height is kept (the top box closes the rest); a window beside the run keeps its height
    b2 = _house()
    b2["furniture"][1]["height"] = 2.1
    b2["openings"] = [{"id": "w1", "type": "window", "level_id": "L0", "center": [10.0, 0.0], "width": 1.2}]
    WF.apply(b2, MODERN)
    a2 = MOD.module_plan(b2["furniture"][1])
    assert a2["carcass_m"] == 2.1 and a2["height_m"] == 2.8 - WF.CEILING_GAP_M
    assert b2["furniture"][2]["see_through"]["ceiling_m"] is None
    assert MOD.module_plan(b2["furniture"][2]).get("carcass_m") is None


def test_a_ceiling_light_over_the_run_slides_off_it():
    b = _house()
    b["decor"] = [{"id": "trk", "type": "ceiling_light", "fixture": "track", "level_id": "L0", "room_id": "r_a",
                   "center": [6.0, 0.5, 2.68], "size": [1.0, 0.05, 0.12], "rotation_deg": 0.0}]
    _chosen, assumed = WF.apply(b, MODERN)
    li = b["decor"][0]
    assert b["furniture"][1]["see_through"]["ceiling_m"] is not None
    assert li["center"][1] >= 0.6 + WF.LIGHT_CLEAR_M - 1e-6 and li["center"][2] == 2.68        # off the run's front
    assert any(a["object"] == "trk" and a["field"] == "center" for a in assumed)


def test_glass_sections_and_reeded_glass():
    for kind, glass in (("slats_glass", "smoked_glass"), ("slats_glass", "reeded_glass"), ("reeded_glass", None)):
        piece = _robe("f", "r", 0.0, 2.5, 2.3)
        piece["see_through"] = {"kind": kind, **({"glass": glass} if glass else {})}
        plan = MOD.module_plan(piece)
        assert plan["see_through"]["kind"] == kind and plan["see_through"]["panels"] >= 2
        parts = MOD.module_parts(plan)
        panes = [p for p in parts if p["role"] == "glass"]
        if kind == "slats_glass":
            n = plan["see_through"]["panels"]
            assert [MOD.panel_kind(plan["see_through"], i) for i in range(n)][:2] == ["slats", glass]
            assert any(p["role"] == "slat" for p in parts) and panes and all(p["key"] == glass for p in panes)
        else:
            assert not any(p["role"] == "slat" for p in parts) and all(p["key"] == "reeded_glass" for p in panes)
        assert any(p["role"] == "reed" for p in parts) == (glass == "reeded_glass" or kind == "reeded_glass")
        x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
        assert x0 >= -1.25 - 0.008 and x1 <= 1.25 + 0.008 and z1 <= 2.3 + 1e-6
    assert WF.is_see_through({"see_through": {"kind": "reeded_glass"}})
    assert MOD.see_through_kind({"type": "wardrobe", "see_through": {"kind": "slats_glass"}}) == "slats_glass"


def test_a_tall_room_or_a_low_ceiling_gets_no_top_box():
    b = _house()
    b["levels"][0]["ceiling_height"] = 4.5
    assert WF.to_ceiling(b, b["furniture"][1])[0] is None
    b["levels"][0]["ceiling_height"] = 2.45
    piece = copy.deepcopy(b["furniture"][1])
    piece["height"] = 2.44
    assert WF.to_ceiling(b, piece)[0] is None
