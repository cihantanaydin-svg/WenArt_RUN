"""real02 (``projects/real02/one_building.dwg``) through the sheets stage and the pipeline handover (docs/milestone10.md
§0.1, §5 acceptance rows 2 and 3 (heights)). Needs LibreDWG ``dwg2dxf`` (``scripts/cloud-setup.sh``); the DWG is
converted once per session into a temporary folder (about a minute).

The walls of real02 are drawn as open face lines (§0.4): until the face-line wall primitive (track A3) lands, the
plans are read but left out (``failed_levels: leave_out``) and the project ends ``needs_review`` with each region
named; the assertions on the building accept both states."""
from __future__ import annotations

import pytest

import wenart.sheets as SH
from conftest import PROJECTS
from wenart.ingest import dwg

pytestmark = pytest.mark.skipif(not dwg.available_converters(), reason="LibreDWG dwg2dxf not installed")


@pytest.fixture(scope="session")
def real02(tmp_path_factory):
    out = tmp_path_factory.mktemp("real02")
    result = SH.run(PROJECTS / "real02", out, no_ai=True)
    return {"out": out, "result": result, "doc": result.doc}


def _by_title(doc, words):
    return next(r for r in doc["regions"] if r.get("title") and r["title"]["text"].strip() == words)


def test_valid_and_ok(real02):
    doc = real02["doc"]
    assert SH.validation_errors(doc) == []
    assert doc["needs_review"] == [] and doc["multi_region"] is True


def test_four_plans_one_section_and_the_title_box(real02):
    doc = real02["doc"]
    classes = sorted(r["class"] for r in doc["regions"])
    assert classes == ["alternative_floor_plan", "floor_plan", "floor_plan", "floor_plan", "section", "title_block"]
    titles = {r["title"]["text"].strip(): r for r in doc["regions"] if r.get("title")}
    assert titles["PLANLAR"]["class"] == "title_block" and titles["PLANLAR"]["use"] == "ignored"
    assert titles["BODRUM KAT PLANI BRÜT 92 M2"]["level"]["id"] == "L-1"
    assert titles["ZEMİN KAT PLANI BRÜT 92M2"]["level"]["id"] == "L0"
    assert titles["ÇATI KAT PLANI"]["level"]["id"] == "L1" and titles["ÇATI KAT PLANI"]["level"]["kind"] == "attic"
    alt = titles["BODRUM KAT PLANI BRÜT 92 M2 ( Açık mutfak)"]
    assert alt["class"] == "alternative_floor_plan" and alt["level"]["id"] == "L-1b"
    assert (alt["variant"], alt["variant_slug"], alt["variant_gloss"]) == ("Açık mutfak", "acik-mutfak", "open kitchen")
    assert alt["variant_group"] == "vg_L-1"
    section = next(r for r in doc["regions"] if r["class"] == "section")
    assert section["title"] is None and section["class_method"] == "geometry" and section["use"] == "heights"
    for r in doc["regions"]:
        if r["use"] == "read":
            assert r["box_m"][0] == pytest.approx(15.17, abs=0.02) or r["box_m"][0] == pytest.approx(16.17, abs=0.02)


def test_strays(real02):
    strays = {s["entity"]: s for s in real02["doc"]["stray"]}
    assert set(strays) == {"HATCH:6633", "DIMENSION:34CEC", "DIMENSION:34CF2"}
    assert strays["HATCH:6633"]["layer"] == "_P3_S_Duvar_T" and strays["HATCH:6633"]["distance_m"] > 300
    assert all("outside the frame" in s["reason"] for s in strays.values())


def test_levels_and_variants(real02):
    doc = real02["doc"]
    assert [(lv["id"], lv["kind"]) for lv in doc["levels"]] == [("L-1", "basement"), ("L0", "floor"), ("L1", "attic")]
    assert [v["id"] for v in doc["variants"]] == ["base", "l-1b-acik-mutfak"]
    assert doc["variants"][1]["levels"] == ["L-1b", "L0", "L1"]


