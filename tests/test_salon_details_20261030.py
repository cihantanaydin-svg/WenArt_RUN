"""The P16 living-dining room as general rules by style family (30 Oct 2026; user, sending photo P16: "salon
inspiration"; lesson UL153; docs/reference_details_20261029.md R39-R49; wenart/furniture/salon_details.py,
wenart/blender/salon_parts.py).

Pure tests on hand-made rooms (exact geometry): the floating TV console and its lit niches, the dining print at 2/3 of
the table, one fixture over the table that the lights plan counts as its row, the rugs (dining set, sofa group, the
round rug under a drum table), the centrepiece set, the panel wall with its lit niche, the wall discs; the parts stay in
their boxes; the fit builds the new forms and variants by design; the review (model review M34, Argus U38); the decor
stage end to end; real04's salon of run 20261029-201533-full when the run is in the checkout.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest
from shapely.geometry import Point, box

from test_decor_m8 import RID, room_building
from wenart import building as B
from wenart.agent import causes as CS
from wenart.audit import kinds as K
from wenart.audit import lessons as LS
from wenart.blender import detail_parts as DP
from wenart.blender import model_review as MR
from wenart.blender import parametric as P
from wenart.blender import salon_parts as SP
from wenart.blender import scene_checks as SC
from wenart.furniture import catalog as C
from wenart.furniture import ceiling_lights as CL
from wenart.furniture import decor as D
from wenart.furniture import decor_ai as DA
from wenart.furniture import fit as FIT
from wenart.furniture import room_details as RD
from wenart.furniture import salon_details as SD

SCANDI = {"family": "scandinavian", "floor": {"material": "wood_oak_light", "asset": "WoodFloor051"},
          "walls": {"material": "plaster_white"}, "wall_accent": None, "decor": {}}
MODERN = dict(SCANDI, family="modern")
REAL04 = Path("/home/user/WenArt_RUN/runs/20261029-201533-full/results/furniture/real04/building_final.json")


def ids():
    counter = iter(range(500, 999))
    return lambda lv: f"dec_{lv}_{next(counter):03d}"


def _room(b, rid=RID):
    return next(r for r in b["rooms"] if r["id"] == rid)


def _rc(b):
    room = _room(b)
    rc = RD.Room(b, room)
    rc.panel_lines = RD.panel_lines(b, room, MODERN)
    return rc


def _piece(b, pid):
    return next(f for f in b["furniture"] if f["id"] == pid)


def _decor(b, rule):
    return [d for d in b.get("decor") or [] if d.get("rule") == f"salon_details.{rule}"]


def tv_room(width=6.0, depth=5.0, doors=(), unit=("tv_unit", (0.23, 2.5), 90.0, (1.8, 0.45))):
    """A living room with the media wall's TV unit on the west wall (its back on x = 0) and its TV on it."""
    b = room_building(width, depth, "living", furniture=[unit], doors=doors)
    u = b["furniture"][0]
    u.update(source="added_by_ai", rule={"name": "media_wall", "free": False}, height=None)
    b["decor"] = [{"id": "dec_L0_001", "kind": "decor", "type": "tv", "level_id": "L0", "room_id": RID,
                   "host_id": u["id"], "center": list(u["footprint"]["center"]), "rotation_deg": 90.0,
                   "size": [1.459, 0.39, 0.889], "tv": {"inches": 65, "mount": "stand"}, "source": "added_by_ai"}]
    return b


def dining_room(width=7.0, depth=5.0, table=((3.5, 3.0), 0.0, (2.4, 0.9)), pendants=3, extra=()):
    """A living-dining room: a 2.4 m dining table, the lights rule's row of pendants over it."""
    b = room_building(width, depth, "living", furniture=[("table_dining",) + tuple(table)] + list(extra))
    t = b["furniture"][0]
    t["height"] = 0.75
    b["decor"] = []
    (cx, cy), _rot, (w, _d) = table
    for k in range(pendants):
        x = cx - 0.75 + 0.75 * k if pendants == 3 else cx
        b["decor"].append({"id": f"dec_L0_{k + 1:03d}", "kind": "decor", "type": "pendant_light", "level_id": "L0",
                           "room_id": RID, "rule": "decor.ceiling_lights", "anchor_ids": [t["id"]],
                           "center": [x, cy, 1.5], "size": [0.35, 0.35, 1.2], "rotation_deg": 0.0,
                           "source": "added_by_ai"})
    return b


