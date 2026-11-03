"""3 Nov 2026, the real09 attic (user: "each duplex flat has its inner stair (winders 1-17) and a 'galeri' void over the
floor below ... the attic must sit over its stair core"): a plan with no axis grid and no lift is placed by its stairs
drawn on a stair layer; the reading check measures stacking by the stair lines and leaves furniture and sanitary arcs
out (real07); voids labelled on a plan are openings of the floor slab, and a void inside a room does not name the
room. CPU only, pure."""
from __future__ import annotations

from types import SimpleNamespace

import numpy as np
from shapely.geometry import Polygon

from wenart import building as B
from wenart.ingest.generic import layer_names as LN
from wenart.ingest.generic import voids as VD
from wenart.ingest.generic.model import Stroke, TextRun
from wenart.reading_check import NOT_ANCHOR_ROLES, stacking, stair_line_gap
from wenart.sheets import register as RG
from wenart.sheets import to_building as TB


def _u_stair(dx=0.0, dy=0.0):
    """Stair segments (metres) of a U stair: 7 tread lines per flight 0.28 m apart, 1.0 m wide flights, a 0.2 m eye,
    and the flights' sides."""
    segs = []
    for k in range(7):
        x = 0.28 * k + dx
        segs.append(((x, dy), (x, 1.0 + dy)))
        segs.append(((x, 1.2 + dy), (x, 2.2 + dy)))
    for y in (0.0, 1.0, 1.2, 2.2):
        segs.append(((dx, y + dy), (1.68 + dx, y + dy)))
    return np.array(segs, dtype=float)


def _mirrored_pair(dx=0.0, dy=0.0):
    """Two such stairs 6 m apart (a mirrored twin, an ambiguity the fit must see through when both are drawn)."""
    return np.vstack([_u_stair(dx, dy), _u_stair(dx + 6.0, dy)])


# ------------------------------------------------------------------ stair-layer registration
def test_a_plan_is_placed_by_its_stair_lines():
    target = _mirrored_pair(10.0, 20.0)
    moving = RG.sample_segments(_mirrored_pair(0.0, 0.0))
    fit = RG.stair_layer_fit(target, moving)
    assert fit is not None and fit["share"] > 0.9
    assert abs(fit["shift"][0] - 10.0) < 0.005 and abs(fit["shift"][1] - 20.0) < 0.005
    assert fit["second"] < RG.STAIR_LAYER_UNIQUE                     # the twin 6 m away fits half of the lines only


def test_a_single_stair_seen_on_one_twin_is_ambiguous_or_placed():
    """One stair over a mirrored pair: two equally good places, so the fit is ambiguous (``second`` near 1)."""
    fit = RG.stair_layer_fit(_mirrored_pair(10.0, 20.0), RG.sample_segments(_u_stair(0.0, 0.0)))
    assert fit is not None and fit["second"] >= RG.STAIR_LAYER_UNIQUE


def test_too_few_stair_lines_give_no_fit():
    assert RG.stair_layer_fit(_u_stair(), np.zeros((10, 2))) is None
    assert RG.stair_layer_fit(np.zeros((0, 2, 2)), RG.sample_segments(_u_stair())) is None


def test_the_check_measures_stacking_by_the_stair_lines():
    lower = _mirrored_pair(5.0, 5.0)
    assert stair_line_gap(_mirrored_pair(5.0, 5.0), lower) < 0.005
    gap = stair_line_gap(_mirrored_pair(5.0, 1.3), lower)            # the attic 3.70 m off
    assert gap is not None and abs(gap - 3.7) < 0.005
    anchors = {"L0": {"axes": {}, "stairs": [], "stair_lines": lower},
               "L1": {"axes": {}, "stairs": [], "stair_lines": _mirrored_pair(5.0, 5.0)},
               "L2": {"axes": {}, "stairs": [], "stair_lines": _mirrored_pair(5.0, 1.3)}}
    found = stacking(anchors, "L0", {"L0": 0, "L1": 1, "L2": 2})
    assert [f["level_id"] for f in found] == ["L2"] and found[0]["severity"] == "critical"


def test_furniture_and_sanitary_arcs_are_no_stacking_anchors():
    assert LN.layer_role("S-TEF") in NOT_ANCHOR_ROLES                # sıhhi tefriş (real07)
    assert LN.layer_role("TEFRIŞ") in NOT_ANCHOR_ROLES
    assert LN.layer_role("vitrifiye") in NOT_ANCHOR_ROLES
    assert LN.layer_role("merdiven") not in NOT_ANCHOR_ROLES


