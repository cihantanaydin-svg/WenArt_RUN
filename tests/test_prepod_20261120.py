"""The fixes of the final pre-pod check (20 Nov 2026, SENSE sections): CPU only, synthetic fixtures."""
from types import SimpleNamespace

from shapely.geometry import box

from wenart.ingest import completion as CP
from wenart.sheets import storeys as ST
from wenart.sheets import roof_frame as RF


# --------------------------------------------------------------------------- R20-01 / BP-03: a sheet frame is no roof
def _txt(text, x, y):
    return SimpleNamespace(text=text, point=(x, y))


def test_a_double_sheet_frame_with_street_texts_is_no_roof():
    walls = box(0, 0, 16.05, 11.12)                           # metres = units (mpu 1)
    frame = box(-1.15, -1.32, 17.79, 13.27)
    top = SimpleNamespace(texts=[_txt("AHMET KAYA CADDESİ", 16.9, 5.0), _txt("3406 PARSEL", 8.0, 12.5)])
    why = RF.reject(top, 1.0, SimpleNamespace(id="LWPOLYLINE:9AD"), frame, [], walls=walls)
    assert why and "9AD" in why
    near = box(-0.6, -0.6, 16.65, 11.72)                      # 0.6 m all round: the edges alone pass ...
    assert RF.reject(SimpleNamespace(texts=[]), 1.0, SimpleNamespace(id="x"), near, [], walls=walls) is None
    top2 = SimpleNamespace(texts=[_txt("AHMET KAYA CADDESİ", 16.4, 5.0)])     # ... a street name in the ring does not
    assert "texts" in RF.reject(top2, 1.0, SimpleNamespace(id="x"), near, [], walls=walls)


def test_a_real_eaves_loop_and_a_break_line_on_the_walls_stay():
    walls = box(0, 0, 12, 9)
    eaves = box(-0.7, -0.7, 12.7, 9.7)
    top = SimpleNamespace(texts=[_txt("SAÇAK", 6.0, 9.4), _txt("+12.00", 12.4, 4.0), _txt("P150/120", 12.3, 2.0)])
    assert RF.reject(top, 1.0, SimpleNamespace(id="e"), eaves, [], walls=walls) is None
    assert RF.break_inside(top, 1.0, SimpleNamespace(id="e"), SimpleNamespace(id="b"), box(0.1, 0.1, 11.9, 8.9),
                           walls=walls)
    assert not RF.break_inside(top, 1.0, SimpleNamespace(id="e"), SimpleNamespace(id="b"),
                               box(-0.5, -0.5, 12.5, 9.5), walls=walls)      # a 'break' outside the walls


def test_a_plan_lines_roof_with_no_height_over_a_counted_storey_sits_on_its_ceiling():
    b = {"levels": [{"id": f"L{k}", "order": k, "elevation": 3.0 * k, "ceiling_height": 2.7} for k in range(5)],
         "roof": {"type": "mansard", "type_source": "plan_roof_lines", "eaves_height": None, "over_level_id": "L0"},
         "warnings": []}
    build = SimpleNamespace(building=b, warn=b["warnings"].append)
    why = CP._plan_roof_eaves(build, b, {"L2", "L3", "L4"})
    assert why and b["roof"]["eaves_height"]["value"] == 14.7 and b["roof"]["eaves_height"]["method"] == "assumed"
    assert b["roof"]["over_level_id"] == "L4"
    b["roof"]["type_source"] = "section"
    b["roof"]["eaves_height"] = None
    assert CP._plan_roof_eaves(build, b, {"L2", "L3", "L4"}) is None          # a section roof: the rebase's job


# --------------------------------------------------------------------------- BP-01: light wells, party walls
def _rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _wall(wid, a, b, t=0.2, **kw):
    return dict({"id": wid, "level_id": "L0", "start": list(a), "end": list(b), "thickness": t}, **kw)


