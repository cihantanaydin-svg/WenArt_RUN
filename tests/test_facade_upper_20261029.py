"""29 Oct 2026 (user on real06 run 20261028-154514-full: "Outside wall texture can be changed"; lesson UL100): a house
of two or more storeys takes its style family's upper-storey cladding on the top storey, and Argus U26 finds a house
left one render (CPU, pure)."""
from wenart.audit import lessons as L
from wenart.blender import facade as FA


def _levels(*kinds):
    return [{"id": f"L{i}", "kind": k, "elevation": 3.0 * i, "height": 2.8} for i, k in enumerate(kinds)]


def test_the_top_storey_of_a_two_storey_house_is_clad():
    b = {"levels": _levels("floor", "floor"), "walls": [], "openings": []}
    faces = FA.scheme_faces(b, {"family": "scandinavian"}, b["levels"])
    up = [f for f in faces if f.get("upper")]
    assert [(f["material"], f["level_id"]) for f in up] == [("wood_cladding", "L1")] and up[0]["inferred"]
    assert not [f for f in FA.scheme_faces(b, {"family": "mediterranean"}, b["levels"]) if f.get("upper")]
    one = {"levels": _levels("floor"), "walls": [], "openings": []}
    assert not [f for f in FA.scheme_faces(one, {"family": "scandinavian"}, one["levels"]) if f.get("upper")]
    base = {"levels": [dict(lv, elevation=lv["elevation"] - 3.0) for lv in _levels("basement", "floor")]}
    assert FA.upper_level(FA.scheme_of({"family": "modern"}), base["levels"]) is None     # one storey over a basement


def test_argus_finds_a_two_storey_house_left_one_render():
    b = {"levels": _levels("floor", "floor"), "facade": {"faces": []}}
    look = {"object": "exterior", "field": "facade", "value": "render",
            "reason": "facade scheme (scandinavian): render in white (no drawing, brief or style names the facade)"}
    got = L.one_render_facades(b, {"assumed": [look]})
    assert [(f["check"], f["target"], f["kind"]) for f in got] == [("U26", "L1", "taste")]
    clad = {"object": "L1", "field": "facade_scheme", "value": "wood_cladding", "reason": "facade scheme"}
    assert L.one_render_facades(b, {"assumed": [look, clad]}) == []
    drawn = dict(b, facade={"faces": [{"material": "brick_red", "side": "all"}]})
    assert L.one_render_facades(drawn, {"assumed": [look]}) == []
    assert "U26" in L.CHECK_LESSONS and L.CHECK_LESSONS["U26"] == ("UL100",)
