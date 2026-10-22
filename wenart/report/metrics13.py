"""The 17 before/after metrics of Milestone 13 (docs/milestone13.md §7, §13.2; track T8).

What: ``metrics(project_out, baseline_out=None)`` computes the 17 metrics of §7 for one run of a project and,
when a baseline run is given, the same numbers for it, so the report shows before | after side by side::

    python -m wenart.report metrics13 --out outputs/real04 --baseline results/final/real04 --json m13.json [--md m13.md]

Every metric is ``{"id", "name", "value", "baseline", "unit", "source", "text", "baseline_text", "parts",
"baseline_parts", "target"}``: ``value`` is a number (``unit`` says what: ``%``, ``count``, ``EV``, ``score``,
``min``, ``USD``) or the string ``"no data"`` when the input it needs is missing (never a silent 0); ``text`` is
the human form ("11 of 35 (31 %)"); ``parts`` holds the components of a composite metric (metric 8 has five
numbers, 9 two, 11 three); ``source`` names the files and the rule. The result also carries a per-view table
(camera, room, EV, bare-wall share, cross-check mismatches, commercial-safe line, rubric score and tags, matched
to the baseline by camera name) and the input files found.

Inputs, never images alone (§7: "script over building_final.json, log.json, final_manifest.json"):

- the building: ``building_final.json`` (metrics 1-5, 8, 10, 11, 13);
- the orchestrator log ``orchestrator/log.json`` (6, 7);
- the scene manifest ``scene/scene_manifest.json`` (4 grey boxes, 9 window rooms, 10 shell slots and fabric
  recolour, 11 vegetation, 12 planned exterior cameras, 13 bare-wall share) and the render manifest
  ``renders/render_manifest.json`` (9, 12);
- the final manifest and report ``final/final_manifest.json`` / ``final_report.md`` (9 as a fallback, 12, 14, 16,
  17 stage seconds) and ``final/ATTRIBUTION.md`` (16);
- the rubric ``*_per_view.json`` of the reviewer (15; ``results/review/<folder>/<p>_per_view.json`` of the committed
  baseline, else ``final/rubric_per_view.json`` of the run);
- the one image-based number §7 defines as such: the black pixels of the site view (11), read from the final
  preview of the aerial / site camera.

Two layouts are read (``locate``): the volume's project output (``outputs/<p>/`` with ``scene/``, ``renders/``,
``orchestrator/``, ``final/``, ``run/``) and the committed results (``results/<area>/<p>``: the folder given is any
area folder of the project, e.g. ``results/final/real02``; the siblings ``furniture``, ``renders``, ``agent``,
``final``, ``run`` and ``review`` are read). The committed baselines (docs/milestone13.md §12 D6) are the M11 runs
of real02 and real03 (commit 93aff07) and the M12 run of real04 (commit eddde01; no scene manifest, no renders
folder: the metrics that need them say "no data").

Why: the user's D6 decision compares the Milestone 13 runs with the committed runs on the same views; the numbers
must come from the same script on both sides, with the definitions fixed here (§7).

How (the definitions):

1.  drawn anchors built: ``from_documents`` pieces whose type (or ``drawn_type``) is in ``ANCHOR_TYPES``; built =
    ``build`` not false and ``asset.method`` in library / module / parametric.
2.  drawn pieces in the scene: the same rule over every ``from_documents`` piece. A second number (parts
    ``furniture``, ``built_of_furniture``) leaves out the explained non-furniture: unbuilt pieces the pipeline
    explained as an outline, a detail, a column or decor (``inferred_as`` in ``EXPLAINED_AS``), a symbol both AI
    passes call ``not_furniture``, or a detail inside a kitchen counter leg (``EXPLAINED_REASONS``).
3.  pieces with ``asset.method: none``.
4.  parametric share of the built pieces (parts: parametric and module shares of the built pieces, parametric
    share of every fitted piece = a piece with an ``asset`` whose method is not ``none`` (§7: 115 of 246 for real04,
    the unbuilt ones counted, the 43 method-none ones not), grey boxes = ``furniture_proxy`` objects of the scene
    manifest).
5.  rooms with a complete group set (``ROOM_SETS`` by room type, over built furniture and decor): share of the
    furnished main rooms (rooms of those types with at least one built piece); parts per room type.
6.  findings of the last orchestrator round of the latest run (``run_first_seq``): F8, S2 deeper than 3 cm
    (``evidence.metrics.depth_m``), G10, LG (non-dropped ``finding`` events); value = their sum, parts = each.
7.  accepted edits of the latest run (``run_first_seq``) whose finding is gone in the next round: accepted ``edit``
    events of round r < last with a checklist and a target; gone = no non-dropped finding with the same checklist
    and target in round r + 1.
8.  built library pieces: top model share (value), distinct models, units unknown (``asset.units_known`` false),
    stretch > 5 % (max / min of ``fit_scale`` - 1), audit quality <= 3 (the lower M8 judge score of ``asset.quality``
    <= 3, or a ``vision_doubt`` on the catalogue entry).
9.  interior views at EV >= +5 (value) and the median EV gap between the views of rooms without a window and the
    views of rooms with one (window rooms from the scene manifest's window objects). Round 4: a view the +3 cap held
    (a ``lighting_dark`` record of the render: the view entry's, its exposure's or the render manifest's list) counts
    at its METERED EV (``metrics.ev_wanted``), not at the +3 it was rendered with, in both numbers; without it a dark
    room capped at +3 never reached the +5 count and the cap hid it (P1: the real02 kitchen metered +9.2, capped
    +3.0). Parts add the lighting_dark views by severity. Runs before Milestone 13 have no record: unchanged.
10. shell material slots on PBR sets with normal + roughness maps (a ``maps`` / ``textures`` record of the scene
    manifest's materials; "no data" when the manifest records no maps) and the brief's fabric colour applied to the
    built upholstered pieces (``UPHOLSTERED_TYPES``; applied = the scene object's ``recolour`` has a ``fabric`` slot;
    fix round after P5: or a module / parametric piece's ``fabric`` material key, read from the alternative's scene
    for a piece the base scene does not build; ``fabric_status``).
11. drawn trees (``site.decor`` kind ``tree``) built as real or generated geometry (the scene manifest's
    ``site.vegetation`` / ``site.trees`` records with a method other than a primitive; tree objects without such a
    record count as primitives), hedges built from the drawn rows (``site.hedges`` of the building vs the scene's
    hedge records or objects), black pixels of the site view (the aerial / site camera's final preview; the
    exterior preview with most black only when the run records no view kind at all; no data, with the reason, when
    the run records its views and none is aerial or site). Fix round after P4a: with no drawn tree the value is the
    share of the scene's (inferred) trees built as real geometry.
12. exterior views rendered of planned (planned = the names of the scene manifest's exterior cameras and of the
    dropped ones, each name once; rendered = the planned cameras with an exterior view).
13. views in halls (``HALL_TYPES``) or with >= 50 % bare wall (the scene camera's ``score.shares.wall``).
14. ``in_json_not_rendered`` mismatches of the final check (final manifest ``json_crosscheck``).
15. rubric score of the reviewer (mean over the views of the final report; parts: views at 1, share at 4-5).
16. commercial-safe line present (share of views with ``commercial_safe`` in the manifest and a line in the report)
    and every flagged asset listed in ``ATTRIBUTION.md`` (parts: missing ids).
17. minutes and USD per full run: the stage seconds of the run (``run/*.json`` records of the run id, else the
    final manifest's ``run_stages``) at ``PRICE_USD_PER_H`` (env ``WENART_GPU_USD_PER_H`` overrides; the §7 price
    of the RTX PRO 6000). The pod's wall minutes (docs/gpu-log.md) are longer: setup and downloads are not stages.

Fix round after P3 (16-17 Oct 2026, docs/milestone13.md §14.8):

- What: ``locate`` keeps only the events of the latest run of an appended orchestrator log (``seq >=
  run_first_seq``, the rule of ``wenart.agent.metrics.compute``); metric 2 adds the share without the explained
  non-furniture next to the §7 number.
- Why: the volume's real04 ``log.json`` is re-used by every run (``AgentLog`` appends): P3's "after" read the M12
  round 7 (m6 123, as the baseline) and 222 accepted edits (183 of them M12); counting P3 alone gives m6 38
  (round 4) and m7 29 of 39. Metric 2 counted 12 duplicate sink details, 10 columns, rug outlines and AI-confirmed
  not-furniture symbols as missing pieces (178 of 240; 178 of 202 without them).
- How: the filter applies only when ``run_first_seq`` > 1 (a log without it, or a hand-built one whose events carry
  no ``seq``, keeps every event); ``parts.run_first_seq`` of metrics 6 and 7 says which run was read.

Fix round after P4a (17 Oct 2026, the library lens of the P4a analysis):

- What: metric 11 counts the trees of the scene as well (``scene_trees``): the scene manifest's tree records
  (``site.vegetation`` kind ``tree``) and its tree objects (``site_kind: tree``) by id, real when the record's method
  (else the object's ``veg_method``) is not a primitive. When no tree is drawn, the value is the share of the scene's
  trees (the ones the pipeline inferred) built as real geometry (``parts.tree_basis: "scene"``), not "no data";
  with drawn trees nothing changes (``tree_basis: "drawn"``). "no data" stays for a run with no tree drawn or built
  and for a run without a scene manifest.
- Why: P4a's real02 has no drawn tree; its two inferred olive trees are Poly Haven models, its six boundary hedges
  leaf cards, its site view 0.0 % black, but the CLI listed m11 under "no data" and the text read "trees built 2 of
  0". The M11 baseline's two inferred trees were parametric lollipops with no vegetation record and were not
  counted at all (the docstring's "tree objects without such a record count as primitives" was never coded):
  before 0 of 2, after 2 of 2.
- How: no input was missing (the analyst's numbers are the parts metrics13 already had); only the value rule and
  the text change.
- Integration of the same round (the agent track's ask): metric 7 is the agent's own count
  (``wenart.agent.metrics.findings_removed_metrics``: ``edits_removing_finding`` of ``edits_with_target``), so the
  report and ``orchestrator/metrics.json`` agree. Before, an edit was keyed by its logged checklist and room, so
  P4a's set_lighting edits (findings on cameras) never counted, and a target its round did not have counted as gone
  (P3 real04: 29 of 39 before, 22 of 39 now; P4a real02: 17 of 25 before, 17 of 24 now).

Fix round after P4b (17 Oct 2026, the library lens of the P4b analysis):

- What: metric 12 counts each camera name once (``planned`` = exterior cameras | ``cameras_dropped`` by name),
  ``dropped`` are the dropped names that are not in the final camera list, a dropped name that is back in it is
  ``re_added`` (named in the text, "(agent)" when the camera carries the agent's record), and a rendered exterior
  view of no planned camera is listed apart (``not_planned``), not counted. Metric 11 measures the black pixels only
  in an aerial or site view (``site_view_black``: the scene cameras' ``view``, else the final manifest's
  ``exterior_view``); when the run records its views and none is one, the part is "no data" with the reason
  (``black_reason``: the dropped aerial / site cameras and their ``dropped_reason``) and ``black_basis: "none"``. The
  old rule (the darkest exterior preview) stays only for a run that records no view kind at all (``black_basis:
  "darkest exterior"``, said in the text).
- Why: P4b (real03) reported m12 "6 of 8 (2 dropped)": ext_6 was dropped (frontal, too small) and the agent's "set
  ext_6" re-created it, so it was counted in both lists; the truth is 6 of 7 (ext_5 dropped, ext_6 re-added). m11
  reported "black pixels 1.9 % (ext_6)": ext_6 is an eye-level 3/4 view and its black pixels are window glass; real03
  has no site view at all (the aerial ext_5 was dropped: "flat_cut roof (upper floors not drawn): no aerial view").
  P4a (real02) had "7 of 6": a duplicate camera rendered as "ext_6.001" next to the planned six.
- How: lead decision 1 of 17 Oct 2026 (replayed cameras are frozen; the agent may add a camera, never set or remove a
  replayed one) makes a re-add an added camera; it still counts once. On the job results (runs/, not committed):
  P4b real03 m12 "6 of 7 (1 dropped: ext_5; re-added after the drop: ext_6 (agent))", m11 black "no data (no aerial
  or site view: ext_5 (aerial) dropped: flat_cut roof ...)"; P4a real02 m12 "6 of 6 (0 dropped); also rendered, not a
  planned camera: ext_6.001"; P3 real04 unchanged (6 of 7, black 6.6 % in ext_5). The committed baselines are
  unchanged (real02 M11 6 of 6, black 0.0 % in ext_5; real04 M12 black 29.8 % in ext_7, now marked as the darkest
  exterior).

Pass before P5 (17 Oct 2026; the review of the fix round after P4b). What: metric 11 measures the exterior camera the
build flagged ``site_view`` (``exterior.py``'s ``copies.site_view`` camera, kept on replay) first, then the aerial /
site views in camera order (``site_view_black``). Why: real04 plans two aerial cameras, ext_5 (no flag) and ext_7 (the
site view); the first-aerial rule measured ext_5, and P3 reported "black pixels in the site view 6.6 % (ext_5)" while
its site view ext_7 has 4.1 %; the M12 baseline's 29.8 % is ext_7 too. No camera has ``view`` "site", so the flag is
the only mark of the site view. How: on the job results (runs/, not committed): P3 real04 now 4.1 % in ext_7; P4a
real02 (ext_5, no flag) 0.0 % and P4b real03 (no site view) unchanged; the committed baselines unchanged.

Fix round after P5 (22 Oct 2026; the library lens of the P5 analysis). What: metric 10's fabric part reads each built
upholstered piece from the scene that builds it: the base scene manifest, else an alternative's
(``variants/<id>/scene/scene_manifest.json`` on the volume, ``renders/<p>/variants/<id>/scene_manifest.json`` in the
results; ``Run.variant_scenes``); a module or parametric piece with a ``fabric`` material key counts as applied (its
fabric part is built in the project fabric in the brief's colour), a library model with a ``recolour.fabric`` record
as before; the library models the fit could not recolour are listed apart (``parts.not_recolourable``,
``not_recolourable_models``; a fabric colour was asked), as are those no colour was asked for (``no_colour_asked``:
the style names none for their type), and a piece no scene builds is named (``no_scene``), not counted. Why: P5's
real04 said "0 of 26": the 4 L-1b sofas exist only in the variant's scene (f_L-1b_041 carries ``recolour.fabric``
there), the two L-shaped module sofas and the parametric L-1b sofa carry ``material_keys.fabric`` but no recolour
record, and the rest are models the fit did not recolour (the L1 sofas moved from the recolourable abo_B072555T67 to
abo_B075X4F5CS). How: on the P5 results (runs/, not committed) fabric colour applied 4 of 26 (recoloured 1, fabric
slot 3; colour asked but not recolourable 8 pieces of 6 models; no colour asked 14: the armchairs and ottomans).
"""
from __future__ import annotations

