"""``check/check_report.md``: the vision check in the markdown style of the other reports (§5.7).

Summary table, one row per view, every confirmed mismatch on a Cycles render
with its source and evidence (never auto-fixed; added_by_ai pieces labelled
as a render/polish issue), the JSON cross-check findings, the polished
images rejected and why, unreliable passes, controls, the calibration and
the plan A/B outcome.
"""
from __future__ import annotations

from collections import Counter
from typing import Optional

from wenart.vision_check.calibrate import NOT_ADOPTED_TEXT
from wenart.vision_check.combine import ADDED_BY_AI_NOTE, MISMATCH_RESULTS


def evidence_text(evidence: list) -> str:
    """``file p1 layer MOBILYA INSERT:10A`` of the first evidence entry, ``-`` when none."""
    if not evidence:
        return "-"
    ev = evidence[0]
    parts = [str(ev.get("file") or "?")]
    if ev.get("page"):
        parts.append(f"p{ev['page']}")
    for key in ("layer", "entity", "block"):
        if ev.get(key):
            parts.append(str(ev[key]))
    parts.append(str(ev.get("method") or "?"))
    return " ".join(parts)


def _fmt(v) -> str:
    if v is None:
        return "-"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)


def check_report(manifest: dict, calibration: Optional[dict] = None, expected: Optional[dict] = None) -> str:
    """Markdown report from ``check_manifest.json`` (+ ``check_calibration.json`` when it exists)."""
    project = manifest.get("project") or "?"
    views_out = manifest.get("views") or {}
    keys = manifest.get("model_keys") or []
    models = manifest.get("models") or {}
    cyc = Counter((v.get("cycles") or {}).get("verdict", "not_checked") for v in views_out.values())
    pol = [v for v in views_out.values() if "polished" in v]
    rejected = Counter(v.get("polished_reason") for v in views_out.values() if v.get("polished_rejected"))
    review = [cam for cam, v in views_out.items() if v.get("needs_review")]
    prefs = [v["polished"]["preference"] for v in views_out.values() if (v.get("polished") or {}).get("preference")]
    advisory = manifest.get("advisory")
    adv_reasons = (calibration or {}).get("advisory_reasons") or [manifest.get("advisory_reason") or ""]
    lines = [f"# Vision check report: {project}", ""]
    lines.append(
        f"{len(views_out)} views checked by {len(keys)} model(s) ({', '.join(keys) or '-'}), "
        f"{'single pass' if manifest.get('single_pass') else 'two independent passes'}. "
        f"Verdicts come only from agreeing passes; nothing is auto-fixed. The check is "
        f"{'ADVISORY' if advisory else 'calibrated'}"
        f"{' (' + '; '.join(r for r in adv_reasons if r) + ')' if advisory else ''}: an advisory check is an open "
        f"item that needs the user's OK; the differential decision on polished images stays active.")
    lines += ["", "| item | value |", "|---|---|"]
    for k in keys:
        m = models.get(k) or {}
        lines.append(f"| model {k} | {m.get('id')} @ {str(m.get('revision') or '-')[:12]} ({m.get('licence')}) |")
    lines.append(f"| Cycles verdicts | {', '.join(f'{n} {c}' for c, n in sorted(cyc.items())) or '-'} |")
    lines.append(f"| polished images checked | {len(pol)} |")
    lines.append(f"| polished rejected | {', '.join(f'{r} {n}' for r, n in sorted(rejected.items())) or 'none'} |")
    lines.append(f"| views needing review | {len(review)} |")
    if prefs:
        lines.append(f"| polished preferred (>= {prefs[0]['min_votes']} of 4 votes) | "
                     f"{sum(p['preferred'] for p in prefs)} of {len(prefs)} |")
    lines += ["", "## Per view", "",
              "| camera | room | Cycles | polished | polished decision | preferred | needs review | cross-check |",
              "|---|---|---|---|---|---|---|---|"]
    for cam in sorted(views_out):
        v = views_out[cam]
        cc = v.get("json_crosscheck") or {}
        ccn = sum(len(cc.get(k) or []) for k in ("in_json_not_rendered", "misplaced", "rendered_not_in_json"))
        pref = ((v.get("polished") or {}).get("preference") or {})
        decision = "-" if "polished" not in v else (v.get("polished_reason") or "kept")
        pref_text = "-"
        if pref:
            pref_text = f"{'yes' if pref.get('preferred') else 'no'} ({pref.get('votes')}/{pref.get('answers')})"
        lines.append(f"| {cam} | {v.get('room_id') or '-'} | {(v.get('cycles') or {}).get('verdict', '-')} | "
                     f"{(v.get('polished') or {}).get('verdict', '-')} | {decision} | {pref_text} | "
                     f"{'yes' if v.get('needs_review') else 'no'} | {ccn or '-'} |")

    lines += ["", "## Mismatches on the Cycles renders", ""]
    found = False
    for cam in sorted(views_out):
        c = views_out[cam].get("cycles") or {}
        exp_els = {e["wenart_id"]: e for e in ((expected or {}).get(cam) or {}).get("elements") or []}
        for eid, e in sorted((c.get("elements") or {}).items()):
            if e["result"] not in MISMATCH_RESULTS + ("disputed",):
                continue
            found = True
            ev = evidence_text((exp_els.get(eid) or {}).get("evidence") or [])
            note = ""
            if e.get("source") == "added_by_ai" and e["result"] in MISMATCH_RESULTS:
                note = f" ({ADDED_BY_AI_NOTE})"
            confirmed = "confirmed" if e["result"] in MISMATCH_RESULTS else "not confirmed"
            lines.append(f"- {cam}: {eid} ({e['type']}, {e.get('source') or '-'}, {e['role']}; evidence {ev}): "
                         f"{e['result']} ({confirmed}){note}")
        for x in c.get("extras") or []:
            if x.get("confirmed") and not x.get("info"):
                found = True
                lines.append(f"- {cam}: confirmed extra {x['class']} {sorted(set(x['categories'].values()))} at "
                             f"{[round(b) for b in x['box_px']]}")
        for kind, cnt in (c.get("counts") or {}).items():
            if cnt.get("result") in ("fewer", "more"):
                found = True
                lines.append(f"- {cam}: {kind} count {cnt['result']} than {cnt['expected']} ({cnt['passes']})")
    if not found:
        lines.append("None.")

    lines += ["", "## JSON cross-check (building JSON projected with a depth test)", ""]
    found = False
    for cam in sorted(views_out):
        cc = views_out[cam].get("json_crosscheck") or {}
        if cc.get("error"):
            found = True
            lines.append(f"- {cam}: not computed ({cc['error']})")
        for item in cc.get("in_json_not_rendered") or []:
            found = True
            lines.append(f"- {cam}: in JSON, not rendered: {item['id']} ({item.get('type')}, {item.get('source')}), "
                         f"visible share {item['visible_share']}, area {item['area_frac']}")
        for item in cc.get("misplaced") or []:
            found = True
            if item.get("outside_share") is None:              # a manifest made before the containment test
                lines.append(f"- {cam}: misplaced: {item['id']} ({item.get('type')}), centre off by "
                             f"{float(item.get('offset_frac_w') or 0.0) * 100:.1f} % of the width")
                continue
            lines.append(f"- {cam}: misplaced: {item['id']} ({item.get('type')}), "
                         f"{item['outside_share'] * 100:.0f} % of its {item['pixels']} rendered pixels lie more than "
                         f"{item['margin_m']:.2f} m outside the drawn shape (90th percentile "
                         f"{item['outside_p90_m']:.2f} m)")
        for item in cc.get("rendered_not_in_json") or []:
            found = True
            lines.append(f"- {cam}: rendered, not in JSON: {item['id']} (index {item['index']})")
    if not found:
        lines.append("None.")

    lines += ["", "## Polished images rejected", ""]
    rej = [(cam, v) for cam, v in sorted(views_out.items()) if v.get("polished_rejected")]
    if not rej:
        lines.append("None.")
    for cam, v in rej:
        details = []
        for r in v.get("polished_reasons") or []:
            if r.get("what") == "element":
                details.append(f"{r['id']} ({r['type']}, {r['source']}) {r['cycles']} -> {r['polished']}")
            elif r.get("what") == "added_by_polish":
                details.append(f"added_by_polish {r['class']} {sorted(set(r['categories'].values()))}")
            else:
                details.append(f"{r.get('image')}: {r.get('detail')}")
        lines.append(f"- {cam}: {v.get('polished_reason')}: {'; '.join(details)}")

    lines += ["", "## Realism preference (info only)", ""]
    rows = []
    for cam in sorted(views_out):
        for kind, entry in sorted(views_out[cam].items()):
            if isinstance(entry, dict) and entry.get("preference"):
                p = entry["preference"]
                rows.append(f"| {cam} | {kind} | {p['votes']} / {p['answers']} of {p['asked']} | "
                            f"{'yes' if p['preferred'] else 'no'} |")
    if rows:
        lines += ["| camera | image | votes for the polished image | preferred |", "|---|---|---|---|"] + rows
    else:
        lines.append("None.")

    lines += ["", "## Unreliable or incomplete checks", ""]
    found = False
    for cam in sorted(views_out):
        for kind, entry in sorted(views_out[cam].items()):
            if not isinstance(entry, dict) or "verdict" not in entry:
                continue
            if entry.get("unreliable"):
                found = True
                lines.append(f"- {cam} {kind}: decoy seen by {', '.join(entry['unreliable'])} (unreliable)")
            if entry.get("not_computed"):
                found = True
                lines.append(f"- {cam} {kind}: not computed for {', '.join(entry['not_computed'])}")
    if not found:
        lines.append("None.")

    controls = []
    for cam in sorted(views_out):
        for kind, entry in sorted(views_out[cam].items()):
            if isinstance(entry, dict) and entry.get("control"):
                controls.append((cam, kind, entry["control"]))
    lines += ["", "## Controls", ""]
    if controls:
        lines += ["| camera | control | flagged | confirmed |", "|---|---|---|---|"]
        for cam, kind, c in controls:
            lines.append(f"| {cam} | {kind} | {_fmt(c.get('flagged'))} | {_fmt(c.get('confirmed'))} |")
    else:
        lines.append("None.")

    lines += ["", "## Calibration", ""]
    if not calibration:
        lines.append("Not calibrated yet (run `python -m wenart.vision_check calibrate`).")
    else:
        m = calibration["metrics"]
        lines += ["| metric | value | target |", "|---|---|---|"]
        t = calibration["targets"]
        lines.append(f"| combined FA missing | {_fmt(m['fa_missing'])} | <= {t['fa_missing_max']} |")
        lines.append(f"| views with a confirmed non-decor extra | {_fmt(m['fa_extra'])} | <= {t['fa_extra_max']} |")
        lines.append(f"| count error rate | {_fmt(m['count_error'])} | - |")
        lines.append(f"| removal flagged | {_fmt(m['removal_flagged'])} | >= {t['removal_flagged_min']} |")
        lines.append(f"| removal confirmed | {_fmt(m['removal_confirmed'])} | >= {t['removal_confirmed_min']} |")
        lines.append(f"| insertion detected | {_fmt(m['insertion'])} | >= {t['insertion_min']} |")
        lines.append(f"| type swap confirmed | {_fmt(m['swap_confirmed'])} | - |")
        for k, mm in (m.get("models") or {}).items():
            lines.append(f"| {k}: answered / decoy accepted / single-pass FA missing | {_fmt(mm['answer_rate'])} / "
                         f"{_fmt(mm['decoy_accept'])} / {_fmt(mm['fa_missing_single'])} | decoy <= "
                         f"{t['decoy_accept_max']} |")
        lines.append("")
        if calibration.get("missed"):
            lines.append("Missed targets (the check is advisory):")
            lines += [f"- {r}" for r in calibration.get("advisory_reasons") or []]
        else:
            lines.append("Every target is met.")
    lines += ["", "## Source plan", ""]
    ab = (calibration or {}).get("plan_ab") or {}
    lines.append(f"- {ab.get('text') or NOT_ADOPTED_TEXT}.")
    if ab:
        lines.append(f"- plan A/B on {len(ab.get('cameras') or [])} camera(s): FA missing "
                     f"{_fmt(ab.get('fa_missing_without'))} -> {_fmt(ab.get('fa_missing_with'))}, removal confirmed "
                     f"{_fmt(ab.get('removal_confirmed_without'))}"
                     f" -> {_fmt(ab.get('removal_confirmed_with'))}.")
    lines.append("- every view's source-plan crop is `<camera>_plan.jpg` in this folder.")
    warnings = manifest.get("warnings") or []
    lines += ["", "## Warnings", ""] + ([f"- {w}" for w in warnings] or ["None."])
    return "\n".join(lines) + "\n"
