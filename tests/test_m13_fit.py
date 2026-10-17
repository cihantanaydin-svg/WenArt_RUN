"""Milestone 13 track T1 (docs/milestone13.md §3.0 K1, K2, K7; §12 D1, D3, D4, D5; §13.2, §13.3): the licence model
of the catalogue (modes, flags, ``usable``), the licence fields the script wrote onto the committed catalogue files,
the fit in commercial and relaxed mode (the committed real02 / real03 / real04 buildings leave no flagged asset in
commercial mode), the product-size snap before the fit, the fallback ladder (library -> module -> parametric), the
uniform scale, the wood re-sort gone, design tags as preferences, pins without the style filter, the diversity
penalty, the fabric colour on the asset and the CLI flags. CPU only; every number here is computed from the files.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path

import pytest

from wenart import building as B
from wenart.furniture import catalog as C
from wenart.furniture import complete as CO
from wenart.furniture import fit as F
from wenart.furniture import sizes as SZ

from conftest import load_truth
from test_furniture_fit_v2 import FakeCatalog, model, piece

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ("real02", "real03", "real04")
ANCHORS = ("sofa", "sofa_corner", "bed_double", "table_dining", "wardrobe", "desk")


@pytest.fixture(scope="module")
def library():
    return C.load()


def drawn(ftype, w, d, pid, room="r_L0_salon", front=0.0, center=(1.0, 2.0), **extra):
    """A drawn piece (``from_documents``) with a front: the snap keeps its back edge where it was."""
    p = piece(ftype, w, d, pid=pid)
    p.update({"room_id": room, "front_deg": front, "footprint": {"center": list(center), "size": [w, d],
                                                                  "rotation_deg": (front + 90.0) % 360.0}})
    p.update(extra)
    return p


# --------------------------------------------------------------------------
# 1. Licence model (catalog.py)
# --------------------------------------------------------------------------

def test_licence_modes_and_flags_are_the_frozen_interface():
    assert C.LICENCE_MODES == ("commercial", "relaxed")
    assert C.LICENCE_FLAGS == ("none", "non_commercial", "share_alike", "no_derivatives", "research_only", "regional",
                               "tool_nc")
    for bad in ("Commercial ", "relaxed", "commercial"):
        assert C.check_mode(bad) in C.LICENCE_MODES
    with pytest.raises(ValueError):
        C.check_mode("comercial")
    assert C.licence_mode() in C.LICENCE_MODES


def test_flags_from_the_licence_text_the_catalogue_flag_and_the_export_tool():
    cc0 = {"id": "a", "source": "polyhaven", "licence": "CC0"}
    by = {"id": "b", "source": "abo", "licence": "CC-BY-4.0"}
    nc = {"id": "c", "source": "objaverse", "licence": "CC-BY-NC-4.0"}
    sa = {"id": "d", "source": "objaverse", "licence": "CC-BY-SA-4.0", "licence_flag": "share_alike"}
    nd = {"id": "e", "source": "objaverse", "licence": "CC-BY-ND-4.0"}
    ncnd = {"id": "f", "source": "objaverse", "licence": "CC-BY-NC-ND-4.0"}
    trellis = {"id": "g", "source": "generated", "licence": "generated (TRELLIS.2-4B, MIT)"}
    infinigen = {"id": "h", "source": "generated", "licence": "generated (Infinigen v1.19.0, BSD-3-Clause)"}
    research = {"id": "i", "source": "abo", "licence": "CC-BY-4.0", "licence_flag": "research_only"}
    regional = {"id": "j", "source": "abo", "licence": "CC-BY-4.0", "licence_flag": "regional"}
    unknown = {"id": "k", "source": "objaverse", "licence": "Sketchfab-Standard"}
    looser = {"id": "l", "source": "objaverse", "licence": "CC-BY-NC-4.0", "licence_flag": "none"}   # never looser
    assert [C.licence_flag_of(e) for e in (cc0, by, nc, sa, nd, ncnd, trellis, infinigen, research, regional)] == [
        "none", "none", "non_commercial", "share_alike", "no_derivatives", "no_derivatives", "tool_nc", "none",
        "research_only", "regional"]
    assert C.licence_flag_of(unknown) == "unknown" and C.licence_flag_of(looser) == "non_commercial"
    assert C.is_tool_nc(trellis) and not C.is_tool_nc(infinigen) and not C.is_tool_nc(by)
    assert C.is_tool_nc({"source": "generated", "licence": "generated (x)", "generated": {"export": "nvdiffrast bake"}})
    # the Milestone 8 call with a licence text keeps its answer (wenart.assets.objaverse writes it into new entries)
    assert C.licence_flag_of("CC0") is None and C.licence_flag_of("CC-BY-4.0") is None
    assert C.licence_flag_of("CC-BY-NC-4.0") == "non_commercial" and C.licence_flag_of("made up") == "unknown"
    assert C.licence_text_flag("CC-BY-NC-SA-4.0") == "non_commercial" and C.licence_text_flag("cc by-nd 4.0") == \
        "no_derivatives"
    # commercial_safe is flag none; the modes
    assert C.commercial_safe(cc0) and C.commercial_safe(by) and C.commercial_safe(infinigen)
    assert not C.commercial_safe(trellis) and not C.commercial_safe(research)
    for e in (cc0, by, infinigen):
        assert C.usable(e) and C.usable(e, "commercial") and C.usable(e, "relaxed") and C.unusable_reason(e) is None
    for e in (nc, sa, trellis, research, regional):
        assert not C.usable(e, "commercial") and C.usable(e, "relaxed")
        assert "relaxed mode only" in C.unusable_reason(e, "commercial") and C.unusable_reason(e, "relaxed") is None
    for e in (nd, ncnd, unknown):
        assert not C.usable(e, "commercial") and not C.usable(e, "relaxed")
        assert "never used in any mode" in C.unusable_reason(e, "relaxed")
    assert C.unusable_reason(nc).startswith("licence CC-BY-NC-4.0 (non_commercial): not used in commercial mode")
    removed = dict(by, audit={"status": "removed", "reasons": ["air bed"]})
    assert not C.usable(removed, "relaxed") and C.unusable_reason(removed, "relaxed").startswith("audit: removed")
    assert not C.usable(dict(by, audit={"status": "pending"}), "relaxed")
    with pytest.raises(ValueError):
        C.usable(by, "free")


def test_licence_mode_env_beats_the_brief_beats_the_default(monkeypatch):
    from wenart import brief as BR

    monkeypatch.delenv(C.LICENCE_MODE_ENV, raising=False)
    assert C.licence_mode() == "commercial" and C.licence_mode_from()[1].endswith("default commercial")
    real02 = BR.load_brief(ROOT / "projects" / "real02")                     # D1: the PoC projects are relaxed
    assert C.licence_mode(real02) == "relaxed" and C.licence_mode_from(real02)[1] == "brief library.licence_mode"
    for p in PROJECTS:
        assert C.licence_mode(BR.load_brief(ROOT / "projects" / p)) == "relaxed"
    defaults = BR.load_brief(ROOT / "projects" / "does-not-exist")           # wenart/defaults.yaml: commercial
    assert C.licence_mode(defaults) == "commercial" and "default of wenart/defaults.yaml" in C.licence_mode_from(defaults)[1]
    assert C.licence_mode({"library": {"licence_mode": "relaxed"}}) == "relaxed"      # a raw brief dict
    assert C.licence_mode(real02, env={"WENART_LICENCE_MODE": "commercial"}) == "commercial"
    assert C.licence_mode(real02, env={"WENART_LICENCE_MODE": " Relaxed "}) == "relaxed"
    mode, why = C.licence_mode_from(defaults, env={"WENART_LICENCE_MODE": "comercial"})   # a typo never picks a mode
    assert mode == "commercial" and "is no mode word, ignored" in why
    monkeypatch.setenv(C.LICENCE_MODE_ENV, "relaxed")
    assert C.licence_mode() == "relaxed" and C.licence_mode(defaults) == "relaxed"
    assert C.licence_mode_from()[1] == "env WENART_LICENCE_MODE"


def test_the_committed_catalogue_files_carry_the_licence_fields_written_by_the_script(tmp_path):
    """The fields of §13.3 on every existing entry, written by ``python -m wenart.furniture licence-fields`` (never by
    hand): the script is idempotent on the committed files, so they are what it writes."""
    for name in ("catalog.json", "catalog_library.json"):
        src = ROOT / "wenart" / "furniture" / name
        copy_path = tmp_path / name
        copy_path.write_bytes(src.read_bytes())
        counts = C.write_licence_fields(copy_path)
        assert counts["changed"] == 0 and copy_path.read_bytes() == src.read_bytes(), name
        data = json.loads(src.read_text(encoding="utf-8"))
        for section in ("entries", "decor"):
            for e in data.get(section) or []:
                if e.get("parametric"):
                    continue
                assert e["licence_flag"] in C.LICENCE_FLAGS, e["id"]
                assert e["licence_declared_by"] in C.DECLARED_BY_VALUES, e["id"]
                assert e["commercial_safe"] == (e["licence_flag"] == "none") == C.commercial_safe(e), e["id"]
                assert e["licence_url"].startswith("https://"), e["id"]
                assert isinstance(e["attribution"], str), e["id"]
                declared = "uploader" if e["source"] == "objaverse" else "publisher"
                assert e["licence_declared_by"] == declared, e["id"]
                if str(e["licence"]).startswith("generated (TRELLIS.2"):            # D3: nvdiffrast in the export
                    assert e["licence_flag"] == "tool_nc" and not e["commercial_safe"], e["id"]
                    assert "nvdiffrast" in e["licence_flag_note"] and e["licence_url"].endswith("TRELLIS.2/blob/main/LICENSE")
                elif str(e["licence"]).startswith("generated"):
                    assert e["licence_flag"] == "none", e["id"]                     # Infinigen: Blender export
    lib = json.loads((ROOT / "wenart" / "furniture" / "catalog_library.json").read_text(encoding="utf-8"))
    flags = {}
    for section in ("entries", "decor"):
        for e in lib[section]:
            flags[e["licence_flag"]] = flags.get(e["licence_flag"], 0) + 1
    trellis = sum(1 for e in lib["entries"] if str(e["licence"]).startswith("generated (TRELLIS.2"))
    assert trellis == 196 and flags["tool_nc"] >= trellis               # the 196 furniture entries + decor
    assert flags["tool_nc"] == sum(1 for s in ("entries", "decor") for e in lib[s]
                                   if str(e["licence"]).startswith("generated (TRELLIS.2"))
    assert set(flags) <= set(C.LICENCE_FLAGS) and "no_derivatives" not in flags
    main = json.loads((ROOT / "wenart" / "furniture" / "catalog.json").read_text(encoding="utf-8"))
    assert all(e["licence_flag"] == "none" and e["licence_url"] == C.POLYHAVEN_LICENCE_URL
               for s in ("entries", "decor") for e in main.get(s) or [] if not e.get("parametric"))
    # the pure writer puts the new keys into the licence block (the file diff holds the new lines only)
    e = {"id": "x", "source": "abo", "licence": "CC-BY-4.0", "licence_flag": None, "licence_url": "https://u",
         "name": "n", "attribution": "a", "bbox_m": [1, 1, 1]}
    data = {"entries": [e]}
    C.add_licence_fields(data)
    assert list(data["entries"][0]) == ["id", "source", "licence", "licence_flag", "licence_url", "licence_declared_by",
                                         "commercial_safe", "name", "attribution", "bbox_m"]
    assert data["entries"][0]["licence_flag"] == "none" and data["entries"][0]["commercial_safe"] is True


def test_real_catalogue_entries_by_mode(library):
    """One committed entry per flag and audit status (ids read from the files on 15 Oct 2026)."""
    by_id = {e["id"]: e for e in library.models}
    trellis_keep = by_id["gen_bed_single_industrial_1_9f087076"]
    assert C.licence_flag_of(trellis_keep) == "tool_nc" and not C.usable(trellis_keep) and C.usable(trellis_keep, "relaxed")
    assert C.unusable_reason(trellis_keep).startswith("licence generated (TRELLIS.2-4B, MIT) (tool_nc): not used in "
                                                      "commercial mode")
    trellis_removed = by_id["gen_bed_single_classic_1_dbac0f10"]
    assert not C.usable(trellis_removed, "relaxed") and C.unusable_reason(trellis_removed, "relaxed").startswith("audit")
    nc = by_id["objaverse_094697a23146463cb5564ac8bf89e5c4"]
    assert nc["licence"] == "CC-BY-NC-4.0" and C.licence_flag_of(nc) == "non_commercial"
    assert not C.usable(nc, "relaxed")                                       # audit removed as well
    sa = by_id["objaverse_3eafb89804b54c8e8cbe35e4d456e0a9"]
    assert C.licence_flag_of(sa) == "share_alike" and not C.usable(sa)
    abo = by_id["abo_B0718WYQ8D"]
    assert C.licence_flag_of(abo) == "none" and C.usable(abo) and C.usable(abo, "relaxed") and abo["commercial_safe"]
    infinigen = by_id["infinigen_bathtub_0"]
    assert C.licence_flag_of(infinigen) == "none" and C.usable(infinigen)
    polyhaven = by_id["sofa_02"]
    assert polyhaven["licence"] == "CC0" and C.usable(polyhaven) and polyhaven["licence_declared_by"] == "publisher"
    # the catalogue validates with the new fields, and refuses a CC BY entry that claims a CC marker it has not
    C.validate(library.data)
    with pytest.raises(C.CatalogError, match="licence_flag"):
        C.validate({"entries": [dict(copy.deepcopy(abo), licence_flag="non_commercial")]}, complete=False)
    with pytest.raises(C.CatalogError, match="commercial_safe"):
        C.validate({"entries": [dict(copy.deepcopy(abo), commercial_safe=False)]}, complete=False)
    C.validate({"entries": [dict(copy.deepcopy(abo), licence_flag="research_only", commercial_safe=False)]},
               complete=False)                                                 # an audit-only limit on a CC BY text
    with pytest.raises(C.CatalogError, match="licence_declared_by"):
        C.validate({"entries": [dict(copy.deepcopy(abo), licence_declared_by="me")]}, complete=False)


# --------------------------------------------------------------------------
# 2. The fit in commercial and relaxed mode on the committed buildings (also T8's test)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("project", PROJECTS)
def test_commercial_mode_fit_of_the_committed_buildings_leaves_no_flagged_asset(project, library):
    path = ROOT / "results" / "furniture" / project / "building_final.json"
    if not path.is_file():
        pytest.skip("no committed building")
    building = json.loads(path.read_text(encoding="utf-8"))
    style = json.loads((path.parent / "style.json").read_text(encoding="utf-8"))
    style = style[0] if isinstance(style, list) else style
    fitted = F.fit_building(building, library, style_family="modern", style=style, mode="commercial")
    assert fitted["project"]["licence_mode"] == "commercial" and fitted["project"]["licence_mode_source"] == "given to the fit"
    assets = [p["asset"] for p in fitted["furniture"]] + [d["asset"] for d in fitted.get("decor") or [] if d.get("asset")]
    assert all(a["commercial_safe"] is True and a["licence_flag"] == "none" for a in assets)
    assert all(a["licence_mode"] == "commercial" for a in assets)
    assert all(C.usable(a) for a in assets if a["method"] == "library")
    assert "commercial-safe: yes" in F.fit_report(fitted)
    # D4: every built piece is built; a drawn anchor is never left out
    built = [p for p in fitted["furniture"] if p.get("build", True) is not False and p["type"] != "unknown"]
    assert all(p["asset"]["method"] in ("library", "module", "parametric") for p in built)
    anchors = [p for p in built if p["source"] == "from_documents" and p["type"] in ANCHORS]
    assert anchors and all(p["asset"]["method"] != "none" for p in anchors)
    for p in built:
        assert p["asset"]["ladder"] and p["asset"]["ladder"][0]["step"] == "library"
        if p["asset"]["method"] in ("module", "parametric") and not p["asset"].get("by_design"):
            assert p["library_gap"]["step"] == p["asset"]["method"], p["id"]
    # relaxed mode: the PoC default (D1); flagged assets are the tool_nc models (the NC / SA uploads are all
    # audit-removed on 15 Oct 2026), never a no-derivatives one; the report says which
    relaxed = F.fit_building(building, library, style_family="modern", style=style, mode="relaxed")
    assert relaxed["project"]["licence_mode"] == "relaxed"
    flagged = {a["asset_id"]: a["licence_flag"] for p in relaxed["furniture"] for a in [p["asset"]]
               if a["method"] == "library" and a["commercial_safe"] is False}
    assert set(flagged.values()) <= set(C.LICENCE_FLAGS) - {"no_derivatives", "none"}
    report = F.fit_report(relaxed)
    assert ("commercial-safe: yes" in report) == (not flagged)
    for asset_id in flagged:
        assert asset_id in report.split("commercial-safe: no")[1].split("\n")[0]
    # the mode written into the building is what a later fit reads when none is given (never the brief)
    again = F.fit_building(relaxed, library, style_family="modern", style=style)
    assert again["project"]["licence_mode"] == "relaxed" and again["project"]["licence_mode_source"] == \
        "building project.licence_mode"


def test_project_licence_mode_is_written_and_resolved(monkeypatch):
    from wenart import brief as BR

    monkeypatch.delenv(C.LICENCE_MODE_ENV, raising=False)
    cat = FakeCatalog([model("exact", "sofa", 2.0, 0.9, 0.8)])
    building = {"furniture": [piece("sofa", 2.0, 0.9)]}
    fitted = F.fit_building(building, cat)
    assert fitted["project"]["licence_mode"] == "commercial" and "default commercial" in fitted["project"]["licence_mode_source"]
    assert "project" not in building and fitted["project"]["size_snap"]["on"] is True
    F.assert_only_assets_changed(building, fitted)
    assert F.fit_building(building, cat, brief=BR.load_brief(ROOT / "projects" / "real02"))["project"]["licence_mode"] == "relaxed"
    assert F.fit_building(building, cat, mode="relaxed")["project"]["licence_mode"] == "relaxed"
    stored = dict(building, project={"id": "t", "licence_mode": "relaxed"})
    assert F.fit_building(stored, cat)["project"]["licence_mode"] == "relaxed"                  # the building wins
    assert F.fit_building(stored, cat, mode="commercial")["project"]["licence_mode"] == "commercial"   # a given mode
    assert F.resolve_mode(stored, None, None) == ("relaxed", "building project.licence_mode")
    with pytest.raises(ValueError):
        F.fit_building(building, cat, mode="free")


# --------------------------------------------------------------------------
# 3. The size snap (sizes.py and the fit)
# --------------------------------------------------------------------------

def test_product_grid_rows_lie_inside_their_ranges_and_cite_a_source():
    assert set(ANCHORS) <= set(SZ.PRODUCT_GRID) and "chair" in SZ.PRODUCT_GRID
    sources = ("std", "syn", "abo", "ph", "objaverse", "r01", "m10", "m11", "m12", "product")
    for ftype, rows in SZ.PRODUCT_GRID.items():
        r = SZ.real_range(ftype)
        for row in rows:
            assert r["width"][0] - 1e-9 <= row["w"] <= r["width"][1] + 1e-9, (ftype, row)
            assert r["depth"][0] - 1e-9 <= row["d"] <= r["depth"][1] + 1e-9, (ftype, row)
            if r["height"] and row.get("h") is not None:
                assert r["height"][0] - 1e-9 <= row["h"] <= r["height"][1] + 1e-9, (ftype, row)
            assert any(s in row["label"] for s in sources), (ftype, row)
    assert SZ.grid_sources("bed_double")[0].startswith("double 140 x 200")
    assert SZ.SNAP_TOLERANCE == 0.05 == F.SIZE_BUCKET


def test_snap_size_on_the_drawn_sizes_of_the_diagnosis():
    bed = SZ.snap_size("bed_double", (2.55, 2.0))                 # the YATAK block: bed + nightstands
    assert bed["changed"] and bed["footprint"] == (1.8, 2.0) and "king 180 x 200" in bed["product"]
    assert bed["reason"].startswith("width 2.55 m is 27 % outside 1.35-2 m")
    chair = SZ.snap_size("chair", (0.71, 0.45))                   # the split artefact of "table + 2 chairs"
    assert chair["changed"] and chair["footprint"] == (0.5, 0.5) and chair["product"].startswith("0.50 x 0.50")
    assert not SZ.snap_size("chair", (0.58, 0.45))["changed"]
    assert not SZ.snap_size("table_dining", (3.35, 1.0))["changed"]        # a real 10-seat table (range to 3.40)
    assert not SZ.snap_size("sofa_corner", (4.38, 1.97))["changed"]        # real (range to 4.50)
    run = SZ.snap_size("wardrobe", (2.57, 0.74))                           # a built-in run keeps its length
    assert run["changed"] and run["footprint"] == (2.57, 0.6) and "run" in run["reason"]
    assert not SZ.snap_size("wardrobe", (3.11, 0.60))["changed"]
    small = SZ.snap_size("sofa", (1.30, 0.63))
    assert small["changed"] and small["footprint"] == (1.3, 0.85) and "small 2-seat 130" in small["product"]
    lamp = SZ.snap_size("floor_lamp", (0.79, 0.79))
    assert lamp["changed"] and lamp["footprint"] == (0.6, 0.6)
    side = SZ.snap_size("table_coffee", (0.56, 0.56))
    assert side["changed"] and side["footprint"] == (0.8, 0.8) and "square symbol" in side["reason"]
    assert SZ.snap_size("table_coffee", (1.52, 0.60))["footprint"] == (1.2, 0.7)
    assert SZ.snap_size("table_dining", (0.79, 0.65))["footprint"] == (0.8, 0.8)
    # the 5 % drawing tolerance: a 1.80 m shelf unit 2 % too shallow stays; a desk 0.7 % too deep stays
    shelf = SZ.snap_size("bookshelf", (1.8003, 0.2456))
    assert not shelf["changed"] and "drawing tolerance" in shelf["reason"]
    assert not SZ.snap_size("desk", (1.4471, 0.9068))["changed"]
    # a long piece whose length is real keeps it and takes the product depth (real03: 1.80 x 0.25 hall consoles are
    # inside the widened console range; one read 0.20 m deep would keep its 1.80 m)
    assert not SZ.snap_size("console_table", (1.8003, 0.2456))["changed"]
    console = SZ.snap_size("console_table", (1.8003, 0.20))                 # the length clamped to the range (1.80)
    assert console["changed"] and console["footprint"] == (1.8, 0.3) and "a long piece keeps its length" in console["reason"]
    assert SZ.snap_size("tv_unit", (1.6, 0.2))["footprint"] == (1.6, 0.4)
    assert SZ.snap_size("desk", (1.45, 1.1))["footprint"] == (1.45, 0.8)
    assert SZ.snap_size("console_table", (0.5, 0.2))["footprint"] == (0.9, 0.3)       # length wrong too: a product
    assert set(SZ.KEEP_LENGTH_TYPES) & set(ANCHORS) == {"desk"} and "chair" not in SZ.KEEP_LENGTH_TYPES
    # an orientation question (fits turned by 90 degrees, or far closer turned) is no snap: the solver's business
    turned = SZ.snap_size("sofa", (0.9, 1.4))
    assert not turned["changed"] and "orientation question" in turned["reason"]
    swapped = SZ.snap_size("bookshelf", (0.40, 2.17))
    assert not swapped["changed"] and "turned by 90 degrees it is only 8 % outside" in swapped["reason"]
    bench = SZ.snap_size("bench", (0.6, 1.5175))
    assert not bench["changed"] and "orientation question" in bench["reason"]
    # heights
    tall = SZ.snap_size("bed_double", (1.6, 2.0), 3.0)
    assert tall["changed"] and tall["footprint"] == (1.6, 2.0) and tall["height"] == 1.0
    assert SZ.snap_size("bed_double", (2.55, 2.0), 0.5)["height"] == 0.5             # inside: kept
    # no table row, no size, a square chair symbol: never changed
    assert SZ.snap_size("nope", (1, 1)) == {"footprint": (1.0, 1.0), "height": None, "product": None,
                                            "changed": False, "reason": "no size row for type 'nope'"}
    assert not SZ.snap_size("chair", (0, 0.4))["changed"] and not SZ.snap_size("chair", "x")["changed"]
    assert not SZ.snap_size("nightstand", (0.5, 0.4))["changed"]


def test_the_fit_snaps_drawn_sizes_before_fitting_and_keeps_the_labels(library):
    bed = drawn("bed_double", 2.55, 2.0, "f_L0_007", room="r_L0_bed", front=270.0, center=(3.0, 4.0))
    sofa = drawn("sofa", 1.2958, 0.6314, "f_L-1_061", front=0.0, center=(1.0, 2.0), height=0.8)
    chairs = [drawn("chair", 0.7091, 0.45, f"f_L-1b_05{i}", center=(0.5 * i, 0.0)) for i in range(2, 4)]
    added = dict(drawn("bed_double", 2.55, 2.0, "f_L0_900"), source="added_by_ai")
    toilet = drawn("toilet", 1.15, 0.36, "f_L0_050", room="r_L0_bath")
    gone = dict(drawn("sofa", 1.3, 0.63, "f_L0_051"), build=False)
    tall = drawn("bed_double", 2.55, 2.0, "f_L0_008", room="r_L0_bed2", height=3.0)     # a misread height too
    building = {"project": {"id": "t", "licence_mode": "relaxed"},
                "furniture": [bed, sofa] + chairs + [added, toilet, gone, tall]}
    before = copy.deepcopy(building)
    fitted = F.fit_building(building, library, style_family="modern")
    assert building == before
    F.assert_only_assets_changed(building, fitted)
    out = {p["id"]: p for p in fitted["furniture"]}
    b = out["f_L0_007"]
    assert b["footprint"]["size"] == [1.8, 2.0] and b["footprint"]["center"] == [3.0, 4.0]     # width: centre kept
    assert b["drawn_footprint"] == bed["footprint"] and b["drawn_type"] == "bed_double"
    assert b["size_snap"] == {"drawn": [2.55, 2.0], "snapped": [1.8, 2.0], "product": b["size_snap"]["product"],
                              "reason": b["size_snap"]["reason"]} and "king 180 x 200" in b["size_snap"]["product"]
    assert b["adjusted_by_ai"]["rule"] == "size_snap" and "size snap" in b["adjusted_by_ai"]["reason"]
    assert "user OK D5 of 12 Oct 2026" in b["adjusted_by_ai"]["reason"]
    assert b["adjusted_by_ai"]["changed"]["footprint"] == bed["footprint"]
    assert b["asset"]["method"] == "library" and b["asset"]["bbox_m"][0] == pytest.approx(1.8, abs=1e-3)
    s = out["f_L-1_061"]                                        # depth: the back edge stays (front along +X)
    assert s["footprint"]["size"] == [1.3, 0.85]
    assert s["footprint"]["center"] == [round(1.0 + (0.85 - 0.6314) / 2, 4), 2.0]
    assert s["drawn_footprint"]["size"] == [1.2958, 0.6314] and s["drawn_height"] == 0.8 and s["height"] == 0.8
    for c in chairs:
        assert out[c["id"]]["footprint"]["size"] == [0.5, 0.5] and out[c["id"]]["size_snap"]["drawn"] == [0.7091, 0.45]
    assert "size_snap" not in out["f_L0_900"] and out["f_L0_900"]["footprint"] == added["footprint"]   # not drawn
    assert "size_snap" not in out["f_L0_050"]                                              # fixed equipment
    assert "size_snap" not in out["f_L0_051"] and out["f_L0_051"]["asset"]["method"] == "none"   # not built
    t = out["f_L0_008"]                                         # the height snapped: the drawn one is kept (review fix)
    assert t["height"] == 1.0 and t["drawn_height"] == 3.0 and t["adjusted_by_ai"]["changed"]["height"] == 3.0
    assert t["size_snap"]["drawn"] == [2.55, 2.0, 3.0] and t["size_snap"]["snapped"] == [1.8, 2.0, 1.0]
    assert F.snap_candidate(added) == "not drawn" and F.snap_candidate(toilet).startswith("fixed equipment")
    assert F.snap_candidate(gone) == "not built" and F.snap_candidate(bed) is None
    assert fitted["project"]["size_snap"]["on"] is True and fitted["project"]["licence_mode"] == "relaxed"
    report = F.fit_report(fitted)
    assert "## Size snaps" in report and "- f_L0_007 (bed_double): 2.55 x 2.00 -> 1.80 x 2.00 m" in report
    # a second fit of the snapped building changes nothing more (the snapped size is inside the range)
    again = F.fit_building(fitted, library, style_family="modern")
    assert again["furniture"][0]["size_snap"] == b["size_snap"] and again["furniture"][0]["footprint"] == b["footprint"]
    assert again["furniture"][0]["adjusted_by_ai"]["reason"] == b["adjusted_by_ai"]["reason"]


def test_the_size_snap_is_off_with_keep_or_keep_size(library):
    from wenart import brief as BR

    bed = drawn("bed_double", 2.55, 2.0, "f_L0_007")
    building = {"furniture": [bed]}
    assert F.snap_allowed(None) == (True, "no brief: furnished_rooms complete (default), size snap on")
    assert F.snap_allowed({"furnished_rooms": "keep"})[0] is False
    assert F.snap_allowed({"furnished_rooms_keep_size": True})[0] is False
    assert F.snap_allowed(CO.Settings(mode="keep"))[0] is False and F.snap_allowed(CO.Settings(keep_size=True))[0] is False
    assert F.snap_allowed(CO.Settings())[0] is True
    for settings in ({"furnished_rooms": "keep"}, {"furnished_rooms_keep_size": True}, CO.Settings(mode="keep"),
                     CO.Settings(keep_size=True)):
        fitted = F.fit_building(building, library, settings=settings)
        p = fitted["furniture"][0]
        assert "size_snap" not in p and p["footprint"] == bed["footprint"] and fitted["project"]["size_snap"]["on"] is False
        assert p["asset"]["method"] in ("library", "module", "parametric")            # still built (the ladder)
    assert "size_snap" in F.fit_building(building, library, settings=CO.Settings())["furniture"][0]
    assert "size_snap" not in F.fit_building(building, library, snap=False)["furniture"][0]
    brief = BR.load_brief(ROOT / "projects" / "real04")                 # the real briefs: complete, keep_size false
    assert "size_snap" in F.fit_building(building, library, brief=brief)["furniture"][0]
    keep = copy.deepcopy(brief)
    keep["values"]["furnished_rooms"] = "keep"
    assert "size_snap" not in F.fit_building(building, library, brief=keep)["furniture"][0]


# --------------------------------------------------------------------------
# 4. The ladder on the real library: the 10-seat table and the YATAK bed
# --------------------------------------------------------------------------

def test_ladder_on_a_ten_seat_table_and_the_yatak_bed(library, monkeypatch):
    table = drawn("table_dining", 3.35, 1.0, "f_L-1_027", height=0.75)
    bed = drawn("bed_double", 2.55, 2.0, "f_L0_007", room="r_L0_bed")
    for mode in ("commercial", "relaxed"):
        fitted = F.fit_building({"furniture": [table, bed]}, library, style_family="modern", mode=mode)
        t, b = fitted["furniture"]
        # the table is a real size (range to 3.40 m): no snap; the library has no 3.35 m table (usable widths
        # 0.75-2.41 m: 39 % too small for the relaxed 1.30 too); step 2 of the ladder builds it from modules when
        # wenart.blender.modules (track T2) knows a long table, else step 3 the family
        assert "size_snap" not in t and t["footprint"]["size"] == [3.35, 1.0]
        assert t["asset"]["method"] in ("module", "parametric") and t["asset"]["method"] != "none"
        steps = [(s["step"], s["result"]) for s in t["asset"]["ladder"]]
        assert steps[0] == ("library", "no model") and "no table_dining candidate" in t["asset"]["ladder"][0]["reason"]
        assert t["library_gap"]["step"] == t["asset"]["method"] and t["library_gap"]["type"] == "table_dining"
        if t["asset"]["method"] == "module":
            assert steps[1][0] == "module" and steps[1][1].startswith("used ")
            assert t["asset"]["module_plan"]["footprint_m"] == [3.35, 1.0] and t["asset"]["bbox_m"][:2] == [3.35, 1.0]
            assert t["library_gap"]["used"].startswith("module builder")
        assert t["asset"]["licence"] == "n/a" and t["asset"]["commercial_safe"] is True
        # the bed block becomes a 1.80 x 2.00 bed (the nightstands are the solver's) and gets a real product
        assert b["size_snap"]["snapped"][:2] == [1.8, 2.0] and b["asset"]["method"] == "library"
        assert b["asset"]["licence_flag"] == "none" and b["asset"]["ladder"] == [
            {"step": "library", "result": f"used {b['asset']['asset_id']}", "reason": b["asset"]["ladder"][0]["reason"]}]
        assert "library_gap" not in b
    # without a module builder the family builds the table (step 3), logged with the reason
    monkeypatch.setattr(F, "module_plan_for", lambda piece, style=None: (None, "no module builder (mocked)"))
    fitted = F.fit_building({"furniture": [table]}, library, style_family="modern", mode="relaxed")
    t = fitted["furniture"][0]
    assert t["asset"]["method"] == "parametric" and t["asset"]["asset_id"] == "parametric:table_dining"
    assert [s["result"] for s in t["asset"]["ladder"]] == ["no model", "no module builder", "used"]
    assert t["asset"]["ladder"][1]["reason"] == "no module builder (mocked)" and t["library_gap"]["step"] == "parametric"
    assert "## Built below the library level" in F.fit_report(fitted)


def test_a_split_table_plan_labels_the_piece_adjusted_by_ai_and_keeps_the_drawn_footprint(library):
    """Build round 2 (T2 review -> T1): a drawn table footprint deeper than a real table includes its chairs
    (CLAUDE.md); the module builder splits it into table + chairs (``plan["split"]``) and the fit labels the piece
    ``adjusted_by_ai`` with the reason, keeps the footprint as drawn and the ``drawn_*`` keys; a table without a
    split gets no label, and ``assert_only_assets_changed`` accepts the labelled piece."""
    from wenart.blender import modules as MOD

    deep = drawn("table_dining", 3.35, 1.8, "f_L0_t1", height=0.75)        # 1.8 m deep: the chairs are in the box
    plain = drawn("table_dining", 3.35, 1.0, "f_L0_t2", height=0.75)
    before = {"furniture": [deep, plain]}
    # Build round 3 (lead decision): with the size snap on (the default) the split decides first: the deep table is
    # labelled module_split, its table part (3.35 x 0.80 m) is inside the product range, so nothing is snapped and
    # the chairs stay in the box (round 2 snapped the 1.8 m depth to a 1.0 m product first, which erased them).
    split_first = F.fit_building(copy.deepcopy(before), library, style_family="modern", mode="relaxed")
    s = split_first["furniture"][0]
    assert "size_snap" not in s and s["footprint"] == deep["footprint"] and s["drawn_footprint"] == deep["footprint"]
    assert s["adjusted_by_ai"]["rule"] == F.SPLIT_RULE and s["asset"]["module_plan"]["split"]["chairs"] >= 2
    assert split_first["project"]["size_snap"] == {"on": True, "why": split_first["project"]["size_snap"]["why"],
                                                   "split_first": ["f_L0_t1"]}
    assert "size_snap" not in split_first["furniture"][1] and "adjusted_by_ai" not in split_first["furniture"][1]
    F.assert_only_assets_changed(before, split_first)
    # with the snap off (furnished_rooms keep_size) the module builder splits at fit time, the same label
    fitted = F.fit_building(copy.deepcopy(before), library, style_family="modern", mode="relaxed", snap=False)
    t, u = fitted["furniture"]
    assert t["adjusted_by_ai"]["split"] == s["adjusted_by_ai"]["split"] and "split_first" not in fitted["project"]["size_snap"]
    assert t["asset"]["method"] == "module" and t["asset"]["module_plan"]["builder"] == "table_long"
    split = t["asset"]["module_plan"]["split"]
    assert split and split["chairs"] >= 2 and split["table_m"][1] <= MOD.TABLE_DEPTH_RANGE_M[1]
    label = t["adjusted_by_ai"]
    assert label["rule"] == F.SPLIT_RULE and label["split"] == split and label["changed"] == {}
    assert "module split" in label["reason"] and f"with {split['chairs']} chairs" in label["reason"]
    assert "3.35 x 1.80 m footprint" in label["reason"] and "drawn_footprint kept" in label["reason"]
    assert t["footprint"] == deep["footprint"] and t["drawn_footprint"] == deep["footprint"]
    assert t["drawn_type"] == "table_dining" and t["drawn_front_deg"] == 0.0 and t["drawn_height"] == 0.75
    assert t["asset"]["adjusted_by_ai"]["rule"] == F.SPLIT_RULE and "size_snap" not in t
    assert "adjusted_by_ai" not in u and "drawn_footprint" not in u and not u["asset"]["module_plan"].get("split")
    F.assert_only_assets_changed(before, fitted)
    # the pure helpers: no split, no label; a second application is a no-op; an earlier label's reason stays in front
    assert F.split_label(plain, u["asset"]["module_plan"]) is None
    assert F.apply_split_label(t) is False and t["adjusted_by_ai"] == label
    snapped = dict(copy.deepcopy(deep), adjusted_by_ai={"reason": "size snap: x", "rule": F.SNAP_RULE,
                                                         "changed": {"footprint": {"size": [3.4, 1.8]}}, "round": 2})
    assert F.apply_split_label(snapped, t["asset"]) is True
    assert snapped["adjusted_by_ai"]["reason"].startswith("size snap: x; module split")
    assert snapped["adjusted_by_ai"]["rules"] == [F.SNAP_RULE, F.SPLIT_RULE] and snapped["adjusted_by_ai"]["round"] == 2
    assert snapped["adjusted_by_ai"]["changed"] == {"footprint": {"size": [3.4, 1.8]}}
    # the label stays on the asset of a refit through fit_piece (the agent's retype path applies it itself)
    asset = F.fit_piece(deep, library, style_family="modern", mode="relaxed")
    assert asset["adjusted_by_ai"]["rule"] == F.SPLIT_RULE and "adjusted_by_ai" not in deep
    # a labelled piece whose footprint changed is not a valid fit result
    broken = copy.deepcopy(fitted)
    broken["furniture"][0]["footprint"]["size"] = [3.35, 1.0]
    with pytest.raises(AssertionError, match="must not change the footprint"):
        F.assert_only_assets_changed(before, broken)


def test_the_real04_ten_seat_tables_keep_their_chairs_with_the_split_before_the_snap(library):
    """Build round 3 item 2 (lead decision: the split decides before the size snap) on the real04 drawing. Its two
    10-seat tables of the L-1 salons (f_L-1_027, f_L-1_038) are drawn 3.35 x 1.00 m with their ten chairs as separate
    drawn pieces (f_L-1_028..037, f_L-1_039..048; read from results/furniture/real04/building.json), not inside the
    table footprint: 1.00 m is not deeper than a real table (1.20 m), so there is no split, and 3.35 m is inside
    the product range (to 3.40 m), so there is no snap; the table and its ten chairs stay as drawn. No drawn table of
    the committed buildings is deeper than 1.20 m (``split_first`` stays empty). The same table drawn WITH its chairs
    inside the footprint (3.35 x 2.20 m) is split first and keeps its chairs (round 2 snapped it to a 1.00 m deep
    product first, which erased them)."""
    from wenart.blender import modules as MOD

    path = ROOT / "results" / "furniture" / "real04" / "building.json"
    if not path.is_file():
        pytest.skip("no committed real04 building")
    drawn_building = json.loads(path.read_text(encoding="utf-8"))
    fitted = F.fit_building(copy.deepcopy(drawn_building), library, style_family="modern", mode="relaxed")
    assert fitted["project"]["size_snap"]["on"] is True and "split_first" not in fitted["project"]["size_snap"]
    before = {f["id"]: f for f in drawn_building["furniture"]}
    after = {f["id"]: f for f in fitted["furniture"]}
    for tid, chairs in (("f_L-1_027", [f"f_L-1_0{n}" for n in range(28, 38)]),
                        ("f_L-1_038", [f"f_L-1_0{n}" for n in range(39, 49)])):
        t = after[tid]
        assert before[tid]["footprint"]["size"] == [3.35, 1.0] and t["footprint"] == before[tid]["footprint"]
        assert "size_snap" not in t and "adjusted_by_ai" not in t and "drawn_footprint" not in t
        assert t["asset"]["method"] in ("library", "module", "parametric")
        assert not (t["asset"].get("module_plan") or {}).get("split")                       # no chairs in the box
        room_chairs = sorted(f["id"] for f in fitted["furniture"] if f["room_id"] == t["room_id"] and f["type"] == "chair")
        assert room_chairs == chairs                                                         # the ten drawn chairs
        for cid in chairs:
            c = after[cid]
            assert c["source"] == "from_documents" and c.get("build") is not False and c["asset"]["method"] != "none"
            assert c["footprint"]["center"] == before[cid]["footprint"]["center"]
    # the same table drawn with its chairs inside: split first, the chairs kept, nothing snapped (3.35 m is a product)
    deep = drawn("table_dining", 3.35, 2.2, "f_L-1_027", height=0.75)
    one = F.fit_building({"furniture": [deep]}, library, style_family="modern", mode="relaxed")
    s = one["furniture"][0]
    split = s["asset"]["module_plan"]["split"]
    per_side = int((3.35 - 0.30 + 1e-9) // MOD.CHAIR_PITCH_M)
    assert one["project"]["size_snap"]["split_first"] == ["f_L-1_027"] and "size_snap" not in s
    assert s["footprint"] == deep["footprint"] and s["drawn_footprint"] == deep["footprint"]
    assert s["adjusted_by_ai"]["rule"] == F.SPLIT_RULE and split["chairs"] == 2 * per_side == 10
    assert split["table_m"] == [3.35, MOD.TABLE_DEPTH_RANGE_M[1]] and "with 10 chairs" in s["adjusted_by_ai"]["reason"]


def test_a_split_table_whose_table_part_is_too_long_snaps_only_the_table_part(library):
    """Build round 3 item 2: a drawn 3.80 x 1.80 m footprint holds a 3.80 x 0.80 m table and its chairs; the table
    part is 12 % longer than the longest product (3.40 m), so the snap takes the nearest real product's width
    (3.00 m) while the drawn depth stays (it holds the chairs); the plan is made again on the snapped footprint (8
    chairs), the label keeps ``rule: module_split`` with both rules and says what is built; a second fit changes
    nothing more."""
    deep = drawn("table_dining", 3.8, 1.8, "f_L0_t3", height=0.75)
    before = {"furniture": [deep]}
    fitted = F.fit_building(copy.deepcopy(before), library, style_family="modern", mode="relaxed")
    t = fitted["furniture"][0]
    assert fitted["project"]["size_snap"]["split_first"] == ["f_L0_t3"]
    assert t["footprint"]["size"] == [3.0, 1.8] and t["footprint"]["center"] == deep["footprint"]["center"]
    assert t["drawn_footprint"] == deep["footprint"] and t["drawn_type"] == "table_dining"
    snap = t["size_snap"]
    assert snap["part"] == [3.8, 0.8] and snap["drawn"][:2] == [3.8, 1.8] and snap["snapped"][:2] == [3.0, 1.8]
    assert "3.00 x 1.00" in snap["product"]
    label = t["adjusted_by_ai"]
    assert label["rule"] == F.SPLIT_RULE and label["rules"] == [F.SPLIT_RULE, F.SNAP_RULE]
    assert label["changed"]["footprint"] == deep["footprint"]
    split = t["asset"]["module_plan"]["split"]
    assert label["split"] == split and split["table_m"] == [3.0, 0.8] and split["chairs"] == 8
    assert label["reason"].startswith("module split, then the size snap of the table part")
    assert "built as a 3.00 x 0.80 m table with 8 chairs" in label["reason"] and "drawn 3.80 x 1.80 m" in label["reason"]
    # review of round 3: the fit CLI's own check accepts the split-then-snap result (it raised "a module split must
    # not change the footprint" on it) and still refuses a part snap that touches the drawn depth
    F.assert_only_assets_changed(before, fitted)
    broken = copy.deepcopy(fitted)
    broken["furniture"][0]["footprint"]["size"] = [3.0, 1.0]
    broken["furniture"][0]["size_snap"]["snapped"] = [3.0, 1.0]
    with pytest.raises(AssertionError, match="width only"):
        F.assert_only_assets_changed(before, broken)
    again = F.fit_building(copy.deepcopy(fitted), library, style_family="modern", mode="relaxed")
    a = again["furniture"][0]
    assert a["footprint"] == t["footprint"] and a["size_snap"] == snap and a["adjusted_by_ai"] == label
    F.assert_only_assets_changed(fitted, again)
    # with the snap off (keep_size) nothing is snapped: the module builder splits the drawn box as it is
    kept = F.fit_building(copy.deepcopy(before), library, style_family="modern", mode="relaxed", snap=False)
    k = kept["furniture"][0]
    assert k["footprint"] == deep["footprint"] and "size_snap" not in k and k["adjusted_by_ai"]["rule"] == F.SPLIT_RULE


def test_a_split_table_is_built_by_its_module_plan_even_when_a_library_table_would_fit(library, monkeypatch):
    """Review of build round 3 item 2: the split decides. A drawn 1.6 x 1.6 m table footprint holds a 1.6 x 0.8 m
    table and its chairs (module plan split); when a library table would fit the full footprint (a square model
    scaled to the drawn width, e.g. from a later catalogue: today's has none, so the fit's library step is stubbed),
    the piece is still built by the module plan, the label names the chairs, the library pick is logged
    (``split_over``, ladder ``not used``) and the fit CLI's own check passes."""
    deep = drawn("table_dining", 1.6, 1.6, "f_L0_sq", height=0.75)
    real = F.fit_piece

    def library_first(piece, *args, **kwargs):
        if piece["id"] == "f_L0_sq":
            return {"method": "library", "asset_id": "lib_square_table", "library": "abo", "scaling": "uniform",
                    "bbox_m": [1.6, 1.6, 0.75], "licence": "CC-BY-4.0", "ladder": [F._step("library", "used x")]}
        return real(piece, *args, **kwargs)

    monkeypatch.setattr(F, "fit_piece", library_first)
    before = {"furniture": [deep]}
    fitted = F.fit_building(copy.deepcopy(before), library, style_family="modern", mode="relaxed")
    t = fitted["furniture"][0]
    assert fitted["project"]["size_snap"]["split_first"] == ["f_L0_sq"]
    assert t["asset"]["method"] == "module" and t["asset"]["module_plan"]["split"]["chairs"] >= 2
    assert t["asset"]["split_over"] == "lib_square_table"
    assert [s["result"] for s in t["asset"]["ladder"]][-2:] == ["not used: lib_square_table", "used table_long"]
    assert t["adjusted_by_ai"]["rule"] == F.SPLIT_RULE and t["footprint"] == deep["footprint"]
    F.assert_only_assets_changed(before, fitted)
    # a long table drawn turned (its depth the long side) is not split first: modules.plan_table_long reads size[1]
    # as the depth without an orientation check, so it would take a 2.40 m table for a 1.00 m one with 2 chairs
    turned = drawn("table_dining", 1.0, 2.4, "f_L0_tt", height=0.75)
    assert F.module_plan_for(turned)[0]["split"] and F.split_plan_first(turned) is None
    assert F.apply_split_then_snap(copy.deepcopy(turned)) is None
    # a piece the split did not label keeps what the fit picked
    plain = drawn("table_dining", 1.6, 0.9, "f_L0_sq", height=0.75)
    assert F.fit_building({"furniture": [plain]}, library, mode="relaxed")["furniture"][0]["asset"]["method"] == "library"