import os
import re
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from wenart.report import common as C

NO_DATA = "no data"
SCHEMA_VERSION = "m13"
ANCHOR_TYPES = ("sofa", "sofa_corner", "bed_double", "table_dining", "wardrobe", "desk")
BUILT_METHODS = ("library", "module", "parametric")
NOT_BUILT_METHOD = "none"
HALL_TYPES = ("hall", "corridor", "vestibule", "landing", "stair")
UPHOLSTERED_TYPES = ("sofa", "sofa_corner", "armchair", "ottoman")
# Metric 2, fix round after P3: unbuilt drawn pieces the pipeline explained as no piece of furniture.
# = wenart.ingest.generic.reading.EXPLAINED_AS (tests/test_m13_report.py keeps them equal)
EXPLAINED_AS = ("rug", "detail", "column", "decor")
# the not_built_reason of a detail inside a kitchen counter leg (wenart.ingest.generic.symbols, M11 split)
EXPLAINED_REASONS = ("detail inside a kitchen counter leg",)
NOT_FURNITURE = "not_furniture"
# Room type -> the group set a furnished room of that type needs (docs/milestone13.md §7 metric 5):
# (name, types that satisfy it, how many).
ROOM_SETS: dict[str, tuple] = {
    "bedroom": (("bed", ("bed_double", "bed_single"), 1), ("nightstands", ("nightstand",), 2),
                ("wardrobe", ("wardrobe",), 1)),
    "living": (("sofa", ("sofa", "sofa_corner"), 1), ("coffee table", ("table_coffee",), 1),
               ("tv unit", ("tv_unit",), 1), ("rug", ("rug",), 1)),
    "kitchen": (("counter", ("kitchen_counter", "kitchen_island"), 1), ("sink", ("sink_kitchen",), 1),
                ("hob", ("stove",), 1), ("fridge", ("fridge",), 1)),
    "bathroom": (("toilet", ("toilet",), 1), ("basin", ("washbasin",), 1), ("shower or tub", ("shower", "bathtub"), 1)),
    "dining": (("table", ("table_dining",), 1), ("chairs", ("chair",), 2)),
}
LAST_ROUND_CHECKS = ("F8", "S2", "G10", "LG")
S2_DEPTH_M = 0.03
EV_HIGH = 5.0
BARE_WALL_SHARE = 0.5
STRETCH_LIMIT = 0.05
QUALITY_LOW = 3
BLACK_LEVEL = 16                  # a pixel is black when every channel is below this (of 255)
PRICE_USD_PER_H = 2.49            # docs/milestone13.md §7 / §8: RTX PRO 6000 median price of 9 Oct 2026
PRICE_ENV = "WENART_GPU_USD_PER_H"
VEGETATION_PRIMITIVES = ("", "primitive", "ellipsoid", "sphere", "proxy", "box", "none")
SITE_VIEWS = ("aerial", "site")   # the exterior camera views whose final preview metric 11 measures for black pixels
DROP_REASON_CHARS = 160           # metric 11: a dropped site camera's reason is cut after this many characters
RESULT_AREAS = ("furniture", "renders", "agent", "final", "run", "review")

# id -> (name, unit of the value, target of §7)
METRICS: dict[int, tuple[str, str, str]] = {
    1: ("drawn anchors built (sofa, sofa_corner, bed_double, table_dining, wardrobe, desk)", "%", "100 %"),
    2: ("drawn pieces in the scene (built, method not none)", "%", ">= 90 %"),
    3: ("pieces with asset.method none", "count", "0"),
    4: ("parametric share of the built pieces; grey boxes", "%", "<= 25 %; 0"),
    5: ("rooms with a complete group set", "%", ">= 90 % of the furnished main rooms"),
    6: ("last-round findings F8 + S2 (> 3 cm) + G10 + LG", "count", "<= 5 / <= 3 / report-only / <= 5"),
    7: ("accepted agent edits whose finding is gone next round", "%", ">= 60 % (or the agent is off)"),
    8: ("built library pieces: top model share; distinct; units unknown; stretch > 5 %; quality <= 3", "%",
        "<= 15 %; >= 60; <= 10 %; <= 10 %; <= 25 %"),
    9: ("interior views at EV >= +5; EV median gap lit vs daylight rooms", "count", "0; <= 2 EV"),
    10: ("shell slots on PBR sets with normal + roughness; fabric colour applied", "%", ">= 90 %; 100 %"),
    11: ("drawn trees built as real geometry; hedges from the drawn rows; black pixels in the site view", "%",
         "100 %; 2; 0 %"),
    12: ("exterior views rendered of planned", "count", "7 of 7"),
    13: ("views in halls or with >= 50 % bare wall", "count", "<= 4"),
    14: ("in_json_not_rendered mismatches of the final check", "count", "0"),
    15: ("rubric score (reviewer, same rubric)", "score", "mean >= 3.0; 0 at 1; >= 25 % at 4-5"),
    16: ("commercial-safe line present; ATTRIBUTION lists every flagged asset", "%", "100 %; 0 missing"),
    17: ("minutes and USD per full run", "min", "<= 150 min, <= $6.50 at $2.49/h"),
}


