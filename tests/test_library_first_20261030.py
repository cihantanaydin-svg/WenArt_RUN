"""30 Oct 2026, lessons UL215 and UL216 (user: "There were already laptop models in the library why we have not use that
one and created a brand new model instead?", "Library models if exist and better than procedural generation should be
used, fix the problem related to it", on logos "no need to reject them", and "bad model stays out but 'For items with
an open part in normal use'. we can use it a dresser with open doors could be used").

- The audit: an open drawer, door or lid (``parts_open``) and a maker's logo or print (the vision answer's
  ``brand_logo`` / ``text_print``, the run-render check ``render_print``) are flags (``open_parts``, ``logo_flag``),
  never removals; a low vision quality and "no real product" still remove furniture. Commercial mode leaves a logo out.
- The catalogue: the extras (the 3D Warehouse objects) are loaded; the entries the two rules change were re-decided
  from their stored answers.
- The fit: a decor item of a type we also build procedurally (laptop, monitor, microwave, TV) takes an audited library
  model when one is better (vision quality >= 4, a real product, the style family's, its real size after a uniform
  scale), else the procedural model with a ``library_gap`` the fit report lists.
"""
from __future__ import annotations

import copy
import json
from types import SimpleNamespace

from wenart.assets.audit import checks as CK
from wenart.assets.audit import decide as D
from wenart.assets.audit import load_config
from wenart.assets.audit import write as W
from wenart.assets.audit.checks import RENDER_FINDINGS, RENDER_FINDING_WHY
from wenart.furniture import catalog as C
from wenart.furniture import fit as F
from wenart.run import copy as CP

CFG = load_config()
KNOWN = {"sofa", "dresser", "laptop"}
SOFA = {"is_type": True, "type_guess": "sofa", "single_object": True, "real_product": True, "indoor": "indoor",
        "upright": True, "size_plausible": True, "parts_open": False, "styles": ["modern"], "quality": 4,
        "front_shown": "front", "has_bedding": None, "has_pillows": None, "has_cushions": True, "contact": None}
OPEN_REASON = "a drawer, door or lid is open, or a part floats apart"          # the removal reason before UL216
LOGO_REASONS = {f"the vision check reads {RENDER_FINDINGS[f]}: {RENDER_FINDING_WHY[f]}"
                for f in ("brand_logo", "text_print")}                           # the removal reasons before UL215


def item(**kw):
    base = {"id": "abo_x", "type": "sofa", "kind": "furniture", "source": "abo", "licence": "CC-BY-4.0",
            "title": "Amazon Brand - Movian Dyvran 3-Seater Upholstered Sofa", "bbox_m": [1.97, 0.83, 0.83],
            "units_known": True, "front_axis": "-Y", "front_axis_confidence": "high", "up_axis": "+Z",
            "bbox_min_m": [-0.985, -0.415, 0.0], "bbox_max_m": [0.985, 0.415, 0.83], "origin_offset": [0.0, 0.0, 0.0],
            "polycount": 20000, "quality": [4, 4]}
    base.update(kw)
    return base


def decide(it, answer=None):
    return D.decide(it, CK.item_checks(it, CFG, KNOWN), answer, None, CFG)


# --------------------------------------------------------------------------
# A. the audit rules
# --------------------------------------------------------------------------

def test_an_open_part_is_a_flag_for_every_type():
    """UL216: an open drawer, door or lid keeps the model (a dresser with open doors may be used) with the flag
    ``open_parts`` and a note; the geometric checks stay as they are."""
    for it, answer in ((item(), SOFA),
                       (item(id="abo_d", type="dresser", title="Dresser with 6 drawers", bbox_m=[1.2, 0.48, 0.8],
                             bbox_min_m=[-0.6, -0.24, 0.0], bbox_max_m=[0.6, 0.24, 0.8]),
                        dict(SOFA, type_guess="dresser", has_cushions=None))):
        d = decide(it, dict(answer, parts_open=True))
        assert d["status"] in ("keep", "fix"), (it["type"], d)
        assert OPEN_REASON not in d["reasons"] and not d["vision_doubt"]
        assert d["flags"]["open_parts"] is True and D.OPEN_PARTS_NOTE in d["notes"]
        assert "open_parts" not in decide(it, answer)["flags"]


