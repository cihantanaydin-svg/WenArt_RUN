"""The full-run scheduler with a fake runner, a fake clock and fake servers (docs/milestone6.md §2.3, §9).

The fake runner (``FakeCLI``) records every command and writes what the real
CLI would write (building, style, scene and render manifests, answers files,
...), so the orchestrator's decisions are checked without Blender, a GPU or a
model: phase order, server sessions only when needed (2/3/4 starts),
needs_review and deadline handling, reuse by fingerprint, statuses, the A/B
steps, the smoke profile, the private plumbing and the exit code.
"""
from __future__ import annotations

import hashlib
import json
import os
from contextlib import contextmanager
from pathlib import Path

import pytest
import yaml

from wenart.run import scheduler as SC
from wenart.run import servers as SV
from wenart.run import stages as S
from wenart.run import state as ST

MODELS = {
    "qwen": {"id": "Qwen/Qwen3-VL-8B-Instruct", "revision": "rev-q", "slug": "qwen3-vl-8b", "server_flags": ""},
    "glm": {"id": "zai-org/GLM-4.6V-Flash", "revision": "rev-g", "slug": "glm-4.6v-flash",
            "server_flags": "--reasoning-parser glm45"},
}
SECONDS = {"pipeline": 5, "build": 30, "render": 100, "control renders": 20, "gate calibrate": 120,
           "polish": 200, "check run": 60, "layout": 40, "realism": 50, "pytest": 30}


def opt(cmd, name, default=None):
    return cmd[cmd.index(name) + 1] if name in cmd else default


def write(path, data) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, (dict, list)):
        path.write_text(json.dumps(data, indent=1), encoding="utf-8")
    elif isinstance(data, bytes):
        path.write_bytes(data)
    else:
        path.write_text(str(data), encoding="utf-8")
    return path


def room(rid, rtype, area, documented):
    return {"id": rid, "label": rid, "level_id": "L0", "room_type": rtype, "area_computed": area,
            "has_documented_furniture": documented, "polygon": [[0, 0], [4, 0], [4, 3], [0, 3]]}


def views_of(building) -> list:
    cams = []
    for r in building.get("rooms") or []:
        a = r["area_computed"]
        n = 3 if a >= 6 else 2 if a >= 3 else 1
        cams += [f"cam_{r['id']}_{i}" for i in range(1, n + 1)]
    return cams


class FakeClock:
    def __init__(self, t: float = 1_000_000.0):
        self.t = float(t)

    def __call__(self) -> float:
        return self.t

    def advance(self, s: float) -> None:
        self.t += float(s)


