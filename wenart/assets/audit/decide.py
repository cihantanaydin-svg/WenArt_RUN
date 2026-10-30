"""Keep / fix / remove per model (docs/milestone12.md §6.1 D21, §6.2 D22).

What: ``decide(item, checks, answer=None, answer2=None, cfg)`` -> ``{"status", "reasons", "fixes", "pending",
"flags", "notes"}``:

- ``removed``: a wrong object (title, vision), outdoor, an NC / SA / ND licence, a broken mesh, proportions no real
  piece of the type has, a model lying on its side (not a light hanging from its top), more than one object (not
  books, candles, a tray, a bowl or a basket), a duplicate, quality <= 2, a crude or not-real model below quality 4
  (a crude real product, ABO or Poly Haven, below 3), a known-unit product more than 30 % off its type's real size
  (30 Oct 2026, UL215 / UL216: an open drawer, door or lid and a maker's logo or print are flags, ``open_parts`` and
  ``logo_flag``, never removals);
- ``fix``: catalogue fields only (``fixes``): ``origin_offset`` / boxes (pivot), ``front_quarter_turns`` (front),
  ``rescale`` (unit scale, size off by 15-30 % or a wrong unit guess), ``type`` (a real product filed under the wrong
  type: the title names the type, the box fits it and the vision check agrees);
- ``keep``: everything else;
- ``vision_doubt`` (user decision 1a of 11 Oct 2026, docs/milestone12.md §14.3): a finding of the vision check alone
  (another type, two passes disagree, outdoor, more than one object, quality <= 2, not a real product below quality 4)
  no longer removes a model: the bake-off and the P3 sheets showed these look judgements are often wrong. The model is
  kept (or fixed) with the findings in ``vision_doubt``; each run's final vision check looks at the doubtful models in
  its views. Code evidence (licence, title, proportions, crude with low quality, duplicates, a broken mesh) and the
  specific vision findings (lying on its side, an open part) still remove; a removed model lists its doubts too;
- ``pending`` (dry audit only, never written to the catalogue): what still needs the vision answer, with the
  expected outcome.

Vision rules (CLAUDE.md evidence rules; risk table of §10: "a wrong object needs both the vision answer and the title
check to stay"): a titled model stays only when the title does not conflict and the vision answer says it is the
type; a model whose title names no type (Objaverse titles such as "Lpuvw", generated models) stays only when two
independent vision passes agree (pass 1, then the type question of pass 2, ``ask.py``).

``flags`` are the catalogue flags of contract §13.3: ``real_product`` (ABO: true; generated: false; else the vision
answer), ``has_bedding`` / ``has_pillows`` (beds), ``has_cushions`` (beds and seats), ``contact`` (decor:
``flat_bottom | hangs | leans | drapes``; the type's default when the vision answer has none).

Milestone 13 (docs/milestone13.md §13.1 track T7; ``audit.yaml gates``): the code gates of ``checks.py`` flow
through the same statuses (``units_anchor`` removes, ``pbr_record`` / ``chaise`` fix, ``pbr`` / ``licence_fields``
warn); a ``material_tags`` review waits for the vision answer's ``materials`` (the m13.1 question, ``ask.py``) and
writes them as the flag ``material_tags`` (the design enum of ``wenart.assets.recolour.TAG_ORDER``); an answer of
the older question (no ``materials``) leaves a note, never a removal and never a second pass (one vision pass).

28 Oct 2026 (user on real04 run 20261028-005318-full: "is this a window? how is this making sense?", a "WARDROBE" the
vision check said is not a wardrobe, kept by decision 1a and fitted): a vision doubt about the type (``is_type``
false, no retype) or the size (``size_plausible`` false while code finds the size ok) keeps the model ``pending``
until the type question of pass 2 confirms the type (``second_look``; two passes against it remove it). A furniture
model the vision check rates ``quality.remove_max`` (2) or lower, or finds no real product (a source whose
``real_product`` the answer sets), is removed (user on real06: "What kind of a bath is this", a 0.37 m bath rated 2);
decor keeps these as doubts.

3D Warehouse layer (23 Oct 2026): an answer of the m13.2 question (``ask.LOGO_FIELDS``) with ``brand_logo`` or
``text_print`` true flags the model (30 Oct 2026, UL215: ``logo_flag`` with the reasons of ``checks.RENDER_FINDINGS``;
trademarks are not licensed, so commercial mode leaves it out, relaxed mode may use it); an open drawer, door or lid
flags ``open_parts`` (UL216), never a removal.

How: pure; reasons in plain words; the same input gives the same decision.
"""
from __future__ import annotations

from typing import Optional

from wenart.assets.audit import keywords as K
from wenart.assets.audit.checks import RENDER_FINDING_WHY, RENDER_FINDINGS
from wenart.assets.audit.items import has_front

