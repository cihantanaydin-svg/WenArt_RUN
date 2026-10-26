"""The vision critic (docs/milestone11.md §4, §8 step 2, §14 "vision critic hallucinates").

What: one agent-model call per room and one per exterior view, with a strict JSON-schema answer
``{"findings": [{check, severity, target, message, evidence_image}]}``:

- a room gets up to 4 images: its top-down image (CPU, ``topdown``), up to 2 preview renders of its views and its
  plan crop (when one exists);
- an exterior view gets its preview and, when one exists, the plan crop of its level.

A finding is kept only when its target is a real id of what was shown (the room, a piece of the room, an opening of
the room, a view of the room; for an exterior view: the view id, ``building`` or an exterior wall / opening id),
its evidence image exists, and the code does not contradict it: a finding of a check that code measures alone
(``how: C``) is dropped when that code family ran and found no such violation on the target; a finding equal to
a code finding (same check and target) is dropped as a duplicate. Every dropped finding is returned with the
reason (the loop logs it).

Why: the model only proposes; code checks decide (CLAUDE.md evidence rules). One pass at temperature 0 replaces
the two-pass rule because every finding is checked by code (M11 D8).

How: ``critique(model, ...)`` is pure apart from the model call and the top-down PNG; prompts in ``prompts``.

Milestone 12 (docs/milestone12.md §5.4, §1.4 "critic quality", bug B5):

- only BUILT pieces are ids of a room (a ``build: false`` piece is in no render; real03 run 3: 12 of 24 kept vision
  findings targeted unbuilt pieces);
- ``critique_room(..., looks=True)`` (the loop's mode) asks only what the renders show (``prompts.ROOM_LOOK_CHECKS``:
  room type, finishes, odd or wrong objects, decor that looks wrong, the camera) on the room's previews and plan
  crop, never what code measures (no top-down image);
- a finding is a duplicate when code already has a finding on the same target in the same family of checks
  (``RELATED``: placement, type, size, decor), not only under the same id (run 3: 60 of 101 vision findings
  repeated code findings under other ids).

Fix round after P3 (16-17 Oct 2026; docs/milestone13.md §14.8 "Attempt 2"): a code record outranks AI vision.
``roof_record(building)`` is the roof the build makes: the drawn type and pitches with the agent's
``exterior.roof`` override on top (``wenart.blender.roof.apply_override``, the build's own rule); the exterior prompt
states its type, source, pitches and overhang. An X2 vision finding that judges the roof TYPE (``is_roof_type_claim``:
it names a roof type with a mismatch word and is not about coverage or a gap) is dropped with the reason when the
built type is the drawn one (``roof_matches``: a known type, no override to another type). Why: P3's vision critic
read the built mansard (type_source plan_roof_lines) as "a standard hipped or gable roof, not a mansard roof as
specified in the brief" in rounds 2-4 (critical in rounds 3-4); an accepted ``set_exterior`` (mansard, 45 deg) was
counted as removing it, and it came back. A roof the agent overrode to another type keeps the vision finding (M12
real04: a corridor session flattened the roof; "the roof is flat, but the building specification requires a
mansard roof" was right).

Fix round after P4a (17 Oct 2026; pod P4a, real02): a D2 / F1 / F9 finding on a piece whose message is about a light
fixture (``light_subject``: a lamp, sconce, wall light ... named before the piece's id or type words, and the piece
is no light) is re-routed (``reroute_light_findings``): its target becomes the room, its cause ``light_fixture`` (no
tool, reported to the lighting stage: ``causes.REPORT_TO``), and its evidence keeps the piece it named
(``metrics.target_was``). Why: P4a's "the wall-mounted lamp next to the desk is rendered as a crude, flat rectangular
box" (a rig wall light) was put on the desk f_L0_029; a swap_model of the desk was accepted and the finding came back.

Fix round after P4b (17 Oct 2026; the review of the P4a fix round, pod P4b's real03 and the lead's decisions):

- a light-fixture finding goes to the piece that IS the light before the rig gets it (``light_target``): a decor lamp
  or light on the piece or over it (``host_id``, a ``ceiling:over_<piece>`` slot: the table lamp on the nightstand,
  the pendant over the table) takes it with the cause ``decor_model`` (reported to the decor stage); a floor lamp of
  the room (the nearest built lamp piece) takes it with its own tools (``swap_model``); only a wall light, or a light
  with no such piece, is the rig's (``light_fixture``). Why: real02 has 2 hosted table lamps and 10 floor lamps;
  "the floor lamp beside the sofa is a plain cylinder" was sent to the lighting stage and its fixable path was lost;
- the exterior critic is told every camera's role and its eye height and pitch measured by code
  (``prompts.camera_note``, ``camera_eye``: the camera z over the scene manifest's terrain, ``scene_ground_z``), and
  an X6 claim the code contradicts is dropped (``drop_camera_claims``): a height or angle claim when the measured eye
  height is within ``exterior_checks.EYE_LEVEL_RANGE_M``, the pitch within 0.5 degrees and the code has no X6 on the
  view; a "frontal, not a corner view" claim only on a frontal or entrance view; a "not the whole building" claim
  only on an entrance view. A corner view keeps a "frontal" claim (P4b's round-3 ext_2 claim was right). Why: P4b's
  vision X6 asked every view for a 3/4 corner at 1.5-1.7 m while the code's X6 asked for a frontal entrance view, so
  the cameras flipped between frontal and corner each round and 5 "low angle" claims sat on cameras 1.60 m above the
  ground.

Pass before P5 (17 Oct 2026; the review of the fix round after P4b):

- the eye height is measured on the ground the code's X6 and the camera validator use (``ground_z``:
  ``exterior_checks._ground_z`` on the site of ``build.prepare`` of the building); the scene manifest's terrain
  (``scene_ground_z``) only stands in when the build makes no site of the building. Why: real04's terrain is a
  ``tin`` whose manifest record has no surface, so ``camera_eye`` gave no eye height for any of its 6 exterior
  cameras (P3, ``runs/20261016-172855-full``), while X6 measured 1.60 m for ext_1-ext_4; the critic was never told
  the height and P3's "low angle, looking up" on ext_3 (z 2.87 over the ground at 1.27) was never dropped;
- the frontal view is X6's own rule (``x6_frontal``: a ``frontal`` view, or an ``elevation`` / ``agent`` view that
  looks square at the main facade, ``main_facade_of``), so a view the agent placed in front of the entrance facade
  is told as the frontal view (``camera_role`` -> ``prompts.camera_note``) and a "flat frontal, not a 3/4 corner"
  claim on it is dropped. Why: real04's planner drops ext_6 (P3: "inside the copy; 100% of the view blocked by
  trees"), so its frontal view is one the agent adds, labelled ``agent`` by the build; the critic was told only "a
  view the agent placed", kept the claim and sent the camera to a corner pose again (decision 2).

Pass before P5, round 2 (17 Oct 2026; P3's real04 log): a height claim on the aerial or site view the camera policy
allows (``allowed_aerial``: ``aerial_allowed`` / ``site_view`` on a pose that looks down at least
``build.AGENT_AERIAL_MIN_DOWN_DEG``, the build's aerial rule) is dropped with the reason: the view above eye level is
a design choice (docs/milestone13.md D8 and the site view rule), and a code record outranks AI vision. Why: on P3 the
critic said "high angle looking down, not at eye level" 9 times on ext_5 (aerial_allowed) and ext_7 (aerial_allowed,
site_view) in rounds 1-6 although the prompt told it the view is allowed; each claim was kept with the cause
exterior_camera (set_camera offered) and the round-6 set brought ext_5 down to z 2.46. ``tools.role_problem`` refuses
such a set too (the aerial role). Review of round 2: the pose must also stand on or above the high-view line of the
camera validator and code X6 (``high_view_line``: the roof's ``ridge_z`` + ``HIGH_VIEW_ABOVE_RIDGE_M``, 7.01 m on
real04); below it the validator and X6 judge the camera as an eye-level view, so a claim "at eye level looking down"
on a flagged record there is kept. Why: real04's ext_5 set 1.60 m over the ground and aimed 6 degrees down passed the
5-degree rule, the build kept it ``aerial`` with ``aerial_allowed``, and such a claim was dropped.

Fix round after P5 (22 Oct 2026): V1 and the code critic's ``camera_blocked`` (``critic_code.blocked_items``: the
lens touches a surface or one element fills the frame) are one family in ``RELATED``: a vision V1 on a view the code
measured blocked is a duplicate of that code finding (the code's names the element, the depth and the share).

Fix round after P6a (22 Oct 2026; pod P6a, real04): ``x6_frontal`` is ``exterior_checks.x6_frontal``, X6's one rule:
an ``elevation`` / ``agent`` view square to the main facade is the frontal view only when it frames the whole building
with the sky (its recorded or measured ``fill`` / ``fits`` / ``sky_share``). ``critique_exterior`` passes its building
and plan, so an agent view that shows only part of the facade (P6a's ext_front_entrance: a blank wall, no sky) is told
as a view the agent placed, not as the frontal view.

Fix round after P6a (23 Oct 2026), review: X6's rule also judges a high agent pose and an agent plan the build keeps
labelled ``frontal`` (a set of the planner's frontal view to another square pose) by their frame, so ``camera_role``
tells such a plan that frames only part of the building or no sky as ``agent`` too.
"""
from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Optional

