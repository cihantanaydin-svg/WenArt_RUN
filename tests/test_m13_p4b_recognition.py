"""Milestone 13 fix round after P4b (17 Oct 2026), track I_ingest: the recognition and reading findings of P4b (real03).

What:
1. ``reading.code_first``: in the run with the answers, the code typing reads the first reading's building (the pieces
   this round's answers typed, and their block copies, are untyped again in its view), so the same pieces are typed
   by code and the same questions withdrawn in both passes; an AI type is never replaced by code.
2. ``pipeline._write_questions``: a late question whose piece is still untyped says so in its review entry.
3. ``reading``: a piece a context rule or a block copy types gets ``type_method: "rule"``, a piece the size inference
   types ``type_method: "inferred"`` (both in the building schema), instead of ``none``.
4. ``reading.tie_break``: two AI passes that disagree on two types that both fit the drawn size and the room are
   decided by code (the type the room misses, else the nearer real product size; never a fixed type the room does not
   miss), marked inferred, built, and the conflict keeps the decision as its resolution.
5. ``symbols.trim_axis_lines``: an unnamed piece drawn with an axis line through and past its outline gets the
   outline's footprint (real03's vanities: 0.85 x 0.80 m -> 0.50 x 0.80 m), so washbasin is in its choices and
   the room's missing washbasin types it by code.
6. ``scheduler``: the late question pass of an orchestrated run starts the GLM session the late questions need and
   runs pipeline_final and fit again before the layout (real02 shape; real03's seed-only case is in
   ``tests/test_run_scheduler.py``).
7. Pass before P5 (17 Oct 2026), ``reading.tie_break``: mirrored twins with disputed answers get the type both
   twins' passes named (real04's f_L1_033 / f_L1_035 sideboard, f_L1_034 / f_L1_036 bookshelf), and the code typing
   runs again after the tie-break (the twin rule types the twin of a decided piece before the review list).
8. Pass before P5, ``scheduler``: a late pass with no other Qwen need still lays out on a server (both chains; the M10
   chain starts no late GLM session); only the questions pipeline_final adds are late (a failed GLM server or a
   recognition exit 2 opens no pass on the first round), and a server that failed in this run is not started again.
Why: P4b real03: six drawn vanities (read as showers) lost their type between the two ingest passes, their questions
were never asked and the agent marked them as not furniture (6 of 8 bathrooms without a washbasin); 24 typed drawn
pieces kept ``type_method: none``; the bedroom oda_01's 1.5 x 0.6 m piece (dresser / wardrobe) stayed an unbuilt box.
How: the hand-made rooms of ``tests/_m11_room.py`` in a real ``pipeline.ProjectBuild``, synthetic strokes in metres
(``tests/_real01_page.py``), the fake runner, clock and servers of ``tests/test_run_scheduler.py`` and the orchestrated
fixture of ``tests/test_run_agent.py``. Every test fails on the code before this fix round.
"""
from __future__ import annotations

import copy
import json
from types import SimpleNamespace

import pytest

import _m11_room as M
import _real01_page as R
import test_run_agent as TRA
import test_run_scheduler as TRS
from wenart import building as BLD
from wenart.furniture import infer as INF
from wenart.ingest import pipeline as PL
from wenart.ingest.generic import reading as RD
from wenart.ingest.generic import symbols as SY
from wenart.ingest.generic import topology as TP
from wenart.run import scheduler as SC

SHA = "0" * 64


def _piece(b: dict, pid: str) -> dict:
    return next(f for f in b["furniture"] if f["id"] == pid)


def _page(build, keys: dict, report: dict) -> dict:
    """One asked page whose extraction holds the core items (``element_id`` -> ``candidate_key``) and ``report``."""
    items = [SimpleNamespace(element_id=pid, details={"candidate_key": key}) for pid, key in keys.items()]
    page = SimpleNamespace(extraction=SimpleNamespace(furniture=items, report=report, level_id="L0"))
    build.furniture_works = [page]
    build.building["project"].setdefault("id", "real03")
    return {"page": page}


def _questions(keys) -> list:
    return [{"key": k, "task": "symbol_type", "images": [f"crops/{k}_ctx.png"], "input_sha256": SHA} for k in keys]


# --------------------------------------------------------------------------
# 1. The code typing reads the first reading's building in both passes
# --------------------------------------------------------------------------

def _bathroom(answered: bool):
    """real03's banyo: a toilet named by its block, a drawn 0.85 x 0.80 m piece (listed first) and a 1.62 x 0.80 m
    piece, both asked. ``answered``: the run with the answers, where both models typed the tub ``bathtub`` and the
    0.85 m piece's question was withdrawn in the first run (so it is not in the round)."""
    wc = M.fp("wc", "toilet", (2.6, 0.4), (0.38, 0.7), front=90.0, type_method="block_name")
    sq = M.fp("s", "unknown", (0.5, 0.5), (0.85, 0.80), front=None, status="unverified", type_method="none")
    if answered:
        tub = M.fp("t", "bathtub", (0.9, 1.9), (1.62, 0.80), front=90.0, status="verified", type_method="ai_two_pass")
    else:
        tub = M.fp("t", "unknown", (0.9, 1.9), (1.62, 0.80), front=None, status="unverified", type_method="none")
    build = PL.ProjectBuild(M.building(w=3.0, h=2.4, room_type="bathroom", window=None, furniture=[sq, tub, wc]))
    keys = {"s": "sym_L0_001", "t": "sym_L0_002"}
    report = {"questions": _questions(keys.values()), "pending": list(keys.values())}
    if answered:
        report.update(pending=[keys["s"]], answers_applied=1)
    return build, _page(build, keys, report), keys


