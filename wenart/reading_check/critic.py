"""RC15, the vision critic of the reading check (6 Nov 2026, Milestone 14 R6; user, 4 Nov 2026: "some AI or something
else to give the feedbacks by itself instead of me at some point").

What: the project's vision model (``check.yaml models.agent``, Qwen3.8-27B-FP8; ``qwen`` for comparison) looks at two
images of every level of a reading, drawn from the reading's own comparison sheet (``reading_check.sheets``): image 1
the source drawing without its grid and dimensions, image 2 the model in the drawing's orientation, both in the same
frame. It is asked, as an architect would be, where the model differs from the drawing (a wall missing or invented, a
recess or balcony closed into a room, rooms merged or split, a door read as a window, an opening missing or invented, a
stair missing or false, a wrong label), each with a point in image 1, a description and a confidence; and then the
reading lessons' question bank (the lessons of the areas reading and plan, ``reading_questions``), each answered ok,
problem (with a point) or cannot_see. Every point comes back from the image into building metres through the sheet's
own frame (the region box and the inverse page transform), so a finding can be matched with the truth, with the user's
correction records and with the elements of the reading.

Why: the code reviewer RC14 is precise on the error classes the user taught it and caught 1 of 11 synthetic failure
classes out of sample. A model that compares the drawing with the model may generalise where rules do not; it must be
measured before it is trusted (docs/milestone14.md §3 R6: "Calibration before trust").

How:
- ``prepare``: the two images per level as JPEGs under ``results/critic/inputs/<set>/<project>/`` with ``index.json``
  (the frame of every image: the level, the region box, the page transform, the image size), committed, so the pod
  (which clones the repository) needs no reading. Readings are read on the CPU and may be deleted after this.
- ``ask``: the pod job (``scripts/jobs/critic.sh``) serves the model with ``wenart.run.servers`` and asks two calls per
  level (differences, questions) with ``wenart.agent.model`` (temperature 0, a strict JSON schema, thinking off), up to
  the server's sequences at once (``map_calls``); every raw answer goes to ``answers.json`` as it arrives, with the
  call log. Nothing new is sent after the deadline. ``--vlm-url`` asks a server someone else started (the CPU preflight
  against ``tests/fakes/fake_vlm.py``).
- ``calibrate`` (CPU, after the pod): precision per kind on the accepted projects (a finding is right when the truth
  disagrees with the reading at that place in the way the finding says: ``score.match``'s unmatched elements within
  ``MATCH_M``), recall of the user's correction records on the readings made before them (same level, within
  ``MATCH_M``, or the same element kind for a record without a place), and the out-of-sample table on the synthetic
  failure classes (caught, missed, false alarm, clean); written to ``models/critic_trust.json``. A kind under
  ``TRUST_MIN`` precision writes its findings as info.
- ``findings(out_dir)``: the stored critic output of a reading (``reading_check/critic.json``, written by ``store``) as
  advisory RC15 findings for ``reading_check.check`` (counted under ``counts["advisory"]``, never in the verdict), the
  trust file applied.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
import os
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parents[2]
CHECK = "RC15"
NAME = "vision critic"
INPUTS_DIR = REPO / "results" / "critic" / "inputs"
TRUST_PATH = Path(__file__).resolve().parent / "models" / "critic_trust.json"
TRUST_MIN = 0.5                # a kind judged right on less than this share of its findings writes them as info
SMALL_SAMPLE = 5               # a kind judged on fewer findings is marked small_sample (reported, not trusted more)
MATCH_M = 1.5                  # a finding and a truth disagreement or a user correction this close in plan are one place
MAX_SIDE = 1600                # the long side of every image sent (the model's image limit, about 1600 px)
JPEG_QUALITY = 82
DPI = 100
DEFAULT_MODEL_KEY = "agent"
CALL_MAX_TOKENS = {"differences": 2048, "questions": 4096}
MAX_FINDINGS = 20              # per level and call (the schema's maxItems; a longer list is a runaway answer)
QUESTION_AREAS = ("reading", "plan")
QUESTION_STATUSES = ("rule", "built", "open")
QUESTION_CHARS = 260           # a lesson's text is cut to its first sentence, at most this long
# The kinds the critic may name (the module docstring); ``other`` for anything else it sees.
KINDS = ("missing_wall", "extra_wall", "closed_open_air", "merged_rooms", "split_room", "door_as_window",
         "window_as_door", "missing_opening", "extra_opening", "missing_stair", "false_stair", "wrong_label", "other")
KIND_TEXT = {
    "missing_wall": "a wall the drawing has and the model lacks",
    "extra_wall": "a wall the model has and the drawing does not draw",
    "closed_open_air": "an open-air space (a recess, a light well, a balcony, a terrace, a court) closed into a room",
    "merged_rooms": "two or more drawn rooms read as one room",
    "split_room": "one drawn room read as two or more rooms",
    "door_as_window": "a drawn door read as a window",
    "window_as_door": "a drawn window read as a door",
    "missing_opening": "a drawn door or window the model lacks",
    "extra_opening": "a door or window the model has where the drawing draws a plain wall",
    "missing_stair": "a drawn stair the model lacks",
    "false_stair": "a stair in the model where the drawing draws none (tiles, a grid, furniture)",
    "wrong_label": "a room whose name or type in the model is not the drawn label",
    "other": "another difference an architect would point out",
}
# How a finding of a kind is judged against the truth (``calibrate``): the element classes of ``score.match`` and the
# side of the disagreement (``truth_only``: the truth has it and the reading lacks it; ``read_only``: the reading has
# it and the truth lacks or negates it; ``label``: a matched room with another label).
KIND_RULES = {
    "missing_wall": (("walls",), ("truth_only",)),
    "extra_wall": (("walls",), ("read_only",)),
    "closed_open_air": (("rooms",), ("read_only",)),
    "merged_rooms": (("rooms",), ("truth_only", "read_only")),
    "split_room": (("rooms",), ("read_only", "truth_only")),
    "door_as_window": (("doors", "windows"), ("truth_only", "read_only")),
    "window_as_door": (("doors", "windows"), ("truth_only", "read_only")),
    "missing_opening": (("doors", "windows", "openings"), ("truth_only",)),
    "extra_opening": (("doors", "windows", "openings"), ("read_only",)),
    "missing_stair": (("stairs",), ("truth_only",)),
    "false_stair": (("stairs",), ("read_only",)),
    "wrong_label": (("rooms",), ("label",)),
    "other": (("rooms", "doors", "windows", "openings", "walls", "stairs"), ("truth_only", "read_only", "label")),
}
# A user correction record's element kind -> the critic kinds that name it (recall of a record without a place).
RECORD_KINDS = {
    "wall": ("missing_wall", "extra_wall", "closed_open_air"),
    "room": ("merged_rooms", "split_room", "closed_open_air", "wrong_label"),
    "region": ("closed_open_air", "merged_rooms", "split_room"),
    "label": ("wrong_label",),
    "door": ("door_as_window", "window_as_door", "missing_opening", "extra_opening"),
    "window": ("door_as_window", "window_as_door", "missing_opening", "extra_opening"),
    "opening": ("door_as_window", "window_as_door", "missing_opening", "extra_opening"),
    "stair": ("missing_stair", "false_stair"),
}
SYSTEM_PROMPT = ("You are a senior architect checking a computer's reading of an architectural floor plan. You answer "
                 "only with the JSON the schema asks for, in simple English. You point only at what you can see.")


# ======================================================================================================== 1. images
def panel_size(box: list, max_side: int = MAX_SIDE) -> tuple[int, int]:
    """``(width, height)`` in pixels of a panel of the region ``box`` (drawing units): the long side ``max_side``, the
    other by the box's aspect, so every pixel is the same length in both directions."""
    w, h = max(1e-9, float(box[2]) - float(box[0])), max(1e-9, float(box[3]) - float(box[1]))
    if w >= h:
        return int(max_side), max(1, int(round(max_side * h / w)))
    return max(1, int(round(max_side * w / h))), int(max_side)


def pixel_to_drawing(px: float, py: float, box: list, size: tuple) -> tuple[float, float]:
    """A pixel of a panel (origin top left) -> drawing units (the box's frame; y up)."""
    w, h = size
    x = float(box[0]) + float(px) / float(w) * (float(box[2]) - float(box[0]))
    y = float(box[3]) - float(py) / float(h) * (float(box[3]) - float(box[1]))
    return x, y


def norm_to_metres(nx: float, ny: float, box: list, tf: list) -> tuple[float, float]:
    """A normalised point of a panel (0-1, origin top left, as the model answers) -> building metres through the
    panel's frame (``box``) and the level's page transform ``tf`` (what the model used: drawing units -> metres)."""
    x = float(box[0]) + float(nx) * (float(box[2]) - float(box[0]))
    y = float(box[3]) - float(ny) * (float(box[3]) - float(box[1]))
    return (tf[0] * x + tf[1] * y + tf[2], tf[3] * x + tf[4] * y + tf[5])


def metres_to_norm(x: float, y: float, box: list, tf: list) -> tuple[float, float]:
    """Building metres -> the normalised point of a panel (the inverse of ``norm_to_metres``)."""
    from wenart.reading_check.sheets import _inverse

    dx, dy = _inverse(tf)(float(x), float(y))
    return ((dx - float(box[0])) / (float(box[2]) - float(box[0])),
            (float(box[3]) - dy) / (float(box[3]) - float(box[1])))


def _figure(box: list, size: tuple):
    """A figure whose one axes fills it exactly and shows ``box``: pixel (0, 0) is the box's top-left corner."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    w, h = size
    fig = plt.figure(figsize=(w / DPI, h / DPI), dpi=DPI)
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    _fit(ax, box)
    return fig, ax


def _fit(ax, box: list) -> None:
    """The axes back to the exact frame (ezdxf's backend and ``sheets._frame`` set an equal aspect that would shrink
    the axes inside the figure; the figure's own aspect already equals the box's, so ``auto`` is equal)."""
    ax.set_position([0.0, 0.0, 1.0, 1.0])
    ax.set_aspect("auto")
    ax.set_xlim(float(box[0]), float(box[2]))
    ax.set_ylim(float(box[1]), float(box[3]))
    ax.axis("off")


def _save(fig, ax, box: list, size: tuple, dest: Path, quality: int = JPEG_QUALITY) -> Path:
    import matplotlib.pyplot as plt
    from PIL import Image

    _fit(ax, box)
    fig.set_size_inches(size[0] / DPI, size[1] / DPI, forward=True)
    tmp = dest.with_suffix(".png")
    fig.savefig(tmp, dpi=DPI, facecolor="white", pad_inches=0)
    plt.close(fig)
    im = Image.open(tmp).convert("RGB")
    if im.size != tuple(size):
        im = im.resize(tuple(size))
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, quality=quality, optimize=True)
    tmp.unlink()
    return dest


def draw_mark(box: list, size: tuple, point_m: tuple, tf: list, dest: Path, radius_px: int = 8) -> Path:
    """A test image: one red dot at ``point_m`` (building metres) in the panel's frame (the mapping is proven when the
    dot's pixels come back to ``point_m``)."""
    fig, ax = _figure(box, size)
    from wenart.reading_check.sheets import _inverse

    dx, dy = _inverse(tf)(*point_m)
    ax.plot([dx], [dy], marker="o", ms=radius_px * 72.0 / DPI * 2, color="#ff0000", mec="#ff0000")
    return _save(fig, ax, box, size, Path(dest), quality=95)


