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

FLAG_KEYS = ("real_product", "has_bedding", "has_cushions", "has_pillows", "contact")
BOX_KEYS = ("bbox_m", "bbox_model_m", "bbox_min_m", "bbox_max_m", "origin_offset")


def _entries(doc: dict):
    for section in ("entries", "decor"):
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
        if e.get("source") == "generated" and e.get("via") != via:
            e["via"] = via
            n += 1
    return n


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
    if turns and entry.get("front_axis") in AXES:
        keep_old("front_axis", "bbox_m", "front_axis_confidence")
        entry["front_axis"] = rotate_axis(entry["front_axis"], turns)
        entry["bbox_m"] = _oriented(entry["bbox_model_m"], entry["front_axis"])
        entry["front_axis_confidence"] = "medium"
        entry["front_axis_note"] = (str(entry.get("front_axis_note") or "") +
                                    f"; M12 audit: front turned {turns * 90} deg to {entry['front_axis']}")
        new["front_axis"] = entry["front_axis"]
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
            stats["skipped_pending"] += 1
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
        if d.get("notes"):
            extra["notes"] = list(d["notes"])
        e["audit"] = audit_record(status, d.get("reasons") or [], checked_utc, new, **extra)
        for k in FLAG_KEYS:
            v = (d.get("flags") or {}).get(k)
            if v is not None:
                e[k] = v
        stats["written"] += 1
    return stats


def summary(doc: dict) -> dict:
    """``{status: n}`` over the entries with an ``audit`` record, plus ``unaudited``."""
    out: dict = {}
    for e in _entries(doc):
        a = e.get("audit") if isinstance(e.get("audit"), dict) else None
        key = a.get("status") if a else "unaudited"
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items()))