# ------------------------------------------------------------------ voids
def test_void_words():
    for t in ("galeri", "GALERİ BOŞLUĞU", "Boşluk", "void", "Open to below", "Luftraum", "double-height"):
        assert B.is_void_label(t), t
    for t in ("Galerie", "Salon", "Oturma O.", "Banyo", "avoid"):
        assert not B.is_void_label(t), t
    assert B.room_type_for("galeri") == "shaft"


def _text(k, s, x, y):
    return TextRun(id=f"TEXT:{k}", text=s, box=(x - 0.2, y - 0.06, x + 0.2, y + 0.06), height=0.12)


def _rect(k0, x0, y0, x1, y1, layer="merdiven"):
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    return [Stroke(id=f"LINE:{k0 + i}", kind="line", pts=[a, b], layer=layer) for i, (a, b) in
            enumerate(zip(pts, pts[1:]))]


def test_a_void_label_closes_its_drawn_outline():
    strokes = _rect(1, 0.0, 0.0, 3.5, 2.5, "duvar") + _rect(10, 0.2, 0.2, 1.3, 1.55)
    voids = VD.read_voids([_text(1, "galeri", 0.7, 0.9), _text(2, "Oda", 2.5, 2.0)], strokes)
    assert len(voids) == 1 and voids[0]["polygon"] and abs(voids[0]["area_m2"] - 1.485) < 0.02
    # two labels of one void give one void; a label with no outline around it builds nothing
    two = VD.read_voids([_text(1, "galeri", 0.7, 0.9), _text(3, "galeri", 0.8, 1.2)], strokes)
    assert len([v for v in two if v["polygon"]]) == 1
    none = VD.read_voids([_text(4, "galeri", 10.0, 10.0)], strokes)
    assert none and none[0]["polygon"] is None


def test_a_void_inside_a_room_does_not_name_the_room():
    voids = [{"label": "galeri", "polygon": [[0.2, 0.2], [1.3, 0.2], [1.3, 1.55], [0.2, 1.55]]}]
    room = Polygon([(0, 0), (3.5, 0), (3.5, 2.5), (0, 2.5)])
    block = SimpleNamespace(name="galeri", anchor=(0.7, 0.9))
    other = SimpleNamespace(name="Salon", anchor=(2.5, 2.0))
    kept, notes = VD.room_labels([block, other], voids, [room])
    assert kept == [other] and notes
    # a void that is its whole room keeps the label (the room is the void)
    whole = [{"label": "galeri", "polygon": [[0, 0], [3.5, 0], [3.5, 2.5], [0, 2.5]]}]
    kept, _ = VD.room_labels([block], whole, [room])
    assert kept == [block]


def test_voids_are_openings_of_their_level_floor_slab():
    rooms = [{"id": "r_L3_galeri", "level_id": "L3", "label_raw": "GALERİ", "label": "Galeri",
              "polygon": [[0, 0], [2, 0], [2, 2], [0, 2]]},
             {"id": "r_L3_salon", "level_id": "L3", "label_raw": "SALON", "label": "Salon",
              "polygon": [[2, 0], [6, 0], [6, 2], [2, 2]]}]
    voids = [{"level_id": "L3", "polygon": [[3, 0.5], [4, 0.5], [4, 1.5], [3, 1.5]], "reason": "r", "entity": "T:1"},
             {"level_id": "L2", "polygon": [[3, 0.5], [4, 0.5], [4, 1.5], [3, 1.5]]}]
    out = TB.void_openings("L3", rooms, voids)
    assert [o["kind"] for o in out] == ["void", "void"] and all(o["source"] == "drawn" for o in out)
    assert {o.get("room_id") for o in out} == {None, "r_L3_galeri"}


def test_an_axis_word_decides_before_the_sanitary_words():
    assert LN.layer_role("00_VİTRİFİYE AKS") == "axis"           # real03: the sanitary ware's axis lines
    assert LN.layer_role("vitrifiye") == "sanitary"


def test_the_sheets_review_reasons_are_critical(tmp_path):
    """real10 structure run 20261103-073227-full: sheets.json failed its schema; the pod's sheets stage stopped."""
    import json

    from wenart import reading_check as RC

    (tmp_path / "building.json").write_text(json.dumps({"levels": [], "walls": [], "rooms": [], "warnings": []}))
    (tmp_path / "sheets.json").write_text(json.dumps({"needs_review": [{"region": None, "file": None,
                                                                        "reason": "sheets.json failed schema "
                                                                                  "validation"}],
                                                      "warnings": ["schema: regions/1/registration/method: x"]}))
    res = RC.check(tmp_path)
    assert res["verdict"] != "ready"
    assert any(f["check"] == "RC6" and f["severity"] == "critical" for f in res["findings"])


