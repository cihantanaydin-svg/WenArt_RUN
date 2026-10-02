"""Synthetic test projects with known ground truth (docs/milestone2.md §1, docs/milestone6.md §3).

``python -m wenart.synthetic.generate --out projects`` writes
``projects/synthetic-01..05`` with documents (DXF, vector PDF, scan PNG, photo
JPEG), ``brief.yaml``, style photos (synthetic-05) and ``truth/``
(``building.json``, ``pages.json``). Module map: ``blocks`` (block table),
``model`` (level model + derivations, outline builder), ``projects`` (the five
layouts), ``dxf_writer``, ``pdf_writer``, ``raster``, ``generate``
(orchestration and truth assembly). See docs/synthetic.md.
"""
