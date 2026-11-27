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
"""
from __future__ import annotations

import math
import re
from typing import Optional

from wenart import building as B

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


def parse(text: str) -> Optional[dict]:
    """``{"risers", "riser_m", "rise_m", "going_m", "text"}`` of a stair formula text, or None (pure). A text holding
    no 'x' between two numbers, a riser outside ``RISER_M``, a count outside ``RISERS`` or an H that N x R does not give
    is no formula. ``rise_m`` is the H written (None when not written)."""
    folded = B.fold_ascii(str(text or "")).upper()
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
    return {"risers": n, "riser_m": round(r, 4), "rise_m": round(h, 3) if h is not None else None,
            "going_m": round(g, 3) if g is not None else None, "text": str(text).strip()}


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
COMMON_RISER_MAX_M = 0.18        # R24: a common stair's riser over this is a finding
GOING_SPREAD_M = 0.05            # ... and flights whose goings differ by more than this


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
    """The goings of a stair's straight flights (their tread spacing, page metres; pure)."""
    out = []
    for f in data.get("flights") or []:
        g = f.get("spacing") if isinstance(f, dict) else None
        if isinstance(g, (int, float)) and g > 0:
            out.append(float(g))
    return out


def attach(pieces: list, texts: list, notes: list) -> int:
    """Every stair piece that holds or touches a stair formula text (``FORMULA_REACH_M``) takes it, in place:
    ``details["stair"]["formula"]`` (risers, riser, rise, going, text, entity); when the stair's drawn risers are the
    formula's N, its riser height is the formula's R (``riser_m``, ``riser_source`` 'documented: ...'), else the treads
    are kept and the difference noted. Risers over ``COMMON_RISER_MAX_M`` and flights whose goings differ by more than
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
    """R24 findings of a stair reading with its formula (pure): a common stair's riser over ``COMMON_RISER_MAX_M``,
    flights whose goings differ by more than ``GOING_SPREAD_M``, and drawn risers that are not the formula's count."""
    out = []
    f = data.get("formula") or {}
    riser = f.get("riser_m") or data.get("riser_m")
    if isinstance(riser, (int, float)) and riser > COMMON_RISER_MAX_M:
        out.append(f"risers of {float(riser):.3f} m over {COMMON_RISER_MAX_M:.2f} m (a steep stair)")
    gs = goings(data)
    if len(gs) >= 2 and max(gs) - min(gs) > GOING_SPREAD_M:
        out.append(f"the flights' goings differ by {max(gs) - min(gs):.3f} m ({', '.join(f'{g:.3f}' for g in gs)})")
    if f and f.get("drawn_risers") is not None and int(f["drawn_risers"]) != int(f.get("risers") or 0):
        out.append(f"the stair draws {f['drawn_risers']} risers, its formula '{f.get('text')}' {f.get('risers')}")
    return out
