"""Copy the small result files of a full run into the results layout (docs/milestone6.md §2.1, docs/milestone7.md
§9.1, §7.3).

What: ``python -m wenart.run copy --projects ... [--private ...] [--ab ...]
--results $RESULTS [--since STAMP]`` copies, per project, the small files of
``<out_dir>`` into ``$RESULTS/<area>/<p>/`` (the committed layout):

| From ``out/`` | To ``$RESULTS/`` |
|---|---|
| ``*.json``, ``*.md``, ``style_photos/*.json`` | ``furniture/<p>/`` (``style*.json`` also ``renders/<p>/``) |
| ``layout_debug/*.json``, ``layout_debug/*.jpg`` | ``furniture/<p>/layout_debug/`` |
| ``scene/*.json``, ``scene/*.log``, ``renders/`` | ``renders/<p>/`` |
| ``controls/``, ``controls/hide_*/`` | ``renders/<p>/controls/``, ``.../hide_*/`` |
| ``polish/`` (+ ``sweep/``, ``smoke/``), ``gate/``, ``check/`` | ``polish/<p>/``, ``gate/<p>/``, ``check/<p>/`` |
| ``final/``, ``final/debug/`` | ``final/<p>/``, ``final/<p>/debug/`` |
| ``run/*.json``, ``run/logs/*.log`` (tails) | ``run/<p>/``, ``run/<p>/logs/`` |
| ``ab/renders/*``, ``ab/cameras_check.json``, ``ab/pairs.json``, ``check/realism/*`` | ``realism/<p>/`` |
| ``ab/pairs_v2.json`` (realism v2) | ``realism/<p>/`` |
| ``debug/*.png``, ``rectified/*.png`` (each <= 3 MB) | ``furniture/<p>/debug/``, ``furniture/<p>/rectified/`` |
| ``recognition/requests.json``, ``recognition/answers_*.json`` | ``recognition/<p>/`` |
| ``recognition/crops/*.png`` (the first 200 by name) | ``recognition/<p>/crops/`` |
| ``recognition/reading/*.png`` (the reading's plan crops, the first 200 by name; fix round after P5) | ``recognition/<p>/reading/`` |
| ``detect/*.json`` | ``check/<p>/detect/`` |
| ``decor_debug/*.png`` (<= 3 MB), ``decor_debug/*.json`` (Milestone 9) | ``furniture/<p>/decor_debug/`` |
| ``export/<p>.blend``, ``export/<p>.glb``, ``export/export_manifest.json`` (Milestone 9) | ``final/<p>/3d/`` |
| ``sheets/requests.json``, ``sheets/answers_*.json``, ``sheets/crops/*.png`` (Milestone 10) | ``recognition/<p>/sheets/`` |
| ``sheets_debug/*.png`` (<= 3 MB, Milestone 10) | ``furniture/<p>/sheets_debug/`` |
| ``orchestrator/`` (+ ``images/``, ``compare/``), ``agent/previews/`` (Milestone 11) | ``agent/<p>/`` (+ the same sub-folders) |
| ``final/agent/`` (the report's before/after images, Milestone 11) | ``final/<p>/agent/`` |
| ``final/sheets13/`` (the before | after sheets of Milestone 13, JPEG <= 300 KB and JSON) | ``final/<p>/sheets13/`` |
| ``variants/<id>/<the rows above>`` (Milestone 10, an alternative) | ``<area>/<p>/variants/<id>/...`` |

Milestone 10 (docs/milestone10.md §1.6b row 9): an alternative's sub-output ``variants/<id>/`` has a project
output's layout and is copied by the same rules into ``variants/<id>/`` of each area folder (private: the same
allow-list into ``<area>/variants/<id>/``); only the alternatives that ``building_final.json`` lists now
(``wenart.building.alternative_ids``): an older run's variant folder stays on the volume, never copied.

Public filter (as ``polish.sh copy_files``): ``*.json`` and ``*.md`` below
8 MB; ``*_preview.jpg``, ``*_alt_preview.jpg``, ``*_gate.jpg``,
``*_check.jpg``, ``*_plan.jpg``, ``contact_*.jpg`` (and every ``*.jpg`` of a
``debug`` folder) up to 300 KB; the last 400 lines of ``*.log``. Only the
files directly in each folder. ``recognition/<p>/`` is the layout of the
committed seeds (``results/recognition/<p>/answers_<slug>.json``: the next
run's ``recognize --seed-answers``). The prep job writes
``$RESULTS/library/**``, ``$RESULTS/detect/**`` and ``$RESULTS/timing/**``
itself (no per-project rule).

``ATTRIBUTION.md`` (M7 §7.3): after a project's copy, every result folder of
it that holds an image (``renders``, ``polish``, ``gate``, ``check``,
``realism``, ``final``; for a private project its ``final``) gets the
credits of the Objaverse models its ``building_final.json`` uses (one §7.3
line per model, from ``furniture[].asset.attribution``) and the ODC-By 1.0
notice; nothing is written when the project uses none. ``library_attribution``
writes the same for a library folder from ``catalog_objaverse.json``.

Milestone 8 (docs/milestone8.md §2): the credits cover every library source
(ABO, Objaverse of any licence, generated models; furniture and decor items),
each line with its licence flag when it has one, followed by the notices of
the sources present (the ODC-By notice for Objaverse, the ABO credit, the
generated-model note); ``library_attribution`` reads ``catalog_library.json``
(else the M7 ``catalog_objaverse.json``), its ``entries`` and ``decor``.
``library_files`` lists what the prep job copies from its library work folder
into ``$RESULTS/library`` (everything but model files and files over 8 MB).

Milestone 13 (docs/milestone13.md §6, §12 D1/D3, §13.2; track T8): ``ATTRIBUTION.md`` has four sections and a
licence mode.

- What: ``attribution_text(title, credits, *, mode="commercial")`` writes (1) the tools and generators with their
  licences (``TOOLS_AND_GENERATORS``: Blender, LibreDWG, the agent and vision models, TRELLIS.2 with its DINOv3 image
  condition and the nvdiffrast export tool, Z-Image-Turbo, Infinigen, the Poly Haven API credit; plus the model rows
  the final report recorded for the run), (2) the CC0 / CC BY assets with author, source, licence and the changes
  made (models and, from the scene manifest, the texture sets and the HDRI), (3) the PoC-only assets (flags
  ``non_commercial``, ``share_alike``, ``research_only``, ``regional``, ``tool_nc``) with the reason and the licence
  page (in ``commercial`` mode a flagged asset is a warning: it must not be there), (4) the dataset notices of the
  sources present (ABO CC BY 4.0, Objaverse ODC-By 1.0, GSO, the generated-model note, HSSD CC BY-NC 4.0 with its
  citation, Poly Haven CC0). ``project_credits`` adds ``licence_flag``, ``commercial_safe`` and ``licence_url`` to
  every credit (``wenart.furniture.catalog.licence_flag_of`` / ``commercial_safe`` / ``licence_url_of``, track T1)
  and lists the CC0 Poly Haven models as well (``CREDIT_SOURCES``); ``texture_credits`` reads the scene manifest;
  ``library_attribution`` writes the same four sections for the whole catalogue (mode ``relaxed``: a catalogue lists
  everything it holds).
- Why: every render must say whether it is commercial-safe and every flagged asset must be listed with the reason
  (CLAUDE.md library rules); the tools section is the GPL / NC bookkeeping the plan asks for.
- How: the mode comes from ``building_final.json`` ``project.licence_mode`` (the fit writes it; T1), else
  ``catalog.licence_mode()`` (env ``WENART_LICENCE_MODE`` > ``commercial``). A Milestone 13 run (a building with
  ``project.licence_mode``) always gets the file, also with no library model (section 1 and 4 still apply); an older
  run gets it only when it uses library models (as before).

Private projects use an allow-list only, into
``<results-private>/<alias>/<area>/``: ``final/final_report.md``,
``final/final_manifest.json``, ``final/*_final_preview.jpg``,
``final/contact_*.jpg``, ``final/ATTRIBUTION.md`` (credits of public
library models only) and ``run/<stage>.json`` without its ``inputs`` map.
Nothing else (documents, plan crops, debug overlays, building JSON, check
answers, logs) ever leaves ``/workspace/outputs-private/<alias>/``.

Fix round after P3, part 2 (17 Oct 2026, docs/milestone13.md §14.9): the view files of ``final/``
(``<cam>_final_preview.jpg``, ``<cam>_plan.jpg``: ``wenart.report.final.STALE_VIEW_PATTERNS``) follow the final
manifest of this run, public and private alike, for a project and for each of its alternatives.

- What: such a file is copied only when ``final/final_manifest.json`` names it (``views[].preview`` /
  ``views[].plan``) and that manifest is this run's (``final_view_names``); a named file that the results miss, or
  hold an older copy of, is copied even when it is older than the ``--since`` stamp. After every copy, each view file
  in the results' ``final`` folder that the manifest does not name moves to that folder's ``earlier_run/``
  (``wenart.report.final.move_stale_view_files``: a free name ``_2``, ``_3`` ...; moved, never deleted).
- Why: ``full.sh``'s first copy (300 s after the start, long before this run's report) took every preview and plan
  crop then in ``final/`` on the volume: the M12 previews of ``cam_r_L0_koridor_2`` / ``_3`` and an earlier run's
  previews of cameras this run does not render. The report moves them on the volume much later, but the copy only
  added files, so the job's results kept showing them next to the new views (the P3 symptom).
- How: this run is the report's own rule (``wenart.report.final.split_runs`` over ``run/*.json``: the run id of the
  newest stage record); the manifest is this run's when its ``run_id`` is that id (both None for a hand run). The
  orchestrator writes a record of this run for every project at the start of phase 1 (the intake, or its skip; an
  alternative gets its first one with its first stage), so from then on an earlier run's manifest names nothing; a
  needs-review manifest has no view. Before that first record (the pod setup) the volume's manifest is still the
  newest run's: the copy takes the views it names, and they move to ``earlier_run/`` of the results at the first
  copy after this run's first record.

Fix round after P3, part 3 (17 Oct 2026, docs/milestone13.md §14.9): an alternative's "this run" is its base
project's.

- What: ``copy_project`` reads this run's id once from the base project's ``run/`` (``this_run_id``) and hands it to
  the copy of the project and of each ``variants/<id>`` (``final_view_names(out_dir, run_id)``); an alternative's
  final manifest names view files only when its ``run_id`` is the base project's run id.
- Why: the scheduler writes an alternative's first record only in phase 5 (``add_variant_runs``, after the base
  project's refit). A job whose base project fails or stops in phases 1-4 never writes one, so the alternative's own
  ``run/`` still ended in the earlier run, its earlier manifest counted as this run's, and every copy (the EXIT trap's
  full copy too) put that run's previews and plan crops into ``final/<p>/variants/<id>/`` of the results as if this
  job had made them, while the base folder rightly held none (real02 and real04 have ``l-1b-acik-mutfak``).
- How: the scheduler gives a project and its alternatives one ``run_id``, so a job that reaches the alternative
  copies the same files as before; one that does not copies none of the alternative's views, and the ones an earlier
  copy of the job took move to ``variants/<id>/earlier_run/`` of the results (``move_stale_view_files``).

Fix round after P4a (17 Oct 2026, the library lens of the P4a analysis): the change list of ``ATTRIBUTION.md`` is
the run's own.

- What: ``write_attributions`` reads how many views of this run were polished (``run_polish``: the views of this
  run's final manifest, and of its alternatives' manifests, whose ``final`` is ``polished``) and hands the count to
  ``attribution_text`` as a ``kind: "run_polish"`` row of the credits (as the ``run_model`` rows, so the frozen
  signature stays). When none was, the text leaves the change "AI-retouched" out of every credit line and dataset
  notice (``without_retouch``) and says so under section 2; when some were, it says how many and keeps it. Without
  this run's manifest (a copy before the report, an earlier run's manifest) the text is as before.
- Why: P4a's real02 ATTRIBUTION.md said "rendered, AI-retouched" 122 times while its report shows 48 views and 0
  polished (AI polish is off in Milestone 13, CLAUDE.md): the change text is the catalogue's static ``attribution``
  string (``catalog_library.json``, the ABO / GSO / HSSD notices), copied as it is. The CC BY credit must name the
  changes that were made, not one that was not.
- How: the catalogue entries keep their text (a run with polish still uses it); only the run's file changes. The copy
  rewrites the file when the text changes (``_write_if_changed``), so the copy after the report corrects the one
  written before it.

Fix round after P4b (17 Oct 2026, the library lens of the P4b analysis): section 1 names the second recognition pass.

- What: ``TOOLS_AND_GENERATORS`` lists ``zai-org/GLM-4.6V-Flash`` (MIT; the plan symbols and sheet regions, pass 2)
  next to Qwen3-VL-8B (pass 1); every model of ``wenart/vision_check/check.yaml`` that the recognition asks (keys
  ``qwen``, ``glm``) has a row with check.yaml's licence (tests/test_m13_report.py keeps them equal). The rows of
  the final report's models table that ``run_model_rows`` reads now include the recognition models with their
  revisions and answer counts (``wenart.report.final.recognition_model_rows``, same fix round).
- Why: P4b's real03 ATTRIBUTION.md listed 9 tools and no GLM, and P4a's real02 file had the same gap, although
  GLM-4.6V-Flash answered 66 of 72 recognition questions on real03 and 48 of 54 on real02 (the pass-2 answers of
  the AI-typed pieces in both reports).
- How: the licence was read on 17 Oct 2026 from the Hugging Face model API (``license: mit``, sha = the pinned
  revision 411bb4d77144); the late recognition pass of lead decision 9 uses the same two models, so nothing else
  is added.

Fix round after P6b (23 Oct 2026; the library lens of the P6b analysis): the credit texts are plain text.

- What: ``_credit`` (every model's credit line, of a run and of a library folder) and ``audit_removed`` (the removal
  reasons) decode complete HTML entities (``plain_text``: ``html.unescape`` of ``HTML_ENTITY``) before the text goes
  into ``ATTRIBUTION.md``.
- Why: P6b's real03 ATTRIBUTION.md listed "Sink Console with Haden Faucet Set - Satin Nickel finish Knobs &amp;
  Faucet", "Hudson Reed Sublime Vanity Unit &amp; Basin" and "Cooke &amp; Lewis Deluvio ..." (P4b had none): the
  HSSD and ABO listings store HTML-escaped names and the catalogue's ``attribution`` (15 entries) copied them; a
  credit must name the product as it is called.
- How: decoded where the file is written; the catalogue keeps its text (``growth_entries.source_text`` decodes the
  titles of new entries), and a credit without an entity is unchanged.

``copy_lock(path)``: the job's copy lock (``full.sh`` exports it as
``WENART_COPY_LOCK``; the same ``flock`` the background loop takes), so the
orchestrator's own copy before the GPU tests never interleaves with the loop.

``--since STAMP``: only files newer than the stamp file (a full copy when it
does not exist yet); the stamp is renewed after the copy, 2 s back (the
volume's timestamps may have 1 s steps). The command prints only file counts
(nothing about a private project's files reaches the job log).

Why: the runner collects ``$RESULTS`` (and ``results-private``) over HTTP;
full-size PNGs, EXR passes and scenes stay on the volume.
"""
from __future__ import annotations

