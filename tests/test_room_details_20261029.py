"""Lessons UL113, UL115 (hall part), UL119 (29 Oct 2026; the user's reference photos: "also take some inspiration from
these photos", "look at all these details I want these details", "As much detail as you can digest", "different
solutions for different rooms"; docs/reference_details_20261029.md H1-H8, R2-R30, R32-R34, G2, G5, V1, K13), checked on
CPU on synthetic rooms:

- the room schemes (``wenart.furniture.room_schemes``): a different scheme for each room of a type on a level, the
  family's pool and its substitutions, the photos' no-panel rule, partners, the record the build reads;
- what the schemes change (``wenart.furniture.room_details``): the TV on the wall (R26), the floating corner desk and
  its wall unit (R27), the drum and floating nightstands (R17, R33), an art pair over the bed (R16), art over a
  headboard panel (R32), the dining wall (K13), track lights (H7, R14), the living models (G5), the statement style,
  the drapes' colour (R6);
- the details: a lit niche (H1), the intercom (H2), a round mirror and pampas over a hall console (H4, R10, H5), a
  floor vase (H5), a hall rug (H6), leaning art (R5), a lived-in bag (R29), blinds behind curtains (R21), objects
  between books (R20);
- the build's side (pure): the wall looks of a scheme (R25, R34), the feature-wall kinds (slats, headboard panel,
  dining slat wall), the detail parts in their boxes, the scheme forms built by design, the art over a headboard, the
  scene checks, the ceiling beams (G2), the stair finishes (H8), the fit's statement styles;
- the checks U32 (Argus) and M28 (model review), the lesson records, and the schemes real06 (run 20261029-100801)
  gets.
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest

from test_decor_m8 import RID, room_building
from wenart import building as B
from wenart.agent import causes as CS
from wenart.audit import kinds as K
from wenart.audit import lessons as LS
from wenart.blender import ceiling_beams as CB
from wenart.blender import detail_parts as DP
from wenart.blender import feature_walls as FW
from wenart.blender import furniture as F
from wenart.blender import looks as LK
from wenart.blender import model_review as MR
from wenart.blender import parametric as P
from wenart.blender import scene_checks as SC
from wenart.blender import shell
from wenart.furniture import catalog as C
from wenart.furniture import decor as D
from wenart.furniture import decor_ai as DA
from wenart.furniture import fit as FIT
from wenart.furniture import media_wall as MW
from wenart.furniture import room_details as RD
from wenart.furniture import room_schemes as RS
from wenart.run import stages as ST
from wenart.style import colours as COL

SCANDI = {"family": "scandinavian", "floor": {"material": "wood_oak_light", "asset": "WoodFloor051"},
          "walls": {"material": "plaster_white"}, "wall_accent": None, "decor": {}}
MODERN = dict(SCANDI, family="modern")
REAL06 = Path("/home/user/WenArt_RUN/runs/20261029-100801-full/results/renders/real06/building_built.json")


def ids():
    counter = iter(range(500, 999))
    return lambda lv: f"dec_{lv}_{next(counter):03d}"


def bedroom(width=4.0, depth=5.0, windows=(), furniture=(), doors=()):
    """A 4 x 5 m bedroom: the double bed's head on the north wall (y = depth), its two nightstands."""
    bed = ("bed_double", (2.0, depth - 1.0), 0.0, (1.6, 2.0))
    stands = [("nightstand", (0.95, depth - 0.21), 0.0, (0.45, 0.42)),
              ("nightstand", (3.05, depth - 0.21), 0.0, (0.45, 0.42))]
    b = room_building(width, depth, "bedroom", furniture=[bed] + stands + list(furniture), windows=windows,
                      doors=doors)
    for f in b["furniture"]:
        f["height"] = {"bed_double": 0.5, "nightstand": 0.5}.get(f["type"], f.get("height"))
    return b


def add_room(b: dict, rid: str, room_type: str, x0: float, level: str = "L0", w: float = 4.0, d: float = 4.0):
    b["rooms"].append({"id": rid, "level_id": level, "label": rid, "room_type": room_type,
                       "polygon": [[x0, 0], [x0 + w, 0], [x0 + w, d], [x0, d]], "area_computed": w * d,
                       "status": "verified", "evidence": []})
    return b


def _room(b, rid=RID):
    return next(r for r in b["rooms"] if r["id"] == rid)


# --------------------------------------------------------------------------
# 1. the schemes (V1)
# --------------------------------------------------------------------------

def test_no_two_rooms_of_one_type_on_a_level_share_a_scheme_and_the_plan_is_stable():
    b = room_building(4.0, 4.0, "bedroom")
    for k in range(2, 6):
        add_room(b, f"r_L0_bed_{k}", "bedroom", 4.2 * k)
    add_room(b, "r_L1_bed_1", "bedroom", 0.0, level="L1")
    add_room(b, "r_L0_liv", "living", 40.0)
    add_room(b, "r_L0_liv_2", "living", 45.0)
    plan = RS.plan(b, SCANDI)
    beds = [r for rid, r in plan.items() if r["kind"] == "bedroom" and r["level_id"] == "L0"]
    assert len(beds) == 5 and len({r["key"] for r in beds}) == 5
    assert len({r["bundle"] for r in beds}) == len(RS.POOLS["bedroom"])         # every bundle before a repeat
    livings = [r for r in plan.values() if r["kind"] == "living"]
    assert len({r["key"] for r in livings}) == 2
    assert RS.plan(copy.deepcopy(b), SCANDI) == plan                             # deterministic by room id
    for r in plan.values():
        assert r["reason"] and r["why"]["walls"] and r["rule"] == RS.RULE and r["lesson"] == "UL119"
    # the record the build reads
    RS.record(b, plan, SCANDI)
    room = _room(b)
    assert room["scheme"]["key"] == plan[RID]["key"] and set(room["scheme"]) <= set(RS.COMPACT_KEYS) | {"rule",
                                                                                                       "reason"}
    assert b["room_schemes"]["lessons"] == ["UL113", "UL115", "UL119"]
    assert RS.scheme_of(b, RID)["key"] == plan[RID]["key"]