# --------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------

@dataclass
class Run:
    """The files of one run, read once; a missing file is None and named in ``missing``."""
    root: Path
    name: str
    layout: str                                   # volume | results
    paths: dict = field(default_factory=dict)     # key -> Path or None
    building: Optional[dict] = None
    scene: Optional[dict] = None
    render: Optional[dict] = None
    final: Optional[dict] = None
    report_md: Optional[str] = None
    attribution_md: Optional[str] = None
    log: Optional[dict] = None
    log_first_seq: int = 1                        # the latest run's first event of an appended log (run_first_seq)
    rubric: Optional[list] = None
    variant_scenes: dict = field(default_factory=dict)  # fix round after P5: alternative id -> its scene manifest
    stage_records: list = field(default_factory=list)
    preview_dirs: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    @property
    def missing(self) -> list[str]:
        return sorted(k for k, p in self.paths.items() if p is None)


def _read_json(path: Optional[Path], warnings: list):
    return C.read_json(path, warnings) if path is not None else None


def _first_file(*candidates: Path) -> Optional[Path]:
    for p in candidates:
        if p is not None and Path(p).is_file():
            return Path(p)
    return None


def _results_root(out: Path) -> Optional[tuple[Path, str]]:
    """``(results root, project name)`` when ``out`` is ``results/<area>/<p>`` (any area folder of the project)."""
    if out.parent.name in RESULT_AREAS:
        root = out.parent.parent
        if any((root / area / out.name).is_dir() for area in RESULT_AREAS):
            return root, out.name
    return None


def _rubric_path(volume_final: Optional[Path], results_root: Optional[Path], name: str) -> Optional[Path]:
    """The reviewer's per-view rubric file: ``final/rubric_per_view.json`` of the run, else the newest
    ``results/review/<folder>/<name>_per_view.json``."""
    if volume_final is not None:
        p = _first_file(volume_final / "rubric_per_view.json", volume_final / f"{name}_per_view.json")
        if p is not None:
            return p
    if results_root is not None and (results_root / "review").is_dir():
        found = sorted((results_root / "review").glob(f"*/{name}_per_view.json"))
        if found:
            return found[-1]
    return None


def locate(project_out) -> Run:
    """Read the files of a run in the volume layout or the committed results layout (module docstring)."""
    out = Path(project_out).resolve()
    hit = _results_root(out)
    volume = (out / "building_final.json").is_file() or (out / "scene").is_dir() or (out / "renders").is_dir() \
        or (out / "final").is_dir() or (out / "orchestrator").is_dir()
    if volume or hit is None:
        run = Run(root=out, name=out.name, layout="volume")
        run.paths = {
            "building": _first_file(out / "building_final.json"),
            "scene": _first_file(out / "scene" / "scene_manifest.json"),
            "render": _first_file(out / "renders" / "render_manifest.json"),
            "final": _first_file(out / "final" / "final_manifest.json"),
            "report": _first_file(out / "final" / "final_report.md"),
            "attribution": _first_file(out / "final" / "ATTRIBUTION.md"),
            "log": _first_file(out / "orchestrator" / "log.json"),
            "rubric": _rubric_path(out / "final", None, out.name),
        }
        run.stage_records = _stage_records(out / "run", run.warnings)
        run.preview_dirs = [out / "final", out / "renders"]
        variant_paths = {d.name: d / "scene" / "scene_manifest.json" for d in _dirs(out / "variants")}
    else:
        root, name = hit
        run = Run(root=out, name=name, layout="results")       # root: the folder given; the areas are its siblings
        run.paths = {
            "building": _first_file(root / "furniture" / name / "building_final.json"),
            "scene": _first_file(root / "renders" / name / "scene_manifest.json"),
            "render": _first_file(root / "renders" / name / "render_manifest.json"),
            "final": _first_file(root / "final" / name / "final_manifest.json"),
            "report": _first_file(root / "final" / name / "final_report.md"),
            "attribution": _first_file(root / "final" / name / "ATTRIBUTION.md"),
            "log": _first_file(root / "agent" / name / "log.json"),
            "rubric": _rubric_path(root / "final" / name, root, name),
        }
        run.stage_records = _stage_records(root / "run" / name, run.warnings)
        run.preview_dirs = [root / "final" / name, root / "renders" / name]
        variant_paths = {d.name: d / "scene_manifest.json" for d in _dirs(root / "renders" / name / "variants")}
    w = run.warnings
    run.building = _read_json(run.paths["building"], w)
    run.scene = _read_json(run.paths["scene"], w)
    for vid, path in sorted(variant_paths.items()):
        data = _read_json(path, w) if path.is_file() else None
        if isinstance(data, dict):
            run.variant_scenes[vid] = data
    run.render = _read_json(run.paths["render"], w)
    run.final = _read_json(run.paths["final"], w)
    run.log = _read_json(run.paths["log"], w)
    _latest_run_only(run)
    rubric = _read_json(run.paths["rubric"], w)
    run.rubric = rubric if isinstance(rubric, list) else None
    for key, attr in (("report", "report_md"), ("attribution", "attribution_md")):
        p = run.paths.get(key)
        if p is not None:
            try:
                setattr(run, attr, p.read_text(encoding="utf-8"))
            except OSError as exc:
                w.append(f"{p.name}: unreadable ({exc})")
    if not run.stage_records and isinstance(run.final, dict):
        run.stage_records = [r for r in run.final.get("run_stages") or [] if isinstance(r, dict)]
    for key in run.missing:
        w.append(f"{key}: no file ({run.layout} layout under {run.root})")
    return run


def _latest_run_only(run: Run) -> None:
    """Keep the events of the latest run of an appended orchestrator log (fix round after P3, module docstring):
    ``seq >= run_first_seq``, as ``wenart.agent.metrics.compute``; nothing changes when ``run_first_seq`` is missing
    or 1."""
    if not isinstance(run.log, dict):
        return
    try:
        first = int(run.log.get("run_first_seq") or 1)
    except (TypeError, ValueError):
        first = 1
    run.log_first_seq = first
    if first <= 1:
        return
    events = [e for e in run.log.get("events") or [] if isinstance(e, dict)]
    kept = [e for e in events if _seq(e) >= first]
    run.log = dict(run.log, events=kept)
    run.warnings.append(f"orchestrator log: the latest run from seq {first} ({len(kept)} of {len(events)} events; "
                        "earlier runs of the appended log left out)")


def _dirs(folder: Path) -> list[Path]:
    """The sub-folders of ``folder`` (none when it is missing), in name order."""
    return sorted(d for d in folder.iterdir() if d.is_dir()) if folder.is_dir() else []


def _seq(event: dict) -> int:
    try:
        return int(event.get("seq") or 0)
    except (TypeError, ValueError):
        return 0


def _stage_records(folder: Path, warnings: list) -> list[dict]:
    """The stage records of the newest run id in ``folder`` (``run/<stage>.json``)."""
    if not folder.is_dir():
        return []
    records = []
    for p in sorted(folder.glob("*.json")):
        data = C.read_json(p, warnings)
        if isinstance(data, dict) and data.get("kind") == "stage_record":
            records.append(data)
    run_ids = [r.get("run_id") for r in records if r.get("run_id")]
    if run_ids:
        newest = max(run_ids)
        records = [r for r in records if r.get("run_id") == newest]
    return records


# --------------------------------------------------------------------------
# Helpers over the building and the manifests
# --------------------------------------------------------------------------

def _method(piece: dict) -> str:
    asset = piece.get("asset") if isinstance(piece.get("asset"), dict) else {}
    return str(asset.get("method") or "")


def _built(piece: dict) -> bool:
    return piece.get("build") is not False and _method(piece) in BUILT_METHODS


def _furniture(run: Run) -> list[dict]:
    return [p for p in (run.building or {}).get("furniture") or [] if isinstance(p, dict)]


def _decor(run: Run) -> list[dict]:
    return [d for d in (run.building or {}).get("decor") or [] if isinstance(d, dict)]


def _room_types(run: Run) -> dict:
    return {r.get("id"): r.get("room_type") for r in (run.building or {}).get("rooms") or [] if isinstance(r, dict)}


def _pct(a: int, b: int) -> Any:
    return NO_DATA if not b else round(100.0 * a / b, 1)


def _of(a: int, b: int) -> str:
    return f"{a} of {b}" + (f" ({100.0 * a / b:.0f} %)" if b else "")


def _views(run: Run) -> list[dict]:
    """The rendered views: the final manifest's (camera, room, kind, EV, cross-check), else the render manifest's."""
    if isinstance(run.final, dict) and isinstance(run.final.get("views"), list):
        return [v for v in run.final["views"] if isinstance(v, dict) and v.get("camera")]
    out = []
    for e in (run.render or {}).get("renders") or []:
        if not isinstance(e, dict) or not e.get("camera") or e.get("skipped"):
            continue
        out.append({"camera": e["camera"], "room_id": e.get("room_id"), "level_id": e.get("level_id"),
                    "view_kind": "interior" if e.get("room_id") else "exterior", "exposure": e.get("exposure"),
                    "json_crosscheck": None, "commercial_safe": None})
    return out


def _scene_cameras(run: Run) -> dict:
    return {c["name"]: c for c in (run.scene or {}).get("cameras") or [] if isinstance(c, dict) and c.get("name")}


