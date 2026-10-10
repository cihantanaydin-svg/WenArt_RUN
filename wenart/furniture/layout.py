"""The layout stage: rooms the documents leave empty are furnished in functional groups, rooms with drawn furniture
are completed (docs/milestone12.md §4.3-§4.5; Milestone 4 §3 and Milestone 10 §2 before; owner: track G).

What, per empty room (``has_documented_furniture: false``, a furnishable room type): the room's program
(``program.room_program``: groups with options) -> the group solver's top 3 candidates (``solver.solve_room``) ->
the vision model picks one (``choose_candidate``: a multimodal request with one top-down image per candidate, its
groups, options, scores and score terms; temperature 0, strict JSON ``{candidate, reason}``; it chooses only among
the candidates, never coordinates) -> the chosen candidate's pieces are added (``apply_choice``: ``added_by_ai``,
``method: rule``, ``group`` membership, evidence of the solver and of the choice). A failed, unreachable or invalid
answer takes candidate 1 (the solver's best), logged. A candidate with hard failures is never applied; a room with
no usable candidate stays empty and the report says why. Prayer rooms, stairs and shafts are never furnished. The
completion of rooms with drawn furniture (``complete.complete_building``) uses the same chooser.

Why: Milestone 11 asked a text-only model for single pieces with raw coordinates and repaired them one by one
(§1.2); now code places whole groups and the model only chooses.

Partners (Milestone 10, kept): an empty room whose ``same_as`` / twin partner is empty too takes the partner's
layout (``complete.copy_empty_layout``: copied, mirrored for twins) instead of being solved and asked. A partner
that does not map, or a copy that would lose a piece here (a check fails), is not used: the room is solved itself.

The request goes through ``wenart.recognition.vlm_client`` (``build_request`` with several labelled images,
``post_json``, ``parse_answer``, ``served_models``). ``LayoutClient.down`` is set by the first transport error:
later rooms are not asked again (candidate 1, logged), so a dead server costs one retry series, not one per room.

CLI (unchanged arguments; ``--passes`` is accepted and ignored): ``python -m wenart.furniture.layout
outputs/<p>/building_fitted.json --style outputs/<p>/style.json --server http://127.0.0.1:8001/v1 --model <id>
--out outputs/<p>/building_furnished.json --debug outputs/<p>/layout_debug/ --project-dir <project>`` writes the
furnished building, ``layout.json``, ``layout_report.md``, ``completion.json`` and ``completion_report.md`` next to
it and per room ``<room>.json`` (program, candidates with their scores, terms and checks, the choice), ``<room>.png``
(the candidates side by side) and ``<room>_c<k>.png`` (the images the model saw) in the debug folder. It runs
``locked.check(source, final, mode)``: a violation writes no furnished building and exits 1; a building with
``status`` other than ``ok`` exits 2. ``--no-orchestrator`` runs of ``wenart.run`` call it the same way.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from wenart import building as B
from wenart.furniture import placer, prompts, schemas
from wenart.recognition import vlm_client

DEFAULT_SERVER = "http://127.0.0.1:8001/v1"
DEFAULT_MODEL = "Qwen/Qwen3-VL-8B-Instruct"
DEFAULT_MAX_TOKENS = 2048
CANDIDATES = 3
CHOICE_CONFIDENCE = 0.8
EVIDENCE_FILE = "building.json"   # what the solver and the model saw: the room, doors, windows and drawn pieces
IMAGE_MAX_SIDE = 900


# --------------------------------------------------------------------------
# Client
# --------------------------------------------------------------------------

@dataclass
class Proposal:
    """One model call for one room (a candidate choice; ``propose``: the Milestone 4 text question)."""
    pass_no: int
    data: Optional[dict]            # schema-valid answer or None
    raw_text: str = ""
    latency_s: float = 0.0
    error: Optional[str] = None
    prompt: str = ""
    model: str = ""
    rejected_types: list = field(default_factory=list)
    transport_error: bool = False   # the last attempt raised VLMError (or the model lookup failed)

    def to_dict(self) -> dict:
        return {"pass": self.pass_no, "model": self.model, "latency_s": round(self.latency_s, 3),
                "error": self.error, "transport_error": self.transport_error}


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
    """Asks the vLLM server. ``choose(prompt, images, labels, schema)`` -> Proposal (Milestone 12);
    ``propose(prompt, pass_no)`` -> Proposal (the Milestone 4 text question, kept for the fake-server tests)."""

    def __init__(self, base_url: str = DEFAULT_SERVER, model: Optional[str] = None, *,
                 timeout_s: float = 600.0, retries: int = 3, max_tokens: int = DEFAULT_MAX_TOKENS) -> None:
        self.base_url = base_url.rstrip("/")
        self._model = model
        self.timeout_s = timeout_s
        self.retries = max(1, retries)
        self.max_tokens = max_tokens
        self.down: Optional[str] = None             # the first transport error: later rooms are not asked

    @property
    def model(self) -> str:
        if self._model is None:
            models = vlm_client.served_models(self.base_url)
            if not models:
                raise vlm_client.VLMError(f"no model served at {self.base_url}")
            self._model = models[0]
        return self._model

    def propose(self, prompt: str, pass_no: int) -> Proposal:
        """An empty room's layout (the Milestone 4 schema; not used by the stage any more)."""
        def body(model):
            return build_text_request(model, prompt, schemas.grammar_schema(), seed=pass_no,
                                      max_tokens=self.max_tokens, system_prompt=prompts.SYSTEM_PROMPT)
        return self._ask(body, prompt, pass_no, schemas.validation_errors)

    def choose(self, prompt: str, images: list, labels: list, schema: dict) -> Proposal:
        """The candidate choice: the top-down images (labelled), the prompt, the strict ``schema``."""
        import jsonschema

        if self.down:
            return Proposal(1, None, error=f"not asked: the server failed before ({self.down})", prompt=prompt,
                            model=self._model or "?", transport_error=True)
        urls = [vlm_client.encode_image(p, IMAGE_MAX_SIDE)[0] for p in images]

        def body(model):
            return vlm_client.build_request(model, prompt, None, schema, max_tokens=self.max_tokens, seed=0,
                                            temperature=0.0, system_prompt=prompts.CHOICE_SYSTEM_PROMPT,
                                            images=urls, labels=labels)

        def errors(data) -> list[str]:
            return [e.message for e in jsonschema.Draft202012Validator(schema).iter_errors(data)]

        out = self._ask(body, prompt, 1, errors)
        if out.transport_error:
            self.down = out.error or "transport error"
        return out

    def _ask(self, make_body, prompt: str, pass_no: int, validation_errors) -> Proposal:
        try:
            model = self.model
        except vlm_client.VLMError as exc:
            return Proposal(pass_no, None, error=str(exc), prompt=prompt, model="?", transport_error=True)
        body = make_body(model)
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
# Rooms
# --------------------------------------------------------------------------

