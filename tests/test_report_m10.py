"""CPU tests of the Milestone 10 parts of wenart.report (docs/milestone10.md §1.2, §1.6, §3.3 item 6).

A project that stops at the ``sheets`` stage (``wenart.sheets`` exit 1: no readable plan, two plans without a level
title, no unit agreement) has no ``building.json`` and no ``report.md``: only ``sheets.json``,
``sheets_report.md`` and ``sheets_debug/``. The final report still has to say ``needs_review``, list the
reasons of ``sheets.json`` and link ``sheets_report.md``. Later tests of this file cover the new sections of the
final report of a rendered project (Sheets, Building, Feature 1, exterior contact sheets, Variants).
"""
import json
from pathlib import Path

import numpy as np

from test_report import links, make_project, stage_record, write_json
from wenart import views as VW
from wenart.report import final as F
from wenart.report.__main__ import main as report_main

STARTED = "2026-10-08T10:00:00Z"
UNTITLED = "review01.dxf r2: plan without a level title; 2 untitled plans, 0 free level slot(s)"


def region(rid, cls="floor_plan", use="read", level=None, method="geometry", title=None, **extra):
    return {"id": rid, "file": "review01.dxf", "sheet": "s1", "box": [0, 0, 100, 100], "box_m": [10.0, 10.0],
            "entities": 100, "frame": None, "class": cls, "class_method": method, "class_confidence": 0.8,
            "status": "verified", "title": title, "features": {}, "level": level, "variant_group": None,
            "variant": None, "variant_slug": None, "ai": [], "transform_to_building": None, "registration": None,
            "use": use, "ignored_reason": extra.pop("ignored_reason", None), "evidence": [], "conflicts": [],
            **extra}


def sheets_doc(needs_review=(UNTITLED,), project="review-01") -> dict:
    return {"schema_version": "0.1", "kind": "sheets", "project": project, "created_utc": "2026-10-08T09:59:00Z",
            "code_commit": "abc",
            "documents": [{"file": "review01.dxf", "format": "dxf", "converter": None,
                           "units": {"insunits": 4, "metres_per_unit": 0.01, "method": "unit_check", "checks": [],
                                     "conflict": "$INSUNITS = 4 (mm) but the room labels agree on cm"},
                           "sheets": [{"id": "s1", "space": "model", "box": [0, 0, 300, 100], "frames": [],
                                       "debug_image": "sheets_debug/review01_dxf_s1.png"}]}],
            "regions": [region("r1", level=None, ignored_reason="plan without a level title (its level cannot be told)",
                               use="ignored"),
                        region("r2", use="ignored", ignored_reason="plan without a level title (its level cannot be "
                                                                   "told)")],
            "stray": [{"file": "review01.dxf", "sheet": "s1", "entity": "HATCH:6633", "type": "HATCH", "layer": "X",
                       "box": [0, 0, 1, 1], "distance_m": 230.0, "reason": "far outside every drawing"}],
            "levels": [], "variants": [], "heights": {"levels": [], "slabs": [], "ground": [], "roof": {}},
            "exterior": {}, "conflicts": [], "warnings": ["review01.dxf: 2 plans without a level title"],
            "needs_review": [{"region": "r2", "file": "review01.dxf", "reason": r} for r in needs_review],
            "questions": 0, "answers": None}


def make_sheets_project(tmp_path, name="review-01x", doc=None, record=True) -> Path:
    out = tmp_path / "outputs" / name
    write_json(out / "sheets.json", doc or sheets_doc())
    (out / "sheets_report.md").write_text("# Sheet analysis: review-01\n\nStatus: **needs review**\n", encoding="utf-8")
    VW.write_png_rgb(out / "sheets_debug" / "review01_dxf_s1.png", np.full((60, 80, 3), 200, dtype=np.uint8))
    if record:
        stage_record(out, "sheets", "needs_review", STARTED, note="exit 1: needs review")
    return out


def test_a_project_that_stopped_at_the_sheets_stage_gets_a_needs_review_report(tmp_path, capsys):
    out = make_sheets_project(tmp_path)
    assert not (out / "building.json").exists() and not (out / "report.md").exists()
    assert report_main(["final", "--project-out", str(out)]) == 0
    assert "needs_review (1 reason(s))" in capsys.readouterr().out
    final = out / "final"
    m = json.loads((final / "final_manifest.json").read_text(encoding="utf-8"))
    assert F.validate_final_manifest(m) == []
    assert m["status"] == "needs_review" and m["private"] is False and m["views"] == []
    assert m["reasons"] == [f"sheets: {UNTITLED}"]
    assert m["hints"] == ["add the level title (e.g. ZEMİN KAT PLANI) to the floor plan"]
    assert m["building"] is None and m["documents"] == []
    sheets = m["sheets"]
    assert [(r["id"], r["class"], r["use"]) for r in sheets["regions"]] == [("r1", "floor_plan", "ignored"),
                                                                           ("r2", "floor_plan", "ignored")]
    assert sheets["strays"] == 1 and sheets["report"] == "sheets_report.md"
    assert sheets["units"][0]["conflict"].startswith("$INSUNITS = 4")
    assert sheets["debug_images"] == [{"source": "sheets_debug/review01_dxf_s1.png",
                                       "preview": "debug/review01_dxf_s1.jpg"}]
    assert (final / "debug" / "review01_dxf_s1.jpg").stat().st_size <= 300_000
    assert (final / "sheets_report.md").read_text(encoding="utf-8") == (out / "sheets_report.md").read_text(
        encoding="utf-8")
    md = (final / "final_report.md").read_text(encoding="utf-8")
    for text in ("# Final report: review-01 (needs review)", "## Reasons", f"- sheets: {UNTITLED}", "## What to do",
                 "## Sheets", "[sheets_report.md](sheets_report.md)", "| r2 | review01.dxf | floor_plan |",
                 "Strays (entities far from every drawing, ignored): 1.", "$INSUNITS = 4",
                 "[debug/review01_dxf_s1.jpg](debug/review01_dxf_s1.jpg)",
                 "The project stopped at the sheets stage", "| sheets | needs_review | 1.0 s | exit 1: needs review |"):
        assert text in md, text
    assert links(md) and all((final / link).is_file() for link in links(md))