def _light_well_plan():
    """A 0.15 m party wall on the west (x 0); a light well (shaft, subtype light_well) against it between a WC (north)
    and a bedroom (south, east of it); the WC's window onto the light well; the bedroom's dark inside window."""
    party = {"text": "bitişik", "reason": "a blank party wall: no window, no balcony"}
    walls = [_wall("w_party", (0, 0), (0, 9), t=0.15, exterior=True, party_wall=party),
             _wall("w_s", (0, 0), (8, 0), exterior=True), _wall("w_e", (8, 0), (8, 9), exterior=True),
             _wall("w_n", (8, 9), (0, 9), exterior=True), _wall("w_lw_n", (0, 5), (2, 5)), _wall("w_lw_s", (0, 3), (2, 3)),
             _wall("w_lw_e", (2, 3), (2, 5)), _wall("w_mid", (2, 0), (2, 3))]
    rooms = [{"id": "r_lw", "level_id": "L0", "label": "Işıklık", "room_type": "shaft", "room_subtype": "light_well",
              "polygon": _rect(0.1, 3.1, 1.9, 4.9)},
             {"id": "r_wc", "level_id": "L0", "label": "WC", "room_type": "wc", "polygon": _rect(0.1, 5.1, 7.9, 8.9)},
             {"id": "r_bed", "level_id": "L0", "label": "Oda", "room_type": "bedroom", "polygon": _rect(2.1, 0.1, 7.9, 4.9)},
             {"id": "r_hall", "level_id": "L0", "label": "Hol", "room_type": "hall", "polygon": _rect(0.1, 0.1, 1.9, 2.9)}]
    ops = [{"id": "win_wc", "type": "window", "level_id": "L0", "wall_id": "w_lw_n", "center": [1.0, 5.0],
            "width": 0.6, "height": 0.6, "sill_height": 1.5},
           {"id": "win_in", "type": "window", "level_id": "L0", "wall_id": "w_mid", "center": [2.0, 1.5],
            "width": 1.0, "height": 1.2, "sill_height": 0.9}]
    return {"levels": [{"id": "L0", "order": 0, "elevation": 0.0, "ceiling_height": 2.7}], "walls": walls,
            "rooms": rooms, "openings": ops, "furniture": []}


def test_a_light_well_is_open_air_and_a_party_wall_takes_no_opening():
    from wenart.blender import architect_actions as AA

    b = _light_well_plan()
    plan = AA.Plan(b)
    assert AA.Plan.is_outside(plan.room["r_lw"]) and AA.is_open_air(plan.room["r_lw"])
    assert plan.outer_runs(plan.walls["w_party"], "r_wc") == []                  # the party wall has no outer run
    assert plan.outer_runs(plan.walls["w_lw_n"], "r_wc")                          # the light well's wall has one
    ok, why = AA.act_move_window(plan, "W2", {}, "win_wc")
    assert ok and "already looks outside" in why and b["openings"][0]["wall_id"] == "w_lw_n"
    AA.act_move_window(plan, "W2", {}, "win_in", "r_bed")
    assert next(o for o in b["openings"] if o["id"] == "win_in")["wall_id"] != "w_party"


# --------------------------------------------------------------------------- R03-02 / BP-02: slabs with no closed union
def test_a_level_with_no_closed_wall_union_gets_its_slab_from_the_walls_outline():
    from wenart.sheets import to_building as TB

    levels = [{"id": f"L{k}", "order": k, "elevation": 3.0 * k, "evidence": [{"file": "x.dwg"}]} for k in range(3)]
    furniture = [{"id": "f_st", "level_id": "L0", "type": "stair",
                  "footprint": {"center": [5.0, 5.0], "size": [1.2, 4.0], "rotation_deg": 0.0}}]
    warns = []
    slabs = TB.slabs_block({}, levels, {}, furniture, 0.2, warns.append)        # no union: no slab
    assert slabs == []
    sq = [(0.0, 0.0), (12.0, 0.0), (12.0, 10.0), (0.0, 10.0)]
    slabs = TB.slabs_block({}, levels, {}, furniture, 0.2, warns.append, outline_of=lambda lid: sq)
    assert [s["id"] for s in slabs] == ["sl_L0", "sl_L1", "sl_L2"]
    s1 = next(s for s in slabs if s["id"] == "sl_L1")
    assert s1["inferred"] and s1["status"] == "assumed" and s1["openings"]          # the stair void of L0's stair


# --------------------------------------------------------------------------- R03-03: the entrance must reach the core
def _rf():
    from tests import test_review_fixes_20261113 as RF
    return RF


