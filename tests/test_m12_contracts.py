"""Milestone 12 contracts (docs/milestone12.md §13.2): the frozen signatures of the tracks' interfaces exist."""
import inspect

from wenart.blender import scene_checks
from wenart.furniture import catalog, decor, edit_ops, group_checks, groups, program, sizes, solver
from wenart.ingest.generic import levels as ingest_levels, reading
from wenart.levels import checks as level_checks, edits as level_edits, marks, model as level_model


def params(fn):
    return list(inspect.signature(fn).parameters)


def test_level_interfaces():
    assert params(marks.parse_mark) == ["text"]
    assert "KOT" in marks.MARK_ATTRIBUTE_TAGS
    assert params(level_model.infer_levels) == ["building", "brief"]
    assert level_checks.CHECKS == ("L1", "L2", "L3", "L4", "L5", "L6", "L7")
    assert params(level_checks.check_levels) == ["building", "scene_manifest", "render_manifest"]
    assert set(level_edits.LEVEL_EDIT_OPS) == set(level_edits.LEVEL_EDIT_SCHEMAS)
    assert params(level_edits.apply_level_edit) == ["building", "edit"]
    assert params(ingest_levels.apply_levels) == ["build", "works"]


def test_reading_interface():
    assert params(reading.read_furniture) == ["build", "works"]


def test_group_interfaces():
    assert params(program.room_program) == ["building", "room_id", "brief", "choices"]
    assert params(solver.solve_room) == ["building", "room_id", "program", "k", "fixed_ids"]
    assert params(solver.apply_candidate) == ["building", "room_id", "candidate"]
    assert group_checks.CHECKS == tuple(f"G{i}" for i in range(1, 15))
    assert params(group_checks.check_room) == ["building", "room_id"]
    assert params(group_checks.check_building) == ["building"]
    assert params(groups.load_groups) == []
    assert params(groups.group_members) == ["building", "room_id"]
    assert params(edit_ops.dry_run) == ["building", "edit", "catalog"]
    assert params(edit_ops.allowed_edits) == ["building", "piece_id"]


def test_scene_and_library_interfaces():
    assert scene_checks.CHECKS == ("S1", "S2", "S3", "S4", "S5", "S6")
    assert params(scene_checks.run_scene_checks) == ["building", "scene_objects", "out_path"]
    assert params(scene_checks.measure_pure) == ["meshes", "building"]
    assert scene_checks.TOLERANCES["decor_gap_m"] == 0.010
    assert scene_checks.TOLERANCES["decor_pen_soft_m"] == 0.030
    assert params(decor.sync_to_hosts) == ["building"]
    assert params(catalog.usable) == ["entry"]
    assert params(sizes.real_range) == ["ftype"]
    assert params(sizes.product_size) == ["ftype", "drawn"]
    assert params(sizes.fits) == ["ftype", "size", "tolerance"]


def test_licence_rule_of_10_oct_2026():
    assert catalog.usable({"licence": "CC-BY-4.0"})
    assert not catalog.usable({"licence": "CC-BY-NC-4.0"})
    assert not catalog.usable({"licence": "CC-BY-SA-4.0"})
    assert not catalog.usable({"licence": "CC-BY-NC-SA-4.0"})
    assert not catalog.usable({"licence": "CC0", "audit": {"status": "removed"}})
    assert catalog.usable({"licence": "CC0", "audit": {"status": "fix"}})