def test_sheets_stop_without_stage_records_and_without_listed_reasons(tmp_path):
    # A hand run: no run/*.json, no building.json, reasons in sheets.json.
    out = make_sheets_project(tmp_path, record=False)
    assert F.write_final(out)["reasons"] == [f"sheets: {UNTITLED}"]
    # The stage record says needs_review but sheets.json lists nothing (e.g. no readable plan region is a reason
    # of the pipeline's own wording): the record's note is the reason.
    out2 = make_sheets_project(tmp_path / "2", doc=sheets_doc(needs_review=()))
    assert F.write_final(out2)["reasons"] == ["sheets: exit 1: needs review"]
    # No sheets.json at all: the generic stage-record reason (the sheets stage crashed before writing it).
    out3 = tmp_path / "3" / "outputs" / "toy"
    stage_record(out3, "sheets", "needs_review", STARTED, note="exit 1, nothing written")
    m = F.write_final(out3)
    assert m["reasons"] == ["sheets: exit 1, nothing written"] and m["sheets"] is None


def test_a_building_from_an_earlier_run_is_ignored_when_the_sheets_stage_stopped(tmp_path):
    out = make_sheets_project(tmp_path)
    write_json(out / "building.json", {"schema_version": "0.1", "status": "ok", "project": {"id": "old"},
                                       "documents": [], "levels": [], "walls": [], "openings": [], "rooms": [],
                                       "furniture": [], "conflicts": [], "unverified": [], "warnings": []})
    m = F.write_final(out)
    assert m["status"] == "needs_review" and m["building"] is None
    assert any("building.json is from an earlier run (the sheets stage stopped" in w for w in m["warnings"])


def test_sheets_reasons_next_to_a_building_of_this_run_are_not_a_stop(tmp_path):
    # failed_levels: leave_out lists a level in sheets.json needs_review and the project goes on (status ok).
    out = make_project(tmp_path)
    write_json(out / "sheets.json", sheets_doc())
    write_json(out / "building.json", {"status": "ok"})
    stage_record(out, "sheets", "ok", STARTED)
    assert F.review_inputs(out) is None
    assert F.write_final(out)["status"] == "ok"


def test_a_private_project_stopped_at_the_sheets_stage_names_but_never_copies_its_images(tmp_path):
    out = make_sheets_project(tmp_path, name="real-03", doc=sheets_doc(project="real-03"))
    write_json(out / "intake_manifest.json", {"kind": "intake_manifest", "alias": "real-03", "status": "ok",
                                              "reasons": [], "totals": {"kept": 1, "documents": 1}})
    m = F.write_final(out)
    final = out / "final"
    assert m["private"] is True and not (final / "debug").exists() and not (final / "sheets_report.md").exists()
    assert m["sheets"]["report"] is None and m["sheets"]["report_kept_on_volume"] == "sheets_report.md"
    assert m["sheets"]["regions"][0]["file"] == "document 1" and m["sheets"]["regions"][0]["title"] is None
    assert [(i["source"], i["preview"]) for i in m["debug_images"]] == [("sheets_debug/review01_dxf_s1.png", None)]
    md = (final / "final_report.md").read_text(encoding="utf-8")
    assert "sheets_debug/review01_dxf_s1.png (on the volume, not copied)" in md and not links(md)
    assert "`sheets_report.md` (a private project" in md


def test_the_hints_of_the_sheets_stop_reasons():
    assert F.review_hints(["sheets: no readable plan region"]) == [
        "add a floor plan the sheets stage can read: a DXF/DWG or vector PDF with closed walls and room labels, or "
        "a sharp scan"]
    assert F.review_hints(["sheets: a.dxf r1: plan without a drawing unit (missing scale)"]) == [
        "set the drawing unit of the CAD file (or add a scale note such as ÖLÇEK 1/50 to the plan)"]


def test_a_variant_output_of_a_private_project_is_private(tmp_path):
    base = tmp_path / "outputs" / "real-04"
    write_json(base / "intake_manifest.json", {"kind": "intake_manifest", "alias": "real-04", "status": "ok"})
    variant = base / "variants" / "l-1b-acik-mutfak"
    variant.mkdir(parents=True)
    assert F.is_private(variant) is True
    assert F.is_private(tmp_path / "outputs" / "synthetic-07" / "variants" / "l-1b") is False
