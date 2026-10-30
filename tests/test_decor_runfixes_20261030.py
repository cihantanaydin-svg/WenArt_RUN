"""Four decor findings of real04 run 20261029-201533-full (30 Oct 2026), each a general rule, checked on CPU:

1. GPU test ``test_surface_decor_rests_on_its_host``: the table lamp on a floating nightstand (R33: its 0.22 m box hung
   under its 0.50 m top) read as 0.28 m over its host: the test took the host's top for its box's bottom plus the
   mesh's height. The lamp stood on the real top; the items and hosts are now measured as built
   (``scene_checks.built_z_range``: ``box3d``) and a raised parametric piece records its real top (``top_m``).
2. GPU test ``test_ai_decor_is_built`` on the open-kitchen variant: the big loop's final round re-solved a bedroom of
   the base (its nightstand f_L0_052 became f_L0_057, the lamp dec_L0_031 handed over) and rebuilt the base only; the
   variant's scene kept the building of before (``Orchestrator.variants_again``).
3. / 4. Argus' criticals S5 (cushions dec_L0_011 / 012 4.9 cm in the bed f_L0_007) and X2 (dec_L1_013 through the
   roof at 5.32 m) were the 28 Oct run's (20261028-005318): that run's inspector record was never rewritten (the
   report raised "unhashable type: 'list'" on an accepted ``set_camera``) and four later runs' Argus read it as their
   own (``inspector.key_of``, ``failed_record``, ``written_utc``; ``audit.inputs.inspector_of_run``, process P13).
   In run 201533 the bed f_L0_007 (an HSSD model with its own pillows) got no decor cushion and dec_L1_013 was books
   at 3.68 m on a coffee table; its real roof findings (the bathrooms' towel rails, shelves and panels) are
   tests/test_under_roof_20261030.py's.
"""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from wenart.agent import inspector as INS
from wenart.audit import inputs as AI
from wenart.audit import process as PR
from wenart.blender import furniture as F
from wenart.blender import scene_checks as SC

RUN = Path("/home/user/WenArt_RUN/runs/20261029-201533-full/results")

# the run's records (renders/real04/scene_manifest.json): the floating nightstand and the lamp on it
NIGHTSTAND = {"name": "furn_f_L0_041", "kind": "furniture", "element_id": "f_L0_041", "type": "nightstand",
              "center": [0.4256, 4.0037, 0.25], "size": [0.4, 0.4, 0.5], "bbox_m": [0.4, 0.4015, 0.22],
              "box3d": {"center": [0.4263, 4.0037, 0.39], "size": [0.4, 0.4015, 0.22], "rotation_deg": 90.0}}
LAMP = {"name": "decor_f_L0_041_7", "kind": "decor", "type": "table_lamp", "host_id": "f_L0_041",
        "center": [0.426, 4.004, 0.7915], "size": [0.297, 0.2943, 0.583],
        "box3d": {"center": [0.426, 4.004, 0.7915], "size": [0.297, 0.2943, 0.583], "rotation_deg": 90.0}}


def test_decor_on_a_floating_nightstand_rests_on_its_real_top():
    bottom, _top = SC.built_z_range(LAMP)
    host_bottom, host_top = SC.built_z_range(NIGHTSTAND)
    assert (host_bottom, host_top) == pytest.approx((0.28, 0.50), abs=1e-3)
    assert host_bottom + 0.15 <= bottom <= host_top + 0.01             # the GPU test's rule
    # without box3d: the box's bottom plus top_m (the build's record of a raised piece), not plus the mesh's height
    old = {k: v for k, v in NIGHTSTAND.items() if k != "box3d"}
    assert SC.built_z_range(old)[1] == pytest.approx(0.22)              # what the test read before
    assert SC.built_z_range(dict(old, top_m=0.5))[1] == pytest.approx(0.5)
    hung = {"center": [0, 0, 1.45 + 0.35], "size": [0.6, 0.35, 0.7], "mount_bottom_m": 1.45, "top_m": 2.15}
    assert SC.built_z_range(hung) == pytest.approx((1.45, 2.15))        # a mount bottom is not counted twice


def test_a_raised_parametric_piece_records_its_real_top():
    from wenart.blender import detail_parts as DP
    from wenart.blender import parametric as P

    parts = DP.floating_nightstand(0.4, 0.4, 0.5)
    _x0, _y0, z0, _x1, _y1, z1 = P.parts_bbox(parts)
    assert z0 == pytest.approx(0.28) and F.raised_top_m((z0, z1)) == pytest.approx(0.5)
    assert F.raised_top_m((0.0, 0.5)) is None                            # standing on its floor: no record
    assert F.raised_top_m((0.28, 0.5), base=0.1) == pytest.approx(0.6)
    drum = DP.drum_nightstand(0.4, 0.4, 0.5)
    assert P.parts_bbox(drum)[2] == pytest.approx(0.0) and P.parts_bbox(drum)[5] == pytest.approx(0.5)


def test_the_gpu_test_measures_items_and_hosts_as_built():
    src = Path(__file__).with_name("gpu").joinpath("test_m9.py").read_text(encoding="utf-8")
    assert "built_z_range(host)" in src and "built_z_range(o)[0]" in src


