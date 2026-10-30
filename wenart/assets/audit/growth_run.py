"""The steps of pod P4, the library growth (docs/milestone12.md §6.4 D24, §14.3; ``scripts/jobs/library_growth.sh``):
``python -m wenart.assets growth run <step> [options]``.

    ingest --source polyhaven|abo|gso   the approved ids only (``growth.approved``: the ingest gate), downloads with
                                        retries and a size limit, files present are kept (resume)
    gso-licence                         unpack the GSO archives safely, CC BY 4.0 evidence per object
                                        (``growth_gso.py``), keep / drop with the reason
    infinigen-list --repo R             the asset factories of the clone, matched to the plan
    infinigen-plan                      the jobs still to do (``growth_infinigen.plan_jobs``); prints ``todo N``
    convert --source gso|infinigen      OBJ -> GLB in our Blender (``convert_blender.py``) into
                                        ``<assets>/models/gso|generated/<uid>.glb``
    catalogue                           every new model measured (``glbmesh.py``), its entry built
                                        (``growth_entries.py``), the catalogue COPIES written to
                                        ``<p4>/audit/catalogue/`` (never ``wenart/furniture/``), ``new_ids.json``
    ask [--plan-only]                   one vLLM server session: the new models (pass 1 and 2) and pass 2 of the P3
                                        models still pending (``cli.second_pass_ids``); answers reused
    vision-fields                       styles and a bed's mattress from the pass 1 answers into the copies
    pending                             the decision of the P3 pending models (P3's answers) into the copies
    gaps                                the gap report over the whole library (the copies' audit status)
    preview --blender B                 audit sheets of the generated models without a type of ours
    report                              ``growth.md`` / ``growth.json``: per source approved, downloaded, converted,
                                        dropped (with reasons), catalogued and the audit's outcome; GSO evidence;
                                        Infinigen commit, factories and jobs; step timings

Folders (all on the volume): ``--growth`` (default ``/workspace/library-growth``: downloads, extracted archives,
Infinigen exports, ``report/`` = the small files the job copies to ``$WENART_RESULTS/library/growth``), ``--assets``
(``/workspace/assets``: the models where the fit and the Blender build find them), ``--p4`` (``/workspace/
library-audit/p4``: the P4 audit, ``audit/`` copied to ``$WENART_RESULTS/library/audit/p4``), ``--p3`` (P3's audit
root, ``/workspace/library-audit``), ``--lists`` (the committed lists and approvals, ``results/library``).

Milestone 13 (docs/milestone13.md §5.1 phase 2, §13.1 track T7, §13.6 pod P2; ``scripts/jobs/library_growth.sh``):

    demands                             the drawn demands of the committed buildings and the size grid
                                        (``demands.py``) -> ``report/demands.json``, ``size_grid.json``
    size-grid                           the coverage per licence mode on the catalogue copies (or the repo's
                                        catalogues before the growth) and the demand gap report
                                        (``coverage.json``, ``gaps_demand.md``) plus the pick plan per source
    speed-probe                         the first ABO downloads timed (``growth.speed_probe`` settings) ->
                                        ``speed.json`` with the MB/s and the pick counts the budget allows
    ingest --source hssd                the HSSD objects of ``approved_hssd.json`` (picks of the committed list; the
                                        gate: HF_TOKEN from the environment, a 403 skips the step with a clear line)
                                        into ``<growth>/hssd/`` and ``<assets>/models/hssd/<uid>.glb``
    ingest --source ambientcg           the shell sets (2K-JPG) through ``wenart.assets.fetch.fetch_texture``
    ingest --source abo|polyhaven --m13 the Milestone 13 lists (``candidates_<source>_m13.json``,
                                        ``approved_<source>_m13.json``); Poly Haven at 2K (``--size 2k``)
    catalogue                           also the HSSD entries (``growth_entries.hssd_entry``) and the 2K relink of
                                        the Poly Haven entries whose 2K glTF is present
    report                              also the counts per source, per licence flag and per licence mode

Milestone 13 round 3 (docs/milestone13.md §14.6, after pod P2):

    ingest --source polyhaven           a glTF size the API does not offer: the next lower one (2k -> 1k, recorded
                                        as ``size`` / ``size_requested`` / ``size_reason``); no glTF at all or an
                                        unknown id: ``dropped`` with the reason (data: rc 0); only network errors
                                        (after ``web``'s own tries) and code errors fail the step
    refetch                             the current file of every catalogue entry waiting for a re-audit (an asset
                                        republished upstream, ``reaudit_entries``); older files kept beside
    catalogue [--only hssd]             the re-audit entries whose current file is on the volume join new_ids.json;
                                        ``--only`` (GROWTH_ONLY=hssd, pod P2b) builds those sources alone, every
                                        other entry as the repo's catalogues have it, the earlier ids kept
    preview                             the vegetation previews (``gltf``) too: P2 stopped at ``KeyError: 'glb'``;
                                        every failure is printed with its reason and recorded in ``preview.json``
    any step                            an unexpected error prints ``growth run <step>: FAILED: <type>: <reason>``
                                        as its last line (and the traceback), rc 1

3D Warehouse layer (23 Oct 2026, the user's request; ``scripts/jobs/library_growth.sh`` ``GROWTH_ONLY=3dwh``):

    ingest --source 3dwh                the user's zip (``approved_3dwh.json``: the whole zip, the ingest gate) from
                                        ``--library`` (``zip/``, downloaded by the job): its GLBs extracted safely to
                                        ``glb/<uid>.glb`` (``members.json``: the member paths), every model typed
                                        from its names, measured, its unit and up axis
                                        chosen and fixed (``wenart.assets.warehouse.process``, ``--workers``
                                        processes) into ``<assets>/models/3dwh/<uid>.glb``; ``ingest_3dwh.json``
                                        (every record), ``3dwh_review.json`` (unmapped, dropped, failed, not fitting
                                        any real size), ``3dwh_extras.json`` (trees, doors, windows)
    catalogue [--only 3dwh]             the furniture and decor entries (``growth_entries.warehouse_entry``); the
                                        trees, doors and windows as previews (no catalogue type yet)
    preview                             also the 3D Warehouse previews (up to 3 Blender workers)
    report                              also the 3D Warehouse counts

HSSD doors and windows (28 Oct 2026, the user: "I want better doors inside the house and the outside ... find the
best models"; ``scripts/jobs/library_growth.sh`` ``GROWTH_ONLY=openings``):

    ingest --source hssd_openings       the picks of ``candidates_hssd_openings.json`` (``approved_hssd_openings.json``;
                                        ``wenart.assets.hssd_openings``: the Floorplanner door and window series of
                                        ``objects/openings/`` and the named products), the HSSD gate and download
                                        of ``ingest --source hssd``, into ``<assets>/models/hssd/<uid>.glb``
    catalogue --only hssd_openings      their ``extras`` entries (``growth_entries.hssd_opening_entry``: kind
                                        ``opening``, the series, the table's kind, operation and categories)
    vision-fields                       also a door's or window's quality (``audit_quality``) and the opening
                                        question's answer (``opening_vision``: role, operation, leaves, glazing,
                                        leaf, handle side; ``ask.version_openings``)
    second-look [--summary]             the pending models the vision audit doubted (``second_look_ids``) join the
                                        new ones in ``audit_ids.json`` (render, code, ask pass 1 and 2, decide,
                                        write); the P3 ones go to ``pending``; ``--summary``: their status after

Exit codes: 0 done, 1 something failed or nothing to do (the record says which), 2 server error, 3 deadline.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from argparse import Namespace
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from wenart.assets.audit import AUDIT_DIR, DEFAULT_OUT, EXIT_DEADLINE, EXIT_NOTHING, EXIT_OK, EXIT_SERVER, HERE, \
    GROWTH_DIR

CONVERT_SCRIPT = HERE / "convert_blender.py"
DRIVER = HERE / "infinigen_driver.py"
PH_SIZE = "1k"            # what wenart.furniture.fit.fetch_models resolves (fetch_model(size="1k")): see P4.md
RETRIES = 3


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path) -> Optional[dict]:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def write_json(path, doc) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def report_dir(args) -> Path:
    return Path(args.report or Path(args.growth) / "report")


def audit_dir(args) -> Path:
    return Path(args.p4) / AUDIT_DIR


def copies(args) -> tuple[Path, Path]:
    cat = audit_dir(args) / "catalogue"
    return cat / "catalog_library.json", cat / "catalog.json"


def list_names(source: str, m13: bool = False) -> tuple[str, str]:
    """``(candidates file, approval source key)`` of a source: the Milestone 12 names, or with ``m13`` the
    Milestone 13 lists of ABO and Poly Haven (``candidates_abo_m13.json`` / ``approved_abo_m13.json``); HSSD and
    ambientCG have one list each."""
    if source == "infinigen":
        return "plan_infinigen.json", "infinigen"
    if source == "hssd_openings":                # 28 Oct 2026: the HSSD doors and windows (wenart.assets.hssd_openings)
        return "candidates_hssd_openings.json", "hssd_openings"
    if m13 and source in ("abo", "polyhaven"):
        return f"candidates_{source}_m13.json", f"{source}_m13"
    return f"candidates_{source}.json", source


def candidates(args, source: str) -> dict:
    name, _key = list_names(source, bool(getattr(args, "m13", False)))
    return read_json(Path(args.lists) / GROWTH_DIR / name) or {}


def m13_candidates(args, source: str) -> dict:
    """The Milestone 13 list of a source whatever ``--m13`` says (the catalogue step reads both)."""
    name, _key = list_names(source, True)
    return read_json(Path(args.lists) / GROWTH_DIR / name) or {}


def deadline_of(args) -> Optional[float]:
    from wenart.assets.audit.render import deadline_of as d
    return d(getattr(args, "deadline", None))


def left_s(deadline: Optional[float]) -> float:
    return float("inf") if deadline is None else deadline - time.time()


# --------------------------------------------------------------------------
# Downloads
# --------------------------------------------------------------------------

def size_limit(size_mb: Optional[float], default_mb: float = 120.0) -> float:
    """Bytes a download may take: the listed size + 25 % (at least + 5 MB), else ``default_mb``."""
    if not size_mb:
        return default_mb * 1e6
    return max(float(size_mb) * 1.25, float(size_mb) + 5.0) * 1e6


def download_retry(url: str, dest: Path, max_bytes: float, retries: int = RETRIES, fetch: Optional[Callable] = None,
                   sleep: Callable = time.sleep) -> int:
    """``fetch(url, dest, max_bytes)`` (default ``abo.download``: ``.part`` then rename) with retries (2, 4 s);
    a file over the limit or an HTTP 4xx is not tried again. Returns the attempts."""
    import urllib.error
    from wenart.assets import abo as AB
    fetch = fetch or (lambda u, d, m: AB.download(u, d, max_bytes=m))
    for attempt in range(1, retries + 1):
        try:
            fetch(url, dest, max_bytes)
            return attempt
        except AB.TooLarge:
            raise
        except urllib.error.HTTPError as exc:
            if 400 <= exc.code < 500 or attempt == retries:
                raise
        except (urllib.error.URLError, OSError, TimeoutError):
            if attempt == retries:
                raise
        sleep(2 ** attempt)
    return retries


def _parallel(fn: Callable, items: list, workers: int) -> list:
    with ThreadPoolExecutor(max_workers=max(1, int(workers))) as pool:
        return list(pool.map(fn, items))


def ingest_polyhaven(args, ids: list, cands: dict, fetch_model: Optional[Callable] = None,
                     sleep: Optional[Callable] = None) -> list:
    """The approved Poly Haven models at ``--size`` (Milestone 13 round 3, docs/milestone13.md §14.6): an asset
    without a glTF at that size takes the next lower size the file table offers (``models.pick_gltf_size``; the
    record keeps ``size`` = the size used, ``size_requested`` and ``size_reason``); an asset without any glTF
    (``models.NoGltf``) or unknown to the API (404) is ``dropped`` with the reason: data, not a failure of the step.
    Network errors (after ``web``'s own tries) are tried ``RETRIES`` times here; they and code errors are
    ``failed`` (the step's rc 1). ``fetch_model`` / ``sleep`` are injectable (tests)."""
    from wenart.assets import fetch as F
    from wenart.assets import models as M
    from wenart.assets import web as W
    fetch_model = fetch_model or M.fetch_model
    sleep = sleep or time.sleep
    out = []
    for aid in ids:
        t0 = time.time()
        rec = {"id": aid, "ok": False, "size": args.size}
        for attempt in range(1, RETRIES + 1):
            try:
                e = fetch_model(aid, Path(args.assets), size=args.size, size_fallback=True)
                rec.update(ok=True, gltf=e["files"]["gltf"], sha256=e.get("sha256") or {}, attempts=attempt,
                           size=e.get("resolution") or args.size,
                           bytes=sum((Path(args.assets) / r).stat().st_size for r in e["files"].values()))
                if e.get("resolution_note"):
                    rec.update(size_requested=args.size, size_reason=e["resolution_note"])
                rec.pop("error", None)
                break
            except (M.NoGltf, F.AssetNotFound) as exc:     # data: dropped with the reason, never tried again
                rec.update(dropped=True, reason=f"{type(exc).__name__}: {exc.args[0] if exc.args else exc}")
                break
            except (W.NetworkError, W.HTTPStatusError, W.ChecksumError) as exc:
                rec["error"] = f"{type(exc).__name__}: {exc}"
                if attempt < RETRIES:
                    sleep(2 ** attempt)
            except Exception as exc:  # noqa: BLE001 - a code or file error: recorded, the step fails
                rec["error"] = f"{type(exc).__name__}: {exc}"
                break
        rec["seconds"] = round(time.time() - t0, 1)
        out.append(rec)
        state = "ok" + (f" at {rec['size']} ({rec['size_reason']})" if rec.get("size_reason") else "") if rec["ok"] \
            else (f"dropped: {rec['reason']}" if rec.get("dropped") else f"FAILED: {rec.get('error')}")
        print(f"growth polyhaven: {aid} {state}", flush=True)
    return out


def ingest_files(rows: list, workers: int, fetch: Optional[Callable] = None) -> list:
    """``rows`` = ``[{"id", "url", "dest", "max_bytes"}]``: downloads in parallel, a present file is kept (``.part``
    then rename: a present file is complete)."""
    def one(r):
        dest = Path(r["dest"])
        rec = {"id": r["id"], "url": r["url"], "path": str(dest), "ok": False}
        t0 = time.time()
        try:
            if dest.is_file():
                rec["kept"] = True
            else:
                rec["attempts"] = download_retry(r["url"], dest, r["max_bytes"], fetch=fetch)
            rec.update(ok=True, bytes=dest.stat().st_size, sha256=sha256_file(dest))
        except Exception as exc:  # noqa: BLE001
            rec["error"] = f"{type(exc).__name__}: {exc}"
        rec["seconds"] = round(time.time() - t0, 1)
        print(f"growth download: {r['id']} {'ok' if rec['ok'] else rec['error']}", flush=True)
        return rec
    return _parallel(one, rows, workers)


def ingest_name(args) -> str:
    """The ingest record's name: ``ingest_<source>.json``, ``ingest_<source>_m13.json`` for the M13 lists."""
    _name, key = list_names(args.source, bool(getattr(args, "m13", False)))
    return f"ingest_{key}.json"


def ingest_hssd(args, ids: list, cands: dict) -> tuple[list, dict]:
    """The HSSD objects (``wenart.assets.hssd.download``) into ``<growth>/hssd/`` (the repo layout), then copied to
    ``<assets>/models/hssd/<uid>.glb`` (kept when present; nothing deleted). ``(records, download record)``."""
    from wenart.assets import hssd as H
    dest = Path(args.growth) / "hssd"
    listing = {c.get("hssd_id") or i[len(H.UID_PREFIX):]: c.get("path") for i, c in cands.items() if c.get("path")}
    rec = H.download(ids, dest, args.token_env, max_workers=args.workers, listing=listing)
    have = H.present([c.get("hssd_id") or i[len(H.UID_PREFIX):] for i, c in cands.items() if i in ids], dest)
    records = []
    for uid in ids:
        hid = (cands.get(uid) or {}).get("hssd_id") or uid[len(H.UID_PREFIX):]
        row = {"id": uid, "hssd_id": hid, "ok": False}
        src = have.get(hid)
        if src is None:
            row["error"] = "not downloaded" + (f": {rec['gate']['reason']}" if rec.get("skipped") and rec.get("gate")
                                               else (f": {rec['error']}" if rec.get("error") else ""))
            records.append(row)
            continue
        target = Path(args.assets) / "models" / "hssd" / f"{uid}.glb"
        if not target.is_file() or target.stat().st_size != src.stat().st_size:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
        else:
            row["kept"] = True
        row.update(ok=True, glb=f"models/hssd/{uid}.glb", path=str(target), bytes=target.stat().st_size,
                   sha256=sha256_file(target))
        records.append(row)
    return records, rec


def _process_all(fn: Callable, jobs: list, workers: int) -> list:
    """``fn(job)`` for every job, in ``workers`` processes (1: in this process); results in job order."""
    if workers <= 1 or len(jobs) <= 1:
        return [fn(j) for j in jobs]
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(fn, jobs, chunksize=4))


WH_KEEP = ("id", "rel", "title", "ok", "group", "kind", "type", "dropped", "error")


def ingest_3dwh(args) -> int:
    """The 3D Warehouse layer (module docstring): extract, list, type, fix; ``ingest_3dwh.json``,
    ``3dwh_review.json``, ``3dwh_extras.json``. Unmapped and dropped models are data (rc 0); rc 1 when the approval
    or the files are missing or a model failed unexpectedly."""
    from collections import Counter

    from wenart.assets import warehouse as WH
    t0 = time.time()
    rep = report_dir(args)
    try:
        ok_doc = WH.approval(args.lists)
    except PermissionError as exc:
        print(f"growth ingest 3dwh refused: {exc}")
        write_json(rep / "ingest_3dwh.json", {"source": WH.SOURCE, "refused": str(exc)})
        return EXIT_NOTHING
    root = Path(args.library)
    # glb/ (23 Oct 2026, after the first pod): the models as <uid>.glb with members.json; the raw/ tree that pod
    # started (member paths on the file system: a name passed 255 bytes) stays on the volume, unused
    zpath, raw = root / "zip" / WH.ZIP_NAME, root / "glb"
    extract = None
    zip_rec = {"path": str(zpath), "present": zpath.is_file(), "expected_bytes": WH.ZIP_BYTES,
               "bytes": zpath.stat().st_size if zpath.is_file() else None}
    if zpath.is_file():
        if zip_rec["bytes"] != WH.ZIP_BYTES:
            print(f"growth ingest 3dwh: {zpath} has {zip_rec['bytes']} bytes, the Drive file {WH.ZIP_BYTES}: an "
                  "incomplete download is not extracted")
            write_json(rep / "ingest_3dwh.json", {"source": WH.SOURCE, "zip": zip_rec, "error": "zip size"})
            return EXIT_NOTHING
        extract = WH.extract(zpath, raw)
        print(f"growth ingest 3dwh: extracted {extract['extracted']}, kept {extract['kept']} of {extract['glb']} GLBs "
              f"({extract['bytes'] / 1e9:.2f} GB); other files {extract['other'] or 'none'}", flush=True)
    elif not raw.is_dir():
        print(f"growth ingest 3dwh: neither {zpath} nor {raw}: run the download first")
        write_json(rep / "ingest_3dwh.json", {"source": WH.SOURCE, "zip": zip_rec, "error": "no zip"})
        return EXIT_NOTHING
    listing = WH.list_glbs(raw)
    cache = Path(args.growth) / WH.SOURCE / "fix"
    jobs = [{"id": r["id"], "rel": r["rel"], "file": r["file"], "raw": str(raw), "assets": str(args.assets),
             "cache": str(cache)} for r in listing]
    records = _process_all(WH.process, jobs, max(1, int(args.workers)))
    ok = [r for r in records if r.get("ok")]
    unmapped = [r for r in records if not r.get("ok") and not r.get("mapped", True)]
    dropped = [r for r in records if not r.get("ok") and r.get("dropped") and r.get("mapped", True)]
    failed = [r for r in records if not r.get("ok") and r.get("error")]
    not_fitting = [r for r in ok if not (r.get("choice") or {}).get("fits")]
    by_group = Counter(r.get("group") or "?" for r in ok)
    by_type = Counter(f"{r.get('kind')}:{r.get('type')}" for r in ok)
    extras = [r for r in ok if r.get("kind") in WH.EXTRA_KINDS]
    write_json(rep / "ingest_3dwh.json",
               {"source": WH.SOURCE, "approved_by": ok_doc.get("approved_by"),
                "approved_utc": ok_doc.get("approved_utc"), "rule": ok_doc.get("rule"), "zip": zip_rec,
                "extract": extract, "listed": len(listing), "ok": len(ok),
                "unmapped": len(unmapped), "dropped": len(dropped), "failed": len(failed),
                "not_fitting": len(not_fitting), "units": dict(Counter((r.get("choice") or {}).get("unit")
                                                                          for r in ok)),
                "up_fixed": sum(1 for r in ok if (r.get("choice") or {}).get("up_fix")),
                "by_group": dict(sorted(by_group.items())), "by_type": dict(sorted(by_type.items())),
                "fix_version": WH.FIX_VERSION, "seconds": round(time.time() - t0, 1), "records": records})
    write_json(rep / "3dwh_review.json",
               {"kind": "library_3dwh_review", "written_utc": now_utc(),
                "unmapped": [{"id": r["id"], "rel": r["rel"], "title": r.get("title")} for r in unmapped],
                "dropped": [{k: r.get(k) for k in WH_KEEP} for r in dropped],
                "failed": [{k: r.get(k) for k in WH_KEEP} for r in failed],
                "not_fitting": [{"id": r["id"], "rel": r["rel"], "type": r.get("type"), "raw_box_m": r.get("raw_box_m"),
                                 "error": (r.get("choice") or {}).get("error")} for r in not_fitting]})
    write_json(rep / "3dwh_extras.json",
               {"kind": "library_3dwh_extras", "written_utc": now_utc(),
                "note": "the extras (trees, doors, windows, objects): catalogued in the extras section and audited; the "
                        "later hooks scale openings to the drawn openings and pick trees by crown size",
                "models": [{k: r.get(k) for k in ("id", "rel", "title", "kind", "type", "glb", "box_m", "crown_m",
                                                  "height_m")} | {"fits": (r.get("choice") or {}).get("fits")}
                           for r in extras]})
    print(f"growth ingest 3dwh: {len(listing)} GLB(s): {len(ok)} fixed ({dict(by_group)}), {len(unmapped)} unmapped "
          f"(review list), {len(dropped)} dropped, {len(failed)} FAILED; {len(not_fitting)} fit no real size "
          f"({round(time.time() - t0)} s)")
    for r in failed[:20]:
        print(f"growth ingest 3dwh: {r['rel']} failed: {r.get('error')}")
    return EXIT_OK if not failed and listing else EXIT_NOTHING


def ingest_ambientcg(args, ids: list, cands: dict) -> list:
    """The ambientCG shell sets (``fetch.fetch_texture``: the 2K-JPG zip unpacked into ``<assets>/textures/<id>/``,
    recorded in the assets manifest; present sets are kept)."""
    from wenart.assets import fetch as F
    out = []
    for aid in ids:
        t0 = time.time()
        row = {"id": aid, "ok": False, "size": args.size if args.size != PH_SIZE else "2k"}
        try:
            entry = F.fetch_texture(aid, Path(args.assets), size=row["size"], source="ambientcg")
            row.update(ok=True, files=entry.get("files"), sha256=entry.get("sha256"))
        except Exception as exc:  # noqa: BLE001 - recorded
            row["error"] = f"{type(exc).__name__}: {exc}"
        row["seconds"] = round(time.time() - t0, 1)
        print(f"growth ambientcg: {aid} {'ok' if row['ok'] else row['error']}", flush=True)
        out.append(row)
    return out


def cmd_ingest(args) -> int:
    from wenart.assets.audit import growth as G
    if args.source == "3dwh":
        return ingest_3dwh(args)
    t0 = time.time()
    _name, key = list_names(args.source, bool(getattr(args, "m13", False)))
    try:
        doc = G.approved(key, args.lists)
    except PermissionError as exc:
        print(f"growth ingest {key} refused: {exc}")
        write_json(report_dir(args) / ingest_name(args), {"source": args.source, "refused": str(exc)})
        return EXIT_NOTHING
    ids = list(doc["ids"])
    cands = {c["id"]: c for c in candidates(args, args.source).get("candidates") or []}
    extra: dict = {}
    if args.source in ("hssd", "hssd_openings"):
        records, dl = ingest_hssd(args, ids, cands)
        extra = {"download": {k: v for k, v in dl.items() if k not in ("ok", "missing")},
                 "gate": dl.get("gate"), "skipped": dl.get("skipped")}
    elif args.source == "ambientcg":
        records = ingest_ambientcg(args, ids, cands)
    elif args.source == "polyhaven":
        if getattr(args, "m13", False):
            # Milestone 13: the Milestone 12 furniture is fetched again at 2K by the same step (the catalogue step
            # relinks the entries whose 2K file is present); its approval and list are the M12 ones
            try:
                old = G.approved("polyhaven", args.lists)
                ids += [i for i in old.get("ids") or [] if i not in ids]
                cands.update({c["id"]: c for c in (read_json(Path(args.lists) / GROWTH_DIR / "candidates_polyhaven.json")
                                                   or {}).get("candidates") or [] if c["id"] not in cands})
                extra["m12_ids_refetched"] = len(old.get("ids") or [])
            except PermissionError:
                pass
        records = ingest_polyhaven(args, ids, cands)
    elif args.source == "abo":
        from wenart.assets import abo as AB
        base = AB.load_config()["dataset"]["base_url"]
        rows = [{"id": i, "url": f"{base}/3dmodels/original/{cands[i]['glb']}",
                 "dest": Path(args.assets) / "models" / "abo" / f"{i}.glb",
                 "max_bytes": size_limit(cands[i].get("size_mb"))} for i in ids if i in cands]
        records = ingest_files(rows, args.workers)
        for r in records:
            r["glb"] = f"models/abo/{r['id']}.glb"
        records += [{"id": i, "ok": False, "error": "not in candidates_abo.json"} for i in ids if i not in cands]
    elif args.source == "gso":
        from wenart.assets.audit import growth_gso as GS
        rev = (candidates(args, "gso").get("query") or {}).get("revision") or "main"
        rows = [{"id": i, "url": GS.HF_RESOLVE.format(repo=GS.HF_REPO, rev=rev, file=cands[i]["file"]),
                 "dest": Path(args.growth) / "gso" / "zips" / cands[i]["file"],
                 "max_bytes": size_limit(cands[i].get("size_mb"))} for i in ids if i in cands]
        records = ingest_files(rows, args.workers)
        records += [{"id": i, "ok": False, "error": "not in candidates_gso.json"} for i in ids if i not in cands]
    else:
        print(f"growth ingest: {args.source} has no download (Infinigen models are generated)")
        return EXIT_NOTHING
    ok = sum(1 for r in records if r["ok"])
    dropped = sum(1 for r in records if not r["ok"] and r.get("dropped"))
    failed = len(records) - ok - dropped
    write_json(report_dir(args) / ingest_name(args),
               {"source": args.source, "list": key, "approved_by": doc.get("approved_by"),
                "approved_utc": doc.get("approved_utc"), "ids_from": doc.get("ids_from"),
                "approved": len(ids), "ok": ok, "failed": failed, "dropped": dropped,
                "size": args.size if args.source in ("polyhaven", "ambientcg") else None,
                "seconds": round(time.time() - t0, 1), "records": records, **extra})
    print(f"growth ingest {key}: {ok} of {len(ids)} ok" + (f", {dropped} dropped (no file to fetch: data, reasons in "
                                                           f"{ingest_name(args)})" if dropped else "")
          + (f", {failed} FAILED" if failed else ""))
    bad = [r for r in records if not r["ok"] and not r.get("dropped")] if not extra.get("skipped") else []
    for r in bad[:20]:
        print(f"growth ingest {key}: {r['id']} failed: {r.get('error')}")
    if len(bad) > 20:
        print(f"growth ingest {key}: ... {len(bad) - 20} more failures in {ingest_name(args)}")
    if extra.get("skipped"):
        # the last line: the job's steps.tsv takes it as the reason of the step
        print(f"growth ingest {key}: SKIPPED: {(extra.get('gate') or {}).get('reason')}")
        return EXIT_NOTHING
    # Milestone 13 round 3: a Poly Haven asset without a glTF (dropped) is data, not a failure of the step
    return EXIT_OK if failed == 0 else EXIT_NOTHING



# --------------------------------------------------------------------------
# Milestone 13: demands, size grid, coverage, speed probe
# --------------------------------------------------------------------------

def cmd_demands(args) -> int:
    """The drawn demands of the committed buildings and their size grid (``demands.py``) -> ``report/demands.json``
    and ``size_grid.json`` (pure: the same files the session commits under results/library/growth/)."""
    from wenart.assets.audit import demands as D
    dem = D.drawn_demands()
    grid = D.size_grid(dem)
    stamp = args.checked_utc or now_utc()
    # the building paths relative to the repo (the file is committed: no path of one machine in it)
    buildings = {k: (v.relative_to(D.REPO).as_posix() if v.is_relative_to(D.REPO) else str(v))
                 for k, v in D.BUILDING_PATHS.items()}
    write_json(report_dir(args) / "demands.json",
               {"kind": "library_demands", "written_utc": stamp, "projects": list(D.PROJECTS),
                "buildings": buildings, "pieces": sum(d["count"] for d in dem),
                "rows": len(dem), "summary": D.summary(dem), "demands": dem})
    write_json(report_dir(args) / "size_grid.json",
               {"kind": "library_size_grid", "written_utc": stamp, "types": len(grid),
                "bins_demanded": sum(1 for t in grid for b in grid[t] if b["demand"]), "grid": grid})
    print(f"growth demands: {sum(d['count'] for d in dem)} pieces in {len(dem)} rows of {len(D.summary(dem))} types; "
          f"{sum(1 for t in grid for b in grid[t] if b['demand'])} bins demanded")
    return EXIT_OK


def coverage_doc(catalog, dem: list, grid: dict, cfg: dict, stamp: str, scope: str) -> dict:
    from wenart.assets.audit import demands as D
    from wenart.furniture import catalog as C
    cov = {m: D.coverage(catalog, dem, m) for m in C.LICENCE_MODES}
    min_n = int((cfg.get("growth") or {}).get("min_models_per_bin", D.MIN_MODELS_PER_BIN))
    gaps = D.demand_gaps(grid, cov, min_n)
    bins = [(t, b) for t in grid for b in grid[t] if b["demand"]]
    covered = {m: sum(1 for t, b in bins if cov[m][t][b["bin"]] >= min_n) for m in cov}
    return {"kind": "library_demand_coverage", "written_utc": stamp, "scope": scope, "min_models_per_bin": min_n,
            "bins_demanded": len(bins), "bins_covered": covered, "gap_rows": len(gaps),
            "by_mode": cov, "gaps": gaps}


def cmd_size_grid(args) -> int:
    """The coverage of the demand bins per licence mode on the catalogue copies when the catalogue step wrote them,
    else the repo's catalogues (before the growth), the demand gap report (``gaps.demand_gaps_markdown``) and the
    pick plan per source (the committed lists' counts against the targets of ``audit.yaml growth``)."""
    from wenart.assets.audit import demands as D
    from wenart.assets.audit import gaps as GP
    from wenart.assets.audit import load_config
    from wenart.furniture import catalog as C
    cfg = load_config()
    stamp = args.checked_utc or now_utc()
    dem = D.drawn_demands()
    grid = D.size_grid(dem)
    lib_path, ph_path = copies(args)
    if lib_path.is_file() and ph_path.is_file():
        catalog, scope = C.load(ph_path, library=lib_path), "catalogue copies after the catalogue step"
    else:
        catalog, scope = C.load(), "the repo's catalogues (before the growth)"
    doc = coverage_doc(catalog, dem, grid, cfg, stamp, scope)
    plan = {}
    g = cfg.get("growth") or {}
    for source, target_key in (("hssd", "hssd_target"), ("abo", "abo_target")):
        lst = m13_candidates(args, source) if source == "abo" else candidates(args, source)
        picked = [c for c in (lst.get("candidates") or []) if c.get("pick", True)]
        plan[source] = {"picked": len(picked), "target": g.get(target_key),
                        "size_mb": round(sum(c.get("size_mb") or 0 for c in picked), 1)}
    for source in ("polyhaven", "ambientcg"):
        lst = m13_candidates(args, source) if source == "polyhaven" else candidates(args, source)
        picked = [c for c in (lst.get("candidates") or []) if c.get("pick", True)]
        plan[source] = {"picked": len(picked), "size_mb": round(sum(c.get("size_mb") or 0 for c in picked), 1)}
    doc["pick_plan"] = plan
    write_json(report_dir(args) / "coverage.json", doc)
    (report_dir(args) / "gaps_demand.md").write_text(
        GP.demand_gaps_markdown(doc["gaps"], "Library gaps by drawn demand", f"Scope: {scope}; written {stamp}; "
                                f"a bin is a gap below {doc['min_models_per_bin']} usable models in a licence mode."),
        encoding="utf-8")
    print(f"growth size-grid: {doc['bins_demanded']} bins demanded, covered {doc['bins_covered']}, "
          f"{doc['gap_rows']} gap rows ({scope}); picks {json.dumps(plan)}")
    return EXIT_OK


def plan_picks(mb_s: float, cfg_growth: dict, list_counts: dict, mean_mb: dict) -> dict:
    """The pick counts the measured speed allows (pure): per source the picked count of its list, cut to the lower
    bound of its target when the budget (``speed_probe.budget_minutes`` at ``mb_s``) does not hold every list's
    bytes; below ``min_mb_s`` every source takes its lower bound."""
    sp = cfg_growth.get("speed_probe") or {}
    budget_mb = float(sp.get("budget_minutes", 60)) * 60.0 * max(float(mb_s), 0.0)
    slow = float(mb_s) < float(sp.get("min_mb_s", 5.0))
    need = sum(list_counts.get(s, 0) * float(mean_mb.get(s, 0.0)) for s in list_counts)
    out = {"mb_s": round(float(mb_s), 2), "budget_mb": round(budget_mb, 1), "need_mb": round(need, 1), "slow": slow,
           "fits_budget": need <= budget_mb, "picks": {}}
    for source, n in list_counts.items():
        target = cfg_growth.get(f"{source}_target")
        lo = int(target[0]) if isinstance(target, (list, tuple)) and target else n
        take = n if (need <= budget_mb and not slow) else min(n, lo)
        out["picks"][source] = {"listed": n, "take": take, "mb": round(take * float(mean_mb.get(source, 0.0)), 1)}
    return out


def cmd_speed_probe(args) -> int:
    """The first ABO GLBs of the Milestone 13 list timed (``growth.speed_probe.files``; present files are kept and
    not timed) -> ``report/speed.json`` with the MB/s and the pick counts (``plan_picks``). Runs before the ingests;
    its downloads are the ingest's (same paths), so nothing is fetched twice."""
    from wenart.assets import abo as AB
    from wenart.assets.audit import load_config
    cfg = (load_config().get("growth") or {})
    sp = cfg.get("speed_probe") or {}
    n_files = int(sp.get("files", 8))
    lst = m13_candidates(args, "abo")
    cands = [c for c in (lst.get("candidates") or []) if c.get("pick", True) and c.get("glb")]
    base = AB.load_config()["dataset"]["base_url"]
    rows = []
    for c in cands:
        dest = Path(args.assets) / "models" / "abo" / f"{c['id']}.glb"
        if dest.is_file():
            continue
        rows.append({"id": c["id"], "url": f"{base}/3dmodels/original/{c['glb']}", "dest": dest,
                     "max_bytes": size_limit(c.get("size_mb"))})
        if len(rows) >= n_files:
            break
    t0 = time.time()
    records = ingest_files(rows, args.workers) if rows else []
    secs = max(time.time() - t0, 1e-3)
    got = sum(r.get("bytes", 0) for r in records if r.get("ok"))
    mb_s = got / 1e6 / secs if rows else float(sp.get("assume_mb_s", 99.0))
    counts = {"hssd": sum(1 for c in (candidates(args, "hssd").get("candidates") or []) if c.get("pick", True)),
              "abo": len(cands)}
    from wenart.assets import hssd as H
    mean = {"hssd": H.FILE_SIZE_MB["mean"],
            "abo": (sum(c.get("size_mb") or 20.8 for c in cands) / len(cands)) if cands else 20.8}
    plan = plan_picks(mb_s, cfg, counts, mean)
    doc = {"kind": "library_growth_speed", "written_utc": now_utc(), "files": len(rows), "bytes": got,
           "seconds": round(secs, 1), "measured": bool(rows), "workers": args.workers, "records": records, **plan}
    write_json(report_dir(args) / "speed.json", doc)
    print(f"growth speed-probe: {len(rows)} file(s), {got / 1e6:.1f} MB in {secs:.1f} s = {mb_s:.1f} MB/s"
          f"{'' if rows else ' (assumed: every probe file was present)'}; picks {json.dumps(plan['picks'])}")
    return EXIT_OK

# --------------------------------------------------------------------------
# GSO licence and conversion
# --------------------------------------------------------------------------

def cmd_gso_licence(args) -> int:
    from wenart.assets.audit import growth_gso as GS
    ing = read_json(report_dir(args) / "ingest_gso.json") or {}
    cands = {c["id"]: c for c in candidates(args, "gso").get("candidates") or []}
    rev = (candidates(args, "gso").get("query") or {}).get("revision")
    root = Path(args.growth) / "gso"
    rows, failed = [], []
    for r in ing.get("records") or []:
        if not r.get("ok") or r["id"] not in cands:
            failed.append({"id": r["id"], "kept": False, "reason": f"not downloaded: {r.get('error')}"})
            continue
        name = GS.name_of(r["id"])
        folder = root / "objects" / name
        marker = folder / ".extracted.json"
        mark = read_json(marker)
        if not mark or mark.get("zip_sha256") != r.get("sha256"):
            try:
                if folder.exists():
                    shutil.rmtree(folder)
                info = GS.safe_extract(Path(r["path"]), folder)
                write_json(marker, dict(info, zip_sha256=r.get("sha256")))
            except (GS.ArchiveError, OSError) as exc:
                failed.append({"id": r["id"], "kept": False, "reason": f"archive refused: {exc}"})
                continue
        rows.append((cands[r["id"]], folder, name))

    def fuel(row):
        cand, _folder, name = row
        if args.no_fuel:
            return None
        cache = root / "fuel" / f"{name}.json"
        hit = read_json(cache)
        if hit and hit.get("record") is not None:
            return hit["record"], hit["url"], None
        rec, url, err = GS.fetch_fuel(name)
        if rec is not None:
            write_json(cache, {"record": rec, "url": url, "fetched_utc": now_utc()})
        return rec, url, err
    fuels = _parallel(fuel, rows, args.workers)
    records = [GS.licence_record(c, f, rev, fz) for (c, f, _n), fz in zip(rows, fuels)] + failed
    kept = [r for r in records if r.get("kept")]
    slim = []
    for r in records:
        s = {k: v for k, v in r.items() if k != "layout"}
        if r.get("layout"):
            s["files"] = r["layout"]["files"]
        slim.append(s)
    write_json(root / "licences.json", {"records": records})
    write_json(report_dir(args) / "gso_licences.json",
               {"kind": "gso_licence_evidence", "checked_utc": now_utc(), "fuel_api": not args.no_fuel,
                "kept": len(kept), "dropped": len(records) - len(kept), "rule": GS.RULE, "records": slim})
    lines = ["# GSO licence evidence (pod P4)", "", f"Kept {len(kept)} of {len(records)}: CC BY 4.0 confirmed per "
             "object (growth_gso.py); the others are dropped and listed.", "",
             "| id | kept | reason | evidence |", "|---|---|---|---|"]
    for r in records:
        ev = "; ".join(e.get("file") or e.get("url") or "" for e in r.get("evidence") or [])
        lines.append(f"| {r['id']} | {'yes' if r.get('kept') else 'no'} | {r.get('reason', '').replace('|', '/')} | "
                     f"{ev} |")
    (report_dir(args) / "gso_licences.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"growth gso-licence: {len(kept)} kept, {len(records) - len(kept)} dropped")
    return EXIT_OK if records else EXIT_NOTHING


def run_blender_jobs(blender: str, jobs: list, work: Path, name: str, timeout: float) -> dict:
    """Run ``convert_blender.py`` on ``jobs``; ``{id: result}`` (a missing result = the job did not run)."""
    work.mkdir(parents=True, exist_ok=True)
    result = work / f"convert_{name}_result.json"
    result.unlink(missing_ok=True)
    jp = work / f"convert_{name}_jobs.json"
    write_json(jp, {"jobs": jobs, "result": str(result)})
    cmd = [str(blender), "-b", "--factory-startup", "--python-exit-code", "1", "--python", str(CONVERT_SCRIPT), "--",
           str(jp)]
    with open(work / f"convert_{name}.log", "w", encoding="utf-8") as fh:
        try:
            subprocess.call(cmd, stdout=fh, stderr=subprocess.STDOUT, timeout=max(60.0, timeout))
        except subprocess.TimeoutExpired:
            fh.write("\nconvert: stopped by the time limit\n")
    return (read_json(result) or {}).get("results") or {}


def convert_targets(args) -> tuple[list, dict]:
    """``(jobs, meta)`` of the models to convert (GSO kept objects, Infinigen exports), each with the cache path
    ``models/<gso|generated>/<uid>.glb``."""
    from wenart.assets.audit import growth_gso as GS
    from wenart.assets.audit import growth_infinigen as GI
    work = Path(args.growth) / args.source / "glb"
    if args.source == "gso":
        recs = (read_json(Path(args.growth) / "gso" / "licences.json") or {}).get("records") or []
        jobs = GS.convert_jobs(recs, work)
        meta = {r["uid"]: {"id": r["id"], "cache": f"models/gso/{r['uid']}.glb"} for r in recs if r.get("kept")}
        return jobs, meta
    plan = read_json(Path(args.growth) / "infinigen" / "jobs.json") or {}
    jobs, meta = [], {}
    for j in plan.get("jobs") or []:
        folder = Path(j["folder"])
        if GI.job_state(folder) != "done":
            continue
        res = read_json(folder / "result.json") or {}
        jobs.append({"id": j["id"], "src": res["obj"], "dst": str(work / f"{j['id']}.glb"),
                     "axes": [["Y", "NEGATIVE_Z"], ["Z", "Y"]], "expect_dims": res.get("dims"), "texture": None})
        meta[j["id"]] = {"id": j["id"], "cache": f"models/generated/{j['id']}.glb", "obj_sha256": None}
    return jobs, meta


def cmd_convert(args) -> int:
    t0 = time.time()
    jobs, meta = convert_targets(args)
    rpath = report_dir(args) / f"convert_{args.source}.json"
    prev = (read_json(rpath) or {}).get("results") or {}
    for j in jobs:
        src_sha = sha256_file(j["src"]) if Path(j["src"]).is_file() else None
        meta[j["id"]]["src_sha256"] = src_sha
    todo = []
    for j in jobs:
        p = prev.get(j["id"]) or {}
        cache = Path(args.assets) / meta[j["id"]]["cache"]
        if p.get("ok") and p.get("src_sha256") == meta[j["id"]]["src_sha256"] and cache.is_file() \
                and sha256_file(cache) == p.get("sha256"):
            continue
        todo.append(j)
    results = dict(prev)
    if todo:
        timeout = min(1800.0, left_s(deadline_of(args)))
        got = run_blender_jobs(args.blender, todo, Path(args.growth) / args.source / "work", args.source, timeout)
        for j in todo:
            r = dict(got.get(j["id"]) or {"ok": False, "error": "the conversion did not run (time limit or Blender "
                                                                  "stopped)"})
            if r.get("ok"):
                cache = Path(args.assets) / meta[j["id"]]["cache"]
                cache.parent.mkdir(parents=True, exist_ok=True)
                part = cache.with_name(cache.name + ".part")
                shutil.copyfile(j["dst"], part)
                part.replace(cache)
                r.update(sha256=sha256_file(cache), glb=meta[j["id"]]["cache"])
            r["src_sha256"] = meta[j["id"]]["src_sha256"]
            results[j["id"]] = r
    keep = {j["id"] for j in jobs}
    results = {k: v for k, v in results.items() if k in keep}
    ok = sum(1 for r in results.values() if r.get("ok"))
    write_json(rpath, {"source": args.source, "converted": ok, "failed": len(results) - ok, "redone": len(todo),
                       "seconds": round(time.time() - t0, 1), "results": results})
    print(f"growth convert {args.source}: {ok} of {len(jobs)} ok ({len(todo)} converted now)")
    return EXIT_OK if ok == len(jobs) else EXIT_NOTHING


# --------------------------------------------------------------------------
# Infinigen
# --------------------------------------------------------------------------

def ig_root(args) -> Path:
    return Path(args.growth) / "infinigen"


def cmd_infinigen_list(args) -> int:
    from wenart.assets.audit import growth_infinigen as GI
    repo = Path(args.repo)
    listing = (repo / GI.LISTING).read_text(encoding="utf-8") if (repo / GI.LISTING).is_file() else ""
    facs = GI.factories_of(listing, GI.scan_sources(repo))
    write_json(ig_root(args) / "factories.json", {"tag": GI.TAG, "commit": GI.COMMIT, "count": len(facs),
                                                  "listing": GI.LISTING, "factories": facs})
    print(f"growth infinigen-list: {len(facs)} factories at {GI.COMMIT[:7]}")
    return EXIT_OK if facs else EXIT_NOTHING


def cmd_infinigen_plan(args) -> int:
    from wenart.assets.audit import growth as G
    from wenart.assets.audit import growth_infinigen as GI
    try:
        approved = G.approved("infinigen", args.lists)["ids"]
    except PermissionError as exc:
        print(f"growth infinigen-plan refused: {exc}")
        return EXIT_NOTHING
    fdoc = read_json(ig_root(args) / "factories.json")
    plan = GI.plan_jobs(candidates(args, "infinigen"), approved, (fdoc or {}).get("factories"), ig_root(args))
    write_json(ig_root(args) / "jobs.json", plan)
    print(f"growth infinigen-plan: todo {len(plan['todo'])}, done {len(plan['done'])}, failed {len(plan['failed'])}"
          + (f", missing factories {plan['missing']}" if plan["missing"] else ""))
    return EXIT_OK


# --------------------------------------------------------------------------
# Catalogue copies
# --------------------------------------------------------------------------

# The fields every cached measurement must carry: ``pbr`` joined ``glbmesh.measure`` in Milestone 13; a record of the
# Milestone 12 measurement has none, so the entry of a model measured then got no ``pbr_maps`` on pod P2
# (``abo_B07124WCZY``: tests/gpu/test_library.py, docs/milestone13.md §14.6) -> measured again.
MEASURE_FIELDS = ("pbr",)


def measured(path: Path, key: str, cache_dir: Path, rules: dict) -> dict:
    """``glbmesh.measure`` of a model, cached by ``key`` (the file hashes) under ``cache_dir``; a cached record
    without the ``MEASURE_FIELDS`` of the current measurement is measured again."""
    from wenart.assets.audit import glbmesh as GM
    safe = hashlib.sha256(str(path).encode("utf-8")).hexdigest()[:16]
    cpath = cache_dir / f"{safe}.json"
    hit = read_json(cpath)
    if hit and hit.get("key") == key and all(f in (hit.get("m") or {}) for f in MEASURE_FIELDS):
        return hit["m"]
    m = GM.measure(path, rules=rules)
    write_json(cpath, {"key": key, "path": str(path), "m": m})
    return m


def _validate_one(e: dict) -> Optional[str]:
    from wenart.assets import warehouse as WH
    from wenart.furniture import catalog as C
    if e.get("kind") in WH.EXTRA_KINDS:              # 23 Oct 2026: the extras section
        try:
            WH.validate_extra(e)
        except C.CatalogError as exc:
            return str(exc)
        return None
    doc = {"entries": [], "decor": [e]} if (e.get("kind") == "decor" or str(e["type"]).startswith("decor_")) \
        else {"entries": [e]}
    try:
        C.validate(doc, complete=False)
    except C.CatalogError as exc:
        return str(exc)
    return None


def new_entries(args, stamp: str, only: Optional[set] = None) -> tuple[list, list, list, dict]:
    """``(entries, dropped, previews, hints)`` of every ingested or converted new model; ``only`` limits them to
    those sources (``GROWTH_ONLY=hssd``: the HSSD layer alone, every other entry stays as the repo has it)."""
    from wenart.assets import abo as AB
    from wenart.assets import objaverse as OV
    from wenart.assets.audit import glbmesh as GM
    from wenart.assets.audit import growth as G
    from wenart.assets.audit import growth_entries as GE
    from wenart.assets.audit import growth_infinigen as GI
    rules = OV.load_config().get("front_rules") or {}
    cache = Path(args.growth) / "measure"
    known = G.known_types()
    entries, dropped, previews, hints = [], [], [], {}
    assets = Path(args.assets)

    def drop(source, iid, why):
        dropped.append({"source": source, "id": iid, "reason": why})

    def guard(source, iid, fn):
        try:
            return fn()
        except (GM.MeshError, OSError, KeyError, ValueError) as exc:
            drop(source, iid, f"not catalogued: {type(exc).__name__}: {exc}")
            return None
    def wanted(source: str) -> bool:
        return only is None or source in only
    # Poly Haven (the Milestone 12 list and the Milestone 13 one: furniture at 2K and vegetation); a record of the
    # M13 ingest whose id is a catalogue model outside the M13 list is the 2K re-fetch of a Milestone 12 model:
    # relinked by cmd_catalogue, never re-made as a pending entry
    cands = {c["id"]: c for c in candidates(args, "polyhaven").get("candidates") or []}
    m13_ph = {c["id"]: c for c in m13_candidates(args, "polyhaven").get("candidates") or []}
    cands.update(m13_ph)
    ph_records = [(r, False) for r in (read_json(report_dir(args) / "ingest_polyhaven.json") or {}).get("records")
                  or []] if wanted("polyhaven") else []
    ph_records += [(r, True) for r in (read_json(report_dir(args) / "ingest_polyhaven_m13.json") or {}).get("records")
                   or []] if wanted("polyhaven") else []
    from wenart.assets.audit import items as I
    ph_doc = I.read_json(I.POLYHAVEN_PATH) or {}
    existing_ph = {e.get("id") for sec in ("entries", "decor") for e in ph_doc.get(sec) or [] if isinstance(e, dict)}
    seen_ph: set = set()
    for r, from_m13 in ph_records:
        if r["id"] in seen_ph:
            continue
        seen_ph.add(r["id"])
        if from_m13 and r["id"] in existing_ph and r["id"] not in m13_ph:
            continue
        if not r.get("ok"):
            drop("polyhaven", r["id"], f"no glTF to fetch on Poly Haven: {r.get('reason')}" if r.get("dropped")
                 else f"not downloaded: {r.get('error')}")
            continue
        c = cands.get(r["id"])
        if c is not None and c.get("kind") == "vegetation":
            previews.append({"id": r["id"], "source": "polyhaven", "kind": "vegetation", "type": c.get("type"),
                             "gltf": r.get("gltf"), "note": "vegetation model for wenart.blender.vegetation (T6): "
                                                            "no furniture catalogue entry"})
            continue
        if c is None or c["type"] not in known:
            drop("polyhaven", r["id"], "no catalogue type")
            continue
        key = json.dumps(r.get("sha256") or {}, sort_keys=True)

        def ph(r=r, c=c, key=key):
            m = measured(assets / r["gltf"], key, cache, rules)
            e = GE.polyhaven_entry(c, m, r["gltf"], (r.get("sha256") or {}).get("gltf"), r.get("size", PH_SIZE),
                                   stamp, rules)
            if r.get("size_reason"):
                e["resolution_note"] = f"growth ingest: {r['size_reason']}"
            if r["id"] in m13_ph:          # Milestone 13 list: marked as growth_entries marks the M13 ABO and HSSD
                e["growth"] = dict(e.get("growth") or {}, milestone="m13", list="candidates_polyhaven_m13.json")
            return e
        e = guard("polyhaven", r["id"], ph)
        if e:
            entries.append(e)
            hints[e["id"]] = [s for s in e["styles"] if s != "neutral"]
    # ABO (the Milestone 12 list and the Milestone 13 size-grid list)
    acfg = AB.load_config()
    cands = {c["id"]: c for c in candidates(args, "abo").get("candidates") or []}
    cands.update({c["id"]: c for c in m13_candidates(args, "abo").get("candidates") or []})
    abo_records = (read_json(report_dir(args) / "ingest_abo.json") or {}).get("records") or []
    abo_records += (read_json(report_dir(args) / "ingest_abo_m13.json") or {}).get("records") or []
    abo_records = abo_records if wanted("abo") else []
    for r in abo_records:
        c = cands.get(r["id"])
        if not r.get("ok"):
            drop("abo", r["id"], f"not downloaded: {r.get('error')}")
            continue
        if c is None or c["type"] not in known:
            drop("abo", r["id"], f"no catalogue type for {(c or {}).get('type', '?')} (downloaded, kept on the volume; "
                                 "headboards wait for a bed-frame type)")
            continue

        def abo(r=r, c=c):
            path = assets / r["glb"]
            m = measured(path, r["sha256"], cache, rules)
            fp = None
            if c["type"] in OV.FOOTPRINT_TYPES:
                fp = OV.footprint_occupancy(GM.triangles_of(path), m["bbox_min_m"], m["bbox_max_m"])
            e = GE.abo_entry(c, m, r["sha256"], acfg, stamp, footprint=fp)
            if m.get("pbr"):
                e["pbr_maps"] = dict(m["pbr"])
            if c.get("bin"):
                e["growth"] = dict(e.get("growth") or {}, milestone="m13", bin=c.get("bin"),
                                   fits_caps=c.get("fits_caps"), list="candidates_abo_m13.json")
            return e
        e = guard("abo", r["id"], abo)
        if e:
            entries.append(e)
            hints[e["id"]] = [s for s in e["styles"] if s != "neutral"]
    # HSSD (Milestone 13, relaxed licence mode: CC BY-NC 4.0)
    cands = {c["id"]: c for c in candidates(args, "hssd").get("candidates") or []}
    hssd_records = (read_json(report_dir(args) / "ingest_hssd.json") or {}).get("records") or []
    for r in hssd_records if wanted("hssd") else []:
        c = cands.get(r["id"])
        if not r.get("ok"):
            drop("hssd", r["id"], f"not downloaded: {r.get('error')}")
            continue
        if c is None or c["type"] not in known:
            drop("hssd", r["id"], f"no catalogue type for {(c or {}).get('type', '?')}")
            continue

        def hssd(r=r, c=c):
            path = assets / r["glb"]
            m = measured(path, r["sha256"], cache, rules)
            fp = None
            if c["type"] in OV.FOOTPRINT_TYPES:
                fp = OV.footprint_occupancy(GM.triangles_of(path), m["bbox_min_m"], m["bbox_max_m"])
            return GE.hssd_entry(c, m, r["sha256"], stamp, rules, footprint=fp, pbr=m.get("pbr"))
        e = guard("hssd", r["id"], hssd)
        if e:
            entries.append(e)
            hints[e["id"]] = [s for s in e["styles"] if s != "neutral"]
    # HSSD doors and windows (28 Oct 2026, the user: "find the best models"): extras entries of kind opening
    cands = {c["id"]: c for c in candidates(args, "hssd_openings").get("candidates") or []}
    op_records = (read_json(report_dir(args) / "ingest_hssd_openings.json") or {}).get("records") or []
    for r in op_records if wanted("hssd_openings") else []:
        c = cands.get(r["id"])
        if not r.get("ok"):
            drop("hssd_openings", r["id"], f"not downloaded: {r.get('error')}")
            continue
        if c is None or c.get("type") not in ("door", "window"):
            drop("hssd_openings", r["id"], f"not a door or window of candidates_hssd_openings.json: "
                                           f"{(c or {}).get('type', '?')}")
            continue
        e = guard("hssd_openings", r["id"], lambda r=r, c=c: GE.hssd_opening_entry(
            c, measured(assets / r["glb"], r["sha256"], cache, rules), r["sha256"], stamp, rules))
        if e:
            entries.append(e)
            hints[e["id"]] = [s for s in e["styles"] if s != "neutral"]
    # 3D Warehouse (23 Oct 2026: the user's zip, relaxed licence mode only); trees, doors, windows and objects are
    # entries of the extras section, audited like the rest (the user: "keep these ones also")
    from wenart.assets import warehouse as WH
    wh_records = ((read_json(report_dir(args) / "ingest_3dwh.json") or {}).get("records") or []) \
        if wanted("3dwh") else []
    for r in wh_records:
        if not r.get("ok"):
            drop("3dwh", r["id"], f"{r.get('rel')}: " + str(r.get("dropped") or r.get("error") or "not fixed"))
            continue
        if r.get("type") not in known and r.get("kind") not in WH.EXTRA_KINDS:
            drop("3dwh", r["id"], f"no catalogue type for {r.get('type')}")
            continue

        def wh(r=r):
            path = assets / r["glb"]
            m = measured(path, r["sha256"], cache, rules)
            fp = None
            if r["type"] in OV.FOOTPRINT_TYPES:
                fp = OV.footprint_occupancy(GM.triangles_of(path), m["bbox_min_m"], m["bbox_max_m"])
            return GE.warehouse_entry(r, m, stamp, rules, footprint=fp)
        e = guard("3dwh", r["id"], wh)
        if e:
            entries.append(e)
            hints[e["id"]] = [x for x in e["styles"] if x != "neutral"]
    # GSO
    gso_lic = (read_json(Path(args.growth) / "gso" / "licences.json") or {}).get("records") or [] \
        if wanted("gso") else []
    lic = {r["uid"]: r for r in gso_lic if r.get("uid")}
    for r in gso_lic:
        if not r.get("kept"):
            drop("gso", r["id"], f"licence not confirmed: {r.get('reason')}")
    gso_conv = (read_json(report_dir(args) / "convert_gso.json") or {}).get("results") or {} \
        if wanted("gso") else {}
    for uid, res in gso_conv.items():
        rec = lic.get(uid)
        if not res.get("ok") or rec is None:
            drop("gso", (rec or {}).get("id", uid), f"not converted: {res.get('error')}")
            continue
        e = guard("gso", rec["id"], lambda res=res, rec=rec: GE.gso_entry(
            rec, measured(assets / res["glb"], res["sha256"], cache, rules), res["sha256"], stamp, rules))
        if e:
            entries.append(e)
            hints[e["id"]] = []
    # Infinigen
    plan = read_json(ig_root(args) / "jobs.json") or {} if wanted("infinigen") else {}
    jobs = {j["id"]: j for j in plan.get("jobs") or []}
    conv = (read_json(report_dir(args) / "convert_infinigen.json") or {}).get("results") or {}
    for jid, j in jobs.items():
        res = conv.get(jid)
        if j.get("state") != "done" and not (res or {}).get("ok"):
            drop("infinigen", jid, f"not generated ({j.get('state')}): "
                                   f"{(read_json(Path(j['folder']) / 'result.json') or {}).get('error', 'not run')}")
            continue
        if not (res or {}).get("ok"):
            drop("infinigen", jid, f"not converted: {(res or {}).get('error', 'not run')}")
            continue
        if not j.get("type"):
            previews.append({"id": jid, "factory": j["factory"], "class": j.get("class"), "glb": res["glb"],
                             "sha256": res["sha256"]})
            continue
        e = guard("infinigen", jid, lambda j=j, res=res: GE.infinigen_entry(
            j, measured(assets / res["glb"], res["sha256"], cache, rules), res["sha256"], GI.COMMIT, GI.TAG, stamp,
            rules))
        if e:
            entries.append(e)
            hints[e["id"]] = []
    good = []
    for e in entries:
        why = _validate_one(e)
        if why:
            drop(source_key(e), e["id"], f"entry refused by catalog.validate: {why}")
        else:
            good.append(e)
    return good, dropped, previews, hints


def source_key(e: dict) -> str:
    """The growth source of a new entry (Infinigen models are ``source: generated``)."""
    return "infinigen" if (e.get("generated") or {}).get("generator") == "infinigen" else e["source"]


def relink_polyhaven_2k(doc: dict, assets: Path, records: list) -> int:
    """Milestone 13: the existing Poly Haven entries whose 2K glTF was fetched (``ingest_polyhaven_m13.json``
    records of the catalogue's own ids) point to the 2K file (``gltf``, ``resolution``, ``sha256_gltf``); the 1K file
    stays on the volume. Returns the number relinked."""
    by_id = {r["id"]: r for r in records if r.get("ok") and r.get("gltf")}
    n = 0
    for section in ("entries", "decor"):
        for e in doc.get(section) or []:
            r = by_id.get(e.get("id")) if isinstance(e, dict) else None
            if not r or e.get("gltf") == r["gltf"] or not (assets / r["gltf"]).is_file():
                continue
            e["gltf_1k"] = e.get("gltf")
            e["gltf"] = r["gltf"]
            e["resolution"] = r.get("size") or "2k"
            if (r.get("sha256") or {}).get("gltf"):
                e["sha256_gltf"] = r["sha256"]["gltf"]
            e["resolution_note"] = (f"M13 growth: {e['resolution'].upper()} glTF fetched by pod P2 (docs/milestone13.md"
                                    " §5.1 phase 2); the 1K file stays as gltf_1k"
                                    + (f"; {r['size_reason']}" if r.get("size_reason") else ""))
            n += 1
    return n


REAUDIT = "reaudit"          # audit[REAUDIT]: the record of an entry whose model file changed upstream


def reaudit_entries(*docs: Optional[dict]) -> list[dict]:
    """The catalogue entries waiting for a new audit of a changed model file: ``audit.status`` pending with an
    ``audit.reaudit`` record (an asset republished upstream: its box was measured again from the current file and
    the next audit judges it again; docs/milestone13.md §14.6: ``vintage_wooden_drawer_01``, round 3)."""
    return [e for doc in docs for sec in ("entries", "decor") for e in (doc or {}).get(sec) or []
            if isinstance(e, dict) and e.get("id") and (e.get("audit") or {}).get("status") == "pending"
            and isinstance((e.get("audit") or {}).get(REAUDIT), dict)]


def file_current(e: dict, assets: Path) -> tuple[bool, str]:
    """``(current, why)``: the model file on the volume is the one the entry was measured on. Poly Haven: the asset
    manifest's entry (every file of the glTF with its sha256 on disk, ``models._cached_ok``) has the entry's
    ``sha256_gltf`` at its ``resolution``; a library GLB: its sha256 is the entry's ``sha256_glb``."""
    from wenart.assets import fetch as F
    from wenart.assets import models as M
    if e.get("source") == "polyhaven":
        want = e.get("sha256_gltf")
        if not want:
            return False, "the entry has no sha256_gltf"
        man = (F.load_manifest(Path(assets)).get("models") or {}).get(e["id"])
        if not man:
            return False, f"not in the asset manifest of {assets}: run growth run refetch"
        if M._cached_ok(Path(assets), man, e.get("resolution") or PH_SIZE, expect_sha256_gltf=want):
            return True, "current"
        got = (man.get("sha256") or {}).get("gltf") or "none"
        return False, f"the files on the volume (gltf sha256 {got[:12]}...) are not the entry's ({want[:12]}...): " \
                      "run growth run refetch"
    rel, want = e.get("glb"), e.get("sha256_glb")
    if not rel or not want:
        return False, "the entry has no glb / sha256_glb"
    path = Path(assets) / rel
    if not path.is_file():
        return False, f"{rel} is not on the volume"
    got = sha256_file(path)
    return (True, "current") if got == want else (False, f"{rel} has sha256 {got[:12]}..., the entry {want[:12]}...")


def cmd_refetch(args) -> int:
    """Fetch again the current file of every repo catalogue entry waiting for a re-audit (``reaudit_entries``): a
    Poly Haven model through ``models.fetch_model(expect_sha256_gltf=...)`` (the files of the older publication are
    kept beside, never deleted); a library GLB is only checked (its pod writes it). ``report/refetch.json`` says per
    entry whether the file now on the volume is the one the entry was measured on (rc 1 when one is not)."""
    from wenart.assets import models as M
    from wenart.assets.audit import items as I
    rows = []
    for e in reaudit_entries(I.read_json(I.LIBRARY_PATH), I.read_json(I.POLYHAVEN_PATH)):
        row = {"id": e["id"], "source": e.get("source"), "reason": (e["audit"][REAUDIT] or {}).get("reason")}
        try:
            if e.get("source") == "polyhaven":
                m = M.fetch_model(e["id"], Path(args.assets), size=e.get("resolution") or PH_SIZE,
                                  expect_sha256_gltf=e.get("sha256_gltf"))
                row.update(sha256_gltf=(m.get("sha256") or {}).get("gltf"), superseded=m.get("superseded") or [])
            row["current"], row["state"] = file_current(e, Path(args.assets))
        except Exception as exc:  # noqa: BLE001 - recorded with the reason
            row.update(current=False, state=f"FAILED: {type(exc).__name__}: {exc}")
        rows.append(row)
        print(f"growth refetch: {e['id']}: {row['state']}", flush=True)
    write_json(report_dir(args) / "refetch.json", {"kind": "library_refetch", "written_utc": now_utc(),
                                                   "rows": rows})
    bad = [r["id"] for r in rows if not r["current"]]
    print(f"growth refetch: {len(rows)} entr{'y' if len(rows) == 1 else 'ies'} waiting for a re-audit, "
          f"{len(rows) - len(bad)} current" + (f"; not current: {bad}" if bad else ""))
    return EXIT_NOTHING if bad else EXIT_OK


def cmd_catalogue(args) -> int:
    """The catalogue copies with the new entries (``new_entries``) and ``new_ids.json`` (the ids the audit steps
    take). ``--only hssd`` (``GROWTH_ONLY=hssd``): only those sources are (re)built; every other entry stays as the
    repo's catalogues have it (P2's audited entries), ``new_ids.json`` keeps the earlier ids as ``kept_ids`` and the
    earlier previews, ``catalogue.json`` the earlier drops of the other sources (nothing disappears from the
    records). Both modes add the entries waiting for a re-audit whose current file is on the volume (``refetch``)."""
    from collections import Counter

    from wenart.assets.audit import growth_entries as GE
    from wenart.assets.audit import items as I
    stamp = args.checked_utc or now_utc()
    only = {x.strip() for x in str(getattr(args, "only", None) or "").split(",") if x.strip()} or None
    entries, dropped, previews, hints = new_entries(args, stamp, only)
    lib, ph, stats = GE.build_copies(I.read_json(I.LIBRARY_PATH), I.read_json(I.POLYHAVEN_PATH), entries)
    if only is None or "polyhaven" in only:
        ph2k = (read_json(report_dir(args) / "ingest_polyhaven_m13.json") or {}).get("records") or []
        stats["polyhaven_relinked_2k"] = relink_polyhaven_2k(ph, Path(args.assets), ph2k)
    lib_path, ph_path = copies(args)
    write_json(lib_path, lib)
    write_json(ph_path, ph)
    ids = [e["id"] for e in entries]
    reaudit, waiting = [], []
    for e in reaudit_entries(lib, ph):
        if e["id"] in ids:
            continue
        current, why = file_current(e, Path(args.assets))
        if current:
            reaudit.append(e["id"])
            hints[e["id"]] = [x for x in e.get("styles") or [] if x != "neutral"]
        else:
            waiting.append({"id": e["id"], "reason": why})
    ids += reaudit
    by_source = Counter(source_key(e) for e in entries)
    # 28 Oct 2026: the growth list of each new entry (the HSSD doors and windows share the source hssd)
    by_list = Counter((e.get("growth") or {}).get("list") or source_key(e) for e in entries)
    doc = {"ids": ids, "by_source": dict(by_source), "hints": hints, "previews": previews, "written_utc": stamp,
           "reaudit": reaudit, "reaudit_waiting": waiting}
    report = {"added": len(entries), "by_source": dict(by_source),
              "by_list": {k[len("candidates_"):-len(".json")] if k.startswith("candidates_") else k: v
                          for k, v in by_list.items()},
              "dropped": dropped, "previews": previews,
              "reaudit": reaudit, "reaudit_waiting": waiting}
    if only is not None:
        prev = new_ids(args)
        before = (set(prev.get("ids") or []) | set(prev.get("kept_ids") or [])) - set(ids)
        prev_rep = read_json(report_dir(args) / "catalogue.json") or {}
        # 23 Oct 2026: the earlier previews of the other sources stay and this run's previews join them (before,
        # --only replaced this run's previews with the earlier ones: the 3D Warehouse trees, doors and windows)
        earlier = [x for x in prev.get("previews") or [] if x.get("source") not in only]
        earlier_rep = [x for x in prev_rep.get("previews") or prev.get("previews") or [] if x.get("source") not in only]
        doc.update(only=sorted(only), kept_ids=sorted(before), previews=earlier + previews)
        report.update(only=sorted(only), previews=earlier_rep + previews,
                      dropped=[d for d in prev_rep.get("dropped") or [] if d.get("source") not in only] + dropped)
    write_json(audit_dir(args) / "new_ids.json", doc)
    by_type = Counter(f"{e['source']}:{e['type']}" for e in entries)
    write_json(report_dir(args) / "catalogue.json",
               dict(report, by_type=dict(sorted(by_type.items())),
                    copies={"library": str(lib_path), "polyhaven": str(ph_path)}, stats=stats))
    print(f"growth catalogue: {len(entries)} new entries {dict(by_source)}, {len(dropped)} dropped, "
          f"{len(previews)} previews" + (f", only {sorted(only)} ({len(doc['kept_ids'])} earlier ids kept)"
                                         if only else "")
          + (f", re-audit {reaudit}" if reaudit else "") + (f", re-audit waiting {waiting}" if waiting else "")
          + f" -> {lib_path.parent}")
    for w in waiting:
        print(f"growth catalogue: {w['id']} waits for a re-audit: {w['reason']}")
    return EXIT_OK if ids else EXIT_NOTHING


# --------------------------------------------------------------------------
# Vision question (one server session), styles, P3 pending, gaps
# --------------------------------------------------------------------------

def ask_args(out, catalog, polyhaven, key, server, pass_, workers, deadline) -> Namespace:
    return Namespace(out=str(out), catalog=str(catalog) if catalog else None,
                     polyhaven=str(polyhaven) if polyhaven else None, model_key=key, model_id=None, slug=None,
                     server=server, serve=False, job_dir=None, pass_=pass_, workers=workers, deadline=deadline)


def unanswered(a: Namespace, model, passes: list) -> int:
    """Requests of ``passes`` without a current answer (the requests files are rebuilt as the ask would)."""
    from wenart.assets.audit import ask as A
    from wenart.assets.audit import cli as CLI
    from wenart.assets.audit import items as I
    from wenart.assets.audit import load_config
    audit = Path(a.out) / AUDIT_DIR
    mdoc = read_json(audit / "measure.json")
    if not mdoc:
        return 0
    items = I.load_items(Path(a.catalog) if a.catalog else None, Path(a.polyhaven) if a.polyhaven else None)
    cfg_ask = load_config().get("ask") or {}
    version = cfg_ask.get("version", "m12.1")
    n = 0
    for p in passes:
        second = p == 2
        only = CLI.second_pass_ids(items, A.load_answers(audit, model)) if second else None
        doc = A.build_requests(items, mdoc, audit, version, only, second, cfg_ask=cfg_ask)
        store = A.store_for(audit, model, second)
        n += sum(1 for i in doc["items"] if store.valid(i) is None)
    return n


def cmd_ask(args) -> int:
    from wenart.assets.audit import ask as A
    from wenart.assets.audit import cli as CLI
    lib, ph = copies(args)
    deadline = deadline_of(args)
    model = A.model_of(args.model_key)
    p4 = ask_args(args.p4, lib, ph, args.model_key, None, "both", args.workers, deadline)
    p3_ok = (Path(args.p3) / AUDIT_DIR / "measure.json").is_file()
    p3 = ask_args(args.p3, None, None, args.model_key, None, "2", args.workers, deadline)
    todo = unanswered(p4, model, [1, 2]) + (unanswered(p3, model, [2]) if p3_ok else 0)
    rec = {"model": model.id, "key": model.key, "unanswered_before": todo, "p3_folder": p3_ok}
    if args.plan_only:
        print(f"growth ask: unanswered {todo}")
        write_json(report_dir(args) / "ask_plan.json", rec)
        return EXIT_OK
    if todo == 0:
        print("growth ask: every request has a current answer; no server")
        write_json(report_dir(args) / "ask.json", dict(rec, rc_p4=EXIT_OK, rc_p3=EXIT_OK, server=False))
        return EXIT_OK
    from wenart.run import servers as S
    stats: list = []
    try:
        with S.server(model.key, deadline, stats=stats, job_dir=Path(args.job_dir) if args.job_dir else None) as url:
            p4.server, p3.server = url, url
            rc4 = CLI.cmd_ask(p4)
            rc3 = CLI.cmd_ask(p3) if p3_ok else EXIT_OK
    except S.ServerError as exc:
        print(f"growth ask: server error: {exc}")
        write_json(report_dir(args) / "ask.json", dict(rec, error=str(exc), server=stats))
        return EXIT_SERVER
    left = unanswered(p4, model, [1, 2]) + (unanswered(p3, model, [2]) if p3_ok else 0)
    write_json(report_dir(args) / "ask.json", dict(rec, rc_p4=rc4, rc_p3=rc3, unanswered_after=left, server=stats))
    print(f"growth ask: P4 rc {rc4}, P3 pass 2 rc {rc3}, {left} left")
    return rc4 if rc4 != EXIT_OK else rc3


def new_ids(args) -> dict:
    return read_json(audit_dir(args) / "new_ids.json") or {"ids": [], "hints": {}}


def cmd_vision_fields(args) -> int:
    from wenart.assets.audit import ask as A
    from wenart.assets.audit import growth_entries as GE
    nid = new_ids(args)
    answers = A.load_answers(audit_dir(args), A.model_of(args.model_key))
    total = {"styled": 0, "beds": 0}
    for path in copies(args):
        doc = read_json(path)
        if not doc:
            continue
        got = GE.apply_vision_fields(doc, answers, set(nid["ids"]), nid.get("hints"))
        total = {k: total[k] + got[k] for k in total}
        write_json(path, doc)
    write_json(report_dir(args) / "vision_fields.json", dict(total, answers=len(answers), new=len(nid["ids"])))
    print(f"growth vision-fields: {total}")
    return EXIT_OK


# --------------------------------------------------------------------------
# The second look at the doubted models (28 Oct 2026)
# --------------------------------------------------------------------------

AUDIT_IDS = "audit_ids.json"          # <p4>/audit/: the new ids and the doubted ones the render, code, decide take


def second_look_ids(*docs: Optional[dict]) -> dict:
    """The pending entries a second audit pass settles (pure; 28 Oct 2026, ``wenart.furniture.model_title``
    ``audit_doubt``: the vision check said a model is not its type or found its size odd; ``decide.second_look``):
    ``{"p4": [ids], "p3": [ids], "other": [ids]}``. ``p4``: audited by a growth pod (a ``growth`` record: their pass 1
    answers and renders are in the growth audit folder), ``p3``: the library audit of pod P3 (decided by ``pending``
    with P3's answers), ``other``: pending for another reason (a front turned off its detail side, a re-audit, no
    title rules record): the type question does not settle them, they stay as they are."""
    out: dict = {"p4": [], "p3": [], "other": []}
    for doc in docs:
        for sec in ("entries", "decor", "extras"):
            for e in (doc or {}).get(sec) or []:
                a = e.get("audit") if isinstance(e, dict) and isinstance(e.get("audit"), dict) else {}
                if not e.get("id") or str(a.get("status") or "") != "pending":
                    continue
                rules = {f.get("rule") for f in (a.get("title_rules") or {}).get("findings") or []
                         if isinstance(f, dict)}
                if rules != {"audit_doubt"} or isinstance(a.get(REAUDIT), dict):
                    out["other"].append(e["id"])
                else:
                    out["p4" if e.get("growth") else "p3"].append(e["id"])
    return {k: sorted(set(v)) for k, v in out.items()}


def cmd_second_look(args) -> int:
    """28 Oct 2026 (coordinator: one pod both audits the new doors and windows and settles the pending models): the
    ids the audit steps take (``<p4>/audit/audit_ids.json``: the new ids of ``new_ids.json`` plus the doubted growth
    models of the copies, ``second_look_ids``) and ``report/second_look.json``; the doubted models are rendered (or
    their current render reused), coded, asked pass 1 (answers reused while current) and pass 2 (``cli
    .second_pass_ids``), decided (``decide.second_look``) and written with the new ones; the P3 ones by ``pending``.
    ``--summary`` (after the write and pending steps): their status now, by source."""
    from collections import Counter
    lib_path, ph_path = copies(args)
    lib, ph = read_json(lib_path), read_json(ph_path)
    if not lib or not ph:
        print(f"growth second-look: no catalogue copies in {lib_path.parent}: run the catalogue step first")
        return EXIT_NOTHING
    rep = report_dir(args) / "second_look.json"
    if getattr(args, "summary", False):
        prev = read_json(audit_dir(args) / AUDIT_IDS) or {}
        status = {e["id"]: ((e.get("audit") or {}).get("status") or "unaudited", e.get("source"))
                  for d in (lib, ph) for s in ("entries", "decor", "extras") for e in d.get(s) or []
                  if isinstance(e, dict) and e.get("id")}
        ids = list(prev.get("second_look") or []) + list(prev.get("p3") or [])
        after = Counter(f"{status.get(i, ('missing', None))[1]}:{status.get(i, ('missing', None))[0]}" for i in ids)
        doc = dict(read_json(rep) or {}, after=dict(sorted(after.items())), summary_utc=now_utc())
        write_json(rep, doc)
        print(f"growth second-look: after the audit {dict(sorted(after.items()))}")
        return EXIT_OK
    sel = second_look_ids(lib, ph)
    nid = new_ids(args)
    new = list(nid.get("ids") or [])
    ids = new + [i for i in sel["p4"] if i not in set(new)]
    write_json(audit_dir(args) / AUDIT_IDS, {"kind": "library_audit_ids", "written_utc": now_utc(), "ids": ids,
                                             "new": new, "second_look": sel["p4"], "p3": sel["p3"],
                                             "left_pending": sel["other"]})
    write_json(rep, {"kind": "library_second_look", "written_utc": now_utc(), "growth": len(sel["p4"]),
                     "p3": len(sel["p3"]), "left_pending": len(sel["other"]), "ids": sel})
    print(f"growth second-look: {len(sel['p4'])} doubted growth model(s) join the {len(new)} new one(s) "
          f"({len(ids)} to audit), {len(sel['p3'])} P3 model(s) for the pending step, {len(sel['other'])} pending "
          f"for another reason stay")
    return EXIT_OK


def cmd_pending(args) -> int:
    """The P3 models still pending (``audit.status`` pending in the copies, not new in P4) decided with P3's answers
    (pass 2 asked by ``ask``) and written into the copies (``write.apply_decisions``)."""
    from wenart.assets.audit import cli as CLI
    from wenart.assets.audit import items as I
    from wenart.assets.audit import report as RP
    from wenart.assets.audit import write as W
    from wenart.furniture import catalog as C
    lib_path, ph_path = copies(args)
    new = set(new_ids(args)["ids"])
    # an entry waiting for a re-audit of a changed file (``reaudit_entries``) needs a render of the new file, never
    # P3's answers about the old one
    pend = [i for i in I.load_items(lib_path, ph_path) if (i.get("audit") or {}).get("status") == "pending"
            and i["id"] not in new and not isinstance((i.get("audit") or {}).get(REAUDIT), dict)]
    if not pend:
        print("growth pending: no P3 model is pending")
        return EXIT_OK
    a = Namespace(out=str(args.p3), catalog=str(lib_path), polyhaven=str(ph_path), dry=False, work=None,
                  model_key=args.model_key)
    code = read_json(Path(args.p3) / AUDIT_DIR / "code.json")
    if not code:
        print(f"growth pending: {Path(args.p3) / AUDIT_DIR / 'code.json'} not found: P3's folder is missing")
        return EXIT_NOTHING
    pend = [i for i in pend if i["id"] in (code.get("checks") or {})]
    items, checks, decisions, a1, a2 = CLI.decide_all(a, pend)
    rows = RP.rows_of(items, checks, decisions, a1, a2)
    RP.write_outputs(audit_dir(args) / "pending_p3", rows, "full", now_utc(), "P3 models decided in pod P4 "
                     "(pass 2 asked in P4)", "The generated models that waited for a second vision pass after pod P3 "
                     "(docs/milestone12.md §14.3).")
    stamp = args.checked_utc or now_utc()
    dec = {r["id"]: {"status": r["status"], "reasons": r["reasons"], "fixes": r["fixes"], "flags": r["flags"],
                     "notes": r["notes"], "vision_doubt": r.get("vision_doubt") or [],
                     "pending": r.get("pending") or [], "vision_quality": r.get("vision_quality")} for r in rows}
    for path, complete in ((lib_path, False), (ph_path, True)):
        doc = read_json(path)
        W.apply_decisions(doc, dec, stamp)
        C.validate(doc, complete=complete)
        write_json(path, doc)
    print(f"growth pending: {RP.counts(rows, 'status')}")
    return EXIT_OK


def cmd_gaps(args) -> int:
    """The gap report over the whole library (``gaps.py``): every model of the copies with its audit status."""
    from wenart.assets.audit import gaps as GP
    from wenart.assets.audit import items as I
    from wenart.assets.audit import load_config
    lib_path, ph_path = copies(args)
    items = I.load_items(lib_path, ph_path)
    statuses = {i["id"]: (i.get("audit") or {}).get("status") or "unaudited" for i in items}
    groups = GP.groups_from_yaml()
    rows = GP.gap_table(items, statuses, GP.merge_groups(groups, GP.BUILTIN_GROUPS), load_config(), ("keep", "fix"))
    note = ("Whole library after pod P4 (the catalogue copies: P3's audit, the P3 pending models decided in P4 and "
            "the new models audited in P4); kept = audit keep or fix. Group needs from " +
            ("wenart/furniture/groups.yaml plus the decor and light rows of the built-in table." if groups else
             "the built-in table."))
    write_json(audit_dir(args) / "gaps.json", {"kind": "library_audit_gaps", "scope": "whole library after P4",
                                               "groups": "groups.yaml" if groups else "builtin", "rows": rows})
    (audit_dir(args) / "gaps.md").write_text(GP.gaps_markdown(rows, "Library gaps after pod P4", note),
                                             encoding="utf-8")
    # Milestone 13: the demand gaps per licence mode on the copies (the audit status written)
    from wenart.assets.audit import demands as D
    from wenart.furniture import catalog as C
    dem = D.drawn_demands()
    grid = D.size_grid(dem)
    doc = coverage_doc(C.load(ph_path, library=lib_path), dem, grid, load_config(), now_utc(),
                       "catalogue copies after the audit")
    write_json(audit_dir(args) / "gaps_demand.json", doc)
    (audit_dir(args) / "gaps_demand.md").write_text(
        GP.demand_gaps_markdown(doc["gaps"], "Library gaps by drawn demand (after the audit)",
                                f"Scope: {doc['scope']}; a bin is a gap below {doc['min_models_per_bin']} usable "
                                "models in a licence mode."), encoding="utf-8")
    print(f"growth gaps: {sum(1 for r in rows if r['gap'])} (type, family) gap(s) of {len(rows)}; demand bins "
          f"{doc['bins_demanded']}, covered {doc['bins_covered']}, {doc['gap_rows']} gap rows")
    return EXIT_OK


def preview_item(p: dict, assets: Path) -> dict:
    """The audit item of one preview of ``new_ids.json``: an Infinigen model without a type of ours (``glb``,
    ``factory``, ``class``) or, since Milestone 13, a Poly Haven vegetation model (``gltf``, ``type``: no furniture
    entry, wenart.blender.vegetation uses it). Raises ``KeyError`` naming the missing field, ``MeshError`` /
    ``OSError`` when the file cannot be measured (``cmd_preview`` prints and records every one)."""
    from wenart.assets.audit import glbmesh as GM
    from wenart.furniture import catalog as C
    rel = p.get("glb") or p.get("gltf")
    if not rel:
        raise KeyError(f"no glb / gltf path in the preview record (keys {sorted(p)})")
    m = GM.measure(Path(assets) / rel)
    if p.get("source") == "3dwh":
        from wenart.assets import warehouse as WH
        title, source, licence = (f"3D Warehouse {p.get('type') or p.get('kind')} ({p.get('kind')}, no catalogue "
                                  f"entry yet): {p.get('title') or p['id']}"), WH.SOURCE, WH.LICENCE
    elif p.get("kind") == "vegetation":
        title, source, licence = f"Poly Haven {p.get('type') or 'vegetation'} (vegetation, no furniture entry)", \
            "polyhaven", "CC0"
    else:
        title = f"Infinigen {p.get('factory', '?')} ({p.get('class', '?')}): no type of ours"
        source, licence = "generated", "generated (Infinigen, BSD-3-Clause)"
    return {"id": p["id"], "type": "unknown", "kind": "furniture", "source": source, "licence": licence,
            "title": title, ("gltf" if rel.endswith(".gltf") else "glb"): rel, "bbox_m": m["bbox_model_m"],
            "unit_scale": 1.0, "origin_offset": C.origin_offset(m["bbox_min_m"], m["bbox_max_m"]), "front_axis": "-Y"}


def cmd_preview(args) -> int:
    """Audit sheets (the scale reference, four views) of the previews of ``new_ids.json``: the generated models
    without a type of ours and (Milestone 13) the Poly Haven vegetation models.

    Pod P2 (15 Oct 2026, docs/milestone13.md §14.6): the step stopped at once with ``KeyError: 'glb'`` (steps.tsv
    ``preview 1 0``): the vegetation previews the Milestone 13 catalogue step adds carry ``gltf``, not ``glb``. Now
    both kinds are measured, every preview that cannot be measured or rendered is printed with its reason and
    recorded in ``report/preview.json``, and the step ends with one line that names what failed (rc 1 then)."""
    from wenart.assets.audit import load_config
    from wenart.assets.audit import render as R
    prev = new_ids(args).get("previews") or []
    if not prev:
        print("growth preview: nothing to show")
        return EXIT_OK
    items, failed = [], []
    for p in prev:
        try:
            items.append(preview_item(p, Path(args.assets)))
        except Exception as exc:  # noqa: BLE001 - KeyError, MeshError, OSError, ValueError: printed and recorded
            failed.append({"id": p.get("id"), "reason": f"not measured: {type(exc).__name__}: {exc}"})
            print(f"growth preview: {p.get('id')} not measured: {type(exc).__name__}: {exc}", flush=True)
    rc = EXIT_OK
    out = audit_dir(args) / "preview"
    if items:
        s = dict(load_config().get("render") or {})
        work = Path(args.p4) / "work_preview"
        doc = R.render_jobs(items, Path(args.assets), work, s, deadline_of(args))
        for miss in doc.get("missing") or []:
            failed.append({"id": miss["id"], "reason": f"file missing: {miss['file']}"})
            print(f"growth preview: {miss['id']} file missing: {miss['file']}")
        # 23 Oct 2026: up to 3 Blender workers (the audit render's AUDIT_WORKERS): the 3D Warehouse trees, doors and
        # windows are hundreds of previews
        rc = R.run_render(doc, args.blender, work, max(1, min(3, int(getattr(args, "workers", 1) or 1))))
        if rc != EXIT_OK:
            print(f"growth preview: the Blender render ended with exit {rc} (logs in {work / 'jobs'})")
        R.compose_all(items, work, out, s)
        measures = R.read_measures(work)
        for it in items:
            m = measures.get(it["id"]) or {}
            if not m.get("ok") and it["id"] not in {f["id"] for f in failed}:
                failed.append({"id": it["id"], "reason": f"not rendered: {m.get('error') or 'no measurement'}"})
                print(f"growth preview: {it['id']} not rendered: {m.get('error') or 'no measurement'}")
    write_json(report_dir(args) / "preview.json", {"kind": "library_growth_preview", "written_utc": now_utc(),
                                                   "previews": len(prev), "rendered": len(items) - sum(
                                                       1 for f in failed if f["reason"].startswith("not rendered")),
                                                   "failed": failed, "render_rc": rc, "out": str(out)})
    print(f"growth preview: {len(items)} of {len(prev)} model(s) measured -> {out}"
          + (f"; {len(failed)} FAILED: {', '.join(f['id'] + ' (' + f['reason'] + ')' for f in failed[:5])}"
             + (" ..." if len(failed) > 5 else "") if failed else ""))
    if rc != EXIT_OK:
        return rc
    return EXIT_NOTHING if failed else EXIT_OK


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------

def steps_of(path: Path) -> list:
    """The rows of the job's ``steps.tsv``: ``name rc seconds [reason]`` (round 3: a failed step's last output line
    is its fourth column, so ``preview 1 0`` never stands without a reason again)."""
    rows = []
    try:
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) >= 3 and parts[1].lstrip("-").isdigit():
                row = {"step": parts[0], "rc": int(parts[1]), "seconds": int(parts[2])}
                if len(parts) >= 4 and parts[3].strip():
                    row["reason"] = parts[3].strip()
                rows.append(row)
    except (OSError, ValueError):
        pass
    return rows


def catalogue_counts(args) -> dict:
    """Milestone 13: the catalogue copies' counts per source, per licence flag and per licence mode (``catalog.usable``);
    {} when the copies are not written yet."""
    from collections import Counter

    from wenart.assets.audit import items as I
    from wenart.furniture import catalog as C
    lib_path, ph_path = copies(args)
    if not (lib_path.is_file() and ph_path.is_file()):
        return {}
    items = I.load_items(lib_path, ph_path)
    lib, ph = read_json(lib_path) or {}, read_json(ph_path) or {}
    entries = [e for doc in (lib, ph) for sec in I.SECTIONS for e in doc.get(sec) or []
               if isinstance(e, dict) and not e.get("parametric")]                 # 23 Oct 2026: extras too
    extras = [e for e in lib.get("extras") or [] if isinstance(e, dict)]
    by_source: dict = {}
    by_flag: dict = {}
    usable = {m: 0 for m in C.LICENCE_MODES}
    for e in entries:
        src = e.get("source") or "polyhaven"
        status = (e.get("audit") or {}).get("status") or "unaudited"
        row = by_source.setdefault(src, {"entries": 0})
        row["entries"] += 1
        row[status] = row.get(status, 0) + 1
        flag = C.licence_flag_of(e)
        frow = by_flag.setdefault(flag, {"entries": 0, **{m: 0 for m in C.LICENCE_MODES}})
        frow["entries"] += 1
        for m in C.LICENCE_MODES:
            if C.usable(e, m):
                frow[m] += 1
                usable[m] += 1
    return {"entries": len(entries), "items": len(items), "by_source": by_source, "by_flag": by_flag,
            "usable": usable, "status": dict(Counter((e.get("audit") or {}).get("status") or "unaudited"
                                                     for e in entries)),
            "extras": {"entries": len(extras), "by_kind_status": dict(Counter(
                f"{e.get('kind')}:{(e.get('audit') or {}).get('status') or 'unaudited'}" for e in extras))}}


def cmd_report(args) -> int:
    from collections import Counter
    rep = report_dir(args)
    ing = {s: read_json(rep / f"ingest_{s}.json") or {} for s in ("polyhaven", "abo", "gso", "hssd", "ambientcg",
                                                                   "polyhaven_m13", "abo_m13", "3dwh",
                                                                   "hssd_openings")}
    lic = read_json(rep / "gso_licences.json") or {}
    conv = {s: read_json(rep / f"convert_{s}.json") or {} for s in ("gso", "infinigen")}
    cat = read_json(rep / "catalogue.json") or {}
    plan = read_json(ig_root(args) / "jobs.json") or {}
    facs = read_json(ig_root(args) / "factories.json") or {}
    check = read_json(ig_root(args) / "check.json") or {}
    setup = read_json(ig_root(args) / "setup.json") or {}
    audit = read_json(audit_dir(args) / "audit.json") or {}
    nid = new_ids(args)
    src_of = {}
    for e_id in nid.get("ids") or []:
        src_of[e_id] = "infinigen" if e_id.startswith("infinigen_") else ("gso" if e_id.startswith("gso_") else
                                                                          "abo" if e_id.startswith("abo_") else
                                                                          "hssd" if e_id.startswith("hssd_") else
                                                                          "3dwh" if e_id.startswith("3dwh_") else
                                                                          "polyhaven")
    # 28 Oct 2026: the HSSD doors and windows are their own row (their ids start with hssd_ too)
    for r in ing["hssd_openings"].get("records") or []:
        if r.get("id") in src_of:
            src_of[r["id"]] = "hssd_openings"
    status = Counter((src_of.get(r["id"], r.get("source")), r["status"]) for r in audit.get("items") or [])
    dropped = Counter(d["source"] if d["source"] in ("polyhaven", "abo", "gso", "infinigen", "hssd", "3dwh",
                                                     "hssd_openings") else "?"
                      for d in cat.get("dropped") or [])                  # hssd: M13 (its drops were counted as "?")
    ig_states = Counter(j.get("state") for j in plan.get("jobs") or [])
    rows = []
    for s in ("polyhaven", "abo", "gso", "infinigen", "hssd", "ambientcg", "polyhaven_m13", "abo_m13", "3dwh",
              "hssd_openings"):
        if s in ("3dwh", "hssd_openings") and not ing[s]:
            continue
        approved = ing[s].get("approved") if s not in ("infinigen", "3dwh") else (
            len(plan.get("jobs") or []) if s == "infinigen" else ing[s].get("listed"))
        got = ing[s].get("ok") if s != "infinigen" else ig_states.get("done", 0)
        rows.append({"source": s, "approved": approved, "downloaded_or_generated": got,
                     "licence_kept": lic.get("kept") if s == "gso" else None,
                     "converted": conv[s].get("converted") if s in conv else None,
                     "catalogued": (cat.get("by_list") or {}).get(s, 0) if s == "hssd_openings" else
                     (cat.get("by_source") or {}).get(s, 0), "dropped": dropped.get(s, 0),
                     "keep": status.get((s, "keep"), 0), "fix": status.get((s, "fix"), 0),
                     "removed": status.get((s, "removed"), 0), "pending": status.get((s, "pending"), 0)})
    steps = steps_of(Path(args.steps)) if args.steps else []
    counts = catalogue_counts(args)
    doc = {"kind": "library_growth_report", "written_utc": now_utc(), "sources": rows, "catalogue": counts,
           "hssd_gate": ing["hssd"].get("gate"), "speed": read_json(rep / "speed.json") or {},
           "coverage": {k: v for k, v in (read_json(audit_dir(args) / "gaps_demand.json") or {}).items()
                        if k in ("bins_demanded", "bins_covered", "gap_rows", "min_models_per_bin", "scope")},
           "infinigen": {"tag": plan.get("tag"), "commit": plan.get("commit"), "factories": facs.get("count"),
                         "matched": plan.get("matched"), "missing": plan.get("missing"), "check": check,
                         "setup": setup, "states": dict(ig_states),
                         "jobs": [{k: j.get(k) for k in ("id", "class", "seed", "state")} for j in plan.get("jobs")
                                  or []]},
           "gso": {"kept": lic.get("kept"), "dropped": lic.get("dropped"), "fuel_api": lic.get("fuel_api")},
           "dropped": cat.get("dropped") or [], "previews": cat.get("previews") or [],
           "parametric_replaced": (cat.get("stats") or {}).get("parametric_replaced"), "steps": steps}
    write_json(rep / "growth.json", doc)
    lines = ["# Library growth, pod P4 / P2", "", "docs/milestone12.md §6.4; user OK of 11 Oct 2026 (four lists); "
             "Milestone 13 (docs/milestone13.md §5.1 phase 2, D2): the size-grid, 2K, vegetation, ambientCG and HSSD "
             "lists.", ""]
    if counts:
        lines += ["## Catalogue copies (Milestone 13)", "",
                  f"Entries {counts['entries']} (usable commercial {counts['usable']['commercial']}, relaxed "
                  f"{counts['usable']['relaxed']}).", "",
                  "| source | entries | keep | fix | removed | pending |", "|---|---|---|---|---|---|"]
        lines += [f"| {src} | {c['entries']} | {c.get('keep', 0)} | {c.get('fix', 0)} | {c.get('removed', 0)} | "
                  f"{c.get('pending', 0)} |" for src, c in sorted(counts["by_source"].items())]
        lines += ["", "| licence flag | entries | usable commercial | usable relaxed |", "|---|---|---|---|"]
        lines += [f"| {flag} | {c['entries']} | {c['commercial']} | {c['relaxed']} |"
                  for flag, c in sorted(counts["by_flag"].items())]
        lines.append("")
    if ing["hssd"].get("gate"):
        lines += [f"HSSD gate: {ing['hssd']['gate'].get('reason')}", ""]
    wh = ing["3dwh"]
    if wh.get("listed") is not None:
        doc["3dwh"] = {k: wh.get(k) for k in ("listed", "ok", "unmapped", "dropped", "failed", "not_fitting", "units",
                                              "up_fixed", "by_group", "by_type", "extract", "zip", "seconds")}
        lines += ["## 3D Warehouse (the user's zip, 23 Oct 2026)", "",
                  f"{wh.get('listed')} GLB(s) listed: {wh.get('ok')} fixed, {wh.get('unmapped')} unmapped (review "
                  f"list), {wh.get('dropped')} dropped, {wh.get('failed')} failed; {wh.get('not_fitting')} fit no real "
                  f"size; units {json.dumps(wh.get('units'))}; up axis turned {wh.get('up_fixed')}.", "",
                  "| group | models |", "|---|---|"]
        lines += [f"| {g} | {n} |" for g, n in (wh.get("by_group") or {}).items()]
        lines += ["", "| kind:type | models |", "|---|---|"]
        lines += [f"| {t} | {n} |" for t, n in (wh.get("by_type") or {}).items()]
        lines.append("")
        write_json(rep / "growth.json", doc)
    if doc["speed"]:
        sp = doc["speed"]
        lines += [f"Speed probe: {sp.get('files')} file(s), {sp.get('mb_s')} MB/s, picks {json.dumps(sp.get('picks'))}",
                  ""]
    lines += [
             "| source | approved | downloaded / generated | GSO licence kept | converted | catalogued | dropped | "
             "keep | fix | removed | pending |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append("| " + " | ".join("" if r[k] is None else str(r[k]) for k in
                                       ("source", "approved", "downloaded_or_generated", "licence_kept", "converted",
                                        "catalogued", "dropped", "keep", "fix", "removed", "pending")) + " |")
    lines += ["", f"Infinigen: tag {plan.get('tag')} = commit {plan.get('commit')}; {facs.get('count')} factories "
              f"listed; jobs {dict(ig_states)}; missing factories: {plan.get('missing') or 'none'}; setup: "
              f"{json.dumps(setup) if setup else 'not run'}.", ""]
    if doc["dropped"]:
        lines += ["## Dropped (not catalogued)", "", "| source | id | reason |", "|---|---|---|"]
        lines += [f"| {d['source']} | {d['id']} | {str(d['reason']).replace('|', '/')[:200]} |" for d in doc["dropped"]]
        lines.append("")
    if steps:
        lines += ["## Steps", "", "| step | rc | seconds | reason (a failed step's last line) |", "|---|---|---|---|"]
        lines += [f"| {s['step']} | {s['rc']} | {s['seconds']} | {str(s.get('reason') or '').replace('|', '/')} |"
                  for s in steps]
        lines.append("")
    (rep / "growth.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"growth report -> {rep / 'growth.md'}")
    return EXIT_OK


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

STEPS = {"ingest": cmd_ingest, "gso-licence": cmd_gso_licence, "infinigen-list": cmd_infinigen_list,
         "infinigen-plan": cmd_infinigen_plan, "convert": cmd_convert, "catalogue": cmd_catalogue, "ask": cmd_ask,
         "vision-fields": cmd_vision_fields, "pending": cmd_pending, "gaps": cmd_gaps, "preview": cmd_preview,
         "report": cmd_report,
         # Milestone 13 (track T7)
         "demands": cmd_demands, "size-grid": cmd_size_grid, "speed-probe": cmd_speed_probe,
         # Milestone 13 round 3: the current file of an entry waiting for a re-audit
         "refetch": cmd_refetch,
         # 28 Oct 2026: the doubted models settled by the same pod (GROWTH_ONLY=openings)
         "second-look": cmd_second_look}
M13_STEPS = ("demands", "size-grid", "speed-probe")
ONLY_SOURCES = ("hssd", "abo", "polyhaven", "gso", "infinigen", "3dwh",      # catalogue --only (GROWTH_ONLY=hssd)
                "hssd_openings")                                             # 28 Oct 2026 (GROWTH_ONLY=openings)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m wenart.assets growth run", description="pod P4: library growth")
    p.add_argument("step", choices=sorted(STEPS))
    p.add_argument("--growth", default="/workspace/library-growth")
    p.add_argument("--assets", default=os.environ.get("WENART_ASSETS", "/workspace/assets"))
    p.add_argument("--p4", default="/workspace/library-audit/p4")
    p.add_argument("--p3", default="/workspace/library-audit")
    p.add_argument("--lists", default=str(DEFAULT_OUT), help="results/library (approvals and candidate lists)")
    p.add_argument("--report", default=None, help="small result files (default <growth>/report)")
    p.add_argument("--source", default=None, choices=["polyhaven", "abo", "gso", "infinigen", "hssd", "ambientcg",
                                                      "3dwh", "hssd_openings"])
    p.add_argument("--library", default=os.environ.get("WENART_3DWH_ROOT") or "/workspace/library/3dwh",
                   help="ingest 3dwh: the folder with zip/ (the download) and glb/ (the extracted GLBs)")
    p.add_argument("--m13", action="store_true", help="ingest: the Milestone 13 list of abo / polyhaven")
    p.add_argument("--token-env", default="HF_TOKEN", help="ingest hssd: the environment variable with the token "
                                                            "(never printed)")
    p.add_argument("--size", default=PH_SIZE, help="Poly Haven glTF resolution (default 1k: what the fit resolves)")
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--blender", default=os.environ.get("WENART_BLENDER") or "blender")
    p.add_argument("--repo", default=None, help="infinigen-list: the Infinigen clone")
    p.add_argument("--no-fuel", action="store_true", help="gso-licence: do not ask Gazebo Fuel")
    p.add_argument("--model-key", default="agent")
    p.add_argument("--job-dir", default=None)
    p.add_argument("--plan-only", action="store_true")
    p.add_argument("--deadline", default=None)
    p.add_argument("--checked-utc", default=None)
    p.add_argument("--steps", default=None, help="report: the job's steps.tsv")
    p.add_argument("--only", default=None, help="catalogue: only these sources, comma separated (GROWTH_ONLY=hssd); "
                                                 "every other entry stays as the repo's catalogues have it")
    p.add_argument("--summary", action="store_true", help="second-look: the doubted models' status after the audit")
    return p


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    if args.step in ("ingest", "convert") and not args.source:
        print(f"growth run {args.step}: --source is needed")
        return EXIT_NOTHING
    if args.step == "infinigen-list" and not args.repo:
        print("growth run infinigen-list: --repo is needed")
        return EXIT_NOTHING
    if args.step == "ask" and args.workers == 8:
        from wenart.assets.audit import load_config
        args.workers = int((load_config().get("ask") or {}).get("workers", 4))
    bad = sorted({x.strip() for x in str(args.only or "").split(",") if x.strip()} - set(ONLY_SOURCES))
    if bad:
        print(f"growth run {args.step}: --only {bad} is not a source of {ONLY_SOURCES}")
        return EXIT_NOTHING
    try:
        return STEPS[args.step](args)
    except KeyboardInterrupt:
        return EXIT_DEADLINE
    except Exception as exc:  # noqa: BLE001 - round 3: every failure prints its reason (pod P2: preview rc 1)
        import traceback
        traceback.print_exc()
        print(f"growth run {args.step}: FAILED: {type(exc).__name__}: {exc}", flush=True)
        return EXIT_NOTHING


if __name__ == "__main__":
    sys.exit(main())
