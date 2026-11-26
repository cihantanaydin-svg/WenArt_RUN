"""Audit fix round 1 (26 Nov 2026): the general rules R19, R04, R10, R13, R25 and R26 found in the re-rendered
real17, real06, real10 and real15 (CPU, pure; synthetic buildings and, where stored, the run's builds)."""
import copy
import json
import os
from pathlib import Path

import pytest

from wenart.blender import architect as AR
from wenart.blender import architect_actions as AA
from wenart.blender import architect_rules as RULES
from wenart.blender import outdoor as OD

ROOT = Path(__file__).resolve().parents[1]
RUNS = Path(os.environ.get("WENART_RUNS") or ROOT / "runs")       # the runs' collected results (not in git)


def _rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _wall(wid, a, b, t=0.1, lid="L1", **kw):
    return dict({"id": wid, "level_id": lid, "start": list(a), "end": list(b), "thickness": t, "status": "verified",
                 "evidence": []}, **kw)


def _window(oid, wid, c, w=0.5, lid="L1", **kw):
    return dict({"id": oid, "type": "window", "level_id": lid, "wall_id": wid, "center": list(c), "width": w,
                 "height": 0.5, "sill_height": 1.5}, **kw)


# --------------------------------------------------------------------------------------------- R19 open-air voids
def _shaft_building():
    """A WC, a 0.5 x 0.5 m air shaft and a bathroom on L1; 0.5 m windows of both wet rooms onto the shaft."""
    return {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7},
                       {"id": "L1", "elevation": 3.0, "ceiling_height": 2.7}],
            "rooms": [{"id": "r_wc", "level_id": "L1", "room_type": "wc", "polygon": _rect(0, 0, 1.45, 1.5)},
                      {"id": "r_hb", "level_id": "L1", "room_type": "shaft", "room_subtype": "air_shaft",
                       "label": "Hava Bacası", "polygon": _rect(1.55, 0.5, 1.95, 1.0)},
                      {"id": "r_bath", "level_id": "L1", "room_type": "bathroom", "polygon": _rect(2.05, 0, 4, 1.5)}],
            "walls": [_wall("w1", (1.5, 0.0), (1.5, 1.5)), _wall("w2", (2.0, 0.0), (2.0, 1.5))],
            "openings": [_window("win1", "w1", (1.5, 0.75)), _window("win2", "w2", (2.0, 0.75))]}


def test_air_shafts_light_wells_and_flags_are_open_air_lifts_are_not():
    assert OD.is_void({"room_type": "shaft", "room_subtype": "air_shaft"})
    assert OD.is_void({"room_type": "light_well"}) and OD.is_void({"room_type": "x", "room_subtype": "light_well"})
    assert OD.is_void({"room_type": "shaft", "label": "Hava Bacası"})          # the label alone names it
    assert OD.is_void({"room_type": None, "label": "H.B 50/50"})
    assert not OD.is_void({"room_type": "shaft", "label": "Asansör"})            # a lift shaft is no void
    assert not OD.is_void({"room_type": "bedroom", "label": "Aydınlık oda"})    # a typed room keeps its type
    assert OD.is_open_air({"room_type": "balcony"}) and OD.is_open_air({"room_type": "x", "open_to_sky": True})
    assert OD.is_open_air({"id": "r1", "room_type": "shaft"}, sky_ids={"r1"})
    for room in ({"room_type": "shaft", "room_subtype": "air_shaft"}, {"room_type": "terrace"}):
        assert AA.is_open_air(room) and AA.Plan.is_outside(room)
    assert OD.sky_room_ids({"roof": {"openings": [{"kind": "light_well", "room_id": "r9"}, {"kind": "x"}]}}) == {"r9"}


def test_w2_never_acts_on_windows_onto_an_air_shaft():
    """R19 (real17-F04): the WC's vent onto 'H.B 50X50' became a 0.80 m door, the bath's was closed."""
    b = _shaft_building()
    plan = AA.Plan(b)
    sides = AR.opening_sides(b)
    w2 = next(q for q in RULES.openings_rules(plan, sides, set()) if q["id"] == "W2")
    rows = {a["element"]: a for a in w2["answers"]}
    for oid in ("win1", "win2"):
        assert not rows[oid].get("open"), rows[oid]
        assert rows[oid]["found"] == "onto an open-air room"
    assert w2["status"] == "ok"
    # the old reading of the shaft as a room no door reaches: the W2 question would make win1 a door
    old = copy.deepcopy(b)
    old["rooms"][1]["room_subtype"], old["rooms"][1]["label"] = None, "Depo"
    plan_old = AA.Plan(old)
    w2_old = next(q for q in RULES.openings_rules(plan_old, AR.opening_sides(old), {"r_hb"}) if q["id"] == "W2")
    assert any(a.get("default") in ("window_to_door", "close_window") for a in w2_old["answers"] if a.get("open"))


