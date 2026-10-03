"""Catalogue and fitting (wenart/furniture/catalog.py, fit.py, Milestone 4 section 1).

Catalogue: every entry complete (bbox, frame fields, CC0, Poly Haven), every
furniture type of the schema covered by a library or a parametric entry,
malformed catalogues refused. Milestone 7 (docs/milestone7.md §6.3, §6.6):
styles and style notes, beds with a mattress only, the style filter of
refit, CC BY / Objaverse entries and the merge of catalog_objaverse.json. Fitting: aspect-closest candidate, the 15 %
non-uniform cap moves to the next candidate or the parametric fallback,
the three synthetic buildings (truth JSON of all three, pipeline output of
the two vector projects) get a fit on every piece with the footprint and
every other field byte-identical, the fitted JSON validates, the report
lists every fallback and the licence of every library fit. CLI offline.
"""
import copy
import json
from pathlib import Path

import pytest

from wenart import building as B
from wenart.furniture import catalog as C
from wenart.furniture import fit as F
from wenart.furniture.__main__ import main as furniture_main
from wenart.ingest.pipeline import build_project
from wenart.style import vocabulary as V

from conftest import PROJECTS, SYNTHETIC, load_truth

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_TYPES = set(B.load_schema()["$defs"]["furniture"]["properties"]["type"]["enum"])


@pytest.fixture(scope="module")
def catalog():
    return C.load()


@pytest.fixture(scope="module")
def buildings(tmp_path_factory):
    """(name, building) for the truth of every synthetic project plus the pipeline output of 01 and 03."""
    out = tmp_path_factory.mktemp("fit_outputs")
    result = [(name + " (truth)", load_truth(name)) for name in SYNTHETIC]
    for name in ("synthetic-01", "synthetic-03"):
        built = build_project(PROJECTS / name, out / name)
        assert built["status"] == "ok" and built["furniture"]
        result.append((name + " (pipeline)", built))
    return result


# --------------------------------------------------------------------------
# Catalogue
# --------------------------------------------------------------------------

def test_catalog_covers_every_schema_type(catalog):
    assert set(C.FURNITURE_TYPES) == SCHEMA_TYPES
    assert set(catalog.types()) == SCHEMA_TYPES
    assert len(catalog.models) >= 25 and len(catalog.parametric_types) >= 8
    for ftype in ("sofa", "armchair", "chair", "table_dining", "table_coffee", "desk", "bed_double",
                  "nightstand", "bookshelf", "tv_unit", "dresser"):
        assert 1 <= len(catalog.candidates(ftype)) <= 3, ftype
    # Milestone 7: old_bed_frame (no mattress) is gone, so bed_single is parametric until Objaverse adds one; the
    # four documented-only types are parametric (the stair is built from the drawn flights).
    for ftype in ("toilet", "washbasin", "shower", "bathtub", "fridge", "washing_machine", "kitchen_counter",
                  "kitchen_island", "sink_kitchen", "wardrobe", "unknown", "bed_single", "stair", "side_table",
                  "floor_lamp", "potted_plant"):
        assert ftype in catalog.parametric_types and catalog.candidates(ftype) == []
    assert catalog.entry("old_bed_frame") is None
    assert len(set(catalog.ids())) == len(catalog.ids())


def test_catalog_entries_are_complete(catalog):
    for entry in [e for e in catalog.models + catalog.decor if e["source"] == "polyhaven"]:
        for key in C.REQUIRED_MODEL_FIELDS:
            assert key in entry, (entry.get("id"), key)
        assert entry["source"] == "polyhaven" and entry["licence"] == "CC0"
        assert entry["url"] == f"https://polyhaven.com/a/{entry['id']}"
        assert entry["gltf"] == f"models/{entry['id']}/{entry['id']}_1k.gltf"
        assert all(0.05 < v < 3.0 for v in entry["bbox_m"]), entry["id"]
        assert entry["bbox_m"] == C.oriented_bbox(entry["bbox_model_m"], entry["front_axis"])
        assert entry["origin_offset"] == C.origin_offset(entry["bbox_min_m"], entry["bbox_max_m"])
        assert abs(entry["origin_offset"][2]) < 0.02, entry["id"]  # origin on the floor
        assert entry["front_axis_confidence"] in ("high", "medium", "low") and entry["front_axis_note"]
        assert entry["up_axis"] == "+Z" and entry["front_axis"] in C.AXES
        assert 0.2 < C.bbox_aspect(entry) < 6.0
    # low confidence is stated for every piece whose front cannot be read from the geometry
    low = {e["id"] for e in catalog.models if e["front_axis_confidence"] == "low"}
    assert {"wooden_table_02", "painted_wooden_table", "modern_coffee_table_02", "side_table_01"} <= low
    for entry in catalog.entries:
        if entry.get("parametric"):
            assert entry["reason"]


