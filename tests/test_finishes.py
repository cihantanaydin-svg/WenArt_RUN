"""Milestone 10 finishes (wenart/style/finishes.py, docs/milestone10.md §4.3, §4.8, §4.9; track C).

Shapes of the entries, the coverage table (§4.11), the keyword tables, the nine lighting moods and, above all, the
asset check record ``wenart/style/asset_checks_m10.json``: every texture id of the vocabulary was verified against the
live Poly Haven / ambientCG APIs on 2026-10-08 and the record is kept equal to the tables.
"""
import json
import re
from pathlib import Path

import pytest

from wenart.assets import fetch
from wenart.style import colours as C
from wenart.style import finishes as F
from wenart.style import vocabulary as V

ROOT = Path(__file__).resolve().parents[1]
CHECKS = json.loads((ROOT / "wenart" / "style" / "asset_checks_m10.json").read_text(encoding="utf-8"))
PROCEDURAL_GROUPS = {"wenart_tiles", "wenart_wallpaper", "wenart_slats", "wenart_standing_seam", None}

# The vocabulary of Milestone 3-9: slugs, assets and moods that Milestone 10 must not move.
LEGACY_ASSETS = {"wood_oak_light": "WoodFloor051", "wood_walnut": "WoodFloor046", "wood_parquet": "herringbone_parquet",
                 "concrete_polished": "Concrete046", "terracotta": "patio_tiles", "marble": "marble_01",
                 "carpet": "Carpet016", "plaster_white": "white_plaster_02", "plaster_cream": "beige_wall_001",
                 "plaster_charcoal": "white_plaster_02", "plaster_exterior": "grey_plaster", "brick": "red_brick_03",
                 "wood_panel": "wooden_panels", "painted_wood_white": "white_planks_clean", "painted_metal_white": "Metal032"}
LEGACY_LIGHTING = {
    "warm daylight": ("kloppenheim_06", 35, 210, 3.0, 5200, 1.0),
    "cool daylight": ("kloofendal_43d_clear_puresky", 55, 180, 4.0, 6500, 1.0),
    "golden evening": ("venice_sunset", 12, 255, 2.0, 3200, 1.2),
    "overcast": ("overcast_soil_puresky", 45, 180, 0.3, 6900, 1.5),
    "night": ("dikhololo_night", -10, 0, 0.0, 3800, 0.6),
}


def textured(table):
    return {slug: e for slug, e in table.items() if e.get("asset")}


# --------------------------------------------------------------------------
# Entry shapes
# --------------------------------------------------------------------------

@pytest.mark.parametrize("table_name", ["MATERIALS", "FURNITURE_MATERIALS"])
def test_entries_follow_the_documented_shapes(table_name):
    table = getattr(F, table_name)
    assert table
    for slug, e in table.items():
        assert re.fullmatch(r"[a-z][a-z0-9_]*", slug), slug
        assert "colour" not in slug.split("_"), f"{slug}: a slug never carries a colour"   # amendment 1, row 14
        assert e["kind"] in F.KINDS, slug
        assert len(e["flat"]) == 3 and all(0.0 <= v <= 1.0 for v in e["flat"]), slug
        assert 0.0 <= e["roughness"] <= 1.0, slug
        assert e.get("flat_source") and e["flat_source"].split(":")[0] in ("measured", "colour", "colour table", "estimated"), slug
        if e["flat_source"].startswith("estimated"):                                        # only an unmeasured ambientCG photo
            assert e["source"] == "ambientcg" and e["albedo_mode"] == "texture", slug
        if e["flat_source"] == "measured":
            assert e["source"] == "polyhaven", slug                                       # only these could be downloaded
        if e.get("source") == "procedural":
            assert e["asset"] is None and e["albedo_mode"] == "flat" and e["detail"] == 0.0, slug
            assert e["procedural"] in PROCEDURAL_GROUPS, slug
        elif e.get("asset"):
            assert e["source"] in ("polyhaven", "ambientcg"), slug                         # CC0 sources only
            assert e["albedo_mode"] in V.ALBEDO_MODES, slug
            assert ("detail" in e) == (e["albedo_mode"] == "flat"), slug
            assert not re.search(r"\s", e["asset"]), slug
            if "size_m" in e:
                assert len(e["size_m"]) == 2 and all(v > 0 for v in e["size_m"]), slug
        else:
            assert table_name == "FURNITURE_MATERIALS" and e["kind"] == "metal", slug     # flat handle metals
    for slug, e in table.items():
        if e.get("metallic"):
            assert 0.0 < e["metallic"] <= 1.0 and V.METALLIC[slug] == e["metallic"]