@dataclass
class RoomLayout:
    room_id: str
    label: str
    room_type: str
    program: Optional[dict] = None
    candidates: list = field(default_factory=list)       # solver candidates (dicts)
    choice: Optional[dict] = None                        # choose_candidate's record
    chosen: Optional[int] = None                         # rank of the applied candidate
    pieces: list = field(default_factory=list)           # building furniture dicts
    skipped: Optional[str] = None                        # why the room got nothing
    context: Optional[placer.RoomContext] = None
    copied_from: Optional[dict] = None                   # Milestone 10: the partner whose layout this room took
    copy_dropped: list = field(default_factory=list)
    solve_s: float = 0.0

    @property
    def latency_s(self) -> float:
        return float((self.choice or {}).get("latency_s") or 0.0)

    def to_dict(self) -> dict:
        out = {"room_id": self.room_id, "label": self.label, "room_type": self.room_type,
               "program": [{k: g.get(k) for k in ("group_id", "group", "options", "drawn", "required")}
                           for g in (self.program or {}).get("groups", [])],
               "candidates": [candidate_summary(c) for c in self.candidates], "chosen": self.chosen,
               "choice": {k: v for k, v in (self.choice or {}).items() if k not in ("prompt", "raw_text", "images")},
               "latency_s": round(self.latency_s, 3), "solve_s": round(self.solve_s, 3), "skipped": self.skipped,
               "pieces": [{"id": f["id"], "type": f["type"], "group": (f.get("group") or {}).get("group")}
                          for f in self.pieces]}
        if self.copied_from is not None:
            out["copied_from"] = self.copied_from
            out["copy_dropped"] = list(self.copy_dropped)
        return out


