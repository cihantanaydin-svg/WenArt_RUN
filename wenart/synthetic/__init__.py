"""Synthetic test projects with known ground truth (docs/milestone2.md §1, docs/milestone6.md §3).

``python -m wenart.synthetic.generate --out projects`` writes
``projects/synthetic-01..05`` with documents (DXF, vector PDF, scan PNG, photo
JPEG), ``brief.yaml``, style photos (synthetic-05) and ``truth/``
(``building.json``, ``pages.json``). Module map: ``blocks`` (block table),
``model`` (level model + derivations, outline builder), ``projects`` (the
layouts), ``dxf_writer``, ``pdf_writer``, ``raster``, ``generate``
(orchestration and truth assembly); synthetic-07 (Milestone 10, one CAD sheet
with every drawing kind): ``sheet`` (layout), ``sheet_writer`` (DXF),
``sheet_truth`` (truth files). See docs/synthetic.md.
"""
