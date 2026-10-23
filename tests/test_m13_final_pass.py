"""Milestone 13 final pass (23 Oct 2026): the fixes from the analysis of pod P6c (real02; no pod verifies them, so
each test fails on the code P6c ran, or catches the mutation the verifier named).

What:

1. ``recognition.answers.rekey`` (verify:agent:1): an answer an item reads by input hash from another key is copied
   under the item's own key in two phases before ``seed_answers`` and ``ask`` write anything. P6c: the store held
   P4a's bench answers under sym_L1_007 / 008, read by this run's sym_L1_005 / 006; ``ask`` wrote the new armchair
   answers of 007 / 008 over them and recognition exited 2 with nothing failed and nothing left.
2. ``--answers --no-ai`` withdraws the code-typed questions as round 1 (verify:agent:0): ``core._ask_and_apply``
   records ``report["unanswered"]`` in every mode and ``reading.answered_keys`` subtracts it. P6c's first
   ``pipeline_final`` (--no-ai) kept the questions round 1 had withdrawn; the late pass answered them from the M11
   seeds and the drawn sofas f_L-1b_041 / 042 were built as kitchen islands.
3. ``agent.causes.cause_of``: a G3 within ``armchair_facing.max_angle`` but over ``max_distance`` is
   ``group_layout`` (verify:agent:3): P6c's f_L1_031 (12.1°, 2.734 m) was offered rotate / set_front / relayout only
   and the plan checker removed the move that fixes it.
4. tests/gpu/test_render.py ``test_closed_door_views_end_on_the_door`` (verify:look:0, test hygiene): a named view
   of a twin the build skipped under ``render.twin_rooms: one`` is checked on the first twin's views that see its
   mirrored doors; a name the project does not have is skipped, never failed.

How: CPU only, hand-made stores, reports, rooms and manifests (the run folders are not in the repository).
"""
from __future__ import annotations

import copy
import importlib.util
import json
import socket
from pathlib import Path
from types import SimpleNamespace

import pytest

import _m11_room as M
from wenart.agent import brief as BR
from wenart.agent import causes as CS
from wenart.agent import critic_code as CC
from wenart.agent import loop as LP
from wenart.furniture import edit_ops as E
from wenart.furniture import groups as GR
from wenart.ingest.generic import reading as RD
from wenart.recognition import answers as A

ROOT = Path(__file__).resolve().parents[1]
MODELS = A.load_models()
QWEN = MODELS["qwen"]["id"]


# --------------------------------------------------------------------------
# 1. The answer store: answers read by input hash are re-keyed before any write
# --------------------------------------------------------------------------

def _answer(ftype: str) -> dict:
    return {"type": ftype, "front": "none", "confidence": 0.9, "reason": "test"}


def _crops(key: str) -> list[str]:
    return [f"crops/{key}_ctx.png", f"crops/{key}_iso.png"]


def _item(key: str, h: str) -> dict:
    return {"key": key, "task": "symbol_type", "input_sha256": h * 64, "images": _crops(key)}


def _record(key: str, h: str, ftype: str) -> dict:
    return {"task": "symbol_type", "input_sha256": h * 64, "data": _answer(ftype), "raw_text": "", "error": None,
            "attempts": 1, "latency_s": 0.0, "model": QWEN, "seed": 0, "images": _crops(key)}


class _Client:
    """A vLLM stand-in: every question is answered "armchair" (P6c's new sym_L1_007 / 008)."""
    model = QWEN

    def __init__(self):
        self.asked = 0

    def run_schema(self, images, *args, **kw):
        self.asked += 1
        data = _answer("armchair")
        return SimpleNamespace(data=data, raw_text=json.dumps(data), error=None, attempts=1, latency_s=0.0,
                               max_tokens=64, finish_reason="stop", guard=[])


def _store(rec_dir: Path, stored: list[tuple]) -> None:
    store = A.AnswerStore.for_model(rec_dir, "qwen", MODELS)
    for key, h, ftype in stored:
        store.put(key, _record(key, h, ftype), save=False)
    store.save()


