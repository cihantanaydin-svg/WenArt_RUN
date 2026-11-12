"""6 Nov 2026 (real21; user: "all floors needs to be done", "Make sense of the building", "underground floors will have
no window"; lesson UL331): what a drawing leaves out, completed by general rules.

What: the storey evidence ladder (``wenart.sheets.storeys``: a floor list in a title, the area table, the zoning texts,
the type default, the brief) and its negatives (a house with no lift and no stair gets no storey; a title wins over the
type default; a level the drawing or the brief names is kept); the window inference (``wenart.ingest.completion``: one
window per habitable room facing out, none on a party wall, none on a plan that draws windows, none below ground, a
balcony door, a light well's windows); the light wells (an open-air void through the storeys); the RC14 checks of what
is left out (no window, a room without one, a single-storey reading of a block, a light well read as a room, a window on
a party wall, a lift that stops, no entrance). Every case is a small hand-made building or region: no project data.
"""
from __future__ import annotations

from types import SimpleNamespace

from shapely.geometry import Polygon

from wenart import building as B
from wenart.ingest import completion as CP
from wenart.reading_check import sense as SN
from wenart.sheets import storeys as ST

NO_TRUST = {"threshold": 0.7, "rules": {r: {"findings": 10, "judged_right": 10, "precision": 1.0, "trusted": True}
                                        for r in SN.RULES}}


# ---------------------------------------------------------------------------------------------------- fixtures
def txt(text, x=0.0, y=0.0, h=0.2, layer=None, tid="TEXT:1"):
    return SimpleNamespace(text=text, box=(x, y, x + h * len(text) * 0.7, y + h), height=h, layer=layer, id=tid,
                           evidence={"entity": tid, "layer": layer},
                           point=(x + h * len(text) * 0.35, y + h / 2.0))


def plan_region(rid="r1", texts=(), level=None, gross=None, features=None, file="a.dxf"):
    sheet = SimpleNamespace(id="s1", texts=list(texts), ents=[])
    r = SimpleNamespace(id=rid, file=file, sheet=sheet, box=(0.0, 0.0, 30.0, 20.0), texts=list(texts), ents=[],
                        use="read", cls="floor_plan", kind="drawing", metres_per_unit=1.0, features=features or {},
                        level=level or {"order": 0, "label": "Ground floor", "id": "L0", "kind": "floor",
                                        "method": "assumed", "evidence": []},
                        title=None, user_level=None)
    r._gross_m2 = gross
    return r


def docs_of(*regions, extra=()):
    sheet = regions[0].sheet
    sheet.texts = [t for r in regions for t in r.texts] + list(extra)
    return [SimpleNamespace(file=regions[0].file, sheets=[sheet])]


def infer(region, extra=(), values=None, regions=None):
    warnings, conflicts = [], []

    def conflict(kind, ids, text, resolution):
        conflicts.append(text)
        return f"sc_{len(conflicts):03d}"

    regions = regions or [region]
    rec = ST.infer([region], regions, docs_of(region, extra=extra), values or {}, warnings, conflict, {})
    return rec, warnings, conflicts


BLOCK_TEXTS = [txt("ASANSÖR", 10, 10), txt("ASANSÖR", 12, 10), txt("DAİRE GİRİŞİ", 5, 8), txt("DAİRE GİRİŞİ", 20, 8),
               txt("MUTFAK", 3, 3), txt("MUTFAK", 25, 3), txt("SALON", 3, 6), txt("SALON", 25, 6)]


# --------------------------------------------------------------------------------------------- the storey ladder
def test_a_title_listing_its_floors_and_ground_plus_texts_count_the_storeys():
    texts = [(txt("1.-4. NORMAL KAT PLANI"), "a.dxf"), (txt("Z+4"), "a.dxf"), (txt("B+Z+6"), "a.dxf")]
    counts = [c["count"] for c in ST.title_counts(texts)]
    assert counts == [5, 5, 7]
    # a ground floor and a list of normal floors (KATLAR, plural): the list counts, never 'ground + 1'
    note = [(txt("1. BODRUM OTOPARK - ZEMİN+1.2.3.4.5. NORMAL KATLAR DAİRE OLARAK İSKAN EDİLECEK"), "a.dxf")]
    assert [c["count"] for c in ST.title_counts(note)] == [6]
    assert ST.zoning_items([(txt("5 KATLI KONUT"), "a.dxf")])["count"][0]["value"] == 5


