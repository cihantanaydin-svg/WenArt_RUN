"""The reading regression set (2 Nov 2026; user: "go ahead with all 4", "can we keep improving this regression set?").

What: ``python -m wenart.reading_check regress [--projects real02,real10] [--update] [--work DIR]`` reads every project
of the set (``results/reading_baseline/<project>.json``; ``--projects`` names others to add) with the CPU pipeline
(no AI answers, so a reading change is judged by itself), runs the reading check and compares the project's key numbers
with its baseline:

- exact: the levels, the levels left out, the reading's status, the check's verdict;
- within ``COUNT_TOL`` (a share, at least ``COUNT_MIN`` items): rooms, walls, doors, windows, openings per level;
- within ``AREA_TOL``: the room area per level;
- the check's critical findings never more, its stacking offsets never larger by ``STACK_TOL_M``.

27 Nov 2026 (audit fix round 4b: a section read mirrored and a flat roof read as a gambrel passed the set unseen): every
project also prints ``struct:`` lines (``structure`` / ``structure_lines``): each level's floor and ceiling height and
their source, the section's cut axis and flip, the roof as read (type, pitch, ridge and eaves heights) and as the build
derives it (eaves, ridge, pitch, ridge direction), and each stair's riser count and riser height as the build plans
them. They are additive: the lines above them are unchanged, so two logs compare line by line (``regcmp``); a baseline
written before them has no ``structure`` and is not compared on it; one written after (``--update``) is, as notes
("struct changed"), never as a regression.

A difference is printed per project and number; the command exits 1 when any project regressed. ``--update`` writes
the new numbers as the baseline (after a change the user accepted: the set keeps improving, one project at a time);
the user's acceptance fields of the old baseline (``ACCEPT_FIELDS``: ``accepted_by_user``, ``accepted_on``,
``accepted_scope``, ``accepted_levels``, ``accepted_note``; 5 Nov 2026, Milestone 14 R1) are carried over, because
an update follows the user's acceptance. Since 6 Nov 2026 no real acceptance stands: a real project's truth is the
user's correction records only (``truth.build_sparse``), and the baselines are a change detector.

Why: real10's reading fixes of 2 Nov 2026 broke 18 tests of real02, real06 and the wall rules before anyone saw it; a
rule for one project must never quietly change another.
"""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parents[2]
BASELINE_DIR = REPO / "results" / "reading_baseline"
PROJECTS_DIR = REPO / "projects"
COUNT_TOL = 0.10
COUNT_MIN = 2
AREA_TOL = 0.03
STACK_TOL_M = 0.05
PER_LEVEL = ("rooms", "walls", "doors", "windows", "openings")
ACCEPT_FIELDS = ("accepted_by_user", "accepted_on", "accepted_scope", "accepted_levels", "accepted_note",
                 "accepted_seen", "acceptance_withdrawn", "acceptance_history")


HEIGHT_TOL_M = 0.05           # 12 Nov 2026: a level, the datum or a slab moved more than this


