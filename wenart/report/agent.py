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

Fix round after P3 (16-17 Oct 2026; the agent track's ask). What: ``reported``: the findings no agent tool fixes,
which the loop reports to another stage (finding events with ``report_to`` / ``not_yours``, e.g. a decor piece
through the roof, cause ``decor_under_roof`` -> ``decor``), one row per check, target and stage with the rounds it
was seen in; ``context``: the planner sessions whose context the loop cut or that ended full (``check`` events with
tool ``context_budget``: status ``cut`` / ``context_full``, ``chars_removed``, ``max_model_len``). The metrics table
quotes the findings removed as measured by the next round's critics (``metrics.findings_removed.total``) and the dry
re-checks' count as a prediction. Why: P3's dec_L1_009 stayed critical in all 4 rounds with no stage told, its
building session ended on a full context without a word in the report, and the dry re-checks' count read as a
result.

Fix round after P4a (17 Oct 2026; the agent track's ask, applied at integration): the metrics table adds "edits
removing their finding" (``findings_removed.edits_removing_finding`` of ``edits_with_target``) and "plans ok / empty
/ refused / default" (``memory.plans_valid``, ``plans_empty``, ``plans_refused``, ``plans_default``: why the default
checklist ran); a log without these keys keeps the old table.

Fix round after P5 (22 Oct 2026; the agent lens of the P5 analysis):

- What: ``agent_block`` reads only the latest run of the appended ``orchestrator/log.json``: the events with ``seq >=
  run_first_seq``, the calls from ``run_first_call`` and the overrides this run made (``result.log_seq >=
  run_first_seq``; an override without a ``log_seq`` counts when it was made on the current ``building_decor.json``,
  ``overrides.source_sha``); ``earlier`` names what was left out. The metrics table compares the measured findings
  removed with the dry re-checks' prediction of the same rounds (the last round has no next round to measure it),
  adds the new critical / major findings of those rounds and the net (``removed_net``: gone - new), and says when
  the "after" totals were counted before the last round's accepted edits.
- Why: P5's real04 report listed M12 and P3 edits (seq 297-4048) next to P5's, the rounds table summed three runs
  (7 rounds, 249 accepted), the findings by check counted X2 70 critical over all runs, "33 measured; 40 predicted"
  set rounds 1-3 against rounds 1-4, the 6 new findings were not counted and the round-4 critical the final build no
  longer has was quoted as "after".
- How: ``run_scope`` (pure) does the filter; a log without ``run_first_seq`` (or 1) keeps everything, so the M11 /
  M12 reports are unchanged.

Fix round after P5 (22 Oct 2026; the user's decisions of 22 Oct 2026 in CLAUDE.md): ``inferred_items`` rows carry
``change`` (drawn type -> type, drawn size -> size), ``rule`` and ``by`` (code or the model of the adjusted_by_ai
record), and ``decision``: ``code_retype`` (code retyped a piece the vision models typed: ``decision_changes``) or
``wet_shrink`` (a drawn bathtub or shower shrunk to a real product size that fits its bay). Such a piece without an
``adjusted_by_ai`` label is listed anyway (label ``unlabelled``), so no change is silent; the final report lists the
inferred items in its own section (``inferred_lines``) when there is no orchestrator section.

Fix round after P6b (23 Oct 2026; the render track's ask): ``blocked_views`` (``last_round_blocked``): the cameras
with a code ``camera_blocked`` finding in the run's last critic round; the final report marks those views blocked
(``final.blocked_views``). Why: P6b's report showed real03's black yasama_3_2 / 5_2 / 6_1 (and the 54 % blocked
yasama_2_2) as normal views.

Fix round after P5 (22 Oct 2026), review:

- What: a row of a code change the agent edited later reads "<the code's reason>; then: <the agent's reason>" with
  its plan crop (``plan_crop``, shown after the reason when the reason does not name it); the code's record comes
  from ``adjusted_by_ai`` or its ``previous`` records, else the reading's text. ``wet_shrink`` compares both axes.
  ``run_scope`` keeps an earlier run's accepted edits made on the current ``building_decor.json`` (replayed into this
  building after a deadline cut), listed as "Replayed edits". The "measured" findings removed and the net come from
  one finding key (a stored ``metrics.json`` whose total differs from ``removed_net`` is computed again).
- Why: P5 f_L0_032/034/036/038 showed the agent's move reason and no plan crop; a bath shrunk across its depth was no
  ``wet_shrink``; a resumed run's report would leave out edits that are in its building; the P4a report read "24
  measured" next to "4 new; net 23" (27 gone by the current key).
"""
from __future__ import annotations

import json
import re
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


DECISION_TEXT = {"code_retype": "code retype of a vision-typed piece, decision of 22 Oct 2026",
                 "wet_shrink": "bath/shower longer than its bay shrunk, decision of 22 Oct 2026"}
WET_TYPES = ("bathtub", "shower")       # decision 3 of 22 Oct 2026: a bath or shower longer than its bay
SIZE_EPS_M = 0.005                      # a size change below this is rounding, not a change
VISION_METHODS = ("ai_two_pass",)       # a type the vision models gave (both passes agreeing)
NOT_A_TYPE = ("unknown", "not_furniture", "")   # answers / types that type nothing (no retype from or to them)


def _size(fp) -> Optional[list]:
    try:
        return [round(float(v), 3) for v in fp["size"][:2]] if isinstance(fp, dict) and fp.get("size") else None
    except (TypeError, ValueError, KeyError):
        return None


def _size_text(size: Optional[list]) -> str:
    return f"{size[0]:.2f} x {size[1]:.2f} m" if size else "-"


def _vision_type(f: dict) -> Optional[str]:
    """The type the vision models gave a drawn piece: its ``drawn_type`` when it has answers, else the type both
    recorded answers agree on (None without answers)."""
    cands = [c for c in f.get("type_candidates") or [] if isinstance(c, dict) and c.get("type")]
    if not cands and f.get("type_method") not in VISION_METHODS:
        return None
    if f.get("drawn_type"):
        return str(f["drawn_type"])
    types = {str(c["type"]) for c in cands}
    return types.pop() if len(types) == 1 else None


def decision_kind(f: dict) -> Optional[str]:
    """Fix round after P5 (the user's decisions of 22 Oct 2026): ``code_retype`` when code retyped a drawn piece the
    vision models typed (its vision type differs from its type, its ``type_method`` is not the vision models' and no
    agent ``retype`` is recorded; ``unknown`` / ``not_furniture`` type nothing), ``wet_shrink`` when a drawn bathtub
    or shower is smaller than drawn along its length or its depth (shrunk to a real product size that fits its bay,
    ``drawn_footprint`` kept); None otherwise (pure)."""
    if not isinstance(f, dict) or f.get("source") not in (None, "from_documents"):
        return None
    adj = f.get("adjusted_by_ai") if isinstance(f.get("adjusted_by_ai"), dict) else {}
    vision = _vision_type(f)
    if (vision and vision not in NOT_A_TYPE and str(f.get("type") or "unknown") not in NOT_A_TYPE
            and vision != f.get("type") and f.get("type_method") not in VISION_METHODS
            and not adj.get("retype")):           # ``retype``: the agent's retype_piece (edit_ops), not code
        return "code_retype"
    if f.get("type") in WET_TYPES:
        drawn, now = _size(f.get("drawn_footprint")), _size(f.get("footprint"))
        # fix round after P5 (22 Oct 2026), review: per axis, either way round (``reading.bay_fit`` also shrinks the
        # depth: a 1.70 x 0.78 m bath in a 0.75 m deep bay becomes 1.70 x 0.75 m)
        if drawn and now and any(a > b + SIZE_EPS_M for a, b in zip(sorted(drawn), sorted(now))):
            return "wet_shrink"
    return None


def change_text(f: dict) -> str:
    """``type a -> b`` and ``size w x d -> w x d m`` of a piece against its drawn record ("-" without a change)."""
    parts = []
    vision = _vision_type(f) or f.get("drawn_type")
    if vision and f.get("type") and vision != f.get("type"):
        parts.append(f"type {vision} -> {f.get('type')}")
    drawn, now = _size(f.get("drawn_footprint")), _size(f.get("footprint"))
    if drawn and now and any(abs(a - b) > SIZE_EPS_M for a, b in zip(sorted(drawn), sorted(now))):
        parts.append(f"size {_size_text(drawn)} -> {_size_text(now)}")
    return "; ".join(parts) or "-"


_CROP_IN_TEXT = re.compile(r"plan crop ([\w./-]+\.(?:png|jpg))")   # "... (plan crop recognition/crops/x.png)"


def _records(adj: dict) -> list[dict]:
    """The adjusted_by_ai record and its earlier records (``previous``, oldest first, kept by ``edit_ops._label``),
    latest first."""
    prev = [r for r in adj.get("previous") or [] if isinstance(r, dict)]
    return ([adj] if adj else []) + prev[::-1]


def _code_record(adj: dict) -> dict:
    """Fix round after P5 (22 Oct 2026), review: the code's own adjusted_by_ai record of a piece (``by: code``): the
    record itself, else the latest earlier record by code (an agent edit after it keeps it under ``previous``); {}
    without one."""
    return next((r for r in _records(adj) if r.get("by") == "code"), {})


def _plan_crop(f: dict, adj: dict) -> Optional[str]:
    """The plan crop of a change: the adjusted_by_ai record's (or an earlier record's) ``plan_crop`` / ``crop`` /
    evidence, else the piece's evidence (``plan_crop`` / ``crop``), else the path a reason or evidence text names
    ("plan crop <path>", as the reading rules write it)."""
    texts: list = []
    for rec in _records(adj):
        for key in ("plan_crop", "crop"):
            if rec.get(key):
                return str(rec[key])
        ev = rec.get("evidence")
        for e in (ev if isinstance(ev, list) else [ev]):
            if isinstance(e, dict) and (e.get("plan_crop") or e.get("crop")):
                return str(e.get("plan_crop") or e.get("crop"))
        texts.append(rec.get("reason"))
    texts.append(f.get("inferred_reason"))
    piece_ev = f.get("evidence")
    for e in (piece_ev if isinstance(piece_ev, list) else [piece_ev]):
        if isinstance(e, dict):
            if e.get("plan_crop") or e.get("crop"):
                return str(e.get("plan_crop") or e.get("crop"))
            texts += [e.get("text"), e.get("reason"), e.get("note")]
    for text in texts:
        hit = _CROP_IN_TEXT.search(str(text or ""))
        if hit:
            return hit.group(1)
    return None


def _change_reason(f: dict, adj: dict, decision: Optional[str]) -> Optional[str]:
    """Fix round after P5 (22 Oct 2026), review: the reason of a piece's row. A change under the decisions of 22 Oct
    2026 that an agent edit followed reads "<the code's reason>; then: <the agent's reason>": the code's record
    (``_code_record``), else, for data written before ``edit_ops`` kept the earlier records (P5: the nightstand retypes
    of f_L0_032/034/036/038, moved in round 1), the reading's text (``inferred_reason`` of a retype, else the last
    ``inferred`` evidence text). Any other row: the record's reason, else ``inferred_reason`` (as before)."""
    own = adj.get("reason") or f.get("inferred_reason")
    if not decision or not adj or adj.get("by") == "code":
        return own
    code = _code_record(adj).get("reason")
    if not code:
        texts = [str(e.get("text")) for e in f.get("evidence") or []
                 if isinstance(e, dict) and e.get("method") == "inferred" and e.get("text")]
        code = (f.get("inferred_reason") if decision == "code_retype" else None) or (texts[-1] if texts else None)
    if not code or code == adj.get("reason"):
        return own
    return f"{code}; then: {adj['reason']}" if adj.get("reason") else str(code)


def _rule_of(f: dict, adj: dict, decision: Optional[str]) -> Optional[str]:
    """The rule of a row: the code record's, else the record's, else a code retype's ``type_method``."""
    return (_code_record(adj).get("rule") or adj.get("rule")
            or (f.get("type_method") if decision == "code_retype" else None))


def _by_of(adj: dict, decision: Optional[str]) -> Optional[str]:
    """Who made a piece's change: the adjusted_by_ai record's ``by`` or ``model`` ("code" for a record without
    either); a code retype that a model edited later reads "code, then <model>"."""
    by = adj.get("by") or adj.get("model") or ("code" if adj else None)
    if (decision == "code_retype" or (decision and _code_record(adj))) and by != "code":
        return f"code, then {by}" if by else "code"
    return by


def _by_text(item: dict) -> str:
    by, rule = item.get("by"), item.get("rule")
    return f"{by or '-'} ({rule})" if rule else (by or "-")


def _reason_text(item: dict) -> str:
    """Fix round after P5 (22 Oct 2026), review: a row's reason with its plan crop ("(plan crop <path>)") when the
    reason does not name it already."""
    reason, crop = item.get("reason") or "-", item.get("plan_crop")
    return f"{reason} (plan crop {crop})" if crop and str(crop) not in reason else reason


def decision_changes(building: Optional[dict]) -> list[dict]:
    """Every drawn piece changed under the user's decisions of 22 Oct 2026 (``decision_kind``) with its change, the
    adjusted_by_ai reason, rule and author, the plan crop when recorded and whether it carries the label (pure)."""
    out = []
    for f in (building or {}).get("furniture") or []:
        kind = decision_kind(f) if isinstance(f, dict) else None
        if kind is None:
            continue
        adj = f.get("adjusted_by_ai") if isinstance(f.get("adjusted_by_ai"), dict) else {}
        by = _by_of(adj, kind)
        # fix round after P5 (22 Oct 2026), review: the code's own reason and rule first, then the agent's later edit
        out.append({"id": f.get("id"), "type": f.get("type"), "room_id": f.get("room_id"), "decision": kind,
                    "change": change_text(f), "reason": _change_reason(f, adj, kind) if adj else None,
                    "rule": _rule_of(f, adj, kind), "type_method": f.get("type_method"), "by": by,
                    "plan_crop": _plan_crop(f, adj), "labelled": bool(f.get("adjusted_by_ai"))})
    return out


def inferred_items(building: Optional[dict], overrides: Optional[dict]) -> list[dict]:
    out = []
    for f in (building or {}).get("furniture") or []:
        if not isinstance(f, dict):
            continue
        labels = [k for k in ("inferred", "adjusted_by_ai", "corrected_by_ai") if f.get(k)]
        decision = decision_kind(f)
        if decision and "adjusted_by_ai" not in labels:
            labels.append("unlabelled")         # fix round after P5: a 22 Oct change without its label is listed
        if labels:
            adj = f.get("adjusted_by_ai") if isinstance(f.get("adjusted_by_ai"), dict) else {}
            # fix round after P5 (22 Oct 2026), review: the code's reason before the agent's later edit, and the
            # plan crop (CLAUDE.md keeps it with a code retype; P5 f_L0_032 showed only the agent's move reason)
            out.append({"id": f.get("id"), "kind": "piece", "type": f.get("type"), "room_id": f.get("room_id"),
                        "labels": labels, "reason": _change_reason(f, adj, decision),
                        "drawn_type": f.get("drawn_type"), "change": change_text(f),
                        "rule": _rule_of(f, adj, decision), "by": _by_of(adj, decision), "decision": decision,
                        "plan_crop": _plan_crop(f, adj)})
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


def _int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def run_scope(log: dict, overrides: Optional[dict], sha_now: str = "", not_replayed=()) -> dict:
    """Fix round after P5 (module docstring): the latest run of an appended log (pure). ``{"first_seq",
    "first_call", "events", "calls", "edits", "replayed", "earlier": {"events", "calls", "edits", "replayed"}}``: the
    events with ``seq >= run_first_seq``, the calls from ``run_first_call``, the overrides with ``result.log_seq >=
    run_first_seq`` (one without a ``log_seq``: made on ``sha_now``, the current ``building_decor.json``, or without a
    recorded sha). A log without ``run_first_seq`` (or 1) keeps everything.

    Fix round after P5 (22 Oct 2026), review: an accepted edit of an earlier run made on ``sha_now`` (a deadline-cut
    run resumed on the same ``building_decor.json``: ``agent_apply`` replays it into this building, as
    ``Overrides.accepted``) stays in ``edits``, unless its override seq is in ``not_replayed`` (the building's
    ``agent_overrides.not_replayed``: its replay failed); ``replayed`` holds its log events (the accepted ``edit``
    events of those log seqs), listed apart from this run's rounds."""
    first = max(1, _int(log.get("run_first_seq"), 1))
    events = [e for e in log.get("events") or [] if isinstance(e, dict)]
    calls = [c for c in log.get("calls") or [] if isinstance(c, dict)]
    edits = [e for e in (overrides or {}).get("edits") or [] if isinstance(e, dict)]
    if first <= 1:
        return {"first_seq": 1, "first_call": 0, "events": events, "calls": calls, "edits": edits, "replayed": [],
                "earlier": {"events": 0, "calls": 0, "edits": 0, "replayed": 0}}
    first_call = max(0, _int(log.get("run_first_call"), 0))
    failed = {_int(n.get("seq") if isinstance(n, dict) else n, -1) for n in not_replayed or ()}

    def replayed(e: dict) -> bool:
        return bool((e.get("result") or {}).get("accepted") and sha_now and e.get("source_sha") == sha_now
                    and _int(e.get("seq"), -1) not in failed)

    def this_run(e: dict) -> bool:
        seq = (e.get("result") or {}).get("log_seq")
        if seq is not None and _int(seq, -1) >= 0:
            return _int(seq) >= first or replayed(e)
        return not e.get("source_sha") or not sha_now or e.get("source_sha") == sha_now

    kept_events = [e for e in events if _int(e.get("seq")) >= first]
    kept_edits = [e for e in edits if this_run(e)]
    from_earlier = [e for e in kept_edits if 0 <= _int((e.get("result") or {}).get("log_seq"), -1) < first]
    earlier_seqs = {_int(e["result"]["log_seq"]) for e in from_earlier}
    replayed_events = [e for e in events if e.get("kind") == "edit" and _int(e.get("seq")) in earlier_seqs]
    return {"first_seq": first, "first_call": first_call, "events": kept_events, "calls": calls[first_call:],
            "edits": kept_edits, "replayed": replayed_events,
            "earlier": {"events": len(events) - len(kept_events), "calls": min(first_call, len(calls)),
                        "edits": len(edits) - len(kept_edits), "replayed": len(from_earlier)}}


def removed_net(events: list[dict]) -> Optional[dict]:
    """Fix round after P5: per pair of consecutive critic rounds the critical / major finding keys gone and new
    (``causes.finding_key``, as ``wenart.agent.metrics.findings_removed_metrics``) and ``net`` = gone - new; the
    rounds measured (every round but the last, which has no next round). None with fewer than two rounds (pure)."""
    from wenart.agent import causes as CS

    findings = [e for e in events if e.get("kind") == "finding" and not e.get("dropped")]
    rounds = [e for e in events if e.get("kind") == "round"]
    round_ids = sorted({_int(e.get("round")) for e in (rounds or findings)})
    if len(round_ids) < 2:
        return None
    keys = {r: {CS.finding_key(e) for e in findings if _int(e.get("round")) == r
                and e.get("severity") in ("critical", "major")} for r in round_ids}
    per_round = {str(a): {"gone": len(keys[a] - keys[b]), "new": len(keys[b] - keys[a])}
                 for a, b in zip(round_ids, round_ids[1:])}
    gone = sum(v["gone"] for v in per_round.values())
    new = sum(v["new"] for v in per_round.values())
    return {"per_round": per_round, "gone": gone, "new": new, "net": gone - new,
            "rounds_measured": [int(k) for k in per_round], "last_round": round_ids[-1]}


def agent_block(project_out, out_dir, private: bool = False, building: Optional[dict] = None) -> Optional[dict]:
    project_out = Path(project_out)
    log = _read(project_out / AGENT_DIR / "log.json")
    if log is None:
        return None
    overrides = _read(project_out / AGENT_DIR / "overrides.json") or {"edits": []}
    try:
        from wenart.agent import overrides as OV
        sha_now = OV.source_sha(project_out)
    except Exception:  # noqa: BLE001 - without the sha an override without a log_seq counts as this run's
        sha_now = ""
    if building is None:
        building = _read(project_out / "building_final.json")
    # fix round after P5 (22 Oct 2026), review: an earlier run's edit whose replay failed is not in this building
    agent_ov = (building or {}).get("agent_overrides") if isinstance(building, dict) else None
    scope = run_scope(log, overrides, sha_now,
                      (agent_ov.get("not_replayed") or []) if isinstance(agent_ov, dict) else [])
    overrides = {"edits": scope["edits"]}
    events = scope["events"]
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

    def edit_row(e: dict) -> dict:
        v = e.get("validation") or {}
        row = {"seq": e["seq"], "round": e.get("round"), "tool": e.get("tool"), "target": e.get("target"),
               "label": e.get("label"), "reason": e.get("reason"), "check": e.get("checklist"),
               "score_before": v.get("score_before"), "score_after": v.get("score_after"),
               "rerun_from": e.get("rerun_from")}
        if e["kind"] == "edit":
            row["before"] = image(e.get("before"))
            row["after"] = image(e.get("after"))
        else:
            row["failed_checks"] = list(v.get("failed_checks") or [])
        return row

    edits = [edit_row(e) for e in events if e["kind"] == "edit"]
    rejected = [edit_row(e) for e in events if e["kind"] == "rejected_edit"]
    # fix round after P5 (22 Oct 2026), review: an earlier run's accepted edits replayed into this building
    replayed = [edit_row(e) for e in scope["replayed"]]
    before_after = []
    for e in events:
        if e["kind"] == "render" and (e.get("before") or e.get("after")):
            before_after.append({"round": e.get("round"), "view": (e.get("views") or [None])[0],
                                 "before": image(e.get("before")), "after": image(e.get("after"))})
    rolled_back = [{"seq": e["seq"], "round": e.get("round"), "tool": e.get("tool"),
                    "why": (e.get("result") or {}).get("rolled_back")}
                   for e in overrides.get("edits") or [] if (e.get("result") or {}).get("rolled_back")]
    seconds = 0.0
    for stage in ("agent", "agent_previews", "agent_apply"):
        rec = _read(project_out / "run" / f"{stage}.json")
        if rec and isinstance(rec.get("seconds"), (int, float)):
            seconds += float(rec["seconds"])
    calls = scope["calls"]
    tokens = sum(int(c.get("prompt_tokens") or 0) + int(c.get("completion_tokens") or 0) for c in calls)
    # Milestone 12 (§5.5 D20): orchestrator/metrics.json of the run (computed when missing); fix round after P5: a
    # metrics.json of another run (its first_seq is not this log's run_first_seq) is computed again
    metrics = _read(orch / "metrics.json")
    if metrics is not None and scope["first_seq"] > 1 and _int(metrics.get("first_seq"), -1) != scope["first_seq"]:
        metrics = None
    net = removed_net(events)
    removed = (metrics or {}).get("findings_removed") if isinstance((metrics or {}).get("findings_removed"),
                                                                     dict) else None
    if metrics is not None and net is not None and removed and _int(removed.get("total"), -1) != net["gone"]:
        # fix round after P5 (22 Oct 2026), review: a metrics.json counted with an older finding key (real02 of P4a:
        # 24 measured, 27 gone by the current key) is computed again, so "measured" and "net" share one key
        metrics = None
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
            "library_gaps": gaps, "reported": reported_findings(events), "context": context_checks(events),
            # fix round after P5: this run only (run_scope), the net findings removed and the last round's edits
            "first_seq": scope["first_seq"], "earlier": scope["earlier"], "removed_net": net,
            "last_round_accepted": _last_round_accepted(events), "replayed": replayed,
            # fix round after P6b: the views the last round still found blocked (the final report marks them)
            "blocked_views": last_round_blocked(events),
            # 26 Oct 2026: what the AI inspector saw on the final renders (wenart/agent/inspector.py)
            "inspector": _read(orch / "inspector.json")}