def _ask(rec_dir: Path, stored: list[tuple], items: list[dict], *extra) -> tuple[int, _Client, A.AnswerStore]:
    """``answers ask`` (the CLI, model key qwen) on ``items`` with ``stored`` = [(key, hash letter, type)] in the
    store before; a fake client unless ``extra`` names a server (then the real health check runs)."""
    A.write_requests(rec_dir, "t", items)
    _store(rec_dir, stored)
    client = _Client()
    factory = None if "--server" in extra else (lambda _info, _server: client)
    rc = A.main(["ask", str(rec_dir), "--model-key", "qwen", "--workers", "1", *extra], client_factory=factory)
    return rc, client, A.AnswerStore.for_model(rec_dir, "qwen", MODELS)


def _data(store: A.AnswerStore, key: str) -> str:
    return store.get(key)["data"]["type"]


def test_the_p6c_shift_keeps_the_answer_read_by_hash_from_the_asked_key(tmp_path):
    """Fails on the code P6c ran (rc 2, the bench answer of sym_L1_005 lost): the store holds K5 -> hash b and K7 ->
    hash c; this run's K5 is hash c (read by hash from K7) and K7 is new. The re-key copies K7's record under K5
    first, so asking K7 overwrites nothing another item reads."""
    rc, client, store = _ask(tmp_path, [("sym_L1_005", "b", "bench"), ("sym_L1_007", "c", "bench")],
                             [_item("sym_L1_005", "c"), _item("sym_L1_007", "d")])
    assert rc == A.EXIT_OK and client.asked == 1
    five = store.get("sym_L1_005")
    assert five["rekeyed_from"] == "sym_L1_007" and five["rekeyed_images"] == _crops("sym_L1_007")
    assert five["images"] == _crops("sym_L1_005") and five["input_sha256"] == "c" * 64
    assert (_data(store, "sym_L1_005"), _data(store, "sym_L1_007")) == ("bench", "armchair")
    assert A.status(tmp_path)["models"]["qwen"]["answered"] == 2


@pytest.mark.parametrize("case", ["keys_shift_up", "two_keys_swap"])
def test_shifted_or_swapped_keys_ask_only_the_new_item(tmp_path, case):
    """Catches a one-by-one copy (the verifier's scratch runs: 2 asked instead of 1, an answer lost) and, for the
    upward shift, fails on the code P6c ran (asking K3 overwrote the answer K5 reads, rc 2). Shift up: K3 new, K5
    was under K3, K7 was under K5. Swap: K1 and K2 swap their crops, K3 new."""
    if case == "keys_shift_up":
        stored = [("sym_L0_003", "a", "bench"), ("sym_L0_005", "b", "bed_double")]
        items = [_item("sym_L0_003", "e"), _item("sym_L0_005", "a"), _item("sym_L0_007", "b")]
        want = {"sym_L0_003": "armchair", "sym_L0_005": "bench", "sym_L0_007": "bed_double"}
    else:
        stored = [("sym_L0_001", "a", "bench"), ("sym_L0_002", "b", "bed_double")]
        items = [_item("sym_L0_001", "b"), _item("sym_L0_002", "a"), _item("sym_L0_003", "e")]
        want = {"sym_L0_001": "bed_double", "sym_L0_002": "bench", "sym_L0_003": "armchair"}
    rc, client, store = _ask(tmp_path, stored, items)
    assert rc == A.EXIT_OK and client.asked == 1
    assert {k: _data(store, k) for k in want} == want
    assert all(store.get(it["key"])["input_sha256"] == it["input_sha256"] for it in items)


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_a_seed_only_pass_without_a_server_keeps_swapped_keys(tmp_path):
    """Catches a one-by-one copy in the late pass (seeds only, no server): K1 and K2 swap, K3 comes from the seed
    folder. A one-by-one copy loses K2's answer, which then waits for a server that does not answer (rc 2)."""
    seed_dir = tmp_path / "seed"
    A.write_json(A.answers_path(seed_dir, MODELS["qwen"]["slug"]),
                 {"kind": "recognition_answers", "model": QWEN, "calls": {"sym_L0_003": _record("sym_L0_003", "e",
                                                                                                "armchair")}})
    rec_dir = tmp_path / "recognition"
    dead = f"http://127.0.0.1:{_free_port()}/v1"
    rc, _client, store = _ask(rec_dir, [("sym_L0_001", "a", "bench"), ("sym_L0_002", "b", "bed_double")],
                              [_item("sym_L0_001", "b"), _item("sym_L0_002", "a"), _item("sym_L0_003", "e")],
                              "--server", dead, "--seed-answers", str(seed_dir))
    assert rc == A.EXIT_OK
    assert [_data(store, k) for k in ("sym_L0_001", "sym_L0_002", "sym_L0_003")] == ["bed_double", "bench",
                                                                                     "armchair"]
    assert store.get("sym_L0_001")["rekeyed_from"] == "sym_L0_002"
    assert store.get("sym_L0_003")["seeded_key"] == "sym_L0_003"
    assert A.status(rec_dir)["complete"] is False                      # glm has none: only qwen was asked
    assert A.status(rec_dir)["models"]["qwen"]["answered"] == 3


