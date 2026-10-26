"""Every labelled outdoor space is built, every drawn site symbol is typed (26 Oct 2026; user: "There was a veranda in
real06, it has been fully missed ... the issue is not just veranda; think to solve issues like veranda").

real06's DWG labels "VERANDA 22,80m²" in the inner corner of its L-shaped ground floor and "BALKON 11,80m²" over it
on the upper floor; neither has walls, so the reading kept them as label-only site areas and nothing was built (the
upper one was even dropped as "not the ground floor's site"). General rules (wenart/levels/outdoor.py, the reading's
step in wenart/ingest/generic/core.py, the site build in wenart/blender/site.py, the entrances in
wenart/levels/model.py), tested on real06 (its strokes and its building, tests/fixtures/real06_outdoor_*.json) and on
hand-made buildings: an L corner, a straight facade, an upper-floor balcony, a label with no stated area (CPU)."""
import copy
import json
from pathlib import Path

import pytest
from shapely.geometry import Point, Polygon

from wenart import geometry as G
from wenart.blender import build as BB
from wenart.blender import site as S
from wenart.levels import model as M
from wenart.levels import outdoor as OD
from tests import _levels_fixture as F

ROOT = Path(__file__).resolve().parents[1]
STROKES = json.loads((ROOT / "tests" / "fixtures" / "real06_outdoor_strokes_20261026.json").read_text("utf-8"))
REAL06 = ROOT / "tests" / "fixtures" / "real06_outdoor_20261026.json"


def _real06() -> dict:
    return json.loads(REAL06.read_text(encoding="utf-8"))


def _space(b, sid):
    return next(s for s in b["site"]["outdoor_spaces"] if s["id"] == sid)


def _ents(b):
    return {e["door_id"]: e for e in b["site"]["entrances"]}


# --------------------------------------------------------------------------
# The vocabulary and the stated area
# --------------------------------------------------------------------------

def test_one_vocabulary_names_the_outdoor_spaces_in_several_languages():
    cases = {"VERANDA": "veranda", "Verandah": "veranda", "SUNDURMA": "porch", "Front porch": "porch",
             "BALKON": "balcony", "Balkonu": "balcony", "Balcony": "balcony", "TERAS": "terrace",
             "Çatı Terası": "terrace",
             "Roof terrace": "terrace", "Terrasse": "terrace", "Deck": "deck", "Patio": "patio", "AVLU": "courtyard",
             "Courtyard": "courtyard", "KIŞ BAHÇESİ": "winter_garden", "Winter garden": "winter_garden",
             "Wintergarten": "winter_garden", "Çardak": "pergola", "Pergola": "pergola", "Loggia": "loggia"}
    for label, kind in cases.items():
        assert OD.space_kind(label)["kind"] == kind, label
    covers = {k: OD.space_kind(k)["cover"]
              for k in ("VERANDA", "SUNDURMA", "BALKON", "TERAS", "KIŞ BAHÇESİ", "Pergola")}
    assert covers == {"VERANDA": "roof", "SUNDURMA": "roof", "BALKON": None, "TERAS": None, "KIŞ BAHÇESİ": "glass",
                      "Pergola": "pergola"}
    for label in ("OTOPARK", "Car porch", "Carport", "HAVUZ", "Pool", "BAHÇE", "Garden", "SALON", "Deckenhöhe", ""):
        assert OD.space_kind(label) is None, label


def test_the_stated_area_is_read_from_the_label_or_its_evidence():
    assert OD.parse_area("22,80m²") == 22.8 and OD.parse_area("24 m2") == 24.0
    assert OD.parse_area("110 sq ft") == pytest.approx(10.219, abs=0.01) and OD.parse_area("VERANDA") is None
    area = {"label": "VERANDA", "evidence": [{"text": "VERANDA"}, {"text": "22,80m²", "entity": "TEXT:29585D"}]}
    assert OD.stated_area(area) == {"m2": 22.8, "text": "22,80m²", "entity": "TEXT:29585D"}
    assert OD.stated_area({"label": "Teras", "stated_area_m2": 12.5})["m2"] == 12.5
    assert OD.stated_area({"label": "Balkon", "evidence": []}) is None


