"""The landscape (1 Nov 2026, lessons UL248, UL249; user on real04 run 20261031-194116-full: "This section also too plain
front of the house", "Outside areas needs a touch up").

Pure tests, no Blender, on synthetic sites (a house on a garden whose ground drops in a bank towards the street) and,
when the committed latest baseline is in the checkout, a real04 replay: the terrain is never paved (the agent's ground
override of the run is refused), a bank gets planting (terraced when steep), never paving; paved areas get a border band,
beds a lawn edge; planters stand by an entrance, lights along a path; nothing stands in a walkway."""
import copy
import json
from pathlib import Path

import pytest

from wenart.blender import exterior_checks as XC
from wenart.blender import grading as GR
from wenart.blender import landscape as LS
from wenart.blender import overrides as O
from wenart.blender import site as S
from wenart.levels import terrain as T

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results" / "baseline" / "latest" / "furniture" / "real04" / "building_final.json"
MANIFEST = ROOT / "results" / "baseline" / "latest" / "renders" / "real04" / "scene_manifest.json"


def _rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _terrain(profile) -> dict:
    """A TIN ground whose level follows ``profile`` (``[(y, z)]``, linear between) across the whole site."""
    pts = [(x, y, z) for x in (-30.0, -10.0, 10.0, 30.0) for y, z in profile]
    surface = T.fit_surface(pts)
    return {"kind": surface["kind"], "surface": surface, "z": {}, "rect": [-10, -10, 10, 10]}


def _site(profile, areas=(), doors=(), steps=(), hedges=()) -> dict:
    """A house (0..10 x 0..8) in a plot (-6..16 x -9..14), its front (-y) towards a street; the ground as ``profile``."""
    return {"mode": "full", "terrain": _terrain(profile), "outline": _rect(0.0, 0.0, 10.0, 8.0),
            "plot": _rect(-6.0, -9.0, 16.0, 14.0), "copy_holes": [], "wells": [], "aprons": [], "hedges": list(hedges),
            "trees": [], "pools": [], "platforms": [], "areas": list(areas), "climate": {"climate": "mediterranean"},
            "inferred": {"steps": list(steps)}, "outside_doors": list(doors), "style_family": "modern"}


# the ground drops 1.2 m over 3 m (1:2.5) in front of the house: a planted bank; 1.6 m over 1.2 m: a terraced one
GENTLE = [(14.0, 0.0), (-1.0, 0.0), (-4.0, -1.2), (-9.0, -1.2)]
STEEP = [(14.0, 0.0), (-1.5, 0.0), (-2.7, -1.6), (-9.0, -1.6)]


def _path(pid, poly):
    return {"id": pid, "kind": "path", "polygon": [list(p) for p in poly], "z": None, "inferred": True,
            "source": "assumed", "reason": "test"}


def _in(p, polys):
    return any(S.G.point_in_polygon(p, q) for q in polys)


def test_the_terrain_is_never_paved():
    """Rule 1 (UL248): the ground and garden slots take a soft finish only: the agent's set_material ground paving_stone
    (real04's override) is refused by the code check, an override stored before the rule keeps the garden soft, and the
    build's terrain falls back to the lawn under any hard garden look (a brief's or a style's)."""
    assert LS.is_soft("grass") and LS.is_soft("gravel__gravel_floor_02") and not LS.is_soft("paving_stone__floor_tiles_02")
    refused = XC.validate_material_override({}, {"ground": "paving_stone"})
    assert not refused["ok"] and any("hard finish" in f for f in refused["failed"])
    assert not XC.validate_material_override({}, {"garden": "paving"})["ok"]
    assert XC.validate_material_override({}, {"ground": "grass"})["ok"]
    assert XC.validate_material_override({}, {"paving": "paving_stone"})["ok"]        # paving stays on the paving slot
    ext = XC.validate_exterior_override({"levels": [], "walls": []}, {"ground": "paving_stone"})
    assert not ext["ok"] and any("hard finish" in f for f in ext["failed"])
    looks = {"garden": {"material": "grass", "colour": None, "source": "fallback"}, "paving": {"material": "paving"}}
    out, applied = O.apply_looks(looks, {"ground": "paving_stone", "paving": "paving_stone"})
    assert out["garden"]["material"] == "grass" and out["paving"]["material"] == "paving_stone"
    assert any(a["slot"] == "garden" and a.get("refused") for a in applied)
    look, note = LS.terrain_look({"material": "paving_stone", "source": "brief"})
    assert look["material"] == LS.TERRAIN_FALLBACK and look["replaced"] == "paving_stone" and "never paved" in note
    kept, none = LS.terrain_look({"material": "gravel", "source": "brief"})
    assert kept["material"] == "gravel" and none is None