def test_the_vocabulary_merges_the_tables_and_keeps_the_old_slugs():
    for slug, asset in LEGACY_ASSETS.items():
        assert V.MATERIALS[slug]["asset"] == asset
    assert set(F.MATERIALS) <= set(V.MATERIALS) and set(F.FURNITURE_MATERIALS) <= set(V.FURNITURE_MATERIALS)
    assert not (set(F.MATERIALS) & set(LEGACY_ASSETS)), "Milestone 10 adds slugs, it never replaces one"
    # "Light tiles" are procedural light ceramic tiles: the old asset Tiles074 is a black and beige marble checkerboard
    # (real02: every bathroom and kitchen had full-height checkerboard walls).
    e = V.MATERIALS["tiles_light"]
    assert e["source"] == "procedural" and e["asset"] is None and e["procedural"] == "wenart_tiles"
    assert e["params"] == V.LIGHT_TILE_PARAMS and e["params"]["pattern"] == "grid" and e["wet_safe"]
    assert min(e["flat"]) >= 0.75 and V.asset_for("tiles_light") == ("procedural", None)
    assert not (set(F.FURNITURE_MATERIALS) & {"fabric_linen", "wood_veneer_oak", "wood_veneer_walnut", "steel_brushed",
                                              "stone_worktop", "ceramic_white", "lacquer_dark", "mirror", "plant_green"})
    assert V.asset_for("paint") == ("polyhaven", "plastered_wall")
    # procedural entries have no asset id: the vocabulary's asset_for returns (source, None) for them and the fetcher skips them
    assert V.asset_for("tiles_subway") == ("procedural", None)
    assert all(row["asset"] for row in fetch.texture_rows())
    assert {(r["source"], r["asset"]) for r in fetch.texture_rows()} >= {("polyhaven", "oak_wood_planks"), ("ambientcg", "Cork002")}


def test_no_slug_name_is_used_twice_across_the_tables():
    assert not (set(V.MATERIALS) & set(V.FURNITURE_MATERIALS))
    assert "slate" in F.MATERIALS and F.MATERIALS["slate"]["kind"] == "roof"
    assert F.MATERIALS["slate_floor"]["kind"] == "hard"                                    # the floor slate has its own slug


# --------------------------------------------------------------------------
# The coverage table (docs/milestone10.md §4.11)
# --------------------------------------------------------------------------

def floors():
    return {slug for _, slug in V.FLOOR_WORDS}