# --------------------------------------------------------------------------
# The reading: the region the label sits in, from real06's strokes
# --------------------------------------------------------------------------

def _closed(level, stated="given"):
    d = STROKES["levels"][level]
    facade = Polygon(d["outline"][0])
    st = d["stated_area_m2"] if stated == "given" else stated
    return d, facade, OD.close_region(d["anchor"], d["strokes"], facade, st)


def test_real06_veranda_closes_from_its_drawn_edge_lines_and_the_facade():
    d, facade, rec = _closed("L0")
    assert rec is not None and rec["pass"] == "BALKON" and rec["layers"] == ["BALKON"]
    assert rec["area_m2"] == pytest.approx(22.8, rel=0.15) and rec["off"] < 0.01         # 22.84 m², 0.2 % off
    poly = Polygon(rec["polygon"])
    assert poly.contains(Point(d["anchor"])) and poly.intersection(facade).area < 0.05   # outside the walls
    assert poly.distance(facade) < 0.01                                                 # against the facade
    xs, ys = [p[0] for p in rec["polygon"]], [p[1] for p in rec["polygon"]]
    assert min(xs) == pytest.approx(-0.474, abs=0.01) and max(xs) == pytest.approx(4.376, abs=0.01)
    assert min(ys) == pytest.approx(-1.575, abs=0.01) and max(ys) == pytest.approx(3.325, abs=0.01)
    assert len(rec["bridges"]) == 4 and max(rec["bridges"]) <= OD.SPACE["gap_m"]         # the column gaps
    steps = OD.drawn_steps(rec["polygon"], [s for s in d["strokes"] if s["layer"] in rec["layers"]])
    assert steps["treads"] == 2 and steps["tread_m"] == pytest.approx(0.25, abs=0.01)
    assert steps["width_m"] == pytest.approx(1.3, abs=0.01) and steps["dir"] == [-1.0, -0.0]   # west, as drawn


def test_real06_upper_balcony_closes_from_its_strokes():
    d, facade, rec = _closed("L1")
    assert rec is not None and rec["layers"] == ["BALKON"]
    assert rec["area_m2"] == pytest.approx(11.8, rel=0.15) and rec["off"] < 0.05
    xs = [p[0] for p in rec["polygon"]]
    assert min(xs) == pytest.approx(1.976, abs=0.01) and max(xs) == pytest.approx(4.376, abs=0.01)


def test_a_wrong_stated_area_or_no_outdoor_layer_closes_nothing():
    _d, _f, rec = _closed("L0", stated=60.0)                   # nothing near 60 m² around the label
    assert rec is None
    _d, _f, rec = _closed("L0", stated=None)                  # no stated area: the BALKON layer may close it alone
    assert rec is not None and rec["layers"] == ["BALKON"] and rec["off"] is None
    d = STROKES["levels"]["L0"]
    plain = [dict(s, layer="0") for s in d["strokes"] if s["layer"] == "BALKON"]
    assert OD.close_region(d["anchor"], plain, Polygon(d["outline"][0]), None) is None
    rec = OD.close_region(d["anchor"], plain, Polygon(d["outline"][0]), 22.8)       # a stated area: any layer
    assert rec["area_m2"] == pytest.approx(22.8, rel=0.15)


# --------------------------------------------------------------------------
# real06: the veranda and the balcony are built, the doors land on them
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def real06():
    return M.infer_levels(_real06())


@pytest.fixture(scope="module")
def prep06(real06):
    return BB.prepare(copy.deepcopy(real06), "base", None)


def test_real06_veranda_is_built_at_the_door_floor_against_the_facade(real06):
    v = _space(real06, "os_L0_veranda")
    assert v["kind"] == "veranda" and v["level_id"] == "L0" and v["method"] == "strokes"
    assert v["area_m2"] == pytest.approx(22.8, rel=0.15) and v["stated_area_m2"] == 22.8
    assert v["z"] == 0.0 and "+0,50" in v["z_source"]                    # the level mark inside it = the doors' floor
    assert sorted(v["doors"]) == ["d_L0_004", "d_L0_006"] and not v["elevated"]
    assert v["steps"]["source"] == "drawn" and v["steps"]["treads"] == 2
    assert v["inferred"] and any(e.get("entity") == "TEXT:29585D" for e in v["evidence"])     # the label's evidence
    outline = Polygon(M.outlines_of(real06)["L0"])
    assert Polygon(v["polygon"]).distance(outline) < 0.05                # against the facade, in the inner corner
    area = next(a for a in real06["site"]["areas"] if a["id"] == "sa_L0_veranda")
    assert area["polygon"] is None and area["space"] == {"built": True, "id": "os_L0_veranda"}    # drawn value kept
    item = next(i for i in real06["level_inference"]["inferred"] if i["item"] == "outdoor space os_L0_veranda")
    assert "22.80" in item["reason"] and "d_L0_004" in item["reason"]   # listed for the report


