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

Node names were checked against Blender 5.2.2: Principled BSDF inputs 'Base
Color', 'Roughness', 'Normal', 'Emission Color', 'Emission Strength', 'Metallic';
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
            entries[slug] = {k: e[k] for k in ("asset", "source", "procedural", "params", "colourable") if k in e}
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


class MaterialLibrary:
    """Creates and caches Blender materials per slug and records, for the
    scene manifest, whether each one is textured or flat and why."""

    def __init__(self, textures: dict | None, assets_dir: str | None, use_textures: bool = True,
                 refused: dict | None = None):
        self.textures = textures or {}
        self.assets_dir = Path(assets_dir) if assets_dir else None
        self.use_textures = use_textures
        # asset id -> why build.load_assets left it out (licence); the reason
        # goes into the material record instead of "not in the manifest".
        self.refused = refused or {}
        self.records: dict[str, dict] = {}
        self._cache: dict = {}

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

        pkey = _json.dumps(params, sort_keys=True) if params else None
        key = (slug, asset_id, tuple(tint) if tint else None, unverified, colour or None, pkey)
        if key in self._cache:
            return self._cache[key]
        tset, reason = self.texture_set(asset_id)
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
        name = (slug + (f"__{tset['id']}" if tset else "") + (f"__{_tag(colour)}" if rgb is not None else "")
                + (f"__p{_short_hash(pkey)}" if pkey and procedural in PROCEDURAL_GROUPS else "")
                + ("__unverified" if unverified else ""))
        mat = pbr_material(name, slug, tset, tint, unverified=unverified, procedural=procedural, base_rgb=rgb,
                           params=all_params)
        self._cache[key] = mat
        mode, detail = albedo_mode(slug)
        clamped = mat.get("wenart_gain_clamped")
        self.records[mat.name] = {
            "slug": slug, "textured": tset is not None, "asset": asset_id if tset else None,
            "source": tset["source"] if tset else None, "licence": tset["licence"] if tset else None,
            "size_m": tset["size_m"] if tset else None, "flat_colour": list(flat_colour(slug)),
            "tint": list(tint) if tint else None, "unverified": unverified,
            "reason": reason if procedural is None else f"{reason}; {procedural_note_for(procedural, slug, all_params)}",
            "albedo_mode": mode, "detail": detail,
            "albedo_gain": mat.get("wenart_albedo_gain"), "albedo_mean_luminance": mat.get("wenart_albedo_mean"),
            "gain_clamped": None if clamped is None else bool(clamped),
            "metallic": metallic(slug), "procedural": procedural,
        }
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
        """``proxy`` (grey), ``proxy_glass`` (shower) or ``proxy_unverified``."""
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

    if unverified:
        _add_unverified_stripes(mat, bsdf, out)
    return mat


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
    link to overlay (left as it is)."""
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


def world_nodes(scene, lighting: dict, hdri_path: str | None) -> dict:
    """World from the style: HDRI when a file is available, else a physical
    sky (sky texture, multiple scattering) at the style's sun position.
    Returns what was used for the manifest."""
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
    strength = MOOD_STRENGTH.get(mood, _MOOD_HDRI_STRENGTH.get(mood, 1.0))
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
        return {"kind": "hdri", "file": hdri_path, "strength": strength}

    sky = nodes.new("ShaderNodeTexSky")
    sky.sky_type = "MULTIPLE_SCATTERING"
    sky.sun_disc = False  # the sun lamp carries the direct light
    sky.sun_elevation = math.radians(max(1.0, elevation))
    # Sky rotation is counter-clockwise from +X; azimuth is clockwise from north (+Y).
    sky.sun_rotation = math.radians(90.0 - azimuth)
    links.new(sky.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength * 0.5
    return {"kind": "sky", "file": None, "strength": strength * 0.5}


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
                f"{float(params.get('grout_m') or 0.002) * 1000:.0f} mm grout in {params.get('grout_colour') or 'light grey'}"
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
                                             ("Tile Roughness", _FLOAT)], _OUTPUTS)
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
    g.links.new(_bump(g, g.math("SUBTRACT", 1.0, grout), 0.4, 0.002), gout.inputs["Normal"])
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
