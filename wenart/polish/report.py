"""Markdown report of a polish manifest (docs/milestone5.md §3.6): ``polish_report.md``.

What: one page a reviewer reads after a pod run: how many views were
polished and why the others kept the Cycles render, every attempt with its
settings, timing and gate decision (failed checks with value and threshold),
the room rule, the per-setting acceptance of a sweep or smoke run, the
prompts, the models with revisions and licences, and every warning. Written
from the manifest alone, so it can be regenerated without a GPU
(``python -m wenart.polish report <manifest>``).
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path


def _num(v, fmt: str = ".3g") -> str:
    if v is None:
        return "-"
    if isinstance(v, (int, float)):
        return format(v, fmt)
    return str(v)


def fmt_check(c: dict) -> str:
    """``edges:f_1 0.81 (needs >= 0.85)`` for one gate reason/note."""
    return (f"{c.get('check', '?')}:{c.get('region', '?')} {_num(c.get('value'))} "
            f"(needs {c.get('op', '?')} {_num(c.get('threshold'))})")


def _decision(rec: dict) -> str:
    if rec.get("error"):
        return f"error: {rec['error']}"
    gate = rec.get("gate")
    if not gate:
        return "not gated"
    return gate.get("decision", "?")


def _failed(rec: dict, limit: int = 4) -> str:
    gate = rec.get("gate") or {}
    items = [fmt_check(c) for c in gate.get("reasons") or []]
    if len(items) > limit:
        items = items[:limit] + [f"+{len(items) - limit} more"]
    return "; ".join(items) or "-"


def _settings(rec: dict) -> str:
    ctrl = rec.get("control") or "none"
    scale = "-" if rec.get("scale") is None else _num(rec["scale"])
    return f"{_num(rec.get('strength'))} / {ctrl} / {scale} / {rec.get('size')} / {rec.get('mode')}"


def _model_rows(models: dict) -> list[str]:
    rows = []
    for role in ("base", "controlnet"):
        m = models.get(role) or {}
        rows.append(f"| polish {role} | {m.get('repo', '-')} | `{str(m.get('revision', '-'))[:12]}` | "
                    f"{m.get('licence', '-')} | {', '.join(m.get('files') or []) or '-'} |")
    for role, m in sorted((models.get("gate") or {}).items()):
        rows.append(f"| gate {role} | {m.get('repo', '-')} | `{str(m.get('revision', '-'))[:12]}` | "
                    f"{m.get('licence', '-')} | - |")
    return rows


def report_markdown(m: dict) -> str:
    """The report text of one polish manifest (run, sweep or smoke)."""
    kind = m.get("kind", "?")
    views = m.get("views") or []
    attempts = [(v, a) for v in views for a in v.get("attempts") or []]
    made = sum(1 for _, a in attempts if a.get("png") and not a.get("reused"))
    reused = sum(1 for _, a in attempts if a.get("reused"))
    lines = [f"# Polish report: {m.get('project', '?')} ({kind})", ""]
    head = (f"{len(views)} views, {len(attempts)} attempts ({made} polished now, {reused} reused). "
            f"Device {m.get('device') or '-'}, torch {m.get('torch') or '-'}, diffusers {m.get('diffusers') or '-'}; "
            f"memory {m.get('memory_mode') or '-'}, peak VRAM {_num(m.get('peak_vram_gib'))} GiB, "
            f"model load {_num(m.get('load_seconds'))} s, prompt encoding {_num(m.get('encode_seconds'))} s, "
            f"{_num(m.get('seconds_per_forward'))} s per forward, run {_num(m.get('seconds'))} s.")
    lines.append(head)
    if m.get("incomplete"):
        lines.append("")
        lines.append("**Incomplete**: the deadline stopped the run; views marked `deadline` keep the Cycles render "
                     "and a rerun continues from the stored attempts.")
    if not m.get("polish_allowed", True):
        lines.append("")
        lines.append("The brief says `polish: false`: every view keeps the Cycles render; nothing was polished.")
    if kind == "run":
        finals = Counter(v.get("final") for v in views)
        reasons = Counter(v.get("reason") for v in views if v.get("final") == "cycles")
        lines += ["", f"Final images: {finals.get('polished', 0)} polished, {finals.get('cycles', 0)} Cycles"
                  + (" (" + ", ".join(f"{r} {n}" for r, n in sorted(reasons.items(), key=lambda x: str(x[0])))
                     + ")" if reasons else "") + ". A polished image is used only when the change gate accepted it "
                  "(and, later, the vision check does not reject it)."]
        lines += ["", "## Views", "",
                  "| camera | room | final | attempt | strength / control / scale / size / mode | gate | "
                  "failed checks | seconds | panes |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for v in views:
            recs = {a["k"]: a for a in v.get("attempts") or []}
            fa = recs.get(v.get("final_attempt")) if v.get("final_attempt") else None
            last = fa or (v.get("attempts") or [None])[-1]
            final = v.get("final") or "-"
            if final == "cycles":
                final += f" ({v.get('reason')})"
            lines.append(f"| {v['camera']} | {v.get('room_id') or '-'} | {final} | "
                         f"{'a' + str(fa['k']) if fa else '-'} | {_settings(last) if last else '-'} | "
                         f"{_decision(last) if last else '-'} | {_failed(last) if last else '-'} | "
                         f"{_num((last or {}).get('seconds'))} | {_num((last or {}).get('panes_restored'), 'd')} |")
        rooms = m.get("rooms") or {}
        lines += ["", "## Room rule", "",
                  "Candidates of one room must have wall Lab means within ΔE 5; otherwise they take the strongest "
                  "rung all of them accept (with agreeing walls) or the Cycles render.", ""]
        if rooms:
            lines += ["| room | rule | rung | ΔE max | ΔE after | candidates |", "|---|---|---|---|---|---|"]
            for room, r in sorted(rooms.items()):
                rung = "cycles" if r.get("rule") == "downgraded" and r.get("rung") is None else (
                    f"a{r['rung']}" if r.get("rung") else "-")
                lines.append(f"| {room} | {r.get('rule')} | {rung} | {_num(r.get('delta_e_max'))} | "
                             f"{_num(r.get('delta_e_after'))} | {', '.join(r.get('candidates') or []) or '-'} |")
        else:
            lines.append("None.")
    else:
        lines += ["", "## Settings", "",
                  "Every setting runs on every view and is gated; nothing stops early.", "",
                  "| k | role | strength / control / scale / size / mode | accepted | views | mean seconds |",
                  "|---|---|---|---|---|---|"]
        by_k: dict = {}
        for v, a in attempts:
            by_k.setdefault(a["k"], []).append(a)
        for k in sorted(by_k):
            recs = by_k[k]
            ok = sum(1 for a in recs if not a.get("error") and (a.get("gate") or {}).get("decision") == "accept")
            secs = [a["seconds"] for a in recs if isinstance(a.get("seconds"), (int, float))]
            mean = sum(secs) / len(secs) if secs else None
            lines.append(f"| a{k} | {recs[0].get('role')} | {_settings(recs[0])} | {ok} | {len(recs)} | "
                         f"{_num(mean)} |")
    lines += ["", "## Attempts", "",
              "| camera | k | role | strength / control / scale / size / mode | seed | sigma0 | forwards | seconds | "
              "decision | failed checks | reused |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for v, a in attempts:
        reuse = "-"
        if a.get("reused"):
            reuse = "png + gate" if a.get("gate_reused") else "png"
        sigma0 = a.get("sigma0") if a.get("sigma0") is not None else a.get("sigma0_numpy")
        lines.append(f"| {v['camera']} | a{a['k']}{' (room rule)' if a.get('room_rule') else ''} | {a.get('role')} | "
                     f"{_settings(a)} | {a.get('seed')} | {_num(sigma0)} | {_num(a.get('forwards'), 'd')} | "
                     f"{_num(a.get('seconds'))} | {_decision(a)} | {_failed(a)} | {reuse} |")
    notes = [(v["camera"], n) for v in views for n in v.get("notes") or []]
    if notes:
        lines += ["", "## Notes", ""] + [f"- {cam}: {n}" for cam, n in notes]
    lines += ["", "## Prompts", ""]
    prompts = [(v["camera"], v.get("prompt")) for v in views if v.get("prompt")]
    lines += [f"- {cam}: {p}" for cam, p in prompts] or ["None (nothing was polished)."]
    lines += ["", "## Models", "", "| role | repo | revision | licence | files |", "|---|---|---|---|---|"]
    lines += _model_rows(m.get("models") or {})
    lines += ["", "## Warnings", ""]
    lines += [f"- {w}" for w in m.get("warnings") or []] or ["None."]
    return "\n".join(lines) + "\n"


def write_report(manifest: dict, path) -> Path:
    """Write ``report_markdown(manifest)`` to ``path`` (UTF-8)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report_markdown(manifest), encoding="utf-8")
    return path