def test_a_twin_takes_its_partners_scheme_and_a_no_panel_room_takes_art():
    b = room_building(4.0, 4.0, "bedroom")
    add_room(b, "r_twin", "bedroom", 5.0)
    plan = RS.plan(b, SCANDI, partners={"r_twin": RID})
    assert plan["r_twin"]["key"] == plan[RID]["key"] and plan["r_twin"]["copied_from"] == RID
    for k in range(6):
        rid = f"r_np_{k}"
        add_room(b, rid, "bedroom", 10.0 + 5 * k)
    plan = RS.plan(b, SCANDI, no_panel={f"r_np_{k}" for k in range(6)})
    for k in range(6):
        r = plan[f"r_np_{k}"]
        assert r.get("feature") not in RS.PANEL_FEATURES and r.get("feature_kind") is None


def test_the_family_resolves_the_bundle():
    classic = RS.resolve("bedroom", "slats", "pale taupe", "classic")
    assert classic["feature_kind"] == "wainscot"
    assert RS.resolve("living", "panel", "pale taupe", "rustic")["feature_kind"] == "slats"
    assert RS.resolve("bedroom", "panel", "x", "scandinavian")["feature_kind"] == "fluted"
    assert RS.resolve("bedroom", "deep", "dark sage", "classic")["nightstand"] == "standing"     # no drum
    assert RS.resolve("bedroom", "deep", "dark sage", "modern")["nightstand"] == "drum"
    assert RS.resolve("bedroom", "limewash", "x", "scandinavian")["nightstand"] == "floating"
    assert RS.resolve("bedroom", "deep", "x", "scandinavian")["lighting"] == "downlights"         # track: modern
    assert RS.resolve("bedroom", "deep", "x", "modern")["lighting"] == "track"
    assert RS.resolve("bedroom", "deep", "x", "classic")["desk"] == "freestanding"
    assert RS.resolve("living", "limewash", "x", "classic")["dining_wall"] == "art"          # a classic home: no slats
    assert RS.resolve("living", "limewash", "x", "modern")["coffee_table"] == "glass"
    # the colours: real phrases; deep walls read deep, not black; limewash lighter
    for fam in RS.DEEP_COLOURS:
        for c in RS.DEEP_COLOURS[fam] + RS.LIMEWASH_COLOURS[fam] + RS.ACCENT_COLOURS[fam]:
            assert COL.parse(c) is not None, c
        for c in RS.DEEP_COLOURS[fam]:
            assert 0.12 <= COL.luminance(*COL.parse(c)) <= 0.30, (fam, c)
        for c in RS.LIMEWASH_COLOURS[fam]:
            assert 0.20 <= COL.luminance(*COL.parse(c)) <= 0.65, (fam, c)


def test_the_scheme_kinds_of_rooms():
    b = room_building(4.0, 4.0, "hall")
    assert RS.scheme_kind(b, _room(b)) == "hall"
    stair = room_building(2.0, 2.0, "hall", furniture=[("stair", (1.0, 1.0), 0.0, (1.9, 1.9))])
    assert RS.scheme_kind(stair, _room(stair)) is None                 # a landing
    office = room_building(3.0, 3.0, "other", furniture=[("desk", (0.6, 2.7), 0.0, (1.2, 0.6))])
    assert RS.scheme_kind(office, _room(office)) == "office"
    kitchen = room_building(4.0, 4.0, "kitchen", furniture=[("table_dining", (2.0, 2.0), 0.0, (1.6, 0.9))])
    assert RS.scheme_kind(kitchen, _room(kitchen)) == "dining"
    assert RS.scheme_kind(room_building(2.0, 2.0, "bathroom"), _room(room_building(2.0, 2.0, "bathroom"))) is None


# --------------------------------------------------------------------------
# 2. what the schemes change
# --------------------------------------------------------------------------

def _tv_bedroom():
    b = bedroom()
    unit = {"id": "f_L0_090", "level_id": "L0", "room_id": RID, "type": "tv_unit", "source": "added_by_ai",
            "method": "rule", "footprint": {"center": [2.0, 0.21], "size": [1.2, 0.4], "rotation_deg": 180.0},
            "front_deg": 90.0, "height": None, "asset": None, "status": "verified",
            "rule": {"name": "media_wall", "seat": "f_L0_001", "free": False}}
    b["furniture"].append(unit)
    b["decor"] = [{"id": "dec_L0_001", "kind": "decor", "type": "tv", "level_id": "L0", "room_id": RID,
                   "host_id": unit["id"], "center": [2.0, 0.21], "size": [1.13, 0.3, 0.7], "tv": {"inches": 50}},
                  {"id": "dec_L0_002", "kind": "decor", "type": "vase", "level_id": "L0", "room_id": RID,
                   "host_id": unit["id"], "center": [2.5, 0.21], "size": [0.18, 0.18, 0.4]}]
    return b, unit