def _last_round_accepted(events: list[dict]) -> dict:
    """Fix round after P5: ``{"round", "accepted"}``: the accepted edits of the last critic round, which no later
    critic measured (its findings are the metrics' "after" totals)."""
    rounds = [e for e in events if e.get("kind") == "round"]
    findings = [e for e in events if e.get("kind") == "finding" and not e.get("dropped")]
    ids = sorted({_int(e.get("round")) for e in (rounds or findings)})
    last = ids[-1] if ids else None
    return {"round": last, "accepted": sum(1 for e in events if e.get("kind") == "edit" and last is not None
                                           and _int(e.get("round")) == last)}


# Fix round after P6b: the code check of a view blocked by a piece (``critic_code.CAMERA_BLOCKED_CHECK``).
CAMERA_BLOCKED_CHECK = "camera_blocked"


def last_round_blocked(events: list[dict]) -> dict[str, str]:
    """Fix round after P6b (the render track's ask): ``{camera: finding text}`` of the code ``camera_blocked``
    findings (not dropped) of the last critic round of the run (pure): the views the final build still renders
    blocked. P6b real03: yasama_2_2 (54 %), yasama_3_2 / 5_2 / 6_1 (100 %, black) in round 4."""
    rounds = sorted({_int(e.get("round")) for e in events if e.get("kind") == "finding" and not e.get("dropped")})
    if not rounds:
        return {}
    last = rounds[-1]
    return {str(e.get("target")): str(e.get("finding") or e.get("message") or "")
            for e in events if e.get("kind") == "finding" and not e.get("dropped") and _int(e.get("round")) == last
            and e.get("source") == "code" and e.get("checklist") == CAMERA_BLOCKED_CHECK and e.get("target")}