# ------------------------------------------------------------------ numbered treads (real09's duplex stairs)
def _numbered_u():
    """A U stair with winders: arm 1 rises north (numbers 1-4 at x 0.4), winders 5-11 across the top (y 1.6),
    arm 2 descends south (12-16 at x 2.0); tread lines across each arm (0.8 m wide)."""
    pts = [(0.4, 0.2 + 0.25 * k) for k in range(4)]                       # 1-4
    pts += [(0.55, 1.25), (0.75, 1.45), (1.0, 1.6), (1.2, 1.62), (1.4, 1.6), (1.65, 1.45), (1.85, 1.25)]   # 5-11
    pts += [(2.0, 0.95 - 0.25 * k) for k in range(5)]                     # 12-16
    texts = [TextRun(id=f"TEXT:{k + 1}", text=str(k + 1), box=(x - 0.03, y - 0.05, x + 0.03, y + 0.05), height=0.1)
             for k, (x, y) in enumerate(pts)]
    strokes = []
    for k in range(5):
        y = 0.075 + 0.25 * k
        strokes.append(Stroke(id=f"LINE:a{k}", kind="line", pts=[(0.0, y), (0.8, y)], layer="merdiven"))
    for k in range(6):
        y = 1.075 - 0.25 * k
        strokes.append(Stroke(id=f"LINE:b{k}", kind="line", pts=[(1.6, y), (2.4, y)], layer="merdiven"))
    return texts, strokes


def test_numbered_treads_read_a_u_stair_with_winders():
    from wenart.ingest.generic import stair_numbers as SN

    texts, strokes = _numbered_u()
    found = SN.chains(texts)
    assert len(found) == 1 and [c[0] for c in found[0]] == list(range(1, 17))
    st = SN.stair_of(found[0], strokes)
    assert st and not st.get("skip")
    assert st["turn"] == "U" and [f["lines"] for f in st["flights"]] == [4, 5] and st["winders"] == 7
    assert all(abs(f["width"] - 0.8) < 0.01 for f in st["flights"])
    assert st["direction"][1] > 0.9                                         # it rises from 1 northwards (drawn)
    land = Polygon(st["landing"]["polygon"]) if st["landing"] else None
    assert land is not None and land.bounds[1] >= 1.0                       # the band beyond the arms, not the eye
    assert land.bounds[0] <= 0.05 and land.bounds[2] >= 2.35                # across the whole stair
    assert abs(st["polygon"].minimum_rotated_rectangle.area - st["polygon"].area) < 1e-6   # a rectangle ...
    assert all(abs(round(c, 4) % 1.0 - 0.0) < 1 for c in st["polygon"].bounds)
    cs = list(st["polygon"].exterior.coords)
    assert all(abs(a[0] - b[0]) < 1e-6 or abs(a[1] - b[1]) < 1e-6 for a, b in zip(cs, cs[1:]))   # ... not tilted


def test_a_numbered_stair_replaces_its_untyped_parts():
    from wenart.ingest.generic import stair_numbers as SN
    from wenart.ingest.model import FurnitureItem

    texts, strokes = _numbered_u()
    part = FurnitureItem(type="unknown", type_raw=None, center=(1.2, 0.8), size=(2.4, 1.4), rotation_deg=0.0,
                         front_deg=None, box=[0, 0, 1, 1], entity="LINE:a0", evidence={})
    cand = {"footprint": {"center": (1.2, 0.8)}, "item": part}
    notes: list = []
    pieces, cands, polys = SN.apply([], [cand], texts, strokes, 1.0, "x.dwg", 1, notes)
    assert [p.type for p in pieces] == ["stair"] and cands == [] and len(polys) == 1
    st = pieces[0].details["stair"]
    assert st["direction_assumed"] is False and st["steps_drawn"] == 16 and st["winders"] == 7
    # a stair piece that already holds the numbers keeps the stair rule's reading
    again, _c, polys2 = SN.apply(pieces, [], texts, strokes, 1.0, "x.dwg", 1, notes)
    assert len(again) == 1 and not polys2


def test_too_short_a_number_run_is_no_stair():
    from wenart.ingest.generic import stair_numbers as SN

    texts = [TextRun(id=f"T:{k}", text=str(k), box=(0.25 * k, 0, 0.25 * k + 0.05, 0.1), height=0.1)
             for k in range(1, 5)]
    assert SN.chains(texts) == []


