"""Milestone 13 track T6 CPU tests (docs/milestone13.md §13.1, §13.2; CLAUDE.md vegetation and site rules): the
hedge-row detector on synthetic rows and on real04's drawn symbols, the tree height classes and the inferred species,
the site platforms from the drawn areas and the level marks, the pool v2 parts, the backdrop and the haze shell, the
pure parts of the vegetation module, the site view's horizon rule, hedges as low obstacles of the camera check, the
facade kit and the two shell scripts. Every test here fails on the Milestone 12 code (no ``hedge_rows``, a 4 m
minimum tree height, no ``platforms``, a site view with the horizon above the frame, hedges unknown to the camera
model, no facade kit)."""
from __future__ import annotations

import copy
import json
import math
import os
import subprocess
from pathlib import Path

import pytest

from wenart import geometry as G
from wenart.blender import copies as CP
from wenart.blender import exterior as E
from wenart.blender import exterior_checks as X
from wenart.blender import facade as FA
from wenart.blender import geom2d
from wenart.blender import site as S
from wenart.blender import vegetation as VG
from wenart.sheets import exterior as EX

ROOT = Path(__file__).resolve().parents[1]
REAL04 = ROOT / "results" / "furniture" / "real04" / "building_final.json"
REAL04_SHEETS = ROOT / "results" / "furniture" / "real04" / "sheets.json"


def assert_walls_within_cap_or_blocked(pfs) -> list:
    """Review of round 3: every platform's tallest retaining wall is within RETAINING_MAX_M except on the edges its
    ``cap_exceeded`` names, each one where a stepped band had no room (``blocked_by``: another platform, the
    building, or band_max), so nothing over the cap is silent. Returns the exceedances ``[(id, edge, height, by)]``."""
    ids = {p["id"] for p in pfs}
    hedge_ids = {f"hedge_{k:03d}" for k in range(1, 100)}          # a drawn hedge stops a band (25 Oct 2026)
    found = []
    for p in pfs:
        over = p.get("cap_exceeded") or []
        assert (p["wall_max_m"] <= S.RETAINING_MAX_M + 1e-6) == (not over), (p["id"], p["wall_max_m"], over)
        if over:
            assert max(c["height_m"] for c in over) == pytest.approx(p["wall_max_m"], abs=1e-3)
        blocked = {b["edge"]: b.get("by") for b in p.get("band_blocked") or []}
        for c in over:
            assert c["blocked_by"] in ids | hedge_ids | {"building", "keep_out", "band_max", "band_side"}, (p["id"], c)
            if not p.get("parent"):
                assert blocked.get(c["edge"]) == c["blocked_by"], (p["id"], c, blocked)
            found.append((p["id"], c["edge"], c["height_m"], c["blocked_by"]))
    return found
REAL02 = ROOT / "results" / "furniture" / "real02" / "building_final.json"
EXAMPLE = json.loads((ROOT / "docs" / "examples" / "building_m10.example.json").read_text(encoding="utf-8"))


def _row(n: int, r: float = 0.35, pitch: float = 0.6, start=(0.0, 0.0), direction=(1.0, 0.0), tag: str = "s"):
    return [{"center": [start[0] + direction[0] * pitch * k, start[1] + direction[1] * pitch * k], "radius_m": r,
             "id": f"{tag}{k}"} for k in range(n)]


# --------------------------------------------------------------------------
# 1. Hedge rows (sheets.exterior.hedge_rows, site.hedges_of)
# --------------------------------------------------------------------------

def test_hedge_rows_on_synthetic_rows():
    rows = EX.hedge_rows(_row(12))
    assert len(rows) == 1
    h = rows[0]
    assert h["count"] == 12 and h["width_m"] == pytest.approx(0.7) and h["pitch_m"] == pytest.approx(0.6)
    assert h["length_m"] == pytest.approx(6.6) and h["height_class"] == "mid" and h["height_m"] == 1.2
    assert h["polyline"][0] == [0.0, 0.0] and h["polyline"][-1] == pytest.approx([6.6, 0.0])
    assert h["symbol_ids"] == [f"s{k}" for k in range(12)]
    # fewer than HEDGE_MIN_COUNT, a pitch over 1.5 x the diameter, or symbols over 0.6 m: trees, not a hedge
    assert EX.hedge_rows(_row(4)) == []
    assert EX.hedge_rows(_row(12, pitch=1.2)) == []                      # 1.2 > 1.5 x 0.7 = 1.05
    assert EX.hedge_rows(_row(12, r=0.8, pitch=1.0)) == []
    # two radii in one line stay two rows (equal radii within 1 cm)
    mixed = _row(6, r=0.35, tag="a") + _row(6, r=0.5, pitch=0.9, start=(10.0, 0.0), tag="b")
    assert sorted(r["radius_m"] for r in EX.hedge_rows(mixed)) == [0.35, 0.5]
    # an L-corner (a 90 degree turn) is two hedges; a gentle curve is one hedge with a bent polyline
    corner = _row(10, tag="x") + _row(10, start=(5.4, 0.6), direction=(0.0, 1.0), tag="y")
    assert sorted(r["count"] for r in EX.hedge_rows(corner)) == [10, 10]
    arc = [{"center": [20.0 * math.sin(a), 20.0 - 20.0 * math.cos(a)], "radius_m": 0.35, "id": f"c{k}"}
           for k, a in enumerate(math.radians(1.72) * k for k in range(14))]
    curve = EX.hedge_rows(arc)
    assert len(curve) == 1 and curve[0]["count"] == 14 and len(curve[0]["polyline"]) >= 3
    assert EX.hedge_height_class(0.25) == "low" and EX.hedge_height_class(0.5) == "high"


@pytest.mark.skipif(not REAL04_SHEETS.is_file(), reason="no committed real04 sheets.json")
def test_hedge_rows_on_the_real04_site_symbols():
    """real04 (docs/milestone13.md §1.7): 101 tree symbols of r 0.359 m in rows; the long rows along the plot edges
    and between the two blocks are hedges, the short 2-3 symbol stubs at their ends stay single shrubs."""
    trees = json.loads(REAL04_SHEETS.read_text(encoding="utf-8"))["exterior"]["site"]["trees"]
    assert len(trees) == 101 and {t["radius_m"] for t in trees} == {0.359}
    rows = EX.hedge_rows(trees)
    assert [r["count"] for r in rows] == [36, 31, 7, 7]
    assert [round(r["length_m"], 1) for r in rows] == pytest.approx([25.6, 21.7, 4.8, 4.8], abs=0.1)
    assert all(r["height_class"] == "mid" and r["height_m"] == 1.2 and r["width_m"] == pytest.approx(0.718) for r in rows)
    hedges, singles = EX.hedge_records(trees)
    assert [h["id"] for h in hedges] == ["hedge_001", "hedge_002", "hedge_003", "hedge_004"]
    assert len(singles) == 20 and sum(h["symbol_count"] for h in hedges) + len(singles) == 101
    for h in hedges:
        assert h["species"] is None and h["inferred"] is True and h["height_class"] == "mid"
        assert h["evidence"] and all(e["rule"] == "site_hedge_symbol" for e in h["evidence"])
        assert len(h["polyline"]) >= 2 and "hedge" in h["reason"]


@pytest.mark.skipif(not REAL04.is_file(), reason="no committed real04 building")
def test_hedges_of_the_committed_real04_building_and_their_symbols_leave_the_trees():
    b = json.loads(REAL04.read_text(encoding="utf-8"))
    hedges, taken = S.hedges_of(b, "mediterranean")
    assert len(hedges) == 4 and len(taken) == 81 and all(h["source"] == "decor_rows" for h in hedges)
    assert {h["species"] for h in hedges} == {"cherry_laurel"} and all(h["species_inferred"] for h in hedges)
    assert S.hedges_of(b, "mediterranean", detect=False) == ([], set())
    # the sheets record wins over the detector when the building carries site.hedges
    b2 = copy.deepcopy(b)
    b2["site"]["hedges"] = [{"id": "hx", "polyline": [[0, 0], [8, 0]], "width_m": 0.6, "height_class": "high",
                             "species": "privet", "symbol_ids": ["sd_L0_007"], "evidence": []}]
    hs, tk = S.hedges_of(b2, "mediterranean")
    assert [h["id"] for h in hs] == ["hx"] and hs[0]["height_m"] == 1.8 and hs[0]["species"] == "privet"
    assert not hs[0]["species_inferred"] and tk == {"sd_L0_007"} and hs[0]["source"] == "site.hedges"
    terrain = {"kind": "flat", "z": {k: 0.0 for k in S.AXES}}
    v, f, info = S.hedge_parts(hedges[0], terrain)
    assert info["length_m"] == pytest.approx(25.5, abs=0.2) and info["top_z"] == pytest.approx(1.2)
    # round 3: the core is a hull with rounded shoulders (a 10-point profile: 2 caps + 10 sides per step), one
    # step per polyline segment on flat ground
    assert info["core"] == "hull" and info["top_round_m"] == 0.2 and len(f) == 12 * info["segments"]


# --------------------------------------------------------------------------
# 2. Tree height by crown class, climate and species
# --------------------------------------------------------------------------

def test_tree_height_classes_and_no_four_metre_minimum():
    assert S.tree_height(0.359) == (0.862, "shrub")                      # real04's symbol: a shrub, not a 4 m tree
    assert S.tree_height(1.0) == (2.4, "shrub")
    assert S.tree_height(1.5) == (4.8, "small") and S.tree_height(2.0) == (6.0, "small")
    assert S.tree_height(2.5) == (8.0, "medium") and S.tree_height(3.0) == (9.6, "medium")
    assert S.tree_height(4.0) == (12.8, "large") and S.tree_height(6.0) == (15.0, "large")
    heights = [S.tree_height(r)[0] for r in (0.2, 0.5, 1.0, 1.49, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 8.0)]
    assert heights == sorted(heights) and 0.4 <= heights[0] and heights[-1] <= 15.0
    assert "tree_min_height" not in S.DEFAULTS
    terrain = {"kind": "flat", "z": {k: 0.0 for k in S.AXES}}
    shrub = S.tree_parts({"id": "t", "kind": "tree", "center": [1.0, 1.0], "size": [0.718, 0.718]}, terrain, "mediterranean")
    assert shrub["size_class"] == "shrub" and shrub["trunk"] is None and shrub["height"] < 1.0
    assert shrub["species"] == "oleander" and shrub["species_inferred"]
    tree = S.tree_parts({"id": "t", "kind": "tree", "center": [1.0, 1.0], "size": [3.5, 3.5]}, terrain, "mediterranean")
    assert tree["size_class"] == "small" and tree["height"] == pytest.approx(5.6) and tree["trunk"] is not None
    assert tree["species"] == "olive"
    named = S.tree_parts({"id": "t", "kind": "tree", "center": [0, 0], "size": [8.0, 8.0], "species": "plane"}, terrain)
    assert named["species"] == "plane" and not named["species_inferred"] and named["size_class"] == "large"


def test_climate_from_the_brief_or_the_drawing_language_and_species_per_class():
    turkish = {"rooms": [{"label_raw": "SALON"}, {"label_raw": "MUTFAK"}, {"label_raw": "YATAK ODASI"}],
               "site": {"areas": [{"label_raw": "OTOPARK ALANI"}]}}
    c = S.climate_of(turkish)
    assert c["climate"] == "mediterranean" and c["inferred"] and "mutfak" in c["evidence"] and c["ask"]
    english = {"rooms": [{"label_raw": "LIVING ROOM"}, {"label_raw": "KITCHEN"}], "site": {}}
    assert S.climate_of(english)["climate"] == "temperate"
    # 27 Oct 2026 (generality review): whole words only, no place names of one project, a named location wins
    french = {"rooms": [{"label_raw": "SALON"}, {"label_raw": "CUISINE"}], "site": {"areas": [{"label": "VILLA"}]}}
    assert S.climate_of(french)["climate"] == "temperate"
    assert S.climate_of({"rooms": [{"label_raw": "KATALOG"}, {"label_raw": "HOLDING"}]})["climate"] == "temperate"
    inland = dict(turkish, project={"brief": {"site": {"location": "Çankaya, Ankara"}}})
    assert S.climate_of(inland)["climate"] == "temperate" and S.climate_of(inland)["evidence"] == ["ankara"]
    coast = {"rooms": [], "project": {"brief": {"location": "Bodrum, Muğla"}}}
    assert S.climate_of(coast)["climate"] == "mediterranean" and "ask" not in S.climate_of(coast)
    assert S.climate_of({"rooms": [{"label_raw": "GİRİŞ"}, {"label_raw": "ÇOCUK ODASI"}]})["climate"] == "mediterranean"
    explicit = dict(turkish, project={"brief": {"climate": "temperate"}})
    assert S.climate_of(explicit) == {"climate": "temperate", "source": "brief.climate", "inferred": False,
                                      "evidence": ["temperate"]}
    for climate, table in S.SPECIES_BY_CLIMATE.items():
        for cls in ("shrub", "small", "medium", "large"):
            assert S.species_for(cls, climate) in VG.SPECIES and VG.SPECIES[S.species_for(cls, climate)]["crown"] != "hedge"
        for cls in ("low", "mid", "high"):
            assert VG.SPECIES[S.species_for(cls, climate, kind="hedge")]["crown"] == "hedge"
    assert S.species_for("small", "mediterranean") == "olive" and S.species_for("large", "mediterranean") == "plane"


def test_the_species_table_resolves_to_verified_sources():
    """Every Poly Haven id was checked on api.polyhaven.com/info/<id> (type 2 = model) on 15 Oct 2026; every Sapling
    preset is one of the add-on's nine preset files."""
    assert set(S.SPECIES_BY_CLIMATE["mediterranean"].values()) <= set(VG.SPECIES)
    for name, rec in VG.SPECIES.items():
        src = rec["source"]
        assert set(src) == {"polyhaven", "sapling"}
        assert src["polyhaven"] is None or src["polyhaven"] in VG.POLYHAVEN_MODELS
        assert src["sapling"] is None or src["sapling"] in VG.SAPLING_PRESETS
        assert rec["crown"] in ("round", "spreading", "columnar", "umbrella", "conical", "palm", "shrub", "hedge")
        assert len(rec["colour"]) == 3 and all(0.0 <= c <= 1.0 for c in rec["colour"])
        assert rec["shape"] is None or rec["shape"] in VG.SAPLING_SHAPES
        assert VG.species_record(name)["name"] == name
    for aid, m in VG.POLYHAVEN_MODELS.items():
        assert m["height_m"] > 0 and m["polycount"] > 0 and m["kind"] in ("tree", "shrub", "grass")
    assert VG.species_record("no such species")["name"] == "generic_broadleaf"
    assert VG.POLYHAVEN_LICENCE == "CC0" and VG.LEAF_LICENCE == "CC0"
    assert set(VG.SAPLING_TOP_PER_SCALE) == set(VG.SAPLING_PRESETS)


# --------------------------------------------------------------------------
# 3. Platforms, pools, backdrop, haze, levers
# --------------------------------------------------------------------------

def _sloped_site(points=((-10, -10, -2.0), (30, -10, 0.0), (-10, 30, 1.0), (30, 30, 3.0), (10, 10, 0.5))):
    from wenart.levels import terrain as T
    surface = T.fit_surface(list(points))
    return {"ground": {"surface": surface, "points": [], "levels": []}, "paving": [], "parking": [], "pools": []}


def test_platforms_one_level_each_with_their_edge_treatment():
    site = _sloped_site()
    site["paving"] = [{"id": "sp_001", "polygon": [[0, 0], [8, 0], [8, 5], [0, 5]], "source": "site_plan", "build": True,
                       "area_id": "sa_terrace"}]
    site["parking"] = [{"id": "spk_001", "polygon": [[12, 0], [20, 0], [20, 6], [12, 6]], "build": True}]
    site["pools"] = [{"id": "pool_001", "polygon": [[2, 5.3], [6, 5.3], [6, 8.3], [2, 8.3]], "build": True},
                     {"id": "pool_002", "polygon": [[22, 20], [28, 20], [28, 23], [22, 23]], "build": True}]
    pfs = S.platforms(site)
    by = {p["id"]: p for p in pfs}
    assert set(by) == {"sp_001", "spk_001", "pool_002_deck"}
    t = by["sp_001"]
    assert t["kind"] == "terrace" and t["z_source"] == "the mean ground under it" and not t["sloped"]
    assert abs(t["z"] / S.PLATFORM["round"] - round(t["z"] / S.PLATFORM["round"])) < 1e-6      # rounded to 5 cm
    assert t["ground"]["min"] <= t["z"] <= t["ground"]["max"] and t["edge"] in ("steps", "retaining")
    assert t["pools"] == ["pool_001"] and len(t["holes"]) == 1          # the pool beside the terrace joins its deck
    assert G.polygon_area(t["polygon"]) > 40.0                           # the deck ring grew the terrace polygon
    assert by["spk_001"]["kind"] == "parking" and by["spk_001"]["edge"] in ("kerb", "retaining", "steps")
    deck = by["pool_002_deck"]
    assert deck["kind"] == "pool" and deck["pools"] == ["pool_002"] and len(deck["holes"]) == 1
    assert all(p["inferred"] and "level" in p["reason"] for p in pfs)
    # level marks inside the polygon set the level; marks that spread over 1 m say the area is drawn sloped
    site["ground"]["points"] = [{"x": 4.0, "y": 2.0, "z": 1.0, "kind": "ground_finished", "mark_id": "lm_1"}]
    t2 = next(p for p in S.platforms(site) if p["id"] == "sp_001")
    assert t2["z"] == 1.0 and t2["z_source"] == "level marks" and t2["marks"] == ["lm_1"]
    site["ground"]["points"].append({"x": 14.0, "y": 3.0, "z": -1.0, "kind": "ground_finished", "mark_id": "lm_2"})
    site["ground"]["points"].append({"x": 19.0, "y": 3.0, "z": 1.5, "kind": "ground_finished", "mark_id": "lm_3"})
    park = next(p for p in S.platforms(site) if p["id"] == "spk_001")
    assert park["sloped"] and park["edge"] == "kerb" and set(park["marks"]) == {"lm_2", "lm_3"}
    # a flat site: no retaining wall, a terrace is flush (none), a parking gets its kerb
    flat = {"ground": {"levels": [{"side": "all", "z": {"value": 0.0}}]}, "paving": site["paving"], "parking": site["parking"],
            "pools": []}
    flat_pfs = {p["id"]: p for p in S.platforms(flat)}
    assert flat_pfs["sp_001"]["edge"] == "none" and flat_pfs["spk_001"]["edge"] == "kerb"


def test_platform_parts_slab_walls_kerbs_steps_and_pool_v2():
    site = _sloped_site()
    site["paving"] = [{"id": "sp_001", "polygon": [[0, 0], [8, 0], [8, 5], [0, 5]], "build": True}]
    site["pools"] = [{"id": "pool_001", "polygon": [[2, 5.3], [6, 5.3], [6, 8.3], [2, 8.3]], "build": True}]
    pf = S.platforms(site)[0]
    terrain = {"kind": "tin", "surface": site["ground"]["surface"], "z": {}, "rect": [0, 0, 8, 5]}
    parts = {p["part"]: p for p in S.platform_parts(pf, terrain)}
    assert "slab" in parts and "wall" in parts
    assert max(v[2] for v in parts["slab"]["verts"]) == pytest.approx(pf["z"])
    assert max(v[2] for v in parts["wall"]["verts"]) >= pf["z"] + S.PLATFORM["lip"] - 1e-6
    if pf["steps_edge"] is not None:
        assert "steps" in parts and parts["steps"]["faces"]
    pool = {"id": "pool_001", "polygon": [[2, 5.3], [6, 5.3], [6, 8.3], [2, 8.3]], "depth": 1.5}
    pp = S.pool_parts(pool, terrain, deck_z=pf["z"])
    assert pp["edge_z"] == pf["z"] and pp["floor_z"] == pytest.approx(pf["z"] - 1.5)
    assert pp["water_z"] == pytest.approx(pf["z"] - S.POOL_WATER_DROP_M) and pp["coping_z"] == pytest.approx(pf["z"] + S.PLATFORM["lip"])
    wv, wf = pp["water"]
    assert len(wf) == 6 and min(v[2] for v in wv) == pytest.approx(pp["floor_z"] + S.POOL_WATER_BOTTOM_M)   # a closed slab
    bv, bf = pp["basin"]
    assert len(bf) == 5 and max(v[2] for v in bv) == pytest.approx(pf["z"])                               # clipped under the deck
    cv, cf = pp["coping"]
    assert cf and max(v[2] for v in cv) == pytest.approx(pp["coping_z"])
    xs = [v[0] for v in cv]
    assert min(xs) == pytest.approx(2.0 - S.POOL_COPING_M) and max(xs) == pytest.approx(6.0 + S.POOL_COPING_M)
    # without a deck level the edge is the highest ground of the corners (the Milestone 12 rule)
    pp2 = S.pool_parts(pool, terrain)
    assert pp2["edge_z"] == pytest.approx(max(S.ground_z(terrain, x, y) for x, y in pool["polygon"]))
    # a sloped (draped) platform keeps the ground: slab and kerbs only
    sloped = dict(pf, sloped=True, edge="kerb", kind="parking", steps_edge=None, railing_edges=[])
    kinds = {p["part"] for p in S.platform_parts(sloped, terrain)}
    assert kinds == {"slab", "kerb"}


