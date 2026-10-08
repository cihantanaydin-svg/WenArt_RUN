"""The full-run scheduler with a fake runner, a fake clock and fake servers (docs/milestone6.md §2.3, §9;
docs/milestone7.md §9.1).

The fake runner (``FakeCLI``) records every command and writes what the real
CLI would write (building, style, scene and render manifests, answers files,
recognition questions and answers, detections, ...), so the orchestrator's
decisions are checked without Blender, a GPU or a model: phase order, server
sessions only when needed (2/3/4 starts), needs_review, pending and deadline
handling, reuse by fingerprint, statuses, the recognition flow, the detector,
the realism v2 A/B steps, the smoke profile, the private plumbing and the
exit code.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
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
SECONDS = {"pipeline": 5, "pipeline_final": 5, "build": 30, "render": 100, "control renders": 20,
           "gate calibrate": 120, "polish": 200, "gate detect": 30, "check run": 60, "layout": 40, "realism2": 50,
           "recognize": 10, "pytest": 30}
# Schema-valid recognition answers (wenart.recognition.schemas.M7_SCHEMAS).
RECOGNITION_ANSWERS = {"symbol_type": {"type": "sofa", "front": "none", "confidence": 0.9, "reason": "fake"},
                       "room_label": {"label": "Salon", "size_text": None, "area_text": None, "box": None}}


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
        self.alt_looks: list = []            # (project, --alt-look) of every render with an alt look
        self.pairs_outs: list = []           # (project, --project-outs names) of every realism2-pairs

    @staticmethod
    def name_of(cmd) -> str:
        if cmd[0] == "nvidia-smi":
            return "nvidia-smi"
        mod = cmd[2] if len(cmd) > 2 and cmd[1] == "-m" else cmd[0]
        sub = cmd[3] if len(cmd) > 3 else ""
        if mod == "wenart.ingest.pipeline":
            return "pipeline_final" if ("--answers" in cmd or "--no-ai" in cmd) else "pipeline"
        if mod == "wenart.sheets":                              # Milestone 10: the sheet analysis (first or final)
            return "sheets"
        if mod == "wenart.recognition.answers":
            return "recognize"
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
        if mod == "wenart.furniture.decor_ai":                  # Milestone 9: ask (VLM) and apply (the decor stage)
            return "decor" if sub == "apply" else "decor_ask"
        if mod == "wenart.blender.cli":
            if sub == "build":
                return "build"
            if sub == "export":                                 # Milestone 9: the 3D files
                return "export"
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
        if mod in ("wenart.ingest.pipeline", "wenart.sheets"):
            return Path(opt(cmd, "--out")).name
        if mod == "wenart.recognition.answers":
            return Path(cmd[4]).parent.name
        if mod == "wenart.gate" and len(cmd) > 4 and cmd[3] == "detect":
            return Path(cmd[4]).name
        if mod == "wenart.intake":
            return cmd[4]
        if mod == "wenart.blender.cli":
            path = Path(opt(cmd, "--out"))
            while path.name in ("scene", "renders", "controls", "ab", "ctl_flat", "ctl_proxy", "ctl_direct",
                                "ctl_lowspp", "nuisance_ev", "export"):
                path = path.parent
            return path.name
        if mod in ("wenart.furniture.fit", "wenart.furniture.layout", "wenart.furniture.decor"):
            return Path(cmd[3]).parent.name
        if mod == "wenart.furniture.decor_ai":
            return Path(cmd[4]).parent.name
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
        if not (Path(opt(cmd, "--root")) / project).is_dir():
            # wenart.intake: no upload -> a fresh needs_review manifest, the old staged copy removed, exit 4.
            shutil.rmtree(out, ignore_errors=True)
            write(out.parent.parent / "intake_manifest.json", {"status": "needs_review", "reasons": ["not uploaded"]})
            return 4
        status = self.flags.get("intake", {}).get(project, "ok")
        out.mkdir(parents=True, exist_ok=True)
        write(out / "plan.dxf", "x")
        if status == "no_manifest":           # exit 4 (needs_review) with an unreadable manifest
            return 4
        reasons = self.flags.get("intake_reasons", {}).get(project, ["document name collision"])
        manifest = {"status": status, "reasons": reasons if status != "ok" else []}
        write(out.parent.parent / "intake_manifest.json", manifest)
        return 0 if status == "ok" else 4    # wenart.intake: exit 4 = needs_review

    def h_sheets(self, cmd, project, log):
        """wenart.sheets: sheets.json and sheets_report.md; exit 1 for a project whose spec says
        ``sheets_status: needs_review``; exit 0 otherwise (the sheet_region questions are tested with track A1's
        answer schema)."""
        out = Path(opt(cmd, "--out"))
        spec = self.buildings.get(project, {})
        status = spec.get("sheets_status", "ok")
        write(out / "sheets.json", {"kind": "sheets", "project": project, "needs_review": [] if status == "ok" else
                                    [{"reason": "no readable plan region"}], "answers": opt(cmd, "--answers"),
                                    "no_ai": "--no-ai" in cmd})
        write(out / "sheets_report.md", "# sheets\n")
        return 0 if status == "ok" else 1

    def h_pipeline(self, cmd, project, log):
        """wenart.ingest.pipeline: exit 0 ok, 1 needs_review, 4 when the project has recognition questions (they go
        to recognition/requests.json; the building is in its pre-answer state)."""
        out = Path(opt(cmd, "--out"))
        spec = self.buildings.get(project, {})
        status = spec.get("status", "ok")
        rooms = spec.get("rooms", [room("r1", "living", 20.0, True), room("r2", "bedroom", 12.0, False)])
        building = {"project": {"id": project, "brief": spec.get("brief", {})}, "status": status,
                    "levels": [{"id": "L0"}], "rooms": rooms if status == "ok" else [], "furniture": [],
                    "stage": "first"}
        questions = int(spec.get("questions", 0)) if status == "ok" else 0
        if questions:
            items = [{"key": f"sym_L0_{i:03d}", "task": "symbol_type", "page": 1,
                      "images": [f"crops/sym_L0_{i:03d}_ctx.png"],
                      "input_sha256": hashlib.sha256(f"{project}:{i}:{spec.get('hash', 'h1')}".encode()).hexdigest()}
                     for i in range(1, questions + 1)]
            write(out / "recognition" / "requests.json", {"kind": "recognition_requests", "project": project,
                                                          "items": items})
            building["furniture"] = [{"id": f"f_L0_{i:03d}", "type": "unknown", "status": "unverified"}
                                     for i in range(1, questions + 1)]
        write(out / "building.json", building)
        write(out / "report.md", "# report\n")
        return 1 if status != "ok" else 4 if questions else 0

    def h_pipeline_final(self, cmd, project, log):
        """The pipeline again with --answers (or --no-ai); the building records how it was made. Exit 4 only for a
        ``second_round`` project without --no-ai: its answers opened new questions (a raster page's second round),
        written to recognition/requests.json."""
        out = Path(opt(cmd, "--out"))
        spec = self.buildings.get(project, {})
        status = spec.get("final_status", "ok")
        building = json.loads((out / "building.json").read_text()) if (out / "building.json").is_file() else {}
        if project in self.flags.get("second_round", ()) and "--no-ai" not in cmd:
            req = out / "recognition" / "requests.json"
            doc = json.loads(req.read_text())
            doc["items"].append({"key": "sym_L0_900", "task": "symbol_type", "page": 1,
                                 "images": ["crops/sym_L0_900_ctx.png"],
                                 "input_sha256": hashlib.sha256(b"second round").hexdigest()})
            write(req, doc)
            building.update(status="ok", stage="final_pending", answers=opt(cmd, "--answers"), no_ai=False)
            write(out / "building.json", building)
            return 4
        building.update(status=status, stage="final", answers=opt(cmd, "--answers"), no_ai="--no-ai" in cmd)
        if status != "ok":
            building["rooms"] = []
        write(out / "building.json", building)
        return 0 if status == "ok" else 1

    def h_recognize(self, cmd, project, log):
        """wenart.recognition.answers ask: seeds first, then (with --server) every missing item; exit 0, 3 (cut) or
        2 (server error)."""
        rec = Path(cmd[4])
        key = opt(cmd, "--model-key")
        slug, model = MODELS[key]["slug"], MODELS[key]["id"]
        items = json.loads((rec / "requests.json").read_text())["items"]
        path = rec / f"answers_{slug}.json"
        store = json.loads(path.read_text()) if path.is_file() else {"model": model, "calls": {}}
        calls = store["calls"]
        if opt(cmd, "--seed-answers"):
            seed = Path(opt(cmd, "--seed-answers")) / f"answers_{slug}.json"
            if seed.is_file():
                for k, r in json.loads(seed.read_text())["calls"].items():
                    item = next((i for i in items if i["key"] == k), None)
                    if item and r.get("input_sha256") == item["input_sha256"] and k not in calls:
                        calls[k] = dict(r, seeded_from=str(seed))
        cut = (project, key) in self.flags.get("recog_cut", ())
        fail = (project, key) in self.flags.get("recog_fail", ())
        if opt(cmd, "--server") and not fail:
            todo = [i for i in items if not (calls.get(i["key"]) or {}).get("input_sha256") == i["input_sha256"]]
            for i in todo[:1] if cut else todo:
                calls[i["key"]] = {"task": i["task"], "input_sha256": i["input_sha256"], "model": model,
                                   "data": RECOGNITION_ANSWERS[i["task"]], "error": None}
        store.update(model=model, slug=slug, model_key=key, kind="recognition_answers", incomplete=cut,
                     calls=dict(sorted(calls.items())))
        write(path, store)
        done = all((calls.get(i["key"]) or {}).get("input_sha256") == i["input_sha256"] for i in items)
        return 0 if done else 3 if cut else 2

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
        b = json.loads(Path(cmd[3]).read_text())
        if project in self.flags.get("download_fail", ()):
            # wenart.furniture.fit: a failed model download is a parametric fallback with exit 0.
            b["furniture"] = list(b.get("furniture") or []) + [{
                "id": "f_doc", "room_id": "r1", "source": "from_documents",
                "asset": {"method": "parametric", "fallback_reason": "download of sofa_01 failed (NetworkError: "
                                                                     "offline); parametric fallback"}}]
        write(opt(cmd, "--out"), b)

    h_refit = h_fit

    def h_decor(self, cmd, project, log):
        src = cmd[4] if cmd[2] == "wenart.furniture.decor_ai" else cmd[3]
        write(opt(cmd, "--out"), json.loads(Path(src).read_text()))

    def h_decor_ask(self, cmd, project, log):
        write(opt(cmd, "--answers"), {"kind": "decor_ai_answers", "answers": {}})

    def h_export(self, cmd, project, log):
        write(Path(opt(cmd, "--out")) / "export_manifest.json", {"files": {}})

    def h_layout(self, cmd, project, log):
        b = json.loads(Path(cmd[3]).read_text())
        empty = [r for r in b["rooms"] if not r["has_documented_furniture"]]
        if empty:
            b["furniture"] = b["furniture"] + [{"id": "f_ai", "room_id": empty[0]["id"], "source": "added_by_ai"}]
        else:           # Milestone 10: only furnished rooms: the completion adds a piece (furnished_rooms: complete)
            b["furniture"] = b["furniture"] + [{"id": "f_ai", "room_id": b["rooms"][0]["id"], "source": "added_by_ai",
                                                "completes_room": True}]
        write(opt(cmd, "--out"), b)
        write(Path(opt(cmd, "--out")).parent / "layout.json", {"rooms": []})
        # Milestone 10: the completion of furnished rooms runs in the same CLI (docs/milestone10.md §1.6a).
        write(Path(opt(cmd, "--out")).parent / "completion.json", {"kind": "completion", "rooms": []})
        write(Path(opt(cmd, "--out")).parent / "completion_report.md", "# completion\n")

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
        if opt(cmd, "--alt-look") is not None:
            self.alt_looks.append((project, opt(cmd, "--alt-look")))
        scene = json.loads((Path(opt(cmd, "--scene")).parent / "scene_manifest.json").read_text())
        cams = [c["name"] for c in scene["cameras"]]
        if opt(cmd, "--cameras", "all") != "all":
            cams = opt(cmd, "--cameras").split(",")
        cut = project in self.flags.get("render_cut", ())
        if cut:
            cams = cams[:1]
        key = self.flags.get("render_key", {}).get(project, "k1")
        alt = opt(cmd, "--alt-look")
        write(out / "render_manifest.json", {"renders": [{"camera": c, "preview": f"{c}_preview.jpg",
                                                          "alt_preview": f"{c}_alt_preview.jpg" if alt else None,
                                                          "scene_sha256": "s1", "render_key": key, "skipped": False}
                                                         for c in cams],
                                             "alt_look": alt, "incomplete": cut, "deadline": self.clock()})
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
              {"kind": "gate_calibration", "incomplete": project in self.flags.get("gate_cut", ()),
               "rates": {"benign_accept": 1.0, "negative_reject": 0.95}})

    def h_gate_validate(self, cmd, project, log):
        decision = self.flags.get("gate_decision", {}).get(project, "ok")
        write(Path(opt(cmd, "--project-out")) / "gate" / "gate_validation.json", {"decision": decision})

    def h_polish(self, cmd, project, log):
        write(Path(opt(cmd, "--project-out")) / "polish" / "polish_manifest.json",
              {"incomplete": project in self.flags.get("polish_cut", ())})

    def h_gate_detect(self, cmd, project, log):
        write(Path(opt(cmd, "--out")) / "detect_manifest.json",
              {"incomplete": project in self.flags.get("detect_cut", ()), "views": {}})

    def h_expected(self, cmd, project, log):
        write(Path(opt(cmd, "--project-out")) / "check" / "expected_views.json", {"views": {}})

    def _answers(self, cmd, project, sub="", cut=False, prefix="answers_"):
        key = opt(cmd, "--model-key")
        path = Path(opt(cmd, "--project-out")) / "check" / sub / f"{prefix}{MODELS[key]['slug']}.json"
        cut = cut or (project, key) in self.flags.get("answers_cut", ())
        write(path, {"incomplete": cut, "sets": opt(cmd, "--sets")})

    def h_check_run(self, cmd, project, log):
        # run_cut: only the run step is cut; the preference after it asks nothing and rewrites the same answers
        # file with incomplete: false (vision_check.calls.run_specs).
        self._answers(cmd, project, cut=(project, opt(cmd, "--model-key")) in self.flags.get("run_cut", ()))

    def h_preference(self, cmd, project, log):
        self._answers(cmd, project)

    def h_style_photo(self, cmd, project, log):
        write(opt(cmd, "--out"), {"calls": [], "incomplete": False})

    def h_combine(self, cmd, project, log):
        write(Path(opt(cmd, "--project-out")) / "check" / "check_manifest.json", {"views": {}})

    def h_report(self, cmd, project, log):
        # wenart.report final: exit 1 with status not_rendered when there is no render manifest and the project
        # is not needs_review.
        po = Path(opt(cmd, "--project-out"))
        reviews = [(json.loads(p.read_text()) if p.is_file() else {}).get("status")
                   for p in (po / "building.json", po / "intake_manifest.json")]
        if (po / "renders" / "render_manifest.json").is_file():
            status, render, rc = "ok", "run", 0
        elif "needs_review" in reviews:
            status, render, rc = "needs_review", "not_run", 0
        else:
            status, render, rc = "not_rendered", "not_run", 1
        write(po / "final" / "final_report.md", "# final\n")
        write(po / "final" / "final_manifest.json", {"status": status, "stages": {"render": render}})
        return rc

    def h_ab_m5(self, cmd, project, log):
        out = Path(opt(cmd, "--project-out"))
        cams = [{"name": c, "position": [1.0, 1.0, 1.4], "target": [2.0, 1.0, 1.3]}
                for c in ("cam_a_1", "cam_a_2", "cam_b_1")]
        write(out / "ab" / "m5" / "scene_manifest.json", {"cameras": cams})
        write(out / "ab" / "m5" / "render_manifest.json", {"renders": []})
        b = {"project": {"id": project}, "status": "ok", "rooms": [], "furniture": []}
        write(out / "ab" / "m5" / "building_final.json", b)
        write(out / "ab" / "building_m5.json", b)

    def h_realism2_pairs(self, cmd, project, log):
        """realism2-pairs: look_alt pairs when the project is among --project-outs, the control sets with --controls
        (paths relative to the project output); exit 1 when no pair could be made."""
        out = Path(opt(cmd, "--project-out"))
        outs = cmd[cmd.index("--project-outs") + 1:] if "--project-outs" in cmd else [str(out)]
        names = sorted(Path(o).name for o in outs)
        pairs = []
        manifest = out / "renders" / "render_manifest.json"
        alt = manifest.is_file() and all(e.get("alt_preview") for e in json.loads(manifest.read_text())["renders"])
        if out.name in names and alt:           # look_alt needs both previews of the main renders
            pairs += [{"pair_id": f"look_alt:c{i}", "set": "look_alt"} for i in range(3)]
        if "--controls" in cmd:
            pairs += [{"pair_id": f"{s}:c{i}", "set": s} for s in ("ctl_flat", "null_identical") for i in range(2)]
        for p in pairs:
            name = p["pair_id"].replace(":", "_")
            p.update(a=f"ab/fake/{name}_a.jpg", b=f"ab/fake/{name}_b.jpg")
            write(out / p["a"], b"a")
            write(out / p["b"], b"b")
        self.pairs_outs.append((project, names))
        write(out / "ab" / "pairs_v2.json", {"kind": "realism2_pairs", "controls": "--controls" in cmd, "pairs": pairs,
                                             "look_alt": {"projects": names}, "dropped": []})
        return 0 if pairs else 1

    def h_realism2(self, cmd, project, log):
        self._answers(cmd, project, "realism", prefix="answers_realism2_")

    def h_realism2_combine(self, cmd, project, log):
        write(Path(opt(cmd, "--project-out")) / "check" / "realism" / "realism2_ab.json", {})

    def h_realism2_summary(self, cmd, project, log):
        write(Path(opt(cmd, "--out")) / "realism2_summary.json", {})

    def h_nvidia_smi(self, cmd, project, log):
        name, mem = self.flags.get("gpu", ("NVIDIA RTX PRO 4500 Blackwell", 32607))
        with open(log, "a") as fh:
            fh.write(f"{name}, {mem}\n")

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
    # furnished_rooms: keep (M9 behaviour): a fully furnished project needs no layout session.
    r2 = Run(tmp2, {"p1": {"brief": {"furnished_rooms": "keep"}}}, buildings={"p1": {"rooms": rooms_full}},
             projects=["p1"])
    assert r2.run() == 0
    assert r2.servers.starts == ["qwen", "glm"]
    assert r2.record("p1", "layout")["status"] == "skipped"
    assert r2.record("p1", "layout")["note"] == "no empty or completable room"
    assert r2.record("p1", "photos")["note"] == "no style photos"
    assert opt(r2.cli.find("decor")[0]["cmd"], "--out").endswith("building_decor.json")
    assert r2.cli.find("decor")[0]["cmd"][4].endswith("building_fitted.json")       # decor_ai apply <building>
    # Milestone 10 default (furnished_rooms: complete): the same project's furnished rooms are completed in a session.
    tmp3 = tmp_path / "third"
    tmp3.mkdir()
    r3 = Run(tmp3, {"p1": {}}, buildings={"p1": {"rooms": rooms_full}}, projects=["p1"])
    assert r3.run() == 0
    assert r3.servers.starts == ["qwen", "qwen", "glm"] and r3.record("p1", "layout")["status"] == "ok"


def test_m9_decor_questions_in_the_qwen_session_and_the_3d_export(tmp_path, monkeypatch):
    """docs/milestone9.md §4, §5: the AI decor asks in the layout's Qwen session, after the layout (no extra server
    start); the decor stage applies the answers; a resumed pod reuses them without a server; the 3D files follow
    the render; a server that fails leaves a warning and the rule decor (never silently)."""
    monkeypatch.setattr(SC.Orchestrator, "decor_rooms_needed", lambda self, pr: 3)
    r = Run(tmp_path, {"p1": {}}, projects=["p1"])
    assert r.run() == 0
    names = r.cli.names()
    assert names.index("layout") < names.index("decor_ask") < names.index("assets") < names.index("decor")
    assert first(names, "render") < first(names, "export") < first(names, "select-controls")
    assert r.servers.starts == ["qwen", "qwen", "glm"]                       # the layout's session, no extra one
    ask = r.cli.find("decor_ask")[0]["cmd"]
    assert opt(ask, "--server").startswith("http://fake-") and opt(ask, "--answers").endswith("decor_ai_answers.json")
    assert ask[4].endswith("building_furnished.json")                         # the layout's building
    assert r.record("p1", "decor_ask")["status"] == "ok" and r.record("p1", "export")["status"] == "ok"
    assert "decor_ai_answers.json" in {Path(k).name for k in r.record("p1", "decor")["inputs"]}
    export = r.cli.find("export")[0]["cmd"]
    assert opt(export, "--name") == "p1" and opt(export, "--out").endswith("p1/export")
    # Resumed: layout and answers reused, so phase 3 starts no server.
    r2 = Run(tmp_path, projects=["p1"])
    assert r2.run() == 0
    assert r2.servers.starts == ["qwen", "glm"] and not r2.cli.find("decor_ask")
    assert r2.record("p1", "decor_ask")["status"] == "reused"
    # A failed Qwen start: the layout fails as before; the decor questions are a warning (rule decor).
    tmp3 = tmp_path / "third"
    tmp3.mkdir()
    r3 = Run(tmp3, {"p1": {"brief": {"furnished_rooms": "keep"}}},
             buildings={"p1": {"rooms": [room("r1", "living", 20.0, True)]}}, projects=["p1"], fail={"qwen": "early_exit"})
    r3.run()
    rec = r3.record("p1", "decor_ask")
    assert rec["status"] == "warning" and "rule decor" in rec["note"]


def test_m9_no_decor_questions_skip_the_stage_and_smoke_skips_the_export(tmp_path):
    r = Run(tmp_path, {"p1": {}}, projects=["p1"])
    assert r.run() == 0
    assert r.record("p1", "decor_ask")["status"] == "skipped"
    assert r.record("p1", "decor_ask")["note"] == "no decor questions"


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
    # Render pod: p1 is the control project (no control renders yet: made with the M6 steps) and an A/B project
    # outside --projects (no main renders on the volume: no look_alt pairs of its own).
    r = Run(tmp_path, {"p1": {}}, ab=["p1"], ab_controls="p1", ab_phase="render")
    assert r.run() == 0
    assert r.servers.starts == []
    pairs = json.loads((tmp_path / "outputs" / "p1" / "ab" / "pairs_v2.json").read_text())
    assert pairs["controls"] and {p["set"] for p in pairs["pairs"]} == {"ctl_flat", "null_identical"}
    r2 = Run(tmp_path, ab=["p1"], ab_controls="p1", ab_phase="judge")
    assert r2.run() == 0
    assert r2.servers.starts == ["qwen", "glm"]
    assert not r2.cli.find("build") and not r2.cli.find("render") and not r2.cli.find("pipeline")
    assert r2.record("p1", "ab_prepare")["note"] == "not in this phase"
    assert r2.record("p1", "ab_pairs")["status"] == "reused"


# --------------------------------------------------------------------------
# needs_review, failures, statuses
# --------------------------------------------------------------------------

def test_needs_review_stops_the_project_and_starts_no_server(tmp_path):
    r = Run(tmp_path, {"p2": {}}, buildings={"p2": {"status": "needs_review"}}, projects=["p2"])
    assert r.run() == 0                       # needs_review is a result, not a failure
    assert r.servers.starts == []
    assert r.cli.names("p2") == ["sheets", "pipeline", "report"]
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
    assert r2.cli.names("p2") == ["sheets", "pipeline", "report"]


def test_sheets_needs_review_stops_the_project_before_the_pipeline(tmp_path):
    """Milestone 10 (docs/milestone10.md §1.6a): sheets exit 1 (no readable plan region, no unit agreement) is the
    project's result; the pipeline never runs, the report does."""
    r = Run(tmp_path, {"p2": {}}, buildings={"p2": {"sheets_status": "needs_review"}}, projects=["p2"])
    assert r.run() == 0
    assert r.cli.names("p2") == ["sheets", "report"]
    assert r.record("p2", "sheets")["status"] == "needs_review"
    assert r.manifest()["projects"][0]["state"] == "needs_review"
    assert r.servers.starts == []


