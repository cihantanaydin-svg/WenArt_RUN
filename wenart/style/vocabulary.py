"""Keyword tables for the rule-based style profile (Milestone 3 section 1).

What: brief words -> material slugs, material slugs -> CC0 asset ids and flat
fallback colours, light words -> HDRI id and sun settings, style families ->
their usual floor / wall / light. Everything is a plain table so a reviewer
can read and change it without touching the matching code in ``profile.py``.

Why tables and not AI: the style profile must be deterministic and
reproducible; unknown words are reported, never guessed (CLAUDE.md).

Asset ids were checked against the live APIs on 2026-10-01:
- Poly Haven: ``https://api.polyhaven.com/assets?type=textures`` and
  ``?type=hdris`` list every id; ``/files/{id}`` has ``Diffuse``, ``nor_gl``,
  ``Rough`` and ``Displacement`` maps for every texture id below; the
  ``dimensions`` field of ``/info/{id}`` is in millimetres.
- ambientCG: ``https://ambientcg.com/api/v2/full_json?id=A,B`` returns the
  ids under ``foundAssets``; ``dimensionX`` / ``dimensionY`` are centimetres
  (``WoodFloor051`` = 180 = 1.8 m); every id below offers ``1K-JPG``, ``2K-JPG``
  and ``4K-JPG`` zip downloads with Color, NormalGL, Roughness, Displacement.
Both sites publish all assets under CC0 1.0 (polyhaven.com/license,
ambientcg.com: "All assets ... CC0").
"""
from __future__ import annotations

# --------------------------------------------------------------------------
# Material slugs -> asset + flat colour
# --------------------------------------------------------------------------

# "flat" is linear RGB in 0..1 and "roughness" the Principled BSDF roughness,
# used when the texture is not available (offline, blocked domain,
# --no-textures); wenart.blender.materials derives its tables from here.
# "kind" groups slugs for the derived slots (a wood floor gives wood doors;
# hard floors stay in wet rooms).
MATERIALS: dict[str, dict] = {
    "wood_oak_light":     {"source": "ambientcg", "asset": "WoodFloor051",       "kind": "wood",    "flat": [0.62, 0.47, 0.30], "roughness": 0.45},
    "wood_walnut":        {"source": "ambientcg", "asset": "WoodFloor046",       "kind": "wood",    "flat": [0.25, 0.14, 0.08], "roughness": 0.4},
    "wood_parquet":       {"source": "polyhaven", "asset": "herringbone_parquet", "kind": "wood",   "flat": [0.45, 0.30, 0.17], "roughness": 0.4},
    "concrete_polished":  {"source": "ambientcg", "asset": "Concrete046",        "kind": "hard",    "flat": [0.45, 0.45, 0.44], "roughness": 0.25},
    "terracotta":         {"source": "polyhaven", "asset": "patio_tiles",        "kind": "hard",    "flat": [0.55, 0.27, 0.16], "roughness": 0.7},
    "marble":             {"source": "polyhaven", "asset": "marble_01",          "kind": "hard",    "flat": [0.80, 0.78, 0.74], "roughness": 0.15},
    "tiles_light":        {"source": "ambientcg", "asset": "Tiles074",           "kind": "hard",    "flat": [0.82, 0.82, 0.80], "roughness": 0.2},
    "carpet":             {"source": "ambientcg", "asset": "Carpet016",          "kind": "soft",    "flat": [0.60, 0.55, 0.45], "roughness": 0.95},
    "plaster_white":      {"source": "polyhaven", "asset": "white_plaster_02",   "kind": "plaster", "flat": [0.85, 0.84, 0.80], "roughness": 0.85},
    "plaster_cream":      {"source": "polyhaven", "asset": "beige_wall_001",     "kind": "plaster", "flat": [0.80, 0.72, 0.55], "roughness": 0.85},
    # Charcoal = the white plaster texture with a dark tint (see WALL_TINTS).
    "plaster_charcoal":   {"source": "polyhaven", "asset": "white_plaster_02",   "kind": "plaster", "flat": [0.05, 0.05, 0.055], "roughness": 0.6},
    "plaster_exterior":   {"source": "polyhaven", "asset": "grey_plaster",       "kind": "plaster", "flat": [0.55, 0.54, 0.52], "roughness": 0.9},
    "brick":              {"source": "polyhaven", "asset": "red_brick_03",       "kind": "brick",   "flat": [0.40, 0.17, 0.12], "roughness": 0.9},
    "wood_panel":         {"source": "polyhaven", "asset": "wooden_panels",      "kind": "wood",    "flat": [0.28, 0.17, 0.09], "roughness": 0.5},
    "painted_wood_white": {"source": "polyhaven", "asset": "white_planks_clean", "kind": "painted", "flat": [0.88, 0.87, 0.84], "roughness": 0.4},
    # Metal032 is bare grey metal (ambientCG has no clean white painted metal);
    # the window-frame tint makes it white. No real-world size on the API -> 1 m.
    "painted_metal_white": {"source": "ambientcg", "asset": "Metal032",          "kind": "metal",   "flat": [0.85, 0.85, 0.85], "roughness": 0.35},
}