# --------------------------------------------------------------------------
# pure rules
# --------------------------------------------------------------------------

def test_the_dining_print_is_two_thirds_of_the_table():
    assert SD.dining_art_width(3.35, 5.0) == 2.0                  # capped at ART_MAX_W_M (real04's 3.35 m table)
    assert SD.dining_art_width(2.4, 5.0) == pytest.approx(1.6)    # 2/3 of 2.4 m
    assert SD.dining_art_width(1.2, 5.0) == SD.ART_MIN_W_M        # never under 0.9 m
    assert SD.dining_art_width(2.4, 1.8) == pytest.approx(1.44)   # at most 0.8 of its free wall stretch


def test_the_dining_fixture_follows_the_scheme_and_the_family():
    assert SD.dining_fixture_kind({"lighting": "track"}, "modern") == "track_pendants"
    assert SD.dining_fixture_kind({"lighting": "downlights", "statement": "linear"}, "japandi") == "linear_pendant"
    assert SD.dining_fixture_kind({"lighting": "downlights", "statement": "linear"}, "classic") is None
    assert SD.dining_fixture_kind({"lighting": "downlights", "statement": "globe"}, "modern") is None


def test_a_near_square_coffee_table_reads_as_a_drum():
    sq = {"type": "table_coffee", "footprint": {"center": [0, 0], "size": [0.8, 0.8], "rotation_deg": 0.0}}
    assert SD.drum_candidate(sq)
    assert not SD.drum_candidate(dict(sq, footprint=dict(sq["footprint"], size=[1.3, 0.63])))   # real04's sofa table
    assert not SD.drum_candidate(dict(sq, form="drum")) and not SD.drum_candidate(dict(sq, type="side_table"))


def test_the_round_rug_spot_shrinks_and_moves_off_a_wall():
    allowed = box(0.3, 0.3, 5.7, 4.7)                             # a 6 x 5 m room shrunk by the rug inset
    assert SD.round_rug_spot(allowed, (3.0, 2.5), 0.8) == (2.0, (3.0, 2.5))     # the table + 0.6 m all round
    diam, c = SD.round_rug_spot(allowed, (3.0, 1.0), 0.8)        # 1.0 m from the wall: smaller and moved off it
    assert diam < 2.0 and c[1] > 1.0 and G_dist(c, (3.0, 1.0)) <= SD.ROUND_RUG_SHIFT_M + 1e-9
    assert allowed.contains(Point(c).buffer(diam / 2.0))
    assert diam / 2.0 - G_dist(c, (3.0, 1.0)) >= 0.4 + SD.ROUND_RUG_MIN_REACH_M - 1e-6    # the table stays on it
    assert SD.round_rug_spot(box(0.3, 0.3, 1.2, 4.7), (0.75, 2.5), 0.8) is None


def G_dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


# --------------------------------------------------------------------------
# 1. the TV wall set (R45)
# --------------------------------------------------------------------------

def test_a_low_wall_backed_tv_unit_floats_and_a_divider_or_a_cabinet_stays():
    b = tv_room()
    notes = SD.console_form(b, _rc(b), {}, "modern")
    u = b["furniture"][0]
    assert u["form"] == "floating" and "R45" in u["form_why"] and "floating console" in notes[0]
    assert b["salon_details"]["rooms"][RID]["tv_console"]["done"]
    assert SC.wall_hung(u) and C.scheme_form(u) and RD._top(u) == pytest.approx(0.5)     # its top as before
    free = tv_room()
    free["furniture"][0]["rule"]["free"] = True
    SD.console_form(free, _rc(free), {}, "modern")
    assert "form" not in free["furniture"][0]
    tall = tv_room()
    tall["furniture"][0]["height"] = 1.2
    SD.console_form(tall, _rc(tall), {}, "modern")
    assert "form" not in tall["furniture"][0] and "stays standing" in tall["salon_details"]["rooms"][RID][
        "tv_console"]["why"]
    classic = tv_room()
    SD.console_form(classic, _rc(classic), {}, "classic")
    assert "form" not in classic["furniture"][0]