class FakeCLI:
    """The one runner, faked: records the call, writes the CLI's outputs, advances the clock, returns rc."""

    def __init__(self, clock: FakeClock, buildings=None, rc=None, seconds=None, flags=None):
        self.clock = clock
        self.calls: list[dict] = []
        self.buildings = buildings or {}     # project -> {"status", "rooms", "brief"}
        self.rc = rc or {}                   # name or (name, project) -> rc
        self.seconds = dict(SECONDS, **(seconds or {}))
        self.flags = flags or {}             # see the handlers

    @staticmethod
    def name_of(cmd) -> str:
        if cmd[0] == "nvidia-smi":
            return "nvidia-smi"
        mod = cmd[2] if len(cmd) > 2 and cmd[1] == "-m" else cmd[0]
        sub = cmd[3] if len(cmd) > 3 else ""
        if mod == "wenart.ingest.pipeline":
            return "pipeline"
        if mod == "wenart.style.photos":
            return f"photos {sub}"
        if mod == "wenart.style":
            return "style"
        if mod == "wenart.assets":
            return "assets"
        if mod == "wenart.furniture.fit":
            return "refit" if cmd[3].endswith("building_decor.json") else "fit"
        if mod == "wenart.furniture.layout":
            return "layout"
        if mod == "wenart.furniture.decor":
            return "decor"
        if mod == "wenart.blender.cli":
            if sub == "build":
                return "build"
            return "control renders" if "--hide-sets" in cmd else "render"
        if mod == "wenart.gate":
            return f"gate {sub}"
        if mod == "wenart.polish":
            return "polish"
        if mod == "wenart.vision_check":
            return {"run": "check run"}.get(sub, sub)
        if mod == "wenart.report":
            return "report"
        if mod == "wenart.run":
            return sub
        if mod == "wenart.intake":
            return "intake"
        if mod == "pytest":
            return "pytest"
        return mod

    @staticmethod
    def project_of(cmd) -> str:
        for flag in ("--project-out",):
            if flag in cmd:
                return Path(opt(cmd, flag)).name
        mod = cmd[2] if len(cmd) > 2 else ""
        if mod == "wenart.ingest.pipeline":
            return Path(opt(cmd, "--out")).name
        if mod == "wenart.intake":
            return cmd[4]
        if mod == "wenart.blender.cli":
            path = Path(opt(cmd, "--out"))
            while path.name in ("scene", "renders", "controls", "ab", "ctl_flat", "ctl_proxy", "ctl_direct",
                                "ctl_lowspp", "nuisance_ev"):
                path = path.parent
            return path.name
        if mod in ("wenart.furniture.fit", "wenart.furniture.layout", "wenart.furniture.decor"):
            return Path(cmd[3]).parent.name
        if mod in ("wenart.style", "wenart.assets", "wenart.style.photos"):
            return Path(opt(cmd, "--out") or opt(cmd, "--style")).parent.name.replace("style_photos", "") or \
                Path(opt(cmd, "--out")).parent.parent.name
        return ""

    def rc_for(self, name, project) -> int:
        value = self.rc.get((name, project), self.rc.get(name, 0))
        return value(self) if callable(value) else int(value)

    def __call__(self, cmd, env, cwd, timeout, log_path) -> int:
        name = self.name_of(cmd)
        project = self.project_of(cmd)
        self.calls.append({"name": name, "project": project, "cmd": list(cmd), "env": dict(env), "timeout": timeout,
                           "log": str(log_path), "t": self.clock(), "cwd": str(cwd)})
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write("$ " + " ".join(cmd) + "\n")
        handler = getattr(self, "h_" + name.replace(" ", "_").replace("-", "_"), None)
        rc = handler(cmd, project, log_path) if handler else 0
        if rc is None:
            rc = 0
        forced = self.rc_for(name, project)
        self.clock.advance(self.seconds.get(name, 1.0))
        return forced if forced else rc

    # ----- handlers ----------------------------------------------------------

    def h_intake(self, cmd, project, log):
        out = Path(opt(cmd, "--out"))
        status = self.flags.get("intake", {}).get(project, "ok")
        out.mkdir(parents=True, exist_ok=True)
        write(out / "plan.dxf", "x")
        manifest = {"status": status, "reasons": ["document name collision"] if status != "ok" else []}
        write(out.parent.parent / "intake_manifest.json", manifest)
        return 0 if status == "ok" else 1

    def h_pipeline(self, cmd, project, log):
        out = Path(opt(cmd, "--out"))
        spec = self.buildings.get(project, {})
        status = spec.get("status", "ok")
        rooms = spec.get("rooms", [room("r1", "living", 20.0, True), room("r2", "bedroom", 12.0, False)])
        building = {"project": {"id": project, "brief": spec.get("brief", {})}, "status": status,
                    "levels": [{"id": "L0"}], "rooms": rooms if status == "ok" else [], "furniture": []}
        write(out / "building.json", building)
        write(out / "report.md", "# report\n")
        return 0 if status == "ok" else 1

    def h_photos_read(self, cmd, project, log):
        key = opt(cmd, "--model-key")
        out = Path(opt(cmd, "--out"))
        photos = cmd[4:cmd.index("--model-key")]
        data = json.loads(out.read_text()) if out.is_file() else {"calls": []}
        fail = key in self.flags.get("photo_fail", {}).get(project, ())
        for p in photos:
            sha = hashlib.sha256(Path(p).read_bytes()).hexdigest()
            passes = [{"model_key": key, "model": MODELS[key]["id"], "data": None if fail else {"floor": "x"},
                       "error": "boom" if fail else None}]
            data["calls"] = [c for c in data["calls"] if not (c["file"] == p and c["model_key"] == key)]
            data["calls"].append({"file": p, "sha256": sha, "model_key": key, "model": MODELS[key]["id"],
                                  "result": {"passes": passes}, "error": "boom" if fail else None})
        write(out, data)

    def h_photos_combine(self, cmd, project, log):
        write(opt(cmd, "--out"), {"terms": []})

    def h_style(self, cmd, project, log):
        write(opt(cmd, "--out"), {"photo_terms": opt(cmd, "--photo-terms")})

    def h_fit(self, cmd, project, log):
        write(opt(cmd, "--out"), json.loads(Path(cmd[3]).read_text()))

    h_refit = h_fit

    def h_decor(self, cmd, project, log):
        write(opt(cmd, "--out"), json.loads(Path(cmd[3]).read_text()))

    def h_layout(self, cmd, project, log):
        b = json.loads(Path(cmd[3]).read_text())
        empty = [r for r in b["rooms"] if not r["has_documented_furniture"]]
        b["furniture"] = b["furniture"] + [{"id": "f_ai", "room_id": empty[0]["id"], "source": "added_by_ai"}]
        write(opt(cmd, "--out"), b)
        write(Path(opt(cmd, "--out")).parent / "layout.json", {"rooms": []})

    def h_build(self, cmd, project, log):
        out = Path(opt(cmd, "--out"))
        rc = self.rc_for("build", project)
        if rc:
            write(out / "build.log", "blender started\nerror: the building refused the request\n")
            return rc
        b = json.loads(Path(opt(cmd, "--building")).read_text())
        cams = [{"name": c, "position": [1.0, 1.0, 1.25], "target": [2.0, 1.0, 1.25]} for c in views_of(b)]
        if "ab" in out.parts:
            cams = [{"name": c, "position": [1.0, 1.0, 1.4], "target": [2.0, 1.0, 1.3]}
                    for c in ("cam_a_1", "cam_a_2", "cam_b_1")]
        write(out / "scene.blend", b"blend")
        write(out / "scene_manifest.json", {"cameras": cams})
        write(out / "build.log", "ok\n")

    def h_render(self, cmd, project, log):
        out = Path(opt(cmd, "--out"))
        scene = json.loads((Path(opt(cmd, "--scene")).parent / "scene_manifest.json").read_text())
        cams = [c["name"] for c in scene["cameras"]]
        if opt(cmd, "--cameras", "all") != "all":
            cams = opt(cmd, "--cameras").split(",")
        cut = project in self.flags.get("render_cut", ())
        if cut:
            cams = cams[:1]
        write(out / "render_manifest.json", {"renders": [{"camera": c, "preview": f"{c}_preview.jpg"} for c in cams],
                                             "incomplete": cut})
        return 3 if cut else 0

    def h_control_renders(self, cmd, project, log):
        for entry in opt(cmd, "--hide-sets").split(";"):
            write(Path(opt(cmd, "--out")) / f"hide_{entry.split(':')[1].split('+')[0]}" / "render_manifest.json",
                  {"renders": []})

    def h_select_controls(self, cmd, project, log):
        write(Path(opt(cmd, "--project-out")) / "check" / "controls.json",
              {"hide_sets": self.flags.get("hide_sets", "cam_r1_1:f1;cam_r1_2:w1+plug;cam_r2_1:f2")})

    def h_gate_calibrate(self, cmd, project, log):
        write(Path(opt(cmd, "--project-out")) / "gate" / "gate_calibration.json",
              {"incomplete": project in self.flags.get("gate_cut", ())})

    def h_gate_validate(self, cmd, project, log):
        decision = self.flags.get("gate_decision", {}).get(project, "ok")
        write(Path(opt(cmd, "--project-out")) / "gate" / "gate_validation.json", {"decision": decision})

    def h_polish(self, cmd, project, log):
        write(Path(opt(cmd, "--project-out")) / "polish" / "polish_manifest.json",
              {"incomplete": project in self.flags.get("polish_cut", ())})

    def h_expected(self, cmd, project, log):
        write(Path(opt(cmd, "--project-out")) / "check" / "expected_views.json", {"views": {}})

    def _answers(self, cmd, project, sub=""):
        key = opt(cmd, "--model-key")
        path = Path(opt(cmd, "--project-out")) / "check" / sub / f"answers_{MODELS[key]['slug']}.json"
        cut = (project, key) in self.flags.get("answers_cut", ())
        write(path, {"incomplete": cut, "sets": opt(cmd, "--sets")})

    def h_check_run(self, cmd, project, log):
        self._answers(cmd, project)

    def h_preference(self, cmd, project, log):
        self._answers(cmd, project)

    def h_style_photo(self, cmd, project, log):
        write(opt(cmd, "--out"), {"calls": [], "incomplete": False})

    def h_combine(self, cmd, project, log):
        write(Path(opt(cmd, "--project-out")) / "check" / "check_manifest.json", {"views": {}})

    def h_report(self, cmd, project, log):
        out = Path(opt(cmd, "--project-out")) / "final"
        write(out / "final_report.md", "# final\n")
        write(out / "final_manifest.json", {"status": "ok"})

    def h_ab_m5(self, cmd, project, log):
        out = Path(opt(cmd, "--project-out"))
        cams = [{"name": c, "position": [1.0, 1.0, 1.4], "target": [2.0, 1.0, 1.3]}
                for c in ("cam_a_1", "cam_a_2", "cam_b_1")]
        write(out / "ab" / "m5" / "scene_manifest.json", {"cameras": cams})
        write(out / "ab" / "m5" / "render_manifest.json", {"renders": []})
        b = {"project": {"id": project}, "status": "ok", "rooms": [], "furniture": []}
        write(out / "ab" / "m5" / "building_final.json", b)
        write(out / "ab" / "building_m5.json", b)

    def h_realism_pairs(self, cmd, project, log):
        pairs = [{"pair_id": f"m5_vs_m6:c{i}", "set": "m5_vs_m6"} for i in range(3)]
        pairs += [{"pair_id": f"look_alt:c{i}", "set": "look_alt"} for i in range(3)]
        if "--controls" in cmd:
            pairs += [{"pair_id": f"{s}:c{i}", "set": s} for s in ("ctl_flat", "null_identical") for i in range(2)]
        write(Path(opt(cmd, "--project-out")) / "ab" / "pairs.json", {"pairs": pairs, "dropped": []})

    def h_realism(self, cmd, project, log):
        self._answers(cmd, project, "realism")

    def h_realism_combine(self, cmd, project, log):
        write(Path(opt(cmd, "--project-out")) / "check" / "realism" / "realism_ab.json", {})

    def h_realism_summary(self, cmd, project, log):
        write(Path(opt(cmd, "--out")) / "realism_summary.json", {})

    def h_nvidia_smi(self, cmd, project, log):
        with open(log, "a") as fh:
            fh.write("32607\n")

    # ----- queries -------------------------------------------------------------

    def names(self, project=None) -> list:
        return [c["name"] for c in self.calls if project is None or c["project"] == project]

    def find(self, name, project=None) -> list:
        return [c for c in self.calls if c["name"] == name and (project is None or c["project"] == project)]