from wenart.agent import critic_code as CC
from wenart.agent import prompts as P
from wenart.agent import topdown as TD
from wenart.agent.model import MAX_IMAGES, user_message


def answer_schema(checks) -> dict:
    return {"type": "object", "additionalProperties": False, "required": ["findings"],
            "properties": {"findings": {"type": "array", "maxItems": 12, "items": {
                "type": "object", "additionalProperties": False,
                "required": ["check", "severity", "target", "message", "evidence_image"],
                "properties": {"check": {"enum": list(checks)}, "severity": {"enum": list(P.SEVERITIES)},
                               "target": {"type": "string", "minLength": 1, "maxLength": 80},
                               "message": {"type": "string", "minLength": 3, "maxLength": 300},
                               "evidence_image": {"type": "integer", "minimum": 1, "maximum": MAX_IMAGES}}}}}}


ROOM_SCHEMA = answer_schema(P.ROOM_CHECKS)
LOOK_SCHEMA = answer_schema(P.ROOM_LOOK_CHECKS)
EXTERIOR_SCHEMA = answer_schema(P.EXTERIOR_CHECKS)
# Families of checks that name the same problem (a vision finding of one is a duplicate of a code finding of another).
_PLACEMENT = ("F3", "F4", "F5", "F6", "F7", "F8", "R3", "S2", "S3", *(f"G{i}" for i in range(1, 14)))
_TYPE = ("F1", "F9", "G14", "S6", "D2", "LG")
_SIZE = ("F2", "S4")
_DECOR = ("D1", "S5")
# fix round after P5: a view the code critic measured blocked (critic_code.blocked_items) is that view's V1
_CAMERA = ("V1", "camera_blocked")
RELATED = {c: fam for fam in (_PLACEMENT, _TYPE, _SIZE, _DECOR, _CAMERA) for c in fam}


def room_ids(building: dict, room_id: str, views: list[str]) -> set:
    """The ids a room finding may target: the room, its BUILT pieces (B5), its openings and views."""
    from wenart.furniture import placer
    room = next((r for r in building.get("rooms") or [] if r.get("id") == room_id), None)
    ids = {room_id} | set(views)
    if room is None:
        return ids
    ids |= {f.get("id") for f in building.get("furniture") or [] if f.get("room_id") == room_id
            and TD.is_built(f)}
    try:
        doors, windows = placer.room_openings(building, room)
        ids |= {o.get("id") for o in doors + windows}
    except Exception:  # noqa: BLE001 - a room without a usable polygon: no opening ids
        pass
    return {i for i in ids if i}


def exterior_ids(building: dict, view: str) -> set:
    ids = {view, "building"}
    ids |= {w.get("id") for w in building.get("walls") or [] if w.get("exterior")}
    ext_walls = {w.get("id") for w in building.get("walls") or [] if w.get("exterior")}
    ids |= {o.get("id") for o in building.get("openings") or [] if o.get("wall_id") in ext_walls}
    return {i for i in ids if i}


def screen(answer: Optional[dict], allowed: set, n_images: int, code: dict, room_id: Optional[str],
           source: str = "vision", call_id: str = "") -> tuple[list[dict], list[dict]]:
    """``(kept, dropped)`` findings of one answer (module docstring rules)."""
    kept, dropped = [], []
    ran = CC.measured(code)
    code_hits = {(f["check"], f["target"]) for f in code.get("findings") or []}
    for f in code.get("findings") or []:            # M12: the same target under a related check id
        for c in RELATED.get(f["check"], ()):
            code_hits.add((c, f["target"]))
    for i, item in enumerate((answer or {}).get("findings") or []):
        f = {"id": f"v:{call_id}:{i + 1}", "source": source, "check": item.get("check"),
             "severity": item.get("severity"), "target": item.get("target"), "room_id": room_id,
             "message": item.get("message"), "evidence": {"image": item.get("evidence_image"), "call_id": call_id}}
        why = None
        if item.get("target") not in allowed:
            why = f"target {item.get('target')!r} is not an id of what was shown"
        elif not 1 <= int(item.get("evidence_image") or 0) <= n_images:
            why = f"evidence image {item.get('evidence_image')} does not exist ({n_images} images)"
        elif (item.get("check"), item.get("target")) in code_hits:
            why = "duplicate of a code finding"
        elif P.CHECKLIST.get(item.get("check"), {}).get("how") == "C" and CC.FAMILY_OF.get(item.get("check")) in ran:
            why = f"code contradicts: {item.get('check')} measured by code without a violation on {item.get('target')}"
        if why:
            f["dropped"] = why
            dropped.append(f)
        else:
            kept.append(f)
    return kept, dropped


