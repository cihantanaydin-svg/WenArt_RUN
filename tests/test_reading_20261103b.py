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
