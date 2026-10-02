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

Milestone 6 (docs/milestone6.md §5): furniture texture maps (Poly Haven
``oak_veneer_01``, ``walnut_veneer``, ``rough_linen``, checked on 2026-10-02
with ``/info/<id>`` and ``/files/<id>``: Diffuse, nor_gl and Rough at 1k-16k),
the veneer slugs, ``METALLIC`` and the procedural wet-wall tiles. No
ambientCG id was added (the session cannot fetch it and most sizes are
unknown).
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
#
# "albedo_mode" (docs/milestone5.md §2.2) says where a textured material
# takes its colour from:
# - "flat": the colour is "flat"; the texture adds luminance detail only,
#   ``flat * (1 - detail + detail * lum(texture) / mean_lum)``, capped at 0.9.
#   Plaster and paint: their photos carry the tan light of the shoot
#   (white_plaster_02 averages linear (0.27, 0.25, 0.20)), so the photo's
#   hue must not reach the wall. "detail" is the share of the texture's
#   luminance variation that is kept.
# - "texture": the texture colour, its mean luminance scaled to the flat
#   colour's (gain clamped to 0.5..2.5, capped at 0.9): wood, stone, tiles,
#   brick and carpet, whose colour is the material.
MATERIALS: dict[str, dict] = {
    "wood_oak_light":     {"source": "ambientcg", "asset": "WoodFloor051",       "kind": "wood",    "flat": [0.62, 0.47, 0.30], "roughness": 0.45, "albedo_mode": "texture"},
    "wood_walnut":        {"source": "ambientcg", "asset": "WoodFloor046",       "kind": "wood",    "flat": [0.25, 0.14, 0.08], "roughness": 0.4,  "albedo_mode": "texture"},
    "wood_parquet":       {"source": "polyhaven", "asset": "herringbone_parquet", "kind": "wood",   "flat": [0.45, 0.30, 0.17], "roughness": 0.4,  "albedo_mode": "texture"},
    "concrete_polished":  {"source": "ambientcg", "asset": "Concrete046",        "kind": "hard",    "flat": [0.45, 0.45, 0.44], "roughness": 0.25, "albedo_mode": "texture"},
    "terracotta":         {"source": "polyhaven", "asset": "patio_tiles",        "kind": "hard",    "flat": [0.55, 0.27, 0.16], "roughness": 0.7,  "albedo_mode": "texture"},
    "marble":             {"source": "polyhaven", "asset": "marble_01",          "kind": "hard",    "flat": [0.80, 0.78, 0.74], "roughness": 0.15, "albedo_mode": "texture"},
    "tiles_light":        {"source": "ambientcg", "asset": "Tiles074",           "kind": "hard",    "flat": [0.82, 0.82, 0.80], "roughness": 0.2,  "albedo_mode": "texture"},
    "carpet":             {"source": "ambientcg", "asset": "Carpet016",          "kind": "soft",    "flat": [0.60, 0.55, 0.45], "roughness": 0.95, "albedo_mode": "texture"},
    "plaster_white":      {"source": "polyhaven", "asset": "white_plaster_02",   "kind": "plaster", "flat": [0.85, 0.84, 0.80], "roughness": 0.85, "albedo_mode": "flat", "detail": 0.35},
    "plaster_cream":      {"source": "polyhaven", "asset": "beige_wall_001",     "kind": "plaster", "flat": [0.80, 0.72, 0.55], "roughness": 0.85, "albedo_mode": "flat", "detail": 0.35},
    # Charcoal = the white plaster texture's luminance detail on the charcoal colour (flat mode).
    "plaster_charcoal":   {"source": "polyhaven", "asset": "white_plaster_02",   "kind": "plaster", "flat": [0.05, 0.05, 0.055], "roughness": 0.6, "albedo_mode": "flat", "detail": 0.35},
    "plaster_exterior":   {"source": "polyhaven", "asset": "grey_plaster",       "kind": "plaster", "flat": [0.55, 0.54, 0.52], "roughness": 0.9,  "albedo_mode": "flat", "detail": 0.5},
    "brick":              {"source": "polyhaven", "asset": "red_brick_03",       "kind": "brick",   "flat": [0.40, 0.17, 0.12], "roughness": 0.9,  "albedo_mode": "texture"},
    "wood_panel":         {"source": "polyhaven", "asset": "wooden_panels",      "kind": "wood",    "flat": [0.28, 0.17, 0.09], "roughness": 0.5,  "albedo_mode": "texture"},
    "painted_wood_white": {"source": "polyhaven", "asset": "white_planks_clean", "kind": "painted", "flat": [0.88, 0.87, 0.84], "roughness": 0.4,  "albedo_mode": "flat", "detail": 0.5},
    # Metal032 is bare grey metal (ambientCG has no clean white painted metal);
    # flat mode takes the white from "flat" and keeps 15 % of the metal's
    # luminance detail. No real-world size on the API -> 1 m.
    "painted_metal_white": {"source": "ambientcg", "asset": "Metal032",          "kind": "metal",   "flat": [0.85, 0.85, 0.85], "roughness": 0.35, "albedo_mode": "flat", "detail": 0.15},
}

