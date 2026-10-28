"""28 Oct 2026 (user: "All these feedback needs to be understand by argus an Argus needs to be able to make these kind of
corrections in the future projects"): Argus's lessons line measures what the user pointed at (``wenart.audit.lessons``
U1-U14), its findings are re-checked after a fix (``argus_ai.target_gone``), every lesson is asked on the lesson walk
(``argus_ai.lesson_jobs``, check AI5), and the inspector's checklist holds the new visitor checks (Q10-Q15, X9, X10)."""
from __future__ import annotations

import copy
from pathlib import Path
from types import SimpleNamespace

import pytest

from test_decor_m8 import RID, room_building
from wenart.agent import causes as CS
from wenart.agent import prompts as P
from wenart.audit import argus_ai as AI
from wenart.audit import kinds as K
from wenart.audit import lessons as LS
from wenart.audit import report as R
from wenart.blender import architect_lessons as L


def _checks(found, check):
    return [f for f in found if f["check"] == check]


def test_an_entrance_at_a_window_is_found():
    b = room_building(windows=(("win1", "s", 3.0, 1.2),), doors=(("d1", "w", 2.5, 0.9),))
    b["site"] = {"entrances": [{"door_id": "win1"}, {"door_id": "d1"}]}
    got = LS.entrances_at_windows(b)
    assert [f["target"] for f in got] == ["win1"] and got[0]["evidence"]["lesson"] == "UL58"
    assert got[0]["kind"] == "no_sense" and got[0]["line"] == "lessons"


def test_storage_before_a_tall_window_is_found_and_the_fix_is_the_sill():
    b = room_building(furniture=[("dresser", (3.0, 0.25), 0.0, (1.0, 0.5))], windows=(("win1", "s", 3.0, 1.2),))
    assert LS.storage_before_tall_windows(b) == []                       # a 0.9 m sill: the dresser stands under it
    b["openings"][0]["sill_height"] = 0.1
    got = LS.storage_before_tall_windows(b)
    assert [f["target"] for f in got] == ["win1"] and "raise_sill win1" in got[0]["fix"]
    b["furniture"][0]["type"] = "nightstand"                             # low pieces are not storage before glass
    assert LS.storage_before_tall_windows(b) == []


def test_a_seat_facing_a_wall_is_found():
    flagged = []
    for rot in (0.0, 90.0, 180.0, 270.0):
        b = room_building(furniture=[("armchair", (3.0, 0.9), rot, (0.8, 0.8))])
        if LS.seats_facing_walls(b):
            flagged.append(rot)
    assert len(flagged) == 1                                             # only the turn that looks at the south wall


def test_indoor_pieces_outdoors_are_found():
    b = room_building(room_type="balcony", furniture=[("desk", (3.0, 2.0), 0.0, (1.2, 0.6)),
                                                      ("armchair", (1.0, 2.0), 0.0, (0.8, 0.8))])
    b["furniture"][1]["asset"] = {"title": "Teak Garden Lounge Chair"}
    b["decor"] = [{"id": "dec_1", "type": "rug", "room_id": RID}]
    got = LS.indoor_pieces_outdoors(b)
    assert sorted(f["target"] for f in got) == ["dec_1", "f_L0_001"]


def test_bathrooms_kitchens_and_tables_that_are_not_dressed_are_found():
    bath = room_building(3.0, 2.5, "bathroom", furniture=[("washbasin", (1.0, 0.3), 0.0, (0.6, 0.45))])
    assert [f["check"] for f in LS.basins_without_mirrors(bath)] == ["U10"]
    bath["decor"] = [{"id": "dec_m", "type": "mirror", "room_id": RID}]
    assert LS.basins_without_mirrors(bath) == []
    kit = room_building(4.0, 3.0, "kitchen", furniture=[("kitchen_counter", (2.0, 0.3), 0.0, (2.4, 0.6)),
                                                        ("table_dining", (2.0, 2.0), 0.0, (1.2, 0.8))])
    assert [f["check"] for f in LS.bare_worktops(kit) + LS.bare_dining_tables(kit)] == ["U11", "U12"]
    kit["decor"] = [{"id": "dec_k", "type": "kettle", "room_id": RID, "host_id": "f_L0_001"},
                    {"id": "dec_p", "type": "plate", "room_id": RID, "host_id": "f_L0_002"}]
    assert LS.bare_worktops(kit) + LS.bare_dining_tables(kit) == []