def test_the_area_table_counts_the_storeys_from_total_footprint_and_typical_floor():
    texts = [(txt("oturum 390"), "a.dxf"), (txt("normal  436"), "a.dxf"), (txt("TOPLAM İNŞAAT ALANI 2134"), "a.dxf")]
    rungs, areas = ST.ladder({}, {}, [], texts, 440.0, ST.plan_signals(plan_region()), 1)
    area = next(r for r in rungs if r["rung"] == "area_table")
    assert (areas["ground"]["value"], areas["typical"]["value"], areas["total"]["value"]) == (390.0, 436.0, 2134.0)
    assert area["count"] == 5                                     # 390 + 4 x 436 = 2134


def test_of_two_area_tables_on_one_sheet_the_plans_own_counts():
    texts = [(txt("oturum 390", -100, 0), "a.dxf"), (txt("normal 436", -100, -2), "a.dxf"),
             (txt("oturum 108 m2", 31, 18), "a.dxf"), (txt("normal 140 m2", 31, 16), "a.dxf")]
    _, areas = ST.ladder({}, {}, [], texts, 150.0, ST.plan_signals(plan_region()), 1, near=("a.dxf", (0, 0, 30, 20)))
    assert (areas["ground"]["value"], areas["typical"]["value"]) == (108.0, 140.0)


def test_a_scale_is_no_area_and_a_number_on_the_row_is():
    texts = [(txt("NORMAL KAT PLANI 1/100", 0, 0), "a.dxf"), (txt("TOPLAM", 0, 5), "a.dxf"),
             (txt("1250,50", 1.4, 5), "a.dxf")]
    items = ST.area_items(texts)
    assert [(i["kind"], i["value"]) for i in items] == [("total", 1250.5)]


def test_the_zoning_texts_count_the_storeys():
    z = ST.zoning_items([(txt("KAT ADEDİ: 6"), "a.dxf"), (txt("Hmax=15.50"), "a.dxf"), (txt("EMSAL=2.00"), "a.dxf")])
    assert z["count"][0]["value"] == 6 and z["height"][0]["value"] == 15.5 and z["far"][0]["value"] == 2.0
    rungs, _ = ST.ladder({}, {}, [], [(txt("Hmax=15.50"), "a.dxf")], 300.0, ST.plan_signals(plan_region()), 1)
    assert next(r for r in rungs if r["rung"] == "zoning")["count"] == 5          # 15.50 / 3.00
    assert ST.zoning_items([(txt("H=2.70"), "a.dxf")])["height"] == []            # a ceiling height is no limit


def test_section_slab_bands_never_count_the_storeys_but_the_storeys_it_names_do():
    # a two-storey house's section reads sills, parapets and landings as 9 slab bands: no storey count
    sec = SimpleNamespace(id="r9", cls="section", _section=SimpleNamespace(bands=list(range(9))))
    signals = ST.plan_signals(plan_region())
    rungs, _ = ST.ladder({}, {}, [sec], [], 100.0, signals, 2, drawn_all=2)
    rung = next(r for r in rungs if r["rung"] == "section")
    assert rung["count"] is None and "9 slab bands" in rung["note"]
    # the storeys the sections name count
    rungs, _ = ST.ladder({}, {0: "Zemin Kat", 1: "1. Normal Kat", 2: "2. Normal Kat"}, [sec], [], 100.0, signals, 1)
    assert next(r for r in rungs if r["rung"] == "section")["count"] == 3


def test_the_floor_role_follows_the_area_table():
    assert ST.floor_role(440.0, 390.0, 436.0)["role"] == "typical"
    assert ST.floor_role(395.0, 390.0, 436.0)["role"] == "ground"
    assert ST.floor_role(300.0, 390.0, 436.0) is None


