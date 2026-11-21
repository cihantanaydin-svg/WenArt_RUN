"""The vector text's CPU side (21 Nov 2026, Milestone 14 queue item 3): ``critic vector`` (the vector files of an input
set already made), ``critic judge-prep`` (the judge inputs, ``critic_judge.prepare``), ``critic vt-measure`` (the A/B
prompt sets of every call of an answered pod, measured without a GPU) and ``critic vt-score`` (an A/B pod's answers,
scored per arm).

``measure`` builds, for every call the pod answered, the prompt of the A arm (``CRITIC_VECTOR_TEXT=0``: what round 2
asked) and of the B arm (``1``: the same question with its vector text), and reports their sizes (the token estimate
of ``vector_text``; the A arm checked against the server's own counts of the pod) and how many questions the text
alone answers: a lower bound on what the text adds, since the model also sees the images. ``text_answer`` (a compare
mark), ``evident`` (a known error) and ``judge_text_verdict`` (a judge item) read the listed items only, by fixed
rules; they are measuring sticks, never findings.

``score_arms`` scores each arm of an A/B answers file the way ``critic calibrate`` scores one pod: the known errors
found (recall), the findings judged wrong (by the user's marks, the synthetic truth, the known errors' fixed places,
and the eye judgements ``--by-eye``), the judge's accuracy on the labelled items.
"""
from __future__ import annotations

import json
import re
import statistics
from pathlib import Path
from typing import Optional

ROOM_TEXT_M = 1.2              # a drawing label this near a compare mark says the drawing has a room there
ANGLED_REACH_M = 0.6
OUTDOOR_REACH_M = 3.0
WINDOW_REACH_M = 0.8
DOOR_REACH_M = 1.0
EVIDENT_M = 1.5                # a drawing item this near a known error's place shows it
OPEN_AIR = ("balcony", "terrace", "loggia", "deck", "patio", "courtyard", "roof_terrace", "garden")


# ===================================================================================================== retrofit
def _cad_file(project: str) -> Optional[Path]:
    from wenart.reading_check.critic import REPO

    folder = REPO / "projects" / project
    cands = sorted(p for p in folder.glob("*") if p.suffix.lower() in (".dxf", ".dwg")) if folder.is_dir() else []
    return cands[0] if len(cands) == 1 else None


def retrofit(index: dict, inputs: Path, *, sets: Optional[list] = None, readings: Optional[dict] = None,
             log=print) -> dict:
    """The vector file of every level entry of ``sets`` (default all with ``facts``) of an input set already made
    (in place): the drawing's items from the project's own drawing (the converted DXF of a reading of it in
    ``readings`` = ``{project: dir}``, else the project's one DXF), clipped to the entry's frame (its box, its page
    transform); the reading's items from the entry's own ``facts`` (what the images were made of), and the walls of
    the given reading's level where its rooms are the entry's (else none listed). The floor texts get their page
    entry's file."""
    from wenart import reading_check as RC
    from wenart.ingest import dxf_generic
    from wenart.reading_check import vector_text as VT

    readings = readings or {}
    buildings = {k: json.loads((Path(d) / "building.json").read_text(encoding="utf-8")) for k, d in readings.items()}
    n = 0
    for e in index.get("entries") or []:
        if (sets and e.get("set") not in sets) or e.get("facts") is None:
            continue
        p = e["project"]
        key = e["folder"] if e["folder"] in buildings else p     # a reading of this input folder, else of the project
        fr = VT.Frame(e["box"], e["tf"])
        dxf, file_rel, walls = None, None, None
        b = buildings.get(key)
        if b is not None:
            pg = RC.level_pages(b).get(e["level"]) or next(iter(RC.level_pages(b).values()), None)
            if pg:
                file_rel = pg.get("file")
                dxf = RC.source_dxf(Path(readings[key]), file_rel)
            have = {r["id"] for r in b.get("rooms") or [] if r.get("level_id") == e["level"]}
            want = {r["id"] for r in e["facts"].get("rooms") or []}
            if want and len(have & want) >= 0.9 * len(want | have):
                walls = [w for w in b.get("walls") or [] if w.get("level_id") == e["level"]]
        if dxf is None:
            cad = _cad_file(p)
            if cad is not None and cad.suffix.lower() == ".dxf":
                dxf, file_rel = cad, cad.name
        page = None
        if dxf is not None:
            try:
                page = dxf_generic.read_page(str(dxf), file_rel, region_box=tuple(e["box"]), units_to_m_override=fr.s)
            except Exception as exc:  # noqa: BLE001 - a drawing that cannot be read: the reading's side only
                log(f"vector {e['id']}: drawing not read ({type(exc).__name__}: {str(exc)[:120]})")
        vec = VT.level_vector(page, fr, e["facts"], walls, RC.model_wall_layers(walls or []))
        name = re.sub(r"[^A-Za-z0-9_.-]", "_", e["level"]) + "_vector.json"
        VT.write_vector(Path(inputs) / e["folder"] / name, vec)
        e["vector"] = name
        n += 1
        log(f"vector {e['id']}: {len(vec['source'])} drawing items, {len(vec['reading'])} model items"
            + ("" if walls is not None else " (no model walls)") + ("" if page is not None else " (no drawing)"))
    byid = {e["id"]: e for e in index.get("entries") or []}
    for t in index.get("texts") or []:
        pe = byid.get(t.get("page_entry") or "")
        if pe is not None and pe.get("vector") and pe.get("folder") == t.get("folder"):
            t["vector"] = pe["vector"]
    log(f"vector: {n} level file(s)")
    return index


