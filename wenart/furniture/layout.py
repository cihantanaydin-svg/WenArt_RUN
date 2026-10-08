"""AI layout for rooms the documents leave empty (docs/milestone4.md section 3).

Flow per room with ``has_documented_furniture: false`` and a furnishable
room type: two text-only calls to the vLLM server (pass 1 and pass 2 with a
different block order and seed, temperature 0, the layout schema as the
structured-output grammar), each answer validated against the schema and
checked and repaired by ``placer.py``. The proposal with the fewest dropped
pieces wins (ties: pass 1). A piece that the other pass also proposed (same
type, centre within 0.5 m) gets confidence 0.9, the rest 0.6. Added pieces
are ``source: added_by_ai``, ``status: verified`` with evidence
``{method: ai, model, pass, text: <reason>}`` and the six placer checks, all
true. A room whose answers are unusable stays empty and the report says so.
Milestone 7 (docs/milestone7.md §0, §6.5): ``dining`` rooms are furnished
like the others (anchor: the dining table); a ``prayer`` room is never
furnished by AI: it is listed as skipped with the reason, never asked.
A pass whose last attempt could not reach the server (``VLMError``, or the
model lookup failed) is a transport error, not an answer: the CLI then exits
3 and writes no furnished building, so a dead server never yields a
"furnished" building with empty rooms (docs/milestone6.md §2.6).

The request goes through ``wenart.recognition.vlm_client`` (``post_json``,
``parse_answer``, ``served_models``); the only difference to the recognition
tasks is that the user message is text only, which the OpenAI chat format
allows as a plain string.

CLI: ``python -m wenart.furniture.layout outputs/<p>/building.json --style
outputs/<p>/style.json --server http://127.0.0.1:8001/v1 --model
Qwen/Qwen3-VL-8B-Instruct --out outputs/<p>/building_furnished.json --debug
outputs/<p>/layout_debug/`` writes the furnished building, ``layout.json``
and ``layout_report.md`` next to it and one PNG + JSON per room in the debug
folder.

Milestone 10 (docs/milestone10.md §1.6a, §2): the same run, with the same
client, also completes the rooms with drawn furniture
(``wenart.furniture.complete``; ``LayoutClient.complete`` asks with the
room's own schema). The brief keys ``furnished_rooms``,
``furnished_rooms_keep``, ``furnished_rooms_keep_size`` and
``render.twin_rooms`` come from ``wenart.brief.load_brief`` of
``--project-dir`` (default: the building's ``project.source_folder``). An
empty room whose partner (``same_as``, or ``twin_of`` with ``twin_rooms:
one``) is an empty room too takes the partner's layout (copied, mirrored for
twins) instead of being asked. The CLI also writes ``completion.json`` and
``completion_report.md`` and runs ``locked.check(source, final, mode)``: a
violation writes no furnished building and exits 1 (the reports list it); a
transport error in either part still exits 3 with no output.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from wenart import building as B
from wenart import geometry as G
from wenart.furniture import placer, prompts, schemas
from wenart.recognition import vlm_client

DEFAULT_SERVER = "http://127.0.0.1:8001/v1"
DEFAULT_MODEL = "Qwen/Qwen3-VL-8B-Instruct"
DEFAULT_MAX_TOKENS = 2048
AGREE_DISTANCE_M = 0.5
CONFIDENCE_AGREED = 0.9
CONFIDENCE_SINGLE = 0.6
EVIDENCE_FILE = "building.json"   # what the model saw: the room, doors and windows of the building JSON


# --------------------------------------------------------------------------
# Client (text-only chat completion with structured output)
# --------------------------------------------------------------------------

@dataclass
class Proposal:
    """One model pass for one room."""
    pass_no: int
    data: Optional[dict]            # schema-valid answer or None
    raw_text: str = ""
    latency_s: float = 0.0
    error: Optional[str] = None
    prompt: str = ""
    model: str = ""
    rejected_types: list = field(default_factory=list)   # proposed types the room type does not allow
    transport_error: bool = False   # the last attempt raised VLMError (or the model lookup failed)

    def to_dict(self) -> dict:
        return {"pass": self.pass_no, "model": self.model, "latency_s": round(self.latency_s, 3),
                "error": self.error, "pieces_proposed": len(self.data["pieces"]) if self.data else 0}


def build_text_request(model: str, prompt: str, schema: dict, *, seed: int = 0, temperature: float = 0.0,
                       max_tokens: int = DEFAULT_MAX_TOKENS, system_prompt: str = prompts.SYSTEM_PROMPT) -> dict:
    """JSON body for ``POST /v1/chat/completions`` without an image (fields as in vlm_client.build_request)."""
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "seed": seed,
        "max_tokens": max_tokens,
        "structured_outputs": {"json": schema},
        "chat_template_kwargs": {"enable_thinking": False},
    }


class LayoutClient:
    """Asks the vLLM server for a layout. ``propose(prompt, pass_no)`` -> Proposal."""

    def __init__(self, base_url: str = DEFAULT_SERVER, model: Optional[str] = None, *,
                 timeout_s: float = 600.0, retries: int = 3, max_tokens: int = DEFAULT_MAX_TOKENS) -> None:
        self.base_url = base_url.rstrip("/")
        self._model = model
        self.timeout_s = timeout_s
        self.retries = max(1, retries)
        self.max_tokens = max_tokens

    @property
    def model(self) -> str:
        if self._model is None:
            models = vlm_client.served_models(self.base_url)
            if not models:
                raise vlm_client.VLMError(f"no model served at {self.base_url}")
            self._model = models[0]
        return self._model

    def propose(self, prompt: str, pass_no: int) -> Proposal:
        """An empty room's layout (the Milestone 4 schema)."""
        return self._ask(prompt, pass_no, schemas.grammar_schema(), schemas.validation_errors, prompts.SYSTEM_PROMPT)

    def complete(self, prompt: str, schema: dict, pass_no: int) -> Proposal:
        """Milestone 10: the completion of a room with drawn furniture (the room's own strict schema)."""
        import jsonschema

        def errors(data) -> list[str]:
            validator = jsonschema.Draft202012Validator(schema)
            return [f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
                    for e in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))]

        return self._ask(prompt, pass_no, schema, errors, prompts.COMPLETION_SYSTEM_PROMPT)

    def _ask(self, prompt: str, pass_no: int, schema: dict, validation_errors, system_prompt: str) -> Proposal:
        try:
            model = self.model
        except vlm_client.VLMError as exc:
            return Proposal(pass_no, None, error=str(exc), prompt=prompt, model="?", transport_error=True)
        body = build_text_request(model, prompt, schema, seed=pass_no, max_tokens=self.max_tokens,
                                  system_prompt=system_prompt)
        url = self.base_url + "/chat/completions"
        t0 = time.monotonic()
        raw_text, error, parsed = "", None, None
        transport = False
        for attempt in range(1, self.retries + 1):
            try:
                resp = vlm_client.post_json(url, body, self.timeout_s)
                raw_text = resp["choices"][0]["message"].get("content") or ""
                parsed = vlm_client.parse_answer(raw_text)
                error = None
                transport = False
                break
            except vlm_client.VLMError as exc:
                error = str(exc)
                transport = True
                if attempt < self.retries:
                    time.sleep(min(30.0, 2.0 * attempt))
            except (KeyError, IndexError, json.JSONDecodeError, ValueError) as exc:
                error = f"bad answer: {exc}"
                transport = False
        latency = time.monotonic() - t0
        data = None
        if parsed is not None:
            problems = validation_errors(parsed)
            if problems:
                error = "schema: " + "; ".join(problems[:5])
            else:
                data = parsed
        return Proposal(pass_no, data, raw_text=raw_text, latency_s=latency, error=error, prompt=prompt, model=model,
                        transport_error=transport)


