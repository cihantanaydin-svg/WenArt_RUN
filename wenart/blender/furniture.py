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

Milestone 12 (docs/milestone12.md §4.1, §4.6-§4.8, §6.4; track S):

- No grey box: an ``unknown`` piece and a library gap (``asset.method == "none"``: no audited model fitted) are not
  built and listed in ``not_built`` (``refused_piece``); ``--proxies`` still builds the Milestone 3 boxes.
- A piece stands on its room's floor (``shell.room_floor_z``: the level's elevation + the room's ``floor_offset_m``,
  sunken or raised; ``piece_floor_z``, the room by ``room_id`` or by the outline holding the piece), and so do floor
  decor, wall art, bed dressings, hosted decor's floor fallbacks and the ``--proxies`` boxes; lights hang from the
  level's ceiling, curtains and blinds stay at their window (``decor_floor``); the built object records
  ``wenart_front_deg`` and ``wenart_method`` for the scene checks.
- Hosted decor rests on the built, scaled host mesh (``_create_hosted_decor`` with ``wenart.blender.rest``): rays
  on the evaluated host (Bevel applied) find the seat, mattress, back, headboard, top or shelf board; a throw is our
  cloth draped on the host (``textiles``); every item is checked (S5) and placed once more, else not built
  (``summary["decor_not_rested"]`` with the measured gap, penetration and support share). No type-table height
  (``decor_rest_height`` is gone).
- A library bed without bedding (a mattress model) gets the procedural duvet and pillows (``_dress_bed``: object
  ``dress_<id>``, the bed's ``wenart_id`` and pass index; decor on the bed rests on it too).
- ``summary["objects"]`` = ``{piece or decor id: object}`` (a dressed bed's bedding as ``<id>#dressing``): the
  scene checks S1-S6 of ``build.py`` (``scene_checks.run_scene_checks``) read them.

Milestone 13 (docs/milestone13.md §3.0 K1, §12 D4, §13.2; track T2): the fallback ladder's middle step. A piece
whose fit says ``asset.method == "module"`` is built by ``wenart.blender.modules.build_module`` from its
``asset.module_plan`` (or the plan computed here from the piece when the fit stored none): a wardrobe run of real
frames, a long table with its chairs, an L sofa of straight modules and a chaise, a kitchen run of base units, a
vanity or shower set. Its manifest entry has ``method: "module"``, ``module`` (builder, products, modules, fit),
the material slots of its parts and the bevel record; the object carries ``wenart_method = "module"`` and
``wenart_module``; the summary counts it under ``by_method["module"]``. The last step, the parametric families v2
of ``wenart.blender.parametric`` (``FAMILY_TYPES``), runs through the parametric path as before, so every piece
built below the library level is either ``module`` or ``parametric`` and the report can list it.

Build round 2 (15 Oct 2026; docs/milestone13.md §3.0 K2, §12 D2):

- HSSD models (``library: hssd``, CC BY-NC 4.0, the relaxed licence mode of pod P2) pass the model gate when the fit
  recorded the catalogue's ``licence_flag: non_commercial`` (``SOURCE_FLAGS``) and the credit fields; the licence
  check of the fit (``wenart.furniture.catalog.usable``) decided the mode, the gate only refuses what no mode may
  build (a wrong licence text, a missing flag or credit line).
- Uniform scaling (K2): the fit scales a model by the drawn width only, so its depth may differ from the footprint
  by up to the fit's cap (``asset.cap``, 10-15 %; ``asset.scaling == "uniform"``, ``asset.depth_abs_m``). A piece of a
  wall-backed type (``WALL_BACKED_TYPES``, or ``against_wall: true`` on the piece) keeps its back edge on the
  footprint's back edge and the difference goes to the front (``depth_alignment``, ``fit_vertices(align="back")``);
  every other piece stays centred. The depth warning of such a fit fires only beyond the cap
  (``fit_mismatch_warnings``); a non-uniform fit (an older building) keeps the 1 cm rule on both axes. The manifest
  entry's ``fit.depth_align`` records the mode, the shift and the depth difference.

Fix round after P4a (17 Oct 2026; the asks of the rig track, applied at integration):

- A library mirror's glass is a real mirror: ``_create_wall_art`` builds a mirror model from
  ``materials.mirror_glass_materials`` (the neutral grey glass texels of the model's own albedo get the vocabulary
  mirror; the frame keeps its maps) through ``wall_art_materials``, never changing the cached geometry's list; the
  entry records ``mirror_glass`` (material name -> ``texture`` | ``all`` | ``none``). P4a's ABO bathroom mirrors
  rendered as matte grey panels.
- A pendant keeps its shade bottom where the decor stage put it (over a dining table's top, above head height) and
  its cord ends at the ceiling over its slot (``pendant_hang``); under a ceiling less than ``PENDANT_MIN_DROP_M`` above
  that bottom it is not built (``decor_skipped``, warning "ceiling X m over its slot too low"). Before, the shade
  was lowered to fit under the slope: P4a's dec_L1_006 rested 0.244 m above the floor, through table f_L1_045.

Fix round after P4b (17 Oct 2026; the review of the P4a fix round, track R_rig):

- Every decor entry of the scene manifest records ``decor_id``, the item's own id: ``_create_decor`` (a lamp, a
  pendant, a curtain, a floor plant, or a hosted item the builder places without rays) and ``_create_wall_art`` as
  ``_create_hosted_decor`` already did. A hosted item's ``element_id`` and ``wenart_id`` stay its host's (one pass
  index per piece), so ``lighting.built_decor_boxes`` keys decor by ``decor_id``: P4a's fix round keyed it by the
  host, and the rig lamp stood through the plant on its own nightstand unflagged.

28 Oct 2026 (user on real04 run 20261028-005318-full: "still flying pillows all around", "More flying pillows", "I did
not like this bed", "Light is flying in the air needs to be connected to ceiling"):

- A decor cushion on a dressed bed finds its back with the bed alone (``BED_CASTER``: it stands on the pillows against
  the headboard), then with the bed and its pillows (``LEAN_CASTER``: it leans back on them); its seat and S5 see the
  whole bedding as built (``rest.plan_decor`` with ``back_caster``). Before, the lean caster was the only caster: the
  cushions stood on the bare mattress inside the duvet's head edge (S5 on the built bedding: 4.9 cm, critical).
- A throw on a bed whose final model has its own made bedding (``rest.own_bedding``) is not built (``decor_skipped``).
- A pendant or ceiling light reaches the ceiling over it (``hang_plan``): a library model fitted to its own size is
  lifted to the ceiling (a ceiling light; a pendant whose top is at most ``PENDANT_LIFT_MAX_M`` under it), else it
  gets a cord and a ceiling canopy (``parametric.suspension_parts``, object ``<name>_cord``, ``entry["suspension"]``);
  ``entry["hang"]`` records the numbers (``gap_left_m``) for S5, the model review (M14) and Argus.

29 Oct 2026 (lesson UL121, the user's photo of a full, soft bed; docs/reference_details_20261029.md R35, R36):

- A dressed bed takes its style family's full set (``_dress_bed`` with the building: ``textiles.bedding_set``; the
  decor stage's ``bedding_layers.set`` or the family's at build time, ``bed_bedding_spec``): shams, standing pillows,
  accent cushions and a lumbar in the AI's cushion colours, a soft deep duvet hanging almost to the floor on each free
  side (``bedding_parts.bed_sides``), still one mesh with a material slot per fabric (``dressing_mesh`` keys
  ``<key>|<colour>``, ``split_key``); the decor cushions on such a bed are not built twice (``decor_skipped``). A
  made-up library bed is measured first (``own_bedding_candidate``, ``_bedding_test``: ``bedding_parts.bedding_relief``
  on its vertices, one ``foreach_get``): a flat cover is dressed in the full set, a duvet without pillows gets the
  pillow set (``mode`` pillows), the rest is kept (``entry["bedding_test"]``); the decor stage's throw for it
  (``when_dressed``) is built only over our dressing. ``summary["bedding"]``: each dressed bed's set and seconds.
- A bed's throw is the woven pair (``textiles.woven_throw_parts``; the decor stage's ``weave``, else the family's): the
  pattern's ink and angle reach its material (``part_params``), the second blanket takes the accent colour
  (``part_colour``: ``colour_runner_<look>`` keys); ``entry["weave"]`` records the pattern and the fringe as built.
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Sequence

from wenart import geometry as G
from wenart.blender import kitchen_details as KD
from wenart.blender import modules as MOD
from wenart.blender import parametric as P
from wenart.blender import proxies
from wenart.blender.proxies import COINCIDENT_LIFT, footprints_overlap, mount_bottom, proxy_height

CC0 = "CC0"
CC_BY = "CC-BY-4.0"
LIBRARIES = ("polyhaven", "abo", "objaverse", "generated", "gso", "hssd", "3dwh", "parametric")
# Licence gate of the model kind (docs/milestone7.md §6.3, docs/milestone8.md §2; the rule of
# wenart.assets.fetch.check_licence with kind "models", repeated here because Blender's Python imports this
# module without the asset code). Generated models carry the licence text "generated (<model>, <licence>)".
MODEL_LICENCES = {"polyhaven": (CC0,), "abo": (CC_BY,), "objaverse": (CC0, CC_BY), "generated": (),
                  "gso": (CC_BY,),   # gso: Google Scanned Objects (Milestone 12 pod P4, CC BY 4.0 per object)
                  # hssd: the HSSD object models (Milestone 13 pod P2, docs/milestone13.md §12 D2; CC BY-NC 4.0 per the
                  # dataset card, relaxed licence mode only; = wenart.assets.hssd.LICENCE)
                  "hssd": ("CC-BY-NC-4.0",),
                  # 3dwh: the 3D Warehouse models of the user's zip (23 Oct 2026; licences not reviewed by the user's
                  # decision, relaxed licence mode only; = wenart.assets.warehouse.LICENCE)
                  "3dwh": ("3DWH-UNREVIEWED",)}
GENERATED_LICENCE_PREFIX = "GENERATED"
# Milestone 8: sources whose other licences pass when the catalogue flagged them (recorded, not filtered); Milestone 13:
# the HSSD layer the same way (its one licence is flagged non_commercial).
FLAGGED_SOURCES = ("objaverse", "hssd", "3dwh")
# The flag a source's every model must carry (the dataset's terms, not a per-object licence): an HSSD asset without
# ``licence_flag: non_commercial`` was not fitted through the Milestone 13 catalogue and is refused.
SOURCE_FLAGS = {"hssd": "non_commercial", "3dwh": "non_commercial"}
# Milestone 13 (§13.3): the catalogue's flag words (``wenart.furniture.catalog.LICENCE_FLAGS`` without ``none``).
LICENCE_FLAGS = ("non_commercial", "share_alike", "no_derivatives", "research_only", "regional", "tool_nc", "unknown")
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
TOWEL_DECOR_KEY = "colour_towel"   # 29 Oct 2026 (UL124 B26): a decor towel takes the item's towel_colour
TOWEL_DECOR_KEYS = (TOWEL_DECOR_KEY, TOWEL_DECOR_KEY + "_alt", TOWEL_DECOR_KEY + "_band")   # 30 Oct 2026 (UL138)


def towel_part_colour(item: dict, key: str):
    """The colour phrase of a decor towel part (pure; 30 Oct 2026, UL138): the item's towel colour, its second shade
    for ``colour_towel_alt`` (``towel_parts.towel_shade``), None for any other key."""
    from wenart.blender import towel_parts as TP

    if key not in TOWEL_DECOR_KEYS:
        return None
    colour = item.get("towel_colour")
    return TP.towel_shade(colour) if key.endswith(TP.ALT_KEY_SUFFIX) else colour
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
# Build round 2 (K2): the depth mismatch a uniform fit may carry when the asset records no cap of its own
# (= wenart.furniture.fit.NON_UNIFORM_CAP, repeated: Blender's Python imports this module without the fit code).
UNIFORM_DEPTH_CAP = 1.10
# Types whose back normally stands on a wall (= wenart.furniture.schemas.WALL_TYPES, repeated: that module needs
# jsonschema; tests/test_blender_furniture.py keeps them equal, and every ``place: wall`` anchor of groups.yaml is
# among them): a uniformly scaled model of such a type keeps its back edge on the footprint's back edge.
WALL_BACKED_TYPES = (
    "bed_single", "bed_double", "sofa", "wardrobe", "kitchen_counter", "tv_unit", "bookshelf", "dresser",
    "fridge", "stove", "sink_kitchen", "washbasin", "toilet", "shower", "bathtub", "washing_machine", "desk",
    "sofa_corner", "bunk_bed", "console_table", "sideboard", "shoe_cabinet", "display_cabinet", "tall_cabinet",
    "wall_cabinet",
)
DEPTH_ALIGNMENTS = ("centre", "back")
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
    # a flagged licence outside the list passes for a source of any uploader licence (Objaverse); a source whose
    # terms are one licence (``SOURCE_FLAGS``: HSSD) has a closed list, its flag never opens it
    if text not in allowed and not (flagged and source not in SOURCE_FLAGS):
        return f"asset {asset.get('asset_id')!r} licence {licence!r} is not {' or '.join(allowed)}; refused"
    want_flag = SOURCE_FLAGS.get(source)
    if want_flag and asset.get("licence_flag") != want_flag:
        return (f"asset {asset.get('asset_id')!r} from {source} must carry licence_flag {want_flag!r} (the dataset's "
                f"terms), not {asset.get('licence_flag')!r}; refused")
    if text.startswith("CC-BY"):          # CC BY 4.0 and its NC / SA variants all ask for the credit line (§3(a)(1))
        missing = [k for k in CC_BY_FIELDS if not str(asset.get(k) or "").strip()]
        if missing:
            return f"asset {asset.get('asset_id')!r} is CC BY 4.0 without {', '.join(missing)} (no credit line); refused"
    return None


def is_built(piece: dict) -> bool:
    """False for a piece with ``build: false`` (docs/milestone7.md §3.3): it stays in the building, unbuilt."""
    return piece.get("build", True) is not False


def not_built_reason(piece: dict) -> str:
    """Integration of the fix round after P5 (P_report's ask): the actual reason a ``build: false`` piece is not built,
    in the order of ``wenart.report.final.not_built_text`` (the scene manifest and the report agree): its
    ``not_built_reason``, the reading's ``inferred_reason`` (a column, an outline, a detail), the agent's or the
    code's ``adjusted_by_ai`` record (a mark with its model and round), both recognition passes calling it
    ``not_furniture`` (``NOT_BUILT_REASON``), else "build false, no reason recorded". Before, every piece carried
    ``NOT_BUILT_REASON`` (P5: A-BA columns typed ottoman, never-asked unknowns and the agent's mark of f_L1_021).

    Fix round after P5 (22 Oct 2026), review: the order of ``not_built_text`` after the report review fix: a later
    mark (``adjusted_by_ai.not_furniture``) follows the reading's reason: "<not_built_reason or inferred_reason>; then
    marked not furniture (<kind>) by <model>, round n: <reason>" (the by/round part only when a model is recorded); a
    record that is no mark never replaces the reason (P5 f_L1_017/018 read only "untyped")."""
    adj = piece.get("adjusted_by_ai") if isinstance(piece.get("adjusted_by_ai"), dict) else {}
    base = piece.get("not_built_reason") or piece.get("inferred_reason")
    if base and adj.get("not_furniture") and not (adj.get("by") == "code"
                                                 and str(adj.get("reason") or "") in str(base)):
        # the review of the reading fixes: a mark the code made with the reason it wrote as not_built_reason (a seat
        # cushion of reading.seat_cushions) is the base itself, not a later decision
        who = f" by {adj['model']}, round {adj.get('round')}" if adj.get("model") else ""
        return (f"{base}; then marked not furniture ({adj['not_furniture']}){who}: "
                f"{adj.get('reason') or 'no reason recorded'}")
    if base:
        return str(base)
    if adj.get("not_furniture") or adj.get("reason"):
        who = f" by {adj['model']}, round {adj.get('round')}" if adj.get("model") else ""
        what = (f"marked not furniture ({adj['not_furniture']}){who}" if adj.get("not_furniture")
                else f"adjusted_by_ai{who}")
        return f"{what}: {adj.get('reason') or 'no reason recorded'}"
    answers = [str(c.get("type")) for c in piece.get("type_candidates") or [] if isinstance(c, dict)]
    if len(answers) >= 2 and set(answers) == {"not_furniture"}:
        return NOT_BUILT_REASON
    return "build false, no reason recorded"


BUILT_IN_REASON = "built into its kitchen run (the run's sink unit, bowl and tap; fix round after P3)"


def built_in_ids(pieces: Sequence[dict]) -> dict[str, str]:
    """``{piece id: run id}`` of the pieces a built kitchen run builds into itself (pure; fix round after P3,
    16-17 Oct 2026): a piece whose ``asset.built_in`` names a built, typed piece of ``pieces`` (the level's) whose
    fitted module plan lists it under ``built_ins`` (``wenart.furniture.fit.kitchen_built_ins``). The scene builds
    such a piece once, as the run's sink unit, never again as its own object (P3 built the drawn sink inside the
    base units). When the run's plan does not hold it (the agent refitted the run without the hints), the piece is
    built on its own as before."""
    by_id = {p.get("id"): p for p in pieces}
    out: dict[str, str] = {}
    for p in pieces:
        host_id = (p.get("asset") or {}).get("built_in")
        host = by_id.get(host_id) if host_id else None
        if host is None or host is p or not is_built(host) or refused_piece(host):
            continue
        plan = (host.get("asset") or {}).get("module_plan") or {}
        if any(isinstance(b, dict) and b.get("id") == p.get("id") for b in plan.get("built_ins") or []):
            out[str(p["id"])] = str(host_id)
    return out


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
                 target_size: Sequence[float] | None = None, align: str = "centre",
                 join: tuple | None = None) -> tuple[list, dict]:
    """Asset-frame vertices -> world vertices on the footprint.

    Steps: rotate into the piece frame, re-centre (XY box centre to the
    origin, bottom to z = 0), scale by ``fit_scale`` (or to ``target_size``
    for decor), rotate by ``footprint.rotation_deg`` and move to
    ``footprint.center`` at ``floor_z``. Returns the vertices and a record
    with the measured boxes before and after the fit, the offsets applied
    and the scale used.

    An Objaverse asset's ``unit_scale`` (raw GLB units -> metres, the prep
    pod's unit guess; 1.0 when absent) is applied first: its catalogue boxes,
    and so ``fit_scale``, are in metres.

    Build round 2 (K2): ``align="back"`` keeps the fitted box's back edge (piece frame +Y) on the footprint's back
    edge (+ depth / 2), so a uniformly scaled model that is deeper or shallower than the drawn depth differs at its
    front, never behind (a sofa stays on its wall); ``"centre"`` (the default, and every decor fit) centres the box
    on the footprint as before. The record's ``depth_align`` says which and by how much the box was shifted.

    30 Oct 2026 (lesson UL140, user: "also the gaps need a rework"): ``join`` = ``(vertex parts, part areas)`` of
    ``soft_seats.vertex_parts`` joins the model's loose parts in the piece frame before the fit (``soft_seats
    .join_parts``: the bodies that face each other across a small gap move together); a uniform fit then keeps the
    drawn width (its one scale grows by the width the gaps took) and the record's ``parts`` holds the gaps before and
    after. The fit itself was never the cause: one uniform scale about one pivot for every part."""
    u = float(asset.get("unit_scale") or 1.0)
    if u != 1.0:
        verts = [(v[0] * u, v[1] * u, v[2] * u) for v in verts]
    R = frame_rotation(asset.get("front_axis"), asset.get("up_axis"))
    local = [apply_rotation(R, v) for v in verts]
    joined = None
    if join is not None:
        from wenart.blender import soft_seats as SS
        local, joined = SS.join_parts(local, join[0], join[1])
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
        if (joined and joined.get("joined") and asset.get("scaling") == "uniform" and raw_bbox[0] > 1e-9
                and joined.get("width_before_m")):
            keep = float(joined["width_before_m"]) / raw_bbox[0]       # the drawn width, kept by the one scale
            scale = [s * keep for s in scale]
            joined["width_kept_scale"] = round(keep, 5)
    local = [(x * scale[0], y * scale[1], z * scale[2]) for x, y, z in local]
    fx0, fy0, fz0, fx1, fy1, fz1 = _bounds(local)
    fitted = [fx1 - fx0, fy1 - fy0, fz1 - fz0]
    if align not in DEPTH_ALIGNMENTS:
        raise ValueError(f"align must be one of {DEPTH_ALIGNMENTS}, not {align!r}")
    want_depth = float(footprint["size"][1]) if len(footprint.get("size") or []) > 1 else fitted[1]
    shift_y = round((want_depth - fitted[1]) / 2.0, 6) if align == "back" else 0.0
    if shift_y:
        local = [(x, y + shift_y, z) for x, y, z in local]
    depth_align = {"mode": align, "shift_m": round(shift_y, 4), "depth_abs_m": round(fitted[1] - want_depth, 4)}
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
        "fit_scale": [round(v, 4) for v in scale], "unit_scale": u, "depth_align": depth_align,
    }
    if joined is not None:
        info["parts"] = joined
    return world, info


def fit_normals(face_normals: Sequence, asset: dict, footprint: dict, scale: Sequence[float] = (1.0, 1.0, 1.0)
                ) -> list:
    """The file's corner normals (``import_gltf_geometry``'s ``face_normals``: None for a flat face) turned as
    ``fit_vertices`` turns the vertices (pure; 30 Oct 2026, UL131): the frame rotation, the inverse of a non-uniform
    scale (a uniform one changes no normal), the footprint's rotation; renormalised."""
    R = frame_rotation(asset.get("front_axis"), asset.get("up_axis"))
    rad = math.radians(float(footprint["rotation_deg"]))
    c, s = math.cos(rad), math.sin(rad)
    inv = [1.0 / float(v) if abs(float(v)) > 1e-12 else 1.0 for v in (list(scale) + [1.0, 1.0, 1.0])[:3]]
    uniform = abs(inv[0] - inv[1]) < 1e-9 and abs(inv[1] - inv[2]) < 1e-9
    out = []
    for face in face_normals:
        if face is None:
            out.append(None)
            continue
        row = []
        for n in face:
            x, y, z = apply_rotation(R, n)
            if not uniform:
                x, y, z = x * inv[0], y * inv[1], z * inv[2]
                ln = math.sqrt(x * x + y * y + z * z) or 1.0
                x, y, z = x / ln, y / ln, z / ln
            row.append((c * x - s * y, s * x + c * y, z))
        out.append(row)
    return out


def depth_alignment(piece: dict, asset: dict | None = None) -> str:
    """How a fitted library model sits in its footprint's depth (pure, build round 2 K2): ``back`` for a uniformly
    scaled model (``asset.scaling == "uniform"``) of a wall-backed type (``WALL_BACKED_TYPES``; the piece's own
    ``against_wall`` true / false, or the solver's ``layout.against_wall``, wins when it says so), else ``centre`` (a non-uniform fit of an older building was
    stretched to the footprint; a free-standing piece keeps its drawn centre)."""
    asset = piece.get("asset") if asset is None else asset
    if not isinstance(asset, dict) or asset.get("scaling") != "uniform":
        return "centre"
    against = piece.get("against_wall")
    if not isinstance(against, bool):
        # 23 Oct 2026 (group options 10x): a solver piece says it in ``layout`` (a reading-corner armchair, a hall
        # bench or plant set on a wall: types that are free-standing elsewhere)
        against = (piece.get("layout") or {}).get("against_wall") if isinstance(piece.get("layout"), dict) else None
    if isinstance(against, bool):
        return "back" if against else "centre"
    return "back" if piece.get("type") in WALL_BACKED_TYPES else "centre"


def depth_cap(asset: dict | None) -> float:
    """The depth mismatch ratio a uniform fit may carry: the fit's own ``cap`` (10 %, or the relaxed 15 % of the
    ladder) when the asset records one, else ``UNIFORM_DEPTH_CAP``."""
    cap = (asset or {}).get("cap") if isinstance(asset, dict) else None
    if isinstance(cap, (int, float)) and not isinstance(cap, bool) and math.isfinite(cap) and cap >= 1.0:
        return float(cap)
    return UNIFORM_DEPTH_CAP


def fit_mismatch_warnings(piece_id: str, asset: dict, footprint_size: Sequence[float],
                          bbox_m: Sequence[float]) -> list[str]:
    """The warnings of a fitted box against its footprint (pure): the width within ``FIT_TOLERANCE_M`` always (the
    fit scales to the drawn width); the depth within ``FIT_TOLERANCE_M`` for a non-uniform fit, and for a uniform
    fit (``asset.scaling == "uniform"``) within the fit's cap (``depth_cap``: the ratio either way, the rule of
    ``wenart.furniture.fit.scale_for``), because the layout absorbs that difference by design (K2)."""
    out = []
    uniform = isinstance(asset, dict) and asset.get("scaling") == "uniform"
    for axis, want, got in (("width", float(footprint_size[0]), float(bbox_m[0])),
                            ("depth", float(footprint_size[1]), float(bbox_m[1]))):
        if abs(want - got) <= FIT_TOLERANCE_M:
            continue
        if axis == "depth" and uniform:
            cap = depth_cap(asset)
            ratio = max(want, got) / min(want, got) if min(want, got) > 1e-9 else math.inf
            if ratio <= cap + 1e-6:
                continue
            out.append(f"{piece_id}: fitted asset {asset.get('asset_id')!r} depth {got:.3f} m differs from the "
                       f"footprint {want:.3f} m by more than the fit's cap of {round((cap - 1) * 100)} % "
                       f"(uniform scale; not adjusted)")
            continue
        out.append(f"{piece_id}: fitted asset {asset.get('asset_id')!r} {axis} {got:.3f} m differs "
                   f"from the footprint {want:.3f} m by more than {FIT_TOLERANCE_M} m (not adjusted)")
    return out


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
        # 29 Oct 2026 (UL120): a see-through wardrobe's smoked glass (``_Materials.get`` -> library.smoked_glass)
        "smoked_glass": ("glass", None, None),
        "mirror": ("mirror", None, None),                     # Milestone 9: the parametric mirror's glass
        # Milestone 10: cabinet fronts (the trim's paint unless a design says otherwise), handles, a marble table
        # top, plant pots, lamp bulbs (frosted when off), rattan.
        "front": (trim, None, None), "handle": ("steel_brushed", None, None), "marble": ("marble", None, None),
        "pot": ("terracotta", None, None), "bulb": ("ceramic_white", None, None),
        "rattan": ("rattan", None, None),
        # 30 Oct 2026 (UL160): a holdall's tan leather handles, tabs, piping and base band (holdall.LEATHER)
        "leather": ("leather_tan", None, None),
        # 29 Oct 2026 (lesson UL93): a laptop's or a monitor's screen; the build gives the key its own material (a
        # dark glossy panel with a faint lit wallpaper: ``_Materials.get`` -> materials.screen_material), the dark
        # lacquer is the slug its records name; a TV's screen (UL99) takes the same material
        "screen": ("screen_black", None, None),
        # 30 Oct 2026 (UL175): the desktop a switched-on screen shows (materials.screen_ui_material; the record's slug
        # is the screen's)
        "screen_ui": ("screen_black", None, None),
        # 29 Oct 2026 (UL106): the sheer layer of a layered curtain (materials.sheer_material: see-through voile)
        "sheer": (SHEER_SLUG, None, None),
        # 29 Oct 2026 (UL114, UL123, UL124: the bathroom details): an LED strip (the build gives the key its own
        # material: materials.led_material), a light stone and a terrazzo top or panel, the towels (white unless the
        # piece's design names the room's towel colour: design_overrides)
        "led": (LED_SLUG, None, None),
        "stone_light": ("marble", _vocab_asset("marble"), None),
        "terrazzo": ("terrazzo", _vocab_asset("terrazzo"), None),
        # 30 Oct 2026 (UL138): the towels' terry cloth, a stack's second shade and a hanging towel's woven band
        # (towel_parts: ``<key>_alt``, ``<key>_band``)
        "towel": ("fabric_terry", None, None), "towel_alt": ("fabric_terry", None, None),
        "towel_band": ("fabric_cotton", None, None),
        # 29 Oct 2026 (UL113, UL115): dried pampas plumes (a cream linen); the reference details' LED strips take
        # the "led" key above (detail_parts.led_strip_material is materials.led_material)
        "pampas": ("fabric_linen", asset_of("fabric_linen"), None),
        # 30 Oct 2026 (UL154): a book's cream page block and paper labels (book_parts; the covers are bookcloth:
        # ``cloth:linen:<colour>`` keys, the bedding's linen in a cover colour)
        "paper": ("book_pages", None, None),
        # 30 Oct 2026 (UL183, UL186: small_parts): fruit skins, the oil in a bottle, a paper roll's cardboard core
        "fruit_red": ("fruit_red", None, None), "fruit_orange": ("fruit_orange", None, None),
        "fruit_yellow": ("fruit_yellow", None, None), "fruit_green": ("fruit_green", None, None),
        "oil": ("oil_amber", None, None), "cardboard": ("cardboard", None, None),
    }
    # 29 Oct 2026 (UL121, R35): the bedding's fabric looks and woven patterns (``textile_<look>``; a throw pair's second
    # blanket ``runner_<look>``): linen keeps its Poly Haven scan, the others are the procedural weaves
    from wenart.blender import bedding_parts as BP

    keys.update({k: (slug, asset_of(slug) or _vocab_asset(slug), None) for k, slug in BP.material_keys().items()})
    return keys, assumed