# ============================================================================================== the prompt sets
def prompt_of(which: str, item: dict, images_root: Path, part: int, vt: str) -> dict:
    """The prompt text, the image sizes and the vector numbers of one call under the switch ``vt`` (pure but for the
    vector file), as ``critic._check_messages`` builds them (images not drawn)."""
    from wenart.reading_check import critic as CR
    from wenart.reading_check import critic_checks as CC
    from wenart.reading_check import critic_judge as CJ

    size = tuple(item.get("size") or (CR.MAX_SIDE, CR.MAX_SIDE))
    if which == "plausibility":
        base, sizes, ans, chunk = CC.plausibility_prompt(item), [], CC.CALL_MAX_TOKENS[which], None
    elif which == "inventory":
        base, sizes, ans, chunk = CC.inventory_prompt(item), [size], CC.CALL_MAX_TOKENS[which], None
    elif which == "compare":
        chunk = CC.chunks_of(item)[part]
        base, sizes, ans = CC.compare_prompt(item, chunk), [size, size], CC.CALL_MAX_TOKENS[which]
    elif which == "second":
        base, sizes, ans, chunk = CC.second_prompt(item), [(CC.SECOND_OUT_PX, CC.SECOND_OUT_PX)], 64, None
    elif which == "judge":
        base, sizes, ans, chunk = CJ.prompt(item), [(CJ.OUT_PX, CJ.OUT_PX)] * 2, CJ.MAX_TOKENS, None
    else:
        raise ValueError(which)
    blk = CR._vector(which, item, images_root, base, ans, sizes, vt, chunk=chunk)
    text = (blk or {}).get("text")
    full = {"plausibility": lambda: CC.plausibility_prompt(item, text),
            "inventory": lambda: CC.inventory_prompt(item, text),
            "compare": lambda: CC.compare_prompt(item, chunk, text), "second": lambda: CC.second_prompt(item, text),
            "judge": lambda: CJ.prompt(item, text)}[which]()
    return {"text": full, "sizes": sizes, "answer": ans, "block": blk}


def prompt_tokens(p: dict) -> int:
    """The prompt's estimated tokens: the system text, the prompt, the image labels and the images."""
    from wenart.reading_check import critic_checks as CC
    from wenart.reading_check import vector_text as VT

    return VT.estimate_tokens(CC.SYSTEM_TEXT + " " + p["text"]) + 12 * len(p["sizes"]) \
        + sum(VT.image_tokens(s) for s in p["sizes"])                    # an image's label about 12 tokens


def _near(items: list, kinds: tuple, p, reach: float, test=None) -> list:
    from wenart.reading_check import vector_text as VT

    return sorted(((VT._dist(it, p), it) for it in items if it["k"] in kinds and (test is None or test(it))
                   and VT._dist(it, p) <= reach), key=lambda t: t[0])


