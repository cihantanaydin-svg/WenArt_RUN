"""Realism A/B with controls (docs/milestone6.md §6; area V).

What: a pairwise, forced-choice comparison of two renders of the same
camera, A (baseline) and B (candidate). Each pair is asked of two vision
models (``check.yaml`` models), in both display orders (``ab``: A is image 1;
``ba``: B is image 1), once per aspect (materials, lighting, furniture,
photo), at temperature 0 and seed 0, with a strict schema and its own system
prompt. Known-direction controls (a degraded render against the normal one)
and null controls (identical files, a JPEG re-encode) show whether a model
can see such differences at all; only then is a decision made.

Why: the M5 preference question allowed a tie, and 90 % of its answers were
"same"; no pair was picked the same way in both orders by both models. A
forced choice in both orders separates a real preference (the same image
picked in both orders) from position bias (the pick follows the position).

How (one CLI subcommand per step, ``wenart/vision_check/cli.py``):

- ``realism-pairs`` (``build_pairs``): reads only files under the project
  output and writes ``ab/pairs.json``: the pair sets of §6.3 (``m5_vs_m6``
  on the cameras ``ab/cameras_check.json`` kept, ``look_alt``, and with
  ``--controls`` the control sets on the 8 ``control_views``), each pair with
  file sizes, sha256 and the measured brightness difference ``delta_ev``
  (log2 of the mean linear luminance ratio B / A of the two JPEGs). It writes
  the ``null_reencode`` A files (PIL, JPEG q70) and copies the ``dropped``
  cameras of ``cameras_check.json``.
- ``realism`` (``realism_specs`` + ``calls.run_specs``): every pair in both
  orders, the sets in the order of §6.2 (controls, then ``m5_vs_m6``, then
  ``look_alt``), into ``check/realism/answers_<slug>.json`` (the M5
  ``AnswerStore`` format; call key ``realism|<set>:<cam>|<order>``; reused by
  ``input_sha256`` = system prompt, prompt, schema, labels, image bytes and
  model id), deadline-aware like ``run``. ``RealismClient`` adds the system
  prompt and the post-validation (repeated cues removed) to every call.
- ``realism-combine`` (``combine``): per pair, model and aspect the outcome
  W (B picked in both orders), L (A in both), T (the pick follows the
  position) or NC (a call failed, is missing or stale: never a tie or a
  loss); the graded score (sum over both orders of +-1/2/3 for
  slight/clear/large, + toward B, -6..+6); the consensus (W only when every
  model says W, L only when every model says L, NC when any is NC, else T);
  per model the order consistency (W+L)/(W+L+T) and the position-bias index
  (share of ``image_1`` picks). Statistics: exact two-sided sign test on
  consensus W vs L; per room the outcome of its non-NC views (W if W > L, L
  if L > W, else T) with a sign test over rooms; a room-cluster bootstrap
  95 % interval of the net win (W - L) / N (2000 resamples, seed 0). For the
  control project also the controls table (``evaluate_controls``). Writes
  ``realism_ab.json``, ``realism_report.md`` and
  ``contact_realism_<set>_<n>.jpg`` (rows A | B | outcomes, <= 300 KB). No
  decision here.
- ``realism-summary`` (``summarise``): pools the A/B sets of every project,
  evaluates the controls of the control project (a model has signal when it
  meets the targets on each of the four ``ctl_*`` sets), forms the
  consensus from the models with signal (``single_model`` when only one has
  it) and writes ``decision`` per set and aspect (``better``, ``worse``,
  ``no_detectable_difference``, ``not_measurable``) into
  ``realism_summary.json`` and ``realism_summary.md``.

Thresholds live in ``check.yaml: realism`` (``realism_cfg``).
"""
from __future__ import annotations

import copy
import hashlib
import io
import json
import math
import random
import re
from collections import Counter
from dataclasses import dataclass
from math import comb
from pathlib import Path
from typing import Iterable, Optional

from wenart import views
from wenart.recognition.vlm_client import schema_errors
from wenart.vision_check import calls as C
from wenart.vision_check import schemas as S
from wenart.vision_check.project import read_json, rel, sha256_file, write_json

# --------------------------------------------------------------------------
# Prompts (§6.1, verbatim; the spec wraps long lines, a paragraph is one line here)
# --------------------------------------------------------------------------

SYSTEM_PROMPT = ("You are a strict interior photographer and 3D artist. You judge whether images look like real "
                 "photographs or like computer renderings. You answer only with JSON that follows the given schema.")

ASPECTS = S.REALISM_ASPECTS
WINNERS = S.REALISM_WINNERS
MARGINS = S.REALISM_MARGINS
CUES = S.REALISM_CUES
OUTCOMES = S.REALISM_OUTCOMES
DECISIONS = S.REALISM_DECISIONS
LABELS = ("Image 1:", "Image 2:")
ORDERS = ("ab", "ba")                  # ab: A is image 1; ba: B is image 1
MARGIN_WEIGHT = {"slight": 1, "clear": 2, "large": 3}
PROMPT_KIND = "realism"

PROMPT = "\n".join([
    "Image 1 and image 2 show the same room from the same camera position. They differ only in how the room was "
    "made into an image: materials, lighting, furniture models, small objects, camera settings.",
    "",
    "Compare them as a professional interior photographer would. For each aspect below, pick the image that looks "
    "more like a real photograph, and say how big the difference is.",
    "",
    "Aspects:",
    "- materials: surfaces look like real materials (wood grain, fabric weave, plaster, tiles, metal) with natural "
    "roughness, sheen and reflections, not flat or plastic colour.",
    "- lighting: light falls off naturally, soft contact shadows where objects touch the floor and walls, plausible "
    "bounce light and window light; no flat, uniform, blown-out or murky light.",
    "- furniture: furniture and objects have real shapes, rounded edges, seams, soft cushions and small details, "
    "not simple boxes.",
    "- photo: the whole image could be a real photograph taken in an existing home.",
    "",
    "Rules:",
    "- You must pick image_1 or image_2 for every aspect. There is no tie. If the two images look almost the same "
    "for an aspect, still pick the better one and set margin to \"slight\".",
    "- margin: slight = you need to look closely; clear = visible at a normal look; large = obvious at first sight.",
    "- cues: up to 3 cues from the list that decided this aspect (empty list if none applies).",
    "- Judge only how real the images look. Do not judge the style, the colour scheme or the layout, and do not "
    "prefer an image because it is shown first or second.",
    "",
    "Cues: " + ", ".join(CUES) + ".",
    "",
    "Answer only with JSON that follows the schema.",
])

# --------------------------------------------------------------------------
# Files and pair sets (§6.2, §6.3)
# --------------------------------------------------------------------------

AB_DIR = Path("ab")
PAIRS_JSON = AB_DIR / "pairs.json"
CAMERAS_CHECK = AB_DIR / "cameras_check.json"
AB_RENDER_MANIFEST = AB_DIR / "renders" / "render_manifest.json"
AB_SCENE_MANIFEST = AB_DIR / "scene" / "scene_manifest.json"
REALISM_DIR = Path("check") / "realism"
REALISM_AB = "realism_ab.json"
REPORT_MD = "realism_report.md"
SUMMARY_JSON = "realism_summary.json"
SUMMARY_MD = "realism_summary.md"
SHEET_PREFIX = "contact_realism_"
NORMAL = "ab/renders/{cam}_preview.jpg"


@dataclass(frozen=True)
class PairSet:
    """One pair set: the A and B files (relative to the project output, ``{cam}`` filled in), what should win."""
    name: str
    a: str
    b: str
    expected: Optional[str]          # "b" | "a" | "tie" | None (no known direction)
    target_aspect: Optional[str]
    control: bool                    # made only with ``realism-pairs --controls`` (the control project)
    text: str


SETS: dict[str, PairSet] = {s.name: s for s in (
    PairSet("ctl_flat", "ab/ctl_flat/renders/{cam}_preview.jpg", NORMAL, "b", "materials", True,
            "A = build --no-textures, B = normal"),
    PairSet("ctl_proxy", "ab/ctl_proxy/renders/{cam}_preview.jpg", NORMAL, "b", "furniture", True,
            "A = build --proxies, B = normal"),
    PairSet("ctl_direct", "ab/ctl_direct/renders/{cam}_preview.jpg", NORMAL, "b", "lighting", True,
            "A = render --max-bounces 0, B = normal"),
    PairSet("ctl_lowspp", "ab/ctl_lowspp/renders/{cam}_preview.jpg", NORMAL, "b", "photo", True,
            "A = render --samples 4 --no-denoise, B = normal"),
    PairSet("null_identical", NORMAL, NORMAL, "tie", None, True, "A and B = the same file"),
    PairSet("null_reencode", "ab/null_reencode/{cam}_reencode.jpg", NORMAL, "tie", None, True,
            "A = the normal preview re-encoded as JPEG q70 (PIL), B = normal"),
    PairSet("nuisance_ev", NORMAL, "ab/nuisance_ev/renders/{cam}_preview.jpg", None, None, True,
            "A = normal, B = render --ev-offset 0.3"),
    PairSet("m5_vs_m6", "ab/m5/{cam}_preview.jpg", NORMAL, None, None, False,
            "A = M5 look (a2adcef), B = M6 look"),
    PairSet("look_alt", NORMAL, "ab/renders/{cam}_alt_preview.jpg", None, None, False,
            "A = default look, B = AgX - Punchy"),
)}
SET_ORDER: tuple[str, ...] = S.REALISM_SETS
CONTROL_SETS = ("ctl_flat", "ctl_proxy", "ctl_direct", "ctl_lowspp")
NULL_SETS = ("null_identical", "null_reencode")
NUISANCE_SET = "nuisance_ev"
AB_SETS = ("m5_vs_m6", "look_alt")
assert tuple(SETS) == SET_ORDER