ALBEDO_MODES = ("flat", "texture")


def albedo_mode(slug: str) -> tuple[str, float | None]:
    """``(mode, detail)`` of a material slug of ``MATERIALS`` or
    ``FURNITURE_MATERIALS``: ``("flat", detail)`` or ``("texture", None)``.
    Slugs of neither table (local slugs of the scene builder) and furniture
    slugs without a texture report ``("texture", None)``: their colour is
    the flat colour anyway."""
    entry = MATERIALS.get(slug) or FURNITURE_MATERIALS.get(slug) or {}
    mode = entry.get("albedo_mode", "texture")
    if mode == "flat":
        return "flat", float(entry["detail"])
    return "texture", None

# Slugs for the parametric furniture, decor and door leaves (wenart.blender.parametric,
# shell.py): fabric, bedding, sanitary ceramic, appliance steel, worktop stone, dark
# lacquer, plant green and wood veneer. They live beside MATERIALS (no brief word
# picks them); FLAT_COLOURS / ROUGHNESS / METALLIC below cover both tables and
# wenart.blender.materials reads those.
#
# Milestone 6 (docs/milestone6.md §5 row 8): Poly Haven CC0 maps for the fabrics
# and the veneers ("source" / "asset"; the real size the fetcher reads from the
# API is repeated in "size_m", checked against https://api.polyhaven.com/info/<id>
# on 2026-10-02). The fabric photos are dyed (rough_linen is blue), so the
# fabrics use the flat albedo mode: the colour stays the vocabulary colour and
# only the weave's luminance, normal and roughness reach the piece. The veneers
# replace the floor planks on furniture wood and door leaves (texture mode, their
# grain runs along the image height, i.e. along the box UV ``v``, which is world Z
# on vertical faces: door leaves and headboards get vertical grain). Steel is a
# metal (``metallic`` 1); glazed ceramic is smoother than in Milestone 4. A
# failed download leaves the flat colour (materials.py records why).
FURNITURE_MATERIALS: dict[str, dict] = {
    "fabric_linen":  {"kind": "fabric",  "flat": [0.72, 0.66, 0.55], "roughness": 0.9, "source": "polyhaven",
                      "asset": "rough_linen", "size_m": [0.2707, 0.2713], "albedo_mode": "flat", "detail": 0.5},
    "fabric_white":  {"kind": "fabric",  "flat": [0.86, 0.85, 0.82], "roughness": 0.9, "source": "polyhaven",
                      "asset": "rough_linen", "size_m": [0.2707, 0.2713], "albedo_mode": "flat", "detail": 0.35},
    "ceramic_white": {"kind": "ceramic", "flat": [0.92, 0.92, 0.90], "roughness": 0.05},
    "steel_brushed": {"kind": "metal",   "flat": [0.62, 0.62, 0.62], "roughness": 0.3, "metallic": 1.0},
    "stone_worktop": {"kind": "hard",    "flat": [0.24, 0.24, 0.25], "roughness": 0.3},
    "lacquer_dark":  {"kind": "painted", "flat": [0.04, 0.04, 0.045], "roughness": 0.4},
    "plant_green":   {"kind": "organic", "flat": [0.10, 0.28, 0.09], "roughness": 0.8},
    "wood_veneer_oak":    {"kind": "wood", "flat": [0.62, 0.47, 0.30], "roughness": 0.45, "source": "polyhaven",
                           "asset": "oak_veneer_01", "size_m": [1.83, 1.83], "albedo_mode": "texture"},
    "wood_veneer_walnut": {"kind": "wood", "flat": [0.25, 0.14, 0.08], "roughness": 0.4, "source": "polyhaven",
                           "asset": "walnut_veneer", "size_m": [1.8, 1.8], "albedo_mode": "texture"},
}
# The style slot the parametric fabric comes from; the Milestone 3 profile
# has no such slot, so this is the slug used (recorded as assumed).
DEFAULT_TEXTILE_MATERIAL = "fabric_linen"
# Furniture wood and wood door leaves take the veneer of the floor's wood tone
# (the Milestone 4/5 builds put the floor planks on headboards and doors).
VENEER_FOR_WOOD: dict[str, str] = {
    "wood_oak_light": "wood_veneer_oak", "wood_parquet": "wood_veneer_oak",
    "wood_walnut": "wood_veneer_walnut", "wood_panel": "wood_veneer_walnut",
    "wood_veneer_oak": "wood_veneer_oak", "wood_veneer_walnut": "wood_veneer_walnut",
}
DEFAULT_VENEER = "wood_veneer_oak"