def candidate_summary(c: dict) -> dict:
    return {"rank": c["rank"], "score": c["score"], "terms": c.get("terms", {}), "options": c.get("options", {}),
            "pieces": [p["type"] for p in c.get("pieces", [])], "not_placed": c.get("not_placed", []),
            "hard_failures": c.get("hard_failures", []),
            "group_violations": [f"{v['check']} {v['severity']} {v['target']}: {v['message']}"
                                 for v in c.get("group_violations", [])], "nodes": c.get("nodes")}


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


# --------------------------------------------------------------------------
# Images of the candidates
# --------------------------------------------------------------------------

GROUP_COLOURS = {"seating": "#4e79a7", "dining": "#f28e2b", "sleeping_double": "#59a14f", "sleeping_single": "#59a14f",
                 "storage": "#b07aa1", "work": "#76b7b2", "living_storage": "#9c755f", "kitchen_run": "#e15759",
                 "island": "#ff9da7", "bathroom_set": "#4e79a7", "wc_set": "#4e79a7", "entrance": "#9c755f",
                 "balcony": "#f28e2b"}


def _draw_room(ax, building: dict, room: dict, cand: Optional[dict], title: str) -> None:
    from matplotlib.patches import Polygon as MplPolygon

    ctx = placer.room_context(building, room)
    ax.set_aspect("equal")
    ax.add_patch(MplPolygon(list(ctx.polygon.exterior.coords), closed=True, fill=False, lw=2, color="black"))
    for door in ctx.doors:
        for part in placer.polygon_parts(door.zone) + placer.polygon_parts(door.swing):
            ax.add_patch(MplPolygon(list(part.exterior.coords), closed=True, color="tab:orange", alpha=0.2))
    for win in ctx.windows:
        for part in placer.polygon_parts(win.band):
            ax.add_patch(MplPolygon(list(part.exterior.coords), closed=True, color="tab:cyan", alpha=0.45))
    items = [(f, "#9a9a9a") for f in building.get("furniture") or [] if f.get("room_id") == room["id"]
             and f.get("source") == "from_documents" and f.get("build") is not False]
    items += [(f, GROUP_COLOURS.get((f.get("group") or {}).get("group"), "#4e79a7")) for f in (cand or {}).get("pieces", [])]
    for f, colour in items:
        try:
            p = placer.drawn_piece(f)
        except (KeyError, TypeError, ValueError):
            continue
        poly = p.polygon()
        ax.add_patch(MplPolygon(list(poly.exterior.coords), closed=True, color=colour, alpha=0.55))
        if f.get("front_deg") is not None:
            fz = p.front_zone(0.08)
            ax.add_patch(MplPolygon(list(fz.exterior.coords), closed=True, color="tab:red", alpha=0.9))
        ax.text(poly.centroid.x, poly.centroid.y, f["type"].replace("_", "\n"), ha="center", va="center", fontsize=6)
    minx, miny, maxx, maxy = ctx.polygon.bounds
    ax.set_xlim(minx - 0.3, maxx + 0.3)
    ax.set_ylim(miny - 0.3, maxy + 0.3)
    ax.set_title(title, fontsize=8)


def candidate_png(building: dict, room: dict, cand: dict, path: Path) -> Path:
    """One candidate as a top-down image (what the vision model sees)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    _draw_room(ax, building, room, cand, f"Candidate {cand['rank']}")
    fig.tight_layout()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return path


def draw_candidates_png(building: dict, room: dict, cands: list, path: Path, chosen: Optional[int] = None) -> None:
    """The candidates side by side (debug), the chosen one marked."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = max(1, len(cands))
    fig, axes = plt.subplots(1, n, figsize=(5.5 * n, 5.5), squeeze=False)
    for ax, c in zip(axes[0], cands or [None]):
        if c is None:
            _draw_room(ax, building, room, None, f"{room.get('label')} ({room['id']}): no candidate")
            continue
        mark = " (chosen)" if c["rank"] == chosen else ""
        _draw_room(ax, building, room, c, f"#{c['rank']}{mark} score {c['score']:.1f}, hard {len(c['hard_failures'])}"
                                          f"\n{', '.join(f'{k}: {v}' for k, v in c.get('options', {}).items())}")
    fig.tight_layout()
    fig.savefig(path, dpi=80)
    plt.close(fig)