# ------------------------------------------------------------------ outdoor outlines: hair-line gaps (real09)
def test_a_balcony_closes_where_its_lines_touch_the_facade_by_a_hair():
    """The left attic terrace: its balcony line ran 0.4 mm beside the facade's edge and its inner line ended a
    fraction of a millimetre short of the facade; its mirror twin closed."""
    from wenart.levels import outdoor as OD

    facade = Polygon([(4.8, 0.086), (8.0, 0.086), (8.0, 6.0), (0.0298, 6.0), (0.0298, 3.913), (4.8, 3.913)])
    lines = [{"id": "a", "pts": [(0.0302, 0.12), (0.0302, 3.89)], "layer": "balkon", "closed": False},
             {"id": "b", "pts": [(4.7999, 0.12), (0.0302, 0.12)], "layer": "balkon", "closed": False},
             {"id": "c", "pts": [(0.2302, 3.89), (0.2302, 0.32)], "layer": "balkon", "closed": False},
             {"id": "d", "pts": [(4.7999, 0.32), (0.2302, 0.32)], "layer": "balkon", "closed": False}]
    rec = OD.close_region((2.9, 2.4), lines, facade, None)
    assert rec is not None and 15.0 < rec["area_m2"] < 17.5


def test_a_void_marked_with_its_diagonals_closes_its_box():
    """real07's GALERİ: the box with an X; the label stands in one triangle of the cross."""
    strokes = _rect(1, 0.0, 0.0, 2.25, 1.6) + [
        Stroke(id="LINE:90", kind="line", pts=[(0.0, 0.0), (2.25, 1.6)], layer="merdiven"),
        Stroke(id="LINE:91", kind="line", pts=[(0.0, 1.6), (2.25, 0.0)], layer="merdiven")]
    voids = VD.read_voids([_text(1, "GALERİ", 1.1, 0.35)], strokes)
    assert voids and voids[0]["polygon"] and abs(voids[0]["area_m2"] - 3.6) < 0.05
    assert "diagonals" in voids[0]["reason"]


# ------------------------------------------------------------------ real10's typical floor (the user's markings)
def _w(s, e, t=0.2):
    from types import SimpleNamespace as NS
    return NS(start=s, end=e, thickness=t, box=[0, 0, 0, 0], evidence={"file": "x.dwg", "entity": "W"}, entity="W",
              status="verified", inferred=False, exterior=False)


def test_a_hall_and_a_salon_split_where_the_walls_stop_offset():
    """The flat's inside hall (a corridor) runs into the salon between a wall stub's end and a kitchen wall's corner,
    0.65 m offset: a separator from the stub's free end to the nearest wall keeps 'antre' and 'salon' apart."""
    from shapely.geometry import Point as P

    from wenart.ingest.generic import topology as TP

    walls = [_w((0, 0), (8, 0)), _w((8, 0), (8, 8)), _w((8, 8), (0, 8)), _w((0, 8), (0, 0)),
             _w((3, 8), (3, 3.5)),                    # the hall's wall stub, free end at (3, 3.5)
             _w((4.2, 0), (4.2, 2.8)), _w((4.2, 2.8), (8, 2.8))]   # the kitchen block, its corner at (4.2, 2.8)
    gap_log = [{"kind": "free_end", "point": (3.0, 3.5), "direction": (0.0, -1.0), "thickness": 0.2, "wall": 4,
                "gap_class": "none"}]
    blocks = [SimpleNamespace(name="antre", anchor=(3.6, 6.0), exterior=False),
              SimpleNamespace(name="salon", anchor=(1.5, 2.0), exterior=False)]
    seps, log = TP.separators(walls, [], gap_log, blocks, [])
    assert seps, log
    fs = TP.faces(walls, [], [s.line for s in seps])
    holder = [next(k for k, f in enumerate(fs) if f.contains(P(b.anchor))) for b in blocks]
    assert holder[0] != holder[1]


def test_the_separator_of_the_named_half_is_mirrored():
    from wenart.ingest.generic import topology as TP

    walls = [_w((0, 0), (16, 0)), _w((16, 0), (16, 8)), _w((16, 8), (0, 8)), _w((0, 8), (0, 0)), _w((8, 0), (8, 8)),
             _w((3, 8), (3, 3.5)), _w((4.2, 0), (4.2, 2.8)), _w((4.2, 2.8), (8, 2.8)),
             _w((13, 8), (13, 3.5)), _w((11.8, 0), (11.8, 2.8)), _w((11.8, 2.8), (8, 2.8))]
    gap_log = [{"kind": "free_end", "point": (3.0, 3.5), "direction": (0.0, -1.0), "thickness": 0.2, "wall": 5,
                "gap_class": "none"}]
    blocks = [SimpleNamespace(name="antre", anchor=(3.6, 6.0), exterior=False),
              SimpleNamespace(name="salon", anchor=(1.5, 2.0), exterior=False)]
    seps, log = TP.separators(walls, [], gap_log, blocks, [], axis=("x", 8.0))
    assert len(seps) == 2 and any(e.get("kind") == "mirror_twin" for e in log)
    xs = sorted(round(s.center[0], 1) for s in seps)
    assert xs[0] < 8 < xs[1] and abs((xs[0] + xs[1]) / 2 - 8.0) < 0.05


