"""Catalogue entries of the new models of pod P4 (docs/milestone12.md §6.4 D24, library growth) and the catalogue
copies they go into.

What:

- ``polyhaven_entry``, ``abo_entry``, ``gso_entry``, ``infinigen_entry``, ``hssd_entry`` (Milestone 13): one entry each, in the shape of the
  source's existing entries (Poly Haven as in ``wenart/furniture/catalog.json``; ABO, GSO and the Infinigen models as
  in ``catalog_library.json``: frame fields, licence, credit fields, units, styles, ``glb`` + ``sha256_glb`` where
  ``wenart.assets.models.fetch_model`` and the Blender build find them). Infinigen models are ``source: generated``
  (made on our pod by Infinigen's BSD-3 code: the approval says "the generated models are ours") with the
  ``generated`` record naming the factory, the seed and the commit; GSO models are ``source: gso`` (CC BY 4.0, with
  the per-object licence evidence of ``growth_gso.py``); HSSD models (Milestone 13, docs/milestone13.md §12 D2) are
  ``source: hssd`` with the licence fields of ``wenart.assets.hssd.entry_fields`` (CC BY-NC 4.0, ``licence_flag:
  non_commercial``, ``commercial_safe: false``: relaxed licence mode only) and the ``hssd`` record (object id,
  synset, Floorplanner tags, the demand bin the pick served, the repo revision).
- ``front_of``: the front of a new model: ABO's documented -Y (README convention 2), else the geometric rule of the
  type (``objaverse.yaml`` front rules on the numpy measurement of ``glbmesh.py``; confidence ``medium``), else -Y
  with confidence ``low`` and the reason, so the audit's vision answer names the front (``decide.py``: a vision front
  turns a model only where code is unsure).
- ``build_copies``: the repo's two catalogues plus the new entries (same id: replaced), the dataset and notes
  fields, validated with ``wenart.furniture.catalog.validate`` and ``merge``. Every new entry starts with ``audit =
  {status: pending}``: until the P4 audit writes its decision nothing uses it (``catalog.usable``).
- ``apply_vision_fields``: after the vision question, the styles (the source's hint plus the answer's styles, at
  most 3 of the answer) and a bed's ``has_mattress`` (true only when the answer sees bedding) into the copies.

Why: CLAUDE.md library rules (only audited models are used; every model carries its licence and credit) and the
evidence rules (every inferred field says how it was found).

How: pure on dicts and measurement records; the CLI (``growth_run.py``) reads and writes the files.

Fix round after P6b (23 Oct 2026; the library lens of the P6b analysis: ATTRIBUTION.md of real03 showed "Hudson Reed
Sublime Vanity Unit &amp; Basin" and two more such titles, and 15 catalogue entries carry ``&amp;`` in ``name``,
``title`` and ``attribution``):

- What: ``source_text`` decodes the complete HTML entities of a title as the source lists it (``html.unescape``:
  ``&amp;`` -> ``&``); ``polyhaven_entry``, ``abo_entry``, ``gso_entry`` and ``hssd_entry`` take their ``name``,
  ``title`` and the title inside ``attribution`` from it.
- Why: the HSSD metadata and some ABO listings store HTML-escaped product names; the entry copied them as they are and
  every text built from the entry (the credit line of ATTRIBUTION.md, the fit report) showed the raw entity.
- How: only where an entry is written (a new model of a growth run); the committed entries keep their text (their
  credit is decoded where it is written: ``wenart.run.copy``), so no audit decision changes.
"""
from __future__ import annotations

import html
import json
import re
from typing import Optional

from wenart.assets.audit import VERSION

CC_BY = "CC-BY-4.0"
CC_BY_URL = "https://creativecommons.org/licenses/by/4.0/"
PH_LICENCE_URL = "https://polyhaven.com/license"
PH_API_FILES = "https://api.polyhaven.com/files/{id}"
PH_PAGE = "https://polyhaven.com/a/{id}"
GROWTH_NOTE = ("Milestone 12 pod P4 (docs/milestone12.md §6.4, user OK of 11 Oct 2026): models added by the library "
               "growth (Poly Haven, ABO, Google Scanned Objects, Infinigen test batch), audited in P4 like the others "
               "(results/library/audit/p4/, results/library/growth/).")