# --------------------------------------------------------------------------
# The choice
# --------------------------------------------------------------------------

def choose_candidate(client, room: dict, building: dict, cands: list[dict], style_text: str,
                     image_dir: Optional[Path] = None, purpose: str = "furnish") -> dict:
    """``{"index", "rank", "by": "vlm" | "default", "reason", "model", "error", "transport_error", "latency_s",
    "prompt", "raw_text", "images"}``: which of ``cands`` (usable, best first) to apply. One candidate, a client
    without ``choose`` or a failed / invalid answer: the first (the solver's best)."""
    out = {"index": 0, "rank": cands[0]["rank"], "by": "default", "reason": "the solver's best candidate",
           "model": None, "error": None, "transport_error": False, "latency_s": 0.0}
    if len(cands) < 2:
        out["reason"] = "the only candidate"
        return out
    if not hasattr(client, "choose"):
        out["reason"] = "no vision model: the solver's best candidate"
        return out
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(image_dir) if image_dir is not None else Path(tmp)
        try:
            images = [candidate_png(building, room, c, folder / f"{room['id']}_c{c['rank']}.png") for c in cands]
        except Exception as exc:  # noqa: BLE001 - no image, no question: the solver's best
            out.update(error=f"images not drawn ({type(exc).__name__}: {exc})")
            return out
        prompt = prompts.choice_prompt(room, cands, style_text, purpose)
        schema = prompts.choice_schema(len(cands))
        labels = [f"Candidate {c['rank']}:" for c in cands]
        answer = client.choose(prompt, images, labels, schema)
        out.update(model=answer.model, error=answer.error, transport_error=bool(answer.transport_error),
                   latency_s=round(answer.latency_s, 3), prompt=prompt, raw_text=answer.raw_text,
                   images=[str(p.name) for p in images])
    data = answer.data
    pick = data.get("candidate") if isinstance(data, dict) else None
    ranks = [c["rank"] for c in cands]
    if pick in ranks:
        out.update(index=ranks.index(pick), rank=pick, by="vlm", reason=str(data.get("reason") or ""))
    else:
        out["reason"] = f"no valid answer ({answer.error or 'candidate ' + repr(pick)}): the solver's best candidate"
    return out


def apply_choice(out: dict, room: dict, cand: dict, choice: dict, completes: bool = False) -> list[dict]:
    """Add the chosen candidate's pieces to ``out`` (changed in place; ``solver.apply_candidate`` gives fresh ids)
    with the evidence of the choice; returns the added pieces."""
    from wenart.furniture import solver as SV

    before = {f["id"] for f in out["furniture"]}
    new = SV.apply_candidate(out, room["id"], cand)
    added = [f for f in new["furniture"] if f["id"] not in before]
    if choice.get("by") == "vlm":
        ev = {"file": EVIDENCE_FILE, "method": "ai", "confidence": CHOICE_CONFIDENCE, "model": choice.get("model"),
              "text": f"candidate {choice['rank']} of {len(choice.get('images') or [])} chosen by the vision model: "
                      f"{choice.get('reason')}"}
    else:
        ev = {"file": EVIDENCE_FILE, "method": "derived", "confidence": 0.9,
              "text": f"candidate {choice['rank']}: {choice.get('reason')}"}
    for f in added:
        f["evidence"] = list(f.get("evidence") or []) + [ev]
        f["checks"] = {name: True for name in placer.CHECKS}
        f["layout"] = dict(f.get("layout") or {}, candidate=cand["rank"], score=cand["score"])
        if completes:
            f["completes_room"] = True
    # The pieces already in ``out`` stay the same objects (the records of earlier rooms hold them).
    kept = {f["id"] for f in new["furniture"]}
    out["furniture"] = [f for f in out["furniture"] if f["id"] in kept] + added
    if "decor" in new:
        hosts = {d.get("host_id") for d in new["decor"]}
        out["decor"] = [d for d in out.get("decor") or [] if d.get("host_id") in hosts or d.get("host_id") is None]
    return added


