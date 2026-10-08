"""``sheets_report.md``: the sheet analysis in tables (docs/milestone10.md §1.6a).

What: documents and their unit checks, regions (class, how it was decided, level, variant, use, registration),
strays, levels and variants, heights (measured or assumed), exterior evidence, conflicts, warnings, needs review and
the AI questions. Simple English, one table per topic.
"""
from __future__ import annotations

from pathlib import Path


def _cell(v) -> str:
    if v is None:
        return "-"
    return str(v).replace("|", "/").replace("\n", " ")


def _val(v) -> str:
    if not v:
        return "-"
    value = v.get("value")
    text = "-" if value is None else f"{value:.2f}"
    if v.get("method") == "assumed":
        text += " (assumed)"
    elif v.get("method"):
        text += f" ({v['method']})"
    return text


def write_report(doc: dict, path: Path, pending: list[str]) -> Path:
    lines = [f"# Sheet analysis: {doc['project']}", ""]
    status = "needs review" if doc["needs_review"] else "ok"
    lines.append(f"Status: **{status}**; {len(doc['regions'])} regions, {len(doc['stray'])} strays, "
                 f"{len(doc['conflicts'])} conflicts; code `{doc.get('code_commit')}`, "
                 f"created {doc.get('created_utc')}")
    lines += ["", "## Documents and units", "",
              "| File | Format | $INSUNITS | Metres per unit | Method | Conflict |", "|---|---|---|---|---|---|"]
    for d in doc["documents"]:
        u = d["units"]
        lines.append(f"| {d['file']} | {d['format']} | {_cell(u.get('insunits'))} | "
                     f"{_cell(u.get('metres_per_unit'))} | {u['method']} | {_cell(u.get('conflict'))} |")
    checks = [(d["file"], c) for d in doc["documents"] for c in d["units"].get("checks") or []]
    if checks:
        lines += ["", "| File | Check | Unit | Score | Samples | Note |", "|---|---|---|---|---|---|"]
        for f, c in checks:
            lines.append(f"| {f} | {c['check']} | {_cell(c['unit'])} | {_cell(c['score'])} | {c['samples']} | "
                         f"{_cell(c.get('note'))} |")
    lines += ["", "## Regions", "",
              "| Region | File | Class | Decided by | Status | Title | Level | Variant | Use | Size (m) | "
              "Registration |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in doc["regions"]:
        title = (r.get("title") or {}).get("text")
        level = (r.get("level") or {}).get("id")
        if r.get("level") and r["level"].get("method") == "assumed":
            level += " (assumed)"
        reg = r.get("registration") or {}
        reg_text = "-"
        if reg:
            reg_text = (f"{reg['method']}, rot {reg.get('rotation_deg', 0):.0f}, shift "
                        f"{reg.get('shift_m')}, residual {_cell(reg.get('residual_m'))}"
                        + (f", stairs {'aligned' if reg['stairs_aligned'] else 'NOT aligned'}"
                           if reg.get("stairs_aligned") is not None else ""))
        size = " x ".join(f"{v:.2f}" for v in r["box_m"]) if r.get("box_m") else "-"
        use = r["use"] + (f" ({r['ignored_reason']})" if r.get("ignored_reason") else "")
        lines.append(f"| {r['id']} | {r['file']} | {r['class']} | {r['class_method']} "
                     f"({r['class_confidence']:.2f}) | {r['status']} | {_cell(title)} | {_cell(level)} | "
                     f"{_cell(r.get('variant'))} | {_cell(use)} | {size} | {_cell(reg_text)} |")
    lines += ["", "## Strays", ""]
    if doc["stray"]:
        lines += ["| File | Entity | Type | Layer | Distance (m) | Reason |", "|---|---|---|---|---|---|"]
        for s in doc["stray"]:
            lines.append(f"| {s['file']} | {s['entity']} | {s['type']} | {_cell(s.get('layer'))} | "
                         f"{_cell(s.get('distance_m'))} | {_cell(s['reason'])} |")
    else:
        lines.append("None.")
    lines += ["", "## Levels and variants", "", "| Level | Order | Label | Kind | Base region | Alternatives |",
              "|---|---|---|---|---|---|"]
    for lv in doc["levels"]:
        alts = ", ".join(f"{a['level_id']} {a['region']} '{a['variant']}'" + (" (base unclear)" if a.get(
            "base_unclear") else "") for a in lv["alternatives"]) or "-"
        lines.append(f"| {lv['id']} | {lv['order']} | {lv['label']} | {lv['kind']} | {lv['base_region']} | {alts} |")
    lines += ["", "| Variant | Label | Levels | Regions |", "|---|---|---|---|"]
    for v in doc["variants"]:
        lines.append(f"| {v['id']} | {v['label']} | {', '.join(v['levels'])} | {', '.join(v['regions'])} |")
    h = doc["heights"]
    lines += ["", "## Heights", "", f"Sections: {', '.join(h.get('section_regions') or []) or 'none'}; cut axis "
              f"{_cell(h.get('cut_axis'))}; datum {_val(h.get('datum'))}", "",
              "| Level | Floor z | Ceiling | Floor to floor | Level mark |", "|---|---|---|---|---|"]
    for lv in h["levels"]:
        lines.append(f"| {lv['level_id']} | {_val(lv.get('floor_z'))} | {_val(lv.get('ceiling_height'))} | "
                     f"{_val(lv.get('floor_to_floor'))} | {_val(lv.get('level_mark'))} |")
    lines += ["", "| Slab between | Top z | Thickness |", "|---|---|---|"]
    for s in h["slabs"]:
        lines.append(f"| {' / '.join(_cell(x) for x in s['between'])} | {_val(s['z_top'])} | {_val(s['thickness'])} |")
    roof = h.get("roof") or {}
    lines += ["", "| Roof | Value |", "|---|---|"]
    for key in ("eaves_z", "ridge_z", "overhang", "thickness", "knee_wall"):
        note = (roof.get(key) or {}).get("note")
        lines.append(f"| {key} | {_val(roof.get(key))}{' - ' + note if note else ''} |")
    lines.append(f"| pitches | {', '.join(_val(p) for p in roof.get('pitches_deg') or []) or '-'} |")
    for g in h.get("ground") or []:
        lines.append(f"| ground {g['side']} | {_val(g['z'])} |")
    ex = doc["exterior"]
    lines += ["", "## Exterior", ""]
    roof_ex = ex.get("roof")
    if roof_ex:
        lines.append(f"Roof: **{roof_ex['type']}** ({roof_ex['type_source']})" +
                     (f"; {roof_ex['note']}" if roof_ex.get("note") else ""))
    else:
        lines.append("Roof: nothing drawn.")
    site = ex.get("site")
    site_text = "no" if not site else "registered (site_outline)" if site.get("registered") else "not registered"
    lines.append(f"Facade entries: {len(ex.get('facade') or [])}; elevations: {len(ex.get('openings_seen') or [])}; "
                 f"site plan: {site_text}; north: {_val(ex.get('north'))}")
    lines += ["", "## Conflicts", ""]
    if doc["conflicts"]:
        lines += ["| Id | Kind | Regions | Description | Resolution |", "|---|---|---|---|---|"]
        for c in doc["conflicts"]:
            lines.append(f"| {c['id']} | {c['kind']} | {', '.join(c.get('regions') or [])} | {_cell(c['description'])} "
                         f"| {_cell(c['resolution'])} |")
    else:
        lines.append("None.")
    lines += ["", "## Needs review", ""]
    lines += [f"- {_cell(n['reason'])}" for n in doc["needs_review"]] or ["None."]
    lines += ["", "## AI questions", "",
              f"{doc.get('questions', 0)} `sheet_region` questions (`sheets/requests.json`); "
              f"{len(pending)} waiting for answers; answers folder: {_cell(doc.get('answers'))}."]
    lines += ["", "## Warnings", ""]
    lines += [f"- {_cell(w)}" for w in doc["warnings"]] or ["None."]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
