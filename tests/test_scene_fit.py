"""Milestone 12 track S (docs/milestone12.md §4.8 D14, §6.4, B1, B7; CLAUDE.md library rules): the fit takes only
usable (audited, no NC/SA/ND) models, ranks them by the judges' quality list (B1), keeps real proportions (10 %,
0.85-1.20), falls back along the style chain (``style_fallback``), uses a related type only for a piece its group
needs, builds parametric pieces only by design (counters, wall cabinets, stairs, the kitchen and bath fixtures) and
writes a ``library_gap`` instead of a parametric sofa, bed or table; throws, curtains and blinds are procedural."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from wenart.furniture import catalog as C
from wenart.furniture import fit as F

from test_furniture_fit_v2 import FakeCatalog, decor_model, model, piece

ROOT = Path(__file__).resolve().parents[1]


def test_quality_list_ranks_the_models_again_b1():
    """B1: the catalogue stores ``quality`` as the two judges' answers; the old ``quality_of`` read 3.0 for a list."""
    assert F.quality_of({"quality": [5, 4]}) == 4.5 and F.quality_of({"quality": [2, 3]}) == 2.5
    assert F.quality_of({"quality": []}) == F.DEFAULT_QUALITY and F.quality_of({"quality": [True, "x"]}) == 3.0
    low = model("low", "sofa", 2.0 / 1.02, 0.9 / 1.02, 0.8, quality=[2, 2])
    high = model("high", "sofa", 2.0 / 1.03, 0.9 / 1.03, 0.8, quality=[5, 4])     # same 5 % size step
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([low, high]))
    assert fit["asset_id"] == "abo_high" and [c["quality"] for c in fit["candidates"]] == [4.5]


@pytest.mark.parametrize("extra, why", [({"licence": "CC-BY-NC-4.0", "licence_flag": "non_commercial"}, "licence"),
                                        ({"licence": "CC-BY-SA-4.0", "licence_flag": "share_alike"}, "licence"),
                                        ({"licence": "CC-BY-ND-4.0", "licence_flag": "no_derivatives"}, "licence"),
                                        ({"audit": {"status": "removed", "reasons": ["air bed"]}}, "audit")])
def test_only_usable_models_are_fitted(extra, why):
    bad = model("bad", "sofa", 2.0, 0.9, 0.8, quality=[5, 5], **extra)
    good = model("good", "sofa", 2.0, 0.9, 0.8, quality=[3, 3])
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([bad, good]))
    assert fit["asset_id"] == "abo_good"
    assert fit["excluded"][0]["id"] == "abo_bad" and why in fit["excluded"][0]["reason"]
    gap = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([bad]))
    assert gap["method"] == "none" and "no usable sofa model" in gap["fallback_reason"]


def test_an_audit_fix_applies_its_catalogue_fixes():
    turned = model("turned", "sofa", 0.9, 2.0, 0.8, audit={"status": "fix", "fixes": {"bbox_m": [2.0, 0.9, 0.8]}})
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([turned]))
    assert fit["method"] == "library" and fit["fit_scale"] == [1.0, 1.0, 1.0] and fit["audit"]["status"] == "fix"
    assert C.usable({"licence": "CC0", "audit": {"status": "keep"}}) and C.effective({"id": "x"}) == {"id": "x"}


def test_style_family_falls_back_along_its_chain():
    rustic = model("rustic", "sofa", 2.0, 0.9, 0.8, styles=("rustic",))
    classic = model("classic", "sofa", 2.0, 0.9, 0.8, styles=("classic",))
    modern = model("modern", "sofa", 2.0, 0.9, 0.8, styles=("modern",))
    cat = FakeCatalog([rustic, classic, modern])
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), cat, style_family="mediterranean")
    assert fit["asset_id"] == "abo_rustic" and fit["style_family"] == "rustic"
    assert fit["style_fallback"] == {"wanted": "mediterranean", "used": "rustic",
                                     "chain": ["mediterranean", "rustic", "classic"],
                                     "why": "mediterranean: no model for style mediterranean"}
    assert F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([classic, modern]),
                       style_family="mediterranean")["asset_id"] == "abo_classic"
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([modern]), style_family="industrial")
    assert fit["asset_id"] == "abo_modern" and fit["style_fallback"]["used"] == "modern"
    assert "style_fallback" not in F.fit_piece(piece("sofa", 2.0, 0.9), cat, style_family="classic")
    assert F.style_chain(None) == [None] and F.style_chain("industrial") == ["industrial", "modern"]
    for family, chain in F.STYLE_FALLBACK.items():
        assert family not in chain and set(chain) <= {f for f, _ in __import__(
            "wenart.style.vocabulary", fromlist=["x"]).STYLE_FAMILIES}


def test_never_a_parametric_sofa_bed_or_table_a_library_gap_instead():
    for ftype, size in (("sofa", (2.0, 0.9)), ("bed_double", (1.6, 2.0)), ("table_dining", (1.6, 0.9)),
                        ("table_coffee", (1.0, 0.6))):
        odd = model("odd", ftype, size[0] * 1.5, size[1], 0.8)               # 50 % wider: outside the caps
        fit = F.fit_piece(piece(ftype, *size), FakeCatalog([odd]))
        assert fit["method"] == "none" and fit["library_gap"]["used"] == "nothing (not built)"
        assert fit["library_gap"]["type"] == ftype and "10 % non-uniform" in fit["library_gap"]["reason"]


