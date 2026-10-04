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
'Factor' (identifier 'Fac'), properties offset / offset_frequency / squash /
squash_frequency; node groups through ``NodeTree.interface.new_socket(name,
in_out=..., socket_type=...)``.
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
    """``"glazed_tiles"`` for a ``tiles_*`` slug without an image texture set
    while textures are on (docs/milestone6.md §5 row 4), else None."""
    if has_texture or not use_textures or not str(slug).startswith(PROCEDURAL_TILE_PREFIX):
        return None
    return "glazed_tiles"


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
    def get(self, slug: str, asset_id: str | None = None, tint=None, unverified: bool = False):
        key = (slug, asset_id, tuple(tint) if tint else None, unverified)
        if key in self._cache:
            return self._cache[key]
        tset, reason = self.texture_set(asset_id)
        # One Blender material per (slug, asset, tint, unverified); the record
        # is keyed by the material's name so a slug used both textured (floor
        # with an asset) and flat (door leaf without one) is reported twice, and
        # an asset that could not be used keeps its own record with the reason.
        procedural = procedural_for(slug, tset is not None, self.use_textures)
        name = slug + (f"__{tset['id']}" if tset else "") + ("__unverified" if unverified else "")
        mat = pbr_material(name, slug, tset, tint, unverified=unverified, procedural=procedural)
        self._cache[key] = mat
        mode, detail = albedo_mode(slug)
        clamped = mat.get("wenart_gain_clamped")
        self.records[mat.name] = {
            "slug": slug, "textured": tset is not None, "asset": asset_id if tset else None,
            "source": tset["source"] if tset else None, "licence": tset["licence"] if tset else None,
            "size_m": tset["size_m"] if tset else None, "flat_colour": list(flat_colour(slug)),
            "tint": list(tint) if tint else None, "unverified": unverified,
            "reason": reason if procedural is None else f"{reason}; {procedural_note()}",
            "albedo_mode": mode, "detail": detail,
            "albedo_gain": mat.get("wenart_albedo_gain"), "albedo_mean_luminance": mat.get("wenart_albedo_mean"),
            "gain_clamped": None if clamped is None else bool(clamped),
            "metallic": metallic(slug), "procedural": procedural,
        }
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

def pbr_material(name: str, slug: str, texture_set: dict | None, tint=None, scale_m=None,
                 unverified: bool = False, procedural: str | None = None):
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
    mode) and ``wenart_albedo_note`` when the texture could not be read."""
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
    colour = _tinted(flat_colour(slug), tint)

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
            gain, clamped = albedo_gain_for(mean_lum, slug)
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


def albedo_gain_for(mean_lum: float, slug: str) -> tuple[float, bool]:
    """``(gain, clamped)``: the gain that brings a map of mean linear luminance
    ``mean_lum`` to the luminance of the slug's flat colour, clamped to
    ``ALBEDO_GAIN_RANGE``; ``clamped`` says whether the clamp changed it."""
    target = luminance(flat_colour(slug))
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
    strength = MOOD_STRENGTH.get(str(lighting.get("mood", "")).lower(), 1.0)
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