def render_level(out_dir, level_id: str, dest_dir, *, max_side: int = MAX_SIDE, building: Optional[dict] = None,
                 sheets: Optional[dict] = None, docs: Optional[dict] = None, model_style: str = "colour") -> Optional[dict]:
    """The two images of one level (``<dest_dir>/<level>_drawing.jpg``, ``<level>_model.jpg``) in the frame of the
    level's region, drawn with ``reading_check.sheets``' own panel functions; the index entry with the frame, or None
    when the level has no CAD source. ``model_style`` ``arch`` (20 Nov 2026, checks 1, 2, 4): the model drawn like an
    architect's plan (``critic_checks.draw_arch``: black walls, door swings, window symbols, no colour legend)."""
    import ezdxf

    from wenart import reading_check as RC
    from wenart.reading_check import sheets as SH

    out_dir, dest_dir = Path(out_dir), Path(dest_dir)
    building = building or json.loads((out_dir / "building.json").read_text(encoding="utf-8"))
    if sheets is None:
        sp = out_dir / "sheets.json"
        sheets = json.loads(sp.read_text(encoding="utf-8")) if sp.is_file() else {}
    pg = RC.level_pages(building).get(level_id)
    if not pg:
        return None
    regions = {r["id"]: r for r in sheets.get("regions") or []}
    reg = regions.get(pg.get("region"))
    dxf = RC.source_dxf(out_dir, pg["file"])
    if dxf is None or (reg is None and pg.get("region")):
        return None
    docs = docs if docs is not None else {}
    if dxf not in docs:
        docs[dxf] = ezdxf.readfile(str(dxf))
    doc = docs[dxf]
    box = list(reg["box"]) if reg is not None else SH._model_box(building, level_id, pg["tf"])
    if box is None:
        return None
    box = [float(v) for v in box]
    size = panel_size(box, max_side)
    ents = SH._entities(doc, box)
    dest_dir.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", level_id)
    fig, ax = _figure(box, size)
    SH._draw_drawing(ax, doc, ents, box, clean=True)
    drawing = _save(fig, ax, box, size, dest_dir / f"{safe}_drawing.jpg")
    fig, ax = _figure(box, size)
    if model_style == "arch":
        from wenart.reading_check import critic_checks as CC

        CC.draw_arch(ax, building, level_id, pg["tf"])
    else:
        SH._draw_model(ax, building, level_id, pg["tf"], box)
    model = _save(fig, ax, box, size, dest_dir / f"{safe}_model.jpg")
    levels = {lv["id"]: lv for lv in building.get("levels") or []}
    lv = levels.get(level_id) or {}
    title = (((reg or {}).get("title") or {}).get("text") or "").strip()
    rooms = [r for r in building.get("rooms") or [] if r.get("level_id") == level_id]
    return {"level": level_id, "label": lv.get("label"), "title": title, "box": box, "tf": list(pg["tf"]),
            "size": list(size), "drawing": drawing.name, "model": model.name, "model_style": model_style,
            "copies": [k for k, v in levels.items() if v.get("typical_of") == level_id],
            "rooms": len(rooms), "walls": sum(1 for w in building.get("walls") or [] if w.get("level_id") == level_id),
            "labels": sorted({str(r.get("label") or "") for r in rooms if r.get("label")})[:40]}


def prepare(readings: list, dest: Path = INPUTS_DIR, *, max_side: int = MAX_SIDE, levels: Optional[list] = None) -> dict:
    """The input set: ``readings`` = ``[{"set", "project", "tag", "out_dir"}]`` (``tag``: the reading's commit or
    ``current``); every level page of every reading rendered under ``<dest>/<set>/<project>[@tag]/``, the index
    ``<dest>/index.json`` extended (an entry per level; an existing entry of the same id is replaced)."""
    from wenart import reading_check as RC

    dest = Path(dest)
    index_path = dest / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.is_file() else {"entries": []}
    byid = {e["id"]: e for e in index.get("entries") or []}
    for rd in readings:
        out_dir = Path(rd["out_dir"])
        building = json.loads((out_dir / "building.json").read_text(encoding="utf-8"))
        sp = out_dir / "sheets.json"
        sheets = json.loads(sp.read_text(encoding="utf-8")) if sp.is_file() else {}
        name = rd["project"] + (f"@{rd['tag']}" if rd.get("tag") and rd["tag"] != "current" else "")
        folder = dest / rd["set"] / name
        docs: dict = {}
        checks = bool(rd.get("checks"))
        rendered = []
        for lid in RC.level_pages(building):
            if levels and lid not in levels:
                continue
            e = render_level(out_dir, lid, folder, max_side=max_side, building=building, sheets=sheets, docs=docs,
                             model_style="arch" if checks else "colour")
            if e is None:
                continue
            e.update({"id": f"{rd['set']}/{name}/{lid}", "set": rd["set"], "project": rd["project"],
                      "tag": rd.get("tag") or "current", "folder": f"{rd['set']}/{name}",
                      "reading_commit": rd.get("commit"), "failure_class": rd.get("failure_class")})
            byid[e["id"]] = e
            rendered.append(e)
        if checks:
            # 20 Nov 2026 (checks 1, 2, 4): the facts, the compare questions, the floor texts and, for a synthetic
            # project, its exact truth's disagreements, so the pod and the calibration need no reading
            from wenart.reading_check import critic_checks as CC
            from wenart.reading_check import truth as TR

            truth = None
            if rd["project"].startswith("synthetic-"):
                truth = TR.load_truth(rd["project"])
                truth = truth if truth is not None and not TR.is_sparse(truth) else None
            res = CC.prepare_reading(out_dir, building, sheets, rendered, set_name=rd["set"], name=name,
                                     project=rd["project"], truth=truth, vector_dir=folder)
            st: list = []
            for doc in docs.values():                           # the storey texts of the whole drawing file
                st += [t for t in CC.storey_texts(doc) if t not in st]
            for e in rendered:
                e["storey_texts"] = st[:25]
            fkey = f"{rd['set']}/{name}"
            index.setdefault("readings", {})[fkey] = {"bfacts": res["bfacts"], "project": rd["project"],
                                                      "tag": rd.get("tag") or "current", "commit": rd.get("commit"),
                                                      "failure_class": rd.get("failure_class"),
                                                      "exact_truth": truth is not None,
                                                      "truth_levels_missing": CC.truth_levels_missing(truth, building)
                                                      if truth is not None else None}
            index["texts"] = [t for t in index.get("texts") or [] if t["folder"] != fkey] + \
                [dict(t, tag=rd.get("tag") or "current") for t in res["texts"]]
    index["entries"] = sorted(byid.values(), key=lambda e: e["id"])
    index["made"] = _dt.date.today().isoformat()
    index["max_side"] = max_side
    dest.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return index


def load_index(inputs: Path = INPUTS_DIR) -> dict:
    return json.loads((Path(inputs) / "index.json").read_text(encoding="utf-8"))


# ================================================================================================ 2. prompt, schema
def _first_sentence(text: str, limit: int = QUESTION_CHARS) -> str:
    t = re.sub(r"\s+", " ", str(text or "")).strip()
    t = re.sub(r"^\d{1,2} \w{3} 20\d\d \(.*?\):\s*", "", t)          # a dated lead ("4 Nov 2026 (user ...):")
    m = re.search(r"[.;](\s|$)", t[30:])
    if m:
        t = t[:30 + m.start() + 1]
    t = re.sub(r"\s*\((?:user|real\d\d|UL\d)[^)]*$", "", t)            # an unclosed aside the cut left open
    if t.count("(") > t.count(")"):
        t = t[:t.rfind("(")].rstrip()
    t = t[:limit].rstrip(" ,;:(")
    return t + ("" if t.endswith(".") else ".")


def reading_questions(lessons: Optional[list] = None) -> list[dict]:
    """The question bank: every lesson of the areas ``QUESTION_AREAS`` with a status of ``QUESTION_STATUSES`` (a
    process lesson is about how we work); a lesson with its own question asks it, the others ask whether the model
    keeps the lesson's first sentence (pure). ``[{"id": lesson id, "ask"}]``."""
    if lessons is None:
        from wenart.blender import architect_lessons as L
        lessons = L.lessons()
    out = []
    for x in lessons:
        if x.get("area") not in QUESTION_AREAS or x.get("status") not in QUESTION_STATUSES:
            continue
        if x.get("question"):
            ask = str(x["question"]).strip()
        else:
            ask = f"Rule: {_first_sentence(x.get('lesson') or x.get('request'))} Does the model keep this rule here?"
        out.append({"id": x["id"], "ask": ask})
    return out


def _context(entry: dict) -> str:
    bits = [f"level {entry.get('level')}"]
    if entry.get("label"):
        bits.append(f"({entry['label']})")
    if entry.get("title"):
        bits.append(f"titled '{entry['title']}'")
    if entry.get("copies"):
        bits.append(f"(also the plan of {', '.join(entry['copies'])})")
    return " ".join(bits)


def differences_prompt(entry: dict) -> str:
    kinds = "\n".join(f"- {k}: {KIND_TEXT[k]}" for k in KINDS)
    return (f"Image 1 is the architect's source drawing of {_context(entry)}: walls, doors (swing arcs), windows, stairs, "
            f"room labels, without its dimension lines and grid. Image 2 is a computer's model of the same level in "
            f"the same frame: rooms yellow with their labels, balconies and terraces green, walls black (inferred walls "
            f"orange, dashed orange where the computer closed an outline), doors green, windows blue, other openings "
            f"purple, stairs dark blue with arrows, floor voids hatched blue.\n"
            f"Read the legend of image 2 before anything else: a GREEN bar on a wall IS a door (the drawing's swing arc "
            f"is not redrawn), a BLUE bar IS a window, a purple bar is another opening; so a door or window is missing "
            f"only where the wall of image 2 shows no bar at all at that place. The model writes labels in its own "
            f"spelling with the type in brackets ('Salon (living)' for 'salon'): that is the same label, not a "
            f"difference; a label is wrong only when it names another room than the drawing does at that place.\n"
            f"List every place where the model (image 2) differs from the drawing (image 1), as an architect checking a "
            f"junior's work would. Use these kinds:\n{kinds}\n"
            f"For each difference give the point in image 1 as x and y in 0-1000 (0,0 the top-left corner, 1000,1000 the "
            f"bottom-right corner), one short sentence, and your confidence in 0-100. Do not list differences of "
            f"colour, line weight, furniture, text size, spelling or dimensions. An orange wall is only a difference "
            f"when the drawing has no wall line there. Most levels have between zero and three real differences: "
            f"leave the list empty when the model follows the drawing, and never list a difference you are not sure "
            f"of. Up to {MAX_FINDINGS} differences, the surest first.")


def questions_prompt(entry: dict, questions: list) -> str:
    qs = "\n".join(f"- {q['id']}: {q['ask']}" for q in questions)
    return (f"Image 1 is the architect's source drawing of {_context(entry)} (walls, doors, windows, stairs, room labels; "
            f"no dimensions or grid). Image 2 is a computer's model of the same level in the same frame: rooms yellow "
            f"with their labels, balconies and terraces green, walls black (inferred walls orange), doors green, windows "
            f"blue, other openings purple, stairs dark blue.\n"
            f"Answer every question below about the model against the drawing: 'ok' when the model is right there, "
            f"'problem' when it is not (then give the point in image 1 as x and y in 0-1000, 0,0 top-left, and one short "
            f"note), 'cannot_see' when these two images cannot show it (heights, other floors, elevations, sections, "
            f"the site). Answer the questions in the order given, one answer per question id.\n{qs}")


DIFFERENCES_SCHEMA = {
    "type": "object",
    "properties": {
        "findings": {
            "type": "array", "maxItems": MAX_FINDINGS,
            "items": {
                "type": "object",
                "properties": {
                    "kind": {"type": "string", "enum": list(KINDS)},
                    "x": {"type": "integer", "minimum": 0, "maximum": 1000},
                    "y": {"type": "integer", "minimum": 0, "maximum": 1000},
                    "description": {"type": "string", "maxLength": 200},
                    "confidence": {"type": "integer", "minimum": 0, "maximum": 100},
                },
                "required": ["kind", "x", "y", "description", "confidence"],
                "additionalProperties": False,
            },
        },
        "summary": {"type": "string", "maxLength": 300},
    },
    "required": ["findings", "summary"],
    "additionalProperties": False,
}