def test_the_run_measures_every_surface_item_on_its_host():
    path = RUN / "renders/real04/scene_manifest.json"
    if not path.is_file():
        pytest.skip("the run's records are not on this machine")
    scene = json.loads(path.read_text(encoding="utf-8"))
    by_id = {o["element_id"]: o for o in scene["objects"] if o.get("kind") in ("furniture", "furniture_proxy")}
    n = 0
    for o in scene["objects"]:
        if o.get("kind") != "decor" or o.get("type") not in ("vase", "bowl", "plant_small", "table_lamp") \
                or not o.get("host_id"):
            continue
        hb, ht = SC.built_z_range(by_id[o["host_id"]])
        assert hb + 0.15 <= SC.built_z_range(o)[0] <= ht + 0.01, o["name"]
        n += 1
    assert n >= 10


# ------------------------------------------------------------------------------------------- 2. the variants

def _fake(tmp_path, fingerprints, views=3):
    """A fake orchestrator with one base and one variant run; ``fingerprints``: the variant's scene before and
    after its build."""
    from wenart.run import scheduler as SC_

    calls = []
    scene = tmp_path / "v" / "scene"
    scene.mkdir(parents=True)
    (scene / "scene_manifest.json").write_text(json.dumps({"build_fingerprint": fingerprints[0]}), encoding="utf-8")
    base = SimpleNamespace(base=None, active=True, name="p", label="p", out=tmp_path)
    var = SimpleNamespace(base=base, active=True, name="p", label="p/v", out=tmp_path / "v", no_views=False)

    def build(pr):
        calls.append(("build", pr.label))
        (scene / "scene_manifest.json").write_text(json.dumps({"build_fingerprint": fingerprints[1]}),
                                                   encoding="utf-8")

    fake = SimpleNamespace(runs=[base, var], out=lambda s: calls.append(("out", s)),
                           status_of=lambda pr, stage: "ok", stage_build=build,
                           scene_views=lambda pr: views,
                           stage_render=lambda pr: calls.append(("render", pr.label)),
                           stage_export=lambda pr: calls.append(("export", pr.label)),
                           final_stages_again=lambda pr, url: calls.append(("final", pr.label)))
    SC_.Orchestrator.variants_again(fake, "url")
    return [c for c in calls if c[0] != "out"]


def test_a_variant_follows_its_bases_final_building(tmp_path):
    assert _fake(tmp_path, ("a", "b")) == [("build", "p/v"), ("render", "p/v"), ("final", "p/v")]


def test_an_unchanged_variant_is_reused(tmp_path):
    assert _fake(tmp_path, ("a", "a")) == [("build", "p/v")]


def test_the_orchestrated_chain_brings_the_variants_up_to_date():
    from wenart.run import scheduler as SC_
    import inspect

    src = inspect.getsource(SC_.Orchestrator.final_chain)
    assert src.index("final_critical_rounds") < src.index("variants_again") < src.index("argus_final")


# ---------------------------------------------------------------------- 3. / 4. the inspector's record of the run

def test_the_inspector_report_takes_a_camera_edit(tmp_path):
    findings = {"code": [{"check": "X2", "severity": "critical", "target": "dec_1", "message": "through the roof"}],
                "vision_kept": [], "vision_dropped": []}
    accepted = [{"tool": "set_camera", "args": {"view_id": "cam_1", "position": [1.0, 2.0, 1.5],
                                                "target": [3.0, 2.0, 0.8]}, "finding_target": ["x"]}]
    rec = INS.report(tmp_path, 4, findings, accepted)              # raised "unhashable type: 'list'" before
    assert rec["code"][0]["target"] == "dec_1"
    INS.write(tmp_path, rec, "p")
    saved = json.loads((tmp_path / "orchestrator" / INS.REPORT_JSON).read_text(encoding="utf-8"))
    assert saved["written_utc"].endswith("Z")
    failed = INS.failed_record(4, "TypeError: boom")
    path = INS.write(tmp_path, failed, "p")
    assert "could not be made" in path.read_text(encoding="utf-8")


def test_argus_never_reads_an_earlier_runs_inspector_record():
    run = {"started_utc": "2026-10-29T20:20:18Z"}
    old = {"round": 2, "code": [{"check": "S5", "severity": "critical", "target": "dec_L0_011"}]}
    rec, why = AI.inspector_of_run(old, run)
    assert rec is None and "no time stamp" in why
    rec, why = AI.inspector_of_run(dict(old, written_utc="2026-10-28T03:38:00Z"), run)
    assert rec is None and "before the run started" in why
    fresh = dict(old, written_utc="2026-10-29T23:01:00Z")
    assert AI.inspector_of_run(fresh, run) == (fresh, None)
    assert AI.inspector_of_run(old, None) == (old, None)             # no run start known: read as before
    inp = SimpleNamespace(stale=[{"record": "inspector", "why": why or "stale"}], inspector={"error": "TypeError: x"})
    found = PR.records_of_run(inp)
    assert [f["check"] for f in found] == ["P13", "P13"] and found[0]["kind"] == "stale"


def test_the_run_201533_reads_no_stale_criticals():
    if not (RUN / "run_manifest.json").is_file():
        pytest.skip("the run's records are not on this machine")
    inp = AI.collected(RUN, "real04")
    assert inp.inspector is None and inp.stale and inp.stale[0]["record"] == "inspector"
    found = PR.records_of_run(inp)
    assert found and found[0]["check"] == "P13"