def test_lit_niches_stand_beside_the_tv_and_the_tv_wall_stays_plain():
    b = tv_room()
    b["decor"].append({"id": "dec_L0_002", "kind": "decor", "type": "wall_art", "level_id": "L0", "room_id": RID,
                       "host_id": None, "free_wall": True, "center": [0.02, 2.6], "wall_point": [0.0, 2.6],
                       "rotation_deg": 90.0, "size": [1.2, 0.04], "bottom_m": 1.2, "max_height_m": 1.0,
                       "method": "ai", "source": "added_by_ai"})
    notes = SD.tv_niches(b, _rc(b), {}, "modern", ids())
    niches = _decor(b, "tv_niche")
    assert len(niches) == 2 and "left it" in notes[0]
    assert {n["niche"]["style"] for n in niches} == {"tv_side"} and len({n["size"][0] for n in niches}) == 1
    ys = sorted(n["center"][1] for n in niches)
    assert ys[0] < 2.5 - 0.9 and ys[1] > 2.5 + 0.9                            # one on each side of the unit
    for n in niches:
        assert n["center"][0] == pytest.approx(SD.NICHE_D_M / 2.0 + 0.002, abs=1e-3)   # its back on the wall
        assert n["anchor_ids"] == ["f_L0_001"] and n["source"] == "added_by_ai" and n["reason"]
        assert abs(n["center"][1] - 2.5) - n["size"][0] / 2.0 - 0.9 >= SD.NICHE_GAP_M - 1e-6
        assert n["size"][2] == pytest.approx(min(SD.NICHE_MAX_H_M, 2.7 - SD.NICHE_CEILING_GAP_M))
    assert not any(d["id"] == "dec_L0_002" for d in b["decor"])
    assert any(x["id"] == "dec_L0_002" and "plain" in x["reason"] for x in b["decor_dropped"])
    # a door beside the unit: one niche, the other side named
    one = tv_room(doors=(("d1", "w", 4.2, 0.9, True),))
    notes = SD.tv_niches(one, _rc(one), {}, "modern", ids())
    assert len(_decor(one, "tv_niche")) == 1 and "no niche on the" in notes[0]


def test_the_niches_keep_off_the_floor_of_other_pieces():
    b = tv_room(width=4.0, unit=("tv_unit", (0.23, 2.5), 90.0, (1.8, 0.45)))
    b["furniture"].append({"id": "f_L0_009", "level_id": "L0", "room_id": RID, "type": "armchair",
                           "source": "from_documents", "status": "verified", "height": None,
                           "footprint": {"center": [0.45, 4.1], "size": [0.8, 0.8], "rotation_deg": 90.0},
                           "front_deg": 0.0, "evidence": []})
    SD.tv_niches(b, _rc(b), {}, "modern", ids())
    niches = _decor(b, "tv_niche")
    assert len(niches) == 1 and niches[0]["center"][1] < 2.5           # not in front of the armchair


# --------------------------------------------------------------------------
# 2. the dining set (R40-R43)
# --------------------------------------------------------------------------

def test_the_dining_wall_art_is_two_thirds_of_the_table():
    b = room_building(6.0, 5.0, "living", furniture=[("table_dining", (3.0, 4.0), 0.0, (2.4, 0.9))])
    RD.dining_wall(b, RD.Room(b, _room(b)), {"dining_wall": "art"}, ids())
    (art,) = [d for d in b["decor"] if d["type"] == "wall_art"]
    assert art["size"][0] == pytest.approx(1.6) and art["max_height_m"] <= SD.ART_MAX_H_M
    assert abs(art["wall_point"][0] - 3.0) < 1e-6 and "R40" in art["reason"]


