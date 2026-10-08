"""Milestone 10 material, finish, exterior and lighting tables (docs/milestone10.md §4.3, §4.8, §4.9; track C).

What: tables in the shape of ``wenart/style/vocabulary.py``'s own, merged into it by the vocabulary (the lead's
wiring, commit 2f94482): ``MATERIALS`` (wall finishes, wet-wall tiles, floors, window frames, exterior materials) and
``FURNITURE_MATERIALS`` (furniture veneers, metal handles) entries, ``LIGHTING`` (all 9 moods) and the keyword tables
``FLOOR_WORDS``, ``WALL_WORDS``, ``LIGHT_WORDS`` that the vocabulary prepends to its own. A slug never carries a colour
(docs/milestone10.md §1.6b row 14): a colour is a name of ``wenart/style/colours.py`` stored beside the slug in the
style profile (``{material, colour}``).

Entry shapes (``kind`` is one of ``KINDS``; ``flat`` is linear RGB; ``roughness`` is the Principled BSDF roughness):

- textured: ``{source: "polyhaven" | "ambientcg", asset, kind, flat, roughness, albedo_mode, [detail], [size_m],
  [wet_safe], [colourable], flat_source}``. ``asset`` and ``size_m`` (the real-world size from the API, metres) were
  checked against the live APIs on 2026-10-08 (``wenart/style/asset_checks_m10.json``, ``python -m
  wenart.assets.fetch check``). ``albedo_mode`` is ``texture`` (the photo's colour, its mean luminance scaled to the
  flat colour's) or ``flat`` (the colour is ``flat`` or the style's colour, the photo adds ``detail`` of its
  luminance variation; docs/milestone5.md §2.2). ``flat_source`` says where ``flat`` comes from: ``measured`` (the mean
  linear colour of the 1k Diffuse map, Poly Haven), ``colour:<name>`` (the entry's colour is a ``colours.py`` name:
  flat-mode looks) or ``estimated:<name>`` (a texture-mode ambientCG look whose photo could not be downloaded in the
  session: the luminance of a ``colours.py`` name stands in until a pod measures it).
- procedural: ``{source: "procedural", asset: None, procedural: <Blender node group name or None>, kind, flat,
  roughness, albedo_mode: "flat", detail: 0.0, [params], ...}``: no external file. ``procedural: None`` is a plain
  Principled BSDF from ``flat``, ``roughness`` and ``metallic``; a node group name (``wenart_tiles``,
  ``wenart_wallpaper``, ``wenart_slats``, ``wenart_standing_seam``) asks the builder (track F) for that pattern with
  ``params``. ``vocabulary.asset_for`` and ``wenart.assets.fetch`` skip entries without an ``asset``.
- ``colourable: True`` marks flat-mode (and procedural) looks that take the profile's colour name for their base
  colour (paint, render, fibre cement, painted brick, tiles, wallpapers ...); ``colourable: False`` a flat-mode or
  procedural look that does not (a wood tone, a window-frame metal); a texture-mode look keeps its photo's colour and
  the profile's colour is only a description of it. ``wenart.style.profile.is_colourable(slug)`` answers for every
  slug of the vocabulary, the Milestone 3 plaster and paint slugs included (flat mode, no flag).
- ``wet_safe: True``: a hard floor that stays in bathrooms, WCs and kitchens (the vocabulary's ``WET_SAFE_FLOORS``
  grows by these; ``wet_safe_floors()``).

Why a separate module: the vocabulary is lead-owned and read by every stage (and by Blender's Python, which has no
PyYAML: this module stays pure Python and imports only ``colours``); track C fills these tables without touching it.

Photos and colours: every Poly Haven texture below was looked at on a contact sheet of its 1k Diffuse map on 2026-10-08
before it was chosen; ambientCG assets were chosen from their API tags (the session cannot download them) and are
listed with ``flat_source: estimated`` or ``colour:<name>``.
"""
from __future__ import annotations

from wenart.style import colours as C

CHECKED = "2026-10-08"
KINDS = ("wood", "hard", "soft", "plaster", "brick", "painted", "metal", "stone", "wallpaper", "roof", "ground",
         "plastic", "organic", "fabric", "ceramic")
PROCEDURAL = "procedural"


def _lin(name: str, *modifiers: str) -> list[float]:
    return [round(v, 3) for v in C.linear_rgb(name, modifiers)]


