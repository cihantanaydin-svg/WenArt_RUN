"""Write the audit into the catalogues (docs/milestone12.md §6.1 ``write``, §6.2 D22, contract §13.3).

What:

- ``licence_removals(doc, checked_utc)`` (U3, run at the start of the build): every entry of a library catalogue
  whose licence is not allowed (NC / SA / ND / unknown; user decision of 10 Oct 2026) gets ``audit = {status:
  "removed", reasons: ["licence <id> not allowed (user decision of 10 Oct 2026)"], fixes: {}, version: "m12",
  checked_utc}``. The GLB stays on the volume (D22).
- ``generated_credit(doc)`` (B2): a generated entry's ``via`` names the generated source, not Objaverse.
- ``apply_decisions(doc, decisions, checked_utc)``: the ``audit`` record of every decided entry, its fixes applied to
  the catalogue fields (never to a GLB) and the flags ``real_product``, ``has_bedding``, ``has_cushions``,
  ``has_pillows``, ``contact``.

Fixes (``decide.py``): ``rescale`` (``unit_scale`` and every box and ``origin_offset`` times the factor),
``front_quarter_turns`` (``front_axis`` turned in 90 degree steps; ``bbox_m`` follows), ``origin_offset`` /
``bbox_min_m`` / ``bbox_max_m`` (the measured box: ``bbox_model_m`` and ``bbox_m`` follow), ``type`` (a real product
filed under the wrong type). ``audit.fixes`` holds the new field values, ``audit.before`` the old ones.

Why: ``catalog.usable(entry)`` (track S) reads ``audit.status``: ``removed`` entries are never used, ``fix`` ones
after their fix, which is in the catalogue fields themselves.

``apply_title_rules(doc, checked_utc)`` (28 Oct 2026, ``wenart.furniture.model_title``): the title rules re-run
over the catalogue (``python -m wenart.assets audit title-rules``): a model whose own names refuse it (a stated size its
box disagrees with, a set of pieces, a title of another type or use) is ``removed``, a unit error with a real size
behind it is fixed by ``rescale``.

How: idempotent: an entry whose ``audit.decision_sha`` equals the decision's hash is left as it is (a second
``write`` never rescales twice). The result passes ``wenart.furniture.catalog.validate``. Pure on the documents;
the CLI reads and writes the files.
"""
from __future__ import annotations

import hashlib
import json
from typing import Optional

from wenart.assets.audit import VERSION
from wenart.assets.audit.checks import AXES, licence_reason, rotate_axis

FLAG_KEYS = ("real_product", "has_bedding", "has_cushions", "has_pillows", "contact",
             "material_tags")                        # Milestone 13: the vision answer's materials (decide.py)
# Milestone 13 gates: plain fields a ``fix`` may set on the entry (checks.pbr_check, chaise_check).
FIELD_FIXES = ("pbr_maps", "chaise_side")
BOX_KEYS = ("bbox_m", "bbox_model_m", "bbox_min_m", "bbox_max_m", "origin_offset")
# Milestone 13 round 3 (docs/milestone13.md §14.6): an entry whose model file was republished upstream carries
# ``audit.reaudit`` (the evidence of the current file) and ``audit.before`` (the values of the older file) while it
# waits for its new audit (``growth_run.reaudit_entries``: pending + reaudit). A write keeps both: a ``pending``
# decision must not turn it into an ordinary pending model (``growth run pending`` would then decide it with P3's
# answers about the OLD file), and a decided record keeps the evidence it was judged on.
CARRIED = ("reaudit",)


def _entries(doc: dict):
    from wenart.assets.audit.items import SECTIONS
    for section in SECTIONS:                          # 23 Oct 2026: the extras section too
        for e in doc.get(section) or []:
            if isinstance(e, dict) and not e.get("parametric") and e.get("id"):
                yield e