class FakeServers:
    """The server factory: records each start, advances the clock by the start time, can fail."""

    def __init__(self, clock: FakeClock, start_s=None, fail=None):
        self.clock = clock
        self.start_s = start_s or {"qwen": 300.0, "glm": 150.0}
        self.fail = fail or {}            # key -> ServerError reason
        self.starts: list[str] = []
        self.open = 0

    def __call__(self, key, deadline, stats):
        @contextmanager
        def cm():
            self.starts.append(key)
            self.clock.advance(self.start_s[key])
            if key in self.fail:
                stats.append({"key": key, "ok": False})
                raise SV.ServerError(key, self.fail[key], "fake failure")
            stats.append({"key": key, "ok": True, "seconds_to_ready": self.start_s[key]})
            self.open += 1
            try:
                yield f"http://fake-{key}/v1"
            finally:
                self.open -= 1
        return cm()


def make_repo(tmp_path, projects: dict) -> Path:
    repo = tmp_path / "repo"
    for name, spec in projects.items():
        d = repo / "projects" / name
        d.mkdir(parents=True)
        (d / "plan.dxf").write_text(name, encoding="utf-8")
        if spec.get("brief") is not None:
            (d / "brief.yaml").write_text(yaml.safe_dump(spec["brief"]), encoding="utf-8")
        for photo in spec.get("photos", []):
            write(d / "style_photos" / photo, photo.encode())
    return repo


class Run:
    def __init__(self, tmp_path, spec=None, buildings=None, rc=None, seconds=None, flags=None,
                 start_s=None, fail=None, deadline_in=None, clock=None, **opts):
        self.tmp = tmp_path
        self.repo = tmp_path / "repo" if (tmp_path / "repo").is_dir() else make_repo(tmp_path, spec or {})
        self.clock = clock or FakeClock()
        self.cli = FakeCLI(self.clock, buildings, rc, seconds, flags)
        self.servers = FakeServers(self.clock, start_s, fail)
        self.lines: list[str] = []
        deadline = None if deadline_in is None else self.clock() + deadline_in
        self.opts = SC.RunOptions(results=tmp_path / "results", repo_root=self.repo, outputs=tmp_path / "outputs",
                                  job_dir=tmp_path / "job", private_root=tmp_path / "pp",
                                  private_outputs=tmp_path / "po", private_results=tmp_path / "pr",
                                  assets=tmp_path / "assets", py="PY", polish_py="POLISH_PY",
                                  logs_dir=tmp_path / "logs", deadline=deadline, **opts)
        self.orch = None
        self.rc = None

    def run(self, **kw) -> int:
        self.orch = SC.Orchestrator(self.opts, runner=self.cli, clock=self.clock, server_factory=self.servers,
                                    out=self.lines.append,
                                    control_views=lambda r, s, n: [c["name"] for c in s["cameras"]][:n],
                                    gpu_mem=lambda: 32607, check_models=MODELS, **kw)
        self.rc = self.orch.run()
        return self.rc

    def record(self, project, stage, root="outputs") -> dict:
        return json.loads((self.tmp / root / project / "run" / f"{stage}.json").read_text())

    def manifest(self) -> dict:
        return json.loads((self.tmp / "results" / "run_manifest.json").read_text())

    def stages(self, project) -> dict:
        entry = next(p for p in self.manifest()["projects"] if p["name"] == project)
        return {s["stage"]: s for s in entry["stages"]}


def first(names, prefix):
    return next(i for i, n in enumerate(names) if n.startswith(prefix))


# --------------------------------------------------------------------------
# Phase order and server sessions
# --------------------------------------------------------------------------

def test_phase_order_and_three_server_starts_without_photos(tmp_path):
    r = Run(tmp_path, {"p1": {}, "p2": {}}, projects=["p1", "p2"])
    assert r.run() == 0
    names = r.cli.names()
    order = ["pipeline", "fit", "style", "layout", "assets", "decor", "refit", "build", "render", "select-controls",
             "control renders", "gate calibrate", "gate validate", "polish", "expected", "plan-crops", "check run",
             "preference", "style-photo", "combine", "calibrate", "report", "pytest"]
    idx = [first(names, n) for n in order]
    assert idx == sorted(idx), names
    # Every project's stage of a phase before the next phase starts.
    assert max(i for i, c in enumerate(r.cli.calls) if c["name"] == "fit") < first(names, "layout")
    assert max(i for i, c in enumerate(r.cli.calls) if c["name"] == "layout") < first(names, "assets")
    assert max(i for i, c in enumerate(r.cli.calls) if c["name"] == "control renders") < first(names, "gate")
    assert r.servers.starts == ["qwen", "qwen", "glm"]
    # Check and preference with the server's sequences (32 GB here: 2) and the session's URL.
    run_calls = r.cli.find("check run")
    assert [opt(c["cmd"], "--model-key") for c in run_calls] == ["qwen", "qwen", "glm", "glm"]
    assert all(opt(c["cmd"], "--workers") == "2" and opt(c["cmd"], "--server").startswith("http://fake-")
               for c in run_calls)
    assert [p["state"] for p in r.manifest()["projects"]] == ["ok", "ok"]
    assert [ph["phase"] for ph in r.manifest()["phases"]] == list(range(1, 12))


