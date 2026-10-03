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
the live endpoint. A completeness critic re-checked the numbers, and three reviewers checked this spec against
the code, the rules and the measurements (41 findings, all applied; the shift projection formula of §1.3 was
verified against Blender's `world_to_camera_view` to 0.011 px, and the `m5` camera policy reproduces all 87
committed M5 cameras within 1 mm).

Scope:
1. One-command full run: Python orchestrator `wenart/run` + bash job `scripts/jobs/full.sh` (§2).
2. Two new synthetic projects `synthetic-04`, `synthetic-05` and the fixes they need (§3).
3. Camera search with straight verticals (§4).
4. Cycles realism package (§5).
5. Realism A/B measurement with controls (§6).
6. Real-project intake path, runner changes, per-project gate validation, final-report changes (§7).
7. Pod runs: all four rendered synthetic projects end to end, synthetic-02 and a private-path self-test as
   `needs_review`, the realism A/B (§8).

Out of scope: DWG reading (LibreDWG never produced geometry, `results/bakeoff/dwg_roundtrip.json`; users export
DXF), the scan/photo recognition path in the pipeline (still `needs_review`), open balconies, doorless
openings, angled walls, a second style of `styles:`, the SigLIP/absolute realism score, vLLM sleep mode.

## 0. Decisions (changes to `docs/plan.md` and `CLAUDE.md`)

| Before | Now | Why |
|---|---|---|
| plan §6 M6: "3+ full project runs" on the user's projects | runs on synthetic-01, -03, and the new -04, -05 (+ synthetic-02 as `needs_review`); real projects run with the same command as soon as the user uploads them (§7.1) | `projects/` holds no real project; the repo is **public**, so a real project can never be committed |
| plan line "real projects in `projects/<name>/`, git-ignored if confidential" | private projects live on the network volume under `/workspace/projects-private/<alias>/`, uploaded by the user with the RunPod S3 API; outputs stay in `/workspace/outputs-private/`, a small allow-listed result set in `/workspace/results-private/`, collected into the git-ignored `runs/` | `pod_entry.sh` runs `git clean -fdx` in `/workspace/repo` on every start; the repo is public; files go user → RunPod only, never through GitHub or the model context |
| three job scripts (`render.sh`, `furnish.sh`, `polish.sh`), each a piece; polish starts from the committed `results/furniture/<p>/building_final.json` | one job `scripts/jobs/full.sh` → `python -m wenart.run pod` runs stages 0–17 for every project; no fallback to committed buildings | polish.sh is 694 lines of array state; a Python orchestrator is unit-testable and owns server sharing, needs_review, deadlines and fingerprints. The old jobs stay as they are (not extended) |
| layout used an unpinned Qwen with `image:1` | layout uses the check's pinned Qwen server (`check.yaml models.qwen`, `image:2`, same served name) | one server start shared by layout and check sessions |
| cameras: 3 fixed rules per room, 1.4 m, looking 0.1 m down | searched cameras for full runs: ray-cast score, fixed height 1.25 m, pitch 0, lens shift `shift_y = −0.10`, 1–3 views per room by area; the M5 rule set stays as `camera_policy: m5` (still the default of the library and the build CLI; the orchestrator passes `search`) | 17/87 M5 views framed bare walls, 12/87 were blocked, 52/87 showed < 1 % floor. Fixed height: the scorer has no optimum in height (it always takes the lowest offered) |
| realism judged with one tie-allowed question (`preference.py`) | new pairwise forced-choice protocol per aspect, both orders, both models, validated by known-direction and null controls (`realism.py`); `preference.py` unchanged (info) | M5: 90 % "same", 0 of 45 pairs order-consistent for both models; the tie option hides a weak signal |
| CLAUDE.md: default GPU RTX A5000 (then 4090, A6000) | default RTX PRO 4500 (32 GB), then RTX 4090 (24 GB), then RTX PRO 4000; never L4; `GPU_PRIORITY` in `gpu_run.py` in that order | A5000/A40/A6000 had no stock on 2 Oct; every M5/M6 timing is measured on the PRO 4500 / 4090. Reported to the user |
| pods kept running for the whole `--grace` | the runner stops the pod right after a successful collection (the in-pod watchdog and job-end stop stay armed) | ≈ 7 idle billed minutes per pod in M5 |
| gate thresholds calibrated once (M5, synthetic-01/03), polish then gate | every project with polish on runs `gate calibrate` **before** its polish and is **validated**: benign accepted ≥ 95 %, negatives rejected ≥ 90 %; a project failing the negative limit, or without a complete calibration, gets no polish (Cycles finals) | the M6 look changes the textures the gate sees; new projects were never calibrated; synthetic-01 is at 0.903 negatives with the current thresholds |
| plan §6 M6 budget 3–5 h, $2–4 | cap $4.00 for M6 pods; three planned pods ≈ $2.7; ask the user before going over | CLAUDE.md limits |

M5 items still waiting for the user's OK stay as they are and are repeated in the M6 report: the looser gate
limits (`calibration.user_ok: pending`) and the advisory vision check.

## 1. Shared contracts (read before any area)

### 1.1 Projects and paths (`wenart/run/projects.py`, committed foundation)

```python
@dataclass(frozen=True)
class ProjectRef:
    name: str            # public project name or private alias
    private: bool
    project_dir: Path    # projects/<p>  |  /workspace/outputs-private/<a>/input/<a> (staged copy, §7.1)
    out_dir: Path        # outputs/<p>   |  /workspace/outputs-private/<a>
    results_dir: Path    # $RESULTS      |  /workspace/results-private/<a>
    def results_area(self, area) -> Path   # $RESULTS/<area>/<p>  |  results-private/<a>/<area>
def check_name(name) -> str                # public project names: ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$
def check_alias(alias) -> str              # private aliases: ^real-[0-9]{2,3}$ or the reserved selftest-02
def public_project(name, results, repo_root=REPO_ROOT) -> ProjectRef
def private_project(alias, private_root=..., outputs_root=..., results_root=..., repo_root=REPO_ROOT) -> ProjectRef
```
- Public results keep the committed layout `$RESULTS/<area>/<p>/` with areas `renders`, `furniture`, `polish`,
  `gate`, `check`, `final`, `run` (new: stage records and log tails), `realism` (new, §6).
- Private results use an allow-listed subset (§2.1) one level down: `/workspace/results-private/<a>/<area>/`.
  The job links `$JOB_DIR/results-private/<a>` → that folder; the runner collects it (§7.2). Job-level private
  files (`_run_manifest.json`, `_logs/`) are real files in `$JOB_DIR/results-private/`.
- **Paths given to CLIs and paths in manifests**: the orchestrator runs every CLI with cwd = repo root and
  passes paths as `views.repo_path_text(p)` (repo-relative when inside the repo, else absolute), so public
  manifests stay repo-relative and private ones carry absolute volume paths. Every reader resolves them with
  `views.resolve_repo_path` / `views._resolve_repo_path` (absolute stays, relative joins the repo root). Paths
  relative to the folder of a JSON (M5 §1.1) stay relative. Areas L, V and IE check their writers and readers;
  the smoke e2e of §2.5 runs one project in a temp dir outside the repo.
- Nothing about a private project (room names, file names, labels) is printed to `job.log`: the orchestrator
  prints only `<alias> <stage> <status> <seconds>s`; every subprocess writes its output to
  `<out_dir>/run/logs/<stage>.log`. `wenart.run pod` catches every exception: when a private project is in the
  run, the traceback goes to `$JOB_DIR/results-private/_logs/orchestrator.log` and `job.log` gets only
  `orchestrator error <ExceptionType>`; `wenart.run copy` prints only file counts.

### 1.2 Stage records and fingerprints (`wenart/run/state.py`; hashes in `wenart/canonical.py`)

Per project and stage: `<out_dir>/run/<stage>.json`

```json
{"schema_version": "0.1", "kind": "stage_record", "project": "synthetic-04", "stage": "layout",
 "rc": 0, "status": "ok|reused|warning|skipped|failed|needs_review|incomplete", "seconds": 91.2,
 "fingerprint": "<sha256>", "inputs": {"<path>": "<canonical sha256>"}, "outputs": ["building_furnished.json"],
 "started_utc": "...", "git_commit": "...", "log": "logs/layout.log", "note": null}
```
- `wenart.canonical.canonical_sha256(path)` (committed, stdlib only; `wenart/run/state.py` re-exports it;
  `build.py` imports `wenart.canonical`, never `wenart.run`): for `.json` files the sha256 of the sorted compact
  JSON without the **volatile keys** `created_utc`, `updated_utc`, `generated_utc`, `started_utc`,
  `finished_utc`, `seconds`, `latency_s` at any depth; raw bytes otherwise; a folder hashes its sorted
  `(relpath, sha)` list.
- `fingerprint = sha256(json([stage, STAGE_VERSION[stage], args, sorted(inputs), code_hash(stage)]))`;
  `code_hash` = sha256 of the source files that implement the stage (listed per stage in `wenart/run/stages.py`,
  plus the package `__init__.py` of every listed module). For every stage reused by its fingerprint (and the
  gate calibration) the list covers the whole `wenart` import closure of the stage's CLI, imports inside functions
  included (`tests/test_run_stages.py` computes it with `ast` and fails on a missing file), plus the data files
  it reads, so a committed fix in an imported module (e.g. `synthetic/blocks.py` for the pipeline,
  `blender/proxies.py` for fit) is never hidden by a reuse.
