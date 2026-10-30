"""UL187 (30 Oct 2026, real04 run 20261030-112241-full): "in the kitchen a full size fridge can be included into the
right side at the end", "for the fridge I was referring the end of the table, maybe by shortening the table" (the
basement kitchen's U run: only an under-counter fridge; its free right end lay in a door swing, so no tall-unit column)
and "There can be a full embedded fridge next to the Owen" (the open kitchen: the fridge a lone steel column at the
other run's end). Every kitchen's full-size fridge stands in the tall-unit column beside the oven tower; an added
under-counter or lone fridge moves there; a run end in a door swing stops short (at most 0.5 m). Pure tests on the
frozen real04 kitchen; real04 is only the test case."""
from __future__ import annotations

import copy
import json
from pathlib import Path

from wenart.blender import kitchen_details as KD
from wenart.blender import modules as MOD
from wenart.furniture import fit as F

ROOT = Path(__file__).resolve().parents[1]
REAL04 = ROOT / "tests" / "fixtures" / "real04_kitchen_20261030.json"
DESIGN = {"front_style": "shaker", "colour": "muted taupe", "handle": "black", "worktop": "stone"}


def _real04() -> dict:
    return json.loads(REAL04.read_text(encoding="utf-8"))


def _column(kitchen: dict) -> tuple[str, dict]:
    return next((rid, d["column"]) for rid, d in kitchen["details"].items() if (d.get("column") or {}).get("kinds"))


def test_the_kitchen_with_an_under_counter_fridge_gets_a_full_size_one_in_the_column():
    b = _real04()
    k = F.kitchen_built_ins(b)
    rid, col = _column(k)
    assert any(n.startswith("fridge") for n in col["kinds"]) and "oven_tower" in col["kinds"]
    assert "UL187" in col["why"]
    old = F.run_hints(k, "f_L-1_004")                      # the run that held the under-counter fridge f_L-1_090
    assert old["fridge_pos_m"] is None and old["fridge_column"] is False and "f_L-1_090" in old["fridge_moved"]
    assert sum(1 for d in k["details"].values() if any(n.startswith("fridge") for n in (d.get("column") or {}).get(
        "kinds") or [])) == 1                              # one full-size fridge per kitchen
    assert not any(d.get("fridge_x_m") for d in k["details"].values())


def test_a_run_end_in_a_door_swing_stops_short_and_the_column_clears_the_swing():
    b = _real04()
    k = F.kitchen_built_ins(b)
    rid, col = _column(k)
    assert rid == "f_L-1_001" and 0.0 < col["trim_m"] <= F.SWING_TRIM_MAX_M + 1e-9
    run = next(f for f in b["furniture"] if f["id"] == rid)
    c, rot, w, d = F._run_axes(run)
    tw = sum(wd for _k, wd in KD.column_widths(col["kinds"]))
    t = col["trim_m"]
    lo, hi = (-w / 2.0 + t, -w / 2.0 + t + tw) if col["end"] == "left" else (w / 2.0 - t - tw, w / 2.0 - t)
    cx, cy = F._to_world(c, rot, (lo + hi) / 2.0, 0.0)
    placed = dict(run, id="col", footprint={"center": [cx, cy], "size": [tw, d], "rotation_deg": rot})
    assert not F._in_door_swing(b, placed)
    end = dict(placed, footprint={"center": list(F._to_world(c, rot, (lo + hi) / 2.0 + (t if col["end"] == "right"
                                                                                        else -t), 0.0)),
                                  "size": [tw, d], "rotation_deg": rot})
    assert F._in_door_swing(b, end)                        # at the drawn end it stood in the swing
    assert run["footprint"]["size"][0] == w                # the drawn footprint stays as drawn


def test_a_drawn_full_size_fridge_keeps_its_place():
    b = _real04()
    fridge = next(f for f in b["furniture"] if f["id"] == "f_L-1_090")
    fridge.update(source="from_documents", height=1.86)
    k = F.kitchen_built_ins(b)
    kinds = [n for d in k["details"].values() for n in (d.get("column") or {}).get("kinds") or []]
    assert not any(n.startswith("fridge") for n in kinds)
    assert not any(d.get("fridge_moved") for d in k["details"].values())
    assert F._fridge_full(fridge) and not F._fridge_full(dict(fridge, height=0.82))


def test_the_module_plan_leaves_the_trimmed_end_unbuilt_and_stands_the_column_beside_it():
    hint = {"end": "right", "kinds": ["fridge_column", "oven_tower"], "top_m": 2.6, "trim_m": 0.35}
    spans, notes = KD.column_spans(3.66, [], hint)
    assert [k for _a, _b, k in spans] == ["oven_tower", "fridge_column"] and abs(spans[-1][1] - (1.83 - 0.35)) < 1e-6
    assert KD.trim_span(3.66, hint) == (1.83 - 0.35, 1.83, "trimmed") and KD.trim_span(3.66, dict(hint, trim_m=0)) is None
    run = {"id": "f_run", "type": "kitchen_counter", "level_id": "L0", "room_id": "r_k", "height": 0.9,
           "footprint": {"center": [0.0, 0.0], "size": [3.66, 0.6], "rotation_deg": 0.0}, "design": dict(DESIGN),
           "module_hints": {"sink_x_m": -1.0, "sink_w_m": 0.6, "column": hint}}
    plan = MOD.plan_kitchen_run(run, {"family": "modern"})
    end = 1.83 - 0.35
    for m in plan["modules"]:
        x, w = float(m["pos_m"][0]), float(m["size_m"][0])
        if m["kind"] in ("base_unit", "filler", "worktop", "plinth", "tall_unit"):
            assert x + w / 2.0 <= end + 1e-6, m["kind"]     # nothing in the trimmed stretch
    talls = [m for m in plan["modules"] if m["kind"] == "tall_unit"]
    assert {m["front"] for m in talls} == {"fridge_column", "oven_tower"}
    assert any("door swing" in n for n in plan.get("notes") or [])


def test_an_integrated_fridge_column_matches_the_run_and_a_steel_one_stays_steel():
    span = (0.0, 0.6, "fridge_column")
    integrated = KD.tall_module(span, 0.6, 2.4, 0.1, look="integrated")
    steel = KD.tall_module(span, 0.6, 2.4, 0.1, look="steel")
    assert integrated["appliance"] == "integrated" and "match the run" in integrated["product"]
    p_int = KD.tall_parts(integrated, DESIGN, 0.6, 0.06)
    p_steel = KD.tall_parts(steel, DESIGN, 0.6, 0.06)
    assert not [p for p in p_int if p.get("key") == "steel"]
    assert [p for p in p_steel if p.get("key") == "steel"]
    long_bars = [p for p in p_int if p.get("role") == "handle"
                 and max(v[2] for v in p["verts"]) - min(v[2] for v in p["verts"]) > 0.3]
    assert len(long_bars) == 2                              # the freezer's and the fridge's bar handles
    oven = KD.tall_module((0.6, 1.2, "oven_tower"), 0.6, 2.4, 0.1, look="integrated")
    assert "appliance" not in oven