def audit_record(status: str, reasons: list, checked_utc: str, fixes: Optional[dict] = None, **extra) -> dict:
    rec = {"status": status, "reasons": list(reasons), "fixes": dict(fixes or {}), "version": VERSION,
           "checked_utc": checked_utc}
    rec.update(extra)
    return rec


def licence_removals(doc: dict, checked_utc: str) -> list[str]:
    """U3: mark every entry with a licence that is not allowed as removed; returns the ids marked now (an entry
    already removed for its licence keeps its record)."""
    done = []
    for e in _entries(doc):
        why = licence_reason(e.get("licence"))
        if not why:
            continue
        old = e.get("audit") if isinstance(e.get("audit"), dict) else {}
        if old.get("status") == "removed" and why in (old.get("reasons") or []):
            continue
        reasons = [why] + [r for r in (old.get("reasons") or []) if r != why]
        e["audit"] = audit_record("removed", reasons, checked_utc)
        done.append(e["id"])
    return done


U3_NOTE = ("Milestone 12 (docs/milestone12.md §6.2, user decision of 10 Oct 2026): the models with a non-commercial, "
           "share-alike or no-derivatives licence carry audit.status removed (catalog.usable never uses them); their "
           "files stay on the volume. Generated models carry via 'generated for WenArt_RUN' (B2).")


def note_u3(doc: dict) -> bool:
    """The U3 / B2 line in the catalogue's ``notes`` (once)."""
    notes = doc.setdefault("notes", [])
    if U3_NOTE in notes:
        return False
    notes.append(U3_NOTE)
    return True


def generated_credit(doc: dict, via: Optional[str] = None) -> int:
    """B2: ``via`` of every generated entry set to the generated source; returns how many changed."""
    from wenart.assets.objaverse import GENERATED_VIA
    via = via or GENERATED_VIA
    n = 0
    for e in _entries(doc):
        gen = (e.get("generated") or {}).get("generator")
        if gen and gen != "trellis":
            continue                    # Milestone 12 pod P4: an Infinigen model keeps its own credit line
        if e.get("source") == "generated" and e.get("via") != via:
            e["via"] = via
            n += 1
    return n


END_FRONT_TYPES = ("car", "truck", "bus", "van", "motorcycle", "bicycle", "boat")


def end_front_turn_ok(entry: dict, turns: int) -> bool:
    """Whether a front turn of ``turns`` quarter turns keeps a vehicle's front on an end of its length (pure; 30 Oct
    2026, lesson UL129: the vision check's "front on the right of view 0" turned cars of the 3D Warehouse layer onto
    their sides, real04's car among them). Always True for other types, a half turn or a box with no long side."""
    if entry.get("type") not in END_FRONT_TYPES or int(turns) % 2 == 0:
        return True
    box = entry.get("bbox_model_m")
    if not box or len(box) < 2 or abs(float(box[0]) - float(box[1])) < 0.05 * max(float(box[0]), float(box[1])):
        return True
    new_axis = rotate_axis(entry["front_axis"], int(turns))
    long_axis = "X" if float(box[0]) > float(box[1]) else "Y"
    return new_axis.endswith(long_axis)


def _oriented(box_model, front_axis):
    from wenart.furniture import catalog as C
    return [round(float(v), 4) for v in C.oriented_bbox(box_model, front_axis)]