# --------------------------------------------------------------------------
# 2. --answers --no-ai withdraws the code-typed questions as round 1
# --------------------------------------------------------------------------

def _two_box_page(path: Path) -> None:
    """The generic synthetic-06 page of tests/test_m13_ingest_fixround.py with two untyped boxes the core asks for
    (sym_L0_001, sym_L0_002)."""
    import ezdxf
    import test_m13_ingest_fixround as FX

    FX._generic_page(path, box=FX.BOX_HERE)
    doc = ezdxf.readfile(path)
    (x, y), (w, h) = FX.BOX_THERE
    block = doc.blocks.new("BOX-B")
    block.add_lwpolyline([(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)], close=True)
    doc.modelspace().add_blockref("BOX-B", (x, y), dxfattribs={"layer": "A-FURN"})
    doc.saveas(path)


def test_the_core_records_the_unanswered_keys_with_no_ai(tmp_path):
    """Fails on the code P6c ran: with answers for sym_L0_001 only, ``--no-ai`` leaves ``pending`` [] (nothing waits)
    and every question of the page counted as asked and answered in this round. ``report["unanswered"]`` now keeps
    sym_L0_002 in every mode, and ``answered_keys`` names sym_L0_001 only."""
    from wenart.ingest import dxf_generic as DG
    from wenart.ingest.generic import core

    path = tmp_path / "plan.dxf"
    _two_box_page(path)
    page = DG.read_page(path, "plan.dxf")
    first = core.extract(page, "L0", "plan.dxf")
    keys = [q["key"] for q in first.report["questions"]]
    assert keys == ["sym_L0_001", "sym_L0_002"] and first.report["pending"] == first.report["unanswered"] == keys
    answers = {"sym_L0_001": {"qwen": _answer("side_table"), "glm": _answer("side_table")}}
    for no_ai in (True, False):
        ex = core.extract(page, "L0", "plan.dxf", answers=answers, no_ai=no_ai)
        assert ex.report["answers_applied"] == 1 and ex.report[RD.UNANSWERED_KEY] == ["sym_L0_002"]
        assert ex.report["pending"] == ([] if no_ai else ["sym_L0_002"])
        works = {"page": SimpleNamespace(extraction=ex)}
        assert RD.answered_keys(SimpleNamespace(), works) == {"sym_L0_001"}


