"""Vector path: documents -> building JSON with evidence (docs/milestone2.md §2).

Module map:
- ``model``: the dataclasses that the extractors fill (``LevelExtraction`` and
  its items) plus small text helpers (roles, scale text, numbers).
- ``classify``: one ``PageRecord`` per file/page: kind (vector/scan/photo),
  class (floor_plan, furniture_plan, ...), level, scale, with evidence.
- ``dwg``: DWG -> DXF through LibreDWG ``dwg2dxf`` or ``ezdwg``; audited with ezdxf.
- ``dxf_extract``: DXF model space -> walls, openings, labels, furniture, dimensions.
- ``pdf_extract``: vector PDF page (pdfplumber) -> the same, by geometry.
- ``rooms``: wall rectangles -> shapely union -> room polygons; labels -> rooms.
- ``debug_image``: page raster with the recognised elements drawn over it.
- ``pipeline``: orchestration, cross-checks, conflicts, report, ``building.json``.

CLI: ``python -m wenart.ingest.pipeline projects/synthetic-01 --out outputs/synthetic-01``.
"""
