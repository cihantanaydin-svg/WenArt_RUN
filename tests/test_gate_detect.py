"""CPU tests of the added-object detector (docs/milestone7.md §8.1, §11 V; ``wenart.gate.detect``).

(Named ``test_gate_detect.py``, not ``test_detect.py``: ``tests/`` has no ``__init__.py``, so pytest imports
test files by their base name, and ``tests/gpu/test_detect.py`` already takes ``test_detect``.)

The model call is replaced by ``FakeDetector`` (``.info()`` + ``.raw(rgb, texts)``),
which turns registered objects (original-image pixel boxes) into raw OWLv2
outputs, so ``boxes_from_raw`` is tested as the exact inverse of the model's
box convention (relative to the padded square). Covered: the query groups
(one per furniture type, the extra objects, decor classes, plain words), the
raw-output conversion (scaling, threshold, per-group NMS), the decision on
canned boxes (Cycles match, coverage by a compatible element, confirmation
by score or by a VLM extra, insertion hits), the ``check.yaml detector:``
block (advisory without thresholds), the calibration maths, the benign
perturbations, ``run_detect`` and both CLI commands on the toy project, and
``combine`` with and without thresholds (rejection, single-pass extras
confirmed by a detector box, plants never reject, missing detection).
"""
import copy
import json
from pathlib import Path

import numpy as np
import pytest

import vc_toy as T
from wenart import views as V
from wenart.gate import detect as D
from wenart.gate.__main__ import main as gate_main
from wenart.vision_check import combine as CB
from wenart.vision_check import schemas as S
from wenart.vision_check.cli import main as check_main
from wenart.vision_check.project import Project

ROOT = Path(__file__).resolve().parents[1]
# The check.yaml detector block before calibration (advisory: listed, never rejected). The committed block is
# calibrated since the M7 prep pod, so the advisory tests pass this one explicitly.
ADVISORY = {"advisory": True, "t_det": None, "t_strong": None, "match_iou": 0.3, "cover_frac": 0.5,
            "confirm_iou": 0.3, "calibration": None}
ADVISORY_BLOCK_CFG = {"detector": ADVISORY}

CAM = T.CAMERA["name"]
REV = "cfd3195ba4ea9592eec887ded089f4c08eff231d"


# --------------------------------------------------------------------------
# Fake detector
# --------------------------------------------------------------------------

def logit(p: float) -> float:
    return float(np.log(p / (1.0 - p)))


class FakeDetector:
    """Registered images (by their pixels) -> objects ``(text, score, [x0, y0, x1, y1] original pixels)``."""

    def __init__(self):
        self.images = []
        self.calls = 0

    def info(self):
        return {"repo": "google/owlv2-base-patch16-ensemble", "revision": REV, "licence": "Apache-2.0"}

    def register(self, rgb, objects):
        self.images.append((np.asarray(rgb, dtype=np.uint8), list(objects)))

    def raw(self, small, texts):
        self.calls += 1
        small = np.asarray(small)
        objects = []
        for rgb, objs in self.images:
            if np.array_equal(D.model_image(rgb), small):
                objects = objs
                H, W = rgb.shape[:2]
                break
        else:
            H, W = small.shape[:2]
        mh, mw = small.shape[:2]
        side = max(mw, mh)
        logits = np.full((len(objects) + 1, len(texts)), -9.0, np.float32)
        boxes = np.zeros((len(objects) + 1, 4), np.float32)
        boxes[-1] = (0.5, 0.5, 0.2, 0.2)                        # a background patch below every threshold
        for i, (text, score, box) in enumerate(objects):
            logits[i, texts.index(text)] = logit(score)
            x0, y0, x1, y1 = (box[0] * mw / W, box[1] * mh / H, box[2] * mw / W, box[3] * mh / H)
            boxes[i] = ((x0 + x1) / 2 / side, (y0 + y1) / 2 / side, (x1 - x0) / side, (y1 - y0) / side)
        return logits, boxes


def bx(group, score, box, cls=None):
    return {"group": group, "text": D.GROUP_BY_NAME[group].texts[0], "score": score, "box_px": list(box),
            "class": cls or D.box_class(group, box, (1000, 1000))}


# --------------------------------------------------------------------------
# Query groups and classes
# --------------------------------------------------------------------------

def test_one_plain_word_group_per_furniture_type_and_the_extra_objects():
    assert set(D.FURNITURE_WORDS) == set(S.FURNITURE_TYPES)
    names = [g.name for g in D.GROUPS]
    assert names[:len(S.FURNITURE_TYPES)] == list(S.FURNITURE_TYPES)
    assert names[len(S.FURNITURE_TYPES):] == ["door", "window", "lamp", "picture_frame", "rug", "vase", "cushion",
                                              "mirror", "television"]
    texts, owners = D.query_texts()
    assert len(texts) == len(set(texts)) == len(D.GROUPS)
    assert all(t == t.lower() and "_" not in t and len(t.split()) <= 3 for t in texts)      # plain words
    assert owners == names


def test_the_mirrored_class_rules_equal_the_vision_check():
    assert D.FURNITURE_TYPES == S.FURNITURE_TYPES
    assert D.NON_DECOR_CLASSES == S.NON_DECOR_CLASSES and D.LAMP_FIXTURE_MAX_Y1 == S.LAMP_FIXTURE_MAX_Y1
    for y1 in (100, 400, 401, 900):
        box = [400, 10, 450, y1]
        assert D.box_class("lamp", box, (1000, 1000)) == S.category_class("lamp", box)
    for g in D.GROUPS:
        if g.name in S.CATEGORIES and g.cls != D.LAMP:
            assert g.cls == S.category_class(g.name), g.name                      # potted_plant decor in both