def _is_exterior(view: dict, cams: dict) -> bool:
    cam = cams.get(view.get("camera")) or {}
    if cam.get("kind") == "exterior":
        return True
    if view.get("view_kind") == "exterior":
        return True
    return not view.get("room_id") and str(view.get("camera") or "").startswith("ext")


def _ev(view: dict) -> Optional[float]:
    exp = view.get("exposure") if isinstance(view.get("exposure"), dict) else None
    ev = exp.get("ev") if exp else None
    return float(ev) if isinstance(ev, (int, float)) else None


def _preview(run: Run, camera: str) -> Optional[Path]:
    for d in run.preview_dirs:
        p = _first_file(d / f"{camera}_final_preview.jpg", d / f"{camera}_preview.jpg")
        if p is not None:
            return p
    return None


def _scene_objects_by_id(run: Run) -> dict:
    return _objects_by_id(run.scene)


def _objects_by_id(scene: Optional[dict]) -> dict:
    out: dict = {}
    for o in (scene or {}).get("objects") or []:
        if isinstance(o, dict) and o.get("wenart_id") and o.get("kind") == "furniture":
            out.setdefault(str(o["wenart_id"]), o)
    return out


def _metric(mid: int, value, text: Optional[str] = None, parts: Optional[dict] = None, source: str = "") -> dict:
    name, unit, target = METRICS[mid]
    return {"id": mid, "name": name, "value": value, "unit": unit, "source": source,
            "text": text if text is not None else (NO_DATA if value == NO_DATA else str(value)),
            "parts": parts or {}, "target": target}


# --------------------------------------------------------------------------
# The 17 metrics
# --------------------------------------------------------------------------

def metric_1(run: Run) -> dict:
    src = "building_final.json furniture[]: source from_documents, type or drawn_type in ANCHOR_TYPES; built = " \
          "build not false and asset.method in library / module / parametric"
    if run.building is None:
        return _metric(1, NO_DATA, source=src)
    anchors = [p for p in _furniture(run) if p.get("source") == "from_documents"
               and (p.get("type") in ANCHOR_TYPES or p.get("drawn_type") in ANCHOR_TYPES)]
    built = [p for p in anchors if _built(p)]
    by_type: dict = {}
    for p in anchors:
        t = p.get("type") if p.get("type") in ANCHOR_TYPES else p.get("drawn_type")
        row = by_type.setdefault(str(t), {"built": 0, "drawn": 0})
        row["drawn"] += 1
        row["built"] += int(_built(p))
    return _metric(1, _pct(len(built), len(anchors)), _of(len(built), len(anchors)),
                   {"built": len(built), "drawn": len(anchors), "by_type": by_type,
                    "not_built": sorted(p.get("id") for p in anchors if not _built(p))}, src)


def explained_not_furniture(piece: dict) -> Optional[str]:
    """Why an unbuilt drawn piece is no piece of furniture (metric 2, fix round after P3), or None: ``inferred_as``
    in ``EXPLAINED_AS`` (an outline, a detail, a column, decor), every AI pass (two or more) says
    ``not_furniture``, or the counter-leg detail of the kitchen split (``EXPLAINED_REASONS``). A built piece is never
    explained away."""
    if _built(piece):
        return None
    if piece.get("inferred_as") in EXPLAINED_AS:
        return str(piece["inferred_as"])
    passes = [c for c in piece.get("type_candidates") or [] if isinstance(c, dict)]
    if len(passes) >= 2 and all(c.get("type") == NOT_FURNITURE for c in passes):
        return NOT_FURNITURE
    reason = str(piece.get("not_built_reason") or "")
    if any(reason.startswith(r) for r in EXPLAINED_REASONS):
        return "detail"
    return None


def metric_2(run: Run) -> dict:
    src = "building_final.json furniture[]: source from_documents; built = build not false and asset.method not " \
          "none; parts furniture / built_of_furniture leave out the unbuilt pieces explained as no furniture " \
          "(inferred_as rug / detail / column / decor, both AI passes not_furniture, a counter-leg detail)"
    if run.building is None:
        return _metric(2, NO_DATA, source=src)
    drawn = [p for p in _furniture(run) if p.get("source") == "from_documents"]
    built = [p for p in drawn if _built(p)]
    explained: dict = {}
    for p in drawn:
        why = explained_not_furniture(p)
        if why is not None:
            explained[why] = explained.get(why, 0) + 1
    n_explained = sum(explained.values())
    furniture = len(drawn) - n_explained
    text = f"{_of(len(built), len(drawn))}; without the {n_explained} explained non-furniture pieces: " \
           f"{_of(len(built), furniture)}"
    return _metric(2, _pct(len(built), len(drawn)), text,
                   {"built": len(built), "drawn": len(drawn),
                    "build_false": sum(1 for p in drawn if p.get("build") is False),
                    "method_none": sum(1 for p in drawn if _method(p) == NOT_BUILT_METHOD),
                    "explained": n_explained, "explained_by": dict(sorted(explained.items())),
                    "furniture": furniture, "built_of_furniture": _pct(len(built), furniture)}, src)


def metric_3(run: Run) -> dict:
    src = "building_final.json furniture[].asset.method == none"
    if run.building is None:
        return _metric(3, NO_DATA, source=src)
    none = [p for p in _furniture(run) if _method(p) == NOT_BUILT_METHOD]
    return _metric(3, len(none), str(len(none)), {"ids": sorted(str(p.get("id")) for p in none)}, src)


def metric_4(run: Run) -> dict:
    src = "building_final.json: built pieces (build not false, method not none) by asset.method; fitted = pieces " \
          "with an asset whose method is not none (the unbuilt ones count, §7); grey boxes = scene_manifest.json " \
          "objects of kind furniture_proxy"
    if run.building is None:
        return _metric(4, NO_DATA, source=src)
    pieces = _furniture(run)
    built = [p for p in pieces if _built(p)]
    # T8 review (15 Oct 2026): §7 counts 115 of 246 fitted pieces for real04 (289 with an asset, 43 of them method
    # none); every asset dict gave 289, a definition §7 does not use.
    fitted = [p for p in pieces if isinstance(p.get("asset"), dict) and _method(p) != NOT_BUILT_METHOD]
    para = sum(1 for p in built if _method(p) == "parametric")
    module = sum(1 for p in built if _method(p) == "module")
    para_all = sum(1 for p in fitted if _method(p) == "parametric")
    grey = NO_DATA
    if run.scene is not None:
        grey = sum(1 for o in run.scene.get("objects") or [] if isinstance(o, dict) and o.get("kind") == "furniture_proxy")
    text = f"{_of(para, len(built))} parametric of the built pieces; {_of(para_all, len(fitted))} of every fitted " \
           f"piece; module {module}; grey boxes {grey}"
    return _metric(4, _pct(para, len(built)), text,
                   {"parametric_of_built": _pct(para, len(built)), "module_of_built": _pct(module, len(built)),
                    "parametric_of_fitted": _pct(para_all, len(fitted)), "built": len(built), "fitted": len(fitted),
                    "parametric": para, "module": module, "grey_boxes": grey}, src)


def metric_5(run: Run) -> dict:
    src = "building_final.json rooms[].room_type x ROOM_SETS over the built furniture and decor of each room " \
          "(furnished main rooms: rooms of a set type with at least one built piece)"
    if run.building is None:
        return _metric(5, NO_DATA, source=src)
    rtypes = _room_types(run)
    by_room: dict = {}
    for p in _furniture(run):
        if _built(p):
            by_room.setdefault(p.get("room_id"), []).append(str(p.get("type")))
    for d in _decor(run):
        # a decor item is built unless build is false (its ``method`` ai / rule says how it was added, not how it was
        # built; one without an asset is built by the decor builder); T8 review: the former condition was always true
        if d.get("build") is not False:
            by_room.setdefault(d.get("room_id"), []).append(str(d.get("type")))
    per_type: dict = {}
    complete = total = 0
    incomplete: dict = {}
    for rid, rtype in rtypes.items():
        if rtype not in ROOM_SETS or not by_room.get(rid):
            continue
        types = by_room[rid]
        missing = [name for name, kinds, n in ROOM_SETS[rtype] if sum(types.count(k) for k in kinds) < n]
        row = per_type.setdefault(rtype, {"complete": 0, "rooms": 0})
        row["rooms"] += 1
        total += 1
        if not missing:
            row["complete"] += 1
            complete += 1
        else:
            incomplete[rid] = missing
    text = "; ".join(f"{t} {r['complete']}/{r['rooms']}" for t, r in sorted(per_type.items())) or "no furnished main room"
    return _metric(5, _pct(complete, total), text,
                   {"complete": complete, "rooms": total, "by_type": per_type, "missing": incomplete}, src)


def _findings(run: Run) -> list[dict]:
    return [e for e in (run.log or {}).get("events") or [] if isinstance(e, dict) and e.get("kind") == "finding"
            and not e.get("dropped")]


def _last_round(run: Run) -> Optional[int]:
    rounds = [int(e.get("round") or 0) for e in _findings(run)]
    return max(rounds) if rounds else None


def metric_6(run: Run) -> dict:
    src = "orchestrator log.json finding events of the last round of the latest run (run_first_seq; not dropped) by " \
          f"checklist; S2 counted when evidence.metrics.depth_m > {S2_DEPTH_M} m"
    last = _last_round(run)
    if run.log is None or last is None:
        return _metric(6, NO_DATA, source=src)
    found = [e for e in _findings(run) if int(e.get("round") or 0) == last]
    counts = {c: 0 for c in LAST_ROUND_CHECKS}
    s2_all = 0
    for e in found:
        c = str(e.get("checklist"))
        if c == "S2":
            s2_all += 1
            depth = ((e.get("evidence") or {}).get("metrics") or {}).get("depth_m")
            if isinstance(depth, (int, float)) and float(depth) > S2_DEPTH_M:
                counts["S2"] += 1
        elif c in counts:
            counts[c] += 1
    text = f"round {last}: F8 {counts['F8']} / S2 > 3 cm {counts['S2']} (S2 all {s2_all}) / G10 {counts['G10']} " \
           f"/ LG {counts['LG']}"
    return _metric(6, sum(counts.values()), text, dict(counts, S2_all=s2_all, round=last, findings=len(found),
                                                      run_first_seq=run.log_first_seq), src)


