"""29 Oct 2026 (lesson UL109, user on real06 run 20261028-154514-full: "There are no chimneys there could be some
chimney in the projects"): the chimney rule (wenart/blender/chimney.py), the model review's M24 and Argus U27 on small
synthetic buildings (CPU, pure; no Blender)."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from wenart import geometry as G
from wenart.audit import kinds as K
from wenart.audit import lessons as L
from wenart.blender import build as B
from wenart.blender import chimney as CH
from wenart.blender import model_review as MR
from wenart.blender import roof as R

ROOT = Path(__file__).resolve().parents[1]


def _v(value):
    return {"value": value, "method": "vector", "confidence": 1.0}


def _wall(wid, a, b, t, exterior, level="L0"):
    return {"id": wid, "level_id": level, "start": list(a), "end": list(b), "thickness": t, "height": 2.7,
            "exterior": exterior, "status": "verified"}


def _house(roof_type="gable", pieces=(), rooms_extra=(), texts=None):
    """One storey, 10 x 8 m (outer wall centre lines), a 35 degree gable along x (ridge over y = 4.0): the living room
    west of an inner wall at x = 6.0 (a door at its south end), the kitchen east of it; a sofa faces the inner wall."""
    walls = [_wall("w_s", (0, 0), (10, 0), 0.2, True), _wall("w_e", (10, 0), (10, 8), 0.2, True),
             _wall("w_n", (10, 8), (0, 8), 0.2, True), _wall("w_w", (0, 8), (0, 0), 0.2, True),
             _wall("w_in", (6, 0.1), (6, 7.9), 0.1, False)]
    openings = [{"id": "win_s", "type": "window", "level_id": "L0", "wall_id": "w_s", "center": [3.0, 0.0],
                 "width": 1.5, "height": 1.4, "sill_height": 0.9},
                {"id": "win_w", "type": "window", "level_id": "L0", "wall_id": "w_w", "center": [0.0, 4.0],
                 "width": 1.2, "height": 1.4, "sill_height": 0.9},
                {"id": "d_in", "type": "door", "level_id": "L0", "wall_id": "w_in", "center": [6.0, 1.5],
                 "width": 0.9, "height": 2.1, "sill_height": 0.0}]
    rooms = [{"id": "r_salon", "level_id": "L0", "label": "Salon", "room_type": "living",
              "polygon": [[0.1, 0.1], [5.95, 0.1], [5.95, 7.9], [0.1, 7.9]]},
             {"id": "r_mutfak", "level_id": "L0", "label": "Mutfak", "room_type": "kitchen",
              "polygon": [[6.05, 0.1], [9.9, 0.1], [9.9, 7.9], [6.05, 7.9]]}] + list(rooms_extra)
    furniture = [{"id": "f_sofa", "level_id": "L0", "room_id": "r_salon", "type": "sofa", "source": "from_documents",
                  "footprint": {"center": [3.0, 4.0], "size": [2.0, 0.9], "rotation_deg": 90.0}, "front_deg": 0.0}]
    furniture += [dict(p) for p in pieces]
    if roof_type == "flat":
        roof = {"type": "flat", "over_level_id": "L0",
                "outline": [[-0.1, -0.1], [10.1, -0.1], [10.1, 8.1], [-0.1, 8.1]],
                "eaves_height": _v(3.0), "planes": [], "openings": [], "evidence": []}
    else:
        roof = {"type": roof_type, "over_level_id": "L0",
                "outline": [[-0.5, -0.5], [10.5, -0.5], [10.5, 8.5], [-0.5, 8.5]],
                "eaves_height": _v(2.9), "pitches_deg": [_v(35.0)], "ridge_lines": [], "planes": [], "openings": [],
                "evidence": []}
    b = {"project": {"id": "chimney_test"}, "status": "ok",
         "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7, "kind": "floor"}],
         "walls": walls, "openings": openings, "rooms": rooms, "furniture": furniture, "roof": roof}
    if texts is not None:
        b["chimney_texts"] = texts
    return b


def _plan(b, family="scandinavian"):
    model = R.roof_model(b["roof"], b)
    return CH.plan(b, model, family), model


# ------------------------------------------------------------------------------------------------- the words
@pytest.mark.parametrize("text,kind", [("ŞÖMİNE", "fireplace"), ("Şöminesi", "fireplace"), ("BACA", "flue"),
                                       ("Duman bacası", "flue"), ("KAZAN DAİRESİ", "boiler_room"),
                                       ("wood stove", "stove"), ("Kaminofen", "stove"), ("Kamin", "fireplace"),
                                       ("Chimney", "flue"), ("Boiler room", "boiler_room"), ("ODUN SOBASI", "stove")])
def test_the_words_of_fire_and_flues(text, kind):
    assert CH.source_word(text)[0] == kind


@pytest.mark.parametrize("text", ["HAVA BACASI", "IŞIK BACASI", "Ocak", "Kitchen stove", "chimney hood", "Salon",
                                  "ASANSÖR", "bacak", "kazanç", "", "Camino", "BOILER", "Kalorifer"])
def test_air_shafts_hobs_and_hoods_are_no_flue(text):
    assert CH.source_word(text) is None


def test_one_family_table_says_which_houses_have_chimneys():
    for fam in ("scandinavian", "rustic", "classic", "mediterranean", "modern", "japandi", "industrial"):
        assert CH.family_rule(fam)["chimney"], fam
    for fam in ("minimal", "modern minimal"):
        assert not CH.family_rule(fam)["chimney"], fam
    assert CH.family_rule(None)["family"] == "default" and CH.family_rule("unknown")["chimney"]
    for row in CH.FAMILY_CHIMNEYS.values():
        assert row["cap"] in CH.CAP_LOOKS and row["why"]


# ---------------------------------------------------------------------------------------------- the inferred one
def test_a_pitched_scandinavian_house_gets_one_chimney_over_its_fireplace_wall():
    b = _house()
    p, model = _plan(b)
    assert p["decision"] == "inferred" and len(p["chimneys"]) == 1
    ch = p["chimneys"][0]
    assert ch["source"] == "inferred" and ch["basis"] == "living_wall" and ch["room_id"] == "r_salon"
    assert ch["wall_id"] == "w_in" and ch["sofa_id"] == "f_sofa"           # the solid inner wall the sofa faces
    assert ch["center"][0] == pytest.approx(6.0)                            # on the wall's centre line
    lo = min(G.point_segment_distance(c, (6.0, 1.05), (6.0, 1.95)) for c in CH.footprint(ch["center"], ch["size"],
                                                                                          ch["rotation_deg"]))
    assert lo >= CH.CHIMNEY["opening_margin_m"] - 1e-6                      # clear of the door in that wall
    ridge = max(R.top_z(model, 6.0, y / 10.0) for y in range(0, 81))
    assert G.point_segment_distance(ch["center"], (0, 4.0), (10, 4.0)) <= 3.0     # within 3 m of the ridge ...
    assert ch["top_z"] >= ridge + 0.6 - 1e-6                                       # ... so 0.6 m over the ridge
    assert ch["top_z"] >= ch["exit_z"][1] + 0.9 - 1e-6
    assert "inferred chimney (scandinavian family" in ch["reason"] and "3-2-10 rule of thumb" in ch["reason"]
    assert ch["cap"] == "cowl" and ch["flues"] == 2 and not ch["inner"]
    assert MR.chimneys_review(b, {"roof": model, "chimneys": p}, None) == ([], 1)


def test_no_chimney_on_a_flat_roof_or_for_a_minimal_house():
    p, _ = _plan(_house("flat"))
    assert p["decision"] == "none" and not p["chimneys"] and "flat" in p["reason"]
    p, _ = _plan(_house(), "minimal")
    assert p["decision"] == "none" and "clean roofline" in p["reason"]


def test_each_dwelling_of_a_mirrored_pair_gets_its_own():
    b = _house()
    # the kitchen half becomes the mirrored dwelling's living room (twin of r_salon about x = 6.0)
    twin = next(r for r in b["rooms"] if r["id"] == "r_mutfak")
    twin.update(room_type="living", label="Salon", twin_of="r_salon", twin_transform=[-1.0, 0.0, 12.0, 0.0, 1.0, 0.0])
    p, _ = _plan(b)
    # the mirrored station of a stack on the party wall is the same stack: one shared chimney
    assert len(p["chimneys"]) == 1 and any("party wall" in n for n in p["notes"])


# ---------------------------------------------------------------------------------------------- the drawn ones
def test_a_drawn_fireplace_gets_its_stack_there_with_its_flue_inside():
    piece = {"id": "f_fire", "level_id": "L0", "room_id": "r_salon", "type": "unknown", "type_raw": "SOMINE_01",
             "source": "from_documents", "build": False, "front_deg": 0.0,
             "footprint": {"center": [1.0, 6.0], "size": [1.5, 0.6], "rotation_deg": 90.0},
             "evidence": [{"file": "plan.dwg", "method": "vector", "confidence": 1.0, "block": "SOMINE_01"}]}
    p, model = _plan(_house(pieces=[piece]), "minimal")          # drawn first: even a family without chimneys
    assert p["decision"] == "drawn" and len(p["chimneys"]) == 1
    ch = p["chimneys"][0]
    assert ch["source"] == "from_documents" and ch["kind"] == "fireplace" and ch["basis"] == "drawn_fireplace"
    assert G.distance(ch["center"], (1.0, 6.0)) < 0.05 and ch["inner"] == {"from_z": 0.0, "level_ids": ["L0"]}
    assert any(e.get("block") == "SOMINE_01" for e in ch["evidence"]) and ch["sources"][0]["id"] == "f_fire"
    parts = CH.meshes(ch, model)
    assert min(v[2] for v in parts["inner"][0]) == pytest.approx(0.0)       # the flue from the fireplace's floor


def test_a_flue_text_snaps_to_its_wall_and_an_air_shaft_is_none():
    text = {"id": "TEXT:1A", "level_id": "L0", "room_id": "r_mutfak", "text": "BACA", "kind": "flue", "pos": [9.4, 6.8],
            "file": "plan.dwg", "layer": "yazi", "method": "vector"}
    p, _ = _plan(_house(texts=[text]), "minimal")
    assert p["decision"] == "drawn" and p["chimneys"][0]["source"] == "from_documents"
    ch = p["chimneys"][0]
    assert G.distance(ch["center"], text["pos"]) <= CH.CHIMNEY["snap_m"] and ch["wall_id"] in ("w_e", "w_n", "w_in")
    assert ch["inner"] is None and ch["evidence"][0]["entity"] == "TEXT:1A"
    shaft = {"id": "r_shaft", "level_id": "L0", "label": "HAVA BACASI", "room_type": "shaft",
             "polygon": [[5.0, 7.0], [5.6, 7.0], [5.6, 7.6], [5.0, 7.6]]}
    assert CH.drawn_sources(_house(rooms_extra=[shaft])) == []
    flue_room = dict(shaft, label="BACA", id="r_baca")
    srcs = CH.drawn_sources(_house(rooms_extra=[flue_room]))
    assert [(s["what"], s["kind"]) for s in srcs] == [("room", "flue")]


def test_a_drawn_flue_on_a_flat_roof_is_still_built():
    text = {"id": "TEXT:2B", "level_id": "L0", "room_id": "r_mutfak", "text": "Kazan dairesi", "pos": [8.0, 4.0]}
    p, _ = _plan(_house("flat", texts=[text]), "minimal")
    assert p["decision"] == "drawn" and p["chimneys"][0]["kind"] == "boiler_room"
    assert p["chimneys"][0]["top_z"] >= 3.0 + 0.9 - 1e-6


# ------------------------------------------------------------------------------------------------- the model
def _closed(verts, faces):
    edges = {}
    for f in faces:
        for i in range(len(f)):
            e = tuple(sorted((f[i], f[(i + 1) % len(f)])))
            edges[e] = edges.get(e, 0) + 1
    return all(n == 2 for n in edges.values())


def test_the_stack_enters_the_roof_slab_with_no_gap_and_its_cap_sits_on_the_coping():
    p, model = _plan(_house())
    ch = p["chimneys"][0]
    for x, y, z in CH.stack_bottom(ch, model):
        assert R.underside_z(model, x, y) < z < R.top_z(model, x, y)
    parts = CH.meshes(ch, model)
    for part in ("stack", "coping"):
        assert _closed(*parts[part]), part
    top = ch["top_z"]
    assert max(v[2] for v in parts["stack"][0]) == pytest.approx(top - CH.CHIMNEY["coping_t_m"])
    assert max(v[2] for v in parts["coping"][0]) == pytest.approx(top)
    assert min(v[2] for v in parts["cap"][0]) == pytest.approx(top)            # pots or cowls stand on the coping
    assert CH.measure(ch, model, _house()) == []


def test_the_looks_follow_the_family_and_are_never_a_grey_box():
    facade = {"facade": {"material": "render", "colour": "white", "asset": "grey_plaster"}}
    lk = CH.looks_of({"family": "scandinavian"}, facade)
    assert (lk["stack"]["material"], lk["stack"]["colour"]) == ("render", "white")
    assert lk["cap"]["material"] == "steel_black"
    lk = CH.looks_of({"family": "rustic"}, facade)
    assert lk["stack"]["material"] == "stone_wall_rubble" and (lk["cap"]["material"], lk["cap"]["colour"]) == \
        ("render", "terracotta")
    lk = CH.looks_of({"family": "classic"}, facade)
    assert lk["stack"]["material"] == "brick_red" and lk["coping"]["material"] == "limestone"
    lk = CH.looks_of({"family": "modern"}, {"facade": {"material": "wood_cladding", "colour": "oak"}})
    assert (lk["stack"]["material"], lk["stack"]["colour"]) == ("render", "oak")     # no flue in timber
    from wenart.blender import materials as M
    for fam in CH.FAMILY_CHIMNEYS:
        for look in CH.looks_of({"family": fam}, facade).values():
            assert look["material"] in M.ENTRIES and look["inferred"] and look["reason"]


# --------------------------------------------------------------------------------------------------------- M24
def test_m24_finds_a_floating_low_off_roof_or_window_blocking_chimney():
    b = _house()
    p, model = _plan(b)
    ch = p["chimneys"][0]
    lifted = [(x, y, z + 0.3) for x, y, z in CH.stack_bottom(ch, model)]
    assert [m["problem"] for m in CH.measure(ch, model, b, lifted)] == ["floats"]
    low = dict(ch, top_z=ch["top_z"] - 0.5)
    assert [m["problem"] for m in CH.measure(low, model, b)] == ["too_low"]
    off = dict(ch, center=[10.4, 4.0])
    assert [m["problem"] for m in CH.measure(off, model, b)] == ["off_roof"]
    # a window of a raised part of the house looks onto the roof 1 m from the stack
    hb = copy.deepcopy(b)
    hb["levels"].append({"id": "L1", "elevation": 3.5, "ceiling_height": 2.5, "kind": "floor"})
    hb["walls"].append(_wall("w_up", (5.0, 2.6), (7.0, 2.6), 0.2, True, level="L1"))
    hb["openings"].append({"id": "win_up", "type": "window", "level_id": "L1", "wall_id": "w_up", "center": [6.0, 2.6],
                           "width": 1.0, "height": 2.0, "sill_height": 0.5})
    near = dict(ch, center=[6.0, 3.6])
    got = CH.measure(near, model, hb)
    assert "window" in [m["problem"] for m in got]
    rec = {"objects": [{"detail": "chimney", "kind": "roof", "chimney": dict(CH.manifest_record(ch, model),
                                                                              bottom=[list(q) for q in lifted])}]}
    found, n = MR.chimneys_review(b, {"roof": model}, rec)
    assert n == 1 and [(f["check"], f["severity"], f["metrics"]["problem"]) for f in found] == [("M24", "critical",
                                                                                                    "floats")]
    assert "M24" in MR.CHECKS and K.CHECK_KIND["M24"] == "no_sense"
    # the inferred plan itself never stands in front of that window
    p2, model2 = _plan(hb)
    assert p2["chimneys"] and all(not CH.measure(c, model2, hb) for c in p2["chimneys"])


def test_the_model_review_runs_m24_on_the_plan():
    b = _house()
    model = R.roof_model(b["roof"], b)
    rev = MR.review(b, None, {"roof": model, "chimneys": CH.plan(b, model, "scandinavian"), "whole": False})
    assert rev["checks"]["M24"] == {"checked": 1, "failed": 0, "status": "ok"}


# --------------------------------------------------------------------------------------------------------- U27
def test_u27_finds_a_chimney_family_house_with_none_and_a_drawn_flue_left_out():
    b = _house()
    man = {"objects": [], "style_profile": {"family": "scandinavian"}, "whole_building": {"roof": {"type": "gable"}}}
    got = L.missing_chimneys(b, man)
    assert [(f["check"], f["kind"], f["target"]) for f in got] == [("U27", "taste", "roof")]
    p, model = _plan(b)
    built = dict(man, objects=[{"detail": "chimney", "kind": "roof", "chimney": CH.manifest_record(p["chimneys"][0],
                                                                                                   model)}])
    assert L.missing_chimneys(b, built) == []
    assert L.missing_chimneys(b, dict(man, style_profile={"family": "minimal"})) == []
    assert L.missing_chimneys(_house("flat"), dict(man, whole_building={"roof": {"type": "flat"}})) == []
    text = {"id": "TEXT:9", "level_id": "L0", "room_id": "r_mutfak", "text": "ŞÖMİNE", "pos": [8.0, 6.0]}
    drawn = _house(texts=[text])
    lost = L.missing_chimneys(drawn, dict(man, style_profile={"family": "minimal"}))
    assert [(f["check"], f["kind"], f["target"]) for f in lost] == [("U27", "lost", "TEXT:9")]
    p, model = _plan(drawn, "minimal")
    served = dict(man, objects=[{"detail": "chimney", "kind": "roof", "chimney": CH.manifest_record(p["chimneys"][0],
                                                                                                    model)}])
    assert L.missing_chimneys(drawn, served) == []
    assert L.CHECK_LESSONS["U27"] == ("UL109",) and K.CHECK_KIND["U27"] == "taste"
    assert "U27" in L.audit(b, man)["checked"]


# ------------------------------------------------------------------------------------- the reading and the build
def test_the_reading_keeps_fireplace_and_flue_texts():
    from wenart.ingest.generic import reading as RD

    def text(eid, s, x, y):
        return SimpleNamespace(text=s, entity=eid, evidence={"layer": "YAZI", "method": "vector"}, box=[x, y, x, y],
                               start=[x, y], height=0.2, rotation_deg=0.0, role="other")

    ex = SimpleNamespace(texts=[text("TEXT:1", "ŞÖMİNE", 2.0, 6.0), text("TEXT:2", "HAVA BACASI", 5.0, 7.0),
                                text("TEXT:3", "Salon", 3.0, 3.0)], labels=[],
                         transform_to_building=[1.0, 0.0, 0.0, 0.0, 1.0, 0.0], report={})
    rec = SimpleNamespace(level_id="L0", file="plan.dwg", page=None, format="dxf")
    build = SimpleNamespace(building=_house(), generic=[])
    got = RD.chimney_texts(build, {"p1": SimpleNamespace(extraction=ex, record=rec)})
    assert [(t["id"], t["kind"], t["room_id"]) for t in got] == [("TEXT:1", "fireplace", "r_salon")]
    schema = json.loads((ROOT / "wenart" / "schema" / "building.schema.json").read_text(encoding="utf-8"))
    assert "chimney_texts" in schema["properties"]


def test_the_build_plans_the_chimney_before_blender():
    out = B.prepare_once(_house(), "base", None, "scandinavian")
    assert out["chimneys"]["decision"] == "inferred" and out["chimneys"]["chimneys"][0]["wall_id"] == "w_in"
    summary = CH.summary(out["chimneys"])
    assert summary["decision"] == "inferred" and summary["chimneys"][0]["id"] == "chimney_1"


def test_lesson_ul109_is_built():
    data = json.loads((ROOT / "wenart" / "blender" / "architect_lessons.json").read_text(encoding="utf-8"))
    x = next(x for x in data["lessons"] if x["id"] == "UL109")
    assert x["status"] == "built" and x["checks"] == ["build"] and "U27" in x["lesson"] and "M24" in x["lesson"]
