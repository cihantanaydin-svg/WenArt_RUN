"""CPU tests of the Milestone 10 sections of the final report of a rendered project (docs/milestone10.md §3.3 item
6): Sheets, Building, Feature 1 per room, exterior views and their contact sheet per variant, Variants, the
assumed values and the gate that holds the exterior views back.

What: the toy project of ``test_report`` plus the data a whole-building run adds (levels with variants, slabs, a
roof, a facade, a site, ``completion.json``, ``sheets.json``, two exterior cameras with their looks, an
alternative's own ``final_manifest.json``), and the pure helpers of ``wenart.report.m10``.

Why: the report is what the user reads; every assumed value must be listed, nothing that was changed or added by
the AI may read as a document conflict, and a failed exterior validation must show as Cycles with its reason.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

from test_report import W, H, check_entry, element, links, make_project, render_entry, write_json
from test_report_m10 import region, sheets_doc
from wenart import views as VW
from wenart.report import final as F
from wenart.report import m10 as M

EXT = [("ext_1", "corner", ["S", "E"]), ("ext_2", "aerial", ["S", "W"])]
ALT = "l0b-acik-mutfak"
GATE = {"decision": "polish_disabled", "polish_allowed": False,
        "reasons": ["too many exterior geometry changes get through (0.40 < 0.80)"],
        "benign_accept": 0.9, "negative_reject": 0.4, "n_benign": 6, "n_negative": 9,
        "limits": {"benign_accept_min": 0.8, "negative_reject_min": 0.8}}
LOOKS = {"facade": {"material": "render", "colour": "greige", "source": "fallback", "assumed": True,
                    "reason": "style.exterior_fallback: render in greige"},
         "roof": {"material": "concrete_tiles", "colour": "anthracite", "source": "fallback", "assumed": True,
                  "reason": "style.exterior_fallback: concrete_tiles in anthracite"},
         "window_frame": {"material": "dark_bronze", "colour": "dark bronze", "source": "brief", "assumed": False,
                          "reason": "brief exterior.window_frame"}}


def value(v, method="vector"):
    return {"value": v, "method": method, "confidence": 1.0 if method != "assumed" else 0.0, "evidence": []}


def whole_building(b: dict) -> dict:
    """Add the Milestone 10 fields to the toy building."""
    b["levels"] = [
        {"id": "L0", "label": "Zemin", "kind": "floor", "order": 0, "elevation": 0.0, "elevation_source": "section",
         "ceiling_height": 2.7, "ceiling_height_source": "assumed_default", "variant": "base", "region_id": "r2"},
        {"id": "L1", "label": "1. Kat", "kind": "floor", "order": 1, "elevation": 2.9,
         "elevation_source": "section", "ceiling_height": 2.6, "ceiling_height_source": "section",
         "variant": "base", "region_id": "r4"}]
    b["variants"] = [
        {"id": "base", "label": "Base", "levels": ["L0", "L1"], "base": True, "changes": [], "rooms_changed": [],
         "exterior_changed": False},
        {"id": ALT, "label": "Zemin: Açık mutfak", "levels": ["L0b", "L1"], "base": False,
         "changes": [{"variant_group": "vg_L0", "level_id": "L0b", "replaces": "L0"}],
         "rooms_changed": ["r_L0_salon"], "exterior_changed": False}]
    b["slabs"] = [{"id": "sl_L1", "below_level_id": "L0", "above_level_id": "L1", "z_top": 2.9, "thickness": 0.2,
                   "thickness_source": "assumed_default", "outline": [[0, 0], [5, 0], [5, 5]], "openings": [],
                   "variants": [], "status": "assumed", "evidence": []}]
    b["roof"] = {"type": "gable", "type_source": "section", "over_level_id": "L1",
                 "eaves_height": value(5.5), "ridge_height": value(6.9), "pitches_deg": [value(30.0)],
                 "overhang": value(0.5), "thickness": dict(value(0.25, "assumed"), note="not drawn"),
                 "knee_wall": value(1.0), "planes": [{"id": "p1"}, {"id": "p2"}], "openings": [], "covering": None,
                 "assumed": ["roof thickness"], "status": "verified", "evidence": []}
    b["facade"] = {"faces": [], "elevations": [{"region_id": "r8", "title": "GÜNEY GÖRÜNÜŞÜ", "side": "S",
                                                "windows": 3, "doors": 1, "plan_check": None}], "evidence": []}
    b["site"] = {"boundary_walls": [], "areas": [{"id": "a_1", "label": "BAHÇE", "kind": "garden", "polygon": None,
                                                  "build": False}],
                 "decor": [], "openings": [], "ground": {"levels": [], "terrain": "flat", "light_wells": []},
                 "north_deg": value(0.0, "assumed"), "plot": {"id": "plot", "polygon": [[0, 0], [9, 0], [9, 9]]},
                 "paving": [{"id": "pv_1", "build": True}], "grass": [], "parking": []}
    b["levels_left_out"] = [{"label": "Çatı", "order": 2, "region_id": "r9", "variant": None,
                             "reason": "no scale"}]
    sofa = next(f for f in b["furniture"] if f["id"] == "f_1")
    sofa.update(modified_by_ai=True, drawn_type="armchair")
    return b


def completion_doc() -> dict:
    return {"kind": "completion", "project": "toy", "server": "http://x", "model": "Qwen/Qwen3-VL-8B-Instruct",
            "settings": {"mode": "complete", "keep_size": False, "twin_rooms": "both", "assumed": ["furnished_rooms"]},
            "rooms": [{"room_id": "r_L0_salon", "label": "Salon", "room_type": "living", "state": "completed",
                       "reason": "", "drawn": [{"id": "f_1", "type": "armchair"}, {"id": "f_9", "type": "unknown"}],
                       "changes": [{"id": "f_1", "drawn_type": "armchair", "drawn_size": [0.8, 0.8], "type": "sofa",
                                    "size": [2.0, 0.9], "status": "applied", "look_only": False, "shrunk": False,
                                    "type_proposal": False},
                                   {"id": "f_9", "drawn_type": "unknown", "drawn_size": [1.0, 0.5], "type": "dresser",
                                    "size": [1.0, 0.5], "status": "reverted", "reason": "blocks the door"}],
                       "added": [{"id": "f_2", "type": "tv_unit", "size": [1.5, 0.4], "confidence": 0.9,
                                  "method": "ai"}],
                       "refused": [{"id": "f_1", "type": "wardrobe", "status": "refused",
                                    "reason": "the room's main piece (sofa) may only become another main piece type"},
                                   {"type": "bed_double", "center": [1, 1], "reason": "not a type the AI may add to "
                                                                                       "a living"}],
                       "dropped": [{"pass": 1, "type": "side_table", "center": [2, 2]}],
                       "wall_cabinets": [], "drawn_layout": {"pieces": {"f_9": ["clearance"]}, "walkways": []}},
                      {"room_id": "r_L1_yatak", "label": "Yatak", "room_type": "bedroom", "state": "kept",
                       "reason": "furnished_rooms_keep", "changes": [], "added": [], "refused": [], "dropped": [],
                       "wall_cabinets": [], "drawn_layout": {}}],
            "rooms_completed": 1, "rooms_copied": 0, "changes_applied": 1, "pieces_added": 1, "wall_cabinets": 0,
            "locked_violations": [], "latency_s": 3.0}


def add_exterior(out: Path) -> None:
    """Two exterior cameras: scene, render manifest, PNGs and the check manifest entries."""
    scene_path = out / "scene" / "scene_manifest.json"
    scene = json.loads(scene_path.read_text(encoding="utf-8"))
    for name, view, sides in EXT:
        scene["cameras"].append({"name": name, "kind": "exterior", "room_id": None, "level_id": None, "view": view,
                                 "sides": sides, "variant": "base", "region_id": None, "dropped_reason": None})
    scene["cameras_dropped"] = [{"name": "ext_3", "kind": "exterior", "room_id": None, "level_id": None,
                                 "view": "corner", "sides": ["N", "W"], "variant": "base", "region_id": None,
                                 "dropped_reason": "inside a tree crown after 6 moves"}]
    scene["exterior_looks"] = LOOKS
    scene_path.write_text(json.dumps(scene), encoding="utf-8")
    rm_path = out / "renders" / "render_manifest.json"
    rm = json.loads(rm_path.read_text(encoding="utf-8"))
    for i, (name, _, _) in enumerate(EXT):
        entry = dict(render_entry("cam_salon_1", None, 0), camera=name, png=f"{name}.png",
                     preview=f"{name}_preview.jpg", room_id=None, level_id=None)
        rm["renders"].append(entry)
        rgb = np.full((H, W, 3), 90 + 40 * i, dtype=np.uint8)
        VW.write_png_rgb(out / "renders" / f"{name}.png", rgb)
        Image.fromarray(rgb).save(out / "renders" / f"{name}_preview.jpg", quality=80)
    rm_path.write_text(json.dumps(rm), encoding="utf-8")
    cm_path = out / "check" / "check_manifest.json"
    cm = json.loads(cm_path.read_text(encoding="utf-8"))
    for name, view, sides in EXT:
        ok = check_entry({"win_1": element("Window", "required", "window", "window", "from_documents", "ok")})
        ok["image_sha256"] = ["x"]
        cm["views"][name] = {
            "cycles": ok, "room_id": None, "json_crosscheck": {"in_json_not_rendered": [], "rendered_not_in_json": [],
                                                              "misplaced": [], "roof_not_rendered": []},
            "polished_rejected": False, "needs_review": False, "needs_review_reasons": [], "view_kind": "exterior",
            "exterior": {"variant": "base", "view": view, "sides": sides, "region_id": None,
                         "roof": {"result": "ok" if name == "ext_1" else "missing", "note": None},
                         "planned_not_seen": [], "seen_not_planned": [], "outer_openings": 4},
            "facades": {"S": {"side": "S", "advisory": True, "result": "ok", "windows": "ok", "doors": "ok",
                              "expected": {"windows": [3, 3], "doors": [1, 1]}}}}
    cm["drawn_check"] = {"kind": "drawn_check", "reference": "source building.json", "mode": "complete",
                         "tolerance_m": 0.05, "tolerance_deg": 1.0,
                         "pieces": [{"id": "f_1", "type": "sofa", "drawn_type": "armchair", "modified_by_ai": True,
                                     "anchor_distance_m": 0.12, "front_turn_deg": 0.0, "same_wall": None,
                                     "checked": True, "ok": False, "notes": [], "type_proposal": False}],
                         "checked": 1, "ok": 0, "failed": ["f_1"], "modified": ["f_1"], "proposals": [],
                         "violations": [], "notes": []}
    cm["elevation_check"] = {"kind": "elevation_check", "variant": "base", "source": "building.json facade.elevations",
                             "north": 0.0, "north_source": "assumed",
                             "facades": [{"region_id": "r8", "title": "GÜNEY GÖRÜNÜŞÜ", "side": "S",
                                          "drawn": {"windows": 3, "doors": 1, "positions": 4}, "result": "mismatch",
                                          "building": {"windows": 2, "doors": 1, "openings": []},
                                          "counts": {"windows": "fewer", "doors": "ok"},
                                          "notes": ["the building has 1 window less than the elevation draws"]}],
                             "roof": {"built": {"eaves": 5.5, "ridge": 7.1}, "drawn": {"ridge": {"value": 6.9,
                                                                                                   "method": "vector"}},
                                      "deltas": {"ridge": 0.2}, "result": "mismatch", "notes": []},
                             "summary": {"facades": 1, "ok": 0, "mismatch": 1, "not_checked": 0, "roof": "mismatch"},
                             "warnings": []}
    cm_path.write_text(json.dumps(cm), encoding="utf-8")


def whole_project(tmp_path, monkeypatch, gate=GATE) -> Path:
    out = make_project(tmp_path)
    bpath = out / "building_final.json"
    bpath.write_text(json.dumps(whole_building(json.loads(bpath.read_text(encoding="utf-8")))), encoding="utf-8")
    write_json(out / "completion.json", completion_doc())
    doc = sheets_doc(needs_review=())
    doc["regions"] = [region("r2", level={"id": "L0", "method": "title", "label": "Zemin"}, title={"text": "ZEMIN KAT"}),
                      region("r3", cls="alternative_floor_plan", variant="Açık mutfak",
                             level={"id": "L0b", "method": "title"}, title={"text": "ZEMIN KAT (AÇIK MUTFAK)"})]
    doc["levels"] = [{"id": "L0", "order": 0, "label": "Zemin", "kind": "floor", "base_region": "r2",
                      "alternatives": [{"region": "r3", "variant": "Açık mutfak", "slug": "acik-mutfak",
                                        "level_id": "L0b", "base_unclear": False}]}]
    doc["variants"] = [{"id": "base", "label": "Base", "base": True, "levels": ["L0", "L1"], "regions": ["r2"]},
                       {"id": ALT, "label": "Zemin: Açık mutfak", "base": False, "levels": ["L0b", "L1"],
                        "regions": ["r3"]}]
    write_json(out / "sheets.json", doc)
    (out / "sheets_report.md").write_text("# Sheet analysis\n", encoding="utf-8")
    VW.write_png_rgb(out / "sheets_debug" / "review01_dxf_s1.png", np.full((60, 80, 3), 200, dtype=np.uint8))
    add_exterior(out)
    # The alternative's own report: one interior view of the changed room, no exterior view (its outside is the base).
    alt_final = out / "variants" / ALT / "final"
    alt_final.mkdir(parents=True)
    Image.fromarray(np.full((H, W, 3), 150, dtype=np.uint8)).save(alt_final / "cam_salon_1_final_preview.jpg")
    write_json(alt_final / "final_manifest.json", {
        "kind": "final", "status": "ok", "project": "toy", "variant": ALT,
        "views": [{"camera": "cam_salon_1", "view_kind": "interior", "preview": "cam_salon_1_final_preview.jpg",
                   "final": "polished", "unverified": [], "final_mismatches": 0, "needs_review": False}]})
    monkeypatch.setattr("wenart.gate.calibrate.exterior_polish", lambda project_out, *a, **k: dict(gate))
    return out


# --------------------------------------------------------------------------
# The decision
# --------------------------------------------------------------------------

POLISHED = {"final": "polished", "final_attempt": 2, "reason": None, "source_sha256": "s",
            "attempts": [{"k": 2, "png": "ext_1_a2.png", "sha256": "p"}]}


def test_decide_holds_an_exterior_view_back_when_the_exterior_gate_does_not_allow_the_polish():
    args = {"polish_ran": True, "check_ran": True, "allowed": True, "source_sha256": "s"}
    out = F.decide(POLISHED, None, **args, gate_decision="ok", exterior_gate=GATE)
    assert (out["final"], out["reason"]) == ("cycles", "gate_validation")
    assert "exterior gate validation polish_disabled" in out["detail"] and "0.40 < 0.80" in out["detail"]
    # An allowing exterior decision, and a room view (no exterior decision), go on to the checks.
    ok = dict(GATE, decision="ok", polish_allowed=True)
    assert F.decide(POLISHED, None, **args, exterior_gate=ok)["reason"] == "check_incomplete"
    assert F.decide(POLISHED, None, **args, exterior_gate=None)["reason"] == "check_incomplete"
    # The brief and the rooms' decision come first.
    assert F.decide(POLISHED, None, **dict(args, allowed=False), exterior_gate=GATE)["reason"] == "brief"
    assert F.decide(POLISHED, None, **args, gate_decision="polish_disabled", exterior_gate=ok)["reason"] == "gate_validation"


# --------------------------------------------------------------------------
# The report of a whole building
# --------------------------------------------------------------------------

def test_the_final_report_of_a_whole_building_project(tmp_path, monkeypatch):
    out = whole_project(tmp_path, monkeypatch)
    m = F.write_final(out)
    assert F.validate_final_manifest(m) == []
    assert not [w for w in m["warnings"] if "schema" in w], m["warnings"]
    final = out / "final"
    views = {v["camera"]: v for v in m["views"]}
    assert m["summary"]["interior_views"] == 5 and m["summary"]["exterior_views"] == 2
    for cam in ("ext_1", "ext_2"):
        assert views[cam]["view_kind"] == "exterior" and views[cam]["room_id"] is None
        assert (views[cam]["final"], views[cam]["reason"]) == ("cycles", "gate_validation")
    assert views["cam_salon_1"]["view_kind"] == "interior" and views["ext_1"]["exterior_view"] == "corner"
    # Contact sheets: the rooms per level as before, the exterior views apart.
    assert m["contact_sheets"] == {"L0": "contact_L0.jpg", "L1": "contact_L1.jpg"}
    assert m["exterior_sheets"] == {"base": "contact_exterior_base.jpg"}
    assert m["variant_sheets"] == {ALT: {"interior": f"contact_variant_{ALT}.jpg"}}
    for name in ("contact_exterior_base.jpg", f"contact_variant_{ALT}.jpg", "contact_L0.jpg"):
        assert (final / name).is_file() and (final / name).stat().st_size <= 300_000
    # The sections.
    md = (final / "final_report.md").read_text(encoding="utf-8")
    for text in ("## Sheets", "## Building", "## AI completion of furnished rooms (Feature 1)",
                 "### Drawn pieces against the source plan", "## Exterior views", "## Variants",
                 "### Exterior views", "Exterior decision: **polish_disabled**",
                 "[contact_exterior_base.jpg](contact_exterior_base.jpg)",
                 f"[contact_variant_{ALT}.jpg](contact_variant_{ALT}.jpg)",
                 "Alternatives with an unchanged outside (l0b-acik-mutfak) use the base views above: ext_1, ext_2.",
                 f"unchanged: the base views (ext_1, ext_2)", "inside a tree crown after 6 moves",
                 "[sheets_report.md](sheets_report.md)", "[debug/review01_dxf_s1.jpg](debug/review01_dxf_s1.jpg)"):
        assert text in md, text
    assert links(md) and all((final / link).is_file() for link in links(md))
    assert (final / "sheets_report.md").is_file()
    # Feature 1 per room.
    for text in ("changed f_1: armchair 0.80 x 0.80 -> sofa 2.00 x 0.90 (changed)",
                 "added f_2: tv_unit 1.50 x 0.40 (confidence 0.90, ai)",
                 "refused f_1 armchair -> wardrobe: the room's main piece (sofa) may only become another main piece type",
                 "refused f_9 unknown -> dresser: blocks the door",
                 "refused to add bed_double: not a type the AI may add to a living", "not placed side_table",
                 "drawn pieces that already fail a placer check as drawn (kept, never moved): f_9",
                 "### Yatak (r_L1_yatak, bedroom): kept (furnished_rooms_keep)"):
        assert text in md, text
    assert m["completion"]["changes_applied"] == 1 and m["drawn_check"]["failed"] == ["f_1"]
    # The elevation check, the roof and the facade counts.
    assert m["exterior"]["elevation"]["summary"]["mismatch"] == 1
    assert [v["roof"] for v in m["exterior"]["views"]] == ["ok", "missing"]
    assert m["exterior"]["views"][0]["facades"] == {"S": {"result": "ok", "windows": "ok", "doors": "ok"}}
    flags = " | ".join(m["advisory_flags"])
    for text in ("1 level(s) left out of the building: Çatı (no scale)",
                 "1 exterior view(s) dropped, no camera place worked: ext_3",
                 "exterior gate polish_disabled", "elevation check: 1 facade(s) differ",
                 "the roof of the building JSON is not in the render: ext_2",
                 "drawn-piece check: 1 piece(s) moved beyond the tolerance",
                 "AI completion: 4 proposal(s) refused, reverted or not placed"):
        assert text in flags, text
    # The variants table reads the alternative's own manifest.
    rows = {v["id"]: v for v in m["variants"]["variants"]}
    assert rows["base"]["exterior"] == "its own views (this report)" and rows[ALT]["reported"]
    assert rows[ALT]["interior_views"] == ["cam_salon_1"] and rows[ALT]["polished"] == 1
    assert rows[ALT]["report"] == f"variants/{ALT}/final/final_report.md"
    assert rows["base"]["exterior_views"] == ["ext_1", "ext_2"]


def test_the_building_section_lists_every_height_as_drawn_or_assumed(tmp_path, monkeypatch):
    out = whole_project(tmp_path, monkeypatch)
    m = F.write_final(out)
    heights = {h["item"]: h for h in m["building_detail"]["heights"]}
    assert heights["L0 ceiling height"]["state"] == "assumed" and heights["L1 ceiling height"]["state"] == "drawn"
    assert heights["sl_L1 thickness"]["state"] == "assumed" and heights["roof eaves height"]["state"] == "drawn"
    assert heights["roof thickness"]["state"] == "assumed" and heights["north direction (deg)"]["state"] == "assumed"
    md = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    assert "| roof ridge height | 6,90 m | drawn | vector |" in md
    assert "| roof thickness | 0,25 m | assumed | assumed | not drawn |" in md
    # Every assumed value is listed again under "Assumed values", once.
    assumed = md.split("## Assumed values")[1].split("\n## ")[0]
    for text in ("L0: ceiling height 2,70 m (assumed_default)", "sl_L1 thickness: 0,20 m (assumed_default)",
                 "roof thickness: 0,25 m (assumed; not drawn)", "north direction (deg): 0 deg (assumed)",
                 "roof: roof thickness assumed", "site ground: flat at 0.00 m (no ground level drawn)",
                 "outside look facade: render in greige (fallback: style.exterior_fallback: render in greige)",
                 "outside look roof: concrete_tiles in anthracite"):
        assert text in assumed, text
    assert "outside look window_frame" not in assumed         # the brief gave it: not assumed
    assert assumed.count("ceiling height") == 1
    assert "Levels left out" in md and "no scale" in md


def test_a_modified_piece_is_noted_next_to_its_mismatch_and_site_text_names_what_is_built(tmp_path, monkeypatch):
    out = whole_project(tmp_path, monkeypatch)
    cm_path = out / "check" / "check_manifest.json"
    cm = json.loads(cm_path.read_text(encoding="utf-8"))
    cm["views"]["cam_salon_1"]["cycles"]["elements"]["f_1"]["result"] = "missing"
    cm_path.write_text(json.dumps(cm), encoding="utf-8")
    m = F.write_final(out)
    item = next(i for i in m["views"][0]["mismatches"] if i.get("id") == "f_1")
    assert "modified_by_ai (drawn armchair): render/polish issue, not a document conflict" in item["notes"]
    assert item["modified_by_ai"] is True
    md = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    assert "an area that is only a label (not built) is recorded, not built" in md
    assert "recorded only (not built)" in md
    assert "No furniture was moved" not in md


def test_a_project_without_m10_data_keeps_its_report(tmp_path):
    out = make_project(tmp_path)
    m = F.write_final(out)
    assert m["sheets"] is None and m["building_detail"] is None and m["completion"] is None
    assert m["exterior"] is None and m["variants"] is None and m["exterior_sheets"] == {}
    md = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    for title in ("## Sheets", "## Building\n", "## Exterior views", "## Variants", "Feature 1"):
        assert title not in md, title
    assert m["summary"]["exterior_views"] == 0


def test_a_private_project_names_its_sheet_documents_but_never_copies_them(tmp_path, monkeypatch):
    out = whole_project(tmp_path, monkeypatch)
    write_json(out / "intake_manifest.json", {"kind": "intake_manifest", "alias": "toy", "status": "ok"})
    m = F.write_final(out)
    assert m["private"] is True and m["sheets"]["report"] is None
    assert m["sheets"]["report_kept_on_volume"] == "sheets_report.md"
    assert not (out / "final" / "sheets_report.md").exists() and not (out / "final" / "debug").exists()
    assert all(r["file"] == "document 1" and r["title"] is None for r in m["sheets"]["regions"])
    assert m["sheets"]["debug_images"] == [{"source": "sheets_debug/review01_dxf_s1.png", "preview": None}]


def test_the_variant_sub_output_reads_the_base_projects_gate_and_is_private_like_it(tmp_path):
    base = tmp_path / "outputs" / "real-04"
    sub = base / "variants" / "l-1b"
    write_json(base / "intake_manifest.json", {"kind": "intake_manifest", "alias": "real-04", "status": "ok"})
    write_json(base / "gate" / "gate_calibration.json", {"benign": []})
    (sub / "scene").mkdir(parents=True)
    assert F.variant_root(sub) == (base.resolve(), "l-1b") and F.variant_root(base) == (base.resolve(), "base")
    inp = F.Inputs(project_out=sub.resolve(), out_dir=sub / "final", project="p", root=base.resolve(), variant="l-1b")
    assert inp.gate_dir == base.resolve() / "gate"
    own = F.Inputs(project_out=sub.resolve(), out_dir=sub / "final", project="p", root=base.resolve())
    write_json(sub / "gate" / "gate_validation.json", {"decision": "ok"})
    assert own.gate_dir == sub.resolve() / "gate"                 # its own gate folder wins when it has files
    assert F.is_private(sub) is True


# --------------------------------------------------------------------------
# wenart.report.m10 (pure)
# --------------------------------------------------------------------------

def test_sheets_block_numbers_private_documents_and_lists_the_unit_checks():
    doc = sheets_doc(needs_review=())
    doc["documents"][0]["units"]["checks"] = [{"check": "area_labels", "unit": "cm", "score": 0.97, "samples": 6,
                                               "note": None}]
    doc["regions"][0]["title"] = {"text": "ZEMİN KAT PLANI"}
    block = M.sheets_block(doc, True, {"review01.dxf": "document 1"})
    assert block["regions"][0]["file"] == "document 1" and block["regions"][0]["title"] is None
    assert block["units"][0]["checks"][0]["score"] == 0.97 and block["regions_by_use"] == {"ignored": 2}
    public = M.sheets_block(doc, False)
    assert public["regions"][0]["title"] == "ZEMİN KAT PLANI" and public["regions"][0]["file"] == "review01.dxf"
    text = "\n".join(M.sheets_lines(public, False, stopped=False))
    assert "2 regions (use: ignored 2)" in text and "area_labels cm 0.97 (6)" in text
    assert "it stopped the project" not in text
    assert "it stopped the project" in "\n".join(M.sheets_lines(public, False, stopped=True))
    assert M.sheets_block(None, False) is None


def test_building_block_marks_what_is_assumed_and_survives_a_pre_m10_building():
    assert M.building_block({"levels": []}) is None and M.building_block(None) is None
    legacy = {"levels": [{"id": "L0", "label": "Zemin", "elevation": 0.0, "ceiling_height": 2.7,
                          "ceiling_height_source": "section"}]}
    assert M.building_block(legacy) is None                  # nothing of Milestone 10 in it: no Building section
    legacy["levels"][0]["kind"] = "floor"
    block = M.building_block(legacy)
    assert block["heights"][0] == {"item": "L0 ceiling height", "value": 2.7, "state": "drawn", "from": "section",
                                   "note": None}
    assert block["heights"][1]["state"] == "unknown"         # no elevation source: not called drawn
    assert block["roof"] is None and block["site"] is None and block["slabs"] == []
    text = "\n".join(M.building_lines(block))
    assert "None recorded: the build puts a flat roof slab on the top level." in text
    assert M.assumed_lines(legacy, None) == []
    assert M.state_of("assumed_default") == "assumed" and M.state_of("section") == "drawn"
    assert M.state_of(None) == "unknown"


def test_completion_block_separates_applied_from_refused_and_reverted():
    block = M.completion_block(completion_doc())
    room = block["rooms"][0]
    assert [c["id"] for c in room["changes"]] == ["f_1"]
    assert [x.get("id") or x["type"] for x in room["refused"]] == ["f_9", "f_1", "bed_double"]
    assert room["refused"][0]["why"] == "blocks the door"
    assert room["dropped"][0]["type"] == "side_table" and room["unplaceable_drawn"] == ["f_9"]
    assert block["mode"] == "complete" and block["assumed"] == ["furnished_rooms"]
    keep = completion_doc()
    keep["settings"]["mode"] = "keep"
    assert "only restyled" in "\n".join(M.completion_lines(M.completion_block(keep)))
    assert M.completion_block(None) is None and M.completion_block({"rooms": None}) is None


def test_variants_block_lists_the_base_views_for_an_unchanged_outside():
    building = {"variants": [{"id": "base", "label": "Base", "levels": ["L0"], "base": True},
                             {"id": "alt", "label": "Alt", "levels": ["L0b"], "base": False,
                              "rooms_changed": ["r1"], "exterior_changed": False},
                             {"id": "alt2", "label": "Alt 2", "levels": ["L0c"], "base": False,
                              "rooms_changed": ["r2"], "exterior_changed": True}]}
    manifests = {"base": {"status": "ok", "views": [{"camera": "ext_1", "view_kind": "exterior", "final": "cycles"}]},
                 "alt2": {"status": "ok", "views": [{"camera": "ext_1", "view_kind": "exterior", "final": "polished"},
                                                    {"camera": "cam_1", "final": "cycles"}]}}
    block = M.variants_block(building, manifests, ["ext_1", "ext_2"], "base")
    rows = {v["id"]: v for v in block["variants"]}
    assert rows["alt"]["exterior"] == "unchanged: the base views (ext_1, ext_2)" and not rows["alt"]["reported"]
    assert rows["alt2"]["exterior"] == "its own 1 view(s)" and rows["alt2"]["interior_views"] == ["cam_1"]
    text = "\n".join(M.variants_lines(block))
    assert "No `variants/<id>/final/final_manifest.json` yet for: alt" in text
    assert M.variants_block({"variants": [{"id": "base"}]}, {}, [], "base") is None