def test_a_bank_gets_planting_not_paving():
    """Rule 2: a slope of the terrain between two levels (1:2.5, 1.2 m) is found as a bank and planted: a gravel bed
    with ground cover, grasses and accent shrubs, its bed cut from the lawn; the review finds the bare bank before and
    nothing after; a path down the bank keeps its walk free."""
    path = _path("path_front", _rect(4.4, -9.0, 5.6, 0.0))
    site = _site(GENTLE, areas=[path])
    found, _n = LS.review(site)
    assert any(f["metrics"]["rule"] == "G16" and "bare terrain" in f["message"] for f in found)
    rec = LS.plan(site)
    assert rec["banks"] and all(b["finish"] == "planted" for b in rec["banks"])
    bank = max(rec["banks"], key=lambda b: b["area_m2"])
    assert bank["rise_m"] >= 1.0 and 0.3 < bank["slope_p75"] <= 0.5 + 1e-6
    bed = next(b for b in rec["beds"] if b["id"] == bank["id"])
    assert bed["kind"] == "planted" and bed["plants"] >= 5
    plants = [t for t in site["trees"] if t.get("source") == LS.SOURCE and t["parent"] == bank["id"]]
    assert {p["role"] for p in plants} >= {"groundcover", "grass", "accent"}
    assert all(_in(p["center"], bed["rects"]) for p in plants)
    assert not [p for p in site["trees"] if _in(p["center"], [path["polygon"]])]        # nothing in the walk
    assert all(t["species"] in ("succulent_shrub", "ornamental_grass", "oleander", "privet_shrub") for t in plants)
    assert LS.ground_holes(site)                                                        # the bed replaces the lawn
    found, _n = LS.review(site)
    assert not [f for f in found if f["severity"] == "major"], found


def test_a_steep_bank_becomes_terraced_planting_steps():
    """Rule 2: a bank steeper than the planted slope (1.6 m over 1.2 m) becomes planting steps: fill terraces of low
    edging walls (at most 0.6 m each, a coping on the level ones), each step a planted bed at its level."""
    site = _site(STEEP)
    rec = LS.plan(site)
    bank = max(rec["banks"], key=lambda b: b["area_m2"])
    assert bank["finish"] == "terraced" and bank["tiers"] >= 2
    lo, hi = LS.LANDSCAPE["terrace_wall_m"]
    assert bank["step_m"] <= hi + 1e-6
    bed = next(b for b in rec["beds"] if b["id"] == bank["id"])
    fronts = [w for w in bed["walls"] if w["kind"] == "front"]
    assert fronts and all(w["coping"] and w["top0"] - w["bottom"] <= hi + LS.LANDSCAPE["below_m"] + 1e-6
                          for w in fronts)
    levels = sorted(t["level"] for t in bed["tiers"])
    assert levels == sorted(set(levels)) and levels[-1] == pytest.approx(bank["z_range"][1], abs=1e-3)
    plants = [t for t in site["trees"] if t.get("source") == LS.SOURCE and str(t["parent"]).startswith(bank["id"])]
    assert plants and all(isinstance(p["z"], float) for p in plants)
    tops = {round(lv - LS.LANDSCAPE["bed_drop_m"], 4) for lv in levels}
    assert {round(p["z"], 4) for p in plants} <= tops                              # each plant on its step's bed
    meshes = LS.terraced_meshes(bed)
    assert meshes["beds"] and meshes["walls"] and meshes["coping"]
    assert not [f for f in LS.review(site)[0] if f["severity"] == "major"]


def test_paved_areas_get_a_border_band_and_beds_a_lawn_edge():
    """Rule 3: a paved area on the lawn gets a contrasting border band along every edge that meets the lawn (none
    against the house); a light paving a dark granite course, a dark one a light stone; every bed a steel edge where it
    meets the lawn."""
    terrace = {"id": "paving_1", "kind": "paving", "polygon": _rect(10.0, 2.0, 13.0, 6.0), "z": None,
               "material": "paving_stone"}
    site = _site([(14.0, 0.0), (-9.0, 0.0)], areas=[terrace])
    rec = LS.plan(site)
    border = next(b for b in rec["borders"] if b["area"] == "paving_1")
    assert border["slug"] == "slate_floor"                                        # light paving, dark course
    assert LS.border_look("slate_floor") == "paving_stone"                         # dark paving, light course
    xs = {round(p0[0], 3) for p0, p1, _n in border["pieces"] if abs(p0[0] - p1[0]) < 1e-6}
    assert 13.0 in xs and 10.0 not in xs                                           # the side on the house has none
    beds = {b["id"]: b for b in rec["beds"]}
    edged = {e["bed"] for e in rec["edges"]}
    assert beds and set(beds) - {b for b, v in beds.items() if v["kind"] == "terraced"} <= edged
    pieces = LS.strip_pieces(border["pieces"], lambda x, y: 0.0, 0.12, 0.006, 0.05, inward=True)
    assert len(pieces) == len(border["pieces"])


