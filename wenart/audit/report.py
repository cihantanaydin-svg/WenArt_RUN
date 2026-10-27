"""Argus's report: every line's findings in one place, by problem kind, with the problem log across runs (26 Oct 2026).

What:

- ``run(inp)`` runs every line on one project's records (``inputs.Inputs``): conservation (C*), process (P*), the
  model review (M*), the inspector's last code and vision findings, the judge (J*: a view a client would not accept
  and the problems it names), and the lines a module adds through ``LINE_MODULES`` (``ledger``, ``plan_vs_model``:
  a module with ``run(inp) -> {"findings", "checked"}``) or a JSON file it left in the orchestrator folder
  (``<line>.json``, e.g. the AI auditor's ``argus_ai.json``). A line that cannot run is listed with the reason; none
  is skipped silently.
- ``merge`` joins the findings of different lines about one target and one kind (the highest severity, every line
  and check that saw it in ``seen_by``): one problem, one row.
- ``score`` is Argus's number (0-100, 100 = nothing open): ``100 / (1 + points / SCALE)``, ``POINTS`` per severity.
- ``write`` puts ``argus.json`` and ``argus.md`` in the orchestrator folder: the verdict, the kinds table (where each
  kind arises, its guards, how many findings and how many have a fix the run can carry out), every finding grouped by
  kind with its owner and fix (no cap), the warnings by rule, the records Argus could not read.
- ``update_log`` adds the run to the problem log (``results/argus/problem_log.json``): every finding's signature
  (project, check, target) with the runs it was seen in; a signature seen in ``RECURRING`` runs or more is
  recurring, and a kind with recurring findings needs a new guard (``prevention``): the report names them so the
  next fix is a rule, not a patch.
"""
from __future__ import annotations

import importlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from wenart.audit import conservation as CV
from wenart.audit import inputs as I
from wenart.audit import kinds as K
from wenart.audit import process as PR

NAME = "Argus"
REPORT_JSON = "argus.json"
REPORT_MD = "argus.md"
LOG_FILE = Path("results/argus/problem_log.json")
LINE_MODULES = ("wenart.audit.sense", "wenart.audit.render_check", "wenart.audit.consistency", "wenart.audit.ledger")
LINE_FILES = ("ledger.json", "plan_vs_model.json", "argus_ai_final.json", "argus_ai.json")
POINTS = {"critical": 10.0, "major": 3.0, "minor": 0.5, "info": 0.0}
SCALE = 50.0                          # a house with 2 major and 5 minor points open scores about 85
JUDGE_LOW = 2                         # a view the judge scores this or lower is a finding (a client would not accept it)
RECURRING = 2                         # a signature seen in this many runs or more is recurring


def _norm(f: dict, line: str, default_check: str) -> dict:
    """A finding of an existing line in Argus's format (``kinds.finding``)."""
    return K.finding(line, str(f.get("check") or default_check), str(f.get("severity") or "minor"),
                     f.get("target") or f.get("room_id") or f.get("room") or f.get("view") or "building",
                     str(f.get("message") or f.get("what") or ""),
                     evidence={k: f[k] for k in ("view", "room", "room_id", "metrics", "cause", "source") if f.get(k)},
                     owner=f.get("owner") or f.get("cause"), fix=f.get("fix"), kind=f.get("kind"))


def model_line(inp: I.Inputs) -> dict:
    rec = inp.model_review
    if rec is None:
        return {"findings": [], "checked": {}, "note": "no model_review.json"}
    return {"findings": [_norm(f, "model", "M?") for f in rec.get("findings") or []],
            "checked": {k: (v or {}).get("checked") for k, v in (rec.get("checks") or {}).items()}}


def inspector_line(inp: I.Inputs) -> dict:
    rec = inp.inspector
    if rec is None:
        return {"findings": [], "checked": {}, "note": "no inspector.json"}
    found = [_norm(f, "inspector", "Q?") for f in (rec.get("code") or []) + (rec.get("vision") or [])]
    return {"findings": found, "checked": {"round": rec.get("round"), **(rec.get("counts") or {})}}