def test_catalog_validation_refuses_broken_files(catalog):
    data = copy.deepcopy(catalog.data)
    good = next(e for e in data["entries"] if not e.get("parametric"))
    broken = copy.deepcopy(data)
    broken["entries"][broken["entries"].index(good)]["licence"] = "CC-BY"
    with pytest.raises(C.CatalogError):
        C.validate(broken)
    broken = copy.deepcopy(data)
    del broken["entries"][broken["entries"].index(good)]["front_axis"]
    with pytest.raises(C.CatalogError):
        C.validate(broken)
    broken = copy.deepcopy(data)
    broken["entries"][broken["entries"].index(good)]["bbox_m"] = [9.0, 9.0, 9.0]
    with pytest.raises(C.CatalogError, match="does not match"):
        C.validate(broken)
    broken = copy.deepcopy(data)
    broken["entries"] = [e for e in broken["entries"] if e.get("type") != "toilet"]
    with pytest.raises(C.CatalogError, match="toilet"):
        C.validate(broken)
    broken = copy.deepcopy(data)
    broken["entries"].append({"type": "sofa", "parametric": True})
    with pytest.raises(C.CatalogError):
        C.validate(broken)


def test_frame_helpers():
    assert C.reorient_rotation_deg({"front_axis": "-Y"}) == 0.0
    assert C.reorient_rotation_deg({"front_axis": "+Y"}) == 180.0
    assert C.reorient_rotation_deg({"front_axis": "+X"}) == 270.0
    assert C.reorient_rotation_deg({"front_axis": "-X"}) == 90.0
    assert C.oriented_bbox([0.6, 1.2, 0.4], "-X") == [1.2, 0.6, 0.4]
    assert C.oriented_bbox([0.6, 1.2, 0.4], "+Y") == [0.6, 1.2, 0.4]
    assert C.origin_offset([-0.5, -0.2, 0.0], [0.5, 0.6, 1.0]) == [0.0, 0.2, 0.0]
    assert C.parametric_height("wardrobe") == 2.1 and C.parametric_height("weird") == 0.8


# --------------------------------------------------------------------------
# Fitting rule on a hand-made catalogue
# --------------------------------------------------------------------------

def _entry(asset_id, ftype, w, d, h, styles=("neutral",), **extra):
    return {"id": asset_id, "type": ftype, "source": "polyhaven", "licence": "CC0", "bbox_m": [w, d, h],
            "bbox_model_m": [w, d, h], "bbox_min_m": [-w / 2, -d / 2, 0.0], "bbox_max_m": [w / 2, d / 2, h],
            "front_axis": "-Y", "up_axis": "+Z", "origin_offset": [0.0, 0.0, 0.0], "front_axis_confidence": "high",
            "url": f"https://polyhaven.com/a/{asset_id}", "gltf": f"models/{asset_id}/{asset_id}_1k.gltf",
            "styles": list(styles), "style_note": "test entry", **extra}


def _piece(ftype, w, d, source="from_documents", pid="f_L0_001"):
    return {"id": pid, "level_id": "L0", "room_id": "r_L0_salon", "type": ftype, "type_raw": None, "source": source,
            "footprint": {"center": [1.0, 2.0], "size": [w, d], "rotation_deg": 90.0}, "front_deg": 0.0,
            "height": None, "asset": None, "status": "verified",
            "evidence": [{"file": "a.dxf", "method": "vector", "confidence": 1.0}]}


@pytest.fixture
def small_catalog():
    entries = [
        _entry("sofa_wide", "sofa", 2.0, 0.8, 0.8),      # aspect 2.5
        _entry("sofa_deep", "sofa", 1.6, 1.0, 0.8),      # aspect 1.6
        _entry("sofa_odd", "sofa", 3.0, 0.5, 0.8),       # aspect 6.0
        _entry("tv_long", "tv_unit", 2.4, 0.5, 0.6),     # aspect 4.8 -> fails the cap on 1.6 x 0.45
    ]
    entries += [{"type": t, "parametric": True, "reason": "test"} for t in C.FURNITURE_TYPES
                if t not in ("sofa", "tv_unit")]
    return C.Catalog({"entries": entries})


def test_fit_picks_the_aspect_closest_candidate(small_catalog):
    piece = _piece("sofa", 2.2, 0.9)
    before = json.dumps(piece, sort_keys=True)
    fit = F.fit_piece(piece, small_catalog)
    assert json.dumps(piece, sort_keys=True) == before  # pure
    assert fit["method"] == "library" and fit["asset_id"] == "sofa_wide" and fit["licence"] == fit["license"] == "CC0"
    assert fit["fit_scale"] == [1.1, 1.125, 1.1125]
    assert fit["bbox_m"] == [2.2, 0.9, 0.89]
    assert fit["gltf"] == "models/sofa_wide/sofa_wide_1k.gltf" and fit["rotation_fix_deg"] == 0.0
    assert [c["id"] for c in fit["candidates"]] == ["sofa_wide"]
    assert fit["candidates"][0]["accepted"] and fit["aspect_error"] == pytest.approx(0.0223, abs=1e-3)


