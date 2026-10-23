"""The furniture catalogue: our furniture types -> CC0 Poly Haven models (and,
from Milestone 7, CC0 / CC BY 4.0 Objaverse models; from Milestone 8 the
library of every source: ABO, Objaverse of any licence, generated models).

``catalog.json`` was written by hand on 2026-10-01 after surveying the 521
models of ``GET https://api.polyhaven.com/assets?type=models`` (85 in the
``furniture`` category), downloading the chosen 1k glTFs with
``wenart.assets.models.fetch_model`` and measuring every bounding box from
the glTF geometry (``measure_gltf``). The front axis of every model was
decided by looking at the geometry: for seating and beds the taller side
(back, headboard) is the back; for cabinets, shelves, desks and
nightstands the side with the doors, drawers or open shelves is the
front (checked on orthographic Blender renders of each model from -Y, +Y
and above). Models with no front (tables, plants) say so with
``front_axis_confidence: "low"``.

Frames:

- Model frame: the Z-up Blender frame the glTF importer produces (metres,
  origin wherever the author left it; Poly Haven puts it on the floor near
  the footprint centre). ``bbox_min_m`` / ``bbox_max_m`` are in this frame.
- Piece frame (Milestone 2 block frame, ``wenart/synthetic/blocks.py``):
  width along X, depth along Y, front = -Y, origin at the footprint centre
  on the floor.
- ``front_axis`` is the model-frame axis that points out of the model's
  front (``-Y``, ``+Y``, ``-X`` or ``+X``); ``up_axis`` is always ``+Z``;
  ``origin_offset`` is the model-frame point (bbox centre x, bbox centre y,
  bbox min z) that must land on the piece origin. Re-orientation, once per
  asset: translate by ``-origin_offset``, rotate about Z by
  ``reorient_rotation_deg(entry)`` (so the front axis becomes -Y), then
  ``bbox_m`` = ``[width (X), depth (Y), height (Z)]`` holds in the piece
  frame; the fit scale of ``wenart.furniture.fit`` applies on top of that.

Entry shapes in ``catalog.json``::

    {"id": "sofa_02", "type": "sofa", "source": "polyhaven", "licence": "CC0", "name": "Sofa 02",
     "bbox_m": [1.8072, 0.8178, 0.7095], "bbox_model_m": [...], "bbox_min_m": [...], "bbox_max_m": [...],
     "front_axis": "-Y", "up_axis": "+Z", "origin_offset": [x, y, z], "front_axis_confidence": "high",
     "front_axis_note": "...", "url": "https://polyhaven.com/a/sofa_02", "api_url": ".../files/sofa_02",
     "gltf": "models/sofa_02/sofa_02_1k.gltf", "resolution": "1k", "polycount": 2728, "dimensions_api_mm": [...]}
    {"type": "toilet", "parametric": true, "reason": "..."}

``gltf`` is relative to the assets dir (where ``fetch_model`` puts it).

Milestone 7 (docs/milestone7.md §6.3, §6.6, user decision 7):

- Every furniture model carries ``styles`` (style families of
  ``wenart.style.vocabulary.STYLE_FAMILIES`` or ``neutral``) and every
  Poly Haven model a ``style_note`` (why). The Poly Haven tags were taken
  from ``GET https://api.polyhaven.com/info/<id>`` (tags, description,
  attributes) on 2026-10-03, and for the ten models the Milestone 6 renders
  show, from those renders (``results/renders``); the thumbnails
  (cdn.polyhaven.com) were not reachable from the session. A family is
  claimed only when the tags or the description say it (conservative: a
  missing family means the parametric mesh, a wrong one the clash the user
  saw). Beds carry ``has_mattress``; ``old_bed_frame`` (a wire-mesh frame
  without a mattress) is gone, so ``bed_single`` is parametric until the
  Objaverse library adds one.
- ``load()`` merges ``catalog_objaverse.json`` (next to the catalogue file,
  written by the prep pod; absent -> nothing) after ``catalog.json``: its
  models are added and a type that is parametric in ``catalog.json`` but has
  models in the Objaverse file stops being parametric (``merged``
  records it). Both files pass ``validate`` (the Objaverse file alone with
  ``complete=False``: it need not cover every type).
- Sources and licences: ``polyhaven`` entries are CC0; ``objaverse``
  entries are ``CC0`` or ``CC-BY-4.0`` (no NC/ND/SA) and carry ``glb``,
  ``sha256_glb``, ``uid``, ``title``, ``author``, ``source_url``,
  ``licence_url``, ``via`` and ``attribution`` (all required for CC BY).
  Their boxes are metres: the raw GLB box times the optional ``unit_scale``
  (the prep pod's unit guess, 1.0 when absent: one of ``UNIT_SCALES``, or
  any positive finite factor with a ``unit_note`` when the model's units are
  unknown and it was normalised by type), which the fit carries into the
  asset and the scene builder applies to the imported mesh before
  ``fit_scale``.

Milestone 8 (docs/milestone8.md §1, §2):

- ``load()`` merges ``catalog_library.json`` (the prep pod's one library
  catalogue of every source) when it is next to the catalogue file, else the
  M7 ``catalog_objaverse.json`` (a fallback until the library file replaces
  it); both are merged the same way (``merge``), and the library file's
  ``decor`` models are appended to the ``decor`` section.
- Sources: ``polyhaven`` (CC0), ``objaverse`` (any licence: CC0 / CC BY 4.0
  unflagged, every other licence of ``LICENCE_FLAGS`` with its
  ``licence_flag``), ``abo`` (Amazon Berkeley Objects, CC BY 4.0, units
  known: metres) and ``generated`` (TRELLIS.2 models, licence
  ``generated (...)``, with the ``generated`` record of how they were made).
  Library entries (every source but Poly Haven) carry the frame fields, the
  GLB fields, ``styles`` and, except generated ones, the credit fields.
- New entry fields: ``source``, ``licence_flag`` (null for CC0 / CC BY 4.0
  and generated models; else ``non_commercial``, ``share_alike``,
  ``no_derivatives`` or ``unknown``; recorded, never filtered while the user
  allows any licence), ``quality`` (the two judges' photoreal quality),
  ``kind`` (``furniture`` / ``decor``) and ``decor_type`` (decor), and for
  beds ``bed_frame`` (a frame without a mattress: the scene builder adds the
  parametric bedding on its deck) with ``deck_height_m``.
- Library decor models live in the ``decor`` section with ``kind: decor``,
  ``decor_type`` in ``DECOR_TYPES`` and ``type`` ``decor_<decor_type>``;
  ``Catalog.decor_candidates(decor_type)`` lists them (the Poly Haven decor
  models of ``catalog.json`` stay as they were).
- ``bed_usable(entry)``: a bed model with a mattress, or a bed frame with a
  deck; ``has_mattress`` keeps its M7 meaning.

Milestone 10 (docs/milestone10.md §1.1, §4.5, §4.6; track F): the 14 new furniture types (a parametric entry
each in ``catalog.json`` until the library pod's ``catalog_library.json`` adds models) and the 12 new decor
types; library entries may carry track D's judged fields ``material_slots``, ``material_tags``,
``recolourable_fabric``, ``recolourable_wood`` (``wenart/assets/recolour.py``) and, for plants, ``species`` and
``pot`` (checked by ``_validate_m10_fields`` when present; the fit reads them, ``fit.GLB_ASSET_FIELDS``), a corner
sofa's ``chaise_side``. The wall cabinet stays parametric whatever the library file holds (``PARAMETRIC_ONLY_TYPES``).

Milestone 13 (docs/milestone13.md §6, §12 D1 and D3, §13.2; track T1): the licence model.

- What: every entry carries ``licence``, ``licence_url``, ``licence_declared_by`` (``publisher`` | ``uploader``),
  ``licence_flag`` (one of ``LICENCE_FLAGS``: ``none`` | ``non_commercial`` | ``share_alike`` | ``no_derivatives`` |
  ``research_only`` | ``regional`` | ``tool_nc``), ``commercial_safe`` and ``attribution``. The fit runs in a
  ``licence_mode`` (``LICENCE_MODES``): ``commercial`` uses only ``commercial_safe`` entries (flag ``none``);
  ``relaxed`` (the PoC projects, user OK of 12 Oct 2026) also uses non-commercial, share-alike, research-only, regional
  and ``tool_nc`` entries; a ``no_derivatives`` entry is never used (we scale and re-texture), nor an audit ``removed``
  or ``pending`` one, nor a licence nobody could read (``unknown``).
- Why: the generated TRELLIS.2 models were exported with nvdiffrast (NVIDIA Source Code License, section 3.3:
  non-commercial), so they are flagged ``tool_nc`` (D3: kept for the PoC, excluded in commercial mode); the HSSD layer
  (T7) is CC BY-NC 4.0. Every render says whether it is commercial-safe (T8 reads the flags the fit writes).
- How: ``licence_flag_of(entry)`` takes the entry's own ``licence_flag`` when it is a stricter flag than the licence
  text gives, else the text (``LICENCE_TEXT_FLAGS``, the ``-NC`` / ``-SA`` / ``-ND`` markers), else the export tool
  (``is_tool_nc``: a generated model whose licence text names TRELLIS.2); ``commercial_safe(entry)`` is flag ``none``;
  ``usable(entry, mode)`` and ``unusable_reason(entry, mode)`` apply the mode; ``licence_mode(brief, env)`` reads
  ``WENART_LICENCE_MODE``, then the brief's ``library.licence_mode``, else ``commercial``. The existing entries got the
  new fields from ``write_licence_fields`` (``python -m wenart.furniture licence-fields``; the old ``licence_flag: null``
  became ``"none"``; every other field stayed byte-identical). ``licence_flag_of`` still accepts a licence text (the
  Milestone 8 call of ``wenart.assets.objaverse``) and then returns ``"none"`` where it returned None.
- Source ``hssd`` (build round 2, 15 Oct 2026; docs/milestone13.md §12 D2, §13.2 row ``hssd.py``): the HSSD object
  models (``wenart.assets.hssd``, entries written by ``wenart.assets.audit.growth_entries.hssd_entry`` on pod P2) are a
  library source like ABO: GLB in the cache, the credit fields, ``styles``; their only licence is ``CC-BY-NC-4.0``
  (``SOURCE_LICENCES``), declared by the publisher (the dataset card), so every entry carries ``licence_flag:
  non_commercial`` and ``commercial_safe: false`` and is used in ``relaxed`` mode only. The credit fields
  (``CC_BY_FIELDS``) are required for every licence but CC0 and a generated one (CC BY-NC 4.0 §3(a)(1) asks for the
  same credit as CC BY 4.0).
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Optional

CATALOG_PATH = Path(__file__).resolve().parent / "catalog.json"
OBJAVERSE_SUFFIX = "_objaverse"        # catalog.json -> catalog_objaverse.json (same folder; M7)
LIBRARY_SUFFIX = "_library"            # catalog.json -> catalog_library.json (same folder; M8, preferred)
LICENCE = "CC0"
CC_BY = "CC-BY-4.0"
SOURCES = ("polyhaven", "objaverse", "abo", "generated", "gso", "hssd", "3dwh")
# written by the prep pod (wenart/assets/objaverse.py); Milestone 12 pod P4 (docs/milestone12.md §6.4): ``gso`` =
# Google Scanned Objects (CC BY 4.0, confirmed per object, ``licence_evidence``; wenart/assets/audit/growth_gso.py);
# Milestone 13 pod P2 (docs/milestone13.md §12 D2): ``hssd`` = the HSSD object models (CC BY-NC 4.0, relaxed mode only;
# wenart/assets/hssd.py, wenart/assets/audit/growth_entries.hssd_entry). = wenart.assets.models.LIBRARY_SOURCES and
# wenart.run.copy.LIBRARY_SOURCES (tests/test_library_growth_p4.py keeps the three equal).
# 3dwh (23 Oct 2026, the user's request): the 3D Warehouse models of the user's zip (wenart/assets/warehouse.py;
# licence not reviewed by the user's decision, relaxed licence mode only, commercial_safe: no).
LIBRARY_SOURCES = ("objaverse", "abo", "generated", "gso", "hssd", "3dwh")
# Milestone 13 (docs/milestone13.md §13.2): the licence modes of the fit and the licence flags of the entries.
LICENCE_MODES: tuple[str, ...] = ("commercial", "relaxed")
LICENCE_MODE_DEFAULT = "commercial"
LICENCE_MODE_ENV = "WENART_LICENCE_MODE"          # overrides the brief (the pod jobs export it, scripts/jobs/full.sh)
LICENCE_MODE_BRIEF_KEY = "library.licence_mode"   # wenart/defaults.yaml brief.library.licence_mode
LICENCE_FLAGS: tuple[str, ...] = ("none", "non_commercial", "share_alike", "no_derivatives", "research_only",
                                  "regional", "tool_nc")
NO_FLAG = "none"
UNKNOWN_FLAG = "unknown"          # a licence nobody could read (Sketchfab-Standard, no metadata): never usable
OWN_LICENCE = "n/a"               # the fit's licence of our own parametric and module geometry (fit.PARAMETRIC_LICENCE)
# The flags no mode may use: no-derivatives (we scale and re-texture, docs/milestone13.md §6) and unknown.
NEVER_USABLE_FLAGS: tuple[str, ...] = ("no_derivatives", UNKNOWN_FLAG)
# The flags an audit may set on top of a CC0 / CC BY text (a dataset's own terms the licence text cannot show); the
# CC markers (-NC, -SA, -ND) must agree with the text, so a CC BY entry never carries non_commercial.
AUDIT_ONLY_FLAGS: tuple[str, ...] = ("research_only", "regional")
# How limiting a flag is (a catalogue flag may be stricter than its licence text says, never looser: _validate_licence).
FLAG_STRICTNESS: dict[str, int] = {NO_FLAG: 0, "regional": 1, "share_alike": 2, "research_only": 3,
                                   "non_commercial": 4, "tool_nc": 4, "no_derivatives": 5, UNKNOWN_FLAG: 6}
# Licence text -> its flag (docs/milestone8.md §2; Milestone 13: ``none`` instead of None for CC0 and CC BY 4.0, and
# CC BY-NC-ND is no_derivatives, the stricter of its two limits). The Objaverse licence strings map onto these names
# in wenart/assets/objaverse.yaml (licences).
LICENCE_TEXT_FLAGS: dict[str, str] = {
    LICENCE: NO_FLAG, CC_BY: NO_FLAG,
    "CC-BY-NC-4.0": "non_commercial", "CC-BY-NC-SA-4.0": "non_commercial", "CC-BY-NC-ND-4.0": "no_derivatives",
    "CC-BY-SA-4.0": "share_alike", "CC-BY-ND-4.0": "no_derivatives",
    "Sketchfab-Editorial": "non_commercial", "Sketchfab-Standard": UNKNOWN_FLAG, "Sketchfab-Free-Standard": UNKNOWN_FLAG,
    "unknown": UNKNOWN_FLAG,
}
# A source's own licence text (not a licence name of the Objaverse table above) -> its flag: the 3D Warehouse models,
# whose licences the user chose not to review (23 Oct 2026; = wenart.assets.warehouse.LICENCE): relaxed mode only.
SOURCE_TEXT_FLAGS: dict[str, str] = {"3DWH-UNREVIEWED": "non_commercial"}
FLAGS = ("non_commercial", "share_alike", "no_derivatives", "unknown")   # the Milestone 8 name (wenart.assets)
GENERATED_LICENCE_PREFIX = "generated"   # e.g. "generated (TRELLIS.2-4B, MIT)" (docs/milestone8.md §3)
# The non-commercial tool in the export chain of the generated TRELLIS.2 models (docs/milestone13.md §2.3, §6, D3):
# o_voxel.postprocess.to_glb imports nvdiffrast (verified in the research of 12 Oct 2026 on the pinned v0.4.0
# LICENSE.txt, byte-identical to main: "Nvidia Source Code License (1-Way Commercial)", 3.3 "may be used ...
# non-commercially"); the Infinigen models were exported by infinigen.tools.export and Blender (BSD-3-Clause, no NC tool).
TOOL_NC_LICENCE_PREFIX = "generated (TRELLIS.2"
TOOL_NC = {"tool": "nvdiffrast", "version": "v0.4.0",
           "licence": "Nvidia Source Code License (1-Way Commercial), section 3.3 non-commercial",
           "licence_url": "https://github.com/NVlabs/nvdiffrast/blob/v0.4.0/LICENSE.txt",
           "where": "o_voxel.postprocess.to_glb (the TRELLIS.2 GLB export and texture bake)",
           "decision": "D3 of 12 Oct 2026: kept for the PoC with licence_flag tool_nc; excluded in commercial mode"}
# Licence text -> the official page (creativecommons.org pages as the catalogue's datasets block and
# wenart/assets/objaverse.yaml already name them; the generated models' code licences on GitHub).
LICENCE_URLS: dict[str, str] = {
    LICENCE: "https://creativecommons.org/publicdomain/zero/1.0/",
    CC_BY: "https://creativecommons.org/licenses/by/4.0/",
    "CC-BY-NC-4.0": "https://creativecommons.org/licenses/by-nc/4.0/",
    "CC-BY-NC-SA-4.0": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
    "CC-BY-NC-ND-4.0": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
    "CC-BY-SA-4.0": "https://creativecommons.org/licenses/by-sa/4.0/",
    "CC-BY-ND-4.0": "https://creativecommons.org/licenses/by-nd/4.0/",
    # MIT for the TRELLIS.2 code and weights (README: "This model and code are released under the MIT License";
    # the LICENSE file of microsoft/TRELLIS.2, verified 12 Oct 2026); the export tool is TOOL_NC
    "generated (TRELLIS.2-4B, MIT)": "https://github.com/microsoft/TRELLIS.2/blob/main/LICENSE",
    # the 3D Warehouse models (licences not reviewed, the user's decision of 23 Oct 2026): the site that hosts them
    "3DWH-UNREVIEWED": "https://3dwarehouse.sketchup.com/",
}
POLYHAVEN_LICENCE_URL = "https://polyhaven.com/license"
# Who declared the licence (docs/milestone13.md §6): the dataset publisher (Amazon for ABO, Poly Haven, Google for GSO,
# the HSSD authors for HSSD, ourselves for generated models) or the uploader of an object (Objaverse: Sketchfab
# uploads, not verified by anyone).
LICENCE_DECLARED_BY: dict[str, str] = {"polyhaven": "publisher", "abo": "publisher", "generated": "publisher",
                                       "gso": "publisher", "hssd": "publisher", "objaverse": "uploader",
                                       "3dwh": "uploader"}
DECLARED_BY_VALUES: tuple[str, ...] = ("publisher", "uploader")
# Source -> licences its models may carry (docs/milestone7.md §6.3, docs/milestone8.md §2): Poly Haven is CC0 only;
# Objaverse objects carry the uploader's licence (any, flagged unless CC0 / CC BY 4.0); ABO is CC BY 4.0; a generated
# model's licence starts with "generated" (checked apart); HSSD is CC BY-NC 4.0 (the dataset card: "You agree to use
# this dataset under the CC BY-NC 4.0 license terms", https://huggingface.co/datasets/hssd/hssd-models, read on
# 15 Oct 2026; = wenart.assets.hssd.LICENCE).
SOURCE_LICENCES: dict[str, tuple[str, ...]] = {"polyhaven": (LICENCE,), "objaverse": tuple(LICENCE_TEXT_FLAGS),
                                               "abo": (CC_BY,), "gso": (CC_BY,), "hssd": ("CC-BY-NC-4.0",),
                                               "3dwh": tuple(SOURCE_TEXT_FLAGS)}
# Fields a CC BY entry needs for its credit line (CC BY 4.0 §3(a)(1)); every library model but a generated one has
# them (any non-CC0 licence asks for the credit).
CC_BY_FIELDS = ("title", "author", "source_url", "licence_url", "via", "attribution")
# The fields of a generated model's ``generated`` record (docs/milestone8.md §2).
GENERATED_FIELDS = ("prompt", "image_sha256", "model", "revision", "seed")
KINDS = ("furniture", "decor")
DECOR_TYPES = ("cushion", "plant", "rug", "wall_art",    # library decor (docs/milestone8.md §4)
               "vase", "bowl", "plant_small", "table_lamp", "mirror",   # Milestone 9 (docs/milestone9.md §3)
               # Milestone 10 (docs/milestone10.md §4.6): ``books`` = library book stacks next to the parametric
               # ``book_set``
               "curtain", "blind", "throw", "books", "candle", "basket", "tray", "clock", "sculpture", "plant_large",
               "pendant_light", "ceiling_light")
# The unit factors of the prep pod's unit guess (docs/milestone7.md §7.2; wenart/assets/objaverse.yaml units).
# An Objaverse entry's optional ``unit_scale`` is one of them, or any positive finite factor with a ``unit_note``
# saying where it comes from (a model of unknown units normalised by type, wenart.assets.objaverse.normalise_unit).
UNIT_SCALES = (1.0, 0.01, 0.0254, 0.001)
AXES = ("-Y", "+Y", "-X", "+X")
NEUTRAL = "neutral"
BED_TYPES = ("bed_single", "bed_double")

# Every furniture type of the building schema enum (wenart/schema/building.schema.json).
FURNITURE_TYPES = (
    "bed_single", "bed_double", "sofa", "armchair", "table_dining", "table_coffee", "desk", "chair", "wardrobe",
    "kitchen_counter", "kitchen_island", "fridge", "stove", "sink_kitchen", "washbasin", "toilet", "shower",
    "bathtub", "tv_unit", "bookshelf", "nightstand", "dresser", "washing_machine",
    "stair", "side_table", "floor_lamp", "potted_plant",              # Milestone 7 (documented-only types)
    # Milestone 10 (docs/milestone10.md §1.1)
    "sofa_corner", "chaise", "ottoman", "bench", "bar_stool", "office_chair", "console_table", "crib", "bunk_bed",
    "sideboard", "shoe_cabinet", "display_cabinet", "tall_cabinet", "wall_cabinet",
    "unknown",
)

# Types built parametrically only (docs/milestone10.md §4.4: the wall cabinet is placed by rule along a drawn
# counter run and built with the counter's fronts): ``merge`` never lets a library model replace their parametric
# entry. = ``wenart.furniture.schemas.RULE_ONLY_TYPES`` (repeated: that module needs jsonschema and the synthetic
# blocks; tests/test_furniture_fit_v2.py keeps them equal).
PARAMETRIC_ONLY_TYPES: tuple[str, ...] = ("wall_cabinet",)
CHAISE_SIDES: tuple[str, ...] = ("left", "right")

# Heights of the parametric fallback (the Milestone 3 proxy table, docs/milestone3.md, conventions; the
# Milestone 7 types as in wenart/furniture/schemas.py HEIGHTS).
PARAMETRIC_HEIGHTS: dict[str, float] = {
    "bed_single": 0.55, "bed_double": 0.55, "sofa": 0.85, "armchair": 0.85, "table_dining": 0.75,
    "table_coffee": 0.45, "desk": 0.75, "chair": 0.9, "wardrobe": 2.1, "bookshelf": 1.8, "tv_unit": 0.5,
    "nightstand": 0.5, "dresser": 0.8, "kitchen_counter": 0.9, "kitchen_island": 0.9, "fridge": 1.8,
    "stove": 0.9, "sink_kitchen": 0.9, "washbasin": 0.85, "toilet": 0.4, "shower": 2.0, "bathtub": 0.55,
    "washing_machine": 0.85, "stair": 2.7, "side_table": 0.55, "floor_lamp": 1.6, "potted_plant": 1.0,
    # Milestone 10 (wenart/furniture/schemas.py HEIGHTS; the wall cabinet's own height)
    "sofa_corner": 0.85, "chaise": 0.8, "ottoman": 0.45, "bench": 0.45, "bar_stool": 0.75, "office_chair": 1.0,
    "console_table": 0.8, "crib": 0.9, "bunk_bed": 1.65, "sideboard": 0.8, "shoe_cabinet": 1.0,
    "display_cabinet": 1.9, "tall_cabinet": 2.1, "wall_cabinet": 0.7,
    "unknown": 0.8,
}

# The frame fields every model has, whatever its source.
FRAME_FIELDS = ("id", "type", "source", "licence", "bbox_m", "bbox_model_m", "bbox_min_m", "bbox_max_m",
                "front_axis", "up_axis", "origin_offset", "front_axis_confidence")
# Poly Haven models (and the Poly Haven decor models).
REQUIRED_MODEL_FIELDS = FRAME_FIELDS + ("url", "gltf")
# Objaverse models (docs/milestone7.md §6.6), written by the prep pod; ABO models the same (docs/milestone8.md §2).
OBJAVERSE_FIELDS = FRAME_FIELDS + ("glb", "sha256_glb", "uid") + CC_BY_FIELDS + ("styles",)
# Generated models: no credit fields (nobody to credit), the record of how they were made instead.
GENERATED_MODEL_FIELDS = FRAME_FIELDS + ("glb", "sha256_glb", "uid", "styles", "generated")


def style_values() -> tuple[str, ...]:
    """The words ``styles`` may hold: the family keywords of ``vocabulary.STYLE_FAMILIES`` and ``neutral``."""
    from wenart.style import vocabulary as V   # pure tables; no PyYAML needed

    return tuple(name for name, _ in V.STYLE_FAMILIES) + (NEUTRAL,)


def objaverse_path(path: Path) -> Path:
    """The Objaverse catalogue next to a catalogue file: ``<stem>_objaverse.json``."""
    path = Path(path)
    return path.with_name(f"{path.stem}{OBJAVERSE_SUFFIX}{path.suffix}")


def library_path(path: Path) -> Path:
    """The library catalogue next to a catalogue file: ``<stem>_library.json`` (docs/milestone8.md §2)."""
    path = Path(path)
    return path.with_name(f"{path.stem}{LIBRARY_SUFFIX}{path.suffix}")


def extra_path(path: Path) -> Optional[Path]:
    """The file ``load`` merges next to ``path``: ``catalog_library.json`` when present, else the M7
    ``catalog_objaverse.json`` when present, else None."""
    for candidate in (library_path(path), objaverse_path(path)):
        if candidate.is_file():
            return candidate
    return None


def licence_text_flag(licence: Optional[str]) -> str:
    """The flag a licence text alone gives (``LICENCE_TEXT_FLAGS``, a source's own text of ``SOURCE_TEXT_FLAGS``,
    else its ``-ND`` / ``-NC`` / ``-SA`` markers): ``none`` for CC0, CC BY 4.0 and a generated model's own licence (the
    export tool is ``is_tool_nc``); ``unknown`` for a name nobody could read."""
    text = str(licence or "").strip()
    if not text:
        return UNKNOWN_FLAG
    if text.startswith(GENERATED_LICENCE_PREFIX):
        return NO_FLAG
    if text in LICENCE_TEXT_FLAGS:
        return LICENCE_TEXT_FLAGS[text]
    if text in SOURCE_TEXT_FLAGS:
        return SOURCE_TEXT_FLAGS[text]
    upper = text.upper()
    if "-ND" in upper:
        return "no_derivatives"
    if "-NC" in upper:
        return "non_commercial"
    if "-SA" in upper:
        return "share_alike"
    if upper in ("CC0", "CC0-1.0", "CC-BY", "CC-BY-4.0") or upper.startswith("CC0 "):
        return NO_FLAG
    return UNKNOWN_FLAG


def is_tool_nc(entry: dict) -> bool:
    """A generated model whose export chain holds a non-commercial tool (``TOOL_NC``): the TRELLIS.2 models (their
    licence text names TRELLIS.2, or their ``generated`` record names nvdiffrast); an explicit ``licence_flag:
    tool_nc`` says so as well. Infinigen models (``infinigen.tools.export`` + Blender) are not."""
    if entry.get("licence_flag") == "tool_nc":
        return True
    if entry.get("source") != "generated" and entry.get("library") != "generated":
        return False
    text = str(entry.get("licence") or entry.get("license") or "")
    rec = entry.get("generated") if isinstance(entry.get("generated"), dict) else {}
    return text.startswith(TOOL_NC_LICENCE_PREFIX) or "nvdiffrast" in str(rec.get("export") or "").lower()


def licence_flag_of(entry) -> str:
    """Milestone 13 (docs/milestone13.md §13.2): the flag of a catalogue entry or a fitted asset, one of
    ``LICENCE_FLAGS`` (or ``unknown`` for a licence nobody could read): the entry's own ``licence_flag`` when it is a
    known flag at least as strict as its licence text gives (the audit may know a regional or research-only limit the
    text does not show), else the text's flag (``licence_text_flag``), else ``tool_nc`` for a generated model exported
    with the non-commercial tool (``is_tool_nc``), else ``none``. A licence text (str) keeps the Milestone 8 answer
    (``wenart.assets.objaverse`` and its tests call it so): None for CC0, CC BY 4.0 and a generated licence, else the
    text's flag; a catalogue entry (dict) always gets a flag word."""
    if entry is None or isinstance(entry, str):
        flag = licence_text_flag(entry)
        return None if flag == NO_FLAG else flag
    text = entry.get("licence") if entry.get("licence") is not None else entry.get("license")
    if text is None or str(text).strip().lower() == OWN_LICENCE:
        text_flag = NO_FLAG        # no licence recorded (a stub; every catalogue entry has one) or our own geometry
    else:
        text_flag = licence_text_flag(text)
    tool_flag = "tool_nc" if is_tool_nc(entry) else NO_FLAG
    strictest = max((text_flag, tool_flag), key=lambda f: FLAG_STRICTNESS.get(f, 0))
    own = entry.get("licence_flag")
    if own in LICENCE_FLAGS or own == UNKNOWN_FLAG:
        if FLAG_STRICTNESS.get(own, 0) >= FLAG_STRICTNESS.get(strictest, 0):
            return own
    return strictest