def test_build_exit_2_is_failed_with_the_last_build_log_line(tmp_path):
    r = Run(tmp_path, {"p1": {}}, rc={"build": 2}, projects=["p1"])
    assert r.run() == 1
    rec = r.record("p1", "build")
    assert rec["status"] == "failed" and rec["rc"] == 2
    assert rec["note"] == "exit 2: error: the building refused the request"
    assert "render" not in r.cli.names("p1") and "report" in r.cli.names("p1")
    assert r.manifest()["projects"][0]["state"] == "failed"


def test_the_brief_lens_reaches_the_build(tmp_path):
    """Milestone 8 (docs/milestone8.md §5): a brief with ``render.lens_mm`` builds with ``--lens-mm``; a brief
    without it (auto) or with a value outside 14-35 mm (reported by the brief loader, default used) builds
    without, so the build's own 18 / 16 mm rule applies."""
    r = Run(tmp_path, {"p1": {"brief": {"render": {"lens_mm": 20}}}, "p2": {},
                       "p3": {"brief": {"render": {"lens_mm": 50}}}}, projects=["p1", "p2", "p3"])
    assert r.run() == 0
    (p1,), (p2,), (p3,) = (r.cli.find("build", p) for p in ("p1", "p2", "p3"))
    assert opt(p1["cmd"], "--lens-mm") == "20" and p1["cmd"][-1] == "--reuse"
    assert "--lens-mm" not in p2["cmd"] and "--lens-mm" not in p3["cmd"]


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
    # p1: calibrate failed -> its stale calibration is moved aside and validate still runs (the report then
    # reads this run's not_validated), but nothing it writes lets the project polish.
    assert r.cli.find("gate validate", "p1") and not r.cli.find("polish")
    gate = tmp_path / "outputs" / "p1" / "gate"
    assert (gate / "gate_calibration.failed.json").is_file() and not (gate / "gate_calibration.json").exists()
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
    assert rec["kind"] == "stage_record" and rec["outputs"] == ["building_furnished.json", "layout.json",
                                                                 "completion.json", "completion_report.md"]
    assert rec["log"] == "logs/layout.log" and len(rec["fingerprint"]) == 64
    assert set(rec["inputs"]) == {ST.file_hashes([tmp_path / "outputs/p1/building_fitted.json"]).popitem()[0],
                                  ST.file_hashes([tmp_path / "outputs/p1/style.json"]).popitem()[0],
                                  # Milestone 10: the brief's furnished_rooms keys drive the layout too
                                  ST.file_hashes([tmp_path / "repo/projects/p1/brief.yaml"]).popitem()[0]}
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