def test_a_bedrooms_tv_hangs_on_the_wall_in_place_of_the_media_walls_unit():
    b, unit = _tv_bedroom()
    rc = RD.Room(b, _room(b))
    notes = RD.wall_tv(b, rc, {"tv": "wall", "kind": "bedroom"}, ids())
    assert not [f for f in b["furniture"] if f["id"] == unit["id"]] and b["furniture_removed"][0]["id"] == unit["id"]
    (tv,) = [d for d in b["decor"] if d["type"] == "tv"]
    assert tv["host_id"] is None and tv["tv"]["mount"] == "wall" and tv["wall_point"][1] == pytest.approx(0.0, abs=1e-3)
    panel_h = tv["size"][2]
    assert tv["center"][2] + panel_h / 2.0 == pytest.approx(RD.TV_WALL_CENTRE_M["bedroom"], abs=1e-3)
    assert {d["id"] for d in b["decor_dropped"]} == {"dec_L0_001", "dec_L0_002"} and notes
    found, n = MW.review(b)
    assert not [f for f in found if f["room_id"] == RID]
    # a drawn unit stays: the TV hangs over it
    b, unit = _tv_bedroom()
    unit["source"] = "from_documents"
    RD.wall_tv(b, RD.Room(b, _room(b)), {"tv": "wall", "kind": "bedroom"}, ids())
    (tv,) = [d for d in b["decor"] if d["type"] == "tv"]
    assert any(f["id"] == unit["id"] for f in b["furniture"]) and tv["over_unit"] == unit["id"]
    assert tv["center"][2] >= RD._top(unit) + RD.TV_OVER_UNIT_M - 1e-6


def _office():
    b = room_building(3.0, 3.0, "other", furniture=[("desk", (0.6, 2.7), 0.0, (1.2, 0.6)),
                                                    ("office_chair", (0.6, 2.05), 180.0, (0.6, 0.6))])
    return b


def test_a_corner_desk_floats_on_its_shelf_unit_with_a_wall_unit_over_it():
    b = _office()
    notes = RD.floating_desk(b, RD.Room(b, _room(b)), {"desk": "floating"}, ids())
    desk = b["furniture"][0]
    assert desk["form"] == "floating" and desk["form_detail"] == {"wall_end": "-x", "support": "+x",
                                                                  "shelf_unit_w": RD.SHELF_UNIT_W_M}
    (unit,) = [d for d in b["decor"] if d["type"] == "desk_wall_unit"]
    assert unit["center"][2] == pytest.approx(RD._top(desk) + RD.DESK_UNIT["shelf_over_m"], abs=1e-3)
    assert unit["desk_id"] == desk["id"] and not unit.get("anchor_ids") and len(notes) == 2
    assert unit["center"][1] == pytest.approx(3.0 - unit["size"][1] / 2.0 - 0.003, abs=1e-3)
    # a window behind the desk: no wall unit; a desk in no corner stays freestanding
    b = room_building(3.0, 3.0, "other", furniture=[("desk", (1.5, 2.7), 0.0, (1.2, 0.6))],
                      windows=(("w", "n", 1.5, 1.0),))
    notes = RD.floating_desk(b, RD.Room(b, _room(b)), {"desk": "floating"}, ids())
    assert "form" not in b["furniture"][0] and not [d for d in b.get("decor", []) if d["type"] == "desk_wall_unit"]
    assert any("no corner" in n for n in notes) and any("no wall unit" in n for n in notes)


def test_drum_and_floating_nightstands_and_the_items_on_a_drum():
    b = bedroom()
    stand = b["furniture"][1]
    b["decor"] = [{"id": "dec_L0_001", "kind": "decor", "type": "table_lamp", "level_id": "L0", "room_id": RID,
                   "host_id": stand["id"], "center": [0.95 + 0.15, 4.79 + 0.12], "size": [0.2, 0.2, 0.45],
                   "rotation_deg": 0.0}]
    notes = RD.nightstand_forms(b, RD.Room(b, _room(b)), {"nightstand": "drum"})
    assert [f.get("form") for f in b["furniture"]] == [None, "drum", "drum"] and len(notes) >= 2
    lamp = b["decor"][0]
    lx, ly = lamp["center"][0] - 0.95, lamp["center"][1] - 4.79
    assert math.hypot(lx, ly) + math.hypot(0.2, 0.2) / 2.0 <= 0.21 - 0.03 + 1e-6 and lamp["moved_for"]
    b = bedroom()
    RD.nightstand_forms(b, RD.Room(b, _room(b)), {"nightstand": "floating"})
    assert [f.get("form") for f in b["furniture"]] == [None, "floating", "floating"]
    assert "R33" in b["furniture"][1]["form_why"]


def test_an_art_pair_over_the_bed_and_art_over_a_headboard_panel():
    b = bedroom()
    rc = RD.Room(b, _room(b))
    RD.bed_wall(b, rc, {"feature": "art_pair", "kind": "bedroom"}, ids())
    pair = [d for d in b["decor"] if d["type"] == "wall_art"]
    assert len(pair) == 2 and all(d["anchor_ids"] == ["f_L0_001"] for d in pair)
    assert pair[0]["size"][0] == pytest.approx((RD.ART_PAIR_SHARE * 1.6 - RD.ART_PAIR_GAP_M) / 2.0, abs=2e-3)
    assert abs(pair[1]["center"][0] - pair[0]["center"][0]) == pytest.approx(pair[0]["size"][0] + RD.ART_PAIR_GAP_M,
                                                                              abs=2e-3)
    b = bedroom()
    RD.bed_wall(b, RD.Room(b, _room(b)), {"feature": "headboard_panel", "feature_kind": "headboard_panel",
                                          "kind": "bedroom"}, ids())
    (art,) = [d for d in b["decor"] if d["type"] == "wall_art"]
    assert art["min_bottom_m"] == pytest.approx(RD.HEADBOARD_TOP_M + RD.HEADBOARD_ART_GAP_M)
    footprint, rec = F.wall_art_placement(art, [0.8, 0.03, 0.6], 1.0, 2.7)
    assert rec["bottom_m"] == pytest.approx(art["min_bottom_m"])               # hung over the panel, not at 1.25