def commercial_safe(entry: dict) -> bool:
    """True when the entry may be used in ``commercial`` mode: its flag is ``none`` (docs/milestone13.md §6)."""
    return licence_flag_of(entry) == NO_FLAG


def check_mode(mode: Optional[str]) -> str:
    """The mode word, validated (a typo must not silently pick a mode)."""
    if mode is None:
        return LICENCE_MODE_DEFAULT
    word = str(mode).strip().lower()
    if word not in LICENCE_MODES:
        raise ValueError(f"licence mode must be one of {LICENCE_MODES}, got {mode!r}")
    return word


def licence_mode_from(brief: Optional[dict] = None, env: Optional[dict] = None) -> tuple[str, str]:
    """``(mode, where it came from)``: the environment's ``WENART_LICENCE_MODE`` (``env`` defaults to ``os.environ``),
    else the brief's ``library.licence_mode`` (a ``wenart.brief.load_brief`` result, or a raw brief dict), else
    ``commercial``. A value that is no mode word is reported in the source text and skipped (never a silent pick)."""
    env = os.environ if env is None else env
    notes = []
    raw = env.get(LICENCE_MODE_ENV) if isinstance(env, dict) or hasattr(env, "get") else None
    if raw is not None and str(raw).strip():
        word = str(raw).strip().lower()
        if word in LICENCE_MODES:
            return word, f"env {LICENCE_MODE_ENV}"
        notes.append(f"env {LICENCE_MODE_ENV}={raw!r} is no mode word, ignored")
    from wenart import brief as BR

    value = BR.value(brief, LICENCE_MODE_BRIEF_KEY, None) if isinstance(brief, dict) and "values" in brief else (
        ((brief or {}).get("library") or {}).get("licence_mode") if isinstance(brief, dict) else None)
    if value is not None:
        word = str(value).strip().lower()
        if word in LICENCE_MODES:
            assumed = BR.is_assumed(brief, LICENCE_MODE_BRIEF_KEY) if "values" in (brief or {}) else False
            return word, "; ".join(notes + [f"brief {LICENCE_MODE_BRIEF_KEY}"
                                            + (" (default of wenart/defaults.yaml)" if assumed else "")])
        notes.append(f"brief {LICENCE_MODE_BRIEF_KEY}={value!r} is no mode word, ignored")
    return LICENCE_MODE_DEFAULT, "; ".join(notes + [f"default {LICENCE_MODE_DEFAULT}"])