PENDING_REASON = "new in pod P4 (library growth): waiting for the P4 audit"
STYLE_MAX = 3                  # styles taken from one vision answer (the bake-off: its look judgements are weak)

GSO_DATASET = {"name": "Google Scanned Objects", "owner": "Google Research",
               "page": "https://app.gazebosim.org/GoogleResearch/fuel/collections/Scanned%20Objects%20by%20Google%20"
                       "Research",
               "mirror": "https://huggingface.co/datasets/suvadityamuk/google-scanned-objects-raw",
               "licence": CC_BY, "licence_url": CC_BY_URL,
               "note": "CC BY 4.0 confirmed per object on pod P4 (licence_evidence of each entry: the archive's own "
                       "files or the object's Gazebo Fuel record); objects without that evidence were not added"}
GSO_VIA = "Google Scanned Objects (Google Research, CC BY 4.0), via the Hugging Face mirror " \
          "suvadityamuk/google-scanned-objects-raw"
GSO_CHANGES = "converted from OBJ to GLB, scaled to the drawn footprint, re-oriented, rendered, AI-retouched"
INFINIGEN_REPO = "princeton-vl/infinigen"
HSSD_CHANGES = "scaled to the drawn footprint, re-oriented, rendered, AI-retouched"
GROWTH_NOTE_M13 = ("Milestone 13 pod P2 (docs/milestone13.md §5.1 phase 2, §13.6; user decisions D1, D2 of 12 Oct "
                   "2026): models added by the library growth by drawn demand (ABO size grid, Poly Haven 2K and "
                   "vegetation, HSSD by type and size bin under CC BY-NC 4.0 for the relaxed licence mode), audited "
                   "in P2 with the Milestone 13 gates (results/library/audit/p4/ and results/library/growth/: the "
                   "folders scripts/jobs/library_growth.sh copy_results writes).")
PENDING_REASON_M13 = "new in pod P2 (Milestone 13 library growth): waiting for the P2 audit"


def _round(v, n: int = 4) -> list:
    return [round(float(x), n) + 0.0 for x in v]          # + 0.0: no -0.0 in the JSON


# --------------------------------------------------------------------------
# Frame and front
# --------------------------------------------------------------------------

def front_of(ftype: str, stats: Optional[dict], documented: Optional[str] = None,
             rules: Optional[dict] = None) -> tuple[str, str, str]:
    """``(front_axis, confidence, note)`` of a new model (module docstring). ``stats`` = ``glbmesh.front_stats``."""
    from wenart.assets import objaverse as OV
    from wenart.assets.audit.items import _front_rules
    if documented:
        return documented, "high", f"documented front {documented}"
    rule = _front_rules().get(ftype)
    if rule in (None, "none"):
        return "-Y", "low", f"a {ftype} has no front"
    if rule == "documented" or not stats:
        why = "only the source can document it" if rule == "documented" else "not measured"
        return "-Y", "low", f"front not known ({why}): -Y assumed, the audit's vision answer names it"
    rules = rules if rules is not None else (OV.load_config().get("front_rules") or {})
    axis, note = OV.geometric_front(stats, rule, rules)
    if axis:
        return axis, "medium", f"geometry: {note}"
    return "-Y", "low", f"geometry: {note}; -Y assumed, the audit's vision answer names the front"


def frame_fields(m: dict, front: str, confidence: str, note: str) -> dict:
    """The frame fields of ``catalog.FRAME_FIELDS`` from a ``glbmesh.measure`` record (a flat side is kept at 1 mm:
    the catalogue needs three positive numbers)."""
    from wenart.furniture import catalog as C
    model = [max(float(v), 0.001) for v in m["bbox_model_m"]]
    if model != [float(v) for v in m["bbox_model_m"]]:
        note += "; a flat side of 0 m is recorded as 1 mm"
    mn, mx = _round(m["bbox_min_m"]), _round(m["bbox_max_m"])
    return {"bbox_m": _round(C.oriented_bbox(model, front)), "bbox_model_m": _round(model), "bbox_min_m": mn,
            "bbox_max_m": mx, "front_axis": front, "up_axis": "+Z", "origin_offset": C.origin_offset(mn, mx),
            "front_axis_confidence": confidence, "front_axis_note": note}