DEFAULTS = {
    "control_views": 8, "reencode_quality": 70, "min_decisive": 30, "min_rooms": 10, "alpha": 0.05,
    "bootstrap_resamples": 2000, "bootstrap_seed": 0,
    "targets": {"correct_min": 0.70, "wrong_max": 0.05, "consensus_correct_min": 0.60,
                "null_identical_tie_min": 0.90, "null_reencode_win_max": 0.10, "nuisance_brighter_max": 0.30,
                "delta_ev_flag": 0.3, "halo_max": 0.80},
}
MODEL_NAMES = {"qwen": "Qwen", "glm": "GLM"}
HALO_NOTE = "ask one aspect per call (M7)"


def realism_cfg(cfg: Optional[dict] = None) -> dict:
    """``check.yaml: realism`` (``cfg`` = the whole check config, None = this package's) over ``DEFAULTS``."""
    if cfg is None:
        from wenart.vision_check.config import load_config
        cfg = load_config()
    block = (cfg or {}).get("realism") or {}
    out = copy.deepcopy(DEFAULTS)
    out.update({k: v for k, v in block.items() if k != "targets"})
    out["targets"].update(block.get("targets") or {})
    return out


def model_name(key: str) -> str:
    return MODEL_NAMES.get(key, key)


def pair_id(set_name: str, cam: str) -> str:
    return f"{set_name}:{cam}"


def call_key(pid: str, order: str) -> str:
    """``realism|<set>:<cam>|<order>`` (§6.1)."""
    return f"{PROMPT_KIND}|{pid}|{order}"


def answers_path(out: Path, slug: str) -> Path:
    return Path(out) / REALISM_DIR / f"answers_{slug}.json"


def select_sets(sets: Optional[str] = None, skip: Optional[str] = None) -> list[str]:
    """Set names from ``--sets`` (default all) minus ``--skip-sets``, in the asking order (UsageError if unknown)."""
    def names(text):
        return [s for s in (text or "").replace(",", " ").split() if s]
    chosen, skipped = names(sets), names(skip)
    unknown = [s for s in chosen + skipped if s not in SETS]
    if unknown:
        raise C.UsageError(f"unknown realism set(s) {unknown}; choose from {', '.join(SET_ORDER)}")
    return [s for s in SET_ORDER if (not chosen or s in chosen) and s not in skipped]


# --------------------------------------------------------------------------
# Answers: post-validation and outcomes (§6.1)
# --------------------------------------------------------------------------

def post_validate(answer) -> tuple[Optional[dict], Optional[str]]:
    """``(answer, None)`` with repeated cues removed (first one kept), or ``(None, error)`` off the schema."""
    problems = schema_errors(S.realism_schema(), answer)
    if problems:
        return None, "schema: " + "; ".join(problems[:5])
    out = copy.deepcopy(answer)
    for aspect in ASPECTS:
        out[aspect]["cues"] = list(dict.fromkeys(out[aspect]["cues"]))
    return out, None


class RealismClient:
    """A client (``.model`` + ``.run_schema``) with the realism system prompt and the post-validation.

    ``calls.run_specs`` hands its deadline to ``.deadline``; it is passed on to
    the wrapped client when that one takes it (``VLMClient``).
    """

    def __init__(self, client) -> None:
        self.client = client

    @property
    def model(self):
        return self.client.model

    @property
    def deadline(self):
        return getattr(self.client, "deadline", None)

    @deadline.setter
    def deadline(self, value) -> None:
        if hasattr(self.client, "deadline"):
            self.client.deadline = value

    def run_schema(self, images, prompt, schema, **kwargs):
        kwargs["system_prompt"] = SYSTEM_PROMPT
        result = self.client.run_schema(images, prompt, schema, **kwargs)
        if result.data is not None:
            data, error = post_validate(result.data)
            result.data = data
            if error:
                result.error = error
        return result


def picks_b(order: str, winner: Optional[str]) -> Optional[bool]:
    """True when ``winner`` of a call in ``order`` is image B (None for no answer)."""
    if winner not in WINNERS:
        return None
    return (order == "ab" and winner == "image_2") or (order == "ba" and winner == "image_1")


def model_outcome(ans_ab: Optional[dict], ans_ba: Optional[dict], aspect: str) -> dict:
    """One model, one pair, one aspect: ``{outcome W|L|T|NC, graded -6..6 | None, winners, margins, cues}``.

    W = B picked in both orders, L = A in both, T = the pick follows the
    position, NC = an answer is missing (never a tie or a loss). The graded
    score sums +-1/2/3 (slight/clear/large, + toward B) over both orders, so a
    pure position bias with equal margins cancels to 0.
    """
    answers = {"ab": ans_ab, "ba": ans_ba}
    winners = [((answers[o] or {}).get(aspect) or {}).get("winner") for o in ORDERS]
    margins = [((answers[o] or {}).get(aspect) or {}).get("margin") for o in ORDERS]
    cues = [list(((answers[o] or {}).get(aspect) or {}).get("cues") or []) if answers[o] else None for o in ORDERS]
    rec = {"outcome": "NC", "graded": None, "winners": winners, "margins": margins, "cues": cues}
    if ans_ab is None or ans_ba is None:
        return rec
    b = [picks_b(o, w) for o, w in zip(ORDERS, winners)]
    graded = 0
    for pick, margin in zip(b, margins):
        weight = MARGIN_WEIGHT[margin]
        graded += weight if pick else -weight
    rec["outcome"] = "W" if all(b) else "L" if not any(b) else "T"
    rec["graded"] = graded
    return rec


def consensus(outcomes: Iterable[str]) -> str:
    """W only when every model says W, L only when every model says L, NC when any is NC (or none), else T."""
    outcomes = list(outcomes)
    if not outcomes or any(o == "NC" for o in outcomes):
        return "NC"
    if all(o == "W" for o in outcomes):
        return "W"
    if all(o == "L" for o in outcomes):
        return "L"
    return "T"


# --------------------------------------------------------------------------
# Statistics (§6.1)
# --------------------------------------------------------------------------

def counts(outcomes: Iterable[str]) -> dict:
    c = Counter(outcomes)
    return {o: int(c.get(o, 0)) for o in OUTCOMES}


def sign_test_p(w: int, l: int) -> float:
    """Exact two-sided sign test of W vs L (ties out): the probability of every split at most as likely as this one."""
    n = int(w) + int(l)
    if n == 0:
        return 1.0
    ck = comb(n, int(w))
    total = sum(c for c in (comb(n, i) for i in range(n + 1)) if c <= ck)
    return min(1.0, total / 2 ** n)


def room_outcome(outcomes: Iterable[str]) -> str:
    """A room's outcome from its views: W if W > L, L if L > W, else T (NC views ignored; NC when all are NC)."""
    outcomes = [o for o in outcomes if o != "NC"]
    if not outcomes:
        return "NC"
    w, l = outcomes.count("W"), outcomes.count("L")
    return "W" if w > l else "L" if l > w else "T"


def room_bootstrap(items: Iterable[tuple[str, str]], resamples: int = 2000, seed: int = 0) -> list:
    """95 % interval ``[lo, hi]`` of the net win (W - L) / N over ``(room, outcome)`` items, resampling rooms.

    Views of one room share materials and lights, so the rooms (sorted by
    name) are drawn with replacement, each bringing all of its views; NC
    views are left out of N. ``[None, None]`` without data. Deterministic for
    a seed (``random.Random``).
    """
    rooms: dict[str, list] = {}
    for room, outcome in items:
        rooms.setdefault(str(room), []).append(outcome)
    names = sorted(rooms)
    if not names:
        return [None, None]
    rng = random.Random(seed)
    stats = []
    for _ in range(int(resamples)):
        sample = [o for _ in names for o in rooms[rng.choice(names)] if o != "NC"]
        if sample:
            stats.append((sample.count("W") - sample.count("L")) / len(sample))
    if not stats:
        return [None, None]
    stats.sort()
    return [round(stats[int(0.025 * len(stats))], 4), round(stats[max(0, int(0.975 * len(stats)) - 1)], 4)]


def _p(value: float) -> float:
    return float(f"{value:.6g}")


def _rate(num: int, den: int) -> Optional[float]:
    return round(num / den, 4) if den else None


def row_outcome(row: dict, model: str, aspect: str) -> str:
    return ((((row.get("models") or {}).get(model) or {}).get("aspects") or {}).get(aspect) or {}).get("outcome", "NC")


