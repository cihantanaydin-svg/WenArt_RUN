# Milestone 6 – one-command full project runs, Cycles realism, real-project intake

Goal: run a whole project folder (documents + brief + optional style photos) to final, checked renders
with **one command on one pod**, for at least three projects; make the plain Cycles renders read more like
photos (better cameras, materials, bedding, windows, dark rooms); measure that realism change with a
protocol that is validated by controls instead of by eye; and give the user a safe way to bring real,
possibly confidential projects to the pod. Nothing about the no-hallucination rules changes: every new
object is a design detail of a documented element or an `assumed` light, recorded in the manifests.

Research and prototypes: 2 Oct 2026, session scratch (not committed): orchestration timings from the M5 pod
logs, two new synthetic projects prototyped end to end on CPU, the look changes prototyped in Blender 5.2.2
(CPU) on synthetic-01/03, a ray-cast camera scorer validated against the real index pass (r = 0.885), the
realism protocol drafted against the M5 preference answers, and the RunPod S3 API checked from the docs and
the live endpoint. A completeness critic re-checked the numbers (§11).

Scope:
1. One-command full run: Python orchestrator `wenart/run` + bash job `scripts/jobs/full.sh` (§2).
2. Two new synthetic projects `synthetic-04`, `synthetic-05` and the fixes they need (§3).
3. Camera search with straight verticals (§4).
4. Cycles realism package (§5).
5. Realism A/B measurement with controls (§6).
6. Real-project intake path, runner changes, per-project gate validation, final-report changes (§7).
7. Pod runs: all four synthetic projects end to end, synthetic-02 and a private-path self-test as
   `needs_review`, the realism A/B (§8).

Out of scope: DWG reading (LibreDWG never produced geometry, `results/bakeoff/dwg_roundtrip.json`; users export
DXF), the scan/photo recognition path in the pipeline (still `needs_review`), open balconies, doorless
openings, angled walls, a second style of `styles:`, the SigLIP/absolute realism score (§11), vLLM sleep mode.

## 0. Decisions (changes to `docs/plan.md` and `CLAUDE.md`)

| Before | Now | Why |
|---|---|---|
| plan §6 M6: "3+ full project runs" on the user's projects | runs on synthetic-01, -03, and the new -04, -05 (+ synthetic-02 as `needs_review`); real projects run with the same command as soon as the user uploads them (§7.1) | `projects/` holds no real project; the repo is **public**, so a real project can never be committed |
| plan line "real projects in `projects/<name>/`, git-ignored if confidential" | private projects live on the network volume under `/workspace/projects-private/<alias>/`, uploaded by the user with the RunPod S3 API; outputs and results stay under `/workspace/outputs-private/`, `/workspace/results-private/`, collected into the git-ignored `runs/` | `pod_entry.sh` runs `git clean -fdx` in `/workspace/repo` on every start; the repo is public; files go user → RunPod only, never through GitHub or the model context |
| three job scripts (`render.sh`, `furnish.sh`, `polish.sh`), each a piece; polish starts from the committed `results/furniture/<p>/building_final.json` | one job `scripts/jobs/full.sh` → `python -m wenart.run pod` runs stages 1–17 for every project; no fallback to committed buildings | polish.sh is 694 lines of array state; a Python orchestrator is unit-testable and owns server sharing, needs_review, deadlines and fingerprints. The old jobs stay as they are (not extended) |
| layout used an unpinned Qwen with `image:1` | layout uses the check's pinned Qwen server (`check.yaml models.qwen`, `image:2`, same served name) | one server start shared by layout and check sessions |
| cameras: 3 fixed rules per room, 1.4 m, looking 0.1 m down | searched cameras: ray-cast score, fixed height 1.25 m, pitch 0, lens shift `shift_y = −0.10`, 1–3 views per room by area; the M5 rule set stays as `camera_policy: m5` | 17/87 M5 views framed bare walls, 12/87 were blocked, 52/87 showed < 1 % floor. Fixed height: the scorer has no optimum in height (it always takes the lowest offered) |
| realism judged with one tie-allowed question (`preference.py`) | new pairwise forced-choice protocol per aspect, both orders, both models, validated by known-direction and null controls (`realism.py`); `preference.py` unchanged (info) | M5: 90 % "same", 0 of 45 pairs order-consistent for both models; the tie option hides a weak signal |
| CLAUDE.md: default GPU RTX A5000 (then 4090, A6000) | default RTX PRO 4500 (32 GB), then RTX 4090 (24 GB), then RTX PRO 4000; never L4; `GPU_PRIORITY` in `gpu_run.py` in that order | A5000/A40/A6000 had no stock on 2 Oct; every M5/M6 timing is measured on the PRO 4500 / 4090. Reported to the user |
| pods kept running for the whole `--grace` | the runner stops the pod right after a successful collection (the in-pod watchdog stays) | ≈ 7 idle billed minutes per pod in M5 |
| gate thresholds calibrated once (M5, synthetic-01/03) | every polished project re-runs `gate calibrate` and is **validated**: benign accepted ≥ 95 %, negatives rejected ≥ 90 %; a project failing the negative limit gets Cycles finals only | the M6 look changes the textures the gate sees; new projects were never calibrated |
| plan §6 M6 budget 3–5 h, $2–4 | cap $4.00 for M6 pods; two planned pods ≈ $2.3; ask the user before going over | CLAUDE.md limits |

M5 items still waiting for the user's OK stay as they are and are repeated in the M6 report: the looser gate
limits (`calibration.user_ok: pending`) and the advisory vision check.

## 1. Shared contracts (read before any area)

### 1.1 Projects and paths (`wenart/run/projects.py`, written first)

```python
@dataclass(frozen=True)
class ProjectRef:
    name: str            # public project name or private alias
    private: bool
    project_dir: Path    # projects/<p>  |  /workspace/outputs-private/<a>/input (NFC staged copy, §7.1)
    out_dir: Path        # outputs/<p>   |  /workspace/outputs-private/<a>
    results_dir: Path    # $RESULTS      |  /workspace/results-private/<a>
def public_project(name, repo_root) -> ProjectRef
def private_project(alias, private_root=Path("/workspace/projects-private"),
                    outputs_root=Path("/workspace/outputs-private"),
                    results_root=Path("/workspace/results-private"), repo_root=REPO_ROOT) -> ProjectRef
```
- Public results keep the committed layout `$RESULTS/<area>/<p>/` with areas `renders`, `furniture`, `polish`,
  `gate`, `check`, `final`, `run` (new: stage records and log tails), `realism` (new, §6).
- Private results use the same areas one level down: `/workspace/results-private/<a>/<area>/`. The job links
  `$JOB_DIR/results-private/<a>` → that folder; the runner collects it (§7.2).
- **Paths in manifests**: every path written relative to the repo root (e.g. `scene_manifest["building"]`) is
  written **absolute** when the file is outside the repo root; every reader accepts both
  (`wenart.views.resolve_repo_path(p)`: absolute stays, relative joins the repo root). Paths relative to the
  folder of the JSON (M5 §1.1) stay relative. Areas L, V and IE check their writers and readers; the e2e test
  of §9 runs one project in a temp dir outside the repo.
- Nothing about a private project (room names, file names, labels) is printed to `job.log`: the orchestrator
  prints only `<alias> <stage> rc=<n> <seconds>s`; every subprocess writes its output to
  `<out_dir>/run/logs/<stage>.log`.

