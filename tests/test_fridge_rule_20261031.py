"""A fridge never stands on or inside a kitchen counter run (31 Oct 2026; user on real04 run 20261030-181158-full, the
basement kitchen: "There can not be a fridge inside the kitchen counter! make this a rule. The kitchen can be built
around the fridge, (kitchen counter ends and continues, if there is a place on top of the fire some sections can be
included) but not over the kitchen counter"; the open kitchen of the variant l-1b-acik-mutfak: "Again fridge inside
the kitchen counter"; the French-door fridge in the tall-unit column: "Fridge here was making sense").

The cause (``wenart.blender.fridge_rule``): UL187 moved the kitchen's fridge into the tall-unit column and cleared the
old run's fridge hints, but nothing held the moved under-counter piece: the fit fitted a 1.64-1.86 m library fridge to
it and the scene built it inside its old run, through the worktop. The rules are general; real04's frozen kitchen is
only the test case."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from test_furniture_fit_v2 import FakeCatalog, model
from test_kitchen_design_20261028 import by_id, fp, kitchen
from wenart.blender import fridge_rule as FR
from wenart.blender import kitchen_details as KD
from wenart.blender import model_review as MR
from wenart.blender import modules as MOD
from wenart.blender import proxies as PX
from wenart.furniture import decor as D
from wenart.furniture import fit as F

ROOT = Path(__file__).resolve().parents[1]
REAL04 = ROOT / "tests" / "fixtures" / "real04_kitchen_20261030.json"
DESIGN = {"front_style": "shaker", "colour": "muted taupe", "handle": "black", "worktop": "stone"}
MODERN = {"family": "modern"}


@pytest.fixture(autouse=True)
def _no_licence_mode_env(monkeypatch):
    monkeypatch.delenv("WENART_LICENCE_MODE", raising=False)


def _real04() -> dict:
    return json.loads(REAL04.read_text(encoding="utf-8"))


def _catalog() -> FakeCatalog:
    # a full-size library fridge, as the HSSD model the run fitted to the 0.82 m under-counter piece
    return FakeCatalog([model("tallfridge", "fridge", 0.6, 0.65, 1.85)])


def _fridges_built(fitted: dict, room_id: str) -> list[str]:
    """What stands in the room as a fridge: library or parametric fridge models of their own (not held by a run) and
    the runs' fridge units (a tall unit or a base unit holding a fridge)."""
    held = FR.held_by(fitted["furniture"])
    out = [f["id"] for f in fitted["furniture"] if f.get("room_id") == room_id and f["type"] == "fridge"
           and f["id"] not in held and (f.get("asset") or {}).get("method") != "none"]
    for f in fitted["furniture"]:
        if f.get("room_id") != room_id or f["type"] not in FR.RUN_HOST_TYPES:
            continue
        for m in ((f.get("asset") or {}).get("module_plan") or {}).get("modules") or []:
            if m.get("holds") == "fridge":
                out.append(f"{f['id']}:{m['kind']}")
    return out


def _worktops(run: dict) -> list[tuple[float, float]]:
    plan = run["asset"]["module_plan"]
    return [(m["pos_m"][0] - m["size_m"][0] / 2.0, m["pos_m"][0] + m["size_m"][0] / 2.0)
            for m in plan["modules"] if m["kind"] in ("worktop", "base_unit", "plinth", "filler")]


# --------------------------------------------------------------------------
# 1. The cause: the moved fridge is held by the tall-unit column (one fridge per kitchen)
# --------------------------------------------------------------------------