def metric_7(run: Run) -> dict:
    """Fix round after P4a (integration of the agent track's ask): the agent's own rule
    (``wenart.agent.metrics.findings_removed_metrics``): an accepted edit is judged when it targets a finding (the keys
    of ``evidence.acceptance.target``, else its checklist and target; record-only tools left out) and its round has a
    next one; it is gone when every critical / major finding it targeted that its round has is gone in the next
    round (``causes.finding_key``: an S2 names its cut). Before, an edit was keyed by its logged checklist and room
    (a set_lighting edit logs the room while its findings are on cameras) and a target its round did not have
    counted as gone."""
    from wenart.agent import metrics as AM

    src = "orchestrator log.json of the latest run (run_first_seq): accepted edits that target a finding and have a " \
          "next round (agent.metrics edits_with_target); gone = every critical / major finding they targeted that " \
          "their round has is gone in the next round (edits_removing_finding)"
    last = _last_round(run)
    if run.log is None or last is None:
        return _metric(7, NO_DATA, source=src)
    events = [e for e in run.log.get("events") or [] if isinstance(e, dict)]
    rounds = [e for e in events if e.get("kind") == "round"]
    round_ids = sorted({int(e.get("round") or 0) for e in (rounds or _findings(run))})
    removed = AM.findings_removed_metrics(events, round_ids)
    gone, judged, accepted = (removed["edits_removing_finding"], removed["edits_with_target"],
                              removed["accepted_edits"])
    return _metric(7, _pct(gone, judged), f"{_of(gone, judged)} (accepted edits {accepted}, rounds {last})",
                   {"gone": gone, "judged": judged, "accepted": accepted, "rounds": last,
                    "run_first_seq": run.log_first_seq}, src)


def _quality_low(asset: dict, entry: Optional[dict]) -> Optional[bool]:
    q = asset.get("quality")
    scores = [float(v) for v in (q if isinstance(q, list) else [q]) if isinstance(v, (int, float))]
    doubt = bool(((entry or {}).get("audit") or {}).get("vision_doubt")) if isinstance(entry, dict) else False
    if not scores and not doubt:
        return None
    return bool(scores and min(scores) <= QUALITY_LOW) or doubt


def metric_8(run: Run, catalog=None) -> dict:
    src = "building_final.json built pieces with asset.method library: asset_id counts, units_known, fit_scale " \
          "(max / min - 1 > 5 %), quality (lower M8 judge <= 3) or a catalogue audit vision_doubt"
    if run.building is None:
        return _metric(8, NO_DATA, source=src)
    lib = [p for p in _furniture(run) if _built(p) and _method(p) == "library"]
    if not lib:
        return _metric(8, NO_DATA, "no built library piece", {}, src)
    counts: dict = {}
    for p in lib:
        aid = str(p["asset"].get("asset_id") or "?")
        counts[aid] = counts.get(aid, 0) + 1
    top_id, top_n = max(counts.items(), key=lambda kv: (kv[1], kv[0]))
    unknown = sum(1 for p in lib if p["asset"].get("units_known") is False)
    stretch = 0
    for p in lib:
        s = [float(v) for v in p["asset"].get("fit_scale") or [] if isinstance(v, (int, float)) and v > 0]
        if s and max(s) / min(s) - 1.0 > STRETCH_LIMIT:
            stretch += 1
    low = judged = 0
    for p in lib:
        entry = None
        if catalog is not None:
            try:
                entry = catalog.entry(str(p["asset"].get("asset_id") or ""))
            except Exception:  # noqa: BLE001 - the asset's own judge scores then decide
                entry = None
        q = _quality_low(p["asset"], entry)
        if q is not None:
            judged += 1
            low += int(q)
    parts = {"top_model": top_id, "top_share": _pct(top_n, len(lib)), "distinct_models": len(counts),
             "units_unknown": _pct(unknown, len(lib)), "stretch_over_5pct": _pct(stretch, len(lib)),
             "quality_le3": _pct(low, judged), "built_library": len(lib), "judged": judged}
    text = f"top {top_id} {_of(top_n, len(lib))}; distinct {len(counts)}; units unknown {_of(unknown, len(lib))}; " \
           f"stretch > 5 % {_of(stretch, len(lib))}; quality <= 3 {_of(low, judged)}"
    return _metric(8, parts["top_share"], text, parts, src)


def _window_rooms(run: Run) -> Optional[set]:
    if run.scene is None:
        return None
    rooms: set = set()
    for o in run.scene.get("objects") or []:
        if isinstance(o, dict) and o.get("kind") == "window":
            rooms.update(str(r) for r in o.get("room_ids") or [])
    return rooms


def _dark(run: Run, view: dict) -> Optional[dict]:
    """The view's ``lighting_dark`` record (round 4): the view's own, its exposure's, else the render manifest's list
    entry for its camera; None within the cap or in a run before Milestone 13."""
    exp = view.get("exposure") if isinstance(view.get("exposure"), dict) else {}
    rec = view.get("lighting_dark") or exp.get("lighting_dark")
    if not isinstance(rec, dict):
        rec = next((d for d in (run.render or {}).get("lighting_dark") or []
                    if isinstance(d, dict) and d.get("target") == view.get("camera")), None)
    return rec if isinstance(rec, dict) else None


def _ev_metered(run: Run, view: dict) -> Optional[float]:
    """The EV metric 9 counts (module docstring): the metered EV of a view the cap held, else the EV used."""
    rec = _dark(run, view)
    wanted = (rec.get("metrics") or {}).get("ev_wanted") if rec is not None else None
    return float(wanted) if isinstance(wanted, (int, float)) else _ev(view)


def metric_9(run: Run) -> dict:
    src = "render_manifest.json (else final_manifest.json views) exposure.ev of the interior views, the metered EV " \
          "(lighting_dark metrics.ev_wanted) for a view the +3 cap held; window rooms from the scene manifest's " \
          "window objects (room_ids); gap = median EV (no window) - median EV (window)"
    views = _views(run)
    cams = _scene_cameras(run)
    interior = [v for v in views if not _is_exterior(v, cams) and _ev(v) is not None]
    if not interior:
        return _metric(9, NO_DATA, source=src)
    ev_of = {v["camera"]: _ev_metered(run, v) for v in interior}
    high = [v["camera"] for v in interior if ev_of[v["camera"]] >= EV_HIGH]
    dark = {v["camera"]: _dark(run, v) for v in views}
    dark = {cam: rec for cam, rec in dark.items() if rec is not None}
    win = _window_rooms(run)
    gap: Any = NO_DATA
    med_lit: Any = NO_DATA
    med_day: Any = NO_DATA
    lit = day = []
    if win is not None:
        day = [ev_of[v["camera"]] for v in interior if str(v.get("room_id")) in win]
        lit = [ev_of[v["camera"]] for v in interior if str(v.get("room_id")) not in win]
        if day and lit:
            med_day = round(statistics.median(day), 2)
            med_lit = round(statistics.median(lit), 2)
            gap = round(abs(med_lit - med_day), 2)
    crit = sorted(c for c, r in dark.items() if r.get("severity") == "critical")
    text = f"{len(high)} of {len(interior)} interior views at EV >= +5; gap {gap}" + \
           (f" EV (median {med_lit:+.2f} over {len(lit)} views of rooms without a window vs {med_day:+.2f} over "
            f"{len(day)} views of rooms with one)" if gap != NO_DATA else
            " (window rooms unknown without the scene manifest)" if win is None else " (one group is empty)") + \
           (f"; {len(dark)} view(s) held at the EV cap (lighting_dark: {len(crit)} critical, {len(dark) - len(crit)} "
            f"major), counted at their metered EV" if dark else "")
    return _metric(9, len(high), text, {"views_ev_ge_5": len(high), "interior_views": len(interior),
                                        "ev_gap": gap, "median_ev_no_window": med_lit, "median_ev_window": med_day,
                                        "cameras": high, "lighting_dark": len(dark),
                                        "lighting_dark_critical": len(crit),
                                        "lighting_dark_major": len(dark) - len(crit),
                                        "lighting_dark_cameras": sorted(dark)}, src)


def _material_maps(m: dict) -> Optional[list]:
    for key in ("maps", "textures", "map_files", "pbr_maps"):
        v = m.get(key)
        if isinstance(v, dict):
            return [str(k) for k, f in v.items() if f]
        if isinstance(v, list):
            return [str(x) for x in v]
    return None


