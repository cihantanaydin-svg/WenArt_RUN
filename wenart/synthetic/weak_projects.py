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
- ``synthetic-34-open-passage`` (UL363, the user's C0053 on real07): the corridor's lower partition ends 2.3 m short of
  the next wall with nothing in the gap but floor hatch and a grid axis, beside a doorless gap under a dashed beam, the
  bathroom's only way in drawn empty, and an empty facade gap. Truth: an open passage up to the ceiling there only.
- ``synthetic-36-light-well-piers`` (UL367-UL369; real10 L-1, "fix the light well and the two bathroom windows"): an
  enclosed light well between two bathrooms, one bathroom's two 0.5 m windows onto it with a 0.30 m pier the wall
  reading drops, a door and a window with a pier between them; a window with a mullion and a closet with a door keep
  their reading. Truth: two windows, the well a light well (a shaft), the closet storage.
- ``synthetic-37-narrow-door`` (UL371, UL378; the user's C0097 on real15 L1, "Wall or column"): an upper floor's facade
  with a column in a 0.50 m break of its faces and a wardrobe block's rails across the wall at the break's jamb (HEAD
  read a 0.50 m door onto nothing), beside a narrow WC door with its swing, a narrow sliding door with a door-high tag,
  a door of two narrow leaves and a narrow window. Truth: the facade runs on (the column a wall piece), every other
  opening as drawn.
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


def _hatch(x0: float, y0: float, x1: float, y1: float, pitch: float = 0.25) -> list:
    """Floor hatch: 45-degree lines ``pitch`` apart on TARAMA, clipped to the box (the drafter's tile hatch)."""
    from shapely.geometry import LineString, box

    clip, out, k = box(x0, y0, x1, y1), [], 0
    while True:
        c = x0 - (y1 - y0) + k * pitch          # the line y - y0 = x - c
        if c > x1:
            return out
        seg = LineString([(c, y0), (c + (y1 - y0) + (x1 - x0), y1 + (x1 - x0))]).intersection(clip)
        if seg.length > 0.05:
            (a, b) = list(seg.coords)[0], list(seg.coords)[-1]
            out.append(Prim("line", "TARAMA", [(r6(a[0]), r6(a[1])), (r6(b[0]), r6(b[1]))]))
        k += 1


def project_34() -> FailureProject:
    """synthetic-34-open-passage (22 Nov 2026, the user's "build the open-passage rule"; C0053 on real07 L1, UL363): the
    base flat whose SALON opens to the HOL where the corridor's lower partition ends 2.325 m short of the SALON |
    YATAK ODASI wall (nothing in the gap but the floor hatch on TARAMA and the grid axis B on AKS). Beside it the
    cases that keep their opening: the MUTFAK's 1.20 m doorless gap with a dashed beam (KIRIS, DASHED) along both
    faces, the BANYO's only way in drawn as an empty 0.80 m gap (a door is needed: RC14 open_passage, info), and an
    empty 0.80 m gap in the MUTFAK's outer wall (an outline gap: closed as before, the reader's possible undrawn
    window). Truth: the passage an opening with no wall over it (``attrs: open_passage``), the beam's gap and the
    BANYO's openings with a head, the facade gap the window the reader closes the outline with; none of the three an
    open passage."""
    plan = base_house()
    plan.openings = [op for op in plan.openings if op.id not in ("d_salon", "d_mutfak", "d_banyo")]
    x_end = 7.0 - FC.INT_T / 2                  # the face of i3 (SALON | YATAK ODASI)
    x0 = 4.6                                     # the corridor's lower partition ends here, short of i3
    plan.openings += [
        FC.Opening("p_salon", "opening", "i1", r6((x0 + x_end) / 2), r6(x_end - x0), draw_symbol=False,
                   truth_attrs={"open_passage": True}),
        FC.Opening("g_beam", "opening", "i2", 2.0, 1.2, draw_symbol=False, truth_attrs={"open_passage": False}),
        FC.Opening("g_banyo", "opening", "i2", 5.2, 0.8, draw_symbol=False, truth_attrs={"open_passage": False}),
        FC.Opening("g_facade", "opening", "e4", 1.6, 0.8, draw_symbol=False, truth_type="window",   # e4: s = 9 - y
                   truth_attrs={"open_passage": False}),
    ]
    h = FC.INT_T / 2
    plan.prims += [Prim("line", "KIRIS", [(1.4, r6(5.8 - h)), (2.6, r6(5.8 - h))], linetype="DASHED"),
                   Prim("line", "KIRIS", [(1.4, r6(5.8 + h)), (2.6, r6(5.8 + h))], linetype="DASHED")]
    plan.prims += _hatch(x0 + 0.1, 3.9, x_end - 0.1, 4.9)
    plan.prims += FC.axis_grid([], [4.4], (-2.0, -2.0, 14.0, 11.0), [], ["B"])
    return FailureProject("synthetic-34-open-passage", "open_passage", "UL363",
                          "a partition ending short of the next wall with nothing in the gap but hatch and an axis (an "
                          "open passage up to the ceiling), beside a gap under a dashed beam, a bathroom's empty way in "
                          "and an empty facade gap (none of them an open passage)", [plan], [GROUND], BRIEF,
                          extra_truth={"weak_kind": "wall_invented", "records": ["C0053"]})


L_FURNITURE = "TEFRIS"
L_RAILING = "KORKULUK"
L_FLOOR = "ZEMIN"


def _bars(x0: float, x1: float, y0: float, y1: float, pitch: float, pair: float, layer: str) -> list:
    """Equal bars across a facade line (vertical lines from ``y0`` to ``y1``), ``pitch`` apart from ``x0`` to ``x1``,
    each drawn twice ``pair`` apart when ``pair`` (the two faces of a flat bar), on ``layer``."""
    out, x = [], x0
    while x <= x1 + 1e-9:
        for dx in ((0.0, pair) if pair else (0.0,)):
            out.append(Prim("line", layer, [(r6(x + dx), r6(y0)), (r6(x + dx), r6(y1))]))
        x += pitch
    return out


def project_35() -> FailureProject:
    """synthetic-35-grille-slot (22 Nov 2026; the user's C0089 on real10 L-1, "it is not a real room and there is no
    doors to outside", UL365): a light slot between the two bedrooms of the top row (1.8 m wide, 2.9 m deep, as
    real10's; the bedrooms' windows open onto its sides, no label), closed at the facade line by a grille: the outer
    wall runs on across its mouth with a 1.8 m gap holding 16 flat bars 0.64 m long from the outer face inward, each
    drawn as two lines 2 cm apart at a 0.10 m pitch, on the furniture layer TEFRIS (real10's light-slot grille): HEAD
    read two of its bars as a double door's leaves opened at 90 degrees and the slot as a room. The cases that must keep
    their door or opening: the entrance drawn open at 90 degrees with no swing arc (one leaf, two lines) above an
    outside step on MERDIVEN; the YATAK ODASI's French window to a BALKON (a swing arc, a balustrade's bars drawn across
    the wall band on KORKULUK); the MUTFAK's 1.20 m doorless way in, across which floor boards on ZEMIN run on from the
    HOL into the kitchen. Truth: the grille gap a window (a fixed grille), the slot a light well (a shaft, 'HAVA
    BOŞLUĞU': no door reaches it, never furnished), the entrance and the French window doors, the kitchen's way in an
    opening."""
    W, H = 12.0, 9.0
    t = FC.EXT_T
    x0, x1 = 6.3, 8.1                           # the slot's inner faces
    walls = FC.outer_walls("e", W, H) + [
        FC.Wall("i1", (0.0, 4.4), (W, 4.4), FC.INT_T), FC.Wall("i2", (0.0, 5.8), (9.0, 5.8), FC.INT_T),
        FC.Wall("i3", (7.0, 0.0), (7.0, 4.4), FC.INT_T), FC.Wall("i4", (3.6, 5.8), (3.6, H), FC.INT_T),
        FC.Wall("i6", (9.0, 4.4), (9.0, 5.875), FC.INT_T),             # the corridor's end
        FC.Wall("k1", (r6(x0 - t / 2), 5.8), (r6(x0 - t / 2), r6(H - t)), t),     # the slot's sides, to the facade
        FC.Wall("k2", (r6(x1 + t / 2), 5.8), (r6(x1 + t / 2), r6(H - t)), t)]
    tb = FC.INT_T * 2 / 3                       # the balcony's parapet walls (synthetic-29's), off the right facade
    walls += [FC.Wall("b1", (W, r6(1.2 + tb / 2)), (r6(W + 1.3), r6(1.2 + tb / 2)), tb),
              FC.Wall("b2", (r6(W + 1.3 - tb / 2), 1.2), (r6(W + 1.3 - tb / 2), 3.2), tb),
              FC.Wall("b3", (r6(W + 1.3), r6(3.2 - tb / 2)), (W, r6(3.2 - tb / 2)), tb)]
    plan = FC.Plan("p0", (10.0, 10.0), walls, title="ZEMİN KAT PLANI")
    for oid, kind, wall, at, width, kw in [
            ("entrance", "door", "e4", (0.125, 5.1), 1.0, dict(draw_symbol=False)),
            ("d_salon", "door", "i1", (3.0, 4.4), 0.9, dict(hinge="start", side=-1)),
            ("d_yatak", "door", "i1", (7.8, 4.4), 0.9, dict(hinge="end", side=-1)),
            ("g_mutfak", "opening", "i2", (1.8, 5.8), 1.2, dict(draw_symbol=False)),
            ("d_ebeveyn", "door", "i2", (4.8, 5.8), 0.9, dict(hinge="end", side=1)),
            ("d_cocuk", "door", "i6", (9.0, 5.1), 0.9, dict(hinge="start", side=-1)),
            ("w_salon1", "window", "e1", (2.0, 0.125), 1.6, {}), ("w_salon2", "window", "e1", (5.0, 0.125), 1.6, {}),
            ("w_salon3", "window", "e4", (0.125, 2.2), 1.4, {}), ("w_yatak1", "window", "e1", (9.5, 0.125), 1.4, {}),
            ("d_balkon", "door", "e2", (W - 0.125, 2.2), 0.9, dict(hinge="start", side=1)),
            ("w_mutfak", "window", "e3", (1.8, H - 0.125), 1.2, {}),
            ("w_ebeveyn1", "window", "e3", (4.8, H - 0.125), 1.4, {}),
            ("w_ebeveyn2", "window", "k1", (r6(x0 - t / 2), 7.4), 0.6, {}),
            ("w_cocuk1", "window", "k2", (r6(x1 + t / 2), 7.4), 0.6, {}),
            ("g_grille", "window", "e3", (r6((x0 + x1) / 2), H - 0.125), r6(x1 - x0), dict(draw_symbol=False)),
            ("w_cocuk2", "window", "e3", (10.0, H - 0.125), 1.4, {}),
            ("w_cocuk3", "window", "e2", (W - 0.125, 6.6), 1.0, {})]:
        FC.place(plan, oid, kind, wall, at, width, **kw)
    plan.labels = [FC.Label("SALON", (3.5, 2.2)), FC.Label("YATAK ODASI", (9.5, 2.6)), FC.Label("HOL", (5.0, 5.1)),
                   FC.Label("MUTFAK", (1.8, 7.4)), FC.Label("EBEVEYN ODASI", (4.8, 7.4), height=0.15),
                   FC.Label("ÇOCUK ODASI", (10.1, 7.4)), FC.Label("BALKON", (r6(W + 0.65), 2.2), height=0.15)]
    # the slot's grille: flat bars from the outer face 0.64 m inward, the first 0.14 m from a jamb (real10's)
    plan.prims += _bars(r6(x0 + 0.14), r6(x1 - 0.14), r6(H - 0.64), H, 0.10, 0.02, L_FURNITURE)
    # the entrance drawn open at 90 degrees, no arc: one leaf (two lines 4 cm apart) hinged at the gap's upper jamb,
    # running 0.95 m into the HOL; the outside step on MERDIVEN (a landing outline and one tread, along the wall)
    y_hinge = 5.6 - 0.04
    plan.prims += [Prim("line", FC.L_DOOR, [(t, r6(y_hinge)), (r6(t + 0.95), r6(y_hinge))]),
                   Prim("line", FC.L_DOOR, [(t, r6(y_hinge + 0.04)), (r6(t + 0.95), r6(y_hinge + 0.04))]),
                   Prim("poly", FC.L_STAIR, [(-0.6, 4.4), (0.0, 4.4), (0.0, 5.8), (-0.6, 5.8)], closed=True),
                   Prim("line", FC.L_STAIR, [(-0.3, 4.4), (-0.3, 5.8)])]
    # the French window's balustrade: bars across the wall band at a 0.12 m pitch from the inner face, standing out
    # 0.20 m onto the balcony (horizontal: the right facade runs up)
    plan.prims += [Prim("line", L_RAILING, [(r6(W - t), r6(y)), (r6(W + 0.2), r6(y))])
                   for y in (1.85 + 0.12 * k for k in range(7))]
    # the kitchen's floor boards drawn on through its doorless way in (x 1.2 .. 2.4): 0.12 m apart from the HOL into the
    # MUTFAK, through the gap from face to face and beyond both, cut by the wall i2 on either side of the gap
    lo, hi = r6(5.8 - FC.INT_T / 2), r6(5.8 + FC.INT_T / 2)
    for p in _bars(0.4, 3.2, 5.1, 6.5, 0.12, 0.0, L_FLOOR):
        x = p.pts[0][0]
        if 1.2 < x < 2.4:
            plan.prims.append(p)
        else:
            plan.prims += [Prim("line", L_FLOOR, [(x, 5.1), (x, lo)]), Prim("line", L_FLOOR, [(x, hi), (x, 6.5)])]
    plan.truth_rooms = {(r6((x0 + x1) / 2), 7.3): "HAVA BOŞLUĞU"}
    return FailureProject("synthetic-35-grille-slot", "grille_slot", "UL365",
                          "a light slot closed at the facade by a grille of equal bars (a fixed grille, no door, no "
                          "room), beside an entrance drawn open with no arc above a step, a French window over a "
                          "balustrade's bars and a doorless way in crossed by floor boards (each keeps its kind)",
                          [plan], [GROUND], BRIEF,
                          extra_truth={"weak_kind": "door_invented", "records": ["C0089"]})


def project_36() -> FailureProject:
    """synthetic-36-light-well-piers (23 Nov 2026; real10 L-1, the user: "fix the light well and the two bathroom
    windows", UL367, UL368, UL369): an enclosed light well (1.65 x 2.1 m, no label, no door) in the upper row between two
    bathrooms; BANYO 1's wall onto it holds two 0.5 m windows with a 0.30 m pier between them (the pier a closed DUVAR
    box shorter than the wall is thick is wide, touching no other wall: the wall reading drops it, as the dataset's
    drawings' piers), BANYO 2's one 0.6 m window. HEAD read the two windows as one unclassified gap, and that gap kept
    the well a room ('Oda'). The YATAK ODASI's facade holds a door and a window with a 0.25 m pier between them. The
    cases that keep their reading: the SALON's 2.4 m window with a mullion (a line across its frame on the window layer,
    no wall pier: one window), the DEPO under the well (a small room with a door: a closet, never a light well).
    Truth: the well a light well (a shaft, 'HAVA BOŞLUĞU'), each window and door as drawn, the DEPO storage."""
    W, H = 12.0, 9.0
    t, ti = FC.EXT_T, FC.INT_T
    walls = FC.outer_walls("e", W, H) + [
        FC.Wall("i1", (0.0, 4.4), (W, 4.4), ti), FC.Wall("i2", (0.0, 5.8), (W, 5.8), ti),
        FC.Wall("i3", (7.0, 0.0), (7.0, 4.4), ti),
        FC.Wall("m1", (3.6, 5.8), (3.6, H), ti), FC.Wall("k1", (5.4, 5.8), (5.4, H), ti),
        FC.Wall("k2", (7.2, 5.8), (7.2, H), ti), FC.Wall("m2", (9.0, 5.8), (9.0, H), ti),
        FC.Wall("d1", (5.4, 6.6), (7.2, 6.6), ti)]                   # the DEPO's top: the well's bottom side
    plan = FC.Plan("p0", (10.0, 10.0), walls, title="ZEMİN KAT PLANI")
    for oid, kind, wall, at, width, kw in [
            ("entrance", "door", "e4", (0.125, 5.1), 1.0, dict(hinge="end", side=1)),
            ("d_salon", "door", "i1", (3.0, 4.4), 0.9, dict(hinge="start", side=-1)),
            ("d_yatak", "door", "i1", (8.5, 4.4), 0.9, dict(hinge="end", side=-1)),
            ("d_mutfak", "door", "i2", (1.8, 5.8), 0.9, dict(hinge="start", side=1)),
            ("d_banyo1", "door", "i2", (4.5, 5.8), 0.8, dict(hinge="start", side=1)),
            ("d_depo", "door", "i2", (6.3, 5.8), 0.7, dict(hinge="end", side=1)),
            ("d_banyo2", "door", "i2", (8.1, 5.8), 0.8, dict(hinge="end", side=1)),
            ("d_cocuk", "door", "i2", (10.5, 5.8), 0.9, dict(hinge="start", side=1)),
            ("w_salon1", "window", "e1", (3.5, 0.125), 2.4, {}),
            ("w_yatak1", "window", "e1", (9.5, 0.125), 1.4, {}),
            ("w_yatak2", "window", "e2", (W - 0.125, 2.1), 1.0, {}),
            ("d_yatak2", "door", "e2", (W - 0.125, 3.3), 0.9, dict(hinge="end", side=1)),
            ("w_mutfak", "window", "e3", (1.8, H - 0.125), 1.2, {}),
            ("w_cocuk1", "window", "e3", (10.5, H - 0.125), 1.4, {}),
            ("w_banyo1a", "window", "k1", (5.4, 7.2), 0.5, {}),
            ("w_banyo1b", "window", "k1", (5.4, 8.0), 0.5, {}),
            ("w_banyo2", "window", "k2", (7.2, 7.6), 0.6, {})]:
        FC.place(plan, oid, kind, wall, at, width, **kw)
    plan.labels = [FC.Label("SALON", (3.5, 2.2)), FC.Label("YATAK ODASI", (9.5, 2.6)), FC.Label("HOL", (5.0, 5.1)),
                   FC.Label("MUTFAK", (1.8, 7.4)), FC.Label("BANYO", (4.5, 7.6), height=0.15),
                   FC.Label("BANYO", (8.1, 7.0), height=0.15), FC.Label("ÇOCUK ODASI", (10.5, 7.4))]
    # the SALON's window: one frame, a mullion across it at its middle on the window layer (no wall pier)
    plan.prims.append(Prim("line", FC.L_WINDOW, [(3.5, 0.0), (3.5, r6(t))]))
    plan.truth_rooms = {(6.3, 7.7): "HAVA BOŞLUĞU", (6.3, 6.2): "DEPO"}
    return FailureProject("synthetic-36-light-well-piers", "light_well_piers", "UL367",
                          "an enclosed light well between two bathrooms, two windows of one bathroom separated by a "
                          "short pier the wall reading drops, a door and a window separated by a pier; a window with a "
                          "mullion and a closet with a door keep their reading",
                          [plan], [GROUND], BRIEF,
                          extra_truth={"weak_kind": "opening_merged", "records": []})


def project_37() -> FailureProject:
    """synthetic-37-narrow-door (23 Nov 2026; the user's C0097 on real15 L1, "Wall or column", UL371): a two-storey
    house (the stair house twice, a section naming ZEMİN KAT ±0.00 and 1. KAT +3.00). The upper floor's facade (e1) has
    a 0.50 x 0.30 m column (a closed outline on KOLON, standing 5 cm out of the wall's room face) in a 0.50 m break of
    the wall's faces inside the EBEVEYN YATAK ODASI; a wardrobe block 'GARDOLAP 2' (TEFRIS) stands against the column,
    three of its rails, 0.45 m long and 4 mm apart, across the wall at the break's jamb (real15's: HEAD read them as the
    leaf of a 0.50 m door opened at 90 degrees, a door onto nothing). The cases that keep their reading: the BANYO's
    0.55 m door with its swing drawn (a WC's), the ÇALIŞMA ODASI's 0.55 m sliding door with a door-high tag '55/210',
    the EBEVEYN YATAK ODASI's 0.90 m door drawn as two 0.45 m leaves opened at 90 degrees (no arc), and the BANYO's
    0.45 m window. Truth: no opening at the column (the facade runs on), every other opening as drawn."""
    from wenart.synthetic.failure_projects import stair_house, upper_floor

    g = stair_house("p0", (10.0, 10.0), "ZEMİN KAT PLANI")
    u = stair_house("p1", (30.0, 10.0), "1. KAT PLANI")
    upper_floor(u)
    x0, x1 = 6.15, 6.65                          # the column's break in the facade's faces
    u.openings.append(FC.Opening("c_kolon", "opening", "e1", r6((x0 + x1) / 2), r6(x1 - x0), draw_symbol=False,
                                 truth_type="absent"))
    # the column: a closed box on the wall layer filling the break and standing 5 cm out of the wall's room face (real15's
    # column with its plaster coat, read as a piece of wall material of its own); in the truth a wall of its own
    u.prims.append(Prim("poly", FC.L_WALL, [(x0, 0.0), (x1, 0.0), (x1, 0.30), (x0, 0.30)], closed=True))
    u.walls.append(FC.Wall("kc", (x0, 0.15), (x1, 0.15), 0.30, drawn=False))
    # the wardrobe against the column: its outline 0.49 x 1.12 m and three rails along its side at the break's jamb
    ward = "GARDOLAP 2"
    u.prims.append(Prim("poly", L_FURNITURE, [(r6(x0 + 0.012), 0.30), (x1, 0.30), (x1, 1.42), (r6(x0 + 0.012), 1.42)],
                        closed=True, block=ward))
    u.prims += [Prim("line", L_FURNITURE, [(r6(x0 + 0.004 * k), 0.33), (r6(x0 + 0.004 * k), 0.78)], block=ward)
                for k in range(3)]
    for op in u.openings:
        if op.id == "d_banyo":                   # a WC's narrow door, its swing drawn
            op.width = 0.55
        if op.id == "d_mutfak":                  # a narrow sliding door with its door-high tag
            op.kind, op.width = "sliding", 0.55
            u.prims.append(_tag(u, op, "55/210", (0.0, 0.40)))
        if op.id == "d_salon":                   # two narrow leaves opened at 90 degrees: one 0.90 m door
            op.draw_symbol = False
            s0, s1 = op.s - op.width / 2, op.s + op.width / 2
            y0, y1 = r6(4.4 - FC.INT_T / 2), r6(4.4 - FC.INT_T / 2 - 0.45)
            for x in (s0, s0 + 0.04, s1 - 0.04, s1):
                u.prims.append(Prim("line", FC.L_DOOR, [(r6(x), y0), (r6(x), y1)]))
        if op.id == "w_banyo":                   # a narrow window
            op.width = 0.45
    storeys = [("ZEMİN KAT", 0.0), ("1. KAT", 3.0)]
    section = FC.section_prims((50.0, 10.0), 12.0, storeys, ("ÇATI", 6.0), "A-A KESİTİ")
    levels = [TruthLevel("L0", "Zemin Kat", 0.0, 0, "p0"), TruthLevel("L1", "1. Kat", 3.0, 1, "p1")]
    return FailureProject("synthetic-37-narrow-door", "narrow_door", "UL371",
                          "a column in an upper-floor facade with a wardrobe's rails across the wall at its jamb (no "
                          "door: the wall runs on), beside a narrow WC door with its swing, a narrow sliding door with "
                          "a door-high tag, a door of two narrow leaves and a narrow window (each keeps its kind)",
                          [g, u], levels, BRIEF, sheet_prims=section,
                          extra_truth={"weak_kind": "door_invented", "records": ["C0097"]})


PROJECTS = (("opening_type", project_24), ("wall_invented", project_25), ("door_invented", project_26),
            ("stair_edge_run", project_28), ("upper_floor_door", project_29), ("fire_stair", project_30),
            ("layer_names", project_31), ("sliding_window_tag", project_32), ("double_wall", project_33),
            ("open_passage", project_34), ("grille_slot", project_35), ("light_well_piers", project_36),
            ("narrow_door", project_37))