def test_backdrop_ring_rises_and_the_haze_is_a_closed_hollow_shell():
    terrain = {"kind": "flat", "z": {k: 0.0 for k in S.AXES}}
    inner = [(-10.0, -10.0), (10.0, -10.0), (10.0, 10.0), (-10.0, 10.0)]
    v, f = S.backdrop_faces(inner, terrain, outer_reach=500.0, rise=20.0)
    assert len(f) == 4 and len(v) == 16
    assert max(p[2] for p in v) == pytest.approx(20.0) and min(p[2] for p in v) == 0.0
    assert max(abs(p[0]) for p in v) == pytest.approx(510.0)
    for q in f:                                                       # every quad faces up
        area = sum(v[q[i]][0] * v[q[(i + 1) % 4]][1] - v[q[(i + 1) % 4]][0] * v[q[i]][1] for i in range(4))
        assert area > 0
    hv, hf = S.haze_box(inner, (0.0, 10.0))
    assert len(hv) == 16 and len(hf) == 12
    outer_normals = [geom2d.face_normal(hv, q) for q in hf[:6]]
    inner_normals = [geom2d.face_normal(hv, q) for q in hf[6:]]
    centre = (0.0, 0.0, 5.0)
    for q, n in zip(hf[:6], outer_normals):                           # the outer shell faces out, the inner one in
        c = geom2d.face_center(hv, q)
        assert sum((c[i] - centre[i]) * n[i] for i in range(3)) > 0
    for q, n in zip(hf[6:], inner_normals):
        c = geom2d.face_center(hv, q)
        assert sum((c[i] - centre[i]) * n[i] for i in range(3)) < 0
    assert 0 < S.HAZE["density"] < 0.01


def test_site_levers_from_the_environment(monkeypatch):
    assert S.site_levers("all") == {k: True for k in S.SITE_LEVERS}
    assert S.site_levers("base") == {k: False for k in S.SITE_LEVERS}
    assert S.site_levers("hedge+pools") == {k: k in ("hedge", "pools") for k in S.SITE_LEVERS}
    monkeypatch.setenv(S.SITE_VARIANT_ENV, "sky")
    assert S.site_levers()["sky"] and not S.site_levers()["hedge"]
    monkeypatch.delenv(S.SITE_VARIANT_ENV)
    assert all(S.site_levers().values())
    with pytest.raises(ValueError):
        S.site_levers("lollipop")


@pytest.mark.skipif(not REAL04.is_file(), reason="no committed real04 building")
def test_site_plan_of_real04_carries_hedges_platforms_species_and_the_levers(monkeypatch):
    from wenart.blender import build as BB

    b = json.loads(REAL04.read_text(encoding="utf-8"))
    monkeypatch.delenv(S.SITE_VARIANT_ENV, raising=False)
    sp = BB.prepare(b, "base", None)["site"]
    assert [h["id"] for h in sp["hedges"]] == ["hedge_001", "hedge_002", "hedge_003", "hedge_004"]
    assert len(sp["trees"]) == 19 and sp["climate"]["climate"] == "mediterranean"
    primary = [p for p in sp["platforms"] if not p.get("parent")]
    # 25 Oct 2026: the terraces without a level mark take the floor their windows open over (the basement of each
    # twin block: -3.00 m, and 0.00 m for the copy b2 raised 3 m), as the marked twin sp_001 does
    assert sorted((p["id"], p["z"]) for p in primary) == [("sp_001", -3.0), ("sp_002", -3.0), ("sp_003", 0.0),
                                                          ("sp_004", 0.0), ("spk_001", 0.75)]
    assert all("the floor of L-1" in p["z_source"] for p in primary if p["id"] in ("sp_002", "sp_003", "sp_004"))
    assert not any(w["opening_id"] == "win_L-1_004" for w in sp["wells"])        # no front court cut into the deck
    # round 3: the stepped terraces (bands) of the steep terraces, every wall within the retaining cap except where a
    # band had no room (recorded with what blocked it; review of round 3)
    bands = [p for p in sp["platforms"] if p.get("parent")]
    assert bands and {b["parent"] for b in bands} <= {"sp_001", "sp_002", "sp_003", "sp_004"}
    assert_walls_within_cap_or_blocked(sp["platforms"])
    assert next(p for p in sp["platforms"] if p["id"] == "spk_001")["sloped"]
    assert {p["deck_z"] for p in sp["pools"]} == {-3.0, 0.0}
    assert all(a.get("platform_id") for a in sp["areas"] if a["kind"] in ("paving", "parking"))
    assert {v["species"] for v in sp["species"].values()} == {"oleander"} and all(v["inferred"] for v in sp["species"].values())
    assert {v["size_class"] for v in sp["species"].values()} == {"shrub"}
    fields = {a["field"] for a in sp["assumed"]}
    assert {"hedge:hedge_001", "platform:sp_001", "climate"} <= fields
    monkeypatch.setenv(S.SITE_VARIANT_ENV, "base")
    sp0 = BB.prepare(b, "base", None)["site"]
    assert sp0["hedges"] == [] and len(sp0["trees"]) == 100 and sp0["platforms"] == [] and not any(sp0["levers"].values())


# --------------------------------------------------------------------------
# 4. The pure parts of the vegetation module
# --------------------------------------------------------------------------

def test_vegetation_plans_hedge_crown_palm_and_sapling_overrides():
    plan = VG.hedge_plan({"polyline": [[0, 0], [20, 0]], "width_m": 0.7, "height_m": 1.2, "species": "cherry_laurel"})
    assert plan["length_m"] == 20.0 and plan["surface_m2"] == pytest.approx(63.68)
    # round 3: the density per species (hedge_density: the same cover for every leaf size), the hull core
    assert plan["density"] == VG.hedge_density(0.9) == 129.6 and plan["cards"] == round(63.68 * 129.6) == 8253
    assert plan["cover_layers"] == pytest.approx(VG.HEDGE_COVER_LAYERS, abs=0.05) and plan["core"] == "hull"
    assert plan["card_m"] == [0.18, 0.216] and plan["species"] == "cherry_laurel" and plan["tilt_deg"] == 45.0
    crown = VG.crown_plan("plane", 6.0, crown_m=5.0)
    assert crown["trunk_h"] == pytest.approx(1.8) and crown["crown_rx"] == 2.5 and crown["crown_rz"] == pytest.approx(2.1)
    assert crown["shells"] == 2 and crown["cards"] > 100 and crown["crown"] == "spreading"
    shrub = VG.crown_plan("oleander", 0.86, crown_m=0.72)
    assert shrub["trunk_h"] == 0.0 and shrub["shells"] == 1 and shrub["crown_rz"] == pytest.approx(0.43)
    palm = VG.palm_plan(7.0, seed=3)
    assert len(palm["fronds"]) == 14 and palm == VG.palm_plan(7.0, seed=3) and palm != VG.palm_plan(7.0, seed=4)
    assert all(-35.0 <= f["pitch_deg"] <= 25.0 for f in palm["fronds"])
    over = VG.sapling_overrides("olive", 5.6, 7)
    assert over["scale"] == pytest.approx(5.6 / VG.SAPLING_TOP_PER_SCALE["small_maple"], abs=1e-3)
    assert over["scaleV"] == 0.0 and over["shape"] == VG.SAPLING_SHAPES["hemispherical"] and over["seed"] == 7
    # round 3 (P1 'sapling': bare branches): the add-on's own 'rect' leaf quads, leaves on, the preset's count
    assert over["leafShape"] == "rect" and over["showLeaves"] and over["bevel"] and not over["useArm"]
    assert over["leaves"] == VG.SAPLING_LEAVES_DEFAULT and over["leafScale"] == VG.SAPLING_LEAF_M
    assert over["leafScaleX"] == 1.0 and over["leafScaleV"] == VG.SAPLING_LEAF_SCALE_V and over["bend"] == 0.0
    with_preset = VG.sapling_overrides("olive", 5.6, 7, {"leaves": 32, "showLeaves": False, "leafShape": "hex"})
    assert with_preset["leaves"] == 32 and with_preset["showLeaves"] and with_preset["leafShape"] == "rect"
    assert "attractUp" in VG.sapling_overrides("cypress", 8.0, 1)
    assert len(VG.leaf_mask_points()) == 16 and 0 < VG.LEAF_MASK_EDGE < 0.5


def test_tree_source_decision_and_the_hero_model_lookup(tmp_path):
    hero = {"id": "island_tree_02", "path": "x", "height_m": 3.4, "licence": "CC0"}
    on = {"instances": True, "sapling": True}
    assert VG.tree_source("olive", True, on, hero, True) == "polyhaven"
    assert VG.tree_source("olive", False, on, hero, True) == "sapling"           # far from the cameras
    assert VG.tree_source("olive", True, {"instances": False, "sapling": True}, hero, True) == "sapling"
    assert VG.tree_source("olive", True, {"instances": False, "sapling": False}, hero, True) == "cards"
    assert VG.tree_source("olive", False, on, None, False) == "cards"
    assert VG.tree_source("palm", False, on, None, True) == "palm"
    assert VG.tree_source("oleander", False, on, None, True) == "cards"           # shrubs never go through Sapling
    # the hero model: only when the assets manifest records the glTF and the file exists
    assets = tmp_path / "assets"
    (assets / "models" / "island_tree_02").mkdir(parents=True)
    gltf = assets / "models" / "island_tree_02" / "island_tree_02_2k.gltf"
    gltf.write_text("{}", encoding="utf-8")
    manifest = {"models": {"island_tree_02": {"files": {"gltf": "models/island_tree_02/island_tree_02_2k.gltf"},
                                              "bbox_m": [8.5, 4.1, 3.41], "bbox_min_m": [0, 0, 0.02], "polycount": 1762064}}}
    (assets / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    h = VG.hero_model("olive", manifest, assets)
    assert h["id"] == "island_tree_02" and h["path"] == str(gltf) and h["height_m"] == 3.41 and h["licence"] == "CC0"
    assert VG.hero_model("stone_pine", manifest, assets) is None                # no CC0 scan for that species
    assert VG.hero_model("olive", {}, assets) is None and VG.hero_model("olive", manifest, tmp_path / "nowhere") is None
    assert VG.leaf_atlas("olive", {}, assets) is None
    assert VG.sapling_preset("not_a_preset") is None


# --------------------------------------------------------------------------
# 5. Cameras: the site view's horizon, hedges as low obstacles, one aerial
# --------------------------------------------------------------------------

def test_site_view_keeps_the_horizon_in_the_frame():
    # Milestone 12: 24 mm, 28 degrees down -> the horizon above the frame (the black band of real04's ext_7)
    assert CP.horizon_fraction(28.0, 24.0) > 1.0
    assert CP.horizon_fraction(0.0, 24.0) == pytest.approx(0.5)
    pitch = CP.pitch_for_horizon(CP.SITE_VIEW_HORIZON_FRAC, CP.SITE_VIEW_LENS_MM)
    assert 0 < pitch <= CP.SITE_VIEW_PITCH_DEG and CP.horizon_fraction(pitch, 24.0) == pytest.approx(0.78, abs=1e-3)
    assert CP.pitch_for_horizon(1.5, 24.0) == CP.SITE_VIEW_PITCH_DEG                 # the cap
    b = {"site": {"buildings": [{"id": "b1", "reference": True, "translate": [0, 0], "dz": 0.0, "footprint": []},
                                {"id": "b2", "reference": False, "rotation_deg": 0.0, "translate": [0.0, 18.6],
                                 "dz": 3.0, "footprint": [[0, 18.6], [15.2, 18.6], [15.2, 30.6], [0, 30.6]]}]}}
    sv = CP.site_view([(0, 0), (15.2, 0), (15.2, 12.0), (0, 12.0)], b, (-3.0, 6.0))
    assert sv["pitch_deg"] == pitch and 1 / 3 < sv["horizon_frac"] < 1.0
    assert sv["position"][2] - sv["target"][2] >= CP.SITE_VIEW_MIN_HEIGHT_M - 1e-6
    d = math.hypot(sv["position"][0] - sv["target"][0], sv["position"][1] - sv["target"][1])
    assert math.degrees(math.atan2(sv["position"][2] - sv["target"][2], d)) == pytest.approx(pitch, abs=0.05)


def _box_building(hedges=(), hedge_height=1.2):
    pts = [(0, 0), (10, 0), (10, 8), (0, 8)]
    walls = [{"id": f"w{i}", "level_id": "L0", "start": list(pts[i]), "end": list(pts[(i + 1) % 4]), "thickness": 0.25,
              "exterior": True} for i in range(4)]
    site = {"ground": {"levels": [{"side": "all", "z": {"value": 0.0, "method": "vector"}}]}, "decor": [],
            "boundary_walls": [], "plot": {"polygon": [[-15, -15], [25, -15], [25, 23], [-15, 23]], "build": True},
            "hedges": [{"id": f"h{k}", "polyline": [list(a), list(b)], "width_m": 0.7, "height_m": hedge_height,
                        "height_class": "mid", "inferred": True, "evidence": []} for k, (a, b) in enumerate(hedges)]}
    return {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.8}], "walls": walls, "openings": [],
            "rooms": [], "slabs": [], "site": site, "facade": {}}


def _model(b):
    outline, _ = geom2d.wall_outline(b["walls"])
    plan = S.site_plan(b, b["levels"], outline, "full", options={"path": False, "fence": "none", "trees": 0})
    return E.build_model(b, b["levels"], None, plan), plan


def test_view_check_treats_hedges_as_obstacles_of_their_height():
    hedge = [((-20.0, -6.0), (30.0, -6.0))]
    b = _box_building(hedge, 1.2)
    m, plan = _model(b)
    assert len(plan["hedges"]) == 1 and m.labels.count(E.LABELS["hedge"]) > 0 and len(m.hedges) == 1
    assert m.inside((5.0, -6.0, 0.6)) == "hedge" and m.inside((5.0, -6.0, 1.9)) is None
    pts = E.building_points(m)
    pos, target = (5.0, -16.0, 1.6), (5.0, 4.0, 1.4)
    lens, shift_y, tgt, _w = E.frame(pos, target, pts, level=True)
    low = E.view_check(m, pos, tgt, lens, shift_y, (5.0, 0.0, 1.4))
    assert low["ok"] and low["hedge_over"] > 0.0 and low["hedge_blocked"] == 0.0 and low["blocked"] <= E.MAX_BLOCKED
    b2 = _box_building(hedge, 2.2)
    m2, _ = _model(b2)
    high = E.view_check(m2, pos, tgt, lens, shift_y, (5.0, 0.0, 1.4))
    assert high["hedge_blocked"] > 0.3 and not high["ok"] and "blocked" in high["why"]
    # a 1.2 m hedge all around the plot, 5 m out: every corner view is kept (the Milestone 12 model dropped a view
    # behind its 4 m "trees" of the hedge symbols)
    ring = [(-5, -5), (15, -5), (15, 13), (-5, 13)]
    b3 = _box_building([(ring[i], ring[(i + 1) % 4]) for i in range(4)], 1.2)
    m3, _ = _model(b3)
    plans, dropped = E.plan_exterior(m3, b3, b3["levels"], b3["site"]["plot"]["polygon"])
    assert [d["name"] for d in dropped if d["view"] == "corner"] == []
    assert all(p["score"]["hedge_over"] >= 0.0 for p in plans if p["view"] == "corner")


@pytest.mark.skipif(not REAL04.is_file(), reason="no committed real04 building")
def test_real04_exterior_views_behind_the_hedges_are_kept_and_the_site_view_sees_the_horizon(monkeypatch):
    from wenart.blender import build as BB

    monkeypatch.delenv(S.SITE_VARIANT_ENV, raising=False)
    b = json.loads(REAL04.read_text(encoding="utf-8"))
    prep = BB.prepare(b, "base", None)
    vb, sp = prep["building"], prep["site"]
    model = E.build_model(vb, vb["levels"], prep["roof"], sp)
    assert len(model.hedges) == 6                                      # 4 rows, one with 3 polyline segments
    plans, dropped = E.plan_exterior(model, vb, vb["levels"], sp["plot"] or [], variant="base")
    names = [p["name"] for p in plans]
    # M12 dropped ext_3 and ext_4. 24 Oct 2026: the roof is the drawn one (the agent's 45 degree override is refused),
    # 1.35 m lower, so from the back corner the trees and the plot wall hide 48 % or more of it: ext_4 goes again
    assert {"ext_1", "ext_2", "ext_3", "ext_5", "ext_7"} <= set(names)
    assert [d["name"] for d in dropped] == ["ext_4", "ext_6"] and "blocked by trees" in dropped[0]["dropped_reason"]
    assert "inside the copy" in dropped[1]["dropped_reason"]
    site_view = next(p for p in plans if p.get("site_view"))
    assert site_view["score"]["ok"] and 1 / 3 < site_view["horizon_frac"] < 1.0 and -28.0 <= site_view["pitch_deg"] < 0
    assert site_view["aerial_allowed"] and next(p for p in plans if p["name"] == "ext_5")["aerial_allowed"]
    for p in plans:
        if p["view"] == "corner":
            assert p["score"]["blocked"] <= E.MAX_BLOCKED and p["score"]["hedge_blocked"] <= E.MAX_BLOCKED


def test_x6_allows_one_true_aerial_view_and_notes_a_second():
    base = {"name": "ext_5", "kind": "exterior", "view": "aerial", "position": [30.0, 30.0, 20.0], "target": [5.0, 4.0, 1.5]}
    hits = []
    X._x6({}, {"outlines": {}, "roof": {}, "main_facade": {}}, {"cameras": [base, dict(base, name="ext_7", site_view=True)]},
          None, hits)
    assert not any("aerial views" in h["message"] for h in hits)
    hits = []
    X._x6({}, {"outlines": {}, "roof": {}, "main_facade": {}}, {"cameras": [base, dict(base, name="ext_9")]}, None, hits)
    second = [h for h in hits if "aerial views" in h["message"]]
    assert len(second) == 1 and second[0]["severity"] == "minor" and second[0]["metrics"]["aerials"] == ["ext_5", "ext_9"]


# --------------------------------------------------------------------------
# 6. The facade kit
# --------------------------------------------------------------------------

