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
- ``synthetic-28-stair-edge-run`` (S2, wall_invented): synthetic-25's flight whose open side runs on past its top end
  as the faces of a 0.10 m partition up to the next wall (one wall piece in the drawing). Truth: the partition beyond
  the flight is a wall, no wall along the flight.
- ``synthetic-33-double-wall`` (the user's C0086 on real10): a facade drawn as two leaves (0.20 m, a 0.04 m cavity,
  0.10 m) with a sliding window in the inner leaf's gap, a door through both, and a shaft wall 0.15 m inside it. Truth:
  one wall of the total thickness, one window, one door, the shaft wall kept.
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


def project_28() -> FailureProject:
    """synthetic-28-stair-edge-run (S2, 22 Nov 2026; the rule the user's C0053 suggested): synthetic-25's straight
    flight of 16 treads along the SALON's inner wall, its open side (stringer and balustrade) drawn as two lines 0.10 m
    apart on the wall layer that run on, past the flight's top end, as the faces of a 0.10 m partition 1.5 m long up to
    the SALON | YATAK ODASI wall (one wall piece in the drawing). Truth: the stair, the partition beyond the flight is a
    wall, no wall along the flight."""
    plan = base_house()
    going, n = 0.25, 16
    x_end = 7.0 - FC.INT_T / 2                   # the face of i3 (SALON | YATAK ODASI)
    x1 = x_end - 1.5                             # the flight's top end, 1.5 m short of i3
    x0 = x1 - n * going
    y_wall = 4.4 - FC.INT_T / 2 - 0.05          # 5 cm clear of the inner wall's face
    y_edge = y_wall - 1.0                        # a 1.0 m wide flight
    t = 0.10
    prims = [Prim("poly", FC.L_STAIR, [(r6(x0), y_edge), (r6(x1), y_edge), (r6(x1), y_wall), (r6(x0), y_wall)],
                  closed=True)]
    for k in range(1, n):
        x = r6(x0 + k * going)
        prims.append(Prim("line", FC.L_STAIR, [(x, y_edge), (x, y_wall)]))
    ym = (y_edge + y_wall) / 2
    prims += [Prim("line", FC.L_STAIR, [(r6(x0 + 0.1), ym), (r6(x1 - 0.1), ym)]),
              Prim("line", FC.L_STAIR, [(r6(x1 - 0.1), ym), (r6(x1 - 0.25), ym + 0.08)]),
              Prim("line", FC.L_STAIR, [(r6(x1 - 0.1), ym), (r6(x1 - 0.25), ym - 0.08)])]
    # the open side and the partition: two lines 0.10 m apart on the wall layer from the flight's foot to i3's face
    prims += [Prim("line", FC.L_WALL, [(r6(x0), r6(y_edge)), (r6(x_end), r6(y_edge))]),
              Prim("line", FC.L_WALL, [(r6(x0), r6(y_edge - t)), (r6(x_end), r6(y_edge - t))])]
    plan.prims += prims
    # the partition stands in the truth; its faces are the two lines above (not drawn a second time)
    plan.walls.append(FC.Wall("p1", (r6(x1), r6(y_edge - t / 2)), (r6(x_end), r6(y_edge - t / 2)), t, drawn=False))
    plan.stairs.append(StairTruth("s_{L}_001", "straight", ((x0 + x1) / 2, ym), n + 1,
                                  extra={"treads": n, "box": [FC.rp((x0, y_edge)), FC.rp((x1, y_wall))]}))
    for lb in plan.labels:
        if lb.text == "SALON":
            lb.at = (2.0, 1.6)
    return FailureProject("synthetic-28-stair-edge-run", "stair_edge_run", "S2",
                          "a straight flight whose open side (stringer and balustrade) runs on past its top end as the "
                          "faces of a 0.10 m partition: one wall piece in the drawing", [plan], [GROUND], BRIEF,
                          extra_truth={"weak_kind": "wall_invented", "records": ["C0053"]})


