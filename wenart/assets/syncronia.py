"""The Syncronia manufacturer models of the user's zip "beds.zip" as a library source (3 Nov 2026, the user: "Include
into the library (the proper ones) and also open up a new ranking tab in the ranking page for them so I can rank them";
before: "Disregard the license things for now").

What: the zip (Google Drive ``DRIVE_FILE_ID``, ``ZIP_BYTES``; on the volume at ``ZIP_PATH`` since the inspection pod
of 3 Nov 2026) is a download set of syncronia.com: one folder per product (``beds/<brand>/<product>/``) with
``meta.json`` (title, brand, source page, the site's terms) and the model files in nested zips. ``ingest``:

- reads every member (``zip_inspect.scan``: nested zips opened, unsafe names refused) and takes every model a free
  tool opens: 3DS through Assimp, FBX / OBJ / COLLADA / glTF through Blender (``zip_inspect``); SketchUp files and
  CAD surfaces (IGES) are listed as not ingested (no open-source reader);
- types and measures each model against the product type of its ``meta.json`` (``META_TYPES``: beds -> double and
  single bed; ``warehouse.choose``: metres, inches, cm, mm, feet; up axis) and keeps only the models that fit a real
  product size (``fits``): "the proper ones";
- fixes units, up axis and origin (``warehouse.fixup``), gives a model without materials its part materials
  (``part_materials``: white linen bedding, taupe upholstery the fit recolours, bronze feet), takes the front from the
  head end (headboard, else pillows) and writes ``<assets>/models/syncronia/<uid>.glb``;
- writes the catalogue entries (``entry``: ``source: syncronia``, licence ``LICENCE`` flagged ``non_commercial``,
  ``commercial_safe: false``, the credit fields from ``meta.json``, ``audit: pending`` until the studio renders are
  looked at) to ``<out>/syncronia_entries.json`` and the record of every model (taken or not, and why) to
  ``<out>/ingest_syncronia.json``.

``merge`` puts entries into ``catalog_library.json`` (an entry of the same id is replaced; ``sources`` and the
source's ``datasets`` note kept current); ``review`` sets the audit of reviewed entries (keep / removed, the notes).

Licence: the user's decision (3 Nov 2026) is to disregard licences for now; the site's own words in ``meta.json``
("for use in a design project and its renders; the file itself is not cleared for republishing") are kept in each
entry's ``syncronia`` record and in ``notice()``; relaxed licence mode only (``catalog.SOURCE_TEXT_FLAGS``).

CLI::

    python -m wenart.assets.syncronia ingest --zip Z --work DIR --assets DIR --out DIR [--merge-catalog]
    python -m wenart.assets.syncronia merge --entries E.json [--catalog PATH]
    python -m wenart.assets.syncronia review --decisions D.json [--catalog PATH]
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Optional

SOURCE = "syncronia"
UID_PREFIX = "syncronia_"
UID_HEX = 24
LICENCE = "SYNCRONIA-UNREVIEWED"
LICENCE_FLAG = "non_commercial"
LICENCE_DECLARED_BY = "publisher"
LICENCE_URL = "https://www.syncronia.com/en"
DRIVE_FILE_ID = "1iYSSFbHkn1DH2qtAJ7LF44bZccQ_SYwL"
ZIP_NAME = "beds.zip"
ZIP_BYTES = 462_846_689
ZIP_PATH = f"/workspace/library/inbox/{DRIVE_FILE_ID}/{ZIP_NAME}"
DATASET_NAME = "Syncronia manufacturer models (syncronia.com), the user's zip \"beds.zip\""
USER_DECISION = ("user request of 3 Nov 2026: include the proper models of beds.zip in the library and rank them; "
                 "licence not reviewed (the user: \"Disregard the license things for now\"): relaxed licence mode "
                 "only, commercial_safe: no")
FIX_VERSION = "syncronia-1"
PENDING_REASON = "new Syncronia model (the user's beds.zip, 3 Nov 2026): waiting for the look at its studio render"
# the product type of meta.json -> the catalogue types it may be
META_TYPES: dict[str, tuple[str, ...]] = {"beds": ("bed_double", "bed_single"), "bed": ("bed_double", "bed_single"),
                                         "sofas": ("sofa", "sofa_corner"), "armchairs": ("armchair",),
                                         "chairs": ("chair",), "tables": ("table_dining", "table_coffee")}
BRANDS = {"bb-italia": "B&B Italia", "maxalto": "Maxalto (B&B Italia)", "riva1920": "Riva 1920",
          "riva-1920": "Riva 1920", "mdf-italia": "MDF Italia", "horm": "Horm"}
# what the brands make (their own descriptions): the style families of the catalogue
BRAND_STYLES = {"bb-italia": ["modern", "modern minimal"], "maxalto": ["modern", "classic"],
                "riva1920": ["modern", "rustic"], "riva-1920": ["modern", "rustic"], "mdf-italia": ["modern minimal"],
                "horm": ["modern"]}
NOT_INGESTED = {".skp": "SketchUp file: no open-source reader (export it as COLLADA or glTF from SketchUp)",
                ".igs": "IGES CAD surfaces: no mesh (tessellate it in a CAD tool first)"}


def uid_of(rel: str) -> str:
    return UID_PREFIX + hashlib.sha256(str(rel).encode("utf-8")).hexdigest()[:UID_HEX]


def model_rel(uid: str) -> str:
    return f"models/{SOURCE}/{uid}.glb"


def brand_of(rel: str, meta: dict) -> str:
    key = str(meta.get("brand") or (PurePosixPath(rel).parts[1] if len(PurePosixPath(rel).parts) > 1 else ""))
    return key


def entry_fields() -> dict:
    return {"licence": LICENCE, "licence_url": LICENCE_URL, "licence_flag": LICENCE_FLAG,
            "licence_declared_by": LICENCE_DECLARED_BY, "commercial_safe": False}


def notice() -> str:
    return (f"{DATASET_NAME}: manufacturer product models downloaded from syncronia.com by the user; the site's own "
            "words: for use in a design project and its renders, the files not cleared for republishing. Licence not "
            "reviewed (the user's decision of 3 Nov 2026): relaxed licence mode only, commercial_safe: no. Changes: "
            "converted from 3DS, units, up axis and origin fixed, part materials added, scaled to the drawn footprint.")


def variant_title(meta: dict, rel: str, size_m: list) -> str:
    """The product title (``meta.json``, "Beds, " cut) with the brand and the size: several sizes of one product are
    told apart (Demetra 1.95 / 2.10 / 2.21 / 2.41 m)."""
    from wenart.assets.audit.growth_entries import source_text
    t = source_text(meta.get("title") or PurePosixPath(rel).parent.name)
    t = t.split(", ", 1)[1] if t.lower().startswith("beds, ") else t
    brand = BRANDS.get(brand_of(rel, meta), "")
    w, d = sorted(float(v) for v in size_m[:2])
    return f"{brand} {t} bed {w * 100:.0f} x {d * 100:.0f}".strip()


def entry(rec: dict, m: dict, meta: dict, checked_utc: str) -> dict:
    """A ``catalog_library.json`` entry of an ingested model (``rec`` = its ingest record, ``m`` = ``glbmesh.measure``
    of the written file)."""
    from wenart.assets.audit import growth_entries as GE
    from wenart.furniture import catalog as C
    ftype, uid = rec["type"], rec["uid"]
    if rec.get("front"):
        front, conf, note = rec["front"], rec["front_confidence"], rec["front_note"]
    else:
        front, conf, note = GE.front_of(ftype, m.get("stats"))
    title = variant_title(meta, rec["rel"], m["bbox_model_m"])
    brand_key = brand_of(rec["rel"], meta)
    author = f"{BRANDS.get(brand_key, brand_key or 'the manufacturer')} (manufacturer model, via Syncronia)"
    styles = [s for s in BRAND_STYLES.get(brand_key, []) if s in C.style_values()] or ["neutral"]
    e = {"id": uid, "type": ftype, "kind": "furniture", "source": SOURCE, **entry_fields(), "name": title}
    e.update(GE.frame_fields(m, front, conf, note))
    w, d, h = e["bbox_m"]
    raw = " x ".join(f"{float(v):.4g}" for v in rec.get("raw_box") or [])
    e.update({"unit_scale": 1.0, "units_known": True,
              "unit_note": (f"units known: the 3DS box {raw} read in {rec['unit']} fits a real {ftype} (size table); "
                            f"written in metres by the syncronia fix-up: {w:.3g} x {d:.3g} x {h:.3g} m"),
              "styles": styles, "style_note": f"the brand {BRANDS.get(brand_key, brand_key)}: {', '.join(styles)}",
              "glb": model_rel(uid), "sha256_glb": rec["sha256"], "uid": uid, "title": title, "author": author,
              "brand": BRANDS.get(brand_key, brand_key), "real_product": True,
              "source_url": str(meta.get("source") or LICENCE_URL),
              "via": f"{DATASET_NAME}; converted by wenart/assets/syncronia.py ({FIX_VERSION})",
              "attribution": (f"\"{title}\" by {author}, {meta.get('source') or LICENCE_URL}, from the user's zip "
                              f"\"{ZIP_NAME}\" ({rec['rel']}); licence not reviewed ({USER_DECISION}); changes: "
                              "converted from 3DS, units, up axis and origin fixed, part materials added, scaled to "
                              "the drawn footprint, re-oriented, rendered; PoC use in relaxed licence mode only")})
    e.update(GE._mesh_fields(m))
    if m.get("pbr"):
        e["pbr_maps"] = dict(m["pbr"])
    classes = rec.get("classes") or {}
    bedding = bool(classes.get("bedding"))
    e.update({"has_mattress": bedding, "has_bedding": bedding, "has_pillows": bool(rec.get("pillows")),
              "has_cushions": False, "bed_frame": False,
              "bed_note": ("the model carries its own mattress and bedding (part classes of "
                           "wenart.assets.part_materials)" if bedding else "no bedding part found")})
    if rec.get("material"):
        from wenart.assets import part_materials as PM
        e.update(PM.material_fields(rec["material"]["slots"]))
        e["material_tags_note"] = ("part materials of wenart.assets.part_materials (the 3DS file has no materials): "
                                   "upholstery fabric (recoloured by the fit), white linen bedding, bronze feet")
    e["syncronia"] = {"rel": rec["rel"], "format": rec.get("format"), "unit": rec.get("unit"),
                      "factor": rec.get("factor"), "up_fix": rec.get("up_fix"), "raw_box_m": rec.get("raw_box"),
                      "candidates": rec.get("candidates"), "converter": rec.get("converter"),
                      "part_classes": classes, "fix_version": FIX_VERSION, "src_sha256": rec.get("src_sha256"),
                      "meta": {k: meta.get(k) for k in ("title", "brand", "type", "source", "licence", "terms")}}
    e["growth"] = {"pod": "syncronia", "list": "ingest_syncronia.json", "decision": USER_DECISION}
    e["audit"] = {"status": "pending", "reasons": [PENDING_REASON], "fixes": {}, "version": FIX_VERSION,
                  "checked_utc": checked_utc}
    return e


def ingest(zip_path: Path, work: Path, assets: Path, out: Path, blender: Optional[str] = None) -> dict:
    """Every model of the zip (module docstring); returns ``{"records": [...], "entries": [...]}``."""
    from wenart.assets import part_materials as PM
    from wenart.assets import warehouse as WH
    from wenart.assets import zip_inspect as ZI
    from wenart.assets.audit import glbmesh as GM
    checked = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    work.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    ZI.scan(zip_path, work)
    records, entries = [], []
    blender_jobs = []
    models = ZI.model_list(work)
    conv: dict = {}
    for mdl in models:
        if mdl["format"] == ".3ds":
            r = ZI.assimp_convert(Path(mdl["src"]), work / "converted" / f"{mdl['id']}.glb")
            if r.get("ok"):
                conv[mdl["id"]] = dict(r, converter="assimp")
        elif mdl["format"] not in (".glb", ".skp") and mdl["format"] not in NOT_INGESTED:
            blender_jobs.append({"id": mdl["id"], "src": mdl["src"],
                                 "dst": str(work / "converted" / f"{mdl['id']}.glb")})
    if blender_jobs and blender:
        for k, v in ZI.blender_run(blender, "convert", blender_jobs, work, timeout_s=3600).items():
            if v.get("ok"):
                conv[k] = dict(v, converter="blender")
    for mdl in models:
        rel = mdl["rel"]
        meta = ZI.meta_for(rel, work)
        rec: dict = {"rel": rel, "format": mdl["format"], "uid": uid_of(rel), "taken": False}
        if mdl["format"] in NOT_INGESTED:
            rec["why"] = NOT_INGESTED[mdl["format"]]
            records.append(rec)
            continue
        glb = Path(mdl["src"]) if mdl["format"] == ".glb" else work / "converted" / f"{mdl['id']}.glb"
        if mdl["format"] != ".glb" and mdl["id"] not in conv:
            rec["why"] = "not converted (no free tool opened it)"
            records.append(rec)
            continue
        types = list(META_TYPES.get(str(meta.get("type") or "").lower(), ()))
        mrec = ZI.measure_one(mdl, glb, work, types)
        rec.update({k: mrec.get(k) for k in ("type", "unit", "factor", "up_fix", "fits", "size_error", "box_m",
                                             "raw_box", "candidates", "triangles", "error")})
        rec["converter"] = (conv.get(mdl["id"]) or {}).get("converter", "none")
        rec["src_sha256"] = WH.sha256_file(Path(mdl["src"]))
        if not mrec.get("ok"):
            rec["why"] = f"not measured: {mrec.get('error')}"
            records.append(rec)
            continue
        if not mrec.get("fits") or mrec.get("type") not in (types or [mrec.get("type")]):
            rec["why"] = f"size outside every real {'/'.join(types) or mrec.get('type')} size: not a proper model"
            records.append(rec)
            continue
        dest = assets / model_rel(rec["uid"])
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(Path(mrec["fixed"]).read_bytes())           # units, up axis, origin (warehouse.fixup)
        doc, _bin = WH.read_glb(dest)
        ps = PM.parts(dest)
        classes = PM.classify(ps, rec["type"])
        PM.write_debug(out / "parts" / f"{rec['uid']}.json", ps, classes)
        if classes and PM.needs_materials(doc):
            rec["material"] = PM.assign(dest, dest, ps, classes)
            rec["classes"] = rec["material"]["classes"]
        else:
            rec["classes"] = {}
        small = [p for p, c in zip(ps, classes) if c["class"] == "bedding"]
        big = max((p["area"] for p in small), default=0.0)
        rec["pillows"] = sum(1 for p in small if p["area"] < 0.25 * big)
        fr = PM.front_from_parts(ps, classes)
        m = GM.measure(dest)
        from wenart.assets.audit import growth_entries as GE
        g_front, g_conf, g_note = GE.front_of(rec["type"], m.get("stats"))
        if fr:
            agree = g_conf != "low" and g_front == fr[0]
            rec.update(front=fr[0], front_confidence="high" if agree else "medium",
                       front_note=fr[1] + (f"; geometry agrees ({g_note})" if agree else f"; geometry: {g_note}"))
        else:
            rec.update(front=g_front, front_confidence=g_conf, front_note=g_note)
        rec["sha256"] = WH.sha256_file(dest)
        rec["taken"] = True
        e = entry(rec, m, meta, checked)
        entries.append(e)
        rec["id"] = e["id"]
        rec["title"] = e["title"]
        records.append(rec)
    doc = {"zip": str(zip_path), "checked_utc": checked, "fix_version": FIX_VERSION,
           "taken": sum(1 for r in records if r["taken"]), "listed": len(records), "records": records}
    (out / "ingest_syncronia.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "syncronia_entries.json").write_text(json.dumps({"entries": entries}, indent=1, ensure_ascii=False) + "\n",
                                                encoding="utf-8")
    return {"records": records, "entries": entries}


def catalog_path() -> Path:
    from wenart.assets.audit import items as I
    return Path(I.LIBRARY_PATH)


def _write(path: Path, doc: dict) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def merge(entries: list[dict], path: Optional[Path] = None) -> dict:
    """The entries into the library catalogue (same id replaced, new ids appended); the catalogue's ``sources`` list
    and a ``datasets`` note for the source. Returns ``{"added", "replaced"}``."""
    path = Path(path) if path else catalog_path()
    doc = json.loads(path.read_text(encoding="utf-8"))
    rows = doc.setdefault("entries", [])
    at = {e.get("id"): i for i, e in enumerate(rows)}
    added = replaced = 0
    for e in entries:
        if e["id"] in at:
            rows[at[e["id"]]] = e
            replaced += 1
        else:
            rows.append(e)
            added += 1
    if SOURCE not in (doc.get("sources") or []):
        doc.setdefault("sources", []).append(SOURCE)
    datasets = doc.get("datasets")
    if isinstance(datasets, dict):
        datasets[SOURCE] = {"name": DATASET_NAME, "licence": LICENCE, "licence_url": LICENCE_URL,
                            "decision": USER_DECISION, "notice": notice()}
    elif isinstance(datasets, list) and not any(isinstance(d, dict) and d.get("source") == SOURCE for d in datasets):
        datasets.append({"source": SOURCE, "name": DATASET_NAME, "licence": LICENCE, "licence_url": LICENCE_URL,
                         "decision": USER_DECISION, "notice": notice()})
    counts = doc.get("counts")
    if isinstance(counts, dict):
        counts[SOURCE] = {"entries": sum(1 for e in rows if e.get("source") == SOURCE)}
    _write(path, doc)
    return {"added": added, "replaced": replaced}


def review(decisions: dict, path: Optional[Path] = None) -> dict:
    """The audit of reviewed entries: ``decisions`` = ``{id: {"status": "keep" | "removed", "notes": [...],
    "reasons": [...], "front_axis"?: axis}}``; a new front axis re-orients ``bbox_m``. Returns the counts."""
    from wenart.furniture import catalog as C
    path = Path(path) if path else catalog_path()
    doc = json.loads(path.read_text(encoding="utf-8"))
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    done: dict[str, int] = {}
    for e in doc.get("entries") or []:
        d = decisions.get(e.get("id"))
        if not d or e.get("source") != SOURCE:
            continue
        if d.get("front_axis") and d["front_axis"] != e["front_axis"]:
            e["front_axis"] = d["front_axis"]
            e["bbox_m"] = [round(float(v), 4) for v in C.oriented_bbox(e["bbox_model_m"], d["front_axis"])]
            e["front_axis_note"] = str(d.get("front_note") or "front set at the review of the studio render")
        if d.get("front_axis_confidence"):
            e["front_axis_confidence"] = d["front_axis_confidence"]
        e["audit"] = {"status": d["status"], "reasons": list(d.get("reasons") or []), "fixes": {},
                      "notes": list(d.get("notes") or []), "version": FIX_VERSION, "checked_utc": now,
                      "reviewed_by": d.get("by") or "Claude (look at the ranking studio render, user request of 3 Nov "
                                                       "2026)"}
        done[d["status"]] = done.get(d["status"], 0) + 1
    _write(path, doc)
    return done


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.assets.syncronia")
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("ingest")
    i.add_argument("--zip", default=ZIP_PATH)
    i.add_argument("--work", required=True)
    i.add_argument("--assets", required=True)
    i.add_argument("--out", required=True)
    i.add_argument("--blender", default=None)
    i.add_argument("--merge-catalog", action="store_true", help="also merge the entries into the catalogue (pending)")
    mg = sub.add_parser("merge")
    mg.add_argument("--entries", required=True)
    mg.add_argument("--catalog", default=None)
    rv = sub.add_parser("review")
    rv.add_argument("--decisions", required=True)
    rv.add_argument("--catalog", default=None)
    a = ap.parse_args(argv)
    if a.cmd == "ingest":
        res = ingest(Path(a.zip), Path(a.work), Path(a.assets), Path(a.out), a.blender)
        print(json.dumps({"taken": len(res["entries"]), "listed": len(res["records"]),
                          "titles": [e["title"] for e in res["entries"]]}, ensure_ascii=False))
        if a.merge_catalog and res["entries"]:
            print(json.dumps(merge(res["entries"])))
        return 0 if res["entries"] else 1
    if a.cmd == "merge":
        ents = json.loads(Path(a.entries).read_text(encoding="utf-8"))["entries"]
        print(json.dumps(merge(ents, Path(a.catalog) if a.catalog else None)))
        return 0
    print(json.dumps(review(json.loads(Path(a.decisions).read_text(encoding="utf-8")),
                            Path(a.catalog) if a.catalog else None)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
