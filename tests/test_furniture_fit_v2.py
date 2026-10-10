"""Fit v2 (docs/milestone8.md §1, §4; wenart/furniture/fit.py): the ranking after the style filter and the bed
rule (generated last -> real size -> quality -> aspect -> source), the caps and frozen keys as before, bed
frames with a deck and their bedding record, models from GLB sources (ABO, Objaverse, generated) and the
library decor (cushion, plant, rug, wall art) picked by host id.

The catalogue here is a duck-typed stand-in (``candidates``, ``parametric_types``, ``decor``,
``decor_candidates``): ``wenart.furniture.catalog.Catalog`` validates only the M7 sources, the Milestone 8
library file is the library agent's.
"""
from __future__ import annotations

import copy
import json

import pytest

from wenart.blender import parametric as P
from wenart.furniture import fit as F

LICENCES = {"abo": "CC-BY-4.0", "polyhaven": "CC0", "objaverse": "CC-BY-4.0",
            "generated": "generated (TRELLIS.2-4B, MIT)"}


def model(uid: str, ftype: str, w: float, d: float, h: float, source: str = "abo", quality=None,
          styles=("neutral",), **extra) -> dict:
    e = {"id": f"{source}_{uid}", "type": ftype, "source": source, "licence": LICENCES[source],
         "bbox_m": [w, d, h], "bbox_model_m": [w, d, h], "bbox_min_m": [-w / 2, -d / 2, 0.0],
         "bbox_max_m": [w / 2, d / 2, h], "front_axis": "-Y", "up_axis": "+Z", "origin_offset": [0.0, 0.0, 0.0],
         "front_axis_confidence": "high", "styles": list(styles)}
    if source == "polyhaven":
        e.update({"url": f"https://polyhaven.com/a/{uid}", "gltf": f"models/{uid}/{uid}_1k.gltf",
                  "style_note": "test"})
    else:
        e.update({"uid": uid, "glb": f"models/{source}/{uid}.glb", "sha256_glb": "ab" * 32, "title": f"Model {uid}",
                  "author": "someone", "source_url": f"https://example.org/{uid}",
                  "licence_url": "https://creativecommons.org/licenses/by/4.0/", "via": source,
                  "attribution": f'"Model {uid}" by someone ({source})', "licence_flag": None})
    if ftype in ("bed_single", "bed_double"):
        e.setdefault("has_mattress", True)
    if quality is not None:
        e["quality"] = quality
    e.update(extra)
    return e


def decor_model(uid: str, dtype: str, w: float, d: float, h: float, styles=("neutral",), **extra) -> dict:
    e = model(uid, f"decor_{dtype}", w, d, h, styles=styles, **extra)
    e.update({"kind": "decor", "decor_type": dtype})
    return e


class FakeCatalog:
    """The duck-typed catalogue of fit.py: furniture models, decor via ``decor_candidates``."""

    def __init__(self, entries=(), decor=(), with_method: bool = True):
        self.entries = [e for e in entries if e.get("kind") != "decor"]
        self._decor = list(decor)
        self.decor = [] if with_method else list(decor)
        if not with_method:
            self.decor_candidates = None

    @property
    def parametric_types(self) -> list[str]:
        return []

    def candidates(self, ftype: str) -> list[dict]:
        return [e for e in self.entries if e["type"] == ftype]

    def decor_candidates(self, dtype: str) -> list[dict]:   # noqa: F811 - replaced by None above when absent
        return [e for e in self._decor if e.get("decor_type") == dtype]


def piece(ftype: str, w: float, d: float, pid: str = "f_L0_001", source: str = "from_documents") -> dict:
    return {"id": pid, "level_id": "L0", "room_id": "r_L0_salon", "type": ftype, "type_raw": None, "source": source,
            "footprint": {"center": [1.0, 2.0], "size": [w, d], "rotation_deg": 90.0}, "front_deg": 0.0,
            "height": None, "asset": None, "status": "verified",
            "evidence": [{"file": "a.dxf", "method": "vector", "confidence": 1.0}]}