LED_SLUG = "led_strip"            # the led key's slug in the records (materials.led_material)


def _vocab_asset(slug: str):
    """The vocabulary's texture set of a slug (None without the style tables)."""
    try:
        from wenart.style import vocabulary as V
        return ((V.MATERIALS.get(slug) or V.FURNITURE_MATERIALS.get(slug)) or {}).get("asset")
    except Exception:  # noqa: BLE001
        return None


SHEER_SLUG = "fabric_sheer"       # the sheer key's slug: the library's translucent voile (MaterialLibrary.sheer)


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
    if design.get("towel_colour"):            # 29 Oct 2026 (UL124 B26): the room's towels in its accent colour
        from wenart.blender import towel_parts as TP

        colour = design["towel_colour"]          # 30 Oct 2026 (UL138): terry, its second shade, the woven band
        out["towel"] = {"slug": TP.TERRY_SLUG, "asset": None, "colour": colour}
        out["towel_alt"] = {"slug": TP.TERRY_SLUG, "asset": None, "colour": TP.towel_shade(colour)}
        out["towel_band"] = {"slug": TP.BAND_SLUG, "asset": None, "colour": colour}
        notes.append(f"towels {colour}")
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
    bath = [p for p in parts if p["role"] in ("led", "button", "towel", "bottle", "jar", "pebble", "perfume",
                                              "hand_shower", "rosette")]
    if bath and piece_type in ("toilet", "washbasin", "tall_cabinet", "shower"):
        roles = sorted({p["role"] for p in bath})
        return [{"field": "bath_details", "kind": "bath_details", "value": ", ".join(roles),
                 "reason": "the bathroom details of the piece (UL114, UL123, UL124: LED strips, a flush plate, "
                           "towels and toiletries, shower fittings) inside its own box, one mesh"}]
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


def decor_height_above_floor(item: dict, host_entry: dict | None = None) -> tuple[float, str]:
    """Rest height of a decor item the builder places without rays (pure): its own ``center[2]`` (a curtain's
    bottom, a light's) when given, else the floor; Milestone 12: no type-table height any more (hosted decor rests on
    the built mesh, ``rest.plan_decor``); only a decor item on a Milestone 3 proxy box (``--proxies``, debugging)
    rests on the box's top."""
    center = item.get("center") or []
    if len(center) > 2 and center[2] is not None:
        return float(center[2]), "center[2]"
    if host_entry is not None and host_entry.get("kind") == "furniture_proxy":
        return float((host_entry.get("size") or [0.0, 0.0, 0.0])[2]), "on the proxy box's top (--proxies)"
    return 0.0, "floor"


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
    if isinstance(item.get("min_bottom_m"), (int, float)):
        bottom = max(bottom, float(item["min_bottom_m"]))     # 29 Oct 2026 (R32): over a headboard panel
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

TWIN_DIGITS = 4              # vertex positions rounded to 0.1 mm to find a face's turned copy
TWIN_OFFSET_M = 0.0002       # each copy moves this far along its own normal


def _newell(pts) -> tuple:
    nx = ny = nz = 0.0
    for a, b in zip(pts, pts[1:] + pts[:1]):
        nx += (a[1] - b[1]) * (a[2] + b[2])
        ny += (a[2] - b[2]) * (a[0] + b[0])
        nz += (a[0] - b[0]) * (a[1] + b[1])
    n = math.sqrt(nx * nx + ny * ny + nz * nz)
    return (nx / n, ny / n, nz / n) if n > 1e-12 else (0.0, 0.0, 0.0)


def backface_twins(verts, faces) -> set:
    """Indices of the faces that have a copy on the same vertices turned the other way (pure; 25 Oct 2026: a
    double-sided export, SketchUp's front face and its back face of another colour at the same place; real04's
    corner sofa "Sofa en L" had 99 % of its faces so and rendered with dark bands where the two copies fight)."""
    groups: dict = {}
    normals = []
    # 29 Oct 2026: each vertex converted and rounded once (it was once per face it is in: 90 s a build on real06)
    pos = [tuple(float(c) for c in v) for v in verts]
    keys = [tuple(round(c, TWIN_DIGITS) for c in p) for p in pos]
    for i, f in enumerate(faces):
        normals.append(_newell([pos[k] for k in f]))
        groups.setdefault(tuple(sorted(keys[k] for k in f)), []).append(i)
    out = set()
    for ids in groups.values():
        for i in ids if len(ids) > 1 else ():
            if any(sum(a * b for a, b in zip(normals[i], normals[j])) < 0 for j in ids if j != i):
                out.add(i)
    return out


def separate_twins(verts, faces, offset: float = TWIN_OFFSET_M) -> tuple[list, list, int]:
    """``(verts, faces, n)``: the faces of ``backface_twins`` moved ``offset`` along their own normals (pure), so
    the copy that faces the camera is always the nearer one and shows its own colour from either side (a ray no
    longer meets two faces at one depth). A vertex gets one moved copy per side (the faces' main axis and its
    sign), along the average normal of that side's faces; library pieces are shaded flat, so the look is the
    model's, and a crack between two sides is at most ``offset`` wide."""
    twins = backface_twins(verts, faces)
    if not twins:
        return list(verts), [list(f) for f in faces], 0
    verts = [tuple(float(c) for c in v) for v in verts]
    faces = [list(f) for f in faces]
    side_sum: dict = {}
    normals = {}
    for i in twins:
        n = _newell([verts[k] for k in faces[i]])
        normals[i] = n
        for k in faces[i]:
            key = (k, max(range(3), key=lambda a: abs(n[a])), n[max(range(3), key=lambda a: abs(n[a]))] > 0)
            acc = side_sum.setdefault(key, [0.0, 0.0, 0.0])
            for a in range(3):
                acc[a] += n[a]
    new_index: dict = {}
    for i in sorted(twins):
        n = normals[i]
        axis = max(range(3), key=lambda a: abs(n[a]))
        out = []
        for k in faces[i]:
            key = (k, axis, n[axis] > 0)
            if key not in new_index:
                s = side_sum[key]
                ln = math.sqrt(sum(c * c for c in s)) or 1.0
                v = verts[k]
                new_index[key] = len(verts)
                verts.append(tuple(v[a] + offset * s[a] / ln for a in range(3)))
            out.append(new_index[key])
        faces[i] = out
    return verts, faces, len(twins)