def test_cap_moves_to_the_next_candidate_or_parametric(small_catalog):
    # 1.0 x 0.48 (aspect 2.08): sofa_wide is closest (2.5) but scales 0.5 / 0.6 -> 20 % non-uniform; sofa_deep
    # (1.6) scales 0.625 / 0.48 -> 30 %; sofa_odd (6.0) 0.333 / 0.96 -> way off -> parametric
    fit = F.fit_piece(_piece("sofa", 1.0, 0.48), small_catalog)
    assert fit["method"] == "parametric" and fit["asset_id"] == "parametric:sofa"
    assert fit["library"] == "parametric" and fit["licence"] == "n/a" and fit["fit_scale"] == [1.0, 1.0, 1.0]
    assert fit["bbox_m"] == F.parametric_box(_piece("sofa", 1.0, 0.48))     # the box Blender builds
    assert "no sofa candidate within 15 %" in fit["fallback_reason"]
    assert [c["id"] for c in fit["candidates"]] == ["sofa_wide", "sofa_deep", "sofa_odd"]
    assert not any(c["accepted"] for c in fit["candidates"])
    # 2.0 x 0.9 (aspect 2.22): sofa_wide first (2.5): 1.0 / 1.125 -> 12.5 % ok
    fit = F.fit_piece(_piece("sofa", 2.0, 0.9), small_catalog)
    assert fit["asset_id"] == "sofa_wide" and fit["method"] == "library"
    # 1.6 x 0.9 (aspect 1.78): sofa_deep closest (1.6): 1.0 / 0.9 -> 11 % ok
    fit = F.fit_piece(_piece("sofa", 1.6, 0.9), small_catalog)
    assert fit["asset_id"] == "sofa_deep"
    # 1.7 x 0.8 (aspect 2.125): sofa_wide (2.5) 0.85 / 1.0 -> 17.6 % fails; sofa_deep (1.6) 1.0625 / 0.8 -> 33 % fails
    fit = F.fit_piece(_piece("sofa", 1.7, 0.8), small_catalog)
    assert fit["method"] == "parametric" and fit["candidates"][0]["id"] == "sofa_wide"
    assert "closest: sofa_wide at 17." in fit["fallback_reason"]
    # a tighter cap is honoured
    assert F.fit_piece(_piece("sofa", 2.0, 0.9), small_catalog, cap=1.10)["method"] == "parametric"


def test_parametric_types_and_unknown(small_catalog):
    fit = F.fit_piece(_piece("toilet", 0.4, 0.7), small_catalog)
    assert fit["method"] == "parametric" and fit["bbox_m"] == F.parametric_box(_piece("toilet", 0.4, 0.7))
    assert fit["bbox_m"][:2] == [0.4, 0.7] and fit["bbox_m"][2] >= 0.4
    assert "parametric in the catalogue" in fit["fallback_reason"] and fit["candidates"] == []
    fit = F.fit_piece(_piece("unknown", 1.2, 0.5), small_catalog)
    assert fit["asset_id"] == "parametric:unknown" and fit["bbox_m"] == [1.2, 0.5, 0.8]
    fit = F.fit_piece(_piece("tv_unit", 1.6, 0.45), small_catalog)
    assert fit["method"] == "parametric" and fit["candidates"][0]["id"] == "tv_long"
    assert F.fit_piece(_piece("sofa", 0.0, 0.9), small_catalog)["method"] == "parametric"


def test_added_by_ai_pieces_get_a_fit_too(small_catalog):
    building = {"furniture": []}
    building["furniture"] = [_piece("sofa", 2.2, 0.9), _piece("sofa", 2.0, 0.9, source="added_by_ai", pid="f_L0_900")]
    fitted = F.fit_building(building, small_catalog)
    assert all(p["asset"]["method"] == "library" for p in fitted["furniture"])
    assert fitted["furniture"][1]["source"] == "added_by_ai"
    assert building["furniture"][0]["asset"] is None  # input untouched
    F.assert_only_assets_changed(building, fitted)
    fitted["furniture"][0]["footprint"]["size"] = [2.0, 0.9]
    with pytest.raises(AssertionError):
        F.assert_only_assets_changed(building, fitted)


# --------------------------------------------------------------------------
# The synthetic buildings
# --------------------------------------------------------------------------

