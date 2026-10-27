"""The vision auditor, documents vs model (26 Oct 2026; user: "the audit is very weak, only the looks being judged,
everything needs to be judged. There was a veranda in real06, it has been fully missed, we need a big smart auditor to
check everything in the project ... the issue is not just veranda").

What: the agent model compares the source documents with the model, level by level and side by side; nobody did
before (the vision critic judges renders, ``critique_model_view`` one top-down view per floor, never next to the
drawing):

- ``plan_image(project_out, level_id)``: the source plan of one level as an image. The page the reading took the
  level from (``documents[].pages[]`` with that ``level_id`` and a ``transform_to_building``, chosen like the plan
  crops: ``wenart.vision_check.plan_crop.plan_page``), its region of a multi-drawing sheet only, is drawn from the
  drawing's own strokes and texts (``dxf_generic.read_page`` of the converted DXF of a DWG, ``cad_pdf.read_page`` of
  a vector PDF): no overlays of the reading, walls (wall-hint layers and fills) darker, the texts upright with a
  white halo in their blocks (a name with its area under it, ``text_blocks``), what only clutters left out: bare
  integers (dimension figures, tread numbers), the dimension lines the reading's own finder recognises
  (``dimension_strokes``) and grid axes or cut lines running through the walls' box (``axis_line``). It is drawn in
  the building frame and turned like the model's top-down view (``wenart.blender.topdown``: seen from its azimuth,
  foreshortened by its tilt; ``topdown/top_<level>.png.frame.json``, else the module's defaults), so the two images
  of a call show every room in the same place; an arrow shows where the drawing's up points. The frame is the
  level's walls, rooms and site areas plus ``FRAME_MARGIN_M`` and the labels near them (a veranda outside the walls
  is in it). Fallbacks, said in the record and the prompt: a raster page's rectified image cropped to the frame
  (``raster``), the reading's debug image (``debug_image``: its colours are the reading's, not the drawing's).
- ``elevation_image(project_out, region_id)``: an elevation or section region of ``sheets.json``, drawn the same
  way in its own frame (its ``metres_per_unit``).
- ``audit_level(model, building, level_id, plan=, topdown=, call_id=)``: one structured call, two images (image 1
  the plan, image 2 ``renders/top_<level>_plan.jpg``: angled, ceilings off, rooms named), the facts of the model's
  level (rooms with types, computed and stated areas and the labels they carry; openings; stairs; built pieces per
  room; unbuilt pieces and symbols; site areas with their build state; platforms, paved and parking surfaces; the
  entrance steps; level marks) and the plan's texts. The model lists every difference: what the plan shows that the
  model lacks or has differently, and what the model has that the plan does not show.
- ``audit_elevations(model, building, sheets=, renders=, call_id=)``: per elevation or section region of
  ``sheets.json`` (``class`` ``elevation`` / ``section``) one call: the drawing and the exterior render of its side
  (``building.facade.elevations`` / ``sheets.exterior.openings_seen`` give the side; the views' ``sides`` of the
  scene manifest); a sheet of every exterior view when the side is unknown (the model names the view it matched).
  Storeys, roof form, window and door rows, balconies, verandas, terraces. A project without elevation or section
  drawings gets a record that says so (no call).
- ``audit_project(model, project_out)``: every level with a plan and a top-down view, then the elevations.

Checks (a claim's ``kind`` names its check; the owner is the stage that owns the fix):

- B1 space: an open-air or semi-open space (veranda, terrace, balcony, loggia, porch, patio, courtyard, pool,
  parking) the documents show and the model lacks or builds otherwise, or one the model has and they do not show.
  Owner ``site`` when the building records it (``site.areas``), else ``reading`` (nothing read it).
- B2 room: a room missing, merged or split, of another type, far from its stated area, or a room the plan does not
  show. Owner ``reading``; a room of another type ``architect`` (``retype_room``).
- B3 stair: a stair or ramp missing, of another form, run or place, or one the plan does not show. Owner
  ``reading``.
- B4 door: a door missing, of another kind, width or place, a window or a wall where the plan has a door, or a door
  the plan does not show. Owner ``openings`` (``reading`` when the model has nothing there); actions
  ``gap_to_door``, ``window_to_door``, ``door_type``, ``widen_door``, ``door_to_window``.
- B5 window: a window missing, of another size or place, a door where the plan has a window, or a window the plan
  does not show. Owner ``openings`` (``reading`` when missing); actions ``door_to_window``,
  ``move_window_to_outer_wall``.
- B6 wall: a wall or part of the outline missing, misplaced, or one the plan does not show. Owner ``reading``.
- B7 fixture: fixed equipment (kitchen run, island, appliances, sanitary ware, built-ins) missing, of another type,
  place or height, or one the plan does not show. Owner ``furniture``; actions ``retype_piece``, ``move_piece``,
  ``mount_fixture``, ``remove_piece``.
- B8 furniture: drawn furniture missing or of another type or place (pieces the model adds to complete a room are
  no difference: the furniture rules add them). Owner ``furniture``; actions ``retype_piece``, ``move_piece``,
  ``remove_piece``.
- B9 level and form: storeys, floor levels, steps and thresholds, the roof form. Owner ``reading`` (a threshold
  ``architect``: ``snap_threshold``; a step outside ``site``).

A ``fix`` is named only when ``wenart.blender.architect_actions.ACTIONS`` has it.

Code checks every claim before it counts (CLAUDE.md: every AI claim is checked by code; vector geometry > AI
vision); a dropped claim keeps its reason:

- an id must exist (an element of the level: room, wall, opening, piece, site area, platform, surface) and fit the
  kind (a door claim on a sofa is dropped); a room id that does not exist is ignored (the claim stays);
- a ``missing`` claim must not name something the model has built (a built piece, an opening, a wall, a room, a
  built site area: a ``build`` true area or a surface or platform made from it, ``area_id``); a labelled space or
  room is matched by its label with ``site.areas`` and ``rooms`` (labels, evidence texts, the space word: veranda,
  terrace, balcony ...): matched and built -> dropped, matched and not built -> kept on that record (the veranda of
  real06: ``sa_L0_veranda``, ``build: false``), not matched -> kept only when the label is a text of the plan
  (owner ``reading``; when the plan's texts are known);
- an ``extra`` claim must name a built element of the model that the plan does not show: a piece the furniture
  rules added (``added_by_ai``) or an element drawn in the source (vector evidence of the plan's page) is dropped;
- a ``different`` claim needs an id, a matched label or a room; on an unbuilt element it becomes ``missing``;
- elevations: a storey count the model does not have, a roof form the model does not have (the code's
  ``roof_record``), a drawn roof form other than the vector reading's when the model builds the reading's, a count
  of windows or doors equal to the model's on that side (``vision_check.exterior.outer_openings``) is dropped;
- the same claim twice is dropped as a duplicate; a missing labelled space with a stated area of at least
  ``MAJOR_AREA_M2`` is at least ``major``.

Finding format (the auditors' common format): ``{"line": "plan_vs_model" | "elevations", "check": "B1".."B9",
"severity", "target": an element id, a room id or "building", "message", "evidence": {"level", "plan_image",
"model_image", "label", ... the claim's kind, change, aspect, room, call id and what code matched}, "owner":
"reading" | "site" | "architect" | "furniture" | "openings", "fix": an action of ``ACTIONS`` or None}``. Images are
paths relative to the project output when they lie in it.

Why: "There was a veranda in real06, it has been fully missed": the reading kept its label (``sa_L0_veranda``,
``build: false``) and no stage built it, and no check compared the model with the drawing.

How: pure apart from the model calls and the images (Pillow); ``MockModel`` replays answers in the CPU tests. Two
images per call, each at most ``IMAGE_MAX_SIDE``; the facts are capped (``MAX_FACT_LINES``) so a call stays far
under the served context.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

from wenart import building as B
from wenart import geometry as G
from wenart.agent.model import IMAGE_MAX_SIDE, user_message

LINE_PLAN = "plan_vs_model"
LINE_ELEVATIONS = "elevations"
AUDIT_DIR = "audit"
SEVERITIES = ("critical", "major", "minor")
OWNERS = ("reading", "site", "architect", "furniture", "openings")

CHECKS = {
    "B1": {"what": "space: veranda, terrace, balcony, loggia, porch, patio, courtyard, pool, parking", "owner": "site"},
    "B2": {"what": "room: missing, merged or split, another type, far from its stated area, or not in the plan",
           "owner": "reading"},
    "B3": {"what": "stair or ramp: missing, another form, run or place, or not in the plan", "owner": "reading"},
    "B4": {"what": "door: missing, another kind, width or place, a window or wall instead, or not in the plan",
           "owner": "openings"},
    "B5": {"what": "window: missing, another size or place, a door instead, or not in the plan", "owner": "openings"},
    "B6": {"what": "wall or outline: missing, misplaced, or not in the plan", "owner": "reading"},
    "B7": {"what": "fixed equipment (kitchen run, island, appliances, sanitary ware, built-ins): missing, another "
                   "type, place or height, or not in the plan", "owner": "furniture"},
    "B8": {"what": "drawn furniture: missing, another type or place", "owner": "furniture"},
    "B9": {"what": "levels and form: storeys, floor levels, steps and thresholds, the roof form", "owner": "reading"},
}
KINDS = ("space", "room", "stair", "door", "window", "wall", "fixture", "furniture", "level")
ELEVATION_KINDS = ("space", "floors", "roof", "window", "door", "stair", "wall", "level")
CHANGES = ("missing_in_model", "different_in_model", "extra_in_model")
ASPECTS = ("presence", "type", "position", "size", "orientation", "height", "shape", "count")
ROOF_FORMS = ("flat", "shed", "gable", "hip", "mansard", "gambrel", "other", "none")
CHECK_OF_KIND = {"space": "B1", "room": "B2", "stair": "B3", "door": "B4", "window": "B5", "wall": "B6",
                 "fixture": "B7", "furniture": "B8", "level": "B9", "floors": "B9", "roof": "B9"}
# The model elements a claim of each kind may target (``element_index`` categories); "" and "building" always.
KIND_TARGETS = {
    "space": ("area", "surface", "platform", "room"),
    "room": ("room",),
    "stair": ("piece", "room"),
    "door": ("opening", "room"),
    "window": ("opening", "room"),
    "wall": ("wall", "room"),
    "fixture": ("piece", "room"),
    "furniture": ("piece", "room"),
    "level": ("room", "opening", "level", "area", "surface", "platform"),
    "floors": ("level",),
    "roof": (),
}
NO_TARGET = ("", "none", "null", "-", "n/a", "building")
MAJOR_AREA_M2 = 4.0            # a missing labelled space at least this large is at least ``major``
FRAME_MARGIN_M = 2.5           # the plan's frame: the level's walls, rooms and site areas plus this ...
LABEL_REACH_M = 6.0            # ... and the plan's labels this far beyond them (+ LABEL_PAD_M)
LABEL_PAD_M = 1.0
AXIS_MIN_M = 3.0               # a grid axis or cut line: at least this long ...
AXIS_OUT_M = 0.5               # ... with both ends this far outside the walls' box
DIM_LAYER_SHARE = 0.2          # a layer with this share of its strokes in dimensions is a dimension layer
STACK_DX = 0.6                 # text_blocks: lines stack within this x the wider one's width across ...
STACK_DY = 1.9                 # ... and this x the taller one's height apart
MAX_FACT_LINES = 140           # lines of facts in one prompt
MAX_PIECES_PER_ROOM = 16
MAX_PLAN_TEXTS = 40
MAX_CLAIMS = 14
AUDIT_MAX_TOKENS = 3072
COUNT_TOL = 1                  # a count claim on the model within this of the code's count is not contradicted
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SUPERSAMPLE = 2
TITLE_H = 48
PAD_PX = 14
INK = (25, 25, 25)
LINE_GREY = (95, 95, 95)
WALL_INK = (0, 0, 0)
FILL_GREY = (205, 205, 205)
DARK_FILL = (70, 70, 70)
ARROW_RGB = (200, 30, 30)
# Words of open-air and semi-open spaces (on ``fold_ascii`` text): space word -> regex. Turkish, English, German,
# French; ``wenart.ingest.generic.labels.AREA_KIND_WORDS`` (pool, terrace, parking, paving, garden) after these.
SPACE_WORDS = (
    ("veranda", r"\b(veranda|verandah|sundurma|porch|portik|portico|veranda couverte|vorbau)\b"),
    ("balcony", r"\b(balkon|balcony|balcon|loggia|lodjia|lodzya)\b"),
    ("terrace", r"\b(teras|terrace|terrasse|deck|sit out|otla|guneslenme|sun deck|sundeck)\b"),
    ("courtyard", r"\b(avlu|courtyard|court|patio|innenhof|hof|cour)\b"),
    ("pool", r"\b(havuz|pool|schwimmbad|piscine)\b"),
    ("parking", r"\b(otopark|park yeri|garaj|parking|car porch|carport|garage|stellplatz|parkplatz)\b"),
    ("garden", r"\b(bahce|garden|lawn|garten|jardin)\b"),
    ("paving", r"\b(kaldirim|paving|drive|driveway|pflaster|pave)\b"),
)
_SPACE_RE = [(k, re.compile(p)) for k, p in SPACE_WORDS]
_AREA_TEXT = re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:m2|m²|m\^2|sq\.? ?m)?", re.IGNORECASE)
_BARE_INT = re.compile(r"^\s*\d{1,4}\s*$")
_LETTERS = re.compile(r"[^\W\d_]", re.UNICODE)

AUDIT_SYSTEM = (
    "You are a meticulous architect. You check that a 3D model a program built matches the architectural drawings "
    "it was built from: you compare the drawing with images of the model and with the model's facts, and you list "
    "every difference you can point at in the drawing. You answer only with JSON that follows the given schema. "
    "Copy ids exactly from the facts; never invent an id. If the model matches the drawing, answer with an empty "
    "list.")


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def fold(text: Any) -> str:
    """Folded text for matching: ASCII look-alikes, lower case, single spaces (``building.fold_ascii``)."""
    return " ".join(B.fold_ascii(str(text or "")).split())


def name_words(text: Any) -> set:
    """The name words of a label (>= 3 letters, no figures or units): "VERANDA 22,80m²" -> {"veranda"}."""
    words = re.findall(r"[a-z]{3,}", fold(text))
    return {w for w in words if w not in ("m2", "sqm", "the", "and", "with")}


def space_word(text: Any) -> Optional[str]:
    """The open-air space a text names (``SPACE_WORDS``), or None."""
    f = fold(text)
    for kind, pattern in _SPACE_RE:
        if pattern.search(f):
            return kind
    return None


def stated_area(text: Any) -> Optional[float]:
    """The area a label states ("22,80m²", "22.80 m2") in m², or None (a bare integer is no area)."""
    s = str(text or "")
    for m in _AREA_TEXT.finditer(s):
        raw = m.group(1)
        if ("," in raw or "." in raw or re.search(r"m2|m²|m\^2|sq", m.group(0), re.IGNORECASE)):
            try:
                return float(raw.replace(",", "."))
            except ValueError:
                continue
    return None


def _rel(path: Any, project_out: Optional[Path]) -> Optional[str]:
    if path in (None, ""):
        return None
    p = Path(path)
    if project_out is not None:
        try:
            return p.resolve().relative_to(Path(project_out).resolve()).as_posix()
        except (ValueError, OSError):
            pass
    return str(p)


def _read_json(path: Path) -> Optional[dict]:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def load_building(project_out) -> Optional[dict]:
    """The building as the scene was built (``scene/building_built.json``: the architect's answers and the clash
    moves), else ``building_agent.json``, ``building_final.json``, ``building.json``."""
    out = Path(project_out)
    for name in ("scene/building_built.json", "building_agent.json", "building_final.json", "building.json"):
        data = _read_json(out / name)
        if isinstance(data, dict) and data.get("levels"):
            return data
    return None


def load_sheets(project_out) -> Optional[dict]:
    out = Path(project_out)
    for cand in (out / "sheets.json", out.parent.parent / "sheets.json" if out.parent.name == "variants" else None):
        if cand is not None and cand.is_file():
            return _read_json(cand)
    return None


def _font(size: int, bold: bool = False):
    from PIL import ImageFont
    try:
        return ImageFont.truetype(FONT_BOLD if bold else FONT, max(6, int(size)))
    except OSError:
        try:
            return ImageFont.load_default(size=max(6, int(size)))
        except Exception:  # noqa: BLE001 - very old Pillow
            return ImageFont.load_default()


# --------------------------------------------------------------------------
# The model's elements (pure)
# --------------------------------------------------------------------------

def area_built(building: dict, area: dict) -> bool:
    """A ``site.areas`` label record is built when it says ``build: true`` or a surface (paving, parking, grass,
    pools) or a platform of the site was made from it (``area_id``) and is not ``build: false``."""
    if not isinstance(area, dict):
        return False
    if area.get("build") is True:
        return True
    aid = area.get("id")
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    for key in ("paving", "parking", "grass", "pools", "platforms", "terraces"):
        for s in site.get(key) or []:
            if isinstance(s, dict) and aid and s.get("area_id") == aid and s.get("build") is not False:
                return True
    return False


def piece_built(piece: dict) -> bool:
    from wenart.agent import topdown as TD
    return bool(TD.is_built(piece))


def element_index(building: dict) -> dict:
    """``{id: {"cat", "level_id", "type", "built", "label", "record"}}`` of every element a claim may name: rooms,
    walls, openings, furniture (built or not), symbols (not furniture), site areas (built or not), surfaces (paving,
    parking, grass, pools), platforms and levels."""
    idx: dict = {}

    def put(eid, cat, level_id, etype, built, label, rec):
        if eid and eid not in idx:
            idx[str(eid)] = {"cat": cat, "level_id": level_id, "type": etype, "built": bool(built),
                             "label": label, "record": rec}

    for lv in building.get("levels") or []:
        put(lv.get("id"), "level", lv.get("id"), lv.get("kind") or "floor", True, lv.get("label"), lv)
    for r in building.get("rooms") or []:
        put(r.get("id"), "room", r.get("level_id"), r.get("room_type"), r.get("build") is not False,
            r.get("label_raw") or r.get("label") or r.get("name"), r)
    for w in building.get("walls") or []:
        put(w.get("id"), "wall", w.get("level_id"), "wall", w.get("build") is not False, None, w)
    for o in building.get("openings") or []:
        put(o.get("id"), "opening", o.get("level_id"), o.get("type"), o.get("build") is not False, None, o)
    for f in building.get("furniture") or []:
        put(f.get("id"), "piece", f.get("level_id"), f.get("type"), piece_built(f), f.get("type_raw"), f)
    for s in building.get("symbols") or []:
        put(s.get("id"), "symbol", s.get("level_id"), s.get("kind"), False, None, s)
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    for a in site.get("areas") or []:
        if isinstance(a, dict):
            put(a.get("id"), "area", a.get("level_id"), a.get("kind"), area_built(building, a),
                a.get("label_raw") or a.get("label"), a)
    for key in ("paving", "parking", "grass", "pools", "terraces"):
        for s in site.get(key) or []:
            if isinstance(s, dict):
                put(s.get("id"), "surface", s.get("level_id"), key, s.get("build") is not False, None, s)
    for p in site.get("platforms") or []:
        if isinstance(p, dict):
            put(p.get("id"), "platform", p.get("level_id"), p.get("kind") or "platform", p.get("build") is not False,
                None, p)
    return idx


def _evidence_texts(rec: dict) -> list[str]:
    return [str(e.get("text")) for e in rec.get("evidence") or [] if isinstance(e, dict) and e.get("text")]


def source_labels(building: dict, level_id: str) -> list[dict]:
    """The labels the reading read on the level's plan: ``[{"element", "cat", "label", "area_m2", "texts"}]`` for
    every room (its name, the area it states, the other texts it carries) and every site area of the level."""
    out = []
    for r in building.get("rooms") or []:
        if r.get("level_id") != level_id:
            continue
        texts = _evidence_texts(r)
        area = r.get("area_label") if isinstance(r.get("area_label"), (int, float)) else None
        out.append({"element": r.get("id"), "cat": "room", "label": r.get("label_raw") or r.get("label") or "",
                    "area_m2": area, "texts": texts})
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    for a in site.get("areas") or []:
        if not isinstance(a, dict) or a.get("level_id") not in (level_id, None):
            continue
        texts = _evidence_texts(a)
        area = next((stated_area(t) for t in texts if stated_area(t) is not None), None)
        out.append({"element": a.get("id"), "cat": "area", "label": a.get("label_raw") or a.get("label") or "",
                    "area_m2": area, "texts": texts})
    return out


def match_label(building: dict, level_id: Optional[str], text: Any, *, kind: Optional[str] = None,
                idx: Optional[dict] = None, by_words: bool = True) -> Optional[dict]:
    """The model record a claim's label (or its message's space word) names: ``{"id", "cat", "built", "how",
    "label"}`` or None. Site areas first (their label or evidence texts share a name word, or the same space word),
    then rooms (label or evidence texts: a room that carries a merged label, e.g. a dining part of the living room).
    With ``level_id`` only records of that level (or of none); ``by_words`` False (a message, not a label): the
    space word only."""
    idx = idx if idx is not None else element_index(building)
    words = name_words(text) if by_words else set()
    sword = space_word(text)
    if not words and not sword:
        return None
    cands = []
    for eid, e in idx.items():
        if e["cat"] not in ("area", "room"):
            continue
        rec = e["record"]
        texts = [e.get("label") or "", rec.get("label") or "", *_evidence_texts(rec)]
        rwords = set().union(*(name_words(t) for t in texts)) if texts else set()
        how = None
        if words and words & rwords:
            how = "label"
        elif sword and any(space_word(t) == sword for t in texts if t):
            how = "space word"
        elif e["cat"] == "room" and sword and e["type"] == "balcony" and sword in ("balcony", "terrace"):
            how = "room type"
        if how is None:
            continue
        if kind == "room" and e["cat"] == "area" and how != "label":
            continue
        if level_id and e["level_id"] not in (level_id, None):
            continue
        rank = (0 if e["cat"] == "area" and (kind in (None, "space")) else 1, 0 if how == "label" else 1, eid)
        cands.append((rank, {"id": eid, "cat": e["cat"], "built": e["built"], "how": how,
                             "label": e.get("label") or rec.get("label"), "level_id": e["level_id"]}))
    if not cands:
        return None
    cands.sort(key=lambda c: c[0])
    return cands[0][1]


def text_in(label: Any, texts: Iterable[str]) -> bool:
    """A claim's label is a text of the plan: a name word in common (or the same stated area)."""
    words = name_words(label)
    area = stated_area(label)
    for t in texts:
        if words and words & name_words(t):
            return True
        if area is not None and stated_area(t) is not None and abs(stated_area(t) - area) < 0.01:
            return True
    return False