def import_gltf_geometry(path: Path, collection, normals: bool = False, parts: bool = False) -> dict:
    """Import a glTF/GLB and return its merged geometry in the file's
    (Z-up) frame: ``{"verts", "faces", "materials", "face_materials", "uvs",
    "uv_name", "objects", "backface_twins"}``. The imported objects are deleted again; the
    materials (and packed images) stay in ``bpy.data`` for the new object. The faces of a double-sided export
    are moved apart from their turned copies (``separate_twins``; ``backface_twins`` counts them).

    30 Oct 2026 (lessons UL131, UL140): with ``normals`` the file's own shading comes along: ``face_normals`` (per
    face: None for a flat face, else its corners' normals in world space, the importer's split normals turned by the
    parts' normal matrices) and ``file_smooth`` (how many faces the file shades smooth); the rebuilt mesh used to be
    flat everywhere (a smooth cushion of 528 faces: 0 smooth after the rebuild), so rounded cushions showed their
    facets. With ``parts`` the loose parts of the model (``face_parts``: ``soft_seats.face_parts``, measured before the
    twins are separated, which splits every double-sided face off its neighbours).

    29 Oct 2026 (real06 run 100801: two pendant lights of about 30,000 parts each took 475 s and 443 s of a build's
    1,160 s furniture phase; profile pod 20261029-150820-profile_build): the same geometry, read without a cost per
    part that grows with the scene. The parts stay where the importer put them (in the view layer) and are read in
    world space (``matrix_world`` holds the parents), each evaluated mesh through ``to_mesh`` and ``foreach_get``
    (no mesh datablock per part), their materials from the object's slots (the originals), and all of them are
    removed in one ``batch_remove`` (one at a time, each removal scanned the whole file: 570 s). ``collection`` is
    kept for the callers."""
    import bpy
    import numpy as np

    before = {o.name for o in bpy.data.objects}
    bpy.ops.import_scene.gltf(filepath=str(path), import_shading="NORMALS", import_scene_as_collection=False,
                              import_select_created_objects=False)
    new = [o for o in bpy.data.objects if o.name not in before]
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    verts, faces, materials, face_materials, uvs = [], [], [], [], []
    face_normals: list = []
    mat_index: dict = {}
    uv_name = None
    for ob in new:
        if ob.type != "MESH":
            continue
        ev = ob.evaluated_get(depsgraph)
        me = ev.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
        try:
            mw = np.array(ob.matrix_world, dtype=np.float32)
            n = len(me.vertices)
            co = np.empty(n * 3, dtype=np.float32)
            me.vertices.foreach_get("co", co)
            world = co.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3]
            offset = len(verts)
            verts.extend(map(tuple, world.tolist()))
            slot_map = []
            for slot in ob.material_slots:
                mat = slot.material
                if mat is None:
                    slot_map.append(None)
                    continue
                if mat.name not in mat_index:
                    mat_index[mat.name] = len(materials)
                    materials.append(mat)
                slot_map.append(mat_index[mat.name])
            layer = me.uv_layers.active
            if layer is not None and uv_name is None:
                uv_name = layer.name
            npoly, nloop = len(me.polygons), len(me.loops)
            starts = np.empty(npoly, dtype=np.int64)
            totals = np.empty(npoly, dtype=np.int64)
            mats = np.empty(npoly, dtype=np.int64)
            loop_verts = np.empty(nloop, dtype=np.int64)
            me.polygons.foreach_get("loop_start", starts)
            me.polygons.foreach_get("loop_total", totals)
            me.polygons.foreach_get("material_index", mats)
            me.loops.foreach_get("vertex_index", loop_verts)
            loop_verts = (loop_verts + offset).tolist()
            uv_list = None
            if layer is not None:
                uv = np.empty(nloop * 2, dtype=np.float32)
                layer.data.foreach_get("uv", uv)
                uv_list = list(map(tuple, uv.reshape(-1, 2).tolist()))
            smooth = corner = None
            if normals:
                smooth = _smooth_flags(me, npoly, np)
                corner = _corner_normals(me, nloop, mw, np) if smooth is not None and any(smooth) else None
            for i, (a, t, m) in enumerate(zip(starts.tolist(), totals.tolist(), mats.tolist())):
                faces.append(loop_verts[a:a + t])
                face_materials.append(slot_map[m] if m < len(slot_map) else None)
                uvs.append(uv_list[a:a + t] if uv_list is not None else None)
                if normals:
                    face_normals.append(corner[a:a + t] if corner is not None and smooth[i] else None)
        finally:
            ev.to_mesh_clear()
    names = [o.name for o in new]
    data = {o.data for o in new if o.data is not None}
    bpy.data.batch_remove(new)
    bpy.data.batch_remove([d for d in data if d.users == 0])
    face_part = None
    if parts:
        from wenart.blender import soft_seats as SS
        face_part = SS.face_parts(verts, faces)            # before the twins are split off their neighbours
    verts, faces, twins = separate_twins(verts, faces)
    geo = {"verts": verts, "faces": faces, "materials": materials, "face_materials": face_materials,
           "uvs": uvs, "uv_name": uv_name or "UVMap", "objects": names, "backface_twins": twins}
    if normals:
        geo["face_normals"] = face_normals
        geo["file_smooth"] = sum(1 for n in face_normals if n is not None)
    if face_part is not None:
        geo["face_parts"] = face_part
    return geo


def _smooth_flags(me, npoly: int, np):
    """The faces' smooth flags of an imported mesh (None when Blender cannot say)."""
    flags = np.zeros(npoly, dtype=bool)
    try:
        me.polygons.foreach_get("use_smooth", flags)
    except (AttributeError, TypeError, RuntimeError):
        return None
    return flags.tolist()


def _corner_normals(me, nloop: int, mw, np):
    """The imported mesh's corner (split) normals in world space (``n @ inverse(M)``: the normal matrix of the part's
    ``matrix_world``), None when Blender has no corner normals (before 4.1)."""
    corner = getattr(me, "corner_normals", None)
    if corner is None or len(corner) != nloop:
        return None
    nr = np.empty(nloop * 3, dtype=np.float64)
    corner.foreach_get("vector", nr)
    try:
        inv = np.linalg.inv(np.asarray(mw, dtype=np.float64)[:3, :3])
    except np.linalg.LinAlgError:
        return None
    nr = nr.reshape(-1, 3) @ inv
    ln = np.linalg.norm(nr, axis=1, keepdims=True)
    ln[ln < 1e-12] = 1.0
    return list(map(tuple, (nr / ln).tolist()))


def _cached_geometry(path: Path, collection, geo_cache: dict, normals: bool = False, parts: bool = False) -> dict:
    """``import_gltf_geometry`` once per file and build: pieces that share an
    asset share its materials and packed images instead of importing it
    again (the importer makes ``name.001`` material copies otherwise). 30 Oct 2026: ``normals`` and ``parts`` (the
    library furniture's own shading, a soft seat's loose parts) are asked by the caller; a file read without them is
    read again with them."""
    key = str(path.resolve())
    cached = geo_cache.get(key)
    if cached is None or (normals and "face_normals" not in cached) or (parts and "face_parts" not in cached):
        geo_cache[key] = import_gltf_geometry(path, collection, normals=normals or bool(cached and "face_normals" in
                                                                                         cached),
                                              parts=parts or bool(cached and "face_parts" in cached))
    return geo_cache[key]


def _material_is_textured(mat) -> bool:
    if mat is None or not mat.use_nodes or mat.node_tree is None:
        return False
    return any(n.bl_idname == "ShaderNodeTexImage" and n.image is not None for n in mat.node_tree.nodes)


def _unverified_copies(materials_list: list, cache: dict) -> list:
    """Copies of the asset materials with the red stripes mixed over the
    surface shader (the overlay of docs/milestone4.md §2); the materials as they are when the stripes are off
    (Milestone 11 decision D3, ``materials.set_markers``)."""
    from wenart.blender.materials import add_unverified_overlay, markers_on

    if not markers_on():
        return list(materials_list)
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
                 uvs=None, uv_name: str | None = None, fallback_material=None, normals=None):
    """Mesh object from world geometry with per-face materials; empty slots
    get ``fallback_material``; asset UVs (when given) become the active
    layer and ``box_m`` stays as a second layer. 30 Oct 2026 (UL131): ``normals`` (per face: None = flat, else its
    corners' normals, ``fit_normals``) shade the faces as the file did (smooth faces with the file's own normals)."""
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
    if normals is not None and any(n is not None for n in normals):
        apply_normals(ob.data, faces, normals)
    return ob


def corner_normal_list(faces, normals) -> tuple[list[bool], list[tuple]]:
    """``(smooth flag per face, one normal per corner in face order)`` for ``Mesh.normals_split_custom_set`` (pure):
    a flat face (or one past the end of ``normals``: bedding added to a frame) gets zero vectors, which Blender reads
    as "its own normal"."""
    flags, loops = [], []
    for i, f in enumerate(faces):
        n = normals[i] if i < len(normals) else None
        if n is not None and len(n) == len(f):
            flags.append(True)
            loops.extend(tuple(float(c) for c in v) for v in n)
        else:
            flags.append(False)
            loops.extend((0.0, 0.0, 0.0) for _ in f)
    return flags, loops


def apply_normals(mesh, faces, normals) -> dict:
    """The file's shading on a rebuilt mesh: the smooth flags, then the custom corner normals (Blender 4.1+: no auto
    smooth needed). Returns ``{"smooth", "custom_normals"}``."""
    flags, loops = corner_normal_list(faces, normals)
    try:
        mesh.polygons.foreach_set("use_smooth", flags)
    except (AttributeError, TypeError, RuntimeError):
        for poly, flag in zip(mesh.polygons, flags):
            poly.use_smooth = flag
    custom = False
    if hasattr(mesh, "normals_split_custom_set") and len(loops) == len(mesh.loops):
        try:
            mesh.normals_split_custom_set(loops)
            custom = True
        except (RuntimeError, TypeError, ValueError):
            custom = False
    mesh.update()
    return {"smooth": sum(flags), "custom_normals": custom}


class _Materials:
    """Style materials per parametric key, cached per (key, unverified)."""

    def __init__(self, library, style: dict, assumed: list):
        self.library = library
        self.keys, extra = style_material_keys(style)
        assumed.extend(extra)
        self._cache: dict = {}

    def get(self, key: str, unverified: bool = False, accent=None, colour=None, overrides: dict | None = None,
            lit: bool = False, params: dict | None = None):
        """The material of a parametric key; an ``accent_<key>`` part (Milestone 9 decor) takes ``accent`` (an RGB
        tint, the item's colour) on the ``<key>`` material, or the plain ``<key>`` material without one. Milestone
        10: a ``colour_<key>`` part takes ``colour`` (a ``colours.py`` name) as its base colour; ``overrides``
        (``design_overrides``, ``pot_override``) replace a key's slug, asset and colour for one piece; ``lit``
        makes the ``bulb`` key a light (``materials.light_material``). 29 Oct 2026 (UL121): ``params`` over a
        procedural look's own (a woven pattern's ink and angle, ``part_params``)."""
        if key.startswith(P.ACCENT_PREFIX):
            key = key[len(P.ACCENT_PREFIX):]
            colour = None
        elif key.startswith(P.COLOUR_PREFIX):
            key = key[len(P.COLOUR_PREFIX):]
            accent = None
        elif key.startswith(CLOTH_PREFIX):
            # 29 Oct 2026 (UL120): a garment, a folded stack or a pair of shoes of a see-through wardrobe: the
            # style's fabric in the colour its key names (``modules.garment_parts``: ``cloth:<colour>``); 30 Oct 2026
            # (UL135): ``cloth:<look>:<colour>`` is the bedding's woven fabric of that look (``textile_<look>``: the
            # wenart_weave cotton, wool, knit or linen) in that colour
            key, colour, accent = cloth_material_key(key, self.keys), cloth_colour(key), None
        else:
            accent, colour = None, None
        if key == "smoked_glass":                 # 29 Oct 2026 (UL120): a see-through wardrobe's smoked glass
            return self.library.smoked_glass()
        if key == "bulb" and lit:
            from wenart.blender import materials as M
            return M.light_material("lamp_light")
        if key == "screen":                       # 29 Oct 2026 (UL93): a screen with a faint lit wallpaper
            from wenart.blender import materials as M
            return M.screen_material()
        if key == "screen_ui":                    # 30 Oct 2026 (UL175): the light windows, bars and dock on it
            from wenart.blender import materials as M
            return M.screen_ui_material()
        if key == "led":                          # 29 Oct 2026 (UL114): an LED strip at a fixture shade's radiance
            from wenart.blender import materials as M
            return M.led_material()
        if key == "pampas":                       # ... and dried pampas plumes: the linen weave in cream
            colour = colour or "cream"
        over = (overrides or {}).get(key)
        if over:
            slug, asset, tint = over["slug"], over.get("asset"), None
            colour = colour or over.get("colour")
        else:
            slug, asset, tint = self.keys[key]
        pkey = tuple(sorted((str(k), str(v)) for k, v in (params or {}).items())) or None
        ck = (slug, asset, unverified, tuple(accent) if accent else None, colour or None, pkey)
        if ck in self._cache:
            return self._cache[ck]
        if asset and self.library.texture_set(asset)[0] is None:
            asset = None  # no usable texture: share the flat material of the same slug
        if accent:
            tint = tuple(float(v) for v in accent)
        if slug == "glass":
            mat = self.library.thin_glass()  # shower panels: the index pass must see the piece behind
        elif slug == SHEER_SLUG:
            mat = self.library.sheer(colour)  # UL106: a sheer curtain lets the daylight and the view through
        elif params:
            mat = self.library.get(slug, asset, tint, unverified=unverified, colour=colour, params=params)
        else:
            mat = self.library.get(slug, asset, tint, unverified=unverified, colour=colour)
        self._cache[ck] = mat
        return mat

    def slug(self, key: str, overrides: dict | None = None) -> str:
        for prefix in (P.ACCENT_PREFIX, P.COLOUR_PREFIX):
            if key.startswith(prefix):
                key = key[len(prefix):]
        if key.startswith(CLOTH_PREFIX):
            key = cloth_material_key(key, self.keys)
        if key.startswith(LIT_KEY):
            key = key[len(LIT_KEY):]
        over = (overrides or {}).get(key)
        return over["slug"] if over else self.keys[key][0]


def cloth_material_key(key: str, keys) -> str:
    """The material key of a ``cloth:`` part (pure; 30 Oct 2026, UL135): ``textile_<look>`` for
    ``cloth:<look>:<colour>`` when the style's keys have it (the bedding's woven fabrics), else ``fabric``."""
    from wenart.blender import wardrobe_contents as WC

    look, _colour = WC.parse_cloth_key(key)
    name = f"textile_{look}" if look else None
    return name if name and name in keys else "fabric"


def cloth_colour(key: str):
    """The colour name of a ``cloth:`` part key (``cloth:<look>:<colour>`` or ``cloth:<colour>``), None without one."""
    from wenart.blender import wardrobe_contents as WC

    return WC.parse_cloth_key(key)[1]


def piece_room(building: dict, level: dict, item: dict) -> dict:
    """The room a piece or decor item stands in (pure, Milestone 12): its ``room_id``, else the room of its level
    whose outline holds its centre (rooms in id order), else ``{}`` (the level's own floor)."""
    rooms = building.get("rooms") or []
    room = next((r for r in rooms if item.get("room_id") is not None and r.get("id") == item.get("room_id")), None)
    if room is not None:
        return room
    fp = item.get("footprint") or {}
    centre = list(fp.get("center") or item.get("center") or [])[:2]
    if len(centre) < 2:
        return {}
    for r in sorted((r for r in rooms if r.get("level_id") == level.get("id") and len(r.get("polygon") or []) >= 3),
                    key=lambda r: str(r.get("id"))):
        if G.point_in_polygon((float(centre[0]), float(centre[1])), [tuple(p[:2]) for p in r["polygon"]]):
            return r
    return {}


def piece_floor_z(building: dict, level: dict, piece: dict) -> float:
    """The floor a piece or decor item stands on (pure, Milestone 12): ``shell.room_floor_z`` of its room (track L:
    the level's elevation + the room's ``floor_offset_m``, sunken or raised; the level's floor without a room).
    ``scene_checks.floor_z_of`` (S1, S5) and ``proxies.create_proxies`` use it too."""
    from wenart.blender.shell import room_floor_z

    fz = piece.get("floor_z")
    if isinstance(fz, (int, float)) and not isinstance(fz, bool) and not piece.get("room_id"):
        return float(fz)          # 27 Oct 2026 (UL42): a piece on an outdoor space stands on its platform
    room = piece_room(building, level, piece)
    offset = room.get("floor_offset_m")
    if isinstance(offset, bool) or not isinstance(offset, (int, float, type(None))):
        room = dict(room, floor_offset_m=None)       # not a number: the level's floor
    return room_floor_z(room, level)


# Milestone 12: decor that does not stand on the room's floor. Lights hang from the level's ceiling (track L: the
# ceiling stays the level's when a room's floor is sunken or raised; ``center[2]`` is measured from the level's
# floor, decor_ai.ceiling_items); curtains and blinds follow their window, which the shell builds from the level's
# floor (``shell.opening_vertical``), but a floor-length curtain reaches the room's own floor.
CEILING_DECOR_TYPES = ("pendant_light", "ceiling_light")
WINDOW_DECOR_TYPES = ("curtain", "blind")
FLOOR_LENGTH_M = 0.05          # a curtain whose bottom is this close to the floor is floor-length
MIN_WINDOW_DECOR_H_M = 0.10