def fix_entry(entry: dict, fixes: dict) -> tuple[dict, dict]:
    """Apply ``fixes`` to one catalogue entry in place; returns ``(new field values, old field values)``."""
    new: dict = {}
    before: dict = {}

    def keep_old(*keys):
        for k in keys:
            if k in entry and k not in before:
                before[k] = entry[k]

    if "bbox_min_m" in fixes and "bbox_max_m" in fixes:
        keep_old("bbox_min_m", "bbox_max_m", "bbox_model_m", "bbox_m", "origin_offset")
        mn, mx = [float(v) for v in fixes["bbox_min_m"]], [float(v) for v in fixes["bbox_max_m"]]
        entry["bbox_min_m"], entry["bbox_max_m"] = [round(v, 4) for v in mn], [round(v, 4) for v in mx]
        entry["bbox_model_m"] = [round(b - a, 4) for a, b in zip(mn, mx)]
        entry["bbox_m"] = _oriented(entry["bbox_model_m"], entry["front_axis"])
        new.update(bbox_min_m=entry["bbox_min_m"], bbox_max_m=entry["bbox_max_m"])
    if "origin_offset" in fixes:
        keep_old("origin_offset")
        entry["origin_offset"] = [round(float(v), 4) for v in fixes["origin_offset"]]
        new["origin_offset"] = entry["origin_offset"]
    s = fixes.get("rescale")
    if s and abs(float(s) - 1.0) > 1e-9:
        s = float(s)
        keep_old("unit_scale", *BOX_KEYS)
        entry["unit_scale"] = float(entry.get("unit_scale", 1.0)) * s
        for k in BOX_KEYS:
            if k in entry:
                entry[k] = [round(float(v) * s, 4) for v in entry[k]]
        note = f"M12 audit: rescaled x{s:.4f} into the real size of a {entry['type']} (size table)"
        entry["unit_note"] = (str(entry.get("unit_note") or "").rstrip("; ") + "; " + note).lstrip("; ")
        new["unit_scale"] = entry["unit_scale"]
    turns = int(fixes.get("front_quarter_turns") or 0) % 4
    if turns and entry.get("front_axis") in AXES and not end_front_turn_ok(entry, turns):
        # 30 Oct 2026 (lesson UL129): a vehicle's front is an end of its length: a turn onto its side is refused
        entry["front_axis_note"] = (str(entry.get("front_axis_note") or "") + f"; M13 audit: a front turn of "
                                    f"{turns * 90} deg onto the long side of a {entry.get('type')} refused")
        turns = 0
    if turns and entry.get("front_axis") in AXES:
        keep_old("front_axis", "bbox_m", "front_axis_confidence")
        entry["front_axis"] = rotate_axis(entry["front_axis"], turns)
        entry["bbox_m"] = _oriented(entry["bbox_model_m"], entry["front_axis"])
        entry["front_axis_confidence"] = "medium"
        entry["front_axis_note"] = (str(entry.get("front_axis_note") or "") +
                                    f"; M12 audit: front turned {turns * 90} deg to {entry['front_axis']}")
        new["front_axis"] = entry["front_axis"]
    for key in FIELD_FIXES:
        if key in fixes and fixes[key] is not None and entry.get(key) != fixes[key]:
            keep_old(key)
            entry[key] = fixes[key]
            new[key] = fixes[key]
            if key == "chaise_side":
                entry["chaise_note"] = (str(entry.get("chaise_note") or "").rstrip("; ") + "; M13 audit: chaise side "
                                        f"{fixes[key]} from the measured footprint").lstrip("; ")
    t = fixes.get("type")
    if t and t != (entry.get("decor_type") or entry.get("type")):
        if entry.get("kind") == "decor" or entry.get("decor_type"):
            keep_old("type", "decor_type")
            entry["decor_type"], entry["type"] = t, f"decor_{t}"
        else:
            keep_old("type")
            entry["type"] = t
        new["type"] = t
    return new, before


def decision_sha(decision: dict) -> str:
    body = {k: decision.get(k) for k in ("status", "reasons", "fixes", "flags")}
    if decision.get("vision_doubt"):
        body["vision_doubt"] = decision["vision_doubt"]
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]