def test_real06_veranda_doors_use_it_and_no_second_platform_is_made(real06, prep06):
    ents = _ents(real06)
    for did in ("d_L0_004", "d_L0_006"):
        assert ents[did]["onto"] == "os_L0_veranda" and ents[did]["solution"] == "none" and not ents[did]["steps"]
    assert ents["d_L0_004"]["main"]                                       # the house's door stays the main entrance
    inf = prep06["site"]["inferred"]
    stepped = {d for s in inf["steps"] for d in (s.get("doors") or [s["opening_id"]])}
    assert not stepped & {"d_L0_004", "d_L0_006"} and inf["entrance_groups"] == []        # no stepped platform
    pf = next(p for p in prep06["site"]["platforms"] if p["id"] == "os_L0_veranda")
    assert pf["z"] == 0.0 and pf["edge"] == "steps" and pf["steps_at"]["source"] == "drawn"
    a, b = pf["polygon"][pf["steps_edge"]], pf["polygon"][(pf["steps_edge"] + 1) % len(pf["polygon"])]
    assert a[0] == pytest.approx(-0.474, abs=0.01) and b[0] == pytest.approx(-0.474, abs=0.01)    # the drawn edge
    path = next(p for p in inf["paths"] if "d_L0_004" in p["opening_ids"])
    assert set(path["opening_ids"]) == {"d_L0_004", "d_L0_006"}
    assert max(q[0] for q in path["polygon"]) < -0.5                     # from the foot of the drawn steps, west
    parts = {q["part"]: q for q in S.platform_parts(pf, prep06["site"]["terrain"])}
    assert {"slab", "wall", "steps", "roof", "beams", "posts"} <= set(parts)
    steps_z = sorted({round(v[2], 3) for v in parts["steps"]["verts"]})
    assert steps_z[-1] == pytest.approx(-0.167, abs=0.01)                # 3 risers of 0.167 m (2 drawn treads)
    by = {q["id"]: q for q in prep06["architect"]["questions"]}
    lands = {x["element"]: x["found"] for x in by["E1"]["answers"]}
    assert "os_L0_veranda" in lands["d_L0_004"] and "os_L0_veranda" in lands["d_L0_006"]


def test_real06_veranda_roof_covers_what_the_balcony_does_not(real06):
    v = _space(real06, "os_L0_veranda")
    roof = v["roof"]
    assert roof["kind"] == "light_roof" and roof["top_z"] == pytest.approx(3.0)        # the L1 floor line
    balcony = Polygon(_space(real06, "os_L1_balkon")["polygon"])
    assert Polygon(roof["polygon"]).intersection(balcony).area < 0.05                  # the balcony covers its part
    assert roof["area_m2"] == pytest.approx(11.2, abs=0.5)
    drawn = [q for q in v["posts"] if q["source"] == "drawn"]
    assert {q["id"] for q in drawn} == {"sd_L0_009", "sd_L0_010"}                      # the drawn KOLON columns
    under = next(q for q in drawn if q["id"] == "sd_L0_009")
    assert under["z1"] == pytest.approx(2.8) and "os_L1_balkon" in under["carries"]   # carries the balcony slab
    inferred = [q for q in v["posts"] if q["source"] == "inferred"]
    assert len(inferred) == 1 and inferred[0]["center"][0] < 0                        # the open front-left corner
    for q in v["posts"]:
        assert q["z0"] == 0.0 and 2.3 <= q["z1"] <= 2.85