BED_TYPES = ("bed_single", "bed_double", "bunk_bed", "crib")
SEAT_TYPES = ("sofa", "sofa_corner", "armchair", "chaise", "chair", "bench", "ottoman", "office_chair", "bar_stool")
# The decor contact of a type when the vision answer gives none (decor ray casts, track S).
DEFAULT_CONTACT = {"wall_art": "hangs", "mirror": "hangs", "clock": "hangs", "curtain": "hangs", "blind": "hangs",
                   "pendant_light": "hangs", "ceiling_light": "hangs", "throw": "drapes", "cushion": "leans"}
CONTACTS = ("flat_bottom", "hangs", "leans", "drapes")
FRONT_TURNS = {"front": 0, "right": 1, "back": 2, "left": 3}     # where the true front faces, seen in view 0
# Pod P3 (11 Oct 2026, docs/milestone12.md §14.2): the sheets show every model standing on the floor, so a light that
# hangs from its top reads as "upside down" (23 pendant and ceiling lights removed); the upright question does not
# apply to them. Decor that is several objects by nature (a stack of books, a candle set, a tray or a bowl with things
# on it, a filled basket) reads as "more than one object"; the single-object question does not apply to it.
HANG_FROM_TOP = ("pendant_light", "ceiling_light")
GROUP_DECOR = ("books", "candle", "tray", "bowl", "basket")
# 30 Oct 2026 (lessons UL215, UL216; user: "There were already laptop models in the library why we have not use that
# one and created a brand new model instead?", then "a dresser with open doors could be used"): an open drawer, door
# or lid (``parts_open``) is no removal for any type; the entry carries the flag ``open_parts`` so a pick may prefer a
# closed model where a closed state matters (a laptop stands open on a desk; the 3D Warehouse layer had removed 5
# laptops for their open lid alone). The geometric checks (parts sticking out, a broken mesh) stay as they are. A
# maker's logo or print (``brand_logo``, ``text_print``) is no removal either: the flag ``logo_flag`` with its reason;
# relaxed mode uses the model, commercial mode leaves it out (``catalog.commercial_safe``). Low quality still removes.
OPEN_PARTS_NOTE = "a drawer, door or lid is open, or a part is pulled out: flagged open_parts (UL216), not removed"
# Textured real products (ABO, Poly Haven scans) are often box-like with few faces: crude only below this quality
# (D21: quality <= 2 removes; the crude rule's quality 4 stays for uploads and generated models).
REAL_SOURCES = ("abo", "polyhaven", "gso", "hssd")  # gso: Google Scanned Objects (scans of products, pod P4); hssd: M13
# The material words a vision answer may name (``ask.schema`` materials) -> the design enum (recolour.TAG_ORDER).
MATERIAL_TAGS: tuple[str, ...] = ("glass", "wood", "metal", "fabric", "rattan", "marble")   # = catalog.MATERIAL_TAGS
                                                                                            # (tests/test_m13_library.py)


def material_tags_of(answer: Optional[dict]) -> Optional[list[str]]:
    """The design material tags of a vision answer's ``materials`` (``other`` dropped, the enum order kept), None when
    the answer has no ``materials`` field (an answer of the m12.1 question)."""
    if not answer or not isinstance(answer.get("materials"), list):
        return None
    words = {str(w).lower() for w in answer["materials"]}
    return [t for t in MATERIAL_TAGS if t in words]


def _by(checks: list[dict], name: str) -> list[dict]:
    return [c for c in checks if c.get("check") == name]


def _status(checks: list[dict], name: str) -> Optional[str]:
    found = _by(checks, name)
    return found[0]["status"] if found else None


def default_flags(item: dict) -> dict:
    flags: dict = {}
    src = item.get("source")
    flags["real_product"] = True if src in ("abo", "gso") else (False if src == "generated" else None)
    if item["kind"] == "decor":
        flags["contact"] = DEFAULT_CONTACT.get(item["type"], "flat_bottom")
    return flags


def answer_flags(item: dict, answer: Optional[dict]) -> dict:
    flags = default_flags(item)
    if not answer:
        return flags
    if item.get("source") not in ("abo", "gso", "generated") and isinstance(answer.get("real_product"), bool):
        flags["real_product"] = answer["real_product"]
    t = item["type"]
    if t in BED_TYPES:
        for key in ("has_bedding", "has_pillows"):
            if isinstance(answer.get(key), bool):
                flags[key] = answer[key]
    if t in BED_TYPES or t in SEAT_TYPES:
        if isinstance(answer.get("has_cushions"), bool):
            flags["has_cushions"] = answer["has_cushions"]
        if isinstance(answer.get("has_scatter_cushions"), bool):     # 30 Oct 2026 (UL180): the m13.4 question
            flags["has_scatter_cushions"] = answer["has_scatter_cushions"]
    if item["kind"] == "decor" and answer.get("contact") in CONTACTS:
        flags["contact"] = answer["contact"]
    return flags