def styles_hint(text: str) -> list[str]:
    """Style families a title, a listing style or tags name (``growth.styles_from_text``)."""
    from wenart.assets.audit.growth import styles_from_text
    from wenart.furniture import catalog as C
    allowed = set(C.style_values())
    return [s for s in styles_from_text(text or "") if s in allowed]


def _styles(hint: list[str], why: str) -> tuple[list[str], str]:
    if hint:
        return list(hint), f"P4 growth: {why} names {', '.join(hint)}; the audit's vision answer adds its styles"
    return ["neutral"], f"P4 growth: {why} names no style: neutral until the audit's vision answer names styles"


def pending_audit(checked_utc: str) -> dict:
    return {"status": "pending", "reasons": [PENDING_REASON], "fixes": {}, "version": VERSION,
            "checked_utc": checked_utc}


def _kind_type(kind: str, ftype: str) -> dict:
    if kind == "decor":
        return {"type": f"decor_{ftype}", "kind": "decor", "decor_type": ftype}
    return {"type": ftype, "kind": "furniture"}


def _mesh_fields(m: dict) -> dict:
    inf = m.get("info") or {}
    return {"polycount": int(m["triangles"]), "vertices": int(m["vertices"]), "textured": bool(inf.get("textured")),
            "vertex_colours": bool(inf.get("vertex_colours"))}


def _bed_fields(ftype: str, kind: str) -> dict:
    from wenart.furniture import catalog as C
    if kind == "furniture" and ftype in C.BED_TYPES:
        return {"has_mattress": False, "bed_frame": False,
                "bed_note": "P4 growth: no mattress known; the audit's vision answer sets has_mattress when it sees "
                            "bedding"}
    return {}


# --------------------------------------------------------------------------
# Entries per source
# --------------------------------------------------------------------------

# fix round after P6b (23 Oct 2026): a complete HTML entity (named with its ";", decimal or hex); a bare "&" ("Stone &
# Beam", "Solid&Co") or a legacy name without ";" ("&copy") is text and stays
HTML_ENTITY = re.compile(r"&(?:#[0-9]+|#[xX][0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]*);")


def source_text(text) -> str:
    """Fix round after P6b (module docstring): a source's title with its complete HTML entities decoded
    (``HTML_ENTITY``: ``&amp;`` -> ``&``, ``&quot;`` -> ``"``) and the outer spaces stripped; "" for None."""
    return HTML_ENTITY.sub(lambda m: html.unescape(m.group(0)), str(text or "")).strip()


def polyhaven_entry(cand: dict, m: dict, gltf_rel: str, sha256_gltf: Optional[str], resolution: str,
                    checked_utc: str, rules: Optional[dict] = None) -> dict:
    """A ``catalog.json`` entry (furniture in ``entries``, decor in ``decor`` with the type ``decor_<name>`` and no
    ``kind``, as the existing Poly Haven decor) of an approved Poly Haven candidate."""
    ftype, kind = cand["type"], cand["kind"]
    front, conf, note = front_of(ftype, m.get("stats"), rules=rules)
    styles, style_note = _styles([s for s in cand.get("styles_hint") or [] if s], "the title and tags")
    e = {"id": cand["id"], "type": f"decor_{ftype}" if kind == "decor" else ftype, "source": "polyhaven",
         "licence": "CC0", "licence_url": PH_LICENCE_URL, "name": source_text(cand.get("title")) or cand["id"],
         "category": cand.get("category")}
    e.update(frame_fields(m, front, conf, note))
    e.update({"styles": styles, "style_note": style_note, "url": PH_PAGE.format(id=cand["id"]),
              "api_url": PH_API_FILES.format(id=cand["id"]), "gltf": gltf_rel, "resolution": resolution,
              "polycount": int(m["triangles"]), "vertices": int(m["vertices"])})
    if cand.get("dims_m"):
        e["dimensions_api_mm"] = [int(round(float(v) * 1000)) for v in cand["dims_m"]]
    if sha256_gltf:
        e["sha256_gltf"] = sha256_gltf
    e.update(_bed_fields(ftype, kind))
    e["growth"] = {"pod": "P4", "list": "candidates_polyhaven.json", "fits_real_size": cand.get("fits_real_size")}
    e["audit"] = pending_audit(checked_utc)
    return e