def reported_findings(events: list[dict]) -> list[dict]:
    """Fix round after P3: the findings the loop reports to another stage (finding events with ``report_to`` or
    ``not_yours``, not dropped), one row per (check, target, stage) with the rounds it was seen in (pure)."""
    rows: dict = {}
    for e in events:
        if e.get("kind") != "finding" or e.get("dropped") or not (e.get("report_to") or e.get("not_yours")):
            continue
        key = (str(e.get("checklist")), str(e.get("target")), str(e.get("report_to") or "-"))
        row = rows.setdefault(key, {"check": key[0], "target": key[1], "report_to": e.get("report_to"),
                                    "severity": e.get("severity"), "cause": e.get("cause"),
                                    "room_id": e.get("room_id"), "why": e.get("not_yours"),
                                    "finding": e.get("finding"), "rounds": []})
        if int(e.get("round") or 0) not in row["rounds"]:
            row["rounds"].append(int(e.get("round") or 0))
    return [rows[k] for k in sorted(rows)]


def context_checks(events: list[dict]) -> list[dict]:
    """Fix round after P3: the planner sessions whose context was cut or full (``check`` events with tool
    ``context_budget``, ``wenart.agent.loop.CONTEXT_CHECK``) (pure)."""
    out = []
    for e in events:
        if e.get("kind") != "check" or e.get("tool") != "context_budget":
            continue
        counts = e.get("counts") or {}
        out.append({"round": e.get("round"), "target": e.get("target"), "status": e.get("status"),
                    "cuts": counts.get("cuts"), "chars_removed": counts.get("chars_removed"),
                    "max_model_len": counts.get("max_model_len"), "call_id": e.get("call_id")})
    return out


