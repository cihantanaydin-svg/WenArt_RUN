"""27 Oct 2026 (user, on real06: a stair arriving on a strip the stair opening cuts off, a balcony left open that the
roof plan covers, a veranda like a carport: "The project needs to find these kind of things by itself without my
input" ... "Make argus catch these kind of things before me"): the outdoor spaces' checks (model review M10,
``wenart.blender.outdoor_review``), the outdoor floors and wood ceilings (``site.outdoor_floor_look``,
``site.down_faces``), one post language (``outdoor.post_look``) and Argus's visitor's walk (``argus_ai.visit``)."""
from __future__ import annotations

import json

import pytest

from wenart.agent.model import MockModel
from wenart.audit import argus_ai as AI
from wenart.audit import inputs as I
from wenart.blender import geom2d
from wenart.blender import outdoor_review as OR
from wenart.blender import site as S
from wenart.levels import outdoor as O


def _building():
    return {"levels": [{"id": "L0", "elevation": 0.0}, {"id": "L1", "elevation": 3.0}],
            "walls": [{"id": "w1", "level_id": "L1", "start": [0.0, 0.0], "end": [6.0, 0.0], "thickness": 0.2}],
            "openings": [{"id": "d1", "type": "door", "level_id": "L1", "center": [3.0, 0.0], "width": 0.9},
                         {"id": "win1", "type": "window", "level_id": "L1", "center": [1.0, 0.0], "width": 1.2}],
            "rooms": [], "furniture": [{"id": "f_L0_001", "type": "stair", "level_id": "L0",
                                        "stair": {"direction_assumed": True, "turn_assumed": True},
                                        "footprint": {"center": [1, 1], "size": [2, 2], "rotation_deg": 0}}],
            "site": {"outdoor_spaces": [{"id": "os_L1_b", "area_id": "sa_L1_b", "kind": "balcony", "label": "BALKON",
                                         "level_id": "L1"}]}}


def _balcony(**over):
    pf = {"id": "os_L1_b", "source": "outdoor_space", "z": 3.0, "elevated": True, "ground": {"min": 0.0},
          "polygon": [[0.0, -2.0], [6.0, -2.0], [6.0, 0.0], [0.0, 0.0]], "railing_edges": [0, 1, 3],
          "space": {"kind": "balcony", "label": "BALKON", "level_id": "L1", "doors": ["d1"], "cover": None},
          "posts": [], "material": None}
    pf.update(over)
    return pf


def test_outdoor_floors_are_never_the_garden_paving_and_undersides_are_wood():
    assert S.outdoor_floor_look({"source": "outdoor_space", "space": {"kind": "veranda"}})["material"] == "decking"
    assert S.outdoor_floor_look({"source": "outdoor_space", "space": {"kind": "balcony"}})["material"] == "paving_stone"
    assert S.outdoor_floor_look({"source": "outdoor_space", "space": {"kind": "balcony"}, "material": "x"}) is None
    assert S.outdoor_floor_look({"source": "drawn", "space": {"kind": "veranda"}}) is None
    assert "paving" not in S.OUTDOOR_FLOOR_LOOKS.values() and "grass" not in S.OUTDOOR_FLOOR_LOOKS.values()
    v, f = geom2d.box((0, 0, 3.0), (2, 2, 0.2), 0.0)
    slots = S.down_faces(v, f)
    assert sum(slots) == 1 and len(slots) == len(f)                  # the one bottom face takes the wood ceiling


def test_inferred_posts_take_the_drawn_columns_shape_and_size():
    rnd = O.post_look([{"size_m": 0.525, "shape": "round"}, {"size_m": 0.425, "shape": "round"},
                       {"size_m": 0.3, "shape": "rect", "size_xy": [0.3, 0.2]}])
    assert (rnd["size_m"], rnd["shape"]) == (0.425, "round")          # the common shape, its median size
    assert O.post_look([])["shape"] == "square" and O.post_look([])["size_m"] == O.SPACE["post_size"]
    posts = [{"size_m": 0.525, "source": "drawn", "id": "c1", "shape": "round"},
             {"size_m": 0.15, "source": "inferred", "id": None}]
    got, n = OR.review({"openings": [], "walls": []},
                       {"site": {"platforms": [_balcony(elevated=False, z=0.0, posts=posts,
                                                        space={"kind": "terrace", "doors": [], "level_id": "L0"},
                                                        steps_edge=1)]}})
    assert n == 1 and [x["metrics"]["rule"] for x in got] == ["O6"]
    posts[1].update(size_m=0.475, shape="round")
    got, _n = OR.review({"openings": [], "walls": []},
                        {"site": {"platforms": [_balcony(elevated=False, z=0.0, posts=posts,
                                                         space={"kind": "terrace", "doors": [], "level_id": "L0"},
                                                         steps_edge=1)]}})
    assert got == []