# --------------------------------------------------------------------------
# Per room
# --------------------------------------------------------------------------

@dataclass
class RoomLayout:
    room_id: str
    label: str
    room_type: str
    proposals: list[Proposal] = field(default_factory=list)
    placements: dict = field(default_factory=dict)       # pass_no -> PlacementResult
    chosen_pass: Optional[int] = None
    pieces: list[dict] = field(default_factory=list)     # building furniture dicts
    skipped: Optional[str] = None                        # why the room got nothing
    context: Optional[placer.RoomContext] = None
    copied_from: Optional[dict] = None                   # Milestone 10: the partner whose layout this room took
    copy_dropped: list = field(default_factory=list)     # Milestone 10: copies that failed a check here

    @property
    def latency_s(self) -> float:
        return sum(p.latency_s for p in self.proposals)

    def to_dict(self) -> dict:
        passes = []
        for p in self.proposals:
            entry = p.to_dict()
            placement = self.placements.get(p.pass_no)
            if placement is not None:
                entry.update({"pieces_placed": len(placement.pieces), "pieces_dropped": len(placement.dropped),
                              "iterations": placement.iterations, "repair_steps": len(placement.log),
                              "anchor_first": placement.anchor_first})
            entry["rejected_types"] = list(p.rejected_types)
            passes.append(entry)
        out = {"room_id": self.room_id, "label": self.label, "room_type": self.room_type, "passes": passes,
               "chosen_pass": self.chosen_pass, "latency_s": round(self.latency_s, 3), "skipped": self.skipped,
               "pieces": [{"id": f["id"], "type": f["type"], "confidence": f["evidence"][0]["confidence"],
                           "checks": f["checks"]} for f in self.pieces]}
        if self.copied_from is not None:
            out["copied_from"] = self.copied_from
            out["copy_dropped"] = list(self.copy_dropped)
        return out


