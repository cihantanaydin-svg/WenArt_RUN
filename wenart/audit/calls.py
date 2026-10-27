"""Argus, its own tool calls made valid before they run (27 Oct 2026, user: "make Argus fix everything itself, give it
more power"; pod run 20261026-224516-full: 0 of Argus's 94 edits were accepted, most for arguments no tool takes:
camera kind 'room' 35 times, a pose at the room's origin, a piece id as a view id, a centre 'drawn', a site 'trees'
string, a group 'living', 13 catalogue models it invented).

What:

- ``tool_help``: each tool Argus may call with every argument's type, its allowed values and ranges (``shape``: the
  JSON schema as one short text) and the tool's whole description, not only the argument names;
- ``Valid``: the values a call may use in this project, from the building and the scene: the camera views by room
  (frozen ones marked), the material looks by slot, the ground looks, the catalogue models a piece may swap to (the
  fit's accepted candidates first, then the models of its type closest to its size), the piece, room and opening ids;
  ``Valid.lines`` puts them to the model;
- ``vet``: one call checked by code before the agent loop runs it: first the code's own repairs (``fix_args``: a
  camera's kind and room from the scene, a piece named as the view becomes what the view must ``show`` in its room's
  view, an interior pose the camera checks refuse becomes ``show`` of the finding's pieces or the room's main pieces so
  the code picks the pose, a group word the program knows under another name, an optional argument that does not match
  its schema left out), then its schema (``vlm_client.schema_errors``) and its ids (``id_errors``: no such piece,
  room, view, look or model, with the valid ones named);
- ``vet_all``: every call of an investigation: the same call twice once, one call per camera view, the valid ones kept,
  the others put to the model in one repair call (``repair``) with the errors and the valid values; a call still
  invalid after it is dropped with its errors (its finding stays for the agent's round).

Why: a call that cannot pass its schema is a wasted try of the round and an "edit refused" in the log; the model is good
at choosing the fix and bad at guessing ids and coordinates, so the code gives both.
"""
from __future__ import annotations

import copy
import json
import re
from typing import Callable, Optional

CAMERA_TOOLS = ("set_camera", "add_camera", "remove_camera")
POSE_TOOLS = ("set_camera", "add_camera")
TOOL_DESC_CHARS = 420          # a tool's description in the help (the whole of most)
MODEL_OPTIONS = 5              # catalogue models shown per piece
SHOW_DEFAULT = 2               # the room's main pieces a view shows when the finding names none
REPAIR_MAX = 40                # invalid calls put to the one repair call
REPAIR_TOKENS = 4096
PIECE_RE = re.compile(r"\b(f_L-?\d+[a-z]?_\d+[a-z0-9_]*)\b")
OPENING_RE = re.compile(r"\b((?:d|o|win|w)_L-?\d+[a-z]?_\d+)\b")
# a group word the model uses -> the program's group (place_group's enum)
GROUP_WORDS = {"living": "seating", "lounge": "seating", "sofa": "seating", "sitting": "seating",
               "bed": "sleeping_double", "bedroom": "sleeping_double", "double_bed": "sleeping_double",
               "single_bed": "sleeping_single", "kitchen": "kitchen_run", "kitchen_set": "kitchen_run",
               "bathroom": "bathroom_set", "bath": "bathroom_set", "toilet": "wc_set", "wc": "wc_set",
               "desk": "work", "office": "work", "study": "work", "wardrobe": "dressing", "closet": "dressing",
               "hall": "entrance", "foyer": "entrance", "dining_set": "dining", "table": "dining"}


