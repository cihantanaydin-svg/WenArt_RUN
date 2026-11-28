"""Stair formula texts (27 Nov 2026, audit fix round 4, R24).

What: ``parse(text) -> dict | None`` reads a stair formula a plan writes inside or next to a stair: the riser count N
and the riser height R, often the storey height H and the going G (``(19X17.36Rh=330/27)``, ``17X17.64Rh=300/27``,
``(17x 17.65 / 28)``, ``16x18/28``, ``19 x 0.1736 = 3.30``). ``near(texts, points, reach)`` gives the formula written
nearest a stair's numbers or footprint.

Why: real drawings print the riser formula in every stair; no code read it, so a stair whose first tread number stood
on the landing farther than a tread from the next lost its first risers and was built with 16 risers of 0.206 m
instead of the drawn 19 x 0.1736 m.

How: pure text parsing, defensively: N 2-40, R 0.10-0.25 m (written in cm when over 1, in m under 1), G 0.18-0.45 m
(cm when over 1), H in cm when over 20; when H is written N x R must give it within ``SELF_TOL`` (else the text is
no formula). The caller checks N x R against the storey height (``storey_ok``, ``STOREY_TOL``).

27 Nov 2026 (audit fix round 4b, defect 10: '20x20 SERAMİK', '15X15', 'S1 25x25', 'ŞAFT 20x20', '10x10' and '2x0.15'
parsed as formulas, and a '15X15' label 1.5 m from a stair's '1' cut its 18-step chain to 15): ``FORMULA_RE`` still
finds the 'N x R' shape, but ``parse`` takes it for a formula only with a formula's context (``formula_context``): a
written H that N x R gives ('Rh=330', '= 3.30'), or a written going in the going range ('/27'), or brackets round it
with N x R a storey's rise (``BRACKET_RISE_M``) and N not R's own number (a square size '(20x20)' is a size); never
with a size, material or element word (``SIZE_WORD_RE``: SERAMİK, ŞAFT, KOLON, DİKME, KÜPEŞTE, PARÇA, cm, a column
label 'S1' ...). ``is_formula(text)`` says the same as ``parse(text) is not None`` (the size-tag parsers use it).
"""
from __future__ import annotations

import math
import re
from typing import Optional

from wenart.textfold import fold_ascii   # 28 Nov 2026 (round 5a fix-up, TAGS-2): never wenart.building (jsonschema), so
#                                          the size-tag grammar stays importable in Blender's Python

SELF_TOL = 0.03                  # N x R within 3 % of the H the text itself writes
STOREY_TOL = 0.03                # N x R within 3 % of the storey height (R24)
RISERS = (2, 40)
RISER_M = (0.10, 0.25)
GOING_M = (0.18, 0.45)
NUMBER = r"(\d{1,3}(?:[.,]\d{1,4})?)"
# N x R [Rh|H|h] [= H] [/ G]: the separators vary ('x', 'X', '*', '×'); spaces anywhere
FORMULA_RE = re.compile(r"(?<![\d.,])(\d{1,2})\s*[xX*×]\s*" + NUMBER
                        + r"(?:\s*(?:R\s*H|RH|H)?\s*=\s*" + NUMBER + r")?"
                        + r"(?:\s*/\s*" + NUMBER + r")?(?![\d.,])")


def _num(s: Optional[str]) -> Optional[float]:
    return float(s.replace(",", ".")) if s else None


def _metres(v: Optional[float], cm_over: float) -> Optional[float]:
    """A length written in cm when over ``cm_over``, else in metres."""
    if v is None:
        return None
    return v / 100.0 if v > cm_over else v


BRACKET_RISE_M = (2.0, 6.0)      # a bracketed 'N x R' with no H and no going is a formula only for a storey's rise
# a size, material or element word: the 'N x R' beside it is a size (tiles, shafts, columns, posts, rails, profiles)
SIZE_WORD_RE = re.compile(r"\b(?:SERAMIK|FAYANS|MERMER|GRANIT|PARKE|KARO|TAS|SAFT|BACA|KOLON|SUTUN|DIKME|KUPESTE|"
                          r"PARCA(?:SI)?|PROFIL|KUTU|LAMA|BORU|KIRIS|HATIL|PERDE|DOSEME|PANO|AYDINLIK|MENFEZ|IZGARA|"
                          r"LAMBA|SPOT|ASPIRATOR|TILE|SHAFT|COLUMN|POST|BEAM|PIPE|DUCT)\b"
                          r"|(?<![A-Z0-9])[SK]\s*\d{1,3}\b")