def test_a_drawn_entrance_into_a_sealed_wind_lobby_is_asked_never_answered_by_its_label():
    """R03-03 (real03): the drawn front door opens into the Rüzgarlık, which no door joins to the core hall: the label
    does not answer the entrance; no door is cut into the core elsewhere; the open point is raised."""
    from wenart import building as B
    from wenart.ingest import core_rules as CR

    RF = _rf()
    b = RF.core_building(("L0", "L1"))
    for r in b["rooms"]:
        if r["id"] == "L0_hall":
            r["polygon"] = [[4.1, 1.6], [7.9, 1.6], [7.9, 5.9], [6.3, 5.9], [6.3, 7.9], [4.1, 7.9]]
    b["walls"].append(RF.wall("L0_rz", (4, 1.5), (8, 1.5)))
    b["rooms"].append(RF.room("L0_rz", "Rüzgarlık", "other", RF.rect(4.1, 0.1, 7.9, 1.4)))
    b["openings"].append(RF.op("d_front", "door", "wL0_s", (6.0, 0.0), 1.2))                 # no door L0_rz -> hall
    b["site"]["entrances"] = [{"door_id": "d_front", "level_id": "L0", "room_id": "L0_rz", "rise": 0.0, "main": True}]
    rec = CR.fix_entrances(b, B.IdCounter().next, {})
    assert rec["added"] == [] and rec["open"] and "d_front" in rec["open"]


def test_an_inferred_entrance_never_goes_into_a_fire_stair():
    from wenart import building as B
    from wenart.ingest import core_rules as CR

    RF = _rf()
    b = RF.entrance_building()
    for r in b["rooms"]:
        if r["id"] == "L-1_hall":
            r.update(label="Yangın Merdiveni", room_type="stair")
    rec = CR.fix_entrances(b, B.IdCounter().next, {})
    assert all(a["level_id"] != "L-1" or "L-1_hall" not in a["reason"] for a in rec["added"])


# --------------------------------------------------------------------------- R03-01: the storeys a DWG's blocks give
def _dwg(path, info_level="93.20", other=None):
    """A DXF inserting only the ground-floor plan 'D BLOK_ZK' (its datum '93.20'); defined, unused: the building-info
    block, a section with marks every 3.20 m and a basement at -4.00 (and -5.00 below it, no storey)."""
    import ezdxf

    doc = ezdxf.new()
    plan = doc.blocks.new("D BLOK_ZK")
    plan.add_text("93.20")
    plan.add_text("+0.00")
    info = doc.blocks.new("XX_BİNA BİLGİLERİ")
    info.add_mtext(f"D BLOK\\P1BK+ZK+12K\\PBİNA GİRİŞ KOTU : {info_level}")
    if other:
        info.add_mtext(other)
    sec = doc.blocks.new("D BLOK KESİTLER")
    for v in ("-5.00", "-4.00", "0.00", "+3.20", "+6.40", "+9.60", "+12.80", "+16.00"):
        sec.add_text(v)
    doc.modelspace().add_blockref("D BLOK_ZK", (0, 0))
    doc.saveas(path)
    return path


def test_the_unused_blocks_of_the_same_building_give_its_storeys_pitch_and_basement(tmp_path):
    from wenart.sheets import dwg_blocks as DB

    got = DB.read(_dwg(tmp_path / "a.dxf"), {93.2})
    assert got["count"] == 13 and got["basements"] == 1 and got["pitch_m"] == 3.2
    assert got["basement_floors_m"] == [-4.0]
    assert {e["block"] for e in got["evidence"]} >= {"XX_BİNA BİLGİLERİ", "D BLOK KESİTLER"}
    assert DB.read(_dwg(tmp_path / "b.dxf", info_level="94.50"), {93.2}) is None     # another building's entrance
    # a second info text naming another block with the same level does not count; the plan's own building does
    got = DB.read(_dwg(tmp_path / "c.dxf", other="C BLOK\\P2BK+ZK+4K\\PBİNA GİRİŞ KOTU : 93.20"), {93.2})
    assert got["count"] == 13 and got["basements"] == 1