def numbers(out_dir: Path) -> dict:
    """The key numbers of a pipeline output (the module docstring)."""
    from wenart import reading_check as RC

    out_dir = Path(out_dir)
    b = json.loads((out_dir / "building.json").read_text(encoding="utf-8"))
    res = RC.check(out_dir)
    per: dict = {}
    for lv in b.get("levels") or []:
        lid = lv["id"]
        rooms = [r for r in b.get("rooms") or [] if r.get("level_id") == lid]
        ops = [o for o in b.get("openings") or [] if o.get("level_id") == lid]
        per[lid] = {"rooms": len(rooms), "walls": sum(1 for w in b.get("walls") or [] if w.get("level_id") == lid),
                    "doors": sum(1 for o in ops if o.get("type") == "door"),
                    "windows": sum(1 for o in ops if o.get("type") == "window"),
                    "openings": sum(1 for o in ops if o.get("type") not in ("door", "window")),
                    "room_area": round(sum(float(r.get("area_computed") or 0) for r in rooms), 1)}
    stack = {f["level_id"]: f.get("offset_m") for f in res["findings"] if f["check"] == "RC2"}
    # 5 Nov 2026 (review): the levels built with reading_confidence low and their reasons are compared numbers too
    low = {lv["id"]: list(lv.get("reading_review") or []) for lv in b.get("levels") or []
           if lv.get("reading_confidence") == "low"}
    # 12 Nov 2026 (round-2 review, A2-FC10 / G9: a 7 m storey and a lost datum passed as '0 diffs'): the heights,
    # the datum, the slabs and the entrance solutions are compared numbers too
    heights = {lv["id"]: {"elevation": lv.get("elevation"), "source": lv.get("elevation_source")}
               for lv in b.get("levels") or []}
    datum = (b.get("project") or {}).get("datum")
    slabs = {s.get("id"): s.get("z_top") for s in b.get("slabs") or [] if isinstance(s, dict)}
    entrances = {e.get("door_id"): e.get("solution") for e in (b.get("site") or {}).get("entrances") or []
                 if isinstance(e, dict)}
    return {"project": (b.get("project") or {}).get("id"), "status": b.get("status"),
            "heights": heights, "datum": datum.get("relative", datum.get("value")) if isinstance(datum, dict) else None,
            "slabs": slabs, "entrances": entrances,
            "levels": [lv["id"] for lv in b.get("levels") or []],
            "levels_left_out": sorted(str(lo.get("label")) for lo in b.get("levels_left_out") or []),
            "low_confidence": low,
            "per_level": per, "check": {"verdict": res["verdict"], "counts": res["counts"], "stacking": stack},
            "structure": structure(out_dir, b)}


def _r(v, nd: int = 2):
    """A number rounded for the struct lines, or None."""
    return round(float(v), nd) + 0.0 if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def _val(entry):
    """``(value, method)`` of a building JSON value (a dict with value / method, or a bare number)."""
    if isinstance(entry, dict):
        return entry.get("value"), entry.get("method")
    return entry, None


def structure(out_dir: Path, b: dict) -> dict:
    """27 Nov 2026 (audit fix round 4b): the structure numbers of a reading (the module docstring): ``levels`` (floor,
    ceiling and their sources), ``section`` (cut axis, flip), ``roof`` (read and derived) and ``stairs`` (risers as the
    build plans them). A part that cannot be computed says why (``error``), never silently."""
    out: dict = {"levels": {}, "section": None, "roof": None, "stairs": {}}
    for lv in b.get("levels") or []:
        out["levels"][lv["id"]] = {"floor": _r(lv.get("elevation")), "floor_source": lv.get("elevation_source"),
                                   "ceiling": _r(lv.get("ceiling_height")),
                                   "ceiling_source": lv.get("ceiling_height_source")}
    try:
        sh = json.loads((Path(out_dir) / "sheets.json").read_text(encoding="utf-8"))
        h = sh.get("heights") or {}
        out["section"] = {"regions": list(h.get("section_regions") or []), "cut_axis": h.get("cut_axis"),
                          "cut_at": _r(h.get("cut_at")), "flipped": h.get("flipped")}
    except (OSError, ValueError) as exc:
        out["section"] = {"error": f"{type(exc).__name__}: {exc}"[:160]}
    roof = b.get("roof") if isinstance(b.get("roof"), dict) else None
    if roof:
        ridge, rm = _val(roof.get("ridge_height"))
        eaves, em = _val(roof.get("eaves_height"))
        pitches = [_r(_val(p)[0], 1) for p in roof.get("pitches_deg") or []]
        rec = {"type": roof.get("type"), "type_source": roof.get("type_source"), "pitches": pitches,
               "ridge": _r(ridge), "ridge_method": rm, "eaves": _r(eaves), "eaves_method": em,
               "ridge_lines": len(roof.get("ridge_lines") or [])}
        try:
            from wenart.blender import roof as RF
            d = RF.derive(roof, b)
            rec["built"] = {"eaves": _r(d.get("eaves_z")), "ridge": _r(d.get("ridge_z")),
                            "pitch": _r((d.get("pitches") or [None])[0], 1), "ridge_dir": _ridge_dir(d),
                            "raise": _r(next((a["value"] for a in d.get("assumed") or []
                                              if a.get("field") == "eaves_raise"), None))}
        except Exception as exc:  # noqa: BLE001 - listed in the struct line, never silent
            rec["built"] = {"error": f"{type(exc).__name__}: {exc}"[:160]}
        out["roof"] = rec
    try:
        from wenart.blender import shell
        for lv in b.get("levels") or []:
            for item in shell.plan_stairs(b, lv):
                plan, piece = item.get("plan"), item.get("piece") or {}
                if piece.get("type") != "stair":
                    continue
                if plan is None:
                    why = "arrives from below" if item.get("arrival") else str(item.get("reason") or "not built")
                    out["stairs"][piece.get("id")] = {"level": lv["id"], "risers": None, "riser": None,
                                                      "source": why[:40]}
                    continue
                out["stairs"][piece.get("id")] = {"level": lv["id"], "risers": plan.get("risers"),
                                                  "riser": _r(plan.get("riser_m"), 3),
                                                  "source": str(plan.get("riser_source") or "")[:40]}
    except Exception as exc:  # noqa: BLE001 - listed in the struct line, never silent
        out["stairs"] = {"error": f"{type(exc).__name__}: {exc}"[:160]}
    return out