def judge_line(inp: I.Inputs) -> dict:
    rows = inp.rubric
    if not rows:
        return {"findings": [], "checked": {}, "note": "no rubric_per_view.json (the big loop did not measure)"}
    out = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        s = r.get("client_ready_score")
        if isinstance(s, int) and s <= JUDGE_LOW:
            out.append(K.finding("judge", "J1", "major", r.get("view"),
                                 f"the judge scores view {r.get('view')} {s}/5 (a client would not accept it): "
                                 f"{r.get('note') or ''}", evidence={"tags": r.get("tags")}, owner="agent",
                                 kind="taste"))
        for p in r.get("problems") or []:
            if isinstance(p, dict):
                out.append(_norm(dict(p, view=r.get("view")), "judge", "J2"))
    scores = [r.get("client_ready_score") for r in rows if isinstance(r, dict)
              and isinstance(r.get("client_ready_score"), int)]
    return {"findings": out, "checked": {"views": len(rows),
                                         "mean": round(sum(scores) / len(scores), 2) if scores else None}}


def module_line(name: str, inp: I.Inputs) -> Optional[dict]:
    """A line from a module (``LINE_MODULES``): None when the module does not exist."""
    try:
        mod = importlib.import_module(name)
    except ImportError:
        return None
    fn = getattr(mod, "run", None)
    if fn is None:
        return {"findings": [], "checked": {}, "note": f"{name} has no run(inp)"}
    try:
        res = fn(inp) or {}
    except Exception as exc:  # noqa: BLE001 - a line that fails is listed, the others still run
        return {"findings": [], "checked": {}, "note": f"failed: {type(exc).__name__}: {exc}"}
    found = [f if f.get("kind") in K.KINDS and f.get("line") else _norm(f, name.rsplit(".", 1)[-1], "?")
             for f in res.get("findings") or []]
    return {"findings": found, "checked": res.get("checked") or {}, "note": res.get("note")}


def file_line(inp: I.Inputs, fname: str) -> Optional[dict]:
    path = (inp.root / "orchestrator" / fname) if inp.layout == "pod" else (inp.root / "agent" / inp.project / fname)
    rec = I.read_json(path) if path.is_file() else None
    if rec is None:
        return None
    line = fname[:-5]
    found = [f if f.get("kind") in K.KINDS and f.get("line") else _norm(f, line, "?") for f in rec.get("findings") or []]
    return {"findings": found, "checked": rec.get("checked") or {}, "note": rec.get("note")}


def lines(inp: I.Inputs) -> dict:
    """``{line: {"findings", "checked", "note"}}`` of every line (module docstring)."""
    out = {}
    cons = CV.audit(inp.stages, inp.manifest)
    out["conservation"] = {"findings": cons["findings"], "checked": cons["checked"],
                           "note": None if inp.stages else "no stage buildings found"}
    proc = PR.audit(inp)
    out["process"] = {"findings": proc["findings"], "checked": proc["checked"],
                      "warning_counts": proc["warning_counts"], "unmatched": proc["unmatched"]}
    out["model"] = model_line(inp)
    out["inspector"] = inspector_line(inp)
    out["judge"] = judge_line(inp)
    for name in LINE_MODULES:
        res = module_line(name, inp)
        if res is not None:
            out[name.rsplit(".", 1)[-1]] = res
    for fname in LINE_FILES:
        line = "argus_ai" if fname.startswith("argus_ai") else fname[:-5]   # the final pass replaces the first
        if line in out:
            continue
        res = file_line(inp, fname)
        if res is not None:
            out[line] = res
    return out


