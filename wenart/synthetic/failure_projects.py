"""The synthetic failure-class projects (synthetic-08 ...), one per way real drawings broke the reader.

What (4 Nov 2026, Milestone 14 track R7): the layouts of the failure-class projects as readable code. Each function
returns a ``FailureProject`` (``wenart.synthetic.failure_classes``) with one failure class the user found in the real
drawings of 3 and 4 Nov 2026 and the lesson that taught it. The user's goal: "I want structure recognition to be
cumulatively better with the feedbacks I am giving".

Why: one class per project, so a reading that fails names its class; small houses (4-8 rooms, one level unless the
class needs more) so a reading takes seconds.

How: ``base_house`` is the 12.0 x 9.0 m CAD-office flat every class starts from (six rooms around a corridor, outer
walls 25 cm, inner walls 15 cm, Turkish labels, a title and a scale note below); each class function changes only what
its class needs. ``failure_projects()`` lists them in order.
"""
from __future__ import annotations

from typing import Optional

from wenart.synthetic import failure_classes as FC
from wenart.synthetic.failure_classes import (
    EXT_T, INT_T, L_FRAME, L_TEXT, FailureProject, Label, Opening, Plan, Prim, StairTruth, TruthLevel, Wall,
    outer_walls)

BRIEF = {"style": "Modern, oak floor, white walls, warm daylight"}
GROUND = TruthLevel("L0", "Zemin Kat", 0.0, 0, "p0")


def base_house(key: str = "p0", origin=(10.0, 10.0), title: str = "ZEMİN KAT PLANI") -> Plan:
    """12.0 x 9.0 m: SALON and YATAK ODASI below an 8.5 m corridor (HOL, the entrance on the left), MUTFAK, BANYO and
    an L-shaped ÇOCUK ODASI above it (the corridor ends at x = 8.5, the bedroom wraps round its end). 6 rooms, 6
    doors, 9 windows. Deliberately not mirror-symmetric: the walls overlap their mirror about the middle by about 85 %,
    under the reader's 90 % for a plan of two mirrored halves (``facade.MIRROR_FIX_SHARE``)."""
    walls = outer_walls("e", 12.0, 9.0) + [
        Wall("i1", (0.0, 4.4), (12.0, 4.4), INT_T),       # corridor, lower side
        Wall("i2", (0.0, 5.8), (8.5, 5.8), INT_T),        # corridor, upper side
        Wall("i3", (7.0, 0.0), (7.0, 4.4), INT_T),        # SALON | YATAK ODASI
        Wall("i4", (4.0, 5.8), (4.0, 9.0), INT_T),        # MUTFAK | BANYO
        Wall("i5", (6.5, 5.8), (6.5, 9.0), INT_T),        # BANYO | ÇOCUK ODASI
        Wall("i6", (8.5, 4.4), (8.5, 5.875), INT_T),      # the corridor's end (to i2's outer face: a clean corner)
    ]
    openings = [
        Opening("entrance", "door", "e4", 3.9, 1.0, hinge="end", side=1),    # e4 runs down: s = 9 - y
        Opening("d_salon", "door", "i1", 3.0, 0.9, hinge="start", side=-1),
        Opening("d_yatak", "door", "i1", 7.8, 0.9, hinge="end", side=-1),
        Opening("d_mutfak", "door", "i2", 2.0, 0.9, hinge="start", side=1),
        Opening("d_banyo", "door", "i2", 5.2, 0.8, hinge="end", side=1),
        Opening("d_cocuk", "door", "i2", 7.5, 0.9, hinge="start", side=1),
        Opening("w_salon1", "window", "e1", 2.0, 1.6),
        Opening("w_salon2", "window", "e1", 5.0, 1.6),
        Opening("w_salon3", "window", "e4", 6.8, 1.4),
        Opening("w_yatak1", "window", "e1", 9.5, 1.4),
        Opening("w_yatak2", "window", "e2", 2.2, 1.2),    # e2 runs up: s = y
        Opening("w_mutfak", "window", "e3", 10.0, 1.2),   # e3 runs right to left: s = 12 - x
        Opening("w_banyo", "window", "e3", 6.75, 0.6),
        Opening("w_cocuk1", "window", "e3", 2.8, 1.4),
        Opening("w_cocuk2", "window", "e2", 6.6, 1.0),
    ]
    labels = [Label("SALON", (3.5, 2.2)), Label("YATAK ODASI", (9.5, 2.6)), Label("HOL", (5.0, 5.1)),
              Label("MUTFAK", (2.0, 7.4)), Label("BANYO", (5.25, 7.4)), Label("ÇOCUK ODASI", (9.25, 7.4))]
    return Plan(key, origin, walls, openings, labels, title=title)


