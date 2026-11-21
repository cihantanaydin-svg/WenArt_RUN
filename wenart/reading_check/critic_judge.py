"""RC15's judge (21 Nov 2026, Milestone 14 queue item 3): the vision model judges a code check's finding.

What: a finding of RC18 (the Turkish regulations), and in the queue RC17 (structure) and RC14 (architectural sense),
says the model of the building breaks a rule at a place. The judge call shows the model two close-ups of that place
(the architect's drawing and the computer's model, the same crop, a red ring at the place) with the finding's message,
the rule and, with ``CRITIC_VECTOR_TEXT``, the vector text of the crop (``vector_text.question_block``), and asks for
one verdict: ``real_breach`` (the drawing itself has the problem; the model follows the drawing), ``reading_error`` (the
model misreads the drawing there; the drawing is fine) or ``unclear``, with one short reason.

Why: RC18's findings are a reading error about half the time (the judged sample of 21 Nov 2026: 7 real breaches, 7
reading errors, 1 case the check cannot settle, ``models/regulations_judged.json``); a finding the reading caused points
at the reading's fault, one the drawing has is the architect's. The 15 eye-judged findings are the first labels; RC14's
judged findings (``models/sense_trust.json``: right means a reading error) label the RC14 items where the current
reading still makes them; RC17's go in unlabelled (queued for the user's marks).

How: ``prepare`` (CPU) reads RC18, RC17 and RC14 on each reading, renders every level with a finding (the page level a
copy storey stands for) into ``<inputs>/judge/<project>/`` with its vector file, and adds the items to the index under
``judge`` (set ``judge``; the level entries are ``judge_only``: no inventory or compare call is asked of them). The pod
asks ``critic ask --which judge``; ``verdicts`` and ``accuracy`` read the answers (``vector_measure.score_arms``).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

SET = "judge"
VERDICTS = ("real_breach", "reading_error", "unclear")
LABEL_MAP = {"real": "real_breach", "reading": "reading_error", "strict": "unclear"}
MAX_TOKENS = 384
OUT_PX = 900                   # the long side of each close-up sent
CROP_MIN_M = 6.0               # a close-up is at least this wide and high (metres) ...
CROP_MARGIN_M = 1.5            # ... and shows the finding's room with this much around it
CAPS = {"RC18": 12, "RC17": 6, "RC14": 6}   # unlabelled items per project and check (labelled ones always go in)
REG_PATH = Path(__file__).resolve().parent / "models" / "regulations_judged.json"
SENSE_PATH = Path(__file__).resolve().parent / "models" / "sense_trust.json"
WHAT = {"RC18": "the Turkish building and fire regulations (PAIY, BYKHY)",
        "RC17": "the structural sense of a building (doors, slabs, outdoor spaces)",
        "RC14": "an architect's sense of a plan"}
RC17_RULES = {"door_into_air": "an exterior door above the ground with nothing to step onto",
              "slab_beyond_walls": "a floor slab open to the sky inside a storey's own walls",
              "outdoor_label_lost": "a balcony or terrace label in no outdoor space",
              "scale_misread": "a plan read at a wrong scale",
              "angled_wall_straight": "a wall drawn at an angle built straight or left out"}
SYSTEM_TEXT = ("You are a senior architect checking a computer's reading of an architectural floor plan. You answer "
               "only with the JSON the schema asks for. You point only at what you can see.")


def rule_text(check: str, rule: Optional[str]) -> str:
    if check == "RC18":
        from wenart.reading_check import regulations as RG

        return RG.RULES.get(rule or "", rule or "")
    if check == "RC14":
        from wenart.reading_check import sense as SN

        return SN.RULES.get(rule or "", rule or "")
    return RC17_RULES.get(rule or "", rule or "")


def schema() -> dict:
    return {"type": "object", "properties": {"verdict": {"type": "string", "enum": list(VERDICTS)},
                                             "reason": {"type": "string", "maxLength": 200}},
            "required": ["verdict", "reason"], "additionalProperties": False}


def prompt(item: dict, vector: Optional[str] = None) -> str:
    """The judge question of one finding (pure)."""
    from wenart.reading_check.critic_checks import with_vector

    msg = re.sub(r"\s+", " ", str(item.get("message") or "")).strip()[:600]
    return with_vector(
        f"Image 1 is a close-up of an architect's floor plan ({item.get('title') or 'a level'}); image 2 is a "
        f"computer's model of the same place drawn the same way (black walls, door swings, window symbols, room "
        f"labels), in the same frame. The red ring marks the place. A code check of the model against "
        f"{WHAT.get(item.get('check'), 'a rule')} reports there: \"{msg}\" (the rule: {item.get('rule_text')}).\n"
        f"Decide what causes the finding. real_breach: the drawing itself has this problem and the model follows the "
        f"drawing (a design fault or something the drawing leaves out). reading_error: the model misreads the drawing "
        f"there and the drawing does not have the problem (a window or door drawn but not read, a wall misplaced or "
        f"invented, a room typed or named wrong, a size misread, a facade not read). unclear: these close-ups cannot "
        f"settle it. Give one short reason naming what you saw.", vector)


# ===================================================================================================== the items
def _labels(path_reg: Path = REG_PATH, path_sense: Path = SENSE_PATH) -> tuple:
    reg, sense = {}, {}
    if Path(path_reg).is_file():
        for x in json.loads(Path(path_reg).read_text(encoding="utf-8")).get("judged") or []:
            reg[(x["project"], x["level"], x["id"], x["rule"])] = {"label": LABEL_MAP.get(x["verdict"]),
                                                                   "why": x.get("why")}
    if Path(path_sense).is_file():
        for j in json.loads(Path(path_sense).read_text(encoding="utf-8")).get("judgements") or []:
            parts = str(j.get("key") or "").split("|")
            if len(parts) < 5 or j.get("right") is None:
                continue
            ids = tuple(sorted(x for x in parts[4].split(",") if x))
            sense[(parts[0], parts[1], parts[2], ids)] = {
                "label": "reading_error" if j["right"] else "real_breach", "why": j.get("reason")}
    return reg, sense


def label_of(f: dict, project: str, reg: dict, sense: dict) -> Optional[dict]:
    """The eye judgement of a finding, if any (pure): RC18 by (project, level, element id, rule), RC14 by (project,
    level, rule, element ids)."""
    if f.get("check") == "RC18":
        for eid in f.get("element_ids") or []:
            hit = reg.get((project, f.get("level_id"), eid, f.get("rule")))
            if hit:
                return hit
        return None
    if f.get("check") == "RC14":
        return sense.get((project, f.get("level_id"), f.get("rule"), tuple(sorted(f.get("element_ids") or []))))
    return None


def _place(f: dict, rooms: dict) -> Optional[list]:
    if f.get("place"):
        return [float(f["place"][0]), float(f["place"][1])]
    for eid in f.get("element_ids") or []:
        r = rooms.get(eid)
        if r and len(r.get("polygon") or []) >= 3:
            from wenart.reading_check.critic_checks import _rep

            return _rep(r["polygon"])
    return None


def crop_of(frame, place, rooms: dict, element_ids: list) -> list:
    """The close-up of a finding in frame metres (pure): its rooms' extent with ``CROP_MARGIN_M`` around, at least
    ``CROP_MIN_M`` each way, centred on them, cut at the image's edges."""
    pts = [frame.from_building(q) for eid in element_ids or [] for q in (rooms.get(eid) or {}).get("polygon") or []]
    p = frame.from_building(place)
    pts = pts or [p]
    x0, y0 = min(q[0] for q in pts) - CROP_MARGIN_M, min(q[1] for q in pts) - CROP_MARGIN_M
    x1, y1 = max(q[0] for q in pts) + CROP_MARGIN_M, max(q[1] for q in pts) + CROP_MARGIN_M
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    hw, hh = max(CROP_MIN_M, x1 - x0) / 2.0, max(CROP_MIN_M, y1 - y0) / 2.0
    side = max(hw, hh)                                         # a square close-up: the model sees both ways alike
    box = [max(0.0, cx - side), max(0.0, cy - side), min(frame.w, cx + side), min(frame.h, cy + side)]
    return [round(v, 3) for v in box]