def row_consensus(row: dict, aspect: str, models: Iterable[str]) -> str:
    return consensus(row_outcome(row, m, aspect) for m in models)


def aspect_stats(rows: list[dict], aspect: str, models: list[str], cons_models: list[str], rc: dict) -> dict:
    """Per model W/L/T/NC, consistency and mean graded; the consensus of ``cons_models`` with its statistics."""
    per_model = {}
    for m in models:
        outs = [row_outcome(r, m, aspect) for r in rows]
        c = counts(outs)
        n = c["W"] + c["L"] + c["T"]
        graded = [((r["models"].get(m) or {}).get("aspects") or {}).get(aspect, {}).get("graded") for r in rows
                  if m in (r.get("models") or {})]
        graded = [g for g in graded if g is not None]
        per_model[m] = {**c, "consistency": _rate(c["W"] + c["L"], n),
                        "mean_graded": round(sum(graded) / len(graded), 3) if graded else None}
    cons = [row_consensus(r, aspect, cons_models) for r in rows]
    c = counts(cons)
    n = c["W"] + c["L"] + c["T"]
    items = [(r["room"], o) for r, o in zip(rows, cons)]
    by_room: dict[str, list] = {}
    for room, o in items:
        by_room.setdefault(room, []).append(o)
    rooms = counts(room_outcome(v) for v in by_room.values())
    return {
        "models": per_model, "consensus": c, "n": n, "decisive": c["W"] + c["L"],
        "decisive_rooms": len({room for room, o in items if o in ("W", "L")}),
        "win_rate": _rate(c["W"], n), "loss_rate": _rate(c["L"], n),
        "net_win": _rate(c["W"] - c["L"], n),
        "sign_p": _p(sign_test_p(c["W"], c["L"])),
        "rooms": rooms, "rooms_sign_p": _p(sign_test_p(rooms["W"], rooms["L"])),
        "net_win_ci95": room_bootstrap(items, int(rc["bootstrap_resamples"]), int(rc["bootstrap_seed"])),
    }


def position_bias(rows: list[dict], model: str) -> dict:
    """``{image_1, picks, index}``: the share of ``image_1`` picks over every answered call and aspect (~0.5)."""
    n1 = n = 0
    for r in rows:
        aspects = ((r.get("models") or {}).get(model) or {}).get("aspects") or {}
        for rec in aspects.values():
            for w in rec.get("winners") or []:
                if w in WINNERS:
                    n += 1
                    n1 += w == "image_1"
    return {"image_1": n1, "picks": n, "index": _rate(n1, n)}


def top_cues(rows: list[dict], aspect: str, cons_models: list[str], k: int = 5) -> dict:
    """Cues of the answers that picked the consensus winner on decisive pairs: ``{"W": [[cue, n]], "L": [...]}``."""
    out = {}
    for side in ("W", "L"):
        c: Counter = Counter()
        for r in rows:
            if row_consensus(r, aspect, cons_models) != side:
                continue
            for m in cons_models:
                rec = ((r["models"].get(m) or {}).get("aspects") or {}).get(aspect) or {}
                for order, w, cues in zip(ORDERS, rec.get("winners") or [], rec.get("cues") or []):
                    if cues and picks_b(order, w) == (side == "W"):
                        c.update(cues)
        out[side] = [[cue, n] for cue, n in sorted(c.items(), key=lambda x: (-x[1], x[0]))[:k]]
    return out


def set_stats(rows: list[dict], models: list[str], cons_models: list[str], rc: dict) -> dict:
    """Statistics of one pair set: pairs, rooms, every aspect, position bias per model, top decisive cues."""
    return {
        "pairs": len(rows), "rooms": len({r["room"] for r in rows}), "consensus_models": list(cons_models),
        "aspects": {a: aspect_stats(rows, a, models, cons_models, rc) for a in ASPECTS},
        "position_bias": {m: position_bias(rows, m) for m in models},
        "top_cues": {a: top_cues(rows, a, cons_models) for a in ASPECTS},
    }


# --------------------------------------------------------------------------
# Controls (§6.2)
# --------------------------------------------------------------------------

def _by_set(rows: list[dict]) -> dict[str, list]:
    out: dict[str, list] = {}
    for r in rows:
        out.setdefault(r["set"], []).append(r)
    return out


def _known_direction(outs: list[str], expected: str, correct_min: float, wrong_max: float) -> dict:
    c = counts(outs)
    n = c["W"] + c["L"] + c["T"]
    good, bad = ("W", "L") if expected == "b" else ("L", "W")
    correct, wrong = c[good], c[bad]
    ok = bool(n) and correct / n >= correct_min and wrong / n <= wrong_max
    return {"n": n, "correct": correct, "wrong": wrong, "tie": c["T"], "nc": c["NC"],
            "correct_rate": _rate(correct, n), "wrong_rate": _rate(wrong, n), "pass": ok}


def evaluate_controls(rows: list[dict], models: list[str], rc: dict) -> Optional[dict]:
    """The controls table of §6.2 from the rows of a control project (None when it has no control set).

    - ``ctl_*``: per model and for the consensus, order-consistent correct
      (the expected image won the target aspect), wrong and T over non-NC
      pairs; per model ``pass`` = correct >= ``correct_min`` and wrong <=
      ``wrong_max`` (consensus: ``consensus_correct_min``);
    - ``null_identical``: T share over pair-aspects, every flip listed;
      ``null_reencode``: share won by the normal file (W);
    - ``nuisance_ev``: share of pair-aspects won by the brighter image (by
      ``delta_ev``); above ``nuisance_brighter_max`` the A/B pairs with
      ``|delta_ev| > delta_ev_flag`` are flagged (``flag``);
    - ``halo``: on the ``ctl_*`` pairs with a decisive target aspect, the
      share of the other aspects with the same outcome;
    - ``signal``: a model has signal when it passes each of the four ``ctl_*``.
    """
    by_set = _by_set(rows)
    if not any(s in by_set for s in CONTROL_SETS + NULL_SETS + (NUISANCE_SET,)):
        return None
    t = rc["targets"]
    sets: dict = {}
    for s in CONTROL_SETS:
        rs = by_set.get(s, [])
        pset = SETS[s]
        entry = {"kind": "known_direction", "text": pset.text, "target_aspect": pset.target_aspect,
                 "expected": pset.expected, "pairs": len(rs), "models": {}}
        for m in models:
            entry["models"][m] = _known_direction([row_outcome(r, m, pset.target_aspect) for r in rs],
                                                  pset.expected, float(t["correct_min"]), float(t["wrong_max"]))
        entry["consensus"] = _known_direction([row_consensus(r, pset.target_aspect, models) for r in rs],
                                              pset.expected, float(t["consensus_correct_min"]), float(t["wrong_max"]))
        sets[s] = entry
    # null_identical: identical files must come back T (the pick follows the position); W or L is a flip.
    rs = by_set.get("null_identical", [])
    entry = {"kind": "null", "text": SETS["null_identical"].text, "pairs": len(rs), "models": {}}
    for m in models:
        n = tie = 0
        flips = []
        for r in rs:
            for a in ASPECTS:
                o = row_outcome(r, m, a)
                if o == "NC":
                    continue
                n += 1
                tie += o == "T"
                if o in ("W", "L"):
                    flips.append(f"{r['pair_id']}/{a}: {o}")
        rate = _rate(tie, n)
        entry["models"][m] = {"n": n, "tie": tie, "tie_rate": rate, "flips": flips,
                              "pass": bool(n) and rate >= float(t["null_identical_tie_min"])}
    sets["null_identical"] = entry
    rs = by_set.get("null_reencode", [])
    entry = {"kind": "null", "text": SETS["null_reencode"].text, "pairs": len(rs), "models": {}}
    for m in models:
        outs = [row_outcome(r, m, a) for r in rs for a in ASPECTS]
        c = counts(outs)
        n = c["W"] + c["L"] + c["T"]
        rate = _rate(c["W"], n)
        entry["models"][m] = {"n": n, "win": c["W"], "loss": c["L"], "tie": c["T"], "win_rate": rate,
                              "pass": bool(n) and rate <= float(t["null_reencode_win_max"])}
    sets["null_reencode"] = entry
    rs = by_set.get(NUISANCE_SET, [])
    devs = [r.get("delta_ev") for r in rs if r.get("delta_ev") is not None]
    entry = {"kind": "nuisance", "text": SETS[NUISANCE_SET].text, "pairs": len(rs), "models": {},
             "mean_delta_ev": round(sum(devs) / len(devs), 3) if devs else None}
    for m in models:
        n = brighter = 0
        for r in rs:
            dev = r.get("delta_ev")
            if not dev:
                continue
            for a in ASPECTS:
                o = row_outcome(r, m, a)
                if o == "NC":
                    continue
                n += 1
                brighter += (o == "W" and dev > 0) or (o == "L" and dev < 0)
        share = _rate(brighter, n)
        entry["models"][m] = {"n": n, "brighter_wins": brighter, "share": share,
                              "flag": share is not None and share > float(t["nuisance_brighter_max"])}
    entry["flag"] = any(v["flag"] for v in entry["models"].values())
    sets[NUISANCE_SET] = entry
    halo = {}
    for m in models:
        n = follow = 0
        for s in CONTROL_SETS:
            target = SETS[s].target_aspect
            for r in by_set.get(s, []):
                o_t = row_outcome(r, m, target)
                if o_t not in ("W", "L"):
                    continue
                for a in ASPECTS:
                    if a != target:
                        n += 1
                        follow += row_outcome(r, m, a) == o_t
        share = _rate(follow, n)
        halo[m] = {"n": n, "follow": follow, "share": share,
                   "note": HALO_NOTE if share is not None and share > float(t["halo_max"]) else None}
    signal = {m: all(sets[s]["models"][m]["pass"] for s in CONTROL_SETS) for m in models}
    notes = [f"no signal from {model_name(m)}" for m in models if not signal[m]]
    notes += [f"halo {model_name(m)} {h['share']:.2f} > {float(t['halo_max']):.2f}: {HALO_NOTE}"
              for m, h in halo.items() if h["note"]]
    if sets[NUISANCE_SET]["flag"]:
        notes.append(f"nuisance_ev: the brighter image wins more than {float(t['nuisance_brighter_max']):.0%} for "
                     f"{', '.join(model_name(m) for m, v in sets[NUISANCE_SET]['models'].items() if v['flag'])}: "
                     f"A/B pairs with |dEV| > {float(t['delta_ev_flag'])} are flagged")
    return {"sets": sets, "halo": halo, "signal": signal, "no_signal": [m for m in models if not signal[m]],
            "notes": notes, "targets": dict(t)}