def abo_entry(cand: dict, m: dict, sha: str, cfg: dict, checked_utc: str, footprint: Optional[dict] = None) -> dict:
    """A ``catalog_library.json`` entry of an approved ABO candidate (as ``objaverse.catalog_entry`` writes ABO
    entries): documented front -Y, units known, the ABO credit line."""
    from wenart.assets import abo as AB
    from wenart.assets import objaverse as OV
    from wenart.assets.audit.items import _front_rules
    ftype, kind = cand["type"], cand["kind"]
    uid = cand["id"]
    ds = cfg["dataset"]
    front, conf, _ = front_of(ftype, m.get("stats"), documented=ds.get("front_axis", "-Y"))
    note = (f"documented front {front} (ABO convention (3dmodels/README.md): glTF +Z points to the product's natural "
            "front = -Y in the importer's Z-up frame)")
    rule = _front_rules().get(ftype)
    if m.get("stats") and rule not in (None, "none", "documented"):
        axis, gnote = OV.geometric_front(m["stats"], rule, OV.load_config().get("front_rules") or {})
        if axis:
            note += f"; geometry: {gnote}"
    title = source_text(cand.get("title")) or uid                  # fix round after P6b: entities decoded
    hint = ([cand["family"]] if cand.get("family") else []) or styles_hint(cand.get("style") or "")
    styles, style_note = _styles(hint, f"the ABO listing style {cand.get('style')!r}" if cand.get("style")
                                 else "the ABO listing")
    e = {"id": uid, **_kind_type(kind, ftype), "source": "abo", "licence": CC_BY, "licence_flag": None,
         "licence_url": ds["licence_url"], "name": title}
    e.update(frame_fields(m, front, conf, note))
    w, d, h = e["bbox_m"]
    e.update({"unit_scale": 1.0, "unit_note": f"units known (metres, abo metadata): {w:.3g} x {d:.3g} x {h:.3g} m",
              "units_known": True, "styles": styles, "style_note": style_note,
              "glb": f"models/abo/{uid}.glb", "sha256_glb": sha, "uid": uid, "title": title,
              "author": ds["credit_data"],
              "source_url": AB.source_url(cand.get("item_id") or uid[4:], cfg), "via": ds["via"],
              "attribution": AB.attribution(title, cfg)})
    e.update(_mesh_fields(m))
    e.update({"abo_item_id": cand.get("item_id"), "abo_3dmodel_id": uid[len(AB.UID_PREFIX):],
              "abo_path": f"3dmodels/original/{cand['glb']}", "abo_product_type": cand.get("product_type"),
              "style_hint": cand.get("style")})
    if kind == "furniture" and ftype in OV.FOOTPRINT_TYPES:
        e["chaise_side"], e["chaise_note"] = OV.chaise_side(footprint, front, OV.load_config())
    e.update(_bed_fields(ftype, kind))
    e["growth"] = {"pod": "P4", "list": "candidates_abo.json", "group": cand.get("group"),
                   "family": cand.get("family")}
    e["audit"] = pending_audit(checked_utc)
    return e


def gso_entry(rec: dict, m: dict, sha: str, checked_utc: str, rules: Optional[dict] = None) -> dict:
    """A ``catalog_library.json`` decor entry of a Google Scanned Objects archive whose CC BY 4.0 licence was
    confirmed (``rec`` = the record of ``growth_gso.licence_records``)."""
    ftype = rec["type"]
    front, conf, note = front_of(ftype, m.get("stats"), rules=rules)
    title = source_text(rec.get("title")) or rec["name"].replace("_", " ")     # fix round after P6b
    source_url = rec.get("page") or GSO_DATASET["page"]
    e = {"id": rec["uid"], **_kind_type("decor", ftype), "source": "gso", "licence": CC_BY, "licence_flag": None,
         "licence_url": CC_BY_URL, "name": title}
    e.update(frame_fields(m, front, conf, note))
    e.update({"unit_scale": 1.0, "unit_note": "units known (metres): Google Scanned Objects are real-scale scans "
                                              "(Gazebo SDF units)",
              "units_known": True, "glb": f"models/gso/{rec['uid']}.glb", "sha256_glb": sha, "uid": rec["uid"],
              "title": title, "author": rec.get("author") or GSO_DATASET["owner"], "source_url": source_url,
              "via": GSO_VIA,
              "attribution": f"\"{title}\" by {rec.get('author') or GSO_DATASET['owner']}, Google Scanned Objects "
                             f"(CC BY 4.0), {source_url}; changes: {GSO_CHANGES}"})
    styles, style_note = _styles([], "the scan's name")
    e.update({"styles": styles, "style_note": style_note})
    e.update(_mesh_fields(m))
    e.update({"gso_name": rec["name"], "gso_archive": rec.get("file"), "dataset_revision": rec.get("revision"),
              "licence_evidence": list(rec.get("evidence") or [])})
    e["growth"] = {"pod": "P4", "list": "candidates_gso.json", "up_axis_of_obj": rec.get("up_axis", "Z")}
    e["audit"] = pending_audit(checked_utc)
    return e


