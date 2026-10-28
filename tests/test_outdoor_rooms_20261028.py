"""Outdoor rooms dressed for outside and enough ceiling light (28 Oct 2026, user on real04 run 20261028-005318-full:
"makes no sense to have that table with the carpet outside, that's outside area" (the roof terrace r_L1_teras got the
"Ravenna Home Traditional Dining Table", two indoor dining chairs and a wool runner rug) and "More lights from the
ceiling needed" (the 50.9 m² living and dining room had one pendant over its 3.35 m table, the halls none)). CPU,
pure; the real04 cases read the committed results when they are there."""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest

from wenart.agent import causes as CS
from wenart.audit import kinds as K
from wenart.audit import sense as SE
from wenart.blender import architect_actions as AA
from wenart.blender import architect_details as AD
from wenart.blender import furniture as BF
from wenart.blender import geom2d
from wenart.blender import looks as LK
from wenart.blender import model_review as MR
from wenart.blender import outdoor as OD
from wenart.blender import parametric as P
from wenart.furniture import ceiling_lights as CL
from wenart.furniture import decor as D
from wenart.furniture import decor_ai as DA
from wenart.furniture import fit as F
from wenart.furniture import solver as SV
from wenart.style import recipe as RC

from test_decor_ai import applied, choose
from test_decor_m8 import RID, room_building
from test_furniture_fit_v2 import FakeCatalog, model, piece

ROOT = Path(__file__).resolve().parents[1]
REAL04 = ROOT / "results" / "furniture" / "real04"


class Catalog(FakeCatalog):
    def entry(self, asset_id):
        return next((e for e in self.entries if e["id"] == asset_id), None)


RAVENNA = dict(title="Amazon Brand – Ravenna Home Traditional Dining Table 29\"H, Gray and Rustic Honey Pine",
               material_tags=["wood"])
GUBI = dict(title="Gubi Beetle Dining Chair", material_tags=["metal"])
BISTRO = dict(title="AmazonBasics Armless Bistro Dining Chair - Set of 2, Beige, Premium Plastic")


# --------------------------------------------------------------------------
# Rule 2: an outdoor room's furniture is made for outside
# --------------------------------------------------------------------------

def test_outdoor_ready_reads_the_models_own_words_whole():
    assert OD.outdoor_ready(RAVENNA, "table_dining") == (False, "its name says inside (traditional)")
    ready, why = OD.outdoor_ready(GUBI, "chair")
    assert not ready and "material tags alone do not" in why               # an indoor chair tagged metal
    assert OD.outdoor_ready(BISTRO, "chair") == (True, "named for outside (bistro)")
    assert OD.outdoor_ready({"title": "Dining Table Reclaimed Teak", "material_tags": ["wood"]}, "table_dining")[0]
    assert not OD.outdoor_ready({"title": "Grattan 68 in. Ext Dining Table"}, "table_dining")[0]   # whole words
    assert OD.outdoor_grade({"title": "Grattan 68 in. Ext Dining Table"}) == 1          # was 0 ("rattan" inside it)
    # an upholstered type may carry its outdoor cushions, a hard one may not
    assert OD.outdoor_ready({"title": "Summerton Teak Loveseat with Cushions", "material_tags": ["wood", "fabric"]},
                            "sofa")[0]
    assert not OD.outdoor_ready({"title": "Mid-Century Beech and Rattan Dining Chair",
                                 "material_tags": ["wood", "fabric"]}, "chair")[0]
    assert not OD.outdoor_ready({"title": "Indoor plants"}, "chair")[0]
    # the 25 Oct grades stay (the ranking among the outdoor models reads them)
    assert [F.outdoor_grade(e) for e in ({"name": "Writing desk with 2 drawers"}, {"name": "Patio table"})] == [2, 0]


def test_open_air_rooms_are_known_by_type_or_by_the_sky():
    assert OD.open_air_room({"room_type": "balcony"}) and OD.open_air_room({"room_type": "Roof_Terrace"})
    assert OD.open_air_room({"room_type": "living", "open_to_sky": True})
    assert not OD.open_air_room({"room_type": "living"}) and not OD.open_air_room(None)


