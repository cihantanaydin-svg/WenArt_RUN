"""Materials for the scene: textured PBR from the assets manifest, flat colour
fallback, glass, the dashed-red "unverified" overlay and the world nodes.

Texture sets follow the shared interface of wenart.assets:
``{"id", "source", "licence", "size_m": [w, h], "files": {"albedo", "normal",
"roughness", ("displacement")}}``; ``normal`` is OpenGL convention, which is
what Blender's Normal Map node expects (no green flip). Displacement is never
connected (material displacement stays at its default, bump only).

UVs: the meshes carry a box-projected UV layer in metres (common.assign_box_uvs),
so the Mapping node scales by ``1 / size_m`` and a tile has its real size.

Albedo modes (docs/milestone5.md §2.2, ``vocabulary.MATERIALS[slug]
["albedo_mode"]``): ``flat`` materials (plaster, paint) take their colour
from the vocabulary and only the luminance detail from the texture
(TexImage -> RGBToBW -> Math DIVIDE by the texture's mean luminance -> Math
MULTIPLY_ADD ``x * detail + 1 - detail`` -> VectorMath SCALE of the flat
colour -> VectorMath MINIMUM 0.9 -> Base Color); ``texture`` materials keep
the texture colour with its mean luminance scaled to the flat colour's (gain
clamped to 0.5..2.5, capped at 0.9). Normal and roughness maps are the same
in both modes. Every record says ``albedo_mode``, ``detail`` and
``gain_clamped``.

Window panes (§2.1): Glass BSDF for camera rays and singular rays (the
camera's ray inside the pane, so both faces refract and the outside view
stays in place), Transparent BSDF for every other ray. The Milestone 3 pane
(Glass BSDF, Transparent for shadow rays) let the sun in 2.4x too strongly
and the sky too weakly (the main cause of the orange cast) and biased light
portals; camera-only glass lights the room like an open hole while the
camera, the depth and the index passes still see the pane.

Milestone 6 (docs/milestone6.md §5):

- the unverified stripes emit for camera rays only (factor = stripe x Light
  Path 'Is Camera Ray'): their red light lit small rooms red and the auto
  white balance then turned the whole view teal (row 1);
- ``tiles_*`` slugs without an image texture set become procedural glazed
  tiles, the node group ``wenart_glazed_tiles`` (Brick Texture on the box UVs
  in metres, 60 x 30 cm, 3 mm grout, roughness 0.08 tile / 0.7 grout, bump
  from the grout mask; ``vocabulary.PROCEDURAL_TILES``) when textures are on;
  with ``--no-textures`` they stay the flat colour (row 4);
- the furniture slugs have albedo modes too (the dyed linen photo in flat
  mode), and ``vocabulary.METALLIC`` sets the Principled Metallic (steel 1).

Milestone 10 (docs/milestone10.md §4.2-§4.8, track F):

- ``MaterialLibrary.get(..., colour=, params=)``: a colour phrase of ``wenart/style/colours.py`` ("warm greige")
  sets the base colour of a slug that takes one (``colourable``: flat albedo mode and procedural looks unless the
  vocabulary says ``colourable: False``; a material without a texture always), the record says when it was not
  applied; ``params`` override a procedural look's vocabulary ``params`` (the wet walls' tile size, pattern and
  grout colour);
- procedural looks of the vocabulary (``source: procedural``) are node groups, no file: ``wenart_tiles_<pattern>``
  (running bond and grid on a Brick Texture, hexagons from two lattices; tile size, grout width and colour, a
  per-tile colour spread), ``wenart_wallpaper_<pattern>`` (stripe, check, geometric, herringbone, botanical,
  grasscloth: the colour and its ``dark`` ink), ``wenart_slats`` and ``wenart_standing_seam``; a procedural entry
  without a group (``procedural: None``: window-frame metals, PVC) is a plain Principled material; ``tiles_*`` slugs
  with an image asset that is missing keep the Milestone 6 glazed tiles;
- ``exterior_material(library, slug, colour=None)`` (the outside looks, §4.8) and ``light_material`` (lit lamp
  parts of the interior evening mood);
- the world strength of the four new moods comes from the vocabulary's ``hdri_strength``.

Milestone 13 (docs/milestone13.md §13.1 track T5, K5; the diagnosis §1.6: 72-81 % of every interior frame is
shell, and the ceiling, worktops, fronts, sanitary ware, handles and the wet-room tiles were flat colours):

- ``SHELL_SLOTS`` is the shell material table per slot (``ceiling``, ``worktop``, ``front``, ``ceramic``, ``metal``,
  ``tile``, ``plaster``): a CC0 texture set of the style vocabulary (every id exists in ``vocabulary.MATERIALS`` /
  ``FURNITURE_MATERIALS`` and in ``wenart/style/asset_checks_m10.json``; none is invented) and the material layers
  of the Blender 5.2 Principled BSDF: ``Sheen Weight`` / ``Sheen Roughness`` (fabrics), ``Coat Weight`` /
  ``Coat Roughness`` / ``Coat IOR`` (lacquer, glazed ceramic, polished stone), a Bevel node on the normal (edge
  highlights, radius in metres, ``samples``), an Ambient Occlusion node mixed into the base colour (contact shadows
  in corners, ``Distance`` in metres, ``only_local`` off) and a procedural roughness variation (``wenart_imperfection``:
  a Noise Texture mixed into the roughness; no CC0 imperfection image is in the catalogue, so it is procedural).
  Tiles get their grout height on the Material Output's Displacement (``displacement_method = "BOTH"``: the bump
  carries the look, true displacement where the object is subdivided). ``shell_material(slot, style, assets)``
  builds one; ``MaterialLibrary.get`` routes the shell slugs through it when the ``shell`` lever is on
  (``lighting.light_levers``; the A/B variant ``shell``). Every record says ``shell_slot`` and ``shell_layers``.
- ``exterior_world_nodes(..., sun_disc=True, sun_elevation_deg, sun_azimuth_deg)``: the exterior sky carries the
  sun disc (``ShaderNodeTexSky.sun_disc``, ``sun_intensity``, ``sun_size``). Round 3 (docs/milestone13.md §14.3,
  P1: at 3 W/m² every facade was flat and bluish): the disc is visible to the camera only. The world is a Mix
  Shader whose factor is the Light Path output 'Is Camera Ray': camera rays see the sky with the disc, every other
  ray (diffuse, glossy, shadow, the background importance map) the same sky without it, so the sun lamp at
  ``lighting.SUN_STRENGTH_WM2`` is the one direct sun and the disc never lights the scene a second time
  (``direct_sun: "lamp"``, ``sun_disc_camera_only``, the ``world_mix`` record; render.py keeps the lamp shown).
  ``sun_intensity`` stays for the disc's look. ``disc_camera_only=False`` gives the P1 world (the disc for every
  ray, ``direct_sun: "sky disc"``, the lamp hidden under it). The HDRI path of the interior views stays.
  Round 4 (§14.8, the P3 pre-flight): the sky's Background Strength is the one whose own sun equals the lamp
  (``exterior_sky_strength``, the measured sky/sun pair ``SKY_SUN_TABLE``: 7.71 at 1000 W/m² and 35 degrees, was
  0.5); the disc keeps its image brightness; the horizontal diffuse-to-direct ratio of the pair (0.166 at 35
  degrees) lies in the clear-sky range; the record's ``sky_calibration`` keeps the derivation.
- Fix round after P3 (16-17 Oct 2026): the ``worktop`` slot is ambientCG Marble012 (one jointless polished slab;
  Poly Haven marble_01 is a set of tiles and P3's worktops read as tiles), repeated every ``size_m`` (2 m) while the
  manifest knows no real size for it (``slot_repeat_m``); the ``front`` slot is a ``paint`` slot: painted trim and
  fronts leave the slug's own plank photo (white_planks_clean) out (``paint_drop``; its board seams showed every
  ~10 cm on P3's skirting), the record says ``shell_photo_dropped``.
- ``fixture_material``: the emissive surface of a light-rig fixture (``lighting.room_rig``), its colour from the
  blackbody temperature of the fixture, its radiance the fixed ``lighting.SHADE_EMISSION_WM2SR`` (round 3: the
  shade no longer follows the lamp power, so it never clips at the project EV range).
- The ``ceiling`` shell slot is the one slot a slug reaches without an asset (``plaster_white`` asked bare), so
  its material name carries ``__ceiling``: the walls' ``plaster_white__white_plaster_02`` (slot ``plaster``) and
  the ceilings' ``plaster_white__white_plaster_02__ceiling`` are two materials with two layer sets, never a
  Blender ``.001`` twin (``material_name``, pure).

Fix round after P4a (17 Oct 2026; pod P4a rendered real02, look review: "bathroom mirrors render as blank frosted
panels"):

- ``mirror_glass_material(mat)``: the glass of a library mirror becomes a real mirror. The cause, measured on the
  seven ABO mirrors real02 used (abo_B07B4W5R8N, B071HBBDZ1, B0718ZKQK8, B07RNMMYNR, B071V8LJQJ, B071V8M937,
  B084HTY39G; their glTF textures read from the ABO bucket on 17 Oct 2026): each model has one material for frame and
  glass (one texture atlas), and the glass is a painted grey ramp whose metal/roughness texels are roughness 1.0
  dielectric (B07B4W5R8N, B071V8LJQJ, B071V8M937, B084HTY39G), roughness 0.4 dielectric (B071HBBDZ1), roughness 0
  dielectric (B0718ZKQK8: a 4 % grey reflector) or roughness 0.1 metal (B07RNMMYNR): a matte grey panel, not a mirror.
  What the glass texels share is an exactly neutral albedo: the linear chroma ``(max - min) / max`` is below
  ``MIRROR_GLASS_CHROMA_MAX`` and the brightest channel above ``MIRROR_GLASS_VALUE_MIN`` for 90-100 % of each model's
  glass texels and for 0.00-2.7 % of every other texel (wood 0.3-0.75, painted white trim 0.05, hammered metal
  0.1; the terrace table abo_B07ML7P94G, a control: 0.01 %). The copy masks those texels in the node tree (Separate
  Color -> max, min -> LESS_THAN / GREATER_THAN) and mixes the vocabulary's ``mirror`` slug in where the mask is 1:
  Base Color 0.9, Metallic 1.0, Roughness 0.03; the frame keeps its own maps. A material whose base colour is a
  constant is all glass or not at all by the same rule. The copy records ``wenart_mirror_glass``.
  ``mirror_glass_materials`` maps a model's material list for the builder (furniture.py calls it for library
  mirrors).

Node names were checked against Blender 5.2.2: Principled BSDF inputs 'Base
Color', 'Roughness', 'Normal', 'Emission Color', 'Emission Strength', 'Metallic';
Milestone 13 (the 5.2 manual, render/shader_nodes/shader/principled.html; API bpy.types.ShaderNodeBevel,
ShaderNodeAmbientOcclusion, ShaderNodeTexSky, Material.displacement_method): 'Sheen Weight', 'Sheen Roughness',
'Sheen Tint', 'Coat Weight', 'Coat Roughness', 'Coat IOR', 'Coat Tint', 'Specular IOR Level'; Bevel 'Radius',
'Normal' -> 'Normal' (property samples); Ambient Occlusion 'Color', 'Distance', 'Normal' -> 'Color', 'AO'
(properties samples, inside, only_local); Displacement 'Height', 'Midlevel', 'Scale' -> 'Displacement'; Sky Texture
sun_disc, sun_size, sun_intensity, sun_elevation, sun_rotation, altitude, air_density, aerosol_density,
ozone_density;
Glass BSDF inputs 'Color', 'Roughness', 'IOR'; Glossy BSDF (ShaderNodeBsdfAnisotropic) 'Color', 'Roughness';
Fresnel 'IOR'; Light Path outputs 'Is Camera Ray', 'Is Singular Ray'; RGB to BW 'Color' -> 'Val';
Math inputs 'Value', 'Value_001', 'Value_002' (operations DIVIDE,
MULTIPLY_ADD, MAXIMUM); Vector Math inputs 'Vector', 'Vector_001', 'Scale'
(operations SCALE, MULTIPLY, MINIMUM); ShaderNodeTexSky sky_type
'MULTIPLE_SCATTERING' with sun_elevation / sun_rotation (radians); Brick
Texture inputs 'Vector', 'Color1', 'Color2', 'Mortar', 'Scale', 'Mortar Size',
'Mortar Smooth', 'Bias', 'Brick Width', 'Row Height', outputs 'Color' and
Brick Texture inputs 'Vector', 'Color1', 'Color2', 'Mortar', 'Scale', 'Mortar Size',
'Factor' (identifier 'Fac'), properties offset / offset_frequency / squash /
squash_frequency; node groups through ``NodeTree.interface.new_socket(name,
in_out=..., socket_type=...)``. Milestone 10: Vector Math WRAP (inputs 0 value, 1 max, 2 min), DOT_PRODUCT
(output 'Value'), ABSOLUTE; Mix (data_type VECTOR / RGBA; identifiers 'Factor_Float', 'A_Vector', 'B_Vector',
'A_Color', 'B_Color', 'Result_Vector', 'Result_Color'); White Noise 'Vector' -> 'Value'; Voronoi 'Vector', 'Scale'
-> 'Distance'; Noise 'Vector', 'Scale', 'Detail' -> 'Fac'; Separate / Combine XYZ; Bump 'Strength', 'Distance',
'Height' -> 'Normal'; Math FRACT, FLOOR, FLOORED_MODULO, LESS_THAN, GREATER_THAN, ABSOLUTE; Emission 'Color',
'Strength'.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

# Flat colours (linear RGB) and roughness per material slug, used when no
# texture set is available. The style vocabulary (wenart.style.vocabulary,
# importable inside Blender: no PyYAML needed) is the source of truth for
# every style slug; the local table only adds the slugs of the scene builder
# itself and is the last resort when the vocabulary cannot be imported
# (``VOCABULARY_IMPORT_ERROR`` then says why and build.py warns).
_LOCAL_FLAT_COLOURS: dict[str, tuple[float, float, float]] = {
    "plaster_exterior": (0.55, 0.54, 0.52),
    "proxy_grey": (0.45, 0.45, 0.45),
    "unknown": (0.50, 0.50, 0.50),
}
_LOCAL_ROUGHNESS: dict[str, float] = {"plaster_exterior": 0.9, "proxy_grey": 0.6, "unknown": 0.6}
UNVERIFIED_RED = (1.0, 0.03, 0.02)
# Milestone 11 decision D3 (docs/milestone11.md §17, brief markers_in_final, default false): the unverified stripes
# stay out of every render; the build turns them on for a debug build (brief markers_in_final: true, build.py
# --markers). One switch for every way a stripe is made: MaterialLibrary.get(unverified=), the striped proxy,
# add_unverified_overlay (furniture assets).
_MARKERS = {"on": False}


def set_markers(on: bool) -> None:
    """Turn the unverified stripes on (debug) or off (the D3 default) for the materials made from now on."""
    _MARKERS["on"] = bool(on)


def markers_on() -> bool:
    """True when the unverified stripes are drawn (``set_markers``)."""
    return bool(_MARKERS["on"])


# Sources whose assets are CC0 (the same list as wenart.assets.fetch.LICENCES;
# repeated here because that module needs packages Blender's Python lacks).
CC0_SOURCES = ("polyhaven", "ambientcg")
CC0 = "CC0"


def _vocabulary_tables() -> tuple[dict, dict, dict, dict, dict, str | None]:
    """``(flat_colours, roughness, albedo_modes, metallic, procedural_tiles, error)`` from the style vocabulary."""
    try:
        from wenart.style import vocabulary as V
        flat = {slug: (float(c[0]), float(c[1]), float(c[2])) for slug, c in V.FLAT_COLOURS.items()}
        rough = {slug: float(r) for slug, r in V.ROUGHNESS.items()}
        modes = {slug: V.albedo_mode(slug) for slug in list(V.MATERIALS) + list(V.FURNITURE_MATERIALS)}
        metal = {slug: float(m) for slug, m in V.METALLIC.items()}
        tiles = dict(V.PROCEDURAL_TILES)
    except Exception as exc:  # noqa: BLE001 - the build must not die over a colour table
        return {}, {}, {}, {}, {}, f"{type(exc).__name__}: {exc}"
    return flat, rough, modes, metal, tiles, None


_FLAT, _ROUGH, _MODES, _METALLIC, _TILES, VOCABULARY_IMPORT_ERROR = _vocabulary_tables()


def _vocabulary_entries() -> tuple[dict, dict]:
    """``({slug: {asset, source, procedural, params, colourable}}, {mood: hdri_strength})`` of the vocabulary
    (Milestone 10); empty when it cannot be imported (``VOCABULARY_IMPORT_ERROR`` says why)."""
    try:
        from wenart.style import vocabulary as V
        entries = {}
        for slug, e in list(V.MATERIALS.items()) + list(V.FURNITURE_MATERIALS.items()):
            entries[slug] = {k: e[k] for k in ("asset", "source", "procedural", "params", "colourable", "kind") if k in e}
        strength = {mood: float(e["hdri_strength"]) for mood, e in V.LIGHTING.items() if "hdri_strength" in e}
    except Exception:  # noqa: BLE001 - see _vocabulary_tables
        return {}, {}
    return entries, strength


ENTRIES, _MOOD_HDRI_STRENGTH = _vocabulary_entries()
FLAT_COLOURS: dict[str, tuple[float, float, float]] = {**_LOCAL_FLAT_COLOURS, **_FLAT}
ROUGHNESS: dict[str, float] = {**_LOCAL_ROUGHNESS, **_ROUGH}
# The local plaster_exterior is a plaster too: flat mode with half the detail
# (the vocabulary entry says the same; this only matters without it).
ALBEDO_MODES: dict[str, tuple[str, float | None]] = {"plaster_exterior": ("flat", 0.5), **_MODES}
# Highest albedo any textured material may reach (a white wall reflects ~85 %;
# above 0.9 inter-reflections blow up and look like a light source).
MAX_ALBEDO = 0.9
METALLIC: dict[str, float] = {"steel_brushed": 1.0, **_METALLIC}
# Procedural glazed tiles (docs/milestone6.md §5 row 4); the local copy is the
# fallback when the vocabulary cannot be imported.
PROCEDURAL_TILES: dict = {"tile_w_m": 0.60, "tile_h_m": 0.30, "grout_m": 0.003, "grout_colour": [0.55, 0.55, 0.53],
                          "tile_roughness": 0.08, "grout_roughness": 0.7, "variation": 0.03, "bump_strength": 0.4,
                          "bump_distance_m": 0.002, **_TILES}
PROCEDURAL_TILE_PREFIX = "tiles_"
TILES_GROUP = "wenart_glazed_tiles"
STRIPES_CAMERA_NODE = "wenart_stripes_camera_only"


def flat_colour(slug: str) -> tuple[float, float, float]:
    """Flat colour for a slug (vocabulary, then the local table, then grey)."""
    return FLAT_COLOURS.get(slug, FLAT_COLOURS["unknown"])


def albedo_mode(slug: str) -> tuple[str, float | None]:
    """``("flat", detail)`` or ``("texture", None)`` for a slug (docs/milestone5.md §2.2)."""
    return ALBEDO_MODES.get(slug, ("texture", None))


def metallic(slug: str) -> float:
    """Principled BSDF Metallic of a slug (``vocabulary.METALLIC``, 0 when not listed)."""
    return float(METALLIC.get(slug, 0.0))


def procedural_for(slug: str, has_texture: bool, use_textures: bool) -> str | None:
    """The procedural look of a slug without an image texture set while textures are on: its vocabulary node group
    (``wenart_tiles``, ``wenart_wallpaper``, ``wenart_slats``, ``wenart_standing_seam``; Milestone 10), the
    Milestone 6 ``"glazed_tiles"`` for another ``tiles_*`` slug (docs/milestone6.md §5 row 4), else None (a
    procedural entry without a group is a plain flat material)."""
    if has_texture or not use_textures:
        return None
    entry = ENTRIES.get(slug) or {}
    if entry.get("source") == "procedural":
        return entry.get("procedural") if entry.get("procedural") in PROCEDURAL_GROUPS else None
    if str(slug).startswith(PROCEDURAL_TILE_PREFIX):
        return "glazed_tiles"
    return None


def procedural_note() -> str:
    """The text recorded for the procedural tiles (material record and custom property)."""
    t = PROCEDURAL_TILES
    return (f"procedural glazed tiles {float(t['tile_w_m']):.2f} x {float(t['tile_h_m']):.2f} m, "
            f"{float(t['grout_m']) * 1000:.0f} mm grout (node group {TILES_GROUP})")


def licence_problem(entry: dict, asset_id: str) -> str | None:
    """Why a manifest entry may not be used, or None: assets must be CC0 and
    come from a source of the CC0 list (docs/milestone3.md §2)."""
    source, licence = entry.get("source"), entry.get("licence")
    if source not in CC0_SOURCES:
        return f"asset {asset_id}: source {source!r} is not in the CC0 source list {list(CC0_SOURCES)}; refused"
    if str(licence or "").strip().upper() != CC0:
        return f"asset {asset_id}: licence {licence!r} is not {CC0}; refused"
    return None


def material_maps(tset: dict | None) -> list[str]:
    """The map names a material record lists (pure; Milestone 13, T8 metric 10 reads ``materials[].maps`` and
    counts a textured slot when the names carry ``normal`` and ``rough``): the texture set's file keys in a
    fixed order (``texture_set`` requires albedo, normal and roughness), [] without a set."""
    files = (tset or {}).get("files") or {}
    order = ("albedo", "normal", "roughness", "displacement", "opacity", "ao", "metallic")
    names = [k for k in order if files.get(k)] + sorted(k for k in files if k not in order and files.get(k))
    return names


def recolour_parts(record: dict | None) -> dict:
    """The per-part view of a scene object's ``recolour`` record (pure; Milestone 13, T8 metric 10 counts an
    upholstered piece as recoloured when its record has a ``fabric`` key): ``furniture.recolour_materials`` writes
    ``{"applied": [{"material", "part", "colour", "copy"}], "missing": [...]}``; this returns the record with
    one key per applied part (``fabric``, ``wood``, ...) holding ``{"colour", "materials": [names], "copies":
    [names]}``. A record that already has part keys, or no ``applied`` list, comes back as it is."""
    if not isinstance(record, dict) or not isinstance(record.get("applied"), list):
        return record if isinstance(record, dict) else {}
    out = dict(record)
    for item in record["applied"]:
        if not isinstance(item, dict) or not item.get("part"):
            continue
        part = str(item["part"])
        if part in ("applied", "missing"):
            continue
        slot = out.get(part) if isinstance(out.get(part), dict) else {"colour": item.get("colour"), "materials": [],
                                                                         "copies": []}
        slot.setdefault("materials", []).append(item.get("material"))
        slot.setdefault("copies", []).append(item.get("copy"))
        slot.setdefault("colour", item.get("colour"))
        out[part] = slot
    return out


class MaterialLibrary:
    """Creates and caches Blender materials per slug and records, for the
    scene manifest, whether each one is textured or flat and why.

    Milestone 13: ``style`` (the style profile) and ``levers`` (``lighting.light_levers``; read from the
    environment when None) route the shell slugs through ``shell_material`` when the ``shell`` lever is on."""

    def __init__(self, textures: dict | None, assets_dir: str | None, use_textures: bool = True,
                 refused: dict | None = None, style: dict | None = None, levers: dict | None = None):
        self.textures = textures or {}
        self.assets_dir = Path(assets_dir) if assets_dir else None
        self.use_textures = use_textures
        # asset id -> why build.load_assets left it out (licence); the reason
        # goes into the material record instead of "not in the manifest".
        self.refused = refused or {}
        self.records: dict[str, dict] = {}
        self._cache: dict = {}
        self.style = style or {}
        self.levers = dict(levers) if levers is not None else current_levers()
        self.shell_on = bool(self.levers.get("shell"))

    # -- texture lookup ----------------------------------------------------
    def texture_set(self, asset_id: str | None) -> tuple[dict | None, str]:
        """``(texture set, reason)``: the set when it is usable (CC0 from a
        known source, every map present), else None and why."""
        if not self.use_textures:
            return None, "textures disabled (--no-textures)"
        if not asset_id:
            return None, "style names no asset for this material"
        if asset_id in self.refused:
            return None, self.refused[asset_id]
        tset = self.textures.get(asset_id)
        if tset is None:
            return None, f"asset {asset_id} not in the assets manifest"
        problem = licence_problem(tset, asset_id)
        if problem:
            return None, problem
        files = {}
        for key in ("albedo", "normal", "roughness"):
            p = tset.get("files", {}).get(key)
            if not p:
                return None, f"asset {asset_id} has no {key} map"
            path = Path(p)
            if not path.is_absolute() and self.assets_dir is not None:
                path = self.assets_dir / path
            if not path.exists():
                return None, f"asset file missing: {path}"
            files[key] = str(path)
        size = tset.get("size_m") or [1.0, 1.0]
        return {"id": asset_id, "files": files, "size_m": [float(size[0]), float(size[1])],
                "source": tset.get("source"), "licence": tset.get("licence")}, "textured"

    # -- public API ----------------------------------------------------------
    def get(self, slug: str, asset_id: str | None = None, tint=None, unverified: bool = False, colour=None,
            params: dict | None = None):
        """The material of ``slug`` (with its texture set ``asset_id`` when usable), ``tint`` multiplied in, the red
        stripes when ``unverified``; Milestone 10: ``colour`` (a ``colours.py`` phrase) as its base colour where the
        slug takes one (``colourable``, or no texture in use), ``params`` over a procedural look's own."""
        import json as _json

        unverified = bool(unverified) and markers_on()      # M11 D3: no stripes unless asked for
        pkey = _json.dumps(params, sort_keys=True) if params else None
        # Milestone 13: the shell slot of the slug (None when the shell lever is off or the slug has none); the
        # slot's texture set stands in for a missing asset (the ceiling's plaster, the worktop's stone).
        slot = shell_slot_of(slug, asset_id) if self.shell_on else None
        spec = shell_slot_spec(slot, self.style) if slot else None
        kind_layers = material_kind_layers(slug) if self.shell_on else None
        # The slot's set stands in only for the slugs of asset_for (the metal slot: steel_brushed; metal_black and
        # metal_brass keep their flat colour), else for every slug of the slot (T5 review, 15 Oct 2026).
        if (spec and spec.get("asset") and not asset_id and slug in (spec.get("asset_for") or spec.get("slugs") or (slug,))
                and self.texture_set(spec["asset"])[0] is not None):
            asset_id = spec["asset"]
        # Fix round after P3 (16-17 Oct 2026): a paint slot (front: painted trim and fronts) leaves the slug's plank
        # photo out (its seams showed every ~10 cm on the skirting)
        dropped = paint_drop(spec, slug, asset_id)
        if dropped:
            asset_id = None
        key = (slug, asset_id, tuple(tint) if tint else None, unverified, colour or None, pkey, slot,
               bool(kind_layers))
        if key in self._cache:
            return self._cache[key]
        tset, reason = self.texture_set(asset_id)
        if spec and spec.get("paint") and tset is None and self.use_textures:
            reason = (f"paint finish of the {slot} shell slot: the set {dropped} (board seams) is left out" if dropped
                      else f"paint finish of the {slot} shell slot (no plank photo: no board seams)")
        # Fix round after P3: the slot's own set without a known real size repeats at the slot's size (the worktop's
        # Marble012: 2 m, one slab, instead of the fetcher's assumed 1 m)
        repeat = slot_repeat_m(spec, tset["id"] if tset else None, self.textures.get(tset["id"]) if tset else None)
        if repeat:
            tset = dict(tset, size_m=repeat)
        # One Blender material per (slug, asset, tint, unverified, colour, params); the record
        # is keyed by the material's name so a slug used both textured (floor
        # with an asset) and flat (door leaf without one) is reported twice, and
        # an asset that could not be used keeps its own record with the reason.
        procedural = procedural_for(slug, tset is not None, self.use_textures)
        rgb = colour_linear(colour)
        colour_note = None
        if colour and rgb is None:
            colour_note = f"colour {colour!r} is not a colours.py name: the slug's own colour is used"
        elif rgb is not None and not takes_colour(slug, tset is not None):
            colour_note = (f"colour {colour!r} not applied: {slug} keeps its own colour (a wood tone, a frame metal "
                           "or the colour of its photo)")
            rgb = None
        all_params = procedural_params(slug, params) if procedural in PROCEDURAL_GROUPS else {}
        # (The shell layers change no name but the ceiling slot's: a build runs under one set of levers, so a slug
        # is either shelled or not, and the slot follows the slug, except plaster_white asked bare (the ceiling)
        # beside plaster_white with its asset (the walls): see material_name. The record's shell_slot says which.)
        name = material_name(slug, tset["id"] if tset else None, _tag(colour) if rgb is not None else None,
                             _short_hash(pkey) if pkey and procedural in PROCEDURAL_GROUPS else None, unverified,
                             slot)
        mat = pbr_material(name, slug, tset, tint, unverified=unverified, procedural=procedural, base_rgb=rgb,
                           params=all_params)
        layers = None
        if spec:
            layers = apply_shell_layers(mat, spec, textured=tset is not None, procedural=procedural)
        elif kind_layers:
            layers = apply_shell_layers(mat, {"slot": None, "layers": kind_layers}, textured=tset is not None,
                                        procedural=procedural)
        self._cache[key] = mat
        mode, detail = albedo_mode(slug)
        clamped = mat.get("wenart_gain_clamped")
        self.records[mat.name] = {
            "slug": slug, "textured": tset is not None, "asset": asset_id if tset else None,
            "source": tset["source"] if tset else None, "licence": tset["licence"] if tset else None,
            "size_m": tset["size_m"] if tset else None, "flat_colour": list(flat_colour(slug)),
            # Milestone 13 (T8 metric 10): the PBR maps the material got (the texture set's files that
            # pbr_material wires: albedo, normal, roughness); [] for a flat or procedural material.
            "maps": material_maps(tset),
            "tint": list(tint) if tint else None, "unverified": unverified,
            "reason": (reason if procedural is None
                       else f"{reason}; {procedural_note_for(procedural, slug, all_params)}"),
            "albedo_mode": mode, "detail": detail,
            "albedo_gain": mat.get("wenart_albedo_gain"), "albedo_mean_luminance": mat.get("wenart_albedo_mean"),
            "gain_clamped": None if clamped is None else bool(clamped),
            "metallic": metallic(slug), "procedural": procedural,
        }
        if spec or kind_layers:
            # pre-flight of pod P3: the slot's set is recorded only when this material uses it; a missing set keeps
            # the slot's layers and says why (the real04 worktop said marble_01 with no texture in the scene)
            wanted = spec.get("asset") if spec else None
            used = bool(wanted and tset is not None and tset["id"] == wanted)
            self.records[mat.name].update(shell_slot=slot, shell_layers=layers,
                                          shell_asset=wanted if used else None,
                                          shell_reason=(spec or {}).get("reason") or "material layers by kind")
            meant = slug in (spec.get("asset_for") or spec.get("slugs") or (slug,)) if spec else False
            if wanted and not used and meant and asset_id in (None, wanted):
                self.records[mat.name]["shell_asset_missing"] = {"asset": wanted,
                                                                 "reason": self.texture_set(wanted)[1]}
            if dropped:
                self.records[mat.name]["shell_photo_dropped"] = {
                    "asset": dropped, "reason": "paint finish: the plank photo's board seams are left out"}
            if repeat:
                self.records[mat.name]["size_note"] = (f"the set's real size is unknown (size_assumed): the "
                                                       f"{slot} slot repeats it every {repeat[0]:g} m")
        if colour:
            self.records[mat.name].update(colour=str(colour), colour_rgb=[round(v, 4) for v in rgb] if rgb else None,
                                          colour_applied=rgb is not None)
            if colour_note:
                self.records[mat.name]["colour_note"] = colour_note
        if all_params:
            self.records[mat.name]["params"] = all_params
        if procedural in PROCEDURAL_GROUPS:
            self.records[mat.name]["group"] = procedural_group_name(procedural, all_params)
        if mat.get("wenart_albedo_note"):
            self.records[mat.name]["albedo_note"] = mat["wenart_albedo_note"]
        return mat

    def textured(self, mat) -> bool:
        return bool(self.records.get(mat.name, {}).get("textured", False))

    def glass(self):
        """Window panes: camera-only glass (``window_glass_material``). Camera
        rays stop at the pane, so the depth and index passes record the window
        itself (nothing of the room is behind a window); light passes through
        as through an open hole."""
        if "glass" not in self._cache:
            self._cache["glass"] = window_glass_material("glass")
            self.records["glass"] = {"slug": "glass", "textured": False, "asset": None, "source": None,
                                     "licence": None, "size_m": None, "flat_colour": [1.0, 1.0, 1.0], "tint": None,
                                     "unverified": False, "albedo_mode": None, "detail": None, "gain_clamped": None,
                                     "reason": "camera-only glass: Glass BSDF (IOR 1.45) for camera rays and "
                                               "singular rays (both faces refract the view), "
                                               "Transparent BSDF for every other ray"}
        return self._cache["glass"]

    def thin_glass(self):
        """Glass inside the room (shower panels): transparent + glossy by Fresnel.
        A Glass BSDF pane counts as opaque for Cycles' data passes, so a toilet
        seen through a shower panel was missing from the object-index pass; a
        transparent closure with alpha below the view layer's threshold lets
        the depth and index passes reach the piece behind it."""
        if "thin_glass" not in self._cache:
            self._cache["thin_glass"] = thin_glass_material("thin_glass")
            self.records["thin_glass"] = {"slug": "glass", "textured": False, "asset": None, "source": None,
                                          "licence": None, "size_m": None, "flat_colour": [1.0, 1.0, 1.0],
                                          "tint": None, "unverified": False, "albedo_mode": None, "detail": None,
                                          "gain_clamped": None,
                                          "reason": "thin glass (transparent + glossy by Fresnel): data passes see through"}
        return self._cache["thin_glass"]

    def proxy(self, look: str = "proxy"):
        """``proxy`` (grey), ``proxy_glass`` (shower) or ``proxy_unverified`` (the grey proxy unless the stripes
        are on, M11 D3)."""
        if look == "proxy_unverified" and not markers_on():
            look = "proxy"
        if look in self._cache:
            return self._cache[look]
        if look == "proxy_glass":
            mat = thin_glass_material("proxy_glass", roughness=0.15)
        elif look == "proxy_unverified":
            mat = pbr_material("proxy_unverified", "proxy_grey", None, None, unverified=True)
        else:
            mat = pbr_material("proxy", "proxy_grey", None, None)
        self._cache[look] = mat
        return mat