def test_module_plan_for_guards_the_import_and_a_builder_error(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def no_modules(name, *args, **kwargs):
        if name == "wenart.blender.modules" or (name == "wenart.blender" and "modules" in (args[2] or ())):
            raise ImportError("mocked away")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_modules)
    plan, why = F.module_plan_for(drawn("table_dining", 3.35, 1.0, "f"))
    assert plan is None and why.startswith("no module builder (wenart.blender.modules not importable")
    monkeypatch.setattr(builtins, "__import__", real_import)
    assert F.module_plan_for(drawn("chair", 0.5, 0.5, "f"))[0] is None               # no builder for the type


# --------------------------------------------------------------------------
# 4b. Build round 2: the HSSD layer as a library source (docs/milestone13.md §12 D2, §13.2 row hssd.py)
# --------------------------------------------------------------------------

def hssd_entry():
    """An HSSD catalogue entry as pod P2 writes it (``growth_entries.hssd_entry`` on fake metadata: a 1.96 x 0.92 m
    sofa measured at real size, the candidate record of ``wenart.assets.hssd``)."""
    from wenart.assets import hssd as H
    from wenart.assets.audit import growth_entries as GE

    hid = "a" * 40
    cand = {"id": H.UID_PREFIX + hid, "hssd_id": hid, "type": "sofa", "kind": "furniture",
            "title": "Taylor 76'' Upholstered Sofa", "dims_m": [1.96, 0.92, 0.86], "path": H.object_path(hid),
            "synset": "sofa.n.01", "found_in": "living", "multi": False, "articulated": False, "bin": [2.0, 0.9],
            "demand": {"type": "sofa", "w": 2.0, "d": 0.9}, "projects": ["real02"], "fits_caps": True}
    m = {"bbox_model_m": [1.96, 0.92, 0.86], "bbox_min_m": [-0.98, -0.46, 0.0], "bbox_max_m": [0.98, 0.46, 0.86],
         "triangles": 12000, "vertices": 7000, "info": {"textured": True, "vertex_colours": False}, "stats": None,
         "pbr": {"base_colour": True, "metallic_roughness": True, "normal": False, "occlusion": False,
                 "emissive": False, "materials": 2, "images": 2}}
    return GE.hssd_entry(cand, m, "0" * 64, "2026-10-15T00:00:00Z", pbr=m["pbr"])