def test_a_door_is_never_wider_than_the_side_of_the_room_it_opens_into():
    b = _shaft_building()
    b["rooms"][1].update(room_type="storage", room_subtype=None, label="Depo")     # a 0.5 m closet, not a void
    plan = AA.Plan(b)
    o = plan.openings["win1"]
    side = AA.room_side_m(plan, o, plan.room["r_hb"])
    assert side == pytest.approx(0.5, abs=0.01)
    assert AA.room_side_m(plan, o, plan.room["r_wc"]) == pytest.approx(1.5, abs=0.01)
    assert "wider than the 0.50 m side of r_hb" in AA.door_too_wide(plan, o, 0.8)
    assert AA.door_too_wide(plan, o, 0.45) is None
    ok, why = AA.act_window_to_door(plan, "W2:win1", {"by": "code"}, "win1")
    assert not ok and "wider than the 0.50 m side" in why and plan.openings["win1"]["type"] == "window"
    # a door of a 0.5 m closet is never widened past the closet's side
    b["openings"][0].update(type="door", width=0.5, sill_height=0.0, height=2.1)
    plan = AA.Plan(b)
    ok, why = AA.act_widen_door(plan, "D1:win1", {"by": "code"}, "win1", "r_wc")
    assert not ok and "wider than" in why and plan.openings["win1"]["width"] == 0.5


def test_w5_never_makes_a_window_onto_a_light_well_tall():
    b = {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}],
         "rooms": [{"id": "r_bed", "level_id": "L0", "room_type": "bedroom", "polygon": _rect(0, 0, 4, 3)},
                   {"id": "r_lw", "level_id": "L0", "room_type": "shaft", "room_subtype": "light_well",
                    "polygon": _rect(4.1, 0, 6, 3)}],
         "walls": [_wall("w1", (4.05, 0), (4.05, 3), lid="L0"), _wall("w2", (0, 3.05), (4, 3.05), lid="L0")],
         "openings": [_window("wa", "w1", (4.05, 1.5), w=1.2, lid="L0", sill_height=0.9, height=1.2),
                      _window("wb", "w2", (2.0, 3.05), w=1.2, lid="L0", sill_height=0.9, height=1.2)]}
    plan = AA.Plan(b)
    groups = AA.tall_window_groups(plan, "r_bed")
    ids = [w["id"] for g in groups for w in g["windows"]]
    assert "wa" not in ids and "wb" in ids


def test_a_light_well_is_no_landing_for_an_outside_door():
    from wenart.blender import site as S

    b = {"levels": [{"id": "L1", "elevation": 3.0}],
         "rooms": [{"id": "r_lw", "level_id": "L1", "room_type": "shaft", "room_subtype": "light_well",
                    "polygon": _rect(0, 0, 2, 2)},
                   {"id": "r_bal", "level_id": "L1", "room_type": "balcony", "polygon": _rect(3, 0, 5, 2)}]}
    assert S.landing_at(b, "L1", (1, 1), 3.0) is None
    assert S.landing_at(b, "L1", (4, 1), 3.0)["id"] == "r_bal"


# --------------------------------------------------------------------------------------------- R04 edge guards
class _Build:
    def __init__(self, b):
        self.building = b
        self.warnings = []

    def warn(self, m):
        self.warnings.append(m)


def _balcony_floor(lid, z, band=0.05, with_door=True):
    """One storey: a kitchen 5 x 4 m and a corner balcony 1.5 x 2.5 m beside it, its open edges drawn as a band."""
    rooms = [{"id": f"r_{lid}_mutfak", "level_id": lid, "room_type": "kitchen", "label": "Mutfak",
              "polygon": _rect(1.6, 0, 6.6, 4)},
             {"id": f"r_{lid}_balkon", "level_id": lid, "room_type": "balcony", "label": "BALKON",
              "polygon": _rect(0.03, 0.03, 1.5, 2.5)}]
    walls = [_wall(f"w_{lid}_k1", (1.55, 0), (1.55, 4), t=0.1, lid=lid),          # kitchen wall with the door
             _wall(f"w_{lid}_k2", (1.55, 4.05), (6.6, 4.05), t=0.2, lid=lid),
             _wall(f"w_{lid}_b1", (0.0, 0.0), (0.0, 2.55), t=band, lid=lid),     # the band: west edge
             _wall(f"w_{lid}_b2", (0.0, 2.55), (1.5, 2.55), t=band, lid=lid),    # north edge
             _wall(f"w_{lid}_b3", (0.0, 0.0), (1.5, 0.0), t=band, lid=lid)]      # south edge
    ops = [{"id": f"d_{lid}_1", "type": "door", "level_id": lid, "wall_id": f"w_{lid}_k1", "center": [1.55, 1.2],
            "width": 0.9}] if with_door else []
    return {"id": lid, "elevation": z, "ceiling_height": 2.7}, rooms, walls, ops


def _storeys(n, band=0.05):
    b = {"levels": [], "rooms": [], "walls": [], "openings": [], "level_inference": {},
         "site": {"outdoor_spaces": []}}
    for k in range(n):
        lv, rooms, walls, ops = _balcony_floor(f"L{k}", 3.0 * k, band)
        lv["order"] = k
        b["levels"].append(lv)
        b["rooms"] += rooms
        b["walls"] += walls
        b["openings"] += ops
    return b