def test_realism2_estimate_counts_8_calls_per_pair_and_serial_null_identical(tmp_path):
    """M7 §9.1: a v2 pair costs 8 calls; null_identical is asked one call at a time. Judge pod with the render
    pod's pairs (p3: 3 look_alt; p1: 2 ctl_flat + 2 null_identical): Qwen start 300; Qwen realism of p3 (est
    4.4 * 8 * 3 / 2 = 52.8 s, takes 50 s) and of p1 (4.4 * (8 * 2 / 2 + 8 * 2 / 1) = 105.6 s, takes 50 s) -> t = 400;
    GLM start (150) -> 550; GLM realism of p3 (602.8 < 640) -> 600; of p1 needs 105.6 s: not before the deadline 640
    (the M6 rule, 2 calls per pair at 2 at once, 15.4 s, would have asked it)."""
    Run(tmp_path, {"p1": {}, "p3": {}}, projects=["p3"], ab=["p3"], ab_controls="p1", ab_phase="render").run()
    r = Run(tmp_path, ab=["p3"], ab_controls="p1", ab_phase="judge", deadline_in=640)
    assert r.run() == 1
    keys = [(c["project"], opt(c["cmd"], "--model-key")) for c in r.cli.find("realism2")]
    assert keys == [("p3", "qwen"), ("p1", "qwen"), ("p3", "glm")]
    rec = r.record("p1", "ab_realism")
    assert rec["status"] == "incomplete" and rec["note"].endswith("deadline: realism (glm) not started")
    assert S.est_realism2(4, 2, 2) == pytest.approx(4.4 * (8 * 2 / 2 + 8 * 2))


# --------------------------------------------------------------------------
# A/B steps
# --------------------------------------------------------------------------

def test_ab_render_phase_commands(tmp_path):
    """M7 §8.2: the control project's control renders (missing here: the M6 steps make them, with the alt look
    None) and the look_alt project's main render with --alt-look None; realism2-pairs over the same --project-outs;
    realism2 asks every set; realism2-summary with the control project's output folder."""
    r = Run(tmp_path, {"p1": {}, "p3": {}}, projects=["p3"], ab=["p3"], ab_controls="p1", ab_phase="all")
    assert r.run() == 0
    out1, out3 = tmp_path / "outputs" / "p1", tmp_path / "outputs" / "p3"
    # Part 1 only for the control project that is not in --projects.
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
    assert opt(ab_render, "--alt-look") == "None" and opt(ab_render, "--preview-quality") == "85"
    assert opt(ab_render, "--cameras") == "all"
    sets = {opt(c, "--out").rsplit("/", 2)[-2]: c for c in renders[1:]}
    assert list(sets) == ["ctl_flat", "ctl_proxy", "ctl_direct", "ctl_lowspp", "nuisance_ev"]
    for name, c in sets.items():
        assert opt(c, "--look-from").endswith("ab/renders/render_manifest.json")
        assert opt(c, "--preview-quality") == "85" and opt(c, "--cameras") == "cam_a_1,cam_a_2,cam_b_1"
    assert opt(sets["ctl_direct"], "--max-bounces") == "0" and opt(sets["ctl_lowspp"], "--samples") == "4"
    assert "--no-denoise" in sets["ctl_lowspp"] and opt(sets["nuisance_ev"], "--ev-offset") == "0.3"
    # The look_alt project: its own main render saves the alt previews; nothing of the M5 A/B for it.
    assert opt(r.cli.find("render", "p3")[0]["cmd"], "--alt-look") == "None"
    assert r.cli.alt_looks == [("p1", "None"), ("p3", "None")] or ("p3", "None") in r.cli.alt_looks
    assert not r.cli.find("ab-m5", "p3") and len(r.cli.find("build", "p3")) == 1
    # Pairs: --controls for the control project only; the same look_alt list for both.
    pairs = {c["project"]: c["cmd"] for c in r.cli.find("realism2-pairs")}
    assert "--controls" in pairs["p1"] and "--controls" not in pairs["p3"]
    for cmd in pairs.values():
        assert cmd[cmd.index("--project-outs") + 1:] == [str(out3)]
    assert {p["set"] for p in json.loads((out3 / "ab" / "pairs_v2.json").read_text())["pairs"]} == {"look_alt"}
    assert {p["set"] for p in json.loads((out1 / "ab" / "pairs_v2.json").read_text())["pairs"]} == \
        {"ctl_flat", "null_identical"}
    assert all(opt(c["cmd"], "--sets") is None for c in r.cli.find("realism2"))
    assert sorted((c["project"], opt(c["cmd"], "--model-key")) for c in r.cli.find("realism2")) == \
        [("p1", "glm"), ("p1", "qwen"), ("p3", "glm"), ("p3", "qwen")]
    assert {c["project"] for c in r.cli.find("realism2-combine")} == {"p1", "p3"}
    summary = r.cli.find("realism2-summary")[0]["cmd"]
    assert summary[summary.index("--project-outs") + 1:summary.index("--controls-project")] == [str(out3)]
    assert opt(summary, "--controls-project") == str(out1) and opt(summary, "--out").endswith("results/realism")
    m = r.manifest()
    assert m["realism_summary"]["status"] == "ok"
    assert m["test_lists"]["AB_TEST_PROJECTS"] == "p3" and m["test_lists"]["AB_CONTROL_PROJECT"] == "p1"
    ab = {a["name"]: a for a in m["ab"]}
    assert ab["p1"]["controls"] and not ab["p1"]["look_alt"] and ab["p1"]["controls_rendered"]
    assert ab["p3"]["look_alt"] and not ab["p3"]["controls"]
    assert {s["stage"] for s in ab["p1"]["stages"]} >= {"ab_m5", "ab_render", "ab_controls", "ab_pairs", "ab_realism",
                                                        "ab_combine"}
    # A second pod (pod C of §10): the control renders are on the volume now and are used as they are.
    r2 = Run(tmp_path, projects=["p3"], ab=["p3"], ab_controls="p1", ab_phase="all")
    assert r2.run() == 0
    assert not r2.cli.find("ab-m5") and not r2.cli.find("build", "p1") and not r2.cli.find("render", "p1")
    assert not r2.cli.find("pipeline", "p1")
    for stage in ("ab_render", "ab_controls"):
        rec = r2.record("p1", stage)
        assert rec["status"] == "reused" and "M6 control renders on the volume" in rec["note"]
    assert "--controls" in r2.cli.find("realism2-pairs", "p1")[0]["cmd"]