def _rounds_text(rounds: list) -> str:
    ids = sorted(int(r) for r in rounds)
    if not ids:
        return "-"
    if len(ids) == 1:
        return f"round {ids[0]}"
    if ids == list(range(ids[0], ids[-1] + 1)):
        return f"rounds {ids[0]}-{ids[-1]}"
    return "rounds " + ", ".join(str(i) for i in ids)


def metrics_lines(m: Optional[dict], net: Optional[dict] = None, last: Optional[dict] = None) -> list[str]:
    """Milestone 12 (§5.5): the agent metrics of the run as a short table. Fix round after P5: ``net``
    (``removed_net``) adds the new findings and the net; the prediction sums the dry re-checks of the measured rounds
    only; ``last`` (``_last_round_accepted``) says when the "after" totals precede the last round's edits."""
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
            ["critical before -> after" + _after_note(f, last),
             f"{f['before_totals']['critical']} -> {f['after_totals']['critical']}"],
            ["major before -> after" + _after_note(f, last),
             f"{f['before_totals']['major']} -> {f['after_totals']['major']}"],
            ["agent minutes; first accepted edit after", f"{t['agent_minutes']}; {t['first_accepted_edit_s']} s"],
            ["repeats refused by the memory; dry runs; plans (valid)",
             f"{mem['repeats_refused']}; {mem['dry_runs']}; {mem['plans']} ({mem['plans_valid']})"]]
    removed = m.get("findings_removed")
    if removed:
        # fix round after P3: the measured number (the next round's critics) leads; the dry re-checks only predict.
        # Fix round after P5: the prediction of the same rounds (the last round has no next round to measure it)
        measured_rounds = sorted(str(k) for k in (removed.get("per_round") or {}))
        dry = removed.get("dry_recheck") or {}
        same = [k for k in dry if str(k) in measured_rounds] if measured_rounds else list(dry)
        predicted = sum(int(dry[k] or 0) for k in same)
        rest = sum(int(dry[k] or 0) for k in dry if k not in same)
        scope = _rounds_text(measured_rounds) if measured_rounds else "-"
        # fix round after P5 (22 Oct 2026), review: with the net, "measured" is its gone count (one finding key)
        measured = net["gone"] if net else removed.get("total", 0)
        rows.append([f"critical/major findings removed in {scope} (measured by the next round; predicted by the dry "
                     "re-checks of the same rounds)",
                     f"{measured} measured; {predicted} predicted"
                     + (f" (the last round's dry re-checks predicted {rest} more, not measured)" if rest else "")])
        if net:
            rows.append([f"new critical/major findings in {_rounds_text(net.get('rounds_measured') or [])}; net "
                         "removed (gone - new)", f"{net['new']} new; net {net['net']}"])
        # fix round after P4a (integration of the agent track's ask): the edits that removed what they targeted
        if removed.get("edits_with_target") is not None:
            rows.append(["edits removing their finding",
                         f"{removed.get('edits_removing_finding', 0)} of {removed['edits_with_target']}"])
    if any(k in mem for k in ("plans_empty", "plans_refused", "plans_default")):
        # fix round after P4a: why the default checklist ran (loop.plan_status)
        rows.append(["plans ok / empty / refused / default",
                     " / ".join(str(mem.get(k, 0)) for k in ("plans_valid", "plans_empty", "plans_refused",
                                                             "plans_default"))])
    return ["", "### Agent metrics", ""] + C.table(["metric", "value"], rows)


