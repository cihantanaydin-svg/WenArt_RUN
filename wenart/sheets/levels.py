"""Levels of the plan regions (docs/milestone10.md §3.1 item 3).

What: ``assign_levels(plans, needs_review, warnings)`` gives every plan region (``use: read``) its level from its
title: order, label, kind (``basement``, ``floor``, ``attic``) and how it was decided (``title`` or ``assumed``).

Why: the pipeline stacks the levels by order and the heights map the section's slab bands to them bottom-up.

How: ``level_of`` reads the level word through the M10 level-word table here (Turkish, English, German, French;
``wenart.building.normalise_level_label`` of M2-M9 is unchanged): ``BODRUM`` = -1, ``ZEMİN`` = 0, ``1. KAT`` = 1, ...
An attic (``ÇATI KAT``, ``ATTIC``, ``DACHGESCHOSS``, ``COMBLES``) is the top level: one above the highest other
titled level (at least 1). An untitled plan gets a level only when it is the project's only plan (``L0``
"Ground floor", as M7), when exactly one level between the titled ones is free, or (real06, 24 Oct 2026: two
untitled plans) when no plan is titled and the plans' own floor marks order them: each plan's floor mark (its most
frequent level mark, ``floor_mark``) at least ``FLOOR_STEP_M`` apart, the lowest one within ``GROUND_BAND_M`` of
±0.00 the ground floor, the others counted from it (``assumed``, listed as inferred); otherwise it needs review.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Optional

from wenart import building as B

# Level words (§3.1 item 3): (order or "top", kind, label, pattern, language).
LEVEL_WORDS: list[tuple[object, str, str, str, str]] = [
    # real10 (1 Nov 2026): the roof terrace floor of an apartment block (its stair house over a flat roof) is the top
    ("top", "roof_terrace", "Teras Katı", r"\bTERAS\.?\s*KATI?\b|\bCATI TERASI\b", "tr"),
    ("top", "roof_terrace", "Roof Terrace", r"\bROOF TERRACE\b", "en"),
    ("top", "roof_terrace", "Dachterrasse", r"\bDACHTERRASSE\b", "de"),
    ("top", "roof_terrace", "Toit-terrasse", r"\bTOIT-TERRASSE\b|\bTOIT TERRASSE\b", "fr"),
    ("top", "attic", "Çatı Katı", r"\bCATI KATI?\b", "tr"),
    ("top", "attic", "Attic", r"\bATTIC\b|\bLOFT\b", "en"),
    ("top", "attic", "Dachgeschoss", r"\bDACHGESCHOSS\b", "de"),
    ("top", "attic", "Combles", r"\bCOMBLES\b", "fr"),
    (-1, "basement", "Bodrum Kat", r"\bBODRUM\b", "tr"),
    (-1, "basement", "Basement", r"\bBASEMENT\b", "en"),
    (-1, "basement", "Untergeschoss", r"\bUNTERGESCHOSS\b|\bKELLER(?:GESCHOSS)?\b", "de"),
    (-1, "basement", "Sous-sol", r"\bSOUS-SOL\b|\bSOUS SOL\b", "fr"),
    (0, "floor", "Zemin Kat", r"\bZEMIN\b", "tr"),
    (0, "floor", "Ground Floor", r"\bGROUND\b", "en"),
    (0, "floor", "Erdgeschoss", r"\bERDGESCHOSS\b", "de"),
    (0, "floor", "Rez-de-chaussée", r"\bREZ-DE-CHAUSSEE\b|\bREZ DE CHAUSSEE\b", "fr"),
]
_LEVEL_RE = [(o, k, lab, re.compile(p), lang) for o, k, lab, p, lang in LEVEL_WORDS]
# real10 (1 Nov 2026): basements counted downwards (``2. BODRUM KAT`` = -2) and a typical floor plan (``NORMAL KAT``,
# ``TİP KAT``: one plan for every upper floor the sections list); a numbered normal floor (``3. NORMAL KAT``) is that
# floor.
_NTH_BASEMENT_RE = [
    (re.compile(r"\b(\d{1,2})\s*\.\s*BODRUM\b"), "tr", "{n}. Bodrum Kat"),
    (re.compile(r"\b(\d{1,2})\s*(?:ST|ND|RD|TH)\s+BASEMENT\b"), "en", "Basement {n}"),
    (re.compile(r"\bBASEMENT\s+(\d{1,2})\b"), "en", "Basement {n}"),
    (re.compile(r"\b(\d{1,2})\s*\.\s*(?:UG|UNTERGESCHOSS)\b"), "de", "{n}. Untergeschoss"),
    (re.compile(r"\b(\d{1,2})\s*(?:ER|E|EME)\s+SOUS-SOL\b"), "fr", "{n}e sous-sol"),
]
_NTH_NORMAL_RE = re.compile(r"\b(\d{1,2})\s*\.\s*(?:NORMAL|TIP)\s+KAT\b")
_TYPICAL_RE = [
    (re.compile(r"\bNORMAL KAT\b|\bTIP KAT\b"), "tr", "Normal Kat"),
    (re.compile(r"\bTYPICAL FLOOR\b|\bTYPICAL PLAN\b"), "en", "Typical Floor"),
    (re.compile(r"\bREGELGESCHOSS\b|\bNORMALGESCHOSS\b"), "de", "Regelgeschoss"),
    (re.compile(r"\bETAGE COURANT\b"), "fr", "Étage courant"),
]
_NTH_RE = [
    (re.compile(r"\b(\d{1,2})\s*\.\s*KAT\b"), "tr", "{n}. Kat"),
    # 2 Nov 2026 (real07: 'I.KAT PLANI'): a floor numbered in Roman numerals
    (re.compile(r"\b(I{1,3}|IV|VI{0,3}|IX|X)\s*\.\s*KAT\b"), "tr", "{n}. Kat"),
    (re.compile(r"\b(I{1,3}|IV|VI{0,3}|IX|X)\s*\.\s*(?:OG|OBERGESCHOSS)\b"), "de", "{n}. Obergeschoss"),
    (re.compile(r"\b(\d{1,2})\s*(?:ST|ND|RD|TH)\s+FLOOR\b"), "en", "{n}th Floor"),
    (re.compile(r"\b(FIRST|SECOND|THIRD|FOURTH)\s+FLOOR\b"), "en", "{w} Floor"),
    (re.compile(r"\b(\d{1,2})\s*\.\s*(?:OG|OBERGESCHOSS)\b"), "de", "{n}. Obergeschoss"),
    (re.compile(r"\b(\d{1,2})\s*(?:ER|E|EME)\s+ETAGE\b"), "fr", "{n}e étage"),
]
_ORDINALS = {"FIRST": 1, "SECOND": 2, "THIRD": 3, "FOURTH": 4, "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
             "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10}
_LEVEL_MARK_IN_BRACKETS_RE = re.compile(r"\([^()]*\d[^()]*\)")


@dataclass
class LevelWord:
    order: Optional[int]          # None = the top level (attic)
    kind: str                     # basement | floor | attic
    label: str
    word: str
    language: str
    typical: bool = False         # a typical floor plan: it stands for every upper floor without a plan of its own


def level_of(text: str) -> Optional[LevelWord]:
    """The level a title names: basement -1, ground 0, ``n. KAT`` / ``n-th FLOOR`` / ``n. OG`` n, attic = the top.
    2 Nov 2026 (real13: ``1.(+5.20 KOTU) KAT PLANI``, ``TERAS.(+13.30 KOTU) KAT PLANI``): a level mark in brackets
    inside the title is left out before the words are read."""
    folded = " ".join(_LEVEL_MARK_IN_BRACKETS_RE.sub(" ", _fold(text)).split())
    for order, kind, label, pattern, lang in _LEVEL_RE:
        if kind != "roof_terrace":                                     # the roof terrace floor first (the top)
            continue
        m = pattern.search(folded)
        if m:
            return LevelWord(order=None, kind=kind, label=label, word=m.group(0), language=lang)
    for pattern, lang, label in _NTH_BASEMENT_RE:
        m = pattern.search(folded)
        if m and int(m.group(1)) > 0:
            n = int(m.group(1))
            return LevelWord(order=-n, kind="basement", label=label.format(n=n), word=m.group(0), language=lang)
    m = _NTH_NORMAL_RE.search(folded)
    if m and int(m.group(1)) > 0:
        n = int(m.group(1))
        return LevelWord(order=n, kind="floor", label=f"{n}. Normal Kat", word=m.group(0), language="tr")
    for pattern, lang, label in _TYPICAL_RE:
        m = pattern.search(folded)
        if m:
            return LevelWord(order=1, kind="floor", label=label, word=m.group(0), language=lang, typical=True)
    for order, kind, label, pattern, lang in _LEVEL_RE:
        if kind == "roof_terrace":
            continue
        m = pattern.search(folded)
        if m:
            return LevelWord(order=None if order == "top" else int(order), kind=kind, label=label, word=m.group(0),
                             language=lang)
    for pattern, lang, label in _NTH_RE:
        m = pattern.search(folded)
        if m:
            g = m.group(1)
            n = _ORDINALS[g] if g in _ORDINALS else int(g)
            if n == 0:
                continue
            text_label = label.format(n=n, w=g.capitalize())
            if lang == "en" and label.startswith("{n}"):
                text_label = f"{n}{_suffix(n)} Floor"
            return LevelWord(order=n, kind="floor", label=text_label, word=m.group(0), language=lang)
    return None


def _suffix(n: int) -> str:
    if 10 <= n % 100 <= 20:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def _fold(text: str) -> str:
    return " ".join(B.fold_ascii(text).upper().split())


ASSUMED_GROUND = ("Ground floor", 0)
FLOOR_STEP_M = 2.0                  # untitled plans ordered by floor marks: marks >= one storey apart
GROUND_BAND_M = (-1.2, 1.5)         # the lowest floor mark in this band (metres from ±0.00) is the ground floor


def floor_mark(region) -> Optional[float]:
    """The floor level a plan's level marks give (real06: ``+0,50`` three times and ``±0,00`` outside -> 0.50): the
    most frequent value among the marks that point at a mark symbol, the highest one on a tie; None without one."""
    from wenart.sheets import units_check as UC

    segs = UC.segments(region.strokes())
    values = [round(rec["value"], 2) for t, rec in UC.mark_records(region.texts) if UC.mark_point(t, segs)]
    if not values:
        return None
    counts = Counter(values)
    return max(counts, key=lambda v: (counts[v], v))


def _by_floor_marks(untitled: list, warnings: list) -> bool:
    """Levels of untitled plans from their floor marks (no plan titled); False (nothing set) when a plan has no
    floor mark, two marks are less than a storey apart, or no mark is near ±0.00."""
    marks = {id(r): floor_mark(r) for r in untitled}
    if any(m is None for m in marks.values()):
        return False
    ordered = sorted(untitled, key=lambda r: marks[id(r)])
    values = [marks[id(r)] for r in ordered]
    if any(b - a < FLOOR_STEP_M for a, b in zip(values, values[1:])):
        return False
    ground = next((i for i, v in enumerate(values) if GROUND_BAND_M[0] <= v <= GROUND_BAND_M[1]), None)
    if ground is None:
        return False
    for i, r in enumerate(ordered):
        order = i - ground
        label = ASSUMED_GROUND[0] if order == 0 else f"Level {order}"
        r.level = {"order": order, "label": label, "id": B.level_id(order), "kind": _kind("floor", order),
                   "method": "assumed", "evidence": [dict(e) for e in r.evidence[:1]]}
        warnings.append(f"{r.file} {r.id}: plan without a level title: level {B.level_id(order)} '{label}' inferred "
                        f"from its floor mark {values[i]:+.2f} m ({len(ordered)} untitled plans ordered by their "
                        f"floor marks)")
    return True


def storey_words(regions: list) -> dict[int, str]:
    """The storeys the sections name (real10: ``2. BODRUM KAT`` ... ``ZEMİN KAT``, ``1. NORMAL KAT`` ... ``6. NORMAL
    KAT`` beside the slab bands): order -> label, from the level words of the regions' texts (a typical-floor word
    or the top floor names no storey of its own)."""
    out: dict[int, str] = {}
    for r in regions:
        for t in getattr(r, "texts", None) or []:
            lw = level_of(t.text)
            if lw is not None and lw.order is not None and not lw.typical:
                out.setdefault(lw.order, lw.label)
    return dict(sorted(out.items()))


def roof_terrace_heights(regions: list) -> Optional[dict]:
    """real10 (1 Nov 2026): the roof terrace floor's heights from a section's level marks. Each storey label of the
    section (``6. NORMAL KAT``) is paired with the level mark beside it (the nearest in height, within three text
    heights); the terrace floor is one storey step (their median) above the top labelled storey, at the mark there
    (within 0.3 m; real10: +23.50 above +20.50); the parapet top is the mark nearest 1 m above it (0.5-1.5 m: +24.40,
    0.90 m), the stair house's roof the mark nearest a storey above it (2.4-4.0 m: +26.50, 3.00 m). Window heads and
    other marks between storeys are not storeys. ``{"floor_mark", "parapet_height", "house_height", "storey_marks",
    "marks"}`` or None when no section pairs two storeys with marks."""
    import statistics as _st

    from wenart.sheets import units_check as UC

    storey: dict[int, float] = {}
    values: set[float] = set()
    for r in regions:
        texts = getattr(r, "texts", None) or []
        marks = [(t, round(v, 2)) for t, v in UC.mark_texts(texts)]
        values.update(v for _, v in marks)
        for t in texts:
            lw = level_of(t.text)
            if lw is None or lw.order is None or lw.typical or not marks:
                continue
            reach = 3.0 * max(getattr(t, "height", 0.0) or 0.0, 1e-9)
            near = min(marks, key=lambda m: abs(m[0].point[1] - t.point[1]))
            if abs(near[0].point[1] - t.point[1]) <= reach:
                storey.setdefault(lw.order, near[1])
    if len(storey) < 2:
        return None
    orders = sorted(storey)
    steps = [(storey[b] - storey[a]) / (b - a) for a, b in zip(orders, orders[1:]) if storey[b] > storey[a]]
    if not steps:
        return None
    step = _st.median(steps)
    guess = storey[orders[-1]] + step
    marks_sorted = sorted(values)
    floor = min(marks_sorted, key=lambda v: abs(v - guess))
    if abs(floor - guess) > 0.3:
        floor = round(guess, 2)

    def nearest(target: float, lo: float, hi: float) -> Optional[float]:
        cands = [v - floor for v in marks_sorted if lo <= v - floor <= hi]
        return round(min(cands, key=lambda d: abs(d - target)), 3) if cands else None

    return {"floor_mark": floor, "parapet_height": nearest(1.0, 0.5, 1.5), "house_height": nearest(step, 2.4, 4.0),
            "storey_marks": {str(k): v for k, v in sorted(storey.items())}, "marks": marks_sorted}


def typical_orders(own: set, storeys: dict[int, str]) -> tuple[list[int], list[int], str]:
    """``(orders, inferred, how)``: the levels a typical floor plan stands for. With storeys named on the sections:
    every one at or above the ground floor without a plan of its own, in one run from the lowest (the ground floor
    among them only when it has no plan: inferred); without them one level, the ground floor when it has no plan,
    else the first floor (how = ``assumed``)."""
    if storeys:
        free = [o for o in storeys if o >= 0 and o not in own]
        run = []
        for o in free:
            if run and o != run[-1] + 1:
                break
            run.append(o)
        if run:
            inferred = [o for o in run if o == 0]
            return run, inferred, "section"
    first = 0 if 0 not in own else 1
    return [first], [first] if first == 0 else [], "assumed"


_ELEVATION_RE = re.compile(r"\(\s*([+\-±]?\s*\d{1,3}[.,]\d{1,3})(?:\s*[-/]\s*([+\-±]?\s*\d{1,3}[.,]\d{1,3}))?"
                           r"\s*(?:KOTU?|KOT|M)?\s*\)")


STOREY_M = 3.0                      # a typical plan's elevation range: its storeys at about this height


def title_elevations(text: Optional[str]) -> Optional[tuple[float, float]]:
    """The floor elevation(s) a title gives in brackets: ``(8,50)`` -> (8.5, 8.5), ``(2,50-5,50)`` -> (2.5, 5.5),
    ``(+5.20 KOTU)`` -> (5.2, 5.2); None without one."""
    m = _ELEVATION_RE.search(_fold(text or ""))
    if not m:
        return None
    vals = [float(g.replace(" ", "").replace("±", "").replace(",", ".")) for g in m.groups() if g]
    return min(vals), max(vals)


_BARE_ELEVATION_RE = re.compile(r"^\(?\s*([+\-±]?\s*\d{1,3}[.,]\d{1,3})(?:\s*[-/]\s*([+\-±]?\s*\d{1,3}[.,]\d{1,3}))?"
                                r"\s*\)?$")


def region_elevations(r) -> Optional[tuple[float, float]]:
    """A plan's floor elevation(s) from its title (``title_elevations``), else from a bare elevation text just right
    of the title (real09: ``( 8,50 )`` written as three texts beside ``DUBLEKS KAT PLANI``): within 8 title heights to
    the right of its end and 2 heights up or down."""
    if not r.title:
        return None
    el = title_elevations(r.title["text"])
    if el is not None:
        return el
    tb = r.title.get("box")
    if not tb:
        return None
    h = max(tb[3] - tb[1], 1e-9)
    cy = (tb[1] + tb[3]) / 2.0
    vals = []
    for t in getattr(r, "texts", []) or []:
        if not (tb[2] - h <= t.box[0] <= tb[2] + 8.0 * h) or abs((t.box[1] + t.box[3]) / 2.0 - cy) > 2.0 * h:
            continue
        m = _BARE_ELEVATION_RE.match(t.text.strip())
        if m:
            vals.extend(float(g.replace(" ", "").replace("±", "").replace(",", ".")) for g in m.groups() if g)
    return (min(vals), max(vals)) if vals else None


def _by_title_elevation(plans: list, words: dict, warnings: Optional[list] = None) -> None:
    """2 Nov 2026 (real09: '1.BODRUM KAT PLANI (0,00)', 'NORMAL KAT PLANI (2,50-5,50)', 'DUBLEKS KAT PLANI (8,50)',
    'ÇATI KAT PLANI (11,50)'): a plan whose title names no level but gives its floor elevation in brackets takes the
    storey right above the titled plan whose elevation lies below it (a typical plan: its highest storey), when the
    titled plan above it (if any) lies higher. Its label is its own title's name ('Dubleks Kat')."""
    titled = []
    for r in plans:
        lw, el = words[id(r)], region_elevations(r)
        if lw is not None and el is not None:
            titled.append((el, r, lw))
    if not titled:
        return
    for r in plans:
        if words[id(r)] is not None or not r.title:
            continue
        el = region_elevations(r)
        if el is None:
            continue
        below = [(e, x, lw) for e, x, lw in titled if e[1] < el[0] and lw.order is not None]
        above = [(e, x, lw) for e, x, lw in titled if e[0] > el[1]]
        if not below:
            continue
        e_b, x_b, lw_b = max(below, key=lambda t: t[0][1])
        span = max(1, round((e_b[1] - e_b[0]) / STOREY_M) + 1) if lw_b.typical else 1   # a typical plan's storeys
        order = lw_b.order + span if lw_b.typical else lw_b.order + 1
        if any(lw.order is not None and lw.order <= order for e, x, lw in above):
            continue
        name = re.sub(r"\(.*?\)|O\s*:\s*1\s*/\s*\d+|\bPLANI?\b", " ", _fold(r.title["text"]))
        label = " ".join(w.capitalize() for w in name.split()) or f"{order}. Kat"
        words[id(r)] = LevelWord(order=order, kind="floor", label=label, word=r.title["text"].strip(),
                                 language="tr")
        if warnings is not None:
            warnings.append(f"{getattr(r, 'file', '')} {getattr(r, 'id', '')}: plan without a level word: level "
                            f"{B.level_id(order)} '{label}' inferred from its title elevation {el[0]:+.2f} m (the storey "
                            f"above '{x_b.title['text'].strip()}' at {e_b[1]:+.2f} m)")


