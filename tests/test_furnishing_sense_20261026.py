"""Furnishing sense (26 Oct 2026; user: "fix should be general, it is not a fix for real06, it must be a fix for the
project"). real06 is the test case; every rule here is general:

A. a kitchen is never empty: an untyped unbuilt drawn piece is no solver obstacle; short outline jogs are merged before
   the kitchen legs are built; a compact run of real module sizes is the fallback; a kitchen that still gets no run is
   a critical finding (the layout record, the building's warnings, G9 critical);
B. a zoned room keeps its own type's groups outside its zones (a bedroom with a misread kitchen zone keeps its bed);
C. at most one dining group per room: drawn tables that touch are one table, a second drawn table set is reported and
   gets nothing added, no dining group is planned beside a drawn one;
D. one model per role of a group (the chairs of a table take one model, fitted on their median drawn size);
E. taste: misfits (folding, camping, outdoor pieces indoors, bar stools as dining chairs) rank last, a dining-group
   model of a style outside the family's compatible styles ranks later.
CPU only.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import _m11_room as M
from wenart.furniture import fit as F
from wenart.furniture import group_checks as GC
from wenart.furniture import groups as GR
from wenart.furniture import layout as L
from wenart.furniture import locked as LK
from wenart.furniture import program as PR
from wenart.furniture import solver as SV
from test_furniture_fit_v2 import FakeCatalog, model, piece

ROOM = M.ROOM_ID
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "real06_kitchen_20261026.json"


def fp(pid, ftype, center, size, front, **kw):
    return M.fp(pid, ftype, center, size, rotation=(front + 90.0) % 360.0, front=front, **kw)


def table(pid, center, size, rotation=0.0):
    """A drawn dining table (no front)."""
    return M.fp(pid, "table_dining", center, size, rotation=rotation, front=None)


# --------------------------------------------------------------------------
# A. A kitchen is never empty
# --------------------------------------------------------------------------

def test_an_untyped_unbuilt_drawn_piece_is_no_solver_obstacle():
    untyped = fp("u1", "unknown", (2.0, 2.0), (2.0, 1.5), 0.0, build=False, not_built_reason="untyped")
    gap = fp("s1", "sofa", (2.5, 0.5), (2.0, 0.9), 90.0, build=False)            # typed, not built: still there
    odd = fp("u2", "unknown", (4.0, 3.0), (0.5, 0.5), 0.0)                          # untyped but not marked unbuilt
    b = M.building(furniture=[untyped, gap, odd])
    ids = [f["id"] for f in SV._fixed_items(b, ROOM, set())]
    assert ids == ["s1", "u2"]
    assert SV.untyped_unbuilt(untyped) and not SV.untyped_unbuilt(gap) and not SV.untyped_unbuilt(odd)
    assert [f["id"] for f in SV._fixed_items(b, ROOM, {"u1"})] == ["u1", "s1", "u2"]   # fixed on purpose: kept


def test_short_outline_jogs_are_merged_onto_the_inner_wall_line():
    # the back wall steps 4.6 cm in at x = 2 (real06's kitchen): one 4 m wall on the inner line
    segs = SV.run_outline([((0.0, 0.0), (4.0, 0.0)), ((4.0, 0.0), (4.0, 3.0)), ((4.0, 3.0), (2.0, 3.0)),
                           ((2.0, 3.0), (2.0, 2.954)), ((2.0, 2.954), (0.0, 2.954)), ((0.0, 2.954), (0.0, 0.0))])
    assert len(segs) == 4
    assert [tuple(round(v, 3) for v in a) for a, _b in segs] == [(0.0, 0.0), (4.0, 0.0), (4.0, 2.954), (0.0, 2.954)]
    # the step the other way: the wall before it is the inner line
    segs = SV.run_outline([((0.0, 0.0), (4.0, 0.0)), ((4.0, 0.0), (4.0, 2.954)), ((4.0, 2.954), (2.0, 2.954)),
                           ((2.0, 2.954), (2.0, 3.0)), ((2.0, 3.0), (0.0, 3.0)), ((0.0, 3.0), (0.0, 0.0))])
    assert [tuple(round(v, 3) for v in a) for a, _b in segs] == [(0.0, 0.0), (4.0, 0.0), (4.0, 2.954), (0.0, 2.954)]
    # a 0.25 m step is a real wall: kept
    deep = [((0.0, 0.0), (4.0, 0.0)), ((4.0, 0.0), (4.0, 3.0)), ((4.0, 3.0), (2.0, 3.0)), ((2.0, 3.0), (2.0, 2.75)),
            ((2.0, 2.75), (0.0, 2.75)), ((0.0, 2.75), (0.0, 0.0))]
    assert len(SV.run_outline(deep)) == 6


def test_fallback_runs_are_never_offered_by_the_program_and_validate():
    fallbacks = SV.fallback_options("kitchen_run")
    assert fallbacks == ["I_compact_fallback", "L_compact_fallback", "galley_compact_fallback"]
    prog = PR.room_program(M.building(w=4.0, h=5.0, room_type="kitchen"), ROOM)
    run = next(g for g in prog["groups"] if g["group"] == "kitchen_run")
    assert not set(fallbacks) & set(run["options"])
    data = copy.deepcopy(GR.config())
    data["groups"]["kitchen_run"]["options"]["I_compact_fallback"]["auto"] = True
    assert any("a fallback option is a run option with auto: false" in p for p in GR.validate_config(data))
    lim = SV.run_limits(SV._option_run(GR.load_groups()["kitchen_run"], "I_compact_fallback"))
    assert (lim["i_min"], lim["landing_min"], lim["triangle"]) == (2.1, 0.3, "soft")
    assert SV.run_limits(GR.load_groups()["kitchen_run"]["run"]) == SV.RUN_LIMITS      # a full run: unchanged


def narrow_kitchen() -> dict:
    """A 1.7 x 3.0 m kitchen: the door swing takes the start of both long walls, a low window the back wall; no
    3.0 m I, no L corner with 1.2 m legs and no galley (1.7 m wide) fits; the west wall holds 2.33 m."""
    return M.building(w=1.7, h=3.0, room_type="kitchen", door_x=1.2, window=(1.1, 0.8), sill=0.5)


def test_a_kitchen_without_room_for_a_full_run_gets_a_compact_one():
    b = narrow_kitchen()
    best = SV.solve_room(b, ROOM, PR.room_program(b, ROOM))[0]
    assert not best["hard_failures"] and f"{ROOM}.kitchen_run" in best["placed"]
    assert best["options"][f"{ROOM}.kitchen_run"] == "I_compact_fallback"
    run = [p for p in best["pieces"] if p["group"]["group"] == "kitchen_run"]
    assert {"fridge", "sink_kitchen", "stove", "kitchen_counter"} <= {p["type"] for p in run}
    widths = sorted({round(p["footprint"]["size"][0], 2) for p in run if p["type"] != "kitchen_counter"})
    assert set(widths) <= {0.45, 0.6}                                     # real module sizes
    after = SV.apply_candidate(b, ROOM, best)
    found = [v for v in GC.check_room(after, ROOM) if v["check"] in ("G8", "G9")]
    assert found and all(v["severity"] == "minor" for v in found)        # landings / triangle scored, not refused
    assert {v["metrics"].get("tier") for v in found if "landing" in v["message"] or "triangle" in v["message"]} == {
        "compact_run"}
    rec = L.layout_room(b["rooms"][0], b, "scandinavian", None)
    assert rec.pieces and rec.critical == [] and not any("critical" in w for w in b["warnings"])


def test_a_kitchen_that_holds_no_run_at_all_is_a_critical_finding():
    b = M.building(w=2.0, h=2.4, room_type="kitchen", door_x=1.4, window=(1.0, 0.7), sill=0.5)
    rec = L.layout_room(b["rooms"][0], b, "scandinavian", None)
    assert not rec.pieces and len(rec.critical) == 1
    c = rec.critical[0]
    assert (c["severity"], c["kind"], c["group_id"]) == ("critical", "kitchen_without_run", f"{ROOM}.kitchen_run")
    assert "not even a compact one" in c["reason"] and rec.to_dict()["critical"] == rec.critical
    assert any(w.startswith(f"{ROOM}: critical: the kitchen of {ROOM} got no counter run") for w in b["warnings"])
    g9 = [v for v in GC.check_room(b, ROOM) if v["check"] == "G9"]
    assert len(g9) == 3 and {v["severity"] for v in g9} == {"critical"}   # an empty kitchen: critical
    assert all(v["metrics"]["empty_kitchen"] for v in g9)
    # a kitchen with a drawn counter that misses its hob stays major (as before)
    part = M.building(w=3.5, h=4.0, room_type="kitchen",
                      furniture=[fp("k1", "kitchen_counter", (1.75, 3.68), (2.4, 0.6), 270.0)])
    assert {v["severity"] for v in GC.check_room(part, ROOM) if v["check"] == "G9"} == {"major"}


def test_real06_kitchen_gets_a_run():
    """The real06 kitchen (24.8 m², a stair, an untyped 3.99 x 2.40 m unbuilt drawn piece over two walls, a 4.6 cm
    jog in the back wall): before, "no candidate position fits the room" and the render had an empty kitchen."""
    b = json.loads(FIXTURE.read_text(encoding="utf-8"))
    best = SV.solve_room(b, "r_L0_mutfak", PR.room_program(b, "r_L0_mutfak"))[0]
    assert not best["hard_failures"] and "r_L0_mutfak.kitchen_run" in best["placed"]
    types = [p["type"] for p in best["pieces"] if p["group"]["group"] == "kitchen_run"]
    assert {"fridge", "sink_kitchen", "stove"} <= set(types)
    drawn = {f["id"] for f in b["furniture"]}
    assert not any(p["id"] in drawn for p in best["pieces"])             # the drawn pieces stay as drawn


def test_a_full_run_is_kept_where_it_fits():
    b = M.building(w=3.5, h=4.0, room_type="kitchen", window=(1.75, 1.0), sill=1.0)
    best = SV.solve_room(b, ROOM, PR.room_program(b, ROOM))[0]
    assert best["options"][f"{ROOM}.kitchen_run"] not in SV.fallback_options("kitchen_run")
    assert not best.get("compact_fallback")


# --------------------------------------------------------------------------
# B. A zoned room keeps its own groups
# --------------------------------------------------------------------------

def zoned(room_type: str, w: float, h: float, zone_w: float, kind: str = "kitchen", **kw) -> dict:
    b = M.building(w=w, h=h, room_type=room_type, **kw)
    b["rooms"][0]["zones"] = [{"zone_id": f"{ROOM}_{kind}", "kind": kind,
                               "polygon": [[0.0, 0.0], [zone_w, 0.0], [zone_w, h], [0.0, h]]}]
    return b


def test_a_bedroom_with_a_kitchen_zone_keeps_its_bed():
    prog = PR.room_program(zoned("bedroom", 4.0, 4.0, 1.5), ROOM)
    groups = {(g["group"], g["zone_id"]) for g in prog["groups"]}
    assert ("kitchen_run", f"{ROOM}_kitchen") in groups
    assert ("sleeping_double", None) in groups and ("storage", None) in groups   # the rest: 10 m² of bedroom
    bed = next(g for g in prog["groups"] if g["group"] == "sleeping_double")
    assert bed["required"] and bed["area"] == 10.0 and bed["group_id"] == f"{ROOM}.sleeping_double"


def test_a_living_room_with_an_open_kitchen_keeps_its_seating_and_one_dining_group():
    prog = PR.room_program(zoned("living", 8.0, 5.0, 3.0), ROOM)
    names = [(g["group"], g["zone_id"]) for g in prog["groups"]]
    assert ("seating", None) in names and ("kitchen_run", f"{ROOM}_kitchen") in names
    dining = [g for g in prog["groups"] if g["group"] == "dining"]
    assert len(dining) == 1 and dining[0]["zone_id"] is None                 # not one per zone and one per room


def test_the_rest_place_is_left_out_when_a_zone_is_of_the_room_kind():
    from shapely.geometry import Polygon

    room = Polygon([(0, 0), (8, 0), (8, 5), (0, 5)])
    zones = [Polygon([(0, 0), (3, 0), (3, 5), (0, 5)]), Polygon([(3, 0), (8, 0), (8, 5), (3, 5)])]
    assert PR.rest_place("living", room, 40.0, zones, ["kitchen", "living"]) is None
    place = PR.rest_place("living", room, 40.0, zones[:1], ["kitchen"])
    assert place[0] is None and place[1] == "living" and place[2] == 25.0
    assert PR.rest_place("bedroom", room, 40.0, [room], ["kitchen"]) is None   # nothing left


# --------------------------------------------------------------------------
# C. One dining group per room
# --------------------------------------------------------------------------

def two_table_sets() -> dict:
    chairs_a = [fp("a1", "chair", (1.0, 1.6), (0.45, 0.45), 0.0), fp("a2", "chair", (1.6, 1.6), (0.45, 0.45), 0.0),
                fp("a3", "chair", (1.0, 3.0), (0.45, 0.45), 180.0), fp("a4", "chair", (1.6, 3.0), (0.45, 0.45), 180.0)]
    chairs_b = [fp("b1", "chair", (5.0, 1.6), (0.45, 0.45), 0.0)]
    return M.building(w=7.0, h=5.0, room_type="dining", furniture=[
        table("ta", (1.3, 2.3), (1.2, 0.8), 0.0), *chairs_a,
        table("tb", (5.0, 2.3), (0.8, 0.8), 0.0), *chairs_b])


def test_a_second_drawn_table_set_is_reported_and_gets_nothing():
    b = two_table_sets()
    prog = PR.room_program(b, ROOM)
    dining = [g for g in prog["groups"] if g["group"] == "dining"]
    assert len(dining) == 2 and all(g["drawn"] for g in dining)            # no dining group planned beside them
    main = next(g for g in dining if g["anchor_id"] == "ta")
    second = next(g for g in dining if g["anchor_id"] == "tb")
    assert second["missing"] == [] and second["note"].startswith("second drawn table set in the room (main: ta)")
    assert main["note"] == ""
    assert [t["anchor_id"] for t in prog["second_tables"]] == ["tb"] and prog["second_tables"][0]["main"] == "ta"
    L.layout_room(b["rooms"][0], b, "scandinavian", None, purpose="complete")
    assert sum("drawn table_dining tb is a second table set in the room beside ta" in w for w in b["warnings"]) == 1


def test_drawn_tables_that_touch_are_one_table():
    t1 = table("t1", (1.6, 2.0), (0.8, 0.8), 0.0)
    t2 = table("t2", (2.4, 2.0), (0.8, 0.8), 0.0)
    t3 = table("t3", (4.0, 3.0), (0.8, 0.8), 30.0)    # its own angle: not one table
    t4 = table("t4", (4.0, 1.97), (0.8, 0.8), 0.0)    # touches t3 only at another angle
    b = M.building(w=6.0, h=4.0, room_type="dining", furniture=[t1, t2, t3, t4])
    source = copy.deepcopy(b)
    assert [[f["id"] for f in c] for c in GR.touching_tables(b, ROOM)] == [["t1", "t2"]]
    done = GR.merge_touching_tables(b)
    assert [(d["table_id"], d["merged"], d["moved_m"]) for d in done] == [("t1", ["t2"], 0.4)]
    by_id = {f["id"]: f for f in b["furniture"]}
    one, gone = by_id["t1"], by_id["t2"]
    assert one["footprint"]["size"] == [1.6, 0.8] and one["footprint"]["center"] == [2.0, 2.0]
    assert one["drawn_footprint"] == source["furniture"][0]["footprint"] and one["drawn_type"] == "table_dining"
    assert one["adjusted_by_ai"]["rule"] == "merge_tables" and one["adjusted_by_ai"]["merged"] == ["t2"]
    assert gone["build"] is False and gone["merged_into"] == "t1" and gone["footprint"] == source["furniture"][1][
        "footprint"] and gone["adjusted_by_ai"]["merged_into"] == "t1"
    assert by_id["t3"] == source["furniture"][2] and by_id["t4"] == source["furniture"][3]
    assert LK.check(source, b, "complete") == []                              # the locked check accepts the merge
    # one dining group for the merged table (t3 / t4 are the reported second sets)
    prog = PR.room_program(b, ROOM)
    assert "t2" not in {g["anchor_id"] for g in prog["groups"]}
    assert {t["anchor_id"] for t in prog["second_tables"]} == {"t3", "t4"}


def test_a_merge_that_would_move_the_table_too_far_is_left_as_drawn():
    t1 = table("t1", (1.5, 2.0), (1.0, 1.0), 0.0)
    t2 = table("t2", (2.5, 2.0), (1.0, 1.0), 0.0)    # the merged centre moves 0.5 m: ok
    t3 = table("t3", (3.5, 2.0), (1.0, 1.0), 0.0)    # three in a row: 1.0 m: too far
    b = M.building(w=6.0, h=4.0, room_type="dining", furniture=[t1, t2, t3])
    assert GR.merge_touching_tables(b) == []
    two = M.building(w=6.0, h=4.0, room_type="dining", furniture=[copy.deepcopy(t1), copy.deepcopy(t2)])
    assert [d["moved_m"] for d in GR.merge_touching_tables(two)] == [0.5]


# --------------------------------------------------------------------------
# D. One model per role of a group
# --------------------------------------------------------------------------

def chair(pid: str, w: float, d: float = 0.45) -> dict:
    p = piece("chair", w, d, pid=pid)
    p["group"] = {"group_id": "r_L0_salon.dining", "group": "dining", "role": "partner", "anchor_id": "t1"}
    return p


def test_the_chairs_of_one_table_take_one_model():
    narrow = model("narrow", "chair", 0.46, 0.45, 0.85)
    wide = model("wide", "chair", 0.54, 0.50, 0.85)
    building = {"furniture": [chair("c1", 0.46), chair("c2", 0.52), chair("c3", 0.54), chair("c4", 0.54)]}
    alone = F.fit_building({"furniture": [dict(chair("c1", 0.46), group=None)]}, FakeCatalog([narrow, wide]))
    assert alone["furniture"][0]["asset"]["asset_id"] == "abo_narrow"        # on its own the narrow chair wins
    fitted = F.fit_building(building, FakeCatalog([narrow, wide]))
    assert {p["asset"]["asset_id"] for p in fitted["furniture"]} == {"abo_wide"}
    rs = fitted["furniture"][0]["asset"]["role_set"]
    assert rs["used"] is True and rs["members"] == ["c1", "c2", "c3", "c4"] and rs["median_size"] == [0.53, 0.45]
    assert rs["group_id"] == "r_L0_salon.dining" and rs["type"] == "chair"
    assert F.role_sets(building) == {("r_L0_salon.dining", "chair"): ["c1", "c2", "c3", "c4"]}


def test_a_member_the_set_model_cannot_fit_is_fitted_on_its_own():
    small = model("small", "chair", 0.38, 0.45, 0.85)
    wide = model("wide", "chair", 0.54, 0.50, 0.85)
    building = {"furniture": [chair("c1", 0.38), chair("c2", 0.54), chair("c3", 0.54)]}
    fitted = F.fit_building(building, FakeCatalog([small, wide]))
    picks = {p["id"]: p["asset"]["asset_id"] for p in fitted["furniture"]}
    assert picks == {"c1": "abo_small", "c2": "abo_wide", "c3": "abo_wide"}
    assert fitted["furniture"][0]["asset"]["role_set"]["used"] is False
    # a pinned member and the anchor are no set members
    pinned = dict(chair("c4", 0.54), asset_pin="abo_small")
    anchor = dict(chair("c5", 0.54), group={"group_id": "r_L0_salon.dining", "role": "anchor"})
    assert F.role_sets({"furniture": [pinned, anchor, chair("c6", 0.5)]}) == {}


# --------------------------------------------------------------------------
# E. Taste: misfits last, compatible styles in a dining group
# --------------------------------------------------------------------------

def test_misfit_words_by_type_and_room():
    folding = {"id": "a", "title": "Wooden IKEA folding chair"}
    garden = {"id": "b", "title": "Garden Chair"}
    bar = {"id": "c", "title": "Chair. Bar stool"}
    audit = {"id": "d", "title": "Park bench", "audit": {"notes": ["the title says park: an outdoor piece"]}}
    plain = {"id": "e", "title": "Rivet Mid-Century Modern Wood Dining Chair", "audit": {"notes": ["barely visible"]}}
    assert "folding" in F.misfit_of(folding, "chair") and "garden" in F.misfit_of(garden, "chair")
    assert "bar" in F.misfit_of(bar, "chair") and F.misfit_of(bar, "bar_stool") is None
    assert "outdoor" in F.misfit_of(audit, "bench") and F.misfit_of(plain, "chair") is None
    assert F.misfit_of(garden, "chair", outdoor=True) is None               # open-air rooms: outdoor ranking


def test_compatible_styles_of_a_family():
    assert F.compatible_styles("scandinavian") == {"scandinavian", "minimal", "modern", "neutral", "japandi"}
    table = {"id": "t", "title": "Ravenna Home Traditional Dining Table, Rustic Honey Pine",
             "styles": ["scandinavian", "minimal", "modern"]}
    assert F.style_mix_of(table, "table_dining", "scandinavian") == ["classic", "rustic"]
    assert F.style_mix_of({"id": "c", "styles": ["minimal", "rustic", "scandinavian"]}, "chair", "scandinavian") == [
        "rustic"]
    assert F.style_mix_of({"id": "j", "styles": ["japandi", "scandinavian"]}, "chair", "scandinavian") == []
    assert F.style_mix_of(table, "sofa", "scandinavian") == [] and F.style_mix_of(table, "chair", None) == []


def test_a_folding_chair_ranks_after_every_other_chair():
    folding = model("fold", "chair", 0.5, 0.5, 0.85, title="Wooden folding chair")
    plain = model("plain", "chair", 0.55, 0.52, 0.85)                       # 10 % off the drawn size
    gen = model("gen", "chair", 0.5, 0.5, 0.85, source="generated")
    flags = F.taste_flags([folding, plain, gen], "chair", False, None)
    order = [e["id"] for e in F.rank_candidates([folding, plain, gen], 0.5, 0.5, flags=flags)]
    assert order == ["abo_plain", "generated_gen", "abo_fold"]
    fit = F.fit_piece(piece("chair", 0.5, 0.5), FakeCatalog([folding, plain]))
    assert fit["asset_id"] == "abo_plain" and "taste_flags" not in fit
    only = F.fit_piece(piece("chair", 0.5, 0.5), FakeCatalog([folding]))      # never a gate
    assert only["asset_id"] == "abo_fold" and "folding" in only["taste_flags"]["misfit"]


def test_a_dining_table_of_another_style_ranks_later():
    farm = model("farm", "table_dining", 1.6, 0.9, 0.75, styles=("scandinavian",),
                 title="Traditional Farmhouse Dining Table")
    plain = model("plain", "table_dining", 1.7, 0.95, 0.76, styles=("scandinavian",))    # 6 % off the drawn size
    fit = F.fit_piece(piece("table_dining", 1.6, 0.9), FakeCatalog([farm, plain]), style_family="scandinavian")
    assert fit["asset_id"] == "abo_plain"
    no_family = F.fit_piece(piece("table_dining", 1.6, 0.9), FakeCatalog([farm, plain]))
    assert no_family["asset_id"] == "abo_farm"                              # without a family: no style rule


def test_drawn_pieces_of_one_type_in_a_room_take_one_model():
    """26 Oct 2026 (the big loop's first finding: a grey dining armchair, brown leather ones and a red egg chair in
    real06's living room): drawn armchairs outside a group join the room's seating set of armchairs, or form a set of
    their own; a piece of another size stays alone."""
    from wenart.furniture import fit as FIT

    def arm(pid, room, size, group=None):
        return {"id": pid, "type": "armchair", "room_id": room, "source": "from_documents",
                "footprint": {"center": [0, 0], "size": size}, **({"group": group} if group else {})}

    g = {"group_id": "r1.seating", "role": "partner"}
    b = {"furniture": [arm("a1", "r1", [0.92, 0.77], g), arm("a2", "r1", [0.92, 0.77], g),
                       arm("a3", "r1", [0.92, 0.62]), arm("a4", "r1", [0.92, 0.77]),
                       arm("b1", "r2", [0.80, 0.80]), arm("b2", "r2", [0.82, 0.78]),
                       arm("c1", "r3", [0.80, 0.80]), arm("c2", "r3", [1.40, 0.90])]}
    sets = FIT.role_sets(b)
    assert sets[("r1.seating", "armchair")] == ["a1", "a2", "a3", "a4"]
    assert sets[("room:r2", "armchair")] == ["b1", "b2"]
    assert not any(k[0] == "room:r3" for k in sets)
