"""Milestone 10 GPU tests: sheets, the whole building, exterior views, the checks and the report
(docs/milestone10.md §5 rows 1-4, 6; Feature 1's own checks are in tests/gpu/test_m10_completion.py).

Run on the pod after a full run of the projects (``pytest -m gpu tests/gpu/test_m10.py``). They read what the
stages wrote under $WENART_OUTPUTS (default /workspace/repo/outputs) for the projects in $M10_TEST_PROJECTS
(default ``real02``); the sheet readings of §0.1 are checked on $M10_SHEETS_PROJECTS (default ``real02``):

- sheets (real02): ``sheets.json`` validates against its schema; 4 plans (basement, basement "Açık mutfak",
  ground floor, attic) and 1 section are read; the stray HATCH ``6633`` is listed (the two DIMENSIONs, when
  listed, are exactly two); the levels are -1, 0, 1 (attic) with the basement's variant group (one alternative,
  two variants); the units are centimetres by the unit check with the ``unit_mismatch`` conflict listed;
- the whole building: every level above the lowest has a slab at its floor level (±1 cm), the levels rise with
  their order, the roof sits over the top level with its eaves under its ridge, every height has evidence or is
  ``assumed``, and the scene manifest holds the built slabs and the roof;
- exterior views: per variant at least 5 are rendered (the base and an alternative whose outside changed) or the
  base views are listed for it (an unchanged outside, ``wenart.views.views_for``); the four corners and the
  aerial view are rendered or dropped with a reason; every rendered one is checked (kind ``exterior``, the
  roof check), the elevation check and the drawn-piece check are in the check manifest, and the exterior polish
  follows the per-kind gate decision (``exterior_gate`` of the polish, ``exterior`` of the gate calibration);
- the final report: the Sheets, Building, Exterior views and Variants sections, a contact sheet of the exterior
  views per variant, the Feature 1 lists (every ``modified_by_ai`` piece with its drawn type and size) and every
  assumed value (heights, slabs, roof, outside looks) in the manifest's ``assumed`` block.
"""
import json
import os
import re
from pathlib import Path

import pytest

from wenart import views as VW

pytestmark = pytest.mark.gpu
OUTPUTS = Path(os.environ.get("WENART_OUTPUTS", "/workspace/repo/outputs"))
PROJECTS = [p for p in os.environ.get("M10_TEST_PROJECTS", "real02").split() if p]
SHEETS_PROJECTS = [p for p in os.environ.get("M10_SHEETS_PROJECTS", "real02").split() if p]
ELEVATION_STRICT = [p for p in os.environ.get("M10_ELEVATION_STRICT", "synthetic-07").split() if p]
MIN_EXTERIOR_VIEWS = 5
SLAB_TOLERANCE_M = 0.01
PLAN_CLASSES = ("floor_plan", "alternative_floor_plan")


def _load(project: str, rel: str):
    path = OUTPUTS / project / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _need(project: str, rel: str) -> dict:
    doc = _load(project, rel)
    assert doc is not None, f"{OUTPUTS / project / rel} missing: did the stage that writes it run for {project}?"
    return doc


def _variant_dir(project: str, variant: str) -> str:
    """The project-relative folder of a variant's outputs: the base is the project itself."""
    return "" if variant == "base" else f"variants/{variant}/"


def _value(rec):
    return rec.get("value") if isinstance(rec, dict) else rec


def _has_evidence_or_assumed(rec) -> bool:
    """A ``{value, method, evidence}`` record: evidence from a document, or the method ``assumed``."""
    return isinstance(rec, dict) and (rec.get("method") == "assumed" or bool(rec.get("evidence")))


# --------------------------------------------------------------------------
# Sheets (real02)
# --------------------------------------------------------------------------

@pytest.fixture(scope="module", params=SHEETS_PROJECTS)
def sheets(request):
    return request.param, _need(request.param, "sheets.json")


def test_sheets_json_validates_against_its_schema(sheets):
    import jsonschema

    project, doc = sheets
    schema = json.loads((Path(__file__).resolve().parents[2] / "wenart" / "schema" / "sheets.schema.json")
                        .read_text(encoding="utf-8"))
    errors = [f"{'/'.join(str(p) for p in e.absolute_path)}: {e.message}"
              for e in jsonschema.Draft202012Validator(schema).iter_errors(doc)]
    assert errors == [], f"{project}: sheets.json: {errors[:5]}"