def _tex(source: str, asset: str, kind: str, flat, roughness: float, size, *, mode: str = "texture",
         detail: float | None = None, wet_safe: bool = False, colourable: bool | None = None,
         flat_source: str = "measured", metallic: float | None = None) -> dict:
    """A textured entry (see the module docstring); ``size`` is the API size ``[w, h]`` in metres or None."""
    entry: dict = {"source": source, "asset": asset, "kind": kind, "flat": [float(v) for v in flat],
                   "roughness": roughness, "albedo_mode": mode}
    if mode == "flat":
        entry["detail"] = detail
    if size:
        entry["size_m"] = [float(v) for v in size]
    if metallic:
        entry["metallic"] = metallic
    if wet_safe:
        entry["wet_safe"] = True
    if mode == "flat" or colourable is not None:
        entry["colourable"] = (mode == "flat") if colourable is None else bool(colourable)
    entry["flat_source"] = flat_source
    return entry


def _proc(procedural: str | None, kind: str, flat, roughness: float, *, params: dict | None = None,
          colourable: bool = True, wet_safe: bool = False, metallic: float | None = None,
          flat_source: str = "colour table") -> dict:
    """A procedural entry (see the module docstring)."""
    entry: dict = {"source": PROCEDURAL, "asset": None, "procedural": procedural, "kind": kind,
                   "flat": [float(v) for v in flat], "roughness": roughness, "albedo_mode": "flat", "detail": 0.0}
    if params:
        entry["params"] = params
    if metallic:
        entry["metallic"] = metallic
    if wet_safe:
        entry["wet_safe"] = True
    entry["colourable"] = bool(colourable)
    entry["flat_source"] = flat_source
    return entry


PH, ACG = "polyhaven", "ambientcg"

# --------------------------------------------------------------------------
# Tiles: one node group, many patterns (docs/milestone10.md §4.3 wet walls)
# --------------------------------------------------------------------------

# pattern: running_bond (offset rows), grid (stacked), hexagon; tile_size_m = [w, h] (hexagon: [flat-to-flat, point-to-point]);
# grout_m; grout_colour: a colours.py name; variation: the +- share of tile-to-tile colour spread ("zellige": a visible spread).
TILE_PATTERNS: dict[str, dict] = {
    "tiles_subway": {"pattern": "running_bond", "tile_size_m": [0.15, 0.075], "grout_m": 0.002, "grout_colour": "light grey",
                     "variation": 0.02, "tile_roughness": 0.08, "label": "subway 7.5 x 15 cm"},
    "tiles_large_porcelain": {"pattern": "grid", "tile_size_m": [0.6, 1.2], "grout_m": 0.002, "grout_colour": "light grey",
                              "variation": 0.02, "tile_roughness": 0.15, "label": "large-format porcelain 60 x 120 cm"},
    "tiles_zellige": {"pattern": "grid", "tile_size_m": [0.1, 0.1], "grout_m": 0.003, "grout_colour": "light grey",
                      "variation": 0.12, "tile_roughness": 0.1, "label": "zellige 10 x 10 cm with a colour spread"},
    "tiles_hexagon": {"pattern": "hexagon", "tile_size_m": [0.1, 0.1155], "grout_m": 0.003, "grout_colour": "light grey",
                      "variation": 0.03, "tile_roughness": 0.12, "label": "hexagon 10 cm flat to flat"},
    "tiles_mosaic": {"pattern": "grid", "tile_size_m": [0.025, 0.025], "grout_m": 0.002, "grout_colour": "light grey",
                     "variation": 0.04, "tile_roughness": 0.08, "label": "mosaic 2.5 cm"},
    "tiles_cement": {"pattern": "grid", "tile_size_m": [0.2, 0.2], "grout_m": 0.002, "grout_colour": "light grey",
                     "variation": 0.08, "tile_roughness": 0.55, "label": "cement tiles 20 x 20 cm, matt, mottled"},
}
TILE_DEFAULT_COLOUR = {"tiles_subway": "white", "tiles_large_porcelain": "off white", "tiles_zellige": "sage",
                       "tiles_hexagon": "off white", "tiles_mosaic": "sky blue", "tiles_cement": "light grey"}

WALLPAPER_PATTERNS: dict[str, dict] = {
    "wallpaper_stripe": {"pattern": "stripe", "repeat_m": [0.106, 0.106], "colour": "cream"},
    "wallpaper_botanical": {"pattern": "botanical", "repeat_m": [0.53, 0.64], "colour": "sage"},
    "wallpaper_geometric": {"pattern": "geometric", "repeat_m": [0.32, 0.32], "colour": "off white"},
    "wallpaper_check": {"pattern": "check", "repeat_m": [0.1, 0.1], "colour": "greige"},
    "wallpaper_herringbone": {"pattern": "herringbone", "repeat_m": [0.2, 0.2], "colour": "light grey"},
    "wallpaper_grasscloth": {"pattern": "grasscloth", "repeat_m": [0.05, 0.05], "colour": "sand"},
}

_FLOOR_TONES = {"light": ("oak", 0.65), "mid": ("coffee", 0.65), "dark": ("walnut brown", 0.65)}