def test_fit_synthetic_buildings(catalog, buildings):
    assert len(buildings) == len(SYNTHETIC) + 2
    for name, building in buildings:
        before = json.dumps(building, sort_keys=True)
        fitted = F.fit_building(building, catalog)
        assert json.dumps(building, sort_keys=True) == before, name  # input never modified
        assert len(fitted["furniture"]) == len(building["furniture"]) >= 10, name
        F.assert_only_assets_changed(building, fitted)
        for original, piece in zip(building["furniture"], fitted["furniture"]):
            asset = piece["asset"]
            assert asset and asset["method"] in ("library", "parametric"), (name, piece["id"])
            # byte-identical footprint and frozen fields
            assert json.dumps(piece["footprint"], sort_keys=True) == json.dumps(original["footprint"], sort_keys=True)
            for key in F.FROZEN_KEYS:
                assert json.dumps(piece.get(key), sort_keys=True) == json.dumps(original.get(key), sort_keys=True)
            assert asset["bbox_m"][0] == round(piece["footprint"]["size"][0], 4)
            assert asset["bbox_m"][1] == round(piece["footprint"]["size"][1], 4)
            if asset["method"] == "library":
                sx, sy, sz = asset["fit_scale"]
                assert max(sx, sy, sz) / min(sx, sy, sz) <= F.NON_UNIFORM_CAP + 1e-6, (name, piece["id"], asset)
                assert sz == pytest.approx((sx + sy) / 2, abs=1e-3)
                entry = catalog.entry(asset["asset_id"])
                assert asset["library"] == entry["source"] and asset["licence"] in C.SOURCE_LICENCES[entry["source"]]
                assert entry["type"] == piece["type"]
                assert asset.get("gltf", asset.get("glb")) == entry.get("gltf", entry.get("glb"))
                assert asset["style_family"] is None and asset["styles"] == entry["styles"]   # fit: no filter
                assert asset["bbox_m"][2] == pytest.approx(entry["bbox_m"][2] * sz, abs=1e-3)
            else:
                assert asset["fallback_reason"] and asset["licence"] == "n/a"
                assert piece["type"] in catalog.parametric_types or asset["candidates"]
        B.validate(fitted)
        methods = {p["asset"]["method"] for p in fitted["furniture"]}
        assert methods == {"library", "parametric"}, name  # sofas, beds, chairs fit; sanitary ware falls back
        library_types = {p["type"] for p in fitted["furniture"] if p["asset"]["method"] == "library"}
        assert {"sofa", "bed_double", "nightstand"} & library_types, name

        report = F.fit_report(fitted, title=name)
        assert "## Parametric fallbacks" in report and "## Library assets and licences" in report
        for piece in fitted["furniture"]:
            asset = piece["asset"]
            assert f"| {piece['id']} |" in report
            if asset["method"] == "parametric":
                assert f"- {piece['id']} ({piece['type']}): {asset['fallback_reason']}" in report
            else:
                assert f"- {asset['asset_id']} ({asset['library']}, {asset['licence']})" in report


def test_fit_is_deterministic(catalog):
    building = load_truth("synthetic-01")
    a = F.fit_building(building, catalog)
    b = F.fit_building(building, catalog)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


# --------------------------------------------------------------------------
# CLI (offline: the model fetcher is replaced)
# --------------------------------------------------------------------------

def test_cli_offline_falls_back_and_says_so(tmp_path, monkeypatch, capsys):
    from wenart.assets import models, web

    src = tmp_path / "building.json"
    B.save(load_truth("synthetic-01"), src)
    out = tmp_path / "building_fitted.json"

    def failing_fetch(asset_id, out_dir, size="1k", source="polyhaven", licence=None):
        raise web.NetworkError("blocked host (simulated)")

    monkeypatch.setattr(models, "fetch_model", failing_fetch)
    assert furniture_main(["fit", str(src), "--out", str(out), "--assets", str(tmp_path / "assets")]) == 0
    text = capsys.readouterr().out
    assert "download(s) failed" in text and "FAILED" in text
    fitted = B.load(out)
    assert all(p["asset"]["method"] == "parametric" for p in fitted["furniture"])
    assert any("download of" in p["asset"]["fallback_reason"] and "NetworkError" in p["asset"]["fallback_reason"]
               for p in fitted["furniture"])
    report = (tmp_path / "building_fitted_report.md").read_text(encoding="utf-8")
    assert "download of" in report and "parametric fallback" in report
    F.assert_only_assets_changed(load_truth("synthetic-01"), fitted)

    # with downloads working (fake), the library fits stay
    fetched = []
    monkeypatch.setattr(models, "fetch_model", lambda a, d, size="1k", source="polyhaven", licence=None: fetched.append(a))
    assert F.main([str(src), "--out", str(out), "--assets", str(tmp_path / "assets"), "--report", str(tmp_path / "r.md")]) == 0
    fitted = B.load(out)
    assert {p["asset"]["method"] for p in fitted["furniture"]} == {"library", "parametric"}
    assert sorted(set(fetched)) == sorted({p["asset"]["asset_id"] for p in fitted["furniture"]
                                           if p["asset"]["method"] == "library"})
    assert (tmp_path / "r.md").is_file()
    # no --assets: nothing downloaded, library fits recorded
    fetched.clear()
    assert F.main([str(src), "--out", str(out)]) == 0 and fetched == []
    assert furniture_main([]) == 2


