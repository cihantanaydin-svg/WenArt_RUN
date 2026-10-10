"""CLI of the library audit: ``python -m wenart.assets audit <step>`` (docs/milestone12.md §6.1, D21).

    audit licences [--write] [--catalog P] [--checked-utc T]       U3 + B2 on catalog_library.json (here, now)
    audit render --assets DIR [--work DIR] [--blender B] [--workers N] [--deadline T] [--textures] [--plan]
                                                                     pod P2: views, measurements, sheets
    audit code [--work DIR] [--dry]                                  code checks -> code.json
    audit ask [--model-key K | --model-id ID --slug S] [--server URL] [--serve] [--pass 1|2] [--workers N]
                                                                     pod P3: the vision question
    audit decide [--model-key K] [--dry]                             keep / fix / remove -> audit.json/.csv/.md
    audit sheets [--dry]                                             contact/<type>.jpg
    audit gaps [--dry]                                               gaps.json, gaps.md
    audit write [--model-key K] [--checked-utc T] [--dry-run]        the catalogue's audit fields and flags
    audit dry                                                        code + decide + sheets + gaps, catalogue only
    audit status [--work DIR]                                        what each step has done

Common: ``--out`` (default ``results/library``; the audit lives in ``<out>/audit/``, the dry audit in
``<out>/audit/dry/``), ``--catalog`` / ``--polyhaven`` (default ``wenart/furniture/catalog_library.json`` /
``catalog.json``). Every step is resumable (renders and answers are reused while current). Exit codes: 0 done, 1
nothing to do or a step failed, 2 server error, 3 cut by the deadline (``--deadline`` or ``WENART_DEADLINE``).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from wenart.assets.audit import (AUDIT_DIR, DEFAULT_OUT, EXIT_DEADLINE, EXIT_NOTHING, EXIT_OK, EXIT_SERVER,
                                 load_config)


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _items(args):
    from wenart.assets.audit import items as I
    return I.load_items(Path(args.catalog) if args.catalog else None, Path(args.polyhaven) if args.polyhaven else None)


def _audit(args) -> Path:
    return Path(args.out) / AUDIT_DIR


def _folder(args) -> Path:
    return _audit(args) / "dry" if getattr(args, "dry", False) else _audit(args)


def _measures(args) -> dict:
    """The render's measurements: ``measure.json`` of the audit folder (the copy that reaches the results), else the
    work folder's ``measure/*.json``."""
    if getattr(args, "dry", False):
        return {}
    p = _audit(args) / "measure.json"
    if p.is_file():
        return (json.loads(p.read_text(encoding="utf-8")).get("measures") or {})
    if getattr(args, "work", None):
        from wenart.assets.audit import render as R
        return R.read_measures(Path(args.work))
    return {}