def layout_room(room: dict, building: dict, style_text: str, client, image_dir: Optional[Path] = None,
                purpose: str = "furnish") -> RoomLayout:
    """Program -> solver -> choice -> pieces for one room; ``building`` (the building being written) is changed in
    place."""
    from wenart.furniture import program as PR
    from wenart.furniture import solver as SV

    rec = RoomLayout(room["id"], room.get("label", room["id"]), room.get("room_type", "other"))
    rec.context = placer.room_context(building, room)
    rec.program = PR.room_program(building, room["id"])
    if not rec.program["groups"]:
        rec.skipped = f"no groups for this room ({rec.program['reason']})"
        return rec
    t0 = time.perf_counter()
    rec.candidates = SV.solve_room(building, room["id"], rec.program, k=CANDIDATES)
    rec.solve_s = time.perf_counter() - t0
    usable = [c for c in rec.candidates if not c["hard_failures"] and c["pieces"]]
    if not usable:
        best = rec.candidates[0] if rec.candidates else None
        if best is None:
            rec.skipped = ("nothing missing: the drawn groups are complete" if purpose == "complete"
                           else "no group fits the room")
        elif not best["hard_failures"]:
            rec.skipped = "nothing fits: " + "; ".join(f"{x['group']}: {x['reason']}" for x in best["not_placed"]) \
                if best["not_placed"] else "nothing missing: the drawn groups are complete"
        else:
            why = "; ".join(f"#{c['rank']}: " + ", ".join(c["hard_failures"][:2]) for c in rec.candidates)
            rec.skipped = f"no candidate passes the checks ({why})"
        return rec
    rec.choice = choose_candidate(client, room, building, usable, style_text, image_dir, purpose)
    cand = usable[rec.choice["index"]]
    rec.chosen = cand["rank"]
    rec.pieces = apply_choice(building, room, cand, rec.choice, completes=(purpose == "complete"))
    return rec


# --------------------------------------------------------------------------
# Whole building
# --------------------------------------------------------------------------

def furnish_building(building: dict, style_text: str, client, passes: Optional[int] = None,
                     debug_dir: Optional[Path] = None,
                     partners: Optional[dict] = None) -> tuple[dict, list[RoomLayout]]:
    """Furnish every empty room (new dict; the input is not changed). ``passes`` is accepted for the Milestone 10
    callers and not used.

    ``partners`` (Milestone 10): room id -> ``(partner room id, "same_as" | "twin")``; an empty room whose
    partner is an empty room too takes the partner's layout (``complete.copy_empty_layout``) instead of being
    solved; a partner that does not map is reported and the room is solved itself."""
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
    image_dir = Path(debug_dir) if debug_dir is not None else None
    for room in empties:
        if mode != "ai":
            done[room["id"]] = RoomLayout(room["id"], room["label"], room.get("room_type", "other"),
                                          skipped=f"brief.empty_rooms is {mode!r}")
            continue
        if room["id"] in copies:
            continue
        done[room["id"]] = layout_room(room, out, style_text, client, image_dir)
    pending = [r for r in empties if r["id"] in copies and r["id"] not in done]
    while pending:
        ready = [r for r in pending if copies[r["id"]][0] in done]
        room = ready[0] if ready else pending[0]               # no partner ready: a cycle, solve the first
        pending.remove(room)
        if ready:
            done[room["id"]] = _copy_layout(room, copies[room["id"]], done, out, style_text, client, image_dir)
        else:
            done[room["id"]] = layout_room(room, out, style_text, client, image_dir)
    for room in empties:
        layout = done[room["id"]]
        layouts.append(layout)
        if debug_dir is not None and mode == "ai":
            write_room_debug(room, layout, out, Path(debug_dir))
    out["warnings"] = list(out.get("warnings", []))
    for layout in layouts:
        if layout.skipped:
            out["warnings"].append(f"{layout.room_id}: no AI furniture, {layout.skipped}")
    return out, layouts