def test_balcony_band_walls_are_guards_on_every_upper_level():
    """R04 (real17-F01): a 5 cm band on the open edges of a corner balcony is a railing, never a 3 m storey wall."""
    from wenart.ingest import edge_guards as EG

    b = _storeys(4)
    out = EG.apply(_Build(b))
    walls = {w["id"]: w for w in b["walls"]}
    for lid in ("L1", "L2", "L3"):
        for k in ("b1", "b2", "b3"):
            w = walls[f"w_{lid}_{k}"]
            assert w["parapet"] and w["height"] <= 1.1 and w["guard"]["top_m"] == pytest.approx(1.1)
            assert w["guard"]["kind"] == "railing" and w["guard_of"] == f"r_{lid}_balkon"
            assert w["drawn_height"] is None and w["guard_drawn_thickness"] == 0.05
            assert w["evidence"][-1]["rule"] == "edge_guard"
        assert not walls[f"w_{lid}_k1"].get("parapet")             # the kitchen wall with the door stays
        assert not walls[f"w_{lid}_k2"].get("parapet")
    assert not any(walls[f"w_L0_{k}"].get("parapet") for k in ("b1", "b2", "b3"))   # the ground floor: no fall edge
    assert len(out) == 9 and b["level_inference"]["edge_guards"]["guards"]


def test_a_solid_band_is_a_solid_parapet_and_a_wall_carrying_the_floor_above_stays():
    from wenart.ingest import edge_guards as EG

    b = _storeys(3, band=0.2)
    # the top floor's balcony is closed in (a room drawn over it): its walls are full walls standing on L1's band
    top = next(r for r in b["rooms"] if r["id"] == "r_L2_balkon")
    top.update(room_type="bedroom", label="Oda")
    EG.apply(_Build(b))
    walls = {w["id"]: w for w in b["walls"]}
    assert not walls["w_L1_b1"].get("parapet")                     # L2's full wall stands on it
    assert any(k["wall"] == "w_L1_b1" and "stands on it" in k["reason"]
               for k in b["level_inference"]["edge_guards"]["kept"])
    b = _storeys(2, band=0.2)
    EG.apply(_Build(b))
    w = next(x for x in b["walls"] if x["id"] == "w_L1_b1")
    assert w["guard"]["kind"] == "solid" and w["height"] == pytest.approx(1.1)


def test_privacy_walls_loggia_sides_and_party_walls_stay_full_walls():
    from wenart.ingest import edge_guards as EG

    b = _storeys(2)
    lv = "L1"
    # a neighbour's balcony beyond the west band: a privacy wall between two balconies
    b["rooms"].append({"id": "r_L1_balkon_n", "level_id": lv, "room_type": "balcony",
                       "polygon": _rect(-1.5, 0.03, -0.03, 2.5)})
    # a room beyond the north band: a loggia's side wall
    b["rooms"].append({"id": "r_L1_oda", "level_id": lv, "room_type": "bedroom", "polygon": _rect(0.0, 2.6, 1.5, 5)})
    walls = {w["id"]: w for w in b["walls"]}
    walls["w_L1_b3"]["party_wall"] = {"reason": "neighbour"}
    EG.apply(_Build(b))
    assert not any(walls[f"w_L1_{k}"].get("parapet") for k in ("b1", "b2", "b3"))


def test_the_build_keeps_a_parapet_walls_own_height():
    from wenart.blender import shell

    lv = {"id": "L1", "elevation": 3.0, "ceiling_height": 2.7}
    h, assumed = shell.wall_height({"height": 0.15, "parapet": True}, lv, True)
    assert h == pytest.approx(0.15) and "slab_thickness" not in assumed
    h, assumed = shell.wall_height({"height": 2.7}, lv, True)
    assert h > 2.7 and "slab_thickness" in assumed
    src = (ROOT / "wenart" / "blender" / "shell.py").read_text(encoding="utf-8")
    assert "if slab_above is not None and not guard_wall:" in src
    assert "if cut_planes is not None and not guard_wall and not outside_roof(wall, roof_cut):" in src
    # a parapet wall carries the balcony's edge: no second rail along it
    room = {"polygon": _rect(0.03, 0.03, 1.5, 2.5)}
    walls = [_wall("p1", (0.0, 0.0), (0.0, 2.55), t=0.05, parapet=True, height=0.15)]
    edges = shell.railing_edges(room, walls)
    assert not any(abs(p[0]) < 0.1 and abs(q[0]) < 0.1 for p, q in edges)


def test_a_roof_terraces_edge_is_left_to_the_roof_and_carries_nothing():
    """A roof terrace cut into the roof keeps the roof's parapet (roof.parapet_cuts, a drawn height wins); the band of
    the balcony under it still becomes a guard (its wall above carries nothing)."""
    from wenart.ingest import edge_guards as EG

    b = _storeys(3)
    b["roof"] = {"openings": [{"id": "ro_001", "kind": "terrace", "room_id": "r_L2_balkon"}]}
    EG.apply(_Build(b))
    walls = {w["id"]: w for w in b["walls"]}
    assert not any(walls[f"w_L2_{k}"].get("parapet") for k in ("b1", "b2", "b3"))
    assert all(walls[f"w_L1_{k}"]["parapet"] for k in ("b1", "b2", "b3"))
    kept = {k["wall"]: k["reason"] for k in b["level_inference"]["edge_guards"]["kept"]}
    assert "roof.parapet_cuts" in kept["w_L2_b1"]


