"""Bathroom sense (26 Oct 2026; user: "fix should be general, it is not a fix for real06, it must be a fix for the
project"). real06's last pod run is the test case; every rule here is general:

1. a room's pieces of a set member's type are that member, never added again: fixed equipment the fit hangs at its
   working top (a wall-hung washbasin, ``mount_bottom_m``) stays a floor piece (``schemas.off_floor``: set member,
   obstacle, clearance); a set lacks no type the room holds (``groups.room_held_types``, a library gap too); the
   solver adopts the pieces it keeps (``groups.held_types``); ``place_group`` on a set the room has completes it;
   a bare gap in an outer wall with drawn fixed equipment in front of it is no passage (``blocked_gaps``);
2. no children's product outside a child's room, no product of another use (a kitchen, utility or composite sink as a
   washbasin) in the fit (``fit.use_misfit``, a gate with its logged reason);
3. a stroke of an outline that a text covers whole (a "50" over a basin's bowl) is drawing, not a glyph
   (``symbols.under_text``): real06's ground-floor basin is read again.
CPU only; the real06 data are trimmed fixtures (no runs/, no LibreDWG).
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from shapely.geometry import box

import _m11_room as M
from wenart.furniture import edit_ops as E
from wenart.furniture import fit as F
from wenart.furniture import group_checks as GC
from wenart.furniture import groups as GR
from wenart.furniture import placer as P
from wenart.furniture import program as PR
from wenart.furniture import schemas as S
from wenart.furniture import solver as SV
from wenart.ingest.generic import symbols as SY
from wenart.ingest.generic.model import Stroke, TextRun
from test_furniture_fit_v2 import FakeCatalog, model, piece

ROOM = M.ROOM_ID
FIXTURES = Path(__file__).resolve().parent / "fixtures"
REAL06_BATH = FIXTURES / "real06_bathroom_20261026.json"
REAL06_STROKES = FIXTURES / "real06_bathroom_strokes_20261026.json"
HUNG = {"mount_bottom_m": 0.3, "mount_source": "fit: a wall-hung model at its working top"}
META = {"reason": "test", "round": 1, "log_seq": 1, "model": "mock"}


def bathroom(*pieces, **kw) -> dict:
    """A 2.6 x 2.4 m bathroom (door on the south wall at x = 1.0, no window)."""
    b = M.building(w=2.6, h=2.4, room_type="bathroom", window=None, furniture=list(pieces), **kw)
    b["rooms"][0]["label"] = "Banyo"
    return b


def toilet(**kw):
    """Its back on the east wall, facing west."""
    return M.fp("t1", "toilet", (2.25, 0.75), (0.4, 0.7), rotation=270.0, **kw)


def basin(pid, x, size=(0.6, 0.45), **kw):
    """On the north wall, facing south."""
    return M.fp(pid, "washbasin", (x, 2.4 - size[1] / 2.0), size, rotation=0.0, **kw)


def types_added(cands) -> list[list[str]]:
    return [sorted(p["type"] for p in c["pieces"]) for c in cands]


# --------------------------------------------------------------------------
# 1. A room's pieces of a member's type are that member
# --------------------------------------------------------------------------

def test_fixed_equipment_hung_at_its_working_top_stays_a_floor_piece():
    hung = basin("w1", 0.5, **HUNG)
    assert not S.off_floor(hung) and not S.off_floor(basin("w2", 1.3))
    assert S.off_floor(M.fp("c1", "wall_cabinet", (1, 2), (0.6, 0.35), mount_bottom_m=1.45))
    assert S.off_floor(dict(hung, mount_bottom_m=1.5))                     # hung above the floor's use
    assert S.off_floor(M.fp("s1", "shoe_cabinet", (1, 2), (0.8, 0.3), mount_bottom_m=0.4))   # not fixed equipment
    b = bathroom(toilet(), hung)
    assert [f["id"] for f in GR._built_floor(b, ROOM)] == ["t1", "w1"]
    assert "w1" in [f["id"] for f in SV._fixed_items(b, ROOM, set())]       # an obstacle for the solver


def test_two_drawn_basins_are_the_sets_washbasins_never_a_third():
    b = bathroom(toilet(), basin("w1", 0.5, **HUNG), basin("w2", 1.3, size=(0.5, 0.4), **HUNG))
    (g,) = GR.group_members(b, ROOM)
    assert g["anchor_id"] == "t1" and g["member_ids"] == ["w1", "w2"] and g["missing"] == ["shower|bathtub"]
    prog = PR.room_program(b, ROOM)
    (row,) = prog["groups"]
    assert row["drawn"] and row["missing"] == ["shower|bathtub"]
    cands = SV.solve_room(b, ROOM, prog)
    assert cands and all("washbasin" not in t and "toilet" not in t for t in types_added(cands))


def test_a_drawn_basin_the_fit_left_unbuilt_is_still_the_sets_washbasin():
    gap = basin("w1", 0.5, build=False, asset={"method": "none", "asset_id": None})
    b = bathroom(toilet(), gap)
    assert GR.holds_piece(gap) and GR.room_held_types(b, ROOM) == {"toilet", "washbasin"}
    (g,) = GR.group_members(b, ROOM)
    assert "washbasin" not in g["missing"]
    # a piece recorded as not furniture, or untyped, holds nothing
    assert not GR.holds_piece(dict(gap, inferred_as="detail")) and not GR.holds_piece(dict(gap, type="unknown"))
    assert not GR.holds_piece(dict(gap, build=False, asset={"method": "parametric"}))


def test_the_solver_adopts_the_pieces_it_keeps_for_a_new_set_entry():
    # a set entry that names no members (the agent's place_group before the fix): the room's drawn basin and toilet
    # are adopted, only the missing bath member is placed
    b = bathroom(toilet(), basin("w1", 0.5, **HUNG))
    entry = PR._entry(ROOM, "bathroom_set", True, ["shower", "bathtub"])
    cands = SV.solve_room(b, ROOM, {"room_id": ROOM, "zones": [], "groups": [entry], "reason": "test"})
    assert all("washbasin" not in t and "toilet" not in t for t in types_added(cands))


def test_place_group_on_a_room_with_its_set_completes_it():
    b = bathroom(toilet(), basin("w1", 0.5, **HUNG), basin("w2", 1.3, size=(0.5, 0.4)))
    res = E.apply_edit(b, dict({"op": "place_group", "room_id": ROOM, "group": "bathroom_set"}, **META))
    assert res["accepted"], res["failed_checks"]
    new = [f for f in res["building"]["furniture"] if f["source"] == "added_by_ai"]
    assert [f["type"] for f in new] == ["shower"]
    assert new[0]["group"]["group_id"] == f"{ROOM}.bathroom_set"            # the room's set, not a second one
    # a complete set is never placed again
    full = bathroom(toilet(), basin("w1", 0.5, **HUNG), M.fp("s1", "shower", (0.45, 0.45), (0.9, 0.9)))
    res = E.apply_edit(full, dict({"op": "place_group", "room_id": ROOM, "group": "bathroom_set"}, **META))
    assert not res["accepted"] and "never a second set" in " ".join(res["failed_checks"]) + res["message"]


def test_a_relayout_replaces_an_added_basin_the_fit_hung():
    b = bathroom(toilet(), M.fp("a1", "washbasin", (0.5, 2.175), (0.6, 0.45), source="added_by_ai", **HUNG))
    assert E._ai_floor_ids(b, ROOM) == ["a1"]
    out = SV.apply_candidate(b, ROOM, {"pieces": [], "kept_ids": []})
    assert [f["id"] for f in out["furniture"]] == ["t1"]


def test_a_bare_gap_behind_a_drawn_fixture_is_no_passage():
    gap = {"id": "o1", "type": "opening", "level_id": "L0", "wall_id": "w_n", "center": [0.5, 2.45], "width": 1.0,
           "status": "unverified", "evidence": []}
    b = bathroom(toilet(), basin("w1", 0.5))
    b["openings"].append(gap)
    room = b["rooms"][0]
    ctx = P.room_context(b, room)
    assert set(GC.blocked_gaps(b, room, ctx)) == {"o1"} and GC.entrance_door(b, room, ctx) == "d1"
    rep = GC.walkway_report(b, room, ctx, [], [])
    assert all("o1" not in (a, c) for a, c, *_rest in rep["pairs"])
    # no fixture in front of it: a gap (a passage or a window the architect decides); a door is never blocked
    clear = bathroom(toilet())
    clear["openings"].append(gap)
    assert GC.blocked_gaps(clear, clear["rooms"][0], P.room_context(clear, clear["rooms"][0])) == {}
    door = bathroom(toilet(), basin("w1", 0.5))
    door["openings"].append(dict(gap, type="door"))
    assert GC.blocked_gaps(door, door["rooms"][0], P.room_context(door, door["rooms"][0])) == {}


def test_real06_upper_bathroom_keeps_its_two_drawn_basins_and_gets_its_shower():
    """The pod's fitted building (run 20261026-125412-full, trimmed): the fit hung both drawn basins
    (f_L1_025 0.6 x 0.6 m, f_L1_029 0.53 x 0.34 m); the completion added a third washbasin f_L1_038 beside them."""
    b = json.loads(REAL06_BATH.read_text(encoding="utf-8"))
    rid = "r_L1_banyo"
    basins = [f for f in b["furniture"] if f["type"] == "washbasin"]
    assert sorted(f["id"] for f in basins) == ["f_L1_025", "f_L1_029"] and all(f.get("mount_bottom_m") for f in basins)
    (g,) = GR.group_members(b, rid)
    assert g["anchor_id"] == "f_L1_028" and g["member_ids"] == ["f_L1_025", "f_L1_029"]
    assert g["missing"] == ["shower|bathtub"]
    room = next(r for r in b["rooms"] if r["id"] == rid)
    ctx = P.room_context(b, room)
    assert set(GC.blocked_gaps(b, room, ctx)) == {"o_L1_004"} and GC.entrance_door(b, room, ctx) == "d_L1_009"
    cands = SV.solve_room(b, rid, PR.room_program(b, rid))
    assert cands and types_added(cands)[0] == ["shower"]
    assert all("washbasin" not in t for t in types_added(cands))
    assert not [v for v in GC.check_room(b, rid) if v["check"] == "G11" and "o_L1_004" in v["message"]]


# --------------------------------------------------------------------------
# 2. Products made for another user or use are no candidates
# --------------------------------------------------------------------------

def test_children_and_other_use_products_by_title_and_material():
    toddler = model("toddler", "washbasin", 0.46, 0.36, 0.59, title="TODDLER SINK")
    kitchen = model("kitchen", "washbasin", 0.86, 0.43, 0.17, title="Sink Kitchen Sink Built-in Sink Einbauspüle")
    utility = model("utility", "washbasin", 0.6, 0.5, 0.4, title="Laundry utility tub")
    commercial = model("abey", "washbasin", 0.82, 0.48, 0.18, title="EC100 - Single Bowl Sink - Commercial Sinkware")
    combo = model("combo", "washbasin", 0.57, 0.54, 0.47, title="Combo CEG-50BF",
                  material_slots=[{"index": 0, "name": "Black_Composite", "material": "other", "share": 0.93},
                                  {"index": 1, "name": "Stainless_Steel", "material": "metal", "share": 0.05}])
    plain = model("plain", "washbasin", 0.6, 0.45, 0.5, title="Cooke &amp; Lewis Lanzo Square Cloakroom Basin")
    vessel = model("vessel", "sink_kitchen", 0.5, 0.4, 0.2, title="Bathroom Vessel Sink")
    assert "children's product" in F.use_misfit(toddler, "washbasin")
    assert F.use_misfit(toddler, "washbasin", child_room=True) is None          # a child's room may take it
    for e in (kitchen, utility, commercial):
        assert "another use" in F.use_misfit(e, "washbasin")
    assert "composite" in F.use_misfit(combo, "washbasin") and F.use_misfit(combo, "sink_kitchen") is None
    assert F.use_misfit(plain, "washbasin") is None and "another use" in F.use_misfit(vessel, "sink_kitchen")
    kids_desk = model("kidsdesk", "desk", 1.2, 0.6, 0.75, title="Kids Taylor Walnut Desk")
    assert F.use_misfit(kids_desk, "desk") and F.use_misfit(kids_desk, "desk", child_room=True) is None


def test_the_fit_never_takes_a_toddler_sink_for_an_adult_bathroom():
    toddler = model("toddler", "washbasin", 0.5, 0.4, 0.86, title="TODDLER SINK", quality=5.0)
    plain = model("plain", "washbasin", 0.52, 0.42, 0.86, title="Wash-basin", quality=3.0)
    cat = FakeCatalog([toddler, plain])
    p = piece("washbasin", 0.5, 0.4)
    asset = F.fit_piece(p, cat)
    assert asset["asset_id"] == "abo_plain"
    (ex,) = [x for x in asset["excluded"] if x["id"] == "abo_toddler"][:1]
    assert ex["rule"] == F.USE_RULE and "children's product" in ex["reason"]
    assert F.fit_piece(dict(p, child_room=True), cat)["asset_id"] == "abo_toddler"     # a child's room: it fits best
    alone = F.fit_piece(p, FakeCatalog([toddler]))
    assert alone["method"] != "library" or alone["asset_id"] != "abo_toddler"


def test_fit_building_reads_the_child_room_from_the_room_subtype():
    toddler = model("toddler", "washbasin", 0.5, 0.4, 0.86, title="TODDLER SINK", quality=5.0)
    plain = model("plain", "washbasin", 0.52, 0.42, 0.86, title="Wash-basin", quality=3.0)
    cat = FakeCatalog([toddler, plain])
    b = {"project": {"id": "t"}, "furniture": [piece("washbasin", 0.5, 0.4)],
         "rooms": [{"id": "r_L0_salon", "room_type": "bathroom", "room_subtype": None, "polygon": []}]}
    assert F.fit_building(b, cat)["furniture"][0]["asset"]["asset_id"] == "abo_plain"
    b["rooms"][0]["room_subtype"] = "child"
    assert F.use_context(b, b["furniture"][0]) == {"child_room": True}
    fitted = F.fit_building(b, cat)
    assert fitted["furniture"][0]["asset"]["asset_id"] == "abo_toddler"
    F.assert_only_assets_changed(b, fitted)


# --------------------------------------------------------------------------
# 3. A text over an outline does not cut it
# --------------------------------------------------------------------------

def _fixture_page():
    data = json.loads(REAL06_STROKES.read_text(encoding="utf-8"))
    strokes = [Stroke(s["id"], s["kind"], [tuple(p) for p in s["pts"]], s["closed"], layer=s["layer"], arc=s["arc"])
               for s in data["strokes"]]
    t = data["text"]
    return strokes, TextRun(t["id"], t["text"], tuple(t["box"]), t["height"])


def _read(strokes, texts):
    notes = []
    pieces, cands, _decor = SY.furniture(strokes, set(), [], [], texts, [], box(-1, -1, 4, 3), [], level_id="L0",
                                         file_rel="real06.dwg", page_no=1, units_to_m=1.0, notes=notes)
    return pieces, cands, notes


def test_real06_ground_floor_basin_is_read_under_its_text():
    """real06's ground-floor bathroom: the text '50' covers the basin's bottom arc ARC:2958A9 whole; dropped as a
    glyph, the basin's ellipse did not close and merged into the vanity + quadrant shower outline (2.54 x 1.01 m, an
    untyped piece), so the drawn basin was never built and the completion added one elsewhere."""
    strokes, text = _fixture_page()
    _pieces, cands, notes = _read(strokes, [text])
    sizes = sorted(tuple(round(v, 3) for v in c["item"].size) for c in cands)
    assert (0.531, 0.342) in sizes
    bowl = next(c for c in cands if tuple(round(v, 3) for v in c["item"].size) == (0.531, 0.342))
    assert "washbasin" in bowl["fits"] and "ARC:2958A9" in bowl["item"].evidence["entity"]
    assert any("kept: they continue a drawn outline under the text" in n and "ARC:2958A9" in n for n in notes)
    outline = next(c for c in cands if c is not bowl)
    assert "ARC:29589A" not in outline["item"].evidence["entity"]


def test_glyphs_and_open_lines_under_a_text_stay_out():
    strokes, text = _fixture_page()
    x0, y0, x1, y1 = text.box
    # the digits' own strokes: a closed '0' and a '5' that ends inside the box
    glyphs = [Stroke("G:5a", "line", [(x0 + 0.03, y0 + 0.08), (x0 + 0.06, y0 + 0.08)]),
              Stroke("G:5b", "line", [(x0 + 0.03, y0 + 0.08), (x0 + 0.03, y0 + 0.05)]),
              Stroke("G:0", "polyline", [(x0 + 0.07, y0 + 0.02), (x0 + 0.1, y0 + 0.02), (x0 + 0.1, y0 + 0.08),
                                         (x0 + 0.07, y0 + 0.08)], closed=True)]
    segs = SY._segments(glyphs + strokes, set())
    inside = [s for s in segs if s.stroke.id.startswith("G:") or s.stroke.id == "ARC:2958A9"]
    outside = [s for s in segs if s not in inside]
    back = {inside[i].stroke.id for i in SY.under_text(inside, outside)}
    assert back == {"ARC:2958A9"}
    # a line under a text that joins the drawing at both ends but closes no outline of a piece stays a glyph
    line = [Stroke("L:a", "line", [(0.0, 0.0), (1.0, 0.0)]), Stroke("L:in", "line", [(1.0, 0.0), (1.05, 0.0)]),
            Stroke("L:b", "line", [(1.05, 0.0), (2.0, 0.0)])]
    segs = SY._segments(line, set())
    assert SY.under_text(segs[1:2], [segs[0], segs[2]]) == set()


def test_without_the_text_the_basin_reads_the_same():
    strokes, text = _fixture_page()
    _p, with_text, _n = _read(copy.deepcopy(strokes), [text])
    _p, without, _n = _read(strokes, [])
    assert sorted(tuple(round(v, 3) for v in c["item"].size) for c in with_text) == \
        sorted(tuple(round(v, 3) for v in c["item"].size) for c in without)



def test_sanitary_ware_in_a_loud_colour_is_not_taken():
    """26 Oct 2026 (merge): an "arancione glass sink" won a basin of a calm modern bathroom; a fixture whose title
    names a loud colour stays out (a white or chrome one is kept)."""
    from wenart.furniture import fit as FIT
    loud = {"id": "x", "title": "Regia Juke Box Light 882000-28 arancione glass sink"}
    assert "loud colour" in FIT.use_misfit(loud, "washbasin", False)
    assert FIT.use_misfit({"id": "y", "title": "Cooke & Lewis Lanzo white basin"}, "washbasin", False) is None
    assert FIT.use_misfit(loud, "vase", False) is None                    # decor may be an accent


def test_a_counter_with_a_basin_in_a_bathroom_is_its_vanity():
    """26 Oct 2026 (full suite with LibreDWG): real03's bathroom vanities with their basin's drain were read as a
    kitchen counter and a kitchen sink, and every such bathroom got an open kitchen. In a wet room the counter is the
    washbasin (a vanity unit) and the sink inside it its basin; a kitchen's sink cabinet keeps its type."""
    from types import SimpleNamespace
    from wenart.ingest.generic import reading as RD

    def piece(pid, ftype, room, c, s):
        return {"id": pid, "type": ftype, "type_method": "rule", "room_id": room, "evidence": [{"file": "x.dwg"}],
                "footprint": {"center": c, "size": s, "rotation_deg": 0.0}}

    b = {"rooms": [{"id": "bath", "room_type": "bathroom", "polygon": [[0, 0], [3, 0], [3, 3], [0, 3]]},
                   {"id": "kit", "room_type": "kitchen", "polygon": [[3, 0], [6, 0], [6, 3], [3, 3]]}],
         "furniture": [piece("c", "kitchen_counter", "bath", [1.0, 0.25], [1.0, 0.5]),
                       piece("s", "sink_kitchen", "bath", [1.0, 0.3], [0.5, 0.4]),
                       piece("k", "kitchen_counter", "kit", [4.0, 0.3], [0.9, 0.6])]}
    build = SimpleNamespace(building=b, warn=lambda text: None)
    assert sorted(RD.wet_room_vanities(build)) == ["c", "s"]
    by = {f["id"]: f for f in b["furniture"]}
    assert by["c"]["type"] == "washbasin" and by["c"]["drawn_type"] == "kitchen_counter"
    assert by["s"]["build"] is False and by["s"]["replaced_by"] == "c"
    assert by["k"]["type"] == "kitchen_counter"
    assert RD.kitchen_zones(build) == 0 and "zones" not in b["rooms"][0]      # no open kitchen in the bathroom
