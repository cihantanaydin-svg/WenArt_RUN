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


def project_11() -> FailureProject:
    """synthetic-11-dimension-chains (UL261, UL296): the base flat with the notation real10 and real13 carry:
    exploded dimension chains on OLCU 0.3 m outside the outer faces (and a total chain 0.9 m out) on all four sides
    and 0.3 m inside the walls of the SALON and the ÇOCUK ODASI, each with 7 cm tick circles, slashes, extension
    lines and lengths in centimetres; and a grid of solid axis lines on AKS through the wall centres with lettered
    and numbered bubbles at both ends. None of it is a wall, a window or a room."""
    plan = base_house()
    W, H = 12.0, 9.0
    xs_bottom = [0.0, 1.2, 2.8, 4.2, 5.8, 6.925, 7.075, 8.8, 10.2, 12.0]
    xs_top = [0.0, 1.4, 2.6, 3.925, 4.075, 4.95, 5.55, 6.425, 6.575, 8.5, 9.9, 12.0]
    ys_left = [0.0, 1.5, 2.9, 4.325, 4.475, 4.6, 5.6, 5.725, 5.875, 9.0]
    ys_right = [0.0, 1.6, 2.8, 4.325, 4.475, 6.1, 7.1, 9.0]
    plan.prims += FC.dim_chain(xs_bottom, (-0.3,), "x", ext_from=-0.05)
    plan.prims += FC.dim_chain([0.0, W], (-0.9,), "x")
    plan.prims += FC.dim_chain(xs_top, (H + 0.3,), "x", ext_from=H + 0.05)
    plan.prims += FC.dim_chain([0.0, W], (H + 0.9,), "x")
    plan.prims += FC.dim_chain(ys_left, (-0.3,), "y", ext_from=-0.05)
    plan.prims += FC.dim_chain([0.0, H], (-0.9,), "y")
    plan.prims += FC.dim_chain(ys_right, (W + 0.3,), "y", ext_from=W + 0.05)
    plan.prims += FC.dim_chain([0.0, H], (W + 0.9,), "y")
    # inside chains, 0.3 m from the inner faces: along the SALON's facade and the ÇOCUK ODASI's right wall
    plan.prims += FC.dim_chain([0.25, 1.2, 2.8, 4.2, 5.8, 6.925], (0.25 + 0.3,), "x")
    plan.prims += FC.dim_chain([4.475, 6.1, 7.1, 8.75], (W - 0.25 - 0.3,), "y")
    plan.prims += FC.axis_grid([0.125, 4.0, 7.0, 11.875], [0.125, 4.4, 8.875], (-2.0, -2.0, W + 2.0, H + 2.0),
                               ["1", "2", "3", "4"], ["A", "B", "C"])
    plan.title_at = (6.0, -3.6)
    return FailureProject("synthetic-11-dimension-chains", "dimension_chains", "UL296",
                          "dimension chains outside and inside the walls with tick circles and slashes, and an axis "
                          "grid with bubbles", [plan], [GROUND], BRIEF, extra_truth={"lessons": ["UL261", "UL296"]})