def test_the_dining_wall_takes_a_slat_wall_with_art():
    b = room_building(6.0, 5.0, "living", furniture=[("table_dining", (3.0, 4.0), 0.0, (1.6, 0.9))])
    room = _room(b)
    room["scheme"] = {"dining_wall": "slats"}
    notes = RD.dining_wall(b, RD.Room(b, room), {"dining_wall": "slats"}, ids())
    at = room["scheme"]["dining_wall_at"]
    assert at["wall_id"] == "w_n" and at["table_id"] == "f_L0_001" and len(notes) == 2
    (art,) = [d for d in b["decor"] if d["type"] == "wall_art"]
    assert art["bottom_m"] == RD.DINING_ART_BOTTOM_M and art["free_wall"]
    plans, skipped = FW.plan_dining_walls(b, b["levels"][0], SCANDI)
    (p,) = plans
    assert p["kind"] == "slats" and p["dining"] and p["wall_id"] == "w_n" and p["width_m"] > 3.0 and not skipped
    boxes = FW.panel_boxes(p)
    assert {bx[3] for bx in boxes} == {"wood", "backing", "plinth"}
    out, _notes = FW.standoff_decor([art], [p])
    assert out[0]["feature_wall_standoff_m"] > 0.02                            # the art stands on the slats


def test_track_lights_statement_style_drapes_and_living_models():
    b = bedroom()
    b["decor"] = [{"id": "dec_L0_001", "kind": "decor", "type": "ceiling_light", "level_id": "L0", "room_id": RID,
                   "rule": "decor.ceiling_lights", "fixture": "downlight", "center": [2.0, 1.2, 2.69],
                   "size": [0.09, 0.09, 0.012]},
                  {"id": "dec_L0_002", "kind": "decor", "type": "pendant_light", "level_id": "L0", "room_id": RID,
                   "fixture": "statement", "anchor_ids": ["f_L0_001"], "center": [2.0, 4.0, 2.0]},
                  {"id": "dec_L0_003", "kind": "decor", "type": "curtain", "level_id": "L0", "room_id": RID,
                   "colour": "beige", "center": [2.0, 0.1, 0.0]}]
    rc = RD.Room(b, _room(b))
    assert RD.track_lights(b, rc, {"lighting": "track"})
    t = b["decor"][0]
    assert t["fixture"] == "track" and t["size"] == list(RD.TRACK_SIZE) and t["center"][2] == pytest.approx(2.58)
    assert RD.statement_style(b, rc, {"statement": "linear"}) and b["decor"][1]["statement_style"] == "linear"
    assert RD.drape_colours(b, rc, {"walls": "deep_colour", "wall_colour": "dark sage"})
    assert b["decor"][2]["colour"] == "dark sage" and b["decor"][2]["colour_ai"] == "beige"
    liv = room_building(6.0, 5.0, "living", furniture=[("table_coffee", (3.0, 3.0), 0.0, (1.2, 0.6)),
                                                       ("armchair", (1.0, 1.0), 0.0, (0.8, 0.8)),
                                                       ("armchair", (5.0, 1.0), 0.0, (0.8, 0.8))])
    liv["furniture"][1]["group"] = {"group": "reading_corner"}
    liv["furniture"][2]["group"] = {"group": "seating"}
    RD.living_models(liv, RD.Room(liv, _room(liv)), {"coffee_table": "glass", "lounge_chair": "rattan"})
    assert liv["furniture"][0]["design"]["material_tags"] == ["glass"] and liv["furniture"][0]["design_why"]
    assert liv["furniture"][1]["design"]["material_tags"] == ["rattan"] and "design" not in liv["furniture"][2]
    entries = [({"title": "Brass Sputnik Chandelier 12 Globes"}, {}), ({"title": "Linear Bar Pendant"}, {}),
               ({"title": "Plain Lamp"}, {})]
    pool, why = FIT.fixture_pool(entries, {"fixture": "statement", "statement_style": "linear"})
    assert [e["title"] for e, _f in pool] == ["Linear Bar Pendant"] and "linear" in why
    pool, _why = FIT.fixture_pool(entries, {"fixture": "statement"})
    assert [e["title"] for e, _f in pool] == ["Brass Sputnik Chandelier 12 Globes"]


# --------------------------------------------------------------------------
# 3. the details
# --------------------------------------------------------------------------

def _hall(width=3.0, depth=3.0, console=True):
    furniture = [("console_table", (1.5, depth - 0.18), 0.0, (1.1, 0.35))] if console else []
    b = room_building(width, depth, "hall", furniture=furniture, doors=(("d1", "s", width / 2.0, 0.9, True),))
    for f in b["furniture"]:
        f["height"] = 0.8
    return b