def test_real02_reads_four_plans_and_one_section(sheets):
    project, doc = sheets
    read = [r for r in doc["regions"] if r["use"] == "read" and r["class"] in PLAN_CLASSES]
    assert len(read) == 4, f"{project}: plans read {[(r['id'], r['class'], r['use']) for r in doc['regions']]}"
    assert sum(r["class"] == "alternative_floor_plan" for r in read) == 1
    sections = [r for r in doc["regions"] if r["class"] == "section"]
    assert len(sections) == 1 and sections[0]["use"] in ("heights", "read"), sections
    assert doc["heights"]["section_regions"] == [sections[0]["id"]]
    assert not [r for r in doc["regions"] if r["use"] == "read" and r["class"] not in PLAN_CLASSES]
    print(f"{project}: {len(doc['regions'])} regions; plans {[r['id'] for r in read]}; section {sections[0]['id']}")


def test_real02_lists_its_strays(sheets):
    project, doc = sheets
    assert any("6633" in str(s["entity"]) and s["type"] == "HATCH" for s in doc["stray"]), \
        f"{project}: the stray HATCH 6633 is not listed: {doc['stray']}"
    dims = [s for s in doc["stray"] if s["type"] == "DIMENSION"]
    assert len(dims) in (0, 2), f"{project}: {len(dims)} stray DIMENSION(s); the drawing has exactly two outside"
    for s in doc["stray"]:
        assert s["reason"] and s["distance_m"] > 0, s
    print(f"{project}: strays {[(s['type'], s['entity']) for s in doc['stray']]}")


def test_real02_levels_and_the_basement_variant_group(sheets):
    project, doc = sheets
    levels = {lv["order"]: lv for lv in doc["levels"]}
    assert sorted(levels) == [-1, 0, 1], f"{project}: level orders {sorted(levels)}"
    assert levels[-1]["kind"] == "basement" and levels[1]["kind"] == "attic" and levels[0]["kind"] == "floor"
    assert len(levels[-1]["alternatives"]) == 1 and not levels[-1]["alternatives"][0]["base_unclear"]
    assert not levels[0]["alternatives"] and not levels[1]["alternatives"]
    variants = {v["id"]: v for v in doc["variants"]}
    assert len(variants) == 2 and "base" in variants, list(variants)
    alt = next(v for v in doc["variants"] if not v["base"])
    assert levels[-1]["alternatives"][0]["level_id"] in alt["levels"] and levels[-1]["id"] not in alt["levels"]
    assert alt["id"].endswith(levels[-1]["alternatives"][0]["slug"]), alt["id"]


def test_real02_units_are_centimetres_by_the_unit_check(sheets):
    project, doc = sheets
    units = doc["documents"][0]["units"]
    assert units["metres_per_unit"] == pytest.approx(0.01), units
    assert units["method"] == "unit_check" and units["insunits"] == 4 and units["conflict"], units
    agreeing = {c["check"] for c in units["checks"] if c["unit"] == "cm"}
    assert {"area_labels", "level_marks"} <= agreeing, units["checks"]
    conflicts = [c for c in doc["conflicts"] if c["kind"] == "unit_mismatch"]
    assert conflicts, f"{project}: no unit_mismatch conflict listed"
    assert "$INSUNITS" in conflicts[0]["description"] or "INSUNITS" in conflicts[0]["description"]


# --------------------------------------------------------------------------
# The whole building
# --------------------------------------------------------------------------

@pytest.fixture(scope="module", params=PROJECTS)
def project(request):
    return request.param


@pytest.fixture(scope="module")
def building(project):
    return _need(project, "building_final.json")


def test_levels_are_stacked_with_slabs(project, building):
    base_ids = [v for v in building["variants"] if v.get("base")][0]["levels"]
    levels = sorted((lv for lv in building["levels"] if lv["id"] in base_ids), key=lambda lv: lv["order"])
    assert len(levels) >= 2, f"{project}: {len(levels)} level(s) in the base variant"
    elevations = [lv["elevation"] for lv in levels]
    assert elevations == sorted(elevations) and len(set(elevations)) == len(elevations), elevations
    slabs = {s["above_level_id"]: s for s in building.get("slabs") or [] if not s.get("variants")}
    for lv in levels[1:]:
        s = slabs.get(lv["id"])
        assert s is not None, f"{project}: no slab under level {lv['id']}"
        assert abs(s["z_top"] - lv["elevation"]) <= SLAB_TOLERANCE_M, (lv["id"], s["z_top"], lv["elevation"])
        assert s["thickness"] > 0 and s["thickness_source"] in ("section", "elevation_drawing", "assumed_default")
        assert len(s["outline"]) >= 3 and s["evidence"], s["id"]
    for lv in levels:
        assert lv["ceiling_height"] > 1.5 and lv["ceiling_height_source"] in (
            "section", "elevation_drawing", "assumed_default"), lv["id"]
        assert lv.get("evidence") or lv["ceiling_height_source"] == "assumed_default", lv["id"]
    print(f"{project}: levels {[(lv['id'], lv['elevation']) for lv in levels]}, slabs {sorted(slabs)}")