def style_text_of(style: Optional[dict], building: dict) -> str:
    """The style text the model is told: style.json ``source_text``, else the brief, else the default."""
    if style and style.get("source_text"):
        return str(style["source_text"])
    brief = (building.get("project") or {}).get("brief") or {}
    if brief.get("style"):
        return str(brief["style"])
    if brief.get("styles"):
        return str(brief["styles"][0])
    from wenart.style.profile import _defaults_or_builtin  # local import: PyYAML is optional there
    return str(_defaults_or_builtin()["style"]["text"])


def empty_rooms(building: dict) -> list[dict]:
    """Rooms without documented furniture whose type the layout handles, in building order."""
    return [r for r in building["rooms"]
            if not r.get("has_documented_furniture") and r.get("room_type") in schemas.FURNISHABLE_ROOM_TYPES]


def not_furnished_rooms(building: dict) -> list[dict]:
    """Empty rooms whose type is never furnished by AI (``schemas.NOT_FURNISHED_ROOM_TYPES``: prayer), in
    building order; the layout lists them as skipped instead of passing them over silently."""
    return [r for r in building["rooms"]
            if not r.get("has_documented_furniture") and r.get("room_type") in schemas.NOT_FURNISHED_ROOM_TYPES]


def _next_furniture_number(building: dict, level_id: str) -> int:
    pattern = re.compile(rf"^f_{re.escape(level_id)}_(\d+)$")
    numbers = [int(m.group(1)) for f in building["furniture"] for m in [pattern.match(f["id"])] if m]
    return max(numbers, default=0) + 1


def _agrees(piece: placer.Piece, other: Optional[dict]) -> bool:
    if not other:
        return False
    c = piece.proposed["center"]
    for item in other.get("pieces", []):
        if item["type"] == piece.type and G.distance(c, item["center"]) <= AGREE_DISTANCE_M:
            return True
    return False


