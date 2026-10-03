"""Generate the synthetic projects and their ground truth.

CLI::

    python -m wenart.synthetic.generate --out projects [--results results/synthetic] [--only synthetic-02]

Deterministic and idempotent: fixed seeds, fixed PDF/DXF metadata, files are
overwritten in place. Two runs give identical truth JSON and identical
document bytes (checked in tests/test_synthetic.py).

Truth assembly rules (what the pipeline is expected to reproduce):
- Elements get one evidence entry per page that shows them. Vector pages give
  ``method: vector`` with the DXF handle or PDF path/char index; raster pages
  give a ``pixel_box`` with ``method: raster`` (walls, openings, furniture
  footprints: deterministic image processing, docs/milestone7.md §0) or ``ocr``
  (texts), because that is how the raster adapter reads a scan or photo. On a
  level drawn only by raster pages (synthetic-02) the furniture *types* come
  from the two VLM passes: one more entry ``method: ai`` per piece. The scale of
  a scan is ``dimension_text`` from the OCR'd dimension texts (a scan carries no
  verified pixel size, so its ``ÖLÇEK 1/100`` note does not count, §0).
- Heights, sill heights and furniture heights are ``null``: the documents do
  not show them. Ceiling height is the assumed default with a warning.
- Furniture from unknown blocks (``BLOK_A``) is ``unknown`` + ``unverified``
  and listed in ``unverified``.

Style photos (``Project.style_photos``, synthetic-05) are copied byte for byte
into ``<project>/style_photos/``; the ingest never reads that folder (top
level only), the style stage does (docs/milestone6.md §3.2).

synthetic-06 (``CadProject``, docs/milestone7.md §5.2) is written by
``generate_cad_project``: the DXF into ``<project>/source/`` (not read by the
pipeline), the DWG at the top level by LibreDWG ``dxf2dwg --as r2000`` (its
sha256 must equal ``projects.DWG_SHA256_06``; without ``dxf2dwg`` the DWG is
not written and the generator says so), and the truth as the generic core
must reproduce it (§1.3 fields: block-name furniture, the virtual separator of
the open kitchen, the assumed level). The titled variant goes to
``tests/fixtures/synthetic-06-titled/`` (``--fixtures``; default only when
``--out`` is the repository's ``projects`` folder).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Optional

import yaml

from wenart import building as B
from wenart import geometry as G
from wenart.style.photos import PHOTO_DIR
from wenart.synthetic import blocks
from shapely.geometry import Point as ShapelyPoint, Polygon
from shapely.ops import unary_union

from wenart.ingest import dwg as dwg_tool
from wenart.synthetic.dxf_writer import INCH_M, cad_text_box, canonical_ring, write_cad_dxf, write_dxf
from wenart.synthetic.model import Level, PageRecord
from wenart.synthetic.pdf_writer import PAGE_H, write_pdf
from wenart.synthetic.projects import CadProject, DxfDoc, PdfDoc, Project, RasterDoc, all_projects
from wenart.synthetic.raster import SCAN_DPI, make_photo, make_scan, preview_from_dxf, preview_from_image, preview_from_pdf

CREATED_UTC = "2026-10-01T00:00:00Z"
PIPELINE_COMMIT = "synthetic-generator"
DEFAULT_RESULTS = Path("results/synthetic")
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURES = REPO_ROOT / "tests" / "fixtures"


# --------------------------------------------------------------------------
# Documents
# --------------------------------------------------------------------------

def _page_spec_dict(spec) -> dict:
    return {"level": spec.level, "title_raw": spec.title, "page_class": spec.page_class,
            "openings": spec.openings(), "furniture": spec.furniture(), "dimensions": spec.dimensions()}


def _raster_record(src: PageRecord, doc: RasterDoc, transform, size, dpi: Optional[float]) -> PageRecord:
    """Page record of a raster made from a vector PDF page: every box mapped to pixels."""
    is_affine = len(transform) == 6
    rec = PageRecord(
        file=doc.file, page=1, kind=doc.kind, page_class=src.page_class, level_id=src.level_id,
        units="px", size=[size[0], size[1]],
        # metres per pixel = metres per point * points per pixel (None for a photo: no single scale)
        scale_metres_per_unit=(src.scale_metres_per_unit * 72.0 / dpi if is_affine and dpi else None),
        transform_kind="affine" if is_affine else "homography",
        building_to_page=(G.compose_affine(transform, src.building_to_page) if is_affine
                          else [v for row in G.matmul(transform, G.affine_to_matrix(src.building_to_page)) for v in row]),
        title_raw=src.title_raw, dpi=dpi,
    )

    def px_box(box):
        return [round(v, 1) for v in G.transform_box(transform, box)]

    for item in src.texts:
        rec.texts.append({**item, "box": px_box(item["box"]), "entity": "pixel_box"})
    for item in src.symbols:
        rec.symbols.append({k: v for k, v in item.items() if k != "paths"} | {"box": px_box(item["box"]), "entity": "pixel_box"})
    for item in src.walls:
        rec.walls.append({**item, "box": px_box(item["box"]), "entity": "pixel_box"})
    for item in src.dimensions:
        rec.dimensions.append({k: v for k, v in item.items() if k not in ("paths", "text_entity")}
                              | {"box": px_box(item["box"]), "entity": "pixel_box"})
    for key, box in src.boxes.items():
        rec.boxes[key] = px_box(box)
        rec.entities[key] = "pixel_box"
    rec.title_entity = "pixel_box"
    rec.scale_entity = "pixel_box"
    return rec


def write_documents(project: Project, project_dir: Path) -> list[tuple[object, PageRecord]]:
    """Write every document; returns (doc, record) pairs in page order."""
    out: list[tuple[object, PageRecord]] = []
    for doc in project.documents:
        if isinstance(doc, DxfDoc):
            spec = doc.page
            rec = write_dxf(spec.level, project_dir / doc.file, doc.file, title_raw=spec.title,
                            page_class=spec.page_class, openings=spec.openings(), furniture=spec.furniture(),
                            dimensions=spec.dimensions())
            out.append((doc, rec))
        elif isinstance(doc, PdfDoc):
            recs = write_pdf([_page_spec_dict(s) for s in doc.pages], project_dir / doc.file, doc.file)
            out.extend((doc, r) for r in recs)
        elif isinstance(doc, RasterDoc):
            src = next(r for d, r in out if isinstance(d, PdfDoc) and d.file == doc.source_pdf and r.page == doc.source_page)
            if doc.kind == "scan":
                transform, size = make_scan(project_dir / doc.source_pdf, doc.source_page, PAGE_H,
                                            project_dir / doc.file, seed=doc.seed)
                out.append((doc, _raster_record(src, doc, transform, size, SCAN_DPI)))
            elif doc.kind == "photo":
                scan = next((d, r) for d, r in out if isinstance(d, RasterDoc) and d.kind == "scan"
                            and d.source_pdf == doc.source_pdf and d.source_page == doc.source_page)
                persp, size = make_photo(project_dir / scan[0].file, project_dir / doc.file, seed=doc.seed)
                # Chain: PDF points -> scan pixels (affine) -> photo pixels (homography);
                # _raster_record prepends building -> PDF points.
                pts_to_scan = G.compose_affine(scan[1].building_to_page, G.invert_affine(src.building_to_page))
                h = G.matmul(persp, G.affine_to_matrix(pts_to_scan))
                out.append((doc, _raster_record(src, doc, h, size, None)))
            else:
                raise ValueError(doc.kind)
        else:
            raise TypeError(type(doc))
    return out


# --------------------------------------------------------------------------
# Truth: building.json
# --------------------------------------------------------------------------

_LAYER_FOR_KIND = {"wall": blocks.LAYER_WALLS, "door": blocks.LAYER_DOORS, "window": blocks.LAYER_WINDOWS,
                   "furniture": blocks.LAYER_FURNITURE, "text": blocks.LAYER_TEXT}


def _evidence_for(rec: PageRecord, element_id: str, kind: str, block: Optional[str] = None,
                  text: Optional[str] = None) -> Optional[dict]:
    """Evidence entry for an element on one page, or None if the page does not show it."""
    entity = rec.entities.get(element_id)
    if entity is None:
        return None
    if rec.kind == "vector" and rec.units == "mm":
        return B.evidence(rec.file, "vector", 1.0, layer=_LAYER_FOR_KIND[kind], entity=entity, block=block, text=text)
    if rec.kind == "vector":
        return B.evidence(rec.file, "vector", 1.0, page=rec.page, entity=entity, text=text)
    method = "ocr" if kind == "text" else "raster"
    return B.evidence(rec.file, method, 1.0, pixel_box=rec.boxes[element_id], dpi=rec.dpi, text=text)


def _title_evidence(rec: PageRecord) -> dict:
    if rec.kind == "vector" and rec.units == "mm":
        return B.evidence(rec.file, "vector", 1.0, layer=blocks.LAYER_TEXT, entity=rec.title_entity, text=rec.title_raw)
    if rec.kind == "vector":
        return B.evidence(rec.file, "vector", 1.0, page=rec.page, entity=rec.title_entity, text=rec.title_raw)
    title = next(t for t in rec.texts if t["role"] == "title")
    return B.evidence(rec.file, "ocr", 1.0, pixel_box=title["box"], dpi=rec.dpi, text=rec.title_raw)


def _scale_block(rec: PageRecord, level: Level) -> Optional[dict]:
    if rec.transform_kind != "affine":
        return None  # a photo has no single scale
    if rec.units == "mm":
        ev = B.evidence(rec.file, "vector", 1.0, entity="$INSUNITS=4")
        return {"metres_per_unit": 0.001, "method": "dxf_insunits", "confidence": 1.0, "evidence": ev}
    scale_text = next(t for t in rec.texts if t["role"] == "scale")
    if rec.kind == "vector":
        ev = B.evidence(rec.file, "vector", 1.0, page=rec.page, entity=rec.scale_entity, text=level.scale_text)
        return {"metres_per_unit": rec.scale_metres_per_unit, "method": "pdf_scale_text", "confidence": 1.0,
                "evidence": ev}
    # A scan has no verified pixel size: its scale comes from the dimension texts (>= 3 agreeing -> 0.9, §2.3/§4.3).
    dim = next(t for t in rec.texts if t["role"] == "dimension")
    ev = B.evidence(rec.file, "ocr", 1.0, pixel_box=dim["box"], dpi=rec.dpi, text=dim["text"])
    return {"metres_per_unit": rec.scale_metres_per_unit, "method": "dimension_text", "confidence": 0.9,
            "evidence": ev}


def _document_format(file: str) -> str:
    suffix = Path(file).suffix.lower()
    return {".dxf": "dxf", ".dwg": "dwg", ".pdf": "pdf"}.get(suffix, "image")


def build_truth(project: Project, pages: list[tuple[object, PageRecord]]) -> dict:
    """Assemble the schema-valid building JSON from the project model and page records."""
    building = B.empty_building(project.name, f"projects/{project.name}", PIPELINE_COMMIT,
                                created_utc=CREATED_UTC, brief=project.brief)
    levels_by_id = {lv.id: lv for lv in project.levels}
    visible = [(d, r) for d, r in pages if not (isinstance(d, PdfDoc) and d.hidden)]

    # Documents
    for doc in project.documents:
        if isinstance(doc, PdfDoc) and doc.hidden:
            continue
        recs = [r for d, r in visible if d is doc]
        entry = {"id": "doc_" + B.slugify(doc.file), "file": doc.file, "format": _document_format(doc.file),
                 "converter": None, "pages": []}
        for rec in recs:
            level = levels_by_id[rec.level_id]
            entry["pages"].append({
                "page": rec.page, "class": rec.page_class, "skip_reason": None, "kind": rec.kind,
                "level_id": rec.level_id, "level_label_raw": rec.title_raw,
                "scale": _scale_block(rec, level),
                "transform_to_building": (_clean(G.invert_affine(rec.building_to_page))
                                          if rec.transform_kind == "affine" else None),
                "confidence": 1.0, "evidence": [_title_evidence(rec)], "debug_image": None,
            })
        building["documents"].append(entry)

    def evidence_list(element_id, kind, block=None, text=None):
        out = []
        for _, rec in visible:
            ev = _evidence_for(rec, element_id, kind, block=block, text=text)
            if ev is not None:
                out.append(ev)
        if not out:
            raise ValueError(f"{element_id}: no page shows it")
        return out

    for level in project.levels:
        building["levels"].append({
            "id": level.id, "label": level.label, "order": level.order, "elevation": level.elevation,
            "ceiling_height": level.ceiling_height, "ceiling_height_source": "assumed_default",
            "evidence": [_title_evidence(r) for _, r in visible if r.level_id == level.id],
        })
        building["warnings"].append(f"Level {level.id}: ceiling height assumed {level.ceiling_height:.2f} m "
                                    "(no section drawing found)")
        for wall in level.walls:
            building["walls"].append({
                "id": wall.id, "level_id": level.id, "start": list(wall.start), "end": list(wall.end),
                "thickness": wall.thickness, "height": level.ceiling_height, "exterior": wall.exterior,
                "status": "verified", "evidence": evidence_list(wall.id, "wall"),
            })
        for opening in level.openings:
            building["openings"].append({
                "id": opening.id, "type": opening.kind, "level_id": level.id,
                "wall_id": level.walls[opening.wall_index].id, "center": list(opening.center),
                "width": opening.width, "height": None, "sill_height": None, "swing_side": opening.swing_side,
                "status": "verified", "evidence": evidence_list(opening.id, opening.kind, block=opening.block),
            })
        for room in level.rooms:
            label_raw = level.labels[room.label_index].label_raw
            evidence = evidence_list(room.id, "text", text=label_raw)
            evidence.append(B.evidence(_first_file_showing(visible, room.wall_ids[0]), "derived", 1.0,
                                       entity="derived-from:" + ",".join(room.wall_ids)))
            furnished = any(p.room_id == room.id for p in level.furniture)
            building["rooms"].append({
                "id": room.id, "level_id": level.id, "label": room.label, "label_raw": label_raw,
                "room_type": room.room_type, "polygon": [list(p) for p in room.polygon],
                "area_computed": room.area_computed, "area_label": room.area_label,
                "has_documented_furniture": furnished, "style_override": None,
                "status": "verified", "evidence": evidence,
            })
        raster_only = all(r.kind != "vector" for _, r in visible if r.level_id == level.id)
        for piece in level.furniture:
            evidence = evidence_list(piece.id, "furniture", block=piece.block)
            if raster_only:
                # No block name on a raster page: the type is what the two VLM passes agree on (docs/milestone7.md §3).
                first = next(r for _, r in visible if r.level_id == level.id and piece.id in r.entities)
                evidence.append(B.evidence(first.file, "ai", 1.0, pixel_box=first.boxes[piece.id],
                                           text=f"type: {piece.type}"))
            building["furniture"].append({
                "id": piece.id, "level_id": level.id, "room_id": piece.room_id, "type": piece.type,
                "type_raw": piece.block, "source": "from_documents",
                "footprint": {"center": list(piece.center), "size": list(piece.size), "rotation_deg": piece.rotation_deg},
                "front_deg": piece.front_deg() if piece.status == "verified" else None,
                "height": None, "asset": None, "status": piece.status,
                "evidence": evidence,
            })
            if piece.status == "unverified":
                building["unverified"].append(piece.id)

    building["conflicts"] = [dict(c) for c in project.conflicts]
    building["warnings"].extend(project.warnings)
    B.validate(building)
    return building


def _clean(numbers) -> list[float]:
    """-0.0 -> 0.0 so the JSON does not carry negative zeros."""
    return [v + 0.0 for v in numbers]


def _first_file_showing(visible, element_id: str) -> str:
    for _, rec in visible:
        if element_id in rec.entities:
            return rec.file
    raise ValueError(element_id)


# --------------------------------------------------------------------------
# Truth: pages.json
# --------------------------------------------------------------------------

def build_pages(pages: list[tuple[object, PageRecord]]) -> dict:
    out = []
    for doc, rec in pages:
        entry = {
            "file": rec.file, "page": rec.page, "class": rec.page_class, "kind": rec.kind,
            "level_id": rec.level_id, "level_label_raw": rec.title_raw, "units": rec.units, "size": rec.size,
            "dpi": rec.dpi, "scale_metres_per_unit": rec.scale_metres_per_unit,
            "transform": {"kind": rec.transform_kind, "building_to_page": _clean(rec.building_to_page)},
            "texts": rec.texts, "symbols": rec.symbols, "walls": rec.walls, "dimensions": rec.dimensions,
        }
        if rec.units == "px":
            matrix = (G.affine_to_matrix(rec.building_to_page) if rec.transform_kind == "affine"
                      else [rec.building_to_page[0:3], rec.building_to_page[3:6], rec.building_to_page[6:9]])
            entry["H_building_to_pixels"] = matrix
        if isinstance(doc, PdfDoc) and doc.hidden:
            entry["hidden"] = True
        out.append(entry)
    return {"pages": out}


# --------------------------------------------------------------------------
# synthetic-06: the CAD project delivered as a DWG (docs/milestone7.md §5.2)
# --------------------------------------------------------------------------

ASSUMED_LEVEL_LABEL = "Ground floor"                # §2.1: one untitled plan page -> L0 "Ground floor", assumed
DOOR_HEIGHT_M = 2.10                                # §1.3 defaults the generic core writes as `assumed`
WINDOW_SILL_M, WINDOW_HEIGHT_M = 0.90, 1.20
WALL_CONFIDENCE = 0.95                              # a DXF hatch on a wall-hint layer (§2.4)
DOOR_CONFIDENCE = 0.95                              # arc + leaf (§2.6)
WINDOW_CONFIDENCE = 0.9
FURNITURE_CONFIDENCE = 0.9                          # block name checked against the size table (§2.8)
GENERIC_LABELS_CONFIDENCE = 0.6                     # untitled page with room names and walls (§2.1)
NO_FRONT_TYPES = ("table_dining", "table_coffee")   # nothing drawn says which side is the front


def _m(v: float) -> float:
    return round(v * INCH_M, 6) + 0.0


def _mp(p) -> list[float]:
    return [_m(p[0]), _m(p[1])]


def cad_ids(project: CadProject) -> dict:
    """Truth ids in drawing order: walls, doors, windows, furniture (DINING-6 = table + its six chairs), rooms per
    label and the separators."""
    plan = project.plan
    ids = B.IdCounter()
    n_pieces = sum(1 + (len(blocks.CAD_DINING_CHAIRS) if p.block == "DINING-6" else 0) for p in plan.furniture)
    rooms = B.IdCounter()
    return {
        "walls": [ids.next("wall", "L0") for _ in plan.walls],
        "doors": [ids.next("door", "L0") for _ in plan.doors],
        "windows": [ids.next("window", "L0") for _ in plan.windows],
        "separators": [ids.next("opening", "L0") for _ in plan.separators],
        "furniture": [ids.next("furniture", "L0") for _ in range(n_pieces)],
        "rooms": [rooms.room("L0", B.normalise_room_label(label.lines[0])[0]) for label in plan.labels],
    }


def _label_anchor(label) -> tuple[float, float]:
    """Centre of the name line's box (building inches), the point that must lie in the room's face."""
    at = label.at
    if label.kind == "mtext":
        at = (at[0], at[1] - label.height)            # top left -> baseline of the first line
    x0, y0, x1, y1 = cad_text_box(at, label.lines[0], label.height)
    return ((x0 + x1) / 2.0, (y0 + y1) / 2.0)


def cad_faces(project: CadProject) -> list[dict]:
    """The room faces: holes of the wall union with each separator's gap band (the stub's band extended to the face
    it meets) bridged, one label inside each. Raises ValueError for a face without exactly one label, a label in
    no face, or open outer walls."""
    plan = project.plan
    bands = [Polygon(w.rectangle()) for w in plan.walls]
    for sep in plan.separators:
        stub = plan.walls[sep.wall]
        bands.append(Polygon(G.centerline_to_rectangle(sep.start, sep.end, stub.thickness)))
    union = unary_union(bands)
    if union.geom_type != "Polygon":
        raise ValueError(f"{project.name}: walls are not one closed loop ({union.geom_type})")
    faces = sorted((canonical_ring(r.coords) for r in union.interiors), key=lambda r: (r[0][1], r[0][0]))
    used = set()
    out = []
    for ring in faces:
        shp = Polygon(ring)
        inside = [i for i, lab in enumerate(plan.labels) if shp.contains(ShapelyPoint(_label_anchor(lab)))]
        if len(inside) != 1:
            raise ValueError(f"{project.name}: face at {ring[0]} holds {len(inside)} labels")
        used.add(inside[0])
        out.append({"ring": ring, "label": inside[0]})
    missing = set(range(len(plan.labels))) - used
    if missing:
        raise ValueError(f"{project.name}: labels outside every face: {sorted(missing)}")
    return out


def _parse_size_pair(text: str) -> tuple[float, float]:
    """``14'-0" X 12'-0"`` -> (168, 144) inches (the generator's own reader: the truth must not depend on the
    parser under test)."""
    sides = []
    for part in text.upper().split("X"):
        feet, inches = part.strip().rstrip('"').split("'-")
        sides.append(int(feet) * 12 + float(inches))
    return sides[0], sides[1]


def build_cad_truth(project: CadProject, record: PageRecord, *, document: str, fmt: str, title: Optional[str],
                    converter: Optional[str]) -> dict:
    """The building JSON the pipeline must reproduce from synthetic-06 (or its titled fixture)."""
    plan = project.plan
    ids = cad_ids(project)
    building = B.empty_building(project.name if not title else project.titled_fixture,
                                f"projects/{project.name}" if not title else f"tests/fixtures/{project.titled_fixture}",
                                PIPELINE_COMMIT, created_utc=CREATED_UTC, brief=project.brief if not title else None)
    building["project"]["unit_system"] = "imperial"
    ox, oy = plan.origin

    def ev(method, confidence, **kw):
        return B.evidence(document, method, confidence, **kw)

    label_evidence = []
    rooms_by_label = {}
    faces = cad_faces(project)
    wall_polys = [Polygon(w.rectangle()) for w in plan.walls]
    room_ids = ids["rooms"]
    sep_ids = ids["separators"]
    furniture_parts = [s for s in record.symbols if s["type"] not in ("door", "window")]
    for face in faces:
        label = plan.labels[face["label"]]
        rid = room_ids[face["label"]]
        rooms_by_label[label.lines[0]] = rid
        name_entry = next(t for t in record.texts if t.get("element_id") == rid and t["role"] == "room_label")
        block = blocks.CAD_ROOMTAG if label.kind == "roomtag" else None
        text_ev = ev("vector", 1.0, layer=blocks.CAD_LAYER_ANNOTATION, entity=name_entry["entity"], block=block,
                     text=label.lines[0])
        label_evidence.append(text_ev)
        face["text_ev"] = text_ev
    level_evidence = ([ev("vector", 1.0, layer=blocks.CAD_LAYER_ANNOTATION, entity=record.title_entity, text=title)]
                      if title else list(label_evidence))
    label, order = project.titled_level if title else (ASSUMED_LEVEL_LABEL, 0)

    # Documents and the level.
    page = {"page": 1, "class": "floor_plan", "skip_reason": None, "kind": "vector", "level_id": "L0",
            "level_label_raw": title, "classifier": "title" if title else "generic_labels",
            "scale": {"metres_per_unit": INCH_M, "method": "dxf_insunits", "confidence": 1.0,
                      "evidence": ev("vector", 1.0, entity="$INSUNITS=1")},
            "transform_to_building": [INCH_M, 0.0, -_m(ox), 0.0, INCH_M, -_m(oy)],
            "confidence": 1.0 if title else GENERIC_LABELS_CONFIDENCE, "evidence": level_evidence,
            "debug_image": None}
    building["documents"].append({"id": "doc_" + B.slugify(document), "file": document, "format": fmt,
                                  "converter": converter, "unit_system": "imperial", "source_kind": "dxf",
                                  "pages": [page]})
    building["levels"].append({"id": "L0", "label": label, "order": order, "elevation": 0.0,
                               "ceiling_height": plan.ceiling_height, "ceiling_height_source": "assumed_default",
                               "label_source": "title" if title else "assumed", "evidence": level_evidence})
    building["warnings"].append(f"Level L0: ceiling height assumed {plan.ceiling_height:.2f} m "
                                "(no section drawing found)")
    if not title:
        building["warnings"].append(f"level title missing: assumed L0 {ASSUMED_LEVEL_LABEL}")

    # Walls (exterior = touching the outer face).
    outer = Polygon(canonical_ring(unary_union(wall_polys).exterior.coords))
    hatch = record.entities[ids["walls"][0]]
    for wall, wid, poly in zip(plan.walls, ids["walls"], wall_polys):
        assert wall.exterior == (poly.exterior.distance(outer.exterior) < 1e-6 and
                                 poly.intersection(outer.exterior).length > 0), wid
        building["walls"].append({
            "id": wid, "level_id": "L0", "start": _mp(wall.start), "end": _mp(wall.end),
            "thickness": _m(wall.thickness), "height": plan.ceiling_height, "exterior": wall.exterior,
            "status": "verified",
            "evidence": [ev("vector", WALL_CONFIDENCE, layer=blocks.CAD_LAYER_WALLS, entity=hatch)]})

    # Openings: doors, windows, the virtual separator of the open plan.
    for door, did in zip(plan.doors, ids["doors"]):
        building["openings"].append({
            "id": did, "type": "door", "level_id": "L0", "wall_id": ids["walls"][door.wall],
            "center": _mp(door.center(plan.walls)), "width": _m(door.width), "height": DOOR_HEIGHT_M,
            "sill_height": None, "assumed": ["height"], "swing_side": rooms_by_label[door.into], "status": "verified",
            "evidence": [ev("vector", DOOR_CONFIDENCE, layer=blocks.CAD_LAYER_DOORS, entity=record.entities[did])]})
    for window, wid in zip(plan.windows, ids["windows"]):
        building["openings"].append({
            "id": wid, "type": "window", "level_id": "L0", "wall_id": ids["walls"][window.wall],
            "center": _mp(window.center), "width": _m(window.width), "height": WINDOW_HEIGHT_M,
            "sill_height": WINDOW_SILL_M, "assumed": ["height", "sill_height"], "swing_side": None,
            "status": "verified",
            "evidence": [ev("vector", WINDOW_CONFIDENCE, layer=blocks.CAD_LAYER_GLAZING, entity=record.entities[wid])]})
    for sep, oid in zip(plan.separators, sep_ids):
        center = ((sep.start[0] + sep.end[0]) / 2.0, (sep.start[1] + sep.end[1]) / 2.0)
        building["openings"].append({
            "id": oid, "type": "opening", "level_id": "L0", "wall_id": None, "virtual": True,
            "line": [_mp(sep.start), _mp(sep.end)], "center": _mp(center), "width": _m(G.distance(sep.start, sep.end)),
            "height": None, "sill_height": None, "swing_side": None, "status": "verified",
            "evidence": [ev("derived", 1.0, entity="derived-from:" + ids["walls"][sep.wall])]})

    # Rooms.
    sep_polys = [(oid, Polygon(G.centerline_to_rectangle(sep.start, sep.end, plan.walls[sep.wall].thickness)))
                 for sep, oid in zip(plan.separators, sep_ids)]
    piece_rooms = {}
    for face in faces:
        label = plan.labels[face["label"]]
        rid = room_ids[face["label"]]
        shp = Polygon(face["ring"])
        for part in furniture_parts:
            center = ((part["box"][0] + part["box"][2]) / 2.0 - ox, (part["box"][1] + part["box"][3]) / 2.0 - oy)
            if shp.contains(ShapelyPoint(center)):
                piece_rooms[part["id"]] = rid
        touching = [wid for wid, poly in zip(ids["walls"], wall_polys) if poly.distance(shp) < 1e-6]
        touching += [oid for oid, poly in sep_polys if poly.distance(shp) < 1e-6]
        name, room_type, area_label = B.normalise_room_label(label.lines[0])
        polygon = [_mp(p) for p in face["ring"]]
        room = {"id": rid, "level_id": "L0", "label": name, "label_raw": label.lines[0], "room_type": room_type,
                "polygon": polygon, "area_computed": round(G.polygon_area(polygon), 3), "area_label": area_label,
                "has_documented_furniture": False, "style_override": None, "status": "verified",
                "evidence": [face["text_ev"], ev("derived", 1.0, entity="derived-from:" + ",".join(touching))]}
        if len(label.lines) > 1:
            w_in, l_in = _parse_size_pair(label.lines[1])
            x0, y0, x1, y1 = G.bbox(face["ring"])
            measured = [_m(x1 - x0), _m(y1 - y0)]
            ok = all(abs(a - _m(b)) <= max(0.05 * _m(b), 0.15) for a, b in zip(measured, (w_in, l_in)))
            room["label_size"] = {"text": label.lines[1], "width_m": _m(w_in), "length_m": _m(l_in),
                                  "measured": measured, "status": "ok" if ok else "conflict"}
        building["rooms"].append(room)

    # Furniture: block-name typed pieces (the table has no drawn front).
    rooms_by_id = {r["id"]: r for r in building["rooms"]}
    for part in furniture_parts:
        fid = part["id"]
        rid = piece_rooms[fid]
        rooms_by_id[rid]["has_documented_furniture"] = True
        name = part["block"].split("/")[-1]
        _, width, depth = blocks.CAD_BLOCKS[name]
        x0, y0, x1, y1 = part["box"]
        building["furniture"].append({
            "id": fid, "level_id": "L0", "room_id": rid, "type": part["type"], "type_raw": part["block"],
            "type_method": "block_name", "source": "from_documents",
            "footprint": {"center": [_m((x0 + x1) / 2.0 - ox), _m((y0 + y1) / 2.0 - oy)],
                          "size": [_m(width), _m(depth)], "rotation_deg": part["rotation_deg"]},
            "front_deg": None if part["type"] in NO_FRONT_TYPES else G.front_direction_deg(part["rotation_deg"]),
            "height": None, "asset": None, "status": "verified",
            "evidence": [ev("vector", FURNITURE_CONFIDENCE, layer=blocks.CAD_LAYER_FURNITURE, entity=part["entity"],
                            block=part["block"])]})
    B.validate(building)
    return building


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_cad_documents(project: CadProject, project_dir: Path) -> tuple[PageRecord, Optional[str]]:
    """Source DXF, then the DWG by ``dxf2dwg``. Returns ``(record, note)``; ``note`` says why no DWG was written."""
    record = write_cad_dxf(project, project_dir / project.source_dxf, project.dwg, ids=cad_ids(project))
    if dwg_tool.find_tool("dxf2dwg") is None:
        return record, f"{project.name}: {project.dwg} not written (LibreDWG dxf2dwg not found; scripts/cloud-setup.sh)"
    dwg_path = dwg_tool.dxf_to_dwg(project_dir / project.source_dxf, project_dir / project.dwg)
    sha = _sha256(dwg_path)
    if sha != project.dwg_sha256:
        version = dwg_tool.libredwg_version(dwg_tool.find_tool("dxf2dwg"))
        raise ValueError(f"{project.name}: {project.dwg} has sha256 {sha}, expected {project.dwg_sha256} "
                         f"(LibreDWG {version}); a changed source DXF needs DWG_SHA256_06 updated in "
                         "wenart/synthetic/projects.py, another LibreDWG build needs the pinned 0.14 d9468ae")
    return record, None


def generate_cad_project(project: CadProject, out_root: Path, results_dir: Optional[Path] = None,
                         fixtures_root: Optional[Path] = None) -> dict:
    """synthetic-06: documents, brief, truth, preview and (with ``fixtures_root``) the titled fixture."""
    project_dir = Path(out_root) / project.name
    (project_dir / "truth").mkdir(parents=True, exist_ok=True)
    record, note = write_cad_documents(project, project_dir)
    if note:
        print(note, file=sys.stderr)
    if project.brief is not None:
        (project_dir / "brief.yaml").write_text(yaml.safe_dump(project.brief, allow_unicode=True, sort_keys=False),
                                                encoding="utf-8")
    converter = f"libredwg dwg2dxf {dwg_tool.LIBREDWG_TAG} {dwg_tool.LIBREDWG_COMMIT[:7]}"
    truth = build_cad_truth(project, record, document=project.dwg, fmt="dwg", title=None, converter=converter)
    B.save(truth, project_dir / "truth" / "building.json")
    (project_dir / "truth" / "pages.json").write_text(
        json.dumps(build_pages([(None, record)]), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if results_dir is not None:
        preview_from_dxf(project_dir / project.source_dxf,
                         Path(results_dir) / f"{project.name}_{Path(project.dwg).stem}_p1.jpg")
    if fixtures_root is not None:
        generate_titled_fixture(project, Path(fixtures_root))
    return truth


def generate_titled_fixture(project: CadProject, fixtures_root: Path) -> dict:
    """The titled variant of synthetic-06 as a one-DXF project: ``<root>/<titled_fixture>/<titled_fixture>.dxf``
    and its truth (level from the title)."""
    folder = Path(fixtures_root) / project.titled_fixture
    (folder / "truth").mkdir(parents=True, exist_ok=True)
    document = f"{project.titled_fixture}.dxf"
    record = write_cad_dxf(project, folder / document, document, title=project.titled_title, ids=cad_ids(project))
    truth = build_cad_truth(project, record, document=document, fmt="dxf", title=project.titled_title,
                            converter=None)
    B.save(truth, folder / "truth" / "building.json")
    return truth


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------

def write_previews(project: Project, pages: list[tuple[object, PageRecord]], project_dir: Path, results_dir: Path) -> list[Path]:
    written = []
    for doc, rec in pages:
        if isinstance(doc, PdfDoc) and doc.hidden:
            continue
        stem = Path(rec.file).stem
        out = results_dir / f"{project.name}_{stem}_p{rec.page}.jpg"
        src = project_dir / rec.file
        if isinstance(doc, DxfDoc):
            preview_from_dxf(src, out)
        elif isinstance(doc, PdfDoc):
            preview_from_pdf(src, rec.page, out)
        else:
            preview_from_image(src, out)
        written.append(out)
    return written


def write_style_photos(project: Project, project_dir: Path) -> list[Path]:
    """Copy the project's style photos into ``<project_dir>/style_photos/`` (none: nothing written)."""
    written = []
    for name, src in project.style_photo_sources().items():
        dst = project_dir / PHOTO_DIR / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        written.append(dst)
    return written