def merge(findings: list[dict]) -> list[dict]:
    """One row per (target, kind): the highest severity; ``seen_by`` lists every line:check that found it; the first
    finding's message, the other messages in ``also``; the first fix any of them names."""
    rows: dict = {}
    order = []
    for f in findings:
        key = (str(f.get("target")), f.get("kind"))
        if f.get("severity") == "info" or str(f.get("target")) in ("building", "run", "None"):
            key = (key[0], key[1], f.get("line"), f.get("check"), len(order))   # never merged
        row = rows.get(key)
        tag = f"{f.get('line')}:{f.get('check')}"
        if row is None:
            row = dict(f, seen_by=[tag], also=[])
            rows[key] = row
            order.append(key)
            continue
        if tag not in row["seen_by"]:
            row["seen_by"].append(tag)
        if K.SEVERITY_RANK.get(f.get("severity"), 0) > K.SEVERITY_RANK.get(row.get("severity"), 0):
            row["also"].append(row["message"])
            row.update(severity=f["severity"], message=f["message"], line=f["line"], check=f["check"])
        elif f.get("message") and f["message"] != row["message"]:
            row["also"].append(f["message"])
        row["fix"] = row.get("fix") or f.get("fix")
        row["owner"] = row.get("owner") or f.get("owner")
    return [rows[k] for k in order]


# The findings that are defects of the house itself (the big loop's house score): the kinds and lines below; the
# geometry of the pieces is the code critic's own part of the score, the run's own state (tests, time) is not the house
HOUSE_KINDS = ("lost", "untyped", "misread", "no_sense", "silent")
HOUSE_LINES = ("conservation", "process", "sense", "ledger", "source", "plan_vs_model", "elevations", "render",
               "argus_ai")
NOT_HOUSE_CHECKS = ("P1", "P3", "P4", "P8", "P9")


def house_findings(rep: dict) -> list[dict]:
    """The critical and major findings of ``rep`` that are defects of the house (``HOUSE_KINDS`` from
    ``HOUSE_LINES``): the big loop counts them in the house score (``judge.house_score``)."""
    return [f for f in rep.get("findings") or [] if f.get("severity") in ("critical", "major")
            and f.get("kind") in HOUSE_KINDS and f.get("line") in HOUSE_LINES and f.get("check") not in NOT_HOUSE_CHECKS]


def score(findings: list[dict]) -> float:
    points = sum(POINTS.get(f.get("severity"), 0.0) for f in findings)
    return round(100.0 / (1.0 + points / SCALE), 1)


def guards_of(inp: I.Inputs) -> list[dict]:
    """The general rules Argus AI proposed in this run (``argus_ai.json`` and ``argus_ai_final.json``), one per text."""
    out, seen = [], set()
    for fname in ("argus_ai.json", "argus_ai_final.json"):
        path = (inp.root / "orchestrator" / fname) if inp.layout == "pod" else (inp.root / "agent" / inp.project / fname)
        rec = I.read_json(path) if path.is_file() else None
        for g in (rec or {}).get("guards") or []:
            key = " ".join(str(g.get("rule") or "").lower().split())
            if key and key not in seen:
                seen.add(key)
                out.append({k: g.get(k) for k in ("kind", "cause", "rule", "check", "target")})
    return out


def own_edits(inp: I.Inputs) -> dict:
    """Argus's own edits of this run in the agent's log (call ids ``argus-r<round>-<n>``, ``loop.argus_session``):
    ``{"tried", "accepted", "tools": {tool: [tried, accepted]}}``."""
    from wenart.audit import process as PR

    out = {"tried": 0, "accepted": 0, "tools": {}, "refusals": {}}
    for e in PR._run_events(inp.agent_log):
        if e.get("kind") not in ("edit", "rejected_edit") or not str(e.get("call_id") or "").startswith("argus-"):
            continue
        ok = e.get("kind") == "edit"
        out["tried"] += 1
        out["accepted"] += ok
        t = out["tools"].setdefault(str(e.get("tool")), [0, 0])
        t[0] += 1
        t[1] += ok
        if not ok:                    # 27 Oct 2026: why code refused it, for the next run's prompt (history_lines)
            why = re.sub(r"[0-9]+(\.[0-9]+)?", "N", PR._refusal(e))[:120] or "no reason given"
            r = out["refusals"].setdefault(str(e.get("tool")), {})
            r[why] = r.get(why, 0) + 1
    return out