def furniture_dict(piece: placer.Piece, checks: dict, room: dict, piece_id: str, model: str, pass_no: int,
                   confidence: float, agreed: bool) -> dict:
    rotation = round(piece.rotation_deg, 2)
    return {
        "id": piece_id, "level_id": room["level_id"], "room_id": room["id"], "type": piece.type, "type_raw": None,
        "source": "added_by_ai",
        "footprint": {"center": [round(piece.center[0], 3), round(piece.center[1], 3)],
                      "size": [piece.size[0], piece.size[1]], "rotation_deg": rotation},
        "front_deg": G.front_direction_deg(rotation), "height": schemas.HEIGHTS.get(piece.type), "asset": None,
        "status": "verified",
        "evidence": [B.evidence(EVIDENCE_FILE, "ai", confidence, model=model, pass_=pass_no,
                                text=piece.reason or f"{piece.type} proposed by the layout model")],
        "checks": dict(checks),
        "layout": {"against_wall": piece.against_wall, "proposed": dict(piece.proposed),
                   "repairs": [r["step"] for r in piece.repairs], "agreed_by_other_pass": agreed},
    }


def propose_layouts(room: dict, building: dict, style_text: str, client, passes: int = 2) -> RoomLayout:
    """Ask ``client`` ``passes`` times, place every answer, keep the best (see module docstring)."""
    result = RoomLayout(room["id"], room["label"], room.get("room_type", "other"))
    ctx = placer.room_context(building, room)
    result.context = ctx
    doors, windows = placer.room_openings(building, room)
    for pass_no in range(1, passes + 1):
        prompt = prompts.layout_prompt(room, doors, windows, style_text, pass_no)
        proposal = client.propose(prompt, pass_no)
        proposal.pass_no = pass_no
        result.proposals.append(proposal)
        if proposal.data is not None:
            # AI proposes, checks decide: a type the room type does not allow (a toilet in a
            # bedroom; Milestone 10: a crib outside a child's room) is removed before placement
            # and listed in the proposal record.
            allowed = (schemas.layout_types(result.room_type, room.get("room_subtype"))
                       if result.room_type in schemas.ALLOWED_TYPES else None)
            pieces = proposal.data["pieces"]
            if allowed is not None:
                proposal.rejected_types = [p["type"] for p in pieces if p["type"] not in allowed]
                pieces = [p for p in pieces if p["type"] in allowed]
            result.placements[pass_no] = placer.place(pieces, ctx)
    usable = [(len(result.placements[p].dropped), p) for p in sorted(result.placements)
              if result.placements[p].pieces]
    if not usable:
        reasons = [f"pass {p.pass_no}: {p.error}" if p.error else f"pass {p.pass_no}: no usable piece" for p in result.proposals]
        result.skipped = "model answered nothing usable (" + "; ".join(reasons) + ")"
        return result
    result.chosen_pass = min(usable)[1]
    chosen = result.placements[result.chosen_pass]
    others = [p.data for p in result.proposals if p.pass_no != result.chosen_pass and p.data is not None]
    model = next(p.model for p in result.proposals if p.pass_no == result.chosen_pass)
    number = _next_furniture_number(building, room["level_id"])
    for piece, checks in zip(chosen.pieces, chosen.checks):
        agreed = any(_agrees(piece, other) for other in others)
        confidence = CONFIDENCE_AGREED if agreed else CONFIDENCE_SINGLE
        result.pieces.append(furniture_dict(piece, checks, room, B.element_id("furniture", room["level_id"], number),
                                            model, result.chosen_pass, confidence, agreed))
        number += 1
    return result


# --------------------------------------------------------------------------
# Whole building
# --------------------------------------------------------------------------