def test_real06_upper_balcony_is_a_slab_with_a_guard_and_its_doors_land_on_it(real06, prep06):
    bal = _space(real06, "os_L1_balkon")
    assert bal["level_id"] == "L1" and bal["z"] == pytest.approx(3.0) and bal["elevated"] and bal["roof"] is None
    assert sorted(bal["doors"]) == ["d_L1_007", "d_L1_011"]
    ents = _ents(real06)
    for did in ("d_L1_007", "d_L1_011"):
        assert ents[did]["onto"] == "os_L1_balkon" and not ents[did]["into_air"] and not ents[did]["main"]
    assert ents["d_L1_001"]["into_air"]                                   # a door with nothing outside stays one
    pf = next(p for p in prep06["site"]["platforms"] if p["id"] == "os_L1_balkon")
    assert pf["elevated"] and pf["steps_edge"] is None and pf["railing_edges"]
    assert set(pf["railing_edges"]).isdisjoint(pf["against_edges"])
    parts = {q["part"]: q for q in S.platform_parts(pf, prep06["site"]["terrain"])}
    assert set(parts) == {"slab", "railing"}                             # no base wall, no steps
    zs = [v[2] for v in parts["slab"]["verts"]]
    assert min(zs) == pytest.approx(3.0 - S.SPACE_SLAB_M) and max(zs) == pytest.approx(3.0)
    by = {q["id"]: q for q in prep06["architect"]["questions"]}
    lands = {x["element"]: x for x in by["E1"]["answers"]}
    assert "os_L1_balkon" in lands["d_L1_007"]["found"] and not lands["d_L1_007"].get("change")
    doors = {o["id"]: o for o in prep06["building"]["openings"]}
    assert doors["d_L1_007"]["type"] == doors["d_L1_011"]["type"] == "door"     # not turned into windows


def test_real06_without_the_strokes_gets_the_inner_corner_rectangle():
    b = _real06()
    for a in b["site"]["areas"]:
        a.pop("outline_inferred", None)
        a.pop("stated_area_m2", None)                                     # the stated area from the evidence text
    n = M.infer_levels(b)
    v = _space(n, "os_L0_veranda")
    assert v["method"] == "rectangle in the inner corner" and v["area_m2"] == pytest.approx(22.8, rel=0.15)
    poly = Polygon(v["polygon"])
    assert poly.contains(Point(1.9746, 0.9031)) and sorted(v["doors"]) == ["d_L0_004", "d_L0_006"]
    xs, ys = [p[0] for p in v["polygon"]], [p[1] for p in v["polygon"]]
    assert max(xs) == pytest.approx(4.35, abs=0.05) and max(ys) == pytest.approx(3.3, abs=0.05)   # the corner
    assert v["steps"] is None                                             # no drawn flight known: the build picks one


# --------------------------------------------------------------------------
# Hand-made buildings: an L corner, a straight facade, a label without an area, an upper-floor balcony
# --------------------------------------------------------------------------

def _area(label, anchor, level="L0", texts=()):
    return {"id": f"sa_{level}_{label.split()[0].lower()}", "level_id": level, "label": label, "label_raw": label,
            "polygon": None, "anchor": list(anchor), "kind": "other", "build": False,
            "evidence": [{"file": "t.dxf", "method": "vector", "confidence": 1.0, "entity": "TEXT:1", "text": label}]
            + [{"file": "t.dxf", "method": "vector", "confidence": 1.0, "entity": f"TEXT:{k + 2}", "text": t}
               for k, t in enumerate(texts)]}


def _l_building(label="TERAS", texts=("12,00 m²",), anchor=(3.2, 2.2)):
    b = F.building()
    b["project"]["brief"] = {"levels": {"ground_rise": 0.5}}
    b["walls"] =[F._wall("w_1", (0, 4), (5, 4)), F._wall("w_2", (5, 4), (5, 0)), F._wall("w_3", (5, 0), (10, 0)),
                  F._wall("w_4", (10, 0), (10, 8)), F._wall("w_5", (10, 8), (0, 8)), F._wall("w_6", (0, 8), (0, 4)),
                  F._wall("w_7", (5, 4), (10, 4), exterior=False)]
    b["openings"] = [dict(F._opening("d_garden", "door", "w_1", (3.0, 4.0), 2.4), operation="sliding"),
                     dict(F._opening("d_side", "door", "w_2", (5.0, 2.0), 0.9), operation="swing"),
                     F._opening("d_inner", "door", "w_7", (7.5, 4.0), 0.9),
                     F._opening("win_1", "window", "w_3", (7.5, 0.0), 1.2)]
    b["rooms"] = [F._room("r_living", [(0.1, 4.1), (9.9, 4.1), (9.9, 7.9), (0.1, 7.9)], "living", label="Salon"),
                  F._room("r_hall", [(5.1, 0.1), (9.9, 0.1), (9.9, 3.9), (5.1, 3.9)], "hall", label="Hol")]
    b["site"] = {"boundary_walls": [], "areas": [_area(label, anchor, texts=texts)], "decor": [], "openings": []}
    return b