# ---------------------------------------------------------------------------------------------------- the help
def shape(s) -> str:
    """A JSON-schema property as one short text: its type, allowed values, range or item shape (pure)."""
    if not isinstance(s, dict):
        return "any"
    if "enum" in s:
        return "one of " + "|".join(str(v) for v in s["enum"])
    if "const" in s:
        return json.dumps(s["const"])
    t = s.get("type")
    if isinstance(t, list):
        t = "|".join(str(x) for x in t)
    if t == "array":
        item = shape(s.get("items") or {})
        lo, hi = s.get("minItems"), s.get("maxItems")
        if lo is not None and lo == hi and lo <= 4:
            return "[" + ", ".join([item] * int(lo)) + "]"
        return f"list of {item}" + (f" ({lo if lo is not None else 0}-{hi if hi is not None else 'n'})"
                                    if lo is not None or hi is not None else "")
    if t == "object":
        props = s.get("properties") or {}
        if props:
            req = set(s.get("required") or [])
            inner = ", ".join(f"{k}{'*' if k in req else ''}: {shape(v)}" for k, v in props.items())
            return "{" + inner + "}" + (" (at least one key)" if s.get("minProperties") else "")
        extra = s.get("additionalProperties")
        return "{name: " + shape(extra) + "}" if isinstance(extra, dict) else "object"
    text = str(t or "any")
    if t in ("number", "integer"):
        lo = s.get("minimum", s.get("exclusiveMinimum"))
        hi = s.get("maximum")
        if lo is not None or hi is not None:
            text += f" {lo if lo is not None else ''}..{hi if hi is not None else ''}"
    if s.get("description"):
        text += f" ({str(s['description'])[:120]})"
    return text


def tool_help(registry, names) -> list[str]:
    """One line per tool: ``name(arg*: shape; ...): description`` (``*`` required; ``reason`` is filled by the loop)."""
    out = []
    for name in names:
        t = registry.tools.get(name)
        if t is None:
            continue
        props = (t.parameters or {}).get("properties") or {}
        req = set((t.parameters or {}).get("required") or [])
        params = "; ".join(f"{k}{'*' if k in req else ''}: {shape(v)}" for k, v in props.items() if k != "reason")
        out.append(f"- {name}({params}): {str(getattr(t, 'description', '') or '')[:TOOL_DESC_CHARS]}")
    return out