def test_group_classes_follow_the_vision_check():
    cls = {g.name: g.cls for g in D.GROUPS}
    assert cls["sofa"] == cls["stair"] == cls["side_table"] == cls["floor_lamp"] == "furniture"
    # potted plant, picture frame, rug, vase, cushion, mirror, television: decor (never a rejection, as today)
    for name in ("potted_plant", "picture_frame", "rug", "vase", "cushion", "mirror", "television"):
        assert cls[name] == "decor", name
    assert (cls["door"], cls["window"]) == ("door", "window")
    assert D.box_class("lamp", [400, 10, 450, 120], (1000, 1000)) == "fixture"       # hangs high
    assert D.box_class("lamp", [400, 500, 450, 900], (1000, 1000)) == "furniture"    # stands
    assert D.box_class("lamp", [40, 1, 45, 12], (100, 100)) == "fixture"             # in pixels of the image
    assert D.box_class("bogus", [0, 0, 1, 1], (10, 10)) is None
    assert not D.non_decor("decor") and D.non_decor("fixture") and D.non_decor("window")


# --------------------------------------------------------------------------
# Raw outputs -> boxes
# --------------------------------------------------------------------------

def test_boxes_from_raw_scale_by_the_padded_square_threshold_and_nms():
    texts, owners = D.query_texts()
    q_sofa, q_chair, q_lamp = texts.index("sofa"), texts.index("chair"), texts.index("lamp")
    logits = np.full((5, len(texts)), -9.0)
    pred = np.zeros((5, 4))
    # A 1920 x 1080 image given to the model as 960 x 540 (padded to 960 x 960): relative to the square.
    logits[0, q_sofa] = logit(0.8)
    pred[0] = (0.5, 0.25, 0.25, 0.125)                        # centre (480, 240) of 960: (960, 480) of 1920
    logits[1, q_sofa] = logit(0.6)
    pred[1] = (0.505, 0.25, 0.25, 0.125)                      # the same sofa again: suppressed by the NMS
    logits[2, q_chair] = logit(0.04)                          # below the record floor
    pred[2] = (0.2, 0.2, 0.1, 0.1)
    logits[3, q_lamp] = logit(0.3)
    pred[3] = (0.95, 0.05, 0.2, 0.2)                          # partly outside: clipped
    logits[4, q_sofa] = logit(0.5)
    logits[4, q_chair] = logit(0.45)                          # one patch, two groups: both recorded
    pred[4] = (0.1, 0.4, 0.1, 0.1)
    boxes = D.boxes_from_raw(logits, pred, (1920, 1080), owners, texts, model_size=(960, 540))
    by = {(b["group"], round(b["score"], 2)): b for b in boxes}
    assert set(by) == {("sofa", 0.8), ("sofa", 0.5), ("chair", 0.45), ("lamp", 0.3)}
    assert by[("sofa", 0.8)]["box_px"] == [720.0, 360.0, 1200.0, 600.0] and by[("sofa", 0.8)]["text"] == "sofa"
    assert by[("lamp", 0.3)]["box_px"] == [1632.0, 0.0, 1920.0, 288.0]
    assert by[("lamp", 0.3)]["class"] == "fixture" and by[("sofa", 0.8)]["class"] == "furniture"
    assert [b["group"] for b in boxes] == ["sofa", "sofa", "chair", "lamp"]           # group order, then score
    with pytest.raises(ValueError):
        D.boxes_from_raw(logits[:, :3], pred, (10, 10), owners)
    with pytest.raises(ValueError):
        D.boxes_from_raw(logits, pred[:3], (10, 10), owners)


def test_fake_detector_round_trips_through_detect_rgb():
    rgb = np.zeros((90, 160, 3), np.uint8)
    rgb[:, :80] = 120
    det = FakeDetector()
    det.register(rgb, [("sofa", 0.7, [10, 40, 70, 80]), ("window", 0.9, [100, 10, 140, 50])])
    found = D.detect_rgb(det, rgb)
    assert found["size"] == [160, 90] and found["model_size"] == [960, 540]
    boxes = {b["group"]: b for b in found["boxes"]}
    assert boxes["sofa"]["box_px"] == pytest.approx([10, 40, 70, 80], abs=0.1)
    assert boxes["window"]["box_px"] == pytest.approx([100, 10, 140, 50], abs=0.1)
    assert boxes["sofa"]["score"] == pytest.approx(0.7, abs=1e-3)
    assert D.model_image(np.zeros((540, 960, 3), np.uint8)).shape == (540, 960, 3)     # already 960: unchanged


# --------------------------------------------------------------------------
# The decision on canned boxes
# --------------------------------------------------------------------------

def index_with(boxes: dict, size=(1000, 1000)) -> np.ndarray:
    idx = np.zeros((size[1], size[0]), np.uint16)
    for pi, (x0, y0, x1, y1) in boxes.items():
        idx[y0:y1, x0:x1] = pi
    return idx


TABLE = {1: {"wenart_id": "f_sofa", "kind": "furniture", "type": "sofa", "host_decor": ["cushion"]},
         2: {"wenart_id": "f_table", "kind": "furniture", "type": "table_dining", "host_decor": []},
         3: {"wenart_id": "w_1", "kind": "window", "type": "window", "host_decor": []},
         4: {"wenart_id": "f_unk", "kind": "furniture", "type": "unknown", "status": "unverified", "host_decor": []},
         5: {"wenart_id": "dec_plant", "kind": "decor", "type": "plant", "host_decor": []}}