def test_the_code_typing_withdraws_the_same_questions_in_the_run_with_the_answers(tmp_path):
    """P4b real03: in the first reading the bath set missed shower|bathtub, so the 0.85 m symbol was typed shower by
    code and its question withdrawn; in the run with the answers the AI's bathtub filled the slot and the symbol was
    left untyped, with a question that was never asked (needs_review, then marked not furniture by the agent). Now
    both passes type it and withdraw the same question; the tub keeps the AI's bathtub; nothing is unanswered."""
    first, works1, keys = _bathroom(answered=False)
    RD.read_furniture(first, works1)
    s1 = _piece(first.building, "s")
    assert (s1["type"], s1["type_method"]) == ("shower", "group_member")
    assert first.code_typed_methods == {keys["s"]: "group_member"}
    assert works1["page"].extraction.report["pending"] == [keys["t"]]
    PL._write_questions(first, tmp_path / "first", None, None)
    asked = {(keys["t"], SHA)}                                  # what the first run wrote to requests.json

    second, works2, _ = _bathroom(answered=True)
    RD.read_furniture(second, works2)
    s2, t2 = _piece(second.building, "s"), _piece(second.building, "t")
    assert (s2["type"], s2["type_method"]) == ("shower", "group_member") and s2.get("build") is not False
    assert (t2["type"], t2["type_method"]) == ("bathtub", "ai_two_pass")            # the AI's type is kept
    assert second.code_typed_methods == first.code_typed_methods
    assert second.reading["answer_typed"] == ["t"] and second.building["needs_review"] == []
    answers = {keys["t"]: {"qwen": {"type": "bathtub"}, "glm": {"type": "bathtub"}}}
    PL._write_questions(second, tmp_path / "second", asked, answers)
    assert second.pending == [] and second.unanswered == []
    assert [q["key"] for q in second.questions] == [keys["t"]]
    assert not any("not in the round" in w for w in second.building["warnings"])


def test_real01_answers_with_real_types_withdraw_the_same_questions(tmp_path):
    """The real01 two-pass run (tests/test_pipeline.py) with answers that give real types instead of 'unknown': both
    models call the chaise sym_L0_015 a sofa. The old code typing then saw the living room's seating anchor filled by
    the AI's sofa and left the drawn sofa sym_L0_014 (typed by code in the first run, question withdrawn) untyped:
    its question came back as a late, never-asked one. Now the same 15 questions are withdrawn in both runs.

    26 Oct 2026 (user: "identical blocks get one type"; infer._same_block_type): the second sofa sym_L0_015 is the
    same block as the first (371 paths, 1.90 x 0.70 m; the real01 reference C06: "the same block as F15", both sofas),
    so code types it in both runs and its question is withdrawn too: 16 withdrawn, sym_L0_017 alone is asked."""
    import shutil

    from wenart.recognition import answers as A

    project = tmp_path / "real01"
    project.mkdir()
    shutil.copyfile(R.ROOT / "projects" / "real01" / "real01.pdf", project / "real01.pdf")
    out = tmp_path / "out"
    rec = out / "recognition"
    _b1, first = PL.run_project(project, out)
    items = A.read_requests(rec)["items"]
    assert [i["key"] for i in items] == ["sym_L0_017"] and len(first.code_typed) == 16
    assert first.code_typed_methods["sym_L0_015"] == "same_block"
    models = A.load_models()
    for key in A.MODEL_KEYS:
        store = A.AnswerStore.for_model(rec, key, models)
        for it, ftype in zip(items, ("side_table",)):
            data = {"type": ftype, "front": "none", "confidence": 0.9, "reason": "fake answer"}
            store.put(it["key"], {"task": it["task"], "input_sha256": it["input_sha256"], "data": data,
                                  "raw_text": json.dumps(data), "error": None, "attempts": 1, "latency_s": 0.0,
                                  "model": store.data["model"], "seed": 0, "images": it["images"]}, save=False)
        store.save()
    building, second = PL.run_project(project, out, answers=rec)
    assert second.code_typed == first.code_typed and second.code_typed_methods == first.code_typed_methods
    assert [q["key"] for q in second.questions] == ["sym_L0_017"]
    assert second.unanswered == [] and second.pending == [] and PL.exit_code(building, second) == PL.EXIT_OK
    assert sorted(f["type"] for f in building["furniture"] if f.get("type_method") == "ai_two_pass") == \
        ["side_table"]
    assert sorted(f["type"] for f in building["furniture"] if f.get("type_method") == "same_block") == \
        ["nightstand", "nightstand", "sofa"]


def test_without_answers_nothing_is_reset():
    first, works, _ = _bathroom(answered=False)
    assert RD.answer_typed(first, works, RD._items(first, works)) == set()
    view = RD._first_reading_view(first.building, {"t"})
    assert _piece(view, "t")["inferred_as"] == RD.ANSWERED_AS and "inferred_as" not in _piece(first.building, "t")
    # A copy typed from an answered piece is reset with it.
    second, works2, _ = _bathroom(answered=True)
    got = RD.answer_typed(second, works2, RD._items(second, works2), {"t2": ["t"], "x": ["wc"]})
    assert got == {"t", "t2"}


