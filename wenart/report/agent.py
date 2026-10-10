"""The "AI orchestrator" section of the final report (docs/milestone11.md §8 "report", §9, §13 step 7; CLAUDE.md:
"Every inferred item is listed in the report").

What: ``agent_block(project_out, out_dir, private)`` reads ``orchestrator/log.json`` and ``overrides.json``, the
building the run rendered and the ``agent`` stage record, and returns the manifest block:

- ``rounds``: per round the findings by severity, the dropped vision findings, accepted / rejected edits, the stage
  re-run from, the re-rendered views, seconds; ``stop``: why the loop stopped;
- ``findings_by_check``: per checklist id the critical / major / minor / dropped counts over all rounds;
- ``edits`` (accepted, with label, reason, score before -> after, re-run stage) and ``rejected`` (with the failed
  checks), ``rolled_back`` (edits a refit refused);
- ``inferred``: every piece or room marked ``inferred``, ``adjusted_by_ai`` or ``corrected_by_ai`` in the
  rendered building, and the record-only geometry corrections (open items for the next full run);
- ``before_after``: per re-rendered view the preview before and after its round (copied into
  ``final/agent/`` for a public project; a private one keeps them on the volume, names only);
- ``minutes``: the agent stages' seconds / 60; ``model``, ``revision``, model calls and tokens;
- ``comparison``: the old-pipeline vs orchestrator table (``compare_rows``), filled once the pods deliver both
  sets of images (``orchestrator/compare.json`` or the ``--old-final`` folder of ``write_compare``).

``agent_lines(manifest)`` renders it as markdown; both return nothing for a run without the orchestrator, so the
M10 report is unchanged.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Optional

from wenart.report import common as C

AGENT_DIR = "orchestrator"
FINAL_AGENT_DIR = "agent"            # final/agent/: the before/after images of a public project
COMPARE_JSON = "compare.json"
SEVERITIES = ("critical", "major", "minor")


def _read(path) -> Optional[dict]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def inferred_items(building: Optional[dict], overrides: Optional[dict]) -> list[dict]:
    out = []
    for f in (building or {}).get("furniture") or []:
        labels = [k for k in ("inferred", "adjusted_by_ai", "corrected_by_ai") if f.get(k)]
        if labels:
            adj = f.get("adjusted_by_ai") if isinstance(f.get("adjusted_by_ai"), dict) else {}
            out.append({"id": f.get("id"), "kind": "piece", "type": f.get("type"), "room_id": f.get("room_id"),
                        "labels": labels, "reason": adj.get("reason"), "drawn_type": f.get("drawn_type")})
    for r in (building or {}).get("rooms") or []:
        labels = [k for k in ("inferred", "corrected_by_ai") if r.get(k)]
        if labels:
            cor = r.get("corrected_by_ai") if isinstance(r.get("corrected_by_ai"), dict) else {}
            out.append({"id": r.get("id"), "kind": "room", "type": r.get("room_type"), "room_id": r.get("id"),
                        "labels": labels, "reason": cor.get("reason")})
    for e in (overrides or {}).get("edits") or []:
        if e.get("tool") == "correct_geometry" and (e.get("result") or {}).get("accepted"):
            a = e.get("args") or {}
            out.append({"id": a.get("opening_id") or ",".join(a.get("wall_ids") or []), "kind": "geometry",
                        "type": a.get("kind"), "room_id": None, "labels": ["corrected_by_ai", "record_only"],
                        "reason": a.get("reason")})
    return out


def _copy_image(src: Path, final_dir: Path, private: bool, root: Optional[Path] = None) -> Optional[str]:
    """The before/after image as a link inside ``final/`` (public), or its path in the project output on the volume
    (private: never copied, as the plan crops of M6 §7.4)."""
    if not src.is_file():
        return None
    if private:
        try:
            return src.resolve().relative_to(Path(root).resolve()).as_posix() if root is not None else src.name
        except ValueError:
            return src.name
    dst = final_dir / FINAL_AGENT_DIR / src.name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    return f"{FINAL_AGENT_DIR}/{src.name}"


def compare_rows(project_out: Path, final_dir: Path, private: bool) -> Optional[dict]:
    """The old-pipeline vs orchestrator table: ``orchestrator/compare.json`` = ``{"old_run": text, "views":
    [{"view", "old", "new", "note"}]}`` (paths relative to the project output), written by ``write_compare`` once
    the pods deliver the images; None when there is none yet."""
    data = _read(Path(project_out) / AGENT_DIR / COMPARE_JSON)
    if data is None:
        return None
    rows = []
    for v in data.get("views") or []:
        row = {"view": v.get("view"), "note": v.get("note")}
        for side in ("old", "new"):
            src = Path(project_out) / str(v.get(side) or "")
            row[side] = _copy_image(src, final_dir, private, project_out) if v.get(side) else None
        rows.append(row)
    return {"old_run": data.get("old_run"), "views": rows}


def write_compare(project_out, old_final, old_run: str = "") -> dict:
    """``orchestrator/compare.json`` from an old run's ``final/`` folder (``<cam>_final_preview.jpg``, copied to
    ``orchestrator/compare/``) and this output's ``final/`` (the same camera names)."""
    project_out, old_final = Path(project_out), Path(old_final)
    folder = project_out / AGENT_DIR / "compare"
    folder.mkdir(parents=True, exist_ok=True)
    views = []
    for old in sorted(old_final.glob("*_final_preview.jpg")):
        cam = old.name[: -len("_final_preview.jpg")]
        new = project_out / "final" / old.name
        dst = folder / f"{cam}_old.jpg"
        shutil.copyfile(old, dst)
        views.append({"view": cam, "old": dst.relative_to(project_out).as_posix(),
                      "new": new.relative_to(project_out).as_posix() if new.is_file() else None})
    data = {"old_run": old_run or str(old_final), "views": views}
    C.write_json(project_out / AGENT_DIR / COMPARE_JSON, data)
    return data