def test_facade_kit_only_where_the_documents_imply_it():
    from wenart import views as V
    from wenart.blender import build as BB

    b = V.variant_building(EXAMPLE, "base")
    prep = BB.prepare(EXAMPLE, "base", None)
    vb, sp = prep["building"], prep["site"]
    plan = FA.articulation_plan(vb, vb["levels"], prep["outlines"], prep["ground_outline"], sp["terrain"], prep["roof"],
                                {"family": "modern"}, {"facade": {"material": "render", "colour": "white"}}, sp["wells"])
    kinds = {x["kind"] for x in plan["boxes"]}
    assert "reveal" in kinds and "canopy" in kinds and "wall_light" in kinds
    kit = plan["kit"]
    assert kit["counts"]["canopy"] == len(kit["entrances"]) and kit["counts"]["wall_light"] == 2 * len(kit["entrances"])
    assert kit["eaves_edges"] > 0 and kit["counts"]["gutter"] == kit["eaves_edges"] and kit["counts"]["downpipe"] >= 1
    for box in plan["boxes"]:
        if box["kind"] in FA.KIT_KINDS:
            assert box["inferred"] and box["reason"] and all(v > 0 for v in box["size"])
    assert {k for k in plan["looks"] if k in FA.KIT_KINDS} == {k for k in kit["counts"]}
    assert {a["field"] for a in plan["assumed"] if a["field"].startswith("kit:")} == {f"kit:{k}" for k in kit["counts"]}
    # a classic family keeps its stone surrounds and gets no reveals
    classic = FA.articulation_plan(vb, vb["levels"], prep["outlines"], prep["ground_outline"], sp["terrain"], prep["roof"],
                                   {"family": "classic"}, {}, sp["wells"])
    assert "reveal" not in {x["kind"] for x in classic["boxes"]} and any(x["kind"] == "surround" for x in classic["boxes"])
    # a flat roof has no eaves: no gutters; no roof: none
    assert FA.eaves_edges(dict(prep["roof"], type="flat")) == [] and FA.eaves_edges(None) == []
    assert set(FA.KIT_LOOKS) == set(FA.KIT_KINDS)
    # the gutters hang just under the eaves, the downpipes reach the ground
    gutters = [x for x in plan["boxes"] if x["kind"] == "gutter"]
    assert all(abs(g["center"][2] + FA.KIT["gutter_h"] / 2 + FA.KIT["gutter_drop"] - prep["roof"]["eaves_z"]) < 1e-6 for g in gutters)
    pipes = [x for x in plan["boxes"] if x["kind"] == "downpipe" and x["size"][0] == x["size"][1]]
    assert all(p["size"][2] > 2.0 and p["center"][2] - p["size"][2] / 2 < 0.5 for p in pipes)
    # 24 Oct 2026: each pipe's outlet runs from the gutter to the pipe's top, square to the wall
    outlets = [x for x in plan["boxes"] if x["kind"] == "downpipe" and x["size"][0] != x["size"][1]]
    assert len(outlets) == len(pipes) and all(o["size"][2] == FA.KIT["downpipe"] for o in outlets)


@pytest.mark.skipif(not REAL02.is_file(), reason="no committed real02 building")
def test_facade_kit_of_real02_is_inferred_and_counted():
    from wenart.blender import build as BB

    b = json.loads(REAL02.read_text(encoding="utf-8"))
    prep = BB.prepare(b, "base", None)
    vb, sp = prep["building"], prep["site"]
    plan = FA.articulation_plan(vb, vb["levels"], prep["outlines"], prep["ground_outline"], sp["terrain"], prep["roof"],
                                {"family": "modern"}, {"facade": {"material": "render", "colour": "warm greige"}}, sp["wells"])
    counts = plan["kit"]["counts"]
    # 24 Oct 2026: the two roof terraces cut the east and west eaves away: gutters on the two eaves left
    assert counts["gutter"] == 2 and counts["canopy"] == 2 and counts["wall_light"] == 4 and counts["reveal"] == 24
    assert counts["downpipe"] >= 4 and plan["kit"]["entrances"] == ["d_L0_011", "d_L0_012"]


# --------------------------------------------------------------------------
# 7. The shell scripts
# --------------------------------------------------------------------------

@pytest.mark.parametrize("script", ["scripts/pod_setup_vegetation.sh", "scripts/jobs/site_ab.sh"])
def test_the_shell_scripts_parse_and_follow_the_conventions(script):
    path = ROOT / script
    assert path.is_file() and os.access(path, os.X_OK)
    subprocess.run(["bash", "-n", str(path)], check=True)
    text = path.read_text(encoding="utf-8")
    assert text.startswith("#!/usr/bin/env bash") and "set -Eeuo pipefail" in text
    assert "/workspace/logs" in text or "$WS/logs" in text          # (review: parenthesised; was A and B and C or D)
    if script.endswith("pod_setup_vegetation.sh"):
        assert "wenart.assets models fetch" in text and "--command extension install" in text
        assert "sapling_tree_gen" in text and "vegetation_status.json" in text and "user_default" in text
        assert "curl" not in text.replace("# ", "")                      # downloads only through the existing code
    else:
        for lever in S.SITE_LEVERS:
            assert lever in text
        assert "ext_1,ext_5,ext_7" in text and "ext_1,ext_5,ext_6" in text and "WENART_SITE_VARIANT" in text
        assert "vram" in text and "summary" in text and "tests/gpu/test_m13_site.py" in text


# --------------------------------------------------------------------------
# Round 2 (the lead's wiring items): agent camera overrides keep the D8 flags, the manifest records of metric 11,
# the vegetation instances of the 3D export, site.platforms into the building
# --------------------------------------------------------------------------

def test_agent_camera_overrides_keep_the_aerial_and_horizon_flags():
    """D8: the one true aerial view and the site view carry ``aerial_allowed`` / ``site_view`` / ``horizon_frac``
    (``cameras.REPLAY_OPTIONAL`` keeps them through a replay); an agent ``set`` of such a camera keeps them from the
    camera it replaces, an ``add`` takes them from the entry, and a plain corner camera gets none."""
    from wenart.blender import overrides as O

    # integration of the fix round after P4b (17 Oct 2026, pinned on purpose): the entrance view's door id too
    assert O.CAMERA_KEEP_KEYS == ("site_view", "aerial_allowed", "horizon_frac", "entrance")
    plans = [{"name": "ext_5", "kind": "exterior", "position": [0, 0, 20], "target": [5, 5, 0], "lens_mm": 24.0,
              "view": "aerial", "aerial_allowed": True, "index": 5},
             {"name": "ext_7", "kind": "exterior", "position": [0, -30, 12], "target": [5, 5, 0], "lens_mm": 24.0,
              "view": "site", "site_view": True, "aerial_allowed": True, "horizon_frac": 0.78, "index": 7},
             {"name": "ext_1", "kind": "exterior", "position": [0, -10, 1.6], "target": [5, 5, 1.6], "lens_mm": 24.0,
              "view": "corner", "index": 1}]
    entries = [{"action": "set", "view_id": "ext_5", "kind": "exterior", "position": [1, 1, 22], "target": [5, 5, 0],
                "reason": "higher"},
               {"action": "set", "view_id": "ext_7", "kind": "exterior", "position": [0, -32, 12], "target": [5, 5, 0],
                "reason": "further back"},
               {"action": "set", "view_id": "ext_1", "kind": "exterior", "position": [0, -12, 1.6],
                "target": [5, 5, 1.6], "reason": "back"},
               {"action": "add", "view_id": "ext_9", "kind": "exterior", "position": [0, 0, 25], "target": [5, 5, 0],
                "aerial_allowed": True, "reason": "a second aerial the critic may judge as such"}]
    out, applied = O.apply_cameras(plans, entries)
    by = {p["name"]: p for p in out}
    assert [a["result"] for a in applied] == ["replaced", "replaced", "replaced", "added"]
    assert by["ext_5"]["aerial_allowed"] is True and "site_view" not in by["ext_5"]
    assert by["ext_7"]["site_view"] is True and by["ext_7"]["aerial_allowed"] is True
    assert by["ext_7"]["horizon_frac"] == 0.78 and by["ext_7"]["position"] == [0.0, -32.0, 12.0]
    assert not any(k in by["ext_1"] for k in O.CAMERA_KEEP_KEYS)
    assert by["ext_9"]["aerial_allowed"] is True and by["ext_9"]["policy"] == "agent"
    # The critic's eye-level rule reads the same flag on the record.
    from wenart.blender import cameras as C
    assert all(k in C.REPLAY_OPTIONAL for k in O.CAMERA_KEEP_KEYS)


def test_vegetation_counts_per_source_for_metric_11():
    """The scene manifest's ``site.vegetation`` records carry ``kind: tree`` and a ``method`` (metrics13 counts
    every method that is not a primitive), ``site.hedges`` their method, and ``site.vegetation_counts`` the
    per-source numbers the lead asked for (Poly Haven instances, Sapling, leaf cards, hedges, grass patches)."""
    summary = {"vegetation": [{"id": "tree_1", "kind": "tree", "method": "polyhaven", "asset": "island_tree_02"},
                              {"id": "tree_2", "kind": "tree", "method": "sapling", "asset": "quaking_aspen"},
                              {"id": "tree_3", "kind": "tree", "method": "cards", "asset": None},
                              {"id": "tree_4", "kind": "tree", "method": "palm", "asset": None},
                              {"id": "tree_5", "kind": "tree", "method": "proxy", "asset": None}],
               "hedges": [{"id": "hedge_001", "method": "cards", "symbols": 36}, {"id": "hedge_002", "method": "box"}],
               "grass": {"method": "polyhaven", "asset": "grass_medium_02", "count": 1100}}
    counts = S.vegetation_counts(summary)
    assert counts == {"library": 0, "polyhaven_instances": 1, "sapling": 1, "leaf_card": 2, "proxy": 1, "trees": 5, "hedges": 2,
                      "hedges_leaf_card": 1, "grass_patches": 1}
    assert S.vegetation_counts({}) == {"library": 0, "polyhaven_instances": 0, "sapling": 0, "leaf_card": 0, "proxy": 0, "trees": 0,
                                       "hedges": 0, "hedges_leaf_card": 0, "grass_patches": 0}
    assert S.vegetation_counts({"grass": {"method": "none", "error": "x"}})["grass_patches"] == 0
    # metrics13 reads the records the way build_site writes them (kind defaults to tree, method not a primitive).
    from wenart.report import metrics13 as M13
    real = [r for r in summary["vegetation"] if r.get("kind", "tree") == "tree"
            and str(r.get("method") or "").lower() not in M13.VEGETATION_PRIMITIVES]
    assert len(real) == 4 == counts["polyhaven_instances"] + counts["sapling"] + counts["leaf_card"]


def test_instance_budget_realizes_the_smallest_groups_under_the_polygon_cap(monkeypatch):
    """The 3D export realizes the vegetation node groups (leaf cards, grass clumps) smallest first while the
    polygons stay under the cap; the rest stay instances with a reason. The cap comes from WENART_REALIZE_CAP
    (0 = nothing), else the documented 1 M polygons."""
    items = [{"group": "veg_scatter_cherry_laurel_120", "objects": ["hedge_001", "hedge_002"], "instances": 2617,
              "polygons": 5234},
             {"group": "veg_grass_polyhaven_4", "objects": ["grass_near"], "instances": 1100, "polygons": 1_210_000},
             {"group": "veg_scatter_olive_60", "objects": ["tree_sd_L0_001_outer"], "instances": 900, "polygons": 1800}]
    b = S.instance_budget(items, 10_000)
    assert [it["group"] for it in b["realize"]] == ["veg_scatter_olive_60", "veg_scatter_cherry_laurel_120"]
    assert b["polygons"] == 7034 and b["polygons_all"] == 1_217_034 and b["cap"] == 10_000
    assert [it["group"] for it in b["skipped"]] == ["veg_grass_polyhaven_4"]
    assert "would pass the cap of 10000" in b["skipped"][0]["reason"]
    assert S.instance_budget(items, 0) == {"cap": 0, "realize": [], "skipped": b["skipped"][:0] + [
        dict(it, reason=f"{it['polygons']} polygons would pass the cap of 0 (0 realized)")
        for it in sorted(items, key=lambda it: it["polygons"])], "polygons": 0, "polygons_all": 1_217_034}
    assert S.instance_budget([], 5)["realize"] == []
    monkeypatch.delenv(S.REALIZE_CAP_ENV, raising=False)
    assert S.realize_cap() == S.REALIZE_CAP_POLYS == 1_000_000
    assert S.realize_cap({S.REALIZE_CAP_ENV: "2500"}) == 2500 and S.realize_cap({S.REALIZE_CAP_ENV: "x"}) == 1_000_000
    assert S.realize_cap({S.REALIZE_CAP_ENV: "0"}) == 0
    assert S.VEGETATION_GROUP_PREFIX == "veg_"       # vegetation.scatter_group names every vegetation group so


@pytest.mark.skipif(not REAL04.is_file(), reason="no committed real04 building")
def test_platforms_into_the_building_after_the_levels_and_the_cli(tmp_path):
    """§13.3 ``site.platforms[]``: the pipeline_final stage's last step writes the platforms of ``site.platforms``
    (on the levels stage's ground model) into building.json; the records validate against the building schema and
    the CLI ``python -m wenart.blender.site platforms`` writes in place or to ``--out``."""
    from wenart import building as BM

    building = json.loads(REAL04.read_text(encoding="utf-8"))
    rec = S.platforms_into_building(building)
    pfs = building["site"]["platforms"]
    assert rec["count"] == len(pfs) >= 4 and rec["ids"] == [pf["id"] for pf in pfs]
    assert {pf["kind"] for pf in pfs} <= {"terrace", "pool", "parking", "path"}
    assert all(pf["edge"] in ("retaining", "kerb", "steps", "none") and len(pf["polygon"]) >= 3 for pf in pfs)
    assert all(isinstance(pf["z"], (int, float)) for pf in pfs)
    assert sum(rec["kinds"].values()) == rec["count"]
    BM.validate(building)                                  # the schema the lead added for the field
    # The same records as the build's site plan (the scene manifest's site.platforms), ids and levels.
    hedges = S.hedges_of(building, S.climate_of(building)["climate"])[0]
    plan = S.platforms(building["site"], keep_out=S.building_keep_out(building),      # the build's keep-out too
                       facades=S.building_facades(building),                         # and its floors (25 Oct 2026)
                       band_keep=S.hedge_keep_out(hedges))                           # and the drawn hedges
    assert [(pf["id"], pf["z"], pf["kind"], pf["edge"]) for pf in plan] == \
        [(pf["id"], pf["z"], pf["kind"], pf["edge"]) for pf in pfs]
    # Idempotent: a second call replaces the list with the same records.
    assert S.platforms_into_building(building)["ids"] == rec["ids"]
    # No site dict: left alone.
    assert S.platforms_into_building({"levels": []}) == {"count": None, "ids": [], "kinds": {}}
    # The CLI (the stage command of wenart.run.stages.site_platforms).
    src = tmp_path / "building.json"
    src.write_text(REAL04.read_text(encoding="utf-8"), encoding="utf-8")
    proc = subprocess.run([os.sys.executable, "-m", "wenart.blender.site", "platforms", str(src)],
                          capture_output=True, text=True, cwd=str(ROOT))
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.startswith("SITE_PLATFORMS ") and f"count={rec['count']}" in proc.stdout
    written = json.loads(src.read_text(encoding="utf-8"))
    assert [pf["id"] for pf in written["site"]["platforms"]] == rec["ids"]
    out = tmp_path / "other.json"
    proc = subprocess.run([os.sys.executable, "-m", "wenart.blender.site", "platforms", str(src), "--out", str(out)],
                          capture_output=True, text=True, cwd=str(ROOT))
    assert proc.returncode == 0 and out.is_file()
    bad = tmp_path / "bad.json"
    bad.write_text("[]", encoding="utf-8")
    assert subprocess.run([os.sys.executable, "-m", "wenart.blender.site", "platforms", str(bad)],
                          capture_output=True, text=True, cwd=str(ROOT)).returncode == 2


def test_m13_site_block_records_the_assets_dir_and_the_realized_instances():
    """Milestone 13 (T6, round 2): the manifest's site block says where the vegetation module found the assets
    (``assets``: WENART_ASSETS, the build's --assets handed over as the scene property ``wenart_assets_dir``, or a
    default candidate) and what ``site.realize_site_instances`` realized before the scene.glb export. Here and not
    in tests/test_blender_build.py (round-2 review, 15 Oct 2026): that module is skipped as a whole without a
    Blender binary, so a pure test there never runs on the CPU suite."""
    from wenart.blender import build as B

    assert B.assets_dir_record(None, None, None) == {"path": None, "source": None}
    assert B.assets_dir_record("/workspace/assets", "/ws/assets", "/workspace/assets") == \
        {"path": "/workspace/assets", "source": "env"}
    assert B.assets_dir_record(None, "/ws/assets", "/ws/assets") == {"path": "/ws/assets", "source": "build --assets"}
    assert B.assets_dir_record("/nope", "/ws/assets", "/workspace/assets") == \
        {"path": "/workspace/assets", "source": "default"}
    site = {"built": True, "objects": ["ground"]}
    rec = {"path": "/ws/assets", "source": "build --assets"}
    realized = {"cap": 1000000, "polygons": 7034, "realized": ["veg_scatter_olive_60"], "skipped": []}
    block = B.site_manifest_block(site, rec, realized)
    assert block == {"built": True, "objects": ["ground"], "assets": rec, "realized_instances": realized}
    assert site == {"built": True, "objects": ["ground"]}                 # a copy, the summary is untouched
    assert B.site_manifest_block(None, rec, realized) is None             # a building without a site
    # A site that is not built (an interior-only build: site_summary's block) keeps its block: the manifest schema's
    # SITE_LEFT_OUT allows only {count, ids} objects next to built and reason (round-2 review, 15 Oct 2026).
    assert B.site_manifest_block({"built": False}, None, None) == {"built": False}
    left = B.site_summary(json.loads(REAL02.read_text(encoding="utf-8")))
    assert left["built"] is False and B.site_manifest_block(left, rec, realized) == left
    import jsonschema
    from wenart.blender import schemas
    site_schema = schemas.SCENE_MANIFEST["properties"]["site"]
    jsonschema.validate(B.site_manifest_block(left, rec, realized), site_schema)
    built = {"built": True, "mode": "full", "reason": "x", "objects": [], "terrain": {"kind": "flat", "z": 0.0,
                                                                                      "changes": []}, "light_wells": []}
    jsonschema.validate(B.site_manifest_block(built, rec, realized), site_schema)
    jsonschema.validate(B.site_manifest_block(built, None, None), site_schema)


# --------------------------------------------------------------------------
# 7. Round 3 (pod P1 of 15 Oct 2026, docs/milestone13.md §14.3): the hedge hull and its cover, the Sapling leaf
#    properties, the retaining cap and the stepped terraces, the terrain record, the lawn tile, the export record
# --------------------------------------------------------------------------

def sapling_source() -> Path | None:
    """The Sapling Tree Gen add-on's ``__init__.py`` when its folder is known (``WENART_SAPLING_DIR``, the same
    variable ``vegetation.sapling_preset`` reads: the folder holding ``sapling_tree_gen`` or ``add_curve_sapling``),
    else None (the property check is skipped; the pod's Blender runs the GPU test against the installed add-on)."""
    folder = os.environ.get(VG.SAPLING_DIR_ENV)
    for pkg in (("sapling_tree_gen", "add_curve_sapling") if folder else ()):
        src = Path(folder) / pkg / "__init__.py"
        if src.is_file():
            return src
    return None