def project_08(spaced: bool = True) -> FailureProject:
    """synthetic-08-spaced-labels (UL323): every room label written letter by letter as separate TEXT entities
    ("S A L O N", "Y A T A K   O D A S I" with a blank letter slot between the words), and a site plan (VAZİYET
    PLANI) beside the floor plan whose pool and road are labelled the same way ("H A V U Z", "Y O L"), as real07's
    site plan was. Truth: the room labels as their words, one pool (the outline round the HAVUZ label)."""
    plan = base_house()
    for lb in plan.labels:
        lb.spaced = spaced
    sx, sy = 40.0, 10.0                     # the site plan's origin on the sheet (the plot's lower-left corner)
    bx, by = 4.0, 6.0                       # the building's outer faces on the plot
    px0, py0, px1, py1 = 19.0, 8.0, 25.0, 11.0
    site = [Prim("poly", "VAZIYET", [(sx, sy), (sx + 30, sy), (sx + 30, sy + 22), (sx, sy + 22)], closed=True),
            Prim("poly", "VAZIYET", [(sx + bx, sy + by), (sx + bx + 12, sy + by), (sx + bx + 12, sy + by + 9),
                                     (sx + bx, sy + by + 9)], closed=True),
            Prim("poly", "HAVUZ", [(sx + px0, sy + py0), (sx + px1, sy + py0), (sx + px1, sy + py1),
                                   (sx + px0, sy + py1)], closed=True),
            Prim("poly", "HAVUZ", [(sx + px0 - 0.3, sy + py0 - 0.3), (sx + px1 + 0.3, sy + py0 - 0.3),
                                   (sx + px1 + 0.3, sy + py1 + 0.3), (sx + px0 - 0.3, sy + py1 + 0.3)], closed=True),
            # the paved terrace from the house's right face round the pool, the garden path to the gate, the road
            Prim("poly", "VAZIYET", [(sx + bx + 12, sy + 7.0), (sx + 26.5, sy + 7.0), (sx + 26.5, sy + 12.0),
                                     (sx + bx + 12, sy + 12.0)], closed=True),
            Prim("line", "VAZIYET", [(sx, sy + 10.6), (sx + bx, sy + 10.6)]),
            Prim("line", "VAZIYET", [(sx, sy + 11.6), (sx + bx, sy + 11.6)]),
            Prim("poly", "VAZIYET", [(sx - 2, sy - 3), (sx + 32, sy - 3), (sx + 32, sy), (sx - 2, sy)], closed=True)]
    for lb in (Label("HAVUZ", (sx + (px0 + px1) / 2, sy + (py0 + py1) / 2), spaced=spaced),
               Label("YOL", (sx + 15, sy - 1.5), spaced=spaced), Label("±0.00", (sx + bx + 6, sy + by + 4.5))):
        site += FC.label_prims(lb)
    site.append(Prim("text", L_TEXT, [(sx + 15, sy - 5)], text="VAZİYET PLANI", height=0.8))
    site.append(Prim("text", L_TEXT, [(sx + 15, sy - 6.2)], text="ÖLÇEK 1/200", height=0.4))
    pool = [[px0 - bx, py0 - by], [px1 - bx, py0 - by], [px1 - bx, py1 - by], [px0 - bx, py1 - by]]
    return FailureProject("synthetic-08-spaced-labels", "spaced_labels", "UL323",
                          "room and site labels written letter by letter as separate TEXT entities",
                          [plan], [GROUND], BRIEF, sheet_prims=site,
                          extra_truth={"site": {"pools": [{"label": "HAVUZ", "polygon": pool}],
                                                "labels": ["HAVUZ", "YOL"]}})