def decor_floor(building: dict, level: dict, item: dict) -> tuple[float, dict, str]:
    """``(floor_z, item, how)`` for a decor item the builder places without rays (pure, Milestone 12): the item's
    room floor (``piece_floor_z``: floor decor, wall art over its piece); a light hangs from the level's ceiling (the
    level's floor); a curtain or blind at a window keeps its place at the window (``center[2]`` re-measured from the
    room floor), a floor-length curtain is lengthened (sunken room) or shortened (raised room) to the room's floor.
    ``item`` is a copy when it changed."""
    level_z = float(level["elevation"])
    if item.get("type") in CEILING_DECOR_TYPES:
        return level_z, item, "the level's ceiling (lights)"
    floor_z = piece_floor_z(building, level, item)
    offset = floor_z - level_z
    if abs(offset) < 1e-9 or item.get("type") not in WINDOW_DECOR_TYPES or not item.get("window_id"):
        return floor_z, item, "the room's floor"
    center = list(item.get("center") or [])
    size = list(item.get("size") or [])
    z = float(center[2]) if len(center) > 2 and center[2] is not None else 0.0
    if len(center) < 2 or len(size) < 3 or size[2] is None:
        return floor_z, item, "the room's floor"
    h = float(size[2])
    if item["type"] == "curtain" and z <= FLOOR_LENGTH_M + 1e-9:          # to the floor: the room's floor
        new_z, new_h, how = z, h - offset, "the room's floor (floor-length curtain, top at its window)"
    else:                                                                 # at the window: the same world height
        new_z, new_h, how = z - offset, h, "its window (built from the level's floor)"
    if new_h < MIN_WINDOW_DECOR_H_M:
        new_h = MIN_WINDOW_DECOR_H_M
    out = dict(item, center=[center[0], center[1], round(new_z, 4)], size=size[:2] + [round(new_h, 4)] + size[3:])
    return floor_z, out, how


def refused_piece(piece: dict) -> str | None:
    """Why the builder refuses a piece (pure, Milestone 12 §4.1, §4.8): an untyped ``unknown`` piece (never a grey
    box), a library gap the fit left unbuilt (``asset.method == "none"``); None when it is built."""
    if piece.get("type") == "unknown":
        return "unknown type: not built (no grey box; docs/milestone12.md §4.1: typed, not furniture or for review)"
    asset = piece.get("asset") or {}
    if asset.get("method") == "none":
        gap = piece.get("library_gap") or asset.get("library_gap") or {}
        why = gap.get("reason") or asset.get("fallback_reason")
        return f"library gap: no audited {piece.get('type')} model ({why}); not built (docs/milestone12.md §4.8)"
    return None


def needs_dressing(piece: dict, entry: dict) -> bool:
    """A bed whose built model has no bedding gets the procedural duvet and pillows (pure, §4.7): a library bed that
    is not a Milestone 8 frame (those get the frame bedding) and whose audit does not say it is made up."""
    from wenart.furniture import catalog as C

    if piece.get("type") not in ("bed_single", "bed_double") or entry.get("method") != "library":
        return False
    asset = piece.get("asset") or {}
    return not entry.get("bedding") and not asset.get("bed_frame") and not C.has_own_bedding(asset)


def own_bedding_candidate(piece: dict, entry: dict) -> bool:
    """29 Oct 2026 (UL121, R35: "a library bed with its own flat or poor bedding is dressed too"): a library bed that
    is not a frame and whose audit says it is made up (``catalog.has_own_bedding``): its bedding is measured on its mesh
    (``_bedding_test``) before it is kept (pure)."""
    from wenart.furniture import catalog as C

    if piece.get("type") not in ("bed_single", "bed_double") or entry.get("method") != "library":
        return False
    asset = piece.get("asset") or {}
    return not entry.get("bedding") and not asset.get("bed_frame") and C.has_own_bedding(asset)


def _bedding_test(piece: dict, entry: dict, ob) -> str | None:
    """The measured test of a made-up library bed's own bedding (``bedding_parts.bedding_relief`` on its evaluated
    mesh's vertices, numpy, no ray; ``dress_mode``): ``full`` / ``pillows`` when it is flat or poorer than ours, None
    when it is kept; recorded on the entry (``bedding_test``)."""
    from wenart.blender import bedding_parts as BP

    pts = _evaluated_world_points(ob)
    centre, rot, size = BP.bed_frame(piece)
    relief = BP.bedding_relief(pts, centre, rot, size) if len(pts) else {}
    mode, why = BP.dress_mode(piece.get("asset"), relief, width=size[0])     # 30 Oct 2026 (UL137): flat pillows
    entry["bedding_test"] = dict(relief, own_bedding=True, mode=mode, poorer=mode is not None, reason=why,
                                 rule=BP.RULE)
    return mode


def hosted_support(item: dict, host: dict | None) -> str | None:
    """The support a hosted decor item rests on (its ``host_frame``, else the type rule), or None for an item the
    builder places without rays (no host, or a support of the floor, a wall or the ceiling)."""
    from wenart.blender import rest as R             # not wenart.furniture.decor: Blender's Python has no shapely

    if host is None:
        return None
    support = R.item_support(item, host)
    return support if support in R.RAY_SUPPORTS else None


SLOWEST_N = 15                   # 29 Oct 2026: the slowest pieces and decor items a build records


def note_time(summary: dict, what: dict, kind: str, seconds: float) -> None:
    """Keep ``what`` among the build's ``SLOWEST_N`` slowest items (``summary["slowest"]``; 29 Oct 2026: real06 run
    100801's furniture took 1,023 s a build against 155 s the day before, and nothing said which item; user: "make the
    pod use the GPU fully")."""
    rows = summary.setdefault("slowest", [])
    rows.append({"id": what.get("id"), "type": what.get("type"), "kind": kind,
                 "host": what.get("host_id"), "seconds": round(float(seconds), 2)})
    rows.sort(key=lambda r: -r["seconds"])
    del rows[SLOWEST_N:]


def create_furniture(building: dict, level: dict, collection, library, style: dict, assets_dir: str | None,
                     pass_indices: dict, manifest_objects: list, assumed: list, warnings: list,
                     use_proxies: bool = False) -> dict:
    """Create the furniture and decor objects of ``level``; returns a
    summary for the manifest (``pieces``, ``by_method``, ``fallbacks``,
    ``proxies``, ``decor``).

    Milestone 12 (track S): untyped pieces and library gaps are refused (``refused_piece``: listed in
    ``not_built``, no grey box; ``--proxies`` still builds the Milestone 3 boxes for debugging); a piece stands on its
    room's floor (``piece_floor_z``); a bed model without bedding is dressed (``needs_dressing``); hosted decor rests
    on the built host mesh (``rest.plan_decor`` / ``plan_throw``: placed, checked S5, placed once more, else not
    built: ``decor_not_rested``); ``summary["objects"]`` = ``{piece or decor id: object}`` (bedding:
    ``<id>#dressing``) for the scene checks (``build.py``); every piece and decor item stands on its room's floor
    (``shell.room_floor_z``: ``piece_floor_z``, ``decor_floor``), the ``--proxies`` boxes too."""
    mats = _Materials(library, style, assumed)
    mats.lamps_on = lamps_on(style)                   # Milestone 10: the interior evening mood lights the lamps
    mats.family = str((style or {}).get("family") or "").lower()     # 29 Oct 2026 (UL121): the bedding's family
    mats.collection = collection
    on_level = [p for p in building.get("furniture", []) if p["level_id"] == level["id"]]
    pieces = [p for p in on_level if is_built(p)]
    not_built = [{"id": p["id"], "type": p["type"], "reason": not_built_reason(p)} for p in on_level if not is_built(p)]
    built_in: dict[str, str] = {}
    if not use_proxies:
        refused = [(p, refused_piece(p)) for p in pieces]
        not_built += [{"id": p["id"], "type": p["type"], "reason": why} for p, why in refused if why]
        pieces = [p for p, why in refused if not why]
        # fix round after P3: a drawn sink built into its kitchen run is that run's sink unit, no object of its own
        built_in = built_in_ids(pieces)
        pieces = [p for p in pieces if p["id"] not in built_in]
        # 28 Oct 2026 (user on real06: "Why is this closing the window"): a wall cabinet never covers a window or a
        # glazed door of the building as built (the architect may add or move one after the completion hung it)
        cleared = []
        for p in pieces:
            q, rec = MOD.clear_windows(p, building)
            if rec is not None:
                assumed.append({"object": f"furn_{p['id']}", "field": "wall_cabinet_cut", "value": rec["windows"],
                                "reason": rec["reason"]})
                warnings.append(f"{p['id']}: {rec['reason']}")
            if q is None:
                not_built.append({"id": p["id"], "type": p["type"], "reason": rec["reason"]})
                continue
            cleared.append(q)
        pieces = cleared
    proxy_pieces = [p for p in pieces if use_proxies or p["type"] not in P.PARAMETRIC_TYPES]
    for p in proxy_pieces:
        if p["type"] != "unknown" and not use_proxies:
            warnings.append(f"{p['id']}: furniture type {p['type']!r} has no parametric builder; proxy box used")
    summary = {"pieces": len(pieces), "by_method": {}, "fallbacks": [], "proxies": len(proxy_pieces), "decor": 0,
               "proxies_forced": bool(use_proxies), "not_built": not_built, "decor_skipped": [],
               "decor_not_rested": [], "dressed_beds": [], "objects": {},
               "built_in": [{"id": p["id"], "type": p["type"], "host": built_in[p["id"]], "reason": BUILT_IN_REASON}
                            for p in on_level if p["id"] in built_in]}
    if proxy_pieces:
        proxies.create_proxies({"furniture": proxy_pieces}, level, collection, {
            "proxy": library.proxy("proxy"), "proxy_glass": library.proxy("proxy_glass"),
            "proxy_unverified": library.proxy("proxy_unverified")}, pass_indices, manifest_objects, assumed,
            others=pieces, floor_of=lambda p: piece_floor_z(building, level, p))
        for p in proxy_pieces:
            summary["by_method"]["proxy"] = summary["by_method"].get("proxy", 0) + 1

    import bpy

    entries: dict[str, dict] = {}
    placed: list[tuple[dict, float]] = []
    unverified_cache: dict = {}
    geo_cache: dict = {}  # file -> imported geometry: one import per asset file, materials shared
    casters: dict = {}    # host id -> its ray caster (the built, evaluated mesh, with its dressing)
    proxy_ids = {p["id"] for p in proxy_pieces}
    flat_ids = {p["id"] for p in proxy_pieces if proxies.flat_reason(p, pieces)}
    for piece in pieces:
        t_piece = time.perf_counter()
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
        entry = _create_piece(piece, level, piece_floor_z(building, level, piece), height, height_assumed, lift,
                              collection, library, mats, assets_dir, pass_indices, assumed, warnings,
                              unverified_cache, geo_cache, style=style, building=building)
        manifest_objects.append(entry)
        entries[piece["id"]] = entry
        method = entry["method"] if entry["method"] in ("library", MOD.MODULE_METHOD) else "parametric"
        summary["by_method"][method] = summary["by_method"].get(method, 0) + 1
        if entry["fallback_reason"]:
            summary["fallbacks"].append({"id": piece["id"], "type": piece["type"], "reason": entry["fallback_reason"]})
        ob = bpy.data.objects.get(entry["name"])
        summary["objects"][piece["id"]] = ob
        mode = "full" if ob is not None and needs_dressing(piece, entry) else None
        if ob is not None and mode is None and own_bedding_candidate(piece, entry):
            # 29 Oct 2026 (UL121): a library bed with its own bedding is dressed when its bedding measures poorer
            mode = _bedding_test(piece, entry, ob)
        if mode is not None:
            t_bed = time.perf_counter()
            dress = _dress_bed(piece, entry, ob, piece_floor_z(building, level, piece), collection, mats, assumed,
                               warnings, casters, building=building, style=style, mode=mode)
            if dress is not None:
                summary["objects"][f"{piece['id']}#dressing"] = dress     # S5 rests on it; S2 skips it
                summary["dressed_beds"].append(piece["id"])
                rec = (entry.get("dressing") or {}).get("record") or {}
                if (rec.get("set") or {}).get("accent") or (rec.get("set") or {}).get("lumbar"):
                    summary.setdefault("bedding_sets", []).append(piece["id"])
                summary.setdefault("bedding", []).append(
                    {"id": piece["id"], "mode": mode, "set": rec.get("set"), "explained": rec.get("explained"),
                     "seconds": round(time.perf_counter() - t_bed, 3)})
        note_time(summary, piece, "piece", time.perf_counter() - t_piece)

    for record in summary["built_in"]:              # the run's manifest entry names what it holds (fix round after P3)
        host_entry = entries.get(record["host"])
        if host_entry is not None:
            host_entry.setdefault("built_ins", []).append({"id": record["id"], "type": record["type"]})

    for host_id in unknown_decor_hosts(building):
        if host_id not in {p["id"] for p in building.get("furniture", [])}:
            msg = f"decor host {host_id!r} is not a furniture piece; item skipped"
            if msg not in warnings:
                warnings.append(msg)
    manifest_by_id = {o["wenart_id"]: o for o in manifest_objects if o.get("kind") in ("furniture", "furniture_proxy")}
    worktop_taken: list[dict] = []                    # 28 Oct 2026: the worktop items built so far (a slide avoids them)
    timed = [None, 0.0]                              # the item before and when it started (``note_time``)
    for n, (item, host) in enumerate(collect_decor(building, level["id"]), start=1):
        if timed[0] is not None:
            note_time(summary, timed[0], "decor", time.perf_counter() - timed[1])
        timed[:] = [dict(item, host_id=(host or {}).get("id")), time.perf_counter()]
        host_entry = None
        if host is not None:
            host_entry = entries.get(host["id"]) or manifest_by_id.get(f"proxy:{host['id']}")
            if host_entry is None:
                summary["decor_skipped"].append({"id": item.get("id"), "type": item.get("type"),
                                                 "room_id": item.get("room_id"),
                                                 "reason": f"its host {host['id']} is not built"})
                continue
        if item.get("type") == "cushion" and host is not None and host["id"] in (summary.get("bedding_sets") or ()):
            # 29 Oct 2026 (UL121): the bed's dressing carries its family's accent cushions and lumbar (their colours
            # are this item's): a decor cushion would stand in front of them as a second set
            summary["decor_skipped"].append({"id": item.get("id"), "type": "cushion", "room_id": item.get("room_id"),
                                             "reason": f"built in the dressing of {host['id']}: its family's cushion "
                                                       "set (UL121), in this cushion's colour"})
            continue
        if item.get("type") == "cushion" and host is not None:
            from wenart.blender import rest as R
            if R.own_cushions(host) and host["id"] not in summary["dressed_beds"]:
                # 25 Oct 2026: the final model (after the refit) has its own cushions or pillows; a decor cushion
                # would lie on top of them and read as floating
                summary["decor_skipped"].append({"id": item.get("id"), "type": "cushion",
                                                 "room_id": item.get("room_id"),
                                                 "reason": f"the model of {host['id']} has its own cushions/pillows"})
                continue
        if item.get("type") == "throw" and host is not None and item.get("when_dressed") \
                and host["id"] not in summary["dressed_beds"]:
            # 29 Oct 2026 (UL121): the decor stage's throw for a made-up bed model, built only over our dressing
            summary["decor_skipped"].append({"id": item.get("id"), "type": "throw", "room_id": item.get("room_id"),
                                             "reason": f"the model of {host['id']} keeps its own made bedding (not "
                                                       "dressed by us): no throw over its folds"})
            continue
        if item.get("type") == "throw" and host is not None:
            from wenart.blender import rest as R
            if R.own_bedding(host) and host["id"] not in summary["dressed_beds"]:
                # 28 Oct 2026 (user on real04's f_L0_021: "I did not like this bed"): the final model is made up with
                # its own duvet; a throw over its modelled folds clips through them
                summary["decor_skipped"].append({"id": item.get("id"), "type": "throw", "room_id": item.get("room_id"),
                                                 "reason": f"the model of {host['id']} has its own made bedding: a "
                                                           "throw over its folds clips through them"})
                continue
        # 30 Oct 2026 (lesson UL151, user: "this vase on the floor not making sense"): table-size decor never stands on
        # the floor, and a floor piece's model reads as one (else ours at the type's height)
        item, floor_why = floor_class_item(item, host)
        if floor_why is not None:
            summary["decor_skipped"].append({"id": item.get("id"), "type": item.get("type"),
                                             "room_id": item.get("room_id"), "reason": floor_why})
            continue
        if item.get("floor_class_note"):
            assumed.append({"object": str(item.get("id")), "field": "floor_class", "value": "parametric",
                            "reason": item["floor_class_note"]})
        # Milestone 12: the room's floor (shell.room_floor_z); lights from the level's ceiling, curtains and blinds at
        # their window (decor_floor)
        item_floor, item, _floor_how = decor_floor(building, level, item)
        if item.get("type") in P.KITCHEN_DECOR_TYPES and host is not None:
            # 29 Oct 2026 (wenart.blender.kitchen_details.item_blocked): never in the run's tall unit or under its rail
            # (the refit may have planned them after the decor stage placed the item)
            planned = KD.item_blocked(item, host)
            if planned is not None:
                summary["decor_skipped"].append({"id": item.get("id"), "type": item.get("type"),
                                                 "room_id": item.get("room_id"), "reason": planned})
                continue
            # 28 Oct 2026: a worktop item never stands in front of a window, glazed door or pass-through of the
            # building as built that it would reach (the architect may add or move one after the decor stage)
            blocked = MOD.worktop_item_window(item, host, building)
            if blocked is not None and item.get("type") == "cookware":
                blocked = None                            # the pot and pan stand on the hob, where it is
            if blocked is not None:
                slid = MOD.slide_worktop_item(item, host, building, worktop_taken)
                if slid is None:
                    summary["decor_skipped"].append({"id": item.get("id"), "type": item.get("type"),
                                                     "room_id": item.get("room_id"),
                                                     "reason": f"it would stand in front of {blocked} of the "
                                                               "building as built and reach over its sill; no free "
                                                               "spot on the worktop"})
                    continue
                assumed.append({"object": str(item.get("id")), "field": "worktop_slide", "value": slid["center"],
                                "reason": f"slid along {host['id']}: in front of {blocked} of the building as built"})
                item = slid
            worktop_taken.append(item)
        if item.get("type") in WALL_DECOR_TYPES:
            built = dict({k[len("proxy:"):]: v for k, v in manifest_by_id.items() if k.startswith("proxy:")},
                         **entries)                      # the built boxes: pieces, and proxies behind --proxies
            entry = _create_wall_art(item, n, level, item_floor, collection, library, assets_dir, pass_indices,
                                     built, on_level, warnings, geo_cache, summary["decor_skipped"], mats=mats)
        elif (item.get("type") in P.KITCHEN_DECOR_TYPES and host is not None and host_entry.get("kind") == "furniture"
              and KD.worktop_z(item, host) is not None):
            # 29 Oct 2026 (lesson UL111: "make slow code efficient"): a worktop item on a kitchen run built from modules
            # rests on the plan's known worktop line (or the hob's rings): no ray per item; the scene check S5 still
            # measures it on the built mesh
            z = KD.worktop_z(item, host)
            known = dict(item, center=[float(item["center"][0]), float(item["center"][1]), z])
            entry = _create_decor(known, host, n, level, piece_floor_z(building, level, host), collection, library,
                                  mats, assets_dir, pass_indices, host_entry, warnings, geo_cache,
                                  skipped=summary["decor_skipped"], assumed=assumed)
            if entry is not None:
                entry["assumed"] = {"rest": f"on the worktop line of {host['id']} ({z:.3f} m over its floor: its "
                                            "module plan)"}
        elif hosted_support(item, host) is not None and host_entry.get("kind") == "furniture":
            entry = _create_hosted_decor(item, host, n, level, piece_floor_z(building, level, host), collection,
                                         library, mats, assets_dir, pass_indices, host_entry, warnings, geo_cache,
                                         casters, summary, assumed)
        else:
            entry = _create_decor(item, host, n, level, item_floor, collection, library, mats, assets_dir,
                                  pass_indices, host_entry, warnings, geo_cache, skipped=summary["decor_skipped"],
                                  assumed=assumed)
        if entry is None:
            continue
        manifest_objects.append(entry)
        if item.get("id"):
            # 28 Oct 2026: a hung light's cord and canopy are part of it (S5 measures its top at the ceiling)
            obs = [bpy.data.objects.get(n) for n in [entry["name"], (entry.get("suspension") or {}).get("name")] if n]
            summary["objects"][str(item["id"])] = obs if len(obs) > 1 else obs[0]
        if host_entry is not None:
            host_entry.setdefault("decor", []).append({"name": entry["name"], "type": entry["type"],
                                                       "method": entry["method"]})
        summary["decor"] += 1
    if timed[0] is not None:
        note_time(summary, timed[0], "decor", time.perf_counter() - timed[1])
    return summary


