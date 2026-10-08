"""Read every document of a project folder into sheets (docs/milestone10.md §3.1 item 1).

What: ``read_documents(project_dir, work_dir) -> list[DocRead]``: one ``DocRead`` per document file with its
sheets (DXF/DWG: the model space and every paper-space layout with entities; PDF: one sheet per page; image: one
sheet), the ``$INSUNITS`` code of a DXF, the converter of a DWG, and why a document could not be read.

Why: the split, the unit check and the classification need the drawn entities of each sheet in source units; the
generic core's adapters already read them (``wenart.ingest.dxf_generic``, ``wenart.ingest.cad_pdf``), so the same
strokes and texts are used here and later by the pipeline (a DXF is parsed once per process, ``dxf_generic`` keeps
it).

How: the documents are those of ``wenart.ingest.classify.project_documents`` (top level, known formats, sorted). A
DWG with a DXF of the same stem is skipped (the DXF wins, as in the classifier); another DWG is converted by
``wenart.ingest.dwg.convert`` into ``work_dir``. A PDF page with paths and a text layer is a vector sheet; a PDF
page without paths, or an image, is a raster sheet (one region, classified later by the pipeline's OCR, M7). A
paper-space layout is listed as a sheet without entities (its viewports show model space, which is read there).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from wenart.sheets.model import Sheet, entities_from_page


@dataclass
class DocRead:
    file: str                                 # project-relative path
    path: Path                                # the file read (the converted DXF for a DWG)
    format: str                               # dwg | dxf | pdf | image
    converter: Optional[str] = None
    conversion: Optional[dict] = None
    insunits: Optional[int] = None
    sheets: list[Sheet] = field(default_factory=list)
    skip_reason: Optional[str] = None
    warnings: list[str] = field(default_factory=list)
    layouts: list[dict] = field(default_factory=list)
    hidden: list[dict] = field(default_factory=list)   # not drawn (layer off or frozen): {id, type, layer, box}


def read_documents(project_dir: Path, work_dir: Optional[Path]) -> list[DocRead]:
    from wenart.ingest import classify as C

    out = []
    for path in C.project_documents(project_dir):
        file_rel = path.relative_to(project_dir).as_posix()
        fmt = C.document_format(path.name)
        if fmt == "dwg":
            out.append(_read_dwg(file_rel, path, work_dir))
        elif fmt == "dxf":
            out.append(_read_dxf(file_rel, path, "dxf"))
        elif fmt == "pdf":
            out.append(_read_pdf(file_rel, path))
        else:
            out.append(_read_image(file_rel, path))
    return out


def _read_dwg(file_rel: str, path: Path, work_dir: Optional[Path]) -> DocRead:
    from wenart.ingest import classify as C
    from wenart.ingest import dwg as dwg_mod

    if C.same_stem_dxf(path) is not None:
        return DocRead(file=file_rel, path=path, format="dwg", skip_reason=C.SAME_STEM_REASON)
    if work_dir is None:
        return DocRead(file=file_rel, path=path, format="dwg", skip_reason="DWG conversion needs a work folder")
    try:
        conversion = dwg_mod.convert(path, work_dir)
    except (dwg_mod.ConverterNotFound, dwg_mod.ConversionError, FileNotFoundError) as exc:
        return DocRead(file=file_rel, path=path, format="dwg", skip_reason=f"DWG conversion failed: {exc}")
    doc = _read_dxf(file_rel, conversion.dxf_path, "dwg")
    doc.converter = conversion.converter
    doc.conversion = conversion.to_json()
    return doc


def _read_dxf(file_rel: str, path: Path, fmt: str) -> DocRead:
    from wenart.ingest import dxf_generic

    page, info = dxf_generic.read_page_info(path, file_rel)
    doc = DocRead(file=file_rel, path=Path(path), format=fmt, insunits=info.get("insunits"),
                  layouts=list(info.get("layouts") or []), hidden=list(info.get("hidden") or []))
    ents, texts = entities_from_page(page, file_rel)
    doc.sheets.append(Sheet(id="s1", space="model", file=file_rel, page=1, ents=ents, texts=texts,
                            generic_page=page))
    for k, layout in enumerate(doc.layouts, start=2):
        doc.warnings.append(f"{file_rel}: paper-space layout {layout['name']!r} holds {layout['entities']} entities; "
                            f"its viewports show model space, which is read there; the layout itself is not split")
        doc.sheets.append(Sheet(id=f"s{k}", space=f"layout:{layout['name']}", file=file_rel, page=1))
    return doc


def _read_pdf(file_rel: str, path: Path) -> DocRead:
    import pdfplumber

    from wenart.ingest import cad_pdf
    from wenart.ingest.classify import _large_image

    doc = DocRead(file=file_rel, path=Path(path), format="pdf")
    with pdfplumber.open(str(path)) as pdf:
        for number, pdf_page in enumerate(pdf.pages, start=1):
            has_paths = bool(pdf_page.curves or pdf_page.lines or pdf_page.rects)
            sheet = Sheet(id=f"s{number}", space=f"page:{number}", file=file_rel, page=number)
            if has_paths and pdf_page.chars:
                page = cad_pdf.page_from_pdfplumber(pdf_page, number, file_rel)
                sheet.ents, sheet.texts = entities_from_page(page, file_rel)
                sheet.generic_page = page
            elif has_paths and not _large_image(pdf_page):
                # Text drawn as geometry (SHX fonts): the paths are split, the texts need OCR (classifier).
                page = cad_pdf.page_from_pdfplumber(pdf_page, number, file_rel)
                sheet.ents, sheet.texts = entities_from_page(page, file_rel)
                sheet.generic_page = page
            else:
                sheet.raster = True
                sheet.size = (float(pdf_page.width), float(pdf_page.height))
            doc.sheets.append(sheet)
    return doc


def _read_image(file_rel: str, path: Path) -> DocRead:
    from PIL import Image

    doc = DocRead(file=file_rel, path=Path(path), format="image")
    try:
        with Image.open(path) as im:
            size = (float(im.width), float(im.height))
    except OSError as exc:
        doc.skip_reason = f"image not readable: {exc}"
        return doc
    doc.sheets.append(Sheet(id="s1", space="page:1", file=file_rel, page=1, raster=True, size=size))
    return doc
