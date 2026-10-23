"""Realism A/B preparation done by the orchestrator (docs/milestone6.md §6.3) and the Milestone 13 lever A/B.

What:
- ``prepare_m5`` (AB prepare part 2): writes ``out/ab/m5/`` from ``git show
  M5_LOOK_COMMIT:``: ``building_final.json`` (also copied to
  ``out/ab/building_m5.json``), ``scene_manifest.json``,
  ``render_manifest.json`` and the ``<cam>_preview.jpg`` of every M5 camera
  (the committed M5 previews: 1920 x 1080, JPEG quality 85). These are the A
  images of the ``m5_vs_m6`` set and the M5 building the B images are
  rendered from (with the M6 look and the M5 cameras).
- ``cameras_check`` (after the A/B render): every camera of the A/B scene is
  compared with the M5 scene manifest (position and target within 1 mm) and
  must have been rendered; ``out/ab/cameras_check.json`` =
  ``{"kept": [...], "dropped": [{"cam", "reason"}]}``. Only kept cameras are
  paired (``vision_check realism-pairs`` reads this file, never git).
- Milestone 13 (docs/milestone13.md §13.2 ab.py, §13.3, decision D6: the committed Milestone 11 runs of real02
  and real03 are the baseline, the committed Milestone 12 run of real04):
  ``prepare_m13(project, project_out, commit)`` writes ``out/ab/m13/`` with the baseline's ``scene_manifest.json``
  (its camera records are what ``build.py --cameras-from`` replays), ``render_manifest.json``, ``building_final.json``,
  the ``<cam>_preview.jpg`` of every camera and a ``style.json`` taken from the scene manifest's ``style_profile``
  (the style the baseline was built with). ``commit`` is a sha for ``git show`` (``M13_BASELINE_COMMITS``) or a
  directory (the pod reads the files of the working tree, which equal the baseline commit's: checked by sha256 on
  15 Oct 2026); a project without camera records (real04: no scene manifest was committed) returns an empty
  camera set with a ``reason``, and its build searches its cameras. ``M13_AB_VIEWS`` are the 8 + 8 fixed interior
  views of the lever A/B (``scripts/jobs/levers_ab.sh``: living, kitchen, bedroom, bath, hall of real02; living,
  bedroom, bath, hall of real03, which has no kitchen), chosen from the committed scene manifests with the
  Milestone 11 exposure of each view (the dark daylight rooms and the lamp-lit rooms both in the set).
  ``lever_sheet`` / ``lever_sheets`` write one contact sheet per view (the variants side by side, PIL) and
  ``lever_summary`` the seconds, VRAM, EV and ``lighting_dark`` per view and variant into ``summary.json`` /
  ``summary.md`` of ``results/ab_m13/``. The variant names are ``lighting.LIGHT_VARIANTS`` (round 3: ``m11`` =
  the Milestone 11 look, ``base`` = the production defaults); a variant folder that is missing is a "not rendered"
  row and a grey tile, so an older results folder (P1: no ``m11`` folder, ``base`` = the Milestone 11 look) still
  summarises and sheets.
- Pod P6a (22 Oct 2026, the user's OK; the interior sky A/B, ``scripts/jobs/m13_p6.sh``): ``M13_SKY_AB_VIEWS`` are
  6 fixed real04 interior views with windows that showed P5's dark sky over a near-white ground band and the green
  daylight, ``M13_SKY_AB_VARIANTS`` the levels (``base`` and ``lighting.SKY_VARIANTS``). real04's cameras are
  searched, so ``resolve_views`` checks the names against the scene manifest the A/B replays (the pod's own run):
  a name it lacks is replaced by the first other camera of the same room, else dropped, each with the reason.
  ``prepare_m13(..., run_dir=)`` prepares from a project's run output (``outputs/<p>``: its
  ``building_final.json`` and ``style.json``, ``scene/scene_manifest.json`` with the run's cameras,
  ``renders/`` with the final previews), never from the committed baseline. ``view_set`` picks the set
  (``AB_VIEW_SETS``: ``levers`` = ``M13_AB_VIEWS``, the default, ``sky``) in the CLI (``m13-views``, and the
  ``--view-set`` / ``--scene`` options of ``m13-prepare``, ``m13-sheets``, ``m13-summary``); every default stays the
  lever A/B's.
- Fix round after P6a (22-23 Oct 2026; the user's decision of 22 Oct 2026, "Windows only +3.5"): the view set
  ``skywin`` (``M13_SKYWIN_AB_VIEWS``: five real02 views with windows from P4a's run and one rig-lit hall; real04's
  six sky views and its rig-lit hall) for the A/B of the windows-only sky (``M13_SKYWIN_AB_VARIANTS``: ``base``,
  ``skywin35``, ``sky35``; pod P6c, ``m13_p6.sh`` with ``P6_SKY_PROJECT=real02 P6_SKY_VIEW_SET=skywin``). The summary
  rows carry ``sky_rays`` and ``world_strength_camera`` (what the camera sees through the panes at a windows-only
  level); the sky table shows it beside the room's world strength.

Why: the A/B compares the same camera rendered two ways; a camera that moved
(or was not rendered) would compare different pictures.

How: ``prepare_m5`` runs ``git show`` itself (it is started by the
orchestrator as ``python -m wenart.run ab-m5`` through the one runner);
``cameras_check`` is pure. ``python -m wenart.run.ab m13-prepare | m13-sheets | m13-summary`` is the CLI of the
Milestone 13 parts (the job script calls it; ``wenart/run/__main__.py`` is the lead's file).
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable, Optional

from wenart.run.stages import M5_LOOK_COMMIT
from wenart.run.state import REPO_ROOT, write_json

CAMERA_TOLERANCE_M = 0.001


def git_show(commit: str, path: str, repo_root: Path = REPO_ROOT) -> bytes:
    """The bytes of ``<commit>:<path>`` (``git show``); ``FileNotFoundError`` when git has no such file."""
    proc = subprocess.run(["git", "-C", str(repo_root), "show", f"{commit}:{path}"], capture_output=True)
    if proc.returncode != 0:
        raise FileNotFoundError(f"{commit[:12]}:{path}: {proc.stderr.decode('utf-8', 'replace').strip()}")
    return proc.stdout


def prepare_m5(project: str, project_out: Path, commit: str = M5_LOOK_COMMIT, repo_root: Path = REPO_ROOT,
               show: Optional[Callable[[str, str], bytes]] = None) -> dict:
    """Write ``<project_out>/ab/m5/`` and ``ab/building_m5.json`` from ``commit`` (see the module docstring)."""
    show = show or (lambda c, p: git_show(c, p, repo_root))
    out = Path(project_out) / "ab" / "m5"
    out.mkdir(parents=True, exist_ok=True)
    building = show(commit, f"results/furniture/{project}/building_final.json")
    scene = show(commit, f"results/renders/{project}/scene_manifest.json")
    render = show(commit, f"results/renders/{project}/render_manifest.json")
    (out / "building_final.json").write_bytes(building)
    (out / "scene_manifest.json").write_bytes(scene)
    (out / "render_manifest.json").write_bytes(render)
    shutil.copyfile(out / "building_final.json", Path(project_out) / "ab" / "building_m5.json")
    cams = [c["name"] for c in json.loads(scene.decode("utf-8")).get("cameras") or []]
    previews, missing = 0, []
    for cam in cams:
        try:
            data = show(commit, f"results/renders/{project}/{cam}_preview.jpg")
        except FileNotFoundError:
            missing.append(cam)
            continue
        (out / f"{cam}_preview.jpg").write_bytes(data)
        previews += 1
    return {"project": project, "commit": commit, "cameras": len(cams), "previews": previews, "missing": missing}


def _close(a, b, tol: float) -> bool:
    if not isinstance(a, (list, tuple)) or not isinstance(b, (list, tuple)) or len(a) != len(b):
        return False
    return math.dist([float(x) for x in a], [float(x) for x in b]) <= tol + 1e-9


def cameras_check(m5_scene: dict, ab_scene: dict, ab_render: Optional[dict] = None,
                  tol_m: float = CAMERA_TOLERANCE_M) -> dict:
    """Kept and dropped cameras of the A/B (see the module docstring)."""
    m5 = {c["name"]: c for c in m5_scene.get("cameras") or []}
    ab = {c["name"]: c for c in ab_scene.get("cameras") or []}
    rendered = None
    if ab_render is not None:
        rendered = {r.get("camera") for r in ab_render.get("renders") or [] if r.get("preview")}
    kept, dropped = [], []
    for name in sorted(set(m5) | set(ab)):
        if name not in ab:
            dropped.append({"cam": name, "reason": "not in the A/B scene"})
        elif name not in m5:
            dropped.append({"cam": name, "reason": "not an M5 camera"})
        elif not _close(m5[name].get("position"), ab[name].get("position"), tol_m):
            dropped.append({"cam": name, "reason": f"position differs from M5 by more than {tol_m * 1000:.0f} mm"})
        elif not _close(m5[name].get("target"), ab[name].get("target"), tol_m):
            dropped.append({"cam": name, "reason": f"target differs from M5 by more than {tol_m * 1000:.0f} mm"})
        elif rendered is not None and name not in rendered:
            dropped.append({"cam": name, "reason": "not rendered in the A/B render"})
        else:
            kept.append(name)
    return {"schema_version": "0.1", "kind": "cameras_check", "tolerance_m": tol_m, "kept": kept, "dropped": dropped}


def write_cameras_check(project_out: Path) -> dict:
    """``out/ab/cameras_check.json`` from ``ab/m5/scene_manifest.json``, ``ab/scene/scene_manifest.json`` and
    ``ab/renders/render_manifest.json``."""
    ab = Path(project_out) / "ab"
    m5 = json.loads((ab / "m5" / "scene_manifest.json").read_text(encoding="utf-8"))
    scene = json.loads((ab / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    render_path = ab / "renders" / "render_manifest.json"
    render = json.loads(render_path.read_text(encoding="utf-8")) if render_path.is_file() else {"renders": []}
    result = cameras_check(m5, scene, render)
    write_json(ab / "cameras_check.json", result)
    return result


def m5_cameras(project_out: Path) -> list[str]:
    """The camera names of ``out/ab/m5/scene_manifest.json`` in manifest order."""
    path = Path(project_out) / "ab" / "m5" / "scene_manifest.json"
    try:
        return [c["name"] for c in json.loads(path.read_text(encoding="utf-8")).get("cameras") or []]
    except (OSError, ValueError, KeyError):
        return []


# --------------------------------------------------------------------------
# Milestone 13 (docs/milestone13.md §12 D6, §13.2, §13.3): the baseline runs and the lever A/B
# --------------------------------------------------------------------------

# The committed baseline runs (D6, 12 Oct 2026): real02 and real03 = the Milestone 11 run (results/renders/<p>/
# scene_manifest.json carries its cameras), real04 = the Milestone 12 run (no camera records committed).
M13_BASELINE_COMMITS = {"real02": "93aff07ff7ac6c2bf9c1c5c1d33298398fce9bc5",
                        "real03": "93aff07ff7ac6c2bf9c1c5c1d33298398fce9bc5",
                        "real04": "eddde01fa626e9af50e21c68bdd05c124bcc3c66"}
M13_DIR = "ab/m13"
M13_FILES = ("scene_manifest.json", "render_manifest.json")
# The 8 + 8 fixed interior views of the lever A/B (scripts/jobs/levers_ab.sh), from the committed Milestone 11
# scene manifests: the room type and the Milestone 11 exposure (results/final/<p>/final_manifest.json views[].exposure
# .ev) of each view, so the set holds the dark daylight rooms (EV +6..+8) and the lamp-lit rooms (EV about -0.5).
# real03 has no kitchen (its rooms: living, bedroom, bathroom, hall, stair), so it gives two halls and two baths.
M13_AB_VIEWS: dict[str, list[dict]] = {
    "real02": [
        {"camera": "cam_r_L-1_salon_1", "room_type": "living", "m11_ev": 4.17},
        {"camera": "cam_r_L-1_salon_2", "room_type": "living", "m11_ev": 3.67},
        {"camera": "cam_r_L-1_mutfak_1", "room_type": "kitchen", "m11_ev": 8.0},
        {"camera": "cam_r_L-1_mutfak_2", "room_type": "kitchen", "m11_ev": 8.0},
        {"camera": "cam_r_L0_yatak_odasi_1", "room_type": "bedroom", "m11_ev": 7.17},
        {"camera": "cam_r_L0_e_yatak_odasi_1", "room_type": "bedroom", "m11_ev": 6.17},
        {"camera": "cam_r_L0_e_banyo_1", "room_type": "bathroom", "m11_ev": -0.5},
        {"camera": "cam_r_L0_koridor_1", "room_type": "hall", "m11_ev": 0.67},
    ],
    "real03": [
        {"camera": "cam_r_L0_yasama_1", "room_type": "living", "m11_ev": 4.0},
        {"camera": "cam_r_L0_yasama_6_1", "room_type": "living", "m11_ev": 5.83},
        {"camera": "cam_r_L0_ebeveyn_odasi_1", "room_type": "bedroom", "m11_ev": 4.5},
        {"camera": "cam_r_L0_ebeveyn_odasi_4_1", "room_type": "bedroom", "m11_ev": 8.0},
        {"camera": "cam_r_L0_banyo_1", "room_type": "bathroom", "m11_ev": -0.5},
        {"camera": "cam_r_L0_banyo_4_1", "room_type": "bathroom", "m11_ev": -0.5},
        {"camera": "cam_r_L0_giris_holu_1", "room_type": "hall", "m11_ev": 7.83},
        {"camera": "cam_r_L0_kat_holu_1", "room_type": "hall", "m11_ev": -0.33},
    ],
}
# = lighting.LIGHT_VARIANTS (pinned equal in tests/test_m13_light.py). Round 3 (docs/milestone13.md §14.3): ``m11``
# is the Milestone 11 look (the "before"), ``base`` the production defaults (sun 1000 W/m², EV cap, rig, shell);
# the single levers keep their P1 meaning (the Milestone 11 look plus that lever), so a P1 sheet and a round-3
# sheet of the same name compare.
M13_AB_VARIANTS = ("m11", "base", "sun100", "sun300", "sun1000", "evcap", "rig", "shell", "all")
NO_CAMERA_RECORDS = ("no scene_manifest.json with camera records in the baseline (real04: the Milestone 12 run "
                     "committed none); the build searches its cameras and the before/after compares by camera name "
                     "and room")


# Pod P6a (22 Oct 2026, the user's OK): the interior sky A/B of real04. Six interior views with windows (or glazed
# doors) from P5's run (runs/20261017-224848-full/results/renders/real04/render_manifest.json): the window pull k, the
# panes before it (clip share, median, p90) and the daylight green ratio G/sqrt(RB) of the bpy 5.2.2 shim of real04
# at P5's anchor (tests/test_m13_light.py, test_fixround_p5_the_view_takes_the_tint_of_its_own_daylight; the anchor's
# 1.002). The dark sky over a near-white ground band shows in yatak_odasi_1, yatak_odasi_3, salon_1 / _2 and oyun_1;
# the green walls in the L0 bedrooms; oyun_1 (L1, over the roof, little lawn) is the control.
M13_SKY_AB_VIEWS: dict[str, list[dict]] = {
    "real04": [
        {"camera": "cam_r_L0_yatak_odasi_1", "room_id": "r_L0_yatak_odasi", "room_type": "bedroom",
         "p5": "pull k3, panes 28.5 % clipped before it (median 0.876, p90 0.999); daylight green 1.402"},
        {"camera": "cam_r_L0_yatak_odasi_3", "room_id": "r_L0_yatak_odasi", "room_type": "bedroom",
         "p5": "pull k2, panes 6.1 % clipped before it (median 0.825, p90 0.998); daylight green 1.348"},
        {"camera": "cam_r_L0_e_yatak_odasi_1", "room_id": "r_L0_e_yatak_odasi", "room_type": "bedroom",
         "p5": "pull k1 (median 0.750, p90 0.781), glazed doors at the frame's edge; daylight green 1.321"},
        {"camera": "cam_r_L-1_salon_1", "room_id": "r_L-1_salon", "room_type": "living",
         "p5": "pull k3, near-white panes before it (median 0.996, p90 0.997); daylight green 1.178"},
        {"camera": "cam_r_L-1_salon_2", "room_id": "r_L-1_salon", "room_type": "living",
         "p5": "pull k3, near-white panes before it (median 0.979, p90 0.994)"},
        {"camera": "cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1", "room_id": "r_L1_oyun_aktivite_ve_dinlenme_odasi",
         "room_type": "other", "p5": "pull k1 (median 0.722, p90 0.959); daylight green 1.022 (the control)"},
    ],
}
# The sky levels of the A/B (lighting.SKY_VARIANTS, pinned equal in tests/test_m13_sky_ab.py): ``base`` = production
# (the interior world as built), then +2, +3.5 and +5.2 stops.
M13_SKY_AB_VARIANTS = ("base", "sky2", "sky35", "sky52")
# Fix round after P6a (22-23 Oct 2026; the user's decision of 22 Oct 2026, "Windows only +3.5", needs one short A/B on
# pod P6c before it becomes the default): the windows-only sky (lighting.SKY_WINDOW_VARIANTS, ``skywin35``) against
# production and the whole-world sky35. real02 replays its Milestone 11 cameras, so the names are stable: five interior
# views with windows from P4a's run (runs/20261017-072801-full/results/renders/real02/: the window pull and the panes
# before it, render_manifest.json; the windows in view, scene_manifest.json) and one rig-lit hall that sees a glazed
# door (verify:sky_ab:0: the orange check's margin of the halls; the room light must not move). real04: P6a's six sky
# views and its rig-lit hall (cam_r_L-1_koridor_2_1, the tightest orange margin of P5), for a later re-check.
M13_SKYWIN_AB_VIEWS: dict[str, list[dict]] = {
    "real02": [
        {"camera": "cam_r_L-1_salon_1", "room_id": "r_L-1_salon", "room_type": "living",
         "p4a": "win_L-1_001; pull k1, panes p50 0.883 / p90 0.891 before it (241,858 pane px)"},
        {"camera": "cam_r_L-1_mutfak_1", "room_id": "r_L-1_mutfak", "room_type": "kitchen",
         "p4a": "win_L-1_003; pull k2, panes 34 % clipped before it (p50 0.850, p90 0.997); rig share 0.79"},
        {"camera": "cam_r_L0_yatak_odasi_1", "room_id": "r_L0_yatak_odasi", "room_type": "bedroom",
         "p4a": "win_L0_001; pull k1, panes p50 0.851 / p90 0.893 before it (138,609 pane px)"},
        {"camera": "cam_r_L0_e_yatak_odasi_3", "room_id": "r_L0_e_yatak_odasi", "room_type": "bedroom",
         "p4a": "win_L0_002; pull k1, panes p50 0.836 / p90 0.879 before it (167,240 pane px)"},
        {"camera": "cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1", "room_id": "r_L1_oyun_aktivite_ve_dinlenme_odasi",
         "room_type": "other",
         "p4a": "d_L1_001, win_L1_001 under the roof; pull k3 (p50 0.922, p90 0.971); the control"},
        {"camera": "cam_r_L-1_koridor_2_1", "room_id": "r_L-1_koridor_2", "room_type": "hall",
         "p4a": "the rig-lit hall (rig share 0.90) seeing the glazed door d_L-1_003 (46,739 pane px); its room light "
                "must not move"},
    ],
    "real04": M13_SKY_AB_VIEWS["real04"] + [
        {"camera": "cam_r_L-1_koridor_2_1", "room_id": "r_L-1_koridor_2", "room_type": "hall",
         "p5": "the rig-lit hall with the tightest orange margin (wall R/B 1.634 against 1.665, verify:sky_ab:0)"},
    ],
}
# The levels of the windows-only A/B: production, the windows-only +3.5 stops and the whole-world +3.5 stops.
M13_SKYWIN_AB_VARIANTS = ("base", "skywin35", "sky35")
AB_VIEW_SETS = {"levers": M13_AB_VIEWS, "sky": M13_SKY_AB_VIEWS, "skywin": M13_SKYWIN_AB_VIEWS}


def m13_views(project: str) -> list[str]:
    """The camera names of the lever A/B of ``project`` (``M13_AB_VIEWS``; ``[]`` for another project)."""
    return [v["camera"] for v in M13_AB_VIEWS.get(project, [])]


def view_set_of(name: Optional[str]) -> dict[str, list[dict]]:
    """The views table of a view set (``AB_VIEW_SETS``; None or "" = ``levers``); an unknown name raises ValueError."""
    key = name or "levers"
    if key not in AB_VIEW_SETS:
        raise ValueError(f"unknown view set {name!r}; one of {sorted(AB_VIEW_SETS)}")
    return AB_VIEW_SETS[key]


def _scene_dict(scene) -> Optional[dict]:
    """A scene manifest (a dict, or a path to one; None when absent or unreadable)."""
    if scene is None or isinstance(scene, dict):
        return scene
    path = Path(scene)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def resolve_views(project: str, view_set: Optional[str] = "levers", scene=None) -> dict:
    """The views of ``project`` in ``view_set`` checked against ``scene`` (a scene manifest dict or path, the one
    the A/B replays; pure apart from reading it): ``{"views": [names], "replaced": [{"wanted", "used", "reason"}],
    "dropped": [{"wanted", "reason"}]}``. Without a scene every configured name is kept (the lever A/B's committed
    baselines). A name the scene lacks is replaced by the first camera record of the same ``room_id`` (manifest
    order) not already in the list, else dropped."""
    wanted = view_set_of(view_set).get(project, [])
    data = _scene_dict(scene)
    if data is None:
        return {"views": [v["camera"] for v in wanted], "replaced": [], "dropped": []}
    records = [c for c in data.get("cameras") or [] if isinstance(c, dict) and c.get("name")]
    names = {str(c["name"]) for c in records}
    views, replaced, dropped = [], [], []
    for v in wanted:
        cam = v["camera"]
        if cam in names and cam not in views:
            views.append(cam)
            continue
        room = v.get("room_id")
        alt = next((str(c["name"]) for c in records if room and c.get("room_id") == room
                    and str(c["name"]) not in views and str(c["name"]) not in {w["camera"] for w in wanted}), None)
        if alt is not None:
            views.append(alt)
            replaced.append({"wanted": cam, "used": alt, "reason": f"no camera {cam} in the scene manifest: the "
                                                                   f"first other camera of {room}"})
        else:
            dropped.append({"wanted": cam, "reason": f"no camera {cam} and no other camera of "
                                                     f"{room or 'its room'} in the scene manifest"})
    return {"views": views, "replaced": replaced, "dropped": dropped}


def ab_views(project: str, view_set: Optional[str] = "levers", scene=None) -> list[str]:
    """The camera names of ``resolve_views`` (the lever A/B without a scene: ``m13_views``)."""
    return resolve_views(project, view_set, scene)["views"]


RUN_SUBDIRS = ("scene", "renders", ".")     # where prepare_m13(run_dir=) looks, in this order


def prepare_m13(project: str, project_out: Path, commit: Optional[str] = None, repo_root: Path = REPO_ROOT,
                show: Optional[Callable[[str, str], bytes]] = None, *, run_dir: Optional[Path] = None,
                view_set: Optional[str] = "levers") -> dict:
    """Write ``<project_out>/ab/m13/`` from the baseline run of ``project`` (module docstring): ``commit`` a git
    sha (default ``M13_BASELINE_COMMITS[project]``) read with ``show(commit, path)`` (``git_show``), or a directory
    holding the baseline files (``scene_manifest.json``, ``render_manifest.json``, ``<cam>_preview.jpg``,
    ``building_final.json`` or the repo's ``results/furniture/<p>/building_final.json``). Returns ``{"project",
    "commit", "source", "out", "files", "cameras", "camera_records", "previews", "missing", "reason", "views",
    "views_missing"}``; a baseline without camera records gives ``cameras 0`` and the ``reason``.

    Pod P6a: ``run_dir`` (a project's run output, ``outputs/<p>``) instead of ``commit``: the files are looked up in
    its ``scene/``, ``renders/`` and top folders (``RUN_SUBDIRS``), the building only as its own
    ``building_final.json`` (never the committed one: the A/B must build what the run built) and ``style.json`` is
    the run's file when it has one (else the scene manifest's ``style_profile``). ``view_set`` (``AB_VIEW_SETS``)
    names the views checked against the prepared cameras (``resolve_views``: ``views``, ``views_missing``,
    ``views_replaced``)."""
    from wenart.blender.cameras import replay_cameras

    view_set_of(view_set)                                   # an unknown set fails before anything is written
    run_dir = Path(run_dir) if run_dir is not None else None
    if run_dir is not None and not run_dir.is_dir():
        raise ValueError(f"{project}: run output {run_dir} is no directory")
    out = Path(project_out) / M13_DIR
    out.mkdir(parents=True, exist_ok=True)
    source_dir = Path(commit) if run_dir is None and commit and Path(commit).is_dir() else None
    if run_dir is None and source_dir is None and commit is None:
        if project not in M13_BASELINE_COMMITS:
            raise ValueError(f"{project}: no baseline commit in M13_BASELINE_COMMITS and no directory given")
        commit = M13_BASELINE_COMMITS[project]
    show = show or (lambda c, p: git_show(c, p, repo_root))

    def read(rel: str) -> Optional[bytes]:
        """The bytes of a baseline file (``rel`` as under results/), None when absent."""
        if run_dir is not None:
            name = Path(rel).name
            folders = [run_dir] if rel.startswith("results/furniture/") else [run_dir / d for d in RUN_SUBDIRS]
            for folder in folders:
                if (folder / name).is_file():
                    return (folder / name).read_bytes()
            return None
        if source_dir is not None:
            name = Path(rel).name
            candidates = [source_dir / name]
            if rel.startswith("results/furniture/"):
                candidates.append(Path(repo_root) / rel)
            for p in candidates:
                if p.is_file():
                    return p.read_bytes()
            return None
        try:
            return show(commit, rel)
        except FileNotFoundError:
            return None

    files: list[str] = []
    scene_bytes = read(f"results/renders/{project}/scene_manifest.json")
    for name in M13_FILES + ("build_brief.json",):
        data = scene_bytes if name == "scene_manifest.json" else read(f"results/renders/{project}/{name}")
        if data is not None:
            (out / name).write_bytes(data)
            files.append(name)
    building = read(f"results/furniture/{project}/building_final.json")
    if building is not None:
        (out / "building_final.json").write_bytes(building)
        files.append("building_final.json")
    configured = [v["camera"] for v in view_set_of(view_set).get(project, [])]
    if run_dir is not None:
        source = f"run {run_dir}"
    else:
        source = str(source_dir) if source_dir is not None else f"git {str(commit)[:12]}"
    info = {"project": project, "commit": None if source_dir is not None or run_dir is not None else commit,
            "source": source, "out": str(out),
            "files": files, "cameras": 0, "camera_records": False, "previews": 0, "missing": [], "reason": None,
            "views": configured, "views_missing": list(configured)}
    if view_set not in (None, "", "levers"):
        info["view_set"] = view_set
    if scene_bytes is None:
        info["reason"] = NO_CAMERA_RECORDS
        return info
    scene = json.loads(scene_bytes.decode("utf-8"))
    style = scene.get("style_profile")
    run_style = run_dir / "style.json" if run_dir is not None else None
    if run_style is not None and run_style.is_file():
        (out / "style.json").write_bytes(run_style.read_bytes())       # the file the run's build read
        files.append("style.json")
    elif isinstance(style, dict):
        (out / "style.json").write_text(json.dumps(style, indent=1, ensure_ascii=False), encoding="utf-8")
        files.append("style.json")
    plans = replay_cameras(scene)["plans"]
    names = [p["name"] for p in plans]
    info.update(cameras=len(names), camera_records=bool(names))
    if not names:
        info["reason"] = NO_CAMERA_RECORDS
        return info
    for cam in names:
        data = read(f"results/renders/{project}/{cam}_preview.jpg")
        if data is None:
            info["missing"].append(cam)
            continue
        (out / f"{cam}_preview.jpg").write_bytes(data)
        info["previews"] += 1
    if view_set in (None, "", "levers"):
        info["views_missing"] = [v for v in m13_views(project) if v not in names]
    else:
        # the sky A/B: the views resolved against the replayed cameras (a missing name -> its room's next camera)
        resolved = resolve_views(project, view_set, {"cameras": [p for p in plans]})
        info.update(views=resolved["views"], views_missing=[d["wanted"] for d in resolved["dropped"]],
                    views_replaced=resolved["replaced"])
    return info


def lever_sheet(view: str, tiles: list, out_path: Path, tile_width: int = 640, label_height: int = 28) -> Path:
    """One contact sheet of a view: ``tiles`` = ``[(label, image path or None)]`` side by side (two rows from
    five tiles on), ``tile_width`` px each, the label under each tile; a missing image is a grey tile that says
    so (PIL, no Blender)."""
    from PIL import Image, ImageDraw

    cols = min(len(tiles), 4) if len(tiles) > 4 else max(1, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sized = []
    for label, path in tiles:
        img = None
        if path and Path(path).is_file():
            with Image.open(path) as im:
                img = im.convert("RGB")
                img = img.resize((tile_width, max(1, round(img.height * tile_width / img.width))), Image.Resampling.LANCZOS)
        sized.append((label, img))
    tile_h = max([t.height for _, t in sized if t is not None] or [round(tile_width * 9 / 16)])
    gap = 4
    cell_h = tile_h + label_height
    sheet = Image.new("RGB", (cols * tile_width + (cols + 1) * gap, rows * cell_h + (rows + 1) * gap + label_height),
                      (32, 32, 32))
    draw = ImageDraw.Draw(sheet)
    draw.text((gap, 6), view, fill=(230, 230, 230))
    for i, (label, img) in enumerate(sized):
        x = gap + (i % cols) * (tile_width + gap)
        y = label_height + gap + (i // cols) * (cell_h + gap)
        if img is None:
            draw.rectangle([x, y, x + tile_width, y + tile_h], fill=(70, 70, 70))
            draw.text((x + 8, y + tile_h // 2), "not rendered", fill=(220, 220, 220))
        else:
            sheet.paste(img, (x, y))
        draw.text((x + 4, y + tile_h + 6), label, fill=(230, 230, 230))
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path, "JPEG", quality=80)
    return out_path


def lever_sheets(results_dir: Path, project: str, variants=M13_AB_VARIANTS, views: Optional[list] = None,
                 baseline_dir: Optional[Path] = None, baseline_label: str = "M11 baseline") -> list[Path]:
    """One sheet per view of the lever A/B: ``results_dir/<variant>/<project>/<cam>_preview.jpg`` of every variant,
    the baseline preview (``baseline_dir/<cam>_preview.jpg``, the committed Milestone 11 render; pod P6a: the run's
    own final render, ``baseline_label``) first; written to ``results_dir/sheets/<project>_<cam>.jpg``."""
    results_dir = Path(results_dir)
    out = []
    for cam in views or m13_views(project):
        tiles = []
        if baseline_dir is not None:
            tiles.append((baseline_label, Path(baseline_dir) / f"{cam}_preview.jpg"))
        for v in variants:
            tiles.append((v, results_dir / v / project / f"{cam}_preview.jpg"))
        out.append(lever_sheet(f"{project} {cam}", tiles, results_dir / "sheets" / f"{project}_{cam}.jpg"))
    return out


def _world_record(folder: Path) -> Optional[dict]:
    """The interior world record of a variant (``lighting.json`` the job copies from the scene manifest:
    ``lighting.world``), None when absent."""
    try:
        data = json.loads((Path(folder) / "lighting.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    world = ((data or {}).get("lighting") or {}).get("world") if isinstance(data, dict) else None
    return world if isinstance(world, dict) else None


def lever_summary(results_dir: Path, projects=("real02", "real03"), variants=M13_AB_VARIANTS,
                  views: Optional[dict] = None, view_set: Optional[str] = "levers") -> dict:
    """The numbers of the lever A/B per project, variant and view from ``results_dir/<variant>/<project>/
    render_manifest.json`` (seconds, samples, EV, the metered EV, at_limit, lighting_dark, incident p50, the white
    balance, ``vram_mib`` of the entry) and ``vram.json`` (the job's nvidia-smi peak of the variant); written to
    ``results_dir/summary.json`` and ``summary.md``.

    Pod P6a: ``views`` ({project: [cameras]}, default ``m13_views``) are the views of a run's resolved set
    (``resolve_views``); every row also carries the window pull (``pull_k``, the panes after it), the view's
    daylight tint (``wb_day_green``, ``wb_view_tint_gain``), the project white point's kelvin and the interior
    world's strength of the variant (``world_strength``, ``sky_stops``: ``lighting.json``), so the sky levels
    compare in numbers; a ``view_set`` other than ``levers`` is named in the summary."""
    results_dir = Path(results_dir)
    rows = []
    for project in projects:
        project_views = list((views or {}).get(project) or []) or m13_views(project)
        for v in variants:
            folder = results_dir / v / project
            manifest = folder / "render_manifest.json"
            if not manifest.is_file():
                rows.append({"project": project, "variant": v, "camera": None, "status": "not rendered"})
                continue
            data = json.loads(manifest.read_text(encoding="utf-8"))
            peak = None
            if (folder / "vram.json").is_file():
                try:
                    peak = json.loads((folder / "vram.json").read_text(encoding="utf-8")).get("peak_mib")
                except ValueError:
                    peak = None
            world = _world_record(folder) or {}
            wb_project = data.get("white_balance_project") if isinstance(data.get("white_balance_project"), dict) \
                else {}
            entries = {r.get("camera"): r for r in data.get("renders") or []}
            for cam in project_views:
                r = entries.get(cam)
                if r is None:
                    rows.append({"project": project, "variant": v, "camera": cam, "status": "not rendered",
                                 "vram_peak_mib": peak})
                    continue
                ex = r.get("exposure") or {}
                dark = ex.get("lighting_dark") or r.get("lighting_dark")
                rows.append({"project": project, "variant": v, "camera": cam, "status": "rendered",
                             "seconds": r.get("seconds"), "samples": r.get("samples"), "ev": ex.get("ev"),
                             "ev_raw": ex.get("ev_raw"), "at_limit": ex.get("at_limit"),
                             "lighting_dark": None if not dark else dark.get("severity"),
                             "incident_p50": ex.get("incident_p50"), "wb_temperature": ex.get("wb_temperature"),
                             "wb_mode": ex.get("wb_mode"), "vram_mib": r.get("vram_mib"), "vram_peak_mib": peak,
                             "light_variant": (data.get("light_variant") or {}).get("build"),
                             "exposure_limits": data.get("exposure_limits"),
                             # pod P6a: the window band, the green daylight and the interior world in numbers
                             "pull_k": (r.get("window_pull") or {}).get("k"),
                             "pane_median_after": (r.get("window_pull") or {}).get("pane_median_after"),
                             "pane_p90_after": (r.get("window_pull") or {}).get("pane_p90_after"),
                             "wb_day_green": ex.get("wb_day_green"), "wb_view_tint_gain": ex.get("wb_view_tint_gain"),
                             "wb_project_k": wb_project.get("kelvin"), "world_strength": world.get("strength"),
                             "sky_stops": world.get("sky_stops", 0.0 if world else None),
                             # fix round after P6a: which rays see the gain (camera_paths: skywin35) and what the
                             # camera sees through the panes then
                             "sky_rays": world.get("sky_rays", "all" if world else None),
                             "world_strength_camera": world.get("strength_camera")})
    summary = {"schema_version": "0.1", "kind": "levers_ab_m13", "variants": list(variants),
               "projects": list(projects),
               "views": {p: list((views or {}).get(p) or []) or m13_views(p) for p in projects}, "rows": rows}
    if view_set not in (None, "", "levers"):
        summary["view_set"] = view_set
    write_json(results_dir / "summary.json", summary)
    (results_dir / "summary.md").write_text(lever_summary_md(summary), encoding="utf-8")
    return summary


def lever_summary_md(summary: dict) -> str:
    """The Markdown table of ``lever_summary`` (one row per view and variant). Pod P6a: a summary of another view set
    (``view_set``: the sky A/B) gets its own title and the columns of the window pull, the daylight tint and the
    interior world; the lever A/B's table is unchanged."""
    if summary.get("view_set") not in (None, "", "levers"):
        return _sky_summary_md(summary)
    lines = ["# Milestone 13 lever A/B (scripts/jobs/levers_ab.sh)", "",
             "| Project | Variant | View | Seconds | EV used | EV metered | lighting_dark | Incident p50 | WB K | "
             "VRAM MiB (view / peak) |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in summary["rows"]:
        if r.get("status") != "rendered":
            lines.append(f"| {r['project']} | {r['variant']} | {r.get('camera') or '-'} | not rendered | | | | | | |")
            continue
        lines.append(f"| {r['project']} | {r['variant']} | {r['camera']} | {r.get('seconds')} | {r.get('ev')} | "
                     f"{r.get('ev_raw')} | {r.get('lighting_dark') or '-'} | {r.get('incident_p50')} | "
                     f"{r.get('wb_temperature')} | {r.get('vram_mib') or '-'} / {r.get('vram_peak_mib') or '-'} |")
    return "\n".join(lines) + "\n"


def _sky_summary_md(summary: dict) -> str:
    """The sky A/B's table (pod P6a): per view and level, the interior world, the exposure, the window pull and the
    panes after it, the white point and the daylight tint."""
    def cell(value) -> str:
        return "-" if value is None else str(value)

    lines = [f"# Milestone 13 interior sky A/B, view set '{summary.get('view_set')}' (scripts/jobs/m13_p6.sh)", "",
             "The interior world (the HDRI that lights the interior views) raised by 2^stops; the exterior world, the "
             "sun, the rig and every other lever as in production. Pull k = the window pull in stops; panes p50 / p90 "
             "after it (display values, 1.0 = white); day green = the view's daylight G/sqrt(RB); tint = the gain on "
             "the white point's G.", "",
             "A windows-only level (skywin*) raises the world only on the camera's paths (through the panes, in sharp "
             "reflections): its world strength is the room's, with the strength the camera sees in brackets.", "",
             "| Project | Variant | View | World strength | Stops | EV used | EV metered | Pull k | Panes p50 / p90 | "
             "WB K (view / project) | Day green | Tint | Seconds |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in summary["rows"]:
        if r.get("status") != "rendered":
            lines.append(f"| {r['project']} | {r['variant']} | {r.get('camera') or '-'} | not rendered "
                         f"| | | | | | | | | |")
            continue
        world = cell(r.get("world_strength"))
        if r.get("world_strength_camera") is not None:          # fix round after P6a: a windows-only level
            world += f" (camera paths {cell(r.get('world_strength_camera'))})"
        lines.append(f"| {r['project']} | {r['variant']} | {r['camera']} | {world} | "
                     f"{cell(r.get('sky_stops'))} | {cell(r.get('ev'))} | {cell(r.get('ev_raw'))} | "
                     f"{cell(r.get('pull_k'))} | {cell(r.get('pane_median_after'))} / {cell(r.get('pane_p90_after'))} | "
                     f"{cell(r.get('wb_temperature'))} / {cell(r.get('wb_project_k'))} | {cell(r.get('wb_day_green'))} | "
                     f"{cell(r.get('wb_view_tint_gain'))} | {cell(r.get('seconds'))} |")
    return "\n".join(lines) + "\n"


def _views_by_project(projects: list, view_set: Optional[str], scene_template: Optional[str]) -> Optional[dict]:
    """``{project: resolve_views(...)["views"]}`` for a view set other than the levers' or with a scene template
    (``{name}`` = the project); None (the lever A/B's ``m13_views``) otherwise."""
    if view_set in (None, "", "levers") and not scene_template:
        return None
    return {p: ab_views(p, view_set, scene_template.replace("{name}", p) if scene_template else None)
            for p in projects}


def main(argv: Optional[list] = None) -> int:
    """``python -m wenart.run.ab m13-prepare --project p --project-out out [--commit sha | --from dir | --from-run
    dir] [--view-set s]``, ``m13-views --project p [--view-set s] [--scene manifest]``, ``m13-sheets --results dir
    --projects a,b [--variants ...] [--baseline dir-template] [--baseline-label text] [--view-set s] [--scene
    template]``, ``m13-summary --results dir [--projects a,b] [--variants ...] [--view-set s] [--scene template]``.
    Pod P6a added ``--from-run``, ``--view-set``, ``--scene``, ``--baseline-label`` and ``m13-views``; without them
    every command does what it did for P1."""
    parser = argparse.ArgumentParser(prog="wenart.run.ab")
    sub = parser.add_subparsers(dest="command", required=True)
    view_help = f"view set: {', '.join(sorted(AB_VIEW_SETS))} (default levers)"
    scene_help = "scene manifest the views are checked against, '{name}' = the project (pod P6a)"
    pp = sub.add_parser("m13-prepare", help="the baseline files of a project into <out>/ab/m13/")
    pp.add_argument("--project", required=True)
    pp.add_argument("--project-out", required=True)
    pp.add_argument("--commit", default=None, help="baseline commit (default M13_BASELINE_COMMITS)")
    pp.add_argument("--from", dest="source", default=None, help="a directory with the baseline files instead of git")
    pp.add_argument("--from-run", dest="run_dir", default=None,
                    help="pod P6a: a project's run output (outputs/<p>) instead of the committed baseline")
    pp.add_argument("--view-set", default="levers", help=view_help)
    pv = sub.add_parser("m13-views", help="the views of a project (comma separated), checked against a scene")
    pv.add_argument("--project", required=True)
    pv.add_argument("--view-set", default="levers", help=view_help)
    pv.add_argument("--scene", default=None, help=scene_help)
    ps = sub.add_parser("m13-sheets", help="one contact sheet per view, the variants side by side")
    ps.add_argument("--results", required=True)
    ps.add_argument("--projects", default="real02,real03")
    ps.add_argument("--variants", default=",".join(M13_AB_VARIANTS))
    ps.add_argument("--baseline", default=None, help="baseline previews, '{name}' = the project (optional)")
    ps.add_argument("--baseline-label", default="M11 baseline", help="the baseline tile's label")
    ps.add_argument("--view-set", default="levers", help=view_help)
    ps.add_argument("--scene", default=None, help=scene_help)
    pm = sub.add_parser("m13-summary", help="summary.json / summary.md of the lever A/B")
    pm.add_argument("--results", required=True)
    pm.add_argument("--projects", default="real02,real03")
    pm.add_argument("--variants", default=",".join(M13_AB_VARIANTS))
    pm.add_argument("--view-set", default="levers", help=view_help)
    pm.add_argument("--scene", default=None, help=scene_help)
    args = parser.parse_args(argv)
    try:
        view_set_of(args.view_set)
    except ValueError as exc:
        print(f"{args.command}: {exc}", file=sys.stderr)
        return 2
    if args.command == "m13-prepare":
        try:
            if args.run_dir and (args.source or args.commit):
                raise ValueError("--from-run excludes --from and --commit")
            info = prepare_m13(args.project, Path(args.project_out), args.source or args.commit,
                               run_dir=Path(args.run_dir) if args.run_dir else None, view_set=args.view_set)
        except (ValueError, OSError) as exc:
            print(f"m13-prepare: {exc}", file=sys.stderr)
            return 1
        print(f"m13-prepare {info['project']}: {info['cameras']} cameras, {info['previews']} previews from "
              f"{info['source']} into {info['out']}" + (f"; {info['reason']}" if info["reason"] else "")
              + (f"; views missing: {info['views_missing']}" if info["views_missing"] else "")
              + (f"; views replaced: {info['views_replaced']}" if info.get("views_replaced") else ""))
        write_json(Path(args.project_out) / M13_DIR / "prepare_m13.json", info)
        return 0
    if args.command == "m13-views":
        resolved = resolve_views(args.project, args.view_set, args.scene)
        for r in resolved["replaced"]:
            print(f"m13-views: {r['wanted']} -> {r['used']} ({r['reason']})", file=sys.stderr)
        for d in resolved["dropped"]:
            print(f"m13-views: {d['wanted']} dropped ({d['reason']})", file=sys.stderr)
        print(",".join(resolved["views"]))
        return 0
    variants = [v for v in args.variants.split(",") if v]
    projects = [p for p in args.projects.split(",") if p]
    views = _views_by_project(projects, args.view_set, args.scene)
    if args.command == "m13-sheets":
        n = 0
        for p in projects:
            base = Path(args.baseline.replace("{name}", p)) if args.baseline else None
            n += len(lever_sheets(Path(args.results), p, variants, views=(views or {}).get(p) or None,
                                  baseline_dir=base, baseline_label=args.baseline_label))
        print(f"m13-sheets: {n} sheets in {Path(args.results) / 'sheets'}")
        return 0
    summary = lever_summary(Path(args.results), projects, variants, views=views, view_set=args.view_set)
    rendered = sum(1 for r in summary["rows"] if r.get("status") == "rendered")
    print(f"m13-summary: {rendered} of {len(summary['rows'])} view renders in {Path(args.results) / 'summary.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