def test_one_track_of_mini_pendants_over_the_table_is_its_row():
    b = dining_room()
    notes = SD.dining_light(b, _rc(b), {"lighting": "track"}, "modern", ids())
    (fx,) = _decor(b, "dining_light")
    assert fx["fixture"] == "track_pendants" and fx["track"]["offsets"] == [-0.75, 0.0, 0.75] and "in place" in notes[0]
    assert fx["center"][:2] == [3.5, 3.0] and fx["center"][2] == pytest.approx(1.5)          # the row's height
    assert fx["size"][2] == pytest.approx(2.7 - 1.5) and fx["size"][0] == pytest.approx(2.0)
    assert not [d for d in b["decor"] if d.get("rule") == "decor.ceiling_lights"]
    assert len([x for x in b["decor_dropped"] if "R42" in x["reason"]]) == 3
    plan = CL.plan_room(b, _room(b), b["furniture"], [d for d in b["decor"] if d["type"] in CL.LIGHT_TYPES])
    assert not any(a.get("anchor_ids") == ["f_L0_001"] for a in plan["add"])       # the row is not laid again
    assert next(z for z in plan["zones"] if z["id"] == "f_L0_001")["lit"]
    assert FIT.fit_decor_item(fx, C.load()) is None                                   # ours, by design


def test_a_linear_pendant_where_the_scheme_hangs_a_linear_statement():
    b = dining_room()
    SD.dining_light(b, _rc(b), {"lighting": "downlights", "statement": "linear"}, "japandi", ids())
    (fx,) = _decor(b, "dining_light")
    assert fx["fixture"] == "linear_pendant" and fx["size"][0] == pytest.approx(1.6) and fx["colour"] == "black"
    keep = dining_room()
    notes = SD.dining_light(keep, _rc(keep), {"statement": "globe"}, "modern", ids())
    assert not _decor(keep, "dining_light") and "stays" in notes[0]


def test_a_rug_under_the_dining_set_and_none_twice():
    b = dining_room(pendants=0)
    SD.dining_rug(b, _rc(b), {}, "modern", ids())
    (rug,) = _decor(b, "dining_rug")
    assert rug["anchor_ids"] == ["f_L0_001"] and rug["fringe"] is True and rug["colour"]
    assert rug["size"][0] >= 2.4 + 1.0 and SD.rug_under(b, RID, (3.5, 3.0)) is rug
    SD.dining_rug(b, _rc(b), {}, "modern", ids())
    assert len(_decor(b, "dining_rug")) == 1
    unsure = dining_room(pendants=0)
    unsure["furniture"][0]["status"] = "unverified"
    unsure["furniture"][0]["type_proposal"] = True
    notes = SD.dining_rug(unsure, _rc(unsure), {}, "modern", ids())
    assert not _decor(unsure, "dining_rug") and "not sure" in notes[0]


def test_the_centrepiece_set_takes_the_tables_centre_between_the_places():
    b = dining_room()
    t = b["furniture"][0]
    b["decor"].append({"id": "dec_L0_050", "kind": "decor", "type": "vase", "level_id": "L0", "room_id": RID,
                       "host_id": t["id"], "center": [3.5, 3.0], "size": [0.18, 0.18, 0.3], "source": "added_by_ai"})
    for k, (dx, dy) in enumerate(((-0.25, 0.275), (0.25, 0.275), (-0.25, -0.275), (0.25, -0.275))):
        b["decor"].append({"id": f"dec_L0_06{k}", "kind": "decor", "type": "plate", "level_id": "L0", "room_id": RID,
                           "host_id": t["id"], "center": [3.5 + dx, 3.0 + dy], "size": [0.27, 0.27, 0.025],
                           "rotation_deg": 0.0, "source": "added_by_ai"})
    notes = SD.centrepiece(b, _rc(b), {}, "modern", ids())
    (cp,) = _decor(b, "centrepiece")
    assert cp["set"] == "centrepiece" and cp["stems"] == "pampas" and cp["host_id"] == t["id"]
    assert cp["size"][0] == pytest.approx(0.6) and cp["size"][1] <= 0.22 + 1e-9 and "in place of" in notes[0]
    assert cp["size"][2] <= 1.5 - 0.75 - SD.CENTRE_UNDER_LIGHT_M + 1e-9                     # under the pendants
    assert not any(d["id"] == "dec_L0_050" for d in b["decor"]) and FIT.fit_decor_item(cp, C.load()) is None
    small = dining_room(table=((3.5, 3.0), 0.0, (0.8, 0.8)), pendants=0)
    assert "too small" in SD.centrepiece(small, _rc(small), {}, "modern", ids())[0]


# --------------------------------------------------------------------------
# 3. the panel wall (R39)
# --------------------------------------------------------------------------