# --------------------------------------------------------------------------
# 2. A late question's piece says so in its review entry
# --------------------------------------------------------------------------

def test_a_late_question_left_untyped_says_so_in_its_review_entry(tmp_path):
    box = M.fp("u", "unknown", (3.5, 1.0), (1.3, 1.3), front=None, status="unverified", type_method="none")
    build = PL.ProjectBuild(M.building(furniture=[box]))
    key = "sym_L0_007"
    works = _page(build, {"u": key}, {"questions": _questions([key]), "pending": [key], "answers_applied": 1})
    RD.read_furniture(build, works)
    (entry,) = build.building["needs_review"]
    assert entry["id"] == "u" and "late" not in entry["reason"]
    PL._write_questions(build, tmp_path, {("sym_L0_001", SHA)}, {})
    assert build.pending == [] and build.unanswered == [key]
    note = PL.LATE_REVIEW_NOTE.format(key=key)
    assert entry["reason"].endswith(note) and any(note in w for w in build.building["warnings"])


# --------------------------------------------------------------------------
# 3. The type method of the context rules and the size inference
# --------------------------------------------------------------------------

def test_context_and_size_typed_pieces_carry_a_schema_valid_type_method():
    """P4b: 24 typed drawn pieces (6 corner sofas) kept type_method none, so the final manifest counted them as
    untyped and the rules keyed on the method (the mark-not-furniture lock) did not see them."""
    bed = M.fp("bed", "bed_double", (2.5, 3.0), (1.6, 2.0), front=270.0, type_method="block_name")
    n1 = M.fp("n1", "unknown", (1.45, 3.75), (0.45, 0.40), front=None, status="unverified", type_method="none")
    build = PL.ProjectBuild(M.building(furniture=[bed, n1]))
    assert RD.context_types(build, {}) == {"nightstand": 1}
    f = _piece(build.building, "n1")
    assert (f["type"], f["type_method"], f["status"]) == ("nightstand", RD.CONTEXT_METHOD, "unverified")
    assert RD.CONTEXT_RULE in [e.get("rule") for e in f["evidence"]]
    # The size inference (no code method): a 1.0 x 0.4 m box in a bedroom that has its bed and its wardrobe.
    wardrobe = M.fp("w0", "wardrobe", (0.9, 3.68), (1.2, 0.6), front=270.0, type_method="block_name")
    bed2 = M.fp("b2", "bed_double", (2.5, 1.5), (1.6, 2.0), front=90.0, type_method="block_name")
    box = M.fp("u1", "unknown", (3.5, 3.68), (1.0, 0.4), front=None, status="unverified", type_method="none")
    build2 = PL.ProjectBuild(M.building(furniture=[wardrobe, bed2, box]))
    assert RD.infer(build2, set()) == (1, [])
    u1 = _piece(build2.building, "u1")
    assert (u1["type"], u1["type_method"], u1["inferred"]) == ("ottoman", RD.INFER_METHOD, True)
    for b in (build.building, build2.building):
        assert not [e for e in BLD.validation_errors(b) if "type_method" in e]


# --------------------------------------------------------------------------
# 4. Two AI passes that disagree
# --------------------------------------------------------------------------

def _answers(*pairs) -> list:
    return [{"type": t, "model_key": k, "pass": n, "confidence": c, "front": "none", "reason": "fake"}
            for n, (k, t, c) in enumerate(pairs, start=1)]


def _disputed(furniture, room_type, pid, pair, area=(4.0, 3.0)):
    build = PL.ProjectBuild(M.building(w=area[0], h=area[1], room_type=room_type, window=None, furniture=furniture))
    build.conflict("symbol_type_disagreement", [pid], f"{pid}: sym_L0_019: the passes disagree: {pair}",
                   "unresolved: the drawn footprint is kept as unknown, unverified")
    return build


def test_a_disagreement_is_decided_by_the_type_the_room_misses():
    """real03 oda_01: f_L0_103, 1.5 x 0.6 m, Qwen dresser (0.95), GLM wardrobe (0.90); the bedroom has no storage."""
    bed = M.fp("bed", "bed_double", (2.0, 1.1), (1.6, 2.0), front=90.0, type_method="block_name")
    piece = M.fp("p", "unknown", (3.1, 2.6), (1.5, 0.6), front=None, status="unverified", type_method="none",
                 type_candidates=_answers(("qwen", "dresser", 0.95), ("glm", "wardrobe", 0.9)))
    build = _disputed([bed, piece], "bedroom", "p", "dresser / wardrobe")
    works = _page(build, {"p": "sym_L0_019"}, {"questions": _questions(["sym_L0_019"]), "pending": [],
                                               "answers_applied": 1})
    RD.read_furniture(build, works)
    p = _piece(build.building, "p")
    assert (p["type"], p["type_method"], p["inferred"], p["status"]) == ("wardrobe", "inferred", True, "unverified")
    assert p.get("build") is not False and build.building["needs_review"] == []
    assert "the room misses it" in p["inferred_reason"] and "recognition/crops/sym_L0_019_ctx.png" in \
        p["inferred_reason"] and RD.TIE_RULE in [e.get("rule") for e in p["evidence"]]
    (c,) = build.raw_conflicts
    assert c["resolution"].startswith("typed wardrobe by code (not dresser)")
    assert build.reading["tie_break"] == ["p"]