def drawn_in_source(rec: dict, regions: set) -> Optional[str]:
    """The evidence entity that puts an element in the source drawing (vector evidence of one of ``regions``, or
    a piece ``from_documents``), else None."""
    if rec.get("source") == "from_documents":
        ev = next((e for e in rec.get("evidence") or [] if isinstance(e, dict)), {})
        return str(ev.get("entity") or "from_documents")
    for e in rec.get("evidence") or []:
        if isinstance(e, dict) and e.get("method") == "vector" and e.get("entity") \
                and (not regions or e.get("region_id") in regions or e.get("region_id") is None):
            return str(e["entity"])
    return None


# --------------------------------------------------------------------------
# Routing: owner and fix
# --------------------------------------------------------------------------

def actions() -> dict:
    from wenart.blender.architect_actions import ACTIONS
    return ACTIONS


def owner_of(kind: str, change: str, aspect: str, cat: Optional[str], etype: Optional[str],
             recorded: bool = True) -> str:
    """The stage that owns a difference (module docstring)."""
    if kind == "space":
        return "site" if recorded else "reading"
    if kind == "room":
        return "architect" if change == "different_in_model" and aspect == "type" else "reading"
    if kind in ("door", "window"):
        return "reading" if change == "missing_in_model" and cat != "opening" else "openings"
    if kind in ("fixture", "furniture"):
        return "furniture"
    if kind == "level":
        if cat == "opening":
            return "architect"
        if cat in ("area", "surface", "platform"):
            return "site"
    return "reading"