def test_ab_stage_failure_fails_the_run_look_alt_does_not(tmp_path):
    """Every A/B stage counts in M7, look_alt included (it is the decided set of realism v2)."""
    r = Run(tmp_path, {"p1": {}}, ab=["p1"], ab_controls="p1", rc={"realism2-pairs": 1})
    assert r.run() == 1
    assert r.record("p1", "ab_pairs")["status"] == "failed"
    tmp2 = tmp_path / "b"
    tmp2.mkdir()
    r2 = Run(tmp2, {"p1": {}, "p3": {}}, projects=["p3"], ab=["p3"], ab_controls="p1",
             rc={("realism2", "p3"): 1})
    assert r2.run() == 1
    assert r2.record("p3", "ab_realism")["status"] == "failed"
    assert r2.manifest()["projects"][0]["state"] == "ok"
    assert S.AB_NOT_COUNTED == ()


def test_ab_project_with_needs_review_is_dropped(tmp_path):
    r = Run(tmp_path, {"p2": {}}, buildings={"p2": {"status": "needs_review"}}, ab=["p2"], ab_controls="p2")
    assert r.run() == 1
    rec = r.record("p2", "ab_prepare")
    assert rec["status"] == "failed" and "pipeline needs_review" in rec["note"]
    assert not r.cli.find("ab-m5")
    # A look_alt project outside --projects without main renders on the volume: no pairs, the A/B fails.
    tmp2 = tmp_path / "b"
    tmp2.mkdir()
    r2 = Run(tmp2, {"p3": {}}, ab=["p3"])
    assert r2.run() == 1
    rec = r2.record("p3", "ab_pairs")
    assert rec["status"] == "failed" and rec["note"] == "look_alt: no renders/render_manifest.json on the volume"
    assert not r2.cli.find("pipeline") and not r2.cli.find("realism2-pairs")


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
    assert r.record("p1", "detect")["note"] == "smoke profile" and not r.cli.find("gate detect")
    assert not r.cli.find("pytest") and not r.cli.find("gate calibrate")
    assert opt(render, "--alt-look") == "None"                     # p1 is a look_alt project of the A/B
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
                      ({"ab": ["p1"], "ab_controls": "p2"}, "--ab-controls: no project folder"),
                      ({"ab_controls": "p1"}, "--ab-controls without --ab"), ({}, "nothing to run")):
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

def fixture_project(repo: Path, name: str = "review-01") -> Path:
    """A committed test project under tests/fixtures/projects/ of the fake repo (the self-test source)."""
    folder = repo / "tests" / "fixtures" / "projects" / name
    write(folder / "plan_a.pdf", "a")
    write(folder / "plan_b.pdf", "b")
    return folder


def test_private_project_paths_link_and_quiet_output(tmp_path):
    fixture_project(make_repo(tmp_path, {"p1": {}}))
    r = Run(tmp_path, projects=["p1"], private=["real-01"], private_selftest=True,
            buildings={"selftest-02": {"status": "needs_review"}})
    upload = tmp_path / "pp" / "real-01"
    write(upload / "Yilmaz villa zemin.dxf", "x")
    assert r.run() == 0
    # selftest-02 copied once from tests/fixtures/projects/review-01; the results-private links exist.
    assert sorted(p.name for p in (tmp_path / "pp" / "selftest-02").iterdir()) == ["plan_a.pdf", "plan_b.pdf"]
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


def test_a_stale_selftest_upload_is_moved_aside_and_copied_again(tmp_path):
    """orch-4: an earlier pod copied synthetic-02 to selftest-02 (M6); the self-test source is review-01 now. A copy
    whose files differ from the source is moved to the archive (never deleted) and copied again; a current copy is
    left as it is."""
    fixture_project(make_repo(tmp_path, {"p1": {}}))
    stale = tmp_path / "pp" / "selftest-02"
    write(stale / "plan_scan.png", b"synthetic-02 scan")
    write(stale / "plan_a.pdf", "old a")
    r = Run(tmp_path, projects=["p1"], private_selftest=True, buildings={"selftest-02": {"status": "needs_review"}})
    assert r.run() == 0
    source = tmp_path / "repo" / "tests" / "fixtures" / "projects" / "review-01"
    assert sorted(p.name for p in stale.iterdir()) == ["plan_a.pdf", "plan_b.pdf"]
    assert all((stale / n).read_bytes() == (source / n).read_bytes() for n in ("plan_a.pdf", "plan_b.pdf"))
    aside = [p for p in (tmp_path / "outputs-archive").iterdir() if p.name.startswith("selftest-02-upload-")]
    assert len(aside) == 1 and sorted(p.name for p in aside[0].iterdir()) == ["plan_a.pdf", "plan_scan.png"]
    assert any("private self-test" in line and "stale" in line for line in r.lines)
    # A current copy stays (same files, same bytes): nothing moved, nothing copied over it.
    stamp = (stale / "plan_a.pdf").stat().st_mtime_ns
    r2 = Run(tmp_path, projects=["p1"], private_selftest=True, buildings={"selftest-02": {"status": "needs_review"}})
    assert r2.run() == 0
    assert (stale / "plan_a.pdf").stat().st_mtime_ns == stamp
    assert len([p for p in (tmp_path / "outputs-archive").iterdir() if p.name.startswith("selftest-02-")]) == 1
    # A changed source (same names, other bytes) replaces the copy again.
    write(source / "plan_b.pdf", "b changed")
    r3 = Run(tmp_path, projects=["p1"], private_selftest=True, buildings={"selftest-02": {"status": "needs_review"}})
    assert r3.run() == 0
    assert (stale / "plan_b.pdf").read_text() == "b changed"
    assert len([p for p in (tmp_path / "outputs-archive").iterdir() if p.name.startswith("selftest-02-")]) == 2


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
    # An earlier ok run of the alias left an ok intake manifest and a staged copy; the upload is gone now.
    write(tmp_path / "po" / "real-02" / "intake_manifest.json", {"status": "ok", "reasons": []})
    write(tmp_path / "po" / "real-02" / "input" / "real-02" / "plan.dxf", "old")
    r = Run(tmp_path, {"p1": {}}, projects=["p1"], private=["real-02"])
    assert r.run() == 0
    rec = r.record("real-02", "intake", root="po")
    assert rec["status"] == "needs_review" and rec["note"] == "not uploaded"
    # IE-2: the intake CLI runs anyway, so the old ok manifest and staged copy are replaced (the report then says
    # needs_review instead of showing the old renders as an ok report).
    assert r.cli.find("intake", "real-02") and not r.cli.find("pipeline", "real-02")
    manifest = json.loads((tmp_path / "po" / "real-02" / "intake_manifest.json").read_text())
    assert manifest["status"] == "needs_review" and manifest["reasons"] == ["not uploaded"]
    assert not (tmp_path / "po" / "real-02" / "input" / "real-02").exists()
    assert json.loads((tmp_path / "po" / "real-02" / "final" / "final_manifest.json").read_text())["status"] == \
        "needs_review"
    assert r.servers.starts == ["qwen", "qwen", "glm"]


def test_intake_fingerprint_is_the_upload_listing_never_its_bytes(tmp_path, monkeypatch):
    """IE-6: the orchestrator never reads the raw upload (GBs of skipped files): the intake's fingerprint is the
    upload's listing (path, size, mtime); a changed file is still seen through its size or mtime."""
    import wenart.canonical as CN
    upload = tmp_path / "pp" / "real-01"
    write(upload / "plan.dxf", "x" * 100)
    write(upload / "renders" / "video.mp4", b"\0" * 4096)
    read: list = []
    real = CN._file_sha256
    monkeypatch.setattr(CN, "_file_sha256", lambda p: read.append(Path(p)) or real(p))
    r = Run(tmp_path, {"p1": {}}, private=["real-01"])
    assert r.run() == 0
    assert not [p for p in read if upload in p.parents], read
    rec = r.record("real-01", "intake", root="po")
    assert rec["inputs"] == {str(upload): ST.listing_sha256(upload)} and rec["status"] == "ok"
    # Unchanged upload: reused. Same size, other mtime: run again.
    r2 = Run(tmp_path, private=["real-01"])
    r2.run()
    assert r2.record("real-01", "intake", root="po")["status"] == "reused"
    os.utime(upload / "plan.dxf", ns=(1_000_000_000, 1_000_000_000))
    r3 = Run(tmp_path, private=["real-01"])
    r3.run()
    assert r3.record("real-01", "intake", root="po")["status"] == "ok" and r3.cli.find("intake")


def test_intake_collision_is_needs_review(tmp_path):
    r = Run(tmp_path, {"p1": {}}, private=["real-03"], flags={"intake": {"real-03": "needs_review"}})
    write(tmp_path / "pp" / "real-03" / "a.dxf", "x")
    assert r.run() == 0
    rec = r.record("real-03", "intake", root="po")
    assert rec["status"] == "needs_review" and rec["note"] == "document name collision"


def test_intake_exit_4_is_needs_review_and_only_fixed_reasons_are_recorded(tmp_path):
    # Exit 4 of wenart.intake is needs_review even without a readable manifest.
    r = Run(tmp_path, {"p1": {}}, private=["real-04"], flags={"intake": {"real-04": "no_manifest"}})
    write(tmp_path / "pp" / "real-04" / "a.dxf", "x")
    assert r.run() == 0
    rec = r.record("real-04", "intake", root="po")
    assert rec["status"] == "needs_review" and rec["note"] == "needs review (intake_manifest.json)"
    assert not r.cli.find("pipeline", "real-04")
    # Another fixed intake reason is recorded as it is; a reason that is not one of them never is.
    r = Run(tmp_path / "b", {"p1": {}}, private=["real-05", "real-06"],
            flags={"intake": {"real-05": "needs_review", "real-06": "needs_review"},
                   "intake_reasons": {"real-05": ["no document in the upload (only skipped files)"],
                                      "real-06": ["Yilmaz villa.dxf is broken"]}})
    write(tmp_path / "b" / "pp" / "real-05" / "a.txt", "x")
    write(tmp_path / "b" / "pp" / "real-06" / "a.dxf", "x")
    assert r.run() == 0
    assert r.record("real-05", "intake", root="po")["note"] == "no document in the upload (only skipped files)"
    assert r.record("real-06", "intake", root="po")["note"] == "needs review (intake_manifest.json)"