def test_the_room_the_stair_core_opens_into_is_the_shared_hall():
    from wenart.ingest import twins as TW

    rooms = [{"id": "core", "level_id": "L0", "label": "Merdiven", "label_raw": None, "room_type": "stair",
              "label_inferred": {"method": "stair_core"}, "polygon": [[0, 2], [3, 2], [3, 5], [0, 5]]},
             {"id": "land", "level_id": "L0", "label": "Oda", "label_raw": None, "room_type": "hall",
              "polygon": [[0, 0], [3, 0], [3, 1.8], [0, 1.8]]},
             {"id": "inner", "level_id": "L0", "label": "Oda", "label_raw": None, "room_type": "hall",
              "polygon": [[-2, 2], [-0.2, 2], [-0.2, 5], [-2, 5]]},
             {"id": "s", "level_id": "L0", "label": "Salon", "label_raw": "SALON", "room_type": "living",
              "polygon": [[5, 0], [8, 0], [8, 3], [5, 3]]}]
    notes = TW.shared_halls(rooms, [{"level_id": "L0", "center": [1.5, 1.9], "type": "opening"}])
    assert notes and [r["label"] for r in rooms] == ["Merdiven", "Kat Holü", "Oda", "Salon"]


def test_the_stair_core_takes_the_room_holding_most_of_the_stair_in_the_plans_language():
    from wenart.ingest import twins as TW

    rooms = [{"id": "core", "level_id": "L0", "label": "Room", "label_raw": None, "room_type": "living",
              "polygon": [[0, 2], [3, 2], [3, 5], [0, 5]]},
             {"id": "hall", "level_id": "L0", "label": "Oda", "label_raw": None, "room_type": "hall",
              "polygon": [[0, 0], [3, 0], [3, 2], [0, 2]]},
             {"id": "s", "level_id": "L0", "label": "Salon", "label_raw": "SALON", "room_type": "living",
              "polygon": [[5, 0], [8, 0], [8, 3], [5, 3]]}]
    stairs = [{"type": "stair", "level_id": lv, "footprint": {"center": [1.5, 2.9], "size": [2.7, 2.4],
                                                              "rotation_deg": 0}} for lv in ("L-1", "L0", "L1")]
    TW.stair_cores(rooms, stairs)
    assert rooms[0]["label"] == "Merdiven" and rooms[0]["room_type"] == "stair" and rooms[1]["label"] == "Oda"


def test_a_small_room_with_one_door_and_no_window_is_a_closet():
    """real10 (user: "red sections are small closets (small rooms with a door to store some stuff inside)")."""
    from wenart.ingest.generic import topology as TP
    from wenart.ingest.model import OpeningItem

    walls = [_w((0, 0), (1.0, 0)), _w((1.0, 0), (1.0, 1.6)), _w((1.0, 1.6), (0, 1.6)), _w((0, 1.6), (0, 0))]
    door = OpeningItem(kind="door", width=0.7, center=(0.5, 0.0), rotation_deg=0.0, box=[0, 0, 1, 1], entity="D",
                       evidence={})
    face = Polygon([(0.1, 0.1), (0.9, 0.1), (0.9, 1.5), (0.1, 1.5)])
    rt, why = TP.unlabelled_face_type(face, walls, [door])
    assert rt == "storage" and why.startswith("closet") and TP.closet_label(why, True) == "Depo"
    win = OpeningItem(kind="window", width=0.6, center=(0.5, 1.6), rotation_deg=0.0, box=[0, 0, 1, 1], entity="W",
                      evidence={})
    assert TP.unlabelled_face_type(face, walls, [door, win])[0] == "unknown"   # a window: no closet