def test_an_hssd_entry_validates_and_is_a_relaxed_mode_candidate_only():
    from wenart.assets import hssd as H
    from wenart.blender import furniture as BF

    e = hssd_entry()
    assert "hssd" in C.SOURCES and "hssd" in C.LIBRARY_SOURCES
    assert C.SOURCE_LICENCES["hssd"] == (H.LICENCE,) == ("CC-BY-NC-4.0",) and C.LICENCE_DECLARED_BY["hssd"] == "publisher"
    assert e["source"] == "hssd" and e["licence"] == "CC-BY-NC-4.0" and e["licence_flag"] == "non_commercial"
    C.validate({"entries": [e]}, complete=False)                       # the validator takes the CC BY credit fields
    assert C.licence_flag_of(e) == "non_commercial" and C.commercial_safe(e) is False
    assert C.licence_fields(e)["licence_declared_by"] == "publisher" and C.licence_fields(e)["commercial_safe"] is False
    # P2 writes the entry with audit pending: no mode uses it until the audit decides (CLAUDE.md library rules)
    assert e["audit"]["status"] == "pending" and not C.usable(e, "relaxed") and "pending" in C.unusable_reason(e, "relaxed")
    e["audit"] = dict(e["audit"], status="keep")
    assert not C.usable(e, "commercial") and C.usable(e, "relaxed")
    assert "relaxed mode only" in C.unusable_reason(e, "commercial") and C.unusable_reason(e, "relaxed") is None
    # the validator refuses what the dataset does not allow: another licence text, a missing credit field, a wrong flag
    for bad in (dict(e, licence="CC-BY-4.0", licence_flag="none", commercial_safe=True),
                dict(e, attribution=""), dict(e, licence_flag="none", commercial_safe=True),
                dict(e, licence_declared_by="uploader", source="abo")):
        with pytest.raises(C.CatalogError):
            C.validate({"entries": [bad]}, complete=False)
    # the fit: excluded in commercial mode with the reason, the model in relaxed mode with its flags; ranked after
    # Poly Haven and before GSO
    sofa = drawn("sofa", 2.0, 0.9, "f_L0_001")
    commercial = F.fit_piece(sofa, FakeCatalog([e]), mode="commercial")
    assert commercial["method"] != "library" and any(x["id"] == e["id"] and "relaxed mode only" in x["reason"]
                                                     for x in commercial["excluded"])
    relaxed = F.fit_piece(sofa, FakeCatalog([e]), mode="relaxed")
    assert relaxed["method"] == "library" and relaxed["library"] == "hssd" and relaxed["asset_id"] == e["id"]
    assert relaxed["licence"] == "CC-BY-NC-4.0" and relaxed["licence_flag"] == "non_commercial"
    assert relaxed["commercial_safe"] is False and relaxed["licence_mode"] == "relaxed" and relaxed["scaling"] == "uniform"
    assert relaxed["glb"] == f"models/hssd/{e['id']}.glb" and relaxed["attribution"] == e["attribution"]
    assert F.SOURCE_ORDER.index("hssd") == 2 and F.source_rank(e) < F.source_rank({"source": "gso"})
    # the scene builder's gate takes the fitted asset (its flag and credit line travel with it)
    assert BF.licence_refusal(relaxed) is None and BF.MODEL_LICENCES["hssd"] == C.SOURCE_LICENCES["hssd"]
    # a building in relaxed mode carries it, flagged in the report
    fitted = F.fit_building({"project": {"licence_mode": "relaxed"}, "furniture": [sofa]}, FakeCatalog([e]))
    assert fitted["furniture"][0]["asset"]["asset_id"] == e["id"]
    report = F.fit_report(fitted)
    assert e["id"] in report and "non_commercial" in report