def project_12() -> FailureProject:
    """synthetic-12-mirrored-halves (UL276): two flats mirrored about a 25 cm party wall (x = 7.0, the building
    14.0 x 9.0 m). The left flat carries the labels and the door swings; the right flat is its mirror image with the
    same walls, door gaps and windows but no labels and no swings (the drafter drew one flat and mirrored the walls
    only). Each flat: SALON below, YATAK ODASI, HOL and BANYO above. Truth: 8 rooms, the right flat's rooms named
    after their twins, 8 doors, 12 windows."""
    W, H = 14.0, 9.0
    plan = Plan("p0", (10.0, 10.0), outer_walls("e", W, H) + [Wall("party", (7.0, 0.0), (7.0, H), EXT_T)],
                title="ZEMİN KAT PLANI")
    left_walls = [Wall("a1", (0.0, 4.6), (7.0, 4.6), INT_T), Wall("a2", (3.0, 4.6), (3.0, H), INT_T),
                  Wall("a3", (5.0, 4.6), (5.0, H), INT_T)]
    plan.walls += left_walls + [Wall("b" + w.id[1:], (W - w.a[0], w.a[1]), (W - w.b[0], w.b[1]), w.t)
                                for w in left_walls]
    left = [("entrance", "door", "e3", (4.0, H - 0.125), 1.0, dict(hinge="start", side=1)),
            ("d_salon", "door", "a1", (4.0, 4.6), 0.9, dict(hinge="start", side=-1)),
            ("d_yatak", "door", "a2", (3.0, 6.0), 0.9, dict(hinge="start", side=1)),
            ("d_banyo", "door", "a3", (5.0, 6.0), 0.8, dict(hinge="end", side=-1)),
            ("w_salon1", "window", "e1", (2.0, 0.125), 1.6, {}),
            ("w_salon2", "window", "e1", (5.0, 0.125), 1.6, {}),
            ("w_salon3", "window", "e4", (0.125, 2.3), 1.2, {}),
            ("w_yatak1", "window", "e4", (0.125, 6.8), 1.2, {}),
            ("w_yatak2", "window", "e3", (1.5, H - 0.125), 1.2, {}),
            ("w_banyo", "window", "e3", (6.0, H - 0.125), 0.6, {})]
    wall_mirror = {"e1": "e1", "e3": "e3", "e4": "e2", "a1": "b1", "a2": "b2", "a3": "b3"}
    for oid, kind, wall, at, width, kw in left:
        FC.place(plan, oid, kind, wall, at, width, **kw)
    for oid, kind, wall, at, width, kw in left:
        FC.place(plan, oid + "_m", kind, wall_mirror[wall], (W - at[0], at[1]), width,
                 draw_symbol=(kind != "door"), **kw)
    plan.labels = [Label("SALON", (3.5, 2.3)), Label("YATAK ODASI", (1.5, 7.0)), Label("HOL", (4.0, 7.0)),
                   Label("BANYO", (6.0, 7.4))]
    plan.truth_rooms = {(W - lb.at[0], lb.at[1]): lb.text for lb in plan.labels}
    return FailureProject("synthetic-12-mirrored-halves", "mirrored_halves", "UL276",
                          "two mirrored flats about a party wall; only the left flat carries labels and door swings",
                          [plan], [GROUND], BRIEF)


def stair_house(key: str, origin, title: Optional[str], *, winders: int = 0, numbers: bool = False,
                flight1: int = 9, flight2: int = 9, going: float = 0.25) -> Plan:
    """The base flat with its L-shaped top-right room turned into the stair hall (MERDİVEN): a U stair of two
    flights along x in the box x 8.7..11.8, y 5.95..8.8, turning at the right end (a landing, or winders)."""
    plan = base_house(key, origin, title)
    _relabel(plan, {"ÇOCUK ODASI": "MERDİVEN"})
    for lb in plan.labels:
        if lb.text == "MERDİVEN":
            lb.at = (7.6, 7.4)
    prims, truth = FC.u_stair(8.7, 5.95, 11.8, 8.8, going, flight1, flight2, winders=winders, numbers=numbers)
    plan.prims += prims
    kind = "u_winder" if winders else "u_landing"
    risers = truth["treads"] + (0 if winders else 1)
    plan.stairs.append(StairTruth("s_{L}_001", kind, (10.25, 7.375), risers, extra=truth))
    return plan