def test_the_roof_sits_over_the_top_level(project, building):
    roof = building.get("roof")
    assert roof is not None, f"{project}: no roof in the building JSON"
    base = [v for v in building["variants"] if v.get("base")][0]["levels"]
    top = max((lv for lv in building["levels"] if lv["id"] in base), key=lambda lv: lv["order"])
    assert roof["over_level_id"] == top["id"], (roof["over_level_id"], top["id"])
    eaves, ridge = _value(roof["eaves_height"]), _value(roof["ridge_height"])
    assert eaves is not None and ridge is not None and ridge > eaves > top["elevation"], (eaves, ridge)
    for key in ("eaves_height", "ridge_height"):
        assert _has_evidence_or_assumed(roof[key]), f"{project}: roof {key} has neither evidence nor method assumed"
    assert roof["type"] in ("flat", "gable", "hip", "mansard", "gambrel", "shed", "other")
    assert roof["planes"] or roof["type"] == "flat", f"{project}: a {roof['type']} roof without planes"


def test_the_scene_holds_the_built_slabs_and_the_roof(project, building):
    scene = _need(project, "scene/scene_manifest.json")
    kinds = {}
    for o in scene["objects"]:
        kinds.setdefault(o["kind"], []).append(o)
    assert kinds.get("slab"), f"{project}: no slab in the scene manifest"
    assert kinds.get("roof"), f"{project}: no roof in the scene manifest"
    assert all(o.get("pass_index") in (None, 0) for o in kinds["slab"] + kinds["roof"]), \
        "slabs and the roof carry no pass index"
    ids = {o["wenart_id"] for o in kinds["slab"]}
    for s in building.get("slabs") or []:
        if not s.get("variants"):
            assert s["id"] in ids, f"{project}: slab {s['id']} of the building is not in the scene"


# --------------------------------------------------------------------------
# Exterior views per variant
# --------------------------------------------------------------------------

def _exterior(project: str, variant: str) -> tuple[list, list, set]:
    """``(exterior cameras, dropped cameras, rendered camera names)`` of a variant's own scene."""
    folder = _variant_dir(project, variant)
    scene = _load(project, f"{folder}scene/scene_manifest.json")
    if scene is None:
        return [], [], set()
    cams = [c for c in scene["cameras"] if c.get("kind") == "exterior"]
    render = _load(project, f"{folder}renders/render_manifest.json") or {"renders": []}
    done = {r["camera"] for r in render["renders"]
            if r.get("png") and (OUTPUTS / project / f"{folder}renders" / r["png"]).is_file()}
    return cams, list(scene.get("cameras_dropped") or []), done


def test_every_variant_has_at_least_five_exterior_views_or_lists_the_base_views(project, building):
    if not VW.views_for(building, "base")["exterior"]:
        pytest.skip(f"{project}: render.exterior_views is false")
    problems = []
    for v in building["variants"]:
        info = VW.views_for(building, v["id"])
        cams, dropped, done = _exterior(project, v["id"])
        rendered = [c for c in cams if c["name"] in done]
        print(f"{project} {v['id']}: {len(rendered)} exterior view(s) rendered, {len(dropped)} dropped; "
              f"exterior {info['exterior']} (from {info['exterior_from']})")
        if info["exterior"] and info["exterior_from"] in ("base", v["id"]) and (v["base"] or v["exterior_changed"]):
            if len(rendered) < MIN_EXTERIOR_VIEWS:
                problems.append(f"{v['id']}: {len(rendered)} exterior views rendered (< {MIN_EXTERIOR_VIEWS})")
            corners = [c for c in cams if c["view"] == "corner"] + [d for d in dropped if d["view"] == "corner"]
            if len(corners) != 4:
                problems.append(f"{v['id']}: {len(corners)} corner views rendered or dropped (4 expected)")
            if not [c for c in cams + dropped if c["view"] == "aerial"]:
                problems.append(f"{v['id']}: no aerial view rendered or dropped")
        else:
            assert info["exterior_from"] == "base" or not info["exterior"], (v["id"], info)
            base_cams, _, base_done = _exterior(project, "base")
            if len([c for c in base_cams if c["name"] in base_done]) < MIN_EXTERIOR_VIEWS:
                problems.append(f"{v['id']}: its outside is the base's, which has fewer than {MIN_EXTERIOR_VIEWS} views")
        for d in dropped:
            assert d.get("dropped_reason"), f"{v['id']}: dropped view {d.get('name')} has no reason"
    assert not problems, f"{project}: " + "; ".join(problems)