def _ridge_dir(d: dict) -> Optional[str]:
    """The direction of the derived roof's highest edge (pure): 'x', 'y', an angle in degrees, 'point' (a pyramid) or
    None (a flat roof or no planes)."""
    import math
    top = d.get("ridge_z")
    if not isinstance(top, (int, float)) or d.get("eaves_z") == top:
        return None
    pts = {(round(q[0], 2), round(q[1], 2)) for pl in d.get("planes") or [] for q in pl.get("points") or []
           if len(q) >= 3 and abs(float(q[2]) - float(top)) <= 0.01}
    if len(pts) < 2:
        return "point" if pts else None
    a, c = max(((p, q) for p in pts for q in pts), key=lambda pq: math.dist(*pq))
    if math.dist(a, c) < 0.05:
        return "point"
    ang = math.degrees(math.atan2(c[1] - a[1], c[0] - a[0])) % 180.0
    if min(ang, 180.0 - ang) <= 1.0:
        return "x"
    if abs(ang - 90.0) <= 1.0:
        return "y"
    return f"{ang:.0f} deg"


def structure_lines(st: Optional[dict]) -> list[str]:
    """The ``struct:`` lines of ``structure`` (pure; stable formatting, one fact per line)."""
    if not isinstance(st, dict):
        return []
    f = (lambda v, fmt="{:+.2f}": "-" if v is None else fmt.format(v))
    out = []
    for lid, lv in (st.get("levels") or {}).items():
        out.append(f"{lid} floor {f(lv.get('floor'))} ({lv.get('floor_source')}) ceiling "
                   f"{f(lv.get('ceiling'), '{:.2f}')} ({lv.get('ceiling_source')})")
    sec = st.get("section") or {}
    if "error" in sec:
        out.append(f"section: {sec['error']}")
    else:
        out.append(f"section {','.join(sec.get('regions') or []) or '-'}: cut axis {sec.get('cut_axis')} at "
                   f"{f(sec.get('cut_at'), '{:.2f}')} flipped {sec.get('flipped')}")
    roof = st.get("roof")
    if roof:
        out.append(f"roof read: {roof.get('type')} ({roof.get('type_source')}) pitch "
                   f"{','.join(f(p, '{:.1f}') for p in roof.get('pitches') or []) or '-'} ridge "
                   f"{f(roof.get('ridge'))} ({roof.get('ridge_method')}) eaves {f(roof.get('eaves'))} "
                   f"({roof.get('eaves_method')}) ridge lines {roof.get('ridge_lines')}")
        built = roof.get("built") or {}
        if "error" in built:
            out.append(f"roof built: {built['error']}")
        else:
            out.append(f"roof built: eaves {f(built.get('eaves'))} ridge {f(built.get('ridge'))} pitch "
                       f"{f(built.get('pitch'), '{:.1f}')} ridge dir {built.get('ridge_dir')} raise "
                       f"{f(built.get('raise'), '{:.2f}')}")
    else:
        out.append("roof: none")
    stairs = st.get("stairs") or {}
    if "error" in stairs:
        out.append(f"stairs: {stairs['error']}")
    else:
        for sid, s_ in sorted(stairs.items(), key=lambda kv: str(kv[0])):
            out.append(f"stair {sid} ({s_.get('level')}): {s_.get('risers')} risers x {f(s_.get('riser'), '{:.3f}')} m "
                       f"({s_.get('source')})")
    return out


