"""Synthetic test projects with known ground truth (docs/milestone2.md §1).

``python -m wenart.synthetic.generate --out projects`` writes
``projects/synthetic-01..03`` with documents (DXF, vector PDF, scan PNG, photo
JPEG), ``brief.yaml`` and ``truth/`` (``building.json``, ``pages.json``).
Module map: ``blocks`` (block table), ``model`` (level model + derivations),
``projects`` (the three layouts), ``dxf_writer``, ``pdf_writer``, ``raster``,
``generate`` (orchestration and truth assembly).
"""