def project_13() -> FailureProject:
    """synthetic-13-typical-floor (UL278, UL303): one sheet with the ground floor plan (ZEMİN KAT PLANI), one plan
    titled '1-6. NORMAL KAT PLANI' standing for the six storeys above it, and a section (A-A KESİTİ) naming the
    storeys at their level marks (ZEMİN KAT ±0.00, 1. NORMAL KAT +3.00 ... 6. NORMAL KAT +18.00, ÇATI +21.00).
    Both plans carry the U stair. The typical plan has a window where the ground floor has its entrance. Truth:
    7 levels, L1 to L6 the typical plan at 3.00 m steps."""
    g = stair_house("p0", (10.0, 10.0), "ZEMİN KAT PLANI")
    t = stair_house("p1", (30.0, 10.0), "1-6. NORMAL KAT PLANI")
    _drop(t, "entrance")
    t.openings.append(Opening("w_hol", "window", "e4", 3.9, 1.0))
    storeys = [("ZEMİN KAT", 0.0)] + [(f"{k}. NORMAL KAT", 3.0 * k) for k in range(1, 7)]
    section = FC.section_prims((50.0, 10.0), 12.0, storeys, ("ÇATI", 21.0), "A-A KESİTİ")
    levels = [TruthLevel("L0", "Zemin Kat", 0.0, 0, "p0")] + [
        TruthLevel(f"L{k}", f"{k}. Normal Kat", 3.0 * k, k, "p1") for k in range(1, 7)]
    return FailureProject("synthetic-13-typical-floor", "typical_floor", "UL278",
                          "a typical plan standing for six floors and a section naming the storeys at level marks",
                          [g, t], levels, BRIEF, sheet_prims=section,
                          extra_truth={"lessons": ["UL278", "UL303"], "roof": {"label": "ÇATI", "elevation": 21.0},
                                       "typical_plan": {"title": "1-6. NORMAL KAT PLANI",
                                                        "levels": [f"L{k}" for k in range(1, 7)]}})


def upper_floor(plan: Plan) -> None:
    """The upper floor of a two-storey house: bedrooms instead of the living rooms, a window for the entrance."""
    _relabel(plan, {"SALON": "EBEVEYN YATAK ODASI", "MUTFAK": "ÇALIŞMA ODASI"})
    _drop(plan, "entrance")
    plan.openings.append(Opening("w_hol", "window", "e4", 3.9, 1.0))


def project_14() -> FailureProject:
    """synthetic-14-elevation-title (UL271): two plans of a two-storey house stacked on one sheet, the ground floor
    plan titled 'ZEMİN KAT PLANI' on top and below it a plan titled only by its elevation, '+3.00 KOTU KAT PLANI'
    (no floor word). Both carry the U stair. Truth: L0 Zemin Kat ±0.00 and L1 at +3.00."""
    g = stair_house("p0", (10.0, 26.0), "ZEMİN KAT PLANI")
    u = stair_house("p1", (10.0, 10.0), "+3.00 KOTU KAT PLANI")
    upper_floor(u)
    levels = [TruthLevel("L0", "Zemin Kat", 0.0, 0, "p0"), TruthLevel("L1", "1. Kat", 3.0, 1, "p1")]
    return FailureProject("synthetic-14-elevation-title", "elevation_title", "UL271",
                          "a plan titled only by its elevation under a titled ground floor plan",
                          [g, u], levels, BRIEF)


def project_15() -> FailureProject:
    """synthetic-15-winder-stair (UL282): the base flat with a U stair in the stair hall: six straight treads, five
    winders round the turn (radial lines from the well's end), six straight treads back, every tread numbered 1 to 17
    on the stair layer, the walking line with its arrow. Truth: one stair, 17 risers, its three arms."""
    plan = stair_house("p0", (10.0, 10.0), "ZEMİN KAT PLANI", winders=5, numbers=True, flight1=6, flight2=6,
                       going=0.27)
    return FailureProject("synthetic-15-winder-stair", "winder_stair", "UL282",
                          "a U stair with numbered treads 1-17 and winders at the turn", [plan], [GROUND], BRIEF)