def test_an_l_corner_terrace_with_a_stated_area_fills_the_corner_and_takes_both_doors():
    n = M.infer_levels(_l_building())
    t = n["site"]["outdoor_spaces"][0]
    assert t["kind"] == "terrace" and t["method"] == "rectangle in the inner corner" and t["roof"] is None
    assert t["area_m2"] == pytest.approx(12.0, rel=0.02) and sorted(t["doors"]) == ["d_garden", "d_side"]
    xs, ys = [p[0] for p in t["polygon"]], [p[1] for p in t["polygon"]]
    assert max(xs) == pytest.approx(4.9, abs=0.02) and max(ys) == pytest.approx(3.9, abs=0.02)    # the wall faces
    assert t["z"] == 0.0 and "threshold" in t["z_source"]                 # no mark: the doors' floor
    ents = _ents(n)
    assert ents["d_garden"]["onto"] == ents["d_side"]["onto"] == t["id"] and ents["d_side"]["main"]
    prep = BB.prepare(n, "base", None)
    inf = prep["site"]["inferred"]
    assert inf["steps"] == [] and inf["entrance_groups"] == []            # the terrace is their landing
    pf = next(p for p in prep["site"]["platforms"] if p["id"] == t["id"])
    assert pf["edge"] == "steps" and pf["steps_edge"] not in pf["against_edges"]
    assert any(set(p["opening_ids"]) == {"d_garden", "d_side"} for p in inf["paths"])


def _box_building():
    b = F.building()
    b["site"] = {"boundary_walls": [], "areas": [], "decor": [], "openings": []}
    return b


def test_a_veranda_against_a_straight_facade_gets_its_area_and_a_light_roof():
    b = _box_building()
    b["site"]["areas"] = [_area("VERANDA", (8.0, -1.6), texts=("9,00m²",))]   # 1.5 m in front of the south face
    n = M.infer_levels(b)
    v = n["site"]["outdoor_spaces"][0]
    assert v["method"] == "rectangle against the facade" and v["area_m2"] == pytest.approx(9.0, rel=0.02)
    ys = [p[1] for p in v["polygon"]]
    assert max(ys) == pytest.approx(-0.1, abs=0.01) and min(ys) == pytest.approx(-3.1, abs=0.02)   # 3 m deep
    assert v["doors"] == ["d_front"] and _ents(n)["d_front"]["onto"] == v["id"]
    roof = v["roof"]
    assert roof["kind"] == "light_roof" and roof["top_z"] == pytest.approx(2.7 + OD.SPACE["eaves_extra"])
    assert roof["plane"]["dir"] == pytest.approx([0.0, -1.0], abs=1e-6)   # falls away from the facade
    assert {tuple(q["center"]) for q in v["posts"]} and all(q["source"] == "inferred" for q in v["posts"])
    assert len(v["posts"]) == 2 and all(q["center"][1] < -2.9 for q in v["posts"])     # the two open front corners
    pf = S.space_platform(v, lambda x, y: -0.15)
    parts = {q["part"]: q for q in S.cover_parts(pf)}
    assert set(parts) == {"roof", "beams", "posts"}
    top = max(v_[2] for v_ in parts["roof"]["verts"])
    low = min(v_[2] for v_ in parts["roof"]["verts"] if abs(v_[1] + 3.1) < 0.02)
    assert top == pytest.approx(roof["top_z"]) and low == pytest.approx(roof["top_z"] - 0.18 - 0.02 * 3.0, abs=0.01)


