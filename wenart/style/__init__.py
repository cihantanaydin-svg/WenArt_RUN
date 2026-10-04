"""Style profile from the brief (Milestone 3 section 1): rule-based, no AI.

``profile_from_brief(brief) -> dict`` and ``profiles_from_brief(brief) ->
list[dict]`` build ``style.json``; ``vocabulary`` holds the keyword and asset
tables. CLI: ``python -m wenart.style <project_dir or building.json> --out style.json``.
"""
from wenart.style.profile import (assets_in_profile, default_profile, is_wet_room, load_defaults,  # noqa: F401
                                  material_slugs, profile_from_brief, profile_from_text, profiles_from_brief,
                                  room_surfaces, write_profiles)
