"""Integration of the fix round after P3, part 2 (17 Oct 2026): the cross-track asks the lead applied.

What: CPU tests of the small changes made for track S's asks: check X6 counts the true aerial views per camera set
(the replayed set of ``--cameras-from`` and the searched set of ``--cameras-extra``), the before | after sheet names
a replayed aerial the build re-pitched (caption, ``sheets13.json`` record, ``sheets13.md`` note column), and the
scene manifest schema documents the re-pitch record (``replay``, ``pitch_deg``, ``horizon_frac``,
``cameras_from.repitched``).
Why: every behaviour change of the integration step gets a test that fails on the code of commit 62b2b3c (part 1).
How: small hand-made inputs and the toy run of ``tests/test_m13_report.py``; no Blender.
"""
from __future__ import annotations

import copy
import json

import jsonschema
import pytest
from PIL import Image

from wenart.blender import build as BB
from wenart.blender import cameras as CA
from wenart.blender import exterior_checks as X
from wenart.blender import schemas
from wenart.report import sheets13 as SH

PREP = {"outlines": {}, "roof": {}, "main_facade": {}}
AERIAL = {"name": "ext_5", "kind": "exterior", "view": "aerial", "position": [30.0, 30.0, 20.0],
          "target": [5.0, 4.0, 1.5]}

# real02's M11 ext_5 (results/renders/real02/scene_manifest.json): 30 degrees down at 28.54 mm, no sky
M11_EXT5 = {"name": "ext_5", "kind": "exterior", "view": "aerial", "lens_mm": 28.54, "sensor_mm": 36.0,
            "resolution": [1920, 1080], "shift_y": 0.0, "position": [-12.1724, -9.4236, 16.2917],
            "target": [7.1726, 6.517, 1.8195], "room_id": None, "level_id": None}


def _aerial_hits(cams):
    hits = []
    X._x6({}, PREP, {"cameras": cams}, None, hits)
    return [h for h in hits if "aerial views" in h["message"]]


def test_x6_counts_one_aerial_per_camera_set_replayed_and_searched():
    """S's ask: P4 builds with --cameras-from (the replayed M11 set: ext_5) and --cameras-extra (the searched set:
    ext_5_s, ``extra``). Part 1 counted both as two aerials and gave a minor X6 on every P4 build; each set may have
    its one true aerial. Two aerials in one set are still noted, and a site view is never counted."""
    replayed = dict(AERIAL, source="replayed")
    searched = dict(AERIAL, name="ext_5_s", source="searched", extra=True)
    assert _aerial_hits([replayed, searched]) == []
    assert _aerial_hits([replayed, searched, dict(searched, name="ext_7_s", site_view=True)]) == []
    two = _aerial_hits([replayed, dict(replayed, name="ext_9"), searched])
    assert len(two) == 1 and two[0]["severity"] == "minor" and two[0]["metrics"]["aerials"] == ["ext_5", "ext_9"]
    assert "searched set" not in two[0]["message"]
    extra_two = _aerial_hits([replayed, searched, dict(searched, name="ext_9_s")])
    assert len(extra_two) == 1 and extra_two[0]["metrics"]["aerials"] == ["ext_5_s", "ext_9_s"]
    assert "searched set of --cameras-extra" in extra_two[0]["message"]


def _repitched_plan() -> dict:
    plans = CA.replay_cameras({"cameras": [copy.deepcopy(M11_EXT5)]})["plans"]
    assert BB.repitch_replayed_aerials(plans) == ["ext_5"]
    return plans[0]


def test_the_scene_camera_schema_documents_the_repitch_record():
    """S's ask (documentation): the scene manifest camera's ``replay`` record, ``pitch_deg`` and ``horizon_frac``
    and ``cameras_from.repitched`` are typed in the schema; the record the build writes validates, a wrong status or a
    non-string name does not."""
    plan = _repitched_plan()
    for key in ("replay", "pitch_deg", "horizon_frac"):
        assert key in schemas.SCENE_CAMERA["properties"], key
    assert "repitched" in schemas.CAMERAS_FROM["properties"]
    cam = dict(plan, index=1, visible_openings=[], visible_furniture=[], warning=None)
    jsonschema.validate(cam, schemas.SCENE_CAMERA)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(dict(cam, replay=dict(cam["replay"], status="moved")), schemas.SCENE_CAMERA)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(dict(cam, pitch_deg="down"), schemas.SCENE_CAMERA)
    summary = BB.cameras_from_summary({"path": "m.json"}, {"plans": [plan], "dropped": []}, [plan], False)
    jsonschema.validate(summary, schemas.CAMERAS_FROM)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(dict(summary, repitched=[1]), schemas.CAMERAS_FROM)


def test_the_before_after_sheet_names_a_repitched_replayed_aerial(tmp_path):
    """S's ask: P4's ext_5 is re-pitched by the build (15.66 degrees at 26 mm, was 30 degrees at 28.54 mm), so it is
    not frame-identical to its M11 baseline. Its sheet gets a fourth caption line, its record ``camera_note`` and the
    index a note column; every other sheet keeps its size and has no note."""
    from test_m13_report import CAMERAS, make_run
    from wenart.report import final as F

    after = make_run(tmp_path / "a", "toy")
    F.write_final(after)
    scene_path = after / "scene" / "scene_manifest.json"
    scene = json.loads(scene_path.read_text(encoding="utf-8"))
    ext = next(c for c in scene["cameras"] if c["name"] == "ext_1")
    ext["replay"] = _repitched_plan()["replay"]
    scene_path.write_text(json.dumps(scene), encoding="utf-8")
    out = tmp_path / "sheets"
    result = SH.sheets(after, after, out)
    rec = {r["camera"]: r for r in result["records"]}
    note = rec["ext_1"]["camera_note"]
    assert note.startswith("replayed aerial re-pitched from 30.0 to 15.7 degrees down at 26 mm (was 28.54 mm)")
    assert "horizon 1.31 -> 0.86" in note and "CLAUDE.md horizon rule" in note
    assert all(rec[c]["camera_note"] is None for c, *_ in CAMERAS if c != "ext_1")
    tall = Image.open(out / result["sheets"]["ext_1"])
    assert tall.height == SH.TILE_HEIGHT + 6 + 21 * 4 + 3 > SH.TILE_HEIGHT + SH.CAPTION_HEIGHT
    assert Image.open(out / result["sheets"]["cam_salon_1"]).height == SH.TILE_HEIGHT + SH.CAPTION_HEIGHT
    index = (out / SH.INDEX_MD).read_text(encoding="utf-8")
    assert "| sheet | note |" in index and note in index
    assert json.loads((out / SH.INDEX_JSON).read_text(encoding="utf-8"))["records"][-1]["camera_note"] == note
    assert SH.camera_note({"replay": {"status": "repitched"}}) == \
        "replayed camera re-pitched by the build (CLAUDE.md horizon rule)"
    assert SH.camera_note({"replay": {"status": "kept"}}) is None and SH.camera_note(None) is None