def agent_block(project_out, out_dir, private: bool = False, building: Optional[dict] = None) -> Optional[dict]:
    project_out = Path(project_out)
    log = _read(project_out / AGENT_DIR / "log.json")
    if log is None:
        return None
    overrides = _read(project_out / AGENT_DIR / "overrides.json") or {"edits": []}
    events = log.get("events") or []
    rounds: dict = {}
    by_check: dict = {}
    for e in events:
        r = rounds.setdefault(int(e.get("round") or 0), {"round": int(e.get("round") or 0),
                                                          "findings": {s: 0 for s in SEVERITIES}, "dropped": 0,
                                                          "accepted": 0, "rejected": 0, "rerun_from": None,
                                                          "views": [], "rerun_status": None})
        if e["kind"] == "finding":
            row = by_check.setdefault(str(e.get("checklist")), {"critical": 0, "major": 0, "minor": 0, "dropped": 0})
            if e.get("dropped"):
                r["dropped"] += 1
                row["dropped"] += 1
            elif e.get("severity") in SEVERITIES:
                r["findings"][e["severity"]] += 1
                row[e["severity"]] += 1
        elif e["kind"] == "edit":
            r["accepted"] += 1
        elif e["kind"] == "rejected_edit":
            r["rejected"] += 1
        elif e["kind"] == "rerun":
            r["rerun_from"] = e.get("rerun_from")
            r["rerun_status"] = e.get("status")
            r["views"] = list(e.get("views") or [])
    final_dir = Path(out_dir)
    orch = project_out / AGENT_DIR

    def image(rel: Optional[str]) -> Optional[str]:
        return _copy_image(orch / rel, final_dir, private, project_out) if rel else None

    edits, rejected = [], []
    for e in events:
        if e["kind"] not in ("edit", "rejected_edit"):
            continue
        v = e.get("validation") or {}
        row = {"seq": e["seq"], "round": e.get("round"), "tool": e.get("tool"), "target": e.get("target"),
               "label": e.get("label"), "reason": e.get("reason"), "check": e.get("checklist"),
               "score_before": v.get("score_before"), "score_after": v.get("score_after"),
               "rerun_from": e.get("rerun_from")}
        if e["kind"] == "edit":
            row["before"] = image(e.get("before"))
            row["after"] = image(e.get("after"))
            edits.append(row)
        else:
            row["failed_checks"] = list(v.get("failed_checks") or [])
            rejected.append(row)
    before_after = []
    for e in events:
        if e["kind"] == "render" and (e.get("before") or e.get("after")):
            before_after.append({"round": e.get("round"), "view": (e.get("views") or [None])[0],
                                 "before": image(e.get("before")), "after": image(e.get("after"))})
    rolled_back = [{"seq": e["seq"], "round": e.get("round"), "tool": e.get("tool"),
                    "why": (e.get("result") or {}).get("rolled_back")}
                   for e in overrides.get("edits") or [] if (e.get("result") or {}).get("rolled_back")]
    if building is None:
        building = _read(project_out / "building_final.json")
    seconds = 0.0
    for stage in ("agent", "agent_previews", "agent_apply"):
        rec = _read(project_out / "run" / f"{stage}.json")
        if rec and isinstance(rec.get("seconds"), (int, float)):
            seconds += float(rec["seconds"])
    calls = log.get("calls") or []
    tokens = sum(int(c.get("prompt_tokens") or 0) + int(c.get("completion_tokens") or 0) for c in calls)
    # Milestone 12 (§5.5 D20): orchestrator/metrics.json of the run (computed when missing)
    metrics = _read(orch / "metrics.json")
    if metrics is None:
        try:
            from wenart.agent import metrics as MX
            metrics = MX.compute(log, _read(orch / "memory.json"))
        except Exception:  # noqa: BLE001 - the report is written without the metrics
            metrics = None
    gaps = [dict(e.get("args") or {}, seq=e.get("seq")) for e in overrides.get("edits") or []
            if e.get("tool") == "report_library_gap" and (e.get("result") or {}).get("accepted")]
    return {"model": log.get("model"), "revision": log.get("revision"), "stop": log.get("stop"),
            "rounds": [rounds[k] for k in sorted(rounds)], "findings_by_check": dict(sorted(by_check.items())),
            "edits": edits, "rejected": rejected, "rolled_back": rolled_back,
            "inferred": inferred_items(building, overrides), "before_after": before_after,
            "minutes": round(seconds / 60.0, 1), "calls": len(calls), "tokens": tokens,
            "comparison": compare_rows(project_out, final_dir, private), "metrics": metrics,
            "library_gaps": gaps}


