"""The weak-spot synthetic projects (22 Nov 2026, Milestone 14 self-improvement round): one project per error kind the
weak-spot hunter ranks highest (``wenart.reading_check.weak_spots``: the bench, the AI checks' known errors, the user's
corrections and the reading checks, each as a share), built on the failure-class base flat
(``failure_projects.base_house``) so a reading that fails names its kind.

- ``synthetic-24-sliding-windows`` (opening_type; the user's C0085, C0086, C0091 on real10, UL346): three windows
  drawn as sliding windows, two sashes on two tracks in the wall gap, on the window layer (as real10's PENCERE
  draws them), the same sashes in the SALON's second window with a door-high tag '160/220' beside them, and the
  kitchen door as a sliding door on the door layer. Truth: the three windows are windows, the tagged pair and the
  kitchen door are doors (the sashes alone cannot tell, the tag does).
- ``synthetic-25-stair-edge`` (wall_invented; the user's C0053 on real07: "no wall: the stair's edge"): a straight
  flight of 16 treads in the SALON along its inner wall, its open side drawn as two parallel lines 5 cm apart on the
  wall layer (the stringer and balustrade), free at both ends. Truth: the stair, no wall there.
- ``synthetic-26-corner-shower`` (door_invented; a curve that is no door swing): a quarter-circle corner shower in
  the BANYO (its curved front an arc of 0.80 m with its two straight sides, on the sanitary layer VITRIFIYE) and a
  quarter-round corner cabinet in the MUTFAK (an arc of 0.60 m on TEFRIS) beside the window gaps. Truth: the base
  house (6 doors, 9 windows), no door at the curves (the rule keys on the sanitary layer; furniture layers may hold
  doors: real03).
"""
from __future__ import annotations

from wenart.synthetic import failure_classes as FC
from wenart.synthetic.failure_classes import FailureProject, Prim, StairTruth, r6
from wenart.synthetic.failure_projects import BRIEF, GROUND, base_house

SASH_T = 0.025               # m, a sash profile across the wall
SASH_OVERLAP = 0.07          # m, the two sashes overlap at the meeting rail


def sliding_window_prims(plan, op) -> list:
    """Two sashes of a sliding window in ``op``'s gap on the window layer: each a thin rectangle on its own track
    (a quarter of the wall thickness either side of the axis), meeting with ``SASH_OVERLAP`` in the middle."""
    w = plan.wall(op.wall)
    s0, s1 = op.s - op.width / 2, op.s + op.width / 2
    mid = (s0 + s1) / 2
    q = w.t / 4
    out = []
    for (a, b), track in (((s0, mid + SASH_OVERLAP / 2), -q), ((mid - SASH_OVERLAP / 2, s1), q)):
        lo, hi = track - SASH_T / 2, track + SASH_T / 2
        out.append(Prim("poly", FC.L_WINDOW, [w.at(a, lo), w.at(b, lo), w.at(b, hi), w.at(a, hi)], closed=True))
    return out


def project_24() -> FailureProject:
    plan = base_house()
    for op in plan.openings:
        if op.id in ("w_salon1", "w_yatak1", "w_cocuk1"):
            op.draw_symbol = False
            plan.prims += sliding_window_prims(plan, op)
        if op.id == "d_mutfak":
            op.kind = "sliding"
        if op.id == "w_salon2":
            # the same sashes on the window layer with a door-high size tag beside them: a sliding door to the garden
            op.draw_symbol = False
            op.truth_type = "door"
            plan.prims += sliding_window_prims(plan, op)
            at = plan.wall(op.wall).at(op.s)
            plan.prims.append(Prim("text", FC.L_TEXT, [(r6(at[0]), r6(at[1] + 0.45))], text="160/220", height=0.12))
    return FailureProject("synthetic-24-sliding-windows", "sliding_windows", "UL346",
                          "sliding windows (two sashes on two tracks on the window layer), a pair tagged door-high, "
                          "a sliding door on the door layer", [plan], [GROUND], BRIEF,
                          extra_truth={"weak_kind": "opening_type", "records": ["C0085", "C0086", "C0091"]})