def generate_project(project, out_root: Path, results_dir: Optional[Path] = None,
                     fixtures_root: Optional[Path] = None) -> dict:
    """Write one project (documents, brief, style photos, truth; previews into ``results_dir``). For synthetic-06
    ``fixtures_root`` also receives the titled variant."""
    if isinstance(project, CadProject):
        return generate_cad_project(project, out_root, results_dir, fixtures_root)
    project_dir = Path(out_root) / project.name
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "truth").mkdir(exist_ok=True)
    pages = write_documents(project, project_dir)
    if project.brief is not None:
        (project_dir / "brief.yaml").write_text(yaml.safe_dump(project.brief, allow_unicode=True, sort_keys=False),
                                                encoding="utf-8")
    write_style_photos(project, project_dir)
    truth = build_truth(project, pages)
    B.save(truth, project_dir / "truth" / "building.json")
    (project_dir / "truth" / "pages.json").write_text(
        json.dumps(build_pages(pages), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if results_dir is not None:
        write_previews(project, pages, project_dir, Path(results_dir))
    return truth


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Generate the synthetic test projects.")
    parser.add_argument("--out", default="projects", help="projects root (default: projects)")
    parser.add_argument("--results", default=str(DEFAULT_RESULTS), help="preview JPEG folder ('' to skip)")
    parser.add_argument("--only", default=None, help="generate one project by name")
    parser.add_argument("--fixtures", default=None,
                        help="root for the synthetic-06 titled fixture ('' to skip; default: tests/fixtures when "
                             "--out is the repository's projects folder)")
    args = parser.parse_args(argv)
    results = Path(args.results) if args.results else None
    if args.fixtures is None:
        fixtures = DEFAULT_FIXTURES if Path(args.out).resolve() == (REPO_ROOT / "projects").resolve() else None
    else:
        fixtures = Path(args.fixtures) if args.fixtures else None
    for project in all_projects():
        if args.only and project.name != args.only:
            continue
        truth = generate_project(project, Path(args.out), results, fixtures)
        print(f"{project.name}: {len(truth['levels'])} levels, {len(truth['walls'])} walls, "
              f"{len(truth['openings'])} openings, {len(truth['rooms'])} rooms, {len(truth['furniture'])} furniture, "
              f"{len(truth['conflicts'])} conflicts, {len(truth['unverified'])} unverified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
