"""The ``sheets`` stage (docs/milestone10.md §1.2, §1.6a, §3.1): what is drawn on every sheet of a project.

What: ``analyse(project_dir, out_dir, answers=None, no_ai=False) -> dict`` splits every sheet into drawing regions,
checks the drawing unit of each CAD document, classifies the regions (title, geometry, then the AI passes as
evidence), gives the plans their levels and variants, registers them into one building frame, reads the heights
from the section and the exterior evidence, and writes ``<out>/sheets.json`` (``wenart/schema/sheets.schema.json``,
validated before writing), ``<out>/sheets_report.md``, ``<out>/sheets_debug/<file>_<sheet>.png`` and the
``sheet_region`` questions (``<out>/sheets/requests.json``, crops in ``<out>/sheets/crops/``). ``run`` returns the
same with what the CLI needs for its exit code (questions without answers, needs review).

Why: real02 holds four plans and a section on one sheet, drawn in centimetres under a millimetre header; the
pipeline must read each plan on its own, at the right scale, in one frame, with heights from the section.

How: ``read`` -> ``split`` -> ``units_check`` -> ``classify`` -> ``question`` (merge) -> ``levels`` ->
``variants`` -> ``register`` -> ``heights`` -> ``exterior`` -> ``debug`` / ``report``. Regions are numbered
``r<n>`` per document in reading order. Raster pages (images, scanned PDF pages) are one region each, left to the
pipeline's OCR classification (M7). The brief is read through ``wenart.brief.load_brief`` (``variants``,
``ceiling_height``, ``slab_thickness``, ``failed_levels``).
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from wenart.sheets.model import Region, round_box

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schema" / "sheets.schema.json"
SHEETS_JSON = "sheets.json"
REPORT_MD = "sheets_report.md"
DEBUG_DIR = "sheets_debug"
QUESTIONS_DIR = "sheets"
NO_PLAN_REASON = "no readable plan region"


@dataclass
class Result:
    doc: dict
    pending: list[str] = field(default_factory=list)       # question keys without a complete pair of answers
    questions: int = 0
    review: list[str] = field(default_factory=list)
    regions: list = field(default_factory=list)            # Region objects (in-process use by the pipeline)


def analyse(project_dir, out_dir, answers=None, no_ai: bool = False) -> dict:
    """Analyse a project's sheets and write the outputs; returns the ``sheets.json`` document."""
    return run(project_dir, out_dir, answers=answers, no_ai=no_ai).doc


def _commit() -> str:
    from wenart.ingest.pipeline import pipeline_commit
    return pipeline_commit()


def file_fingerprint(path: Path) -> dict:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return {"size": path.stat().st_size, "sha256": h.hexdigest()}


def inputs_of(project_dir: Path) -> list[dict]:
    """The documents and the brief a ``sheets.json`` was made from (the pipeline re-runs the stage when they
    changed)."""
    from wenart.ingest.classify import project_documents

    project_dir = Path(project_dir)
    files = list(project_documents(project_dir))
    brief = project_dir / "brief.yaml"
    if brief.is_file():
        files.append(brief)
    return [{"file": p.relative_to(project_dir).as_posix(), **file_fingerprint(p)} for p in files]