def test_uniform_scale_cap_rejects_stretched_models():
    """A 1.57 m sofa model must not be stretched 1.4x onto a 2.2 m footprint."""
    from wenart.furniture import catalog as C, fit as F
    cat = C.load()
    piece = {"id": "f", "type": "sofa", "footprint": {"center": [0, 0], "size": [2.2, 0.9], "rotation_deg": 0}}
    asset = F.fit_piece(piece, cat)
    for t in asset["candidates"]:
        if t["accepted"]:
            assert F.UNIFORM_RANGE[0] <= t["mean_scale"] <= F.UNIFORM_RANGE[1]
    wide = F.fit_piece(piece, cat, uniform_range=(0.99, 1.01))
    assert wide["method"] == "parametric" and "mean scale" in wide["fallback_reason"]


def test_plants_get_a_library_model_and_cushions_stay_parametric(catalog):
    building = load_truth("synthetic-01")
    building["decor"] = [
        {"id": "dec_L0_001", "kind": "decor", "type": "plant", "level_id": "L0", "room_id": "r_L0_salon",
         "center": [0.25, 0.25], "rotation_deg": 0.0, "size": [0.4, 0.4], "asset": None, "host_id": None,
         "source": "added_by_ai", "method": "rule", "reason": "potted plant in a free corner"},
        {"id": "dec_L0_002", "kind": "decor", "type": "cushion", "level_id": "L0", "room_id": "r_L0_salon",
         "center": [1.0, 1.0], "rotation_deg": 0.0, "size": [0.45, 0.15], "asset": None, "host_id": "f_L0_001",
         "source": "added_by_ai", "method": "rule", "reason": "cushion"},
    ]
    fitted = F.fit_building(building, catalog)
    F.assert_only_assets_changed(building, fitted)
    plant, cushion = fitted["decor"]
    assert plant["asset"]["method"] == "library" and plant["asset"]["asset_id"].startswith("potted_plant")
    assert plant["asset"]["licence"] == "CC0" and plant["asset"]["gltf"].endswith(".gltf")
    assert plant["asset"]["bbox_m"][:2] == [0.4, 0.4] and plant["asset"]["target"] == "size"
    assert cushion["asset"] is None
    report = F.fit_report(fitted)
    assert "## Decor" in report and "plant: potted_plant" in report and "parametric by design" in report


def test_parametric_box_is_what_blender_builds():
    from wenart.blender import parametric as P
    bed = _piece("bed_double", 1.6, 2.0)
    fit = F.parametric_fit(bed, "test")
    assert fit["bbox_m"][:2] == [1.6, 2.0]
    assert fit["bbox_m"][2] == pytest.approx(P.parametric_bbox("bed_double", 1.6, 2.0, P.proxy_height("bed_double", None)[0])[2])
    assert fit["bbox_m"][2] > 0.5                                           # the headboard rises above the mattress
    tall = dict(_piece("wardrobe", 1.2, 0.6), height=2.4)
    assert F.parametric_fit(tall, "test")["bbox_m"][2] == pytest.approx(P.parametric_bbox("wardrobe", 1.2, 0.6, 2.4)[2])



# --------------------------------------------------------------------------
# Milestone 7: styles, mattresses, the refit style filter, CC BY / Objaverse (docs/milestone7.md §6.3, §6.6)
# --------------------------------------------------------------------------

def test_every_model_has_styles_a_note_and_beds_a_mattress(catalog):
    allowed = set(C.style_values())
    assert allowed == {name for name, _ in V.STYLE_FAMILIES} | {"neutral"}
    polyhaven = [e for e in catalog.models if e["source"] == "polyhaven"]
    assert len(polyhaven) == 30                                       # the 31 surveyed models minus old_bed_frame
    for e in polyhaven:
        assert e["styles"] and set(e["styles"]) <= allowed, e["id"]
        assert e["style_note"].startswith("Poly Haven /info (2026-10-03): tags"), e["id"]
    by_id = {e["id"]: e for e in polyhaven}
    assert by_id["GothicBed_01"]["styles"] == ["classic"] and by_id["GothicCommode_01"]["styles"] == ["classic"]
    assert by_id["GothicBed_01"]["has_mattress"] is True
    for e in catalog.models:
        if e["type"] in C.BED_TYPES:
            assert e["has_mattress"] is True, e["id"]
    # What a Scandinavian project (the default style) can take from Poly Haven: the plain oak side table, the
    # pine shelves and the neutral stove; everything else is parametric (user decision 7).
    scandi = sorted({e["type"] for e in catalog.models if C.styles_match(e, "scandinavian")})
    assert scandi == ["bookshelf", "nightstand", "stove"]