def _evaluated_world_mesh(ob) -> tuple[list, list]:
    """World vertices and faces of an object's evaluated mesh (its Bevel modifier applied)."""
    import bpy

    depsgraph = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(depsgraph)
    me = ev.to_mesh()
    try:
        mw = ob.matrix_world
        verts = [tuple(mw @ v.co) for v in me.vertices]
        faces = [list(p.vertices) for p in me.polygons]
    finally:
        ev.to_mesh_clear()
    return verts, faces


def _evaluated_world_points(ob):
    """The world vertices of an object's evaluated mesh as an ``(N, 3)`` numpy array (29 Oct 2026, UL111: one
    ``foreach_get`` and a matrix product, no Python loop per vertex; ``_bedding_test`` measures a model's bedding),
    with points on its big faces (``bedding_parts.surface_samples``)."""
    import bpy
    import numpy as np

    from wenart.blender import bedding_parts as BP

    depsgraph = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(depsgraph)
    me = ev.to_mesh()
    try:
        co = np.empty(len(me.vertices) * 3, dtype=np.float64)
        me.vertices.foreach_get("co", co)
        m = np.array(ob.matrix_world, dtype=np.float64)
        pts = co.reshape(-1, 3) @ m[:3, :3].T + m[:3, 3]
        # 30 Oct 2026: points on the big faces too (a mattress of a few faces has no vertex over its middle)
        me.calc_loop_triangles()
        tris = np.empty(len(me.loop_triangles) * 3, dtype=np.int64)
        me.loop_triangles.foreach_get("vertices", tris)
        extra = BP.surface_samples(pts, tris.reshape(-1, 3))
    finally:
        ev.to_mesh_clear()
    return np.concatenate([pts, extra]) if len(extra) else pts


def _host_caster(host_entry: dict, casters: dict):
    """The ray caster of a built host (its evaluated mesh and the bedding the build dressed it with), cached."""
    import bpy

    from wenart.blender import rest as R

    key = host_entry.get("wenart_id") or host_entry.get("name")
    if key in casters:
        return casters[key]
    found = []
    for name in [host_entry.get("name")] + [(host_entry.get("dressing") or {}).get("name")]:
        ob = bpy.data.objects.get(name or "")
        if ob is not None and ob.type == "MESH":
            verts, faces = _evaluated_world_mesh(ob)
            if verts and faces:
                found.append(R.BVHCaster(verts, faces))
    casters[key] = None if not found else (found[0] if len(found) == 1 else R.MultiCaster(found))
    return casters[key]


def dressing_mesh(parts: list) -> tuple[list, list, list]:
    """World parts (already placed) -> one mesh: ``(verts, faces, face_keys)`` (pure). 29 Oct 2026 (UL121): a part
    with a ``colour`` (the family set's fabrics) gives its faces the key ``<key>|<colour>`` (``split_key``)."""
    verts, faces, keys = [], [], []
    for part in parts:
        off = len(verts)
        verts.extend(part["verts"])
        key = f"{part['key']}|{part['colour']}" if part.get("colour") else part["key"]
        faces.extend([[i + off for i in f] for f in part["faces"]])
        keys.extend([key] * len(part["faces"]))
    return verts, faces, keys


def split_key(key: str) -> tuple[str, str | None]:
    """``(key, colour)`` of a dressing face key (``dressing_mesh``)."""
    k, _sep, colour = key.partition("|")
    return k, (colour or None)


LEAN_CASTER = "{}#lean"           # casters key: a dressed bed and its pillows, what a decor cushion leans against
BED_CASTER = "{}#bed"             # 28 Oct 2026: a dressed bed's model alone (its headboard, the pillows not in it)


def bed_bedding_spec(piece: dict, style: dict | None) -> tuple[dict, str]:
    """``(spec, reason)`` of a bed's bedding set (pure; 29 Oct 2026, UL121): the decor stage's (``bedding_layers.set``,
    ``wenart.furniture.bedding``), else its style family's (``bedding_parts.family_spec``: a decor output from before
    the rule)."""
    from wenart.blender import bedding_parts as BP

    layers = piece.get("bedding_layers") if isinstance(piece.get("bedding_layers"), dict) else {}
    if isinstance(layers.get("set"), dict) and layers["set"].get("duvet"):
        return layers["set"], str(layers.get("set_why") or "the decor stage's bedding set")
    fam = layers.get("family") or (style or {}).get("family")
    spec, why = BP.family_spec(fam)
    return spec, f"the {spec['family']} family's set at build time: {why}"


def _dress_bed(piece, entry, ob, floor_z, collection, mats, assumed, warnings, casters=None, building=None,
               style=None, mode="full"):
    """The procedural duvet and pillows of a bed model without bedding (§4.7: fixes the bare mattresses): draped on
    the evaluated bed mesh (``textiles.duvet_and_pillows``), one object ``dress_<id>`` with the bed's ``wenart_id``
    and pass index (a design detail of the piece), recorded on the entry (``dressing``) and in ``assumed``. 27 Oct
    2026: ``casters[LEAN_CASTER]`` gets the bed with its pillows only (``textiles.lean_parts``): the decor cushions
    lean against the pillows, never the duvet's fold. 28 Oct 2026: ``casters[BED_CASTER]`` the bed model alone, so a
    decor cushion first stands on the pillows against the headboard (``rest.plan_decor`` takes both, in order).

    29 Oct 2026 (lesson UL121, R35): with the ``building`` the bed is dressed in its family's full set
    (``textiles.bedding_set``: euro shams, standing pillows, the accent cushions and the lumbar in the AI's cushion
    colours, the soft deep duvet hanging almost to the floor on each side ``bedding_parts.bed_sides`` finds free, the
    rolled turn-down), still one mesh: each fabric is a material slot (``split_key``); ``mode`` pillows (a made-up model
    whose duvet has folds but no pillows) leaves the duvet out. 30 Oct 2026 (UL136, UL137, UL146): a real made bed
    (``textiles.bedding_set``: the smooth duvet with a level hem, the thin turned-down band, the flanged pillows standing
    against the headboard, a gap at the head closed); the record carries the duvet's measured look and the head."""
    from wenart.blender import bedding_parts as BP
    from wenart.blender import rest as R
    from wenart.blender import textiles as T

    verts, faces = _evaluated_world_mesh(ob)
    fp = piece["footprint"]
    host_fp = {"center": [float(fp["center"][0]), float(fp["center"][1])], "size": [float(v) for v in fp["size"][:2]],
               "rotation_deg": float(fp["rotation_deg"])}
    # 29 Oct 2026 (UL106): the euro shams the decor stage asks for (``bedding_layers``, wenart.furniture.dressing)
    layers = piece.get("bedding_layers") if isinstance(piece.get("bedding_layers"), dict) else {}
    if building is not None:
        spec, spec_why = bed_bedding_spec(piece, style)
        _c, _r, (bw, bd) = BP.bed_frame(piece)
        sides = BP.bed_sides(piece, building, (-bd / 2.0, -bd / 2.0 + BP.DUVET_SHARE * bd))
        colours = [d.get("colour") for d in building.get("decor") or []
                   if d.get("type") == "cushion" and d.get("host_id") == piece["id"]]
        plan = T.bedding_set(R.BVHCaster(verts, faces), host_fp, floor_z, spec, sides, mode=mode, colours=colours)
        if plan is not None:
            plan["record"]["spec_why"] = spec_why
            if entry.get("bedding_test"):
                plan["record"]["bedding_test"] = entry["bedding_test"].get("reason")
    else:
        plan = T.duvet_and_pillows(R.BVHCaster(verts, faces), host_fp, floor_z,
                                   shams=int(layers.get("euro_shams") or 0))
    if plan is None:
        warnings.append(f"{piece['id']}: no mattress top found on the bed model; no bedding added")
        return None
    if casters is not None:
        pv, pf = T.lean_parts(plan["parts"])
        sv, sf = T.sham_mesh(plan["parts"])
        bed = R.BVHCaster(verts, faces)
        # a decor cushion stands against the euro shams where they are (the headboard behind them is covered)
        casters[BED_CASTER.format(piece["id"])] = R.MultiCaster([bed, R.BVHCaster(sv, sf)]) if sf else bed
        casters[LEAN_CASTER.format(piece["id"])] = R.MultiCaster([bed] + ([R.BVHCaster(pv, pf)] if pf else []))
    dverts, dfaces, keys = dressing_mesh(plan["parts"])
    used = sorted(set(keys), key=keys.index)
    unverified = entry.get("status") == "unverified"
    slots = [mats.get(split_key(k)[0], unverified, colour=split_key(k)[1]) for k in used]
    name = f"dress_{piece['id']}"
    index = {k: i for i, k in enumerate(used)}
    dob = _mesh_object(name, dverts, dfaces, slots, [index[k] for k in keys], collection, piece["id"],
                       "furniture", entry.get("status") or "verified")
    for poly in dob.data.polygons:
        poly.use_smooth = True
    dob.pass_index = entry["pass_index"]
    dob["wenart_type"] = piece["type"]
    dob["wenart_dressing"] = "bedding"
    entry["dressing"] = {"name": name, "record": plan["record"],
                         "material_keys": {k: mats.slug(split_key(k)[0]) for k in used},
                         "vertices": len(dverts), "faces": len(dfaces)}
    rec = plan["record"]
    if rec.get("set"):
        s = rec["set"]
        free = ", ".join(k for k, v in (rec.get("sides") or {}).items() if v.get("free")) or "no"
        detail = (f"the {rec.get('family')} bedding set (UL121): {s['euro_shams']} euro sham(s), {s['pillows']} "
                  f"{'standing' if rec.get('pillows_upright') else 'lying'} pillow(s), {s['accent']} accent "
                  f"cushion(s), {s['lumbar']} lumbar"
                  + (f", a soft duvet over the foot {T.DUVET_SHARE:.0%} hanging on the {free} side(s)"
                     if rec.get("duvet") else ", the model's own duvet kept"))
        why = (rec.get("bedding_test") or "the bed model has no bedding (docs/milestone12.md §4.7)") \
            + f"; {rec.get('spec_why')}"
    else:
        detail = (f"procedural bedding: a draped duvet over the foot {T.DUVET_SHARE:.0%} and {rec['pillows']} "
                  "pillow(s) against the headboard"
                  + (f" in front of {rec['euro_shams']} euro sham(s)" if rec.get("euro_shams") else ""))
        why = "the bed model has no bedding (docs/milestone12.md §4.7): our cloth on its mattress"
    entry["assumed"]["bedding"] = detail
    assumed.append({"object": name, "field": "bedding", "value": detail, "parent": piece["id"], "kind": "bedding",
                    "reason": why})
    return dob


STANDING_CUSHION_T = 0.15        # an old two-value cushion against a back stands: its width square, 15 cm thick
RUNNER_KEY = "colour_duvet"      # = textiles.RUNNER_KEY: a layered throw's second blanket (29 Oct 2026, UL106)


def part_colour(item: dict, key: str):
    """The colour phrase of a decor part (pure): a layered throw's second blanket (``RUNNER_KEY``; 29 Oct 2026, UL121:
    any ``colour_runner_<look>`` key) takes the item's ``accent_colour`` when it has one, every other part the item's
    ``colour``."""
    from wenart.blender import bedding_parts as BP

    if (key == RUNNER_KEY or key.startswith(BP.COLOUR_PREFIX + BP.RUNNER_PREFIX)) and item.get("accent_colour"):
        return item["accent_colour"]
    return item.get("colour")


PATTERN_INK = "charcoal"         # a woven pattern's ink where the throw names no accent colour


def part_params(item: dict, key: str, host: dict | None = None) -> dict | None:
    """The procedural parameters of a decor part's material (pure; 29 Oct 2026, UL121): a throw's woven pattern
    (``colour_textile_<pattern>``) takes the item's accent colour as its ink (its second blanket's colour: the pair
    goes together) and its host's rotation as its angle (the pattern runs with the bed, not with the world); None for
    every other part."""
    from wenart.blender import bedding_parts as BP

    k = key[len(BP.COLOUR_PREFIX):] if key.startswith(BP.COLOUR_PREFIX) else key
    if not k.startswith(BP.TEXTILE_PREFIX) or k[len(BP.TEXTILE_PREFIX):] not in BP.PATTERN_SLUGS:
        return None
    rot = float(((host or {}).get("footprint") or {}).get("rotation_deg") or item.get("rotation_deg") or 0.0)
    return {"ink": item.get("accent_colour") or PATTERN_INK, "angle_deg": round(rot % 180.0, 3)}


def local_decor_mesh(item: dict, dtype: str, support: str | None = None) -> dict:
    """The parametric or textile mesh of a decor item in its own frame (pure): ``{"verts", "faces", "keys",
    "parts"}`` (bottom on z = 0, centred, front -Y); cushions and rugs take the item's colour on their fabric. A
    cushion against a back or a headboard stands (Milestone 12: an item written with two values, before the real
    sizes of ``decor.CUSHION_SIZE``, becomes a square cushion ``STANDING_CUSHION_T`` thick)."""
    size = list(item.get("size") or [0.4, 0.4])
    if dtype == "cushion" and support in ("back", "headboard") and len(size) < 3:
        size = [float(size[0]), STANDING_CUSHION_T, float(size[0])]
    w, d, h = P.decor_size(dtype, size)
    parts = P.decor_parts(dtype, w, d, h, item)
    if dtype in BRIEF_COLOURED_DECOR:
        parts = [dict(part, key=P.COLOUR_PREFIX + part["key"]) if part["key"] == "fabric" else part for part in parts]
    verts, faces, keys = P.world_mesh(parts, (0.0, 0.0), 0.0, 0.0)
    return {"verts": verts, "faces": faces, "keys": keys, "parts": parts}