def test_the_moved_fridge_is_held_by_the_column_and_never_built_in_its_old_run():
    fitted = F.fit_building(_real04(), _catalog(), style=MODERN, snap=False)
    fr = by_id(fitted)["f_L-1_090"]
    assert fr["asset"]["method"] == "module" and fr["asset"]["built_in"] == "f_L-1_001"   # not the library model
    assert "tall-unit column" in fr["asset"]["fallback_reason"] and "f_L-1_004" in fr["asset"]["fallback_reason"]
    col = by_id(fitted)["f_L-1_001"]["asset"]["module_plan"]
    rec = next(b for b in col["built_ins"] if b["id"] == "f_L-1_090")
    assert rec["column"] and rec["moved"] and rec["moved_from"] == "f_L-1_004"
    old = by_id(fitted)["f_L-1_004"]["asset"]["module_plan"]
    assert not [m for m in old["modules"] if m.get("holds") == "fridge"]                  # its unit is a cupboard
    assert FR.findings(fitted) == []                                                      # the check is clean
    assert _fridges_built(fitted, "r_L-1_mutfak") == ["f_L-1_001:tall_unit"]              # one fridge per kitchen
    from wenart.blender import furniture as BF
    assert BF.built_in_ids(fitted["furniture"])["f_L-1_090"] == "f_L-1_001"              # the scene skips it
    log = fitted["project"]["fridge_rule"]
    assert [(f["rule"], f["piece"]) for f in log["findings"]] == [("one_per_kitchen", "f_L-1_090")] and not log["open"]


def test_before_the_fix_the_old_run_built_the_fridge_model_inside_it():
    """The defect as the run had it: the moved piece fitted on its own is a full-size model inside its old run."""
    b = _real04()
    run = by_id(b)["f_L-1_004"]
    plan = MOD.plan_kitchen_run(dict(run, module_hints={}), MODERN)            # the run planned whole (a cupboard)
    run["asset"] = {"method": "module", "module_plan": plan}
    by_id(b)["f_L-1_090"]["asset"] = {"method": "library", "asset_id": "hssd_x", "bbox_m": [0.6, 0.5546, 1.6389]}
    found = FR.findings(b)
    assert [(f["rule"], f["piece"], f["run"]) for f in found] == [("in_run", "f_L-1_090", "f_L-1_004")]
    assert found[0]["severity"] == "critical" and "never stands on or inside" in found[0]["message"]


def test_without_a_fridge_unit_in_the_column_the_fridge_goes_back_into_its_run():
    """No style: the plan builds no tall-unit column, so the column holds nothing; the guard gives the fridge back to
    its run (its built-in unit) instead of leaving a model inside it."""
    fitted = F.fit_building(_real04(), _catalog(), style=None, snap=False)
    fr = by_id(fitted)["f_L-1_090"]
    assert fr["asset"]["built_in"] == "f_L-1_004"
    assert any(b["id"] == "f_L-1_090" for b in by_id(fitted)["f_L-1_004"]["asset"]["module_plan"]["built_ins"])
    assert FR.findings(fitted) == []
    fixes = [f for f in fitted["project"]["fridge_rule"]["findings"] if f["stage"] == "guard"]
    assert len(fixes) == 1 and "goes back into its run f_L-1_004" in fixes[0]["fix"]
    assert len(_fridges_built(fitted, "r_L-1_mutfak")) == 1


# --------------------------------------------------------------------------
# 2. A fridge in a run: the run ends at it and continues past it
# --------------------------------------------------------------------------

def _drawn_fridge_in_real04(center=None) -> dict:
    b = _real04()
    fr = by_id(b)["f_L-1_090"]
    for key in ("built_into", "built_in"):
        fr.pop(key, None)
    fr.update(source="from_documents", height=None)
    if center is not None:
        fr["footprint"]["center"] = list(center)
    return b


def test_a_run_overlapping_a_drawn_fridge_is_split_around_it():
    b = _drawn_fridge_in_real04()
    assert [f["rule"] for f in FR.findings(b)] == ["in_run"]                          # before the fit
    fitted = F.fit_building(b, _catalog(), style=MODERN, snap=False)
    run, fr = by_id(fitted)["f_L-1_004"], by_id(fitted)["f_L-1_090"]
    gap = next(g for g in run["asset"]["module_plan"]["gaps"] if g["id"] == "f_L-1_090")
    assert gap["fridge_rule"] and gap["adjusted_by_ai"] and "ends at it and continues past it" in gap["reason"]
    g0, g1 = gap["x_m"] - gap["w_m"] / 2.0, gap["x_m"] + gap["w_m"] / 2.0
    assert g1 == pytest.approx(run["footprint"]["size"][0] / 2.0)       # a 3 cm sliver beyond it joins the gap
    assert all(s1 <= g0 + 1e-6 or s0 >= g1 - 1e-6 for s0, s1 in _worktops(run))   # no worktop or unit over it
    assert fr["asset"]["method"] == "library" and not fr["asset"].get("built_in")  # it stands on the floor
    assert run["footprint"] == by_id(b)["f_L-1_004"]["footprint"]                  # the drawn footprint is kept
    assert FR.findings(fitted) == []
    log = fitted["project"]["fridge_rule"]["findings"]
    assert [(f["rule"], f["stage"], f["run"]) for f in log] == [("in_run", "pre-pass", "f_L-1_004")]
    col = F.run_hints(F.kitchen_built_ins(b), "f_L-1_001")["column"]
    assert col["kinds"] == ["oven_tower"]                    # a drawn fridge is the kitchen's fridge: no second one
    assert _fridges_built(fitted, "r_L-1_mutfak") == ["f_L-1_090"]
    assert "a 0.63 m gap for the fridge f_L-1_090" in F.fit_report(fitted)