def test_the_title_keeps_the_basements_apart_and_a_fire_lobby_is_no_walk_up():
    texts = [(SimpleNamespace(text=t, entity="e", point=(0, 0), layer=None), "f") for t in ("1BK+ZK+12K",)]
    got = ST.title_counts(texts)
    assert got[0]["count"] == 13 and got[0]["basements"] == 1
    assert ST.title_counts([(SimpleNamespace(text="Z+4", entity="e", point=(0, 0), layer=None), "f")])[0]["basements"] == 0
    sig = {"lifts": 0, "flat_words": 8, "kitchens": 0, "stairs": 0, "stair_words": 2, "fire": 2, "fire_stair": 1,
           "fire_lobby": 1}
    assert ST.building_type(sig, False) == "apartment_block_lift"
    assert ST.building_type(dict(sig, fire_lobby=0), False) == "apartment_block"


def test_a_listed_basement_no_plan_draws_is_recorded_with_its_marked_floor():
    rec, warns = {}, []
    chosen = {"rung": "dwg_blocks", "count": 13, "basements": 1, "basement_floors_m": [-4.0], "pitch_m": 3.2,
              "confidence": 0.6, "evidence": [{"rule": "dwg_building_info"}], "note": "1BK+ZK+12K"}
    read = [SimpleNamespace(level={"order": 0}, use="read")]
    ST._basements(rec, chosen, read, warns)
    assert rec["basements"] == 1 and rec["basements_inferred"][0]["level_id"] == "L-1"
    assert rec["basements_inferred"][0]["floor_m"] == -4.0 and rec["basements_inferred"][0]["floor_marked"]
    rec2 = {}
    ST._basements(rec2, dict(chosen, basement_floors_m=[], pitch_m=None), read, warns)
    assert rec2["basements_inferred"][0]["floor_m"] == -3.0 and not rec2["basements_inferred"][0]["floor_marked"]


def test_the_floors_only_assumed_take_the_pitch_of_the_dwg_sections():
    from wenart.sheets import heights as HT

    levels = [{"id": f"L{k}", "order": k} for k in range(3)]
    out = {"levels": [], "slabs": []}
    HT._assumed_levels(out, levels, 2.7, 0.2, "no section")
    lines = HT.apply_pitch(out, levels, 3.2, 0.2, "a.dwg", "the unused sections")
    z = {e["level_id"]: e["floor_z"]["value"] for e in out["levels"]}
    assert z == {"L0": 0.0, "L1": 3.2, "L2": 6.4} and lines
    assert out["levels"][1]["ceiling_height"]["value"] == 3.0
    assert out["levels"][1]["floor_z"]["evidence"][0]["method"] == "inferred"


def test_an_inferred_basement_is_the_footprint_with_the_core_and_no_window():
    from wenart.ingest import basement as BS

    RF = _rf()
    b = RF.core_building(("L0",))
    b["levels"][0]["evidence"] = [{"file": "x.dwg", "method": "vector", "confidence": 1.0}]
    b["walls"] = [dict(w, exterior=w["id"].startswith("wL0_")) for w in b["walls"]]
    b["openings"].append(RF.op("win_k", "window", "wL0_w", (0.0, 2.0), 1.2))
    b["furniture"].append({"id": "f_L0_st", "level_id": "L0", "room_id": "L0_hall", "type": "stair",
                           "footprint": {"center": [5.2, 3.0], "size": [2.0, 4.0], "rotation_deg": 0.0}})
    rec = {"basements_inferred": [{"level_id": "L-1", "order": -1, "floor_m": -3.0, "floor_marked": False,
                                   "rule": "title", "confidence": 0.6, "evidence": [], "reason": "basement 1 of 1"}]}
    warns = []
    made = BS.apply(SimpleNamespace(building=b, warn=warns.append, unions={}), rec, 0.2)
    assert made and made[0]["level_id"] == "L-1"
    lv = next(x for x in b["levels"] if x["id"] == "L-1")
    assert lv["kind"] == "basement" and lv["elevation"] == -3.0 and lv["reading_confidence"] == "low"
    rooms = [r for r in b["rooms"] if r["level_id"] == "L-1"]
    kinds = {r["room_type"] for r in rooms}
    assert {"hall", "shaft", "storage"} <= kinds and not kinds & {"kitchen", "bedroom", "living", "bathroom"}
    ops = [o for o in b["openings"] if o["level_id"] == "L-1"]
    assert ops and all(o["type"] != "window" for o in ops) and any(o.get("lift_door") for o in ops)
    walls = {w["id"]: w for w in b["walls"] if w["level_id"] == "L-1"}
    assert all(walls[o["wall_id"]].get("exterior") is not True for o in ops)          # no outside door
    assert any(f["level_id"] == "L-1" and f["type"] == "stair" for f in b["furniture"])
    assert all(x.get("inferred") for x in rooms + ops + list(walls.values()))
    assert any(s["id"] == "sl_L-1" for s in b["slabs"])


