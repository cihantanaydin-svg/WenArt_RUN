"""The user's review of real04 run 20261030-043021-full (30 Oct 2026; user rule of 26 Oct 2026: every fix is general):

- UL156, "I did not like this lamp table combo": the open-kitchen variant's living room had a Herman Miller Nelson end
  table (a thin top on a swivel 4-star base, office furniture) beside the sofa under a two-tone drum lamp. A side table,
  nightstand or coffee table stands on a solid base (``fit.base_misfit``, a gate outside a study); a table lamp is
  chosen with its host: shade, height and real size in proportion (``fit.lamp_limits``, ``fit.lamp_pairing``), no
  novelty lamp, no work light beside a seat or a bed (``fit.lamp_misfit``), recorded on the lamp (``asset.pairing``).
- UL161, "I did not like these sofas here maybe used in another project but not here": two white HEMNES daybed frames
  pinned by the agent as the play-and-rest room's sofas. A daybed is no sofa of a living-type room unless the piece
  asks for one in a family that seats a living room on a daybed (``fit.daybed_misfit``); the pin and the agent's swap
  are refused with the rule (``fit.room_rule_refusal``); a bedroom or a study keeps it.
CPU only (a fake catalogue; no runs/).
"""
from __future__ import annotations

import _m11_room as M
from wenart.furniture import edit_ops as E
from wenart.furniture import fit as F
from test_furniture_fit_v2 import FakeCatalog, decor_model, model, piece

NELSON = "Herman Miller Nelson Small End Table from Smart Furniture"
SOLID = "Ameriwood Home Carver End Table, Gray/Sonoma Oak"
DAYBED = "HEMNES daybed frame A white [ud6311f5]"
SOFA = "Rivet Lawson Modern Angled Sofa, 78\"W, Smoke"


def side_tables():
    return [model("nelson", "side_table", 0.50, 0.50, 0.55, title=NELSON, quality=5.0),
            model("cart", "side_table", 0.48, 0.46, 0.48, title="go-cart yellow rolling table CB2", quality=5.0),
            model("solid", "side_table", 0.50, 0.50, 0.58, title=SOLID, quality=3.0)]


def living_room_building(*pieces, room_type="living"):
    return {"project": {"id": "t"}, "furniture": list(pieces), "decor": [],
            "rooms": [{"id": "r_L0_salon", "room_type": room_type, "room_subtype": None, "polygon": []}]}


# --------------------------------------------------------------------------
# UL156: a solid base
# --------------------------------------------------------------------------

def test_office_swivel_star_and_rolling_bases_are_no_living_room_side_tables():
    nelson, cart, solid = side_tables()
    assert "nelson small end table" in F.base_misfit(nelson, "side_table", "living")
    assert "rolling" in F.base_misfit(cart, "nightstand", "bedroom")
    assert F.base_misfit(solid, "side_table", "living") is None
    assert F.base_misfit(nelson, "side_table", "other") is None                  # a study or office keeps it
    assert F.base_misfit(nelson, "chair", "living") is None                      # the rule is the tables'
    swivel = model("sw", "table_coffee", 1.0, 0.6, 0.4, title="Swivel Coffee Table")
    assert "swivel" in F.base_misfit(swivel, "table_coffee", "living")


def test_the_fit_gates_the_base_and_logs_the_rule():
    b = living_room_building(piece("side_table", 0.5, 0.5))
    fitted = F.fit_building(b, FakeCatalog(side_tables()))
    asset = fitted["furniture"][0]["asset"]
    assert asset["asset_id"] == "abo_solid"
    rules = {x["id"]: x for x in asset["excluded"] if x.get("rule") == F.BASE_RULE}
    assert set(rules) == {"abo_nelson", "abo_cart"} and "UL156" in rules["abo_nelson"]["reason"]
    F.assert_only_assets_changed(b, fitted)
    study = F.fit_building(living_room_building(piece("side_table", 0.5, 0.5), room_type="other"),
                           FakeCatalog(side_tables()))
    assert study["furniture"][0]["asset"]["asset_id"] == "abo_nelson"            # the best rated, in a study


def test_the_agents_pin_and_swap_to_a_star_base_are_refused():
    pinned = F.fit_building(living_room_building(dict(piece("side_table", 0.5, 0.5), asset_pin="abo_nelson")),
                            FakeCatalog(side_tables()))
    asset = pinned["furniture"][0]["asset"]
    assert asset["asset_id"] == "abo_solid" and asset["pin_refused"].startswith("abo_nelson: names nelson")
    nelson, _cart, solid = side_tables()

    class Cat:
        def entry(self, asset_id):
            return {e["id"]: e for e in (nelson, solid)}.get(asset_id)

    living = M.building(w=5.0, h=4.0, room_type="living", furniture=[
        M.fp("f_L0_001", "side_table", (0.4, 0.4), (0.5, 0.5), rotation=0.0)])
    swap = dict({"op": "swap_model"}, reason="test", round=1, log_seq=1, model="mock", piece_id="f_L0_001")
    res = E.apply_edit(living, dict(swap, asset_id="abo_nelson"), catalog=Cat())
    assert not res["accepted"] and any("star" in c for c in res["failed_checks"]), res["failed_checks"]
    assert E.apply_edit(living, dict(swap, asset_id="abo_solid"), catalog=Cat())["accepted"]