def test_four_starts_with_uncached_photos_and_two_without_empty_rooms(tmp_path):
    rooms_full = [room("r1", "living", 20.0, True), room("r2", "bedroom", 12.0, True)]
    r = Run(tmp_path, {"p1": {"photos": ["a.jpg"], "brief": {"style": "x"}}}, projects=["p1"])
    assert r.run() == 0
    assert r.servers.starts == ["glm", "qwen", "qwen", "glm"]
    reads = r.cli.find("photos read")
    assert [opt(c["cmd"], "--model-key") for c in reads] == ["glm", "qwen"]
    # The terms reach the style before the layout (phase 3) and the build.
    styles = r.cli.find("style")
    assert opt(styles[0]["cmd"], "--photo-terms") is None and opt(styles[-1]["cmd"], "--photo-terms")
    assert r.cli.calls.index(styles[-1]) < r.cli.calls.index(r.cli.find("layout")[0])
    assert r.record("p1", "photos")["status"] == "ok"

    tmp2 = tmp_path / "second"
    tmp2.mkdir()
    r2 = Run(tmp2, {"p1": {}}, buildings={"p1": {"rooms": rooms_full}}, projects=["p1"])
    assert r2.run() == 0
    assert r2.servers.starts == ["qwen", "glm"]
    assert r2.record("p1", "layout")["status"] == "skipped" and r2.record("p1", "layout")["note"] == "no empty room"
    assert r2.record("p1", "photos")["note"] == "no style photos"
    assert opt(r2.cli.find("decor")[0]["cmd"], "--out").endswith("building_decor.json")
    assert r2.cli.find("decor")[0]["cmd"][3].endswith("building_fitted.json")


def test_photo_terms_reused_on_resume_without_a_server(tmp_path):
    r = Run(tmp_path, {"p1": {"photos": ["a.jpg", "b.jpg"]}}, projects=["p1"])
    assert r.run() == 0
    first_starts = list(r.servers.starts)
    assert first_starts == ["glm", "qwen", "qwen", "glm"]
    r2 = Run(tmp_path, projects=["p1"])          # same volume, same repo: a resumed pod
    assert r2.run() == 0
    assert r2.servers.starts == ["qwen", "glm"]  # layout reused, photos reused: only the check sessions
    assert not r2.cli.find("photos read")
    styles = r2.cli.find("style")
    assert len(styles) == 1 and opt(styles[0]["cmd"], "--photo-terms")      # the first style has the terms
    assert r2.record("p1", "photos")["status"] == "reused"
    assert r2.record("p1", "layout")["status"] == "reused"
    assert r2.record("p1", "pipeline")["status"] == "reused" and r2.record("p1", "fit")["status"] == "reused"


def test_photo_answers_missing_give_a_warning_and_the_brief_style(tmp_path):
    r = Run(tmp_path, {"p1": {"photos": ["a.jpg"]}}, projects=["p1"], flags={"photo_fail": {"p1": ("glm",)}})
    assert r.run() == 0
    rec = r.record("p1", "photos")
    assert rec["status"] == "warning" and "glm 1" in rec["note"] and "brief only" in rec["note"]
    assert all(opt(c["cmd"], "--photo-terms") is None for c in r.cli.find("style"))
    assert r.manifest()["projects"][0]["state"] == "ok"


def test_photos_forced_ask_again(tmp_path):
    r = Run(tmp_path, {"p1": {"photos": ["a.jpg"]}}, projects=["p1"])
    r.run()
    r2 = Run(tmp_path, projects=["p1"], force=frozenset({"photos"}))
    assert r2.run() == 0
    assert [opt(c["cmd"], "--model-key") for c in r2.cli.find("photos read")] == ["glm", "qwen"]


def test_ab_judge_phase_starts_two_servers(tmp_path):
    r = Run(tmp_path, {"p1": {}}, ab=["p1"], ab_controls="p1", ab_phase="render")
    assert r.run() == 0
    assert r.servers.starts == []
    r2 = Run(tmp_path, ab=["p1"], ab_controls="p1", ab_phase="judge")
    assert r2.run() == 0
    assert r2.servers.starts == ["qwen", "glm"]
    assert not r2.cli.find("build") and not r2.cli.find("render") and not r2.cli.find("pipeline")
    assert r2.record("p1", "ab_prepare")["note"] == "not in this phase"


# --------------------------------------------------------------------------
# needs_review, failures, statuses
# --------------------------------------------------------------------------

def test_needs_review_stops_the_project_and_starts_no_server(tmp_path):
    r = Run(tmp_path, {"p2": {}}, buildings={"p2": {"status": "needs_review"}}, projects=["p2"])
    assert r.run() == 0                       # needs_review is a result, not a failure
    assert r.servers.starts == []
    assert r.cli.names("p2") == ["pipeline", "report"]
    assert r.record("p2", "pipeline")["status"] == "needs_review"
    assert r.manifest()["projects"][0]["state"] == "needs_review"
    lists = r.manifest()["test_lists"]
    assert lists["NEEDS_REVIEW_TEST_PROJECTS"] == "p2" and lists["RUN_TEST_PROJECTS"] == ""
    # With an ok project the server count is the ok project's.
    tmp2 = tmp_path / "b"
    tmp2.mkdir()
    r2 = Run(tmp2, {"p1": {}, "p2": {}}, buildings={"p2": {"status": "needs_review"}}, projects=["p1", "p2"])
    assert r2.run() == 0
    assert r2.servers.starts == ["qwen", "qwen", "glm"]
    assert r2.cli.names("p2") == ["pipeline", "report"]


def test_build_exit_2_is_failed_with_the_last_build_log_line(tmp_path):
    r = Run(tmp_path, {"p1": {}}, rc={"build": 2}, projects=["p1"])
    assert r.run() == 1
    rec = r.record("p1", "build")
    assert rec["status"] == "failed" and rec["rc"] == 2
    assert rec["note"] == "exit 2: error: the building refused the request"
    assert "render" not in r.cli.names("p1") and "report" in r.cli.names("p1")
    assert r.manifest()["projects"][0]["state"] == "failed"


def test_warnings_and_skips_keep_the_project_ok(tmp_path):
    r = Run(tmp_path, {"p1": {"brief": {"polish": False}}}, rc={"assets": 1, "control renders": 1},
            projects=["p1"])
    assert r.run() == 0
    assert r.record("p1", "assets")["status"] == "warning"
    assert r.record("p1", "controls")["status"] == "warning"
    assert r.record("p1", "gate")["note"] == "polish off" and r.record("p1", "polish")["note"] == "polish off"
    assert r.record("p1", "intake")["note"] == "private only"
    assert not r.cli.find("gate calibrate") and not r.cli.find("polish")
    assert r.manifest()["projects"][0]["state"] == "ok"


