"""The source ledger: line 1 of the auditor (26 Oct 2026). Every meaningful item of the source documents is accounted
for: an element of the model uses it, or an explicit, logged reason says why not. Anything else is a finding.

Why (the user, 26 Oct 2026): "the audit is very weak, only the looks being judged, everything needs to be judged.
There was a veranda in real06, it has been fully missed ... think to solve issues like veranda". real06's DWG holds
``VERANDA`` / ``22,80m²`` (TEXT:29585C / TEXT:29585D); the reading recorded a site area without an outline
(``build: false``) and a warning; nothing later looked at it and the veranda vanished silently. The fix is a rule for
every project: the model is checked against the full list of what the documents hold.

Inputs: the building JSON (``building.json`` or any later stage's building) and the inventory the pipeline writes
(``<out>/source_items.json``, ``wenart.ingest.source_items``). Pure code: no I/O in ``ledger``, no AI.

``ledger(building, source_items) -> {"items", "accounted", "findings", "coverage", "summary"}``.

Every source item gets a kind (``classify_text`` for texts: a space name, an outdoor-space name, a printed area or
size, a level mark, a furniture name, a dimension, a title / grid / note / opening tag text; blocks by their name:
furniture, door / window, vegetation, annotation; layers; hatches and closed outlines; pages). Items of kinds that
must be used (space and outdoor-space names, areas, level marks, furniture names and blocks, door / window and
vegetation blocks) on a plan page the pipeline read are accounted only when an element uses them (its
``evidence[].entity`` ids, ranges such as ``LINE:295900-295929`` and block paths such as ``INSERT:4B/3`` included)
and that element is built, or when a logged reason explains them. Items of the other kinds are counted, never
findings.

The checks (a finding names one):

- **A1 space not built** - a space name (a room label, or an outdoor space of ``OUTDOOR_SPACES``: veranda, teras,
  balkon, sundurma, porch, patio, deck, kış bahçesi, loggia, havuz, ... in Turkish, English, German, French, Italian
  and Spanish) that no built element uses: no room, no built site surface. Critical for a room label and for an
  outdoor space of the house (veranda, terrace, balcony, porch, patio, deck, loggia, winter garden, pergola, pool);
  major for parking and paving; minor for a garden (the ground stands for it). Its printed area and the unused
  layer and outline of the same space join the finding (the fix gets the outline as ``polygon_hint``).
- **A2 unbuilt element without a reason** - an element with drawn evidence and ``build: false`` whose reason does not
  explain it. For a space (a site area, a room) "no outline", "not a room", "recorded in site", "outside the
  walls" are no explanation: critical (major for parking / paving, minor for a garden). A piece needs any logged
  reason (its warning, its review entry, the symbol it moved to): major without one.
- **A3 label merged into another room** - a space name inside a built room whose own label is another one (it is in
  the room's evidence as a second label, or it lies in the room unused): the space the documents name is not a
  room of its own. Major; minor for an open-plan pair (dining in a living room or a kitchen, a kitchen or a hall in
  a living room), a shaft, or a space under ``SMALL_SPACE_M2`` (a niche). A room without a label of its own (an
  unlabelled face with its placeholder name) that holds the name is not named and typed by it: major (``label_room``).
- **A4 printed area not used** - an area text no element uses: minor when its space name is used (the area check is
  lost), major when it stands alone near the building (a space drawn with an area and no name).
- **A5 level mark not read** - a level mark text (``wenart.levels.marks``) of a read plan page that no level mark
  and no element uses. Major.
- **A6 named piece missing** - a furniture, door / window or vegetation block that no element uses, or a furniture
  name text with no built piece of that kind within ``NAME_NEAR_M`` (an untyped piece there gets a ``type_piece``
  fix). Major (other blocks: minor). Site decor of a kind the site does not build (``other``: grid bubbles, railings,
  sills read as decor) is a *weak* user: geometry and blocks only it records are not accounted for.
- **A7 reading drops something** - a reading warning that says something was left out, not used, dropped,
  skipped or "recorded ... not a room", that is not the logged reason of an element and that no other finding
  carries (a warning that names a flagged item joins that finding). Major when it names spaces or areas, critical
  for a level left out, else minor.
- **A8 page or level not read** - a level left out (``levels_left_out``): critical; a plan page or region that was
  not read for a reason other than the brief's variants: critical; a region of another use that holds room or area
  labels and was ignored: major.
- **A9 drawn geometry not used** - a hatch or closed outline of at least ``SURFACE_MIN_M2`` outside every built
  room, site surface and wall that no element uses (a surface the model may miss): major; a geometry layer of at
  least ``LAYER_MIN_ENTITIES`` entities on a read plan page none of which is used and that no warning names as a
  layer: major when its name says a building part (railing, balcony, stair, door, window, furniture, ...), minor
  otherwise. Annotation layers (dimensions, texts, axes, hatch patterns, level marks, the title block, the legend,
  layer ``0``; a layer whose texts are dimensions) are counted only. A layer named for an outdoor space (from
  ``OUTDOOR_LAYER_MIN`` entities) joins the A1 finding of that level instead; the hull of its drawing near the
  label (a veranda's railing) is the fix's ``polygon_hint`` when it is about as large as the printed area.

A finding: ``{"line": "source", "check": "A1".."A9", "severity": "critical" | "major" | "minor", "target": element
id or source item id, "message": what the documents say and what the model has, "evidence": {"file", "entity",
"layer", "text", "position", "level_id", "region_id"}, "owner": "reading" | "site" | "levels" | "sheets",
"fix": a typed action or None}``; merged findings keep the other checks in ``also`` and the warnings that name them
in ``warnings``.

CLI: ``python -m wenart.audit.ledger <out_dir> [--building building_final.json] [--json <path>]`` prints the
counts and the critical and major findings.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Optional

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from wenart import building as B
from wenart import units as U

LINE = "source"
SEVERITIES = ("critical", "major", "minor")
SEVERITY_RANK = {"critical": 0, "major": 1, "minor": 2}
CHECKS = ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9")
PLAN_CLASSES = ("floor_plan", "furniture_plan")
NAME_NEAR_M = 1.2               # a furniture name text and the piece it names
AREA_NEAR_M = 1.5               # an area text and the space name it belongs to
TABLE_FAR_M = 3.0               # an area text farther than this from every room is a table entry, not a space
SURFACE_MIN_M2 = 2.0            # A9: hatches and closed outlines smaller than this are counted only
LAYER_MIN_ENTITIES = 10         # A9: layers with fewer entities are counted only ...
OUTDOOR_LAYER_MIN = 3           # ... except a layer named for an outdoor space (BALKON, TERAS: a railing)
SMALL_SPACE_M2 = 1.5            # A3: a merged space smaller than this (a niche, a shaft) is minor
MAX_WORDS = 5                   # a longer text is a note
RANGE_MAX = 200000              # an entity range longer than this is not expanded

# Outdoor spaces (multi-language, on fold_ascii lower-case text): (kind, class, pattern). The class sets the
# severity of a space the model does not build: "house" critical, "site" major, "garden" minor.
OUTDOOR_SPACES: tuple[tuple[str, str, str], ...] = (
    ("veranda", "house", r"(?<![a-z])verandah?"),
    ("winter_garden", "house", r"(?<![a-z])kis bahce|winter ?garden|wintergarten|jardin d.hiver|conservatory|"
                               r"(?<![a-z])sun ?room"),
    ("terrace", "house", r"(?<![a-z])teras|(?<![a-z])terrace|(?<![a-z])terrass|(?<![a-z])terraz|(?<![a-z])terras|"
                         r"(?<![a-z])guneslenme|(?<![a-z])sun ?deck|(?<![a-z])sit ?out(?![a-z])|"
                         r"(?<![a-z])otla(?![a-z])"),
    ("balcony", "house", r"(?<![a-z])balkon|(?<![a-z])balcon|(?<![a-z])balcony"),
    ("porch", "house", r"(?<![a-z])sundurma|(?<![a-z])porch(?![a-z])|(?<![a-z])portico|(?<![a-z])porche|"
                       r"(?<![a-z])portique|(?<![a-z])vordach"),
    ("patio", "house", r"(?<![a-z])patio|(?<![a-z])avlu|(?<![a-z])court ?yard|(?<![a-z])innenhof|(?<![a-z])cortile"),
    ("deck", "house", r"(?<![a-z])deck(?:s|ing)?(?![a-z])"),
    ("loggia", "house", r"(?<![a-z])loggia|(?<![a-z])lodzie"),
    ("pergola", "house", r"(?<![a-z])pergola|(?<![a-z])gazebo|(?<![a-z])kameriye|(?<![a-z])cardak"),
    ("pool", "house", r"(?<![a-z])havuz|(?<![a-z])(?:swimming )?pool(?:s)?(?![a-z])|(?<![a-z])schwimmbad|"
                      r"(?<![a-z])piscin|(?<![a-z])pileta"),
    ("parking", "site", r"(?<![a-z])otopark|(?<![a-z])park yeri|(?<![a-z])car ?port|(?<![a-z])car porch|"
                        r"(?<![a-z])parking|(?<![a-z])stellplatz|(?<![a-z])parkplatz|(?<![a-z])garaj|"
                        r"(?<![a-z])garage"),
    ("paving", "site", r"(?<![a-z])kaldirim|(?<![a-z])paving|(?<![a-z])drive ?way|(?<![a-z])pflaster"),
    ("garden", "garden", r"(?<![a-z])bahce|(?<![a-z])garden|(?<![a-z])lawn|(?<![a-z])cim(?![a-z])|"
                         r"(?<![a-z])yesil alan|(?<![a-z])garten|(?<![a-z])rasen|(?<![a-z])jardin|(?<![a-z])pelouse|"
                         r"(?<![a-z])peyzaj|(?<![a-z])landscap"),
)
_OUTDOOR_RE = [(kind, cls, re.compile(p)) for kind, cls, p in OUTDOOR_SPACES]
CLASS_SEVERITY = {"house": "critical", "site": "major", "garden": "minor"}
# Texts that are entries of an area table, a title block or a note, never a space of the plan.
NOTE_RE = re.compile(r"(?<![a-z])(brut|net alan|net area|toplam|total|daire tipi|kat alani|insaat alani|emsal|taks|"
                     r"kaks|gross|carpet area|built ?up|plot area|parsel|pafta|olcek|scale|cizen|drawn by|proje|"
                     r"project|tarih|date|revizyon|revision|onay|mimar|architect|aciklama|legend|lejant|not:|note)"
                     r"(?![a-z])|=")
TURKISH_ROOM_MARKERS = re.compile(r"(?<![a-z])(oda|yemek|giyinme|soyunma|camasirlik|ofis|cocuk|misafir)")
# Open-plan pairs (sorted type pairs): a dining area in a living room, a kitchen in a living room, ...
OPEN_PLAN_PAIRS = {tuple(sorted(p)) for p in (("dining", "living"), ("dining", "kitchen"), ("kitchen", "living"),
                                              ("other", "living"), ("other", "kitchen"), ("hall", "living"))}
GRID_LAYER_RE = re.compile(r"aks|grid|axis|raster", re.I)
OPENING_TAG_LAYER_RE = re.compile(r"kapi|pencere|door|window|denizlik", re.I)
EXTRA_FURNITURE_WORDS = (("SIFONIYER", "dresser"), ("SIFONYER", "dresser"), ("KOMODIN", "nightstand"),
                         ("CAMASIR MAK", "washing_machine"), ("BULASIK MAK", "kitchen_counter"))
# Type families: a name text is matched by a built piece of the same family.
FAMILIES = {
    "bed": ("bed_single", "bed_double", "bunk_bed", "crib", "bed"),
    "seat": ("sofa", "sofa_corner", "armchair", "chaise", "ottoman", "bench", "seat"),
    "table": ("table_dining", "table_coffee", "side_table", "console_table", "desk", "table"),
    "storage": ("wardrobe", "dresser", "tall_cabinet", "sideboard", "shoe_cabinet", "display_cabinet", "bookshelf",
                "nightstand", "tv_unit", "wall_cabinet"),
    "kitchen": ("kitchen_counter", "kitchen_island", "sink_kitchen", "stove", "fridge"),
    "laundry": ("washing_machine",),
    "bath": ("bathtub", "shower"),
    "basin": ("washbasin",),
    "toilet": ("toilet",),
}
_FAMILY_OF = {t: fam for fam, types in FAMILIES.items() for t in types}

BLOCK_OPENING_RE = re.compile(r"(?<![A-Z])(KAPI|DOOR|PENCERE|WINDOW|WIN\d|DR\d|SURME|SLIDING|VASISTAS)", re.I)
BLOCK_TREE_RE = re.compile(r"AGAC|TREE|BITKI|PLANT|CICEK|FLOWER|CALI|SHRUB|PALM|CONIFER|BUSH|HEDGE|CIT(?![A-Z])",
                           re.I)
BLOCK_ANNOTATION_RE = re.compile(r"KOT|LEVEL|ELEV|NORTH|KUZEY|AKS|GRID|AXIS|KESIT|SECTION|TITLE|ANTET|FRAME|CERCEVE|"
                                 r"PAFTA|LOGO|DIM|ARROW|(?<![A-Z])OK(?![A-Z])|TAG|ETIKET|MARK|SEMBOL|SYMBOL|SCALE|"
                                 r"OLCEK|YON|PERSON|INSAN|HUMAN|CAR(?![A-Z])|ARABA|OTOMOBIL|VEHICLE", re.I)
FRAME_MIN_M = 30.0              # a block this large is the sheet frame or a site drawing, never a piece
ANNOTATION_LAYER_RE = re.compile(r"OLCU|DIM|YAZI|TEXT|AKS|GRID|AXIS|TARAMA|HATCH|KOT|KESIT|SECTION|ANTET|TITLE|"
                                 r"FRAME|CERCEVE|PAFTA|DEFPOINTS|VIEWPORT|(?<![A-Z])NOT(?![A-Z])|NOTE|LEJAN|LEGEND|"
                                 r"(?<![A-Z])POZ(?![A-Z])|ISIM|NAME|ETIKET|TAG|IZDUSUM|IZDOT",
                                 re.I)
BUILDING_PART_LAYER_RE = re.compile(r"KORKULUK|RAILING|PARAPET|BALKON|BALCON|TERAS|TERRAC|VERANDA|SUNDURMA|PORCH|"
                                    r"MERDIVEN|STAIR|KAPI|DOOR|PENCERE|WINDOW|DUVAR|WALL|KOLON|COLUMN|DOSEME|SLAB|"
                                    r"MOBILYA|TEFRIS|FURNIT|VITRIFIYE|SANITAR|HAVUZ|POOL|BAHCE|GARDEN|PEYZAJ|"
                                    r"LANDSCAPE|AGAC|TREE|ROOF|CATI", re.I)
DROP_WARNING_RE = re.compile(r"not built|not used|dropped|skipped|left out|leaves? out|ignored|not read|"
                             r"recorded in site|not a room|outside the (?:outer )?walls|outside the building|"
                             r"no closed face|removed", re.I)
REGION_USE_NOTE_RE = re.compile(r"read for the (?:exterior|heights|site)|by the sheets stage", re.I)
HARMLESS_WARNING_RE = re.compile(r"entity types not read: ATTDEF x\d+$|XCLIP boundar|AI front is not used", re.I)
SPACE_WARNING_RE = re.compile(r"\bareas?\b|room label|balcony|exterior label|terrace|veranda", re.I)
# A space that is not built is explained only by these reasons (a duplicate, a variant the brief leaves out, ...).
SPACE_EXPLAINED_RE = re.compile(r"duplicate|drawn twice|same as|variant|alternative|not selected|brief|user|"
                                r"neighbou?r|existing building|demolish", re.I)
# A plan page that is not read is explained only by these reasons (the brief's variants, the same drawing twice).
PAGE_EXPLAINED_RE = re.compile(r"variant|alternative|not select|same stem|same drawing|duplicate", re.I)
ID_HEAD_RE = re.compile(r"^([a-z]{1,4}_[A-Za-z0-9-]+(?:_[A-Za-z0-9]+)+):\s")
QUOTED_RE = re.compile(r"'([^']{1,60})'")
# A warning names a layer as a layer: "layer 'SIVA' chosen", "runner-up 'DUVAR'", "on the 'KAPI' layer(s)".
LAYER_NAMED_RE = re.compile(r"layers?(?:\(s\))?\s+'([^']{1,60})'|runner-up\s+'([^']{1,60})'|'([^']{1,60})'\s+layer",
                            re.I)
REASON_KEYS = ("not_built_reason", "reason", "note", "inferred_reason", "build_reason")
DATA_KEYS = ("level_marks", "levels", "conflicts", "documents", "needs_review", "unverified", "level_inference",
             "variants", "project")
SITE_LABEL_KEYS = ("areas",)
SITE_SKIP_SURFACE = ("areas", "decor", "openings", "boundary_walls", "entrances", "hedges", "buildings")


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def fold(text) -> str:
    """Folded lower-case text with single spaces (Turkish letters to ASCII)."""
    return " ".join(B.fold_ascii(str(text or "")).lower().replace("_", " ").split())


def top_entity(eid: str) -> str:
    """The model-space entity of an id: ``INSERT:4B[2]/3`` -> ``INSERT:4B``, ``HATCH:5C#0`` -> ``HATCH:5C``,
    ``MTEXT:2B:1`` -> ``MTEXT:2B`` (``dxf_generic.stroke_entity``; PDF ids pass through)."""
    head = eid.split("/")[0].split("#")[0]
    head = re.sub(r"\[\d+\]$", "", head)
    return ":".join(head.split(":")[:2])


def id_keys(eid: str) -> set[str]:
    """The ids an evidence id stands for: itself, its entity (hatch path and polyline piece dropped) and every
    enclosing block instance (``INSERT:4B/3/0`` -> ``INSERT:4B/3``, ``INSERT:4B``; a MINSERT copy ``INSERT:4B[2]``
    also as ``INSERT:4B``). A source item is used when its own id is among them."""
    out = {eid}
    base = eid.split("#")[0]
    parts = base.split("/")
    last = parts[-1]
    if last.count(":") >= 2 and not last.split(":")[-1].startswith("attrib"):
        parts[-1] = ":".join(last.split(":")[:2])
    for k in range(1, len(parts) + 1):
        path = "/".join(parts[:k])
        out.add(path)
        out.add(re.sub(r"\[\d+\]", "", path))
    out.add(top_entity(eid))
    return out


def expand_entities(value) -> list[str]:
    """Evidence entity text -> ids: comma lists, ``LINE:295900-295929`` ranges (decimal, as ``symbols.id_ranges``
    writes them), lists of ids."""
    if isinstance(value, (list, tuple)):
        out = []
        for v in value:
            out.extend(expand_entities(v))
        return out
    if not isinstance(value, str):
        return []
    out = []
    for part in value.split(","):
        part = part.strip()
        if not part or ":" not in part:
            continue
        head, _, tail = part.partition(":")
        m = re.fullmatch(r"(\d+)-(\d+)", tail)
        if m and 0 <= int(m.group(2)) - int(m.group(1)) <= RANGE_MAX:
            out.extend(f"{head}:{n}" for n in range(int(m.group(1)), int(m.group(2)) + 1))
        else:
            out.append(part)
    return out


def outdoor_kind(text) -> Optional[tuple[str, str]]:
    """(kind, class) of an outdoor-space name, else None."""
    f = fold(text)
    for kind, cls, rx in _OUTDOOR_RE:
        if rx.search(f):
            return kind, cls
    return None


def _furniture_type(text: str) -> Optional[str]:
    from wenart.ingest.generic import symbols as SY

    t = SY.keyword_type(text)
    if t is not None:
        return t
    up = B.fold_ascii(text or "").upper().replace(".", " ")
    up = " ".join(up.replace("*", " ").split())
    for word, ftype in EXTRA_FURNITURE_WORDS:
        if word in up:
            return ftype
    return None


def _family(ftype: Optional[str]) -> Optional[str]:
    if not ftype:
        return None
    return _FAMILY_OF.get(ftype, ftype)


def classify_text(row: dict) -> str:
    """The kind of a source text: ``space_name``, ``outdoor_space``, ``area``, ``size``, ``level_mark``,
    ``furniture_name``, ``dimension``, ``number``, ``title``, ``grid``, ``opening_tag``, ``note`` or ``other``."""
    from wenart.levels import marks as MK

    text = str(row.get("text") or "").strip()
    role = row.get("role")
    part = row.get("label_part")
    layer = fold(row.get("layer"))
    f = fold(text)
    if role == "dimension":
        return "dimension"
    if role in ("title", "scale"):
        return "title"
    if MK.parse_mark(text) is not None or (MK.is_mark_tag(row.get("tag")) and MK.read_mark(text, bare=True)):
        return "level_mark"
    if NOTE_RE.search(f) or len(f.split()) > MAX_WORDS:
        return "note"
    if part == "size":
        return "size"
    if part == "area" or U.parse_area(text) is not None or re.fullmatch(r"m\s*(?:²|2)", text.strip(), re.I):
        if outdoor_kind(text) is None:
            return "area"
    if outdoor_kind(text) is not None:
        return "outdoor_space"
    turkish, english = B.room_keyword_hits(text)
    if turkish or english or part == "name" or role == "room_label":
        return "space_name"
    if _furniture_type(text) is not None:
        return "furniture_name"
    if TURKISH_ROOM_MARKERS.search(f):
        return "space_name"
    if GRID_LAYER_RE.search(layer) and len(text) <= 3:
        return "grid"
    if OPENING_TAG_LAYER_RE.search(layer):
        return "opening_tag"
    if re.fullmatch(r"[\d.,'\"/x×*+\- ]+", text):
        return "number" if U.parse_size_pair(text) is None else "size"
    if len(text) <= 2:
        return "grid"
    return "other"


MUST_TEXT_KINDS = ("space_name", "outdoor_space", "area", "size", "level_mark", "furniture_name")


def layer_core(name) -> str:
    """A layer name without its external-reference prefix (``xref_PLAN$0$MYD - DUVAR`` -> ``MYD - DUVAR``), folded
    to ASCII upper case."""
    return B.fold_ascii(str(name or "")).split("$")[-1].strip().upper()


def annotation_layer(name) -> bool:
    """A layer of drawing annotation (dimensions, texts, axes, hatch patterns, level marks, the title block, the
    legend) or the default layer ``0``: counted, never judged."""
    core = layer_core(name)
    return core in ("0", "-", "") or bool(ANNOTATION_LAYER_RE.search(core))


def same_label(a, b) -> bool:
    """Two labels name the same space: equal once folded, without an area suffix and without punctuation, or one a
    cut-off start of the other (an OCR read ``EBEVEYN YATAK OD`` of ``Ebeveyn Yatak Odası``, 6 letters or more)."""
    def key(x) -> str:
        head = B.parse_area_label(str(x or ""))[0]
        return re.sub(r"[^a-z0-9]+", "", fold(head))
    ka, kb = key(a), key(b)
    if not ka or not kb:
        return False
    short, long_ = sorted((ka, kb), key=len)
    return ka == kb or (len(short) >= 6 and long_.startswith(short))


def _poly(points) -> Optional[Polygon]:
    try:
        if not points or len(points) < 3:
            return None
        p = Polygon([(float(x), float(y)) for x, y in points])
        return p if p.is_valid else p.buffer(0)
    except Exception:                                    # noqa: BLE001 - a broken polygon is no polygon
        return None


def _dist(a, b) -> float:
    return ((float(a[0]) - float(b[0])) ** 2 + (float(a[1]) - float(b[1])) ** 2) ** 0.5


# --------------------------------------------------------------------------
# The model side: elements, what they use, what is built
# --------------------------------------------------------------------------

class _Model:
    """The building's elements (every dict with an ``id`` and the evidence below it), the entities they use, what is
    built, the rooms and site surfaces per level, and the reasons the warnings and review entries log."""

    def __init__(self, building: dict) -> None:
        self.b = building
        self.elements: dict[str, dict] = {}          # key -> {"id", "path", "dict", "entities"}
        self.users: dict[str, set] = {}              # entity id (exact and top-level) -> element keys
        self.reasons: dict[str, list[str]] = {}      # element id -> logged reasons
        self._walk(building, "", None)
        for w in building.get("warnings") or []:
            m = ID_HEAD_RE.match(str(w))
            if m:
                self.reasons.setdefault(m.group(1), []).append(str(w))
        for nr in building.get("needs_review") or []:
            if isinstance(nr, dict) and nr.get("id"):
                self.reasons.setdefault(str(nr["id"]), []).append(f"listed for review: {nr.get('reason')}")
        for s in building.get("symbols") or []:
            if isinstance(s, dict) and s.get("former_piece_id"):
                self.reasons.setdefault(str(s["former_piece_id"]), []).append(
                    f"moved to the symbols ({s.get('id')}): {s.get('reason')}")
        for el in self.elements.values():
            for k in REASON_KEYS:
                if el["dict"].get(k):
                    self.reasons.setdefault(el["id"], []).append(str(el["dict"][k]))
        self.rooms: dict[str, list[tuple[dict, Polygon]]] = {}
        for r in building.get("rooms") or []:
            p = _poly(r.get("polygon"))
            if p is not None and r.get("build", True) is not False:
                self.rooms.setdefault(r.get("level_id"), []).append((r, p))
        site = building.get("site") or {}
        self.surfaces: list[tuple[dict, Polygon]] = []
        for key, items in site.items():
            if key in SITE_SKIP_SURFACE or not isinstance(items, list):
                continue
            for s in items:
                if isinstance(s, dict) and s.get("build", True) is not False:
                    p = _poly(s.get("polygon") or s.get("outline") or s.get("footprint"))
                    if p is not None:
                        self.surfaces.append((s, p))
        walls = []
        for w in list(building.get("walls") or []) + list(site.get("boundary_walls") or []):
            try:
                walls.append(LineString([w["start"], w["end"]]).buffer(max(float(w.get("thickness") or 0.1), 0.05)
                                                                         / 2.0 + 0.05))
            except Exception:                            # noqa: BLE001 - a wall without a line
                continue
        self.walls = unary_union(walls) if walls else None
        self.pieces = [f for f in building.get("furniture") or [] if f.get("build", True) is not False]

    def _walk(self, node, path: str, owner: Optional[str]) -> None:
        if isinstance(node, dict):
            key = owner
            if isinstance(node.get("id"), str) and path.split(".")[0] not in ("documents", "conflicts"):
                key = f"{path}#{len(self.elements)}"
                self.elements[key] = {"id": node["id"], "path": path, "dict": node}
            for k, v in node.items():
                if k in ("entity", "entities", "symbol_ids", "entity_ids") and key is not None:
                    for eid in expand_entities(v):
                        for idk in id_keys(eid):
                            self.users.setdefault(idk, set()).add(key)
                elif isinstance(v, (dict, list)):
                    self._walk(v, f"{path}.{k}" if path else k, key)
        elif isinstance(node, list):
            for v in node:
                self._walk(v, path, owner)

    # ---- what is built ---------------------------------------------------

    def space_built(self, el: dict) -> bool:
        """A site area is a label record: built when it says so with an outline, when another built element uses its
        label (an outdoor space the site or the levels build from it, whatever list holds it), or when a built site
        surface or room holds its anchor."""
        d = el["dict"]
        if d.get("build") is True and _poly(d.get("polygon")) is not None:
            return True
        for ev in d.get("evidence") or []:
            if not isinstance(ev, dict):
                continue
            for eid in expand_entities(ev.get("entity")):
                for key in self.users.get(eid, ()):
                    other = self.elements[key]
                    if other["dict"] is d or other["path"] in ("site.areas", "site.decor") or \
                            other["path"].split(".")[0] in DATA_KEYS + ("symbols",):
                        continue
                    if other["dict"].get("build", True) is not False:
                        return True
        anchor = d.get("anchor")
        if anchor:
            pt = Point(float(anchor[0]), float(anchor[1]))
            if any(p.buffer(0.05).contains(pt) for _, p in self.surfaces):
                return True
            if any(p.contains(pt) for _, p in self.rooms.get(d.get("level_id"), [])):
                return True
        return False

    def status(self, key: str) -> str:
        """``built``, ``data`` (level marks, levels ...: used as data), ``explained`` (not built, a logged reason or
        a rule says why) or ``not_built``."""
        el = self.elements[key]
        path, d = el["path"], el["dict"]
        root = path.split(".")[0]
        if root in DATA_KEYS:
            return "data"
        if root == "symbols":
            return "explained"
        if path == "site.areas":
            return "built" if self.space_built(el) else "not_built"
        if path == "site.decor":
            return "built" if d.get("kind") in ("tree", "plant") else "explained"
        if d.get("build", True) is False:
            return "explained" if self.reasons.get(el["id"]) else "not_built"
        return "built"

    def weak(self, key: str) -> bool:
        """An element that records a drawn item without building or explaining it: site decor of a kind the site
        does not build (``other``: grid bubbles, railings and sills read as decor). Geometry used only by such an
        element is not accounted for."""
        el = self.elements[key]
        return el["path"] == "site.decor" and el["dict"].get("kind") not in ("tree", "plant")

    def users_of(self, eid: str, strong: bool = False) -> list[str]:
        """The elements that use a source item (its own id among their evidence ids or their enclosing blocks)."""
        keys = self.users.get(eid, ())
        return sorted(k for k in keys if not (strong and self.weak(k)))

    def text_users(self, tid: str) -> list[str]:
        """The elements that use a text: its own id, its MTEXT entity (``MTEXT:2B:1`` -> ``MTEXT:2B``), and for a block
        attribute (``.../attrib1``) the tag block it belongs to. Never the block a whole plan is drawn in."""
        keys = set(self.users.get(tid, ()))
        parts = tid.split("/")
        if len(parts) > 1 and parts[-1].startswith("attrib"):
            keys |= set(self.users.get("/".join(parts[:-1]), ()))
        last = parts[-1]
        if len(parts) == 1 and last.startswith("MTEXT:") and last.count(":") >= 2:
            keys |= set(self.users.get(":".join(last.split(":")[:2]), ()))
        return sorted(keys)

    def room_at(self, level_id, pos) -> Optional[dict]:
        if pos is None:
            return None
        pt = Point(float(pos[0]), float(pos[1]))
        for r, p in self.rooms.get(level_id, []):
            if p.contains(pt):
                return r
        return None

    def room_distance(self, level_id, pos) -> float:
        if pos is None or not self.rooms.get(level_id):
            return float("inf")
        pt = Point(float(pos[0]), float(pos[1]))
        return min(p.distance(pt) for _, p in self.rooms[level_id])


# --------------------------------------------------------------------------
# The ledger
# --------------------------------------------------------------------------

class _Ledger:
    def __init__(self, building: dict, items: dict) -> None:
        self.m = _Model(building)
        self.items = items or {}
        self.pages = {p["id"]: p for p in self.items.get("pages") or []}
        self.findings: dict[str, dict] = {}
        self.coverage: dict[str, Counter] = {}
        self.text_findings: dict[str, str] = {}     # text id -> finding target that carries it
        self.id_count = Counter(el["id"] for el in self.m.elements.values())
        self.kinds: dict[str, str] = {}
        self.label_rows: dict[tuple, list[dict]] = {}
        self.by_page: dict[str, list[dict]] = {}

    # ---- bookkeeping -----------------------------------------------------

    def count(self, kind: str, must: bool, accounted: bool) -> None:
        c = self.coverage.setdefault(kind, Counter())
        c["items"] += 1
        c["must"] += int(must)
        c["accounted"] += int(accounted)

    def add(self, check: str, severity: str, target: str, message: str, evidence: dict, owner: str,
            fix: Optional[dict] = None) -> dict:
        f = {"line": LINE, "check": check, "severity": severity, "target": target, "message": message,
             "evidence": {k: v for k, v in evidence.items() if v is not None}, "owner": owner, "fix": fix}
        cur = self.findings.get(target)
        if cur is None:
            self.findings[target] = f
            return f
        if SEVERITY_RANK[severity] < SEVERITY_RANK[cur["severity"]]:
            f["also"] = sorted(set(cur.get("also", [])) | {cur["check"]})
            f["warnings"] = cur.get("warnings", [])
            f["related"] = cur.get("related", [])
            f["fix"] = f["fix"] or cur["fix"]
            self.findings[target] = f
            return f
        if check != cur["check"]:
            cur["also"] = sorted(set(cur.get("also", [])) | {check})
        return cur

    def page_of(self, row: dict) -> dict:
        return self.pages.get(row.get("page")) or {}

    def plan_read(self, page: dict) -> bool:
        return bool(page.get("read")) and (page.get("class") in PLAN_CLASSES or page.get("region_class")
                                           in PLAN_CLASSES)

    @staticmethod
    def evidence(row: dict, page: dict, **extra) -> dict:
        ev = {"file": page.get("file"), "entity": row.get("id"), "layer": row.get("layer"), "text": row.get("text"),
              "position": row.get("pos"), "level_id": page.get("level_id"), "region_id": page.get("region_id")}
        if page.get("format") == "pdf" or (page.get("page") or 1) > 1:
            ev["page"] = page.get("page")
        ev.update(extra)
        return ev

    # ---- texts -----------------------------------------------------------

    def tgt(self, key: str) -> str:
        """A finding target for an element: its id, with its position when several elements share the id."""
        el = self.m.elements[key]
        if self.id_count[el["id"]] == 1:
            return el["id"]
        d = el["dict"]
        pos = d.get("anchor") or (d.get("footprint") or {}).get("center") or d.get("center")
        return f"{el['id']}@{pos}"

    def texts(self) -> None:
        rows = self.items.get("texts") or []
        kinds = {r["id"]: classify_text(r) for r in rows}
        self.kinds = kinds
        self.label_rows: dict[tuple, list[dict]] = {}
        by_page: dict[str, list[dict]] = {}
        for r in rows:
            by_page.setdefault(r.get("page"), []).append(r)
            if r.get("label_id"):
                self.label_rows.setdefault((r.get("page"), r["label_id"]), []).append(r)
        self.by_page = by_page
        first_pass = [r for r in rows if kinds[r["id"]] in ("space_name", "outdoor_space")]
        rest = [r for r in rows if kinds[r["id"]] not in ("space_name", "outdoor_space")]
        for r in first_pass + rest:
            page = self.page_of(r)
            kind = kinds[r["id"]]
            must = kind in MUST_TEXT_KINDS and self.plan_read(page)
            if not must:
                self.count(f"text:{kind}", False, True)
                continue
            users = self.m.text_users(r["id"])
            states = {k: self.m.status(k) for k in users}
            if kind in ("space_name", "outdoor_space"):
                ok = self._space_text(r, page, users, states)
            elif kind in ("area", "size"):
                ok = self._area_text(r, page, users, states)
            elif kind == "level_mark":
                ok = self._level_mark(r, page, users)
            else:                                        # furniture_name
                ok = self._furniture_text(r, page, users, states)
            self.count(f"text:{kind}", True, ok)

    def _level_mark(self, r: dict, page: dict, users: list[str]) -> bool:
        from wenart.levels import marks as MK

        if users:
            return True
        mark = MK.parse_mark(r["text"]) or {}
        self.add("A5", "major", r["id"],
                 f"level mark {r['text']!r} on {page.get('level_id')} is not read: no level mark and no element uses "
                 f"it", self.evidence(r, page), "levels",
                 {"action": "read_level_mark", "entity": r["id"], "level_id": page.get("level_id"),
                  "point": r.get("pos"), "value": mark.get("value")})
        return False

    def _space_text(self, r: dict, page: dict, users: list[str], states: dict) -> bool:
        if r.get("label_part") not in (None, "name"):
            return True
        if r.get("label_id") and r["label_id"] != r["id"]:
            # A later name line of a label block (``EBEVEYN`` / ``Y.ODASI``): its first line speaks for the block.
            return r["label_id"] not in self.text_findings
        level = page.get("level_id")
        od = outdoor_kind(r.get("label") or r["text"])
        label = r.get("label") or r["text"]
        built = [k for k in users if states[k] == "built"]
        rooms_using = [self.m.elements[k] for k in built if self.m.elements[k]["path"] == "rooms"]
        if built and not rooms_using:
            return True                                  # a built site surface or another built element
        for el in rooms_using:
            room = el["dict"]
            if same_label(room.get("label_raw") or room.get("label"), label) or not r.get("label"):
                return True
        if rooms_using:
            self._merged(r, page, rooms_using[0]["dict"], label, "is a second label of")
            return False
        room = self.m.room_at(level, r.get("pos"))
        if room is not None and same_label(room.get("label_raw") or room.get("label"), label):
            return True
        if room is not None and not od:
            self._merged(r, page, room, label, "lies unused in")
            return False
        # Not built: an outdoor space or a room the model does not have.
        unbuilt = [k for k in users if states[k] == "not_built"]
        el = self.m.elements[unbuilt[0]] if unbuilt else None
        target = self.tgt(unbuilt[0]) if unbuilt else r["id"]
        area = self._printed_area(r)
        if od:
            kind, cls = od
            have = (f"the model records {el['id']} ({el['path']}) but builds nothing"
                    + (f": {el['dict'].get('note')}" if el["dict"].get("note") else "")
                    if el else "no element of the model uses it")
            msg = (f"the documents name an outdoor space {label!r} ({kind}"
                   + (f", {area:g} m²" if area else "") + f") on {level}; {have}")
            fix = {"action": "build_outdoor_space", "kind": kind, "level_id": level, "label": label,
                   "anchor": r.get("pos"), "area_m2": area, "element_id": el["id"] if el else None,
                   "polygon_hint": None}
            f = self.add("A1", CLASS_SEVERITY[cls], target, msg, self.evidence(r, page), "site", fix)
        else:
            have = f"the model records {el['id']} but builds nothing" if el else "no room of the model uses it"
            msg = (f"the documents name a room {label!r}" + (f" ({area:g} m²)" if area else "") +
                   f" on {level}; {have}")
            f = self.add("A1", "critical", target, msg, self.evidence(r, page), "reading",
                         {"action": "add_room", "level_id": level, "label": label, "anchor": r.get("pos"),
                          "area_m2": area})
        self._carry_label(r, f)
        return False

    def _merged(self, r: dict, page: dict, room: dict, label: str, how: str) -> None:
        own = room.get("room_type") or B.room_type_for(room.get("label_raw") or room.get("label") or "")
        theirs = "dining" if re.search(r"(?<![a-z])yemek", fold(label)) else B.room_type_for(label)
        area = self._printed_area(r)
        if not self._room_has_label(room):
            # The room is an unlabelled face (its placeholder name): the documents' name is its name.
            size = area if area is not None else room.get("area_computed")
            sev = "minor" if size is not None and float(size) < SMALL_SPACE_M2 else "major"
            f = self.add("A3", sev, f"{room['id']}:{r['id']}",
                         f"the documents name {label!r}" + (f" ({area:g} m²)" if area else "") +
                         f" ({theirs}) inside room {room['id']}, which has no label of its own "
                         f"({room.get('label')}, {room.get('room_type')}): the room is not named and typed by it",
                         self.evidence(r, page, room_id=room["id"]), "reading",
                         {"action": "label_room", "room_id": room["id"], "label": label, "room_type": theirs})
            self._carry_label(r, f)
            return
        pair = tuple(sorted((theirs, own)))
        small = area is not None and area < SMALL_SPACE_M2
        sev = "minor" if pair in OPEN_PLAN_PAIRS or theirs in (own, "shaft") or small else "major"
        f = self.add("A3", sev, f"{room['id']}:{r['id']}",
                     f"the documents name a space {label!r}" + (f" ({area:g} m²)" if area else "") +
                     f" that {how} room {room['id']} ({room.get('label')}, {room.get('room_type')}): it is not a "
                     f"room of its own in the model", self.evidence(r, page, room_id=room["id"]), "reading",
                     {"action": "split_room", "room_id": room["id"], "label": label, "anchor": r.get("pos"),
                      "area_m2": area})
        self._carry_label(r, f)

    @staticmethod
    def _room_has_label(room: dict) -> bool:
        """A room named by a drawn text (its evidence holds a text), not an unlabelled face with a placeholder."""
        return any(isinstance(e, dict) and (e.get("text") or re.match(r"(TEXT|MTEXT|ATTRIB|char):", str(
            e.get("entity") or "")) or "/attrib" in str(e.get("entity") or "")) for e in room.get("evidence") or [])

    def _label_rows(self, r: dict) -> list[dict]:
        if not r.get("label_id"):
            return []
        return [x for x in self.label_rows.get((r.get("page"), r["label_id"]), []) if x["id"] != r["id"]]

    def _printed_area(self, r: dict) -> Optional[float]:
        for x in self._label_rows(r):
            a = U.parse_area(str(x.get("text") or ""))
            if a:
                return round(a[0], 2)
        a = U.area_suffix(str(r.get("text") or ""))
        return round(a[1], 2) if a else None

    def _carry_label(self, r: dict, f: dict) -> None:
        """The other runs of the flagged label (its area, size) belong to the same finding."""
        self.text_findings[r["id"]] = f["target"]
        for x in self._label_rows(r):
            self.text_findings[x["id"]] = f["target"]
            related = f.setdefault("related", [])
            if x["id"] not in [e.get("entity") for e in related]:
                related.append({"entity": x["id"], "text": x.get("text")})

    def _area_value_text(self, r: dict) -> str:
        """The printed area as read: a bare unit run (``m²``) joins the number run just left of it (``9,00 m²``)."""
        text = str(r.get("text") or "")
        if re.fullmatch(r"\s*m\s*(?:²|2)\s*", text, re.I) and r.get("pos"):
            nums = [x for x in self.by_page.get(r.get("page"), []) if x.get("pos") and x["id"] != r["id"]
                    and re.fullmatch(r"\s*\d+(?:[.,]\d+)?\s*", str(x.get("text") or ""))
                    and abs(x["pos"][1] - r["pos"][1]) <= 0.15 and 0 < r["pos"][0] - x["pos"][0] <= 1.0]
            if nums:
                n = max(nums, key=lambda x: x["pos"][0])
                return f"{n['text']} {text}"
        return text

    def _area_text(self, r: dict, page: dict, users: list[str], states: dict) -> bool:
        if r["id"] in self.text_findings:
            return False                                 # its space is flagged (A1 / A3)
        if any(states[k] in ("built", "data", "explained") for k in users):
            return True
        level = page.get("level_id")
        shown = self._area_value_text(r)
        what = "size" if self.kinds.get(r["id"]) == "size" else "area"
        if r.get("label_id"):
            names = [x for x in self.label_rows.get((r.get("page"), r["label_id"]), [])
                     if x.get("label_part") == "name"]
        else:
            names = [x for x in self.by_page.get(r.get("page"), [])
                     if self.kinds.get(x["id"]) in ("space_name", "outdoor_space") and x.get("pos") and r.get("pos")
                     and _dist(x["pos"], r["pos"]) <= AREA_NEAR_M]
        if names:
            flagged = [n for n in names if n["id"] in self.text_findings]
            if flagged:
                f = self.findings.get(self.text_findings[flagged[0]["id"]])
                if f is not None:
                    f.setdefault("related", []).append({"entity": r["id"], "text": shown})
                return False
            name = names[0]
            self.add("A4", "minor", r["id"],
                     f"printed {what} {shown!r} of {name.get('label') or name['text']!r} on {level} is not used: the "
                     f"{what} check of that space is lost", self.evidence(r, page), "reading",
                     {"action": "check_area_label", "label": name.get("label") or name["text"], "text": shown,
                      "anchor": r.get("pos")})
            return False
        room = self.m.room_at(level, r.get("pos"))
        if room is not None:
            self.add("A4", "minor", r["id"],
                     f"printed {what} {shown!r} in room {room['id']} ({room.get('label')}) on {level} is tied to no "
                     f"label: its {what} check is lost", self.evidence(r, page, room_id=room["id"]), "reading",
                     {"action": "check_area_label", "room_id": room["id"], "text": shown})
            return False
        if what == "size" or self.m.room_distance(level, r.get("pos")) > TABLE_FAR_M:
            return True                                  # an entry of an area table beside the plan
        self.add("A4", "major", r["id"],
                 f"printed area {shown!r} beside the building on {level} names no space and no element uses it: "
                 f"a space the model may miss", self.evidence(r, page), "site",
                 {"action": "classify_surface", "level_id": level, "anchor": r.get("pos"), "text": shown})
        return False

    def _furniture_text(self, r: dict, page: dict, users: list[str], states: dict) -> bool:
        if any(states[k] in ("built", "explained") for k in users):
            return True
        ftype = _furniture_type(r["text"])
        fam = _family(ftype)
        level = page.get("level_id")
        pos = r.get("pos")
        if not pos:
            return True

        def centre(f):
            return (f.get("footprint") or {}).get("center") or (1e9, 1e9)

        near = sorted((f for f in self.m.b.get("furniture") or [] if f.get("level_id") == level
                       and _dist(centre(f), pos) <= NAME_NEAR_M), key=lambda f: _dist(centre(f), pos))
        built = [f for f in near if f.get("build", True) is not False]
        if any(_family(f.get("type")) == fam for f in built):
            return True
        unbuilt = [f for f in near if f.get("build", True) is False and f.get("type") in (None, "unknown")]
        have = ", ".join(f"{f['id']} {f.get('type')}" + ("" if f.get("build", True) is not False else " (not built)")
                         for f in near[:3]) or "no piece"
        fix = ({"action": "type_piece", "element_id": unbuilt[0]["id"], "type": ftype, "named_by": r["id"]}
               if unbuilt else
               {"action": "add_piece", "type": ftype, "level_id": level, "anchor": pos, "named_by": r["id"]})
        self.add("A6", "major", r["id"],
                 f"the documents name a {ftype} ({r['text']!r}) on {level}; the model has {have} within "
                 f"{NAME_NEAR_M:g} m", self.evidence(r, page), "reading", fix)
        return False

    # ---- blocks ----------------------------------------------------------

    def blocks(self) -> None:
        from wenart.ingest.generic import symbols as SY

        for blk in self.items.get("blocks") or []:
            name = str(blk.get("name") or "?")
            folded = B.fold_ascii(name)
            ftype = SY.keyword_type(name)
            if BLOCK_ANNOTATION_RE.search(folded) and ftype is None:
                kind = "annotation"
            elif ftype is not None:
                kind = "furniture"
            elif BLOCK_TREE_RE.search(folded):
                kind = "vegetation"
            elif BLOCK_OPENING_RE.search(folded):
                kind = "opening"
            else:
                kind = "other"
            for ins in blk.get("inserts") or []:
                page = self.page_of(ins)
                large = max(ins.get("size") or [0.0, 0.0]) >= FRAME_MIN_M
                if not self.plan_read(page) or kind == "annotation" or large:
                    self.count(f"block:{kind}", False, True)
                    continue
                ok = bool(self.m.users_of(ins["id"], strong=True))
                self.count(f"block:{kind}", kind != "other", ok)
                if ok:
                    continue
                level = page.get("level_id")
                if kind == "other":
                    sev, owner, what = "minor", "reading", f"block {name!r}"
                elif kind == "vegetation":
                    sev, owner, what = "major", "site", f"vegetation block {name!r}"
                elif kind == "opening":
                    sev, owner, what = "major", "reading", f"door / window block {name!r}"
                else:
                    sev, owner, what = "major", "reading", f"{ftype} block {name!r}"
                weak = self.m.users_of(ins["id"])
                have = (f"only {', '.join(sorted({self.m.elements[k]['id'] for k in weak}))} records it (site decor, "
                        f"not built)" if weak else "no element of the model uses it")
                self.add("A6", sev, ins["id"],
                         f"the documents draw a {what} ({ins.get('size')} m) on {level}; {have}",
                         self.evidence(dict(ins, text=None), page, block=name), owner,
                         {"action": "add_piece", "type": ftype, "block": name, "entity": ins["id"],
                          "level_id": level, "anchor": ins.get("pos"), "size": ins.get("size")}
                         if kind == "furniture" else None)

    # ---- layers, hatches, outlines ----------------------------------------

    def _dimension_layers(self) -> set:
        """(page, layer) pairs whose texts are mostly dimensions or bare numbers: dimension-chain layers."""
        per: dict[tuple, Counter] = {}
        for r in self.items.get("texts") or []:
            c = per.setdefault((r.get("page"), r.get("layer")), Counter())
            c["all"] += 1
            c["dim"] += int(self.kinds.get(r["id"]) in ("dimension", "number"))
        return {k for k, c in per.items() if c["all"] >= 3 and c["dim"] >= 0.8 * c["all"]}

    def geometry(self) -> None:
        named = set()                                    # layers a warning names as layers (a logged choice)
        for w in self.m.b.get("warnings") or []:
            named.update(next(g for g in m.groups() if g).strip() for m in LAYER_NAMED_RE.finditer(str(w)))
        dim_layers = self._dimension_layers()
        for lay in self.items.get("layers") or []:
            page = self.page_of(lay)
            name = str(lay.get("name") or "-")
            n = int(lay.get("entities") or 0)
            annotation = annotation_layer(name) or (lay.get("page"), name) in dim_layers
            enough = n >= LAYER_MIN_ENTITIES or (outdoor_kind(layer_core(name)) is not None and n >= OUTDOOR_LAYER_MIN)
            if not self.plan_read(page) or not enough or annotation:
                self.count("layer", False, True)
                continue
            used = any(self.m.users_of(eid, strong=True) for eid in lay.get("ids") or [])
            if used or name in named:
                self.count("layer", True, True)
                continue
            self.count("layer", True, False)
            level = page.get("level_id")
            od = outdoor_kind(layer_core(name))
            part = bool(BUILDING_PART_LAYER_RE.search(layer_core(name)))
            carriers = [f for f in self.findings.values() if f["check"] == "A1" and od
                        and (f.get("fix") or {}).get("action") == "build_outdoor_space"
                        and f["evidence"].get("level_id") == level and f["evidence"].get("region_id") ==
                        page.get("region_id")] if od else []
            if carriers:
                for f in carriers:
                    f.setdefault("related", []).append({"layer": name, "entities": n,
                                                        "note": "drawn on this layer, none of it used"})
                    self._hint_from_layer(f, lay)
                continue
            self.add("A9", "major" if part else "minor", f"layer:{lay.get('page')}:{name}",
                     f"layer {name!r} ({n} entities: " + ", ".join(f"{k} {v}" for k, v in
                                                                  sorted((lay.get('types') or {}).items())) +
                     f") on {level}: none of it is used by the model and no warning names it",
                     {"file": page.get("file"), "layer": name, "level_id": level, "region_id": page.get("region_id")},
                     "reading", None)
        for key in ("hatches", "outlines"):
            for reg in self.items.get(key) or []:
                self._surface(reg, key)

    @staticmethod
    def _hint_from_layer(f: dict, lay: dict) -> None:
        """An outdoor space without an outline takes the hull of its own layer's drawing near its label (the
        railing of a veranda or a balcony) as ``polygon_hint`` when that hull is about as large as the printed area
        (or at least 1 m² without one)."""
        fx = f.get("fix") or {}
        anchor, boxes = fx.get("anchor"), lay.get("boxes")
        if not anchor or not boxes or fx.get("polygon_hint"):
            return
        area = fx.get("area_m2")
        reach = 1.5 * (float(area) ** 0.5) + 1.0 if area else 5.0
        pts = []
        for b in boxes:
            if b and _dist(((b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0), anchor) <= reach:
                pts += [(b[0], b[1]), (b[2], b[3]), (b[0], b[3]), (b[2], b[1])]
        if len(pts) < 3:
            return
        hull = unary_union([Point(p) for p in pts]).convex_hull
        if hull.geom_type != "Polygon" or hull.area < (0.4 * float(area) if area else 1.0):
            return
        if area and hull.area > 2.5 * float(area):
            return
        fx["polygon_hint"] = [[round(x, 3), round(y, 3)] for x, y in list(hull.exterior.coords)[:-1]]
        fx["railing_layer"] = lay.get("name")
        fx["polygon_method"] = (f"convex hull of layer {lay.get('name')!r} near the label ({hull.area:.1f} m²"
                                + (f", printed {float(area):g} m²" if area else "") + ")")

    def _surface(self, reg: dict, key: str) -> None:
        page = self.page_of(reg)
        area = float(reg.get("area_m2") or 0.0)
        name = str(reg.get("layer") or "")
        kind = {"hatches": "hatch", "outlines": "outline"}[key]
        if not self.plan_read(page) or area < SURFACE_MIN_M2 or annotation_layer(name):
            self.count(kind, False, True)
            return
        if self.m.users_of(reg["id"], strong=True):
            self.count(kind, True, True)
            return
        level = page.get("level_id")
        poly = _poly(reg.get("polygon"))
        if poly is None:
            self.count(kind, False, True)
            return
        rooms = self.m.rooms.get(level, [])
        centre = poly.representative_point()
        inside_room = any(p.contains(centre) for _, p in rooms)
        inside_surface = any(p.contains(centre) for _, p in self.m.surfaces)
        in_wall = self.m.walls is not None and self.m.walls.contains(centre)
        holds_rooms = sum(1 for _, p in rooms if poly.contains(p.representative_point())) >= 2
        if inside_room or inside_surface or in_wall or holds_rooms:
            self.count(kind, True, True)
            return
        # An outdoor space flagged on this level whose label lies in the surface takes it as its outline.
        for f in self.findings.values():
            fx = f.get("fix") or {}
            if f["check"] == "A1" and fx.get("action") == "build_outdoor_space" and fx.get("level_id") == level \
                    and fx.get("anchor") and poly.buffer(0.05).contains(Point(*fx["anchor"])):
                if fx.get("polygon_hint") is None or area < float(fx.get("polygon_area_m2") or 1e9):
                    fx["polygon_hint"] = reg.get("polygon")
                    fx["polygon_area_m2"] = area
                    fx["polygon_method"] = f"{kind} {reg['id']} around the label ({area:g} m²)"
                self.count(kind, True, False)
                return
        self.count(kind, True, False)
        self.add("A9", "major", reg["id"],
                 f"a drawn {'hatch' if key == 'hatches' else 'closed outline'} of {area:g} m² on layer {name!r} lies "
                 f"outside every room, site surface and wall on {level} and no element uses it: a surface the model "
                 f"may miss", {"file": page.get("file"), "entity": reg["id"], "layer": name,
                               "position": reg.get("pos"), "level_id": level, "region_id": page.get("region_id")},
                 "site", {"action": "classify_surface", "entity": reg["id"], "level_id": level,
                          "polygon": reg.get("polygon"), "area_m2": area})

    # ---- elements not built ------------------------------------------------

    def elements(self) -> None:
        for key, el in self.m.elements.items():
            d, path = el["dict"], el["path"]
            root = path.split(".")[0]
            if root in DATA_KEYS or root == "symbols" or path == "site.decor":
                continue
            drawn = any(isinstance(e, dict) and e.get("entity") and e.get("method") in ("vector", "ocr", "ai")
                        for e in d.get("evidence") or [])
            if not drawn:
                continue
            space = path in ("site.areas", "rooms")
            built = self.m.space_built(el) if path == "site.areas" else d.get("build", True) is not False
            if built:
                self.count(f"element:{path}", True, True)
                continue
            reasons = list(self.m.reasons.get(el["id"], []))
            ok = any(SPACE_EXPLAINED_RE.search(x) for x in reasons) if space else bool(reasons)
            self.count(f"element:{path}", True, ok)
            if ok:
                continue
            ev0 = next((e for e in d.get("evidence") or [] if isinstance(e, dict) and e.get("entity")), {})
            evidence = {"file": ev0.get("file"), "entity": ev0.get("entity"), "layer": ev0.get("layer"),
                        "text": ev0.get("text"), "position": d.get("anchor") or (d.get("footprint") or {}).get(
                            "center"), "level_id": d.get("level_id"), "region_id": ev0.get("region_id")}
            target = self.tgt(key)
            if space:
                label = d.get("label_raw") or d.get("label") or ""
                od = outdoor_kind(label) or ((d.get("kind") or "other"), "house")
                sev = CLASS_SEVERITY.get(od[1], "critical")
                self.add("A2", sev, target,
                         f"{el['id']} ({label!r}) is drawn but not built; its reason does not explain a space: "
                         + ("; ".join(reasons) if reasons else "none logged"), evidence, "site",
                         {"action": "build_outdoor_space", "kind": od[0], "level_id": d.get("level_id"),
                          "label": label, "anchor": d.get("anchor"), "element_id": el["id"], "polygon_hint": None})
            else:
                self.add("A2", "major", target,
                         f"{el['id']} ({d.get('type') or path}) is drawn but not built and no warning, review entry "
                         f"or symbol says why", evidence, "reading", None)

    # ---- warnings ----------------------------------------------------------

    def warnings(self) -> None:
        ids = {el["id"] for el in self.m.elements.values()}
        for w in self.m.b.get("warnings") or []:
            w = str(w)
            if not DROP_WARNING_RE.search(w):
                self.count("warning", False, True)
                continue
            m = ID_HEAD_RE.match(w)
            if (m and m.group(1) in ids) or REGION_USE_NOTE_RE.search(w) or HARMLESS_WARNING_RE.search(w):
                self.count("warning", True, True)          # the logged reason of an element, a region's use
                continue
            quoted = {fold(q) for q in QUOTED_RE.findall(w)}
            levels = set(re.findall(r"\bL-?\d+[a-z]?\b", w)[:1])
            carriers = [f for f in self.findings.values()
                        if quoted & {fold(f["evidence"].get("text")), fold((f.get("fix") or {}).get("label"))}]
            if not carriers and levels and SPACE_WARNING_RE.search(w):
                carriers = [f for f in self.findings.values() if f["check"] in ("A1", "A2")
                            and f["evidence"].get("level_id") in levels]
            if carriers:
                for f in carriers:
                    f.setdefault("warnings", []).append(w)
                self.count("warning", True, True)
                continue
            if quoted and all(self._quoted_is_note(q) for q in quoted):
                self.count("warning", True, True)          # a table entry or note read as a label
                continue
            self.count("warning", True, False)
            if re.search(r"\blevel\b.*\bleft out\b", w):
                sev = "critical"
            elif SPACE_WARNING_RE.search(w):
                sev = "major"
            else:
                sev = "minor"
            owner = "site" if re.search(r"\bsite\b|decor|areas?\b", w) else "reading"
            self.add("A7", sev, f"warning:{len(self.findings)}", f"the reading says: {w}",
                     {"text": w}, owner, None)

    def _quoted_is_note(self, q: str) -> bool:
        return bool(NOTE_RE.search(q))

    # ---- pages and levels ----------------------------------------------------

    def pages_and_levels(self) -> None:
        for lv in self.m.b.get("levels_left_out") or []:
            self.add("A8", "critical", f"level:{lv.get('label')}",
                     f"level {lv.get('label')} ({lv.get('region_id')}) is left out of the model: {lv.get('reason')}",
                     {"region_id": lv.get("region_id")}, "sheets",
                     {"action": "read_region", "region_id": lv.get("region_id")})
            self.count("level", True, False)
        left_regions = {lv.get("region_id") for lv in self.m.b.get("levels_left_out") or []}
        for page in self.items.get("pages") or []:
            cls = page.get("region_class") or page.get("class")
            reason = page.get("skip_reason") or ""
            feats = page.get("region_features") or {}
            if page.get("read"):
                self.count("page", True, True)
                continue
            if page.get("region_id") in left_regions:
                self.count("page", True, False)
                continue
            if cls in PLAN_CLASSES:
                if PAGE_EXPLAINED_RE.search(reason):
                    self.count("page", True, True)
                    continue
                self.count("page", True, False)
                self.add("A8", "critical", f"page:{page['id']}",
                         f"plan {page.get('file')} p{page.get('page')}"
                         + (f" ({page.get('region_id')})" if page.get("region_id") else "")
                         + f" is not read: {reason or 'no reason logged'}",
                         {"file": page.get("file"), "region_id": page.get("region_id"), "page": page.get("page")},
                         "sheets" if page.get("region_id") else "reading",
                         {"action": "read_region", "region_id": page.get("region_id")} if page.get("region_id")
                         else None)
                continue
            labels = int(feats.get("room_labels") or 0) + int(feats.get("area_labels") or 0)
            if page.get("region_use") in (None, "ignored") and labels and cls not in ("section", "elevation"):
                self.count("page", True, False)
                self.add("A8", "major", f"page:{page['id']}",
                         f"{cls} {page.get('file')} ({page.get('region_id') or 'p' + str(page.get('page'))}) holds "
                         f"{labels} room / area label(s) and is not read: {reason or 'no reason logged'}",
                         {"file": page.get("file"), "region_id": page.get("region_id"), "page": page.get("page")},
                         "sheets", None)
                continue
            self.count("page", False, True)

    # ---- result --------------------------------------------------------------

    def run(self) -> dict:
        if not self.items:
            self.add("A8", "major", "source_items",
                     "no source inventory (source_items.json): the documents' items cannot be checked", {},
                     "reading", None)
        else:
            self.texts()
            self.elements()
            self.blocks()
            self.geometry()
            self.pages_and_levels()
            self.warnings()
        findings = sorted(self.findings.values(),
                          key=lambda f: (SEVERITY_RANK[f["severity"]], f["check"], str(f["target"])))
        for f in findings:
            fx = f.get("fix")
            if isinstance(fx, dict):
                fx.pop("polygon_area_m2", None)
        coverage = {k: {"items": c["items"], "must": c["must"], "accounted": c["accounted"],
                        "unaccounted": c["items"] - c["accounted"]} for k, c in sorted(self.coverage.items())}
        items = sum(c["items"] for c in self.coverage.values())
        accounted = sum(c["accounted"] for c in self.coverage.values())
        must = sum(c["must"] for c in self.coverage.values())
        must_ok = sum(min(c["must"], c["accounted"]) for c in self.coverage.values() if c["must"])
        by_check = Counter(f["check"] for f in findings)
        by_severity = Counter(f["severity"] for f in findings)
        return {"items": items, "accounted": accounted, "findings": findings,
                "coverage": {"by_kind": coverage, "must_use": must, "must_use_accounted": must_ok,
                             "share": round(accounted / items, 4) if items else 1.0},
                "summary": {"by_check": {c: by_check.get(c, 0) for c in CHECKS},
                            "by_severity": {s: by_severity.get(s, 0) for s in SEVERITIES},
                            "by_check_severity": {f"{c}/{s}": n for (c, s), n in
                                                  sorted(Counter((f["check"], f["severity"])
                                                                 for f in findings).items())}}}


def ledger(building: dict, source_items: Optional[dict]) -> dict:
    """The source ledger of a building against the inventory of its documents (module docstring)."""
    return _Ledger(building, source_items or {}).run()


def ledger_for(out_dir, building_name: str = "building.json") -> dict:
    """``ledger`` on a run folder: ``<out>/<building_name>`` and ``<out>/source_items.json``."""
    out = Path(out_dir)
    building = json.loads((out / building_name).read_text(encoding="utf-8"))
    path = out / "source_items.json"
    items = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
    return ledger(building, items)


def summary_lines(result: dict, limit: int = 40) -> list[str]:
    """A short text report: the counts, then the critical and major findings."""
    s = result["summary"]
    lines = [f"items {result['items']}, accounted {result['accounted']} ({result['coverage']['share']:.1%}); "
             f"must-use {result['coverage']['must_use']}, accounted {result['coverage']['must_use_accounted']}",
             "by severity: " + ", ".join(f"{k} {v}" for k, v in s["by_severity"].items()),
             "by check: " + ", ".join(f"{k} {v}" for k, v in s["by_check"].items() if v)]
    shown = [f for f in result["findings"] if f["severity"] != "minor"][:limit]
    for f in shown:
        lines.append(f"[{f['severity']}] {f['check']} {f['target']}: {f['message']}")
    return lines


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Source ledger: every item of the documents is used or explained")
    parser.add_argument("out_dir", help="a run folder with building.json and source_items.json")
    parser.add_argument("--building", default="building.json", help="building file in the run folder")
    parser.add_argument("--json", default=None, help="write the full result here")
    parser.add_argument("--all", action="store_true", help="print the minor findings too")
    args = parser.parse_args(argv)
    result = ledger_for(args.out_dir, args.building)
    if args.json:
        Path(args.json).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    for line in summary_lines(result, limit=10 ** 6 if args.all else 40):
        print(line)
    if args.all:
        for f in result["findings"]:
            if f["severity"] == "minor":
                print(f"[minor] {f['check']} {f['target']}: {f['message']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


def run(inp) -> dict:
    """The line for ``wenart.audit.report`` (Argus): the building as built (the scene's, else the last stage's)
    against the run's ``source_items.json`` (``<out>/`` on the pod, ``furniture/<p>/`` in a collected run)."""
    building = inp.stage("build") or inp.final
    if not building:
        return {"findings": [], "checked": {}, "note": "no building"}
    root = Path(inp.root)
    path = root / "source_items.json" if inp.layout == "pod" else root / "furniture" / inp.project / "source_items.json"
    if not path.is_file():
        return {"findings": [], "checked": {}, "note": "no source_items.json (the reading wrote no inventory)"}
    res = ledger(building, json.loads(path.read_text(encoding="utf-8")))
    return {"findings": res.get("findings") or [], "checked": res.get("coverage") or res.get("summary") or {}}