def test_related_type_only_when_the_group_needs_it():
    chair = model("chair", "chair", 0.8, 0.8, 0.8)
    odd = model("wide", "armchair", 1.4, 0.8, 0.8)
    cat = FakeCatalog([odd, chair])
    added = piece("armchair", 0.8, 0.8, source="added_by_ai")
    assert F.fit_piece(added, cat)["method"] == "none"                         # nobody needs it: a gap
    grouped = dict(added, group={"group_id": "g1", "group": "seating", "role": "partner"})
    for p in (grouped, piece("armchair", 0.8, 0.8)):                           # a group member, a drawn piece
        fit = F.fit_piece(p, cat)
        assert fit["method"] == "library" and fit["asset_id"] == "abo_chair" and fit["related_type"] == "chair"
        assert fit["library_gap"]["used"] == "related type chair: abo_chair" and fit["library_gap"]["type"] == \
            "armchair"
    assert "sofa" not in F.RELATED_TYPES and "bed_double" not in F.RELATED_TYPES
    assert not set(F.RELATED_TYPES) & set(C.PARAMETRIC_FIXTURE_TYPES)


def test_parametric_only_by_design():
    assert set(C.BY_DESIGN_PARAMETRIC_TYPES) == {"kitchen_counter", "kitchen_island", "wall_cabinet", "stair",
                                                 "shower", "washing_machine", "fridge", "toilet", "washbasin",
                                                 "bathtub", "sink_kitchen", "stove"}
    assert C.by_design_parametric({"type": "washbasin"}) and C.by_design_parametric(
        {"type": "wardrobe", "design": {"built_in": True}}) and not C.by_design_parametric({"type": "wardrobe"})
    odd = model("odd", "shower", 2.0, 0.9, 2.0)
    fit = F.fit_piece(piece("shower", 0.9, 0.9), FakeCatalog([odd]))
    assert fit["method"] == "parametric" and fit["by_design"] and "our parametric shower" in fit["fallback_reason"]
    assert fit["library_gap"]["used"] == "our parametric fixture (by design)"


def test_fit_building_writes_the_gap_on_the_piece_and_changes_nothing_else():
    cat = FakeCatalog([model("odd", "sofa", 3.0, 0.9, 0.8), model("ok", "nightstand", 0.5, 0.4, 0.5)])
    building = {"project": {"id": "t"}, "furniture": [piece("sofa", 2.0, 0.9),
                                                      piece("nightstand", 0.5, 0.4, pid="f_L0_002")]}
    before = copy.deepcopy(building)
    fitted = F.fit_building(building, cat)
    assert building == before
    F.assert_only_assets_changed(building, fitted)
    sofa, night = fitted["furniture"]
    assert sofa["library_gap"]["type"] == "sofa" and "library_gap" not in night
    report = F.fit_report(fitted)
    assert "1 library gaps (not built)" in report and "## Library gaps" in report
    assert "- f_L0_001 (sofa, style None): nothing (not built)" in report
    refit = F.fit_building(dict(fitted, furniture=[dict(sofa, footprint=dict(sofa["footprint"], size=[3.0, 0.9]))]),
                           cat)
    assert "library_gap" not in refit["furniture"][0]                     # a later fit clears a stale gap


def test_throws_curtains_and_blinds_are_procedural_b7():
    """B7: Milestone 11 fitted any 'throw' model (a juice machine, a bench) squashed to 5 cm; now never a model."""
    cat = FakeCatalog(decor=[decor_model("juice", "throw", 0.6, 0.4, 0.3), decor_model("c", "curtain", 1.4, 0.1, 2.4),
                             decor_model("b", "blind", 1.2, 0.05, 1.2)])
    for dtype, size in (("throw", (1.5, 0.5, 0.05)), ("curtain", (1.4, 0.08, 2.4)), ("blind", (1.2, 0.06, 1.0))):
        it = {"id": "d", "type": dtype, "size": list(size), "host_id": "f"}
        assert F.fit_decor_item(it, cat) is None
    assert set(F.PROCEDURAL_DECOR_TYPES) == {"throw", "curtain", "blind"}
    assert not set(F.PROCEDURAL_DECOR_TYPES) & set(F.DECOR_LIBRARY_TYPES)


def test_decor_models_must_be_usable():
    nc = decor_model("nc", "vase", 0.18, 0.18, 0.4, licence="CC-BY-NC-4.0", licence_flag="non_commercial")
    ok = decor_model("ok", "vase", 0.18, 0.18, 0.4)
    it = {"id": "d", "type": "vase", "size": [0.18, 0.18, 0.4], "host_id": "f"}
    assert F.fit_decor_item(it, FakeCatalog(decor=[nc])) is None
    assert F.fit_decor_item(it, FakeCatalog(decor=[nc, ok]))["asset_id"] == "abo_ok"


@pytest.mark.parametrize("project", ["real02", "real03"])
def test_committed_buildings_parametric_only_by_design_gaps_listed(project):
    path = ROOT / "results" / "furniture" / project / "building_final.json"
    if not path.is_file():
        pytest.skip("no committed building")
    building = json.loads(path.read_text(encoding="utf-8"))
    for p in building["furniture"]:
        p.pop("library_gap", None)
    fitted = F.fit_building(building, C.load(), style_family="modern")
    built = [p for p in fitted["furniture"] if p.get("build", True) is not False and p["type"] != "unknown"]
    for p in built:
        a = p["asset"]
        assert a["method"] in ("library", "parametric", "none")
        if a["method"] == "parametric":
            assert C.by_design_parametric(p), p["id"]
        if a["method"] == "none":
            assert p["library_gap"]["used"] == "nothing (not built)" and not C.by_design_parametric(p)
        if a["method"] == "library":
            assert C.usable(a) and a["fit_scale"][0] / a["fit_scale"][1] <= 1.10 + 1e-6
            assert 0.85 - 1e-6 <= sum(a["fit_scale"]) / 3 <= 1.20 + 1e-6
    gaps = sum(1 for p in built if p["asset"]["method"] == "none")
    assert gaps < 0.2 * len(built)
