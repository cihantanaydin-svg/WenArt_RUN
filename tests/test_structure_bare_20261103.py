"""3 Nov 2026 (user, real04 structure run 20261103-131052-full: "last zip top down views are still having furnitures
inside, why there are furnitures inside in the last pod run?"): the structure profile builds the bare building. Only
the drawn fixed equipment (stairs, kitchen runs and appliances, sanitary ware: CLAUDE.md treats it like walls) stays;
drawn movable furniture, the AI's added pieces and the decor are left out of that build, and the flag enters the build
fingerprint so a bare scene is never reused for a furnished one. CPU only."""
from __future__ import annotations

from pathlib import Path

from wenart.blender import build as B

ROOT = Path(__file__).resolve().parents[1]


def _piece(pid, ftype, source="from_documents"):
    return {"id": pid, "type": ftype, "source": source, "footprint": {"center": [0, 0], "size": [1, 1]}}


def test_bare_building_keeps_only_the_drawn_fixed_equipment():
    b = {"furniture": [_piece("s", "stair"), _piece("k", "kitchen_counter"), _piece("w", "toilet"),
                       _piece("f", "fridge", "added_by_ai"), _piece("sofa", "sofa"), _piece("bed", "bed_double"),
                       _piece("plant", "potted_plant", "added_by_ai"), _piece("u", "unknown")],
         "decor": [{"id": "vase"}], "wall_items": [{"id": "art"}], "bedding": {"x": 1}, "walls": [{"id": "w1"}]}
    bare, out, kept = B.bare_building(b)
    assert [f["id"] for f in bare["furniture"]] == ["s", "k", "w"]
    assert (out, kept) == (5, 3)
    assert bare["decor"] == [] and bare["wall_items"] == [] and bare["bedding"] == {}
    assert bare["walls"] == [{"id": "w1"}]
    assert len(b["furniture"]) == 8 and b["decor"]          # the input is not changed


def test_the_bare_flag_comes_from_the_environment_and_enters_the_fingerprint(monkeypatch):
    assert B.bare_build_flag({}) is False
    assert B.bare_build_flag({B.BARE_ENV: "1"}) is True
    monkeypatch.delenv(B.BARE_ENV, raising=False)
    furnished = B.fingerprint_args("b.json")
    monkeypatch.setenv(B.BARE_ENV, "1")
    bare = B.fingerprint_args("b.json")
    assert furnished["bare"] is False and bare["bare"] is True
    assert B.build_fingerprint(furnished) != B.build_fingerprint(bare)


def test_the_structure_job_and_scheduler_turn_bare_builds_on():
    job = (ROOT / "scripts" / "jobs" / "full.sh").read_text(encoding="utf-8")
    assert 'export WENART_BARE_BUILD=1' in job
    sched = (ROOT / "wenart" / "run" / "scheduler.py").read_text(encoding="utf-8")
    assert 'os.environ["WENART_BARE_BUILD"] = "1"' in sched
    assert B.BARE_ENV == "WENART_BARE_BUILD"