def test_a_disagreement_never_guesses_fixed_equipment_the_room_does_not_miss():
    """real02 (P4a) f_L-1b_045: a two-seat sofa drawing in the salon of an open kitchen that has its island; Qwen said
    kitchen_island, GLM sofa. The island is fixed equipment the room does not miss: sofa. Two fixed types the room
    does not miss stay for review; a pair where only one type fits the size is not decided either."""
    sofa = M.fp("s0", "sofa_corner", (1.2, 2.2), (2.2, 1.6), front=270.0, type_method="block_name")
    island = M.fp("k0", "kitchen_island", (4.5, 2.5), (1.8, 0.9), front=None, type_method="block_name")
    piece = M.fp("p", "unknown", (3.0, 0.6), (1.64, 0.82), front=None, status="unverified", type_method="none",
                 type_candidates=_answers(("qwen", "kitchen_island", 0.8), ("glm", "sofa", 0.8)))
    build = _disputed([sofa, island, piece], "living", "p", "kitchen_island / sofa", area=(6.0, 4.0))
    build.conflict("label_conflict", [M.ROOM_ID], "one face holds the room names 'Açık Mutfak' and 'SALON'",
                   "both room types apply")             # real02's open kitchen: the island is allowed there
    assert RD.tie_break(build, {}) == ["p"]
    p = _piece(build.building, "p")
    assert p["type"] == "sofa" and "fixed equipment the room does not miss" in p["inferred_reason"]
    # two fixed types, neither missing (a shower and a bathtub drawn, the set complete): no decision
    wc = M.fp("wc", "toilet", (2.6, 0.4), (0.38, 0.7), front=90.0, type_method="block_name")
    tub = M.fp("t", "bathtub", (0.9, 1.9), (1.62, 0.80), front=90.0, type_method="block_name")
    basin = M.fp("b", "washbasin", (2.6, 2.0), (0.6, 0.45), front=270.0, type_method="block_name")
    odd = M.fp("q", "unknown", (1.9, 0.5), (0.85, 0.85), front=None, status="unverified", type_method="none",
               type_candidates=_answers(("qwen", "shower", 0.8), ("glm", "washing_machine", 0.8)))
    build2 = _disputed([wc, tub, basin, odd], "bathroom", "q", "shower / washing_machine", area=(3.0, 2.4))
    assert RD.tie_break(build2, {}) == [] and _piece(build2.building, "q")["type"] == "unknown"
    # one of the two types does not fit the drawn size (a 1.5 x 0.6 m piece is no nightstand): no decision
    lone = M.fp("p", "unknown", (3.1, 2.6), (1.5, 0.6), front=None, status="unverified", type_method="none",
                type_candidates=_answers(("qwen", "nightstand", 0.9), ("glm", "wardrobe", 0.9)))
    build3 = _disputed([lone], "bedroom", "p", "nightstand / wardrobe")
    assert RD.tie_break(build3, {}) == []


def _twin_flats(furniture: list, room_type: str = "other", label: str = "OYUN AKTİVİTE VE DİNLENME ODASI") -> dict:
    """Two 4 x 4 m rooms side by side, the second the mirror of the first about x = 4.5 (real04's two play and rest
    rooms, ``r_L1_oyun_aktivite_ve_dinlenme_odasi`` and its ``_2``: type other, kind living by the label, so the size
    inference allows a bench and the tie-break does not)."""
    b = M.building(w=4.0, h=4.0, room_type=room_type, window=None, furniture=furniture)
    b["rooms"][0].update(label=label, label_raw=label)
    second = copy.deepcopy(b["rooms"][0])
    second.update(id="r_L0_oda_2", polygon=[[5.0, 0.0], [9.0, 0.0], [9.0, 4.0], [5.0, 4.0]],
                  twin_of=b["rooms"][0]["id"], twin_transform=[-1.0, 0.0, 9.0, 0.0, 1.0, 0.0])
    b["rooms"].append(second)
    return b


def _disputed_at(pid, center, size, room, *pair, rotation=0.0):
    f = M.fp(pid, "unknown", center, size, rotation=rotation, front=None, status="unverified", type_method="none",
             type_candidates=_answers(*pair))
    f["room_id"] = room
    return f