def test_a_label_without_a_stated_area_takes_the_doors_span_and_twice_its_distance():
    b = _box_building()
    b["site"]["areas"] = [_area("Balkon", (8.0, -1.1))]                 # 1 m in front of the south face, no area
    n = M.infer_levels(b)
    s = n["site"]["outdoor_spaces"][0]
    assert s["stated_area_m2"] is None and s["method"] == "rectangle against the facade"
    xs, ys = [p[0] for p in s["polygon"]], [p[1] for p in s["polygon"]]
    assert min(ys) == pytest.approx(-2.1, abs=0.02)                      # depth 2 x 1.0 m
    assert min(xs) <= 7.0 and max(xs) >= 9.0 and max(xs) - min(xs) == pytest.approx(2.0, abs=0.05)   # the door + 0.5
    assert s["doors"] == ["d_front"]


def _two_levels():
    b = F.building()
    up = copy.deepcopy(b["levels"][0])
    up.update(id="L1", label="1. Kat", order=1, elevation=3.0)
    b["levels"].append(up)
    for w in list(b["walls"]):
        b["walls"].append(dict(copy.deepcopy(w), id=w["id"] + "_up", level_id="L1"))
    b["openings"].append(F._opening("d_up", "door", "w_1_up", (3.0, 0.0), 0.9, level="L1"))
    b["rooms"] += [F._room("r_bed", [(0.1, 0.1), (5.9, 0.1), (5.9, 7.9), (0.1, 7.9)], "bedroom", level="L1",
                           label="Yatak Odası"),
                   F._room("r_up_hall", [(6.1, 0.1), (9.9, 0.1), (9.9, 7.9), (6.1, 7.9)], "hall", level="L1",
                           label="Hol")]
    b["roof"] = {"type": "flat_cut"}
    b["site"] = {"boundary_walls": [], "areas": [_area("BALKON", (3.0, -0.85), level="L1", texts=("4,50 m²",))],
                 "decor": [], "openings": []}
    return b


def test_an_upper_floor_balcony_is_a_slab_with_a_guard_at_its_floor_and_its_door_lands_on_it():
    n = M.infer_levels(_two_levels())
    s = n["site"]["outdoor_spaces"][0]
    assert s["level_id"] == "L1" and s["kind"] == "balcony" and s["elevated"] and s["z"] == pytest.approx(3.0)
    assert s["area_m2"] == pytest.approx(4.5, rel=0.02) and s["doors"] == ["d_up"]
    e = _ents(n)["d_up"]
    assert e["onto"] == s["id"] and not e["into_air"] and e["upper_floor"] and not e["main"]
    assert "d_up" not in [r["opening_id"] for r in S.record_entrances(n, M.base_levels(n))]
    terrain = {"kind": "flat", "levels": {}, "default": -0.15, "flat_z": -0.15}
    pfs = S.platforms(n["site"], None, keep_out=[M.outlines_of(n)["L0"]], outlines=M.outlines_of(n))
    pf = next(p for p in pfs if p["id"] == s["id"])
    assert pf["elevated"] and pf["edge"] == "none" and pf["wall_max_m"] == 0.0 and pf["steps_edge"] is None
    assert len(pf["railing_edges"]) >= 3 and set(pf["railing_edges"]).isdisjoint(pf["against_edges"])
    assert pf["against_edges"]                                            # its edge on the facade has no guard
    del terrain
    # without the label the door stays a door into the air
    b = _two_levels()
    b["site"]["areas"] = []
    assert _ents(M.infer_levels(b))["d_up"]["into_air"]


def test_a_balcony_flush_with_the_garden_outside_a_window_is_reached_from_the_garden():
    # real03's case: "BALKON 1.80 m2" in front of a window of a ground floor 0.15 m over the ground, no door onto it
    b = _box_building()
    b["site"]["areas"] = [_area("BALKON", (3.0, -0.6), texts=("2,50 m²",))]
    n = M.infer_levels(b)
    s = n["site"]["outdoor_spaces"][0]
    assert s["doors"] == [] and not s["elevated"] and s["z"] == 0.0 and "no door" in s["z_source"]
    prep = BB.prepare(n, "base", None)
    by = {q["id"]: q for q in prep["architect"]["questions"]}
    a2 = next(a for a in by["A2"]["answers"] if a["element"] == s["id"])
    assert "from the garden" in a2["found"] and not a2.get("open")
    a5 = [a for a in by["A5"]["answers"] if a["element"] == s["id"]]
    assert a5 and not a5[0].get("open") and "windows stay as drawn" in a5[0]["change"]