def questions_schema(questions: list) -> dict:
    ids = [q["id"] for q in questions]
    return {
        "type": "object",
        "properties": {
            "answers": {
                "type": "array", "minItems": len(ids), "maxItems": len(ids),
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "enum": ids},
                        "answer": {"type": "string", "enum": ["ok", "problem", "cannot_see"]},
                        "x": {"type": "integer", "minimum": 0, "maximum": 1000},
                        "y": {"type": "integer", "minimum": 0, "maximum": 1000},
                        "note": {"type": "string", "maxLength": 160},
                    },
                    "required": ["id", "answer", "x", "y", "note"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["answers"],
        "additionalProperties": False,
    }


# ======================================================================================================== 3. client
def _messages(entry: dict, images_root: Path, text: str, max_side: int) -> list:
    from wenart.agent import model as AM

    folder = Path(images_root) / entry["folder"]
    return [{"role": "system", "content": SYSTEM_PROMPT},
            AM.user_message(text, [folder / entry["drawing"], folder / entry["model"]],
                            labels=["Image 1 (the source drawing):", "Image 2 (the computer's model):"],
                            max_side=max_side)]


def _vector(which: str, item: dict, images_root: Path, base_prompt: str, answer_tokens: int, images: list,
            vt: str, chunk: Optional[list] = None) -> Optional[dict]:
    """The vector text of one call (21 Nov 2026, ``vector_text``) under the switch ``vt`` (``0`` none, ``1`` text and
    id tags, ``text`` text only), cut to what the context leaves after the images, the prompt and the answer; None
    when off or when the item has no vector file."""
    from wenart.reading_check import critic_checks as CC
    from wenart.reading_check import vector_text as VT

    if vt not in ("1", "text"):
        return None
    vec = VT.load_vector(images_root, item)
    if vec is None:
        return None
    sizes = [tuple(s) for s in images]
    cap = VT.cap_for(VT.estimate_tokens(CC.SYSTEM_TEXT + base_prompt), answer_tokens, sizes)
    blk = VT.question_block(which, item, vec, cap_tokens=cap, tags=(vt == "1"), chunk=chunk,
                            crop_px=float(CC.SECOND_CROP_PX))
    if blk is not None:
        blk["cap"] = cap
    return blk


def _check_messages(which: str, item: dict, images_root: Path, part: int, max_side: int,
                    marked_dir: Optional[Path], vt: str = "0", meta: Optional[dict] = None) -> tuple:
    """The messages and schema of one call of checks 1, 2, 4 (``critic_checks``): inventory image 1 only, compare both
    images with the chunk's numbered marks (drawn now, into ``marked_dir``), plausibility the floor text only; the
    second look a close-up; the judge (``critic_judge``) two close-ups. ``vt`` (21 Nov 2026): the vector text switch
    of this call (``_vector``); ``meta`` gets its numbers (tokens, items listed and left out, the cap)."""
    from wenart.agent import model as AM
    from wenart.reading_check import critic_checks as CC
    from wenart.reading_check import critic_judge as CJ
    from wenart.reading_check import vector_text as VT

    system = {"role": "system", "content": CC.SYSTEM_TEXT}
    meta = meta if meta is not None else {}
    tags = vt == "1"

    def note(blk):
        if blk is not None:
            meta.update({k: blk.get(k) for k in ("tokens", "listed", "left_out", "cap")})
        return (blk or {}).get("text")

    if which == "plausibility":
        base = CC.plausibility_prompt(item)
        text = note(_vector(which, item, images_root, base, CC.CALL_MAX_TOKENS[which], [], vt))
        return [system, AM.user_message(CC.plausibility_prompt(item, text))], CC.PLAUSIBILITY_SCHEMA
    if which == "second":
        safe = re.sub(r"[^A-Za-z0-9_.-]", "_", item["id"])
        img = CC.second_image(item, images_root, Path(marked_dir or images_root) / "second" / f"{safe}.jpg")
        blk = _vector(which, item, images_root, CC.second_prompt(item), 64, [(CC.SECOND_OUT_PX, CC.SECOND_OUT_PX)], vt)
        text = note(blk)
        if tags and blk and blk.get("tags"):
            img = VT.tag_image(img, blk["tags"], img.with_name(img.stem + "_vt.jpg"), "source")
        return ([system, AM.user_message(CC.second_prompt(item, text), [img], labels=["The close-up:"],
                                         max_side=max_side)], CC.second_schema(item))
    if which == "judge":
        system = {"role": "system", "content": CJ.SYSTEM_TEXT}
        d, m = CJ.images(item, images_root, Path(marked_dir or images_root) / "judge")
        blk = _vector(which, item, images_root, CJ.prompt(item), CJ.MAX_TOKENS, [(CJ.OUT_PX, CJ.OUT_PX)] * 2, vt)
        text = note(blk)
        if tags and blk and blk.get("tags"):
            d = VT.tag_image(d, blk["tags"], d.with_name(d.stem + "_vt.jpg"), "source")
            m = VT.tag_image(m, blk["tags"], m.with_name(m.stem + "_vt.jpg"), "reading")
        return ([system, AM.user_message(CJ.prompt(item, text), [d, m],
                                         labels=["Image 1 (the drawing):", "Image 2 (the computer's model):"],
                                         max_side=max_side)], CJ.schema())
    folder = Path(images_root) / item["folder"]
    size = tuple(item.get("size") or (MAX_SIDE, MAX_SIDE))
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", item["id"])
    if which == "inventory":
        img = folder / item["drawing"]
        blk = _vector(which, item, images_root, CC.inventory_prompt(item), CC.CALL_MAX_TOKENS[which], [size], vt)
        text = note(blk)
        if tags and blk and blk.get("tags"):
            img = VT.tag_image(img, blk["tags"], Path(marked_dir or folder) / "marked" / f"{safe}_inventory_vt.jpg",
                               "source")
        return ([system, AM.user_message(CC.inventory_prompt(item, text), [img],
                                         labels=["The floor plan:"], max_side=max_side)], CC.INVENTORY_SCHEMA)
    chunk = CC.chunks_of(item)[part]
    mdir = Path(marked_dir or folder) / "marked"
    d = CC.mark_image(folder / item["drawing"], chunk, mdir / f"{safe}_{part}_drawing.jpg")
    m = CC.mark_image(folder / item["model"], chunk, mdir / f"{safe}_{part}_model.jpg")
    blk = _vector(which, item, images_root, CC.compare_prompt(item, chunk), CC.CALL_MAX_TOKENS["compare"],
                  [size, size], vt, chunk=chunk)
    text = note(blk)
    if tags and blk and blk.get("tags"):
        d = VT.tag_image(d, blk["tags"], d.with_name(d.stem + "_vt.jpg"), "source")
        m = VT.tag_image(m, blk["tags"], m.with_name(m.stem + "_vt.jpg"), "reading")
    return ([system, AM.user_message(CC.compare_prompt(item, chunk, text), [d, m],
                                     labels=["Image 1 (the source drawing):", "Image 2 (the computer's model):"],
                                     max_side=max_side)], CC.compare_schema(chunk))


def ask_entry(model, entry: dict, images_root: Path, which: str, questions: Optional[list] = None,
              max_side: int = MAX_SIDE, part: int = 0, marked_dir: Optional[Path] = None,
              arm: Optional[str] = None) -> dict:
    """One call for one level: ``which`` ``differences`` or ``questions`` (or, 20 Nov 2026, ``inventory``,
    ``compare`` with its chunk ``part``, ``plausibility`` for a floor text; 21 Nov 2026 ``judge`` for a code check's
    finding); the raw answer with the call's log. ``arm`` (21 Nov 2026): the vector text switch of this call
    (``CRITIC_VECTOR_TEXT``: ``0``, ``1``, ``text``); recorded on the answer with the text's numbers when given."""
    from wenart.reading_check import critic_checks as CC
    from wenart.reading_check import critic_judge as CJ

    meta: dict = {}
    vt = arm or "0"
    if which in CC.CHECKS or which in ("second", "judge"):
        messages, schema = _check_messages(which, entry, images_root, part, max_side, marked_dir, vt=vt, meta=meta)
        max_tokens = CJ.MAX_TOKENS if which == "judge" else CC.CALL_MAX_TOKENS.get(which, 64)
    elif which == "questions":
        questions = questions if questions is not None else reading_questions()
        text, schema = questions_prompt(entry, questions), questions_schema(questions)
        messages, max_tokens = _messages(entry, images_root, text, max_side), CALL_MAX_TOKENS[which]
    else:
        text, schema = differences_prompt(entry), DIFFERENCES_SCHEMA
        messages, max_tokens = _messages(entry, images_root, text, max_side), CALL_MAX_TOKENS[which]
    call_id = f"{which}:{entry['id']}" + (f":{part}" if part else "") + (f"@vt{arm}" if arm else "")
    t0 = time.time()
    reply = model.structured(messages, schema, call_id=call_id, name=f"critic_{which}", kind="critic",
                             max_tokens=max_tokens)
    out = {"id": entry["id"], "which": which, "part": part, "call_id": call_id, "data": reply.data,
           "errors": list(reply.errors), "raw": reply.raw if reply.data is None else "", "usage": reply.usage,
           "seconds": round(time.time() - t0, 1), "attempts": reply.attempts, "model": getattr(model, "model", None)}
    if arm is not None:
        out["arm"] = arm
        if meta:
            out["vector"] = meta
    if which == "second":
        out["item"] = entry                                     # the second look's own question, kept for the scoring
    return out


def check_jobs(index: dict, which: tuple, sets: Optional[list] = None) -> list:
    """``[(which, item, part)]`` of every call in ``which`` (pure): the old calls per level entry, ``inventory`` per
    entry with an architect image, ``compare`` per chunk of an entry's questions, ``plausibility`` per floor text;
    the sets' order kept (the pod's first sets are asked first), every check of a set before the next set."""
    from wenart.reading_check import critic_checks as CC

    entries = [e for e in index.get("entries") or [] if not sets or e.get("set") in sets]
    texts = [t for t in index.get("texts") or [] if not sets or t.get("set") in sets]
    judged = [x for x in index.get("judge") or [] if not sets or x.get("set") in sets]
    order = list(sets) if sets else sorted({e.get("set") for e in entries} | {t.get("set") for t in texts}
                                           | {x.get("set") for x in judged})
    jobs = []
    for s in order:
        for w in which:
            if w == "second":
                continue                                        # asked after the first pass (ask)
            if w == "plausibility":
                jobs += [(w, t, 0) for t in texts if t.get("set") == s]
            elif w == "judge":
                jobs += [(w, x, 0) for x in judged if x.get("set") == s]   # 21 Nov 2026: a code check's finding
            elif w == "inventory":
                jobs += [(w, e, 0) for e in entries if e.get("set") == s and e.get("facts") is not None
                         and not e.get("judge_only")]
            elif w == "compare":
                jobs += [(w, e, k) for e in entries if e.get("set") == s and e.get("facts") is not None
                         and not e.get("judge_only") for k in range(len(CC.chunks_of(e)))]
            else:
                jobs += [(w, e, 0) for e in entries if e.get("set") == s and not e.get("judge_only")]
    return jobs


def split_arms(answers: dict) -> dict:
    """``{arm: answers}`` of an answers file asked with several arms (``ask(arms=...)``; pure): each arm's answers
    with the file's other fields, so every reader of one pod's answers reads one arm."""
    arms = sorted({a.get("arm") for a in answers.get("answers") or [] if a.get("arm") is not None})
    if not arms:
        return {None: answers}
    return {arm: dict(answers, answers=[a for a in answers.get("answers") or [] if a.get("arm") == arm])
            for arm in arms}


def ask(index: dict, model, images_root: Path, out: Path, *, deadline: Optional[float] = None,
        which: tuple = ("differences", "questions"), questions: Optional[list] = None, sets: Optional[list] = None,
        max_side: int = MAX_SIDE, arms: Optional[tuple] = None, log=print) -> dict:
    """Every call of every entry (the differences of every level first, then the questions), up to the model's
    ``parallel`` at once; ``answers.json`` in ``out`` rewritten after every answer; a call is skipped (recorded as
    ``skipped: deadline``) once ``deadline`` (epoch seconds) has passed. ``arms`` (21 Nov 2026, the vector text A/B):
    the ``CRITIC_VECTOR_TEXT`` values to ask every call with, the arms of one call one after the other (a deadline
    cuts both arms at the same question); each answer carries its ``arm``, and ``arm_<value>/answers.json`` holds each
    arm's answers at the end (``split_arms``). None asks once, as before (no ``arm`` on the answers)."""
    from wenart.agent import model as AM

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "answers.json"
    done = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"answers": []}
    arm_list = list(arms) if arms else [None]
    have = {(a["id"], a["which"], a.get("part") or 0, a.get("arm")) for a in done["answers"] if a.get("data") is not None}
    jobs = [(w, e, part, arm) for (w, e, part) in check_jobs(index, which, sets) for arm in arm_list
            if (e["id"], w, part, arm) not in have]
    questions = questions if questions is not None else reading_questions()
    lock = threading.Lock()
    stats = {"asked": 0, "answered": 0, "failed": 0, "skipped": 0, "started": time.time()}

    def save():
        done["model"] = getattr(model, "model", None)
        done["revision"] = getattr(model, "revision", None)
        done["questions"] = questions
        done["stats"] = dict(stats, seconds=round(time.time() - stats["started"], 1))
        if arms:
            done["arms"] = list(arms)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(done, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, path)

    def one(job):
        w, e, part, arm = job
        if deadline is not None and time.time() >= deadline:
            with lock:
                stats["skipped"] += 1
                done["answers"].append(dict({"id": e["id"], "which": w, "part": part, "skipped": "deadline",
                                             "data": None}, **({"arm": arm} if arm is not None else {})))
                save()
            return None
        with lock:
            stats["asked"] += 1
        try:
            a = ask_entry(model, e, images_root, w, questions, max_side, part=part,
                          marked_dir=out / f"arm_{arm}" if arm is not None else out, arm=arm)
        except Exception as exc:  # noqa: BLE001 - one failed call is recorded, the others go on
            a = dict({"id": e["id"], "which": w, "part": part, "data": None,
                      "errors": [f"{type(exc).__name__}: {str(exc)[:300]}"]}, **({"arm": arm} if arm is not None else {}))
        with lock:
            if a.get("data") is not None:
                stats["answered"] += 1
            else:
                stats["failed"] += 1
            done["answers"] = [x for x in done["answers"] if not (x["id"] == e["id"] and x["which"] == w
                                                                  and (x.get("part") or 0) == part
                                                                  and x.get("arm") == arm)] + [a]
            save()
            n = len(a.get("data", {}).get("findings", [])) if a.get("data") and w == "differences" else None
            log(f"critic {w} {e['id']}{f' part {part}' if part else ''}{f' arm {arm}' if arm is not None else ''}: "
                f"{'ok' if a.get('data') is not None else 'FAILED'}"
                + (f", {n} findings" if n is not None else "") + f", {a.get('seconds', '?')} s")
        return a

    save()
    AM.map_calls(model, one, jobs)
    if "second" in which:
        # 20 Nov 2026: the second look, once, on the findings of this pass under the confidence threshold (per arm:
        # each arm looks again at its own findings, with its own switch)
        from wenart.reading_check import critic_checks as CC

        jobs2 = []
        for arm, part_answers in split_arms(done).items():
            have2 = {a["id"] for a in part_answers["answers"] if a.get("which") == "second" and a.get("data") is not None}
            items = CC.second_look_items(index, [f for f in answers_to_findings(index, part_answers)
                                                 if not sets or f.get("set") in sets])
            jobs2 += [("second", it, 0, arm) for it in items if it["id"] not in have2]
        log(f"critic: second look on {len(jobs2)} finding(s)")
        AM.map_calls(model, one, jobs2)
    done["calls"] = list(getattr(model, "calls", []) or [])
    save()
    if arms:
        for arm, part_answers in split_arms(done).items():
            (out / f"arm_{arm}").mkdir(parents=True, exist_ok=True)
            (out / f"arm_{arm}" / "answers.json").write_text(json.dumps(part_answers, ensure_ascii=False, indent=1),
                                                            encoding="utf-8")
    log(f"critic: {stats['answered']} answered, {stats['failed']} failed, {stats['skipped']} skipped after the "
        f"deadline, {round(time.time() - stats['started'])} s")
    return done