def test_mirrored_twins_with_disputed_answers_get_one_type_and_the_twin_rule_runs_after_the_tie_break():
    """Pass before P5, real04 (P3's building): the tie-break typed f_L1_035 (2.17 x 0.40 m, sideboard / tv_unit)
    sideboard and left its mirror twin f_L1_033 (sideboard / bench; no bench in that room) an unbuilt unknown; it
    typed f_L1_034 (1.09 x 0.40 m, bookshelf / tv_unit) bookshelf and its twin f_L1_036 (bookshelf / console_table)
    console_table. Now the twins get the type both twins' passes named, built and inferred. A disputed piece whose twin
    is already typed gets the twin's type (the code pass after the tie-break), and so does a piece whose question was
    not answered in this round (a late one: its question is withdrawn, as the pipeline's inference withdrew it after
    the reading before). Fails on HEAD adc3004 (f_L1_033 untyped, f_L1_036 console_table, no code pass)."""
    a2, rest = "r_L0_oda_2", M.ROOM_ID
    side_b = _disputed_at("f033", (7.0, 3.78), (2.17, 0.40), a2, ("qwen", "sideboard", 0.95), ("glm", "bench", 0.8))
    side_a = _disputed_at("f035", (2.0, 3.78), (2.17, 0.40), rest, ("qwen", "sideboard", 0.95),
                          ("glm", "tv_unit", 0.9))
    shelf_b = _disputed_at("f036", (8.78, 2.0), (1.09, 0.40), a2, ("qwen", "bookshelf", 0.95),
                           ("glm", "console_table", 0.9), rotation=90.0)
    shelf_a = _disputed_at("f034", (0.22, 2.0), (1.09, 0.40), rest, ("qwen", "bookshelf", 0.95),
                           ("glm", "tv_unit", 0.9), rotation=90.0)
    # A pair whose first twin the AI typed (both passes console_table) and whose second the passes dispute.
    typed = M.fp("f040", "console_table", (2.6, 0.22), (1.09, 0.40), front=90.0, status="verified",
                 type_method="ai_two_pass")
    disputed = _disputed_at("f041", (6.4, 0.22), (1.09, 0.40), a2, ("qwen", "bookshelf", 0.95),
                            ("glm", "tv_unit", 0.9))
    # A piece whose question has no answers in this round (late), at the mirrored spot of a piece the tie-break types.
    waits = M.fp("f050", "unknown", (5.22, 1.6), (1.09, 0.40), rotation=90.0, front=None, status="unverified",
                 type_method="none")
    waits["room_id"] = a2
    shelf_c = _disputed_at("f051", (3.78, 1.6), (1.09, 0.40), rest, ("qwen", "bookshelf", 0.95),
                           ("glm", "console_table", 0.9), rotation=90.0)
    pieces = [side_b, side_a, shelf_b, shelf_a, typed, disputed, waits, shelf_c]       # real04's order: f033 first
    build = PL.ProjectBuild(_twin_flats(pieces))
    for f in pieces:
        if f.get("type_candidates"):
            build.conflict("symbol_type_disagreement", [f["id"]], f"{f['id']}: the passes disagree",
                           "unresolved: the drawn footprint is kept as unknown, unverified")
    keys = {f["id"]: f"sym_L0_{n:03d}" for n, f in enumerate(pieces, start=1)}
    works = _page(build, keys, {"questions": _questions(keys.values()), "pending": [keys["f050"]],
                                "answers_applied": 1})
    RD.read_furniture(build, works)
    got = {f["id"]: (f["type"], f.get("type_method"), f.get("build") is not False) for f in build.building["furniture"]}
    assert got["f033"] == got["f035"] == ("sideboard", RD.INFER_METHOD, True)
    assert got["f034"] == got["f036"] == ("bookshelf", RD.INFER_METHOD, True)
    for pid, twin in (("f033", "f035"), ("f035", "f033"), ("f036", "f034"), ("f034", "f036")):
        f = _piece(build.building, pid)
        assert f["inferred"] is True and f"its twin {twin}" in f["inferred_reason"] and \
            "the twins get one type" in f["inferred_reason"]
    (c,) = [c for c in build.raw_conflicts if c["element_ids"] == ["f033"]]
    assert c["resolution"].startswith("typed sideboard by code (not bench)")
    # The typed twin decides (the twin rule, after the tie-break), and the twin of a decided piece gets its type.
    assert got["f041"] == ("console_table", "twin", True)
    assert got["f051"] == ("console_table", RD.INFER_METHOD, True) and got["f050"] == ("console_table", "twin", True)
    assert {k: build.reading["typed_by"][k] for k in ("f041", "f050")} == {"f041": "twin", "f050": "twin"}
    assert sorted(build.reading["tie_break"]) == ["f033", "f034", "f035", "f036", "f051"]
    # Only the late question is withdrawn; the answered one of f041 stays listed.
    assert build.reading["questions_withdrawn"] == [keys["f050"]] and build.code_typed == {keys["f050"]: "f050"}
    report = works["page"].extraction.report
    assert report["pending"] == [] and report[RD.CODE_TYPED_KEY] == [keys["f050"]]
    assert build.building["needs_review"] == []
    assert all(_piece(build.building, pid).get("front_deg") is not None for pid in ("f041", "f050"))
    # tie_break alone: a disputed piece whose twin is typed is left to the twin rule (``deferred``), never decided.
    pair = [M.fp("f040", "console_table", (2.6, 0.22), (1.09, 0.40), front=90.0, status="verified",
                 type_method="ai_two_pass"),
            _disputed_at("f041", (6.4, 0.22), (1.09, 0.40), a2, ("qwen", "bookshelf", 0.95), ("glm", "tv_unit", 0.9))]
    later: set = set()
    assert RD.tie_break(PL.ProjectBuild(_twin_flats(pair)), {}, (), later) == [] and later == {"f041"}
    # Twins whose passes both name one type that fits besides one that does not stay for review (as a single piece):
    # real04's f_L0_021 / f_L0_024 (desk / sofa in two bedrooms).
    lone = [_disputed_at("d1", (2.0, 2.0), (1.45, 0.91), rest, ("qwen", "desk", 0.9), ("glm", "sofa", 0.8)),
            _disputed_at("d2", (7.0, 2.0), (1.45, 0.91), a2, ("qwen", "desk", 0.9), ("glm", "sofa", 0.8))]
    build2 = PL.ProjectBuild(_twin_flats(lone, room_type="bedroom", label="YATAK ODASI"))
    assert RD.tie_break(build2, {}) == [] and {f["type"] for f in build2.building["furniture"]} == {"unknown"}