def _balcony_piece(ftype, w, d, pid="f_L1_001"):
    p = piece(ftype, w, d, pid=pid, source="added_by_ai")
    return dict(p, room_id="r_t", level_id="L1")


def test_the_fit_takes_only_outdoor_models_in_an_open_air_room():
    indoor = model("rav", "table_dining", 0.7, 0.7, 0.75, **RAVENNA)
    teak = model("teak", "table_dining", 0.75, 0.75, 0.74, title="Teak Garden Bistro Table")
    target = dict(_balcony_piece("table_dining", 0.7, 0.7), open_air_room=True)
    fit = F.fit_piece(target, Catalog([indoor, teak]))
    assert fit["asset_id"] == "abo_teak"
    gone = next(x for x in fit["excluded"] if x["id"] == "abo_rav")
    assert gone["rule"] == F.OUTDOOR_ROOM_RULE and "traditional" in gone["reason"]
    # the indoor model alone: no candidate is left, the ladder builds it (never the indoor model)
    only = F.fit_piece(target, Catalog([indoor]))
    assert only["method"] == "parametric" and "made for outside" in only["fallback_reason"]
    # indoors nothing changes: the exact-size model wins
    inside = F.fit_piece(dict(target, open_air_room=False), Catalog([indoor, teak]))
    assert inside["asset_id"] == "abo_rav"


def _terrace_building(room_type="balcony"):
    b = {"project": {"id": "t"}, "levels": [{"id": "L1", "elevation": 3.0, "ceiling_height": 2.7}],
         "walls": [], "openings": [],
         "rooms": [{"id": "r_t", "level_id": "L1", "room_type": room_type, "status": "verified", "label": "Teras",
                    "polygon": [[0, 0], [4, 0], [4, 5], [0, 5]]}],
         "furniture": [dict(_balcony_piece("table_dining", 0.7, 0.7), id="f_L1_001",
                            group={"group_id": "r_t.balcony", "group": "balcony", "role": "anchor"}),
                       dict(_balcony_piece("chair", 0.45, 0.45), id="f_L1_002",
                            group={"group_id": "r_t.balcony", "group": "balcony", "role": "chair"})]}
    return b


def test_fit_building_builds_a_weather_proof_family_when_no_outdoor_model_fits():
    cat = Catalog([model("rav", "table_dining", 0.7, 0.7, 0.75, **RAVENNA),
                   model("gubi", "chair", 0.45, 0.45, 0.85, **GUBI),
                   model("bistro", "chair", 0.47, 0.47, 0.82, **BISTRO)])
    b = _terrace_building()
    fitted = F.fit_building(b, cat)
    F.assert_only_assets_changed(b, fitted)
    table, chair = fitted["furniture"]
    assert table["asset"]["method"] == "parametric"
    build = table["asset"]["outdoor_build"]
    assert build["material_tags"] == ["metal"] and build["wood"] == OD.OUTDOOR_WOOD
    assert table["asset"]["outdoor"]["ready"] and table["asset"]["outdoor"]["rule"] == OD.OUTDOOR_RULE
    gap = table["library_gap"]                                   # the report lists it (CLAUDE.md library rules)
    assert gap["type"] == "table_dining" and "weather-proof" in gap["used"]
    assert chair["asset"]["asset_id"] == "abo_bistro" and chair["asset"]["outdoor"]["ready"]
    assert "table_dining" in F.fit_report(fitted) and "weather-proof" in F.fit_report(fitted)
    # the same pieces in a living room keep the drawn-size indoor models
    indoors = F.fit_building(_terrace_building("living"), cat)
    kept = indoors["furniture"][0]["asset"]
    assert kept["asset_id"] == "abo_rav" and "outdoor" not in kept


