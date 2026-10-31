"""31 Oct 2026, the user's review of real04 run 20261030-181158-full (a bathroom's open shelf column): "This little
items needs a lot better models, check the library of similar things exist to use if not create them with better
texture and more detailed way" (two cube-shaped bottles with black pump heads, a basket that read like a ribbed plastic
bowl, cotton balls as plain white spheres, a soap dish, a reed diffuser, a lidded jar). General rules; real04 is only
the test case.

- The library first (``wenart.furniture.small_items``): a small item of a host (a column's cubbies, a vanity, a towel
  shelf, an installation wall's niches) takes an audited library model of its kind that is rated good (the user's rank
  from 6, else vision quality from 4) and fits its reserved box; else our model and a ``library_gap``. The builders
  leave a library slot for a picked kind (``bath_objects.placed``), the build places the model in it, the credits and
  the licence flags read the picks.
- Else our models with the details of the real product and real materials (``bath_objects``, ``SMALL_ITEM_KEYS``,
  ``materials.SMALL_ITEM_LOOKS``); the rattan key takes its Wicker005 photo.
Pure tests (no ``bpy``)."""
from __future__ import annotations

import copy
import json
import math
from types import SimpleNamespace

import pytest

import test_bathroom_details_20261029 as TB
from wenart.blender import bath_objects as BO
from wenart.blender import bath_parts as BT
from wenart.blender import furniture as BF
from wenart.blender import materials as M
from wenart.blender import modules as MOD
from wenart.blender import parametric as P
from wenart.furniture import catalog as C
from wenart.furniture import fit as F
from wenart.furniture import small_items as SI
from wenart.furniture import user_ranks as UR
from wenart.polish import prompt as PR
from wenart.report import final as FR
from wenart.run import copy as CP
from wenart.style import vocabulary as V


def _basket(**kw):
    e = {"id": "objaverse_basket_good", "type": "decor_basket", "kind": "decor", "decor_type": "basket",
         "source": "objaverse", "licence": "CC-BY-4.0", "glb": "models/objaverse/b.glb", "bbox_m": [0.30, 0.28, 0.12],
         "audit": {"status": "keep", "reasons": [], "vision_quality": 4}, "real_product": True, "styles": ["neutral"],
         "title": "Seagrass towel basket", "author": "someone", "source_url": "https://example.org/b",
         "attribution": "\"Seagrass towel basket\" by someone, CC BY 4.0"}
    e.update(kw)
    return e


def _dispenser(**kw):
    e = {"id": "3dwh_dispenser", "type": "untyped_object", "kind": "object", "source": "3dwh", "licence": "CC-BY-4.0",
         "glb": "models/3dwh/d.glb", "bbox_m": [0.07, 0.07, 0.19], "real_product": True, "styles": [],
         "audit": {"status": "keep", "reasons": [], "vision_quality": 4}, "title": "Ceramic soap dispenser"}
    e.update(kw)
    return e


def _cat(decor=(), extras=()):
    return SimpleNamespace(decor=list(decor), extras=list(extras), entries=[])


def _roles(parts) -> set:
    return {p["role"] for p in parts}


# --------------------------------------------------------------------------
# A. the library first: the choice
# --------------------------------------------------------------------------

def test_a_good_basket_in_the_library_takes_the_columns_basket_and_the_rest_are_gaps():
    slots = SI.host_slots("column", 0.3, 0.3, 1.6)
    kinds = {s["kind"] for s in slots}
    assert {"pump_bottle", "potted_plant", "apothecary_jar", "reed_diffuser", "woven_basket", "perfume_bottle",
            "soap_dish"} <= kinds
    rec = SI.plan(slots, _cat(decor=[_basket()]), "modern", "relaxed")
    pick = rec["picks"]["woven_basket"]
    assert pick["asset_id"] == "objaverse_basket_good" and pick["method"] == "library" and pick["small_item"] == \
        "woven_basket"
    assert pick["licence_flag"] == "none" and pick["commercial_safe"] is True and pick["attribution"]
    assert all(f["fill"] >= SI.MIN_FILL for f in pick["slot_fits"])
    assert set(rec["gaps"]) == kinds - {"woven_basket"} and rec["slots"]["pump_bottle"] == 3
    assert all("no audited library model" in g["why"] for g in rec["gaps"].values())
    assert SI.assets_of(rec) == [pick] and [g["type"] for g in SI.gaps_of(rec)] == sorted(rec["gaps"])
    assert SI.plan([], _cat(), "modern", "relaxed") is None