def _create_hosted_decor(item, host, n, level, floor_z, collection, library, mats, assets_dir, pass_indices,
                         host_entry, warnings, geo_cache, casters, summary, assumed) -> dict | None:
    """A decor item resting on its built host (Milestone 12, §4.7): its mesh in its own frame (a library model fitted
    to its box, else the parametric or textile one), placed by rays on the host's evaluated mesh
    (``rest.plan_decor``; a throw is draped, ``rest.plan_throw``), checked (S5) and placed once more; when it still
    does not rest it is not built and ``summary["decor_not_rested"]`` holds the measured numbers."""
    from wenart.blender import rest as R

    dtype = item.get("type")
    if dtype not in P.DECOR_TYPES:
        warnings.append(f"decor on {host['id']}: unknown decor type {dtype!r}; skipped")
        return None
    caster = _host_caster(host_entry, casters)
    if caster is None:
        summary["decor_skipped"].append({"id": item.get("id"), "type": dtype, "room_id": item.get("room_id"),
                                         "reason": f"the built host {host['id']} has no mesh to rest on"})
        return None
    frame = item.get("host_frame") if isinstance(item.get("host_frame"), dict) else {}
    support = hosted_support(item, host)
    back = None
    if support == "headboard":
        # 27 Oct 2026: against the pillows, not the duvet. 28 Oct 2026 (user on real04: "More flying pillows"): the
        # back rays only see the bed (its headboard: the cushion stands on the pillows) then the bed and its pillows
        # (it leans on them); its seat and S5 see everything built, the duvet too (its cushions were placed without the
        # duvet: S5 on the built bedding found them 4.9 cm in it). 29 Oct 2026: a bed that is one mesh with its pillows
        # (parametric, a frame with our bedding) has neither: on its host caster the cushion first stands on the
        # pillows against the headboard too (``rest.stand_modes``, the back rays through its upper part), then leans
        back = [c for c in (casters.get(BED_CASTER.format(host["id"])), casters.get(LEAN_CASTER.format(host["id"])))
                if c is not None] or None
    file, reason = resolve_asset(item.get("asset"), assets_dir)
    local, geo = None, None
    if file is not None and dtype != "throw":
        try:
            geo = _cached_geometry(file, collection, geo_cache)
            if not geo["faces"]:
                raise ValueError("file has no mesh faces")
            w, d, h = P.decor_size(dtype, item.get("size") or [0.4, 0.4])
            target = [w, d, h] if len(item.get("size") or []) > 2 else [w, d]
            if item["asset"].get("target") == "within" and len(item["asset"].get("bbox_m") or []) > 2:
                target = [float(v) for v in item["asset"]["bbox_m"][:3]]   # the model's own (real) proportions
            lv, info = fit_vertices(geo["verts"], item["asset"], {"center": [0.0, 0.0], "rotation_deg": 0.0}, 0.0,
                                    target_size=target)
            local = {"verts": lv, "faces": geo["faces"], "info": info}
        except Exception as exc:  # noqa: BLE001 - a broken file: the parametric item, loudly
            reason = f"import of {file} failed: {type(exc).__name__}: {exc}"
            warnings.append(f"decor {dtype} on {host['id']}: {reason}; parametric mesh used")
            local, geo = None, None
    parametric = local is None
    if parametric and dtype != "throw":
        local = local_decor_mesh(item, dtype, support)
    if dtype == "throw":
        if not isinstance(item.get("weave"), dict) and host.get("type") in ("bed_single", "bed_double") \
                and getattr(mats, "family", None) is not None:
            from wenart.blender import bedding_parts as BP     # 29 Oct 2026 (UL121): a decor output from before the
            item = dict(item, weave=BP.throw_weave(mats.family))   # rule: the family's woven pair at build time
        plan = R.plan_throw(item, host, caster, floor_z)
        keys = [p["key"] for p in plan.get("parts") or [] for _f in p["faces"]]
    else:
        iw, idp, _ih = R.local_bounds(local["verts"])
        fp = host["footprint"]
        rot_i = float(item.get("rotation_deg") if item.get("rotation_deg") is not None else fp["rotation_deg"])
        # 30 Oct 2026 (UL128): under a sloped ceiling the item's top stays under it, at its spot and towards the host's
        # centre (where a top item may move); a shelf item takes a board low enough
        max_top = slope_top_z(level, [(item.get("center") or fp["center"], (iw, idp), rot_i),
                                      (fp["center"], (iw, idp), rot_i)], host.get("room_id"))
        plan = R.plan_decor(item, host, caster, local["verts"], local["faces"], support,
                            lean_deg=float(frame.get("lean_deg") or 0.0), shelf=frame.get("shelf"), back_caster=back,
                            max_top_z=max_top)
        keys = local.get("keys")
    if "not_rested" in plan:
        record = dict(plan["not_rested"], room_id=item.get("room_id"))
        summary["decor_not_rested"].append(record)
        warnings.append(f"decor {dtype} {item.get('id')} on {host['id']}: not rested ({record['reason']}); not built")
        return None
    status = item.get("status") if item.get("status") in ("verified", "unverified", "assumed") else "assumed"
    name = f"decor_{host['id']}_{n}"
    index = pass_indices.get(host["id"]) or 0
    lit = decor_lit(item, bool(getattr(mats, "lamps_on", False)))
    if parametric:
        used = sorted(set(keys), key=keys.index)
        if lit:
            keys = [f"{LIT_KEY}{k}" if k in _shade_keys(local.get("parts") or []) else k for k in keys]
            used = sorted(set(keys), key=keys.index)
        accent = P.DECOR_COLOURS.get(str(item.get("colour") or ""))
        slots = [_part_material(mats, k, False, accent=accent, colour=part_colour(item, k),
                                lit=lit or bulb_glows(dtype, k), params=part_params(item, k, host)) for k in used]
        ob = _mesh_object(name, plan["verts"], plan["faces"], slots, [used.index(k) for k in keys], collection,
                          host["id"], "decor", status)
        for poly in ob.data.polygons:
            poly.use_smooth = dtype in ("cushion", "throw")
        method = f"parametric (fallback: {reason})" if dtype != "throw" else "procedural (textiles)"
        materials = [m.name for m in slots]
        textured = any(mats.library.textured(m) for m in slots)
    else:
        ob = _mesh_object(name, plan["verts"], plan["faces"], geo["materials"], geo["face_materials"], collection,
                          host["id"], "decor", status, uvs=geo["uvs"], uv_name=geo["uv_name"],
                          fallback_material=library.proxy("proxy"))
        method = "library"
        materials = [m.name for m in ob.data.materials if m is not None]
        textured = any(_material_is_textured(m) for m in geo["materials"])
    pose = plan["pose"]
    x0, y0, z0, x1, y1, z1 = _bounds(plan["verts"])
    how = f"{dtype} on {host['type']} {host['id']} ({support}: {pose.get('how')})"
    entry = {
        "name": name, "wenart_id": host["id"], "kind": "decor", "status": status, "level_id": level["id"],
        "element_id": host["id"], "host_id": host["id"], "room_id": host.get("room_id"), "type": dtype,
        "source": "added_by_ai", "decor_method": "ai" if item.get("method") == "ai" else "rule",
        "slot": item.get("slot"), "colour": item.get("colour"),
        "evidence": ([dict(e) for e in item.get("evidence") or []] if item.get("method") == "ai" else [])
        or [{"file": "decor", "method": "rule", "confidence": float(item.get("confidence") or 1.0), "text": how}],
        "pass_index": index, "assumed": {"rest": pose.get("how")},
        "center": [(x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0], "size": [x1 - x0, y1 - y0, z1 - z0],
        "rotation_deg": float(pose.get("rotation_deg") or item.get("rotation_deg") or 0.0),
        "asset": item.get("asset") if not parametric else None, "method": method,
        "bbox_m": [round(x1 - x0, 4), round(y1 - y0, 4), round(z1 - z0, 4)], "fit_scale": [1.0, 1.0, 1.0],
        "materials": materials, "material": materials[0] if materials else None, "textured": textured,
        "fallback_reason": reason if parametric else None, "decor_id": item.get("id"), "support": support,
        "rest": dict(plan["rest"], attempt=plan["attempt"], how=pose.get("how"), footprint=plan["footprint"]),
    }
    if not parametric and local.get("info"):
        entry["fit"] = local["info"]
    if plan.get("weave"):
        entry["weave"] = plan["weave"]              # 29 Oct 2026 (UL121): the throw pair's pattern and fringe as built
    if lit and dtype in LAMP_LIGHTS:
        _lamp_light(dtype, name, ob, pose["center"], float(pose.get("z") or z0), entry,
                    getattr(mats, "collection", None), assumed, host["id"],
                    parts=local.get("parts") if parametric else None, rotation_deg=entry["rotation_deg"])
    ob["wenart_type"] = dtype
    ob["wenart_room"] = host.get("room_id") or ""
    ob["wenart_source"] = "added_by_ai"
    ob["wenart_host"] = host["id"]
    ob["wenart_asset"] = (item.get("asset") or {}).get("asset_id") if not parametric else "parametric"
    ob["wenart_rest_footprint"] = json.dumps(plan["footprint"])
    ob.pass_index = index
    return entry


def _shade_keys(parts: list) -> set:
    return {p["key"] for p in parts if p.get("role") == "shade"}


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
    design, design_notes = _looks().outdoor_design(piece, design, design_notes)   # 28 Oct 2026: open-air rooms
    overrides, override_notes = design_overrides(design, piece["type"])
    piece = dict(piece, design=design)
    fp = piece["footprint"]
    w, d = float(fp["size"][0]), float(fp["size"][1])
    rot = float(fp["rotation_deg"])
    cx, cy = float(fp["center"][0]), float(fp["center"][1])
    # 30 Oct 2026 (UL128, user: "Some frames coming out of the roof it needs fixing"): under a sloped ceiling a piece
    # stays under it: its height at most what the slope over its footprint leaves (``under_roof_cap``); a library
    # model taller than that gives way to the module or parametric piece at that height (below)
    cap = under_roof_cap(level, piece, floor_z)
    roof = None
    if cap is not None and height > cap + UNDER_ROOF_TOL_M:
        roof = {"was": round(height, 4), "height": round(max(cap, MIN_PIECE_H_M), 4), "room_m": cap,
                "reason": f"{piece['type']} {height:.2f} m high where the sloped ceiling over its footprint leaves "
                          f"{cap:.2f} m: built {max(cap, MIN_PIECE_H_M):.2f} m high (UL128)"}
        height = roof["height"]
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
    model_h = fitted_height(piece.get("asset"))
    if cap is not None and file is not None and model_h is not None and model_h > cap + UNDER_ROOF_TOL_M:
        reason = (f"the model is {model_h:.2f} m tall where the sloped ceiling over its footprint leaves {cap:.2f} m "
                  f"(UL128)")
        warnings.append(f"{piece['id']}: {reason}; the piece is built {min(height, max(cap, MIN_PIECE_H_M)):.2f} m "
                        "high from modules or parametric")
        height = min(height, round(max(cap, MIN_PIECE_H_M), 4))
        roof = dict(roof or {"was": round(model_h, 4), "room_m": cap}, height=height, model_m=round(model_h, 4),
                    reason=reason)
        entry["center"][2], entry["size"][2] = floor_z + height / 2.0, height
        file = None
    if roof is not None:
        entry["under_roof"] = roof
        assumed.append({"object": name, "field": "under_roof", "value": roof["height"], "reason": roof["reason"],
                        "parent": piece["id"], "kind": "piece_under_roof"})
    ob = None
    if file is not None:
        try:
            ob = _library_object(piece, file, name, status, floor_z, collection, library, entry, warnings,
                                 unverified_cache, geo_cache, mats=mats, assumed=assumed, overrides=overrides)
        except Exception as exc:  # noqa: BLE001 - a broken file falls back, loudly
            reason = f"import of {file} failed: {type(exc).__name__}: {exc}"
            warnings.append(f"{piece['id']}: {reason}; parametric mesh used")
            ob = None
    if ob is None and (piece.get("asset") or {}).get("method") == MOD.MODULE_METHOD and roof is None:
        # Milestone 13: the module builder (the fit's plan, else the plan of the piece as it is)
        plan, plan_reason = module_plan_of(piece, style)
        if plan is not None and design:
            # 28 Oct 2026: the fronts and handles follow the design the build resolves (style.json, the family's
            # kitchen look), as a parametric piece's do; the fit's plan kept the piece's design of its own stage
            plan = dict(plan, design={**(plan.get("design") or {}), **design})
        if plan is not None:
            try:
                ob = _module_object(piece, plan, name, status, floor_z, collection, mats, entry, overrides=overrides)
            except Exception as exc:  # noqa: BLE001 - a plan the builder cannot build: the family, loudly
                plan_reason = f"module build failed: {type(exc).__name__}: {exc}"
                ob = None
        if ob is None:
            reason = f"{plan_reason}; parametric family used"
            warnings.append(f"{piece['id']}: {reason}")
    if ob is None and roof is not None and (piece.get("asset") or {}).get("method") in ("library", MOD.MODULE_METHOD):
        reason = roof["reason"]                       # 30 Oct 2026 (UL128): the slope over it decides the build
    if ob is None:
        ob = _parametric_object(piece, name, status, floor_z, height + lift, collection, mats, entry,
                                overrides=overrides)
        top = raised_top_m(entry.pop("_parts_z", None), base)
        if top is not None and "top_m" not in entry:
            entry["top_m"] = top          # 30 Oct 2026: a floating nightstand's top (decor and wall art over it)
        entry["method"] = f"parametric (fallback: {reason})"
        entry["fallback_reason"] = reason
        if lift:
            entry["assumed"]["height_lift"] = lift
            assumed.append({"object": name, "field": "height_lift", "value": lift,
                            "reason": "footprint overlaps another piece of the same height; "
                                      "lifted so the top faces do not coincide"})
    look = piece.get("bath_look") if isinstance(piece.get("bath_look"), dict) else {}
    if piece["type"] == "washbasin" and look.get("made_to_measure") and look.get("top_m") and "top_m" not in entry:
        entry["top_m"] = float(look["top_m"]) + base   # 29 Oct 2026 (UL114): the mirror hangs over the vanity's top
    for detail in entry.pop("_details", []):           # the design details of a parametric or module piece
        entry["assumed"][detail["field"]] = detail["value"]
        assumed.append({"object": name, "field": detail["field"], "value": detail["value"],
                        "reason": detail["reason"], "parent": piece["id"], "kind": detail["kind"]})
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
    if entry["method"] == "library":
        ob["wenart_asset"] = (piece.get("asset") or {}).get("asset_id")
    elif entry["method"] == MOD.MODULE_METHOD:
        # the fit's asset_id (``module:<type>:<builder>``; docs/milestone13.md §13.3: objects keep wenart_id <->
        # asset_id), ``module:<builder>`` only for a plan computed here without one (reviewer fix 15 Oct 2026)
        ob["wenart_asset"] = (piece.get("asset") or {}).get("asset_id") or f"module:{entry['module']['builder']}"
    else:
        ob["wenart_asset"] = "parametric"
    # Milestone 12 (scene checks S3, S6): the built front and how the piece was built (Milestone 13: ``module``)
    ob["wenart_front_deg"] = float(G.front_direction_deg(rot))
    ob["wenart_method"] = entry["method"] if entry["method"] in ("library", MOD.MODULE_METHOD) else "parametric"
    ob.pass_index = index
    return entry


def module_plan_of(piece: dict, style: dict | None = None) -> tuple[dict | None, str]:
    """``(plan, reason)`` for a piece the fit marked ``asset.method == "module"`` (pure, Milestone 13): the fit's
    ``asset.module_plan`` when it is a plan of a known builder, else the plan of the piece as it is
    (``modules.module_plan``); None and the reason when neither exists."""
    asset = piece.get("asset") or {}
    plan = asset.get("module_plan")
    if isinstance(plan, dict) and plan.get("builder") in MOD._PART_BUILDERS and plan.get("modules"):
        return plan, "the fit's module plan"
    hints = asset.get("module_hints")
    if isinstance(hints, dict) and hints:
        # fix round after P3: the fit keeps a run's hints (its drawn sink and stoves) in the asset, never on the piece
        piece = dict(piece, module_hints={**(piece.get("module_hints") or {}), **hints})
    plan = MOD.module_plan(piece, style)
    if plan is not None:
        return plan, "module plan of the piece (the fit stored none)"
    return None, (f"asset method 'module' but no module builder fits a {piece.get('type')} of "
                  f"{piece['footprint']['size'][0]:.2f} x {piece['footprint']['size'][1]:.2f} m")


def _module_object(piece, plan, name, status, floor_z, collection, mats, entry, overrides=None):
    """The object of a module plan (Milestone 13): ``modules.build_module`` with the style materials of the parts'
    keys (the piece's design overrides apply, as for a parametric piece), recorded on the entry like a parametric
    piece plus ``module`` (``modules.module_record``) and a design detail of the modules used."""
    unverified = status == "unverified"
    parts = MOD.module_parts(plan)
    keys = [p["key"] for p in parts]
    used = sorted(set(keys), key=keys.index)
    provider = MOD.ModuleMaterials(lambda k: _part_material(mats, k, unverified and k != "glass", overrides=overrides),
                                   collection=collection, floor_z=floor_z, name=name, status=status,
                                   slugs=lambda k: mats.slug(k, overrides))
    ob = MOD.build_module(plan, piece, provider)
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    slots = [provider.get(k) for k in used]
    record = MOD.module_record(plan)
    if isinstance(plan.get("top_m"), (int, float)):          # 29 Oct 2026 (UL114): a vanity's top (the mirror hangs over it)
        entry["top_m"] = float(plan["top_m"])
    if plan.get("items"):
        entry.setdefault("_details_extra", []).append(
            {"field": "bath_items", "kind": "bath_details", "value": ", ".join(plan["items"]),
             "reason": "the floating vanity's styling (UL114 B3, UL123 B19): part of its one mesh"})
    entry.update({"method": MOD.MODULE_METHOD, "fallback_reason": None,
                  "bbox_m": [round(x1 - x0, 4), round(y1 - y0, 4), round(z1 - z0, 4)],
                  "materials": [m.name for m in slots], "material": slots[0].name if slots else None,
                  "textured": any(mats.library.textured(m) for m in slots),
                  "material_keys": {k: mats.slug(k, overrides) for k in used},
                  "bevel": json.loads(ob.get("wenart_bevel") or "null"), "module": record,
                  "_details": [{"field": "modules", "kind": "modules",
                                "value": f"{plan['builder']}: {record['modules']} module(s), "
                                         f"{', '.join(record['products']) or 'no product names'}",
                                "reason": "built from real product modules (docs/milestone13.md §12 D4): no audited "
                                          "library model fits the drawn size; the drawn footprint is kept "
                                          f"(fit {record['fit']})"}]})
    if plan.get("split"):
        entry["_details"].append({"field": "split", "kind": "split", "value": json.dumps(plan["split"]),
                                  "reason": "the drawn footprint includes the chairs (CLAUDE.md): table + chairs"})
    lights = MOD.bay_lights(plan)                 # 30 Oct 2026 (UL135): the light of each bay's LED strip
    if lights:
        entry["bay_lights"] = bay_light_objects(lights, piece, provider.floor_z, collection, name)
        entry["_details"].append({"field": "bay_lights", "kind": "see_through_light",
                                  "value": f"{len(lights)} x {lights[0]['lumens']:.0f} lm, {lights[0]['temperature_k']:.0f} K",
                                  "reason": "an LED strip at the top of every bay lights the contents so they read "
                                            "through the see-through front (UL135; " + lights[0]["source"] + ")"})
    entry["_details"] += entry.pop("_details_extra", [])
    return ob


def bay_light_world(light: dict, footprint: dict, floor_z: float) -> list[float]:
    """The world centre of a bay light given in its wardrobe's frame (pure; ``parametric.world_mesh``'s transform)."""
    x, y, z = (float(v) for v in light["center"])
    rad = math.radians(float(footprint.get("rotation_deg") or 0.0))
    c, s = math.cos(rad), math.sin(rad)
    cx, cy = float(footprint["center"][0]), float(footprint["center"][1])
    return [round(cx + c * x - s * y, 4), round(cy + s * x + c * y, 4), round(float(floor_z) + z, 4)]


def bay_light_objects(lights: list[dict], piece: dict, floor_z: float, collection, name: str) -> list[dict]:
    """30 Oct 2026 (UL135): one area light per bay of a see-through wardrobe (``modules.bay_lights``) under its top at
    the front, pointing down, its colour temperature on; a rig light of the room (``wenart_rig`` ``wardrobe``,
    ``wenart_room``), so render.py hides it while the daylight white point is metered and counts it in the view's rig
    share; not seen by the camera (the strip's LED mesh is). Returns the records (the piece's manifest entry)."""
    import bpy

    from wenart.blender import common

    fp = piece["footprint"]
    out = []
    for light in lights:
        data = bpy.data.lights.new(f"{name}_bay{light['bay']}_light", "AREA")
        data.energy = float(light["energy_w"])
        data.shape = "RECTANGLE"
        data.size, data.size_y = float(light["size_m"][0]), float(light["size_m"][1])
        try:
            data.use_temperature = True
            data.temperature = float(light["temperature_k"])
        except AttributeError:                       # an older Blender: the colour of the temperature
            from wenart.blender import lighting as L
            data.color = L._blackbody_rgb(float(light["temperature_k"]))
        ob = bpy.data.objects.new(data.name, data)
        ob.location = bay_light_world(light, fp, floor_z)
        ob.rotation_euler = (0.0, 0.0, math.radians(float(fp.get("rotation_deg") or 0.0)))   # -Z down, along the run
        ob.visible_camera = False
        collection.objects.link(ob)
        common.set_props(ob, wenart_id=ob.name, kind="light", status="assumed")
        ob["wenart_room"] = piece.get("room_id") or ""
        ob["wenart_rig"] = "wardrobe"
        out.append({"name": ob.name, "bay": light["bay"], "center": list(ob.location), "energy_w": light["energy_w"],
                    "lumens": light["lumens"], "temperature_k": light["temperature_k"], "size_m": light["size_m"]})
    return out


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


def _material_look(mat) -> dict:
    """``{"name", "textured", "rgb", "metallic", "alpha"}`` of an imported material: the Principled BSDF's base colour
    (linear), metallic and alpha, else the viewport colour."""
    out = {"name": getattr(mat, "name", None), "textured": _material_is_textured(mat), "rgb": None, "metallic": 0.0,
           "alpha": 1.0}
    if mat is None:
        return out
    tree = getattr(mat, "node_tree", None)
    bsdf = next((n for n in tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"), None) if tree else None
    try:
        if bsdf is not None:
            out["rgb"] = tuple(float(c) for c in bsdf.inputs["Base Color"].default_value[:3])
            out["metallic"] = float(bsdf.inputs["Metallic"].default_value)
            out["alpha"] = float(bsdf.inputs["Alpha"].default_value)
        else:
            out["rgb"] = tuple(float(c) for c in mat.diffuse_color[:3])
            out["metallic"] = float(getattr(mat, "metallic", 0.0) or 0.0)
    except (KeyError, AttributeError, TypeError):
        pass
    return out


def _dress_fabric(piece: dict, geo: dict, mats_list: list, mats, overrides: dict | None = None
                  ) -> tuple[list, dict | None]:
    """30 Oct 2026 (lesson UL140, user: "I like this sofa but it needs more details"; real04's corner sofa rendered in
    the flat white of its export): the flat upholstery slots of a library soft seat (``soft_seats.fabric_slots``, the
    names read by ``wenart.assets.material_names``) wear the style's fabric (``_Materials``: the linen weave's normal
    and roughness maps, the fabric sheen layer) in the design's fabric colour, else in the named colour nearest the
    slot's own. Returns the materials and the record (None when the model has no flat upholstery slot)."""
    from wenart.assets.material_names import name_rule
    from wenart.blender import soft_seats as SS
    from wenart.style import colours as CL

    if "material_shares" not in geo:              # once per file
        geo["material_shares"] = SS.material_shares(geo["verts"], geo["faces"], geo["face_materials"],
                                                    len(geo["materials"]))
    shares = geo["material_shares"]
    slots = []
    for i, mat in enumerate(mats_list):
        look = _material_look(mat)
        named = name_rule(_base_name(look["name"] or ""))
        slots.append(dict(look, index=i, share=shares[i], rule=named[0] if named else "unnamed"))
    picks = SS.fabric_slots(slots)
    if not picks:
        return mats_list, None
    design = piece.get("design") if isinstance(piece.get("design"), dict) else {}
    wanted = design.get("fabric_colour") or (piece.get("asset") or {}).get("fabric_colour")
    out, rows = list(mats_list), []
    for p in picks:
        own = slots[p["index"]]["rgb"]
        colour = wanted or (CL.nearest(own) if own else None)
        mat = mats.get(P.COLOUR_PREFIX + "fabric", False, colour=colour, overrides=overrides)
        out[p["index"]] = mat
        rows.append({"slot": p["name"], "share": p["share"], "why": p["why"], "colour": colour,
                     "material": getattr(mat, "name", None),
                     "was_rgb": [round(c, 4) for c in own] if own else None})
    return out, {"slots": rows, "colour_source": "design" if wanted else "the slot's own colour (nearest name)",
                 "rule": "soft_seats.fabric_slots (UL140)"}


def _library_object(piece, file: Path, name, status, floor_z, collection, library, entry, warnings,
                    unverified_cache, geo_cache, mats=None, assumed=None, overrides=None):
    from wenart.blender import soft_seats as SS

    asset = piece["asset"]
    soft = piece.get("type") in SS.SOFT_SEAT_TYPES
    # 30 Oct 2026 (UL131, UL140): the file's own shading for every library model; a soft seat's loose parts
    geo = _cached_geometry(file, collection, geo_cache, normals=True, parts=soft)
    if not geo["faces"]:
        raise ValueError("file has no mesh faces")
    join = None
    if soft and geo.get("face_parts") is not None:
        if "vertex_parts" not in geo:             # once per file (a pair of armchairs shares it)
            geo["vertex_parts"] = SS.vertex_parts(len(geo["verts"]), geo["faces"], geo["face_parts"], geo["verts"])
        join = geo["vertex_parts"]
    verts, info = fit_vertices(geo["verts"], asset, piece["footprint"], floor_z, align=depth_alignment(piece, asset),
                               join=join)
    normals = (fit_normals(geo["face_normals"], asset, piece["footprint"], info["fit_scale"])
               if geo.get("face_normals") is not None else None)
    mats_list = geo["materials"]
    if asset.get("recolour"):
        mats_list, record = recolour_materials(mats_list, asset["recolour"], unverified_cache, library)
        entry["recolour"] = record
        for missing in record.get("missing") or []:
            warnings.append(f"{piece['id']}: recolour slot {missing} not found in {asset.get('asset_id')}; left as "
                            "it is")
    if soft and mats is not None:
        mats_list, dressing = _dress_fabric(piece, geo, mats_list, mats, overrides)
        if dressing is not None:
            entry["fabric_dressing"] = dressing
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
                      "furniture", status, uvs=uvs, uv_name=geo["uv_name"], fallback_material=fallback,
                      normals=normals)
    if normals is not None:
        entry["shading"] = {"faces": len(geo["faces"]), "file_smooth": int(geo.get("file_smooth") or 0),
                            "smooth": sum(1 for p in ob.data.polygons[:len(geo["faces"])] if p.use_smooth),
                            "custom_normals": bool(getattr(ob.data, "has_custom_normals", False)),
                            "rule": "the file's own normals (UL131)"}
    if info.get("parts") is not None:
        entry["parts"] = info["parts"]
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
    warnings.extend(fit_mismatch_warnings(piece["id"], asset, fp["size"], info["bbox_m"]))
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
                  "bevel": add_bevel(ob, parts), "_details": design_details(piece["type"], parts),
                  "_parts_z": (float(z0), float(z1))})          # 30 Oct 2026: a hung form's box (raised_top_m)
    return ob