def test_a_panel_wall_with_a_lit_niche_on_a_free_dining_wall():
    b = dining_room(pendants=0)
    notes = SD.panel_wall(b, _rc(b), {}, "modern", ids())
    (pw,) = _decor(b, "panel_wall")
    w, d, h = pw["size"]
    assert w == pytest.approx(SD.PANEL_MAX_W_M) and d == SD.PANEL_D_M and h == pytest.approx(2.7 - 0.005)
    assert pw["wall_id"] == "w_n" and pw["center"][1] == pytest.approx(5.0 - SD.PANEL_D_M / 2.0 - 0.002, abs=1e-3)
    assert pw["panel"]["niche"] and "R39" in pw["reason"] and "panel wall" in notes[0]
    before = dict(b, decor=[x for x in b["decor"] if x is not pw])
    assert not RD.Room(before, _room(before)).floor_failures("wardrobe", pw["center"][:2], pw["rotation_deg"], (w, d),
                                                              wall_n=(0.0, -1.0))
    assert RD.Room(b, _room(b)).floor_failures("plant", (3.5, 4.5), 0.0, (0.4, 0.4))     # it is a floor obstacle now
    # a family without it, a wall behind the chairs (nothing free within 0.9 m)
    assert not _decor(dining_room(pendants=0), "panel_wall")
    classic = dining_room(pendants=0)
    SD.panel_wall(classic, _rc(classic), {}, "classic", ids())
    assert not _decor(classic, "panel_wall")
    near = dining_room(table=((3.5, 4.0), 0.0, (2.4, 0.9)), pendants=0, extra=[
        ("chair", (3.0, 4.68), 180.0, (0.45, 0.45)), ("chair", (4.0, 4.68), 180.0, (0.45, 0.45))])
    SD.panel_wall(near, _rc(near), {}, "modern", ids())
    for p in _decor(near, "panel_wall"):                                   # beside the dining set, never behind it
        assert abs(p["center"][0] - 3.5) >= 1.2 + p["size"][0] / 2.0 - 1e-6 or abs(p["center"][1] - 4.8) > 0.5


# --------------------------------------------------------------------------
# 4. the seating corner (R44, R47, R48)
# --------------------------------------------------------------------------

def test_a_square_coffee_table_becomes_a_drum_on_a_round_striped_rug():
    b = room_building(6.0, 5.0, "living", furniture=[
        ("table_coffee", (3.0, 2.5), 0.0, (0.8, 0.8)), ("armchair", (1.95, 2.5), 270.0, (0.8, 0.8)),
        ("armchair", (4.05, 2.5), 90.0, (0.8, 0.8)), ("table_coffee", (3.0, 4.0), 0.0, (1.3, 0.6))])
    b["furniture"][0]["design"] = {"material_tags": ["glass"]}
    b["furniture"][0]["height"] = 0.42
    b["decor"] = [{"id": "dec_L0_001", "kind": "decor", "type": "tray", "level_id": "L0", "room_id": RID,
                   "host_id": "f_L0_001", "center": [3.33, 2.83], "size": [0.3, 0.2, 0.04], "source": "added_by_ai"}]
    rc = _rc(b)
    SD.drum_tables(b, rc, {}, "modern")
    t = b["furniture"][0]
    assert t["form"] == "drum" and t["design"]["material_tags"] == [] and "form" not in b["furniture"][3]
    tray = b["decor"][0]
    assert math.hypot(tray["center"][0] - 3.0, tray["center"][1] - 2.5) + math.hypot(0.3, 0.2) / 2.0 <= 0.4
    SD.round_rug(b, rc, {}, "modern", ids())
    (rug,) = _decor(b, "round_rug")
    assert rug["shape"] == "round" and rug["pattern"] == "rings" and rug["size"] == [2.0, 2.0]
    assert rug["anchor_ids"] == ["f_L0_001", "f_L0_002", "f_L0_003"]
    asset = FIT.fit_piece(dict(t, level_id="L0"), C.load(), style_family="modern", mode="relaxed")
    assert asset["method"] == "parametric" and asset["by_design"] and asset["scheme_form"] == "drum"
    assert FIT.fit_decor_item(rug, C.load()) is None