def test_coverage_floors_wall_finishes_wet_walls():
    assert len(floors()) >= 25
    for slug in floors():
        assert V.MATERIALS[slug]["kind"] in ("wood", "hard", "soft"), slug
    walls = {slug for _, slug in V.WALL_WORDS}
    assert len(walls) >= 14 and {"paint", "lime_plaster", "microcement", "venetian_plaster", "wood_slat", "concrete_exposed"} <= walls
    wallpapers = {s for s in V.MATERIALS if s.startswith("wallpaper_")}
    assert wallpapers == {"wallpaper_stripe", "wallpaper_botanical", "wallpaper_geometric", "wallpaper_check",
                          "wallpaper_herringbone", "wallpaper_grasscloth"}
    assert {s for s in V.MATERIALS if s.startswith("stone_wall_")} >= {"stone_wall_ledgestone", "stone_wall_rubble"}
    assert {"brick_red", "brick_white", "brick_grey", "brick_reclaimed"} <= set(V.MATERIALS)
    # wet walls: six kinds, with tile size, pattern and grout colour
    wet = {"tiles_subway", "tiles_large_porcelain", "tiles_zellige", "tiles_hexagon", "tiles_mosaic", "marble_slab"}
    assert wet <= set(V.MATERIALS)
    assert F.TILE_PATTERNS["tiles_subway"]["tile_size_m"] == [0.15, 0.075]                # 7.5 x 15 cm
    assert F.TILE_PATTERNS["tiles_large_porcelain"]["tile_size_m"] == [0.6, 1.2]
    assert F.TILE_PATTERNS["tiles_zellige"]["tile_size_m"] == [0.1, 0.1] and F.TILE_PATTERNS["tiles_zellige"]["variation"] >= 0.1
    assert F.TILE_PATTERNS["tiles_mosaic"]["tile_size_m"] == [0.025, 0.025]
    for slug, p in F.TILE_PATTERNS.items():
        assert V.MATERIALS[slug]["procedural"] == "wenart_tiles" and V.MATERIALS[slug]["params"]["pattern"] == p["pattern"]
        assert C.known(p["grout_colour"]) and C.known(F.TILE_DEFAULT_COLOUR[slug])
    assert V.MATERIALS["marble_slab"]["asset"]


def test_coverage_cabinets_doors_frames_exterior():
    assert F.CABINET_FRONT_STYLES == ("flat", "shaker", "slatted", "glass")
    assert set(F.CABINET_WORKTOPS) == {"stone", "wood", "terrazzo", "steel"} and set(F.CABINET_HANDLES) == {"brushed_steel", "black", "brass"}
    for slug in list(F.CABINET_WORKTOPS.values()) + list(F.CABINET_HANDLES.values()):
        assert slug in V.MATERIALS or slug in V.FURNITURE_MATERIALS, slug
    assert len(F.DOOR_STYLES) == 8 and set(F.DOOR_STYLES) >= {"flush", "shaker_panel", "glazed", "pocket", "sliding", "barn", "double", "entrance"}
    assert set(F.WINDOW_FRAME_MATERIALS) == {"pvc_white", "aluminium_anthracite", "steel_black", "dark_bronze", "oak", "painted_metal_white"}
    for slug in F.WINDOW_FRAME_MATERIALS:
        assert slug in V.MATERIALS
    exterior = {m for mats in F.EXTERIOR_MATERIALS.values() for m in mats}
    assert len(exterior) >= 13
    assert {"render", "brick_red", "stone_cladding", "wood_cladding", "fibre_cement", "clay_tiles", "concrete_tiles", "slate",
            "standing_seam", "green_roof", "paving", "gravel", "grass", "decking"} <= set(V.MATERIALS)
    for slot, mats in F.EXTERIOR_MATERIALS.items():
        assert slot in F.EXTERIOR_SLOTS
        for slug in mats:
            assert slug in V.MATERIALS or slug in V.FURNITURE_MATERIALS, (slot, slug)
    for slug in F.FURNITURE_WOODS:
        assert slug in V.FURNITURE_MATERIALS and V.FURNITURE_MATERIALS[slug]["kind"] == "wood"
    assert V.MATERIALS["standing_seam"]["procedural"] == "wenart_standing_seam" and V.MATERIALS["standing_seam"]["metallic"] > 0
    for frame, colour in F.FRAME_COLOUR_MATERIALS.items():
        assert C.known(frame) and colour in F.WINDOW_FRAME_MATERIALS