# --------------------------------------------------------------------------
# Node builders
# --------------------------------------------------------------------------

def _tag(colour) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in str(colour).strip().lower())


def material_name(slug: str, tset_id: str | None = None, colour_tag: str | None = None, params_hash: str | None = None,
                  unverified: bool = False, slot: str | None = None) -> str:
    """The Blender material name of a library request (pure): ``slug``, then ``__<asset>`` for a texture set,
    ``__ceiling`` for the ceiling shell slot (round 3: the one slot that does not follow the slug, so the walls'
    ``plaster_white__white_plaster_02`` and the ceilings' ``plaster_white__white_plaster_02__ceiling`` never collide
    into a Blender ``.001`` twin), ``__<colour>``, ``__p<hash>`` for procedural overrides, ``__unverified``."""
    return (str(slug) + (f"__{tset_id}" if tset_id else "") + ("__ceiling" if slot == "ceiling" else "")
            + (f"__{colour_tag}" if colour_tag else "") + (f"__p{params_hash}" if params_hash else "")
            + ("__unverified" if unverified else ""))


def _short_hash(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]


def pbr_material(name: str, slug: str, texture_set: dict | None, tint=None, scale_m=None,
                 unverified: bool = False, procedural: str | None = None, base_rgb=None, params: dict | None = None):
    """Principled BSDF material: albedo / normal / roughness maps from
    ``texture_set`` (box UVs in metres, Mapping scale 1/size_m), the
    procedural glazed tiles (``procedural="glazed_tiles"`` and no texture
    set), or the flat colour of ``slug``. The base colour follows the slug's
    albedo mode (module docstring); Metallic comes from
    ``vocabulary.METALLIC``. ``tint`` multiplies the colour (no style slot
    sets one since Milestone 5; kept for a ``textiles`` tint). ``unverified``
    adds red emission stripes on top (camera rays only) so reviewers spot it
    in renders.

    Custom properties on the material: ``wenart_albedo_mode``,
    ``wenart_albedo_detail`` (flat), ``wenart_albedo_mean`` (texture mean
    luminance), ``wenart_albedo_gain`` and ``wenart_gain_clamped`` (texture
    mode) and ``wenart_albedo_note`` when the texture could not be read.
    Milestone 10: ``base_rgb`` (linear) replaces the slug's flat colour (a
    colour phrase of the style); ``procedural`` may name a vocabulary node
    group, set up with ``params``."""
    import bpy

    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    nodes, links = tree.nodes, tree.links
    bsdf = nodes.get("Principled BSDF")
    out = nodes.get("Material Output")
    bsdf.inputs["Roughness"].default_value = ROUGHNESS.get(slug, 0.6)
    bsdf.inputs["Metallic"].default_value = metallic(slug)
    mode, detail = albedo_mode(slug)
    mat["wenart_albedo_mode"] = mode
    if detail is not None:
        mat["wenart_albedo_detail"] = detail
    if base_rgb is not None:                       # a colour phrase: white is 1.0 linear, capped like a texture
        base_rgb = tuple(min(MAX_ALBEDO, float(c)) for c in base_rgb)
    colour = _tinted(base_rgb if base_rgb is not None else flat_colour(slug), tint)
    if base_rgb is not None:
        mat["wenart_colour"] = [round(float(v), 4) for v in base_rgb]

    if texture_set is not None:
        size = scale_m or texture_set.get("size_m") or [1.0, 1.0]
        uvmap = nodes.new("ShaderNodeUVMap")
        uvmap.uv_map = "box_m"
        mapping = nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (1.0 / float(size[0]), 1.0 / float(size[1]), 1.0)
        links.new(uvmap.outputs["UV"], mapping.inputs["Vector"])

        albedo = _image_node(nodes, texture_set["files"]["albedo"], "sRGB")
        links.new(mapping.outputs["Vector"], albedo.inputs["Vector"])
        # Photographed albedo maps carry the lighting of the photo: Poly Haven's
        # "white_plaster_02" averages linear (0.27, 0.25, 0.20), a tan, dark wall.
        mean_lum = texture_mean_luminance(albedo.image)
        mat["wenart_albedo_mean"] = round(mean_lum, 4) if mean_lum is not None else -1.0
        if mean_lum is None or mean_lum <= 1e-4:
            # Unreadable or black map: nothing to normalise by, so the flat colour
            # is used and the record says why (never a silent guess).
            mat["wenart_albedo_note"] = "albedo map unreadable or black: flat colour used, texture colour ignored"
            bsdf.inputs["Base Color"].default_value = (*colour, 1.0)
        elif mode == "flat":
            _flat_detail_albedo(nodes, links, albedo.outputs["Color"], bsdf, colour, detail, mean_lum)
        else:
            gain, clamped = albedo_gain_for(mean_lum, slug, base_rgb)
            mat["wenart_albedo_gain"] = gain
            mat["wenart_gain_clamped"] = clamped
            colour_out = albedo.outputs["Color"]
            factor = _tinted((gain, gain, gain), tint)
            if any(abs(f - 1.0) > 1e-3 for f in factor):
                scale = nodes.new("ShaderNodeVectorMath")
                scale.operation = "MULTIPLY"
                scale.inputs[1].default_value = factor
                links.new(colour_out, scale.inputs[0])
                colour_out = scale.outputs["Vector"]
            links.new(_cap(nodes, links, colour_out), bsdf.inputs["Base Color"])

        rough = _image_node(nodes, texture_set["files"]["roughness"], "Non-Color")
        links.new(mapping.outputs["Vector"], rough.inputs["Vector"])
        links.new(rough.outputs["Color"], bsdf.inputs["Roughness"])

        normal = _image_node(nodes, texture_set["files"]["normal"], "Non-Color")
        links.new(mapping.outputs["Vector"], normal.inputs["Vector"])
        nmap = nodes.new("ShaderNodeNormalMap")
        nmap.space = "TANGENT"
        nmap.uv_map = "box_m"
        links.new(normal.outputs["Color"], nmap.inputs["Color"])
        links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    elif procedural == "glazed_tiles":
        group = nodes.new("ShaderNodeGroup")
        group.node_tree = glazed_tiles_group()
        group.inputs["Tile Color"].default_value = (*colour, 1.0)
        links.new(group.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(group.outputs["Roughness"], bsdf.inputs["Roughness"])
        links.new(group.outputs["Normal"], bsdf.inputs["Normal"])
        mat["wenart_procedural"] = procedural_note()
    elif procedural in PROCEDURAL_GROUPS:
        group = procedural_node(nodes, links, procedural, slug, colour, params or {})
        links.new(group.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(group.outputs["Roughness"], bsdf.inputs["Roughness"])
        links.new(group.outputs["Normal"], bsdf.inputs["Normal"])
        mat["wenart_procedural"] = procedural_note_for(procedural, slug, params or {})
    else:
        bsdf.inputs["Base Color"].default_value = (*colour, 1.0)

    if is_ground(slug):
        _matte(nodes, links, bsdf)
        mat["wenart_matte"] = f"ground: roughness >= {GROUND_MIN_ROUGHNESS}, specular {GROUND_SPECULAR}"
    if unverified:
        _add_unverified_stripes(mat, bsdf, out)
    return mat


# Milestone 11 (docs/milestone11.md §1.1 E12): the grass looked wet at low angles (its photo's roughness map and the
# default specular on a flat plane). Ground looks (vocabulary kind "ground": grass, gravel, soil ...) are matte.
GROUND_MIN_ROUGHNESS = 0.85
GROUND_SPECULAR = 0.2
GROUND_SLUGS = ("soil",)


def is_ground(slug: str) -> bool:
    """True for a ground look (``vocabulary.MATERIALS[slug]["kind"] == "ground"``, or ``soil``)."""
    return (ENTRIES.get(slug) or {}).get("kind") == "ground" or slug in GROUND_SLUGS


def _matte(nodes, links, bsdf) -> None:
    """Roughness at least ``GROUND_MIN_ROUGHNESS`` (a Math MAXIMUM after whatever feeds it) and the Principled
    'Specular IOR Level' at ``GROUND_SPECULAR`` (Blender 5.2 input name; 0.5 is the default)."""
    rough_in = bsdf.inputs["Roughness"]
    mx = nodes.new("ShaderNodeMath")
    mx.operation = "MAXIMUM"
    mx.inputs[1].default_value = GROUND_MIN_ROUGHNESS
    if rough_in.links:
        links.new(rough_in.links[0].from_socket, mx.inputs[0])
    else:
        mx.inputs[0].default_value = float(rough_in.default_value)
    links.new(mx.outputs["Value"], rough_in)
    spec = bsdf.inputs.get("Specular IOR Level")
    if spec is not None:
        spec.default_value = GROUND_SPECULAR


def glazed_tiles_group():
    """The shader node group ``wenart_glazed_tiles`` (created once per file).

    Input ``Tile Color``; outputs ``Color``, ``Roughness``, ``Normal``. A
    Brick Texture on the ``box_m`` UVs (metres, scale 1): bricks of
    ``tile_w_m`` x ``tile_h_m``, mortar ``grout_m``, half offset every second
    row; the two brick colours are the tile colour x (1 +- variation), the
    mortar the grout colour. Roughness = Map Range of the mortar mask
    (tile 0.08 -> grout 0.7); Normal = Bump of (1 - mortar mask), so the grout
    lines are recessed."""
    import bpy

    group = bpy.data.node_groups.get(TILES_GROUP)
    if group is not None:
        return group
    t = PROCEDURAL_TILES
    group = bpy.data.node_groups.new(TILES_GROUP, "ShaderNodeTree")
    group.interface.new_socket(name="Tile Color", in_out="INPUT", socket_type="NodeSocketColor")
    group.interface.new_socket(name="Color", in_out="OUTPUT", socket_type="NodeSocketColor")
    group.interface.new_socket(name="Roughness", in_out="OUTPUT", socket_type="NodeSocketFloat")
    group.interface.new_socket(name="Normal", in_out="OUTPUT", socket_type="NodeSocketVector")
    group.interface.new_socket(name="Height", in_out="OUTPUT", socket_type="NodeSocketFloat")   # M13: 1 tile, 0 grout
    nodes, links = group.nodes, group.links
    gin = nodes.new("NodeGroupInput")
    gout = nodes.new("NodeGroupOutput")
    uv = nodes.new("ShaderNodeUVMap")
    uv.uv_map = "box_m"
    brick = nodes.new("ShaderNodeTexBrick")
    brick.offset = 0.5
    brick.offset_frequency = 2
    brick.squash = 1.0
    brick.squash_frequency = 1
    links.new(uv.outputs["UV"], brick.inputs["Vector"])
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Brick Width"].default_value = float(t["tile_w_m"])
    brick.inputs["Row Height"].default_value = float(t["tile_h_m"])
    brick.inputs["Mortar Size"].default_value = float(t["grout_m"])
    brick.inputs["Mortar Smooth"].default_value = 0.3
    brick.inputs["Bias"].default_value = 0.0
    brick.inputs["Mortar"].default_value = (*[float(c) for c in t["grout_colour"]], 1.0)
    for socket, factor in (("Color1", 1.0 + float(t["variation"])), ("Color2", 1.0 - float(t["variation"]))):
        scale = nodes.new("ShaderNodeVectorMath")
        scale.operation = "SCALE"
        links.new(gin.outputs["Tile Color"], scale.inputs["Vector"])
        scale.inputs["Scale"].default_value = factor
        links.new(scale.outputs["Vector"], brick.inputs[socket])
    links.new(brick.outputs["Color"], gout.inputs["Color"])
    rough = nodes.new("ShaderNodeMapRange")
    links.new(brick.outputs["Factor"], rough.inputs["Value"])
    rough.inputs["To Min"].default_value = float(t["tile_roughness"])
    rough.inputs["To Max"].default_value = float(t["grout_roughness"])
    links.new(rough.outputs["Result"], gout.inputs["Roughness"])
    invert = nodes.new("ShaderNodeMath")
    invert.operation = "SUBTRACT"
    invert.inputs[0].default_value = 1.0
    links.new(brick.outputs["Factor"], invert.inputs[1])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = float(t["bump_strength"])
    bump.inputs["Distance"].default_value = float(t["bump_distance_m"])
    links.new(invert.outputs["Value"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], gout.inputs["Normal"])
    links.new(invert.outputs["Value"], gout.inputs["Height"])
    return group


# Texture mode: the gain that brings the map's mean luminance to the flat
# colour's is clamped to this range (Milestone 4 allowed 4.0, which turned
# the tan white_plaster_02 photo into a glowing tan wall).
ALBEDO_GAIN_RANGE = (0.5, 2.5)


def luminance(rgb) -> float:
    return 0.2126 * float(rgb[0]) + 0.7152 * float(rgb[1]) + 0.0722 * float(rgb[2])


def _tinted(colour, tint) -> tuple[float, float, float]:
    if not tint:
        return (float(colour[0]), float(colour[1]), float(colour[2]))
    return tuple(float(c) * float(t) for c, t in zip(colour, tint))


def albedo_gain_for(mean_lum: float, slug: str, base_rgb=None) -> tuple[float, bool]:
    """``(gain, clamped)``: the gain that brings a map of mean linear luminance
    ``mean_lum`` to the luminance of the slug's flat colour (``base_rgb`` when given), clamped to
    ``ALBEDO_GAIN_RANGE``; ``clamped`` says whether the clamp changed it."""
    target = luminance(base_rgb if base_rgb is not None else flat_colour(slug))
    if mean_lum <= 1e-4 or target <= 0:
        return 1.0, False
    wanted = target / mean_lum
    gain = min(ALBEDO_GAIN_RANGE[1], max(ALBEDO_GAIN_RANGE[0], wanted))
    return round(gain, 4), gain != wanted


def texture_mean_luminance(image) -> float | None:
    """Mean scene-linear luminance (Rec.709 weights, the ones RGB to BW uses
    in the default colour config) of an albedo image, or None when the
    pixels cannot be read."""
    try:
        import numpy as np
        px = np.empty(len(image.pixels), dtype=np.float32)
        image.pixels.foreach_get(px)   # RGBA floats
        px = px.reshape(-1, 4)[:, :3]
        if len(px) > 262_144:          # a 512x512 sample is plenty for a mean
            px = px[:: max(1, len(px) // 262_144)]
        # image.pixels of a byte image are the stored (sRGB-encoded) values, not
        # scene-linear ones: decode before averaging (checked on Blender 5.2.2).
        if image.colorspace_settings.name == "sRGB":
            px = np.where(px > 0.04045, ((px + 0.055) / 1.055) ** 2.4, px / 12.92)
        mean = px.mean(axis=0)
        return float(0.2126 * mean[0] + 0.7152 * mean[1] + 0.0722 * mean[2])
    except Exception:  # noqa: BLE001 - never fail a build over a brightness tweak
        return None


def albedo_gain(image, slug: str) -> tuple[float, float]:
    """``(gain, mean_luminance)`` of an albedo image for a texture-mode slug
    (``albedo_gain_for``); ``(1.0, -1.0)`` when the image cannot be read."""
    mean_lum = texture_mean_luminance(image)
    if mean_lum is None:
        return 1.0, -1.0
    gain, _ = albedo_gain_for(mean_lum, slug)
    return gain, round(mean_lum, 4)


def _cap(nodes, links, colour_socket):
    """VectorMath MINIMUM against (MAX_ALBEDO, MAX_ALBEDO, MAX_ALBEDO); returns its output."""
    cap = nodes.new("ShaderNodeVectorMath")
    cap.operation = "MINIMUM"
    links.new(colour_socket, cap.inputs[0])
    cap.inputs[1].default_value = (MAX_ALBEDO, MAX_ALBEDO, MAX_ALBEDO)
    return cap.outputs["Vector"]


def _flat_detail_albedo(nodes, links, texture_colour, bsdf, colour, detail: float, mean_lum: float) -> None:
    """Flat albedo mode: ``min(colour * (lum(tex) / mean_lum * detail + 1 - detail), 0.9)`` into Base Color.

    Only the texture's luminance reaches the material, so a tan photo of a
    white wall gives a white wall with 'detail' of its light/dark variation."""
    bw = nodes.new("ShaderNodeRGBToBW")
    links.new(texture_colour, bw.inputs["Color"])
    ratio = nodes.new("ShaderNodeMath")
    ratio.operation = "DIVIDE"
    links.new(bw.outputs["Val"], ratio.inputs[0])
    ratio.inputs[1].default_value = float(mean_lum)
    mod = nodes.new("ShaderNodeMath")
    mod.operation = "MULTIPLY_ADD"          # Value * Value_001 + Value_002
    links.new(ratio.outputs["Value"], mod.inputs[0])
    mod.inputs[1].default_value = float(detail)
    mod.inputs[2].default_value = 1.0 - float(detail)
    scale = nodes.new("ShaderNodeVectorMath")
    scale.operation = "SCALE"
    scale.inputs["Vector"].default_value = tuple(float(c) for c in colour)
    links.new(mod.outputs["Value"], scale.inputs["Scale"])
    links.new(_cap(nodes, links, scale.outputs["Vector"]), bsdf.inputs["Base Color"])


def _image_node(nodes, path: str, colorspace: str):
    import bpy

    path = os.path.abspath(path)
    image = bpy.data.images.load(path, check_existing=True)
    try:
        image.colorspace_settings.name = colorspace
    except TypeError:  # the OCIO config of this build lacks the alias
        pass
    node = nodes.new("ShaderNodeTexImage")
    node.image = image
    node.projection = "FLAT"
    node.extension = "REPEAT"
    return node


def add_unverified_overlay(mat) -> bool:
    """Red stripes over whatever shader feeds the Material Output of an
    existing material (an imported furniture asset of an unverified piece,
    docs/milestone4.md §2). Returns False when the material has no surface
    link to overlay (left as it is), and when the stripes are off (M11 D3, ``set_markers``)."""
    if not markers_on():
        return False
    if not mat.use_nodes:
        mat.use_nodes = True
    tree = mat.node_tree
    out = next((n for n in tree.nodes if n.bl_idname == "ShaderNodeOutputMaterial" and n.is_active_output), None)
    out = out or next((n for n in tree.nodes if n.bl_idname == "ShaderNodeOutputMaterial"), None)
    if out is None or not out.inputs["Surface"].links:
        return False
    _stripes_over_socket(mat, out.inputs["Surface"].links[0].from_socket, out)
    return True


def _add_unverified_stripes(mat, base_shader, out):
    """Mix red emission stripes over the base shader node's first output."""
    _stripes_over_socket(mat, base_shader.outputs[0], out)


def _stripes_over_socket(mat, shader_socket, out):
    """Mix red emission stripes (world-space bands, 10 cm period) over ``shader_socket``.

    The mix factor is stripe x Light Path 'Is Camera Ray' (docs/milestone6.md
    §5 row 1): the camera sees the stripes, every other ray sees the piece's
    own shader, so the red emission no longer lights the room (in a small
    room it did, and the auto white balance then turned the view teal). The
    material's emission sampling is off (``cycles.emission_sampling = NONE``):
    an emission no light path can see would only take light samples from the
    real lights."""
    tree = mat.node_tree
    nodes, links = tree.nodes, tree.links
    mat.cycles.emission_sampling = "NONE"
    coord = nodes.new("ShaderNodeTexCoord")
    wave = nodes.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "DIAGONAL"
    wave.wave_profile = "SAW"
    wave.inputs["Scale"].default_value = 10.0
    wave.inputs["Distortion"].default_value = 0.0
    links.new(coord.outputs["Object"], wave.inputs["Vector"])
    step = nodes.new("ShaderNodeMath")
    step.operation = "GREATER_THAN"
    step.inputs[1].default_value = 0.5
    links.new(wave.outputs["Fac"], step.inputs[0])
    emit = nodes.new("ShaderNodeEmission")
    emit.inputs["Color"].default_value = (*UNVERIFIED_RED, 1.0)
    emit.inputs["Strength"].default_value = 3.0
    path = nodes.new("ShaderNodeLightPath")
    camera_only = nodes.new("ShaderNodeMath")
    camera_only.operation = "MULTIPLY"
    camera_only.name = STRIPES_CAMERA_NODE
    links.new(step.outputs["Value"], camera_only.inputs[0])
    links.new(path.outputs["Is Camera Ray"], camera_only.inputs[1])
    mix = nodes.new("ShaderNodeMixShader")
    links.new(camera_only.outputs["Value"], mix.inputs["Fac"])
    links.new(shader_socket, mix.inputs[1])
    links.new(emit.outputs["Emission"], mix.inputs[2])
    links.new(mix.outputs["Shader"], out.inputs["Surface"])


WINDOW_GLASS_IOR = 1.45


def window_glass_material(name: str, ior: float = WINDOW_GLASS_IOR):
    """Window pane seen as glass only on the camera's paths (docs/milestone5.md §2.1).

    Mix Shader with factor = Math MAXIMUM of the Light Path outputs 'Is
    Camera Ray' and 'Is Singular Ray': Glass BSDF (IOR 1.45, roughness 0) for
    camera rays and for rays that left a sharp (singular) refraction or
    reflection, Transparent BSDF for every other ray.

    - The camera ray refracts at the pane's room face and becomes a singular
      transmission ray, so the far face refracts it back: the view through
      the pane only moves by a fraction of the 6 mm thickness, as through
      real glass. With 'Is Camera Ray' alone the far face was transparent
      and bent the whole outside view (23 px of 200 at 17 degrees); with
      'Is Transmission Ray' instead of 'Is Singular Ray' the reflection at
      the far face left unrefracted (a second, misplaced reflection of a
      lamp) and rough transmission rays saw glass (+20 % light behind a
      frosted panel).
    - Shadow rays and diffuse / rough glossy / rough transmission rays see
      the Transparent BSDF: light sampling and BSDF sampling agree and see
      an open hole, so the sun is not over-counted, the sky is not lost in
      refractive caustics and light portals stay unbiased (measured on
      Blender 5.2.2: interior light equal to an open hole within 0.2 %, also
      behind a frosted panel). Singular paths take no light samples, so the
      glass they see adds no bias.
    - Camera rays stop at the pane: the depth and index passes still record
      the window and the camera still sees reflections.
    tests/test_blender_glass.py renders all four properties."""
    import bpy

    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    nodes, links = tree.nodes, tree.links
    for n in list(nodes):
        if n.bl_idname == "ShaderNodeBsdfPrincipled":
            nodes.remove(n)
    out = nodes.get("Material Output")
    glass = nodes.new("ShaderNodeBsdfGlass")
    glass.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    glass.inputs["Roughness"].default_value = 0.0
    glass.inputs["IOR"].default_value = ior
    transparent = nodes.new("ShaderNodeBsdfTransparent")
    path = nodes.new("ShaderNodeLightPath")
    mix = nodes.new("ShaderNodeMixShader")
    # 1 -> Glass (second shader): the camera ray, and the camera's ray after a sharp
    # refraction or reflection (by this pane's room face, so the far face refracts it back).
    glass_rays = nodes.new("ShaderNodeMath")
    glass_rays.operation = "MAXIMUM"
    links.new(path.outputs["Is Camera Ray"], glass_rays.inputs[0])
    links.new(path.outputs["Is Singular Ray"], glass_rays.inputs[1])
    links.new(glass_rays.outputs["Value"], mix.inputs["Fac"])
    links.new(transparent.outputs["BSDF"], mix.inputs[1])
    links.new(glass.outputs["BSDF"], mix.inputs[2])
    links.new(mix.outputs["Shader"], out.inputs["Surface"])
    mat.surface_render_method = "BLENDED"
    mat["wenart_glass"] = "camera_only"
    return mat


def thin_glass_material(name: str, roughness: float = 0.0, ior: float = 1.45):
    """Thin pane without refraction: Transparent BSDF mixed with a Glossy BSDF by
    Fresnel (about 4 % reflection head-on, more at grazing angles). Cycles writes
    the depth, normal and index passes at the first surface whose alpha is at or
    above the view layer's ``pass_alpha_threshold`` (0.5); this pane's alpha is
    the Fresnel factor, so the passes see through it except at grazing angles.
    Shadow rays see it as fully transparent. Shower panels keep this pane in
    Milestone 5; windows use ``window_glass_material``."""
    import bpy

    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    nodes, links = tree.nodes, tree.links
    for n in list(nodes):
        if n.bl_idname == "ShaderNodeBsdfPrincipled":
            nodes.remove(n)
    out = nodes.get("Material Output")
    fresnel = nodes.new("ShaderNodeFresnel")
    fresnel.inputs["IOR"].default_value = ior
    glossy = nodes.new("ShaderNodeBsdfAnisotropic")  # the Glossy BSDF (merged with Anisotropic in 4.0)
    glossy.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    glossy.inputs["Roughness"].default_value = roughness
    transparent = nodes.new("ShaderNodeBsdfTransparent")
    pane = nodes.new("ShaderNodeMixShader")
    links.new(fresnel.outputs["Fac"], pane.inputs["Fac"])
    links.new(transparent.outputs["BSDF"], pane.inputs[1])
    links.new(glossy.outputs["BSDF"], pane.inputs[2])
    path = nodes.new("ShaderNodeLightPath")
    shadow = nodes.new("ShaderNodeBsdfTransparent")
    mix = nodes.new("ShaderNodeMixShader")
    links.new(path.outputs["Is Shadow Ray"], mix.inputs["Fac"])
    links.new(pane.outputs["Shader"], mix.inputs[1])
    links.new(shadow.outputs["BSDF"], mix.inputs[2])
    links.new(mix.outputs["Shader"], out.inputs["Surface"])
    mat.surface_render_method = "BLENDED"
    return mat


# --------------------------------------------------------------------------
# World
# --------------------------------------------------------------------------

MOOD_STRENGTH = {"warm daylight": 1.0, "cool daylight": 1.2, "golden evening": 0.8,
                 "overcast": 1.4, "night": 0.05}
# Milestone 10: the four new moods take the vocabulary's ``hdri_strength`` (bright noon 1.0, blue hour 0.8, cloudy
# soft 1.4, interior evening 0.5; wenart/style/finishes.py LIGHTING).


def world_strength_record(strength: float, strength_gain: float = 1.0) -> tuple[float, dict]:
    """``(Background Strength, extra record keys)`` of the interior world (pure; pod P6a, the interior sky A/B):
    ``strength`` times ``strength_gain`` (``lighting.interior_sky_gain``) with ``{"strength_base", "strength_gain",
    "sky_stops"}``; a gain of exactly 1.0 (production) returns ``strength`` untouched and no keys, so the world and
    its manifest record stay as they were. A gain that is not a positive finite number raises ValueError."""
    gain = float(strength_gain)
    if not math.isfinite(gain) or gain <= 0.0:
        raise ValueError(f"interior world strength gain must be a positive number, not {strength_gain!r}")
    if gain == 1.0:
        return strength, {}
    return strength * gain, {"strength_base": strength, "strength_gain": round(gain, 6),
                             "sky_stops": round(math.log2(gain), 6)}


def world_nodes(scene, lighting: dict, hdri_path: str | None, strength_gain: float = 1.0) -> dict:
    """World from the style: HDRI when a file is available, else a physical
    sky (sky texture, multiple scattering) at the style's sun position.
    Returns what was used for the manifest.

    Pod P6a (22 Oct 2026): ``strength_gain`` (``lighting.interior_sky_gain``, the ``sky*`` light variants) multiplies
    the Background Strength of this world only (``world_strength_record``); the record then carries
    ``strength_base``, ``strength_gain`` and ``sky_stops``. 1.0 (the default) builds the world as before.

    Round 4 check of the interior HDRI against the 1000 W/m² sun lamp (bpy 5.2.2, the measurement of the exterior
    pair): Poly Haven's kloppenheim_06 (1k, the warm-daylight HDRI of real02/03/04) at Strength 1.0 puts 2.54 W/m²
    on a horizontal plane, 0.0044 of the lamp's direct light there (573.6 W/m² at 35 degrees); the clear-sky pair
    of the exterior sky gives 0.166 (``exterior_sky_strength``), about 38 x (5.2 stops) more sky. Not changed: the
    P1 sun1000 sheets (results/review/m13_p1/levers, decided in docs/milestone13.md §14.3) were rendered with this
    balance and the lead read them as right (§14.3: "a real sun patch through the window, clean contrast, warm;
    sun1000 reads most natural, no clipping seen"), and the P1 EV numbers, the EV cap and the rig gain rest on it.
    The HDRI is a look (its own units, no real sun disc: the 3 degrees around its brightest pixel hold 0.1 % of its
    irradiance), not a calibrated sky. A brighter interior HDRI is a lever for a pod A/B, not a silent change."""
    import bpy

    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    tree = world.node_tree
    nodes, links = tree.nodes, tree.links
    for n in list(nodes):
        nodes.remove(n)
    out = nodes.new("ShaderNodeOutputWorld")
    bg = nodes.new("ShaderNodeBackground")
    links.new(bg.outputs["Background"], out.inputs["Surface"])
    mood = str(lighting.get("mood", "")).lower()
    strength, gain_record = world_strength_record(MOOD_STRENGTH.get(mood, _MOOD_HDRI_STRENGTH.get(mood, 1.0)),
                                                  strength_gain)
    bg.inputs["Strength"].default_value = strength
    azimuth = float(lighting.get("sun_azimuth_deg", 210.0))
    elevation = float(lighting.get("sun_elevation_deg", 35.0))

    if hdri_path and os.path.exists(hdri_path):
        env = nodes.new("ShaderNodeTexEnvironment")
        env.image = bpy.data.images.load(os.path.abspath(hdri_path), check_existing=True)
        coord = nodes.new("ShaderNodeTexCoord")
        mapping = nodes.new("ShaderNodeMapping")
        # Turn the HDRI so its brightest region sits roughly at the style azimuth.
        mapping.inputs["Rotation"].default_value = (0.0, 0.0, math.radians(-azimuth))
        links.new(coord.outputs["Generated"], mapping.inputs["Vector"])
        links.new(mapping.outputs["Vector"], env.inputs["Vector"])
        links.new(env.outputs["Color"], bg.inputs["Color"])
        return {"kind": "hdri", "file": hdri_path, "strength": strength, **gain_record}

    sky = nodes.new("ShaderNodeTexSky")
    sky.sky_type = "MULTIPLE_SCATTERING"
    sky.sun_disc = False  # the sun lamp carries the direct light
    sky.sun_elevation = math.radians(max(1.0, elevation))
    # The sky's sun at the lamp's compass azimuth (sky_sun_rotation_rad: measured on 5.2.2, round 3; the old
    # ``90 - azimuth`` was 30 degrees off at real03's 210).
    sky.sun_rotation = sky_sun_rotation_rad(azimuth)
    links.new(sky.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength * 0.5
    if gain_record:
        gain_record = dict(gain_record, strength_base=gain_record["strength_base"] * 0.5)
    return {"kind": "sky", "file": None, "strength": strength * 0.5, **gain_record}


EXTERIOR_WORLD = "wenart_world_exterior"
# The physical sky of the exterior views (Blender 5.2 ShaderNodeTexSky, sky_type MULTIPLE_SCATTERING: the Nishita
# model of Blender 4.x, checked with bpy.types.ShaderNodeTexSky.bl_rna on 5.2.2; enum SINGLE_SCATTERING,
# MULTIPLE_SCATTERING, PREETHAM, HOSEK_WILKIE). Clean air, a little haze.
# ``strength_factor`` is the Milestone 11 sky strength (x the mood's strength). Since round 4 it is used only when no
# sun lamp is given or the mood has no sun (``exterior_sky_strength``); a lit scene's sky strength comes from the
# lamp through the measured sky/sun pair below.
EXTERIOR_SKY = {"sky_type": "MULTIPLE_SCATTERING", "air_density": 1.0, "aerosol_density": 1.0, "ozone_density": 1.0,
                "altitude": 0.0, "strength_factor": 0.5}
# Milestone 13: the sun disc of the exterior sky (bpy.types.ShaderNodeTexSky: sun_disc "Include the sun itself in the
# output", sun_size "Size of sun disc" default 0.00951204 rad = 0.545 degrees, sun_intensity "Strength of Sun" in
# [0, 1000] default 1.0; the manual: "Single and Multiple Scattering skies are very bright by default (hence
# accurate)"). With the disc on, the sky carries the direct sun of the exterior views and render.py hides the sun
# lamp under that world (select_world), so nothing doubles it; the disc's intensity is 1.0 (the model's own physical
# scale: the manual's clear sky is 1000 W/m², EXTERIOR_SUN_DISC_REFERENCE_WM2) scaled by the lamp's strength over
# that reference, so the exterior sun follows SUN_STRENGTH_WM2 as the interior one does. tests/gpu/test_m13_light.py
# measures the disc's irradiance against the lamp's and the lead corrects the reference from P1.
SUN_DISC_SIZE_DEG = 0.545
EXTERIOR_SUN_DISC_REFERENCE_WM2 = 1000.0

# Round 4 (16 Oct 2026; docs/milestone13.md §14.8: "the exterior sky world is about 4 stops too dark against the
# 1000 W/m² lamp"): the strength of the exterior sky comes from the physics, not from taste.
#
# 1. The MULTIPLE_SCATTERING sky and its own sun are one physical pair: one atmosphere (the air, aerosol and ozone
#    densities of EXTERIOR_SKY) scatters the sky light and dims the sun. Per sun elevation, SKY_SUN_TABLE holds
#    (elevation_deg, sun_ratio, dome_ratio): sun_ratio = the sky's own sun (sun_intensity 1, Background Strength 1)
#    on a white plane facing it, over a SKY_PAIR_REFERENCE_WM2 sun lamp on the same plane; dome_ratio = the sky
#    without the disc (Strength 1) on a horizontal plane, over the same lamp facing its plane. Measured on bpy 5.2.2
#    (CPU Cycles, 256 samples, the Diffuse Direct pass of a white Lambert plane, the median pixel; 16 Oct 2026).
#    The 35-degree row repeats the P1 measurement SUN_DISC_RATIO 0.129 (tests/gpu/test_m13_light.py).
# 2. The world strength whose sun equals the lamp is k = lamp_wm2 / (SKY_PAIR_REFERENCE_WM2 x sun_ratio(e)):
#    7.71 for the 1000 W/m² lamp at 35 degrees, x15.4 the Milestone 11 value 0.5. The P3 pre-flight (agent B)
#    found that about x15.5 turns the real04 ext_7 sky band at the metered EV -7.67 from 14/255 (nearly black, grey
#    only through the haze) into a blue (106, 130, 146).
# 3. The visible disc keeps its image brightness: sky_sun_intensity divides by k, so k x sun_intensity stays
#    lamp_wm2 / EXTERIOR_SUN_DISC_REFERENCE_WM2 (the P1 disc); the disc stays camera-only and the lamp stays the one
#    direct sun (round 3).
# 4. Check: the sky's diffuse light over the sun's direct light on a horizontal plane is
#    dome_ratio / (sun_ratio x sin e), a property of the pair whatever k is: 0.166 at 35 degrees, 0.11-0.22 from 25
#    to 85 degrees, higher for a low sun (0.45 at 12 degrees). The clear-sky models of pvlib 0.13.1
#    (raw.githubusercontent.com/pvlib/pvlib-python/main/pvlib/clearsky.py, ``bird`` and ``ineichen``; run on CPU,
#    sea level) give DHI / (DNI x sin e) at 35 degrees of 0.149 (Bird, AOD500 0.05), 0.212 (Bird, AOD500 0.1) and
#    0.173 (Ineichen-Perez, Linke turbidity 3); from 25 to 85 degrees 0.095-0.194 (Bird, AOD500 0.05), 0.129-0.282
#    (Bird, AOD500 0.1) and 0.119-0.220 (Ineichen-Perez, TL 3). The pair lies between Bird at AOD500 0.05 and 0.1
#    at every row from 10 to 85 degrees (pinned in tests/test_m13_light.py), and inside the usual clear-sky range
#    CLEAR_SKY_DIFFUSE_RANGE (about 0.1-0.25). Below CLEAR_SKY_RANGE_MIN_ELEVATION_DEG a clear
#    sky's share rises (Bird at 12 degrees: 0.35-0.55), so the range is checked only above it.
# 5. Moods: the mood's sky strength over its sun factor (MOOD_STRENGTH over the style's sun_strength / 3 W/m²) keeps
#    the Milestone 11 balance between the moods; warm daylight (every PoC project) is exactly the pair. Without a
#    lamp (no ``sun_wm2``, a sunless mood) there is no sun to pair with: the Milestone 11 strength stays.
# The table is valid for EXTERIOR_SKY's air (SKY_TABLE_AIR, pinned in tests/test_m13_light.py): re-measure it when
# the air changes. tests/gpu/test_m13_light.py re-measures rows with the same method (test_sky_sun_table_rows_
# reproduce: 12, 45 and 65 degrees, the elevations of the golden-evening, overcast and bright-noon moods; its
# script takes any elevation list) and its sun-disc test checks the 35-degree pair in the production world.
SKY_PAIR_REFERENCE_WM2 = 1000.0
SKY_TABLE_AIR = {"air_density": 1.0, "aerosol_density": 1.0, "ozone_density": 1.0, "altitude": 0.0}
SKY_SUN_TABLE: tuple[tuple[float, float, float], ...] = (
    (5.0, 0.0408, 0.00469), (10.0, 0.0757, 0.00722), (12.0, 0.0853, 0.00796), (15.0, 0.0967, 0.00887),
    (20.0, 0.1098, 0.01003), (25.0, 0.1187, 0.01095), (30.0, 0.1250, 0.01172), (35.0, 0.1297, 0.01238),
    (40.0, 0.1331, 0.01296), (45.0, 0.1359, 0.01348), (55.0, 0.1397, 0.01434), (65.0, 0.1421, 0.01499),
    (75.0, 0.1435, 0.01542), (85.0, 0.1442, 0.01564),
)
SKY_TABLE_SOURCE = ("bpy 5.2.2 CPU Cycles, 16 Oct 2026: Diffuse Direct of a white plane, the MULTIPLE_SCATTERING "
                    "sky (EXTERIOR_SKY air) against a 1000 W/m2 sun lamp (round 4)")
CLEAR_SKY_DIFFUSE_RANGE = (0.10, 0.25)
CLEAR_SKY_RANGE_MIN_ELEVATION_DEG = 25.0
CLEAR_SKY_SOURCE = ("pvlib 0.13.1 clear-sky models at sea level (pvlib/clearsky.py bird, ineichen): DHI / (DNI x "
                    "sin e) at 35 degrees 0.149-0.212 (Bird, AOD500 0.05-0.1), 0.173 (Ineichen-Perez, Linke "
                    "turbidity 3); 25-85 degrees 0.095-0.282 (Bird), 0.119-0.220 (Ineichen-Perez)")


def sky_pair_ratios(elevation_deg: float) -> tuple[float, float]:
    """``(sun_ratio, dome_ratio)`` of the exterior sky at a sun elevation (pure): ``SKY_SUN_TABLE`` read linearly
    between its rows and held at its first and last rows outside them (5 and 85 degrees)."""
    e = float(elevation_deg)
    rows = SKY_SUN_TABLE
    if e <= rows[0][0]:
        return rows[0][1], rows[0][2]
    for (e0, s0, d0), (e1, s1, d1) in zip(rows, rows[1:]):
        if e <= e1:
            t = (e - e0) / (e1 - e0)
            return s0 + t * (s1 - s0), d0 + t * (d1 - d0)
    return rows[-1][1], rows[-1][2]


def exterior_sky_strength(sun_wm2: float | None, elevation_deg: float, mood_strength: float = 1.0,
                          mood_factor: float = 1.0) -> dict:
    """The exterior sky's Background Strength for a sun lamp of ``sun_wm2`` at ``elevation_deg`` (pure; the
    derivation is the comment above ``SKY_SUN_TABLE``). ``mood_strength`` is the mood's sky strength
    (``MOOD_STRENGTH``, 1.0 for warm daylight), ``mood_factor`` the lamp's mood factor (the style's sun_strength
    over 3 W/m², ``lighting.sun_strength_wm2``; 1.0 for warm daylight). Returns the record the scene manifest keeps:
    ``strength``, ``rule`` ("sun pair" or "m11"), the table's ``sun_ratio`` / ``dome_ratio`` at the elevation,
    ``sky_sun_wm2`` (the sky's own sun at Strength 1), ``mood_balance``, the horizontal diffuse-to-direct ratio of
    the pair and of this sky (``pair_diffuse_to_direct``, ``diffuse_to_direct``), the clear-sky range and whether
    the pair lies in it (None below ``CLEAR_SKY_RANGE_MIN_ELEVATION_DEG``), and the sources."""
    sun_ratio, dome_ratio = sky_pair_ratios(elevation_deg)
    sky_sun = SKY_PAIR_REFERENCE_WM2 * sun_ratio
    sin_e = math.sin(math.radians(max(1.0, float(elevation_deg))))
    pair_ratio = dome_ratio / (sun_ratio * sin_e)
    rec = {"elevation_deg": float(elevation_deg), "sun_ratio": round(sun_ratio, 6), "dome_ratio": round(dome_ratio, 6),
           "sky_sun_wm2": round(sky_sun, 4), "lamp_wm2": None if sun_wm2 is None else float(sun_wm2),
           "mood_strength": float(mood_strength), "mood_factor": float(mood_factor),
           "pair_diffuse_to_direct": round(pair_ratio, 4), "clear_sky_range": list(CLEAR_SKY_DIFFUSE_RANGE),
           "pair_in_clear_sky_range": (CLEAR_SKY_DIFFUSE_RANGE[0] <= pair_ratio <= CLEAR_SKY_DIFFUSE_RANGE[1])
           if float(elevation_deg) >= CLEAR_SKY_RANGE_MIN_ELEVATION_DEG else None,
           "table_source": SKY_TABLE_SOURCE, "clear_sky_source": CLEAR_SKY_SOURCE}
    if sun_wm2 is None or float(sun_wm2) <= 0.0 or float(mood_factor) <= 0.0:
        strength = float(mood_strength) * EXTERIOR_SKY["strength_factor"]
        rec.update(rule="m11", strength=round(strength, 6), mood_balance=None, diffuse_to_direct=None,
                   reason="no sun lamp to pair the sky with: the Milestone 11 strength (0.5 x the mood's)")
        return rec
    balance = float(mood_strength) / float(mood_factor)
    strength = balance * float(sun_wm2) / sky_sun
    rec.update(rule="sun pair", strength=round(strength, 6), mood_balance=round(balance, 6),
               diffuse_to_direct=round(balance * pair_ratio, 4),
               reason=f"the sky's own sun equals the {float(sun_wm2):g} W/m2 lamp: {float(sun_wm2):g} / "
                      f"({SKY_PAIR_REFERENCE_WM2:g} x {sun_ratio:.4f}) x the mood balance {balance:.3g}")
    return rec


def sky_sun_rotation_rad(azimuth_deg: float) -> float:
    """The ``ShaderNodeTexSky.sun_rotation`` (radians) that puts the sky's sun at the compass azimuth
    ``azimuth_deg`` (clockwise from +Y, the frame of ``lighting.sun_direction``), pure. Measured on bpy 5.2.2
    (15 Oct 2026, equirectangular renders of the disc against an emissive sphere placed with ``sun_direction``):
    rotation 0 puts the sun at +Y, 90 degrees at +X (east), 180 at -Y, 270 at -X, i.e. ``sun_rotation`` is the
    compass azimuth itself. The Milestone 3-11 formula ``90 - azimuth`` agreed with the lamp only at 45 degrees
    (real02's azimuth) and put real03's sun (210) at 240, 30 degrees off the lamp's shadows."""
    return math.radians(float(azimuth_deg))


def sky_sun_intensity(sun_wm2: float | None, reference_wm2: float = EXTERIOR_SUN_DISC_REFERENCE_WM2,
                      world_strength: float = 1.0) -> float:
    """The sky's ``sun_intensity`` for a sun lamp of ``sun_wm2`` (pure): ``sun_wm2 / (reference_wm2 x
    world_strength)`` clamped to the node's range [0, 1000]; 1.0 (the model's own scale) when the lamp strength is
    not given. ``world_strength`` is the Background node's Strength of the exterior world (since round 4
    ``exterior_sky_strength``, before it ``EXTERIOR_SKY`` ``strength_factor`` x the mood's strength): it multiplies
    the whole sky texture, the disc included, so without it the disc would deliver ``world_strength x sun_wm2`` and
    vary by mood (T5 review, 15 Oct 2026); with it the disc's image brightness stays ``sun_wm2 / reference_wm2``."""
    if sun_wm2 is None:
        return 1.0
    scale = float(reference_wm2) * max(float(world_strength), 1e-6)
    return round(min(1000.0, max(0.0, float(sun_wm2) / scale)), 6)


def exterior_world(lighting: dict, sun_disc: bool = False, sun_elevation_deg: float | None = None,
                   sun_azimuth_deg: float | None = None, sun_wm2: float | None = None,
                   disc_camera_only: bool = True) -> dict:
    """The world of the exterior views (pure record; docs/milestone11.md §1.1 E13): a physical sky whose sun stands
    where the lamp is (``sun_elevation_deg``, ``sun_azimuth_deg`` in the building frame; the arguments win over the
    ``lighting`` keys), so the sky's bright side, the shadows and the light agree; the HDRI of the style (its own low
    sun and its own ground showed in the exterior views) stays for the interior views.

    Milestone 13: ``sun_disc`` puts the sun itself into the sky (``sun_intensity`` from ``sky_sun_intensity``,
    ``sun_size_deg``); the record's ``direct_sun`` says who carries the direct light. Round 3 (§14.3):
    ``disc_camera_only`` (the default) shows the disc to camera rays only (``world_mix``: a Mix Shader on the
    Light Path 'Is Camera Ray' between the sky with the disc and the same sky without it), so the lamp is the one
    direct sun (``direct_sun: "lamp"``, ``sun_disc_camera_only: True``); ``False`` is the P1 world (the disc for
    every ray, ``"sky disc"``, the lamp hidden under it). Without a disc the Milestone 11 world (``"lamp"``).

    Round 4: ``strength`` comes from ``exterior_sky_strength`` (the sky whose own sun equals the lamp of
    ``sun_wm2``, the measured pair of ``SKY_SUN_TABLE``; the Milestone 11 0.5 x the mood's strength without a
    lamp); the record keeps the derivation as ``sky_calibration``."""
    from wenart.blender.lighting import sun_strength_wm2

    mood = str(lighting.get("mood", "")).lower()
    mood_strength = MOOD_STRENGTH.get(mood, _MOOD_HDRI_STRENGTH.get(mood, 1.0))
    elevation = float(lighting.get("sun_elevation_deg", 35.0) if sun_elevation_deg is None else sun_elevation_deg)
    azimuth = float(lighting.get("sun_azimuth_deg", 210.0) if sun_azimuth_deg is None else sun_azimuth_deg)
    # the lamp's mood factor (the style's sun_strength over 3 W/m²), the one formula of lighting.sun_strength_wm2
    _, mood_factor = sun_strength_wm2(lighting, {"sun_wm2": 1.0})
    calibration = exterior_sky_strength(sun_wm2, elevation, mood_strength, mood_factor)
    strength = calibration["strength"]
    rec = {"kind": "sky", "name": EXTERIOR_WORLD, "sky_type": EXTERIOR_SKY["sky_type"], "file": None,
           "strength": strength, "sun_elevation_deg": elevation, "sun_azimuth_deg": azimuth, "sun_disc": bool(sun_disc),
           "reason": "exterior views: a physical sky matched to the sun lamp (E13)", "sky_calibration": calibration}
    if sun_disc:
        rec.update(sun_intensity=sky_sun_intensity(sun_wm2, world_strength=strength), sun_size_deg=SUN_DISC_SIZE_DEG,
                   sun_disc_reference_wm2=EXTERIOR_SUN_DISC_REFERENCE_WM2, sun_lamp_wm2=sun_wm2,
                   sun_disc_world_strength=strength, sun_disc_camera_only=bool(disc_camera_only))
        if disc_camera_only:
            rec.update(direct_sun="lamp",
                       world_mix={"node": "ShaderNodeMixShader", "factor": "ShaderNodeLightPath 'Is Camera Ray'",
                                  "camera_rays": "ShaderNodeTexSky with sun_disc (the disc in the image)",
                                  "other_rays": "the same ShaderNodeTexSky without sun_disc (no second sun)"},
                       reason="exterior views: a daytime physical sky whose sun disc only the camera sees (Light "
                              "Path 'Is Camera Ray' mix of the sky with and without the disc); the sun lamp is the "
                              "one direct sun (Milestone 13 round 3, docs/milestone13.md section 14.3)")
        else:
            rec.update(direct_sun="sky disc",
                       reason="exterior views: a daytime physical sky with the sun disc; the sun lamp is hidden "
                              "under this world so the sky does not double the sun (Milestone 13 K5, the P1 world)")
    else:
        rec["direct_sun"] = "lamp"
    return rec


def _sky_texture_node(nodes, rec: dict, disc: bool):
    """One ``ShaderNodeTexSky`` of the exterior world record (bpy): the sun where the lamp stands, the disc on or
    off (``disc``), the air of ``EXTERIOR_SKY``."""
    sky = nodes.new("ShaderNodeTexSky")
    sky.sky_type = EXTERIOR_SKY["sky_type"]
    sky.sun_disc = bool(disc)
    if disc:
        sky.sun_intensity = float(rec["sun_intensity"])
        sky.sun_size = math.radians(SUN_DISC_SIZE_DEG)
    sky.sun_elevation = math.radians(max(1.0, rec["sun_elevation_deg"]))
    sky.sun_rotation = sky_sun_rotation_rad(rec["sun_azimuth_deg"])     # the disc where the lamp's shadows point
    for key in ("air_density", "aerosol_density", "ozone_density", "altitude"):
        if hasattr(sky, key):
            setattr(sky, key, EXTERIOR_SKY[key])
    return sky


def exterior_world_nodes(scene, lighting: dict, sun_disc: bool = True, sun_elevation_deg: float | None = None,
                         sun_azimuth_deg: float | None = None, sun_wm2: float | None = None,
                         disc_camera_only: bool = True) -> dict:
    """Make the exterior world (``exterior_world``) as its own Blender world (not assigned to the scene: render.py
    switches to it for exterior cameras, ``scene["wenart_world_exterior"]``). Scene properties for render.py:
    ``wenart_world_exterior_sun_disc`` (the sky carries a disc) and ``wenart_world_exterior_disc_camera_only``
    (round 3: the disc is for camera rays only, so the sun lamp stays shown; without it the lamp is hidden under
    this world, the P1 behaviour).

    Node names checked on bpy 5.2.2 (15 Oct 2026): ShaderNodeLightPath output 'Is Camera Ray'; ShaderNodeMixShader
    inputs 'Factor' (identifier 'Fac', index 0) and two 'Shader' inputs (indices 1 and 2: factor 0 takes the first,
    1 the second), output 'Shader'; ShaderNodeTexSky sun_disc / sun_intensity / sun_elevation / sun_rotation /
    sun_size; ShaderNodeBackground inputs 'Color', 'Strength'."""
    import bpy

    rec = exterior_world(lighting, sun_disc=sun_disc, sun_elevation_deg=sun_elevation_deg,
                         sun_azimuth_deg=sun_azimuth_deg, sun_wm2=sun_wm2, disc_camera_only=disc_camera_only)
    world = bpy.data.worlds.get(EXTERIOR_WORLD) or bpy.data.worlds.new(EXTERIOR_WORLD)
    world.use_nodes = True
    tree = world.node_tree
    nodes, links = tree.nodes, tree.links
    for n in list(nodes):
        nodes.remove(n)
    out = nodes.new("ShaderNodeOutputWorld")
    bg = nodes.new("ShaderNodeBackground")
    bg.name = "wenart_sky_camera"
    sky = _sky_texture_node(nodes, rec, disc=bool(rec["sun_disc"]))
    links.new(sky.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = rec["strength"]
    if rec["sun_disc"] and rec.get("sun_disc_camera_only"):
        # Every ray but the camera's sees the sky without the disc: the lamp is the one direct sun.
        sky_lit = _sky_texture_node(nodes, rec, disc=False)
        bg_lit = nodes.new("ShaderNodeBackground")
        bg_lit.name = "wenart_sky_lighting"
        links.new(sky_lit.outputs["Color"], bg_lit.inputs["Color"])
        bg_lit.inputs["Strength"].default_value = rec["strength"]
        path = nodes.new("ShaderNodeLightPath")
        mix = nodes.new("ShaderNodeMixShader")
        mix.name = "wenart_sun_disc_mix"
        links.new(path.outputs["Is Camera Ray"], mix.inputs[0])     # 'Factor': 1 on the camera ray only
        links.new(bg_lit.outputs["Background"], mix.inputs[1])     # factor 0: every other ray, no disc
        links.new(bg.outputs["Background"], mix.inputs[2])         # factor 1: the camera ray sees the disc
        links.new(mix.outputs["Shader"], out.inputs["Surface"])
    else:
        links.new(bg.outputs["Background"], out.inputs["Surface"])
    world.use_fake_user = True
    scene["wenart_world_exterior"] = world.name
    scene["wenart_world_exterior_sun_disc"] = bool(rec["sun_disc"])
    scene["wenart_world_exterior_disc_camera_only"] = bool(rec["sun_disc"] and rec.get("sun_disc_camera_only"))
    if scene.world is not None:
        scene["wenart_world_interior"] = scene.world.name
    return rec


# --------------------------------------------------------------------------
# Milestone 13: the shell material table per slot and the material layers (docs/milestone13.md §13.2)
# --------------------------------------------------------------------------

SHELL_SLOT_NAMES = ("ceiling", "worktop", "front", "ceramic", "metal", "tile", "plaster")
# The layers (Blender 5.2 Principled BSDF inputs and shader nodes, names in the module docstring). Every value is a
# designer value (assumed) within the manual's ranges: coat weight 0-1 ("typically zero or one for physically-based
# materials, but may be textured"), coat IOR 1-2, sheen weight 0-1; bevel radius in metres (2-5 mm on plaster and
# wood, 1 mm on metal), AO distance in metres (corners within 0.15-0.30 m), the imperfection amount is the share of
# roughness variation (0.06-0.20) at a noise scale in metres.
SHELL_SLOTS: dict[str, dict] = {
    "ceiling": {"slugs": ("plaster_white",), "asset": "white_plaster_02", "mode": "flat",
                "layers": {"ao": {"distance_m": 0.30, "mix": 0.10}, "bevel": {"radius_m": 0.004},
                           "imperfection": {"amount": 0.10, "scale_m": 0.80}},
                "reason": "ceiling plaster on the Poly Haven white_plaster_02 set (flat albedo mode: the colour stays "
                          "the ceiling's, the photo adds its detail), corner AO and a 4 mm edge bevel"},
    # Fix round after P3 (16-17 Oct 2026): the worktop was Poly Haven marble_01 ("smooth, even cream-beige tiles",
    # tag "tiles"): P3's kitchen worktops showed a square joint every 0.75 m and read as tiles. ambientCG Marble012
    # (CC0; tags kitchen, polished, veined; a procedural, seamless set, vocabulary slug marble_slab, checked in
    # asset_checks_m10.json) is one jointless slab. Its API gives no real size (the fetcher assumes 1 m and flags
    # size_assumed), so the slot repeats it every size_m (slot_repeat_m): a 3 m run shows the veins 1.5 times.
    "worktop": {"slugs": ("stone_worktop",), "asset": "Marble012", "mode": "texture", "size_m": [2.0, 2.0],
                "layers": {"coat": {"weight": 0.6, "roughness": 0.10, "ior": 1.5}, "bevel": {"radius_m": 0.002},
                           "imperfection": {"amount": 0.15, "scale_m": 0.30}},
                "reason": "stone worktop on the ambientCG Marble012 set (one jointless slab, repeated every 2 m; "
                          "texture mode, gain-matched to the slug's grey), a polished coat and a 2 mm edge bevel"},
    # Fix round after P3: painted fronts and trim (skirting, door frames, sills) were the Poly Haven
    # white_planks_clean photo in flat mode: its board seams showed as a joint every ~10 cm along every skirting.
    # Painted MDF has no seam: the slot is a paint finish (``paint``: the slug's own plank set is left out, also when a
    # caller passes it, as furniture.py does for painted cabinet fronts); a set the style names itself still applies.
    "front": {"slugs": ("painted_wood_white",), "asset": None, "mode": "flat", "paint": True,
              "layers": {"coat": {"weight": 0.3, "roughness": 0.25, "ior": 1.45}, "bevel": {"radius_m": 0.0015},
                         "imperfection": {"amount": 0.12, "scale_m": 0.25}},
              "reason": "painted fronts and trim: a seamless paint finish in the style's colour (no plank photo), a "
                        "satin lacquer coat, a 1.5 mm edge bevel and roughness variation"},
    "ceramic": {"slugs": ("ceramic_white",), "asset": None, "mode": "flat", "roughness": 0.12,
                "layers": {"coat": {"weight": 1.0, "roughness": 0.03, "ior": 1.5}, "bevel": {"radius_m": 0.003},
                           "imperfection": {"amount": 0.06, "scale_m": 0.20}},
                "reason": "glazed sanitary ceramic: a full clear coat over the white body, a 3 mm edge bevel"},
    "metal": {"slugs": ("steel_brushed", "metal_black", "metal_brass"), "asset": "Metal032", "mode": "texture",
              "asset_for": ("steel_brushed",),
              "layers": {"bevel": {"radius_m": 0.001}, "imperfection": {"amount": 0.20, "scale_m": 0.10}},
              "reason": "brushed steel on the ambientCG Metal032 set (its roughness map), black and brass handles keep "
                        "their flat colour; a 1 mm edge bevel and roughness variation"},
    "tile": {"slugs": (), "prefix": PROCEDURAL_TILE_PREFIX, "asset": None, "mode": "flat",
             "layers": {"coat": {"weight": 0.8, "roughness": 0.08, "ior": 1.5}, "displacement": {"scale_m": 0.0015},
                        "ao": {"distance_m": 0.15, "mix": 0.06}, "imperfection": {"amount": 0.08, "scale_m": 0.50}},
             "reason": "glazed tiles: the procedural tile group with its grout on the material displacement "
                       "(displacement_method BOTH), a glaze coat, corner AO"},
    "plaster": {"slugs": (), "kind": "plaster", "asset": None, "mode": None,
                "layers": {"ao": {"distance_m": 0.25, "mix": 0.08}, "bevel": {"radius_m": 0.004},
                           "imperfection": {"amount": 0.10, "scale_m": 1.00}},
                "reason": "wall plaster and paint keep their own set; corner AO, a 4 mm edge bevel and roughness "
                          "variation"},
}
# Layers by material kind for every other slug (vocabulary ``kind``): fabrics get the Principled sheen ("Sheen
# simulates very small fibers on the surface. For cloth this adds a soft velvet like reflection near edges"), woods a
# light varnish coat and a 1.5 mm bevel.
MATERIAL_KIND_LAYERS: dict[str, dict] = {
    "fabric": {"sheen": {"weight": 0.5, "roughness": 0.5}},
    "wood": {"coat": {"weight": 0.25, "roughness": 0.3, "ior": 1.45}, "bevel": {"radius_m": 0.0015}},
}
BEVEL_SAMPLES = 4           # the manual: "The default value of 4 works well for most cases"
AO_SAMPLES = 4
IMPERFECTION_GROUP = "wenart_imperfection"


def current_levers() -> dict:
    """``lighting.light_levers()`` (the environment's ``WENART_LIGHT_VARIANT``); every lever off when the lighting
    module cannot be imported."""
    try:
        from wenart.blender.lighting import light_levers
        return light_levers()
    except Exception:  # noqa: BLE001 - a material must never die over a lever table
        return {"variant": None, "sun_wm2": None, "ev_cap": False, "rig": False, "shell": False, "source": "none"}


def shell_slot_of(slug: str, asset_id: str | None = None) -> str | None:
    """The shell slot of a material slug (pure), or None: ``ceramic_white`` -> ``ceramic``, ``stone_worktop`` ->
    ``worktop``, ``painted_wood_white`` -> ``front``, the handle metals -> ``metal``, a ``tiles_*`` slug -> ``tile``,
    ``plaster_white`` asked without an asset (the ceiling slot of the style profiles) -> ``ceiling``, any other
    plaster-kind slug (paint, lime_plaster, plaster_cream, a textured plaster_white wall) -> ``plaster``."""
    for name, spec in SHELL_SLOTS.items():
        if slug in spec.get("slugs", ()) and name != "ceiling":
            return name
    if str(slug).startswith(SHELL_SLOTS["tile"]["prefix"]):
        return "tile"
    if slug == "plaster_white" and not asset_id:
        return "ceiling"
    if (ENTRIES.get(slug) or {}).get("kind") == "plaster":
        return "plaster"
    return None


def shell_slot_spec(slot: str, style: dict | None = None) -> dict:
    """The resolved table entry of ``slot`` (pure): ``{"slot", "asset", "mode", "layers", "reason", "roughness"}``.
    The style's own slot asset wins where the profile names one (``ceiling.asset``, ``trim.asset``); the ``metal``
    slot's set applies to ``steel_brushed`` only (``asset_for``). KeyError for an unknown slot."""
    spec = dict(SHELL_SLOTS[slot])
    style = style or {}
    own = {"ceiling": "ceiling", "front": "trim"}.get(slot)
    entry = style.get(own) if own else None
    if isinstance(entry, dict) and entry.get("asset"):
        spec["asset"] = entry["asset"]
    spec["slot"] = slot
    spec["layers"] = {k: dict(v) for k, v in spec["layers"].items()}
    return spec


def slot_repeat_m(spec: dict | None, asset_id: str | None, manifest_entry: dict | None) -> list[float] | None:
    """The repeat in metres a shell slot gives its own texture set (pure; fix round after P3, 16-17 Oct 2026): the
    slot's ``size_m`` when ``asset_id`` is the slot's set and the assets manifest knows no real size for it
    (``size_assumed``, or no ``size_m``: ambientCG gives 0 x 0 for Marble012 and the fetcher assumes 1 m), else None
    (the set's own size stays)."""
    if not spec or not spec.get("size_m") or not asset_id or asset_id != spec.get("asset"):
        return None
    entry = manifest_entry if isinstance(manifest_entry, dict) else {}
    if entry.get("size_m") and not entry.get("size_assumed"):
        return None
    return [float(v) for v in spec["size_m"]][:2]


def paint_drop(spec: dict | None, slug: str, asset_id: str | None) -> str | None:
    """The texture set a paint slot leaves out (pure; fix round after P3): the slug's own vocabulary set (the plank
    photo of ``painted_wood_white``) when the slot is a ``paint`` slot and ``asset_id`` is that set, else None (a set
    the style names itself stays)."""
    if not spec or not spec.get("paint") or not asset_id or slug not in (spec.get("slugs") or ()):
        return None
    own = (ENTRIES.get(slug) or {}).get("asset")
    return asset_id if own and asset_id == own else None


def shell_assets() -> dict[str, str | None]:
    """``{slot: asset id}`` of the table (pure; the tests check every id against the vocabulary and the asset
    checks file, so no invented id can enter)."""
    return {slot: spec.get("asset") for slot, spec in SHELL_SLOTS.items()}


def material_kind_layers(slug: str) -> dict | None:
    """The ``MATERIAL_KIND_LAYERS`` of a slug's vocabulary kind (pure), None for other kinds or a shell slug."""
    kind = (ENTRIES.get(slug) or {}).get("kind")
    layers = MATERIAL_KIND_LAYERS.get(str(kind))
    return {k: dict(v) for k, v in layers.items()} if layers else None


def shell_material(slot: str, style: dict | None, assets):
    """The Blender material of a shell slot (docs/milestone13.md §13.2): the slot's representative slug through
    ``MaterialLibrary.get`` with the shell lever on, so the slot's CC0 set (when ``assets`` holds it) and its layers
    apply. ``assets``: a ``MaterialLibrary``, or the assets manifest's ``textures`` dict (paths absolute, or relative
    to the current folder), or None (flat / procedural with the layers)."""
    if isinstance(assets, MaterialLibrary):
        library = assets
        library.shell_on = True
        library.style = style or library.style
    else:
        library = MaterialLibrary(assets if isinstance(assets, dict) else None, None, use_textures=True, style=style,
                                  levers={"shell": True})
    spec = shell_slot_spec(slot, style)
    slug = {"ceiling": "plaster_white", "worktop": "stone_worktop", "front": "painted_wood_white",
            "ceramic": "ceramic_white", "metal": "steel_brushed", "tile": "tiles_light", "plaster": "paint"}[slot]
    asset = None if slot in ("ceiling",) else (ENTRIES.get(slug) or {}).get("asset")
    if slot == "metal":
        asset = None
    return library.get(slug, asset)


def _bsdf_of(mat):
    tree = mat.node_tree
    return next((n for n in tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"), None)


def _set_input(bsdf, name: str, value) -> bool:
    sock = bsdf.inputs.get(name)
    if sock is None:
        return False
    sock.default_value = value
    return True


def apply_shell_layers(mat, spec: dict, textured: bool = False, procedural: str | None = None) -> dict:
    """Add the layers of ``spec["layers"]`` to a Principled material (bpy): ``coat`` and ``sheen`` set the BSDF
    inputs; ``bevel`` puts a Bevel node on the normal chain (after the normal map or bump that feeds it);
    ``ao`` mixes the Ambient Occlusion factor into the base colour (``base x (1 - mix + mix x AO)``);
    ``imperfection`` multiplies the roughness by ``1 + amount x (noise - 0.5) x 2`` (``wenart_imperfection``);
    ``displacement`` (tiles) feeds the tile group's ``Height`` to a Displacement node on the Material Output
    (``displacement_method = "BOTH"``). Returns what was applied (the record's ``shell_layers``)."""
    bsdf = _bsdf_of(mat)
    if bsdf is None:
        return {"applied": [], "note": "no Principled BSDF: layers not applied"}
    tree = mat.node_tree
    nodes, links = tree.nodes, tree.links
    layers = spec.get("layers") or {}
    applied: dict = {}
    if spec.get("roughness") is not None and not bsdf.inputs["Roughness"].links:
        bsdf.inputs["Roughness"].default_value = float(spec["roughness"])
        applied["roughness"] = float(spec["roughness"])
    coat = layers.get("coat")
    if coat:
        ok = _set_input(bsdf, "Coat Weight", float(coat["weight"]))
        ok = _set_input(bsdf, "Coat Roughness", float(coat["roughness"])) and ok
        ok = _set_input(bsdf, "Coat IOR", float(coat["ior"])) and ok
        applied["coat"] = dict(coat, applied=ok)
    sheen = layers.get("sheen")
    if sheen:
        ok = _set_input(bsdf, "Sheen Weight", float(sheen["weight"]))
        ok = _set_input(bsdf, "Sheen Roughness", float(sheen["roughness"])) and ok
        applied["sheen"] = dict(sheen, applied=ok)
    bevel = layers.get("bevel")
    if bevel:
        node = nodes.new("ShaderNodeBevel")
        node.samples = BEVEL_SAMPLES
        node.inputs["Radius"].default_value = float(bevel["radius_m"])
        normal_in = bsdf.inputs["Normal"]
        if normal_in.links:
            links.new(normal_in.links[0].from_socket, node.inputs["Normal"])
        links.new(node.outputs["Normal"], normal_in)
        applied["bevel"] = dict(bevel, samples=BEVEL_SAMPLES)
    ao = layers.get("ao")
    if ao:
        node = nodes.new("ShaderNodeAmbientOcclusion")
        node.samples = AO_SAMPLES
        node.only_local = False
        node.inputs["Distance"].default_value = float(ao["distance_m"])
        node.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        mix = float(ao["mix"])
        weight = nodes.new("ShaderNodeMath")               # AO x mix + (1 - mix)
        weight.operation = "MULTIPLY_ADD"
        links.new(node.outputs["AO"], weight.inputs[0])
        weight.inputs[1].default_value = mix
        weight.inputs[2].default_value = 1.0 - mix
        scale = nodes.new("ShaderNodeVectorMath")
        scale.operation = "SCALE"
        base_in = bsdf.inputs["Base Color"]
        if base_in.links:
            links.new(base_in.links[0].from_socket, scale.inputs["Vector"])
        else:
            scale.inputs["Vector"].default_value = tuple(base_in.default_value)[:3]
        links.new(weight.outputs["Value"], scale.inputs["Scale"])
        links.new(scale.outputs["Vector"], base_in)
        applied["ao"] = dict(ao, samples=AO_SAMPLES)
    imp = layers.get("imperfection")
    if imp:
        group = nodes.new("ShaderNodeGroup")
        group.node_tree = imperfection_group()
        group.inputs["Amount"].default_value = float(imp["amount"])
        group.inputs["Scale"].default_value = 1.0 / max(1e-3, float(imp["scale_m"]))
        rough_in = bsdf.inputs["Roughness"]
        if rough_in.links:
            links.new(rough_in.links[0].from_socket, group.inputs["Roughness"])
        else:
            group.inputs["Roughness"].default_value = float(rough_in.default_value)
        links.new(group.outputs["Roughness"], rough_in)
        applied["imperfection"] = dict(imp)
    disp = layers.get("displacement")
    if disp:
        height = next((n.outputs["Height"] for n in nodes if n.bl_idname == "ShaderNodeGroup" and n.node_tree is not None
                       and "Height" in n.outputs), None)
        out = next((n for n in nodes if n.bl_idname == "ShaderNodeOutputMaterial"), None)
        if height is not None and out is not None:
            node = nodes.new("ShaderNodeDisplacement")
            node.space = "OBJECT"
            links.new(height, node.inputs["Height"])
            node.inputs["Midlevel"].default_value = 1.0          # tiles (height 1) stay, the grout (0) sinks
            node.inputs["Scale"].default_value = float(disp["scale_m"])
            links.new(node.outputs["Displacement"], out.inputs["Displacement"])
            mat.displacement_method = "BOTH"
            applied["displacement"] = dict(disp, method="BOTH")
        else:
            applied["displacement"] = dict(disp, applied=False, note="no tile group with a Height output")
    mat["wenart_shell_slot"] = str(spec.get("slot") or "")
    mat["wenart_shell_layers"] = ",".join(sorted(applied))
    return {"applied": sorted(applied), **applied}


def imperfection_group():
    """``wenart_imperfection`` (created once per file): inputs Roughness, Amount, Scale; output Roughness =
    ``clamp(Roughness x (1 + Amount x (noise - 0.5) x 2))`` with a 3-D fBM Noise Texture on the object coordinates
    (world space for the shell meshes, which sit at the origin), so no surface is perfectly uniform. No CC0
    imperfection image is in the catalogue (none audited), so the overlay is procedural."""
    import bpy

    group = bpy.data.node_groups.get(IMPERFECTION_GROUP)
    if group is not None:
        return group
    group = bpy.data.node_groups.new(IMPERFECTION_GROUP, "ShaderNodeTree")
    for sname in ("Roughness", "Amount", "Scale"):
        group.interface.new_socket(name=sname, in_out="INPUT", socket_type="NodeSocketFloat")
    group.interface.new_socket(name="Roughness", in_out="OUTPUT", socket_type="NodeSocketFloat")
    nodes = group.nodes
    gin, gout = nodes.new("NodeGroupInput"), nodes.new("NodeGroupOutput")
    g = _Graph(group)
    coord = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.noise_dimensions = "3D"
    noise.noise_type = "FBM"
    g.links.new(coord.outputs["Object"], noise.inputs["Vector"])
    g.links.new(gin.outputs["Scale"], noise.inputs["Scale"])
    noise.inputs["Detail"].default_value = 3.0
    centred = g.math("SUBTRACT", noise.outputs["Fac"], 0.5)                  # -0.5 .. 0.5
    factor = g.math("MULTIPLY_ADD", g.math("MULTIPLY", centred, 2.0), gin.outputs["Amount"], 1.0)
    rough = g.nodes.new("ShaderNodeMath")
    rough.operation = "MULTIPLY"
    rough.use_clamp = True
    g.links.new(gin.outputs["Roughness"], rough.inputs[0])
    g.links.new(factor, rough.inputs[1])
    g.links.new(rough.outputs["Value"], gout.inputs["Roughness"])
    return group


# --------------------------------------------------------------------------
# Milestone 10: colours and the procedural looks (docs/milestone10.md §4.2, §4.3, §4.8)
# --------------------------------------------------------------------------

def colour_linear(colour) -> tuple[float, float, float] | None:
    """Linear RGB of a colour phrase of ``wenart/style/colours.py`` (``"warm greige"``), None when unknown."""
    if not colour:
        return None
    try:
        from wenart.style import colours as C
        return tuple(float(v) for v in C.linear_rgb(str(colour)))  # type: ignore[return-value]
    except (ImportError, KeyError, ValueError):
        return None


def colourable(slug: str) -> bool:
    """True when a colour name sets the base colour of ``slug`` while its texture is in use: flat-albedo-mode and
    procedural looks unless the vocabulary says ``colourable: False`` (``wenart.style.profile.is_colourable``). A
    material without a texture set always takes the colour (it is a flat colour anyway)."""
    entry = ENTRIES.get(slug) or {}
    if "colourable" in entry:
        return bool(entry["colourable"])
    return albedo_mode(slug)[0] == "flat"


def takes_colour(slug: str, textured: bool) -> bool:
    """Whether a colour phrase sets the base colour of ``slug`` in a material: the vocabulary's ``colourable`` flag
    when it has one (``False``: a wood tone, a window-frame metal keep their own colour); without the flag a flat
    albedo look, or any look whose texture is not in use (a flat colour: ceramic, steel, a missing photo)."""
    entry = ENTRIES.get(slug) or {}
    if "colourable" in entry:
        return bool(entry["colourable"])
    return albedo_mode(slug)[0] == "flat" or not textured


def procedural_params(slug: str, overrides: dict | None = None) -> dict:
    """The vocabulary ``params`` of a procedural slug with the style's overrides (``tile_size_m``, ``pattern``,
    ``grout_colour`` of the wet walls) on top; None values of the overrides are ignored."""
    params = dict((ENTRIES.get(slug) or {}).get("params") or {})
    for key, value in (overrides or {}).items():
        if value is not None:
            params[key] = value
    return params


PROCEDURAL_GROUPS = ("wenart_tiles", "wenart_wallpaper", "wenart_slats", "wenart_standing_seam")
WALLPAPER_PATTERNS = ("stripe", "botanical", "geometric", "check", "herringbone", "grasscloth")
TILE_PATTERNS = ("running_bond", "grid", "hexagon")
TILE_GROUT_ROUGHNESS = 0.7
DEFAULT_INK_MODIFIER = "dark"


def procedural_group_name(procedural: str, params: dict) -> str:
    """The node group of a procedural look: one per tile and wallpaper pattern (their layout is node properties),
    one each for slats and standing seams."""
    if procedural == "wenart_tiles":
        pattern = params.get("pattern") if params.get("pattern") in TILE_PATTERNS else "grid"
        return f"wenart_tiles_{pattern}"
    if procedural == "wenart_wallpaper":
        pattern = params.get("pattern") if params.get("pattern") in WALLPAPER_PATTERNS else "stripe"
        return f"wenart_wallpaper_{pattern}"
    return procedural


def procedural_note_for(procedural: str, slug: str, params: dict) -> str:
    """The text recorded for a procedural look (material record and custom property)."""
    if procedural == "glazed_tiles":
        return procedural_note()
    if procedural == "wenart_tiles":
        size = params.get("tile_size_m") or [0.2, 0.2]
        return (f"procedural tiles {params.get('pattern') or 'grid'} {float(size[0]):.3f} x {float(size[1]):.3f} m, "
                f"{float(params.get('grout_m') or 0.002) * 1000:.0f} mm grout in "
                f"{params.get('grout_colour') or 'light grey'}"
                f" (node group {procedural_group_name(procedural, params)})")
    if procedural == "wenart_wallpaper":
        rep = params.get("repeat_m") or [0.2, 0.2]
        return (f"procedural wallpaper {params.get('pattern')}, repeat {float(rep[0]):.2f} x {float(rep[1]):.2f} m, "
                f"ink = the colour {params.get('ink_modifier') or DEFAULT_INK_MODIFIER} "
                f"(node group {procedural_group_name(procedural, params)})")
    if procedural == "wenart_slats":
        return (f"procedural wood slats {float(params.get('slat_width_m') or 0.03) * 100:.1f} cm, gap "
                f"{float(params.get('gap_m') or 0.02) * 100:.1f} cm on {params.get('backing_colour') or 'charcoal'} "
                f"(node group wenart_slats)")
    if procedural == "wenart_standing_seam":
        return (f"procedural standing seam, seams every {float(params.get('seam_spacing_m') or 0.45):.2f} m "
                f"(node group wenart_standing_seam)")
    return f"procedural {procedural} ({slug})"


class _Graph:
    """Small helper to wire shader nodes: sockets are linked, plain values set as defaults."""

    def __init__(self, tree):
        self.nodes, self.links = tree.nodes, tree.links

    def feed(self, socket, value) -> None:
        if hasattr(value, "is_output"):
            self.links.new(value, socket)
        elif isinstance(value, (tuple, list)):
            socket.default_value = tuple(value)
        else:
            socket.default_value = value

    def math(self, op: str, *values):
        node = self.nodes.new("ShaderNodeMath")
        node.operation = op
        for i, v in enumerate(values):
            self.feed(node.inputs[i], v)
        return node.outputs[0]

    def vmath(self, op: str, *values, value_out: bool = False):
        node = self.nodes.new("ShaderNodeVectorMath")
        node.operation = op
        for i, v in enumerate(values):
            if op == "SCALE" and i == 1:
                self.feed(node.inputs["Scale"], v)
            else:
                self.feed(node.inputs[i], v)
        return node.outputs["Value" if value_out else "Vector"]

    def mix(self, data_type: str, factor, a, b):
        node = self.nodes.new("ShaderNodeMix")
        node.data_type = data_type
        ids = {"RGBA": ("A_Color", "B_Color", "Result_Color"), "VECTOR": ("A_Vector", "B_Vector", "Result_Vector"),
               "FLOAT": ("A_Float", "B_Float", "Result_Float")}[data_type]
        self.feed(_socket(node.inputs, "Factor_Float"), factor)
        self.feed(_socket(node.inputs, ids[0]), a)
        self.feed(_socket(node.inputs, ids[1]), b)
        return _socket(node.outputs, ids[2])

    def xyz(self, vector):
        node = self.nodes.new("ShaderNodeSeparateXYZ")
        self.links.new(vector, node.inputs["Vector"])
        return node.outputs["X"], node.outputs["Y"]

    def combine(self, x, y, z=0.0):
        node = self.nodes.new("ShaderNodeCombineXYZ")
        for name, v in (("X", x), ("Y", y), ("Z", z)):
            self.feed(node.inputs[name], v)
        return node.outputs["Vector"]

    def fract_below(self, value, period, share):
        """1 where ``fract(value / period) < share`` (a band of ``share`` of each period), else 0."""
        return self.math("LESS_THAN", self.math("FRACT", self.math("DIVIDE", value, period)), share)


def _socket(collection, identifier: str):
    return next(s for s in collection if s.identifier == identifier)


def _new_group(name: str, inputs: list[tuple[str, str]], outputs: list[tuple[str, str]]):
    import bpy

    group = bpy.data.node_groups.new(name, "ShaderNodeTree")
    for sname, stype in inputs:
        group.interface.new_socket(name=sname, in_out="INPUT", socket_type=stype)
    for sname, stype in outputs:
        group.interface.new_socket(name=sname, in_out="OUTPUT", socket_type=stype)
    gin = group.nodes.new("NodeGroupInput")
    gout = group.nodes.new("NodeGroupOutput")
    uv = group.nodes.new("ShaderNodeUVMap")
    uv.uv_map = "box_m"
    return group, gin, gout, uv.outputs["UV"]


_COLOUR, _FLOAT = "NodeSocketColor", "NodeSocketFloat"
_OUTPUTS = [("Color", _COLOUR), ("Roughness", _FLOAT), ("Normal", "NodeSocketVector")]


def _bump(g: _Graph, height, strength: float, distance: float):
    node = g.nodes.new("ShaderNodeBump")
    node.inputs["Strength"].default_value = strength
    node.inputs["Distance"].default_value = distance
    g.feed(node.inputs["Height"], height)
    return node.outputs["Normal"]


def tiles_group(pattern: str):
    """``wenart_tiles_<pattern>`` (created once per file): inputs Tile Color, Grout Color, Tile Width, Tile Height,
    Grout, Variation, Tile Roughness; outputs Color, Roughness, Normal. ``running_bond`` / ``grid``: a Brick
    Texture on the ``box_m`` UVs (offset 0.5 / 0), the brick colours the tile colour x (1 +- variation);
    ``hexagon``: pointy-top hexagons ``Tile Width`` flat to flat (the nearer of two rectangular lattices, the
    hexagon distance of the local position, one white-noise value per tile centre for the spread). Grout
    roughness 0.7, a bump from the grout mask (recessed joints)."""
    import bpy

    name = f"wenart_tiles_{pattern}"
    group = bpy.data.node_groups.get(name)
    if group is not None:
        return group
    group, gin, gout, uv = _new_group(name, [("Tile Color", _COLOUR), ("Grout Color", _COLOUR), ("Tile Width", _FLOAT),
                                             ("Tile Height", _FLOAT), ("Grout", _FLOAT), ("Variation", _FLOAT),
                                             ("Tile Roughness", _FLOAT)], _OUTPUTS + [("Height", _FLOAT)])
    g = _Graph(group)
    i = gin.outputs
    if pattern == "hexagon":
        r3 = math.sqrt(3.0)
        p = g.vmath("SCALE", uv, g.math("DIVIDE", 1.0, i["Tile Width"]))
        lattice, half = (1.0, r3, 1.0), (0.5, r3 / 2.0, 0.0)          # z stays 0 in both lattices
        a = g.vmath("SUBTRACT", g.vmath("WRAP", p, lattice, (0.0, 0.0, 0.0)), half)
        b = g.vmath("SUBTRACT", g.vmath("WRAP", g.vmath("SUBTRACT", p, half), lattice, (0.0, 0.0, 0.0)), half)
        closer_a = g.math("LESS_THAN", g.vmath("DOT_PRODUCT", a, a, value_out=True),
                          g.vmath("DOT_PRODUCT", b, b, value_out=True))
        local = g.mix("VECTOR", closer_a, b, a)
        ax, ay = g.xyz(g.vmath("ABSOLUTE", local))
        hexd = g.math("MAXIMUM", ax, g.math("ADD", g.math("MULTIPLY", ax, 0.5), g.math("MULTIPLY", ay, r3 / 2.0)))
        edge_at = g.math("SUBTRACT", 0.5, g.math("DIVIDE", g.math("MULTIPLY", i["Grout"], 0.5), i["Tile Width"]))
        grout = g.math("GREATER_THAN", hexd, edge_at)
        noise = g.nodes.new("ShaderNodeTexWhiteNoise")
        g.links.new(g.vmath("SUBTRACT", p, local), noise.inputs["Vector"])
        spread = g.math("MULTIPLY_ADD", g.math("SUBTRACT", g.math("MULTIPLY", noise.outputs["Value"], 2.0), 1.0),
                        i["Variation"], 1.0)
        tile = g.vmath("SCALE", i["Tile Color"], spread)
        colour = g.mix("RGBA", grout, tile, i["Grout Color"])
    else:
        brick = g.nodes.new("ShaderNodeTexBrick")
        brick.offset = 0.5 if pattern == "running_bond" else 0.0
        brick.offset_frequency = 2
        brick.squash = 1.0
        brick.squash_frequency = 1
        g.links.new(uv, brick.inputs["Vector"])
        brick.inputs["Scale"].default_value = 1.0
        brick.inputs["Mortar Smooth"].default_value = 0.3
        brick.inputs["Bias"].default_value = 0.0
        g.links.new(i["Tile Width"], brick.inputs["Brick Width"])
        g.links.new(i["Tile Height"], brick.inputs["Row Height"])
        g.links.new(i["Grout"], brick.inputs["Mortar Size"])
        g.links.new(i["Grout Color"], brick.inputs["Mortar"])
        for sock, sign in (("Color1", 1.0), ("Color2", -1.0)):
            factor = g.math("MULTIPLY_ADD", i["Variation"], sign, 1.0)
            g.links.new(g.vmath("SCALE", i["Tile Color"], factor), brick.inputs[sock])
        colour = brick.outputs["Color"]
        grout = brick.outputs["Factor"]
    g.links.new(colour, gout.inputs["Color"])
    rough = g.nodes.new("ShaderNodeMapRange")
    g.links.new(grout, rough.inputs["Value"])
    g.links.new(i["Tile Roughness"], rough.inputs["To Min"])
    rough.inputs["To Max"].default_value = TILE_GROUT_ROUGHNESS
    g.links.new(rough.outputs["Result"], gout.inputs["Roughness"])
    height = g.math("SUBTRACT", 1.0, grout)                     # 1 on the tile, 0 in the grout (M13: displacement)
    g.links.new(_bump(g, height, 0.4, 0.002), gout.inputs["Normal"])
    g.links.new(height, gout.inputs["Height"])
    return group


def wallpaper_group(pattern: str):
    """``wenart_wallpaper_<pattern>``: inputs Color, Ink, Repeat X, Repeat Y; outputs Color, Roughness (the material
    sets it), Normal. The ink share per pattern (box UVs in metres): stripe = vertical bands half a repeat wide;
    check = gingham (two crossing band sets, the crossing in full ink); geometric = diamonds (a check turned 45
    degrees); herringbone = short diagonal bands turning every column; botanical = leaf blobs (Voronoi cells
    distorted by noise); grasscloth = fine horizontal fibres (stretched noise, a third of the ink)."""
    import bpy

    name = f"wenart_wallpaper_{pattern}"
    group = bpy.data.node_groups.get(name)
    if group is not None:
        return group
    group, gin, gout, uv = _new_group(name, [("Color", _COLOUR), ("Ink", _COLOUR), ("Repeat X", _FLOAT),
                                             ("Repeat Y", _FLOAT), ("Roughness", _FLOAT)], _OUTPUTS)
    g = _Graph(group)
    i = gin.outputs
    x, y = g.xyz(uv)
    rx, ry = i["Repeat X"], i["Repeat Y"]
    if pattern == "check":
        share = g.math("MULTIPLY", g.math("ADD", g.fract_below(x, rx, 0.5), g.fract_below(y, ry, 0.5)), 0.5)
    elif pattern == "geometric":
        u, v = g.math("ADD", x, y), g.math("SUBTRACT", x, y)
        share = g.math("ABSOLUTE", g.math("SUBTRACT", g.fract_below(u, rx, 0.5), g.fract_below(v, rx, 0.5)))
    elif pattern == "herringbone":
        column = g.math("FLOOR", g.math("DIVIDE", x, rx))
        turn = g.math("MULTIPLY_ADD", g.math("FLOORED_MODULO", column, 2.0), -2.0, 1.0)
        share = g.fract_below(g.math("ADD", x, g.math("MULTIPLY", y, turn)), g.math("MULTIPLY", rx, 0.25), 0.5)
    elif pattern == "botanical":
        noise = g.nodes.new("ShaderNodeTexNoise")
        g.links.new(uv, noise.inputs["Vector"])
        g.feed(noise.inputs["Scale"], g.math("DIVIDE", 3.0, rx))
        offset = g.vmath("SCALE", g.vmath("SUBTRACT", noise.outputs["Color"], (0.5, 0.5, 0.5)),
                         g.math("MULTIPLY", rx, 0.3))
        cells = g.nodes.new("ShaderNodeTexVoronoi")
        cells.voronoi_dimensions = "2D"                     # the UV plane (3D cells would cut random slices)
        g.links.new(g.vmath("ADD", uv, offset), cells.inputs["Vector"])
        g.feed(cells.inputs["Scale"], g.math("DIVIDE", 1.0, rx))
        share = g.math("LESS_THAN", cells.outputs["Distance"], 0.3)
    elif pattern == "grasscloth":
        noise = g.nodes.new("ShaderNodeTexNoise")
        g.links.new(g.combine(g.math("DIVIDE", x, g.math("MULTIPLY", rx, 4.0)),
                              g.math("DIVIDE", y, g.math("MULTIPLY", ry, 0.05))), noise.inputs["Vector"])
        noise.inputs["Scale"].default_value = 1.0
        noise.inputs["Detail"].default_value = 4.0
        share = g.math("MULTIPLY", noise.outputs["Fac"], 0.35)
    else:                                                       # stripe
        share = g.fract_below(x, rx, 0.5)
    g.links.new(g.mix("RGBA", share, i["Color"], i["Ink"]), gout.inputs["Color"])
    g.links.new(i["Roughness"], gout.inputs["Roughness"])
    g.links.new(_bump(g, share, 0.05, 0.0005), gout.inputs["Normal"])
    return group


def slats_group():
    """``wenart_slats``: inputs Color (the wood), Backing, Slat Width, Gap, Roughness; vertical slats (along the box
    UV v, world Z on a wall) with a wood-grain luminance from stretched noise, the gaps in the backing colour, a bump
    that stands the slats proud."""
    import bpy

    group = bpy.data.node_groups.get("wenart_slats")
    if group is not None:
        return group
    group, gin, gout, uv = _new_group("wenart_slats", [("Color", _COLOUR), ("Backing", _COLOUR), ("Slat Width", _FLOAT),
                                                       ("Gap", _FLOAT), ("Roughness", _FLOAT)], _OUTPUTS)
    g = _Graph(group)
    i = gin.outputs
    x, y = g.xyz(uv)
    pitch = g.math("ADD", i["Slat Width"], i["Gap"])
    slat = g.fract_below(x, pitch, g.math("DIVIDE", i["Slat Width"], pitch))
    grain = g.nodes.new("ShaderNodeTexNoise")
    g.links.new(g.combine(g.math("MULTIPLY", x, 40.0), g.math("MULTIPLY", y, 1.5)), grain.inputs["Vector"])
    grain.inputs["Scale"].default_value = 1.0
    wood = g.vmath("SCALE", i["Color"], g.math("MULTIPLY_ADD", grain.outputs["Fac"], 0.3, 0.85))
    g.links.new(g.mix("RGBA", slat, i["Backing"], wood), gout.inputs["Color"])
    g.links.new(i["Roughness"], gout.inputs["Roughness"])
    g.links.new(_bump(g, slat, 0.8, 0.01), gout.inputs["Normal"])
    return group


def standing_seam_group():
    """``wenart_standing_seam``: inputs Color, Seam Spacing, Roughness; raised seams every ``Seam Spacing`` (2 cm
    wide, 10 % lighter) by a bump."""
    import bpy

    group = bpy.data.node_groups.get("wenart_standing_seam")
    if group is not None:
        return group
    group, gin, gout, uv = _new_group("wenart_standing_seam", [("Color", _COLOUR), ("Seam Spacing", _FLOAT),
                                                               ("Roughness", _FLOAT)], _OUTPUTS)
    g = _Graph(group)
    i = gin.outputs
    x, _y = g.xyz(uv)
    share = g.math("SUBTRACT", 1.0, g.math("DIVIDE", 0.02, i["Seam Spacing"]))
    seam = g.math("SUBTRACT", 1.0, g.fract_below(x, i["Seam Spacing"], share))
    g.links.new(g.vmath("SCALE", i["Color"], g.math("MULTIPLY_ADD", seam, 0.1, 1.0)), gout.inputs["Color"])
    g.links.new(i["Roughness"], gout.inputs["Roughness"])
    g.links.new(_bump(g, seam, 1.0, 0.02), gout.inputs["Normal"])
    return group


def _colour_param(name, fallback) -> tuple[float, float, float, float]:
    rgb = colour_linear(name) or tuple(fallback)
    return (float(rgb[0]), float(rgb[1]), float(rgb[2]), 1.0)


def procedural_node(nodes, links, procedural: str, slug: str, colour, params: dict):
    """A group node of a procedural look in a material, its inputs set from ``colour`` (linear RGB of the material)
    and ``params``; returns the node (outputs Color, Roughness, Normal)."""
    node = nodes.new("ShaderNodeGroup")
    rough = ROUGHNESS.get(slug, 0.6)
    base = (float(colour[0]), float(colour[1]), float(colour[2]), 1.0)
    if procedural == "wenart_tiles":
        pattern = params.get("pattern") if params.get("pattern") in TILE_PATTERNS else "grid"
        node.node_tree = tiles_group(pattern)
        size = params.get("tile_size_m") or [0.2, 0.2]
        node.inputs["Tile Color"].default_value = base
        node.inputs["Grout Color"].default_value = _colour_param(params.get("grout_colour"), (0.55, 0.55, 0.53))
        node.inputs["Tile Width"].default_value = float(size[0])
        node.inputs["Tile Height"].default_value = float(size[1] if len(size) > 1 else size[0])
        node.inputs["Grout"].default_value = float(params.get("grout_m") or 0.002)
        node.inputs["Variation"].default_value = float(params.get("variation") or 0.0)
        node.inputs["Tile Roughness"].default_value = rough
    elif procedural == "wenart_wallpaper":
        pattern = params.get("pattern") if params.get("pattern") in WALLPAPER_PATTERNS else "stripe"
        node.node_tree = wallpaper_group(pattern)
        rep = params.get("repeat_m") or [0.2, 0.2]
        ink = _ink_colour(colour, params.get("ink_modifier") or DEFAULT_INK_MODIFIER)
        node.inputs["Color"].default_value = base
        node.inputs["Ink"].default_value = (*ink, 1.0)
        node.inputs["Repeat X"].default_value = float(rep[0])
        node.inputs["Repeat Y"].default_value = float(rep[1] if len(rep) > 1 else rep[0])
        node.inputs["Roughness"].default_value = rough
    elif procedural == "wenart_slats":
        node.node_tree = slats_group()
        node.inputs["Color"].default_value = base
        node.inputs["Backing"].default_value = _colour_param(params.get("backing_colour"), (0.03, 0.03, 0.03))
        node.inputs["Slat Width"].default_value = float(params.get("slat_width_m") or 0.03)
        node.inputs["Gap"].default_value = float(params.get("gap_m") or 0.02)
        node.inputs["Roughness"].default_value = rough
    elif procedural == "wenart_standing_seam":
        node.node_tree = standing_seam_group()
        node.inputs["Color"].default_value = base
        node.inputs["Seam Spacing"].default_value = float(params.get("seam_spacing_m") or 0.45)
        node.inputs["Roughness"].default_value = rough
    else:
        raise KeyError(f"unknown procedural look {procedural!r}")
    return node


def _ink_colour(colour, modifier: str) -> tuple[float, float, float]:
    """The wallpaper ink: the base colour with the ``dark`` modifier (CIELAB, ``colours.apply_modifier``)."""
    try:
        from wenart.style import colours as C
        lab = C.apply_modifier(C.linear_to_lab(tuple(float(c) for c in colour[:3])), modifier)
        return tuple(float(v) for v in C.lab_to_linear(lab))  # type: ignore[return-value]
    except (ImportError, ValueError, KeyError):
        return tuple(float(c) * 0.5 for c in colour[:3])  # type: ignore[return-value]


def exterior_material(library, slug: str, colour=None):
    """The Blender material of an outside look (docs/milestone10.md §1.6b row 20, §4.8): a vocabulary slug with its
    asset (``vocabulary`` entry; a procedural look its node group) in ``colour`` (a ``colours.py`` phrase) where the
    slug takes a colour (``colourable``), else as the library makes it; the record says when a colour was not
    applied. A slug the vocabulary does not know gets the flat ``unknown`` grey (recorded)."""
    asset = (ENTRIES.get(slug) or {}).get("asset")
    return library.get(slug, asset, colour=colour)


def fixture_material(name: str, kelvin: float = 2700.0, strength: float | None = None):
    """The emissive surface of a light-rig fixture (Milestone 13, ``lighting.room_rig``): an Emission shader in the
    blackbody colour of ``kelvin`` (``lighting._blackbody_rgb``) at ``strength`` (round 3: the fixed
    ``lighting.SHADE_EMISSION_WM2SR`` when None, so a shade never clips at the project EV range; the P1 value 6.0
    rendered every shade white); the room's light comes from the point or area light inside the fixture, the
    emission is what the camera sees. ``cycles.emission_sampling`` is ``NONE`` (the small surface is no light to
    sample). One material per kelvin, cached by name."""
    import bpy

    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    from wenart.blender.lighting import SHADE_EMISSION_WM2SR, _blackbody_rgb
    radiance = float(SHADE_EMISSION_WM2SR if strength is None else strength)
    mat = light_material(name, _blackbody_rgb(float(kelvin)), radiance)
    mat.cycles.emission_sampling = "NONE"
    mat["wenart_fixture_k"] = float(kelvin)
    mat["wenart_shade_emission_wm2sr"] = radiance
    return mat


def light_material(name: str, rgb=(1.0, 0.78, 0.55), strength: float = 8.0):
    """A lit lamp part (bulb, diffuser, flame; docs/milestone10.md §4.9 interior evening): an Emission shader of a
    warm white (about 2700 K) at ``strength``; the room gets its light from the lamp's own point light
    (``furniture.py``), the emission is what the camera sees."""
    import bpy

    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    for n in list(nodes):
        if n.bl_idname == "ShaderNodeBsdfPrincipled":
            nodes.remove(n)
    emit = nodes.new("ShaderNodeEmission")
    emit.inputs["Color"].default_value = (*[float(c) for c in rgb], 1.0)
    emit.inputs["Strength"].default_value = float(strength)
    links.new(emit.outputs["Emission"], nodes.get("Material Output").inputs["Surface"])
    mat["wenart_light"] = float(strength)
    return mat


# --------------------------------------------------------------------------
# Fix round after P4a (17 Oct 2026): the glass of a library mirror
# --------------------------------------------------------------------------

MIRROR_GLASS_CHROMA_MAX = 0.02      # linear (max - min) / max of the albedo under this: a neutral grey texel ...
MIRROR_GLASS_VALUE_MIN = 0.07       # ... whose brightest linear channel is above this (sRGB about 0.30): the glass
MIRROR_GLASS_SLUG = "mirror"        # the vocabulary's mirror: flat 0.90, roughness 0.03, metallic 1.0


def srgb_to_linear(c: float) -> float:
    """One sRGB channel (0..1) in linear light (pure; the IEC 61966-2-1 curve, as Blender's sRGB colour space)."""
    c = float(c)
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def mirror_glass_texel(rgb_linear) -> bool:
    """Whether a linear albedo colour is mirror glass by the rule of ``mirror_glass_material`` (pure): neutral (the
    chroma ``(max - min) / max`` under ``MIRROR_GLASS_CHROMA_MAX``) and bright enough (max over
    ``MIRROR_GLASS_VALUE_MIN``)."""
    r, g, b = (float(v) for v in tuple(rgb_linear)[:3])
    hi, lo = max(r, g, b), min(r, g, b)
    return hi > MIRROR_GLASS_VALUE_MIN and (hi - lo) / max(hi, 1e-4) < MIRROR_GLASS_CHROMA_MAX


def mirror_glass_spec() -> dict:
    """The mirror the glass becomes (pure): the vocabulary's ``mirror`` slug (``base`` linear grey, ``roughness``,
    ``metallic``)."""
    base = flat_colour(MIRROR_GLASS_SLUG)
    return {"slug": MIRROR_GLASS_SLUG, "base": tuple(float(v) for v in base),
            "roughness": float(ROUGHNESS.get(MIRROR_GLASS_SLUG, 0.03)), "metallic": metallic(MIRROR_GLASS_SLUG)}


def mirror_glass_material(mat):
    """A copy of a library mirror's material whose glass is a real mirror (fix round after P4a, 17 Oct 2026; the
    module docstring has the measurement): where the albedo is neutral grey (``mirror_glass_texel``, built as nodes on
    the Base Color's own input) the Principled BSDF gets the ``mirror`` slug's base colour, Metallic and Roughness;
    elsewhere the model's own values. A constant base colour decides for the whole material. The copy is cached by name
    (``<name>__mirror``) and records ``wenart_mirror_glass`` (``mask``: ``texture`` | ``all`` | ``none``). A material
    without a Principled BSDF is returned unchanged."""
    import bpy

    if mat is None or not getattr(mat, "use_nodes", False) or mat.node_tree is None:
        return mat
    name = f"{mat.name}__mirror"
    found = bpy.data.materials.get(name)
    if found is not None:
        return found
    if _bsdf_of(mat) is None:
        return mat
    copy = mat.copy()
    copy.name = name
    bsdf = _bsdf_of(copy)
    spec = mirror_glass_spec()
    g = _Graph(copy.node_tree)
    base_in, metal_in, rough_in = bsdf.inputs["Base Color"], bsdf.inputs["Metallic"], bsdf.inputs["Roughness"]
    record = {"slug": spec["slug"], "chroma_max": MIRROR_GLASS_CHROMA_MAX, "value_min": MIRROR_GLASS_VALUE_MIN,
              "base": list(spec["base"]), "roughness": spec["roughness"], "metallic": spec["metallic"]}
    if not base_in.is_linked:
        glass = mirror_glass_texel(tuple(base_in.default_value)[:3])
        record["mask"] = "all" if glass else "none"
        if glass:
            for socket in (metal_in, rough_in):
                for link in list(socket.links):
                    copy.node_tree.links.remove(link)
            base_in.default_value = (*spec["base"], 1.0)
            metal_in.default_value = spec["metallic"]
            rough_in.default_value = spec["roughness"]
        copy["wenart_mirror_glass"] = json.dumps(record)
        return copy
    src = base_in.links[0].from_socket
    sep = copy.node_tree.nodes.new("ShaderNodeSeparateColor")
    copy.node_tree.links.new(src, sep.inputs["Color"])
    r, gg, b = sep.outputs["Red"], sep.outputs["Green"], sep.outputs["Blue"]
    hi = g.math("MAXIMUM", g.math("MAXIMUM", r, gg), b)
    lo = g.math("MINIMUM", g.math("MINIMUM", r, gg), b)
    rel = g.math("DIVIDE", g.math("SUBTRACT", hi, lo), g.math("MAXIMUM", hi, 1e-4))
    mask = g.math("MULTIPLY", g.math("LESS_THAN", rel, MIRROR_GLASS_CHROMA_MAX),
                  g.math("GREATER_THAN", hi, MIRROR_GLASS_VALUE_MIN))
    mask.node.name = "wenart_mirror_glass_mask"

    def own(socket):
        return socket.links[0].from_socket if socket.is_linked else float(socket.default_value)

    metal_src, rough_src = own(metal_in), own(rough_in)
    g.links.new(g.mix("RGBA", mask, src, (*spec["base"], 1.0)), base_in)
    g.links.new(g.mix("FLOAT", mask, metal_src, spec["metallic"]), metal_in)
    g.links.new(g.mix("FLOAT", mask, rough_src, spec["roughness"]), rough_in)
    record["mask"] = "texture"
    copy["wenart_mirror_glass"] = json.dumps(record)
    return copy


def mirror_glass_materials(materials_list: list) -> tuple[list, dict]:
    """``(materials, record)``: ``mirror_glass_material`` of each material of a library mirror model (None stays None)
    and ``{material name: mask}`` for the manifest entry (pure apart from bpy)."""
    out, record = [], {}
    for mat in materials_list:
        if mat is None:
            out.append(None)
            continue
        new = mirror_glass_material(mat)
        out.append(new)
        if new is not mat:
            record[mat.name] = json.loads(new.get("wenart_mirror_glass") or "{}").get("mask")
    return out, record