# --------------------------------------------------------------------------
# 5. The ranking (K2): uniform scale, no wood re-sort, preferences, tie-breaks, pins, diversity, fabric colour
# --------------------------------------------------------------------------

def test_uniform_scale_to_the_drawn_width():
    entry = model("m", "sofa", 2.0, 0.8, 0.8)
    assert F.scale_for(entry, 2.2, 0.9) == ([1.1, 1.1, 1.1], 1.0227) and F.fitted_depth(entry, 2.2) == 0.88
    fit = F.fit_piece(piece("sofa", 2.2, 0.9), FakeCatalog([entry]))
    assert fit["fit_scale"] == [1.1, 1.1, 1.1] and fit["bbox_m"] == [2.2, 0.88, 0.88] and fit["depth_abs_m"] == -0.02
    assert fit["scaling"] == "uniform" and fit["candidates"][0]["depth_m"] == 0.88
    assert F.NON_UNIFORM_CAP == 1.10 and F.UNIFORM_RANGE == (0.85, 1.20) and F.HEIGHT_TOLERANCE == 0.15


def test_the_wood_resort_is_gone_and_the_design_is_a_preference():
    wood_slot = [{"index": 0, "name": "w", "material": "wood", "separable": True, "share": 0.5, "textured": True}]
    real = model("real", "sofa", 2.0, 0.9, 0.8, real_product=True)
    woody = model("woody", "sofa", 2.0 / 1.08, 0.9 / 1.08, 0.8, recolourable_wood=True, material_slots=wood_slot)
    design = {"wood": "wood_veneer_oak_light"}
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([woody, real]), design=design)
    assert fit["asset_id"] == "abo_real" and fit["ranking"]["rank"] == 1       # Milestone 12 put abo_woody first
    alone = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([woody]), design=design)
    assert alone["asset_id"] == "abo_woody" and "wood" in alone["recolour"]       # the look still applies
    # material tags: a preference, no gate (Milestone 12: "no sofa model can show the design" -> a gap). Within one
    # size step the model that shows the design ranks first; when it fails the caps (here the real height: a 1.6 m
    # "sofa") the next one is taken and the asset says the design is not shown
    tagged = model("tagged", "sofa", 2.0, 0.9, 1.6, material_tags=["fabric"])
    plain = model("plain", "sofa", 2.0, 0.9, 0.8)                                       # never judged
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([plain, tagged]), design={"material_tags": ["fabric"]})
    assert fit["asset_id"] == "abo_plain" and fit["design_not_shown"] == {"material_tags": ["fabric"]}
    assert fit["design_not_shown_why"].startswith("no judged material tags")
    assert [c["id"] for c in fit["candidates"]] == ["abo_tagged", "abo_plain"]       # the tagged one ranked first
    assert [c["design_pref"] for c in fit["candidates"]] == [0, 1]
    assert [c["height_ok"] for c in fit["candidates"]] == [False, True]
    assert next(x for x in fit["excluded"] if x["id"] == "abo_plain")["preference"] is True
    # the real-size step comes before the preference: an exact plain model beats a tagged one two steps off
    wide = model("wide", "sofa", 2.0 / 0.9, 0.9 / 0.9, 0.8, material_tags=["fabric"])
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([wide, plain]), design={"material_tags": ["fabric"]})
    assert fit["asset_id"] == "abo_plain" and [c["id"] for c in fit["candidates"]] == ["abo_plain"]
    assert F.rank_key(plain, 2.0, 0.9, None, {"abo_plain": 1})[2:5] == (0, 1, 1)
    assert F.rank_key(wide, 2.0, 0.9, None, {})[2:5] == (2, 1, 0)
    both = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([plain, model("tagged2", "sofa", 2.0, 0.9, 0.8,
                                                                           material_tags=["fabric"])]),
                       design={"material_tags": ["fabric"]})
    assert both["asset_id"] == "abo_tagged2" and "design_not_shown" not in both and both["material_tags_asked"] == ["fabric"]