# Fix round after P4a (module docstring): the words of a light fixture in a finding's message (never the adjective
# "light": "a light grey sofa"), the piece types that are lights, and the checks a re-route applies to.
LIGHT_WORDS = re.compile(r"\b(?:lamps?|sconces?|chandeliers?|luminaires?|spotlights?|downlights?|pendant lights?|"
                         r"(?:wall|ceiling|bedside|reading|wall-mounted|wall mounted|recessed|panel|strip)[ -]lights?|"
                         r"light[ -](?:fixtures?|fittings?|panels?))\b")
LIGHT_TYPE_WORDS = ("lamp", "light", "sconce", "chandelier", "pendant")
REROUTE_CHECKS = ("D2", "D3", "F1", "F9")
LIGHT_CAUSE = "light_fixture"               # = causes (no tool, REPORT_TO lighting)


def light_subject(message: str, piece: Optional[dict]) -> Optional[str]:
    """The light fixture a finding's ``message`` is about (``LIGHT_WORDS``) when it names it before the piece (its id
    or a word of its type, 3 letters or more) and the piece is no light; else None."""
    if not isinstance(piece, dict):
        return None
    text = str(message or "").lower()
    m = LIGHT_WORDS.search(text)
    if m is None:
        return None
    ptype = str(piece.get("type") or "").lower()
    if any(w in ptype for w in LIGHT_TYPE_WORDS):
        return None
    words = [str(piece.get("id") or "").lower()] + [w for w in re.split(r"[_\s]+", ptype) if len(w) >= 3]
    hits = [h.start() for w in words if w for h in [re.search(rf"\b{re.escape(w)}s?\b", text)] if h]
    if hits and min(hits) < m.start():
        return None
    return m.group(0)


# Fix round after P4b (module docstring): the kind of light a message names, from the two words before the light word
# and the light word itself, and the decor types of a ceiling light.
WALL_LIGHT_WORDS = ("wall", "wall-mounted", "sconce", "sconces", "mirror", "vanity", "strip", "mounted")
CEILING_LIGHT_WORDS = ("pendant", "ceiling", "chandelier", "chandeliers", "recessed", "downlight", "downlights",
                       "spotlight", "spotlights", "panel", "hanging", "suspended")
FLOOR_LIGHT_WORDS = ("floor", "standing", "arc", "tripod")
TABLE_LIGHT_WORDS = ("table", "bedside", "desk", "nightstand", "reading")
CEILING_DECOR_WORDS = ("pendant", "ceiling", "chandelier")
DECOR_CAUSE = "decor_model"                 # = causes (no tool, REPORT_TO decor)


def light_kind(message: str) -> str:
    """Fix round after P4b: ``wall``, ``ceiling``, ``floor``, ``table`` or ``generic``: the light a message names
    (``LIGHT_WORDS``), by the words just before it ("the wall-mounted lamp", "the floor lamp") and the light word
    itself ("pendant light", "sconce"); "on the wall" anywhere makes it a wall light."""
    text = str(message or "").lower()
    m = LIGHT_WORDS.search(text)
    if m is None:
        return "generic"
    words = re.findall(r"[a-z][a-z-]*", text[:m.start()])[-2:] + re.findall(r"[a-z][a-z-]*", m.group(0))
    words += [x for w in words if "-" in w for x in w.split("-")]
    for kind, table in (("wall", WALL_LIGHT_WORDS), ("ceiling", CEILING_LIGHT_WORDS), ("floor", FLOOR_LIGHT_WORDS),
                        ("table", TABLE_LIGHT_WORDS)):
        if any(w in table for w in words):
            return kind
    if "on the wall" in text or "wall-mounted" in text or "wall mounted" in text:
        return "wall"
    return "generic"


def _is_light_type(ptype) -> bool:
    t = str(ptype or "").lower()
    return any(w in t for w in LIGHT_TYPE_WORDS)


def light_target(message: str, piece: dict, building: dict, room_id: str) -> Optional[dict]:
    """Fix round after P4b (module docstring): the piece a light-fixture finding on ``piece`` is really about:
    ``{"kind": "decor" | "furniture", "id", "type"}``, or None for the room's lighting rig (a wall light, or no
    lamp or light piece on, over or near ``piece``)."""
    kind = light_kind(message)
    if kind == "wall":
        return None
    pid = piece.get("id")
    tied = [d for d in building.get("decor") or [] if isinstance(d, dict) and _is_light_type(d.get("type"))
            and (d.get("host_id") == pid or str(d.get("slot") or "").endswith(f"over_{pid}"))]
    on = [d for d in tied if "lamp" in str(d.get("type")).lower()]
    over = [d for d in tied if any(w in str(d.get("type")).lower() for w in CEILING_DECOR_WORDS)]
    centre = (piece.get("footprint") or {}).get("center") or [0.0, 0.0]

    def dist(f):
        c = (f.get("footprint") or {}).get("center") or centre
        return math.dist([float(v) for v in c[:2]], [float(v) for v in centre[:2]])

    lamps = sorted((f for f in building.get("furniture") or [] if isinstance(f, dict) and f.get("room_id") == room_id
                    and f.get("id") != pid and _is_light_type(f.get("type")) and TD.is_built(f)),
                   key=lambda f: (dist(f), str(f.get("id"))))
    if kind == "floor":
        lamps = [f for f in lamps if "floor" in str(f.get("type")).lower()] or lamps
    order = {"table": [on], "ceiling": [over], "floor": [[], lamps], "generic": [on, over, lamps]}[kind]
    for group in order:
        if not group:
            continue
        hit = group[0]
        return {"kind": "furniture" if group is lamps else "decor", "id": hit.get("id"), "type": hit.get("type")}
    return None


