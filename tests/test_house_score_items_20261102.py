"""2 Nov 2026 (user: "start with the score-budget table, then items 1-6"): the general rules for the house score's
critical findings (item 6) and the room, material, light and outside rules (items 1-5). CPU only."""
import json
from pathlib import Path

from wenart.blender import door_states as DS


def _bath():
    wall = {"id": "w1", "level_id": "L1", "start": [0.0, 0.0], "end": [6.0, 0.0], "thickness": 0.1}
    basin = {"id": "f_basin", "level_id": "L1", "type": "washbasin",
             "footprint": {"center": [2.6, 0.35], "size": [0.6, 0.45], "rotation_deg": 0.0}}
    door = {"id": "d1", "level_id": "L1", "wall_id": "w1", "center": [1.0, 0.0], "width": 0.8, "type": "door"}
    return {"furniture": [basin], "walls": [wall], "openings": [door]}, wall, door


def test_a_door_never_slides_into_the_fixed_equipment():
    """real04 run 20261101-093151-full: the attic bathroom door slid 0.50 m for head room onto the drawn washbasin."""
    b, wall, door = _bath()
    assert DS.doorway_clear(b, door, wall, 1.0)            # the drawn place: the basin is 1.3 m away
    assert not DS.doorway_clear(b, door, wall, 2.6)        # in front of the basin: its approach strip is taken
    b["furniture"][0]["build"] = False
    assert DS.doorway_clear(b, door, wall, 2.6)            # a piece not built is no obstacle


def _two_rooms(swing_into="r_bath", basin_y=0.45):
    level = {"id": "L1", "elevation": 0.0, "ceiling_height": 2.6}
    wall = {"id": "w1", "level_id": "L1", "start": [0.0, 0.0], "end": [6.0, 0.0], "thickness": 0.1, "height": 2.6}
    bath = {"id": "r_bath", "level_id": "L1", "room_type": "bathroom",
            "polygon": [[0, 0.05], [6, 0.05], [6, 3], [0, 3]]}
    hall = {"id": "r_hall", "level_id": "L1", "room_type": "hall", "polygon": [[0, -3], [6, -3], [6, -0.05], [0, -0.05]]}
    door = {"id": "d1", "level_id": "L1", "wall_id": "w1", "center": [2.0, 0.0], "width": 0.8, "height": 2.1,
            "type": "door", "swing_side": swing_into}
    basin = {"id": "f_basin", "level_id": "L1", "room_id": "r_bath", "type": "washbasin",
             "footprint": {"center": [2.0, basin_y], "size": [0.6, 0.45], "rotation_deg": 0.0}}
    return {"levels": [level], "walls": [wall], "rooms": [bath, hall], "openings": [door], "furniture": [basin]}


def test_a_door_whose_swing_sweeps_a_washbasin_opens_the_other_way():
    """2 Nov 2026 (user: "for doors to the washbasin, the door can open to the other side, and this can be a general
    rule, if it is hiding something or not opening properly it can open to the other way"; lesson UL257)."""
    b = _two_rooms()
    wall = b["walls"][0]
    door = b["openings"][0]
    fixed = DS.fixed_polys(b, "L1")
    assert DS.sweep_blocked(door, wall, 1, fixed) and not DS.sweep_blocked(door, wall, -1, fixed)
    states, assumed = DS.apply_states(b, {"family": "modern"})
    rec = states["d1"]
    assert rec.get("swing_turned") and rec["into"] == "r_hall" and "opens the other way" in rec["reason"]
    assert door["swing_side"] == "r_hall" and door["drawn_swing_side"] == "r_bath"
    assert door["adjusted_by_ai"]["by"] == "code" and any(a["kind"] == "door_swing_turned" for a in assumed)


def test_a_door_with_a_free_swing_keeps_its_drawn_side():
    b = _two_rooms(basin_y=2.5)                              # the basin far from the door
    states, _assumed = DS.apply_states(b, {"family": "modern"})
    assert not states["d1"].get("swing_turned") and b["openings"][0]["swing_side"] == "r_bath"


