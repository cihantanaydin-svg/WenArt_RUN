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
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Optional

CATALOG_PATH = Path(__file__).resolve().parent / "catalog.json"
OBJAVERSE_SUFFIX = "_objaverse"        # catalog.json -> catalog_objaverse.json (same folder; M7)
LIBRARY_SUFFIX = "_library"            # catalog.json -> catalog_library.json (same folder; M8, preferred)
LICENCE = "CC0"
CC_BY = "CC-BY-4.0"
SOURCES = ("polyhaven", "objaverse", "abo", "generated")
LIBRARY_SOURCES = ("objaverse", "abo", "generated")      # written by the prep pod (wenart/assets/objaverse.py)
# Licence -> its flag (docs/milestone8.md §2): None for CC0 and CC BY 4.0 (credit only), else what limits the use.
# The Objaverse licence strings map onto these names in wenart/assets/objaverse.yaml (licences).
LICENCE_FLAGS: dict[str, Optional[str]] = {
    LICENCE: None, CC_BY: None,
    "CC-BY-NC-4.0": "non_commercial", "CC-BY-NC-SA-4.0": "non_commercial", "CC-BY-NC-ND-4.0": "non_commercial",
    "CC-BY-SA-4.0": "share_alike", "CC-BY-ND-4.0": "no_derivatives",
    "Sketchfab-Editorial": "non_commercial", "Sketchfab-Standard": "unknown", "Sketchfab-Free-Standard": "unknown",
    "unknown": "unknown",
}
FLAGS = ("non_commercial", "share_alike", "no_derivatives", "unknown")
GENERATED_LICENCE_PREFIX = "generated"   # e.g. "generated (TRELLIS.2-4B, MIT)" (docs/milestone8.md §3)
# Source -> licences its models may carry (docs/milestone7.md §6.3, docs/milestone8.md §2): Poly Haven is CC0 only;
# Objaverse objects carry the uploader's licence (any, flagged unless CC0 / CC BY 4.0); ABO is CC BY 4.0; a generated
# model's licence starts with "generated" (checked apart).
SOURCE_LICENCES: dict[str, tuple[str, ...]] = {"polyhaven": (LICENCE,), "objaverse": tuple(LICENCE_FLAGS),
                                               "abo": (CC_BY,)}
# Fields a CC BY entry needs for its credit line (CC BY 4.0 §3(a)(1)); every library model but a generated one has
# them (any non-CC0 licence asks for the credit).
CC_BY_FIELDS = ("title", "author", "source_url", "licence_url", "via", "attribution")
# The fields of a generated model's ``generated`` record (docs/milestone8.md §2).
GENERATED_FIELDS = ("prompt", "image_sha256", "model", "revision", "seed")
KINDS = ("furniture", "decor")
DECOR_TYPES = ("cushion", "plant", "rug", "wall_art",    # library decor (docs/milestone8.md §4)
               "vase", "bowl", "plant_small", "table_lamp", "mirror")   # Milestone 9 (docs/milestone9.md §3)
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
    "unknown",
)

# Heights of the parametric fallback (the Milestone 3 proxy table, docs/milestone3.md, conventions; the
# Milestone 7 types as in wenart/furniture/schemas.py HEIGHTS).
PARAMETRIC_HEIGHTS: dict[str, float] = {
    "bed_single": 0.55, "bed_double": 0.55, "sofa": 0.85, "armchair": 0.85, "table_dining": 0.75,
    "table_coffee": 0.45, "desk": 0.75, "chair": 0.9, "wardrobe": 2.1, "bookshelf": 1.8, "tv_unit": 0.5,
    "nightstand": 0.5, "dresser": 0.8, "kitchen_counter": 0.9, "kitchen_island": 0.9, "fridge": 1.8,
    "stove": 0.9, "sink_kitchen": 0.9, "washbasin": 0.85, "toilet": 0.4, "shower": 2.0, "bathtub": 0.55,
    "washing_machine": 0.85, "stair": 2.7, "side_table": 0.55, "floor_lamp": 1.6, "potted_plant": 1.0,
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


def licence_flag_of(licence: Optional[str]) -> Optional[str]:
    """The flag of a catalogue licence (``LICENCE_FLAGS``; generated models: None; an unknown name: unknown)."""
    text = str(licence or "")
    if text.startswith(GENERATED_LICENCE_PREFIX):
        return None
    return LICENCE_FLAGS.get(text, "unknown")


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
    that is parametric in ``base`` but has models in ``extra`` loses its parametric entry; ids stay unique across
    both. ``merged`` records the source, the number of models (and decor models) added and the replaced types."""
    validate(base)
    validate(extra, complete=False)
    added = [e for e in extra.get("entries", []) if not e.get("parametric")]
    decor = list(extra.get("decor", []))
    library_types = {e["type"] for e in added}
    replaced = sorted(e["type"] for e in base.get("entries", []) if e.get("parametric") and e["type"] in library_types)
    out = dict(base)
    out["entries"] = [e for e in base.get("entries", []) if not (e.get("parametric") and e["type"] in library_types)]
    out["entries"] += added
    if decor:
        out["decor"] = list(base.get("decor", [])) + decor
    out["merged"] = {"source": source, "models_added": len(added), "parametric_replaced": replaced}
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
    expect = licence_flag_of(licence)
    if ("licence_flag" in e or expect is not None) and e.get("licence_flag") != expect:
        raise CatalogError(f"{e['id']}: licence {licence} needs licence_flag {expect!r}, not "
                           f"{e.get('licence_flag')!r} (docs/milestone8.md §2)")
    if licence == CC_BY or (source in ("objaverse", "abo") and licence != LICENCE):
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