def _json(path: Path, doc) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def _read(path: Path) -> Optional[dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


# --------------------------------------------------------------------------
# Steps
# --------------------------------------------------------------------------

def cmd_licences(args) -> int:
    from wenart.assets.audit import items as I
    from wenart.assets.audit import write as W
    from wenart.furniture import catalog as C
    path = Path(args.catalog) if args.catalog else I.LIBRARY_PATH
    doc = json.loads(path.read_text(encoding="utf-8"))
    ids = W.licence_removals(doc, args.checked_utc or now_utc())
    n = W.generated_credit(doc)
    noted = W.note_u3(doc)
    C.validate(doc, complete=False)
    for e in [e for s in ("entries", "decor") for e in doc.get(s) or []]:
        if e["id"] in ids:
            print(f"removed {e['id']:<45} {e['licence']:<16} {e['type']:<16} {str(e.get('title'))[:50]}")
    print(f"audit licences: {len(ids)} entr(ies) removed for their licence, {n} generated credit(s) fixed "
          f"({'written' if args.write else 'not written: --write'}) -> {path}")
    if args.write and (ids or n or noted):
        path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return EXIT_OK


def cmd_render(args) -> int:
    from wenart.assets.audit import render as R
    cfg = load_config()
    s = dict(cfg.get("render") or {})
    s["device"] = args.device
    items = _items(args)
    if args.ids:
        items = [i for i in items if i["id"] in set(args.ids)]
    if args.types:
        items = [i for i in items if i["type"] in set(args.types.split(","))]
    if args.smoke:
        items = smoke_items(items, args.smoke)
    work = Path(args.work or (_audit(args) / "work"))
    deadline = R.deadline_of(args.deadline)
    doc = R.render_jobs(items, Path(args.assets), work, s, deadline)
    workers = args.workers or int(s.get("workers", 1))
    est = len(doc["jobs"]) * float(s.get("seconds_per_item", 4.0)) / max(1, workers) / 60.0
    print(f"audit render: {len(doc['jobs'])} job(s), {len(doc['skipped'])} current, {len(doc['missing'])} file(s) "
          f"missing in {args.assets}; {workers} worker(s), about {est:.0f} min")
    _json(_audit(args) / "render_plan.json", {"jobs": [j["id"] for j in doc["jobs"]], "skipped": doc["skipped"],
                                              "missing": doc["missing"], "workers": workers,
                                              "estimate_min": round(est, 1)})
    if args.plan:
        return EXIT_OK
    rc = R.run_render(doc, args.blender or R.default_blender(), work, workers)
    if args.textures and not args.smoke:
        man = _read(Path(args.assets) / "manifest.json") or {}
        tj = R.texture_jobs(man, Path(args.assets), work)
        if tj:
            rc_t = _render_textures(R, dict(doc, jobs=[], textures=tj), args, work)
            if rc == EXIT_OK and rc_t != 0:
                rc = EXIT_DEADLINE if rc_t == EXIT_DEADLINE else EXIT_NOTHING
        R.overlay_textures(work, _audit(args), s)
    R.compose_all(items, work, _audit(args), s)
    if args.smoke:
        measures = R.read_measures(work)
        ok = [i["id"] for i in items if (measures.get(i["id"]) or {}).get("ok")]
        print(f"audit render smoke: {len(ok)} of {len(items)} model(s) measured and rendered: {ok}")
        return EXIT_OK if ok and len(ok) == len(items) else EXIT_NOTHING
    return rc


def smoke_items(items: list, n: int) -> list:
    """``n`` models for a smoke render before the full run: the first of each source in turn (GLB and glTF)."""
    by: dict = {}
    for it in items:
        by.setdefault(it.get("source"), []).append(it)
    out: list = []
    while len(out) < n and any(by.values()):
        for src in sorted(by):
            if by[src] and len(out) < n:
                out.append(by[src].pop(0))
    return out


def _render_textures(R, tdoc: dict, args, work: Path) -> int:
    """One Blender process for the texture samples (the jobs file carries ``textures``, no model jobs)."""
    import subprocess
    jp = work / "jobs" / "jobs_textures.json"
    jp.parent.mkdir(parents=True, exist_ok=True)
    jp.write_text(json.dumps(dict(tdoc, worker="textures"), indent=1), encoding="utf-8")
    with open(work / "jobs" / "blender_textures.log", "w", encoding="utf-8") as fh:
        return subprocess.call(R.blender_command(args.blender or R.default_blender(), jp), stdout=fh,
                               stderr=subprocess.STDOUT)


def cmd_code(args) -> int:
    from wenart.assets.audit import checks as C
    cfg = load_config()
    items = _items(args)
    measures = _measures(args)
    checks = C.run_checks(items, cfg, measures)
    # the passed checks are not kept (they say "ok"), except the title's verdict that decide reads
    kept = {iid: [c for c in recs if c["status"] not in ("ok", "skip") or c["check"] == "title"]
            for iid, recs in checks.items()}
    _json(_folder(args) / "code.json", {"kind": "library_audit_code", "mode": "dry" if args.dry else "full",
                                        "measured": len(measures), "checks": kept})
    print(f"audit code: {len(items)} model(s), {len(measures)} measured -> {_folder(args) / 'code.json'}")
    return EXIT_OK


def _model(args):
    from wenart.assets.audit import ask as A
    cfg = load_config()
    key = args.model_key or (cfg.get("ask") or {}).get("model_key", "agent")
    return A.model_of(key, getattr(args, "model_id", None), getattr(args, "slug", None))


def _answers(args, items):
    from wenart.assets.audit import ask as A
    if getattr(args, "dry", False):
        return {}, {}
    try:
        model = _model(args)
    except KeyError:
        return {}, {}
    return A.load_answers(_audit(args), model), A.load_answers(_audit(args), model, second=True)


def second_pass_ids(items: list, first: dict) -> set:
    """The models of pass 2: no title evidence (generated, a title naming no type) and pass 1 says it is the type."""
    from wenart.assets.audit import checks as CK
    out = set()
    for it in items:
        v = CK.title_check(it, set())[0]["metrics"]["verdict"]
        a = first.get(it["id"])
        if v in ("silent", "generated") and a and a.get("is_type") is True:
            out.add(it["id"])
    return out


def cmd_ask(args) -> int:
    """Pass 1, pass 2 or both (``--pass both``: one server session for both)."""
    from wenart.assets.audit import ask as A
    from wenart.assets.audit import render as R
    cfg = load_config()
    items = _items(args)
    audit = _audit(args)
    mdoc = _read(audit / "measure.json")
    if not mdoc:
        print(f"audit ask: {audit / 'measure.json'} not found: run the render first")
        return EXIT_NOTHING
    version = (cfg.get("ask") or {}).get("version", "m12.1")
    model = _model(args)
    deadline = R.deadline_of(args.deadline)
    workers = args.workers or int((cfg.get("ask") or {}).get("workers", 4))
    passes = [1, 2] if args.pass_ == "both" else [int(args.pass_)]

    def run(url: str) -> int:
        rc = EXIT_OK
        for n in passes:
            second = n == 2
            only = second_pass_ids(items, A.load_answers(audit, model)) if second else None
            doc = A.build_requests(items, mdoc, audit, version, only, second)
            print(f"audit ask: {len(doc['items'])} request(s) (pass {n}), model {model.id}")
            if doc["items"]:
                rc = A.ask(audit, model, url, second=second, workers=workers, deadline=deadline)
            if rc != EXIT_OK:
                return rc
        return rc
    if args.serve:
        from wenart.run import servers as S
        try:
            with S.server(model.key, deadline, job_dir=Path(args.job_dir) if args.job_dir else None) as url:
                return run(url)
        except S.ServerError as exc:
            print(f"audit ask: server error: {exc}")
            return EXIT_SERVER
    return run(args.server)


def decide_all(args, items=None):
    from wenart.assets.audit import checks as C
    from wenart.assets.audit import decide as D
    cfg = load_config()
    items = items if items is not None else _items(args)
    code = _read(_folder(args) / "code.json")
    checks = (code or {}).get("checks") or C.run_checks(items, cfg, _measures(args))
    a1, a2 = _answers(args, items)
    decisions = {it["id"]: D.decide(it, checks[it["id"]], a1.get(it["id"]), a2.get(it["id"]), cfg) for it in items}
    return items, checks, decisions, a1, a2


DRY_INTRO = ("CPU dry audit (no render, no vision check): the checks code can make on the catalogue fields alone "
             "(licence, title words in any language, the box against the real-size table, pivot, units, M8-M10 "
             "quality, face count, duplicates by box, faces and material colours). `removed` / `fix` are decided by "
             "code; `removed?` / `fix?` / `keep?` are the expected outcomes once the vision check has answered; "
             "`vision?` = no title evidence (generated models, titles naming no type): two vision passes decide.")


def cmd_decide(args) -> int:
    from wenart.assets.audit import report as RP
    items, checks, decisions, a1, a2 = decide_all(args)
    rows = RP.rows_of(items, checks, decisions, a1, a2)
    title = "Library audit (dry, CPU)" if args.dry else "Library audit"
    paths = RP.write_outputs(_folder(args), rows, "dry" if args.dry else "full", args.generated_utc or now_utc(),
                             title, DRY_INTRO if args.dry else "", {"answers": len(a1), "answers2": len(a2)})
    print(f"audit decide: {RP.counts(rows)} -> {', '.join(str(p) for p in paths)}")
    return EXIT_OK


def cmd_sheets(args) -> int:
    from wenart.assets.audit import sheets as SH
    folder = _folder(args)
    doc = _read(folder / "audit.json")
    if not doc:
        print(f"audit sheets: {folder / 'audit.json'} not found: run decide first")
        return EXIT_NOTHING
    items = {i["id"]: i for i in _items(args)}
    mdoc = _read(_audit(args) / "measure.json") or {}
    sheets = mdoc.get("sheets") or {}
    by_type: dict = {}
    for r in doc["items"]:
        by_type.setdefault((r["kind"], r["type"]), []).append(r)
    px = int(getattr(args, "tile_px", None) or (load_config().get("render") or {}).get("tile_px", 256))
    n = 0
    for (kind, t), rows in by_type.items():
        tiles = []
        for r in rows:
            src, crop = None, False
            if not args.dry and sheets.get(r["id"]):
                src, crop = _audit(args) / sheets[r["id"]], True
            elif items.get(r["id"], {}).get("thumbnail"):
                src = Path(args.out) / items[r["id"]]["thumbnail"]
            tiles.append({"id": r["id"], "status": r["expected"], "reasons": r["reasons"]
                          or [p["why"] for p in r["pending"]], "source": src, "crop": crop})
        SH.contact_sheet(t, tiles, folder / "contact" / f"{'decor_' if kind == 'decor' else ''}{t}.jpg", px,
                         quality=70 if args.dry else 85)
        n += 1
    print(f"audit sheets: {n} contact sheet(s) -> {folder / 'contact'}")
    return EXIT_OK


def cmd_gaps(args) -> int:
    from wenart.assets.audit import gaps as G
    folder = _folder(args)
    doc = _read(folder / "audit.json")
    if not doc:
        print(f"audit gaps: {folder / 'audit.json'} not found: run decide first")
        return EXIT_NOTHING
    items = _items(args)
    if args.dry:
        statuses = {r["id"]: r["expected"].rstrip("?") if r["expected"] != "vision?" else "vision"
                    for r in doc["items"]}
        keep = ("keep", "fix")
    else:
        statuses = {r["id"]: r["status"] for r in doc["items"]}
        keep = ("keep", "fix")
    groups = G.groups_from_yaml()
    rows = G.gap_table(items, statuses, groups, load_config(), keep)
    note = ("Group needs from " + ("wenart/furniture/groups.yaml" if groups else
                                   "the built-in table (wenart/assets/audit/gaps.py; groups.yaml not found)") + ".")
    if args.dry:
        note += (" Dry audit: models expected to stay (`keep?`, `fix?`); generated models waiting for two vision "
                 "passes are not counted.")
    _json(folder / "gaps.json", {"kind": "library_audit_gaps", "groups": "groups.yaml" if groups else "builtin",
                                 "rows": rows})
    (folder / "gaps.md").write_text(G.gaps_markdown(rows, "Library gaps" + (" (dry)" if args.dry else ""), note),
                                    encoding="utf-8")
    print(f"audit gaps: {sum(1 for r in rows if r['gap'])} (type, family) gap(s) of {len(rows)} -> {folder}")
    return EXIT_OK


def cmd_write(args) -> int:
    from wenart.assets.audit import items as I
    from wenart.assets.audit import write as W
    from wenart.furniture import catalog as C
    doc = _read(_audit(args) / "audit.json")
    if not doc or doc.get("mode") != "full":
        print(f"audit write: {_audit(args) / 'audit.json'} of a full audit not found (the dry audit is never written)")
        return EXIT_NOTHING
    decisions = {r["id"]: {"status": r["status"], "reasons": r["reasons"], "fixes": r["fixes"], "flags": r["flags"],
                           "notes": r["notes"]} for r in doc["items"]}
    stamp = args.checked_utc or now_utc()
    for path, indent, complete in ((Path(args.catalog) if args.catalog else I.LIBRARY_PATH, 1, False),
                                   (Path(args.polyhaven) if args.polyhaven else I.POLYHAVEN_PATH, 2, True)):
        cat = json.loads(path.read_text(encoding="utf-8"))
        stats = W.apply_decisions(cat, decisions, stamp)
        C.validate(cat, complete=complete)
        print(f"audit write: {path.name}: {stats} -> {W.summary(cat)}")
        if not args.dry_run:
            path.write_text(json.dumps(cat, indent=indent, ensure_ascii=False) + "\n", encoding="utf-8")
    return EXIT_OK


def cmd_dry(args) -> int:
    args.dry = True
    for step in (cmd_code, cmd_decide, cmd_sheets, cmd_gaps):
        rc = step(args)
        if rc != EXIT_OK:
            return rc
    return EXIT_OK


def cmd_status(args) -> int:
    audit = _audit(args)
    out = {}
    for name in ("render_plan.json", "measure.json", "code.json", "audit.json", "gaps.json"):
        p = audit / name
        out[name] = p.is_file()
    asks = sorted(p.name for p in (audit / "ask").glob("answers*.json")) if (audit / "ask").is_dir() else []
    out["answers"] = asks
    doc = _read(audit / "audit.json")
    if doc:
        out["counts"] = doc.get("counts")
    print(json.dumps(out, indent=1))
    return EXIT_OK


# --------------------------------------------------------------------------
# Parser
# --------------------------------------------------------------------------

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m wenart.assets audit", description="library audit (Milestone 12)")
    sub = p.add_subparsers(dest="step", required=True)

    def common(sp):
        sp.add_argument("--out", default=str(DEFAULT_OUT), help="library results folder (default results/library)")
        sp.add_argument("--catalog", default=None, help="catalog_library.json (default wenart/furniture/)")
        sp.add_argument("--polyhaven", default=None, help="catalog.json (default wenart/furniture/)")
        return sp

    s = common(sub.add_parser("licences", help="U3 + B2: NC/SA/ND out of the catalogue, generated credits"))
    s.add_argument("--write", action="store_true")
    s.add_argument("--checked-utc", default=None)
    s = common(sub.add_parser("render", help="pod P2: views, measurements, sheets (Blender)"))
    s.add_argument("--assets", required=True, help="assets folder with models/ (pod: /workspace/assets)")
    s.add_argument("--work", default=None, help="views and measurements (pod: /workspace/library-audit/work)")
    s.add_argument("--blender", default=None)
    s.add_argument("--workers", type=int, default=None)
    s.add_argument("--device", default="auto", choices=["auto", "cpu"])
    s.add_argument("--deadline", default=None)
    s.add_argument("--ids", nargs="*", default=None)
    s.add_argument("--types", default=None, help="comma list of types")
    s.add_argument("--textures", action="store_true", help="also the texture sets of <assets>/manifest.json")
    s.add_argument("--plan", action="store_true", help="only write render_plan.json")
    s.add_argument("--smoke", type=int, default=0, help="render only N models (one per source in turn); exit 1 "
                   "unless every one was measured and rendered")
    s = common(sub.add_parser("code", help="code checks"))
    s.add_argument("--work", default=None)
    s.add_argument("--dry", action="store_true", help="catalogue fields only (no render)")
    s = common(sub.add_parser("ask", help="pod P3: the vision question"))
    s.add_argument("--model-key", default=None, help="check.yaml models key (default audit.yaml ask.model_key)")
    s.add_argument("--model-id", default=None)
    s.add_argument("--slug", default=None)
    s.add_argument("--server", default="http://127.0.0.1:8001/v1")
    s.add_argument("--serve", action="store_true", help="start and stop the vLLM server (wenart.run.servers)")
    s.add_argument("--job-dir", default=None)
    s.add_argument("--pass", dest="pass_", default="1", choices=["1", "2", "both"])
    s.add_argument("--workers", type=int, default=None)
    s.add_argument("--deadline", default=None)
    s = common(sub.add_parser("decide", help="keep / fix / remove"))
    s.add_argument("--model-key", default=None)
    s.add_argument("--dry", action="store_true")
    s.add_argument("--work", default=None)
    s.add_argument("--generated-utc", default=None)
    s = common(sub.add_parser("sheets", help="contact sheets per type"))
    s.add_argument("--dry", action="store_true")
    s.add_argument("--tile-px", type=int, default=None, help="tile size (default audit.yaml render.tile_px)")
    s = common(sub.add_parser("gaps", help="gap report"))
    s.add_argument("--dry", action="store_true")
    s = common(sub.add_parser("write", help="audit fields and flags into the catalogues"))
    s.add_argument("--checked-utc", default=None)
    s.add_argument("--dry-run", action="store_true")
    s = common(sub.add_parser("dry", help="the CPU dry audit: code + decide + sheets + gaps"))
    s.add_argument("--generated-utc", default=None)
    s.add_argument("--tile-px", type=int, default=128, help="contact sheet tiles (default 128: small files in git)")
    s.add_argument("--model-key", default=None)
    s.add_argument("--work", default=None)
    s = common(sub.add_parser("status", help="what each step has done"))
    s.add_argument("--work", default=None)
    return p


COMMANDS = {"licences": cmd_licences, "render": cmd_render, "code": cmd_code, "ask": cmd_ask, "decide": cmd_decide,
            "sheets": cmd_sheets, "gaps": cmd_gaps, "write": cmd_write, "dry": cmd_dry, "status": cmd_status}


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    try:
        return COMMANDS[args.step](args)
    except KeyboardInterrupt:
        return EXIT_DEADLINE


if __name__ == "__main__":
    sys.exit(main())