def test_m10_finds_a_balcony_nobody_can_reach_an_open_edge_and_a_roof_to_step_onto():
    b = _building()
    ok, n = OR.review(b, {"site": {"platforms": [_balcony()]}})
    assert n == 1 and ok == []                                       # door, guards, tiles: nothing to say
    # O1: only a window opens onto it
    got, _n = OR.review(b, {"site": {"platforms": [_balcony(space=dict(_balcony()["space"], doors=["win1"]))]}})
    assert [(x["metrics"]["rule"], x["severity"]) for x in got] == [("O1", "critical")]
    # O2: the south edge (index 0) open over 3 m
    got, _n = OR.review(b, {"site": {"platforms": [_balcony(railing_edges=[1, 3])]}})
    assert [(x["metrics"]["rule"], x["metrics"]["edge"]) for x in got] == [("O2", 0)]
    # O3: the garden paving on a balcony
    got, _n = OR.review(b, {"site": {"platforms": [_balcony(material="paving")]}})
    assert [x["metrics"]["rule"] for x in got] == ["O3"]
    # O4: a veranda half under a roof
    ver = _balcony(id="os_L0_v", z=0.0, elevated=False, ground={"min": 0.0}, steps_edge=1,
                   space={"kind": "veranda", "label": "VERANDA", "level_id": "L0", "doors": [], "cover": "roof"},
                   roof={"polygon": [[0.0, -2.0], [3.0, -2.0], [3.0, 0.0], [0.0, 0.0]], "top_z": 3.0})
    got, _n = OR.review(b, {"site": {"platforms": [ver]}})
    assert [x["metrics"]["rule"] for x in got] == ["O4"] and got[0]["metrics"]["covered"] == 0.5
    # O5: the veranda's roof beside a balcony at its floor level, along the balcony's unguarded edge
    bal = _balcony(polygon=[[3.0, -2.0], [6.0, -2.0], [6.0, 0.0], [3.0, 0.0]], railing_edges=[0, 1, 2])
    got, _n = OR.review(b, {"site": {"platforms": [ver, bal]}})
    rules = [x["metrics"]["rule"] for x in got]
    assert "O5" in rules and next(x for x in got if x["metrics"]["rule"] == "O5")["target"] == "os_L1_b"


def test_the_visitor_walks_every_stair_and_outdoor_space_and_reports_on_the_element(tmp_path):
    b = _building()
    qs = AI.visitor_questions(b, "L1")
    ids = [q["id"] for q in qs]
    assert ids == ["stair:f_L0_001", "outdoor:os_L1_b", "rooms:L1", "sense:L1"]
    assert "assumed" in qs[0]["ask"] and "0.8 m" in qs[0]["ask"]
    assert AI.visitor_questions(b, "L0")[0]["id"] == "start:f_L0_001"
    answers = {"answers": [
        {"id": "stair:f_L0_001", "verdict": "problem", "what": "the top step lands on a strip the stair opening cuts off",
         "element": "f_L0_001", "cause": "reading", "fix": "rule_needed", "value": "", "args": "",
         "rule": "a stair arrives on the floor that leads to the rooms"},
        {"id": "outdoor:os_L1_b", "verdict": "ok", "what": "", "element": "", "cause": "site", "fix": "rule_needed",
         "value": "", "args": "", "rule": ""},
        {"id": "sense:L1", "verdict": "problem", "what": "the balcony sits on the veranda's roof", "element": "BALKON",
         "cause": "site", "fix": "rule_needed", "value": "", "args": "", "rule": ""}]}
    def reply(body):                     # the floors are walked in parallel: answer by the floor's questions
        return answers if "sense:L1" in json.dumps(body.get("response_format")) else {"answers": []}
    model = MockModel(critic=[reply, reply])
    inp = I.Inputs(project="t", layout="results", root=tmp_path)
    inp.stages = [("final", b)]
    found, got = AI.visit(model, inp, ["facts"])
    assert len(got) == 3
    stair = next(f for f in found if f["target"] == "f_L0_001")
    assert stair["severity"] == "critical" and stair["check"] == "AI4" and stair["kind"] == "no_sense"
    assert "cuts off" in stair["message"]
    sense = next(f for f in found if f["check"] == "AI4" and f is not stair)
    assert sense["target"] == "os_L1_b"                               # the label the model named, as an element id
    schemas = [json.dumps(r["response_format"]) for r in model.critic_requests()]
    assert all("argus_visit" in s for s in schemas)