import fnmatch
import html
import json
import os
import re
import shutil
import time
from collections import deque
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from wenart.run.projects import ProjectRef
from wenart.run.state import private_record

KIB = 1024
MAX_TEXT_BYTES = 7999 * KIB        # find -size -8000k (rounded up to KiB, less than 8000)
MAX_JPEG_BYTES = 300 * KIB         # find -size -301k
MAX_PNG_BYTES = 3 * 1024 * KIB     # debug overlays and rectified pages (M7 §9.1)
MAX_CROPS = 200                    # recognition crops per project (M7 §9.1)
ATTRIBUTION = "ATTRIBUTION.md"
LIBRARY_CATALOG = "catalog_library.json"      # the prep pod's library catalogue (docs/milestone8.md §2)
OBJAVERSE_CATALOG = "catalog_objaverse.json"  # its M7 name (read when the library file is missing)
# = wenart.furniture.catalog.LIBRARY_SOURCES (hssd since build round 2 of Milestone 13: the HSSD layer of track T7,
# CC BY-NC 4.0, relaxed mode only; tests/test_library_growth_p4.py keeps the lists equal)
LIBRARY_SOURCES = ("objaverse", "abo", "generated", "gso", "hssd", "3dwh")     # 3dwh: 23 Oct 2026
# Milestone 13: the sources whose models are credited in section 2 / 3: the library sources (the HSSD layer among
# them) and the CC0 Poly Haven models (no credit required, listed as CC0 assets).
CREDIT_SOURCES = ("polyhaven",) + LIBRARY_SOURCES
POC_ONLY_FLAGS = ("non_commercial", "share_alike", "research_only", "regional", "tool_nc")
POC_FLAG_REASONS = {
    "non_commercial": "the licence forbids commercial use (a CC BY-NC licence or the dataset's non-commercial terms)",
    "share_alike": "the licence asks for derived works under the same licence (CC BY-SA)",
    "research_only": "the dataset's terms allow research use only",
    "regional": "the licence excludes some regions or uses",
    "tool_nc": "exported with nvdiffrast v0.4.0 (NVIDIA Source Code License, section 3.3: non-commercial; "
               "wenart.furniture.catalog.TOOL_NC); kept for the PoC by the user's decision D3 of 12 Oct 2026",
}
# Section 1: the tools and generators of the pipeline with their licences. Verified on 15 Oct 2026 against the
# official pages named in ``url`` (and docs/plan.md, wenart/vision_check/check.yaml, wenart/assets/generate.yaml):
# GPL tools run as installed programs (the renders and the DXF are not derived works: "The GPL only applies to
# the Blender application and not the artwork you create with it", docs.blender.org); the model ids and revisions
# are the ones the configs pin. Blender's GPL version (T8 review, 15 Oct 2026): the manual page names no version;
# the source (github.com/blender/blender, main) carries ``SPDX-License-Identifier: GPL-2.0-or-later`` in its files
# and its COPYING points to doc/license/GPL-license.txt, the GPL version 2 text, so the line says GPL-2.0-or-later
# (docs/plan.md §"Blender" writes GPL-3.0; the lead decides on the doc).
TOOLS_AND_GENERATORS = (
    {"name": "Blender 5.2 LTS (bpy, Cycles)", "licence": "GPL-2.0-or-later (program only; the renders are ours)",
     "url": "https://docs.blender.org/manual/en/latest/getting_started/about/license.html",
     "role": "scene build, Cycles renders, .blend / .glb export"},
    {"name": "GNU LibreDWG 0.14 (dwg2dxf)", "licence": "GPL-3.0-or-later (separate program)",
     "url": "https://github.com/LibreDWG/libredwg", "role": "DWG to DXF of the input documents (when a DWG is read)"},
    {"name": "Qwen/Qwen3.8-27B-FP8", "licence": "Apache-2.0", "url": "https://huggingface.co/Qwen/Qwen3.8-27B-FP8",
     "role": "agent and critic (orchestrator), vision judge (wenart/vision_check/check.yaml models.agent)"},
    {"name": "Qwen/Qwen3-VL-8B-Instruct", "licence": "Apache-2.0",
     "url": "https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct",
     "role": "recognition of plan symbols and sheet regions (pass 1), layout proposals, decor, vision check "
             "(wenart/vision_check/check.yaml models.qwen)"},
    # Fix round after P4b (17 Oct 2026): the second recognition pass. Verified on 17 Oct 2026 against the Hugging Face
    # model API (https://huggingface.co/api/models/zai-org/GLM-4.6V-Flash: license "mit", sha 411bb4d77144 = the
    # revision check.yaml pins); docs/plan.md §4.1 and docs/milestone5.md §1.6 record MIT as well.
    {"name": "zai-org/GLM-4.6V-Flash", "licence": "MIT", "url": "https://huggingface.co/zai-org/GLM-4.6V-Flash",
     "role": "recognition of plan symbols and sheet regions (pass 2, the independent second opinion; "
             "wenart/vision_check/check.yaml models.glm)"},
    {"name": "microsoft/TRELLIS.2-4B", "licence": "MIT (weights and code)",
     "url": "https://huggingface.co/microsoft/TRELLIS.2-4B",
     "role": "generated library models (image to 3D); its image condition is facebook/dinov3-vitl16-pretrain-lvd1689m "
             "(DINOv3 License, custom, gated: https://huggingface.co/facebook/dinov3-vitl16-pretrain-lvd1689m); "
             "its GLB export ran through nvdiffrast v0.4.0 (NVIDIA Source Code License, non-commercial: the models "
             "carry licence_flag tool_nc, https://github.com/NVlabs/nvdiffrast/blob/v0.4.0/LICENSE.txt)"},
    {"name": "Tongyi-MAI/Z-Image-Turbo", "licence": "Apache-2.0", "url": "https://huggingface.co/Tongyi-MAI/Z-Image-Turbo",
     "role": "product images for the generated models (and the AI polish, off in Milestone 13)"},
    {"name": "Infinigen (princeton-vl/infinigen)", "licence": "BSD-3-Clause (its infinigen_gpl submodule GPL-3.0, "
                                                             "run on the pod only)",
     "url": "https://github.com/princeton-vl/infinigen", "role": "procedural generated models (Milestone 12 pod P4)"},
    {"name": "Poly Haven API", "licence": "assets CC0 1.0 (https://polyhaven.com/license); the live API asks for a "
                                          "\"Powered by Poly Haven\" credit",
     "url": "https://github.com/Poly-Haven/Public-API", "role": "texture sets, HDRIs and CC0 models"},
)
POLYHAVEN_API_CREDIT = "Powered by Poly Haven (https://polyhaven.com): CC0 textures, HDRIs and models."
# Section 4: the HSSD layer (track T7, docs/milestone13.md §12 D2). Licence from the dataset card
# (https://huggingface.co/datasets/hssd/hssd-models: "You agree to use this dataset under the CC BY-NC 4.0 license
# terms"), citation from the README of https://github.com/3dlg-hcvc/hssd (both read on 15 Oct 2026).
HSSD_NOTICE = ("Contains 3D models from the Habitat Synthetic Scenes Dataset (HSSD-200), hssd/hssd-models "
               "(https://huggingface.co/datasets/hssd/hssd-models), licensed CC BY-NC 4.0 "
               "(https://creativecommons.org/licenses/by-nc/4.0/): non-commercial use only; used in relaxed licence "
               "mode with the user's acceptance of the dataset terms (12 Oct 2026). Citation: Khanna*, M., Mao*, Y., "
               "Jiang, H., Haresh, S., Shacklett, B., Batra, D., Clegg, A., Undersander, E., Chang, A. X., Savva, M.: "
               "Habitat Synthetic Scenes Dataset (HSSD-200): An Analysis of 3D Scene Scale and Realism Tradeoffs for "
               "ObjectGoal Navigation. arXiv preprint arXiv:2306.11290 (2023). Changes: scaled to the drawn "
               "footprint, re-oriented, rendered.")