def ids(fit: dict) -> list[str]:
    return [c["id"] for c in fit["candidates"]]


# --------------------------------------------------------------------------
# Ranking rules, one at a time
# --------------------------------------------------------------------------

def test_real_size_beats_quality_and_aspect():
    """A product whose real size is the footprint wins over a better-rated model of the same shape that
    must shrink by 17 %."""
    cat = FakeCatalog([model("exact", "sofa", 2.0, 0.9, 0.8, quality=2.0),
                       model("big", "sofa", 2.4, 1.08, 0.9, quality=5.0)])
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), cat)
    assert fit["asset_id"] == "abo_exact" and ids(fit) == ["abo_exact"]
    assert fit["candidates"][0]["size_error"] == 0.0 and fit["candidates"][0]["size_bucket"] == 0
    assert fit["ranking"]["rank"] == 1 and fit["ranking"]["reasons"][0].startswith("real size: mean |scale - 1| 0.000")
    # The big one is next in line: it is taken when the exact one fails the caps (a tighter mean-scale range).
    order = F.rank_candidates(cat.entries, 2.0, 0.9)
    assert [e["id"] for e in order] == ["abo_exact", "abo_big"]


def test_quality_decides_within_the_same_size_step():
    # both within the first 5 % step: 2 % and 3 % mean scale change
    a = model("a", "sofa", 2.0 / 1.02, 0.9 / 1.02, 0.8, quality=3.0)        # scales 1.02, 1.02, 1.02
    b = model("b", "sofa", 2.0 / 1.03, 0.9 / 1.03, 0.8, quality=4.5)        # scales 1.03 ...
    cat = FakeCatalog([a, b])
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), cat)
    assert fit["asset_id"] == "abo_b" and fit["quality"] == 4.5
    assert [c["size_bucket"] for c in fit["candidates"]] == [0]
    # outside the step the size wins again
    c = model("c", "sofa", 2.0 / 1.08, 0.9 / 1.08, 0.8, quality=5.0)       # 8 %: second step
    assert F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([a, c]))["asset_id"] == "abo_a"


def test_missing_quality_counts_as_three():
    none = model("none", "sofa", 2.0, 0.9, 0.8)
    low = model("low", "sofa", 2.0, 0.9, 0.8, quality=2.5)
    high = model("high", "sofa", 2.0, 0.9, 0.8, quality=3.5)
    assert F.quality_of(none) == F.DEFAULT_QUALITY == 3.0 and F.quality_of({"quality": "good"}) == 3.0
    assert [e["id"] for e in F.rank_candidates([low, none, high], 2.0, 0.9)] == ["abo_high", "abo_none", "abo_low"]


def test_aspect_then_source_break_the_remaining_ties():
    # same size step and quality: the smaller aspect error wins
    square = model("square", "sofa", 2.0 / 1.02, 0.9 / 0.99, 0.8, quality=4.0)
    off = model("off", "sofa", 2.0 / 0.99, 0.9 / 1.03, 0.8, quality=4.0)
    order = F.rank_candidates([off, square], 2.0, 0.9)
    assert F.rank_key(square, 2.0, 0.9)[2] == F.rank_key(off, 2.0, 0.9)[2] == 0
    errs = [round(abs(F.C.aspect_error(e, 2.0, 0.9)), 4) for e in order]
    assert errs == sorted(errs) and order[0]["id"] == "abo_square"
    # identical boxes and quality: abo, polyhaven, objaverse (generated is a rule of its own)
    same = [model("x", "sofa", 2.0, 0.9, 0.8, source=s, quality=4.0) for s in ("objaverse", "polyhaven", "abo")]
    assert [e["source"] for e in F.rank_candidates(same, 2.0, 0.9)] == ["abo", "polyhaven", "objaverse"]
    assert F.SOURCE_ORDER == ("abo", "polyhaven", "objaverse", "generated")