def test_a_weak_an_open_or_a_misfitting_model_leaves_our_model_with_a_library_gap(monkeypatch):
    box = [s["box"] for s in SI.host_slots("column", 0.3, 0.3, 1.6) if s["kind"] == "woven_basket"]
    weak = _basket(id="b_weak", audit={"status": "keep", "reasons": [], "vision_quality": 3})
    lid = _basket(id="b_lid", open_parts=True)
    tall = _basket(id="b_tall", bbox_m=[0.37, 0.33, 0.23])            # a laundry basket: squeezed it is no towel basket
    fake = _basket(id="b_fake", real_product=False)
    asset, note = SI.pick("woven_basket", box, _cat(decor=[weak]), "modern", "relaxed")
    assert asset is None and "rated good" in note["why"] and "vision quality 3" in note["refused"]["b_weak"]
    asset, note = SI.pick("woven_basket", box, _cat(decor=[lid, tall, fake]), "modern", "relaxed")
    assert asset is None and "suits the item" in note["why"]
    assert "open_parts" in note["refused"]["b_lid"] and "reserved box" in note["refused"]["b_tall"]
    assert "real product" in note["refused"]["b_fake"]
    # the user's rank decides before the vision quality: 7 makes an unrated model good, 4 a vision-5 model weak
    unrated = _basket(id="b_unrated", audit={"status": "keep", "reasons": []})
    five = _basket(id="b_five", audit={"status": "keep", "reasons": [], "vision_quality": 5})
    monkeypatch.setattr(UR, "rank_of", lambda e, path=None: {"b_unrated": 7, "b_five": 4}.get(e.get("id")
                                                                                               or e.get("asset_id")))
    asset, note = SI.pick("woven_basket", box, _cat(decor=[unrated, five]), "modern", "relaxed")
    assert asset["asset_id"] == "b_unrated" and asset["user_rank"] == 7 and "rank 4" in note["refused"]["b_five"]


def test_a_titled_kind_needs_its_name_in_the_title_and_commercial_mode_its_licence():
    box = [s["box"] for s in SI.host_slots("vanity", 0.531, 0.342, 0.85, {"vanity": "stone_slab"})
           if s["kind"] == "pump_bottle"]
    assert box
    good = _dispenser()
    vase = _dispenser(id="3dwh_vase", type="decor_vase", kind="decor", title="Tall ceramic vase")
    jar_word = _dispenser(id="3dwh_jar", title="Jars of dispensers")          # "dispensers" is no "soap dispenser"
    asset, note = SI.pick("pump_bottle", box, _cat(extras=[good, vase, jar_word]), "modern", "relaxed")
    assert asset["asset_id"] == "3dwh_dispenser" and note["candidates"] == 1
    assert SI.names_item(good, "pump_bottle") == "soap dispenser" and SI.names_item(vase, "pump_bottle") is None
    nc = _dispenser(id="3dwh_nc", licence="CC-BY-NC-4.0")
    assert SI.pick("pump_bottle", box, _cat(extras=[nc]), "modern", "relaxed")[0]["asset_id"] == "3dwh_nc"
    asset, note = SI.pick("pump_bottle", box, _cat(extras=[nc]), "modern", "commercial")
    assert asset is None and "no audited" in note["why"]