# --------------------------------------------------------------------------
# UL156: the lamp with its host
# --------------------------------------------------------------------------

def host(ftype="side_table", top=0.5, height=0.58, title=SOLID):
    return {"id": "f_L0_009", "type": ftype, "footprint": {"size": [top, top]}, "height": height,
            "asset": {"asset_id": "abo_host", "bbox_m": [top, top, height], "title": title}}


def lamp(uid, w, h, title):
    return decor_model(uid, "table_lamp", w, w, h, title=title)


def lamp_item():
    return {"id": "dec_L0_001", "type": "table_lamp", "host_id": "f_L0_009", "room_id": "r_L0_salon",
            "size": [0.35, 0.35, 0.6]}


def test_lamp_limits_follow_the_host():
    lim = F.lamp_limits(host())
    assert lim["shade_max_m"] == round(0.5 * F.LAMP_SHADE_TOP_RATIO, 4) and lim["shade_hard_m"] == 0.375
    assert lim["height_range_m"] == [round(0.58 * 0.75, 4), round(0.58 * 1.15, 4)] and not lim["light_base"]
    light = F.lamp_limits(host(title="Tulip pedestal side table"))
    assert light["light_base"] and light["shade_max_m"] == round(0.5 * F.LIGHT_BASE_SHADE_RATIO, 4)
    assert "height_range_m" not in F.lamp_limits(host("desk", 0.7, 0.75, "Oak desk"))   # a desk: no eye-level rule
    assert F.lamp_limits(None) is None


def test_a_lamp_in_proportion_to_its_host_wins():
    big = lamp("drum", 0.33, 0.57, "Two Tone Table Lamp with Drum Shade")           # shade 66 % of the 0.5 m top
    toy = lamp("tall", 0.47, 0.92, "Table Lamp A")                                  # 0.92 m: shrunk to a toy
    good = lamp("linen", 0.28, 0.55, "Ceramic Table Lamp with Linen Shade")
    for pool in ([big, good], [toy, good], [big, toy, good]):
        asset = F.fit_decor_item(lamp_item(), FakeCatalog(decor=pool), host=host())
        assert asset["asset_id"] == "abo_linen" and asset["fit_scale"] == [1.0, 1.0, 1.0], pool
        assert asset["pairing"]["held"] == "shade, height and real size"
        assert asset["pairing"]["host_id"] == "f_L0_009" and asset["pairing"]["rule"] == F.PAIRING_RULE
    alone = F.fit_decor_item(lamp_item(), FakeCatalog(decor=[big]), host=host())
    assert alone["asset_id"] == "abo_drum" and alone["pairing"]["held"] == "the hard shade limit only"
    wide = lamp("wide", 0.45, 0.6, "Wide Drum Lamp")                               # wider than 75 % of the top
    shrunk = F.fit_decor_item(lamp_item(), FakeCatalog(decor=[wide]), host=host())
    assert shrunk is None or max(shrunk["bbox_m"][:2]) <= 0.375 + 1e-9               # never a shade over the top


def test_no_novelty_lamp_and_no_work_light_beside_a_seat():
    deer = lamp("deer", 0.28, 0.5, "Modern Deer Head Ceramic Lamp, White and Brass")
    task = lamp("task", 0.19, 0.6, "Mid-Century Modern Curved Task Desk Table Lamp With USB Port")
    desk = lamp("desk", 0.2, 0.55, "IKEA Ranarp Desk Lamp")
    good = lamp("linen", 0.24, 0.55, "Accent Table Lamp with White Shade")
    assert "novelty" in F.lamp_misfit(deer, "side_table") and "novelty" in F.lamp_misfit(deer, "desk")
    assert "work light" in F.lamp_misfit(task, "nightstand") and F.lamp_misfit(task, "desk") is None
    assert "desk lamp" in F.lamp_misfit(desk, "side_table")
    assert F.lamp_misfit(lamp("tbl", 0.2, 0.5, "Modern Bedroom Table Desk Lamp, Wood"), "nightstand") is None
    asset = F.fit_decor_item(dict(lamp_item(), colour="brass"), FakeCatalog(decor=[deer, task, desk, good]),
                             host=host())
    assert asset["asset_id"] == "abo_linen"
    assert set(asset["pairing"]["misfits_dropped"]) == {"abo_deer", "abo_task", "abo_desk"}
    only = F.fit_decor_item(lamp_item(), FakeCatalog(decor=[deer]), host=host())
    assert only["asset_id"] == "abo_deer"                                            # nothing else: it stays