def test_wet_safe_floors_are_the_hard_ones():
    safe = set(F.wet_safe_floors())
    assert {"terrazzo", "travertine", "limestone", "slate_floor", "vinyl", "tiles_large_porcelain", "tiles_cement",
            "tiles_hexagon"} <= safe
    assert not (safe & {s for s, e in V.MATERIALS.items() if e["kind"] in ("wood", "soft")})
    assert set(V.WET_SAFE_FLOORS) == {"tiles_light", "marble", "terracotta", "concrete_polished"}      # the vocabulary's list is unchanged


# --------------------------------------------------------------------------
# Keyword tables
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name, slugs", [("FLOOR_WORDS", lambda: set(V.MATERIALS)), ("WALL_WORDS", lambda: set(V.MATERIALS)),
                                          ("LIGHT_WORDS", lambda: set(V.LIGHTING))])
def test_keyword_tables(name, slugs):
    table = getattr(F, name)
    valid = slugs()
    seen: dict[str, str] = {}
    for keyword, slug in table:
        assert slug in valid, (keyword, slug)
        assert keyword == keyword.lower().strip() and keyword, keyword
        assert seen.setdefault(keyword, slug) == slug, f"{keyword!r} gives two slugs"
    assert list(getattr(V, name))[:len(table)] == list(table), "the vocabulary prepends the tables of finishes.py"


def test_new_words_do_not_steal_old_ones():
    old_floor = dict(V.FLOOR_WORDS[len(F.FLOOR_WORDS):])
    assert old_floor["oak"] == "wood_oak_light" and old_floor["herringbone"] == "wood_parquet" and old_floor["carpet"] == "carpet"
    old_wall = dict(V.WALL_WORDS[len(F.WALL_WORDS):])
    assert old_wall["brick"] == "brick" and old_wall["white"] == "plaster_white" and old_wall["wood panelling"] == "wood_panel"
    for keyword in dict(F.FLOOR_WORDS):
        assert keyword not in old_floor or old_floor[keyword] == dict(F.FLOOR_WORDS)[keyword], keyword


# --------------------------------------------------------------------------
# Lighting
# --------------------------------------------------------------------------

def test_nine_moods_with_their_strengths_white_balance_and_lamps():
    assert list(V.LIGHTING) == ["warm daylight", "cool daylight", "golden evening", "overcast", "night", "bright noon",
                                "blue hour", "cloudy soft", "interior evening"]
    assert set(F.LIGHTING) == set(V.LIGHTING)
    for mood, e in V.LIGHTING.items():
        assert {"hdri", "sun_elevation_deg", "sun_azimuth_deg", "sun_strength", "colour_temperature_k", "hdri_strength",
                "wb_residual", "lamps_on"} <= set(e), mood
        assert 0.0 <= e["wb_residual"] <= 1.0 and e["hdri_strength"] > 0 and isinstance(e["lamps_on"], bool)
    for mood, values in LEGACY_LIGHTING.items():
        e = V.LIGHTING[mood]
        assert (e["hdri"], e["sun_elevation_deg"], e["sun_azimuth_deg"], e["sun_strength"], e["colour_temperature_k"],
                e["hdri_strength"]) == values, f"{mood}: Milestone 3 values must not move"
    from wenart.blender import render as R

    for mood in LEGACY_LIGHTING:                                                           # the white-balance residuals agree with render.py
        assert V.LIGHTING[mood]["wb_residual"] == R.WB_RESIDUAL[mood], mood
    assert [m for m, e in V.LIGHTING.items() if e["lamps_on"]] == ["interior evening"]
    assert len({e["hdri"] for e in V.LIGHTING.values()}) == 9 and set(V.HDRIS) == {e["hdri"] for e in V.LIGHTING.values()}
    assert V.LIGHTING["bright noon"]["hdri"] == "qwantani_noon_puresky" and V.LIGHTING["interior evening"]["hdri"] == "sunset_jhbcentral"


