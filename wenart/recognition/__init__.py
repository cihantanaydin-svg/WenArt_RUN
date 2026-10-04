"""Raster path of Milestone 2: OCR and vision-language models on scans and photos.

Modules (docs/milestone2.md, section 3):

- ``schemas``: strict JSON schemas for the model answers (page class, text
  items, symbols, room labels) and a validator.
- ``prompts``: one prompt per task, Turkish plan vocabulary explained in English.
- ``vlm_client``: OpenAI-compatible client for a local vLLM server with
  structured output (``structured_outputs.json``), temperature 0, seed 0.
- ``ocr``: PaddleOCR (GPU) and Tesseract (CPU) with one normalised output shape.
- ``detect``: two-pass symbol agreement between two models.
- ``metrics``: scores against the synthetic ground truth and a markdown summary.
- ``bakeoff``: the CLI that runs everything over the synthetic raster pages.

Milestone 7 (docs/milestone7.md §1.4, §3):

- ``crops``: deterministic context/iso crops of a furniture candidate and the canonical input hash.
- ``symbols``: the symbol-type question and the two-pass decision rule.
- ``answers``: recognition requests, the answer store and the ``ask`` / ``status`` CLI.
- ``room_labels``: raster room labels, accepted by two-pass or Tesseract equality.
- ``size_table.yaml``: plausible footprint ranges per furniture type (read by the generic core too).

The heavy dependencies (paddleocr, PIL for image encoding) are imported lazily
inside functions so the CPU tests import every module without them.
"""