def metrics_lines(m: Optional[dict]) -> list[str]:
    """Milestone 12 (§5.5): the agent metrics of the run as a short table."""
    if not m:
        return []
    e, r, f, t, mem = m["edits"], m["rooms"], m["findings"], m["time"], m["memory"]
    share = e.get("accepted_share")
    top = sorted((e.get("rejected_by_reason") or {}).items(), key=lambda kv: (-kv[1], kv[0]))[:5]
    rows = [["edits accepted / rejected", f"{e['accepted']} / {e['rejected']}"
             + (f" ({share * 100:.0f} % accepted)" if share is not None else "")],
            ["rejected by reason", ", ".join(f"{k} {v}" for k, v in top) or "-"],
            ["rooms checked by code / vision / planner", f"{r['code']} / {r['vision']} / {r['planner']}"],
            ["rooms with fixable critical or major findings visited",
             f"{len(set(r.get('planner_rooms') or []) & set(r.get('fixable_rooms') or []))} of {r['fixable']}"],
            ["critical before -> after", f"{f['before_totals']['critical']} -> {f['after_totals']['critical']}"],
            ["major before -> after", f"{f['before_totals']['major']} -> {f['after_totals']['major']}"],
            ["agent minutes; first accepted edit after", f"{t['agent_minutes']}; {t['first_accepted_edit_s']} s"],
            ["repeats refused by the memory; dry runs; plans (valid)",
             f"{mem['repeats_refused']}; {mem['dry_runs']}; {mem['plans']} ({mem['plans_valid']})"]]
    return ["", "### Agent metrics", ""] + C.table(["metric", "value"], rows)


def _img(link: Optional[str]) -> str:
    return f"![]({link})" if link else "-"