def test_lift_shafts_carved_after_a_walk_up_count_reopen_the_storey_question():
    b = {"levels": [{"id": "L0", "order": 0}], "rooms": [{"id": "r1", "level_id": "L0", "label": "Asansör",
                                                           "room_type": "shaft", "polygon": [[0, 0], [2, 0], [2, 2], [0, 2]]}]}
    rec = {"rule": "type_default", "signals": {"lifts": 0}, "ladder": [{"rung": "type_default", "kind": "apartment_block"}],
           "open_point": {"options": [1, 2, 3], "default": 3, "severity": "major", "question": "?"}}
    got = CP._late_lifts(b, rec)
    assert got and got["default_with_lift"] == ST.TYPE_DEFAULTS["apartment_block_lift"]
    assert ST.TYPE_DEFAULTS["apartment_block_lift"] in rec["open_point"]["options"]


# --------------------------------------------------------------------------- R20-02, R20-04, R21-01: the ground cut
def test_the_slab_over_a_cut_ground_floor_covers_the_footprint_and_cut_walls_stop_at_its_line():
    from tests import test_ground_floor_20261113 as TG

    b = TG.building()
    b["slabs"].append({"id": "sl_L1", "below_level_id": "L0", "above_level_id": "L1", "outline": TG.rect(0, 0, 12, 7.8)})
    out = TG.run(b, TG.drawn(*TG.FOOT))
    s1 = next(s for s in b["slabs"] if s["id"] == "sl_L1")
    assert max(y for _x, y in s1["outline"]) == 8.5 and s1["adjusted_by_ai"]["rule"] == "ground_cut"
    assert out["cut"]["slab_above_extended"]["slab"] == "sl_L1"
    walls = {w["id"]: w for w in b["walls"]}
    for wid in ("w_L0_x4", "w_L0_x8"):                     # they cross the footprint line: they stop at it
        assert max(walls[wid]["start"][1], walls[wid]["end"][1]) <= 8.51


def test_a_moved_window_slides_along_the_new_wall_instead_of_being_dropped():
    from shapely.geometry import Polygon as P

    from wenart import building as B
    from wenart.ingest import ground_floor as GF

    r = {"id": "r_bed", "level_id": "L0", "label": "Oda", "room_type": "bedroom",
         "polygon": [[0.1, 0.1], [3.9, 0.1], [3.9, 8.3], [0.1, 8.3]]}
    new = {"id": "w_new", "level_id": "L0", "start": [0.0, 8.4], "end": [4.0, 8.4], "thickness": 0.2, "exterior": True}
    b = {"levels": [{"id": "L0", "order": 0}], "rooms": [r], "walls": [new], "openings": [], "site": {}}
    level = CP.Level(b, "L0")
    o = {"id": "win_old", "type": "window", "level_id": "L0", "center": [3.36, 9.9], "width": 1.4, "height": 1.4}
    build = SimpleNamespace(ids=B.IdCounter())
    got = GF._move_window(build, b, level, dict(o, center=[3.36, 8.35]), [new], {"r_bed": P(r["polygon"])}, "cut",
                          {"entities": [], "layer": None})
    assert got is not None and abs(got["center"][0] - 3.2) < 1e-6 and "moved 0.16 m" in got["inference"]["reason"]


def test_a_new_facade_wall_stops_at_the_party_walls_outer_face():
    from shapely.geometry import box as bx

    from wenart.ingest import ground_floor as GF

    new = {"id": "w_new", "start": [0.0, 9.9], "end": [12.25, 9.9], "thickness": 0.2}
    party = {"id": "w_p", "start": [12.0, 0.0], "end": [12.0, 10.5], "thickness": 0.2, "exterior": True,
             "party_wall": {"text": "bitişik"}}
    assert GF._stop_at_party([new], [party], bx(0, 0, 12.25, 10)) == ["w_new"]
    assert abs(new["end"][0] - 12.1) < 1e-6 and new["start"] == [0.0, 9.9]