def project_16() -> FailureProject:
    """synthetic-16-open-recess (UL313): a 1.2 m wide, 3.0 m deep recess between the two bedrooms of the top row,
    open to the facade (the outline steps in round it), the bedrooms' windows opening onto its sides, no label and
    no door inside. Truth: 6 rooms; the recess is open air, not a room."""
    W, H = 12.0, 9.0
    outline = [(0.0, 0.0), (W, 0.0), (W, H), (8.1, H), (8.1, 6.0), (6.9, 6.0), (6.9, H), (0.0, H)]
    walls = FC.outline_walls("e", outline) + [
        Wall("i1", (0.0, 4.4), (W, 4.4), INT_T), Wall("i2", (0.0, 5.8), (8.5, 5.8), INT_T),
        Wall("i3", (7.0, 0.0), (7.0, 4.4), INT_T), Wall("i4", (3.6, 5.8), (3.6, H), INT_T),
        Wall("i6", (8.5, 4.4), (8.5, 5.875), INT_T)]
    plan = Plan("p0", (10.0, 10.0), walls, title="ZEMİN KAT PLANI")
    for oid, kind, wall, at, width, kw in [
            ("entrance", "door", "e8", (0.125, 5.1), 1.0, dict(hinge="end", side=1)),
            ("d_salon", "door", "i1", (3.0, 4.4), 0.9, dict(hinge="start", side=-1)),
            ("d_yatak", "door", "i1", (7.8, 4.4), 0.9, dict(hinge="end", side=-1)),
            ("d_mutfak", "door", "i2", (1.8, 5.8), 0.9, dict(hinge="start", side=1)),
            ("d_ebeveyn", "door", "i2", (5.0, 5.8), 0.9, dict(hinge="end", side=1)),
            ("d_cocuk", "door", "i6", (8.5, 5.1), 0.9, dict(hinge="start", side=-1)),
            ("w_salon1", "window", "e1", (2.0, 0.125), 1.6, {}), ("w_salon2", "window", "e1", (5.0, 0.125), 1.6, {}),
            ("w_salon3", "window", "e8", (0.125, 2.2), 1.4, {}), ("w_yatak1", "window", "e1", (9.5, 0.125), 1.4, {}),
            ("w_yatak2", "window", "e2", (W - 0.125, 2.2), 1.2, {}),
            ("w_mutfak", "window", "e7", (1.8, H - 0.125), 1.2, {}),
            ("w_ebeveyn1", "window", "e7", (5.2, H - 0.125), 1.4, {}),
            ("w_ebeveyn2", "window", "e6", (6.775, 7.6), 0.9, {}),
            ("w_cocuk1", "window", "e4", (8.225, 7.6), 0.9, {}),
            ("w_cocuk2", "window", "e3", (10.0, H - 0.125), 1.4, {}),
            ("w_cocuk3", "window", "e2", (W - 0.125, 6.6), 1.0, {})]:
        FC.place(plan, oid, kind, wall, at, width, **kw)
    plan.labels = [Label("SALON", (3.5, 2.2)), Label("YATAK ODASI", (9.5, 2.6)), Label("HOL", (5.0, 5.1)),
                   Label("MUTFAK", (1.8, 7.4)), Label("EBEVEYN ODASI", (5.1, 7.4), height=0.2),
                   Label("ÇOCUK ODASI", (10.1, 7.4))]
    recess = [[6.9, 6.0], [8.1, 6.0], [8.1, H], [6.9, H]]
    return FailureProject("synthetic-16-open-recess", "open_recess", "UL313",
                          "a narrow recess between two bedrooms, open to the facade, windows onto it, no label",
                          [plan], [GROUND], BRIEF,
                          extra_truth={"open_air": [{"kind": "recess", "polygon": recess, "width": 1.2, "depth": 3.0}]})