# ---------------------------------------------------------------------------------------------------- the values
class Valid:
    """The values a call may use in this project (module docstring). ``catalog``: ``wenart.furniture.catalog``'s
    ``Catalog`` (None: loaded on first use; a failure leaves the model ids unchecked)."""

    def __init__(self, building: Optional[dict], manifest: Optional[dict], catalog=None):
        self.building = building or {}
        self.cameras = [c for c in (manifest or {}).get("cameras") or [] if isinstance(c, dict) and c.get("name")]
        self.pieces = {f["id"]: f for f in self.building.get("furniture") or [] if f.get("id")}
        self.rooms = {r["id"]: r for r in self.building.get("rooms") or [] if r.get("id")}
        self.openings = {o["id"]: o for o in self.building.get("openings") or [] if o.get("id")}
        self._catalog = catalog
        self._catalog_failed = False

    # -- cameras
    def camera(self, view_id) -> Optional[dict]:
        return next((c for c in self.cameras if c.get("name") == str(view_id)), None)

    def views_of(self, room_id) -> list[dict]:
        return [c for c in self.cameras if c.get("room_id") == room_id]

    @staticmethod
    def frozen(cam: Optional[dict]) -> bool:
        from wenart.agent import causes as CS
        return CS.frozen_camera(cam)

    # -- looks
    @staticmethod
    def looks_by_kind() -> dict:
        from wenart.style import profile as P
        out: dict = {}
        for slug, e in P.V.MATERIALS.items():
            out.setdefault(str(e.get("kind")), []).append(slug)
        return out

    @staticmethod
    def slot_kinds() -> dict:
        from wenart.blender import exterior_checks as XC
        return dict(XC.SLOT_KINDS)

    def looks_for(self, slot: str) -> list[str]:
        from wenart.blender import exterior_checks as XC
        kinds = self.slot_kinds().get(XC.SLOT_ALIASES.get(slot, slot)) or ()
        by = self.looks_by_kind()
        return [s for k in kinds for s in by.get(k, [])]

    # -- models
    def catalog(self):
        if self._catalog is None and not self._catalog_failed:
            try:
                from wenart.furniture import catalog as C
                self._catalog = C.load()
            except Exception:  # noqa: BLE001 - no catalogue here: model ids stay unchecked
                self._catalog_failed = True
        return self._catalog

    def model_options(self, piece: Optional[dict], n: int = MODEL_OPTIONS) -> list[str]:
        """``"id (w x d x h m, styles)"`` of the models ``piece`` may swap to: the fit's accepted candidates other
        than its model, then the catalogue's models of its type and of the project's style chain closest to its
        footprint."""
        if not piece:
            return []
        asset = piece.get("asset") if isinstance(piece.get("asset"), dict) else {}
        current = {asset.get("asset_id"), piece.get("asset_pin")}
        ids = [c.get("id") for c in asset.get("candidates") or [] if isinstance(c, dict) and c.get("accepted")
               and c.get("id") not in current]
        cat = self.catalog()
        entries = []
        if cat is not None:
            try:
                entries = list(cat.candidates(str(piece.get("type"))))
            except Exception:  # noqa: BLE001
                entries = []
        size = ((piece.get("footprint") or {}).get("size") or [0, 0])[:2]

        def dist(e):
            bb = e.get("bbox_m") or [0, 0, 0]
            try:
                return abs(float(bb[0]) - float(size[0])) + abs(float(bb[1]) - float(size[1]))
            except (TypeError, ValueError, IndexError):
                return 99.0
        try:                     # only models of the project's style chain, never rated below the current one
            from wenart.furniture import edit_ops as EO
            now = cat.entry(asset.get("asset_id")) if cat is not None and asset.get("asset_id") else None
            entries = [e for e in entries if EO.off_style_refusal(self.building, e) is None
                       and EO.lower_quality_refusal(now, e) is None]
            if cat is not None:
                ids = [i for i in ids if i in {e.get("id") for e in entries}]
        except Exception:  # noqa: BLE001
            pass
        by_id = {e.get("id"): e for e in entries}
        ids += [e.get("id") for e in sorted(entries, key=dist) if e.get("id") not in current]
        out = []
        for i in dict.fromkeys(x for x in ids if x):
            e = by_id.get(i) or {}
            bb = e.get("bbox_m") or []
            out.append(f"{i}" + (f" ({' x '.join(f'{float(v):.2f}' for v in bb[:3])} m"
                                 + (f", {'/'.join(e.get('styles') or [])}" if e.get("styles") else "") + ")"
                                 if bb else ""))
            if len(out) >= n:
                break
        return out

    def model_ok(self, asset_id: str, piece: Optional[dict]) -> Optional[str]:
        """None when ``asset_id`` is a catalogue model of the piece's type (or no catalogue is here), else why not."""
        cat = self.catalog()
        if cat is None:
            return None
        try:
            entry = cat.entry(asset_id)
        except Exception:  # noqa: BLE001
            return None
        if entry is None:
            return f"no catalogue model {asset_id!r}"
        if piece and entry.get("type") != piece.get("type"):
            return f"{asset_id} is a {entry.get('type')} model, not a {piece.get('type')}"
        return None

    # -- the prompt lines
    def lines(self) -> list[str]:
        out = ["", "Valid values (use only these; never invent an id):"]
        rooms: dict = {}
        for c in self.cameras:
            rooms.setdefault(c.get("room_id") or "exterior", []).append(
                str(c["name"]) + (" (frozen: add_camera instead)" if self.frozen(c) else ""))
        if rooms:
            out.append("- camera views (view_id) by room: " + "; ".join(f"{r}: {', '.join(v)}"
                                                                        for r, v in rooms.items()))
        out.append("- an interior view: set_camera {view_id, show: [the piece, door or window ids it must show]}, "
                   "never position or target (the code picks the free pose that shows them); add_camera {view_id: "
                   "cam_<room id>_<n>, room_id, show}; an exterior view (ext_*) needs position and target")
        try:
            by_kind = self.looks_by_kind()
            out.append("- material looks by kind: " + "; ".join(f"{k}: {', '.join(v)}" for k, v in by_kind.items()))
            out.append("- the kinds a slot takes: " + "; ".join(f"{s}: {'|'.join(k)}"
                                                                for s, k in self.slot_kinds().items()))
        except Exception:  # noqa: BLE001 - no look vocabulary here
            pass
        return out