# --------------------------------------------------------------------------
# 5. An axis line through an unnamed piece
# --------------------------------------------------------------------------

def _rect(x0, y0, x1, y1):
    return R.stroke([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], closed=True)


def _vanity(axis):
    """real03's vanity (sym_L0_055-058): a 0.50 x 0.80 m counter outline, the basin outline, the drain and ``axis``."""
    return [_rect(2.0, 2.0, 2.5, 2.8), _rect(2.08, 2.12, 2.42, 2.68), R.arc((2.25, 2.4), 0.03, 0.0, 360.0), axis]


def _candidates(strokes) -> list:
    walls = [R.wall((0, 0), (9, 0), 0.2), R.wall((9, 0), (9, 6), 0.2), R.wall((9, 6), (0, 6), 0.2),
             R.wall((0, 6), (0, 0), 0.2)]
    _pieces, cands, _decor = SY.furniture(list(strokes), set(), walls, [], [], [], TP.building_outline(walls, []), [],
                                          level_id="L0", file_rel="t.dxf", page_no=1,
                                          size_table=SY.FALLBACK_SIZE_TABLE)
    return cands


def test_an_axis_line_through_an_unnamed_vanity_is_left_out_of_its_footprint():
    """P4b real03: the line through the drain made the vanities 0.85 x 0.80 m, out of the washbasin range, so the
    question offered no washbasin and both models said shower."""
    (cand,) = _candidates(_vanity(R.stroke([(1.825, 2.4), (2.675, 2.4)])))
    assert sorted(cand["footprint"]["size"]) == pytest.approx([0.5, 0.8])
    assert "washbasin" in cand["fits"] and "shower" not in cand["fits"]
    det = cand["item"].details
    assert det["untrimmed_size"] == pytest.approx([0.85, 0.8]) and len(det["axis_lines"]) == 1
    assert "drawn through and past the outline" in cand["item"].evidence["note"]
    # The 1.00 x 0.50 m vanities (sym_L0_005/006): a vertical line through the drain, 0.175 m out at both ends.
    wide = [_rect(2.0, 2.0, 3.0, 2.5), _rect(2.25, 2.08, 2.75, 2.42), R.arc((2.5, 2.25), 0.03, 0.0, 360.0),
            R.stroke([(2.5, 1.825), (2.5, 2.675)])]
    (cand2,) = _candidates(wide)
    assert sorted(cand2["footprint"]["size"]) == pytest.approx([0.5, 1.0])


@pytest.mark.parametrize("axis", [
    R.stroke([(2.25, 2.4), (2.675, 2.4)]),            # sticks out on one side only
    R.stroke([(1.825, 2.02), (2.675, 2.02)]),         # past both ends but along the outline's edge, off the centre
], ids=["one-side", "off-centre"])
def test_lines_that_are_no_axis_line_stay_in_the_footprint(axis):
    (cand,) = _candidates(_vanity(axis))
    assert "untrimmed_size" not in cand["item"].details
    assert max(cand["footprint"]["size"]) > 0.8 or min(cand["footprint"]["size"]) > 0.5


@pytest.mark.parametrize("size,want", [((0.50, 0.80), "washbasin"), ((1.00, 0.50), "washbasin"),
                                       ((0.8457, 0.80), None)])
def test_the_trimmed_vanity_is_the_bathrooms_missing_washbasin(size, want):
    """With the true outline the bathroom's missing washbasin types the piece by code (no question, no AI); with the
    axis line it fits no missing member (in P4b's first reading, before the AI's bath pieces, it was the missing
    shower)."""
    wc = M.fp("wc", "toilet", (2.6, 0.4), (0.38, 0.7), front=90.0, type_method="block_name")
    tub = M.fp("t", "bathtub", (0.9, 1.9), (1.62, 0.80), front=90.0, type_method="block_name")
    van = M.fp("v", "unknown", (2.5, 1.9), size, front=None, status="unverified", type_method="none")
    b = M.building(w=3.0, h=2.4, room_type="bathroom", window=None, furniture=[wc, tub, van])
    props = INF.code_types(b)
    assert [(p["piece_id"], p["type"], p["type_method"]) for p in props] == ([("v", want, "group_member")] if want
                                                                             else [])


# --------------------------------------------------------------------------
# 6. The late question pass of an orchestrated run (real02 shape)
# --------------------------------------------------------------------------

@pytest.fixture
def agent_models(monkeypatch):
    monkeypatch.setattr(TRS, "MODELS", dict(TRS.MODELS, agent=TRA.AGENT))
    monkeypatch.delenv("WENART_AGENT_SLEEP", raising=False)
    return TRS.MODELS


