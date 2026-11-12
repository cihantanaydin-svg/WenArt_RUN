"""12 Nov 2026 (the coordinator: the building-sense audit rules are being verified against every project by misfire
hunters; their guards drop in without a rewrite): every change a completion rule makes passes
``wenart.ingest.rule_guards.blocked`` first.

What: every rule key is asked by its rule; a guard (one function) stops one change and the stop is logged with the
rule, its audit ids, the item and the reason; a rule switched off by its key or its audit id (code, environment,
``level_inference.rules_off``) makes no change; without guards the rules work as before.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from test_core_rules_20261112 import block, run
from test_sense_rules_20261112 import balcony_site, building, flat

from wenart import building as B
from wenart.ingest import completion as CP
from wenart.ingest import rule_guards as RG
from wenart.ingest import sense_rules as SR

ROOT = Path(__file__).resolve().parents[1] / "wenart" / "ingest"


@pytest.fixture(autouse=True)
def clean(monkeypatch):
    monkeypatch.delenv("WENART_RULES_OFF", raising=False)
    saved = {k: list(v) for k, v in RG.GUARDS.items()}
    yield
    RG.GUARDS.clear()
    RG.GUARDS.update(saved)
    RG.OFF.clear()


def test_every_rule_key_is_asked_by_its_rule():
    src = "".join((ROOT / f).read_text(encoding="utf-8") for f in ("completion.py", "core_rules.py", "sense_rules.py"))
    asked = set(re.findall(r'RG\.blocked\(\s*"([a-z_]+)"', src))
    asked |= {"stair_box", "stair_typical_copy", "stair_dogleg"} if 'RG.blocked(kind, b' in src else set()
    assert asked == set(RULES := RG.RULES), sorted(set(RULES) ^ asked)
    assert all(ids and all(re.fullmatch(r"R\d\d", i) for i in ids) and what for ids, what in RULES.values())


def test_a_guard_stops_one_change_and_says_why():
    RG.guard("lift_door_add")(lambda b, item: "a through-car lift is drawn" if item["level_id"] == "L1" else None)
    b = block()
    rec = run(b)
    assert [x["level_id"] for x in rec["lift_doors"]["added"]] == ["L0"]
    log = b["level_inference"]["guarded"]
    assert [(e["rule"], e["item"]["level_id"], e["reason"]) for e in log] == \
        [("lift_door_add", "L1", "a through-car lift is drawn")]
    assert log[0]["audit"] == ["R19"] and log[0]["item"]["lift"] == "r_L1_lift"


def test_a_rule_switched_off_by_its_audit_id_makes_no_change(monkeypatch):
    monkeypatch.setenv("WENART_RULES_OFF", "R16, stair_box")
    b = block()
    rec = run(b)
    assert rec["core_gaps"] == [] and rec["stairs"] == []
    assert {o["id"] for o in b["openings"]} >= {"o_L0_gap", "o_L1_gap"}
    # R16 also covers the removal of a lift door into a flat's room
    assert rec["lift_doors"]["removed"] == []
    rules = {e["rule"] for e in b["level_inference"]["guarded"]}
    assert {"core_gap", "stair_box", "lift_door_remove"} <= rules
    assert all("WENART_RULES_OFF" in e["reason"] for e in b["level_inference"]["guarded"])


def test_the_building_can_switch_a_rule_off_and_the_log_holds_each_item_once():
    b = building(flat(), site=balcony_site())
    b["level_inference"]["rules_off"] = ["balcony_door"]
    assert SR.balcony_doors(b, B.IdCounter().next) == []
    assert SR.balcony_doors(b, B.IdCounter().next) == []
    assert [e["rule"] for e in b["level_inference"]["guarded"]] == ["balcony_door"]


def test_a_guard_can_keep_a_level_above_ground():
    b = building(flat())
    b["levels"][0].update(kind="basement", order=-1)
    assert CP.below_ground(b, b["levels"][0])
    RG.OFF.add("below_ground")
    assert CP.below_ground(b, b["levels"][0]) is None


def test_without_guards_the_rules_work_as_before():
    b = block()
    rec = run(b)
    assert rec["stairs"] and rec["core_gaps"] and rec["lift_doors"]["added"]
    assert "guarded" not in b["level_inference"]
    with pytest.raises(KeyError):
        RG.guard("no_such_rule")
