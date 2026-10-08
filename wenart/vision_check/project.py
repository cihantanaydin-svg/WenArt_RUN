"""One project output as the vision check sees it (docs/milestone5.md §1.1, §5).

What: ``Project`` loads, once and lazily, what every subcommand needs:
the scene manifest, building and project folder (``views.project_paths``),
the Cycles views (``views.load_views``; stale entries skipped with a
warning), their expected elements (``expected.expected_view``), the final
polished image per camera (``polish/polish_manifest.json``), the two best
gate-accepted sweep attempts per camera (``polish/sweep/polish_manifest.json``),
the removal/insertion/type-swap controls (``check/controls.json`` plus the
control renders in ``controls/hide_<id>/``), the plan-crop paths and the
plan A/B camera set. Nothing here talks to a model or writes a file.

A control whose render is missing, stale or still shows the hidden element
is dropped with a warning (never an error, §5.5).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional

import numpy as np

from wenart import views
from wenart.vision_check import expected as X

CHECK_DIR = "check"
POLISH_MANIFEST = Path("polish") / "polish_manifest.json"
SWEEP_MANIFEST = Path("polish") / "sweep" / "polish_manifest.json"
CONTROLS_JSON = "controls.json"
EXPECTED_JSON = "expected_views.json"
MAPS_KEPT = 4


def read_json(path: Path) -> Optional[dict]:
    """Parsed JSON or None when the file does not exist."""
    path = Path(path)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> Path:
    """JSON with indent=1, ensure_ascii=False; written to a temporary file first, then moved in place."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


def rel(path: Path, base: Path) -> str:
    """POSIX path of ``path`` relative to ``base`` (``..`` allowed), as every M5 JSON stores paths (§1.1)."""
    import os
    return Path(os.path.relpath(Path(path).resolve(), Path(base).resolve())).as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