def project_25() -> FailureProject:
    plan = base_house()
    x0, x1, going = 2.6, 6.6, 0.25              # 16 treads: 17 risers of 0.176 m over a 3.00 m storey
    y_wall = 4.4 - FC.INT_T / 2 - 0.05          # 5 cm clear of the inner wall's face
    y_edge = y_wall - 1.0                        # a 1.0 m wide flight
    prims = [Prim("poly", FC.L_STAIR, [(x0, y_edge), (x1, y_edge), (x1, y_wall), (x0, y_wall)], closed=True)]
    for k in range(1, int(round((x1 - x0) / going))):
        x = r6(x0 + k * going)
        prims.append(Prim("line", FC.L_STAIR, [(x, y_edge), (x, y_wall)]))
    ym = (y_edge + y_wall) / 2
    prims += [Prim("line", FC.L_STAIR, [(x0 + 0.1, ym), (x1 - 0.1, ym)]),
              Prim("line", FC.L_STAIR, [(x1 - 0.1, ym), (x1 - 0.25, ym + 0.08)]),
              Prim("line", FC.L_STAIR, [(x1 - 0.1, ym), (x1 - 0.25, ym - 0.08)])]
    # the open side: the stringer and balustrade as two parallel lines 5 cm apart on the wall layer, free at both ends
    prims += [Prim("line", FC.L_WALL, [(x0, r6(y_edge)), (x1, r6(y_edge))]),
              Prim("line", FC.L_WALL, [(x0, r6(y_edge - 0.05)), (x1, r6(y_edge - 0.05))])]
    plan.prims += prims
    n = int(round((x1 - x0) / going))
    plan.stairs.append(StairTruth("s_{L}_001", "straight", ((x0 + x1) / 2, ym), n + 1,
                                  extra={"treads": n, "box": [FC.rp((x0, y_edge)), FC.rp((x1, y_wall))]}))
    for lb in plan.labels:
        if lb.text == "SALON":
            lb.at = (2.0, 1.6)
    return FailureProject("synthetic-25-stair-edge", "stair_edge", "UL315",
                          "a straight flight whose open side (stringer and balustrade) is drawn as two lines on the "
                          "wall layer", [plan], [GROUND], BRIEF,
                          extra_truth={"weak_kind": "wall_invented", "records": ["C0053"]})


def project_26() -> FailureProject:
    plan = base_house()
    t2 = FC.INT_T / 2
    # BANYO: x 4.0..6.5, y 5.8..9.0 (inner faces x 4.075..6.425, y 5.875..8.875); the shower in its top-right corner
    cx, cy, r = 6.425, 8.875, 0.80
    shower = [Prim("arc", "VITRIFIYE", [(cx, cy)], radius=r, angles=(180.0, 270.0)),
              Prim("line", "VITRIFIYE", [(cx - r, cy), (cx, cy)]),
              Prim("line", "VITRIFIYE", [(cx, cy - r), (cx, cy)]),
              Prim("arc", "VITRIFIYE", [(cx, cy)], radius=r - 0.05, angles=(180.0, 270.0))]
    # MUTFAK: x 0..4.0, y 5.8..9.0 (inner faces x 0.125..3.925, y 5.875..8.875); a quarter-round corner cabinet
    kx, ky, kr = 0.125, 8.875, 0.60
    cabinet = [Prim("arc", "TEFRIS", [(kx, ky)], radius=kr, angles=(270.0, 360.0)),
               Prim("line", "TEFRIS", [(kx, ky - kr), (kx, ky)]),
               Prim("line", "TEFRIS", [(kx, ky), (kx + kr, ky)])]
    plan.prims += shower + cabinet
    _ = t2
    return FailureProject("synthetic-26-corner-shower", "furniture_arcs", "UL321",
                          "a quarter-circle corner shower and a quarter-round corner cabinet beside window gaps: "
                          "curves that are no door swings", [plan], [GROUND], BRIEF,
                          extra_truth={"weak_kind": "door_invented"})


PROJECTS = (("opening_type", project_24), ("wall_invented", project_25), ("door_invented", project_26))