def _copy_layout(room: dict, partner: tuple[str, str], done: dict, out: dict, style_text: str, client,
                 image_dir: Optional[Path]) -> RoomLayout:
    """The partner's layout mapped into ``room`` (Milestone 10), else the room is solved itself."""
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
    count = len(out["furniture"])
    added, dropped, info = C.copy_empty_layout(room, rooms[pid], kind, source.pieces, out, out)
    if added is None or dropped:
        # A partner that does not map, or a copy that would lose pieces (a table without its chairs): the room is
        # solved itself; a whole group matters more than the same look in both rooms.
        del out["furniture"][count:]
        layout = layout_room(room, out, style_text, client, image_dir)
        why = info.get("reason") or f"{len(dropped)} of {len(source.pieces)} copied pieces fail a check here (" + \
            "; ".join(f"{x['type']}: {x['reason']}" for x in dropped) + ")"
        layout.copied_from = dict(info, used=False, reason=why)
        layout.copy_dropped = list(dropped)
        return layout
    record.pieces, record.copy_dropped, record.copied_from = added, dropped, info
    return record


def layout_summary(layouts: list[RoomLayout], building: dict, server: str, model: str) -> dict:
    return {"project": building["project"]["id"], "server": server, "model": model,
            "rooms": [l.to_dict() for l in layouts],
            "pieces_added": sum(len(l.pieces) for l in layouts),
            "latency_s": round(sum(l.latency_s for l in layouts), 3),
            "solve_s": round(sum(l.solve_s for l in layouts), 3)}


def layout_report(layouts: list[RoomLayout], building: dict) -> str:
    lines = [f"# AI layout: {building['project']['id']}", "",
             "Rooms without documented furniture, furnished in functional groups (docs/milestone12.md §4.3-§4.5): "
             "the room's program, the group solver's top candidates (every one checked: inside the room, no overlap, "
             "doors, windows, walkways, use zones, group checks G1-G14), the vision model's choice (else the "
             "solver's best). Every added piece is `added_by_ai`, `method: rule`, with its group.", "",
             "| Room | Type | Groups (options) | Candidates (score, hard) | Chosen | By | Added | Solve s | Result |",
             "|---|---|---|---|---|---|---|---|---|"]
    for l in layouts:
        groups = ", ".join(f"{g['group']}{'*' if g.get('drawn') else ''} ({'/'.join(g['options'])})"
                           for g in (l.program or {}).get("groups", [])) or "-"
        cands = ", ".join(f"#{c['rank']} {c['score']:.1f} {len(c['hard_failures'])}" for c in l.candidates) or "-"
        added = ", ".join(f["type"] for f in l.pieces) or "-"
        by = (l.choice or {}).get("by", "-")
        result = f"room stays empty: {l.skipped}" if l.skipped else "ok"
        if l.copied_from and l.copied_from.get("used", True) and not l.skipped:
            result = f"copied from {l.copied_from['room']} ({l.copied_from['kind']})" + (
                f", {len(l.copy_dropped)} copies dropped" if l.copy_dropped else "")
        lines.append(f"| {l.label} ({l.room_id}) | {l.room_type} | {groups} | {cands} | {l.chosen or '-'} | {by} | "
                     f"{added} | {l.solve_s:.2f} | {result} |")
    choices = [(l, l.choice) for l in layouts if l.choice and l.choice.get("by") == "vlm"]
    if choices:
        lines += ["", "Choices of the vision model:", ""]
        lines += [f"- {l.room_id}: candidate {c['rank']}: {c.get('reason')}" for l, c in choices]
    fallbacks = [(l, l.choice) for l in layouts if l.choice and l.choice.get("by") != "vlm" and l.choice.get("error")]
    if fallbacks:
        lines += ["", "Rooms that took the solver's best candidate because the choice failed:", ""]
        lines += [f"- {l.room_id}: {c.get('error')}" for l, c in fallbacks]
    return "\n".join(lines) + "\n"