def _styled_catalog():
    entries = [
        _entry("sofa_classic", "sofa", 2.0, 0.8, 0.8, styles=("classic",)),
        _entry("sofa_scandi", "sofa", 2.1, 0.85, 0.8, styles=("scandinavian", "japandi")),
        _entry("sofa_any", "sofa", 1.6, 1.0, 0.8, styles=("neutral",)),
        _entry("bed_frame", "bed_double", 1.6, 2.0, 1.0, has_mattress=False),
        _entry("bed_soft", "bed_single", 0.9, 2.0, 0.6, has_mattress=True, styles=("rustic",)),
    ]
    entries += [{"type": t, "parametric": True, "reason": "test"} for t in C.FURNITURE_TYPES
                if t not in ("sofa", "bed_double", "bed_single")]
    return C.Catalog({"entries": entries})


def test_refit_takes_only_models_of_the_style_family_or_neutral():
    cat = _styled_catalog()
    piece = _piece("sofa", 2.1, 0.85)
    assert F.fit_piece(piece, cat)["asset_id"] == "sofa_scandi"          # no family: every model (fit)
    fit = F.fit_piece(piece, cat, style_family="scandinavian")
    assert fit["asset_id"] == "sofa_scandi" and fit["style_family"] == "scandinavian"
    assert fit["styles"] == ["scandinavian", "japandi"]
    assert [x["id"] for x in fit["excluded"]] == ["sofa_classic"] and "classic" in fit["excluded"][0]["reason"]
    fit = F.fit_piece(piece, cat, style_family="industrial")            # only the neutral one is left ...
    assert fit["method"] == "parametric" and [c["id"] for c in fit["candidates"]] == ["sofa_any"]   # ... too square
    assert {x["id"] for x in fit["excluded"]} == {"sofa_classic", "sofa_scandi"}
    assert F.fit_piece(_piece("sofa", 1.6, 1.0), cat, style_family="industrial")["asset_id"] == "sofa_any"
    no_neutral = C.Catalog({"entries": [e for e in cat.entries if e.get("id") != "sofa_any"]})
    fit = F.fit_piece(piece, no_neutral, style_family="industrial")
    assert fit["method"] == "parametric" and fit["fallback_reason"] == "no model for style industrial"
    assert fit["candidates"] == [] and {x["id"] for x in fit["excluded"]} == {"sofa_classic", "sofa_scandi"}
    building = {"furniture": [piece, _piece("sofa", 2.0, 0.8, pid="f_L0_002")]}
    fitted = F.fit_building(building, cat, style_family="classic")
    assert [p["asset"]["asset_id"] for p in fitted["furniture"]] == ["sofa_classic", "sofa_classic"]


def test_beds_without_a_mattress_are_never_taken():
    cat = _styled_catalog()
    fit = F.fit_piece(_piece("bed_double", 1.6, 2.0), cat)
    assert fit["method"] == "parametric" and fit["fallback_reason"] == "no bed_double model with a mattress"
    assert fit["excluded"] == [{"id": "bed_frame", "reason": "bed model without a mattress"}]
    assert F.fit_piece(_piece("bed_single", 0.9, 2.0), cat)["asset_id"] == "bed_soft"
    assert F.fit_piece(_piece("bed_single", 0.9, 2.0), cat, style_family="modern")["fallback_reason"] == \
        "no model for style modern"


def _objaverse_entry(uid, ftype, w, d, h, licence="CC-BY-4.0", styles=("modern",), **extra):
    e = _entry(f"objaverse_{uid}", ftype, w, d, h, styles=styles)
    for key in ("url", "gltf", "style_note"):
        e.pop(key)
    e.update({"source": "objaverse", "licence": licence, "uid": uid, "glb": f"models/objaverse/{uid}.glb",
              "sha256_glb": "ab" * 32, "title": f"Model {uid}", "author": "someone",
              "source_url": f"https://sketchfab.com/3d-models/{uid}",
              "licence_url": "https://creativecommons.org/licenses/by/4.0/",
              "via": "Objaverse (allenai/objaverse, ODC-By 1.0)",
              "attribution": f'"Model {uid}" by someone (https://sketchfab.com/3d-models/{uid}), CC BY 4.0'})
    e.update(extra)
    return e


