"""The bathroom and WC details of the user's reference photos (29 Oct 2026; lessons UL114, UL123, UL124;
docs/reference_details_20261029.md B1-B26): the style families' table, the parts of every detail, the layout stage's
looks (``bath_details.plan_building``), the decor stage's accessories (``bath_details.dress``), the fit's
made-to-measure pieces, the build hooks, the checks M26 and U30, and real06's bathrooms. CPU only; synthetic rooms
(tests/_m11_room.py) and, when the main repository holds it, real06's built building of run 20261029-100801-full."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import numpy as np
import pytest

import _m11_room as M
from wenart.blender import bath_parts as BT
from wenart.blender import build as BU
from wenart.blender import furniture as BF
from wenart.blender import looks as LK
from wenart.blender import modules as MOD
from wenart.blender import parametric as P
from wenart.blender import shell as SH
from wenart.furniture import bath_details as BD
from wenart.furniture import catalog as C
from wenart.furniture import decor as D
from wenart.furniture import fit as F
from wenart.furniture import locked as LO
from wenart.style import vocabulary as V

ROOT = Path(__file__).resolve().parents[1]
REAL06 = Path("/home/user/WenArt_RUN/runs/20261029-100801-full/results/renders/real06/building_built.json")
REAL06_STYLE = REAL06.with_name("style.json")
ROOM = M.ROOM_ID


def bathroom(*pieces, w: float = 3.0, h: float = 2.6) -> dict:
    """A 3.0 x 2.6 m bathroom, 2.7 m high, the door on the south wall at x = 1.0 opening into it, no window."""
    b = M.building(w=w, h=h, room_type="bathroom", window=None, furniture=list(pieces))
    b["rooms"][0]["label"] = "Banyo"
    return b


def toilet(pid="t1", **kw):
    """Its back on the east wall (x = 3.0), facing west."""
    return M.fp(pid, "toilet", (2.65, 0.95), (0.4, 0.7), rotation=270.0, **kw)


def basin(pid="w1", x=1.2, size=(0.6, 0.45), **kw):
    """On the north wall (y = 2.6), facing south."""
    return M.fp(pid, "washbasin", (x, 2.6 - size[1] / 2.0), size, rotation=0.0, **kw)


def shower(pid="s1", size=(0.9, 0.9)):
    """In the north-east corner, its back on the north wall."""
    return M.fp(pid, "shower", (3.0 - size[0] / 2.0, 2.6 - size[1] / 2.0), size, rotation=0.0)


def column(pid="c1"):
    return M.fp(pid, "tall_cabinet", (0.2, 1.4), (0.4, 0.35), rotation=270.0, source="added_by_ai", height=1.6)


def style_of(family):
    return {"family": family, "wet_walls": {"material": "tiles_light"}, "wet_floor": {"material": "tiles_light"},
            "floor": {"material": "wood_oak_light"}, "walls": {"material": "plaster_white"}}


def new_ids():
    counters = {}

    def new_id(level):
        counters[level] = counters.get(level, 0) + 1
        return f"dec_{level}_{counters[level]:03d}"
    return new_id


def volume(part) -> float:
    v = np.array(part["verts"], float)
    out = 0.0
    for f in part["faces"]:
        for k in range(1, len(f) - 1):
            out += float(np.dot(v[f[0]], np.cross(v[f[k]], v[f[k + 1]]))) / 6.0
    return out


def full(family="scandinavian"):
    b = bathroom(toilet(), basin(), shower(), column())
    st = style_of(family)
    BD.plan_building(b, st)
    return b, st


# --------------------------------------------------------------------------
# The family table
# --------------------------------------------------------------------------

def test_every_style_family_has_its_bathroom_row_and_the_modern_ones_are_wall_hung():
    for fam, _slots in V.STYLE_FAMILIES:
        spec, why = BT.spec_of(fam)
        assert spec["family"] == fam and "assumed" not in why
        assert spec["finish"] in BT.FINISH_HANDLE and spec["towel_colour"]
    for fam in ("modern", "minimal", "scandinavian", "japandi", "industrial"):
        spec = BT.spec_of(fam)[0]
        assert spec["wc"] == "wall_hung" and spec["mirror"] != "framed" and spec["vanity"] in BT.VANITY_KINDS
        assert spec["column"] == "open_lit"
    for fam in ("classic", "rustic", "mediterranean"):
        spec = BT.spec_of(fam)[0]
        assert spec["wc"] == "close_coupled" and spec["mirror"] == "framed" and spec["vanity"] == "as_drawn"
    # B22: the round oak frame in japandi, scandinavian and organic modern; backlit rectangles in minimal and modern
    assert {BT.spec_of(f)[0]["mirror"] for f in ("japandi", "scandinavian", "organic modern")} == {"round_oak"}
    assert all(BT.spec_of(f)[0]["mirror"] == "backlit" and not BT.spec_of(f)[0]["mirror_round"]
               for f in ("minimal", "modern"))
    # one feature wall per room: the vanity's panel (B13) or the fluted wall behind the WC (B24), never both
    for fam in BT.FAMILY_BATH:
        spec = BT.spec_of(fam)[0]
        assert not (spec.get("panel") and spec.get("feature") == "wc_fluted"), fam
    spec, why = BT.spec_of("bauhaus")
    assert spec["family"] == BT.DEFAULT_FAMILY and "assumed" in why
    assert BT.spec_of("farmhouse")[0]["family"] == "rustic"


def test_the_decor_types_are_one_table_everywhere():
    assert P.BATH_DECOR_TYPES == BT.BATH_DECOR_TYPES == D.BATH_DECOR_TYPES
    assert set(BT.BATH_DECOR_TYPES) <= set(P.DECOR_TYPES) and set(BT.BATH_DECOR_TYPES) <= set(D.DECOR_TYPES)
    schema = json.loads((ROOT / "wenart" / "schema" / "building.schema.json").read_text(encoding="utf-8"))
    assert set(BT.BATH_DECOR_TYPES) <= set(schema["$defs"]["decor"]["properties"]["type"]["enum"])
    from wenart.polish import prompt as PR
    from wenart.vision_check import prompts as VP
    assert set(BT.BATH_DECOR_TYPES) <= set(PR.DECOR_WORDS)
    assert all(t in VP._DECOR_HINTS_M10 for t in BT.BATH_DECOR_TYPES)
    for key in ("led", "stone_light", "terrazzo", "towel"):
        assert key in P.MATERIAL_KEYS
    from wenart.blender import rest as R
    from wenart.blender import scene_checks as SC
    assert set(BT.WALL_BATH_DECOR) <= set(R.WALL_SUPPORT_TYPES) and set(BT.WALL_BATH_DECOR) <= set(SC.UNMEASURED_DECOR)
    assert "toilet_brush" in R.FLOOR_SUPPORT_TYPES and "toilet_brush" in SC.FLOOR_DECOR


# --------------------------------------------------------------------------
# The parts: real sizes, outward faces, inside the drawn footprint, one mesh per host
# --------------------------------------------------------------------------

def _inside(parts, w, d, tol=0.012):
    x0, y0, _z0, x1, y1, _z1 = P.parts_bbox(parts)
    return x0 >= -w / 2 - tol and x1 <= w / 2 + tol and y0 >= -d / 2 - tol and y1 <= d / 2 + tol


@pytest.mark.parametrize("name,parts,w,d", [
    ("wc", BT.wall_hung_wc_parts(0.445, 0.705, 0.8), 0.445, 0.705),
    ("slab", BT.stone_slab_vanity_parts(0.531, 0.342, 0.85), 0.531, 0.342),
    ("slab_double", BT.stone_slab_vanity_parts(1.2, 0.5, 0.85), 1.2, 0.5),
    ("fluted", BT.fluted_vanity_parts(1.4, 0.5, 0.85), 1.4, 0.5),
    ("fluted_square", BT.fluted_vanity_parts(0.8, 0.46, 0.85, "worktop", False), 0.8, 0.46),
    ("curved", BT.curved_vanity_parts(1.0, 0.5, 0.85), 1.0, 0.5),
    ("column", BT.open_column_parts(0.4, 0.35, 1.6), 0.4, 0.35),
    ("shower", BT.walk_in_shower_parts(0.9, 0.9, 2.0), 0.9, 0.9),
    ("shower_wide", BT.walk_in_shower_parts(1.2, 0.9, 2.0), 1.2, 0.9),
])
def test_every_piece_is_a_closed_product_inside_its_drawn_footprint(name, parts, w, d):
    assert parts and all(volume(p) > -1e-9 for p in parts), name            # every part wound outwards
    assert all(0 <= i < len(p["verts"]) for p in parts for f in p["faces"] for i in f)
    assert _inside(parts, w, d), name
    assert min(z for p in parts for _x, _y, z in p["verts"]) >= -1e-9
    # small: one mesh, built in one go (30 Oct 2026, UL166: the styling's real products, bath_objects, take ~1.5k;
    # UL184: glass bottles with the soap in them, printed labels, a curved basin with its waste, a turned vase ~1.2k more;
    # 31 Oct 2026, user on real04 run 20261030-181158-full: "This little items needs a lot better models ... more
    # detailed way": glass walls and contents, knurled collars, fluffy cotton, a woven basket: a column ~19k)
    assert sum(len(p["verts"]) for p in parts) < 30000


def test_the_wall_hung_wc_hangs_on_the_wall_with_its_flush_plate():
    parts = BT.wall_hung_wc_parts(0.445, 0.705, 0.8)
    bowl = [p for p in parts if p["role"] in ("bowl", "back")]
    assert max(y for p in bowl for _x, y, _z in p["verts"]) == pytest.approx(0.705 / 2.0, abs=0.002)   # on the wall
    assert min(z for p in bowl for _x, _y, z in p["verts"]) == pytest.approx(BT.WC_BOTTOM_M, abs=1e-6)  # floating
    plate = next(p for p in parts if p["role"] == "plate")
    zs = [z for _x, _y, z in plate["verts"]]
    assert min(zs) == pytest.approx(BT.FLUSH_PLATE_Z_M) and max(zs) - min(zs) == pytest.approx(0.164)
    assert plate["key"] == "handle" and sum(p["role"] == "button" for p in parts) == 2
    on_panel = BT.wall_hung_wc_parts(0.445, 0.705, 0.8, wall_offset=0.02)  # B24: on the fluted wall's face
    plate2 = next(p for p in on_panel if p["role"] == "plate")
    assert max(y for _x, y, _z in plate2["verts"]) == pytest.approx(0.705 / 2.0 - 0.02, abs=1e-6)
    assert [p["role"] for p in P.build_parts("toilet", 0.445, 0.705, 0.8)] == ["back", "bowl", "seat"]   # the M4 WC
    assert len(P.build_parts("toilet", 0.445, 0.705, 0.8, {"bath_look": {"wc": "wall_hung"}})) == len(parts)


def test_the_floating_vanities_have_their_top_basin_mixer_led_and_styling():
    lay = BT.vanity_layout(0.531, 0.342, 0.85)
    assert lay["top"] == pytest.approx((0.70, 0.85)) and lay["bottom_m"] == pytest.approx(0.32)   # 15 cm stone top
    parts = BT.stone_slab_vanity_parts(0.531, 0.342, 0.85)
    roles = {p["role"] for p in parts}
    assert {"top", "basin", "spout", "led", "towel", "jar", "front"} <= roles
    led = next(p for p in parts if p["key"] == "led")
    assert max(z for _x, _y, z in led["verts"]) == pytest.approx(lay["bottom_m"])        # under it, lighting the floor
    items = BT.vanity_items(0.531, 0.342, 0.85, {"vanity": "stone_slab"})
    assert "rolled towel" in items and {"dried stems in a vase", "soap dispenser"} <= set(items)   # B19: two clusters
    # B12: open lit end cubbies from 1.2 m only; B15 a vessel and a tall mixer; B21 the terrazzo apron
    wide = BT.vanity_layout(1.4, 0.5, 0.85, "fluted", "vessel")
    narrow = BT.vanity_layout(1.0, 0.5, 0.85, "fluted", "vessel")
    assert wide["end_cubbies"] and not narrow["end_cubbies"]
    fluted = BT.fluted_vanity_parts(1.4, 0.5, 0.85)
    assert sum(p["role"] == "led" for p in fluted) >= 5 and any(p["role"] == "basin" for p in fluted)
    assert any(p["role"] == "body" and p["key"] == "handle" for p in fluted)          # the tall deck mixer
    curved = BT.curved_vanity_parts(1.0, 0.5, 0.85)
    assert {"apron", "plinth", "groove"} <= {p["role"] for p in curved}
    assert all(p["key"] == "terrazzo" for p in curved if p["role"] in ("apron", "plinth"))     # B21: one material
    assert {p["key"] for p in curved if p["role"] in ("top", "body")} == {"worktop", "painted"}
    assert any(p["role"] == "basin" and p["key"] == "ceramic" for p in curved)                 # B23: a white vessel
    from shapely.geometry import Point, Polygon
    top = Polygon(BT.curved_outline(1.0, 0.25 - BT.APRON_T_M, -0.25)).buffer(0.003)
    on_top = [p for p in curved if p["role"] in ("bottle", "vase", "jar", "cap", "pump", "nozzle", "lid")]
    assert on_top and all(top.contains(Point(x, y)) for p in on_top for x, y, _z in p["verts"])   # B19 on the curve
    assert BT.vanity_fits(0.531, 0.342) is None and "wide" in BT.vanity_fits(0.35, 0.35)
    assert "deep" in BT.vanity_fits(0.6, 0.25)


def test_the_column_is_open_and_lit_with_a_styled_cubby_each():
    parts = BT.open_column_parts(0.3, 0.3, 1.6)
    n = BT.column_cubbies(1.6)
    assert n == 6 and sum(p["role"] == "led" for p in parts) == n               # an LED strip under every shelf
    assert BT.column_items(1.6)[:3] == ["towels", "pump bottles", "plant"]
    assert not any(p["role"] == "front" for p in parts)                         # open: no doors
    assert P.build_parts("tall_cabinet", 0.3, 0.3, 1.6, {"bath_look": {"column": "open_lit"}}) == parts


def test_the_walk_in_shower_slides_from_one_metre_and_has_its_fittings():
    narrow = {p["role"] for p in BT.walk_in_shower_parts(0.9, 0.9, 2.0)}
    wide = {p["role"] for p in BT.walk_in_shower_parts(1.2, 0.9, 2.0)}
    assert "roller" in wide and "roller" not in narrow and "profile" in narrow
    for roles in (narrow, wide):
        assert {"head", "arm", "hand_shower", "hose", "mixer", "knob", "drain", "glass"} <= roles


def test_the_mirrors_and_lights_are_the_familys():
    led = BT.decor_parts("mirror", 0.5, 0.03, 1.0, {"fixture": "led_mirror"})
    assert sum(p["key"] == "led" for p in led) == 4                              # B4: the inset band
    backlit = BT.decor_parts("mirror", 1.0, 0.03, 0.9, {"fixture": "backlit_mirror", "rounded": True})
    assert [p["key"] for p in backlit] == ["mirror", "led"]                      # B14: the halo behind the glass
    assert len(backlit[0]["verts"]) > 16                                         # rounded corners
    rnd = BT.decor_parts("mirror", 0.7, 0.04, 0.7, {"fixture": "round_mirror"})
    assert [p["key"] for p in rnd] == ["wood", "mirror"]                         # B22: the oak frame
    assert P.decor_parts("mirror", 0.5, 0.03, 1.0, {"fixture": "led_mirror"}) == led
    sq = P.decor_parts("ceiling_light", 0.1, 0.1, 0.012, {"fixture": "downlight", "trim": "square_dark"})
    assert sq[0]["key"] == "dark" and len(sq[0]["verts"]) == 8                  # B9: a square black trim
    assert BF.mirror_box({"size": [0.5, 0.03], "fixture": "led_mirror"}) == [0.5, 0.03, 1.0]
    assert BF.mirror_box({"size": [1.0, 0.03], "fixture": "backlit_mirror"})[2] == pytest.approx(BT.BACKLIT_MIRROR_H)
    assert BF.mirror_box({"size": [0.6, 0.03], "fixture": "round_mirror"})[0] == BF.mirror_box(
        {"size": [0.6, 0.03], "fixture": "round_mirror"})[2]
    assert BF.mirror_box({"size": [0.5, 0.03]})[2] == pytest.approx(0.5 * BF.MIRROR_ASPECT)   # the framed one stays


# --------------------------------------------------------------------------
# 1. The layout stage: the fixtures' looks, the drawn footprints kept
# --------------------------------------------------------------------------

def test_the_layout_gives_each_fixture_its_familys_look_and_keeps_every_footprint():
    src = bathroom(toilet(), basin(), shower(), column())
    b = copy.deepcopy(src)
    _b, recs = BD.plan_building(b, style_of("scandinavian"))
    by = {f["id"]: f for f in b["furniture"]}
    assert BT.made_to_measure(by["t1"]) == "wc" and by["t1"]["bath_look"]["finish"] == "black"
    assert BT.made_to_measure(by["w1"]) == "vanity" and by["w1"]["bath_look"]["vanity"] == "stone_slab"
    assert BT.made_to_measure(by["s1"]) == "shower" and BT.made_to_measure(by["c1"]) == "column"
    for f, g in zip(src["furniture"], b["furniture"]):
        assert f["footprint"] == g["footprint"] and f["type"] == g["type"] and f["front_deg"] == g["front_deg"]
        assert g["bath_look"]["reason"] and g["bath_look"]["source"] == "inferred"
    assert LO.check(src, b, "complete") == []                                   # fixed equipment: only its look
    assert b["bath_details"]["rooms"][ROOM]["finish"] == "black" == BD.room_finish(b, ROOM)   # B20
    assert recs[0]["room_id"] == ROOM and recs[0]["feature"] in ("wc_fluted", None)


def test_a_classic_family_keeps_its_close_coupled_wc_and_a_small_basin_stays_as_drawn():
    b = bathroom(toilet(), basin(size=(0.36, 0.30)))
    BD.plan_building(b, style_of("classic"))
    by = {f["id"]: f for f in b["furniture"]}
    assert by["t1"]["bath_look"]["wc"] == "close_coupled" and BT.made_to_measure(by["t1"]) is None
    assert by["w1"]["bath_look"]["vanity"] == "as_drawn" and BT.made_to_measure(by["w1"]) is None
    b2 = bathroom(basin(size=(0.36, 0.30)))
    _b, recs = BD.plan_building(b2, style_of("modern"))
    assert "wide" in recs[0]["pieces"]["w1"]["why"] and BT.made_to_measure(b2["furniture"][0]) is None


def test_the_fluted_wall_goes_behind_the_wall_hung_wc_and_it_hangs_on_its_face():
    b, _st = full("japandi")
    rec = b["bath_details"]["rooms"][ROOM]
    assert rec["feature"] == "wc_fluted" and rec["feature_panel"]["material"] == "fluted_dark"
    wc = next(f for f in b["furniture"] if f["id"] == "t1")
    assert wc["bath_look"]["wall_offset_m"] == BT.FLUTED_WALL_T_M
    assert rec["feature_panel"]["width"] >= 0.4 + BD.WC_PANEL_MIN_EXTRA_M
    b2, _st2 = full("modern")                          # B13: a fluted vanity's terrazzo panel, no fluted wall
    rec2 = b2["bath_details"]["rooms"][ROOM]
    assert rec2["feature"] in ("vanity_panel", None) and "feature_panel" not in rec2


def test_the_fit_builds_the_made_to_measure_pieces_by_design():
    b, st = full("scandinavian")
    by = {f["id"]: f for f in b["furniture"]}
    vanity = F.bath_made_fit(by["w1"], "scandinavian", "relaxed", st)
    assert vanity["method"] == "module" and vanity["module_plan"]["variant"] == "stone_slab"
    assert vanity["by_design"] and vanity["library_gap"]["step"] == "module"
    assert vanity["module_plan"]["top_m"] == pytest.approx(0.85)
    sh = F.bath_made_fit(by["s1"], "scandinavian", "relaxed", st)
    assert sh["method"] == "module" and sh["module_plan"]["variant"] == "walk_in"
    for pid in ("t1", "c1"):
        asset = F.bath_made_fit(by[pid], "scandinavian", "relaxed", st)
        assert asset["method"] == "parametric" and asset["by_design"] and asset["library_gap"]
    assert C.by_design_parametric(by["c1"]) and F.bath_made_fit(M.fp("x", "sofa", (1, 1), (2, 1)), None,
                                                                 "relaxed") is None
    assert F.fit_decor_item({"type": "mirror", "size": [0.5, 0.03], "fixture": "round_mirror"}, None) is None
    parts = MOD.module_parts(vanity["module_plan"])
    assert any(p["key"] == "led" for p in parts) and MOD.plan_bbox(vanity["module_plan"])[0] == pytest.approx(0.6)


# --------------------------------------------------------------------------
# 2. The decor stage: the accessories
# --------------------------------------------------------------------------

def test_the_decor_stage_gives_the_bathroom_its_set_and_the_review_is_clean():
    b, st = full("scandinavian")
    before, _n = BD.review(dict(b, decor=[{"type": "plant", "room_id": "elsewhere"}]))
    assert {f["missing"] for f in before} >= {"toilet_paper_holder", "toilet_brush", "towel_rail", "towel_shelf",
                                              "mirror"}
    b["decor"] = [{"id": "dec_L0_090", "kind": "decor", "type": "mirror", "level_id": "L0", "room_id": ROOM,
                   "anchor_ids": ["w1"], "center": [1.2, 2.58], "wall_point": [1.2, 2.6], "rotation_deg": 180.0,
                   "size": [0.54, 0.04], "asset": {"asset_id": "abo_x", "method": "library"}},
                  {"id": "dec_L0_091", "kind": "decor", "type": "ceiling_light", "level_id": "L0", "room_id": ROOM,
                   "center": [1.5, 1.3, 2.58], "size": [0.4, 0.4, 0.12], "rule": "decor.ceiling_lights"}]
    _b, notes = BD.dress(b, st, new_ids())
    items = {d["type"]: d for d in b["decor"]}
    assert {"toilet_paper_holder", "toilet_brush", "towel_rail", "towel_shelf", "feature_panel"} <= set(items)
    holder = items["toilet_paper_holder"]
    assert holder["center"][2] == pytest.approx(BT.paper_holder_bottom())      # UL183: the roll's axis at 0.70 m
    assert holder["anchor_ids"] == ["t1"] and holder["source"] == "added_by_ai" and "B2" in holder["reason"]
    assert items["toilet_brush"]["center"][2] == 0.0 and holder["colour"] == "black"     # the family's finish
    assert all(d.get("towel_colour") == "sage" for d in b["decor"] if d.get("rule") == BD.RULE)   # B26
    assert items["mirror"]["fixture"] == "round_mirror" and items["mirror"]["asset"] is None        # B22
    assert items["ceiling_light"]["fixture"] == "downlight" and items["ceiling_light"]["trim"] == "square_dark"
    from shapely.geometry import Point
    rail = items["towel_rail"]
    sh = next(f for f in b["furniture"] if f["id"] == "s1")
    assert not BD._poly(sh).contains(Point(rail["center"][:2]))                 # never in the shower
    after, n = BD.review(b)
    assert n == 1 and not [f for f in after if f["missing"] in ("toilet_paper_holder", "toilet_brush", "towel_rail",
                                                                  "towel_shelf", "mirror", "mirror_kind")], after
    count = len(b["decor"])
    BD.dress(b, st, new_ids())                                                   # idempotent
    assert len(b["decor"]) == count


def test_the_cove_light_runs_over_the_vanity_wall_and_wraps_into_the_shower_corner():
    b, st = full("modern")
    BD.dress(b, st, new_ids())
    coves = [d for d in b["decor"] if d["type"] == "cove_light"]
    assert coves and coves[0]["anchor_ids"] == ["w1"]
    assert coves[0]["center"][2] == pytest.approx(2.7 - BT.COVE_DROP_M)
    assert len(coves) == 1 or coves[1]["wraps"] == coves[0]["id"]              # B17 where the band meets the corner
    b2, st2 = full("industrial")                                                 # open ceilings: no cove
    BD.dress(b2, st2, new_ids())
    assert not [d for d in b2["decor"] if d["type"] == "cove_light"]


def test_the_decor_items_build_into_their_boxes():
    for dtype in BT.BATH_DECOR_TYPES:
        size = {"toilet_paper_holder": BT.PAPER_HOLDER_SIZE, "toilet_brush": BT.TOILET_BRUSH_SIZE,
                "towel_rail": BT.TOWEL_RAIL_SIZE, "towel_shelf": BT.TOWEL_SHELF_SIZE, "towel_bar": BT.TOWEL_BAR_SIZE,
                "feature_panel": (1.0, 0.02, 2.7), "cove_light": (1.5, 0.3, 0.12),
                "install_wall": (1.6, BT.INSTALL_WALL_D_M, BT.INSTALL_WALL_H_M)}[dtype]      # UL205
        parts = P.decor_parts(dtype, *size, {"material": "fluted_dark"} if dtype == "feature_panel" else None)
        x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
        assert x1 - x0 <= size[0] + 1e-9 and y1 - y0 <= size[1] + 1e-9 and z1 - z0 <= size[2] + 1e-9, dtype
        assert z0 == pytest.approx(0.0, abs=1e-9), dtype
        assert all(volume(p) > -1e-9 for p in parts), dtype
    towels = [p for p in P.decor_parts("towel_rail", *BT.TOWEL_RAIL_SIZE) if p["role"] == "towel"]
    assert towels and all(p["key"] == BF.TOWEL_DECOR_KEY for p in towels)


# --------------------------------------------------------------------------
# The build hooks (pure parts of them)
# --------------------------------------------------------------------------

def test_the_build_takes_the_finish_the_towels_and_the_familys_wet_tiles():
    design, notes = LK.design_for({"type": "toilet", "bath_look": {"finish": "brass", "towel_colour": "navy"}}, {})
    assert design["handle"] == "brass" and design["towel_colour"] == "navy" and notes
    over, _n = BF.design_overrides(design, "toilet")
    assert over["handle"]["slug"] == "metal_brass" and over["towel"]["colour"] == "navy"
    st = style_of("japandi")
    assumed = []
    BU.family_wet_tiles(st, assumed)                          # build.load_style: the scene's profile names the tiles
    assert st["wet_walls"]["material"] == BT.LARGE_TILE_SLUG and st["wet_walls"]["tile_size_m"] == [0.6, 1.2]
    assert LK.wet_wall_look(st)["colour"] == "sand" and LK.wet_wall_look(st)["params"]["tile_size_m"] == [0.6, 1.2]
    assert st[BU.WET_WALLS_BRIEF] == {"material": "tiles_light"} and len(assumed) == 1   # the kitchen splashback's
    assert BU.family_wet_tiles(st, assumed) and len(assumed) == 1                # idempotent
    slot, wet = SH.floor_style({"room_type": "bathroom"}, st)
    assert wet and slot["material"] == BT.LARGE_TILE_SLUG and slot["colour"] == "taupe"
    assert SH.floor_style({"room_type": "kitchen"}, st)[0]["material"] == "tiles_light"   # the kitchen's own helper
    brief = dict(style_of("japandi"), wet_walls={"material": "tiles_zellige", "colour": "sage"})
    BU.family_wet_tiles(brief, assumed)
    assert brief["wet_walls"]["material"] == "tiles_zellige" and len(assumed) == 1  # the brief's tiles win
    assert BU.family_wet_tiles({"wet_walls": {"material": "tiles_light"}}, assumed) and len(assumed) == 1  # no family
    keys, _a = BF.style_material_keys({"floor": {"material": "wood_oak_light"}})
    assert keys["led"][0] == BF.LED_SLUG and keys["terrazzo"][0] == "terrazzo"


# --------------------------------------------------------------------------
# 3. The checks M26 and U30, the lesson
# --------------------------------------------------------------------------

def test_m26_and_u30_are_registered_and_flag_a_bare_bathroom():
    from wenart.agent import causes as CS
    from wenart.audit import kinds as K
    from wenart.audit import lessons as LS
    from wenart.blender import model_review as MR
    b = bathroom(toilet(), basin())
    b["decor"] = [{"type": "plant", "room_id": ROOM, "center": [0.3, 0.3]}]
    assert "M26" in MR.CHECKS and CS.CHECK_CAUSE["M26"] == "decor_look"
    assert K.kind_of({"check": "M26"}) == "taste" == K.kind_of({"check": "U30"})
    assert LS.CHECK_LESSONS["U30"] == ("UL114", "UL123", "UL124")
    assert ("U30", LS.bathroom_sets) in LS.BUILDING_CHECKS
    got = LS.audit(b, None)
    u30 = [f for f in got["findings"] if f["check"] == "U30"]
    assert got["checked"]["U30"] == len(u30) >= 4
    rec = MR.review(b)
    assert rec["checks"]["M26"]["status"] == "ok" and rec["checks"]["M26"]["failed"] >= 4
    m26 = next(f for f in rec["findings"] if f["check"] == "M26")
    assert m26["kind"] == "taste" and m26["severity"] == "minor"


def test_lessons_ul114_ul123_ul124_are_built_with_their_checks():
    data = json.loads((ROOT / "wenart" / "blender" / "architect_lessons.json").read_text(encoding="utf-8"))
    items = data["lessons"] if isinstance(data, dict) else data
    by = {x["id"]: x for x in items}
    for lid in ("UL114", "UL123", "UL124"):
        if lid not in by:
            continue                                   # a lesson the coordinator adds on its branch
        assert by[lid]["status"] == "built" and by[lid]["checks"] == ["build"], lid
        assert "M26" in by[lid]["lesson"] and "U30" in by[lid]["lesson"], lid


# --------------------------------------------------------------------------
# real06 (run 20261029-100801-full): what each bathroom gets
# --------------------------------------------------------------------------

@pytest.mark.skipif(not REAL06.exists(), reason="real06's run 20261029-100801-full is not in the main repository")
def test_real06_bathrooms_get_their_scandinavian_set():
    b = json.loads(REAL06.read_text(encoding="utf-8"))
    style = json.loads(REAL06_STYLE.read_text(encoding="utf-8")) if REAL06_STYLE.exists() else style_of("scandinavian")
    src = copy.deepcopy(b)
    _b, recs = BD.plan_building(b, style)
    counters = {}

    def new_id(level):
        counters[level] = counters.get(level, 900) + 1
        return f"dec_{level}_{counters[level]}"
    _b, notes = BD.dress(b, style, new_id)
    print()
    for r in recs:
        rid = r["room_id"]
        print(f"{rid} ({r['family']}, {r['finish']}, towels {r['towel_colour']}): feature {r['feature']} "
              f"({r.get('feature_why')})")
        for pid, pr in r["pieces"].items():
            print(f"    {pid}: {pr.get('why')}")
        got = [d for d in b["decor"] if d.get("room_id") == rid and (d.get("rule") == BD.RULE or d.get("bath_detail")
                                                                     or d.get("fixture") == "downlight")]
        for d in got:
            print(f"    + {d['type']} {d.get('fixture') or ''} at {[round(v, 2) for v in d['center']]}: "
                  f"{d['reason'][:100]}")
    for n in notes:
        print("    note:", n)
    assert {r["room_id"] for r in recs} == {"r_L0_banyo", "r_L1_banyo", "r_L1_dus"}
    for f, g in zip(src["furniture"], b["furniture"]):
        assert f["footprint"] == g["footprint"] and f["type"] == g["type"]          # drawn fixtures stay
    by = {f["id"]: f for f in b["furniture"]}
    assert all(BT.made_to_measure(by[p]) == "wc" for p in ("f_L0_024", "f_L1_021", "f_L1_022"))
    assert all(BT.made_to_measure(by[p]) == "vanity" for p in ("f_L0_026", "f_L1_023", "f_L1_027"))
    assert BT.made_to_measure(by["f_L1_018"]) == "shower"
    rails = [d for d in b["decor"] if d.get("type") == "towel_rail"]
    assert {d["room_id"] for d in rails} == {"r_L0_banyo", "r_L1_banyo", "r_L1_dus"}
    holders = {d["anchor_ids"][0] for d in b["decor"] if d.get("type") == "toilet_paper_holder"}
    assert {"f_L0_024", "f_L1_021"} <= holders


def test_an_accessory_without_an_anchor_has_no_anchor_list():
    """real04 run 20261029-180458-full stopped in the decor stage: towel rails and shelves on a free wall carried
    ``anchor_ids: []`` and the building schema wants at least one piece or no key."""
    from wenart.furniture import bath_details as BDX

    room = {"id": "r_bath", "level_id": "L0"}
    spec = {"finish": next(iter(BDX.BT.FINISH_COLOUR)), "towel_colour": "white"}
    free = BDX._item(room, "towel_rail", (1.0, 1.0), 0.0, (0.5, 0.1, 0.8), "a towel rail on a free wall", spec,
                     lambda level: "dec_L0_900")
    held = BDX._item(room, "toilet_paper_holder", (1.0, 1.0), 0.0, (0.15, 0.1, 0.12), "beside the WC", spec,
                     lambda level: "dec_L0_901", anchors=["f_wc"])
    assert "anchor_ids" not in free and held["anchor_ids"] == ["f_wc"]