# Flat-colour-only slugs for the parametric furniture and decor of Milestone 4
# (wenart.blender.parametric): fabric, bedding, sanitary ceramic, appliance
# steel, worktop stone, dark lacquer and plant green. They have no texture
# asset on purpose (no download, nothing to verify against the APIs), so
# they live beside MATERIALS instead of inside it; FLAT_COLOURS / ROUGHNESS
# below cover both tables and wenart.blender.materials reads those.
FURNITURE_MATERIALS: dict[str, dict] = {
    "fabric_linen":  {"kind": "fabric",  "flat": [0.72, 0.66, 0.55], "roughness": 0.9},
    "fabric_white":  {"kind": "fabric",  "flat": [0.86, 0.85, 0.82], "roughness": 0.9},
    "ceramic_white": {"kind": "ceramic", "flat": [0.92, 0.92, 0.90], "roughness": 0.12},
    "steel_brushed": {"kind": "metal",   "flat": [0.58, 0.58, 0.58], "roughness": 0.35},
    "stone_worktop": {"kind": "hard",    "flat": [0.24, 0.24, 0.25], "roughness": 0.3},
    "lacquer_dark":  {"kind": "painted", "flat": [0.04, 0.04, 0.045], "roughness": 0.4},
    "plant_green":   {"kind": "organic", "flat": [0.10, 0.28, 0.09], "roughness": 0.8},
}
# The style slot the parametric fabric comes from; the Milestone 3 profile
# has no such slot, so this is the slug used (recorded as assumed).
DEFAULT_TEXTILE_MATERIAL = "fabric_linen"

FLAT_COLOURS: dict[str, list[float]] = {
    **{slug: entry["flat"] for slug, entry in MATERIALS.items()},
    **{slug: entry["flat"] for slug, entry in FURNITURE_MATERIALS.items()},
}
ROUGHNESS: dict[str, float] = {
    **{slug: entry["roughness"] for slug, entry in MATERIALS.items()},
    **{slug: entry["roughness"] for slug, entry in FURNITURE_MATERIALS.items()},
}

# Multiplied into the albedo of the wall material (linear RGB).
WALL_TINTS: dict[str, list[float]] = {
    "plaster_white": [0.95, 0.94, 0.90],
    "plaster_cream": [0.93, 0.87, 0.75],
    "plaster_charcoal": [0.22, 0.22, 0.23],
    "brick": [1.0, 1.0, 1.0],
    "wood_panel": [1.0, 1.0, 1.0],
}

# Slugs that stay as they are in bathrooms / kitchens; everything else
# (wood, carpet) becomes ``tiles_light`` there.
WET_SAFE_FLOORS = ("tiles_light", "marble", "terracotta", "concrete_polished")
WET_ROOM_TYPES = ("bathroom", "wc", "kitchen")

# --------------------------------------------------------------------------
# Keyword tables. Matching is whole-word, longest keyword first at the same
# position, first position wins inside a phrase (see profile._first_hit).
# --------------------------------------------------------------------------

FLOOR_WORDS: list[tuple[str, str]] = [
    ("light oak", "wood_oak_light"),
    ("oak", "wood_oak_light"),
    ("walnut", "wood_walnut"),
    ("herringbone", "wood_parquet"),
    ("parquet", "wood_parquet"),
    ("polished concrete", "concrete_polished"),
    ("concrete", "concrete_polished"),
    ("terracotta", "terracotta"),
    ("marble", "marble"),
    ("tiles", "tiles_light"),
    ("tile", "tiles_light"),
    ("carpet", "carpet"),
]