def write_room_debug(room: dict, layout: RoomLayout, building: dict, debug_dir: Path) -> None:
    debug_dir.mkdir(parents=True, exist_ok=True)
    record = layout.to_dict()
    record["program_full"] = layout.program
    record["candidates_full"] = [{k: v for k, v in c.items()} for c in layout.candidates]
    if layout.choice:
        record["choice_full"] = {k: v for k, v in layout.choice.items()}
    (debug_dir / f"{room['id']}.json").write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
    try:
        source = {k: v for k, v in building.items()}
        source["furniture"] = [f for f in building["furniture"] if f.get("source") == "from_documents"]
        draw_candidates_png(source, room, layout.candidates, debug_dir / f"{room['id']}.png", layout.chosen)
    except ImportError as exc:   # matplotlib missing: the JSON is the record, the PNG is a convenience
        print(f"layout: debug PNG for {room['id']} skipped ({exc})", file=sys.stderr)
    except Exception as exc:     # noqa: BLE001 - real03: an odd geometry must not fail the stage over a picture
        print(f"layout: debug PNG for {room['id']} not drawn ({type(exc).__name__}: {exc})", file=sys.stderr)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv: Optional[list[str]] = None, client_factory=None) -> int:
    parser = argparse.ArgumentParser(description="Furniture layout of empty rooms and the completion of rooms with "
                                                 "drawn furniture, in functional groups (Milestone 12)")
    parser.add_argument("building", help="building.json (or building_fitted.json)")
    parser.add_argument("--style", help="style.json from python -m wenart.style")
    parser.add_argument("--server", default=DEFAULT_SERVER, help=f"vLLM server base URL (default {DEFAULT_SERVER})")
    parser.add_argument("--model", default=None, help=f"model id (default: first served, e.g. {DEFAULT_MODEL})")
    parser.add_argument("--out", required=True, help="furnished building JSON")
    parser.add_argument("--debug", help="folder for the program, candidates and images per room")
    parser.add_argument("--passes", type=int, default=2, help="accepted for older callers; not used (Milestone 12)")
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
    furnished, layouts = furnish_building(building, style_text, client, debug_dir=debug, partners=partners)
    profile = style[0] if isinstance(style, list) and style else style
    family = profile.get("family") if isinstance(profile, dict) else None
    completed, records = C.complete_building(furnished, style_text, client, settings, debug_dir=debug, family=family,
                                             style=profile if isinstance(profile, dict) else None)
    down = getattr(client, "down", None)
    if down:
        print(f"layout: the vision model could not be reached ({down}): every room took the solver's best candidate",
              file=sys.stderr)
    keep_rooms = [r.room_id for r in records if r.state == "kept"]
    violations = LK.check(building, completed, "keep" if settings.mode == "keep" else "complete", keep_rooms)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    model = next((l.choice.get("model") for l in layouts if l.choice and l.choice.get("model") not in (None, "?")),
                 None)
    model = model or next((r.choice.get("model") for r in records if r.choice and r.choice.get("model")
                           not in (None, "?")), args.model or "?")
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
    summary["vision_model_down"] = down
    summary["completion"] = {k: completion[k] for k in ("rooms_completed", "rooms_copied", "changes_applied",
                                                         "pieces_added", "wall_cabinets", "latency_s")}
    (out.parent / "layout.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    (out.parent / "layout_report.md").write_text(layout_report(layouts, completed), encoding="utf-8")
    for l in layouts:
        state = f"{len(l.pieces)} added, candidate {l.chosen} ({(l.choice or {}).get('by')})" if l.chosen \
            else f"empty ({l.skipped})"
        if l.copied_from and l.copied_from.get("used", True) and l.pieces:
            state = f"{len(l.pieces)} copied from {l.copied_from['room']}"
        print(f"layout: {l.room_id} [{l.room_type}] {state}, solve {l.solve_s:.1f} s, choice {l.latency_s:.1f} s")
    for r in records:
        print(f"layout: {r.room_id} [{r.room.get('room_type')}] {r.state}: {len(r.added)} added, "
              f"{len(r.wall_cabinets)} wall cabinet(s), {r.latency_s:.1f} s" + (f" ({r.reason})" if r.reason else ""))
    print(f"layout: {summary['pieces_added']} pieces added to empty rooms, {completion['pieces_added']} added to "
          f"furnished rooms, locked check passed -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