# --------------------------------------------------------------------------
# Decisions (realism-summary only)
# --------------------------------------------------------------------------

def _significant(st: dict, side: str, alpha: float) -> bool:
    c = st["consensus"]
    other = "L" if side == "W" else "W"
    return c[side] > c[other] and st["sign_p"] < alpha


def aspect_verdict(st: dict, rc: dict) -> Optional[str]:
    """``better`` / ``worse`` for one aspect's statistics, None when neither rule holds (§6.1)."""
    alpha = float(rc["alpha"])
    enough = st["decisive"] >= int(rc["min_decisive"]) and st["decisive_rooms"] >= int(rc["min_rooms"])
    lo, hi = st["net_win_ci95"]
    if enough and _significant(st, "W", alpha) and lo is not None and lo > 0:
        return "better"
    if enough and _significant(st, "L", alpha) and hi is not None and hi < 0:
        return "worse"
    return None


def decide(stats: dict, measurable: bool, rc: dict) -> tuple[str, dict]:
    """``(set decision, {aspect: decision})`` from ``set_stats``.

    - ``not_measurable`` when no model has signal (the controls fail for every model);
    - ``better`` when the consensus ``photo`` W > L with sign p < alpha, at
      least ``min_decisive`` decisive pairs from ``min_rooms`` rooms, the room
      net-win interval above 0, and no aspect with significantly more L than W;
    - ``worse`` the same with W and L swapped;
    - otherwise ``no_detectable_difference`` (never "equal").
    Each aspect gets the same rule on its own statistics (without the
    cross-aspect clause).
    """
    if not measurable:
        return "not_measurable", {a: "not_measurable" for a in ASPECTS}
    alpha = float(rc["alpha"])
    aspects = {a: aspect_verdict(stats["aspects"][a], rc) or "no_detectable_difference" for a in ASPECTS}
    photo = aspect_verdict(stats["aspects"]["photo"], rc)
    if photo == "better" and not any(_significant(stats["aspects"][a], "L", alpha) for a in ASPECTS):
        return "better", aspects
    if photo == "worse" and not any(_significant(stats["aspects"][a], "W", alpha) for a in ASPECTS):
        return "worse", aspects
    return "no_detectable_difference", aspects


# --------------------------------------------------------------------------
# Control views and the pairs file (realism-pairs)
# --------------------------------------------------------------------------

def furniture_share(entry: dict, table: dict) -> float:
    """Share of the frame covered by furniture pass indices (``index_stats`` + ``views.index_table``)."""
    res = entry.get("resolution") or []
    if len(res) != 2 or not int(res[0]) or not int(res[1]):
        return 0.0
    pixels = sum(int(v.get("pixels") or 0) for k, v in (entry.get("index_stats") or {}).items()
                 if (table.get(int(k)) or {}).get("kind") == "furniture")
    return pixels / (int(res[0]) * int(res[1]))


def control_views(render_manifest: dict, scene_manifest: dict, n: int = 8) -> list[str]:
    """The ``n`` cameras of a render manifest with the highest furniture pixel share, ties by name (§6.2)."""
    table = views.index_table(scene_manifest or {})
    scored: dict[str, float] = {}
    for entry in (render_manifest or {}).get("renders") or []:
        cam = entry.get("camera")
        if cam and cam not in scored:
            scored[cam] = furniture_share(entry, table)
    ranked = sorted(scored, key=lambda cam: (-scored[cam], cam))
    return ranked[:max(0, int(n))]


def write_reencode(src: Path, dst: Path, quality: int) -> Path:
    """``src`` re-encoded by PIL as a JPEG of ``quality`` (rewritten only when the bytes change)."""
    from PIL import Image
    buf = io.BytesIO()
    with Image.open(src) as img:
        img.convert("RGB").save(buf, format="JPEG", quality=int(quality))
    data = buf.getvalue()
    dst = Path(dst)
    if not dst.is_file() or dst.read_bytes() != data:
        dst.parent.mkdir(parents=True, exist_ok=True)
        tmp = dst.with_name(dst.name + ".tmp")
        tmp.write_bytes(data)
        tmp.replace(dst)
    return dst


def mean_luminance(path: Path) -> Optional[float]:
    """Mean linear Rec. 709 luminance (0..1) of an sRGB image file."""
    import numpy as np
    from PIL import Image
    with Image.open(path) as img:
        rgb = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    y = float((lin @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)).mean())
    return y if y > 0 else None


def delta_ev(a: Path, b: Path, cache: Optional[dict] = None) -> Optional[float]:
    """Measured brightness difference of B over A in stops: log2 of the mean linear luminance ratio."""
    cache = {} if cache is None else cache
    lum = []
    for p in (a, b):
        key = str(Path(p).resolve())
        if key not in cache:
            cache[key] = mean_luminance(p)
        lum.append(cache[key])
    if lum[0] is None or lum[1] is None:
        return None
    return round(math.log2(lum[1] / lum[0]), 3)


def check_unique(pairs: list[dict]) -> None:
    """ValueError when two pairs share a ``pair_id`` (it is the call key: answers would overwrite each other)."""
    ids = Counter(p["pair_id"] for p in pairs)
    dup = sorted(pid for pid, n in ids.items() if n > 1)
    if dup:
        raise ValueError(f"duplicate pair ids: {', '.join(dup)}")


def _room_ids(manifest: dict, scene: dict) -> dict:
    rooms = {c.get("name"): c.get("room_id") for c in (scene or {}).get("cameras") or [] if c.get("name")}
    for e in manifest.get("renders") or []:
        if e.get("camera") and e.get("room_id"):
            rooms[e["camera"]] = e["room_id"]
    return rooms


