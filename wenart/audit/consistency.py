"""Argus, the consistency line: two checkers that disagree about one element (26 Oct 2026, Argus on real06: the code
critic called the drawn counter across the 2.9 m kitchen gap o_L0_001 a critical blocked door in every run, while the
architect's doorway rule F2 never looked at doorless gaps).

What: every critical or major finding of the code critic (the inspector's last ``code`` list) is put beside the
architect's rule for the same concern (``CONCERN``: a blocked opening F7 / G12 and the doorway and window rules F2 /
F3, clashing pieces F9 and F5, a room's set G9 / G10 and S4, walkways G11 and circulation C1, a door into the air X3
and the outside doors E1, the use zone F6 and F4). The element is the finding's target, or the opening its message
names for an opening concern.

- Y1 the architect's rule never asked about that element: a blind spot of the rule (the critic sees what the
  architect cannot fix);
- Y2 the architect's rule says the element is fine (asked, not open) while the critic finds it critical or major: the
  two measure the same thing differently.

Why: a problem one checker sees and the other cannot is never fixed: the architect has the fixes, the critic the
eyes. Each finding names the rule that needs the case (kind ``stale``, owner ``architect``, fix ``rule_needed``).
"""
from __future__ import annotations

import re
from typing import Optional

from wenart.audit import kinds as K

CONCERN = {"F7": ("F2", "F3"), "G12": ("F3",), "F9": ("F5",), "G9": ("S4",), "G10": ("S4",), "G11": ("C1",),
           "X3": ("E1",), "F6": ("F4",)}
OPENING_CHECKS = ("F7", "G12", "X3")
OPENING_RE = re.compile(r"\b((?:d|o|win|w)_L-?\d+[a-z]?_\d+)\b")


def _answers(architect: Optional[dict]) -> dict:
    """``{rule: {element: open?}}`` of the architect's record."""
    out: dict = {}
    for q in (architect or {}).get("questions") or []:
        for a in q.get("answers") or []:
            if a.get("element"):
                out.setdefault(q.get("id"), {})[str(a["element"])] = bool(a.get("open"))
    return out


def _element(f: dict) -> Optional[str]:
    if f.get("check") in OPENING_CHECKS:
        m = OPENING_RE.search(str(f.get("message") or ""))
        if m and not str(f.get("target") or "").startswith(("d_", "o_", "win_")):
            return m.group(1)
    return str(f.get("target")) if f.get("target") else None


def audit(inspector: Optional[dict], architect: Optional[dict]) -> dict:
    if not isinstance(inspector, dict) or not isinstance(architect, dict):
        return {"findings": [], "checked": {}, "note": "no inspector or architect record"}
    answers = _answers(architect)
    groups: dict = {}
    checked = 0
    for f in inspector.get("code") or []:
        rules = CONCERN.get(str(f.get("check")))
        if not rules or f.get("severity") not in ("critical", "major"):
            continue
        el = _element(f)
        if not el:
            continue
        checked += 1
        asked = [(r, answers.get(r, {})[el]) for r in rules if el in answers.get(r, {})]
        if asked and any(is_open for _r, is_open in asked):
            continue                                       # the architect sees it too (open)
        y = "Y2" if asked else "Y1"
        g = groups.setdefault((y, f.get("check"), rules), {"sev": f["severity"], "elements": [], "examples": []})
        if K.SEVERITY_RANK.get(f["severity"], 0) > K.SEVERITY_RANK.get(g["sev"], 0):
            g["sev"] = f["severity"]
        if el not in g["elements"]:
            g["elements"].append(el)
            g["examples"].append(str(f.get("message"))[:140])
    out = []
    for (y, check, rules), g in groups.items():
        els = g["elements"]
        what = (f"the architect's rule {' / '.join(rules)} never asked about them" if y == "Y1" else
                f"the architect's rule {' / '.join(rules)} says they are fine")
        out.append(K.finding("consistency", y, g["sev"], els[0] if len(els) == 1 else f"{check}: {len(els)} elements",
                             f"the critic finds {check} on {len(els)} element(s) ({', '.join(els[:6])}"
                             f"{' ...' if len(els) > 6 else ''}; e.g. {g['examples'][0]}) and {what}: the rule needs "
                             f"these cases", owner="architect", kind="stale", fix="rule_needed",
                             evidence={"critic": check, "rules": list(rules), "elements": els,
                                       "examples": g["examples"][:8]}))
    return {"findings": out, "checked": {"critic_findings": checked}}


def run(inp) -> dict:
    """The line for ``report.LINE_MODULES``."""
    return audit(inp.inspector, inp.architect)
