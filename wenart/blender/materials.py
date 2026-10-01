"""Materials for the scene: textured PBR from the assets manifest, flat colour
fallback, glass, the dashed-red "unverified" overlay and the world nodes.

Texture sets follow the shared interface of wenart.assets:
``{"id", "source", "licence", "size_m": [w, h], "files": {"albedo", "normal",
"roughness", ("displacement")}}``; ``normal`` is OpenGL convention, which is
what Blender's Normal Map node expects (no green flip). Displacement is never
connected (material displacement stays at its default, bump only).

UVs: the meshes carry a box-projected UV layer in metres (common.assign_box_uvs),
so the Mapping node scales by ``1 / size_m`` and a tile has its real size.

Node names were checked against Blender 5.2.2: Principled BSDF inputs 'Base
Color', 'Roughness', 'Normal', 'Emission Color', 'Emission Strength', 'Metallic';
Glass BSDF inputs 'Color', 'Roughness', 'IOR'; ShaderNodeTexSky sky_type
'MULTIPLE_SCATTERING' with sun_elevation / sun_rotation (radians).
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


def _vocabulary_tables() -> tuple[dict, dict, str | None]:
    """``(flat_colours, roughness, error)`` from the style vocabulary."""
    try:
        from wenart.style import vocabulary as V
        flat = {slug: (float(c[0]), float(c[1]), float(c[2])) for slug, c in V.FLAT_COLOURS.items()}
        rough = {slug: float(r) for slug, r in V.ROUGHNESS.items()}
    except Exception as exc:  # noqa: BLE001 - the build must not die over a colour table
        return {}, {}, f"{type(exc).__name__}: {exc}"
    return flat, rough, None


_FLAT, _ROUGH, VOCABULARY_IMPORT_ERROR = _vocabulary_tables()
FLAT_COLOURS: dict[str, tuple[float, float, float]] = {**_LOCAL_FLAT_COLOURS, **_FLAT}
ROUGHNESS: dict[str, float] = {**_LOCAL_ROUGHNESS, **_ROUGH}


def flat_colour(slug: str) -> tuple[float, float, float]:
    """Flat colour for a slug (vocabulary, then the local table, then grey)."""
    return FLAT_COLOURS.get(slug, FLAT_COLOURS["unknown"])


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
        # with an asset) and flat (door leaf without one) is reported twice.
        name = slug + (f"__{tset['id']}" if tset else "") + ("__unverified" if unverified else "")
        mat = pbr_material(name, slug, tset, tint, unverified=unverified)
        self._cache[key] = mat
        self.records[mat.name] = {
            "slug": slug, "textured": tset is not None, "asset": asset_id if tset else None,
            "source": tset["source"] if tset else None, "licence": tset["licence"] if tset else None,
            "size_m": tset["size_m"] if tset else None, "flat_colour": list(flat_colour(slug)),
            "tint": list(tint) if tint else None, "unverified": unverified, "reason": reason,
            "albedo_gain": mat.get("wenart_albedo_gain"), "albedo_mean_luminance": mat.get("wenart_albedo_mean"),
        }
        return mat

    def textured(self, mat) -> bool:
        return bool(self.records.get(mat.name, {}).get("textured", False))

    def glass(self):
        if "glass" not in self._cache:
            self._cache["glass"] = glass_material("glass")
            self.records["glass"] = {"slug": "glass", "textured": False, "asset": None, "source": None,
                                     "licence": None, "size_m": None, "flat_colour": [1.0, 1.0, 1.0], "tint": None,
                                     "unverified": False, "reason": "glass BSDF"}
        return self._cache["glass"]

    def proxy(self, look: str = "proxy"):
        """``proxy`` (grey), ``proxy_glass`` (shower) or ``proxy_unverified``."""
        if look in self._cache:
            return self._cache[look]
        if look == "proxy_glass":
            mat = glass_material("proxy_glass", roughness=0.15)
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
                 unverified: bool = False):
    """Principled BSDF material: albedo / normal / roughness maps from
    ``texture_set`` (box UVs in metres, Mapping scale 1/size_m), or the flat
    colour of ``slug``. ``tint`` multiplies the base colour. ``unverified``
    adds red emission stripes on top so reviewers spot it in renders."""
    import bpy

    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    nodes, links = tree.nodes, tree.links
    bsdf = nodes.get("Principled BSDF")
    out = nodes.get("Material Output")
    bsdf.inputs["Roughness"].default_value = ROUGHNESS.get(slug, 0.6)
    bsdf.inputs["Metallic"].default_value = 0.0

    if texture_set is not None:
        size = scale_m or texture_set.get("size_m") or [1.0, 1.0]
        uvmap = nodes.new("ShaderNodeUVMap")
        uvmap.uv_map = "box_m"
        mapping = nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (1.0 / float(size[0]), 1.0 / float(size[1]), 1.0)
        links.new(uvmap.outputs["UV"], mapping.inputs["Vector"])

        albedo = _image_node(nodes, texture_set["files"]["albedo"], "sRGB")
        links.new(mapping.outputs["Vector"], albedo.inputs["Vector"])
        colour_out = albedo.outputs["Color"]
        # Photographed albedo maps carry the lighting of the photo: Poly Haven's
        # "white_plaster_02" averages 0.27 linear, far from a white wall. The map
        # is scaled so its mean luminance matches the slug's intended colour
        # (gain clamped to 0.5..4.0 and recorded on the material and in the manifest).
        gain, mean_lum = albedo_gain(albedo.image, slug)
        mat["wenart_albedo_gain"] = gain
        mat["wenart_albedo_mean"] = mean_lum
        if abs(gain - 1.0) > 1e-3:
            scale = nodes.new("ShaderNodeVectorMath")
            scale.operation = "MULTIPLY"
            scale.inputs[1].default_value = (gain, gain, gain)
            links.new(colour_out, scale.inputs[0])
            colour_out = scale.outputs["Vector"]
        if tint:
            mul = nodes.new("ShaderNodeVectorMath")
            mul.operation = "MULTIPLY"
            mul.inputs[1].default_value = (float(tint[0]), float(tint[1]), float(tint[2]))
            links.new(colour_out, mul.inputs[0])
            colour_out = mul.outputs["Vector"]
        links.new(colour_out, bsdf.inputs["Base Color"])

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
    else:
        r, g, b = flat_colour(slug)
        if tint:
            r, g, b = r * float(tint[0]), g * float(tint[1]), b * float(tint[2])
        bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)

    if unverified:
        _add_unverified_stripes(tree, bsdf, out)
    return mat


ALBEDO_GAIN_RANGE = (0.5, 4.0)


def luminance(rgb) -> float:
    return 0.2126 * float(rgb[0]) + 0.7152 * float(rgb[1]) + 0.0722 * float(rgb[2])


def albedo_gain(image, slug: str) -> tuple[float, float]:
    """Gain that brings the mean linear luminance of an albedo image to the
    luminance of the slug's intended flat colour. Returns (gain, mean_luminance);
    (1.0, mean) when the image cannot be read or the slug has no colour."""
    try:
        import numpy as np
        px = np.empty(len(image.pixels), dtype=np.float32)
        image.pixels.foreach_get(px)   # scene-linear floats, RGBA
        px = px.reshape(-1, 4)[:, :3]
        if len(px) > 262_144:          # a 512x512 sample is plenty for a mean
            px = px[:: max(1, len(px) // 262_144)]
        # image.pixels of a byte image are the stored (sRGB-encoded) values, not
        # scene-linear ones: decode before averaging (checked on Blender 5.2.2).
        if image.colorspace_settings.name == "sRGB":
            px = np.where(px > 0.04045, ((px + 0.055) / 1.055) ** 2.4, px / 12.92)
        mean = px.mean(axis=0)
        mean_lum = float(0.2126 * mean[0] + 0.7152 * mean[1] + 0.0722 * mean[2])
    except Exception:  # noqa: BLE001 - never fail a build over a brightness tweak
        return 1.0, -1.0
    target = luminance(flat_colour(slug))
    if mean_lum <= 1e-4 or target <= 0:
        return 1.0, mean_lum
    gain = min(ALBEDO_GAIN_RANGE[1], max(ALBEDO_GAIN_RANGE[0], target / mean_lum))
    return round(gain, 4), round(mean_lum, 4)


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
    _stripes_over_socket(tree, out.inputs["Surface"].links[0].from_socket, out)
    return True


def _add_unverified_stripes(tree, base_shader, out):
    """Mix red emission stripes over the base shader node's first output."""
    _stripes_over_socket(tree, base_shader.outputs[0], out)


def _stripes_over_socket(tree, shader_socket, out):
    """Mix red emission stripes (world-space bands, 10 cm period) over ``shader_socket``."""
    nodes, links = tree.nodes, tree.links
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
    mix = nodes.new("ShaderNodeMixShader")
    links.new(step.outputs["Value"], mix.inputs["Fac"])
    links.new(shader_socket, mix.inputs[1])
    links.new(emit.outputs["Emission"], mix.inputs[2])
    links.new(mix.outputs["Shader"], out.inputs["Surface"])


def glass_material(name: str, roughness: float = 0.0, ior: float = 1.45):
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
    glass.inputs["Roughness"].default_value = roughness
    glass.inputs["IOR"].default_value = ior
    # Shadow rays see a transparent surface, otherwise the pane blocks the sun
    # and the interior behind a window (or inside a glass shower box) goes dark.
    path = nodes.new("ShaderNodeLightPath")
    transparent = nodes.new("ShaderNodeBsdfTransparent")
    mix = nodes.new("ShaderNodeMixShader")
    links.new(path.outputs["Is Shadow Ray"], mix.inputs["Fac"])
    links.new(glass.outputs["BSDF"], mix.inputs[1])
    links.new(transparent.outputs["BSDF"], mix.inputs[2])
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
