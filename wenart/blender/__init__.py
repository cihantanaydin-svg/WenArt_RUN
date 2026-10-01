"""Blender scene construction and rendering for the building JSON (Milestone 3 §3).

Two kinds of modules live here:

- Pure Python, importable anywhere (no ``bpy``): ``geom2d`` (3D boxes, UV
  projection maths, free-area search), ``cameras`` (camera placement),
  ``proxies`` (heights table and proxy geometry), ``schemas`` (manifest
  schemas), ``cli`` (finds the Blender binary and runs the scripts).
- Run inside Blender (``import bpy`` happens lazily inside functions):
  ``common``, ``shell``, ``materials``, ``lighting``, ``build``, ``render``.

Everything is in metres, Z up. Building X, Y map to Blender X, Y. Every
object carries the custom properties ``wenart_id``, ``wenart_kind`` and
``wenart_status`` so a reviewer can trace it back to the JSON element.
"""