def run(inp: I.Inputs) -> dict:
    """The audit of one project (module docstring)."""
    per_line = lines(inp)
    allf = [f for res in per_line.values() for f in res.get("findings") or []]
    rows = merge(allf)
    sev = {s: sum(1 for f in rows if f.get("severity") == s) for s in K.SEVERITIES}
    by_kind = {}
    for f in rows:
        k = by_kind.setdefault(f["kind"], {s: 0 for s in K.SEVERITIES} | {"fixable": 0, "owners": []})
        k[f["severity"]] = k.get(f["severity"], 0) + 1
        if f.get("fix") and f["severity"] != "info":
            k["fixable"] += 1
        if f.get("owner") and f["owner"] not in k["owners"]:
            k["owners"].append(f["owner"])
    return {"name": NAME, "project": inp.project, "layout": inp.layout, "root": str(inp.root),
            "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "run_id": (inp.run_manifest or {}).get("run_id") or (inp.run_manifest or {}).get("job"),
            "score": score(rows), "severity": sev, "by_kind": by_kind,
            "lines": {n: {"findings": len(r.get("findings") or []), "checked": r.get("checked"),
                          "note": r.get("note")} for n, r in per_line.items()},
            "warning_counts": per_line["process"].get("warning_counts"),
            "unmatched_warnings": per_line["process"].get("unmatched") or [],
            "missing": list(inp.missing), "guards": guards_of(inp), "own_edits": own_edits(inp), "findings": rows}


# ---------------------------------------------------------------------------------------------------- problem log
def signature(project: str, f: dict) -> str:
    return f"{project}|{f.get('line')}:{f.get('check')}|{f.get('target')}"


def update_log(rep: dict, path: Path = LOG_FILE) -> dict:
    """Add this run to the problem log (module docstring); returns the log. A run already in the log is replaced."""
    path = Path(path)
    log = I.read_json(path) or {"runs": [], "signatures": {}, "kinds": {}}
    run_id = rep.get("run_id") or rep.get("created_utc")
    project = rep.get("project")
    if any(r.get("run_id") == run_id and r.get("project") == project for r in log["runs"]):
        for sig in log["signatures"].values():
            sig["runs"] = [r for r in sig["runs"] if r != run_id]
        log["runs"] = [r for r in log["runs"] if not (r.get("run_id") == run_id and r.get("project") == project)]
    own = rep.get("own_edits") or {}
    log["runs"].append({"run_id": run_id, "project": project, "score": rep.get("score"),
                        "severity": rep.get("severity"), "created_utc": rep.get("created_utc"),
                        "own_edits": {t: list(v) for t, v in (own.get("tools") or {}).items()},
                        "own_refusals": {t: dict(sorted(r.items(), key=lambda kv: -kv[1])[:OWN_REFUSALS_KEPT])
                                         for t, r in (own.get("refusals") or {}).items()}})
    for f in rep.get("findings") or []:
        if f.get("severity") == "info":
            continue
        sig = log["signatures"].setdefault(signature(project, f), {"kind": f.get("kind"), "runs": [],
                                                                   "severity": f.get("severity"),
                                                                   "message": f.get("message")})
        if run_id not in sig["runs"]:
            sig["runs"].append(run_id)
        sig.update(kind=f.get("kind"), severity=f.get("severity"), message=f.get("message"), last=run_id)
    for g in rep.get("guards") or []:
        key = " ".join(str(g.get("rule") or "").lower().split())
        entry = log.setdefault("guards", {}).setdefault(key, dict(g, runs=[]))
        if run_id not in entry["runs"]:
            entry["runs"].append(run_id)
    kinds: dict = {}
    for sig in log["signatures"].values():
        k = kinds.setdefault(sig["kind"], {"signatures": 0, "recurring": 0})
        k["signatures"] += 1
        k["recurring"] += 1 if len(sig["runs"]) >= RECURRING else 0
    log["kinds"] = kinds
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(log, indent=1, ensure_ascii=False), encoding="utf-8")
    return log


OWN_REFUSALS_KEPT = 4           # refusal reasons kept per tool and run in the problem log