def test_every_lighting_mood_has_the_values_the_render_reads_in_sane_ranges():
    """Lead item (track E, finding #37): one loop over every mood of the vocabulary. The Blender code reads
    ``sun_strength`` (lighting.py, W/m2), ``sun_elevation_deg`` / ``sun_azimuth_deg``, ``hdri_strength`` (world strength of the
    four new moods) and ``wb_residual``; ``lamps_on`` decides whether the lamps emit. The profile's lamps claim follows
    ``finishes.LIGHTING``."""
    from wenart.blender import materials as M
    from wenart.style import profile as P

    assert list(V.LIGHTING) == list(F.LIGHTING) and len(V.LIGHTING) == 9
    for mood, e in V.LIGHTING.items():
        for key in ("hdri", "sun_elevation_deg", "sun_azimuth_deg", "sun_strength", "colour_temperature_k", "hdri_strength",
                    "wb_residual", "lamps_on"):
            assert key in e and e[key] is not None, (mood, key)
        assert isinstance(e["lamps_on"], bool) and isinstance(e["hdri"], str) and e["hdri"] in V.HDRIS, mood
        assert 0.0 <= e["sun_strength"] <= 10.0, mood                         # W/m2 of the sun lamp
        assert 0.0 < e["hdri_strength"] <= 3.0, mood
        assert 0.0 <= e["wb_residual"] <= 1.0, mood
        assert -90 <= e["sun_elevation_deg"] <= 90 and 0 <= e["sun_azimuth_deg"] <= 360, mood
        assert 1500 <= e["colour_temperature_k"] <= 12000, mood
        assert e == F.LIGHTING[mood], f"{mood}: the vocabulary and finishes.LIGHTING must agree"      # lamps_on included
        # a mood with no sun is lit by the sky or by the lamps: it says so in the profile, matching the table
        profile = P.profile_from_text(mood)
        assert profile["lighting"]["mood"] == mood and profile["lighting"]["sun_strength"] == e["sun_strength"], mood
        claims = [w for w in profile["warnings"] if w.startswith(f"{mood} mood:")]
        if F.LIGHTING[mood]["lamps_on"]:
            assert len(claims) == 1 and "the lamps are on" in claims[0], (mood, claims)
        else:
            assert not any("lamps are on" in w for w in claims), (mood, claims)
            assert bool(claims) == (e["sun_strength"] == 0), (mood, claims)   # night and blue hour: "lamps are off"
    for mood in set(V.LIGHTING) - set(M.MOOD_STRENGTH):                       # the moods whose world strength is the table's
        assert M._MOOD_HDRI_STRENGTH[mood] == V.LIGHTING[mood]["hdri_strength"], mood
    assert [m for m, e in F.LIGHTING.items() if e["lamps_on"]] == ["interior evening"]


# --------------------------------------------------------------------------
# The asset check record
# --------------------------------------------------------------------------

def test_the_check_record_covers_every_texture_and_hdri_without_problems():
    assert CHECKS["schema"] == fetch.CHECKS_SCHEMA and CHECKS["problems"] == []
    assert re.fullmatch(r"2026-10-\d\d", CHECKS["checked"])
    rows = fetch.texture_rows()
    assert {f"{r['source']}:{r['asset']}" for r in rows} == set(CHECKS["textures"]), "regenerate: python -m wenart.assets.fetch check --measure"
    for r in rows:
        rec = CHECKS["textures"][f"{r['source']}:{r['asset']}"]
        assert rec["exists"] is True and rec["licence"] == "CC0" and rec["has_required_maps"] and rec["jpg_1k_2k"], r
        if r["source"] == "polyhaven":
            assert rec["api_type"] == fetch.PH_TEXTURE_TYPE, r                              # a texture, not an HDRI or a model
        assert sorted(rec["slugs"]) == sorted(r["slugs"]), r
    assert set(CHECKS["hdris"]) == set(V.HDRIS)
    for hdri_id, rec in CHECKS["hdris"].items():
        assert rec["exists"] and rec["hdr_1k_2k"] and rec["licence"] == "CC0", hdri_id
        assert rec["moods"] == [V.HDRIS[hdri_id]["mood"]]


