"""Generate the synthetic projects and their ground truth.

CLI::

    python -m wenart.synthetic.generate --out projects [--results results/synthetic] [--only synthetic-02]

Deterministic and idempotent: fixed seeds, fixed PDF/DXF metadata, files are
overwritten in place. Two runs give identical truth JSON and identical
document bytes (checked in tests/test_synthetic.py).

Truth assembly rules (what the pipeline is expected to reproduce):
- Elements get one evidence entry per page that shows them. Vector pages give
  ``method: vector`` with the DXF handle or PDF path/char index; raster pages
  give a ``pixel_box`` with ``method: ai`` (geometry, symbols) or ``ocr``
  (texts), because that is how a pipeline would read a scan or photo.
- Heights, sill heights and furniture heights are ``null``: the documents do
  not show them. Ceiling height is the assumed default with a warning.
- Furniture from unknown blocks (``BLOK_A``) is ``unknown`` + ``unverified``
  and listed in ``unverified``.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

import yaml

from wenart import building as B
from wenart import geometry as G
from wenart.synthetic import blocks
from wenart.synthetic.dxf_writer import write_dxf
from wenart.synthetic.model import Level, PageRecord
from wenart.synthetic.pdf_writer import PAGE_H, write_pdf
from wenart.synthetic.projects import DxfDoc, PdfDoc, Project, RasterDoc, all_projects
from wenart.synthetic.raster import SCAN_DPI, make_photo, make_scan, preview_from_dxf, preview_from_image, preview_from_pdf

CREATED_UTC = "2026-10-01T00:00:00Z"
PIPELINE_COMMIT = "synthetic-generator"
DEFAULT_RESULTS = Path("results/synthetic")


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
    method = "ocr" if kind == "text" else "ai"
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
    else:
        ev = B.evidence(rec.file, "ocr", 1.0, pixel_box=scale_text["box"], dpi=rec.dpi, text=level.scale_text)
    return {"metres_per_unit": rec.scale_metres_per_unit, "method": "pdf_scale_text", "confidence": 1.0, "evidence": ev}


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
        for piece in level.furniture:
            building["furniture"].append({
                "id": piece.id, "level_id": level.id, "room_id": piece.room_id, "type": piece.type,
                "type_raw": piece.block, "source": "from_documents",
                "footprint": {"center": list(piece.center), "size": list(piece.size), "rotation_deg": piece.rotation_deg},
                "front_deg": piece.front_deg() if piece.status == "verified" else None,
                "height": None, "asset": None, "status": piece.status,
                "evidence": evidence_list(piece.id, "furniture", block=piece.block),
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


def generate_project(project: Project, out_root: Path, results_dir: Optional[Path] = None) -> dict:
    project_dir = Path(out_root) / project.name
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "truth").mkdir(exist_ok=True)
    pages = write_documents(project, project_dir)
    if project.brief is not None:
        (project_dir / "brief.yaml").write_text(yaml.safe_dump(project.brief, allow_unicode=True, sort_keys=False),
                                                encoding="utf-8")
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
    args = parser.parse_args(argv)
    results = Path(args.results) if args.results else None
    for project in all_projects():
        if args.only and project.name != args.only:
            continue
        truth = generate_project(project, Path(args.out), results)
        print(f"{project.name}: {len(truth['levels'])} levels, {len(truth['walls'])} walls, "
              f"{len(truth['openings'])} openings, {len(truth['rooms'])} rooms, {len(truth['furniture'])} furniture, "
              f"{len(truth['conflicts'])} conflicts, {len(truth['unverified'])} unverified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