def own_record(log: dict, project: Optional[str] = None, runs: int = 3) -> dict:
    """27 Oct 2026 (user: "give it more power"; Argus learns from its own edits): ``{tool: {"tried", "accepted",
    "refusals": {why: n}}}`` over the last ``runs`` runs of ``project`` (every project when None) in the problem log."""
    rows = [r for r in (log or {}).get("runs") or [] if project is None or r.get("project") == project]
    out: dict = {}
    for r in rows[-runs:]:
        for tool, (tried, ok) in (r.get("own_edits") or {}).items():
            e = out.setdefault(tool, {"tried": 0, "accepted": 0, "refusals": {}})
            e["tried"] += int(tried)
            e["accepted"] += int(ok)
        for tool, why in (r.get("own_refusals") or {}).items():
            e = out.setdefault(tool, {"tried": 0, "accepted": 0, "refusals": {}})
            for k, n in why.items():
                e["refusals"][k] = e["refusals"].get(k, 0) + int(n)
    return out


def recurring(log: dict, project: Optional[str] = None) -> list[tuple[str, dict]]:
    return sorted(((s, v) for s, v in (log or {}).get("signatures", {}).items()
                   if len(v.get("runs") or []) >= RECURRING and (project is None or s.startswith(project + "|"))),
                  key=lambda kv: -len(kv[1]["runs"]))


def prevention(rep: dict, log: Optional[dict] = None) -> list[dict]:
    """Per kind with open findings: its guards, how many findings have a fix the run carries out, and the ones that
    need a new guard (no fix, or recurring)."""
    out = []
    rec = dict(recurring(log or {}, rep.get("project")))
    for kind, c in sorted(rep.get("by_kind", {}).items(), key=lambda kv: -(kv[1]["critical"] * 100 + kv[1]["major"])):
        open_n = c["critical"] + c["major"] + c["minor"]
        if not open_n:
            continue
        need = [f for f in rep["findings"] if f["kind"] == kind and f["severity"] in ("critical", "major")
                and (not f.get("fix") or signature(rep["project"], f) in rec)]
        proposed = sorted((g for g in (log or {}).get("guards", {}).values() if g.get("kind") == kind),
                          key=lambda g: -len(g.get("runs") or []))
        proposed = proposed or [g for g in rep.get("guards") or [] if g.get("kind") == kind]
        out.append({"kind": kind, "what": K.KINDS.get(kind, {}).get("what"),
                    "rules_proposed": [{"rule": g.get("rule"), "runs": len(g.get("runs") or [1])} for g in proposed],
                    "arises": K.KINDS.get(kind, {}).get("arises"), "guards": K.KINDS.get(kind, {}).get("guards"),
                    "open": open_n, "fixable": c["fixable"],
                    "needs_guard": [{"target": f["target"], "check": f"{f['line']}:{f['check']}",
                                     "message": f["message"][:200],
                                     "recurring": signature(rep["project"], f) in rec} for f in need]})
    return out


# ---------------------------------------------------------------------------------------------------- output
def _cell(text) -> str:
    return str(text if text is not None else "").replace("|", "/").replace("\n", " ")