def test_the_slot_fit_is_one_uniform_scale_turned_when_that_fills_better():
    e = {"bbox_m": [0.13, 0.30, 0.10]}
    f = SI.slot_fit(e, "woven_basket", [0.30, 0.15, 0.12])
    assert f["turned_deg"] == 90.0 and f["scale"] == pytest.approx(1.0) and f["fill"] == pytest.approx(0.8333, abs=1e-3)
    assert SI.slot_fit({"bbox_m": [0.6, 0.6, 0.1]}, "woven_basket", [0.3, 0.12, 0.12]) is None     # fills too little
    assert SI.slot_fit({"bbox_m": [2.0, 1.8, 0.8]}, "pump_bottle", [0.06, 0.06, 0.18]) is None      # not a bottle


def test_the_committed_library_has_no_good_model_for_the_bathrooms_small_items_today():
    """The library check of the review: 28 baskets (one rated good, its lid off and too tall for the cubby), 46 small
    plants and 25 candles (none rated good), no soap dispenser, perfume, apothecary jar, diffuser or soap dish: every
    kind keeps our detailed model with its gap note until the user ranks a model good."""
    cat = C.load()
    slots = SI.host_slots("column", 0.3, 0.3, 1.6) + SI.host_slots("vanity", 0.531, 0.342, 0.85,
                                                                     {"vanity": "stone_slab"})
    rec = SI.plan(slots, cat, "modern", "relaxed")
    assert not rec["picks"] and set(rec["gaps"]) == set(rec["slots"])
    assert rec["gaps"]["woven_basket"]["candidates"] >= 10 and rec["gaps"]["potted_plant"]["candidates"] >= 10
    assert rec["gaps"]["pump_bottle"]["candidates"] == 0


# --------------------------------------------------------------------------
# B. the library slots in the hosts
# --------------------------------------------------------------------------

def test_a_picked_kind_leaves_its_reserved_box_as_a_library_slot_and_no_mesh():
    pick = {"woven_basket": {"asset_id": "objaverse_basket_good"}}
    every = P.library_slots(BT.open_column_parts(0.3, 0.3, 1.6, BO.ALL))
    parts = BT.open_column_parts(0.3, 0.3, 1.6, {"picks": pick})
    plain = BT.open_column_parts(0.3, 0.3, 1.6)
    slots = P.library_slots(parts)
    assert [s["kind"] for s in slots] == ["woven_basket"] and slots[0]["asset_id"] == "objaverse_basket_good"
    assert slots[0]["box"] == next(s["box"] for s in every if s["kind"] == "woven_basket")
    assert not {"stake", "rim"} & _roles(parts) and {"stake", "rim"} <= _roles(plain)
    slot_part = next(p for p in parts if p["role"] == P.SLOT_ROLE)
    assert slot_part["faces"] == [] and len(slot_part["verts"]) == 8
    verts, faces, keys = P.world_mesh(parts, (0.0, 0.0), 0.0, 0.0)
    assert len(verts) == sum(len(p["verts"]) for p in parts if p["role"] != P.SLOT_ROLE) and BO.SLOT_KEY not in keys
    # the vanity (its module plan), the towel shelf and the installation wall carry them the same way
    vanity = BT.vanity_parts(0.531, 0.342, 0.85, {"vanity": "stone_slab"}, {"pump_bottle": {"asset_id": "x"}})
    assert {s["kind"] for s in P.library_slots(vanity)} == {"pump_bottle"} and "nozzle" not in _roles(vanity)
    shelf = P.decor_parts("towel_shelf", *BT.TOWEL_SHELF_SIZE, {"small_items": {"picks": {"apothecary_jar": {}}}})
    assert [s["kind"] for s in P.library_slots(shelf)] == ["apothecary_jar"] and "jar" not in _roles(shelf)
    wall = P.decor_parts("install_wall", 2.2, BT.INSTALL_WALL_D_M, BT.INSTALL_WALL_H_M,
                         {"wc_x": 0.45, "small_items": {"picks": {"pump_bottle": {}}}})
    assert {s["kind"] for s in P.library_slots(wall)} == {"pump_bottle"}
    assert P.library_slots(plain) == [] and BO.picks_of(None) == {} and BO.picks_of(BO.ALL) is BO.ALL