def reroute_light_findings(kept: list[dict], building: dict, room_id: Optional[str]) -> list[dict]:
    """Fix round after P4a (module docstring): the kept findings, with those about a light fixture re-routed
    (``evidence.metrics``: ``named``, ``target_was``, ``target_type``). Fix round after P4b: to the decor light
    (cause ``decor_model``) or the lamp piece (its own cause and tools) the message is about (``light_target``,
    ``metrics.light_kind``, ``retarget``), else to the room (cause ``light_fixture``)."""
    pieces = {f.get("id"): f for f in building.get("furniture") or [] if isinstance(f, dict)}
    out = []
    for f in kept:
        piece = pieces.get(f.get("target"))
        subject = light_subject(f.get("message"), piece) if f.get("check") in REROUTE_CHECKS and room_id else None
        if subject is None:
            out.append(f)
            continue
        hit = light_target(f.get("message"), piece, building, room_id)
        evidence = dict(f.get("evidence") or {})
        evidence["metrics"] = dict(evidence.get("metrics") or {}, named=subject, target_was=piece.get("id"),
                                   target_type=piece.get("type"), light_kind=light_kind(f.get("message")),
                                   retarget=(hit or {}).get("kind") or "rig")
        if hit is None:
            out.append(dict(f, target=room_id, cause=LIGHT_CAUSE, evidence=evidence))
        elif hit["kind"] == "decor":
            out.append(dict(f, target=hit["id"], cause=DECOR_CAUSE, evidence=evidence))
        else:
            g = {k: v for k, v in f.items() if k != "cause"}
            out.append(dict(g, target=hit["id"], evidence=evidence))
    return out


def with_decor_doubts(pieces: list[dict], building: dict) -> list[dict]:
    """Copies of ``pieces`` with ``decor_doubt`` [{type, doubt}]: the decor models on them that the library audit
    kept with a vision doubt (decision 1a; the prompt marks them for D2)."""
    from wenart.furniture import catalog as C
    by_host: dict = {}
    for d in building.get("decor") or []:
        doubt = C.vision_doubt(d.get("asset") if isinstance(d.get("asset"), dict) else None)
        if doubt and d.get("host_id"):
            by_host.setdefault(d["host_id"], []).append({"type": d.get("type"), "doubt": doubt})
    return [dict(p, decor_doubt=by_host[p["id"]]) if p.get("id") in by_host else p for p in pieces]


def room_context(building: dict, room_id: str, pieces: list[dict]) -> dict:
    """Milestone 13: what the critic must know (``prompts.context_lines``): the licence mode, the pieces built below
    the library level and the drawn groups of the room (``brief.below_library``, ``brief.drawn_group_lines``)."""
    from wenart.agent import brief as BR
    try:
        groups = BR.drawn_group_lines(building, room_id)
    except Exception:  # noqa: BLE001 - a room without usable geometry has no drawn groups
        groups = []
    return {"licence_mode": BR.licence_mode_of(building), "below_library": BR.below_library(pieces),
            "drawn_groups": groups}


def critique_room(model, building: dict, room_id: str, *, previews: list[tuple[str, Path]],
                  topdown: Optional[Path], plan_crop: Optional[Path], code: dict, call_id: str,
                  looks: bool = False) -> dict:
    """One room: ``{"kept", "dropped", "error", "images"}``. ``looks`` (M12, the loop's mode): the renders and the
    plan crop only, the look checklist; else the M11 room checklist with the top-down image."""
    room = next(r for r in building.get("rooms") or [] if r.get("id") == room_id)
    images, labels = [], []
    if topdown is not None and not looks:
        images.append(topdown)
        labels.append("top-down plan of the room as built (pieces, fronts, doors, windows)")
    for view, path in previews[:3 if looks else 2]:
        images.append(path)
        labels.append(f"render of view {view}")
    if plan_crop is not None and len(images) < MAX_IMAGES:
        images.append(plan_crop)
        labels.append("crop of the source drawing (what the architect drew)")
    from wenart.furniture import placer
    try:
        doors, windows = placer.room_openings(building, room)
    except Exception:  # noqa: BLE001
        doors, windows = [], []
    pieces = [f for f in building.get("furniture") or [] if f.get("room_id") == room_id
              and TD.is_built(f)]
    pieces = with_decor_doubts(pieces, building)
    room_code = [f for f in code.get("findings") or [] if f.get("room_id") == room_id]
    views = [v for v, _ in previews]
    if looks:
        prompt = P.room_look_prompt(room, pieces, views, labels, room_code, context=room_context(building, room_id,
                                                                                                pieces),
                                    openings=doors + windows)
    else:
        prompt = P.room_critic_prompt(room, pieces, doors + windows, views, labels, room_code)
    messages = [{"role": "system", "content": P.CRITIC_SYSTEM},
                user_message(prompt, images, [f"Image {i + 1}: {lab}" for i, lab in enumerate(labels)])]
    reply = model.critic(messages, LOOK_SCHEMA if looks else ROOM_SCHEMA, call_id=call_id)
    if reply.data is None:
        return {"kept": [], "dropped": [], "error": "; ".join(reply.errors[:3]) or "no answer", "images": images}
    kept, dropped = screen(reply.data, room_ids(building, room_id, [v for v, _ in previews]), len(images), code,
                           room_id, call_id=call_id)
    kept = reroute_light_findings(kept, building, room_id)      # fix round after P4a
    return {"kept": kept, "dropped": dropped, "error": None, "images": images}


def storeys_of(building: dict) -> int:
    """Milestone 13 (bug B5): the storeys the critic is told about: the levels without their variants (``L-1b`` is a
    variant of ``L-1``: the same storey; real04 was told "4 levels" for a 3-storey villa, a false critical for 5
    rounds)."""
    ids = set()
    for lv in building.get("levels") or []:
        lid = str(lv.get("id") or "")
        if not lid:
            continue
        m = re.match(r"^(L-?\d+)[a-z]$", lid)
        ids.add(m.group(1) if m else lid)
    return len(ids)


# Fix round after P3 (module docstring): the roof types of a claim ("hipped" and "gabled" are the hip and gable
# types), the words of a mismatch claim, and the words of a coverage problem (a roof-type word in such a finding is
# no type claim: "the mansard roof does not cover the rear facade" stays).
ROOF_TYPE_WORDS = {"mansard": "mansard", "gambrel": "gambrel", "gable": "gable", "gabled": "gable",
                   "hip": "hip", "hipped": "hip", "shed": "shed", "mono-pitch": "shed", "lean-to": "shed",
                   "flat": "flat", "pitched": "pitched"}
ROOF_MISMATCH_WORDS = ("not a", "not the", "instead of", "rather than", "but", "requires", "required", "specified",
                       "specifies", "specification", "brief", "described", "should be", "expected", "roof type")