def test_a_fridge_reaching_into_a_run_end_stops_the_run_short():
    run_len = 2.1808
    b = _drawn_fridge_in_real04(center=(0.5007, 8.234 - run_len / 2.0 + 0.25))   # 0.55 m into the run's left end
    fitted = F.fit_building(b, _catalog(), style=MODERN, snap=False)
    run = by_id(fitted)["f_L-1_004"]
    gap = next(g for g in run["asset"]["module_plan"]["gaps"] if g["id"] == "f_L-1_090")
    assert gap["x_m"] - gap["w_m"] / 2.0 == pytest.approx(-run_len / 2.0)
    assert gap["w_m"] == pytest.approx(0.55, abs=1e-3)
    assert FR.findings(fitted) == []
    # a fridge that only meets the run (2 cm) is no finding: no gap of a drawing slip
    slip = _drawn_fridge_in_real04(center=(0.5007, 8.234 - run_len / 2.0 - 0.28))
    assert FR.findings(slip) == [] and not F.loose_in_runs(
        [by_id(slip)["f_L-1_004"]], slip["furniture"], set())


def test_the_guard_splits_a_run_the_pre_pass_missed(monkeypatch):
    """The check on the fitted plans is the safety net: whatever left a fridge model where a run is built (here the
    pre-pass is switched off), the guard gives the run a gap before the build and logs it."""
    monkeypatch.setattr(F, "loose_in_runs", lambda runs, pieces, claimed: {})
    fitted = F.fit_building(_drawn_fridge_in_real04(), _catalog(), style=MODERN, snap=False)
    assert FR.findings(fitted) == []
    log = fitted["project"]["fridge_rule"]
    assert [(f["rule"], f["stage"]) for f in log["findings"]] == [("in_run", "guard")] and not log["open"]
    assert any(g["id"] == "f_L-1_090" for g in by_id(fitted)["f_L-1_004"]["asset"]["module_plan"]["gaps"])


def test_a_synthetic_kitchen_run_is_split_around_its_fridge_and_its_wall_run_stops_at_it():
    b = kitchen(extra=[fp("fr", "fridge", (3.7, 1.0), (0.6, 0.6), 180.0)])
    k = F.kitchen_built_ins(b)
    entry = next(r for r in k["hints"]["kB"]["ranges"] if r["id"] == "fr")
    assert entry["fridge_rule"] and entry["x1_m"] - entry["x0_m"] == pytest.approx(0.6, abs=1e-3)
    plan = MOD.plan_kitchen_run(dict(by_id(b)["kB"], module_hints=F.run_hints(k, "kB")), MODERN)
    assert [g["id"] for g in plan["gaps"]] == ["fr"]
    assert any("ends at the fridge fr and continues past it" in n for n in plan["notes"])
    run = dict(by_id(b)["kB"], asset={"method": "module", "module_plan": plan})
    cab = fp("wc", "wall_cabinet", (3.825, 1.8), (2.4, 0.35), 180.0, height=0.7, mount_bottom_m=1.45)
    cols = F.wall_run_hints(cab, run, b).get("column_m") or []
    assert any(abs((c1 - c0) - 0.6) < 0.01 for c0, c1 in cols)          # the wall units stop at the fridge
    # the decor keeps off the fridge's span (no worktop there), whatever height the drawn fridge carries
    blocks = D.worktop_blocks(by_id(b)["kB"], b["furniture"] + [fp("fr", "fridge", (3.7, 1.0), (0.6, 0.6), 180.0)])
    assert any(k == "tall" for _a, _b, k in blocks)
    under = fp("fr2", "fridge", (3.7, 1.0), (0.6, 0.6), 180.0, height=0.82, built_into="kB")
    assert not [x for x in D.worktop_blocks(by_id(b)["kB"], [under]) if x[2] == "tall"]   # under the worktop