def test_a_balcony_over_the_roof_of_the_floor_below_keeps_its_wall():
    """A setback storey: beyond the band lies the roof of a room of the floor below (or a room the reading missed),
    no drop: the wall stays (real14 L6, w_L6_031)."""
    from wenart.ingest import edge_guards as EG

    b = _storeys(3)
    b["rooms"].append({"id": "r_L1_oda_w", "level_id": "L1", "room_type": "bedroom",
                       "polygon": _rect(-3.0, 0.0, -0.05, 2.5)})              # under L2's west band, on L1
    EG.apply(_Build(b))
    walls = {w["id"]: w for w in b["walls"]}
    assert not walls["w_L2_b1"].get("parapet") and walls["w_L2_b2"]["parapet"]


def test_a_short_thick_block_at_a_balcony_corner_is_no_guard():
    from wenart.ingest import edge_guards as EG

    b = _storeys(2)
    b["walls"].append(_wall("w_L1_pier", (0.0, 1.0), (0.0, 1.2), t=0.23, lid="L1"))     # 0.20 m long, 0.23 thick
    EG.apply(_Build(b))
    assert not next(w for w in b["walls"] if w["id"] == "w_L1_pier").get("parapet")


REAL17 = RUNS / "20261126-110510-full" / "results" / "renders" / "real17" / "building_built.json"


@pytest.mark.skipif(not REAL17.is_file(), reason="the real17 build of run 20261126-110510-full is not stored here")
def test_real17_balcony_bands_become_guards():
    from wenart.ingest import edge_guards as EG

    b = json.loads(REAL17.read_text(encoding="utf-8"))
    for w in b["walls"]:                                            # the stored build: as the reader left them
        w.pop("parapet", None)
    EG.apply(_Build(b))
    guards = {w["id"] for w in b["walls"] if w.get("parapet")}
    assert {"w_L1_041", "w_L1_042", "w_L2_041", "w_L2_042", "w_L1_010", "w_L1_033"} <= guards
    assert all(w["height"] <= 1.1 for w in b["walls"] if w.get("parapet"))
    assert not {"w_L1_043", "w_L1_044", "w_L2_043"} & guards       # the flats' own facade walls stay


# ------------------------------------------------------------------------------------- R10 guards and landings
def _guard_building(space_z=3.0, with_space=True, room_floor=0.0):
    b = {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7, "order": 0},
                    {"id": "L1", "elevation": 3.0, "ceiling_height": 2.7, "order": 1}],
         "rooms": [{"id": "r_L1_oda", "level_id": "L1", "room_type": "bedroom", "polygon": _rect(0, 0, 4, 4)},
                   {"id": "r_L0_salon", "level_id": "L0", "room_type": "living", "polygon": _rect(0, 0, 4, 4),
                    "floor_offset_m": room_floor}],
         "site": {"outdoor_spaces": [{"id": "os_L1_balkon", "kind": "balcony", "level_id": "L1", "z": space_z,
                                      "polygon": _rect(4.1, 0, 6, 4)}] if with_space else []}}
    return b


def _rec(level, oid, typ, bottom, centre=(4.05, 2.0)):
    return {"opening": {"id": oid, "type": typ, "width": 0.9}, "level": level, "centre": centre,
            "outward": (1.0, 0.0), "bottom": bottom, "top": bottom + 2.1, "half_t": 0.1}


def test_a_door_onto_an_outdoor_space_gets_no_guard_even_when_an_answer_asked():
    from wenart.blender import facade as FA

    b = _guard_building()
    L1 = b["levels"][1]
    ground = (lambda x, y: -0.5)
    need = FA.guard_need(b, _rec(L1, "d1", "door", 3.0), ground)
    assert not need["need"] and need["landing"]["id"] == "os_L1_balkon"
    rec = _rec(L1, "d1", "door", 3.0)
    rec["opening"]["guard"] = {"top_m": 1.1, "reason": "AI.french_window:d_old"}     # a stale answer
    assert not FA.guard_need(b, rec, ground)["need"]
    # no space (or one a full step lower): the door into the air keeps its guard
    assert FA.guard_need(_guard_building(with_space=False), rec, ground)["need"]
    assert FA.guard_need(_guard_building(space_z=2.6), _rec(L1, "d1", "door", 3.0), ground)["need"]


def test_the_drop_counts_from_the_floor_not_the_sill():
    from wenart.blender import facade as FA

    b = _guard_building(with_space=False)
    L0 = b["levels"][0]
    ground = (lambda x, y: -0.5)                                   # a 0.5 m plinth
    need = FA.guard_need(b, _rec(L0, "w0", "window", 0.7), ground)
    assert not need["need"] and need["drop"] == pytest.approx(0.5)
    # the floor of a room 1.2 m up on the same level is measured with its offset
    b = _guard_building(with_space=False, room_floor=1.2)
    need = FA.guard_need(b, _rec(b["levels"][0], "w0", "window", 1.4), ground)
    assert need["floor"] == pytest.approx(1.2) and need["need"]     # 0.2 m sill over a 1.7 m drop