def test_gate_before_polish_and_the_decision_decides(tmp_path):
    r = Run(tmp_path, {"p1": {}, "p2": {}, "p3": {}}, projects=["p1", "p2", "p3"],
            flags={"gate_decision": {"p1": "flagged", "p2": "polish_disabled", "p3": "not_validated"}})
    assert r.run() == 0
    for p in ("p1", "p2", "p3"):
        names = r.cli.names(p)
        assert names.index("gate calibrate") < names.index("gate validate")
        assert all(c["env"]["PYTORCH_CUDA_ALLOC_CONF"] == "expandable_segments:True"
                   for c in r.cli.find("gate calibrate", p))
        assert r.cli.find("gate calibrate", p)[0]["cmd"][0] == "POLISH_PY"
        assert r.cli.find("gate validate", p)[0]["cmd"][0] == "PY"
    assert r.cli.names("p1").index("gate validate") < r.cli.names("p1").index("polish")
    assert r.cli.find("polish", "p1")[0]["env"]["PYTORCH_CUDA_ALLOC_CONF"] == "expandable_segments:True"
    assert not r.cli.find("polish", "p2") and not r.cli.find("polish", "p3")
    assert r.record("p2", "polish")["note"] == "gate not validated"
    assert r.record("p1", "gate")["note"] == "gate decision flagged"
    lists = r.manifest()["test_lists"]
    assert lists["POLISH_TEST_PROJECTS"] == "p1" and lists["GATE_TEST_PROJECTS"] == "p1 p2 p3"


def test_failed_gate_steps_never_allow_the_polish(tmp_path):
    """A stale gate_validation.json (decision ok) must not let a project polish when this run's calibration or
    validation failed."""
    for p in ("p1", "p2"):
        write(tmp_path / "outputs" / p / "gate" / "gate_validation.json", {"decision": "ok"})
    r = Run(tmp_path, {"p1": {}, "p2": {}}, projects=["p1", "p2"],
            rc={("gate calibrate", "p1"): 1, ("gate validate", "p2"): 1})
    assert r.run() == 0                       # warnings: the views keep Cycles, reported
    assert not r.cli.find("gate validate", "p1") and not r.cli.find("polish")
    assert r.record("p1", "gate")["status"] == "warning" and "not_validated" in r.record("p1", "gate")["note"]
    assert r.record("p2", "gate")["note"] == "gate decision not_validated (validate exit 1)"
    assert r.record("p1", "polish")["note"] == r.record("p2", "polish")["note"] == "gate not validated"
    assert r.manifest()["test_lists"]["GATE_TEST_PROJECTS"] == "p1 p2"


@pytest.mark.parametrize("flag, stage", [("render_cut", "render"), ("gate_cut", "gate"), ("polish_cut", "polish")])
def test_incomplete_from_the_output_files(tmp_path, flag, stage):
    r = Run(tmp_path, {"p1": {}}, projects=["p1"], flags={flag: ("p1",)})
    assert r.run() == 1
    assert r.record("p1", stage)["status"] == "incomplete"
    assert r.manifest()["projects"][0]["state"] == "incomplete"
    assert "report" in r.cli.names("p1")                 # phase 10 still runs


def test_check_answers_incomplete_and_polish_rc_1_warning(tmp_path):
    r = Run(tmp_path, {"p1": {}}, projects=["p1"], rc={"polish": 1}, flags={"answers_cut": {("p1", "glm")}})
    assert r.run() == 1
    assert r.record("p1", "polish")["status"] == "warning"
    rec = r.record("p1", "check")
    assert rec["status"] == "incomplete" and "glm" in rec["note"]
    assert [s["name"] for s in rec["steps"]] == ["run qwen", "preference qwen", "style-photo test qwen",
                                                 "run glm", "preference glm", "style-photo test glm"]


def test_failed_layout_is_never_reused(tmp_path):
    r = Run(tmp_path, {"p1": {}}, projects=["p1"], rc={"layout": 3})
    assert r.run() == 1
    rec = r.record("p1", "layout")
    assert rec["status"] == "failed" and "exit 3" in rec["note"]
    assert "build" not in r.cli.names("p1")
    r2 = Run(tmp_path, projects=["p1"])
    assert r2.run() == 0
    assert len(r2.cli.find("layout")) == 1 and r2.record("p1", "layout")["status"] == "ok"
    assert r2.servers.starts == ["qwen", "qwen", "glm"]


def test_fingerprint_reuse_outputs_missing_and_force(tmp_path):
    r = Run(tmp_path, {"p1": {}}, projects=["p1"])
    r.run()
    r2 = Run(tmp_path, projects=["p1"])
    r2.run()
    for stage in ("pipeline", "fit", "layout", "decor", "refit"):
        assert r2.record("p1", stage)["status"] == "reused", stage
    assert not {"pipeline", "fit", "layout", "decor", "refit"} & set(r2.cli.names())
    assert "build" in r2.cli.names() and "render" in r2.cli.names()    # own reuse: always invoked
    # A missing output -> run again; a third run reuses the reused record.
    (tmp_path / "outputs" / "p1" / "building_decor.json").unlink()
    r3 = Run(tmp_path, projects=["p1"])
    r3.run()
    assert r3.record("p1", "decor")["status"] == "ok" and r3.record("p1", "fit")["status"] == "reused"
    # --force
    r4 = Run(tmp_path, projects=["p1"], force=frozenset({"fit", "render", "build", "polish"}))
    r4.run()
    assert r4.record("p1", "fit")["status"] == "ok" and r4.record("p1", "pipeline")["status"] == "reused"
    assert "--force" in r4.cli.find("render")[0]["cmd"] and "--force" in r4.cli.find("polish")[0]["cmd"]
    assert "--reuse" not in r4.cli.find("build")[0]["cmd"]
    # A changed project file changes the pipeline fingerprint.
    (tmp_path / "repo" / "projects" / "p1" / "plan.dxf").write_text("changed", encoding="utf-8")
    r5 = Run(tmp_path, projects=["p1"])
    r5.run()
    assert r5.record("p1", "pipeline")["status"] == "ok"


def test_records_hold_the_contract_fields(tmp_path):
    r = Run(tmp_path, {"p1": {}}, projects=["p1"])
    r.run()
    rec = r.record("p1", "layout")
    for key in ("schema_version", "kind", "project", "stage", "rc", "status", "seconds", "fingerprint", "inputs",
                "outputs", "started_utc", "git_commit", "log", "note"):
        assert key in rec, key
    assert rec["kind"] == "stage_record" and rec["outputs"] == ["building_furnished.json", "layout.json"]
    assert rec["log"] == "logs/layout.log" and len(rec["fingerprint"]) == 64
    assert set(rec["inputs"]) == {ST.file_hashes([tmp_path / "outputs/p1/building_fitted.json"]).popitem()[0],
                                  ST.file_hashes([tmp_path / "outputs/p1/style.json"]).popitem()[0]}
    assert rec["seconds"] == SECONDS["layout"]
    log = tmp_path / "outputs" / "p1" / "run" / "logs" / "layout.log"
    assert log.is_file() and "wenart.furniture.layout" in log.read_text()
    assert all(c["log"].endswith(f"run/logs/{c['log'].rsplit('/', 1)[1]}") for c in r.cli.calls if c["project"])


# --------------------------------------------------------------------------
# Deadline and timeouts
# --------------------------------------------------------------------------