def test_the_weather_proof_design_reaches_the_parametric_builders():
    piece_ = {"type": "table_dining", "asset": {"method": "parametric", **OD.outdoor_asset(
        {"method": "parametric"}, "table_dining")}}
    design, notes = LK.outdoor_design(piece_, {"colour": "white", "wood": "wood_veneer_oak"}, [])
    assert design["wood"] == OD.OUTDOOR_WOOD and design["material_tags"] == ["metal"] and "colour" not in design
    assert notes and notes[-1].startswith("outdoor build")
    parts = P.build_parts("table_dining", 0.7, 0.7, 0.75, dict(piece_, design=design))
    assert {p["key"] for p in parts if p["role"] == "leg"} == {"steel"}
    assert {p["key"] for p in parts if p["role"] == "top"} == {"wood"}
    chair = {"type": "chair", "asset": OD.outdoor_asset({"method": "parametric"}, "chair")}
    cd, _ = LK.outdoor_design(chair, {}, [])
    assert P.chair_design(dict(chair, design=cd)) == {"frame": "steel", "seat": "wood", "base": "sled",
                                                      "back": "panel"}
    # a library piece and an indoor parametric piece keep their design
    lib = {"type": "chair", "asset": {"method": "library", "outdoor_build": {"wood": "x"}}}
    assert LK.outdoor_design(lib, {"wood": "oak"}, []) == ({"wood": "oak"}, [])


# --------------------------------------------------------------------------
# Rule 1: no rug, runner or carpet outside
# --------------------------------------------------------------------------

def _room(room_type):
    return room_building(4.0, 5.0, room_type, furniture=[("table_dining", (2.0, 2.5), 0.0, (0.9, 0.9)),
                                                         ("chair", (2.0, 1.6), 180.0, (0.45, 0.45)),
                                                         ("chair", (2.0, 3.4), 0.0, (0.45, 0.45))])


def test_no_rug_in_an_outdoor_room_from_any_stage():
    for kind in ("balcony", "terrace", "roof_terrace"):
        b = _room("balcony")                                 # the schema's outdoor room type; the others by name
        b["rooms"][0]["room_type"] = kind
        rugs, notes = D.rugs_for_room(b["rooms"][0], b["furniture"], b)
        assert rugs == [] and notes[0].startswith("no rug: an outdoor room")
    inside = _room("dining")
    assert D.rugs_for_room(inside["rooms"][0], inside["furniture"], inside)[0]      # a dining room keeps its rug
    assert SV._rug_dicts({"room_type": "terrace", "id": "x", "level_id": "L0"}, None, []) == []
    # whatever rule laid one: out, with the reason, in a room and on an outdoor space
    b = _room("balcony")
    b["decor"] = [{"id": "dec_L0_001", "type": "rug", "room_id": RID},
                  {"id": "dec_L0_002", "type": "vase", "room_id": RID},
                  {"id": "dec_L0_003", "type": "rug", "room_id": None, "outdoor_space": "os_v"}]
    gone = OD.strip_outdoor_textiles(b)
    assert [d["id"] for d in gone] == ["dec_L0_001", "dec_L0_003"] and [d["id"] for d in b["decor"]] == ["dec_L0_002"]
    assert all("makes no sense" in d["removed_reason"] for d in gone)


def test_the_ai_decorator_offers_only_outdoor_decor_on_a_terrace():
    b = _room("balcony")
    slots, _notes = DA.room_slots(b["rooms"][0], b["furniture"], b)
    assert not any(s.kind in ("rug", "window", "wall", "ceiling") for s in slots)
    assert all(set(s.types) <= set(DA.OUTDOOR_DECOR_TYPES) for s in slots)
    assert "no rug" in DA.ROOM_GUIDE["balcony"]
    # a room open to the sky is outside whatever its type
    b["rooms"][0].update(room_type="dining", open_to_sky=True)
    assert not any(s.kind == "rug" for s in DA.room_slots(b["rooms"][0], b["furniture"], b)[0])
    # the built-in outdoor recipes ask for no rug (the measured layer stays)
    assert "outdoor_rug" not in RC.default_recipe("terrace")["must"] and "outdoor_rug" in RC.OUTDOOR_LAYERS


def test_the_decor_stage_lays_no_rug_on_a_terrace():
    b = _room("balcony")
    out, records = applied(b, choose())
    assert not [d for d in out["decor"] if d["type"] == "rug"]
    assert OD.review(out)[0] == []


# --------------------------------------------------------------------------
# The check: model review M15, Argus, the agent loop
# --------------------------------------------------------------------------

