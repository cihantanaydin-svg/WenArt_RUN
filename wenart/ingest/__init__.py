"""Vector path: documents -> building JSON with evidence (docs/milestone2.md §2).

Module map:
- ``model``: the dataclasses that the extractors fill (``LevelExtraction`` and
  its items) plus small text helpers (roles, scale text, numbers).
- ``classify``: one ``PageRecord`` per file/page: kind (vector/scan/photo),
  class (floor_plan, furniture_plan, ...), level, scale, with evidence.
- ``dwg``: DWG -> DXF through LibreDWG 0.14 ``dwg2dxf`` (no ezdwg); audited with ezdxf (docs/milestone7.md §5.1).
- ``dxf_extract``: DXF model space -> walls, openings, labels, furniture, dimensions
  (the synthetic layer convention).
- ``pdf_extract``: vector PDF page (pdfplumber) -> the same, by geometry (the synthetic convention).
- ``cad_pdf`` / ``dxf_generic``: any vector PDF page / DXF -> the adapter-neutral ``generic.model.GenericPage``
  (docs/milestone7.md §1.2, §2.2, §5.2).
- ``generic``: the generic plan core (Milestone 7): labels and scale (metric or imperial, ``wenart.units``),
  walls, openings, topology (plot, faces, separators), furniture symbols; ``core.extract`` -> ``LevelExtraction``.
- ``rooms``: wall rectangles -> shapely union -> room polygons; labels -> rooms.
- ``debug_image``: page raster with the recognised elements drawn over it.
- ``pipeline``: orchestration, cross-checks, conflicts, report, ``building.json``.

CLI: ``python -m wenart.ingest.pipeline projects/synthetic-01 --out outputs/synthetic-01``.
"""