def test_a_logo_or_a_print_is_a_flag_with_its_reason():
    """UL215: the vision answer's logo or print, and a run render's (render_print), flag the model; never a reason."""
    for field, word in (("brand_logo", "logo"), ("text_print", "lettering")):
        d = decide(item(), dict(SOFA, **{field: True}))
        assert d["status"] == "keep" and not d["reasons"], d
        assert d["flags"]["logo_flag"] is True and word in d["flags"]["logo_reason"]
    sha = "e" * 64
    seen = {"run": "P5", "project": "real04", "view": "cam_x", "piece": "f_1"}
    rec = {"finding": "brand_logo", "detail": "the maker's name on the front", "seen_in": seen, "sha256_glb": sha}
    it = item(sha256_glb=sha, render_findings=[rec])
    check = CK.render_print_check(it)
    assert check["status"] == "remove"                               # the check itself still fires
    d = decide(it, SOFA)
    assert d["status"] == "keep" and check["reason"] not in d["reasons"]
    assert d["flags"]["logo_flag"] is True and d["flags"]["logo_reason"] == check["reason"]


def test_low_quality_and_no_real_product_still_remove_furniture():
    """Rule 1 of UL215 / UL216: a bad model stays out, with or without a logo or an open part."""
    d = decide(item(), dict(SOFA, quality=2, brand_logo=True, parts_open=True))
    assert d["status"] == "removed" and "vision quality 2 (<= 2)" in d["reasons"]
    assert d["flags"]["logo_flag"] is True and d["flags"]["open_parts"] is True
    obj = item(id="objaverse_x", source="objaverse", title="Sofa")
    d = decide(obj, dict(SOFA, real_product=False, brand_logo=True))
    assert d["status"] == "removed" and d["flags"]["logo_flag"] is True
    d = decide(item(), dict(SOFA, upright=False))                        # on its side: still a removal
    assert d["status"] == "removed"


def test_the_writer_copies_the_flags_and_the_quality_without_changing_the_decision_sha():
    d = decide(item(), dict(SOFA, brand_logo=True, parts_open=True))
    assert d["vision_quality"] == 4 and "vision_quality" not in d["flags"]
    plain = dict(d)
    plain.pop("vision_quality")
    assert W.decision_sha(d) == W.decision_sha(plain)              # the entries already written stay unchanged
    doc = {"entries": [dict(item(), audit={"status": "pending", "reasons": []})], "decor": []}
    W.apply_decisions(doc, {"abo_x": d}, "2026-10-30T00:00:00Z")
    e = doc["entries"][0]
    assert e["logo_flag"] is True and e["open_parts"] is True and "logo" in e["logo_reason"]
    assert e["audit"]["status"] == "keep" and e["audit"]["vision_quality"] == 4
    assert F.vision_quality_of(e) == 4.0


# --------------------------------------------------------------------------
# The catalogue
# --------------------------------------------------------------------------

def _cc_by(**kw):
    e = {"id": "3dwh_a", "type": "laptop", "kind": "object", "source": "3dwh", "licence": "CC-BY-4.0",
         "audit": {"status": "keep", "reasons": [], "vision_quality": 4}, "glb": "models/3dwh/a.glb",
         "bbox_m": [0.36, 0.28, 0.20], "real_product": True, "styles": []}
    e.update(kw)
    return e


def test_a_logo_flagged_entry_is_usable_in_relaxed_mode_only():
    clean, logo = _cc_by(), _cc_by(logo_flag=True, logo_reason="the vision check reads a maker's logo")
    assert C.usable(clean, "commercial") and C.commercial_safe(clean) and not C.logo_flagged(clean)
    assert C.usable(logo, "relaxed") and not C.usable(logo, "commercial") and not C.commercial_safe(logo)
    assert "logo" in C.unusable_reason(logo, "commercial") and C.unusable_reason(logo, "relaxed") is None
    assert not C.logo_flagged(None)
    nc = dict(logo, licence="CC-BY-NC-4.0")                          # both reasons are named
    why = C.unusable_reason(nc, "commercial")
    assert "licence" in why and "logo" in why