def licence_mode(brief: Optional[dict] = None, env: Optional[dict] = None) -> str:
    """Milestone 13 (docs/milestone13.md §13.2): the fit's licence mode: env ``WENART_LICENCE_MODE`` > brief
    ``library.licence_mode`` > ``commercial`` (``licence_mode_from`` says which one it was)."""
    return licence_mode_from(brief, env)[0]


class CatalogError(ValueError):
    """The catalogue file is malformed (a test catches this before any fit runs)."""


class Catalog:
    """The loaded catalogue: ``candidates(type)``, ``parametric_types``, ``entry(id)``."""

    def __init__(self, data: dict, path: Optional[Path] = None):
        self.data = data
        self.path = path
        self.entries: list[dict] = list(data.get("entries", []))
        self.decor: list[dict] = list(data.get("decor", []))
        self.merged: dict = dict(data.get("merged") or {})
        validate(data)

    @property
    def models(self) -> list[dict]:
        return [e for e in self.entries if not e.get("parametric")]

    @property
    def parametric_types(self) -> list[str]:
        return [e["type"] for e in self.entries if e.get("parametric")]

    def candidates(self, ftype: str) -> list[dict]:
        """Library entries of ``ftype`` in file order (empty for parametric or unknown types)."""
        return [e for e in self.models if e["type"] == ftype]

    def decor_candidates(self, decor_type: str) -> list[dict]:
        """Library decor models (``kind: decor``) of ``decor_type`` (``DECOR_TYPES``) in file order; the Poly Haven
        decor models of ``catalog.json`` are not listed (they have no ``kind``)."""
        return [e for e in self.decor if e.get("kind") == "decor" and e.get("decor_type") == decor_type]

    def entry(self, asset_id: str) -> Optional[dict]:
        for e in self.models + self.decor:
            if e.get("id") == asset_id:
                return e
        return None

    def ids(self) -> list[str]:
        return [e["id"] for e in self.models] + [e["id"] for e in self.decor]

    def types(self) -> list[str]:
        return sorted({e["type"] for e in self.entries})