# --------------------------------------------------------------------------- R21-02: the inferred stair's void and box
def test_an_inferred_stair_box_fits_its_room_and_its_landing_is_assumed():
    from shapely.geometry import box as bx

    from wenart.blender import stair_access as SA
    from wenart.ingest import core_rules as CR

    fp = {"center": [5.92, 14.425], "size": [1.8, 4.75], "rotation_deg": 0.0}           # y 12.05-16.80
    got = CR.fit_to_room(fp, bx(5.0, 12.30, 6.9, 16.55))
    assert abs(got["size"][1] - 4.25) < 1e-6 and abs(got["center"][1] - 14.425) < 1e-6
    st = CR.stair_dict(got, "inferred", "U", 3.0)
    assert st["landing_assumed"] is True
    up = {"id": "f_L1", "level_id": "L1", "type": "stair", "inferred": True, "stair": dict(st, landing_assumed=False)}
    low = {"id": "f_L0", "level_id": "L0", "type": "stair", "stair": st}
    b = {"levels": [{"id": "L0", "order": 0, "elevation": 0.0}, {"id": "L1", "order": 1, "elevation": 3.0}],
         "furniture": [low, up], "walls": []}
    assert SA.upper_match(b, low) is None                    # an inferred stair above is no drawn evidence


# --------------------------------------------------------------------------- R09-8, R10-P4, OL-05: below ground
def test_an_at_grade_basement_is_not_underground_and_a_tin_counts_its_lowest_point():
    lv = {"id": "L-1", "order": -1, "kind": "basement", "elevation": -3.0, "ceiling_height": 2.8}
    vec = {"value": -3.0, "method": "vector", "confidence": 1.0}
    b = {"site": {"ground": {"levels": [{"side": "south", "z": vec}]}}, "warnings": []}
    assert CP.below_ground(b, lv) is None                       # the drawn ground at its floor: a garden storey
    assert "inferred" in CP.below_ground({"site": {}, "warnings": []}, lv)        # no ground read: the kind counts
    b = {"site": {"ground": {"levels": [{"z": {"value": 0.5, "method": "vector", "confidence": 1.0}}]},
                  "entrances": [{"level_id": "L-1", "below_ground": False, "rise": 0.15}]}, "warnings": []}
    assert CP.below_ground(b, lv) is None                       # an outside entrance at grade on it
    tin = {"surface": {"kind": "tin", "points": [[0, 0, 2.36], [9, 0, 3.94], [0, 9, 3.9], [9, 9, 3.94]],
                       "flat_z": 3.54}}
    l0 = {"id": "L0", "order": 0, "kind": "floor", "elevation": 0.0, "ceiling_height": 3.3}
    assert CP.below_ground({"site": {"ground": tin}, "warnings": []}, l0) is None
    assert CP._ground_min({"site": {"ground": tin}}) == 2.36


# --------------------------------------------------------------------------- R09-2, R09-6: R37 both ways, twins
def _tag_building(elev=0.0, kind="door", width=1.2):
    from tests import test_entrance_tags_20261113 as TT

    b = TT.building()
    b["levels"][0]["elevation"] = elev
    b["rooms"] = [TT.room("r_a", "Yatak Odası", "bedroom", TT.rect(5.1, 0.1, 9.9, 5.9)),
                  TT.room("r_b", "Yatak Odası", "bedroom", TT.rect(0.1, 0.1, 4.9, 5.9))]
    b["openings"] = [{"id": "o_a", "type": kind, "level_id": "L0", "wall_id": "s", "center": [7.5, 0.0], "width": width,
                      "evidence": [{"method": "vector"}]},
                     {"id": "o_b", "type": kind, "level_id": "L0", "wall_id": "s", "center": [2.5, 0.0], "width": width,
                      "evidence": [{"method": "vector"}]}]
    b["site"] = {"entrances": [], "ground": {"levels": [{"z": {"value": 0.0, "method": "vector", "confidence": 1.0}}]}}
    return b


