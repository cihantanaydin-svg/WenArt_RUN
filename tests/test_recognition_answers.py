"""CPU tests of the recognition requests and answers (docs/milestone7.md §1.4, §3.1, §3.4, §11 Y).

- crops: deterministic PNGs without metadata; the canonical input hash (stroke order and sub-millimetre noise do not
  change it; a moved stroke, a wall entering the crop or a changed prompt do; it never reads PNG bytes) and its
  value pinned in ``tests/fixtures/recognition_answers/toy/requests.json`` (the same in the session and on any pod);
  raster crops hash their decoded source pixels; the iso crop's 80 % fill and 1 m bar;
- requests and the answer store (current key + hash + schema-valid data only), ``load`` and ``is_complete``,
  seeding from a results folder (matching key, hash and model id only);
- the CLI with a fake vLLM server: exit 0 (all answered, reused on the next run), 3 (deadline), 2 (no server,
  answers that are not schema-valid, usage errors), ``status``;
- raster room labels: the one rule for every field (two passes, or one pass equal to Tesseract), null never agrees,
  boxes back in page pixels, Tesseract through a subprocess (skipped without tesseract eng+tur);
- the pipeline's exit 4 / ``--answers`` / ``--no-ai`` contract on real01 (needs the generic core of area G).

The fake answers in ``tests/fixtures/recognition_answers/toy/`` are written by ``build_toy`` below (no model ran;
the files say so). Regenerate them after an intended prompt, schema or crop change with
``python tests/test_recognition_answers.py --write-fixture``; pod answers go next to them later (§9.2).
"""
import json
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wenart.recognition import answers as A  # noqa: E402
from wenart.recognition import crops as C  # noqa: E402
from wenart.recognition import prompts, schemas  # noqa: E402
from wenart.recognition import room_labels as RL  # noqa: E402
from wenart.recognition import symbols as S  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "recognition_answers" / "toy"
PROJECTS = ROOT / "projects"
MODELS = A.load_models()