def furnish_building(building: dict, style_text: str, client, passes: int = 2,
                     debug_dir: Optional[Path] = None,
                     partners: Optional[dict] = None) -> tuple[dict, list[RoomLayout]]:
    """Add AI furniture to every empty room (new dict; the input is not changed).

    ``partners`` (Milestone 10): room id -> ``(partner room id, "same_as" | "twin")``; an empty room whose
    partner is an empty room too takes the partner's layout (``complete.copy_empty_layout``) instead of
    being asked; a partner that does not map is reported and the room is asked itself."""
    out = json.loads(json.dumps(building))
    layouts: list[RoomLayout] = []
    brief = (out.get("project") or {}).get("brief") or {}
    mode = brief.get("empty_rooms", "ai")
    for room in not_furnished_rooms(out):
        layouts.append(RoomLayout(room["id"], room["label"], room.get("room_type", "other"),
                                  skipped=f"{room.get('room_type')} room: never furnished by AI "
                                          f"(docs/milestone7.md §0)"))
    empties = empty_rooms(out)
    ids = {r["id"] for r in empties}
    copies = {rid: p for rid, p in (partners or {}).items() if rid in ids and p[0] in ids and rid != p[0]}
    done: dict[str, RoomLayout] = {}
    for room in empties:
        if mode != "ai":
            done[room["id"]] = RoomLayout(room["id"], room["label"], room.get("room_type", "other"),
                                          skipped=f"brief.empty_rooms is {mode!r}")
            continue
        if room["id"] in copies:
            continue
        done[room["id"]] = layout = propose_layouts(room, out, style_text, client, passes)
        out["furniture"].extend(layout.pieces)
    pending = [r for r in empties if r["id"] in copies and r["id"] not in done]
    while pending:
        ready = [r for r in pending if copies[r["id"]][0] in done]
        room = ready[0] if ready else pending[0]               # no partner ready: a cycle, ask the first
        pending.remove(room)
        if ready:
            done[room["id"]] = _copy_layout(room, copies[room["id"]], done, out, style_text, client, passes)
        else:
            done[room["id"]] = layout = propose_layouts(room, out, style_text, client, passes)
            out["furniture"].extend(layout.pieces)
    for room in empties:
        layout = done[room["id"]]
        layouts.append(layout)
        if debug_dir is not None and mode == "ai":
            write_room_debug(room, layout, Path(debug_dir))
    out["warnings"] = list(out.get("warnings", []))
    for layout in layouts:
        if layout.skipped:
            out["warnings"].append(f"{layout.room_id}: no AI furniture, {layout.skipped}")
    return out, layouts


def _copy_layout(room: dict, partner: tuple[str, str], done: dict, out: dict, style_text: str, client,
                 passes: int) -> RoomLayout:
    """The partner's layout mapped into ``room`` (Milestone 10), else the room is asked itself."""
    from wenart.furniture import complete as C   # lazy: complete imports this module

    pid, kind = partner
    source = done[pid]
    rooms = {r["id"]: r for r in out["rooms"]}
    record = RoomLayout(room["id"], room["label"], room.get("room_type", "other"),
                        context=placer.room_context(out, room))
    if not source.pieces:
        record.skipped = f"partner {pid} ({kind}) got no AI furniture: {source.skipped or 'nothing placed'}"
        record.copied_from = {"room": pid, "kind": kind}
        return record
    added, dropped, info = C.copy_empty_layout(room, rooms[pid], kind, source.pieces, out, out)
    if added is None:
        layout = propose_layouts(room, out, style_text, client, passes)
        out["furniture"].extend(layout.pieces)
        layout.copied_from = dict(info, used=False)
        return layout
    record.pieces, record.copy_dropped, record.copied_from = added, dropped, info
    if not added:
        record.skipped = f"every piece copied from {pid} fails a check here"
    return record


def layout_summary(layouts: list[RoomLayout], building: dict, server: str, model: str) -> dict:
    return {"project": building["project"]["id"], "server": server, "model": model,
            "rooms": [l.to_dict() for l in layouts],
            "pieces_added": sum(len(l.pieces) for l in layouts),
            "latency_s": round(sum(l.latency_s for l in layouts), 3)}