def test_facade_kit_builds_no_guard_at_a_balcony_door():
    from wenart.blender import facade as FA

    b = _guard_building()
    b["walls"] = [_wall("w1", (4.05, 0), (4.05, 4), t=0.1)]
    b["openings"] = [{"id": "d1", "type": "door", "level_id": "L1", "wall_id": "w1", "center": [4.05, 2.0],
                      "width": 0.9, "height": 2.1, "guard": {"top_m": 1.1}}]
    outline = _rect(0, 0, 4.1, 4)
    kit = FA.facade_kit(b, b["levels"], {"L0": outline, "L1": outline}, outline, None, None,
                        FA.family_rules(None))
    assert not [x for x in kit["boxes"] if x.get("parent") == "d1"]
    b["site"]["outdoor_spaces"] = []
    kit = FA.facade_kit(b, b["levels"], {"L0": outline, "L1": outline}, outline, None, None,
                        FA.family_rules(None))
    assert [x for x in kit["boxes"] if x.get("parent") == "d1"]


def test_the_rise_table_names_the_landing():
    from wenart.report import m10

    b = _guard_building()
    e = {"door_id": "d1", "level_id": "L1", "threshold_z": 3.0, "ground_z": -0.5, "rise": 3.5, "solution": "none",
         "face": [4.1, 2.0], "outward": [1.0, 0.0]}
    assert m10.entrance_landing(b, e)["id"] == "os_L1_balkon"
    b["level_marks"] = [{"kind": "floor", "z": 3.0}]
    b["site"]["entrances"] = [e]
    lines = m10.level_lines(m10.level_summary(b))
    row = next(x for x in lines if x.startswith("| d1 |"))
    assert "lands on the balcony os_L1_balkon" in row and "3,50" not in row.split("|")[4]


REAL06 = RUNS / "20261126-110510-full" / "results" / "renders" / "real06" / "building_built.json"


@pytest.mark.skipif(not REAL06.is_file(), reason="the real06 build of run 20261126-110510-full is not stored here")
def test_real06_balcony_doors_and_ground_floor_windows_need_no_guard():
    from wenart.blender import build as BB
    from wenart.blender import facade as FA
    from wenart.blender import site as S
    from wenart.levels import model as LM

    b = json.loads(REAL06.read_text(encoding="utf-8"))
    levels = LM.base_levels(b)
    outlines = LM.outlines_of(b)
    outline = BB.ground_outline(b, outlines)
    ground = (lambda x, y: -0.5)
    needs = {r["opening"]["id"]: FA.guard_need(b, r, ground)
             for r in S.outer_openings(b, levels, outline, outlines, kinds=("door", "window", "opening"))}
    assert not needs["d_L1_002"]["need"] and not needs["d_L1_007"]["need"]
    assert not any(n["need"] for oid, n in needs.items() if oid.split("_")[1] == "L0")


# ------------------------------------------------------------------------------------- R13 typical copies
def _typical(n):
    levels = [{"id": "L0", "elevation": 0.0}] + [{"id": f"L{k}", "elevation": 3.0 * k, "typical_of": "L0"}
                                                 for k in range(1, n)]
    b = {"levels": levels, "rooms": [], "furniture": [], "decor": []}
    for lv in levels:
        lid = lv["id"]
        b["rooms"] += [{"id": f"r_{lid}_banyo", "level_id": lid, "polygon": _rect(0, 0, 2, 2)},
                       {"id": f"r_{lid}_salon", "level_id": lid, "polygon": _rect(2, 0, 6, 4)}]
        b["furniture"] += [
            {"id": f"f_{lid}_001", "level_id": lid, "type": "toilet", "source": "from_documents",
             "room_id": f"r_{lid}_banyo", "floor_z": lv["elevation"]},
            {"id": f"f_{lid}_002", "level_id": lid, "type": "kitchen_counter", "source": "from_documents",
             "room_id": f"r_{lid}_salon"},
            {"id": f"f_{lid}_003", "level_id": lid, "type": "hob", "source": "added_by_ai",
             "asset": {"built_in": f"f_{lid}_002"}},
            {"id": f"f_{lid}_004", "level_id": lid, "type": "stairs"},
            {"id": f"f_{lid}_005", "level_id": lid, "type": "sofa", "source": "added_by_ai",
             "room_id": f"r_{lid}_salon"},
            {"id": f"f_{lid}_006", "level_id": lid, "type": "wardrobe", "source": "from_documents",
             "design": {"built_in": True}},
            {"id": f"f_{lid}_007", "level_id": lid, "type": "washbasin", "source": "added_by_ai"}]
        b["decor"].append({"id": f"dec_{lid}_001", "level_id": lid, "host_id": f"f_{lid}_005"})
    return b