def test_known_units_rank_before_models_normalised_by_type():
    normalised = model("norm", "sofa", 2.0, 0.9, 0.8, source="objaverse", quality=5.0, unit_scale=0.0137,
                       unit_note="unknown units: normalised by type")
    known = model("known", "sofa", 2.3, 1.0, 0.85, quality=3.0)            # 13 % smaller when fitted
    assert not F.units_known(normalised) and F.units_known(known)
    assert F.units_known(dict(normalised, units_known=True)) and not F.units_known(dict(known, units_known=False))
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([normalised, known]))
    assert fit["asset_id"] == "abo_known" and fit["units_known"] is True
    # when the known one fails the caps the normalised one is next (its size step is not ranked)
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([normalised, model("tiny", "sofa", 1.2, 0.9, 0.8)]))
    assert fit["asset_id"] == "objaverse_norm" and ids(fit) == ["abo_tiny", "objaverse_norm"]
    assert fit["candidates"][1]["size_bucket"] is None and not fit["candidates"][1]["units_known"]
    assert "units not known" in fit["ranking"]["reasons"][0]
    assert fit["unit_scale"] == 0.0137 and fit["glb"] == "models/objaverse/norm.glb"


def test_generated_models_only_when_no_other_library_model_passes():
    gen = model("sofa_scandinavian_1_abcd1234", "sofa", 2.0, 0.9, 0.8, source="generated", quality=5.0,
                generated={"prompt": "a single scandinavian style sofa", "image_sha256": "cd" * 32,
                           "model": "microsoft/TRELLIS.2-4B", "revision": "af44b45", "seed": 7})
    real = model("real", "sofa", 2.3, 1.0, 0.85, source="polyhaven", quality=2.0)
    assert not F.units_known(gen)
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([gen, real]))
    assert fit["asset_id"] == "polyhaven_real" and ids(fit) == ["polyhaven_real"] and fit["gltf"].endswith(".gltf")
    # every real model outside the caps: the generated one, said so
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([gen, model("odd", "sofa", 3.0, 0.5, 0.8)]))
    assert fit["asset_id"] == gen["id"] and ids(fit) == ["abo_odd", gen["id"]]
    assert fit["library"] == "generated" and fit["licence"].startswith("generated")
    assert fit["generated"]["model"] == "microsoft/TRELLIS.2-4B" and fit["glb"].endswith(".glb")
    assert fit["ranking"]["reasons"][0] == "generated: no other library model passed the caps"
    assert fit["ranking"]["passed_over"] == [{"id": "abo_odd", "why": fit["ranking"]["passed_over"][0]["why"]}]
    assert "outside the caps" in fit["ranking"]["passed_over"][0]["why"]


def test_caps_and_style_filter_still_apply():
    cat = FakeCatalog([model("classic", "sofa", 2.0, 0.9, 0.8, styles=("classic",), quality=5.0),
                       model("stretched", "sofa", 1.4, 0.9, 0.8),          # 43 % wider: non-uniform cap
                       model("ok", "sofa", 2.1, 0.92, 0.8, styles=("scandinavian",))])
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), cat, style_family="scandinavian")
    assert fit["asset_id"] == "abo_ok" and [x["id"] for x in fit["excluded"]] == ["abo_classic"]
    assert ids(fit) == ["abo_ok"]
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([model("stretched", "sofa", 1.4, 0.9, 0.8)]))
    assert fit["method"] == "none" and "10 % non-uniform" in fit["fallback_reason"]      # Milestone 12: a gap
    assert fit["candidates"][0]["rank"] == 1 and fit["candidates"][0]["accepted"] is False