def gpu_mem_mib() -> Optional[int]:
    from wenart.run import servers as SV

    try:
        out = subprocess.run(SV.NVIDIA_SMI_QUERY, capture_output=True, text=True, timeout=20).stdout
        return SV.gpu_from_text(out)[1] or None
    except (OSError, subprocess.SubprocessError, AttributeError):
        return None


def serve_and_ask(key: str, index: dict, images_root: Path, out: Path, *, deadline: Optional[float] = None,
                  server_flags: str = "", job_dir: Optional[Path] = None, logs_dir: Optional[Path] = None,
                  sets: Optional[list] = None, which: tuple = ("differences", "questions"),
                  arms: Optional[tuple] = None, log=print) -> dict:
    """The pod: serve ``check.yaml models.<key>`` with ``wenart.run.servers`` (the project's launcher; ``server_flags``
    appended, e.g. the memory share of a pod with no renders beside the server) and ask every call; the server's
    stats and the answers in ``out``."""
    from wenart.agent import model as AM
    from wenart.run import servers as SV

    mem = gpu_mem_mib()
    models = SV.check_models()
    seqs = SV.server_seqs(mem, SV.max_seqs_of(models, key))
    stats: list = []
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    kw = {}
    if logs_dir is not None:
        kw["logs_dir"] = Path(logs_dir)
    if job_dir is not None:
        kw["job_dir"] = Path(job_dir)
    with SV.server(key, deadline, stats=stats, seqs=seqs, mem_mib=mem, extra_flags=server_flags, **kw) as url:
        (out / "server.json").write_text(json.dumps(dict(stats[-1], url=url, gpu_mem_mib=mem, key=key),
                                                    indent=1), encoding="utf-8")
        model = AM.from_check_yaml(url, key, timeout_s=900.0, parallel=seqs)
        return ask(index, model, images_root, out, deadline=deadline, sets=sets, which=which, arms=arms, log=log)


# ================================================================================================ 4. findings
def _entries_by_id(index: dict) -> dict:
    return {e["id"]: e for e in index.get("entries") or []}


def answers_to_findings(index: dict, answers: dict, model_key: str = "") -> list:
    """Every difference and every ``problem`` answer as a finding with its place in building metres (pure):
    ``{check, name, kind, level_id, project, tag, set, at, point, description, confidence, lesson, model, call}``."""
    from wenart.reading_check import critic_checks as CC

    byid = _entries_by_id(index)
    byid.update({t["id"]: t for t in index.get("texts") or []})
    readings = index.get("readings") or {}
    sf = CC.stands_for(index) if index.get("readings") else {}
    out = []
    for a in answers.get("answers") or []:
        e, data = byid.get(a.get("id")), a.get("data")
        if e is None or not isinstance(data, dict):
            continue
        base = {"check": CHECK, "name": NAME, "level_id": e["level"], "project": e["project"], "tag": e.get("tag"),
                "set": e.get("set"), "entry": e["id"], "model": a.get("model") or answers.get("model"),
                "model_key": model_key}
        if a.get("which") in CC.CHECKS:
            # 20 Nov 2026 (checks 1, 2, 4): mapped by critic_checks; a stable id per finding (the review sheets'
            # numbers and the user's marks refer to it)
            w, part = a["which"], int(a.get("part") or 0)
            bfacts = (readings.get(e.get("folder")) or {}).get("bfacts")
            found, _extra = CC.item_findings(w, e, data, part, bfacts)
            for f in found:
                copies = sorted(set(CC.copy_levels(e.get("copies"))) | (sf.get(e["id"]) or set()) - {e["level"]})
                out.append(dict(base, **f, call=w, part=part, folder=e.get("folder"), copies=copies,
                                image_entry=e.get("page_entry") if w == "plausibility" else e["id"],
                                id=f"{e['id']}|{w}|{f['key']}"))
            continue
        if a.get("which") == "differences":
            for k, f in enumerate(data.get("findings") or []):
                nx, ny = float(f.get("x", 0)) / 1000.0, float(f.get("y", 0)) / 1000.0
                at = norm_to_metres(nx, ny, e["box"], e["tf"])
                out.append(dict(base, kind=str(f.get("kind") or "other"), at=[round(at[0], 3), round(at[1], 3)],
                                point=[round(nx, 4), round(ny, 4)], description=str(f.get("description") or ""),
                                confidence=round(float(f.get("confidence", 0)) / 100.0, 2), call="differences",
                                rank=k))
        elif a.get("which") == "questions":
            for q in data.get("answers") or []:
                if q.get("answer") != "problem":
                    continue
                nx, ny = float(q.get("x", 0)) / 1000.0, float(q.get("y", 0)) / 1000.0
                at = norm_to_metres(nx, ny, e["box"], e["tf"])
                out.append(dict(base, kind="question", lesson=str(q.get("id") or ""),
                                at=[round(at[0], 3), round(at[1], 3)], point=[round(nx, 4), round(ny, 4)],
                                description=str(q.get("note") or ""), confidence=0.5, call="questions"))
    # 20 Nov 2026: the second looks (a rejected finding is flagged ``dropped``, its consumers leave it out)
    return CC.apply_second_looks(out, answers)


def question_table(answers: dict) -> dict:
    """``{lesson id: {ok, problem, cannot_see}}`` over every answered level (pure)."""
    out: dict = {}
    for a in answers.get("answers") or []:
        if a.get("which") != "questions" or not isinstance(a.get("data"), dict):
            continue
        for q in a["data"].get("answers") or []:
            k = out.setdefault(str(q.get("id")), {"ok": 0, "problem": 0, "cannot_see": 0})
            k[q.get("answer") if q.get("answer") in k else "cannot_see"] += 1
    return out