def test_the_committed_catalogue_loads_the_extras_and_keeps_no_open_part_or_logo_removal():
    """Catalog.extras holds the audited 3D Warehouse objects (no stage read them before); no entry is removed only for
    an open part or a logo; the laptops removed for their open lid alone are usable with the flag."""
    cat = C.load()
    assert len(cat.extras) > 1000 and any(e.get("type") == "laptop" for e in cat.extras)
    one = copy.deepcopy(next(e for e in cat.entries if not e.get("parametric")))
    one["id"] = "test_merge_one"
    merged = C.merge(cat.data, {"entries": [one], "decor": [], "extras": [_cc_by(id="3dwh_merged")]})
    assert len(merged["extras"]) == len(cat.extras) + 1 and merged["extras"][-1]["id"] == "3dwh_merged"
    only = []
    for e in cat.entries + cat.decor + cat.extras:
        a = e.get("audit") or {}
        rs = a.get("reasons") or []
        if a.get("status") == "removed" and rs and all(
                r == OPEN_REASON or r in LOGO_REASONS or r.startswith("a maker's logo") for r in rs):
            only.append(e["id"])
    assert not only, only
    laptops = [e for e in cat.extras if e.get("type") == "laptop" and e.get("open_parts")]
    assert len(laptops) >= 10 and all(C.usable(e, "relaxed") for e in laptops)
    assert all(any("UL215" in n for n in e["audit"].get("notes") or []) for e in laptops)


# --------------------------------------------------------------------------
# B. the library first
# --------------------------------------------------------------------------

def _cat(*extras):
    return SimpleNamespace(extras=list(extras))


def test_a_laptop_takes_the_best_audited_library_model():
    good = _cc_by(id="3dwh_good")
    logo = _cc_by(id="3dwh_logo", logo_flag=True, logo_reason="a logo")
    item = {"id": "d_1", "type": "laptop", "size": [0.38, 0.30]}
    a = F.fit_decor_item(dict(item), _cat(logo, good), "modern", mode="relaxed")
    assert a["method"] == "library" and a["asset_id"] == "3dwh_good" and a["target"] == "within"
    assert a["fit_scale"] == [1.0, 1.0, 1.0] and a["pick"]["rule"].startswith("library_first")
    assert a["pick"]["ids"] == ["3dwh_good", "3dwh_logo"]           # the same quality: the clean one first
    # a higher quality wins over the logo order; commercial mode never takes the logo model
    better_logo = _cc_by(id="3dwh_logo5", logo_flag=True, audit={"status": "keep", "reasons": [], "vision_quality": 5})
    assert F.fit_decor_item(dict(item), _cat(good, better_logo), "modern", mode="relaxed")["asset_id"] == "3dwh_logo5"
    assert F.fit_decor_item(dict(item), _cat(good, better_logo), "modern", mode="commercial")["asset_id"] == "3dwh_good"
    # too small a model is scaled up uniformly into the real range
    small = _cc_by(id="3dwh_small", bbox_m=[0.2, 0.15, 0.12])
    a = F.fit_decor_item(dict(item), _cat(small), "modern", mode="relaxed")
    assert a["fit_scale"][0] == a["fit_scale"][1] == a["fit_scale"][2] == 1.4 and abs(a["bbox_m"][0] - 0.28) < 1e-6


def test_no_better_model_keeps_the_procedural_build_with_a_library_gap():
    item = {"id": "d_2", "type": "laptop", "size": [0.38, 0.30]}
    weak = _cc_by(id="3dwh_weak", audit={"status": "keep", "reasons": [], "vision_quality": 3})
    it = dict(item)
    assert F.fit_decor_item(it, _cat(weak), "modern", mode="relaxed") is None
    assert it["library_gap"]["type"] == "laptop" and "rates 4" in it["library_gap"]["why"]
    it = dict(item)
    assert F.fit_decor_item(it, _cat(), "modern", mode="relaxed") is None
    assert "no audited laptop" in it["library_gap"]["why"]
    removed = _cc_by(audit={"status": "removed", "reasons": ["x"], "vision_quality": 5})
    fake = _cc_by(id="3dwh_fake", real_product=False)
    wide = _cc_by(id="3dwh_wide", bbox_m=[0.36, 0.60, 0.20])          # no uniform scale puts it in the range
    for bad in (removed, fake, wide):
        it = dict(item)
        assert F.fit_decor_item(it, _cat(bad), "modern", mode="relaxed") is None, bad["id"]
        assert it["library_gap"]["type"] == "laptop"