def test_the_main_entrance_is_the_door_reached_from_the_core_nearest_the_ground():
    """real10 (user: "this should be the main entrance to the building"): the 1st basement's 2.40 m double front door
    into the passage the shared hall opens onto, not a bedroom's garden door nor a door a storey up."""
    from wenart.levels import model as LM

    def room(rid, lid, label, rtype, poly, method=None):
        r = {"id": rid, "level_id": lid, "label": label, "label_raw": None, "room_type": rtype, "polygon": poly}
        if method:
            r["label_inferred"] = {"method": method}
        return r

    b = {"rooms": [room("core", "L-1", "Merdiven", "stair", [[4, 6], [7, 6], [7, 9], [4, 9]], "stair_core"),
                   room("hall", "L-1", "Kat Holü", "hall", [[4, 4], [7, 4], [7, 5.8], [4, 5.8]], "shared_hall"),
                   room("pass", "L-1", "Oda", "hall", [[5, 0.2], [6.5, 0.2], [6.5, 3.8], [5, 3.8]]),
                   room("bed", "L-1", "Yatak", "bedroom", [[0, 6], [3, 6], [3, 9], [0, 9]]),
                   room("core0", "L0", "Merdiven", "stair", [[4, 6], [7, 6], [7, 9], [4, 9]], "stair_core"),
                   room("hall0", "L0", "Kat Holü", "hall", [[4, 4], [7, 4], [7, 5.8], [4, 5.8]], "shared_hall")],
         "openings": [{"id": "o1", "level_id": "L-1", "center": [5.5, 5.9], "type": "opening"},
                      {"id": "o2", "level_id": "L-1", "center": [5.7, 3.9], "type": "opening"},
                      {"id": "front", "level_id": "L-1", "center": [5.7, 0.1], "type": "door", "operation": "double"},
                      {"id": "garden", "level_id": "L-1", "center": [1.5, 9.1], "type": "door", "operation": "swing"},
                      {"id": "up", "level_id": "L0", "center": [5.5, 3.95], "type": "door", "operation": "sliding"}]}
    usable = [{"door_id": "front", "level_id": "L-1", "room_id": "pass", "width": 2.4, "outward": [0, -1], "rise": 0.1},
              {"door_id": "garden", "level_id": "L-1", "room_id": "bed", "width": 0.8, "outward": [0, 1], "rise": 0.1},
              {"door_id": "up", "level_id": "L0", "room_id": "hall0", "width": 2.3, "outward": [0, -1], "rise": 3.0}]
    main, why = LM.main_entrance(b, usable, [])
    assert main["door_id"] == "front" and "stair core" in why


def test_the_shared_hall_touches_the_lift_where_the_floor_has_one():
    from wenart.ingest import twins as TW

    rooms = [{"id": "core", "level_id": "L0", "label": "Merdiven", "label_raw": None, "room_type": "stair",
              "label_inferred": {"method": "stair_core"}, "polygon": [[3, 2], [6, 2], [6, 5], [3, 5]]},
             {"id": "lift", "level_id": "L0", "label": "Asansör", "label_raw": "ASANSÖR", "room_type": "shaft",
              "polygon": [[1, 2.2], [2.8, 2.2], [2.8, 4], [1, 4]]},
             {"id": "land", "level_id": "L0", "label": "Oda", "label_raw": None, "room_type": "hall",
              "polygon": [[1, 0], [6, 0], [6, 1.8], [1, 1.8]]},
             {"id": "flat", "level_id": "L0", "label": "Oda", "label_raw": None, "room_type": "hall",
              "polygon": [[6.3, 0], [10, 0], [10, 6], [6.3, 6]]}]
    ops = [{"level_id": "L0", "center": [4.5, 1.9]}, {"level_id": "L0", "center": [6.15, 3.5]}]
    TW.shared_halls(rooms, ops)
    assert rooms[2]["label"] == "Kat Holü" and rooms[3]["label"] == "Oda"   # the flat joins the stair, not the lift


def test_short_parallel_strokes_wider_than_a_wall_are_no_wall_pieces():
    """real10: the stair's middle wall and rails, four lines 0.6, 0.4 and 0.6 m apart and 0.85 m long, made a 1.6 m
    band read as one wall 0.85 m thick across the stair; a wall's long faces beside such strokes keep their pair."""
    from wenart.ingest.generic import walls as W

    def line(off, s0, s1):
        return W._Line(off, s0, s1, [f"L{off}"])

    u, n = (0.0, 1.0), (-1.0, 0.0)
    stair = [line(o, 0.0, 0.85) for o in (0.0, 0.6, 1.0, 1.6)]
    pairs = W._pairs_of(stair, "SIVA", u, n)
    W.stepped_runs(pairs)
    assert len(pairs) == 3 and W._drop_wide_bands(pairs) == []
    # a 25 cm wall whose faces run on for 4 m, its pieces cut short by crossing lines, beside a 0.45 m pier band
    wall = [line(0.0, 0.0, 4.0), line(0.25, 0.0, 4.0), line(0.5, 0.0, 0.85), line(0.95, 0.0, 0.85)]
    pairs = W._pairs_of(wall, "SIVA", u, n)
    W.stepped_runs(pairs)
    kept = W._drop_wide_bands(pairs)
    assert any(abs(p.width - 0.25) < 1e-9 for p in kept)