def structure_changes(base: dict, new: dict) -> list[str]:
    """The struct lines that changed against a baseline that has them (pure; notes, never regressions)."""
    if not isinstance(base.get("structure"), dict):
        return []
    old, cur = structure_lines(base["structure"]), structure_lines(new.get("structure"))
    return [f"struct changed: {a} -> {c}" for a, c in zip(old, cur) if a != c] + \
        [f"struct gone: {a}" for a in old[len(cur):]] + [f"struct new: {c}" for c in cur[len(old):]]


def notes(base: dict, new: dict) -> list[str]:
    """What changed without being a regression (pure; 5 Nov 2026, review): a level the baseline never read, with its
    low-confidence reason when it has one and its stacking offset as a new finding; printed with the comparison so a
    level that newly goes low-confidence or stacks badly is never silent."""
    out = []
    old_levels = set(base.get("levels") or [])
    if not old_levels:
        out.append("the baseline holds no level: its per-level numbers cannot be compared")
    low = new.get("low_confidence") or {}
    stack = (new.get("check") or {}).get("stacking") or {}
    for lid in new.get("levels") or []:
        if lid in old_levels:
            continue
        text = f"new level {lid}"
        if lid in low:
            text += f" (low confidence: {'; '.join(low[lid])[:200]})"
        if stack.get(lid):
            text += f"; new finding: it stacks {stack[lid]:.2f} m off the reference"
        out.append(text)
    # 5 Nov 2026 (review of the test fixes): a count that moved within the tolerance (an 8-room level may gain or lose
    # 2 rooms and still pass) is written as a note, so "regression set unchanged" means unchanged, not "within 10 %"
    for lid, b in (base.get("per_level") or {}).items():
        n = (new.get("per_level") or {}).get(lid)
        if n is None:
            continue
        for key in PER_LEVEL:
            if n.get(key, 0) != b.get(key, 0) and abs(n.get(key, 0) - b.get(key, 0)) <= max(COUNT_MIN, COUNT_TOL * b.get(key, 0)):
                out.append(f"{lid} {key}: {b.get(key)} -> {n.get(key)} (within the tolerance)")
    return out