def test_deadline_makes_heavy_stages_incomplete_and_phases_10_11_run(tmp_path):
    # pipeline 5 + fit 1 + style 1 + qwen start 300 + layout 40 + cpu ~4 + build 30 = ~381 s; render needs 8*5+60.
    r = Run(tmp_path, {"p1": {}}, projects=["p1"], deadline_in=420)
    assert r.run() == 1
    assert r.record("p1", "render")["status"] == "incomplete"
    assert r.record("p1", "render")["note"] == "deadline: render not started"
    names = r.cli.names("p1")
    assert "render" not in names and "gate calibrate" not in names and "check run" not in names
    assert "report" in names
    assert r.servers.starts == ["qwen"]
    # Phase 1-9 timeouts: max(60, deadline - now); phase 10: max(300, deadline + 600 - now).
    deadline = r.opts.deadline
    for c in r.cli.calls:
        if c["name"] == "report":
            assert c["timeout"] == max(300.0, deadline + 600 - c["t"])
        elif c["name"] == "pipeline":
            assert c["timeout"] == max(60.0, deadline - c["t"])


def test_no_server_start_after_the_deadline(tmp_path):
    r = Run(tmp_path, {"p1": {}}, projects=["p1"], deadline_in=100)
    assert r.run() == 1
    assert r.servers.starts == []
    rec = r.record("p1", "layout")
    assert rec["status"] == "incomplete" and "qwen server not started" in rec["note"]
    assert r.cli.find("report")


def test_timeout_rc_is_incomplete(tmp_path):
    r = Run(tmp_path, {"p1": {}}, projects=["p1"], rc={"expected": SC.TIMEOUT_RC})
    assert r.run() == 1
    assert r.record("p1", "expected")["status"] == "incomplete"


def test_wenart_deadline_reaches_every_subprocess(tmp_path):
    r = Run(tmp_path, {"p1": {}}, projects=["p1"], deadline_in=100_000)
    r.run()
    assert {c["env"]["WENART_DEADLINE"] for c in r.cli.calls} == {str(int(r.opts.deadline))}
    assert all(c["cwd"] == str(r.repo) for c in r.cli.calls)


def test_look_alt_only_when_the_glm_session_still_fits(tmp_path):
    big = Run(tmp_path, {"p1": {}}, ab=["p1"], ab_controls="p1", ab_phase="judge", deadline_in=100_000)
    big.cli.flags = {}
    # Prepare the A/B files with a render pod first.
    Run(tmp_path, ab=["p1"], ab_controls="p1", ab_phase="render").run()
    assert big.run() == 0
    sets = [opt(c["cmd"], "--sets") for c in big.cli.find("realism")]
    assert sets == ["ctl_flat,null_identical,m5_vs_m6", "look_alt", "ctl_flat,null_identical,m5_vs_m6", "look_alt"]
    # Tight deadline: Qwen's look_alt does not fit before the GLM session; GLM's own look_alt neither.
    # judge: pairs 1 s; Qwen start 300; main 14 calls (est 30.8 s, takes 50 s) -> t = 351; Qwen look_alt needs
    # 6 calls (13.2 s) + GLM start 150 + GLM main 30.8 -> 545 > deadline 540: skipped; GLM starts at 351 (501 < 540),
    # its main (est 531.8 < 540) runs to 551; its look_alt (564.2) is skipped.
    tmp2 = tmp_path / "tight"
    tmp2.mkdir()
    Run(tmp2, {"p1": {}}, ab=["p1"], ab_controls="p1", ab_phase="render").run()
    tight = Run(tmp2, ab=["p1"], ab_controls="p1", ab_phase="judge", deadline_in=540)
    assert tight.run() == 0                                  # look_alt is never counted
    sets = [opt(c["cmd"], "--sets") for c in tight.cli.find("realism")]
    assert sets == ["ctl_flat,null_identical,m5_vs_m6", "ctl_flat,null_identical,m5_vs_m6"]
    rec = tight.record("p1", "ab_look_alt")
    assert rec["status"] == "incomplete" and "not asked" in rec["note"]


# --------------------------------------------------------------------------
# A/B steps
# --------------------------------------------------------------------------

def test_ab_render_phase_commands(tmp_path):
    r = Run(tmp_path, {"p1": {}, "p3": {}}, projects=["p3"], ab=["p1", "p3"], ab_controls="p1", ab_phase="all")
    assert r.run() == 0
    # Part 1 only for the A/B project that is not in --projects.
    assert r.cli.names("p1")[:3] == ["pipeline", "style", "assets"]
    assert opt(r.cli.find("style", "p1")[0]["cmd"], "--photo-terms") is None
    assert r.cli.find("ab-m5", "p1")[0]["cmd"][:4] == ["PY", "-m", "wenart.run", "ab-m5"]
    assert opt(r.cli.find("ab-m5", "p1")[0]["cmd"], "--commit") == S.M5_LOOK_COMMIT
    builds = [c["cmd"] for c in r.cli.find("build", "p1")]
    assert [opt(b, "--out").rsplit("/", 2)[-2:] for b in builds] == [["ab", "scene"], ["ctl_flat", "scene"],
                                                                    ["ctl_proxy", "scene"]]
    assert all(opt(b, "--camera-policy") == "m5" and opt(b, "--building").endswith("ab/building_m5.json")
               for b in builds)
    assert "--no-textures" in builds[1] and "--proxies" in builds[2]
    renders = [c["cmd"] for c in r.cli.find("render", "p1")]
    ab_render = renders[0]
    assert opt(ab_render, "--alt-look") == "AgX - Punchy" and opt(ab_render, "--preview-quality") == "85"
    assert opt(ab_render, "--cameras") == "all"
    sets = {opt(c, "--out").rsplit("/", 2)[-2]: c for c in renders[1:]}
    assert list(sets) == ["ctl_flat", "ctl_proxy", "ctl_direct", "ctl_lowspp", "nuisance_ev"]
    for name, c in sets.items():
        assert opt(c, "--look-from").endswith("ab/renders/render_manifest.json")
        assert opt(c, "--preview-quality") == "85" and opt(c, "--cameras") == "cam_a_1,cam_a_2,cam_b_1"
    assert opt(sets["ctl_direct"], "--max-bounces") == "0" and opt(sets["ctl_lowspp"], "--samples") == "4"
    assert "--no-denoise" in sets["ctl_lowspp"] and opt(sets["nuisance_ev"], "--ev-offset") == "0.3"
    assert opt(sets["ctl_flat"], "--scene").endswith("ab/ctl_flat/scene/scene.blend")
    assert opt(sets["ctl_direct"], "--scene").endswith("ab/scene/scene.blend")
    # Camera check and pairs.
    check = json.loads((tmp_path / "outputs" / "p1" / "ab" / "cameras_check.json").read_text())
    assert check["kept"] == ["cam_a_1", "cam_a_2", "cam_b_1"] and check["dropped"] == []
    assert "--controls" in r.cli.find("realism-pairs", "p1")[0]["cmd"]
    assert "--controls" not in r.cli.find("realism-pairs", "p3")[0]["cmd"]
    assert not r.cli.find("ab_controls", "p3")
    summary = r.cli.find("realism-summary")[0]["cmd"]
    assert opt(summary, "--controls-project") == "p1" and opt(summary, "--out").endswith("results/realism")
    m = r.manifest()
    assert m["realism_summary"]["status"] == "ok" and m["test_lists"]["AB_TEST_PROJECTS"] == "p1 p3"
    ab = {a["name"]: a for a in m["ab"]}
    assert ab["p1"]["controls"] and {s["stage"] for s in ab["p1"]["stages"]} >= {"ab_m5", "ab_render", "ab_controls",
                                                                                   "ab_pairs", "ab_realism"}