def test_fit_building_keeps_every_frozen_key_and_the_report_lists_the_ranking():
    # Milestone 12 (CLAUDE.md library rules): the non-commercial twin of the sofa is never taken
    cat = FakeCatalog([model("exact_nc", "sofa", 2.0, 0.9, 0.8, quality=5.0, licence_flag="non_commercial",
                             licence="CC-BY-NC-4.0", source="objaverse"),
                       model("exact", "sofa", 2.0, 0.9, 0.8, quality=4.0, source="objaverse"),
                       model("frame", "bed_double", 1.6, 2.0, 1.0, has_mattress=False, bed_frame=True,
                             deck_height_m=0.3)])
    building = {"project": {"id": "t"}, "furniture": [piece("sofa", 2.0, 0.9),
                                                      piece("bed_double", 1.6, 2.0, pid="f_L0_002",
                                                            source="added_by_ai")]}
    before = copy.deepcopy(building)
    fitted = F.fit_building(building, cat, style_family="scandinavian")
    assert building == before
    F.assert_only_assets_changed(building, fitted)
    for a, b in zip(building["furniture"], fitted["furniture"]):
        assert {k: a.get(k) for k in F.FROZEN_KEYS} == {k: b.get(k) for k in F.FROZEN_KEYS}
    report = F.fit_report(fitted)
    assert "## Ranking (fit v2)" in report and F.RANKING_RULE in report
    assert "- f_L0_001 (sofa): objaverse_exact (objaverse), rank 1 of 1 tried: real size" in report
    assert "## Bed frames with bedding" in report and "CC-BY-NC-4.0 (non_commercial)" not in report.split(
        "## Models not taken")[0]
    assert "objaverse_exact_nc: licence CC-BY-NC-4.0 (non_commercial): not used" in report
    assert "## Attribution (CC BY 4.0)" in report and '"Model exact" by someone' in report
    json.dumps(fitted)   # plain JSON


# --------------------------------------------------------------------------
# Bed frames
# --------------------------------------------------------------------------

def test_bed_frames_with_a_deck_are_taken_and_carry_their_bedding():
    frame = model("frame", "bed_double", 1.7, 2.1, 1.1, has_mattress=False, bed_frame=True, deck_height_m=0.32)
    fit = F.fit_piece(piece("bed_double", 1.6, 2.0), FakeCatalog([frame]))
    assert fit["method"] == "library" and fit["bed_frame"] is True and fit["deck_height_m"] == 0.32
    sz = fit["fit_scale"][2]
    bed = fit["bedding"]
    assert bed["deck_z_m"] == pytest.approx(0.32 * sz, abs=1e-4)
    assert bed["mattress_top_m"] == pytest.approx(0.32 * sz + P.FRAME_MATTRESS_M, abs=1e-4)
    assert bed["inner_box_m"] == pytest.approx([1.6 * 0.92, 2.0 * 0.92])
    assert fit["bbox_m"][2] == pytest.approx(max(1.1 * sz, bed["top_m"]), abs=1e-4)
    # a low platform frame: the box covers the bedding the scene builder adds
    low = model("low", "bed_double", 1.6, 2.0, 0.25, has_mattress=False, bed_frame=True, deck_height_m=0.2)
    fit = F.fit_piece(piece("bed_double", 1.6, 2.0), FakeCatalog([low]))
    assert fit["bbox_m"][2] == fit["bedding"]["top_m"] > 0.25 + P.FRAME_MATTRESS_M
    # a bed with a mattress is no frame
    soft = F.fit_piece(piece("bed_double", 1.6, 2.0), FakeCatalog([model("soft", "bed_double", 1.6, 2.0, 1.0)]))
    assert "bed_frame" not in soft and "bedding" not in soft


@pytest.mark.parametrize("extra", [{}, {"bed_frame": True}, {"bed_frame": True, "deck_height_m": 0},
                                   {"bed_frame": True, "deck_height_m": None},
                                   {"bed_frame": False, "deck_height_m": 0.3},
                                   {"bed_frame": True, "deck_height_m": True}])
def test_beds_without_a_mattress_or_a_deck_are_still_refused(extra):
    bare = model("bare", "bed_double", 1.6, 2.0, 1.0, has_mattress=False, **extra)
    fit = F.fit_piece(piece("bed_double", 1.6, 2.0), FakeCatalog([bare]))
    assert fit["method"] == "none" and fit["fallback_reason"] == "no bed_double model with a mattress"
    assert fit["excluded"] == [{"id": "abo_bare", "reason": "bed model without a mattress"}]


# --------------------------------------------------------------------------
# Library decor
# --------------------------------------------------------------------------