def test_answers_with_no_ai_withdraw_the_questions_of_the_plain_run_and_keep_an_answered_one():
    """Fails on the code P6c ran (0 withdrawn, 6 "kept: it was asked and answered in this round"): the dining drawing
    of ``test_the_questions_withdrawn_are_the_same_in_every_mode_and_an_answered_one_stays`` read as P6c's first
    ``pipeline_final``: --answers --no-ai (``pending`` []), the page got answers (the odd piece's question), the
    six code-typed questions round 1 withdrew have none (``unanswered``). They are withdrawn as in the plain run,
    with the same types; a question that really was answered (the table's) stays listed."""
    import test_reading_building as T

    sha = "0" * 64
    table = M.fp("t", "unknown", (2.5, 2.0), (1.24, 0.74), front=None, status="unverified")
    seats = [M.fp(f"c{k}", "unknown", c, (0.46, 0.38), front=None, status="unverified")
             for k, c in enumerate([(2.2, 1.4), (2.8, 1.4), (2.2, 2.6), (2.8, 2.6), (1.65, 2.0)])]
    odd = M.fp("q", "unknown", (4.4, 3.5), (0.3, 0.3), front=None, status="unverified")
    ids = ["t", "q"] + [s["id"] for s in seats]
    keys = {pid: f"sym_L0_{i + 1:03d}" for i, pid in enumerate(ids)}
    questions = [{"key": keys[pid], "task": "symbol_type", "images": [], "input_sha256": sha} for pid in ids]

    def read(report):
        build = T._build([copy.deepcopy(table), copy.deepcopy(odd)] + [copy.deepcopy(s) for s in seats],
                         room_type="dining", window=None)
        works = T._works(report=dict(report, questions=copy.deepcopy(questions)),
                         **{pid: {"candidate_key": keys[pid]} for pid in ids})
        RD.read_furniture(build, works)
        return build, works

    def kept(build):
        return sorted(w.split(" recognition question ")[1].split(" ")[0] for w in build.building["warnings"]
                      if "kept: it was asked and answered" in w)

    plain, plain_works = read({"pending": [keys[pid] for pid in ids]})
    want = set(plain_works["page"].extraction.report[RD.CODE_TYPED_KEY])
    assert want == {keys[pid] for pid in ids if pid != "q"}
    no_ai, works = read({"pending": [], RD.UNANSWERED_KEY: sorted(want), "answers_applied": 1})
    report = works["page"].extraction.report
    assert set(report[RD.CODE_TYPED_KEY]) == want and no_ai.code_typed_methods == plain.code_typed_methods
    assert kept(no_ai) == [] and RD.answered_keys(no_ai, works) == {keys["q"]}
    assert {f["id"]: f["type"] for f in no_ai.building["furniture"]} == \
        {f["id"]: f["type"] for f in plain.building["furniture"]}
    # the table's question was asked and answered in this round: it stays listed, the seats' are withdrawn
    answered, works = read({"pending": [], RD.UNANSWERED_KEY: sorted(want - {keys["t"]}), "answers_applied": 2})
    assert set(works["page"].extraction.report[RD.CODE_TYPED_KEY]) == want - {keys["t"]}
    assert kept(answered) == [keys["t"]]


# --------------------------------------------------------------------------
# 3. A G3 that faces its target but stands too far is a group layout (a move fixes it)
# --------------------------------------------------------------------------

def _g3(angle: float, distance: float, target: str = "f_L1_031") -> dict:
    """P6c's finding (seq 1401): armchair f_L1_031, 12.1° off the coffee table f_L1_023 at 2.734 m."""
    return CC.finding({"check": "G3", "severity": "major", "target": target, "room_id": M.ROOM_ID,
                       "message": f"armchair {target} is {angle:.0f}° off the table_coffee f_L1_023 (needs ≤ 30°) "
                                  f"at {distance:.2f} m (needs ≤ 2.50 m)",
                       "metrics": {"target": "f_L1_023", "angle_deg": angle, "distance_m": distance}})


def test_a_g3_within_the_angle_but_too_far_offers_the_moves():
    """Fails on the code P6c ran (G3 always ``orientation``: rotate_piece, set_front, relayout_room)."""
    rule = GR.rule("armchair_facing")
    assert (rule["max_angle"], rule["max_distance"]) == (30.0, 2.50)
    far = _g3(12.1, 2.734)
    assert CS.cause_of(far) == "group_layout"
    assert {"move_piece", "move_group"} <= set(CS.tools_for_finding(far))
    # the angle fails (with or without the distance): a rotation still fixes it first
    assert CS.cause_of(_g3(45.0, 2.734)) == CS.cause_of(_g3(45.0, 1.2)) == "orientation"
    assert CS.cause_of(_g3(30.0, 2.50)) == "orientation"                    # both on their limits: no move
    no_metrics = dict(far, evidence={"metrics": {}})
    assert CS.cause_of(no_metrics) == "orientation"