def test_table_sizes_and_flat_colours_equal_the_checked_values():
    for table in (V.MATERIALS, V.FURNITURE_MATERIALS):
        for slug, e in textured(table).items():
            rec = CHECKS["textures"][f"{e['source']}:{e['asset']}"]
            if e.get("size_m"):
                assert rec["size_m"] == pytest.approx(e["size_m"], abs=1e-4), slug         # the API's real-world size
            if e["source"] == "polyhaven":
                assert rec["size_m"], f"{slug}: Poly Haven gave no size"
            if e.get("flat_source") == "measured":
                assert e["flat"] == pytest.approx(rec["measured_flat_linear"], abs=0.0015), slug
    # an ambientCG entry the API gives no size for is not given one here (the fetcher assumes 1 m and flags it)
    for slug in ("cork", "marble_slab"):
        assert "size_m" not in V.MATERIALS[slug] and CHECKS["textures"][f"ambientcg:{V.MATERIALS[slug]['asset']}"]["size_m"] is None


def test_the_flat_colour_of_a_colour_derived_entry_is_that_colour():
    for slug, e in F.MATERIALS.items():
        src = e["flat_source"]
        if src.startswith(("colour:", "estimated:")):
            assert e["flat"] == pytest.approx(list(C.linear_rgb(src.split(":", 1)[1])), abs=1e-3), slug


def test_every_asset_source_is_cc0():
    for e in list(F.MATERIALS.values()) + list(F.FURNITURE_MATERIALS.values()):
        if e.get("asset"):
            assert e["source"] in fetch.LICENCES and fetch.LICENCES[e["source"]] == "CC0"


def test_a_fake_check_run_finds_a_missing_id_and_a_changed_size(monkeypatch):
    """check_assets with fake API answers: a 404, a missing map and a size that differs from the vocabulary are problems."""
    from wenart.assets import ambientcg, polyhaven, web

    files = {"Diffuse": {"1k": {"jpg": {}}, "2k": {"jpg": {}}}, "nor_gl": {"1k": {"jpg": {}}, "2k": {"jpg": {}}},
             "Rough": {"1k": {"jpg": {}}, "2k": {"jpg": {}}}}
    infos = {"good": {"dimensions": [2000, 2000], "name": "Good", "type": 1, "categories": []},
             "small": {"dimensions": [1000, 1000], "name": "Small", "type": 1, "categories": []}}

    def fake_info(asset_id):
        if asset_id == "gone":
            raise web.HTTPStatusError("u", 404)
        return infos[asset_id]

    def fake_files(asset_id):
        if asset_id == "gone":
            raise web.HTTPStatusError("u", 404)
        return {k: v for k, v in files.items() if not (asset_id == "small" and k == "Rough")}

    monkeypatch.setattr(polyhaven, "info", fake_info)
    monkeypatch.setattr(polyhaven, "files", fake_files)
    monkeypatch.setattr(ambientcg, "infos", lambda ids: {})
    monkeypatch.setattr(V, "HDRIS", {})
    rows = [{"source": "polyhaven", "asset": a, "slugs": [a], "size_m": [2.0, 2.0]} for a in ("good", "gone", "small")]
    checks = fetch.check_assets(rows, log=lambda *_: None)
    problems = " | ".join(checks["problems"])
    assert "polyhaven:gone: not found" in problems and "polyhaven:small: missing map" in problems
    assert "polyhaven:good" not in problems and len(checks["problems"]) == 2
    infos["good"] = dict(infos["good"], type=2)                                           # a model id is no texture
    checks = fetch.check_assets(rows[:1], log=lambda *_: None)
    assert checks["problems"] and "not a texture" in checks["problems"][0]