def fix_of(kind: str, change: str, aspect: str, cat: Optional[str], etype: Optional[str]) -> Optional[str]:
    """The AI architect's action that carries the fix out, or None (only actions of ``ACTIONS``)."""
    act = None
    if kind in ("fixture", "furniture") and cat == "piece":
        if change == "extra_in_model":
            act = "remove_piece"
        elif aspect == "type":
            act = "retype_piece"
        elif aspect in ("position", "orientation"):
            act = "move_piece"
        elif aspect == "height" and kind == "fixture":
            act = "mount_fixture"
    elif kind == "room" and cat == "room" and change == "different_in_model" and aspect == "type":
        act = "retype_room"
    elif kind == "door" and cat == "opening":
        if etype == "opening" and change != "extra_in_model":
            act = "gap_to_door"
        elif etype == "window" and change != "extra_in_model":
            act = "window_to_door"
        elif etype == "door" and change == "different_in_model":
            act = {"type": "door_type", "size": "widen_door"}.get(aspect)
        elif etype == "door" and change == "extra_in_model":
            act = "door_to_window"
    elif kind == "window" and cat == "opening":
        if etype == "door" and change != "missing_in_model":
            act = "door_to_window"
        elif etype == "window" and change == "different_in_model" and aspect == "position":
            act = "move_window_to_outer_wall"
    elif kind == "level" and cat == "opening" and etype == "door":
        act = "snap_threshold"
    return act if act in actions() else None


# --------------------------------------------------------------------------
# Drawing the source (plan_image, elevation_image)
# --------------------------------------------------------------------------

def topdown_view(project_out, level_id: str) -> dict:
    """The model's top-down view of a level: ``{"azimuth_deg", "tilt_deg", "source"}`` from
    ``topdown/top_<level>.png.frame.json``, else ``wenart.blender.topdown``'s defaults."""
    fr = _read_json(Path(project_out) / "topdown" / f"top_{level_id}.png.frame.json") if project_out else None
    if isinstance(fr, dict) and fr.get("azimuth_deg") is not None:
        return {"azimuth_deg": float(fr.get("azimuth_deg") or 0.0), "tilt_deg": float(fr.get("tilt_deg") or 0.0),
                "source": "frame.json"}
    from wenart.blender import topdown as BT
    return {"azimuth_deg": float(BT.AZIMUTH_DEG), "tilt_deg": float(BT.TILT_DEG), "source": "topdown defaults"}


def seen_from(azimuth_deg: float) -> str:
    from wenart.report.topdown_labels import seen_from as sf
    return sf(azimuth_deg)


def _project_dirs(building: dict, project_out: Optional[Path]) -> list[Path]:
    folder = (building.get("project") or {}).get("source_folder")
    out = []
    if folder:
        p = Path(folder)
        if p.is_absolute():
            out.append(p)
        else:
            out += [Path.cwd() / p, Path(__file__).resolve().parents[2] / p]
    if project_out is not None:
        out.append(Path(project_out))
    return out


def _source_path(doc: dict, page: dict, building: dict, project_out: Optional[Path]) -> Optional[Path]:
    """The file to draw a page from: the converted DXF of a DWG (``<out>/converted``, converted there with
    LibreDWG when missing), the document itself, or None."""
    from wenart.vision_check import plan_crop as PC
    for pdir in _project_dirs(building, project_out):
        path = PC.source_file(doc, pdir, project_out or pdir, page)
        if path is not None:
            return path
    if doc.get("format") == "dwg" and project_out is not None:
        for pdir in _project_dirs(building, project_out):
            dwg = pdir / doc["file"]
            if dwg.is_file():
                try:
                    from wenart.ingest import dwg as DWG
                    return DWG.convert(dwg, Path(project_out) / "converted").dxf_path
                except Exception:  # noqa: BLE001 - no converter here: the fallbacks take over
                    return None
    return None


def _read_vector_page(doc: dict, page: dict, path: Path, region_box=None):
    """The ``GenericPage`` of a vector page (DXF model space or a vector PDF page), cut to its region."""
    from wenart.ingest import dxf_generic as DG
    fmt = doc.get("format")
    box = region_box if region_box is not None else page.get("region_box")
    if fmt in ("dxf", "dwg"):
        return DG.read_page(path, doc.get("file") or path.name, region_box=box if box else None)
    if fmt == "pdf":
        from wenart.ingest import cad_pdf
        gp = cad_pdf.read_page(path, int(page.get("page") or 1), doc.get("file") or path.name)
        return DG.clip_page(gp, box) if box else gp
    return None


def _projector(view: Optional[dict]):
    """Building metres -> drawing plane (u right, v up) of the view: turned by the azimuth so the view's direction
    points up, foreshortened by the tilt along it (the floor plane of ``wenart.blender.topdown``'s ortho camera)."""
    if not view:
        return lambda x, y: (x, y)
    az = math.radians(float(view.get("azimuth_deg") or 0.0))
    k = math.cos(math.radians(float(view.get("tilt_deg") or 0.0)))
    ca, sa = math.cos(az), math.sin(az)
    return lambda x, y: (x * ca - y * sa, (x * sa + y * ca) * k)


def keep_text(text: str) -> bool:
    """A text worth drawing: not a bare integer (dimension figures, tread numbers) and not empty."""
    t = str(text or "").strip()
    return bool(t) and not _BARE_INT.match(t)


def _is_label(text: str) -> bool:
    return len(_LETTERS.findall(str(text or ""))) >= 2


def render_drawing(strokes: Sequence, texts: Sequence, to_m: Sequence[float], frame_m: Sequence[float], *,
                   view: Optional[dict] = None, title: Sequence[str] = (), max_side: int = IMAGE_MAX_SIDE,
                   arrow: bool = False, core_m: Optional[Sequence[float]] = None, skip: Iterable[str] = ()):
    """``(image, placed_texts)``: the strokes and texts of a page (page units) drawn in the frame ``(x0, y0, x1,
    y1)`` in metres (``to_m``: page units -> metres), turned and foreshortened like ``view`` (None: as drawn).
    Lines are drawn ``SUPERSAMPLE`` times larger and scaled down (smooth lines); walls (wall-hint layers, fills)
    darker; texts upright with a white halo, labels first, a text that would cover a drawn one moves a line or is
    left out. ``core_m``: the walls' box; a long straight line that crosses it and runs on past both its sides (a
    grid axis, a section cut line) is left out (``axis_line``), and so are the strokes of ``skip`` (the dimension
    lines: ``dimension_strokes``)."""
    from PIL import Image, ImageDraw

    from wenart.ingest.dxf_generic import is_wall_hint_layer

    proj = _projector(view)
    x0, y0, x1, y1 = (float(v) for v in frame_m)
    corners = [proj(x0, y0), proj(x1, y0), proj(x1, y1), proj(x0, y1)]
    umin, umax = min(c[0] for c in corners), max(c[0] for c in corners)
    vmin, vmax = min(c[1] for c in corners), max(c[1] for c in corners)
    du, dv = max(umax - umin, 1e-6), max(vmax - vmin, 1e-6)
    title_h = TITLE_H if title else 0
    s = min((max_side - 2 * PAD_PX) / du, (max_side - 2 * PAD_PX - title_h) / dv)
    w = int(round(du * s + 2 * PAD_PX))
    h = int(round(dv * s + 2 * PAD_PX + title_h))
    ss = SUPERSAMPLE

    def px(x, y, k=1.0):
        u, v = proj(x, y)
        return ((PAD_PX + (u - umin) * s) * k, (title_h + PAD_PX + (vmax - v) * s) * k)

    def page_to_m(p):
        return G.apply_affine(to_m, p)

    big = Image.new("RGB", (w * ss, h * ss), "white")
    dr = ImageDraw.Draw(big)
    fills, lines = [], []
    skip = set(skip or ())
    for st in strokes:
        if st.id in skip:
            continue
        pts_m = [page_to_m(p) for p in st.pts]
        if not pts_m:
            continue
        bx0, by0 = min(p[0] for p in pts_m), min(p[1] for p in pts_m)
        bx1, by1 = max(p[0] for p in pts_m), max(p[1] for p in pts_m)
        if bx1 < x0 or bx0 > x1 or by1 < y0 or by0 > y1:
            continue
        wall = is_wall_hint_layer(getattr(st, "layer", None))
        if not wall and axis_line(pts_m, core_m):
            continue
        if getattr(st, "fill", None) is not None and st.closed and len(pts_m) >= 3:
            fills.append((pts_m, st.fill, wall))
        lines.append((pts_m, bool(st.closed), wall))
    for pts_m, fill, _wall in fills:
        dark = sum(fill) / 3.0 < 0.5
        dr.polygon([px(*p, k=ss) for p in pts_m], fill=DARK_FILL if dark else FILL_GREY)
    for pts_m, closed, wall in lines:
        pts = [px(*p, k=ss) for p in pts_m]
        if closed and len(pts) > 2:
            pts = pts + [pts[0]]
        if len(pts) < 2 or pts[0] == pts[-1] and len(pts) == 2:
            continue
        dr.line(pts, fill=WALL_INK if wall else LINE_GREY, width=(2 if wall else 1) * ss)
    img = big.resize((w, h), Image.LANCZOS)
    # everything outside the frame (a turned frame leaves corners of other drawings) is white
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon([px(x, y) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))], fill=255)
    img = Image.composite(img, Image.new("RGB", (w, h), "white"), mask)
    dr = ImageDraw.Draw(img)
    mpu = math.sqrt(abs(to_m[0] * to_m[4] - to_m[1] * to_m[3])) or 1.0
    placed, boxes = [], []
    blocks = text_blocks([t for t in texts if keep_text(t.text)])
    blocks.sort(key=lambda bl: (0 if any(_is_label(t.text) for t in bl) else 1,
                                -max(float(t.height or 0.0) for t in bl)))
    for bl in blocks:
        centres = [page_to_m(((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0)) for t in bl]
        inside = [(t, c) for t, c in zip(bl, centres) if x0 <= c[0] <= x1 and y0 <= c[1] <= y1]
        if not inside:
            continue
        cx = sum(c[0] for _t, c in inside) / len(inside)
        cy = sum(c[1] for _t, c in inside) / len(inside)
        label = any(_is_label(t.text) for t, _c in inside)
        size = max(float(t.height or 0.0) for t, _c in inside) * mpu * s * 1.15
        size = max(13 if label else 11, min(24, size))
        font = _font(size, bold=label)
        body = "\n".join(str(t.text) for t, _c in inside)       # the drawing's own line order (a label block)
        x, y = px(cx, cy)
        spot = None
        for dy in (0.0, 1.0, -1.0, 2.0, -2.0):          # a text that would cover a drawn one moves a line
            box = dr.multiline_textbbox((x, y + dy * size), body, font=font, anchor="mm", align="center",
                                        stroke_width=2)
            if not any(_overlap(box, b) > 0.1 for b in boxes):
                spot = (y + dy * size, box)
                break
        if spot is None:
            continue
        boxes.append(spot[1])
        dr.multiline_text((x, spot[0]), body, font=font, fill=INK, anchor="mm", align="center", stroke_width=2,
                          stroke_fill=(255, 255, 255))
        placed += [{"id": t.id, "text": str(t.text), "at": [round(c[0], 3), round(c[1], 3)]} for t, c in inside]
    if arrow and view:
        _plan_up_arrow(dr, proj, w, h)
    if title:
        dr.rectangle((0, 0, w, title_h), fill=(30, 30, 30))
        dr.text((10, 5), str(title[0]), font=_font(17, bold=True), fill=(255, 255, 255))
        if len(title) > 1:
            dr.text((10, 27), str(title[1])[:160], font=_font(12), fill=(225, 225, 225))
    return img, placed


def text_blocks(texts: Sequence) -> list[list]:
    """The texts in blocks of lines stacked in the drawing (page units: a room name with its area under it), each
    block top line first; a turned image draws a block upright in this order (pure). Two lines stack when their
    centres are within ``STACK_DX`` x the wider one's width across and ``STACK_DY`` x the taller one's height
    apart."""
    n = len(texts)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    geo = []
    for t in texts:
        b = t.box
        h = max(float(t.height or 0.0), abs(b[3] - b[1]) * 0.8)
        geo.append(((b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0, abs(b[2] - b[0]), h))
    by_y = sorted(range(n), key=lambda k: geo[k][1])
    reach = STACK_DY * max((g[3] for g in geo), default=0.0)
    for a, i in enumerate(by_y):                         # a sweep up the page: only lines within reach
        for j in by_y[a + 1:]:
            if geo[j][1] - geo[i][1] > reach:
                break
            (xi, yi, wi, hi), (xj, yj, wj, hj) = geo[i], geo[j]
            h = max(hi, hj)
            if h > 0 and abs(xi - xj) <= STACK_DX * max(wi, wj) and abs(yi - yj) <= STACK_DY * h:
                parent[find(i)] = find(j)
    groups: dict = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return [[texts[i] for i in sorted(ix, key=lambda k: -geo[k][1])] for ix in groups.values()]


def dimension_strokes(page) -> set:
    """The ids of the strokes that draw the page's dimensions (``wenart.ingest.generic.scale.find_dimensions``:
    a figure with its marked line) on layers where dimensions make at least ``DIM_LAYER_SHARE`` of the strokes (a
    wall face or a window line the finder used as a mark stays); empty when the finder fails."""
    try:
        from wenart.ingest.generic import scale as SC
        dims = SC.find_dimensions(page)
    except Exception:  # noqa: BLE001 - a page the finder cannot read keeps its lines
        return set()
    ids = {i for d in dims for i in d.stroke_ids}
    total: dict = {}
    hit: dict = {}
    for st in page.strokes:
        total[st.layer] = total.get(st.layer, 0) + 1
        if st.id in ids:
            hit[st.layer] = hit.get(st.layer, 0) + 1
    layers = {k for k, n in hit.items() if n >= DIM_LAYER_SHARE * total.get(k, 1)}
    return {st.id for st in page.strokes if st.id in ids and st.layer in layers}


def axis_line(pts_m: Sequence, core_m: Optional[Sequence[float]]) -> bool:
    """A straight line of at least ``AXIS_MIN_M`` whose two ends lie ``AXIS_OUT_M`` outside the walls' box and
    that crosses it: a grid axis or a section cut line, never a wall (pure)."""
    if core_m is None or len(pts_m) != 2:
        return False
    (ax, ay), (bx, by) = pts_m[0], pts_m[1]
    if math.hypot(bx - ax, by - ay) < AXIS_MIN_M:
        return False
    x0, y0, x1, y1 = (float(v) for v in core_m)
    m = AXIS_OUT_M

    def outside(x, y):
        return x < x0 - m or x > x1 + m or y < y0 - m or y > y1 + m

    if not (outside(ax, ay) and outside(bx, by)):
        return False
    from shapely.geometry import LineString, box
    return LineString([(ax, ay), (bx, by)]).intersects(box(x0, y0, x1, y1))


def _overlap(a, b) -> float:
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    small = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1])) or 1.0
    return ix * iy / small