ROOF_COVERAGE_WORDS = ("cover", "missing", "gap", "hole", "poke", "through", "expose", "transparent", "open",
                       "float", "furniture", "visible from above", "wall rises", "above the roof")


def roof_record(building: dict) -> dict:
    """The roof the build makes (module docstring): ``{"type", "drawn_type", "source", "pitches", "overhang_m",
    "override"}``; ``type`` None when the building has no roof record."""
    from wenart.blender import roof as RF
    drawn = building.get("roof") if isinstance(building.get("roof"), dict) else None
    override = RF.override_of(building)
    built, _changes = RF.apply_override(drawn, override)
    built = built or {}

    def value(v):
        v = v.get("value") if isinstance(v, dict) else v
        try:
            return round(float(v), 1)
        except (TypeError, ValueError):
            return None

    pitches = [p for p in (value(x) for x in built.get("pitches_deg") or []) if p is not None]
    btype, dtype = (built.get("type") if drawn else None), (drawn or {}).get("type")
    # an override that keeps the drawn type keeps its source (the drawings); another type is the agent's
    source = (drawn or {}).get("type_source") if btype == dtype else "agent override"
    return {"type": btype, "drawn_type": dtype, "source": source, "pitches": pitches,
            "overhang_m": value(built.get("overhang")), "override": dict(override) if override else None}


def roof_note(building: dict) -> str:
    """The roof sentence of the exterior prompt: the type, where it comes from, the pitches and the overhang."""
    rec = roof_record(building)
    if not rec["type"]:
        return "roof: unknown."
    parts = [f"roof as built: {rec['type']}"]
    if rec["source"]:
        parts.append(f"(from {rec['source']})")
    text = " ".join(parts)
    if rec["pitches"]:
        text += f", pitch {' / '.join(f'{p:g}' for p in rec['pitches'])} deg"
    if rec["overhang_m"] is not None:
        text += f", overhang {rec['overhang_m']:g} m"
    if rec["drawn_type"] and rec["drawn_type"] != rec["type"]:
        text += f" (the drawings say {rec['drawn_type']})"
    return text + "."


def roof_matches(building: dict) -> bool:
    """The built roof type is the drawn one and a known type (no agent override to another type): code knows the
    roof type, so a vision claim about it is no finding."""
    from wenart.blender.roof import ROOF_TYPES
    rec = roof_record(building)
    return bool(rec["type"]) and rec["type"] in ROOF_TYPES and rec["type"] != "other" \
        and rec["type"] == rec["drawn_type"]


def is_roof_type_claim(message: str) -> bool:
    """An X2 message that judges the roof's TYPE (module docstring): a roof-type word, a mismatch word, the word
    roof, and no coverage word."""
    text = f" {str(message or '').lower()} "
    if "roof" not in text or any(w in text for w in ROOF_COVERAGE_WORDS):
        return False
    words = set(re.findall(r"[a-z][a-z-]*", text))
    return bool(words & set(ROOF_TYPE_WORDS)) and any(w in text for w in ROOF_MISMATCH_WORDS)


def drop_roof_type_claims(kept: list[dict], dropped: list[dict], building: dict) -> tuple[list[dict], list[dict]]:
    """Fix round after P3: the X2 roof-type claims of ``kept`` move to ``dropped`` with the code's reason when
    ``roof_matches`` (a code record outranks AI vision)."""
    if not any(f.get("check") == "X2" for f in kept) or not roof_matches(building):
        return kept, dropped
    rec = roof_record(building)
    out = []
    for f in kept:
        if f.get("check") == "X2" and is_roof_type_claim(f.get("message")):
            dropped.append(dict(f, dropped=f"code contradicts: the build makes the drawn {rec['type']} roof "
                                          f"(type from {rec['source'] or 'the building JSON'}); a code record "
                                          f"outranks AI vision on the roof type"))
        else:
            out.append(f)
    return out, dropped


def scene_ground_z(scene: Optional[dict], x: float, y: float) -> Optional[float]:
    """Fix round after P4b: the ground z at ``(x, y)`` from the scene manifest's terrain (``site.terrain``, the
    build's ``site.ground_z``); None when the terrain is not there or its record is not enough (a summary without
    the surface)."""
    from wenart.blender import site as S
    terrain = (((scene or {}).get("site") or {}).get("terrain")) if isinstance(scene, dict) else None
    if not isinstance(terrain, dict):
        return None
    try:
        return float(S.ground_z(terrain, float(x), float(y)))
    except (KeyError, TypeError, ValueError, IndexError):
        return None


def ground_z(building: Optional[dict], scene: Optional[dict], x: float, y: float,
             prep: Optional[dict] = None) -> Optional[float]:
    """Pass before P5 (module docstring): the ground z at ``(x, y)`` as the code's X6 and the camera validator
    measure it: ``exterior_checks._ground_z`` on the site of ``build.prepare`` of ``building`` (``prep``: that plan
    when the caller has it already); the scene manifest's terrain (``scene_ground_z``) only when the build makes no
    site of the building (or no building is given). None when neither knows the ground."""
    if isinstance(building, dict):
        from wenart.blender import exterior_checks as X
        plan = prep if prep is not None else X._prep(building)
        if isinstance(plan, dict) and plan.get("site"):
            try:
                return float(X._ground_z(plan, float(x), float(y)))
            except (KeyError, TypeError, ValueError, IndexError):
                pass
    return scene_ground_z(scene, x, y)


def camera_eye(camera: Optional[dict], scene: Optional[dict], building: Optional[dict] = None,
               prep: Optional[dict] = None) -> Optional[dict]:
    """Fix round after P4b (module docstring): ``{"eye_m", "pitch_deg", "ground_z"}`` of an exterior camera
    measured by code: the camera z over the ground under it and the pitch of its line of sight; None without a pose.
    Pass before P5: the ground is ``ground_z`` (the building's site as X6 measures it, the scene's terrain only
    without one; None when unknown)."""
    if not isinstance(camera, dict) or not camera.get("position") or not camera.get("target"):
        return None
    try:
        x, y, z = (float(v) for v in camera["position"][:3])
        tx, ty, tz = (float(v) for v in camera["target"][:3])
    except (TypeError, ValueError):
        return None
    pitch = math.degrees(math.atan2(tz - z, math.hypot(tx - x, ty - y)))
    ground = ground_z(building, scene, x, y, prep)
    return {"eye_m": None if ground is None else round(z - ground, 3), "pitch_deg": round(pitch, 2),
            "ground_z": ground}