# ================================================================================================ 5. store, wiring
def store(out_dir, findings: list, *, source: Optional[dict] = None) -> Path:
    """``reading_check/critic.json`` of a reading: the critic's findings of that project (``answers_to_findings``) in
    building metres, with their source (model, commit, date); what ``findings(out_dir)`` reads."""
    out_dir = Path(out_dir)
    d = out_dir / "reading_check"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "critic.json"
    p.write_text(json.dumps({"check": CHECK, "source": source or {}, "date": _dt.date.today().isoformat(),
                             "findings": findings}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return p


def load_trust(path: Path = TRUST_PATH) -> Optional[dict]:
    path = Path(path)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def severity_of(f: dict) -> str:
    c = float(f.get("confidence") or 0)
    return "major" if c >= 0.8 else "minor"


def apply_trust(found: list, trust: Optional[dict]) -> list:
    """Each finding gets ``trust`` ``{precision, findings, threshold}`` of its kind; a kind below the threshold, or
    never judged, is written with severity ``info`` (``base_severity`` kept) and says so (in place)."""
    # 12 Nov 2026 (review F8): a trust file measured against the withdrawn accepted readings is marked ``stale``; its
    # kinds count as not calibrated (every finding info) until it is measured again on the synthetic and sparse truths
    kinds = {} if (trust or {}).get("stale") else ((trust or {}).get("kinds") or {})
    # 20 Nov 2026: checks 1, 2, 4 have their own kinds per check (``checks``: {check: {kind: ...}})
    by_check = {} if (trust or {}).get("stale") else ((trust or {}).get("checks") or {})
    threshold = float((trust or {}).get("threshold") or TRUST_MIN)
    for f in found:
        if f.get("check") != CHECK:
            continue
        if "base_message" not in f:
            f["base_message"] = f["message"]
            f["base_severity"] = f["severity"]
        k = ((by_check.get(f.get("call")) or {}).get(f.get("kind")) if f.get("call") in by_check
             else kinds.get(f.get("kind"))) or {}
        if f.get("call") in by_check and k.get("judged") is not None:
            k = dict(k, findings=k.get("judged"))
        n, prec = int(k.get("findings") or 0), k.get("precision")
        f["trust"] = {"precision": prec, "findings": n, "threshold": threshold}
        f["severity"] = f["base_severity"]
        if prec is None or n == 0:
            f["severity"] = "info"
            f["message"] = f["base_message"] + " [info only: this kind is not calibrated yet]"
        elif float(prec) < threshold:
            f["severity"] = "info"
            f["message"] = f["base_message"] + (f" [info only: kind precision {float(prec):.2f} on {n} judged "
                                                f"findings < {threshold:g}]")
        else:
            f["message"] = f["base_message"] + f" [kind precision {float(prec):.2f} on {n} judged findings]"
    return found


def findings(out_dir, trust: Optional[dict] = None) -> list:
    """The RC15 findings of a reading: its stored ``reading_check/critic.json`` (none when the file is absent: the
    critic runs on the pod, not in ``check()``), each with ``at`` in building metres, the trust file applied."""
    p = Path(out_dir) / "reading_check" / "critic.json"
    if not p.is_file():
        return []
    stored = json.loads(p.read_text(encoding="utf-8"))
    out = []
    for f in stored.get("findings") or []:
        kind = str(f.get("kind") or "other")
        what = f"lesson {f.get('lesson')}" if kind == "question" else kind
        if f.get("call"):
            what = f"{f['call']} {what}"
        where = f"at ({f['at'][0]:.2f}, {f['at'][1]:.2f}) m" if f.get("at") else "(the whole building)"
        msg = (f"{what} {where}: {f.get('description') or ''}"
               f" (confidence {float(f.get('confidence') or 0):.2f}, {f.get('model') or 'the vision model'})")
        out.append({"check": CHECK, "name": NAME, "kind": kind, "severity": severity_of(f), "level_id": f.get("level_id"),
                    "message": msg, "at": list(f.get("at") or []), "place": list(f.get("at") or []),
                    "lesson": f.get("lesson"), "confidence": f.get("confidence"), "call": f.get("call"),
                    "finding_id": f.get("id"), "element_ids": list(f.get("element_ids") or [])})
    return apply_trust(out, trust if trust is not None else load_trust())


# ================================================================================================ 6. calibration
def _seg_dist(p, a, b) -> float:
    ax, ay, bx, by = float(a[0]), float(a[1]), float(b[0]), float(b[1])
    dx, dy = bx - ax, by - ay
    n2 = dx * dx + dy * dy
    if n2 <= 1e-12:
        return math.dist(p, (ax, ay))
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / n2))
    return math.dist(p, (ax + t * dx, ay + t * dy))


def _anchor(kind: str, e: dict):
    if kind == "rooms":
        return e.get("centroid")
    if kind == "walls":
        a, b = e.get("start"), e.get("end")
        return [(a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0] if a and b else None
    return e.get("center")


def disagreements(truth_level: dict, read_level: dict) -> list:
    """Where the truth and a reading of one level disagree (pure, ``score``'s own matching): truth elements the reading
    lacks (``truth_only``), reading elements the truth lacks or negates (``read_only``), matched rooms with another
    label (``label``); each with its class, its anchor point and, for a wall, its segment."""
    from wenart.reading_check import score as SC
    from wenart.reading_check import truth as TR

    out = []
    for kind in TR.ELEMENT_TYPES:
        all_t, rr = truth_level.get(kind) or [], read_level.get(kind) or []
        tt = TR.positives(all_t)
        absent = [e for e in all_t if e.get("absent")]
        pairs = SC.match_kind(kind, tt, rr)
        ti, rj = {i for i, _ in pairs}, {j for _, j in pairs}
        for i, t in enumerate(tt):
            if i not in ti:
                out.append({"class": kind, "side": "truth_only", "at": _anchor(kind, t), "id": t.get("id"),
                            "label": t.get("label"), "seg": (t.get("start"), t.get("end")) if kind == "walls" else None})
        for j, r in enumerate(rr):
            if j not in rj:
                out.append({"class": kind, "side": "read_only", "at": _anchor(kind, r), "id": r.get("id"),
                            "label": r.get("label"), "seg": (r.get("start"), r.get("end")) if kind == "walls" else None})
        if absent:
            left = [r for j, r in enumerate(rr) if j not in rj]
            for _i, j in SC.match_kind(kind, absent, left):
                r = left[j]
                out.append({"class": kind, "side": "read_only", "negated": True, "at": _anchor(kind, r),
                            "id": r.get("id"), "label": r.get("label"),
                            "seg": (r.get("start"), r.get("end")) if kind == "walls" else None})
        if kind == "rooms":
            for i, j in pairs:
                t, r = tt[i], rr[j]
                if TR.norm_label(t.get("label")) != TR.norm_label(r.get("label")) and (t.get("label") or r.get("label")):
                    out.append({"class": kind, "side": "label", "at": _anchor(kind, r), "id": r.get("id"),
                                "label": f"{r.get('label')} -> {t.get('label')}", "seg": None})
    return [d for d in out if d.get("at")]


def _dist_to(p, d: dict) -> float:
    if d.get("seg") and d["seg"][0] and d["seg"][1]:
        return _seg_dist(p, d["seg"][0], d["seg"][1])
    return math.dist(p, d["at"])


def judge(finding: dict, level_disagreements: list, match_m: float = MATCH_M) -> dict:
    """A finding against the truth's disagreements of its level (pure): right when one of its kind's classes and sides
    lies within ``match_m`` of its point (``KIND_RULES``); the nearest disagreement of any kind is named either way."""
    classes, sides = KIND_RULES.get(finding.get("kind"), KIND_RULES["other"])
    p = tuple(finding["at"])
    best, best_any = None, None
    for d in level_disagreements:
        dist = _dist_to(p, d)
        if best_any is None or dist < best_any[0]:
            best_any = (dist, d)
        if d["class"] in classes and d["side"] in sides and (best is None or dist < best[0]):
            best = (dist, d)
    right = best is not None and best[0] <= match_m
    hit = best[1] if right else None
    return {"right": right, "distance": round(best[0], 2) if best else None,
            "matched": {k: hit[k] for k in ("class", "side", "id", "label")} if hit else None,
            "nearest": {"distance": round(best_any[0], 2), "class": best_any[1]["class"], "side": best_any[1]["side"],
                        "id": best_any[1]["id"]} if best_any else None}


def level_disagreements(truth: dict, read: dict) -> dict:
    """``{level id: disagreements}`` of a reading against its truth (the truth's levels; a reading level the truth
    lacks counts every element as ``read_only``)."""
    out = {}
    t_levels = {lv["id"] for lv in truth.get("levels") or []}
    for lid in t_levels:
        out[lid] = disagreements((truth.get("per_level") or {}).get(lid) or {},
                                 (read.get("per_level") or {}).get(lid) or {})
    for lid, rl in (read.get("per_level") or {}).items():
        if lid not in t_levels and truth.get("status") != "partial":
            out[lid] = disagreements({}, rl)
    return out


def precision_table(judged: list) -> dict:
    """Per kind ``{findings, judged_right, precision, trusted, small_sample}`` (pure); a judgement with
    ``counts: false`` is left out."""
    kinds: dict = {}
    for k in list(KINDS) + ["question"]:
        js = [j for j in judged if j.get("kind") == k and j.get("counts", True)]
        n, r = len(js), sum(1 for j in js if j.get("right"))
        kinds[k] = {"findings": n, "judged_right": r, "precision": round(r / n, 4) if n else None,
                    "trusted": bool(n) and r / n >= TRUST_MIN, "small_sample": n < SMALL_SAMPLE}
    n_all = sum(1 for j in judged if j.get("counts", True))
    r_all = sum(1 for j in judged if j.get("counts", True) and j.get("right"))
    kinds["all"] = {"findings": n_all, "judged_right": r_all, "precision": round(r_all / n_all, 4) if n_all else None}
    return kinds


def record_raised(rec: dict, found: list, match_m: float = MATCH_M) -> dict:
    """Whether the critic raised a user correction record on the reading made before it (pure): a finding on the
    record's level within ``match_m`` of its place; for a record without a place, a finding of a kind that names the
    record's element kind (``RECORD_KINDS``) anywhere in the project. The nearest finding is named either way."""
    place, level = rec.get("place"), rec.get("level")
    cands = [f for f in found if f.get("project") == rec.get("project") and f.get("kind") != "question"]
    if place and level:
        same = [f for f in cands if f.get("level_id") == level] or cands
        p = (float(place["x"]), float(place["y"]))
        best = min(((math.dist(p, f["at"]), f) for f in same), key=lambda t: t[0], default=None)
        raised = best is not None and best[0] <= match_m and best[1].get("level_id") == level
        return {"id": rec["id"], "raised": raised, "how": "place" if raised else None,
                "nearest": {"distance": round(best[0], 2), "kind": best[1]["kind"], "level": best[1].get("level_id"),
                            "description": best[1].get("description")} if best else None}
    kinds = RECORD_KINDS.get(str(rec.get("element_kind") or ""), ())
    hits = [f for f in cands if f.get("kind") in kinds and (not level or f.get("level_id") == level)]
    return {"id": rec["id"], "raised": bool(hits), "how": "kind" if hits else None,
            "nearest": {"distance": None, "kind": hits[0]["kind"], "level": hits[0].get("level_id"),
                        "description": hits[0].get("description")} if hits else None}


def out_of_sample_row(project: str, failure_class: Optional[str], dis: dict, found: list, match_m: float = MATCH_M) -> dict:
    """One synthetic project's row (pure): the reading's real errors (the truth's disagreements), the critic's
    findings there, and the verdict: caught (a finding within ``match_m`` of an error), missed (errors, none found),
    false_alarm (findings on a reading that matches its truth) or clean."""
    errors = [d for lid, ds in dis.items() for d in ds]
    fs = [f for f in found if f.get("project") == project and f.get("kind") != "question"]
    caught = []
    for lid, ds in dis.items():
        for d in ds:
            near = [f for f in fs if f.get("level_id") == lid and _dist_to(tuple(f["at"]), d) <= match_m]
            if near:
                caught.append({"class": d["class"], "side": d["side"], "id": d["id"],
                               "by": [f["kind"] for f in near][:3]})
    if errors:
        verdict = "caught" if caught else "missed"
    else:
        verdict = "false_alarm" if fs else "clean"
    return {"project": project, "failure_class": failure_class, "errors": len(errors), "findings": len(fs),
            "errors_caught": len(caught), "verdict": verdict, "caught": caught[:10],
            "error_classes": sorted({f"{d['class']}:{d['side']}" for d in errors})}


def level_bounds_m(entry: dict) -> tuple:
    """``(xmin, ymin, xmax, ymax)`` in building metres of an entry's frame (the box's corners through its page
    transform)."""
    b, tf = entry["box"], entry["tf"]
    pts = [(tf[0] * x + tf[1] * y + tf[2], tf[3] * x + tf[4] * y + tf[5])
           for x, y in ((b[0], b[1]), (b[2], b[1]), (b[2], b[3]), (b[0], b[3]))]
    return (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))


def random_findings(index: dict, found: list, seed: int) -> list:
    """The findings with their points replaced by uniform random points in their level's frame (the same number and
    kinds per level): what the critic would score if it pointed anywhere (pure given ``seed``)."""
    import random

    rnd = random.Random(seed)
    entries = _entries_by_id(index)
    out = []
    for f in found:
        e = entries.get(f.get("entry"))
        if e is None:
            out.append(dict(f))
            continue
        x0, y0, x1, y1 = level_bounds_m(e)
        out.append(dict(f, at=[round(rnd.uniform(x0, x1), 3), round(rnd.uniform(y0, y1), 3)]))
    return out