def load(path: Optional[Path] = None, objaverse: Optional[Path] | bool = True,
         library: Optional[Path] | bool | None = None) -> Catalog:
    """The catalogue at ``path`` (default ``catalog.json``) merged with its library file: with True (default)
    ``catalog_library.json`` next to it when present, else ``catalog_objaverse.json`` when present (``extra_path``);
    a given path; nothing with False/None. ``library`` (when given) wins over the M7 name ``objaverse``; a missing
    file adds nothing."""
    path = Path(path) if path else CATALOG_PATH
    data = json.loads(path.read_text(encoding="utf-8"))
    want = objaverse if library is None else library
    extra = extra_path(path) if want is True else (Path(want) if want else None)
    if extra is not None and extra.is_file():
        data = merge(data, json.loads(extra.read_text(encoding="utf-8")), source=extra.name)
    return Catalog(data, path)


def merge(base: dict, extra: dict, source: str = "catalog_library.json") -> dict:
    """``base`` with the models of ``extra`` appended (docs/milestone7.md §6.6) and its decor models appended to the
    ``decor`` section (docs/milestone8.md §2). Both are validated first (``extra`` with ``complete=False``); a type
    that is parametric in ``base`` but has models in ``extra`` loses its parametric entry, except the types of
    ``PARAMETRIC_ONLY_TYPES`` (Milestone 10: their models are left out and listed as ``parametric_only_dropped``);
    ids stay unique across both. ``merged`` records the source, the number of models (and decor models) added and
    the replaced types."""
    validate(base)
    validate(extra, complete=False)
    models = [e for e in extra.get("entries", []) if not e.get("parametric")]
    added = [e for e in models if e["type"] not in PARAMETRIC_ONLY_TYPES]
    dropped = sorted(str(e.get("id")) for e in models if e["type"] in PARAMETRIC_ONLY_TYPES)
    decor = list(extra.get("decor", []))
    library_types = {e["type"] for e in added}
    replaced = sorted(e["type"] for e in base.get("entries", []) if e.get("parametric") and e["type"] in library_types)
    out = dict(base)
    out["entries"] = [e for e in base.get("entries", []) if not (e.get("parametric") and e["type"] in library_types)]
    out["entries"] += added
    if decor:
        out["decor"] = list(base.get("decor", [])) + decor
    out["merged"] = {"source": source, "models_added": len(added), "parametric_replaced": replaced}
    if dropped:
        out["merged"]["parametric_only_dropped"] = dropped
    if decor:
        out["merged"]["decor_added"] = len(decor)
    validate(out)
    return out