def _simple_polygon(poly) -> bool:
    """No two non-adjacent edges of ``poly`` cross (a bow-tie quad fails)."""
    def orient(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def cross(p0, p1, q0, q1):
        return orient(q0, q1, p0) * orient(q0, q1, p1) < 0 and orient(p0, p1, q0) * orient(p0, p1, q1) < 0

    n = len(poly)
    return not any(cross(poly[i], poly[(i + 1) % n], poly[j], poly[(j + 1) % n])
                   for i in range(n) for j in range(i + 2, n) if not (i == 0 and j == n - 1))


SAPLING_SRC = sapling_source()
P1_SITE = ROOT / "runs" / "20261015-165506-m13_p1" / "results" / "ab_m13" / "site" / "platforms" / "real04" / "site.json"


def test_round3_hedge_hull_profile_and_the_cover_behind_the_card_density():
    """P1 'hedge' row: the hedges read as boxes of yellow-green dots. The core is a hull with rounded shoulders,
    the card density follows a cover target per species (the round-1 60/m² gave 0.17-0.68 opaque layers)."""
    prof = S.hedge_hull_profile(0.7, 1.2)
    assert prof[0] == (-0.35, 0.0) and prof[1] == (0.35, 0.0) and max(z for _s, z in prof) == 1.2
    assert len(prof) == 10 and len(set(prof)) == 10                     # no repeated point
    assert all(abs(x) <= 0.35 + 1e-9 for x, _z in prof)
    assert (0.15, 1.2) in prof and (-0.15, 1.2) in prof                  # the flat top between the shoulders
    assert G.polygon_signed_area(prof) > 0 and len(geom2d.convex_hull(prof)) == 10      # convex
    assert S.hedge_hull_profile(0.7, 1.2, round_m=0.0) == [(-0.35, 0.0), (0.35, 0.0), (0.35, 1.2), (-0.35, 1.2)]
    assert len(S.hedge_hull_profile(0.3, 0.3)) == 9                    # a full half-round top: no flat segment
    # the hull follows a sloped ground in steps, like the plot walls
    terrain = {"kind": "sides", "z": {"+x": 0.0, "-x": -1.0, "+y": 0.0, "-y": 0.0}, "rect": [0, 0, 1, 1]}
    v, f, info = S.hedge_parts({"polyline": [[-6, 0.5], [6, 0.5]], "width_m": 0.6, "height_m": 1.0}, terrain)
    assert info["core"] == "hull" and info["segments"] == 1 and len(f) > 12
    assert info["z_range"] == [-1.1, 1.0]                                # 0.1 m under the -x ground, 1.0 over +x
    # the density: every hedge species gets HEDGE_COVER_LAYERS whatever its leaf size
    for name in VG.HEDGE_SPECIES:
        plan = VG.hedge_plan({"polyline": [[0, 0], [10, 0]], "width_m": 0.6, "height_m": 1.0, "species": name})
        assert plan["cover_layers"] == pytest.approx(VG.HEDGE_COVER_LAYERS, abs=0.05), name
        assert plan["density"] == VG.hedge_density(VG.SPECIES[name]["card_scale"]) >= VG.LEAF_CARDS_PER_M2
    assert VG.hedge_density(0.45) == 518.5 and VG.hedge_density(1.0) == VG.LEAF_CARDS_PER_M2 == 105.0
    assert VG.cover_layers(60.0, [0.16 * 0.45, 0.22 * 0.45]) == pytest.approx(0.171, abs=0.001)   # round 1, boxwood
    assert VG.cover_layers(VG.CROWN_CARDS_PER_M2, VG.LEAF_CARD_M) == pytest.approx(VG.CROWN_COVER_LAYERS, abs=0.02)
    assert VG.LEAF_CARD_M == (0.20, 0.24) and VG.HEDGE_CARD_TILT_DEG == 45.0
    assert VG.LEAF_TINT_FACTOR == 1.0 and VG.LEAF_TINT_GAIN == 1.6 and 0 < VG.LEAF_TRANSLUCENT < 0.25


def test_review_round3_leaf_atlases_carry_the_opacity_map_into_the_leaf_material(tmp_path):
    """Item 3 of round 3: the hedge and crown cards take the ambientCG LeafSet atlas colour and its Opacity map. The
    atlas ids are ambientCG ids every species resolves to, the fetcher keeps the Opacity map (OPTIONAL_SUFFIXES) and
    leaf_atlas hands it to leaf_material (``files["opacity"]``: the alpha; else the procedural leaf mask)."""
    from wenart.assets import ambientcg as AC

    assert AC.OPTIONAL_SUFFIXES["opacity"] == "_Opacity"
    assert set(VG.LEAF_ATLASES.values()) == {"LeafSet027", "LeafSet012", "LeafSet016"}
    assert all(AC.looks_like_id(a) for a in VG.LEAF_ATLASES.values())
    assert all(VG.LEAF_ATLASES.get(rec.get("leaf") or "broadleaf") for rec in VG.SPECIES.values())
    folder = tmp_path / "assets"
    files = {}
    for key, suffix in (("albedo", "Color"), ("opacity", "Opacity"), ("normal", "NormalGL")):
        f = folder / "textures" / "LeafSet027" / f"LeafSet027_2K-JPG_{suffix}.jpg"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(b"x")
        files[key] = str(f.relative_to(folder))
    manifest = {"textures": {"LeafSet027": {"files": files, "size_m": [1.0, 1.0]}}}
    atlas = VG.leaf_atlas("cherry_laurel", manifest, folder)
    assert atlas["id"] == "LeafSet027" and atlas["licence"] == "CC0" and atlas["files"]["opacity"].endswith("Opacity.jpg")
    assert VG.leaf_atlas("boxwood", manifest, folder)["id"] == "LeafSet027"
    manifest["textures"]["LeafSet027"]["files"].pop("albedo")
    assert VG.leaf_atlas("cherry_laurel", manifest, folder) is None          # no colour map: the procedural card


def test_round3_sapling_leaf_properties_exist_in_the_add_on_and_the_presets_keep_their_counts():
    """The override keys are properties of sapling_tree_gen 0.3.7's AddTree operator (its source, when the
    verification copy is present), the leaf shape is one of its enum values, and sapling_args keeps a preset's own
    leaf count while turning the leaves on."""
    over = VG.sapling_overrides("olive", 5.6, 7)
    if SAPLING_SRC is not None:
        import re
        src = SAPLING_SRC.read_text(encoding="utf-8")
        props = set(re.findall(r"^    (\w+): (?:Bool|Int|Float|Enum|FloatVector|IntVector|String)Property\(", src, re.M))
        assert {"showLeaves", "leaves", "leafShape", "leafScale", "leafScaleX", "leafScaleT", "leafScaleV", "bend",
                "leafDist", "leafDupliObj"} <= props
        assert set(over) - {"shape", "attractUp"} <= props, set(over) - props
        assert "('rect', 'Rectangular', '1')" in src and "leafMesh = bpy.data.meshes.new('leaves')" in \
            SAPLING_SRC.with_name("utils.py").read_text(encoding="utf-8")
    preset = {"leaves": 150, "showLeaves": False, "leafShape": "hex", "leafScale": 0.4, "scale": 5.0, "levels": 2,
              "chooseSet": "0", "presetName": "x", "attractUp": 0.5}
    args = VG.sapling_args("conifer", 8.0, 3, preset)
    assert args["leaves"] == 150 and args["showLeaves"] and args["leafShape"] == "rect"
    assert args["leafScale"] == VG.SAPLING_LEAF_M and "chooseSet" not in args and "presetName" not in args
    assert args["levels"] == 3 and args["scale"] == pytest.approx(8.0 / VG.SAPLING_TOP_PER_SCALE["douglas_fir"], abs=1e-3)


@pytest.mark.skipif(not REAL04.is_file(), reason="no committed real04 building")
def test_round3_real04_platforms_step_down_with_no_wall_over_the_retaining_cap(monkeypatch):
    """P1 real04 ext_1 'platforms' / 'all': sp_001 (level -3.0 m, the ground 1.86 m under and 1.79 m over it) showed
    as a tall white box. Now no retaining wall on the committed real04 site is taller than RETAINING_MAX_M where a
    band fits: the terraces step down in bands, each with its own wall; the records say the terrain under them.
    Review of round 3: the edges drawn into the building (sp_001 0.65 m into the basement L-1) or facing the copy's
    footprint (sp_003, sp_004) build no wall and no band (round 3 put 5 bands of 1.2-2.1 m inside the basement), no
    band enters the building, a copy or another platform, and the two walls next to the parking spk_001 (drawn 0.2 m
    from sp_004 and beside sp_002) stay over the cap with the reason recorded."""
    from wenart.blender import build as BB
    from wenart.blender import geom2d as GD

    assert S.RETAINING_MAX_M == 1.2
    b = json.loads(REAL04.read_text(encoding="utf-8"))
    if P1_SITE.is_file():                                      # the P1 numbers this fixes (the runs/ folder, local)
        p1 = {p["id"]: p for p in json.loads(P1_SITE.read_text(encoding="utf-8"))["platforms"]}
        assert p1["sp_001"]["drop_m"] > S.RETAINING_MAX_M and p1["sp_001"]["rise_m"] > S.RETAINING_MAX_M
    keep = S.building_keep_out(b)
    assert len(keep) == 2                                      # the ground outline and the copy b2's footprint
    inner = [GD.offset_polygon(q, S.PLATFORM["keep_out_wall"]) for q in keep]
    # the pure records on the site's own ground (platforms_into_building) and on the build's terrain
    prep = BB.prepare(b, "base", None)
    # building_keep_out restates build.ground_outline (site.py must not import build.py): the same outline within
    # 1 cm (prepare reads the variant building, whose walls differ by a millimetre)
    def same_outline(p, q):
        return all(min(G.distance(v, w) for w in q) < 0.01 for v in p) and \
            all(min(G.distance(v, w) for w in p) < 0.01 for v in q)

    assert same_outline(keep[0], prep["ground_outline"]) and keep[1:] == prep["site"]["copy_holes"]
    for name in ("real02", "real03"):
        other = ROOT / "results" / "furniture" / name / "building_final.json"
        if other.is_file():
            ob = json.loads(other.read_text(encoding="utf-8"))
            op = BB.prepare(ob, "base", None)
            if op["ground_outline"]:
                assert same_outline(S.building_keep_out(ob)[0], op["ground_outline"]), name
    for pfs in (S.platforms(b["site"], keep_out=keep, facades=S.building_facades(b)), prep["site"]["platforms"]):
        primary = [p for p in pfs if not p.get("parent")]
        assert [p["id"] for p in primary] == ["sp_001", "sp_002", "sp_003", "sp_004", "spk_001"]
        bands = [p for p in pfs if p.get("parent")]
        assert len(bands) >= 15 and all(p["kind"] == "terrace" and p["edge"] == "retaining" for p in bands)
        over = assert_walls_within_cap_or_blocked(pfs)
        # 25 Oct 2026: the pool decks at the basement floor are held by the driveway's retaining wall (a guard on it)
        # and the sides of the bands at sp_002's north end; nothing else passes the cap
        assert {(pid, by) for pid, _e, _h, by in over} == {("sp_002", "spk_001"), ("sp_003", "spk_001"),
                                                            ("sp_004", "spk_001"), ("sp_002_s1e4", "band_side"),
                                                            ("sp_002_s1e5", "band_side")}
        assert all(h < 2.6 for _pid, _e, h, _by in over)
        walls = next(q for q in S.platform_parts(next(p for p in pfs if p["id"] == "sp_002"),
                                                 prep["site"]["terrain"]) if q["part"] == "wall")["walls"]
        assert any(w.get("guard") for w in walls) and all(w.get("guard") for w in walls
                                                          if w["z1"] - w["z0"] > S.GUARD_RISE_M + S.PLATFORM["below"] + 0.2)
        sp1 = primary[0]
        assert sp1["against_edges"] == [0, 1, 12, 13, 14, 15, 16]          # drawn into the basement L-1
        assert {p["id"]: bool(p["against_edges"]) for p in primary} == \
            {"sp_001": True, "sp_002": True, "sp_003": True, "sp_004": True, "spk_001": False}
        assert sp1["stepped"] and all(st["step_m"] <= S.RETAINING_MAX_M + 1e-9 for st in sp1["stepped"])
        assert {st["direction"] for st in sp1["stepped"]} == {"up", "down"}          # a cut and a fill side
        assert all(str(st["edge"]) in sp1["edge_floor"] for st in sp1["stepped"])
        assert all(st["edge"] not in p["against_edges"] for p in primary for st in p.get("stepped") or [])
        assert len(sp1["polygon"]) > 6                       # the long edges are split (edge_split_m)
        by_id = {p["id"]: p for p in pfs}
        for band in bands:
            assert band["step"] >= 1 and band["shared_edges"] and band["outer_edge"] is not None
            assert band["bottom_z"] == round(by_id[band["parent"]]["z"] - S.PLATFORM["below"], 3)
            assert band["ground"]["min"] <= band["ground"]["max"] and "retaining cap" in band["reason"]
            assert "stepped terrace" in band["reason"]
            # every band is a proper strip (review of round 3: the mitred band on sp_001's 0.67 m edge 16 was a
            # bow-tie, a twisted slab; such an edge gets square ends)
            assert _simple_polygon(band["polygon"]) and G.polygon_signed_area(band["polygon"]) > 0.05, band["id"]
            assert len(band["mitred"]) == 2
            # no band inside the building (beyond its outer wall), a copy or another platform: a 5 x 5 grid
            others = [p["polygon"] for p in primary if p["id"] != band["parent"]] + \
                [q["polygon"] for q in bands if q is not band]
            q0, q1, q2, q3 = band["polygon"]
            for u in (0.1, 0.3, 0.5, 0.7, 0.9):
                for v in (0.1, 0.3, 0.5, 0.7, 0.9):
                    pt = tuple((1 - u) * (1 - v) * q0[k] + u * (1 - v) * q1[k] + u * v * q2[k] + (1 - u) * v * q3[k]
                               for k in (0, 1))
                    assert not any(G.point_in_polygon(pt, q) for q in inner + others), (band["id"], pt)
    # the meshes: every wall built is within the cap but the two recorded ones, a band's inner edge and an edge
    # facing the building have no wall, a parent's wall on a stepped edge ends at the band (to_band)
    monkeypatch.delenv(S.SITE_VARIANT_ENV, raising=False)
    sp = BB.prepare(b, "base", None)["site"]
    over = {(pid, edge) for pid, edge, _h, _by in assert_walls_within_cap_or_blocked(sp["platforms"])}
    heights, to_band, n_walls = [], 0, 0
    for pf in sp["platforms"]:
        parts = {q["part"]: q for q in S.platform_parts(pf, sp["terrain"])}
        assert "slab" in parts
        for w in (parts.get("wall") or {}).get("walls") or []:
            n_walls += 1
            to_band += int(w["to_band"])
            assert w["edge"] not in (pf.get("shared_edges") or []) and w["edge"] not in pf["against_edges"]
            if (pf["id"], w["edge"]) not in over:
                heights.append(w["height_m"])
            # the box spans the piece's buried part and the lip; its visible face is height_m (wall_pieces)
            assert w["z1"] - w["z0"] <= w["height_m"] + S.PLATFORM["below"] + S.PLATFORM["lip"] + 0.1 + 1e-6
        if pf.get("parent"):
            # bands carry no railing, only the guard on a side wall that holds the ground over the cap (25 Oct 2026)
            assert "railing" not in parts or any(w.get("guard") for w in parts["wall"]["walls"])
        if pf.get("steps_edge") is not None:
            assert pf["steps_edge"] not in pf["against_edges"]
    assert n_walls > 50 and max(heights) <= S.RETAINING_MAX_M + 1e-6 and to_band >= 10
    # the record's wall_max_m is the same measure as the built pieces (wall_pieces) on the same terrain
    assert S.wall_pieces((0, 0), (3, 0), 0.0, lambda x, y: -0.4 * x)[-1]["height_m"] == pytest.approx(1.2, abs=0.01)
    assert S.wall_pieces((0, 0), (3, 0), 0.0, lambda x, y: 0.0) == []
    assert [q["height_m"] for q in S.wall_pieces((0, 0), (2, 0), 0.0, lambda x, y: 0.0, floor=-0.9)] == [0.9, 0.9]
    # the building JSON round trip keeps the bands (string edge keys) and validates
    from wenart import building as BM
    rec = S.platforms_into_building(b)
    assert rec["count"] == len(sp["platforms"]) and rec["kinds"]["terrace"] >= 15
    BM.validate(b)
    assert all(isinstance(k, str) for pf in b["site"]["platforms"] for k in (pf.get("edge_floor") or {}))


def test_review_round3_against_edges_and_blocked_bands_on_a_synthetic_site():
    """Review of round 3: a terrace drawn 0.5 m into a building on a steep slope builds no wall or band on the edge
    inside the building, a band that would enter another platform is not built (recorded), a mitred band blocked
    by a neighbour retries with square ends, and with no keep-out nothing changes."""
    from wenart.levels import terrain as T

    surface = T.fit_surface([(-20, -20, -8.0), (20, -20, 8.0), (-20, 20, -8.0), (20, 20, 8.0)])    # z = 0.4 x
    site = {"ground": {"surface": surface, "points": [], "levels": []},
            "paving": [{"id": "t1", "polygon": [[-3, -3], [3, -3], [3, 3], [-3, 3]], "build": True}], "parking": [],
            "pools": []}
    house = [(2.5, -10), (12, -10), (12, 10), (2.5, 10)]                 # the terrace's east 0.5 m lies in it
    free = S.platforms(site)
    held = S.platforms(site, keep_out=[house])
    t_free, t_held = free[0], held[0]
    assert t_free["against_edges"] == [] and t_held["against_edges"]
    poly = geom2d.ccw(t_held["polygon"])
    for i in t_held["against_edges"]:                                     # the east edge pieces (x = 3)
        a, b = poly[i], poly[(i + 1) % len(poly)]
        assert a[0] == b[0] == 3.0
        assert str(i) not in t_held["edge_floor"] and i not in {st["edge"] for st in t_held["stepped"]}
    assert any(st["direction"] == "up" for st in t_free["stepped"])       # the uphill (east) side stepped up before
    assert all(st["direction"] == "down" for st in t_held["stepped"])     # now it faces the house: no band
    assert all(not G.point_in_polygon(G.polygon_centroid(p["polygon"]), house) for p in held if p.get("parent"))
    parts = {q["part"]: q for q in S.platform_parts(t_held, {"kind": "planar", "surface": surface, "z": {},
                                                             "rect": [-3, -3, 3, 3]})}
    assert all(w["edge"] not in t_held["against_edges"] for w in parts["wall"]["walls"])
    # a second terrace 0.3 m west of t1's downhill edge: no band enters it, the edge says what blocked it
    site2 = dict(site, paving=site["paving"] + [{"id": "t2", "polygon": [[-9, -3], [-3.3, -3], [-3.3, 3], [-9, 3]],
                                                 "build": True}])
    pfs = S.platforms(site2)
    t1 = next(p for p in pfs if p["id"] == "t1")
    west = [b for b in t1["band_blocked"] if b["by"] == "t2"]
    assert west and all(b["bands"] == 0 for b in west)
    t2 = next(p for p in pfs if p["id"] == "t2")
    for band in (p for p in pfs if p.get("parent") == "t1"):
        assert not G.point_in_polygon(G.polygon_centroid(band["polygon"]), t2["polygon"])
    assert_walls_within_cap_or_blocked(pfs)
    # a sloped (draped) parking: every kerb piece reaches under the ground at both ends (P1 real04 ext_5: the pieces
    # floated as bars over the slope, their bottom 4 cm under the piece's highest ground)
    park = {"id": "pk", "polygon": geom2d.ccw([(-6, 4), (6, 4), (6, 9), (-6, 9)]), "holes": [], "z": 0.0,
            "kind": "parking", "sloped": True, "edge": "kerb", "railing_edges": [], "steps_edge": None}
    terrain = {"kind": "planar", "surface": surface, "z": {}, "rect": [-6, 4, 6, 9]}
    kerb = next(q for q in S.platform_parts(park, terrain) if q["part"] == "kerb")
    boxes = [kerb["verts"][k:k + 8] for k in range(0, len(kerb["verts"]), 8)]
    assert len(boxes) >= 12
    for box in boxes:
        zb, zt = min(v[2] for v in box), max(v[2] for v in box)
        ground = [S.ground_z(terrain, v[0], v[1]) for v in box]
        assert zb <= min(ground) + 1e-6 and zt >= max(ground) + S.PLATFORM["kerb_h"] - 1e-6
    # the blocked index and the quad grid
    assert S._band_blocked([(0, 0), (1, 0), (1, 1), (0, 1)], [[(5, 5), (6, 5), (6, 6)]]) is None
    assert S._band_blocked([(0, 0), (1, 0), (1, 1), (0, 1)], [[(5, 5), (6, 5), (6, 6)], [(0.4, 0.4), (2, 0.4), (2, 2)]]) == 1
    assert S.against_edges([(0, 0), (4, 0), (4, 4), (0, 4)], [[(4.1, -1), (9, -1), (9, 5), (4.1, 5)]]) == [1]
    assert S.against_edges([(0, 0), (4, 0), (4, 4), (0, 4)], []) == []


def test_round3_stepped_bands_on_a_synthetic_steep_slope_and_the_wall_materials():
    """A 40 % slope under a 6 x 6 m terrace: the downhill edge gets stepped bands (mitred at the shared corner),
    the uphill edge steps up, the flat site gets none; the wall look is a concrete slug, never the facade."""
    from wenart.levels import terrain as T

    surface = T.fit_surface([(-20, -20, -8.0), (20, -20, 8.0), (-20, 20, -8.0), (20, 20, 8.0)])    # z = 0.4 x
    site = {"ground": {"surface": surface, "points": [], "levels": []},
            "paving": [{"id": "t1", "polygon": [[-3, -3], [3, -3], [3, 3], [-3, 3]], "build": True}], "parking": [],
            "pools": []}
    pfs = S.platforms(site)
    t1 = next(p for p in pfs if p["id"] == "t1")
    assert t1["z"] == 0.0 and t1["drop_m"] == pytest.approx(1.2, abs=0.01) and t1["rise_m"] == pytest.approx(1.2, abs=0.01)
    bands = [p for p in pfs if p.get("parent") == "t1"]
    assert bands and {b["stepped_from"]["direction"] for b in bands} == {"down", "up"}
    assert all(p["wall_max_m"] <= S.RETAINING_MAX_M + 1e-6 for p in pfs)
    down = [b for b in bands if b["stepped_from"]["direction"] == "down"]
    assert all(b["z"] < 0 for b in down) and all(b["bottom_z"] == -S.PLATFORM["below"] for b in down)
    # the bands lie outside the terrace and never overlap each other (a partition of the strips)
    for b in bands:
        assert not G.point_in_polygon(G.polygon_centroid(b["polygon"]), t1["polygon"])
    for i, a in enumerate(bands):
        for c in bands[i + 1:]:
            ca, cc = G.polygon_centroid(a["polygon"]), G.polygon_centroid(c["polygon"])
            assert not G.point_in_polygon(ca, c["polygon"]) and not G.point_in_polygon(cc, a["polygon"])
    # the terrain record and the wall parts: a band's outer wall ends at the next band
    terrain = {"kind": "planar", "surface": surface, "z": {}, "rect": [-3, -3, 3, 3]}
    for b in down:
        parts = {q["part"]: q for q in S.platform_parts(b, terrain)}
        for w in parts.get("wall", {}).get("walls", []):
            assert w["height_m"] <= S.RETAINING_MAX_M + 1e-6
    # every band is a proper strip: square ends lie on this edge's normal, mitred ends on the bisector (review of
    # round 3: the square branch of _offset_corner moved the b corner along the next edge's normal)
    for b in bands:
        assert _simple_polygon(b["polygon"]) and G.polygon_signed_area(b["polygon"]) > 0.5, b["id"]
    assert S._offset_corner((1.0, 0.0), (0.0, -1.0), (1.0, 0.0), 1.2, False) == (1.0, -1.2)      # square: n_this
    assert S._offset_corner((1.0, 0.0), (0.0, -1.0), (1.0, 0.0), 1.2, True) == pytest.approx((2.2, -1.2))  # mitre
    # real04 sp_001 edge 16 (0.67 m, a square a end and a mitred b end at a reflex corner): the outer edge would run
    # backwards (a bow-tie), so the edge gets square ends
    a, bb = (1.66415, 8.64995), (0.996941, 8.650924)
    assert not S._band_quad_ok(a, bb, (2.198678, 9.849171), (1.665902, 9.849949))
    assert S._band_quad_ok(a, bb, (0.998693, 9.850923), (1.665902, 9.849949))
    assert not S._band_quad_ok((0, 0), (1, 0), (0.5, -1), (0.6, -1))                             # crossed ends
    # a flat site: no bands at all
    flat = {"ground": {"levels": [{"side": "all", "z": {"value": 0.0}}]}, "paving": site["paving"], "parking": [],
            "pools": []}
    assert [p["id"] for p in S.platforms(flat)] == ["t1"] and S.platforms(flat)[0]["wall_max_m"] == 0.0
    assert S.subdivide_edges([(0, 0), (9, 0), (9, 1)], 3.0)[:4] == [(0, 0), (3, 0), (6, 0), (9, 0)]
    # the looks of the parts: walls and kerbs a concrete vocabulary slug of kind stone / ground, never 'render'
    from wenart.blender import materials as M
    assert S.PLATFORM_LOOKS["wall"][0] == S.PLATFORM_LOOKS["kerb"][0] == "concrete_exposed"
    assert (M.ENTRIES.get("concrete_exposed") or {}).get("kind") in ("stone", "ground", "hard")
    assert S.PLATFORM_LOOKS["wall"][0] not in ("render", "plaster_white")


def test_round3_terrain_record_never_raises_and_matches_the_manifest_schema():
    """P1: build_site raised KeyError 'sides' on a bare terrain record; the record is normalised now."""
    import jsonschema
    from wenart.blender import schemas

    bare = S.terrain_record({"kind": "flat", "z": {k: 0.0 for k in S.AXES}})
    assert bare == {"kind": "flat", "z": {k: 0.0 for k in S.AXES}, "sides": [], "north_deg": None,
                    "north_source": None, "changes": []}
    tin = S.terrain_record({"kind": "tin", "surface": {"kind": "tin"}, "z": {}, "rect": [0, 0, 1, 1]})
    assert tin["kind"] == "tin" and tin["z"] == {} and tin["sides"] == [] and tin["changes"] == []
    assert S.terrain_record({})["kind"] == "flat"
    real = S.terrain_model({"site": {"ground": {"levels": [{"side": "left", "z": {"value": -3.0}},
                                                           {"side": "right", "z": {"value": 0.0}}]}}},
                           [(0, 0), (10, 0), (10, 8), (0, 8)])
    rec = S.terrain_record(real)
    assert rec["kind"] == "sides" and len(rec["sides"]) == 2 and rec["north_deg"] == real["north_deg"]
    assert rec["z"] == {k: round(v, 4) for k, v in real["z"].items()}
    schema = schemas.SITE_BUILT["properties"]["terrain"]
    for r in (bare, tin, rec):
        jsonschema.validate(r, schema)


def test_round3_lawn_tile_clamp_and_the_site_kinds_in_the_manifest_schema():
    """P1: every exterior rendered the lawn as a flat saturated green (real02's ground: grass__Grass004, a 1.4 m
    photo tile that averages to one green at a distance). The texture tile is clamped to 1-2 m; the variation is a
    multiplier around 1. The four site
    kinds are in the scene-manifest schema (round-2 leftover), so site.site_kind writes its own names."""
    from wenart.blender import schemas

    assert VG.lawn_tile_m([4.0, 4.0]) == 2.0 and VG.lawn_tile_m([0.5, 0.5]) == 1.0 and VG.lawn_tile_m([1.2, 1.2]) == 1.2
    assert VG.lawn_tile_m(None) == 1.5 and VG.lawn_tile_m([0, 0]) == 1.5 and VG.lawn_tile_m(["x"]) == 1.5
    dark, light = VG.LAWN_VARIATION["dark"], VG.LAWN_VARIATION["light"]
    assert all(0.6 <= d < 1.0 for d in dark) and all(0.85 <= lt <= 1.2 for lt in light)
    assert sum(dark) / 3 < 1.0 < sum(light) / 3                          # a multiplier around 1: a mild variation
    assert 0 < VG.LAWN_VARIATION["scale_per_m"] < 0.5 and 0 < VG.LAWN_VARIATION["bump"] < 0.3
    assert {"site_platform", "site_hedge", "site_grass", "atmosphere"} <= set(schemas.WHOLE_BUILDING_KINDS)
    assert {S.site_kind(p) for p in ("platform", "hedge", "grass", "haze")} == \
        {"site_platform", "site_hedge", "site_grass", "atmosphere"}
    assert VG._manifest_kind("site_hedge") == "site_hedge" and VG._manifest_kind("atmosphere") == "atmosphere"


# --------------------------------------------------------------------------
# Pre-flight of pod P3 (16 Oct 2026, CPU build of P3's real04 inputs with the bpy module)
# --------------------------------------------------------------------------

def _assumed_appends(path: Path) -> list:
    """``(line, keys)`` of every ``assumed.append({...})`` / ``out["assumed"].append({...})`` call with a dict literal
    in a module (ast): the entries that reach the scene manifest's ``assumed`` list as they are written."""
    import ast
    found = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "append"
                and node.args and isinstance(node.args[0], ast.Dict)):
            continue
        target = node.func.value
        name = target.id if isinstance(target, ast.Name) else (
            target.slice.value if isinstance(target, ast.Subscript) and isinstance(target.slice, ast.Constant) else None)
        if name != "assumed":
            continue
        keys = {k.value for k in node.args[0].keys if isinstance(k, ast.Constant)}
        if "object" in keys:              # a manifest entry (the builders' detail lists get their parent later)
            found.append((node.lineno, keys))
    return found