def test_an_exterior_view_of_a_veranda_is_judged_against_veranda_photos():
    from wenart.agent import judge as JD

    b = {"site": {"outdoor_spaces": [
        {"id": "os_v", "kind": "veranda", "doors": ["d1", "d2"], "polygon": [[0, -2], [4, -2], [4, 0], [0, 0]]},
        {"id": "os_b", "kind": "balcony", "doors": ["d7"], "polygon": [[2, -2], [4, -2], [4, 0], [2, 0]]}]}}
    assert JD.outdoor_space_of(b, {"visible_openings": ["d1", "d2", "d7"]}) == "veranda"
    assert JD.outdoor_space_of(b, {"visible_openings": ["d7"]}) == "balcony"
    assert JD.outdoor_space_of(b, {"visible_openings": [], "target": [1.0, -3.0]}) == "veranda"
    assert JD.outdoor_space_of(b, {"visible_openings": ["x"], "target": [20.0, 20.0]}) is None


def test_a_drawn_column_is_built_in_its_drawn_shape():
    # generality review of 27 Oct 2026: every drawn column of 0.2 m or more was built round
    circle = {"size": [0.42, 0.44], "evidence": [{"entity": "CIRCLE:1,LINE:2"}]}
    rect = {"size": [0.25, 0.5], "rotation_deg": 30.0, "evidence": [{"entity": "LINE:1,LINE:2,LINE:3,LINE:4"}]}
    square = {"size": [0.3, 0.3], "evidence": [{"entity": "LWPOLYLINE:9"}]}
    assert O.column_look(circle)["shape"] == "round" and O.column_look(circle)["size_m"] == 0.44
    r = O.column_look(rect)
    assert r["shape"] == "rect" and r["size_xy"] == [0.25, 0.5] and r["rotation_deg"] == 30.0 and r["size_m"] == 0.5
    assert O.column_look(square)["shape"] == "square"
    pf = {"roof": None, "posts": [dict(r, center=[0.0, 0.0], z0=0.0, z1=2.5, source="drawn", id="c1"),
                                  dict(O.column_look(circle), center=[3.0, 0.0], z0=0.0, z1=2.5, source="drawn",
                                       id="c2")]}
    parts = {q["part"]: q for q in S.cover_parts(pf)}
    verts = parts["posts"]["verts"]
    box = [v for v in verts if abs(v[0]) < 1.0]
    cyl = [v for v in verts if abs(v[0] - 3.0) < 1.0]
    assert len(box) == 8 and len(cyl) > 8                            # a box of the drawn footprint, a cylinder
    xs, ys = [v[0] for v in box], [v[1] for v in box]
    import math
    a = math.radians(30.0)
    assert max(xs) - min(xs) == pytest.approx(0.25 * math.cos(a) + 0.5 * math.sin(a), abs=1e-6)
    assert max(ys) - min(ys) == pytest.approx(0.25 * math.sin(a) + 0.5 * math.cos(a), abs=1e-6)
    # inferred posts copy the drawn rectangular columns
    look = O.post_look([dict(r, id="c1")])
    assert look["shape"] == "rect" and look["size_xy"] == [0.25, 0.5] and look["rotation_deg"] == 30.0