def project_17() -> FailureProject:
    """synthetic-17-garage-lift (UL320, UL306): the base flat with the bottom-right bedroom turned into a GARAJ with
    a 3.4 m opening in the outer wall (the gap and the overhead door's dashed line on KAPI) and a door to the
    corridor, and an ASANSÖR shaft (1.65 x 1.75 m inside, the diagonal cross on ASANSOR) at the corridor's end with
    a sliding landing door. Truth: 7 rooms (GARAJ garage, ASANSÖR shaft), the garage door and the lift door."""
    plan = base_house()
    _relabel(plan, {"YATAK ODASI": "GARAJ"})
    _drop(plan, "w_yatak1", "w_yatak2")
    plan.walls = [w for w in plan.walls if w.id != "i6"] + [
        Wall("i6", (8.5, 4.4), (8.5, 6.375), INT_T), Wall("i7", (10.3, 4.4), (10.3, 6.375), INT_T),
        Wall("i8", (8.5, 6.3), (10.3, 6.3), INT_T)]
    plan.openings.append(Opening("garage", "garage", "e1", 9.5, 3.4))
    plan.openings.append(Opening("lift", "sliding", "i6", 0.7, 0.9, truth_type="door"))
    x0, y0, x1, y1 = 8.575, 4.475, 10.225, 6.225
    plan.prims += [Prim("line", "ASANSOR", [(x0 + 0.1, y0 + 0.1), (x1 - 0.1, y1 - 0.1)]),
                   Prim("line", "ASANSOR", [(x0 + 0.1, y1 - 0.1), (x1 - 0.1, y0 + 0.1)]),
                   Prim("poly", "ASANSOR", [(x0 + 0.1, y0 + 0.1), (x1 - 0.1, y0 + 0.1), (x1 - 0.1, y1 - 0.1),
                                            (x0 + 0.1, y1 - 0.1)], closed=True)]
    plan.labels.append(Label("ASANSÖR", (9.4, 5.4), height=0.18))
    for lb in plan.labels:
        if lb.text == "ÇOCUK ODASI":
            lb.at = (9.25, 7.6)
    return FailureProject("synthetic-17-garage-lift", "garage_lift", "UL320",
                          "a garage with a 3.4 m opening to the outside and a lift shaft with a landing door",
                          [plan], [GROUND], BRIEF, extra_truth={"lessons": ["UL320", "UL306"]})


def project_18() -> FailureProject:
    """synthetic-18-sheet-frame (UL268): one sheet frame (PAFTA, 47 x 18 m at drawing scale, a title block at its
    bottom right) holding three titled drawings only 1.5 m apart: the ground floor plan, the first floor plan
    (1. KAT PLANI) and a section (A-A KESİTİ) naming the two storeys and the roof. Both plans carry the U stair.
    Truth: two levels, three drawings."""
    g = stair_house("p0", (2.0, 4.0), "ZEMİN KAT PLANI")
    u = stair_house("p1", (15.5, 4.0), "1. KAT PLANI")
    upper_floor(u)
    sheet = FC.section_prims((30.5, 4.0), 12.0, [("ZEMİN KAT", 0.0), ("1. KAT", 3.0)], ("ÇATI", 6.0), "A-A KESİTİ")
    sheet += [Prim("poly", L_FRAME, [(0.0, 0.0), (47.0, 0.0), (47.0, 18.0), (0.0, 18.0)], closed=True),
              Prim("poly", L_FRAME, [(38.0, 0.0), (47.0, 0.0), (47.0, 3.0), (38.0, 3.0)], closed=True),
              Prim("text", L_TEXT, [(42.5, 2.2)], text="KONUT PROJESİ", height=0.4),
              Prim("text", L_TEXT, [(42.5, 1.3)], text="MİMARİ UYGULAMA PROJESİ", height=0.25),
              Prim("text", L_TEXT, [(42.5, 0.5)], text="PAFTA NO: M-01", height=0.25)]
    levels = [TruthLevel("L0", "Zemin Kat", 0.0, 0, "p0"), TruthLevel("L1", "1. Kat", 3.0, 1, "p1")]
    return FailureProject("synthetic-18-sheet-frame", "sheet_frame", "UL268",
                          "one sheet frame holding three titled drawings close together",
                          [g, u], levels, BRIEF,
                          extra_truth={"drawings": [{"title": "ZEMİN KAT PLANI", "class": "floor_plan"},
                                                    {"title": "1. KAT PLANI", "class": "floor_plan"},
                                                    {"title": "A-A KESİTİ", "class": "section"}]})


def failure_projects() -> list[FailureProject]:
    return [project_08(), project_09(), project_10(), project_11(), project_12(), project_13(), project_14(),
            project_15(), project_16(), project_17(), project_18()]