def test_tie_breaks_audit_vision_quality_texture_maps_and_faces_never_gates():
    base = dict(real_product=True)
    plain = model("plain", "sofa", 2.0, 0.9, 0.8, audit={"status": "keep", "vision": {"quality": 2}}, **base)
    fine = model("fine", "sofa", 2.0, 0.9, 0.8, audit={"status": "keep", "vision_quality": 4}, **base)
    assert F.vision_quality_of(plain) == 2.0 and F.vision_quality_of(fine) == 4.0 and F.vision_quality_of({}) is None
    assert [e["id"] for e in F.rank_candidates([plain, fine], 2.0, 0.9)] == ["abo_fine", "abo_plain"]
    pbr = model("pbr", "sofa", 2.0, 0.9, 0.8, texture_maps={"base_colour": True, "normal": True, "roughness": True}, **base)
    flat = model("flat", "sofa", 2.0, 0.9, 0.8, textured=False, **base)
    colour = model("colour", "sofa", 2.0, 0.9, 0.8, textured=True, **base)
    assert [F.maps_rank(e) for e in (pbr, colour, flat, plain)] == [0, 1, 2, 1]
    assert [e["id"] for e in F.rank_candidates([flat, colour, pbr], 2.0, 0.9)] == ["abo_pbr", "abo_colour", "abo_flat"]
    low = model("low", "sofa", 2.0, 0.9, 0.8, polycount=1200, **base)
    rich = model("rich", "sofa", 2.0, 0.9, 0.8, polycount=24000, **base)
    assert [F.faces_rank(e) for e in (rich, plain, low)] == [0, 1, 2]
    assert [e["id"] for e in F.rank_candidates([low, rich], 2.0, 0.9)] == ["abo_rich", "abo_low"]
    # tie-breaks, never gates (decision 1a of 11 Oct 2026): alone, the plain low-poly flat model is taken
    worst = model("worst", "sofa", 2.0, 0.9, 0.8, polycount=900, textured=False,
                  audit={"status": "keep", "vision": {"quality": 1}})
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([worst]))
    assert fit["asset_id"] == "abo_worst" and fit["faces"] == 900 and fit["texture_maps"] == {"base_colour": False}
    assert "audit vision quality 1" in fit["ranking"]["reasons"] and "faces 900" in fit["ranking"]["reasons"]
    # the real size step and a real product still come first (the Milestone 8 / 12 order)
    better_size = model("size", "sofa", 2.0, 0.9, 0.8, audit={"status": "keep", "vision": {"quality": 2}})
    assert F.rank_candidates([fine, dict(better_size, bbox_m=[2.2, 0.99, 0.88], bbox_model_m=[2.2, 0.99, 0.88])],
                             2.0, 0.9)[0]["id"] == "abo_fine"
    assert "vision quality" in F.RANKING_RULE and "faces" in F.RANKING_RULE and "diversity" in F.RANKING_RULE