### 1.2 Stage records and fingerprints (`wenart/run/state.py`)

Per project and stage: `<out_dir>/run/<stage>.json`

```json
{"schema_version": "0.1", "kind": "stage_record", "project": "synthetic-04", "stage": "layout",
 "rc": 0, "status": "ok|reused|failed|needs_review|skipped|incomplete", "seconds": 91.2,
 "fingerprint": "<sha256>", "inputs": {"<path>": "<canonical sha256>"}, "outputs": ["building_furnished.json"],
 "started_utc": "...", "git_commit": "...", "log": "logs/layout.log", "note": null}
```
- `canonical_sha256(path)`: for `.json` files the sha256 of `json.dumps(obj, sort_keys=True,
  separators=(",", ":"))` after removing the **volatile keys** `created_utc`, `updated_utc`, `generated_utc`,
  `started_utc`, `finished_utc`, `seconds`, `latency_s` at any depth; raw bytes for other files; for a folder
  the sha256 of the sorted `(relpath, sha)` list.
- `fingerprint = sha256(json([stage, STAGE_VERSION[stage], args, sorted(inputs), code_hash(stage)]))`;
  `code_hash` = sha256 of the source files that implement the stage (listed in the stage table, §2.2).
- A stage with `reuse: fingerprint` is skipped (status `reused`) when the stored fingerprint equals the new
  one, the stored `rc` is 0 and every listed output exists. Stages with their own fine-grained reuse (build
  `--reuse`, render `render_key`, polish `attempt_key`, check answers by call key) are always invoked.
- `build.build_fingerprint` hashes the building with `canonical_sha256` too (area L), so a re-run pipeline that
  only changed `created_utc` never rebuilds the scene.

### 1.3 Cameras (`wenart/blender/cameras.py` plan dict, scene manifest, projection)

New plan / scene-manifest camera fields (schema in `wenart/blender/schemas.py`, all optional for old
manifests): `shift_x` (number, default 0), `shift_y` (number, default 0), `policy` (`"search"` | `"m5"`),
`score` (object or null: `total`, `furniture`, `openings`, `floor`, `depth`, `penalties`). Names stay
`cam_<room_id>_<i>`, `i = 1..n`. `target` is still a world point (search: position + 1 m along the yaw at
the same height).

