"""The sheets stage and the pipeline on synthetic-07 against its truth (docs/synthetic.md "synthetic-07",
docs/milestone10.md §3.4, acceptance row 5): one CAD sheet in cm with every drawing kind.

Tolerances (stated once): region boxes 0.01 cm; registration shifts and transforms 1 cm; heights 1 mm (pitch 0.1°);
elevation positions 1 cm; site points 1 cm (labels: 1 m, their truth is the insertion point, ours the text's centre);
north 0.5°; walls: the same centre line within 2 cm and thickness within 1 cm, ends within 0.26 m of the truth's
(the truth runs every wall face to face, the core trims one wall of a corner or T at the other's face); rooms: label
and area within 0.05 m²; openings: type, centre and width within 2 cm.

Track A3 fixed the two gaps listed here before: the basement plan L-1 is built (a ray through a door or window gap of
one wall band counts as a hit, so the Salon is closed in) and ``KAPI_SURME_90`` is a sliding door (a leaf as long as
its gap, drawn half open). The elevation check leaves out the openings whose head is below the ground line (the
elevations do not draw them; ``sheets/to_building.plan_check``)."""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

import wenart.sheets as SH
from wenart import building as B
from wenart.ingest import pipeline as P

PROJECT = Path(__file__).resolve().parents[1] / "projects" / "synthetic-07"
TRUTH = PROJECT / "truth"