def test_every_sofa_group_stands_on_a_rug_a_corner_sofa_too():
    b = room_building(6.0, 5.0, "living", furniture=[("sofa", (3.0, 4.53), 0.0, (2.2, 0.9)),
                                                     ("table_coffee", (3.0, 3.38), 0.0, (1.2, 0.6))])
    b["decor"] = []
    SD.seating_rug(b, _rc(b), {}, "classic", ids())                  # every family
    (rug,) = _decor(b, "seating_rug")
    assert set(rug["anchor_ids"]) == {"f_L0_001", "f_L0_002"} and SD.rug_under(b, RID, (3.0, 3.38)) is rug
    corner = room_building(6.0, 5.0, "living", furniture=[("sofa_corner", (3.0, 3.9), 0.0, (3.0, 2.0)),
                                                          ("table_coffee", (2.6, 3.4), 0.0, (0.9, 0.6))])
    corner["furniture"][0].update(chaise_side="right", shape="L")
    corner["decor"] = []
    assert SD.seating_group(corner["furniture"]) is not None
    SD.seating_rug(corner, _rc(corner), {}, "modern", ids())
    assert len(_decor(corner, "seating_rug")) == 1


def test_two_black_wall_discs_on_a_free_wall_never_on_the_tv_wall():
    b = tv_room()
    SD.wall_discs(b, _rc(b), {}, "modern", ids())
    (wd,) = _decor(b, "wall_discs")
    assert wd["type"] == "wall_discs" and wd["center"][2] >= SD.DISC_BOTTOM_M and wd["colour"] == "black"
    assert wd["wall_point"][0] > 0.5                                             # not on the TV's west wall
    assert wd["center"][2] + wd["size"][2] <= 2.7 - SD.DISC_CEILING_GAP_M + 1e-9
    scandi = tv_room()
    assert "no wall discs" in SD.wall_discs(scandi, _rc(scandi), {}, "scandinavian", ids())[0]


# --------------------------------------------------------------------------
# the parts and the fit
# --------------------------------------------------------------------------

def test_the_salon_parts_stay_in_their_boxes_with_known_keys():
    assert set(SP.DECOR_TYPES) <= set(DP.DETAIL_DECOR_TYPES) and DP.DETAIL_DECOR_TYPES == D.DETAIL_DECOR_TYPES
    keys = set(P.MATERIAL_KEYS)
    cases = (("panel_wall", (3.3, 0.4, 2.695), {"panel": {"module_m": 0.55, "niche": True}}),
             ("panel_wall", (1.65, 0.4, 2.4), {"panel": {"niche": False}}),
             ("wall_discs", (0.85, 0.04, 0.72), {}),
             ("wall_niche", (0.6, 0.3, 2.4), {"niche": {"style": "tv_side", "shelves": 4}}),
             ("pendant_light", (1.6, 0.08, 1.2), {"fixture": "linear_pendant"}),
             ("pendant_light", (2.0, 0.12, 1.2), {"fixture": "track_pendants", "track": {"offsets": [-0.75, 0, 0.75]}}),
             ("vase", (0.6, 0.22, 0.55), {"set": "centrepiece", "stems": "pampas"}),
             ("rug", (2.0, 2.0, 0.012), {"shape": "round", "pattern": "rings"}))
    for dtype, (w, d, h), item in cases:
        parts = P.decor_parts(dtype, w, d, h, item)
        x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
        assert x1 - x0 <= w + 1e-9 and y1 - y0 <= d + 1e-9 and z1 - z0 <= h + 1e-9 and z0 == pytest.approx(0.0), dtype
        assert {P.plain_key(p["key"]) for p in parts} <= keys, dtype
    roles = {p["role"] for p in P.decor_parts("pendant_light", 2.0, 0.12, 1.2,
                                               {"fixture": "track_pendants", "track": {"pendants": 3}})}
    assert {"rail", "cord", "shade", "bulb"} <= roles
    assert sum(p["role"] == "shade" for p in SP.track_pendants_parts(2.0, 0.12, 1.2, {"track": {"pendants": 4}})) == 4
    assert any(p["key"] == "led" for p in SP.panel_wall_parts(3.3, 0.4, 2.7, {"panel": {}}))
    assert not any(p["key"] == "led" for p in SP.panel_wall_parts(3.3, 0.4, 2.7, {"panel": {"niche": False}}))
    assert any(p["key"] == "dark" and p["role"] == "lining" for p in SP.tv_niche_parts(0.6, 0.3, 2.4))