def _outdoor_label(it: dict) -> bool:
    return bool(it.get("exterior")) or str(it.get("type") or "") in OPEN_AIR


def text_answer(q: dict, items: list, p) -> Optional[str]:
    """The drawing answer of a compare mark that the listed drawing ``items`` alone give (pure; ``p`` the mark in frame
    metres), None when they cannot say: a room label at the mark (a room); a wall pair at the mark at an angle, or
    only on the axes (angled or not); an outdoor label in front of a door (a balcony); a window symbol or a door arc at
    the mark (a window or door; an opening's type)."""
    from wenart.reading_check import vector_text as VT

    k = q["kind"]
    if k == "room":
        return "yes" if _near(items, ("T",), p, ROOM_TEXT_M, lambda it: not _outdoor_label(it)) else None
    if k == "angled":
        ws = _near(items, ("W",), p, ANGLED_REACH_M)
        if not ws:
            return None
        return "yes" if any(VT._off_axis(it.get("deg") or 0.0) > 3.0 for _d, it in ws) else "no"
    if k == "balcony":
        return "yes" if _near(items, ("T",), p, OUTDOOR_REACH_M, _outdoor_label) else None
    if k == "window":
        return "yes" if _near(items, ("G",), p, WINDOW_REACH_M) or \
            _near(items, ("A",), p, DOOR_REACH_M, lambda it: it.get("door")) else None
    if k == "opening":
        door = _near(items, ("A",), p, DOOR_REACH_M, lambda it: it.get("door"))
        win = _near(items, ("G",), p, 0.5)
        if door and (not win or door[0][0] <= win[0][0]):
            return "door"
        if win:
            return "window"
        return None
    return None


def _angled(it: dict) -> bool:
    from wenart.reading_check import vector_text as VT

    return VT._off_axis(it.get("deg") or 0.0) > 3.0


EVIDENT_KINDS = {
    "room_missing": (("T",), lambda it: not _outdoor_label(it)),
    "mirror_twin_missing": (("T",), lambda it: not _outdoor_label(it)),
    "balcony_missing": (("T",), _outdoor_label),
    "stair_missing": (("S",), None),
    "angled_wall_straight": (("W",), _angled),
    "opening_type_differs": (("G", "A"), None),
    "window_missing": (("G", "A"), None),
    "kitchen_no_window": (("G",), None),
    "habitable_no_window": (("G",), None),
    "door_into_air": (("T",), _outdoor_label),
    "room_not_in_drawing": (("T",), None),
    "opening_not_in_drawing": (("G", "A"), None),
}


def evident(kinds: list, items: list, p, reach: float = EVIDENT_M) -> Optional[bool]:
    """Whether the listed drawing ``items`` show a known error of these ``kinds`` at ``p`` (pure): an item of the
    kinds' drawing class within ``reach`` (a label for a missing room, an outdoor label for a balcony, stair lines, a
    wall pair at an angle, a window symbol or door arc for an opening or a window); None for kinds the drawing's items
    cannot show (a storey count)."""
    out = None
    for k in kinds or []:
        rule = EVIDENT_KINDS.get(k)
        if rule is None:
            continue
        out = bool(out) or bool(_near(items, rule[0], p, reach if k not in ("kitchen_no_window", "habitable_no_window")
                                      else 3.0, rule[1]))
    return out