def test_the_untagged_mirror_twin_of_a_tagged_door_becomes_the_same_window():
    from wenart.ingest import core_rules as CR

    b = _tag_building()
    out = CR.size_tags(b, {"L0": [{"text": "P:120/150", "x": 7.6, "y": -0.4}]})
    ops = {o["id"]: o for o in b["openings"]}
    assert ops["o_a"]["type"] == ops["o_b"]["type"] == "window"
    assert ops["o_b"]["adjusted_by_ai"]["rule"] == "window_tag_twin" and len(out["windows"]) == 2


def test_a_door_tag_on_an_outer_window_at_grade_makes_it_that_door_never_on_an_upper_storey():
    from wenart.ingest import core_rules as CR

    texts = {"L0": [{"text": "K:80/210", "x": 7.6, "y": -0.4}]}
    b = _tag_building(kind="window", width=0.75)
    CR.size_tags(b, texts)
    ops = {o["id"]: o for o in b["openings"]}
    assert ops["o_a"]["type"] == "door" and ops["o_a"]["width"] == 0.8 and ops["o_b"]["type"] == "window"
    b = _tag_building(elev=3.0, kind="window", width=0.75)                 # an upper storey: no door into the air
    CR.size_tags(b, texts)
    assert all(o["type"] == "window" for o in b["openings"])


# --------------------------------------------------------------------------- R09-7: nothing stays from a refused ground
def test_a_refused_ground_leaves_no_light_well_or_entrance_at_its_height():
    from wenart.ingest import ground_lines as GL

    b = {"site": {"ground": {"levels": [], "light_wells": [
        {"opening_id": "w1", "source": "assumed", "top_z": 11.113, "floor_z": -0.05},
        {"opening_id": "w2", "source": "drawn", "top_z": 11.113, "floor_z": -0.05}]},
        "entrances": [{"door_id": "d1", "threshold_z": 0.0, "ground_z": 11.113, "rise": -11.113, "below_ground": True,
                       "reason": "the door is 11.11 m below the ground"}]}}
    how = GL.refresh(b, [11.113], -2.5)
    assert how and [w["opening_id"] for w in b["site"]["ground"]["light_wells"]] == ["w2"]
    e = b["site"]["entrances"][0]
    assert e["ground_z"] == -2.5 and e["rise"] == 2.5 and e["below_ground"] is False


# --------------------------------------------------------------------------- R20-05, R20-06
def test_a_door_the_drawn_storey_keeps_stays_on_its_copies():
    import copy

    from tests import test_s1fix_20261113 as T1

    b = T1._copy_building()
    # L0 the inferred ground floor, L1 the drawn storey, L2 its copy (as real20)
    b["levels"][0]["storey_inference"] = {"rule": "type_default"}
    b["levels"][1].pop("storey_inference")
    b["levels"][1]["order"] = 1
    lv2 = copy.deepcopy(b["levels"][1])
    lv2.update(id="L2", order=2, elevation=6.0, storey_inference={"rule": "type_default"},
               reading_places=[{"kind": "unplaced_label", "text": "SALON", "at": [12.6, 1.5]}])
    b["levels"].append(lv2)
    for key in ("walls", "rooms", "openings"):
        b[key] += [dict(copy.deepcopy(x), id=x["id"].replace("L1", "L2"), level_id="L2",
                        **({"wall_id": x["wall_id"].replace("L1", "L2")} if "wall_id" in x else {}))
                   for x in b[key] if x["level_id"] == "L1"]
    rec = CP.copy_doors(b)
    acts = {x["opening"]: x["action"] for x in rec}
    assert acts.get("d_L2_air") == "kept"                    # the drawn L1 keeps d_L1_air: one decision per plan


def test_the_entrance_hall_closes_a_flats_second_door_into_it():
    from tests import test_ground_floor_20261113 as TG

    b = TG.building()
    # the east salon gets its own door from the core hall and a second door into the front room (the future hall)
    b["walls"].append(TG.wall("w_L0_y6e", (8, 6), (12, 6)))
    b["openings"].append({"id": "d_L0_fe", "type": "door", "level_id": "L0", "wall_id": "w_L0_x8", "center": [8.0, 8.0],
                          "width": 0.9, "evidence": [{"method": "vector"}]})
    out = TG.run(b, TG.drawn(*TG.FOOT))
    hall = out["entrance_hall"]
    assert hall["rooms"] == ["r_L0_front"]
    assert [x["opening"] for x in hall.get("closed") or []] == ["d_L0_fe"]
    assert all(o["id"] != "d_L0_fe" for o in b["openings"])
    assert any(x["kind"] == "entrance_hall_rooms" for x in b.get("needs_review") or [])