# ---------------------------------------------------------------------------------------------------- the checks
def _room_of(valid: Valid, args: dict, finding: Optional[dict]) -> Optional[str]:
    for key in ("room_id",):
        if args.get(key) in valid.rooms:
            return args[key]
    t = str((finding or {}).get("target") or "")
    if t in valid.rooms:
        return t
    if t in valid.pieces:
        return valid.pieces[t].get("room_id")
    if (finding or {}).get("room_id") in valid.rooms:
        return finding["room_id"]
    return None


def _show_ids(valid: Valid, room_id: str, args: dict, finding: Optional[dict]) -> list[str]:
    """The elements a view of ``room_id`` must show: ``show`` of the call, else the pieces of the room the finding
    names (its target, its message), else the room's main pieces (``camsearch.type_weight``)."""
    here = {i for i, f in valid.pieces.items() if f.get("room_id") == room_id and f.get("build") is not False}
    from wenart.agent.tools import show_ids
    ids = [i for i in show_ids(valid.building, room_id, args.get("show") or []) if i in here or i in valid.openings]
    if ids:
        return ids[:6]
    message = str((finding or {}).get("message") or "")
    named = [str((finding or {}).get("target") or "")] + PIECE_RE.findall(message) + OPENING_RE.findall(message)
    ids = [i for i in dict.fromkeys(named) if i in here or i in valid.openings]
    if not ids:                                   # "the washbasin is missing from the frame": the room's washbasin
        low = message.lower()
        ids = [i for i in sorted(here) if any(re.search(rf"\b{re.escape(w)}", low)
                                              for w in type_words(valid.pieces[i].get("type")))]
    if ids:
        return ids[:6]
    try:
        from wenart.blender import camsearch as CSR
        weight = CSR.type_weight
    except Exception:  # noqa: BLE001
        def weight(_t):
            return 1.0
    ranked = sorted(here, key=lambda i: (-float(weight(valid.pieces[i].get("type"))), i))
    return ranked[:SHOW_DEFAULT]


HEAD_FIRST = ("bed", "table", "sofa", "sink", "bar")


def type_words(ftype) -> list[str]:
    """The words a message uses for a piece type: ``bed_double`` -> "bed double", "bed"; ``kitchen_counter`` ->
    "kitchen counter", "counter"; ``washbasin`` -> "washbasin", "basin" (pure)."""
    t = str(ftype or "").lower()
    if not t or t in ("unknown", "other"):
        return []
    parts = t.split("_")
    words = [" ".join(parts), parts[0] if parts[0] in HEAD_FIRST else parts[-1]]
    if t.endswith("basin"):
        words.append("basin")
    return list(dict.fromkeys(w for w in words if len(w) >= 3))