MATERIALS: dict[str, dict] = {
    # ---- wall finishes (paint in any colour: the profile's walls.colour) ------------------------------------------
    "paint": _tex(PH, "plastered_wall", "plaster", _lin("off white"), 0.9, [2.0, 2.0], mode="flat", detail=0.2,
                  flat_source="colour:off white"),
    "lime_plaster": _tex(PH, "grey_plaster_03", "plaster", _lin("off white"), 0.95, [1.0, 1.0], mode="flat", detail=0.55,
                         flat_source="colour:off white"),
    "microcement": _tex(PH, "painted_concrete_02", "plaster", _lin("light grey"), 0.4, [4.0, 4.0], mode="flat",
                        detail=0.5, flat_source="colour:light grey"),
    "venetian_plaster": _tex(PH, "white_plaster_02", "plaster", _lin("off white"), 0.25, [1.0, 1.0], mode="flat",
                             detail=0.5, flat_source="colour:off white"),
    "wood_slat": _proc("wenart_slats", "wood", _lin("oak"), 0.5, colourable=False,
                       params={"slat_width_m": 0.03, "gap_m": 0.02, "backing_colour": "charcoal"}),
    "stone_wall_ledgestone": _tex(PH, "rustic_stone_wall_02", "stone", [0.248, 0.178, 0.109], 0.85, [1.5, 1.5]),
    "stone_wall_rubble": _tex(PH, "stone_wall", "stone", [0.368, 0.292, 0.2], 0.85, [2.0, 2.0]),
    "stone_wall_ashlar": _tex(PH, "seaworn_sandstone_brick", "stone", [0.261, 0.191, 0.122], 0.8, [1.69, 1.69]),
    "stone_wall_slate": _tex(PH, "castle_wall_slates", "stone", [0.265, 0.218, 0.141], 0.7, [2.5, 2.5]),
    "brick_red": _tex(PH, "large_red_bricks", "brick", [0.403, 0.185, 0.096], 0.9, [2.0, 2.0]),
    "brick_white": _tex(ACG, "PaintedBricks004", "brick", _lin("off white"), 0.7, [1.55, 1.55], mode="flat", detail=0.7,
                        flat_source="colour:off white"),
    "brick_grey": _tex(PH, "brick_wall_13", "brick", [0.214, 0.184, 0.15], 0.85, [2.0, 2.0]),
    "brick_reclaimed": _tex(PH, "brick_wall_001", "brick", [0.136, 0.074, 0.048], 0.9, [3.0, 3.0]),
    "concrete_exposed": _tex(PH, "concrete_wall_001", "stone", [0.29, 0.273, 0.242], 0.7, [1.5, 1.5]),
    # ---- floors (wood) --------------------------------------------------------------------------------------------
    "wood_oak_natural": _tex(PH, "oak_wood_planks", "wood", [0.363, 0.18, 0.088], 0.45, [1.2, 1.2]),
    "wood_oak_whitewashed": _tex(PH, "laminate_floor_02", "wood", _lin("greige", "light"), 0.55, [1.7, 1.7], mode="flat",
                                 detail=0.6, flat_source="colour:light greige", colourable=False),
    "wood_oak_smoked": _tex(PH, "dark_wooden_planks", "wood", [0.087, 0.069, 0.05], 0.4, [2.0, 2.0]),
    "wood_oak_grey": _tex(PH, "laminate_floor_02", "wood", _lin("greige"), 0.5, [1.7, 1.7], mode="flat", detail=0.55,
                          flat_source="colour:greige", colourable=False),
    "wood_wide_plank": _tex(PH, "wood_floor", "wood", [0.216, 0.117, 0.055], 0.45, [1.7, 1.7]),
    "wood_herringbone_light": _tex(ACG, "WoodFloor034", "wood", _lin(_FLOOR_TONES["light"][0]), 0.4, [1.9, 1.9], mode="flat",
                                   detail=_FLOOR_TONES["light"][1], flat_source=f"colour:{_FLOOR_TONES['light'][0]}",
                                   colourable=False),
    "wood_herringbone_mid": _tex(ACG, "WoodFloor034", "wood", _lin(_FLOOR_TONES["mid"][0]), 0.4, [1.9, 1.9], mode="flat",
                                 detail=_FLOOR_TONES["mid"][1], flat_source=f"colour:{_FLOOR_TONES['mid'][0]}",
                                 colourable=False),
    "wood_herringbone_dark": _tex(ACG, "WoodFloor034", "wood", _lin(_FLOOR_TONES["dark"][0]), 0.4, [1.9, 1.9], mode="flat",
                                  detail=_FLOOR_TONES["dark"][1], flat_source=f"colour:{_FLOOR_TONES['dark'][0]}",
                                  colourable=False),
    "wood_chevron_light": _tex(PH, "herringbone_parquet", "wood", _lin(_FLOOR_TONES["light"][0]), 0.4, [3.4, 3.4],
                               mode="flat", detail=_FLOOR_TONES["light"][1], flat_source=f"colour:{_FLOOR_TONES['light'][0]}",
                               colourable=False),
    "wood_chevron_mid": _tex(PH, "herringbone_parquet", "wood", _lin(_FLOOR_TONES["mid"][0]), 0.4, [3.4, 3.4],
                             mode="flat", detail=_FLOOR_TONES["mid"][1], flat_source=f"colour:{_FLOOR_TONES['mid'][0]}",
                             colourable=False),
    "wood_chevron_dark": _tex(PH, "herringbone_parquet", "wood", _lin(_FLOOR_TONES["dark"][0]), 0.4, [3.4, 3.4],
                              mode="flat", detail=_FLOOR_TONES["dark"][1], flat_source=f"colour:{_FLOOR_TONES['dark'][0]}",
                              colourable=False),
    "wood_ash": _tex(PH, "ash_veneer", "wood", [0.413, 0.297, 0.205], 0.5, [1.0, 1.0]),
    "wood_bamboo": _tex(PH, "bamboo_veneer", "wood", [0.646, 0.42, 0.217], 0.45, [1.0, 1.0]),
    # ---- floors (stone, tile, resilient, soft) --------------------------------------------------------------------
    "terrazzo": _tex(PH, "terrazzo_tiles", "hard", [0.251, 0.152, 0.095], 0.25, [2.0, 2.0], wet_safe=True),
    "travertine": _tex(PH, "floor_tiles_04", "hard", [0.572, 0.382, 0.192], 0.35, [4.0, 4.0], wet_safe=True),
    "limestone": _tex(PH, "floor_tiles_02", "hard", [0.346, 0.282, 0.21], 0.5, [4.0, 4.0], wet_safe=True),
    "slate_floor": _tex(PH, "granite_tile", "hard", [0.076, 0.077, 0.077], 0.55, [2.3, 2.3], wet_safe=True),
    "vinyl": _tex(PH, "linoleum_brown", "hard", _lin("light grey"), 0.35, [2.0, 2.0], mode="flat", detail=0.25,
                  wet_safe=True, flat_source="colour:light grey"),
    "cork": _tex(ACG, "Cork002", "soft", _lin("coffee"), 0.7, None, flat_source="estimated:coffee"),
    "carpet_wool": _tex(ACG, "Carpet016", "soft", _lin("light grey"), 0.95, [1.7, 1.7], mode="flat", detail=0.6,
                        flat_source="colour:light grey"),
    "sisal": _tex(PH, "hessian_230", "soft", [0.264, 0.189, 0.101], 0.95, [0.2688, 0.2672]),
    # ---- tiles (floors and wet walls): procedural patterns, colour and grout from the brief -----------------------
    **{slug: _proc("wenart_tiles", "hard", _lin(TILE_DEFAULT_COLOUR[slug]), p["tile_roughness"],
                   params={k: v for k, v in p.items() if k not in ("tile_roughness", "label")},
                   wet_safe=True, flat_source=f"colour:{TILE_DEFAULT_COLOUR[slug]}")
       for slug, p in TILE_PATTERNS.items()},
    "marble_slab": _tex(ACG, "Marble012", "hard", _lin("silver"), 0.12, None, wet_safe=True, flat_source="estimated:silver"),
    # ---- wallpapers: procedural patterns, base colour from the brief, ink = the base colour with the "dark" modifier --
    **{slug: _proc("wenart_wallpaper", "wallpaper", _lin(p["colour"]), 0.85,
                   params={"pattern": p["pattern"], "repeat_m": p["repeat_m"], "ink_modifier": "dark"},
                   flat_source=f"colour:{p['colour']}")
       for slug, p in WALLPAPER_PATTERNS.items()},
    # ---- window frames (inside and outside); painted frames are painted_metal_white in a colour -------------------
    "pvc_white": _proc(None, "plastic", _lin("white"), 0.45, colourable=False, flat_source="colour:white"),
    "aluminium_anthracite": _proc(None, "metal", _lin("anthracite"), 0.45, colourable=False, metallic=0.6,
                                  flat_source="colour:anthracite"),
    "steel_black": _proc(None, "metal", _lin("black"), 0.4, colourable=False, metallic=0.8, flat_source="colour:black"),
    "dark_bronze": _proc(None, "metal", _lin("dark bronze"), 0.4, colourable=False, metallic=0.8,
                         flat_source="colour:dark bronze"),
    "oak": _tex(PH, "oak_veneer_01", "wood", [0.358, 0.21, 0.097], 0.5, [1.83, 1.83]),
    # ---- exterior: facade ------------------------------------------------------------------------------------------
    "render": _tex(PH, "grey_plaster", "plaster", _lin("greige"), 0.9, [1.0, 1.0], mode="flat", detail=0.4,
                   flat_source="colour:greige"),
    "stone_cladding": _tex(PH, "rustic_stone_wall", "stone", [0.186, 0.136, 0.075], 0.85, [1.52, 1.52]),
    "wood_cladding": _tex(PH, "weathered_plank_siding", "wood", [0.073, 0.047, 0.032], 0.7, [1.57, 1.57]),
    "fibre_cement": _tex(PH, "exterior_wall_cladding", "painted", _lin("grey"), 0.7, [2.0, 2.0], mode="flat", detail=0.35,
                         flat_source="colour:grey"),
    # ---- exterior: roofs --------------------------------------------------------------------------------------------
    "clay_tiles": _tex(PH, "clay_roof_tiles_03", "roof", [0.272, 0.093, 0.039], 0.6, [2.6, 2.6]),
    "concrete_tiles": _tex(PH, "grey_roof_01", "roof", _lin("anthracite"), 0.65, [8.0, 8.0], mode="flat", detail=0.6,
                           flat_source="colour:anthracite"),
    "slate": _tex(PH, "roof_slates_03", "roof", [0.167, 0.16, 0.14], 0.5, [3.0, 3.0]),
    "standing_seam": _proc("wenart_standing_seam", "metal", _lin("dark grey"), 0.35, metallic=0.8,
                           params={"seam_spacing_m": 0.45, "seam_height_m": 0.025}, flat_source="colour:dark grey"),
    "green_roof": _tex(PH, "concrete_moss", "roof", [0.098, 0.097, 0.013], 0.95, [3.0, 3.0]),
    # ---- exterior: ground ------------------------------------------------------------------------------------------
    "paving": _tex(PH, "large_square_pattern_01", "ground", [0.204, 0.189, 0.154], 0.8, [3.0, 3.0]),
    "paving_stone": _tex(PH, "floor_tiles_02", "ground", [0.346, 0.282, 0.21], 0.7, [4.0, 4.0]),
    "gravel": _tex(PH, "gravel_floor_02", "ground", [0.405, 0.384, 0.33], 0.95, [2.0, 2.0]),
    "grass": _tex(ACG, "Grass004", "ground", _lin("olive", "dark"), 0.95, [1.4, 1.4], flat_source="estimated:dark olive"),
    "decking": _tex(PH, "synthetic_wood", "wood", [0.17, 0.078, 0.04], 0.65, [2.0, 2.0]),
    # ---- decor pots ---------------------------------------------------------------------------------------------------
    "rattan": _tex(ACG, "Wicker005", "organic", _lin("coffee"), 0.8, [0.2, 0.2], flat_source="estimated:coffee"),
}