POLYHAVEN_NOTICE = ("Poly Haven assets (textures, HDRIs, models; https://polyhaven.com) are CC0 1.0 "
                    "(https://polyhaven.com/license): no credit required. " + POLYHAVEN_API_CREDIT)
# ambientCG (the leaf atlases of the site's trees and hedges, the shell texture sets): "All assets are released under
# the Creative Commons CC0 license" (https://ambientcg.com, as wenart/blender/vegetation.py and wenart/assets/fetch.py
# LICENCES record it).
AMBIENTCG_NOTICE = ("ambientCG assets (texture sets and leaf atlases; https://ambientcg.com) are CC0 1.0 "
                    "(https://creativecommons.org/publicdomain/zero/1.0/): no credit required.")
# Section 1, the site build (build round 2; wenart/blender/vegetation.py, track T6): the Sapling Tree Gen add-on makes
# the species-look trees. Its 0.3.7 extension manifest (blender_manifest.toml: id sapling_tree_gen, version 0.3.7,
# license SPDX:GPL-3.0-or-later, website https://projects.blender.org/extensions/add_curve_sapling) and its source
# headers (SPDX-License-Identifier: GPL-2.0-or-later, Blender Foundation 2011-2022) were read on 15 Oct 2026 from the
# extension package; it runs as an installed program through bpy.ops.curve.tree_add, nothing of it is in this
# repository, and the trees it generates are our scene geometry (the GPL covers the program, not its output).
SAPLING_TOOL = {"name": "Sapling Tree Gen 0.3.7 (Blender extension sapling_tree_gen)",
                "licence": "GPL-3.0-or-later per its 0.3.7 extension manifest (GPL-2.0-or-later per its source "
                           "headers); run through bpy.ops.curve.tree_add as an installed add-on, nothing copied",
                "url": "https://projects.blender.org/extensions/add_curve_sapling",
                "role": "species-look trees of the site (the generated trees are ours)"}
POLYHAVEN_PAGE = "https://polyhaven.com/a/{id}"            # = wenart.assets.models.PAGE_URL
VEGETATION_TABLE_NOTE = "per the vegetation table (wenart/blender/vegetation.py; the manifest entry names no atlas)"
DEFAULT_CHANGES = "scaled to the drawn footprint, re-oriented, rendered"
# Fix round after P4a: the change the catalogue's credit texts name for AI polish; left out when no view of the run
# was polished (``without_retouch``, ``run_polish``).
RETOUCH_CHANGE = "AI-retouched"
# The library work folder's files that never go to $RESULTS (``library_files``): model files (the GLBs live in the
# sources' caches and <assets>/models/<source>/) and anything larger than the text limit.
LIBRARY_SKIP_SUFFIXES = (".glb", ".gltf", ".bin", ".blend", ".ply", ".obj", ".fbx", ".part", ".tmp")
# Milestone 10: nor the generation's input images (``generate/**/*.png``, about 0.5 MB each, 310 MB after pod L1d):
# they filled the runner's 400 MB collection cap, so later result files were left out (pod L1d of 9 Oct 2026);
# their prompts and records (``generate/**/*.json``) still go, as M9 committed them.
LIBRARY_SKIP_GENERATE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp")
IMAGE_AREAS = ("renders", "polish", "gate", "check", "realism", "final", "agent")   # folders with images
VARIANTS_DIR = "variants"          # = wenart.run.stages.VARIANTS_DIR (Milestone 10)
LOG_TAIL_LINES = 400
STAMP_OVERLAP_S = 2
PREVIEW_PATTERNS = ("*_preview.jpg", "*_alt_preview.jpg", "*_gate.jpg", "*_check.jpg", "*_plan.jpg", "contact_*.jpg")


@dataclass(frozen=True)
class Rule:
    src: str          # folder relative to out/ ("" = out itself; may end in a glob such as controls/hide_*)
    area: str         # result area
    dst: str          # sub-folder of the area folder ("{name}" = the matched folder's name)
    kind: str         # general | style | json | debug | scene | png | crops | recognition | names:<a>,<b> |
                      # private_final | private_run