def validate(data: dict, complete: bool = True) -> None:
    """Raise ``CatalogError`` unless every entry is complete and consistent. ``complete`` (the main
    catalogue and the merged one): every furniture type has a library or a parametric entry; the
    Objaverse file alone is checked with ``complete=False`` (models only, any subset of types)."""
    entries = data.get("entries")
    if not isinstance(entries, list) or (not entries and (complete or not data.get("decor"))):
        raise CatalogError("catalog has no entries")      # a partial library file may hold decor models only
    seen_types, seen_ids = set(), set()
    for e in entries:
        if e.get("parametric"):
            if not complete:
                raise CatalogError(f"parametric entry {e.get('type')!r} in a partial (Objaverse) catalogue")
            if e.get("type") not in FURNITURE_TYPES:
                raise CatalogError(f"parametric entry with unknown type {e.get('type')!r}")
            if e["type"] in seen_types:
                raise CatalogError(f"type {e['type']} is both parametric and library")
            seen_types.add(e["type"])
            continue
        _validate_model(e, seen_ids, furniture=True)
        if e["type"] not in FURNITURE_TYPES:
            raise CatalogError(f"{e['id']}: unknown furniture type {e['type']!r}")
    library_types = {e["type"] for e in entries if not e.get("parametric")}
    if library_types & seen_types:
        raise CatalogError(f"types both parametric and library: {sorted(library_types & seen_types)}")
    missing = set(FURNITURE_TYPES) - library_types - seen_types
    if complete and missing:
        raise CatalogError(f"types with neither a library entry nor a parametric entry: {sorted(missing)}")
    for e in data.get("decor", []):
        _validate_model(e, seen_ids, furniture=False)


def _validate_model(e: dict, seen_ids: set, furniture: bool) -> None:
    source = e.get("source")
    if source not in SOURCES:
        raise CatalogError(f"{e.get('id', '?')}: source {source!r} is not one of {SOURCES}")
    required = {"polyhaven": REQUIRED_MODEL_FIELDS, "generated": GENERATED_MODEL_FIELDS}.get(source, OBJAVERSE_FIELDS)
    if furniture and source == "polyhaven":
        required = required + ("styles", "style_note")
    for key in required:
        if key not in e:
            raise CatalogError(f"{e.get('id', '?')}: missing field {key!r}")
    if e["id"] in seen_ids:
        raise CatalogError(f"duplicate id {e['id']}")
    seen_ids.add(e["id"])
    _validate_licence(e, source)
    _validate_kind(e, source, furniture)
    for key in ("bbox_m", "bbox_model_m"):
        if len(e[key]) != 3 or not all(isinstance(v, (int, float)) and v > 0 for v in e[key]):
            raise CatalogError(f"{e['id']}: {key} must be three positive numbers")
    if e["front_axis"] not in AXES or e["up_axis"] != "+Z":
        raise CatalogError(f"{e['id']}: front_axis {e['front_axis']!r} / up_axis {e['up_axis']!r}")
    if e["front_axis_confidence"] not in ("high", "medium", "low"):
        raise CatalogError(f"{e['id']}: front_axis_confidence must be high/medium/low")
    if len(e["origin_offset"]) != 3:
        raise CatalogError(f"{e['id']}: origin_offset must have three numbers")
    # bbox_m is bbox_model_m with x/y swapped when the front axis is along X
    expect = oriented_bbox(e["bbox_model_m"], e["front_axis"])
    if any(abs(a - b) > 1e-6 for a, b in zip(expect, e["bbox_m"])):
        raise CatalogError(f"{e['id']}: bbox_m {e['bbox_m']} does not match bbox_model_m {e['bbox_model_m']} "
                           f"re-oriented by front_axis {e['front_axis']} ({expect})")
    if "styles" in e:
        styles = e["styles"]
        allowed = style_values()
        if not isinstance(styles, list) or not all(isinstance(v, str) for v in styles):
            raise CatalogError(f"{e['id']}: styles must be a list of style words")
        unknown = [v for v in styles if v not in allowed]
        if unknown:
            raise CatalogError(f"{e['id']}: unknown style word(s) {unknown} (allowed: {', '.join(allowed)})")
        if source in LIBRARY_SOURCES and not styles:
            raise CatalogError(f"{e['id']}: a {source} model needs at least one style (docs/milestone7.md §7.2)")
    if "style_note" in e and not (isinstance(e["style_note"], str) and e["style_note"].strip()):
        raise CatalogError(f"{e['id']}: style_note must say why the styles were chosen")
    if furniture and e["type"] in BED_TYPES and not isinstance(e.get("has_mattress"), bool):
        raise CatalogError(f"{e['id']}: a bed model needs has_mattress (true/false)")
    _validate_bed_frame(e, furniture)
    _validate_m10_fields(e)
    if "quality" in e:
        q = e["quality"]
        if not (isinstance(q, list) and len(q) == 2 and all(isinstance(v, int) and not isinstance(v, bool)
                                                            and 1 <= v <= 5 for v in q)):
            raise CatalogError(f"{e['id']}: quality {q!r} must be the two judges' 1..5 answers")
    if source in LIBRARY_SOURCES:
        if not (isinstance(e["sha256_glb"], str) and len(e["sha256_glb"]) == 64):
            raise CatalogError(f"{e['id']}: sha256_glb must be 64 hex digits")
        if not str(e["glb"]).endswith(".glb"):
            raise CatalogError(f"{e['id']}: glb {e['glb']!r} is not a .glb path")
        if "unit_note" in e and not (isinstance(e["unit_note"], str) and e["unit_note"].strip()):
            raise CatalogError(f"{e['id']}: unit_note must say where unit_scale comes from")
        if "unit_scale" in e:
            u = e["unit_scale"]
            if isinstance(u, bool) or not isinstance(u, (int, float)) or not math.isfinite(u) or u <= 0:
                raise CatalogError(f"{e['id']}: unit_scale {u!r} is not a positive finite number")
            if not any(abs(float(u) - f) < 1e-12 for f in UNIT_SCALES) and "unit_note" not in e:
                raise CatalogError(f"{e['id']}: unit_scale {u!r} is not one of {UNIT_SCALES} and has no unit_note "
                                   "(a model normalised by type says so there)")