- A stage with `reuse: fingerprint` is skipped (status `reused`) when the stored fingerprint equals the new
  one, the stored status is `ok`, `warning` or `reused` (a reused record carries over the status of the run
  that made the outputs, so a third run of an unchanged project still skips) and every listed output exists. Stages with their own
  fine-grained reuse (build `--reuse`, render `render_key`, polish `attempt_key`, check answers by call key)
  are always invoked.
- Status meanings: `warning` = rc ≠ 0 (or a reported problem) on a stage whose failure is not terminal (§2.2
  column), the project goes on, `note` holds the reason; `skipped` = not needed, `note` is one of `private only`,
  `no style photos`, `polish off`, `no empty room`, `smoke profile`, `gate not validated`, `not in this phase`;
  `incomplete` = cut by the deadline (rc 3 or an output file with `incomplete: true`, §2.2).
- A project's state: `needs_review` when stage 1 (or 0) says so; `failed` when any stage failed; `incomplete`
  when any stage is incomplete; else `ok`. Only the project stages 0–17 count: the AB stages of a project that is
  also in `--ab` never decide its state or its test lists (a failed or incomplete AB stage fails the run's exit
  code on its own, `look_alt` never).
- `build.build_fingerprint` hashes the building with `canonical_sha256` (area L), so a re-run pipeline that
  only changed `created_utc` never rebuilds the scene.

### 1.3 Cameras (`wenart/blender/cameras.py` plan dict, scene manifest, projection)

New plan / scene-manifest camera fields (`wenart/blender/schemas.py`, committed, optional for old manifests):
`shift_x` (number, default 0), `shift_y` (number, default 0), `policy` (`"search"` | `"m5"`), `score`
(object or null: `total`, `furniture`, `openings`, `floor`, `depth`, `penalties`, `blocked`). Names stay
`cam_<room_id>_<i>`, `i = 1..n`. `target` is still a world point (search: position + 1 m along the yaw at
the same height).

Projection with shift (sensor fit HORIZONTAL; Blender's shift unit is the larger image side = W; verified
in Blender 5.2.2): `u = W/2 − shift_x·W + f·(d·r)/(d·f)`, `v = H/2 + shift_y·W − f·(d·u)/(d·f)` (pixel origin
top-left). Inverse: `a = (col + 0.5 − W/2 + shift_x·W)/f`, `b = −(row + 0.5 − H/2 − shift_y·W)/f`. Readers that
project or unproject (`vision_check/expected.py` `project_points`, `unproject_pixels`; `geom2d.point_in_frustum`
and the frustum tangents) use `shift_x/shift_y` when present (default 0). The plan-crop view cone uses the
horizontal field of view only (unchanged; `shift_x` is always 0).

### 1.4 VLM server (`wenart/run/servers.py`)

Port of `polish.sh` `start_server` / `stop_server` / `server_args` / `server_seqs`: model id, revision and
`server_flags` from `check.yaml models.<key>`; `vllm serve <id> --revision <rev> --served-model-name <id>
--port 8001 --limit-mm-per-prompt '{"image":2}' --gpu-memory-utilization 0.90`; below 40 GB VRAM
`--quantization fp8 --max-model-len 8192 --max-num-seqs 2`, else `--max-model-len 16384 --max-num-seqs 4`;
env `VLLM_USE_FLASHINFER_SAMPLER=0`; log `/workspace/logs/vllm-<key>.log` (copied as a 200-line tail); `/health`
every 10 s; early exit → last 40 log lines into `<out>`-independent `$JOB_DIR/server-<key>.log` (never job.log
when a private project is in the run); give up after `SERVER_WAIT_S` (1500 s) or at the deadline; stop = TERM,
wait 60 s, KILL. The pid goes to `$WENART_JOB_DIR/vllm.pid` (the bash EXIT trap kills it). A context manager:
`with server("qwen", deadline) as url: ...`. `--vlm-url URL` (smoke profile, §2.5) skips starting and uses an
external server. `seqs` (2 or 4) is the `--workers` of every VLM stage.

### 1.5 Ownership (parallel implementation)

| Area | Owns |
|---|---|
| R run | `wenart/run/*` (except `projects.py`, foundation), `scripts/jobs/full.sh` (new), `wenart/furniture/layout.py` (transport-error exit code only), `tests/fakes/fake_vlm.py` (new), `tests/test_run_*.py`, `tests/test_full_job.py`, `tests/test_layout.py`, `tests/gpu/test_full_run.py`, `pyproject.toml` (register the `slow` marker) |
| S synthetic | `wenart/synthetic/*`, `wenart/building.py` (room keywords), `projects/synthetic-04/`, `projects/synthetic-05/` (generated), `docs/synthetic.md`, `tests/test_synthetic.py`, `tests/test_pipeline.py`, `tests/test_building.py` |
| C cameras | `wenart/blender/cameras.py`, `wenart/blender/camsearch.py` (new), `wenart/blender/geom2d.py` (frustum with shift), `project_points`/`unproject_pixels`/`focal_px` in `wenart/vision_check/expected.py`, `tests/test_blender_cameras.py`, `tests/test_blender_geometry.py`, `tests/test_camsearch.py` (new), `tests/test_vision_check_expected.py`, `tests/gpu/test_render.py` |
| L look | `wenart/blender/{materials,parametric,furniture,shell,lighting,render,build,cli,schemas}.py`, `wenart/style/{vocabulary,profile}.py`, `wenart/assets/*`, `tests/test_blender_{build,look,render,furniture,materials,glass}.py`, `tests/test_m5_e2e.py`, new Blender CPU tests, `tests/gpu/test_look_m6.py` (new) |
| V realism | `wenart/vision_check/realism.py` (new), `wenart/vision_check/{cli,schemas}.py` (realism commands and schemas), `check.yaml` `realism:` block, `wenart/recognition/vlm_client.py` (system prompt argument, if missing), `tests/test_realism_ab.py` (CPU; `tests/` has no `__init__.py`, so a CPU `test_realism.py` would clash with the GPU file of the same base name), `tests/gpu/test_realism.py` |
| IE intake + report | `wenart/intake.py` (new), `docs/intake.md` (new), `.gitignore`, `scripts/gpu_run.py`, `wenart/gate/validate.py` + `wenart/gate/validation.yaml` (new), `wenart/gate/__main__.py` (`validate` command), `wenart/report/*`, `tests/test_intake.py`, `tests/test_private_guard.py`, `tests/test_gpu_run.py`, `tests/test_report.py`, `tests/test_gate_validate.py`, `tests/gpu/test_polish.py`, `tests/gpu/test_check.py` |

Files outside this table are changed only by the integrator (foundation files: `wenart/canonical.py`,
`wenart/run/projects.py`, `wenart/views.py` helpers, `cameras.plan_cameras` signature, camera schema fields).
Interfaces between areas are the ones in §1, §2.2 and §6.3.

## 2. One-command full run (area R)

### 2.1 Commands

```
python -m wenart.run plan --projects synthetic-01,synthetic-03 [--out run_plan.json]
python -m wenart.run pod  --projects "synthetic-01 synthetic-03" [--private "real-01"] [--private-selftest]
                          [--ab "synthetic-01 synthetic-03"] [--ab-controls synthetic-01] [--ab-phase all|render|judge]
                          --results $RESULTS [--profile full|smoke] [--force stage[,stage]] [--vlm-url URL]
python -m wenart.run copy --projects ... [--private ...] [--ab ...] --results $RESULTS [--since STAMP]
```
- `plan` (CPU, session or pod): runs stage 1 (pipeline) for each project and writes per project: status,
  levels, rooms, empty rooms, views (§4.1 area rule, `camsearch.room_view_count`: the area of the room polygon),
  minutes (§8.1 rule), server starts, and a suggested pod
  split: first-fit under `100 − fixed(server starts) − 8` min of project work per pod (≤ 73 min with 3 server
  starts, ≤ 71 min with 4). `needs_review` projects get their report and no pod time.
- `pod` (inside `full.sh`): the whole run. Exit 0 when every project ended `ok` or `needs_review`, no AB stage
  failed or ended incomplete (`look_alt` excluded), and every GPU test group passed; else 1.
- `--ab-phase render`: AB prepare, builds, renders and control renders only; `judge`: realism calls, combine and
  summary only (the AB files from an earlier pod are on the volume); `all` (default): both. **`judge` needs the
  same control project as `render`** (`--ab-controls`, `AB_CONTROL_PROJECT` in `full.sh`); without it, the one AB
  project whose `ab/control_views.json` the render pod wrote is used (printed), and the run is refused (exit 2)
  when several have one. `judge` reuses each project's complete `ab/pairs.json` (`ab_pairs` `reused`: every pair's
  images exist, control sets present for the control project) instead of rebuilding it; any rebuild of a pairs
  file keeps `--controls` when the stored file has control sets.
- `copy`: copies the small result files into the results layout, only files newer than `--since` (a stamp
  file) unless omitted. Public filter (as `polish.sh copy_files`): `*.json`, `*.md` (< 8 MB), `*_preview.jpg`,
  `*_alt_preview.jpg`, `*_gate.jpg`, `*_check.jpg`, `*_plan.jpg`, `contact_*.jpg`, `debug/*.jpg` (< 301 KB),
  last 400 lines of `*.log`. Mapping (public, `<p>`):