def test_a_stair_core_holding_its_open_landing_splits_into_stair_and_shared_hall():
    """real10: no wall is drawn between the core stair and the landing in front of it and the lift: the stair core
    room is the stair (its footprint) and the shared hall 'Kat Holü', joined by a virtual opening."""
    from wenart.ingest import twins as TW

    rooms = [{"id": "core", "level_id": "L0", "label": "Merdiven", "label_raw": None, "room_type": "stair",
              "label_inferred": {"method": "stair_core"}, "evidence": [{"file": "a.dwg"}],
              "polygon": [[0, 0], [4.6, 0], [4.6, 3.5], [0, 3.5]]},
             {"id": "lift", "level_id": "L0", "label": "Asansör", "label_raw": "ASANSÖR", "room_type": "shaft",
              "polygon": [[0.1, 1.9], [1.4, 1.9], [1.4, 3.1], [0.1, 3.1]]}]
    stairs = [{"type": "stair", "level_id": "L0", "footprint": {"center": [3.25, 2.35], "size": [2.7, 2.3],
                                                                "rotation_deg": 0}}]
    openings: list = []
    notes = TW.split_core_landings(rooms, openings, stairs)
    assert len(notes) == 1 and len(rooms) == 3
    core, hall = rooms[0], rooms[2]
    assert core["room_type"] == "stair" and hall["label"] == "Kat Holü" and hall["room_type"] == "hall"
    assert abs(Polygon(core["polygon"]).area - 2.7 * 2.3) < 0.05
    assert abs(Polygon(core["polygon"]).area + Polygon(hall["polygon"]).area - 4.6 * 3.5) < 0.05
    assert openings and openings[0]["virtual"] and 2.0 < openings[0]["width"] < 5.1
    # a stair standing free inside a room (a hole in the rest) is no core landing
    free = [dict(rooms[0], polygon=[[0, 0], [6, 0], [6, 5], [0, 5]])]
    assert TW.split_core_landings(free, [], [{"type": "stair", "level_id": "L0", "footprint": {
        "center": [3, 2.5], "size": [2.7, 2.3], "rotation_deg": 0}}]) == []
    # a stair core that is only its stair (no landing in it) stays one room
    rooms2 = [dict(rooms[0], polygon=[[1.9, 1.2], [4.6, 1.2], [4.6, 3.5], [1.9, 3.5]])]
    assert TW.split_core_landings(rooms2, [], stairs) == [] and len(rooms2) == 1


def test_the_storey_marks_set_the_frame_of_the_plans_relative_marks():
    """real10: the section names the storeys at -0.50, +2.50, +5.50; the ground floor's +2.50 is building z 0, so the
    plan's '-0.50' at the front door is the 1st basement's floor (z -3.00), not a door 2.50 m up in the air."""
    from wenart.levels import read as LR
    from wenart.sheets import heights as HT

    out: dict = {"levels": []}
    levels = [{"order": -1, "id": "L-1"}, {"order": 0, "id": "L0"}, {"order": 1, "id": "L1"}]
    HT.apply_storey_marks(out, levels, {-1: -0.5, 0: 2.5, 1: 5.5}, 0.2, "a.dwg", "r1")
    z = {e["level_id"]: e["floor_z"]["value"] for e in out["levels"]}
    assert z == {"L-1": -3.0, "L0": 0.0, "L1": 3.0}
    assert out["datum"]["relative"] == 2.5 and LR.relative_zero(out["datum"]) == 2.5
    # a section whose ground floor is printed ±0.00 keeps no datum of its own
    out0: dict = {"levels": []}
    HT.apply_storey_marks(out0, levels, {-1: -3.0, 0: 0.0, 1: 3.0}, 0.2, "a.dwg", "r1")
    assert out0.get("datum") is None