def _dressed_wrong():
    b = _room("balcony")
    b["furniture"][0]["asset"] = {"method": "library", "asset_id": "abo_B07M6PKC6B", "title": RAVENNA["title"],
                                  "material_tags": ["wood"]}
    b["furniture"][1]["asset"] = {"method": "library", "asset_id": "abo_bistro", "title": BISTRO["title"]}
    b["decor"] = [{"id": "dec_L0_001", "kind": "decor", "type": "rug", "level_id": "L0", "room_id": RID,
                   "center": [2.0, 2.5], "size": [0.9, 2.5], "rotation_deg": 0.0,
                   "asset": {"title": "Heidi Floral Farmhouse Wool Runner Rug"}}]
    return b


def test_model_review_m13_finds_an_indoor_rug_and_an_indoor_model_outside():
    b = _dressed_wrong()
    got, n = OD.review(b)
    assert n == 4 and {f["target"] for f in got} == {"dec_L0_001", "f_L0_001"}
    assert all(f["check"] == "M15" and f["severity"] == "major" for f in got)
    rug = next(f for f in got if f["target"] == "dec_L0_001")
    assert "Runner Rug" in rug["message"] and "outdoor area" in rug["message"]
    table = next(f for f in got if f["target"] == "f_L0_001")
    assert "traditional" in table["message"] and table["metrics"]["kind_of_item"] == "indoor_model"
    rec = MR.review(b)
    assert "M15" in MR.CHECKS and rec["checks"]["M15"]["failed"] == 2
    assert K.kind_of({"check": "M15"}) == "no_sense" and K.kind_of({"check": "M16"}) == "taste"
    # the agent loop: the indoor model is swapped (the fit takes outdoor models only), the rug is the decor stage's
    assert CS.cause_of(table, b) == "wrong_model" and "swap_model" in CS.CAUSE_TOOLS["wrong_model"]
    assert CS.cause_of(rug, b) == "decor_model" and CS.REPORT_TO["decor_model"] == "decor"
    # Argus's sense line finds them on the building as built (a model review that predates M15 too)
    rows = SE.dressing(b)
    assert {(f["check"], f["target"]) for f in rows} >= {("M15", "dec_L0_001"), ("M15", "f_L0_001")}
    assert all(f["line"] == "sense" and f["kind"] in K.KINDS for f in rows)
    assert next(f for f in rows if f["target"] == "f_L0_001")["fix"] == "swap_model"


def test_the_architect_no_longer_passes_an_indoor_wood_table_as_hard_materials():
    b = _dressed_wrong()
    q = AD.outdoor_furniture(AA.Plan(b))
    by = {a["element"]: a for a in q["answers"]}
    assert "inside model" in by["f_L0_001"]["found"] and by["f_L0_001"].get("library_gap")
    assert "made for outside" in by["f_L0_002"]["found"]


# --------------------------------------------------------------------------
# Ceiling lights by room type and size
# --------------------------------------------------------------------------

def test_the_lumen_method_counts_the_lights_of_a_room():
    def room(t, area, **kw):
        s = math.sqrt(area)
        return dict({"room_type": t, "polygon": [[0, 0], [s, 0], [s, s], [0, s]]}, **kw)
    assert CL.lights_needed(room("living", 50.9))[0] == 6                    # real04's r_L-1_salon
    assert CL.lights_needed(room("living", 50.9), "sparse")[0] == 4         # a sparse style hangs fewer
    assert CL.lights_needed(room("living", 50.9), "layered")[0] == 8
    assert CL.lights_needed(room("hall", 11.9))[0] == 1 and CL.lights_needed(room("bedroom", 13.1))[0] == 2
    assert CL.lights_needed(room("wc", 1.6))[0] == 1                          # never none
    n, why = CL.lights_needed(room("kitchen", 13.6))
    assert n == 3 and why.startswith("lumen method: 100 lx x 13.6 m²")
    assert [CL.pendants_for_length(x) for x in (0.7, 1.6, 2.4, 3.35)] == [1, 2, 3, 4]
    assert CL.pendants_for_length(3.35, "sparse") == 3 and CL.pendants_for_length(9.0) == CL.PENDANT_MAX