INDEX = index_with({1: (100, 500, 400, 800), 2: (500, 500, 800, 700), 3: (600, 100, 800, 300),
                    4: (850, 600, 950, 800), 5: (50, 850, 100, 950)})


def test_added_candidates_cycles_match_and_compatible_cover():
    cycles = [bx("sofa", 0.6, (100, 500, 400, 800)), bx("window", 0.2, (600, 100, 800, 300))]
    polished = [
        bx("sofa", 0.9, (110, 510, 390, 790)),          # matched on Cycles (same group, IoU high)
        bx("armchair", 0.8, (100, 500, 400, 800)),      # no armchair box on Cycles, but on the drawn sofa: covered
        bx("chair", 0.7, (480, 480, 620, 720)),         # next to the table: a table does not host chairs -> added
        bx("lamp", 0.5, (420, 520, 470, 900)),          # on bare floor -> added (furniture)
        bx("window", 0.4, (300, 100, 450, 300)),        # a second window where the wall was -> added
        bx("potted_plant", 0.9, (40, 840, 110, 960)),   # on the drawn plant: covered
        bx("sofa", 0.3, (850, 600, 950, 800)),          # on the unverified proxy: any furniture fits it
        bx("vase", 0.2, (900, 50, 950, 120)),           # decor, added (listed, never a rejection)
        bx("cushion", 0.6, (150, 520, 250, 600)),       # on the sofa (hosts cushions): covered
        bx("chair", 0.04, (0, 0, 50, 50)),              # below t_det
    ]
    got = D.added_candidates(polished, cycles, 0.1, INDEX, TABLE)
    assert [(c["group"], c["score"]) for c in got] == [("chair", 0.7), ("lamp", 0.5), ("window", 0.4), ("vase", 0.2)]
    chair = got[0]
    assert chair["cycles_iou"] == 0.0 and chair["covered"] == 0.0                # the table is not compatible
    # A Cycles chair at IoU >= 0.3 (even a weak one): it was there before the polish.
    got = D.added_candidates(polished, cycles + [bx("chair", 0.06, (490, 490, 610, 710))], 0.1, INDEX, TABLE)
    assert "chair" not in [c["group"] for c in got]
    # The same chair box but the Cycles one at IoU < 0.3: still added.
    got = D.added_candidates(polished, cycles + [bx("chair", 0.9, (560, 600, 700, 760))], 0.1, INDEX, TABLE)
    assert "chair" in [c["group"] for c in got]
    # Without a map nothing is covered; the threshold decides who is a candidate.
    assert len(D.added_candidates(polished, cycles, 0.65, None, None)) == 3
    # An insertion target is left out of the coverage.
    assert [c["group"] for c in D.added_candidates([bx("sofa", 0.9, (100, 500, 400, 800))], [], 0.1, INDEX, TABLE,
                                                   exclude_ids=["f_sofa"])] == ["sofa"]


def test_element_matches_and_cover():
    assert D.element_matches("chair", TABLE[1]) and D.element_matches("bed_double", {"kind": "furniture",
                                                                                     "type": "bed_single"})
    assert not D.element_matches("chair", TABLE[2]) and not D.element_matches("window", TABLE[1])
    assert D.element_matches("window", TABLE[3]) and D.element_matches("door", {"kind": "door", "type": "x"})
    assert D.element_matches("lamp", {"kind": "furniture", "type": "floor_lamp"})
    assert D.element_matches("potted_plant", TABLE[5]) and D.element_matches("cushion", TABLE[1])
    assert not D.element_matches("rug", TABLE[1]) and not D.element_matches("nope", TABLE[1])
    assert D.compatible_cover([100, 500, 400, 800], "sofa", INDEX, TABLE) == 1.0
    assert D.compatible_cover([100, 500, 400, 800], "sofa", INDEX, TABLE, ["f_sofa"]) == 0.0
    assert D.compatible_cover([0, 0, 0, 0], "sofa", INDEX, TABLE) == 0.0


def test_confirm_by_score_or_a_vlm_extra_of_either_pass():
    cands = [bx("lamp", 0.5, (420, 520, 470, 900)), bx("chair", 0.25, (480, 480, 620, 720))]
    extras = [{"class": "decor", "box_px": [482, 470, 618, 730], "passes": ["glm"], "confirmed": False},
              {"class": "furniture", "box_px": [0, 0, 10, 10], "passes": ["qwen", "glm"], "confirmed": True},
              {"class": "furniture", "box_px": [420, 520, 470, 900], "passes": ["qwen"], "unreliable": True}]
    got = D.confirm(cands, 0.45, extras)
    assert (got[0]["confirmed"], got[0]["confirmed_by"]) == (True, ["score"])          # unreliable pass ignored
    assert (got[1]["confirmed"], got[1]["confirmed_by"]) == (True, ["vlm:glm"])        # any class, one pass
    got = D.confirm(cands, 0.6, extras[1:])
    assert [c["confirmed"] for c in got] == [False, False]
    assert D.confirm(cands, None, [])[0]["confirmed"] is False


def test_target_hit_needs_half_of_the_target_box():
    cands = [bx("sofa", 0.4, (100, 500, 260, 800)), bx("armchair", 0.7, (100, 500, 240, 800))]
    assert D.target_hit(cands, [100, 500, 400, 800])["group"] == "sofa"           # 160/300 >= 50 %, 140/300 not
    assert D.target_hit(cands, [600, 100, 800, 300]) is None