def items_of(building: dict, found: list, page_entries: dict, page_lv: dict, project: str, name: str,
             reg: dict, sense: dict, caps: Optional[dict] = None) -> list:
    """The judge items of one reading's findings (pure): ``page_entries`` = ``{page level: index entry}``,
    ``page_lv`` = ``{level: its page level}``. A finding with no place, or on a level with no page image, is left out;
    the labelled ones always go in, the others up to ``caps`` per check."""
    from wenart.reading_check import vector_text as VT

    caps = dict(CAPS, **(caps or {}))
    rooms = {r["id"]: r for r in building.get("rooms") or [] if r.get("id")}
    out, n = [], {}
    order = sorted(found, key=lambda f: (label_of(f, project, reg, sense) is None, f.get("check"), f.get("rule") or "",
                                         f.get("level_id") or "", ",".join(f.get("element_ids") or [])))
    for f in order:
        if f.get("check") not in caps or (f.get("severity") == "info" and not f.get("place")
                                          and not f.get("element_ids")):
            continue
        lab = label_of(f, project, reg, sense)
        if lab is None and n.get(f["check"], 0) >= caps[f["check"]]:
            continue
        page = page_lv.get(f.get("level_id"))
        e = page_entries.get(page)
        place = _place(f, rooms)
        if e is None or place is None:
            continue
        fr = VT.Frame(e["box"], e["tf"])
        q = fr.from_building(place)
        if not (0.0 <= q[0] <= fr.w and 0.0 <= q[1] <= fr.h):
            continue
        what = ",".join(f.get("element_ids") or []) or "%.1f,%.1f" % tuple(place)
        key = f"{f['check']}:{f.get('rule')}:{f.get('level_id')}:{what}"
        iid = f"{SET}/{name}#{key}"
        if any(x["id"] == iid for x in out):
            continue
        if lab is None:
            n[f["check"]] = n.get(f["check"], 0) + 1
        out.append({"id": iid, "set": SET, "project": project, "folder": e["folder"], "level": f.get("level_id"),
                    "page_level": page, "page_entry": e["id"], "drawing": e["drawing"], "model": e["model"],
                    "size": e["size"], "vector": e.get("vector"), "title": e.get("title"), "check": f["check"],
                    "rule": f.get("rule"), "rule_text": rule_text(f["check"], f.get("rule")), "limit": f.get("limit"),
                    "message": str(f.get("message") or "")[:600], "element_ids": list(f.get("element_ids") or []),
                    "at": [round(place[0], 3), round(place[1], 3)],
                    "crop": crop_of(fr, place, rooms, f.get("element_ids") or []),
                    "reading_suspect": bool(f.get("reading_suspect")),
                    "label": (lab or {}).get("label"), "label_why": (lab or {}).get("why")})
    return out