def _veneer(asset: str, flat, roughness: float, size) -> dict:
    return {"kind": "wood", "flat": [float(v) for v in flat], "roughness": roughness, "source": PH, "asset": asset,
            "size_m": [float(v) for v in size], "albedo_mode": "texture", "flat_source": "measured"}


FURNITURE_MATERIALS: dict[str, dict] = {
    # Furniture veneers (docs/milestone10.md §1.6b row 14: ``design.wood`` is one of these ``wood_veneer_*`` slugs);
    # the two of Milestone 6 (oak, walnut) stay in vocabulary.py.
    "wood_veneer_oak_light": _veneer("oak_veneer_02", [0.715, 0.485, 0.3], 0.45, [1.0, 1.0]),
    "wood_veneer_ash":       _veneer("ash_veneer", [0.413, 0.297, 0.205], 0.5, [1.0, 1.0]),
    "wood_veneer_maple":     _veneer("white_maple_veneer", [0.769, 0.659, 0.484], 0.45, [1.0, 1.0]),
    "wood_veneer_teak":      _veneer("teak_veneer", [0.432, 0.223, 0.095], 0.5, [1.0, 1.0]),
    "wood_veneer_black_oak": _veneer("black_oak_veneer", [0.147, 0.121, 0.096], 0.45, [1.0, 1.0]),
    "wood_veneer_cherry":    _veneer("cherry_veneer", [0.747, 0.433, 0.23], 0.4, [1.0, 1.0]),
    # Handles (steel_brushed is the brushed-steel handle of Milestone 6).
    "metal_black": {"kind": "metal", "flat": _lin("black"), "roughness": 0.35, "metallic": 0.8, "flat_source": "colour:black"},
    "metal_brass": {"kind": "metal", "flat": _lin("brass"), "roughness": 0.25, "metallic": 1.0, "flat_source": "colour:brass"},
}