def test_orchestrator_traceback_goes_to_the_private_log(tmp_path):
    r = Run(tmp_path, {"p1": {}}, projects=["p1"], private=["real-01"])
    write(tmp_path / "pp" / "real-01" / "a.dxf", "x")

    def broken(cmd, env, cwd, timeout, log_path):
        if "wenart.furniture.decor_ai" in cmd:
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


def test_results_are_copied_before_the_gpu_tests(tmp_path, monkeypatch):
    # tests/gpu/test_full_run.py reads the private allow-list under results-private/<alias>/ in phase 11; the
    # job's copy loop runs only every 300 s, so the orchestrator copies once before the tests (under the lock).
    monkeypatch.setenv("WENART_COPY_LOCK", str(tmp_path / "logs" / "copy.lock"))
    seen = {}

    def runner(cmd, env, cwd, timeout, log_path):
        if "pytest" in cmd:
            seen["files"] = sorted(p.relative_to(tmp_path / "pr").as_posix()
                                   for p in (tmp_path / "pr").rglob("*") if p.is_file())
        return r.cli(cmd, env, cwd, timeout, log_path)

    fixture_project(make_repo(tmp_path, {"p1": {}}))
    r = Run(tmp_path, projects=["p1"], private_selftest=True, buildings={"selftest-02": {"status": "needs_review"}})
    rc = SC.Orchestrator(r.opts, runner=runner, clock=r.clock, server_factory=r.servers, out=r.lines.append,
                         control_views=lambda rm, s, n: [c["name"] for c in s["cameras"]][:n],
                         gpu_mem=lambda: 32607, check_models=MODELS).run()
    assert rc in (0, 1)
    assert "selftest-02/final/final_report.md" in seen["files"]
    assert any(f.startswith("selftest-02/run/") for f in seen["files"])
    assert any(re.fullmatch(r"copy: \d+ public file\(s\), \d+ private file\(s\) \(full copy\)", ln) for ln in r.lines)
    assert (tmp_path / "logs" / "copy.lock").is_file()


def test_layout_deadline_estimate_counts_its_calls_one_at_a_time(tmp_path):
    # The layout CLI sends its 2 passes per room one after the other: 2 x 4.4 s for one empty room, never
    # divided by the server's sequences (2 here), so 6 s before the deadline it does not start.
    probe = Run(tmp_path / "probe", {"p1": {}}, projects=["p1"])
    probe.run()
    t_layout = next(c["t"] for c in probe.cli.calls if c["name"] == "layout") - probe.cli.calls[0]["t"]
    r = Run(tmp_path / "tight", {"p1": {}}, projects=["p1"], deadline_in=t_layout + 6.0 + 1.0)
    assert r.run() == 1
    rec = r.record("p1", "layout")
    assert rec["status"] == "incomplete" and rec["note"] == "deadline: layout not started"
    assert not r.cli.find("layout")


# --------------------------------------------------------------------------
# Review fixes (M6 review: R1/V1, R3, R4, R5, R6, IE-4, pre-M6 outputs)
# --------------------------------------------------------------------------

def test_judge_without_ab_controls_keeps_the_render_pods_control_sets(tmp_path):
    """R1/V1: a judge pod without AB_CONTROL_PROJECT must neither rebuild ab/pairs_v2.json without the control
    sets nor run the summary without the control project."""
    Run(tmp_path, {"p1": {}, "p3": {}}, projects=["p1", "p3"], ab=["p1", "p3"], ab_controls="p1",
        ab_phase="render").run()
    pairs = tmp_path / "outputs" / "p1" / "ab" / "pairs_v2.json"
    before = pairs.read_text()
    assert json.loads(before)["controls"] is True
    r = Run(tmp_path, ab=["p1", "p3"], ab_phase="judge")
    assert r.run() == 0
    assert not r.cli.find("realism2-pairs")                      # judge reuses the render pod's complete files
    assert pairs.read_text() == before
    for p in ("p1", "p3"):
        rec = r.record(p, "ab_pairs")
        assert rec["status"] == "reused" and rec["note"].startswith("ab/pairs_v2.json of the render pod"), rec
    assert [opt(c["cmd"], "--model-key") for c in r.cli.find("realism2", "p1")] == ["qwen", "glm"]
    assert opt(r.cli.find("realism2-summary")[0]["cmd"], "--controls-project") == str(tmp_path / "outputs" / "p1")
    m = r.manifest()
    assert m["ab_controls"] == "p1" and {a["name"]: a["controls"] for a in m["ab"]} == {"p1": True, "p3": False}
    assert any(line.startswith("A/B controls: p1") for line in r.lines)
    assert m["test_lists"]["AB_TEST_PROJECTS"] == "p1 p3" and m["test_lists"]["AB_CONTROL_PROJECT"] == "p1"


def test_judge_refuses_two_control_projects_without_ab_controls(tmp_path):
    make_repo(tmp_path, {"p1": {}, "p3": {}})
    for p in ("p1", "p3"):
        (tmp_path / "outputs" / p / "run").mkdir(parents=True)
        write(tmp_path / "outputs" / p / "ab" / "control_views.json", {"views": ["cam_a_1"]})
    r = Run(tmp_path, ab=["p1", "p3"], ab_phase="judge")
    lines = []
    assert SC.run_pod(r.opts, out=lines.append, runner=r.cli, clock=r.clock, server_factory=r.servers,
                      check_models=MODELS) == 2
    assert "p1, p3" in lines[-1] and "--ab-controls" in lines[-1]
    assert not r.cli.calls
    # --ab-controls decides.
    r2 = Run(tmp_path, ab=["p1", "p3"], ab_phase="judge", ab_controls="p3")
    orch = SC.Orchestrator(r2.opts, runner=r2.cli, clock=r2.clock, server_factory=r2.servers,
                           out=r2.lines.append, check_models=MODELS)
    orch.setup()
    assert orch.ab_controls == "p3"


def test_a_pairs_rebuild_never_drops_stored_control_sets(tmp_path):
    Run(tmp_path, {"p1": {}}, ab=["p1"], ab_controls="p1", ab_phase="render").run()
    # A second render pod without --ab-controls rebuilds the pairs: the control sets stay.
    r = Run(tmp_path, ab=["p1"], ab_phase="render")
    r.run()
    assert "--controls" in r.cli.find("realism2-pairs", "p1")[0]["cmd"]
    assert json.loads((tmp_path / "outputs" / "p1" / "ab" / "pairs_v2.json").read_text())["controls"] is True
    # Judge with a pairs file whose image is gone: rebuilt (with the control sets).
    (tmp_path / "outputs" / "p1" / "ab" / "fake" / "ctl_flat_c0_a.jpg").unlink()
    r2 = Run(tmp_path, ab=["p1"], ab_phase="judge")
    assert r2.run() == 0
    assert "--controls" in r2.cli.find("realism2-pairs", "p1")[0]["cmd"]
    assert r2.record("p1", "ab_pairs")["status"] == "ok"
    # Judge of the control project whose render pod wrote no control sets: rebuilt with them.
    tmp2 = tmp_path / "b"
    tmp2.mkdir()
    Run(tmp2, {"p1": {}}, projects=["p1"], ab=["p1"], ab_phase="render").run()
    r3 = Run(tmp2, ab=["p1"], ab_controls="p1", ab_phase="judge")
    r3.run()
    assert "--controls" in r3.cli.find("realism2-pairs", "p1")[0]["cmd"]
    # A stored file made over other look_alt projects is rebuilt in the judge phase.
    stored = json.loads((tmp2 / "outputs" / "p1" / "ab" / "pairs_v2.json").read_text())
    assert stored["look_alt"]["projects"] == ["p1"]
    assert not SC.Orchestrator.pairs_complete(r3.orch.ab_runs[0], stored, True, [tmp2 / "outputs" / "px"])


def test_ab_records_never_decide_the_state_of_a_project_also_in_projects(tmp_path):
    """R3: a failed A/B stage fails the run (exit 1) but not the project's state."""
    r = Run(tmp_path, {"p1": {}}, projects=["p1"], ab=["p1"], ab_controls="p1",
            rc={"realism2": lambda cli: 1 if opt(cli.calls[-1]["cmd"], "--model-key") == "glm" else 0})
    assert r.run() == 1
    assert r.record("p1", "ab_realism")["status"] == "failed"
    m = r.manifest()
    assert m["projects"][0]["state"] == "ok" and m["test_lists"]["RUN_TEST_PROJECTS"] == "p1"
    assert m["test_lists"]["RENDER_TEST_PROJECTS"] == "p1" and m["test_lists"]["POLISH_TEST_PROJECTS"] == "p1"
    assert m["test_lists"]["AB_TEST_PROJECTS"] == ""
    tmp2 = tmp_path / "b"
    tmp2.mkdir()
    r2 = Run(tmp2, {"p1": {}}, projects=["p1"], ab=["p1"], ab_controls="p1", rc={"realism2-pairs": 1})
    assert r2.run() == 1                                     # the A/B failed ...
    assert r2.manifest()["projects"][0]["state"] == "ok"      # ... the project did not
    assert r2.manifest()["test_lists"]["RUN_TEST_PROJECTS"] == "p1"


