"""Architectural details and the open-air rooms (25 Oct 2026, user: "better architectural details needed, better
internal stairs, better finishes in the fences on top of the parapets" and "the architect should ask: is that table
on the terrace ok? is it suitable for the terrace? is the door to the terrace ok?"; "pillows on beds and sofas seem
to float"). CPU, pure."""
import json
import math
from pathlib import Path

import pytest

from wenart.blender import architect_actions as AA
from wenart.blender import architect_details as AD
from wenart.blender import details as D
from wenart.blender import geom2d
from wenart.blender import parametric as P
from wenart.blender import rest as R
from wenart.furniture import fit as F

ROOT = Path(__file__).resolve().parents[1]
REAL04 = ROOT / "results" / "furniture" / "real04" / "building_agent.json"


def _closed(verts, faces) -> bool:
    edges = {}
    for f in faces:
        for a, b in zip(f, f[1:] + f[:1]):
            edges[(a, b)] = edges.get((a, b), 0) + 1
    return all(edges.get((b, a)) == 1 for (a, b) in edges)


@pytest.mark.parametrize("kind", D.KINDS)
def test_every_balustrade_kind_is_a_closed_guard_one_metre_high(kind):
    metal, glass = D.balustrade((0.0, 0.0), (3.0, 0.0), 0.5, 1.0, kind)
    assert metal and all(_closed(v, f) for v, f in metal + glass)
    top = max(p[2] for v, _f in metal + glass for p in v)
    assert top == pytest.approx(1.5, abs=0.005)
    if kind == "bars":                                   # no 0.1 m sphere passes between two bars
        bars = [(min(p[0] for p in v), max(p[0] for p in v)) for v, _f in metal
                if max(p[0] for p in v) - min(p[0] for p in v) < 0.05 and max(p[2] for p in v) > 1.2]
        bars.sort()
        assert len(bars) > 15 and max(b[0] - a[1] for a, b in zip(bars, bars[1:])) <= 0.11 + 1e-6
    else:
        assert glass
    cap = D.coping((0.0, 0.0), (3.0, 0.0), 1.0, 0.2)
    assert max(p[2] for p in cap[0]) == pytest.approx(1.0 + D.DIMS["coping_t"])
    assert max(p[1] for p in cap[0]) == pytest.approx(0.1 + D.DIMS["coping_proud"])


def test_the_balustrade_follows_the_style_and_a_tube_can_have_an_exact_top():
    assert D.balustrade_kind({"family": "modern"}) == "glass_channel"
    assert D.balustrade_kind({"family": "rustic"}) == "bars"
    assert D.balustrade_kind({"family": "modern", "railing": {"material": "black steel balusters"}}) == "bars"
    assert D.balustrade_kind(None) == D.DEFAULT_KIND
    v, f = D.tube((0, 0, 1.0), (2.0, 0, 1.0), 0.02, 12, 0.0)
    assert max(p[2] for p in v) == pytest.approx(1.02) and _closed(v, f)


def _straight_stair(walls_both_sides: bool):
    piece = {"id": "s", "type": "stair", "footprint": {"center": [0.5, 1.5], "size": [1.0, 3.0], "rotation_deg": 0.0},
             "stair": {"flights": [{"start": [0.5, 0.0], "end": [0.5, 2.8], "width": 1.0, "lines": 15}],
                       "landing": None, "direction": [0.0, 1.0]}}
    walls = [{"id": "wl", "start": [-0.1, -1.0], "end": [-0.1, 4.0], "thickness": 0.2},
             {"id": "wr", "start": [1.1, -1.0], "end": [1.1, 4.0], "thickness": 0.2}] if walls_both_sides else []
    return P.stair_plan(piece, 2.85, 2.70, walls=walls)


def test_a_stair_has_tread_plates_with_nosings_a_balustrade_and_a_wall_handrail():
    plan = _straight_stair(False)
    parts = P.stair_parts(dict(plan, balustrade="bars"))
    roles = {p["role"] for p in parts}
    assert {"step", "tread", "riser", "rail", "post", "baluster"} <= roles
    treads = [p for p in parts if p["role"] == "tread"]
    steps = [p for p in parts if p["role"] == "step"]
    assert len(treads) == len(steps) == 14
    # every tread but the first overhangs the riser below by the nosing
    first = min(min(v[1] for v in t["verts"]) for t in treads)
    assert first == pytest.approx(0.0, abs=1e-9)
    glass = P.stair_parts(dict(plan, balustrade="glass_channel"))
    assert any(p["key"] == "glass" for p in glass) and not any(p["role"] == "baluster" for p in glass)
    slots = P.stair_face_slots(glass)
    assert 3 in slots and len(slots) == sum(len(p["faces"]) for p in glass)
    walled = P.stair_parts(_straight_stair(True))
    assert not _straight_stair(True)["rails"] and {"rail", "bracket"} <= {p["role"] for p in walled}