def apply_decisions(doc: dict, decisions: dict, checked_utc: str) -> dict:
    """Write ``decisions`` (``{id: decide.decide(...)}``; ``pending`` ones are skipped) into a catalogue document.
    Returns ``{"written", "skipped_pending", "unchanged", "counts": {status: n}}``."""
    stats = {"written": 0, "skipped_pending": 0, "unchanged": 0, "counts": {}}
    for e in _entries(doc):
        d = decisions.get(e["id"])
        if d is None:
            continue
        if d["status"] == "pending":
            # still waiting for a vision pass: recorded as pending, never used (catalog.usable; CLAUDE.md library
            # rules: only audited models are used)
            stats["skipped_pending"] += 1
            old = e.get("audit") if isinstance(e.get("audit"), dict) else {}
            kept = {k: old[k] for k in ("before", *CARRIED) if old.get(k)} if isinstance(old.get("reaudit"), dict) \
                else {}
            rec = audit_record("pending", [p.get("why", "") for p in d.get("pending") or []], checked_utc, **kept)
            if old.get("status") != "pending" or old.get("reasons") != rec["reasons"]:
                e["audit"] = rec
            continue
        status = d["status"]
        stats["counts"][status] = stats["counts"].get(status, 0) + 1
        sha = decision_sha(d)
        old = e.get("audit") if isinstance(e.get("audit"), dict) else {}
        if old.get("decision_sha") == sha:
            stats["unchanged"] += 1
            continue
        new, before = ({}, {}) if status == "removed" else fix_entry(e, d.get("fixes") or {})
        if old.get("before"):
            before = dict(old["before"], **{k: v for k, v in before.items() if k not in old["before"]})
        extra = {"decision_sha": sha}
        if before:
            extra["before"] = before
        extra.update({k: old[k] for k in CARRIED if isinstance(old.get(k), dict)})
        if d.get("notes"):
            extra["notes"] = list(d["notes"])
        if d.get("vision_doubt"):
            extra["vision_doubt"] = list(d["vision_doubt"])      # user decision 1a: kept, watched by the final check
        e["audit"] = audit_record(status, d.get("reasons") or [], checked_utc, new, **extra)
        for k in FLAG_KEYS:
            v = (d.get("flags") or {}).get(k)
            if v is None:
                continue
            if k == "material_tags" and isinstance(e.get("material_tags"), list) and e["material_tags"]:
                continue                                  # the Milestone 10 slot judgement stays
            e[k] = v
            if k == "material_tags":
                e["material_tags_note"] = "M13 audit: from the vision answer's materials (one pass; the slot " \
                                          "judgement of recolour.py is finer where it exists)"
        stats["written"] += 1
    return stats


# 28 Oct 2026, provenance: user on real04 run 20261028-005318-full (a coffee table that was a 2.4 m high table with its
# barstools read in feet, a kitchen sink as a washbasin, a wardrobe with a window at its end) and on real06 (a flat bath)
TITLE_RULES_NOTE = ("28 Oct 2026 (user: a coffee table that was a 2.4 m high table with its barstools read in feet, a "
                    "kitchen sink as a washbasin): the entries whose own names "
                    "disagree with them (wenart.furniture.model_title: a stated size the box disagrees with, a set of "
                    "pieces, a title of another type or use; furniture the vision check rates 2 or lower or finds no "
                    "real product in) carry audit.status removed (or fix with the units "
                    "corrected), the ones whose own audit doubts their type (the vision check: not the type, the size "
                    "odd; a front turned off its detail side) audit.status pending until a later audit pass confirms "
                    "them; both with audit.title_rules; their files stay on the volume.")