PUBLIC_RULES = (
    Rule("", "furniture", "", "general"),
    Rule("", "renders", "", "style"),
    Rule("style_photos", "furniture", "style_photos", "json"),
    Rule("layout_debug", "furniture", "layout_debug", "debug"),
    Rule("scene", "renders", "", "scene"),
    Rule("scene", "renders", "", "names:architect.md"),          # 25 Oct 2026: the architect's review
    Rule("scene", "renders", "", "names:model_review.md,model_review.json"),     # 26 Oct 2026: the model review
    Rule("renders", "renders", "", "general"),
    Rule("controls", "renders", "controls", "general"),
    Rule("controls/hide_*", "renders", "controls/{name}", "general"),
    Rule("polish", "polish", "", "general"),
    Rule("polish/sweep", "polish", "sweep", "general"),
    Rule("polish/smoke", "polish", "smoke", "general"),
    Rule("gate", "gate", "", "general"),
    Rule("check", "check", "", "general"),
    Rule("final", "final", "", "general"),
    Rule("final/debug", "final", "debug", "debug"),
    Rule("run", "run", "", "general"),
    Rule("run/logs", "run", "logs", "general"),
    Rule("ab/renders", "realism", "", "general"),
    Rule("ab", "realism", "", "names:cameras_check.json,pairs.json,pairs_v2.json"),
    Rule("check/realism", "realism", "", "general"),
    # Milestone 7 (§9.1)
    Rule("debug", "furniture", "debug", "png"),
    Rule("rectified", "furniture", "rectified", "png"),
    Rule("recognition", "recognition", "", "recognition"),
    Rule("recognition/crops", "recognition", "crops", "crops"),
    # fix round after P5 (22 Oct 2026), review: the plan crops the reading draws for a fixed piece it shrinks or
    # corrects without a question crop (reading.READING_CROP_DIR); kept apart from the question crops' MAX_CROPS
    Rule("recognition/reading", "recognition", "reading", "crops"),
    Rule("detect", "check", "detect", "json"),
    # Milestone 9: the AI decor's debug images and records; the 3D files of the final scene (user request of
    # 4 Oct 2026: a packed .blend and a .glb that open in Blender) with their manifest.
    Rule("decor_debug", "furniture", "decor_debug", "png"),
    Rule("decor_debug", "furniture", "decor_debug", "json"),
    Rule("export", "final", "3d", "export"),
    # Milestone 10 (docs/milestone10.md §1.5): the sheet_region questions and answers (the next run's seeds,
    # results/recognition/<p>/sheets/) and the sheet debug images; sheets.json and sheets_report.md go with the
    # general rule of out/.
    Rule("sheets", "recognition", "sheets", "recognition"),
    Rule("sheets/crops", "recognition", "sheets/crops", "crops"),
    Rule("sheets_debug", "furniture", "sheets_debug", "png"),
    # Milestone 11 (docs/milestone11.md §9): the orchestrator's decision log, overrides and images, the round
    # previews, and the before/after images the final report links (final/agent/).
    Rule("orchestrator", "agent", "", "agent"),
    Rule("orchestrator/images", "agent", "images", "agent"),
    Rule("orchestrator/compare", "agent", "compare", "agent"),
    Rule("agent/previews", "agent", "previews", "general"),
    Rule("final/agent", "final", "agent", "agent"),
    # Milestone 13 (docs/milestone13.md §7): the before | after sheets of wenart.report.sheets13 (JPEG <= 300 KB,
    # sheets13.json / .md); the metrics13 JSON and markdown in final/ go with the general rule.
    Rule("final/sheets13", "final", "sheets13", "debug"),
)
PRIVATE_RULES = (
    Rule("final", "final", "", "private_final"),
    Rule("run", "run", "", "private_run"),
)


def _match(name: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatchcase(name, p) for p in patterns)


def wanted(rule: Rule, path: Path) -> Optional[str]:
    """How ``path`` is copied under ``rule``: ``copy``, ``tail`` (log), ``record`` (private stage record)
    or None (not copied)."""
    name = path.name
    size = path.stat().st_size
    text = name.endswith((".json", ".md")) and size <= MAX_TEXT_BYTES
    small_jpg = name.endswith(".jpg") and size <= MAX_JPEG_BYTES
    kind = rule.kind
    if kind == "general":
        if text:
            return "copy"
        if small_jpg and _match(name, PREVIEW_PATTERNS):
            return "copy"
        return "tail" if name.endswith(".log") else None
    if kind == "style":
        return "copy" if _match(name, ("style*.json",)) and size <= MAX_TEXT_BYTES else None
    if kind == "json":
        return "copy" if name.endswith(".json") and size <= MAX_TEXT_BYTES else None
    if kind == "debug":
        return "copy" if (name.endswith(".json") and size <= MAX_TEXT_BYTES) or small_jpg else None
    if kind == "scene":
        if name.endswith(".json") and size <= MAX_TEXT_BYTES:
            return "copy"
        return "tail" if name.endswith(".log") else None
    if kind in ("png", "crops"):
        return "copy" if name.endswith(".png") and size <= MAX_PNG_BYTES else None
    if kind == "recognition":
        ok = name == "requests.json" or (name.startswith("answers_") and name.endswith(".json"))
        return "copy" if ok and size <= MAX_TEXT_BYTES else None
    if kind.startswith("names:"):
        return "copy" if name in kind[6:].split(",") and size <= MAX_TEXT_BYTES else None
    if kind == "agent":                       # Milestone 11: log.json / log.md / overrides.json and the log's images
        if text:
            return "copy"
        if name.endswith(".png") and size <= MAX_PNG_BYTES:
            return "copy"
        return "copy" if small_jpg else None
    if kind == "private_final":
        if name in ("final_report.md", "final_manifest.json") and size <= MAX_TEXT_BYTES:
            return "copy"
        return "copy" if small_jpg and _match(name, ("*_final_preview.jpg", "contact_*.jpg")) else None
    if kind == "private_run":
        return "record" if name.endswith(".json") and size <= MAX_TEXT_BYTES else None
    if kind == "export":                      # Milestone 9: the 3D files (no size limit: they are the deliverable)
        if name.endswith((".blend", ".glb")):
            return "copy"
        return "copy" if name == "export_manifest.json" and size <= MAX_TEXT_BYTES else (
            "tail" if name.endswith(".log") else None)
    raise ValueError(f"unknown copy rule kind {kind!r}")


def _sources(out_dir: Path, rule: Rule) -> list[tuple[Path, str]]:
    """``[(source folder, destination sub-folder)]`` of a rule."""
    if any(ch in rule.src for ch in "*?["):
        found = sorted(p for p in out_dir.glob(rule.src) if p.is_dir() and not p.is_symlink())
        return [(p, rule.dst.format(name=p.name)) for p in found]
    folder = out_dir / rule.src if rule.src else out_dir
    return [(folder, rule.dst)] if folder.is_dir() and not folder.is_symlink() else []


def tail_text(path: Path, n: int = LOG_TAIL_LINES) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return "".join(deque(fh, maxlen=n))


def copy_project(ref: ProjectRef, since: Optional[float] = None) -> int:
    """Copy one project's files (public layout or private allow-list) and those of its alternatives (Milestone
    10); the number of files written."""
    out_dir = Path(ref.out_dir)
    if not out_dir.is_dir():
        return 0
    run_id = this_run_id(out_dir)            # fix round part 3: the base project's run decides for its alternatives
    count = _copy_tree(ref, out_dir, "", since, run_id)
    for vid in variant_folders(out_dir):
        count += _copy_tree(ref, out_dir / VARIANTS_DIR / vid, f"{VARIANTS_DIR}/{vid}", since, run_id)
    count += write_attributions(ref)
    return count