def build_pairs(out, controls: bool = False, cfg: Optional[dict] = None) -> dict:
    """The ``ab/pairs.json`` content of one project output (§6.3); writes the ``null_reencode`` A files.

    Reads only files under ``out``: ``ab/renders/render_manifest.json`` (the
    AB render cameras, their rooms and index statistics),
    ``ab/scene/scene_manifest.json`` (index table for ``control_views``),
    ``ab/cameras_check.json`` (``kept`` cameras for ``m5_vs_m6``, ``dropped``
    copied). A pair whose file is missing is listed under ``skipped``.
    Raises FileNotFoundError without the AB render manifest or the camera
    check, ValueError on a duplicate pair id.
    """
    out = Path(out).resolve()
    rc = realism_cfg(cfg)
    manifest = read_json(out / AB_RENDER_MANIFEST)
    if manifest is None:
        raise FileNotFoundError(f"no {AB_RENDER_MANIFEST.as_posix()} in {out} (AB render missing)")
    check = read_json(out / CAMERAS_CHECK)
    if check is None:
        raise FileNotFoundError(f"no {CAMERAS_CHECK.as_posix()} in {out} (AB camera check missing)")
    scene = read_json(out / AB_SCENE_MANIFEST) or {}
    warnings: list[str] = []
    skipped: list[dict] = []
    cams: list[str] = []
    for e in manifest.get("renders") or []:
        if e.get("camera") and e["camera"] not in cams:
            cams.append(e["camera"])
    rooms = _room_ids(manifest, scene)
    project = str(scene.get("project") or (read_json(out / AB_DIR / "m5" / "scene_manifest.json") or {}).get("project")
                  or out.name)
    kept = [str(c) for c in check.get("kept") or []]
    dropped = [{"cam": str(d.get("cam")), "reason": str(d.get("reason") or "")}
               for d in check.get("dropped") or [] if isinstance(d, dict)]
    for cam in kept:
        if cam not in cams:
            skipped.append({"set": "m5_vs_m6", "cam": cam, "reason": "kept camera not in the AB render manifest"})
    by_set: dict[str, list] = {"m5_vs_m6": [c for c in cams if c in kept], "look_alt": list(cams)}
    chosen: list[str] = []
    if controls:
        if not scene:
            warnings.append(f"no {AB_SCENE_MANIFEST.as_posix()}: control views ranked without the index table")
        chosen = control_views(manifest, scene, int(rc["control_views"]))
        for s in SET_ORDER:
            if SETS[s].control:
                by_set[s] = list(chosen)
        for cam in chosen:
            src = out / NORMAL.format(cam=cam)
            if src.is_file():
                write_reencode(src, out / SETS["null_reencode"].a.format(cam=cam), int(rc["reencode_quality"]))
    pairs: list[dict] = []
    sha: dict = {}
    lum: dict = {}

    def file_sha(p: Path) -> str:
        key = str(p)
        if key not in sha:
            sha[key] = sha256_file(p)
        return sha[key]

    for s in SET_ORDER:
        pset = SETS[s]
        set_cams = by_set.get(s, [])
        if s == "look_alt" and set_cams and not any((out / pset.b.format(cam=c)).is_file() for c in set_cams):
            warnings.append("look_alt: no alt previews in ab/renders (rendered without --alt-look?): no look_alt pairs")
            continue
        for cam in set_cams:
            a, b = out / pset.a.format(cam=cam), out / pset.b.format(cam=cam)
            missing = [rel(p, out) for p in (a, b) if not p.is_file()]
            if missing:
                skipped.append({"set": s, "cam": cam, "reason": "missing " + ", ".join(dict.fromkeys(missing))})
                continue
            room_id = rooms.get(cam)
            msg = f"{cam}: no room id in the AB render or scene manifest; the camera is its own room"
            if room_id is None and msg not in warnings:
                warnings.append(msg)
            pairs.append({
                "pair_id": pair_id(s, cam), "set": s, "cam": cam, "room_id": room_id,
                "a": rel(a, out), "b": rel(b, out), "expected": pset.expected, "target_aspect": pset.target_aspect,
                "a_sha256": file_sha(a), "b_sha256": file_sha(b), "a_bytes": a.stat().st_size,
                "b_bytes": b.stat().st_size, "delta_ev": delta_ev(a, b, lum),
            })
    check_unique(pairs)
    sets = {s: sum(1 for p in pairs if p["set"] == s) for s in SET_ORDER if any(p["set"] == s for p in pairs)}
    return {"schema_version": "0.1", "kind": "realism_pairs", "project": project, "controls": bool(controls),
            "control_views": chosen, "reencode_quality": int(rc["reencode_quality"]),
            "render_manifest": AB_RENDER_MANIFEST.as_posix(), "cameras_check": CAMERAS_CHECK.as_posix(),
            "sets": sets, "pairs": pairs, "dropped": dropped, "skipped": skipped, "warnings": warnings}


# --------------------------------------------------------------------------
# Calls (realism)
# --------------------------------------------------------------------------

def input_sha256(image_shas: list[str], model: str) -> str:
    """sha256 of everything the answer depends on: system prompt, prompt, schema, labels, image bytes, model id."""
    payload = {"system": SYSTEM_PROMPT, "prompt": PROMPT, "schema": S.realism_schema(), "labels": list(LABELS),
               "images": list(image_shas), "model": model}
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def pair_images(out: Path, pair: dict, order: str) -> list[Path]:
    a, b = Path(out) / pair["a"], Path(out) / pair["b"]
    return [a, b] if order == "ab" else [b, a]


def _image_size(path: Path) -> tuple:
    from PIL import Image
    with Image.open(path) as img:
        return tuple(img.size)


def pair_spec(out: Path, pair: dict, order: str, model: str, cache: dict,
              warnings: Optional[list] = None) -> Optional[C.CallSpec]:
    """The call of one pair in one order, or None when an image is missing (a warning)."""
    images = pair_images(out, pair, order)
    missing = [p for p in images if not p.is_file()]
    if missing:
        if warnings is not None:
            msg = f"{pair['pair_id']}: image missing ({', '.join(rel(p, out) for p in missing)}); not asked"
            if msg not in warnings:
                warnings.append(msg)
        return None
    shas = []
    for p in images:
        key = str(p.resolve())
        if key not in cache:
            cache[key] = sha256_file(p)
        shas.append(cache[key])
    want = [pair.get("a_sha256"), pair.get("b_sha256")]
    if order == "ba":
        want.reverse()
    if warnings is not None and want != shas:
        msg = f"{pair['pair_id']}: an image changed after realism-pairs; run realism-pairs again"
        if msg not in warnings:
            warnings.append(msg)
    first, second = ("a", "b") if order == "ab" else ("b", "a")
    items = [{"label": "image_1", "decoy": False, "wenart_id": first},
             {"label": "image_2", "decoy": False, "wenart_id": second}]
    spec = C.CallSpec(key=call_key(pair["pair_id"], order), camera=pair["cam"], image_kind=pair["set"],
                      prompt_kind=PROMPT_KIND, prompt=PROMPT, schema=S.realism_schema(), images=images,
                      image_labels=list(LABELS), size=_image_size(images[0]), items=items, order=order)
    spec.input_sha256 = input_sha256(shas, model)
    return spec


def realism_specs(out, pairs_doc: dict, model: str = "", sets: Optional[Iterable[str]] = None,
                  warnings: Optional[list] = None) -> list[C.CallSpec]:
    """Every call of the pairs file: sets in ``SET_ORDER`` (only ``sets`` when given), each pair ``ab`` then ``ba``."""
    out = Path(out).resolve()
    wanted = set(SET_ORDER if sets is None else sets)
    cache: dict = {}
    specs = []
    for s in SET_ORDER:
        if s not in wanted:
            continue
        for pair in pairs_doc.get("pairs") or []:
            if pair.get("set") != s:
                continue
            for order in ORDERS:
                spec = pair_spec(out, pair, order, model, cache, warnings)
                if spec is not None:
                    specs.append(spec)
    return specs


# --------------------------------------------------------------------------
# realism-combine
# --------------------------------------------------------------------------

def call_answer(store: C.AnswerStore, spec: Optional[C.CallSpec]) -> tuple[str, Optional[dict]]:
    """``(status, answer)``: ``answered`` (current inputs, valid answer), ``failed``, ``stale`` or ``missing``."""
    if spec is None:
        return "missing", None
    rec = store.get(spec.key)
    if rec is None:
        return "missing", None
    if rec.get("input_sha256") != spec.input_sha256:
        return "stale", None
    if rec.get("data") is None or rec.get("error"):
        return "failed", None
    data, error = post_validate(rec["data"])
    return ("answered", data) if error is None else ("failed", None)


def room_key(project: str, room_id: Optional[str], cam: str) -> str:
    """Rooms of different projects never pool: ``<project>:<room_id>`` (a camera without a room is its own)."""
    return f"{project}:{room_id}" if room_id else f"{project}:?{cam}"


def stores_for(out: Path, keys: list[str], cfg: dict) -> dict:
    models = cfg["models"]
    unknown = [k for k in keys if k not in models]
    if unknown:
        raise C.UsageError(f"model key(s) {unknown} not in check.yaml (known: {', '.join(models)})")
    return {k: C.AnswerStore(answers_path(out, models[k]["slug"]), k, models[k]["slug"]) for k in keys}


def call_stats(project: str, rows: list[dict], models: list[str]) -> list[dict]:
    """Per set and model: calls expected (2 per pair), answered, failed, stale, missing and the set status."""
    out = []
    by_set = _by_set(rows)
    for s in SET_ORDER:
        rs = by_set.get(s)
        if not rs:
            continue
        for m in models:
            c = Counter(((r["models"].get(m) or {}).get("calls") or {}).get(o, "missing") for r in rs for o in ORDERS)
            expected = 2 * len(rs)
            recorded = c["answered"] + c["failed"] + c["stale"]
            status = "complete" if c["answered"] == expected else "not_started" if recorded == 0 else "incomplete"
            out.append({"project": project, "set": s, "model": m, "expected": expected, "answered": c["answered"],
                        "failed": c["failed"], "stale": c["stale"], "missing": c["missing"],
                        "answered_rate": _rate(c["answered"], expected), "status": status})
    return out


