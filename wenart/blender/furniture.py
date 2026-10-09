"""Furniture objects for the scene (docs/milestone4.md §2): fitted library
glTF assets on the drawn footprints, parametric meshes as the fallback, the
Milestone 3 proxy box for ``unknown`` pieces and behind ``--proxies``, and
decor items on their host pieces.

Per piece of ``building.furniture`` on the level:

- ``asset`` with ``method: library`` and a readable glTF/GLB file whose
  licence passes the model gate (``licence_refusal``: Poly Haven CC0;
  Objaverse CC0 or CC BY 4.0 with its credit line) ->
  the file is imported (``bpy.ops.import_scene.gltf``), its meshes merged
  into one object, re-oriented from the catalogue frame (``front_axis``,
  ``up_axis``) into the piece frame (width X, depth Y, front -Y, Z up),
  re-centred so the bounding box centre sits on the footprint centre and
  its bottom on the floor, scaled by ``fit_scale``, rotated by
  ``footprint.rotation_deg`` and placed at ``footprint.center`` on the
  floor of the level. The asset's own materials are kept.
- otherwise -> the parametric mesh of ``wenart.blender.parametric`` with
  materials from the style, and the manifest says why
  (``method: "parametric (fallback: <reason>)"``).
- ``type == "unknown"`` (and every piece with ``use_proxies``) -> the
  Milestone 3 proxy box of ``wenart.blender.proxies`` (name ``proxy_<id>``,
  kind ``furniture_proxy``, pass index key ``proxy:<id>``), unchanged.

Objects are named ``furn_<id>`` with ``wenart_id = <id>``, ``wenart_kind =
furniture``, ``wenart_status``, ``wenart_source`` (from_documents /
added_by_ai), ``wenart_asset`` (asset id or ``parametric``) and
``wenart_type``. Unverified pieces get the red emission stripes as an
overlay on every material. Each piece has one pass index (``pass_indices[
<id>]``); its decor shares the index and the ``wenart_id``, like a door's
frame and leaf (``decor_<host id>_<n>``, kind ``decor``).

Nothing is moved: footprint centre, size and rotation are taken from the
JSON as they are; a fitted asset whose box does not match the footprint
within 1 cm after the fit is reported as a warning, never adjusted.

Milestone 6 (docs/milestone6.md §5 rows 2 and 8): parametric wood is the
veneer of the floor's wood tone (Poly Haven ``oak_veneer_01`` /
``walnut_veneer``), fabrics, bedding and the duvet carry the
``rough_linen`` weave in flat albedo mode, steel is metallic; every
parametric piece and decor item gets one Bevel modifier (``add_bevel``:
weight-limited, per-part radii from ``parametric.part_bevel_radius``); the
soft bedding of a bed and the fronts of a kitchen counter are recorded as
``assumed`` design details (``design_details``: parent = the piece, kind,
reason); decor on a parametric bed rests on the bedding top.

Milestone 7 (docs/milestone7.md §6.3-6.4): Objaverse models are GLB files
in the prep pod's cache (``asset.glb`` = ``models/objaverse/<uid>.glb``
under the assets dir; the importer reads GLB like glTF). Pieces with
``build: false`` (drawn symbols both recognition passes called
``not_furniture``) are not built at all: no object, no proxy, no pass index,
no decor; the summary lists them under ``not_built``.

Milestone 8 (docs/milestone8.md §2, §4):

- Model sources ``abo`` (CC BY 4.0 with its credit line) and ``generated``
  (licence text ``generated (...)``) pass the model gate; an Objaverse model
  of another licence passes when its fit records the catalogue's
  ``licence_flag`` (licences are recorded and flagged, not filtered, while
  the user allows it). GLBs of every non-Poly-Haven source live under
  ``models/<source>/<uid>.glb``.
- Bed frames: a library bed whose asset says ``bed_frame: true`` gets the
  parametric mattress, duvet, turn-down band and pillows
  (``parametric.frame_bedding``: the frame's inner box = footprint minus 4 %
  per side, mattress top = ``deck_height_m`` x the z fit scale + 0.20 m, in
  the piece frame: head = local +Y) merged into the bed's object, so frame
  and bedding are one piece (one ``wenart_id``, one pass index); materials
  from the style like the parametric bed (``bedding``, ``duvet``); the
  manifest entry records ``bedding`` and the design detail. Decor on such a
  bed rests on the bedding top.
- Rugs and wall art are hostless decor (own ``wenart_id`` = the decor id,
  own pass index, kind ``decor``; ``views.index_table`` makes them decor
  elements, never furniture). A rug lies on the floor: its library model
  scaled to the rug size and kept flat (``target: rug``), else the flat
  parametric rug in the style's fabric. Wall art needs a library model (no
  parametric shape): scaled to its fitted box, its back on the wall plane
  (``wall_point``) facing the room, its bottom ``gap_m`` (0.25 m) above the
  built top of the piece it hangs over (``anchor_ids[0]``; the item's
  ``bottom_m`` when that piece is not built), scaled down when it would come
  closer than ``WALL_ART_CEILING_M`` to the ceiling; without a model it is
  not built (``summary.decor_skipped`` says why).

Milestone 10 (docs/milestone10.md §4.4-§4.7, §1.6b rows 15, 18; track F):

- Designs: every piece is built with ``looks.design_for`` (its ``furniture.design``, or ``style.json``
  ``cabinets`` / ``furniture`` and the vanity / built-in rules when the layout stage wrote none): cabinet fronts
  (flat, shaker, slatted, glass) in the design colour or wood, handles (brushed steel, black, brass), worktops,
  the fabric colour of upholstered pieces, the furniture wood, glass or marble table tops; the manifest entry
  records ``design`` and its sources. Material keys ``front``, ``handle``, ``worktop``, ``fabric``, ``wood`` take
  the design (``design_overrides``).
- Wall-hung pieces (``wall_cabinet``) stand ``mount_bottom_m`` above the floor; the corner sofa is built from
  ``schemas.l_parts`` (``chaise_side``, ``seat_depth``, ``chaise_width``).
- Recolour (§4.5): a library model whose fit carries ``asset.recolour`` (the brief's fabric / wood colour and the
  material slots that may take it, ``wenart.furniture.fit``) gets copies of those materials in that colour (the
  texture's luminance detail on the colour, ``materials`` flat mode); a slot whose material is not found is listed
  and left as it is.
- Decor: the 12 new types (curtains and blinds at their window, throws, books, candles, baskets, trays, wall
  clocks, sculptures, large plants of their species in their pot, pendant and ceiling lights reaching the
  ceiling: under a roof the lowest point of the sloped attic ceiling over them, ``ceiling_above``);
  ``colour_*`` part keys take the item's colour name, ``pot`` the plant's pot.
- Lights (§4.9): in a mood with ``lamps_on`` (interior evening) and for decor with ``light_on``, lamp bulbs and
  shades glow and a warm point light (``LAMP_LIGHTS``, assumed wattage) sits in each lamp; recorded as ``light``
  on the entry and in ``assumed``.

The glTF importer of Blender 5.2.2 (checked with ``get_rna_type``):
``filepath``, ``import_shading`` (NORMALS/FLAT/SMOOTH), ``merge_vertices``,
``import_pack_images``, ``import_scene_as_collection`` (default True: a new
collection per file; set False here, the objects are re-linked into the
level collection), ``import_select_created_objects``. glTF files are Y-up
and the importer converts them to Blender's Z-up, so ``front_axis`` /
``up_axis`` of the catalogue are read in the imported (Z-up) frame.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Sequence

from wenart import geometry as G
from wenart.blender import parametric as P
from wenart.blender import proxies
from wenart.blender.proxies import COINCIDENT_LIFT, footprints_overlap, mount_bottom, proxy_height

CC0 = "CC0"
CC_BY = "CC-BY-4.0"
LIBRARIES = ("polyhaven", "abo", "objaverse", "generated", "parametric")
# Licence gate of the model kind (docs/milestone7.md §6.3, docs/milestone8.md §2; the rule of
# wenart.assets.fetch.check_licence with kind "models", repeated here because Blender's Python imports this
# module without the asset code). Generated models carry the licence text "generated (<model>, <licence>)".
MODEL_LICENCES = {"polyhaven": (CC0,), "abo": (CC_BY,), "objaverse": (CC0, CC_BY), "generated": ()}
GENERATED_LICENCE_PREFIX = "GENERATED"
# Milestone 8: sources whose other licences pass when the catalogue flagged them (recorded, not filtered).
FLAGGED_SOURCES = ("objaverse",)
LICENCE_FLAGS = ("non_commercial", "share_alike", "no_derivatives", "unknown")
CC_BY_FIELDS = ("title", "author", "source_url", "licence_url", "via", "attribution")
OBJAVERSE_CACHE = "models/objaverse"          # <assets>/models/objaverse/<uid>.glb (written by the prep pod)
WALL_ART_CEILING_M = 0.10                     # wall art top at least this far below the ceiling
WALL_ART_WALL_GAP_M = 0.005                   # back of a picture this far off the wall face (no z-fighting)
WALL_ART_MIN_WIDTH_M = 0.3                    # scaled down for the ceiling below this: not built
WALL_DECOR_TYPES = ("wall_art", "mirror")     # Milestone 9: hung by wall_art_placement over their anchor piece
SURFACE_RAY_STEPS = 4                          # Milestone 9: a missed ray tries 4 points towards the host centre
MIRROR_ASPECT = 1.25                           # the parametric mirror's height / width (portrait)
# Milestone 10: wall decor of a parametric shape when no library model is fitted (the mirror since Milestone 9).
PARAMETRIC_WALL_DECOR = ("mirror", "clock")
CLOCK_DEPTH_M = 0.045
# Lamps that light up in a ``lamps_on`` mood (or with ``light_on``): kind -> (watts, temperature K, radius m,
# where: "below_shade" / "bulb"); designer values (assumed), recorded per light.
LAMP_LIGHTS: dict[str, tuple[float, float, float, str]] = {
    "floor_lamp": (25.0, 2700.0, 0.05, "below_shade"), "table_lamp": (15.0, 2700.0, 0.04, "below_shade"),
    "pendant_light": (35.0, 2700.0, 0.04, "bulb"), "ceiling_light": (50.0, 3000.0, 0.08, "bulb"),
    "candle": (0.5, 1900.0, 0.01, "bulb"),
}
LIT_SHADE_STRENGTH = 1.5
NOT_BUILT_REASON = "build false: a drawn symbol both recognition passes call not_furniture; kept as an obstacle, not built"
# A fitted box may differ from the footprint by this much before a warning.
FIT_TOLERANCE_M = 0.01
AXES = {"+X": (1.0, 0.0, 0.0), "-X": (-1.0, 0.0, 0.0), "+Y": (0.0, 1.0, 0.0), "-Y": (0.0, -1.0, 0.0),
        "+Z": (0.0, 0.0, 1.0), "-Z": (0.0, 0.0, -1.0)}
PIECE_FRONT = (0.0, -1.0, 0.0)
PIECE_UP = (0.0, 0.0, 1.0)


# --------------------------------------------------------------------------
# Pure helpers (no bpy): asset resolution, frame rotation, fitting maths
# --------------------------------------------------------------------------

def asset_licence(asset: dict) -> str | None:
    return asset.get("licence", asset.get("license"))


def licence_refusal(asset: dict) -> str | None:
    """Why a library asset may not be built (None when it may): Poly Haven models are CC0 only;
    ABO models CC BY 4.0; Objaverse models CC0 or CC BY 4.0, or (Milestone 8) any other licence the
    catalogue flagged (``licence_flag`` one of ``LICENCE_FLAGS``); generated models carry a
    ``generated (...)`` licence text. A CC BY one (also a flagged CC BY-NC/SA/ND) only with every credit
    field (CC BY 4.0 §3(a)(1)). An asset without a library is held to the Poly Haven rule (the strictest)."""
    source = asset.get("library") or asset.get("source") or "polyhaven"
    licence = asset_licence(asset)
    allowed = MODEL_LICENCES.get(source)
    if allowed is None:
        return f"asset {asset.get('asset_id')!r} comes from {source!r}, not a model source {sorted(MODEL_LICENCES)}; refused"
    text = str(licence or "").strip().upper()
    if source == "generated":
        if not text.startswith(GENERATED_LICENCE_PREFIX):
            return f"asset {asset.get('asset_id')!r} is generated but its licence {licence!r} does not say so; refused"
        return None
    flagged = bool(source in FLAGGED_SOURCES and text and asset.get("licence_flag") in LICENCE_FLAGS)
    if text not in allowed and not flagged:
        return f"asset {asset.get('asset_id')!r} licence {licence!r} is not {' or '.join(allowed)}; refused"
    if text == CC_BY or (flagged and text.startswith("CC-BY")):
        missing = [k for k in CC_BY_FIELDS if not str(asset.get(k) or "").strip()]
        if missing:
            return f"asset {asset.get('asset_id')!r} is CC BY 4.0 without {', '.join(missing)} (no credit line); refused"
    return None


def is_built(piece: dict) -> bool:
    """False for a piece with ``build: false`` (docs/milestone7.md §3.3): it stays in the building, unbuilt."""
    return piece.get("build", True) is not False


def resolve_asset(asset: dict | None, assets_dir: str | None) -> tuple[Path | None, str | None]:
    """``(file, reason)``: the glTF/GLB file of a fitted library asset, or
    None and why the parametric fallback is used (docs/milestone4.md §2:
    missing ``asset`` or missing file -> parametric)."""
    if not asset:
        return None, "no asset in the building JSON"
    method = asset.get("method") or ("library" if asset.get("file") or asset.get("asset_id") else None)
    if method == "parametric" or asset.get("library") == "parametric":
        return None, "fitting chose the parametric mesh"
    if method != "library":
        return None, f"asset method {method!r} is not 'library'"
    refusal = licence_refusal(asset)
    if refusal is not None:
        return None, refusal
    # The fitter records the catalogue's `gltf` path (Poly Haven) or `glb` path (Objaverse cache).
    file = asset.get("file") or asset.get("gltf") or asset.get("glb")
    candidates: list[Path] = []
    if file:
        p = Path(file)
        if not p.is_absolute() and assets_dir:
            p = Path(assets_dir) / p
        candidates.append(p)
    elif asset.get("uid") and assets_dir:
        source = asset.get("library") or "objaverse"
        cache = OBJAVERSE_CACHE if source == "objaverse" else f"models/{source}"
        candidates.append(Path(assets_dir) / cache / f"{asset['uid']}.glb")
    elif asset.get("asset_id") and assets_dir:
        base = Path(assets_dir) / "models" / str(asset["asset_id"])
        candidates += [base / f"{asset['asset_id']}_1k.gltf", base / f"{asset['asset_id']}.gltf",
                       base / f"{asset['asset_id']}.glb"]
    for p in candidates:
        if p.is_file():
            return p, None
    if not candidates:
        return None, f"asset {asset.get('asset_id')!r} has no file and no assets dir to look in"
    return None, f"asset file missing: {candidates[0]}"


def frame_rotation(front_axis: str | None, up_axis: str | None) -> list[list[float]]:
    """3x3 rotation that turns the asset's ``front_axis`` into the piece
    front (-Y) and its ``up_axis`` into +Z (row-major, applied as R @ v)."""
    f = AXES[(front_axis or "-Y").upper()]
    u = AXES[(up_axis or "+Z").upper()]
    if abs(_dot(f, u)) > 1e-9:
        raise ValueError(f"front_axis {front_axis!r} and up_axis {up_axis!r} are not perpendicular")
    src = (f, u, _cross(f, u))
    dst = (PIECE_FRONT, PIECE_UP, _cross(PIECE_FRONT, PIECE_UP))
    # R = D @ S^T with S = [f u f×u] and D = [-Y +Z (-Y)×(+Z)] as columns.
    return [[sum(dst[k][i] * src[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def _dot(a, b) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b) -> tuple[float, float, float]:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def apply_rotation(R: Sequence[Sequence[float]], v: Sequence[float]) -> tuple[float, float, float]:
    return tuple(R[i][0] * v[0] + R[i][1] * v[1] + R[i][2] * v[2] for i in range(3))


def fit_vertices(verts: Sequence[Sequence[float]], asset: dict, footprint: dict, floor_z: float,
                 target_size: Sequence[float] | None = None) -> tuple[list, dict]:
    """Asset-frame vertices -> world vertices on the footprint.

    Steps: rotate into the piece frame, re-centre (XY box centre to the
    origin, bottom to z = 0), scale by ``fit_scale`` (or to ``target_size``
    for decor), rotate by ``footprint.rotation_deg`` and move to
    ``footprint.center`` at ``floor_z``. Returns the vertices and a record
    with the measured boxes before and after the fit, the offsets applied
    and the scale used.

    An Objaverse asset's ``unit_scale`` (raw GLB units -> metres, the prep
    pod's unit guess; 1.0 when absent) is applied first: its catalogue boxes,
    and so ``fit_scale``, are in metres."""
    u = float(asset.get("unit_scale") or 1.0)
    if u != 1.0:
        verts = [(v[0] * u, v[1] * u, v[2] * u) for v in verts]
    R = frame_rotation(asset.get("front_axis"), asset.get("up_axis"))
    local = [apply_rotation(R, v) for v in verts]
    x0, y0, z0, x1, y1, z1 = _bounds(local)
    raw_bbox = [x1 - x0, y1 - y0, z1 - z0]
    offset = (-(x0 + x1) / 2.0, -(y0 + y1) / 2.0, -z0)
    local = [(x + offset[0], y + offset[1], z + offset[2]) for x, y, z in local]
    if target_size is not None:
        sx = float(target_size[0]) / raw_bbox[0] if raw_bbox[0] > 1e-9 else 1.0
        sy = float(target_size[1]) / raw_bbox[1] if raw_bbox[1] > 1e-9 else 1.0
        if len(target_size) > 2 and target_size[2]:
            sz = float(target_size[2]) / raw_bbox[2] if raw_bbox[2] > 1e-9 else 1.0
        else:
            sz = (sx + sy) / 2.0
        scale = [sx, sy, sz]
    else:
        scale = [float(v) for v in (list(asset.get("fit_scale") or [1.0, 1.0, 1.0]) + [1.0, 1.0, 1.0])[:3]]
    local = [(x * scale[0], y * scale[1], z * scale[2]) for x, y, z in local]
    fx0, fy0, fz0, fx1, fy1, fz1 = _bounds(local)
    fitted = [fx1 - fx0, fy1 - fy0, fz1 - fz0]
    rot = float(footprint["rotation_deg"])
    rad = math.radians(rot)
    c, s = math.cos(rad), math.sin(rad)
    cx, cy = float(footprint["center"][0]), float(footprint["center"][1])
    world = [(cx + c * x - s * y, cy + s * x + c * y, floor_z + z) for x, y, z in local]
    info = {
        "front_axis": asset.get("front_axis") or "-Y", "up_axis": asset.get("up_axis") or "+Z",
        "origin_offset_catalog": asset.get("origin_offset"),
        "origin_offset_applied": [round(v, 4) for v in offset],
        "bbox_raw_m": [round(v, 4) for v in raw_bbox], "bbox_m": [round(v, 4) for v in fitted],
        "fit_scale": [round(v, 4) for v in scale], "unit_scale": u,
    }
    return world, info


def _bounds(points) -> tuple[float, float, float, float, float, float]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    zs = [p[2] for p in points]
    return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)


def style_material_keys(style: dict) -> tuple[dict, list[dict]]:
    """Map the parametric material keys to ``(slug, asset_id, tint)`` from
    the style: wood = the veneer of the floor's wood tone (oak or walnut,
    ``vocabulary.veneer_for``; Poly Haven veneer maps, not the floor planks;
    oak veneer, recorded as assumed, when the floor is not wood), fabric and
    duvet from the ``textiles`` slot (the Milestone 3 profile has none:
    ``DEFAULT_TEXTILE_MATERIAL`` with its linen weave in flat albedo mode,
    recorded as assumed), bedding = white linen weave, painted fronts from the
    trim, and fixed slugs for ceramic, steel, worktop, dark lacquer, plant
    green and terracotta. An asset that is not in the assets manifest leaves
    the flat colour (``_Materials.get``). Returns ``(keys, assumed)``."""
    try:
        from wenart.style import vocabulary as V
        default_textile, furniture_materials = V.DEFAULT_TEXTILE_MATERIAL, V.FURNITURE_MATERIALS
        veneer_for, default_veneer = V.veneer_for, V.DEFAULT_VENEER
    except Exception:  # noqa: BLE001 - the local fallback of materials.py applies
        default_textile, furniture_materials, default_veneer = "fabric_linen", {}, "wood_veneer_oak"

        def veneer_for(_slug):
            return None

    def asset_of(slug: str):
        return (furniture_materials.get(slug) or {}).get("asset")

    assumed: list[dict] = []
    floor = style.get("floor") or {}
    floor_slug = floor.get("material")
    veneer = veneer_for(floor_slug)
    if veneer is None:
        veneer = default_veneer
        assumed.append({"object": "furniture", "field": "wood", "value": veneer,
                        "reason": f"style floor {floor_slug!r} is not wood; default veneer for furniture frames"})
    wood = (veneer, asset_of(veneer), None)
    textiles = style.get("textiles") or {}
    if textiles.get("material"):
        fabric = (textiles["material"], textiles.get("asset"), textiles.get("tint"))
    else:
        fabric = (default_textile, asset_of(default_textile), None)
        assumed.append({"object": "furniture", "field": "fabric", "value": default_textile,
                        "reason": "style profile has no textiles slot; default fabric for sofas and chairs"})
    trim = (style.get("trim") or {}).get("material") or "painted_wood_white"
    # Milestone 10: the style's furniture wood (a wood_veneer_* slug) wins over the floor's tone.
    furniture_wood = (style.get("furniture") or {}).get("wood") if isinstance(style.get("furniture"), dict) else None
    if furniture_wood and furniture_wood in furniture_materials:
        wood = (furniture_wood, asset_of(furniture_wood), None)
        assumed[:] = [a for a in assumed if a.get("field") != "wood"]
    keys = {
        "wood": wood, "fabric": fabric, "duvet": fabric, "painted": (trim, None, None),
        "bedding": ("fabric_white", asset_of("fabric_white"), None), "ceramic": ("ceramic_white", None, None),
        "steel": ("steel_brushed", None, None), "worktop": ("stone_worktop", None, None),
        "dark": ("lacquer_dark", None, None), "green": ("plant_green", None, None),
        "terracotta": ("terracotta", None, None), "glass": ("glass", None, None),
        "mirror": ("mirror", None, None),                     # Milestone 9: the parametric mirror's glass
        # Milestone 10: cabinet fronts (the trim's paint unless a design says otherwise), handles, a marble table
        # top, plant pots, lamp bulbs (frosted when off), rattan.
        "front": (trim, None, None), "handle": ("steel_brushed", None, None), "marble": ("marble", None, None),
        "pot": ("terracotta", None, None), "bulb": ("ceramic_white", None, None),
        "rattan": ("rattan", None, None),
    }
    return keys, assumed


def design_overrides(design: dict, ftype: str) -> tuple[dict, list[str]]:
    """``({key: {"slug", "asset", "colour"}}, notes)``: the material keys a piece's design changes (pure).
    ``front``: painted (the trim's paint, ``painted_wood_white``) in the design colour, else the design wood's
    veneer; ``handle``: ``finishes.CABINET_HANDLES``; ``worktop``: ``finishes.CABINET_WORKTOPS``; ``fabric`` and
    ``duvet``: the fabric colour on the linen; ``wood``: the design's veneer, or for a piece that is not upholstered
    and has a ``colour`` the painted look in that colour."""
    try:
        from wenart.style import finishes as FIN
        from wenart.style import vocabulary as V
        handles, worktops, furniture_materials = FIN.CABINET_HANDLES, FIN.CABINET_WORKTOPS, V.FURNITURE_MATERIALS
        all_materials = {**V.MATERIALS, **V.FURNITURE_MATERIALS}
    except Exception:  # noqa: BLE001 - without the tables the style keys stay
        return {}, ["design not applied: the style tables cannot be imported"]

    def asset(slug):
        return (all_materials.get(slug) or {}).get("asset")

    out: dict[str, dict] = {}
    notes: list[str] = []
    wood = design.get("wood") if design.get("wood") in furniture_materials else None
    upholstered = ftype in _looks().FABRIC_TYPES
    if design.get("colour"):
        out["front"] = {"slug": "painted_wood_white", "asset": asset("painted_wood_white"), "colour": design["colour"]}
        notes.append(f"fronts painted {design['colour']}")
        if not upholstered and ftype not in _looks().CABINET_TYPES + _looks().STORAGE_TYPES and not wood:
            out["wood"] = {"slug": "painted_wood_white", "asset": asset("painted_wood_white"),
                           "colour": design["colour"]}
            notes.append(f"wood parts painted {design['colour']}")
    elif wood:
        out["front"] = {"slug": wood, "asset": asset(wood), "colour": None}
        notes.append(f"fronts {wood}")
    if wood:
        out["wood"] = {"slug": wood, "asset": asset(wood), "colour": None}
    if design.get("handle") in handles:
        out["handle"] = {"slug": handles[design["handle"]], "asset": None, "colour": None}
        notes.append(f"handles {design['handle']}")
    if design.get("worktop") in worktops:
        slug = worktops[design["worktop"]]
        out["worktop"] = {"slug": slug, "asset": asset(slug), "colour": None}
        notes.append(f"worktop {design['worktop']}")
    fabric = design.get("fabric_colour") or (design.get("colour") if upholstered else None)
    if fabric:
        for key in ("fabric", "duvet"):
            out[key] = {"slug": "fabric_linen", "asset": asset("fabric_linen"), "colour": fabric}
        notes.append(f"fabric {fabric}")
    return out, notes


def _looks():
    from wenart.blender import looks
    return looks


def lamps_on(style: dict) -> bool:
    """True when the style's lighting mood turns the lamps on (``vocabulary.LIGHTING[mood]["lamps_on"]``: the
    interior evening mood, docs/milestone10.md §4.9)."""
    mood = str(((style or {}).get("lighting") or {}).get("mood") or "")
    try:
        from wenart.style import vocabulary as V
        return bool((V.LIGHTING.get(mood) or {}).get("lamps_on"))
    except Exception:  # noqa: BLE001
        return False


def pot_override(item: dict) -> dict:
    """The ``pot`` key of a plant (pure): ``item.pot.material`` through ``finishes.POT_MATERIALS`` (a colour alone:
    white ceramic in that colour, assumed), its colour; the terracotta default without a pot."""
    pot = item.get("pot") if isinstance(item.get("pot"), dict) else {}
    try:
        from wenart.style import finishes as FIN
        from wenart.style import vocabulary as V
        slug = FIN.POT_MATERIALS.get(str(pot.get("material") or "").lower())
        all_materials = {**V.MATERIALS, **V.FURNITURE_MATERIALS}
    except Exception:  # noqa: BLE001
        slug, all_materials = None, {}
    if slug is None:
        slug = "ceramic_white" if pot.get("colour") else "terracotta"
    return {"slug": slug, "asset": (all_materials.get(slug) or {}).get("asset"), "colour": pot.get("colour")}


def design_details(piece_type: str, parts: list[dict]) -> list[dict]:
    """The ``assumed`` design-detail records of a parametric piece (docs/milestone6.md §5):
    ``[{"field", "kind", "value", "reason"}]``: the soft bedding set of a bed and the
    counter-front set of a kitchen counter or island; [] for other types. They are details
    of the documented piece inside its own box, never new elements."""
    if piece_type in P.BED_TYPES:
        pillows = sum(1 for p in parts if p["role"] == "pillow")
        return [{"field": "bedding", "kind": "bedding",
                 "value": f"mattress, draped duvet, turn-down band, {pillows} pillow(s) leaning "
                          f"{P.PILLOW_TILT_DEG:g} degrees",
                 "reason": "design detail of the bed (soft bedding inside the bed's own box); "
                           "the documents show only the footprint"}]
    if piece_type in P.COUNTER_TYPES:
        fronts = sum(1 for p in parts if p["role"] == "handle")       # one handle per front, whatever its style
        return [{"field": "counter_fronts", "kind": "counter_fronts",
                 "value": f"{fronts} front(s) {P.FRONT_GAP * 1000:g} mm proud of the carcass with handles",
                 "reason": "design detail of the counter (fronts and handles inside its own box); "
                           "the documents show only the footprint"}]
    if piece_type in P.CABINET_LOOK_TYPES:
        fronts = sum(1 for p in parts if p["role"] == "handle")
        return [{"field": "cabinet_fronts", "kind": "cabinet_fronts",
                 "value": f"{fronts} front(s) with handles",
                 "reason": "design detail of the cabinet (fronts and handles inside its own box); "
                           "the documents show only the footprint"}]
    return []


def collect_decor(building: dict, level_id: str) -> list[tuple[dict, dict]]:
    """``(decor item, host piece)`` pairs for a level: the top-level
    ``building.decor`` list (by ``host_id``) and per-piece ``decor`` lists.
    Items whose host is unknown or on another level are left out (the
    caller warns about unknown hosts via ``unknown_decor_hosts``)."""
    pieces = {p["id"]: p for p in building.get("furniture", [])}
    out = []
    for item in building.get("decor") or []:
        if item.get("host_id") is None:                      # a plant on the floor: no host
            if item.get("level_id") == level_id and item.get("center"):
                out.append((item, None))
            continue
        host = pieces.get(item.get("host_id"))
        if host is not None and host["level_id"] == level_id:
            out.append((item, host))
    for piece in building.get("furniture", []):
        if piece["level_id"] != level_id:
            continue
        for item in piece.get("decor") or []:
            out.append((dict(item, host_id=piece["id"]), piece))
    return out


def unknown_decor_hosts(building: dict) -> list[str]:
    pieces = {p["id"] for p in building.get("furniture", [])}
    return [str(item.get("host_id")) for item in building.get("decor") or []
            if item.get("host_id") is not None and item.get("host_id") not in pieces]


def decor_height_above_floor(item: dict, host: dict, host_parametric: bool = False) -> tuple[float, str]:
    """Rest height of a decor item: its own ``center[2]`` when given, else
    the host's seat / mattress / shelf / top (``parametric.decor_rest_height``);
    on a bed built parametrically (``host_parametric``) the bedding top."""
    center = item.get("center") or []
    if len(center) > 2 and center[2] is not None:
        return float(center[2]), "center[2]"
    if host is None:
        return 0.0, "floor"
    host_h, _ = proxy_height(host["type"], host.get("height"))
    size = host["footprint"]["size"] if host_parametric else None
    return P.decor_rest_height(host["type"], host_h, item["type"], size), f"on {host['type']} {host['id']}"


def frame_bedding_plan(asset: dict | None, footprint: dict, z_scale: float) -> dict | None:
    """The bedding of a library bed frame (pure, docs/milestone8.md §4): ``{"parts", "record"}`` with the
    ``parametric.frame_bedding`` parts in the piece frame (deck = ``deck_height_m`` x ``z_scale``, the z fit
    scale the import applied) and their record; None when the asset is not a bed frame with a deck."""
    asset = asset or {}
    deck = asset.get("deck_height_m")
    if (asset.get("bed_frame") is not True or isinstance(deck, bool) or not isinstance(deck, (int, float))
            or not math.isfinite(deck) or deck <= 0):
        return None
    w, d = (float(v) for v in footprint["size"][:2])
    deck_z = float(deck) * float(z_scale)
    record = dict(P.frame_bedding_info(w, d, deck_z), deck_height_m=float(deck), z_scale=round(float(z_scale), 4))
    return {"parts": P.frame_bedding(w, d, deck_z), "record": record}


def wall_art_placement(item: dict, art_box, host_top: float | None, ceiling: float) -> tuple[dict | None, dict]:
    """Where a wall art piece hangs (pure): ``(footprint, record)``; footprint None when it cannot hang.

    ``art_box`` is the fitted ``[width, depth, height]`` (piece frame: the picture faces local -Y, its back
    is local +Y). Bottom edge = ``host_top`` (the built top of the piece it hangs over, above the floor)
    + ``item.gap_m`` (0.25 m), or the item's ``bottom_m`` when ``host_top`` is None; the whole box is scaled
    down uniformly when its top would come closer than ``WALL_ART_CEILING_M`` to ``ceiling`` (height above
    the floor), and refused below ``WALL_ART_MIN_WIDTH_M``. The back stands ``WALL_ART_WALL_GAP_M`` off the
    wall point (``item.wall_point``, on the wall face; else ``item.center``), the box centre half its depth
    further into the room."""
    w, dp, h = (float(v) for v in art_box[:3])
    gap = float(item.get("gap_m", 0.25))
    bottom = host_top + gap if host_top is not None else float(item.get("bottom_m") or 0.0)
    limit = float(ceiling) - WALL_ART_CEILING_M
    scale = 1.0
    if bottom + h > limit:
        scale = max(0.0, (limit - bottom) / h)
    record = {"bottom_m": round(bottom, 4), "gap_m": gap, "host_top_m": None if host_top is None else round(host_top, 4),
              "ceiling_m": round(float(ceiling), 4), "scale": round(scale, 4)}
    if w * scale < WALL_ART_MIN_WIDTH_M - 1e-9:
        record["reason"] = (f"only {max(0.0, limit - bottom):.2f} m between {bottom:.2f} m (piece top + gap) and the "
                            f"ceiling limit; the picture would be narrower than {WALL_ART_MIN_WIDTH_M} m")
        return None, record
    w, dp, h = w * scale, dp * scale, h * scale
    rot = float(item.get("rotation_deg") or 0.0)
    rad = math.radians(rot)
    front = (math.sin(rad), -math.cos(rad))            # local -Y turned by the rotation: into the room
    wall = item.get("wall_point") or item["center"]
    off = dp / 2.0 + WALL_ART_WALL_GAP_M
    center = [float(wall[0]) + front[0] * off, float(wall[1]) + front[1] * off]
    record.update({"top_m": round(bottom + h, 4), "box_m": [round(w, 4), round(dp, 4), round(h, 4)],
                   "wall_point": [float(wall[0]), float(wall[1])]})
    return {"center": center, "size": [w, dp], "rotation_deg": rot}, record


# --------------------------------------------------------------------------
# bpy: import, merge, objects
# --------------------------------------------------------------------------

def import_gltf_geometry(path: Path, collection) -> dict:
    """Import a glTF/GLB and return its merged geometry in the file's
    (Z-up) frame: ``{"verts", "faces", "materials", "face_materials", "uvs",
    "uv_name", "objects"}``. The imported objects are deleted again; the
    materials (and packed images) stay in ``bpy.data`` for the new object."""
    import bpy

    before = {o.name for o in bpy.data.objects}
    bpy.ops.import_scene.gltf(filepath=str(path), import_shading="NORMALS", import_scene_as_collection=False,
                              import_select_created_objects=False)
    new = [o for o in bpy.data.objects if o.name not in before]
    for ob in new:
        for col in list(ob.users_collection):
            col.objects.unlink(ob)
        collection.objects.link(ob)
    bpy.context.view_layer.update()
    meshes = [o for o in new if o.type == "MESH"]
    for ob in meshes:  # keep world transforms, drop the parents
        mw = ob.matrix_world.copy()
        ob.parent = None
        ob.matrix_world = mw
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    verts, faces, materials, face_materials, uvs = [], [], [], [], []
    uv_name = None
    for ob in meshes:
        ev = ob.evaluated_get(depsgraph)
        me = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=True, depsgraph=depsgraph)
        mw = ob.matrix_world
        offset = len(verts)
        verts.extend([tuple(mw @ v.co) for v in me.vertices])
        slot_map = []
        for mat in me.materials:
            if mat is None:
                slot_map.append(None)
                continue
            if mat not in materials:
                materials.append(mat)
            slot_map.append(materials.index(mat))
        layer = me.uv_layers.active
        if layer is not None and uv_name is None:
            uv_name = layer.name
        for poly in me.polygons:
            faces.append([offset + me.loops[li].vertex_index for li in poly.loop_indices])
            slot = slot_map[poly.material_index] if poly.material_index < len(slot_map) else None
            face_materials.append(slot)
            uvs.append([tuple(layer.data[li].uv) for li in poly.loop_indices] if layer is not None else None)
        bpy.data.meshes.remove(me)
    names = [o.name for o in new]
    for ob in new:
        _delete_object(ob)
    return {"verts": verts, "faces": faces, "materials": materials, "face_materials": face_materials,
            "uvs": uvs, "uv_name": uv_name or "UVMap", "objects": names}


def _cached_geometry(path: Path, collection, geo_cache: dict) -> dict:
    """``import_gltf_geometry`` once per file and build: pieces that share an
    asset share its materials and packed images instead of importing it
    again (the importer makes ``name.001`` material copies otherwise)."""
    key = str(path.resolve())
    if key not in geo_cache:
        geo_cache[key] = import_gltf_geometry(path, collection)
    return geo_cache[key]


def _delete_object(ob) -> None:
    from wenart.blender import common

    for child in list(ob.children):
        child.parent = None
    common.delete_object(ob)


def _material_is_textured(mat) -> bool:
    if mat is None or not mat.use_nodes or mat.node_tree is None:
        return False
    return any(n.bl_idname == "ShaderNodeTexImage" and n.image is not None for n in mat.node_tree.nodes)


def _unverified_copies(materials_list: list, cache: dict) -> list:
    """Copies of the asset materials with the red stripes mixed over the
    surface shader (the overlay of docs/milestone4.md §2)."""
    from wenart.blender.materials import add_unverified_overlay

    out = []
    for mat in materials_list:
        if mat is None:
            out.append(None)
            continue
        if mat.name not in cache:
            copy = mat.copy()
            copy.name = f"{mat.name}__unverified"
            add_unverified_overlay(copy)
            cache[mat.name] = copy
        out.append(cache[mat.name])
    return out


def _mesh_object(name: str, verts, faces, materials_list, face_materials, collection, wenart_id, kind, status,
                 uvs=None, uv_name: str | None = None, fallback_material=None):
    """Mesh object from world geometry with per-face materials; empty slots
    get ``fallback_material``; asset UVs (when given) become the active
    layer and ``box_m`` stays as a second layer."""
    from wenart.blender import common

    slots = [m if m is not None else fallback_material for m in materials_list]
    if not slots:
        slots = [fallback_material]
    indices = [i if i is not None else len(slots) - 1 for i in face_materials]
    if any(i is None for i in face_materials) and fallback_material not in slots:
        slots.append(fallback_material)
        indices = [i if i is not None else len(slots) - 1 for i in face_materials]
    ob = common.new_mesh_object(name, verts, faces, collection=collection, wenart_id=wenart_id, kind=kind,
                                status=status, materials=slots, face_material_indices=indices)
    if uvs is not None and any(u is not None for u in uvs):
        mesh = ob.data
        layer = mesh.uv_layers.new(name=uv_name or "UVMap")
        for poly, uv in zip(mesh.polygons, uvs):
            if uv is None:
                continue
            for li, co in zip(poly.loop_indices, uv):
                layer.data[li].uv = co
        mesh.uv_layers.active = layer
        # Image Texture nodes without a UV Map node sample the *render* UV layer,
        # which stays the first layer created (box_m) unless set here: without
        # this the asset's atlas was sampled with box UVs in metres (scrambled
        # wood on every library piece in furnish run 3).
        layer.active_render = True
    return ob


class _Materials:
    """Style materials per parametric key, cached per (key, unverified)."""

    def __init__(self, library, style: dict, assumed: list):
        self.library = library
        self.keys, extra = style_material_keys(style)
        assumed.extend(extra)
        self._cache: dict = {}

    def get(self, key: str, unverified: bool = False, accent=None, colour=None, overrides: dict | None = None,
            lit: bool = False):
        """The material of a parametric key; an ``accent_<key>`` part (Milestone 9 decor) takes ``accent`` (an RGB
        tint, the item's colour) on the ``<key>`` material, or the plain ``<key>`` material without one. Milestone
        10: a ``colour_<key>`` part takes ``colour`` (a ``colours.py`` name) as its base colour; ``overrides``
        (``design_overrides``, ``pot_override``) replace a key's slug, asset and colour for one piece; ``lit``
        makes the ``bulb`` key a light (``materials.light_material``)."""
        if key.startswith(P.ACCENT_PREFIX):
            key = key[len(P.ACCENT_PREFIX):]
            colour = None
        elif key.startswith(P.COLOUR_PREFIX):
            key = key[len(P.COLOUR_PREFIX):]
            accent = None
        else:
            accent, colour = None, None
        if key == "bulb" and lit:
            from wenart.blender import materials as M
            return M.light_material("lamp_light")
        over = (overrides or {}).get(key)
        if over:
            slug, asset, tint = over["slug"], over.get("asset"), None
            colour = colour or over.get("colour")
        else:
            slug, asset, tint = self.keys[key]
        ck = (slug, asset, unverified, tuple(accent) if accent else None, colour or None)
        if ck in self._cache:
            return self._cache[ck]
        if asset and self.library.texture_set(asset)[0] is None:
            asset = None  # no usable texture: share the flat material of the same slug
        if accent:
            tint = tuple(float(v) for v in accent)
        if slug == "glass":
            mat = self.library.thin_glass()  # shower panels: the index pass must see the piece behind
        else:
            mat = self.library.get(slug, asset, tint, unverified=unverified, colour=colour)
        self._cache[ck] = mat
        return mat

    def slug(self, key: str, overrides: dict | None = None) -> str:
        for prefix in (P.ACCENT_PREFIX, P.COLOUR_PREFIX):
            if key.startswith(prefix):
                key = key[len(prefix):]
        over = (overrides or {}).get(key)
        return over["slug"] if over else self.keys[key][0]


def create_furniture(building: dict, level: dict, collection, library, style: dict, assets_dir: str | None,
                     pass_indices: dict, manifest_objects: list, assumed: list, warnings: list,
                     use_proxies: bool = False) -> dict:
    """Create the furniture and decor objects of ``level``; returns a
    summary for the manifest (``pieces``, ``by_method``, ``fallbacks``,
    ``proxies``, ``decor``)."""
    floor_z = float(level["elevation"])
    mats = _Materials(library, style, assumed)
    mats.lamps_on = lamps_on(style)                   # Milestone 10: the interior evening mood lights the lamps
    mats.collection = collection
    on_level = [p for p in building.get("furniture", []) if p["level_id"] == level["id"]]
    pieces = [p for p in on_level if is_built(p)]
    not_built = [{"id": p["id"], "type": p["type"], "reason": NOT_BUILT_REASON} for p in on_level if not is_built(p)]
    proxy_pieces = [p for p in pieces if use_proxies or p["type"] == "unknown" or p["type"] not in P.PARAMETRIC_TYPES]
    for p in proxy_pieces:
        if p["type"] != "unknown" and not use_proxies:
            warnings.append(f"{p['id']}: furniture type {p['type']!r} has no parametric builder; proxy box used")
    summary = {"pieces": len(pieces), "by_method": {}, "fallbacks": [], "proxies": len(proxy_pieces), "decor": 0,
               "proxies_forced": bool(use_proxies), "not_built": not_built, "decor_skipped": []}
    if proxy_pieces:
        proxies.create_proxies({"furniture": proxy_pieces}, level, collection, {
            "proxy": library.proxy("proxy"), "proxy_glass": library.proxy("proxy_glass"),
            "proxy_unverified": library.proxy("proxy_unverified")}, pass_indices, manifest_objects, assumed,
            others=pieces)
        for p in proxy_pieces:
            summary["by_method"]["proxy"] = summary["by_method"].get("proxy", 0) + 1

    entries: dict[str, dict] = {}
    placed: list[tuple[dict, float]] = []
    unverified_cache: dict = {}
    geo_cache: dict = {}  # file -> imported geometry: one import per asset file, materials shared
    proxy_ids = {p["id"] for p in proxy_pieces}
    flat_ids = {p["id"] for p in proxy_pieces if proxies.flat_reason(p, pieces)}
    for piece in pieces:
        height, height_assumed = proxy_height(piece["type"], piece.get("height"))
        if piece["id"] in flat_ids:
            height = proxies.FLAT_PROXY_HEIGHT_M          # the flat proxy (M11): no lift for pieces standing on it
        lift = 0.0
        for other_fp, other_h in placed:
            if abs(other_h - height) < 1e-3 and footprints_overlap(piece["footprint"], other_fp):
                lift = COINCIDENT_LIFT
                break
        placed.append((piece["footprint"], height))
        if piece["id"] in proxy_ids:
            continue
        entry = _create_piece(piece, level, floor_z, height, height_assumed, lift, collection, library, mats,
                              assets_dir, pass_indices, assumed, warnings, unverified_cache, geo_cache,
                              style=style, building=building)
        manifest_objects.append(entry)
        entries[piece["id"]] = entry
        method = "library" if entry["method"] == "library" else "parametric"
        summary["by_method"][method] = summary["by_method"].get(method, 0) + 1
        if entry["fallback_reason"]:
            summary["fallbacks"].append({"id": piece["id"], "type": piece["type"], "reason": entry["fallback_reason"]})

    for host_id in unknown_decor_hosts(building):
        if host_id not in {p["id"] for p in building.get("furniture", [])}:
            msg = f"decor host {host_id!r} is not a furniture piece; item skipped"
            if msg not in warnings:
                warnings.append(msg)
    manifest_by_id = {o["wenart_id"]: o for o in manifest_objects if o.get("kind") in ("furniture", "furniture_proxy")}
    for n, (item, host) in enumerate(collect_decor(building, level["id"]), start=1):
        host_entry = None
        if host is not None:
            host_entry = entries.get(host["id"]) or manifest_by_id.get(f"proxy:{host['id']}")
            if host_entry is None:
                continue
        if item.get("type") in WALL_DECOR_TYPES:
            built = dict({k[len("proxy:"):]: v for k, v in manifest_by_id.items() if k.startswith("proxy:")},
                         **entries)                      # the built boxes: pieces, and proxies behind --proxies
            entry = _create_wall_art(item, n, level, floor_z, collection, library, assets_dir, pass_indices,
                                     built, on_level, warnings, geo_cache, summary["decor_skipped"], mats=mats)
        else:
            entry = _create_decor(item, host, n, level, floor_z, collection, library, mats, assets_dir, pass_indices,
                                  host_entry, warnings, geo_cache, skipped=summary["decor_skipped"], assumed=assumed)
        if entry is None:
            continue
        manifest_objects.append(entry)
        if host_entry is not None:
            host_entry.setdefault("decor", []).append({"name": entry["name"], "type": entry["type"],
                                                       "method": entry["method"]})
        summary["decor"] += 1
    return summary


def _base_entry(piece: dict, name: str, wenart_id: str, kind: str, status: str, level: dict, index: int) -> dict:
    return {
        "name": name, "wenart_id": wenart_id, "kind": kind, "status": status, "level_id": level["id"],
        "element_id": piece["id"], "room_id": piece.get("room_id"), "type": piece["type"],
        "source": piece.get("source"), "evidence": piece.get("evidence", []), "pass_index": index, "assumed": {},
        "decor": [],
    }


def _create_piece(piece, level, floor_z, height, height_assumed, lift, collection, library, mats, assets_dir,
                  pass_indices, assumed, warnings, unverified_cache, geo_cache, style=None, building=None) -> dict:
    # Milestone 10: a wall-hung piece stands mount_bottom_m above the floor; the design (or the style's fallback).
    base, base_assumed = mount_bottom(piece)
    floor_z = floor_z + base
    design, design_notes = _looks().design_for(piece, style or {}, building)
    overrides, override_notes = design_overrides(design, piece["type"])
    piece = dict(piece, design=design)
    fp = piece["footprint"]
    w, d = float(fp["size"][0]), float(fp["size"][1])
    rot = float(fp["rotation_deg"])
    cx, cy = float(fp["center"][0]), float(fp["center"][1])
    status = piece.get("status", "verified")
    unverified = status == "unverified"
    name = f"furn_{piece['id']}"
    index = len(pass_indices) + 1
    pass_indices[piece["id"]] = index
    entry = _base_entry(piece, name, piece["id"], "furniture", status, level, index)
    entry.update({"center": [cx, cy, floor_z + height / 2.0], "size": [w, d, height], "rotation_deg": rot,
                  "front_deg": None if piece.get("front_deg") is None else float(piece["front_deg"]),
                  "asset": piece.get("asset"), "fit_scale": [1.0, 1.0, 1.0], "method": None, "bbox_m": None,
                  "fallback_reason": None, "materials": [], "material": None, "textured": False})

    if base > 0:
        entry["mount_bottom_m"] = round(base, 4)
        if base_assumed:
            entry["assumed"]["mount_bottom_m"] = base
            assumed.append({"object": name, "field": "mount_bottom_m", "value": base,
                            "reason": f"{piece['type']} without mount_bottom_m: hung at the rule's {base} m"})
    if design or override_notes:
        entry["design"] = dict(design, sources=design_notes, materials=override_notes)
    if piece.get("shape") == "L" or piece["type"] == "sofa_corner":
        entry["l_shape"] = P.sofa_corner_parts_info(piece)
        if entry["l_shape"]["chaise_side_assumed"]:
            assumed.append({"object": name, "field": "chaise_side", "value": "right",
                            "reason": "corner sofa without chaise_side: the chaise on the right (assumed)"})
    file, reason = resolve_asset(piece.get("asset"), assets_dir)
    if file is None and (piece.get("asset") or {}).get("method") == "library":
        warnings.append(f"{piece['id']}: {reason}; parametric mesh used")  # a fit was made but cannot be built
    ob = None
    if file is not None:
        try:
            ob = _library_object(piece, file, name, status, floor_z, collection, library, entry, warnings,
                                 unverified_cache, geo_cache, mats=mats, assumed=assumed)
        except Exception as exc:  # noqa: BLE001 - a broken file falls back, loudly
            reason = f"import of {file} failed: {type(exc).__name__}: {exc}"
            warnings.append(f"{piece['id']}: {reason}; parametric mesh used")
            ob = None
    if ob is None:
        ob = _parametric_object(piece, name, status, floor_z, height + lift, collection, mats, entry,
                                overrides=overrides)
        entry["method"] = f"parametric (fallback: {reason})"
        entry["fallback_reason"] = reason
        for detail in entry.pop("_details", []):
            entry["assumed"][detail["field"]] = detail["value"]
            assumed.append({"object": name, "field": detail["field"], "value": detail["value"],
                            "reason": detail["reason"], "parent": piece["id"], "kind": detail["kind"]})
        if lift:
            entry["assumed"]["height_lift"] = lift
            assumed.append({"object": name, "field": "height_lift", "value": lift,
                            "reason": "footprint overlaps another piece of the same height; "
                                      "lifted so the top faces do not coincide"})
    if height_assumed:
        entry["assumed"]["height"] = height
        assumed.append({"object": name, "field": "height", "value": height,
                        "reason": f"no height in the JSON; type height for {piece['type']}"})
    if piece["type"] in LAMP_LIGHTS and getattr(mats, "lamps_on", False):
        parts = P.build_parts(piece["type"], w, d, height, piece=piece) if entry["method"] != "library" else None
        _lamp_light(piece["type"], name, ob, (cx, cy), floor_z, entry, getattr(mats, "collection", None), assumed,
                    piece["id"], parts=parts, rotation_deg=rot)
    ob["wenart_type"] = piece["type"]
    ob["wenart_room"] = piece.get("room_id") or ""
    ob["wenart_source"] = piece.get("source") or "from_documents"
    ob["wenart_asset"] = (piece.get("asset") or {}).get("asset_id") if entry["method"] == "library" else "parametric"
    ob.pass_index = index
    return entry


RECOLOUR_DETAIL = 0.6                  # recoloured texture slots keep this share of their luminance detail


def _base_name(name: str) -> str:
    """A material name without Blender's ``.001`` suffix of a second import."""
    import re

    return re.sub(r"\.\d{3}$", "", str(name))


def recolour_plan(names: list, recolour: dict) -> tuple[dict, list[str]]:
    """``({material name: (part, colour, rgb)}, missing slots)`` (pure): the imported materials (``names``, by
    glTF name, ``.001`` suffixes ignored) the fit's ``asset.recolour`` (``{part: {"colour", ["rgb"], "slots":
    [{"index", "name"}]}}``; ``rgb``: linear, a wood's flat colour) recolours; a model with one material takes it
    whatever its name when the slot is index 0."""
    plan: dict = {}
    missing: list[str] = []
    real = [n for n in names if n]
    for part, spec in sorted((recolour or {}).items()):
        if not isinstance(spec, dict) or not spec.get("colour"):
            continue
        for slot in spec.get("slots") or []:
            hits = [n for n in real if _base_name(n) == str(slot.get("name"))]
            if not hits and len(real) == 1 and slot.get("index") == 0:
                hits = real
            if not hits:
                missing.append(f"{part} slot {slot.get('index')} ({slot.get('name')})")
            for n in hits:
                plan[n] = (part, spec["colour"], spec.get("rgb"))
    return plan, missing


def recolour_materials(mats_list: list, recolour: dict, cache: dict, library) -> tuple[list, dict]:
    """Copies of the asset materials of ``recolour_plan`` in their colour (the base colour replaced; a texture's
    luminance keeps ``RECOLOUR_DETAIL`` of its detail, ``materials`` flat albedo mode), the others as they are;
    returns the list and the manifest record (``applied``, ``missing``)."""
    from wenart.blender import materials as M

    plan, missing = recolour_plan([m.name if m is not None else None for m in mats_list], recolour)
    out, applied = [], []
    for mat in mats_list:
        if mat is None or mat.name not in plan:
            out.append(mat)
            continue
        part, colour, given = plan[mat.name]
        rgb = tuple(given) if given else M.colour_linear(colour)
        if rgb is None:
            out.append(mat)
            missing.append(f"{part}: colour {colour!r} unknown")
            continue
        key = (mat.name, colour)
        if key not in cache:
            cache[key] = _recoloured_copy(mat, rgb, colour)
        out.append(cache[key])
        applied.append({"material": mat.name, "part": part, "colour": colour, "copy": cache[key].name})
    return out, {"applied": applied, "missing": missing}


def _recoloured_copy(mat, rgb, colour: str):
    from wenart.blender import materials as M

    copy = mat.copy()
    copy.name = f"{mat.name}__{M._tag(colour)}"
    if not copy.use_nodes or copy.node_tree is None:
        copy.diffuse_color = (*rgb, 1.0)
        return copy
    nodes, links = copy.node_tree.nodes, copy.node_tree.links
    bsdf = next((n for n in nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"), None)
    if bsdf is None:
        return copy
    base = bsdf.inputs["Base Color"]
    capped = tuple(min(M.MAX_ALBEDO, float(c)) for c in rgb)
    if base.links:
        src = base.links[0].from_socket
        image = getattr(src.node, "image", None)
        mean = M.texture_mean_luminance(image) if image is not None else None
        links.remove(base.links[0])
        if mean and mean > 1e-4:
            M._flat_detail_albedo(nodes, links, src, bsdf, capped, RECOLOUR_DETAIL, mean)
        else:
            base.default_value = (*capped, 1.0)
    else:
        base.default_value = (*capped, 1.0)
    copy["wenart_recolour"] = str(colour)
    return copy


def _library_object(piece, file: Path, name, status, floor_z, collection, library, entry, warnings,
                    unverified_cache, geo_cache, mats=None, assumed=None):
    asset = piece["asset"]
    geo = _cached_geometry(file, collection, geo_cache)
    if not geo["faces"]:
        raise ValueError("file has no mesh faces")
    verts, info = fit_vertices(geo["verts"], asset, piece["footprint"], floor_z)
    mats_list = geo["materials"]
    if asset.get("recolour"):
        mats_list, record = recolour_materials(mats_list, asset["recolour"], unverified_cache, library)
        entry["recolour"] = record
        for missing in record.get("missing") or []:
            warnings.append(f"{piece['id']}: recolour slot {missing} not found in {asset.get('asset_id')}; left as "
                            "it is")
    if status == "unverified":
        mats_list = _unverified_copies(mats_list, unverified_cache)
    fallback = library.proxy("proxy_unverified" if status == "unverified" else "proxy")
    faces, face_materials, uvs = geo["faces"], geo["face_materials"], geo["uvs"]
    fp = piece["footprint"]
    # Milestone 8: a bed frame gets the parametric bedding, merged into the same object (one piece).
    bedding = frame_bedding_plan(asset, fp, info["fit_scale"][2]) if mats is not None else None
    bedding_faces = 0
    if bedding is not None:
        b_verts, b_faces, b_keys = P.world_mesh(bedding["parts"], fp["center"], float(fp["rotation_deg"]), floor_z)
        used = sorted(set(b_keys), key=b_keys.index)
        slots = [mats.get(k, status == "unverified") for k in used]
        offset_v, offset_m = len(verts), len(mats_list)
        verts = list(verts) + list(b_verts)
        faces = list(faces) + [[i + offset_v for i in f] for f in b_faces]
        mats_list = list(mats_list) + slots
        face_materials = list(face_materials) + [offset_m + used.index(k) for k in b_keys]
        uvs = list(uvs) + [None] * len(b_faces)
        bedding_faces = len(b_faces)
    ob = _mesh_object(name, verts, faces, mats_list, face_materials, collection, piece["id"],
                      "furniture", status, uvs=uvs, uv_name=geo["uv_name"], fallback_material=fallback)
    if bedding is not None:
        polys = ob.data.polygons
        for poly in list(polys)[len(polys) - bedding_faces:]:
            poly.use_smooth = True                     # superellipsoid bedding: smooth like the parametric bed
        record = dict(bedding["record"], material_keys={k: mats.slug(k) for k in used},
                      frame_height_m=round(info["bbox_m"][2], 4))
        deck_z = record["deck_z_m"]
        if not 0.05 <= deck_z <= max(0.05, info["bbox_m"][2]):
            warnings.append(f"{piece['id']}: bed frame deck {deck_z:.3f} m (deck_height_m {record['deck_height_m']} x "
                            f"z scale {record['z_scale']}) is outside 0.05 m .. the frame height "
                            f"{info['bbox_m'][2]:.3f} m; bedding placed as recorded")
        entry["bedding"] = record
        detail = (f"mattress {P.FRAME_MATTRESS_M:g} m on the frame deck (top {record['mattress_top_m']:.3f} m), "
                  f"draped duvet, turn-down band, {record['pillows']} pillow(s) in the inner box "
                  f"{record['inner_box_m'][0]:.2f} x {record['inner_box_m'][1]:.2f} m")
        entry["assumed"]["bedding"] = detail
        if assumed is not None:
            assumed.append({"object": name, "field": "bedding", "value": detail, "parent": piece["id"],
                            "kind": "bedding", "reason": "design detail of the library bed frame (a frame without a "
                                                         "mattress): soft bedding inside the frame's own box; the "
                                                         "documents show only the footprint"})
    for axis, want, got in (("width", float(fp["size"][0]), info["bbox_m"][0]),
                            ("depth", float(fp["size"][1]), info["bbox_m"][1])):
        if abs(want - got) > FIT_TOLERANCE_M:
            warnings.append(f"{piece['id']}: fitted asset {asset.get('asset_id')!r} {axis} {got:.3f} m differs "
                            f"from the footprint {want:.3f} m by more than {FIT_TOLERANCE_M} m (not adjusted)")
    bbox = list(info["bbox_m"])
    if bedding is not None:
        bbox[2] = max(bbox[2], entry["bedding"]["top_m"])
    entry.update({"method": "library", "fit_scale": info["fit_scale"], "bbox_m": bbox,
                  "fit": info, "file": str(file),
                  "materials": [m.name for m in ob.data.materials if m is not None],
                  "material": ob.data.materials[0].name if ob.data.materials and ob.data.materials[0] else None,
                  "textured": any(_material_is_textured(m) for m in geo["materials"]),
                  "imported_objects": geo["objects"]})
    return ob


def _parametric_object(piece, name, status, floor_z, height, collection, mats, entry, overrides=None):
    fp = piece["footprint"]
    w, d = float(fp["size"][0]), float(fp["size"][1])
    parts = P.build_parts(piece["type"], w, d, height, piece=piece)
    lit = bool(getattr(mats, "lamps_on", False)) and piece["type"] in LAMP_LIGHTS
    if lit:                                           # Milestone 10: a lit lamp's shade glows
        parts = [dict(part, key=f"{LIT_KEY}{part['key']}") if part["role"] == "shade" else part for part in parts]
    verts, faces, keys = P.world_mesh(parts, fp["center"], float(fp["rotation_deg"]), floor_z)
    unverified = status == "unverified"
    used_keys = sorted(set(keys), key=keys.index)
    slots = [_part_material(mats, k, unverified and k != "glass", overrides=overrides, lit=lit) for k in used_keys]
    indices = [used_keys.index(k) for k in keys]
    ob = _mesh_object(name, verts, faces, slots, indices, collection, piece["id"], "furniture", status)
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    entry.update({"bbox_m": [round(x1 - x0, 4), round(y1 - y0, 4), round(z1 - z0, 4)],
                  "materials": [m.name for m in slots], "material": slots[0].name,
                  "textured": any(mats.library.textured(m) for m in slots),
                  "material_keys": {k.removeprefix(LIT_KEY): mats.slug(k.removeprefix(LIT_KEY), overrides)
                                    for k in used_keys},
                  "bevel": add_bevel(ob, parts), "_details": design_details(piece["type"], parts)})
    return ob


LIT_KEY = "lit:"                     # a part key prefix: the key's material with a glow (a lit lamp's shade)


def _part_material(mats, key: str, unverified: bool, accent=None, colour=None, overrides=None, lit: bool = False):
    """The material of one parametric part key (``_Materials.get``); a ``lit:`` key the glowing copy."""
    if key.startswith(LIT_KEY):
        return glow_copy(mats.get(key[len(LIT_KEY):], unverified, accent=accent, colour=colour, overrides=overrides))
    return mats.get(key, unverified, accent=accent, colour=colour, overrides=overrides, lit=lit)


def glow_copy(mat, strength: float = LIT_SHADE_STRENGTH):
    """A copy of a material whose Principled BSDF emits its base colour, warm (a lamp shade lit from inside)."""
    import bpy

    name = f"{mat.name}__lit"
    found = bpy.data.materials.get(name)
    if found is not None:
        return found
    copy = mat.copy()
    copy.name = name
    bsdf = next((n for n in copy.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"), None) \
        if copy.use_nodes else None
    if bsdf is not None:
        bsdf.inputs["Emission Color"].default_value = (1.0, 0.8, 0.6, 1.0)
        bsdf.inputs["Emission Strength"].default_value = float(strength)
    copy["wenart_light"] = float(strength)
    return copy


def lamp_light_point(kind: str, parts: list, center, rotation_deg: float, floor_z: float) -> tuple[float, float, float]:
    """Where a lamp's point light sits (pure): ``below_shade`` lamps 5 cm under the shade's lowest point (the shade
    is a closed solid), ``bulb`` lamps at the bulb's centre; on the piece's centre line otherwise."""
    where = LAMP_LIGHTS[kind][3]
    roles = ("shade",) if where == "below_shade" else ("bulb", "flame")
    zs = [v[2] for p in parts if p["role"] in roles for v in p["verts"]]
    if not zs:
        zs = [v[2] for p in parts for v in p["verts"]]
    if where == "below_shade":
        z = min(zs) - 0.05
    else:
        z = (min(zs) + max(zs)) / 2.0
    return (float(center[0]), float(center[1]), floor_z + z)


def _lamp_light(kind: str, name: str, ob, center, floor_z: float, entry: dict, collection, assumed: list,
                parent: str, parts: list | None = None, rotation_deg: float = 0.0) -> None:
    """A warm point light in a lamp (``LAMP_LIGHTS``; assumed wattage and colour), linked to ``collection`` and
    recorded on the entry (``light``) and in ``assumed`` (kind ``light``, parent the piece or item)."""
    import bpy

    watts, temp, radius, _where = LAMP_LIGHTS[kind]
    if parts is None:                                 # a library lamp: in its upper part, on its centre line
        top = float((entry.get("bbox_m") or entry.get("size") or [0.0, 0.0, 1.0])[2])
        loc = (float(center[0]), float(center[1]), floor_z + top * 0.8)
    else:
        loc = lamp_light_point(kind, parts, center, rotation_deg, floor_z)
    light = bpy.data.lights.new(f"{name}_light", "POINT")
    light.energy = watts
    light.shadow_soft_size = radius
    try:
        light.use_temperature = True
        light.temperature = temp
    except AttributeError:
        light.color = (1.0, 0.78, 0.55)
    lob = bpy.data.objects.new(f"{name}_light", light)
    lob.location = loc
    (collection or bpy.context.scene.collection).objects.link(lob)
    lob["wenart_kind"] = "light"
    lob["wenart_id"] = parent
    entry["light"] = {"name": lob.name, "energy_w": watts, "temperature_k": temp, "radius_m": radius,
                      "location": [round(v, 4) for v in loc]}
    assumed.append({"object": lob.name, "field": "lamp_light", "value": f"{watts:g} W point light at {temp:g} K",
                    "reason": "the lighting mood turns the lamps on (interior evening) or the item says light_on; "
                              "wattage and colour assumed", "parent": parent, "kind": "light"})


# Edges whose two faces turn by less than this keep weight 0 (cylinder sides, superellipsoid grids).
BEVEL_MIN_ANGLE_DEG = 30.0


def edge_bevel_weights(face_radii: Sequence[float], face_normals: Sequence[Sequence[float]],
                       edge_faces: Sequence[Sequence[int]], width: float = P.BEVEL_WIDTH_M,
                       min_angle_deg: float = BEVEL_MIN_ANGLE_DEG) -> list[float]:
    """Bevel weight per edge (pure): ``radius / width`` of the edge's part (the
    largest radius of its faces, capped at 1), 0 where the faces turn by less
    than ``min_angle_deg`` (a smooth surface: no bevel there) or the radius is 0."""
    cos_min = math.cos(math.radians(min_angle_deg))
    weights = []
    for faces in edge_faces:
        if not faces:
            weights.append(0.0)
            continue
        r = max(float(face_radii[f]) for f in faces)
        if r <= 0.0:
            weights.append(0.0)
            continue
        if len(faces) >= 2 and _dot(face_normals[faces[0]], face_normals[faces[1]]) > cos_min:
            weights.append(0.0)
            continue
        weights.append(min(1.0, r / width))
    return weights


def add_bevel(ob, parts: list[dict]) -> dict | None:
    """One Bevel modifier on a parametric object (docs/milestone6.md §5 row 8):
    limit method WEIGHT, width ``BEVEL_WIDTH_M``, ``BEVEL_SEGMENTS`` segments,
    clamp overlap, harden normals; the edge weights come from
    ``parametric.part_bevel_radius`` per part (``edge_bevel_weights``). Faces of
    bevelled and smooth parts are shaded smooth (harden normals keeps the flat
    faces flat), the others flat. The bevel only cuts inwards: the boxes of
    ``parametric`` stay as they are. Returns the manifest record, or None when
    the mesh does not have the parts' faces (left without a bevel)."""
    mesh = ob.data
    radii, smooth = [], []
    for part in parts:
        r = P.part_bevel_radius(part)
        radii.extend([r] * len(part["faces"]))
        smooth.extend([bool(part.get("smooth")) or r > 0.0] * len(part["faces"]))
    if len(radii) != len(mesh.polygons):
        return None
    normals = [tuple(p.normal) for p in mesh.polygons]
    edge_faces: list[list[int]] = [[] for _ in mesh.edges]
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            edge_faces[mesh.loops[li].edge_index].append(poly.index)
    weights = edge_bevel_weights(radii, normals, edge_faces)
    attr = mesh.attributes.get("bevel_weight_edge") or mesh.attributes.new("bevel_weight_edge", "FLOAT", "EDGE")
    attr.data.foreach_set("value", weights)
    for poly, s in zip(mesh.polygons, smooth):
        poly.use_smooth = s
    mod = ob.modifiers.new("bevel", "BEVEL")
    mod.width = P.BEVEL_WIDTH_M
    mod.limit_method = "WEIGHT"
    mod.segments = P.BEVEL_SEGMENTS
    mod.use_clamp_overlap = True
    mod.harden_normals = True
    return {"width_m": P.BEVEL_WIDTH_M, "segments": P.BEVEL_SEGMENTS, "edges": sum(1 for w in weights if w > 0),
            "max_radius_m": round(max(radii, default=0.0), 4)}


def on_surface(item: dict, host: dict | None) -> bool:
    """Milestone 9: decor that rests on its host's built top (found by a ray down onto the host mesh): the
    tabletop types, and books an AI decor slot put on a top (the M4 books keep the shelf or type height)."""
    if host is None:
        return False
    if item.get("type") in P.SURFACE_DECOR_TYPES:
        return True
    return item.get("type") == "book_set" and item.get("method") == "ai" and host.get("type") != "bookshelf"


def surface_points(center, host_center, steps: int = SURFACE_RAY_STEPS) -> list[tuple[float, float]]:
    """The points a surface item tries, in order: its centre, then towards the host centre (pure)."""
    cx, cy = float(center[0]), float(center[1])
    hx, hy = float(host_center[0]), float(host_center[1])
    return [(cx + (hx - cx) * k / steps, cy + (hy - cy) * k / steps) for k in range(steps + 1)]


def _surface_hit(host_entry: dict | None, center, host_center, floor_z: float, above: float):
    """``(z of the topmost host surface, the point used)`` for a surface item: a ray straight down from ``above`` m
    over the floor at the item centre (then towards the host centre) onto the host's built mesh; None when it
    never hits."""
    import bpy
    from mathutils import Vector

    ob = bpy.data.objects.get((host_entry or {}).get("name") or "")
    if ob is None or ob.type != "MESH":
        return None
    inv = ob.matrix_world.inverted()
    down = (inv.to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()
    for x, y in surface_points(center, host_center):
        hit, loc, _normal, _index = ob.ray_cast(inv @ Vector((x, y, floor_z + above)), down)
        if hit:
            return (ob.matrix_world @ loc).z, (x, y)
    return None


# Decor whose fabric takes the item's colour name (the brief's cushion and rug colours, the AI's choice).
BRIEF_COLOURED_DECOR: tuple[str, ...] = ("cushion", "rug")


def decor_lit(item: dict, lamps_on_mood: bool) -> bool:
    """A lamp-type decor item emits light: its ``light_on`` when set, else the mood's ``lamps_on`` (pure)."""
    if item.get("type") not in LAMP_LIGHTS:
        return False
    if isinstance(item.get("light_on"), bool):
        return item["light_on"]
    return lamps_on_mood


def ceiling_above(level: dict, center, size, rotation_deg: float = 0.0) -> tuple[float, str]:
    """``(ceiling height above the floor, how)`` over a footprint (pure): the level's ``ceiling_height``; under a
    roof (``level["ceiling_planes"]``, the sloped attic ceiling the shell builds) the lowest ceiling plane over the
    footprint's corners and centre, so a ceiling light or a pendant meets the slope without passing through it."""
    flat = float(level.get("ceiling_height") or 2.7)
    planes = level.get("ceiling_planes")
    if not planes:
        return flat, "the level's ceiling"
    from wenart.blender import geom2d

    floor_z = float(level.get("elevation") or 0.0)
    points = list(G.rotated_rectangle((float(center[0]), float(center[1])), (float(size[0]), float(size[1])),
                                      float(rotation_deg))) + [(float(center[0]), float(center[1]))]
    z = min(geom2d.surface_z(planes, x, y) for x, y in points) - floor_z
    return round(z, 4), "the sloped ceiling under the roof (its lowest point over the item)"


def _create_decor(item, host, n, level, floor_z, collection, library, mats, assets_dir, pass_indices, host_entry,
                  warnings, geo_cache, skipped: list | None = None, assumed: list | None = None) -> dict | None:
    dtype = item.get("type")
    where = f"on {host['id']}" if host is not None else f"{item.get('id')} (no host)"
    if dtype not in P.DECOR_TYPES:
        warnings.append(f"decor {where}: unknown decor type {dtype!r}; skipped")
        return None
    center = item.get("center") or host["footprint"]["center"]
    rot = float(item.get("rotation_deg", host["footprint"]["rotation_deg"] if host is not None else 0.0))
    w, d, h = P.decor_size(dtype, item.get("size") or [0.4, 0.4])
    size_in = item.get("size") or []
    if dtype not in P.LARGE_DECOR_TYPES and any(float(v) > P.DECOR_MAX_M for v in size_in if v):
        warnings.append(f"decor {dtype} {where}: size {size_in} capped at {P.DECOR_MAX_M} m")
    host_parametric = (host_entry is not None and host_entry.get("kind") == "furniture"
                       and host_entry.get("method") != "library")
    z_above, z_how = decor_height_above_floor(item, host, host_parametric)
    if z_how != "center[2]" and host_entry is not None and host_entry.get("bedding"):
        # Milestone 8: on a library bed frame the item rests on the bedding the builder added.
        z_above, z_how = host_entry["bedding"]["top_m"], f"on the bedding of bed frame {host['id']}"
    if z_how != "center[2]" and on_surface(item, host):
        # Milestone 9: on the host's built top (library or parametric), found by a ray down onto its mesh.
        box = (host_entry or {}).get("bbox_m") or (host_entry or {}).get("size") or [0.0, 0.0, z_above]
        hit = _surface_hit(host_entry, center, host["footprint"]["center"], floor_z, float(box[2]) + 0.5)
        if hit is None:
            reason = f"{dtype} on {host['id']}: no ray down onto the built top hit the piece"
            warnings.append(f"decor {reason}; not built")
            if skipped is not None:
                skipped.append({"id": item.get("id"), "type": dtype, "room_id": item.get("room_id"), "reason": reason})
            return None
        z_above = round(hit[0] - floor_z, 4)
        moved = (abs(hit[1][0] - float(center[0])) > 1e-6 or abs(hit[1][1] - float(center[1])) > 1e-6)
        center = [hit[1][0], hit[1][1]]
        z_how = f"on the built top of {host['type']} {host['id']} (ray" + (", moved towards its centre)" if moved
                                                                             else ")")
    ceiling, ceiling_how = ceiling_above(level, center, (w, d), rot)    # Milestone 10: sloped under a roof
    if dtype == "ceiling_light" and z_how != "center[2]":
        z_above, z_how = round(ceiling - h, 4), f"ceiling (flush, {ceiling_how})"
    if dtype == "pendant_light" and ceiling - z_above > h:
        h = round(ceiling - z_above, 4)                 # Milestone 10: the cord reaches the ceiling
    elif dtype == "pendant_light" and z_above + h > ceiling + 1e-6:
        z_above = round(max(0.0, ceiling - h), 4)       # a low (sloped) ceiling: the shade hangs lower
        z_how = f"hung from {ceiling_how}, lowered to fit"
    if host is not None:
        owner_id, room_id = host["id"], host.get("room_id")
        name = f"decor_{host['id']}_{n}"
        index = pass_indices.get(host["id"]) or pass_indices.get(f"proxy:{host['id']}") or 0
        text = f"{dtype} on {host['type']} {host['id']} ({z_how})"
    else:                                                     # hostless decor: its own id and pass index
        owner_id, room_id = str(item.get("id") or f"decor_{n}"), item.get("room_id")
        name = f"decor_{owner_id}"
        index = pass_indices.get(owner_id) or len(pass_indices) + 1
        pass_indices[owner_id] = index
        text = f"{dtype} in {room_id} on the {z_how}"
    status = item.get("status") or "assumed"
    if status not in ("verified", "unverified", "assumed"):
        status = "assumed"
    footprint = {"center": [float(center[0]), float(center[1])], "size": [w, d], "rotation_deg": rot}
    method = "ai" if item.get("method") == "ai" else "rule"
    evidence = ([dict(e) for e in item.get("evidence") or []] if method == "ai" else [])
    entry = {
        "name": name, "wenart_id": owner_id, "kind": "decor", "status": status, "level_id": level["id"],
        "element_id": owner_id, "host_id": host["id"] if host is not None else None, "room_id": room_id,
        "type": dtype, "source": "added_by_ai", "decor_method": method, "slot": item.get("slot"),
        "colour": item.get("colour"),
        "evidence": evidence or [{"file": "decor", "method": method, "confidence": float(item.get("confidence") or 1.0),
                                  "text": text}],
        "pass_index": index, "assumed": {"rest_height": z_above} if z_how != "center[2]" else {},
        "center": [footprint["center"][0], footprint["center"][1], floor_z + z_above + h / 2.0],
        "size": [w, d, h], "rotation_deg": rot, "asset": item.get("asset"), "method": None, "bbox_m": None,
        "fit_scale": [1.0, 1.0, 1.0], "materials": [], "material": None, "textured": False, "fallback_reason": None,
    }
    file, reason = resolve_asset(item.get("asset"), assets_dir)
    ob = None
    if file is not None:
        try:
            geo = _cached_geometry(file, collection, geo_cache)
            if not geo["faces"]:
                raise ValueError("file has no mesh faces")
            target = [w, d, h] if len(size_in) > 2 else [w, d]
            if (item["asset"].get("target") == "rug" and item["asset"].get("bbox_m")
                    and len(item["asset"]["bbox_m"]) > 2):
                target = [w, d, float(item["asset"]["bbox_m"][2])]   # flat: the rug size, the model's thickness
            if item["asset"].get("target") == "within" and len(item["asset"].get("bbox_m") or []) > 2:
                target = [float(v) for v in item["asset"]["bbox_m"][:3]]   # Milestone 9: the model's own size
            verts, info = fit_vertices(geo["verts"], item["asset"], footprint, floor_z + z_above,
                                       target_size=target)
            fallback = library.proxy("proxy")
            ob = _mesh_object(name, verts, geo["faces"], geo["materials"], geo["face_materials"], collection,
                              owner_id, "decor", status, uvs=geo["uvs"], uv_name=geo["uv_name"],
                              fallback_material=fallback)
            entry.update({"method": "library", "fit_scale": info["fit_scale"], "bbox_m": info["bbox_m"], "fit": info,
                          "file": str(file), "materials": [m.name for m in ob.data.materials if m is not None],
                          "material": ob.data.materials[0].name if ob.data.materials else None,
                          "textured": any(_material_is_textured(m) for m in geo["materials"])})
            entry["size"] = [w, d, info["bbox_m"][2]]
            if item["asset"].get("target") == "within":
                entry["size"] = list(info["bbox_m"])
            entry["center"][2] = floor_z + z_above + info["bbox_m"][2] / 2.0
        except Exception as exc:  # noqa: BLE001
            reason = f"import of {file} failed: {type(exc).__name__}: {exc}"
            warnings.append(f"decor {dtype} {where}: {reason}; parametric mesh used")
            ob = None
    lit = decor_lit(item, bool(getattr(mats, "lamps_on", False)))
    if ob is None:
        parts = P.decor_parts(dtype, w, d, h, item)
        if dtype in BRIEF_COLOURED_DECOR:                # Milestone 10: the cushion and rug colour (brief, AI)
            parts = [dict(part, key=P.COLOUR_PREFIX + part["key"]) if part["key"] == "fabric" else part
                     for part in parts]
        if lit:
            parts = [dict(part, key=f"{LIT_KEY}{part['key']}") if part["role"] == "shade" else part for part in parts]
        verts, faces, keys = P.world_mesh(parts, footprint["center"], rot, floor_z + z_above)
        used_keys = sorted(set(keys), key=keys.index)
        accent = P.DECOR_COLOURS.get(str(item.get("colour") or ""))       # Milestone 9: the AI decor's colour
        overrides = {"pot": pot_override(item)} if dtype == "plant_large" else None
        slots = [_part_material(mats, k, False, accent=accent, colour=item.get("colour"), overrides=overrides,
                                lit=lit) for k in used_keys]
        ob = _mesh_object(name, verts, faces, slots, [used_keys.index(k) for k in keys], collection, owner_id,
                          "decor", status)
        x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
        entry.update({"method": f"parametric (fallback: {reason})", "fallback_reason": reason,
                      "bbox_m": [round(x1 - x0, 4), round(y1 - y0, 4), round(z1 - z0, 4)],
                      "materials": [m.name for m in slots], "material": slots[0].name,
                      "textured": any(mats.library.textured(m) for m in slots), "bevel": add_bevel(ob, parts)})
        if dtype == "plant_large":
            entry["species"] = item.get("species")
            entry["pot"] = dict(overrides["pot"])
        if lit and dtype in LAMP_LIGHTS:
            _lamp_light(dtype, name, ob, footprint["center"], floor_z + z_above, entry,
                        getattr(mats, "collection", None), assumed if assumed is not None else [], owner_id,
                        parts=parts, rotation_deg=rot)
    elif lit and dtype in LAMP_LIGHTS:
        _lamp_light(dtype, name, ob, footprint["center"], floor_z + z_above, entry, getattr(mats, "collection", None),
                    assumed if assumed is not None else [], owner_id)
    if item.get("window_id"):
        entry["window_id"] = item["window_id"]
    if item.get("mirrored_from"):
        entry["mirrored_from"] = item["mirrored_from"]
    ob["wenart_type"] = dtype
    ob["wenart_room"] = room_id or ""
    ob["wenart_source"] = "added_by_ai"
    ob["wenart_host"] = host["id"] if host is not None else ""
    ob["wenart_asset"] = (item.get("asset") or {}).get("asset_id") if entry["method"] == "library" else "parametric"
    ob.pass_index = index
    if item.get("anchor_ids"):
        entry["anchor_ids"] = list(item["anchor_ids"])
        ob["wenart_anchor"] = ",".join(str(a) for a in item["anchor_ids"])
    return entry


def mirror_box(item: dict) -> list[float]:
    """The box of a parametric mirror (pure): the item's width, a portrait height (``MIRROR_ASPECT``, at most the
    item's ``max_height_m``), the frame depth."""
    w = float(item["size"][0])
    h = w * MIRROR_ASPECT
    max_h = item.get("max_height_m")
    if isinstance(max_h, (int, float)) and max_h > 0:
        h = min(h, float(max_h))
    return [w, P.MIRROR_FRAME_M, h]


def clock_box(item: dict) -> list[float]:
    """The box of a parametric wall clock (pure): a round face as wide as the item, ``CLOCK_DEPTH_M`` deep."""
    w = float(item["size"][0])
    return [w, CLOCK_DEPTH_M, w]


def _create_wall_art(item, n, level, floor_z, collection, library, assets_dir, pass_indices, entries, on_level,
                     warnings, geo_cache, skipped: list, mats=None) -> dict | None:
    """One wall art piece (Milestone 8) or mirror (Milestone 9): hostless decor with its own ``wenart_id`` (the
    decor id) and pass index, built from its fitted library model (``asset.bbox_m``) and hung by
    ``wall_art_placement`` over the built top of ``anchor_ids[0]``. Wall art without a model is skipped; a mirror
    without one is the parametric framed mirror (``mirror_box``, ``parametric.decor_parts``). When it cannot hang
    it is skipped and ``skipped`` (the summary's ``decor_skipped``) says why."""
    dtype = item.get("type") or "wall_art"
    label = dtype.replace("_", " ")
    owner_id = str(item.get("id") or f"decor_{n}")
    room_id = item.get("room_id")
    anchors = [str(a) for a in item.get("anchor_ids") or []]
    asset = item.get("asset") or None
    file, reason = resolve_asset(asset, assets_dir)
    parametric = file is None and dtype in PARAMETRIC_WALL_DECOR and mats is not None
    if file is None and not parametric:
        if asset and asset.get("method") == "library":
            warnings.append(f"decor {dtype} {owner_id}: {reason}; not built ({label} has no parametric shape)")
        skipped.append({"id": owner_id, "type": dtype, "room_id": room_id,
                        "reason": f"no library {label} model ({reason}); {label} has no parametric shape"})
        return None
    box = (mirror_box(item) if dtype == "mirror" else clock_box(item)) if parametric else asset.get("bbox_m")
    if not box or len(box) < 3:
        skipped.append({"id": owner_id, "type": dtype, "room_id": room_id,
                        "reason": f"the fitted {label} asset has no 3D box"})
        return None
    host_entry = entries.get(anchors[0]) if anchors else None
    host_top = None
    if host_entry is not None and (host_entry.get("bbox_m") or host_entry.get("size")):
        # the built box above the floor (library or parametric piece; a proxy box behind --proxies)
        host_top = float((host_entry.get("bbox_m") or host_entry["size"])[2])
    elif anchors and any(p["id"] == anchors[0] for p in on_level):
        warnings.append(f"decor {dtype} {owner_id}: piece {anchors[0]} is not built; hung at the item's bottom_m")
    footprint, mount = wall_art_placement(item, box, host_top, float(level.get("ceiling_height") or 2.7))
    if footprint is None:
        skipped.append({"id": owner_id, "type": dtype, "room_id": room_id, "reason": mount["reason"]})
        return None
    index = pass_indices.get(owner_id) or len(pass_indices) + 1
    pass_indices[owner_id] = index
    name = f"decor_{owner_id}"
    w, dp, h = mount["box_m"]
    status = item.get("status") if item.get("status") in ("verified", "unverified", "assumed") else "assumed"
    if parametric:
        parts = P.decor_parts(dtype, w, dp, h, item)
        verts, faces, keys = P.world_mesh(parts, footprint["center"], footprint["rotation_deg"],
                                          floor_z + mount["bottom_m"])
        used = sorted(set(keys), key=keys.index)
        slots = [mats.get(k, accent=P.DECOR_COLOURS.get(str(item.get("colour") or "")), colour=item.get("colour"))
                 for k in used]
        ob = _mesh_object(name, verts, faces, slots, [used.index(k) for k in keys], collection, owner_id, "decor",
                          status)
        x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
        bbox = [round(x1 - x0, 4), round(y1 - y0, 4), round(z1 - z0, 4)]
        info = {"bbox_m": bbox, "fit_scale": [1.0, 1.0, 1.0]}
        materials, textured = [m.name for m in slots], any(mats.library.textured(m) for m in slots)
        method = f"parametric (fallback: {reason})"
    else:
        try:
            geo = _cached_geometry(file, collection, geo_cache)
            if not geo["faces"]:
                raise ValueError("file has no mesh faces")
            verts, info = fit_vertices(geo["verts"], asset, footprint, floor_z + mount["bottom_m"],
                                       target_size=[w, dp, h])
        except Exception as exc:  # noqa: BLE001 - a broken file: no wall decor, loudly
            warnings.append(f"decor {dtype} {owner_id}: import of {file} failed: {type(exc).__name__}: {exc}; "
                            "not built")
            skipped.append({"id": owner_id, "type": dtype, "room_id": room_id,
                            "reason": f"import of {file} failed: {type(exc).__name__}"})
            pass_indices.pop(owner_id, None)
            return None
        ob = _mesh_object(name, verts, geo["faces"], geo["materials"], geo["face_materials"], collection, owner_id,
                          "decor", status, uvs=geo["uvs"], uv_name=geo["uv_name"],
                          fallback_material=library.proxy("proxy"))
        materials = [m.name for m in ob.data.materials if m is not None]
        textured = any(_material_is_textured(m) for m in geo["materials"])
        method = "library"
    host_text = f"over {anchors[0]}" if anchors else "on its wall"
    decor_method = "ai" if item.get("method") == "ai" else "rule"
    evidence = [dict(e) for e in item.get("evidence") or []] if decor_method == "ai" else []
    entry = {
        "name": name, "wenart_id": owner_id, "kind": "decor", "status": status, "level_id": level["id"],
        "element_id": owner_id, "host_id": None, "room_id": room_id, "type": dtype, "source": "added_by_ai",
        "decor_method": decor_method, "slot": item.get("slot"), "colour": item.get("colour"),
        "evidence": evidence or [{"file": "decor", "method": decor_method, "confidence": 1.0,
                                  "text": f"{label} {host_text} ({mount['gap_m']:g} m above its top)"}],
        "pass_index": index, "assumed": {"mount_height": mount["bottom_m"]},
        "center": [footprint["center"][0], footprint["center"][1], floor_z + mount["bottom_m"] + info["bbox_m"][2] / 2.0],
        "size": [info["bbox_m"][0], info["bbox_m"][1], info["bbox_m"][2]], "rotation_deg": footprint["rotation_deg"],
        "asset": asset if not parametric else None, "method": method, "bbox_m": info["bbox_m"],
        "fit_scale": info["fit_scale"], "fit": info, "file": str(file) if file else None, "materials": materials,
        "material": materials[0] if materials else None, "textured": textured,
        "fallback_reason": reason if parametric else None, "mount": mount, "anchor_ids": anchors,
    }
    ob["wenart_type"] = dtype
    ob["wenart_room"] = room_id or ""
    ob["wenart_source"] = "added_by_ai"
    ob["wenart_host"] = ""
    ob["wenart_anchor"] = ",".join(anchors)
    ob["wenart_asset"] = asset.get("asset_id") if (asset and not parametric) else "parametric"
    ob.pass_index = index
    return entry