class Project:
    """Lazy, cached access to one ``outputs/<p>`` folder for the vision check."""

    def __init__(self, project_out, cfg: Optional[dict] = None, render_dir=None) -> None:
        self.out = Path(project_out).resolve()
        self.cfg = X.load_cfg(cfg)
        self.paths = views.project_paths(self.out)
        self.warnings: list[str] = list(self.paths["warnings"])
        self.scene: dict = self.paths["scene_manifest"]
        bpath = Path(self.paths["building_path"])
        self.building: dict = json.loads(bpath.read_text(encoding="utf-8")) if bpath.is_file() else {}
        self.render_dir = Path(render_dir).resolve() if render_dir else Path(self.paths["render_dir"])
        self.check_dir = self.out / CHECK_DIR
        self._views: Optional[dict] = None
        self._expected: dict[str, dict] = {}
        self._table: Optional[dict] = None
        self._maps: dict = {}
        self._sha: dict = {}
        self._controls: Optional[list] = None
        self._swaps: Optional[list] = None
        self._control_views: dict = {}
        self.memo: dict = {}

    # ---- basics ---------------------------------------------------------

    @property
    def project(self) -> str:
        return self.paths["project"]

    @property
    def project_dir(self) -> Path:
        return Path(self.paths["project_dir"])

    @property
    def table(self) -> dict:
        if self._table is None:
            self._table = views.index_table(self.scene)
        return self._table

    def warn(self, msg: str) -> None:
        if msg not in self.warnings:
            self.warnings.append(msg)

    def views(self) -> dict:
        """``{camera: View}`` of the Cycles renders (stale entries skipped with a warning)."""
        if self._views is None:
            found: list[str] = []
            manifest = self.render_dir / "render_manifest.json"
            if manifest.is_file():
                self._views = views.load_views(self.render_dir, skip_stale=True, warnings=found)
            else:
                self._views = {}
                found.append(f"no render manifest at {manifest}")
            for w in found:
                self.warn(w)
        return self._views

    def expected(self, camera: str) -> dict:
        """``expected_view`` of a Cycles camera (cached)."""
        if camera not in self._expected:
            self._expected[camera] = X.expected_view(self.views()[camera], self.scene, self.building, self.cfg)
        return self._expected[camera]

    def expected_all(self) -> dict:
        return {cam: self.expected(cam) for cam in self.views()}

    def expected_of(self, view: "views.View") -> dict:
        """``expected_view`` of any view (a control render's list is not cached under the camera name)."""
        key = (view.camera, str(view.png))
        if key not in self._expected:
            self._expected[key] = X.expected_view(view, self.scene, self.building, self.cfg)
        return self._expected[key]

    def maps(self, view: "views.View") -> tuple[np.ndarray, np.ndarray]:
        """``(index, depth_mm)`` uint16 maps of a view (the last few are kept: 8 MB per 1920x1080 view)."""
        key = (str(view.index), str(view.depth_mm))
        if key in self._maps:
            self._maps[key] = self._maps.pop(key)          # most recent last
        else:
            self._maps[key] = (view.read_index(), view.read_depth_mm())
            while len(self._maps) > MAPS_KEPT:
                self._maps.pop(next(iter(self._maps)))
        return self._maps[key]

    def cached(self, key, make):
        """A small memo for derived values (decoy boxes per render, ...)."""
        if key not in self.memo:
            self.memo[key] = make()
        return self.memo[key]

    def file_sha(self, path: Path) -> str:
        key = str(Path(path).resolve())
        if key not in self._sha:
            self._sha[key] = sha256_file(Path(path))
        return self._sha[key]

    def room(self, room_id: Optional[str]) -> dict:
        return next((r for r in self.building.get("rooms") or [] if r.get("id") == room_id), {})

    # ---- Milestone 10: Feature 1 and the exterior ---------------------------

    def variant(self) -> str:
        """The variant this output renders (``base`` for a project output)."""
        return str((self.scene.get("variant") or {}).get("id") or "base")

    def exterior_cameras(self) -> list[str]:
        """The rendered cameras of kind ``exterior``."""
        from wenart.vision_check import exterior as EXT
        cams = {c.get("name"): c for c in self.scene.get("cameras") or []}
        return [cam for cam in self.views() if EXT.is_exterior(cams.get(cam), self.views()[cam])]

    def completion(self) -> Optional[dict]:
        """``completion.json`` of the layout stage (next to ``building_final.json``, else in the project output)."""
        for folder in (Path(self.paths["building_path"]).parent, self.out, self.out.parent.parent):
            data = read_json(Path(folder) / "completion.json")
            if data is not None:
                return data
        return None

    def drawn_check(self) -> Optional[dict]:
        """``wenart.vision_check.drawn.drawn_check`` of this output (cached); None without a building."""
        def make():
            from wenart.vision_check import drawn
            if not self.building:
                return None
            try:
                return drawn.drawn_check(self.building, drawn.load_source(self.out), self.completion(), self.cfg)
            except ImportError as exc:                       # shapely missing: the check cannot run here
                self.warn(f"drawn-piece check not run ({exc})")
                return None
        return self.cached("drawn_check", make)

    def elevation_check(self) -> Optional[dict]:
        """``wenart.vision_check.elevation.elevation_check`` of this output's variant (cached)."""
        def make():
            from wenart.vision_check import elevation
            if not self.building:
                return None
            return elevation.elevation_check(self.building, self.scene, elevation.load_sheets(self.out), self.cfg,
                                             self.variant())
        return self.cached("elevation_check", make)

    # ---- polish outputs -------------------------------------------------

    def polished(self) -> dict[str, dict]:
        """``{camera: {"png": Path, "k": int}}`` of the views whose polish final is ``polished``."""
        return self.cached("polished", self._polished)

    def _polished(self) -> dict[str, dict]:
        manifest = read_json(self.out / POLISH_MANIFEST)
        out: dict[str, dict] = {}
        if not manifest:
            return out
        base = (self.out / POLISH_MANIFEST).parent
        for v in manifest.get("views") or []:
            if v.get("final") != "polished" or v.get("final_attempt") is None:
                continue
            if not self._same_source(v, "polish"):
                continue
            rec = next((a for a in v.get("attempts") or [] if a.get("k") == v["final_attempt"]), None)
            if not rec or not rec.get("png"):
                self.warn(f"{v.get('camera')}: polish final attempt {v['final_attempt']} has no PNG")
                continue
            png = base / rec["png"]
            if not png.is_file():
                self.warn(f"{v.get('camera')}: polished PNG missing ({png})")
                continue
            out[v["camera"]] = {"png": png, "k": int(v["final_attempt"])}
        return out

    def _same_source(self, view_rec: dict, what: str) -> bool:
        """True when a polish view was made from the current Cycles PNG (``source_sha256``), else a warning."""
        cam = view_rec.get("camera")
        view = self.views().get(cam)
        if view is None:
            self.warn(f"{cam}: {what} view has no current Cycles render; not checked")
            return False
        want = view_rec.get("source_sha256")
        if want and Path(view.png).is_file() and self.file_sha(view.png) != want:
            self.warn(f"{cam}: {what} images were made from another Cycles render (source_sha256); not checked")
            return False
        return True

    def sweep_attempts(self, best: int = 2) -> dict[str, list[dict]]:
        """``{camera: [{"k", "png", "strength"}]}``: the ``best`` gate-accepted grid attempts per sweep view.

        Best = strongest first (the most polish the gate still accepted), then
        the lower attempt number. ``presumed_bad`` attempts are left out.
        """
        return self.cached(("sweep", best), lambda: self._sweep_attempts(best))

    def _sweep_attempts(self, best: int) -> dict[str, list[dict]]:
        manifest = read_json(self.out / SWEEP_MANIFEST)
        out: dict[str, list[dict]] = {}
        if not manifest:
            return out
        base = (self.out / SWEEP_MANIFEST).parent
        for v in manifest.get("views") or []:
            if not self._same_source(v, "sweep"):
                continue
            accepted = []
            for a in v.get("attempts") or []:
                if a.get("role") == "presumed_bad" or not a.get("png"):
                    continue
                if ((a.get("gate") or {}).get("decision")) != "accept":
                    continue
                png = base / a["png"]
                if png.is_file():
                    accepted.append({"k": int(a["k"]), "png": png, "strength": float(a.get("strength") or 0.0)})
            accepted.sort(key=lambda a: (-a["strength"], a["k"]))
            if accepted:
                out[v["camera"]] = accepted[:best]
        return out

    # ---- controls -------------------------------------------------------

    def _load_controls(self) -> None:
        data = read_json(self.check_dir / CONTROLS_JSON)
        if data is None:
            self.warn(f"no {CONTROLS_JSON} in {rel(self.check_dir, self.out)} (run select-controls): no controls")
            data = {}
        valid = []
        for c in data.get("controls") or []:
            view = self.control_view(c)
            if view is not None:
                valid.append(dict(c))
        self._controls = valid
        self._swaps = [dict(s) for s in data.get("swaps") or [] if s.get("camera") in self.views()]

    def control_view(self, control: dict) -> Optional["views.View"]:
        """The hidden render of a control, or None (dropped with a warning) when missing, stale or not hidden."""
        key = (control["id"], control["camera"])
        if key in self._control_views:
            return self._control_views[key]
        hdir = self.out / control.get("dir", f"controls/hide_{control['id']}")
        view = None
        if control["camera"] not in self.views():
            self.warn(f"control {control['id']}: camera {control['camera']} has no Cycles view; dropped")
        elif not (hdir / "render_manifest.json").is_file():
            self.warn(f"control {control['id']}: no render in {rel(hdir, self.out)}; dropped")
        else:
            found: list[str] = []
            try:
                vs = views.load_views(hdir, [control["camera"]], skip_stale=True, warnings=found)
            except KeyError:
                vs = {}
                found.append(f"{control['camera']} not rendered")
            view = vs.get(control["camera"])
            if view is None:
                self.warn(f"control {control['id']}: {'; '.join(found) or 'no view'}; dropped")
            else:
                ids = {self.table[i]["wenart_id"] for i in view.index_stats if i in self.table}
                if control["id"] in ids:
                    self.warn(f"control {control['id']}: the control render still contains it; dropped")
                    view = None
        self._control_views[key] = view
        return view

    def controls(self) -> list[dict]:
        """Valid controls of ``check/controls.json`` (each has a usable hidden render)."""
        if self._controls is None:
            self._load_controls()
        return self._controls

    def swaps(self) -> list[dict]:
        if self._swaps is None:
            self._load_controls()
        return self._swaps

    # ---- plan crops and the plan A/B set --------------------------------

    def plan_path(self, camera: str) -> Path:
        return self.check_dir / f"{camera}_plan.jpg"

    def plan_ab_cameras(self) -> list[str]:
        """Cameras of the plan A/B: the control cameras, then the sweep views (``plan_ab.views``)."""
        cams: list[str] = []
        for c in self.controls():
            if c["camera"] not in cams:
                cams.append(c["camera"])
        n = int((self.cfg.get("plan_ab") or {}).get("views", 4))
        for cam in X.sweep_views(self.expected_all(), n):
            if cam not in cams:
                cams.append(cam)
        return cams