def test_planters_stand_by_an_entrance_and_lights_along_a_path():
    """Rule 4: a pair of large planters beside an entrance's landing (against the facade, out of the door's approach and
    the path), low garden lights every few metres beside a path (never on it); the plan is deterministic."""
    door = {"id": "d1", "point": [5.0, -0.4], "z": 0.0, "main": True}
    landing = {"opening_id": "d1", "step_up": {"riser": 0.15}, "blocks": [{"polygon": _rect(4.3, -1.2, 5.7, 0.0),
                                                                           "z_top": -0.15}]}
    path = _path("path_d1", _rect(4.4, -9.0, 5.6, -1.2))
    upper = {"id": "d2", "point": [8.0, -0.4], "z": 3.0, "main": False}           # a door of the upper floor
    site = _site([(14.0, 0.0), (-9.0, 0.0)], areas=[path], doors=[door, upper], steps=[landing])
    rec = LS.plan(site)
    pots = [p for p in rec["planters"] if p["door"] == "d1"]
    assert len(pots) == 2 and not [p for p in rec["planters"] if p["door"] == "d2"]
    zone = LS.door_zones(site)[0]
    for p in pots:
        assert not _in(p["center"], [zone, path["polygon"], landing["blocks"][0]["polygon"]])
        assert -1.2 < p["center"][1] < 0.0                                         # against the facade
    potted = [t for t in site["trees"] if t.get("role") == "potted"]
    assert len(potted) == 2 and all(t["z"] > 0.4 for t in potted)                   # on the planter's soil
    lights = [lt for lt in rec["lights"] if lt["along"] == "path_d1"]
    assert len(lights) >= 2 and all(not _in(lt["center"], [path["polygon"]]) for lt in lights)
    assert all(abs(abs(lt["center"][0] - 5.0) - (0.6 + GR.GRADE["edging_t"] + 0.35)) < 1e-6 for lt in lights)
    again = copy.deepcopy(_site([(14.0, 0.0), (-9.0, 0.0)], areas=[path], doors=[door, upper], steps=[landing]))
    rec2 = LS.plan(again)
    assert json.dumps(rec2, sort_keys=True, default=str) == json.dumps(rec, sort_keys=True, default=str)
    LS.plan(site)                                                                   # a second plan replaces the first
    assert sum(1 for t in site["trees"] if t.get("role") == "potted") == 2


def test_nothing_of_the_landscape_stands_in_a_walkway():
    """G16 (and G14 for the plants): no plant, planter, light or boulder in a path, a landing, a door's approach or a
    pool's walkway; a planter put on the path is found."""
    door = {"id": "d1", "point": [5.0, -0.4], "z": 0.0, "main": True}
    path = _path("path_d1", _rect(4.4, -9.0, 5.6, 0.0))
    site = _site(GENTLE, areas=[path], doors=[door])
    LS.plan(site)
    found, n = LS.review(site)
    assert n > 0 and not [f for f in found if "walkway" in f["message"]]
    from wenart.blender import site_sense as SS
    assert not [f for f in SS.walkways(site) if "stands in the walk" in f["message"]]
    site["landscape"]["planters"].append({"id": "bad", "center": [5.0, -4.0], "z": 0.0})
    found, _n = LS.review(site)
    assert any(f["target"] == "bad" and f["severity"] == "major" and f["metrics"]["rule"] == "G16" for f in found)


def test_a_large_lawn_gets_a_feature_tree_and_boulders():
    """Rule 4: a large free lawn (no tree in it) gets one tree of the climate's small class in its most open spot, with a
    few boulders at its foot; boulders are generated rock meshes."""
    site = _site([(14.0, 0.0), (-9.0, 0.0)])
    site["plot"] = _rect(-6.0, -20.0, 16.0, 14.0)
    rec = LS.plan(site)
    tree = next(t for t in site["trees"] if t.get("role") == "feature")
    assert rec.get("feature_tree") == tree["id"] and tree["kind"] == "tree" and tree["center"][1] < -4.0
    assert S.tree_parts(tree, site["terrain"], "mediterranean")["species"] == "olive"
    lawn = [b for b in rec["boulders"] if b["parent"] == "lawn"]
    assert lawn
    v, f = LS.boulder_mesh(lawn[0])
    assert len(v) > 50 and len(f) > 50 and min(p[2] for p in v) < lawn[0]["z"] < max(p[2] for p in v)