def variant_folders(out_dir: Path) -> list[str]:
    """The alternatives of ``<out>/building_final.json`` that have a folder ``<out>/variants/<id>`` (Milestone 10)."""
    from wenart.building import alternative_ids

    try:
        building = json.loads((Path(out_dir) / "building_final.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    root = Path(out_dir) / VARIANTS_DIR
    return [vid for vid in alternative_ids(building if isinstance(building, dict) else None)
            if (root / vid).is_dir() and not (root / vid).is_symlink()]


def this_run_id(project_out: Path) -> Optional[str]:
    """Fix round after P3, part 3 (module docstring): this run's id for a project output and its alternatives, by
    the report's own rule: the run id of the newest stage record of ``<project_out>/run/``
    (``wenart.report.final.split_runs`` over ``load_stage_records``); None for a hand run without run ids. For an
    alternative pass its base project's folder: the alternative's own ``run/`` gets this run's first record only in
    phase 5."""
    from wenart.report import final as F

    return F.split_runs(F.load_stage_records(Path(project_out)))[2]


def final_view_names(out_dir: Path, run_id: Optional[str]) -> set:
    """Fix round after P3, part 2 (module docstring): the preview and plan-crop names that
    ``<out>/final/final_manifest.json`` names (``views[].preview``, ``views[].plan``) when that manifest is this
    run's, else an empty set (no manifest, an earlier run's manifest, a needs-review manifest: no view). The manifest
    is this run's when its ``run_id`` is ``run_id`` (both None for a hand run without run ids). Part 3: ``run_id`` is
    this run's id of the base project (``this_run_id`` of the project folder, also for its ``variants/<id>``), never
    the one of an alternative's own ``run/``."""
    from wenart.report import final as F

    out_dir = Path(out_dir)
    try:
        manifest = json.loads((out_dir / F.FINAL_DIR / F.MANIFEST_NAME).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    if not isinstance(manifest, dict):
        return set()
    if (manifest.get("run_id") or None) != (run_id or None):
        return set()
    views = manifest.get("views") if isinstance(manifest.get("views"), list) else []
    return {str(v[key]) for v in views if isinstance(v, dict) for key in ("preview", "plan")
            if isinstance(v.get(key), str) and v[key]}


def _view_due(path: Path, target: Path, since: Optional[float]) -> bool:
    """A view file of this run is copied when it is new since the stamp, or when the results miss it or hold an
    older copy (a preview written while the volume's manifest was still an earlier run's is taken by the next copy,
    not only by the job's last full copy)."""
    if since is None:
        return True
    mtime = path.stat().st_mtime
    if mtime > since:
        return True
    try:
        return target.stat().st_mtime < mtime
    except OSError:
        return True


def unchanged_copy(path: Path, target: Path) -> bool:
    """30 Oct 2026 (pod-time item 5, user OK): ``target`` is a copy of ``path`` that is still current: the same size
    and the same modified time to the nanosecond (``shutil.copy2`` keeps it; the quick check of ``prep``'s library
    copy, exact here: a stage record rewritten within a second keeps its size). Real04 run 20261030-112241-full: the
    job's two full copies wrote all ~9,300 result files to the network volume again (3.6 min the last one) though only
    the top-down views had changed."""
    try:
        st, tt = path.stat(), target.stat()
    except OSError:
        return False
    return tt.st_size == st.st_size and tt.st_mtime_ns == st.st_mtime_ns


def _copy_tree(ref: ProjectRef, out_dir: Path, prefix: str, since: Optional[float], run_id: Optional[str]) -> int:
    """The rules over one output folder: the project's (``prefix`` "") or an alternative's (``variants/<id>``).
    Fix round after P3, part 2: the view files of ``final/`` follow this run's final manifest (``final_view_names``)
    and an earlier run's view files in the results' ``final`` folder move to its ``earlier_run/``. Part 3: this run
    is ``run_id``, the base project's (``copy_project``)."""
    from wenart.report import final as F

    rules = PRIVATE_RULES if ref.private else PUBLIC_RULES
    views = final_view_names(out_dir, run_id)
    count = 0
    for rule in rules:
        final_rule = rule.src == F.FINAL_DIR
        for folder, sub in _sources(out_dir, rule):
            sub = "/".join(p for p in (prefix, sub) if p)
            dst_dir = ref.results_area(rule.area) / sub if sub else ref.results_area(rule.area)
            taken = 0
            for path in sorted(folder.iterdir()):
                if not path.is_file() or path.is_symlink():
                    continue
                how = wanted(rule, path)
                if how is not None and rule.kind == "crops":
                    taken += 1                       # the first MAX_CROPS crops by name, new or not
                    if taken > MAX_CROPS:
                        continue
                if how is None:
                    continue
                if final_rule and _match(path.name, F.STALE_VIEW_PATTERNS):
                    if path.name not in views or not _view_due(path, dst_dir / path.name, since):
                        continue                     # an earlier run's view file, or this run's already copied
                elif since is not None and path.stat().st_mtime <= since:
                    continue
                dst_dir.mkdir(parents=True, exist_ok=True)
                target = dst_dir / path.name
                if how == "copy":
                    if unchanged_copy(path, target):
                        continue                     # pod-time item 5: copied before and not changed since
                    shutil.copy2(path, target)
                elif how == "tail":
                    target.write_text(tail_text(path), encoding="utf-8")
                else:   # private stage record without its inputs map
                    try:
                        data = json.loads(path.read_text(encoding="utf-8"))
                    except (OSError, ValueError):
                        continue
                    if not isinstance(data, dict) or data.get("kind") != "stage_record":
                        continue
                    target.write_text(json.dumps(private_record(data), indent=1, ensure_ascii=False) + "\n",
                                      encoding="utf-8")
                count += 1
        if final_rule:
            # The view files the results took before (earlier in this job, before this run's report) that this run's
            # manifest does not name leave the results' final folder: moved to its earlier_run/, never deleted.
            area = ref.results_area(rule.area)
            F.move_stale_view_files(area / prefix if prefix else area, views, [])
    return count


# --------------------------------------------------------------------------
# ATTRIBUTION.md (docs/milestone7.md §7.3)
# --------------------------------------------------------------------------

def _source_of(asset: dict) -> str:
    """The library source of a fitted asset or a catalogue entry (``library`` of a fit asset, else ``source``)."""
    return str(asset.get("library") or asset.get("source") or "")


# fix round after P6b (23 Oct 2026): a complete HTML entity (named with its ";", decimal or hex); a bare "&" ("Stone &
# Beam", "R&B") or a legacy name without ";" ("&copy") is text and stays
HTML_ENTITY = re.compile(r"&(?:#[0-9]+|#[xX][0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]*);")


def plain_text(text) -> str:
    """Fix round after P6b (module docstring): ``text`` with its complete HTML entities decoded (``HTML_ENTITY``:
    ``&amp;`` -> ``&``, ``&quot;`` -> ``"``); a text without one is returned as it is."""
    return HTML_ENTITY.sub(lambda m: html.unescape(m.group(0)), str(text))


def _credit(asset: dict) -> str:
    """The credit line of a fitted library asset or catalogue entry (``attribution``; for an Objaverse one without
    it, the §7.3 line built from its fields). Fix round after P6b: as plain text (``plain_text``)."""
    return plain_text(_credit_raw(asset))


def _credit_raw(asset: dict) -> str:
    if asset.get("attribution"):
        return str(asset["attribution"])
    if _source_of(asset) == "polyhaven":          # Milestone 13: CC0 models are listed (section 2), credit optional
        name = asset.get("name") or asset.get("title") or asset.get("asset_id") or asset.get("id") or "?"
        return f"\"{name}\" by Poly Haven ({asset.get('url') or 'https://polyhaven.com'}), CC0 1.0: no credit required"
    fields = [asset.get(k) for k in ("title", "author", "source_url")]
    if all(fields) and _source_of(asset) in ("objaverse", "") and asset.get("licence"):
        from wenart.assets.objaverse import attribution_line
        try:
            from wenart.assets.objaverse import load_config
            cfg = load_config()
        except Exception:  # noqa: BLE001 - the line has built-in names for CC0 and CC BY 4.0
            cfg = None
        return attribution_line(str(fields[0]), str(fields[1]), str(fields[2]), str(asset["licence"]), cfg)
    return f"{asset.get('asset_id') or asset.get('uid') or '?'}: no attribution recorded (check the catalogue entry)"


def _library_asset(asset) -> bool:
    """A credited model: a library asset of ``CREDIT_SOURCES`` (Milestone 13: the CC0 Poly Haven models too) that is
    not a parametric, module or not-built record."""
    return (isinstance(asset, dict) and _source_of(asset) in CREDIT_SOURCES
            and asset.get("method") not in ("parametric", "module", "none"))


def _licence_fields(asset: dict) -> dict:
    """Milestone 13: ``licence``, ``licence_flag``, ``commercial_safe``, ``licence_url`` of a fitted asset or a
    catalogue entry through track T1's catalogue functions (the flag from the entry's own flag, the licence text and
    the export tool; the page from ``licence_url`` or the licence text)."""
    from wenart.furniture import catalog as CAT

    flag = CAT.licence_flag_of(asset)
    out = {"licence": asset.get("licence") or asset.get("license"), "licence_flag": flag,
           "commercial_safe": CAT.commercial_safe(asset), "licence_url": CAT.licence_url_of(asset)}
    if CAT.logo_flagged(asset):                   # 30 Oct 2026 (UL215): a maker's logo or print, relaxed mode only
        out.update(logo_flag=True, logo_reason=asset.get("logo_reason") or "a maker's logo or print on the model")
    return out


def read_building(out_dir: Path) -> Optional[dict]:
    """``<out>/building_final.json`` as a dict, None when missing or unreadable."""
    try:
        building = json.loads((Path(out_dir) / "building_final.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return building if isinstance(building, dict) else None


def project_licence_mode(out_dir: Path) -> str:
    """The licence mode of a project output (Milestone 13): ``project.licence_mode`` of its ``building_final.json``
    (the fit writes it, track T1), else ``catalog.licence_mode()`` (env ``WENART_LICENCE_MODE`` > ``commercial``)."""
    from wenart.furniture import catalog as CAT

    building = read_building(out_dir) or {}
    mode = ((building.get("project") or {}).get("licence_mode") if isinstance(building.get("project"), dict)
            else None)
    if mode in CAT.LICENCE_MODES:
        return str(mode)
    return CAT.licence_mode()


def project_credits(out_dir: Path) -> list[dict]:
    """``[{"credit", "pieces": [(id, type)], "source", "asset_id", "licence", "licence_flag", "commercial_safe",
    "licence_url", "changes", "kind": "model"}]`` of the library models (ABO, Objaverse, generated, GSO, HSSD and,
    Milestone 13, the CC0 Poly Haven models; docs/milestone8.md §2, docs/milestone13.md §6) in
    ``<out>/building_final.json``: its furniture pieces' and decor items' ``asset``, one entry per model (catalogue
    id), in id order. Milestone 13: every entry carries ``licence_flag``, ``commercial_safe`` and ``licence_url``
    (``wenart.furniture.catalog``, track T1)."""
    building = read_building(out_dir)
    if building is None:
        return []
    found: dict = {}
    for item in list(building.get("furniture") or []) + list(building.get("decor") or []):
        asset = item.get("asset") if isinstance(item, dict) else None
        if not _library_asset(asset):
            continue
        key = str(asset.get("asset_id") or asset.get("uid") or "")
        if key not in found:
            entry = {"credit": _credit(asset), "pieces": [], "source": _source_of(asset), "asset_id": key,
                     "kind": "model", "changes": DEFAULT_CHANGES}
            entry.update(_licence_fields(asset))
            found[key] = entry
        found[key]["pieces"].append((str(item.get("id") or "?"), str(item.get("type") or "?")))
    return [found[k] for k in sorted(found)]


def texture_credits(out_dir: Path) -> list[dict]:
    """Milestone 13, section 2: the CC0 texture sets and the HDRI of ``<out>/scene/scene_manifest.json`` (its
    ``materials`` with ``textured`` and ``asset``: slug, asset, source, licence; ``lighting.world`` of kind ``hdri``:
    every HDRI under the assets folder was fetched by ``wenart.assets.fetch``, which accepts CC0 only), one entry
    per asset, in asset order; ``[]`` without a scene manifest."""
    try:
        scene = json.loads((Path(out_dir) / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(scene, dict):
        return []
    found: dict = {}
    for key, m in (scene.get("materials") or {}).items():
        if not isinstance(m, dict) or not m.get("textured") or not m.get("asset"):
            continue
        asset = str(m["asset"])
        source = str(m.get("source") or "unknown")
        licence = str(m.get("licence") or "unknown")
        entry = found.setdefault(asset, {
            "credit": f"texture set {asset} ({SOURCE_NAMES.get(source, source)}, {licence})", "pieces": [],
            "source": source, "asset_id": asset, "kind": "texture", "licence": licence,
            "licence_flag": "none" if licence.upper().startswith("CC0") else "unknown",
            "commercial_safe": licence.upper().startswith("CC0"),
            "licence_url": _texture_licence_url(source), "changes": "tiled, tinted and lit in the shell materials"})
        entry["pieces"].append((str(key), str(m.get("slug") or "material")))
    world = (scene.get("lighting") or {}).get("world") if isinstance(scene.get("lighting"), dict) else None
    if isinstance(world, dict) and world.get("kind") == "hdri" and world.get("file"):
        stem = Path(str(world["file"])).stem
        found.setdefault(f"hdri:{stem}", {
            "credit": f"HDRI {stem} (CC0: fetched by wenart.assets.fetch, which accepts CC0 only, from Poly Haven)",
            "pieces": [("world", "hdri")], "source": "polyhaven", "asset_id": f"hdri:{stem}", "kind": "hdri",
            "licence": "CC0", "licence_flag": "none", "commercial_safe": True,
            "licence_url": _texture_licence_url("polyhaven"), "changes": "used as the sky light of the interiors"})
    return [found[k] for k in found]


def hssd_notice() -> str:
    """The HSSD dataset notice of section 4, built from ``wenart.assets.hssd.DATASET`` (the module states the name,
    the page, the licence and its page, the citation and the use note; the citation text was checked against the
    README BibTeX of https://github.com/3dlg-hcvc/hssd and the dataset card, which has no citation block, on
    15 Oct 2026); ``HSSD_NOTICE`` (the same facts) when the module cannot be imported."""
    try:
        from wenart.assets import hssd as H
        d = H.DATASET
    except Exception:  # noqa: BLE001 - the notice must never fail the copy
        return HSSD_NOTICE
    return (f"Contains 3D models from {d['name']} ({d['page']}), licensed {d['licence']} ({d['licence_url']}): "
            f"non-commercial use only; {d['note']}. Dataset terms: \"{d['gated']}\" (the dataset card, "
            f"revision {str(d.get('revision') or '')[:7]}). Citation: {d['citation']}. Changes: {DEFAULT_CHANGES}.")


def vegetation_credits(out_dir: Path) -> list[dict]:
    """Build round 2 (track T6's site build): the credits of the vegetation sources the scene manifest says were
    used, read from ``<out>/scene/scene_manifest.json`` ``objects[]`` entries that carry ``veg_method`` (trees,
    hedges, grass; ``wenart.blender.site.build_site`` writes ``veg_method``, ``asset`` and ``licence`` on them):

    - ``polyhaven``: the Poly Haven CC0 model instanced (``asset`` = its id; kind ``model``, section 2, with the name
      of ``vegetation.POLYHAVEN_MODELS`` and the asset page);
    - ``sapling``: one ``kind: "tool"`` row for section 1 (``SAPLING_TOOL``, with the trees it made), and the leaf
      atlas its leaf card uses (``vegetation._tree_sapling``: ``leaf_atlas(species)``), credited like a card tree's;
    - ``cards`` / ``sapling``: the ambientCG CC0 leaf atlas (``asset`` = the atlas id; kind ``texture``, section 2).
      The builders record the atlas as ``atlas`` and ``site.build_site`` copies ``asset`` only, so a tree or hedge
      entry names no atlas today: then the atlas of the species' leaf kind comes from ``vegetation.LEAF_ATLASES``
      with the note ``VEGETATION_TABLE_NOTE`` (the entry's ``species`` is the species name; its leaf kind is looked
      up; ``leaf_atlas`` picks the same one). A grass patch of cards uses no atlas (nothing to credit);
    - ``palm``: our frond geometry without an atlas (``vegetation._tree_palm``: ``atlas`` None): nothing to credit
      unless the entry names an ``asset``.

    One row per asset, in asset order; ``[]`` without a scene manifest or without vegetation."""
    try:
        scene = json.loads((Path(out_dir) / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    rows = scene.get("objects") if isinstance(scene, dict) else None
    if not isinstance(rows, list):
        return []
    try:
        from wenart.blender import vegetation as VG      # stdlib-only at import; bpy is imported in its builders
    except Exception:  # noqa: BLE001 - the credits then carry the manifest's facts only
        VG = None
    found: dict = {}
    tool_pieces: list = []
    for o in rows:
        if not isinstance(o, dict) or not o.get("veg_method"):
            continue
        method = str(o["veg_method"])
        oid = str(o.get("element_id") or o.get("wenart_id") or o.get("name") or "?")
        part = str(o.get("site_part") or ("tree" if o.get("species") else "vegetation"))
        if method == "polyhaven" and o.get("asset"):
            aid = str(o["asset"])
            name = ((VG.POLYHAVEN_MODELS.get(aid) or {}).get("name") if VG else None) or aid
            entry = found.setdefault(aid, {
                "credit": f"\"{name}\" by Poly Haven ({POLYHAVEN_PAGE.format(id=aid)}), CC0 1.0: no credit required",
                "pieces": [], "source": "polyhaven", "asset_id": aid, "kind": "model", "licence": "CC0",
                "licence_flag": "none", "commercial_safe": True, "licence_url": _texture_licence_url("polyhaven"),
                "changes": "instanced and scaled to the drawn height (site vegetation)"})
            entry["pieces"].append((oid, part))
            continue
        if method == "library" and o.get("asset"):
            # 30 Oct 2026 (lesson UL129): the site's library models (cars, trees, a pool's seats) are credited from
            # their catalogue entry like the furniture (real04's car was missing from ATTRIBUTION.md)
            aid = str(o["asset"])
            cat = _site_catalogue().get(aid) or {"id": aid, "licence": o.get("licence")}
            entry = found.get(aid)
            if entry is None:
                entry = found[aid] = {"credit": _credit(cat), "pieces": [], "source": _source_of(cat), "asset_id": aid,
                                      "kind": "model", "changes": "fitted uniformly to a real size on the site"}
                entry.update(_licence_fields(cat))
            entry["pieces"].append((oid, part))
            continue
        if method == "sapling":
            tool_pieces.append((oid, part))               # the add-on (section 1); its leaf atlas is credited below
        # 26 Oct 2026: ``context`` is the distant tree groups at the horizon (site.build_context), its crowns textured
        # with the leaf atlas its entry names (none: a procedural leaf texture, nothing to credit)
        if method in ("cards", "palm", "sapling", "context"):
            aid = str(o.get("asset") or "")
            note = ""
            # no atlas named: a card tree, a Sapling tree's leaves and a hedge all use the species' atlas of the
            # vegetation table (``leaf_atlas``); a palm's fronds and grass cards are our geometry without one
            if not aid and VG is not None and method != "palm" and part in ("hedge", "tree", "vegetation"):
                leaf = (VG.species_record(o.get("species")).get("leaf") if o.get("species") else None) or "broadleaf"
                aid = str(VG.LEAF_ATLASES.get(leaf) or VG.LEAF_ATLASES.get("broadleaf") or "")
                note = f" ({VEGETATION_TABLE_NOTE})"
            if not aid:
                continue                                  # grass cards, a palm: our geometry, nothing to credit
            entry = found.setdefault(f"atlas:{aid}", {
                "credit": f"leaf atlas {aid} (ambientCG, CC0){note}", "pieces": [], "source": "ambientcg",
                "asset_id": aid, "kind": "texture", "licence": "CC0", "licence_flag": "none",
                "commercial_safe": True, "licence_url": _texture_licence_url("ambientcg"),
                "changes": "leaf cards of the site's trees and hedges (the leaves of the Sapling trees among them)"})
            entry["pieces"].append((oid, part))
    out = [found[k] for k in found]
    if tool_pieces:
        out.append(dict(SAPLING_TOOL, kind="tool", pieces=tool_pieces))
    return out


_SITE_CATALOGUE: dict = {}


def _site_catalogue() -> dict:
    """``{id: entry}`` of the library catalogue (``wenart/furniture/catalog_library.json``: entries, decor, extras),
    read once; {} without it."""
    if "by_id" not in _SITE_CATALOGUE:
        try:
            data = json.loads((Path(__file__).resolve().parents[1] / "furniture" / "catalog_library.json")
                              .read_text(encoding="utf-8"))
            _SITE_CATALOGUE["by_id"] = {str(e.get("id")): e for key in ("entries", "decor", "extras")
                                        for e in data.get(key) or [] if isinstance(e, dict) and e.get("id")}
        except (OSError, ValueError):
            _SITE_CATALOGUE["by_id"] = {}
    return _SITE_CATALOGUE["by_id"]


def _texture_licence_url(source: str) -> str:
    try:
        from wenart.assets import fetch as FETCH
        return str(FETCH.LICENCE_URLS.get(source) or "")
    except Exception:  # noqa: BLE001 - the page is a courtesy; the licence word is recorded anyway
        return ""


def _notices(sources) -> list[str]:
    """The notices of the sources present (``wenart.assets.objaverse.source_notices``: the ODC-By notice of
    Objaverse, the ABO credit, the generated-model note)."""
    from wenart.assets import objaverse as OBJ      # stdlib-only at import; the yaml is read here
    try:
        cfg = OBJ.load_config()
    except Exception:  # noqa: BLE001 - the notice has built-in defaults (allenai/objaverse @ 21e4e14)
        cfg = None
    try:
        return OBJ.source_notices(sources, cfg)
    except Exception:  # noqa: BLE001 - abo.yaml unreadable: the ODC-By notice stays (Objaverse is the M7 source)
        return [OBJ.odc_by_notice(cfg)] if "objaverse" in sources else []


def _notice() -> str:
    """The ODC-By notice (M7 name)."""
    return _notices(["objaverse"])[0]


SOURCE_NAMES = {"abo": "Amazon Berkeley Objects", "objaverse": "Objaverse 1.0", "generated": "generated models",
                "gso": "Google Scanned Objects", "polyhaven": "Poly Haven", "hssd": "HSSD (Habitat Synthetic Scenes "
                "Dataset)", "ambientcg": "ambientCG", "3dwh": "3D Warehouse (the user's zip)"}
SOURCE_ORDER = ("abo", "gso", "objaverse", "generated", "hssd", "3dwh", "polyhaven", "ambientcg")


def run_model_rows(out_dir: Path) -> list[dict]:
    """The AI models the final report recorded for the run (``<out>/final/final_manifest.json`` ``models``:
    role, repo, revision, licence), for section 1; ``[]`` without a report."""
    try:
        manifest = json.loads((Path(out_dir) / "final" / "final_manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    rows = manifest.get("models") if isinstance(manifest, dict) else None
    return [r for r in rows or [] if isinstance(r, dict) and r.get("repo")]


def audit_removed(entry: dict) -> str:
    """The reasons of a model the Milestone 12 library audit removed (catalogue ``audit.status == "removed"``,
    docs/m12_tracks/B.md) as one text; "" for every other entry. Removed models stay credited: older thumbnails
    and renders still show them."""
    audit = entry.get("audit") if isinstance(entry, dict) else None
    if not isinstance(audit, dict) or audit.get("status") != "removed":
        return ""
    reasons = [plain_text(r) for r in audit.get("reasons") or [] if str(r).strip()]     # fix round after P6b
    return "; ".join(reasons) or "no reason recorded"


def _credit_flag(c: dict) -> str:
    """The flag word of a credit: its ``licence_flag`` (Milestone 13: ``none`` for CC0 / CC BY), else derived from
    the licence text (an older credit dict without the field)."""
    flag = c.get("licence_flag")
    if flag in (None, ""):
        from wenart.furniture import catalog as CAT
        flag = CAT.licence_text_flag(c.get("licence")) if c.get("licence") else "none"
    return str(flag)


def _credit_line(c: dict) -> str:
    """One credit line (the docs/milestone8.md §2 format: the credit, the licence flag when it limits the use, the
    M12 audit removal, the pieces that use it)."""
    pieces = ", ".join(f"{pid} ({ptype})" for pid, ptype in c.get("pieces") or [])
    flag = _credit_flag(c)
    text = f" [licence flag: {flag}]" if flag != "none" else ""
    if c.get("removed"):
        text += f" [removed by the M12 library audit: {c['removed']}]"
    # Milestone 13: the catalogue id of a model closes the line, so a flagged id of the report (final manifest
    # views[].commercial_safe.flagged) can be found in the file (metric 16 of docs/milestone13.md §7).
    aid = f" [asset: {c['asset_id']}]" if c.get("asset_id") and c.get("kind", "model") == "model" else ""
    return f"- {c['credit']}{text}" + (f" (used for {pieces})" if pieces else "") + aid


def without_retouch(text: str) -> str:
    """Fix round after P4a: ``text`` without the change ``RETOUCH_CHANGE`` of a change list ("rendered,
    AI-retouched; PoC use" -> "rendered; PoC use", "AI-retouched, scaled" -> "scaled"); other text is kept."""
    word = re.escape(RETOUCH_CHANGE)
    text = re.sub(rf",\s*{word}\b", "", text)
    text = re.sub(rf"\b{word},\s*", "", text)
    return re.sub(rf"\s*\b{word}\b", "", text)


def _manifest_polish(path: Path, run_id: Optional[str]) -> Optional[tuple[int, int]]:
    """``(polished views, views)`` of a final manifest of this run (``run_id``, both None for a hand run), else None
    (no manifest, an earlier run's, no view that records its ``final`` image: ``polished`` or ``cycles``)."""
    try:
        manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(manifest, dict) or (manifest.get("run_id") or None) != (run_id or None):
        return None
    views = [v for v in manifest.get("views") or [] if isinstance(v, dict) and v.get("final") in ("polished", "cycles")]
    if not views:
        return None
    return sum(1 for v in views if v.get("final") == "polished"), len(views)


def run_polish(out_dir: Path) -> Optional[dict]:
    """Fix round after P4a (module docstring): ``{"polished": n, "views": m}`` over this run's final manifest of the
    project and of each alternative (``variants/<id>/final/final_manifest.json`` of the same run id), or None when the
    project's own manifest is missing, an earlier run's, or has no view (then the change list is not known)."""
    from wenart.report import final as F

    out_dir = Path(out_dir)
    run_id = this_run_id(out_dir)
    base = _manifest_polish(out_dir / F.FINAL_DIR / F.MANIFEST_NAME, run_id)
    if base is None:
        return None
    polished, views = base
    for vid in variant_folders(out_dir):
        got = _manifest_polish(out_dir / VARIANTS_DIR / vid / F.FINAL_DIR / F.MANIFEST_NAME, run_id)
        if got is not None:
            polished, views = polished + got[0], views + got[1]
    return {"polished": polished, "views": views}


def polish_note(polish: Optional[dict]) -> Optional[str]:
    """The line under section 2 that says whether the change list names AI polish (fix round after P4a)."""
    if not isinstance(polish, dict):
        return None
    n, m = int(polish.get("polished") or 0), int(polish.get("views") or 0)
    if n == 0:
        return (f"Changes made for these images: no view of this run was AI-retouched (0 of {m} views polished), so "
                f"the change \"{RETOUCH_CHANGE}\" of the catalogue's credit texts is left out below.")
    return f"Changes made for these images: {n} of {m} views were AI-retouched (the polish stage)."


def attribution_text(title: str, credits: list[dict], *, mode: str = "commercial") -> str:
    """The ``ATTRIBUTION.md`` text (Milestone 13, docs/milestone13.md §6, §13.2): the licence mode, then

    1. the tools and generators with their licences (``TOOLS_AND_GENERATORS``; the credits may carry ``kind:
       "run_model"`` rows for the models the final report recorded);
    2. the CC0 / CC BY assets (flag ``none``) with author, source, licence and changes, one line per model
       (docs/milestone8.md §2 format, with the M12 audit removal and its reasons) and per texture set / HDRI;
    3. the PoC-only assets (``POC_ONLY_FLAGS``) with the reason and the licence page; in ``commercial`` mode such
       an asset is a warning (the mode must not use it); a no-derivatives or unknown licence is listed as never
       usable;
    4. the dataset notices of the sources present (Objaverse ODC-By, ABO, GSO, generated, HSSD, Poly Haven).

    ``credits`` are ``project_credits`` (+ ``texture_credits`` + ``vegetation_credits``) or ``library_attribution``'s
    rows. Build round 2: a ``kind: "tool"`` row (the Sapling add-on of the site build, ``vegetation_credits``) is
    listed under section 1 with the trees it made; the HSSD notice comes from ``wenart.assets.hssd.DATASET``
    (``hssd_notice``); ambientCG textures and leaf atlases add ``AMBIENTCG_NOTICE`` to section 4.

    Fix round after P4a: a ``kind: "run_polish"`` row (``run_polish``: ``polished``, ``views``) with no polished
    view leaves "AI-retouched" out of the credit lines and notices (``without_retouch``) and says so under section 2
    (``polish_note``); without the row the texts stay as they are.
    """
    from wenart.furniture import catalog as CAT

    mode = CAT.check_mode(mode)
    models = [c for c in credits if c.get("kind", "model") == "model"]
    textures = [c for c in credits if c.get("kind") in ("texture", "hdri")]
    run_models = [c for c in credits if c.get("kind") == "run_model"]
    polish = next((c for c in reversed(credits) if c.get("kind") == "run_polish"), None)    # fix round after P4a
    tools = [c for c in credits if c.get("kind") == "tool"]
    sources = sorted({c.get("source") or "objaverse" for c in models},
                     key=lambda s: SOURCE_ORDER.index(s) if s in SOURCE_ORDER else len(SOURCE_ORDER))
    names = ", ".join(SOURCE_NAMES.get(s, s) for s in sources) or "no library model"
    mode_text = ("commercial: only commercial-safe assets (licence flag none) may be used"
                 if mode == "commercial" else
                 "relaxed (PoC, user OK of 12 Oct 2026): non-commercial, share-alike, research-only, regional and "
                 "tool_nc assets may be used and are listed in section 3; no-derivatives assets never")
    lines = ["# Attribution", "", f"{title} show 3D models from the furniture library ({names}). Credits "
             "(docs/milestone7.md §7.3, docs/milestone8.md §2, docs/milestone13.md §6):", "",
             f"Licence mode: {mode_text}.", "",
             "## 1. Tools and generators", ""]
    for t in TOOLS_AND_GENERATORS:
        lines.append(f"- {t['name']}: {t['licence']} ({t['url']}); {t['role']}")
    if run_models:
        lines += ["", "Models recorded by this run's final report (role: model @ revision, licence):", ""]
        lines += [f"- {m.get('role')}: {m.get('repo')} @ {str(m.get('revision') or '-')[:12]} "
                  f"({m.get('licence') or 'licence not recorded'})" for m in run_models]
    if tools:
        lines += ["", "Tools of the site build (GPL add-ons run as installed programs; their output is ours):", ""]
        for t in tools:
            pieces = ", ".join(f"{pid} ({ptype})" for pid, ptype in t.get("pieces") or [])
            lines.append(f"- {t['name']}: {t['licence']} ({t['url']}); {t['role']}"
                         + (f" (used for {pieces})" if pieces else ""))
    lines += ["", "## 2. CC0 / CC BY assets (author, source, licence, changes)", ""]
    safe = [c for c in models if _credit_flag(c) == "none"]
    if safe:
        lines += [_credit_line(c) + (f"; changes: {c['changes']}" if c.get("changes") and "changes:" not in
                                     str(c.get("credit")) else "") for c in safe]
    else:
        lines.append("No CC0 / CC BY library model in these images (parametric and module geometry is ours).")
    if textures:
        lines += [""] + [_credit_line(c) + (f"; changes: {c['changes']}" if c.get("changes") else "")
                         for c in textures]
    lines += ["", "## 3. PoC-only assets (not commercial-safe)", ""]
    flagged = [c for c in models + textures if _credit_flag(c) != "none" or c.get("logo_flag")]   # UL215: logos
    if not flagged:
        lines.append("None." + (" Commercial mode: every asset in these images is commercial-safe."
                                if mode == "commercial" else ""))
    else:
        if mode == "commercial":
            lines += [f"WARNING: {len(flagged)} flagged asset(s) in commercial mode. They must not be in a commercial "
                      "deliverable: re-run the fit in commercial mode (docs/milestone13.md §6).", ""]
        for c in flagged:
            flag = _credit_flag(c)
            reason = POC_FLAG_REASONS.get(flag) or ("never usable in any mode (no-derivatives or an unknown licence)"
                                                    if flag in ("no_derivatives", "unknown") else
                                                    f"licence flag {flag}")
            if c.get("logo_flag"):                    # UL215: a maker's logo or print (trademarks are not licensed)
                logo = f"a maker's logo or print on the model ({c.get('logo_reason') or 'logo_flag'})"
                reason = logo if flag == "none" else f"{reason}; {logo}"
            url = c.get("licence_url") or "licence page not recorded"
            if flag == "tool_nc":             # the limit comes from the export tool, not the model's own licence
                url = f"{CAT.TOOL_NC['licence_url']} (tool); model: {url}"
            lines.append(f"{_credit_line(c)}; PoC only: {reason}; licence: {url}")
    lines += ["", "## 4. Dataset notices", ""]
    notices = _notices(sources)
    if "hssd" in sources:
        notices.append(hssd_notice())
    if "3dwh" in sources:                             # 23 Oct 2026: the 3D Warehouse models (licences not reviewed)
        from wenart.assets import warehouse as WH
        notices.append(WH.notice())
    if "polyhaven" in sources or any(c.get("source") == "polyhaven" for c in textures):
        notices.append(POLYHAVEN_NOTICE)
    if any(c.get("source") == "ambientcg" for c in textures):
        notices.append(AMBIENTCG_NOTICE)
    if not notices:
        lines.append("None: no dataset asset in these images.")
    for text in notices:
        lines += [text, ""]
    note = polish_note(polish)
    if note is not None:                              # fix round after P4a: the run's own change list
        if int(polish.get("polished") or 0) == 0:
            lines = [without_retouch(line) for line in lines]
        at = lines.index("## 2. CC0 / CC BY assets (author, source, licence, changes)") + 2
        lines[at:at] = [note, ""]
    return "\n".join(lines)


def _has_image(folder: Path) -> bool:
    return folder.is_dir() and any(p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png")
                                   for p in folder.rglob("*"))


def _write_if_changed(path: Path, text: str) -> bool:
    try:
        if path.read_text(encoding="utf-8") == text:
            return False
    except OSError:
        pass
    path.write_text(text, encoding="utf-8")
    return True


def write_attributions(ref: ProjectRef) -> int:
    """``ATTRIBUTION.md`` into every image folder of the project's results (module docstring); files written.
    Milestone 13: the file carries the four sections in the project's licence mode and the run's model rows; a
    Milestone 13 run (``project.licence_mode`` in the building) gets it even without a library model."""
    credits = project_credits(ref.out_dir)
    building = read_building(ref.out_dir) or {}
    m13_run = isinstance(building.get("project"), dict) and bool(building["project"].get("licence_mode"))
    vegetation = vegetation_credits(ref.out_dir)         # build round 2: the site's trees, hedges and grass
    if not credits and not m13_run and not vegetation:
        return 0
    credits = credits + texture_credits(ref.out_dir) + vegetation
    credits += [dict(m, kind="run_model") for m in run_model_rows(ref.out_dir)]
    areas = ("final",) if ref.private else IMAGE_AREAS
    polish = run_polish(ref.out_dir)                      # fix round after P4a: the run's own change list
    if polish is not None:
        credits.append(dict(polish, kind="run_polish"))
    text = attribution_text(f"The images of project {ref.name}", credits, mode=project_licence_mode(ref.out_dir))
    n = 0
    for area in areas:
        folder = ref.results_area(area)
        if _has_image(folder):
            n += int(_write_if_changed(folder / ATTRIBUTION, text))
    return n


def library_catalog_path(library_dir: Path) -> Path:
    """The catalogue of a library folder: ``catalog_library.json`` (Milestone 8) when present, else the M7
    ``catalog_objaverse.json``."""
    library_dir = Path(library_dir)
    for name in (LIBRARY_CATALOG, OBJAVERSE_CATALOG):
        if (library_dir / name).is_file():
            return library_dir / name
    return library_dir / LIBRARY_CATALOG


def library_attribution(library_dir: Path, catalog: Optional[Path] = None) -> Optional[Path]:
    """``<library_dir>/ATTRIBUTION.md`` with the credit (and licence flag) of every model and decor model of
    ``catalog`` (default ``library_catalog_path``); None when the catalogue has no entry."""
    library_dir = Path(library_dir)
    path = Path(catalog) if catalog is not None else library_catalog_path(library_dir)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if isinstance(data, dict):                                 # objaverse.write_catalog's layout
        entries = list(data.get("entries") or []) + list(data.get("decor") or [])
    else:
        entries = data
    entries = [e for e in entries or [] if isinstance(e, dict)]
    if not entries:
        return None
    credits = []
    for e in sorted(entries, key=lambda e: str(e.get("id") or e.get("uid") or "")):
        row = {"credit": _credit(dict(e, asset_id=e.get("id"))), "pieces": [], "source": _source_of(e),
               "asset_id": str(e.get("id") or e.get("uid") or ""), "kind": "model", "removed": audit_removed(e)}
        row.update(_licence_fields(e))        # Milestone 13: licence_flag, commercial_safe, licence_url
        credits.append(row)
    target = library_dir / ATTRIBUTION
    library_dir.mkdir(parents=True, exist_ok=True)
    # A catalogue lists everything it holds: relaxed mode, so the flagged entries go to section 3 with their reason.
    _write_if_changed(target, attribution_text("The thumbnails and models of this library", credits, mode="relaxed"))
    return target


def library_files(library_dir: Path) -> list[Path]:
    """The files of a library work folder that go to ``$RESULTS/library`` (the prep job's copy): every survey file
    (``survey.json``, ``survey_abo.json``, ``survey_generated.json``), the thumbnails, judging sheets, requests
    and answers, ``accepted.json``, ``catalog_library.json``, the report, ``ATTRIBUTION.md`` and the generation plan
    and records; never a model file (``LIBRARY_SKIP_SUFFIXES``: the GLBs stay in the caches and
    ``<assets>/models/<source>/``), a generation input image (``LIBRARY_SKIP_GENERATE_SUFFIXES`` under
    ``generate/``), a symlink or a file over ``MAX_TEXT_BYTES``."""
    src = Path(library_dir)
    if not src.is_dir():
        return []
    out = []
    for f in sorted(src.rglob("*")):
        if not f.is_file() or f.is_symlink() or f.suffix.lower() in LIBRARY_SKIP_SUFFIXES:
            continue
        rel = f.relative_to(src)
        if rel.parts[0] == "generate" and f.suffix.lower() in LIBRARY_SKIP_GENERATE_SUFFIXES:
            continue
        if f.stat().st_size > MAX_TEXT_BYTES:
            continue
        out.append(f)
    return out


def _stamp(path: Path) -> None:
    """An empty file whose mtime is the volume's own time minus the overlap (polish.sh ``stamp``)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")
    t = path.stat().st_mtime - STAMP_OVERLAP_S
    os.utime(path, (t, t))


def copy_results(refs: Iterable[ProjectRef], since_stamp: Optional[Path] = None) -> dict:
    """Copy every project; ``{"public": n, "private": m, "full": bool}``. With ``since_stamp`` only the files
    changed since that stamp's time (all when it does not exist) and the stamp is renewed afterwards."""
    since = None
    nxt = None
    if since_stamp is not None:
        since_stamp = Path(since_stamp)
        if since_stamp.is_file():
            since = since_stamp.stat().st_mtime
        nxt = since_stamp.with_name(since_stamp.name + ".next")
        _stamp(nxt)                    # before the scan: files written during it go next time
    counts = {"public": 0, "private": 0, "full": since is None}
    for ref in refs:
        counts["private" if ref.private else "public"] += copy_project(ref, since)
    if nxt is not None:
        os.replace(nxt, since_stamp)
    return counts


@contextmanager
def copy_lock(path, wait_s: float = 120.0):
    """Hold the job's copy lock (``flock`` on ``path``, as ``full.sh``'s copy loop); no lock for None.
    ``TimeoutError`` when it stays busy for ``wait_s`` seconds."""
    if not path:
        yield
        return
    import fcntl
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as fh:
        give_up = time.monotonic() + float(wait_s)
        while True:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() > give_up:
                    raise TimeoutError(f"copy lock busy for {wait_s:.0f} s") from None
                time.sleep(1.0)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def summary_line(counts: dict) -> str:
    what = "full copy" if counts["full"] else "changed since the last copy"
    return f"copy: {counts['public']} public file(s), {counts['private']} private file(s) ({what})"