def formula_context(folded: str, m, n: int, r: float, h: Optional[float], g: Optional[float]) -> bool:
    """Whether an 'N x R' match ``m`` of the folded text ``folded`` stands in a stair formula's context (pure): a written
    H that N x R gives, a written going in ``GOING_M``, or brackets round it with N x R in ``BRACKET_RISE_M`` and N not
    R's own number in cm; never beside a size or material word (``SIZE_WORD_RE``)."""
    rest = (folded[:m.start()] + " " + folded[m.end():])
    if SIZE_WORD_RE.search(rest):
        return False
    if h is not None or g is not None:
        return True
    before, after = folded[:m.start()].rstrip(), folded[m.end():].lstrip()
    bracketed = before.endswith("(") and after.startswith(")")
    square = abs(n - r * 100.0) < 0.5
    return bracketed and BRACKET_RISE_M[0] <= n * r <= BRACKET_RISE_M[1] and not square


def parse(text: str) -> Optional[dict]:
    """``{"risers", "riser_m", "rise_m", "going_m", "text"}`` of a stair formula text, or None (pure). A text holding
    no 'x' between two numbers, a riser outside ``RISER_M``, a count outside ``RISERS``, an H that N x R does not give
    or no formula context (``formula_context``: '20x20 SERAMİK', '15X15', '2x0.15' are sizes) is no formula.
    ``rise_m`` is the H written (None when not written)."""
    folded = fold_ascii(str(text or "")).upper()
    m = FORMULA_RE.search(folded)
    if not m:
        return None
    n = int(m.group(1))
    r = _metres(_num(m.group(2)), 1.0)
    h = _metres(_num(m.group(3)), 20.0)
    g = _metres(_num(m.group(4)), 1.0)
    if not RISERS[0] <= n <= RISERS[1] or r is None or not RISER_M[0] <= r <= RISER_M[1]:
        return None
    if g is not None and not GOING_M[0] <= g <= GOING_M[1]:
        g = None
    if h is not None and abs(n * r - h) > SELF_TOL * h:
        return None
    if not formula_context(folded, m, n, r, h, g):
        return None
    return {"risers": n, "riser_m": round(r, 4), "rise_m": round(h, 3) if h is not None else None,
            "going_m": round(g, 3) if g is not None else None, "text": str(text).strip()}


def is_formula(text: str) -> bool:
    """True when ``text`` is a stair formula (``parse``; pure)."""
    return parse(text) is not None


def storey_ok(formula: dict, storey_m: Optional[float]) -> Optional[bool]:
    """Whether the formula's N x R climbs ``storey_m`` within ``STOREY_TOL`` (None without a storey height)."""
    if not storey_m or storey_m <= 0:
        return None
    return abs(formula["risers"] * formula["riser_m"] - float(storey_m)) <= STOREY_TOL * float(storey_m)


def near(texts: list, points: list, reach: float) -> Optional[tuple[dict, object]]:
    """The formula text nearest the stair's ``points`` (its numbers or footprint corners, page metres) within
    ``reach``: ``(formula, text)`` or None (pure)."""
    best = None
    for t in texts or []:
        f = parse(getattr(t, "text", ""))
        if f is None:
            continue
        p = ((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0)
        d = min((math.dist(p, q) for q in points), default=math.inf)
        if d <= reach and (best is None or d < best[0]):
            best = (d, f, t)
    return (best[1], best[2]) if best else None


FORMULA_REACH_M = 1.0            # a formula text stands inside the stair's footprint or this close to it
# 27 Nov 2026 (audit fix round 4b, item 3): a common stair's steep riser is checked against the regulation's limits
# (``wenart.reading_check.regulations.riser_limit``: 0.18 m with a lift, 0.16 m without), on common stairs only, by
# ``wenart.levels.model._stair_formulas``; this module holds no riser limit of its own
GOING_SPREAD_M = 0.05            # flights whose goings differ by more than this (no going written)
GOING_MIN_LINES = 3              # ... counted on flights of at least this many tread lines (a landing's lines are none)


def _footprint(piece):
    """The stair piece's footprint polygon (page metres), or None."""
    from shapely.geometry import Polygon
    try:
        cx, cy = piece.center
        w, d = piece.size
        a = math.radians(float(piece.rotation_deg or 0.0))
    except (TypeError, ValueError):
        return None
    ca, sa = math.cos(a), math.sin(a)
    return Polygon([(cx + ca * u - sa * v, cy + sa * u + ca * v)
                    for u, v in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2))])