# --------------------------------------------------------------------------
# Value sets of the looks (docs/milestone10.md §1.4, §4.4, §4.7)
# --------------------------------------------------------------------------

CABINET_FRONT_STYLES = ("flat", "shaker", "slatted", "glass")
CABINET_HANDLES = {"brushed_steel": "steel_brushed", "black": "metal_black", "brass": "metal_brass"}
CABINET_WORKTOPS = {"stone": "stone_worktop", "wood": "wood_veneer_oak", "terrazzo": "terrazzo", "steel": "steel_brushed"}
DOOR_STYLES = ("flush", "shaker_panel", "glazed", "pocket", "sliding", "barn", "double", "entrance")
DOOR_HANDLES = tuple(CABINET_HANDLES)
# The window-frame materials (a colour phrase picks one; any other colour is painted_metal_white in that colour).
WINDOW_FRAME_MATERIALS = ("pvc_white", "aluminium_anthracite", "steel_black", "dark_bronze", "oak", "painted_metal_white")
FRAME_COLOUR_MATERIALS = {"white": "pvc_white", "off white": "pvc_white", "anthracite": "aluminium_anthracite",
                          "charcoal": "aluminium_anthracite", "black": "steel_black", "dark bronze": "dark_bronze",
                          "bronze": "dark_bronze"}