def test_the_bench_vanity_plan_is_built_by_its_own_builder():
    """31 Oct 2026: the bench variant of the bath set fell through to two plain module boxes."""
    look = {"vanity": "bench", "basin": "vessel_wall", "top_key": "wood", "top_m": 0.85, "made_to_measure": True}
    plan = {"builder": "bath_set", "type": "washbasin", "variant": "bench", "bath_look": look, "top_m": 0.85,
            "footprint_m": [0.8, 0.55], "height_m": 0.85, "modules": [], "small_items": None}
    parts = MOD._bath_parts(plan)
    assert {"leg", "foot", "shelf", "basin", "stake", "rim"} <= _roles(parts)


# --------------------------------------------------------------------------
# C. the fit, the report, the credits and the licence flags
# --------------------------------------------------------------------------

def test_the_fit_records_the_small_items_of_the_column_the_vanity_and_the_towel_shelf():
    b, st = TB.full("scandinavian")
    by = {f["id"]: f for f in b["furniture"]}
    cat = _cat(decor=[_basket()], extras=[_dispenser()])
    col = F.bath_made_fit(by["c1"], "scandinavian", "relaxed", st, cat)
    assert col["method"] == "parametric" and col["small_items"]["picks"]["woven_basket"]["asset_id"] == \
        "objaverse_basket_good"
    assert set(col["small_items"]["picks"]) == {"woven_basket", "pump_bottle"}       # the dispenser fits its bottles
    built = P.build_parts("tall_cabinet", 0.4, 0.35, 1.6, dict(by["c1"], asset=col))
    assert sorted(s["kind"] for s in P.library_slots(built)) == ["pump_bottle"] * 3 + ["woven_basket"]
    van = F.bath_made_fit(by["w1"], "scandinavian", "relaxed", st, cat)
    assert van["module_plan"]["small_items"] is van["small_items"]
    assert set(van["small_items"]["picks"]) == {"pump_bottle"}
    assert {s["kind"] for s in P.library_slots(MOD.module_parts(van["module_plan"]))} == {"pump_bottle"}
    assert F.bath_made_fit(by["t1"], "scandinavian", "relaxed", st, cat).get("small_items") is None   # the WC
    item = {"id": "d_shelf", "type": "towel_shelf", "size": list(BT.TOWEL_SHELF_SIZE)}
    assert F.fit_decor_item(item, _cat(), "scandinavian", mode="relaxed") is None
    assert set(item["small_items"]["gaps"]) == {"apothecary_jar"} and not item["small_items"]["picks"]
    before = {"furniture": [], "decor": [{"id": "d_shelf", "type": "towel_shelf", "size": [0.6, 0.25, 0.4]}]}
    after = copy.deepcopy(before)
    after["decor"][0]["small_items"] = item["small_items"]
    F.assert_only_assets_changed(before, after)                       # the fit's own record


def _building_with_picks():
    rec = SI.plan(SI.host_slots("column", 0.3, 0.3, 1.6), _cat(decor=[_basket()]), "modern", "relaxed")
    shelf = SI.plan(SI.host_slots("towel_shelf", *BT.TOWEL_SHELF_SIZE), _cat(), "modern", "relaxed")
    return {"project": {"id": "p"}, "furniture": [
        {"id": "c1", "type": "tall_cabinet", "room_id": "r", "source": "added_by_ai", "status": "verified",
         "footprint": {"center": [0, 0], "size": [0.3, 0.3], "rotation_deg": 0.0},
         "asset": {"method": "parametric", "asset_id": "parametric:tall_cabinet", "library": "parametric",
                   "licence": "n/a", "fit_scale": [1.0, 1.0, 1.0], "bbox_m": [0.3, 0.3, 1.6], "small_items": rec}}],
        "decor": [{"id": "d_shelf", "type": "towel_shelf", "size": [0.6, 0.25, 0.4], "small_items": shelf}]}