def test_a_label_that_a_room_or_a_drawn_surface_holds_is_not_built_twice():
    b = _box_building()
    b["site"]["areas"] = [_area("TERAS", (3.0, 4.0))]                    # inside the living room
    n = M.infer_levels(b)
    assert n["site"]["outdoor_spaces"] == [] and "r_living" in n["site"]["areas"][0]["space"]["reason"]
    b = _box_building()
    b["site"]["areas"] = [_area("Teras", (5.0, -3.0))]
    b["site"]["paving"] = [{"id": "sp_001", "polygon": [[2, -5], [8, -5], [8, -1], [2, -1]], "area_id": "sa_L0_teras",
                            "build": True, "source": "site_plan"}]
    n = M.infer_levels(b)
    assert n["site"]["outdoor_spaces"] == [] and "sp_001" in n["site"]["areas"][0]["space"]["reason"]


# --------------------------------------------------------------------------
# The drawn site symbols
# --------------------------------------------------------------------------

def test_real06_site_symbols_are_typed_by_their_layers_and_none_is_a_plant(real06):
    decor = real06["site"]["decor"]
    kinds: dict = {}
    for d in decor:
        kinds.setdefault(d["inferred_as"], []).append(d["id"])
        assert d["inferred"] and d["type_reason"] and d["drawn_kind"] == "other"
    assert len(kinds["axis_bubble"]) == 28 and sorted(kinds["column"]) == ["sd_L0_009", "sd_L0_010"]
    assert len(kinds["window_sill"]) == 7 and "level_mark" in kinds and "tree" not in kinds and "hedge" not in kinds
    assert all(d["kind"] == "other" for d in decor)                     # nothing becomes a tree
    bubble = next(d for d in decor if d["id"] == "sd_L0_001")
    assert "AKS YAZI" in bubble["type_reason"] and "not built" in bubble["type_reason"]
    by = {d["id"]: d for d in decor}
    for cid in ("sd_L0_009", "sd_L0_010"):                              # the KOLON circles: the veranda's posts
        assert by[cid]["built_by"] == "os_L0_veranda" and "post" in by[cid]["type_reason"]
    assert by["sd_L0_018"]["inferred_as"] == "outdoor_space_detail" and by["sd_L0_018"]["built_by"] == "os_L0_veranda"
    # the upper plan's symbols: the ones that repeat the ground plan's are recorded as the same symbol
    other = real06["site"]["decor_other_levels"]
    same = [x for x in other if x.get("same_as")]
    assert len(other) == 42 and len(same) == 26 and all(x["inferred_as"] for x in other if not x.get("same_as"))
    items = [i["item"] for i in real06["level_inference"]["inferred"]]
    assert "site symbols: axis_bubble" in items and "site symbols: column" in items


def _circle(sid, centre, dia, layer=None, entity="CIRCLE"):
    ev = {"file": "t.dxf", "method": "vector", "confidence": 0.9, "entity": f"{entity}:{sid}"}
    if layer:
        ev["layer"] = layer
    return {"id": sid, "kind": "other", "center": list(centre), "size": [dia, dia], "evidence": [ev]}