def findings_of(out_dir: Path, building: dict) -> list:
    """RC18, RC17 (rules on the building) and RC14 (with the drawing's texts) of one reading."""
    from wenart.reading_check import regulations as RG
    from wenart.reading_check import sense as SN
    from wenart.reading_check import structure as SR

    found = [f for f in RG.findings(building) if f.get("severity") != "info" or f.get("place")]
    try:
        found += SR.findings(building)
    except Exception:  # noqa: BLE001 - a structural rule that fails adds nothing here
        pass
    try:
        found += SN.findings(out_dir)
    except Exception:  # noqa: BLE001 - the sense rules need sheets and texts; without them nothing
        pass
    return found


def prepare(readings: list, dest: Path, *, labels: Optional[tuple] = None, caps: Optional[dict] = None,
            log=print) -> dict:
    """The judge inputs of ``readings`` = ``[{"project", "out_dir"}]`` (current readings): the findings, the page
    images and vector files of the levels they are on (set ``judge``, entries ``judge_only``), the items under
    ``index["judge"]`` (an item of the same id replaced). Returns the index."""
    from wenart import reading_check as RC
    from wenart.reading_check import critic as CR
    from wenart.reading_check import critic_checks as CC
    from wenart.reading_check import structure as SR
    from wenart.reading_check import vector_text as VT

    dest = Path(dest)
    index_path = dest / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.is_file() else {"entries": []}
    reg, sense = labels if labels is not None else _labels()
    byid = {e["id"]: e for e in index.get("entries") or []}
    items = {x["id"]: x for x in index.get("judge") or []}
    for rd in readings:
        out_dir = Path(rd["out_dir"])
        building = json.loads((out_dir / "building.json").read_text(encoding="utf-8"))
        sp = out_dir / "sheets.json"
        sheets = json.loads(sp.read_text(encoding="utf-8")) if sp.is_file() else {}
        name = rd["project"]
        found = findings_of(out_dir, building)
        bfacts = CC.building_facts(building)
        pages = RC.level_pages(building)
        page_lv = CC.page_levels(building, bfacts["levels"], set(pages))
        want = sorted({page_lv.get(f.get("level_id")) for f in found} - {None})
        shapes = SR.outlines(building)
        folder = dest / SET / name
        page_entries, docs = {}, {}
        for lid in want:
            e = CR.render_level(out_dir, lid, folder, building=building, sheets=sheets, docs=docs, model_style="arch")
            if e is None:
                continue
            pg = pages.get(lid) or {}
            try:
                page = RC.read_level_page(out_dir, sheets, pg)
            except Exception:  # noqa: BLE001 - no page: the reading's side only
                page = None
            facts = CC.level_facts(building, lid, outline=shapes.get(lid))
            walls = [w for w in building.get("walls") or [] if w.get("level_id") == lid]
            vec = VT.level_vector(page, VT.Frame(e["box"], e["tf"]), facts, walls, RC.model_wall_layers(walls))
            vname = re.sub(r"[^A-Za-z0-9_.-]", "_", lid) + "_vector.json"
            VT.write_vector(folder / vname, vec)
            e.update({"id": f"{SET}/{name}/{lid}", "set": SET, "project": name, "tag": "current",
                      "folder": f"{SET}/{name}", "vector": vname, "judge_only": True})
            byid[e["id"]] = e
            page_entries[lid] = e
        new = items_of(building, found, page_entries, page_lv, name, name, reg, sense, caps)
        for x in new:
            items[x["id"]] = x
        log(f"judge {name}: {len(found)} findings, {len(new)} items ({sum(1 for x in new if x['label'])} labelled) on "
            f"{len(page_entries)} level image(s)")
    index["entries"] = sorted(byid.values(), key=lambda e: e["id"])
    index["judge"] = sorted(items.values(), key=lambda x: x["id"])
    dest.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return index