MATERIAL_TAGS = ("glass", "wood", "metal", "fabric", "rattan", "marble")   # = the schema's design.material_tags
PLANT_SPECIES = ("palm", "monstera", "fiddle_leaf_fig", "olive", "fern", "other")


def _validate_m10_fields(e: dict) -> None:
    """Milestone 10 fields of a library entry, when present: ``material_tags`` from ``MATERIAL_TAGS``,
    ``recolourable_fabric`` / ``recolourable_wood`` booleans, ``material_slots`` a list of slots with an integer
    ``index``, ``species`` one of ``PLANT_SPECIES``, ``chaise_side`` left / right / null."""
    tags = e.get("material_tags")
    if tags is not None and (not isinstance(tags, list) or any(t not in MATERIAL_TAGS for t in tags)):
        raise CatalogError(f"{e['id']}: material_tags {tags!r} must be a list of {', '.join(MATERIAL_TAGS)}")
    for key in ("recolourable_fabric", "recolourable_wood"):
        if key in e and not isinstance(e[key], bool):
            raise CatalogError(f"{e['id']}: {key} must be true/false")
    slots = e.get("material_slots")
    if slots is not None and (not isinstance(slots, list) or any(
            not isinstance(s, dict) or isinstance(s.get("index"), bool) or not isinstance(s.get("index"), int)
            for s in slots)):
        raise CatalogError(f"{e['id']}: material_slots must be a list of slots with an integer index")
    if e.get("species") is not None and e["species"] not in PLANT_SPECIES:
        raise CatalogError(f"{e['id']}: species {e['species']!r} is not one of {', '.join(PLANT_SPECIES)}")
    if e.get("chaise_side") is not None and e["chaise_side"] not in CHAISE_SIDES:
        raise CatalogError(f"{e['id']}: chaise_side {e['chaise_side']!r} is not left, right or null")


def _validate_licence(e: dict, source: str) -> None:
    """The licence rule of the source (``SOURCE_LICENCES``), the flag (``LICENCE_FLAGS``) and the credit fields."""
    licence = e["licence"]
    if source == "generated":
        if not (isinstance(licence, str) and licence.startswith(GENERATED_LICENCE_PREFIX)):
            raise CatalogError(f"{e['id']}: a generated model's licence must start with "
                               f"{GENERATED_LICENCE_PREFIX!r}, not {licence!r}")
        rec = e["generated"]
        missing = [k for k in GENERATED_FIELDS if not isinstance(rec, dict) or k not in rec]
        if missing:
            raise CatalogError(f"{e['id']}: generated record without {', '.join(missing)}")
    elif licence not in SOURCE_LICENCES[source]:
        raise CatalogError(f"{e['id']}: source/licence {source}/{licence} is not allowed "
                           f"({source}: {', '.join(SOURCE_LICENCES[source])})")
    # Milestone 13: the flag the licence text (and the export tool) gives; the entry's own flag may be absent (a file
    # written before Milestone 13: None) or at least as strict (the audit may add research_only / regional); a text
    # flag of NC / SA / ND / unknown must be carried exactly (docs/milestone8.md §2, docs/milestone13.md §6).
    expect = licence_flag_of({k: v for k, v in e.items() if k != "licence_flag"})
    given = e.get("licence_flag")
    if given is not None:
        if given not in LICENCE_FLAGS and given != UNKNOWN_FLAG:
            raise CatalogError(f"{e['id']}: licence_flag {given!r} is not one of {LICENCE_FLAGS} "
                               "(docs/milestone13.md §13.2)")
        if expect in (NO_FLAG, "tool_nc"):
            if given != expect and given not in AUDIT_ONLY_FLAGS:
                raise CatalogError(f"{e['id']}: licence {licence} needs licence_flag {expect!r} (or one of "
                                   f"{AUDIT_ONLY_FLAGS}, a limit the licence text cannot show), not {given!r} "
                                   "(docs/milestone13.md §6)")
        elif given != expect:
            raise CatalogError(f"{e['id']}: licence {licence} needs licence_flag {expect!r}, not {given!r} "
                               "(docs/milestone8.md §2)")
    elif expect not in (NO_FLAG, "tool_nc"):
        raise CatalogError(f"{e['id']}: licence {licence} needs licence_flag {expect!r}, not None "
                           "(docs/milestone8.md §2)")
    if "commercial_safe" in e and (not isinstance(e["commercial_safe"], bool) or e["commercial_safe"] != commercial_safe(e)):
        raise CatalogError(f"{e['id']}: commercial_safe {e['commercial_safe']!r} does not follow its licence flag "
                           f"{licence_flag_of(e)!r} (docs/milestone13.md §6)")
    if "licence_declared_by" in e and e["licence_declared_by"] not in DECLARED_BY_VALUES:
        raise CatalogError(f"{e['id']}: licence_declared_by must be one of {DECLARED_BY_VALUES}, not "
                           f"{e['licence_declared_by']!r}")
    # Every licence but CC0 (and a generated model's own) asks for the credit line: CC BY 4.0 and its NC / SA variants
    # (ABO, GSO, Objaverse, HSSD) all carry §3(a)(1); the Milestone 8 rule named the sources, this one the licences.
    if licence != LICENCE and source != "generated":
        empty = [k for k in CC_BY_FIELDS if not (isinstance(e.get(k), str) and e[k].strip())]
        if empty:
            raise CatalogError(f"{e['id']}: a {licence} entry needs {', '.join(empty)} for its credit line")


def _validate_kind(e: dict, source: str, furniture: bool) -> None:
    """``kind`` / ``decor_type``: entries are furniture; a library decor model (decor section) is ``kind: decor`` with
    a ``decor_type`` of ``DECOR_TYPES`` and the type ``decor_<decor_type>``."""
    kind = e.get("kind", "furniture" if furniture else None)
    if kind is not None and kind not in KINDS:
        raise CatalogError(f"{e['id']}: kind {kind!r} is not one of {KINDS}")
    if furniture and kind != "furniture":
        raise CatalogError(f"{e['id']}: a model in entries must be kind furniture, not {kind!r}")
    if kind == "decor":
        if e.get("decor_type") not in DECOR_TYPES:
            raise CatalogError(f"{e['id']}: decor_type {e.get('decor_type')!r} is not one of {DECOR_TYPES}")
        if e["type"] != f"decor_{e['decor_type']}":
            raise CatalogError(f"{e['id']}: a {e['decor_type']} decor model has type decor_{e['decor_type']}, "
                               f"not {e['type']!r}")
    elif e.get("decor_type") is not None:
        raise CatalogError(f"{e['id']}: decor_type on an entry that is not kind decor")
    if not furniture and source in LIBRARY_SOURCES and kind != "decor":
        raise CatalogError(f"{e['id']}: a {source} model in the decor section needs kind decor")