RAISED_PARTS_M = 0.005     # a parametric piece whose parts start this far over its floor hangs (a floating form)


def raised_top_m(parts_z, base: float = 0.0) -> float | None:
    """The built top over the room floor of a parametric piece whose parts start above its own floor (pure; 30 Oct
    2026): ``base`` (its mount bottom) + the parts' top, None for a piece standing on its floor (``parts_z`` = the
    parts' ``(z0, z1)`` in the piece frame). Why: a floating nightstand (R33) is a 0.22 m box hung under its top at
    0.50 m; its manifest box keeps the footprint and the height (0-0.50 m) and ``bbox_m`` the mesh's 0.22 m, so a
    reader of "bottom + bbox height" took its top for 0.22 m (real04 run 20261029-201533: the GPU test said the lamp
    on it stood 0.28 m over it; a picture hung over it would have hung 0.28 m too low)."""
    if not parts_z or float(parts_z[0]) <= RAISED_PARTS_M:
        return None
    return round(float(base) + float(parts_z[1]), 4)


LIT_KEY = "lit:"                     # a part key prefix: the key's material with a glow (a lit lamp's shade)
CLOTH_PREFIX = "cloth:"              # 29 Oct 2026 (UL120): a part key prefix: the fabric in a colour (= modules')


def _part_material(mats, key: str, unverified: bool, accent=None, colour=None, overrides=None, lit: bool = False,
                   params=None):
    """The material of one parametric part key (``_Materials.get``); a ``lit:`` key the glowing copy. 29 Oct 2026
    (UL121): ``params`` (``part_params``: a woven pattern's ink and angle) reach a procedural look."""
    if key.startswith(LIT_KEY):
        return glow_copy(mats.get(key[len(LIT_KEY):], unverified, accent=accent, colour=colour, overrides=overrides))
    if params:
        return mats.get(key, unverified, accent=accent, colour=colour, overrides=overrides, lit=lit, params=params)
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


SLOPE_SEAT_HOW = "mounted on the sloped ceiling: its top centre on the ceiling plane over it, tilted onto the slope"


def slope_seated(item: dict, dtype: str) -> bool:
    """Whether a decor light is mounted on a sloped ceiling (pure): a ceiling light the decor stage gave a
    ``slope_mount`` (``wenart.furniture.ceiling_lights.slope_mount``)."""
    return dtype == "ceiling_light" and isinstance(item.get("slope_mount"), dict)


def slope_seat(item: dict, verts, floor_z: float, z_above: float, top_m: float) -> tuple[list, float, dict]:
    """30 Oct 2026 (M14 on real04 run 20261030-043021-full; pure): a library ceiling light mounted on a sloped ceiling
    with its model's top centre on the plane over its centre (``top_m`` over the floor): ``(verts moved, z_above,
    hang record)``. The verts are moved up or down so their top meets the plane there; ``slope_verts`` then tilts them
    onto the plane about that point. The hang record says so (``gap_left_m`` 0: nothing hangs in the air)."""
    top = max(float(v[2]) for v in verts)
    shift = round(floor_z + float(top_m) - top, 4)
    moved = [(x, y, z + shift) for x, y, z in verts] if abs(shift) > 1e-9 else list(verts)
    model_h = top - min(float(v[2]) for v in verts)
    xs, ys = [float(v[0]) for v in verts], [float(v[1]) for v in verts]
    z_new = round(float(z_above) + shift, 4)
    sm = item.get("slope_mount") if isinstance(item.get("slope_mount"), dict) else {}
    hang = {"bottom_m": z_new, "model_top_m": round(float(top_m), 4), "ceiling_m": round(float(top_m), 4),
            "gap_m": 0.0, "lift_m": shift, "cord_m": 0.0, "canopy_m": 0.0, "how": SLOPE_SEAT_HOW,
            "top_m": round(float(top_m), 4), "gap_left_m": 0.0, "model_h_m": round(model_h, 4),
            "cord_xy": [round((min(xs) + max(xs)) / 2.0, 4), round((min(ys) + max(ys)) / 2.0, 4)],
            "tilt_deg": sm.get("tilt_deg")}
    return moved, z_new, hang