def chance_baseline(index: dict, found: list, *, dis_by_folder: dict, records: list, rc14: Optional[dict],
                    match_m: float = MATCH_M, draws: int = 30, seed: int = 0) -> dict:
    """Precision, recall and out-of-sample catches of random points with the critic's own counts and kinds per level,
    averaged over ``draws`` draws (6 Nov 2026: at ten findings a level a match within 1.5 m is likely by chance; the
    critic earns trust only above this)."""
    entries = _entries_by_id(index)
    rc14_ids = set(rc14 or {})
    sums = {"precision": 0.0, "recall": 0.0, "oos_caught": 0.0, "oos_classes_caught": 0.0}
    for k in range(draws):
        rf = random_findings(index, found, seed + k)
        judged = []
        for f in rf:
            e = entries.get(f.get("entry"))
            if e is None or e.get("set") != "a" or e["folder"] not in dis_by_folder:
                continue
            judged.append(judge(f, dis_by_folder[e["folder"]].get(f["level_id"]) or [], match_m)["right"])
        sums["precision"] += (sum(judged) / len(judged)) if judged else 0.0
        b_found = [f for f in rf if f.get("set") == "b"]
        rec = [record_raised(r, b_found, match_m)["raised"] for r in records if r.get("id") in rc14_ids]
        sums["recall"] += sum(rec)
        caught = classes = 0
        for folder, e in {e["folder"]: e for e in entries.values()}.items():
            if e.get("set") != "c" or folder not in dis_by_folder:
                continue
            row = out_of_sample_row(e["project"], e.get("failure_class"), dis_by_folder[folder], rf, match_m)
            if row["errors"]:
                classes += 1
                caught += 1 if row["verdict"] == "caught" else 0
        sums["oos_caught"] += caught
        sums["oos_classes_caught"] += classes
    n = float(draws)
    return {"draws": draws, "precision": round(sums["precision"] / n, 4), "recall_of_rc14_records": round(sums["recall"] / n, 2),
            "rc14_records": len([r for r in records if r.get("id") in rc14_ids]),
            "out_of_sample_caught": round(sums["oos_caught"] / n, 2),
            "out_of_sample_classes": int(sums["oos_classes_caught"] / n) if draws else 0}


def _reading_dict(building: dict, project: str, truth: dict) -> dict:
    from wenart.reading_check import truth as TR

    return TR.extract(building, project=project, leave_out=truth.get("levels_left_out") or [])


def calibrate(index: dict, found: list, *, readings: dict, truths: Optional[dict] = None, records: Optional[list] = None,
              rc14: Optional[dict] = None, match_m: float = MATCH_M, model_key: str = "",
              by_eye: Optional[dict] = None) -> dict:
    """The trust file's content (pure given its inputs): ``readings`` = ``{entry folder: building dict}`` of the
    readings the images were made from (sets a and c; b is judged by the records), ``truths`` =
    ``{project: truth dict}`` (default ``results/reading_truth/``), ``records`` the correction store, ``rc14`` =
    ``{record id: RC14's answer}`` for the side-by-side. ``by_eye`` (6 Nov 2026: "judge the doubtful ones from the
    drawing") = ``{"findings": {"<entry>#<rank>": {"right": bool, "reason"}}, "recall": {"<record id>": {"raised":
    bool, "reason"}}}``: a judgement from the drawing replaces the truth's for that finding (the accepted truth can
    carry a reading's own error), and a record's ``raised_by_meaning`` says whether the nearest finding names the
    record's problem, not only lies near its place."""
    by_eye = by_eye or {}
    eye_f, eye_r = by_eye.get("findings") or {}, by_eye.get("recall") or {}
    from wenart.reading_check import truth as TR

    truths = truths if truths is not None else {}
    entries = _entries_by_id(index)
    by_folder: dict = {}
    for e in entries.values():
        by_folder.setdefault(e["folder"], e)
    # the truth's disagreements with every reading we have (sets a and c)
    dis_by_folder: dict = {}
    for folder, b in readings.items():
        e = by_folder.get(folder)
        if e is None:
            continue
        truth = truths.get(e["project"]) if e["project"] in truths else TR.load_truth(e["project"])
        if truth is None or TR.is_sparse(truth):
            # 6 Nov 2026: a sparse truth (a real project's: the user's corrections only) lists what the user said, not
            # everything there is; it cannot judge a finding where it lists nothing (set b is judged by the records)
            continue
        truths[e["project"]] = truth
        dis_by_folder[folder] = level_disagreements(truth, _reading_dict(b, e["project"], truth))
    # precision on set a (and the false alarms of set c are reported in their own table)
    judged = []
    for f in found:
        e = entries.get(f.get("entry"))
        if e is None or e.get("set") != "a" or e["folder"] not in dis_by_folder:
            continue
        j = judge(f, dis_by_folder[e["folder"]].get(f["level_id"]) or [], match_m)
        eye = eye_f.get(f"{f['entry']}#{f.get('rank')}")
        if eye is not None:
            j.update(right_by_truth=j["right"], right=bool(eye.get("right")), by_eye=str(eye.get("reason") or ""))
        judged.append(dict({"entry": f["entry"], "project": f["project"], "level": f["level_id"], "kind": f["kind"],
                            "at": f["at"], "description": f.get("description"), "confidence": f.get("confidence"),
                            "lesson": f.get("lesson")}, **j))
    kinds = precision_table(judged)
    kinds_by_truth = precision_table([dict(j, right=j.get("right_by_truth", j["right"])) for j in judged])
    # recall on set b
    rec_rows = []
    if records:
        b_projects = {(e["project"], e["tag"]) for e in entries.values() if e.get("set") == "b"}
        b_found = [f for f in found if f.get("set") == "b"]
        for rec in records:
            if not any(rec.get("project") == p for p, _t in b_projects):
                continue
            row = record_raised(rec, b_found, match_m)
            eye = eye_r.get(rec["id"])
            row.update(project=rec.get("project"), level=rec.get("level"), element_kind=rec.get("element_kind"),
                       status=rec.get("status"), right_answer=(rec.get("right_answer") or "")[:120],
                       in_rc14_set=bool(rc14 and rec["id"] in rc14),
                       rc14=(rc14 or {}).get(rec["id"]),
                       raised_by_meaning=bool(eye.get("raised")) if eye is not None else None,
                       by_eye=str(eye.get("reason") or "") if eye is not None else None)
            rec_rows.append(row)
    in_set = [r for r in rec_rows if r["in_rc14_set"]]
    placed = [r for r in rec_rows if not r["in_rc14_set"] and r.get("level")]
    rc14_yes = sum(1 for r in in_set if str(r.get("rc14") or "").startswith("yes"))
    recall = {"rc14_records": len(in_set), "critic_raised": sum(1 for r in in_set if r["raised"]), "rc14_raised": rc14_yes,
              "critic_raised_by_meaning": sum(1 for r in in_set if r.get("raised_by_meaning")),
              "judged_by_meaning": sum(1 for r in in_set if r.get("raised_by_meaning") is not None),
              "only_critic": [r["id"] for r in in_set if r["raised"] and not str(r.get("rc14") or "").startswith("yes")],
              "only_critic_by_meaning": [r["id"] for r in in_set if r.get("raised_by_meaning")
                                         and not str(r.get("rc14") or "").startswith("yes")],
              "only_rc14": [r["id"] for r in in_set if not r["raised"] and str(r.get("rc14") or "").startswith("yes")],
              "other_placed_records": len(placed), "other_placed_raised": sum(1 for r in placed if r["raised"]),
              "records": rec_rows}
    # out of sample on set c
    oos = []
    for folder, e in sorted(by_folder.items()):
        if e.get("set") != "c" or folder not in dis_by_folder:
            continue
        oos.append(out_of_sample_row(e["project"], e.get("failure_class"), dis_by_folder[folder], found, match_m))
    with_errors = [r for r in oos if r["errors"]]
    oos_summary = {"projects": len(oos), "with_reading_errors": len(with_errors),
                   "caught": sum(1 for r in with_errors if r["verdict"] == "caught"),
                   "missed": sum(1 for r in with_errors if r["verdict"] == "missed"),
                   "false_alarm": sum(1 for r in oos if r["verdict"] == "false_alarm"),
                   "clean": sum(1 for r in oos if r["verdict"] == "clean"), "rows": oos}
    chance = chance_baseline(index, found, dis_by_folder=dis_by_folder, records=records or [], rc14=rc14,
                             match_m=match_m) if found else None
    per_level = {}
    for f in found:
        if f.get("kind") != "question":
            per_level[f["entry"]] = per_level.get(f["entry"], 0) + 1
    density = {"levels": len(per_level), "findings": sum(per_level.values()),
               "per_level": round(sum(per_level.values()) / len(per_level), 2) if per_level else 0.0}
    return {"note": ("Trust of the vision critic (RC15) per finding kind: precision on the accepted projects' current "
                     "readings (a finding is right when the truth disagrees with the reading within 1.5 m in the way "
                     "the kind says), recall of the user's past correction records on the readings made before them, "
                     "and the out-of-sample table on the synthetic failure classes. A kind under the threshold, or "
                     "never judged, writes its findings as info."),
            "check": CHECK, "model_key": model_key, "date": _dt.date.today().isoformat(), "threshold": TRUST_MIN,
            "match_m": match_m, "kinds": kinds, "kinds_by_truth_only": kinds_by_truth, "recall": recall,
            "out_of_sample": oos_summary, "chance": chance, "density": density,
            "by_eye": {"findings": len(eye_f), "recall": len(eye_r)}, "judgements": judged}