def main_facade_of(scene: Optional[dict], building: Optional[dict] = None,
                   prep: Optional[dict] = None) -> Optional[dict]:
    """Pass before P5 (module docstring): the main (entrance) facade whose frontal view X6 asks for
    (``axis``, ``direction``): the scene manifest's ``whole_building.main_facade``, else ``build.prepare``'s of
    ``building`` (``prep`` when the caller has it); None without a direction."""
    main = ((scene.get("whole_building") or {}).get("main_facade")) if isinstance(scene, dict) else None
    if not (isinstance(main, dict) and main.get("direction")) and isinstance(building, dict):
        from wenart.blender import exterior_checks as X
        plan = prep if prep is not None else X._prep(building)
        main = (plan or {}).get("main_facade") if isinstance(plan, dict) else None
    return main if isinstance(main, dict) and main.get("direction") else None


X6_FRONTAL_POSE_VIEWS = ("elevation", "agent")      # = exterior_checks.FRONTAL_POSE_VIEWS (asserted in the tests)


def x6_frontal(camera: Optional[dict], main: Optional[dict], *, building: Optional[dict] = None,
               prep: Optional[dict] = None) -> bool:
    """Pass before P5 (module docstring): ``camera`` is the frontal view X6 asks for, by X6's own rule
    (``exterior_checks.x6_frontal``): its view is ``frontal``, or ``elevation`` / ``agent`` with a pose that looks
    square (``exterior_checks._faces``, within 30 degrees) at the main facade ``main`` (``main_facade_of``).

    Fix round after P6a (22 Oct 2026; pod P6a, real04): and that frames the whole building with the sky
    (``exterior_checks.frames_building``): the frame the camera record carries (``fill`` / ``fits`` / ``sky_share``,
    recorded by the build on the agent's plans), else measured on the build's exterior model of ``building``
    (``prep``: ``build.prepare``'s plan when the caller has it); a pose whose frame cannot be measured keeps the pose
    rule. Why: P6a's agent camera ext_front_entrance (a blank wall 5 m away, both doors cut, no sky) was told to the
    critic as "the frontal view", so its vision X3 / X6 claims were judged as about a frontal view and the camera
    tools' role guards protected it.

    Fix round after P6a (23 Oct 2026), review: X6's rule judges a high pose and an agent plan labelled ``frontal`` by
    their frame too (``exterior_checks.x6_frontal``); the ridge is no longer passed."""
    if not isinstance(camera, dict):
        return False
    from wenart.blender import exterior_checks as X
    model = None
    if isinstance(prep, dict) or isinstance(building, dict):
        plan = prep if isinstance(prep, dict) else (X._prep(building) or {})
        made: list = []

        def model():
            if not made:
                made.append(X.exterior_model(plan))
            return made[0]
    try:
        return bool(X.x6_frontal(camera, main, model=model))
    except (KeyError, TypeError, ValueError, IndexError):
        return False


def camera_role(camera: Optional[dict], main: Optional[dict], *, building: Optional[dict] = None,
                prep: Optional[dict] = None) -> Optional[str]:
    """Pass before P5 (module docstring): the role the critic is told and the claims are judged by: ``frontal`` for
    an ``agent`` view that is X6's frontal view (``x6_frontal``; fix round after P6a: with ``building`` / ``prep`` its
    frame is measured when the record does not carry it), else the camera's own ``view``.

    Fix round after P6a (23 Oct 2026), review: ``agent`` for an agent plan (``exterior_checks._agent_camera``) that
    the build keeps labelled ``frontal`` but that is not X6's frontal view (it frames only part of the building or no
    sky), as for P6a's ext_front_entrance: the critic is not told "the one frontal view X6 asks for" about it."""
    if not isinstance(camera, dict):
        return None
    if camera.get("view") == "agent" and x6_frontal(camera, main, building=building, prep=prep):
        return "frontal"
    from wenart.blender import exterior_checks as X
    if camera.get("view") == "frontal" and X._agent_camera(camera) \
            and not x6_frontal(camera, main, building=building, prep=prep):
        return "agent"
    return camera.get("view")


# Fix round after P4b (module docstring): the claims of a vision X6 by kind (any word of a kind makes the claim).
HEIGHT_CLAIM_WORDS = ("eye level", "eye-level", "height", "low angle", "low-angle", "high angle", "high-angle",
                      "looking up", "looking down", "worm", "tilt", "pitch", "too low", "too high", "ground level",
                      "from below", "upward", "downward")
FRONTAL_CLAIM_WORDS = ("frontal", "front-on", "straight-on", "straight on", "head-on", "flat elevation",
                       "elevation view", "3/4", "three-quarter", "three quarter", "corner view", "single facade",
                       "one facade", "only one facade", "two facades")
FRAME_CLAIM_WORDS = ("whole building", "entire building", "not in frame", "out of frame", "cut off", "cropped",
                     "partial view", "part of the building", "too close")
PITCH_LEVEL_DEG = 0.5                      # = exterior_checks._x6's level camera (a minor X6 above it)


def camera_claims(message: str) -> set:
    """Fix round after P4b: the kinds of an X6 claim in ``message``: ``height``, ``frontal``, ``frame``."""
    text = str(message or "").lower()
    out = set()
    for kind, words in (("height", HEIGHT_CLAIM_WORDS), ("frontal", FRONTAL_CLAIM_WORDS),
                        ("frame", FRAME_CLAIM_WORDS)):
        if any(w in text for w in words):
            out.add(kind)
    return out


AERIAL_SOURCE = "docs/milestone13.md D8 and the site view rule"
HIGH_VIEW_ABOVE_RIDGE_M = 1.0   # = exterior_checks.validate_camera_override and _x6: z >= ridge_z + 1.0 is a high view


def high_view_line(building: Optional[dict] = None, prep: Optional[dict] = None) -> Optional[tuple[float, float]]:
    """Pass before P5, round 2, review (module docstring): ``(ridge_z, line)`` of the high-view line the camera
    validator and code X6 use (``exterior_checks.validate_camera_override`` / ``_x6``: an exterior camera with
    ``z >= ridge_z + 1.0`` is a high view, below it the eye height must lie in ``EYE_LEVEL_RANGE_M``): the roof's
    ``ridge_z`` of ``build.prepare`` (``prep``: that plan when the caller has it, else ``exterior_checks._prep`` of
    ``building``; 0.0 without a roof, as the validator reads it) and that ridge + ``HIGH_VIEW_ABOVE_RIDGE_M``. None
    without a building or a plan."""
    if not isinstance(prep, dict):
        if not isinstance(building, dict):
            return None
        from wenart.blender import exterior_checks as X
        prep = X._prep(building) or {}
    try:
        ridge = float(((prep.get("roof") or {}).get("ridge_z")) or 0.0)
    except (TypeError, ValueError, AttributeError):
        ridge = 0.0
    return ridge, ridge + HIGH_VIEW_ABOVE_RIDGE_M


