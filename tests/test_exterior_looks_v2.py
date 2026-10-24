"""Exterior upgrade of 24 Oct 2026 (user request: facade materials, no slab 'balcony', library doors and windows):
the facade scheme, the railing posts and the library opening plan (CPU, pure)."""
import math

from wenart.blender import exterior as E
from wenart.blender import facade as FA
from wenart.blender import opening_models as OM
from wenart.blender import shell as SH

LEVELS = [{"id": "L-1", "elevation": -3.0, "height": 3.0, "kind": "basement"},
          {"id": "L0", "elevation": 0.0, "height": 3.0, "kind": "floor"},
          {"id": "L1", "elevation": 3.0, "height": 3.0, "kind": "floor"}]


def _building():
    return {"walls": [{"id": "w1", "level_id": "L0", "start": [0.0, 0.0], "end": [10.0, 0.0]}],
            "openings": [{"id": "d1", "type": "door", "wall_id": "w1", "center": [4.0, 0.0], "width": 1.0}],
            "site": {"entrances": [{"door_id": "d1", "level_id": "L0", "main": True}]}}


def test_scheme_of_falls_back_to_the_default_family():
    assert FA.scheme_of({"family": "industrial"})["base"] == "brick_red"
    sch = FA.scheme_of({"family": "unknown"})
    assert sch["family"] == "unknown" and sch["main"] == FA.FACADE_SCHEMES["default"]["main"]
    assert FA.scheme_of(None)["family"] == "default"


def test_scheme_faces_frame_the_entrance_and_clad_the_basement():
    faces = FA.scheme_faces(_building(), {"family": "modern"}, LEVELS)
    accent, base = faces
    assert accent["material"] == "wood_cladding" and accent["wall_id"] == "w1" and accent["inferred"]
    (x0, _), (x1, _) = accent["span"]
    assert math.isclose(x0, 2.5) and math.isclose(x1, 5.5)              # door 1.0 m + 1.0 m margin each side
    assert accent["z_range"] == [-0.5, 3.0]                            # up to the next level
    assert base["level_id"] == "L-1" and base["material"] == "stone_wall_ledgestone"
    assert FA.on_span([4.0, 0.3], accent["span"]) and not FA.on_span([6.0, 0.0], accent["span"])


def test_scheme_without_an_accent_or_an_entrance_clads_only_the_basement():
    assert [f.get("level_id") for f in FA.scheme_faces(_building(), {"family": "industrial"}, LEVELS)] == ["L-1"]
    b = dict(_building(), site={})
    assert [f.get("level_id") for f in FA.scheme_faces(b, {"family": "modern"}, LEVELS)] == ["L-1"]


def test_resolve_looks_takes_the_scheme_when_nothing_names_the_facade():
    looks = E.resolve_looks({"facade": {}}, {"family": "rustic"})
    assert looks["facade"]["source"] == "fallback" and looks["facade"]["colour"] == "cream"
    assert looks["facade"]["rgb"] is not None and looks["facade"]["scheme"]["base"] == "stone_wall_rubble"


def test_railing_posts_reach_both_ends_and_stay_within_the_spacing():
    posts = SH.railing_posts((0.0, 0.0), (4.0, 0.0), 0.0)
    assert len(posts) == 4                                             # 4.0 m / 1.5 m -> 3 bays, 4 posts
    xs = sorted(sum(v[0] for v in verts) / len(verts) for verts, _ in posts)
    assert math.isclose(xs[0], SH.RAILING["post"] / 2) and math.isclose(xs[-1], 4.0 - SH.RAILING["post"] / 2)
    assert max(b - a for a, b in zip(xs, xs[1:])) <= SH.RAILING["post_every"] + 1e-9
    assert SH.railing_posts((0.0, 0.0), (0.0, 0.0), 0.0) == []


def _extra(i, kind, w, d, h, title, status="keep", flag="none", textured=True):
    return {"id": f"x{i}", "type": kind, "title": title, "glb": f"x{i}.glb", "bbox_m": [w, d, h],
            "audit": {"status": status}, "licence_flag": flag, "textured": textured}


EXTRAS = [_extra(1, "door", 0.95, 0.16, 2.05, "Front Door"),
          _extra(2, "door", 2.4, 0.18, 2.1, "Sliding Double Door"),
          _extra(3, "window", 1.2, 0.12, 1.2, "Window 3"),
          _extra(4, "window", 1.2, 0.12, 1.2, "Window pack", ),                     # a pack: never
          _extra(5, "window", 0.6, 0.1, 1.2, "Casement window", flag="no_derivatives"),
          _extra(6, "door", 0.9, 0.1, 2.0, "Closet door")]


def _outer(oid, kind, width, bottom, top):
    return {"opening": {"id": oid, "type": kind, "width": width}, "bottom": bottom, "top": top}


def test_opening_plan_picks_one_model_per_category_and_panels_long_windows():
    outer = [_outer("d1", "door", 1.0, 0.0, 2.1), _outer("d2", "door", 2.4, 0.0, 2.1),
             _outer("w1", "window", 3.6, 0.9, 2.1), _outer("w2", "window", 0.3, 1.8, 2.1)]
    plan = OM.plan(_building(), outer, EXTRAS)
    assert plan["d1"]["category"] == "entrance" and plan["d1"]["asset"]["asset_id"] == "x1"
    assert plan["d2"]["category"] == "glazed_door" and plan["d2"]["asset"]["asset_id"] == "x2"
    assert plan["w1"]["asset"]["asset_id"] == "x3" and plan["w1"]["panels"] == 3
    assert "w2" not in plan                                             # 0.3 x 0.3: no model of that shape
    assert plan["d1"]["panels"] == 1 and "not its product" in plan["d1"]["reason"]


def test_opening_candidates_respect_audit_licence_and_words():
    assert [e["id"] for e in OM.candidates(EXTRAS, "window", "relaxed")] == ["x3"]
    nc = [_extra(7, "window", 1.2, 0.1, 1.2, "Window", flag="non_commercial")]
    assert OM.candidates(nc, "window", "relaxed") and not OM.candidates(nc, "window", "commercial")
    assert not OM.candidates([_extra(8, "window", 1.2, 0.1, 1.2, "Window", status="drop")], "window", "relaxed")
    assert [e["id"] for e in OM.candidates(EXTRAS, "door", "relaxed")] == ["x1"]