# ================================================================================================= the ask path
def images(item: dict, images_root: Path, dest_dir: Path) -> list:
    """The two close-ups of a judge item (drawing, model) with a red ring at the place, ``OUT_PX`` on the long side
    (the crop is frame metres, the image's pixels the same box)."""
    from PIL import Image, ImageDraw

    from wenart.reading_check import vector_text as VT

    out = []
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", item["id"])[-120:]
    vec = VT.load_vector(images_root, item)
    W = float(((vec or {}).get("frame") or {}).get("w") or 0.0)
    H = float(((vec or {}).get("frame") or {}).get("h") or 0.0)
    for key in ("drawing", "model"):
        im = Image.open(Path(images_root) / item["folder"] / item[key]).convert("RGB")
        w, h = im.size
        if not (W and H):                                       # no vector file: the frame from the image's aspect
            W, H = float(w), float(h)
        x0, y0, x1, y1 = item["crop"]
        box = (int(x0 / W * w), int(y0 / H * h), max(int(x0 / W * w) + 1, int(x1 / W * w)),
               max(int(y0 / H * h) + 1, int(y1 / H * h)))
        c = im.crop(box)
        s = OUT_PX / float(max(c.size))
        c = c.resize((max(1, int(c.size[0] * s)), max(1, int(c.size[1] * s))), Image.LANCZOS)
        if vec is not None:
            p = VT.frame_of(vec).from_building(item["at"])
            px, py = (p[0] / W * w - box[0]) * s, (p[1] / H * h - box[1]) * s
            d = ImageDraw.Draw(c)
            d.ellipse([px - 22, py - 22, px + 22, py + 22], outline=(220, 0, 0), width=4)
        dest = Path(dest_dir) / f"{safe}_{key}.jpg"
        dest.parent.mkdir(parents=True, exist_ok=True)
        c.save(dest, quality=88)
        out.append(dest)
    return out


def verdicts(index: dict, answers: dict) -> list:
    """Each judge answer with its item's label (pure): ``[{id, check, rule, project, label, verdict, reason,
    right}]`` (``right`` None for an unlabelled item)."""
    items = {x["id"]: x for x in index.get("judge") or []}
    out = []
    for a in answers.get("answers") or []:
        if a.get("which") != "judge" or not isinstance(a.get("data"), dict):
            continue
        it = items.get(a.get("id"))
        if it is None:
            continue
        v = a["data"].get("verdict")
        out.append({"id": it["id"], "check": it["check"], "rule": it.get("rule"), "project": it["project"],
                    "label": it.get("label"), "verdict": v, "reason": a["data"].get("reason"),
                    "right": (v == it["label"]) if it.get("label") else None, "arm": a.get("arm")})
    return out


def accuracy(rows: list) -> dict:
    """Per check and in all: labelled items answered, right, and the confusion ``{label: {verdict: n}}`` (pure)."""
    out = {}
    for check in sorted({r["check"] for r in rows}) + ["all"]:
        rs = [r for r in rows if r.get("label") and (check == "all" or r["check"] == check)]
        conf: dict = {}
        for r in rs:
            conf.setdefault(r["label"], {}).setdefault(r["verdict"], 0)
            conf[r["label"]][r["verdict"]] += 1
        right = sum(1 for r in rs if r["right"])
        out[check] = {"labelled": len(rs), "right": right, "accuracy": round(right / len(rs), 3) if rs else None,
                      "confusion": conf, "answered": sum(1 for r in rows if check == "all" or r["check"] == check)}
    return out