def _drop(plan: Plan, *ids: str) -> None:
    plan.openings = [o for o in plan.openings if o.id not in ids]


def _relabel(plan: Plan, mapping: dict) -> None:
    for lb in plan.labels:
        lb.text = mapping.get(lb.text, lb.text)


def project_09() -> FailureProject:
    """synthetic-09-jamb-stubs (UL301): the inner walls are 16 cm thick and every inner door's jambs are drawn the
    way real10's drafter drew them: on one side of the gap the wall faces stop open and two short stubs stand side by
    side across the wall (7 cm and 3 cm, 5 cm long, the frame and its stop), on the other side the wall faces stop
    open with a frame cap (one line across the wall end on KAPI). The doors are drawn as usual (arc and leaf)."""
    plan = base_house()
    plan.walls = [Wall(w.id, w.a, w.b, 0.16) if w.id.startswith("i") else w for w in plan.walls]
    for op in plan.openings:
        if op.kind == "door" and op.wall.startswith("i"):
            op.jamb_start, op.jamb_end = ("cap", "stubs") if op.hinge == "start" else ("stubs", "cap")
    return FailureProject("synthetic-09-jamb-stubs", "jamb_stubs", "UL301",
                          "door jambs drawn as two short stubs side by side and as frame caps at open wall ends",
                          [plan], [GROUND], BRIEF)


def project_10() -> FailureProject:
    """synthetic-10-glazed-facade (UL274): the SALON's facade (the bottom wall from x = 0 to 7) has no wall faces:
    it is drawn only as its frames, a 2.2 m window, a 2.4 m sliding door to the garden and a 1.1 m window, each a
    frame rectangle across the wall band (windows on PENCERE, the sliding door on KAPI) with short posts between them
    on a column layer (KOLON). The other walls are drawn as usual. Truth: the wall stands there (``drawn: false``)
    with two windows and a door."""
    plan = base_house()
    _drop(plan, "w_salon1", "w_salon2")
    e1 = plan.wall("e1")
    plan.walls.remove(e1)
    plan.walls[0:0] = [Wall("e1a", (0.0, EXT_T / 2), (7.0, EXT_T / 2), EXT_T, drawn=False),
                       Wall("e1b", (7.0, EXT_T / 2), (12.0, EXT_T / 2), EXT_T)]
    for op in plan.openings:
        if op.wall == "e1":
            op.wall, op.s = "e1b", op.s - 7.0
    plan.openings += [Opening("g_win_a", "window", "e1a", 1.55, 2.2),
                      Opening("g_slide", "sliding", "e1a", 4.15, 2.4),
                      Opening("g_win_b", "window", "e1a", 6.2, 1.1)]
    for x0, x1 in ((0.25, 0.45), (2.65, 2.95), (5.35, 5.65)):
        plan.prims.append(Prim("poly", "KOLON", [(x0, 0.0), (x1, 0.0), (x1, EXT_T), (x0, EXT_T)], closed=True))
    return FailureProject("synthetic-10-glazed-facade", "glazed_facade", "UL274",
                          "a living room whose outer wall is drawn only as window and sliding-door frames",
                          [plan], [GROUND], BRIEF)


def failure_projects() -> list[FailureProject]:
    return [project_08(), project_09(), project_10()]