# --------------------------------------------------------------------------
# 3. On the floor; the model review reads the built model
# --------------------------------------------------------------------------

def test_a_fridge_over_the_floor_is_found_and_stands_on_the_floor():
    b = kitchen(extra=[fp("fr", "fridge", (2.0, 1.5), (0.6, 0.6), 0.0, mount_bottom_m=0.9)])
    found = FR.findings(b)
    assert [(f["rule"], f["piece"]) for f in found] == [("off_floor", "fr")] and found[0]["lift_m"] == 0.9
    assert PX.mount_bottom(by_id(b)["fr"]) == (0.0, False)                        # the build stands it on the floor
    assert PX.mount_bottom({"type": "wall_cabinet", "mount_bottom_m": 1.5}) == (1.5, False)
    on_top = kitchen(extra=[fp("fr", "fridge", (2.0, 1.5), (0.6, 0.6), 0.0)])
    floors = MR._room_floors(on_top)
    assert [f["rule"] for f in FR.findings(on_top, {"fr": (0.90, 2.75)}, floors)] == ["off_floor"]
    assert FR.findings(on_top, {"fr": (0.0, 1.85)}, floors) == []
    fitted = F.fit_building(b, _catalog(), snap=False)
    log = fitted["project"]["fridge_rule"]["findings"]
    assert [(f["rule"], f["stage"]) for f in log] == [("off_floor", "guard")] and "on the floor" in log[0]["fix"]


def test_the_model_review_flags_a_fridge_model_inside_a_run_or_on_its_worktop():
    b = kitchen(extra=[fp("fr", "fridge", (3.7, 1.0), (0.6, 0.6), 180.0)])
    by_id(b)["kB"]["asset"] = {"method": "module", "module_plan": MOD.plan_kitchen_run(dict(by_id(b)["kB"]))}
    by_id(b)["fr"]["asset"] = {"method": "library", "bbox_m": [0.6, 0.6, 1.85]}
    manifest = {"objects": [{"kind": "furniture", "element_id": "fr",
                             "box3d": {"center": [3.7, 1.0, 1.825], "size": [0.6, 0.6, 1.85]}}]}
    got = [f for f in MR.kitchen_design(b, manifest)[0] if f["target"] == "fr"]
    rules = sorted(f["metrics"]["rule"] for f in got)
    assert rules == ["fridge_in_run", "fridge_off_floor"] and all(f["severity"] == "critical" for f in got)
    # split around it (the plan's gap), standing on the floor: clean
    k = F.kitchen_built_ins(b)
    by_id(b)["kB"]["asset"]["module_plan"] = MOD.plan_kitchen_run(dict(by_id(b)["kB"], module_hints=F.run_hints(k, "kB")))
    manifest["objects"][0]["box3d"]["center"][2] = 0.925
    assert not [f for f in MR.kitchen_design(b, manifest)[0] if f["target"] == "fr"]


# --------------------------------------------------------------------------
# 4. The column fridge the user kept: a real appliance, not a steel box
# --------------------------------------------------------------------------

def test_the_column_fridge_has_door_seals_a_plinth_vent_and_a_display():
    french = KD.tall_module((0.0, 0.9, "fridge_french"), 0.6, 2.4, 0.1, look="steel")
    parts = KD.tall_parts(french, DESIGN, 0.6, 0.06)
    roles = {p.get("role") for p in parts}
    assert {"gasket", "grille", "display"} <= roles
    gasket = next(p for p in parts if p.get("role") == "gasket")
    assert gasket["key"] == "dark" and max(v[2] for v in gasket["verts"]) > 2.0    # behind the doors' gaps
    integrated = KD.tall_module((0.0, 0.6, "fridge_column"), 0.6, 2.4, 0.1, look="integrated")
    p_int = KD.tall_parts(integrated, DESIGN, 0.6, 0.06)
    assert "gasket" in {p.get("role") for p in p_int} and not [p for p in p_int if p.get("key") == "steel"]