def judge_text_verdict(item: dict, vec: dict, listed: set, limits: Optional[dict] = None) -> Optional[str]:
    """The judge verdict the listed items alone give, for the three rules judged by eye (pure): ``room_min_size``: the
    drawing's own area text in the room under the limit (a real breach) or not (a reading error); ``light_air``: a
    window symbol on the room's outline (a reading error) or none (real); ``light_well_size``: a label in the well
    naming another room type (a reading error). None otherwise."""
    from shapely.geometry import Point, Polygon

    from wenart.reading_check import vector_text as VT

    fr = VT.frame_of(vec)
    room = next((it for it in vec.get("reading") or [] if it["k"] in ("r", "b") and it.get("bid") in
                 (item.get("element_ids") or [])), None)
    if room is None:
        p = fr.from_building(item["at"])
        room = next((it for it in vec.get("reading") or [] if it["k"] == "r"
                     and Polygon(it["poly"]).buffer(0).contains(Point(p))), None)
    if room is None:
        return None
    g = Polygon(room["poly"]).buffer(0)
    src = [it for it in vec.get("source") or [] if it["id"] in listed]
    inside = [it for it in src if it["k"] in ("T", "M") and g.buffer(0.1).contains(Point(it["p"]))]
    rule = item.get("rule")
    if rule == "room_min_size":
        areas = [float(it["area"]) for it in inside if it.get("area")]
        lim = (limits or {}).get(item.get("limit") or "") or {}
        need = lim.get("value") if isinstance(lim.get("value"), (int, float)) else (lim.get("min_area") or None)
        if not areas or not isinstance(need, (int, float)):
            return None
        return "real_breach" if max(areas) < float(need) else "reading_error"
    if rule == "light_air":
        edge = [it for it in src if it["k"] in ("G",) and g.boundary.distance(Point(it["p"])) <= VT.EDGE_M]
        return "reading_error" if edge else "real_breach"
    if rule == "light_well_size":
        labs = [it for it in inside if it["k"] == "T" and it.get("type")]
        if any(str(it["type"]) not in ("light_well", "shaft", "other", "unknown") for it in labs):
            return "reading_error"                              # the drawing names another room there
        texts = [str(it.get("text") or "") for it in src if it["k"] in ("T", "X")
                 and g.buffer(0.3).contains(Point(it["p"]))]
        sizes = [(int(a), int(b)) for t in texts for a, b in re.findall(r"(\d{2,3})\s*[*xX/]\s*(\d{2,3})", t)]
        narrow = ((limits or {}).get(item.get("limit") or "") or {}).get("narrow")
        if sizes and isinstance(narrow, (int, float)):
            n = min(min(s) for s in sizes) / 100.0              # written in centimetres (50*65, H.B 50/50)
            return "real_breach" if n < float(narrow) else "reading_error"
        return None
    return None


def _quantiles(xs: list) -> dict:
    if not xs:
        return {"n": 0}
    return {"n": len(xs), "median": round(statistics.median(xs)), "max": max(xs), "min": min(xs)}


def measure(index: dict, inputs: Path, answers: dict, *, known: Optional[dict] = None,
            judgements: Optional[list] = None, log=print) -> dict:
    """The A/B prompt sets of every call ``answers`` holds (plus the judge items and the second looks the next pod
    asks), measured (the module docstring). ``judgements``: the pod's calibration (``calibrate_checks``'s
    ``judgements``) for the compare marks' truth; ``known``: the known errors."""
    from wenart.reading_check import critic as CR
    from wenart.reading_check import critic_checks as CC
    from wenart.reading_check import vector_text as VT

    items = {e["id"]: e for e in index.get("entries") or []}
    items.update({t["id"]: t for t in index.get("texts") or []})
    calls = [(a["which"], items[a["id"]], int(a.get("part") or 0), a) for a in answers.get("answers") or []
             if a.get("which") in CC.CHECKS and a.get("id") in items]
    found = [f for f in CR.answers_to_findings(index, answers) if f.get("call") in CC.CHECKS and not f.get("dropped")]
    second = CC.second_look_items(index, found)
    for it in second:
        e = items.get(it["id"].split("|")[0]) or {}
        it.setdefault("vector", e.get("vector"))
        it.setdefault("size", e.get("size"))
    calls += [("second", it, 0, None) for it in second]
    calls += [("judge", it, 0, None) for it in index.get("judge") or []]
    rows = []
    est_err = []
    for which, it, part, a in calls:
        pa, pb = prompt_of(which, it, inputs, part, "0"), prompt_of(which, it, inputs, part, "1")
        ta, tb = prompt_tokens(pa), prompt_tokens(pb)
        real = ((a or {}).get("usage") or {}).get("prompt_tokens")
        if real:
            est_err.append((ta - real) / real)
        blk = pb["block"] or {}
        rows.append({"which": which, "id": it["id"], "part": part, "a_tokens": ta, "b_tokens": tb, "server_a": real,
                     "vector_tokens": blk.get("tokens") or 0, "listed": blk.get("listed") or 0,
                     "left_out": blk.get("left_out") or 0, "cap": blk.get("cap"),
                     "b_total": tb + pb["answer"], "has_vector": bool(blk)})
    sizes = {}
    for w in ("inventory", "compare", "plausibility", "second", "judge"):
        rs = [r for r in rows if r["which"] == w]
        if not rs:
            continue
        sizes[w] = {"calls": len(rs), "with_vector": sum(1 for r in rs if r["has_vector"]),
                    "a_tokens": _quantiles([r["a_tokens"] for r in rs]),
                    "b_tokens": _quantiles([r["b_tokens"] for r in rs]),
                    "vector_tokens": _quantiles([r["vector_tokens"] for r in rs if r["has_vector"]]),
                    "b_prompt_plus_answer_max": max(r["b_total"] for r in rs),
                    "cut_by_cap": sum(1 for r in rs if r["left_out"]),
                    "server_a": _quantiles([r["server_a"] for r in rs if r["server_a"]])}
    lower = lower_bound(index, inputs, answers, judgements=judgements, known=known)
    return {"calls": len(rows), "context": VT.CONTEXT_TOKENS, "cap": VT.CAP_TOKENS, "sizes": sizes,
            "estimate_vs_server_a": {"calls": len(est_err),
                                     "mean_over": round(statistics.mean(est_err), 3) if est_err else None,
                                     "min": round(min(est_err), 3) if est_err else None,
                                     "max": round(max(est_err), 3) if est_err else None},
            "lower_bound": lower, "rows": rows}