def test_pins_skip_the_style_filter_but_not_the_caps_or_the_licence():
    classic = model("classic", "sofa", 2.0, 0.9, 0.8, styles=("classic",))
    scandi = model("scandi", "sofa", 2.1, 0.92, 0.8, styles=("scandinavian",))
    big = model("big", "sofa", 3.0, 0.9, 0.8, styles=("scandinavian",))
    gen = model("sofa_x", "sofa", 2.0, 0.9, 0.8, source="generated", styles=("scandinavian",),
                generated={"prompt": "p", "image_sha256": "cd" * 32, "model": "microsoft/TRELLIS.2-4B",
                           "revision": "r", "seed": 1})
    cat = FakeCatalog([classic, scandi, big, gen])
    plain = F.fit_piece(piece("sofa", 2.0, 0.9), cat, style_family="scandinavian")
    assert plain["asset_id"] == "abo_scandi" and "pinned" not in plain
    pinned = F.fit_piece(dict(piece("sofa", 2.0, 0.9), asset_pin="abo_classic"), cat, style_family="scandinavian")
    assert pinned["asset_id"] == "abo_classic" and pinned["pinned"] == "abo_classic"
    assert pinned["pin_skips_style"] is True and pinned["style_family"] == "scandinavian"
    refused = F.fit_piece(dict(piece("sofa", 2.0, 0.9), asset_pin="abo_big"), cat, style_family="scandinavian")
    assert refused["asset_id"] == "abo_scandi" and refused["pin_refused"] == "abo_big: fails the fit rules (caps, height)"
    nc = F.fit_piece(dict(piece("sofa", 2.0, 0.9), asset_pin=gen["id"]), cat, style_family="scandinavian")
    assert nc["asset_id"] == "abo_scandi" and "tool_nc" in nc["pin_refused"] and "commercial mode" in nc["pin_refused"]
    ok = F.fit_piece(dict(piece("sofa", 2.0, 0.9), asset_pin=gen["id"]), cat, style_family="scandinavian", mode="relaxed")
    assert ok["pinned"] == gen["id"] and ok["licence_flag"] == "tool_nc" and ok["commercial_safe"] is False
    unknown = F.fit_piece(dict(piece("sofa", 2.0, 0.9), asset_pin="abo_nope"), cat, style_family="scandinavian")
    assert unknown["pin_refused"] == "abo_nope: not a sofa model of the catalogue"