def test_the_floating_console_hangs_and_the_drum_is_round():
    console = {"id": "u", "type": "tv_unit", "form": "floating",
               "footprint": {"center": [0, 0], "size": [1.8, 0.45], "rotation_deg": 0.0}}
    parts = P.build_parts("tv_unit", 1.8, 0.45, 0.5, console)
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    assert z0 == pytest.approx(0.5 - SP.CONSOLE_BOX_M) and z1 == pytest.approx(0.5)      # nothing to the floor
    assert sum(p["role"] == "rib" for p in parts) >= 8 and x1 - x0 == pytest.approx(1.8)
    assert SC.HUNG_FORMS["tv_unit"] == ("floating",) and SC.wall_hung(console)
    drum = {"id": "t", "type": "table_coffee", "form": "drum",
            "footprint": {"center": [0, 0], "size": [0.8, 0.8], "rotation_deg": 0.0}}
    parts = P.build_parts("table_coffee", 0.8, 0.8, 0.42, drum)
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    assert x1 - x0 == pytest.approx(0.8, abs=0.002) and z0 == 0.0 and z1 == pytest.approx(0.42)
    assert {p["key"] for p in parts} == {"stone_light", "dark"}
    asset = FIT.fit_piece(dict(console, level_id="L0"), C.load(), style_family="modern", mode="relaxed")
    assert asset["method"] == "parametric" and asset["by_design"] and asset["scheme_form"] == "floating"


# --------------------------------------------------------------------------
# the review (M34, U38), the decor stage, the lesson
# --------------------------------------------------------------------------

def _bare_salon():
    b = room_building(8.0, 6.0, "living", furniture=[
        ("sofa", (2.0, 5.53), 0.0, (2.2, 0.9)), ("table_coffee", (2.0, 4.38), 0.0, (1.2, 0.6)),
        ("tv_unit", (0.23, 2.5), 90.0, (1.8, 0.45)), ("table_dining", (6.0, 3.0), 90.0, (3.0, 1.0)),
        ("table_coffee", (4.5, 1.0), 0.0, (0.8, 0.8))])
    b["salon_details"] = {"family": "modern", "rooms": {}}
    b["room_schemes"] = {"family": "modern", "rooms": {RID: {"kind": "living", "lighting": "track"}}}
    b["decor"] = [{"id": f"dec_L0_00{k}", "kind": "decor", "type": "pendant_light", "level_id": "L0", "room_id": RID,
                   "rule": "decor.ceiling_lights", "anchor_ids": ["f_L0_004"], "center": [6.0, 2.0 + k, 1.5],
                   "size": [0.35, 0.35, 1.2], "rotation_deg": 0.0} for k in range(3)]
    b["decor"].append({"id": "dec_L0_010", "kind": "decor", "type": "wall_art", "level_id": "L0", "room_id": RID,
                       "rule": "room_details.dining_art", "center": [7.98, 3.0], "wall_point": [8.0, 3.0],
                       "size": [1.2, 0.04], "rotation_deg": 270.0})
    return b


def test_m34_and_u38_find_what_the_family_takes_from_p16():
    b = _bare_salon()
    found, n = SD.review(b, None, "U38")
    assert n == 1 and sorted(f["problem"] for f in found) == ["centrepiece", "dining_art_small", "dining_light",
                                                              "dining_rug", "drum_table", "seating_rug",
                                                              "tv_console", "tv_niches"]
    assert {f["kind"] for f in found} == {"taste"} and {f["lesson"] for f in found} == {"UL153"}
    b["salon_details"]["rooms"][RID] = {"tv_niches": {"done": False, "why": "no free wall beside it", "ids": []}}
    assert "tv_niches" not in {f["problem"] for f in SD.review(b, None, "U38")[0]}      # a recorded reason
    b["salon_details"]["family"] = b["room_schemes"]["family"] = "classic"
    b["room_schemes"]["rooms"][RID]["lighting"] = "downlights"                    # a classic scheme has no track
    assert sorted(f["problem"] for f in SD.review(b, None)[0]) == ["dining_art_small", "dining_rug", "seating_rug"]
    b = _bare_salon()
    got = LS.audit(b, None)
    assert got["checked"]["U38"] == 8 and LS.CHECK_LESSONS["U38"] == ("UL153",)
    u38 = next(x for x in got["findings"] if x["check"] == "U38")
    assert u38["kind"] == "taste" and u38["evidence"]["lesson"] == "UL153" and "salon_details" in u38["fix"]
    rec = MR.review(b, {"objects": []})
    assert "M34" in MR.CHECKS and rec["checks"]["M34"]["failed"] == 8
    assert next(x for x in rec["findings"] if x["check"] == "M34")["kind"] == "taste"
    assert K.kind_of({"check": "M34"}) == "taste" and K.CHECK_KIND["U38"] == "taste"
    assert CS.CHECK_CAUSE["M34"] == "decor_look"


