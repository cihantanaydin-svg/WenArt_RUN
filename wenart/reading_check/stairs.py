"""The stair integrity check of a reading (RC16; 13 Nov 2026, coordinator after review B3: "The user should never have
to point at a hole in a stair").

What: ``findings(out_dir)`` builds every drawn stair of a pipeline output as ``wenart.blender.parametric.stair_plan``
plans it (the storey from the level elevations, the ceiling a slab under the floor above, the level's walls) and lists
each violation of ``parametric.stair_integrity``: (a) the walking surfaces (treads, winders, landings, turns) form a
continuous path, every surface within 3 cm of the one before; (b) no two overlap deeper than 3 cm; (c) the risers rise
one at a time and sum to the floor-to-floor height within one riser, each 0.15-0.22 m high (19 Nov 2026, review A3
POD-A3-03: real10's 0.43 m risers on a flight read from furnishing lines passed); (d) the ceiling opening holds every surface
without its headroom, every loop; (e) no tread runs into a wall deeper than 3 cm. Each finding is shaped like
``wenart.reading_check._finding`` (``check: "RC16"``) with ``rule`` (the check's letter name), ``element_ids`` and
``advisory: true``: counted, never in the verdict.

Why: the stairs the numbered treads re-read were built with holes in their walking line (review B3-ST-LAND,
B3-REG-02, BLD-03), turns under a solid slab (BLD-02) and treads through walls (BLD-05), and no check said so.

How: ``python -m wenart.reading_check stairs --out DIR`` prints one line per stair and its violations. No AI, no pod.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

CHECK = "RC16"
NAME = "stair integrity"
STOREY_M = 3.0                  # a storey's rise where the levels give none (the reader's own assumption)
SLAB_M = 0.20                   # the slab under the floor above (parametric.STAIR_SLAB_M's role)
RISER_M = (0.15, 0.22)          # 19 Nov 2026 (review A3, POD-A3-03): a walkable riser's height
SEVERITY = {"continuous": "major", "overlap": "major", "risers": "major", "opening": "major", "walls": "minor"}


def _rise(building: dict, level_id: str) -> float:
    levels = sorted((lv for lv in building.get("levels") or [] if lv.get("elevation") is not None),
                    key=lambda lv: float(lv["elevation"]))
    for i, lv in enumerate(levels):
        if lv.get("id") == level_id and i + 1 < len(levels):
            rise = float(levels[i + 1]["elevation"]) - float(lv["elevation"])
            if 2.0 <= rise <= 6.0:
                return rise
    return STOREY_M


def stairs(building: dict) -> list[dict]:
    """``[{"id", "level_id", "risers", "violations": [{"check", "message"}], "error"}]`` for every stair piece with
    drawn flights (pure)."""
    from wenart.blender import parametric as P

    out = []
    for f in building.get("furniture") or []:
        if f.get("type") != "stair" or not (P.stair_data(f) or {}).get("flights"):
            continue
        rise = _rise(building, f.get("level_id"))
        walls = [w for w in building.get("walls") or [] if w.get("level_id") == f.get("level_id")]
        rec = {"id": f.get("id"), "level_id": f.get("level_id"), "risers": None, "violations": [], "error": None}
        try:
            plan = P.stair_plan(f, rise, rise - SLAB_M, rise - SLAB_M + P.STAIR_SHAFT_CAP_M, walls)
        except Exception as exc:  # noqa: BLE001 - a stair that cannot be planned is itself the finding
            rec["error"] = f"{type(exc).__name__}: {str(exc)[:160]}"
            out.append(rec)
            continue
        rec["risers"] = plan.get("risers")
        rec["violations"] = list(plan.get("integrity") or [])
        # 19 Nov 2026 (review A3, POD-A3-03: real10's 7 risers of 0.43 m on a 1.2 m flight read from furnishing lines
        # passed every check): a walkable riser is ``RISER_M`` high
        riser = plan.get("riser_m")
        if isinstance(riser, (int, float)) and not RISER_M[0] - 1e-9 <= float(riser) <= RISER_M[1] + 1e-9:
            rec["violations"].append({"check": "risers", "message": (
                f"{plan.get('risers')} risers of {float(riser):.3f} m over {rise:.2f} m: a riser is "
                f"{RISER_M[0]:.2f}-{RISER_M[1]:.2f} m high (no walkable stair: misread tread lines or flight)")})
        out.append(rec)
    return out


def findings(out_dir) -> list[dict]:
    """Every RC16 finding of a pipeline output (the module docstring)."""
    building = json.loads((Path(out_dir) / "building.json").read_text(encoding="utf-8"))
    return findings_of(building)


def findings_of(building: dict) -> list[dict]:
    out = []
    for rec in stairs(building):
        if rec["error"]:
            out.append({"check": CHECK, "name": NAME, "rule": "plan", "severity": "major",
                        "level_id": rec["level_id"], "message": f"stair {rec['id']} cannot be planned: {rec['error']}",
                        "element_ids": [rec["id"]], "advisory": True})
        for v in rec["violations"]:
            out.append({"check": CHECK, "name": NAME, "rule": v["check"], "severity": SEVERITY.get(v["check"], "major"),
                        "level_id": rec["level_id"], "message": f"stair {rec['id']}: {v['message']}",
                        "element_ids": [rec["id"]], "advisory": True})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.reading_check stairs")
    ap.add_argument("--out", required=True, help="a pipeline output folder (with building.json)")
    args = ap.parse_args(argv)
    building = json.loads((Path(args.out) / "building.json").read_text(encoding="utf-8"))
    recs = stairs(building)
    bad = 0
    for rec in recs:
        kinds = sorted({v["check"] for v in rec["violations"]})
        print(f"{rec['level_id']} {rec['id']}: {rec['risers']} risers, "
              f"{len(rec['violations'])} violation(s) {kinds}" + (f"; ERROR {rec['error']}" if rec["error"] else ""))
        for v in rec["violations"][:12]:
            print(f"   {v['check']}: {v['message']}")
        bad += bool(rec["violations"] or rec["error"])
    print(f"{len(recs)} stair(s) checked, {bad} with violations")
    return 0