def test_gate_calibration_reused_on_resume_when_nothing_changed(tmp_path):
    """R4: a complete calibration of the same renders, controls and gate code is reused; it is never moved aside
    when calibrate did not run."""
    r = Run(tmp_path, {"p1": {}}, projects=["p1"])
    assert r.run() == 0
    gate = tmp_path / "outputs" / "p1" / "gate"
    # A resumed pod (the renders are reused: another deadline in the render manifest). A calibrate that ran
    # would crash here and move the calibration aside.
    r2 = Run(tmp_path, projects=["p1"], rc={"gate calibrate": 1})
    assert r2.run() == 0
    assert not r2.cli.find("gate calibrate") and r2.cli.find("gate validate") and r2.cli.find("polish")
    rec = r2.record("p1", "gate")
    assert rec["status"] == "ok" and rec["note"] == "gate decision ok (calibration reused)"
    assert rec["steps"][0] == {"name": "calibrate", "rc": 0, "seconds": 0.0, "reused": True}
    assert (gate / "gate_calibration.json").is_file() and not (gate / "gate_calibration.failed.json").exists()
    assert r2.manifest()["test_lists"]["GATE_TEST_PROJECTS"] == "p1"
    # Other renders (render_key) -> calibrated again.
    r3 = Run(tmp_path, projects=["p1"], flags={"render_key": {"p1": "k2"}})
    assert r3.run() == 0
    assert len(r3.cli.find("gate calibrate")) == 1 and r3.record("p1", "gate")["note"] == "gate decision ok"
    # --force gate -> calibrated again.
    r4 = Run(tmp_path, projects=["p1"], flags={"render_key": {"p1": "k2"}}, force=frozenset({"gate"}))
    r4.run()
    assert len(r4.cli.find("gate calibrate")) == 1
    # A calibration the deadline cut is never reused.
    tmp2 = tmp_path / "cut"
    tmp2.mkdir()
    Run(tmp2, {"p1": {}}, projects=["p1"], flags={"gate_cut": ("p1",)}).run()
    r5 = Run(tmp2, projects=["p1"])
    assert r5.run() == 0 and len(r5.cli.find("gate calibrate")) == 1


def test_failed_model_downloads_are_a_warning_and_never_reused(tmp_path):
    """R5: fit exits 0 with a parametric fallback when a model download fails; the stage is a warning and the
    next run fits (and downloads) again instead of reusing the fallback."""
    r = Run(tmp_path, {"p1": {}}, projects=["p1"], flags={"download_fail": ("p1",)})
    assert r.run() == 0
    assert r.record("p1", "fit")["status"] == "warning"
    assert r.record("p1", "fit")["note"] == "1 model download(s) failed: parametric fallback"
    assert r.record("p1", "refit")["status"] == "warning"
    assert r.record("p1", "refit")["note"].endswith("model download(s) failed: parametric fallback")
    assert r.manifest()["projects"][0]["state"] == "ok"
    r2 = Run(tmp_path, projects=["p1"])                     # the asset host is back
    assert r2.run() == 0
    assert len(r2.cli.find("fit")) == 1 and len(r2.cli.find("refit")) == 1
    assert r2.record("p1", "fit")["status"] == "ok" and r2.record("p1", "refit")["status"] == "ok"
    r3 = Run(tmp_path, projects=["p1"])
    r3.run()
    assert r3.record("p1", "fit")["status"] == "reused" and r3.record("p1", "refit")["status"] == "reused"


def test_a_cut_check_run_is_not_hidden_by_the_preference_after_it(tmp_path):
    """R6: run writes incomplete: true, the preference after it (nothing to ask) rewrites the same answers file
    with incomplete: false; the check still ends incomplete."""
    r = Run(tmp_path, {"p1": {}}, projects=["p1"], flags={"run_cut": {("p1", "glm")}})
    assert r.run() == 1
    rec = r.record("p1", "check")
    assert rec["status"] == "incomplete" and rec["note"] == "deadline: glm answers incomplete"
    answers = tmp_path / "outputs" / "p1" / "check" / "answers_glm-4.6v-flash.json"
    assert json.loads(answers.read_text())["incomplete"] is False
    # A private project (no style-photo step) too.
    tmp2 = tmp_path / "private"
    tmp2.mkdir()
    r2 = Run(tmp2, {"p1": {}}, private=["real-01"], flags={"run_cut": {("real-01", "qwen")}})
    write(tmp2 / "pp" / "real-01" / "a.dxf", "x")
    assert r2.run() == 1
    assert r2.record("real-01", "check", root="po")["status"] == "incomplete"


def test_report_of_a_project_cut_before_its_first_render_keeps_it_incomplete(tmp_path):
    """IE-4: the deadline stops the build; the report has nothing to report (exit 1, render not_run): a warning,
    the project stays incomplete (resumed with the same command), never failed."""
    # pipeline 5 + fit 1 + style 1 + Qwen start 300 + layout 40 + assets/decor/refit 3 = 350; the build needs 60.
    r = Run(tmp_path, {"p1": {}}, projects=["p1"], deadline_in=380)
    assert r.run() == 1
    assert r.record("p1", "build")["note"] == "deadline: build not started"
    rec = r.record("p1", "report")
    assert rec["status"] == "warning" and rec["note"] == "no renders in this run" and rec["rc"] == 1
    assert r.manifest()["projects"][0]["state"] == "incomplete"
    # A report that fails for an ok project stays a failure.
    tmp2 = tmp_path / "b"
    tmp2.mkdir()
    r2 = Run(tmp2, {"p1": {}}, projects=["p1"], rc={"report": 1})
    assert r2.run() == 1
    assert r2.record("p1", "report")["status"] == "failed" and r2.manifest()["projects"][0]["state"] == "failed"


def test_outputs_of_an_earlier_job_are_moved_aside_never_deleted(tmp_path, monkeypatch):
    """§2.3: an out_dir without run/ (the M5 polish.sh outputs on the volume) is renamed to
    <archive root>/<name>-<UTC stamp> before the project starts; private out_dirs never are."""
    monkeypatch.delenv("WENART_OUTPUTS_ARCHIVE", raising=False)
    old = tmp_path / "outputs"
    write(old / "p1" / "renders" / "cam_r_L0_hol_3_preview.jpg", b"m5")
    write(old / "p1" / "polish" / "polish_manifest.json", {"views": []})
    write(old / "p2" / "ab" / "pairs.json", {"pairs": []})                    # an A/B-only project
    write(tmp_path / "po" / "real-01" / "notes.txt", "private")                 # a private out_dir: kept as is
    r = Run(tmp_path, {"p1": {}, "p2": {}, "p3": {}}, projects=["p1"], ab=["p2"], ab_controls="p2",
            private=["real-01"])
    assert r.run() == 0
    archive = tmp_path / "outputs-archive"
    moved = {p.name.split("-", 1)[0]: p for p in archive.iterdir()}
    assert set(moved) == {"p1", "p2"}
    assert all(re.fullmatch(r"p[12]-\d{8}T\d{6}Z", p.name) for p in moved.values())
    assert (moved["p1"] / "renders" / "cam_r_L0_hol_3_preview.jpg").read_bytes() == b"m5"
    assert (moved["p1"] / "polish" / "polish_manifest.json").is_file()
    assert not (old / "p1" / "renders" / "cam_r_L0_hol_3_preview.jpg").exists() and (old / "p1" / "run").is_dir()
    assert (tmp_path / "po" / "real-01" / "notes.txt").is_file()
    note = f"earlier outputs without run records moved to {moved['p1']}"
    assert r.record("p1", "sheets")["note"] == note           # the project's first stage of the run (Milestone 10)
    assert r.record("p1", "intake")["note"] == "private only"                 # a skip keeps its reason
    assert r.record("p2", "pipeline")["note"] == f"earlier outputs without run records moved to {moved['p2']}"
    m = r.manifest()
    entries = {p["name"]: p for p in m["projects"]}
    assert entries["p1"]["archived_outputs"] == str(moved["p1"]) and "archived_outputs" not in entries["real-01"]
    assert {a["name"]: a.get("archived_outputs") for a in m["ab"]} == {"p2": str(moved["p2"])}
    assert f"p1: {note}" in r.lines
    # A later run finds run/ and moves nothing; WENART_OUTPUTS_ARCHIVE sets the archive root.
    monkeypatch.setenv("WENART_OUTPUTS_ARCHIVE", str(tmp_path / "elsewhere"))
    write(old / "p3" / "renders" / "x.jpg", b"x")
    r2 = Run(tmp_path, projects=["p1", "p3"], ab=["p2"], ab_controls="p2")
    r2.run()
    assert len(list(archive.iterdir())) == 2 and "archived_outputs" not in r2.manifest()["projects"][0]
    assert [p.name.split("-", 1)[0] for p in (tmp_path / "elsewhere").iterdir()] == ["p3"]


# --------------------------------------------------------------------------
# Milestone 7: recognition, pipeline_final, detect, vLLM tiers, GPU speed (docs/milestone7.md §9)
# --------------------------------------------------------------------------

def test_questions_pending_recognize_then_pipeline_final_then_fit(tmp_path):
    r = Run(tmp_path, {"p1": {}}, buildings={"p1": {"questions": 3}}, projects=["p1"])
    assert r.run() == 0
    names = r.cli.names("p1")
    # Phase 1: the pipeline exits 4 (pending), no fit yet; GLM pass (phase 2), Qwen pass, pipeline_final, fit
    # (phase 3), then the layout in the same Qwen session.
    order = ["pipeline", "style", "recognize", "recognize", "pipeline_final", "fit", "layout", "assets"]
    idx = [names.index(n) if i == 0 or n != "recognize" else names.index(n, names.index(n) + 1) if i == 3
           else names.index(n) for i, n in enumerate(order)]
    assert idx == sorted(idx), names
    assert names.index("fit") > names.index("pipeline_final")
    assert r.servers.starts == ["glm", "qwen", "qwen", "glm"]       # <= 4 starts (§9.1)
    asks = r.cli.find("recognize", "p1")
    assert [opt(c["cmd"], "--model-key") for c in asks] == ["glm", "qwen"]
    for c in asks:
        assert c["cmd"][:5] == ["PY", "-m", "wenart.recognition.answers", "ask",
                                str(tmp_path / "outputs" / "p1" / "recognition")]
        assert opt(c["cmd"], "--workers") == "2" and opt(c["cmd"], "--server").startswith("http://fake-")
        assert "--seed-answers" not in c["cmd"]                     # no results/recognition/p1/ in this repo
    final = r.cli.find("pipeline_final", "p1")[0]["cmd"]
    assert opt(final, "--answers") == str(tmp_path / "outputs" / "p1" / "recognition") and "--no-ai" not in final
    rec = r.record("p1", "pipeline")
    assert rec["status"] == "pending" and rec["note"].startswith("3 recognition question(s)") and rec["rc"] == 4
    assert r.record("p1", "recognize")["status"] == "ok"
    assert [s["name"] for s in r.record("p1", "recognize")["steps"]] == ["ask glm", "ask qwen"]
    pf = r.record("p1", "pipeline_final")
    assert pf["status"] == "ok" and pf["note"] == "answers applied"
    assert pf["written"]["building.json"] == ST.canonical_sha256(tmp_path / "outputs" / "p1" / "building.json")
    assert {Path(k).name for k in pf["inputs"]} >= {"p1", "answers_qwen3-vl-8b.json", "answers_glm-4.6v-flash.json"}
    assert json.loads((tmp_path / "outputs" / "p1" / "building_fitted.json").read_text())["stage"] == "final"
    assert r.manifest()["projects"][0]["state"] == "ok"
    # A project without questions skips both new stages.
    tmp2 = tmp_path / "b"
    tmp2.mkdir()
    r2 = Run(tmp2, {"p1": {}}, projects=["p1"])
    assert r2.run() == 0
    for stage in ("recognize", "pipeline_final"):
        assert r2.record("p1", stage)["status"] == "skipped" and r2.record("p1", stage)["note"] == "no questions"