def test_every_exterior_view_has_a_camera_without_a_room_and_its_looks_are_recorded(project):
    scene = _need(project, "scene/scene_manifest.json")
    cams = [c for c in scene["cameras"] if c.get("kind") == "exterior"]
    assert cams, f"{project}: no exterior camera"
    for c in cams:
        assert c["room_id"] is None and c["level_id"] is None and c["view"] in ("corner", "aerial", "elevation"), c
        assert c["name"].startswith("ext_") and c["sides"], c
    looks = scene["exterior_looks"]
    for slot in ("facade", "roof", "window_frame", "door", "paving", "garden"):
        assert looks[slot]["material"] and looks[slot]["source"] in (
            "documents", "brief", "style", "fallback", "build"), (slot, looks[slot])
        assert looks[slot]["assumed"] == (looks[slot]["source"] in ("fallback", "build")), (slot, looks[slot])


def test_exterior_views_are_checked_with_the_roof_and_the_elevation_check(project, building):
    check = _load(project, "check/check_manifest.json")
    if check is None:
        pytest.skip(f"{project}: the vision check did not run")
    cams, _, done = _exterior(project, "base")
    for c in cams:
        if c["name"] not in done:
            continue
        entry = check["views"].get(c["name"])
        assert entry is not None and entry["view_kind"] == "exterior", f"{project}: {c['name']} not in the check"
        assert entry["room_id"] is None and "roof" in entry["exterior"], c["name"]
        assert entry["exterior"]["roof"]["result"] in ("ok", "partial", "missing", "not_in_view", "not_checked")
    elev = check.get("elevation_check")
    assert isinstance(elev, dict) and elev["kind"] == "elevation_check", f"{project}: no elevation check"
    assert set(elev["summary"]) >= {"facades", "ok", "mismatch", "not_checked", "roof"} and "roof" in elev
    drawn = len((building.get("facade") or {}).get("elevations") or [])
    if drawn:
        assert elev["summary"]["facades"] == drawn, (elev["summary"], drawn)
    if project in ELEVATION_STRICT:
        assert elev["summary"]["mismatch"] == 0 and elev["roof"]["result"] != "mismatch", elev
    assert isinstance(check.get("drawn_check"), dict) and check["drawn_check"]["kind"] == "drawn_check"
    print(f"{project}: elevation check {elev['summary']}")


def test_the_exterior_polish_follows_the_per_kind_gate_decision(project):
    cams, _, done = _exterior(project, "base")
    rendered = [c["name"] for c in cams if c["name"] in done]
    polish = _load(project, "polish/polish_manifest.json")
    if not rendered or polish is None:
        pytest.skip(f"{project}: no exterior view or no polish run")
    if polish.get("polish_allowed") is False:
        pytest.skip(f"{project}: brief polish is false: every view is Cycles by the brief")
    from wenart.gate.calibrate import exterior_polish

    decision = exterior_polish(OUTPUTS / project)
    recorded = polish.get("exterior_gate")
    assert recorded is not None, f"{project}: the polish manifest has no exterior_gate record"
    assert recorded["polish_allowed"] == bool(decision["polish_allowed"]), (recorded, decision)
    cal = _load(project, "gate/gate_calibration.json")
    assert cal is not None and cal["exterior"]["cameras_rendered"] == len(rendered), \
        f"{project}: the gate calibration saw {(cal or {}).get('exterior')} for {len(rendered)} exterior views"
    views = {v["camera"]: v for v in polish["views"]}
    for name in rendered:
        v = views[name]
        assert v["view_kind"] == "exterior" and v["room_id"] is None
        if not decision["polish_allowed"]:
            assert (v["final"], v["reason"], v["attempts"]) == ("cycles", "gate", []), (name, v["final"], v["reason"])
    rooms = [v for v in polish["views"] if v["view_kind"] == "interior"]
    assert rooms, f"{project}: no room view in the polish manifest"
    print(f"{project}: exterior gate {decision['decision']} (polish {'allowed' if decision['polish_allowed'] else 'off'})")


# --------------------------------------------------------------------------
# The final report
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def final(project):
    manifest = _need(project, "final/final_manifest.json")
    report = (OUTPUTS / project / "final" / "final_report.md").read_text(encoding="utf-8")
    return manifest, report