def _salon():
    """A 9 x 5.6 m living and dining room: a 3.35 m table with an AI pendant at its middle, a sofa with its coffee
    table, a wardrobe, a door swinging in at the east wall."""
    b = room_building(9.0, 5.6, "living", ceiling=2.85,
                      furniture=[("table_dining", (6.0, 2.8), 90.0, (3.35, 1.0)),
                                 ("sofa", (2.0, 0.6), 0.0, (2.2, 0.9)),
                                 ("table_coffee", (2.0, 1.9), 0.0, (1.2, 0.6)),
                                 ("wardrobe", (0.35, 4.5), 90.0, (1.8, 0.6))],
                      doors=[("d1", "e", 1.0, 0.9, True)])
    b["decor"] = [{"id": "dec_L0_001", "kind": "decor", "type": "pendant_light", "level_id": "L0", "room_id": RID,
                   "center": [6.0, 2.8, 1.5], "size": [0.45, 0.45, 1.35], "rotation_deg": 0.0, "colour": "brass",
                   "anchor_ids": ["f_L0_001"], "method": "ai"}]
    return b


def test_a_large_living_room_gets_a_pendant_row_zone_lights_and_even_general_light():
    b = _salon()
    room = b["rooms"][0]
    rec = CL.plan_room(b, room, b["furniture"], CL.room_lights(b, RID))
    adds = rec["add"]
    row = [a for a in adds if a.get("anchor_ids") == ["f_L0_001"]]
    assert len(row) == 4 and rec["remove"] == ["dec_L0_001"]                # laid again along the table
    assert all(a["type"] == "pendant_light" and a["colour"] == "brass" for a in row)   # the AI's colour kept
    ys = sorted(a["center"][1] for a in row)
    assert ys[0] == pytest.approx(2.8 - (3.35 / 2 - 0.3), abs=0.01) and ys[-1] == pytest.approx(2.8 + 1.375, abs=0.01)
    assert all(a["center"][2] == pytest.approx(0.75 + 0.75, abs=0.05) for a in row)   # 0.75 m over the top
    assert any(a.get("anchor_ids") == ["f_L0_003"] and a["type"] == "ceiling_light" for a in adds)
    total = len(CL.room_lights(b, RID)) - len(rec["remove"]) + len(adds)
    assert total >= CL.lights_needed(room)[0] == 6
    geo = CL.Room(b, room, b["furniture"])
    general = [a for a in adds if not a.get("anchor_ids")]
    assert general
    for a in adds:
        ok, why = geo.free(a["center"][:2], a["size"][:2], inside=False)
        assert ok, (a, why)                                      # off the wardrobe, out of the door swing
    pts = [tuple(a["center"][:2]) for a in adds if a not in row]
    for i, p in enumerate(pts):
        for q in pts[i + 1:] + [tuple(r["center"][:2]) for r in row]:
            assert math.dist(p, q) >= CL.MIN_GAP_M - 1e-6
    # applied: the room passes M16; nothing left to add
    new_ids = iter(f"dec_L0_{n:03d}" for n in range(10, 99))
    made, notes = CL.add_lights(b, lambda lv: next(new_ids))
    assert made and notes[RID][-1].startswith("lighting rule: 1 -> ")
    assert CL.review(b)[0] == [] and not CL.plan_room(b, room, b["furniture"], CL.room_lights(b, RID))["add"]


def test_m14_flags_a_room_with_too_little_ceiling_light():
    b = _salon()
    got, n = CL.review(b)
    assert n == 1 and got[0]["check"] == "M16" and got[0]["severity"] == "major" and got[0]["target"] == RID
    assert got[0]["metrics"]["have"] == 1 and got[0]["metrics"]["needed"] >= 6 and "lumen method" in got[0]["message"]
    assert MR.review(b)["checks"]["M16"]["failed"] == 1 and "M16" in MR.CHECKS
    assert CS.CHECK_CAUSE["M16"] == "ceiling_light" and CS.REPORT_TO["ceiling_light"] == "decor"
    assert CS.CAUSE_TOOLS["ceiling_light"] == () and "ceiling_light" in CS.NO_TOOL_REASON
    assert any(f["check"] == "M16" and f["owner"] == "decor" for f in SE.dressing(b))
    # an outdoor room is not lit from a ceiling
    t = _room("balcony")
    assert CL.review(t) == ([], 0)