def test_outdoor_models_rank_first_on_a_terrace():
    teak = {"id": "a", "name": "Reclaimed Teak Dining Table", "material_tags": ["wood"]}
    desk = {"id": "b", "name": "Writing desk with drawer", "material_tags": ["wood"]}
    sofa = {"id": "c", "name": "Sofa", "material_tags": ["fabric", "wood"]}
    bistro = {"id": "d", "name": "Table", "material_tags": ["metal"]}
    plain = {"id": "e", "name": "Table", "material_tags": ["wood", "glass"]}
    assert [F.outdoor_grade(e) for e in (teak, desk, sofa, bistro, plain)] == [0, 2, 2, 0, 1]


def test_a_cushion_is_not_built_on_a_model_with_its_own_and_sinks_into_a_soft_seat():
    bed = {"type": "bed_double", "asset": {"has_pillows": True}}
    sofa = {"type": "sofa", "asset": {"has_scatter_cushions": True}}
    assert R.own_cushions(bed) and R.own_cushions(sofa)
    assert not R.own_cushions({"type": "sofa", "asset": {"has_cushions": True}})     # UL180: loose seat cushions
    assert not R.own_cushions({"type": "sofa", "asset": {"has_pillows": True}})
    assert not R.own_cushions({"type": "bed_double", "asset": {}})
    assert R.LEAN_DEG >= 18.0 and R.HEADBOARD_LEAN_DEG >= R.LEAN_DEG and 0.0 < R.SOFT_SINK_M <= 0.03


def _terrace_building(source="added_by_ai"):
    return {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}], "walls": [], "openings": [],
            "rooms": [{"id": "t", "level_id": "L0", "room_type": "terrace",
                       "polygon": [[0, 0], [5, 0], [5, 3], [0, 3]]}],
            "furniture": [{"id": "w", "type": "wardrobe", "room_id": "t", "level_id": "L0", "source": source,
                           "footprint": {"center": [1, 1], "size": [1.2, 0.6], "rotation_deg": 0.0}},
                          {"id": "d", "type": "desk", "room_id": "t", "level_id": "L0", "source": "from_documents",
                           "footprint": {"center": [3, 1], "size": [1.2, 0.6], "rotation_deg": 0.0}},
                          {"id": "c", "type": "chair", "room_id": "t", "level_id": "L0", "source": "added_by_ai",
                           "asset": {"method": "library", "asset_id": "x", "outdoor_grade": 0},
                           "footprint": {"center": [3, 2], "size": [0.5, 0.5], "rotation_deg": 0.0}}]}


def test_the_architect_takes_inside_pieces_off_a_terrace_and_asks_about_drawn_ones():
    b = _terrace_building()
    q = AD.outdoor_furniture(AA.Plan(b))
    by = {a["element"]: a for a in q["answers"]}
    assert b["furniture"][0]["build"] is False and "inside piece" in by["w"]["change"]
    assert by["d"].get("open") and {o["choice"] for o in by["d"]["options"]} >= {"remove_piece",
                                                                                   "retype_piece:table_dining"}
    assert "made for outside" in by["c"]["found"]
    # the answer carries it out: the drawn desk is the terrace's table
    recs = AA.apply_answers(b, {"U1:d": {"option": "retype_piece", "params": {"type": "table_dining"}}})
    assert recs[0]["ok"] and b["furniture"][1]["type"] == "table_dining" and b["furniture"][1]["drawn_type"] == "desk"
    recs = AA.apply_answers(b, {"U1:d": {"option": "remove_piece"}})
    assert recs[0]["ok"] and b["furniture"][1]["build"] is False


@pytest.mark.skipif(not REAL04.is_file(), reason="no committed real04 building")
def test_real04_architect_asks_about_terraces_stairs_and_guards():
    from wenart.blender import build as BU

    prep = BU.prepare(json.loads(REAL04.read_text(encoding="utf-8")), "base", None, style_family="modern")
    q = {x["id"]: x for x in prep["architect"]["questions"]}
    assert {"U1", "D3", "K1", "K2", "K3"} <= set(q)
    assert q["D3"]["counts"]["asked"] >= 2                                  # the two roof-terrace doors
    # real04's stairs are drawn with too few treads for a 3 m storey: the architect turns their landings into winders
    assert q["K1"]["status"] == "fixed" and all("winders" in (a.get("change") or "") for a in q["K1"]["answers"])
    assert any("coping" in (a.get("change") or "") for a in q["K2"]["answers"])
    assert "glass channel" in q["K3"]["answers"][0]["change"]