def _after_note(f: dict, last: Optional[dict]) -> str:
    """Fix round after P5: " (after: round n, before its k accepted edit(s))" when the last critic round had
    accepted edits no later critic measured."""
    if not last or not last.get("accepted"):
        return ""
    rnd = f.get("last_round") if f.get("last_round") is not None else last.get("round")
    return f" (after: round {rnd}'s critics, before its {last['accepted']} accepted edit(s))"


def inferred_lines(items: list[dict], heading: str = "### Inferred and AI-changed items") -> list[str]:
    """The inferred and AI-changed items as a table (the orchestrator section's, and the final report's own section
    for a run without the orchestrator). Fix round after P5: the change against the drawn record, who made it (rule)
    and the decision of 22 Oct 2026 it falls under."""
    lines = ["", heading, ""]
    if not items:
        return lines + ["None."]
    lines += C.table(["id", "kind", "type", "room", "labels", "change", "by (rule)", "reason"],
                     [[i["id"], i["kind"], i["type"], i.get("room_id") or "-",
                       ", ".join(i["labels"]) + (f" ({DECISION_TEXT[i['decision']]})" if i.get("decision") else ""),
                       i.get("change") or "-", _by_text(i), _reason_text(i)] for i in items])
    if any(i["kind"] == "geometry" for i in items):
        lines.append("")
        lines.append("Geometry corrections are record-only in M11: the drawn geometry was not changed; they are "
                     "open items for the next full run.")
    return lines


