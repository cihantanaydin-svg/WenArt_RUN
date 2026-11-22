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
from wenart.synthetic.failure_classes import FailureProject, Prim, StairTruth, TruthLevel, r6
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


def project_31() -> FailureProject:
    """synthetic-31-plain-layers (S5, 22 Nov 2026; read twice with renamed layers: real09 lost 290 of 388 walls): the
    base flat with every layer renamed L1, L2 ... (layer 0 kept), so no layer name says wall, door, window or text.
    Truth: the base house (6 rooms, 6 doors, 9 windows), as with the named layers."""
    plan = base_house()
    return FailureProject("synthetic-31-plain-layers", "plain_layers", "S5",
                          "the base flat with its layers renamed L1, L2 ...: the layer names say nothing", [plan],
                          [GROUND], BRIEF, extra_truth={"weak_kind": "layer_names"}, plain_layers=True)


def _tag(plan, op, text: str, off: tuple) -> Prim:
    at = plan.wall(op.wall).at(op.s)
    return Prim("text", FC.L_TEXT, [(r6(at[0] + off[0]), r6(at[1] + off[1]))], text=text, height=0.12)


def project_29() -> FailureProject:
    """synthetic-29-upper-floor-door (S3, 22 Nov 2026; the user's C0089, RC17 door_into_air on real06 L1): a
    two-storey house (the stair house twice, a section naming ZEMİN KAT ±0.00 and 1. KAT +3.00). The upper floor's
    SALON facade carries (a) a 1.6 m pair of sliding leaves on the window layer PENCERE with a door-high tag '160/220'
    (read as a sliding door, like real06's '220/230') with nothing outside to step onto: truth a window; and (b) the
    bedroom's swung door onto a drawn balcony (BALKON, a 0.10 m parapet round it): truth a door."""
    from wenart.synthetic.failure_projects import stair_house, upper_floor

    g = stair_house("p0", (10.0, 10.0), "ZEMİN KAT PLANI")
    u = stair_house("p1", (30.0, 10.0), "1. KAT PLANI")
    upper_floor(u)
    for op in u.openings:
        if op.id == "w_salon1":
            op.draw_symbol = False
            u.prims += sliding_window_prims(u, op)
            u.prims.append(_tag(u, op, "160/220", (0.0, 0.45)))
        if op.id == "w_yatak1":
            op.kind, op.width, op.hinge, op.side = "door", 0.9, "start", 1
    t = FC.INT_T * 2 / 3
    u.walls += [FC.Wall("b1", (8.5 + t / 2, 0.0), (8.5 + t / 2, -1.3), t),
                FC.Wall("b2", (8.5, -1.3 + t / 2), (10.5, -1.3 + t / 2), t),
                FC.Wall("b3", (10.5 - t / 2, -1.3), (10.5 - t / 2, 0.0), t)]
    u.labels.append(FC.Label("BALKON", (9.5, -0.65)))
    storeys = [("ZEMİN KAT", 0.0), ("1. KAT", 3.0)]
    section = FC.section_prims((50.0, 10.0), 12.0, storeys, ("ÇATI", 6.0), "A-A KESİTİ")
    levels = [TruthLevel("L0", "Zemin Kat", 0.0, 0, "p0"), TruthLevel("L1", "1. Kat", 3.0, 1, "p1")]
    return FailureProject("synthetic-29-upper-floor-door", "upper_floor_door", "S3",
                          "an upper-floor sliding pair on the window layer tagged door-high with nothing outside "
                          "(a window) and a swung door onto a drawn balcony (a door)", [g, u], levels, BRIEF,
                          sheet_prims=section, extra_truth={"weak_kind": "door_invented", "records": ["C0089"]})