def test_preflight_p3_assumed_entries_name_their_parent_with_their_kind():
    """The real04 scene manifest failed validate_scene_manifest: 28 site_platform and 4 site_hedge assumed entries
    carried ``kind`` without ``parent`` (schemas.ASSUMED_ENTRY: dependentRequired). Every assumed entry written as a
    literal in the blender package names both or neither."""
    bad = []
    for path in sorted((ROOT / "wenart" / "blender").glob("*.py")):
        for line, keys in _assumed_appends(path):
            if ("kind" in keys) != ("parent" in keys):
                bad.append(f"{path.name}:{line} {sorted(keys)}")
    assert not bad, bad
    assert len(_assumed_appends(ROOT / "wenart" / "blender" / "site.py")) >= 4      # the scan sees site.py's entries


def test_preflight_p3_a_missing_tree_source_is_recorded_with_its_reason(monkeypatch, tmp_path):
    """real04 on the CPU: the 20 shrubs near the cameras became leaf cards (no Poly Haven model in the assets) and the
    manifest said ``fallback_from: null``. ``missing_source`` names the planned source that is missing and why."""
    (tmp_path / "manifest.json").write_text("{}", encoding="utf-8")       # an assets folder without the models
    monkeypatch.setenv("WENART_ASSETS", str(tmp_path))
    near = VG.missing_source("oleander", True, {"instances": True, "sapling": True}, hero=None, sapling={"ok": True})
    assert near["fallback_from"] == "polyhaven" and "searsia_lucida" in near["fallback_reason"]
    assert str(tmp_path) in near["fallback_reason"]
    hero = {"id": "searsia_lucida"}
    assert VG.missing_source("oleander", True, None, hero=hero, sapling={"ok": True}) == {}
    assert VG.missing_source("oleander", False, None, hero=None, sapling=None) == {}       # a shrub has no Sapling
    assert VG.missing_source("oleander", True, {"instances": False, "sapling": True}, None, {"ok": True}) == {}
    far = VG.missing_source("birch", False, None, hero=None, sapling={"ok": False, "how": "not installed"})
    assert far == {"fallback_from": "sapling", "fallback_reason": "the Sapling add-on is not usable (not installed)"}
    assert VG.missing_source("birch", False, {"instances": True, "sapling": False}, None, None) == {}
    assert VG.missing_source("birch", False, None, hero=None, sapling={"ok": True}) == {}
    assert VG.missing_source("palm", False, None, hero=None, sapling={"ok": False, "how": "x"}) == {}
    # near a camera without the model: the Poly Haven reason (Sapling, when there, still builds it)
    assert VG.missing_source("birch", True, None, hero=None, sapling={"ok": True})["fallback_from"] == "polyhaven"


def test_preflight_p3_draped_faces_never_use_a_vertex_twice():
    """real04 on the CPU: 732 ground and 112 grass faces used one vertex twice (two clip points within the 0.1 mm
    vertex key), "Mesh ground is not valid, and may be exported wrongly" in the scene.glb export. A hole corner 0.04
    mm from a grid line reproduces it on a slope and on the flat path."""
    outer = [(0, 0), (10, 0), (10, 10), (0, 10)]
    terrain = S.terrain_model({"site": {"ground": {"levels": [{"side": "left", "z": {"value": -2.0}},
                                                              {"side": "right", "z": {"value": 0.0}}]}}},
                              [(20, 0), (30, 0), (30, 8), (20, 8)])
    assert not S.is_flat(terrain)
    for hole in ([(3.00004, 3.00003), (6, 3.00003), (6.00002, 6), (3.00004, 6)],
                 [(2.99996, 2.99997), (6, 3), (6, 6), (3, 6)]):
        for kw in ({"step": 1.0}, {"z": 0.0}):
            verts, faces = S.draped_faces(outer, [hole], terrain, **kw)
            assert faces and all(len(set(f)) == len(f) >= 3 for f in faces), kw
            assert all(0 <= i < len(verts) for f in faces for i in f)
            # the faces still cover the region (10 x 10 minus the 3 x 3 hole) within the dropped slivers
            area = sum(abs(G.polygon_area([verts[i][:2] for i in f])) for f in faces)
            assert area == pytest.approx(91.0, abs=1e-2), (kw, area)


# --------------------------------------------------------------------------
# Fix round after P3 (16-17 Oct 2026; docs/milestone13.md §14.8 attempt 2: P3's real04 exterior views). Every test
# below fails on the code of the P3 results commit (5bd7bab): the aerial pitched 30 degrees with the horizon at 1.27
# of the frame, no site finish set fetched (no ``site_texture_rows``), hedges and shrubs built on the terrain under the
# terraces (no ``stand_terrain``), hedge hulls through the retaining walls (no ``fit_hedges``), a lawn relief of +-3 cm
# over 1.2 cm paving (no ``relief_range``).
# --------------------------------------------------------------------------

def _example_exterior():
    """The docs example building's exterior camera model (as tests/test_blender_exterior.py builds it)."""
    from wenart import views as V
    from wenart.blender import roof as R

    b = V.variant_building(EXAMPLE, "base")
    plan = S.site_plan(b, b["levels"], geom2d.ccw(b["slabs"][0]["outline"]), "full")
    return b, E.build_model(b, b["levels"], R.roof_model(b["roof"], b), plan), plan


def _real04_prep(monkeypatch):
    from wenart.blender import build as BB

    monkeypatch.delenv(S.SITE_VARIANT_ENV, raising=False)
    return BB.prepare(json.loads(REAL04.read_text(encoding="utf-8")), "base", None)


def test_p3_the_aerial_view_keeps_the_horizon_in_the_upper_part_of_the_frame(monkeypatch):
    """CLAUDE.md: "the sky, the sun and the horizon are always in the image". P3's ext_5 pitched 30 degrees at
    26.87 mm: horizon at 1.27 of the frame height, lawn at the top, no sky. The aerial pitch now comes from
    copies.pitch_for_horizon (the horizon at AERIAL_HORIZON_FRAC) and its lens never gets longer than AERIAL_LENS_MM;
    the site view (ext_7) and the one-aerial policy flags stay as they were."""
    pitch = CP.pitch_for_horizon(E.AERIAL_HORIZON_FRAC, E.AERIAL_LENS_MM, E.AERIAL_PITCH_DEG)
    assert 14.0 <= pitch <= 18.0 and pitch < E.AERIAL_PITCH_DEG
    assert CP.horizon_fraction(E.AERIAL_PITCH_DEG, 26.87) > 1.0            # P3's ext_5: above the frame
    b, m, plan = _example_exterior()
    plans, _dropped = E.plan_exterior(m, b, b["levels"], plan["plot"], variant="base")
    cases = [(next(p for p in plans if p["name"] == "ext_5"), m)]
    if REAL04.is_file():
        prep = _real04_prep(monkeypatch)
        vb, sp = prep["building"], prep["site"]
        model = E.build_model(vb, vb["levels"], prep["roof"], sp)
        rplans, _ = E.plan_exterior(model, vb, vb["levels"], sp["plot"] or [], variant="base")
        cases.append((next(p for p in rplans if p["name"] == "ext_5"), model))
        site_view = next(p for p in rplans if p.get("site_view"))
        assert site_view["horizon_frac"] == pytest.approx(CP.SITE_VIEW_HORIZON_FRAC, abs=1e-3)
        assert [p["name"] for p in rplans if p["view"] == "aerial"] == ["ext_5", site_view["name"]]
    for ext5, cam_model in cases:
        assert ext5["view"] == "aerial" and ext5["aerial_allowed"] and not ext5.get("dropped")
        assert -E.AERIAL_PITCH_DEG <= ext5["pitch_deg"] < 0 and ext5["pitch_deg"] == pytest.approx(-pitch, abs=0.05)
        assert ext5["lens_mm"] <= E.AERIAL_LENS_MM and ext5["shift_y"] == 0.0
        frac = CP.horizon_fraction(-ext5["pitch_deg"], ext5["lens_mm"])
        assert ext5["horizon_frac"] == pytest.approx(frac, abs=1e-3) and 0.5 < frac <= E.AERIAL_HORIZON_FRAC + 1e-3
        assert cam_model.inside(ext5["position"]) is None
        assert ext5["score"]["ok"] and ext5["score"]["aim_visible"]


def test_p3_the_site_finish_sets_are_fetched_and_follow_the_build_fingerprint():
    """P3: concrete_exposed (the platforms' retaining walls and kerbs, 29 objects, and the plinth) said ``textured
    false, asset concrete_wall_001 not in the assets manifest``: the style names none of the finishes the outside
    build puts on by itself. The assets stage now fetches their sets (fetch.site_texture_rows, read from
    exterior.build_finish_slugs) and the build fingerprint lists the same ids (build.referenced_asset_ids), like
    test_referenced_assets_follow_the_shell_sets_the_assets_stage_fetches does for the shell slots."""
    from wenart.assets import fetch
    from wenart.blender import build as BB
    from wenart.style import profile as SP
    from wenart.style import vocabulary as V

    slugs = dict(E.build_finish_slugs({}))
    assert slugs["concrete_exposed"] == "platform_wall" and S.PLATFORM_LOOKS["wall"][0] == "concrete_exposed"
    assert slugs["concrete_exposed"] and set(S.SITE_FALLBACK_LOOKS.values()) <= set(slugs)
    rows = fetch.site_texture_rows({})
    assert ("polyhaven", "concrete_wall_001", "site:platform_wall") in rows
    checks = json.loads(fetch.CHECKS_PATH.read_text(encoding="utf-8"))["textures"]
    vocab = {e.get("asset") for e in list(V.MATERIALS.values()) + list(V.FURNITURE_MATERIALS.values())}
    for source, asset_id, label in rows:                    # existing CC0 sets of the vocabulary, never invented
        record = checks[f"{source}:{asset_id}"]
        assert asset_id in vocab and record["exists"] and record["licence"] == "CC0", label
        assert record["has_required_maps"] and record["jpg_1k_2k"] and fetch.LICENCES[source] == "CC0", label
    # a family with a stone plinth and window surrounds fetches those sets too (facade.ARTICULATION)
    classic = {a for _s, a, _l in fetch.site_texture_rows({"family": "classic"})}
    assert {"rustic_stone_wall", "floor_tiles_02"} <= classic and "rustic_stone_wall" not in {a for _s, a, _l in rows}
    # P3's case: a profile that names none of them; the fetch plan and the fingerprint both hold the walls' set
    profile = SP.profile_from_text("dark bronze window frames, oak floor")
    assert "concrete_wall_001" not in {a for _s, a, _l in SP.assets_in_profile(profile)["textures"]}
    assert "concrete_wall_001" in {a for _s, a, _l in fetch.texture_plan(profile)}
    building = json.loads(REAL04.read_text(encoding="utf-8")) if REAL04.is_file() else {}
    ids = set(BB.referenced_asset_ids(building, profile))
    assert {a for _s, a, _l in fetch.site_texture_rows(profile)} <= ids