# ------------------------------------------------------------------ item 1: fuller styled rooms (decor)
def _decor_living(room_type="living", windows=()):
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from test_decor_m8 import room_building
    furniture = [("sofa", (3.0, 4.5), 0.0, (2.2, 0.9)), ("table_coffee", (3.0, 3.0), 0.0, (1.0, 0.6)),
                 ("side_table", (1.5, 4.6), 0.0, (0.45, 0.45)), ("side_table", (4.5, 4.6), 0.0, (0.45, 0.45)),
                 ("dresser", (5.75, 2.5), 270.0, (1.2, 0.5))]
    return room_building(room_type=room_type, furniture=furniture, windows=windows)


def test_an_untyped_room_is_dressed_by_what_stands_in_it():
    """2 Nov 2026 (item 1; real04's play-and-rest rooms held a sofa, typed "other" at decor time): an untyped room with
    a sofa is dressed as a living room, with a bed as a bedroom; its drawn type is kept and the change recorded."""
    from wenart.furniture import decor as D
    from wenart.furniture import decor_ai as DA
    b = _decor_living(room_type="other")
    room, pieces = D.rooms_with_pieces(b)[0]
    assert D.decor_room_type(room, pieces)[0] == "living"
    assert D.decor_room_type(dict(room, room_type="kitchen"), pieces) == ("kitchen", None)
    assert D.decor_room_type(room, [dict(pieces[0], type="bed_double")])[0] == "bedroom"
    assert D.decor_room_type(room, [dict(pieces[1])]) == ("other", None)
    view, changes = D.decor_view(b)
    assert view["rooms"][0]["room_type"] == "living" and b["rooms"][0]["room_type"] == "other"
    qs = DA.room_questions(b, "modern")
    assert qs and qs[0].room["room_type"] == "living" and "living labelled" in qs[0].prompts[1]
    out, records = DA.apply(b, "modern", {"answers": {}})
    assert out["rooms"][0]["room_type"] == "other"
    assert out["decor_room_types"][room["id"]]["to"] == "living"
    assert records[0].room_type == "living"


def test_every_styled_room_gets_its_layer_floor():
    """2 Nov 2026 (item 1): a living room without AI items gets art on two walls, two plants, a lamp on each side
    table, a throw, curtains at every window; the reasons name the floor; a sparse style asks one of each."""
    from wenart.furniture import decor_ai as DA
    b = _decor_living(windows=[("win_1", "s", 3.0, 1.2), ("win_2", "w", 2.5, 1.0)])
    q = DA.room_questions(b, "modern")[0]
    floor = DA.floor_recipe(q, None, "modern")
    assert floor["layers"]["table_lamps"]["median"] == 2.0 and floor["layers"]["wall_art"]["median"] == 2.0
    assert DA.floor_recipe(q, None, "japandi")["layers"]["wall_art"]["median"] == 1.0
    counter = {}

    def new_id(level):
        counter[level] = counter.get(level, 0) + 1
        return f"dec_{level}_{counter[level]:03d}"
    made = DA.ensure_layers(q, [], b, new_id, None, "modern")
    types = [d["type"] for d in made]
    lamps = [d for d in made if d["type"] == "table_lamp"]
    assert {d["host_id"] for d in lamps} == {"f_L0_003", "f_L0_004"}          # one on each side table
    assert types.count("curtain") == 2 and "throw" in types
    assert sum(t in ("plant", "plant_large", "plant_small") for t in types) >= 2
    assert all("layer floor" in d["reason"] for d in made)
    again = DA.ensure_layers(q, made, b, new_id, None, "modern")
    assert again == []                                                      # nothing twice


def test_the_minimum_counts_layers_and_large_rooms_take_a_third_picture():
    from wenart.furniture import decor as D
    from wenart.furniture import decor_ai as DA
    from wenart.furniture import tabletop as TT
    assert DA.styled_count([{"type": "cushion"}] * 4) == 2
    assert DA.styled_count([{"type": "cushion"}] * 4 + [{"type": "rug"}, {"type": "kettle"}]) == 4
    assert D.free_wall_art_most({"area_computed": 30.0}) == 3 and D.free_wall_art_most({"area_computed": 20}) == 2
    assert TT.GROUPS["nightstand"][1][0] == "table_lamp" and TT.GROUPS["side_table"][1][0] == "table_lamp"