def test_the_plan_checker_keeps_a_move_for_a_far_armchair():
    """Fails on the code P6c ran: oyun_2's plan lost its move_piece ("move_piece does not fix c:G3:f_L1_032 (its
    tools: relayout_room, rotate_piece)"). Through the room brief (``brief.classify``) the far armchair's G3 offers
    move_piece, and ``check_plan`` keeps the step."""
    sofa = M.fp("f_L1_030", "sofa", (3.0, 0.5), (2.0, 0.9), source="added_by_ai")
    coffee = M.fp("f_L1_023", "table_coffee", (3.0, 1.6), (1.0, 0.6), source="added_by_ai")
    chair = M.fp("f_L1_031", "armchair", (3.0, 4.4), (0.8, 0.8), rotation=180.0, source="added_by_ai")
    b = M.building(w=6.0, h=5.0, room_type="living", window=None, furniture=[sofa, coffee, chair])
    brief = BR.room_brief(b, M.ROOM_ID, findings=[_g3(12.1, 2.734)], allowed_fn=E.allowed_edits)
    (fx,) = brief["findings"]["fixable"]
    assert fx["cause"] == "group_layout" and "move_piece" in fx["tools"]
    plan = {"room_id": M.ROOM_ID, "program": {"keep": True},
            "steps": [{"tool": "move_piece", "target": "f_L1_031", "finding_ids": [fx["id"]],
                       "why": "nearer the coffee table"}]}
    steps, problems = LP.check_plan(plan, brief, ["move_piece", "rotate_piece", "set_front", "relayout_room"])
    assert [s["tool"] for s in steps] == ["move_piece"] and problems == []


# --------------------------------------------------------------------------
# 4. The closed-door GPU test on a twin the build skipped (test hygiene)
# --------------------------------------------------------------------------