def infinigen_licence(tag: str) -> str:
    return f"generated (Infinigen {tag}, BSD-3-Clause)"


def infinigen_entry(rec: dict, m: dict, sha: str, commit: str, tag: str, checked_utc: str,
                    rules: Optional[dict] = None) -> dict:
    """A ``catalog_library.json`` entry of a model made by an Infinigen factory on the pod (``source: generated``;
    ``rec`` = a job record of ``growth_infinigen``: id, type, kind, factory class and module path, seed)."""
    ftype, kind = rec["type"], rec["kind"]
    front, conf, note = front_of(ftype, m.get("stats"), rules=rules)
    title = f"Infinigen {rec['factory'].replace('_', ' ')} ({rec['class']}, seed {rec['seed']})"
    url = f"https://github.com/{INFINIGEN_REPO}/tree/{commit}"
    e = {"id": rec["id"], **_kind_type(kind, ftype), "source": "generated", "licence": infinigen_licence(tag),
         "licence_flag": None, "licence_url": f"https://github.com/{INFINIGEN_REPO}/blob/{commit}/LICENSE",
         "name": title}
    e.update(frame_fields(m, front, conf, note))
    e.update({"unit_scale": 1.0, "unit_note": "units known (metres): Infinigen builds its assets at real scale in "
                                              "Blender units",
              "units_known": True, "glb": f"models/generated/{rec['id']}.glb", "sha256_glb": sha, "uid": rec["id"],
              "title": title,
              "author": "generated: Infinigen (princeton-vl/infinigen, Princeton University, BSD-3-Clause)",
              "source_url": url,
              "via": f"generated for WenArt_RUN with Infinigen {tag} ({INFINIGEN_REPO} @{commit[:7]}, BSD-3-Clause)",
              "attribution": f"\"{title}\": generated with Infinigen {tag} ({INFINIGEN_REPO}, BSD-3-Clause, "
                             "Copyright (c) 2023 Princeton University) for WenArt_RUN"})
    styles, style_note = _styles([], "the factory")
    e.update({"styles": styles, "style_note": style_note})
    e.update(_mesh_fields(m))
    e["generated"] = {"prompt": f"Infinigen {rec['dotted']} (factory seed {rec['seed']}, spawn index {rec['seed']})",
                      "image_sha256": None, "model": f"{INFINIGEN_REPO} {rec['dotted']}", "revision": commit,
                      "seed": int(rec["seed"]), "generator": "infinigen",
                      "export": "infinigen.tools.export (obj, procedural materials baked), converted to GLB by "
                                "Blender 5.2"}
    e.update(_bed_fields(ftype, kind))
    e["growth"] = {"pod": "P4", "list": "plan_infinigen.json", "factory": rec["factory"], "class": rec["class"]}
    e["audit"] = pending_audit(checked_utc)
    return e