def fix_args(tool: str, args: dict, valid: Valid, registry, finding: Optional[dict] = None) -> tuple[dict, list[str]]:
    """``(args, repairs)``: the code's own repairs of one call (module docstring), each named in ``repairs``."""
    args = copy.deepcopy(args or {})
    notes: list[str] = []
    if tool in CAMERA_TOOLS:
        vid = str(args.get("view_id") or "")
        cam = valid.camera(vid)
        if cam is None and tool != "add_camera":
            room = _room_of(valid, args, finding)
            if vid in valid.pieces:                       # a piece named as the view: show it in its room's view
                args.setdefault("show", [vid])
                room = valid.pieces[vid].get("room_id") or room
            elif vid in valid.rooms:
                room = vid
            views = [c for c in valid.views_of(room) if not valid.frozen(c)] if room else []
            if views:
                args["view_id"] = views[0]["name"]
                cam = views[0]
                notes.append(f"view_id {vid or '(none)'} is no view: {room}'s view {views[0]['name']}")
        if tool != "remove_camera":
            kind = args.get("kind")
            want = (cam or {}).get("kind") or ("interior" if (cam or {}).get("room_id") or
                                               (tool == "add_camera" and args.get("room_id")) else
                                               "exterior" if cam is not None else None)
            if want and kind != want:
                args["kind"] = want
                notes.append(f"kind {kind!r} -> {want} (the view's)")
            if args.get("kind") == "interior":
                room = (cam or {}).get("room_id") or _room_of(valid, args, finding)
                if room and args.get("room_id") != room:
                    args["room_id"] = room
                    notes.append(f"room_id -> {room} (the view's)")
                posed = args.get("position") is not None or args.get("target") is not None
                if room and args.get("show") and not posed:
                    ids = _show_ids(valid, room, args, finding)       # type names -> the room's pieces (27 Oct)
                    if ids and ids != [str(i) for i in args["show"]]:
                        notes.append(f"show {', '.join(str(i) for i in args['show'])[:80]} -> {', '.join(ids)}")
                        args["show"] = ids
                if room and (posed or not args.get("show")) and not _pose_ok(valid, args):
                    args.pop("position", None)
                    args.pop("target", None)
                    args["show"] = _show_ids(valid, room, args, finding)
                    notes.append(f"the pose is left to the code: show {', '.join(args['show'])}" if args["show"]
                                 else "the pose is left to the code")
                    if not args["show"]:
                        args.pop("show")
                if args.get("show") and args.pop("lens_mm", None) is not None:
                    notes.append("lens_mm left out: the room's lens rule (18 / 16 mm, CLAUDE.md camera policy)")
            elif args.get("kind") == "exterior" and args.pop("show", None) is not None:
                notes.append("show is for interior views: left out")
    if tool == "place_group" and isinstance(args.get("group"), str):
        enum = (((registry.tools.get(tool).parameters or {}).get("properties") or {}).get("group") or {}).get("enum")
        g = args["group"].strip().lower()
        if enum and g not in enum and GROUP_WORDS.get(g) in enum:
            notes.append(f"group {args['group']!r} -> {GROUP_WORDS[g]}")
            args["group"] = GROUP_WORDS[g]
    t = registry.tools.get(tool)
    params = (t.parameters if t is not None else None) or {}
    props = params.get("properties") or {}
    req = set(params.get("required") or [])
    if params.get("additionalProperties") is False:
        for k in [k for k in args if k not in props]:
            args.pop(k)
            notes.append(f"{k} is no argument of {tool}: left out")
    from wenart.recognition.vlm_client import schema_errors
    for k in [k for k in args if k in props and k not in req and k != "reason"]:
        if schema_errors(props[k], args[k]):
            notes.append(f"{k} {json.dumps(args[k], ensure_ascii=False)[:60]} does not match {shape(props[k])[:80]}: "
                         f"left out")
            args.pop(k)
    return args, notes


def _pose_ok(valid: Valid, args: dict) -> bool:
    """An interior pose given by the model that the camera checks accept (False: no pose, or a refused one)."""
    if args.get("position") is None or args.get("target") is None:
        return False
    try:
        from wenart.blender import exterior_checks as XC
        entry = {k: v for k, v in args.items() if k not in ("show",)}
        entry.setdefault("reason", "check")
        return bool((XC.validate_camera_override(valid.building, dict(entry, action="set")) or {}).get("ok"))
    except Exception:  # noqa: BLE001 - no check here: the pose stays
        return True