def assign_levels(plans: list, needs_review: list, warnings: list,
                  storeys: Optional[dict[int, str]] = None) -> None:
    words = {}
    for r in plans:
        lw = level_of(r.title["text"]) if r.title else None
        words[id(r)] = lw
    _by_title_elevation(plans, words, warnings)
    storeys = storeys or {}
    own = {lw.order for lw in words.values() if lw is not None and lw.order is not None and not lw.typical}
    typical = {}
    for r in plans:
        lw = words[id(r)]
        if lw is not None and lw.typical:
            typical[id(r)] = typical_orders(own, storeys)
            own |= set(typical[id(r)][0])
    orders = sorted(own)
    top = max(max(orders) + 1, 1) if orders else 0
    untitled = [r for r in plans if words[id(r)] is None]
    for r in plans:
        lw = words[id(r)]
        if lw is None:
            continue
        ev = [dict(r.evidence[0])] if r.evidence else []
        if lw.typical:
            run, inferred, how = typical[id(r)]
            labels = [storeys.get(o) or ("Zemin Kat" if o == 0 else f"{o}. {lw.label}") for o in run]
            r.level = {"order": run[0], "label": labels[0], "id": B.level_id(run[0]), "kind": "floor",
                       "method": "title", "evidence": ev,
                       "typical": {"label": lw.label, "orders": run, "ids": [B.level_id(o) for o in run],
                                   "labels": labels, "inferred": [B.level_id(o) for o in inferred], "how": how}}
            text = (f"{r.file} {r.id}: typical floor plan '{r.title['text'].strip()}' stands for "
                    f"{len(run)} level(s) {', '.join(f'{B.level_id(o)} {lab}' for o, lab in zip(run, labels))}"
                    + (" (the storeys the sections name)" if how == "section" else
                       " (no section names the storeys: one level assumed)"))
            if inferred:
                text += (f"; {', '.join(B.level_id(o) for o in inferred)} has no plan of its own: the typical plan "
                         f"is used (inferred)")
            warnings.append(text)
            continue
        order = top if lw.order is None else lw.order
        r.level = {"order": order, "label": lw.label, "id": B.level_id(order), "kind": _kind(lw.kind, order),
                   "method": "title", "evidence": ev}
        if lw.kind == "roof_terrace":
            r.level["roof_terrace"] = True
    if not untitled:
        return
    titled = sorted({r.level["order"] for r in plans if r.level})
    if not titled and len(untitled) == 1:
        r = untitled[0]
        r.level = {"order": 0, "label": ASSUMED_GROUND[0], "id": "L0", "kind": "floor", "method": "assumed",
                   "evidence": [dict(e) for e in r.evidence[:1]]}
        warnings.append(f"{r.file} {r.id}: plan without a level title, the project's only plan: level L0 "
                        f"'{ASSUMED_GROUND[0]}' assumed")
        return
    if not titled and len(untitled) >= 2 and _by_floor_marks(untitled, warnings):
        return
    free = [o for o in range(titled[0], titled[-1] + 1) if o not in titled] if titled else []
    if len(untitled) == 1 and len(free) == 1:
        r = untitled[0]
        order = free[0]
        r.level = {"order": order, "label": f"Level {order}", "id": B.level_id(order), "kind": _kind("floor", order),
                   "method": "assumed", "evidence": [dict(e) for e in r.evidence[:1]]}
        warnings.append(f"{r.file} {r.id}: plan without a level title in the only free level slot: level "
                        f"{B.level_id(order)} assumed")
        return
    for r in untitled:
        r.use, r.ignored_reason = "ignored", "plan without a level title (its level cannot be told)"
        needs_review.append({"region": r.id, "file": r.file,
                             "reason": f"{r.file} {r.id}: plan without a level title; {len(untitled)} untitled plans, "
                                       f"{len(free)} free level slot(s)"})


def _kind(kind: str, order: int) -> str:
    if kind == "attic":
        return "attic"
    return "basement" if order < 0 else "floor"
