"""Built-in wardrobes: used sometimes, only wall to wall or from a wall, and a much better look (31 Oct 2026; user on
real04 run 20261030-181158-full, an L0 bedroom with a desk: "Not every room needs this built in wardrobe, we can use it
sometime but it needs to be wall to wall or from wall to middle, also you can make this a lot better with the better
material and details"). CPU, pure.

The rules are general (``wenart/blender/wardrobe_fronts.py``, ``modules.py``, ``materials.py``, ``finishes.py``):
(1) a house gets at most ``BUILT_IN_ROOMS_MAX`` rooms with a built-in see-through run (the walk-ins, then the master
with its twin, then the bedrooms whose scheme asks, the best fit first; a twin pair whole or not at all); every other
wardrobe keeps the fit's free-standing model, each skip logged. (2) A built-in stands against a solid wall at one end
at least; a gap of at most 0.5 m to a side wall is closed when the strip, the floor before it and the doors' approaches
are free and no opening is behind it (``drawn_footprint`` kept, ``adjusted_by_ai``); never with keep sizes. (3) Its
look: the shell in the style's veneer or the family's matte lacquer, slim metal frames with a glazing step and a bead,
a grip channel, end panels to the floor, a fascia to the ceiling, shadow gaps, a recessed plinth, wood slats with real
gaps, tinted glass that lets half the light through, rounded flutes on reeded glass, a subtler LED.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from wenart.blender import furniture as F
from wenart.blender import modules as MOD
from wenart.blender import parametric as P
from wenart.blender import wardrobe_contents as WC
from wenart.blender import wardrobe_fronts as WF
from wenart.style import colours as C
from wenart.style import vocabulary as V

MODERN = {"family": "modern"}
REAL04 = Path("/home/user/WenArt_RUN/results/baseline/latest/furniture/real04/building_final.json")


def _bed(rid, x0, label="Yatak", bundle=None, copied=None, w=4.0):
    room = {"id": rid, "level_id": "L0", "room_type": "bedroom", "label": label,
            "polygon": [[x0, 0], [x0 + w, 0], [x0 + w, 4], [x0, 4]]}
    if bundle:
        room["scheme"] = {"kind": "bedroom", "bundle": bundle, "copied_from": copied}
    return room


def _robe(fid, rid, x0, width=1.5, gap=0.0, asset=None):
    """A wardrobe on the south wall of a room starting at ``x0``, ``gap`` off its west wall, front north."""
    f = {"id": fid, "type": "wardrobe", "level_id": "L0", "room_id": rid, "front_deg": 90.0, "height": None,
         "footprint": {"center": [round(x0 + gap + width / 2.0, 4), 0.3], "size": [width, 0.6], "rotation_deg": 0.0}}
    if asset:
        f["asset"] = {"library": "abo", "asset_id": asset, "method": "library"}
    return f


def _building(rooms, robes, walls=(), openings=(), decor=()):
    return {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.8}], "rooms": list(rooms),
            "walls": list(walls), "openings": list(openings), "furniture": list(robes), "decor": list(decor)}


# ------------------------------------------------------------------------------- (1) some rooms, not every bedroom

def test_a_house_gets_built_ins_in_a_few_rooms_and_free_standing_wardrobes_elsewhere():
    rooms = [_bed("r_m", 0, "Master bedroom", "deep"), _bed("r_m2", 4, "Master bedroom", "deep", copied="r_m"),
             _bed("r_a", 8, bundle="panel"), _bed("r_b", 12, bundle="limewash"), _bed("r_c", 16, bundle="panel")]
    robes = [_robe("f_m", "r_m", 0, 2.5), _robe("f_m2", "r_m2", 4, 2.5), _robe("f_a", "r_a", 8, asset="abo_a"),
             _robe("f_b", "r_b", 12, asset="abo_b"), _robe("f_c", "r_c", 16, asset="abo_c")]
    b = _building(rooms, robes)
    notes: list = []
    got = WF.plan(b, MODERN, notes)
    assert WF.BUILT_IN_ROOMS_MAX == 2
    # the master and its twin (a mirrored pair) take the house's two rooms; the bedrooms whose schemes ask stay free
    assert set(got) == {"f_m", "f_m2"} and {got[k]["kind"] for k in got} == {WF.FRONTS["modern"]}
    skipped = {n["id"]: n["reason"] for n in notes}
    assert set(skipped) == {"f_a", "f_b", "f_c"} and all("free-standing" in r for r in skipped.values())
    chosen, assumed = WF.apply(b, MODERN)
    for f in b["furniture"]:
        if f["id"] in ("f_a", "f_b", "f_c"):                 # the fit's free-standing library model stays
            assert "see_through" not in f and f["asset"]["method"] == "library"
        else:
            assert f["asset"]["method"] == "module" and f["see_through"]["kind"] == "slats"
    logged = [a for a in assumed if a["kind"] == "built_in_wardrobe" and a["field"] == "built_in"]
    assert {a["parent"] for a in logged} == {"f_a", "f_b", "f_c"} and all(a["value"] == "free-standing" for a in logged)


def test_the_walk_in_and_the_master_first_then_the_best_fit_and_twins_whole():
    dressing = {"id": "r_dr", "level_id": "L0", "room_type": "storage", "label": "Dressing",
                "polygon": [[20, 0], [22.4, 0], [22.4, 2.45], [20, 2.45]]}
    runs = [{"id": "f_d1", "type": "wardrobe", "level_id": "L0", "room_id": "r_dr", "front_deg": 0.0,
             "footprint": {"center": [20.3, 1.225], "size": [2.45, 0.6], "rotation_deg": 90.0}},
            {"id": "f_d2", "type": "wardrobe", "level_id": "L0", "room_id": "r_dr", "front_deg": 180.0,
             "footprint": {"center": [22.1, 1.225], "size": [2.45, 0.6], "rotation_deg": 90.0}}]
    rooms = [_bed("r_m", 0, "Master bedroom", "deep"), _bed("r_a", 4, bundle="panel"), dressing]
    b = _building(rooms, [_robe("f_m", "r_m", 0, 2.5), _robe("f_a", "r_a", 4)] + runs)
    got = WF.plan(b, MODERN)
    assert set(got) == {"f_d1", "f_d2", "f_m"}                    # the walk-in (one room) and the master: 2 rooms
    assert got["f_d1"]["walk_in"] and not got["f_m"]["walk_in"]
    # no master: a twin pair that asks would make 3 rooms with the walk-in; the single room that asks takes the slot
    rooms = [_bed("r_a", 0, bundle="panel"), _bed("r_c", 4, bundle="panel", copied="r_a"),
             _bed("r_b", 8, bundle="limewash"), dressing]
    b = _building(rooms, [_robe("f_a", "r_a", 0), _robe("f_c", "r_c", 4), _robe("f_b", "r_b", 8)] + runs)
    notes: list = []
    got = WF.plan(b, MODERN, notes)
    assert set(got) == {"f_d1", "f_d2", "f_b"} and {n["id"] for n in notes} == {"f_a", "f_c"}
    # the best fit first: a run from wall to wall wins over a run from one wall, the larger room over a smaller one
    rooms = [_bed("r_a", 0, bundle="panel"), _bed("r_b", 4, bundle="limewash"), _bed("r_x", 8, bundle="panel")]
    b = _building(rooms, [_robe("f_a", "r_a", 0, 1.5), _robe("f_b", "r_b", 4, 4.0), _robe("f_x", "r_x", 8, 2.0)])
    got = WF.plan(b, MODERN)
    assert set(got) == {"f_b", "f_a"} and got["f_b"]["fit"]["wall_to_wall"]
    rooms[2] = _bed("r_x", 8, bundle="panel", w=5.0)                 # the larger room beats r_a's equal fit
    got = WF.plan(_building(rooms, [_robe("f_a", "r_a", 0, 1.5), _robe("f_b", "r_b", 4, 4.0),
                                    _robe("f_x", "r_x", 8, 2.0)]), MODERN)
    assert set(got) == {"f_b", "f_x"}


def test_a_scheme_recorded_before_ul207_reads_its_bundles_front_now():
    room = _bed("r_s", 0, bundle="slats")
    room["scheme"]["wardrobe_front"] = "slats"              # recorded before UL207 (real04's stored building)
    kind, why = WF.bedroom_front(room, MODERN)
    assert kind is None and "closed" in why
    room["scheme"]["bundle"] = "panel"
    assert WF.bedroom_front(room, MODERN)[0] == WF.SCHEME_FRONTS["panel"]


# --------------------------------------------------------------------------------------- (2) the wall rule

def test_a_built_in_stands_against_a_wall_and_never_floats_mid_wall():
    room = _bed("r_a", 0, bundle="panel")
    against = _robe("f", "r_a", 0, 1.5)
    ends = WF.run_ends(_building([room], [against]), against, room)
    assert sorted(e["touch"] for e in ends) == [False, True] and min(e["gap_m"] for e in ends) == 0.0
    fit = WF.built_in_fit(_building([room], [against]), against, room)
    assert fit["ok"] and not fit["wall_to_wall"] and fit["footprint"] is None and "one end" in fit["why"]
    mid = _robe("f", "r_a", 0, 1.5, gap=1.2)
    fit = WF.built_in_fit(_building([room], [mid]), mid, room)
    assert not fit["ok"] and "never floats mid-wall" in fit["why"]
    b = _building([room], [mid])
    chosen, assumed = WF.apply(b, MODERN)
    assert chosen == {} and "see_through" not in b["furniture"][0]                      # free-standing
    assert any(a["kind"] == "built_in_wardrobe" and "never floats" in a["reason"] for a in assumed)
    # the walls of the level count as well as the outline (a wall stub beside the run)
    stub = {"id": "w_stub", "level_id": "L0", "start": [1.7, 0.0], "end": [1.7, 0.7], "thickness": 0.1}
    near = _robe("f", "r_a", 0, 1.5, gap=0.15)                                          # ends at x = 1.65
    ends = WF.run_ends(_building([room], [near], walls=[stub]), near, room)
    assert any(e["touch"] and e["wall"] == "w_stub" for e in ends)
    # an end at a doorway does not stand against a wall
    wall = {"id": "w_w", "level_id": "L0", "start": [-0.05, 0.0], "end": [-0.05, 4.0], "thickness": 0.1}
    door = {"id": "d1", "type": "door", "level_id": "L0", "wall_id": "w_w", "center": [-0.05, 0.4], "width": 0.9}
    ends = WF.run_ends(_building([room], [against], walls=[wall], openings=[door]), against, room)
    west = next(e for e in ends if e["gap_m"] == 0.0)
    assert west["passage"] == "d1" and not west["touch"]


def test_a_small_gap_to_the_wall_closes_and_a_large_one_leaves_it_free_standing():
    room = _bed("r_m", 0, "Master bedroom", "deep")
    near = _robe("f", "r_m", 0, 2.0, gap=0.3, asset="abo_x")
    b = _building([room], [near])
    chosen, assumed = WF.apply(b, MODERN)
    f = b["furniture"][0]
    assert set(chosen) == {"f"} and f["see_through"]["kind"] == "slats"
    assert f["drawn_footprint"]["size"] == [2.0, 0.6] and f["drawn_footprint"]["center"] == [1.3, 0.3]
    grown = 0.3 - WF.EXTEND_CLEAR_M
    assert f["footprint"]["size"][0] == pytest.approx(2.0 + grown)
    assert f["footprint"]["center"][0] == pytest.approx(1.3 - grown / 2.0)               # the west end at the wall
    assert f["adjusted_by_ai"]["by"] == "code" and f["adjusted_by_ai"]["rule"].startswith("built-in wardrobe")
    assert "drawn_footprint kept" in f["adjusted_by_ai"]["reason"]
    assert any(a["kind"] == "built_in_wardrobe" and a["field"] == "footprint" for a in assumed)
    assert f["asset"]["bbox_m"][0] == pytest.approx(2.0 + grown) and MOD.module_plan(f)["footprint_m"][0] == \
        pytest.approx(2.0 + grown)
    # both ends near a wall: from wall to wall
    both = _robe("f", "r_m", 0, 3.4, gap=0.25)
    fit = WF.built_in_fit(_building([room], [both]), both, room)
    assert fit["ok"] and fit["wall_to_wall"] and len(fit["extend"]) == 2
    assert fit["footprint"]["size"][0] == pytest.approx(4.0 - 2 * WF.EXTEND_CLEAR_M)
    # more than EXTEND_MAX_M: no change, free-standing
    far = _robe("f", "r_m", 0, 2.0, gap=0.6, asset="abo_x")
    b = _building([room], [far])
    assert WF.apply(b, MODERN)[0] == {} and b["furniture"][0]["footprint"]["center"] == [1.6, 0.3]
    assert b["furniture"][0]["asset"]["method"] == "library" and "drawn_footprint" not in b["furniture"][0]


def test_the_gap_closes_only_where_the_strip_its_front_and_the_wall_behind_are_free():
    room = _bed("r_m", 0, "Master bedroom", "deep")
    near = _robe("f", "r_m", 0, 2.0, gap=0.3)

    def fit(**kw):
        return WF.built_in_fit(_building([room], [near] + kw.pop("pieces", []), **kw), near, room)

    plant = {"id": "dec_plant", "type": "plant", "level_id": "L0", "center": [0.15, 0.3], "size": [0.25, 0.25]}
    assert not fit(decor=[plant])["ok"]                                       # a floor plant in the strip
    desk = {"id": "f_desk", "type": "desk", "level_id": "L0", "room_id": "r_m", "front_deg": 0.0,
            "footprint": {"center": [0.3, 1.2], "size": [1.2, 0.6], "rotation_deg": 90.0}}
    got = fit(pieces=[desk])                                                  # the desk 0.0 m before its doors
    assert not got["ok"] and "open onto f_desk" in got["ends"][0].get("blocked", "") + got["ends"][1].get("blocked", "")
    win = {"id": "w1", "type": "window", "level_id": "L0", "center": [0.2, 0.0], "width": 0.6}
    got = fit(openings=[win])
    assert not got["ok"] and any("w1" in (e.get("blocked") or "") for e in got["ends"])
    wall = {"id": "w_w", "level_id": "L0", "start": [-0.05, 0.0], "end": [-0.05, 4.0], "thickness": 0.1}
    door = {"id": "d1", "type": "door", "level_id": "L0", "wall_id": "w_w", "center": [-0.05, 0.9], "width": 0.9}
    got = fit(walls=[wall], openings=[door])                                # the door's approach beside the wall
    assert not got["ok"] and any("d1" in (e.get("blocked") or "") for e in got["ends"])
    assert fit()["ok"]
    # with keep sizes the drawn size stays: no gap closes, the run stays free-standing
    kept = _building([room], [near])
    kept["project"] = {"brief": {"furnished_rooms_keep_size": True}}
    assert WF.sizes_kept(kept)[0] and WF.apply(kept, MODERN)[0] == {}
    keep = _building([room], [near])
    keep["project"] = {"brief": {"furnished_rooms": "keep"}}
    assert WF.plan(keep, MODERN) == {}
    named = _building([room], [near])
    named["project"] = {"brief": {"furnished_rooms_keep": ["Master bedroom"]}}
    assert WF.room_sizes_kept(named, room) and WF.plan(named, MODERN) == {}


@pytest.mark.skipif(not REAL04.is_file(), reason=f"{REAL04} not here")
def test_real04_built_ins_only_in_the_two_masters_and_the_desk_room_keeps_its_wardrobe():
    b = json.loads(REAL04.read_text(encoding="utf-8"))
    notes: list = []
    got = WF.plan(b, MODERN, notes)
    # the mirrored pair of master bedrooms (their runs from the corner, 3.11 m) and no other room of the house
    assert set(got) == {"f_L0_023", "f_L0_024"} and all(not v["walk_in"] for v in got.values())
    assert {n["id"] for n in notes} >= {"f_L0_010", "f_L0_012"}
    rooms = {r["id"]: r for r in b["rooms"]}
    robe = next(f for f in b["furniture"] if f["id"] == "f_L0_009")             # the reviewed room with a desk
    fit = WF.built_in_fit(b, robe, rooms[robe["room_id"]])
    assert not fit["ok"] and "never floats mid-wall" in fit["why"]
    assert any("f_L0_029" in (e.get("blocked") or "") for e in fit["ends"])     # the desk before the closed gap


# ------------------------------------------------------------------------------------------------- (3) the look

def _piece(kind, fam="modern", glass=None, style=None):
    style = style or {"family": fam}
    st = {"kind": kind, "ceiling_m": 2.795, "look": WF.built_in_look(style)}
    if glass:
        st["glass"] = glass
    return {"id": "f_robe", "type": "wardrobe", "height": None, "see_through": st,
            "footprint": {"center": [0, 0], "size": [2.5, 0.6], "rotation_deg": 0.0}}


def test_the_looks_shell_metal_and_glass_by_family():
    materials = {**V.MATERIALS, **V.FURNITURE_MATERIALS}
    for fam, row in WF.BUILT_IN_LOOKS.items():
        look = WF.built_in_look({"family": fam})
        assert look["shell"] in ("veneer", "lacquer") and look["metal"] in materials and look["wood"] in materials
        assert look["glass"] in P.MATERIAL_KEYS and look["glass"] in ("bronze_glass", "smoked_glass")
        assert materials[look["metal"]].get("metallic", 0.0) >= 0.8                       # anodised metal profiles
        if look["shell"] == "lacquer":
            assert look["shell_slug"] == WF.LACQUER_SLUG and look["colour"] in C.COLOURS
        else:
            assert look["shell_slug"] == look["wood"] and look["wood"].startswith("wood_veneer_")
    # the style's furniture veneer wins (the room's pieces fit together); a period family takes the default row
    look = WF.built_in_look({"family": "modern", "furniture": {"wood": "wood_veneer_walnut"}})
    assert look["wood"] == look["shell_slug"] == "wood_veneer_walnut"
    assert WF.built_in_look({"family": "classic"})["metal"] == WF.BUILT_IN_LOOKS[WF.BUILT_IN_LOOK_DEFAULT]["metal"]
    lacquer = V.FURNITURE_MATERIALS[WF.LACQUER_SLUG]
    assert lacquer["kind"] == "painted" and lacquer["colourable"] and lacquer.get("asset") is None
    assert 0.45 <= lacquer["roughness"] <= 0.7                                            # matte, not gloss
    # the build lays the look over the design: the shell on the fronts, the veneer inside, the metal on the profiles
    over = WF.look_overrides(_piece("slats_glass", "minimal", "smoked_glass"))
    assert over["front"] == {"slug": WF.LACQUER_SLUG, "asset": None, "colour": "off white"}
    assert over["handle"]["slug"] == "steel_brushed" and over["wood"]["slug"].startswith("wood_veneer_")
    assert WF.look_overrides({"see_through": {"kind": "slats"}}) == {}                  # no look: the style's keys
    assert "bronze_glass" in F.style_material_keys({})[0] and "bronze_glass" in P.MATERIAL_KEYS
    assert not any("black" in text for text in WF.FRONT_WHAT.values())


def test_the_built_in_has_end_panels_a_fascia_shadow_gaps_and_a_recessed_plinth():
    piece = _piece("slats_glass", glass="smoked_glass")
    plan = MOD.module_plan(piece)
    parts = MOD.module_parts(plan)
    k = MOD.SEE_THROUGH
    w, d, top = 2.5, 0.6, plan["height_m"]
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    assert x0 >= -w / 2 - 1e-6 and x1 <= w / 2 + 1e-6 and y0 >= -d / 2 - 1e-6 and y1 <= d / 2 + 1e-6
    assert z0 >= -1e-9 and z1 <= top + 1e-6

    def box(p):
        return P.parts_bbox([p])

    ends = [p for p in parts if p["role"] == "end_panel"]
    assert len(ends) == 2 and all(p["key"] == "front" and box(p)[2] == 0.0 and box(p)[5] == pytest.approx(top)
                                  for p in ends)                                 # the shell, floor to ceiling
    e = MOD.end_panel_t(plan)
    plinth = next(p for p in parts if p["role"] == "plinth")
    assert plinth["key"] == "dark" and box(plinth)[1] == pytest.approx(-d / 2 + k["plinth_recess_m"])
    fascia = next(p for p in parts if p["role"] == "fascia")
    assert fascia["key"] == "front" and box(fascia)[5] == pytest.approx(top) and box(fascia)[1] == pytest.approx(-d / 2)
    frames = [p for p in parts if p["role"] == "panel_frame"]
    assert frames and all(p["key"] == "handle" for p in frames)                  # the look's metal, not black lacquer
    lo = min(box(p)[0] for p in frames)
    hi = max(box(p)[3] for p in frames)
    assert lo == pytest.approx(-w / 2 + e + k["shadow_m"]) and hi == pytest.approx(w / 2 - e - k["shadow_m"])
    assert max(box(p)[5] for p in frames) == pytest.approx(top - k["fascia_m"][0] - k["shadow_m"])
    assert min(box(p)[2] for p in frames) == pytest.approx(MOD.WARDROBE_PLINTH_M + k["shadow_m"])
    # slim profiles with a step: full-depth members and the thinner strips of the glazing channel
    depths = {round(box(p)[4] - box(p)[1], 4) for p in frames}
    assert {k["panel_t"], round(k["panel_t"] - 2 * k["rebate_m"][1], 4)} <= depths
    assert k["stile_m"] <= 0.025
    grips = [p for p in parts if p["role"] == "grip"]
    assert grips and all(p["key"] == "dark" for p in grips)                     # the recessed channel's shadow
    assert all(box(p)[5] - box(p)[2] >= 1.0 for p in grips)                     # a long grip
    beads = [p for p in parts if p["role"] == "bead"]
    assert beads and all(p["key"] == "handle" for p in beads)
    panes = [p for p in parts if p["role"] == "glass"]
    assert panes and all(p["key"] == "bronze_glass" for p in panes)              # the modern family's warm glass
    assert not [p for p in parts if p["key"] == "dark" and p["role"] not in ("plinth", "grip")]


def test_wood_slats_with_real_gaps_and_reeded_glass_with_rounded_flutes():
    parts = MOD.module_parts(MOD.module_plan(_piece("slats")))
    slats = [p for p in parts if p["role"] == "slat"]
    assert slats and all(p["key"] == "front" for p in slats)                     # the shell's veneer, not black
    k = MOD.SEE_THROUGH
    assert k["slat_d_m"] >= 0.018 and k["slat_pitch_m"] - k["slat_h_m"] >= 0.02
    by_panel: dict = {}
    for p in slats:
        bb = P.parts_bbox([p])
        by_panel.setdefault((round(bb[1], 3), round(bb[0] + bb[3], 3)), []).append(bb)
    for boxes in by_panel.values():
        boxes.sort(key=lambda b: b[2])
        gaps = [b[2] - a[5] for a, b in zip(boxes, boxes[1:])]
        assert min(gaps) >= 0.02 - 1e-6                                         # the contents show between them
    reeded = MOD.module_parts(MOD.module_plan(_piece("reeded_glass", "scandinavian")))
    reeds = [p for p in reeded if p["role"] == "reed"]
    assert reeds and all(p["key"] == "reeded_glass" and len(p["verts"]) >= 10 for p in reeds)    # rounded facets
    pane = next(p for p in reeded if p["role"] == "glass")
    assert pane["key"] == "reeded_glass"
    xs = sorted({round(sum(v[0] for v in p["verts"]) / len(p["verts"]), 4) for p in reeds})
    assert xs[1] - xs[0] == pytest.approx(k["reed_pitch_m"], abs=1e-4)          # one flute beside the next
    assert MOD.pane_key("smoked_glass", WF.built_in_look({"family": "scandinavian"})) == "smoked_glass"
    assert MOD.pane_key("smoked_glass") == "smoked_glass"


def test_the_glass_reads_as_glass_and_the_light_inside_is_subtle():
    from wenart.blender import materials as M

    for tone in ("grey", "bronze"):
        rgb = M.TINTED_GLASS[tone]
        assert sum(rgb) / 3.0 >= 0.45 > sum(M.SMOKED_GLASS_RGB) / 3.0              # half the light, not a black mirror
    assert M.TINTED_GLASS["bronze"][0] > M.TINTED_GLASS["bronze"][2]                # warm
    assert M.REEDED_GLASS["transmission"] > M.SATIN_GLASS["transmission"]
    assert M.REEDED_GLASS["roughness"] < M.SATIN_GLASS["roughness"]                 # clearer than a door's satin lite
    assert WC.LED_LM_PER_M <= 800.0 and WC.SHELF_LM_PER_M <= 400.0 and WC.LED_K == 3000.0
    plan = MOD.module_plan(_piece("slats"))
    assert any("the built-in's look" in n for n in plan["notes"]) and plan["see_through"]["look"]["family"] == "modern"