def _gpu_render_module(monkeypatch, outputs: Path):
    """tests/gpu/test_render.py imported against ``outputs`` (its env is read at import), as tests/test_m13_light.py
    does."""
    monkeypatch.setenv("WENART_OUTPUTS", str(outputs))
    monkeypatch.setenv("RENDER_TEST_PROJECTS", "real02")
    spec = importlib.util.spec_from_file_location("gpu_test_render_final_pass",
                                                  ROOT / "tests" / "gpu" / "test_render.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _corridors(tmp_path: Path) -> tuple[dict, dict]:
    """P6c's L1 corridors (real02): r_L1_koridor_2 is the mirror of r_L1_koridor about x = 7.5865 (its
    ``twin_transform``), d_L1_003 -> d_L1_006 and d_L1_001 -> d_L1_002; the replayed M11 views of r_L1_koridor see
    those doors only, the twin is skipped (``render.twin_rooms: one``)."""
    def room(rid, x0, x1, **extra):
        return dict({"id": rid, "level_id": "L1", "room_type": "hall", "polygon": [[x0, 7.5], [x1, 7.5], [x1, 9.0],
                                                                                    [x0, 9.0]]}, **extra)

    def door(did, x, y):
        return {"id": did, "type": "door", "level_id": "L1", "center": [x, y], "width": 0.82}

    building = {"rooms": [room("r_L1_koridor", 1.5, 3.0),
                          room("r_L1_koridor_2", 12.173, 13.673, twin_of="r_L1_koridor",
                               twin_transform=[-1.0, 0.0, 15.173, 0.0, 1.0, 0.0])],
                "openings": [door("d_L1_001", 2.3835, 7.518), door("d_L1_002", 12.7895, 7.518),
                             door("d_L1_003", 1.7505, 8.439), door("d_L1_006", 13.4225, 8.439),
                             {"id": "w_L1_001", "type": "window", "level_id": "L1", "center": [2.0, 9.0]}],
                "levels": [{"id": "L1"}]}
    path = tmp_path / "building_final.json"
    path.write_text(json.dumps(building), encoding="utf-8")
    seen = {"cam_r_L1_koridor_1": ["d_L1_003"], "cam_r_L1_koridor_2": ["d_L1_001", "d_L1_003"],
            "cam_r_L1_koridor_3": ["d_L1_001"], "cam_r_L1_koridor_4": ["d_L1_003", "w_L1_001"]}
    scene = {"building": str(path), "variant": {"id": "base"},
             "cameras": [{"name": n, "room_id": "r_L1_koridor", "visible_openings": v} for n, v in seen.items()]}
    render = {"renders": [{"camera": n, "room_id": "r_L1_koridor", "depth": {"max": 3.4, "coverage": 1.0}}
                          for n in seen]}
    render["renders"][-1]["depth"] = {"max": 75.0, "coverage": 0.95}        # sees the window: not a door view
    return scene, render


def test_the_closed_door_view_of_a_skipped_twin_is_checked_on_the_first_twins_door_views(tmp_path, monkeypatch,
                                                                                         capsys):
    """P6c: cam_r_L1_koridor_2_2 is not rendered (its room is a twin under ``render.twin_rooms: one``, as in M11).
    Before, the test skipped; now the first twin's views that see only doors, one mirrored into the twin, are
    checked (a leak through a door slit fails them) and the window view is left out."""
    gpu = _gpu_render_module(monkeypatch, tmp_path / "outputs")
    scene, render = _corridors(tmp_path)
    try:
        gpu.test_closed_door_views_end_on_the_door(("real02", scene, render))
    except pytest.skip.Exception as exc:                                # the test before the final pass
        pytest.fail(f"the closed-door test skipped the twin's door views: {exc}")
    out = capsys.readouterr().out
    assert "['cam_r_L1_koridor_1', 'cam_r_L1_koridor_2', 'cam_r_L1_koridor_3']" in out
    leak = copy.deepcopy(render)
    leak["renders"][0]["depth"] = {"max": 196.3, "coverage": 0.99966}     # P3's door slit
    with pytest.raises(AssertionError):
        gpu.test_closed_door_views_end_on_the_door(("real02", scene, leak))
    # a named view that was rendered is checked as before
    named = copy.deepcopy(render)
    named["renders"].append({"camera": "cam_r_L1_koridor_2_2", "depth": {"max": 196.3, "coverage": 0.99966}})
    with pytest.raises(AssertionError):
        gpu.test_closed_door_views_end_on_the_door(("real02", scene, named))


def test_the_closed_door_test_skips_a_project_without_the_named_room(tmp_path, monkeypatch):
    """real03 has no such camera or room (P4b / P6b skipped): still a skip with the reason, never a failure; a twin
    room without a door view and a missing building skip too."""
    gpu = _gpu_render_module(monkeypatch, tmp_path / "outputs")
    scene, render = _corridors(tmp_path)
    building = json.loads(Path(scene["building"]).read_text(encoding="utf-8"))
    other = tmp_path / "real03.json"
    other.write_text(json.dumps(dict(building, rooms=[dict(r, id=r["id"].replace("koridor", "salon"))
                                                      for r in building["rooms"]])), encoding="utf-8")
    with pytest.raises(pytest.skip.Exception, match="no room of the building"):
        gpu.test_closed_door_views_end_on_the_door(("real03", dict(scene, building=str(other)), render))
    windows = copy.deepcopy(scene)
    for c in windows["cameras"]:
        c["visible_openings"] = ["w_L1_001"]
    with pytest.raises(pytest.skip.Exception, match="twin of r_L1_koridor under render.twin_rooms: one"):
        gpu.test_closed_door_views_end_on_the_door(("real02", windows, render))
    with pytest.raises(pytest.skip.Exception, match="not readable"):
        gpu.test_closed_door_views_end_on_the_door(("real02", dict(scene, building=str(tmp_path / "none.json")),
                                                    render))