FURNITURE_WOODS = ("wood_veneer_oak", "wood_veneer_oak_light", "wood_veneer_walnut", "wood_veneer_ash", "wood_veneer_maple",
                   "wood_veneer_teak", "wood_veneer_black_oak", "wood_veneer_cherry")
POT_MATERIALS = {"rattan": "rattan", "wicker": "rattan", "basket": "rattan", "ceramic": "ceramic_white",
                 "porcelain": "ceramic_white", "terracotta": "terracotta", "concrete": "concrete_polished",
                 "metal": "steel_brushed", "steel": "steel_brushed"}
PLANT_SPECIES = ("palm", "monstera", "fiddle_leaf_fig", "olive", "fern", "other")
EXTERIOR_SLOTS = ("facade", "roof", "window_frame", "door", "paving", "garden")
EXTERIOR_MATERIALS = {
    "facade": ("render", "brick_red", "brick_white", "brick_grey", "brick_reclaimed", "stone_cladding", "wood_cladding",
               "fibre_cement"),
    "roof": ("clay_tiles", "concrete_tiles", "slate", "standing_seam", "green_roof"),
    "window_frame": WINDOW_FRAME_MATERIALS,
    "door": ("wood_oak_light", "wood_walnut", "painted_wood_white", "lacquer_dark", "steel_black", "aluminium_anthracite"),
    "paving": ("paving", "paving_stone", "gravel", "decking"),
    "garden": ("grass", "gravel", "decking", "green_roof"),
}


def wet_safe_floors() -> tuple[str, ...]:
    """The floor slugs of this module that stay in wet rooms (``wet_safe``), in table order."""
    return tuple(slug for slug, e in MATERIALS.items() if e.get("wet_safe"))


# --------------------------------------------------------------------------
# Lighting moods (docs/milestone10.md §4.9): all nine, every one with hdri_strength, wb_residual and lamps_on
# --------------------------------------------------------------------------

