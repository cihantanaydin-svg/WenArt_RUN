"""Argus, the process line: the run itself is audited, not only its images (26 Oct 2026, user: "everything needs to
be judged ... this auditor should have no limits").

What (each check over every item, nothing sampled):

- P1 a stage that failed, timed out or stayed pending (``run_manifest.json`` and the per-stage records); a skipped
  stage only when its note does not say why;
- P2 every warning of the reading, the build and the site, matched against ``WARN_RULES``: a warning that says
  something was left out, fell short of its plan ("placed 0 of 3"), was not read or could not be done is a finding
  (kind ``silent``: a stage noted it and nothing acted on it); every other warning is counted by its rule in the
  report, none is dropped unread;
- P3 open questions: recognition questions no model answered, the architect's open questions;
- P4 failed tests (``junit-*.xml``): each failure with its message;
- P5 the scene's own checks that failed: a door ray that hits an object (a blocked door or pass-through), the
  furniture scene checks S1-S6 with failures, decor that could not rest on its host;
- P6 rooms with no view (a room of the documents no image shows), cameras dropped;
- P7 pieces built below the library level (parametric fallbacks, proxies) and openings built parametric because no
  model fits: the library gaps to close;
- P8 time left unused: the run stopped with open major or critical points and time left before its deadline;
- P9 the agent's and the big loop's own result: a cycle that made the house worse, a loop that did not raise the
  score;
- P10 the agent itself: a finding the agent tried to fix ``FUTILE_TRIES`` times or more with every try refused by code
  (this run's log events only), with the refusal it met most: the stage or rule behind it must change, not the agent
  (real06: "kitchen_run (missing stove, fridge): no place passes the checks", 30 tries).

- P12 (29 Oct 2026) a finish built flat although the vocabulary gives it a texture set: the set never reached the
  assets (real04 run 20261029-201533-full: 37 herringbone floors flat, "asset WoodFloor034 not in the assets
  manifest"); kind ``lost``, owner the asset stage.
- P11 (28 Oct 2026) a built library model its own names or its audit refuse: a stated size its box disagrees with
  (a table set read in feet), a set of pieces in one mesh, a title of another type or use (a kitchen sink as a
  washbasin), a vision doubt of its type or size (a wardrobe with a window at its end): ``wenart.furniture
  .model_title``.

Why: the veranda was written in a warning ("an open balcony, recorded in site, not a room") and then nothing built
it; real06's inferred trees were "placed 0 of 3" in a warning. A warning nobody reads is the ``silent`` kind.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Optional

from wenart.audit import kinds as K
from wenart.audit.inputs import Inputs

# (rule id, pattern, severity, kind, what it means). The first match wins; a warning no rule matches is ``other``
# and counted (``unmatched``) so the rules can grow.
WARN_RULES = (
    ("shortfall", re.compile(r"\bplaced (\d+) of (\d+)\b", re.I), "major", "silent",
     "a stage placed fewer items than it planned"),
    # 27 Oct 2026 (stair_access: the walk from every stair into its floors; the architect's K4, the model review's M9)
    ("stair_cut_off", re.compile(r"no other reading of the stair leads into both floors", re.I), "major", "no_sense",
     "a stair cut off from its floor that no reading of it fixes (the model review's M9 names the walk)"),
    ("stair_reading", re.compile(r"^architect K4: |\bdraws the same stair\b", re.I), "info", "other",
     "a stair read again so it leads into its floors (the plan of the level above, or the architect's K4), logged"),
    ("outside_not_room", re.compile(r"outside the outer walls.*not a room|recorded in site, not a room", re.I),
     "major", "lost", "a labelled space outside the walls was kept as a site record: it must be built"),
    ("not_used", re.compile(r"\bread\b.*\bnot used\b|\bunused\b", re.I), "major", "lost",
     "items the reading found and no stage used"),
    ("not_cut", re.compile(r"not cut through|is not cut\b", re.I), "major", "no_sense",
     "an opening of the documents is not cut through its wall"),
    # 27 Oct 2026 (real06 run 180412, two runs in a row: the bath through its basin): a recurring kind gets its rule
    ("clash_left", re.compile(r"furniture clash left", re.I), "major", "geometry",
     "two pieces still cut each other after the build's clash resolver (F5): Argus moves the one that gives way"),
    ("drawn_mismatch", re.compile(r"vs the drawn .*?\(([+-]?\d+) cm\)", re.I), "major", "misread",
     "the model differs from the drawn section or elevation"),
    ("not_read", re.compile(r"entity types not read|not read\b|could not read|unreadable", re.I), "minor", "lost",
     "source entities the reading did not read (the ledger checks what they hold)"),
    ("not_checked", re.compile(r"not checked\b", re.I), "minor", "process", "a check that could not run"),
    ("failed", re.compile(r"\bfailed\b|\berror\b|could not|cannot\b|exception", re.I), "major", "process",
     "a step failed"),
    ("nothing_fits", re.compile(r"nothing fits|no place passes|no candidate position", re.I), "minor", "taste",
     "a group the room should have found no place"),
    ("not_allowed", re.compile(r"not a type allowed", re.I), "minor", "misread",
     "a piece whose type the room does not allow, kept unverified"),
    ("more_labels", re.compile(r"has more labels", re.I), "minor", "misread",
     "one room outline holds the labels of two rooms (a wall not read?)"),
    ("not_rested", re.compile(r"not rested", re.I), "minor", "geometry", "decor that could not rest on its host"),
    ("no_model", re.compile(r"no model|not built \(no model\)|without a library model", re.I), "minor", "taste",
     "no library model: built parametric or not at all"),
    ("not_built", re.compile(r"\bnot built\b|\bleft out\b|\bdropped\b|\bskipped\b|\bremoved\b|withdrawn",
                             re.I), "info", "lost",
     "an element not built, with the reason the stage gave (conservation and the AI auditor judge the reason)"),
    ("no_label", re.compile(r"has no label", re.I), "info", "untyped", "a room outline with no label"),
    ("disagree", re.compile(r"disagree|but that side", re.I), "info", "other", "the AI and the drawing disagree; the "
                                                                             "drawing is kept"),
    ("assumed", re.compile(r"\bassumed\b|\binferred\b|\btyped .* by code\b|tie_break|taken from|-> \w+ \(reading",
                           re.I), "info", "other", "an inference, logged"),
    ("parametric", re.compile(r"parametric", re.I), "minor", "taste", "built parametric (library gap)"),
    ("read_by", re.compile(r"read for the|read \(|mark\(s\) read|kept\b|moved to the symbols|adjusted|completion "
                           r"added nothing|no view|overlaps", re.I), "info", "other", "a reading or build note"),
)
DRAWN_MISMATCH_CM = 25              # drawn_mismatch: a difference under this is noise of the reading (info)
FUTILE_TRIES = 4                    # P10: tries on one finding, all refused
TIME_LEFT_MIN_S = 15 * 60           # P8: this much time left before the deadline with open majors is time unused
STAGE_BAD = ("failed", "error", "timeout", "timed_out", "pending", "incomplete", "needs_review")


def classify(text: str) -> tuple[str, str, str, str]:
    """``(rule, severity, kind, meaning)`` of one warning (``WARN_RULES``; ``("other", "info", "other", "")``)."""
    for rule, pat, sev, kind, meaning in WARN_RULES:
        m = pat.search(text)
        if not m:
            continue
        if rule == "shortfall" and int(m.group(1)) >= int(m.group(2)):
            continue                                  # placed all it planned
        if rule == "drawn_mismatch" and abs(int(m.group(1))) < DRAWN_MISMATCH_CM:
            return rule, "info", kind, meaning
        if rule == "not_used":
            rep = re.search(r"(\d+) [^;]*\bnot used\b.*?(\d+) of them repeat", text)
            if rep:                               # the stage says which of them repeat another level's (recorded)
                return rule, "info" if int(rep.group(2)) >= int(rep.group(1)) else "minor", kind, meaning
        return rule, sev, kind, meaning
    return "other", "info", "other", ""


ID_RE = re.compile(r"\b((?:sa|sd|sym|sy|f|w|o|d|win|r|dec|cam|sv|sl)_[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*)\b")
LABEL_RE = re.compile(r"'([^']{2,40})'")


def _target(text: str) -> str:
    """The element a warning is about: its first element id, else its first quoted label, else its start."""
    m = ID_RE.search(text)
    if m:
        return m.group(1)
    m = LABEL_RE.search(text)
    return m.group(1) if m else _subject(text)


def _built_label(inp: Inputs, label: str) -> bool:
    """A site area of the final building with this label that is built with an outline (or a platform naming it)."""
    site = (inp.final or {}).get("site") or {}
    lab = label.strip().lower()
    for a in (site.get("areas") or []) + (site.get("platforms") or []) + (site.get("outdoor_spaces") or []):
        if lab and lab in str(a.get("label") or a.get("label_raw") or a.get("id") or "").lower() \
                and a.get("build") is not False and (a.get("polygon") or a.get("outline")):
            return True
    return False


def stages(inp: Inputs) -> list[dict]:
    """P1."""
    out = []
    rows = []
    for pr in (inp.run_manifest or {}).get("projects") or []:
        if pr.get("name") == inp.project:
            rows = pr.get("stages") or []
    seen = {r.get("stage") for r in rows}
    rows = list(rows) + [dict(r, stage=name) for name, r in inp.records.items()
                         if isinstance(r, dict) and name not in seen and r.get("status")]
    finals = {r.get("stage"): r for r in rows}
    for name, r in finals.items():
        status = str(r.get("status") or "")
        if status == "pending" and finals.get(f"{name}_final", {}).get("status") == "ok":
            continue                                   # the pipeline waits for its answers, then runs again
        if status in STAGE_BAD:
            out.append(K.finding("process", "P1", "critical" if status in ("failed", "error") else "major", name,
                                 f"stage {name} ended '{status}': {r.get('note') or 'no note'}", owner=name,
                                 evidence={"seconds": r.get("seconds")}, kind="process"))
        elif status == "skipped" and not r.get("note"):
            out.append(K.finding("process", "P1", "minor", name, f"stage {name} was skipped with no reason",
                                 owner=name, kind="process"))
    return out


def warnings_of(inp: Inputs) -> list[tuple[str, str]]:
    """Every warning a stage wrote, with its source: the final building's (the reading's and the fit's), the scene
    manifest's, the site's."""
    out = []
    seen = set()
    for src, items in (("building", (inp.final or {}).get("warnings")), ("scene", (inp.manifest or {}).get("warnings")),
                       ("site", ((inp.manifest or {}).get("site") or {}).get("warnings"))):
        for w in items or []:
            text = w if isinstance(w, str) else str((w or {}).get("message") or (w or {}).get("text") or w)
            if text not in seen:
                seen.add(text)
                out.append((src, text))
    return out


PREFIX_RE = re.compile(r"^\s*(?:[\w.-]+\.(?:dwg|dxf|pdf)(?: r\d+)?|[A-Z]\d+)\s*:\s*", re.I)


def _subject(text: str) -> str:
    """What a warning is about, for merging the cases of one problem: its element id, else its text up to the first
    ':' or ';' with the file or level prefix taken off and numbers and quoted names made general ("roof vs the drawn
    section at s # m" for every point of that check; "room '...' has more labels" for every room)."""
    m = ID_RE.search(text)
    if m:
        return m.group(1)
    t = PREFIX_RE.sub("", text)
    t = re.sub(r"'[^']*'", "'...'", t)
    t = re.sub(r"[-+]?\d+(?:[.,]\d+)?", "#", t)
    head = re.split(r"[:;]", t, maxsplit=1)[0].strip(" ,")
    return head[:80] or text[:48]


def unmatched(inp: Inputs) -> list[str]:
    """The warnings no rule of ``WARN_RULES`` knows: listed in full in the report and read by Argus AI (nothing unread)."""
    return [text for _src, text in warnings_of(inp) if classify(text)[0] == "other"]


def warnings(inp: Inputs) -> tuple[list[dict], dict]:
    """P2 and the count of every warning by rule (``{"rule": n}``, ``other`` = no rule matched). The cases of one
    problem (one rule, one subject) are one finding with every case in its evidence and the worst severity."""
    groups: dict = {}
    counts: dict = {}
    for src, text in warnings_of(inp):
        rule, sev, kind, meaning = classify(text)
        if rule == "outside_not_room" and _built_label(inp, _target(text)):
            rule, sev = "outside_built", "info"        # the site stage built it after all
        counts[rule] = counts.get(rule, 0) + 1
        if sev not in ("major", "critical", "minor"):
            continue
        key = (rule, _subject(text) if rule != "outside_not_room" else _target(text))
        g = groups.setdefault(key, {"rule": rule, "sev": sev, "kind": kind, "meaning": meaning, "src": src,
                                    "target": _target(text), "cases": []})
        if K.SEVERITY_RANK.get(sev, 0) > K.SEVERITY_RANK.get(g["sev"], 0):
            g["sev"] = sev
        g["cases"].append(text)
    out = []
    for (rule, subject), g in groups.items():
        cases = g["cases"]
        target = g["target"] if len(cases) == 1 else subject
        msg = cases[0] if len(cases) == 1 else f"{subject}: {len(cases)} cases, e.g. {cases[0]}"
        out.append(K.finding("process", "P2", g["sev"], target, f"{g['meaning']}: {msg[:400]}", owner=g["src"],
                             evidence={"rule": rule, "source": g["src"], "cases": cases}, kind=g["kind"],
                             fix="build_outdoor_space" if rule == "outside_not_room" else None))
    return out, counts


def questions(inp: Inputs) -> list[dict]:
    """P3."""
    out = []
    req = inp.requests or {}
    items = req.get("requests") or req.get("questions") or (req if isinstance(req, list) else [])
    answered = set()
    for ans in inp.answers.values():
        for a in (ans or {}).get("answers") or (ans if isinstance(ans, list) else []):
            if isinstance(a, dict) and a.get("id") and a.get("answer") not in (None, "", "unknown"):
                answered.add(a["id"])
    for q in items or []:
        if isinstance(q, dict) and q.get("id") and inp.answers and q["id"] not in answered:
            out.append(K.finding("process", "P3", "major", q["id"],
                                 f"recognition question {q['id']} ({q.get('kind') or q.get('topic') or '?'}) has no "
                                 f"answer from any model", owner="recognize", kind="untyped"))
    arch = inp.architect or {}
    for q in arch.get("questions") or []:
        if not isinstance(q, dict):
            continue
        for a in q.get("answers") or []:
            if isinstance(a, dict) and a.get("open") and q.get("severity") in ("major", "critical"):
                out.append(K.finding("process", "P3", q["severity"], f"{q.get('id')}:{a.get('element')}",
                                     f"the architect's question {q.get('id')} ({q.get('topic')}) is open for "
                                     f"{a.get('element')}: {a.get('found') or ''}"[:300], owner="architect",
                                     kind="no_sense"))
    return out


def tests(inp: Inputs) -> list[dict]:
    """P4."""
    out = []
    for path in inp.junit:
        try:
            root = ET.parse(path).getroot()
        except (OSError, ET.ParseError):
            out.append(K.finding("process", "P4", "major", path.name, f"test report {path.name} cannot be read",
                                 owner="tests", kind="process"))
            continue
        for tc in root.iter("testcase"):
            for ch in tc:
                if ch.tag in ("failure", "error"):
                    out.append(K.finding("process", "P4", "major", tc.get("name"),
                                         f"test {tc.get('classname')}::{tc.get('name')} {ch.tag}: "
                                         f"{(ch.get('message') or '').strip()[:400]}", owner="tests", kind="process",
                                         evidence={"report": path.name}))
    return out


def scene_checks(inp: Inputs) -> list[dict]:
    """P5."""
    out = []
    m = inp.manifest or {}
    for ray in (m.get("checks") or {}).get("door_rays") or []:
        if ray.get("hit"):
            out.append(K.finding("process", "P5", "major", ray.get("opening_id"),
                                 f"the ray through opening {ray.get('opening_id')} hits {ray.get('hit_object')} "
                                 f"({ray.get('hit_kind')}): something blocks the way through", owner="build",
                                 kind="no_sense", fix="clear_opening"))
    furn = m.get("furniture") or {}
    for level, checks in (furn.get("scene_checks") or {}).items():
        for cid, c in (checks or {}).items():
            if isinstance(c, dict) and c.get("failed"):
                out.append(K.finding("process", "P5", "major", f"{level}:{cid}",
                                     f"scene check {cid} on {level}: {c['failed']} of {c.get('checked')} failed",
                                     owner="build", kind="detached" if cid == "S5" else "geometry"))   # 28 Oct 2026
    for d in furn.get("decor_not_rested") or []:
        out.append(K.finding("process", "P5", "minor", d.get("id"),
                             f"decor {d.get('type')} {d.get('id')} on {d.get('host_id')} not built: {d.get('reason')}",
                             owner="decor", kind="geometry"))
    return out


def views(inp: Inputs) -> list[dict]:
    """P6."""
    out = []
    m = inp.manifest or {}
    for r in m.get("rooms_without_view") or []:
        area = float(r.get("area_m2") or 0)
        out.append(K.finding("process", "P6", "major" if area >= 4.0 else "info", r.get("room_id"),
                             f"room {r.get('label') or r.get('room_id')} ({area:.1f} m2) has no view: "
                             f"{r.get('reason')}", owner="cameras", kind="lost"))
    for c in m.get("cameras_dropped") or []:
        cid = c.get("name") if isinstance(c, dict) else str(c)
        out.append(K.finding("process", "P6", "minor", cid, f"camera {cid} dropped: "
                             f"{(c.get('reason') if isinstance(c, dict) else '') or 'no reason'}", owner="cameras",
                             kind="lost"))
    return out


def library(inp: Inputs) -> list[dict]:
    """P7."""
    out = []
    furn = (inp.manifest or {}).get("furniture") or {}
    for f in furn.get("fallbacks") or []:
        out.append(K.finding("process", "P7", "minor", f.get("id"),
                             f"{f.get('type')} {f.get('id')} built below the library level: {f.get('reason')}",
                             owner="fit", kind="taste", fix="library_gap"))
    proxies = furn.get("proxies")
    if isinstance(proxies, list):
        for p in proxies:
            pid = p.get("id") if isinstance(p, dict) else str(p)
            out.append(K.finding("process", "P7", "major", pid, f"{pid} built as a proxy", owner="fit", kind="taste",
                                 fix="library_gap"))
    elif proxies:
        out.append(K.finding("process", "P7", "major", "proxies", f"{proxies} piece(s) built as proxies", owner="fit",
                             kind="taste", fix="library_gap"))
    return out


def library_titles(inp: Inputs) -> list[dict]:
    """P11 (28 Oct 2026, user on real04 run 20261028-005318-full: "what is this miniature table makes no sense", a
    2.4 m table set read in feet as a coffee table; "terrible sink", a kitchen sink as five washbasins; "is this a
    window?", a "WARDROBE" the vision audit said is not one): every built library model its own names or its audit
    refuse (``wenart.furniture.model_title.fitted_findings`` on the final building: a stated size its box disagrees
    with, a set of pieces, a title of another type or use, a vision doubt of its type or size), kind ``misread`` (the
    library read the model wrong), fixed by another model (``swap_model``) and the catalogue rule."""
    from wenart.furniture import model_title as MT
    out, seen = [], set()
    # the fitted building (every dwelling's pieces) and the building as built (the pieces the scene holds)
    for b in (inp.stage("final"), inp.final):
        for v in MT.fitted_findings(b):
            if v.get("target") in seen:
                continue
            seen.add(v.get("target"))
            out.append(K.finding("process", "P11", "major", v.get("target"), v.get("message") or "", owner="fit",
                                 kind="misread", evidence=dict(v.get("metrics") or {}, room_id=v.get("room_id")),
                                 fix="swap_model"))
    return out


def _open_points(inp: Inputs) -> int:
    """The open major and critical points at the end: the model review's, the inspector's (code and vision) and the
    architect's open majors."""
    sev = ("major", "critical")
    n = sum(1 for f in (inp.model_review or {}).get("findings") or [] if f.get("severity") in sev)
    ins = inp.inspector or {}
    n += sum(1 for f in (ins.get("code") or []) + (ins.get("vision") or []) if f.get("severity") in sev)
    n += int((ins.get("counts") or {}).get("architect_open_major") or 0)
    return n


def time_left(inp: Inputs) -> list[dict]:
    """P8."""
    from datetime import datetime, timezone

    rm = inp.run_manifest or {}
    deadline, finished = rm.get("deadline"), rm.get("finished_utc")
    if not deadline or not finished:
        return []
    try:
        end = datetime.strptime(finished, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
    except ValueError:
        return []
    left = float(deadline) - end
    open_n = _open_points(inp)
    if left >= TIME_LEFT_MIN_S and open_n:
        return [K.finding("process", "P8", "major", "run",
                          f"the run ended {left / 60:.0f} min before its deadline with {open_n} open major point(s): "
                          f"the time could have gone to more fix cycles", owner="scheduler", kind="process",
                          evidence={"minutes_left": round(left / 60, 1), "open": open_n}, fix="more_cycles")]
    return []


def _score(cycle: dict):
    s = cycle.get("score")
    return s.get("score") if isinstance(s, dict) else s


def loop_result(inp: Inputs) -> list[dict]:
    """P9."""
    out = []
    loop = inp.big_loop or {}
    cycles = [c for c in loop.get("cycles") or [] if _score(c) is not None]
    for c in cycles:
        if c.get("verdict") == "worse":
            out.append(K.finding("process", "P9", "minor", f"cycle {c.get('cycle')}",
                                 f"big-loop cycle {c.get('cycle')} made the house worse (score {_score(c)}); "
                                 f"{c.get('note') or 'rolled back'}", owner="agent", kind="process"))
    first = next((c for c in cycles if c.get("cycle") == 0), None)
    later = [c for c in cycles if c.get("cycle")]
    if first is not None and (not later or max(float(_score(c)) for c in later) <= float(_score(first))):
        out.append(K.finding("process", "P9", "major", "big_loop",
                             f"the big loop did not raise the house score (first {_score(first)}; "
                             f"{len(later)} cycle(s); stop: {loop.get('stop')})", owner="agent", kind="process",
                             fix="more_cycles"))
    return out


def _run_events(log: Optional[dict]) -> list[dict]:
    """The events of this run of an appended log (``run_first_seq`` on, as ``wenart.report.agent.run_scope``)."""
    log = log or {}
    try:
        first = int(log.get("run_first_seq") or 1)
    except (TypeError, ValueError):
        first = 1

    def seq(e):
        try:
            return int(e.get("seq") or 0)
        except (TypeError, ValueError):
            return 0
    return [e for e in log.get("events") or [] if isinstance(e, dict) and seq(e) >= first]


def _refusal(e: dict) -> str:
    v = e.get("validation")
    if isinstance(v, str):
        m = re.search(r"failed_checks': \[['\"](.*?)['\"]", v)
        text = m.group(1) if m else v
    elif isinstance(v, dict):
        text = "; ".join(map(str, v.get("failed_checks") or [])) or str(v.get("reason") or "")
    else:
        text = str(e.get("note") or "")
    text = re.sub(r"^memory: the same edit was rejected in round \d+: ", "", text)
    return text[:160]


def futile(inp: Inputs) -> list[dict]:
    """P10 (module docstring)."""
    tries: dict = {}
    for e in _run_events(inp.agent_log):
        if e.get("kind") not in ("edit", "rejected_edit"):
            continue
        key = (str(e.get("checklist") or "?"), str(e.get("target") or "?"))
        t = tries.setdefault(key, {"n": 0, "ok": 0, "tools": {}, "why": {}, "finding": e.get("finding"),
                                   "severity": e.get("severity"), "room": e.get("room_id")})
        t["n"] += 1
        if e.get("kind") == "edit":
            t["ok"] += 1
        else:
            w = _refusal(e)
            t["why"][w] = t["why"].get(w, 0) + 1
        t["tools"][str(e.get("tool"))] = t["tools"].get(str(e.get("tool")), 0) + 1
    out = []
    for (check, target), t in sorted(tries.items(), key=lambda kv: -kv[1]["n"]):
        if t["n"] < FUTILE_TRIES or t["ok"]:
            continue
        why = max(t["why"].items(), key=lambda kv: kv[1])[0] if t["why"] else "?"
        owner = "furniture" if why.startswith(("no_place", "drawn_lock")) else "agent"
        out.append(K.finding("process", "P10", "major" if t["severity"] in ("critical", "major") else "minor", target,
                             f"the agent tried {t['n']} times to fix {check} on {target} ({str(t['finding'])[:120]}) "
                             f"with {', '.join(sorted(t['tools']))}; code refused every try, most often: {why}",
                             owner=owner, kind="silent",
                             evidence={"check": check, "tries": t["n"], "tools": t["tools"], "refusals": t["why"],
                                       "room": t["room"]}, fix="rule_needed"))
    return out


MISSING_SET = "not in the assets manifest"      # materials.MaterialLibrary's reason for a set it could not find


def lost_textures(inp: Inputs) -> list[dict]:
    """P12 (module docstring): one finding per material of the scene built flat because its texture set was missing,
    with the number of objects that wear it (the scene manifest's ``materials`` records and its objects)."""
    man = inp.manifest or {}
    mats = man.get("materials") or {}
    users: dict = {}
    for o in man.get("objects") or []:
        if o.get("material"):
            users[o["material"]] = users.get(o["material"], 0) + 1
    out = []
    for name, rec in sorted(mats.items()):
        reason = str((rec or {}).get("reason") or "")
        if rec.get("textured") or MISSING_SET not in reason:
            continue
        n = users.get(name, 0)
        out.append(K.finding("process", "P12", "major" if n >= 3 else "minor", name,
                             f"{name} ({rec.get('slug')}) is built flat on {n} object(s): {reason}", owner="assets",
                             kind="lost", evidence={"slug": rec.get("slug"), "objects": n},
                             fix="rerun_stage assets (wenart.assets.fetch: the finish's texture set)"))
    return out


def audit(inp: Inputs) -> dict:
    """``{"findings", "warning_counts", "checked"}`` of the process line."""
    warn, counts = warnings(inp)
    findings = stages(inp) + warn + questions(inp) + tests(inp) + scene_checks(inp) + views(inp) + library(inp) \
        + time_left(inp) + loop_result(inp) + futile(inp) + library_titles(inp) + lost_textures(inp)
    return {"findings": findings, "warning_counts": counts, "unmatched": unmatched(inp),
            "checked": {"stages": len(inp.records) or len(((inp.run_manifest or {}).get("projects") or [{}])[0]
                                                          .get("stages") or []),
                        "warnings": sum(counts.values()), "test_reports": len(inp.junit),
                        "missing_records": list(inp.missing)}}


def summary_line(res: dict) -> Optional[str]:
    c = res.get("warning_counts") or {}
    return ", ".join(f"{k} {v}" for k, v in sorted(c.items(), key=lambda kv: -kv[1])) if c else None