def test_committed_detector_block_equals_the_calibration():
    """The integrator copies ``check_yaml_block`` of the prep pod's calibration into check.yaml (M7 §8.1); the
    committed block must equal the committed calibration, so the thresholds are measured, never typed in."""
    import json
    from wenart.vision_check.config import load_config
    cfg = load_config()["detector"]
    calib = json.loads((ROOT / "results" / "detect" / "detector_calibration.json").read_text(encoding="utf-8"))
    assert calib["usable"] is True and calib["targets_met"] is True
    assert cfg["advisory"] is False and cfg["t_det"] == calib["t_det"] and cfg["t_strong"] == calib["t_strong"]
    for key, value in cfg["calibration"].items():
        if key in calib["rates"]:
            assert value == calib["rates"][key]


def test_detector_block_without_thresholds_is_advisory():
    assert D.detector_cfg(ADVISORY_BLOCK_CFG) is None
    assert D.detector_cfg({}) is None and D.detector_cfg({"detector": None}) is None
    assert D.detector_cfg({"detector": {"t_det": None, "t_strong": None}}) is None
    assert D.detector_cfg({"detector": {"t_det": 0.2, "t_strong": 0.4, "advisory": True}}) is None
    got = D.detector_cfg({"detector": {"t_det": 0.2, "t_strong": 0.4, "calibration": {"x": 1}}})
    assert got == {"t_det": 0.2, "t_strong": 0.4, "match_iou": 0.3, "cover_frac": 0.5, "confirm_iou": 0.3,
                   "calibration": {"x": 1}}
    for bad in ({"t_det": 0.5, "t_strong": 0.4}, {"t_det": 0.2}, {"t_det": "x", "t_strong": 0.3},
                {"t_det": 0.0, "t_strong": 0.3}, [1, 2]):
        with pytest.raises(ValueError):
            D.detector_cfg({"detector": bad})


# --------------------------------------------------------------------------
# Calibration maths and perturbations
# --------------------------------------------------------------------------

def test_calibration_maths_picks_the_lowest_safe_thresholds():
    hits = [0.9, 0.8, 0.7, 0.6, 0.5, 0.45, 0.3, None, 0.2, 0.75]           # 10 positives
    falses = [None] * 90 + [0.12] * 6 + [0.25, 0.25, 0.35, 0.5]            # 100 negatives
    r = D.calibrate_scores(hits, falses)
    # false share: 0.10 up to t 0.12, 0.04 up to 0.25, 0.02 above: t_det 0.05 (<= 10 %), t_strong 0.26 (<= 3 %)
    assert (r["t_det"], r["t_strong"]) == (0.05, 0.26)
    assert r["rates"] == {"insertion_confirmed": 0.8, "false_confirmed": 0.02, "insertion_flagged": 0.9,
                          "false_flagged": 0.1}
    assert r["targets_met"] and r["usable"] and r["positives"] == 10 and r["negatives"] == 100
    row = next(g for g in r["grid"] if g["t"] == 0.5)
    assert row == {"t": 0.5, "insertion": 0.6, "false": 0.01}
    # Too few insertions at the safe threshold: proposed, but not usable (the detector stays advisory).
    weak = D.calibrate_scores([0.2, 0.1, None, 0.3], falses)
    assert weak["t_strong"] == 0.26 and weak["rates"]["insertion_confirmed"] == 0.25 and not weak["usable"]
    assert "stays advisory" in weak["note"]
    # Every negative flagged at every score: nothing safe.
    none = D.calibrate_scores([0.9], [0.99, 0.99])
    assert none["t_strong"] is None and not none["usable"]
    assert D.calibrate_scores([], [0.1])["note"] == "no positives"
    assert D.calibrate_scores([0.5], [])["note"] == "no negatives"
    assert D.rates_at(0.5, [], []) == {"t": 0.5, "insertion": None, "false": None}


def test_perturbations_are_benign_and_deterministic():
    yy, xx = np.mgrid[0:40, 0:60]
    rgb = np.stack([xx * 4, yy * 5, (xx + yy) * 2], axis=2).astype(np.uint8)        # a smooth render-like image
    for kind in D.PERTURBATIONS:
        a, b = D.perturb(rgb, kind), D.perturb(rgb, kind)
        assert np.array_equal(a, b) and a.shape == rgb.shape and a.dtype == np.uint8
        assert not np.array_equal(a, rgb) and np.abs(a.astype(int) - rgb).mean() < 4
    assert np.array_equal(D.perturb(rgb, None), rgb)
    with pytest.raises(ValueError):
        D.perturb(rgb, "sharpen")


def test_pair_scores_positive_and_negative():
    pos = {"kind": "positive", "target_box_px": [100, 500, 400, 800], "exclude_ids": ["f_sofa"]}
    got = D.pair_scores(pos, [], [bx("sofa", 0.6, (100, 500, 400, 800))], INDEX, TABLE)
    assert got["hit"] == 0.6 and got["hit_group"] == "sofa"
    neg = {"kind": "negative"}
    got = D.pair_scores(neg, [], [bx("vase", 0.9, (900, 50, 950, 120)), bx("lamp", 0.3, (420, 520, 470, 900))],
                        INDEX, TABLE)
    assert got["false"] == 0.3 and got["false_group"] == "lamp"                       # decor never counts
    assert D.pair_scores(neg, [], [], INDEX, TABLE)["false"] is None