def test_the_report_the_credits_and_the_licence_flags_read_the_picks(tmp_path):
    building = _building_with_picks()
    assert [r["host"] for r in SI.records(building)] == ["c1", "d_shelf"]
    text = F.fit_report(building)
    assert "## Small items" in text and "woven_basket: library model objaverse_basket_good (1 host(s): c1)" in text
    assert "apothecary_jar: library gap, our model" in text
    (tmp_path / "building_final.json").write_text(json.dumps(building), encoding="utf-8")
    credits = CP.project_credits(tmp_path)
    basket = next(c for c in credits if c["asset_id"] == "objaverse_basket_good")
    assert basket["pieces"] == [("c1", "tall_cabinet")] and "Seagrass towel basket" in basket["credit"]
    scene = {"objects": [{"wenart_id": "c1", "pass_index": 4, "asset": {"method": "parametric"},
                          "library_items": [{"kind": "woven_basket",
                                             "asset": {"asset_id": "3dwh_x", "licence": "3DWH-UNREVIEWED",
                                                       "licence_flag": "non_commercial", "method": "library"}}]}]}
    by_index = FR.assets_by_index(scene)
    assert by_index[4] == [("c1", scene["objects"][0]["library_items"][0]["asset"])]
    cs = FR.commercial_safe_of_view({"index_values": [4]}, by_index)
    assert cs["safe"] is False and cs["flagged"] == ["3dwh_x"]


# --------------------------------------------------------------------------
# D. the build's pure helpers
# --------------------------------------------------------------------------

def test_a_pick_without_its_file_falls_back_to_our_model_and_a_slot_is_placed_in_the_hosts_frame(tmp_path):
    (tmp_path / "models").mkdir()
    (tmp_path / "models" / "b.glb").write_bytes(b"glTF")
    lib = {"method": "library", "library": "objaverse", "licence": "CC0"}
    rec = {"rule": SI.RULE, "picks": {"woven_basket": dict(lib, asset_id="b", glb="models/b.glb"),
                                      "pump_bottle": dict(lib, asset_id="d", glb="models/d.glb")},
           "gaps": {"soap_dish": {"why": "none"}}}
    out, notes = BF.resolved_small_items(rec, str(tmp_path))
    assert set(out["picks"]) == {"woven_basket"} and "cannot be built" in out["gaps"]["pump_bottle"]["why"]
    assert set(out["gaps"]) == {"pump_bottle", "soap_dish"} and len(notes) == 1
    assert BF.resolved_small_items(None, str(tmp_path)) == (None, [])
    s, turned = BF.slot_scale({"bbox_m": [0.10, 0.30, 0.10]}, [0.30, 0.12, 0.12])
    assert turned == 90.0 and s == pytest.approx(1.0)
    centre, z = BF.slot_world({"center": [0.1, 0.0], "z": 0.5}, {"center": [2.0, 1.0], "rotation_deg": 90.0}, 0.2)
    assert centre == pytest.approx([2.0, 1.1]) and z == pytest.approx(0.7)


# --------------------------------------------------------------------------
# E. our models: the real product's details and materials
# --------------------------------------------------------------------------

