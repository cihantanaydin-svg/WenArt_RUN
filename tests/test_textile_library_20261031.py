"""Lesson UL231 (31 Oct 2026, user: "Change the rule on the curtain etc to be use, if is needed and better library
models can be used"): curtains and blinds take a better library model first, our textile build only when none is
better or none stretches to the window; a throw (draped over its host) stays our build."""
from __future__ import annotations

from wenart.furniture import fit as F


class _Cat:
    def __init__(self, decor):
        self.decor = decor
        self.entries = []
        self.extras = []


def _curtain(iid, quality=None, bbox=(2.2, 0.18, 2.6), styles=("modern", "minimal")):
    e = {"id": iid, "kind": "decor", "decor_type": "curtain", "type": "decor_curtain", "glb": f"{iid}.glb",
         "bbox_m": list(bbox), "source": "3dwh", "licence": "CC-BY-4.0", "licence_flag": "none",
         "commercial_safe": True, "audit": {"status": "keep"}, "styles": list(styles), "real_product": True}
    if quality is not None:
        e["audit"]["vision_quality"] = quality
    return e


def _item(w=2.0, h=2.5):
    return {"id": "dc_1", "type": "curtain", "size": [w, 0.08, h], "center": [0.0, 0.0, 0.01], "rotation_deg": 0.0}


def test_a_better_library_curtain_hangs_in_the_window_box():
    cat = _Cat([_curtain("good", quality=4), _curtain("unrated")])
    item = _item()
    asset = F.fit_decor_item(item, cat, "modern", mode="relaxed")
    assert asset is not None and asset["asset_id"] == "good" and asset["method"] == "library"
    assert asset["target"] == "within" and asset["bbox_m"][0] == 2.0 and asset["bbox_m"][2] == 2.5
    assert asset["pick"]["rule"].startswith("textile_library_first") and "library_gap" not in item
    assert F.TEXTILE_STRETCH[0] <= asset["fit_scale"][0] <= F.TEXTILE_STRETCH[1]


def test_no_better_model_keeps_our_curtain_with_the_reason():
    cat = _Cat([_curtain("unrated"), _curtain("poor", quality=2)])
    item = _item()
    assert F.fit_decor_item(item, cat, "modern", mode="relaxed") is None
    assert "rates better than our build" in item["library_gap"]["why"]


def test_a_better_model_that_cannot_stretch_to_the_window_is_not_used():
    cat = _Cat([_curtain("short", quality=5, bbox=(2.0, 0.15, 0.8))])     # a valance, not a full-drop curtain
    item = _item(h=2.5)
    assert F.fit_decor_item(item, cat, "modern", mode="relaxed") is None
    assert "stretches to the window" in item["library_gap"]["why"]


def test_a_model_of_another_style_is_not_used_and_throws_stay_ours():
    cat = _Cat([_curtain("classic", quality=5, styles=("classic",))])
    item = _item()
    assert F.fit_decor_item(item, cat, "modern", mode="relaxed") is None
    assert "throw" not in F.TEXTILE_LIBRARY_FIRST and "throw" in F.PROCEDURAL_DECOR_TYPES