def test_resume_reuses_the_pending_pipeline_and_the_final_building(tmp_path):
    r = Run(tmp_path, {"p1": {}}, buildings={"p1": {"questions": 2}}, projects=["p1"])
    assert r.run() == 0
    final_building = (tmp_path / "outputs" / "p1" / "building.json").read_text()
    r2 = Run(tmp_path, buildings={"p1": {"questions": 2}}, projects=["p1"])
    assert r2.run() == 0
    # The pending pipeline is reused as pending (it never overwrites the final building); the stored answers
    # complete both passes, so no recognition server; pipeline_final and the stages after it are reused.
    assert not r2.cli.find("pipeline") and not r2.cli.find("pipeline_final")
    assert r2.record("p1", "pipeline")["status"] == "pending"
    assert r2.record("p1", "pipeline")["note"].startswith("reused: 2 recognition question(s)")
    assert [s["name"] for s in r2.record("p1", "recognize")["steps"]] == ["stored answers qwen", "stored answers glm"]
    assert all("--server" not in c["cmd"] for c in r2.cli.find("recognize"))
    assert r2.record("p1", "recognize")["status"] == "reused"
    for stage in ("pipeline_final", "fit", "layout", "decor", "refit"):
        assert r2.record("p1", stage)["status"] == "reused", stage
    assert (tmp_path / "outputs" / "p1" / "building.json").read_text() == final_building
    assert r2.servers.starts == ["qwen", "glm"]                      # the check sessions only
    # A changed project: the first pipeline runs again (pre-answer building), the answers are reused by key and
    # hash, pipeline_final runs again because the building is not the one it wrote.
    (tmp_path / "repo" / "projects" / "p1" / "plan.dxf").write_text("changed", encoding="utf-8")
    r3 = Run(tmp_path, buildings={"p1": {"questions": 2}}, projects=["p1"])
    assert r3.run() == 0
    assert len(r3.cli.find("pipeline")) == 1 and len(r3.cli.find("pipeline_final")) == 1
    assert r3.record("p1", "pipeline_final")["status"] == "ok"
    assert r3.servers.starts == ["qwen", "glm"]


def test_committed_answers_seed_the_recognition_without_a_server(tmp_path):
    make_repo(tmp_path, {"p1": {}})
    probe = Run(tmp_path / "probe", {"p1": {}}, buildings={"p1": {"questions": 2}}, projects=["p1"])
    probe.run()
    seeds = tmp_path / "repo" / "results" / "recognition" / "p1"
    for slug in ("qwen3-vl-8b", "glm-4.6v-flash"):
        write(seeds / f"answers_{slug}.json", (tmp_path / "probe" / "outputs" / "p1" / "recognition" /
                                               f"answers_{slug}.json").read_text())
    r = Run(tmp_path, buildings={"p1": {"questions": 2}}, projects=["p1"])
    assert r.run() == 0
    assert r.servers.starts == ["qwen", "qwen", "glm"]               # layout + checks: no recognition session
    calls = r.cli.find("recognize", "p1")
    assert [opt(c["cmd"], "--model-key") for c in calls] == ["qwen", "glm"]
    seed_dir = str(tmp_path / "repo" / "results" / "recognition" / "p1")   # absolute: the fake repo is not the repo
    assert all(opt(c["cmd"], "--seed-answers") == seed_dir and "--server" not in c["cmd"] for c in calls)
    assert "--no-ai" not in r.cli.find("pipeline_final")[0]["cmd"]
    # Seeds that answer only part of the questions: the GLM session asks the rest (with the seeds).
    tmp2 = tmp_path / "partial"
    make_repo(tmp2, {"p1": {}})
    seed = json.loads((tmp_path / "probe" / "outputs" / "p1" / "recognition" / "answers_glm-4.6v-flash.json")
                      .read_text())
    seed["calls"] = dict(list(seed["calls"].items())[:1])
    write(tmp2 / "repo" / "results" / "recognition" / "p1" / "answers_glm-4.6v-flash.json", seed)
    r2 = Run(tmp2, buildings={"p1": {"questions": 2}}, projects=["p1"])
    assert r2.run() == 0
    assert r2.servers.starts == ["glm", "qwen", "qwen", "glm"]
    glm = r2.cli.find("recognize", "p1")[0]["cmd"]
    assert opt(glm, "--server") and opt(glm, "--seed-answers") == str(tmp2 / "repo" / "results" / "recognition" / "p1")


def test_recognition_failure_is_a_warning_and_pipeline_final_runs_with_no_ai(tmp_path):
    r = Run(tmp_path, {"p1": {}}, buildings={"p1": {"questions": 2}}, projects=["p1"],
            flags={"recog_fail": {("p1", "glm")}})
    assert r.run() == 0
    rec = r.record("p1", "recognize")
    assert rec["status"] == "warning" and "recognition glm exit 2" in rec["note"]
    final = r.cli.find("pipeline_final")[0]["cmd"]
    assert "--no-ai" in final and opt(final, "--answers")
    assert r.record("p1", "pipeline_final")["note"].startswith("--no-ai")
    assert r.manifest()["projects"][0]["state"] == "ok"
    # A server that never starts: the same, with the server's reason.
    tmp2 = tmp_path / "b"
    tmp2.mkdir()
    r2 = Run(tmp2, {"p1": {}}, buildings={"p1": {"questions": 2}}, projects=["p1"], fail={"glm": "early_exit"})
    assert r2.run() == 1                                    # the GLM check session fails too
    rec = r2.record("p1", "recognize")
    assert rec["status"] == "warning" and "server glm: early_exit" in rec["note"]
    assert "--no-ai" in r2.cli.find("pipeline_final")[0]["cmd"]


def test_recognition_cut_by_the_deadline_leaves_the_project_incomplete(tmp_path):
    r = Run(tmp_path, {"p1": {}}, buildings={"p1": {"questions": 4}}, projects=["p1"],
            flags={"recog_cut": {("p1", "glm")}}, deadline_in=100_000)
    assert r.run() == 1
    assert r.record("p1", "recognize")["status"] == "incomplete"
    assert not r.cli.find("pipeline_final") and not r.cli.find("fit") and r.cli.find("report")
    assert r.manifest()["projects"][0]["state"] == "incomplete"
    # No time for the GLM server at all.
    tmp2 = tmp_path / "b"
    tmp2.mkdir()
    r2 = Run(tmp2, {"p1": {}}, buildings={"p1": {"questions": 4}}, projects=["p1"], deadline_in=100)
    assert r2.run() == 1
    assert r2.servers.starts == [] and r2.record("p1", "recognize")["status"] == "incomplete"
    assert "glm server not started" in r2.record("p1", "recognize")["note"]
    # A pending pipeline without a finished pipeline_final of the run is incomplete (state rule).
    assert ST.project_state([ST.StageRecord("p", "pipeline", "pending")]) == "incomplete"


def test_pipeline_final_needs_review_makes_the_project_needs_review(tmp_path):
    r = Run(tmp_path, {"p1": {}}, buildings={"p1": {"questions": 1, "final_status": "needs_review"}},
            projects=["p1"])
    assert r.run() == 0
    assert r.record("p1", "pipeline_final")["status"] == "needs_review"
    assert "fit" not in r.cli.names("p1") and "report" in r.cli.names("p1")
    assert r.manifest()["projects"][0]["state"] == "needs_review"
    assert r.manifest()["test_lists"]["NEEDS_REVIEW_TEST_PROJECTS"] == "p1"


def test_pipeline_final_exit_4_runs_again_with_no_ai_and_is_a_warning(tmp_path):
    """Second-round questions (the answers opened new ones): pipeline_final exits 4 although every answer was in.
    Never failed: it runs once more with --no-ai (the new items stay unknown/unverified) and is a warning; the
    project goes on (fit, layout, render, ...)."""
    r = Run(tmp_path, {"p1": {}}, buildings={"p1": {"questions": 2}}, projects=["p1"],
            flags={"second_round": {"p1"}})
    assert r.run() == 0
    finals = r.cli.find("pipeline_final", "p1")
    assert len(finals) == 2
    assert "--no-ai" not in finals[0]["cmd"] and opt(finals[0]["cmd"], "--answers")
    assert finals[1]["cmd"] == finals[0]["cmd"] + ["--no-ai"]
    rec = r.record("p1", "pipeline_final")
    assert rec["status"] == "warning" and rec["note"] == "second-round questions left unanswered (no-ai)"
    assert [s["name"] for s in rec["steps"]] == ["pipeline_final", "pipeline_final --no-ai"]
    out = tmp_path / "outputs" / "p1"
    assert json.loads((out / "building.json").read_text())["no_ai"] is True
    assert rec["written"]["building.json"] == ST.canonical_sha256(out / "building.json")
    names = r.cli.names("p1")
    assert names.index("fit") > names.index("pipeline_final") and "render" in names and "report" in names
    assert r.manifest()["projects"][0]["state"] == "ok"


def test_the_gpu_full_run_test_accepts_a_second_round_warning(tmp_path):
    """orch-1: tests/gpu/test_full_run.py::test_pending_pipeline_has_its_final_building (phase 11 on the pod) must
    accept the second-round warning of pipeline_final (it used to demand ok or reused, so a pod whose raster
    answers opened new questions failed its GPU tests); any other warning stays refused."""
    import subprocess
    import sys
    r = Run(tmp_path, {"p1": {}}, buildings={"p1": {"questions": 2}}, projects=["p1"],
            flags={"second_round": {"p1"}})
    assert r.run() == 0
    repo = Path(__file__).resolve().parents[1]
    env = dict(os.environ, WENART_RESULTS=str(tmp_path / "results"), WENART_OUTPUTS=str(tmp_path / "outputs"),
               RUN_TEST_PROJECTS="p1", NEEDS_REVIEW_TEST_PROJECTS="", SELFTEST_TEST_ALIAS="")

    def gpu_test() -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-m", "pytest", "-m", "gpu", "tests/gpu/test_full_run.py", "-k",
                               "test_pending_pipeline_has_its_final_building", "-p", "no:cacheprovider", "-q", "-s"],
                              cwd=repo, env=env, capture_output=True, text=True, timeout=300)

    proc = gpu_test()
    assert proc.returncode == 0 and "1 passed" in proc.stdout, proc.stdout + proc.stderr
    assert "p1 warning pipeline_final: second-round questions left unanswered (no-ai)" in proc.stdout
    # Another pipeline_final warning is not the second round: still refused.
    path = tmp_path / "results" / "run_manifest.json"
    doc = json.loads(path.read_text())
    stage = next(s for s in doc["projects"][0]["stages"] if s["stage"] == "pipeline_final")
    stage["note"] = "something else"
    path.write_text(json.dumps(doc))
    proc = gpu_test()
    assert proc.returncode == 1 and "1 failed" in proc.stdout, proc.stdout + proc.stderr


