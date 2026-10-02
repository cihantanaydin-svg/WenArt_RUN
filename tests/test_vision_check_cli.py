"""CPU tests of the vision-check CLI, answers file, plan crops and the whole flow with fake models (§5.2, §5.7).

The toy project of tests/vc_toy.py is checked end to end with fake clients
that implement only ``.model`` and ``.run_schema``: expected -> plan-crops ->
select-controls -> run (both models, every image kind) -> preference ->
combine -> calibrate. Also: the plan-crop mapping (a known building point
lands on a known pixel), resumable answers (reuse, stale inputs, failed
calls, deadline, a crash mid-run), single-pass mode, check_incomplete and
the style-photo pass.
"""
import json
import sys
import types
from pathlib import Path

import pytest
from PIL import Image

import vc_toy as T
from wenart import views as V
from wenart.vision_check import calls as C
from wenart.vision_check import plan_crop as PC
from wenart.vision_check.cli import main
from wenart.vision_check.project import Project

CAM = T.CAMERA["name"]
CYC = f"renders/{CAM}.png"
POL = f"polish/{CAM}_a1.png"


def factory_for(clients: dict, **kw):
    """client_factory(model_key, base_url) -> a FakeClient (one per key, kept in ``clients``)."""
    def factory(key, url):
        clients.setdefault(key, T.FakeClient(model=f"fake/{key}", **kw))
        clients[key].url = url
        return clients[key]
    return factory