def test_diversity_penalty_per_room_and_per_project_keeps_sets_together():
    assert (F.ROOM_REUSE_MAX, F.ROOM_REUSE_STEPS, F.PROJECT_REUSE_STEP) == (2, 4, 1)
    assert set(F.SET_TYPES) == {"chair", "bar_stool", "office_chair", "nightstand", "side_table"}
    used = {"project": {"a": 3}, "room": {"a": 2}, "type": "sofa"}
    assert F.diversity_steps("a", used) == 1 + 4 and F.diversity_steps("b", used) == 0 and F.diversity_steps("a", None) == 0
    assert F.diversity_steps("a", dict(used, type="chair")) == 1                 # a set: no room penalty
    assert F.diversity_steps("a", {"project": {"a": 5}, "room": {}}) == 5
    a = model("a", "sofa", 2.0, 0.9, 0.8)
    b = model("b", "sofa", 2.0, 0.9, 0.8)
    cat = FakeCatalog([a, b])
    rooms = {"r1": 3, "r2": 2, "r3": 1}
    building = {"furniture": [dict(piece("sofa", 2.0, 0.9, pid=f"f_{r}_{i}"), room_id=r)
                              for r, n in rooms.items() for i in range(n)]}
    fitted = F.fit_building(building, cat)
    picks = [(p["room_id"], p["asset"]["asset_id"]) for p in fitted["furniture"]]
    assert picks == [("r1", "abo_a"), ("r1", "abo_a"), ("r1", "abo_b"),      # the third use in a room: the other
                     ("r2", "abo_b"), ("r2", "abo_b"),                       # b used once elsewhere, a twice
                     ("r3", "abo_a")]                                        # a 2 elsewhere, b 3 elsewhere
    third = fitted["furniture"][2]["asset"]
    assert third["candidates"][0]["id"] == "abo_b" and third["candidates"][0]["diversity_steps"] == 0
    second_room = [p["asset"]["candidates"][0]["diversity_steps"] for p in fitted["furniture"][3:5]]
    assert second_room == [1, 1]                                            # b: one use in another room, both times
    assert "diversity penalty 1 step(s) (used before in the room or project)" in fitted["furniture"][3]["asset"]["ranking"]["reasons"]
    # a matched set: six chairs round one table take one model; the next room's set takes the other
    c1 = model("c1", "chair", 0.5, 0.5, 0.9)
    c2 = model("c2", "chair", 0.5, 0.5, 0.9)
    chairs = {"furniture": [dict(piece("chair", 0.5, 0.5, pid=f"f_{r}_{i}"), room_id=r)
                            for r in ("r1", "r2", "r3") for i in range(6)]}
    fitted = F.fit_building(chairs, FakeCatalog([c1, c2]))
    by_room = {}
    for p in fitted["furniture"]:
        by_room.setdefault(p["room_id"], set()).add(p["asset"]["asset_id"])
    assert by_room == {"r1": {"abo_c1"}, "r2": {"abo_c2"}, "r3": {"abo_c1"}}
    # a penalty, never a gate: with one model every piece gets it
    only = F.fit_building(building, FakeCatalog([a]))
    assert {p["asset"]["asset_id"] for p in only["furniture"]} == {"abo_a"}
    assert only["furniture"][-1]["asset"]["candidates"][0]["diversity_steps"] == 5
    assert "diversity penalty 5 step(s)" in " ".join(only["furniture"][-1]["asset"]["ranking"]["reasons"])
    # the penalty counts library uses only (a parametric piece uses no model)
    assert F.fit_building({"furniture": [piece("sofa", 2.0, 0.9)]}, FakeCatalog([]))["furniture"][0]["asset"]["method"] \
        == "parametric"


def test_the_fabric_colour_of_the_brief_reaches_the_asset():
    style = {"family": "modern", "furniture": {"wood": None, "fabric_colour": "beige", "accents": [],
                                               "by_type": {"sofa": {"fabric_colour": "light grey", "colour": None,
                                                                    "material_tags": ["fabric"]}}}}
    cat = FakeCatalog([model("sofa", "sofa", 2.0, 0.9, 0.8), model("chair", "armchair", 0.8, 0.8, 0.8),
                       model("table", "table_coffee", 1.0, 0.6, 0.4), model("bed", "bed_double", 1.6, 2.0, 1.0)])
    sofa = dict(piece("sofa", 2.0, 0.9, pid="f1"), design={"material_tags": ["fabric"]})     # the layout's design (B1)
    chair = piece("armchair", 0.8, 0.8, pid="f2")
    table = piece("table_coffee", 1.0, 0.6, pid="f3")
    bed = dict(piece("bed_double", 1.6, 2.0, pid="f4"), design={"fabric_colour": "navy"})
    fitted = F.fit_building({"furniture": [sofa, chair, table, bed]}, cat, style=style)
    s, c, t, b = (p["asset"] for p in fitted["furniture"])
    assert s["fabric_colour"] == "light grey" and s["fabric_colour_source"] == "style.json furniture.by_type.sofa"
    assert c["fabric_colour"] == "beige" and c["fabric_colour_source"] == "style.json furniture.fabric_colour"
    assert "fabric_colour" not in t
    assert b["fabric_colour"] == "navy" and b["fabric_colour_source"] == "furniture.design (layout stage)"
    assert F.fabric_colour_of(sofa, style) == ("light grey", "style.json furniture.by_type.sofa")
    assert F.fabric_colour_of(table, style) == (None, None) and F.fabric_colour_of(chair, None) == (None, None)
    assert F.design_of(sofa, style)["fabric_colour"] == "light grey"            # the fit's preference as well
    assert all(p["asset"]["method"] == "library" for p in fitted["furniture"])  # a colour is never a gate
    # the committed real02 style: "light grey fabric sofa" of the brief (0 of 18 upholstered pieces got it in M11)
    real02 = json.loads((ROOT / "results" / "furniture" / "real02" / "style.json").read_text(encoding="utf-8"))
    real02 = real02[0] if isinstance(real02, list) else real02
    assert F.fabric_colour_of(sofa, real02)[0] == "light grey"


# --------------------------------------------------------------------------
# 6. The CLI: --licence-mode and --project
# --------------------------------------------------------------------------

