"""Infinigen side of the pod P4 test batch (docs/milestone12.md §6.4; ``growth_infinigen.py``). Runs ONLY in the
Infinigen venv (Python 3.11, ``bpy==4.2.0``, the clone of princeton-vl/infinigen at the pinned commit on the container
disk); it imports nothing from ``wenart``.

    python infinigen_driver.py check --repo R --jobs jobs.json --out check.json
        imports every matched factory (``infinigen.core.util.test_utils.import_item``), records the versions
    python infinigen_driver.py generate --repo R --jobs jobs.json [--deadline T] [--job-timeout S] [--tex-res N]
        one child process per job still to do (``one``), each with a time limit; stops starting jobs near the
        deadline; every job writes ``<folder>/result.json`` (resume: done jobs are skipped, a job that failed twice
        is not tried again)
    python infinigen_driver.py one --repo R --job job.json [--tex-res N]
        one asset: Infinigen's own ``infinigen_examples.generate_individual_assets.build_and_save_asset`` with
        ``--render none --save_blend -G --export obj`` (the documented exporter bakes the procedural materials into
        textures, docs/ExportingToExternalFileFormats.md), then the size of the exported meshes in Infinigen's Z-up
        scene (our converter checks its axes against it)

Cycles bakes on the CPU (``configure_cycles_devices`` is not called): bpy 4.2's GPU kernels predate the pod's GPU.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path

MAX_ATTEMPTS = 2


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1), encoding="utf-8")
    tmp.replace(path)


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def enter_repo(repo):
    repo = str(Path(repo).resolve())
    os.chdir(repo)                                   # the gin config folders are relative to the repo root
    if repo not in sys.path:
        sys.path.insert(0, repo)


def cmd_check(args):
    enter_repo(args.repo)
    out = {"python": sys.version.split()[0], "factories": {}}
    try:
        import bpy
        out["bpy"] = bpy.app.version_string
        from infinigen.core.util.test_utils import import_item
        import infinigen
        out["infinigen"] = getattr(infinigen, "__version__", None)
    except Exception as exc:  # noqa: BLE001 - recorded, the job goes on without Infinigen
        out["error"] = f"{type(exc).__name__}: {exc}"
        write_json(args.out, out)
        return 1
    jobs = (read_json(args.jobs) or {}).get("jobs") or []
    for dotted in sorted({j["dotted"] for j in jobs if j.get("dotted")}):
        try:
            import_item(dotted)
            out["factories"][dotted] = "ok"
        except Exception as exc:  # noqa: BLE001
            out["factories"][dotted] = f"{type(exc).__name__}: {exc}"
    write_json(args.out, out)
    return 0 if all(v == "ok" for v in out["factories"].values()) else 1


def scene_dims():
    """Size of the visible mesh objects after the export (world box, Z up)."""
    import bpy
    lo, hi, n = [1e30] * 3, [-1e30] * 3, 0
    for ob in bpy.data.objects:
        if ob.type != "MESH" or ob.hide_viewport or not len(ob.data.vertices):
            continue
        mw = ob.matrix_world
        for v in ob.data.vertices:
            w = mw @ v.co
            for i in range(3):
                lo[i], hi[i] = min(lo[i], w[i]), max(hi[i], w[i])
        n += 1
    if not n:
        return None, 0
    return [round(hi[i] - lo[i], 4) for i in range(3)], n


def cmd_one(args):
    job = read_json(args.job)
    enter_repo(args.repo)
    folder = Path(job["folder"])
    folder.mkdir(parents=True, exist_ok=True)
    seed = int(job["seed"])
    t0 = time.time()
    sys.argv = ["generate_individual_assets", "--output_folder", str(folder), "-f", job["dotted"], "-n", "1",
                "--render", "none", "--save_blend", "-G", "--export", "obj", "--export_texture_res",
                str(int(args.tex_res))]
    from infinigen_examples import generate_individual_assets as G
    gargs = G.make_args()
    gargs.no_mod = gargs.no_mod or gargs.fire
    gargs.film_transparent = gargs.film_transparent and not gargs.hdri
    G.configure_cycles_devices = lambda *a, **k: None        # bake on the CPU (module docstring)
    with G.FixedSeed(1):
        G.build_and_save_asset({"fac": job["dotted"], "args": gargs, "idx": seed})
    objs = sorted(folder.glob(f"export_{seed:03d}/*.obj")) or sorted(folder.glob("export_*/*.obj"))
    dims, meshes = scene_dims()
    blends = sorted(folder.glob("*/scene.blend"))
    import bpy
    rec = {"id": job["id"], "ok": bool(objs), "obj": str(objs[0]) if objs else None,
           "blend": str(blends[0]) if blends else None, "dims": dims, "meshes": meshes, "class": job.get("class"),
           "dotted": job["dotted"], "seed": seed, "bpy": bpy.app.version_string, "tex_res": int(args.tex_res),
           "seconds": round(time.time() - t0, 1)}
    if not objs:
        rec["error"] = "no OBJ was exported"
    prev = read_json(folder / "result.json") or {}
    rec["attempts"] = int(prev.get("attempts", 0)) + 1
    write_json(folder / "result.json", rec)
    return 0 if rec["ok"] else 1


def state(folder):
    rec = read_json(Path(folder) / "result.json")
    if not rec:
        return "todo", 0
    if rec.get("ok") and rec.get("obj") and Path(rec["obj"]).is_file():
        return "done", int(rec.get("attempts", 1))
    n = int(rec.get("attempts", 1))
    return ("failed" if n >= MAX_ATTEMPTS else "todo"), n


def cmd_generate(args):
    jobs = [j for j in (read_json(args.jobs) or {}).get("jobs") or [] if j.get("dotted")]
    deadline = float(args.deadline) if args.deadline else None
    me = str(Path(__file__).resolve())
    left = failed = done = 0
    for job in jobs:
        st, attempts = state(job["folder"])
        if st == "done":
            done += 1
            continue
        if st == "failed":
            failed += 1
            continue
        now = time.time()
        if deadline is not None and now + float(args.min_job_s) > deadline:
            left += 1
            print(f"INFINIGEN {job['id']} not started: the time cap is near", flush=True)
            continue
        limit = float(args.job_timeout)
        if deadline is not None:
            limit = max(30.0, min(limit, deadline - now))
        folder = Path(job["folder"])
        folder.mkdir(parents=True, exist_ok=True)
        jp = folder / "job.json"
        write_json(jp, job)
        t0 = time.time()
        with open(folder / "log.txt", "w", encoding="utf-8") as fh:
            try:
                code = subprocess.call([sys.executable, me, "one", "--repo", args.repo, "--job", str(jp),
                                        "--tex-res", str(args.tex_res)], stdout=fh, stderr=subprocess.STDOUT,
                                       timeout=limit)
                why = None if code == 0 else f"exit {code}"
            except subprocess.TimeoutExpired:
                code, why = 124, f"stopped after {limit:.0f} s (time limit)"
        st, _ = state(folder)
        if st != "done":
            rec = read_json(folder / "result.json") or {}
            if rec.get("attempts", 0) <= attempts:          # the child died before writing its record
                rec = {"id": job["id"], "ok": False, "attempts": attempts + 1, "dotted": job["dotted"],
                       "seed": job["seed"], "error": why or "no OBJ was exported",
                       "seconds": round(time.time() - t0, 1)}
                try:
                    rec["log_tail"] = (folder / "log.txt").read_text(encoding="utf-8", errors="replace")[-3000:]
                except OSError:
                    pass
                write_json(folder / "result.json", rec)
            failed += 1
            print(f"INFINIGEN {job['id']} failed: {why or rec.get('error')}", flush=True)
        else:
            done += 1
            print(f"INFINIGEN {job['id']} ok in {time.time() - t0:.0f} s", flush=True)
    print(f"INFINIGEN batch: {done} done, {failed} failed, {left} not started", flush=True)
    return 0 if not failed and not left else 1


def main(argv=None):
    p = argparse.ArgumentParser(prog="infinigen_driver.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("check")
    s.add_argument("--repo", required=True)
    s.add_argument("--jobs", required=True)
    s.add_argument("--out", required=True)
    s = sub.add_parser("generate")
    s.add_argument("--repo", required=True)
    s.add_argument("--jobs", required=True)
    s.add_argument("--deadline", default=None)
    s.add_argument("--job-timeout", type=float, default=600.0)
    s.add_argument("--min-job-s", type=float, default=120.0)
    s.add_argument("--tex-res", type=int, default=1024)
    s = sub.add_parser("one")
    s.add_argument("--repo", required=True)
    s.add_argument("--job", required=True)
    s.add_argument("--tex-res", type=int, default=1024)
    args = p.parse_args(argv)
    try:
        return {"check": cmd_check, "generate": cmd_generate, "one": cmd_one}[args.cmd](args)
    except Exception:  # noqa: BLE001 - printed for the job's log
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