def save_trust(trust: dict, path: Path = TRUST_PATH) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(trust, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return path


def trust_summary(trust: dict) -> str:
    lines = ["| kind | findings | right | precision | trusted |", "|---|---|---|---|---|"]
    for k, v in (trust.get("kinds") or {}).items():
        p = v.get("precision")
        lines.append(f"| {k} | {v.get('findings', 0)} | {v.get('judged_right', 0)} | "
                     f"{'-' if p is None else f'{p:.2f}'} | {v.get('trusted', '-')} |")
    r = trust.get("recall") or {}
    lines.append("")
    lines.append(f"recall: critic {r.get('critic_raised', 0)} of {r.get('rc14_records', 0)} records by place (RC14 "
                 f"{r.get('rc14_raised', 0)}); only the critic: {', '.join(r.get('only_critic') or []) or '-'}; only "
                 f"RC14: {', '.join(r.get('only_rc14') or []) or '-'}; other placed records "
                 f"{r.get('other_placed_raised', 0)} of {r.get('other_placed_records', 0)}")
    if r.get("judged_by_meaning"):
        lines.append(f"recall by meaning (the nearest finding names the record's problem, judged by eye on "
                     f"{r['judged_by_meaning']} records): {r.get('critic_raised_by_meaning', 0)}; only the critic: "
                     f"{', '.join(r.get('only_critic_by_meaning') or []) or '-'}")
    o = trust.get("out_of_sample") or {}
    lines.append(f"out of sample: {o.get('caught', 0)} caught, {o.get('missed', 0)} missed of "
                 f"{o.get('with_reading_errors', 0)} classes with reading errors; {o.get('false_alarm', 0)} false alarm(s), "
                 f"{o.get('clean', 0)} clean")
    for row in o.get("rows") or []:
        lines.append(f"  {row['project']}: {row['verdict']} ({row['errors']} errors, {row['findings']} findings, "
                     f"{row['errors_caught']} caught)")
    c, d = trust.get("chance") or {}, trust.get("density") or {}
    if c:
        lines.append(f"chance (random points, the critic's own {d.get('per_level', 0)} findings a level, {c.get('draws')} "
                     f"draws): precision {c.get('precision')}, recall {c.get('recall_of_rc14_records')} of "
                     f"{c.get('rc14_records')}, out of sample {c.get('out_of_sample_caught')} of "
                     f"{c.get('out_of_sample_classes')} caught")
    return "\n".join(lines)


# ================================================================================================ 7. readings
def read_at_commit(project: str, commit: str, work: Path, *, python: str = "python3", log=print) -> Path:
    """A reading of ``projects/<project>`` with the reader of ``commit`` (``git archive`` into ``work/src_<commit>``,
    run as a subprocess with ``PYTHONPATH`` on it; the projects folder of this tree): ``work/<project>@<commit>``.
    The readings made before the user's corrections (set b)."""
    work = Path(work)
    src = work / f"src_{commit[:8]}"
    if not (src / "wenart").is_dir():
        src.mkdir(parents=True, exist_ok=True)
        ar = subprocess.run(["git", "-C", str(REPO), "archive", "--format=tar", commit, "wenart", "scripts"],
                            capture_output=True, check=True)
        subprocess.run(["tar", "-x", "-C", str(src)], input=ar.stdout, check=True)
    out = work / f"{project}@{commit[:8]}"
    shutil.rmtree(out, ignore_errors=True)
    code = ("import sys; from pathlib import Path; from wenart.ingest import pipeline as PL; "
            "PL.run_project(Path(sys.argv[1]), Path(sys.argv[2]), no_ai=True)")
    env = dict(os.environ, PYTHONPATH=str(src))
    t0 = time.time()
    r = subprocess.run([python, "-c", code, str(REPO / "projects" / project), str(out)], env=env, cwd=str(src),
                       capture_output=True, text=True)
    log(f"reading {project} at {commit[:8]}: rc {r.returncode} in {round(time.time() - t0)} s")
    if r.returncode != 0:
        raise RuntimeError(f"reading {project} at {commit[:8]} failed: {r.stderr[-1500:]}")
    return out


def read_current(project: str, work: Path) -> Path:
    from wenart.reading_check import regress as RG

    return RG.read_project(project, Path(work))


# ================================================================================================ 8. CLI
def _add_prepare(sub):
    p = sub.add_parser("prepare", help="render the two images per level of readings into the input set")
    p.add_argument("--set", required=True, choices=["a", "b", "c", "before", "after", "synth"],
                   help="a precision, b recall, c out of sample; before / after / synth: the sets of checks 1, 2, 4")
    p.add_argument("--checks", action="store_true",
                   help="also the inputs of checks 1, 2, 4 (architect image, facts, questions, floor texts); "
                        "default for the sets before, after, synth")
    p.add_argument("--reading", action="append", default=[], metavar="PROJECT[@TAG]=DIR",
                   help="a reading folder (repeatable); TAG the reader's commit (default current)")
    p.add_argument("--read", action="append", default=[], metavar="PROJECT[@COMMIT]",
                   help="read the project here first (at COMMIT with git archive), then render, then delete")
    p.add_argument("--work", default=None, help="work folder for --read (default a temporary folder)")
    p.add_argument("--keep", action="store_true", help="keep the readings made by --read")
    p.add_argument("--dest", default=str(INPUTS_DIR))
    p.add_argument("--max-side", type=int, default=MAX_SIDE)
    p.add_argument("--levels", default=None, help="only these level ids, comma separated")


def _parse_reading(text: str) -> tuple:
    name, _, folder = text.partition("=")
    project, _, tag = name.partition("@")
    return project, tag or "current", folder


def _failure_class(project: str) -> Optional[str]:
    try:
        from wenart.synthetic import failure_projects as FP
        for fp in FP.failure_projects():
            if fp.name == project:
                return fp.failure_class
    except Exception:  # noqa: BLE001 - no synthetic module: no class
        return None
    return None


def _cmd_prepare(args) -> int:
    import tempfile

    readings = []
    work = Path(args.work) if args.work else Path(tempfile.mkdtemp(prefix="critic_read_"))
    made = []
    checks = bool(args.checks) or args.set in ("before", "after", "synth")
    for item in args.reading:
        project, tag, folder = _parse_reading(item)
        commit = None
        cp = Path(folder) / "reading_check" / "commit.txt"
        if cp.is_file():
            commit = cp.read_text(encoding="utf-8").strip()[:12] or None
        readings.append({"set": args.set, "project": project, "tag": tag, "out_dir": folder, "checks": checks,
                         "commit": commit or (tag if tag != "current" else None),
                         "failure_class": _failure_class(project)})
    for item in args.read:
        project, _, commit = item.partition("@")
        folder = read_at_commit(project, commit, work) if commit else read_current(project, work)
        made.append(folder)
        readings.append({"set": args.set, "project": project, "tag": commit[:8] if commit else "current",
                         "out_dir": folder, "commit": commit or None, "failure_class": _failure_class(project),
                         "checks": checks})
    levels = [x for x in (args.levels or "").split(",") if x] or None
    index = prepare(readings, Path(args.dest), max_side=args.max_side, levels=levels)
    n = sum(1 for e in index["entries"] if e["set"] == args.set)
    size = sum(p.stat().st_size for p in Path(args.dest).rglob("*.jpg"))
    print(f"critic inputs: set {args.set} now {n} level(s); {len(index['entries'])} in all, "
          f"{size / 1e6:.1f} MB of JPEGs in {args.dest}")
    if not args.keep:
        for f in made:
            shutil.rmtree(f, ignore_errors=True)
    return 0


def arms_of(text: Optional[str], env: Optional[dict] = None) -> Optional[tuple]:
    """The arms of an ask (pure): ``--arms`` (``0,1``: the vector text A/B), else ``CRITIC_VECTOR_TEXT`` alone (``1`` or
    ``text``: every call with it); None (asked as before, no ``arm`` on the answers) for ``0`` or nothing."""
    from wenart.reading_check import vector_text as VT

    if text:
        arms = tuple(dict.fromkeys(a.strip().lower() for a in text.split(",") if a.strip().lower() in VT.MODES))
        return arms or None
    m = VT.mode(env)
    return None if m == "0" else (m,)


def _cmd_ask(args) -> int:
    from wenart.reading_check import critic_checks as CC

    index = load_index(Path(args.inputs))
    deadline = float(args.deadline) if args.deadline else None
    known_calls = ("differences", "questions") + CC.CHECKS + ("second", "judge")
    which = tuple(w for w in (args.which or "differences,questions").split(",") if w in known_calls)
    sets = [s for s in (args.sets or "").split(",") if s] or None
    arms = arms_of(args.arms)
    out = Path(args.out) / args.key
    if args.vlm_url:
        from wenart.agent import model as AM
        model = AM.from_check_yaml(args.vlm_url, args.key, timeout_s=900.0, parallel=args.workers or 1)
        res = ask(index, model, Path(args.inputs), out, deadline=deadline, sets=sets, which=which, arms=arms)
    else:
        res = serve_and_ask(args.key, index, Path(args.inputs), out, deadline=deadline, server_flags=args.server_flags,
                            job_dir=Path(args.job_dir) if args.job_dir else None,
                            logs_dir=Path(args.logs_dir) if args.logs_dir else None, sets=sets, which=which,
                            arms=arms)
    st = res.get("stats") or {}
    print(f"critic ask {args.key}: {st.get('answered', 0)} answered, {st.get('failed', 0)} failed, "
          f"{st.get('skipped', 0)} skipped -> {out / 'answers.json'}")
    return 0 if st.get("answered") or not (st.get("failed") or st.get("skipped")) else 1


def _load_readings(index: dict, folders: list) -> dict:
    """``{entry folder: building dict}`` from ``--readings SET/NAME=DIR`` items and a ``--readings-root`` layout."""
    out = {}
    for item in folders:
        key, _, folder = item.partition("=")
        bp = Path(folder) / "building.json"
        if bp.is_file():
            out[key] = json.loads(bp.read_text(encoding="utf-8"))
    return out


KNOWN_PATH = REPO / "results" / "critic" / "known_errors.json"
MARKS_PATH = REPO / "results" / "critic" / "user_marks.json"
REVIEW_DIR = REPO / "results" / "critic" / "review"


def run_review_dir(answers_path, base: Path = REVIEW_DIR) -> Path:
    """A new review-sheet folder for one pod's answers (20 Nov 2026, the coordinator: a re-calibration must never
    renumber the sheets the user is marking): ``review_<run>`` after the answers' run folder (``YYYYMMDD-HHMMSS``),
    with ``_2``, ``_3`` ... when that folder holds sheets already."""
    import re as _re

    m = _re.search(r"(\d{8}-\d{6})", str(answers_path))
    name = f"{base.name}_{m.group(1) if m else _dt.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    dest = base.parent / name
    k = 2
    while dest.exists() and any(dest.rglob("findings_index.json")):
        dest = base.parent / f"{name}_{k}"
        k += 1
    return dest


def _cmd_calibrate(args) -> int:
    from wenart.reading_check import critic_checks as CC

    # 20 Nov 2026: a pod's answers are scored against the index it was asked with (``--index``: the frozen copy,
    # e.g. index_pod1.json; the images stay under --inputs)
    index = json.loads(Path(args.index).read_text(encoding="utf-8")) if args.index else load_index(Path(args.inputs))
    answers = json.loads(Path(args.answers).read_text(encoding="utf-8"))
    by_arm = split_arms(answers)
    if len(by_arm) > 1 and getattr(args, "arm", None) is None:
        print(f"the answers hold the arms {', '.join(str(a) for a in by_arm)}: name one with --arm (or use vt-score)")
        return 2
    answers = by_arm.get(getattr(args, "arm", None)) or next(iter(by_arm.values()))
    found_all = answers_to_findings(index, answers, args.key or "")
    new_all = [f for f in found_all if f.get("call") in CC.CHECKS]
    new = [f for f in new_all if not f.get("dropped")]
    dropped = [f for f in new_all if f.get("dropped")]
    old = [f for f in found_all if f.get("call") not in CC.CHECKS]
    trust = _calibrate_old(args, index, answers, old) if old or not new else (load_trust() or {})
    if new:
        # 20 Nov 2026 (checks 1, 2, 4): judged by the user's marks, the synthetic truth and the known errors; the
        # review sheets for the user's marks; the trust per check and kind in the same trust file
        kp, mp = Path(args.known or KNOWN_PATH), Path(args.marks or MARKS_PATH)
        known = json.loads(kp.read_text(encoding="utf-8")).get("readings") if kp.is_file() else {}
        marks = json.loads(mp.read_text(encoding="utf-8")).get("marks") if mp.is_file() else {}
        res = CC.calibrate_checks(index, new, answers, known=known, marks=marks, match_m=MATCH_M, dropped=dropped)
        print(CC.checks_summary(res))
        trust["checks"] = res["checks"]
        trust["checks_calibration"] = {k: res[k] for k in ("recall", "synthetic", "calls", "judged_by", "second_look")}
        trust["checks_calibration"].update(date=_dt.date.today().isoformat(), answers=str(args.answers),
                                           findings=len(new), known=str(kp), marks=str(mp))
        trust.setdefault("threshold", TRUST_MIN)
        trust.setdefault("check", CHECK)
        if args.json:
            Path(args.json).write_text(json.dumps(dict(res, findings=new), ensure_ascii=False, indent=1) + "\n",
                                       encoding="utf-8")
            print(f"written {args.json}")
        if not args.no_sheets:
            dest = Path(args.review) if args.review else run_review_dir(args.answers)
            sheets = CC.review_sheets(index, new, Path(args.inputs), dest,
                                      judged={j["id"]: j for j in res["judgements"]})
            print(f"review sheets: {sum(len(v) for v in sheets.values())} in {dest}")
    if args.write:
        print(f"written {save_trust(trust)}")
    return 0


def _calibrate_old(args, index: dict, answers: dict, found: list) -> dict:
    """The differences and question-bank calls' calibration (6 Nov 2026), as before."""
    from wenart.reading_check import truth as TR

    readings = _load_readings(index, args.readings)
    if args.readings_root:
        root = Path(args.readings_root)
        for e in index.get("entries") or []:
            bp = root / e["folder"] / "building.json"
            if bp.is_file() and e["folder"] not in readings:
                readings[e["folder"]] = json.loads(bp.read_text(encoding="utf-8"))
    records = TR.load_corrections() if not args.no_records else []
    rc14 = json.loads(Path(args.rc14).read_text(encoding="utf-8")) if args.rc14 else None
    by_eye = json.loads(Path(args.by_eye).read_text(encoding="utf-8")) if args.by_eye else None
    trust = calibrate(index, found, readings=readings, records=records, rc14=rc14, model_key=args.key or "",
                      by_eye=by_eye)
    trust["questions"] = question_table(answers)
    trust["answers"] = str(args.answers)
    trust["findings_total"] = len(found)
    print(trust_summary(trust))
    if args.json and found:
        Path(args.json).write_text(json.dumps(trust, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"written {args.json}")
    old = load_trust() or {}
    for k in ("checks", "checks_calibration"):               # the checks' own calibration is kept
        if k in old:
            trust[k] = old[k]
    return trust


def _cmd_known(args) -> int:
    """``known_errors.json``: per input folder of the sets before and after, the known errors (and, after, the
    places fixed) of each pod project (``critic_checks.known_errors_for``) and the user's corrections that do not
    hold (``sparse_known``)."""
    from wenart.reading_check import critic_checks as CC

    index = load_index(Path(args.inputs))
    folders = {(r["project"], k.split("/", 1)[0]): k for k, r in (index.get("readings") or {}).items()}
    path = Path(args.out or KNOWN_PATH)
    doc = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"readings": {}}
    for item in args.pair:
        project, _, dirs = item.partition("=")
        bdir, _, adir = dirs.partition(",")
        before = json.loads((Path(bdir) / "building.json").read_text(encoding="utf-8"))
        after = json.loads((Path(adir) / "building.json").read_text(encoding="utf-8"))
        kb, ka = CC.known_errors_for(project, before, after)
        kb += [dict(x, id=f"{project}-UB{i + 1:02d}", reading="before") for i, x in
               enumerate(CC.sparse_known(project, before))]
        ka += [dict(x, id=f"{project}-UA{i + 1:02d}", reading="after") for i, x in
               enumerate(CC.sparse_known(project, after))]
        fb, fa = folders.get((project, "before")), folders.get((project, "after"))
        if fb:
            doc["readings"][fb] = kb
        if fa:
            doc["readings"][fa] = ka
        print(f"{project}: before {fb} {sum(1 for x in kb if not x.get('fixed'))} known error(s); after {fa} "
              f"{sum(1 for x in ka if not x.get('fixed'))} error(s), {sum(1 for x in ka if x.get('fixed'))} fixed place(s)")
    doc["note"] = ("Known errors of the readings of checks 1, 2, 4 (20 Nov 2026): per input folder, each error with its "
                   "level, place (building metres; null for a building-wide one), the finding kinds that name it, and "
                   "fixed: true for a place the after reading has fixed (a finding there is a false alarm). From the "
                   "brief's list (real09's missing left salon, kitchen and balcony and its roof, real20's straight "
                   "angled wall and doors into the air, real10's missing kitchen windows, real03's storey count), "
                   "RC17's doors into the air and the user's screenshot corrections (sparse truth).")
    doc["made"] = _dt.date.today().isoformat()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"written {path}")
    return 0


