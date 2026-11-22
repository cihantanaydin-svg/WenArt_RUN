"""RL pilot of the AI checks' vision model (22 Nov 2026; user: "Yes, prepare it"; the pod itself needs a separate OK).

What (the CPU side of ``scripts/jobs/rl_pilot.sh``):

- ``python -m wenart.reading_check rl_pilot build [--out DIR]``: the training questions, verifiable against the
  synthetic projects' exact truth (``results/reading_truth/synthetic-*``) on close-up crops of their drawing images
  (``results/critic/inputs/synth/``, the RC15 input set): ``opening_kind`` (a marked place on a wall line: door,
  window, opening or wall), ``room_window`` (does the marked room have a window), ``stair_here`` (is the marked place
  on a stair), ``room_here`` (is the marked place inside a room closed by drawn walls); each with a short JSON answer.
  Deterministic; the split by project (``held_project``): the held-out synthetic projects are never trained on. Writes
  ``questions.jsonl`` and the crops (``crops/``), and prints the counts.
- ``sample`` (pod): every training question asked ``N_SAMPLES`` times (vLLM's OpenAI server, ``n``, temperature
  ``TEMPERATURE``, short JSON), each answer verified (``verify``) -> ``samples.jsonl``.
- ``filter``: rejection sampling: the correct answers of the questions answered neither all right nor all wrong
  (``keep_question``) -> ``sft.jsonl`` (TRL prompt-completion rows with the crop), at most ``KEEP_PER_QUESTION`` per
  question.
- ``train`` (pod): a LoRA on the BF16 base of the agent model (TRL ``SFTTrainer``, PEFT ``LoraConfig``) -> the adapter.
- ``heldout`` (pod): the held-out synthetic questions once each, temperature 0, base or LoRA -> accuracy.
- ``fewshot``: the zero-training arm's examples: the user's marks (``results/critic/user_marks.json``) in two folds;
  each fold's examples are shown while the other fold is examined (never examined on its own examples).

The exam (never trained on): the RC15 calls on the real readings (``critic ask``) with the LoRA served beside the
base model (``CRITIC_SERVED_MODEL``), scored on the CPU by ``critic calibrate`` against the user's marks and
``known_errors.json``; today's numbers: 66 of 73 known errors found, 11 false findings, the judge 51 of 62.

Library versions (checked on PyPI on 22 Nov 2026, each at least a week old): trl 1.17.1 (30 Oct; requires
transformers>=4.56.2, accelerate>=1.11.0, datasets>=4.7.0), peft 0.21.3 (13 Nov), vLLM 0.30.0 (the project's pinned
server, ``scripts/pod_setup_recognition.sh``; ``--enable-lora``, ``--lora-modules name=path``, ``--max-lora-rank`` from
its docs at the v0.30.0 tag), transformers 5.18.0 (the project's pin; TRL's vision assistant-only loss needs >= 5.18.0).
TRL 1.17.1: a VLM dataset has an ``images`` column and conversational ``prompt``/``completion`` messages whose content
is a list of ``{"type": "image"}`` / ``{"type": "text"}``; ``SFTConfig(max_length=None)`` keeps the image tokens;
prompt-completion rows train on the completion only by default.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parents[2]
INPUTS = REPO / "results" / "critic" / "inputs"
TRUTH_DIR = REPO / "results" / "reading_truth"
MARKS = REPO / "results" / "critic" / "user_marks.json"
N_SAMPLES = 8
TEMPERATURE = 0.8
MAX_TOKENS = 24
KEEP_PER_QUESTION = 2
HOLD_EVERY = 4                # every fourth synthetic project (by a stable hash) is held out of training
CROP_M = 6.0                  # a crop shows this many metres around its point (rooms: their box and a margin)
CROP_PX = 512
OPENING_TYPES = ("door", "window", "opening")
WALL_CLEAR_M = 0.9            # a negative 'wall' point lies this far from every opening
WALL_MIN_M = 1.2
WINDOW_ON_ROOM_M = 0.45       # a window this near a room's boundary is that room's
STAIR_IN_ROOM_M = 0.6
OUTSIDE_M = 1.5               # a 'not in a room' point: this far outside the walls' hull
SEED = 20261122

PROMPTS = {
    "opening_kind": ("A close-up of an architectural floor plan. The red circle marks a place on a wall line. What is "
                     "drawn there: a door (a leaf or swing), a window (glass lines in the wall), an opening (a gap with "
                     "nothing in it) or a solid wall? Answer only JSON: {\"answer\": \"door\" | \"window\" | "
                     "\"opening\" | \"wall\"}"),
    "room_window": ("A close-up of an architectural floor plan. The red circle marks a room. Does that room have at "
                    "least one window in its walls (glass lines drawn in a wall, not a door)? Answer only JSON: "
                    "{\"answer\": true | false}"),
    "stair_here": ("A close-up of an architectural floor plan. Is the red circle on a stair (treads drawn as parallel "
                   "lines, a flight or a landing)? Answer only JSON: {\"answer\": true | false}"),
    "room_here": ("A close-up of an architectural floor plan. Is the red circle inside a room closed by drawn walls "
                  "(doors and windows close a room too), not outside the building? Answer only JSON: {\"answer\": true "
                  "| false}"),
}


# --- the questions (pure but for the image crops) -------------------------------------------------------------------

def held_project(project: str) -> bool:
    """A held-out synthetic project (a stable sha1 hash): never trained on, examined only."""
    return int(hashlib.sha1(project.encode("utf-8")).hexdigest(), 16) % HOLD_EVERY == 0


def _seg_dist(p, a, b) -> float:
    ax, ay, bx, by = map(float, (a[0], a[1], b[0], b[1]))
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 <= 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2))
    return math.hypot(p[0] - (ax + t * dx), p[1] - (ay + t * dy))


def _poly_dist(p, poly) -> float:
    return min(_seg_dist(p, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))


def _inside(p, poly) -> bool:
    x, y = p
    c = False
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / ((y2 - y1) or 1e-12):
            c = not c
    return c


def level_questions(project: str, level: str, tl: dict) -> list:
    """The questions of one truth level (pure): ``{id, project, level, kind, at, crop_m, answer}``; the id is stable."""
    qs = []
    ops = [(t, o) for t in ("doors", "windows", "openings") for o in tl.get(t) or [] if not o.get("absent")
           and o.get("center") and not o.get("virtual")]

    def q(kind, at, answer, crop_m=CROP_M, ref=None):
        qid = f"{project}|{level}|{kind}|{at[0]:.2f},{at[1]:.2f}"
        qs.append({"id": qid, "project": project, "level": level, "kind": kind, "at": [round(at[0], 3), round(at[1], 3)],
                   "crop_m": round(crop_m, 2), "answer": answer, "ref": ref})

    for t, o in ops:
        q("opening_kind", o["center"], {"doors": "door", "windows": "window", "openings": "opening"}[t], ref=o.get("id"))
    for w in tl.get("walls") or []:
        if w.get("absent") or not w.get("start") or not w.get("end"):
            continue
        a, b = w["start"], w["end"]
        if math.dist(a, b) < WALL_MIN_M:
            continue
        mid = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]
        if all(math.dist(mid, o["center"]) >= WALL_CLEAR_M + float(o.get("width") or 0) / 2 for _t, o in ops):
            q("opening_kind", mid, "wall", ref=w.get("id"))
    rooms = [r for r in tl.get("rooms") or [] if not r.get("absent") and r.get("polygon") and r.get("centroid")]
    stairs = [s for s in tl.get("stairs") or [] if not s.get("absent") and s.get("center")]
    windows = [o for t, o in ops if t == "windows"]
    for r in rooms:
        poly = [tuple(map(float, p)) for p in r["polygon"]]
        xs, ys = [p[0] for p in poly], [p[1] for p in poly]
        side = max(max(xs) - min(xs), max(ys) - min(ys)) + 2.0
        c = tuple(map(float, r["centroid"]))
        if not _inside(c, poly):                      # an L-shaped room: its centroid may lie outside it
            continue
        has = any(_poly_dist(tuple(map(float, w["center"])), poly) <= WINDOW_ON_ROOM_M for w in windows)
        q("room_window", c, bool(has), crop_m=max(CROP_M, side), ref=r.get("id"))
        q("room_here", c, True, ref=r.get("id"))
        on_stair = any(math.dist(c, s["center"]) <= STAIR_IN_ROOM_M for s in stairs)
        if not on_stair and str(r.get("room_type") or "") != "stair":
            q("stair_here", c, False, ref=r.get("id"))
    for s in stairs:
        q("stair_here", s["center"], True, ref=s.get("id"))
    # points outside the building: beyond the rooms' box by OUTSIDE_M, on the four sides
    pts = [tuple(map(float, p)) for r in rooms for p in r["polygon"]]
    if pts:
        x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
        y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
        for at in (((x0 + x1) / 2, y0 - OUTSIDE_M), ((x0 + x1) / 2, y1 + OUTSIDE_M),
                   (x0 - OUTSIDE_M, (y0 + y1) / 2), (x1 + OUTSIDE_M, (y0 + y1) / 2)):
            if not any(_inside(at, [tuple(map(float, p)) for p in r["polygon"]]) for r in rooms):
                q("room_here", at, False)
    return qs


def verify(question: dict, text: str) -> Optional[bool]:
    """True / False when the answer ``text`` (the model's JSON, maybe fenced) is right / wrong against the truth, None
    when it gives no answer (pure)."""
    ans = parse_answer(text)
    if ans is None:
        return None
    want = question["answer"]
    if isinstance(want, bool):
        return isinstance(ans, bool) and ans == want
    return isinstance(ans, str) and ans.strip().lower() == str(want)


def parse_answer(text: str):
    t = (text or "").strip()
    if "</think>" in t:
        t = t.split("</think>")[-1]
    t = t.strip().strip("`")
    if t.lower().startswith("json"):
        t = t[4:]
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j <= i:
        return None
    try:
        return json.loads(t[i:j + 1]).get("answer")
    except (ValueError, AttributeError):
        return None


def keep_question(results: list) -> bool:
    """Rejection sampling keeps a question whose samples were neither all right nor all wrong (pure; an unparsed
    answer is wrong)."""
    ok = [bool(r) for r in results]
    return 0 < sum(ok) < len(ok)


def sft_rows(questions: dict, samples: list, keep_per_question: int = KEEP_PER_QUESTION) -> tuple:
    """``(rows, report)``: TRL prompt-completion rows (the crop path in ``images``) of the verified answers of the
    kept questions (pure). ``samples``: ``[{id, answers: [text], verified: [bool|None]}]``."""
    rows, report = [], {"questions": 0, "all_right": 0, "all_wrong": 0, "kept": 0, "rows": 0}
    for s in samples:
        q = questions.get(s["id"])
        if q is None or held_project(q["project"]):
            continue
        report["questions"] += 1
        ver = [bool(v) for v in s["verified"]]
        if all(ver):
            report["all_right"] += 1
            continue
        if not any(ver):
            report["all_wrong"] += 1
            continue
        report["kept"] += 1
        seen = set()
        for text, v in zip(s["answers"], ver):
            norm = json.dumps({"answer": parse_answer(text)})
            if not v or norm in seen or len(seen) >= keep_per_question:
                continue
            seen.add(norm)
            rows.append({"id": q["id"], "kind": q["kind"], "images": [q["crop"]],
                         "prompt": [{"role": "user", "content": [{"type": "image"},
                                                                {"type": "text", "text": PROMPTS[q["kind"]]}]}],
                         "completion": [{"role": "assistant", "content": [{"type": "text", "text": norm}]}]})
    report["rows"] = len(rows)
    return rows, report


def fewshot_folds(marks: dict, n_folds: int = 2) -> dict:
    """``{fold: {"examples": [mark id], "exam": [mark id]}}`` (pure): the user's marks in ``n_folds`` folds by a
    stable hash; a fold's examples are the other folds' marks, so no arm is examined on an example it was shown."""
    ids = sorted(marks)
    fold_of = {m: int(hashlib.sha1(m.encode("utf-8")).hexdigest(), 16) % n_folds for m in ids}
    return {f: {"examples": [m for m in ids if fold_of[m] != f], "exam": [m for m in ids if fold_of[m] == f]}
            for f in range(n_folds)}


def mark_findings(critic_dir: Path) -> dict:
    """``{finding or question id: its record}`` of the RC15 calibrations and the question sheets (the marks' texts)."""
    found: dict = {}
    for f in sorted(Path(critic_dir).glob("calibration_checks*.json")):
        for x in json.loads(f.read_text(encoding="utf-8")).get("findings") or []:
            found.setdefault(x["id"], x)
    for q in sorted(Path(critic_dir).glob("questions/*/questions.json")):
        for k, v in (json.loads(q.read_text(encoding="utf-8")).get("questions") or {}).items():
            found.setdefault(k, v)
    return found


def fewshot_text(examples: list) -> str:
    """The zero-training arm's block for the system prompt (pure): the architect's past verdicts on findings of the
    same kinds, one line each, the finding's text cut to 140 characters."""
    lines = ["Past verdicts of the architect on findings like yours (learn what counts as a real error):"]
    for e in examples:
        verdict = "a real error of the reading (the finding was right)" if e["right"] else \
            "not an error (the reading was right, the finding was wrong)"
        lines.append(f"- {e['kind']}: {str(e['description'])[:140]} -> {verdict}")
    return "\n".join(lines)


def fewshot_files(out: Path, marks: Optional[dict] = None, critic_dir: Optional[Path] = None) -> dict:
    """``out/fewshot_fold<k>.json`` per fold: ``{examples: [{id, kind, description, right}], exam: [mark ids]}``."""
    critic_dir = critic_dir or MARKS.parent
    marks = marks if marks is not None else json.loads(MARKS.read_text(encoding="utf-8")).get("marks") or {}
    found = mark_findings(critic_dir)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    res = {}
    for k, f in fewshot_folds(marks).items():
        ex = [{"id": m, "kind": (found.get(m) or {}).get("kind"), "description": (found.get(m) or {}).get("description"),
               "right": bool(marks[m].get("right"))} for m in f["examples"] if m in found]
        doc = {"fold": k, "examples": ex, "exam": f["exam"], "text": fewshot_text(ex)}
        (out / f"fewshot_fold{k}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                                                  encoding="utf-8")
        res[k] = {"examples": len(ex), "exam": len(f["exam"])}
    return res


# --- building (CPU) -------------------------------------------------------------------------------------------------

def synth_entries(inputs: Path = INPUTS) -> list:
    idx = json.loads((inputs / "index.json").read_text(encoding="utf-8"))
    return [e for e in idx["entries"] if e.get("set") == "synth"]


def build(out: Path, inputs: Path = INPUTS, truth_dir: Path = TRUTH_DIR) -> dict:
    """The training set (the module docstring): ``out/questions.jsonl``, ``out/crops/*.jpg``, ``out/manifest.json``."""
    from PIL import Image

    from wenart.reading_check.critic import metres_to_norm
    from wenart.reading_check.critic_checks import _crop

    out = Path(out)
    (out / "crops").mkdir(parents=True, exist_ok=True)
    allq = []
    for e in synth_entries(inputs):
        tp = truth_dir / f"{e['project']}.json"
        if not tp.is_file():
            continue
        truth = json.loads(tp.read_text(encoding="utf-8"))
        tl = (truth.get("per_level") or {}).get(e["level"])
        if not tl:
            continue
        im = Image.open(inputs / e["folder"] / e["drawing"]).convert("RGB")
        w, h = im.size
        # pixels per metre of this panel (two points one metre apart, through the panel's frame)
        a = metres_to_norm(0.0, 0.0, e["box"], e["tf"])
        b = metres_to_norm(1.0, 0.0, e["box"], e["tf"])
        ppm = math.hypot((b[0] - a[0]) * w, (b[1] - a[1]) * h)
        for q in level_questions(e["project"], e["level"], tl):
            nx, ny = metres_to_norm(q["at"][0], q["at"][1], e["box"], e["tf"])
            if not (0.0 <= nx <= 1.0 and 0.0 <= ny <= 1.0):
                continue
            name = hashlib.sha1(q["id"].encode("utf-8")).hexdigest()[:16] + ".jpg"
            crop = _crop(im, (nx, ny), max(64, int(q["crop_m"] * ppm)), CROP_PX)
            crop.save(out / "crops" / name, quality=88)
            q["crop"] = f"crops/{name}"
            q["held_out"] = held_project(q["project"])
            allq.append(q)
    with open(out / "questions.jsonl", "w", encoding="utf-8") as fh:
        for q in allq:
            fh.write(json.dumps(q, ensure_ascii=False) + "\n")
    counts: dict = {}
    for q in allq:
        k = (q["kind"], "held" if q["held_out"] else "train", str(q["answer"]))
        counts["|".join(k)] = counts.get("|".join(k), 0) + 1
    bytes_ = sum(p.stat().st_size for p in (out / "crops").glob("*.jpg"))
    manifest = {"questions": len(allq), "train": sum(1 for q in allq if not q["held_out"]),
                "held_out": sum(1 for q in allq if q["held_out"]),
                "projects_held_out": sorted({q["project"] for q in allq if q["held_out"]}),
                "projects_train": sorted({q["project"] for q in allq if not q["held_out"]}),
                "counts": dict(sorted(counts.items())), "crops_mb": round(bytes_ / 1e6, 1),
                "samples_per_question": N_SAMPLES, "calls": sum(1 for q in allq if not q["held_out"]) * N_SAMPLES}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    return manifest


def load_questions(path: Path) -> dict:
    out = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            q = json.loads(line)
            out[q["id"]] = q
    return out


# --- the pod side (vLLM's OpenAI server; TRL + PEFT) ----------------------------------------------------------------

def chat_url(url: str) -> str:
    """The chat completions route of an OpenAI server given as ``http://host:port`` or ``http://host:port/v1`` (pure)."""
    root = url.rstrip("/")
    return (root[:-3] if root.endswith("/v1") else root) + "/v1/chat/completions"


def _image_url(path: Path) -> str:
    import base64
    return "data:image/jpeg;base64," + base64.b64encode(Path(path).read_bytes()).decode("ascii")


def sample(train_dir: Path, url: str, model: str, out: Path, *, n: int = N_SAMPLES, temperature: float = TEMPERATURE,
           held_out: bool = False, workers: int = 16, deadline: Optional[float] = None) -> dict:
    """Ask every (training, or with ``held_out`` every held-out) question ``n`` times; verify; ``out`` (jsonl)."""
    import concurrent.futures as cf
    import time
    import urllib.request

    qs = [q for q in load_questions(Path(train_dir) / "questions.jsonl").values() if bool(q["held_out"]) == held_out]

    def one(q):
        if deadline and time.time() > deadline:
            return {"id": q["id"], "answers": [], "verified": [], "skipped": "deadline"}
        body = {"model": model, "n": n, "temperature": temperature, "max_tokens": MAX_TOKENS, "seed": SEED,
                "messages": [{"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": _image_url(Path(train_dir) / q["crop"])}},
                    {"type": "text", "text": PROMPTS[q["kind"]]}]}],
                "chat_template_kwargs": {"enable_thinking": False}}
        # 22 Nov 2026 (pod 1p2wukgcbep0d8: 763 of 763 calls "HTTP Error 404"): ``servers.server`` yields the ``/v1``
        # base URL; the route goes on the server's root
        req = urllib.request.Request(chat_url(url), data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.loads(r.read())
            texts = [c["message"]["content"] or "" for c in data["choices"]]
        except Exception as exc:                           # a failed call is a result
            return {"id": q["id"], "answers": [], "verified": [], "error": str(exc)[:200]}
        return {"id": q["id"], "kind": q["kind"], "answers": texts, "verified": [verify(q, t) for t in texts]}

    res = []
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(one, qs):
            res.append(r)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        for r in res:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    done = [r for r in res if r.get("verified")]
    right = sum(sum(bool(v) for v in r["verified"]) for r in done)
    total = sum(len(r["verified"]) for r in done)
    per: dict = {}
    for r in done:
        k = r.get("kind")
        a = per.setdefault(k, [0, 0])
        a[0] += sum(bool(v) for v in r["verified"])
        a[1] += len(r["verified"])
    return {"questions": len(qs), "answered": len(done), "accuracy": round(right / total, 4) if total else None,
            "per_kind": {k: round(a / b, 4) for k, (a, b) in per.items()}}


EXAM_SETS = "before,after,synth,judge"                      # today's numbers were measured on these (critic.sh)
EXAM_WHICH = "plausibility,inventory,compare,judge,second"
LORA_NAME = "wenart-rs"


def _exam(url: str, key: str, out: Path, served: Optional[str] = None, fewshot: Optional[Path] = None,
          deadline: Optional[float] = None, workers: int = 8) -> dict:
    """One exam arm: the RC15 calls of today's measurement asked at ``url`` (``critic.ask``), the LoRA by its served
    name, the few-shot block by its fold file; scored afterwards on the CPU (``critic calibrate``)."""
    import os

    from wenart.agent import model as AM
    from wenart.reading_check import critic as CR

    old = {k: os.environ.get(k) for k in ("CRITIC_SERVED_MODEL", "CRITIC_FEWSHOT")}
    try:
        for k, v in (("CRITIC_SERVED_MODEL", served), ("CRITIC_FEWSHOT", str(fewshot) if fewshot else None)):
            if v:
                os.environ[k] = v
            else:
                os.environ.pop(k, None)
        model = AM.from_check_yaml(url, key, timeout_s=900.0, parallel=workers)
        if served:
            model.model = served
        res = CR.ask(CR.load_index(), model, CR.INPUTS_DIR, Path(out), deadline=deadline,
                     sets=EXAM_SETS.split(","), which=tuple(EXAM_WHICH.split(",")))
        return res.get("stats") or {}
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def phase_sample(train_dir: Path, out: Path, *, key: str = "agent", server_flags: str = "",
                 deadline: Optional[float] = None, fewshot: Optional[Path] = None, log=print) -> dict:
    """Pod phase A (the FP8 agent model): the training questions ``N_SAMPLES`` times at ``TEMPERATURE``, the held-out
    synthetic questions once at temperature 0 (the base number), then the zero-training arm's exam (``fewshot``)."""
    import time

    from wenart.run import servers as SV

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rep: dict = {}
    with SV.server(key, deadline, extra_flags=server_flags) as url:
        model = SV.model_entry(SV.check_models(), key)["id"]
        rep["train"] = sample(train_dir, url, model, out / "samples.jsonl", deadline=deadline)
        log(f"rl_pilot: sampled {rep['train']}")
        rep["held_base_fp8"] = sample(train_dir, url, model, out / "held_base_fp8.jsonl", n=1, temperature=0.0,
                                      held_out=True, deadline=deadline)
        log(f"rl_pilot: held-out base (fp8) {rep['held_base_fp8']}")
        if fewshot is not None and (deadline is None or deadline - time.time() > 900):
            rep["exam_fewshot"] = _exam(url, key, out / "exam_fewshot", fewshot=fewshot, deadline=deadline)
            log(f"rl_pilot: few-shot exam {rep['exam_fewshot']}")
    (out / "phase_sample.json").write_text(json.dumps(rep, indent=1) + "\n", encoding="utf-8")
    return rep


def phase_exam(train_dir: Path, adapter: Path, out: Path, *, key: str = "bakeoff.bf16", rank: int = 16,
               server_flags: str = "", deadline: Optional[float] = None, log=print) -> dict:
    """Pod phase C: the BF16 base with the LoRA beside it (``--enable-lora --max-lora-rank --lora-modules``, vLLM
    0.30.0): the held-out synthetic questions with the LoRA and with the base, the exam with the LoRA, then (time
    left) the exam with the BF16 base alone as the control."""
    import time

    from wenart.run import servers as SV

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    flags = f"{server_flags} --enable-lora --max-lora-rank {int(rank)} --lora-modules {LORA_NAME}={adapter}".strip()
    rep: dict = {}
    with SV.server(key, deadline, extra_flags=flags) as url:
        base = SV.model_entry(SV.check_models(), key)["id"]
        rep["held_lora"] = sample(train_dir, url, LORA_NAME, out / "held_lora.jsonl", n=1, temperature=0.0,
                                  held_out=True, deadline=deadline)
        rep["held_base_bf16"] = sample(train_dir, url, base, out / "held_base_bf16.jsonl", n=1, temperature=0.0,
                                       held_out=True, deadline=deadline)
        log(f"rl_pilot: held-out lora {rep['held_lora']} base {rep['held_base_bf16']}")
        rep["exam_lora"] = _exam(url, key, out / "exam_lora", served=LORA_NAME, deadline=deadline)
        log(f"rl_pilot: lora exam {rep['exam_lora']}")
        if deadline is None or deadline - time.time() > 900:
            rep["exam_base_bf16"] = _exam(url, key, out / "exam_base_bf16", deadline=deadline)
            log(f"rl_pilot: bf16 base exam {rep['exam_base_bf16']}")
    (out / "phase_exam.json").write_text(json.dumps(rep, indent=1) + "\n", encoding="utf-8")
    return rep


def train(train_dir: Path, base_model: str, revision: str, out: Path, *, epochs: float = 2.0, rank: int = 16,
          lr: float = 1e-4, max_minutes: float = 30.0) -> dict:
    """The LoRA (TRL ``SFTTrainer`` + PEFT ``LoraConfig``) on ``sft.jsonl``; pod only (GPU, the BF16 base)."""
    import torch
    from datasets import Dataset
    from peft import LoraConfig
    from PIL import Image
    from transformers import AutoModelForImageTextToText, AutoProcessor
    from trl import SFTConfig, SFTTrainer

    rows = [json.loads(x) for x in (Path(train_dir) / "sft.jsonl").read_text(encoding="utf-8").splitlines() if x]
    ds = Dataset.from_list([{"prompt": r["prompt"], "completion": r["completion"],
                             "images": [Image.open(Path(train_dir) / p).convert("RGB") for p in r["images"]]}
                            for r in rows])
    processor = AutoProcessor.from_pretrained(base_model, revision=revision)
    model = AutoModelForImageTextToText.from_pretrained(base_model, revision=revision, dtype=torch.bfloat16,
                                                        device_map="auto")
    cfg = SFTConfig(output_dir=str(out), num_train_epochs=epochs, per_device_train_batch_size=1,
                    gradient_accumulation_steps=8, learning_rate=lr, lr_scheduler_type="cosine", warmup_ratio=0.05,
                    bf16=True, gradient_checkpointing=True, max_length=None, logging_steps=5, save_strategy="no",
                    report_to=[], max_steps=-1, seed=SEED)
    lora = LoraConfig(r=rank, lora_alpha=2 * rank, lora_dropout=0.05, target_modules="all-linear",
                      task_type="CAUSAL_LM")
    trainer = SFTTrainer(model=model, args=cfg, train_dataset=ds, processing_class=processor, peft_config=lora)
    res = trainer.train()
    trainer.save_model(str(out))
    return {"rows": len(rows), "train_loss": float(res.training_loss), "steps": int(res.global_step)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.reading_check rl_pilot", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--out", required=True)
    s = sub.add_parser("sample")
    s.add_argument("--train", required=True)
    s.add_argument("--url", required=True)
    s.add_argument("--model", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--n", type=int, default=N_SAMPLES)
    s.add_argument("--temperature", type=float, default=TEMPERATURE)
    s.add_argument("--held-out", action="store_true")
    s.add_argument("--deadline", type=float, default=None)
    f = sub.add_parser("filter")
    f.add_argument("--train", required=True)
    f.add_argument("--samples", required=True)
    t = sub.add_parser("train")
    t.add_argument("--train", required=True)
    t.add_argument("--base", required=True)
    t.add_argument("--revision", required=True)
    t.add_argument("--out", required=True)
    t.add_argument("--epochs", type=float, default=2.0)
    t.add_argument("--rank", type=int, default=16)
    pa = sub.add_parser("phase-sample")
    pa.add_argument("--train", required=True)
    pa.add_argument("--out", required=True)
    pa.add_argument("--server-flags", default="")
    pa.add_argument("--deadline", type=float, default=None)
    pa.add_argument("--fewshot", default=None)
    pc = sub.add_parser("phase-exam")
    pc.add_argument("--train", required=True)
    pc.add_argument("--adapter", required=True)
    pc.add_argument("--out", required=True)
    pc.add_argument("--server-flags", default="")
    pc.add_argument("--deadline", type=float, default=None)
    pc.add_argument("--rank", type=int, default=16)
    fs = sub.add_parser("fewshot")
    fs.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    if args.cmd == "build":
        print(json.dumps(build(Path(args.out)), indent=1))
        return 0
    if args.cmd == "sample":
        print(json.dumps(sample(Path(args.train), args.url, args.model, Path(args.out), n=args.n,
                                temperature=args.temperature, held_out=args.held_out, deadline=args.deadline)))
        return 0
    if args.cmd == "filter":
        qs = load_questions(Path(args.train) / "questions.jsonl")
        samples = [json.loads(x) for x in Path(args.samples).read_text(encoding="utf-8").splitlines() if x.strip()]
        rows, rep = sft_rows(qs, [s for s in samples if s.get("verified")])
        with open(Path(args.train) / "sft.jsonl", "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(json.dumps(rep))
        return 0 if rows else 1
    if args.cmd == "phase-sample":
        print(json.dumps(phase_sample(Path(args.train), Path(args.out), server_flags=args.server_flags,
                                      deadline=args.deadline, fewshot=Path(args.fewshot) if args.fewshot else None)))
        return 0
    if args.cmd == "phase-exam":
        print(json.dumps(phase_exam(Path(args.train), Path(args.adapter), Path(args.out), rank=args.rank,
                                    server_flags=args.server_flags, deadline=args.deadline)))
        return 0
    if args.cmd == "train":
        print(json.dumps(train(Path(args.train), args.base, args.revision, Path(args.out), epochs=args.epochs,
                               rank=args.rank)))
        return 0
    print(json.dumps(fewshot_files(Path(args.out)), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
