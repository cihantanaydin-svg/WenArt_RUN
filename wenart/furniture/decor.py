"""Rule-based decor: cushions on sofas and beds, books on shelves and desks, one
potted plant per living room or bedroom (docs/milestone4.md section 4).

Only when ``brief.decor`` is not false (default true, ``wenart/defaults.yaml``).
Decor is ``added_by_ai`` with ``method: "rule"``, never larger than 0.6 m, and
never on a walkway: a plant goes into a free room corner that passes the
placer checks (inside the room, no overlap with furniture, not on a door
approach or swing, and the 0.9 m walkways of the room stay intact; a corner
within 0.3 m of a window is skipped because the plant is taller than the
sill). Cushions and books sit on their host piece (``host_id``), expressed in
building coordinates so the Blender build can drop them on the host's top.

Output on the building: a top-level list ``decor`` of
``{"id", "kind": "decor", "type": "cushion"|"book_set"|"plant", "level_id",
"room_id", "center": [x, y], "rotation_deg", "size": [w, d], "asset": null,
"host_id": <furniture id or null>, "source": "added_by_ai", "method": "rule",
"reason"}`` plus a short markdown report.

CLI: ``python -m wenart.furniture.decor outputs/<p>/building_furnished.json
--out outputs/<p>/building_decor.json`` (``decor_report.md`` next to it).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from wenart import building as B
from wenart import geometry as G
from wenart.furniture import placer

DECOR_TYPES: tuple[str, ...] = ("cushion", "book_set", "plant")
MAX_DECOR_M = 0.6
CUSHION_SIZE = (0.45, 0.15)       # standing against a sofa back
PILLOW_SIZE = (0.5, 0.3)          # lying at the head of a bed
BOOK_SIZE = (0.3, 0.22)
PLANT_SIZE = (0.4, 0.4)
PLANT_HEIGHT_M = 1.0
PLANT_ROOM_TYPES: tuple[str, ...] = ("living", "bedroom")
CORNER_INSET_M = 0.25             # plant centre from each wall of the corner
HOST_TYPES: dict[str, str] = {    # host type -> decor type
    "sofa": "cushion", "bed_double": "cushion", "bed_single": "cushion",
    "bookshelf": "book_set", "desk": "book_set",
}


def decor_allowed(building: dict) -> bool:
    brief = (building.get("project") or {}).get("brief") or {}
    return brief.get("decor", True) is not False


def _local_to_building(host: dict, local_x: float, local_y: float) -> list[float]:
    fp = host["footprint"]
    p = G.rotate_point((fp["center"][0] + local_x, fp["center"][1] + local_y), fp["rotation_deg"], tuple(fp["center"]))
    return [round(p[0], 3), round(p[1], 3)]


def host_decor(host: dict) -> list[dict]:
    """Cushions / books for one furniture piece, in building coordinates (without ids)."""
    w, d = host["footprint"]["size"]
    rot = host["footprint"]["rotation_deg"]
    kind = HOST_TYPES.get(host["type"])
    items = []
    if kind == "cushion" and host["type"] == "sofa":
        for x in (-w / 4.0, w / 4.0):
            items.append({"type": "cushion", "center": _local_to_building(host, x, d / 2.0 - CUSHION_SIZE[1] / 2.0 - 0.1),
                          "rotation_deg": rot, "size": list(CUSHION_SIZE), "reason": "cushion against the sofa back"})
    elif kind == "cushion":
        xs = (-w / 4.0, w / 4.0) if host["type"] == "bed_double" else (0.0,)
        for x in xs:
            items.append({"type": "cushion", "center": _local_to_building(host, x, d / 2.0 - PILLOW_SIZE[1] / 2.0 - 0.1),
                          "rotation_deg": rot, "size": list(PILLOW_SIZE), "reason": "cushion at the head of the bed"})
    elif kind == "book_set" and host["type"] == "bookshelf":
        items.append({"type": "book_set", "center": _local_to_building(host, 0.0, 0.0), "rotation_deg": rot,
                      "size": list(BOOK_SIZE), "reason": "books on the shelf"})
    elif kind == "book_set":
        items.append({"type": "book_set", "center": _local_to_building(host, w / 2.0 - BOOK_SIZE[0] / 2.0 - 0.05,
                                                                         d / 2.0 - BOOK_SIZE[1] / 2.0 - 0.05),
                      "rotation_deg": rot, "size": list(BOOK_SIZE), "reason": "books on the back corner of the desk"})
    return items


def _corner_candidates(ctx: placer.RoomContext) -> list[tuple[float, float]]:
    """Plant centres inset from every convex corner of the room, in boundary order."""
    segs = ctx.segments
    out = []
    for i in range(len(segs)):
        a, b = segs[i - 1]          # previous segment ends at the corner
        _b2, c = segs[i]            # next segment starts at the corner
        corner = b
        u_prev = placer._unit((a[0] - corner[0], a[1] - corner[1]))
        u_next = placer._unit((c[0] - corner[0], c[1] - corner[1]))
        cross = u_prev[0] * u_next[1] - u_prev[1] * u_next[0]
        if cross >= -1e-9:          # reflex or straight corner (CCW ring): not a corner to stand in
            continue
        out.append((round(corner[0] + (u_prev[0] + u_next[0]) * CORNER_INSET_M, 3),
                    round(corner[1] + (u_prev[1] + u_next[1]) * CORNER_INSET_M, 3)))
    return out


def plant_position(room: dict, furniture: list[dict], building: dict) -> tuple[Optional[tuple[float, float]], str]:
    """A free corner for the plant, or (None, reason)."""
    ctx = placer.room_context(building, room)
    pieces = [placer.piece_from_furniture(f, i) for i, f in enumerate(furniture)]
    candidates = _corner_candidates(ctx)
    if not candidates:
        return None, "no convex corner"
    reasons = []
    for center in candidates:
        plant = placer.Piece("plant", center, 0.0, PLANT_SIZE, False, index=len(pieces))
        checks = placer.check_piece(plant, pieces, ctx)
        failed = placer.failed_checks(checks)
        if not failed and placer.walkway_failures(pieces + [plant], ctx):
            failed = ["walkway"]
        if not failed:
            return center, "free corner"
        reasons.append(f"{center}: {', '.join(failed)}")
    return None, "no free corner (" + "; ".join(reasons) + ")"


def add_decor(building: dict) -> tuple[dict, list[dict]]:
    """Return (building with ``decor``, report rows). Idempotent: existing decor is replaced."""
    out = json.loads(json.dumps(building))
    out["decor"] = []
    rows: list[dict] = []
    if not decor_allowed(out):
        rows.append({"room_id": "-", "label": "-", "note": "brief.decor is false: no decor"})
        return out, rows
    counters: dict[str, int] = {}

    def new_id(level_id: str) -> str:
        counters[level_id] = counters.get(level_id, 0) + 1
        return f"dec_{level_id}_{counters[level_id]:03d}"

    furniture_by_room: dict[str, list[dict]] = {}
    for f in out["furniture"]:
        if f.get("room_id"):
            furniture_by_room.setdefault(f["room_id"], []).append(f)
    for room in out["rooms"]:
        pieces = furniture_by_room.get(room["id"], [])
        row = {"room_id": room["id"], "label": room["label"], "cushions": 0, "books": 0, "plant": "-", "note": ""}
        for host in pieces:
            if host.get("status") != "verified" or host["type"] not in HOST_TYPES:
                continue
            for item in host_decor(host):
                assert max(item["size"]) <= MAX_DECOR_M
                out["decor"].append({"id": new_id(room["level_id"]), "kind": "decor", "type": item["type"],
                                     "level_id": room["level_id"], "room_id": room["id"], "center": item["center"],
                                     "rotation_deg": item["rotation_deg"], "size": item["size"], "asset": None,
                                     "host_id": host["id"], "source": "added_by_ai", "method": "rule",
                                     "reason": item["reason"]})
                row["cushions" if item["type"] == "cushion" else "books"] += 1
        if room.get("room_type") in PLANT_ROOM_TYPES and room.get("status") == "verified":
            center, why = plant_position(room, pieces, out)
            if center is not None:
                out["decor"].append({"id": new_id(room["level_id"]), "kind": "decor", "type": "plant",
                                     "level_id": room["level_id"], "room_id": room["id"], "center": list(center),
                                     "rotation_deg": 0.0, "size": list(PLANT_SIZE), "asset": None, "host_id": None,
                                     "source": "added_by_ai", "method": "rule", "reason": "potted plant in a free corner"})
                row["plant"] = f"{center[0]}, {center[1]}"
            else:
                row["plant"] = "none"
                row["note"] = why
        rows.append(row)
    return out, rows


def decor_report(building: dict, rows: list[dict]) -> str:
    lines = [f"# Decor: {building['project']['id']}", "",
             f"{len(building.get('decor', []))} decor pieces (rule-based, `added_by_ai`, max {MAX_DECOR_M} m). "
             "Cushions on sofas and beds, books on shelves and desks, one plant per living room or bedroom in a "
             "free corner (never on a door approach, a swing or a 0.9 m walkway).", "",
             "| Room | Cushions | Books | Plant | Note |", "|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['label']} ({r['room_id']}) | {r.get('cushions', '-')} | {r.get('books', '-')} | "
                     f"{r.get('plant', '-')} | {r.get('note', '')} |")
    return "\n".join(lines) + "\n"


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="rule-based decor (cushions, books, plants) on a building JSON")
    parser.add_argument("building", help="building JSON (furnished or not)")
    parser.add_argument("--out", required=True, help="building JSON with the decor list")
    parser.add_argument("--report", help="markdown report (default: decor_report.md next to --out)")
    args = parser.parse_args(argv)
    building = B.load(args.building)
    out, rows = add_decor(building)
    out_path = Path(args.out)
    B.save(out, out_path)
    report = Path(args.report) if args.report else out_path.parent / "decor_report.md"
    report.write_text(decor_report(out, rows), encoding="utf-8")
    print(f"decor: {len(out['decor'])} pieces -> {out_path} (report {report})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
