# Bringing a real project to WenArt (private projects)

This page is for you, the project owner. It says how to send a real, possibly confidential project
to the GPU machine (the RunPod network volume) so that WenArt can render it, and what Claude can and
cannot see. The spec behind it is `docs/milestone6.md` §7.1.

## The short version

1. Pick a neutral name for the project: `real-01`, then `real-02`, and so on.
2. Create a RunPod **S3 API key** once (step 2 below). Never paste it into the chat.
3. Upload the project folder from your computer to the volume with the AWS command-line tool.
4. Tell Claude only: "real-01 is uploaded". Nothing else.
5. Later, download the full results from the volume with the same tool.

Your files go from your computer straight to RunPod (data centre EU-RO-1). They never go through
GitHub, never through the Claude chat and never into the public repository.

## Why this way

- The repository `cihantanaydin-svg/WenArt_RUN` is **public**. Everything committed there can be read
  by anyone. A real project can never be committed, not even its results.
- The GPU machine deletes every unknown file in its copy of the repository at each start, so private
  files must live on the volume, outside the repository: `/workspace/projects-private/<alias>/`.

## 1. Choose an alias

- Use `real-01` for the first project, `real-02` for the second, and so on (`real-` and 2 or 3
  digits; nothing else is accepted).
- The alias is **public**: it appears in the job log, the run manifest, `docs/gpu-log.md` and commit
  messages. So it must never contain a client name, an address or a project name.
- Use each alias for one project only. Keep your own list of which alias is which project; do not
  share that list in the chat.

## 2. Create an S3 API key (once)

1. Open the RunPod console, **Credentials** page: https://console.runpod.io/user/credentials
   (the tab is called **S3 API Keys**).