def test_a_tv_is_scaled_to_the_panel_width_and_a_wall_tv_is_not_library_first():
    tv = _cc_by(id="3dwh_tv", type="tv", bbox_m=[1.0, 0.2, 0.62])
    deep = _cc_by(id="3dwh_deep", type="tv", bbox_m=[1.2, 0.46, 0.8])
    it = {"id": "d_3", "type": "tv", "size": [1.4, 0.35]}
    a = F.fit_decor_item(dict(it), _cat(deep, tv), "modern", mode="relaxed")
    assert a["asset_id"] == "3dwh_tv" and a["fit_scale"] == [1.4, 1.4, 1.4] and abs(a["bbox_m"][0] - 1.4) < 1e-6
    wall = dict(it, tv={"mount": "wall"})
    F.fit_decor_item(wall, _cat(tv), "modern", mode="relaxed")
    assert "library_gap" not in wall                                   # the media wall's own panel


def test_the_fit_guard_allows_the_decor_library_gap():
    """The replay of real04 / real06 (30 Oct 2026): the gap note on a decor item is the fit's own record, like the
    furniture's ``library_gap``; ``assert_only_assets_changed`` lets it through and still refuses anything else."""
    before = {"furniture": [], "decor": [{"id": "d_7", "type": "laptop", "size": [0.38, 0.3]}]}
    after = copy.deepcopy(before)
    after["decor"][0]["library_gap"] = {"type": "laptop", "why": "none fits"}
    F.assert_only_assets_changed(before, after)
    after["decor"][0]["size"] = [0.5, 0.3]
    try:
        F.assert_only_assets_changed(before, after)
    except AssertionError:
        pass
    else:
        raise AssertionError("a changed decor size must be refused")


def test_the_committed_library_gives_real_laptops_in_relaxed_mode_only():
    cat = C.load()
    it = {"id": "d_4", "type": "laptop", "size": [0.38, 0.30]}
    a = F.fit_decor_item(dict(it), cat, "modern", mode="relaxed")
    assert a and a["method"] == "library" and F.vision_quality_of(cat.entry(a["asset_id"]) or
                                                                   next(e for e in cat.extras
                                                                        if e["id"] == a["asset_id"])) >= 4
    com = dict(it)
    assert F.fit_decor_item(com, cat, "modern", mode="commercial") is None       # 3D Warehouse is non-commercial
    assert "library_gap" in com


# --------------------------------------------------------------------------
# C. the report, the credits
# --------------------------------------------------------------------------

def test_the_fit_report_lists_the_decor_library_gaps_and_the_logo_assets():
    building = {"furniture": [], "decor": [
        {"id": "d_5", "type": "tv", "library_gap": {"type": "tv", "why": "none fits"}},
        {"id": "d_6", "type": "laptop", "asset": dict(_cc_by(), asset_id="3dwh_a", method="library",
                                                      licence_flag="none", commercial_safe=False, logo_flag=True)}]}
    text = F.fit_report(building)
    assert "## Decor library gaps" in text and "- tv: none fits (1 item(s): d_5)" in text
    assert "3dwh_a [logo]" in text


def test_the_credits_name_a_logo_model_as_not_commercial_safe():
    asset = {"asset_id": "3dwh_a", "licence": "CC-BY-4.0", "logo_flag": True, "logo_reason": "a logo on the lid"}
    f = CP._licence_fields(copy.deepcopy(asset))
    assert f["commercial_safe"] is False and f["logo_flag"] is True and f["logo_reason"] == "a logo on the lid"
    credit = {"credit": "x", "source": "3dwh", "asset_id": "3dwh_a", "licence": "CC-BY-4.0", "licence_flag": "none",
              "commercial_safe": False, "licence_url": "https://creativecommons.org/licenses/by/4.0/",
              "pieces": [("d_6", "laptop")], "kind": "model", "changes": "scaled", "logo_flag": True,
              "logo_reason": "a logo on the lid"}
    text = CP.attribution_text("These images", [credit], mode="relaxed")
    section = text.split("## 3. PoC-only assets")[1]
    assert "3dwh_a" in section and "a maker's logo or print on the model (a logo on the lid)" in section
    assert json.dumps(f)