def combine(out, keys: list[str], cfg: Optional[dict] = None) -> dict:
    """The ``realism_ab.json`` content of one project: rows, statistics per set, controls, calls (no decision).

    Raises FileNotFoundError without ``ab/pairs.json``, ``calls.UsageError``
    for a model key that is not in ``check.yaml``.
    """
    from wenart.vision_check.config import load_config
    out = Path(out).resolve()
    cfg = cfg if cfg is not None else load_config()
    rc = realism_cfg(cfg)
    pairs_doc = read_json(out / PAIRS_JSON)
    if pairs_doc is None:
        raise FileNotFoundError(f"no {PAIRS_JSON.as_posix()} in {out} (run realism-pairs first)")
    keys = list(keys)
    stores = stores_for(out, keys, cfg)
    project = str(pairs_doc.get("project") or out.name)
    warnings: list[str] = []
    cache: dict = {}
    rows = []
    for s in SET_ORDER:
        for pair in pairs_doc.get("pairs") or []:
            if pair.get("set") != s:
                continue
            row = {"pair_id": pair["pair_id"], "set": s, "cam": pair["cam"], "room_id": pair.get("room_id"),
                   "room": room_key(project, pair.get("room_id"), pair["cam"]), "project": project,
                   "a": pair["a"], "b": pair["b"], "expected": pair.get("expected"),
                   "target_aspect": pair.get("target_aspect"), "delta_ev": pair.get("delta_ev"), "models": {}}
            for k in keys:
                model = stores[k].data.get("model") or ""
                answers, statuses = {}, {}
                for order in ORDERS:
                    spec = pair_spec(out, pair, order, model, cache, warnings)
                    statuses[order], answers[order] = call_answer(stores[k], spec)
                    if statuses[order] == "stale":
                        msg = f"{k}: stale answer for {call_key(pair['pair_id'], order)} (inputs changed); not used"
                        if msg not in warnings:
                            warnings.append(msg)
                row["models"][k] = {"calls": statuses,
                                    "aspects": {a: model_outcome(answers["ab"], answers["ba"], a) for a in ASPECTS}}
            row["consensus"] = {a: row_consensus(row, a, keys) for a in ASPECTS}
            rows.append(row)
    by_set = _by_set(rows)
    models_info = {}
    for k in keys:
        mc = cfg["models"][k]
        models_info[k] = {"id": mc["id"], "slug": mc["slug"], "model": stores[k].data.get("model") or None,
                          "answers": rel(stores[k].path, out / REALISM_DIR) if stores[k].path.is_file() else None,
                          "incomplete": bool(stores[k].data.get("incomplete")),
                          "position_bias": position_bias(rows, k)}
    return {
        "schema_version": "0.1", "kind": "realism_ab", "project": project, "project_out": views.repo_path_text(out),
        "pairs_file": rel(out / PAIRS_JSON, out / REALISM_DIR), "models": models_info,
        "sets": {s: set_stats(by_set[s], keys, keys, rc) for s in SET_ORDER if s in by_set},
        "controls": evaluate_controls(rows, keys, rc), "calls": call_stats(project, rows, keys),
        "control_views": list(pairs_doc.get("control_views") or []),
        "dropped": list(pairs_doc.get("dropped") or []), "skipped": list(pairs_doc.get("skipped") or []),
        "warnings": list(pairs_doc.get("warnings") or []) + warnings, "contact_sheets": {}, "rows": rows,
    }


# --------------------------------------------------------------------------
# Contact sheets
# --------------------------------------------------------------------------

SHEET_ROWS = 10
THUMB_W = 320
TEXT_W = 430
HEADER_H = 44
COLOURS = {"W": (90, 200, 110), "L": (235, 90, 80), "T": (170, 170, 170), "NC": (230, 190, 60)}


def _font(size: int = 14):
    from PIL import ImageFont
    try:
        return ImageFont.load_default(size=size)
    except TypeError:                       # Pillow < 10.1: fixed bitmap font
        return ImageFont.load_default()


def _thumb(path: Path, width: int = THUMB_W):
    from PIL import Image
    try:
        with Image.open(path) as img:
            img = img.convert("RGB")
            h = max(1, round(img.height * width / img.width))
            return img.resize((width, h), Image.Resampling.LANCZOS)
    except (OSError, ValueError):
        return None


def sheet_image(out: Path, project: str, set_name: str, rows: list[dict], models: list[str], page: int, pages: int):
    """One contact sheet: a header, then per pair a row A | B | outcomes (per model with graded score, consensus)."""
    from PIL import Image, ImageDraw
    thumbs = [(_thumb(Path(out) / r["a"]), _thumb(Path(out) / r["b"])) for r in rows]
    th = max([t.height for pair in thumbs for t in pair if t is not None] or [round(THUMB_W * 9 / 16)])
    line = 18
    row_h = max(th, line * 7) + 6
    width = 2 * THUMB_W + TEXT_W + 4 * 6
    sheet = Image.new("RGB", (width, HEADER_H + len(rows) * row_h + 6), (28, 28, 28))
    draw = ImageDraw.Draw(sheet)
    font, small = _font(16), _font(14)
    pset = SETS[set_name]
    draw.text((8, 4), f"{project}  {set_name}  ({page}/{pages})", fill=(255, 255, 255), font=font)
    expected = (f"expected: {pset.expected.upper()} wins {pset.target_aspect}" if pset.expected in ("a", "b")
                else "expected: T" if pset.expected == "tie" else "no expected direction")
    draw.text((8, 24), f"left A, right B: {pset.text} | {expected}", fill=(200, 200, 200), font=small)
    cols = [len("furniture") * 8 + 14]
    for i, r in enumerate(rows):
        y = HEADER_H + i * row_h
        for j, t in enumerate(thumbs[i]):
            x = 6 + j * (THUMB_W + 6)
            if t is None:
                draw.rectangle([x, y, x + THUMB_W - 1, y + th - 1], outline=(230, 190, 60))
                draw.text((x + 8, y + 8), "image missing", fill=(230, 190, 60), font=small)
            else:
                sheet.paste(t, (x, y))
        x0 = 6 + 2 * (THUMB_W + 6)
        dev = r.get("delta_ev")
        head = f"{r['cam']}  {r.get('room_id') or '-'}" + (f"  dEV {dev:+.2f}" if dev is not None else "")
        draw.text((x0, y), head, fill=(255, 255, 255), font=small)
        x_models = [x0 + cols[0] + k * 72 for k in range(len(models) + 1)]
        draw.text((x0, y + line), "aspect", fill=(200, 200, 200), font=small)
        for k, m in enumerate(models):
            draw.text((x_models[k], y + line), model_name(m), fill=(200, 200, 200), font=small)
        draw.text((x_models[-1], y + line), "both", fill=(200, 200, 200), font=small)
        for n, a in enumerate(ASPECTS):
            ya = y + (n + 2) * line
            draw.text((x0, ya), a, fill=(220, 220, 220), font=small)
            for k, m in enumerate(models):
                rec = ((r["models"].get(m) or {}).get("aspects") or {}).get(a) or {}
                o = rec.get("outcome", "NC")
                g = rec.get("graded")
                draw.text((x_models[k], ya), o if g is None else f"{o} {g:+d}", fill=COLOURS[o], font=small)
            c = r["consensus"].get(a, "NC")
            draw.text((x_models[-1], ya), c, fill=COLOURS[c], font=small)
    return sheet


def write_contact_sheets(out: Path, doc: dict, models: list[str], rows_per_sheet: int = SHEET_ROWS) -> dict:
    """``check/realism/contact_realism_<set>_<n>.jpg`` (<= 300 KB each); older sheets of a set beyond ``n`` go."""
    from wenart.vision_check.plan_crop import save_jpeg
    out = Path(out)
    folder = out / REALISM_DIR
    names: dict[str, list] = {}
    by_set = _by_set(doc["rows"])
    for s in SET_ORDER:
        rows = by_set.get(s, [])
        chunks = [rows[i:i + rows_per_sheet] for i in range(0, len(rows), rows_per_sheet)]
        made = []
        for i, chunk in enumerate(chunks):
            name = f"{SHEET_PREFIX}{s}_{i + 1}.jpg"
            save_jpeg(sheet_image(out, doc["project"], s, chunk, models, i + 1, len(chunks)), folder / name)
            made.append(name)
        pattern = re.compile(rf"{re.escape(SHEET_PREFIX + s)}_(\d+)\.jpg")
        for old in folder.glob(f"{SHEET_PREFIX}{s}_*.jpg") if folder.is_dir() else []:
            if pattern.fullmatch(old.name) and old.name not in made:
                old.unlink()
        if made:
            names[s] = made
    return names


# --------------------------------------------------------------------------
# Markdown
# --------------------------------------------------------------------------

def _fmt(value, digits: int = 2) -> str:
    return "-" if value is None else f"{value:.{digits}f}"


def _fmt_p(p) -> str:
    return "-" if p is None else f"{p:.3g}"


def _fmt_ci(ci) -> str:
    if not ci or ci[0] is None:
        return "-"
    return f"[{ci[0]:+.2f}, {ci[1]:+.2f}]"


def table_header(models: list[str]) -> list[str]:
    """The decision-table header of §6.3 (with the model names of ``models``)."""
    cells = ["Aspect"] + [f"{model_name(m)} W/L/T (consistency)" for m in models]
    cells += ["Consensus W/L/T", "Win rate W/N", "Sign p", "Net win 95 % (rooms)",
              f"Mean graded {'/'.join(model_name(m) for m in models)}"]
    return ["| " + " | ".join(cells) + " |", "|" + "---|" * len(cells)]