def _plan_up_arrow(dr, proj, w: int, h: int) -> None:
    """An arrow in the lower right corner: where the drawing's up (+Y of the building frame) points."""
    ux, uy = proj(0.0, 1.0)
    ox, oy = proj(0.0, 0.0)
    dx, dy = ux - ox, -(uy - oy)
    n = math.hypot(dx, dy) or 1.0
    dx, dy = dx / n, dy / n
    cx, cy, r = w - 70, h - 60, 34
    a, b = (cx - dx * r, cy - dy * r), (cx + dx * r, cy + dy * r)
    dr.line((a, b), fill=ARROW_RGB, width=4)
    left = (b[0] - dx * 12 - dy * 8, b[1] - dy * 12 + dx * 8)
    right = (b[0] - dx * 12 + dy * 8, b[1] - dy * 12 - dx * 8)
    dr.polygon((b, left, right), fill=ARROW_RGB)
    dr.text((cx, cy + r + 4), "plan up", font=_font(12, bold=True), fill=ARROW_RGB, anchor="mt",
            stroke_width=2, stroke_fill=(255, 255, 255))


def level_frame(building: dict, level_id: str, texts_m: Sequence[dict] = (), margin: float = FRAME_MARGIN_M
                ) -> Optional[list[float]]:
    """``[x0, y0, x1, y1]`` metres: the level's walls, rooms and site areas plus ``margin``, grown to take in the
    plan's labels within ``LABEL_REACH_M`` of them (a veranda's label outside the walls)."""
    pts = []
    for w in building.get("walls") or []:
        if w.get("level_id") == level_id:
            pts += [w.get("start"), w.get("end")]
    for r in building.get("rooms") or []:
        if r.get("level_id") == level_id:
            pts += list(r.get("polygon") or [])
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    for a in site.get("areas") or []:
        if isinstance(a, dict) and a.get("level_id") == level_id:
            pts += list(a.get("polygon") or []) + ([a["anchor"]] if a.get("anchor") else [])
    pts = [p for p in pts if p is not None and len(p) >= 2]
    if not pts:
        return None
    x0, y0 = min(p[0] for p in pts) - margin, min(p[1] for p in pts) - margin
    x1, y1 = max(p[0] for p in pts) + margin, max(p[1] for p in pts) + margin
    for t in texts_m:
        if not _is_label(t.get("text")):
            continue
        tx, ty = t["at"]
        if x0 - LABEL_REACH_M <= tx <= x1 + LABEL_REACH_M and y0 - LABEL_REACH_M <= ty <= y1 + LABEL_REACH_M:
            x0, y0 = min(x0, tx - LABEL_PAD_M), min(y0, ty - LABEL_PAD_M)
            x1, y1 = max(x1, tx + LABEL_PAD_M), max(y1, ty + LABEL_PAD_M)
    return [round(v, 3) for v in (x0, y0, x1, y1)]


def walls_box(building: dict, level_id: str) -> Optional[list[float]]:
    """The box of the level's walls (metres), or None."""
    pts = [p for w in building.get("walls") or [] if w.get("level_id") == level_id
           for p in (w.get("start"), w.get("end")) if p]
    if not pts:
        return None
    return [min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)]


def _level_label(building: dict, level_id: str) -> str:
    lv = next((lv for lv in building.get("levels") or [] if lv.get("id") == level_id), {})
    return str(lv.get("label") or "")


def plan_image(project_out, level_id: str, *, building: Optional[dict] = None, out_path=None,
               orient: str = "view", max_side: int = IMAGE_MAX_SIDE) -> dict:
    """The source plan of one level as an image (module docstring): ``{"path", "level_id", "method": "strokes" |
    "raster" | "region" | "debug_image" | None, "orient": "view" | "plan", "view", "file", "page", "region_id",
    "frame_m", "texts": [{"id", "text", "at"}], "note"}``; ``path`` None when no source could be drawn (the note says
    why). A level whose page has no transform to the building gets the sheets' region of the level (``sheets.json``
    ``levels[].base_region``, as drawn) or its page's debug image."""
    from wenart.vision_check import plan_crop as PC

    out = Path(project_out)
    building = building if building is not None else load_building(out)
    rec: dict = {"path": None, "level_id": level_id, "method": None, "orient": orient, "view": None, "file": None,
                 "page": None, "region_id": None, "frame_m": None, "texts": [], "note": ""}
    if not building:
        rec["note"] = "no building JSON in the project output"
        return rec
    dest = Path(out_path) if out_path else out / AUDIT_DIR / f"plan_{level_id}.png"
    label = _level_label(building, level_id)
    found = PC.plan_page(building, level_id, None)
    if found is None:
        sheets = load_sheets(out)
        lvl = next((x for x in (sheets or {}).get("levels") or [] if x.get("id") == level_id), {})
        if lvl.get("base_region"):
            got = region_image(out, lvl["base_region"], building=building, sheets=sheets, out_path=dest,
                               max_side=max_side, title=f"SOURCE PLAN  {level_id}  {label}".rstrip())
            if got.get("path"):
                rec.update(path=got["path"], method="region" if got["method"] == "strokes" else got["method"],
                           orient="plan", region_id=lvl["base_region"], texts=got.get("texts") or [],
                           note=f"no page of level {level_id} with a transform to the building: the sheets' "
                                f"region {lvl['base_region']}, as drawn")
                return rec
        page = next((p for d in building.get("documents") or [] for p in d.get("pages") or []
                     if p.get("level_id") == level_id and p.get("debug_image")), None)
        if page is not None and _debug_fallback(out, page, dest, level_id, label, max_side):
            rec.update(path=str(dest), method="debug_image", orient="plan", region_id=page.get("region_id"),
                       note=f"no page of level {level_id} with a transform to the building: its debug image")
            return rec
        rec["note"] = f"no page of level {level_id} with a transform to the building, no region, no debug image"
        return rec
    doc, page = found
    rec.update(file=doc.get("file"), page=page.get("page"), region_id=page.get("region_id"))
    view = topdown_view(out, level_id) if orient == "view" else None
    rec["view"] = view
    to_m = list(page["transform_to_building"])
    notes = []
    if not page.get("rectified_image") and page.get("kind", "vector") == "vector":
        try:
            path = _source_path(doc, page, building, out)
            gp = _read_vector_page(doc, page, path) if path is not None else None
        except Exception as exc:  # noqa: BLE001 - an unreadable source: the fallbacks take over
            gp, path = None, None
            notes.append(f"source not read ({exc})")
        if gp is not None:
            texts_m = [{"id": t.id, "text": t.text,
                        "at": list(G.apply_affine(to_m, ((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0)))}
                       for t in gp.texts if keep_text(t.text)]
            frame = level_frame(building, level_id, texts_m)
            if frame is not None:
                where = f"{doc.get('file')}" + (f" region {page.get('region_id')}" if page.get("region_id") else "") \
                    + (f" page {page.get('page')}" if doc.get("format") == "pdf" else "")
                turn = (f"turned like the model view (seen from the {seen_from(view['azimuth_deg'])}, "
                        f"{view['tilt_deg']:g} deg from above)" if view else "as drawn (building frame)")
                title = (f"SOURCE PLAN  {level_id}  {label}".rstrip(),
                         f"{where}: the drawing's own lines and texts (dimension figures left out), {turn}")
                img, placed = render_drawing(gp.strokes, gp.texts, to_m, frame, view=view, title=title,
                                             max_side=max_side, arrow=bool(view),
                                             core_m=walls_box(building, level_id), skip=dimension_strokes(gp))
                dest.parent.mkdir(parents=True, exist_ok=True)
                img.save(dest)
                drawn = {t["id"] for t in placed}
                texts = [dict(t, at=[round(v, 3) for v in t["at"]], drawn=t["id"] in drawn) for t in texts_m
                         if frame[0] <= t["at"][0] <= frame[2] and frame[1] <= t["at"][1] <= frame[3]]
                rec.update(path=str(dest), method="strokes", frame_m=frame, texts=texts,
                           note="; ".join(notes + [f"{len(placed)} of {len(texts)} texts drawn"]))
                return rec
            notes.append("the level has no walls, rooms or site areas to frame")
        else:
            notes.append("no readable source file (DXF, DWG with a converter, vector PDF)")
    # a raster page (scan, photo): its rectified image cropped to the frame, as drawn
    try:
        frame = level_frame(building, level_id)
        path = _source_path(doc, page, building, out)
        if frame is not None and path is not None and (page.get("rectified_image") or doc.get("format") not in
                                                       ("dxf", "dwg")):
            raster = PC.load_raster(doc, page, path, out)
            inv = G.invert_affine(to_m)
            pts = [raster.to_pixels(G.apply_affine(inv, (x, y))) for x in (frame[0], frame[2])
                   for y in (frame[1], frame[3])]
            box = [max(0, int(min(p[0] for p in pts))), max(0, int(min(p[1] for p in pts))),
                   min(raster.image.width, int(max(p[0] for p in pts))),
                   min(raster.image.height, int(max(p[1] for p in pts)))]
            if box[2] - box[0] > 20 and box[3] - box[1] > 20:
                img = raster.image.crop(box)
                _save_titled(img, dest, (f"SOURCE PLAN  {level_id}  {label}".rstrip(),
                                         f"{doc.get('file')}: the page as drawn (not turned)"), max_side)
                rec.update(path=str(dest), method="raster", orient="plan", view=None, frame_m=frame,
                           note="; ".join(notes + ["raster page, cropped, not turned"]))
                return rec
    except Exception as exc:  # noqa: BLE001
        notes.append(f"raster not drawn ({exc})")
    if _debug_fallback(out, page, dest, level_id, label, max_side):
        rec.update(path=str(dest), method="debug_image", orient="plan", view=None,
                   note="; ".join(notes + ["the reading's debug image (annotated)"]))
        return rec
    rec["note"] = "; ".join(notes + ["no debug image either"])
    return rec


def _debug_fallback(out: Path, page: dict, dest: Path, level_id: str, label: str, max_side: int) -> bool:
    """The page's debug image of the reading, titled as such, at ``dest``; False without one."""
    dbg = out / str(page.get("debug_image") or "")
    if not page.get("debug_image") or not dbg.is_file():
        return False
    from PIL import Image
    with Image.open(dbg) as im:
        img = im.convert("RGB")
    _save_titled(img, dest, (f"SOURCE PLAN  {level_id}  {label} (the reading's debug image)".rstrip(),
                             "coloured lines and boxes are what the reading found, not the drawing"), max_side)
    return True


def _save_titled(img, dest: Path, title: Sequence[str], max_side: int) -> None:
    from PIL import Image, ImageDraw
    k = min(1.0, (max_side - TITLE_H) / max(img.width, img.height))
    if k < 1.0:
        img = img.resize((max(1, int(img.width * k)), max(1, int(img.height * k))), Image.LANCZOS)
    canvas = Image.new("RGB", (img.width, img.height + TITLE_H), "white")
    canvas.paste(img, (0, TITLE_H))
    dr = ImageDraw.Draw(canvas)
    dr.rectangle((0, 0, canvas.width, TITLE_H), fill=(30, 30, 30))
    dr.text((10, 5), str(title[0]), font=_font(17, bold=True), fill=(255, 255, 255))
    if len(title) > 1:
        dr.text((10, 27), str(title[1])[:160], font=_font(12), fill=(225, 225, 225))
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest)