def test_the_type_default_needs_what_the_plan_shows():
    block = ST.plan_signals(plan_region(texts=BLOCK_TEXTS))
    assert ST.building_type(block, False) == "apartment_block_lift"
    house = ST.plan_signals(plan_region(texts=[txt("SALON"), txt("MUTFAK"), txt("MERDİVEN")]))
    assert ST.building_type(house, False) == "house_stair"
    flat = ST.plan_signals(plan_region(texts=[txt("SALON"), txt("MUTFAK"), txt("YATAK ODASI")]))
    assert ST.building_type(flat, False) is None


def test_a_single_family_house_with_no_lift_and_no_upper_floor_evidence_gets_no_storey():
    r = plan_region(texts=[txt("SALON"), txt("MUTFAK"), txt("YATAK ODASI"), txt("BANYO")], gross=120.0)
    rec, warnings, _ = infer(r)
    assert rec["count"] is None and rec["inferred"] == [] and "typical" not in r.level


def test_an_apartment_block_with_lifts_and_no_count_gets_the_type_default_marked_as_a_guess():
    r = plan_region(texts=BLOCK_TEXTS, gross=300.0)
    rec, warnings, _ = infer(r)
    assert rec["rule"] == "type_default" and rec["guess"] is True and rec["count"] == ST.TYPE_DEFAULTS[
        "apartment_block_lift"]
    assert r.level["typical"]["ids"] == ["L0", "L1", "L2", "L3", "L4"]
    assert [i["level_id"] for i in rec["inferred"]] == ["L1", "L2", "L3", "L4"]
    assert rec["open_point"]["key"] == ST.OPEN_POINT_KEY and rec["open_point"]["severity"] == "major"
    assert "type default" in rec["guess_note"] and "storeys: N" in rec["guess_note"]


def test_a_floor_list_in_a_title_wins_over_the_type_default():
    r = plan_region(texts=BLOCK_TEXTS, gross=300.0)
    rec, warnings, _ = infer(r, extra=[txt("Z+2", 40, 40)])
    assert rec["rule"] == "title" and rec["count"] == 3 and rec["guess"] is False
    assert r.level["typical"]["ids"] == ["L0", "L1", "L2"]
    assert any("disagree" in w for w in warnings)


def test_the_brief_storeys_win_over_every_rung():
    r = plan_region(texts=BLOCK_TEXTS, gross=300.0)
    rec, _, _ = infer(r, extra=[txt("Z+2", 40, 40)], values={"storeys": 4})
    assert rec["rule"] == "user" and rec["count"] == 4 and len(r.level["typical"]["ids"]) == 4


def test_an_untitled_typical_floor_stands_over_an_inferred_ground_floor_without_cantilevers():
    r = plan_region(texts=BLOCK_TEXTS, gross=440.0)
    rec, warnings, _ = infer(r, extra=[txt("oturum 390", 40, 40), txt("normal  436", 40, 42)])
    assert rec["ground_from_typical"] is True and rec["cantilevers"]["ground_m2"] == 390.0
    assert r.level["typical"]["labels"][:2] == ["Zemin Kat", "1. Normal Kat"]
    assert "L0" in r.level["typical"]["inferred"] and "L1" not in r.level["typical"]["inferred"]


def test_a_level_the_drawing_names_is_kept_against_the_area_table():
    r = plan_region(texts=BLOCK_TEXTS, gross=440.0,
                    level={"order": 0, "label": "Zemin Kat", "id": "L0", "kind": "floor", "method": "title",
                           "evidence": []})
    rec, warnings, conflicts = infer(r, extra=[txt("oturum 390", 40, 40), txt("normal  436", 40, 42)])
    assert r.level["label"] == "Zemin Kat" and rec["ground_from_typical"] is False
    assert conflicts and "the level is kept" in conflicts[0]


def test_a_drawn_roof_terrace_means_the_top_is_drawn():
    r = plan_region(texts=BLOCK_TEXTS, level={"order": 3, "label": "Teras Katı", "id": "L3", "kind": "floor",
                                              "method": "title", "roof_terrace": True, "evidence": []})
    rec, _, _ = infer(r)
    assert rec["count"] is None and "typical" not in r.level