def test_cli_licence_mode_and_project_flags(tmp_path, monkeypatch, capsys):
    from wenart.furniture.__main__ import main as furniture_main

    monkeypatch.delenv(C.LICENCE_MODE_ENV, raising=False)
    src = tmp_path / "building.json"
    B.save(load_truth("synthetic-01"), src)
    out = tmp_path / "building_fitted.json"
    assert furniture_main(["fit", str(src), "--out", str(out)]) == 0
    assert "licence mode: commercial" in capsys.readouterr().out
    assert B.load(out)["project"]["licence_mode"] == "commercial"
    assert furniture_main(["fit", str(src), "--out", str(out), "--licence-mode", "relaxed"]) == 0
    fitted = B.load(out)
    assert fitted["project"]["licence_mode"] == "relaxed" and fitted["project"]["licence_mode_source"] == "given to the fit"
    project = tmp_path / "proj"
    project.mkdir()
    (project / "brief.yaml").write_text("library:\n  licence_mode: relaxed\nfurnished_rooms_keep_size: true\n",
                                        encoding="utf-8")
    assert furniture_main(["fit", str(src), "--out", str(out), "--project", str(project)]) == 0
    text = capsys.readouterr().out
    fitted = B.load(out)
    assert fitted["project"]["licence_mode"] == "relaxed" and fitted["project"]["licence_mode_source"] == \
        "brief library.licence_mode"
    assert fitted["project"]["size_snap"]["on"] is False and "size snap off" in text
    monkeypatch.setenv(C.LICENCE_MODE_ENV, "commercial")
    assert furniture_main(["fit", str(src), "--out", str(out), "--project", str(project)]) == 0
    assert B.load(out)["project"]["licence_mode"] == "commercial"
    assert furniture_main(["fit", str(src), "--out", str(out), "--project", str(project), "--licence-mode", "relaxed"]) == 0
    assert B.load(out)["project"]["licence_mode"] == "relaxed"
    with pytest.raises(SystemExit):
        furniture_main(["fit", str(src), "--out", str(out), "--licence-mode", "free"])
    assert F.project_dir_of({"project": {"source_folder": str(project)}}) == project
    assert F.project_dir_of({"project": {"source_folder": str(tmp_path / "gone")}}) is None
    assert F.project_dir_of({}, "x") == Path("x")
    # the licence-fields command runs the script on given files (idempotent on the committed ones)
    copy_path = tmp_path / "catalog.json"
    copy_path.write_bytes(C.CATALOG_PATH.read_bytes())
    assert furniture_main(["licence-fields", str(copy_path)]) == 0
    assert '"changed": 0' in capsys.readouterr().out
    assert furniture_main(["licence-fields", str(tmp_path / "nope.json")]) == 2


# --------------------------------------------------------------------------
# Fix round after P3 (16-17 Oct 2026): drawn sinks built into the kitchen runs, gaps for drawn stoves
# --------------------------------------------------------------------------

def _real04_kitchen(room="r_L-1_mutfak"):
    path = ROOT / "results" / "furniture" / "real04" / "building.json"
    if not path.is_file():
        pytest.skip("no committed real04 building")
    building = json.loads(path.read_text(encoding="utf-8"))
    return dict(building, furniture=[p for p in building["furniture"] if p.get("room_id") == room], decor=[])


def test_kitchen_built_ins_on_the_real04_kitchen():
    """P3's drawing: f_L-1_003 holds four sink_kitchen pieces at 100 %; only f_L-1_067 is built (the 0.51 x 0.11 m
    f_L-1_009 and the 0.35 x 0.44 m bowls f_L-1_081 / f_L-1_083 are build false), so it is the sink built in;
    f_L-1_002 holds the stove f_L-1_008 (98.6 %): a gap at its drawn span."""
    found = F.kitchen_built_ins(_real04_kitchen())
    assert found["sinks"] == {"f_L-1_067": "f_L-1_003"}
    assert found["hints"]["f_L-1_003"] == {"sink_pos_m": [1.4507, 10.2592], "sink_w_m": pytest.approx(0.7885, abs=1e-4),
                                           "sink_piece": "f_L-1_067"}
    assert found["hints"]["f_L-1_002"] == {"ranges": [{"id": "f_L-1_008", "type": "stove",
                                                       "x0_m": pytest.approx(-0.1531, abs=1e-4),
                                                       "x1_m": pytest.approx(0.5969, abs=1e-4)}]}
    assert set(found["hints"]) == {"f_L-1_002", "f_L-1_003"}                  # f_L-1_001 / 004 hold nothing


def test_the_fit_builds_the_drawn_sink_into_its_run_and_changes_only_assets(library):
    """The verifier's better fix: the hints reach the plan on a copy and live in ``asset.module_hints``; the sink's
    asset is ``built_in`` (method module, the run's asset id, by design, ours), its build, type and evidence stay;
    ``assert_only_assets_changed`` and ``FROZEN_KEYS`` hold; the stove keeps its own model."""
    building = _real04_kitchen()
    fitted = F.fit_building(copy.deepcopy(building), library, style_family="modern", mode="relaxed")
    F.assert_only_assets_changed(building, fitted)
    after = {p["id"]: p for p in fitted["furniture"]}
    assert not [p for p in fitted["furniture"] if "module_hints" in p or "built_in" in p]
    run = after["f_L-1_003"]["asset"]
    assert run["method"] == "module" and run["module_plan"]["cutouts"] == ["sink"]
    assert [b["id"] for b in run["module_plan"]["built_ins"]] == ["f_L-1_067"]
    assert run["module_hints"]["sink_piece"] == "f_L-1_067"
    sink = after["f_L-1_067"]
    a = sink["asset"]
    assert (a["method"], a["asset_id"], a["built_in"]) == ("module", "module:kitchen_counter:kitchen_run", "f_L-1_003")
    assert a["by_design"] and a["commercial_safe"] is True and a["licence_flag"] == "none" and a["licence"] == "n/a"
    assert [s["step"] for s in a["ladder"]] == ["library", "module"] and "library_gap" not in sink
    assert sink.get("build", True) is not False and sink["type"] == "sink_kitchen"
    assert sink["evidence"] == next(p for p in building["furniture"] if p["id"] == "f_L-1_067")["evidence"]
    for bowl in ("f_L-1_009", "f_L-1_081", "f_L-1_083"):                     # build false: not built, no built_in
        assert after[bowl]["asset"]["method"] == "none" and "built_in" not in after[bowl]["asset"]
    stove_run = after["f_L-1_002"]["asset"]["module_plan"]
    assert stove_run["gaps"][0]["id"] == "f_L-1_008" and stove_run["gaps"][0]["w_m"] == pytest.approx(0.75)
    assert after["f_L-1_008"]["asset"]["method"] in ("library", "parametric") and "built_in" not in after["f_L-1_008"]["asset"]
    report = F.fit_report(fitted)
    assert "## Kitchen runs" in report and "f_L-1_067 (sink_kitchen): built into the kitchen run f_L-1_003" in report
    assert "a 0.75 m gap for the drawn stove f_L-1_008" in report


def test_the_synthetic03_run_takes_its_sink_and_leaves_a_gap_for_its_stove(library):
    building = load_truth("synthetic-03")
    fitted = F.fit_building(copy.deepcopy(building), library, mode="commercial")
    F.assert_only_assets_changed(building, fitted)
    after = {p["id"]: p for p in fitted["furniture"]}
    plan = after["f_L0_007"]["asset"]["module_plan"]
    assert [b["id"] for b in plan["built_ins"]] == ["f_L0_008"] and [g["id"] for g in plan["gaps"]] == ["f_L0_009"]
    assert after["f_L0_008"]["asset"]["built_in"] == "f_L0_007"
    assert "built_in" not in after["f_L0_009"]["asset"]


def test_a_sink_beside_its_run_a_pinned_sink_and_a_run_without_modules_keep_the_sink_s_own_model(library, monkeypatch):
    run = drawn("kitchen_counter", 2.4, 0.6, "f_run", room="r_k", front=0.0, center=(0.0, 0.0), height=0.9)
    # the run lies along y (``drawn``: front 0 -> rotation 90), from y -1.2 to 1.2
    beside = drawn("sink_kitchen", 0.8, 0.5, "f_sink", room="r_k", front=0.0, center=(0.0, 1.7))
    inside = drawn("sink_kitchen", 0.8, 0.5, "f_sink", room="r_k", front=0.0, center=(0.0, -0.2))
    assert F.kitchen_built_ins({"furniture": [run, inside]})["sinks"] == {"f_sink": "f_run"}
    assert F.kitchen_built_ins({"furniture": [run, beside]}) == {"hints": {}, "sinks": {}}
    one = F.fit_building({"furniture": [copy.deepcopy(run), copy.deepcopy(beside)]}, library, mode="relaxed")
    assert "built_in" not in one["furniture"][1]["asset"] and "built_ins" not in one["furniture"][0]["asset"]["module_plan"]
    pinned = dict(inside, asset_pin="some_model")
    assert F.kitchen_built_ins({"furniture": [run, pinned]})["sinks"] == {}       # the agent's model wins
    other_room = dict(inside, room_id="r_other")
    assert F.kitchen_built_ins({"furniture": [run, other_room]})["sinks"] == {}
    # the run has no module plan (no module builder): the sink is fitted as before, never left out
    monkeypatch.setattr(F, "module_plan_for", lambda piece, style=None: (None, "mocked: no module builder"))
    two = F.fit_building({"furniture": [copy.deepcopy(run), copy.deepcopy(inside)]}, library, mode="relaxed")
    sink = two["furniture"][1]["asset"]
    assert "built_in" not in sink and sink["method"] in ("library", "parametric")


def test_the_build_loop_skips_a_built_in_only_when_its_run_holds_it():
    """furniture.built_in_ids: the scene does not build a sink its run builds in; when the run's plan does not hold
    it (the agent refitted the run without the hints), the sink is built on its own."""
    from wenart.blender import furniture as BF

    plan = {"builder": "kitchen_run", "modules": [{"kind": "plinth"}], "built_ins": [{"id": "f_sink", "kind": "sink"}]}
    run = {"id": "f_run", "type": "kitchen_counter", "asset": {"method": "module", "module_plan": plan}}
    sink = {"id": "f_sink", "type": "sink_kitchen", "asset": {"method": "module", "built_in": "f_run"}}
    assert BF.built_in_ids([run, sink]) == {"f_sink": "f_run"}
    lost = dict(run, asset={"method": "module", "module_plan": dict(plan, built_ins=[])})
    assert BF.built_in_ids([lost, sink]) == {}
    assert BF.built_in_ids([dict(run, build=False), sink]) == {}
    assert BF.built_in_ids([sink]) == {}
    assert BF.built_in_ids([run, dict(sink, asset={"method": "library"})]) == {}