def test_validation_of_sources_licences_styles_and_mattresses(catalog):
    base = copy.deepcopy(catalog.data)
    C.validate(base)

    def broken(mutate, complete=True, data=None):
        d = copy.deepcopy(data or base)
        mutate(d)
        with pytest.raises(C.CatalogError):
            C.validate(d, complete=complete)

    first = next(i for i, e in enumerate(base["entries"]) if not e.get("parametric"))
    bed = next(i for i, e in enumerate(base["entries"]) if e.get("type") == "bed_double" and not e.get("parametric"))
    broken(lambda d: d["entries"][first].update(licence="CC-BY-4.0"))      # Poly Haven is CC0 only
    broken(lambda d: d["entries"][first].update(source="sketchfab"))
    broken(lambda d: d["entries"][first].update(styles=["boho"]))
    broken(lambda d: d["entries"][first].update(styles="classic"))
    broken(lambda d: d["entries"][first].pop("styles"))
    broken(lambda d: d["entries"][first].pop("style_note"))
    broken(lambda d: d["entries"][bed].pop("has_mattress"))
    broken(lambda d: d["entries"][bed].update(has_mattress="yes"))
    extra = {"entries": [_objaverse_entry("u1", "bed_single", 0.9, 2.0, 0.6, has_mattress=True)]}
    C.validate(extra, complete=False)
    with pytest.raises(C.CatalogError, match="neither a library entry"):
        C.validate(extra)                                                  # alone it covers one type only
    broken(lambda d: d["entries"][0].update(licence="CC-BY-NC-4.0"), complete=False, data=extra)
    broken(lambda d: d["entries"][0].update(licence="CC-BY-SA-4.0"), complete=False, data=extra)
    for field in C.CC_BY_FIELDS:
        broken(lambda d, f=field: d["entries"][0].update({f: ""}), complete=False, data=extra)
    broken(lambda d: d["entries"][0].update(styles=[]), complete=False, data=extra)
    broken(lambda d: d["entries"][0].update(sha256_glb="abc"), complete=False, data=extra)
    for bad in (0, -0.01, float("inf"), float("nan"), "0.01", True, None):  # not a positive finite factor
        broken(lambda d, u=bad: d["entries"][0].update(unit_scale=u, unit_note="normalised by type"),
               complete=False, data=extra)
    for unit in C.UNIT_SCALES:
        C.validate({"entries": [dict(extra["entries"][0], unit_scale=unit)]}, complete=False)
    # Prep pod P2: a model of unknown units normalised by type carries any positive factor, with its unit_note.
    broken(lambda d: d["entries"][0].update(unit_scale=0.00215423), complete=False, data=extra)   # no unit_note
    broken(lambda d: d["entries"][0].update(unit_scale=0.00215423, unit_note=" "), complete=False, data=extra)
    C.validate({"entries": [dict(extra["entries"][0], unit_scale=0.00215423,
                                 unit_note="normalised by type (model units unknown): x0.00215423 ...")]},
               complete=False)
    broken(lambda d: d["entries"][0].pop("has_mattress"), complete=False, data=extra)
    broken(lambda d: d["entries"].append({"type": "sofa", "parametric": True, "reason": "x"}), complete=False,
           data=extra)
    cc0 = {"entries": [_objaverse_entry("u2", "floor_lamp", 0.4, 0.4, 1.6, licence="CC0", attribution="")]}
    C.validate(cc0, complete=False)                                        # CC0 needs no credit line


