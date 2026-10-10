"""Keep / fix / remove per model (docs/milestone12.md §6.1 D21, §6.2 D22).

What: ``decide(item, checks, answer=None, answer2=None, cfg)`` -> ``{"status", "reasons", "fixes", "pending",
"flags", "notes"}``:

- ``removed``: a wrong object (title, vision), outdoor, an NC / SA / ND licence, a broken mesh, proportions no real
  piece of the type has, a model lying on its side, a duplicate, quality <= 2, a crude or not-real model below
  quality 4, an open drawer or a part apart, a known-unit product more than 30 % off its type's real size;
- ``fix``: catalogue fields only (``fixes``): ``origin_offset`` / boxes (pivot), ``front_quarter_turns`` (front),
  ``rescale`` (unit scale, size off by 15-30 % or a wrong unit guess), ``type`` (a real product filed under the wrong
  type: the title names the type, the box fits it and the vision check agrees);
- ``keep``: everything else;
- ``pending`` (dry audit only, never written to the catalogue): what still needs the vision answer, with the
  expected outcome.

Vision rules (CLAUDE.md evidence rules; risk table of §10: "a wrong object needs both the vision answer and the title
check to stay"): a titled model stays only when the title does not conflict and the vision answer says it is the
type; a model whose title names no type (Objaverse titles such as "Lpuvw", generated models) stays only when two
independent vision passes agree (pass 1, then the type question of pass 2, ``ask.py``).

``flags`` are the catalogue flags of contract §13.3: ``real_product`` (ABO: true; generated: false; else the vision
answer), ``has_bedding`` / ``has_pillows`` (beds), ``has_cushions`` (beds and seats), ``contact`` (decor:
``flat_bottom | hangs | leans | drapes``; the type's default when the vision answer has none).

How: pure; reasons in plain words; the same input gives the same decision.
"""
from __future__ import annotations

from typing import Optional

from wenart.assets.audit import keywords as K
from wenart.assets.audit.items import has_front

BED_TYPES = ("bed_single", "bed_double", "bunk_bed", "crib")
SEAT_TYPES = ("sofa", "sofa_corner", "armchair", "chaise", "chair", "bench", "ottoman", "office_chair", "bar_stool")
# The decor contact of a type when the vision answer gives none (decor ray casts, track S).
DEFAULT_CONTACT = {"wall_art": "hangs", "mirror": "hangs", "clock": "hangs", "curtain": "hangs", "blind": "hangs",
                   "pendant_light": "hangs", "ceiling_light": "hangs", "throw": "drapes", "cushion": "leans"}
CONTACTS = ("flat_bottom", "hangs", "leans", "drapes")
FRONT_TURNS = {"front": 0, "right": 1, "back": 2, "left": 3}     # where the true front faces, seen in view 0


def _by(checks: list[dict], name: str) -> list[dict]:
    return [c for c in checks if c.get("check") == name]


def _status(checks: list[dict], name: str) -> Optional[str]:
    found = _by(checks, name)
    return found[0]["status"] if found else None


def default_flags(item: dict) -> dict:
    flags: dict = {}
    src = item.get("source")
    flags["real_product"] = True if src == "abo" else (False if src == "generated" else None)
    if item["kind"] == "decor":
        flags["contact"] = DEFAULT_CONTACT.get(item["type"], "flat_bottom")
    return flags


def answer_flags(item: dict, answer: Optional[dict]) -> dict:
    flags = default_flags(item)
    if not answer:
        return flags
    if item.get("source") not in ("abo", "generated") and isinstance(answer.get("real_product"), bool):
        flags["real_product"] = answer["real_product"]
    t = item["type"]
    if t in BED_TYPES:
        for key in ("has_bedding", "has_pillows"):
            if isinstance(answer.get(key), bool):
                flags[key] = answer[key]
    if t in BED_TYPES or t in SEAT_TYPES:
        if isinstance(answer.get("has_cushions"), bool):
            flags["has_cushions"] = answer["has_cushions"]
    if item["kind"] == "decor" and answer.get("contact") in CONTACTS:
        flags["contact"] = answer["contact"]
    return flags