def test_a_hall_console_gets_a_round_mirror_pampas_and_a_round_rug():
    b = _hall()
    rc = RD.Room(b, _room(b))
    m = RD.round_mirror(b, rc, "test")
    assert m["type"] == "mirror" and m["shape"] == "round" and m["anchor_ids"] == ["f_L0_001"]
    assert m["size"][0] in RD.ROUND_MIRROR_W and m["max_height_m"] == m["size"][0]
    assert F.mirror_box(m) == [m["size"][0], P.MIRROR_FRAME_M, m["size"][0]]
    b.setdefault("decor", []).append(dict(m, id="dec_L0_400"))
    notes = RD.pampas_vase(b, rc, "scandinavian", ids())
    (vase,) = [d for d in b["decor"] if d["type"] == "vase"]
    assert vase["stems"] == "pampas" and vase["host_id"] == "f_L0_001" and notes
    assert RD.PAMPAS_MIN_ROOM_M <= vase["size"][2] <= RD.PAMPAS_MAX_H_M
    rug = RD.hall_rug(b, rc, {"rug": "round"})
    assert rug["shape"] == "round" and rug["size"][0] in RD.RUG_ROUND_D
    from shapely.geometry import Point, Polygon
    disc = Point(rug["center"][:2]).buffer(rug["size"][0] / 2.0)
    door = rc.ctx.doors[0]
    assert disc.intersection(door.swing).area < 1e-6                         # off the door's swing
    assert Polygon(_room(b)["polygon"]).buffer(-RD.RUG_EDGE_M + 1e-6).contains(disc)
    long_hall = _hall(1.6, 6.0, console=False)
    runner = RD.hall_rug(long_hall, RD.Room(long_hall, _room(long_hall)), {"rug": "round"})
    assert runner.get("shape") is None and runner["size"][0] > runner["size"][1]       # a runner in a long hall


def test_a_hall_without_a_console_gets_a_lit_niche_off_the_door():
    b = _hall(3.0, 3.0, console=False)
    rc = RD.Room(b, _room(b))
    niche = RD.wall_niche(b, rc, "test")
    assert niche["type"] == "wall_niche" and niche["center"][2] == 0.0 and niche["size"][1] == RD.NICHE["depth"]
    assert rc.floor_failures("bookshelf", niche["center"], niche["rotation_deg"], niche["size"][:2],
                             wall_n=(math.sin(math.radians(niche["rotation_deg"])),
                                     -math.cos(math.radians(niche["rotation_deg"])))) == []
    assert niche["niche"]["shelves"] >= 3 and niche["wall_point"]
    parts = DP.niche_parts(*niche["size"], niche)
    keys = {p["key"] for p in parts}
    assert {"led", "wood", "painted"} <= keys and sum(p["role"] == "led" for p in parts) >= 3
    assert sum(p["role"] == "book" for p in parts) >= 6 and sum(p["role"] == "plume" for p in parts) >= 3


def test_wall_details_keep_off_the_wall_the_build_panels():
    b = room_building(4.0, 4.0, "living", furniture=[("sofa", (2.0, 3.53), 0.0, (2.2, 0.9))])
    room = _room(b)
    room["scheme"] = {"feature": "slats", "feature_kind": "slats", "key": "slats:x"}
    rc = RD.Room(b, room)
    rc.panel_lines = RD.panel_lines(b, room, SCANDI)
    assert len(rc.panel_lines) == 1                                     # the wall behind the sofa (w_n)
    assert all(abs(st["n"][1] + 1.0) > 1e-6 for st in rc.stretches(min_len=0.8, block_low=True, front_m=0.5))
    room["scheme"] = {"feature": "art", "feature_kind": None, "key": "gallery:x"}
    assert RD.panel_lines(b, room, SCANDI) == []


def test_the_intercom_hangs_beside_the_main_entrance():
    b = _hall(3.0, 3.0, console=False)
    b["site"] = {"entrances": [{"door_id": "d1", "level_id": "L0", "room_id": RID, "main": True}]}
    got = RD.intercoms(b, ids())
    (it,) = [d for d in b["decor"] if d["type"] == "intercom"]
    assert it["center"][2] + it["size"][2] / 2.0 == pytest.approx(RD.INTERCOM_CENTRE_M)
    assert it["door_id"] == "d1" and not it.get("anchor_ids") and got[RID]
    off = abs(it["wall_point"][0] - 1.5)
    assert off == pytest.approx(0.45 + RD.INTERCOM_DOOR_GAP_M + RD.INTERCOM_SIZE[0] / 2.0, abs=1e-3)
    assert it["wall_point"][1] == pytest.approx(0.0, abs=1e-3)
    assert RD.intercoms(b, ids()) == {}                                      # one per door
    synced = D.sync_to_hosts(b)
    assert any(d["type"] == "intercom" for d in synced["decor"])            # not dropped with its door


def test_a_floor_vase_leaning_art_and_a_lived_in_bag():
    b = bedroom(furniture=[("wardrobe", (3.6, 0.35), 180.0, (0.8, 0.6))])
    rc = RD.Room(b, _room(b))
    vase = RD.floor_vase(b, rc, "test")
    assert vase["type"] == "floor_vase" and vase["stems"] == "pampas" and vase["center"][2] == 0.0
    b.setdefault("decor", []).append(dict(vase, id="dec_L0_401"))
    art = RD.leaning_art(b, rc, "test")
    assert art["type"] == "art_leaning" and art["size"][2] in [x[2] for x in RD.LEANING_ART]
    assert G_dist(art["center"], vase["center"]) > 0.5
    bag = RD.lived_in(b, rc)
    assert bag["type"] == "bag" and tuple(bag["size"]) == RD.BAG_SIZE and "R29" in bag["reason"]


def G_dist(a, b):
    return math.hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1]))