def _validate_bed_frame(e: dict, furniture: bool) -> None:
    """``bed_frame`` (docs/milestone8.md §2): only on a bed without a mattress, with a positive ``deck_height_m``."""
    deck = e.get("deck_height_m")
    if deck is not None and (isinstance(deck, bool) or not isinstance(deck, (int, float)) or not math.isfinite(deck)
                             or deck <= 0):
        raise CatalogError(f"{e['id']}: deck_height_m {deck!r} is not a positive number")
    frame = e.get("bed_frame")
    if frame is None:
        return
    if not isinstance(frame, bool):
        raise CatalogError(f"{e['id']}: bed_frame must be true/false")
    if frame:
        if not furniture or e["type"] not in BED_TYPES:
            raise CatalogError(f"{e['id']}: bed_frame on a {e['type']} (beds only)")
        if e.get("has_mattress") is not False:
            raise CatalogError(f"{e['id']}: a bed frame has no mattress (has_mattress false)")
        if deck is None:
            raise CatalogError(f"{e['id']}: a bed frame needs deck_height_m (docs/milestone8.md §2: no deck -> "
                               "refused)")


def styles_match(entry: dict, family: Optional[str]) -> bool:
    """True when ``entry`` may be used for a project of style ``family``: its ``styles`` contain the
    family or ``neutral``; every entry matches when the family is None (docs/milestone7.md §6.3)."""
    if family is None:
        return True
    styles = entry.get("styles") or []
    return family in styles or NEUTRAL in styles


def has_mattress(entry: dict) -> bool:
    """A bed model is usable only with a mattress (user decision 7); other types always are."""
    return entry["type"] not in BED_TYPES or entry.get("has_mattress") is True


def bed_usable(entry: dict) -> bool:
    """Milestone 8: a bed model is usable with a mattress, or as a bed frame with a measured deck (the scene builder
    puts the parametric mattress, duvet and pillows on it, docs/milestone8.md §4); other types always are."""
    if entry["type"] not in BED_TYPES:
        return True
    deck = entry.get("deck_height_m")
    return entry.get("has_mattress") is True or (entry.get("bed_frame") is True and isinstance(deck, (int, float))
                                                 and not isinstance(deck, bool) and deck > 0)


# --------------------------------------------------------------------------
# Frame helpers (pure, used by the fitter and the Blender importer)
# --------------------------------------------------------------------------

def reorient_rotation_deg(entry: dict) -> float:
    """Rotation about +Z (degrees, counter-clockwise) that turns the model's front axis into -Y."""
    return {"-Y": 0.0, "+X": 270.0, "+Y": 180.0, "-X": 90.0}[entry["front_axis"]]


def oriented_bbox(bbox_model_m: list[float], front_axis: str) -> list[float]:
    """``[width, depth, height]`` in the piece frame from the model-frame extents."""
    x, y, z = bbox_model_m
    return [y, x, z] if front_axis in ("+X", "-X") else [x, y, z]


def origin_offset(bbox_min_m: list[float], bbox_max_m: list[float]) -> list[float]:
    """The model-frame point that lands on the piece origin: bbox centre in x/y, bbox bottom in z."""
    return [round((bbox_min_m[0] + bbox_max_m[0]) / 2.0, 4), round((bbox_min_m[1] + bbox_max_m[1]) / 2.0, 4),
            round(bbox_min_m[2], 4)]


def bbox_aspect(entry: dict) -> float:
    """``width / depth`` of the entry's piece-frame bounding box."""
    return entry["bbox_m"][0] / entry["bbox_m"][1]


def aspect_error(entry: dict, width: float, depth: float) -> float:
    """``|ln(entry aspect / footprint aspect)|``: 0 for a perfect match, symmetric in both directions."""
    return abs(math.log(bbox_aspect(entry) / (width / depth)))


def parametric_height(ftype: str) -> float:
    return PARAMETRIC_HEIGHTS.get(ftype, PARAMETRIC_HEIGHTS["unknown"])


# Milestone 12 contract (docs/milestone12.md §4.8, §6.2, §13.2; owner: track S; the audit fields: track B).
NOT_USABLE_LICENCE_MARKERS = ("-NC", "-SA", "-ND")
NOT_USABLE_FLAGS = ("non_commercial", "share_alike", "no_derivatives")
# pending: the audit waits for a vision pass (not used, CLAUDE.md library rules)
REMOVED_STATUSES = ("removed", "remove", "pending")
# Types built from code by design (docs/milestone12.md §4.8, D14): the kitchen counter run and island, wall cabinets
# and stairs are made to the drawing; the kitchen and bath fixtures come from code when no audited model fits (§6.4:
# "no open, commercial-safe library has realistic kitchen or bath fixtures; they come from code": our shower, washing
# machine and full-size fridge now, the Infinigen fixtures later), because drawn fixed equipment is built like a
# wall (CLAUDE.md furniture rules) and never left out; such a piece still records its ``library_gap``. Every other
# parametric piece is a library gap (never a parametric sofa, bed or table).
PARAMETRIC_FIXTURE_TYPES: tuple[str, ...] = ("shower", "washing_machine", "fridge", "toilet", "washbasin", "bathtub",
                                             "sink_kitchen", "stove")
BY_DESIGN_PARAMETRIC_TYPES: tuple[str, ...] = ("kitchen_counter", "kitchen_island", "wall_cabinet",
                                               "stair") + PARAMETRIC_FIXTURE_TYPES


def usable(entry: dict, mode: str = "commercial") -> bool:
    """A library entry the fit may use in licence ``mode`` (Milestone 13, docs/milestone13.md §6, §13.2): its audit
    status is not ``removed`` or ``pending`` (``entry["audit"]["status"]`` in keep / fix, or no audit yet: a fitted
    asset dict carries none), and its flag (``licence_flag_of``: the catalogue flag, the licence text's ``-NC`` /
    ``-SA`` / ``-ND`` markers, the export tool) suits the mode: ``commercial`` takes flag ``none`` only
    (``commercial_safe``, the rule of 10 Oct 2026); ``relaxed`` (user OK of 12 Oct 2026) takes every flag but
    ``no_derivatives`` and ``unknown`` (``NEVER_USABLE_FLAGS``). Works on a catalogue entry and on a fitted ``asset``
    dict alike."""
    mode = check_mode(mode)
    audit = entry.get("audit") if isinstance(entry.get("audit"), dict) else {}
    if str(audit.get("status") or "").lower() in REMOVED_STATUSES:
        return False
    flag = licence_flag_of(entry)
    if mode == "commercial":
        return flag == NO_FLAG
    return flag in LICENCE_FLAGS and flag not in NEVER_USABLE_FLAGS


def unusable_reason(entry: dict, mode: str = "commercial") -> Optional[str]:
    """Why ``usable`` refuses an entry in ``mode`` (None when it is usable)."""
    mode = check_mode(mode)
    audit = entry.get("audit") if isinstance(entry.get("audit"), dict) else {}
    if str(audit.get("status") or "").lower() in REMOVED_STATUSES:
        reasons = "; ".join(str(r) for r in audit.get("reasons") or []) or "no reason recorded"
        return f"audit: {str(audit.get('status')).lower()} ({reasons})"
    if not usable(entry, mode):
        flag = licence_flag_of(entry)
        why = ("never used in any mode: no derivatives or an unknown licence" if flag in NEVER_USABLE_FLAGS
               else "not commercial-safe: relaxed mode only")
        return (f"licence {entry.get('licence') or entry.get('license')} ({flag}): not used in {mode} mode ({why}; "
                "CLAUDE.md library rules)")
    return None


# --------------------------------------------------------------------------
# Milestone 13: the licence fields of the existing entries (written by a script, never by hand)
# --------------------------------------------------------------------------

LICENCE_FIELDS: tuple[str, ...] = ("licence", "licence_url", "licence_declared_by", "licence_flag", "commercial_safe",
                                   "attribution")


