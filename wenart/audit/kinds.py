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
                 "guards": ["sense (N*: every room reached, no bathroom as a corridor, every level reached; a stair "
                            "joins the room it starts in and the room it arrives in)",
                            "model review (M*; M9: the walk from every stair into the rooms, to every door; M15: the "
                            "stair's handrails as one balustrade, no rail crossing another or stopping short)",
                            "architect rules (K4: a cut-off stair takes the reading that leads into its floors)",
                            "visitor checks (Q*)"]},
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
    # 28 Oct 2026 (user, five times since 25 Oct: "flying pillows", "still flying pillows all around", "More flying
    # pillows", "Light is flying in the air needs to be connected to ceiling"; "I did not like this bed"): a recurring
    # kind gets its guards
    "detached": {"what": "a piece is not attached to what holds it: a cushion standing free in front of its back or "
                         "over its seat, a pendant short of the ceiling with no cord, a cloth its host pokes through",
                 "arises": "decor, build",
                 "guards": ["scene check S5 (rest.measure_rest under, measure_back behind, measure_cloth through; "
                            "hang_gap to the ceiling)", "model review M14 (the rest and hang records)",
                            "rest.plan_decor (leans until it rests), furniture.hang_plan (cord and canopy)"]},
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
    "M7": "misread", "M8": "no_sense", "M10": "no_sense",
    # 27 Oct 2026: the roof against the roof plan (an outline assumed while drawn; a finding of a roof the model lost
    # carries its own kind, ``lost``)
    "M11": "misread",
    # 27 Oct 2026: the visitor's walk from every stair into its floors and to every door (model_review.stair_walks)
    "M9": "no_sense",
    "M12": "no_sense",
    # 28 Oct 2026: the kitchen as one designed kitchen (model_review.kitchen_design; its look findings carry "taste")
    "M13": "no_sense",
    # 28 Oct 2026: decor not attached to its support (model review M14, scene check S5)
    "M14": "detached", "S5": "detached",
    # 28 Oct 2026: the grading of the site and its outdoor floors (grading.review; a finding of a tread through a
    # planter carries its own kind, geometry, a crude look taste)
    "M15": "no_sense",
    # 28 Oct 2026 (user on real04's roof terrace: "makes no sense to have that table with the carpet outside"): an
    # indoor rug or model in an outdoor room (outdoor.review); (user: "More lights from the ceiling needed") a room with too
    # little ceiling light for its zones and floor (ceiling_lights.review)
    "M16": "no_sense", "M17": "taste",
    # 28 Oct 2026 (user on real04's stairs: "There should have been better indoor stair solutions"): the stair's
    # handrails as one designed balustrade (model_review.stair_rails_review): rails that cross, stop short, run through
    # a tread, a wall or the floor above, stand beside the floor guard above; a rail out over the room carries "taste"
    "M18": "no_sense",
    # 29 Oct 2026 (user: "Better door models needed"): a door no real product (model_review.door_products; a planned
    # library door the build did not make carries "lost")
    "M20": "taste",
    # 29 Oct 2026: the rooms furnished for their use (model review M21, Argus U19; wenart.furniture.room_use)
    "M21": "taste", "U19": "taste",
    # 29 Oct 2026 (user on real06: "This washing machine would not open", "this sink not making sense there"): a door or
    # drawer front that cannot open, a basin under a low window (model_review.fixtures_in_use); ("There is a gap between
    # wall and water faucet not looking good") a back a drawing gap off its wall (model_review.backs_on_walls)
    "M19": "no_sense", "M22": "misread",
    # 29 Oct 2026 (lesson UL109: "There are no chimneys"): a chimney off the roof, floating, too low for the rule or in
    # front of a window (model_review.chimneys_review)
    "M24": "no_sense",
    # the visitor checks and the looks
    "Q1": "no_sense", "Q2": "no_sense", "Q3": "no_sense", "Q4": "misread", "Q5": "taste", "Q6": "geometry",
    "Q7": "taste", "Q8": "no_sense", "Q9": "no_sense", "D1": "geometry", "D2": "taste", "D3": "taste",
    "Q10": "no_sense", "Q11": "no_sense", "Q12": "no_sense", "Q13": "taste", "Q14": "taste", "Q15": "taste",
    "X9": "no_sense", "X10": "no_sense",
    # 28 Oct 2026: the lessons line (wenart.audit.lessons): what the user pointed at, measured
    "U11": "taste", "U12": "taste", "U13": "taste", "U14": "taste", "U15": "taste",
    # 29 Oct 2026: the user's real06 review
    "U21": "no_sense", "U22": "taste", "U24": "no_sense", "U25": "misread", "U26": "taste", "U28": "no_sense",
    "U18": "taste",                  # 29 Oct 2026: the door models as built (UL89)
    # 29 Oct 2026 (lesson UL93: "Computer on the table would have been nice or a laptop"): a desk with no work set
    "U17": "taste",
    # 29 Oct 2026: a door front that cannot open (U16, UL92), a back a drawing gap off its wall (U20, UL96)
    "U16": "no_sense", "U20": "misread",
    # 29 Oct 2026 (lesson UL109): a pitched-roof house of a chimney family with no chimney (a drawn fireplace or flue
    # left without one carries "lost")
    "U27": "taste",
    # code critic
    "F7": "geometry", "F8": "geometry", "G11": "geometry", "G9": "misread", "G10": "misread",
    # conservation
    "C1": "lost", "C2": "lost", "C3": "lost", "C4": "untyped", "C5": "lost", "C8": "geometry",
    # 28 Oct 2026: a built library model its names or its audit refuse (code critic LT, process P11)
    "LT": "misread", "P11": "misread",
}
CHECK_KIND.update({"U23": "taste", "M23": "taste"})     # 29 Oct 2026 (UL106): the professional bar (dressing.review)
# 29 Oct 2026 (UL116, UL117, UL120, UL122, UL125; user: "argus should have think of this"): a reference solution the
# model misses (closed doors everywhere, one door size, a walk-in behind closed panels, doors without frames)
KINDS["reference_missed"] = {
    "what": "the model misses a solution the user's reference photos show and the rules now build (inside doors open, "
            "doors sized by role and family, framed doors, a see-through walk-in dressing room): not a fault of a "
            "stage, a design move left out",
    "arises": "build, architect",
    "guards": ["model review M29", "Argus U33", "the architect's D7 / D8", "the lesson walk (AI5)"]}
CHECK_KIND.update({"U33": "reference_missed", "M29": "reference_missed"})
CHECK_KIND.update({"U30": "taste", "M26": "taste"})     # 29 Oct 2026 (UL114): the bathroom's set (bath_details.review)
# 29 Oct 2026 (UL115, UL118): a kitchen missing what its style family's kitchen details give it (kitchen_details.review)
CHECK_KIND.update({"M27": "taste", "U31": "taste"})
# 29 Oct 2026 (UL113, UL115, UL119): a different solution for each room, the reference photos' details
# (room_schemes.review)
CHECK_KIND.update({"U32": "taste", "M28": "taste"})
PREFIX_KIND = {"A": "lost", "B": "lost", "C": "lost", "P": "process", "J": "taste", "F": "geometry", "G": "geometry",
               "S": "taste", "L": "no_sense", "X": "no_sense", "V": "taste", "R": "misread", "W": "no_sense",
               "E": "no_sense", "O": "no_sense", "H": "no_sense", "K": "no_sense", "T": "no_sense", "U": "no_sense"}
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