def metric_10(run: Run) -> dict:
    src = "scene_manifest.json materials[] (textured shell slots with a maps record naming normal and roughness); " \
          "built upholstered pieces (sofa, sofa_corner, armchair, ottoman) of the scene that builds them (base, else " \
          "an alternative's scene manifest): applied = a recolour with a fabric slot (library model) or a fabric " \
          "material key (module / parametric); models without a recolourable fabric slot are listed apart"
    if run.building is None and run.scene is None:
        return _metric(10, NO_DATA, source=src)
    shell: Any = NO_DATA
    with_maps = textured = 0
    if run.scene is not None:
        recorded = False
        for m in (run.scene.get("materials") or {}).values():
            if not isinstance(m, dict) or not m.get("textured"):
                continue
            textured += 1
            maps = _material_maps(m)
            if maps is not None:
                recorded = True
                names = " ".join(maps).lower()
                if "normal" in names and "rough" in names:
                    with_maps += 1
        if recorded:
            shell = _pct(with_maps, textured)
    uph = [p for p in _furniture(run) if _built(p) and p.get("type") in UPHOLSTERED_TYPES] if run.building else []
    applied: Any = NO_DATA
    fabric = fabric_status(run, uph) if run.scene is not None and run.building is not None else None
    n_applied = n_scene = 0
    extra = ""
    if fabric is not None:
        n_applied = len(fabric["recoloured"]) + len(fabric["fabric_slot"])
        n_scene = n_applied + len(fabric["not_recolourable"]) + len(fabric["no_colour_asked"])
        applied = _pct(n_applied, n_scene)
        models = sorted(set(fabric["not_recolourable"].values()))
        extra = (f" (recoloured {len(fabric['recoloured'])}, module / parametric fabric slot "
                 f"{len(fabric['fabric_slot'])}; colour asked but the model has no recolourable fabric slot: "
                 f"{len(fabric['not_recolourable'])} piece(s), {len(models)} model(s); no fabric colour asked: "
                 f"{len(fabric['no_colour_asked'])} piece(s)"
                 + (f"; read from the alternatives' scenes: {len(fabric['from_variant'])}" if fabric["from_variant"]
                    else "")
                 + (f"; in no scene: {', '.join(fabric['no_scene'])}" if fabric["no_scene"] else "") + ")")
    text = (f"shell slots with normal + roughness: {NO_DATA if shell == NO_DATA else _of(with_maps, textured)}"
            + (" (maps not recorded in the scene manifest)" if shell == NO_DATA and run.scene is not None else "")
            + f"; fabric colour applied: {NO_DATA if applied == NO_DATA else _of(n_applied, n_scene)}" + extra
            + (f" ({len(uph)} upholstered pieces built)" if run.building else ""))
    value = shell if shell != NO_DATA else applied
    parts = {"shell_slots_pbr": shell, "textured_slots": textured, "fabric_applied": applied,
             "upholstered_built": len(uph), "fabric_applied_n": n_applied}
    if fabric is not None:
        # fix round after P5: the pieces in a scene, how each got (or could not get) the brief's fabric colour
        parts.update({"upholstered_in_scene": n_scene, "fabric_recoloured": sorted(fabric["recoloured"]),
                      "fabric_slot": sorted(fabric["fabric_slot"]),
                      "not_recolourable": dict(sorted(fabric["not_recolourable"].items())),
                      "not_recolourable_models": sorted(set(fabric["not_recolourable"].values())),
                      "no_colour_asked": dict(sorted(fabric["no_colour_asked"].items())),
                      "from_variant": dict(sorted(fabric["from_variant"].items())), "no_scene": fabric["no_scene"]})
    return _metric(10, value, text, parts, src)


def fabric_status(run: Run, pieces: list[dict]) -> dict:
    """Fix round after P5 (the library lens of the P5 analysis): how each built upholstered piece got the brief's
    fabric colour, read from the scene that builds it (the base scene, else an alternative's scene manifest:
    ``Run.variant_scenes``; the L-1b sofas of real04 exist only in the variant's scene). ``recoloured``: a library
    model whose scene object's ``recolour`` has a ``fabric`` slot; ``fabric_slot``: a module or parametric piece
    whose scene object has a ``fabric`` material key (built in the project fabric in the brief's colour) and that was
    asked a fabric colour; ``not_recolourable``: ``{id: model}`` of the library models the fit could not recolour
    although a fabric colour was asked (``asset.fabric_colour`` / ``design.fabric_colour``); ``no_colour_asked``:
    ``{id: model}`` of the pieces no fabric colour was asked for (the style names none for their type; fix round after
    P5 (22 Oct 2026), review: a module or parametric piece too, whose fabric key then holds the default fabric); both
    listed apart, not hidden, and both count as not applied; ``no_scene``: pieces no scene builds; ``from_variant``:
    ``{id: alternative}`` (pure over the run's manifests)."""
    base = _scene_objects_by_id(run)
    variants = {vid: _objects_by_id(sc) for vid, sc in sorted(run.variant_scenes.items())}
    out: dict = {"recoloured": [], "fabric_slot": [], "not_recolourable": {}, "no_colour_asked": {}, "no_scene": [],
                 "from_variant": {}}
    for p in pieces:
        pid = str(p.get("id"))
        obj = base.get(pid)
        if obj is None:
            vid = next((v for v, objs in variants.items() if pid in objs), None)
            obj = variants[vid][pid] if vid is not None else None
            if vid is not None:
                out["from_variant"][pid] = vid
        if obj is None:
            out["no_scene"].append(pid)
            continue
        rec = obj.get("recolour")
        keys = obj.get("material_keys") if isinstance(obj.get("material_keys"), dict) else {}
        asked = (p.get("asset") or {}).get("fabric_colour") or (p.get("design") or {}).get("fabric_colour")
        model = str((p.get("asset") or {}).get("asset_id") or obj.get("method") or "?")
        if isinstance(rec, dict) and rec.get("fabric"):
            out["recoloured"].append(pid)
        elif not asked:
            # fix round after P5 (22 Oct 2026), review: a module / parametric piece always has a fabric key (the
            # default fabric when no colour is asked); it counts as applied only when a colour was asked
            out["no_colour_asked"][pid] = model
        elif _method(p) in ("module", "parametric") and keys.get("fabric"):
            out["fabric_slot"].append(pid)
        else:
            out["not_recolourable"][pid] = model
    return out


def _vegetation_records(run: Run) -> Optional[list]:
    site = (run.scene or {}).get("site") if isinstance((run.scene or {}).get("site"), dict) else None
    if site is None:
        return None
    for key in ("vegetation", "trees"):
        v = site.get(key)
        if isinstance(v, list):
            return [x for x in v if isinstance(x, dict)]
    return []


def _black_share(path: Optional[Path]) -> Any:
    if path is None:
        return NO_DATA
    try:
        from PIL import Image
        import numpy as np
        rgb = np.asarray(Image.open(path).convert("RGB"))
    except Exception:  # noqa: BLE001 - no PIL or a broken file: no number
        return NO_DATA
    black = (rgb.max(axis=2) < BLACK_LEVEL).mean()
    return round(100.0 * float(black), 1)


def _primitive(method) -> bool:
    return str(method or "").lower() in VEGETATION_PRIMITIVES


def scene_trees(run: Run) -> tuple[Any, Any]:
    """Fix round after P4a (module docstring): ``(trees, real)`` of the scene manifest, drawn or inferred: its tree
    records (``site.vegetation`` / ``site.trees`` kind ``tree``) and its tree objects (``site_kind: tree``) by id; a
    tree is real when its record's method (else its object's ``veg_method``) is not a primitive (an M11 tree object
    without a record is a parametric primitive). ``(NO_DATA, NO_DATA)`` without a scene manifest."""
    if run.scene is None:
        return NO_DATA, NO_DATA
    methods: dict = {}
    for o in run.scene.get("objects") or []:
        if isinstance(o, dict) and o.get("site_kind") == "tree":
            oid = str(o.get("wenart_id") or o.get("element_id") or o.get("name") or f"object_{len(methods)}")
            methods[oid] = o.get("veg_method")
    for i, r in enumerate(_vegetation_records(run) or []):
        if r.get("kind", "tree") == "tree":
            methods[str(r.get("id") or f"record_{i}")] = r.get("method") or r.get("source")
    return len(methods), sum(1 for m in methods.values() if not _primitive(m))


def metric_11(run: Run) -> dict:
    src = "building_final.json site.decor (kind tree) and site.hedges; scene_manifest.json site.vegetation / " \
          "site.trees records (method not a primitive), site hedge objects; black pixels (every channel < 16) of " \
          "the aerial / site camera's final preview; with no drawn tree, the scene's trees (records and site_kind " \
          "tree objects; an object without a record is a primitive) built as real geometry"
    if run.building is None:
        return _metric(11, NO_DATA, source=src)
    site = run.building.get("site") if isinstance(run.building.get("site"), dict) else {}
    trees = [d for d in site.get("decor") or [] if isinstance(d, dict) and d.get("kind") == "tree"]
    hedges_drawn = len([h for h in site.get("hedges") or [] if isinstance(h, dict)])
    records = _vegetation_records(run)
    built: Any = NO_DATA
    if records is not None:
        real = [r for r in records if r.get("kind", "tree") == "tree"
                and not _primitive(r.get("method") or r.get("source"))]
        built = len(real)
    n_scene, n_real = scene_trees(run)
    hedges_built: Any = NO_DATA
    if run.scene is not None:
        site_s = run.scene.get("site") if isinstance(run.scene.get("site"), dict) else {}
        hedge_recs = site_s.get("hedges") if isinstance(site_s.get("hedges"), list) else None
        if hedge_recs is not None:
            hedges_built = len(hedge_recs)
        else:
            hedges_built = sum(1 for n in site_s.get("objects") or [] if "hedge" in str(n).lower())
    black, black_cam, black_basis, black_reason = site_view_black(run)
    if trees:
        basis = "drawn"
        value = _pct(built, len(trees)) if built != NO_DATA else NO_DATA
        tree_text = f"trees built {NO_DATA if built == NO_DATA else _of(built, len(trees))} ({len(trees)} drawn)"
    elif n_scene != NO_DATA and n_scene > 0:
        # fix round after P4a: no drawn tree, but the pipeline inferred some: the share of those built as real geometry
        basis = "scene"
        value = _pct(n_real, n_scene)
        tree_text = f"no drawn tree; trees in the scene (inferred) as real geometry {_of(n_real, n_scene)}"
    else:
        basis = None
        value = NO_DATA                                               # no tree drawn or built (or no scene): no share
        tree_text = "no drawn tree" + ("; no tree in the scene" if n_scene == 0 else
                                       "; trees in the scene: no data (no scene manifest)")
    if black != NO_DATA:
        black_text = f"{black} % ({black_cam}" + (", the darkest exterior: the run records no view kinds)"
                                                  if black_basis == "darkest exterior" else ")")
    else:
        black_text = NO_DATA + (f" ({black_reason})" if black_reason else "")
    text = f"{tree_text}; hedges {hedges_built} built of {hedges_drawn} drawn rows; black pixels in the site view " \
           f"{black_text}"
    return _metric(11, value, text, {"trees_drawn": len(trees), "trees_built": built, "trees_scene": n_scene,
                                     "trees_scene_real": n_real, "tree_basis": basis, "hedges_drawn": hedges_drawn,
                                     "hedges_built": hedges_built, "black_pct": black, "site_camera": black_cam,
                                     "black_basis": black_basis, "black_reason": black_reason}, src)