# The five moods of Milestone 3 repeat vocabulary.py's own values (sun, temperature, strength) unchanged and add
# ``wb_residual`` (the white-balance residual of ``wenart.blender.render.WB_RESIDUAL``: 0 = full correction,
# 1 = none) and ``lamps_on``. The four new moods use verified Poly Haven HDRIs (``asset_checks_m10.json``):
#   bright noon      qwantani_noon_puresky   "clear midday pure sky with a bright sun" (white balance 5313 K)
#   blue hour        aarfontein_dusk         "dusk under broad overcast clouds, soft cool ambient light" (5303 K)
#   cloudy soft      kloofendal_overcast_puresky  "soft, low-contrast overcast light" (5303 K)
#   interior evening sunset_jhbcentral       "low-contrast rooftop sunset, cool twilight, skyline" (5319 K), lamps on
# Sun elevation / azimuth / strength, colour temperature, hdri_strength and wb_residual of the new moods are
# designer values (assumed, like the five old ones); a sun_strength of 0 means "no sun": the sky alone lights the
# room (blue hour) or the lamps do (interior evening: table, floor, pendant and ceiling lights emit).
LIGHTING: dict[str, dict] = {
    "warm daylight": {"hdri": "kloppenheim_06", "sun_elevation_deg": 35, "sun_azimuth_deg": 210, "sun_strength": 3.0,
                      "colour_temperature_k": 5200, "hdri_strength": 1.0, "wb_residual": 0.35, "lamps_on": False},
    "cool daylight": {"hdri": "kloofendal_43d_clear_puresky", "sun_elevation_deg": 55, "sun_azimuth_deg": 180,
                      "sun_strength": 4.0, "colour_temperature_k": 6500, "hdri_strength": 1.0, "wb_residual": 0.0,
                      "lamps_on": False},
    "golden evening": {"hdri": "venice_sunset", "sun_elevation_deg": 12, "sun_azimuth_deg": 255, "sun_strength": 2.0,
                       "colour_temperature_k": 3200, "hdri_strength": 1.2, "wb_residual": 0.5, "lamps_on": False},
    "overcast": {"hdri": "overcast_soil_puresky", "sun_elevation_deg": 45, "sun_azimuth_deg": 180, "sun_strength": 0.3,
                 "colour_temperature_k": 6900, "hdri_strength": 1.5, "wb_residual": 0.0, "lamps_on": False},
    "night": {"hdri": "dikhololo_night", "sun_elevation_deg": -10, "sun_azimuth_deg": 0, "sun_strength": 0.0,
              "colour_temperature_k": 3800, "hdri_strength": 0.6, "wb_residual": 0.5, "lamps_on": False},
    "bright noon": {"hdri": "qwantani_noon_puresky", "sun_elevation_deg": 65, "sun_azimuth_deg": 180, "sun_strength": 5.0,
                    "colour_temperature_k": 5600, "hdri_strength": 1.0, "wb_residual": 0.0, "lamps_on": False},
    "blue hour": {"hdri": "aarfontein_dusk", "sun_elevation_deg": -4, "sun_azimuth_deg": 270, "sun_strength": 0.0,
                  "colour_temperature_k": 8500, "hdri_strength": 0.8, "wb_residual": 0.5, "lamps_on": False},
    "cloudy soft": {"hdri": "kloofendal_overcast_puresky", "sun_elevation_deg": 40, "sun_azimuth_deg": 180,
                    "sun_strength": 0.15, "colour_temperature_k": 6500, "hdri_strength": 1.4, "wb_residual": 0.0,
                    "lamps_on": False},
    "interior evening": {"hdri": "sunset_jhbcentral", "sun_elevation_deg": -3, "sun_azimuth_deg": 285, "sun_strength": 0.0,
                         "colour_temperature_k": 3000, "hdri_strength": 0.5, "wb_residual": 0.5, "lamps_on": True},
}

# --------------------------------------------------------------------------
# Keyword tables (the vocabulary prepends them to its own; matching is whole-word, earliest position first, the
# longest keyword at the same position; see profile._first_hit). A phrase with an object word ("... floor",
# "... walls") only reads the table of that object.
# --------------------------------------------------------------------------

FLOOR_WORDS: list[tuple[str, str]] = [
    ("natural oak", "wood_oak_natural"), ("honey oak", "wood_oak_natural"), ("white oak", "wood_oak_light"),
    ("pale oak", "wood_oak_light"), ("blonde oak", "wood_oak_light"),
    ("whitewashed oak", "wood_oak_whitewashed"), ("white-washed oak", "wood_oak_whitewashed"),
    ("white washed oak", "wood_oak_whitewashed"), ("limed oak", "wood_oak_whitewashed"),
    ("bleached oak", "wood_oak_whitewashed"), ("washed oak", "wood_oak_whitewashed"),
    ("smoked oak", "wood_oak_smoked"), ("dark oak", "wood_oak_smoked"),
    ("grey oak", "wood_oak_grey"), ("gray oak", "wood_oak_grey"), ("greige oak", "wood_oak_grey"),
    ("silver oak", "wood_oak_grey"),
    ("wide plank", "wood_wide_plank"), ("wide-plank", "wood_wide_plank"), ("wide planks", "wood_wide_plank"),
    ("wide boards", "wood_wide_plank"), ("wide board", "wood_wide_plank"),
    ("light herringbone", "wood_herringbone_light"), ("mid herringbone", "wood_herringbone_mid"),
    ("medium herringbone", "wood_herringbone_mid"), ("dark herringbone", "wood_herringbone_dark"),
    ("light chevron", "wood_chevron_light"), ("mid chevron", "wood_chevron_mid"), ("medium chevron", "wood_chevron_mid"),
    ("dark chevron", "wood_chevron_dark"), ("chevron", "wood_chevron_mid"),
    ("ash", "wood_ash"), ("bamboo", "wood_bamboo"),
    ("terrazzo", "terrazzo"), ("travertine", "travertine"), ("limestone", "limestone"),
    ("slate floor", "slate_floor"), ("slate tiles", "slate_floor"), ("slate", "slate_floor"),
    ("large format tiles", "tiles_large_porcelain"), ("large-format tiles", "tiles_large_porcelain"),
    ("large porcelain", "tiles_large_porcelain"), ("porcelain tiles", "tiles_large_porcelain"),
    ("porcelain", "tiles_large_porcelain"),
    ("cement tiles", "tiles_cement"), ("cement tile", "tiles_cement"), ("encaustic", "tiles_cement"),
    ("hydraulic tiles", "tiles_cement"),
    ("hexagon tiles", "tiles_hexagon"), ("hexagonal tiles", "tiles_hexagon"), ("hex tiles", "tiles_hexagon"),
    ("honeycomb tiles", "tiles_hexagon"),
    ("luxury vinyl", "vinyl"), ("vinyl", "vinyl"), ("lvt", "vinyl"),
    ("cork", "cork"),
    ("wool carpet", "carpet_wool"), ("berber", "carpet_wool"),
    ("sisal", "sisal"), ("jute", "sisal"), ("seagrass", "sisal"), ("coir", "sisal"),
]