def test_fit_building_fits_the_lamp_with_its_fitted_host():
    tbl = piece("side_table", 0.5, 0.5, pid="f_L0_009")
    b = living_room_building(tbl)
    b["decor"] = [lamp_item()]
    big = lamp("drum", 0.33, 0.57, "Two Tone Table Lamp with Drum Shade")
    good = lamp("linen", 0.28, 0.55, "Ceramic Table Lamp with Linen Shade")
    fitted = F.fit_building(b, FakeCatalog(side_tables(), decor=[big, good]))
    assert fitted["furniture"][0]["asset"]["asset_id"] == "abo_solid"
    asset = fitted["decor"][0]["asset"]
    assert asset["asset_id"] == "abo_linen" and asset["pairing"]["host_top_m"] == 0.5


# --------------------------------------------------------------------------
# UL161: a daybed is no living room's sofa
# --------------------------------------------------------------------------

def sofas():
    return [model("hemnes", "sofa", 2.11, 0.91, 0.86, source="objaverse", title=DAYBED, quality=5.0),
            model("lawson", "sofa", 2.0, 0.84, 0.9, title=SOFA, quality=3.0)]


def test_daybed_rule():
    hemnes, lawson = sofas()
    why = F.daybed_misfit(hemnes, "sofa", "living", "modern")
    assert "daybed" in why and "UL161" in why
    assert F.daybed_misfit(lawson, "sofa", "living", "modern") is None
    assert F.daybed_misfit(hemnes, "sofa", "bedroom", "modern") is None              # a guest or child's room
    assert F.daybed_misfit(hemnes, "sofa", "other", "modern") is None                # a study
    assert F.daybed_misfit(hemnes, "sofa", "living", "scandinavian", asked=True) is None
    assert "asks for a daybed" in F.daybed_misfit(hemnes, "sofa", "living", "modern", asked=True)
    assert F.daybed_misfit(hemnes, "bed_single", "living", "modern") is None
    assert F.daybed_asked({"type": "sofa", "type_raw": "DAYBED_200"})
    assert F.daybed_asked({"type": "sofa", "design": {"form": "daybed"}})
    assert not F.daybed_asked({"type": "sofa", "type_raw": None, "label": "Kanepe"})


def test_a_pinned_daybed_is_refused_as_a_living_room_sofa():
    sofa = dict(piece("sofa", 2.1, 0.9), asset_pin="objaverse_hemnes")
    b = living_room_building(sofa)
    fitted = F.fit_building(b, FakeCatalog(sofas()), style_family="modern")
    asset = fitted["furniture"][0]["asset"]
    assert asset["asset_id"] == "abo_lawson" and "daybed" in asset["pin_refused"]
    assert asset["pin_refused"].startswith("objaverse_hemnes:")
    free = F.fit_building(living_room_building(piece("sofa", 2.1, 0.9)), FakeCatalog(sofas()), style_family="modern")
    got = free["furniture"][0]["asset"]
    assert got["asset_id"] == "abo_lawson"
    assert any(x.get("rule") == F.DAYBED_RULE and x["id"] == "objaverse_hemnes" for x in got["excluded"])
    guest = F.fit_building(living_room_building(dict(piece("sofa", 2.1, 0.9), asset_pin="objaverse_hemnes"),
                                                room_type="bedroom"), FakeCatalog(sofas()), style_family="modern")
    assert guest["furniture"][0]["asset"]["asset_id"] == "objaverse_hemnes"              # a guest room keeps the pin


def test_the_agents_swap_to_a_daybed_is_refused_with_the_rule():
    hemnes, lawson = sofas()

    class Cat:
        def entry(self, asset_id):
            return {e["id"]: e for e in (hemnes, lawson)}.get(asset_id)

    living = M.building(w=5.0, h=4.0, room_type="living", furniture=[
        M.fp("f_L0_001", "sofa", (2.5, 0.5), (2.1, 0.9), rotation=0.0)])
    res = E.apply_edit(living, dict({"op": "swap_model"}, reason="test", round=1, log_seq=1, model="mock",
                                    piece_id="f_L0_001", asset_id="objaverse_hemnes"), catalog=Cat())
    assert not res["accepted"] and any("daybed" in c for c in res["failed_checks"]), res["failed_checks"]
    ok = E.apply_edit(living, dict({"op": "swap_model"}, reason="test", round=1, log_seq=1, model="mock",
                                   piece_id="f_L0_001", asset_id="abo_lawson"), catalog=Cat())
    assert ok["accepted"], ok["failed_checks"]