def item(dtype: str, size, host=None, anchors=None, iid="dec_L0_001", **extra) -> dict:
    out = {"id": iid, "kind": "decor", "type": dtype, "level_id": "L0", "room_id": "r", "center": [1.0, 1.0],
           "rotation_deg": 0.0, "size": list(size), "asset": None, "host_id": host, "source": "added_by_ai",
           "method": "rule", "reason": "test"}
    if anchors:
        out["anchor_ids"] = list(anchors)
    out.update(extra)
    return out


RUGS = [decor_model(f"rug{i}", "rug", 2.4, 1.7, 0.01, styles=s)
        for i, s in enumerate([("scandinavian",), ("neutral",), ("classic",), ("scandinavian", "japandi")])]


def test_decor_pick_is_deterministic_by_host_and_follows_the_style():
    cat = FakeCatalog(decor=RUGS)
    rug = item("rug", (2.6, 2.0), anchors=["f_L0_001", "f_L0_002"])
    a = F.fit_decor_item(rug, cat, style_family="scandinavian")
    assert a["method"] == "library" and a["decor_type"] == "rug" and a["pick"]["key"] == "f_L0_001"
    assert a["pick"]["ids"] == ["abo_rug0", "abo_rug1", "abo_rug3"] and a["pick"]["other_style"] == 1
    assert a["asset_id"] == a["pick"]["ids"][F.pick_index("f_L0_001", 3)]
    # the same host gets the same model whatever the catalogue order; other hosts spread over the models
    again = F.fit_decor_item(rug, FakeCatalog(decor=list(reversed(RUGS))), style_family="scandinavian")
    assert again["asset_id"] == a["asset_id"]
    picks = {F.fit_decor_item(item("rug", (2.6, 2.0), anchors=[f"f_L0_{n:03d}"]), cat, "scandinavian")["asset_id"]
             for n in range(1, 13)}
    assert len(picks) >= 2
    # a classic project takes the classic and the neutral one only
    assert F.fit_decor_item(rug, cat, style_family="classic")["pick"]["ids"] == ["abo_rug1", "abo_rug2"]
    # no model of the family or neutral: none (the parametric rug)
    only_classic = FakeCatalog(decor=[RUGS[2]])
    assert F.fit_decor_item(rug, only_classic, style_family="industrial") is None
    # the pick key: host, else first anchor, else the item itself
    assert F.decor_pick_key(item("cushion", (0.45, 0.15), host="f_9")) == "f_9"
    assert F.decor_pick_key(item("plant", (0.4, 0.4))) == "dec_L0_001"


def test_rugs_are_flat_on_the_rug_size_and_turn_to_their_long_side():
    thick = decor_model("thick", "rug", 1.7, 2.4, 0.08)     # long side along Y, thick
    a = F.fit_decor_item(item("rug", (2.6, 1.8), anchors=["f"]), FakeCatalog(decor=[thick]))
    assert a["target"] == "rug" and a["turned_deg"] == 90.0 and a["front_axis"] == "-X"
    assert a["bbox_m"] == [2.6, 1.8, F.RUG_MAX_THICKNESS_M]
    assert a["fit_scale"][:2] == [round(2.6 / 2.4, 4), round(1.8 / 1.7, 4)]
    straight = F.fit_decor_item(item("rug", (2.0, 3.0), anchors=["f"]), FakeCatalog(decor=[thick]))
    assert straight["turned_deg"] == 0.0 and straight["front_axis"] == "-Y"
    # too stretched (a runner on a square rug): refused -> parametric
    runner = decor_model("runner", "rug", 3.0, 0.8, 0.01)
    assert F.fit_decor_item(item("rug", (2.0, 2.0), anchors=["f"]), FakeCatalog(decor=[runner])) is None