def table_row(aspect: str, st: dict, models: list[str]) -> str:
    cells = [aspect]
    for m in models:
        s = st["models"].get(m) or {}
        nc = f"; NC {s.get('NC')}" if s.get("NC") else ""
        cells.append(f"{s.get('W', 0)}/{s.get('L', 0)}/{s.get('T', 0)} ({_fmt(s.get('consistency'))}{nc})")
    c = st["consensus"]
    cells.append(f"{c['W']}/{c['L']}/{c['T']}" + (f" (NC {c['NC']})" if c["NC"] else ""))
    cells.append(f"{_fmt(st['win_rate'])} ({c['W']}/{st['n']})")
    cells.append(_fmt_p(st["sign_p"]))
    cells.append(_fmt_ci(st["net_win_ci95"]))
    graded = [(st["models"].get(m) or {}).get("mean_graded") for m in models]
    cells.append("/".join("-" if g is None else f"{g:+.2f}" for g in graded))
    return "| " + " | ".join(cells) + " |"


def stats_table(stats: dict, models: list[str]) -> list[str]:
    return table_header(models) + [table_row(a, stats["aspects"][a], models) for a in ASPECTS]


def cue_lines(top: dict) -> list[str]:
    lines = []
    for a in ASPECTS:
        parts = []
        for side, label in (("W", "B wins"), ("L", "A wins")):
            cues = (top.get(a) or {}).get(side) or []
            if cues:
                parts.append(f"{label}: " + ", ".join(f"{c} ({n})" for c, n in cues))
        if parts:
            lines.append(f"- {a}: " + "; ".join(parts))
    return lines or ["- no decisive pair"]


def bias_line(bias: dict) -> str:
    return "Position bias (share of image_1 picks, about 0.5 expected): " + ", ".join(
        f"{model_name(m)} {_fmt(b['index'])} ({b['picks']} picks)" for m, b in bias.items()) + "."