def test_p3_trees_shrubs_and_hedges_stand_on_the_terrace_they_are_drawn_on(monkeypatch):
    """P3 built every plant on the terrain under the terraces: real04's hedge_003 (on the -3.0 m terrace sp_001)
    stood on the terrain at -4.8 .. -4.0 m, so its 1.2 m hull ended under the slab and showed as dark triangles and
    loose leaf cards on the retaining wall; the shrubs on the stepped bands were buried. stand_terrain gives a point
    on a flat platform its level, for build_site and for the exterior camera model alike.

    Fix round part 2 (17 Oct 2026; review of part 1): the camera model's half is checked on its own records: the
    docs example's tree (a trunk tree, so a ``model.trees`` record) on a terrace stands at the terrace's level, and
    real04's hedge_003 segments in ``model.hedges`` top out at sp_001's level + the hedge's height (part 1's check
    ``max(tops) >= ...`` held for the raw terrain too: another hedge's top is 1.58 m)."""
    terrain = {"kind": "flat", "z": {k: 0.0 for k in S.AXES}}
    pfs = [{"id": "t", "polygon": [[0, 0], [6, 0], [6, 4], [0, 4]], "z": -2.0, "sloped": False},
           {"id": "band", "polygon": [[6, 0], [7, 0], [7, 4], [6, 4]], "z": -1.0, "sloped": False},
           {"id": "park", "polygon": [[0, 5], [6, 5], [6, 9], [0, 9]], "z": 0.5, "sloped": True}]
    stand = S.stand_terrain(terrain, pfs)
    assert S.ground_z(stand, 3, 2) == -2.0 and S.ground_z(stand, 6.5, 2) == -1.0
    assert S.ground_z(stand, 3, 7) == 0.0 and S.ground_z(stand, 20, 20) == 0.0     # sloped: draped on the terrain
    assert "stand" not in terrain and S.stand_terrain(terrain, []) is terrain
    hedge = {"id": "h", "polyline": [[1, 2], [5, 2]], "width_m": 0.7, "height_m": 1.2}
    _v, _f, info = S.hedge_parts(hedge, stand)
    assert info["z_range"] == pytest.approx([-2.1, -0.8])
    shrub = S.tree_parts({"center": [3, 2], "size": [0.718, 0.718], "kind": "tree"}, stand)
    assert shrub["ground_z"] == -2.0 and shrub["size_class"] == "shrub"
    # the camera model (exterior.build_model): the docs example's 3 m tree on a terrace at +0.5 m (terrain -1.78 there)
    from wenart import views as V
    from wenart.blender import roof as R
    b = V.variant_building(EXAMPLE, "base")
    plan = S.site_plan(b, b["levels"], geom2d.ccw(b["slabs"][0]["outline"]), "full")
    tree = next(t for t in plan["trees"] if t["id"] == "sd_L0_001")
    cx, cy = tree["center"]
    terrace = {"id": "tt", "polygon": [[cx - 2.5, cy - 2.5], [cx + 2.5, cy - 2.5], [cx + 2.5, cy + 2.5],
                                       [cx - 2.5, cy + 2.5]], "z": 0.5, "sloped": False}
    assert S.ground_z(plan["terrain"], cx, cy) < -1.0                               # the raw terrain under it
    cam = E.build_model(b, b["levels"], R.roof_model(b["roof"], b), dict(plan, platforms=[terrace]))
    rec = next(t for t in cam.trees if t[0] == (cx, cy))
    assert rec[6] == pytest.approx(0.5) and rec[3] > 0.5                           # ground z, crown bottom
    if not REAL04.is_file():
        return
    prep = _real04_prep(monkeypatch)
    sp, vb = prep["site"], prep["building"]
    real = S.stand_terrain(sp["terrain"], sp["platforms"])
    by_id = {pf["id"]: pf for pf in sp["platforms"]}
    h3 = next(h for h in sp["hedges"] if h["id"] == "hedge_003")
    _v, _f, info = S.hedge_parts(h3, real)
    assert info["z_range"][0] == pytest.approx(by_id["sp_001"]["z"] - 0.1, abs=1e-6)        # was -4.9 (terrain)
    _v, _f, old = S.hedge_parts(h3, sp["terrain"])
    assert old["z_range"][1] < by_id["sp_001"]["z"] + 0.5                                   # P3: mostly buried
    on_band = 0
    for t in sp["trees"]:
        pf = next((p for p in sp["platforms"] if not p.get("sloped")
                   and G.point_in_polygon(tuple(t["center"]), p["polygon"])), None)
        if pf is not None:
            on_band += 1
            assert S.tree_parts(t, real)["ground_z"] == pytest.approx(pf["z"]), t["id"]
    assert on_band >= 1          # 25 Oct 2026: fewer bands since the terraces take their floor level
    # the camera model's obstacles stand where build_site builds them: every segment of hedge_003 (its fitted polyline)
    # tops out at sp_001's level + its height (the raw terrain gave -2.72 / -2.37 m tops there)
    model = E.build_model(vb, vb["levels"], prep["roof"], sp)
    segs = list(zip([tuple(map(float, q)) for q in h3["polyline"]], [tuple(map(float, q)) for q in h3["polyline"][1:]]))
    tops = [h[3] for h in model.hedges if (h[0], h[1]) in segs]
    assert len(tops) == len(segs) >= 1
    assert all(t == pytest.approx(by_id["sp_001"]["z"] + h3["height_m"], abs=1e-3) for t in tops), tops


def test_p3_hedges_keep_their_hull_on_their_planting_side(monkeypatch):
    """fit_hedges: a hedge on a terrace keeps its hull on the slab (half its width inside the edges), a hedge beside a
    terrace keeps its hull HEDGE_FIT card_reach_m off the terrace (no leaf card through the retaining wall), no hull
    reaches into the building; the polyline moves at most max_shift_m, then the hedge gets narrower; a hedge drawn
    across a platform is left alone. Synthetic cases and real04 (hedge_003 / hedge_004 overhung their terraces by
    0.22 / 0.16 m in P3)."""
    shapely = pytest.importorskip("shapely.geometry")
    hw = 0.35
    terrace = {"id": "t", "polygon": [[0, 0], [8, 0], [8, 6], [0, 6]], "z": 1.0}
    on = {"id": "on", "polyline": [[0.1, 1], [0.1, 5]], "width_m": 2 * hw, "height_m": 1.2}       # 0.1 m from the edge
    beside = {"id": "beside", "polyline": [[8.05, 1], [8.05, 5]], "width_m": 2 * hw, "height_m": 1.2}
    across = {"id": "across", "polyline": [[-3, 3], [11, 3]], "width_m": 2 * hw, "height_m": 1.2}
    far = {"id": "far", "polyline": [[20, 1], [20, 5]], "width_m": 2 * hw, "height_m": 1.2}
    out, assumed = S.fit_hedges([on, beside, across, far], [terrace], [[[30, 0], [40, 0], [40, 8], [30, 8]]])
    got = {h["id"]: h for h in out}
    assert got["on"]["polyline"] == [[pytest.approx(hw), 1.0], [pytest.approx(hw), 5.0]]
    assert got["on"]["fit"]["shift_m"] == [pytest.approx(hw - 0.1, abs=1e-3)] * 2 and not got["on"]["fit"]["narrowed"]
    assert got["on"]["fit"]["polyline_drawn"] == [[0.1, 1.0], [0.1, 5.0]] and got["on"]["fit"]["width_m_drawn"] == 0.7
    reach = S.HEDGE_FIT["card_reach_m"]
    assert got["beside"]["polyline"][0][0] == pytest.approx(8.0 + hw + reach, abs=1e-3)
    assert got["across"] is across and got["far"] is far                     # crossing / out of reach: unchanged
    assert {a["field"] for a in assumed} == {"hedge:on:fit", "hedge:beside:fit"}
    # a strip too narrow for the drawn width: moved at most max_shift_m, then narrowed (never under min_width_m)
    strip = {"id": "s", "polygon": [[0, 0], [0.2, 0], [0.2, 6], [0, 6]], "z": 1.0}
    narrow, _ = S.fit_hedges([dict(on, id="n", polyline=[[0.1, 1], [0.1, 5]])], [strip], [])
    assert narrow[0]["width_m"] == pytest.approx(S.HEDGE_FIT["min_width_m"]) and narrow[0]["fit"]["narrowed"]
    assert narrow[0]["fit"]["crossing_left_m"] > 0.0                        # the 0.3 m minimum still crosses
    # a 1.4 m hedge 0.1 m outside the terrace needs 0.75 m: it moves the 0.5 m cap, then is 0.9 m wide
    big = {"id": "b", "polyline": [[-0.1, 1], [-0.1, 5]], "width_m": 1.4, "height_m": 1.2}
    moved, _ = S.fit_hedges([big], [terrace], [])
    assert moved[0]["fit"]["shift_m"] == [pytest.approx(S.HEDGE_FIT["max_shift_m"])] * 2
    assert moved[0]["width_m"] == pytest.approx(0.9) and moved[0]["fit"]["crossing_left_m"] == 0.0
    far_out = {"id": "f", "polyline": [[-0.8, 1], [-0.8, 5]], "width_m": 0.7, "height_m": 1.2}
    assert S.fit_hedges([far_out], [terrace], [])[0] == [far_out]           # 0.8 m off: clear already
    if not REAL04.is_file():
        return
    prep = _real04_prep(monkeypatch)
    sp = prep["site"]
    flat = [pf for pf in sp["platforms"] if not pf.get("sloped")]
    by_id = {h["id"]: h for h in sp["hedges"]}
    for hid, pid in (("hedge_003", "sp_001"), ("hedge_004", "sp_004")):
        h = by_id[hid]
        hull = shapely.LineString(h["polyline"]).buffer(h["width_m"] / 2.0, cap_style=3)
        pf = next(p for p in flat if p["id"] == pid)
        assert shapely.Polygon(pf["polygon"]).buffer(2e-3).contains(hull), hid
        assert h["fit"]["keeps"] == [pid] and max(h["fit"]["shift_m"]) <= S.HEDGE_FIT["max_shift_m"]
        assert not h["fit"]["narrowed"] and h["width_m"] == pytest.approx(0.718)
        assert any(a["field"] == f"hedge:{hid}:fit" for a in sp["assumed"])
    outline = shapely.Polygon(sp["outline"])
    for h in sp["hedges"]:
        hull = shapely.LineString(h["polyline"]).buffer(h["width_m"] / 2.0, cap_style=2)
        assert hull.intersection(outline).area < 1e-6, h["id"]
        for pf in flat:
            poly = shapely.Polygon(pf["polygon"])
            core = [shapely.Point(p) for p in h["polyline"]]
            if all(poly.contains(c) for c in core) or not any(poly.contains(c) for c in core) and \
                    hull.distance(poly) > 0:
                continue
            crossing = hull.intersection(poly).area / hull.area
            assert crossing < 0.1 or h["id"] == "hedge_002", (h["id"], pf["id"], crossing)


def test_p3_the_lawn_relief_goes_down_only_and_keeps_the_ground_edges():
    """P3: green lawn blobs poked through the paved paths (ext_3, ext_7): the far lawn's Displace relief (strength
    0.06 m, mid level 0.5) lifted the ground up to 3 cm, over paving draped PAVING_LIFT (1.2 cm) above it. The relief
    now only goes down, and the ground's boundary vertices (the rim, the building, platforms, wells, pools) keep their
    level (vertex weights 0)."""
    lo, hi = VG.relief_range()
    assert hi <= 0.0 < S.PAVING_LIFT and S.GRASS_LIFT > hi and -0.05 <= lo < 0.0
    assert VG.relief_range(0.06, 0.5) == (-0.03, 0.03) and VG.relief_range(0.06, 0.5)[1] > S.PAVING_LIFT    # P3
    verts, faces = S.draped_faces([(0, 0), (10, 0), (10, 10), (0, 10)], [[(4, 4), (6, 4), (6, 6), (4, 6)]],
                                  S.terrain_model({"site": {"ground": {"levels": [
                                      {"side": "left", "z": {"value": -2.0}}, {"side": "right", "z": {"value": 0.0}}]}}},
                                      [(20, 0), (30, 0), (30, 8), (20, 8)]), step=1.0)
    weights = VG.relief_weights(len(verts), faces)
    assert len(weights) == len(verts) and set(weights) == {0.0, 1.0}
    for i, (x, y, _z) in enumerate(verts):
        on_rim = x in (0, 10) or y in (0, 10)
        on_hole = 4 <= x <= 6 and 4 <= y <= 6 and (x in (4, 6) or y in (4, 6))
        if on_rim or on_hole:
            assert weights[i] == 0.0, (x, y)
    assert sum(weights) > 0.5 * len(weights)                 # the inner lawn keeps its relief
    tri = VG.relief_weights(5, [[0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]])
    assert tri == [0.0, 0.0, 0.0, 0.0, 1.0]


_SLOPED = {"site": {"ground": {"levels": [{"side": "left", "z": {"value": -6.0}},
                                           {"side": "right", "z": {"value": 0.0}}]}}}
_OUTLINE = [(60.0, 0.0), (70.0, 0.0), (70.0, 8.0), (60.0, 8.0)]
_PATH = [(45.0, -10.0), (58.0, -10.0), (58.0, -8.8), (45.0, -8.8)]
_PARK = [(42.0, 4.0), (52.0, 4.0), (52.0, 12.0), (42.0, 12.0)]
_TERRACE = [(74.0, 2.0), (80.0, 2.0), (80.0, 7.0), (74.0, 7.0)]


def _relief_plan(terrain: dict) -> dict:
    """A site plan for the lawn relief tests (fix round part 2): a building, a draped inferred path, a sloped parking,
    a flat terrace (a hole), a shrub and a tree on the lawn, a hedge and inferred entrance steps with a ramp."""
    site = {"ground": {"levels": [], "points": []}, "pools": [],
            "paving": [{"id": "tt", "polygon": [list(q) for q in _TERRACE], "build": True}],
            "parking": [{"id": "pk", "polygon": [list(q) for q in _PARK], "build": True}]}
    pfs = [dict(pf, sloped=pf["id"] == "pk") for pf in S.platforms(site, terrain)]     # the parking draped (sloped)
    steps = {"opening_id": "d1", "blocks": [{"polygon": [(63.0, -1.2), (65.0, -1.2), (65.0, 0.0), (63.0, 0.0)],
                                             "z_top": 0.3}],
             "cheeks": [], "count": 1, "rise": 0.3, "rails": [], "posts": [],
             "ramp": {"polygon": [(65.0, -1.2), (68.0, -1.2), (68.0, -0.2), (65.0, -0.2)], "z_start": 0.3,
                      "z_end": 0.0, "s": [1.0, 4.0], "d": [0.0, 1.0], "length": 3.0, "slope": 0.1}}
    return {"mode": "full", "terrain": terrain, "outline": list(_OUTLINE), "plot": [(40, -14), (82, -14), (82, 16),
                                                                                   (40, 16)],
            "plot_source": "test", "extent": [(30, -24), (90, -24), (90, 26), (30, 26)], "wells": [], "plot_walls": [],
            "areas": [{"id": "path_d1", "kind": "path", "polygon": [list(q) for q in _PATH], "z": None,
                       "material": None, "colour": None, "source": "assumed", "area_id": None, "lift": S.PAVING_LIFT,
                       "inferred": True},
                      {"id": "pk", "kind": "parking", "polygon": [list(q) for q in _PARK], "z": None, "material": None,
                       "colour": None, "source": "site_plan", "area_id": None, "lift": S.PAVING_LIFT,
                       "platform_id": "pk"}],
            "trees": [{"id": "shrub_1", "kind": "tree", "center": [48.3, 0.7], "size": [0.718, 0.718]},
                      {"id": "tree_1", "kind": "tree", "center": [74.3, -9.6], "size": [4.0, 4.0]}],
            "not_built": [], "assumed": [], "warnings": [], "ground_is_grass": True,
            "inferred": {"steps": [steps], "boundary": [], "plot": [], "plot_inferred": False, "main": None,
                         "entrances": [], "paths": [], "trees": []},
            "copy_holes": [], "pools": [], "platforms": pfs, "climate": {"climate": "temperate"},
            "hedges": [{"id": "hedge_1", "polyline": [[44.0, -4.0], [54.0, -4.0]], "width_m": 0.7, "height_m": 1.2,
                        "height_class": "mid", "species": "cherry_laurel", "species_inferred": True,
                        "inferred": True, "evidence": [], "source": "site.hedges", "symbol_ids": [],
                        "reason": "a test hedge"}],
            "levers": {k: (k not in ("sky", "pools")) for k in S.SITE_LEVERS},
            "near_extent": [(30, -24), (90, -24), (90, 26), (30, 26)], "species": {}}


def test_fix2_the_lawn_relief_keeps_the_ground_level_under_paths_platforms_steps_and_plants():
    """Fix round part 2 (17 Oct 2026; review of part 1): the down-only relief lowered the lawn about 2 cm under
    everything built at terrain height (bpy 5.2.2: a draped path and a sloped parking 2.1 / 2.0 cm over the lawn, a
    shrub's and a tree's base 2.6 / 2.8 cm in the air). relief_keep lists those footprints, relief_weights keeps every
    ground vertex within relief_reach (the margin plus a cell's diagonal) of one at its level, so every ground face
    under a path, a platform, steps, a shrub, a tree or a hedge stays level as a whole."""
    terrain = S.terrain_model(_SLOPED, _OUTLINE)
    plan = _relief_plan(terrain)
    keep = S.relief_keep(plan)
    kinds = {}
    for k in keep:
        kinds[k["kind"]] = kinds.get(k["kind"], 0) + 1
    # holes: the building and the flat terrace; the parking's draped area has a platform (the sloped one stands in)
    assert kinds == {"hole": 2, "area": 1, "sloped_platform": 1, "steps": 2, "shrub": 1, "tree": 1, "hedge": 1}
    by = {(k["kind"], k["id"]): k["polygon"] for k in keep}
    assert G.point_in_polygon((48.3, 0.7), by[("shrub", "shrub_1")]) and G.point_in_polygon(
        (48.3 + 0.35, 0.7), by[("shrub", "shrub_1")])                       # the shrub's drawn crown (r 0.359 m)
    assert not G.point_in_polygon((74.3 + 1.0, -9.6), by[("tree", "tree_1")])        # a tree: its base only
    assert G.point_in_polygon((74.3 + S.RELIEF_KEEP_TREE_BASE_M - 0.01, -9.6), by[("tree", "tree_1")])
    assert G.point_in_polygon((44.0 - 0.3, -4.0 + 0.3), by[("hedge", "hedge_1")])    # half the width past each end
    step = S.grid_step(plan["extent"])
    reach = VG.relief_reach(step)
    assert reach == pytest.approx(VG.RELIEF_KEEP["margin_m"] + math.sqrt(2.0) * step)
    verts, faces = S.draped_faces(plan["extent"], S.ground_holes(plan), terrain)
    weights = VG.relief_weights(len(verts), faces, verts=verts, keep=[k["polygon"] for k in keep], reach=reach)
    old = VG.relief_weights(len(verts), faces)                              # part 1: the boundary vertices only

    def face_weights(x, y):
        """The weights of the ground face that holds (x, y)."""
        for f in faces:
            if G.point_in_polygon((x, y), [verts[i][:2] for i in f]):
                return [weights[i] for i in f], [old[i] for i in f]
        raise AssertionError((x, y))

    probes = [(51.5, -9.4), (45.1, -8.9), (57.9, -9.95), (47.0, 8.0), (42.1, 11.9), (48.3, 0.7), (74.3, -9.6),
              (49.0, -4.0), (64.0, -0.6), (67.5, -0.7)]
    for x, y in probes:                                   # path, parking, shrub, tree, hedge, steps, ramp
        new_w, old_w = face_weights(x, y)
        assert new_w and all(w == 0.0 for w in new_w), (x, y, new_w)
        assert any(w == 1.0 for w in old_w), (x, y)       # part 1 let these faces drop
    far = [i for i, (x, y, _z) in enumerate(verts) if all(not VG.near_polygon((x, y), k["polygon"], reach + 1.0)
                                                         for k in keep) and old[i] == 1.0]
    assert len(far) > 100 and all(weights[i] == 1.0 for i in far)         # the open lawn keeps its relief
    assert sum(weights) > 0.5 * sum(old)
    # the reach: a vertex just inside it stays level, one just outside moves
    square = [[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]]
    pts = [(0.5, 0.5), (1.0 + reach - 0.01, 0.5), (1.0 + reach + 0.01, 0.5), (0.5, -reach - 0.01)]
    assert VG.relief_weights(4, [[0, 1, 2, 3]], verts=pts, keep=square, reach=reach, pin_edges=False) == [
        0.0, 0.0, 1.0, 1.0]