def test_wall_art_keeps_its_aspect_and_the_room_under_the_ceiling():
    art = decor_model("art", "wall_art", 0.8, 0.03, 0.6)
    a = F.fit_decor_item(item("wall_art", (1.2, 0.04), anchors=["f_sofa"], max_height_m=1.2),
                         FakeCatalog(decor=[art]))
    assert a["target"] == "wall_art" and a["fit_scale"] == [1.5, 1.5, 1.5]
    assert a["bbox_m"] == [1.2, 0.045, 0.9]
    # little room under the ceiling: scaled by its height, still keeping the aspect
    low = F.fit_decor_item(item("wall_art", (1.2, 0.04), anchors=["f_sofa"], max_height_m=0.45),
                           FakeCatalog(decor=[art]))
    assert low["bbox_m"] == [0.6, 0.0225, 0.45]
    # narrower than 0.3 m: no wall art at all (it has no parametric shape)
    tall = decor_model("tall", "wall_art", 0.3, 0.03, 1.2)
    assert F.fit_decor_item(item("wall_art", (1.0, 0.04), anchors=["f"], max_height_m=0.6),
                            FakeCatalog(decor=[tall])) is None


def test_cushions_plants_and_books():
    flat = decor_model("flat", "cushion", 0.45, 0.45, 0.15)   # a pillow lying flat: 3 x squashed in depth
    stand = decor_model("stand", "cushion", 0.45, 0.15, 0.45)
    cat = FakeCatalog(decor=[flat, stand])
    # Milestone 12 (B7): a standing cushion (width, thickness, height) keeps the model's proportions (uniform scale)
    a = F.fit_decor_item(item("cushion", (0.45, 0.15, 0.45), host="f_sofa"), cat)
    assert a["asset_id"] == "abo_stand" and a["target"] == "within" and a["pick"]["not_fitting"] == ["abo_flat"]
    assert a["fit_scale"] == [1.0, 1.0, 1.0] and a["bbox_m"] == [0.45, 0.15, 0.45]
    assert F.fit_decor_item(item("cushion", (0.45, 0.15, 0.45), host="f_sofa"), FakeCatalog(decor=[flat])) is None
    # never a pillow stretched to a tower (Milestone 11: 0.5 x 0.3 x 0.60 m): proportions off by > 10 % are refused
    low = decor_model("low", "cushion", 0.5, 0.15, 0.3)
    assert F.fit_decor_item(item("cushion", (0.5, 0.15, 0.5), host="f_bed"), FakeCatalog(decor=[low])) is None
    # a lying cushion (2 values: ottoman, bench) is the procedural one
    assert F.fit_decor_item(item("cushion", (0.4, 0.4), host="f_ottoman"), cat) is None
    assert F.fit_decor_item(item("book_set", (0.3, 0.22), host="f_desk"), cat) is None
    # without decor_candidates (an M7 catalogue object) the decor list is scanned for kind/decor_type
    plant = decor_model("palm", "plant", 0.5, 0.5, 1.2)
    old = FakeCatalog(decor=[plant], with_method=False)
    assert F.fit_decor_item(item("plant", (0.4, 0.4)), old)["asset_id"] == "abo_palm"


def test_fit_building_sets_every_decor_asset_and_changes_nothing_else():
    cat = FakeCatalog([model("exact", "sofa", 2.0, 0.9, 0.8)], decor=RUGS)
    building = {"furniture": [piece("sofa", 2.0, 0.9)],
                "decor": [item("rug", (2.6, 2.0), anchors=["f_L0_001"]),
                          dict(item("wall_art", (1.2, 0.04), anchors=["f_L0_001"], iid="dec_L0_002"),
                               asset={"stale": True}),
                          item("cushion", (0.45, 0.15), host="f_L0_001", iid="dec_L0_003")]}
    fitted = F.fit_building(building, cat, style_family="scandinavian")
    F.assert_only_assets_changed(building, fitted)
    rug, art, cushion = fitted["decor"]
    assert rug["asset"]["asset_id"].startswith("abo_rug") and art["asset"] is None and cushion["asset"] is None
    report = F.fit_report(fitted)
    assert "- wall_art: none (not built) x 1" in report and "- rug: abo_rug" in report
    assert f"- {rug['asset']['asset_id']}: \"Model {rug['asset']['uid']}\" by someone (abo)" in report   # credited
    assert "parametric by design" in report