def allowed_aerial(camera: Optional[dict], eye: Optional[dict] = None, *, building: Optional[dict] = None,
                   prep: Optional[dict] = None) -> Optional[str]:
    """Pass before P5, round 2 (module docstring): ``site view`` / ``aerial view`` when ``camera`` is the view the
    camera policy allows above eye level: it carries ``site_view`` / ``aerial_allowed`` (the build keeps them only on
    an aerial or site pose, ``build.AGENT_AERIAL_FLAGS``) and its pose looks down at least
    ``build.AGENT_AERIAL_MIN_DOWN_DEG`` (the build's aerial rule; ``eye``: ``camera_eye`` when the caller has it);
    None otherwise. Review of round 2: the pose also stands on or above the high-view line of the validator and X6
    (``high_view_line`` of ``building`` / ``prep``); without either, its measured eye height (``eye["eye_m"]``) lies
    above ``EYE_LEVEL_RANGE_M``. A pose below the line, or of an unknown height, is no allowed aerial: the claim
    stays."""
    if not isinstance(camera, dict) or not (camera.get("aerial_allowed") or camera.get("site_view")):
        return None
    from wenart.blender import build as B
    from wenart.blender import exterior_checks as X
    pitch = (eye or {}).get("pitch_deg")
    if pitch is None:
        if not camera.get("position") or not camera.get("target"):
            return None
        try:
            pitch = -B._down_pitch_deg(camera["position"], camera["target"])
        except (TypeError, ValueError, IndexError):
            return None
    if -float(pitch) < B.AGENT_AERIAL_MIN_DOWN_DEG - 1e-9:
        return None
    line = high_view_line(building, prep)
    if line is not None:
        try:
            if float(camera["position"][2]) < line[1]:
                return None                  # the validator and X6 judge it as an eye-level view
        except (KeyError, TypeError, ValueError, IndexError):
            return None
    elif (eye or {}).get("eye_m") is None or float(eye["eye_m"]) <= X.EYE_LEVEL_RANGE_M[1] + 1e-3:
        return None
    return "site view" if camera.get("site_view") else "aerial view"


def drop_camera_claims(kept: list[dict], dropped: list[dict], view: str, camera: Optional[dict],
                       eye: Optional[dict], code: dict, role: Optional[str] = None, *, building: Optional[dict] = None,
                       prep: Optional[dict] = None) -> tuple[list[dict], list[dict]]:
    """Fix round after P4b (module docstring): the X6 claims on ``view`` that the code contradicts move to
    ``dropped`` with the reason: every claim kind of the message (``camera_claims``) must be one the code record
    answers (height: the measured eye height within ``EYE_LEVEL_RANGE_M``, level within ``PITCH_LEVEL_DEG`` and no
    code X6 on the view; frontal: the camera's role is frontal or entrance; frame: the role is entrance). A message
    with no known claim, or one kind the code does not answer, stays. Pass before P5: ``role`` (``camera_role``:
    ``frontal`` for an agent view that is X6's frontal view) replaces the camera's ``view``. Pass before P5, round 2:
    a height claim on the aerial or site view the camera policy allows (``allowed_aerial``) is answered by that
    record: its height and downward pitch are by design (``AERIAL_SOURCE``), so the claim is dropped and no camera
    tool is offered to bring the view down to eye level (P3's 9 "high angle, not at eye level" claims on real04's
    ext_5 / ext_7). Review of round 2: only for a pose on or above the high-view line (``allowed_aerial`` with
    ``building`` / ``prep``)."""
    from wenart.blender import exterior_checks as X
    if not any(f.get("check") == "X6" and f.get("target") == view for f in kept) or not isinstance(camera, dict):
        return kept, dropped
    role = role or camera.get("view")
    code_x6 = any(f.get("check") == "X6" and f.get("target") == view for f in code.get("findings") or [])
    eye_ok = bool(eye) and eye.get("eye_m") is not None and not code_x6 \
        and X.EYE_LEVEL_RANGE_M[0] - 1e-3 <= float(eye["eye_m"]) <= X.EYE_LEVEL_RANGE_M[1] + 1e-3 \
        and abs(float(eye.get("pitch_deg") or 0.0)) <= PITCH_LEVEL_DEG + 1e-9
    aerial = allowed_aerial(camera, eye, building=building, prep=prep)
    answers = {"height": eye_ok or bool(aerial), "frontal": role in ("frontal", "elevation", "entrance"),
               "frame": role == "entrance"}
    out = []
    for f in kept:
        claims = camera_claims(f.get("message")) if f.get("check") == "X6" and f.get("target") == view else set()
        if not claims or not all(answers.get(c) for c in claims):
            out.append(f)
            continue
        parts = []
        if "height" in claims and aerial:
            flags = ", ".join(k for k in ("aerial_allowed", "site_view") if camera.get(k))
            measured = []
            if eye and eye.get("eye_m") is not None:
                measured.append(f"eye {float(eye['eye_m']):.2f} m above the ground")
            if eye and eye.get("pitch_deg") is not None:
                measured.append(f"looking {round(-float(eye['pitch_deg']), 1) + 0.0:.1f} deg down")
            parts.append(f"{view} is the {aerial} the camera policy allows ({flags}; {AERIAL_SOURCE}): its height "
                         f"above eye level and its downward pitch are by design"
                         + (f" ({', '.join(measured)}, measured by code)" if measured else "")
                         + "; a code record outranks AI vision")
        elif "height" in claims:
            parts.append(f"eye {float(eye['eye_m']):.2f} m above the ground, pitch {float(eye['pitch_deg']):.1f} deg "
                         f"(measured by code, within {X.EYE_LEVEL_RANGE_M[0]:g}-{X.EYE_LEVEL_RANGE_M[1]:g} m)")
        if claims & {"frontal", "frame"}:
            parts.append(f"{view} is the {role} view the camera policy requires (square to one facade"
                         + (", the door up close, not the whole building" if role == "entrance" else "") + ")")
        dropped.append(dict(f, dropped="code contradicts: " + "; ".join(parts)))
    return out, dropped


