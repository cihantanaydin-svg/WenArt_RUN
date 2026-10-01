"""Shared fixtures and matching helpers for the ingest tests (Milestone 2 §2).

The tolerances come from docs/milestone2.md: walls by centre line within 5 mm
and thickness within 5 mm; openings by type, centre within 10 mm and width
within 10 mm; rooms by label with area within 1 %; furniture by type, centre
within 10 mm, size within 10 mm and rotation within 1 degree.
"""
import json
from pathlib import Path

import pytest

from wenart import building as B
from wenart import geometry as G

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"
SYNTHETIC = ["synthetic-01", "synthetic-02", "synthetic-03"]


def load_truth(name: str) -> dict:
    return B.load(PROJECTS / name / "truth" / "building.json")


def load_pages(name: str) -> list[dict]:
    return json.loads((PROJECTS / name / "truth" / "pages.json").read_text(encoding="utf-8"))["pages"]


@pytest.fixture(scope="session")
def truth():
    return load_truth


@pytest.fixture(scope="session")
def truth_pages():
    return load_pages


# --------------------------------------------------------------------------
# Matching helpers (one truth element per extracted element and vice versa)
# --------------------------------------------------------------------------

def wall_matches(start, end, thickness, wall: dict) -> bool:
    return (G.distance(start, wall["start"]) <= 0.005 and G.distance(end, wall["end"]) <= 0.005
            and abs(thickness - wall["thickness"]) <= 0.005)


def opening_matches(kind, center, width, opening: dict) -> bool:
    return (kind == opening["type"] and G.distance(center, opening["center"]) <= 0.01
            and abs(width - opening["width"]) <= 0.01)


def furniture_matches(ftype, center, size, rotation, piece: dict, check_type: bool = True) -> bool:
    fp = piece["footprint"]
    return ((not check_type or ftype == piece["type"]) and G.distance(center, fp["center"]) <= 0.01
            and abs(size[0] - fp["size"][0]) <= 0.01 and abs(size[1] - fp["size"][1]) <= 0.01
            and G.angle_difference_deg(rotation, fp["rotation_deg"]) <= 1.0)


def room_matches(label, area, room: dict) -> bool:
    return label == room["label"] and abs(area - room["area_computed"]) <= 0.01 * room["area_computed"]


def assert_one_to_one(items, candidates, match_fn, what: str) -> None:
    """Every item matches exactly one candidate and every candidate is used once."""
    assert len(items) == len(candidates), f"{what}: {len(items)} found, {len(candidates)} expected"
    used = set()
    for item in items:
        hits = [j for j, cand in enumerate(candidates) if match_fn(item, cand)]
        assert len(hits) == 1, f"{what}: {item} matches {len(hits)} truth elements"
        assert hits[0] not in used, f"{what}: truth element {candidates[hits[0]]['id']} matched twice"
        used.add(hits[0])