def _leaf_pieces(y0: float, y1: float, x0: float, x1: float, gaps: list) -> list:
    """The closed outlines of one facade leaf (y0..y1) from x0 to x1 on the wall layer, cut at ``gaps``."""
    out, x = [], x0
    for g0, g1 in sorted(gaps) + [(x1, x1)]:
        if g0 - x > 1e-6:
            out.append(Prim("poly", FC.L_WALL, [(r6(x), r6(y0)), (r6(g0), r6(y0)), (r6(g0), r6(y1)),
                                                (r6(x), r6(y1))], closed=True))
        x = g1
    return out


def project_33() -> FailureProject:
    """synthetic-33-double-wall (22 Nov 2026; the user's C0086 on real10 L0, "it is a sliding window"): the base flat
    whose bottom facade is drawn as two leaves, an inner 0.20 m leaf, a 0.04 m cavity and an outer 0.10 m skin (the
    build-up of a Turkish double wall with its insulation gap). The SALON's first window is a sliding window, its two
    sashes in the inner leaf's gap (the outer leaf's gap facing it is empty), its second opening a swung door through
    both leaves; the YATAK ODASI has a 0.10 m shaft wall 0.15 m inside the facade, parallel to it. Truth: one facade
    wall of the total thickness (0.34 m), one window, one door, the shaft wall a wall of its own."""
    plan = base_house()
    inner_t, cavity, outer_t = 0.20, 0.04, 0.10
    total = inner_t + cavity + outer_t
    e1 = plan.wall("e1")
    e1.a, e1.b, e1.t, e1.drawn = (0.0, r6(total / 2)), (12.0, r6(total / 2)), r6(total), False
    plan.wall("i3").a = (7.0, r6(total))         # SALON | YATAK ODASI ends on the inner leaf's face
    plan.openings = [op for op in plan.openings if op.id != "w_yatak1"]
    gaps = []
    for op in plan.openings:
        if op.wall != "e1":
            continue
        if op.id == "w_salon1":                  # the sliding window: two sashes on two tracks in the inner leaf
            op.draw_symbol = False
            s0, s1 = op.s - op.width / 2, op.s + op.width / 2
            mid, yc, q = (s0 + s1) / 2, outer_t + cavity + inner_t / 2, inner_t / 4
            for (a, b), track in (((s0, mid + 0.035), yc - q), ((mid - 0.035, s1), yc + q)):
                lo, hi = track - 0.0125, track + 0.0125
                plan.prims.append(Prim("poly", FC.L_WINDOW, [(r6(a), r6(lo)), (r6(b), r6(lo)), (r6(b), r6(hi)),
                                                             (r6(a), r6(hi))], closed=True))
        if op.id == "w_salon2":                  # a swung door to the garden through both leaves
            op.kind, op.width, op.hinge, op.side = "door", 0.9, "start", 1
        gaps.append((op.s - op.width / 2, op.s + op.width / 2))
    x0, x1 = FC.EXT_T, 12.0 - FC.EXT_T           # the inner faces of e4 and e2
    plan.prims += _leaf_pieces(outer_t + cavity, total, x0, x1, gaps)      # the inner leaf
    plan.prims += _leaf_pieces(0.0, outer_t, x0, x1, gaps)                 # the outer skin
    # the shaft wall: 0.10 m thick, 0.15 m inside the facade's inner face, from x 9.5 to e2's inner face
    ys = r6(total + 0.15 + 0.05)
    plan.walls.append(FC.Wall("sh1", (9.5, ys), (x1, ys), 0.10))
    return FailureProject("synthetic-33-double-wall", "double_wall", "UL362",
                          "a facade drawn as two leaves (0.20 m, a 0.04 m cavity, 0.10 m) with a sliding window and a "
                          "door through both, and a shaft wall 0.15 m inside it", [plan], [GROUND], BRIEF,
                          extra_truth={"weak_kind": "opening_invented", "records": ["C0086"]})


PROJECTS = (("opening_type", project_24), ("wall_invented", project_25), ("door_invented", project_26),
            ("stair_edge_run", project_28), ("upper_floor_door", project_29), ("fire_stair", project_30),
            ("layer_names", project_31), ("sliding_window_tag", project_32), ("double_wall", project_33))