def layout_report(layouts: list[RoomLayout], building: dict) -> str:
    lines = [f"# AI layout: {building['project']['id']}", "",
             "Rooms without documented furniture. Every added piece is `added_by_ai`, `verified` by the placer "
             "checks (inside room, no overlap, clearance, doors free, windows free, wall contact), "
             f"confidence {CONFIDENCE_AGREED} when both passes proposed it (same type, centre within "
             f"{AGREE_DISTANCE_M} m), else {CONFIDENCE_SINGLE}.", "",
             "| Room | Type | Pass 1 (proposed/placed/dropped, s) | Pass 2 | Chosen | Added | Result |",
             "|---|---|---|---|---|---|---|"]
    for l in layouts:
        cells = []
        for pass_no in (1, 2):
            prop = next((p for p in l.proposals if p.pass_no == pass_no), None)
            if prop is None:
                cells.append("-")
            elif prop.data is None:
                cells.append(f"error: {prop.error}"[:60] + f" ({prop.latency_s:.1f} s)")
            else:
                pl = l.placements.get(pass_no)
                cells.append(f"{len(prop.data['pieces'])}/{len(pl.pieces)}/{len(pl.dropped)} ({prop.latency_s:.1f} s)")
        added = ", ".join(f"{f['type']} ({f['evidence'][0]['confidence']})" for f in l.pieces) or "-"
        result = l.skipped and f"room stays empty: {l.skipped}" or "ok"
        if l.copied_from and l.copied_from.get("used", True) and not l.skipped:
            result = f"copied from {l.copied_from['room']} ({l.copied_from['kind']})" + (
                f", {len(l.copy_dropped)} copies dropped" if l.copy_dropped else "")
        lines.append(f"| {l.label} ({l.room_id}) | {l.room_type} | {cells[0]} | {cells[1]} | "
                     f"{l.chosen_pass or '-'} | {added} | {result} |")
    repairs = [(l, entry) for l in layouts if l.chosen_pass for entry in l.placements[l.chosen_pass].log]
    lines += ["", f"Repair steps of the chosen proposals: {len(repairs)}", ""]
    if repairs:
        lines += ["| Room | Step | Piece | Before | After | Failed checks |", "|---|---|---|---|---|---|"]
        for l, e in repairs:
            lines.append(f"| {l.room_id} | {e['step']} | {e['type']} #{e['piece']} | {e['before']['center']} | "
                         f"{e['after']['center']} | {', '.join(e['failed']) or '-'} |")
    dropped = [(l, d) for l in layouts if l.chosen_pass for d in l.placements[l.chosen_pass].dropped]
    if dropped:
        lines += ["", "Dropped pieces (chosen proposals):", ""]
        for l, d in dropped:
            lines.append(f"- {l.room_id}: {d['type']} at {d['proposed']['center']}: {d['reason']} ({', '.join(d['failed'])})")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# Debug output (PNG + JSON per room)
# --------------------------------------------------------------------------

def write_room_debug(room: dict, layout: RoomLayout, debug_dir: Path) -> None:
    debug_dir.mkdir(parents=True, exist_ok=True)
    record = {"room": room["id"], "passes": [], "chosen_pass": layout.chosen_pass, "skipped": layout.skipped}
    for p in layout.proposals:
        entry = p.to_dict()
        entry.update({"prompt": p.prompt, "raw_text": p.raw_text, "data": p.data})
        placement = layout.placements.get(p.pass_no)
        if placement is not None:
            entry["placement"] = placement.to_dict()
        record["passes"].append(entry)
    (debug_dir / f"{room['id']}.json").write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
    try:
        draw_room_png(room, layout, debug_dir / f"{room['id']}.png")
    except ImportError as exc:   # matplotlib missing: the JSON is the record, the PNG is a convenience
        print(f"layout: debug PNG for {room['id']} skipped ({exc})", file=sys.stderr)