def drawn_risers(data: dict) -> int:
    """The risers a stair reading builds: its flights' lines and its winders (pure)."""
    return sum(int(f.get("lines") or 0) for f in data.get("flights") or [] if isinstance(f, dict)) \
        + sum(int(w or 0) for w in data.get("turn_winders") or []) + (0 if data.get("turn_winders")
                                                                     else int(data.get("winders") or 0))


def goings(data: dict) -> list:
    """The goings of a stair's straight flights of at least ``GOING_MIN_LINES`` tread lines (their tread spacing, page
    metres; pure)."""
    out = []
    for f in data.get("flights") or []:
        g = f.get("spacing") if isinstance(f, dict) else None
        if isinstance(g, (int, float)) and g > 0 and int(f.get("lines") or 0) >= GOING_MIN_LINES:
            out.append(float(g))
    return out


def attach(pieces: list, texts: list, notes: list) -> int:
    """Every stair piece that holds or touches a stair formula text (``FORMULA_REACH_M``) takes it, in place:
    ``details["stair"]["formula"]`` (risers, riser, rise, going, text, entity); when the stair's drawn risers are the
    formula's N, its riser height is the formula's R (``riser_m``, ``riser_source`` 'documented: ...'), else the treads
    are kept and the difference noted. Flights whose goings differ by more than
    ``GOING_SPREAD_M`` are noted as findings (``formula_findings``). Returns the stairs that took a formula."""
    from shapely.geometry import Point
    n = 0
    forms = []
    for t in texts or []:
        f = parse(getattr(t, "text", ""))
        if f is not None:
            forms.append((f, t, Point((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0)))
    if not forms:
        return 0
    used: set = set()
    for p in pieces:
        if getattr(p, "type", None) != "stair":
            continue
        data = (p.details or {}).get("stair")
        fp = _footprint(p)
        if data is None or fp is None:
            continue
        near = sorted(((fp.distance(q), k) for k, (_f, _t, q) in enumerate(forms) if k not in used
                       and fp.distance(q) <= FORMULA_REACH_M), key=lambda x: x[0])
        if not near:
            continue
        k = near[0][1]
        f, t, _q = forms[k]
        used.add(k)
        rec = dict(f)
        rec["entity"] = getattr(t, "id", None) or (t.evidence[0].get("entity") if isinstance(getattr(t, "evidence", None), list)
                                                   and t.evidence and isinstance(t.evidence[0], dict) else None)
        risers = drawn_risers(data)
        rec["drawn_risers"] = risers
        if risers == f["risers"] and not data.get("riser_m"):
            data["riser_m"] = f["riser_m"]
            data["riser_source"] = f"documented: the stair formula '{f['text']}'"
            rec["used"] = "riser"
        else:
            rec["used"] = "count_differs" if risers != f["risers"] else "kept"
        data["formula"] = rec
        n += 1
        notes.append(f"stair {getattr(p, 'entity', None) or ''}: formula '{f['text']}' = {f['risers']} x "
                     f"{f['riser_m']:.4f} m" + (f" = {f['rise_m']:.2f} m" if f.get("rise_m") else "")
                     + (": the riser height" if rec["used"] == "riser" else
                        f"; the stair draws {risers} risers (its treads kept, the formula listed)"))
    return n


def formula_findings(data: dict) -> list[str]:
    """R24 findings of a stair reading with its formula (pure): flights whose goings differ by more than
    ``GOING_SPREAD_M`` when the formula writes no going, and drawn risers that are not the formula's count.
    27 Nov 2026 (audit fix round 4b, defect 13: real17's stairs, every one written '/27', had five 'goings differ'
    findings from the reader's number spacing, 0.241 / 0.404 / 0.304): a written going wins over the measured spacing
    (no goings finding); the steep-riser finding is the regulation's, on common stairs only
    (``wenart.levels.model._stair_formulas``)."""
    out = []
    f = data.get("formula") or {}
    gs = goings(data)
    if not f.get("going_m") and len(gs) >= 2 and max(gs) - min(gs) > GOING_SPREAD_M:
        out.append(f"the flights' goings differ by {max(gs) - min(gs):.3f} m ({', '.join(f'{g:.3f}' for g in gs)})")
    if f and f.get("drawn_risers") is not None and int(f["drawn_risers"]) != int(f.get("risers") or 0):
        out.append(f"the stair draws {f['drawn_risers']} risers, its formula '{f.get('text')}' {f.get('risers')}")
    return out