# -------------------------------------------------------------------------------------------- the window evidence
def test_the_window_evidence_of_a_plan():
    ent = SimpleNamespace(layer="PENCERE", kind="LINE", block=None)
    region = SimpleNamespace(ents=[ent], texts=[])
    assert ST.windows_drawn(region)["draws_windows"] is True
    tags = SimpleNamespace(ents=[], texts=[txt("150/140", layer="penc-yazi")])
    assert ST.windows_drawn(tags)["tags"] == 1
    doors = SimpleNamespace(ents=[SimpleNamespace(layer="KAPI", kind="LINE", block=None)],
                            texts=[txt("90/210", layer="kapi-yazi")])
    assert ST.windows_drawn(doors)["draws_windows"] is False
    assert ST.window_tag("90/210", None) is None and ST.window_tag("1500/1400", None) == (1.5, 1.4)


# --------------------------------------------------------------------------------------------- a small building
def rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def room(rid, label, rtype, poly, level="L0", **kw):
    return dict({"id": rid, "level_id": level, "label": label, "room_type": rtype, "polygon": poly,
                 "area_computed": round(Polygon(poly).area, 3)}, **kw)


def wall(wid, a, b, level="L0", t=0.2, exterior=False):
    return {"id": wid, "level_id": level, "start": list(a), "end": list(b), "thickness": t, "exterior": exterior}


def flat(level="L0", order=0, elevation=0.0, well=False):
    """A 10 x 6 m flat: a bedroom (west) and a living room (east) with a door between them; with ``well`` a 1.6 m
    light well cut from the bedroom's north-west corner, holding the word AYDINLIK."""
    w = [wall(f"w_{level}_1", (0, 0), (10, 0), level, exterior=True),
         wall(f"w_{level}_2", (10, 0), (10, 6), level, exterior=True),
         wall(f"w_{level}_3", (10, 6), (0, 6), level, exterior=True),
         wall(f"w_{level}_4", (0, 6), (0, 0), level, exterior=True),
         wall(f"w_{level}_5", (5, 0), (5, 6), level)]
    rooms = [room(f"r_{level}_living", "Salon", "living", rect(5.1, 0.1, 9.9, 5.9), level)]
    if well:
        w += [wall(f"w_{level}_6", (0, 4.4), (1.6, 4.4), level), wall(f"w_{level}_7", (1.6, 4.4), (1.6, 6), level)]
        rooms += [room(f"r_{level}_oda", "Oda", "bedroom", [[0.1, 0.1], [4.9, 0.1], [4.9, 5.9], [1.7, 5.9],
                                                             [1.7, 4.3], [0.1, 4.3]], level),
                  room(f"r_{level}_oda_2", "Oda", "unknown", rect(0.1, 4.5, 1.5, 5.9), level)]
    else:
        rooms += [room(f"r_{level}_oda", "Oda", "bedroom", rect(0.1, 0.1, 4.9, 5.9), level)]
    doors = [{"id": f"d_{level}_001", "type": "door", "level_id": level, "wall_id": f"w_{level}_5",
              "center": [5.0, 3.0], "width": 0.9}]
    lv = {"id": level, "label": "Zemin Kat" if order == 0 else f"{order}. Kat", "order": order,
          "elevation": elevation, "ceiling_height": 2.7, "kind": "basement" if order < 0 else "floor"}
    return lv, w, rooms, doors


def building(*parts, site=None, li=None):
    b = {"levels": [], "walls": [], "rooms": [], "openings": [], "furniture": [], "documents": [], "warnings": [],
         "site": site or {}, "level_inference": li or {}}
    for lv, w, rooms, doors in parts:
        b["levels"].append(lv)
        b["walls"] += w
        b["rooms"] += rooms
        b["openings"] += doors
    return b


SIZES = dict(CP.DEFAULT_SIZES)


def infer_windows(b, lid="L0", party=None, texts=None):
    ids = B.IdCounter()
    return CP.infer_level(b, lid, party or {}, SIZES, "defaults", ids.next, texts)


def test_every_habitable_room_facing_out_gets_one_inferred_window_marked_inferred():
    b = building(flat())
    new = infer_windows(b)
    by_room = {o["inference"]["room_id"]: o for o in new}
    assert set(by_room) == {"r_L0_oda", "r_L0_living"}
    o = by_room["r_L0_living"]
    assert o["type"] == "window" and o["inferred"] is True and o["evidence"][0]["method"] == "inferred"
    assert abs(o["width"] - SIZES["living"][0]) < 1e-6 and o["inference"]["faces"] == "outside"