# --------------------------------------------------------------------------
# Elevations and sections of sheets.json
# --------------------------------------------------------------------------

def elevation_regions(sheets: Optional[dict], building: Optional[dict] = None) -> list[dict]:
    """``[{"region_id", "class", "file", "page", "box", "metres_per_unit", "title", "side", "view_bearing_deg"}]``:
    the regions of ``sheets.json`` drawn as an elevation or a section (``class``), with the side the reading gave
    them (``building.facade.elevations``, else ``sheets.exterior.openings_seen``)."""
    from wenart.vision_check.elevation import drawn_elevations
    known: dict = {}
    for source in (building or {}, {}):            # the building's record first, then the sheets' own
        elevs, _src = drawn_elevations(source, sheets)
        for e in elevs:
            rid, side, bearing = e.get("region_id"), e.get("side"), e.get("view_bearing_deg")
            cur = known.setdefault(rid, {"side": None, "view_bearing_deg": None})
            if cur["side"] is None and side not in (None, "all"):
                cur["side"] = side
            if cur["view_bearing_deg"] is None and isinstance(bearing, (int, float)):
                cur["view_bearing_deg"] = bearing
    out = []
    for r in (sheets or {}).get("regions") or []:
        if not isinstance(r, dict) or r.get("class") not in ("elevation", "section") or r.get("ignored_reason"):
            continue
        e = known.get(r.get("id"), {})
        out.append({"region_id": r.get("id"), "class": r.get("class"), "file": r.get("file"), "page": r.get("page"),
                    "box": r.get("box"), "metres_per_unit": r.get("metres_per_unit"), "title": r.get("title"),
                    "side": e.get("side"), "view_bearing_deg": e.get("view_bearing_deg")})
    return out


def elevation_image(project_out, region_id: str, *, building: Optional[dict] = None, sheets: Optional[dict] = None,
                    out_path=None, max_side: int = IMAGE_MAX_SIDE) -> dict:
    """An elevation or section region of ``sheets.json`` as an image (``region_image``), at
    ``<out>/audit/elevation_<region>.png``."""
    dest = Path(out_path) if out_path else Path(project_out) / AUDIT_DIR / f"elevation_{region_id}.png"
    return region_image(project_out, region_id, building=building, sheets=sheets, out_path=dest, max_side=max_side)


def region_image(project_out, region_id: str, *, building: Optional[dict] = None, sheets: Optional[dict] = None,
                 out_path=None, max_side: int = IMAGE_MAX_SIDE, title: Optional[str] = None) -> dict:
    """A region of ``sheets.json`` as an image, from its strokes and texts in its own frame (its
    ``metres_per_unit``; ``{"path", "region_id", "method", "texts", "note"}``); the region's debug image when the
    source cannot be read."""
    out = Path(project_out)
    building = building if building is not None else (load_building(out) or {})
    sheets = sheets if sheets is not None else load_sheets(out)
    rec = {"path": None, "region_id": region_id, "method": None, "texts": [], "note": ""}
    region = next((r for r in (sheets or {}).get("regions") or [] if r.get("id") == region_id), None)
    if region is None:
        rec["note"] = f"no region {region_id} in sheets.json"
        return rec
    dest = Path(out_path) if out_path else out / AUDIT_DIR / f"region_{region_id}.png"
    doc = next((d for d in (sheets or {}).get("documents") or [] if d.get("file") == region.get("file")), None) \
        or next((d for d in building.get("documents") or [] if d.get("file") == region.get("file")), None) \
        or {"file": region.get("file"), "format": Path(str(region.get("file"))).suffix.lstrip(".").lower()}
    page = {"page": region.get("page"), "region_box": region.get("box"), "kind": "vector"}
    box = region.get("box")
    title = (title or (f"SOURCE {str(region.get('class') or 'elevation').upper()}  {region_id}"
                       + (f"  {region.get('title')}" if region.get("title") else "")),
             f"{region.get('file')} region {region_id}: the drawing's own lines and texts (dimension figures left "
             "out), as drawn")
    try:
        path = _source_path(doc, page, building, out)
        gp = _read_vector_page(doc, page, path, region_box=box) if path is not None and box else None
    except Exception as exc:  # noqa: BLE001
        gp = None
        rec["note"] = f"source not read ({exc}); "
    if gp is not None and box:
        mpu = float(region.get("metres_per_unit") or 1.0)
        to_m = [mpu, 0.0, -mpu * float(box[0]), 0.0, mpu, -mpu * float(box[1])]
        frame = [0.0, 0.0, mpu * (float(box[2]) - float(box[0])), mpu * (float(box[3]) - float(box[1]))]
        img, placed = render_drawing(gp.strokes, gp.texts, to_m, frame, title=title, max_side=max_side,
                                     skip=dimension_strokes(gp))
        dest.parent.mkdir(parents=True, exist_ok=True)
        img.save(dest)
        rec.update(path=str(dest), method="strokes", texts=placed)
        return rec
    for d in building.get("documents") or []:
        for p in d.get("pages") or []:
            if p.get("region_id") == region_id and p.get("debug_image") and (out / p["debug_image"]).is_file():
                from PIL import Image
                with Image.open(out / p["debug_image"]) as im:
                    img = im.convert("RGB")
                _save_titled(img, dest, title, max_side)
                rec.update(path=str(dest), method="debug_image")
                return rec
    rec["note"] += "no source and no debug image"
    return rec


def exterior_renders(project_out, scene: Optional[dict] = None, render_dir: str = "renders") -> dict:
    """``{view: {"image", "sides", "kind"}}`` of the exterior views (the scene manifest's exterior cameras, their
    ``<render_dir>/<view>_preview.jpg``, else the agent's previews); without a manifest every
    ``ext_*_preview.jpg`` (sides unknown)."""
    out = Path(project_out)
    scene = scene if scene is not None else (_read_json(out / "scene" / "scene_manifest.json")
                                             or _read_json(out / render_dir / "scene_manifest.json"))
    found: dict = {}
    dirs = [out / render_dir, out / "agent" / "previews"]
    for cam in (scene or {}).get("cameras") or []:
        if cam.get("kind") != "exterior" or cam.get("status") == "dropped" or cam.get("dropped_reason"):
            continue
        name = cam.get("name")
        img = next((d / f"{name}{suf}" for d in dirs for suf in ("_preview.jpg", ".png", ".jpg")
                    if (d / f"{name}{suf}").is_file()), None)
        if img is not None:
            found[name] = {"image": str(img), "sides": list(cam.get("sides") or []), "kind": cam.get("view")}
    if not found:
        for d in dirs:
            for img in sorted(d.glob("ext_*_preview.jpg")):
                found.setdefault(img.name[:-len("_preview.jpg")], {"image": str(img), "sides": [], "kind": None})
    return found


def _render_list(renders) -> list[dict]:
    items = []
    if isinstance(renders, dict):
        for k, v in renders.items():
            if isinstance(v, dict):
                items.append({"view": str(k), "image": v.get("image"), "sides": list(v.get("sides") or []),
                              "kind": v.get("kind")})
            elif v:
                items.append({"view": str(k), "image": str(v), "sides": [], "kind": None})
    else:
        for v in renders or []:
            if isinstance(v, dict) and v.get("view"):
                items.append({"view": str(v["view"]), "image": v.get("image"), "sides": list(v.get("sides") or []),
                              "kind": v.get("kind")})
    return [i for i in items if i.get("image") and Path(i["image"]).is_file()]