def test_unreadable_facade_gaps_are_windows_over_a_drop_and_doors_onto_a_balcony():
    """real10 (user: "tell me what purple means"): a gap with unreadable lines in an outside wall is a window when
    the ground lies under it (real06: the east windows tagged 160/160, 0.50 m over the ground), a door onto a drawn
    balcony or terrace at its floor; a gap that holds another opening of its wall (real06's 1.95 m gap around the
    0.70 m balcony door) stays as it is."""
    import json
    from pathlib import Path

    from wenart.levels import model as M

    path = Path(__file__).resolve().parent / "fixtures" / "real06_outdoor_20261026.json"
    if not path.is_file():
        import pytest
        pytest.skip("real06 building not in the repository")
    b = M.infer_levels(json.loads(path.read_text(encoding="utf-8")))
    ops = {o["id"]: o for o in b["openings"]}
    for oid in ("o_L0_005", "o_L0_006", "o_L1_003"):
        assert ops[oid]["type"] == "window" and ops[oid]["drawn_type"] == "opening"
        assert ops[oid]["type_inferred"]["method"] == "facade_gap" and ops[oid]["sill_height"] >= 0.6
    assert ops["o_L1_001"]["type"] == "opening" and not ops["o_L1_001"].get("type_inferred")


def test_dimension_lines_and_their_ticks_are_never_a_gaps_content():
    """real10 (user: "This should have been a lesson learned from before ... fix it properly"): a dimension chain
    crossing a facade recess's mouth (its DH line, a 7 cm tick circle and slash on layer 0) made the gap and the
    recess's window 'unclassified', so the recess (UL277) became a room. Notation strokes are never gap content."""
    import math

    from wenart.ingest.generic import axes as AX

    circle = [(0.341 + 0.035 * math.cos(a / 8 * math.pi), 7.229 + 0.035 * math.sin(a / 8 * math.pi))
              for a in range(17)]
    strokes = [Stroke(id="LINE:dh1", kind="line", pts=[(0.411, 7.229), (1.771, 7.229)], layer="DH"),
               Stroke(id="LINE:dh2", kind="line", pts=[(0.341, 6.889), (0.341, 7.329)], layer="DH"),
               Stroke(id="LINE:tick", kind="line", pts=[(0.341, 7.229), (0.411, 7.229)], layer="0"),
               Stroke(id="CIRCLE:tick", kind="circle", pts=circle, layer="0"),
               Stroke(id="LINE:axis", kind="line", pts=[(-1.0, 3.0), (5.0, 3.0)], layer="AKS"),
               Stroke(id="LINE:dimfound", kind="line", pts=[(3.0, 0.0), (3.0, 1.0)], layer="0"),
               Stroke(id="LINE:glass", kind="line", pts=[(1.70, 7.30), (1.70, 8.00)], layer="PENCERE"),
               Stroke(id="CIRCLE:lamp", kind="circle", pts=[(p[0] + 2.0, p[1]) for p in circle], layer="0")]
    got = AX.notation_ids(strokes, {"LINE:dimfound"})
    assert got == {"LINE:dh1", "LINE:dh2", "LINE:tick", "CIRCLE:tick", "LINE:axis", "LINE:dimfound"}


def test_a_recess_whose_window_is_unreadable_follows_its_open_mirror_twin():
    """real10 (user: "this section is still wrong should be similar as the mirror", "There is no Oda on the left side
    that's outside"): the left flat's facade recess, its window to the salon unreadable, is open air because its
    mirror twin on the right half is; a twin covered by a room, or a space across the axis, decides nothing."""
    from shapely.geometry import Point, box

    from wenart.ingest.generic import core as C

    face = box(0.3, 6.6, 1.8, 9.0)
    outline = box(0.4, 0.0, 22.0, 18.0).difference(box(0.3, 6.6, 1.8, 9.0)).difference(box(20.6, 6.6, 22.1, 9.0))
    axis = ("x", 11.2)
    out = Point(0.1, 7.8)
    assert C._open_twin(face, out, axis, [face], outline) == "x = 11.20"
    assert C._open_twin(face, out, axis, [face, box(20.6, 6.6, 22.1, 9.0)], outline) is None   # the twin is a room
    assert C._open_twin(box(10.0, 6.6, 12.0, 9.0), out, axis, [], outline) is None             # across the axis


def test_every_conflict_kind_the_sheets_stage_writes_is_in_its_schema():
    """real11 (3 Nov 2026): a registration conflict 'shaft_grid_mismatch' failed sheets.json's schema, so the reading
    check reported 'the sheets need review' (critical) and a pod's sheets stage would stop the project."""
    import json
    import re
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    enum = set(json.loads((root / "wenart" / "schema" / "sheets.schema.json").read_text(encoding="utf-8"))
               ["$defs"]["conflict"]["properties"]["kind"]["enum"])
    kinds = set()
    for f in (root / "wenart" / "sheets").glob("*.py"):
        kinds |= set(re.findall(r"""conflict\(\s*["']([a-z_]+)["']""", f.read_text(encoding="utf-8")))
    assert kinds and kinds <= enum, kinds - enum
