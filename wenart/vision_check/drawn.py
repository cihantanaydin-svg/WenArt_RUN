"""Drawn furniture against the source plan (docs/milestone10.md §1.7, §2.7, §2.8).

What: ``drawn_check(final, source)`` lists every drawn piece (``source: from_documents``) of the final building
with its distance to the drawn anchor, the turn of its front and whether it is still against the same wall:
the "cross-check against the source plan" of Feature 1. A piece the AI changed (``modified_by_ai``) is listed
with its drawn and new type and size, so the check shows what changed and that what is locked did not move.

Why: with ``furnished_rooms: complete`` the AI may change the type, size, height and look of a drawn piece, but
its location (footprint centre ± 5 cm; against a wall the back-edge midpoint on the same wall line) and
position (front ± 1 degree, the same wall) are locked (CLAUDE.md). ``wenart.furniture.locked.check`` guards the
layout and refit stages; this check repeats it on the files the renders were made from, per piece and against the
source plan, so the final report can show the numbers.

How: the reference is, in this order, the source building (``building.json``: the pipeline's output, read from the
documents), else the piece's own ``anchor`` and ``drawn_footprint`` (written by the completion), else nothing
(the piece is listed with ``reference: none``, never counted as checked). The anchor of a piece is
``locked.anchor_of`` (a free piece: its footprint centre; a piece whose back edge touches a wall within 5 cm:
the midpoint of that edge and the wall id). ``locked.check`` runs as well when the source is there, and its
lines are listed as ``locked``. ``wenart.furniture.locked`` imports shapely, so this module is imported where
shapely is (the vision check CLI, the report), never by ``expected``.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from wenart import geometry as G

ANCHOR_TOL_M = 0.05
FRONT_TOL_DEG = 1.0


def source_path(project_out) -> Optional[Path]:
    """The source building of a project output: ``building.json`` in it, else (a variant's sub-output
    ``outputs/<p>/variants/<id>``) the base project's."""
    out = Path(project_out).resolve()
    candidates = [out / "building.json"]
    if out.parent.name == "variants":
        candidates.append(out.parent.parent / "building.json")
    return next((c for c in candidates if c.is_file()), None)


def load_source(project_out) -> Optional[dict]:
    path = source_path(project_out)
    return json.loads(path.read_text(encoding="utf-8")) if path is not None else None


def _size(fp: Optional[dict]) -> Optional[list]:
    return [round(float(v), 3) for v in fp["size"]] if isinstance(fp, dict) and fp.get("size") else None


def _row(piece: dict, final: dict, source: Optional[dict], src: Optional[dict], tol_m: float, tol_deg: float) -> dict:
    from wenart.furniture import locked

    row = {"id": piece["id"], "room_id": piece.get("room_id"), "type": piece.get("type"),
           "drawn_type": piece.get("drawn_type") or (src or {}).get("type") or piece.get("type"),
           "modified_by_ai": bool(piece.get("modified_by_ai")), "type_proposal": bool(piece.get("type_proposal")),
           "status": piece.get("status"), "size": _size(piece.get("footprint")),
           "drawn_size": _size(piece.get("drawn_footprint")) or _size((src or {}).get("footprint"))
           or _size(piece.get("footprint")),
           "reference": "none", "anchor_kind": None, "anchor_distance_m": None, "front_turn_deg": None,
           "same_wall": None, "checked": False, "ok": None, "notes": []}
    if not piece.get("footprint"):
        row["notes"].append("no footprint")
        return row
    if src is not None and src.get("footprint"):
        ref = locked.anchor_of(src, source)
        row["reference"] = "source building.json"
        ref_front = src.get("front_deg")
    elif isinstance(piece.get("anchor"), dict) and piece["anchor"].get("point"):
        ref = piece["anchor"]
        row["reference"] = "anchor of building_final.json"
        ref_front = None
        row["notes"].append("no source building.json: the front is not checked")
    else:
        row["notes"].append("no source building.json and no recorded anchor: nothing to check against")
        return row
    row["anchor_kind"] = ref.get("kind")
    if ref.get("kind") == "back_edge" and piece.get("front_deg") is not None:
        point = locked._back_edge(piece)[1]
    else:
        point = (float(piece["footprint"]["center"][0]), float(piece["footprint"]["center"][1]))
    row["anchor_distance_m"] = round(G.distance(point, ref["point"]), 4)
    if ref.get("kind") == "back_edge":
        now = locked.anchor_of(piece, final)
        row["same_wall"] = now.get("kind") == "back_edge" and now.get("wall_id") == ref.get("wall_id")
        if not row["same_wall"]:
            row["notes"].append(f"no longer against wall {ref.get('wall_id')} (now {now.get('kind')} "
                                f"{now.get('wall_id')})")
    if ref_front is not None and piece.get("front_deg") is not None:
        row["front_turn_deg"] = round(G.angle_difference_deg(float(ref_front), float(piece["front_deg"])), 3)
    elif ref_front is not None or piece.get("front_deg") is not None:
        row["notes"].append("front missing on one side")
    row["checked"] = True
    row["ok"] = (row["anchor_distance_m"] <= tol_m + 1e-6 and row["same_wall"] is not False
                 and (row["front_turn_deg"] is None or row["front_turn_deg"] <= tol_deg + 1e-6))
    return row