def test_the_decor_stage_lights_every_room_whatever_the_ai_chose():
    b = room_building(6.0, 5.0, "living", furniture=[("sofa", (3.0, 0.5), 0.0, (2.0, 0.9)),
                                                     ("table_coffee", (3.0, 1.7), 0.0, (1.0, 0.5))])
    out, records = applied(b, choose())                      # the AI chose nothing
    lights = CL.room_lights(out, RID)
    assert len(lights) >= CL.lights_needed(out["rooms"][0])[0] and CL.review(out)[0] == []
    ruled = [d for d in lights if d.get("rule") == CL.RULE]
    assert ruled and all(d["method"] == "rule" and d["id"].startswith("dec_L0_") for d in ruled)
    assert any(d.get("anchor_ids") == ["f_L0_002"] for d in lights)          # over the coffee table
    assert {i["id"] for i in records[0].items} >= {d["id"] for d in lights}
    assert any(n.startswith("lighting rule:") for n in records[0].notes)


def test_the_rig_puts_its_light_into_the_rooms_decor_lights():
    from wenart.blender import lighting as LI

    room = {"id": "r", "room_type": "dining", "polygon": [[0, 0], [6, 0], [6, 4], [0, 4]]}
    table = {"id": "t", "type": "table_dining", "front_deg": 270.0,
             "footprint": {"center": [3.0, 2.0], "size": [3.35, 1.0], "rotation_deg": 0.0}}
    row = [{"id": f"dec_{i}", "type": "pendant_light", "center": [x, 2.0, 1.5 + 0.675], "size": [0.35, 0.35, 1.35],
            "rotation_deg": 0.0} for i, x in enumerate((1.625, 2.54, 3.46, 4.375))]
    assert [d["id"] for d in LI.rig_row_hosts(row, table)] == ["dec_0", "dec_1", "dec_2", "dec_3"]
    plan = LI.rig_plan(room, [table], 0.0, 2.85, decor=row)
    pend = [f for f in plan["fixtures"] if f["kind"] == "pendant"]
    assert len(pend) == 4 and not any(f["mesh"] for f in pend)              # no fifth pendant between the row's
    assert {f["host_id"] for f in pend} == {d["id"] for d in row}
    spec = LI.room_rig("dining")[0]
    assert sum(f["light"]["energy_w"] for f in pend) == pytest.approx(spec["watts_applied"], rel=1e-3)
    # a kitchen's ceiling fixture: shared out over the decor ceiling lights when none hangs at its spot
    kitchen = dict(room, room_type="kitchen")
    lights = [{"id": f"dec_c{i}", "type": "ceiling_light", "center": [x, 1.0, 2.79], "size": [0.4, 0.4, 0.12],
               "rotation_deg": 0.0} for i, x in enumerate((1.5, 4.5))]
    ceil = [f for f in LI.rig_plan(kitchen, [], 0.0, 2.85, decor=lights)["fixtures"] if f["kind"] == "ceiling"]
    assert len(ceil) == 2 and {f["host_id"] for f in ceil} == {"dec_c0", "dec_c1"} and not any(f["mesh"] for f in ceil)
    # no decor light: the rig's own fixture, as before
    alone = [f for f in LI.rig_plan(kitchen, [], 0.0, 2.85)["fixtures"] if f["kind"] == "ceiling"]
    assert len(alone) == 1 and alone[0]["mesh"]


def test_no_ceiling_light_is_asked_when_the_brief_turns_decor_off():
    b = _salon()
    b["project"]["brief"] = {"decor": False}
    assert CL.review(b) == ([], 0)