def test_load_merges_the_objaverse_catalogue(tmp_path, catalog):
    main = tmp_path / "catalog.json"
    main.write_text(json.dumps(catalog.data), encoding="utf-8")
    assert C.load(main).merged == {} and C.objaverse_path(main) == tmp_path / "catalog_objaverse.json"
    extra = {"schema_version": "0.1", "notice": "ODC-By 1.0", "entries": [
        _objaverse_entry("u1", "bed_single", 0.9, 2.0, 0.6, has_mattress=True, styles=("scandinavian",)),
        _objaverse_entry("u2", "sofa", 2.2, 0.9, 0.8, styles=("scandinavian",), unit_scale=0.01),
        _objaverse_entry("u3", "floor_lamp", 0.4, 0.4, 1.6, licence="CC0", styles=("neutral",))]}
    C.objaverse_path(main).write_text(json.dumps(extra), encoding="utf-8")
    merged = C.load(main)
    assert merged.merged == {"source": "catalog_objaverse.json", "models_added": 3,
                             "parametric_replaced": ["bed_single", "floor_lamp"]}
    assert "bed_single" not in merged.parametric_types and "floor_lamp" not in merged.parametric_types
    assert [e["id"] for e in merged.candidates("bed_single")] == ["objaverse_u1"]
    assert C.load(main, objaverse=False).merged == {}
    # A Scandinavian refit takes the Objaverse sofa with its credit line; the report lists it.
    building = {"project": {"id": "t"}, "furniture": [_piece("sofa", 2.2, 0.9), _piece("bed_single", 0.9, 2.0,
                                                                                        pid="f_L0_002")]}
    fitted = F.fit_building(building, merged, style_family="scandinavian")
    sofa, bed = (p["asset"] for p in fitted["furniture"])
    assert sofa["asset_id"] == "objaverse_u2" and sofa["library"] == "objaverse" and sofa["licence"] == "CC-BY-4.0"
    assert sofa["glb"] == "models/objaverse/u2.glb" and sofa["sha256_glb"] == "ab" * 32 and "gltf" not in sofa
    assert sofa["attribution"].startswith('"Model u2" by someone') and sofa["via"].startswith("Objaverse")
    assert bed["asset_id"] == "objaverse_u1"
    # unit_scale (raw GLB units -> metres) travels with the fit; the scene builder applies it (1.0 when absent).
    assert sofa["unit_scale"] == 0.01 and bed["unit_scale"] == 1.0
    report = F.fit_report(fitted, style_note="family 'scandinavian'")
    assert "## Attribution (CC BY 4.0)" in report and '- objaverse_u2: "Model u2" by someone' in report
    assert "Library style filter: family 'scandinavian'" in report and "## Models not taken" in report
    # A broken Objaverse file is refused, not half-used.
    extra["entries"][0]["licence"] = "CC-BY-NC-4.0"
    C.objaverse_path(main).write_text(json.dumps(extra), encoding="utf-8")
    with pytest.raises(C.CatalogError):
        C.load(main)


def test_style_family_of_a_profile():
    assert F.style_family_of({"family": "japandi", "source_text": "Scandinavian"}) == ("japandi", "the profile's family")
    assert F.style_family_of({"family": None, "source_text": "Scandinavian"})[0] is None
    assert F.style_family_of({"source_text": "Modern minimal, concrete"})[0] == "modern minimal"   # pre-M7 file
    assert F.style_family_of([{"family": "rustic"}, {"family": "modern"}])[0] == "rustic"
    assert F.style_family_of({})[0] is None


def test_cli_style_flag_filters_the_library(tmp_path, monkeypatch, capsys):
    from wenart.assets import models
    from wenart.style import profile as SP

    src = tmp_path / "building.json"
    B.save(load_truth("synthetic-01"), src)
    style = tmp_path / "style.json"
    style.write_text(json.dumps(SP.profile_from_text("Scandinavian, light oak floor")), encoding="utf-8")
    out = tmp_path / "building_final.json"
    assert F.main([str(src), "--out", str(out), "--style", str(style)]) == 0
    assert "style filter: family 'scandinavian'" in capsys.readouterr().out
    fitted = B.load(out)
    by_type = {}
    for p in fitted["furniture"]:
        by_type.setdefault(p["type"], set()).add((p["asset"]["method"], p["asset"]["asset_id"]))
        assert p["asset"]["style_family"] == "scandinavian"
    assert by_type["sofa"] == {("parametric", "parametric:sofa")}         # sofa_02 is classic
    assert ("library", "side_table_01") in by_type["nightstand"]
    assert all(m == "parametric" for m, _ in by_type["bed_double"])         # GothicBed_01 is classic
    sofa = next(p for p in fitted["furniture"] if p["type"] == "sofa")
    assert sofa["asset"]["fallback_reason"] == "no model for style scandinavian"
    report = (tmp_path / "building_final_report.md").read_text(encoding="utf-8")
    assert "Library style filter: family 'scandinavian'" in report and "sofa_02: styles ['classic']" in report
    F.assert_only_assets_changed(load_truth("synthetic-01"), fitted)
    # Without --style (the fit stage) nothing is filtered.
    assert F.main([str(src), "--out", str(out)]) == 0
    assert any(p["asset"]["asset_id"] == "sofa_02" for p in B.load(out)["furniture"])
    # An Objaverse fit is fetched from the cache only: the fetcher gets the asset (uid, sha256) as meta.
    seen = []
    monkeypatch.setattr(models, "fetch_model", lambda a, d, size="1k", source="polyhaven", licence=None, meta=None:
                        seen.append((a, source, licence, (meta or {}).get("uid"))))
    asset = _objaverse_entry("u9", "sofa", 2.2, 0.9, 0.8)
    building = {"furniture": [dict(_piece("sofa", 2.2, 0.9), asset={
        "method": "library", "library": "objaverse", "asset_id": asset["id"], "licence": "CC-BY-4.0",
        "uid": "u9", "sha256_glb": asset["sha256_glb"], "glb": asset["glb"]})]}
    assert F.download_fitted(building, tmp_path / "assets", log=lambda *_: None)["fetched"] == ["objaverse_u9"]
    assert seen == [("objaverse_u9", "objaverse", "CC-BY-4.0", "u9")]