def test_a_party_wall_named_by_an_attached_text_gets_no_window():
    b = building(flat())
    level = CP.Level(b, "L0")
    party = CP.party_walls(level, [{"kind": "party", "text": "bitişik", "at": [-1.5, 3.0]},
                                   {"kind": "street", "text": "Kalem Sokağı", "at": [5.0, 7.5]}])
    assert set(party) == {"w_L0_4"}
    new = infer_windows(b, party=party)
    assert new and all(o["wall_id"] != "w_L0_4" for o in new)
    # the plan's shape alone never makes a party wall
    assert CP.party_walls(level, []) == {}


def test_a_balcony_on_a_party_wall_is_left_out_and_one_on_a_facade_stays():
    b = building(flat(), site={"outdoor_spaces": [
        {"id": "os_party", "kind": "balcony", "level_id": "L0", "polygon": rect(-1.3, 1.0, -0.1, 4.0)},
        {"id": "os_street", "kind": "balcony", "level_id": "L0", "polygon": rect(-0.1, 6.1, 4.0, 7.3)}]})
    party = {"w_L0_4": {"text": "bitişik"}}
    out = CP.party_balconies(b, {"L0": party})
    assert [d["id"] for d in out] == ["os_party"]
    assert [s["id"] for s in b["site"]["outdoor_spaces"]] == ["os_street"]


def test_a_plan_that_draws_windows_gets_none_inferred():
    b = building(flat())
    lv = b["levels"][0]
    assert CP.window_decision(b, lv, 0, {"draws_windows": True, "layer_entities": 4})[0] is False
    assert CP.window_decision(b, lv, 2, {"draws_windows": False})[0] is False
    assert CP.window_decision(b, lv, 0, None)[0] is False                    # no record: never guessed
    assert CP.window_decision(b, lv, 0, {"draws_windows": False})[0] is True


def test_a_level_below_ground_gets_no_inferred_window():
    basement = flat("L-1", -1, -3.0)
    b = building(basement, site={"ground": {"levels": [{"z": {"value": -0.15}}], "surface": {"flat_z": -0.15}}})
    lv = b["levels"][0]
    assert CP.below_ground(b, lv) and CP.window_decision(b, lv, 0, {"draws_windows": False})[0] is False
    # a floor whose floor and ceiling lie under the ground, whatever its name
    deep = flat("L0", 0, -3.5)
    b2 = building(deep, site={"ground": {"surface": {"flat_z": 0.0}}})
    assert "under the ground" in CP.below_ground(b2, b2["levels"][0])
    assert CP.below_ground(building(flat()), {"id": "L0", "order": 0, "elevation": 0.0}) is None
    # and RC14 raises no room without a window there
    assert SN.room_without_window(b) == []


def test_a_room_onto_a_balcony_gets_a_balcony_door():
    b = building(flat(), site={"outdoor_spaces": [{"id": "os_1", "kind": "balcony", "level_id": "L0",
                                                   "polygon": rect(5.2, 6.1, 9.8, 7.4)}]})
    new = infer_windows(b)
    doors = [o for o in new if o["type"] == "door"]
    assert len(doors) == 1 and doors[0]["inference"]["room_id"] == "r_L0_living" and doors[0]["wall_id"] == "w_L0_3"


def test_a_light_well_is_an_open_air_void_and_the_room_beside_it_looks_onto_it():
    b = building(flat(well=True))
    texts = [{"text": "AYDINLIK", "x": 0.8, "y": 5.2}]
    # read as a room: RC14 says so
    found = SN.run(b, {"L0": texts}, trust=NO_TRUST)
    assert [f for f in found if f["rule"] == "light_well_room"]
    build = SimpleNamespace(building=b, warn=lambda *_: None, ids=B.IdCounter())
    rec = CP._light_wells(build, {"L0": texts})
    well = next(r for r in b["rooms"] if r["id"] == "r_L0_oda_2")
    assert well["room_type"] == "shaft" and well["room_subtype"] == "light_well" and well["label"] == "Aydınlık"
    assert well["adjusted_by_ai"]["changed"]["room_type"] == "unknown" and rec["rooms"] == {"L0": ["r_L0_oda_2"]}
    assert not [f for f in SN.run(b, {"L0": texts}, trust=NO_TRUST) if f["rule"] == "light_well_room"]
    assert "r_L0_oda_2" not in {o["inference"]["room_id"] for o in infer_windows(b, texts=texts)}