def test_ab_stage_failure_fails_the_run_look_alt_does_not(tmp_path):
    r = Run(tmp_path, {"p1": {}}, ab=["p1"], ab_controls="p1", rc={"realism-pairs": 1})
    assert r.run() == 1
    assert r.record("p1", "ab_pairs")["status"] == "failed"
    tmp2 = tmp_path / "b"
    tmp2.mkdir()
    r2 = Run(tmp2, {"p1": {}}, ab=["p1"], ab_controls="p1",
             rc={"realism": lambda cli: 1 if opt(cli.calls[-1]["cmd"], "--sets") == "look_alt" else 0})
    assert r2.run() == 0
    assert r2.record("p1", "ab_look_alt")["status"] == "failed"


def test_ab_project_with_needs_review_is_dropped(tmp_path):
    r = Run(tmp_path, {"p2": {}}, buildings={"p2": {"status": "needs_review"}}, ab=["p2"])
    assert r.run() == 1
    rec = r.record("p2", "ab_prepare")
    assert rec["status"] == "failed" and "pipeline needs_review" in rec["note"]
    assert not r.cli.find("ab-m5")


# --------------------------------------------------------------------------
# Smoke profile
# --------------------------------------------------------------------------

def test_smoke_profile(tmp_path):
    r = Run(tmp_path, {"p1": {}}, projects=["p1"], ab=["p1"], ab_controls="p1", profile="smoke",
            vlm_url="http://127.0.0.1:9/v1")
    assert r.run() == 0
    render = r.cli.find("render", "p1")[0]["cmd"]
    assert opt(render, "--res") == "480x270" and opt(render, "--samples") == "16" and opt(render, "--device") == "cpu"
    controls = r.cli.find("control renders")[0]["cmd"]
    assert opt(controls, "--hide-sets") == "cam_r1_1:f1;cam_r1_2:w1+plug"           # 2 control views
    assert opt(controls, "--device") == "cpu" and opt(controls, "--res") == "480x270"
    assert r.record("p1", "gate")["note"] == "smoke profile" and r.record("p1", "polish")["note"] == "smoke profile"
    assert not r.cli.find("pytest") and not r.cli.find("gate calibrate")
    ab_renders = [c["cmd"] for c in r.cli.find("render", "p1")][1:]
    assert opt(ab_renders[0], "--cameras") == "cam_a_1,cam_a_2" and opt(ab_renders[0], "--device") == "cpu"
    assert all(opt(c, "--cameras") == "cam_a_1,cam_a_2" for c in ab_renders[1:])
    check = json.loads((tmp_path / "outputs" / "p1" / "ab" / "cameras_check.json").read_text())
    assert check["kept"] == ["cam_a_1", "cam_a_2"]
    assert check["dropped"] == [{"cam": "cam_b_1", "reason": "not rendered in the A/B render"}]


def test_smoke_profile_uses_the_external_server(tmp_path):
    r = Run(tmp_path, {"p1": {}}, projects=["p1"], profile="smoke", vlm_url="http://127.0.0.1:9/v1")
    r.opts.vlm_url = "http://127.0.0.1:9/v1"
    orch = SC.Orchestrator(r.opts, runner=r.cli, clock=r.clock, out=r.lines.append, check_models=MODELS)
    assert orch.run() == 0
    assert {opt(c["cmd"], "--server") for c in r.cli.find("check run")} == {"http://127.0.0.1:9/v1"}
    assert [s.get("external") for s in orch.servers] == [True, True, True]
    assert not r.cli.find("nvidia-smi")


def test_options_are_checked(tmp_path):
    make_repo(tmp_path, {"p1": {}})
    for opts, msg in (({"profile": "smoke"}, "--vlm-url"), ({"ab_phase": "x"}, "ab-phase"),
                      ({"force": frozenset({"nope"})}, "unknown stage"), ({"projects": ["../x"]}, "invalid"),
                      ({"projects": ["p9"]}, "no project folder"), ({"private": ["client-villa"]}, "alias"),
                      ({"ab": ["p1"], "ab_controls": "p2"}, "not one of"), ({}, "nothing to run")):
        opts.setdefault("projects", [] if "ab" in opts or opts == {} else ["p1"])
        r = Run(tmp_path, **opts)
        lines = []
        assert SC.run_pod(r.opts, out=lines.append, runner=r.cli, clock=r.clock, server_factory=r.servers,
                          check_models=MODELS) == 2
        assert msg in lines[-1], (opts, lines)
        assert not any("client-villa" in line for line in lines)      # a wrong alias is never echoed


# --------------------------------------------------------------------------
# Private projects
# --------------------------------------------------------------------------

def test_private_project_paths_link_and_quiet_output(tmp_path):
    r = Run(tmp_path, {"p1": {}, "synthetic-02": {}}, projects=["p1"], private=["real-01"], private_selftest=True,
            buildings={"selftest-02": {"status": "needs_review"}})
    upload = tmp_path / "pp" / "real-01"
    write(upload / "Yilmaz villa zemin.dxf", "x")
    assert r.run() == 0
    # selftest-02 copied once from projects/synthetic-02; the results-private links exist.
    assert (tmp_path / "pp" / "selftest-02" / "plan.dxf").is_file()
    for alias in ("real-01", "selftest-02"):
        link = tmp_path / "job" / "results-private" / alias
        assert link.is_symlink() and Path(os.readlink(link)) == tmp_path / "pr" / alias
    intake = r.cli.find("intake", "real-01")[0]["cmd"]
    assert intake[:5] == ["PY", "-m", "wenart.intake", "stage", "real-01"]
    assert opt(intake, "--out") == str(tmp_path / "po" / "real-01" / "input" / "real-01")
    assert opt(intake, "--root") == str(tmp_path / "pp")
    pipeline = r.cli.find("pipeline", "real-01")[0]["cmd"]
    assert pipeline[3] == str(tmp_path / "po" / "real-01" / "input" / "real-01")
    assert r.record("real-01", "pipeline", root="po")["status"] == "ok"
    # The orchestrator prints only "<alias> <stage> <status> <seconds>s" for a private project.
    for line in r.lines:
        if line.startswith(("real-01 ", "selftest-02 ")):
            parts = line.split()
            assert len(parts) == 4 and parts[2] in ST.STATUSES and parts[3].endswith("s"), line
    assert not any("Yilmaz" in line for line in r.lines)
    # No style-photo test (synthetic fixture) for a private project; no private project in any test list.
    assert not [c for c in r.cli.find("style-photo") if c["project"] == "real-01"]
    lists = r.manifest()["test_lists"]
    assert "real-01" not in " ".join(lists.values()) and lists["SELFTEST_TEST_ALIAS"] == "selftest-02"