def test_blinds_behind_the_curtains_of_the_modern_families_and_styled_shelves():
    b = bedroom(windows=(("win", "s", 2.0, 1.2),))
    cur = {"id": "dec_L0_001", "kind": "decor", "type": "curtain", "level_id": "L0", "room_id": RID,
           "window_id": "win", "center": [2.0, 0.1, 0.01], "rotation_deg": 180.0, "size": [1.6, 0.14, 2.6],
           "wall_point": [2.0, 0.0]}
    b["decor"] = [cur]
    rc = RD.Room(b, _room(b))
    assert RD.blinds_with_curtains(b, rc, "scandinavian", ids()) == []
    notes = RD.blinds_with_curtains(b, rc, "modern", ids())
    (blind,) = [d for d in b["decor"] if d["type"] == "blind"]
    assert blind["blind_kind"] == "slats" and blind["window_id"] == "win" and notes
    front = blind["center"][1] + blind["size"][1] / 2.0
    assert cur["center"][1] - cur["size"][1] / 2.0 >= front + RD.CURTAIN_BLIND_GAP_M - 1e-3      # mm rounding
    shelf = room_building(4.0, 4.0, "living", furniture=[("bookshelf", (2.0, 3.8), 0.0, (1.0, 0.35))])
    shelf["decor"] = [{"id": f"b{k}", "type": "book_set", "host_id": "f_L0_001", "room_id": RID,
                       "host_frame": {"support": "shelf", "shelf": k, "u": 0.0}} for k in range(4)]
    RD.styled_shelves(shelf, RD.Room(shelf, _room(shelf)))
    assert [bool(d.get("styled")) for d in shelf["decor"]] == [False, True, False, True]


def test_the_decor_stage_records_the_schemes_and_the_details():
    b = bedroom(windows=(("win", "s", 2.0, 1.2),))
    out, _records = DA.apply(b, "scandinavian", {"answers": {}}, style=SCANDI)
    B.validate(out)
    assert out["room_schemes"]["rooms"][RID]["kind"] == "bedroom" and _room(out)["scheme"]["key"]
    assert RID in out["room_schemes"]["applied"]
    assert any(d.get("rule", "").startswith("room_details.") for d in out["decor"])
    assert "wenart/furniture/room_details.py" in ST.DECOR_CODE and "wenart/furniture/room_schemes.py" in ST.DECOR_CODE


# --------------------------------------------------------------------------
# 4. the build's side (pure)
# --------------------------------------------------------------------------

def test_a_scheme_paints_the_room_all_round_or_names_its_accent():
    room = {"id": "r", "room_type": "bedroom", "scheme": {"walls": "deep_colour", "wall_colour": "dark sage",
                                                          "key": "deep:dark sage"}}
    look = LK.wall_face_material(SCANDI, room)
    assert look["material"] == "paint" and look["colour"] == "dark sage" and "R25" in look["scheme"]
    room["scheme"].update(walls="limewash", wall_colour="warm greige")
    assert LK.wall_face_material(SCANDI, room)["material"] == "lime_plaster"
    assert LK.wall_face_material(dict(SCANDI, room_schemes=False), room)["material"] == "plaster_white"
    b = bedroom()
    _room(b)["scheme"] = {"walls": "accent", "wall_colour": "pale dusty blue", "key": "panel:pale dusty blue"}
    acc = LK.accent_walls(b, b["levels"][0], SCANDI)
    assert acc["w_n"][RID]["colour"] == "pale dusty blue"
    brief = dict(SCANDI, wall_accent={"material": "paint", "colour": "sage"})
    assert LK.accent_walls(b, b["levels"][0], brief)["w_n"][RID]["colour"] == "sage"     # the brief wins
    _room(b)["scheme"] = dict(room["scheme"])
    acc = LK.accent_walls(b, b["levels"][0], SCANDI)
    assert acc["w_n"][RID]["material"] == "lime_plaster" and acc["w_n"][RID]["accent"]   # still the anchor wall


def test_the_schemes_feature_wall_kinds():
    b = bedroom()
    room = _room(b)
    room["scheme"] = {"feature": "slats", "feature_kind": "slats", "key": "slats:x"}
    (p,), _s = FW.plan_feature_walls(b, b["levels"][0], SCANDI)
    assert p["kind"] == "slats" and p["width_m"] == pytest.approx(4.0 - 2 * FW.END_GAP_M, abs=1e-3)
    assert p["z1"] == pytest.approx(2.7 - FW.FLUTED["ceiling_gap"])
    slats = FW.slat_layout(p["width_m"], p["spec"])
    assert slats[1][0] - slats[0][0] == pytest.approx(FW.SLATS["slat_w"] + FW.SLATS["gap"], abs=3e-3)
    room["scheme"] = {"feature": "headboard_panel", "feature_kind": "headboard_panel", "key": "limewash:x"}
    (p,), _s = FW.plan_feature_walls(b, b["levels"][0], SCANDI)
    assert p["kind"] == "headboard_panel" and p["width_m"] == pytest.approx(1.6 + 2 * FW.HEADBOARD["extra_m"])
    assert p["z1"] - p["z0"] == pytest.approx(FW.HEADBOARD["height"])
    boxes = FW.panel_boxes(p)
    assert {bx[3] for bx in boxes} == {"backing", "wood"} and len(boxes) == FW.HEADBOARD["boards"] + 2
    assert max(bx[0][2] + bx[1][2] / 2.0 for bx in boxes) == pytest.approx(p["z1"])
    art = {"id": "a", "type": "wall_art", "room_id": RID, "level_id": "L0", "wall_point": [2.0, 5.0],
           "center": [2.0, 4.98], "bottom_m": 1.0, "min_bottom_m": 1.32}
    assert FW.standoff_decor([art], [p])[0][0] is art                        # over the panel: on the wall
    low = dict(art, min_bottom_m=None, bottom_m=0.9)
    assert FW.standoff_decor([low], [p])[0][0]["feature_wall_standoff_m"] > 0.0
    room["scheme"] = {"feature": "art_pair", "feature_kind": None, "key": "deep:x"}
    plans, skipped = FW.plan_feature_walls(b, b["levels"][0], SCANDI)
    assert plans == [] and "two framed prints" in skipped[0]["reason"]
    assert FW.plan_feature_walls(b, b["levels"][0], dict(SCANDI, room_schemes=False))[0][0]["kind"] == "fluted"