def critique_exterior(model, building: dict, view: str, *, preview: Path, plan_crop: Optional[Path], code: dict,
                      call_id: str, camera: Optional[dict] = None, scene: Optional[dict] = None) -> dict:
    """One exterior view. ``camera`` (round 2, Milestone 13 D8 / T6): the view's camera record of the scene manifest;
    a record with ``aerial_allowed`` (the one true aerial view, the site view) is told to the critic
    (``prompts.camera_note``): a true aerial is allowed by the policy and is not a finding. Fix round after P3: the
    prompt states the built roof (``roof_note``) and a roof-type claim is dropped when the built type is the drawn
    one (``drop_roof_type_claims``). Fix round after P4b: ``scene`` (the round's scene manifest) gives the camera's
    measured eye height (``camera_eye``); the prompt states the camera's role and its eye height
    (``prompts.camera_note``) and the X6 claims the code contradicts are dropped (``drop_camera_claims``). Pass
    before P5: the eye height is measured on ``building``'s site (``ground_z``, the scene's terrain only without one)
    and the role is ``camera_role`` (an agent view square to the main facade is the frontal view)."""
    prep = None
    if isinstance(camera, dict) and camera.get("position") and isinstance(building, dict):
        from wenart.blender import exterior_checks as X
        prep = X._prep(building)                 # one plan for the ground and the main facade of this view
    eye = camera_eye(camera, scene, building, prep)
    role = camera_role(camera, main_facade_of(scene, building, prep), building=building, prep=prep) \
        if isinstance(camera, dict) else None                    # fix round after P6a: the frame is measured too
    images, labels = [preview], [f"render of exterior view {view}"]
    if plan_crop is not None:
        images.append(plan_crop)
        labels.append("crop of the source drawing")
    # Milestone 13 (bug B5): the storeys, not len(levels): a level variant (L-1b) is no storey of its own
    levels = storeys_of(building)
    note = f"The building has {levels} storey(s); {roof_note(building)}"
    note = " ".join(part for part in (note, P.camera_note(camera, eye, role=role)) if part)
    ids = exterior_ids(building, view)
    ext_code = [f for f in code.get("findings") or [] if f.get("check", "").startswith("X") or f.get("target") == view]
    prompt = P.exterior_critic_prompt(view, note, sorted(ids)[:60], labels, ext_code)
    messages = [{"role": "system", "content": P.CRITIC_SYSTEM},
                user_message(prompt, images, [f"Image {i + 1}: {lab}" for i, lab in enumerate(labels)])]
    reply = model.critic(messages, EXTERIOR_SCHEMA, call_id=call_id)
    if reply.data is None:
        return {"kept": [], "dropped": [], "error": "; ".join(reply.errors[:3]) or "no answer", "images": images}
    kept, dropped = screen(reply.data, ids, len(images), code, None, call_id=call_id)
    kept, dropped = drop_roof_type_claims(kept, dropped, building)
    kept, dropped = drop_camera_claims(kept, dropped, view, camera, eye, code, role=role,  # after P4b, P5 pass
                                       building=building, prep=prep)
    return {"kept": kept, "dropped": dropped, "error": None, "images": images}


# --------------------------------------------------------------------------
# 26 Oct 2026 (user: "reviewing the 3d model itself could be better solution rather than individual renders"): the
# model's floors from above, every room at once
# --------------------------------------------------------------------------

MODEL_VIEW_CHECKS = ("Q3", "Q4", "Q5", "Q6", "D3", "F9")
MODEL_VIEW_SCHEMA = answer_schema(MODEL_VIEW_CHECKS)


def model_view_ids(building: dict, level_id: str) -> tuple[set, list[dict]]:
    """The ids a finding on a level's top-down view may target: its rooms, their built pieces and its openings."""
    rooms = [r for r in building.get("rooms") or [] if r.get("level_id") == level_id and r.get("id")]
    rids = {r["id"] for r in rooms}
    ids = set(rids)
    ids |= {f.get("id") for f in building.get("furniture") or [] if f.get("room_id") in rids and TD.is_built(f)}
    ids |= {o.get("id") for o in building.get("openings") or [] if o.get("level_id") == level_id}
    return {i for i in ids if i}, rooms


def critique_model_view(model, building: dict, level_id: str, *, image: Path, code: dict, call_id: str) -> dict:
    """One level of the model seen from above (``renders/top_<level>_plan.jpg``: angled, ceilings off, walls cut at
    0.6 m, rooms named): the visitor checks a whole floor shows (rooms that make no sense, pieces that repeat or
    clash, pieces with their back to the room or before a window or door, a stair void with no guard) on every room
    of the level, also the ones no camera frames. Findings target a room (or a piece) and are screened like the
    room critic's."""
    ids, rooms = model_view_ids(building, level_id)
    pieces = {}
    for f in building.get("furniture") or []:
        if f.get("room_id") in {r["id"] for r in rooms} and TD.is_built(f):
            pieces.setdefault(f["room_id"], []).append(f"{f.get('id')} {f.get('type')}")
    room_lines = [f"- {r['id']} ({r.get('label') or r.get('name') or ''}, type {r.get('room_type')}): "
                  + (", ".join(pieces.get(r["id"], [])[:14]) or "no furniture") for r in rooms]
    known = [f"- {f['check']} {f['severity']} {f['target']}: {f['message']}" for f in code.get("findings") or []
             if f.get("room_id") in {r["id"] for r in rooms} and f.get("severity") in ("critical", "major")][:30]
    prompt = "\n".join([
        f"Image 1 is the 3D model of level {level_id} seen from above at an angle: the ceilings are off and the walls "
        "are cut at 0.6 m, so every room and every piece of furniture shows; each room carries its name, the windows "
        "are blue lines with their ids.",
        "", "Rooms (use these ids as target; a piece id when one piece is the problem):", *room_lines,
        "", "Checklist:", P.checklist_text(MODEL_VIEW_CHECKS),
        "", "Problems the code already measured (do not repeat them):", *(known or ["- none"]),
        "", P.VISITOR_TEXT, P.SEVERITY_TEXT,
        "List what is wrong on this floor of the model. evidence_image = 1."])
    messages = [{"role": "system", "content": P.CRITIC_SYSTEM},
                user_message(prompt, [image], [f"Image 1: the model of level {level_id} from above"])]
    reply = model.critic(messages, MODEL_VIEW_SCHEMA, call_id=call_id)
    if reply.data is None:
        return {"kept": [], "dropped": [], "error": "; ".join(reply.errors[:3]) or "no answer", "images": [image]}
    kept, dropped = screen(reply.data, ids, 1, code, None, call_id=call_id)
    room_of = {f.get("id"): f.get("room_id") for f in building.get("furniture") or []}
    for f in kept + dropped:
        if not f.get("room_id"):
            f["room_id"] = f.get("target") if f.get("target") in {r["id"] for r in rooms} else room_of.get(f.get("target"))
        if not isinstance(f.get("evidence"), dict):
            f["evidence"] = {}
        f["evidence"]["model_view"] = level_id
    return {"kept": kept, "dropped": dropped, "error": None, "images": [image]}