def _cmd_mark(args) -> int:
    """The user's marks on a review sheet (numbers right / wrong) as truth for the next calibration
    (``user_marks.json``, by finding id)."""
    from wenart.reading_check import critic_checks as CC

    idx = json.loads((Path(args.review or REVIEW_DIR) / args.folder / "findings_index.json").read_text(encoding="utf-8"))
    nums = lambda s: [int(x) for x in (s or "").split(",") if x.strip()]  # noqa: E731
    new = CC.marks_from_numbers(idx, args.sheet, nums(args.right), nums(args.wrong))
    path = Path(args.marks or MARKS_PATH)
    doc = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"marks": {}}
    for fid, m in new.items():
        doc["marks"][fid] = dict(m, date=_dt.date.today().isoformat())
    doc["note"] = ("The user's marks on the RC15 review sheets (finding id -> right or wrong); truth for the next "
                   "calibration of checks 1, 2, 4 (critic calibrate).")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(new)} mark(s) -> {path}")
    return 0


def _cmd_store(args) -> int:
    index = load_index(Path(args.inputs))
    answers = json.loads(Path(args.answers).read_text(encoding="utf-8"))
    found = [f for f in answers_to_findings(index, answers, args.key or "")
             if f["project"] == args.project and (not args.tag or f.get("tag") == args.tag) and not f.get("dropped")]
    p = store(args.out, found, source={"answers": str(args.answers), "model": answers.get("model"),
                                       "model_key": args.key, "index": str(args.inputs)})
    print(f"{len(found)} critic finding(s) of {args.project} -> {p}")
    return 0


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.reading_check critic", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    _add_prepare(sub)
    a = sub.add_parser("ask", help="ask the vision model about every level of the input set (the pod job)")
    a.add_argument("--key", default=DEFAULT_MODEL_KEY, help="check.yaml model key (agent, qwen)")
    a.add_argument("--inputs", default=str(INPUTS_DIR))
    a.add_argument("--out", required=True, help="results folder (answers under <out>/<key>/)")
    a.add_argument("--vlm-url", dest="vlm_url", default=None, help="a server already running (the CPU preflight)")
    a.add_argument("--workers", type=int, default=None, help="with --vlm-url: calls at once")
    a.add_argument("--deadline", default=None, help="epoch seconds; nothing new is sent after it")
    a.add_argument("--server-flags", dest="server_flags", default="", help="appended to vllm serve (the job only)")
    a.add_argument("--job-dir", dest="job_dir", default=None)
    a.add_argument("--logs-dir", dest="logs_dir", default=None)
    a.add_argument("--sets", default=None, help="only these sets, comma separated (default all)")
    a.add_argument("--which", default=None, help="differences,questions (default both)")
    a.add_argument("--arms", default=None,
                   help="the vector text arms, e.g. 0,1 for the A/B on the same questions (default CRITIC_VECTOR_TEXT, "
                        "itself 0: the prompts as before)")
    v = sub.add_parser("vector", help="write the vector text data of an input set's levels (for a set already made)")
    v.add_argument("--inputs", default=str(INPUTS_DIR))
    v.add_argument("--sets", default=None, help="only these sets, comma separated (default all)")
    v.add_argument("--reading", action="append", default=[], metavar="FOLDER_OR_PROJECT=DIR",
                   help="a reading of an input folder (before/real09@324c487f) or of a project: its converted DXF, and "
                        "its walls where its rooms are the entry's")
    j = sub.add_parser("judge-prep", help="the judge inputs: RC18 (and RC17, RC14) findings of current readings")
    j.add_argument("--inputs", default=str(INPUTS_DIR))
    j.add_argument("--reading", action="append", default=[], metavar="PROJECT=DIR")
    ms = sub.add_parser("vt-measure", help="the vector text A/B prompt sets of an answered pod, measured on the CPU")
    ms.add_argument("--inputs", default=str(INPUTS_DIR))
    ms.add_argument("--index", default=None)
    ms.add_argument("--answers", required=True, help="the pod's answers.json the A arm repeats")
    ms.add_argument("--known", default=None)
    ms.add_argument("--json", default=None)
    sc = sub.add_parser("vt-score", help="recall, false findings and judge accuracy per arm of an A/B pod's answers")
    sc.add_argument("--inputs", default=str(INPUTS_DIR))
    sc.add_argument("--index", default=None)
    sc.add_argument("--answers", required=True)
    sc.add_argument("--known", default=None)
    sc.add_argument("--marks", default=None)
    sc.add_argument("--by-eye", dest="by_eye", default=None)
    sc.add_argument("--json", default=None)
    q = sub.add_parser("questions", help="print the question bank")
    c = sub.add_parser("calibrate", help="precision, recall and the out-of-sample table from the pod's answers")
    c.add_argument("--inputs", default=str(INPUTS_DIR))
    c.add_argument("--index", default=None, help="the index the answers were asked with (default <inputs>/index.json)")
    c.add_argument("--answers", required=True, help="the pod's answers.json")
    c.add_argument("--key", default=None)
    c.add_argument("--readings", action="append", default=[], metavar="SET/NAME=DIR",
                   help="the reading folder of an input folder (sets a and c; repeatable)")
    c.add_argument("--readings-root", dest="readings_root", default=None,
                   help="a folder holding readings as <set>/<name>/building.json")
    c.add_argument("--rc14", default=None, help="JSON {record id: RC14's answer} for the side-by-side")
    c.add_argument("--by-eye", dest="by_eye", default=None,
                   help="JSON of judgements from the drawing: {findings: {'<entry>#<rank>': {right, reason}}, "
                        "recall: {'<record>': {raised, reason}}}")
    c.add_argument("--no-records", dest="no_records", action="store_true")
    c.add_argument("--json", default=None, help="write the full table here")
    c.add_argument("--write", action="store_true", help=f"write {TRUST_PATH.name}")
    c.add_argument("--known", default=None, help=f"checks 1, 2, 4: the known errors (default {KNOWN_PATH.name})")
    c.add_argument("--marks", default=None, help=f"checks 1, 2, 4: the user's marks (default {MARKS_PATH.name})")
    c.add_argument("--review", default=None, help="checks 1, 2, 4: where the review sheets go (default "
                                                  "results/critic/review)")
    c.add_argument("--no-sheets", dest="no_sheets", action="store_true", help="no review sheets")
    c.add_argument("--arm", default=None, help="the arm of an A/B answers file (0, 1, text)")
    k = sub.add_parser("known", help="checks 1, 2, 4: the known errors of the before and after readings")
    k.add_argument("--inputs", default=str(INPUTS_DIR))
    k.add_argument("--pair", action="append", default=[], metavar="PROJECT=BEFORE_DIR,AFTER_DIR")
    k.add_argument("--out", default=None)
    m = sub.add_parser("mark", help="checks 1, 2, 4: the user's right / wrong marks of a review sheet's numbers")
    m.add_argument("--folder", required=True, help="the sheet's input folder, e.g. before/real09@324c487f")
    m.add_argument("--sheet", type=int, default=1)
    m.add_argument("--right", default="", help="numbers marked right, comma separated")
    m.add_argument("--wrong", default="", help="numbers marked wrong, comma separated")
    m.add_argument("--review", default=None)
    m.add_argument("--marks", default=None)
    s = sub.add_parser("store", help="write a reading's reading_check/critic.json from the pod's answers")
    s.add_argument("--inputs", default=str(INPUTS_DIR))
    s.add_argument("--answers", required=True)
    s.add_argument("--project", required=True)
    s.add_argument("--tag", default=None)
    s.add_argument("--key", default=None)
    s.add_argument("--out", required=True, help="the reading folder")
    args = ap.parse_args(argv)
    if args.cmd == "prepare":
        return _cmd_prepare(args)
    if args.cmd == "ask":
        return _cmd_ask(args)
    if args.cmd == "questions":
        for qq in reading_questions():
            print(f"{qq['id']}: {qq['ask']}")
        return 0
    if args.cmd == "calibrate":
        return _cmd_calibrate(args)
    if args.cmd == "store":
        return _cmd_store(args)
    if args.cmd == "known":
        return _cmd_known(args)
    if args.cmd == "mark":
        return _cmd_mark(args)
    if args.cmd in ("vector", "judge-prep", "vt-measure", "vt-score"):
        from wenart.reading_check import vector_measure as VM

        return VM.main_cmd(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