def test_the_detail_parts_stay_in_their_boxes_with_known_keys():
    assert DP.DETAIL_DECOR_TYPES == P.DETAIL_DECOR_TYPES == D.DETAIL_DECOR_TYPES == RD.DETAIL_TYPES
    schema = B.load_schema()["$defs"]["decor"]["properties"]["type"]["enum"]
    from wenart.polish import prompt as PR
    from wenart.vision_check import prompts as VP
    for t in DP.DETAIL_DECOR_TYPES:
        assert t in schema and t in PR.DECOR_WORDS and t in VP.HINTS and t not in DA.AI_TYPES
        assert P.DECOR_DEFAULT_HEIGHT[t] == DP.DETAIL_DEFAULT_HEIGHT[t]
    assert set(DP.LARGE_DETAIL_TYPES) <= set(P.LARGE_DECOR_TYPES) and set(DP.LARGE_DETAIL_TYPES) <= set(
        D.LARGE_DECOR_TYPES)
    real = {"wall_niche": (1.0, 0.26, 2.2), "intercom": DP.DETAIL_DEFAULT_HEIGHT and (0.13, 0.03, 0.22),
            "floor_vase": (0.4, 0.4, 1.3), "art_leaning": (1.0, 0.24, 1.4), "bag": (0.55, 0.3, 0.3),
            "desk_wall_unit": (1.2, 0.32, 0.68)}
    for t, (w, d, h) in real.items():
        for box in ((w, d, h), (0.4, 0.3, 0.2)):
            parts = P.decor_parts(t, *box, {"niche": {"shelves": 4}})
            x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
            assert x1 - x0 <= box[0] + 1e-9 and y1 - y0 <= box[1] + 1e-9 and z1 - z0 <= box[2] + 1e-9, t
            assert z0 == 0.0 and {p["key"].replace("accent_", "").replace("colour_", "") for p in parts} <= set(
                P.MATERIAL_KEYS), t
    for dtype, box, item in (("mirror", (0.7, 0.04, 0.7), {"shape": "round"}), ("rug", (2.0, 2.0, 0.012),
                             {"shape": "round"}), ("ceiling_light", (1.0, 0.05, 0.12), {"fixture": "track"}),
                             ("tv", (1.2, 0.07, 0.7), {"tv": {"mount": "wall"}}),
                             ("vase", (0.18, 0.18, 0.7), {"stems": "pampas"}),
                             ("book_set", (0.4, 0.2, 0.22), {"styled": {"object": "bowl"}})):
        parts = P.decor_parts(dtype, *box, item)
        assert parts == DP.variant_parts(dtype, *box, item)
        x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
        assert x1 - x0 <= box[0] + 1e-9 and y1 - y0 <= box[1] + 1e-9 and z1 - z0 <= box[2] + 1e-9 and z0 == 0.0
    assert "pedestal" not in {p["role"] for p in DP.wall_tv_parts(1.2, 0.07, 0.7)}       # R26: no stand
    keys, _a = F.style_material_keys(SCANDI)
    from wenart.style import vocabulary as V
    assert keys["led"][0] in V.FLAT_COLOURS and keys["pampas"][0] == "fabric_linen"


def test_the_scheme_forms_are_built_by_design():
    drum = {"id": "n", "type": "nightstand", "form": "drum", "footprint": {"center": [0, 0], "size": [0.45, 0.42],
                                                                           "rotation_deg": 0.0}}
    parts = P.build_parts("nightstand", 0.45, 0.42, 0.55, drum)
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    assert x1 - x0 == pytest.approx(0.42, abs=0.005) and z0 == 0.0 and z1 == pytest.approx(0.55)
    assert sum(p["role"] == "groove" for p in parts) == 2 and sum(p["role"] == "handle" for p in parts) == 2
    floating = dict(drum, form="floating")
    parts = P.build_parts("nightstand", 0.45, 0.42, 0.5, floating)
    assert P.parts_bbox(parts)[2] == pytest.approx(0.5 - DP.FLOAT_NIGHTSTAND_H_M)          # nothing to the floor
    assert SC.wall_hung(floating) and not SC.wall_hung(drum)
    desk = {"id": "d", "type": "desk", "form": "floating", "form_detail": {"support": "+x", "shelf_unit_w": 0.4},
            "footprint": {"center": [0, 0], "size": [1.2, 0.6], "rotation_deg": 0.0}}
    parts = P.build_parts("desk", 1.2, 0.6, 0.75, desk)
    assert P.parts_bbox(parts)[2] == 0.0 and sum(p["role"] == "book" for p in parts) >= 4    # on its shelf unit
    assert all(v[0] >= 0.6 - 0.4 - 1e-6 for p in parts if p["role"] == "side" for v in p["verts"])
    assert C.scheme_form(drum) and C.by_design_parametric(desk) and not C.scheme_form(dict(drum, form="square"))
    asset = FIT.fit_piece(dict(drum, level_id="L0"), C.load(), style_family="scandinavian", mode="relaxed")
    assert asset["method"] == "parametric" and asset["by_design"] and asset["scheme_form"] == "drum"
    assert FIT.fit_decor_item({"type": "mirror", "shape": "round", "size": [0.7, 0.04]}, C.load()) is None