def test_the_final_report_has_the_milestone_10_sections(project, building, final):
    manifest, report = final
    assert manifest["status"] == "ok", f"{project}: final status {manifest['status']}"
    wanted = ["## Building", "## Exterior views"]
    if _load(project, "sheets.json") is not None:
        wanted.append("## Sheets")
    if len(building["variants"]) > 1:
        wanted.append("## Variants")
    if _load(project, "completion.json") is not None:
        wanted.append("## AI completion of furnished rooms (Feature 1)")
    missing = [w for w in wanted if w not in report]
    assert not missing, f"{project}: final_report.md lacks {missing}"
    links = re.findall(r"\[[^\]]*\]\(([^)\s]+)\)", report)
    broken = [l for l in links if not l.startswith("http") and not (OUTPUTS / project / "final" / l).is_file()]
    assert not broken, f"{project}: report links to missing files {broken[:5]}"


def test_the_exterior_views_of_every_variant_have_a_contact_sheet_or_list_the_base(project, building, final):
    manifest, report = final
    own = {v["camera"] for v in manifest["views"] if v.get("view_kind") == "exterior"}
    assert own, f"{project}: the final manifest holds no exterior view"
    assert "base" in manifest["exterior_sheets"] and (OUTPUTS / project / "final" /
                                                      manifest["exterior_sheets"]["base"]).is_file()
    rows = {v["id"]: v for v in (manifest.get("variants") or {}).get("variants") or []}
    for v in building["variants"]:
        if v["base"]:
            continue
        row = rows[v["id"]]
        if v["exterior_changed"]:
            assert row["exterior_views"], f"{project}: {v['id']} changed its outside but reported no exterior view"
            assert manifest["variant_sheets"][v["id"]].get("exterior"), v["id"]
        else:
            assert row["exterior"].startswith("unchanged: the base views"), row["exterior"]
        assert row["reported"], f"{project}: variants/{v['id']}/final/final_manifest.json missing or unreadable"
        assert row["interior_views"], f"{project}: {v['id']} reports no interior view"


def test_the_report_lists_the_ai_changes_of_furnished_rooms(project, building, final):
    manifest, report = final
    completion = _load(project, "completion.json")
    if completion is None:
        pytest.skip(f"{project}: no completion.json")
    block = manifest["completion"]
    assert block is not None and {r["room_id"] for r in block["rooms"]} == {r["room_id"] for r in completion["rooms"]}
    listed = {c["id"]: c for r in block["rooms"] for c in r["changes"]}
    for f in building["furniture"]:
        if f.get("modified_by_ai"):
            c = listed.get(f["id"])
            assert c is not None and c["drawn_type"] == f["drawn_type"], f"{project}: {f['id']} not listed in the report"
            assert f"changed {f['id']}: {f['drawn_type']}" in report, f["id"]
    added = {a["id"] for r in block["rooms"] for a in r["added"]}
    assert {f["id"] for f in building["furniture"] if f.get("completes_room")} <= added | {
        f["id"] for f in building["furniture"] if f.get("mirrored_from")}, f"{project}: added pieces not listed"
    drawn = manifest["drawn_check"]
    assert drawn is not None and drawn["failed"] == [] and drawn["violations"] == [], \
        f"{project}: drawn pieces moved beyond the tolerance: {drawn and drawn['failed']} {drawn and drawn['violations']}"
    assert drawn["checked"] >= 1 and drawn["reference"] == "source building.json", drawn["reference"]


def test_every_assumed_value_is_listed_in_the_report(project, building, final):
    manifest, report = final
    assumed = manifest["assumed"]
    text = " | ".join(assumed["building"] + assumed["m10"])
    for lv in building["levels"]:
        if lv["ceiling_height_source"] == "assumed_default":
            assert f"{lv['id']}: ceiling height" in text, f"{project}: assumed ceiling height of {lv['id']} not listed"
    for s in building.get("slabs") or []:
        if s["thickness_source"] == "assumed_default":
            assert f"{s['id']} thickness" in text, f"{project}: assumed thickness of {s['id']} not listed"
    roof = building.get("roof") or {}
    for key in ("eaves_height", "ridge_height", "overhang", "thickness", "knee_wall"):
        if isinstance(roof.get(key), dict) and roof[key].get("method") == "assumed":
            assert f"roof {key.replace('_', ' ')}" in text, f"{project}: assumed roof {key} not listed"
    scene = _need(project, "scene/scene_manifest.json")
    for slot, look in scene["exterior_looks"].items():
        if look["assumed"]:
            assert f"outside look {slot}:" in text, f"{project}: assumed outside look {slot} not listed"
    assert "## Assumed values" in report