# ------------------------------------------------------------------ item 3: matching sets (taste)
class _Taste:
    def __init__(self, attrs):
        self.attrs = attrs

    def get(self, entry):
        return self.attrs.get(entry["id"], {})


def test_a_room_takes_the_styles_wood_tone_and_one_contrast():
    """2 Nov 2026 (item 3; real04's salon mixed light and medium wood, black and brass): the style's tone and the first
    other tone the room took; a third tone costs steps even when the room took it before the style's tone."""
    from wenart.furniture import taste as T
    target = {"wood_tone": "medium", "metal": "black", "palette": []}
    room = {"tones": ["light", "dark"], "metal": "black"}
    assert T.steps({"wood_tone": "medium"}, room, target) == 0
    assert T.steps({"wood_tone": "light"}, room, target) == 0             # the contrast
    assert T.steps({"wood_tone": "dark"}, room, target) >= 2              # a third tone (was allowed before)
    assert T.steps({"wood_tone": "dark"}, {"tones": ["light", "dark"]}, {"palette": []}) == 0   # no style tone


def test_the_matching_model_is_tried_before_a_better_sized_other_one():
    from wenart.furniture import fit as F
    near = {"id": "a_dark", "bbox_m": [1.6, 0.9, 0.75], "units_known": True}
    off = {"id": "b_light", "bbox_m": [2.2, 0.9, 0.75], "units_known": True}       # 5 size steps worse
    cache = _Taste({"a_dark": {"wood_tone": "dark"}, "b_light": {"wood_tone": "light"}})
    got = F.rank_candidates([near, off], 1.6, 0.9, taste=(cache, {"tones": ["light"]}, {"wood_tone": "light",
                                                                                          "palette": []}))
    assert [e["id"] for e in got] == ["b_light", "a_dark"]          # the taste penalty alone (4 steps) kept a_dark


# ------------------------------------------------------------------ the lessons review fits the context
def test_the_lessons_review_fits_the_agent_models_context():
    """2 Nov 2026 (real10 run 20261102-122729-full: HTTP 400 "maximum context length is 32768 tokens", 30721 input
    tokens): a typical floor's copies are left out of the facts, the facts are counted per type when large, and the
    lessons go in batches that fit."""
    from wenart.agent import lessons as LS
    levels = [{"id": "L0"}, {"id": "L1"}] + [{"id": f"L{k}", "typical_of": "L1"} for k in range(2, 9)]
    rooms = [{"id": f"r_{lv['id']}_{k}", "level_id": lv["id"], "room_type": "bedroom",
              "polygon": [[0, 0], [4, 0], [4, 4], [0, 4]]} for lv in levels for k in range(12)]
    furniture = [{"id": f"f_{r['id']}_{k}", "room_id": r["id"], "type": "chair", "source": "added_by_ai"}
                 for r in rooms for k in range(12)]
    b = {"levels": levels, "rooms": rooms, "furniture": furniture, "decor": []}
    facts = LS.building_facts(b)
    assert {r["level"] for r in facts["rooms"]} == {"L0", "L1"} and len(facts["typical_copies"]) == 7
    todo = [{"id": f"UL{k}", "lesson": "x" * 400, "question": "y" * 100, "checks": []} for k in range(160)]
    budget = LS.prompt_chars_max()
    sent, batches = LS.review_batches(todo, facts, None)
    assert sum(len(x) for x in batches) == 160 and len(batches) > 1
    for batch in batches:
        assert len(json.dumps({"lessons": batch, "building": sent})) + len(LS.REVIEW_SYSTEM) <= budget
    big = dict(facts, rooms=facts["rooms"] * 6)
    assert LS.review_batches(todo[:3], big, None)[0].get("compact")


