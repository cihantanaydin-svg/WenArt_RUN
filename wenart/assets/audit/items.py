"""The audit's items: every furniture and decor model of both catalogues in one shape (docs/milestone12.md §6.1).

What: ``load_items()`` reads ``wenart/furniture/catalog_library.json`` (ABO, Objaverse, generated: ``entries`` and
``decor``) and ``wenart/furniture/catalog.json`` (Poly Haven models and decor; parametric entries are not models)
and returns one record per model: id, catalogue, section, kind, type (a furniture type or a decor name such as
``cushion``), source, licence, title, the frame fields, units, file, counts and the M8-M10 judge fields.

Why: the checks, the vision question, the decisions and the sheets work on one shape whatever the source.

How: pure; the records keep the catalogue's values (no copy of the entry itself). ``has_front(type)`` comes from
``wenart/assets/objaverse.yaml`` (the front rule of the type: ``none`` = no front).
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

from wenart.assets.audit import REPO

LIBRARY_PATH = REPO / "wenart" / "furniture" / "catalog_library.json"
POLYHAVEN_PATH = REPO / "wenart" / "furniture" / "catalog.json"
DECOR_PREFIX = "decor_"
FIELDS = ("bbox_m", "bbox_model_m", "bbox_min_m", "bbox_max_m", "origin_offset", "front_axis", "up_axis",
          "front_axis_confidence", "front_axis_note", "unit_scale", "unit_note", "polycount", "vertices", "textured",
          "vertex_colours", "quality", "judged", "styles", "has_mattress", "bed_frame", "deck_height_m", "thumbnail",
          "licence_flag", "author", "material_slots", "sha256_glb", "glb", "gltf", "abo_product_type", "abo_3dmodel_id",
          "brand", "audit", "real_product", "has_bedding", "has_cushions", "has_pillows", "contact")


def read_json(path) -> Optional[dict]:
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


@lru_cache(maxsize=1)
def _front_rules() -> dict:
    from wenart.assets import objaverse as OV
    return {t: spec.get("front") for t, spec in (OV.load_config().get("types") or {}).items()}


def has_front(ftype: str) -> bool:
    """A type with a front (seating, beds, cabinets, appliances, wall art ...); tables, lamps, plants and most decor
    have none. Unknown types: True (checked as if they had one)."""
    rule = _front_rules().get(ftype)
    return rule != "none"


def type_of(entry: dict) -> tuple[str, str]:
    """``(kind, type)`` of a catalogue entry: decor by its ``decor_type`` (or a ``decor_<name>`` type), else
    furniture."""
    if entry.get("kind") == "decor" or entry.get("decor_type") or str(entry.get("type", "")).startswith(DECOR_PREFIX):
        name = entry.get("decor_type") or str(entry["type"])[len(DECOR_PREFIX):]
        return "decor", name
    return "furniture", str(entry["type"])


def item_of(entry: dict, catalog: str, section: str) -> dict:
    kind, ftype = type_of(entry)
    rec = {"id": entry["id"], "catalog": catalog, "section": section, "kind": kind, "type": ftype,
           "catalog_type": entry["type"], "source": entry.get("source") or ("polyhaven" if catalog == "polyhaven"
                                                                             else "?"),
           "licence": entry.get("licence"), "title": entry.get("title") or entry.get("name") or "",
           "units_known": bool(entry.get("units_known", entry.get("source") in ("abo", "polyhaven")
                                         or catalog == "polyhaven"))}
    for key in FIELDS:
        if key in entry:
            rec[key] = entry[key]
    return rec


def items_of(library: Optional[dict], polyhaven: Optional[dict]) -> list[dict]:
    """The models of both catalogue documents (library first), in catalogue order."""
    out: list[dict] = []
    for doc, catalog in ((library, "library"), (polyhaven, "polyhaven")):
        if not doc:
            continue
        for section in ("entries", "decor"):
            for e in doc.get(section) or []:
                if isinstance(e, dict) and not e.get("parametric") and e.get("id"):
                    out.append(item_of(e, catalog, section))
    return out


def load_items(library: Optional[Path] = None, polyhaven: Optional[Path] = None) -> list[dict]:
    return items_of(read_json(library or LIBRARY_PATH), read_json(polyhaven or POLYHAVEN_PATH))


def model_file(item: dict) -> Optional[str]:
    """The model file relative to the assets folder (GLB of the library, glTF of Poly Haven)."""
    return item.get("glb") or item.get("gltf")