def test_a_decor_box_on_the_target_is_not_an_insertion_hit():
    """Review vision-1: combine rejects only on confirmed NON-DECOR boxes, so a picture frame or mirror box over an
    inserted window must not count as "insertion found" in the calibration (the positives, like the negatives,
    count only non-decor boxes)."""
    target = [100, 100, 300, 400]
    frame = bx("picture_frame", 0.90, (95, 95, 305, 405))
    window = bx("window", 0.20, (100, 100, 300, 400))
    assert frame["class"] == "decor" and window["class"] == "window"
    assert D.target_hit([frame, window], target)["group"] == "window"
    assert D.target_hit([frame, bx("mirror", 0.8, (100, 100, 300, 400))], target) is None
    pos = {"kind": "positive", "target_box_px": target, "exclude_ids": ["w1"]}
    got = D.pair_scores(pos, [], [frame, window])
    assert (got["hit"], got["hit_group"]) == (0.2, "window")
    assert D.rates_at(0.5, [got["hit"]], [None])["insertion"] == 0.0           # not confirmed at t_strong 0.5
    got = D.pair_scores(pos, [], [frame])
    assert got["hit"] is None and got["hit_group"] is None


# --------------------------------------------------------------------------
# run_detect and the CLI on the toy project
# --------------------------------------------------------------------------

def free_box(out: Path, size=14) -> list:
    """A box of bare structure (index 0) in the toy render, away from every element."""
    idx = V.read_index(out / "renders" / f"{CAM}_index.png")
    H, W = idx.shape
    for y in range(H - size, 0, -2):
        for x in range(0, W - size, 2):
            if not idx[y:y + size, x:x + size].any():
                return [x, y, x + size, y + size]
    raise AssertionError("no free box")


def element_box(out: Path, wid: str) -> list:
    exp = Project(out).expected(CAM)
    return next(e["box_px"] for e in exp["elements"] if e["wenart_id"] == wid)


def toy(tmp_path, controls=("f_sofa",)):
    out = T.write_toy_project(tmp_path, polished=True)
    assert check_main(["expected", "--project-out", str(out)]) == 0
    sel = {"schema_version": "0.1", "dir_relative_to": "project_out", "swaps": [],
           "controls": [{"id": c, "index": 3, "kind": "furniture", "type": "sofa", "camera": CAM, "room_id": "r_salon",
                         "plug": False, "area_frac": 0.1, "source": "from_documents", "dir": f"controls/hide_{c}"}
                        for c in controls]}
    (out / "check" / "controls.json").write_text(json.dumps(sel), encoding="utf-8")
    for c in controls:
        T.write_control(out, c)
    return out


def register_toy(det: FakeDetector, out: Path, polished_extra=(), cycles_extra=()):
    sofa = element_box(out, "f_sofa")
    cyc = V.read_rgb(out / "renders" / f"{CAM}.png")
    pol = V.read_rgb(out / "polish" / f"{CAM}_a1.png")
    det.register(cyc, [("sofa", 0.8, sofa)] + list(cycles_extra))
    det.register(pol, [("sofa", 0.85, sofa)] + list(polished_extra))
    hidden = out / "controls" / "hide_f_sofa" / f"{CAM}.png"
    if hidden.is_file():
        det.register(V.read_rgb(hidden), [])
    return sofa


def test_run_detect_writes_reuses_and_skips(tmp_path, capsys):
    out = toy(tmp_path)
    det = FakeDetector()
    lamp = free_box(out)
    register_toy(det, out, polished_extra=[("lamp", 0.6, lamp)])
    manifest = out / "polish" / "polish_manifest.json"
    assert gate_main(["detect", str(out), "--manifest", str(manifest), "--out", str(out / "detect")],
                     detector=det) == 0
    assert det.calls == 3                                           # Cycles, polished, the hidden render
    doc = json.loads((out / "detect" / f"{CAM}.json").read_text())
    assert doc["kind"] == "detect_view" and doc["model"]["revision"] == REV
    assert set(doc["images"]) == {"cycles", "polished"} and set(doc["controls"]) == {"f_sofa"}
    assert doc["images"]["polished"]["k"] == 1 and doc["controls"]["f_sofa"]["target"] == "f_sofa"
    pol = doc["images"]["polished"]
    assert pol["sha256"] == D.sha256_file(out / "polish" / f"{CAM}_a1.png") and pol["file"] == f"../polish/{CAM}_a1.png"
    assert {b["group"] for b in pol["boxes"]} == {"sofa", "lamp"}
    assert doc["queries"]["potted_plant"]["class"] == "decor" and doc["settings"]["image_long_side"] == 960
    man = json.loads((out / "detect" / "detect_manifest.json").read_text())
    assert man["views"][CAM]["status"] == "ok" and man["detected_images"] == 3 and not man["incomplete"]
    # A second run reuses every image (same detection key); --force detects again.
    assert gate_main(["detect", str(out), "--out", str(out / "detect")], detector=det) == 0
    assert det.calls == 3 and json.loads((out / "detect" / "detect_manifest.json").read_text())["reused_images"] == 3
    assert gate_main(["detect", str(out), "--force", "--no-controls"], detector=det) == 0
    assert det.calls == 5
    # A deadline in the past: nothing detected, the manifest says incomplete.
    assert gate_main(["detect", str(out), "--force", "--deadline", "1"], detector=det) == 0
    assert det.calls == 5 and json.loads((out / "detect" / "detect_manifest.json").read_text())["incomplete"]
    # No polish manifest: exit 1. A polish that was not allowed: skipped, exit 0.
    assert gate_main(["detect", str(out), "--manifest", str(tmp_path / "none.json")], detector=det) == 1
    pm = json.loads(manifest.read_text())
    pm["polish_allowed"] = False
    manifest.write_text(json.dumps(pm))
    assert gate_main(["detect", str(out), "--out", str(tmp_path / "d2")], detector=det) == 0
    assert "gate not validated" in json.loads((tmp_path / "d2" / "detect_manifest.json").read_text())["skipped"]
    # A polish made from another Cycles render is not detected.
    pm["polish_allowed"] = True
    pm["views"][0]["source_sha256"] = "0" * 64
    manifest.write_text(json.dumps(pm))
    doc = D.run_detect(out, manifest, tmp_path / "d3", det, controls=False, log=lambda *_: None)
    assert doc["views"][CAM]["status"] == "skipped" and any("another Cycles render" in w for w in doc["warnings"])