| From `out/` | To `$RESULTS/` |
|---|---|
| `*.json`, `*.md`, `style_photos/*.json` | `furniture/<p>/` (`style*.json` also → `renders/<p>/`) |
| `layout_debug/*.json`, `layout_debug/*.jpg` | `furniture/<p>/layout_debug/` |
| `scene/*.json`, `scene/*.log`, `renders/` | `renders/<p>/` |
| `controls/`, `controls/hide_*/` | `renders/<p>/controls/`, `.../hide_*/` |
| `polish/` (+ `sweep/`, `smoke/`), `gate/`, `check/` | `polish/<p>/`, `gate/<p>/`, `check/<p>/` |
| `final/`, `final/debug/` | `final/<p>/`, `final/<p>/debug/` |
| `run/*.json`, `run/logs/*.log` (tails) | `run/<p>/`, `run/<p>/logs/` |
| `ab/renders/*`, `ab/cameras_check.json`, `ab/pairs.json`, `check/realism/*` | `realism/<p>/` |

  **Private projects use an allow-list only**: `final/final_report.md`, `final/final_manifest.json`,
  `final/*_final_preview.jpg`, `final/contact_*.jpg`, and `run/<stage>.json` without its `inputs` map. Never
  copied for private projects: `debug/`, `final/debug/`, `*_plan.jpg`, `building*.json`, `report.md`,
  `intake_manifest.json`, `layout_debug/`, `check/answers_*.json`, logs. They stay under
  `/workspace/outputs-private/<a>/` for the user to download over S3 (§7.1).

### 2.2 Stage table (per project; batched over all projects by GPU holder)

PY = `/workspace/venv/bin/python`, POLISH_PY = `/opt/wenart/venv-polish/bin/python`. `out` = `out_dir`
(passed as `repo_path_text`).