def lower_bound(index: dict, inputs: Path, answers: dict, *, judgements: Optional[list] = None,
                known: Optional[dict] = None) -> dict:
    """How many questions the B arm's text alone answers (the module docstring)."""
    from wenart.reading_check import critic as CR
    from wenart.reading_check import critic_checks as CC
    from wenart.reading_check import critic_judge as CJ
    from wenart.reading_check import regulations as RG
    from wenart.reading_check import vector_text as VT

    items = {e["id"]: e for e in index.get("entries") or []}
    jby = {j["id"]: j for j in judgements or []}
    comp = {"marks": 0, "answered_by_text": 0, "by_kind": {}, "finding_right": 0, "finding_right_text_agrees": 0,
            "finding_wrong": 0, "finding_wrong_text_refutes": 0, "no_finding_text_differs": 0}
    for a in answers.get("answers") or []:
        if a.get("which") != "compare" or a.get("id") not in items:
            continue
        e = items[a["id"]]
        vec = VT.load_vector(inputs, e)
        if vec is None:
            continue
        chunk = CC.chunks_of(e)[int(a.get("part") or 0)]
        p = CR._vector("compare", e, inputs, CC.compare_prompt(e, chunk), CC.CALL_MAX_TOKENS["compare"],
                       [tuple(e["size"])] * 2, "1", chunk=chunk)
        listed = set((p or {}).get("ids") or [])
        src = [it for it in vec["source"] if it["id"] in listed]
        fr = VT.frame_of(vec)
        drew = {x.get("id"): x for x in CC._first_answers(a.get("data") or {})}
        for q in chunk:
            comp["marks"] += 1
            t = text_answer(q, src, fr.from_building(q["at"]))
            k = comp["by_kind"].setdefault(q["kind"], {"marks": 0, "answered_by_text": 0})
            k["marks"] += 1
            if t is None:
                continue
            comp["answered_by_text"] += 1
            k["answered_by_text"] += 1
            j = jby.get(f"{e['id']}|compare|{q['qid']}")
            dr = (drew.get(q["qid"]) or {}).get("drawing")
            if j is not None and j.get("right") is True:
                comp["finding_right"] += 1
                comp["finding_right_text_agrees"] += int(t == dr)
            elif j is not None and j.get("right") is False:
                comp["finding_wrong"] += 1
                comp["finding_wrong_text_refutes"] += int(t == q["model_fact"] or (q["kind"] == "opening" and t != dr))
            elif j is None and t != q["model_fact"] and q["kind"] in ("room", "angled", "opening") \
                    and not (q["kind"] == "room" and q["model_fact"] == "yes"):
                comp["no_finding_text_differs"] += 1
    # the known errors: shown by the listed items of the page image's whole-level block (inventory) or the marks'
    rows = []
    sf = CC.stands_for(index)
    for folder, ks in (known or {}).items():
        es = [e for e in index.get("entries") or [] if e.get("folder") == folder and e.get("vector")]
        for k in ks:
            if k.get("fixed"):
                continue
            hit = None
            for e in es:
                if k.get("level") and k["level"] not in (sf.get(e["id"]) or {e["level"]}):
                    continue
                if k.get("at") is None:
                    continue
                vec = VT.load_vector(inputs, e)
                fr = VT.frame_of(vec)
                p = fr.from_building(k["at"])
                # what a B call about this place lists: the items within the focus reach of the place
                near = VT.block(vec, focus=[("p", p)], cap_tokens=VT.CAP_TOKENS)
                listed = set(near["ids"])
                v = evident(k.get("kinds"), [it for it in vec["source"] if it["id"] in listed], p)
                hit = v if hit is None else (hit or bool(v))
            rows.append({"id": k["id"], "folder": folder, "kinds": k.get("kinds"), "desc": k.get("desc"),
                         "evident_in_text": hit})
    known_res = {"errors": len(rows), "evident": sum(1 for r in rows if r["evident_in_text"]),
                 "not_shown_by_drawing_items": sum(1 for r in rows if r["evident_in_text"] is None), "rows": rows}
    # the judge's labelled items
    limits = RG.load_limits()
    jrows = []
    for it in index.get("judge") or []:
        if not it.get("label"):
            continue
        vec = VT.load_vector(inputs, it)
        if vec is None:
            continue
        blk = CR._vector("judge", it, inputs, CJ.prompt(it), CJ.MAX_TOKENS, [(CJ.OUT_PX, CJ.OUT_PX)] * 2, "1")
        v = judge_text_verdict(it, vec, set((blk or {}).get("ids") or []), _limits_flat(limits))
        jrows.append({"id": it["id"], "check": it["check"], "rule": it["rule"], "label": it["label"], "text_verdict": v,
                      "right": None if v is None else v == it["label"]})
    judge = {"labelled": len(jrows), "decided_by_text": sum(1 for r in jrows if r["text_verdict"]),
             "right": sum(1 for r in jrows if r["right"]), "rows": jrows}
    return {"compare": comp, "known_errors": known_res, "judge": judge}