def _dropped_records(run: Run) -> list[dict]:
    """The scene manifest's ``cameras_dropped`` as dicts (a bare name becomes ``{"name": name}``; a record without a
    name gets ``dropped_<i>``, so it still counts once)."""
    out = []
    for i, d in enumerate((run.scene or {}).get("cameras_dropped") or []):
        if isinstance(d, dict):
            out.append(dict(d, name=str(d.get("name") or f"dropped_{i}")))
        elif d:
            out.append({"name": str(d)})
    return out


def site_view_black(run: Run) -> tuple[Any, Optional[str], Optional[str], Optional[str]]:
    """Fix round after P4b (module docstring): ``(black %, camera, basis, reason)`` of metric 11's site view.

    - basis ``site view``: the exterior camera the build flagged ``site_view`` (pass before P5: the copies'
      site-view camera, real04's ext_7), else the first one whose ``view`` is aerial or site (the scene manifest's
      cameras, else the final manifest's ``exterior_view``), is measured;
    - basis ``none``: the run records the view of its exterior cameras (or of a dropped one) and none is a site view:
      no data, and ``reason`` names the dropped aerial / site cameras with their ``dropped_reason`` (real03: "ext_5
      (aerial) dropped: flat_cut roof ..."), else "no aerial or site camera planned";
    - basis ``darkest exterior``: a run that records no view kind at all (the M12 real04 baseline: no scene manifest,
      no ``exterior_view``) keeps the old rule, the exterior preview with the most black, and says so."""
    cams = _scene_cameras(run)
    views = _views(run)
    ext = {n: c for n, c in cams.items() if c.get("kind") == "exterior"}
    # pass before P5: the camera flagged as the site view first, then the aerial / site views in camera order
    site_cams = [n for n, c in ext.items() if c.get("site_view")]
    site_cams += [n for n, c in ext.items() if c.get("view") in SITE_VIEWS and n not in site_cams]
    site_cams += [v["camera"] for v in views if v.get("exterior_view") in SITE_VIEWS and v["camera"] not in site_cams]
    if site_cams:
        return _black_share(_preview(run, site_cams[0])), site_cams[0], "site view", None
    dropped = _dropped_records(run)
    if any(c.get("view") for c in ext.values()) or any(v.get("exterior_view") for v in views) or \
            any(d.get("view") for d in dropped):
        why = []
        for d in dropped:
            if d.get("view") in SITE_VIEWS:
                reason = str(d.get("dropped_reason") or "no reason recorded")
                if len(reason) > DROP_REASON_CHARS:
                    reason = reason[:DROP_REASON_CHARS - 3].rstrip() + "..."
                again = f"; re-added as a {ext[d['name']].get('view') or 'other'} view" if d["name"] in ext else ""
                why.append(f"{d['name']} ({d['view']}) dropped: {reason}{again}")
        return NO_DATA, None, "none", "no aerial or site view: " + ("; ".join(why) or
                                                                    "no aerial or site camera planned")
    best = []
    for v in views:
        if _is_exterior(v, cams):
            share = _black_share(_preview(run, v["camera"]))
            if share != NO_DATA:
                best.append((share, v["camera"]))
    if not best:
        return NO_DATA, None, None, None
    black, cam = max(best)
    return black, cam, "darkest exterior", None


def metric_12(run: Run) -> dict:
    src = "scene_manifest.json cameras (kind exterior) | cameras_dropped, by name = planned; render_manifest.json / " \
          "final_manifest.json exterior views of a planned camera = rendered"
    views = _views(run)
    cams = _scene_cameras(run)
    rendered = list(dict.fromkeys(v["camera"] for v in views if _is_exterior(v, cams)))
    if run.scene is None:
        return _metric(12, len(rendered) if views else NO_DATA,
                       f"{len(rendered)} rendered of {NO_DATA} planned (no scene manifest)" if views else NO_DATA,
                       {"rendered": len(rendered) if views else NO_DATA, "planned": NO_DATA, "cameras": rendered}, src)
    # fix round after P4b: one name is one planned view. A camera that was dropped and then re-added (real03: the
    # agent's "set ext_6" re-created the dropped frontal ext_6) counts once, and dropped means dropped and not in the
    # final camera list (lead decision 1 of 17 Oct 2026: the agent may add a camera, never set or remove a replayed one)
    ext = [n for n, c in cams.items() if c.get("kind") == "exterior"]
    dropped_names = list(dict.fromkeys(d["name"] for d in _dropped_records(run)))
    planned = list(dict.fromkeys(ext + dropped_names))
    dropped = [n for n in dropped_names if n not in ext]
    re_added = [n for n in dropped_names if n in ext]
    shown = [n for n in rendered if n in planned]
    extra = [n for n in rendered if n not in planned]       # P4a: a duplicate camera rendered as "ext_6.001"
    text = f"{len(shown)} of {len(planned)} ({len(dropped)} dropped" + (f": {', '.join(dropped)}" if dropped else "")
    if re_added:
        text += "; re-added after the drop: " + ", ".join(
            f"{n} (agent)" if isinstance(cams[n].get("agent"), dict) and cams[n]["agent"] else n for n in re_added)
    text += ")" + (f"; also rendered, not a planned camera: {', '.join(extra)}" if extra else "")
    return _metric(12, len(shown), text,
                   {"rendered": len(shown), "planned": len(planned), "dropped": len(dropped),
                    "dropped_cameras": dropped, "re_added": re_added, "not_planned": extra, "cameras": shown}, src)


def _bare_wall(run: Run, camera: str) -> Any:
    cam = _scene_cameras(run).get(camera)
    if cam is None:
        return NO_DATA
    share = ((cam.get("score") or {}).get("shares") or {}).get("wall")
    return round(float(share), 3) if isinstance(share, (int, float)) else NO_DATA


def metric_13(run: Run) -> dict:
    src = "views whose room (building rooms[].room_type, else the final manifest's room_type) is a hall type " \
          "(hall, corridor, vestibule, landing, stair) or whose scene camera score.shares.wall >= 0.5"
    views = _views(run)
    if not views:
        return _metric(13, NO_DATA, source=src)
    rtypes = _room_types(run)
    cams = _scene_cameras(run)
    halls, bare = [], []
    bare_known = run.scene is not None
    for v in views:
        if _is_exterior(v, cams):
            continue
        rtype = rtypes.get(v.get("room_id")) or v.get("room_type")
        if rtype in HALL_TYPES:
            halls.append(v["camera"])
        share = _bare_wall(run, v["camera"])
        if share != NO_DATA and share >= BARE_WALL_SHARE:
            bare.append(v["camera"])
    both = sorted(set(halls) | set(bare))
    text = f"{len(both)} of {len(views)} views: halls {len(halls)}, bare wall >= 50 % " \
           f"{len(bare) if bare_known else NO_DATA}"
    return _metric(13, len(both), text, {"hall_views": len(halls), "bare_wall_views": len(bare) if bare_known
                                         else NO_DATA, "views": len(views), "cameras": both}, src)


def metric_14(run: Run) -> dict:
    src = "final_manifest.json views[].json_crosscheck.in_json_not_rendered"
    if not isinstance(run.final, dict):
        return _metric(14, NO_DATA, source=src)
    n = views = 0
    for v in _views(run):
        cc = v.get("json_crosscheck") if isinstance(v.get("json_crosscheck"), dict) else {}
        k = len(cc.get("in_json_not_rendered") or [])
        if k:
            n += k
            views += 1
    return _metric(14, n, f"{n} in {views} view(s)", {"mismatches": n, "views": views}, src)


def metric_15(run: Run) -> dict:
    src = "the reviewer's per-view rubric file (client_ready_score 1-5), over the views of the final report"
    if not run.rubric:
        return _metric(15, NO_DATA, "no reviewer rubric file", {}, src)   # fix round after P4a: the CLI names why
    cams = {v["camera"] for v in _views(run)}
    rows = [r for r in run.rubric if isinstance(r, dict) and isinstance(r.get("client_ready_score"), (int, float))]
    if cams:
        rows = [r for r in rows if r.get("view") in cams]
    if not rows:
        return _metric(15, NO_DATA, "no rubric row matches a view of the report", {}, src)
    scores = [float(r["client_ready_score"]) for r in rows]
    at1 = sum(1 for s in scores if s <= 1)
    at45 = sum(1 for s in scores if s >= 4)
    mean = round(statistics.mean(scores), 2)
    text = f"mean {mean:.2f} over {len(scores)} views; {at1} at 1; {at45} at 4-5 ({100.0 * at45 / len(scores):.0f} %)"
    return _metric(15, mean, text, {"mean": mean, "views": len(scores), "at_1": at1, "at_4_5": at45,
                                    "share_4_5": _pct(at45, len(scores)),
                                    "file": str(run.paths.get("rubric"))}, src)