def controls_lines(controls: Optional[dict], models: list[str]) -> list[str]:
    """The controls table and the null, nuisance and halo lines (§6.2)."""
    if not controls:
        return ["No control pairs."]
    t = controls["targets"]
    head = ["Set", "Target"] + [f"{model_name(m)} correct/wrong/T (n)" for m in models] + ["Consensus correct/wrong/T",
                                                                                         "Pass"]
    lines = [f"Targets per model: correct >= {t['correct_min']:.0%} (consensus >= {t['consensus_correct_min']:.0%}), "
             f"wrong <= {t['wrong_max']:.0%}. A model has signal when it passes every ctl_* set.", "",
             "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for s in CONTROL_SETS:
        e = controls["sets"][s]
        cells = [s, f"B wins {e['target_aspect']} ({e['text']})"]
        for m in models + ["consensus"]:
            v = e["models"].get(m) if m != "consensus" else e["consensus"]
            v = v or {}
            cells.append(f"{v.get('correct', 0)}/{v.get('wrong', 0)}/{v.get('tie', 0)} ({v.get('n', 0)})"
                         if m == "consensus" else
                         f"{v.get('correct', 0)}/{v.get('wrong', 0)}/{v.get('tie', 0)} ({v.get('n', 0)}) "
                         f"{_fmt(v.get('correct_rate'))}")
        cells.append(", ".join(f"{model_name(m)} {'yes' if (e['models'].get(m) or {}).get('pass') else 'no'}"
                               for m in models) + f", consensus {'yes' if e['consensus']['pass'] else 'no'}")
        lines.append("| " + " | ".join(cells) + " |")
    ni = controls["sets"]["null_identical"]
    lines += ["", f"null_identical ({ni['pairs']} pairs, target T >= {t['null_identical_tie_min']:.0%} of "
                  "pair-aspects): " + "; ".join(
                      f"{model_name(m)} T {_fmt(v['tie_rate'])} of {v['n']} ({'pass' if v['pass'] else 'FAIL'})"
                      + (f", flips: {', '.join(v['flips'])}" if v["flips"] else ", no flip")
                      for m, v in ni["models"].items())]
    nr = controls["sets"]["null_reencode"]
    lines.append(f"null_reencode ({nr['pairs']} pairs, target W <= {t['null_reencode_win_max']:.0%}): " + "; ".join(
        f"{model_name(m)} W {_fmt(v['win_rate'])} of {v['n']} ({'pass' if v['pass'] else 'FAIL'})"
        for m, v in nr["models"].items()))
    nu = controls["sets"][NUISANCE_SET]
    lines.append(f"nuisance_ev ({nu['pairs']} pairs, measured dEV {_fmt(nu['mean_delta_ev'])}): brighter image wins "
                 + "; ".join(f"{model_name(m)} {_fmt(v['share'])} of {v['n']}" for m, v in nu["models"].items())
                 + (f" -> above {t['nuisance_brighter_max']:.0%}: A/B pairs with |dEV| > {t['delta_ev_flag']} "
                    "are flagged" if nu["flag"] else f" (flag above {t['nuisance_brighter_max']:.0%})"))
    lines.append("halo (non-target aspects following the target winner on ctl_*): " + "; ".join(
        f"{model_name(m)} {_fmt(h['share'])} of {h['n']}" + (f" -> {h['note']}" if h["note"] else "")
        for m, h in controls["halo"].items()))
    lines.append("Signal: " + ", ".join(f"{model_name(m)} {'yes' if ok else 'no'}"
                                        for m, ok in controls["signal"].items()) + ".")
    return lines


def calls_lines(calls: list[dict], with_project: bool = False) -> list[str]:
    head = (["Project"] if with_project else []) + ["Set", "Model", "Answered", "Failed", "Stale", "Missing", "Status"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for c in calls:
        cells = ([c["project"]] if with_project else []) + [
            c["set"], model_name(c["model"]), f"{c['answered']}/{c['expected']}", str(c["failed"]), str(c["stale"]),
            str(c["missing"]), c["status"]]
        lines.append("| " + " | ".join(cells) + " |")
    return lines if calls else ["No calls."]


def report_md(doc: dict) -> str:
    """``realism_report.md`` of one project (statistics only; the decision is in realism_summary.md)."""
    models = list(doc["models"])
    lines = [f"# Realism A/B – {doc['project']}", "",
             "Pairwise forced choice per aspect, both orders, models "
             + ", ".join(f"{model_name(k)} (`{v['id']}`)" for k, v in doc["models"].items())
             + " (docs/milestone6.md §6). W = B picked in both orders, L = A in both, T = the pick follows the "
               "position, NC = a call is missing or failed. No decision here: `realism-summary` decides over all "
               "A/B projects after the controls.", "",
             f"Pairs: {len(doc['rows'])} in {len(doc['sets'])} set(s); dropped cameras: {len(doc['dropped'])}; "
             f"skipped pairs: {len(doc['skipped'])}.", "", "## Calls", ""] + calls_lines(doc["calls"])
    for s, st in doc["sets"].items():
        pset = SETS[s]
        lines += ["", f"## {s} ({pset.text})", "",
                  f"{st['pairs']} pairs from {st['rooms']} rooms; consensus of "
                  f"{', '.join(model_name(m) for m in st['consensus_models'])}.", ""]
        lines += stats_table(st, models)
        lines += ["", bias_line(st["position_bias"]), "", "Top decisive cues:"] + cue_lines(st["top_cues"])
        sheets = doc["contact_sheets"].get(s) or []
        if sheets:
            lines += ["", "Contact sheets: " + ", ".join(f"`{n}`" for n in sheets)]
    if doc.get("controls"):
        lines += ["", "## Controls", ""] + controls_lines(doc["controls"], models)
    lines += ["", "## Pairs", "", "| Pair | Room | dEV | " + " | ".join(ASPECTS) + " |",
              "|" + "---|" * (3 + len(ASPECTS))]
    for r in doc["rows"]:
        cells = [r["pair_id"], r.get("room_id") or "-", _fmt(r.get("delta_ev"))]
        for a in ASPECTS:
            per = "/".join(row_outcome(r, m, a) for m in models)
            cells.append(f"{r['consensus'][a]} ({per})")
        lines.append("| " + " | ".join(cells) + " |")
    if doc["dropped"]:
        lines += ["", "## Dropped cameras (ab/cameras_check.json)", ""]
        lines += [f"- {d['cam']}: {d['reason']}" for d in doc["dropped"]]
    if doc["skipped"]:
        lines += ["", "## Skipped pairs", ""] + [f"- {d['set']} {d['cam']}: {d['reason']}" for d in doc["skipped"]]
    if doc["warnings"]:
        lines += ["", "## Warnings", ""] + [f"- {w}" for w in doc["warnings"]]
    return "\n".join(lines) + "\n"


def write_combine(out, doc: dict, sheets: bool = True) -> Path:
    """``realism_ab.json``, ``realism_report.md`` and (``sheets``) the contact sheets of one project."""
    out = Path(out).resolve()
    folder = out / REALISM_DIR
    folder.mkdir(parents=True, exist_ok=True)
    if sheets:
        doc["contact_sheets"] = write_contact_sheets(out, doc, list(doc["models"]))
    path = write_json(folder / REALISM_AB, doc)
    (folder / REPORT_MD).write_text(report_md(doc), encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# realism-summary
# --------------------------------------------------------------------------

def _controls_doc(docs: list[tuple[Path, Optional[dict]]], controls_project: Optional[str], warnings: list):
    if not controls_project:
        warnings.append("no --controls-project given: no controls")
        return None
    for out, doc in docs:
        if doc is not None and controls_project in (doc.get("project"), out.name, str(out)):
            return doc
    path = Path(controls_project)
    doc = read_json(path.resolve() / REALISM_DIR / REALISM_AB) if path.is_dir() else None
    if doc is None:
        warnings.append(f"controls project {controls_project}: no {REALISM_DIR.as_posix()}/{REALISM_AB}")
    return doc


def summarise(outs: Iterable, controls_project: Optional[str], keys: list[str], cfg: Optional[dict] = None) -> dict:
    """``realism_summary.json`` over the projects' ``realism_ab.json`` (§6.1-6.3): pooled A/B sets, decisions."""
    from wenart.vision_check.config import load_config
    cfg = cfg if cfg is not None else load_config()
    rc = realism_cfg(cfg)
    keys = list(keys)
    unknown = [k for k in keys if k not in cfg["models"]]
    if unknown:
        raise C.UsageError(f"model key(s) {unknown} not in check.yaml (known: {', '.join(cfg['models'])})")
    warnings: list[str] = []
    docs: list[tuple[Path, Optional[dict]]] = []
    projects = []
    for out in dict.fromkeys(Path(o).resolve() for o in outs):        # a project given twice counts once
        doc = read_json(out / REALISM_DIR / REALISM_AB)
        docs.append((out, doc))
        if doc is None:
            warnings.append(f"{out.name}: no {REALISM_DIR.as_posix()}/{REALISM_AB} (run realism-combine)")
        projects.append({"project": (doc or {}).get("project") or out.name, "project_out": views.repo_path_text(out),
                         "found": doc is not None, "pairs": len((doc or {}).get("rows") or []),
                         "dropped": len((doc or {}).get("dropped") or [])})
    cdoc = _controls_doc(docs, controls_project, warnings)
    controls = evaluate_controls(cdoc.get("rows") or [], keys, rc) if cdoc else None
    if cdoc is not None and controls is None:
        warnings.append(f"controls project {cdoc.get('project')}: no control pairs")
    signal = dict(controls["signal"]) if controls else {k: False for k in keys}
    measurable = any(signal.values())
    cons_models = [k for k in keys if signal.get(k)] if measurable else list(keys)
    single = measurable and len(cons_models) == 1
    notes = list(controls["notes"]) if controls else []
    if not measurable:
        notes.append("not measurable: the controls fail for every model" if controls else
                     "not measurable: no controls")
    elif single:
        notes.append(f"consensus from {model_name(cons_models[0])} alone (single_model)")
    all_rows = [r for _, doc in docs if doc for r in doc.get("rows") or []]
    by_set = _by_set(all_rows)
    sets = {}
    for s in AB_SETS:
        rows = by_set.get(s)
        if not rows:
            continue
        st = set_stats(rows, keys, cons_models, rc)
        decision, per_aspect = decide(st, measurable, rc)
        for a in ASPECTS:
            st["aspects"][a]["decision"] = per_aspect[a]
        st["decision"] = decision
        st["single_model"] = single
        st["projects"] = sorted({r["project"] for r in rows})
        sets[s] = st
    t = rc["targets"]
    flag_active = bool(controls and controls["sets"][NUISANCE_SET]["flag"])
    flagged = [{"project": r["project"], "pair_id": r["pair_id"], "delta_ev": r["delta_ev"]}
               for s in AB_SETS for r in by_set.get(s, [])
               if r.get("delta_ev") is not None and abs(r["delta_ev"]) > float(t["delta_ev_flag"])]
    models_info = {}
    for k in keys:
        mc = cfg["models"][k]
        models_info[k] = {"id": mc["id"], "slug": mc["slug"],
                          "answered_by": sorted({(doc["models"].get(k) or {}).get("model") or "-"
                                                 for _, doc in docs if doc})}
    return {
        "schema_version": "0.1", "kind": "realism_summary", "projects": projects,
        "controls_project": (cdoc or {}).get("project") or controls_project, "models": models_info,
        "controls": controls, "signal": signal, "measurable": measurable, "single_model": single,
        "consensus_models": cons_models, "sets": sets,
        "position_bias": {k: position_bias(all_rows, k) for k in keys},
        "ev_flags": {"active": flag_active, "threshold": float(t["delta_ev_flag"]), "pairs": flagged},
        "top_cues": {s: st["top_cues"] for s, st in sets.items()},
        "calls": [c for _, doc in docs if doc for c in doc.get("calls") or []],
        "config": {k: rc[k] for k in ("min_decisive", "min_rooms", "alpha", "bootstrap_resamples", "bootstrap_seed")},
        "notes": notes, "warnings": warnings,
    }


def summary_md(summary: dict) -> str:
    """``realism_summary.md``: the decision table of §6.3 per set, controls, position bias, dEV flags, cues."""
    keys = list(summary["models"])
    cfg = summary["config"]
    found = [p for p in summary["projects"] if p["found"]]
    lines = ["# Realism A/B summary", "",
             "Pairwise forced choice per aspect, both orders, two models (docs/milestone6.md §6). W = B picked in "
             "both orders, L = A in both, T = the pick follows the position, NC = a call failed. Decision rule: "
             f"consensus `photo` W > L with sign p < {cfg['alpha']}, >= {cfg['min_decisive']} decisive pairs from >= "
             f"{cfg['min_rooms']} rooms, room-level net-win interval above 0, no aspect significantly worse "
             "(better; swapped: worse); controls failing for every model: not_measurable; else "
             "no_detectable_difference.", "",
             f"Projects: {', '.join(p['project'] for p in found) or 'none'}"
             + (f" (missing: {', '.join(p['project'] for p in summary['projects'] if not p['found'])})"
                if len(found) < len(summary["projects"]) else "")
             + f". Controls: {summary['controls_project'] or '-'}. Models: "
             + ", ".join(f"{model_name(k)} (`{v['id']}`)" for k, v in summary["models"].items()) + ".",
             "Signal: " + ", ".join(f"{model_name(k)} {'yes' if ok else 'no'}" for k, ok in summary["signal"].items())
             + f"; consensus of {', '.join(model_name(k) for k in summary['consensus_models'])}"
             + (" (single_model)." if summary["single_model"] else "."), "",
             "| Set | Decision | Single model | Pairs | Rooms | Projects |", "|---|---|---|---|---|---|"]
    for s, st in summary["sets"].items():
        lines.append(f"| {s} | **{st['decision']}** | {'yes' if st['single_model'] else 'no'} | {st['pairs']} | "
                     f"{st['rooms']} | {', '.join(st['projects'])} |")
    if not summary["sets"]:
        lines.append("| - | no A/B pairs | - | 0 | 0 | - |")
    for s, st in summary["sets"].items():
        lines += ["", f"## {s}: {st['decision']} ({SETS[s].text})", ""] + stats_table(st, keys)
        lines += ["", "Per aspect: " + ", ".join(f"{a} {st['aspects'][a]['decision']}" for a in ASPECTS) + ".",
                  "Rooms (consensus per room W/L/T): " + ", ".join(
                      f"{a} {st['aspects'][a]['rooms']['W']}/{st['aspects'][a]['rooms']['L']}/"
                      f"{st['aspects'][a]['rooms']['T']} (p {_fmt_p(st['aspects'][a]['rooms_sign_p'])})"
                      for a in ASPECTS) + ".",
                  "", bias_line(st["position_bias"]), "", "Top decisive cues:"] + cue_lines(st["top_cues"])
    lines += ["", f"## Controls ({summary['controls_project'] or '-'})", ""] + controls_lines(summary["controls"], keys)
    lines += ["", "## Position bias", "", bias_line(summary["position_bias"])]
    ev = summary["ev_flags"]
    lines += ["", "## dEV flags", ""]
    if not ev["active"]:
        lines.append(f"Not active (the nuisance control did not show a brightness preference above the target); "
                     f"{len(ev['pairs'])} A/B pair(s) have |dEV| > {ev['threshold']}.")
    elif ev["pairs"]:
        lines.append(f"Active: the A/B pairs with |dEV| > {ev['threshold']} (B brighter when > 0):")
        lines += [f"- {p['project']} {p['pair_id']}: dEV {p['delta_ev']:+.2f}" for p in ev["pairs"]]
    else:
        lines.append(f"Active, but no A/B pair has |dEV| > {ev['threshold']}.")
    lines += ["", "## Calls", ""] + calls_lines(summary["calls"], with_project=True)
    if summary["notes"]:
        lines += ["", "## Notes", ""] + [f"- {n}" for n in summary["notes"]]
    if summary["warnings"]:
        lines += ["", "## Warnings", ""] + [f"- {w}" for w in summary["warnings"]]
    return "\n".join(lines) + "\n"


def write_summary(dest, summary: dict) -> Path:
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    path = write_json(dest / SUMMARY_JSON, summary)
    (dest / SUMMARY_MD).write_text(summary_md(summary), encoding="utf-8")
    return path