def test_the_decor_stage_dresses_a_living_dining_room_like_p16():
    b = _bare_salon()
    b.pop("salon_details")
    b.pop("room_schemes")
    b["decor"] = []
    out, _records = DA.apply(b, "modern", {"answers": {}}, style=MODERN)
    B.validate(out)
    rec = out["salon_details"]
    assert rec["family"] == "modern" and rec["lesson"] == "UL153" and RID in rec["rooms"]
    rules = {str(d.get("rule")) for d in out["decor"]}
    assert {"salon_details.tv_niche", "salon_details.centrepiece", "salon_details.dining_light"} <= rules
    assert rec["rooms"][RID]["seating_rug"]["done"] and rec["rooms"][RID]["dining_rug"]["done"]   # the rules' or ours
    forms = {f["id"]: f.get("form") for f in out["furniture"]}
    assert forms["f_L0_003"] == "floating" and forms["f_L0_005"] == "drum"
    found, _n = SD.review(out, None)
    assert not [f for f in found if f["problem"] in ("tv_console", "drum_table", "seating_rug", "centrepiece")]
    assert any("salon_details" in t or "R45" in t for t in out["room_schemes"]["applied"][RID])


def test_the_lesson_ul153_is_built():
    from wenart.blender import architect_lessons as L

    x = {y["id"]: y for y in L.lessons()}["UL153"]
    assert x["status"] == "built" and x["checks"] == ["build"] and "U38" in x["lesson"] and "M34" in x["lesson"]
    assert x["question"]


@pytest.mark.skipif(not REAL04.is_file(), reason="the real04 run 20261029-201533-full is not in this checkout")
def test_real04_salon_gets_the_p16_set():
    b = json.loads(REAL04.read_text(encoding="utf-8"))
    counters = D.decor_counters(b["decor"])

    def new_id(lv):
        counters[lv] = counters.get(lv, 0) + 1
        return f"dec_{lv}_{counters[lv]:03d}"

    SD.start(b, "modern")
    room = _room(b, "r_L-1_salon")
    sc = b["room_schemes"]["rooms"]["r_L-1_salon"]
    rc = RD.Room(b, room)
    rc.panel_lines = RD.panel_lines(b, room, MODERN)
    SD.console_form(b, rc, sc, "modern")
    SD.drum_tables(b, rc, sc, "modern")
    SD.before_extras(b, rc, sc, "modern", new_id)
    SD.after_extras(b, rc, sc, "modern", new_id)
    assert _piece(b, "f_L-1_101")["form"] == "floating" and _piece(b, "f_L-1_073")["form"] == "drum"
    assert len([d for d in b["decor"] if d.get("rule") == "salon_details.tv_niche"]) == 2
    (fx,) = [d for d in b["decor"] if d.get("rule") == "salon_details.dining_light"]
    assert fx["fixture"] == "linear_pendant" and fx["size"][0] == pytest.approx(1.8)    # its scheme: a linear statement
    assert [d for d in b["decor"] if d.get("rule") == "salon_details.centrepiece"]
    assert not any(d["id"] == "dec_L-1_007" for d in b["decor"])        # the print beside the TV left the TV wall
    rec = b["salon_details"]["rooms"]["r_L-1_salon"]
    assert not rec["panel_wall"]["done"] and rec["panel_wall"]["why"]