def id_errors(tool: str, args: dict, valid: Valid) -> list[str]:
    """The ids of a call that are none of this project's (with the valid ones named)."""
    out = []
    pid = args.get("piece_id")
    if pid is not None and pid not in valid.pieces:
        out.append(f"piece_id: no piece {pid!r}")
    rid = args.get("room_id")
    if rid is not None and tool not in POSE_TOOLS and rid not in valid.rooms:
        out.append(f"room_id: no room {rid!r} (rooms: {', '.join(list(valid.rooms)[:30])})")
    if tool in POSE_TOOLS and rid is not None and args.get("kind") == "interior" and rid not in valid.rooms:
        out.append(f"room_id: no room {rid!r}")
    vid = args.get("view_id")
    if tool in ("set_camera", "remove_camera") and vid is not None and valid.cameras and valid.camera(vid) is None:
        out.append(f"view_id: no view {vid!r} (views: {', '.join(c['name'] for c in valid.cameras[:40])})")
    if tool == "set_camera" and valid.frozen(valid.camera(vid)):
        out.append(f"view_id: {vid} is frozen (a replayed camera): add_camera with a new view id instead")
    if tool == "add_camera" and vid is not None and valid.camera(vid) is not None:
        out.append(f"view_id: {vid} exists already (add_camera takes a new id; set_camera moves it)")
    if tool == "fix_fixture" and pid in valid.pieces:
        try:                       # 27 Oct 2026 (pod run 091638: 6 of Argus's 15 fix_fixture calls named a chair)
            from wenart.furniture import edit_ops as EO
            piece = valid.pieces[pid]
            if not EO._fixed(piece):
                out.append(f"piece_id: {pid} is a {piece.get('type')}, no drawn fixed equipment (stairs, kitchen runs, "
                           f"sanitary ware): move it with move_piece, turn it with rotate_piece, size it with "
                           f"resize_piece")
        except Exception:  # noqa: BLE001
            pass
    if tool == "swap_model" and args.get("asset_id"):
        why = valid.model_ok(str(args["asset_id"]), valid.pieces.get(pid))
        if why:
            opts = valid.model_options(valid.pieces.get(pid))
            out.append(f"asset_id: {why}" + (f" (models it may take: {', '.join(o.split(' ')[0] for o in opts)})"
                                             if opts else ""))
    if tool == "set_material" and args.get("slot") and args.get("look_id"):
        try:
            looks = valid.looks_for(str(args["slot"]))
            if looks and args["look_id"] not in looks:
                out.append(f"look_id: {args['look_id']!r} is no look of the slot {args['slot']} (its looks: "
                           f"{', '.join(looks)})")
        except Exception:  # noqa: BLE001
            pass
    if tool == "set_exterior" and isinstance(args.get("ground"), str):
        try:
            grounds = valid.looks_for("ground")
            if grounds and args["ground"] not in grounds:
                out.append(f"ground: {args['ground']!r} is no ground look (the ground looks: {', '.join(grounds)})")
        except Exception:  # noqa: BLE001
            pass
    if tool in POSE_TOOLS and args.get("kind") == "interior" and not args.get("show") \
            and (args.get("position") is None or args.get("target") is None):
        out.append("an interior view needs show (the pieces it must show) or a position and a target")
    if tool in POSE_TOOLS and args.get("kind") == "exterior" and (args.get("position") is None
                                                                   or args.get("target") is None):
        out.append("an exterior view needs position and target")
    return out


def vet(action: dict, valid: Valid, registry, finding: Optional[dict] = None) -> tuple[dict, list[str], list[str]]:
    """``(action, errors, repairs)`` of one call: the code's repairs, then its schema and its ids (module docstring).
    ``errors`` empty: the call is valid."""
    from wenart.recognition.vlm_client import schema_errors

    tool = action.get("tool")
    t = registry.tools.get(tool)
    if t is None:
        return action, [f"no tool {tool!r}"], []
    args, notes = fix_args(tool, action.get("args") or {}, valid, registry, finding)
    trial = dict(args)
    trial.setdefault("reason", "Argus: check")             # the loop fills the reason
    errors = schema_errors(t.parameters, trial) + id_errors(tool, args, valid)
    if not [k for k in args if k != "reason"] and [k for k in (action.get("args") or {}) if k != "reason"]:
        errors.append(f"no argument of {tool} is left (each one was wrong)")
    out = dict(action, args=args)
    if notes:
        out["repaired"] = list(action.get("repaired") or []) + notes
    return out, errors, notes


def _key(a: dict) -> tuple:
    return a.get("tool"), json.dumps(a.get("args") or {}, sort_keys=True, ensure_ascii=False)