def test_a_ceiling_light_under_a_slope_is_mounted_on_it():
    slope = 0.2                                               # 11.3°: z = 0.2 x + 2.0 over the floor at 0
    planes = [(slope, 0.0, 2.0), (0.0, 0.0, 3.5)]
    sm = CL.slope_mount(planes, 0.0, (2.0, 1.0), (0.4, 0.4), 0.12)
    assert sm["tilt_deg"] == pytest.approx(math.degrees(math.atan(slope)), abs=1e-3) and sm["fits"]
    assert sm["top_m"] == pytest.approx(2.4) and sm["lowest_m"] == pytest.approx(
        2.4 - 0.12 * math.cos(math.atan(slope)) - 0.2 * math.sin(math.atan(slope)), abs=1e-4)
    assert CL.slope_mount([(0.0, 0.0, 2.7)], 0.0, (2.0, 1.0), (0.4, 0.4), 0.12) is None    # a flat ceiling
    low = CL.slope_mount(planes, 0.0, (0.2, 1.0), (0.4, 0.4), 0.12)
    assert low["lowest_m"] < 2.0                              # the mount refuses it (below 2.0 m)
    # the builder turns the fixture onto the plane: its top face lies in the plane, +Z becomes the normal
    top = 2.4
    verts = [(x, y, z) for x in (1.8, 2.2) for y in (0.8, 1.2) for z in (top - 0.12, top)]
    item = {"type": "ceiling_light", "slope_mount": sm}
    turned = BF.slope_verts(item, verts)
    for (x, y, z), v in zip(verts, turned):
        if z == top:
            assert v[2] == pytest.approx(slope * v[0] + 2.0, abs=1e-6)
    axis = geom2d.tilt_onto_plane([(0, 0, 0), (0, 0, 1)], (0, 0, 0), slope, 0.0)[1]
    n = (-slope, 0.0, 1.0)
    ln = math.sqrt(sum(c * c for c in n))
    assert axis == pytest.approx(tuple(c / ln for c in n), abs=1e-9)
    assert BF.slope_verts({"type": "pendant_light", "slope_mount": sm}, verts) == verts
    assert BF.slope_verts({"type": "ceiling_light"}, verts) == verts


# --------------------------------------------------------------------------
# real04 (committed results): the roof terrace and the lights
# --------------------------------------------------------------------------

@pytest.mark.skipif(not (REAL04 / "building_final.json").is_file(), reason="no committed real04 building")
def test_real04_roof_terrace_gets_outdoor_models_and_no_rug():
    from wenart.furniture import catalog as C

    b = json.loads((REAL04 / "building_final.json").read_text(encoding="utf-8"))
    open_ids = OD.open_air_room_ids(b)
    before = [f for f in b["furniture"] if f.get("room_id") in open_ids and f.get("type") in OD.OUTDOOR_FURNITURE_TYPES
              and (f.get("asset") or {}).get("method") == "library"]
    assert any("Traditional" in str(f["asset"].get("title")) for f in before)        # the run's indoor table
    fitted = F.fit_building(copy.deepcopy(b), C.load(), style_family="modern", mode="relaxed")
    outside = [f for f in fitted["furniture"] if f.get("room_id") in open_ids
               and f.get("type") in OD.OUTDOOR_FURNITURE_TYPES and f.get("build") is not False]
    assert outside
    for f in outside:
        a = f["asset"]
        assert a["outdoor"]["ready"], (f["id"], a.get("asset_id"))
        assert a["method"] != "library" or OD.outdoor_ready(C.load().entry(a["asset_id"]), f["type"])[0]
        assert a["method"] == "library" or a["outdoor_build"]["wood"] == OD.OUTDOOR_WOOD
    assert not [x for x in OD.review(dict(fitted, decor=[]))[0]]
    # the decor: a rug laid on the terrace by any rule is taken out
    dec = copy.deepcopy(fitted)
    dec["decor"] = [{"id": "dec_L1_900", "type": "rug", "room_id": sorted(open_ids)[0]}]
    assert OD.strip_outdoor_textiles(dec) and not dec["decor"]


@pytest.mark.skipif(not (REAL04 / "building_decor.json").is_file(), reason="no committed real04 decor")
def test_real04_rooms_get_their_ceiling_lights():
    b = json.loads((REAL04 / "building_decor.json").read_text(encoding="utf-8"))
    found, _n = CL.review(b)
    assert found                                              # the committed run is under-lit
    counter = iter(range(900, 999))
    made, _notes = CL.add_lights(b, lambda lv: f"dec_{lv}_{next(counter)}")
    assert made and CL.review(b)[0] == []
    for d in made:
        assert d["type"] in CL.LIGHT_TYPES and d["rule"] == CL.RULE and d["reason"].startswith("lighting rule")
        if d.get("slope_mount"):
            assert d["slope_mount"]["lowest_m"] >= D.MIN_LIGHT_BOTTOM_M - 1e-9