def test_plants_stand_on_their_bed_or_planter():
    """``site.tree_parts`` honours a plant's own ``z`` (a planting step, a planter's soil) and ``height_m``, and keeps
    the inferred flag of a planted species."""
    terrain = _terrain(GENTLE)
    item = {"id": "p", "kind": "plant", "center": [3.0, -2.0], "size": [0.5, 0.5], "z": 0.62, "height_m": 0.6,
            "species": "ornamental_grass", "species_inferred": True}
    parts = S.tree_parts(item, terrain)
    assert parts["ground_z"] == pytest.approx(0.62) and parts["height"] == pytest.approx(0.6)
    assert parts["species_inferred"] is True
    from wenart.blender import vegetation as VG
    assert VG.species_record("ornamental_grass")["source"]["polyhaven"] == "grass_medium_02"
    assert VG.library_plant("ornamental_grass") is None                       # its own scan, never a library bush


def test_the_landscape_finishes_are_fetched_and_verified():
    """The landscape's looks are vocabulary slugs the assets stage fetches (exterior.build_finish_slugs); the boulder's
    Poly Haven set was checked on the API (asset_checks_m10.json)."""
    from wenart.blender import exterior as E
    from wenart.style.vocabulary import MATERIALS
    slugs = {s for s, _part in E.build_finish_slugs({"family": "modern"})}
    assert set(LS.LOOKS.values()) <= slugs
    assert all(s in MATERIALS for s in LS.LOOKS.values())
    checks = json.loads((ROOT / "wenart" / "style" / "asset_checks_m10.json").read_text(encoding="utf-8"))
    rec = checks["textures"]["polyhaven:rock_boulder_dry"]
    assert rec["exists"] and rec["has_required_maps"] and MATERIALS["rock_boulder"]["flat"] == rec["measured_flat_linear"]


def test_real04_front_bank_is_planted_and_the_ground_soft():
    """real04 (latest baseline, run 20261031-194116-full): the bank between the glazed lower front and the street hedge
    (the house's lower floor at -3.0 m, the pavement at -4.6 m) is found and built as terraced planting steps with
    plants, the drawn oleanders on it stand on a step; the run's agent override (ground paving_stone) is refused and the
    garden stays lawn; G16 finds the paved ground of the run's manifest and nothing major on the new plan; the walk (G15)
    and the walkways (G14) gain no finding."""
    if not BASE.is_file():
        pytest.skip("the latest real04 baseline is not in this checkout")
    from wenart.blender import build as B
    from wenart.blender import site_sense as SS

    building = json.loads(BASE.read_text(encoding="utf-8"))
    assert O.materials_of(building).get("ground") == "paving_stone"
    assert not XC.validate_material_override({}, {"ground": O.materials_of(building)["ground"]})["ok"]
    looks, applied = O.apply_looks({"garden": {"material": "grass", "source": "fallback"}}, O.materials_of(building))
    assert looks["garden"]["material"] == "grass" and any(a.get("refused") for a in applied)
    prep = B.prepare(building)
    site = prep["site"]
    ls = site["landscape"]
    assert not ls.get("error")
    front = [b for b in ls["banks"] if b["finish"] == "terraced" and b["area_m2"] >= 8.0]
    assert front, ls["banks"]
    bank = max(front, key=lambda b: b["area_m2"])
    fr = bank["frame"]
    c = bank["cell_m"]
    ys = [fr["o"][1] + fr["u"][1] * (i + 0.5) * c + fr["v"][1] * (j + 0.5) * c for i, j in bank["cells"]]
    assert -3.2 < min(ys) and max(ys) < -1.0                     # between the facade (y 0) and the street hedge
    assert bank["plants"] >= 10 and bank["walls"] >= 4 and bank["rise_m"] > 1.2
    assert any(t.get("id") == "sd_L0_007" and (t.get("stand") or {}).get("by") == LS.SOURCE for t in site["trees"])
    assert ls["counts"]["planters"] >= 2 and ls["counts"]["lights"] >= 2 and ls["counts"]["plants"] >= 40
    found, _n = LS.review(site)
    assert not [f for f in found if f["severity"] == "major"], found
    if MANIFEST.is_file():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        old, _n = LS.review(site, manifest)
        assert any(f["target"] == "ground" and "paved" in f["message"] for f in old)
    walk = [f for f in SS.review(site)[0] if f["metrics"]["rule"] in ("G14", "G15") and f["severity"] == "major"]
    assert not walk, walk