| # | Stage | Command (existing CLIs unless marked new) | Holder | Reuse | On failure |
|---|---|---|---|---|---|
| 0 | intake (private only) | `PY -m wenart.intake stage <alias> --out out/input/<alias>` (§7.1), also when the upload folder is missing (the CLI then writes a fresh `needs_review` manifest and removes an older staged copy, so an earlier ok intake never reaches the report) | – | fingerprint (of the upload's listing: relative path, size, mtime of every file, never its bytes; the intake's own sha256 of the kept files drives the later stages) | exit 4 (or manifest `status: needs_review`) → `needs_review` (not uploaded, a name collision, no document, a cap; the note is one of the intake's fixed reasons, never a file name); other → failed |
| 1 | pipeline | `PY -m wenart.ingest.pipeline <project_dir> --out out` | – | fingerprint (project files + `wenart/ingest/**`, `wenart/synthetic/**` (block types and sizes), `wenart/building.py`, `wenart/geometry.py`, `wenart/schema/**`) | exit 1 + building status `needs_review` → **needs_review** (stop); other → failed |
| 2 | photos (style photos in the brief or folder) | `PY -m wenart.style.photos read <photos> --model-key <k> --server <url> --out out/style_photos/passes.json` for glm and qwen; `PY -m wenart.style.photos combine out/style_photos/passes.json --out out/style_photos/terms.json` | VLM (GLM session, then Qwen session) | skipped when `passes.json` holds a valid answer (data, no error) of both check.yaml model **ids** for every current photo sha256 (the revision is not recorded; `--force photos` after a revision change) | warning (style from the brief only) |
| 3 | style | `PY -m wenart.style <project_dir> --out out/style.json [--photo-terms out/style_photos/terms.json]` (terms only when complete) | – | always (deterministic, < 1 s) | failed |
| 4 | assets | `PY -m wenart.assets fetch --style out/style.json --assets /workspace/assets --size 2k` | – | always (cached) | warning |
| 5 | fit | `PY -m wenart.furniture.fit out/building.json --catalog wenart/furniture/catalog.json --out out/building_fitted.json --assets /workspace/assets` | – | fingerprint; never reused while the output has a piece whose model download failed | failed; a failed model download (fit exits 0 with a parametric fallback, `fallback_reason: download of ...`) → warning `N model download(s) failed: parametric fallback`, and the next run fits and downloads again |
| 6 | layout (rooms without documented furniture; skipped `no empty room`) | `PY -m wenart.furniture.layout out/building_fitted.json --style out/style.json --server <url> --model Qwen/Qwen3-VL-8B-Instruct --out out/building_furnished.json --debug out/layout_debug --passes 2` | VLM Qwen | fingerprint (+ Qwen id and revision) | failed (never reused) |
| 7 | decor | `PY -m wenart.furniture.decor <furnished or fitted> --out out/building_decor.json` | – | fingerprint | failed |
| 8 | refit | `PY -m wenart.furniture.fit out/building_decor.json ... --out out/building_final.json` | – | fingerprint (as fit) | failed; failed model download → warning (as fit) |
| 9 | build | `PY -m wenart.blender.cli build --building out/building_final.json --style out/style.json --assets /workspace/assets --out out/scene --preview-samples 32 --camera-policy search --reuse` | Blender | build fingerprint | exit ≠ 0 → failed (stage 1 already stopped needs_review buildings; exit 2 here is a refused request or a usage error; note = last line of build.log) |
| 10 | render | `PY -m wenart.blender.cli render --scene out/scene/scene.blend --out out/renders --cameras all --samples $RENDER_SAMPLES --res 1920x1080 --exposure auto --white-balance auto` | Blender | render_key | exit 3 → incomplete; else failed |
| 11 | controls | `PY -m wenart.vision_check select-controls --project-out out`; when `check/controls.json["hide_sets"]` is not empty: `PY -m wenart.blender.cli render --scene out/scene/scene.blend --out out/controls --hide-sets "<hide_sets>" --look-from out/renders/render_manifest.json` (same string as polish.sh's `HIDE_SETS` line) | Blender | render_key | warning (check stays advisory) |
| 12 | gate calibrate + validate (polish on; skipped `polish off`) | `POLISH_PY -m wenart.gate calibrate --project-out out`; `PY -m wenart.gate validate --project-out out` (§7.3), always after calibrate (a failed calibrate's file, stale or partial, is first moved to `gate/gate_calibration.failed.json`, so `gate_validation.json` always describes this run) | gate models | calibrate: fingerprint in the gate record (args, `(camera, scene_sha256, render_key)` of `renders/` and `controls/hide_*/` render manifests, `check/controls.json`, `polish/sweep/polish_manifest.json`, the gate code incl. `thresholds.yaml`); a complete calibration (`incomplete: false`, rates) whose fingerprint matches is reused (step `calibrate` with `reused: true`, note `(calibration reused)`) and never moved aside; `--force gate` recalibrates. validate: always | calibration incomplete → incomplete; calibrate exit ≠ 0 → warning, no polish; validation decides stage 13 |
| 13 | polish (decision `ok` or `flagged`; else skipped `gate not validated`) | `POLISH_PY -m wenart.polish run --project-out out` (`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`) | diffusion | attempt_key | rc 1 → warning (views keep Cycles) |
| 14 | expected + plan crops | `PY -m wenart.vision_check expected` / `plan-crops --project-out out` | – | always | failed |
| 15 | check (per model session) | `vision_check run --model-key K --server URL --kinds cycles,polished --workers <seqs>`; `preference --kinds polished`; `style-photo --photo tests/fixtures/style_photo_synthetic-03_salon.jpg --out out/check/style_photo_test.json` (every public project: 1 call per model, read by `tests/gpu/test_check.py::test_style_photo_test`) | VLM Qwen, then GLM | answers by call key | failed |
| 16 | combine | `vision_check combine`, `calibrate` | – | always | failed |
| 17 | report | `PY -m wenart.report final --project-out out` (+ `--private` for a private project; also for needs_review, §7.4) | – | always | failed; exit 1 with `final_manifest.json` `stages.render: not_run` (written by this run) for a project that already ended `incomplete` or `failed` → warning `no renders in this run` (a deadline cut before the first render stays `incomplete`) |

Deadline cuts are read from the outputs, whatever the rc: `polish/polish_manifest.json`,
`gate/gate_calibration.json`, `check/answers_<slug>.json`, `check/realism/answers_<slug>.json` with
`incomplete: true`, or render exit 3 (`cli.main` passes 3 through; area L) → the stage is `incomplete`.
`check/answers_<slug>.json` is read after each step that writes it (`run`, then `preference`), and a cut seen
once stays a cut: a preference that asks nothing rewrites the file with `incomplete: false`.

AB stages (§6.3) run inside the same phases for the projects in `--ab`. GPU tests run once at the end (§2.4).

### 2.3 Scheduler

Phases, each over all active projects in the given order, stopping a project at its first terminal state:
1. CPU: intake, pipeline, fit; for projects with style photos whose `passes.json` is complete (stage 2 reuse
   rule): photo combine + style with `--photo-terms`; every other project: style without terms. AB prepare
   part 1 (§6.3) for AB projects not in `--projects`.
2. VLM GLM session — only when some project has style photos without a valid GLM answer: photos (glm).
3. VLM Qwen session — only when some project needs a layout or Qwen photo answers: photos (qwen); photo
   combine and style again with `--photo-terms` only for projects that got new photo answers in this run (fit
   reads no style, so its fingerprint never changes here); layout (its deadline estimate counts its calls one
   at a time: the layout CLI sends them sequentially).
4. CPU: assets, decor, refit; AB prepare part 2 (§6.3).
5. Blender: build, render, controls for every project; AB builds, renders, `cameras_check.json`, control-view
   choice (`realism.control_views`) and control renders.
6. Diffusion: per project with polish on: gate calibrate → gate validate → polish when the decision allows it.
7. CPU: expected, plan crops; AB pairs files (`realism-pairs`; `judge`: the render pod's complete file reused,
   §2.1).
8. VLM Qwen session: check run, preference, style-photo test, realism (AB; `look_alt` only when
   `now + est(look_alt) + est(GLM start + GLM non-look_alt realism + GLM check) < deadline`).
9. VLM GLM session: the same.
10. CPU: combine, calibrate, realism-combine, realism-summary, report for every project (also needs_review
    and incomplete ones).
11. One copy of the small result files (as `wenart.run copy`, under the job's copy lock `WENART_COPY_LOCK`, so
    the private allow-list under `results-private/<alias>/` exists for the tests), GPU tests (§2.4), then
    `run_manifest.json`.

Rules:
- `WENART_DEADLINE` (epoch s, set by `pod_entry.sh` = entry + MAX_RUNTIME_S − 900): a heavy stage (build,
  render, controls, gate, polish, any server start, any VLM stage) starts only when `now + estimate(stage) <
  deadline`. Estimates (§8.1): build 60 s; render 8 s per view + 60 s; control renders 8 s per view; gate
  calibrate 150 s; polish 20 s per view; server start 300 s Qwen / 150 s GLM; VLM calls 4.4 s / seqs per call
  (2.1–2.4 s wall at 2 in flight, M5 runs 1b/2). A project whose stage cannot start becomes `incomplete`.
  Phases 10–11 always run.
- Timeouts: phases 1–9 `max(60, deadline − now)`; phases 10–11 `max(300, deadline + 600 − now)` per stage (the
  watchdog fires at `deadline + 900`; the EXIT-trap copy needs ≈ 1 min). On timeout TERM then KILL, status
  `incomplete`.
- Server sessions are skipped when no project needs them (3 starts without photos, 4 with uncached photos, 2
  with no empty room and no photos, 2 for `--ab-phase judge`).
- `--force stage,...` ignores the fingerprint for those stages.
- **Outputs of earlier jobs.** Before its first stage, a public project's out_dir (also an AB-only project's) that
  exists, is not empty and has no `run/` folder (written only by `wenart.run`) holds outputs of an earlier job:
  on the volume, `outputs/synthetic-01` and `outputs/synthetic-03` of the M5 `polish.sh` (renders and previews of
  cameras the M6 search no longer makes, an old polish manifest, `controls/hide_*`, ...). It is renamed, never
  deleted, to `<archive root>/<name>-<UTC stamp>` (`-2`, `-3`, ... when taken); archive root =
  `$WENART_OUTPUTS_ARCHIVE`, else `<repo>/../outputs-archive` (pod: `/workspace/outputs-archive`, outside the
  repo, so `pod_entry.sh`'s `git clean` never touches it). The move is printed, recorded in the run manifest
  (`archived_outputs` of the project or AB entry) and in the note of the project's first stage record that is
  not a skip (e.g. `pipeline`: `earlier outputs without run records moved to ...`). A failed rename is noted the
  same way and the run goes on. Private out_dirs are created by `wenart.run` and are never moved this way.
- `run_manifest.json` in `$RESULTS` (public projects with all details; private aliases with their state only)
  and `$JOB_DIR/results-private/_run_manifest.json` (private details): per project state and stage list
  (status, seconds, note), per phase start/end, server starts (seconds to ready), totals, deadline, profile,
  git commit.

### 2.4 `scripts/jobs/full.sh` and GPU tests

Bash with `#!/usr/bin/env bash`, `set -Eeuo pipefail`, ERR trap (line + command into the log), TERM → exit
143, logs under `/workspace/logs/full-<job>.log` (tee), the same exports as `polish.sh`
(`WENART_BLENDER=$WS/tools/blender/blender`, `HF_HOME=/opt/wenart/hf`, `HF_XET_HIGH_PERFORMANCE=1`,
`WENART_OUTPUTS=/workspace/repo/outputs`, `CHECK_MODELS="qwen glm"`), the cgroup CPU thread budget of
`polish.sh` (OMP/OPENBLAS/MKL/NUMEXPR/VECLIB/OPENCV threads), `bash scripts/pod_setup_polish.sh` with all parts
(venv, models, check), then `HF_HUB_OFFLINE=1`, a background copy loop every 300 s under `flock` calling
`$PY -m wenart.run copy ... --since $COPY_STAMP`, then `$PY -m wenart.run pod ...`. EXIT trap: kill the pid in
`$WENART_JOB_DIR/vllm.pid`, stop the copy loop, one full copy, copy this job's vLLM/setup logs (tail 200) to
`$RESULTS/logs/` — or to `$JOB_DIR/results-private/_logs/` when any private project is in the run.
Env (one of `RUN_PROJECTS`, `PRIVATE_PROJECTS`, `AB_PROJECTS` required): `RUN_PROJECTS`, `PRIVATE_PROJECTS`,
`PRIVATE_SELFTEST=1`, `AB_PROJECTS`, `AB_CONTROL_PROJECT`, `AB_PHASE` (all), `RUN_FORCE`, `RENDER_SAMPLES` (128).

GPU tests (after the last server stopped, junit into `$RESULTS/junit-*.xml`; the orchestrator exports every
list, empty when no project qualifies, so a test never falls back to old outputs on the volume):
`PY -m pytest -m gpu tests/gpu/test_full_run.py tests/gpu/test_render.py tests/gpu/test_look_m6.py
tests/gpu/test_furnish.py tests/gpu/test_check.py tests/gpu/test_realism.py` and `POLISH_PY -m pytest -m gpu
tests/gpu/test_polish.py tests/gpu/test_polish_backend.py`, with `RUN_TEST_PROJECTS` (ok public projects),
`NEEDS_REVIEW_TEST_PROJECTS`, `RENDER_TEST_PROJECTS`, `FURNISH_TEST_PROJECTS` (ok projects with ≥ 1
AI-furnished room), `CHECK_TEST_PROJECTS`, `POLISH_TEST_PROJECTS` (ok projects with polish on and gate decision
`ok` or `flagged`), `GATE_TEST_PROJECTS` (projects that ran gate calibrate), `AB_TEST_PROJECTS`,
`SELFTEST_TEST_ALIAS=selftest-02` (only with `PRIVATE_SELFTEST=1`: synthetic data, the only private alias a test
may see). Other private projects are never in a test list. Test groups with an empty list are skipped.

### 2.5 Smoke profile (CPU, for the session)

`--profile smoke`: render `--res 480x270 --samples 16 --device cpu`, AB renders likewise, builds
`--preview-samples 4` (the top-down previews on the CPU: 32 samples took 55 of a 66 s build), controls 2 views, no
gate/polish (skipped `smoke profile`), `--vlm-url` required (the fake server), no GPU tests, private roots
given by `--private-root/--private-outputs/--private-results` (temp dirs). `tests/fakes/fake_vlm.py`: stdlib
`http.server` on a free port with `/health`, `/v1/models`, `/v1/chat/completions` answering a minimal valid
instance of the request's JSON schema (enum → first value, integer → minimum, number → minimum or 0, string →
"", array → `minItems` copies, object → required keys), deterministic. `tests/test_run_e2e.py` (marked `slow`,
skipped without Blender) runs synthetic-04 + synthetic-02 + a private copy of synthetic-02 (alias
`selftest-02`) + a private copy of synthetic-04 (alias `real-01`, uploaded into the temp private root: the private
path through intake, build, render, check and report with absolute paths) + AB on synthetic-01 (2 cameras,
controls on synthetic-01) with the smoke profile end to end and checks the run manifest, stage records, reports,
the private allow-list and that nothing private reaches `$RESULTS` or the job log.

### 2.6 Fixes the full run needs

- `layout.py`: `Proposal.transport_error: bool = False`, set by `LayoutClient.propose` only when its last
  attempt raised `VLMError` (or the model lookup failed); `main` exits 3 and writes no output file when any
  proposal has `transport_error`; fake clients returning an error string keep rc 0 (`tests/test_layout.py`).
- No `ensure_buildings` fallback (committed buildings are never inputs of a full run).
- The style-photo terms reach the **first** style stage that builds the scene (phases 1/3).

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
  among all matching keywords the room type with the highest priority wins: `wc` > `bathroom` > `storage` >
  `balcony` > `bedroom` > `living` > `kitchen` > `hall` > `other` (a combined living + kitchen label is a living
  room; its documented kitchen pieces stay kitchen pieces). New keywords: `lavabo` → `wc`, `tuvalet` → `wc`,
  `dus` → `bathroom`, `giris` → `hall`, `teras` → `balcony`, `calisma` → `other`. The test pins
  `SALON + MUTFAK 39,05 m²` → living, `EBEVEYN BANYO` → bathroom, `ÇALIŞMA ODASI` → other, and every
  synthetic-01..03 `room_type` (their truth must not change).
- `docs/synthetic.md`: the two projects, their purpose and expected numbers. Commit the generated projects
  (≈ 0.5 MB) and their previews.

## 4. Cameras (area C)

### 4.1 Search (`camsearch.py`, pure numpy, no Blender)

Port of the validated prototype scorer: per candidate camera, rays on a 64 × 36 grid against the room prism
(floor, ceiling, polygon edges as walls), the door/window rectangles of the room's edges and the room's
furniture boxes (`parametric.piece_bbox` + footprint rotation); per pixel a label (furniture id, opening id,
floor, ceiling, wall) and a depth.

Score (all constants in one table `SCORE` in `camsearch.py`):
- `furn = Σ_k w(type_k)·min(c_k, 0.25)/0.25·(0.6 if piece k touches the frame border else 1) / Σ_{pieces of
  the room} w(type)` (0 when the room has no piece);
- `score = 4·furn + min(open, 0.12)/0.12 + min(floor, 0.25)/0.25 + min(d_wall/3 m, 1) − 3·max(0, near − 0.08)
  − 3·max(0, max_single − 0.40) − 2·max(0, wall − 0.55) − 2·max(0, window − 0.20) − 1·max(0, ceiling − 0.15)`;
- `c_k`, `open`, `floor`, `wall`, `window`, `ceiling` are pixel shares on the grid; `near` = share with depth
  < 0.9 m; `max_single` = largest share of one piece or opening; `d_wall` = median depth of wall pixels (of all
  finite pixels when there are none); `window` = window openings only;
- type weights `w`: bed, bed_double, bed_single, sofa, kitchen_counter, kitchen_island 3; bathtub 2.5;
  table_dining, desk, toilet, washbasin, shower, sink_kitchen 2; wardrobe, armchair, stove, tv_unit,
  table_coffee 1.5; chair 0.8; every other type 1.

Candidates: free points (`geom2d.point_is_free` with the existing wall 0.3 m / obstacle 0.2 m clearances) on a
0.5 m grid plus two points per convex polygon corner (0.45 m and 0.6 m in along the bisector); yaw every 30°;
height 1.25 m; pitch 0; `shift_y = −0.10`; lens 24 mm / 36 mm; 1920 × 1080. A room without a free point gets
the M5 fallback (`cameras._Search.fallback`, unchanged) anchored at the room's inner point (`lighting.polylabel`,
always inside the polygon) instead of the centroid, which can lie outside an L-shaped room (review C1): that point,
else the nearest point clear of the tall pieces, else the inner point itself. The warning names the inner point
and says "INSIDE a proxy" only when it is in a tall piece (else its distance to the nearest wall); such a cramped
view is then flagged `blocked unavoidable` by the pick.

Blocked = model `near` > 0.30 or `max_single` > 0.50. Views per room: 3 when the room area ≥ 6 m², 2 when 3–6
m², 1 when < 3 m². Greedy pick by score among unblocked candidates; a later pick must differ from every earlier
one by ≥ 50° yaw or ≥ 1.0 m; a pick below 0.5 × the room's best score is dropped (at least 1 view per room). A
room with no unblocked candidate gets its best blocked one with `warning: "blocked unavoidable"`. Ties: score,
then x, y, yaw. Deterministic. Budget ≤ 60 s per project on one CPU core for synthetic-03 (`search_seconds` in
the scene manifest: the sum over the levels, null for `m5`; every searched plan also carries its level's
seconds). The model's depth is the planar depth (Cycles Z, what the GPU test reads), not the ray length.

### 4.2 Integration

- `plan_cameras(building, level_id, policy="m5")` keeps the default `m5` (pure function, as committed);
  `policy="search"` runs camsearch. The build's `--camera-policy` / `cli.build(..., camera_policy="m5")` also
  default to `m5` (area L); the orchestrator passes `search`. Existing tests keep the m5 behaviour unchanged.
- Plans carry `shift_x`, `shift_y`, `policy`, `score`, `placement` (text with the score parts), `anchor` null,
  `warning`, `visible_openings` / `visible_furniture` (frustum with shift).
- `create_cameras` sets `cam.shift_x/shift_y`.
- `expected.project_points` and `unproject_pixels` with shift (§1.3). CPU tests: `unproject(project(p)) = p` on
  a camera with `shift_y = −0.10`; json cross-check on a shifted synthetic view reports no misplaced opening;
  the projection matches Blender's `world_to_camera_view` on a shifted camera (skip without Blender).
- `tests/gpu/test_render.py`: `test_every_room_has_three_views` becomes: policy `m5` → 3 views per room;
  policy `search` → 1–3 views per room by the area rule, every room ≥ 1; new: no blocked view (index pass: one
  element > 0.55 of the frame, or depth: > 0.35 of pixels nearer than 0.9 m) except views with the warning
  "blocked unavoidable" (listed); the share of views with < 10 % object pixels is printed.

## 5. Cycles realism (area L)

All prototyped on CPU (Blender 5.2.2) with before/after evidence; render time change ≤ 2 %. Blender's Python
has numpy but no cv2, scipy, PIL or shapely: everything below that runs inside Blender uses numpy (and OIIO for
image files) only. Every new design-detail object or light gets a scene-manifest `assumed` entry with `parent`
(documented element id or room id), `kind` and `reason`; none of them appears in `building_final.json`.

| # | Change | Where | Contract / test |
|---|---|---|---|
| 1 | Unverified-piece stripes emit only for camera rays: factor = stripe × Light Path `Is Camera Ray` | `materials.py` | a small room with an unverified piece: wall pixels neutral, stripes still visible |
| 2 | Kitchen counter fronts 1 mm proud of the carcass, handles on the fronts | `parametric.py` | no front face coplanar with a carcass face; bbox unchanged |
| 3 | Wall faces split at every room corner along the wall (`bmesh.ops.bisect_plane`) before the per-face material probe | `shell.py` | CPU test on a hand-made building (a wall shared by a bathroom and a bedroom: tiles on the bathroom span only) and on synthetic-03 L1 wall `w_L1_006` |
| 4 | Wet walls: procedural glazed tiles (Brick Texture on metre UVs, 60 × 30 cm, 3 mm grout, roughness 0.08 tile / 0.7 grout, bump from the grout mask) for `tiles_*` slugs without an image asset | `materials.py`, `vocabulary.py`, `profile.py` | material has the node group; flat albedo mode still works |
| 5 | Area light of a windowless room at the pole of inaccessibility (pure-Python/numpy polylabel, 1 cm precision), square size ≤ 2 × its distance to the polygon boundary | `lighting.py` | CPU test on a hand-made L-shaped windowless hall: light fully inside the room |
| 6 | Dim rooms (glass area / floor area < 0.08) get the assumed ceiling area light at half power (6 W/m²), invisible to the camera, recorded `assumed` with the reason | `lighting.py` | manifest entry; GPU: the dim rooms below +6 EV (synthetic-03 has three by the 0.08 rule: `r_L-1_kiler` 0.051, `r_L-1_yatak_odasi` 0.036, `r_L-1_kiler_2` 0.049; synthetic-01 two: `r_L1_hol`, `r_L1_banyo`) |
| 7 | Window pull: the final render also enables the Diffuse Color pass (the EXR gains a `Diffuse Color` layer, Blender 5.2.2's name; readers also accept `DiffCol`; existing passes unchanged; `RENDER_CODE_VERSION` → `m6.1`). After the render, the Render Result is saved again at EV − k to a temp PNG and read back with OIIO; pane mask = window index ∧ Diffuse Color luminance < 0.05, feathered over 3 px with numpy; k = the smallest of 1..4 with pane clip ≤ 1 % and pane median > wall median (wall = `views.regions` walls); if none qualifies, the k with the lowest clip that keeps pane median > wall median; with no wall pixels the clip rule alone; with no pane pixels `window_pull: null`. Blended into the PNG and the preview; recorded as `window_pull: {ev (= −k), k, clip_before, clip_after, pane_px, ...}` | `render.py` | pixels outside the mask unchanged (max diff 0); EXR passes other than `Diffuse Color` unchanged |
| 8 | Soft bedding (superellipsoid mattress, draped duvet, turn-down band, pillows leaning 14°) inside the bed's own box; veneer slugs (`wood_veneer_oak`, `wood_veneer_walnut`, Poly Haven `oak_veneer_01`, `walnut_veneer`) for furniture wood instead of the floor planks; fabric textures in flat albedo mode (Poly Haven `rough_linen`); `metallic = 1` for steel; one Bevel modifier (weight-limited, 0.05 m, 3 segments, per-part weights, ≤ 1/3 of the smallest side); `parametric.decor_rest_height` follows the bedding top for bed hosts (build time, so the M5 building of the A/B gets it too) | `parametric.py`, `furniture.py`, `materials.py`, `vocabulary.py`, `wenart/assets` | bbox equals the footprint box (1.6 × 2.0 × 1.0 m bed checked); `obstacle_rect`/`piece_bbox` unchanged for every type (the `m5` cameras depend on it) |
| 9 | Doors: veneer with vertical grain, lever handles on both faces at 1.02 m (steel, the door's pass index); painted skirting 8 cm × 12 mm along dry-room walls, interrupted at doors, pass index 0, status `assumed` | `shell.py`, `materials.py` | handles inside the door's bbox + handle depth; skirting absent in wet rooms |
| 10 | `--alt-look "AgX - Punchy"`: also save `<cam>_alt_preview.jpg` with that look and the **same** window pull (alt look saved at EV and at EV − k with the main PNG's k and mask, blended with the same mask) | `render.py`, `cli.py` | outside the mask the alt preview equals a plain alt-look save; main PNG unchanged |
| 11 | Control and A/B flags for §6: `--max-bounces N`, `--no-denoise`, `--ev-offset X` (added to the auto or `--look-from` EV), `--preview-quality Q` (fixed JPEG quality, no size step-down; the AB renders use 85 = the committed M5 previews); all part of `render_key`. `--max-bounces N` sets N diffuse, glossy and volume bounces and keeps transmission and the total at ≥ 2, so camera rays still pass both faces of the window glass (a plain Cycles `max_bounces = 0` turned every pane black, review L1); the applied limits are in the render key and the manifest (`bounces`) | `render.py`, `cli.py` | key changes with each flag; `--max-bounces 0` keeps the sky in the panes (pane median > 0) with darker walls |
| 12 | `render` stops before a new camera once `WENART_DEADLINE` is past, writes the manifest with `incomplete: true`, exit 3; `cli.main` passes 3 through. A camera it did not render whose carried-over entry comes from another scene build loses that entry (review L2) | `render.py`, `cli.py` | CPU test with a past deadline |
| 12a | Stale entries (review L2): entries of cameras no longer in the scene (e.g. M5 cameras the search dropped) and the older-build entries of row 12 leave `renders` and are listed under `dropped_stale: [{camera, reason, scene_sha256, render_key, files}]`; their files are not deleted; an item is carried over while files of the camera remain and it has no entry. Readers take views from `renders` only; `views.load_views` also skips (`StaleRender`) an entry of a camera in `not_rendered` whose `scene_sha256` differs from the manifest's (manifests written before the fix) | `render.py`, `views.py` | CPU tests (Blender: dropped camera and deadline cut; views: old manifests, readers) |
| 13 | `build --camera-policy search|m5` (default `m5`, part of the fingerprint; `cli.build(..., camera_policy="m5")`); building hashed with `canonical_sha256` | `build.py`, `cli.py` | fingerprint unchanged when only `created_utc` changes |

Rules: furniture type, footprint, rotation and room never change; bedding, handles, fronts and skirting are
design details of documented elements; the dim-room light is lighting mood; window pull and the alt look change
display pixels only. Texture downloads happen on the pod (`/workspace/assets`); ambientCG is not used for new
slugs (sizes mostly unknown; the session cannot fetch it).

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
`$ref`). Post-validation removes repeated cues. Call key `realism|<pair_id>|<order>` with `pair_id =
<set>:<cam>` (unique per pairs file), stored in the M5 `AnswerStore` format in
`out/check/realism/answers_<model slug>.json`, resumable by `input_sha256`. Images are sent at the M5 size
(1600 px long side).

Outcomes per model, pair, aspect: **W** = B picked in both orders, **L** = A in both, **T** = the pick follows
the position, **NC** = a call failed (never a tie or loss). Graded score per model: Σ over both orders of
±{1,2,3} (slight/clear/large, + toward B), range −6..+6. Consensus: W only when both models W, L only when both
L, NC when any NC, else T. Per model also: order consistency (W+L)/(W+L+T) and the position-bias index (share
of `image_1` picks, ≈ 0.5 expected).

Statistics: exact two-sided sign test on consensus W vs L (ties out); per room the outcome of its non-NC
views (W if W > L, L if L > W, else T) and a sign test over rooms; a room-cluster bootstrap 95 % interval of the
net win (W−L)/N (2000 resamples, seed 0).

`realism-combine` (per project) writes outcomes, per-model stats and, for the control project, the controls
table — no decision. `realism-summary` pools all AB projects per set, reads the controls from the
`--ab-controls` project and writes `decision` and `single_model` per set and aspect into
`realism_summary.json`:
- `not_measurable` when the controls of §6.2 fail for both models;
- `better` when consensus `photo` W > L with sign-test p < 0.05 **and** ≥ 30 decisive pairs from ≥ 10 rooms
  **and** the room-level net-win interval is above 0 **and** no aspect has significantly (p < 0.05) more L
  than W;
- `worse` when the same holds with L and W swapped;
- otherwise `no_detectable_difference` (never "equal").

### 6.2 Controls (the A/B is trusted only after they pass)

Every control render uses `--look-from out/ab/renders/render_manifest.json` (same EV and white point as the
normal render; nuisance adds `--ev-offset 0.3`) and `--preview-quality 85`.

| Set | Pairs (A = degraded, B = normal unless noted) | Expected | Target per model |
|---|---|---|---|
| `ctl_flat` | `build --no-textures` render vs normal, 8 views | B wins `materials` | order-consistent correct ≥ 70 % (consensus ≥ 60 %), wrong ≤ 5 % |
| `ctl_proxy` | `build --proxies` vs normal, 8 views | B wins `furniture` | same |
| `ctl_direct` | `render --max-bounces 0` (no indirect diffuse/glossy/volume light; window glass still transmits, §5 row 11) vs normal, 8 views | B wins `lighting` | same |
| `ctl_lowspp` | `render --samples 4 --no-denoise` vs normal, 8 views | B wins `photo` | same |
| `null_identical` | normal vs the byte-identical file, 8 views | T | ≥ 90 % T, every flip listed |
| `null_reencode` | normal vs a JPEG q70 re-encode (PIL), 8 views | T | W ≤ 10 % |
| `nuisance_ev` | normal vs `--ev-offset 0.3`, 8 views | none | report brighter-wins share; > 30 % → flag ΔEV next to every A/B pair with \|ΔEV\| > 0.3 |
| halo (derived) | on the four `ctl_*` sets, share of non-target aspects that follow the target winner | low | reported; > 80 % → note "ask one aspect per call" for M7 |

A model has signal when it meets the target on each of the four `ctl_*` sets; a model without signal is
reported as "no signal from <model>", the consensus then uses the other model alone and the decision is marked
`single_model`. The 8 control views: `realism.control_views(render_manifest, scene_manifest, n=8)` = the 8 views
of the control project's AB renders with the highest furniture pixel share (`index_stats` + the index table),
ties by name. Controls are asked first, then `m5_vs_m6`, then `look_alt`.

### 6.3 Pair sets of M6 and how they are made (orchestrated by R, commands by V and L)

`M5_LOOK_COMMIT = a2adcef58ede7e4f9e92dd6a847e1e4692075131`.
- **AB prepare part 1** (R, phase 1, only for AB projects not in `--projects`): stages 1, 3 and 4 (pipeline,
  style without photos, assets) so `out/style.json` and the new textures exist; needs_review or failed drops the
  project from the A/B with the reason.
- **AB prepare part 2** (R, phase 4): from `git show M5_LOOK_COMMIT:` write `out/ab/m5/`:
  `building_final.json` (also copied to `out/ab/building_m5.json`), `scene_manifest.json`,
  `render_manifest.json` and `<cam>_preview.jpg` for every M5 camera (quality 85, 1920 × 1080).
- **AB render** (R, phase 5): `build --building out/ab/building_m5.json --style out/style.json --camera-policy m5
  --out out/ab/scene --reuse`; `render --scene out/ab/scene/scene.blend --out out/ab/renders --alt-look "AgX -
  Punchy" --preview-quality 85` (other flags as stage 10). Then compare every AB camera's position and target
  with `out/ab/m5/scene_manifest.json` (1 mm) → `out/ab/cameras_check.json` `{kept: [...], dropped: [{cam,
  reason}]}`. For the control project: `control_views(...)`, builds `out/ab/ctl_flat/scene` (`--no-textures`)
  and `out/ab/ctl_proxy/scene` (`--proxies`), both `--camera-policy m5`, and renders of the 8 views into
  `out/ab/<set>/renders` (`ctl_flat`, `ctl_proxy` from their scenes; `ctl_direct`, `ctl_lowspp`, `nuisance_ev`
  from `out/ab/scene` with the flags of §6.2).
- **Sets**: `m5_vs_m6` (A = `ab/m5/<cam>_preview.jpg`, B = `ab/renders/<cam>_preview.jpg`, kept cameras);
  `look_alt` (A = `ab/renders/<cam>_preview.jpg`, B = `ab/renders/<cam>_alt_preview.jpg`; decides whether the
  default look should become `AgX - Punchy` in M7; asked last, skipped at the deadline, never counted in the
  exit code or the 95 % rule); `ctl_*`, `null_*`, `nuisance_ev` (control project only).
- `python -m wenart.vision_check realism-pairs --project-out out [--controls]` reads only files under `out`
  (no git) and writes `out/ab/pairs.json`: `{pairs: [{pair_id, set, cam, room_id, a, b, expected:
  "b"|"a"|"tie"|null, target_aspect, a_sha256, b_sha256, a_bytes, b_bytes, delta_ev}], dropped, skipped,
  control_views, sets}` (paths relative to `out`; `dropped` copied from `cameras_check.json`; `delta_ev` = log2
  of the mean linear Rec. 709 luminance ratio B/A measured from the two JPEGs); the `null_reencode` A files
  (`ab/null_reencode/<cam>_reencode.jpg`) are written by this command (PIL q70).
- `realism --project-out out --model-key K --server URL --workers <seqs> [--sets s,... | --skip-sets s,...]`
  asks the pairs (deadline-aware, sets in the order of §6.2, file `incomplete: true` when cut; the orchestrator
  passes every set but `look_alt` in one call and `--sets look_alt` in a later one when the time rule allows); `realism-combine --project-out out` →
  `out/check/realism/realism_ab.json`, `realism_report.md`, `contact_realism_<set>_<n>.jpg` (rows A | B |
  outcomes, ≤ 300 KB each); `realism-summary --project-outs ... --controls-project <p> --out
  $RESULTS/realism/` → `realism_summary.json/.md` with the decision table:

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|

  plus the controls table, position-bias index per model, ΔEV flags and the top decisive cues.

Calls per model: 174 `m5_vs_m6` + 64 `ctl_*` + 48 null/nuisance = 286, + 174 `look_alt` = 460. At 2.2 s wall
per call (2 in flight) ≈ 10.5 min per model without `look_alt`, ≈ 17 min with it.

## 7. Intake, runner, gate validation, report (area IE)

### 7.1 Private projects (`wenart/intake.py`, `docs/intake.md`)

- Alias: `^real-[0-9]{2,3}$`, or the reserved `selftest-02` (§1.1 `check_alias`). The alias is public (job log,
  run manifest, gpu-log, commit messages): never a client, address or project name. Refused when
  `projects/<alias>` exists. A missing upload folder → that project ends `needs_review: not uploaded`, others go
  on.
- `python -m wenart.intake stage <alias> --out <out_dir>/input/<alias> [--root /workspace/projects-private]`:
  walks the upload; skips junk (`.DS_Store`, `__MACOSX/`, `._*`, `Thumbs.db`, `desktop.ini`); refuses symlinks;
  caps 500 MB per file and 2 GB per project; keeps only `.pdf .dxf .dwg .jpg .jpeg .png .tif .tiff .yaml .yml
  .txt .md` (others listed as skipped); **NFC-normalises** names (macOS writes NFD; Turkish names); stages
  documents from subfolders at the top level as `<subfolder>__<name>` (the pipeline reads the top level only;
  `style_photos/` keeps its folder); a staged-name collision → `needs_review` with reason "document name
  collision". `--out` is rebuilt on every run (stage into `<out>.tmp/`, then replace), so a file removed from the
  upload is never read again; the upload itself is never modified or deleted. Writes
  `<out_dir>/intake_manifest.json` (per file: original path, staged name, size, sha256, kept/skipped + reason; a
  DWG without a DXF of the same stem gets the note "DWG is not read; export DXF from the CAD program").
- `PRIVATE_SELFTEST=1`: the job copies `projects/synthetic-02` to `/workspace/projects-private/selftest-02`
  (once) and adds the alias; expected end state `needs_review` (scan-only project); its allow-listed files under
  `results-private/selftest-02/`, nothing under `$RESULTS/*/selftest-02`.
- `docs/intake.md` (for the user, simple English): choose an alias `real-01`, `real-02`, …; create a RunPod
  **S3 API key** (console → Settings → S3 API Keys; never paste it into the chat), install the AWS CLI, `aws
  configure --profile runpod`, upload with `aws s3 cp --recursive ./<folder>
  s3://h9er811d55/projects-private/<alias>/ --profile runpod --region EU-RO-1 --endpoint-url
  https://s3api-eu-ro-1.runpod.io/` (with `AWS_REQUEST_CHECKSUM_CALCULATION=when_required`,
  `AWS_RESPONSE_CHECKSUM_VALIDATION=when_required`, `AWS_RETRY_MODE=standard`, `AWS_MAX_ATTEMPTS=10`), list it,
  tell Claude only the alias; folder layout and optional `brief.yaml` / `style_photos/`; export DXF (and/or
  vector PDF) from CAD instead of DWG; download the full outputs from
  `s3://h9er811d55/outputs-private/<alias>/`; removal only by the user. **What reaches Claude** for a private
  run: the final report (it contains room names and counts), the final previews and contact sheets, the stage
  records, `_run_manifest.json` and `_logs/` (vLLM, setup and download log tails, tail 200, and the
  orchestrator traceback after a crash, which can name a file or a room; §1.1, §2.4). **What stays on the
  volume**: the documents, plan crops, debug overlays, building JSON, check answers, the per-stage logs
  (`<out>/run/logs/`).

### 7.2 Runner and repository guards

- `scripts/gpu_run.py`: `collect` also walks `results-private/` into `runs/<job>/results-private/` (same caps,
  one total); after a successful collection the runner stops the pod at once (REST stop, then the usual
  terminate) and logs the result as `<tag>, stopped by runner after collect (watchdog and job-end stop armed)`;
  `self-stop ok` only when the pod reached EXITED before the runner sent a stop. A collection is successful
  (review F2) only with job.log, the job-folder listing (5 tries, 10 s apart, like each tree's root listing:
  without it the runner cannot know whether `results-private/` exists), every tree listed and no failed file
  download (a file left out for its size is not a failure; the size cap stays a warning); otherwise the next
  poll collects again (up to 3 times) and the pod is not stopped from the runner. `GPU_PRIORITY = ["RTX PRO
  4500", "RTX 4090", "RTX PRO 4000", "RTX A5000", "RTX A6000", "A40"]` (no L4).
- `.gitignore`: `/projects-private/`, `/results-private/`, `/outputs-private/`.
- `tests/test_private_guard.py`: every `results/<area>/<p>/` folder (areas `renders furniture polish gate check
  final run realism`) has a committed `projects/<p>/`; `git check-ignore` holds for the three private roots; no
  committed file mentions a private alias other than `selftest-02`.

### 7.3 Gate validation (`wenart/gate/validate.py`)

`python -m wenart.gate validate --project-out out` reads `gate/gate_calibration.json` `rates` (computed with the
thresholds in use) and `wenart/gate/validation.yaml` (`benign_accept_min: 0.95`, `negative_reject_min: 0.90`),
writes `gate/gate_validation.json` `{benign_accept, negative_reject, n_benign, n_negative, pass_benign,
pass_negative, decision, reasons}`: `ok` both pass; `flagged` only the benign limit fails (polish runs, the
report flags it); `polish_disabled` the negative limit fails; `not_validated` missing or incomplete calibration.
`polish_disabled` and `not_validated` → no polish for the project, Cycles finals, listed in the report and in
progress.md.

### 7.4 Final report (`wenart/report`)

- `needs_review` projects: `final_report.md` is the needs-review report (status, every reason, page table from
  `building.json`/`report.md`, debug images converted to JPEG ≤ 300 KB under `final/debug/`; for a private
  project the debug images are named, not copied), `final_manifest.json` `status: needs_review`, exit 0.
- Gate validation section and its effect; camera policy and score per view; views per room as rendered (1–3);
  a stage table from `out/run/*.json` (status, seconds, note); the window-pull EV per view.
- The views are the render manifest's cameras: a camera only in the polish manifest (an earlier run's) is a
  warning, never a view. With the gate decision `polish_disabled` or `not_validated` a
  `polish/polish_manifest.json` on the volume is an earlier run's and is not used (`stages.polish: not_run`,
  no polish models or seconds), so the view count always equals the render manifest's.
- The stage table is this run's: the run is the `run_id` of the newest record (`run_id` in the manifest).
  Records of earlier runs (stages this run did not reach) are listed apart as `earlier run <run_id>`
  (`earlier_run_stages`) and never decide the status, so a needs-review report never lists an older run's
  build or render as part of this run.
- No render manifest and not `needs_review`: `status: not_rendered`, `status_note: "no renders in this run"`,
  the report names this run's `incomplete`/`failed` stages (`stopped_stages`, e.g. `build incomplete
  (deadline: build not started)`); exit 1, the only exit 1 besides a crash. `final_manifest.json` is written
  after `final_report.md`, so a manifest newer than the report call means the report finished; the
  orchestrator records the report of a project that was already `incomplete` or `failed` as `warning` (note
  `no renders in this run`), so a deadline cut stays `incomplete`.
- For a private project the plan crops are named, not copied into `final/`. The intake section shows counts,
  reasons and the fixed note texts by kind (`intake.notes_by_kind`: a misnamed or nested brief, a DWG, a name
  collision; any other note only as a count), never a file name; a brief that was not read (no `brief.yaml` at
  the top level next to a `Brief.yaml`, `brief.yml` or a nested one) and DWG notes are advisory flags.
- The brief's own warnings (`wenart.brief.load_brief`: no `brief.yaml`, a value of the wrong type) are report
  warnings; for a private project the user's value is left out (`got str`, not the value).
- Uses `wenart.views.resolve_repo_path` for every repo-relative path.

## 8. Pod plan and budget

### 8.1 Time rule (measured on the RTX PRO 4500 in M5, critic- and review-checked)

Per project ≈ 4 min + 0.63 min per view (+ 10 s per AI-furnished room) with polish, controls and gate
calibration; per pod fixed ≈ 19 min with 3 server starts, ≈ 21.3 with 4 (boot 1.5, setup 4.4, starts, tests
0.7, copy 1.1). `--max-minutes 115` → `WENART_DEADLINE` = entry + 100 min. Views by the §4.1 rule (computed on
the committed buildings): synthetic-01 29, synthetic-03 50, synthetic-04 ≈ 14, synthetic-05 ≈ 25.

`python -m wenart.run plan` for all five projects (2 Oct, after the integration; views by
`camsearch.room_view_count`):

| Project | Status | Rooms | Empty rooms | Views | Photos | Minutes | Server starts | Pod |
|---|---|---|---|---|---|---|---|---|
| synthetic-01 | ok | 10 | 7 | 29 | – | 23.44 | 3 | 1 |
| synthetic-02 | needs_review | – | – | – | – | – | – | – |
| synthetic-03 | ok | 19 | 11 | 50 | – | 37.33 | 3 | 1 |
| synthetic-04 | ok | 5 | 2 | 14 | – | 13.15 | 3 | 2 |
| synthetic-05 | ok | 9 | 3 | 25 | 1 (to ask) | 20.25 | 4 | 2 |

Split: pod 1 = synthetic-01 + synthetic-03 (3 starts, 60.8 project min of 73.0, job ≈ 79.8 min); pod 2 =
synthetic-04 + synthetic-05 (4 starts, 33.4 of 70.7, job ≈ 54.7 min). The plan counts project work only: pod A
below adds the CPU-measured render cost of the window pull (≈ +0.8 s per 1080p view with panes, about +10 % on
8 s per view) as margin; pod B adds synthetic-02, the self-test and the A/B renders and controls, and the time
rule over-counts synthetic-05 (polish off: no gate calibration or polish, ≈ 15 min instead of 20.25). The
searched cameras can be fewer than the rule's views (a pick below half the room's best score is dropped:
synthetic-03 searches to 49).

| Pod | Content | Estimate | Cost (≤ $0.74/h) |
|---|---|---|---|
| A | full run synthetic-01 + synthetic-03 | ≈ 83–88 min job, ≈ 92 pod-min | ≈ $1.15 |
| B | full run synthetic-04 + synthetic-05 (photos → 4 server starts) + synthetic-02 (needs_review) + `PRIVATE_SELFTEST=1` + AB `synthetic-01 synthetic-03` with `AB_PHASE=render` and controls on synthetic-01 | ≈ 21 + 13 + 15 + 13 (AB renders) + 6 (controls) ≈ 69 min job | ≈ $0.95 |
| C | AB `synthetic-01 synthetic-03`, `AB_PHASE=judge`, `AB_CONTROL_PROJECT=synthetic-01` (the same control project as pod B, §2.1; 2 server starts, 460 calls per model) | ≈ 6 + 7 + 34 + 3 ≈ 50 min job | ≈ $0.65 |

`python scripts/gpu_run.py run --job scripts/jobs/full.sh --gpu 'RTX PRO 4500' --disk 130 --max-minutes 115
--grace 600 --env RUN_PROJECTS=... [--env ...] --purpose "M6 ..."` (`RTX 4090` when the 4500 has no stock;
the runner stops the pod after collecting). Pods run one at a time, A first. Before pod A: the CPU suite, the
smoke e2e (§2.5) and `python -m wenart.run plan` for all five projects green in the session. A pod that the
deadline cuts exits 1; the same command resumes from the volume (fingerprints, render keys, complete gate
calibrations, attempts, answers). Cap for M6: $4.00 in total; ask the user before going over it or the $10/day limit. Every pod is
logged in `docs/gpu-log.md` (private projects only by alias and counts); no pod is left running.

## 9. Tests

CPU (`pytest -m "not gpu"`):
- run: ProjectRef paths (public, private, alias rules, traversal), canonical hash (volatile keys at any depth,
  key order), fingerprints and reuse (outputs missing → re-run, `--force`), stage table commands (golden lists
  per stage), statuses and project states (warning, skipped reasons, incomplete from output flags, build exit 2
  → failed), scheduler with an injected runner and fake clock (phase order; server sessions only when needed:
  2/3/4 starts; needs_review stops a project and no server starts for it; deadline → incomplete; failed layout
  never reused; photo terms reused on resume without a server; gate before polish), server context manager with
  a fake process (ready, early exit, timeout, deadline, TERM/KILL, pid file), copy mapping and filters (public
  layout, private allow-list: no file outside it), run manifests (private details only in the private one),
  traceback redirect and count-only copy output for private runs, exit code rules, `plan` golden output for
  synthetic-01..05 (status, views 29/–/50/14/25, minutes, server starts, split); the code lists cover each
  fingerprinted stage's import closure (`ast`, imports inside functions included); judge without `--ab-controls`
  (control project from `ab/control_views.json`, pairs reused, two candidates refused); calibration reuse; failed
  model downloads → warning, retried; a cut check run seen through the preference; a report without renders
  keeps a cut project `incomplete`; A/B records outside the project state; the upload fingerprinted by its
  listing; outputs of earlier jobs moved aside; `full.sh` static checks
  (shebang, `set -Eeuo pipefail`, ERR trap, logs under `/workspace/logs`, exports, flock, EXIT trap kills the
  vLLM pid); `layout.py` transport error → exit 3, no file; smoke e2e (§2.5, `slow`).
- synthetic: five projects generated, counts, truth equality (synthetic-04/05 in `test_matches_truth` and
  `test_evidence_matches_truth`), furniture-plan warning, style photo copied, room types pinned for all five.
- cameras: score parts on hand-made rooms (the §4.1 formula), candidate grid, blocked rule, diversity and
  view-count rules, determinism, `m5` policy identical to the M5 scene-manifest cameras of synthetic-01 and -03
  (positions and targets within 1 mm, from `git show a2adcef:results/renders/<p>/scene_manifest.json`),
  projection and unprojection with shift (vs Blender when present), search time.
- look (skip without Blender): one test per row of §5, and the `assumed` entries (one per bedding set,
  counter-front set, door-handle pair, skirting run and dim-room light, each with parent, kind, reason).
- realism (`tests/test_realism_ab.py`): prompt/schema strictness, post-validation, outcomes W/L/T/NC per order pair, graded score, consensus,
  sign test values, bootstrap determinism, controls evaluation and `single_model`, decision rules (in
  realism-summary only), unique pair ids, pairs file, `control_views`, fake client end to end, resumable answers,
  summary table.
- intake/guard/runner/gate/report: alias rules, junk skip, NFC names, subfolder staging and collisions, caps,
  rebuild on re-stage, manifest; guard test; collect of `results-private` with a fake server; stop-after-collect
  and its gpu-log wording; gate validate decisions; needs-review report; private report without plan crops;
  `resolve_repo_path`.

GPU (`pytest -m gpu` on the pod): `test_full_run.py` (every RUN_TEST project `ok` with every stage `ok`,
`reused`, `warning` or `skipped` with an allowed reason, warnings listed; a final report whose view count
equals the render manifest; every NEEDS_REVIEW project `needs_review` with ≥ 1 reason and no scene built in
this run; with SELFTEST_TEST_ALIAS: its files only under `results-private/<alias>/`, none under `$RESULTS`;
every `polish_disabled` or `not_validated` project has Cycles finals only), `test_render.py` (§4.2),
`test_look_m6.py` (rooms with unverified pieces: |tint| ≤ 40; kitchen counter index pixels mean display
luminance ≥ 0.15; `window_pull.clip_after ≤ 0.05` in ≥ 90 % of the views with panes; every dim-room view
below +6 EV (three dim synthetic-03 rooms by the 0.08 rule, §5 row 6); the `assumed` entries as in the CPU test), `tests/gpu/test_realism.py` (realism_summary.json valid;
≥ 95 % of calls answered per model over the sets that were started, `look_alt` cut by the deadline reported,
not counted; `null_identical` ≥ 90 % T; controls table present), `test_polish.py`
(`test_gate_calibration_separates_benign_from_negative` becomes `test_gate_validation_recorded` over
GATE_TEST_PROJECTS: `gate_validation.json` present, its rates equal a recomputation from
`gate_calibration.json` with the current thresholds (with the thresholds the calibration recorded when they
differ; the decision is then `not_validated`), its decision follows `validation.yaml`; `flagged`,
`polish_disabled` and `not_validated` are reported outcomes, not failures), `test_check.py`, `test_furnish.py`,
`test_polish_backend.py` as in M5.

## 10. Done criteria

CPU suite and the smoke e2e green here; `wenart.run plan` for all five projects; pods A, B and C exit 0 (a cut
pod resumed with the same command counts); synthetic-01, -03, -04, -05 `ok` end to end from their project
folders; synthetic-02 and `selftest-02` `needs_review` with their reports; GPU tests green; per-project gate
validation reported; the realism A/B decision reported with its controls (whatever it says); results, previews
and reports of the public projects committed under `results/`; `docs/plan.md`, `docs/progress.md`,
`docs/gpu-log.md`, `docs/synthetic.md`, `docs/intake.md`, `CLAUDE.md` (GPU default) updated; no pod running.
Items needing the user's OK or action are listed in progress.md: the M5 gate limits and advisory check, any
`flagged`/`polish_disabled` project, uploading real projects (S3 key, DXF export, alias).

## 11. Risks

- A second Qwen start in the same pod was never measured (first CUDA-graph capture 138 s); pod B's 4 starts may
  take a few minutes more or less than estimated.
- Pod A has ≈ 12–17 min of margin; the deadline rule turns an overrun into `incomplete`, resumed by a second pod.
- The VLM judges may not see the controls (then the A/B is `not_measurable` and says so).
- vLLM greedy outputs are not guaranteed identical across batches; the identical-pair control allows 10 % flips.
- New Poly Haven textures are first downloaded on the pod (≈ seconds each); a failed download falls back to the
  flat colour and is listed by `assets fetch`.
- The window pull changes the PNG that polish and gate read; the gate compares Cycles PNG and polished PNG, both
  with the same pull, and is re-validated per project before its polish.
- The S3 upload path is documented from the RunPod docs and a live 401 probe; it is tested only when the user
  creates a key. The private plumbing on the pod is tested with `selftest-02`.

## 12. Sources (checked 2 Oct 2026)

- Repo: `scripts/jobs/{polish,furnish,render}.sh`, `scripts/pod_entry.sh:29-34,149` (deadline, `git clean
  -fdxq`), `scripts/gpu_run.py:61,389-465,602,639`, `wenart/blender/{cameras,render,materials,parametric,shell,
  lighting,build,cli}.py`, `wenart/vision_check/{expected,preference,calls}.py`, `wenart/building.py:47-61`,
  `wenart/ingest/classify.py:89-95` (top level only), `wenart/furniture/layout.py`, M5 pod logs
  `runs/20261002-*`, `results/check/*/check_manifest.json` (advisory), `results/gate/*/gate_calibration.json`
  (`rates`), `tests/gpu/{test_check,test_polish,test_render}.py`.
- RunPod: https://docs.runpod.io/storage/s3-api (endpoint `https://s3api-eu-ro-1.runpod.io/`, bucket = volume
  id, S3 API key from the console only, supported operations, multipart), /storage/network-volumes,
  /pods/configuration/expose-ports (100 s proxy timeout), /get-started/credentials; live probe of the S3
  endpoint (HTTP 401 without credentials); botocore CHANGELOG 1.36.0 (default CRC32 checksums).
- FastChat `fastchat/llm_judge/show_result.py` (swap rule: inconsistent → tie); Wang et al. 2023 "Large
  Language Models are not Fair Evaluators" (arXiv 2305.17926, position bias, balanced position calibration).
- Poly Haven API `https://api.polyhaven.com/files/<id>` for `oak_veneer_01`, `walnut_veneer`, `rough_linen`
  (CC0, https://polyhaven.com/license); Blender 5.2.2: look list (`AgX - Punchy`), `bmesh.ops.bisect_plane`,
  Light Path node outputs, `Camera.shift_x/shift_y` vs `bpy_extras.object_utils.world_to_camera_view`
  (0.011 px), no cv2/scipy/PIL/shapely in Blender's Python.
- GitHub API: repository `cihantanaydin-svg/WenArt_RUN` is public.