_WALLPAPER_WORDS = (("striped", "wallpaper_stripe"), ("stripe", "wallpaper_stripe"), ("stripes", "wallpaper_stripe"),
                    ("botanical", "wallpaper_botanical"), ("floral", "wallpaper_botanical"), ("leaf", "wallpaper_botanical"),
                    ("geometric", "wallpaper_geometric"), ("checked", "wallpaper_check"), ("check", "wallpaper_check"),
                    ("gingham", "wallpaper_check"), ("herringbone", "wallpaper_herringbone"))

WALL_WORDS: list[tuple[str, str]] = [
    ("lime plaster", "lime_plaster"), ("limewash", "lime_plaster"), ("lime wash", "lime_plaster"),
    ("venetian plaster", "venetian_plaster"), ("marmorino", "venetian_plaster"),
    ("microcement", "microcement"), ("micro-cement", "microcement"), ("micro cement", "microcement"),
    ("polished plaster", "microcement"),
    *[(f"{word} wallpaper", slug) for word, slug in _WALLPAPER_WORDS],
    *[(f"wallpaper {word}", slug) for word, slug in _WALLPAPER_WORDS],
    ("grasscloth", "wallpaper_grasscloth"), ("grass cloth", "wallpaper_grasscloth"),
    ("wood slat", "wood_slat"), ("wood slats", "wood_slat"), ("slatted wood", "wood_slat"), ("slat panelling", "wood_slat"),
    ("slat paneling", "wood_slat"), ("slat wall", "wood_slat"), ("fluted wood", "wood_slat"),
    ("ledgestone", "stone_wall_ledgestone"), ("stacked stone", "stone_wall_ledgestone"),
    ("rubble stone", "stone_wall_rubble"), ("rubble", "stone_wall_rubble"), ("fieldstone", "stone_wall_rubble"),
    ("ashlar", "stone_wall_ashlar"), ("sandstone blocks", "stone_wall_ashlar"), ("cut stone", "stone_wall_ashlar"),
    ("slate wall", "stone_wall_slate"), ("slate cladding", "stone_wall_slate"),
    ("natural stone", "stone_wall_ledgestone"), ("stone wall", "stone_wall_ledgestone"),
    ("exposed brick", "brick"), ("white-painted brick", "brick_white"), ("white painted brick", "brick_white"), ("whitewashed brick", "brick_white"),
    ("white brick", "brick_white"), ("painted brick", "brick_white"),
    ("grey brick", "brick_grey"), ("gray brick", "brick_grey"),
    ("reclaimed brick", "brick_reclaimed"), ("antique brick", "brick_reclaimed"), ("old brick", "brick_reclaimed"),
    ("rustic brick", "brick_reclaimed"),
    ("red brick", "brick_red"),
    ("exposed concrete", "concrete_exposed"), ("raw concrete", "concrete_exposed"), ("béton brut", "concrete_exposed"),
    ("concrete", "concrete_exposed"),
    ("painted walls", "paint"), ("paint", "paint"),
]

LIGHT_WORDS: list[tuple[str, str]] = [
    ("bright noon", "bright noon"), ("bright daylight", "bright noon"), ("midday", "bright noon"), ("noon", "bright noon"),
    ("blue hour", "blue hour"), ("twilight", "blue hour"), ("dusk", "blue hour"),
    ("cloudy soft", "cloudy soft"), ("soft cloudy", "cloudy soft"), ("cloudy", "cloudy soft"),
    ("interior evening", "interior evening"), ("evening lamps", "interior evening"), ("lamps on", "interior evening"),
    ("lamplight", "interior evening"), ("lamp light", "interior evening"), ("evening lights", "interior evening"),
]