def slope_verts(item: dict, verts) -> list:
    """28 Oct 2026 (user: "More lights from the ceiling needed"): a ceiling light the decor stage mounted on a sloped
    ceiling (``slope_mount``, ``wenart.furniture.ceiling_lights``) is turned onto the ceiling plane about its top
    centre (``geom2d.tilt_onto_plane``), so it sits on the slope instead of hanging level under its low side; every
    other item unchanged (pure)."""
    sm = item.get("slope_mount") if isinstance(item.get("slope_mount"), dict) else None
    if not sm or item.get("type") != "ceiling_light" or not verts:
        return verts
    from wenart.blender import geom2d

    plane = list(sm.get("plane") or [0.0, 0.0])
    xs, ys = [float(v[0]) for v in verts], [float(v[1]) for v in verts]
    pivot = ((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0, max(float(v[2]) for v in verts))
    return geom2d.tilt_onto_plane(verts, pivot, float(plane[0]), float(plane[1]))


# 30 Oct 2026 (lesson UL170, user: "keep the black one and make it give light"): a pendant is the light of its zone
# (the rig puts the room's light into it, ``lighting.pendant_lights``), so its bulb parts glow in every mood; its shade
# and its own lamp light stay with the mood (``decor_lit``)
GLOWING_BULB_TYPES: tuple[str, ...] = ("pendant_light",)


def bulb_glows(dtype: str, key: str) -> bool:
    """Whether a decor part's ``key`` is a bulb that glows whatever the mood (pure): the bulb of a pendant."""
    return dtype in GLOWING_BULB_TYPES and key == "bulb"


def decor_lit(item: dict, lamps_on_mood: bool) -> bool:
    """A lamp-type decor item emits light: its ``light_on`` when set, else the mood's ``lamps_on`` (pure)."""
    if item.get("type") not in LAMP_LIGHTS:
        return False
    if isinstance(item.get("light_on"), bool):
        return item["light_on"]
    return lamps_on_mood


PENDANT_MIN_DROP_M = 0.3      # as wenart.furniture.decor_ai.PENDANT_MIN_DROP_M: the least drop under the ceiling


def pendant_hang(z_above: float, ceiling: float) -> tuple[float, str | None]:
    """Fix round after P4a (17 Oct 2026; module docstring): ``(height, why not)`` of a pendant whose shade bottom is
    ``z_above`` m over the floor under a ceiling ``ceiling`` m over the floor at its slot (pure). The cord always
    ends at the ceiling (height = ceiling - bottom) and the bottom never moves; ``why not`` is None, or the reason
    the pendant is not built when that drop is under ``PENDANT_MIN_DROP_M`` (a low, sloped ceiling over its slot)."""
    drop = round(float(ceiling) - float(z_above), 4)
    if drop < PENDANT_MIN_DROP_M - 1e-9:
        return drop, (f"ceiling {float(ceiling):.2f} m over its slot too low (bottom {float(z_above):.2f} m, drop "
                      f"{drop:.2f} m < {PENDANT_MIN_DROP_M:g} m)")
    return drop, None


PENDANT_LIFT_MAX_M = 0.10     # 28 Oct 2026: a hung model this close under the ceiling is lifted to meet it


def hang_plan(dtype: str, bottom_m: float, model_h: float, ceiling_m: float) -> dict:
    """28 Oct 2026 (user on real04 run 005318's salon: "Light is flying in the air needs to be connected to ceiling";
    pure): how a ceiling-hung decor model (heights over its floor) reaches the ceiling over it. A ceiling light, or a
    pendant whose top is at most ``PENDANT_LIFT_MAX_M`` under the ceiling (its own cord and canopy), or above it, moves
    by ``lift_m`` until its top meets the ceiling; a pendant further down keeps its shade where the decor stage put it
    and gets a cord (``cord_m``) and a ceiling canopy (``parametric.suspension_parts``) from its top to the ceiling.
    ``gap_left_m`` = the ceiling minus the top of what is built (0: connected). Why: the decor stage plans a pendant
    from its bottom up to the ceiling (dec_L-1_008: 0.45 x 0.45 x 1.35 m from 1.50 m), the build fits a library model
    to its own size (0.358 m) and its top hung 0.99 m under the ceiling with nothing up to it; a flush ceiling light
    of 2.4 cm took the planned 12 cm and hung 9.6 cm under the ceiling (dec_L0_026)."""
    bottom, model_h, ceiling = float(bottom_m), float(model_h), float(ceiling_m)
    gap = ceiling - (bottom + model_h)
    rec = {"bottom_m": round(bottom, 4), "model_top_m": round(bottom + model_h, 4), "ceiling_m": round(ceiling, 4),
           "gap_m": round(gap, 4), "lift_m": 0.0, "cord_m": 0.0, "canopy_m": 0.0}
    if dtype == "ceiling_light" or gap <= PENDANT_LIFT_MAX_M + 1e-9:
        rec["lift_m"] = round(gap, 4)
        rec["how"] = ("flush: its top on the ceiling" if dtype == "ceiling_light" else
                      "its own top on the ceiling (moved %+.3f m)" % gap)
    else:
        rec["cord_m"] = round(gap - P.SUSPENSION_CANOPY_H_M, 4)
        rec["canopy_m"] = P.SUSPENSION_CANOPY_H_M
        rec["how"] = f"a {rec['cord_m']:.2f} m cord and a ceiling canopy from its top to the ceiling"
    top = bottom + model_h + rec["lift_m"] + rec["cord_m"] + rec["canopy_m"]
    rec["top_m"] = round(top, 4)
    rec["gap_left_m"] = round(ceiling - top, 4)
    return rec


def top_point(verts) -> tuple[float, float]:
    """The plan point of a model's top (pure): the mean x, y of its vertices within 1 cm of its highest one (where a
    pendant's cord leaves it)."""
    zmax = max(float(v[2]) for v in verts)
    top = [v for v in verts if float(v[2]) >= zmax - 0.01]
    return (sum(float(v[0]) for v in top) / len(top), sum(float(v[1]) for v in top) / len(top))


def wall_art_materials(dtype: str, materials_list: list) -> tuple[list, dict | None]:
    """Fix round after P4a (17 Oct 2026; module docstring): ``(materials, mirror_glass record)`` of a library wall
    decor model: for a mirror a new list from ``materials.mirror_glass_materials`` (the cached geometry's list is
    shared per file and never changed), else the model's own list and None."""
    if dtype != "mirror":
        return materials_list, None
    from wenart.blender import materials as M

    return M.mirror_glass_materials(list(materials_list))


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


def floor_class_item(item: dict, host: dict | None) -> tuple[dict, str | None]:
    """``(item, None)`` to build, or ``(item, why)`` not to build (pure; 30 Oct 2026, lesson UL151, user on real04's
    kitchen: "this vase on the floor not making sense"): a table-size item with no host standing on the floor is not
    built (``rest.floor_class_problem``); a floor piece (a plant, a floor vase) whose fitted library model is too low or
    a table piece by its title is built as ours at the type's height (its ``asset`` dropped, ``floor_class_note``)."""
    from wenart.blender import rest as R

    if not R.on_the_floor(item, host):
        return item, None
    dtype = item.get("type")
    if dtype in R.TABLETOP_TYPES:
        return item, (f"{R.floor_class_problem(dtype)}: it has no surface to stand on (no host); the decor stage "
                      "puts it on a worktop, a table, a shelf or a sideboard")
    asset = item.get("asset") if isinstance(item.get("asset"), dict) else {}
    if dtype in R.FLOOR_MIN_H_M and asset.get("method") == "library":
        box = asset.get("bbox_m") or []
        why = R.floor_class_problem(dtype, float(box[2]) if len(box) > 2 else None, asset.get("title"))
        if why is not None:
            w, d, h = P.decor_size(dtype, item.get("size") or [0.4, 0.4])
            size = [w, d, max(h, R.FLOOR_MIN_H_M[dtype])]
            return dict(item, asset=None, size=size,
                        floor_class_note=f"{why}: built as our {dtype.replace('_', ' ')} {size[2]:.2f} m high instead "
                                         f"of {asset.get('asset_id')}"), None
    elif dtype in R.FLOOR_MIN_H_M:
        w, d, h = P.decor_size(dtype, item.get("size") or [0.4, 0.4])
        if h < R.FLOOR_MIN_H_M[dtype] - 1e-9:                # ours, as tall as a floor piece of its type
            return dict(item, size=[w, d, R.FLOOR_MIN_H_M[dtype]],
                        floor_class_note=f"{R.floor_class_problem(dtype, h)}: built "
                                         f"{R.FLOOR_MIN_H_M[dtype]:.2f} m high"), None
    return item, None


UNDER_ROOF_CLEAR_M = 0.02        # = build.WINDOW_DECOR_CEILING_CLEAR_M: what stays under a sloped ceiling, stays this far
UNDER_ROOF_TOL_M = 0.005         # a piece this much over what the slope leaves is cut down (a rounding is no cut)
MIN_PIECE_H_M = 0.05
UNDER_ROOF_EXEMPT: tuple[str, ...] = ("stair",)        # fixed equipment the stair builder makes


def under_roof_cap(level: dict, piece: dict, floor_z: float) -> float | None:
    """How tall a piece may be over its bottom (``floor_z``, world: its floor and mount height) under the sloped
    ceiling over its footprint (pure; 30 Oct 2026, lesson UL128): the lowest ``ceiling_above`` over its footprint less
    ``UNDER_ROOF_CLEAR_M``; None on a level without a sloped ceiling, for ``UNDER_ROOF_EXEMPT`` or without a
    footprint."""
    fp = piece.get("footprint") if isinstance(piece.get("footprint"), dict) else None
    if not level.get("ceiling_planes") or piece.get("type") in UNDER_ROOF_EXEMPT or not fp or not fp.get("size") \
            or under_sky(level, piece.get("room_id")):
        return None
    low, _how = ceiling_above(level, fp["center"], fp["size"], float(fp.get("rotation_deg") or 0.0))
    return round(float(level.get("elevation") or 0.0) + low - UNDER_ROOF_CLEAR_M - float(floor_z), 4)


def fitted_height(asset) -> float | None:
    """The fitted library model's height (``asset.bbox_m[2]``, the fit's scaled box), None without one (pure)."""
    box = (asset or {}).get("bbox_m") if isinstance(asset, dict) else None
    if (asset or {}).get("method") != "library" or not box or len(box) < 3:
        return None
    try:
        return float(box[2])
    except (TypeError, ValueError):
        return None


def under_sky(level: dict, room_id) -> bool:
    """A room of the level open to the sky (a roof terrace, a balcony out of the roof: ``level["open_rooms"]``, the
    build's ``prepare``): no ceiling over it (pure; 30 Oct 2026, UL128: the sloped ceiling's planes run on past the
    roof's outline and would cap a terrace's chairs)."""
    return bool(room_id) and room_id in (level.get("open_rooms") or ())


def slope_top_z(level: dict, footprints, room_id=None) -> float | None:
    """The highest world z an item may reach under the sloped ceiling over ``footprints`` (``[(centre, (w, d),
    rotation_deg)]``: the lowest ``ceiling_above`` over them, ``UNDER_ROOF_CLEAR_M`` under it; pure; 30 Oct 2026, lesson
    UL128), None on a level without a sloped ceiling or in a room under the sky (``under_sky``)."""
    if not level.get("ceiling_planes") or under_sky(level, room_id):
        return None
    low = min(ceiling_above(level, c, s, r)[0] for c, s, r in footprints)
    return round(float(level.get("elevation") or 0.0) + low - UNDER_ROOF_CLEAR_M, 4)


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
    # Milestone 12: hosted decor rests on the built mesh (``_create_hosted_decor``); here: the floor, the item's own
    # height (curtains, blinds, lights) or, behind ``--proxies``, a proxy box's top.
    z_above, z_how = decor_height_above_floor(item, host_entry)
    ceiling, ceiling_how = ceiling_above(level, center, (w, d), rot)    # Milestone 10: sloped under a roof
    on_slope = slope_seated(item, dtype)
    if on_slope:
        # 30 Oct 2026 (the model review's M14 on real04 run 20261030-043021-full: six L1 flush lights 0.04 m under the
        # slope with nothing up to it): a light mounted on a sloped ceiling has its top centre on the plane over its
        # centre and is tilted onto it about that point (``slope_verts``); the lowest point over its box left the
        # top centre half its width x the slope under the plane
        ceiling, ceiling_how = ceiling_above(level, center, (0.0, 0.0), rot)[0], SLOPE_SEAT_HOW
    if dtype == "ceiling_light" and z_how != "center[2]":
        z_above, z_how = round(ceiling - h, 4), f"ceiling (flush, {ceiling_how})"
    if dtype == "pendant_light":
        # Milestone 10: the cord reaches the ceiling. Fix round after P4a: the shade bottom stays where the decor stage
        # put it and the cord gets shorter under a low (sloped) ceiling; too low a drop is not built (pendant_hang)
        cut_to_fit = z_above + h > ceiling + 1e-6
        h, too_low = pendant_hang(z_above, ceiling)
        if too_low is not None:
            room_of = host.get("room_id") if host is not None else item.get("room_id")
            warnings.append(f"decor {dtype} {where}: {too_low} ({ceiling_how}); not built")
            if skipped is not None:
                skipped.append({"id": item.get("id"), "type": dtype, "room_id": room_of, "reason": too_low})
            return None
        if cut_to_fit:
            z_how = f"{z_how}; cord shortened to {ceiling_how}"
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
        # fix round after P4b: the item's own id (a hosted item's element_id and wenart_id are its host's)
        "decor_id": item.get("id"),
    }
    if item.get("fixture"):                # 29 Oct 2026 (UL106): a light's role (statement, bedside, downlight)
        entry["fixture"] = item["fixture"]
    if isinstance(item.get("track"), dict):  # 30 Oct 2026 (UL170): a track's mini pendants (the rig lights each)
        entry["track"] = item["track"]
    file, reason = resolve_asset(item.get("asset"), assets_dir)
    ob = None
    hang, z_above0, z_how0 = None, z_above, z_how
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
            if dtype in CEILING_DECOR_TYPES and not (dtype == "ceiling_light" and item.get("slope_mount")):
                # 28 Oct 2026 (hang_plan): the model fitted to its own size reaches the ceiling over it
                cord_xy = top_point(verts)
                ceil_c = ceiling if dtype == "ceiling_light" else ceiling_above(level, cord_xy, (0.0, 0.0))[0]
                hang = dict(hang_plan(dtype, z_above, float(info["bbox_m"][2]), ceil_c), cord_xy=list(cord_xy))
                if abs(hang["lift_m"]) > 1e-6:
                    verts = [(x, y, z + hang["lift_m"]) for x, y, z in verts]
                    z_above = round(z_above + hang["lift_m"], 4)
                    z_how = f"{z_how}; {hang['how']}"
            if on_slope:                                   # 30 Oct 2026 (M14): the model's top on the plane
                verts, z_above, hang = slope_seat(item, verts, floor_z, z_above, ceiling)
                z_how = f"{z_how}; {hang['how']}"
            verts = slope_verts(item, verts)               # 28 Oct 2026: a ceiling light on a sloped ceiling
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
            hang, z_above, z_how = None, z_above0, z_how0
    lit = decor_lit(item, bool(getattr(mats, "lamps_on", False)))
    if ob is None:
        parts = P.decor_parts(dtype, w, d, h, item)
        if dtype in BRIEF_COLOURED_DECOR:                # Milestone 10: the cushion and rug colour (brief, AI)
            parts = [dict(part, key=P.COLOUR_PREFIX + part["key"]) if part["key"] == "fabric" else part
                     for part in parts]
        if lit:
            parts = [dict(part, key=f"{LIT_KEY}{part['key']}") if part["role"] == "shade" else part for part in parts]
        verts, faces, keys = P.world_mesh(parts, footprint["center"], rot, floor_z + z_above)
        verts = slope_verts(item, verts)                   # 28 Oct 2026: a ceiling light on a sloped ceiling
        used_keys = sorted(set(keys), key=keys.index)
        accent = P.DECOR_COLOURS.get(str(item.get("colour") or ""))       # Milestone 9: the AI decor's colour
        overrides = {"pot": pot_override(item)} if dtype == "plant_large" else None
        slots = [_part_material(mats, k, False, accent=accent,
                                colour=towel_part_colour(item, k) if k in TOWEL_DECOR_KEYS else item.get("colour"),
                                overrides=overrides,
                                lit=lit or bulb_glows(dtype, k)) for k in used_keys]
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
        if dtype in CEILING_DECOR_TYPES:                  # 28 Oct 2026: the parametric light spans up to the ceiling
            hang = dict(hang_plan(dtype, z_above, z1 - z0, ceiling), cord_xy=list(footprint["center"]),
                        how=SLOPE_SEAT_HOW if on_slope else "the parametric light's own canopy on the ceiling")
            if on_slope:
                hang["tilt_deg"] = (item.get("slope_mount") or {}).get("tilt_deg")
            hang.update(lift_m=0.0, cord_m=0.0, canopy_m=0.0, top_m=round(z_above + z1 - z0, 4),
                        gap_left_m=round(ceiling - z_above - (z1 - z0), 4))
        if lit and dtype in LAMP_LIGHTS:
            _lamp_light(dtype, name, ob, footprint["center"], floor_z + z_above, entry,
                        getattr(mats, "collection", None), assumed if assumed is not None else [], owner_id,
                        parts=parts, rotation_deg=rot)
    elif lit and dtype in LAMP_LIGHTS:
        _lamp_light(dtype, name, ob, footprint["center"], floor_z + z_above, entry, getattr(mats, "collection", None),
                    assumed if assumed is not None else [], owner_id)
    if hang is not None:
        entry["hang"] = dict(hang, ceiling_how=ceiling_how)
        if hang["cord_m"] > 0.0 or hang["canopy_m"] > 0.0:
            sparts = P.suspension_parts(hang["cord_m"])
            sv, sf, sk = P.world_mesh(sparts, hang["cord_xy"], 0.0, floor_z + hang["model_top_m"] + hang["lift_m"])
            used_s = sorted(set(sk), key=sk.index)
            sslots = [_part_material(mats, k, False) for k in used_s]
            cord_ob = _mesh_object(f"{name}_cord", sv, sf, sslots, [used_s.index(k) for k in sk], collection,
                                   owner_id, "decor", status)
            cord_ob.pass_index = index
            cord_ob["wenart_type"] = dtype
            cord_ob["wenart_room"] = room_id or ""
            cord_ob["wenart_source"] = "added_by_ai"
            cord_ob["wenart_detail"] = "suspension"
            entry["suspension"] = {"name": f"{name}_cord", "cord_m": hang["cord_m"], "canopy_m": hang["canopy_m"],
                                   "materials": [m.name for m in sslots if m is not None]}
            (assumed if assumed is not None else []).append(
                {"object": f"{name}_cord", "field": "suspension", "value": hang["how"], "parent": owner_id,
                 "kind": "suspension", "reason": "a hung light is connected to the ceiling over it (28 Oct 2026)"})
    if item.get("window_id"):
        entry["window_id"] = item["window_id"]
    if item.get("slope_mount") and dtype == "ceiling_light":
        entry["slope_mount"] = dict(item["slope_mount"])
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
    max_h = item.get("max_height_m")
    fixture = item.get("fixture")
    if fixture in P.BATH_MIRRORS:             # 29 Oct 2026 (UL114 B4, UL123 B14, UL124 B22): the bathroom's mirrors
        from wenart.blender import bath_parts as BT
        if fixture == "round_mirror":
            dia = min(w, BT.ROUND_MIRROR_D_M[1], float(max_h) if isinstance(max_h, (int, float)) and max_h > 0
                      else BT.ROUND_MIRROR_D_M[1])
            return [dia, 0.04, dia]
        if fixture == "backlit_mirror":
            h = BT.BACKLIT_MIRROR_H
            if isinstance(max_h, (int, float)) and max_h > 0:
                h = min(h, float(max_h))
            return [w, 0.03, h]
        return [w, 0.03, BT.led_mirror_height(w, max_h)]
    h = w if item.get("shape") == "round" else w * MIRROR_ASPECT      # 29 Oct 2026 (R10): a round mirror
    if item.get("shape") == "arch":
        h = w * 1.6                                                    # ... (R19): an arched one, tall
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
        if isinstance(host_entry.get("top_m"), (int, float)):
            # 29 Oct 2026 (UL114): a floating vanity's top (its decor clusters and the mixer stand over it)
            host_top = float(host_entry["top_m"])
    elif anchors and any(p["id"] == anchors[0] for p in on_level):
        warnings.append(f"decor {dtype} {owner_id}: piece {anchors[0]} is not built; hung at the item's bottom_m")
    # 30 Oct 2026 (UL128; real04 run 20261028-005318: the mirror dec_L1_013 hung by the level's flat 2.45 m ceiling,
    # its top 2.17 m over the floor where the slope over its wall was lower, showed through the roof): the ceiling over
    # the item's place on its wall (the sloped one under the roof)
    wall_at = item.get("wall_point") or item.get("center") or (host_entry or {}).get("center") or [0.0, 0.0]
    ceiling, _how = ceiling_above(level, wall_at, (float(box[0]), max(float(box[1]), 0.02)),
                                  float(item.get("rotation_deg") or 0.0))
    footprint, mount = wall_art_placement(item, box, host_top, ceiling)
    if footprint is None:
        skipped.append({"id": owner_id, "type": dtype, "room_id": room_id, "reason": mount["reason"]})
        return None
    index = pass_indices.get(owner_id) or len(pass_indices) + 1
    pass_indices[owner_id] = index
    name = f"decor_{owner_id}"
    w, dp, h = mount["box_m"]
    status = item.get("status") if item.get("status") in ("verified", "unverified", "assumed") else "assumed"
    mirror_glass = None
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
        model_mats, mirror_glass = wall_art_materials(dtype, geo["materials"])    # fix round after P4a: the glass
        ob = _mesh_object(name, verts, geo["faces"], model_mats, geo["face_materials"], collection, owner_id,
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
        "decor_id": owner_id,                         # fix round after P4b: every decor entry names its item
    }
    if mirror_glass is not None:
        entry["mirror_glass"] = mirror_glass
    ob["wenart_type"] = dtype
    ob["wenart_room"] = room_id or ""
    ob["wenart_source"] = "added_by_ai"
    ob["wenart_host"] = ""
    ob["wenart_anchor"] = ",".join(anchors)
    ob["wenart_asset"] = asset.get("asset_id") if (asset and not parametric) else "parametric"
    ob.pass_index = index
    return entry