def hssd_entry(cand: dict, m: dict, sha: str, checked_utc: str, rules: Optional[dict] = None,
               footprint: Optional[dict] = None, pbr: Optional[dict] = None) -> dict:
    """A ``catalog_library.json`` entry of an HSSD candidate (``wenart.assets.hssd.candidate_records``; Milestone
    13): ``source: hssd``, the CC BY-NC 4.0 licence fields (``hssd.entry_fields``: ``licence_flag: non_commercial``,
    ``commercial_safe: false``), units known (metres: the Floorplanner products are modelled at real size; the box of
    ``glbmesh.measure`` is what the catalogue carries), the front from the geometric rule of the type (the metadata's
    ``front`` column is empty for most objects: confidence medium at best, the audit's vision answer names it), the
    ``pbr_maps`` record when measured, an L-sofa's ``chaise_side`` from the footprint, and ``audit: pending`` until
    the P2 audit decides."""
    from wenart.assets import hssd as H
    from wenart.assets import objaverse as OV
    ftype, kind = cand["type"], cand.get("kind") or "furniture"
    hid = cand.get("hssd_id") or cand["id"][len(H.UID_PREFIX):]
    uid = H.UID_PREFIX + hid
    front, conf, note = front_of(ftype, m.get("stats"), rules=rules)
    title = source_text(cand.get("title")) or f"HSSD object {hid[:8]}"     # fix round after P6b: entities decoded
    hint = styles_hint(title)
    styles, style_note = _styles(hint, "the product title")
    e = {"id": uid, **_kind_type(kind, ftype), "source": "hssd", **H.entry_fields(), "name": title}
    e.update(frame_fields(m, front, conf, note))
    w, d, h = e["bbox_m"]
    e.update({"unit_scale": 1.0, "unit_note": f"units known (metres, HSSD aligned.dims {', '.join(f'{v:.3g}' for v in cand.get('dims_m') or [])}): "
                                              f"{w:.3g} x {d:.3g} x {h:.3g} m measured",
              "units_known": True, "styles": styles, "style_note": style_note,
              "glb": f"models/hssd/{uid}.glb", "sha256_glb": sha, "uid": uid, "title": title,
              "author": "the HSSD authors (Floorplanner product models; 3dlg-hcvc / Meta FAIR)",
              # the Hub's file page is /blob/<revision>/<path> (/tree/ answers 404 for a file; checked 15 Oct 2026)
              "source_url": f"{H.PAGE_URL}/blob/{H.REVISION}/{cand.get('path') or H.object_path(hid)}",
              "via": f"{H.DATASET_NAME} (CC BY-NC 4.0), {H.PAGE_URL}",
              "attribution": H.attribution(title, hid)})
    e.update(_mesh_fields(m))
    if pbr:
        e["pbr_maps"] = dict(pbr)
    if kind == "furniture" and ftype in OV.FOOTPRINT_TYPES:
        e["chaise_side"], e["chaise_note"] = OV.chaise_side(footprint, front, OV.load_config())
    e.update(_bed_fields(ftype, kind))
    e["hssd"] = {"id": hid, "synset": cand.get("synset"), "found_in": cand.get("found_in"), "multi": cand.get("multi"),
                 "articulated": cand.get("articulated"), "bin": cand.get("bin"), "demand": cand.get("demand"),
                 "projects": list(cand.get("projects") or []), "repo": H.REPO_ID, "revision": H.REVISION,
                 "path": cand.get("path") or H.object_path(hid)}
    e["growth"] = {"pod": "P2", "milestone": "m13", "list": "candidates_hssd.json", "bin": cand.get("bin"),
                   "fits_caps": cand.get("fits_caps")}
    e["audit"] = dict(pending_audit(checked_utc), reasons=[PENDING_REASON_M13])
    return e


# --------------------------------------------------------------------------
# Catalogue copies
# --------------------------------------------------------------------------

def _is_decor(e: dict) -> bool:
    return e.get("kind") == "decor" or str(e.get("type", "")).startswith("decor_")


def add_entries(doc: dict, entries: list[dict]) -> dict:
    """``doc`` with ``entries`` added to its ``entries`` / ``decor`` sections (an entry with the same id is replaced
    in place); returns ``{"added", "replaced"}``."""
    stats = {"added": 0, "replaced": 0}
    for e in entries:
        section = "decor" if _is_decor(e) else "entries"
        rows = doc.setdefault(section, [])
        for i, old in enumerate(rows):
            if isinstance(old, dict) and old.get("id") == e["id"]:
                rows[i] = e
                stats["replaced"] += 1
                break
        else:
            rows.append(e)
            stats["added"] += 1
    return stats


