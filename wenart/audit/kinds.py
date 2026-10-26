"""The problem kinds (26 Oct 2026, user: "don't only fix the problem I gave it to you, also develop a system to
understand the problem kinds and prevent it happening").

What: ``KINDS`` names the general kinds of problem the project has met (each with what it is, the stage boundary where
it arises, and the guards that catch it: the audit lines and checks that prevent it from passing silently);
``kind_of(finding)`` gives a finding's kind from its line and check (``CHECK_KIND``, ``LINE_KIND``; a finding may carry
its own ``kind``, e.g. from the AI auditor); ``FINDING_KEYS`` is the one format every audit line writes.

Why: a problem the user names is one case of a kind (the veranda: something the documents hold that a stage dropped);
the fix of the case is not enough. With every finding labelled by kind, the report shows which kinds the run still
has, where they arise, and which guard caught them; the problem log (``report.update_log``) counts them across runs,
so a kind that keeps coming back gets its own guard (a rule, a check, a lesson).
"""
from __future__ import annotations

from typing import Optional

FINDING_KEYS = ("line", "check", "kind", "severity", "target", "message", "evidence", "owner", "fix")
SEVERITIES = ("critical", "major", "minor", "info")
SEVERITY_RANK = {"info": 0, "minor": 1, "major": 2, "critical": 3}

KINDS = {
    "lost": {"what": "something the documents or an earlier stage hold is missing from the model (a labelled "
                     "veranda, drawn site symbols, a room, an opening, a piece)",
             "arises": "any stage boundary: reading -> building, fit, layout, build, render",
             "guards": ["ledger (A*)", "conservation (C*)", "plan_vs_model (B*)", "process (P*)"]},
    "untyped": {"what": "a drawn element no rule or model typed, so nothing builds it ('other', 'unknown')",
                "arises": "reading",
                "guards": ["conservation C4", "ledger", "the reading's AI questions"]},
    "misread": {"what": "the reading typed, sized or placed something wrong (armchairs read as tables with chairs, a "
                        "vanity read as a kitchen counter)",
                "arises": "reading",
                "guards": ["plan_vs_model (B*)", "the room-sense rules (G*, R*)", "model review M7"]},
    "no_sense": {"what": "the model makes no sense to a visitor (a door into the air, a basin at knee height, stairs "
                         "running into each other, a railing across a door)",
                 "arises": "architect, build",
                 "guards": ["sense (N*: every room reached, no bathroom as a corridor, every level reached)",
                            "model review (M*)", "architect rules", "visitor checks (Q*)"]},
    "taste": {"what": "the house does not look designed (pieces that do not match, plain or dated rooms, a garage "
                      "door look)",
              "arises": "fit, decor, opening models",
              "guards": ["judge (J*)", "visitor checks Q5, Q7", "the fit's matched sets"]},
    "geometry": {"what": "pieces through walls or each other, blocked doors and windows, no walkway",
                 "arises": "layout, agent",
                 "guards": ["code critic (F*, G*)", "architect F-rules"]},
    "stale": {"what": "a stage acted on an older state than the one built (the critic reading doors the architect had "
                      "made windows)",
              "arises": "agent loop, critics",
              "guards": ["the critics read the building as built", "conservation C2",
                         "consistency (Y*: the critic and the architect's rule disagree about one element)"]},
    "silent": {"what": "a stage noted a problem in a warning and nothing acted on it",
               "arises": "any stage",
               "guards": ["process P2 (warnings that say something was left out)"]},
    "process": {"what": "the run itself: a stage failed or was skipped, a test failed, time was left unused, a "
                        "question "
                        "stayed unanswered",
                "arises": "scheduler",
                "guards": ["process (P*)"]},
    "other": {"what": "not classified yet: a new kind to name", "arises": "-", "guards": []},
}

# A finding's kind from its check (exact id first, then its letter prefix)
CHECK_KIND = {
    # the model review
    "M1": "no_sense", "M2": "no_sense", "M3": "no_sense", "M4": "no_sense", "M5": "no_sense", "M6": "taste",
    "M7": "misread", "M8": "no_sense",
    # the visitor checks and the looks
    "Q1": "no_sense", "Q2": "no_sense", "Q3": "no_sense", "Q4": "misread", "Q5": "taste", "Q6": "geometry",
    "Q7": "taste", "Q8": "no_sense", "Q9": "no_sense", "D1": "geometry", "D2": "taste", "D3": "taste",
    # code critic
    "F7": "geometry", "F8": "geometry", "G11": "geometry", "G9": "misread", "G10": "misread",
    # conservation
    "C1": "lost", "C2": "lost", "C3": "lost", "C4": "untyped", "C5": "lost",
}
PREFIX_KIND = {"A": "lost", "B": "lost", "C": "lost", "P": "process", "J": "taste", "F": "geometry", "G": "geometry",
               "S": "taste", "L": "no_sense", "X": "no_sense", "V": "taste", "R": "misread", "W": "no_sense",
               "E": "no_sense", "O": "no_sense", "H": "no_sense", "K": "no_sense", "T": "no_sense"}
LINE_KIND = {"ledger": "lost", "source": "lost", "conservation": "lost", "process": "process",
             "plan_vs_model": "lost", "sense": "no_sense", "render": "lost", "consistency": "stale",
             "elevations": "lost", "judge": "taste", "model": "no_sense", "architect": "no_sense"}


def kind_of(finding: dict) -> str:
    """The kind of a finding (module docstring): its own ``kind`` when it names one of ``KINDS``, else by its check,
    its check's letter, its line; ``other`` when nothing says."""
    k = finding.get("kind")
    if k in KINDS:
        return k
    check = str(finding.get("check") or "")
    if check in CHECK_KIND:
        return CHECK_KIND[check]
    if finding.get("source") == "judge":
        return "taste"
    if check[:1] in PREFIX_KIND and check[1:2].isdigit():
        return PREFIX_KIND[check[:1]]
    return LINE_KIND.get(str(finding.get("line") or ""), "other")


def finding(line: str, check: str, severity: str, target, message: str, *, evidence: Optional[dict] = None,
            owner: Optional[str] = None, fix: Optional[str] = None, kind: Optional[str] = None) -> dict:
    """One audit finding in the common format (``FINDING_KEYS``), its kind filled in."""
    f = {"line": line, "check": check, "severity": severity, "target": target, "message": message,
         "evidence": dict(evidence or {}), "owner": owner, "fix": fix}
    f["kind"] = kind if kind in KINDS else kind_of(f)
    return f
