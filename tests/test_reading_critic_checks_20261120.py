"""20 Nov 2026 (RC15 checks 1, 2, 4: the user chose options 1, 2 and 4 for the structure stage).

What: the inventory comparison (each kind at its point in metres, a mirrored twin instead of a missing room, a
written storey count), the compare question generator (the order, the caps, what the reading has at each mark, the
chunks), the floor summary (rooms, door joins, exterior windows, balcony doors, stairs, lifts) and the mapping of
answers to findings (a contradiction only, the confidence by how the model read image 2, ids that exist and are of
the asked class); the judging against known errors and fixed places; the review sheets (stable numbers, at most 30 a
sheet, under 2 MB, ``findings_index.json``) and the user's marks; the whole ask path of the three checks against the
fake vLLM server on the committed input set's entries, then the calibration and the sheets.
Why: the 6 Nov open differences call gave 570 findings, nearly all false; closed questions about marked places and a
typed inventory compared by code must be measured kind by kind before they are trusted.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from wenart.reading_check import critic as CR
from wenart.reading_check import critic_checks as CC

REPO = Path(__file__).resolve().parents[1]
FAKES = REPO / "tests" / "fakes"
BOX = [0.0, 0.0, 20.0, 10.0]          # drawing units = metres (tf identity), 2:1 frame
TF = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]


def _entry(**kw):
    return dict({"id": "s/p/L0", "level": "L0", "box": BOX, "tf": TF, "size": [1600, 800], "folder": "s/p",
                 "drawing": "L0_drawing.jpg", "model": "L0_model.jpg", "copies": [], "set": "s", "project": "p"}, **kw)


def _sq(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _facts():
    return {"level": "L0", "axis_deg": 0.0, "above_ground": True,
            "rooms": [{"id": "r1", "label": "Salon", "type": "living", "at": [3.0, 5.0], "area": 30.0,
                       "poly": _sq(0, 0, 6, 10)},
                      {"id": "r2", "label": "Oda", "type": "bedroom", "at": [17.0, 5.0], "area": 30.0,
                       "poly": _sq(14, 0, 20, 10)}],
            "outdoor": [], "stairs": [{"id": "f1", "at": [10.0, 5.0], "room_id": None}], "lifts": [],
            "openings": [{"id": "d1", "type": "door", "at": [6.0, 5.0], "width": 0.9, "exterior": False,
                          "sides": ["r1", "unknown"], "front": None},
                         {"id": "d2", "type": "door", "at": [19.5, 3.0], "width": 0.9, "exterior": True,
                          "sides": ["r2", "outside"], "front": "nothing"},
                         {"id": "w1", "type": "window", "at": [0.5, 5.0], "width": 1.2, "exterior": True,
                          "sides": ["r1", "outside"], "front": None}],
            "entrances": [], "angled_walls": [],
            "drawn_labels": [{"text": "SALON", "at": [3.0, 5.0], "exterior": False},
                             {"text": "MUTFAK", "at": [10.0, 8.5], "exterior": False},
                             {"text": "BALKON", "at": [10.0, 0.5], "exterior": True}],
            "drawn_angled": [{"a": [7.0, 1.0], "b": [12.0, 3.0], "mid": [9.5, 2.0], "deg": 21.8, "length": 5.4}]}


def _px(x, y):
    """Metres -> the 0-1000 point the model answers (frame BOX, origin top left)."""
    return int(round(x / 20.0 * 1000)), int(round((10.0 - y) / 10.0 * 1000))


# ================================================================================================== inventory
def test_inventory_comparison_writes_each_kind_at_its_point_in_metres():
    sx, sy = _px(3.0, 5.0)
    mx, my = _px(10.0, 8.5)
    tx, ty = _px(10.0, 5.0)
    s2x, s2y = _px(12.0, 1.5)
    bx, by = _px(10.0, 0.5)
    a0, a1 = _px(7.0, 1.0), _px(12.0, 3.0)
    data = {"rooms": [{"label": "SALON", "x": sx, "y": sy}, {"label": "MUTFAK", "x": mx, "y": my}],
            "mirror": {"axis": "none", "position": 500},
            "stairs": [{"x": tx, "y": ty}, {"x": s2x, "y": s2y}], "lifts": [{"x": tx, "y": ty}],
            "balconies": [{"kind": "balcony", "x": bx, "y": by}],
            "entrance": {"shown": True, "street_side": "bottom", "x": bx, "y": by},
            "angled_walls": [{"x0": a0[0], "y0": a0[1], "x1": a1[0], "y1": a1[1]}],
            "storeys": {"names": ["ZEMIN KAT", "1. KAT"], "count": 4}}
    found = CC.inventory_findings(data, _entry(), _facts(), {"storeys": 2, "storeys_without_roof": 2})
    kinds = sorted(f["kind"] for f in found)
    assert kinds == ["angled_wall_straight", "balcony_missing", "entrance_missing", "lift_missing", "room_missing",
                     "stair_missing", "storey_count_differs"]
    room = next(f for f in found if f["kind"] == "room_missing")
    assert abs(room["at"][0] - 10.0) < 0.05 and abs(room["at"][1] - 8.5) < 0.05 and "MUTFAK" in room["description"]
    stair = next(f for f in found if f["kind"] == "stair_missing")
    assert abs(stair["at"][0] - 12.0) < 0.05                     # the stair at (10, 5) is the reading's own
    ang = next(f for f in found if f["kind"] == "angled_wall_straight")
    assert abs(ang["at"][0] - 9.5) < 0.05 and abs(ang["at"][1] - 2.0) < 0.05
    st = next(f for f in found if f["kind"] == "storey_count_differs")
    assert st["at"] is None and "4 storeys" in st["description"]
    assert len({f["key"] for f in found}) == len(found)
    # the count the reading has (with or without a roof storey) is no finding; a model wall at the angle follows it
    facts = dict(_facts(), angled_walls=[{"id": "w9", "a": [7.0, 1.0], "b": [12.0, 3.0], "deg": 21.8}])
    found2 = CC.inventory_findings(dict(data, storeys={"names": [], "count": 2}), _entry(), facts, {"storeys": 2})
    assert not {"storey_count_differs", "angled_wall_straight"} & {f["kind"] for f in found2}


def test_a_listed_mirror_pair_with_one_half_missing_is_a_mirror_twin_finding():
    # the axis at x = 10 m (500): Oda at (17, 5) mirrors (3, 5); a second pair at (17, 2) / (3, 2): only (17, 2) read
    facts = _facts()
    facts["rooms"][0]["poly"] = _sq(0, 3, 6, 10)                  # the left room no longer covers (3, 2)
    facts["rooms"][0]["at"] = [3.0, 6.5]
    data = {"rooms": [{"label": "BANYO", "x": 850, "y": 800},
                      {"label": "BANYO", "x": 150, "y": 800}],
            "mirror": {"axis": "vertical", "position": 500}, "stairs": [], "lifts": [], "balconies": [],
            "entrance": {"shown": False, "street_side": "unknown", "x": 0, "y": 0}, "angled_walls": [],
            "storeys": {"names": [], "count": 0}}
    found = CC.inventory_findings(data, _entry(), facts, None)
    assert [f["kind"] for f in found] == ["mirror_twin_missing"]
    assert abs(found[0]["at"][0] - 3.0) < 0.05 and abs(found[0]["at"][1] - 2.0) < 0.05
    assert found[0]["element_ids"] == ["r2"]


# =================================================================================================== compare
def test_compare_questions_ask_rooms_first_with_what_the_reading_has_at_each_mark():
    qs = CC.compare_questions(_entry(), _facts())
    kinds = [q["kind"] for q in qs]
    assert kinds[:3] == ["room", "room", "room"] and "angled" in kinds and "balcony" in kinds and "opening" in kinds
    assert kinds == sorted(kinds, key=["room", "angled", "balcony", "opening"].index)
    byat = {tuple(q["at"]): q for q in qs}
    assert byat[(3.0, 5.0)]["model_fact"] == "yes" and byat[(10.0, 8.5)]["model_fact"] == "no"
    assert (10.0, 0.5) not in byat                                # a balcony label is no room question
    assert byat[(9.5, 2.0)]["model_fact"] == "yes"                # drawn angled, no model wall follows: straight
    bal = next(q for q in qs if q["kind"] == "balcony")
    assert bal["element_ids"] == ["d2"] and bal["model_fact"] == "no"
    assert [q["n"] for q in qs] == list(range(1, len(qs) + 1)) and qs[0]["qid"] == "q1"
    assert all(0 < q["point"][0] < 1 and 0 < q["point"][1] < 1 for q in qs)
    # the caps: at most COMPARE_MAX a level, COMPARE_CHUNK a call
    many = dict(_facts(), drawn_labels=[{"text": f"ODA {i}", "at": [0.5 + (i % 19), 0.5 + (i // 19) * 1.0],
                                         "exterior": False} for i in range(150)])
    qs2 = CC.compare_questions(_entry(), many)
    assert len(qs2) <= CC.COMPARE_MAX and sum(1 for q in qs2 if q["kind"] == "room") <= CC.COMPARE_CAPS["room"]
    chunks = CC.compare_chunks(qs2)
    assert all(len(c) <= CC.COMPARE_CHUNK for c in chunks) and sum(len(c) for c in chunks) == len(qs2)


def test_compare_answers_become_findings_only_where_the_drawing_contradicts_the_reading():
    qs = CC.compare_questions(_entry(), _facts())
    q = {tuple(x["at"]): x for x in qs}
    room_yes, room_no = q[(3.0, 5.0)], q[(10.0, 8.5)]
    ang = q[(9.5, 2.0)]
    bal = next(x for x in qs if x["kind"] == "balcony")
    win = next(x for x in qs if x["kind"] == "opening" and x["element_ids"] == ["w1"])
    answers = {"answers": [
        {"id": room_yes["qid"], "drawing": "yes", "model": "yes"},       # agrees: nothing
        {"id": room_no["qid"], "drawing": "yes", "model": "no"},         # drawn room the reading lacks, image 2 read right
        {"id": room_no["qid"], "drawing": "no", "model": "no"},          # a repeated id: the first answer counts
        {"id": ang["qid"], "drawing": "yes", "model": "no"},             # angled, image 2 misread (fact: straight)
        {"id": bal["qid"], "drawing": "no", "model": "no"},              # door into the air
        {"id": win["qid"], "drawing": "door", "model": "window"}]}       # a drawn door read as a window
    found = CC.compare_findings(answers, qs)
    kinds = {f["kind"]: f for f in found}
    assert set(kinds) == {"room_missing", "angled_wall_straight", "door_into_air", "opening_type_differs"}
    assert kinds["room_missing"]["confidence"] == 0.8 and kinds["room_missing"]["model_read_right"]
    assert kinds["angled_wall_straight"]["confidence"] == 0.4
    assert kinds["opening_type_differs"]["element_ids"] == ["w1"]
    rel = CC.compare_reliability(answers, qs)
    assert rel["asked"] == 5 and rel["right"] == 4


def test_the_architect_image_and_the_marks_are_drawn(tmp_path):
    from PIL import Image

    b = {"levels": [{"id": "L0", "elevation": 0.0}],
         "walls": [{"id": "w1", "level_id": "L0", "start": [0, 0], "end": [20, 0], "thickness": 0.3},
                   {"id": "w2", "level_id": "L0", "start": [0, 0], "end": [0, 10], "thickness": 0.3}],
         "openings": [{"id": "d1", "level_id": "L0", "wall_id": "w1", "type": "door", "center": [5, 0], "width": 0.9},
                      {"id": "x1", "level_id": "L0", "wall_id": "w2", "type": "window", "center": [0, 5],
                       "width": 1.2}],
         "rooms": [{"id": "r1", "level_id": "L0", "label": "SALON", "polygon": _sq(0, 0, 10, 10)}],
         "furniture": [], "site": {}}
    fig, ax = CR._figure(BOX, (800, 400))
    CC.draw_arch(ax, b, "L0", TF)
    p = CR._save(fig, ax, BOX, (800, 400), tmp_path / "arch.jpg")
    im = Image.open(p).convert("L")
    assert im.size == (800, 400)
    # the wall along y = 0 is black at its middle, white in its door gap
    assert im.getpixel((600, 398)) < 100 and im.getpixel((200, 398)) > 150
    qs = [{"n": 1, "point": [0.5, 0.5]}, {"n": 12, "point": [0.1, 0.2]}]
    m = CC.mark_image(p, qs, tmp_path / "marked.jpg")
    mi = Image.open(m).convert("RGB")
    r, g, bb = mi.getpixel((400 + 13, 200))
    assert r > 150 and g < 100 and bb < 100                      # the red ring at mark 1


# ============================================================================================== plausibility
def _building():
    return {"levels": [{"id": "L0", "label": "Zemin", "elevation": 0.0, "order": 0},
                       {"id": "L1", "label": "1. Kat", "elevation": 3.0}],
            "walls": [{"id": "w1", "level_id": "L1", "start": [0, 0], "end": [10, 0], "thickness": 0.2, "exterior": True},
                      {"id": "w2", "level_id": "L1", "start": [5, 0], "end": [5, 6], "thickness": 0.1},
                      {"id": "w3", "level_id": "L1", "start": [0, 6], "end": [10, 6], "thickness": 0.2, "exterior": True},
                      {"id": "w4", "level_id": "L1", "start": [0, 0], "end": [0, 6], "thickness": 0.2, "exterior": True},
                      {"id": "w5", "level_id": "L1", "start": [10, 0], "end": [10, 6], "thickness": 0.2, "exterior": True}],
            "openings": [{"id": "d1", "level_id": "L1", "wall_id": "w2", "type": "door", "center": [5, 3], "width": 0.9},
                         {"id": "win1", "level_id": "L1", "wall_id": "w1", "type": "window", "center": [2, 0],
                          "width": 1.2},
                         {"id": "d2", "level_id": "L1", "wall_id": "w3", "type": "door", "center": [8, 6], "width": 0.9}],
            "rooms": [{"id": "r_salon", "level_id": "L1", "label": "Salon", "room_type": "living",
                       "polygon": _sq(0, 0, 5, 6)},
                      {"id": "r_mutfak", "level_id": "L1", "label": "Mutfak", "room_type": "kitchen",
                       "polygon": _sq(5, 0, 10, 6)},
                      {"id": "r_lift", "level_id": "L1", "label": "Asansör", "room_type": "shaft",
                       "polygon": _sq(10.2, 0, 12, 2)}],
            "furniture": [], "site": {"outdoor_spaces": [{"id": "os1", "level_id": "L1", "label": "Balkon",
                                                          "kind": "balcony", "polygon": _sq(0, -1.5, 4, -0.1)}]}}


def test_the_floor_summary_lists_rooms_joins_windows_and_the_id_tables():
    b = _building()
    bf = CC.building_facts(b)
    assert bf["storeys"] == 2 and bf["ground"] == 0.0
    s = CC.floor_summary(b, "L1", bf)
    t = s["text"]
    assert "Storey L1 '1. Kat'" in t and "+3.00 m" in t
    assert "r_salon Salon (living), 30.0 m2, 1 window(s)" in t
    assert "r_mutfak Mutfak (kitchen), 30.0 m2, 0 window(s)" in t
    assert "d1 (door, 0.90 m): r_mutfak Mutfak (kitchen) <-> r_salon Salon (living)" in t or \
        "d1 (door, 0.90 m): r_salon Salon (living) <-> r_mutfak Mutfak (kitchen)" in t
    assert "d2 (door, 0.90 m)" in t and "nothing in front" in t
    assert "os1 Balkon (balcony)" in t and "Lifts: r_lift Asansör (shaft)" in t
    assert s["windows"] == {"r_salon": 1, "r_mutfak": 0, "r_lift": 0}
    assert s["doors_air"] == ["d2"] and set(s["ids"]["room"]) == {"r_salon", "r_mutfak", "r_lift"}
    assert s["ids"]["door"] == ["d1", "d2"] and s["ids"]["outdoor"] == ["os1"]
    assert s["points"]["d2"] == [8.0, 6.0]


def test_plausibility_answers_keep_only_existing_ids_of_the_asked_class():
    b = _building()
    item = CC.floor_summary(b, "L1", CC.building_facts(b))
    data = {"answers": [{"q": "P4", "ids": ["r_mutfak", "r_nowhere"], "note": ""},
                        {"q": "P8", "ids": ["d2", "r_salon"], "note": "no balcony"},
                        {"q": "P1", "ids": ["r_salon"], "note": ""},
                        {"q": "P7", "ids": ["r_salon", "r_mutfak"], "note": ""},
                        {"q": "P4", "ids": ["r_salon"], "note": "a repeated question: the first answer counts"}]
            + [{"q": q, "ids": [], "note": ""} for q in ("P2", "P3", "P5", "P6", "P9")]}
    found, invalid = CC.plausibility_findings(data, item)
    got = {(f["kind"], tuple(f["element_ids"])) for f in found}
    assert got == {("kitchen_no_window", ("r_mutfak",)), ("door_into_air", ("d2",)),
                   ("habitable_no_window", ("r_salon",)), ("storey_no_stair_access", ("r_salon", "r_mutfak"))}
    assert {(x["q"], x["id"]) for x in invalid} == {("P4", "r_nowhere"), ("P8", "r_salon")}
    byk = {f["kind"]: f for f in found}
    assert byk["kitchen_no_window"]["code_agrees"] is True and byk["door_into_air"]["code_agrees"] is True
    assert byk["habitable_no_window"]["code_agrees"] is False and byk["habitable_no_window"]["confidence"] == 0.4
    assert byk["door_into_air"]["at"] == [8.0, 6.0]


# ================================================================================================== judging
def test_judging_by_known_errors_fixed_places_and_page_copies():
    known = [{"id": "K1", "level": "L2", "at": [5.0, 5.0], "kinds": ["room_missing"]},
             {"id": "K2", "level": "L0", "at": [1.0, 1.0], "kinds": ["door_into_air"], "fixed": True},
             {"id": "K3", "level": None, "at": None, "kinds": ["storey_count_differs"], "building": True}]
    f = {"kind": "room_missing", "level_id": "L1", "copies": ["L2", "L3"], "at": [5.5, 5.0]}
    assert CC.judge_known(f, known, 1.5)["right"] is True
    assert CC.judge_known(dict(f, copies=[]), known, 1.5)["right"] is None
    assert CC.judge_known({"kind": "door_into_air", "level_id": "L0", "at": [1.2, 1.0]}, known, 1.5)["right"] is False
    assert CC.judge_known({"kind": "storey_count_differs", "level_id": "L0", "at": None}, known, 1.5)["right"] is True
    assert CC.judge_known({"kind": "stair_missing", "level_id": "L2", "at": [5.0, 5.0]}, known, 1.5)["right"] is None


def test_review_sheets_number_findings_stably_and_marks_map_to_ids(tmp_path):
    from PIL import Image

    folder = tmp_path / "inputs" / "s" / "p"
    folder.mkdir(parents=True)
    Image.new("RGB", (1600, 800), "white").save(folder / "L0_drawing.jpg")
    Image.new("RGB", (1600, 800), "white").save(folder / "L0_model.jpg")
    index = {"entries": [_entry()]}
    found = [{"id": f"s/p/L0|compare|q{i}", "call": "compare", "kind": "room_missing", "folder": "s/p",
              "entry": "s/p/L0", "image_entry": "s/p/L0", "level_id": "L0", "at": [i * 0.3, 5.0],
              "point": [i * 0.015, 0.5], "confidence": 0.8 if i % 2 else 0.4, "description": f"finding {i}"}
             for i in range(1, 32)]
    found.append({"id": "s/p/L0|inventory|storey_count_differs:0", "call": "inventory", "kind": "storey_count_differs",
                  "folder": "s/p", "entry": "s/p/L0", "image_entry": "s/p/L0", "level_id": "L0", "at": None,
                  "point": None, "confidence": 0.9, "description": "4 storeys written"})
    out = CC.review_sheets(index, found, tmp_path / "inputs", tmp_path / "review")
    files = out["s/p"]
    assert len(files) == 2 and all(Path(p).stat().st_size < 2_000_000 for p in files)
    idx = json.loads((tmp_path / "review" / "s" / "p" / "findings_index.json").read_text(encoding="utf-8"))
    assert len(idx["sheets"][0]["numbers"]) == 30 and len(idx["sheets"][1]["numbers"]) == 2
    assert idx["sheets"][0]["numbers"]["1"] == "s/p/L0|inventory|storey_count_differs:0"   # the most confident first
    again = CC.review_sheets(index, list(reversed(found)), tmp_path / "inputs", tmp_path / "review2")
    idx2 = json.loads((tmp_path / "review2" / "s" / "p" / "findings_index.json").read_text(encoding="utf-8"))
    assert idx2["sheets"] == idx["sheets"] and len(again["s/p"]) == 2
    marks = CC.marks_from_numbers(idx, 1, [1, 2], [3])
    assert marks[idx["sheets"][0]["numbers"]["3"]]["right"] is False and len(marks) == 3
    with pytest.raises(ValueError):
        CC.marks_from_numbers(idx, 2, [3], [])


# ======================================================================================= the ask path (fake vLLM)
def test_the_three_checks_ask_map_calibrate_and_sheet_against_the_fake_server(tmp_path):
    sys.path.insert(0, str(FAKES))
    from fake_vlm import FakeVLM
    from wenart.agent import model as AM

    full = CR.load_index()
    sets = ("before", "after", "synth")
    entries = [e for e in full["entries"] if e.get("set") in sets and e.get("facts") is not None]
    if not entries:
        pytest.skip("no inputs of checks 1, 2, 4 committed")
    pick = [next(e for e in entries if e["set"] == s) for s in sets]
    folders = {e["folder"] for e in pick}
    index = {"entries": pick, "texts": [t for t in full.get("texts") or [] if t["folder"] in folders],
             "readings": {k: v for k, v in (full.get("readings") or {}).items() if k in folders}}
    which = CC.CHECKS
    jobs = CR.check_jobs(index, which, list(sets))
    with FakeVLM() as url:
        model = AM.from_check_yaml(url, "agent", parallel=2)
        res = CR.ask(index, model, CR.INPUTS_DIR, tmp_path / "out", which=which, sets=list(sets),
                     log=lambda *_a: None)
    assert res["stats"]["answered"] == len(jobs) and res["stats"]["failed"] == 0
    saved = json.loads((tmp_path / "out" / "answers.json").read_text(encoding="utf-8"))
    assert {a["which"] for a in saved["answers"]} == set(which)
    calls = {c.get("call_id") or c.get("id"): c for c in saved["calls"]}
    assert any(c.get("images") == 2 for c in saved["calls"]) and any(c.get("images") == 1 for c in saved["calls"])
    assert any(c.get("images") == 0 for c in saved["calls"]) and calls
    assert (tmp_path / "out" / "marked").is_dir()
    found = [f for f in CR.answers_to_findings(index, saved, "agent") if f.get("call") in CC.CHECKS]
    assert all(f["id"].count("|") == 2 for f in found)
    known = {pick[0]["folder"]: [{"id": "K1", "level": pick[0]["level"], "at": None, "kinds": ["storey_count_differs"],
                                  "building": True}]}
    cal = CC.calibrate_checks(index, found, saved, known=known)
    assert set(cal["checks"]) == set(CC.CHECKS) and cal["calls"]["compare"]["answered"] >= 1
    assert "recall of the known errors" in CC.checks_summary(cal)
    sheets = CC.review_sheets(index, found, CR.INPUTS_DIR, tmp_path / "review",
                              judged={j["id"]: j for j in cal["judgements"]})
    for files in sheets.values():
        assert all(Path(p).stat().st_size < 2_000_000 for p in files)


def test_the_pod_job_passes_the_calls_and_the_trust_file_reads_the_checks():
    job = (REPO / "scripts" / "jobs" / "critic.sh").read_text(encoding="utf-8")
    assert 'ASK_ARGS+=(--which "$CRITIC_WHICH")' in job and "--max-minutes 45" in job
    trust = {"threshold": 0.5, "kinds": {}, "checks": {"compare": {"room_missing": {"judged": 10, "right": 8,
                                                                                   "precision": 0.8}}}}
    found = [{"check": "RC15", "kind": "room_missing", "call": "compare", "severity": "major", "message": "m"},
             {"check": "RC15", "kind": "door_into_air", "call": "compare", "severity": "major", "message": "m"}]
    CR.apply_trust(found, trust)
    assert found[0]["severity"] == "major" and found[1]["severity"] == "info"