def _truth(name: str) -> dict:
    return json.loads((TRUTH / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def sheets(tmp_path_factory) -> dict:
    return SH.run(PROJECT, tmp_path_factory.mktemp("s07"), no_ai=True).doc


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    building, build = P.run_project(PROJECT, tmp_path_factory.mktemp("p07"), no_ai=True)
    return building, build


def _region(doc: dict, rid: str) -> dict:
    return next(r for r in doc["regions"] if r["id"] == rid)


def flat(value) -> list:
    """Nested lists of numbers -> one flat list (pytest.approx compares flat sequences only)."""
    if isinstance(value, (list, tuple)):
        return [x for v in value for x in flat(v)]
    return [value]


# ------------------------------------------------------------------------------------------------------------------
# Sheets stage
# ------------------------------------------------------------------------------------------------------------------

def test_regions_classes_titles_and_boxes(sheets):
    truth = _truth("sheets_truth.json")
    assert SH.validation_errors(sheets) == []
    assert [r["id"] for r in sheets["regions"]] == [r["id"] for r in truth["regions"]]
    for t in truth["regions"]:
        r = _region(sheets, t["id"])
        assert r["class"] == t["class"], t["id"]
        assert r["box"] == pytest.approx(t["box"], abs=0.01), t["id"]
        assert (r["title"] or {}).get("text") == (t["title"] or {}).get("text"), t["id"]
        assert r["use"] == t["use"], t["id"]
        assert r["class_method"] == ("geometry" if t["id"] == "r10" else "title"), t["id"]
    assert sheets["documents"][0]["sheets"][0]["frames"] == truth["documents"][0]["sheets"][0]["frames"]
    # Title and geometry decide every region: no AI question (§3.1 item 2).
    assert sheets["questions"] == 0


def test_units_are_cm_without_conflict(sheets):
    units = sheets["documents"][0]["units"]
    assert units["metres_per_unit"] == 0.01 and units["method"] == "dxf_insunits" and units["conflict"] is None
    assert not [c for c in sheets["conflicts"] if c["kind"] == "unit_mismatch"]


def test_one_stray(sheets):
    truth = _truth("sheets_truth.json")["stray"]
    assert [s["entity"] for s in sheets["stray"]] == [s["entity"] for s in truth]
    assert sheets["stray"][0]["distance_m"] == pytest.approx(truth[0]["distance_m"], abs=0.1)


def test_levels_and_the_alternative_group(sheets):
    truth = _truth("sheets_truth.json")
    got = [(lv["id"], lv["order"], lv["kind"], lv["base_region"],
            [(a["region"], a["variant"], a["slug"], a["level_id"]) for a in lv["alternatives"]])
           for lv in sheets["levels"]]
    want = [(lv["id"], lv["order"], lv["kind"], lv["base_region"],
             [(a["region"], a["variant"], a["slug"], a["level_id"]) for a in lv["alternatives"]])
            for lv in truth["levels"]]
    assert got == want
    alt = _region(sheets, "r2")
    assert alt["title"]["text"] == "BODRUM KAT PLANI (AÇIK MUTFAK)" and alt["variant_gloss"] == "open kitchen"
    assert alt["variant_group"] == "vg_L-1" and _region(sheets, "r1")["variant_group"] == "vg_L-1"
    assert [(v["id"], v["label"], v["levels"], v["regions"]) for v in sheets["variants"]] == \
        [(v["id"], v["label"], v["levels"], v["regions"]) for v in truth["variants"]]


def test_registration_shifts(sheets):
    truth = _truth("sheets_truth.json")
    for t in truth["regions"]:
        if not t.get("registration"):
            continue
        r = _region(sheets, t["id"])
        assert r["registration"]["shift_m"] == pytest.approx(t["registration"]["shift_m"], abs=0.01), t["id"]
        assert r["registration"]["rotation_deg"] == 0.0
        assert r["transform_to_building"] == pytest.approx(t["transform_to_building"], abs=0.01), t["id"]
        if t["class"] != "site_plan":
            assert r["registration"]["residual_m"] <= 0.01, t["id"]
    assert _region(sheets, "r5")["registration"]["method"] == "site_outline"
    assert all(_region(sheets, rid)["registration"]["stairs_aligned"] for rid in ("r1", "r2", "r4"))
    assert sheets["conflicts"] == []


def test_heights(sheets):
    truth = _truth("heights_truth.json")
    h = sheets["heights"]
    assert (h["cut_axis"], h["cut_at"], h["flipped"]) == (truth["cut_axis"], truth["cut_at"], truth["flipped"])
    assert h["datum"]["value"] == pytest.approx(truth["datum"]["value"])
    got = {lv["level_id"]: lv for lv in h["levels"]}
    for t in truth["levels"]:
        lv = got[t["level_id"]]
        for key in ("floor_z", "ceiling_height", "level_mark", "level_mark_target_z"):
            assert lv[key]["value"] == pytest.approx(t[key], abs=0.001), (t["level_id"], key)
        if t["floor_to_floor"] is None:
            assert lv["floor_to_floor"] is None
        else:
            assert lv["floor_to_floor"]["value"] == pytest.approx(t["floor_to_floor"], abs=0.001)
    assert [(s["between"], round(s["thickness"]["value"], 3), round(s["z_top"]["value"], 3)) for s in h["slabs"]] == \
        [(s["between"], s["thickness"], s["z_top"]) for s in truth["slabs"]]
    assert not [c for c in sheets["conflicts"] if c["kind"] == "level_mark_mismatch"]
    # The section's two sides: south (front, -Y) and north (back), both 0.00 (the east one is on the elevation).
    assert [(g["side"], g["z"]["value"]) for g in h["ground"]] == [("front", 0.0), ("back", 0.0)]
    roof, troof = h["roof"], truth["roof"]
    for key in ("eaves_z", "ridge_z", "overhang", "thickness"):
        assert roof[key]["value"] == pytest.approx(troof[key], abs=0.001), key
    assert [p["value"] for p in roof["pitches_deg"]] == pytest.approx(troof["pitches_deg"], abs=0.1)
    assert flat(roof["profile"]) == pytest.approx(flat(troof["profile"]), abs=0.001)
    # knee_wall follows building.schema (the top surface at the outer face: 3.00 + 1.305); the truth's 1.00 is the
    # underside there, which the note gives.
    assert roof["knee_wall"]["value"] == pytest.approx(0.5 * math.tan(math.radians(35)) + 0.95509, abs=0.001)
    assert f"underside meets the outer face {troof['knee_wall']:.2f} m" in roof["knee_wall"]["note"]


def test_roof_from_the_section_seen_on_the_elevation(sheets):
    truth = _truth("exterior_truth.json")["roof"]
    roof = sheets["exterior"]["roof"]
    assert (roof["type"], roof["type_source"]) == (truth["type"], truth["type_source"])
    assert flat(roof["outline"]) == pytest.approx(flat(truth["outline"]), abs=0.01)
    assert flat(roof["ridge_lines"]) == pytest.approx(flat(truth["ridge_lines"]), abs=0.01)
    assert roof["break_line"] is None and roof["covering"] == truth["covering"]
    assert roof["also_seen_in"] == ["elevation"]
    assert not any(a.startswith("hip/gable") for a in roof["assumed"])


def test_facade_and_elevations(sheets):
    truth = _truth("exterior_truth.json")
    ex = sheets["exterior"]
    faces = {(f["side"], f["material"]): f for f in ex["facade"]}
    stone = faces[("south", "stone_cladding")]
    assert stone["source"] == "hatch" and stone["z_range"] == pytest.approx([0.0, 0.6], abs=0.001)
    assert {"HATCH:252", "TEXT:259"} <= {e["entity"] for e in stone["evidence"]}
    # Render from the labels on both elevations (z_range null = the whole height; the truth bands it).
    assert faces[("south", "render")]["source"] == "label" and faces[("east", "render")]["source"] == "label"
    assert len(ex["facade"]) == len(truth["facade"])
    for t in truth["openings_seen"]:
        seen = next(s for s in ex["openings_seen"] if s["region"] == t["region"])
        assert (seen["side"], seen["view_bearing_deg"], seen["windows"], seen["doors"]) == \
            (t["side"], t["view_bearing_deg"], t["windows"], t["doors"])
        got = sorted((p["kind"], p["x"], p["x_left"], p["width"], p["sill"], p["head"]) for p in seen["positions_m"])
        want = sorted((p["kind"], p["x"], p["x_left"], p["width"], p["sill"], p["head"]) for p in t["positions_m"])
        assert [g[0] for g in got] == [w[0] for w in want]
        assert flat([g[1:] for g in got]) == pytest.approx(flat([w[1:] for w in want]), abs=0.01)


def test_site_plan(sheets):
    truth = _truth("exterior_truth.json")
    site, tsite = sheets["exterior"]["site"], truth["site"]
    assert site["registered"] and flat(site["plot"]) == pytest.approx(flat(tsite["plot"]), abs=0.01)
    parking = flat([p["polygon"] for p in site["parking"]])
    assert parking == pytest.approx(flat([p["polygon"] for p in tsite["parking"]]), abs=0.01)
    assert flat(sorted(t["points"][0] for t in site["trees"])) == \
        pytest.approx(flat(sorted(t["center"] for t in tsite["trees"])), abs=0.01)
    assert all(t["radius_m"] == pytest.approx(1.2, abs=0.01) for t in site["trees"])
    walls = sorted((tuple(w["start"]), tuple(w["end"])) for w in site["plot_walls"])
    twalls = sorted((tuple(w["start"]), tuple(w["end"])) for w in tsite["plot_walls"])
    assert len(walls) == len(twalls) and all(w["thickness"] == pytest.approx(0.2) for w in site["plot_walls"])
    for (a, b), (c, d) in zip(sorted(walls, key=lambda w: sorted(w)), sorted(twalls, key=lambda w: sorted(w))):
        assert flat(sorted([a, b])) == pytest.approx(flat(sorted([c, d])), abs=0.01)
    labels = {lab["label"]: lab for lab in site["labels"]}
    assert labels["OTOPARK"]["kind"] == "parking" and labels["BAHÇE"]["kind"] == "garden"
    for t in tsite["labels"]:
        if t["text"] in labels:
            assert math.dist(labels[t["text"]]["point"], t["at"]) <= 1.0
    assert sheets["exterior"]["north"]["value"] == pytest.approx(truth["north"]["value"], abs=0.5)


# ------------------------------------------------------------------------------------------------------------------
# Pipeline
# ------------------------------------------------------------------------------------------------------------------

def _same_line(w: dict, t: dict) -> bool:
    """The same wall within the stated tolerances (centre line 2 cm, thickness 1 cm, ends 0.26 m)."""
    def axis(x):
        (x0, y0), (x1, y1) = x["start"], x["end"]
        vertical = abs(x1 - x0) < abs(y1 - y0)
        return vertical, ((x0 + x1) / 2.0 if vertical else (y0 + y1) / 2.0), \
            sorted((y0, y1) if vertical else (x0, x1))
    vw, cw, sw = axis(w)
    vt, ct, st = axis(t)
    return vw == vt and abs(cw - ct) <= 0.02 and abs(w["thickness"] - t["thickness"]) <= 0.01 \
        and abs(sw[0] - st[0]) <= 0.26 and abs(sw[1] - st[1]) <= 0.26


BUILT = ("L-1b", "L0", "L1")


def test_pipeline_levels_heights_and_variants(built):
    building, build = built
    truth = _truth("building.json")
    assert building["status"] == "ok" and B.validation_errors(building) == []
    tl = {lv["id"]: lv for lv in truth["levels"]}
    for lv in building["levels"]:
        t = tl[lv["id"]]
        for key in ("elevation", "ceiling_height", "kind", "variant", "variant_slug", "base_level_id", "region_id",
                    "elevation_source"):
            want = t[key]
            assert lv[key] == (pytest.approx(want, abs=0.001) if isinstance(want, float) else want), (lv["id"], key)
    assert building["project"]["datum"]["value"] == pytest.approx(0.0)
    pages = {p["region_id"]: p for p in building["documents"][0]["pages"]}
    for p in truth["documents"][0]["pages"]:
        assert pages[p["region_id"]]["region_box"] == pytest.approx(p["region_box"], abs=0.01)
        assert pages[p["region_id"]]["region_class"] == p["region_class"]


@pytest.mark.parametrize("level_id", BUILT)
def test_pipeline_walls_rooms_openings(built, level_id):
    building, _ = built
    truth = _truth("building.json")
    walls = [w for w in building["walls"] if w["level_id"] == level_id]
    twalls = [w for w in truth["walls"] if w["level_id"] == level_id]
    assert len(walls) == len(twalls)
    assert all(any(_same_line(w, t) for w in walls) for t in twalls), level_id
    assert sorted(w["exterior"] for w in walls) == sorted(w["exterior"] for w in twalls)
    rooms = sorted((r["label"], r["area_computed"]) for r in building["rooms"] if r["level_id"] == level_id)
    trooms = sorted((r["label"], r["area_computed"]) for r in truth["rooms"] if r["level_id"] == level_id)
    assert [r[0] for r in rooms] == [r[0] for r in trooms]
    assert [r[1] for r in rooms] == pytest.approx([r[1] for r in trooms], abs=0.05)
    ops = [o for o in building["openings"] if o["level_id"] == level_id]
    for t in truth["openings"]:
        if t["level_id"] != level_id or t.get("operation") == "sliding":
            continue
        hit = [o for o in ops if o["type"] == t["type"] and math.dist(o["center"], t["center"]) <= 0.02
               and abs(o["width"] - t["width"]) <= 0.02]
        assert hit, (level_id, t["id"], t["type"], t["center"])
        if t["type"] == "door":
            assert hit[0].get("operation") == t["operation"], (level_id, t["id"])


def test_double_door_on_the_ground_floor(built):
    building, _ = built
    double = [o for o in building["openings"] if o.get("operation") == "double"]
    assert [(o["level_id"], o["width"]) for o in double] == [("L0", pytest.approx(1.4, abs=0.02))]
    assert double[0]["operation_source"] == "geometry"


def test_sliding_doors_in_both_basement_plans(built):
    building, _ = built
    sliding = sorted(o["level_id"] for o in building["openings"] if o.get("operation") == "sliding")
    assert sliding == ["L-1", "L-1b"]


def test_all_four_plan_levels_build(built):
    building, _ = built
    assert [lv["id"] for lv in building["levels"]] == ["L-1", "L-1b", "L0", "L1"]
    variants = {v["id"]: v for v in building["variants"]}
    assert variants["l-1b-acik-mutfak"]["rooms_changed"] == ["r_L-1b_salon_acik_mutfak"]
    assert variants["l-1b-acik-mutfak"]["exterior_changed"] is False


def test_pipeline_roof_facade_and_site(built):
    building, _ = built
    ext = _truth("exterior_truth.json")
    roof = building["roof"]
    assert roof["type"] == "gable" and roof["over_level_id"] == "L1" and roof["covering"] == "clay_tiles"
    assert roof["covering_source"] == "elevation"
    assert flat(roof["profile"]["points"]) == pytest.approx(flat(_truth("heights_truth.json")["roof"]["profile"]),
                                                          abs=0.001)
    (terrace,) = roof["openings"]
    assert terrace["room_id"] == ext["roof"]["openings"][0]["room_id"]
    assert flat(terrace["polygon"]) == pytest.approx(flat(ext["roof"]["openings"][0]["polygon"]), abs=0.01)
    assert len(terrace["parapet_wall_ids"]) == len(ext["roof"]["openings"][0]["parapet_wall_ids"])
    faces = {(f["side"], f["material"]): f for f in building["facade"]["faces"]}
    assert faces[("south", "stone_cladding")]["z_range"] == pytest.approx([0.0, 0.6])
    site = building["site"]
    assert site["north_deg"]["value"] == pytest.approx(0.0, abs=0.5)
    assert [(g["side"], g["z"]["value"]) for g in site["ground"]["levels"]] == [("south", 0.0), ("north", 0.0)]
    assert site["plot"]["source"] == "site_plan"
    assert flat(site["plot"]["polygon"]) == pytest.approx(flat(ext["site"]["plot"]))
    assert len([w for w in site["boundary_walls"] if w["kind"] == "plot"]) == 4
    parking = site["parking"][0]
    assert flat(parking["polygon"]) == pytest.approx(flat(ext["site"]["parking"][0]["polygon"]), abs=0.01)
    assert next(a for a in site["areas"] if a["id"] == parking["area_id"])["kind"] == "parking"
    assert flat(sorted(d["center"] for d in site["decor"] if d["kind"] == "tree")) == \
        pytest.approx(flat(sorted(t["center"] for t in ext["site"]["trees"])), abs=0.01)


def test_elevation_openings_match_the_plans(built):
    building, _ = built
    # The elevations' openings match the plans' (elevation_opening_mismatch stays empty).
    for e in building["facade"]["elevations"]:
        assert e["plan_check"]["missing"] == 0 and e["plan_check"]["extra"] == 0, e["region_id"]


@pytest.mark.skipif(not __import__("wenart.ingest.dwg", fromlist=["x"]).available_converters(),
                    reason="LibreDWG dwg2dxf not installed")
def test_the_dwg_copy_reads_like_the_dxf(tmp_path, sheets):
    # source/sheet.dwg holds the same sheet (docs/synthetic.md): a project with the DWG alone gives the same regions,
    # classes, levels, registration and heights (entity handles differ).
    import shutil

    project = tmp_path / "synthetic-07-dwg"
    project.mkdir()
    shutil.copy(PROJECT / "source" / "sheet.dwg", project / "sheet.dwg")
    shutil.copy(PROJECT / "brief.yaml", project / "brief.yaml")
    doc = SH.run(project, tmp_path / "out", no_ai=True).doc
    assert [(r["id"], r["class"], r["use"]) for r in doc["regions"]] == \
        [(r["id"], r["class"], r["use"]) for r in sheets["regions"]]
    for r, s in zip(doc["regions"], sheets["regions"]):
        assert r["box"] == pytest.approx(s["box"], abs=0.01), r["id"]
        assert (r["title"] or {}).get("text") == (s["title"] or {}).get("text"), r["id"]
        if s["registration"]:
            assert r["registration"]["shift_m"] == pytest.approx(s["registration"]["shift_m"], abs=0.01), r["id"]
    assert [lv["id"] for lv in doc["levels"]] == [lv["id"] for lv in sheets["levels"]]
    assert [lv["floor_z"]["value"] for lv in doc["heights"]["levels"]] == \
        pytest.approx([lv["floor_z"]["value"] for lv in sheets["heights"]["levels"]], abs=0.001)
    assert doc["heights"]["roof"]["ridge_z"]["value"] == pytest.approx(sheets["heights"]["roof"]["ridge_z"]["value"],
                                                                       abs=0.001)


def test_untitled_plans_with_a_section_need_review_without_a_crash(tmp_path):
    # Review finding 8: no plan level known but a usable section: the heights are assumed, sheets.json and the
    # report are written and the CLI exits 1 (needs review), not 2 with a traceback.
    from ezdxf import recover

    from wenart.sheets import __main__ as CLI

    project = tmp_path / "untitled"
    project.mkdir()
    doc, _ = recover.readfile(str(PROJECT / "sheet.dxf"))
    msp = doc.modelspace()
    for handle in ("164", "1AF", "202", "230"):                 # the four plan titles
        msp.delete_entity(doc.entitydb[handle])
    doc.saveas(project / "sheet.dxf")
    out = tmp_path / "out"
    assert CLI.main([str(project), "--out", str(out), "--no-ai"]) == CLI.EXIT_REVIEW
    sheets = SH.load(out)
    assert sheets["levels"] == [] and sheets["needs_review"]
    assert any("no plan level known" in w for w in sheets["warnings"])
    assert (out / "sheets_report.md").is_file()