def test_an_agent_refit_keeps_the_rooms_set(tmp_path, monkeypatch):
    """2 Nov 2026 (item 3): the agent's refits rank by the room's set as the fit did (``fit.building_taste``)."""
    from wenart.furniture import fit as F
    b = {"project": {"taste": {"target": {"wood_tone": "light", "metal": "black"}}},
         "furniture": [{"id": "sofa", "type": "sofa", "room_id": "r", "asset": {"taste": {"wood_tone": "medium"}}},
                       {"id": "t", "type": "table_coffee", "room_id": "r", "asset": {"taste": {"metal": "brass"}}},
                       {"id": "x", "type": "chair", "room_id": "other", "asset": {"taste": {"wood_tone": "dark"}}}]}
    monkeypatch.delenv("WENART_ASSETS", raising=False)
    assert F.building_taste(b, {"id": "new", "room_id": "r"}) is None
    monkeypatch.setenv("WENART_ASSETS", str(tmp_path))
    cache, room, target = F.building_taste(b, {"id": "new", "room_id": "r"})
    assert room == {"tones": ["medium"], "metal": "brass"} and target == {"wood_tone": "light", "metal": "black",
                                                                          "palette": []}
    assert F.building_taste({"furniture": []}, {"id": "n"}) is None              # no fit record: as before


def test_a_stage_run_more_than_once_names_its_last_runs_own_time():
    """2 Nov 2026 (real10 run 20261102-122729-full: the job log's "build ok 3866.1s" was the running total of four
    builds of 13-18 min, read as one build of 64 min)."""
    from types import SimpleNamespace
    from wenart.run import scheduler as SC
    o = SC.Orchestrator.__new__(SC.Orchestrator)
    lines = []
    o.out = lines.append
    pr = SimpleNamespace(name="p", ref=SimpleNamespace(private=False),
                         parts={"build": [{"seconds": 1080.2}, {"seconds": 934.9}]})
    o.say(pr, "build", "ok", 2015.1, None)
    assert lines[-1] == "p build ok 2015.1s in all (run 2: 934.9s)"
    o.say(SimpleNamespace(name="p", ref=pr.ref, parts={"fit": [{"seconds": 17.1}]}), "fit", "ok", 17.1, None)
    assert lines[-1] == "p fit ok 17.1s"


# ------------------------------------------------------------------ the structure profile (a short pod run)
def test_the_structure_profile_renders_the_exterior_views_only(tmp_path):
    """2 Nov 2026 (user: "only run the top down views and outside views ... a very short pod run"): no agent, no
    test, the exterior cameras only, no export, no control set, no check."""
    from types import SimpleNamespace
    from wenart.run import __main__ as RM
    from wenart.run import scheduler as SC
    from wenart.run import state as ST
    man = {"cameras": [{"name": "cam_r_a_1", "kind": "interior"}, {"name": "ext_1", "kind": "exterior"},
                       {"name": "ext_2", "kind": "exterior"}]}
    assert SC.exterior_cameras(man) == ["ext_1", "ext_2"] and SC.exterior_cameras(None) == []
    assert SC.RunOptions(profile="structure").structure and not SC.RunOptions().structure
    assert "structure profile" in ST.SKIP_REASONS
    o = SC.Orchestrator.__new__(SC.Orchestrator)
    o.opts = SC.RunOptions(profile="structure")
    lines = []
    o.out = lines.append
    o.vlm_phase(8, "qwen")
    assert lines == ["phase 8: structure profile: no check"]
    calls = []
    pr = SimpleNamespace(active=True, base=None, out=tmp_path, name="p")
    (tmp_path / "scene").mkdir()
    (tmp_path / "scene" / "scene_manifest.json").write_text(json.dumps(man))
    o.runs = [pr]
    o.add_variant_runs = lambda: None
    o.stage_build = lambda p: calls.append("build")
    o.status_of = lambda p, s: "ok"
    o.scene_views = lambda p: 3
    o.stage_render = lambda p, cameras=None: calls.append(("render", cameras))
    o.stage_export = lambda p: calls.append("export")
    o.stage_controls = lambda p: calls.append("controls")
    o.skip = lambda p, stage, reason: calls.append(("skip", stage, reason))
    o.controls_run = lambda: None
    o.phase5()
    assert calls == ["build", ("render", ["ext_1", "ext_2"]), ("skip", "export", "structure profile"),
                     ("skip", "controls", "structure profile")]
    assert "structure" in open(RM.__file__).read()