def test_run_manifests_keep_private_details_private(tmp_path):
    r = Run(tmp_path, {"p1": {}}, projects=["p1"], private=["real-01"], rc={("build", "real-01"): 1})
    write(tmp_path / "pp" / "real-01" / "a.dxf", "x")
    assert r.run() == 1
    public = r.manifest()
    entries = {p["name"]: p for p in public["projects"]}
    assert set(entries["real-01"]) == {"name", "private", "state"} and entries["real-01"]["state"] == "failed"
    assert "stages" in entries["p1"] and entries["p1"]["out_dir"]
    assert "outputs-private" not in json.dumps(public) and str(tmp_path / "po") not in json.dumps(public)
    private = json.loads((tmp_path / "job" / "results-private" / "_run_manifest.json").read_text())
    assert [p["name"] for p in private["projects"]] == ["real-01"]
    stages = {s["stage"]: s for s in private["projects"][0]["stages"]}
    assert stages["build"]["status"] == "failed"
    # A private record keeps only neutral notes (the build log line is not copied into it).
    assert stages["build"]["note"] == "exit 1 (details in the stage log on the volume)"


def test_not_uploaded_private_project_is_needs_review(tmp_path):
    r = Run(tmp_path, {"p1": {}}, projects=["p1"], private=["real-02"])
    assert r.run() == 0
    rec = r.record("real-02", "intake", root="po")
    assert rec["status"] == "needs_review" and rec["note"] == "not uploaded"
    assert not r.cli.find("intake") and not r.cli.find("pipeline", "real-02")
    assert r.servers.starts == ["qwen", "qwen", "glm"]


def test_intake_collision_is_needs_review(tmp_path):
    r = Run(tmp_path, {"p1": {}}, private=["real-03"], flags={"intake": {"real-03": "needs_review"}})
    write(tmp_path / "pp" / "real-03" / "a.dxf", "x")
    assert r.run() == 0
    rec = r.record("real-03", "intake", root="po")
    assert rec["status"] == "needs_review" and rec["note"] == "document name collision"


def test_orchestrator_traceback_goes_to_the_private_log(tmp_path):
    r = Run(tmp_path, {"p1": {}}, projects=["p1"], private=["real-01"])
    write(tmp_path / "pp" / "real-01" / "a.dxf", "x")

    def broken(cmd, env, cwd, timeout, log_path):
        if "wenart.furniture.decor" in cmd:
            raise KeyError("/workspace/outputs-private/real-01/Yilmaz villa.dxf")
        return r.cli(cmd, env, cwd, timeout, log_path)

    lines = []
    rc = SC.run_pod(r.opts, out=lines.append, runner=broken, clock=r.clock, server_factory=r.servers,
                    check_models=MODELS)
    assert rc == 1
    assert "orchestrator error KeyError" in lines
    assert not any("Yilmaz" in line for line in lines)
    log = tmp_path / "job" / "results-private" / "_logs" / "orchestrator.log"
    assert "Yilmaz villa" in log.read_text() and "Traceback" in log.read_text()
    assert r.manifest()["exit_code"] == 1
    # A public run prints the traceback.
    tmp2 = tmp_path / "pub"
    tmp2.mkdir()
    r2 = Run(tmp2, {"p1": {}}, projects=["p1"])
    lines2 = []
    rc = SC.run_pod(r2.opts, out=lines2.append, runner=lambda *a: (_ for _ in ()).throw(ValueError("bad")),
                    clock=r2.clock, server_factory=r2.servers, check_models=MODELS)
    assert rc == 1 and any("Traceback" in line for line in lines2)


# --------------------------------------------------------------------------
# GPU tests and the exit code
# --------------------------------------------------------------------------

def test_gpu_test_groups_lists_and_junit(tmp_path):
    r = Run(tmp_path, {"p1": {}, "p2": {}, "p4": {"brief": {"polish": False}}},
            buildings={"p2": {"status": "needs_review"}}, projects=["p1", "p2", "p4"])
    assert r.run() == 0
    calls = r.cli.find("pytest")
    assert [c["cmd"][0] for c in calls] == ["PY", "POLISH_PY"]
    full, polish = calls
    assert full["cmd"][3:6] == ["-m", "gpu", "tests/gpu/test_full_run.py"]
    assert "tests/gpu/test_realism.py" not in full["cmd"]           # no A/B project
    assert "tests/gpu/test_render.py" in full["cmd"] and "tests/gpu/test_check.py" in full["cmd"]
    assert f"--junitxml={tmp_path / 'results' / 'junit-full.xml'}" in full["cmd"]
    assert polish["cmd"][5:7] == ["tests/gpu/test_polish.py", "tests/gpu/test_polish_backend.py"]
    env = full["env"]
    assert env["RUN_TEST_PROJECTS"] == "p1 p4" and env["NEEDS_REVIEW_TEST_PROJECTS"] == "p2"
    assert env["RENDER_TEST_PROJECTS"] == "p1 p4" and env["CHECK_TEST_PROJECTS"] == "p1 p4"
    assert env["FURNISH_TEST_PROJECTS"] == "p1 p4" and env["POLISH_TEST_PROJECTS"] == "p1"
    assert env["GATE_TEST_PROJECTS"] == "p1" and env["AB_TEST_PROJECTS"] == "" and env["SELFTEST_TEST_ALIAS"] == ""
    assert env["WENART_OUTPUTS"] == str(tmp_path / "outputs")
    # Every list is exported even when empty: a test never falls back to old outputs on the volume.
    assert all(k in env for k in SC.TEST_LISTS)
    # Tests run after the last server stopped.
    assert r.servers.open == 0
    assert [t["status"] for t in r.manifest()["tests"]] == ["passed", "passed"]


def test_failed_test_group_fails_the_run(tmp_path):
    r = Run(tmp_path, {"p1": {}}, projects=["p1"], rc={"pytest": lambda cli: 1 if cli.calls[-1]["cmd"][0] == "PY" else 0})
    assert r.run() == 1
    assert [t["status"] for t in r.manifest()["tests"]] == ["failed", "passed"]


def test_empty_lists_skip_test_groups(tmp_path):
    r = Run(tmp_path, {"p2": {}}, buildings={"p2": {"status": "needs_review"}}, projects=["p2"])
    assert r.run() == 0
    calls = r.cli.find("pytest")
    assert len(calls) == 1 and calls[0]["cmd"][5:] == ["tests/gpu/test_full_run.py", "-v", "-ra",
                                                        f"--junitxml={tmp_path / 'results' / 'junit-full.xml'}"]
    assert [t["status"] for t in r.manifest()["tests"]] == ["passed", "skipped"]


def test_server_failure_fails_the_layout(tmp_path):
    r = Run(tmp_path, {"p1": {}}, projects=["p1"], fail={"qwen": "early_exit"})
    assert r.run() == 1
    rec = r.record("p1", "layout")
    assert rec["status"] == "failed" and "early_exit" in rec["note"]
    assert not r.cli.find("build")