class _FakeOb:
    """Stands in for a Blender object in build_site (fix round part 2 tests): the mesh and the attributes it sets."""

    def __init__(self, name, verts=(), faces=(), **kw):
        self.name, self.verts, self.faces, self.kw = name, list(verts), [list(f) for f in faces], kw


def _fake_build_site(monkeypatch, plan):
    """build_site on the CPU: the bpy calls replaced (common.new_mesh_object, vegetation.lawn_relief computes the
    real relief_weights on the fake ground's mesh, vegetation.grass_patch records its arguments)."""
    from wenart.blender import common
    calls = {"relief": [], "grass": []}
    monkeypatch.setattr(common, "new_mesh_object",
                        lambda name, verts, faces, **kw: _FakeOb(name, verts, faces, **kw))

    def fake_relief(ob, strength=None, scale=None, pin_edges=True, keep=(), reach=None):
        w = VG.relief_weights(len(ob.verts), ob.faces, verts=ob.verts, keep=keep, reach=reach, pin_edges=pin_edges)
        calls["relief"].append({"ob": ob, "keep": list(keep), "reach": reach, "weights": w})
        n = sum(1 for v in w if v > 0)
        return {"applied": n > 0, "weighted": n, "vertices": len(w)}

    def fake_grass(polygon, density, **kw):
        calls["grass"].append(dict(kw, polygon=polygon))
        return _FakeOb("grass_near"), {"method": "cards", "relief": bool(kw.get("relief")), "count": 1}

    def no_bpy(*_a, **_k):
        raise RuntimeError("no bpy in the CPU tests")

    monkeypatch.setattr(VG, "lawn_relief", fake_relief)
    monkeypatch.setattr(VG, "grass_patch", fake_grass)
    monkeypatch.setattr(VG, "tree_object", no_bpy)
    monkeypatch.setattr(VG, "hedge_object", no_bpy)
    looks = {k: {"material": k, "colour": None, "source": "build"} for k in (
        "garden", "paving", "plot_wall", "light_well", "bark", "foliage", "ground", "steps", "railing")}
    objs, assumed = [], []
    summary = S.build_site(plan, None, looks, lambda look: _FakeOb(str(look.get("material"))), objs, assumed)
    return summary, calls


def test_fix2_build_site_keeps_the_relief_off_built_things_and_gives_the_grass_the_ground_s_relief(monkeypatch):
    """Fix round part 2 (17 Oct 2026; review of part 1): build_site gives the ground's lawn relief the keep polygons of
    relief_keep with the ground's reach (the ground under the path, the sloped parking, the steps, the shrub and the
    tree stays level), and the near-camera grass the relief only when the ground got one, with the same polygons,
    reach and grid. On a flat site (the ground of convex pieces has no inner vertex, so no relief) the grass got the
    down-only relief alone and its clumps sank 2.1 cm into the lawn (bpy 5.2.2); now it gets none."""
    terrain = S.terrain_model(_SLOPED, _OUTLINE)
    plan = _relief_plan(terrain)
    summary, calls = _fake_build_site(monkeypatch, plan)
    (relief,) = calls["relief"]
    assert relief["ob"].name == "ground" and relief["reach"] == pytest.approx(VG.relief_reach(S.grid_step(
        plan["extent"])))
    keep = [k["polygon"] for k in S.relief_keep(plan)]
    assert relief["keep"] == keep
    verts, faces, w = relief["ob"].verts, relief["ob"].faces, relief["weights"]
    for x, y in ((51.5, -9.4), (47.0, 8.0), (48.3, 0.7), (74.3, -9.6), (49.0, -4.0), (64.0, -0.6)):
        face = next(f for f in faces if G.point_in_polygon((x, y), [verts[i][:2] for i in f]))
        assert all(w[i] == 0.0 for i in face), (x, y)
    lr = summary["lawn_relief"]
    assert lr["weighted"] > 0 and lr["range_m"] == list(VG.relief_range()) and lr["edges_kept"]
    assert lr["keep"] == {"hole": 2, "area": 1, "sloped_platform": 1, "steps": 2, "shrub": 1, "tree": 1, "hedge": 1}
    (grass,) = calls["grass"]
    assert grass["relief"] is True and grass["keep"] == keep and grass["reach"] == relief["reach"]
    assert grass["step"] == S.grid_step(plan["extent"])
    assert summary["grass"]["relief_requested"] is True and "follows" in summary["grass"]["relief_reason"]
    # a flat site: no relief on the ground, so none on the grass
    flat = {"kind": "flat", "z": {k: 0.0 for k in S.AXES}, "warnings": [], "assumed": []}
    fplan = dict(_relief_plan(flat), platforms=[], areas=_relief_plan(flat)["areas"][:1])
    summary, calls = _fake_build_site(monkeypatch, fplan)
    assert calls["relief"][0]["weights"] and not any(calls["relief"][0]["weights"])
    assert summary["lawn_relief"]["weighted"] == 0
    (grass,) = calls["grass"]
    assert grass["relief"] is False and summary["grass"]["relief"] is False
    assert summary["grass"]["relief_requested"] is False and "no relief" in summary["grass"]["relief_reason"]


def test_fix3_build_site_gives_the_haze_its_reserved_pass_index(monkeypatch):
    """Fix round part 3 (17 Oct 2026; review of part 2): Cycles writes the haze shell into the depth and index passes
    on a random half of the rays that cross it (bpy 5.2.2, real02's terrace and ext_2), and with index 0 the render
    could not tell the shell from a wall, so its sky pull ran on a speckled mask. build_site gives the haze object
    ``HAZE_PASS_INDEX`` (Blender's ``Object.pass_index`` maximum, above every index the build counts from 1) and records
    it in the haze's manifest entry; render.py reads the same constant (and stands it in for a scene built before)."""
    import jsonschema

    from wenart.blender import common
    from wenart.blender import render as R
    from wenart.blender import schemas as SC

    assert S.HAZE_PASS_INDEX == R._haze_index() == 32767
    monkeypatch.setattr(S, "haze_material", lambda: _FakeOb("site_haze"))
    terrain = S.terrain_model(_SLOPED, _OUTLINE)
    plan = dict(_relief_plan(terrain), levers={k: k == "sky" for k in S.SITE_LEVERS})
    objs, assumed = [], []
    made = {}
    monkeypatch.setattr(common, "new_mesh_object",
                        lambda name, verts, faces, **kw: made.setdefault(name, _FakeOb(name, verts, faces, **kw)))
    looks = {k: {"material": k, "colour": None, "source": "build"} for k in (
        "garden", "paving", "plot_wall", "light_well", "bark", "foliage", "ground", "steps", "railing")}
    S.build_site(plan, None, looks, lambda look: _FakeOb(str(look.get("material"))), objs, assumed)
    haze = made["haze"]
    assert haze.pass_index == S.HAZE_PASS_INDEX and haze.kw["wenart_id"] == "haze"
    (entry,) = [o for o in objs if o["wenart_id"] == "haze"]
    assert entry["pass_index"] == S.HAZE_PASS_INDEX and entry["kind"] == S.site_kind("haze")
    assert entry["material"] == "site_haze" and entry["site_part"] == "haze"
    jsonschema.validate(entry, SC.SCENE_OBJECT)                         # the scene manifest takes the record
    # no other site object carries an index: the haze is the only reserved one
    assert all(o["pass_index"] is None for o in objs if o["wenart_id"] != "haze")


def test_fix2_a_replayed_aerial_without_sky_is_repitched_about_its_target():
    """Fix round part 2 (17 Oct 2026; the lead's decision on the review of part 1: the CLAUDE.md horizon rule wins):
    P4 replays real02's M11 ext_5 (aerial, 30 degrees down at 28.54 mm: the horizon at 1.31 of the frame height, no
    sky). build.repitch_replayed_aerials keeps its target, its distance and its compass direction and gives it the
    planner's aerial pitch (copies.pitch_for_horizon(AERIAL_HORIZON_FRAC, min(lens, AERIAL_LENS_MM),
    AERIAL_PITCH_DEG)) with its lens at most AERIAL_LENS_MM; the record says ``replay: repitched`` with the old and
    new pitch and the reason. A corner view, the site view and an aerial that already shows the sky stay as replayed."""
    from wenart.blender import build as BB
    from wenart.blender import cameras as C

    ext5 = {"name": "ext_5", "kind": "exterior", "view": "aerial", "lens_mm": 28.54, "sensor_mm": 36.0,
            "resolution": [1920, 1080], "shift_y": 0.0, "position": [-12.1724, -9.4236, 16.2917],
            "target": [7.1726, 6.517, 1.8195], "room_id": None, "level_id": None}
    corner = dict(ext5, name="ext_1", view="corner", lens_mm=26.0, position=[-6.3495, -10.8243, 1.6],
                  target=[1.5159, -1.1091, 1.6], shift_y=0.0455)
    site_view = dict(ext5, name="ext_7", site_view=True, lens_mm=24.0)
    low = dict(ext5, name="ext_9", lens_mm=26.0, position=[-20.0, 6.517, 4.0])         # 7.4 degrees down: sky
    plans = C.replay_cameras({"cameras": [ext5, corner, site_view, low]})["plans"]
    before = {p["name"]: json.loads(json.dumps(p)) for p in plans}
    assert CP.horizon_fraction(30.0, 28.54) > 1.3                         # the M11 aerial: no sky
    assert BB.repitch_replayed_aerials(plans) == ["ext_5"]
    got = {p["name"]: p for p in plans}
    for name in ("ext_1", "ext_7", "ext_9"):
        assert got[name] == before[name] and "replay" not in got[name], name
    p = got["ext_5"]
    pitch = CP.pitch_for_horizon(E.AERIAL_HORIZON_FRAC, min(28.54, E.AERIAL_LENS_MM), E.AERIAL_PITCH_DEG)
    rp = p["replay"]
    assert rp["status"] == "repitched" and rp["pitch_deg_old"] == pytest.approx(-30.0, abs=0.01)
    assert rp["pitch_deg"] == pytest.approx(-pitch) and p["pitch_deg"] == pytest.approx(-pitch)
    assert rp["lens_mm_old"] == 28.54 and rp["lens_mm"] == p["lens_mm"] == E.AERIAL_LENS_MM
    assert rp["horizon_frac_old"] == pytest.approx(CP.horizon_fraction(30.0, 28.54), abs=1e-3)
    assert rp["horizon_frac"] == p["horizon_frac"] == pytest.approx(E.AERIAL_HORIZON_FRAC, abs=1e-3)
    assert rp["position_old"] == ext5["position"] and "CLAUDE.md" in rp["reason"] and "horizon" in rp["reason"]
    assert p["target"] == ext5["target"]                                   # the target, the distance, the direction
    assert math.dist(p["position"], p["target"]) == pytest.approx(math.dist(ext5["position"], ext5["target"]),
                                                                  abs=1e-3)
    az = lambda q: math.atan2(q[1] - ext5["target"][1], q[0] - ext5["target"][0])  # noqa: E731
    assert az(p["position"]) == pytest.approx(az(ext5["position"]), abs=1e-4)
    down = math.degrees(math.atan2(p["target"][2] - p["position"][2],
                                   math.hypot(p["target"][0] - p["position"][0], p["target"][1] - p["position"][1])))
    assert down == pytest.approx(-pitch, abs=0.01) and CP.horizon_fraction(-down, p["lens_mm"]) < 1.0
    summary = BB.cameras_from_summary({"path": "m.json"}, {"plans": plans, "dropped": []}, plans, False)
    assert summary["repitched"] == ["ext_5"]
    import inspect                                                        # the build re-pitches the replayed set
    assert "repitch_replayed_aerials(ext_replayed)" in inspect.getsource(BB.main)
    m11 = ROOT / "results" / "renders" / "real02" / "scene_manifest.json"
    if m11.is_file():                                                     # P4's camera file
        rplans = [q for q in C.replay_cameras(json.loads(m11.read_text(encoding="utf-8")))["plans"]
                  if q["kind"] == "exterior"]
        assert BB.repitch_replayed_aerials(rplans) == ["ext_5"]
        q = next(q for q in rplans if q["name"] == "ext_5")
        assert q["replay"]["pitch_deg_old"] == pytest.approx(-30.0, abs=0.01)
        assert q["horizon_frac"] == pytest.approx(E.AERIAL_HORIZON_FRAC, abs=1e-3)


def test_p3_real04_tree_symbols_are_shrubs_by_their_drawn_crown(monkeypatch):
    """Item 4 of the P3 analysis: "every drawn tree symbol became a shrub". Checked, not a misreading: real04's 100
    tree symbols (the committed building: 19 single ones, 81 in the four hedge rows; P3's: 20 single ones) are
    INSERTs of one block on layer BS_09_AGAC with a 0.359 m crown radius as drawn (the DXF reader explodes the block
    with its insert scale, virtual_entities), 0.7-0.8 m apart; CLAUDE.md: "tree height follows the crown radius by
    size class (a crown under 1.5 m is a shrub)". So they stay 0.86 m shrubs (tree_height), now standing on the
    terrace or band they are drawn on."""
    if not REAL04.is_file():
        pytest.skip("no committed real04 building")
    b = json.loads(REAL04.read_text(encoding="utf-8"))
    symbols = [d for d in b["site"]["decor"] if d.get("kind") == "tree"]
    assert len(symbols) == 100 and {tuple(t["size"]) for t in symbols} == {(0.718, 0.718)}
    prep = _real04_prep(monkeypatch)
    singles, hedges = prep["site"]["trees"], prep["site"]["hedges"]
    assert len(hedges) == 4 and len(singles) + sum(len(h["symbol_ids"]) for h in hedges) == 100
    assert S.tree_height(0.718 / 2.0) == (pytest.approx(0.862), "shrub")
    assert {S.tree_parts(t, prep["site"]["terrain"])["size_class"] for t in singles} == {"shrub"}
    assert S.tree_height(1.5)[1] == "small"


# --------------------------------------------------------------------------
# Fix round after P4b (17 Oct 2026; pod P4b, real03: runs/20261017-091212-full/results, not committed)
# --------------------------------------------------------------------------

# P4b's real03 inputs of site.place_trees (build.prepare of the run's building_final.json): the ground outline (a
# 33.3 x 14.8 m bungalow), the inferred plot (6 m margin), the inferred path and the 22 outside windows
# (centre, outward, width); the entrance facade faces -y.
P4B_REAL03_OUTLINE = [
    [0, 6.179], [0.004, 6.179], [0.004, 0.925], [0.154, 0.925], [0.154, 0.941], [0.404, 0.941], [0.404, 1],
    [3.154, 1], [3.154, 0.15], [3.079, 0.15], [3.079, 0], [3.154, 0], [3.154, -0.009], [3.454, -0.009], [3.454, 0],
    [13.638, 0], [13.638, 0], [16.579, 0], [16.579, 0], [19.564, 0], [19.564, -0.095], [20.053, -0.095],
    [20.053, 0], [29.752, 0], [29.752, -0.017], [30.067, -0.017], [30.067, 0], [30.129, 0], [30.129, 0.15],
    [30.067, 0.15], [30.067, 1], [32.804, 1], [32.804, 0.941], [33.054, 0.941], [33.054, 0.925], [33.204, 0.925],
    [33.204, 6.418], [33.332, 6.418], [33.332, 6.973], [33.204, 6.973], [33.204, 12.475], [33.054, 12.475],
    [33.054, 12.45], [32.804, 12.45], [32.804, 12.4], [30.067, 12.4], [30.067, 13.408], [30.054, 13.408],
    [30.054, 13.45], [29.954, 13.45], [29.954, 13.408], [29.752, 13.408], [29.752, 13.4], [26.404, 13.4],
    [26.404, 14.75], [26.104, 14.75], [26.104, 14.6], [23.504, 14.6], [23.504, 14.75], [23.204, 14.75],
    [23.204, 14.2], [10.004, 14.2], [10.004, 14.75], [9.704, 14.75], [9.704, 14.6], [7.104, 14.6], [7.104, 14.75],
    [6.804, 14.75], [6.804, 13.4], [3.454, 13.4], [3.454, 13.4], [3.254, 13.4], [3.254, 13.45], [3.154, 13.45],
    [3.154, 12.4], [0.404, 12.4], [0.404, 12.45], [0.154, 12.45], [0.154, 12.475], [0.004, 12.475], [0.004, 7.208],
    [0, 7.208]]
P4B_REAL03_PLOT = [(-6.0, -6.0948), (39.3318, -6.0948), (39.3318, 20.7503), (-6.0, 20.7503)]
P4B_REAL03_PATHS = [{"polygon": [[14.103, -6.1448], [16.203, -6.1448], [16.203, -1.1997], [14.103, -1.1997]]}]
P4B_REAL03_WINDOWS = [
    ((15.204, 0.225), (0, -1), 2.9), ((18.079, 0.225), (0, -1), 2.55), ((5.028, 0.075), (0, -1), 1.6),
    ((8.753, 0.075), (0, -1), 1.6), ((11.603, 0.075), (0, -1), 1.6), ((21.603, 0.075), (0, -1), 1.6),
    ((24.453, 0.075), (0, -1), 1.6), ((28.178, 0.075), (0, -1), 1.6), ((1.753, 1.075), (0, -1), 1.6),
    ((31.453, 1.075), (0, -1), 1.6), ((1.753, 12.325), (0, 1), 1.6), ((31.453, 12.325), (0, 1), 1.6),
    ((5.028, 13.325), (0, 1), 1.6), ((28.178, 13.325), (0, 1), 1.6), ((12.203, 14.125), (0, 1), 1.6),
    ((15.241, 14.125), (0, 1), 1.6), ((17.965, 14.125), (0, 1), 1.6), ((21.003, 14.125), (0, 1), 1.6),
    ((0.079, 3.526), (-1, 0), 1.6), ((0.079, 9.876), (-1, 0), 1.6), ((33.129, 3.526), (1, 0), 1.6),
    ((33.129, 9.876), (1, 0), 1.6)]


def _p4b_windows():
    return [{"centre": c, "outward": o, "opening": {"width": w}} for c, o, w in P4B_REAL03_WINDOWS]


def _corner_sightlines(outline):
    """The 30 degree lines of sight of the corner views from the corners of an axis-aligned outline (E14)."""
    xs, ys = [p[0] for p in outline], [p[1] for p in outline]
    out = []
    for cx, sx in ((min(xs), -1.0), (max(xs), 1.0)):
        for cy, sy in ((min(ys), -1.0), (max(ys), 1.0)):
            a = math.radians(S.INFERRED["sightline_deg"])
            for d in ((sx * math.cos(a), sy * math.sin(a)), (sx * math.sin(a), sy * math.cos(a))):
                out.append(((cx, cy), (cx + d[0] * S.INFERRED["sightline_m"], cy + d[1] * S.INFERRED["sightline_m"])))
    return out