def vet_all(model, actions: list[dict], valid: Valid, registry, findings: Optional[dict] = None, *,
            help_lines: Optional[list] = None, errors: Optional[list] = None,
            time_ok: Callable[[], bool] = lambda: True, thinking: bool = False) -> tuple[list[dict], dict]:
    """``(valid actions, counts)`` of module docstring: every call vetted, the invalid ones repaired by the model in one
    call, the rest dropped (``errors`` gets each with its reasons). ``findings``: ``{finding_id: finding}`` (what a
    camera must show)."""
    errors = errors if errors is not None else []
    findings = findings or {}
    good, bad, seen, views = [], [], set(), set()
    counts = {"calls": len(actions), "valid": 0, "code_repaired": 0, "model_repaired": 0, "dropped": 0,
              "duplicates": 0}

    def keep(a: dict) -> bool:
        k = _key(a)
        vid = a["args"].get("view_id") if a.get("tool") in CAMERA_TOOLS else None
        if k in seen or (vid and vid in views):
            counts["duplicates"] += 1
            return False
        seen.add(k)
        if vid:
            views.add(vid)
        return True

    for a in actions:
        v, errs, notes = vet(a, valid, registry, findings.get(a.get("finding_id")))
        if errs:
            bad.append((v, errs))
            continue
        if keep(v):
            good.append(v)
            counts["code_repaired"] += bool(notes)
    if bad and model is not None and time_ok():
        fixed = repair(model, bad[:REPAIR_MAX], valid, registry, help_lines or [], errors=errors, thinking=thinking)
        still = []
        for n, (v, errs) in enumerate(bad[:REPAIR_MAX]):
            new = fixed.get(n)
            if new is None:
                still.append((v, errs))
                continue
            v2, errs2, _notes = vet(dict(v, args=new), valid, registry, findings.get(v.get("finding_id")))
            if errs2:
                still.append((v2, errs2))
            elif keep(v2):
                v2["repaired"] = list(v2.get("repaired") or []) + ["the model repaired its call"]
                good.append(v2)
                counts["model_repaired"] += 1
        bad = still + bad[REPAIR_MAX:]
    for v, errs in bad:
        counts["dropped"] += 1
        errors.append(f"{v.get('finding_id')} {v.get('tool')} dropped: {'; '.join(errs[:3])}"[:300])
    counts["valid"] = len(good)
    return good, counts


REPAIR_SYSTEM = (
    "You are Argus, the auditor of a pipeline that builds a furnished 3D house from an architect's drawings. Code "
    "refused some of your tool calls before they ran: for each, give the corrected arguments as a JSON object in args "
    "(the same tool, the same aim), using only the valid values and the argument shapes you are given; for an "
    "interior camera give show (the pieces it must show), never coordinates. Set drop = true when no correct call of "
    "that tool can do what you wanted.")


def repair(model, bad: list[tuple[dict, list[str]]], valid: Valid, registry, help_lines: list[str], *,
           errors: Optional[list] = None, thinking: bool = False) -> dict:
    """``{index: args}`` of the calls the model corrected in one structured call (the others: none)."""
    errors = errors if errors is not None else []
    ids = [str(n) for n in range(len(bad))]
    schema = {"type": "object", "additionalProperties": False, "required": ["items"],
              "properties": {"items": {"type": "array", "items": {
                  "type": "object", "additionalProperties": False, "required": ["id", "args", "drop"],
                  "properties": {"id": {"type": "string", "enum": ids}, "args": {"type": "string"},
                                 "drop": {"type": "boolean"}}}}}}
    tools = sorted({v.get("tool") for v, _e in bad})
    rows = [{"id": str(n), "tool": v.get("tool"), "args": v.get("args"), "refused_because": errs[:4],
             "fixes": v.get("why") or v.get("finding_id"),
             **({"models_it_may_take": valid.model_options(valid.pieces.get((v.get("args") or {}).get("piece_id")))}
                if v.get("tool") == "swap_model" else {})}
            for n, (v, errs) in enumerate(bad)]
    text = "\n".join(["The tools (arguments: * required):", *[h for h in help_lines
                                                                if any(h.startswith(f"- {t}(") for t in tools)],
                      *valid.lines(), "", "The refused calls:", json.dumps(rows, indent=1, ensure_ascii=False)])
    try:
        reply = model.structured([{"role": "system", "content": REPAIR_SYSTEM}, {"role": "user", "content": text}],
                                 schema, call_id="argus_repair", name="argus_repair", kind="task", thinking=thinking,
                                 max_tokens=REPAIR_TOKENS)
    except Exception as exc:  # noqa: BLE001 - no repair: the calls are dropped with their errors
        errors.append(f"repair: {type(exc).__name__}: {exc}"[:300])
        return {}
    out = {}
    for item in (reply.data or {}).get("items") or []:
        if item.get("drop"):
            continue
        try:
            args = json.loads(item.get("args") or "{}")
        except ValueError:
            continue
        if isinstance(args, dict):
            out[int(item["id"])] = args
    return out