def test_unfurnished_typical_copies_keep_the_drawn_fixed_equipment():
    """R13 (real10-F09): L1-L6 of real10 lost every toilet, basin and counter in the build."""
    from wenart.blender import typical_copies as TC

    b = _typical(6)
    recs = TC.furnish_typical_copies(b)
    assert {r["value"] for r in recs} == {"fixed as L0"} and len(recs) == 5
    for k in range(1, 6):
        lid = f"L{k}"
        ids = sorted(f["id"] for f in b["furniture"] if f["level_id"] == lid)
        assert ids == [f"f_{lid}_001", f"f_{lid}_002", f"f_{lid}_003", f"f_{lid}_004", f"f_{lid}_006"]
        toilet = next(f for f in b["furniture"] if f["id"] == f"f_{lid}_001")
        assert toilet["room_id"] == f"r_{lid}_banyo" and toilet["typical_copy_of"] == "f_L0_001"
        assert toilet["floor_z"] == pytest.approx(3.0 * k)
        assert not [d for d in b["decor"] if d["level_id"] == lid]
    assert recs[0]["kept_of_typical"] == ["f_L0_001", "f_L0_002", "f_L0_003", "f_L0_006"]   # its own stair stays
    assert not next(f for f in b["furniture"] if f["id"] == "f_L1_004").get("typical_copy_of")
    assert recs[0]["counts"]["furniture"] == {"was": 7, "now": 5}


def test_a_typical_floor_without_fixed_equipment_keeps_only_the_copies_stairs():
    from wenart.blender import typical_copies as TC

    b = _typical(5)
    b["furniture"] = [f for f in b["furniture"] if f["type"] in ("stairs", "sofa")]
    recs = TC.furnish_typical_copies(b)
    assert {r["value"] for r in recs} == {"none"}
    assert sorted(f["id"] for f in b["furniture"] if f["level_id"] == "L2") == ["f_L2_004"]


def test_a_fixed_only_copy_duplicates_only_the_kept_pieces_objects():
    from wenart.blender import typical_copies as TC

    class Ob:
        def __init__(self, name, parent=None):
            self.name, self.parent = name, parent

    toilet, part, sofa, cushion = Ob("furn_f_L0_001"), None, Ob("furn_f_L0_005"), None
    part = Ob("furn_f_L0_001_bowl", toilet)
    cushion = Ob("decor_dec_L0_001", sofa)
    picked = TC.objects_under([toilet, part, sofa, cushion], [toilet])
    assert [o.name for o in picked] == ["furn_f_L0_001", "furn_f_L0_001_bowl"]
    s = TC.copy_summary({"pieces": 7, "decor": 3, "by_method": {"library": 7}, "fallbacks": [{"id": "f_L0_005"}],
                         "not_built": [{"id": "f_L0_001"}]}, "L0", "L2", {"f_L2_001": None}, only=["f_L0_001"])
    assert s["pieces"] == 1 and s["decor"] == 0 and "by_method" not in s and s["fallbacks"] == []
    assert s["not_built"] == [{"id": "f_L2_001"}] and s["fixed_only"]
    src = (ROOT / "wenart" / "blender" / "build.py").read_text(encoding="utf-8")
    assert 'out.setdefault("typical_fixed_only", {})' in src and '(prep.get("typical_fixed_only") or {})' in src


REAL10 = RUNS / "20261126-114512-full" / "results" / "furniture" / "real10" / "building_furnished.json"


@pytest.mark.skipif(not REAL10.is_file(), reason="the real10 furnished building of run 20261126-114512-full is "
                                                   "not stored here")
def test_real10_copied_floors_keep_their_toilets_and_counters():
    from wenart.blender import typical_copies as TC

    b = json.loads(REAL10.read_text(encoding="utf-8"))
    TC.furnish_typical_copies(b)
    for lid in ("L1", "L6"):
        types = {f["type"] for f in b["furniture"] if f["level_id"] == lid}
        assert {"toilet", "washbasin", "kitchen_counter", "stair"} <= types


# ------------------------------------------------------------------------------------- R25 courts and wells
def _basement(rooms_type="wc", width=0.5, height=0.5, door_at=None, platforms=()):
    b = {"levels": [{"id": "L-1", "elevation": -3.0, "ceiling_height": 2.7, "order": -1},
                    {"id": "L0", "elevation": 0.0, "ceiling_height": 2.7, "order": 0}],
         "rooms": [{"id": "r_b", "level_id": "L-1", "room_type": rooms_type, "polygon": _rect(0, 0, 8, 6)},
                   {"id": "r_g", "level_id": "L0", "room_type": "hall", "polygon": _rect(0, 0, 8, 6)}],
         "walls": [_wall("wb", (8.1, 0), (8.1, 6), t=0.2, lid="L-1"), _wall("wg", (8.1, 0), (8.1, 6), t=0.2, lid="L0"),
                   _wall("wb2", (0, 6.1), (8, 6.1), t=0.2, lid="L-1"), _wall("wg2", (0, 6.1), (8, 6.1), t=0.2, lid="L0")],
         "openings": [_window("v1", "wb", (8.1, 3.0), w=width, lid="L-1", height=height, sill_height=1.7)],
         "site": {"ground": {"levels": [{"side": "all", "z": {"value": 0.2, "method": "vector"}}]}}}
    if door_at is not None:
        b["openings"].append({"id": "dg", "type": "door", "level_id": "L0", "wall_id": "wg",
                              "center": [8.1, door_at], "width": 1.5, "height": 2.1})
        b["site"]["entrances"] = [{"door_id": "dg"}]
    return b