def test_units_are_centimetres_with_the_mismatch_listed(real02):
    doc = real02["doc"]
    units = doc["documents"][0]["units"]
    assert units["insunits"] == 4 and units["metres_per_unit"] == 0.01 and units["method"] == "unit_check"
    assert any(c["kind"] == "unit_mismatch" for c in doc["conflicts"])
    decided = {c["check"]: c["unit"] for c in units["checks"]}
    assert decided["area_labels"] == "cm" and decided["level_marks"] == "cm"


def test_heights(real02):
    doc = real02["doc"]
    h = doc["heights"]
    floors = {lv["level_id"]: lv["floor_z"]["value"] for lv in h["levels"]}
    assert floors == pytest.approx({"L-1": -3.0, "L0": 0.0, "L1": 3.15}, abs=0.01)
    f2f = {lv["level_id"]: (lv["floor_to_floor"] or {}).get("value") for lv in h["levels"]}
    assert f2f["L-1"] == pytest.approx(3.0, abs=0.01) and f2f["L0"] == pytest.approx(3.15, abs=0.01)
    assert all(s["thickness"]["value"] == pytest.approx(0.15, abs=0.01) for s in h["slabs"])
    assert h["datum"]["value"] == 43.0 and h["cut_axis"] == "x"
    mism = [c for c in doc["conflicts"] if c["kind"] == "level_mark_mismatch"]
    assert len(mism) == 1 and "40.00" in mism[0]["description"] and "0.15 m apart" in mism[0]["description"]
    roof = h["roof"]
    pitches = sorted(p["value"] for p in roof["pitches_deg"])
    assert pitches[0] == pytest.approx(13.0, abs=0.5) and pitches[1] == pytest.approx(40.0, abs=0.5)
    attic = floors["L1"]
    assert roof["eaves_z"]["value"] - attic == pytest.approx(0.50, abs=0.01)
    assert roof["ridge_z"]["value"] - attic == pytest.approx(3.64, abs=0.01)
    assert roof["overhang"]["value"] == pytest.approx(0.50, abs=0.01)
    profile_width = roof["profile"][-1][0] - roof["profile"][0][0]
    assert profile_width == pytest.approx(15.17 + 2 * 0.50, abs=0.02)
    assert all(lv["floor_z"]["evidence"] for lv in h["levels"])


def test_registration_and_the_outline_polylines(real02):
    doc = real02["doc"]
    plans = [r for r in doc["regions"] if r["use"] == "read"]
    for r in plans:
        assert r["registration"]["residual_m"] <= 0.05 and r["registration"]["rotation_deg"] == 0.0
    note = next(w for w in doc["warnings"] if w.startswith("the largest drawn polylines"))
    assert "7.19 x 10.50" in note and "7.59 x 10.50" in note


def test_mansard_from_the_attic_plan(real02):
    roof = real02["doc"]["exterior"]["roof"]
    assert roof["type"] == "mansard" and roof["type_source"] == "plan_roof_lines"
    entities = {e["entity"] for e in roof["evidence"]}
    assert {"LWPOLYLINE:304CA", "LWPOLYLINE:2F87A"} <= entities
    xs = [p[0] for p in roof["outline"]]
    ys = [p[1] for p in roof["outline"]]
    assert max(xs) - min(xs) == pytest.approx(16.17, abs=0.01) and max(ys) - min(ys) == pytest.approx(13.0, abs=0.01)
    assert real02["doc"]["exterior"]["facade"] == []


def test_pipeline_reads_one_record_per_region(real02):
    from wenart.ingest import pipeline as P

    building, build = P.run_project(PROJECTS / "real02", real02["out"], no_ai=True)
    pages = building["documents"][0]["pages"]
    assert [p["region_id"] for p in pages] == [r["id"] for r in real02["doc"]["regions"]]
    plans = [p for p in pages if p["region_class"] in ("floor_plan", "alternative_floor_plan")]
    assert all(p["scale"]["metres_per_unit"] == 0.01 for p in plans)
    left = {x["region_id"] for x in building.get("levels_left_out") or []}
    built = {lv["region_id"] for lv in building["levels"]}
    assert left | built == {p["region_id"] for p in plans}
    if building["status"] == "needs_review":
        reasons = [w for w in building["warnings"] if w.startswith("needs review: r")]
        assert reasons and all("(L" in r for r in reasons)
    assert any(c["kind"] == "unit_mismatch" for c in building["conflicts"])