2. Click **Create an S3 API key**, name it `wenart-upload`, click **Create**.
3. RunPod shows two values once:
   - the **access key**, which is your RunPod user id and starts with `user_`
     (it is also in the key's description: `Shared Secret for user_... <number>`);
   - the **secret**, which starts with `rps_`.

   Save both in your password manager. **Never paste them into the chat, an email or a file in the
   repository.** This key is separate from the RunPod API key. The RunPod documentation describes no
   way to limit what it can do, so treat it as full read and write access to your volumes, like a
   password.

## 3. Install the AWS command-line tool (once)

On a Mac: download and run the AWS CLI v2 installer from
https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html (or `brew install awscli`
if you use Homebrew). Then, in Terminal:

```
aws configure --profile runpod
```

Answer the four questions:

| Question | Answer |
|---|---|
| AWS Access Key ID | your `user_...` value |
| AWS Secret Access Key | your `rps_...` secret |
| Default region name | leave empty (press Enter) |
| Default output format | leave empty (press Enter) |

## 4. Prepare the project folder

Put everything of one project in one folder on your computer. Recommended layout:

```
my-folder/
  zemin_kat.dxf            plans: DXF (best) or vector PDF exported from the CAD program
  1_kat.pdf
  brief.yaml               optional: style, polish, decor, style_photos, ... (keys: wenart/defaults.yaml, brief:)
  style_photos/            optional: photos of rooms whose look you like (jpg, png)
    salon_referans.jpg
```

Rules:

- **DWG is read with LibreDWG 0.14 (beta); if it fails, export DXF** (or a vector PDF) from the CAD
  program. A DWG next to a DXF of the same name is skipped (the DXF is used); a DWG alone is kept with
  that note and converted on the pod. A conversion that fails or gives an empty drawing stops the
  project with "needs review" and says so; nothing of a DWG is guessed. Only the model space is read
  (no layouts or paper space).
- Plans in subfolders are fine: `plans/zemin.dxf` is used as `plans__zemin.dxf`. Two files that end
  up with the same name (also when they differ only in upper/lower case) stop the project with
  "document name collision"; rename one of them.
- Top-level folders named `debug/`, `outputs/` or `truth/` are not read (WenArt uses these names for
  its own files).
- `brief.yaml` is read only at the top level and only with exactly this name. A brief with another
  name (`Brief.yaml`, `brief.yml`) or in a subfolder is not read; the final report says so, and then
  every brief value is the default.
- `style_photos/` keeps its photos; other files in it are skipped.
- Files that are used: `.pdf .dxf .dwg .jpg .jpeg .png .tif .tiff .yaml .yml .txt .md`. Everything
  else (`.docx`, `.xlsx`, `.zip`, `.rvt`, ...) is skipped and listed. macOS and Windows helper files
  (`.DS_Store`, `__MACOSX/`, `._*`, `Thumbs.db`, `desktop.ini`) are skipped. Symbolic links are refused.
- Turkish and other accented file names are fine (macOS writes them in a different Unicode form; the
  pod converts them).
- Size limits: 500 MB per file, 2 GB per project. Over a limit, the project stops with "needs review".
- **Use neutral file names** (`zemin_kat.dxf`, `plan_1.pdf`) if the names themselves are confidential:
  file names and room names appear in the final report that Claude reads (see "What reaches Claude").

## 5. Upload

In Terminal, in the folder that contains your project folder (replace `my-folder` and the alias):

```
export AWS_REQUEST_CHECKSUM_CALCULATION=when_required AWS_RESPONSE_CHECKSUM_VALIDATION=when_required
export AWS_RETRY_MODE=standard AWS_MAX_ATTEMPTS=10
ALIAS=real-01
E="--profile runpod --region EU-RO-1 --endpoint-url https://s3api-eu-ro-1.runpod.io/"
aws s3 cp --recursive $E ./my-folder s3://h9er811d55/projects-private/$ALIAS/
aws s3 ls --recursive $E s3://h9er811d55/projects-private/$ALIAS/
```

- `h9er811d55` is the id of the WenArt network volume (`wenart`, EU-RO-1).
- The first `export` line keeps newer AWS CLI versions from sending checksums that S3-compatible
  stores may refuse; the second retries on short "502" errors.
- The `ls` line lists what arrived. Check that every plan is there.
- Then tell Claude only the alias, for example: "real-01 is uploaded, please run it". You may add
  the number of files. Do not paste file names or the listing if they are confidential.

To replace a file, upload it again under the same name. To add a missing file, upload it the same
way. Every run stages the upload again from scratch, so a file you removed is never read again.

## 6. What happens on the pod

- The job copies your upload into a clean working folder (`/workspace/outputs-private/<alias>/input/<alias>`):
  junk skipped, names converted, subfolder plans moved to the top level. It writes
  `intake_manifest.json` with every file, what was kept or skipped and why. **Your upload itself is
  never changed or deleted by the pipeline.**
- Then the same pipeline as for the test projects runs: plans to building JSON, furniture, renders,
  optional AI polish, checks, final report.
- If something is missing (no usable plan, no scale, a DWG that LibreDWG cannot convert, a name
  collision, not uploaded), the project ends with **needs review** and a report that says why. Nothing
  is guessed.
- Files kept with a note (a DWG, a brief that is not read) are counted by note in the final report,
  without their names.
- If the job's time runs out before the renders of your project, the report says "no renders in this
  run" and the project is **incomplete**; it continues from where it stopped when the job runs again.
- In the job log the project appears only as `<alias> <stage> <status> <seconds>s`.

## 7. What reaches Claude, and what stays on the volume

| Reaches Claude (and you, in the session) | Stays on the volume only |
|---|---|
| `final/final_report.md`: status, room ids and names, counts, element ids, the names of your document files (in evidence and, for needs review, the page table), warnings; from the intake only counts and fixed note texts (for example "DWG is read with LibreDWG 0.14 (beta); if it fails, export DXF", or a brief that was not read), never a file name | your documents (`projects-private/<alias>/`) |
| `final/*_final_preview.jpg` and `final/contact_*.jpg`: the final renders | plan crops (`check/*_plan.jpg`) and debug overlays of your plan pages (`debug/`, `final/debug/`) |
| stage records `run/<stage>.json` (status, seconds, a short note; without the input file list) | building JSON, `report.md`, `intake_manifest.json`, layout debug images, check answers |
| `_run_manifest.json` (the state of each private project, its stages, their status and notes) | per-stage logs (`outputs-private/<alias>/run/logs/`), which hold the full tool output |
| `_logs/`: the last 200 lines of the vLLM (vision model server), setup and model-download logs of the job, and, after a crash of the job itself, the orchestrator's error trace, which can name one of your files or a room | |

These files are copied to the session's git-ignored `runs/<job>/results-private/` folder. They are
never committed: a test (`tests/test_private_guard.py`) fails if a private result lands in `results/`.
The renders and the report do enter the model context when Claude reviews them; the raw documents do
not need to. The vision model server is started without request logging, so its log normally holds
no prompt (an error message there can still quote part of one, with room names or labels); the setup
and download logs name only models.

## 8. Download the results

All outputs (renders, building JSON, reports, debug images):

```
ALIAS=real-01
E="--profile runpod --region EU-RO-1 --endpoint-url https://s3api-eu-ro-1.runpod.io/"
aws s3 cp --recursive $E s3://h9er811d55/outputs-private/$ALIAS/ ./$ALIAS-outputs/
```

Only the small result set (final report, previews, contact sheets, stage records):

```
aws s3 cp --recursive $E s3://h9er811d55/results-private/$ALIAS/ ./$ALIAS-results/
```

## 9. Removing a project

Only you decide when your data is deleted; Claude never deletes it. To remove the upload and the
outputs of one project:

```
aws s3 rm --recursive $E s3://h9er811d55/projects-private/$ALIAS/
aws s3 rm --recursive $E s3://h9er811d55/outputs-private/$ALIAS/
aws s3 rm --recursive $E s3://h9er811d55/results-private/$ALIAS/
```

The volume is not a backup: keep your originals. If the RunPod account balance reaches $0, the volume
can be deleted by RunPod after a while.

## Notes

- The S3 path was checked against the RunPod documentation (https://docs.runpod.io/storage/s3-api)
  and a live probe of the endpoint (it answers 401 without a key). It is first really used when you
  create a key. If an upload fails, tell Claude the error message (never the key).
- The pod side of the private path is tested with a synthetic project under the reserved alias
  `selftest-02` (a copy of `tests/fixtures/projects/review-01`: two untitled plan pages; it ends "needs review" on
  purpose). A stale copy on the volume (e.g. the M6 copy of synthetic-02) is moved to
  `/workspace/outputs-archive/selftest-02-upload-<stamp>` and copied again.