def test_a_deadline_inside_a_camera_keeps_the_records_not_reached(tmp_path):
    out = toy(tmp_path)
    det = FakeDetector()
    register_toy(det, out)
    manifest = out / "polish" / "polish_manifest.json"
    D.run_detect(out, manifest, out / "detect", det, log=lambda *_: None)
    before = json.loads((out / "detect" / f"{CAM}.json").read_text())
    rgb = V.read_rgb(out / "polish" / f"{CAM}_a1.png")              # a new polish: needs a new detection
    V.write_png_rgb(out / "polish" / f"{CAM}_a1.png", np.clip(rgb.astype(int) + 2, 0, 255).astype(np.uint8))
    times = iter([0.0, 0.0, 100.0, 100.0, 100.0, 100.0])              # start, Cycles (reused), then past the deadline
    calls = det.calls
    doc = D.run_detect(out, manifest, out / "detect", det, deadline=50.0, clock=lambda: next(times),
                       log=lambda *_: None)
    after = json.loads((out / "detect" / f"{CAM}.json").read_text())
    assert doc["incomplete"] and det.calls == calls
    assert after["images"]["polished"] == before["images"]["polished"]           # kept, now stale by its sha256
    assert after["controls"] == before["controls"]
    assert D.image_boxes(after, "polished", D.sha256_file(out / "polish" / f"{CAM}_a1.png")) is None


def test_detect_calibrate_cli_builds_pairs_and_writes_the_calibration(tmp_path, capsys):
    out = toy(tmp_path)
    det = FakeDetector()
    sofa = register_toy(det, out)
    # The hide render lacks the sofa; the normal render shows it: the detector finds it as added.
    for kind in D.PERTURBATIONS:
        det.register(D.perturb(V.read_rgb(out / "renders" / f"{CAM}.png"), kind), [("sofa", 0.8, sofa)])
    dest = tmp_path / "results" / "detect"
    assert gate_main(["detect-calibrate", "--project-outs", str(out), "--out", str(dest), "--pairs-only"],
                     detector=det) == 0
    pairs = json.loads((dest / "detect_pairs.json").read_text())
    assert pairs["counts"] == {"insertion_control": 1, "accepted_polish": 1, "perturbation": 3}
    pos = next(p for p in pairs["pairs"] if p["kind"] == "positive")
    assert pos["target"] == "f_sofa" and pos["exclude_ids"] == ["f_sofa"] and pos["cycles"].endswith(
        f"hide_f_sofa/{CAM}.png") and pos["target_box_px"] == sofa
    assert det.calls == 0
    assert gate_main(["detect-calibrate", "--pairs", str(dest / "detect_pairs.json"), "--out", str(dest)],
                     detector=det) == 0
    cal = json.loads((dest / "detector_calibration.json").read_text())
    assert cal["kind"] == "detector_calibration" and cal["positives"] == 1 and cal["negatives"] == 4
    assert cal["t_strong"] == 0.05 and cal["rates"]["insertion_confirmed"] == 1.0 and cal["usable"]
    assert cal["check_yaml_block"]["t_strong"] == 0.05 and cal["check_yaml_block"]["advisory"] is False
    assert D.detector_cfg({"detector": cal["check_yaml_block"]})["t_det"] == 0.05
    hit = next(r for r in cal["per_pair"] if r["kind"] == "positive")
    assert hit["hit"] == pytest.approx(0.8, abs=1e-3) and hit["hit_group"] == "sofa"
    calls = det.calls
    assert gate_main(["detect-calibrate", "--pairs", str(dest / "detect_pairs.json"), "--out", str(dest)],
                     detector=det) == 0
    assert det.calls == calls                                      # every image from the box cache
    empty = tmp_path / "empty.json"
    empty.write_text(json.dumps({"pairs": []}))
    assert gate_main(["detect-calibrate", "--pairs", str(empty), "--out", str(dest)], detector=det) == 1


# --------------------------------------------------------------------------
# combine with the detector
# --------------------------------------------------------------------------

CALIBRATED = {"advisory": False, "t_det": 0.3, "t_strong": 0.7}


def check_flow(out: Path, extras=None, cfg_detector=None):
    """Both fake models see every toy element on both images (plus ``extras``), then combine (answers asked anew)."""
    for old in (out / "check").glob("answers_*.json"):
        old.unlink()
    truth = {f"renders/{CAM}.png": set(T.TOY_TYPES), f"polish/{CAM}_a1.png": set(T.TOY_TYPES),
             f"hide_f_sofa/{CAM}.png": set(T.TOY_TYPES) - {"sofa"}}
    for key in ("qwen", "glm"):
        client = T.FakeClient(model=f"fake/{key}", truth=truth, extras=(extras or {}).get(key))
        assert check_main(["run", "--project-out", str(out), "--model-key", key, "--kinds", "cycles,polished,controls"],
                          client_factory=lambda k, u, c=client: c) == 0
    project = Project(out)
    if cfg_detector is not None:
        project.cfg = dict(project.cfg, detector=cfg_detector)
    return CB.combine_project(project, ["qwen", "glm"])


def norm_box(box, size=T.SIZE):
    W, H = size
    return [round(box[0] * 1000 / W), round(box[1] * 1000 / H), round(box[2] * 1000 / W), round(box[3] * 1000 / H)]