def _limits_flat(limits: dict) -> dict:
    """``{limit id: {"value": the minimum area, "narrow": the minimum narrow side}}`` (``regulations_tr.json``'s own
    fields; a limit by storeys, its lowest band: the bound every building must keep)."""
    out = {}
    for lid, lim in (limits or {}).items():
        band = lim.get("low") if isinstance(lim.get("low"), dict) else lim
        area, narrow = band.get("min_area_m2"), band.get("min_narrow_side_m")
        out[lid] = {"value": float(area) if isinstance(area, (int, float)) else None,
                    "narrow": float(narrow) if isinstance(narrow, (int, float)) else None}
    return out


# ======================================================================================================= scoring
def score_arms(index: dict, answers: dict, *, known: Optional[dict] = None, marks: Optional[dict] = None,
               by_eye: Optional[dict] = None) -> dict:
    """Per arm of an A/B answers file (``critic.split_arms``): the known errors found (``calibrate_checks``' recall),
    the findings judged wrong (marks, synthetic truth, fixed places, then the eye judgements ``by_eye`` =
    ``{"findings": {finding id or '<entry>#<rank>': {"right": bool}}}``), the findings not judged, and the judge's
    accuracy on the labelled items (``critic_judge.accuracy``)."""
    from wenart.reading_check import critic as CR
    from wenart.reading_check import critic_checks as CC
    from wenart.reading_check import critic_judge as CJ

    eye = (by_eye or {}).get("findings") or {}
    out = {}
    for arm, part in CR.split_arms(answers).items():
        found_all = [f for f in CR.answers_to_findings(index, part) if f.get("call") in CC.CHECKS]
        found = [f for f in found_all if not f.get("dropped")]
        dropped = [f for f in found_all if f.get("dropped")]
        cal = CC.calibrate_checks(index, found, part, known=known or {}, marks=marks or {}, dropped=dropped)
        judged = [j for j in cal["judgements"] if not j.get("dropped")]
        for j in judged:
            ey = eye.get(j["id"])
            if ey is not None and j.get("by") != "user":
                j.update(right=bool(ey.get("right")), by="eye")
        rows = cal["recall"]["rows"]
        targeted = [r for r in rows if r.get("targeted")]
        wrong = [j for j in judged if j.get("right") is False]
        by_kind: dict = {}
        for j in judged:
            k = by_kind.setdefault(f"{j['check']}:{j['kind']}", {"findings": 0, "right": 0, "wrong": 0})
            k["findings"] += 1
            k["right"] += int(j.get("right") is True)
            k["wrong"] += int(j.get("right") is False)
        verdicts = CJ.verdicts(index, part)
        out[str(arm)] = {"answered": sum(1 for a in part.get("answers") or [] if a.get("data") is not None),
                         "failed": sum(1 for a in part.get("answers") or [] if a.get("data") is None
                                       and not a.get("skipped")),
                         "skipped": sum(1 for a in part.get("answers") or [] if a.get("skipped")),
                         "findings": len(found), "dropped_by_second_look": len(dropped),
                         "known_errors": len(rows), "targeted": len(targeted),
                         "found": sum(1 for r in rows if r["found_by"]),
                         "found_ids": sorted(r["id"] for r in rows if r["found_by"]),
                         "false_findings": len(wrong),
                         "right_findings": sum(1 for j in judged if j.get("right") is True),
                         "not_judged": sum(1 for j in judged if j.get("right") is None),
                         "false_ids": sorted(j["id"] for j in wrong), "by_kind": by_kind,
                         "judge": CJ.accuracy(verdicts), "judge_rows": verdicts,
                         "vector_tokens": _quantiles([int((a.get("vector") or {}).get("tokens") or 0)
                                                      for a in part.get("answers") or [] if a.get("vector")])}
    arms = sorted(out)
    if len(arms) == 2:
        a, b = (out[x] for x in arms)
        out["delta"] = {"found_only_" + arms[1]: sorted(set(b["found_ids"]) - set(a["found_ids"])),
                        "found_only_" + arms[0]: sorted(set(a["found_ids"]) - set(b["found_ids"])),
                        "false_only_" + arms[0]: len(set(a["false_ids"]) - set(b["false_ids"])),
                        "false_only_" + arms[1]: len(set(b["false_ids"]) - set(a["false_ids"]))}
    return out