def licence_url_of(entry: dict) -> str:
    """The official licence page of an entry: its own ``licence_url`` when it has one, else by its licence text
    (``LICENCE_URLS``; Poly Haven's CC0 page for Poly Haven models); '' when nothing is known."""
    own = str(entry.get("licence_url") or "").strip()
    if own:
        return own
    text = str(entry.get("licence") or "")
    if entry.get("source") == "polyhaven" and text == LICENCE:
        return POLYHAVEN_LICENCE_URL
    return LICENCE_URLS.get(text, "")


def licence_fields(entry: dict) -> dict:
    """The Milestone 13 licence fields of an existing entry (pure): ``licence_url`` (filled where missing),
    ``licence_declared_by`` (``LICENCE_DECLARED_BY`` by source), ``licence_flag`` (``licence_flag_of``: ``none``
    instead of None, ``tool_nc`` for the TRELLIS.2 models), ``commercial_safe``, ``attribution`` (a CC0 Poly Haven
    model gets the no-credit line; every other entry keeps its own) and, on a ``tool_nc`` entry, ``licence_flag_note``
    (the tool and the decision). Nothing else."""
    flag = licence_flag_of(entry)
    out = {"licence_url": licence_url_of(entry),
           "licence_declared_by": entry.get("licence_declared_by") or LICENCE_DECLARED_BY.get(str(entry.get("source")),
                                                                                                 "uploader"),
           "licence_flag": flag, "commercial_safe": flag == NO_FLAG}
    if isinstance(entry.get("attribution"), str) and entry["attribution"].strip():
        out["attribution"] = entry["attribution"]
    elif entry.get("source") == "polyhaven":
        out["attribution"] = (f"{entry.get('name') or entry.get('id')} by Poly Haven "
                              f"({entry.get('url') or 'https://polyhaven.com'}), CC0 1.0: no credit required")
    else:
        out["attribution"] = entry.get("attribution") or ""
    if flag == "tool_nc":
        out["licence_flag_note"] = (f"exported with {TOOL_NC['tool']} {TOOL_NC['version']} ({TOOL_NC['licence']}, "
                                    f"{TOOL_NC['licence_url']}) in {TOOL_NC['where']}; {TOOL_NC['decision']}")
    return out


LICENCE_BLOCK_KEYS: tuple[str, ...] = ("licence", "licence_flag", "licence_url", "licence_declared_by",
                                       "commercial_safe", "licence_flag_note", "attribution")
# The keys a new field is inserted after (the last one present): the licence block proper; an entry's own
# ``attribution`` may sit anywhere and stays there.
LICENCE_ANCHOR_KEYS: tuple[str, ...] = LICENCE_BLOCK_KEYS[:-1]


def add_licence_fields(data: dict) -> dict:
    """Give every model entry of a catalogue dict (``entries`` and ``decor``; parametric rows untouched) the Milestone
    13 licence fields, in place, keeping the key order: a field the entry has is set where it is, a new one goes right
    after the last licence field the entry already has (``LICENCE_BLOCK_KEYS``: the licence block stays together and
    the file diff holds the new lines only, no trailing-comma change on the entry's last key). Returns the counts
    (entries touched, flags)."""
    counts: dict = {"entries": 0, "changed": 0, "flags": {}}
    for section in ("entries", "decor"):
        rows = data.get(section) or []
        for i, e in enumerate(rows):
            if not isinstance(e, dict) or e.get("parametric") or "licence" not in e:
                continue
            new = licence_fields(e)
            counts["entries"] += 1
            counts["flags"][new["licence_flag"]] = counts["flags"].get(new["licence_flag"], 0) + 1
            if all(k in e and e[k] == v for k, v in new.items()):
                continue
            anchor = [k for k in e if k in LICENCE_ANCHOR_KEYS][-1]     # "licence" at least
            rebuilt: dict = {}
            pending = dict(new)
            for key, value in e.items():
                rebuilt[key] = pending.pop(key) if key in pending else value
                if key == anchor:
                    for k in LICENCE_BLOCK_KEYS:
                        if k in pending and k not in e:
                            rebuilt[k] = pending.pop(k)
            rebuilt.update(pending)          # cannot happen (every new key is a block key); keeps the data whole
            rows[i] = rebuilt
            counts["changed"] += 1
    return counts


def write_licence_fields(path: Path) -> dict:
    """``add_licence_fields`` on a catalogue file, written back as it was written (indent 1, UTF-8, trailing newline;
    ``wenart.assets.objaverse`` and this package write every catalogue so). Validates before writing."""
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    counts = add_licence_fields(data)
    validate(data, complete=path.name == CATALOG_PATH.name)
    if counts["changed"]:
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    counts["path"] = str(path)
    return counts


def audit_status(entry: dict) -> str | None:
    """``keep`` / ``fix`` / ``removed`` of an entry's audit (track B: ``audit = {status, reasons, fixes, version,
    checked_utc}``), None before the audit has run. A ``fix`` is already applied to the catalogue fields by the audit
    writer (``wenart.assets.audit.write``: ``fixes`` holds the new values, ``before`` the old ones): the fit reads the
    fields as they are."""
    audit = entry.get("audit") if isinstance(entry.get("audit"), dict) else {}
    status = audit.get("status")
    return str(status) if status else None


def vision_doubt(entry: Optional[dict]) -> list[str]:
    """The audit's ``vision_doubt`` of a catalogue entry or a fitted asset (user decision 1a of 11 Oct 2026,
    docs/milestone12.md §14.3): findings of the vision check alone that kept the model in use; the room critic and
    the final check look at such models. [] when there is none."""
    audit = (entry or {}).get("audit") if isinstance((entry or {}).get("audit"), dict) else {}
    return [str(x) for x in audit.get("vision_doubt") or []]


def by_design_parametric(piece: dict) -> bool:
    """True for a piece built from code by design (``BY_DESIGN_PARAMETRIC_TYPES``; a made-to-measure vanity or
    built-in wardrobe of its design, Milestone 10 §4.4)."""
    if piece.get("type") in BY_DESIGN_PARAMETRIC_TYPES:
        return True
    design = piece.get("design") if isinstance(piece.get("design"), dict) else {}
    return bool((piece.get("type") == "washbasin" and design.get("vanity"))
                or (piece.get("type") == "wardrobe" and design.get("built_in")))


def model_flag(entry: Optional[dict], flag: str) -> Optional[bool]:
    """A dressing flag of a model or its fitted asset (track B's audit: ``has_bedding``, ``has_pillows``,
    ``has_cushions``), None when the audit has not said (docs/milestone12.md §13.3)."""
    value = (entry or {}).get(flag)
    return value if isinstance(value, bool) else None


def has_own_bedding(asset: Optional[dict]) -> bool:
    """A bed model that is already made up (its own duvet or pillows): the audit's ``has_bedding`` / ``has_pillows``;
    until the audit has run a model without the flags counts as bare (a mattress model, §1.3)."""
    return bool(model_flag(asset, "has_bedding") or model_flag(asset, "has_pillows"))


def has_own_cushions(asset: Optional[dict]) -> bool:
    """A seat model with loose cushions of its own (the audit's ``has_cushions``): decor cushions would duplicate
    them (§4.7)."""
    return bool(model_flag(asset, "has_cushions"))


# The audit's decor ``contact`` (flat_bottom | hangs | leans | drapes, track B) each decor type needs: a model that
# rests otherwise is not taken (a hanging lamp is no table lamp). Types not listed take any contact.
DECOR_CONTACTS: dict[str, tuple[str, ...]] = {
    **{t: ("flat_bottom",) for t in ("vase", "bowl", "plant_small", "table_lamp", "books", "candle", "tray",
                                     "sculpture", "basket", "plant", "plant_large")},
    **{t: ("hangs",) for t in ("wall_art", "mirror", "clock", "pendant_light", "ceiling_light")},
    "cushion": ("leans", "flat_bottom"), "rug": ("flat_bottom", "drapes"),
}


def contact_fits(entry: dict, decor_type: str) -> bool:
    """A decor model's audited ``contact`` suits its decor type (``DECOR_CONTACTS``); True before the audit."""
    contact = entry.get("contact")
    return contact is None or decor_type not in DECOR_CONTACTS or contact in DECOR_CONTACTS[decor_type]