def _wells(b, mode="auto"):
    from wenart.blender import build as BB
    from wenart.blender import site as S
    from wenart.levels import model as LM

    levels = LM.base_levels(b)
    outlines = {"L-1": _rect(0, 0, 8.2, 6.2), "L0": _rect(0, 0, 8.2, 6.2)}
    outline = _rect(0, 0, 8.2, 6.2)
    tm = S.terrain_model(b, outline)
    return S.light_wells(b, levels, tm, outline, outlines, front_court=mode)[0]


def test_no_court_for_a_vent_a_wc_or_beside_an_entrance():
    """R25 (real17-F09): 3 m courts were dug for WC and store vents beside the entrance."""
    wells = _wells(_basement())
    assert wells and not [w for w in wells if w.get("kind") == "front_court"]
    assert wells[0]["vent_pit"] and wells[0]["grate"] and "vent pit" in wells[0]["reason"]
    # a big window of a WC: no court either
    wells = _wells(_basement(width=1.5, height=1.2))
    assert not [w for w in wells if w.get("kind") == "front_court"] and "no habitable room" in wells[0]["reason"]
    # the main window of a bedroom: its court
    wells = _wells(_basement("bedroom", width=1.5, height=1.2))
    assert [w for w in wells if w.get("kind") == "front_court"]
    # ... but never within 1.5 m of the entrance
    wells = _wells(_basement("bedroom", width=1.5, height=1.2, door_at=4.6))
    assert not [w for w in wells if w.get("kind") == "front_court"] and "entrance or exit door dg" in wells[0]["reason"]


def test_a_ground_floor_light_well_needs_the_ground_045_m_over_the_sill():
    """R25 (real17-F10): shop windows a few cm under a sloping pavement got concrete pits; a basement window at grade
    keeps its paved light well (lesson UL158, the user on real04)."""
    b = _basement("other", width=4.7, height=2.4)
    b["openings"][0].update(level_id="L0", wall_id="wg", sill_height=0.0)       # sill 0.00, ground +0.20: 0.20 m
    assert _wells(b) == []
    b["site"]["ground"]["levels"][0]["z"]["value"] = 0.5                         # 0.50 m: a light well
    assert len(_wells(b)) == 1
    b = _basement("bedroom", width=1.5, height=1.2)
    b["openings"][0]["sill_height"] = 2.9                          # a basement sill -0.10, ground +0.20: 0.30 m
    assert len(_wells(b)) == 1 and _wells(b)[0].get("kind") != "front_court"


def test_an_elevated_platform_never_raises_a_well():
    from wenart.blender import site as S

    well = {"opening_id": "w", "level_id": "L0", "polygon": _rect(0, 0, 1, 1), "sill_z": 0.0, "top_z": 0.2,
            "source": "assumed"}
    balcony = {"id": "os_L1_balkon_1", "polygon": _rect(-1, -1, 2, 2), "z": 3.3, "elevated": True}
    kept, dropped = S.wells_on_platforms([well], [balcony])
    assert kept == [well] and not dropped
    terrace = {"id": "t", "polygon": _rect(-1, -1, 2, 2), "z": -0.5, "elevated": False}
    kept, dropped = S.wells_on_platforms([well], [terrace])
    assert not kept and dropped


# ------------------------------------------------------------------------------------- R26 stale views
def test_views_of_another_build_are_left_out_of_the_final_views():
    from wenart.report import final as F

    inp = F.Inputs(project_out=Path("."), out_dir=Path("."), project="p")
    inp.render_manifest = {"scene_sha256": "new"}
    inp.building = {"openings": [{"id": "o_L0_001", "type": "window"}],
                    "furniture": [{"id": "f_L0_084", "type": "washbasin"}]}
    els = F.building_elements(inp.building)
    assert "another scene build" in F.stale_view_reason(inp, {"scene_sha256": "old"}, None, els)
    assert "another scene build" in F.stale_view_reason(inp, {"scene_sha256": "new", "stale_build": {}}, None, els)
    cc = {"projected": {"o_L0_002": {"kind": "window", "type": "window"},
                        "f_L0_084": {"kind": "furniture", "type": "table_coffee"}}}
    why = F.stale_view_reason(inp, {"scene_sha256": "new"}, cc, els)
    assert "o_L0_002 (not in the building)" in why and "f_L0_084 (a table_coffee in the view" in why
    ok = {"projected": {"o_L0_001": {"kind": "window", "type": "window"}, "sl_L1": {"kind": "slab"}}}
    assert F.stale_view_reason(inp, {"scene_sha256": "new"}, ok, els) is None