def score_table(res: dict) -> str:
    """The per-arm scores as a short markdown table."""
    arms = [a for a in res if a != "delta"]
    lines = ["| arm | answered | findings | known errors found | false findings | right | not judged | judge RC18 | "
             "judge all |", "|---|---|---|---|---|---|---|---|---|"]
    for a in arms:
        r = res[a]
        j18, ja = (r["judge"].get("RC18") or {}), (r["judge"].get("all") or {})
        jt = lambda j: f"{j.get('right', 0)}/{j.get('labelled', 0)}" if j.get("labelled") else "-"  # noqa: E731
        lines.append(f"| {a} | {r['answered']} | {r['findings']} | {r['found']}/{r['targeted']} | "
                     f"{r['false_findings']} | "
                     f"{r['right_findings']} | {r['not_judged']} | {jt(j18)} | {jt(ja)} |")
    if "delta" in res:
        lines.append("")
        lines.append("delta: " + "; ".join(f"{k} {v}" for k, v in res["delta"].items()))
    return "\n".join(lines)


# =========================================================================================================== CLI
def _readings(items: list) -> dict:
    """``{key: dir}`` of ``KEY=DIR`` items; a key is an input folder (``before/real09@324c487f``) or a project."""
    out = {}
    for x in items or []:
        k, _, d = x.partition("=")
        out[k] = d
    return out