def metric_16(run: Run) -> dict:
    src = "final_manifest.json views[].commercial_safe and the commercial-safe lines of final_report.md; the " \
          "flagged asset ids against final/ATTRIBUTION.md"
    if not isinstance(run.final, dict):
        return _metric(16, NO_DATA, source=src)
    views = _views(run)
    if not views:
        return _metric(16, NO_DATA, "no view", {}, src)
    with_field = [v for v in views if isinstance(v.get("commercial_safe"), dict) and "safe" in v["commercial_safe"]]
    report = run.report_md or ""
    lines = len(re.findall(r"commercial-safe: (?:yes|no)", report))
    present = min(len(with_field), lines)
    flagged: set = set()
    for v in with_field:
        flagged.update(str(a) for a in v["commercial_safe"].get("flagged") or [])
    missing = sorted(a for a in flagged if a not in (run.attribution_md or ""))
    att: Any = len(missing) if run.attribution_md is not None else (NO_DATA if flagged else 0)
    text = f"line present for {_of(present, len(views))}; flagged assets {len(flagged)}, missing in ATTRIBUTION.md " \
           f"{att}"
    return _metric(16, _pct(present, len(views)), text,
                   {"views_with_field": len(with_field), "report_lines": lines, "views": len(views),
                    "flagged_assets": sorted(flagged), "missing_in_attribution": att, "missing_ids": missing}, src)


def metric_17(run: Run) -> dict:
    price = PRICE_USD_PER_H
    raw = os.environ.get(PRICE_ENV)
    if raw:
        try:
            price = float(raw)
        except ValueError:
            run.warnings.append(f"{PRICE_ENV}={raw!r} is no number; {PRICE_USD_PER_H} used")
    src = "the stage seconds of the run (run/*.json records of the run id, else final_manifest.json run_stages) " \
          f"/ 60; USD at {price} USD per GPU hour ({PRICE_ENV} overrides); the pod's wall time is longer (setup, " \
          "downloads: docs/gpu-log.md)"
    records = [r for r in run.stage_records if isinstance(r.get("seconds"), (int, float))]
    if not records:
        return _metric(17, NO_DATA, source=src)
    minutes = round(sum(float(r["seconds"]) for r in records) / 60.0, 1)
    usd = round(minutes / 60.0 * price, 2)
    by_stage = {str(r.get("stage")): round(float(r["seconds"]) / 60.0, 1) for r in records}
    text = f"{minutes:.0f} min of stages, ${usd:.2f} at ${price:.2f}/h ({len(records)} stage records)"
    return _metric(17, minutes, text, {"minutes": minutes, "usd": usd, "price_usd_per_h": price,
                                       "stages": len(records), "by_stage": by_stage}, src)


def _catalog():
    try:
        from wenart.report.final import report_catalog
        return report_catalog()
    except Exception:  # noqa: BLE001 - the asset's own fields decide
        return None


def compute(run: Run) -> dict:
    """The 17 metrics of one run, ``{"m1": ..., "m17": ...}``."""
    cat = _catalog()
    out = {}
    for mid in sorted(METRICS):
        fn = globals()[f"metric_{mid}"]
        try:
            m = fn(run, cat) if mid == 8 else fn(run)
        except Exception as exc:  # noqa: BLE001 - one broken input must not hide the other 16 numbers
            run.warnings.append(f"metric {mid}: not computed ({type(exc).__name__}: {exc})")
            m = _metric(mid, NO_DATA, f"not computed ({type(exc).__name__})")
        out[f"m{mid}"] = m
    return out


# --------------------------------------------------------------------------
# Per view
# --------------------------------------------------------------------------

def view_rows(run: Run) -> list[dict]:
    """One row per rendered view: camera, room, type, kind, EV, bare-wall share, cross-check mismatches,
    commercial-safe line, rubric score and tags."""
    from wenart.report.final import commercial_safe_line

    rtypes = _room_types(run)
    cams = _scene_cameras(run)
    rubric = {r.get("view"): r for r in run.rubric or [] if isinstance(r, dict)}
    rows = []
    for v in _views(run):
        cc = v.get("json_crosscheck") if isinstance(v.get("json_crosscheck"), dict) else {}
        rub = rubric.get(v["camera"]) or {}
        cs = v.get("commercial_safe")
        rows.append({"camera": v["camera"], "room_id": v.get("room_id"),
                     "room_type": rtypes.get(v.get("room_id")) or v.get("room_type"),
                     "kind": "exterior" if _is_exterior(v, cams) else "interior",
                     "ev": round(_ev(v), 2) if _ev(v) is not None else None,
                     # round 4: the metered EV of a view the cap held and its lighting_dark severity (None within it)
                     "ev_metered": round(_ev_metered(run, v), 2) if _ev_metered(run, v) is not None else None,
                     "lighting_dark": (_dark(run, v) or {}).get("severity"),
                     "bare_wall": _bare_wall(run, v["camera"]),
                     "in_json_not_rendered": len(cc.get("in_json_not_rendered") or []) if cc else NO_DATA,
                     "commercial_safe": commercial_safe_line(cs) if cs is not None else "commercial-safe: not recorded",
                     "score": rub.get("client_ready_score", NO_DATA), "tags": list(rub.get("tags") or [])})
    return rows


# --------------------------------------------------------------------------
# metrics(), JSON and markdown
# --------------------------------------------------------------------------

def metrics(project_out, baseline_out=None) -> dict:
    """The 17 metrics of ``project_out`` with, when ``baseline_out`` is given, the baseline's numbers in
    ``baseline`` / ``baseline_text`` / ``baseline_parts`` of every metric and ``views[].before`` per camera."""
    run = locate(project_out)
    after = compute(run)
    base = locate(baseline_out) if baseline_out else None
    before = compute(base) if base is not None else {}
    out_metrics = {}
    for key, m in after.items():
        b = before.get(key) or {}
        out_metrics[key] = dict(m, baseline=b.get("value", NO_DATA) if base is not None else None,
                                baseline_text=b.get("text") if base is not None else None,
                                baseline_parts=b.get("parts") if base is not None else None)
    rows = view_rows(run)
    if base is not None:
        by_cam = {r["camera"]: r for r in view_rows(base)}
        for r in rows:
            r["before"] = by_cam.get(r["camera"])
        extra = sorted(set(by_cam) - {r["camera"] for r in rows})
    else:
        extra = []
    return {"schema_version": SCHEMA_VERSION, "kind": "metrics13", "project": run.name,
            "project_out": str(run.root), "layout": run.layout, "baseline_out": str(base.root) if base else None,
            "baseline_layout": base.layout if base else None, "baseline_project": base.name if base else None,
            "inputs": {k: (str(p) if p else None) for k, p in run.paths.items()},
            "baseline_inputs": {k: (str(p) if p else None) for k, p in base.paths.items()} if base else None,
            "metrics": out_metrics, "views": rows, "baseline_only_views": extra,
            "warnings": list(run.warnings) + ([f"baseline: {w}" for w in base.warnings] if base else [])}


def _fmt(value) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def markdown(result: dict) -> str:
    """The markdown report: the 17 metrics (before | after | target) and the per-view table."""
    has_base = result.get("baseline_out") is not None
    lines = [f"# Milestone 13 metrics: {result['project']}", "",
             f"After: `{result['project_out']}` ({result['layout']} layout)."
             + (f" Before (baseline): `{result['baseline_out']}` ({result['baseline_layout']} layout, project "
                f"{result['baseline_project']})." if has_base else " No baseline given.")
             + " Definitions: docs/milestone13.md §7 and the docstring of wenart/report/metrics13.py; a metric says "
               "\"no data\" when the file it needs is missing.", ""]
    lines += ["## Inputs", ""]
    rows = [[k, v or "missing", (result.get("baseline_inputs") or {}).get(k) or "missing" if has_base else "-"]
            for k, v in (result.get("inputs") or {}).items()]
    lines += C.table(["input", "after", "before"], rows)
    lines += ["", "## The 17 metrics", ""]
    rows = []
    for key in sorted(result["metrics"], key=lambda k: int(k[1:])):
        m = result["metrics"][key]
        rows.append([m["id"], m["name"], (m.get("baseline_text") or _fmt(m.get("baseline"))) if has_base else "-",
                     m.get("text") or _fmt(m.get("value")), m.get("target"), m.get("unit")])
    lines += C.table(["#", "metric", "before", "after", "target", "unit"], rows)
    lines += ["", "Sources:", ""] + [f"- {m['id']}: {m['source']}" for m in
                                      (result["metrics"][k] for k in sorted(result["metrics"], key=lambda k: int(k[1:])))]
    lines += ["", "## Per view", ""]
    rows = []
    for r in result.get("views") or []:
        b = r.get("before") or {}
        row = [r["camera"], r.get("room_id"), r.get("room_type"), r.get("kind")]
        if has_base:
            row += [_fmt(b.get("ev")) if b else "-", _fmt(r.get("ev")), _fmt(b.get("score")) if b else "-",
                    _fmt(r.get("score")), b.get("commercial_safe", "-") if b else "-", r.get("commercial_safe")]
        else:
            row += [_fmt(r.get("ev")), _fmt(r.get("score")), r.get("commercial_safe")]
        row += [_fmt(r.get("in_json_not_rendered")), _fmt(r.get("bare_wall")), ", ".join(r.get("tags") or [])]
        rows.append(row)
    header = ["camera", "room", "type", "kind"]
    header += (["EV before", "EV after", "score before", "score after", "commercial-safe before",
                "commercial-safe after"] if has_base else ["EV", "score", "commercial-safe"])
    header += ["in_json_not_rendered", "bare wall", "rubric tags"]
    lines += C.table(header, rows) if rows else ["No view."]
    if result.get("baseline_only_views"):
        lines += ["", "Views only in the baseline: " + ", ".join(result["baseline_only_views"]) + "."]
    lines += ["", "## Warnings", ""] + C.bullets(result.get("warnings") or [])
    return "\n".join(lines) + "\n"


def write(project_out, baseline_out, json_path, md_path=None) -> dict:
    """``metrics`` written as JSON (and markdown); returns the result."""
    result = metrics(project_out, baseline_out)
    C.write_json(json_path, result)
    if md_path:
        Path(md_path).parent.mkdir(parents=True, exist_ok=True)
        Path(md_path).write_text(markdown(result), encoding="utf-8")
    return result