def run(project_dir, out_dir, answers=None, no_ai: bool = False, work_dir=None, debug: bool = True,
        questions: bool = True) -> Result:
    from wenart import brief as BR
    from wenart.recognition import answers as A
    from wenart.sheets import classify as CL
    from wenart.sheets import exterior as EX
    from wenart.sheets import heights as HT
    from wenart.sheets import levels as LV
    from wenart.sheets import question as Q
    from wenart.sheets import read as RD
    from wenart.sheets import register as RG
    from wenart.sheets import report as RP
    from wenart.sheets import split as SP
    from wenart.sheets import units_check as UC
    from wenart.sheets import variants as VR

    project_dir = Path(project_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    brief = BR.load_brief(project_dir)
    values = brief["values"]
    conflicts: list[dict] = []
    warnings: list[str] = []
    needs_review: list[dict] = []

    def conflict(kind: str, regions: list, description: str, resolution: str) -> str:
        cid = f"sc_{len(conflicts) + 1:03d}"
        conflicts.append({"id": cid, "kind": kind, "regions": list(regions), "description": description,
                          "resolution": resolution})
        return cid

    docs = RD.read_documents(project_dir, Path(work_dir) if work_dir else out_dir / "converted")
    documents_json, regions, strays_json = [], [], []
    stray_draw: dict[tuple, list] = {}
    for doc in docs:
        units_json = {"insunits": doc.insunits, "metres_per_unit": None, "method": "none", "checks": [],
                      "conflict": None}
        entry = {"file": doc.file, "format": doc.format, "converter": doc.converter, "units": units_json,
                 "sheets": []}
        documents_json.append(entry)
        warnings.extend(doc.warnings)
        if doc.skip_reason:
            entry["skip_reason"] = doc.skip_reason
            if doc.skip_reason.startswith("DWG conversion failed"):
                needs_review.append({"region": None, "file": doc.file, "reason": f"{doc.file}: {doc.skip_reason}"})
            else:
                warnings.append(f"{doc.file}: {doc.skip_reason}")
            continue
        doc_regions: list[Region] = []
        n_doc = sum(len(s.ents) + len(s.texts) for s in doc.sheets)
        frames_all = []
        for sheet in doc.sheets:
            sheet_json = {"id": sheet.id, "space": sheet.space, "box": [0.0, 0.0, 0.0, 0.0], "frames": [],
                          "gap_units": None, "debug_image": None}
            entry["sheets"].append(sheet_json)
            if sheet.raster:
                w, h = sheet.size or (0.0, 0.0)
                sheet.box = (0.0, 0.0, w, h)
                sheet_json["box"] = round_box(sheet.box)
                r = Region(id=f"r{len(regions) + len(doc_regions) + 1}", file=doc.file, sheet=sheet, box=sheet.box,
                           geometry_box=sheet.box, kind="raster")
                r.features = {"raster": True, "note": "raster page: one region; classified and read by the "
                                                      "pipeline's OCR path (M7), not split"}
                r.use, r.ignored_reason = "ignored", "raster page: classified and read by the pipeline's OCR path"
                doc_regions.append(r)
                continue
            if not sheet.ents and not sheet.texts:
                continue
            res = SP.split_sheet(sheet, n_doc)
            sheet_json.update({"box": round_box(res.box), "frames": [{"entity": f["entity"], "box": round_box(f["box"])}
                                                                    for f in res.frames],
                               "gap_units": round(res.gap, 3)})
            frames_all.extend(res.frames)
            for c in res.clusters:
                rid = f"r{len(regions) + len(doc_regions) + 1}"         # unique in the project (§1.6b row 2)
                doc_regions.append(Region(id=rid, file=doc.file, sheet=sheet, box=c.box,
                                          geometry_box=c.geometry_box, ents=c.ents, texts=c.texts, frame=c.frame,
                                          kind=c.kind))
            for c, dist in res.strays:
                for e in c.ents:
                    strays_json.append({"file": doc.file, "sheet": sheet.id, "entity": e.id, "type": e.kind,
                                        "layer": e.layer, "box": round_box(e.box), "distance_m": dist,
                                        "reason": _stray_reason(c, n_doc, bool(res.frames))})
                    stray_draw.setdefault((doc.file, sheet.id), []).append((e.box, dist, e.id))
                for t in c.texts:
                    strays_json.append({"file": doc.file, "sheet": sheet.id, "entity": t.id, "type": t.id.split(":")[0],
                                        "layer": t.layer, "box": round_box(t.box), "distance_m": dist,
                                        "reason": _stray_reason(c, n_doc, bool(res.frames))})
            for hid in doc.hidden if sheet.space == "model" else []:
                dist = _hidden_stray(hid, res, doc_regions)
                if dist is not None:
                    strays_json.append({"file": doc.file, "sheet": sheet.id, "entity": hid["id"], "type": hid["type"],
                                        "layer": hid["layer"], "box": round_box(hid["box"]), "distance_m": dist,
                                        "reason": "far outside the frame; on a layer that is off or frozen (not drawn)"
                                        if res.frames else "far from every drawing; on a layer that is off or frozen"})
                    stray_draw.setdefault((doc.file, sheet.id), []).append((tuple(hid["box"]), dist, hid["id"]))

        # Units.
        mpu = None
        if doc.format in ("dxf", "dwg"):
            ur = UC.check_units(doc.insunits, [r for r in doc_regions if r.kind != "raster"], doc.file)
            entry["units"] = ur.to_json()
            mpu = ur.metres_per_unit
            warnings.extend(ur.warnings)
            if ur.conflict:
                entry["units"]["conflict"] = ur.conflict
                conflict("unit_mismatch", [r.id for r in doc_regions], f"{doc.file}: {ur.conflict}",
                         f"{ur.unit} used (user decision 8 of 8 Oct 2026: >= 2 independent checks agree)")
            if ur.review:
                needs_review.append({"region": None, "file": doc.file, "reason": ur.review})
        elif doc.format == "pdf":
            mpu, method = _pdf_scale(doc)
            entry["units"].update({"metres_per_unit": mpu, "method": method})
        else:
            entry["units"]["method"] = "raster"
        for r in doc_regions:
            r.metres_per_unit = mpu if r.kind != "raster" else None
        for sj in entry["sheets"]:
            if mpu is not None and sj["gap_units"] is not None:
                sj["gap_m"] = round(sj["gap_units"] * mpu, 4)
        for s in strays_json:
            if s["file"] == doc.file and isinstance(s["distance_m"], float) and not s.get("_m"):
                s["distance_m"] = round(s["distance_m"] * mpu, 2) if mpu else None
                s["_m"] = True

        # Classes: title, then geometry.
        for r in doc_regions:
            if r.kind == "raster":
                continue
            titled = CL.by_title(r)
            r.features = CL.features(r, mpu)
            if not titled:
                CL.by_geometry(r, r.features, r.sheet.frames, r.sheet.gap or 0.0)
        regions.extend(doc_regions)
    for s in strays_json:
        s.pop("_m", None)

    # AI questions and answers.
    asked = [r for r in regions if r.kind != "raster"]
    items: list[dict] = []
    pending: list[str] = []
    qdir = out_dir / QUESTIONS_DIR
    if questions and asked:
        items = Q.requests(asked, qdir)
        A.write_requests(qdir, project_dir.name, items, crop_version=Q.CROP_VERSION)
        if answers is not None:
            models = {}
            try:
                models = A.load_models()
            except OSError:
                pass
            loaded = A.load(Path(answers), items) if isinstance(answers, (str, Path)) else dict(answers)
            missing = Q.merge(asked, loaded, models, conflict, warnings)
            pending = [] if no_ai else missing
        else:
            pending = [] if no_ai else [it["key"] for it in items]
    for r in regions:
        if r.kind != "raster":
            CL.use_of(r)

    # Levels, variants, registration.
    plans = [r for r in regions if r.use == "read" and r.cls in CL.PLAN_CLASSES]
    LV.assign_levels(plans, needs_review, warnings)
    levels_json, variants_json = VR.group(plans, values.get("variants", "all"), conflict, warnings)
    read_plans = [r for r in plans if r.use == "read" and r.level is not None]
    multi = multi_region(regions)
    reference = _reference(read_plans, levels_json)
    outlines = {}
    if not multi:
        # One drawing per page (M2-M9 projects): every level keeps its own frame (the pipeline's page records).
        reference = None
    if reference is not None and reference.metres_per_unit:
        registrable = [r for r in read_plans if r.metres_per_unit]
        outlines = RG.register(registrable, reference, conflict, warnings)
        RG.stairs_check(registrable, conflict, warnings)
        _polyline_note(registrable, warnings)
    for r in read_plans:
        cad = r.sheet.generic_page is not None and r.sheet.generic_page.source_kind == "dxf"
        if not r.metres_per_unit and cad and not any(n["file"] == r.file for n in needs_review):
            # A PDF's scale comes from its dimension texts in the generic core (M7); a CAD document needs a unit.
            needs_review.append({"region": r.id, "file": r.file,
                                 "reason": f"{r.file} {r.id}: plan without a drawing unit (missing scale)"})
    if not read_plans and not any(r.kind == "raster" for r in regions):
        needs_review.append({"region": None, "file": None, "reason": NO_PLAN_REASON})

    # Heights and exterior.
    sections = [r for r in regions if r.use == "heights" and r.cls == "section"]
    section_geom = None
    if sections:
        sec = sections[0]
        section_geom = getattr(sec, "_section", None)
        if len(sections) > 1:
            warnings.append(f"{len(sections)} sections: heights from {sections[0].id}; "
                            f"{', '.join(s.id for s in sections[1:])} not read for heights")
    base_levels = [{"id": lv["id"], "order": lv["order"], "kind": lv["kind"]} for lv in levels_json]
    ref_extent = None
    if reference is not None and reference.id in outlines:
        b = outlines[reference.id].bounds
        ref_extent = (b[2] - b[0], b[3] - b[1])
    heights_json, hw = HT.heights(section_geom, base_levels, ref_extent, values,
                                  sections[0].file if sections else None, conflict)
    if multi:
        warnings.extend(hw)
    top_plan = None
    if levels_json:
        top_level = max(levels_json, key=lambda lv: lv["order"])
        top_plan = next((r for r in read_plans if r.id == top_level["base_region"]), None)
    elevations = [r for r in regions if r.cls == "elevation" and r.use == "exterior"]
    sites = [r for r in regions if r.cls == "site_plan" and r.use == "exterior"]
    exterior_json = EX.exterior(top_plan, section_geom, elevations, sites,
                                outlines.get(reference.id) if reference is not None else None, conflict, warnings)
    if multi and not elevations:
        warnings.append("no elevation drawn: facade materials and outside openings are not drawn (facade empty)")

    # Debug images.
    if debug:
        for entry, doc in zip(documents_json, docs):
            for sj in entry["sheets"]:
                sheet = next((s for s in doc.sheets if s.id == sj["id"]), None)
                sheet_regions = [r for r in regions if r.file == doc.file and r.sheet is sheet and r.kind != "raster"]
                if sheet is None or not sheet_regions:
                    continue
                from wenart.building import slugify
                from wenart.sheets import debug as DB
                name = f"{slugify(doc.file)}_{sheet.id}.png"
                mpu = entry["units"].get("metres_per_unit") or 1.0
                DB.sheet_image(sheet, sheet_regions,
                               [(b, d * mpu, e) for b, d, e in stray_draw.get((doc.file, sheet.id), [])],
                               out_dir / DEBUG_DIR / name)
                sj["debug_image"] = f"{DEBUG_DIR}/{name}"

    doc_json = {
        "schema_version": "1.0", "kind": "sheets", "project": project_dir.name,
        "created_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "code_commit": _commit(),
        "inputs": inputs_of(project_dir),
        "multi_region": multi,
        "documents": documents_json, "regions": [region_json(r) for r in regions], "stray": strays_json,
        "levels": levels_json, "variants": variants_json, "heights": heights_json, "exterior": exterior_json,
        "conflicts": conflicts, "warnings": list(dict.fromkeys(warnings)), "needs_review": needs_review,
        "questions": len(items), "answers": str(answers) if isinstance(answers, (str, Path)) else None,
    }
    errors = validation_errors(doc_json)
    if errors:
        doc_json["warnings"].extend(f"schema: {e}" for e in errors[:20])
        doc_json["needs_review"].append({"region": None, "file": None,
                                         "reason": "sheets.json failed schema validation"})
    (out_dir / SHEETS_JSON).write_text(json.dumps(doc_json, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    RP.write_report(doc_json, out_dir / REPORT_MD, pending)
    return Result(doc=doc_json, pending=pending, questions=len(items),
                  review=[n["reason"] for n in doc_json["needs_review"]], regions=regions)


def multi_region(regions: list) -> bool:
    """True when a sheet holds >= 2 plan regions, or a section, elevation, roof plan or site plan is drawn: the
    project is read region by region in one registered frame (M10). Otherwise every page is one plan (M2-M9)."""
    per_sheet: dict[tuple, int] = {}
    for r in regions:
        if r.use == "read":
            per_sheet[(r.file, r.sheet.id)] = per_sheet.get((r.file, r.sheet.id), 0) + 1
    return any(n >= 2 for n in per_sheet.values()) or any(r.use in ("heights", "exterior") for r in regions)


def _polyline_note(plans: list, warnings: list) -> None:
    """Report (never fix) the largest drawn polylines of registered plans whose sizes differ by more than 5 cm
    (real02: the dwelling outline is 7.19 x 10.50 m in the basement, 7.59 x 10.50 m on the ground floor)."""
    sized = [(r, r.features.get("largest_polyline")) for r in plans]
    sized = [(r, p) for r, p in sized if p and p.get("size_m")]
    if len(sized) < 2:
        return
    sizes = {tuple(sorted(p["size_m"])) for _, p in sized}
    lo = min(min(s) for s in sizes), min(max(s) for s in sizes)
    hi = max(min(s) for s in sizes), max(max(s) for s in sizes)
    if max(hi[0] - lo[0], hi[1] - lo[1]) <= 0.05:
        return
    def one(r, p) -> str:
        shape = "closed" if p["closed"] else f"open, ends {p['ends_m']:.2f} m apart"
        return (f"{r.id} ({(r.level or {}).get('id')}) {p['entity']} on {p['layer']} {p['size_m'][0]:.2f} x "
                f"{p['size_m'][1]:.2f} m ({shape})")

    listed = "; ".join(one(r, p) for r, p in sized)
    residuals = ", ".join(f"{r.id} {r.registration.get('residual_m')}" for r, _ in sized
                          if r.registration and r.registration.get("method") not in ("reference", None))
    warnings.append(f"the largest drawn polylines of the plans differ in size: {listed}; the registered outlines "
                    f"(all long strokes, columns included) give residuals {residuals or '-'} m; each level is kept "
                    f"as drawn")


def _stray_reason(cluster, n_doc: int, framed: bool) -> str:
    share = cluster.size / max(n_doc, 1) * 100.0
    where = "far outside the frame" if framed else "far from every other drawing"
    return f"{where}, {cluster.size} entit{'y' if cluster.size == 1 else 'ies'} ({share:.2f} % of the document)"


def _hidden_stray(hid: dict, res, regions: list) -> Optional[float]:
    """Distance (source units) of a not-drawn entity that lies outside every frame (or far from every region)."""
    from wenart.sheets.model import box_distance, in_box
    from wenart.sheets.split import STRAY_FAR

    b = tuple(hid["box"])
    c = ((b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0)
    drawn = [r for r in regions if r.kind != "raster"]
    if not drawn:
        return None
    dist = min(box_distance(b, r.box) for r in drawn)
    if res.frames:
        if any(in_box(c, f["box"]) for f in res.frames):
            return None
        return dist
    sizes = [max(r.box[2] - r.box[0], r.box[3] - r.box[1]) for r in drawn]
    if dist > STRAY_FAR * statistics.median(sizes):
        return dist
    return None


def _pdf_scale(doc) -> tuple[Optional[float], str]:
    """A PDF's scale from its scale notes (``ÖLÇEK 1/100``) when every page that has one agrees; else none (the
    generic core reads the scale from the dimension texts, M7)."""
    from wenart.ingest.model import METRES_PER_POINT, parse_scale_text

    ratios = {parse_scale_text(t.text) for s in doc.sheets for t in s.texts if parse_scale_text(t.text)}
    if len(ratios) == 1:
        return next(iter(ratios)) * METRES_PER_POINT, "pdf_scale_text"
    return None, "none"


def _reference(plans: list, levels: list) -> Optional[Region]:
    """The base ground-floor plan, else the lowest base plan."""
    bases = []
    for lv in levels:
        r = next((p for p in plans if p.id == lv["base_region"]), None)
        if r is not None and r.metres_per_unit:
            bases.append((lv["order"], r))
    if not bases:
        return None
    ground = [r for o, r in bases if o == 0]
    return ground[0] if ground else min(bases, key=lambda x: x[0])[1]


def region_json(r: Region) -> dict:
    mpu = r.metres_per_unit
    w, h = r.box[2] - r.box[0], r.box[3] - r.box[1]
    return {
        "id": r.id, "file": r.file, "sheet": r.sheet.id, "page": r.sheet.page, "box": round_box(r.box),
        "box_m": [round(w * mpu, 3), round(h * mpu, 3)] if mpu else None, "entities": r.n_entities,
        "frame": r.frame, "class": r.cls, "class_method": r.class_method,
        "class_confidence": round(float(r.class_confidence), 3), "status": r.status, "title": r.title,
        "features": _jsonable(r.features), "level": r.level, "variant_group": r.variant_group, "variant": r.variant,
        "variant_slug": r.variant_slug, "variant_gloss": r.variant_gloss, "ai": r.ai, "metres_per_unit": mpu,
        "transform_to_building": r.transform_to_building, "registration": r.registration, "use": r.use,
        "ignored_reason": r.ignored_reason, "evidence": r.evidence, "conflicts": r.conflicts,
    }


def _jsonable(value):
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items() if not k.startswith("_")}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, float):
        return round(value, 4)
    return value


def validation_errors(doc: dict) -> list[str]:
    import jsonschema

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    return [f"{'/'.join(map(str, e.absolute_path))}: {e.message}" for e in validator.iter_errors(doc)]


def load(out_dir) -> Optional[dict]:
    """``<out>/sheets.json`` or None."""
    path = Path(out_dir) / SHEETS_JSON
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
