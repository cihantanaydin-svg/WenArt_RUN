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
import json
import os
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
LIBRARY_SOURCES = ("objaverse", "abo", "generated", "gso", "hssd")
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
     "role": "recognition of plan symbols, layout proposals, decor, vision check"},
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
    count = _copy_tree(ref, out_dir, "", since)
    for vid in variant_folders(out_dir):
        count += _copy_tree(ref, out_dir / VARIANTS_DIR / vid, f"{VARIANTS_DIR}/{vid}", since)
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


def _copy_tree(ref: ProjectRef, out_dir: Path, prefix: str, since: Optional[float]) -> int:
    """The rules over one output folder: the project's (``prefix`` "") or an alternative's (``variants/<id>``)."""
    rules = PRIVATE_RULES if ref.private else PUBLIC_RULES
    count = 0
    for rule in rules:
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
                if how is None or (since is not None and path.stat().st_mtime <= since):
                    continue
                dst_dir.mkdir(parents=True, exist_ok=True)
                target = dst_dir / path.name
                if how == "copy":
                    shutil.copyfile(path, target)
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
    return count


# --------------------------------------------------------------------------
# ATTRIBUTION.md (docs/milestone7.md §7.3)
# --------------------------------------------------------------------------

def _source_of(asset: dict) -> str:
    """The library source of a fitted asset or a catalogue entry (``library`` of a fit asset, else ``source``)."""
    return str(asset.get("library") or asset.get("source") or "")


def _credit(asset: dict) -> str:
    """The credit line of a fitted library asset or catalogue entry (``attribution``; for an Objaverse one without
    it, the §7.3 line built from its fields)."""
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
    return {"licence": asset.get("licence") or asset.get("license"), "licence_flag": flag,
            "commercial_safe": flag == CAT.NO_FLAG, "licence_url": CAT.licence_url_of(asset)}


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
        if method == "sapling":
            tool_pieces.append((oid, part))               # the add-on (section 1); its leaf atlas is credited below
        if method in ("cards", "palm", "sapling"):
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
                "Dataset)", "ambientcg": "ambientCG"}
SOURCE_ORDER = ("abo", "gso", "objaverse", "generated", "hssd", "polyhaven", "ambientcg")


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
    reasons = [str(r) for r in audit.get("reasons") or [] if str(r).strip()]
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
    """
    from wenart.furniture import catalog as CAT

    mode = CAT.check_mode(mode)
    models = [c for c in credits if c.get("kind", "model") == "model"]
    textures = [c for c in credits if c.get("kind") in ("texture", "hdri")]
    run_models = [c for c in credits if c.get("kind") == "run_model"]
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
    flagged = [c for c in models + textures if _credit_flag(c) != "none"]
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
            url = c.get("licence_url") or "licence page not recorded"
            if flag == "tool_nc":             # the limit comes from the export tool, not the model's own licence
                url = f"{CAT.TOOL_NC['licence_url']} (tool); model: {url}"
            lines.append(f"{_credit_line(c)}; PoC only: {reason}; licence: {url}")
    lines += ["", "## 4. Dataset notices", ""]
    notices = _notices(sources)
    if "hssd" in sources:
        notices.append(hssd_notice())
    if "polyhaven" in sources or any(c.get("source") == "polyhaven" for c in textures):
        notices.append(POLYHAVEN_NOTICE)
    if any(c.get("source") == "ambientcg" for c in textures):
        notices.append(AMBIENTCG_NOTICE)
    if not notices:
        lines.append("None: no dataset asset in these images.")
    for text in notices:
        lines += [text, ""]
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