def main_cmd(args) -> int:
    from wenart.reading_check import critic as CR
    from wenart.reading_check import critic_checks as CC

    inputs = Path(args.inputs)
    if args.cmd == "vector":
        index = CR.load_index(inputs)
        sets = [s for s in (args.sets or "").split(",") if s] or None
        retrofit(index, inputs, sets=sets, readings=_readings(args.reading))
        (inputs / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        return 0
    if args.cmd == "judge-prep":
        from wenart.reading_check import critic_judge as CJ

        rds = [{"project": p, "out_dir": d} for p, d in _readings(args.reading).items()]
        index = CJ.prepare(rds, inputs)
        print(f"judge: {len(index.get('judge') or [])} item(s), "
              f"{sum(1 for x in index.get('judge') or [] if x.get('label'))} labelled")
        return 0
    index = json.loads(Path(args.index).read_text(encoding="utf-8")) if args.index else CR.load_index(inputs)
    answers = json.loads(Path(args.answers).read_text(encoding="utf-8"))
    kp = Path(args.known or CR.KNOWN_PATH)
    known = json.loads(kp.read_text(encoding="utf-8")).get("readings") if kp.is_file() else {}
    if args.cmd == "vt-measure":
        part = next(iter(CR.split_arms(answers).values()))
        found = [f for f in CR.answers_to_findings(index, part) if f.get("call") in CC.CHECKS and not f.get("dropped")]
        cal = CC.calibrate_checks(index, found, part, known=known)
        res = measure(index, inputs, part, known=known, judgements=cal["judgements"])
        print(measure_table(res))
        if args.json:
            Path(args.json).write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        return 0
    mp = Path(args.marks or CR.MARKS_PATH)
    marks = json.loads(mp.read_text(encoding="utf-8")).get("marks") if mp.is_file() else {}
    by_eye = json.loads(Path(args.by_eye).read_text(encoding="utf-8")) if args.by_eye else None
    res = score_arms(index, answers, known=known, marks=marks, by_eye=by_eye)
    print(score_table(res))
    if args.json:
        Path(args.json).write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


def measure_table(res: dict) -> str:
    lines = [f"calls {res['calls']}; context {res['context']}, cap {res['cap']} tokens per text block; the A arm's "
             f"estimate against the server: mean {res['estimate_vs_server_a']['mean_over']:+.0%} "
             f"({res['estimate_vs_server_a']['min']:+.0%} to {res['estimate_vs_server_a']['max']:+.0%}) on "
             f"{res['estimate_vs_server_a']['calls']} calls" if res["estimate_vs_server_a"]["calls"] else
             f"calls {res['calls']}",
             "| call | calls | with text | A tokens median/max | B tokens median/max | text median/max | cut by cap | "
             "B + answer max |", "|---|---|---|---|---|---|---|---|"]
    for w, s in res["sizes"].items():
        q = lambda d: f"{d.get('median', '-')}/{d.get('max', '-')}"  # noqa: E731
        lines.append(f"| {w} | {s['calls']} | {s['with_vector']} | {q(s['a_tokens'])} | {q(s['b_tokens'])} | "
                     f"{q(s['vector_tokens'])} | {s['cut_by_cap']} | {s['b_prompt_plus_answer_max']} |")
    lb = res["lower_bound"]
    c = lb["compare"]
    lines.append("")
    lines.append(f"compare marks answered by the text alone: {c['answered_by_text']} of {c['marks']} ("
                 + ", ".join(f"{k} {v['answered_by_text']}/{v['marks']}" for k, v in c["by_kind"].items()) + ")")
    lines.append(f"  right findings the text agrees with: {c['finding_right_text_agrees']} of {c['finding_right']}; "
                 f"false findings the text refutes: {c['finding_wrong_text_refutes']} of {c['finding_wrong']}; marks "
                 f"with no finding where the text differs from the reading: {c['no_finding_text_differs']}")
    k = lb["known_errors"]
    lines.append(f"known errors shown by the listed drawing items: {k['evident']} of {k['errors']} "
                 f"({k['not_shown_by_drawing_items']} of a kind no drawing item shows)")
    j = lb["judge"]
    lines.append(f"judge items decided by the text alone: {j['decided_by_text']} of {j['labelled']} labelled, "
                 f"{j['right']} right")
    return "\n".join(lines)