def test_the_pump_bottle_is_glass_with_its_soap_dip_tube_knurled_collar_bent_nozzle_and_printed_label():
    r, h = 0.03, 0.18
    parts = BO.pump_bottle(0.0, 0.0, 0.0, r, h, "terracotta", "dark")
    assert {"bottle", "contents", "tube", "cap", "pump", "nozzle", "label", "print"} <= _roles(parts)
    bottle = next(p for p in parts if p["role"] == "bottle")
    soap = next(p for p in parts if p["role"] == "contents")
    assert bottle["key"] == BO.GLASS["amber"] and soap["key"] == BO.SOAP_GEL_KEY
    assert max(math.hypot(x, y) for x, y, _z in soap["verts"]) < r - BO.GLASS_WALL_M
    assert min(z for _x, _y, z in soap["verts"]) > BO.GLASS_BASE_M                     # on the thick glass base
    collar = next(p for p in parts if p["role"] == "cap")
    radii = sorted({round(math.hypot(x, y), 5) for x, y, _z in collar["verts"]})
    assert len(radii) >= 4                                                              # ribs: two radii, chamfers
    nozzle = [v for p in parts if p["role"] == "nozzle" for v in p["verts"]]
    tip = min(nozzle, key=lambda v: v[1])
    assert tip[2] < max(z for _x, _y, z in nozzle) - 0.004                              # its tip turned down
    assert sum(p["role"] == "print" for p in parts) >= 10                               # words, not bars
    frosted = BO.pump_bottle(0.0, 0.0, 0.0, r, h, "frosted", "handle")
    assert next(p for p in frosted if p["role"] == "bottle")["key"] == BO.GLASS["frosted"]
    black = BO.pump_bottle(0.0, 0.0, 0.0, r, h, "dark")
    assert next(p for p in black if p["role"] == "bottle")["key"] == "dark" and "contents" not in _roles(black)


def test_the_perfume_is_a_thick_glass_flacon_with_its_scent_tube_collar_and_cap():
    w, d, h = 0.05, 0.031, 0.11
    for style in (0, 1):
        parts = BO.perfume_bottle(0.0, 0.0, 0.0, w, d, h, "handle", "dark", style=style)
        glass = next(p for p in parts if p["role"] == "perfume")
        scent = next(p for p in parts if p["role"] == "liquid")
        assert glass["key"] == BO.GLASS["clear"] and scent["key"] == BO.SCENT_KEY
        inner = [v for v in glass["verts"] if abs(v[0]) < w / 2.0 - 0.003 and 0.008 < v[2] < h * 0.6]
        assert inner                                                                    # the cavity in thick glass
        assert min(z for _x, _y, z in scent["verts"]) >= 0.008                          # over the heavy base
        assert {"tube", "cap"} <= _roles(parts)
        assert max(z for p in parts for _x, _y, z in p["verts"]) == pytest.approx(h, abs=0.002)


def test_the_cotton_balls_are_fluffy_lumpy_balls_of_cotton_wool_packed_in_the_jar():
    r, h = 0.042, 0.12
    parts = BO.apothecary_jar(0.0, 0.0, 0.0, r, h, "wood", "cotton", seed=3)
    balls = [p for p in parts if p["role"] == "fill"]
    assert len(balls) >= 8 and all(p["key"] == BO.COTTON_KEY for p in balls)
    for p in balls:
        cx = sum(v[0] for v in p["verts"]) / len(p["verts"])
        cy = sum(v[1] for v in p["verts"]) / len(p["verts"])
        cz = sum(v[2] for v in p["verts"]) / len(p["verts"])
        dist = [math.dist(v, (cx, cy, cz)) for v in p["verts"]]
        assert max(dist) / min(dist) > 1.25 and len(p["verts"]) >= 150                # lumpy, finely tufted
    assert {"seal", "lid"} <= _roles(parts) and next(p for p in parts if p["role"] == "jar")["key"] == BO.GLASS["clear"]


def test_the_basket_is_woven_over_and_under_its_stakes_with_a_braided_rim_and_handles():
    w, d, h = 0.23, 0.24, 0.126
    parts = BO.woven_basket(0.0, 0.0, 0.0, w, d, h)
    stakes = [p for p in parts if p["role"] == "stake"]
    weavers = [p for p in parts if p["role"] == "basket" and p["key"] == BO.CANE_KEY]
    assert len(stakes) >= 12 and len(stakes) % 2 == 0 and all(p["key"] == BO.REED_KEY for p in stakes)
    assert len(weavers) >= 5 and sum(p["role"] == "rim" for p in parts) == 2 and sum(p["role"] == "handle"
                                                                                     for p in parts) == 2
    assert any(p["role"] == "basket" and p["key"] == "rattan" for p in parts)          # the woven base: the photo
    for p in weavers:                                                                    # in and out round its ring
        rho = [math.hypot(x, y) for x, y, _z in p["verts"]]
        assert max(rho) - min(rho) > 0.004
    towels = [v for p in parts if p["role"] == "towel" for v in p["verts"]]
    inner = (w / 2.0 - 0.006) * 0.92 - BO.WEAVE["weave_in_m"] - BO.WEAVE["weaver_t_m"]
    assert max(abs(x) for x, _y, _z in towels) <= inner + 1e-6                          # inside the weave
    assert max(z for p in parts for _x, _y, z in p["verts"]) <= h + 1e-6


