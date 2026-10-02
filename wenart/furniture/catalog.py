"""The furniture catalogue: our furniture types -> CC0 Poly Haven models.

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
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Optional

CATALOG_PATH = Path(__file__).resolve().parent / "catalog.json"
LICENCE = "CC0"
SOURCES = ("polyhaven",)
AXES = ("-Y", "+Y", "-X", "+X")

# Every furniture type of the building schema enum (wenart/schema/building.schema.json).
FURNITURE_TYPES = (
    "bed_single", "bed_double", "sofa", "armchair", "table_dining", "table_coffee", "desk", "chair", "wardrobe",
    "kitchen_counter", "kitchen_island", "fridge", "stove", "sink_kitchen", "washbasin", "toilet", "shower",
    "bathtub", "tv_unit", "bookshelf", "nightstand", "dresser", "washing_machine", "unknown",
)

# Heights of the parametric fallback (the Milestone 3 proxy table, docs/milestone3.md, conventions).
PARAMETRIC_HEIGHTS: dict[str, float] = {
    "bed_single": 0.55, "bed_double": 0.55, "sofa": 0.85, "armchair": 0.85, "table_dining": 0.75,
    "table_coffee": 0.45, "desk": 0.75, "chair": 0.9, "wardrobe": 2.1, "bookshelf": 1.8, "tv_unit": 0.5,
    "nightstand": 0.5, "dresser": 0.8, "kitchen_counter": 0.9, "kitchen_island": 0.9, "fridge": 1.8,
    "stove": 0.9, "sink_kitchen": 0.9, "washbasin": 0.85, "toilet": 0.4, "shower": 2.0, "bathtub": 0.55,
    "washing_machine": 0.85, "unknown": 0.8,
}

REQUIRED_MODEL_FIELDS = ("id", "type", "source", "licence", "bbox_m", "bbox_model_m", "bbox_min_m", "bbox_max_m",
                         "front_axis", "up_axis", "origin_offset", "front_axis_confidence", "url", "gltf")


class CatalogError(ValueError):
    """The catalogue file is malformed (a test catches this before any fit runs)."""


class Catalog:
    """The loaded catalogue: ``candidates(type)``, ``parametric_types``, ``entry(id)``."""

    def __init__(self, data: dict, path: Optional[Path] = None):
        self.data = data
        self.path = path
        self.entries: list[dict] = list(data.get("entries", []))
        self.decor: list[dict] = list(data.get("decor", []))
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

    def entry(self, asset_id: str) -> Optional[dict]:
        for e in self.models + self.decor:
            if e.get("id") == asset_id:
                return e
        return None

    def ids(self) -> list[str]:
        return [e["id"] for e in self.models] + [e["id"] for e in self.decor]

    def types(self) -> list[str]:
        return sorted({e["type"] for e in self.entries})


def load(path: Optional[Path] = None) -> Catalog:
    path = Path(path) if path else CATALOG_PATH
    return Catalog(json.loads(path.read_text(encoding="utf-8")), path)


def validate(data: dict) -> None:
    """Raise ``CatalogError`` unless every entry is complete and consistent."""
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        raise CatalogError("catalog has no entries")
    seen_types, seen_ids = set(), set()
    for e in entries:
        if e.get("parametric"):
            if e.get("type") not in FURNITURE_TYPES:
                raise CatalogError(f"parametric entry with unknown type {e.get('type')!r}")
            if e["type"] in seen_types:
                raise CatalogError(f"type {e['type']} is both parametric and library")
            seen_types.add(e["type"])
            continue
        _validate_model(e, seen_ids)
        if e["type"] not in FURNITURE_TYPES:
            raise CatalogError(f"{e['id']}: unknown furniture type {e['type']!r}")
    library_types = {e["type"] for e in entries if not e.get("parametric")}
    if library_types & seen_types:
        raise CatalogError(f"types both parametric and library: {sorted(library_types & seen_types)}")
    missing = set(FURNITURE_TYPES) - library_types - seen_types
    if missing:
        raise CatalogError(f"types with neither a library entry nor a parametric entry: {sorted(missing)}")
    for e in data.get("decor", []):
        _validate_model(e, seen_ids)


def _validate_model(e: dict, seen_ids: set) -> None:
    for key in REQUIRED_MODEL_FIELDS:
        if key not in e:
            raise CatalogError(f"{e.get('id', '?')}: missing field {key!r}")
    if e["id"] in seen_ids:
        raise CatalogError(f"duplicate id {e['id']}")
    seen_ids.add(e["id"])
    if e["source"] not in SOURCES or e["licence"] != LICENCE:
        raise CatalogError(f"{e['id']}: source/licence {e['source']}/{e['licence']} is not CC0 Poly Haven")
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