Projection with shift (horizontal sensor fit, Blender's shift unit is the larger image side = W):
`u = W/2 − shift_x·W + f·(d·r)/(d·f)`, `v = H/2 + shift_y·W − f·(d·u)/(d·f)` (pixel origin top-left).
The sign convention **must** be confirmed by a Blender CPU test against
`bpy_extras.object_utils.world_to_camera_view` before any other code relies on it (area C). Readers that
project (`vision_check/expected.py`, `geom2d.point_in_frustum`) use `shift_x/shift_y` when present; the
plan-crop view cone uses the horizontal field of view only (unchanged, `shift_x` is always 0).

### 1.4 VLM server (`wenart/run/servers.py`)

Port of `polish.sh` `start_server` / `stop_server` / `server_args` / `server_seqs`: model id, revision and
`server_flags` from `check.yaml models.<key>`; `vllm serve <id> --revision <rev> --served-model-name <id>
--port 8001 --limit-mm-per-prompt '{"image":2}' --gpu-memory-utilization 0.90`; below 40 GB VRAM
`--quantization fp8 --max-model-len 8192 --max-num-seqs 2`, else `--max-model-len 16384 --max-num-seqs 4`;
env `VLLM_USE_FLASHINFER_SAMPLER=0`; log `/workspace/logs/vllm-<key>-<job>.log`; `/health` every 10 s;
early exit → last 40 log lines into the job log; give up after `SERVER_WAIT_S` (1500 s) or at the deadline;
stop = TERM, wait 60 s, KILL. The pid goes to `$WENART_JOB_DIR/vllm.pid` (the bash EXIT trap kills it).
A context manager: `with server("qwen", deadline) as url: ...`. `--vlm-url URL` (smoke profile, §2.5)
skips starting and uses an external server.

### 1.5 Ownership (parallel implementation)

| Area | Owns |
|---|---|
| R run | `wenart/run/*` (new), `scripts/jobs/full.sh` (new), `wenart/furniture/layout.py` (dead-server exit code only), `tests/fakes/fake_vlm.py` (new), `tests/test_run_*.py`, `tests/test_full_job.py`, `tests/gpu/test_full_run.py` |
| S synthetic | `wenart/synthetic/*`, `wenart/building.py` (room keywords), `projects/synthetic-04/`, `projects/synthetic-05/` (generated), `docs/synthetic.md`, `tests/test_synthetic.py`, `tests/test_pipeline.py`, `tests/test_building.py` |
| C cameras | `wenart/blender/cameras.py`, `wenart/blender/camsearch.py` (new), `wenart/blender/geom2d.py` (frustum with shift), `project_points`/`focal_px` in `wenart/vision_check/expected.py`, `tests/test_blender_cameras.py`, `tests/test_camsearch.py` (new), `tests/gpu/test_render.py` |
| L look | `wenart/blender/{materials,parametric,furniture,shell,lighting,render,build,cli,schemas}.py`, `wenart/style/{vocabulary,profile}.py`, `wenart/assets/*`, `wenart/furniture/decor.py` (cushion rest height), Blender CPU tests, `tests/gpu/test_look_m6.py` (new) |
| V realism | `wenart/vision_check/realism.py` (new), `wenart/vision_check/{cli,schemas}.py` (realism commands and schemas), `check.yaml` `realism:` block, `wenart/recognition/vlm_client.py` (system prompt argument, if missing), `tests/test_realism.py`, `tests/gpu/test_realism.py` |
| IE intake + report | `wenart/intake.py` (new), `docs/intake.md` (new), `.gitignore`, `scripts/gpu_run.py`, `wenart/gate/validate.py` + `wenart/gate/validation.yaml` (new), `wenart/gate/__main__.py` (`validate` command), `wenart/report/*`, `wenart/views.py` (`resolve_repo_path`), `tests/test_intake.py`, `tests/test_private_guard.py`, `tests/test_gpu_run.py`, `tests/test_report.py`, `tests/test_gate_validate.py` |

Files outside this table are changed only by the integrator. Interfaces between areas are the ones in §1.

## 2. One-command full run (area R)

### 2.1 Commands

```
python -m wenart.run plan --projects synthetic-01,synthetic-03 [--out run_plan.json]
python -m wenart.run pod  --projects "synthetic-01 synthetic-03" [--private "real-01"] [--private-selftest]
                          [--ab "synthetic-01 synthetic-03"] [--ab-controls synthetic-01]
                          --results $RESULTS [--profile full|smoke] [--force stage[,stage]] [--vlm-url URL]
python -m wenart.run copy --projects ... [--private ...] [--ab ...] --results $RESULTS [--since STAMP]
```
- `plan` (CPU, session or pod): runs stage 1 (pipeline) for each project and writes per project: status,
  levels, rooms, empty rooms, views estimate (§4 rule), minutes estimate (§8.1 rule) and a suggested pod split
  (first-fit under 84 min of project work per pod). `needs_review` projects get their report and no pod time.
- `pod` (inside `full.sh`): the whole run. Exit 0 when every project ended `ok` or `needs_review`, no AB
  stage failed, and every GPU test group passed; else 1.
- `copy`: copies the small result files of the given projects into the results layout (§1.1), only files newer
  than `--since` (a stamp file) unless omitted. Same file filter as `polish.sh copy_files`: `*.json`, `*.md`
  (< 8 MB), `*_preview.jpg`, `*_gate.jpg`, `*_check.jpg`, `*_plan.jpg`, `contact_*.jpg`, `*_alt_preview.jpg`,
  `debug/*.jpg` (< 301 KB), last 400 lines of `*.log`.

### 2.2 Stage table (per project; batched over all projects by GPU holder)

PY = `/workspace/venv/bin/python`, POLISH_PY = `/opt/wenart/venv-polish/bin/python`. `out` = `out_dir`.

| # | Stage | Command (existing CLIs unless marked new) | Holder | Reuse | Terminal on failure |
|---|---|---|---|---|---|
| 0 | intake (private only) | `PY -m wenart.intake stage <alias> --out out/input` (§7.1) | – | fingerprint | failed |
| 1 | pipeline | `PY -m wenart.ingest.pipeline <project_dir> --out out` | – | fingerprint (project files + `wenart/ingest/**`, `wenart/building.py`, `wenart/geometry.py`) | exit 1 + building status `needs_review` → **needs_review** (stop); other → failed |
| 2 | photos (if the brief/folder has style photos) | `PY -m wenart.style.photos read <photos> --model-key <k> --server <url> --out out/style_photos/passes.json` for qwen and glm, then `... combine out/style_photos/passes.json --out out/style_photos/terms.json` | VLM (GLM session, then Qwen session) | skipped when `passes.json` holds an answer of both models for every photo sha256 at the pinned revisions | photos ignored, warning (style from the brief only) |
| 3 | style | `PY -m wenart.style <project_dir> --out out/style.json [--photo-terms out/style_photos/terms.json]` | – | always (deterministic, < 1 s) | failed |
| 4 | assets | `PY -m wenart.assets fetch --style out/style.json --assets /workspace/assets --size 2k` | – | always (cached) | warning only |
| 5 | fit | `PY -m wenart.furniture.fit out/building.json --catalog wenart/furniture/catalog.json --out out/building_fitted.json --assets /workspace/assets` | – | fingerprint | failed |
| 6 | layout (rooms without documented furniture) | `PY -m wenart.furniture.layout out/building_fitted.json --style out/style.json --server <url> --model Qwen/Qwen3-VL-8B-Instruct --out out/building_furnished.json --debug out/layout_debug --passes 2` | VLM Qwen | fingerprint (+ Qwen id and revision) | exit ≠ 0 → failed (never reused) |
| 7 | decor | `PY -m wenart.furniture.decor <furnished or fitted> --out out/building_decor.json` | – | fingerprint | failed |
| 8 | refit | `PY -m wenart.furniture.fit out/building_decor.json ... --out out/building_final.json` | – | fingerprint | failed |
| 9 | build | `PY -m wenart.blender.cli build --building out/building_final.json --style out/style.json --assets /workspace/assets --out out/scene --preview-samples 32 --reuse` | Blender | build fingerprint | exit 2 → needs_review; else failed |
| 10 | render | `PY -m wenart.blender.cli render --scene out/scene/scene.blend --out out/renders --cameras all --samples 128 --res 1920x1080 --exposure auto --white-balance auto` | Blender | render_key | exit 3 → incomplete; else failed |
| 11 | controls | `PY -m wenart.vision_check select-controls --project-out out`; `PY -m wenart.blender.cli render ... --out out/controls --hide-sets <lines> --look-from out/renders/render_manifest.json` | Blender | render_key | warning (check stays advisory) |
| 12 | polish (brief `polish` not false) | `POLISH_PY -m wenart.polish run --project-out out` (`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`) | diffusion | attempt_key | rc 1 → warning (views keep Cycles); deadline → incomplete |
| 13 | gate calibrate + validate (polish on) | `POLISH_PY -m wenart.gate calibrate --project-out out`; `PY -m wenart.gate validate --project-out out` (§7.3) | gate models | own | validation result only |
| 14 | expected + plan crops | `PY -m wenart.vision_check expected` / `plan-crops --project-out out` | – | always | failed |
| 15 | check (per model session) | `vision_check run --model-key K --server URL --kinds cycles,polished --workers <seqs>`; `preference --kinds polished`; `style-photo --photo tests/fixtures/style_photo_synthetic-03_salon.jpg --out out/check/style_photo_test.json` (first public project only) | VLM Qwen, then GLM | answers by call key | deadline → incomplete |
| 16 | combine | `vision_check combine`, `calibrate` | – | always | failed |
| 17 | report | `PY -m wenart.report final --project-out out` (also for needs_review, §7.4) | – | always | failed |

AB stages (§6.3) run inside the same phases for the projects in `--ab`. GPU tests run once at the end (§2.4).

### 2.3 Scheduler

Phases, each over all active projects in the given order, stopping a project at its first terminal state:
1. CPU: intake, pipeline, style (without photo terms), fit.
2. VLM GLM session — only when some project has style photos without cached GLM answers: photos (glm).
3. VLM Qwen session — only when some project needs a layout or Qwen photo answers: photos (qwen), photo
   combine, style again with `--photo-terms` (re-run fit only if the style changed what fit reads), layout.
4. CPU: assets, decor, refit; AB prepare (§6.3).
5. Blender: build, render, controls for every project; AB builds and renders.
6. Diffusion: polish, gate calibrate for every project with polish on; gate validate (CPU).
7. CPU: expected, plan crops; AB pairs file.
8. VLM Qwen session: check run, preference, style-photo test, realism (AB).
9. VLM GLM session: the same.
10. CPU: combine, calibrate, realism-combine, realism-summary, report for every project (also needs_review
    and incomplete ones).
11. GPU tests (§2.4), then `run_manifest.json`.

Rules:
- `WENART_DEADLINE` (epoch s, set by `pod_entry.sh`): a heavy stage (build, render, controls, polish, gate,
  any server start, any VLM stage) starts only when `now + estimate(stage) < deadline`, with estimates from
  §8.1 (render 8 s per view + 60 s, polish 20 s per view, server start 300 s Qwen / 150 s GLM, check 2.2 s per
  call / seqs). A project whose stage cannot start becomes `incomplete` (not `failed`). Phases 10–11 always
  run. The orchestrator itself never exceeds the deadline by more than the running stage.
- Stage subprocesses get `timeout = max(60, deadline − now)`; on timeout TERM then KILL, status `incomplete`.
- Server sessions are skipped when no project needs them (3 starts without photos, 4 with uncached photos,
  2 when no project has an empty room and no photos).
- `--force stage,...` ignores the fingerprint for those stages.
- `run_manifest.json` in `$RESULTS` (public projects with all details; private aliases with state only) and
  `results-private/_run_manifest.json` (private details): per project state, stage list (status, seconds), per
  phase start/end, server starts (seconds to ready), totals, deadline, profile, git commit.

### 2.4 `scripts/jobs/full.sh` and GPU tests

Bash with `#!/usr/bin/env bash`, `set -Eeuo pipefail`, ERR trap (line + command into the log), TERM → exit
143, logs under `/workspace/logs/full-<job>.log` (tee), the cgroup CPU thread budget of `polish.sh`
(OMP/OPENBLAS/MKL/NUMEXPR/VECLIB/OPENCV threads), `bash scripts/pod_setup_polish.sh` with all parts (venv,
models, check), then `HF_HUB_OFFLINE=1`, a background copy loop every 300 s under `flock` calling
`$PY -m wenart.run copy ... --since $COPY_STAMP`, then `$PY -m wenart.run pod ...`. EXIT trap: kill the pid in
`$WENART_JOB_DIR/vllm.pid`, stop the copy loop, one full copy, copy this job's vLLM/setup logs (tail 200) to
`$RESULTS/logs/` — or to `results-private/_logs/` when any private project is in the run.
Env (all optional except `RUN_PROJECTS` or `PRIVATE_PROJECTS`): `RUN_PROJECTS`, `PRIVATE_PROJECTS`,
`PRIVATE_SELFTEST=1`, `AB_PROJECTS`, `AB_CONTROL_PROJECT`, `RUN_FORCE`, `RENDER_SAMPLES` (128).

GPU tests (after the last server stopped, junit into `$RESULTS/junit-*.xml`; project lists exported by the
orchestrator from the final states): `PY -m pytest -m gpu tests/gpu/test_full_run.py tests/gpu/test_render.py
tests/gpu/test_look_m6.py tests/gpu/test_furnish.py tests/gpu/test_check.py tests/gpu/test_realism.py` and
`POLISH_PY -m pytest -m gpu tests/gpu/test_polish.py tests/gpu/test_polish_backend.py`, with
`RUN_TEST_PROJECTS` (ok public projects), `NEEDS_REVIEW_TEST_PROJECTS`, `RENDER_TEST_PROJECTS`,
`FURNISH_TEST_PROJECTS` (ok projects with ≥ 1 AI-furnished room), `CHECK_TEST_PROJECTS`,
`POLISH_TEST_PROJECTS` (ok projects with polish on), `AB_TEST_PROJECTS`. Private projects are never in a test
list (tests print paths and names).

### 2.5 Smoke profile (CPU, for the session)

`--profile smoke`: render `--res 480x270 --samples 16 --device cpu`, controls 2 views, no polish/gate
(skipped with status `skipped`), `--vlm-url` required (the fake server), no GPU tests. `tests/fakes/fake_vlm.py`:
stdlib `http.server` on a free port with `/health`, `/v1/models`, `/v1/chat/completions` answering a minimal
valid instance of the request's JSON schema (enum → first value, integer → minimum, number → minimum or 0,
string → "", array → `minItems` copies, object → required keys), deterministic. `tests/test_run_e2e.py`
(marked `slow`, skipped without Blender) runs synthetic-04 + a private copy of synthetic-02 in a temp dir with
the smoke profile end to end and checks the run manifest, stage records, reports and the private layout.