def test_the_soap_dish_the_diffuser_the_candle_and_the_plant_have_their_details():
    dish = BO.soap_dish(0.0, 0.0, 0.0, 0.045)
    assert sum(p["role"] == "rib" for p in dish) == 5 and sum(p["role"] == "soap" for p in dish) == 2
    assert next(p for p in dish if p["role"] == "dish")["key"] == BO.STONEWARE_KEY
    assert {p["key"] for p in dish if p["role"] == "soap"} == {BO.SOAP_KEY}
    dif = BO.reed_diffuser(0.0, 0.0, 0.0, 0.035, 0.10, 0.2, seed=1)
    reeds = [p for p in dif if p["role"] == "reed"]
    assert len(reeds) == BO.DIFFUSER["reeds"] and all(p["key"] == BO.REED_KEY for p in reeds)
    assert all(min(z for _x, _y, z in p["verts"]) < 0.02 for p in reeds)                # standing in the oil
    assert next(p for p in dif if p["role"] == "contents")["key"] == BO.DIFFUSER_OIL_KEY
    candle = BO.candle_glass(0.0, 0.0, 0.0, 0.035, 0.085)
    wax = next(p for p in candle if p["role"] == "candle")
    top = [v for v in wax["verts"] if v[2] > 0.085 * 0.78 - 0.005]
    centre = min(top, key=lambda v: math.hypot(v[0], v[1]))
    edge = max(top, key=lambda v: math.hypot(v[0], v[1]))
    assert centre[2] < edge[2] - 0.001 and wax["key"] == BO.SOAP_KEY                    # its melt pool
    plant = BO.potted_plant(0.0, 0.0, 0.0, 0.05, 0.08, 0.22, max_r=0.12)
    assert {p["key"] for p in plant if p["role"] == "leaf"} == {BO.LEAF_KEY}
    assert next(p for p in plant if p["role"] == "pot")["key"] == BO.STONEWARE_KEY
    assert sum(p["role"] == "dressing" for p in plant) >= 5


def test_every_small_item_key_has_its_slug_its_look_and_rattan_its_photo():
    keys, _ = BF.style_material_keys({})
    assert set(BO.SMALL_ITEM_KEYS) == set(P.SMALL_ITEM_KEYS) <= set(P.MATERIAL_KEYS)
    assert set(BO.SLUGS) == set(BO.SMALL_ITEM_KEYS) == set(M.SMALL_ITEM_LOOKS)
    for k in BO.SMALL_ITEM_KEYS:
        slug = keys[k][0]
        assert slug == BO.SLUGS[k] == M.SMALL_ITEM_LOOKS[k]["slug"], k
        assert slug in V.FLAT_COLOURS and slug in V.ROUGHNESS and slug in PR.MATERIAL_WORDS, slug
        assert M.SMALL_ITEM_LOOKS[k]["kind"] in M.SMALL_ITEM_REASONS
    assert keys["rattan"] == ("rattan", "Wicker005", None)
    glass = [k for k, v in M.SMALL_ITEM_LOOKS.items() if v["kind"] == "glass"]
    assert set(glass) == set(BO.GLASS.values()) and all(M.SMALL_ITEM_LOOKS[k]["ior"] == 1.5 for k in glass)
    for k in ("bottle_glass", "scent", "cotton_wool", "stoneware"):
        assert P.part_bevel_radius({"key": k, "role": "x", "smooth": True, "verts": [(0, 0, 0), (1, 1, 1)]}) == 0.0