def test_untyped_round_symbols_follow_the_vegetation_rule_unless_a_name_or_the_grid_says_otherwise():
    b = _box_building()
    row = [_circle(f"sd_h{k}", (1.0 + 0.8 * k, -4.0), 0.6) for k in range(6)]          # pitch 0.8 <= 1.5 x 0.6
    single = _circle("sd_tree", (14.0, 4.0), 3.0)
    grid = [_circle(f"sd_g{k}", (x, -6.0), 0.6) for k, x in enumerate((0.0, 6.0, 10.0))]   # on the wall axes
    lamp = _circle("sd_lamp", (12.0, -2.0), 0.4, layer="BAHCE LAMBA")
    planter = _circle("sd_pot", (12.0, 2.0), 0.6, layer="SAKSI")
    dot = _circle("sd_dot", (13.0, -3.0), 0.15)
    lines = dict(_circle("sd_lines", (12.0, 6.0), 1.0, entity="LINE"), size=[1.4, 0.3])
    b["site"]["decor"] = row + [single] + grid + [lamp, planter, dot, lines]
    entries = OD.type_site_decor(b, M.outlines_of(b)["L0"])
    by = {d["id"]: d for d in b["site"]["decor"]}
    assert all(by[f"sd_h{k}"]["inferred_as"] == "hedge" and by[f"sd_h{k}"]["kind"] == "tree" for k in range(6))
    assert by["sd_tree"]["inferred_as"] == "tree" and by["sd_tree"]["kind"] == "tree"
    assert all(by[f"sd_g{k}"]["inferred_as"] == "axis_bubble" and by[f"sd_g{k}"]["kind"] == "other" for k in range(3))
    assert by["sd_lamp"]["inferred_as"] == "lamp" and by["sd_pot"]["inferred_as"] == "planter"
    assert by["sd_dot"]["inferred_as"] == "marker" and by["sd_lines"]["inferred_as"] == "unidentified"
    assert all(by[i]["kind"] == "other" for i in ("sd_lamp", "sd_pot", "sd_dot", "sd_lines"))
    assert {e["item"] for e in entries} >= {"site symbols: hedge", "site symbols: tree", "site symbols: axis_bubble"}
    # the site build takes the typed plants: the row is one hedge, the single circle one tree
    hedges, taken = S.hedges_of(b)
    assert len(hedges) == 1 and set(taken) == {f"sd_h{k}" for k in range(6)}
    plan = S.site_plan(b, b["levels"], M.outlines_of(b)["L0"], "full")
    assert [t["id"] for t in plan["trees"]] == ["sd_tree"]
    nb = {x["id"]: x for x in plan["not_built"]}
    assert nb["sd_g0"]["inferred_as"] == "axis_bubble" and "grid" in nb["sd_g0"]["reason"]


def test_same_symbols_matches_place_and_size():
    ground = [_circle("sd_L0_001", (1.0, 1.0), 0.6), _circle("sd_L0_002", (5.0, 1.0), 0.6)]
    upper = [_circle("sd_L1_001", (1.02, 1.0), 0.6), _circle("sd_L1_002", (5.0, 1.0), 1.2),
             _circle("sd_L1_003", (9.0, 1.0), 0.6)]
    assert OD.same_symbols(upper, ground) == {"sd_L1_001": "sd_L0_001"}


def test_the_roof_height_follows_its_plane_and_posts_reach_its_underside():
    roof = {"top_z": 3.0, "fall": 0.02, "plane": {"origin": [0.0, 0.0], "dir": [0.0, -1.0]}}
    assert S.roof_z(roof, (5.0, 0.0)) == pytest.approx(3.0) and S.roof_z(roof, (5.0, -2.0)) == pytest.approx(2.96)
    assert S.roof_z(roof, (5.0, 1.0)) == pytest.approx(3.0)              # never above its top
    seg = S._clip_convex((-1.0, 0.5), (3.0, 0.5), [(0, 0), (2, 0), (2, 1), (0, 1)])
    assert seg[0] == pytest.approx((0.0, 0.5)) and seg[1] == pytest.approx((2.0, 0.5))
    pf = {"roof": {"kind": "pergola", "polygon": [[0, -3], [4, -3], [4, 0], [0, 0]], "top_z": 2.6, "thickness": 0.18,
                   "fall": 0.0, "plane": {"origin": [0, 0], "dir": [0.0, -1.0]},
                   "open_edges": [[[0, -3], [4, -3]]]},
          "posts": [{"center": [0.1, -2.9], "size_m": 0.15, "source": "inferred", "z0": 0.0, "z1": 2.6}]}
    parts = {q["part"]: q for q in S.cover_parts(pf)}
    assert set(parts) == {"beams", "posts"}                              # a pergola has no roof slab
    assert len(parts["beams"]["faces"]) >= 6 * 7                         # the edge beam and its rafters
    assert max(v[2] for v in parts["posts"]["verts"]) == pytest.approx(2.6)
    assert G.distance((0, 0), (0, 0)) == 0.0