def test_combine_rejects_a_confirmed_added_object_and_records_the_insertion_control(tmp_path):
    out = toy(tmp_path / "a")
    det = FakeDetector()
    lamp = free_box(out)
    register_toy(det, out, polished_extra=[("lamp", 0.8, lamp)])
    assert gate_main(["detect", str(out)], detector=det) == 0
    m = check_flow(out, cfg_detector=CALIBRATED)
    view = m["views"][CAM]
    assert view["polished_rejected"] and view["polished_reason"] == "vision_check" and view["added_by_polish"]
    r = next(r for r in view["polished_reasons"] if r.get("source") == "detector")
    assert r["what"] == "added_by_polish" and r["class"] == "furniture" and r["confirmed_by"] == ["score"]
    assert r["box_px"] == pytest.approx(lamp, abs=0.2)
    assert view["detector"]["status"] == "calibrated" and len(view["detector"]["added"]) == 1
    assert m["detector"]["status"] == "calibrated" and m["detector"]["views"] == [CAM]
    # The insertion control seen by the detector: the sofa is found where the hide render had none.
    dc = view["insertion:f_sofa"]["detector_control"]
    assert dc["computed"] and dc["hit_group"] == "sofa" and dc["flagged"] and dc["confirmed"]
    from wenart.vision_check.calibrate import calibrate
    cal = calibrate(m, Project(out).cfg)
    assert cal["metrics"]["detector_insertion"]["n"] == 1 and cal["metrics"]["detector_insertion"]["confirmed"] == 1.0
    # The report names the detector.
    from wenart.vision_check.report import check_report
    text = check_report(m, cal)
    assert "## Added-object detector" in text and "Calibrated: t_det 0.3" in text and "detector: lamp" in text
    # Advisory (the pre-calibration check.yaml block): listed, never rejected.
    m = check_flow(out, cfg_detector=ADVISORY)
    view = m["views"][CAM]
    assert not view["polished_rejected"] and not view["added_by_polish"]
    assert view["detector"]["status"] == "advisory" and view["detector"]["unmatched"][0]["group"] == "lamp"
    assert m["detector"]["advisory"] and "insertion:f_sofa" in view
    dc = view["insertion:f_sofa"]["detector_control"]
    assert dc["advisory"] and dc["hit_group"] == "sofa" and "confirmed" not in dc
    assert "Advisory" in check_report(m, None)


def test_a_weak_box_needs_a_vlm_extra_and_a_single_pass_extra_needs_a_box(tmp_path):
    out = toy(tmp_path)
    det = FakeDetector()
    lamp = free_box(out)
    register_toy(det, out, polished_extra=[("lamp", 0.4, lamp)])           # >= t_det 0.3, < t_strong 0.7
    assert gate_main(["detect", str(out)], detector=det) == 0
    m = check_flow(out, cfg_detector=CALIBRATED)
    view = m["views"][CAM]
    assert not view["polished_rejected"] and view["detector"]["added"] == []
    assert view["detector"]["candidates"][0]["confirmed"] is False
    # One VLM pass reports a lamp there: the extra is confirmed by the detector box, the box by the extra.
    extra = {"category": "lamp", "box": norm_box(lamp), "confidence": 0.7}
    m = check_flow(out, extras={"glm": {f"polish/{CAM}_a1.png": [extra]}}, cfg_detector=CALIBRATED)
    view = m["views"][CAM]
    x = next(x for x in view["polished"]["extras"] if x["passes"] == ["glm"])
    assert x["confirmed"] and x["confirmed_by"] == "detector" and x["detector"]["group"] == "lamp"
    assert view["polished"]["verdict"] == "mismatch" and view["polished_rejected"] and view["added_by_polish"]
    reasons = [r for r in view["polished_reasons"] if r.get("what") == "added_by_polish"]
    assert len(reasons) == 1 and reasons[0].get("detector")                 # one object, one reason (VLM + box)
    # Advisory: the single-pass extra stays unconfirmed.
    m = check_flow(out, extras={"glm": {f"polish/{CAM}_a1.png": [extra]}}, cfg_detector=ADVISORY)
    x = next(x for x in m["views"][CAM]["polished"]["extras"] if x["passes"] == ["glm"])
    assert not x["confirmed"] and not m["views"][CAM]["polished_rejected"]


def test_an_added_plant_never_rejects_and_a_lamp_already_on_cycles_is_not_added(tmp_path):
    out = toy(tmp_path / "p")
    det = FakeDetector()
    spot = free_box(out)
    register_toy(det, out, polished_extra=[("potted plant", 0.95, spot)])
    assert gate_main(["detect", str(out)], detector=det) == 0
    m = check_flow(out, cfg_detector=CALIBRATED)
    view = m["views"][CAM]
    assert not view["polished_rejected"] and view["detector"]["added"] == []
    assert view["detector"]["candidates"][0]["class"] == "decor" and view["detector"]["candidates"][0]["confirmed"]
    out = toy(tmp_path / "l")
    det = FakeDetector()
    spot = free_box(out)
    register_toy(det, out, polished_extra=[("lamp", 0.95, spot)], cycles_extra=[("lamp", 0.1, spot)])
    assert gate_main(["detect", str(out)], detector=det) == 0
    assert not check_flow(out, cfg_detector=CALIBRATED)["views"][CAM]["polished_rejected"]