def test_the_orchestrated_late_pass_asks_qwen_in_its_session_then_starts_glm(tmp_path, agent_models):
    """P4a real02: 48 questions asked, 54 at the end (6 late, never asked). The open Qwen session of phase 3 answers
    them, then one GLM session, then pipeline_final and fit run again with the answers, before the agent's layout
    session. Fails on the old scheduler (one pipeline_final, no late session)."""
    r = TRA.orchestrated(tmp_path, [TRA.FINISH], [[]], buildings={"p1": {"questions": 2}})
    r.cli.flags = {"late_questions": {"p1": 2}}
    assert r.run(**r.kwargs) == 0
    assert r.servers.starts == ["glm", "qwen", "glm", "agent"]
    asks = [(TRS.opt(c["cmd"], "--model-key"), bool(TRS.opt(c["cmd"], "--server")))
            for c in r.cli.find("recognize", "p1")]
    assert asks == [("glm", True), ("qwen", True), ("qwen", True), ("glm", True)]
    finals = r.cli.find("pipeline_final", "p1")
    assert len(finals) == 2 and all("--no-ai" not in c["cmd"] for c in finals)
    names = r.cli.names("p1")
    assert names.index("layout") > max(i for i, n in enumerate(names) if n in ("pipeline_final", "fit"))
    out = tmp_path / "outputs" / "p1"
    assert json.loads((out / "building.json").read_text())["late_unanswered"] == []
    rec = r.record("p1", "pipeline_final")
    assert rec["status"] == "ok" and SC.LATE_NOTE.format(n=2) in rec["note"]
    steps = [s["name"] for s in r.record("p1", "recognize")["steps"]]
    assert steps == ["ask glm", "ask qwen", "ask qwen (late)", "ask glm (late)"]
    assert r.record("p1", "recognize")["status"] == "ok" and r.manifest()["projects"][0]["state"] == "ok"


def test_no_time_for_the_late_glm_session_is_a_warning_never_incomplete(tmp_path, agent_models):
    r = TRA.orchestrated(tmp_path, [TRA.FINISH], [[]], buildings={"p1": {"questions": 2}})
    r.cli.flags = {"late_questions": {"p1": 1}}
    orch_start = SC.Orchestrator.start_session

    def no_late_glm(self, key, need, on_fail):
        if key == "glm" and any(pr.late == "open" for pr in need):
            for pr in need:
                on_fail(pr, "incomplete", "deadline: glm server not started")
            return None
        return orch_start(self, key, need, on_fail)

    SC.Orchestrator.start_session = no_late_glm
    try:
        assert r.run(**r.kwargs) == 0
    finally:
        SC.Orchestrator.start_session = orch_start
    assert r.servers.starts == ["glm", "qwen", "agent"]
    assert len(r.cli.find("pipeline_final", "p1")) == 1
    rec = r.record("p1", "recognize")
    assert rec["status"] == "warning" and "1 late recognition question(s) left unanswered" in rec["note"]
    assert r.manifest()["projects"][0]["state"] == "ok" and "layout" in r.cli.names("p1")


# --------------------------------------------------------------------------
# 7. Pass before P5 (17 Oct 2026): the late pass with no other Qwen need, after a failed server
# --------------------------------------------------------------------------

def _late_for_qwen_only(tmp_path) -> None:
    """A repo whose committed seeds answer the first round for both models and the late key for Qwen only; the brief
    asks for rule decor (no decor question): phase 3 has no other Qwen need."""
    TRS.make_repo(tmp_path, {"p1": {"brief": {"decor": "rules"}}})
    seeds = TRS._seed_answers(tmp_path / "repo", "p1", TRS._first_items("p1", 2))
    qwen = seeds / f"answers_{TRS.MODELS['qwen']['slug']}.json"
    data = json.loads(qwen.read_text())
    late = TRS.late_item("p1", 1)
    data["calls"][late["key"]] = {"task": late["task"], "input_sha256": late["input_sha256"],
                                  "model": TRS.MODELS["qwen"]["id"], "data": TRS.RECOGNITION_ANSWERS[late["task"]],
                                  "error": None}
    qwen.write_text(json.dumps(data))


@pytest.mark.parametrize("chain", ["m10", "orchestrated"])
def test_a_late_pass_with_no_other_qwen_need_still_lays_out_on_a_server(tmp_path, agent_models, chain):
    """Review of the fix round after P4b: phase 3 put off the layout of a project whose late pass was open and, with no
    other Qwen need, took its no-server branch: the late GLM session ran there, pipeline_final and fit ran again, and
    the layout failed without a server ('server agent not available' / 'server qwen not available'; project failed,
    exit 1; both chains). Now the orchestrated run asks GLM in its late session and lays out on the agent session; the
    M10 chain ends the pass before its Qwen session (no late GLM session) and lays out there. Fails on HEAD adc3004."""
    _late_for_qwen_only(tmp_path)
    buildings = {"p1": {"questions": 2, "brief": {"decor": "rules"}}}
    if chain == "orchestrated":
        r = TRA.orchestrated(tmp_path, [TRA.FINISH], [[]], buildings=buildings)
        r.cli.flags = {"late_questions": {"p1": 1}}
        assert r.run(**r.kwargs) == 0
        assert r.servers.starts == ["glm", "agent"]
        assert len(r.cli.find("pipeline_final", "p1")) == 2
        assert r.record("p1", "pipeline_final")["note"].endswith(SC.LATE_NOTE.format(n=1))
        assert [s["name"] for s in r.record("p1", "recognize")["steps"]][-2:] == ["stored answers qwen (late)",
                                                                                 "ask glm (late)"]
    else:
        r = TRS.Run(tmp_path, buildings=buildings, projects=["p1"], flags={"late_questions": {"p1": 1}})
        assert r.run() == 0
        assert r.servers.starts == ["qwen", "qwen", "glm"]          # the layout session, then the two checks
        assert len(r.cli.find("pipeline_final", "p1")) == 1
        rec = r.record("p1", "recognize")
        assert rec["status"] == "warning" and f"({SC.M10_LATE_NOTE})" in rec["note"]
        layout = r.cli.find("layout", "p1")
        assert len(layout) == 1 and TRS.opt(layout[0]["cmd"], "--server") == "http://fake-qwen/v1"
    assert r.record("p1", "layout")["status"] == "ok" and r.manifest()["projects"][0]["state"] == "ok"