def test_an_exterior_views_cross_check_is_no_test_of_the_building():
    from wenart.report import final as F

    inp = F.Inputs(project_out=Path("."), out_dir=Path("."), project="p")
    inp.render_manifest = {"scene_sha256": "new"}
    els = F.building_elements({"openings": [{"id": "d1", "type": "door"}]})
    cc = {"projected": {"d1": {"kind": "window", "type": "window"}, "o9": {"kind": "window"}},
          "roof_not_rendered": []}
    assert F.stale_view_reason(inp, {"camera": "ext_1", "scene_sha256": "new"}, cc, els) is None
    # the same items in an interior view's cross-check: checked against another building
    assert F.stale_view_reason(inp, {"camera": "cam_r_x_1", "scene_sha256": "new"}, {"projected": cc["projected"]},
                               els)


def test_build_views_lists_the_stale_views():
    from wenart.report import final as F

    inp = F.Inputs(project_out=Path("."), out_dir=Path("."), project="p")
    inp.render_manifest = {"scene_sha256": "new"}
    inp.entries = {"cam_a": {"camera": "cam_a", "scene_sha256": "old"}}
    assert F.build_views(inp) == []
    assert inp.stale_views[0]["camera"] == "cam_a" and any("left out of the final views" in w for w in inp.warnings)
    src = (ROOT / "wenart" / "blender" / "render.py").read_text(encoding="utf-8")
    assert 'entry["stale_build"] = {' in src and 'entry.pop("stale_build", None)' in src


REAL10_FINAL = RUNS / "20261126-114512-full" / "results" / "final" / "real10" / "final_manifest.json"
REAL10_RENDER = RUNS / "20261126-114512-full" / "results" / "renders" / "real10" / "render_manifest.json"


@pytest.mark.skipif(not (REAL10_FINAL.is_file() and REAL10_RENDER.is_file()),
                    reason="the real10 run 20261126-114512-full is not stored here")
def test_real10_carried_interiors_are_not_published():
    from wenart.report import final as F

    inp = F.Inputs(project_out=Path("."), out_dir=Path("."), project="real10")
    inp.render_manifest = json.loads(REAL10_RENDER.read_text(encoding="utf-8"))
    entries = {e["camera"]: e for e in inp.render_manifest["renders"]}
    stale = [c for c, e in entries.items() if F.stale_view_reason(inp, e, None, {})]
    assert sorted(stale) == sorted(inp.render_manifest["carried_from_earlier_build"]) and len(stale) == 29
    assert not [c for c in stale if c.startswith("ext_")]


# ------------------------------------------------------------------------------------- R14 top-down covers
def test_a_carve_may_only_remove_geometry():
    """R14 (real17-F14, real06-F09): the footprint carve of an open surface kept the cutter's box, its top at the
    cutter's (wall cut + 1 m): a plate over the whole floor. Blender runs on the pod; the rule's arithmetic is pure."""
    from wenart.blender import topdown as TD

    before = ([0.0, 0.0, 2.25], [10.0, 8.0, 3.0])                  # a veranda roof, 2.25-3.0 m
    assert TD.carve_grew(before, [(1.0, 1.0, 4.6), (9.0, 7.0, 2.3)]).startswith("rose from 3.00 to 4.60")
    assert TD.carve_grew(before, [(-0.5, 1.0, 2.5)]) == "spread past its own plan box"
    assert TD.carve_grew(before, [(1.0, 1.0, 2.9), (9.0, 7.0, 2.3)]) == ""
    src = (ROOT / "wenart" / "blender" / "topdown.py").read_text(encoding="utf-8")
    assert src.count("abs((rot @ p.normal).z) <= 0.5") == 1 and src.count("abs((rot @ f.normal).z) <= 0.5") == 1
    assert "grew = carve_grew(before.get(o.name), inside)" in src
    assert "qa = covers_qa(level_id" in src and '"covers_left": qa["covers_left"]' in src


def test_an_upper_floors_door_never_blocks_a_court_and_every_window_under_the_ground_counts():
    """R25 (real09: the L3 balcony doors over the basement facade had refused its courts; a room's windows under the
    ground are its main windows together)."""
    b = _basement("bedroom", width=1.5, height=1.2)
    b["levels"].append({"id": "L1", "elevation": 3.0, "ceiling_height": 2.7, "order": 1})
    b["rooms"].append({"id": "r_up", "level_id": "L1", "room_type": "bedroom", "polygon": _rect(0, 0, 8, 6)})
    b["walls"].append(_wall("wu", (8.1, 0), (8.1, 6), t=0.2, lid="L1"))
    b["openings"].append({"id": "du", "type": "door", "level_id": "L1", "wall_id": "wu", "center": [8.1, 3.0],
                          "width": 0.9, "height": 2.1})
    b["openings"].append(_window("v2", "wb", (8.1, 5.0), w=0.6, lid="L-1", height=1.2, sill_height=1.7))
    courts = [w for w in _wells(b) if w.get("kind") == "front_court"]
    assert courts and {"v1", "v2"} <= {i for c in courts for i in c["opening_ids"]}