def apply_title_rules(doc: dict, checked_utc: str) -> dict:
    """28 Oct 2026 (``wenart.furniture.model_title``; the user's two models on real04 run 20261028-005318-full): the
    model rules re-run over every ``keep`` / ``fix`` entry of a catalogue document, in place. An entry with a refusal
    of its names gets ``audit.status`` ``removed``, the rules' reasons first in ``audit.reasons`` (its notes, doubts,
    fixes and ``before`` kept); one with a doubt of its own audit (``audit_doubt``: the vision check said it is not
    its type or found its size odd; ``front_side``: its front turned off its detail side) gets ``pending``: never used
    until a later audit pass confirms it; one with only a unit ``fix`` gets the ``rescale`` applied to its fields
    (``fix_entry``) and ``audit.status`` ``fix``. Each carries ``audit.title_rules`` = ``{version, checked_utc,
    status_before, findings}``. ``removed`` and ``pending`` entries are left as they are (nothing is deleted, no file
    is touched). Idempotent: a corrected entry agrees with its title, a removed or pending one is not read again.
    Returns the counts ``{"checked", "removed": [ids], "pending": [ids], "fixed": [ids], "by_rule": {rule: n},
    "by_type": {type: n}, "by_section"}``."""
    from wenart.assets.audit.items import SECTIONS
    from wenart.furniture import model_title as MT
    stats: dict = {"checked": 0, "removed": [], "pending": [], "fixed": [], "by_rule": {}, "by_type": {},
                   "by_section": {}}
    for section in SECTIONS:
        for e in doc.get(section) or []:
            if not isinstance(e, dict) or e.get("parametric") or not e.get("id"):
                continue
            old = e.get("audit") if isinstance(e.get("audit"), dict) else {}
            status = str(old.get("status") or "")
            if status not in ("keep", "fix"):
                continue
            stats["checked"] += 1
            found = MT.findings(e)
            if not found:
                continue
            record = {"version": MT.VERSION, "checked_utc": checked_utc, "status_before": status,
                      "findings": [{k: f[k] for k in ("rule", "status", "reason", "fix", "metrics") if k in f}
                                   for f in found]}
            for f in found:
                stats["by_rule"][f"{f['rule']} {f['status']}"] = stats["by_rule"].get(f"{f['rule']} {f['status']}",
                                                                                       0) + 1
            ftype = MT.entry_type(e)
            stats["by_type"][ftype] = stats["by_type"].get(ftype, 0) + 1
            stats["by_section"][section] = stats["by_section"].get(section, 0) + 1
            refuse = [f for f in found if f["status"] == "refuse"]
            review = [f for f in found if f["status"] == "review"]
            audit = dict(old)
            if refuse or review:
                reasons = [f"28 Oct 2026, {f['rule']}: {f['reason']}" for f in refuse + review]
                audit.update(status="removed" if refuse else "pending",
                             reasons=reasons + [r for r in old.get("reasons") or [] if r not in reasons],
                             title_rules=record)
                stats["removed" if refuse else "pending"].append(e["id"])
            else:
                fixes: dict = {}
                for f in found:
                    for k, v in (f.get("fix") or {}).items():
                        fixes[k] = round(fixes.get(k, 1.0) * float(v), 6) if k == "rescale" else v
                new, before = fix_entry(e, fixes)
                if "unit_scale" in new:
                    e["unit_note"] = (str(e.get("unit_note") or "").rstrip("; ") + "; 28 Oct 2026 title rules: the "
                                      "units of the title's stated size").lstrip("; ")
                if old.get("before"):
                    before = dict(old["before"], **{k: v for k, v in before.items() if k not in old["before"]})
                audit.update(status="fix", fixes=dict(old.get("fixes") or {}, **new), title_rules=record,
                             notes=list(old.get("notes") or []) + [f"28 Oct 2026, {f['rule']}: {f['reason']}"
                                                                   for f in found])
                if before:
                    audit["before"] = before
                stats["fixed"].append(e["id"])
            e["audit"] = audit
    if stats["removed"] or stats["fixed"] or stats["pending"]:
        notes = doc.setdefault("notes", [])
        if TITLE_RULES_NOTE not in notes:
            notes.append(TITLE_RULES_NOTE)
    return stats


def summary(doc: dict) -> dict:
    """``{status: n}`` over the entries with an ``audit`` record, plus ``unaudited``."""
    out: dict = {}
    for e in _entries(doc):
        a = e.get("audit") if isinstance(e.get("audit"), dict) else None
        key = a.get("status") if a else "unaudited"
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items()))
