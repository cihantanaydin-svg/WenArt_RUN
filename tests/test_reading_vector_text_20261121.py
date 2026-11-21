"""21 Nov 2026 (Milestone 14 queue item 3: the drawing's exact vector data as text beside each image of the AI checks).

What: the serializer on a synthetic plan drawn in millimetres: the frame (metres from the image's top-left corner, y
down), the units (a 200-unit gap is a 0.20 m wall), a rotated and a mirrored page transform (the reading's walls and
rooms come back onto the drawn lines, sizes unchanged), the crop frame of a close-up (coordinates from the crop's
corner, a wall crossing it kept), the token cap (never passed, the left-out count said), the same ids in the text and
the image overlay; the prompts behind the switch (``CRITIC_VECTOR_TEXT=0`` asks exactly what round 2 asked), the
A/B arms of one ask against the fake vLLM server, the judge question of a code check's finding with its label, the
text-alone rules of the offline measure, and C0008: the critic's known errors match the user's corrections on the
reading as the score reads it (the outdoor spaces included).
Why: the critic guessed numbers and labels from pixels; the text must place every item where the image shows it,
or the model is told the wrong thing.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

from wenart.ingest.generic.model import GenericPage, Stroke, TextRun
from wenart.reading_check import critic as CR
from wenart.reading_check import critic_checks as CC
from wenart.reading_check import critic_judge as CJ
from wenart.reading_check import score as SC
from wenart.reading_check import truth as TR
from wenart.reading_check import vector_measure as VM
from wenart.reading_check import vector_text as VT

REPO = Path(__file__).resolve().parents[1]
FAKES = REPO / "tests" / "fakes"
BOX = [0.0, 0.0, 20000.0, 10000.0]                 # millimetres: a 20 x 10 m image
S = 0.001
TFS = {"straight": [S, 0.0, 5.0, 0.0, S, 3.0],
       "rotated": [0.0, -S, 30.0, S, 0.0, 2.0],    # the page turned 90 degrees into the building
       "mirrored": [-S, 0.0, 25.0, 0.0, S, 1.0]}   # the page mirrored (negative determinant)


def _apply(tf, p):
    return [tf[0] * p[0] + tf[1] * p[1] + tf[2], tf[3] * p[0] + tf[4] * p[1] + tf[5]]


def _line(i, a, b, layer):
    return Stroke(id=f"ent:{i}", kind="line", pts=[tuple(a), tuple(b)], layer=layer)


def _page():
    c30, s30 = math.cos(math.radians(30)), math.sin(math.radians(30))
    a0 = (10000.0, 2000.0)
    a1 = (a0[0] + 4000 * c30, a0[1] + 4000 * s30)
    off = (-200 * s30, 200 * c30)
    strokes = [_line(1, (2000, 5000), (8000, 5000), "DUVAR"), _line(2, (2000, 5200), (8000, 5200), "DUVAR"),
               _line(3, a0, a1, "DUVAR"), _line(4, (a0[0] + off[0], a0[1] + off[1]), (a1[0] + off[0], a1[1] + off[1]),
                                                "DUVAR"),
               Stroke(id="ent:5", kind="arc", pts=[(9900, 5000), (9000, 5900)], layer="KAPI",
                      arc={"center": (9000.0, 5000.0), "radius": 900.0, "start_deg": 0.0, "end_deg": 90.0}),
               _line(6, (3000, 9800), (4500, 9800), "PENCERE"), _line(7, (3000, 9900), (4500, 9900), "PENCERE"),
               _line(8, (3000, 9800), (3000, 10000), "PENCERE"), _line(9, (4500, 9800), (4500, 10000), "PENCERE")]
    strokes += [_line(20 + k, (15000, 6000 + 280 * k), (16200, 6000 + 280 * k), "MERDIVEN") for k in range(8)]

    def t(i, text, x, y, h=250.0):
        return TextRun(id=f"TEXT:{i}", text=text, box=(x, y, x + 120 * len(text), y + h), height=h)

    texts = [t(1, "SALON", 4000, 6000), t(2, "18,40 m2", 4000, 5650), t(3, "+3.00", 12000, 8000),
             t(4, "150/130", 3200, 9300), t(5, "450", 6000, 5400), t(6, "NORMAL KAT PLANI", 2000, 500)]
    return GenericPage(file="plan.dxf", page=1, source_kind="dxf", units="dxf", units_to_m=S, size=(20000, 10000),
                       strokes=strokes, texts=texts)


def _facts(tf):
    room = [_apply(tf, p) for p in ((2000, 5200), (8000, 5200), (8000, 9200), (2000, 9200))]
    return {"rooms": [{"id": "r_L0_salon", "label": "Salon", "type": "living", "area": 24.0, "poly": room,
                       "at": _apply(tf, (5000, 7200))}],
            "outdoor": [], "openings": [{"id": "d_L0_1", "type": "door", "at": _apply(tf, (9000, 5100)), "width": 0.9,
                                         "sides": ["r_L0_salon", "outside"], "exterior": True}],
            "stairs": [], "lifts": []}


def _wall(tf):
    return {"id": "w_L0_1", "level_id": "L0", "start": _apply(tf, (2000, 5100)), "end": _apply(tf, (8000, 5100)),
            "thickness": 0.2, "exterior": True, "evidence": [{"layer": "DUVAR", "method": "vector"}]}


# =============================================================================================== frame and units
@pytest.mark.parametrize("name", list(TFS))
def test_the_frame_reads_as_drawn_for_a_straight_rotated_and_mirrored_transform(name):
    tf = TFS[name]
    fr = VT.Frame(BOX, tf)
    assert math.isclose(fr.w, 20.0) and math.isclose(fr.h, 10.0) and math.isclose(fr.s, S)
    assert fr.from_page((0, 10000)) == (0.0, 0.0)                          # the image's top-left corner
    assert all(math.isclose(a, b, abs_tol=1e-9) for a, b in zip(fr.from_page((20000, 0)), (20.0, 10.0)))
    for p in ((2000, 5100), (17000, 300)):
        q = fr.from_building(_apply(tf, p))
        assert all(math.isclose(a, b, abs_tol=1e-9) for a, b in zip(q, fr.from_page(p)))
        assert all(math.isclose(a, b, abs_tol=1e-9) for a, b in zip(fr.to_building(q), _apply(tf, p)))


@pytest.mark.parametrize("name", list(TFS))
def test_drawn_items_are_in_metres_and_the_reading_lands_on_the_drawn_lines(name):
    tf = TFS[name]
    fr = VT.Frame(BOX, tf)
    vec = VT.level_vector(_page(), fr, _facts(tf), [_wall(tf)], {"DUVAR"})
    src = {it["k"] + str(i): it for i, it in enumerate(vec["source"])}
    walls = [it for it in vec["source"] if it["k"] == "W"]
    straight = next(w for w in walls if VT._off_axis(w["deg"]) < 1)
    assert straight["t"] == 0.2 and math.isclose(straight["a"][1], 4.9, abs_tol=0.01)
    assert sorted([straight["a"][0], straight["b"][0]]) == [2.0, 8.0]
    angled = next(w for w in walls if VT._off_axis(w["deg"]) > 3)
    assert abs(angled["deg"] - 30.0) < 0.5 and angled["t"] == 0.2         # the drawing's own angle, whatever tf
    arc = next(it for it in vec["source"] if it["k"] == "A")
    assert arc["door"] and arc["r"] == 0.9 and arc["p"] == [9.0, 5.0]
    win = next(it for it in vec["source"] if it["k"] == "G")
    assert win["w"] == 1.5 and math.isclose(win["p"][0], 3.75, abs_tol=0.01)
    stair = next(it for it in vec["source"] if it["k"] == "S")
    assert stair["n"] == 8
    label = next(it for it in vec["source"] if it["k"] == "T")
    assert label["text"] == "SALON" and label["area"] == 18.4
    kinds = {it["k"]: it for it in vec["source"]}
    assert kinds["K"]["text"] == "+3.00" and kinds["Z"]["text"] == "150/130" and kinds["D"]["text"] == "450"
    assert kinds["X"]["text"] == "NORMAL KAT PLANI" and src
    # the reading's wall sits on the drawn pair's centre line, its room keeps its size, the door its place
    w = next(it for it in vec["reading"] if it["k"] == "w")
    ends = sorted([tuple(w["a"]), tuple(w["b"])])
    assert all(math.isclose(a, b, abs_tol=0.01) for p, q in zip(ends, sorted([tuple(straight["a"]),
                                                                              tuple(straight["b"])]))
               for a, b in zip(p, q))
    room = next(it for it in vec["reading"] if it["k"] == "r")
    assert room["size"] == [6.0, 4.0] and room["bid"] == "r_L0_salon"
    door = next(it for it in vec["reading"] if it["k"] == "d")
    assert door["p"] == [9.0, 4.9] and door["sides"] == ["r1", "outside"]
    assert "r1 room 'Salon' living 24.0 m2 6.00x4.00" in VT.item_line(room)


# ===================================================================================== crop, cap, ids and tags
def test_a_close_up_lists_from_its_own_corner_and_keeps_a_wall_crossing_it():
    fr = VT.Frame(BOX, TFS["straight"])
    vec = VT.level_vector(_page(), fr, _facts(TFS["straight"]), [_wall(TFS["straight"])], {"DUVAR"})
    blk = VT.block(vec, what="the close-up", region=(4.0, 3.0, 6.0, 6.0), sides=("source", "reading"))
    assert "it is 2.00 m wide and 3.00 m high" in blk["text"]
    w = next(it for it in vec["source"] if it["k"] == "W" and VT._off_axis(it["deg"]) < 1)
    assert w["id"] in blk["ids"]                                           # both ends outside the crop: kept
    line = next(x for x in blk["text"].splitlines() if x.startswith(w["id"] + " "))
    assert "(-2.0,1.9)-(4.0,1.9)" in line                                  # from the crop's corner (4, 3)
    assert not any(i.startswith("G") for i in blk["ids"])                  # the window lies outside the crop


def test_the_token_cap_is_never_passed_and_the_left_out_count_is_said():
    fr = {"box": BOX, "tf": TFS["straight"], "m_per_unit": S, "w": 20.0, "h": 10.0}
    dims = [{"id": f"D{i + 1}", "k": "D", "p": [5.0 + (i % 20) * 0.01, 5.0], "text": str(100 + i)} for i in range(400)]
    vec = {"frame": fr, "source": dims, "reading": []}
    assert VT.block(vec, focus=[("mark 1", (5.0, 5.0))], cap_tokens=150)["listed"] == 0   # the header alone
    for cap in (400, 800, 2400):
        blk = VT.block(vec, focus=[("mark 1", (5.0, 5.0))], cap_tokens=cap)
        assert blk["tokens"] <= cap and blk["left_out"] > 0 and blk["listed"] > 0
        assert f"({blk['left_out']} more items" in blk["text"]
    assert VT.cap_for(10000, 2048, [(1600, 1600)] * 2) == 0                 # nothing left in the context
    assert VT.cap_for(1000, 500, [(1600, 800)]) == VT.CAP_TOKENS
    assert VT.question_block("inventory", {}, vec, cap_tokens=0) is None
    assert VT.estimate_tokens("(12.3,4.5)-(6.7,8.9)") >= 16                 # a digit or a sign is a token


def test_the_ids_of_the_overlay_are_the_texts_and_sit_at_their_items(tmp_path):
    from PIL import Image

    fr = VT.Frame(BOX, TFS["straight"])
    vec = VT.level_vector(_page(), fr, _facts(TFS["straight"]), [_wall(TFS["straight"])], {"DUVAR"})
    blk = VT.block(vec, focus=[("mark 1", (9.0, 5.0))], cap_tokens=2400, tags=True)
    assert "tagged in blue" in blk["text"] and blk["tags"]
    lines = blk["text"].splitlines()
    for tid, side, nx, ny in blk["tags"]:
        assert any(x.strip().startswith(tid + " ") for x in lines)
        assert (side == "source") == tid[0].isupper()
    arc = next(t for t in blk["tags"] if t[0].startswith("A"))
    assert math.isclose(arc[2], 0.45) and math.isclose(arc[3], 0.5)
    Image.new("RGB", (200, 100), "white").save(tmp_path / "d.jpg")
    out = VT.tag_image(tmp_path / "d.jpg", [("A1", "source", 0.5, 0.5), ("r1", "reading", 0.2, 0.2)],
                       tmp_path / "t.jpg", "source")
    im = Image.open(out).convert("RGB")
    px = im.getpixel((100, 50))
    assert px[2] > 150 and px[0] < 100                                     # the blue dot at the item
    assert min(im.getpixel((40, 20))) > 200                                # a model id is not on the drawing


# ============================================================================================== prompts and arms
def _entry(tmp_path):
    from PIL import Image

    folder = tmp_path / "inputs" / "s" / "p"
    folder.mkdir(parents=True)
    Image.new("RGB", (1600, 800), "white").save(folder / "L0_drawing.jpg")
    Image.new("RGB", (1600, 800), "white").save(folder / "L0_model.jpg")
    tf = TFS["straight"]
    fr = VT.Frame(BOX, tf)
    facts = dict(_facts(tf), drawn_labels=[{"text": "SALON", "at": _apply(tf, (4300, 6100)), "exterior": False}],
                 drawn_angled=[], angled_walls=[], entrances=[], window_places=[], above_ground=False, axis_deg=0.0)
    VT.write_vector(folder / "L0_vector.json", VT.level_vector(_page(), fr, facts, [_wall(tf)], {"DUVAR"}))
    e = {"id": "s/p/L0", "level": "L0", "box": BOX, "tf": tf, "size": [1600, 800], "folder": "s/p",
         "drawing": "L0_drawing.jpg", "model": "L0_model.jpg", "copies": [], "set": "s", "project": "p",
         "facts": facts, "vector": "L0_vector.json", "title": "ZEMIN KAT"}
    e["compare"] = CC.compare_questions(e, facts)
    e["compare_chunk"] = CC.COMPARE_CHUNK
    e["mark_layout"] = 2
    return e


def test_the_switch_leaves_the_prompts_as_they_were_and_adds_the_text_when_on(tmp_path):
    e = _entry(tmp_path)
    root = tmp_path / "inputs"
    chunk = CC.chunks_of(e)[0]
    assert CC.compare_prompt(e, chunk, None) == CC.compare_prompt(e, chunk)
    off, _s = CR._check_messages("compare", e, root, 0, 1600, tmp_path / "m", vt="0")
    meta: dict = {}
    on, _s = CR._check_messages("compare", e, root, 0, 1600, tmp_path / "m", vt="1", meta=meta)
    text_off, text_on = off[1]["content"][-1]["text"], on[1]["content"][-1]["text"]
    assert text_off == CC.compare_prompt(e, chunk) and text_on.startswith(text_off)
    assert "Exact data read from the drawing file" in text_on and "mark 1 at" in text_on
    assert meta["tokens"] <= meta["cap"] and meta["listed"] > 0
    inv, _s = CR._check_messages("inventory", e, root, 0, 1600, tmp_path / "m", vt="text")
    assert "T1 label 'SALON' 18.40 m2" in inv[1]["content"][-1]["text"]
    assert "tagged in blue" not in inv[1]["content"][-1]["text"]          # text only: no tags drawn
    text = {"id": "s/p/L0#text", "folder": "s/p", "vector": "L0_vector.json", "text": "Storey L0.",
            "ids": {"room": ["r_L0_salon"]}, "points": {"r_L0_salon": _facts(TFS["straight"])["rooms"][0]["at"]}}
    pl, _s = CR._check_messages("plausibility", text, root, 0, 1600, None, vt="1")
    body = pl[1]["content"][-1]["text"]
    assert "- r_L0_salon: T1 'SALON' 18.40 m2" in body and body.index("Questions:") > body.index("r_L0_salon:")
    assert CR.arms_of("0,1") == ("0", "1") and CR.arms_of(None, env={}) is None
    assert CR.arms_of(None, env={"CRITIC_VECTOR_TEXT": "1"}) == ("1",) and VT.mode({"CRITIC_VECTOR_TEXT": "x"}) == "0"


def test_one_ask_runs_both_arms_on_the_same_calls_against_the_fake_server(tmp_path):
    sys.path.insert(0, str(FAKES))
    from fake_vlm import FakeVLM
    from wenart.agent import model as AM

    e = _entry(tmp_path)
    index = {"entries": [e], "texts": [], "readings": {}}
    which = ("inventory", "compare")
    with FakeVLM() as url:
        model = AM.from_check_yaml(url, "agent", parallel=2)
        res = CR.ask(index, model, tmp_path / "inputs", tmp_path / "out", which=which, sets=["s"], arms=("0", "1"),
                     log=lambda *_a: None)
    jobs = CR.check_jobs(index, which, ["s"])
    assert res["stats"]["answered"] == 2 * len(jobs) and res["arms"] == ["0", "1"]
    arms = CR.split_arms(res)
    assert set(arms) == {"0", "1"} and all(len(v["answers"]) == len(jobs) for v in arms.values())
    assert all(a.get("vector") for a in arms["1"]["answers"]) and not any(a.get("vector") for a in arms["0"]["answers"])
    for arm in ("0", "1"):
        saved = json.loads((tmp_path / "out" / f"arm_{arm}" / "answers.json").read_text(encoding="utf-8"))
        assert {a["arm"] for a in saved["answers"]} == {arm}
    assert any((tmp_path / "out" / "arm_1" / "marked").glob("*_vt.jpg"))     # the tagged images of the B arm
    scored = VM.score_arms(index, res)
    assert set(scored) >= {"0", "1"} and scored["0"]["answered"] == len(jobs)


# ======================================================================================================== judge
def test_a_judge_item_carries_its_crop_label_and_question():
    tf = TFS["straight"]
    corners = ((2000, 2000), (5000, 2000), (5000, 4500), (2000, 4500))
    rooms = [{"id": "r_L1_oda", "level_id": "L1", "polygon": [_apply(tf, p) for p in corners]}]
    building = {"rooms": rooms}
    e = {"id": "judge/p/L1", "folder": "judge/p", "drawing": "L1_drawing.jpg", "model": "L1_model.jpg",
         "size": [1600, 800], "box": BOX, "tf": tf, "vector": "L1_vector.json", "title": "1. KAT"}
    f = {"check": "RC18", "rule": "light_air", "severity": "minor", "level_id": "L2", "place": None,
         "element_ids": ["r_L1_oda"], "message": "PAIY 32(1): bedroom r_L1_oda has no window to the outside"}
    reg = {("p", "L2", "r_L1_oda", "light_air"): {"label": "reading_error", "why": "a window drawn"}}
    items = CJ.items_of(building, [f], {"L1": e}, {"L2": "L1"}, "p", "p", reg, {})
    assert len(items) == 1
    it = items[0]
    assert it["label"] == "reading_error" and it["page_entry"] == "judge/p/L1" and it["level"] == "L2"
    x0, y0, x1, y1 = it["crop"]
    assert math.isclose(x1 - x0, 6.0) and math.isclose(y1 - y0, 6.0)        # the minimum close-up, square
    q = CJ.prompt(it)
    assert "no window to the outside" in q and "real_breach" in q and "the rule: a bedroom" in q
    assert CJ.schema()["properties"]["verdict"]["enum"] == list(CJ.VERDICTS)
    answers = {"answers": [{"id": it["id"], "which": "judge", "data": {"verdict": "reading_error", "reason": "G4"}}]}
    rows = CJ.verdicts({"judge": items}, answers)
    acc = CJ.accuracy(rows)
    assert rows[0]["right"] is True and acc["RC18"]["accuracy"] == 1.0 and acc["all"]["labelled"] == 1
    assert CR.check_jobs({"judge": items, "entries": [dict(e, judge_only=True, facts={}, set="judge")]},
                         ("judge", "inventory"), ["judge"]) == [("judge", it, 0)]


def test_the_text_alone_rules_of_the_offline_measure():
    items = [{"id": "T1", "k": "T", "p": [5.0, 5.0], "text": "SALON", "type": "living"},
             {"id": "T2", "k": "T", "p": [9.0, 1.0], "text": "BALKON", "type": "balcony", "exterior": True},
             {"id": "A1", "k": "A", "p": [3.0, 3.0], "r": 0.9, "sweep": 90, "door": True},
             {"id": "G1", "k": "G", "p": [7.0, 7.0], "w": 1.2},
             {"id": "W1", "k": "W", "a": [0.0, 9.0], "b": [4.0, 6.7], "t": 0.2, "deg": 30.0}]
    assert VM.text_answer({"kind": "room"}, items, (5.5, 5.0)) == "yes"
    assert VM.text_answer({"kind": "room"}, items, (9.0, 1.0)) is None      # an outdoor label is no room
    assert VM.text_answer({"kind": "opening"}, items, (3.4, 3.0)) == "door"
    assert VM.text_answer({"kind": "opening"}, items, (7.0, 7.2)) == "window"
    assert VM.text_answer({"kind": "angled"}, items, (2.0, 7.85)) == "yes"
    assert VM.text_answer({"kind": "balcony"}, items, (8.0, 2.0)) == "yes"
    assert VM.evident(["balcony_missing"], items, (9.5, 1.5)) is True
    assert VM.evident(["storey_count_differs"], items, (0, 0)) is None


# ================================================================================================ C0008
def test_the_known_errors_read_the_user_corrections_as_the_score_does(monkeypatch):
    bal = [[0.0, 0.0], [2.0, 0.0], [2.0, 2.0], [0.0, 2.0]]
    building = {"project": {"id": "p"}, "levels": [{"id": "L0", "label": "Zemin", "elevation": 0.0, "order": 0}],
                "rooms": [], "openings": [], "walls": [], "furniture": [],
                "site": {"outdoor_spaces": [{"id": "os_1", "level_id": "L0", "kind": "balcony", "label": "Balkon",
                                             "polygon": bal}]}}
    truth = {"sparse": True, "project": "p", "levels": [{"id": "L0"}],
             "per_level": {"L0": {"outdoor": [{"id": "u_C9_1", "label": "Balkon", "outdoor_kind": "balcony",
                                               "polygon": bal, "centroid": [1.0, 1.0], "corrections": ["C9"]}]}}}
    assert "outdoor" not in TR.extract(building, project="p")["per_level"]["L0"]   # the cause: no sparse fields
    res = SC.match_sparse(truth, SC.reading_for(truth, building, "p"), building)
    assert [x["satisfied"] for x in res["entries"]] == [True]
    monkeypatch.setattr(TR, "load_truth", lambda project, *a, **k: truth)
    known = CC.sparse_known("p", building)
    assert len(known) == 1 and known[0]["fixed"] is True and "holds" in known[0]["desc"]
    building["site"]["outdoor_spaces"] = []
    assert CC.sparse_known("p", building)[0]["fixed"] is False