def test_a_failed_glm_server_opens_no_late_pass_on_the_first_round_questions(tmp_path, agent_models):
    """Review of the fix round after P4b: after a phase-2 GLM failure pipeline_final ran --no-ai and the late pass
    opened on every first-round question ('2 late recognition question(s)') and started the failed GLM server again
    (on a pod: up to 25 min more before the same failure). Now only the questions pipeline_final adds are late, and a
    server that failed in this run is not started again: no second GLM start, with or without late questions. Fails on
    HEAD adc3004 (server starts glm, qwen, glm, agent)."""
    r = TRA.orchestrated(tmp_path, [TRA.FINISH], [[]], buildings={"p1": {"questions": 2}}, fail={"glm": "early_exit"})
    assert r.run(**r.kwargs) == 0
    assert r.servers.starts == ["glm", "qwen", "agent"]
    assert not [line for line in r.lines if "late recognition question" in line]
    assert [s["name"] for s in r.record("p1", "recognize")["steps"]] == ["ask qwen"]
    assert len(r.cli.find("pipeline_final", "p1")) == 1 and r.record("p1", "layout")["status"] == "ok"
    # With a real late question: the pass opens on it alone and ends without a GLM start (and no Qwen ask for it).
    tmp2 = tmp_path / "late"
    tmp2.mkdir()
    r2 = TRA.orchestrated(tmp2, [TRA.FINISH], [[]], buildings={"p1": {"questions": 2}}, fail={"glm": "early_exit"})
    r2.cli.flags = {"late_questions": {"p1": 1}}
    assert r2.run(**r2.kwargs) == 0
    assert r2.servers.starts == ["glm", "qwen", "agent"]
    assert "p1: 1 late recognition question(s): a second short recognition pass" in r2.lines
    rec = r2.record("p1", "recognize")
    assert rec["status"] == "warning" and SC.LATE_FAILED_NOTE.format(key="glm", reason="early_exit") in rec["note"]
    assert [s["name"] for s in rec["steps"]] == ["ask qwen"]
    assert r2.manifest()["projects"][0]["state"] == "ok"
    # Qwen's first round in the committed seeds: nothing else needs a Qwen session, and the late pass that GLM can no
    # longer complete starts none either.
    tmp3 = tmp_path / "qwen-seeded"
    TRS.make_repo(tmp3, {"p1": {}})
    seeds = TRS._seed_answers(tmp3 / "repo", "p1", TRS._first_items("p1", 2))
    (seeds / f"answers_{TRS.MODELS['glm']['slug']}.json").unlink()
    r3 = TRA.orchestrated(tmp3, [TRA.FINISH], [[]], buildings={"p1": {"questions": 2}}, fail={"glm": "early_exit"})
    r3.cli.flags = {"late_questions": {"p1": 1}}
    assert r3.run(**r3.kwargs) == 0
    assert r3.servers.starts == ["glm", "agent"]
    assert SC.LATE_FAILED_NOTE.format(key="glm", reason="early_exit") in r3.record("p1", "recognize")["note"]


def test_a_recognition_exit_2_or_a_failed_qwen_server_is_not_asked_again_as_late(tmp_path, agent_models):
    """The same for a GLM recognition that answers nothing (exit 2, the server up): its first-round questions are no
    late ones (one GLM start); and a Qwen server that fails in phase 3 is not started again for a late question that
    needs it. Both fail on HEAD adc3004 (a second GLM start, a second Qwen start)."""
    r = TRA.orchestrated(tmp_path, [TRA.FINISH], [[]], buildings={"p1": {"questions": 2}})
    r.cli.flags = {"recog_fail": {("p1", "glm")}}
    assert r.run(**r.kwargs) == 0
    assert r.servers.starts == ["glm", "qwen", "agent"]
    assert [s["name"] for s in r.record("p1", "recognize")["steps"]] == ["ask glm", "ask qwen"]
    # Qwen fails in phase 3: the project finalized before that session (first round in the seeds) keeps its late
    # question unanswered, and no second Qwen session starts for it.
    tmp2 = tmp_path / "qwen"
    TRS.make_repo(tmp2, {"p1": {}})
    TRS._seed_answers(tmp2 / "repo", "p1", TRS._first_items("p1", 2))
    r2 = TRA.orchestrated(tmp2, [TRA.FINISH], [[]], buildings={"p1": {"questions": 2}}, fail={"qwen": "early_exit"})
    r2.cli.flags = {"late_questions": {"p1": 1}}
    r2.run(**r2.kwargs)
    assert r2.servers.starts.count("qwen") == 1 and "glm" not in r2.servers.starts
    rec = r2.record("p1", "recognize")
    assert rec["status"] == "warning" and "1 late recognition question(s) left unanswered" in rec["note"]
    assert SC.LATE_FAILED_NOTE.format(key="qwen", reason="early_exit") in rec["note"]