### 2.6 Fixes the full run needs

- `layout.py`: when any room's call fails with a transport error after the client's retries, exit 3 and write
  no output file (today: rc 0 with empty rooms, then reused forever).
- No `ensure_buildings` fallback (committed buildings are never inputs of a full run).
- The style-photo terms reach the **first** style stage of the same run (phase 3).

## 3. Test projects (area S)

### 3.1 synthetic-04 – 2+1 flat on the 3rd floor, DXF + vector PDF of the same level, L-shaped rooms

Footprint 12.0 × 8.0 m, one level `3. KAT PLANI` (L3, elevation 9.0). Documents `3_kat_plani.dxf` and
`3_kat_plani_pdf.pdf` (different stem: the generator's preview names derive from the stem), both with walls,
openings and furniture. Brief: `style: "Japandi, walnut floor, cream walls, warm daylight, linen and paper
lamps"`.

| Room | Polygon | Size | Doors / windows | Furniture in documents |
|---|---|---|---|---|
| SALON + MUTFAK 39,05 m² (living) | L, 6 vertices | 6.7 × 4.3 + 3.2 × 3.2 | door from Hol; 5 windows on 3 walls | TEZGAH, EVIYE, OCAK, BUZDOLABI, YEMEK_MASASI, SANDALYE ×4, KANEPE_3LU, SEHPA, TV_UNITESI, KOLTUK at 45°, KITAPLIK (14) |
| HOL (hall) | L, 6 vertices | 4.4 × 1.2 + 1.6 × 1.9 = 8.32 m² | entrance + 4 doors, no window | none → AI |
| YATAK ODASI (bedroom) | rect | 4.7 × 4.3 | door; windows on 2 walls | YATAK_CIFT, KOMIDIN ×2, DOLAP (4) |
| BANYO (bathroom) | rect | 2.7 × 1.8 | door; 1 window | KUVET (new block), KLOZET, LAVABO (3) |
| ÇOCUK ODASI (bedroom) | rect | 3.7 × 3.1 | door; windows on 2 walls | none → AI |

Expected: ingest ok, 10 walls, 15 openings (5 doors, 10 windows), 5 rooms, 21 pieces with 2 evidence entries
each (DXF INSERT + PDF path), 0 conflicts, 0 unverified, the 45° armchair matched across DXF and PDF.

### 3.2 synthetic-05 – 3+1 flat, notched outline, floor plan without furniture + furniture plan, style photo, polish off

Footprint 13.5 × 9.0 m with a 3.0 × 1.75 m recess at the bottom right, level `ZEMİN KAT PLANI` (L0).
Documents: `zemin_kat.dxf` (floor plan, dimensions, no furniture), `zemin_kat_mobilya.dxf` (`ZEMİN KAT MOBİLYA
PLANI`, furniture, no dimensions), `style_photos/salon_referans.jpg` (copy of
`tests/fixtures/style_photo_synthetic-03_salon.jpg`, our own M4 render). Brief: `style: "Modern, white walls,
warm daylight, linen textiles, brass details"`, `style_photos: [salon_referans.jpg]`, `polish: false`.

| Room | Size | Doors / windows | Furniture (furniture plan only) |
|---|---|---|---|
| SALON 19,76 m² (living) | 5.2 × 3.8 | door from Hol; 2 windows | KANEPE_3LU, SEHPA, TV_UNITESI, YEMEK_MASASI, SANDALYE ×2 |
| EBEVEYN YATAK ODASI (bedroom) | 4.7 × 3.8 | door from Hol + door to the en-suite; 1 window | YATAK_CIFT, KOMIDIN ×2, DOLAP, SIFONYER |
| EBEVEYN BANYO (bathroom) | 2.9 × 2.05 | door from the bedroom only; window onto the recess | DUS, KLOZET, LAVABO |
| MUTFAK (kitchen) | 3.2 × 4.6 | door from Hol; windows on 2 walls | TEZGAH ×2 (L), EVIYE, OCAK, BUZDOLABI, CAMASIR_MAK |
| HOL (hall) | 6.6 × 1.2 | 7 doors, no window | none → AI |
| ANTRE (hall) | 1.5 × 3.3 | entrance + door to Hol | none → AI |
| BANYO (bathroom) | 2.0 × 3.3 | door; 1 window | KUVET, KLOZET, LAVABO |
| YATAK ODASI (bedroom) | 2.9 × 3.3 | door; 1 window | YATAK_TEK ×2 (new block), KOMIDIN |
| ÇALIŞMA ODASI (other) | 3.0 × 4.6 | door; windows on 2 walls | none → AI (`other`) |

Expected: ingest ok, 14 walls (6 exterior), 19 openings (9 doors, 10 windows), 9 rooms, 26 pieces, 0
conflicts, 0 unverified, warning "furniture taken from zemin_kat_mobilya.dxf"; with the photo terms the
floor becomes `concrete_polished` (photo), walls stay white (brief wins).

### 3.3 Code changes

- `model.py`: `LevelBuilder(outline=[(x, y), ...])` for non-rectangular outlines (outer walls corner to
  corner; default = the current 4-wall rectangle, so synthetic-01..03 are unchanged).
- `projects.py`: `project_04`, `project_05` from the prototypes; `Project.style_photos` copied by
  `generate_project`; `all_projects()` lists five.
- `building.py` room keywords: a keyword matches at the **start of a word** (so `banyosu` matches `banyo`);
  among all matching keywords the room type with the highest priority wins: `wc` > `bathroom` > `kitchen` >
  `storage` > `balcony` > `bedroom` > `living` > `hall`. New keywords: `lavabo` → `wc`, `tuvalet` → `wc`,
  `dus` → `bathroom`, `giris` → `hall`, `teras` → `balcony`, `calisma` → `other`. `EBEVEYN BANYO` →
  `bathroom`. The truth of synthetic-01..03 must not change (test pins every `room_type`).
- `docs/synthetic.md`: the two projects, their purpose and expected numbers. Commit the generated projects
  (≈ 0.5 MB) and their previews.

## 4. Cameras (area C)

### 4.1 Search (`camsearch.py`, pure numpy, no Blender)

Port of the validated prototype scorer: per candidate camera, rays on a 64 × 36 grid against the room prism
(floor, ceiling, polygon edges as walls), the door/window rectangles of the room's edges and the room's
furniture boxes (`parametric.piece_bbox` + footprint rotation); per pixel a label (furniture id, opening,
floor, ceiling, wall) and a depth.

Score = 4·Σ_pieces min(coverage·type_weight, 0.25)·(0.6 if cut by the frame) + 1·min(openings, 0.12)
+ 1·min(floor, 0.25) + 1·min(median wall depth / 3 m, 1), minus penalties for near pixels (< 0.9 m) > 8 %,
one element > 40 %, bare wall > 55 %, window > 20 %, ceiling > 15 % (penalty sizes and type weights as in the
prototype, kept in one table `SCORE` in `camsearch.py`).

Candidates: free points (`geom2d.point_is_free` with the existing wall 0.3 m / obstacle 0.2 m clearances) on a
0.5 m grid plus two points per convex polygon corner (0.45 m and 0.6 m in along the bisector); yaw every 30°;
height 1.25 m; pitch 0; `shift_y = −0.10`; lens 24 mm / 36 mm; 1920 × 1080.

Views per room: 3 when the room area ≥ 6 m², 2 when 3–6 m², 1 when < 3 m². Greedy pick by score; a later
pick must differ from every earlier one by ≥ 50° yaw or ≥ 1.0 m; a pick below 0.5 × the room's best score is
dropped (at least 1 view per room). Ties: score, then x, y, yaw. Deterministic. Budget ≤ 60 s per project on
one CPU core for synthetic-03 (measure and record `search_seconds` in the scene manifest).

### 4.2 Integration

- `plan_cameras(building, level_id, policy="search")`; `policy="m5"` = today's code path, unchanged byte for
  byte (names, positions, targets) — the realism A/B depends on it (§6.3).
- Plans carry `shift_x`, `shift_y`, `policy`, `score`, `placement` (text with the score parts), `anchor` null,
  `warning` (e.g. "no candidate without penalty"), `visible_openings` / `visible_furniture` (frustum with shift).
- `create_cameras` sets `cam.shift_x/shift_y`.
- `expected.project_points` with shift (§1.3); a Blender CPU test proves the formula on a shifted camera.
- `tests/gpu/test_render.py`: `test_every_room_has_three_views` becomes: policy `m5` → 3 views per room;
  policy `search` → 1–3 views per room by the area rule, every room ≥ 1; new: no blocked view (one element
  > 50 % of the frame by the index pass, or > 30 % of pixels nearer than 0.9 m by the depth map); report the
  share of views with < 10 % object pixels.

## 5. Cycles realism (area L)

All prototyped on CPU (Blender 5.2.2) with before/after evidence; render time change ≤ 2 %.

| # | Change | Where | Contract / test |
|---|---|---|---|
| 1 | Unverified-piece stripes emit only for camera rays: factor = stripe × Light Path `Is Camera Ray` | `materials.py` | a small room with an unverified piece: wall pixels neutral (|tint| small), stripes still visible |
| 2 | Kitchen counter fronts 1 mm proud of the carcass, handles on the fronts | `parametric.py` | no front face coplanar with a carcass face (CPU test); bbox unchanged |
| 3 | Wall faces split at every room corner along the wall (`bmesh.bisect_plane`) before the per-face material probe | `shell.py` | a wall shared by a bathroom and a bedroom gets tiles on the bathroom span only (CPU test on synthetic-05 L0) |
| 4 | Wet walls: procedural glazed tiles (Brick Texture on metre UVs, 60 × 30 cm, 3 mm grout, roughness 0.08 tile / 0.7 grout, bump from the grout mask) for `tiles_*` slugs without an image asset | `materials.py`, `vocabulary.py`, `profile.py` | material has the node group; flat albedo mode still works |
| 5 | Area light of a windowless room at the pole of inaccessibility (polylabel, 1 cm precision), square size ≤ 2 × its distance to the polygon boundary | `lighting.py` | L-shaped hall of synthetic-04: light fully inside the room |
| 6 | Dim rooms (glass area / floor area < 0.08) get the assumed ceiling area light at half power (6 W/m²), invisible to the camera, recorded `assumed` with the reason | `lighting.py` | manifest entry; GPU: the four dark synthetic-03 rooms below +6 EV |
| 7 | Window pull: after the render, save the Render Result again at EV − k (k ∈ {1,2,3,4}; the view transform is applied at save time); blend the panes (window index ∧ Diffuse Color luminance < 0.05, 3 px feather) into the PNG and preview; smallest k with window clip ≤ 1 % while the pane median stays above the wall median; recorded as `window_pull: {ev, clip_before, clip_after, pane_px}` in the render manifest entry | `render.py` | pixels outside the mask unchanged (max diff 0); EXR passes unchanged |
| 8 | Soft bedding (superellipsoid mattress, draped duvet, turn-down band, pillows leaning 14°) inside the bed's own box; veneer slugs (`wood_veneer_oak`, `wood_veneer_walnut`, Poly Haven `oak_veneer_01`, `walnut_veneer`) for furniture wood instead of the floor planks; fabric textures in flat albedo mode (Poly Haven `rough_linen`); `metallic = 1` for steel; one Bevel modifier (weight-limited, 0.05 m, 3 segments, per-part weights, ≤ 1/3 of the smallest side) | `parametric.py`, `furniture.py`, `materials.py`, `vocabulary.py`, `wenart/assets` | bbox equals the footprint box (1.6 × 2.0 × 1.0 m bed checked); decor cushions on beds rest on the bedding (`decor.py` host height) |
| 9 | Doors: veneer with vertical grain, lever handles on both faces at 1.02 m (steel, the door's pass index); painted skirting 8 cm × 12 mm along dry-room walls, interrupted at doors, pass index 0, status `assumed` | `shell.py`, `materials.py` | handles inside the door's bbox + handle depth; skirting absent in wet rooms |
| 10 | `--alt-look "AgX - Punchy"`: also save `<cam>_alt_preview.jpg` with that look (AB renders only) | `render.py`, `cli.py` | file exists; main PNG unchanged |
| 11 | Control flags for §6: `--max-bounces N`, `--no-denoise`, `--ev-offset X` (added to the auto or `--look-from` EV); all part of `render_key` | `render.py`, `cli.py` | key changes with each flag |
| 12 | `render` stops before a new camera once `WENART_DEADLINE` is past, writes the manifest with `incomplete: true`, exit 3 | `render.py`, `cli.py` | CPU test with a past deadline |
| 13 | `build --camera-policy search|m5` (default search, part of the fingerprint); building hashed with `canonical_sha256` (§1.2) | `build.py`, `cli.py` | fingerprint unchanged when only `created_utc` changes |

Rules: furniture type, footprint, rotation and room never change; bedding, handles, fronts and skirting are
design details of documented elements (recorded in the scene manifest `assumed` block); the dim-room light is
lighting mood (`assumed`, reason recorded); window pull and the alt look change display pixels only.
Texture downloads happen on the pod (`/workspace/assets`); ambientCG is not used for new slugs (its sizes are
mostly unknown and the session cannot fetch it).

## 6. Realism A/B (area V)

### 6.1 Protocol (`realism.py`)

Pair = the same camera rendered two ways, A (baseline) and B (candidate). Per pair: 2 orders (`ab`: A is image
1; `ba`: B is image 1) × 2 models (Qwen3-VL-8B, GLM-4.6V-Flash), temperature 0, seed 0, strict schema, own
system prompt:

```
You are a strict interior photographer and 3D artist. You judge whether images look like real photographs or
like computer renderings. You answer only with JSON that follows the given schema.
```

User prompt (labels "Image 1:" / "Image 2:" before the images):

```
Image 1 and image 2 show the same room from the same camera position. They differ only in how the room was
made into an image: materials, lighting, furniture models, small objects, camera settings.

Compare them as a professional interior photographer would. For each aspect below, pick the image that looks
more like a real photograph, and say how big the difference is.

Aspects:
- materials: surfaces look like real materials (wood grain, fabric weave, plaster, tiles, metal) with natural
  roughness, sheen and reflections, not flat or plastic colour.
- lighting: light falls off naturally, soft contact shadows where objects touch the floor and walls, plausible
  bounce light and window light; no flat, uniform, blown-out or murky light.
- furniture: furniture and objects have real shapes, rounded edges, seams, soft cushions and small details,
  not simple boxes.
- photo: the whole image could be a real photograph taken in an existing home.

Rules:
- You must pick image_1 or image_2 for every aspect. There is no tie. If the two images look almost the same
  for an aspect, still pick the better one and set margin to "slight".
- margin: slight = you need to look closely; clear = visible at a normal look; large = obvious at first sight.
- cues: up to 3 cues from the list that decided this aspect (empty list if none applies).
- Judge only how real the images look. Do not judge the style, the colour scheme or the layout, and do not
  prefer an image because it is shown first or second.

Cues: material_texture, material_response, contact_shadows, light_falloff, window_light, exposure_colour,
furniture_shape, soft_textiles, small_objects, imperfections, fewer_artifacts, camera_look.

Answer only with JSON that follows the schema.
```

Schema (Draft 2020-12, the subset the M5 schemas use): object with required `materials`, `lighting`,
`furniture`, `photo` (in that order), each `{"winner": enum[image_1, image_2], "margin": enum[slight, clear,
large], "cues": array ≤ 3 of the 12 cue enums}`, `additionalProperties: false` everywhere (inlined, no
`$ref`). Post-validation removes repeated cues. Call key `realism|<set>|<cam>|<order>`, stored in the M5
`AnswerStore` format in `out/check/realism/answers_<model slug>.json`, resumable by `input_sha256`.
Images are sent at the M5 size (1600 px long side).

Outcomes per model, pair, aspect: **W** = B picked in both orders, **L** = A in both, **T** = the pick follows
the position, **NC** = a call failed (never a tie or loss). Graded score per model: Σ over both orders of
±{1,2,3} (slight/clear/large, + toward B), range −6..+6. Consensus: W only when both models W, L only when both
L, NC when any NC, else T. Per model also: order consistency (W+L)/(W+L+T) and the position-bias index (share
of `image_1` picks, ≈ 0.5 expected).

Statistics: exact two-sided sign test on consensus W vs L (ties out); per room the majority outcome of its
views and a sign test over rooms; a room-cluster bootstrap 95 % interval of the net win (W−L)/N (2000
resamples, seed 0).

Decision for a pair set (per aspect and overall, written to `realism_ab.json`):
- `not_measurable` when the controls of §6.2 fail for both models;
- `better` when consensus `photo` W > L with sign-test p < 0.05 **and** ≥ 30 decisive pairs from ≥ 10 rooms
  **and** the room-level net-win interval is above 0 **and** no aspect has significantly (p < 0.05) more L
  than W;
- `worse` when the same holds with L and W swapped;
- otherwise `no_detectable_difference` (never "equal").

### 6.2 Controls (the A/B is trusted only after they pass)

| Control | Pairs (A = degraded, B = normal unless noted) | Expected | Target per model |
|---|---|---|---|
| flat materials | `build --no-textures` render vs normal, 8 views | B wins `materials` | order-consistent correct ≥ 70 % (consensus ≥ 60 %), wrong ≤ 5 % |
| proxy furniture | `build --proxies` vs normal, 8 views | B wins `furniture` | same |
| direct light | `render --max-bounces 0` vs normal, 8 views | B wins `lighting` | same |
| low samples | `render --samples 4 --no-denoise` vs normal, 8 views | B wins `photo` | same |
| null identical | normal vs the byte-identical file, 8 views | T | 100 % T (determinism) |
| null re-encode | normal vs a JPEG q70 re-encode (PIL), 8 views | T | W ≤ 10 % |
| nuisance +0.3 EV | `--look-from` + `--ev-offset 0.3` vs normal, 8 views | none | report brighter-wins share; > 30 % → flag ΔEV next to every A/B pair with |ΔEV| > 0.3 |
| halo | on the four single-factor controls, share of non-target aspects that follow the target winner | low | reported; > 80 % → note "ask one aspect per call" for M7 |

A model that misses the known-direction targets is reported as "no signal from <model>"; the consensus then
uses the other model alone and the decision is marked `single_model`. The 8 control views: the 8 views of the
control project's AB renders with the highest furniture pixel share (render manifest `index_stats`), ties by
name. Controls are asked first (so a deadline cut still leaves them).

### 6.3 Pair sets of M6 and how they are made (orchestrated by R, commands by V and L)

`M5_LOOK_COMMIT = a2adcef58ede7e4f9e92dd6a847e1e4692075131`.
- `m5_vs_m6` for every AB project: A = `git show M5_LOOK_COMMIT:results/renders/<p>/<cam>_preview.jpg` (the
  committed M5 look, 1920 × 1080), B = the M6 look rendered from the **M5 cameras and M5 building**:
  building `git show M5_LOOK_COMMIT:results/furniture/<p>/building_final.json` → `out/ab/building_m5.json`;
  style = this run's `out/style.json`; `build --camera-policy m5 --out out/ab/scene --reuse`; `render --out
  out/ab/renders --alt-look "AgX - Punchy"` (all other flags as stage 10). Every AB camera's position and
  target must equal the M5 scene manifest's (`git show ...:results/renders/<p>/scene_manifest.json`) within
  1 mm; a camera that differs is dropped from the pair set with the reason listed.
- `look_alt` (lowest priority, asked last, skipped at the deadline): A = `out/ab/renders/<cam>_preview.jpg`,
  B = `<cam>_alt_preview.jpg`. Decides whether the default look should become `AgX - Punchy` in M7.
- `controls` for `--ab-controls` (default the first AB project): builds `out/ab/ctl_flat/` (`--no-textures`)
  and `out/ab/ctl_proxy/` (`--proxies`) with `--camera-policy m5`, renders of the 8 control views from them
  and from `out/ab/scene` with the control flags into `out/ab/ctl_<name>/renders`.
- `python -m wenart.vision_check realism-pairs --project-out out [--controls]` writes `out/ab/pairs.json`:
  `[{pair_id, set, cam, room_id, a, b, expected: "b"|"a"|"tie"|null, target_aspect, a_sha256, b_sha256}]`
  (paths relative to `out`).
- `realism --project-out out --model-key K --server URL --workers <seqs>` asks the pairs (deadline-aware);
  `realism-combine --project-out out` → `out/check/realism/realism_ab.json`, `realism_report.md`,
  `realism_contact_<set>_<n>.jpg` (rows A | B | outcomes, ≤ 300 KB each); `realism-summary --project-outs
  ... --out $RESULTS/realism/` → the cross-project `realism_summary.json/.md` with the decision table:

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|

  plus the controls table, position-bias index per model, ΔEV flags and the top decisive cues.

Copy: `out/ab/renders/*_preview.jpg`, `*_alt_preview.jpg`, `render_manifest.json`, `scene_manifest.json` and
`out/check/realism/*` → `$RESULTS/realism/<p>/` (the A side stays in git history; it is not copied again).
Expected cost: per model ≈ 174 main + 64 control + 32 null calls + 174 `look_alt` calls.

## 7. Intake, runner, gate validation, report (area IE)

### 7.1 Private projects (`wenart/intake.py`, `docs/intake.md`)

- Alias `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$`; refused when `projects/<alias>` exists or the path escapes the
  root. Missing folder → that project ends `needs_review: not uploaded`, others go on.
- `python -m wenart.intake stage <alias> --out <out_dir>/input [--root /workspace/projects-private]`: walks the
  upload, skips junk (`.DS_Store`, `__MACOSX/`, `._*`, `Thumbs.db`, `desktop.ini`), copies the remaining files
  into `--out` with **NFC-normalised** names (macOS writes NFD; Turkish names), refuses symlinks, caps 500 MB
  per file and 2 GB per project, keeps only `.pdf .dxf .dwg .jpg .jpeg .png .tif .tiff .yaml .yml .txt .md`
  (others listed as skipped), and writes `intake_manifest.json` (per file: original name, staged name, size,
  sha256, kept/skipped + reason; a DWG without a DXF of the same stem gets the note "DWG is not read; export
  DXF from the CAD program"). The original upload is never modified or deleted.
- `PRIVATE_SELFTEST=1`: the job copies `projects/synthetic-02` to `/workspace/projects-private/selftest-02`
  (once) and adds the alias; expected end state `needs_review` (scan-only project), all its files under
  `results-private/selftest-02/`, nothing under `$RESULTS/*/selftest-02`.
- `docs/intake.md` (for the user, simple English): create a RunPod **S3 API key** (console → Settings /
  Credentials → S3 API Keys; never paste it into the chat), install the AWS CLI, `aws configure --profile
  runpod`, upload with `aws s3 cp --recursive ... s3://h9er811d55/projects-private/<alias>/ --region EU-RO-1
  --endpoint-url https://s3api-eu-ro-1.runpod.io/` (with `AWS_REQUEST_CHECKSUM_CALCULATION=when_required`,
  `AWS_RESPONSE_CHECKSUM_VALIDATION=when_required`, `AWS_RETRY_MODE=standard`, `AWS_MAX_ATTEMPTS=10`), list,
  tell Claude only the alias; folder layout and optional `brief.yaml` / `style_photos/`; export DXF (and/or
  vector PDF) from CAD instead of DWG; download results from `s3://h9er811d55/results-private/<alias>/`;
  removal only by the user. What Claude sees of a private run (final report, contact sheets, review JPEGs)
  and what it never sees (the raw documents).

### 7.2 Runner and repository guards

- `scripts/gpu_run.py`: `collect` also walks `results-private/` into `runs/<job>/results-private/` (same caps,
  one total); after a successful collection the runner stops the pod at once (REST stop, then the usual
  terminate) instead of waiting for `--grace`; `GPU_PRIORITY = ["RTX PRO 4500", "RTX 4090", "RTX PRO 4000",
  "RTX A5000", "RTX A6000", "A40"]` (no L4).
- `.gitignore`: `/projects-private/`, `/results-private/`, `/outputs-private/`.
- `tests/test_private_guard.py`: every `results/<area>/<p>/` folder (areas `renders furniture polish gate
  check final run realism`) has a committed `projects/<p>/`; `git check-ignore` holds for the three private
  roots; no committed file contains `projects-private/` followed by an alias other than `selftest-02`.

### 7.3 Gate validation (`wenart/gate/validate.py`)

`python -m wenart.gate validate --project-out out` reads `gate/gate_calibration.json` `rates` (computed with
the thresholds in use) and `wenart/gate/validation.yaml` (`benign_accept_min: 0.95`,
`negative_reject_min: 0.90`), writes `gate/gate_validation.json` `{benign_accept, negative_reject, n_benign,
n_negative, pass_benign, pass_negative, decision: ok|flagged|polish_disabled, reasons}`: `polish_disabled`
when the negative limit fails (the final report then uses Cycles for every view of the project), `flagged`
when only the benign limit fails. Missing or incomplete calibration → `decision: not_validated` (flagged).

### 7.4 Final report (`wenart/report`)

- `needs_review` projects: `final_report.md` is the needs-review report (status, every reason, page table from
  `building.json`/`report.md`, debug images converted to JPEG ≤ 300 KB under `final/debug/`),
  `final_manifest.json` `status: needs_review`, exit 0.
- Gate validation section and its effect; camera policy and score per view; views per room as rendered (1–3);
  a stage table from `out/run/*.json` (status, seconds, reused); the window-pull EV per view.
- Uses `wenart.views.resolve_repo_path` for every repo-relative path.

## 8. Pod plan and budget

### 8.1 Time rule (measured on the RTX PRO 4500 in M5, critic-checked)

Per project ≈ 4 min + 0.63 min per view (+ 10 s per AI-furnished room) with polish, controls and gate
calibration; per pod fixed ≈ 19 min (boot 1.5, setup 4.4, server starts ≈ 11 for 3 starts, tests 0.7, copy
1.1). `--max-minutes 115` → `WENART_DEADLINE` = entry + 100 min → ≈ 80 min of project work per pod.

| Pod | Content | Estimate | Cost (≤ $0.74/h) |
|---|---|---|---|
| A | full run synthetic-01 + synthetic-03 (fewer views with the camera rule) | ≈ 85–90 min job, ≈ 95 pod-min | ≈ $1.2 |
| B | full run synthetic-04 + synthetic-05 (photos → 4 server starts) + `PRIVATE_SELFTEST=1` + AB `synthetic-01 synthetic-03` with controls on synthetic-01 | ≈ 75–80 min job (AB: 2 builds + 87 renders ≈ 13 min, controls ≈ 6 min, ≈ 500 calls per model ≈ 8–12 min) | ≈ $1.1 |

`python scripts/gpu_run.py run --job scripts/jobs/full.sh --gpu 'RTX PRO 4500' --disk 130 --max-minutes 115
--grace 600 --env RUN_PROJECTS=... [--env ...] --purpose "M6 ..."` (`RTX 4090` when the 4500 has no stock;
the runner stops the pod after collecting). Pods run one at a time, A first. Before pod A: the CPU suite, the
smoke e2e (§2.5) and `python -m wenart.run plan` for all five projects green in the session. A pod that the
deadline cuts exits 1; the same command resumes from the volume (fingerprints, render keys, attempts,
answers). Cap for M6: $4.00 in total; ask the user before going over it or the $10/day limit. Every pod is
logged in `docs/gpu-log.md`; no pod is left running.

## 9. Tests

CPU (`pytest -m "not gpu"`):
- run: ProjectRef paths (public, private, alias refusal, traversal), canonical hash (volatile keys at any
  depth, key order), fingerprints and reuse (outputs missing → re-run, `--force`), stage table commands
  (golden lists per stage), scheduler with an injected runner and fake clock (phases order; server sessions
  only when needed: 2/3/4 starts; needs_review stops a project and no server starts for it; deadline →
  incomplete; failed layout never reused), server context manager with a fake process (ready, early exit,
  timeout, deadline, TERM/KILL, pid file), copy mapping and filter (public and private layout, `--since`), run
  manifest (private details only in the private one), exit code rules; `full.sh` static checks (shebang,
  `set -Eeuo pipefail`, ERR trap, logs under `/workspace/logs`, flock, EXIT trap kills the vLLM pid); smoke
  e2e (§2.5, slow).
- synthetic: five projects generated, counts, truth equality (synthetic-04/05 in `test_matches_truth` and
  `test_evidence_matches_truth`), furniture-plan warning, style photo copied, room types pinned for all five.
- cameras: score parts on hand-made rooms, candidate grid, diversity and view-count rules, determinism,
  `m5` policy identical to the committed M5 scene-manifest cameras of synthetic-01 and -03 (positions and
  targets within 1 mm, from `git show a2adcef:...` or the committed `results/renders/<p>/scene_manifest.json`
  at that commit), projection with shift vs Blender (skip without Blender), search time.
- look (skip without Blender): one test per row of §5.
- realism: prompt/schema strictness, post-validation, outcomes W/L/T/NC per order pair, graded score, consensus,
  sign test values, bootstrap determinism, controls evaluation and `single_model`, decision rules, pairs file,
  fake client end to end, resumable answers, summary table.
- intake/guard/runner/gate/report: alias rules, junk skip, NFC names, caps, manifest; guard test; collect of
  `results-private` with a fake server; stop-after-collect; gate validate decisions; needs-review report;
  `resolve_repo_path`.

GPU (`pytest -m gpu` on the pod): `test_full_run.py` (every RUN_TEST project `ok` with every stage `ok` or
`reused`, a final report whose view count equals the render manifest; every NEEDS_REVIEW project
`needs_review` with ≥ 1 reason and no scene built in this run; selftest results only under `results-private`),
`test_render.py` (§4.2), `test_look_m6.py` (no red/teal cast in rooms with unverified pieces: |tint| ≤ 40;
kitchen counter index pixels mean display luminance ≥ 0.15; window clip ≤ 0.05 in ≥ 90 % of views; the four
dim synthetic-03 rooms below +6 EV; bedding/handles/skirting objects present in the scene manifest),
`test_realism.py` (≥ 95 % of realism calls answered per model; identical-pair control 100 % T; controls table
present; `realism_ab.json` valid), `test_polish.py` (adds: `gate_validation.json` present per polished project),
`test_check.py`, `test_furnish.py`, `test_polish_backend.py` as in M5.

## 10. Done criteria

CPU suite and the smoke e2e green here; `wenart.run plan` for all five projects; pods A and B exit 0 (a cut
pod resumed with the same command counts); synthetic-01, -03, -04, -05 `ok` end to end from their project
folders; synthetic-02 and `selftest-02` `needs_review` with their reports; GPU tests green; per-project gate
validation reported; the realism A/B decision reported with its controls (whatever it says); results,
previews and reports of the public projects committed under `results/`; `docs/plan.md`, `docs/progress.md`,
`docs/gpu-log.md`, `docs/synthetic.md`, `docs/intake.md`, `CLAUDE.md` (GPU default) updated; no pod running.
Items needing the user's OK or action are listed in progress.md: the M5 gate limits and advisory check, any
`polish_disabled` project, uploading real projects (S3 key, DXF export).

## 11. Risks

- A second Qwen start in the same pod was never measured (first CUDA-graph capture 138 s); the 4-start pod B
  estimate may be pessimistic or optimistic by a few minutes.
- Pod A has ≈ 10 min of margin; the deadline rule turns an overrun into `incomplete`, resumed by a second pod.
- The VLM judges may not see the controls (then the A/B is `not_measurable` and says so).
- New Poly Haven textures are first downloaded on the pod (≈ seconds each); a failed download falls back to the
  flat colour and is listed by `assets fetch`.
- The window pull changes the PNG that polish and gate read; the gate compares Cycles PNG and polished PNG, both
  with the same pull, and is re-validated per project.
- The S3 upload path is documented from the RunPod docs and a live 401 probe; it is tested only when the user
  creates a key. The private plumbing on the pod is tested with `selftest-02`.

## 12. Sources (checked 2 Oct 2026)

- Repo: `scripts/jobs/{polish,furnish,render}.sh`, `scripts/pod_entry.sh:149` (`git clean -fdxq`),
  `scripts/gpu_run.py:61,389-465`, `wenart/blender/{cameras,render,materials,parametric,shell,lighting}.py`,
  `wenart/vision_check/{expected,preference}.py`, `wenart/building.py:47-61`, M5 pod logs `runs/20261002-*`,
  `results/check/*/check_manifest.json` (advisory), `results/gate/*/gate_calibration.json` (`rates`).
- RunPod: https://docs.runpod.io/storage/s3-api (endpoint `https://s3api-eu-ro-1.runpod.io/`, bucket = volume
  id, S3 API key from the console only, supported operations, multipart), /storage/network-volumes,
  /pods/configuration/expose-ports (100 s proxy timeout), /get-started/credentials; live probe of the S3
  endpoint (HTTP 401 without credentials); botocore CHANGELOG 1.36.0 (default CRC32 checksums).
- vLLM v0.30.0 `docs/features/sleep_mode.md` (not used in M6).
- FastChat `fastchat/llm_judge/show_result.py` (swap rule: inconsistent → tie); Wang et al. 2023 "Large
  Language Models are not Fair Evaluators" (arXiv 2305.17926, position bias, balanced position calibration).
- Poly Haven API `https://api.polyhaven.com/files/<id>` for `oak_veneer_01`, `walnut_veneer`, `rough_linen`
  (CC0, https://polyhaven.com/license); Blender 5.2.2 look list (`AgX - Punchy`), `bmesh.ops.bisect_plane`,
  Light Path node outputs, `Camera.shift_x/shift_y`.
- GitHub API: repository `cihantanaydin-svg/WenArt_RUN` is public.