def _u_stair(winders=None):
    flights = [{"start": [0.0, 0.0], "end": [1.4, 0.0], "width": 0.95, "lines": 6},
               {"start": [0.27, 1.15], "end": [1.39, 1.15], "width": 0.95, "lines": 5}]
    data = {"flights": flights, "landing": {"polygon": [[1.4, -0.475], [1.4, 1.625], [2.67, 1.625], [2.67, -0.475]]},
            "direction": [1.0, 0.0], "turn": "U"}
    if winders is not None:
        data["winders"] = winders
    return {"id": "st", "type": "stair", "footprint": {"center": [1.33, 0.57], "size": [2.67, 2.1], "rotation_deg": 0},
            "stair": data}


def test_a_steep_u_stair_gets_winders_in_its_half_landing():
    """25 Oct 2026 (user: "better internal stairs"; real04: 11 lines for a 3 m storey, 0.25 m risers): the half
    landing turns into winders around the well; the footprint stays, the risers become comfortable."""
    steep = P.stair_plan(_u_stair(), 3.0)
    assert steep["riser_m"] == pytest.approx(3.0 / 11) and steep["landing"]["role"] == "mid" and not steep["winders"]
    plan = P.stair_plan(_u_stair("auto"), 3.0)
    k = plan["winders"]
    assert k == 6 and plan["risers"] == 17 and plan["riser_m"] == pytest.approx(3.0 / 17)
    a, b = plan["flights"]
    assert b["base_z"] == pytest.approx(a["top_z"] + k * plan["riser_m"]) and b["top_z"] == pytest.approx(3.0)
    tops = [w["top"] for w in plan["landing"]["winders"]]
    # 28 Oct 2026 (parametric.WINDER_TREADS_NOTE): k risers in the turn are k + 1 treads, the first at the landing's
    # level (no double step after the first flight's last riser), the last at the second flight's foot
    assert tops == pytest.approx([a["top_z"] + j * plan["riser_m"] for j in range(k + 1)])
    assert tops[-1] == pytest.approx(b["base_z"])
    # the winders tile the landing
    from shapely.geometry import Polygon
    area = sum(Polygon(w["polygon"]).area for w in plan["landing"]["winders"])
    assert area == pytest.approx(1.27 * 2.1, rel=1e-3)
    parts = P.stair_parts(plan)
    assert sum(1 for p in parts if p["role"] == "winder") == k + 1 and not any(p["role"] == "landing" for p in parts)
    assert P.stair_plan(_u_stair(0), 3.0)["winders"] == 0


@pytest.mark.skipif(not REAL04.is_file(), reason="no committed real04 building")
def test_real04_stairs_get_winders_and_the_answer_can_keep_them_as_drawn():
    from wenart.blender import build as BU

    b = json.loads(REAL04.read_text(encoding="utf-8"))
    prep = BU.prepare(b, "base", None, style_family="modern")
    k1 = next(q for q in prep["architect"]["questions"] if q["id"] == "K1")
    assert k1["status"] == "fixed" and all("winders" in (a.get("change") or "") for a in k1["answers"])
    assert all(any(o["choice"] == "stair_winders:0" for o in a.get("options") or []) for a in k1["answers"])
    # the user's answer "keep it as drawn" is carried out on the next build
    b["architect_answers"] = {"K1:f_L0_001": {"option": "stair_winders", "params": {"count": 0}}}
    prep2 = BU.prepare(b, "base", None, style_family="modern")
    k1b = next(q for q in prep2["architect"]["questions"] if q["id"] == "K1")
    kept = next(a for a in k1b["answers"] if a["element"] == "f_L0_001")
    assert "riser 0.286 m" in kept["found"] and not kept.get("open")             # answered: steep as drawn
    from wenart.blender import shell
    lv = next(x for x in prep2["building"]["levels"] if x["id"] == "L0")
    plans = {i["piece"]["id"]: i["plan"] for i in shell.plan_stairs(prep2["building"], lv) if i["plan"]}
    assert plans["f_L0_001"]["winders"] == 0 and plans["f_L0_002"]["winders"] > 0
