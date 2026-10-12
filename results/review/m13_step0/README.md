# Milestone 13, step 0: visual review of the committed final renders (12 Oct 2026)

One reviewer (an AI agent with the images opened one by one) looked at every committed `*_final_preview.jpg` of
real02 (49 files; 41 belong to the run of `final_report.md`, 8 are stale files of an earlier run), real03 (85 files;
83 in the report) and real04 (48). Per view: tags from a fixed list, a one-line note naming the objects, and a score
`client_ready_score` 1-5 (1 = embarrassing, 5 = could show a client). `*_counts.json` holds the tag counts and the
score histogram, computed from the per-view files with a script.

Code versions: real04 = M12 code (pod `jeqodk9uyn9o6p`, 11 Oct 2026, polish off); real02 and real03 = M11 code
(runs 20261010-015217 and 20261010-153706; before the M12 solver and audit). The tags and scores are one reviewer's
judgement, not a measurement; they are kept here so the Milestone 13 before/after uses the same rubric
(`docs/milestone13.md` §1.1 and §7).

Tags: missing_anchor, empty_room, parametric_boxy, grey_box, floating_or_odd_placement, overlap_cut,
blocked_door_window, bare_material, wrong_scale, lollipop_vegetation, flat_outdoor, bad_camera, lighting_bad,
decor_wrong, looks_acceptable (definitions in `docs/milestone13.md` §1.1).