def test_p4b_real03_gets_inferred_trees_from_the_framing_pass_and_says_how():
    """P4b look lens (verified in part): real03's exterior was a bare paddock; the documents draw no planting and
    site.place_trees kept none of its 122 candidates (the 8 m window bands of the 22 windows removed 108), silently.
    The relaxed second pass of the fix round after P4b placed 2 behind the building. 26 Oct 2026 (real06, the framing
    rule, ``site.TREE_FRAMING``): the framing pass places all 3 planned trees, never in the front garden, on a corner
    view's line of sight, at a plot corner or near the building, out of every window's light zone and straight view,
    each seen from windows, 6 m apart; the stats name the window band of the strict pass; ``trees_record`` lists
    "placed 3 of 3" and the framing pass. Fails on HEAD 11949a9 (0 trees, no stats)."""
    stats = {}
    trees = S.place_trees(P4B_REAL03_PLOT, P4B_REAL03_OUTLINE, P4B_REAL03_PATHS, _p4b_windows(),
                          {"direction": (0.0, -1.0)}, 3, stats=stats)
    assert len(trees) == 3 and all(t["inferred"] and t["placement"] == "framing" for t in trees)
    assert stats["candidates"] == 122 and stats["placed_first"] == 0 and stats["relaxed"]
    assert stats["placed"] == 3 and stats["placed_relaxed"] == 3 and not stats["beyond"]
    assert stats["top_filter"] == "window" and stats["removed"]["window"] == 108
    assert stats["passes"][0] == {"name": "strict", "ran": True, "candidates": 122, "kept": 0, "placed": 0,
                                  "removed": stats["removed"]}             # the strict pass alone: the old nothing
    r = S.INFERRED["tree_crown"] / 2.0
    front_edge = max(-p[1] for p in P4B_REAL03_OUTLINE)
    lines = _corner_sightlines(P4B_REAL03_OUTLINE)
    cfg = S.TREE_FRAMING
    for t in trees:
        x, y = t["center"]
        assert -y <= front_edge - S.INFERRED["front_zone_extra"]                          # not in the front garden
        assert all(G.point_segment_distance((x, y), a, b) >= r + S.INFERRED["tree_sightline"] for a, b in lines)
        assert geom2d.distance_to_polygon_edges((x, y), P4B_REAL03_OUTLINE) >= S.INFERRED["tree_from_building"] - 1e-6
        assert min(math.dist((x, y), c) for c in P4B_REAL03_PLOT) > 5.0                  # not at a plot corner
        for w in _p4b_windows():                                  # out of the light zone and the straight view
            assert S.window_zone((x, y), w, r, cfg["light_m"], cfg["side_m"], cfg["view_m"]) is None
        assert len(t["seen_from"]) >= 2 and t["window_distance_m"] >= cfg["light_m"] + r
        assert "frames the windows' view" in t["reason"] and "the strict pass placed 0 of 3" in t["reason"]
    assert all(math.dist(a["center"], b["center"]) >= S.INFERRED["tree_spacing"]
               for i, a in enumerate(trees) for b in trees[i + 1:])
    entry, warning = S.trees_record(stats)
    assert entry["field"] == "trees" and entry["value"] == 3 and warning is None
    assert "placed 3 of 3" in entry["reason"] and "most by window" in entry["reason"]
    assert "the framing pass (the window rule near the facade only) placed 3 of 1100" in entry["reason"]


def test_p4b_inferred_site_lists_its_trees_and_warns_when_short():
    """Every build that infers trees lists ``inferred trees: placed k of n`` in ``assumed`` (CLAUDE.md: everything
    inferred is listed); fewer than asked also gives a site warning (site_plan's warnings). The first pass is
    enough on an open plot (no relaxed pass, no warning); real02's two first-pass trees stay as they were (its
    test_e11 pins them at x -3.6 and 18.8)."""
    pts = [(0, 0), (10, 0), (10, 8), (0, 8)]
    walls = [{"id": f"w{i}", "level_id": "L0", "start": list(pts[i]), "end": list(pts[(i + 1) % 4]),
              "thickness": 0.25, "exterior": True} for i in range(4)]
    b = {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.8}], "walls": walls, "openings": [],
         "rooms": [], "slabs": [], "site": {"ground": {"levels": [{"side": "all", "z": {"value": 0.0,
                                                                                         "method": "vector"}}]}},
         "facade": {}}
    outline, _ = geom2d.wall_outline(b["walls"])
    plan = S.site_plan(b, b["levels"], outline, "full", options={"path": False, "fence": "none", "trees": 2})
    inf = plan["inferred"]
    assert len(inf["trees"]) == 2 and not inf["tree_stats"]["relaxed"] and inf["warnings"] == []
    [entry] = [a for a in plan["assumed"] if a["field"] == "trees"]
    assert entry["value"] == 2 and entry["reason"].startswith("inferred trees: placed 2 of 2")
    many = S.site_plan(b, b["levels"], outline, "full", options={"path": False, "fence": "none", "trees": 40})
    short = [w for w in many["warnings"] if w.startswith("inferred trees: placed ")]
    assert len(short) == 1 and f"placed {len(many['inferred']['trees'])} of 40" in short[0]
    # trees: 0 (the agent's choice) infers nothing and lists nothing
    none = S.site_plan(b, b["levels"], outline, "full", options={"path": False, "fence": "none", "trees": 0})
    assert none["inferred"]["trees"] == [] and not [a for a in none["assumed"] if a["field"] == "trees"]


def test_p4b_flat_cut_parapet_and_slab_edge_take_the_facade_look():
    """P4b look lens (the cause the verifier confirmed): real03's flat_cut roof gave its 0.30 m parapet and the slab
    edge (roof slot 2, ``roof.SLOT_FASCIA``) the roof covering (concrete_tiles), so the band read as a tiled
    mansard. ``build.roof_slot_looks`` gives a flat_cut roof's fascia slot the facade look and an assumed entry with
    the reason; pitched (real02) and mansard (real04) roofs keep the roof look on both slots; the build uses it.
    Fails on HEAD 11949a9 (no roof_slot_looks; the build passed looks["roof"] to slot 2)."""
    import inspect

    from wenart.blender import build as BB
    from wenart.blender import roof as R

    looks = {"roof": {"material": "concrete_tiles", "colour": "anthracite"},
             "facade": {"material": "render", "colour": "warm greige", "asset": "grey_plaster"}}
    covering, fascia, note = BB.roof_slot_looks({"kind": "flat_cut", "parapet": 0.3}, looks)
    assert covering is looks["roof"] and fascia is looks["facade"]
    assert note["object"] == "roof" and note["field"] == "parapet_material" and note["value"] == "render"
    assert "0.30 m parapet" in note["reason"] and "concrete_tiles" in note["reason"]
    for kind in (None, "pitched", "mansard"):
        assert BB.roof_slot_looks({"kind": kind}, looks) == (looks["roof"], looks["roof"], None)
    # 24 Oct 2026: a pitched roof type gets the fascia board (the gutter's look) on slot 2
    _c, board, why = BB.roof_slot_looks({"type": "mansard"}, looks)
    assert board["material"] == "aluminium_anthracite" and why["field"] == "fascia_material"
    assert BB.roof_slot_looks({"type": "flat"}, looks) == (looks["roof"], looks["roof"], None)
    src = inspect.getsource(BB.main)
    assert "roof_slot_looks(roof, looks)" in src and "shell.look_material(library, fascia)" in src
    # the parapet ring and the slab edge are the faces of slot 2
    model = {"kind": "flat_cut", "parapet": 0.3, "equations": [(0.0, 0.0, 3.0)],
             "outline": [(0, 0), (10, 0), (10, 8), (0, 8)], "openings": [], "planes": [], "thickness": 0.2}
    ring = R.parapet_ring(model)
    assert len(ring) == 4
    _verts, faces, slots = R.roof_solid(dict(model, equations=[[0.0, 0.0, 3.0]]))
    assert slots.count(R.SLOT_FASCIA) >= 4 * 6


# real03's fire stair (P4b building_final.json, f_L0_032) and the two walls of its 2.6 m stairwell
P4B_FIRE_STAIR = {
    "id": "f_L0_032", "level_id": "L0", "type": "stair", "room_id": "r_L0_yangin_merdiveni",
    "footprint": {"center": [8.403, 12.0018], "size": [3.6375, 2.6], "rotation_deg": 90.0},
    "stair": {"flights": [{"start": [7.703, 10.2355], "end": [7.703, 13.2055], "width": 1.2, "lines": 12,
                           "spacing": 0.27},
                          {"start": [9.103, 10.2655], "end": [9.103, 13.2355], "width": 1.2, "lines": 12,
                           "spacing": 0.27}],
              "landing": {"polygon": [[7.103, 13.2355], [9.703, 13.2355], [9.703, 13.8205], [7.103, 13.8205]],
                          "depth": 0.585},
              "direction": [0.0, 1.0], "direction_assumed": True, "turn": "U", "turn_assumed": True,
              "void_assumed": True, "riser_m": None, "riser_source": None}}
P4B_STAIRWELL = [{"id": "w_L0_097", "level_id": "L0", "start": [6.9539, 7.5503], "end": [6.9539, 14.6003],
                  "thickness": 0.3},
                 {"id": "w_L0_103", "level_id": "L0", "start": [9.8539, 11.4905], "end": [9.8539, 14.6003],
                  "thickness": 0.3}]


def test_p4b_fire_stair_meets_its_walls_and_its_structure_is_smooth_paint():
    """P4b look lens, yangin_merdiveni_3: a light slit down the wall at the joint of the flight and the wall, and
    coarse plaster on the stringer. Measured: the drawn U-stair is as wide as its stairwell, but its centre was read
    0.9 mm off, so flight 2 and the landing stop 0.9 mm short of w_L0_103's face (flight 1 and the landing's other
    edge are 0.9 mm inside w_L0_097). ``shell.stair_wall_joints`` takes every flight side and landing edge within
    5 cm of a parallel wall face 1 cm into the wall (an assumed ``stair_wall_joint`` entry; the drawn footprint
    stays); ``parametric.stair_parts`` builds the steps and the landing to it; the rails keep the drawn width;
    ``build_stairs`` builds through ``stair_build_plan`` (plan_stairs' plan is unchanged). The
    structure slot is the wall colour as a smooth paint (``stair_structure_slot``: no wall texture set). Fails on HEAD
    11949a9 (no wall joints; the right flight ends at x 9.703 < the face 9.7039)."""
    import inspect

    from wenart.blender import parametric as P
    from wenart.blender import shell as SH

    face_r = 9.8539 - 0.15
    face_l = 6.9539 + 0.15
    plan = P.stair_plan(copy.deepcopy(P4B_FIRE_STAIR), 2.85, 2.7, walls=P4B_STAIRWELL)
    bare = P.stair_parts(plan)
    assert max(v[0] for p in bare if p["role"] in ("step", "landing") for v in p["verts"]) < face_r    # the slit
    joints = SH.stair_wall_joints(plan, P4B_STAIRWELL)
    got = {(j["part"], j.get("flight", j.get("edge")), j["wall_id"]): (j["gap_m"], j["extend_m"]) for j in joints}
    assert got == {("flight", 0, "w_L0_097"): (-0.0009, 0.0091), ("flight", 1, "w_L0_103"): (0.0009, 0.0109),
                   ("landing", 1, "w_L0_103"): (0.0009, 0.0109), ("landing", 3, "w_L0_097"): (-0.0009, 0.0091)}
    [entry] = [a for a in plan["assumed"] if a["kind"] == "stair_wall_joint"]
    assert "drawn footprint is kept" in entry["reason"] and set(entry) == {"field", "kind", "value", "reason"}
    parts = P.stair_parts(plan)
    for role in ("step", "landing"):
        xs = [v[0] for p in parts if p["role"] == role for v in p["verts"]]
        assert max(xs) == pytest.approx(face_r + SH.STAIR_JOINT_EMBED_M, abs=1e-4)
        assert min(xs) == pytest.approx(face_l - SH.STAIR_JOINT_EMBED_M, abs=1e-4)
    # the inner sides (the 0.2 m well between the flights), the landing's open edges and the rails stay as drawn
    inner = [v[0] for p in parts if p["role"] == "step" and p["flight"] == 0 for v in p["verts"]]
    assert max(inner) == pytest.approx(7.703 + 0.6, abs=1e-6)
    land = [v for p in parts if p["role"] == "landing" for v in p["verts"]]
    assert min(v[1] for v in land) == pytest.approx(13.2355) and max(v[1] for v in land) == pytest.approx(13.8205)
    assert [p for p in parts if p["key"] == "steel"] == [p for p in bare if p["key"] == "steel"]
    assert len(parts) == len(bare) and SH.stair_record(plan, parts)["wall_joints"] == joints
    # nothing near a wall: no joint, the parts as drawn
    free = P.stair_plan(copy.deepcopy(P4B_FIRE_STAIR), 2.85, 2.7, walls=[])
    assert SH.stair_wall_joints(free, []) == [] and P.stair_parts(free) == P.stair_parts(
        P.stair_plan(copy.deepcopy(P4B_FIRE_STAIR), 2.85, 2.7, walls=[]))
    # a wall 8 cm away is a real gap of the drawing, not a joint
    far = [dict(w, start=[w["start"][0] + 0.08, w["start"][1]], end=[w["end"][0] + 0.08, w["end"][1]])
           if w["id"] == "w_L0_103" else w for w in P4B_STAIRWELL]
    assert {j["wall_id"] for j in SH.stair_wall_joints(P.stair_plan(copy.deepcopy(P4B_FIRE_STAIR), 2.85, 2.7,
                                                                    walls=far), far)} == {"w_L0_097"}
    # build_stairs builds a copy with the joints on the level's walls; plan_stairs' plan stays as it was
    level = {"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}
    building = {"levels": [level], "walls": P4B_STAIRWELL, "rooms": [], "openings": [],
                "furniture": [copy.deepcopy(P4B_FIRE_STAIR)]}
    [item] = SH.plan_stairs(building, level)
    built = SH.stair_build_plan(item["plan"], P4B_STAIRWELL)
    assert len(built["wall_joints"]) == 4 and "wall_joints" not in item["plan"]
    assert len(built["assumed"]) == len(item["plan"]["assumed"]) + 1
    src = inspect.getsource(SH.build_stairs)
    assert "stair_build_plan(plan, level_walls)" in src and src.index("stair_build_plan(") < src.index("stair_mesh(")
    # the structure slot: the wall colour without its texture set and tint
    walls_style = {"material": "paint", "asset": "plastered_wall", "colour": "warm greige", "tint": [1.0, 0.9, 0.8]}
    assert SH.stair_structure_slot(walls_style) == {"material": "paint", "colour": "warm greige"}
    assert "stair_structure_slot(walls_style)" in inspect.getsource(SH.build_stairs)


# --------------------------------------------------------------------------
# Pass before P5 (17 Oct 2026; the review of the fix round after P4b): the stair structure of "white walls" styles
# --------------------------------------------------------------------------

class _Mat(dict):
    """A Blender material stand-in: the name and what ``materials.pbr_material`` was given."""

    def __init__(self, name, slug, tset, tint, base_rgb):
        super().__init__()
        self.name, self.slug, self.tset, self.tint, self.base_rgb = name, slug, tset, tint, base_rgb


def _bpy_free_library(monkeypatch, tmp_path, shell: bool = True):
    """A ``MaterialLibrary`` whose manifest holds every vocabulary set as a usable CC0 set (files on disk), with
    ``pbr_material`` and ``apply_shell_layers`` replaced by recorders: ``MaterialLibrary.get``'s choice of the texture
    set, the shell slot and the colour run as on the pod."""
    from wenart.blender import materials as M

    monkeypatch.setattr(M, "pbr_material", lambda name, slug, tset, tint=None, unverified=False, procedural=None,
                        base_rgb=None, params=None: _Mat(name, slug, tset, tint, base_rgb))
    monkeypatch.setattr(M, "apply_shell_layers", lambda mat, spec, textured, procedural: sorted(spec["layers"]))
    textures = {}
    for entry in M.ENTRIES.values():
        aid = entry.get("asset")
        if aid and entry.get("source") in M.CC0_SOURCES and aid not in textures:
            files = {}
            for key in ("albedo", "normal", "roughness"):
                path = tmp_path / f"{aid}_{key}.png"
                path.write_bytes(b"png")
                files[key] = str(path)
            textures[aid] = {"source": entry["source"], "licence": "CC0", "files": files, "size_m": [1.0, 1.0]}
    return M, M.MaterialLibrary(textures, None, levers={"shell": shell})


def test_p5_stair_structure_of_white_plaster_walls_gets_no_texture_set_back(monkeypatch, tmp_path):
    """Review of the fix round after P4b (S_site): every "white walls" style (synthetic-01/02/05/06/07, real01, the
    profile fallback) has walls ``plaster_white`` + white_plaster_02. ``stair_structure_slot`` dropped the asset, and
    ``MaterialLibrary.get`` with the shell lever on maps a bare ``plaster_white`` to the ceiling slot and puts
    white_plaster_02 back: the stringer kept the wall's plaster photo and normal map, as the material
    ``plaster_white__white_plaster_02__ceiling``. Fails on HEAD adc3004 (the structure is that textured ceiling
    material). Now it is ``paint`` with the walls' colour (the slug's flat colour as a tint) and the paint's plaster
    layers, no set; real04's walls (P3: ``paint`` + plastered_wall in warm greige) keep ``paint`` in warm greige."""
    from wenart.blender import shell as SH

    M, lib = _bpy_free_library(monkeypatch, tmp_path)
    white = json.loads((ROOT / "results" / "renders" / "synthetic-01" / "style.json").read_text(encoding="utf-8"))
    walls = white["walls"]
    assert walls == {"material": "plaster_white", "asset": "white_plaster_02", "colour": None}
    wall = SH.slot_material(lib, walls)
    ceiling = SH.slot_material(lib, {"material": "plaster_white", "colour": None})
    assert lib.records[wall.name]["textured"] and lib.records[ceiling.name]["shell_slot"] == "ceiling"
    assert lib.records[ceiling.name]["textured"]                    # the stand-in the structure must not get
    slot = SH.stair_structure_slot(walls)
    assert slot == {"material": "paint", "tint": [0.8656, 0.92, 1.0114]}
    structure = SH.slot_material(lib, slot)
    rec = lib.records[structure.name]
    assert (rec["textured"], rec["asset"], rec["maps"], structure.tset) == (False, None, [], None)
    assert structure.name not in (wall.name, ceiling.name)
    assert rec["shell_slot"] == "plaster" and rec["shell_layers"] == ["ao", "bevel", "imperfection"]
    colour = M._tinted(M.flat_colour(structure.slug), structure.tint)
    assert colour == pytest.approx(M.flat_colour("plaster_white"), abs=1e-4)    # the walls' colour, no photo
    # a colour phrase that colours the walls is the paint's colour
    sage = SH.slot_material(lib, SH.stair_structure_slot(dict(walls, colour="sage")))
    assert not lib.records[sage.name]["textured"] and sage.base_rgb == M.colour_linear("sage") and sage.tint is None
    # real04 (P3's style when the run folder is here): unchanged
    p3 = ROOT / "runs" / "20261016-172855-full" / "results" / "renders" / "real04" / "style.json"
    real04 = (json.loads(p3.read_text(encoding="utf-8"))["walls"] if p3.is_file() else
              {"material": "paint", "asset": "plastered_wall", "colour": "warm greige"})
    assert SH.stair_structure_slot(real04) == {"material": "paint", "colour": "warm greige"}
    greige = SH.slot_material(lib, SH.stair_structure_slot(real04))
    assert greige.name == "paint__warm_greige" and not lib.records[greige.name]["textured"]
    # every vocabulary wall slug with its own set: the structure never ends up textured, lever on or off
    for shell in (True, False):
        _, lib2 = _bpy_free_library(monkeypatch, tmp_path, shell=shell)
        for slug, entry in M.ENTRIES.items():
            mat = SH.slot_material(lib2, SH.stair_structure_slot({"material": slug, "asset": entry.get("asset")}))
            assert not lib2.records[mat.name]["textured"], (shell, slug, mat.name)
    assert {s for s in M.ENTRIES if SH.shell_stand_in(s)} == {"plaster_white", "stone_worktop", "steel_brushed"}
