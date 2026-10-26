"""Argus, the render line: what the final renders show against what the building plans (26 Oct 2026, user:
"everything needs to be judged").

What (the final vision check's record, ``check/check_manifest.json``, every view and every element):

- K1 a required element of the building (a drawn door, window, fixture or piece the view must show) that the check
  model saw ``absent`` in half or more of the views that should show it (major), or in some of them (minor);
- K2 an element the check model saw as something else (``different``) in a view that must show it;
- K3 a drawn piece the drawn check (``drawn_check``) finds away from its drawn place, size or front beyond the
  check's tolerance;
- K4 an elevation the check could not compare with the model (``not_checked``), and views marked for review.

Why: the renders are what the client sees; an element the building holds and no render shows is lost to the client
as surely as one the build dropped.
"""
from __future__ import annotations

from typing import Optional

from wenart.audit import kinds as K

MAJOR_SHARE = 0.5           # K1: absent in at least this share of the views that must show it is major


def audit(check: Optional[dict]) -> dict:
    if not isinstance(check, dict):
        return {"findings": [], "checked": {}, "note": "no check_manifest.json (the final check did not run)"}
    need: dict = {}
    absent: dict = {}
    different: dict = {}
    info: dict = {}
    for view, v in (check.get("views") or {}).items():
        if not isinstance(v, dict):
            continue
        status: dict = {}                   # one status per element and view (a view may have several passes)
        for _pass, rec in v.items():
            if not isinstance(rec, dict) or not isinstance(rec.get("elements"), dict):
                continue
            for eid, e in rec["elements"].items():
                if e.get("role") != "required":
                    continue
                info.setdefault(eid, e)
                seen = ((e.get("passes") or {}).get("agent") or {}).get("seen_as")
                st = e.get("single")
                if st == "different" and str(seen or "") == str(e.get("type") or ""):
                    st = "present"          # seen as its own type: the same thing (a style difference at most)
                prev = status.get(eid)
                if prev is None or (prev != "present" and st == "present"):  # present in any pass wins
                    status[eid] = (st, seen) if st == "different" else st
        for eid, st in status.items():
            need[eid] = need.get(eid, 0) + 1
            if st == "absent":
                absent.setdefault(eid, []).append(view)
            elif isinstance(st, tuple):
                different.setdefault(eid, []).append(f"{view} (seen as {st[1]})")
    out = []
    for eid, views in absent.items():
        e = info[eid]
        share = len(views) / max(1, need[eid])
        out.append(K.finding("render", "K1", "major" if share >= MAJOR_SHARE else "minor", eid,
                             f"{e.get('type')} {eid} ({e.get('source')}) is not seen in {len(views)} of the {need[eid]} "
                             f"view(s) that must show it: {', '.join(views[:6])}", owner="render", kind="lost",
                             evidence={"views": views, "required_in": need[eid]}))
    for eid, views in different.items():
        e = info[eid]
        out.append(K.finding("render", "K2", "minor", eid, f"{e.get('type')} {eid} looks like something else in "
                             f"{len(views)} view(s): {', '.join(views[:4])}", owner="fit", kind="misread",
                             evidence={"views": views}))
    dc = check.get("drawn_check") or {}
    tol = dc.get("tolerance_m")
    for p in dc.get("pieces") or []:
        if p.get("checked") and p.get("ok") is False:
            why = [f"{float(p['anchor_distance_m']):.2f} m from its drawn place" if p.get("anchor_distance_m") else None,
                   f"turned {p['front_turn_deg']:.0f} deg" if p.get("front_turn_deg") else None,
                   f"size {p.get('size')} vs drawn {p.get('drawn_size')}" if p.get("size") != p.get("drawn_size") else None]
            why = [w for w in why if w] + list(p.get("notes") or [])
            out.append(K.finding("render", "K3", "minor", p.get("id"),
                                 f"{p.get('type')} {p.get('id')} differs from the drawing (tolerance {tol} m): "
                                 f"{'; '.join(why) or 'see the drawn check'}", owner="layout", kind="misread",
                                 evidence={"modified_by_ai": p.get("modified_by_ai")}))
    facades = (check.get("elevation_check") or {}).get("facades") or []
    nc = [f.get("region_id") for f in facades if f.get("result") == "not_checked"]
    if nc:
        out.append(K.finding("render", "K4", "minor", "elevations",
                             f"{len(nc)} elevation(s) could not be compared with the model ({', '.join(map(str, nc))}): "
                             f"{(facades[0].get('notes') or [''])[0]}", owner="check", kind="process"))
    review = [vn for vn, v in (check.get("views") or {}).items() if isinstance(v, dict) and v.get("needs_review")]
    if review:
        out.append(K.finding("render", "K4", "major", "views", f"{len(review)} view(s) marked for review: "
                             f"{', '.join(review[:8])}", owner="check", kind="process"))
    return {"findings": out, "checked": {"views": len(check.get("views") or {}), "required_elements": len(need),
                                         "drawn_pieces": len(dc.get("pieces") or []), "elevations": len(facades)}}


def run(inp) -> dict:
    """The line for ``report.LINE_MODULES``."""
    return audit(inp.check)