def test_ceiling_beams_under_a_slope_in_the_families_that_show_them():
    b = room_building(4.0, 5.0, "bedroom")
    level = b["levels"][0]
    level["ceiling_planes"] = [(0.0, -0.5, 4.0)]                   # z = 4 - 0.5 y: under 2.7 m from y = 2.6
    plans, _n = CB.plan_beams(b, level, dict(SCANDI, family="rustic"))
    (plan,) = plans
    beams = plan["beams"]
    assert len(beams) >= 5
    for bm in beams:
        assert abs(bm["p0"][0] - bm["p1"][0]) < 1e-6                 # along the fall line (y)
        assert 0.0 < bm["p0"][0] < 4.0 and min(bm["p0"][1], bm["p1"][1]) >= 2.6 - 0.06
        assert bm["z0"] < 2.7 and bm["z1"] < 2.7
    xs = sorted(bm["p0"][0] for bm in beams)
    assert all(x1 - x0 == pytest.approx(CB.PITCH_M, abs=1e-6) for x0, x1 in zip(xs, xs[1:]))
    verts, faces = CB.room_mesh(plan, level["ceiling_planes"])
    assert len(faces) == 6 * len(beams)
    assert CB.plan_beams(b, level, MODERN)[0] == []
    assert CB.plan_beams(b, level, dict(MODERN, ceiling_beams=True))[0]
    flat = copy.deepcopy(b)
    flat["levels"][0]["ceiling_planes"] = []
    assert CB.plan_beams(flat, flat["levels"][0], dict(SCANDI, family="rustic"))[0] == []


def test_the_stair_finishes_follow_the_family():
    tread, metal, why = shell.stair_finishes(MODERN, {"material": "tiles_light"})
    assert metal == "metal_black" and tread is not None and "timber treads" in why
    tread, metal, _w = shell.stair_finishes(SCANDI, {"material": "wood_oak_light"})
    assert metal == "steel_brushed" and tread is None                      # the wood floor's own treads


# --------------------------------------------------------------------------
# 5. the checks, the lessons, real06
# --------------------------------------------------------------------------

def test_u32_and_m28_find_a_shared_scheme_a_bare_hall_and_a_bare_bed_wall():
    b = bedroom()
    add_room(b, "r_L0_bed_2", "bedroom", 5.0)
    add_room(b, "r_L0_hall", "hall", 10.0)
    b["furniture"].append({"id": "f_L0_050", "level_id": "L0", "room_id": "r_L0_bed_2", "type": "bed_single",
                           "footprint": {"center": [6.0, 2.0], "size": [0.9, 2.0], "rotation_deg": 0.0},
                           "front_deg": 270.0, "source": "from_documents", "status": "verified", "evidence": []})
    same = RS.resolve("bedroom", "panel", "pale taupe", "scandinavian")
    b["room_schemes"] = {"rooms": {RID: dict(same, room_id=RID), "r_L0_bed_2": dict(same, room_id="r_L0_bed_2")}}
    found, n = RS.review(b, None, "U32")
    problems = sorted(f["problem"] for f in found)
    assert n == 3 and problems == ["bed_wall_bare", "bed_wall_bare", "hall_bare", "same_scheme"]
    b["decor"] = [{"id": "art", "type": "wall_art", "room_id": RID, "anchor_ids": ["f_L0_001"]}]
    found, _n = RS.review(b, None, "U32")
    assert sorted(f["room_id"] for f in found if f["problem"] == "bed_wall_bare") == ["r_L0_bed_2"]
    got = LS.audit(b, None)
    assert got["checked"]["U32"] == 3 and LS.CHECK_LESSONS["U32"] == ("UL113", "UL115", "UL119")
    u32 = next(x for x in got["findings"] if x["check"] == "U32")
    assert u32["kind"] == "taste" and u32["evidence"]["lesson"] in ("UL113", "UL115", "UL119")
    rec = MR.review(b, {"objects": []})
    assert "M28" in MR.CHECKS and rec["checks"]["M28"]["failed"] == 3
    assert next(x for x in rec["findings"] if x["check"] == "M28")["kind"] == "taste"
    assert K.kind_of({"check": "M28"}) == "taste" and K.CHECK_KIND["U32"] == "taste"
    assert CS.CHECK_CAUSE["M28"] == "decor_look"


def test_the_lessons_ul113_and_ul119_are_built():
    from wenart.blender import architect_lessons as L
    by = {x["id"]: x for x in L.lessons()}
    for lid in ("UL113", "UL119"):
        x = by[lid]
        assert x["status"] == "built" and x["checks"] == ["build"] and "U32" in x["lesson"] and "M28" in x["lesson"]
    assert by["UL115"]["status"] in ("open", "built")


@pytest.mark.skipif(not REAL06.is_file(), reason="the real06 run 20261029-100801-full is not in this checkout")
def test_real06_rooms_each_get_their_own_scheme():
    b = json.loads(REAL06.read_text(encoding="utf-8"))
    style = json.loads((REAL06.parent / "style.json").read_text(encoding="utf-8"))
    no_panel = {rid for rid, dec in ((b.get("dressing") or {}).get("rooms") or {}).items()
                if isinstance(dec, dict) and dec.get("feature_wall") is False}
    plan = RS.plan(b, style, no_panel)
    print("\nreal06 room schemes (run 20261029-100801-full):")
    for rid, r in sorted(plan.items()):
        print(f"  {rid:24s} {r['kind']:8s} {r['key']:28s} walls={r['walls']} feature={r.get('feature_kind')} "
              f"tv={r.get('tv')} desk={r.get('desk')} nightstand={r.get('nightstand')} lighting={r['lighting']} "
              f"dining_wall={r.get('dining_wall')} hall={r.get('hall')}")
    seen = {}
    for r in plan.values():
        k = (r["level_id"], r["kind"], r["key"])
        assert k not in seen, (k, seen.get(k))
        seen[k] = r["room_id"]
    beds = [r for r in plan.values() if r["kind"] == "bedroom"]
    assert len(beds) == 3 and len({r["bundle"] for r in beds}) == 3
    assert all(r.get("feature_kind") is None for rid, r in plan.items() if rid in no_panel)
    assert RS.plan(b, style, no_panel) == plan