def decide(item: dict, checks: list[dict], answer: Optional[dict] = None, answer2: Optional[dict] = None,
           cfg: Optional[dict] = None) -> dict:
    cfg = cfg or {}
    qc = cfg.get("quality") or {}
    remove_max, keep_min = int(qc.get("remove_max", 2)), int(qc.get("crude_keep_min", 4))
    reasons: list[str] = []
    fixes: dict = {}
    pending: list[dict] = []
    notes: list[str] = []

    for c in checks:
        if c["status"] == "remove":
            reasons.append(c["reason"])
        elif c["status"] == "fix":
            for k, v in (c.get("fix") or {}).items():
                if k == "front_quarter_turns":
                    fixes[k] = (fixes.get(k, 0) + int(v)) % 4
                elif k == "rescale":
                    fixes[k] = round(fixes.get(k, 1.0) * float(v), 4)
                else:
                    fixes[k] = v
            notes.append(c["reason"])
        elif c["status"] == "warn":
            notes.append(c["reason"])

    title = (_by(checks, "title") or [{}])[0]
    verdict = (title.get("metrics") or {}).get("verdict")
    q = answer.get("quality") if answer else None

    # title review cases: a retype candidate, a scene word, no title evidence
    if title.get("status") == "review" and verdict == "conflict":
        sug = title["metrics"].get("suggested_type")
        if answer is None:
            pending.append({"needs": "vision", "why": title["reason"], "expect": "fix"})
        elif answer.get("is_type") is True:
            reasons.append(f"the title names a {sug}, the vision check a {item['type']}: they disagree")
        elif answer.get("type_guess") in (sug, None) or not answer.get("type_guess"):
            fixes["type"] = sug
            notes.append(f"retyped {item['type']} -> {sug}: the title and the vision check agree")
        else:
            reasons.append(f"the title names a {sug}, the vision check a {answer.get('type_guess')}")
    for c in _by(checks, "title_flag"):
        if c["status"] != "review":
            continue
        if answer is None:
            pending.append({"needs": "vision", "why": c["reason"], "expect": "remove"})
        elif not (answer.get("single_object") is True and answer.get("is_type") is True):
            reasons.append(c["reason"] + " (the vision check confirms)")
    if _status(checks, "crude") == "review":
        c = _by(checks, "crude")[0]
        if answer is None:
            # textured real products (ABO, Poly Haven scans) are often box-like with few faces: expected to stay
            real = item.get("source") in ("abo", "polyhaven")
            pending.append({"needs": "vision", "why": c["reason"], "expect": "keep" if real else "remove"})
        elif not (isinstance(q, int) and q >= keep_min):
            reasons.append(f"{c['reason']}; vision quality {q}")
    if _status(checks, "outside_parts") == "review" and answer is not None and answer.get("parts_open") is None:
        notes.append(_by(checks, "outside_parts")[0]["reason"])

    # the vision answer
    untitled = verdict in ("silent", "generated")
    if answer is None:
        if untitled:
            pending.append({"needs": "vision x2", "why": title.get("reason", ""), "expect": "keep or remove"})
        elif not reasons:
            pending.append({"needs": "vision", "why": "every model needs the vision check (type, indoor, quality)",
                            "expect": "keep"})
    else:
        if answer.get("is_type") is False and "type" not in fixes:
            reasons.append(f"the vision check says it is not a {item['type']}"
                           + (f" (a {answer['type_guess']})" if answer.get("type_guess") not in (None, "other",
                                                                                                    item["type"])
                              else ""))
        elif answer.get("is_type") is True and untitled:
            if answer2 is None:
                pending.append({"needs": "vision pass 2", "why": "no title evidence: two passes must agree",
                                "expect": "keep"})
            elif not K.near(str(answer2.get("type_guess")), item["type"]):
                reasons.append(f"the two vision passes disagree: a {item['type']} and a {answer2.get('type_guess')}")
        if answer.get("indoor") == "outdoor":
            reasons.append("the vision check says it is an outdoor piece")
        if answer.get("single_object") is False:
            reasons.append("the vision check sees more than one object")
        if answer.get("upright") is False:
            reasons.append("the vision check sees it lying on its side or upside down")
        if answer.get("parts_open") is True:
            reasons.append("a drawer, door or lid is open, or a part floats apart")
        if isinstance(q, int) and q <= remove_max:
            reasons.append(f"vision quality {q} (<= {remove_max})")
        elif answer.get("real_product") is False and item.get("source") != "abo" and isinstance(q, int) \
                and q < keep_min:
            reasons.append(f"not a real manufactured product and vision quality {q} (< {keep_min})")
        side = answer.get("front_shown")
        if has_front(item["type"]) and side in FRONT_TURNS and FRONT_TURNS[side]:
            fixes["front_quarter_turns"] = (fixes.get("front_quarter_turns", 0) + FRONT_TURNS[side]) % 4
            notes.append(f"the vision check sees the front on the {side} of view 0: front turned")
        elif has_front(item["type"]) and side == "unclear":
            notes.append("the vision check cannot tell the front")
        if answer.get("size_plausible") is False and _status(checks, "size") == "ok":
            notes.append("the vision check finds the size odd next to the scale reference (code: size ok)")

    flags = answer_flags(item, answer)
    if fixes.get("front_quarter_turns") == 0:
        fixes.pop("front_quarter_turns")
    if fixes.get("rescale") == 1.0:
        fixes.pop("rescale")
    if reasons:
        status = "removed"
    elif pending:
        status = "pending"
    elif fixes:
        status = "fix"
    else:
        status = "keep"
    return {"status": status, "reasons": reasons, "fixes": fixes if status != "removed" else {},
            "pending": pending if not reasons else [], "flags": flags, "notes": notes}


def expected_status(decision: dict) -> str:
    """The dry audit's expected outcome: removed / fix / keep as decided, else the expectation of its pending items
    (remove beats fix beats keep; an untitled model needs two passes: ``vision``)."""
    if decision["status"] != "pending":
        return decision["status"]
    expects = [p.get("expect") for p in decision["pending"]]
    if "remove" in expects:
        return "removed?"
    if "fix" in expects or decision.get("fixes"):
        return "fix?"
    if "keep or remove" in expects:
        return "vision?"
    return "keep?"
