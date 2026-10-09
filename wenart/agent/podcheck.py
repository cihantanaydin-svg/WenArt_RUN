"""The model check of pod G1 (docs/milestone11.md §11 "to be confirmed on the model-check pod", §12 pod G1).

    python -m wenart.agent.podcheck --key agent [--mtp] [--render-scene outputs/real02/scene/scene.blend]
                                    [--planted real02] --out $RESULTS/agent_check

What, per model (``check.yaml models.<key>``), with the server started as the orchestrator starts it
(``wenart.run.servers``, sleep mode on so it can be tested):

1. start: seconds to ready, VRAM used by the server (``nvidia-smi memory.used`` before / after);
2. speed: tokens/s of one stream (512 tokens) and of 4 streams at once;
3. temperature-0 repetition: a long free-text answer; the most repeated 8-word sequence (``repetition``);
4. tool call: the planner's tool list (``tools.build_registry``), one finding to fix; the call must name a tool and
   its arguments must validate against that tool's schema;
5. structured output: the room critic's schema (``critic_vision.ROOM_SCHEMA``) on a top-down image;
6. VRAM next to Cycles: one view of an existing scene rendered by Blender while critic calls run; peak VRAM, the
   render's exit code and seconds (skipped, with the reason, when the scene is not on the volume);
7. sleep / wake: ``POST /sleep?level=1``, the VRAM after it, ``POST /wake_up``, one call after it;
8. the critic on planted errors (``plant_errors``: a bed turned 180 deg, a sofa turned to face its wall) in the
   committed real02 building (``results/furniture/<p>/building_final.json``) with the committed previews of the
   rooms: flagged when a kept finding names the planted piece;
9. ``--mtp``: the server again with ``--speculative-config '{"method":"mtp","num_speculative_tokens":5}'``:
   speed and the tool-call check (kept in the config only if both work, §11).

Every step's result goes to ``<out>/<key>.json`` (also after each step, so a cut pod keeps what it measured); the
job ``scripts/jobs/agent_check.sh`` runs it and then ``pytest -m gpu tests/gpu/test_agent.py``. Steps 1-7 and 9
need the GPU; ``plant_errors`` and ``repetition`` are pure (CPU tests).
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
import threading
import time
from collections import Counter
from pathlib import Path
from typing import Optional

from wenart.agent import critic_vision as CV
from wenart.agent import log as LG
from wenart.agent import model as M
from wenart.agent import topdown as TD
from wenart.agent import tools as TL

REPO_ROOT = Path(__file__).resolve().parents[2]
MTP_FLAGS = """--speculative-config '{"method":"mtp","num_speculative_tokens":5}'"""
LONG_PROMPT = ("Describe in detail, room by room, how you would furnish a two-storey family house with a living room, "
               "a kitchen, three bedrooms, two bathrooms and a study. Write at least 600 words.")


# --------------------------------------------------------------------------
# Pure helpers (CPU tests)
# --------------------------------------------------------------------------

def repetition(text: str, n: int = 8) -> dict:
    """The most repeated ``n``-word sequence of ``text``: ``{"ngram", "count", "looped"}`` (looped: >= 4 times)."""
    words = text.split()
    grams = Counter(tuple(words[i:i + n]) for i in range(max(0, len(words) - n + 1)))
    if not grams:
        return {"ngram": None, "count": 0, "looped": False, "words": len(words)}
    gram, count = grams.most_common(1)[0]
    return {"ngram": " ".join(gram), "count": count, "looped": count >= 4, "words": len(words)}


def plant_errors(building: dict) -> tuple[dict, list[dict]]:
    """A copy of ``building`` with a bed turned by 180 deg and a sofa turned to face the wall behind it (front + 180);
    the planted items ``[{piece_id, room_id, what}]``."""
    b = copy.deepcopy(building)
    planted = []
    for kind, what in (("bed", "bed turned 180 deg: headboard into the room"),
                       ("sofa", "sofa turned to face the wall behind it")):
        p = next((f for f in b.get("furniture") or [] if str(f.get("type", "")).startswith(kind)
                  and (f.get("footprint") or {}).get("size")), None)
        if p is None:
            continue
        fp = p["footprint"]
        fp["rotation_deg"] = (float(fp.get("rotation_deg") or 0.0) + 180.0) % 360.0
        if p.get("front_deg") is not None:
            p["front_deg"] = (float(p["front_deg"]) + 180.0) % 360.0
        planted.append({"piece_id": p["id"], "room_id": p.get("room_id"), "what": what})
    return b, planted


# --------------------------------------------------------------------------
# GPU steps
# --------------------------------------------------------------------------

def vram_used_mib() -> Optional[int]:
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=20).stdout
        return int(out.strip().splitlines()[0])
    except (OSError, ValueError, IndexError, subprocess.SubprocessError):
        return None


def speed(model: M.AgentModel, tokens: int = 512, streams: int = 1) -> dict:
    results: list = []

    def one(i):
        t0 = time.time()
        reply = model.chat([{"role": "user", "content": LONG_PROMPT}], None, call_id=f"speed-{streams}-{i}",
                           max_tokens=tokens)
        results.append((reply.usage.get("completion_tokens") or 0, time.time() - t0))

    t0 = time.time()
    threads = [threading.Thread(target=one, args=(i,)) for i in range(streams)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    wall = time.time() - t0
    total = sum(n for n, _s in results)
    return {"streams": streams, "completion_tokens": total, "seconds": round(wall, 2),
            "tokens_per_s_total": round(total / wall, 1) if wall else None,
            "tokens_per_s_per_stream": round(total / wall / max(1, streams), 1) if wall else None}


def repetition_check(model: M.AgentModel) -> dict:
    reply = model.chat([{"role": "user", "content": LONG_PROMPT}], None, call_id="repetition", max_tokens=1500)
    return dict(repetition(reply.content), finish_reason=reply.finish_reason,
                completion_tokens=reply.usage.get("completion_tokens"))


def tool_call_check(model: M.AgentModel) -> dict:
    from wenart.recognition.vlm_client import schema_errors
    from wenart.agent import prompts as P
    reg = TL.build_registry()
    finding = {"id": "c:F4:f_L0_001", "check": "F4", "severity": "major", "target": "f_L0_001", "room_id": "r_L0_salon",
               "message": "the sofa f_L0_001 faces the wall; the TV unit f_L0_003 is in front of the other wall",
               "source": "code"}
    messages = [{"role": "system", "content": P.PLANNER_SYSTEM},
                {"role": "user", "content": P.planner_task(1, [finding], [], 40, False)}]
    t0 = time.time()
    reply = model.chat(messages, reg.specs(), call_id="toolcall")
    calls = []
    for tc in reply.tool_calls:
        tool = reg.tools.get(tc.name)
        errors = [tc.error] if tc.error else (["unknown tool"] if tool is None else
                                               schema_errors(tool.parameters, tc.parsed or {}))
        calls.append({"name": tc.name, "arguments": tc.parsed, "errors": errors})
    return {"ok": bool(calls) and all(not c["errors"] for c in calls), "calls": calls, "content": reply.content[:500],
            "seconds": round(time.time() - t0, 2), "usage": reply.usage}


def structured_check(model: M.AgentModel, building: dict, room_id: str, image: Path) -> dict:
    t0 = time.time()
    res = CV.critique_room(model, building, room_id, previews=[], topdown=image, plan_crop=None,
                           code={"findings": [], "checks": []}, call_id="structured")
    return {"ok": res["error"] is None, "error": res["error"], "kept": len(res["kept"]), "dropped": len(res["dropped"]),
            "seconds": round(time.time() - t0, 2)}


def concurrent_render(model: M.AgentModel, scene: Path, out_dir: Path, building: dict, room_id: str,
                      topdown: Path, py: str) -> dict:
    if not scene.is_file():
        return {"skipped": f"no scene {scene} on the volume"}
    manifest = json.loads((scene.parent / "scene_manifest.json").read_text(encoding="utf-8"))
    cam = next((c["name"] for c in manifest.get("cameras") or [] if c.get("room_id")), None)
    if cam is None:
        return {"skipped": "no interior camera in the scene"}
    cmd = [py, "-m", "wenart.blender.cli", "render", "--scene", str(scene), "--out", str(out_dir / "render"),
           "--cameras", cam, "--samples", "128", "--res", "1920x1080", "--force"]
    peak = [vram_used_mib() or 0]
    t0 = time.time()
    proc = subprocess.Popen(cmd, cwd=str(REPO_ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    calls = []
    while proc.poll() is None:
        peak.append(vram_used_mib() or 0)
        try:
            res = structured_check(model, building, room_id, topdown)
            calls.append(res["ok"])
        except M.ModelError:
            calls.append(False)
        peak.append(vram_used_mib() or 0)
    return {"camera": cam, "render_rc": proc.returncode, "render_seconds": round(time.time() - t0, 1),
            "peak_vram_mib": max(peak), "critic_calls": len(calls), "critic_calls_ok": sum(calls)}


def sleep_wake(url: str, model: M.AgentModel) -> dict:
    from wenart.run import servers as SV
    before = vram_used_mib()
    slept = SV.server_control(url, "sleep")
    during = vram_used_mib()
    woke = SV.server_control(url, "wake")
    try:
        ok = bool(model.chat([{"role": "user", "content": "Say ok."}], None, call_id="after-wake", max_tokens=8).content)
    except M.ModelError:
        ok = False
    return {"sleep_ok": slept, "wake_ok": woke, "vram_before_mib": before, "vram_asleep_mib": during,
            "call_after_wake": ok}


def planted_critic(model: M.AgentModel, project: str, out_dir: Path) -> dict:
    src = REPO_ROOT / "results" / "furniture" / project / "building_final.json"
    renders = REPO_ROOT / "results" / "renders" / project
    if not src.is_file():
        return {"skipped": f"no {src}"}
    building = json.loads(src.read_text(encoding="utf-8"))
    planted_b, planted = plant_errors(building)
    rows = []
    for item in planted:
        rid = item["room_id"]
        topdown = TD.draw_room(planted_b, rid, out_dir / f"planted_{item['piece_id']}.png")
        previews = [(p.name[:-len("_preview.jpg")], p) for p in sorted(renders.glob(f"cam_{rid}_*_preview.jpg"))][:2]
        res = CV.critique_room(model, planted_b, rid, previews=previews, topdown=topdown, plan_crop=None,
                               code={"findings": [], "checks": []}, call_id=f"planted-{item['piece_id']}")
        flagged = [f for f in res["kept"] if f["target"] == item["piece_id"]]
        rows.append(dict(item, flagged=bool(flagged), findings=[{k: f[k] for k in ("check", "severity", "target",
                                                                                    "message")} for f in res["kept"]],
                         dropped=len(res["dropped"]), error=res["error"]))
    return {"planted": rows, "flagged": sum(r["flagged"] for r in rows), "of": len(rows)}


def run(key: str, out: Path, *, mtp: bool = False, render_scene: Optional[Path] = None,
        planted: Optional[str] = None, deadline: Optional[float] = None) -> dict:
    from wenart.run import servers as SV
    out.mkdir(parents=True, exist_ok=True)
    result: dict = {"key": key, "started_utc": LG.utc_text(time.time()), "steps": {}}
    path = out / f"{key}{'-mtp' if mtp else ''}.json"

    def save():
        LG.write_json_atomic(path, result)

    def step(name, fn):
        t0 = time.time()
        try:
            result["steps"][name] = fn()
        except Exception as exc:  # noqa: BLE001 - every step is recorded, the next one still runs
            result["steps"][name] = {"error": f"{type(exc).__name__}: {exc}"}
        result["steps"][name]["step_seconds"] = round(time.time() - t0, 1)
        save()

    mem = None
    try:
        out_q = subprocess.run(SV.NVIDIA_SMI_QUERY, capture_output=True, text=True, timeout=20).stdout
        result["gpu"], mem = SV.gpu_from_text(out_q)
    except (OSError, subprocess.SubprocessError):
        pass
    before = vram_used_mib()
    stats: list = []
    building = json.loads((REPO_ROOT / "results" / "furniture" / "synthetic-01" / "building_final.json").read_text())
    room_id = next(r["id"] for r in building["rooms"] if any(f.get("room_id") == r["id"] for f in building["furniture"]))
    topdown = TD.draw_room(building, room_id, out / f"topdown_{room_id}.png")
    try:
        with SV.server(key, deadline, stats=stats, seqs=4, mem_mib=mem, logs_dir=Path(os.environ.get(
                "WENART_LOGS", "/workspace/logs")), job_dir=Path(os.environ.get("WENART_JOB_DIR", str(out))),
                sleep_mode=True, extra_flags=MTP_FLAGS if mtp else "") as url:
            result["server"] = dict(stats[-1], vram_before_mib=before, vram_after_start_mib=vram_used_mib(), url=url)
            model = M.from_check_yaml(url, key, timeout_s=900.0)
            save()
            step("speed_1", lambda: speed(model, 512, 1))
            step("speed_4", lambda: speed(model, 512, 4))
            step("tool_call", lambda: tool_call_check(model))
            if not mtp:
                step("repetition", lambda: repetition_check(model))
                step("structured", lambda: structured_check(model, building, room_id, topdown))
                if render_scene is not None:
                    py = os.environ.get("WENART_PY") or "/workspace/venv/bin/python"
                    step("concurrent_render", lambda: concurrent_render(model, render_scene, out, building, room_id,
                                                                        topdown, py))
                step("sleep_wake", lambda: sleep_wake(url, model))
                if planted:
                    step("planted_critic", lambda: planted_critic(model, planted, out))
            result["calls"] = model.calls
    except SV.ServerError as exc:
        result["server"] = {"error": str(exc), "reason": exc.reason, "stats": stats}
    result["finished_utc"] = LG.utc_text(time.time())
    save()
    return result


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m wenart.agent.podcheck", description="M11 pod G1 model check")
    p.add_argument("--key", default="agent")
    p.add_argument("--mtp", action="store_true", help="the server with MTP speculative decoding")
    p.add_argument("--render-scene", default=None, help="scene.blend for the concurrent Cycles render")
    p.add_argument("--planted", default=None, help="project of results/furniture/<p> for the planted errors")
    p.add_argument("--out", required=True)
    p.add_argument("--deadline", type=float, default=None)
    a = p.parse_args(argv)
    deadline = a.deadline
    if deadline is None and os.environ.get("WENART_DEADLINE", "").strip():
        deadline = float(os.environ["WENART_DEADLINE"])
    res = run(a.key, Path(a.out), mtp=a.mtp, render_scene=Path(a.render_scene) if a.render_scene else None,
              planted=a.planted, deadline=deadline)
    ok = "error" not in (res.get("server") or {})
    print(f"podcheck {a.key}{' mtp' if a.mtp else ''}: server {'ok' if ok else 'FAILED'}; steps: "
          + ", ".join(f"{k}={'error' if 'error' in v else 'ok'}" for k, v in res["steps"].items()))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