def _img(link: Optional[str]) -> str:
    return f"![]({link})" if link else "-"


def inspector_lines(rec: Optional[dict]) -> list[str]:
    """26 Oct 2026: the AI inspector's summary (``orchestrator/inspector.md`` has every finding): what it saw on the
    final renders, fixed, handed on and left; the open majors are listed so they are known before anyone looks."""
    if not isinstance(rec, dict) or not rec.get("counts"):
        return []
    c = rec["counts"]
    lines = ["", "### What the AI inspector saw on the final renders", "",
             f"{c.get('seen', 0)} vision finding(s) ({c.get('visitor', 0)} of the visitor checks Q1-Q9: doors, "
             f"working heights, falls, rooms that make no sense, pieces that clash, doors and windows, rain water): "
             f"{c.get('fixed', 0)} fixed in the final round, {c.get('handed', 0)} handed to the stage that owns them, "
             f"{c.get('open', 0)} open; the architect leaves {c.get('architect_open_major', 0)} major open point(s). "
             "Every finding with its outcome: `orchestrator/inspector.md`."
             + ("" if rec.get("final_round_started", True) else " The final round did not start (time): these are "
                                                                  "the last round's findings on the previews.")]
    rows = [r for r in (rec.get("vision") or []) + (rec.get("code") or [])
            if r.get("severity") in ("critical", "major") and not str(r.get("outcome") or "").startswith("fixed")]
    if rows:
        lines += ["", "Still open or handed on (critical and major):", ""]
        lines += [f"- {r.get('severity')} {r.get('check')} {r.get('target')}: {str(r.get('message') or '')[:140]} "
                  f"({str(r.get('outcome') or '')[:90]})" for r in rows[:25]]
    return lines


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
    earlier = a.get("earlier") or {}
    if earlier.get("events") or earlier.get("edits"):
        # fix round after P5: the latest run of the appended log only (run_scope)
        lines += ["", f"This run only (log events from seq {a.get('first_seq')}): earlier runs of the appended log "
                      f"are left out ({earlier.get('events', 0)} events, {earlier.get('calls', 0)} model calls, "
                      f"{earlier.get('edits', 0)} stored edits); `orchestrator/log.md` has them."
                  # fix round after P5 (22 Oct 2026), review: a cut run's edits replayed into this building
                  + (f" {earlier['replayed']} accepted edit(s) of an earlier run on the same `building_decor.json` "
                     "were replayed into this building (listed under Replayed edits and the library gaps)."
                     if earlier.get("replayed") else "")]
    lines += metrics_lines(a.get("metrics"), a.get("removed_net"), a.get("last_round_accepted"))
    lines += inspector_lines(a.get("inspector"))
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
    if a.get("replayed"):
        # fix round after P5 (22 Oct 2026), review: run_scope's replayed edits (a resumed deadline-cut run)
        lines += ["", "### Replayed edits of an earlier run on the same building", ""]
        lines += C.table(["#", "round", "tool", "target", "label", "score", "reason"],
                         [[e["seq"], e["round"], e["tool"], e["target"], e["label"] or "-",
                           f"{e['score_before']} -> {e['score_after']}" if e["score_before"] is not None else "-",
                           e["reason"]] for e in a["replayed"]])
    if a["rejected"]:
        lines += ["", "### Rejected edits", ""]
        lines += C.table(["#", "round", "tool", "target", "failed checks", "reason"],
                         [[e["seq"], e["round"], e["tool"], e["target"], ", ".join(e["failed_checks"]) or "-",
                           e["reason"]] for e in a["rejected"]])
    if a["rolled_back"]:
        lines += ["", "Rolled back (the refit refused them): "
                  + ", ".join(f"#{r['seq']} {r['tool']} ({r['why']})" for r in a["rolled_back"]) + "."]
    if a.get("reported"):
        # fix round after P3: findings no agent tool fixes go back to the stage that caused them
        lines += ["", "### Reported to other stages", ""]
        lines += C.table(["check", "severity", "target", "room", "stage", "cause", "rounds", "why"],
                         [[r["check"], r["severity"] or "-", r["target"], r.get("room_id") or "-",
                           r.get("report_to") or "-", r.get("cause") or "-", ", ".join(str(n) for n in r["rounds"]),
                           r.get("why") or r.get("finding") or "-"] for r in a["reported"]])
    if a.get("context"):
        lines += ["", "### Context budget of the planner sessions", ""]
        lines += C.table(["round", "session", "status", "cuts", "characters removed", "context (tokens)"],
                         [[c["round"], c.get("target") or "building", c["status"], c.get("cuts") or 0,
                           c.get("chars_removed") or 0, c.get("max_model_len") or "-"] for c in a["context"]])
    lines += inferred_lines(a["inferred"])
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