def project_30() -> FailureProject:
    """synthetic-30-fire-stair (S4, 22 Nov 2026; the user's C0035, C0040, UL307, UL316): the stair house's typical
    floor (a ground floor plan and '1-3. NORMAL KAT PLANI' for three storeys, a section naming them) with a second U
    stair, the fire escape, in a closed enclosure labelled YANGIN MERDİVENİ (the BANYO's place): its 1.40 m door to the
    hall drawn as a bare gap with the tag '140/230' over it, and one empty 0.9 m gap (nothing drawn in it) to the flat's
    MUTFAK. Truth: the door, no opening at the empty gap, on every floor."""
    from wenart.synthetic.failure_projects import _relabel, stair_house

    def plan(key, origin, title):
        p = stair_house(key, origin, title)
        _relabel(p, {"BANYO": "YANGIN MERDİVENİ"})
        for lb in p.labels:
            if lb.text == "YANGIN MERDİVENİ":
                lb.at = (5.25, 6.4)
        prims, truth = FC.u_stair(4.15, 6.75, 6.35, 8.75, 0.25, 6, 6, winders=5, numbers=True)
        p.prims += prims
        p.stairs.append(StairTruth("s_{L}_002", "u_winder", ((4.15 + 6.35) / 2, (6.75 + 8.75) / 2),
                                   truth["treads"], extra=truth))
        for op in p.openings:
            if op.id == "d_banyo":
                op.width, op.draw_symbol = 1.4, False
                p.prims.append(_tag(p, op, "140/230", (0.0, 0.40)))
        p.openings.append(FC.Opening("g_empty", "opening", "i4", 1.6, 0.9, draw_symbol=False, truth_type="absent"))
        return p
    g = plan("p0", (10.0, 10.0), "ZEMİN KAT PLANI")
    t = plan("p1", (30.0, 10.0), "1-3. NORMAL KAT PLANI")
    t.openings = [op for op in t.openings if op.id != "entrance"]
    t.openings.append(FC.Opening("w_hol", "window", "e4", 3.9, 1.0))
    storeys = [("ZEMİN KAT", 0.0)] + [(f"{k}. NORMAL KAT", 3.0 * k) for k in range(1, 4)]
    section = FC.section_prims((50.0, 10.0), 12.0, storeys, ("ÇATI", 12.0), "A-A KESİTİ")
    levels = [TruthLevel("L0", "Zemin Kat", 0.0, 0, "p0")] + [
        TruthLevel(f"L{k}", f"{k}. Normal Kat", 3.0 * k, k, "p1") for k in range(1, 4)]
    return FailureProject("synthetic-30-fire-stair", "fire_stair", "S4",
                          "a second U stair in a closed fire-escape enclosure: a tagged 1.40 m door to the hall and "
                          "an empty gap to a flat (no opening)", [g, t], levels, BRIEF, sheet_prims=section,
                          extra_truth={"weak_kind": "opening_invented", "records": ["C0035", "C0040"],
                                       "typical_plan": {"title": "1-3. NORMAL KAT PLANI",
                                                        "levels": ["L1", "L2", "L3"]}})


def project_32() -> FailureProject:
    """synthetic-32-sliding-window-tag (S6, 22 Nov 2026; the user's C0086 "it is a sliding window", C0087 "it is a
    sliding door for the lift"): synthetic-24's flat with the SALON's second window drawn as a pair of sliding leaves on
    the door layer KAPI with the window-high tag '160/140' beside it (truth: a window), and the MUTFAK turned into the
    lift (ASANSÖR) whose sliding door on KAPI carries '90/210' (truth: a door)."""
    from wenart.synthetic.failure_projects import _relabel

    plan = base_house()
    _relabel(plan, {"MUTFAK": "ASANSÖR"})
    for op in plan.openings:
        if op.id == "w_salon2":
            op.kind, op.truth_type = "sliding", "window"
            plan.prims.append(_tag(plan, op, "160/140", (0.0, 0.45)))
        if op.id == "d_mutfak":
            op.kind = "sliding"
            plan.prims.append(_tag(plan, op, "90/210", (0.0, 0.40)))
    return FailureProject("synthetic-32-sliding-window-tag", "sliding_window_tag", "S6",
                          "door-layer sliding leaves with a window-high tag (a window) beside a lift's tagged sliding "
                          "door (a door)", [plan], [GROUND], BRIEF,
                          extra_truth={"weak_kind": "opening_type", "records": ["C0086", "C0087"]})


PROJECTS = (("opening_type", project_24), ("wall_invented", project_25), ("door_invented", project_26),
            ("upper_floor_door", project_29), ("fire_stair", project_30), ("layer_names", project_31),
            ("sliding_window_tag", project_32))