def _space(**roof):
    return {"id": "os_v", "level_id": "L0", "polygon": [[0, -3], [4, -3], [4, 0], [0, 0]], "roof": roof}


def test_outdoor_roofs_that_make_no_sense_are_found():
    b = room_building()
    b["site"] = {"outdoor_spaces": [_space(kind="light_roof", polygon=[[0, -3], [4, -3], [4, 0], [0, 0]],
                                           area_m2=12.0, roof_area_m2=12.0, drawn={"polygon": []})]}
    got = LS.traced_covers(b) + LS.flat_drawn_roofs(b)
    assert [f["check"] for f in got] == ["U5", "U4"]
    b["site"]["outdoor_spaces"] = [_space(kind="light_roof", polygon=[[-0.25, -3.25], [4.25, -3.25], [4.25, 0],
                                                                      [-0.25, 0]], area_m2=12.0, roof_area_m2=14.6)]
    assert LS.traced_covers(b) == []
    deep = {"id": "os_b", "level_id": "L0", "cover_source": "building_roof", "columns": [], "posts": [],
            "polygon": [[1, -2.5], [4, -2.5], [4, -0.1], [1, -0.1]]}
    b["site"]["outdoor_spaces"] = [deep]
    assert [f["check"] for f in LS.roofs_without_posts(b)] == ["U2"]
    deep["posts"] = [{"carries": "the building's roof over os_b"}]
    assert LS.roofs_without_posts(b) == []


def test_door_models_and_wall_finishes_are_checked_against_the_drawing_and_the_style():
    b = room_building(doors=(("d1", "s", 3.0, 2.0),))
    b["openings"][0]["door_type"] = "glazed_sliding"
    man = {"objects": [{"element_id": "d1", "library_model": {"title": "Folding Sliding Door - 4 Door",
                                                               "asset_id": "x"}}],
           "style_profile": {"walls": {"material": "plaster_white"}, "wall_accent": None,
                             "kitchen_walls": {"material": "wood_oak_light", "asset": "WoodFloor051"}}}
    assert [f["check"] for f in LS.door_operations(b, man)] == ["U7"]
    assert [f["target"] for f in LS.floor_finish_on_walls(man)] == ["kitchen_walls"]
    man["objects"].append({"kind": "wall", "name": "w_n", "room_ids": []})
    assert [f["target"] for f in LS.plain_walls(b, man)] == [RID]              # a living room with one paint
    man["objects"][-1].update(accent=True, room_ids=[RID])
    assert LS.plain_walls(b, man) == []


def test_the_line_runs_in_the_report_and_its_findings_are_rechecked_after_a_fix():
    assert "wenart.audit.lessons" in R.LINE_MODULES and "lessons" in R.HOUSE_LINES
    b = room_building(windows=(("win1", "s", 3.0, 1.2),))
    b["site"] = {"entrances": [{"door_id": "win1"}]}
    res = R.module_line("wenart.audit.lessons", SimpleNamespace(stage=lambda name: b, final=b, manifest=None))
    u1 = _checks(res["findings"], "U1")
    assert u1 and res["checked"]["U7"].startswith("no scene manifest")
    assert AI.target_gone(u1[0], {"building": b}) is False
    fixed = copy.deepcopy(b)
    fixed["site"]["entrances"] = []
    assert AI.target_gone(u1[0], {"building": fixed}) is True
    assert all(K.kind_of({"check": c, "line": "lessons"}) in K.KINDS for c in LS.CHECK_LESSONS)


def test_every_lesson_is_measured_or_asked():
    cov = LS.coverage()
    by = {x["id"]: x for x in L.lessons()}
    missing = [lid for lid, row in cov.items() if not row["code"] and not row["walk"] and by[lid]["area"] != "process"]
    assert missing == [], missing
    assert all(lid in by for ls in LS.CHECK_LESSONS.values() for lid in ls)
    inner = {q["lesson"] for q in LS.lesson_questions("interior")}
    outer = {q["lesson"] for q in LS.lesson_questions("exterior")}
    assert "UL66" in inner and "UL64" in outer and "UL25" not in inner | outer          # process lessons: never
    fresh = [{"id": "UL99", "area": "other", "status": "open", "request": "the lamps are too dim"}]
    assert "the lamps are too dim" in LS.lesson_questions("interior", fresh)[0]["ask"]  # asked from the day it is added