# Bare colour words (white, cream, charcoal) are wall words only when the
# phrase has no floor match; "white marble floor" must not recolour the walls.
WALL_COLOUR_WORDS = ("white", "cream", "charcoal")
WALL_WORDS: list[tuple[str, str]] = [
    ("white plaster", "plaster_white"),
    ("cream plaster", "plaster_cream"),
    ("charcoal plaster", "plaster_charcoal"),
    ("white walls", "plaster_white"),
    ("cream walls", "plaster_cream"),
    ("charcoal walls", "plaster_charcoal"),
    ("wood panelling", "wood_panel"),
    ("wood paneling", "wood_panel"),
    ("wood panels", "wood_panel"),
    ("wood panel", "wood_panel"),
    ("brick", "brick"),
    ("plaster", "plaster_white"),
    ("white", "plaster_white"),
    ("cream", "plaster_cream"),
    ("charcoal", "plaster_charcoal"),
]

LIGHT_WORDS: list[tuple[str, str]] = [
    ("warm daylight", "warm daylight"),
    ("cool daylight", "cool daylight"),
    ("golden evening", "golden evening"),
    ("golden hour", "golden evening"),
    ("evening", "golden evening"),
    ("sunset", "golden evening"),
    ("overcast", "overcast"),
    ("night", "night"),
    ("daylight", "warm daylight"),
]

# A style family fills the slots the brief does not name explicitly; the
# profile records such fills in ``warnings`` as assumed.
STYLE_FAMILIES: list[tuple[str, dict]] = [
    ("scandinavian", {"floor": "wood_oak_light", "walls": "plaster_white", "light": "warm daylight"}),
    ("japandi", {"floor": "wood_oak_light", "walls": "plaster_cream", "light": "warm daylight"}),
    ("modern minimal", {"floor": "concrete_polished", "walls": "plaster_white", "light": "cool daylight"}),
    ("minimal", {"floor": "concrete_polished", "walls": "plaster_white", "light": "cool daylight"}),
    ("modern", {"floor": "wood_oak_light", "walls": "plaster_white", "light": "cool daylight"}),
    ("industrial", {"floor": "concrete_polished", "walls": "brick", "light": "cool daylight"}),
    ("mediterranean", {"floor": "terracotta", "walls": "plaster_cream", "light": "golden evening"}),
    ("classic", {"floor": "wood_parquet", "walls": "plaster_cream", "light": "warm daylight"}),
    ("rustic", {"floor": "wood_parquet", "walls": "plaster_cream", "light": "golden evening"}),
]

# --------------------------------------------------------------------------
# Lighting moods -> HDRI (Poly Haven, CC0) and sun settings
# --------------------------------------------------------------------------
# sun_azimuth_deg is a compass bearing: 0 = north (+Y of the building frame),
# 90 = east (+X), 180 = south, clockwise. sun_elevation_deg above the horizon;
# a negative elevation with strength 0 means "no sun" (night).
# hdri_strength is the world background strength the Blender side uses.
LIGHTING: dict[str, dict] = {
    "warm daylight": {"hdri": "kloppenheim_06", "sun_elevation_deg": 35, "sun_azimuth_deg": 210,
                      "sun_strength": 3.0, "colour_temperature_k": 5200, "hdri_strength": 1.0},
    "cool daylight": {"hdri": "kloofendal_43d_clear_puresky", "sun_elevation_deg": 55, "sun_azimuth_deg": 180,
                      "sun_strength": 4.0, "colour_temperature_k": 6500, "hdri_strength": 1.0},
    "golden evening": {"hdri": "venice_sunset", "sun_elevation_deg": 12, "sun_azimuth_deg": 255,
                       "sun_strength": 2.0, "colour_temperature_k": 3200, "hdri_strength": 1.2},
    "overcast": {"hdri": "overcast_soil_puresky", "sun_elevation_deg": 45, "sun_azimuth_deg": 180,
                 "sun_strength": 0.3, "colour_temperature_k": 6900, "hdri_strength": 1.5},
    "night": {"hdri": "dikhololo_night", "sun_elevation_deg": -10, "sun_azimuth_deg": 0,
              "sun_strength": 0.0, "colour_temperature_k": 3800, "hdri_strength": 0.6},
}

HDRIS: dict[str, dict] = {entry["hdri"]: {"source": "polyhaven", "mood": mood} for mood, entry in LIGHTING.items()}

# Fixed slots (no brief words change them in this milestone).
TRIM_MATERIAL = "painted_wood_white"
WINDOW_FRAME_MATERIAL = "painted_metal_white"
CEILING_MATERIAL = "plaster_white"
WET_WALLS_MATERIAL = "tiles_light"
WET_FLOOR_DEFAULT = "tiles_light"


def asset_for(slug: str) -> tuple[str, str]:
    """``(source, asset_id)`` of a material slug; KeyError for unknown slugs."""
    entry = MATERIALS[slug]
    return entry["source"], entry["asset"]