def tesseract_has_langs(*langs: str) -> bool:
    if shutil.which("tesseract") is None:
        return False
    try:
        proc = subprocess.run(["tesseract", "--list-langs"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return False
    have = {line.strip() for line in (proc.stdout + proc.stderr).splitlines()}
    return all(lang in have for lang in langs)


HAS_TESSERACT = tesseract_has_langs("eng", "tur")


# --------------------------------------------------------------------------
# The toy project: three candidates in a 5 x 4 m room (page metres, y up)
# --------------------------------------------------------------------------

def rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]


def toy_candidates() -> list[dict]:
    bed = {"key": "sym_T0_1", "file": "toy.pdf", "page": 1, "level": "L0", "room_type": "bedroom",
           "footprint": {"center": [1.2, 2.5], "size": [1.6, 2.0], "rotation_deg": 0.0},
           "strokes": [rect(0.4, 1.5, 2.0, 3.5), [[0.45, 3.2], [1.95, 3.2]], rect(0.55, 3.25, 1.15, 3.45),
                       rect(1.25, 3.25, 1.85, 3.45)],
           "bbox": [0.4, 1.5, 2.0, 3.5]}
    chair = {"key": "sym_T0_2", "file": "toy.pdf", "page": 1, "level": "L0", "room_type": "bedroom",
             "footprint": {"center": [3.425, 1.025], "size": [0.45, 0.45], "rotation_deg": 0.0},
             "strokes": [rect(3.2, 0.8, 3.65, 1.25), [[3.2, 1.15], [3.65, 1.15]]],
             "bbox": [3.2, 0.8, 3.65, 1.25]}
    hatch = {"key": "sym_T0_3", "file": "toy.pdf", "page": 1, "level": "L0", "room_type": "bedroom",
             "footprint": {"center": [3.85, 3.4], "size": [0.9, 0.3], "rotation_deg": 0.0},
             "strokes": [[[3.4 + 0.1 * i, 3.25], [3.5 + 0.1 * i, 3.55]] for i in range(9)],
             "bbox": [3.4, 3.25, 4.3, 3.55]}
    return [bed, chair, hatch]


def toy_context(cands: list[dict], key: str) -> dict:
    from shapely.geometry import box
    walls = [box(-0.2, -0.2, 5.2, 0.0), box(-0.2, 4.0, 5.2, 4.2), box(-0.2, 0.0, 0.0, 4.0), box(5.0, 0.0, 5.2, 4.0)]
    others = [pts for c in cands if c["key"] != key for pts in c["strokes"]]
    return {"walls": walls, "others": others}


FAKE_ANSWERS = {   # key -> (qwen answer, glm answer): agree, disagree, both not_furniture
    "sym_T0_1": ({"type": "bed_double", "front": "bottom", "confidence": 0.9, "reason": "wide bed, two pillows"},
                 {"type": "bed_double", "front": "bottom", "confidence": 0.8, "reason": "double bed"}),
    "sym_T0_2": ({"type": "chair", "front": "top", "confidence": 0.6, "reason": "small square seat"},
                 {"type": "armchair", "front": "top", "confidence": 0.5, "reason": "seat with a back"}),
    "sym_T0_3": ({"type": "not_furniture", "front": "none", "confidence": 0.7, "reason": "hatching"},
                 {"type": "not_furniture", "front": "none", "confidence": 0.6, "reason": "diagonal lines"}),
}


def build_toy(rec_dir: Path) -> list[dict]:
    """Render the toy crops into ``<rec_dir>/crops``, write ``requests.json``; return the items."""
    cands = toy_candidates()
    items = []
    for cand in cands:
        rendered = C.render_pair(cand, toy_context(cands, cand["key"]), rec_dir / A.CROPS_DIR, cand["key"])
        items.append(S.question(cand, rendered))
    A.write_requests(rec_dir, "toy", items)
    return items


def write_fake_answers(rec_dir: Path, items: list[dict], answers=FAKE_ANSWERS) -> None:
    for idx, key in enumerate(A.MODEL_KEYS):
        store = A.AnswerStore.for_model(rec_dir, key, MODELS)
        for item in items:
            data = answers[item["key"]][idx]
            store.put(item["key"], {"task": item["task"], "input_sha256": item["input_sha256"], "data": data,
                                    "raw_text": json.dumps(data), "error": None, "attempts": 1, "latency_s": 0.0,
                                    "model": store.data["model"], "seed": 0, "images": item["images"]},
                      save=False)
        store.data["fake"] = True
        store.data["note"] = "fake answers written by tests/test_recognition_answers.py (no model ran)"
        store.save()


def write_fixture(dest: Path = FIXTURE) -> None:
    """(Re)write the committed toy fixture: requests.json and the fake answer files (no crops)."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        rec = Path(tmp)
        items = build_toy(rec)
        write_fake_answers(rec, items)
        dest.mkdir(parents=True, exist_ok=True)
        for name in [A.REQUESTS_NAME] + [A.answers_path(rec, MODELS[k]["slug"]).name for k in A.MODEL_KEYS]:
            shutil.copy2(rec / name, dest / name)


@pytest.fixture()
def toy(tmp_path):
    rec = tmp_path / "recognition"
    items = build_toy(rec)
    return rec, items


# --------------------------------------------------------------------------
# Crops and the canonical hash
# --------------------------------------------------------------------------

def png_chunks(path: Path) -> list[str]:
    data = Path(path).read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    pos, out = 8, []
    while pos < len(data):
        length = int.from_bytes(data[pos:pos + 4], "big")
        out.append(data[pos + 4:pos + 8].decode("ascii"))
        pos += 12 + length
    return out


def test_crops_are_deterministic_grey_pngs_without_metadata(tmp_path):
    from PIL import Image
    cands = toy_candidates()
    a = C.render_pair(cands[0], toy_context(cands, "sym_T0_1"), tmp_path / "a", "sym_T0_1")
    b = C.render_pair(cands[0], toy_context(cands, "sym_T0_1"), tmp_path / "b", "sym_T0_1")
    assert a["input_sha256"] == b["input_sha256"]
    for name in ("ctx_png", "iso_png"):
        assert Path(a[name]).read_bytes() == Path(b[name]).read_bytes()
        assert set(png_chunks(a[name])) == {"IHDR", "IDAT", "IEND"}
        with Image.open(a[name]) as img:
            assert img.mode == "L" and img.size == (C.CROP_PX, C.CROP_PX)
    assert Path(a["ctx_png"]).name == "sym_T0_1_ctx.png" and Path(a["iso_png"]).name == "sym_T0_1_iso.png"


def test_hash_is_a_canonical_description_not_png_bytes(tmp_path):
    cands = toy_candidates()
    bed, ctx = cands[0], toy_context(cands, "sym_T0_1")
    base = C.render_pair(bed, ctx, tmp_path, "sym_T0_1")["input_sha256"]
    # The hash is the description's: computed without any file.
    assert C.canonical_sha256(C.vector_description(bed, ctx)) == base
    # Re-saving the PNG with metadata does not change it.
    from PIL import Image, PngImagePlugin
    info = PngImagePlugin.PngInfo()
    info.add_text("Software", "something else")
    with Image.open(tmp_path / "sym_T0_1_ctx.png") as img:
        img.save(tmp_path / "sym_T0_1_ctx.png", pnginfo=info)
    assert C.canonical_sha256(C.vector_description(bed, ctx)) == base
    # Stroke order and sub-millimetre noise do not change it.
    shuffled = dict(bed, strokes=list(reversed(bed["strokes"])))
    assert C.canonical_sha256(C.vector_description(shuffled, ctx)) == base
    noisy = dict(bed, strokes=[[[x + 0.0001, y - 0.0002] for x, y in s] for s in bed["strokes"]])
    assert C.canonical_sha256(C.vector_description(noisy, ctx)) == base
    # A moved stroke, a wall entering the context square and a changed prompt do.
    moved = dict(bed, strokes=[[[x + 0.002, y] for x, y in bed["strokes"][0]]] + bed["strokes"][1:])
    assert C.canonical_sha256(C.vector_description(moved, ctx)) != base
    from shapely.geometry import box
    near = dict(ctx, walls=ctx["walls"] + [box(2.5, 1.0, 2.7, 3.0)])
    far = dict(ctx, walls=ctx["walls"] + [box(20.0, 1.0, 20.2, 3.0)])
    assert C.canonical_sha256(C.vector_description(bed, near)) != base
    assert C.canonical_sha256(C.vector_description(bed, far)) == base
    as_lists = dict(ctx, walls=[list(w.exterior.coords) for w in ctx["walls"]])          # outlines as point lists
    assert C.canonical_sha256(C.vector_description(bed, as_lists)) == base
    old = prompts.SYMBOL_QUESTION
    try:
        prompts.SYMBOL_QUESTION = old + " "
        assert C.canonical_sha256(C.vector_description(bed, ctx)) != base
    finally:
        prompts.SYMBOL_QUESTION = old


def test_hash_covers_the_question_facts_of_the_item(tmp_path):
    """Prep pod P5: the question names the room, the fitting types and the neighbours, so they are hashed (a stored
    answer to another question is stale). Raster questions never depend on room names or neighbours (they may change
    with the label answers of the same round), so those do not change a raster hash (review raster-1)."""
    cands = toy_candidates()
    chair, ctx = cands[1], toy_context(cands, "sym_T0_2")
    base = C.canonical_sha256(C.vector_description(chair, ctx))
    for change in ({"room_type": "living"}, {"room_label": "Salon"},
                   {"neighbours": {"similar": 2, "next_to": None, "around": None}},
                   {"footprint": dict(chair["footprint"], size=[0.7, 0.7])}):
        assert C.canonical_sha256(C.vector_description(dict(chair, **change), ctx)) != base, change
    page = np.full((600, 800), 255, np.uint8)
    page[200:260, 300:420] = 0
    raster = {"key": "sym_R0_1", "footprint": {"center": [3.6, 3.7], "size": [1.2, 0.6], "rotation_deg": 0.0},
              "strokes": [rect(3.0, 3.4, 4.2, 4.0)], "bbox": [3.0, 3.4, 4.2, 4.0]}
    rctx = {"image": page, "to_px": [100.0, 0.0, 0.0, 0.0, -100.0, 600.0]}
    rbase = C.canonical_sha256(C.raster_crops(raster, rctx)[0])
    for change in ({"room_type": "living"}, {"room_label": "Salon"},
                   {"neighbours": {"similar": 2, "next_to": None, "around": None}}):
        assert C.canonical_sha256(C.raster_crops(dict(raster, **change), rctx)[0]) == rbase, change
    desc = C.raster_crops(raster, rctx)[0]
    assert desc["question"]["facts"]["kind"] == "raster" and "mid-grey" not in desc["question"]["prompt"]


def test_call_args_ask_exactly_the_hashed_question(toy):
    rec, items = toy
    for item in items:
        args = A.call_args(item, rec)
        digest = C.question_digest("symbol_type", item["question"])
        assert args["prompt"] == digest["prompt"] and args["schema"] == digest["schema"]
        assert args["schema"]["properties"]["type"]["enum"] == item["question"]["choices"]
        assert args["labels"] == list(prompts.SYMBOL_IMAGE_LABELS)
    bed = A.call_args(items[0], rec)
    assert "bed_double" in bed["schema"]["properties"]["type"]["enum"]
    assert "chair" not in bed["schema"]["properties"]["type"]["enum"]
    assert "bed_double" not in A.call_args(items[1], rec)["schema"]["properties"]["type"]["enum"]
    # An item without facts (hand-made, older requests) gets the generic question and the full list.
    bare = {k: v for k, v in items[0].items() if k != "question"}
    assert A.call_args(bare, rec)["prompt"] == prompts.symbol_type_prompt()
    assert A.call_args(bare, rec)["schema"] == schemas.SYMBOL_TYPE


def test_requests_refuse_a_broken_question(toy, tmp_path):
    _, items = toy
    for bad in ({"kind": "vector", "choices": ["couch", "unknown"]}, {"kind": "vector", "choices": []},
                {"kind": "photo", "choices": ["chair"]}, "chair"):
        with pytest.raises(ValueError, match="question"):
            A.write_requests(tmp_path, "toy", [dict(items[0], question=bad)])


def test_canonical_rings_do_not_depend_on_vertex_order():
    ring = [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]
    rotated = [[1, 1], [0, 1], [0, 0], [1, 0], [1, 1]]
    clockwise = list(reversed(ring))
    extra = [[0, 0], [0.5, 0], [1, 0], [1, 1], [0, 1], [0, 0]]          # a collinear vertex
    canon = C._canonical_ring(ring)
    assert C._canonical_ring(rotated) == canon == C._canonical_ring(clockwise) == C._canonical_ring(extra)
    assert canon[0] == [0, 0]


def test_pinned_hashes_match_the_committed_fixture(tmp_path):
    """The canonical hash is the same in every session and on every pod: the committed hashes still come out."""
    committed = json.loads((FIXTURE / A.REQUESTS_NAME).read_text(encoding="utf-8"))
    items = build_toy(tmp_path / "recognition")
    assert [i["key"] for i in items] == [i["key"] for i in committed["items"]]
    for mine, pinned in zip(items, committed["items"]):
        assert mine["input_sha256"] == pinned["input_sha256"], (
            f"{mine['key']}: the canonical description changed; if intended (prompt, schema or crop change), "
            "rewrite the fixture with `python tests/test_recognition_answers.py --write-fixture`")


def test_iso_crop_fills_80_percent_and_draws_a_1_m_bar(tmp_path):
    from PIL import Image
    cands = toy_candidates()
    for cand, big in ((cands[0], True), (cands[1], False)):
        res = C.render_pair(cand, {"walls": [], "others": []}, tmp_path, cand["key"])
        arr = np.asarray(Image.open(res["iso_png"]))
        side_mm = res["crop"]["iso_box"][2] - res["crop"]["iso_box"][0]
        px_per_m = C.CROP_PX / side_mm * 1000.0
        bar_rows = arr[C.CROP_PX - C.BAR_BOTTOM_PX - C.BAR_THICK_PX:C.CROP_PX - C.BAR_BOTTOM_PX]
        bar_len = int((bar_rows == 0).all(axis=0).sum())
        assert abs(bar_len - px_per_m) <= 1.5
        obj = arr[:C.CROP_PX - C.BAR_BOTTOM_PX - C.BAR_THICK_PX - 4]
        ys, xs = np.nonzero(obj < 255)
        extent = max(xs.max() - xs.min(), ys.max() - ys.min())
        if big:     # 2.0 m bed: the object fills 80 % (+ the 2 px line)
            assert abs(extent - C.ISO_FILL * C.CROP_PX) <= 4
        else:       # 0.45 m chair: zoom capped so the 1 m bar is BAR_MAX_PX long
            assert bar_len == C.BAR_MAX_PX and extent < C.ISO_FILL * C.CROP_PX


def test_ctx_crop_shows_walls_others_and_a_dashed_box(tmp_path):
    from PIL import Image
    cands = toy_candidates()
    ctx = toy_context(cands, "sym_T0_2")
    ctx["others"].append(rect(2.5, 0.5, 2.9, 0.9))                         # a neighbour inside the square
    res = C.render_pair(cands[1], ctx, tmp_path, "sym_T0_2")
    arr = np.asarray(Image.open(res["ctx_png"]))
    values = set(np.unique(arr).tolist())
    assert {C.PAPER, C.WALL_GREY, C.OTHER_GREY, C.INK} <= values
    assert values <= {C.PAPER, C.WALL_GREY, C.OTHER_GREY, C.INK}          # LINE_8: no anti-aliased greys
    ctx = res["crop"]["ctx_box"]
    assert ctx[2] - ctx[0] == 2500                                           # max(2.5 m, 1.6 x 0.45 m)


def test_raster_candidates_hash_their_source_pixels(tmp_path):
    rng = np.random.default_rng(0)
    page = np.full((600, 800), 255, np.uint8)
    page[200:260, 300:420] = 0                                     # a drawn object
    page[100:110, :] = 90                                          # a wall band
    to_px = [100.0, 0.0, 0.0, 0.0, -100.0, 600.0]                  # 100 px/m, y flipped, page 8 x 6 m
    cand = {"key": "sym_R0_1", "footprint": {"center": [3.6, 3.7], "size": [1.2, 0.6], "rotation_deg": 0.0},
            "strokes": [rect(3.0, 3.4, 4.2, 4.0)], "bbox": [3.0, 3.4, 4.2, 4.0]}
    a = C.render_pair(cand, {"image": page, "to_px": to_px}, tmp_path / "a", "sym_R0_1")
    b = C.render_pair(cand, {"image": page.copy(), "to_px": to_px}, tmp_path / "b", "sym_R0_1")
    assert a["input_sha256"] == b["input_sha256"] and a["crop"]["kind"] == "raster"
    assert Path(a["ctx_png"]).read_bytes() == Path(b["ctx_png"]).read_bytes()
    inside, outside = page.copy(), page.copy()
    inside[230, 350] = 128                                         # inside both crops
    outside[590, 10] = int(rng.integers(0, 200))                   # far outside
    assert C.render_pair(cand, {"image": inside, "to_px": to_px}, tmp_path / "c", "k")["input_sha256"] != \
        a["input_sha256"]
    assert C.render_pair(cand, {"image": outside, "to_px": to_px}, tmp_path / "d", "k")["input_sha256"] == \
        a["input_sha256"]
    from PIL import Image
    iso = np.asarray(Image.open(a["iso_png"]))
    assert iso.shape == (C.CROP_PX, C.CROP_PX) and (iso == 0).any()
    # The wall band is outside the object's box: kept in the context crop, blanked in the iso crop.
    ctx = np.asarray(Image.open(a["ctx_png"]))
    assert (ctx == 90).sum() > 1000 and (iso == 90).sum() == 0


# --------------------------------------------------------------------------
# Requests and the answer store
# --------------------------------------------------------------------------

def test_requests_file_shape(toy):
    rec, items = toy
    doc = json.loads((rec / A.REQUESTS_NAME).read_text(encoding="utf-8"))
    assert doc["schema_version"] == "0.1" and doc["kind"] == "recognition_requests" and doc["project"] == "toy"
    assert doc["crop_version"] == C.CROP_VERSION
    assert doc["models"]["qwen"]["pass"] == 1 and doc["models"]["glm"]["pass"] == 2
    assert [i["key"] for i in doc["items"]] == ["sym_T0_1", "sym_T0_2", "sym_T0_3"]
    for item in doc["items"]:
        assert item["task"] == "symbol_type"
        for img in item["images"]:
            assert (rec / img).is_file()
    assert A.read_requests(rec)["items"] == doc["items"]
    assert A.read_requests(rec / "nothing") is None


def test_write_requests_rejects_bad_items(toy, tmp_path):
    _, items = toy
    with pytest.raises(ValueError, match="duplicate"):
        A.write_requests(tmp_path, "toy", [items[0], items[0]])
    with pytest.raises(ValueError, match="unknown task"):
        A.write_requests(tmp_path, "toy", [dict(items[0], task="symbols")])
    with pytest.raises(ValueError, match="sha256"):
        A.write_requests(tmp_path, "toy", [dict(items[0], input_sha256="abc")])
    with pytest.raises(ValueError, match="images"):
        A.write_requests(tmp_path, "toy", [dict(items[0], images=[])])


def test_answer_store_counts_only_current_schema_valid_answers(toy):
    rec, items = toy
    write_fake_answers(rec, items)
    store = A.AnswerStore.for_model(rec, "qwen", MODELS)
    assert all(store.valid(i) for i in items)
    assert store.valid(dict(items[0], input_sha256="0" * 64)) is None                 # stale
    rec0 = dict(store.get("sym_T0_1"))
    store.put("sym_T0_1", dict(rec0, data=None))                                        # failed call
    assert store.valid(items[0]) is None and A.item_state(store, items[0]) == "failed"
    store.put("sym_T0_1", dict(rec0, data={"type": "couch", "front": "top", "confidence": 1, "reason": ""}))
    assert store.valid(items[0]) is None                                                # not schema-valid
    store.put("sym_T0_1", dict(rec0, input_sha256="1" * 64))
    assert A.item_state(store, items[0]) == "stale"
    store.put("sym_T0_1", dict(rec0, model="someone/else"))                             # another model's answer
    assert store.valid(items[0]) is None and A.item_state(store, items[0]) == "stale"
    del store.calls["sym_T0_1"]
    assert A.item_state(store, items[0]) == "missing"
    # The file keeps the calls in key order.
    store.put("sym_T0_0", dict(rec0))
    assert list(json.loads(store.path.read_text(encoding="utf-8"))["calls"]) == sorted(store.calls)


def test_load_gives_every_model_per_key_and_none_for_stale_or_missing(toy):
    rec, items = toy
    assert A.load(rec) == {i["key"]: {"qwen": None, "glm": None} for i in items}
    write_fake_answers(rec, items)
    loaded = A.load(rec)
    assert loaded["sym_T0_1"]["qwen"]["type"] == "bed_double" and loaded["sym_T0_2"]["glm"]["type"] == "armchair"
    assert A.is_complete(loaded)
    # The pipeline passes its own items: a changed candidate makes its answers stale.
    changed = [dict(items[0], input_sha256="2" * 64)] + items[1:]
    loaded = A.load(rec, changed)
    assert loaded["sym_T0_1"] == {"qwen": None, "glm": None} and not A.is_complete(loaded)
    assert A.is_complete(loaded, ["sym_T0_2", "sym_T0_3"])


def test_fake_answers_through_the_two_pass_rule(toy):
    rec, items = toy
    write_fake_answers(rec, items)
    loaded = A.load(rec)
    table = S.load_size_table()
    cands = {c["key"]: c for c in toy_candidates()}
    bed = S.decide(cands["sym_T0_1"], loaded["sym_T0_1"], table, "bedroom")
    chair = S.decide(cands["sym_T0_2"], loaded["sym_T0_2"], table, "bedroom")
    hatch = S.decide(cands["sym_T0_3"], loaded["sym_T0_3"], table, "bedroom")
    assert (bed["type"], bed["status"], bed["front"]) == ("bed_double", "verified", 270.0)
    assert (chair["type"], chair["status"], chair["conflict"]["kind"]) == ("unknown", "unverified",
                                                                          "symbol_type_disagreement")
    assert (hatch["type"], hatch["build"]) == ("unknown", False)


# --------------------------------------------------------------------------
# Seeding
# --------------------------------------------------------------------------

def test_seeding_copies_only_matching_key_hash_and_model(toy, tmp_path):
    rec, items = toy
    seed_dir = tmp_path / "results"
    shutil.copytree(FIXTURE, seed_dir)
    slug = MODELS["qwen"]["slug"]
    seed_file = seed_dir / f"answers_{slug}.json"
    doc = json.loads(seed_file.read_text(encoding="utf-8"))
    doc["calls"]["sym_T0_2"]["input_sha256"] = "3" * 64                                 # stale
    doc["calls"]["sym_T0_3"]["data"] = {"type": "", "front": "none"}                    # not schema-valid
    seed_file.write_text(json.dumps(doc), encoding="utf-8")
    store = A.AnswerStore.for_model(rec, "qwen", MODELS)
    logs = []
    assert A.seed_answers(store, items, seed_dir, log=logs.append) == 1
    saved = json.loads(store.path.read_text(encoding="utf-8"))
    assert list(saved["calls"]) == ["sym_T0_1"] and saved["calls"]["sym_T0_1"]["seeded_from"].endswith(slug + ".json")
    # Another model's file is never seeded.
    doc["model"] = "someone/else"
    seed_file.write_text(json.dumps(doc), encoding="utf-8")
    other = A.AnswerStore(tmp_path / "x.json", "qwen", slug, MODELS["qwen"]["id"])
    assert A.seed_answers(other, items, seed_dir, log=logs.append) == 0
    assert any("not " + MODELS["qwen"]["id"] in m for m in logs)
    # No file for the slug: nothing.
    assert A.seed_answers(other, items, tmp_path / "empty", log=logs.append) == 0


# --------------------------------------------------------------------------
# CLI with a fake server
# --------------------------------------------------------------------------

def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class BadVLM:
    """A server that answers every completion with JSON that breaks the schema."""

    def __init__(self):
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                return

            def _send(self, code, data):
                raw = json.dumps(data).encode("utf-8") if data is not None else b""
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def do_GET(self):  # noqa: N802
                self._send(200, None if self.path == "/health" else {"data": [{"id": "bad"}]})

            def do_POST(self):  # noqa: N802
                self.rfile.read(int(self.headers.get("Content-Length") or 0))
                content = json.dumps({"type": "couch", "front": "up"})
                self._send(200, {"choices": [{"message": {"content": content}}], "usage": {}})

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True

    def __enter__(self):
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return f"http://127.0.0.1:{self.server.server_address[1]}/v1"

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()


def run_cli(*args) -> int:
    return A.main([str(a) for a in args])


def test_cli_answers_everything_then_reuses(toy, capsys):
    from fakes.fake_vlm import FakeVLM
    rec, items = toy
    fake = FakeVLM()
    with fake as url:
        assert run_cli("ask", rec, "--model-key", "qwen", "--server", url, "--workers", "2") == 0
        asked = sum(fake.requests.values())
        assert asked == len(items)
        assert run_cli("ask", rec, "--model-key", "qwen", "--server", url) == 0          # reused, nothing asked
        assert sum(fake.requests.values()) == asked
        assert run_cli("ask", rec, "--model-key", "glm", "--server", url, "--workers", "1") == 0
    saved = json.loads((rec / f"answers_{MODELS['qwen']['slug']}.json").read_text(encoding="utf-8"))
    assert saved["kind"] == "recognition_answers" and saved["model"] == MODELS["qwen"]["id"]
    assert saved["incomplete"] is False and sorted(saved["calls"]) == [i["key"] for i in items]
    for call in saved["calls"].values():
        assert schemas.is_valid("symbol_type", call["data"]) and call["seed"] == 0
    assert A.is_complete(A.load(rec))
    assert run_cli("status", rec) == 0
    out = capsys.readouterr().out
    assert "3 answered, 0 stale, 0 failed, 0 missing" in out


def test_cli_exit_3_at_the_deadline_and_status_1(toy, capsys):
    from fakes.fake_vlm import FakeVLM
    rec, items = toy
    with FakeVLM() as url:
        assert run_cli("ask", rec, "--model-key", "glm", "--server", url, "--deadline", time.time() - 1) == 3
    saved = json.loads((rec / f"answers_{MODELS['glm']['slug']}.json").read_text(encoding="utf-8"))
    assert saved["incomplete"] is True and saved["calls"] == {}
    assert run_cli("status", rec, "--json") == 1
    summary = json.loads(capsys.readouterr().out.split("\n", 1)[1])
    assert summary["complete"] is False and summary["models"]["glm"]["missing"] == len(items)
    # WENART_DEADLINE is the default deadline.
    os.environ["WENART_DEADLINE"] = str(time.time() - 1)
    try:
        assert run_cli("ask", rec, "--model-key", "glm", "--server", "http://127.0.0.1:9/v1") == 3
    finally:
        del os.environ["WENART_DEADLINE"]


def test_cli_exit_2_without_a_server_or_with_invalid_answers(toy):
    rec, items = toy
    dead = f"http://127.0.0.1:{free_port()}/v1"
    assert run_cli("ask", rec, "--model-key", "qwen", "--server", dead) == 2
    with BadVLM() as url:
        assert run_cli("ask", rec, "--model-key", "qwen", "--server", url, "--retries", "1") == 2
    saved = json.loads((rec / f"answers_{MODELS['qwen']['slug']}.json").read_text(encoding="utf-8"))
    assert all(c["data"] is None and c["error"].startswith("schema:") for c in saved["calls"].values())
    assert A.load(rec)["sym_T0_1"]["qwen"] is None


def test_cli_usage_errors_exit_2(toy, tmp_path):
    rec, _ = toy
    assert run_cli("ask", rec, "--model-key", "llava") == 2
    assert run_cli("ask", tmp_path / "nothing", "--model-key", "qwen") == 2
    assert run_cli("status", tmp_path / "nothing") == 2


def test_cli_seeded_answers_need_no_server(toy):
    rec, items = toy
    dead = f"http://127.0.0.1:{free_port()}/v1"
    for key in A.MODEL_KEYS:
        assert run_cli("ask", rec, "--model-key", key, "--server", dead, "--seed-answers", FIXTURE) == 0
    loaded = A.load(rec)
    assert A.is_complete(loaded)
    assert loaded["sym_T0_1"]["qwen"] == FAKE_ANSWERS["sym_T0_1"][0]


def test_cli_asks_room_label_requests_with_one_image(tmp_path):
    from fakes.fake_vlm import FakeVLM
    import cv2
    rec = tmp_path / "recognition"
    page = np.full((400, 600), 255, np.uint8)
    cv2.putText(page, "SALON", (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, 0, 2)
    face = {"key": "lbl_L0_1", "file": "plan_scan.png", "page": 1, "level": "L0",
            "crop": RL.render_crop(page, [100, 100, 500, 300], 80.0, rec / A.CROPS_DIR, "lbl_L0_1")}
    A.write_requests(rec, "scan", [RL.question(face)])
    with FakeVLM() as url:
        for key in A.MODEL_KEYS:
            assert run_cli("ask", rec, "--model-key", key, "--server", url) == 0
    loaded = A.load(rec)
    assert A.is_complete(loaded)
    assert schemas.is_valid("room_label", loaded["lbl_L0_1"]["qwen"])
    # The fake answers "" for every text: empty values never agree, the room stays unverified.
    res = RL.decide(face, loaded["lbl_L0_1"])
    assert res["label"] is None and res["status"] == "unverified"


def test_cli_runs_as_a_module(toy):
    rec, _ = toy
    proc = subprocess.run([sys.executable, "-m", "wenart.recognition.answers", "status", str(rec)],
                          capture_output=True, text=True, cwd=ROOT, timeout=120)
    assert proc.returncode == 1 and "3 item(s)" in proc.stdout


# --------------------------------------------------------------------------
# Raster room labels (§3.4)
# --------------------------------------------------------------------------

def label_answer(label, size=None, area=None, box=(300, 300, 500, 360)):
    return {"label": label, "size_text": size, "area_text": area, "box": list(box) if box else None}


@pytest.fixture()
def face(tmp_path):
    import cv2
    page = np.full((800, 1200), 255, np.uint8)
    cv2.rectangle(page, (100, 100), (700, 600), 0, 6)
    cv2.putText(page, "KITCHEN", (280, 320), cv2.FONT_HERSHEY_SIMPLEX, 1.4, 0, 3)
    cv2.putText(page, "9'3\" x 10'3\"", (270, 380), cv2.FONT_HERSHEY_SIMPLEX, 1.0, 0, 2)
    crop = RL.render_crop(page, [100, 100, 700, 600], 100.0, tmp_path / "crops", "lbl_L0_1")
    return {"key": "lbl_L0_1", "file": "plan_scan.png", "page": 1, "level": "L0", "crop": crop, "page_img": page}


def test_room_label_crop_and_question(face, tmp_path):
    from PIL import Image
    crop = face["crop"]
    assert crop["crop"]["rect_px"] == [50, 50, 750, 650]                  # grown by 0.5 m at 100 px/m
    assert max(crop["crop"]["size"]) == RL.CROP_LONG_PX
    with Image.open(crop["png"]) as img:
        assert img.size == tuple(crop["crop"]["size"]) and img.mode == "L"
    assert set(png_chunks(crop["png"])) == {"IHDR", "IDAT", "IEND"}
    again = RL.render_crop(face["page_img"], [100, 100, 700, 600], 100.0, tmp_path / "again", "lbl_L0_1")
    assert again["input_sha256"] == crop["input_sha256"]
    changed = face["page_img"].copy()
    changed[400, 400] = 0
    assert RL.render_crop(changed, [100, 100, 700, 600], 100.0, tmp_path / "c", "x")["input_sha256"] != \
        crop["input_sha256"]
    item = RL.question(face)
    assert item["task"] == "room_label" and item["images"] == ["crops/lbl_L0_1.png"]
    A.check_item(item)


def test_room_label_rule_two_passes_or_one_pass_and_tesseract(face):
    # Two passes agree after normalisation (case, spaces, Turkish dotless i, quote marks).
    res = RL.decide(face, {"qwen": label_answer("Yatak  Odası"), "glm": label_answer("YATAK ODASI")})
    assert res["label"] == "Yatak  Odası" and res["status"] == "verified"
    assert res["fields"]["label"]["path"] == "two_pass"
    res = RL.decide(face, {"qwen": label_answer("LIVING"), "glm": label_answer("Living")})
    assert res["fields"]["label"]["path"] == "two_pass"
    res = RL.decide(face, {"qwen": label_answer("K", size="11’ x 10’"), "glm": label_answer("K", size="11' x 10'")})
    assert res["size_text"] == "11’ x 10’"
    # One pass equal to Tesseract.
    res = RL.decide(face, {"qwen": label_answer("Kitchen"), "glm": label_answer("Store")},
                    [{"text": "KITCHEN", "box": [280, 290, 450, 320], "confidence": 0.9}])
    assert res["label"] == "Kitchen" and res["fields"]["label"]["path"] == "tesseract"
    assert res["box"] == [280, 290, 450, 320]
    assert any(e["method"] == "ocr" and e["text"] == "KITCHEN" for e in res["evidence"])
    # A stacked two-line label read by Tesseract counts joined.
    lines = [{"text": "Bath+", "box": [300, 300, 380, 330], "confidence": 0.9},
             {"text": "Toilet", "box": [300, 335, 390, 365], "confidence": 0.8}]
    res = RL.decide(face, {"qwen": label_answer("Bath+ Toilet"), "glm": label_answer("Bath")}, lines)
    assert res["label"] == "Bath+ Toilet" and res["box"] == [300, 300, 390, 365]
    # Neither: null, both candidates listed, the room unverified.
    res = RL.decide(face, {"qwen": label_answer("Kitchen"), "glm": label_answer("Store")}, ["Dining"])
    assert res["label"] is None and res["status"] == "unverified" and res["box"] is None
    assert [c["value"] for c in res["fields"]["label"]["candidates"]] == ["Kitchen", "Store"]
    assert any("label not accepted" in w for w in res["warnings"])
    # The passes matching two different Tesseract texts is not an acceptance.
    res = RL.decide(face, {"qwen": label_answer("Kitchen"), "glm": label_answer("Store")}, ["KITCHEN", "STORE"])
    assert res["label"] is None and any("different Tesseract texts" in w for w in res["warnings"])


@pytest.mark.parametrize("other", [label_answer(None), label_answer(""), label_answer("   "), None,
                                   {"label": "Kitchen"}])
def test_room_label_null_or_empty_never_agrees(face, other):
    res = RL.decide(face, {"qwen": label_answer(None), "glm": other}, [""])
    assert res["label"] is None and res["status"] == "unverified"
    res = RL.decide(face, {"qwen": label_answer(""), "glm": label_answer("")}, ["", " "])
    assert res["label"] is None


def test_room_label_boxes_come_back_in_page_pixels(face):
    res = RL.decide(face, {"qwen": label_answer("Kitchen", box=(0, 0, 500, 500)),
                           "glm": label_answer("KITCHEN", box=(100, 100, 600, 400))})
    # crop rect [50, 50, 750, 650]: 0..1000 of 700 x 600 px; the agreeing passes' boxes are joined.
    assert res["box"] == [50.0, 50.0, 470.0, 350.0]
    ai = [e for e in res["evidence"] if e["method"] == "ai"]
    assert [e["pass"] for e in ai] == [1, 2] and all(e["confidence"] == RL.AGREE_CONFIDENCE for e in ai)


def test_norm_value():
    assert RL.norm_value(" Bed  Room ") == RL.norm_value("BED ROOM") == "bed room"
    assert RL.norm_value("YATAK ODASI") == RL.norm_value("Yatak Odası") == RL.norm_value("yatak odasi")
    assert RL.norm_value("14’-0″ X 12’-0″") == RL.norm_value("14'-0\" x 12'-0\"")
    assert RL.norm_value(None) is None and RL.norm_value("  ") is None


def test_tesseract_texts_join_stacked_lines_only():
    lines = [{"text": "Bath+", "box": [300, 300, 380, 330], "confidence": 0.9},
             {"text": "Toilet", "box": [300, 335, 390, 365], "confidence": 0.8},
             {"text": "7' x 5'", "box": [300, 370, 380, 395], "confidence": 0.9},
             {"text": "Far", "box": [900, 335, 950, 365], "confidence": 0.9}]
    texts = [t["text"] for t in RL.tesseract_texts(lines)]
    assert "Bath+ Toilet" in texts and "Bath+ Toilet 7' x 5'" in texts and "Toilet 7' x 5'" in texts
    assert not any("Far" in t and " " in t for t in texts)


def test_items_inside_a_face():
    items = [{"text": "A", "box": [10, 10, 20, 20]}, {"text": "B", "box": [200, 200, 220, 220]}]
    assert [i["text"] for i in RL.items_inside(items, [0, 0, 100, 100])] == ["A"]
    square = [[100, 100], [300, 100], [300, 300], [100, 300]]
    assert [i["text"] for i in RL.items_inside(items, square)] == ["B"]


@pytest.mark.skipif(not HAS_TESSERACT, reason="tesseract with the eng and tur language packs not installed")
def test_tesseract_reads_the_face_and_confirms_one_pass(face):
    items = RL.tesseract_face(face)
    texts = {RL.norm_value(i["text"]) for i in items}
    assert "kitchen" in texts
    kitchen = next(i for i in items if RL.norm_value(i["text"]) == "kitchen")
    x0, y0, x1, y1 = kitchen["box"]
    assert 260 <= x0 <= 300 and 270 <= y0 <= 300 and 430 <= x1 <= 470 and 310 <= y1 <= 335   # page pixels
    res = RL.decide(face, {"qwen": label_answer("Kitchen", size="9'3\" x 10'3\""),
                           "glm": label_answer("Pantry", size=None)}, items)
    assert res["label"] == "Kitchen" and res["fields"]["label"]["path"] == "tesseract"


@pytest.mark.skipif(not HAS_TESSERACT, reason="tesseract with the eng and tur language packs not installed")
def test_tesseract_reads_rotated_text_at_90_degrees(tmp_path):
    import cv2
    img = np.full((600, 300), 255, np.uint8)
    strip = np.full((300, 600), 255, np.uint8)
    cv2.putText(strip, "DINING", (150, 170), cv2.FONT_HERSHEY_SIMPLEX, 1.6, 0, 3)
    img[:, :] = cv2.rotate(strip, cv2.ROTATE_90_COUNTERCLOCKWISE)              # reads bottom to top
    items = RL.tesseract_items(img, rotations=(0, 90))
    hits = [i for i in items if RL.norm_value(i["text"]) == "dining"]
    assert hits and hits[0]["rotation"] == 90
    x0, y0, x1, y1 = hits[0]["box"]
    assert x1 - x0 < y1 - y0 and 0 <= x0 and x1 <= 300 and 0 <= y0 and y1 <= 600     # upright box


# --------------------------------------------------------------------------
# Pipeline: exit 4, --answers, --no-ai (§1.4) on real01
# --------------------------------------------------------------------------

def run_pipeline(out: Path, *extra) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "wenart.ingest.pipeline", str(PROJECTS / "real01"), "--out",
                           str(out), *[str(e) for e in extra]], capture_output=True, text=True, cwd=ROOT,
                          timeout=1800)


def agreeing_answers(items: list[dict]) -> dict:
    """Fake answers that agree: the first size-table type that fits each footprint (both passes)."""
    table = S.load_size_table()
    out = {}
    for item in items:
        size = item["context"]["footprint"]["size"]
        ftype = next((t for t in table if t != "stair" and S.fits(table, t, size)), "not_furniture")
        ans = {"type": ftype, "front": "none", "confidence": 0.8, "reason": "fake agreeing answer"}
        out[item["key"]] = (ans, ans)
    return out


def test_pipeline_exit_4_then_answers_then_no_ai(tmp_path):
    pytest.importorskip("wenart.ingest.generic.core", reason="the generic core (area G3) is not in this tree yet")
    out = tmp_path / "out"
    first = run_pipeline(out)
    assert first.returncode == 4, first.stdout[-2000:] + first.stderr[-2000:]
    rec = out / "recognition"
    doc = A.read_requests(rec)
    assert doc and doc["items"], "exit 4 without questions"
    for item in doc["items"]:
        assert item["task"] == "symbol_type" and item["key"].startswith("sym_")
        assert all((rec / p).is_file() for p in item["images"])
    building = json.loads((out / "building.json").read_text(encoding="utf-8"))
    asked = [f for f in building["furniture"] if f.get("type_method") == "none"]
    assert asked and all(f["type"] == "unknown" and f["status"] == "unverified" for f in asked)
    # The same inputs give the same questions (hashes) on a second run.
    again = run_pipeline(tmp_path / "again")
    assert again.returncode == 4
    assert [i["input_sha256"] for i in A.read_requests(tmp_path / "again" / "recognition")["items"]] == \
        [i["input_sha256"] for i in doc["items"]]
    # With complete (agreeing) answers the pipeline never exits 4 and applies the types.
    write_fake_answers(rec, doc["items"], agreeing_answers(doc["items"]))
    final = run_pipeline(out, "--answers", rec)
    assert final.returncode in (0, 1) and final.returncode != 4, final.stdout[-2000:]
    building = json.loads((out / "building.json").read_text(encoding="utf-8"))
    assert any(f.get("type_method") == "ai_two_pass" for f in building["furniture"])
    # --no-ai never exits 4 either: unanswered pieces stay unknown / unverified.
    no_ai = run_pipeline(tmp_path / "no_ai", "--no-ai")
    assert no_ai.returncode in (0, 1) and no_ai.returncode != 4, no_ai.stdout[-2000:]


if __name__ == "__main__":
    if "--write-fixture" in sys.argv:
        write_fixture()
        print(f"wrote {FIXTURE}")