def agent_lines(manifest: dict) -> list[str]:
    a = manifest.get("agent")
    if not a:
        return []
    stop = a.get("stop") or {}
    lines = ["", "## AI orchestrator", "",
             f"Model `{a.get('model')}` @ `{a.get('revision')}`: {len(a['rounds'])} round(s), {len(a['edits'])} edit(s) "
             f"accepted, {len(a['rejected'])} rejected, {a['calls']} model calls ({a['tokens']} tokens), "
             f"{a['minutes']} min. Stop: {stop.get('reason') or '-'}. Every edit was checked by code before it was "
             "accepted; the full log is `orchestrator/log.md` on the volume."]
    lines += metrics_lines(a.get("metrics"))
    if a.get("library_gaps"):
        lines += ["", "Library gaps reported by the agent: " + ", ".join(
            f"{g.get('type')} {g.get('style') or ''} ({g.get('reason') or '-'})".replace("  ", " ")
            for g in a["library_gaps"]) + "."]
    lines += ["", "### Rounds", ""]
    lines += C.table(["round", "critical", "major", "minor", "dropped (vision)", "accepted", "rejected", "re-run from",
                      "views"],
                     [[r["round"], r["findings"]["critical"], r["findings"]["major"], r["findings"]["minor"],
                       r["dropped"], r["accepted"], r["rejected"], r["rerun_from"] or "-", len(r["views"])]
                      for r in a["rounds"]])
    if a["findings_by_check"]:
        lines += ["", "### Findings by check", ""]
        lines += C.table(["check", "critical", "major", "minor", "dropped"],
                         [[k, v["critical"], v["major"], v["minor"], v["dropped"]]
                          for k, v in a["findings_by_check"].items()])
    lines += ["", "### Accepted edits", ""]
    if a["edits"]:
        lines += C.table(["#", "round", "tool", "target", "label", "score", "reason", "before", "after"],
                         [[e["seq"], e["round"], e["tool"], e["target"], e["label"] or "-",
                           f"{e['score_before']} -> {e['score_after']}" if e["score_before"] is not None else "-",
                           e["reason"], _img(e.get("before")), _img(e.get("after"))] for e in a["edits"]])
    else:
        lines.append("None.")
    if a["rejected"]:
        lines += ["", "### Rejected edits", ""]
        lines += C.table(["#", "round", "tool", "target", "failed checks", "reason"],
                         [[e["seq"], e["round"], e["tool"], e["target"], ", ".join(e["failed_checks"]) or "-",
                           e["reason"]] for e in a["rejected"]])
    if a["rolled_back"]:
        lines += ["", "Rolled back (the refit refused them): "
                  + ", ".join(f"#{r['seq']} {r['tool']} ({r['why']})" for r in a["rolled_back"]) + "."]
    lines += ["", "### Inferred and AI-changed items", ""]
    if a["inferred"]:
        lines += C.table(["id", "kind", "type", "room", "labels", "reason"],
                         [[i["id"], i["kind"], i["type"], i.get("room_id") or "-", ", ".join(i["labels"]),
                           i.get("reason") or "-"] for i in a["inferred"]])
        if any(i["kind"] == "geometry" for i in a["inferred"]):
            lines.append("")
            lines.append("Geometry corrections are record-only in M11: the drawn geometry was not changed; they are "
                         "open items for the next full run.")
    else:
        lines.append("None.")
    if a["before_after"]:
        lines += ["", "### Before and after (previews of the re-rendered views)", ""]
        lines += C.table(["round", "view", "before", "after"],
                         [[b["round"], b["view"], _img(b["before"]), _img(b["after"])] for b in a["before_after"]])
    comp = a.get("comparison")
    lines += ["", "### Old pipeline vs orchestrator", ""]
    if comp and comp.get("views"):
        lines.append(f"Old run: {comp.get('old_run') or '-'}.")
        lines += [""] + C.table(["view", "old pipeline", "orchestrator", "note"],
                                [[v["view"], _img(v.get("old")), _img(v.get("new")), v.get("note") or "-"]
                                 for v in comp["views"]])
    else:
        lines.append("Not made yet: the images of both runs come from the pods (`orchestrator/compare.json`).")
    return lines