def build_copies(library: dict, polyhaven: dict, entries: list[dict]) -> tuple[dict, dict, dict]:
    """``(library copy, polyhaven copy, stats)``: the repo's catalogues (deep copies) with the new entries (Poly Haven
    ones into ``catalog.json``, every other source into ``catalog_library.json``), the GSO dataset record and the
    growth note; both validated (``CatalogError`` when an entry is malformed)."""
    from wenart.furniture import catalog as C
    lib = json.loads(json.dumps(library))
    ph = json.loads(json.dumps(polyhaven))
    ph_new = [e for e in entries if e["source"] == "polyhaven"]
    stats = {"library": add_entries(lib, [e for e in entries if e["source"] != "polyhaven"]),
             "polyhaven": add_entries(ph, ph_new)}
    # a type that gets Poly Haven models is no longer parametric in catalog.json (validate: a type is library or
    # parametric); the merged catalogue already had no parametric entry for it when catalog_library.json has models
    library_types = {e["type"] for e in lib.get("entries") or [] if not e.get("parametric")}
    gained = {e["type"] for e in ph_new if not _is_decor(e)}
    replaced = sorted(t for t in gained if any(p.get("parametric") and p.get("type") == t for p in ph["entries"]))
    if replaced:
        ph["entries"] = [p for p in ph["entries"] if not (p.get("parametric") and p.get("type") in replaced)]
        note = (f"Milestone 12 pod P4: the parametric entries of {', '.join(replaced)} gave way to the new Poly Haven "
                "models (a type is either library or parametric; catalog_library.json has models of "
                f"{', '.join(t for t in replaced if t in library_types) or 'none'} of them, so the merged catalogue "
                "had no parametric entry for those already)")
        ph.setdefault("notes", []).append(note)
    stats["parametric_replaced"] = replaced
    if any(e["source"] == "gso" for e in entries):
        srcs = list(lib.get("sources") or [])
        if "gso" not in srcs:
            lib["sources"] = srcs + ["gso"]
        lib.setdefault("datasets", {})["gso"] = dict(GSO_DATASET)
    if any(e["source"] == "hssd" for e in entries):
        from wenart.assets import hssd as H
        srcs = list(lib.get("sources") or [])
        if "hssd" not in srcs:
            lib["sources"] = srcs + ["hssd"]
        lib.setdefault("datasets", {})["hssd"] = dict(H.DATASET)
    m13 = any((e.get("growth") or {}).get("milestone") == "m13" for e in entries)
    for doc in (lib, ph):
        notes = doc.setdefault("notes", [])
        if GROWTH_NOTE not in notes:
            notes.append(GROWTH_NOTE)
        if m13 and GROWTH_NOTE_M13 not in notes:
            notes.append(GROWTH_NOTE_M13)
    C.validate(lib, complete=False)
    C.validate(ph, complete=True)
    C.merge(ph, lib)
    return lib, ph, stats


def apply_vision_fields(doc: dict, answers: dict, ids: set, hints: Optional[dict] = None) -> dict:
    """Styles and the bed's ``has_mattress`` of the new entries (``ids``) from their pass 1 answers (``answers``:
    ``{id: answer}``): styles = the source's hint (``hints[id]``, or the entry's styles unless they are the
    ``neutral`` placeholder) plus at most ``STYLE_MAX`` styles of the answer; nothing named -> neutral. Returns
    ``{"styled", "beds"}``."""
    from wenart.furniture import catalog as C
    allowed = set(C.style_values())
    out = {"styled": 0, "beds": 0}
    for section in ("entries", "decor"):
        for e in doc.get(section) or []:
            if not isinstance(e, dict) or e.get("id") not in ids:
                continue
            a = answers.get(e["id"])
            if not a:
                continue
            hint = list((hints or {}).get(e["id"]) or [s for s in e.get("styles") or [] if s != "neutral"])
            seen = [s for s in a.get("styles") or [] if s in allowed and s != "neutral"][:STYLE_MAX]
            styles = sorted(set(hint) | set(seen)) or ["neutral"]
            e["styles"] = styles
            e["style_note"] = (f"P4 growth: source hint {hint or 'none'}; the audit's vision answer (pass 1) names "
                               f"{seen or 'none'}" + ("" if styles != ["neutral"] else ": neutral"))
            out["styled"] += 1
            if e.get("type") in C.BED_TYPES and isinstance(a.get("has_bedding"), bool) and not e.get("bed_frame"):
                e["has_mattress"] = bool(a["has_bedding"])
                e["bed_note"] = (f"P4 growth: has_mattress {e['has_mattress']} from the vision answer (bedding "
                                 f"{'seen' if a['has_bedding'] else 'not seen'})")
                out["beds"] += 1
    return out