def test_smoke_profile_final_pipeline_has_no_ai(tmp_path):
    r = Run(tmp_path, {"p1": {}}, buildings={"p1": {"questions": 2}}, projects=["p1"], profile="smoke",
            vlm_url="http://127.0.0.1:9/v1")
    assert r.run() == 0
    final = r.cli.find("pipeline_final")[0]["cmd"]
    assert "--no-ai" in final and "--answers" not in final            # the fake server's answers would agree
    assert r.record("p1", "pipeline_final")["note"] == "smoke profile: --no-ai"
    assert [opt(c["cmd"], "--model-key") for c in r.cli.find("recognize")] == ["glm", "qwen"]
    assert all(opt(c["cmd"], "--server") and opt(c["cmd"], "--workers") == "2" for c in r.cli.find("recognize"))
    assert r.record("p1", "detect")["note"] == "smoke profile"


def test_detect_after_polish_and_its_statuses(tmp_path):
    r = Run(tmp_path, {"p1": {}, "p2": {}, "p3": {"brief": {"polish": False}}}, projects=["p1", "p2", "p3"],
            flags={"gate_decision": {"p2": "not_validated"}})
    assert r.run() == 0
    det = r.cli.find("gate detect", "p1")[0]
    o = str(tmp_path / "outputs" / "p1")
    assert det["cmd"] == ["POLISH_PY", "-m", "wenart.gate", "detect", o, "--manifest",
                          f"{o}/polish/polish_manifest.json", "--out", f"{o}/detect"]
    assert det["env"]["PYTORCH_CUDA_ALLOC_CONF"] == "expandable_segments:True"
    names = r.cli.names("p1")
    assert names.index("polish") < names.index("gate detect") < names.index("expected")
    assert r.record("p1", "detect")["status"] == "ok"
    assert r.record("p2", "detect")["note"] == "gate not validated" and r.record("p3", "detect")["note"] == "polish off"
    lists = r.manifest()["test_lists"]
    assert lists["DETECT_TEST_PROJECTS"] == "p1"
    polish_group = [c for c in r.cli.find("pytest") if c["cmd"][0] == "POLISH_PY"][0]
    assert "tests/gpu/test_detect.py" in polish_group["cmd"] and polish_group["env"]["DETECT_TEST_PROJECTS"] == "p1"
    # The calibration is the prep pod's, committed as results/detect/: deselected (and said) while it is missing.
    assert opt(polish_group["cmd"], "--deselect") == "tests/gpu/test_detect.py::test_calibration_recorded"
    assert "DETECT_CALIBRATION" not in polish_group["env"]
    assert "deselected" in [t for t in r.manifest()["tests"] if t["group"] == "polish"][0]["note"]
    write(tmp_path / "repo" / "results" / "detect" / "detector_calibration.json", {"kind": "detector_calibration"})
    r5 = Run(tmp_path, projects=["p1"], force=frozenset({"detect"}))
    r5.run()
    polish_group = [c for c in r5.cli.find("pytest") if c["cmd"][0] == "POLISH_PY"][0]
    assert "--deselect" not in polish_group["cmd"]
    assert polish_group["env"]["DETECT_CALIBRATION"] == str(tmp_path / "repo" / "results" / "detect" /
                                                             "detector_calibration.json")
    # A cut detection is incomplete; a failed one a warning (the views then keep their Cycles images).
    tmp2 = tmp_path / "cut"
    tmp2.mkdir()
    r2 = Run(tmp2, {"p1": {}}, projects=["p1"], flags={"detect_cut": ("p1",)})
    assert r2.run() == 1 and r2.record("p1", "detect")["status"] == "incomplete"
    tmp3 = tmp_path / "rc1"
    tmp3.mkdir()
    r3 = Run(tmp3, {"p1": {}}, projects=["p1"], rc={"gate detect": 1})
    assert r3.run() == 0
    assert r3.record("p1", "detect")["status"] == "warning" and r3.manifest()["projects"][0]["state"] == "ok"
    # --force detect passes --force.
    r4 = Run(tmp_path, projects=["p1"], force=frozenset({"detect"}))
    r4.run()
    assert r4.cli.find("gate detect", "p1")[0]["cmd"][-1] == "--force"


def test_check_asks_the_controls_and_refit_gets_the_style(tmp_path):
    r = Run(tmp_path, {"p1": {}}, projects=["p1"])
    assert r.run() == 0
    assert {opt(c["cmd"], "--kinds") for c in r.cli.find("check run")} == {"cycles,polished,controls"}
    refit = r.cli.find("refit")[0]["cmd"]
    assert opt(refit, "--style") == str(tmp_path / "outputs" / "p1" / "style.json")
    rec = r.record("p1", "refit")
    names = {Path(k).name for k in rec["inputs"]}
    assert {"building_decor.json", "style.json", "catalog.json", "catalog_objaverse.json"} <= names
    assert "catalog_objaverse.json" in {Path(k).name for k in r.record("p1", "fit")["inputs"]}
    # A new style re-runs refit (the library style filter, M7 §6.3).
    write(tmp_path / "outputs" / "p1" / "style.json", {"family": "industrial"})
    r2 = Run(tmp_path, projects=["p1"])

    def industrial(cmd, project, log):
        write(opt(cmd, "--out"), {"family": "industrial"})

    r2.cli.h_style = industrial
    r2.run()
    # Milestone 9: the decor reads the style too (the AI decor asks with the style text), so it runs again.
    assert r2.record("p1", "refit")["status"] == "ok" and r2.record("p1", "decor")["status"] == "ok"
    assert "style.json" in {Path(k).name for k in r2.record("p1", "decor")["inputs"]}


def test_vllm_tiers_follow_the_vram_and_max_seqs(tmp_path):
    models = {k: dict(v) for k, v in MODELS.items()}
    models["glm"]["max_seqs"] = 4
    r = Run(tmp_path, {"p1": {}}, buildings={"p1": {"questions": 2}}, projects=["p1"])
    orch = SC.Orchestrator(r.opts, runner=r.cli, clock=r.clock, server_factory=r.servers, out=r.lines.append,
                           control_views=lambda rm, s, n: [], gpu_mem=lambda: 97887, check_models=models)
    assert orch.run() == 0
    workers = {(c["name"], opt(c["cmd"], "--model-key")): opt(c["cmd"], "--workers")
               for c in r.cli.calls if opt(c["cmd"], "--workers")}
    assert workers[("check run", "qwen")] == "8" and workers[("check run", "glm")] == "4"
    assert workers[("recognize", "qwen")] == "8" and workers[("recognize", "glm")] == "4"
    assert r.manifest()["gpu"]["seqs"] == {"glm": 4, "qwen": 8}


def test_gpu_speed_scales_the_deadline_estimates(tmp_path, monkeypatch):
    from wenart.run import plan as P
    # pipeline 5 + fit 1 + style 1 + nvidia-smi 1 + Qwen start 300 + layout 40 + cpu 3 + build 30 = 381 s; the
    # render of 6 views needs (8 + 1) * 6 + 60 = 114 s at speed 1 (too late for a deadline at 460), 57 s at speed 2.
    def run(tmp, gpu):
        r = Run(tmp, {"p1": {}}, projects=["p1"], deadline_in=460, flags={"gpu": gpu})
        SC.Orchestrator(r.opts, runner=r.cli, clock=r.clock, server_factory=r.servers, out=r.lines.append,
                        control_views=lambda rm, s, n: [], check_models=MODELS).run()
        return r

    # A GPU without a measured speed counts as 1.0. The prep pod measured the RTX PRO 6000 (plan.GPU_SPEED 1.634,
    # commit b7436b9), so the unmeasured case takes its entry out for this run.
    monkeypatch.delitem(P.GPU_SPEED, "RTX PRO 6000", raising=False)
    slow = run(tmp_path / "slow", ("NVIDIA RTX PRO 6000 Blackwell Server Edition", 97887))   # not measured: 1.0
    assert not slow.cli.find("render", "p1") and slow.record("p1", "render")["status"] == "incomplete"
    assert slow.manifest()["gpu"]["speed"] == 1.0 and slow.manifest()["gpu"]["speed_of"] is None
    monkeypatch.setitem(P.GPU_SPEED, "RTX PRO 6000", 2.0)
    r = run(tmp_path / "fast", ("NVIDIA RTX PRO 6000 Blackwell Server Edition", 97887))
    assert r.cli.find("render", "p1") and len(r.cli.find("nvidia-smi")) == 1
    gpu = r.manifest()["gpu"]
    assert gpu["name"] == "NVIDIA RTX PRO 6000 Blackwell Server Edition" and gpu["speed"] == 2.0
    assert gpu["speed_of"] == "RTX PRO 6000" and gpu["memory_mib"] == 97887
    assert P.gpu_speed("NVIDIA GeForce RTX 4090")["speed"] == 1.1
    assert P.gpu_speed("NVIDIA RTX PRO 4500 Blackwell") == {"name": "NVIDIA RTX PRO 4500 Blackwell", "speed": 1.0,
                                                           "matched": "RTX PRO 4500"}
    assert P.gpu_speed(None)["speed"] == 1.0 and P.gpu_speed("NVIDIA L40S")["matched"] is None


def test_the_libredwg_version_is_in_the_pipeline_fingerprint(tmp_path, monkeypatch):
    import wenart.ingest.dwg as DWG
    monkeypatch.setattr(DWG, "libredwg_version", lambda tool=None: "0.14 d9468ae")
    r = Run(tmp_path, {"p1": {}}, projects=["p1"])
    r.run()
    assert r.record("p1", "pipeline")["inputs"]["<LibreDWG VERSION>"] == "0.14 d9468ae"
    r2 = Run(tmp_path, projects=["p1"])
    r2.run()
    assert r2.record("p1", "pipeline")["status"] == "reused"
    monkeypatch.setattr(DWG, "libredwg_version", lambda tool=None: "0.15 abcdef0")
    r3 = Run(tmp_path, projects=["p1"])
    r3.run()
    assert r3.record("p1", "pipeline")["status"] == "ok"


def test_photos_and_questions_need_at_most_four_server_starts(tmp_path):
    r = Run(tmp_path, {"p1": {"photos": ["a.jpg"]}, "p2": {}}, buildings={"p2": {"questions": 2}},
            projects=["p1", "p2"])
    assert r.run() == 0
    assert r.servers.starts == ["glm", "qwen", "qwen", "glm"]
    names = r.cli.names()
    glm_phase = [c["name"] for c in r.cli.calls if c["name"] in ("recognize", "photos read")][:2]
    assert glm_phase == ["recognize", "photos read"]                 # recognition first in each session
    assert names.index("pipeline_final") < names.index("layout")