# --------------------------------------------------------------------------- R21-03: a read door's tag is its own
def test_a_door_tag_a_read_door_claims_does_not_keep_a_core_gap_open():
    from wenart.ingest import core_rules as CR

    RF = _rf()
    b = RF.core_building(("L0",))
    b["openings"] += [RF.gap("g_bed", "L0_8", (8.0, 4.8), 0.9), RF.op("d_x", "door", "L0_8", (8.0, 3.2), 1.0)]
    texts = {"L0": [{"text": "100/210", "x": 8.2, "y": 3.8}]}
    out = CR.close_core_gaps(b, None, texts)
    assert "g_bed" in [x["opening"] for x in out["closed"]] and not out["review"]


# --------------------------------------------------------------------------- R03-05: the copies' marks and RC12
def test_a_copys_marks_are_its_own_floors_and_rc12_lists_planned_changes_as_info():
    from wenart.levels import model as LMOD
    from wenart.levels import read as LR
    from wenart.reading_check import crossdoc as CD

    b = {"project": {}, "levels": [{"id": "L0", "order": 0, "elevation": 0.0},
                                   {"id": "L1", "order": 1, "elevation": 3.2, "typical_of": "L0"}]}
    texts = [{"text": "+0.00", "point": (1.0, 1.0), "level_id": lid,
              "evidence": {"file": "x.dwg", "method": "vector", "confidence": 1.0}} for lid in ("L0", "L1")]
    marks = LR.read_marks(texts, b, LMOD.level_params({}))["marks"]
    z = {m["level_id"]: m["z"] for m in marks}
    assert z == {"L0": 0.0, "L1": 3.2} and next(m for m in marks if m["level_id"] == "L1")["copy_of"]["level_id"] == "L0"
    bb = {"levels": b["levels"], "rooms": [{"id": f"r{k}", "level_id": f"L{k}"} for k in (0, 1)], "walls": [],
          "openings": [{"id": "d0", "level_id": "L0", "type": "door"},
                       {"id": "d1", "level_id": "L1", "type": "window", "drawn_type": "door",
                        "adjusted_by_ai": {"rule": "copy_door_window"}}]}
    got = [f for f in CD.rc12(bb) if f["check"] == "RC12"]
    assert got and all(f["severity"] == "info" for f in got) and "the drawn floor" in got[0]["message"]


# --------------------------------------------------------------------------- R09-5: no core door into a flat's room
def test_a_door_from_the_core_into_a_bedroom_with_its_own_flat_door_is_refused():
    from wenart.ingest import core_rules as CR

    RF = _rf()
    b = RF.core_building(("L0",))
    b["openings"].append(RF.op("d_leaf", "door", "L0_8", (8.0, 5.0), 1.52, operation="sliding"))
    got = CR.core_doors_into_flats(b)
    assert [x["opening"] for x in got] == ["d_leaf"]
    assert all(o["id"] != "d_leaf" for o in b["openings"])
    assert b["openings_merged"][-1]["corrected_by_ai"]["rule"] == "core_flat_door"
    assert any(o["id"] == "L0_ab" for o in b["openings"])                # the bedroom's own door stays


# --------------------------------------------------------------------------- R03-07: probes in another wall's solid
def test_stations_inside_another_walls_solid_do_not_keep_an_inner_wall_exterior():
    from wenart.ingest import sense_rules as SR

    RF = _rf()
    b = RF.building(("L0",))
    b["walls"] = RF.box_walls(0, 0, 10, 6) + [RF.wall("m", (5, 0), (5, 6), exterior=True),
                                             RF.wall("st", (3.5, 0.7), (6.5, 0.7), t=1.4)]
    b["rooms"] = [RF.room("r_l", "Salon", "living", RF.rect(0.1, 1.5, 4.9, 5.9)),
                  RF.room("r_r", "Oda", "bedroom", RF.rect(5.1, 1.5, 9.9, 5.9))]
    got = SR.exterior_flags(b)
    assert any(x["wall"] == "m" and x["exterior"] is False for x in got)