def draw_room_png(room: dict, layout: RoomLayout, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MplPolygon

    ctx = layout.context or placer.room_context({"walls": [], "openings": []}, room)
    passes = sorted(layout.placements) or [None]
    fig, axes = plt.subplots(1, len(passes), figsize=(6 * len(passes), 6), squeeze=False)
    for ax, pass_no in zip(axes[0], passes):
        ax.set_aspect("equal")
        ax.add_patch(MplPolygon(list(ctx.polygon.exterior.coords), closed=True, fill=False, lw=2, color="black"))
        for door in ctx.doors:
            ax.add_patch(MplPolygon(list(door.zone.exterior.coords), closed=True, color="tab:orange", alpha=0.25))
            if door.swing is not None and not door.swing.is_empty:
                ax.add_patch(MplPolygon(list(door.swing.exterior.coords), closed=True, color="tab:orange", alpha=0.15))
            ax.plot(*door.approach_point, "o", color="tab:orange", ms=4)
        for win in ctx.windows:
            ax.add_patch(MplPolygon(list(win.band.exterior.coords), closed=True, color="tab:blue", alpha=0.25))
        if pass_no is None:
            ax.set_title(f"{room['label']} ({room['id']}): no proposal")
            continue
        placement = layout.placements[pass_no]
        for piece in placement.pieces:
            prop = placer.Piece(piece.type, tuple(piece.proposed["center"]), piece.proposed["rotation_deg"],
                                tuple(piece.proposed["size"]), piece.against_wall)
            ax.add_patch(MplPolygon(list(prop.polygon().exterior.coords), closed=True, fill=False, ls="--",
                                    color="grey", lw=1))
            ax.add_patch(MplPolygon(list(piece.polygon().exterior.coords), closed=True, color="tab:green", alpha=0.5))
            fz = piece.front_zone(0.15)
            ax.add_patch(MplPolygon(list(fz.exterior.coords), closed=True, color="tab:green", alpha=0.9))
            if piece.repairs:
                ax.annotate("", xy=piece.center, xytext=tuple(piece.proposed["center"]),
                            arrowprops={"arrowstyle": "->", "color": "tab:red"})
            ax.text(piece.center[0], piece.center[1], piece.type, ha="center", va="center", fontsize=7)
        for d in placement.dropped:
            prop = placer.Piece(d["type"], tuple(d["proposed"]["center"]), d["proposed"]["rotation_deg"],
                                tuple(d["proposed"]["size"]), False)
            ax.add_patch(MplPolygon(list(prop.polygon().exterior.coords), closed=True, fill=False, ls=":", color="tab:red"))
            ax.text(d["proposed"]["center"][0], d["proposed"]["center"][1], f"x {d['type']}", color="tab:red",
                    ha="center", va="center", fontsize=7)
        chosen = " (chosen)" if pass_no == layout.chosen_pass else ""
        ax.set_title(f"{room['label']} pass {pass_no}{chosen}: {len(placement.pieces)} placed, "
                     f"{len(placement.dropped)} dropped, {placement.iterations} steps", fontsize=9)
        minx, miny, maxx, maxy = ctx.polygon.bounds
        ax.set_xlim(minx - 0.5, maxx + 0.5)
        ax.set_ylim(miny - 0.5, maxy + 0.5)
    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv: Optional[list[str]] = None, client_factory=None) -> int:
    parser = argparse.ArgumentParser(description="AI furniture layout for rooms without documented furniture")
    parser.add_argument("building", help="building.json (or building_fitted.json)")
    parser.add_argument("--style", help="style.json from python -m wenart.style")
    parser.add_argument("--server", default=DEFAULT_SERVER, help=f"vLLM server base URL (default {DEFAULT_SERVER})")
    parser.add_argument("--model", default=None, help=f"model id (default: first served, e.g. {DEFAULT_MODEL})")
    parser.add_argument("--out", required=True, help="furnished building JSON")
    parser.add_argument("--debug", help="folder for one PNG + JSON per room")
    parser.add_argument("--passes", type=int, default=2)
    parser.add_argument("--timeout", type=float, default=600.0, help="seconds per model call")
    parser.add_argument("--project-dir", help="project folder with brief.yaml (default: the building's "
                                              "project.source_folder)")
    args = parser.parse_args(argv)

    from wenart.furniture import complete as C   # lazy: complete imports this module
    from wenart.furniture import locked as LK

    building = B.load(args.building)
    style = json.loads(Path(args.style).read_text(encoding="utf-8")) if args.style else None
    style_text = style_text_of(style, building)
    factory = client_factory or (lambda: LayoutClient(args.server, args.model, timeout_s=args.timeout))
    client = factory()
    if building.get("status") != "ok":
        print(f"layout: building status {building.get('status')!r}, nothing furnished", file=sys.stderr)
        return 2
    project_dir = args.project_dir or (building.get("project") or {}).get("source_folder") or "."
    settings = C.load_settings(project_dir)
    for warning in settings.warnings:
        print(f"layout: brief: {warning}", file=sys.stderr)
    partners = {r["id"]: p for r in building["rooms"] for p in [C.partner_of(r, settings)] if p}
    rooms = empty_rooms(building)
    print(f"layout: {len(rooms)} empty room(s), {len(C.furnished_rooms(building))} furnished room(s) "
          f"(furnished_rooms: {settings.mode}) in {building['project']['id']}, style '{style_text}'")
    debug = Path(args.debug) if args.debug else None
    furnished, layouts = furnish_building(building, style_text, client, args.passes, debug, partners=partners)
    profile = style[0] if isinstance(style, list) and style else style
    family = profile.get("family") if isinstance(profile, dict) else None
    completed, records = C.complete_building(furnished, style_text, client, settings, args.passes, debug, family)
    failed = [(l.room_id, p.pass_no, p.error) for l in layouts for p in l.proposals if p.transport_error]
    failed += [(r.room_id, k, e) for r in records for k, e in r.transport_errors]
    if failed:
        # The server was not reachable: no answer is not "nothing to add" (the job must not reuse an
        # empty layout), so no furnished building is written and the exit code says why.
        for room_id, pass_no, error in failed:
            print(f"layout: {room_id} pass {pass_no}: server not reachable ({error})", file=sys.stderr)
        print(f"layout: {len(failed)} call(s) could not reach {args.server}: no output written (exit 3)",
              file=sys.stderr)
        return 3
    keep_rooms = [r.room_id for r in records if r.state == "kept"]
    violations = LK.check(building, completed, "keep" if settings.mode == "keep" else "complete", keep_rooms)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    # The model as the proposals recorded it (asking the client could raise when the server is down).
    model = next((p.model for l in layouts for p in l.proposals if p.model and p.model != "?"), None)
    model = model or next((p["model"] for r in records for p in r.passes if p.get("model") not in (None, "?")),
                          args.model or "?")
    completion = C.summary(records, completed, settings, args.server, str(model), violations)
    (out.parent / "completion.json").write_text(json.dumps(completion, ensure_ascii=False, indent=1), encoding="utf-8")
    (out.parent / "completion_report.md").write_text(C.report(records, completed, settings, violations),
                                                     encoding="utf-8")
    if violations:
        for v in violations:
            print(f"layout: locked check: {v}", file=sys.stderr)
        print(f"layout: {len(violations)} locked violation(s): no furnished building written (exit 1)",
              file=sys.stderr)
        return 1
    B.save(completed, out)
    summary = layout_summary(layouts, completed, args.server, str(model))
    summary["completion"] = {k: completion[k] for k in ("rooms_completed", "rooms_copied", "changes_applied",
                                                         "pieces_added", "wall_cabinets", "latency_s")}
    (out.parent / "layout.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    (out.parent / "layout_report.md").write_text(layout_report(layouts, completed), encoding="utf-8")
    for l in layouts:
        state = f"{len(l.pieces)} added, pass {l.chosen_pass}" if l.chosen_pass else f"empty ({l.skipped})"
        if l.copied_from and l.copied_from.get("used", True) and l.pieces:
            state = f"{len(l.pieces)} copied from {l.copied_from['room']}"
        print(f"layout: {l.room_id} [{l.room_type}] {state}, {l.latency_s:.1f} s")
    for r in records:
        changed = sum(c["status"] == "applied" for c in r.changes)
        print(f"layout: {r.room_id} [{r.room.get('room_type')}] {r.state}: {changed} changed, {len(r.added)} added, "
              f"{len(r.wall_cabinets)} wall cabinet(s), {r.latency_s:.1f} s" + (f" ({r.reason})" if r.reason else ""))
    print(f"layout: {summary['pieces_added']} pieces added to empty rooms, {completion['pieces_added']} added and "
          f"{completion['changes_applied']} changed in furnished rooms, locked check passed -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