def drawn_check(final: dict, source: Optional[dict] = None, completion: Optional[dict] = None,
                cfg: Optional[dict] = None) -> dict:
    """The drawn-piece check of ``final`` (module docstring) as ``{"kind": "drawn_check", "reference",
    "mode", "pieces": [row], "checked", "ok", "failed": [ids], "modified": [ids], "violations": [str],
    "notes": [str]}``. ``completion``: ``completion.json`` (its settings give the mode and the rooms kept as
    drawn, as ``locked.mode_of`` / ``locked.keep_rooms_of``)."""
    from wenart.furniture import locked

    dcfg = (cfg or {}).get("drawn") or {}
    tol_m = float(dcfg.get("anchor_tolerance_m", ANCHOR_TOL_M))
    tol_deg = float(dcfg.get("front_tolerance_deg", FRONT_TOL_DEG))
    src_by_id = {f["id"]: f for f in (source or {}).get("furniture") or [] if f.get("id")}
    rows = [_row(f, final, source, src_by_id.get(f["id"]), tol_m, tol_deg)
            for f in final.get("furniture") or [] if f.get("source") == "from_documents"]
    mode = locked.mode_of(completion)
    notes: list[str] = []
    violations: list[str] = []
    if source is not None:
        gone = sorted(set(f["id"] for f in source.get("furniture") or [] if f.get("source") == "from_documents")
                      - {r["id"] for r in rows})
        for pid in gone:
            violations.append(f"{pid}: drawn piece missing from the final building")
        violations.extend(locked.check(source, final, mode, locked.keep_rooms_of(completion)))
    else:
        notes.append("no source building.json: the anchor is compared with the anchor recorded in the final "
                     "building, the front and the locked rules are not checked")
    return {"kind": "drawn_check", "reference": "source building.json" if source is not None else "recorded anchors",
            "mode": mode, "tolerance_m": tol_m, "tolerance_deg": tol_deg, "pieces": rows,
            "checked": sum(r["checked"] for r in rows), "ok": sum(bool(r["ok"]) for r in rows),
            "failed": [r["id"] for r in rows if r["ok"] is False],
            "modified": [r["id"] for r in rows if r["modified_by_ai"]],
            "proposals": [r["id"] for r in rows if r["type_proposal"]],
            "violations": violations, "notes": notes}


def lines(check: dict) -> list[str]:
    """One readable line per failed piece and per violation (for the CLI and the check report)."""
    out = []
    by_id = {r["id"]: r for r in check.get("pieces") or []}
    for pid in check.get("failed") or []:
        r = by_id[pid]
        out.append(f"{pid} ({r['type']}): anchor moved {r['anchor_distance_m']} m, front turned "
                   f"{r['front_turn_deg']} deg" + (f", {'; '.join(r['notes'])}" if r["notes"] else ""))
    out.extend(check.get("violations") or [])
    return out