def read(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def element_box(out: Path, wid: str) -> list:
    exp = read(out / "check" / "expected_views.json")["views"][CAM]
    return next(e["box_1000"] for e in exp["elements"] if e["wenart_id"] == wid)


# --------------------------------------------------------------------------
# Plan crop
# --------------------------------------------------------------------------

def test_plan_crop_maps_a_known_building_point_to_its_pixel(tmp_path):
    out = T.write_toy_project(tmp_path)
    assert main(["plan-crops", "--project-out", str(out)]) == 0
    info = read(out / "check" / "plan_crops.json")["views"][CAM]
    assert info["plan"] == f"{CAM}_plan.jpg" and info["document"] == "plan.png" and info["page"] == 1
    jpg = out / "check" / f"{CAM}_plan.jpg"
    assert jpg.stat().st_size <= 300_000
    project = Project(out)
    raster = PC.load_raster(project.building["documents"][0], project.building["documents"][0]["pages"][0],
                            project.project_dir / "plan.png")
    page = project.building["documents"][0]["pages"][0]
    room = project.room("r_salon")
    image, mapping = PC.render_plan_crop(raster, page, room, T.CAMERA, [], project.building)
    # Building (X, Y) -> page pixel ((X + 1) * 100, (6 - Y) * 100) by the page's transform_to_building.
    assert mapping.to_raster_px((0.0, 0.0)) == pytest.approx((100.0, 600.0))
    assert mapping.to_raster_px((6.0, 4.0)) == pytest.approx((700.0, 200.0))
    # The crop is the room + 0.5 m: its origin is building (-0.5, 4.5) = page pixel (50, 150); the
    # 700 x 500 crop is scaled up to 800 px on its longest side before drawing.
    s = 800 / 700
    assert mapping.origin == (50, 150) and mapping.scale == pytest.approx(s) and image.size == (800, 571)
    assert mapping.to_crop((0.0, 0.0)) == pytest.approx((50.0 * s, 450.0 * s))
    assert mapping.to_crop((6.0, 4.0)) == pytest.approx((650.0 * s, 50.0 * s))
    # The drawn room corner of the source page is dark at that crop pixel.
    plain = Image.open(project.project_dir / "plan.png").convert("L").crop((50, 150, 750, 650))
    assert plain.getpixel((51, 449)) < 60
    assert info["crop_origin_px"] == [50, 150]


def test_plan_page_selection_and_dwg_source(tmp_path):
    def page(level, cls="floor_plan", n=1, t=True):
        return {"page": n, "class": cls, "level_id": level, "transform_to_building": [1, 0, 0, 0, 1, 0] if t else None}
    building = {"documents": [
        {"id": "a", "file": "plan.pdf", "format": "pdf", "pages": [page("L0", n=1), page("L1", n=2)]},
        {"id": "b", "file": "zemin.dxf", "format": "dxf", "pages": [page("L0")]},
        {"id": "c", "file": "furn.dxf", "format": "dxf", "pages": [page("L0", cls="furniture_plan")]},
        {"id": "d", "file": "scan.png", "format": "image", "pages": [page("L0", t=False)]},
    ]}
    assert PC.plan_page(building, "L0", {})[0]["file"] == "zemin.dxf"            # DXF before PDF
    cited = {"evidence": [{"file": "plan.pdf", "page": 1}]}
    assert PC.plan_page(building, "L0", cited)[0]["file"] == "plan.pdf"           # the room's evidence wins
    assert PC.plan_page(building, "L1", {})[1]["page"] == 2
    assert PC.plan_page(building, "L9", {}) is None
    conv = tmp_path / "out" / "converted"
    conv.mkdir(parents=True)
    (conv / "kat.dxf").write_text("0\nEOF\n")
    assert PC.source_file({"file": "kat.dwg", "format": "dwg"}, tmp_path / "proj", tmp_path / "out") == conv / "kat.dxf"
    assert PC.source_file({"file": "nope.pdf", "format": "pdf"}, tmp_path / "proj", tmp_path / "out") is None


def test_plan_crop_without_a_page_is_reported_not_raised(tmp_path):
    out = T.write_toy_project(tmp_path)
    b = read(out / "building_final.json")
    b["documents"][0]["pages"][0]["level_id"] = "L9"
    (out / "building_final.json").write_text(json.dumps(b), encoding="utf-8")
    assert main(["plan-crops", "--project-out", str(out)]) == 0
    info = read(out / "check" / "plan_crops.json")
    assert info["views"][CAM]["plan"] is None and "no page" in info["warnings"][0]


# --------------------------------------------------------------------------
# Answers file: resumable, stale, failed, deadline
# --------------------------------------------------------------------------

def test_answers_are_resumable_and_stale_inputs_are_asked_again(tmp_path):
    out = T.write_toy_project(tmp_path, polished=True)
    clients = {}
    f = factory_for(clients, truth={CYC: T.TOY_TYPES, POL: T.TOY_TYPES})
    args = ["run", "--project-out", str(out), "--model-key", "qwen", "--server", "http://x:8001/v1"]
    assert main(args, client_factory=f) == 0
    assert clients["qwen"].url == "http://x:8001/v1" and len(clients["qwen"].calls) == 2     # cycles + polished
    answers = read(out / "check" / "answers_qwen3-vl-8b.json")
    assert answers["model"] == "fake/qwen" and answers["slug"] == "qwen3-vl-8b" and not answers["incomplete"]
    rec = answers["calls"][f"check|{CAM}|cycles"]
    assert rec["camera"] == CAM and rec["image_kind"] == "cycles" and rec["prompt_kind"] == "check"
    assert rec["data"]["elements"] and rec["error"] is None and rec["images"] == [f"../renders/{CAM}.png"]
    assert set(rec) >= {"prompt", "raw_text", "latency_s", "input_sha256", "labels"}
    assert "decoy" in rec["labels"].values()
    # Second run: nothing is asked again.
    assert main(args, client_factory=f) == 0
    assert len(clients["qwen"].calls) == 2
    # A new polished image: only that call is stale and asked again.
    V.write_png_rgb(out / "polish" / f"{CAM}_a1.png", V.read_rgb(out / "renders" / f"{CAM}.png"))
    assert main(args, client_factory=f) == 0
    assert [c["images"][0] for c in clients["qwen"].calls[2:]] == [POL]


def test_failed_calls_are_recorded_and_retried(tmp_path):
    out = T.write_toy_project(tmp_path)
    clients = {}
    assert main(["run", "--project-out", str(out), "--model-key", "glm"],
                client_factory=factory_for(clients, fail={CYC})) == 0
    rec = read(out / "check" / "answers_glm-4.6v-flash.json")["calls"][f"check|{CAM}|cycles"]
    assert rec["data"] is None and "refused" in rec["error"]
    clients["glm"].fail = set()
    clients["glm"].truth = {CYC: T.TOY_TYPES}
    assert main(["run", "--project-out", str(out), "--model-key", "glm"], client_factory=factory_for(clients)) == 0
    assert read(out / "check" / "answers_glm-4.6v-flash.json")["calls"][f"check|{CAM}|cycles"]["data"]


def test_deadline_starts_no_new_call(tmp_path, monkeypatch):
    out = T.write_toy_project(tmp_path, polished=True)
    clients = {}
    monkeypatch.setenv("WENART_DEADLINE", "1")                  # long past
    assert main(["run", "--project-out", str(out), "--model-key", "qwen"], client_factory=factory_for(clients)) == 0
    answers = read(out / "check" / "answers_qwen3-vl-8b.json")
    assert answers["incomplete"] is True and answers["calls"] == {} and not clients["qwen"].calls
    # run_specs with a clock that passes the deadline after the first call.
    project = Project(out)
    specs = C.build_specs(project, C.check_kinds(project, ["cycles", "polished"]), [], "fake/qwen")
    store = C.AnswerStore(tmp_path / "a.json", "qwen", "qwen3-vl-8b", "fake/qwen")
    ticks = iter([0.0, 10.0, 10.0])
    stats = C.run_specs(specs, store, T.FakeClient(model="fake/qwen"), deadline=5.0, clock=lambda: next(ticks),
                        log=lambda *_: None)
    assert stats == {"asked": 1, "reused": 0, "failed": 0, "left": 1, "incomplete": True}
    assert read(tmp_path / "a.json")["incomplete"] is True


def test_answers_file_is_written_after_every_call(tmp_path):
    out = T.write_toy_project(tmp_path, polished=True)

    class Crashing(T.FakeClient):
        def run_schema(self, *a, **kw):
            if len(self.calls) >= 1:
                raise KeyboardInterrupt("pod stopped")
            return super().run_schema(*a, **kw)

    with pytest.raises(KeyboardInterrupt):
        main(["run", "--project-out", str(out), "--model-key", "qwen"],
             client_factory=lambda k, u: Crashing(model="fake/qwen", truth={CYC: T.TOY_TYPES}))
    calls = read(out / "check" / "answers_qwen3-vl-8b.json")["calls"]
    assert list(calls) == [f"check|{CAM}|cycles"]


def test_unknown_kind_or_model_key_exits_2(tmp_path, capsys):
    out = T.write_toy_project(tmp_path)
    f = factory_for({})
    assert main(["run", "--project-out", str(out), "--model-key", "qwen", "--kinds", "cycles,bogus"],
                client_factory=f) == 2
    assert main(["run", "--project-out", str(out), "--model-key", "llava"], client_factory=f) == 2
    assert main(["combine", "--project-out", str(out), "--models", "qwen,llava"]) == 2
    assert main(["calibrate", "--project-out", str(out)]) == 2                   # no manifest yet
    assert "bogus" in capsys.readouterr().err


# --------------------------------------------------------------------------
# End to end
# --------------------------------------------------------------------------

def run_flow(out: Path, keys=("qwen", "glm"), truth=None, extras=None, fail=None, prefer=None, kinds=None,
             capsys=None) -> dict:
    assert main(["expected", "--project-out", str(out)]) == 0
    assert main(["plan-crops", "--project-out", str(out)]) == 0
    assert main(["select-controls", "--project-out", str(out)]) == 0
    for c in read(out / "check" / "controls.json")["controls"]:
        T.write_control(out, c["id"])
    clients = {}
    for key in keys:
        f = factory_for(clients, truth=truth, extras=extras, fail=(fail or {}).get(key, ()), prefer=prefer)
        assert main(["run", "--project-out", str(out), "--model-key", key, "--kinds",
                     kinds or "cycles,polished,controls,plan_ab"], client_factory=f) == 0
        assert main(["preference", "--project-out", str(out), "--model-key", key], client_factory=f) == 0
    assert main(["combine", "--project-out", str(out), "--models", ",".join(keys)]) == 0
    assert main(["calibrate", "--project-out", str(out)]) == 0
    return clients


def test_end_to_end_with_fake_models(tmp_path, capsys):
    out = T.write_toy_project(tmp_path, polished=True)
    assert main(["expected", "--project-out", str(out)]) == 0
    assert main(["select-controls", "--project-out", str(out)]) == 0
    printed = capsys.readouterr().out.splitlines()
    controls = read(out / "check" / "controls.json")
    assert [l for l in printed if l.startswith("CONTROL\t")] == [
        f"CONTROL\t{c['id']}\t{c['camera']}\t{int(c['plug'])}\t{c['dir']}" for c in controls["controls"]]
    assert any(l.startswith("HIDE_SETS\t") and "win_1+plug" in l for l in printed)
    assert {c["id"] for c in controls["controls"]} == {"f_sofa", "win_1", "d_1"}
    # Both models see what the renders show and report the sofa as an extra where it stands
    # (on the Cycles image it is an indexed element and dropped; on the insertion check it is new).
    sofa_box = element_box(out, "f_sofa")
    extras = {CYC: [{"category": "sofa", "box": sofa_box, "confidence": 0.9}]}
    truth = {CYC: set(T.TOY_TYPES), POL: set(T.TOY_TYPES)}
    for c in controls["controls"]:
        truth[f"hide_{c['id']}/{CAM}.png"] = set(T.TOY_TYPES) - {c["type"]}
    clients = run_flow(out, truth=truth, extras=extras, prefer={POL: 1})

    check = out / "check"
    manifest = read(check / "check_manifest.json")
    assert manifest["schema_version"] == "0.1" and manifest["project"] == "toy" and not manifest["single_pass"]
    assert set(manifest["models"]) == {"qwen", "glm"} and manifest["models"]["glm"]["id"] == "zai-org/GLM-4.6V-Flash"
    view = manifest["views"][CAM]
    kinds = {k for k, v in view.items() if isinstance(v, dict) and "verdict" in v}
    assert kinds == {"cycles", "polished", "removal:f_sofa", "insertion:f_sofa", "removal:win_1", "insertion:win_1",
                     "removal:d_1", "insertion:d_1", "swap:f_sofa", f"plan_ab:{CAM}", "plan_ab:removal:f_sofa",
                     "plan_ab:removal:win_1", "plan_ab:removal:d_1"}
    cyc = view["cycles"]
    assert cyc["verdict"] == "ok" and cyc["unreliable"] == [] and cyc["decoy"]["passes"] == {"qwen": "absent",
                                                                                              "glm": "absent"}
    sofa = cyc["elements"]["f_sofa"]
    assert set(sofa) >= {"label", "role", "source", "passes", "result"} and sofa["result"] == "ok"
    assert sofa["passes"]["qwen"] == {"status": "present", "seen_as": "sofa", "confidence": 0.9, "normalised": False,
                                      "unreliable": False}
    assert cyc["extras"] == [] and cyc["extras_dropped"] == {"qwen": 1, "glm": 1}
    assert not view["polished_rejected"] and view["polished_reason"] is None and not view["needs_review"]
    assert view["polished"]["preference"]["preferred"] and view["polished"]["preference"]["votes"] == 4
    for cid in ("f_sofa", "win_1", "d_1"):
        assert view[f"removal:{cid}"]["control"]["confirmed"]
    assert view["insertion:f_sofa"]["control"]["confirmed"]
    assert not view["insertion:win_1"]["control"]["confirmed"]          # nobody reported a window extra
    assert view["swap:f_sofa"]["control"]["confirmed"]                     # asked for a bed_double: absent
    # Plan A/B calls send the plan crop as the second image with its label.
    ab = [c for c in clients["qwen"].calls if c["images"][-1].endswith("_plan.jpg")]
    assert ab and ab[0]["labels"] == ["Image 1 (the render to check):",
                                      "Image 2 (source floor plan of this room, for orientation):"]
    # Calibration and advisory.
    cal = read(check / "check_calibration.json")
    assert set(cal) >= {"metrics", "targets", "missed", "advisory", "plan_ab"}
    assert cal["metrics"]["removal_flagged"] == 1.0 and cal["metrics"]["insertion"] == pytest.approx(1 / 3, abs=1e-3)
    assert {m["metric"] for m in cal["missed"]} == {"insertion"}
    assert manifest_after(check)["advisory"] is True and "insertion" in manifest_after(check)["advisory_reason"]
    # Debug images and the report.
    for kind in kinds:
        jpg = check / f"{CAM}_{C.kind_slug(kind)}_check.jpg"
        assert jpg.is_file() and jpg.stat().st_size <= 300_000, kind
    report = (check / "check_report.md").read_text(encoding="utf-8")
    for heading in ("# Vision check report: toy", "## Per view", "## Mismatches on the Cycles renders",
                    "## JSON cross-check", "## Polished images rejected", "## Controls", "## Calibration",
                    "## Source plan"):
        assert heading in report
    assert "ADVISORY" in report


def manifest_after(check: Path) -> dict:
    return read(check / "check_manifest.json")


def test_end_to_end_polish_rejected_and_needs_review(tmp_path):
    out = T.write_toy_project(tmp_path, polished=True, drop=("f_table",))
    truth = {CYC: set(T.TOY_TYPES), POL: set(T.TOY_TYPES) - {"armchair"}}
    run_flow(out, truth=truth, kinds="cycles,polished")
    view = read(out / "check" / "check_manifest.json")["views"][CAM]
    assert view["polished_rejected"] and view["polished_reason"] == "vision_check"
    assert view["polished_reasons"][0]["id"] == "f_arm" and view["polished"]["elements"]["f_arm"]["result"] == "missing"
    assert CB_NOTE in view["polished"]["elements"]["f_arm"]["notes"]
    # The table is in the building JSON but was not rendered: the view needs review (never fixed).
    assert view["needs_review"] and any("f_table" in r for r in view["needs_review_reasons"])
    report = (out / "check" / "check_report.md").read_text(encoding="utf-8")
    assert "in JSON, not rendered: f_table" in report and "f_arm (armchair, added_by_ai) ok -> missing" in report


CB_NOTE = "added_by_ai: render/polish issue, not a document conflict"


def test_end_to_end_check_incomplete_and_single_pass(tmp_path):
    out = T.write_toy_project(tmp_path, polished=True)
    truth = {CYC: set(T.TOY_TYPES), POL: set(T.TOY_TYPES)}
    run_flow(out, truth=truth, fail={"glm": {POL}}, kinds="cycles,polished")
    view = read(out / "check" / "check_manifest.json")["views"][CAM]
    assert view["polished"]["verdict"] == "not_computed" and view["polished_reason"] == "check_incomplete"
    assert view["polished_rejected"]
    # The same answers combined as one model: single pass, info, advisory.
    assert main(["combine", "--project-out", str(out), "--models", "qwen"]) == 0
    m = read(out / "check" / "check_manifest.json")
    assert m["single_pass"] and m["advisory"] and m["views"][CAM]["cycles"]["verdict"] == "info"
    assert {e["result"] for e in m["views"][CAM]["cycles"]["elements"].values()} == {"unverified"}
    assert not m["views"][CAM]["polished_rejected"]
    assert main(["calibrate", "--project-out", str(out)]) == 0
    assert read(out / "check" / "check_calibration.json")["advisory"] is True


def test_yes_biased_model_is_unreliable_and_blocks_the_polish(tmp_path):
    out = T.write_toy_project(tmp_path, polished=True)
    assert main(["expected", "--project-out", str(out)]) == 0
    clients = {}
    for key, see_all in (("qwen", True), ("glm", False)):
        f = factory_for(clients, truth={CYC: set(T.TOY_TYPES), POL: set(T.TOY_TYPES)}, see_all=see_all)
        assert main(["run", "--project-out", str(out), "--model-key", key], client_factory=f) == 0
    assert main(["combine", "--project-out", str(out)]) == 0
    view = read(out / "check" / "check_manifest.json")["views"][CAM]
    assert view["cycles"]["unreliable"] == ["qwen"] and view["polished_reason"] == "check_incomplete"
    assert main(["calibrate", "--project-out", str(out)]) == 0
    cal = read(out / "check" / "check_calibration.json")
    assert cal["metrics"]["models"]["qwen"]["decoy_accept"] == 1.0
    assert any(m["metric"] == "decoy_accept[qwen]" for m in cal["missed"])


def test_stale_render_answers_are_not_used(tmp_path):
    out = T.write_toy_project(tmp_path)
    f = factory_for({}, truth={CYC: set(T.TOY_TYPES)})
    for key in ("qwen", "glm"):
        assert main(["run", "--project-out", str(out), "--model-key", key], client_factory=f) == 0
    rgb = V.read_rgb(out / "renders" / f"{CAM}.png")
    V.write_png_rgb(out / "renders" / f"{CAM}.png", 255 - rgb)                 # re-rendered, not re-checked
    assert main(["combine", "--project-out", str(out)]) == 0
    m = read(out / "check" / "check_manifest.json")
    assert m["views"][CAM]["cycles"]["verdict"] == "not_computed"
    assert any("stale answer" in w for w in m["warnings"])


def test_controls_with_missing_or_unhidden_renders_are_dropped(tmp_path):
    out = T.write_toy_project(tmp_path)
    assert main(["select-controls", "--project-out", str(out)]) == 0
    T.write_control(out, "f_sofa")
    # win_1's folder holds a render that still shows the window: dropped, not an error.
    hdir = out / "controls" / "hide_win_1"
    entry = T.write_render(hdir, CAM, *T.raycast(T.default_boxes(), T.default_openings()))
    T.write_manifest(hdir, [entry])
    project = Project(out)
    assert [c["id"] for c in project.controls()] == ["f_sofa"]
    assert any("win_1" in w and "still contains" in w for w in project.warnings)
    assert any("d_1" in w and "no render" in w for w in project.warnings)


def test_no_current_views_is_an_error_for_expected_and_combine(tmp_path, capsys):
    out = T.write_toy_project(tmp_path)
    manifest = read(out / "renders" / "render_manifest.json")
    del manifest["renders"][0]["render_key"]                    # pre-M5 entry: stale
    (out / "renders" / "render_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    assert main(["expected", "--project-out", str(out)]) == 1
    assert main(["combine", "--project-out", str(out)]) == 1
    assert "stale" in capsys.readouterr().err


def test_polish_made_from_another_render_is_not_checked(tmp_path):
    out = T.write_toy_project(tmp_path, polished=True)
    pm = read(out / "polish" / "polish_manifest.json")
    pm["views"][0]["source_sha256"] = "0" * 64
    (out / "polish" / "polish_manifest.json").write_text(json.dumps(pm), encoding="utf-8")
    project = Project(out)
    assert project.polished() == {} and any("another Cycles render" in w for w in project.warnings)
    pm["views"][0]["source_sha256"] = project.file_sha(out / "renders" / f"{CAM}.png")
    (out / "polish" / "polish_manifest.json").write_text(json.dumps(pm), encoding="utf-8")
    assert list(Project(out).polished()) == [CAM]


def test_sweep_preference_uses_the_two_strongest_accepted_attempts(tmp_path):
    out = T.write_toy_project(tmp_path)
    sweep = out / "polish" / "sweep"
    rgb = V.read_rgb(out / "renders" / f"{CAM}.png")
    attempts = []
    for k, (strength, decision, role) in enumerate([(0.125, "accept", "grid"), (0.5, "reject", "grid"),
                                                     (0.375, "accept", "grid"), (0.25, "accept", "grid"),
                                                     (0.75, "accept", "presumed_bad")], 1):
        V.write_png_rgb(sweep / f"{CAM}_a{k}.png", rgb)
        attempts.append({"k": k, "role": role, "strength": strength, "png": f"{CAM}_a{k}.png",
                         "gate": {"decision": decision}})
    (sweep / "polish_manifest.json").write_text(json.dumps({"kind": "sweep", "views": [
        {"camera": CAM, "attempts": attempts, "final": None, "final_attempt": None}]}), encoding="utf-8")
    project = Project(out)
    assert [a["k"] for a in project.sweep_attempts()[CAM]] == [3, 4]
    clients = {}
    for key in ("qwen", "glm"):
        f = factory_for(clients, prefer={f"sweep/{CAM}_a3.png": 1})
        assert main(["preference", "--project-out", str(out), "--model-key", key, "--kinds", "sweep"],
                    client_factory=f) == 0
    assert len(clients["qwen"].calls) == 4                       # 2 attempts x 2 orders
    assert main(["combine", "--project-out", str(out)]) == 0
    view = read(out / "check" / "check_manifest.json")["views"][CAM]
    assert view["sweep:a3"]["preference"]["preferred"] and view["sweep:a3"]["preference_only"]
    assert not view["sweep:a4"]["preference"]["preferred"] and view["sweep:a4"]["preference"]["votes"] == 0
    report = (out / "check" / "check_report.md").read_text(encoding="utf-8")
    assert "## Realism preference (info only)" in report and "sweep:a3" in report


def test_the_default_client_factory_sends_images_labels_and_the_strict_schema(tmp_path, monkeypatch):
    """The real VLMClient (vlm_client.post_json stubbed): two images with labels, schema without $schema."""
    from wenart.recognition import vlm_client
    out = T.write_toy_project(tmp_path)
    assert main(["plan-crops", "--project-out", str(out)]) == 0
    assert main(["expected", "--project-out", str(out)]) == 0
    bodies = []

    def fake_post(url, body, timeout_s):
        bodies.append((url, body))
        schema = body["structured_outputs"]["json"]
        labels = schema["properties"]["elements"]["required"]
        data = {"elements": {l: {"status": "present", "seen_as": "nothing", "confidence": 0.5} for l in labels},
                "extras": [], "door_count": 1, "window_count": 1}
        return {"choices": [{"message": {"content": json.dumps(data)}}], "usage": {"prompt_tokens": 10}}

    monkeypatch.setattr(vlm_client, "post_json", fake_post)
    assert main(["run", "--project-out", str(out), "--model-key", "glm", "--server", "http://127.0.0.1:8001/v1",
                 "--kinds", "cycles,plan_ab"]) == 0
    assert len(bodies) == 2
    url, body = next(b for b in bodies if len(b[1]["messages"][1]["content"]) == 5)
    assert url == "http://127.0.0.1:8001/v1/chat/completions" and body["model"] == "zai-org/GLM-4.6V-Flash"
    content = body["messages"][1]["content"]
    assert [c["type"] for c in content] == ["text", "image_url", "text", "image_url", "text"]
    assert content[0]["text"].startswith("Image 1") and content[2]["text"].startswith("Image 2 (source floor plan")
    assert "$schema" not in body["structured_outputs"]["json"] and body["temperature"] == 0
    assert body["chat_template_kwargs"] == {"enable_thinking": False}
    # "present" with seen_as "nothing" is inconsistent: valid JSON, normalised to unsure by combine.
    assert main(["run", "--project-out", str(out), "--model-key", "qwen", "--server", "http://127.0.0.1:8001/v1"]) == 0
    assert main(["combine", "--project-out", str(out)]) == 0
    sofa = read(out / "check" / "check_manifest.json")["views"][CAM]["cycles"]["elements"]["f_sofa"]
    assert sofa["passes"]["glm"]["status"] == "unsure" and sofa["passes"]["glm"]["normalised"]


# --------------------------------------------------------------------------
# Style photo
# --------------------------------------------------------------------------

def test_style_photo_pass_appends_and_resumes(tmp_path, monkeypatch):
    out = T.write_toy_project(tmp_path)
    seen = []
    fake = types.ModuleType("wenart.style.photos")

    def read_style_photo(path, clients):
        seen.append((Path(path).name, sorted(clients)))
        key = next(iter(clients))
        return {"passes": {key: {"model": clients[key].model, "data": {"walls": "plaster_charcoal"}}}}

    fake.read_style_photo = read_style_photo
    monkeypatch.setitem(sys.modules, "wenart.style.photos", fake)
    photo = Path(__file__).resolve().parent / "fixtures" / "style_photo_synthetic-03_salon.jpg"
    target = out / "check" / "style_photo_test"
    f = factory_for({})
    for key in ("qwen", "glm", "qwen"):
        assert main(["style-photo", "--project-out", str(out), "--model-key", key, "--photo", str(photo),
                     "--out", str(target)], client_factory=f) == 0
    data = read(out / "check" / "style_photo_test.json")
    assert data["kind"] == "style_photo_passes" and [c["model_key"] for c in data["calls"]] == ["qwen", "glm"]
    assert data["calls"][0]["result"]["passes"]["qwen"]["data"]["walls"] == "plaster_charcoal"
    assert seen == [(photo.name, ["qwen"]), (photo.name, ["glm"])]                  # the third run reused qwen's


def test_style_photo_without_the_photos_module_records_the_error(tmp_path, monkeypatch):
    out = T.write_toy_project(tmp_path)
    monkeypatch.setitem(sys.modules, "wenart.style.photos", None)              # import fails
    photo = Path(__file__).resolve().parent / "fixtures" / "style_photo_synthetic-03_salon.jpg"
    assert main(["style-photo", "--project-out", str(out), "--model-key", "qwen", "--photo", str(photo)],
                client_factory=factory_for({})) == 0
    data = read(out / "check" / "style_photos.json")
    assert data["calls"][0]["result"] is None and "wenart.style.photos" in data["calls"][0]["error"]