def test_a_light_well_through_two_storeys_cuts_the_slab_and_the_roof():
    b = building(flat("L0", 0, 0.0, well=True), flat("L1", 1, 3.0, well=True))
    b["slabs"] = [{"id": "sl_L1", "above_level_id": "L1", "below_level_id": "L0", "openings": []}]
    b["roof"] = None
    texts = {lid: [{"text": "AYDINLIK", "x": 0.8, "y": 5.2}] for lid in ("L0", "L1")}
    build = SimpleNamespace(building=b, warn=lambda *_: None, ids=B.IdCounter())
    rec = CP._light_wells(build, texts)
    assert rec["slab_voids"] and b["slabs"][0]["openings"][0]["kind"] == "void"
    assert b["roof"]["openings"][0]["kind"] == "light_well" and b["roof"]["openings"][0]["room_id"] == "r_L1_oda_2"


# ------------------------------------------------------------------------------------------------- RC14 checks
def test_a_building_with_no_window_and_one_with_every_window_inferred():
    b = building(flat())
    assert [f["severity"] for f in SN.no_windows(b)] == ["major"]
    b["openings"] += infer_windows(b)
    found = SN.no_windows(b)
    assert [(f["severity"], f["part"]) for f in found] == [("minor", "all_inferred")]


def test_drawn_windows_that_were_not_read_are_a_reading_miss_never_covered():
    b = building(flat(), li={"windows": {"levels": {"L0": {"windows_read": 0, "inferred": [],
                                                           "drawing": {"draws_windows": True, "layer_entities": 6,
                                                                       "blocks": 0, "tags": 2}}}}})
    found = SN.no_windows(b)
    assert {f["part"] for f in found} == {"not_read", "none"}
    assert all(f["severity"] == "major" for f in found)


def test_a_stair_on_the_top_storey_that_no_stair_below_meets_goes_up_to_an_unread_storey():
    l0, l1 = flat("L0", 0, 0.0), flat("L1", 1, 3.0)
    stair = {"id": "f_L1_001", "level_id": "L1", "type": "stair",
             "footprint": {"center": [3.0, 3.0], "size": [1.0, 2.5], "rotation_deg": 0.0},
             "stair": {"flights": [{"lines": 8}, {"lines": 8}]}}
    b = building(l0, l1)
    b["furniture"] = [stair]
    found = SN.storeys_missing(b)
    assert found and found[0]["part"] == "stair_up"
    b["furniture"].append(dict(stair, id="f_L0_001", level_id="L0"))
    assert SN.storeys_missing(b) == []
    # a few steps (an entrance, a split level) climb no storey: a one-storey house with them is no finding
    steps = dict(stair, id="f_L0_009", level_id="L0", stair={"flights": [{"lines": 4}]})
    one = building(flat())
    one["furniture"] = [steps]
    assert SN.storeys_missing(one) == []
    one["furniture"] = [dict(stair, id="f_L0_009", level_id="L0")]
    assert SN.storeys_missing(one)[0]["part"] == "single"


def test_a_habitable_room_facing_out_without_a_window_is_a_finding_until_it_has_one():
    b = building(flat())
    found = SN.room_without_window(b)
    assert {f["element_ids"][0] for f in found} == {"r_L0_oda", "r_L0_living"}
    b["openings"] += infer_windows(b)
    assert SN.room_without_window(b) == []