def test_the_lesson_walk_asks_every_lesson_per_floor_and_outside(tmp_path):
    b = room_building()
    imgs = [tmp_path / n for n in ("cam_r_L0_room_1_final_preview.jpg", "ext_1_final_preview.jpg")]
    inp = SimpleNamespace(images=imgs, top_plans=[])
    jobs = AI.lesson_jobs(b, inp)
    floors = [j for j in jobs if j[0] == "L0"]
    site = [j for j in jobs if j[0] == AI.LESSON_SITE]
    assert floors and site
    ids = [q["id"] for _lv, qs, _shown in jobs for q in qs]
    assert len(ids) == len(set(ids)) and all(q["kind"] == "lesson" for _lv, qs, _s in jobs for q in qs)
    assert floors[0][2][0][0].name.startswith("cam_r_L0_") and site[0][2][0][0].name.startswith("ext_")
    assert sum(len(qs) for _lv, qs, _s in floors) == len(LS.lesson_questions("interior"))
    assert all(len(qs) <= AI.VISIT_MAX_QUESTIONS for _lv, qs, _s in jobs)


class _Model:
    def __init__(self):
        self.calls = []

    def structured(self, messages, schema, **kw):
        self.calls.append(kw.get("call_id"))
        qids = schema["properties"]["answers"]["items"]["properties"]["id"]["enum"]
        answers = [{"id": q, "verdict": "problem" if "UL66" in q else "ok", "what": "the basin has no mirror",
                    "element": RID if "UL66" in q else "", "cause": "decor", "fix": "agent_round", "value": "",
                    "args": "", "rule": ""} for q in qids]
        return SimpleNamespace(data={"answers": answers})


def test_a_lesson_problem_becomes_an_ai5_finding_on_the_named_element(tmp_path, monkeypatch):
    b = room_building()
    inp = SimpleNamespace(final=b, images=[tmp_path / "cam_r_L0_room_1_final_preview.jpg"], top_plans=[])
    monkeypatch.setattr("wenart.agent.model.user_message", lambda text, images, labels: {"role": "user",
                                                                                         "content": text})
    model = _Model()
    found, answers = AI.visit(model, inp, ["fact"])
    ai5 = [f for f in found if f["check"] == "AI5"]
    assert ai5 and all(f["target"] == RID for f in ai5) and ai5[0]["evidence"]["lesson"] == "UL66"
    assert any(str(c).startswith("argus_lessons_L0") for c in model.calls)


def test_the_inspector_asks_what_the_user_pointed_at():
    new = ("Q10", "Q11", "Q12", "Q13", "Q14", "Q15")
    assert set(new) <= set(P.ROOM_LOOK_CHECKS) and set(new) <= set(P.VISITOR_CHECKS)
    assert {"X9", "X10", "Q10"} <= set(P.EXTERIOR_CHECKS)
    for c in new + ("X9", "X10"):
        assert P.CHECKLIST[c]["how"] == "V" and CS.CHECK_CAUSE[c] in CS.CAUSES and K.kind_of({"check": c}) != "other"
    assert "glazed frame on a piece of furniture" in P.CHECKLIST["D2"]["what"]


def test_the_doors_of_the_house_are_checked_for_variety():
    man = {"objects": [{"kind": "door", "element_id": f"d{i}", "library_model": {"asset_id": "x", "title": "Front Door",
                                                                                "category": "door"}}
                       for i in range(4)]}
    got = LS.door_variety(man)
    assert got and all(f["check"] == "U15" and f["evidence"]["lesson"] == "UL65" for f in got)
    assert LS.door_variety({"objects": []}) == []


def test_a_labelled_area_built_as_its_outdoor_space_is_a_built_fact():
    """real06 run 154514: Argus AI's fact sheet said the VERANDA and BALKON areas were 'NOT built (no outline)' (the
    areas hold no polygon; their outdoor spaces os_L0_veranda / os_L1_balkon do) and it raised two false major
    findings; the fact names the outdoor space now (``conservation.outdoor_built``)."""
    b = room_building()
    b["site"] = {"areas": [{"id": "sa_L0_veranda", "label": "VERANDA", "kind": "other"},
                           {"id": "sa_L0_x", "label": "BAHCE", "kind": "other"}],
                 "outdoor_spaces": [dict(_space(), id="os_L0_veranda", area_id="sa_L0_veranda")]}
    lines = AI.facts(b)
    assert any("sa_L0_veranda" in x and "built as the outdoor space os_L0_veranda" in x for x in lines)
    assert any("sa_L0_x" in x and "NOT built" in x for x in lines)
