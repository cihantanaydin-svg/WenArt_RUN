"""Lighting from the style profile (docs/milestone3.md §3, lighting.py).

- World: HDRI from the assets manifest when available, else a physical sky
  (materials.world_nodes); strength from the mood.
- Sun lamp at the style's elevation / azimuth; colour through the lamp's
  blackbody temperature (SunLight.use_temperature / temperature, Blender 5.2),
  strength in W/m2 from ``sun_strength``.
- One soft area light at the ceiling of every room that has no window on its
  edges, recorded as ``assumed`` in the manifest. Rooms with windows get their
  light from the sun and the sky only.

Azimuth is compass degrees clockwise from north (+Y); elevation above the
horizon. Blender lamps shine along their local -Z.
"""
from __future__ import annotations

import math

from wenart import geometry as G
from wenart.blender.cameras import room_openings

# Area light power scales with the floor area (a fixed 120 W washed out a 3 m2 WC).
AREA_LIGHT_W_PER_M2 = 12.0
AREA_LIGHT_MIN_W = 10.0
AREA_LIGHT_MAX_W = 150.0
AREA_LIGHT_MAX_SIZE = 1.5


def sun_direction(elevation_deg: float, azimuth_deg: float) -> tuple[float, float, float]:
    """Unit vector from the scene towards the sun."""
    el, az = math.radians(elevation_deg), math.radians(azimuth_deg)
    return (math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el))


def build_lighting(building: dict, levels: list[dict], style: dict, hdri_path: str | None, collection,
                   manifest_objects: list, assumed: list) -> dict:
    """World + sun + area lights for the windowless rooms of ``levels``."""
    import bpy
    from mathutils import Vector

    from wenart.blender import common
    from wenart.blender.materials import world_nodes

    scene = bpy.context.scene
    lighting = style.get("lighting") or {}
    elevation = float(lighting.get("sun_elevation_deg", 35.0))
    azimuth = float(lighting.get("sun_azimuth_deg", 210.0))
    strength = float(lighting.get("sun_strength", 3.0))
    temperature = float(lighting.get("colour_temperature_k", 5200))

    world = world_nodes(scene, lighting, hdri_path)

    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = strength
    sun.angle = math.radians(0.53)
    try:
        sun.use_temperature = True
        sun.temperature = temperature
    except AttributeError:  # older API: fall back to a plain colour
        sun.color = _blackbody_rgb(temperature)
    ob = bpy.data.objects.new("sun", sun)
    d = Vector(sun_direction(elevation, azimuth))
    ob.location = d * 30.0
    ob.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    collection.objects.link(ob)
    common.set_props(ob, wenart_id="sun", kind="light", status="assumed")
    manifest_objects.append({
        "name": "sun", "wenart_id": "sun", "kind": "light", "status": "assumed", "level_id": None,
        "element_id": None, "evidence": [], "material": None, "textured": False, "pass_index": None,
        "assumed": {"elevation_deg": elevation, "azimuth_deg": azimuth, "strength": strength,
                    "temperature_k": temperature},
    })

    area_lights = []
    for level in levels:
        floor_z = float(level["elevation"])
        ceil_z = floor_z + float(level["ceiling_height"])
        for room in building["rooms"]:
            if room["level_id"] != level["id"]:
                continue
            polygon = [tuple(p[:2]) for p in room["polygon"]]
            windows = [o for o in room_openings(room, polygon, building) if o["type"] == "window"]
            if windows:
                continue
            cx, cy = G.polygon_centroid(polygon)
            x0, y0, x1, y1 = G.bbox(polygon)
            size = min(AREA_LIGHT_MAX_SIZE, max(0.3, min(x1 - x0, y1 - y0) * 0.5))
            power = min(AREA_LIGHT_MAX_W, max(AREA_LIGHT_MIN_W, AREA_LIGHT_W_PER_M2 * G.polygon_area(polygon)))
            light = bpy.data.lights.new(f"light_{room['id']}", "AREA")
            light.shape = "SQUARE"
            light.size = size
            light.energy = power
            try:
                light.use_temperature = True
                light.temperature = temperature
            except AttributeError:
                light.color = _blackbody_rgb(temperature)
            lob = bpy.data.objects.new(f"light_{room['id']}", light)
            lob.location = (cx, cy, ceil_z - 0.05)
            collection.objects.link(lob)
            common.set_props(lob, wenart_id=f"light_{room['id']}", kind="light", status="assumed")
            lob["wenart_room"] = room["id"]
            manifest_objects.append({
                "name": lob.name, "wenart_id": lob.name, "kind": "light", "status": "assumed",
                "level_id": level["id"], "element_id": room["id"], "evidence": [], "material": None,
                "textured": False, "pass_index": None,
                "assumed": {"power_w": power, "size_m": size, "reason": "room has no window"},
            })
            assumed.append({"object": lob.name, "field": "area_light", "value": power,
                            "reason": f"{room['id']} has no window; soft ceiling light added"})
            area_lights.append(lob)
    return {"world": world, "sun": {"elevation_deg": elevation, "azimuth_deg": azimuth, "strength": strength,
                                    "temperature_k": temperature},
            "area_lights": [o.name for o in area_lights]}


def _blackbody_rgb(kelvin: float) -> tuple[float, float, float]:
    """Rough blackbody colour (only used when the lamp has no temperature input)."""
    t = kelvin / 100.0
    r = 1.0 if t <= 66 else min(1.0, 1.2929 * (t - 60) ** -0.1332)
    g = min(1.0, 0.3900 * math.log(t) - 0.6318) if t <= 66 else min(1.0, 1.1299 * (t - 60) ** -0.0755)
    b = 1.0 if t >= 66 else (0.0 if t <= 19 else min(1.0, 0.5432 * math.log(t - 10) - 1.1963))
    return (max(0.0, r), max(0.0, g), max(0.0, b))