def second_look(text: str, item: dict, answer2: Optional[dict], reasons: list, notes: list, doubts: list,
                pending: list) -> None:
    """28 Oct 2026 (user on real04 run 20261028-005318-full: "is this a window? how is this making sense?", a
    "WARDROBE" whose vision answer said is_type false and size_plausible false, audited ``fix`` and fitted): a vision
    doubt about the type or the size no longer keeps the model (decision 1a of 11 Oct 2026 for these two findings):
    the type question of pass 2 confirms it (its type guess near the type: a note, the model is used), contradicts it
    (removed: two passes) or is still to be asked (``pending``: the doubt recorded, ``cli.second_pass_ids`` asks it)."""
    guess = str((answer2 or {}).get("type_guess") or "")
    if answer2 is not None and K.near(guess, item["type"]):
        notes.append(f"{text.replace('the vision check', 'pass 1')}; pass 2 names a {guess}: the type is confirmed")
    elif answer2 is not None:
        reasons.append(f"{text}, and pass 2 names a {guess or 'other'}: two passes doubt the {item['type']}")
    else:
        doubts.append(text)
        pending.append({"needs": "vision pass 2", "why": f"{text}: a second pass must confirm the type before the "
                        f"model is used", "expect": "keep or remove"})


def decide(item: dict, checks: list[dict], answer: Optional[dict] = None, answer2: Optional[dict] = None,
           cfg: Optional[dict] = None) -> dict:
    cfg = cfg or {}
    qc = cfg.get("quality") or {}
    remove_max, keep_min = int(qc.get("remove_max", 2)), int(qc.get("crude_keep_min", 4))
    keep_min_real = int(qc.get("crude_keep_min_real", remove_max + 1))
    reasons: list[str] = []
    fixes: dict = {}
    pending: list[dict] = []
    notes: list[str] = []
    doubts: list[str] = []          # vision-only findings (user decision 1a of 11 Oct 2026, §14.3)
    extra_flags: dict = {}          # UL215, UL216: open_parts, logo_flag and logo_reason (flags, never removals)

    for c in checks:
        if c["status"] == "remove" and c.get("check") == "render_print":
            # UL215: a maker's logo or print a run's render showed is a flag (commercial mode leaves it out), never a
            # removal (the user: "no need to reject them")
            extra_flags.update(logo_flag=True, logo_reason=c["reason"])
        elif c["status"] == "remove":
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
    if answer and answer.get("is_type") is False and answer.get("type_guess") == item["type"]:
        # a contradictory answer ("not a clock", type guess: clock): its type guess names the type, so it is the type
        answer = dict(answer, is_type=True)
        notes.append(f"the vision answer says not a {item['type']} but names {item['type']} as what it is: "
                     f"taken as a {item['type']}")

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
        elif not (isinstance(q, int) and q >= (keep_min_real if item.get("source") in REAL_SOURCES else keep_min)):
            reasons.append(f"{c['reason']}; vision quality {q}")
    if _status(checks, "outside_parts") == "review" and answer is not None and answer.get("parts_open") is None:
        notes.append(_by(checks, "outside_parts")[0]["reason"])
    material_flags: dict = {}
    if _status(checks, "material_tags") == "review":
        tags = material_tags_of(answer)
        if answer is None:
            pending.append({"needs": "vision", "why": _by(checks, "material_tags")[0]["reason"], "expect": "keep"})
        elif tags is None:
            notes.append("material tags not judged: the vision answer is of the question without materials (m12.1); "
                         "the m13.1 question names them")
        else:
            # Review fix (15 Oct 2026): never write "other" into material_tags: catalog.validate (_validate_m10_fields)
            # accepts the design enum MATERIAL_TAGS only, and the write step validates the copy (cli.py), so an
            # "other" tag would make the catalogue copy unloadable. An answer naming none of the design words is
            # recorded as judged with an empty list and the note says what the vision answer named.
            material_flags["material_tags"] = tags
            notes.append(f"material tags from the vision answer: {', '.join(tags) or 'none of the design words'}"
                         + ("" if tags else f" (the answer named: {', '.join(str(w) for w in answer['materials'])})"))

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
            text = (f"the vision check says it is not a {item['type']}"
                    + (f" (a {answer['type_guess']})" if answer.get("type_guess") not in (None, "other", item["type"])
                       else ""))
            # 28 Oct 2026 (user on real04: "is this a window?"): a type doubt waits for a second pass that confirms
            second_look(text, item, answer2, reasons, notes, doubts, pending)
        elif answer.get("is_type") is True and untitled:
            if answer2 is None:
                pending.append({"needs": "vision pass 2", "why": "no title evidence: two passes must agree",
                                "expect": "keep"})
            elif not K.near(str(answer2.get("type_guess")), item["type"]):
                doubts.append(f"the two vision passes disagree: a {item['type']} and a {answer2.get('type_guess')}")
        if answer.get("indoor") == "outdoor":
            doubts.append("the vision check says it is an outdoor piece")
        if answer.get("single_object") is False and item["type"] not in GROUP_DECOR:
            doubts.append("the vision check sees more than one object")
        if answer.get("upright") is False and item["type"] not in HANG_FROM_TOP:
            reasons.append("the vision check sees it lying on its side or upside down")
        if answer.get("parts_open") is True:
            # UL216: a flag and a note, never a removal (OPEN_PARTS_NOTE)
            extra_flags["open_parts"] = True
            notes.append(OPEN_PARTS_NOTE)
        # 23 Oct 2026 (the 3D Warehouse layer, ask.LOGO_FIELDS): a logo or a print the vision check reads. UL215: a flag
        # with its reason (``logo_flag``, ``logo_reason``), never a removal; commercial mode leaves the model out
        logos = [f"the vision check reads {RENDER_FINDINGS[f]}: {RENDER_FINDING_WHY[f]}"
                 for f in ("brand_logo", "text_print") if answer.get(f) is True]
        if logos:
            extra_flags.update(logo_flag=True, logo_reason="; ".join(logos))
        # 28 Oct 2026 (user on real06: "What kind of a bath is this", a bath rated 2, no real product, kept by
        # decision 1a): a furniture model rated this low or found no real product is removed; decor keeps the doubt
        furniture = item.get("kind") == "furniture"
        if isinstance(q, int) and q <= remove_max:
            (reasons if furniture else doubts).append(f"vision quality {q} (<= {remove_max})")
        elif furniture and answer.get("real_product") is False and item.get("source") not in ("abo", "gso",
                                                                                            "generated"):
            reasons.append("the vision check finds no real manufactured product"
                           + (f" (vision quality {q})" if isinstance(q, int) else ""))
        elif answer.get("real_product") is False and item.get("source") not in ("abo", "gso") and isinstance(q, int) \
                and q < keep_min:
            doubts.append(f"not a real manufactured product and vision quality {q} (< {keep_min})")
        side = answer.get("front_shown")
        # pod P3: the vision answer about one angled view (front 3/4) turns a front only where code is unsure of it
        # (front check review / warn); 179 of 188 turns overrode fronts the M8-M10 judges had agreed on
        unsure_front = _status(checks, "front") in ("review", "warn")
        if has_front(item["type"]) and side in FRONT_TURNS and FRONT_TURNS[side] and not unsure_front:
            notes.append(f"the vision check sees the front on the {side} of view 0; the agreed front is kept")
        elif has_front(item["type"]) and side in FRONT_TURNS and FRONT_TURNS[side]:
            fixes["front_quarter_turns"] = (fixes.get("front_quarter_turns", 0) + FRONT_TURNS[side]) % 4
            notes.append(f"the vision check sees the front on the {side} of view 0: front turned")
        elif has_front(item["type"]) and side == "unclear":
            notes.append("the vision check cannot tell the front")
        if answer.get("size_plausible") is False and _status(checks, "size") in (None, "ok"):
            # 28 Oct 2026: the size doubt waits for a second pass too (its note is the doubt model_title reads)
            second_look("the vision check finds the size odd next to the scale reference (code: size ok)", item,
                        answer2, reasons, notes, notes, pending)

    flags = answer_flags(item, answer)
    flags.update(material_flags)
    flags.update(extra_flags)
    if fixes.get("front_quarter_turns") == 0:
        fixes.pop("front_quarter_turns")
    if fixes.get("rescale") == 1.0:
        fixes.pop("rescale")
    if reasons:
        status = "removed"
        reasons = reasons + doubts
        doubts = []
    elif pending:
        status = "pending"
    elif fixes:
        status = "fix"
    else:
        status = "keep"
    out = {"status": status, "reasons": reasons, "fixes": fixes if status != "removed" else {},
           "pending": pending if not reasons else [], "flags": flags, "notes": notes,
           "vision_doubt": doubts if status in ("keep", "fix") else []}
    if answer and isinstance(answer.get("quality"), int) and not isinstance(answer["quality"], bool):
        # 30 Oct 2026 (UL215): the vision quality, written to ``audit.vision_quality`` (``fit.vision_quality_of``) so
        # a pick can tell a library model better than the procedural build (``fit.library_first_item``); not a flag,
        # so the decision_sha of the entries already written stays the same
        out["vision_quality"] = int(answer["quality"])
    return out


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