def report_md(rep: dict, prev: Optional[list] = None) -> str:
    sev = rep["severity"]
    lines_ = [f"# {NAME}: the audit of {rep['project']}", "",
              f"Argus checks everything a run makes, not only the looks: what the documents hold against the model "
              f"(nothing lost between stages, every label and symbol used), the run itself (stages, warnings nobody "
              f"acted on, tests, time), the model's sense, the inspector's and the judge's findings. Every finding "
              f"has a kind (where such problems arise and the guards that catch them), an owner (the stage that "
              f"caused it) and, where the run can carry it out, a fix.", "",
              f"Score **{rep['score']}** / 100 (100 = nothing open; {POINTS['critical']:g} points per critical, "
              f"{POINTS['major']:g} per major, {POINTS['minor']:g} per minor). Open: {sev['critical']} critical, "
              f"{sev['major']} major, {sev['minor']} minor; {sev['info']} notes."
              + (f" Argus's own edits this run: {rep['own_edits']['accepted']} of {rep['own_edits']['tried']} accepted "
                 f"by code ({', '.join(f'{k} {v[1]}/{v[0]}' for k, v in sorted(rep['own_edits']['tools'].items()))})."
                 if (rep.get("own_edits") or {}).get("tried") else ""), "",
              "## Lines", "", "| line | findings | checked | note |", "|---|---|---|---|"]
    for n, r in rep["lines"].items():
        lines_.append(f"| {n} | {r['findings']} | {_cell(json.dumps(r.get('checked'), ensure_ascii=False)[:160])} | "
                      f"{_cell(r.get('note') or '')} |")
    lines_ += ["", "## Problem kinds", "",
               "| kind | critical | major | minor | with a fix | owners | arises | guards |",
               "|---|---|---|---|---|---|---|---|"]
    for kind, c in sorted(rep["by_kind"].items(), key=lambda kv: -(kv[1]["critical"] * 100 + kv[1]["major"] * 10
                                                                    + kv[1]["minor"])):
        kd = K.KINDS.get(kind, {})
        lines_.append(f"| {kind} | {c['critical']} | {c['major']} | {c['minor']} | {c['fixable']} | "
                      f"{_cell(', '.join(c['owners'][:6]))} | {_cell(kd.get('arises'))} | "
                      f"{_cell(', '.join(kd.get('guards') or []))} |")
    order = {"critical": 0, "major": 1, "minor": 2, "info": 3}
    for kind in sorted({f["kind"] for f in rep["findings"]}):
        rows = sorted((f for f in rep["findings"] if f["kind"] == kind),
                      key=lambda f: (order.get(f["severity"], 4), str(f["target"])))
        lines_ += ["", f"## {kind}: {K.KINDS.get(kind, {}).get('what', '')}", "",
                   "| severity | target | what | seen by | owner | fix |", "|---|---|---|---|---|---|"]
        lines_ += [f"| {f['severity']} | {_cell(f['target'])} | {_cell(f['message'][:400])} | "
                   f"{_cell(', '.join(f.get('seen_by') or []))} | {_cell(f.get('owner'))} | {_cell(f.get('fix'))} |"
                   for f in rows]
    if prev:
        lines_ += ["", "## Prevention: the kinds to guard", "",
                   "Each open kind with the findings no fix of the run covers, or that came back from an earlier run: "
                   "these need a new rule or check (a general one, for every project), not a one-off patch.", ""]
        for p in prev:
            lines_.append(f"- **{p['kind']}** ({p['open']} open, {p['fixable']} with a fix; arises: {p['arises']}; "
                          f"guards: {', '.join(p['guards'] or []) or 'none'})")
            lines_ += [f"  - {'RECURRING ' if n['recurring'] else ''}{n['check']} {n['target']}: {n['message']}"
                       for n in p["needs_guard"]]
            lines_ += [f"  - rule proposed by Argus AI ({g['runs']} run(s)): {g['rule']}" for g in p.get("rules_proposed")
                       or []]
    wc = rep.get("warning_counts") or {}
    if wc:
        lines_ += ["", "## Warnings by rule", "", "Every warning of the reading, the build and the site, matched to a "
                   "rule (``process.WARN_RULES``); 'other' = no rule yet.", "",
                   ", ".join(f"{k} {v}" for k, v in sorted(wc.items(), key=lambda kv: -kv[1]))]
    if rep.get("unmatched_warnings"):
        lines_ += ["", "Warnings no rule knows yet (Argus AI reads each one; a new rule in ``process.WARN_RULES`` "
                   "when one keeps coming):", ""] + [f"- {_cell(w)[:300]}" for w in rep["unmatched_warnings"]]
    if rep.get("missing"):
        lines_ += ["", f"Records Argus could not read: {', '.join(rep['missing'])}."]
    return "\n".join(lines_) + "\n"


def out_dir(inp: I.Inputs) -> Path:
    return inp.root / "orchestrator" if inp.layout == "pod" else inp.root / "agent" / inp.project


def write(rep: dict, odir: Path, prev: Optional[list] = None) -> None:
    odir = Path(odir)
    odir.mkdir(parents=True, exist_ok=True)
    (odir / REPORT_JSON).write_text(json.dumps(dict(rep, prevention=prev or []), indent=1, ensure_ascii=False),
                                    encoding="utf-8")
    (odir / REPORT_MD).write_text(report_md(rep, prev), encoding="utf-8")