def test_the_insertion_control_counts_no_decor_box_on_the_target(tmp_path):
    """Review vision-1 in combine.detector_control: a strong "picture frame" box over the shown sofa (the hidden
    render has nothing) is not the control's hit; the weak sofa box is, and it is neither flagged nor confirmed."""
    out = toy(tmp_path)
    det = FakeDetector()
    sofa = element_box(out, "f_sofa")
    det.register(V.read_rgb(out / "renders" / f"{CAM}.png"), [("sofa", 0.2, sofa), ("picture frame", 0.95, sofa)])
    det.register(V.read_rgb(out / "polish" / f"{CAM}_a1.png"), [("sofa", 0.2, sofa), ("picture frame", 0.95, sofa)])
    det.register(V.read_rgb(out / "controls" / "hide_f_sofa" / f"{CAM}.png"), [])
    assert gate_main(["detect", str(out)], detector=det) == 0
    m = check_flow(out, cfg_detector=CALIBRATED)
    dc = m["views"][CAM]["insertion:f_sofa"]["detector_control"]
    assert dc["computed"] and dc["hit_group"] == "sofa" and dc["hit_score"] == pytest.approx(0.2, abs=1e-3)
    assert dc["flagged"] is False and dc["confirmed"] is False
    from wenart.vision_check.calibrate import calibrate
    cal = calibrate(m, Project(out).cfg)
    assert cal["metrics"]["detector_insertion"]["confirmed"] == 0.0


def test_a_calibrated_detector_without_a_current_detection_is_check_incomplete(tmp_path):
    out = toy(tmp_path)
    det = FakeDetector()
    register_toy(det, out)
    m = check_flow(out, cfg_detector=CALIBRATED)                 # never detected
    view = m["views"][CAM]
    assert view["polished_rejected"] and view["polished_reason"] == "check_incomplete" and not view["added_by_polish"]
    assert any("detector: no current detection" in r["detail"] for r in view["polished_reasons"])
    assert m["detector"]["not_computed"] == [CAM]
    # Detected, then the polished image changes: the detection is stale and not used.
    assert gate_main(["detect", str(out)], detector=det) == 0
    assert not check_flow(out, cfg_detector=CALIBRATED)["views"][CAM]["polished_rejected"]
    rgb = V.read_rgb(out / "polish" / f"{CAM}_a1.png")
    V.write_png_rgb(out / "polish" / f"{CAM}_a1.png", np.clip(rgb.astype(int) + 3, 0, 255).astype(np.uint8))
    m = check_flow(out, cfg_detector=CALIBRATED)
    assert m["views"][CAM]["polished_reason"] == "check_incomplete"
    assert any("made from another image" in w for w in m["warnings"])
    # Advisory and never run: no detector record at all.
    out2 = toy(tmp_path / "none")
    m = check_flow(out2, cfg_detector=ADVISORY)
    assert "detector" not in m["views"][CAM] and m["detector"]["status"] == "not_run"
    assert not m["views"][CAM]["polished_rejected"]


def test_combine_extras_with_detector_candidates_unit():
    cfg = {"extras": {"match_iou": 0.3, "covered_frac": 0.5}}
    per_pass = {"qwen": [{"category": "lamp", "class": "furniture", "box_1000": [0, 0, 1, 1],
                          "box_px": [420, 520, 470, 900], "confidence": 0.8, "covered": 0.0},
                         {"category": "plant", "class": "decor", "box_1000": [0, 0, 1, 1],
                          "box_px": [40, 840, 110, 960], "confidence": 0.8, "covered": 0.0}],
                "glm": []}
    cands = [bx("lamp", 0.35, (420, 520, 470, 900)), bx("vase", 0.4, (40, 840, 110, 960))]
    got = CB.combine_extras(copy.deepcopy(per_pass), ["qwen", "glm"], ["qwen", "glm"], False, cfg, cands)
    lamp, plant = got
    assert lamp["confirmed"] and lamp["confirmed_by"] == "detector" and not lamp["info"]
    assert plant["confirmed"] and plant["info"]                      # decor with decor: confirmed, info only
    # Family mismatch (a decor box under a furniture extra), an unreliable pass, single-pass mode: not confirmed.
    got = CB.combine_extras(copy.deepcopy(per_pass), ["qwen", "glm"], ["qwen", "glm"], False, cfg,
                            [bx("vase", 0.4, (420, 520, 470, 900))])
    assert not got[0]["confirmed"]
    got = CB.combine_extras(copy.deepcopy(per_pass), ["qwen", "glm"], ["glm"], False, cfg, cands)
    assert not any(x["confirmed"] for x in got)
    got = CB.combine_extras(copy.deepcopy(per_pass), ["qwen"], ["qwen"], True, cfg, cands)
    assert not any(x["confirmed"] for x in got)
    assert CB.combine_extras(copy.deepcopy(per_pass), ["qwen", "glm"], ["qwen", "glm"], False, cfg) == \
        CB.combine_extras(copy.deepcopy(per_pass), ["qwen", "glm"], ["qwen", "glm"], False, cfg, [])


# --------------------------------------------------------------------------
# models.yaml and the model wrapper (no torch here)
# --------------------------------------------------------------------------

def test_models_yaml_detect_block_and_the_lazy_wrapper():
    from wenart.gate.api import load_models_config
    from wenart.gate.models import Detector
    cfg = load_models_config()
    assert set(cfg["models"]) == {"depth", "sam", "dino"}          # the gate models (and the gate key) unchanged
    det = cfg["detect"]
    assert (det["repo"], det["revision"], det["licence"]) == ("google/owlv2-base-patch16-ensemble", REV, "Apache-2.0")
    assert det["allow_patterns"] == ["*.json", "*.safetensors", "*.txt"]
    d = Detector(device="cpu")
    assert d.info() == {"repo": det["repo"], "revision": REV, "licence": "Apache-2.0"} and d._loaded is None
    with pytest.raises(KeyError):
        Detector(config={"models": {}})