def compare(base: dict, new: dict) -> list[str]:
    """The regressions of ``new`` against ``base`` (pure; an improvement is no regression)."""
    out = []
    for key in ("status", "levels", "levels_left_out"):
        if base.get(key) != new.get(key):
            better = key == "levels_left_out" and set(new.get(key) or []) < set(base.get(key) or [])
            better = better or (key == "levels" and set(base.get(key) or []) < set(new.get(key) or []))
            better = better or (key == "status" and new.get(key) == "ok")
            if not better:
                out.append(f"{key}: {base.get(key)} -> {new.get(key)}")
    bc, nc = base.get("check") or {}, new.get("check") or {}
    if bc.get("verdict") == "ready" and nc.get("verdict") != "ready":
        out.append(f"check verdict: ready -> {nc.get('verdict')}")
    if (nc.get("counts") or {}).get("critical", 0) > (bc.get("counts") or {}).get("critical", 0):
        out.append(f"critical findings: {(bc.get('counts') or {}).get('critical', 0)} -> "
                   f"{(nc.get('counts') or {}).get('critical', 0)}")
    for lid, off in (nc.get("stacking") or {}).items():
        if lid not in (base.get("levels") or []):
            continue                                   # 4 Nov 2026: a level the baseline never read cannot regress
        was = (bc.get("stacking") or {}).get(lid) or 0.0
        if off is not None and off > was + STACK_TOL_M:
            out.append(f"{lid} stacking offset: {was:.2f} -> {off:.2f} m")
    # 5 Nov 2026 (review): a level the baseline read that now carries reading_confidence low is a regression
    old_low = set(base.get("low_confidence") or {})
    for lid, reasons in (new.get("low_confidence") or {}).items():
        if lid in (base.get("levels") or []) and lid not in old_low:
            out.append(f"{lid} newly low confidence: {'; '.join(reasons)[:200]}")
    # 12 Nov 2026 (round-2 review, A2-FC10): heights, datum, slabs and entrance solutions, when the baseline has them
    if "heights" in base:
        for lid, h in (base.get("heights") or {}).items():
            n = (new.get("heights") or {}).get(lid)
            if n is not None and h.get("elevation") is not None and n.get("elevation") is not None \
                    and abs(float(n["elevation"]) - float(h["elevation"])) > HEIGHT_TOL_M:
                out.append(f"{lid} elevation: {h['elevation']} ({h.get('source')}) -> {n['elevation']} ({n.get('source')})")
        if (base.get("datum") is None) != (new.get("datum") is None) or (
                base.get("datum") is not None and new.get("datum") is not None
                and abs(float(base["datum"]) - float(new["datum"])) > HEIGHT_TOL_M):
            out.append(f"datum: {base.get('datum')} -> {new.get('datum')}")
        for sid, z in (base.get("slabs") or {}).items():
            nz = (new.get("slabs") or {}).get(sid)
            if z is not None and nz is not None and abs(float(nz) - float(z)) > HEIGHT_TOL_M:
                out.append(f"slab {sid} z_top: {z} -> {nz}")
        for did, sol in (base.get("entrances") or {}).items():
            ns = (new.get("entrances") or {}).get(did)
            if ns is not None and ns != sol:
                out.append(f"entrance {did}: {sol} -> {ns}")
    for lid, b in (base.get("per_level") or {}).items():
        n = (new.get("per_level") or {}).get(lid)
        if n is None:
            continue                                   # a level gone is reported by "levels"
        for key in PER_LEVEL:
            tol = max(COUNT_MIN, COUNT_TOL * b.get(key, 0))
            if abs(n.get(key, 0) - b.get(key, 0)) > tol:
                out.append(f"{lid} {key}: {b.get(key)} -> {n.get(key)}")
        ba, na = float(b.get("room_area") or 0), float(n.get("room_area") or 0)
        if ba and abs(na - ba) > AREA_TOL * ba:
            out.append(f"{lid} room area: {ba:.1f} -> {na:.1f} m2")
    return out


def read_project(project: str, work: Path) -> Path:
    """The CPU reading of ``projects/<project>`` into ``work/<project>`` (no AI answers)."""
    from wenart.ingest import pipeline as PL

    out = Path(work) / project
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    PL.run_project(PROJECTS_DIR / project, out, no_ai=True)
    return out


def main(args) -> int:
    projects = [p.strip() for p in (args.projects or "").split(",") if p.strip()] or \
        sorted(p.stem for p in BASELINE_DIR.glob("*.json"))
    if not projects:
        print("reading regress: no baseline in results/reading_baseline/ and no --projects")
        return 2
    work = Path(args.work) if args.work else Path(tempfile.mkdtemp(prefix="reading_regress_"))
    failed = 0
    for p in projects:
        new = numbers(read_project(p, work))
        path = BASELINE_DIR / f"{p}.json"
        if args.update or not path.is_file():
            BASELINE_DIR.mkdir(parents=True, exist_ok=True)
            if path.is_file():                                     # the user's acceptance outlives an update
                old = json.loads(path.read_text(encoding="utf-8"))
                new.update({k: old[k] for k in ACCEPT_FIELDS if k in old})
            path.write_text(json.dumps(new, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            print(f"{p}: baseline {'updated' if args.update else 'written'} ({new['check']['verdict']}, "
                  f"{len(new['levels'])} levels)")
            continue
        base = json.loads(path.read_text(encoding="utf-8"))
        diffs = compare(base, new)
        if diffs:
            failed += 1
            print(f"{p}: REGRESSED\n  " + "\n  ".join(diffs))
        else:
            print(f"{p}: ok ({new['check']['verdict']}, {len(new['levels'])} levels"
                  + (f", {len(new.get('low_confidence') or {})} low confidence" if new.get("low_confidence") else "")
                  + ")")
        for n in notes(base, new) + structure_changes(base, new):
            print(f"  note: {n}")
        for line in structure_lines(new.get("structure")):
            print(f"  struct: {line}")
    return 1 if failed else 0