def test_a_room_whose_only_outer_face_is_a_party_wall_is_no_finding():
    lv, w, rooms, doors = flat()
    # a 2 m deep slice along the west wall: the bedroom faces out only through the party wall w_L0_4 ...
    rooms[1]["polygon"] = rect(0.1, 2.0, 4.9, 4.0)
    w += [wall("w_L0_8", (0, 1.9), (5, 1.9)), wall("w_L0_9", (0, 4.1), (5, 4.1))]
    rooms += [room("r_L0_s", "Depo", "storage", rect(0.1, 0.1, 4.9, 1.8)),
              room("r_L0_n", "Depo", "storage", rect(0.1, 4.2, 4.9, 5.9))]
    b = building((lv, w, rooms, doors))
    assert "r_L0_oda" in {f["element_ids"][0] for f in SN.room_without_window(b)}
    b["level_inference"] = {"windows": {"party_walls": {"L0": {"w_L0_4": {"text": "bitişik"}}}}}
    assert "r_L0_oda" not in {f["element_ids"][0] for f in SN.room_without_window(b)}


def test_a_single_storey_reading_of_a_block_with_a_lift_is_a_finding():
    lv, w, rooms, doors = flat()
    rooms.append(room("r_L0_lift", "Asansör", "shaft", rect(4.0, 2.0, 4.8, 2.8)))
    found = SN.storeys_missing(building((lv, w, rooms, doors)))
    assert found and "lift" in found[0]["message"]
    assert SN.storeys_missing(building(flat())) == []          # a flat with no lift, no stair: nothing


def test_a_window_on_a_party_wall_is_a_finding():
    b = building(flat())
    b["walls"][3]["party_wall"] = {"text": "bitişik"}
    b["openings"].append({"id": "win_L0_001", "type": "window", "level_id": "L0", "wall_id": "w_L0_4",
                          "center": [0.0, 3.0], "width": 1.2})
    assert [f["element_ids"][0] for f in SN.party_wall_openings(b)] == ["win_L0_001"]


def test_a_lift_that_stops_between_storeys_is_a_finding():
    l0 = flat("L0", 0, 0.0)
    l0[2].append(room("r_L0_lift", "Asansör", "shaft", rect(4.0, 2.0, 4.8, 2.8), "L0"))
    l1 = flat("L1", 1, 3.0)
    found = SN.core_continuity(building(l0, l1))
    assert found and found[0]["element_ids"] == ["r_L0_lift"]
    l1[2].append(room("r_L1_lift", "Asansör", "shaft", rect(4.0, 2.0, 4.8, 2.8), "L1"))
    assert SN.core_continuity(building(l0, l1)) == []


def test_the_inferred_storey_count_is_an_open_point_of_the_architect_with_its_default():
    from wenart.blender import architect as AR
    from wenart.blender import architect_actions as AA
    from wenart.blender import architect_storeys as ASTO

    b = {"levels": [], "rooms": [], "walls": [], "openings": [],
         "level_inference": {"storeys": {"count": 5, "rule": "type_default", "confidence": 0.25, "guess": True,
                                         "guess_note": "a type default", "inferred": [{"level_id": "L1"}],
                                         "open_point": {"key": ST.OPEN_POINT_KEY, "default": 5, "options": [3, 4, 5, 6],
                                                        "severity": "major", "question": "How many storeys?"}}}}
    q = ASTO.review(b)
    a = q["answers"][0]
    assert q["id"] == "N1" and q["severity"] == "major" and a["open"] and a["default"] == "keep"
    assert {o["choice"] for o in a["options"]} == {"keep", "storey_count:3", "storey_count:4", "storey_count:6"}
    # the architect's safe default keeps the inferred count; the AI may pick another, recorded for the reading
    assert AR.defaults_of({"questions": [q]}, {})[ST.OPEN_POINT_KEY]["choice"] == "keep"
    done = AA.apply_answers(b, {ST.OPEN_POINT_KEY: {"option": "storey_count", "params": {"count": 6}, "by": "ai"}})
    assert done[0]["ok"] and b["level_inference"]["storeys"]["answer"]["count"] == 6
    assert ASTO.review(b)["answers"][0]["open"] is False
    assert ASTO.review({"level_inference": {}}) is None


def test_a_building_without_a_door_from_outside_is_a_finding():
    b = building(flat())
    assert SN.no_entrance(b)
    b["openings"].append({"id": "d_L0_002", "type": "door", "level_id": "L0", "wall_id": "w_L0_1",
                          "center": [7.5, 0.0], "width": 1.0})
    assert SN.no_entrance(b) == []