def exterior_sheet(views: Sequence[dict], dest: Path, max_side: int = IMAGE_MAX_SIDE) -> Path:
    """One image of every exterior view (2 columns, each tagged with its id and the sides it shows)."""
    from PIL import Image, ImageDraw
    cols = 2 if len(views) > 1 else 1
    rows = max(1, math.ceil(len(views) / cols))
    cw = max_side // cols
    tiles = []
    for v in views:
        with Image.open(v["image"]) as im:
            im = im.convert("RGB")
            k = cw / im.width
            tiles.append(im.resize((cw, max(1, int(im.height * k))), Image.LANCZOS))
    ch = max(t.height for t in tiles) if tiles else cw // 2
    sheet = Image.new("RGB", (cw * cols, ch * rows), "white")
    dr = ImageDraw.Draw(sheet)
    for i, (v, t) in enumerate(zip(views, tiles)):
        x, y = (i % cols) * cw, (i // cols) * ch
        sheet.paste(t, (x, y))
        tag = v["view"] + (f" ({', '.join(v['sides'])})" if v.get("sides") else "")
        dr.rectangle((x, y, x + 12 + 9 * len(tag), y + 24), fill=(30, 30, 30))
        dr.text((x + 6, y + 4), tag, font=_font(14, bold=True), fill=(255, 255, 255))
    if max(sheet.size) > max_side:
        k = max_side / max(sheet.size)
        sheet = sheet.resize((int(sheet.width * k), int(sheet.height * k)), Image.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(dest, quality=88)
    return dest


# --------------------------------------------------------------------------
# Facts of the model's level (the prompt)
# --------------------------------------------------------------------------

def _fmt_area(v) -> str:
    return f"{float(v):.2f}".replace(".", ",") if isinstance(v, (int, float)) else "?"


def level_facts(building: dict, level_id: str) -> list[str]:
    """The model's level as the prompt states it (one line each; capped at ``MAX_FACT_LINES``)."""
    lv = next((lv for lv in building.get("levels") or [] if lv.get("id") == level_id), {})
    lines = [f"Level {level_id} ({lv.get('label') or ''}): floor at {float(lv.get('elevation') or 0.0):+.2f} m, "
             f"ceiling {float(lv.get('ceiling_height') or 0.0):.2f} m."]
    rooms = [r for r in building.get("rooms") or [] if r.get("level_id") == level_id]
    lines.append("Rooms (id: name, type, area built / area the plan states; other labels it carries):")
    for r in rooms:
        texts = [t for t in _evidence_texts(r) if t and fold(t) != fold(r.get("label_raw") or r.get("label"))]
        stated = r.get("area_label")
        extra = [t for t in texts if stated_area(t) is None or abs((stated_area(t) or 0) - float(stated or -1)) > 0.01]
        lines.append(f"- {r.get('id')}: {r.get('label_raw') or r.get('label') or '-'}, {r.get('room_type')}, "
                     f"{_fmt_area(r.get('area_computed'))} m² built"
                     + (f" / {_fmt_area(stated)} m² stated" if isinstance(stated, (int, float)) else "")
                     + (f"; also {', '.join(extra[:4])}" if extra else ""))
    walls = {w.get("id"): w for w in building.get("walls") or []}
    ops = [o for o in building.get("openings") or [] if o.get("level_id") == level_id]
    if ops:
        lines.append("Doors, windows and openings (id: kind, width, wall):")
        for o in ops:
            w = walls.get(o.get("wall_id")) or {}
            bits = [str(o.get("type")), f"{float(o.get('width') or 0):.2f} m"]
            if o.get("operation"):
                bits.append(str(o["operation"]))
            if o.get("type") == "window" and o.get("sill_height") is not None:
                bits.append(f"sill {float(o['sill_height']):.2f} m")
            bits.append("outer wall" if w.get("exterior") else "inner wall")
            lines.append(f"- {o.get('id')}: {', '.join(bits)}")
    pieces = [f for f in building.get("furniture") or [] if f.get("level_id") == level_id]
    stairs = [f for f in pieces if f.get("type") == "stair" and piece_built(f)]
    if stairs:
        lines.append("Stairs: " + "; ".join(
            f"{f.get('id')} in {f.get('room_id')} ({len((f.get('stair') or {}).get('flights') or [])} flights)"
            for f in stairs))
    lines.append("Built pieces per room (id type, source):")
    for r in rooms:
        built = [f for f in pieces if f.get("room_id") == r.get("id") and piece_built(f) and f.get("type") != "stair"]
        if built:
            tag = {"from_documents": "drawn", "added_by_ai": "added", "adjusted_by_ai": "drawn, adjusted"}
            items = [f"{f.get('id')} {f.get('type')} ({tag.get(f.get('source'), f.get('source') or '?')})"
                     for f in built[:MAX_PIECES_PER_ROOM]]
            more = len(built) - len(items)
            lines.append(f"- {r.get('id')}: " + ", ".join(items) + (f", +{more} more" if more > 0 else ""))
    unbuilt = [f for f in pieces if not piece_built(f)]
    if unbuilt:
        lines.append("Drawn but NOT built (in no image of the model): " + ", ".join(
            f"{f.get('id')} {f.get('type')}" for f in unbuilt[:20]))
    syms = [s for s in building.get("symbols") or [] if s.get("level_id") == level_id]
    if syms:
        lines.append("Drawn symbols that are not furniture (not built): " + ", ".join(
            f"{s.get('id')} {s.get('kind')}" for s in syms[:12]))
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    areas = [a for a in site.get("areas") or [] if isinstance(a, dict) and a.get("level_id") in (level_id, None)]
    lines.append("Outdoor and open spaces the plan labels (site areas):" + ("" if areas else " none"))
    for a in areas:
        texts = ", ".join(_evidence_texts(a)[:3])
        lines.append(f"- {a.get('id')}: {a.get('label_raw') or a.get('label')} ({texts}), kind {a.get('kind')}: "
                     + ("BUILT" if area_built(building, a) else "NOT BUILT (only its label is recorded)"))
    surfaces = []
    for key in ("platforms", "paving", "parking", "pools", "terraces"):
        for s in site.get(key) or []:
            if isinstance(s, dict) and s.get("level_id") in (level_id, None) and s.get("build") is not False:
                surfaces.append(f"{s.get('id')} {key[:-1] if key.endswith('s') else key}"
                                + (f" from {s.get('area_id')}" if s.get("area_id") else ""))
    if surfaces:
        lines.append("Built outdoor surfaces and platforms: " + ", ".join(surfaces[:12]))
    ents = [e for e in site.get("entrances") or [] if isinstance(e, dict) and e.get("level_id") == level_id]
    if ents:
        lines.append("Steps and landings outside the doors (built): " + "; ".join(
            f"{e.get('door_id')}: {e.get('solution')}"
            + (f" {((e.get('steps') or {}).get('count'))} risers" if e.get("steps") else "")
            + (" (drawn)" if e.get("drawn") else " (inferred)") for e in ents[:10]))
    marks = [m for m in building.get("level_marks") or [] if isinstance(m, dict) and m.get("level_id") == level_id]
    if marks:
        lines.append("Level marks of the plan: " + ", ".join(
            f"{m.get('raw')} ({m.get('kind')}" + (f" {m.get('room_id')}" if m.get("room_id") else "")
            + (f" {m.get('door_id')}" if m.get("door_id") else "") + ")" for m in marks[:12]))
    if len(lines) > MAX_FACT_LINES:
        lines = lines[:MAX_FACT_LINES - 1] + [f"... {len(lines) - MAX_FACT_LINES + 1} more lines left out"]
    return lines


def plan_text_lines(building: dict, level_id: str, plan: Optional[dict]) -> list[str]:
    """The labels of the plan: the ones the reading kept (rooms, site areas: their texts) and the plan's other
    texts with letters (when the plan was drawn from its strokes)."""
    out, seen = [], set()
    for lab in source_labels(building, level_id):
        texts = [t for t in lab["texts"] if t] or [lab["label"]]
        out.append(f"- {' / '.join(texts[:4])} -> {lab['element']}")
        seen |= {fold(t) for t in texts}
    others = []
    for t in (plan or {}).get("texts") or []:
        f = fold(t.get("text"))
        if f and f not in seen and _is_label(t.get("text")) and len(_LETTERS.findall(t.get("text") or "")) >= 3:
            seen.add(f)
            others.append(str(t.get("text")))
    if others:
        out.append("- other texts on the plan: " + ", ".join(others[:MAX_PLAN_TEXTS]))
    return out


# --------------------------------------------------------------------------
# audit_level
# --------------------------------------------------------------------------

def _str_prop(n: int) -> dict:
    return {"type": "string", "maxLength": n}


PLAN_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["differences"],
    "properties": {"differences": {"type": "array", "maxItems": MAX_CLAIMS, "items": {
        "type": "object", "additionalProperties": False,
        "required": ["kind", "change", "aspect", "label", "room", "target", "severity", "message"],
        "properties": {"kind": {"enum": list(KINDS)}, "change": {"enum": list(CHANGES)},
                       "aspect": {"enum": list(ASPECTS)}, "label": _str_prop(60), "room": _str_prop(60),
                       "target": _str_prop(80), "severity": {"enum": list(SEVERITIES)},
                       "message": {"type": "string", "minLength": 3, "maxLength": 300}}}}}}


def plan_prompt(building: dict, level_id: str, plan: dict, facts: list[str], labels: list[str]) -> str:
    method = plan.get("method")
    if method == "strokes" and plan.get("view"):
        img1 = ("Image 1 is the SOURCE PLAN of level {lv}: the architect's drawing (its own lines and texts), turned "
                "and foreshortened like image 2 so every room is in the same place in both images; the red arrow "
                "shows where the drawing's up points.").format(lv=level_id)
    elif method == "debug_image":
        img1 = (f"Image 1 is the source plan of level {level_id} with the reading's marks drawn over it (coloured "
                "lines and boxes are what a program read, not the drawing; judge the grey drawing under them). It is "
                "not turned like image 2.")
    else:
        img1 = f"Image 1 is the SOURCE PLAN of level {level_id} (the architect's drawing), as drawn, not turned."
    return "\n".join([
        img1,
        f"Image 2 is the 3D MODEL of level {level_id} seen from above at an angle: ceilings off, walls cut low, every "
        "room named, windows as blue lines with their ids.",
        "", "The model's facts (from code; copy ids exactly from here):", *facts,
        "", "Labels written on the plan (vector texts; '-> id' is the model record that carries the label):",
        *(labels or ["- none"]),
        "", "Task: compare the plan with the model and list EVERY difference:",
        "- something the plan shows that the model lacks or has differently: a space (veranda, terrace, balcony, "
        "porch, loggia, courtyard), a room, a stair, a door or a window, a wall, fixed equipment (kitchen run, "
        "island, sanitary ware, built-ins), a drawn piece of furniture, a level or a step;",
        "- something the model has that the plan does not show.",
        "Fields: kind = what it is; change = missing_in_model | different_in_model | extra_in_model; aspect = what "
        "differs (presence for missing or extra); label = the plan's text for it copied exactly, or \"\"; room = the "
        "id of the room it is in, or \"\"; target = the model id concerned, copied from the facts (\"\" when the "
        "model has nothing there, \"building\" for the whole level); severity: critical = a whole space, room or "
        "level missing or wrong, major = a door, window, stair, wall or fixture missing or wrong, minor = a detail; "
        "message = one sentence: what the plan shows and what the model has.",
        "Not differences: furniture the model added to complete a room ('added'), colours, materials, styles, the "
        "camera angle. Only list what you can point at in image 1. If the model matches the plan, answer "
        "{\"differences\": []}."])


def audit_level(model, building: dict, level_id: str, *, plan, topdown, call_id: str,
                project_out=None) -> dict:
    """One level, documents vs model (module docstring). ``plan``: ``plan_image``'s record or an image path;
    ``topdown``: the model's top-down image (``renders/top_<level>_plan.jpg``). Returns ``{"line", "level",
    "call_id", "images", "kept": [findings], "dropped": [{"claim", "reason"}], "error"}``; no call without both
    images (``error`` says which is missing)."""
    plan_rec = plan if isinstance(plan, dict) else {"path": str(plan) if plan else None, "method": "image",
                                                    "texts": [], "view": None}
    po = Path(project_out) if project_out else None
    images = [plan_rec.get("path"), str(topdown) if topdown else None]
    rec = {"line": LINE_PLAN, "level": level_id, "call_id": call_id,
           "images": [_rel(i, po) for i in images], "kept": [], "dropped": [], "error": None,
           "plan_method": plan_rec.get("method")}
    missing = [n for n, p in zip(("plan", "top-down view"), images) if not p or not Path(p).is_file()]
    if missing:
        rec["error"] = f"no {' and no '.join(missing)} image of level {level_id}: not audited"
        return rec
    facts = level_facts(building, level_id)
    labels = plan_text_lines(building, level_id, plan_rec)
    prompt = plan_prompt(building, level_id, plan_rec, facts, labels)
    messages = [{"role": "system", "content": AUDIT_SYSTEM},
                user_message(prompt, images, [f"Image 1: the source plan of level {level_id}",
                                              f"Image 2: the 3D model of level {level_id} from above"])]
    reply = model.structured(messages, PLAN_SCHEMA, call_id=call_id, name="audit", kind="audit",
                             thinking=bool(getattr(model, "critic_thinking", False)), max_tokens=AUDIT_MAX_TOKENS)
    if reply.data is None:
        rec["error"] = "; ".join(reply.errors[:3]) or "no answer"
        return rec
    plan_texts = [t.get("text") for t in plan_rec.get("texts") or []] \
        if plan_rec.get("method") in ("strokes", "region") else None
    regions = {r for r in (plan_rec.get("region_id"),) if r}
    kept, dropped = check_plan_claims(reply.data.get("differences") or [], building, level_id,
                                      plan_texts=plan_texts, regions=regions, call_id=call_id,
                                      images=rec["images"])
    rec.update(kept=kept, dropped=dropped)
    return rec


def _finding(line: str, kind: str, change: str, aspect: str, severity: str, target: str, message: str, *,
             level: Optional[str], images: Sequence, label: str, room: Optional[str], call_id: str, n: int,
             cat: Optional[str], etype: Optional[str], recorded: bool = True, extra: Optional[dict] = None) -> dict:
    ev = {"level": level, "plan_image": images[0] if images else None,
          "model_image": images[1] if len(images) > 1 else None, "label": label or None, "kind": kind,
          "change": change, "aspect": aspect, "room": room, "call_id": call_id, "claim": n}
    ev.update(extra or {})
    return {"line": line, "check": CHECK_OF_KIND.get(kind, "B9"), "severity": severity, "target": target or "building",
            "message": message, "evidence": ev, "owner": owner_of(kind, change, aspect, cat, etype, recorded),
            "fix": fix_of(kind, change, aspect, cat, etype)}


def _claim(item: dict) -> dict:
    return {k: (item.get(k).strip() if isinstance(item.get(k), str) else item.get(k)) for k in item}


def _resolve_target(target: str, idx: dict) -> tuple[Optional[str], Optional[dict]]:
    """``(id, element)`` a claim's target names (exact, else case-insensitive), ``(None, None)`` for no target;
    ``(target, None)`` when it names nothing of the model."""
    if target.lower() in NO_TARGET:
        return None, None
    if target in idx:
        return target, idx[target]
    hit = next((k for k in idx if k.lower() == target.lower()), None)
    return (hit, idx[hit]) if hit else (target, None)


def _space_area(label: str, el: Optional[dict]) -> Optional[float]:
    """The area a missing space's label states, else the one its record's texts state."""
    area = stated_area(label)
    if area is None and el is not None:
        area = next((stated_area(t) for t in _evidence_texts(el["record"]) if stated_area(t) is not None), None)
    return area


def check_plan_claims(claims: Sequence[dict], building: dict, level_id: str, *, plan_texts: Optional[list] = None,
                      regions: Optional[set] = None, call_id: str = "", images: Sequence = ()
                      ) -> tuple[list[dict], list[dict]]:
    """``(kept findings, dropped claims)`` of one level's answer (module docstring: the code checks)."""
    idx = element_index(building)
    rooms = {r.get("id"): r for r in building.get("rooms") or [] if r.get("level_id") == level_id}
    kept, dropped, seen = [], [], {}
    for n, raw in enumerate(claims, start=1):
        c = _claim(raw)
        kind, change, aspect = c.get("kind"), c.get("change"), c.get("aspect") or "presence"
        label, room = c.get("label") or "", c.get("room") or ""
        severity, message = c.get("severity") or "minor", c.get("message") or ""
        notes: list = []

        def drop(why: str, raw=raw, n=n) -> None:
            dropped.append({"line": LINE_PLAN, "level": level_id, "claim": dict(raw), "n": n, "reason": why,
                            "call_id": call_id})

        # 1. the id: it exists, is on this level and fits the kind
        target, el = _resolve_target(c.get("target") or "", idx)
        if target is not None and el is None:
            drop(f"target {target!r} is not an id of the model")
            continue
        if el is not None:
            if el["level_id"] not in (level_id, None):
                drop(f"target {target} is on level {el['level_id']}, not {level_id}")
                continue
            if el["cat"] == "symbol":                    # a drawn symbol is an unbuilt piece of the plan
                el = dict(el, cat="piece", built=False)
            if el["cat"] not in KIND_TARGETS.get(kind, ()):
                drop(f"a {kind} claim on {el['cat']} {target} ({el['type']})")
                continue
            if kind == "stair" and el["cat"] == "piece" and el["type"] != "stair":
                drop(f"a stair claim on {target}, a {el['type']}")
                continue
        # 2. the room: an id of this level (a room's name is read as its id), else ignored
        if room and room not in rooms:
            hit = match_label(building, level_id, room, kind="room", idx=idx)
            if hit and hit["id"] in rooms:
                notes.append(f"room {room!r} read as {hit['id']}")
                room = hit["id"]
            else:
                notes.append(f"room {room!r} is no room of {level_id}: ignored")
                room = ""
        if not room and el is not None:
            room = (el["record"].get("room_id") if el["cat"] == "piece" else target if el["cat"] == "room" else "")
            room = room or ""
        # 3. a labelled space or room: matched with the site areas and rooms by its label (the space word for a
        #    space without a label); another kind's label only places it in a room
        match = None
        if el is None and kind in ("space", "room") and (label or kind == "space"):
            match = match_label(building, level_id, label or message, kind=kind, idx=idx, by_words=bool(label))
        elif el is None and label and not room:
            hit = match_label(building, level_id, label, kind="room", idx=idx)
            if hit and hit["id"] in rooms:
                room = hit["id"]
                notes.append(f"label {label!r} is in room {room}")
        if el is None and match is not None:
            target, el = match["id"], idx[match["id"]]
            notes.append(f"matched {target} by {match['how']}")
        cat, etype, recorded = (el or {}).get("cat"), (el or {}).get("type"), True
        # 4. what the change claims, against what the model has
        if change == "missing_in_model":
            if el is not None:
                if (el["cat"] == "room" and kind == "room") or (el["cat"] != "room" and el["built"]):
                    drop(f"the model has built {target} ({el['type']})"
                         + (f": it carries the claim's label (matched by {match['how']})" if match else ""))
                    continue
                if not el["built"]:
                    notes.append(f"{target} is not built")
            elif label:
                if plan_texts is not None and not text_in(label, plan_texts):
                    drop(f"the label {label!r} is no text of the plan (its texts are read as vector)")
                    continue
                recorded = False
                notes.append("no record of it in the model (the reading missed it)")
            elif not room:
                drop("names nothing the code can check (no id, no room, no label)")
                continue
        elif change == "extra_in_model":
            if el is None:
                drop("an extra claim must name the model's element (no id)")
                continue
            if not el["built"]:
                drop(f"{target} is not built: nothing extra in the model")
                continue
            if el["cat"] == "piece" and el["record"].get("source") == "added_by_ai":
                drop(f"{target} was added by the furniture rules (added_by_ai): not a difference with the plan")
                continue
            drawn = drawn_in_source(el["record"], regions or set())
            if drawn:
                drop(f"{target} is drawn in the source ({drawn})")
                continue
        else:                                            # different_in_model
            if el is not None and not el["built"]:
                change = "missing_in_model"
                notes.append(f"{target} is not built: missing in the model")
            elif el is None:
                if not room:
                    drop("names nothing the code can check (no id, no room, no label)")
                    continue
                cat, etype = "room", rooms[room].get("room_type")
        where = target or room or "building"
        key = (CHECK_OF_KIND.get(kind), where, change, aspect, fold(label))
        if key in seen:
            drop(f"the same claim as claim {seen[key]}")
            continue
        seen[key] = n
        if kind == "space" and change == "missing_in_model" and severity == "minor":
            area = _space_area(label, el)
            if area is not None and area >= MAJOR_AREA_M2:
                severity = "major"
                notes.append(f"major: a labelled space of {area:g} m2")
        kept.append(_finding(LINE_PLAN, kind, change, aspect, severity, where, message, level=level_id,
                             images=images, label=label, room=room or None, call_id=call_id, n=n, cat=cat,
                             etype=etype, recorded=recorded,
                             extra={"matched": target, "built": (el or {}).get("built"), "notes": notes or None}))
    return kept, dropped


# --------------------------------------------------------------------------
# audit_elevations
# --------------------------------------------------------------------------

ELEVATION_SCHEMA_ITEM = {
    "type": "object", "additionalProperties": False,
    "required": ["kind", "change", "aspect", "label", "target", "drawn_count", "model_count", "drawn_roof",
                 "model_roof", "severity", "message"],
    "properties": {"kind": {"enum": list(ELEVATION_KINDS)}, "change": {"enum": list(CHANGES)},
                   "aspect": {"enum": list(ASPECTS)}, "label": _str_prop(60), "target": _str_prop(80),
                   "drawn_count": {"type": "integer", "minimum": -1, "maximum": 60},
                   "model_count": {"type": "integer", "minimum": -1, "maximum": 60},
                   "drawn_roof": {"enum": list(ROOF_FORMS)}, "model_roof": {"enum": list(ROOF_FORMS)},
                   "severity": {"enum": list(SEVERITIES)},
                   "message": {"type": "string", "minLength": 3, "maxLength": 300}}}


def elevation_schema(views: Sequence[str]) -> dict:
    return {"type": "object", "additionalProperties": False, "required": ["view", "differences"],
            "properties": {"view": {"enum": [*views, "none"]},
                           "differences": {"type": "array", "maxItems": MAX_CLAIMS, "items": ELEVATION_SCHEMA_ITEM}}}


def side_counts(building: dict, out_dir) -> dict:
    """``{"window": n, "door": n, "by_level": {level: {"window", "door"}}}``: the model's openings on the outer
    walls facing ``out_dir`` (within 45 degrees)."""
    from wenart.vision_check import exterior as EXT
    from wenart.vision_check.elevation import facing
    counts = {"window": 0, "door": 0, "by_level": {}}
    for _oid, info in EXT.outer_openings(building).items():
        if info.get("outward") is None or not facing(info["outward"], out_dir):
            continue
        t = info.get("type")
        if t not in ("window", "door"):
            continue
        counts[t] += 1
        lv = counts["by_level"].setdefault(info.get("level_id"), {"window": 0, "door": 0})
        lv[t] += 1
    return counts


def _dir_of_side(side: Optional[str], north: float):
    from wenart.blender import site as S
    return S.side_direction(side, north) if side else None


def _elev_dir(elev: dict, north: float):
    from wenart.vision_check.elevation import elevation_out
    d, _how = elevation_out({"side": elev.get("side"), "view_bearing_deg": elev.get("view_bearing_deg")}, north)
    return d


def views_for(elev: dict, views: Sequence[dict], north: float) -> list[dict]:
    """The exterior views that show the elevation's side (a single-side view first, then corners)."""
    from wenart.vision_check.elevation import facing
    d = _elev_dir(elev, north)
    if d is None:
        return []
    hits = []
    for v in views:
        dirs = [_dir_of_side(s, north) for s in v.get("sides") or []]
        if any(x is not None and facing(x, d) for x in dirs):
            hits.append((0 if len(dirs) == 1 else 1, v["view"], v))
    return [h[2] for h in sorted(hits, key=lambda h: (h[0], h[1]))]


def elevation_facts(building: dict, elev: dict, north: float, sides: Sequence[str] = ()) -> list[str]:
    from wenart.agent.critic_vision import roof_note, storeys_of
    lines = [f"The model has {storeys_of(building)} storey(s): " + ", ".join(
        f"{lv.get('id')} floor {float(lv.get('elevation') or 0):+.2f} m" for lv in building.get("levels") or []) + ".",
        roof_note(building)]
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    spaces = [a for a in site.get("areas") or [] if isinstance(a, dict)]
    balconies = [r for r in building.get("rooms") or [] if r.get("room_type") == "balcony"]
    lines.append("Open-air spaces of the documents: " + (", ".join(
        f"{a.get('id')} {a.get('label_raw') or a.get('label')} on {a.get('level_id')}: "
        + ("built" if area_built(building, a) else "NOT BUILT") for a in spaces)
        + "".join(f", {r.get('id')} balcony room on {r.get('level_id')}: built" for r in balconies)
        if spaces or balconies else "none."))
    d = _elev_dir(elev, north)
    if d is not None:
        c = side_counts(building, d)
        lines.append(f"The model's openings facing this side ({elev.get('side') or 'by bearing'}): {c['window']} "
                     f"windows, {c['door']} doors (" + "; ".join(
                         f"{k}: {v['window']} windows, {v['door']} doors" for k, v in sorted(c["by_level"].items()))
                     + ").")
    for s in sides:
        ds = _dir_of_side(s, north)
        if ds is not None:
            c = side_counts(building, ds)
            lines.append(f"The model's openings on its {s} side: {c['window']} windows, {c['door']} doors.")
    return lines


def elevation_prompt(elev: dict, views: Sequence[dict], sheet: bool, facts: list[str]) -> str:
    what = "a SECTION (a cut through the building)" if elev.get("class") == "section" else "an ELEVATION"
    side = elev.get("side") or ("by its bearing" if elev.get("view_bearing_deg") is not None else None)
    if sheet:
        img2 = ("Image 2 shows every exterior render of the 3D model, each tagged with its view id and the sides it "
                "shows. First find the render that shows the same side as the drawing (view = its id, or none).")
    else:
        img2 = f"Image 2 is the exterior render {views[0]['view']} of the 3D model ({', '.join(views[0]['sides'])})."
    kinds = ("floors, roof, level" if elev.get("class") == "section" else
             "floors, roof, window, door, space (balcony, veranda, terrace, porch), stair, wall, level")
    return "\n".join([
        f"Image 1 is {what} of the architect's drawings, region {elev.get('region_id')}"
        + (f" ({elev.get('title')})" if elev.get("title") else "")
        + (f", the {side} side" if side else ", side not known") + ".",
        img2, "", "The model's facts (from code):", *facts, "",
        f"Task: list every difference between the drawing (image 1) and the model (image 2 and the facts) in: {kinds}.",
        "Fields: kind; change = missing_in_model | different_in_model | extra_in_model; aspect = what differs; "
        "label = the drawing's text for it, or \"\"; target = a model id from the facts, or \"\"; drawn_count and "
        "model_count = the counts compared (storeys for floors; windows or doors on this side), -1 when no count; "
        "drawn_roof and model_roof = the roof forms for a roof difference, none otherwise; severity: critical = a "
        "storey, the roof form or a whole balcony, veranda or terrace missing or wrong, major = a row of windows or "
        "doors, a stair, minor = a detail; message = one sentence.",
        "Not differences: colours, materials, the sky, the ground, trees, the camera, details of window frames. Only "
        "list what you can point at in image 1. If the model matches, answer with no differences."])


def check_elevation_claims(claims: Sequence[dict], building: dict, elev: dict, *, north: float,
                           view: Optional[dict], call_id: str, images: Sequence) -> tuple[list[dict], list[dict]]:
    """``(kept findings, dropped claims)`` of one elevation's answer (module docstring: the code checks)."""
    from wenart.agent.critic_vision import roof_record, storeys_of
    idx = element_index(building)
    storeys = storeys_of(building)
    roof = roof_record(building)
    side_dir = _elev_dir(elev, north)
    if side_dir is None and view and len(view.get("sides") or []) == 1:
        side_dir = _dir_of_side(view["sides"][0], north)
    counts = side_counts(building, side_dir) if side_dir is not None else None
    kept, dropped, seen = [], [], {}
    for n, raw in enumerate(claims, start=1):
        c = _claim(raw)
        kind, change, aspect = c.get("kind"), c.get("change"), c.get("aspect") or "presence"
        label, target = c.get("label") or "", c.get("target") or ""
        severity, message = c.get("severity") or "minor", c.get("message") or ""
        dc, mc = int(c.get("drawn_count", -1)), int(c.get("model_count", -1))
        notes, cat, etype, recorded = [], None, None, True

        def drop(why: str, raw=raw, n=n) -> None:
            dropped.append({"line": LINE_ELEVATIONS, "region": elev.get("region_id"), "claim": dict(raw), "n": n,
                            "reason": why, "call_id": call_id})

        if elev.get("class") == "section" and kind not in ("floors", "roof", "level"):
            drop(f"a section is compared for floors, roof and levels only (a {kind} claim)")
            continue
        rec_t = None
        if target.lower() not in NO_TARGET and target != (view or {}).get("view"):
            rec_t = idx.get(target)
            if rec_t is None:
                drop(f"target {target!r} is not an id of the model")
                continue
            if kind in KIND_TARGETS and KIND_TARGETS[kind] and rec_t["cat"] not in KIND_TARGETS[kind]:
                drop(f"a {kind} claim on {rec_t['cat']} {target} ({rec_t['type']})")
                continue
            cat, etype = rec_t["cat"], rec_t["type"]
        else:
            target = ""
        if kind == "floors":
            if mc >= 0 and mc != storeys:
                drop(f"the model has {storeys} storey(s) (code); the claim reads {mc}")
                continue
            if dc >= 0 and dc == storeys:
                drop(f"no difference: the drawing's {dc} storey(s) are built")
                continue
            if dc < 0:
                drop("a floors claim without the drawn count")
                continue
        elif kind == "roof":
            built = roof.get("type")
            if built and c.get("model_roof") not in (None, "none", "other") and c["model_roof"] != built:
                drop(f"the model's roof is built as {built} (code record); the claim reads {c['model_roof']}")
                continue
            if built and c.get("drawn_roof") == built:
                drop(f"no difference: the drawing's {built} roof is built")
                continue
            if built and roof.get("drawn_type") == built and c.get("drawn_roof") not in (None, "none", "other"):
                drop(f"the reading of the drawings gives a {built} roof (vector; {roof.get('source')}) and the "
                     f"model builds it; the claim reads the drawing as {c['drawn_roof']} (AI vision)")
                continue
        elif kind in ("window", "door") and aspect == "count":
            if counts is None:
                notes.append("count not checked: the side is not known")
            else:
                have = counts[kind]
                if dc >= 0 and dc == have:
                    drop(f"no difference: the model has {have} {kind}s on this side, as drawn")
                    continue
                if mc >= 0 and abs(mc - have) > COUNT_TOL:
                    drop(f"the model has {have} {kind}s on this side (code); the claim reads {mc}")
                    continue
                notes.append(f"the model has {have} {kind}s on this side")
        elif kind == "space":
            match = None
            if rec_t is None:
                match = match_label(building, None, label or message, kind="space", idx=idx, by_words=bool(label))
            el = rec_t if rec_t is not None else (idx[match["id"]] if match else None)
            if match is not None:
                target, cat, etype = match["id"], match["cat"], el["type"]
                notes.append(f"matched {target} by {match['how']}")
            if change == "missing_in_model":
                if el is not None and el["built"]:
                    drop(f"the model has built {target} ({el['type']})"
                         + (f": it carries the claim's {match['how']}" if match else ""))
                    continue
                if el is None:
                    recorded = False
                    notes.append("no record of it in the model (the reading missed it)")
            elif el is None:
                if change == "extra_in_model":
                    drop("an extra claim must name the model's element (no id)")
                    continue
            elif not el["built"]:
                if change == "extra_in_model":
                    drop(f"{target} is not built: nothing extra in the model")
                    continue
                change = "missing_in_model"
                notes.append(f"{target} is not built: missing in the model")
        elif change == "extra_in_model" and rec_t is None and kind in ("window", "door", "stair", "wall"):
            drop("an extra claim must name the model's element (no id)")
            continue
        key = (kind, target, change, aspect, label)
        if key in seen:
            drop(f"the same claim as claim {seen[key]}")
            continue
        seen[key] = n
        if kind == "space" and change == "missing_in_model" and severity == "minor":
            severity = "major"
            notes.append("major: a whole open-air space")
        kept.append(_finding(LINE_ELEVATIONS, kind, change, aspect, severity, target or "building", message,
                             level=None, images=images, label=label, room=None, call_id=call_id, n=n, cat=cat,
                             etype=etype, recorded=recorded,
                             extra={"region": elev.get("region_id"), "region_class": elev.get("class"),
                                    "side": elev.get("side"), "view": (view or {}).get("view"),
                                    "drawn_count": dc if dc >= 0 else None, "model_count": mc if mc >= 0 else None,
                                    "drawn_roof": c.get("drawn_roof"), "model_roof": c.get("model_roof"),
                                    "notes": notes or None}))
    return kept, dropped


def audit_elevations(model, building: dict, *, sheets: Optional[dict], renders, call_id: str, project_out=None,
                     drawings: Optional[dict] = None) -> dict:
    """The elevations and sections vs the exterior renders (module docstring). ``renders``: ``exterior_renders``'
    mapping ``{view: {"image", "sides", "kind"}}`` (or ``{view: path}``); ``drawings``: ``{region_id: image}``
    (else made by ``elevation_image`` under ``project_out``). Returns ``{"line", "call_id", "regions": [{region
    record}], "kept", "dropped", "calls", "note"}``."""
    from wenart.blender import site as S
    po = Path(project_out) if project_out else None
    regions = elevation_regions(sheets, building)
    rec = {"line": LINE_ELEVATIONS, "call_id": call_id, "regions": [], "kept": [], "dropped": [], "calls": 0,
           "note": None}
    if not regions:
        rec["note"] = "the project has no elevation or section drawings (sheets.json): nothing to compare"
        return rec
    views = _render_list(renders)
    if not views:
        rec["note"] = "no exterior render to compare the elevations with"
        rec["regions"] = [{"region_id": e["region_id"], "class": e["class"], "error": "no exterior render"}
                          for e in regions]
        return rec
    north, _src = S.north_deg(building)
    sheet_path = None
    for elev in regions:
        rid = elev["region_id"]
        rrec = {"region_id": rid, "class": elev["class"], "side": elev.get("side"), "view": None, "images": [],
                "kept": 0, "dropped": 0, "error": None}
        rec["regions"].append(rrec)
        img1 = (drawings or {}).get(rid)
        if img1 is None and po is not None:
            img1 = elevation_image(po, rid, building=building, sheets=sheets).get("path")
        if not img1 or not Path(img1).is_file():
            rrec["error"] = "no image of the drawing"
            continue
        match = views_for(elev, views, north)
        sheet = not match
        if sheet:
            if sheet_path is None:              # made once per audit, from this round's renders
                sheet_path = exterior_sheet(views, (po / AUDIT_DIR if po else Path(img1).parent)
                                            / f"exterior_views_{call_id}.jpg")
            img2, shown = str(sheet_path), views
        else:
            img2, shown = match[0]["image"], [match[0]]
        sides = sorted({s for v in shown for s in v.get("sides") or []}) if sheet else []
        facts = elevation_facts(building, elev, north, sides)
        prompt = elevation_prompt(elev, shown, sheet, facts)
        cid = f"{call_id}_{rid}"
        images = [str(img1), img2]
        rrec["images"] = [_rel(p, po) for p in images]
        messages = [{"role": "system", "content": AUDIT_SYSTEM},
                    user_message(prompt, images, [f"Image 1: the drawing {rid}",
                                                  "Image 2: " + ("every exterior render" if sheet
                                                                 else f"the render {shown[0]['view']}")])]
        reply = model.structured(messages, elevation_schema([v["view"] for v in shown]), call_id=cid, name="audit",
                                 kind="audit", thinking=bool(getattr(model, "critic_thinking", False)),
                                 max_tokens=AUDIT_MAX_TOKENS)
        rec["calls"] += 1
        if reply.data is None:
            rrec["error"] = "; ".join(reply.errors[:3]) or "no answer"
            continue
        named = reply.data.get("view")
        view = next((v for v in shown if v["view"] == named), None) if sheet else shown[0]
        rrec["view"] = view["view"] if view else None
        kept, dropped = check_elevation_claims(reply.data.get("differences") or [], building, elev, north=north,
                                               view=view, call_id=cid, images=rrec["images"])
        rrec["kept"], rrec["dropped"] = len(kept), len(dropped)
        rec["kept"] += kept
        rec["dropped"] += dropped
    return rec


# --------------------------------------------------------------------------
# The roof against the roof plan (code, 27 Oct 2026)
# --------------------------------------------------------------------------

def roof_outline_findings(building: dict) -> list[dict]:
    """The roof's outline against the roof plan, measured by code (27 Oct 2026; user: "Make argus catch these kind of
    things before me", after the roof plan drew the roof over a balcony the model left open): the model review's
    ``roof_vs_plan`` (M11) on the roof the build makes (``roof.apply_override`` + ``roof.roof_model``), as B9 findings
    of this line (kind ``level``, aspect ``shape``, owner ``reading``; ``evidence.source`` ``code``). No model call:
    a drawing-vs-model claim that code measures needs no vision. [] when the building has no roof plan outline."""
    from wenart.blender import model_review as MR
    from wenart.blender import roof as R
    drawn = building.get("roof") if isinstance(building.get("roof"), dict) else None
    if drawn is None or not isinstance(drawn.get("roof_plan_outline"), dict):
        return []
    try:
        built, _changes = R.apply_override(drawn, R.override_of(building))
        got, _n = MR.roof_vs_plan(dict(building, roof=built), R.roof_model(built, building))
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return []
    out = []
    for n, f in enumerate(got, start=1):
        change = "missing_in_model" if f.get("kind") == "lost" else "different_in_model"
        rec = _finding(LINE_PLAN, "level", change, "shape", f["severity"], str(f.get("target") or "roof"),
                       f["message"], level=None, images=[], label="", room=f.get("room_id"), call_id="code_roof",
                       n=n, cat=None, etype="roof", extra={"source": "code", "model_review": f["check"],
                                                          "metrics": f.get("metrics")})
        rec["owner"], rec["kind"] = "reading", f.get("kind") or "misread"
        out.append(rec)
    return out


# --------------------------------------------------------------------------
# The whole project
# --------------------------------------------------------------------------

def audit_project(model, project_out, *, building: Optional[dict] = None, levels: Optional[Sequence[str]] = None,
                  call_prefix: str = "audit", render_dir: str = "renders") -> dict:
    """Every level that has a plan and a top-down view (``<render_dir>/top_<level>_plan.jpg``), then the
    elevations: ``{"findings", "dropped", "levels": [records], "elevations": record}``. 27 Oct 2026: the roof's
    outline against the roof plan first, by code (``roof_outline_findings``)."""
    out = Path(project_out)
    building = building if building is not None else load_building(out)
    res = {"findings": [], "dropped": [], "levels": [], "elevations": None}
    if not building:
        res["error"] = "no building JSON"
        return res
    res["findings"] += roof_outline_findings(building)
    for lv in building.get("levels") or []:
        lid = lv.get("id")
        if levels and lid not in levels:
            continue
        plan = plan_image(out, lid, building=building)
        top = out / render_dir / f"top_{lid}_plan.jpg"
        r = audit_level(model, building, lid, plan=plan, topdown=top, call_id=f"{call_prefix}_{lid}",
                        project_out=out)
        r["plan_note"] = plan.get("note")
        res["levels"].append(r)
        res["findings"] += r["kept"]
        res["dropped"] += r["dropped"]
    ev = audit_elevations(model, building, sheets=load_sheets(out),
                          renders=exterior_renders(out, render_dir=render_dir), call_id=f"{call_prefix}_elev",
                          project_out=out)
    res["elevations"] = ev
    res["findings"] += ev["kept"]
    res["dropped"] += ev["dropped"]
    return res