def veneer_for(slug: str | None) -> str | None:
    """The veneer slug for a wood slug (``VENEER_FOR_WOOD``), None for a slug that is not wood."""
    if slug in VENEER_FOR_WOOD:
        return VENEER_FOR_WOOD[slug]
    entry = MATERIALS.get(slug or "") or FURNITURE_MATERIALS.get(slug or "") or {}
    return DEFAULT_VENEER if entry.get("kind") == "wood" else None


def furniture_textures() -> list[tuple[str, str, str]]:
    """``[(source, asset_id, slug)]`` of the furniture texture maps (one row per asset id).

    Every build with parametric furniture or wood doors uses them, whatever
    the style says, so ``wenart.assets fetch`` downloads them with the style's
    assets and ``build.referenced_asset_ids`` puts them into the fingerprint."""
    rows, seen = [], set()
    for slug, entry in FURNITURE_MATERIALS.items():
        asset = entry.get("asset")
        if asset and asset not in seen:
            seen.add(asset)
            rows.append((entry["source"], asset, slug))
    return rows

FLAT_COLOURS: dict[str, list[float]] = {
    **{slug: entry["flat"] for slug, entry in MATERIALS.items()},
    **{slug: entry["flat"] for slug, entry in FURNITURE_MATERIALS.items()},
}
ROUGHNESS: dict[str, float] = {
    **{slug: entry["roughness"] for slug, entry in MATERIALS.items()},
    **{slug: entry["roughness"] for slug, entry in FURNITURE_MATERIALS.items()},
}
# Principled BSDF Metallic per slug (0 when not listed).
METALLIC: dict[str, float] = {
    slug: float(entry.get("metallic", 0.0))
    for slug, entry in list(MATERIALS.items()) + list(FURNITURE_MATERIALS.items()) if entry.get("metallic")
}

# Wet-room tiles without an image asset (docs/milestone6.md §5 row 4): every
# ``tiles_*`` slug whose texture set is not available is drawn as procedural
# glazed tiles (materials.py node group ``wenart_glazed_tiles``): Brick
# Texture on the box UVs in metres, the tile colour from "flat" with +-3 % per
# tile, grey grout, roughness 0.08 tile / 0.7 grout, a bump from the grout mask.
PROCEDURAL_TILES: dict[str, float | list[float]] = {
    "tile_w_m": 0.60, "tile_h_m": 0.30, "grout_m": 0.003, "grout_colour": [0.55, 0.55, 0.53],
    "tile_roughness": 0.08, "grout_roughness": 0.7, "variation": 0.03, "bump_strength": 0.4, "bump_distance_m": 0.002,
}
PROCEDURAL_TILE_PREFIX = "tiles_"

# Milestone 3 multiplied these into the wall albedo. The plaster entries went
# in Milestone 5 (§2.2): flat albedo mode takes the plaster colour from
# "flat" directly, and charcoal had been darkened twice (albedo 0.027 instead
# of 0.05). The profile no longer has a ``walls.tint``; the identity entries
# below are kept only for readers of the old table.
WALL_TINTS: dict[str, list[float]] = {
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
