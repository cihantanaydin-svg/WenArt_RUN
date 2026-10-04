"""Render one lit cube with Cycles on the GPU. Run inside Blender:
blender -b --python scripts/blender_smoke.py -- /path/out.png
Prints 'DEVICE=<OPTIX|CUDA|CPU>' so the test can check the GPU was used."""
import sys
import bpy

out = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, 0))
bpy.ops.object.light_add(type="SUN", location=(4, -4, 8))
bpy.context.object.data.energy = 4
bpy.ops.object.camera_add(location=(6, -6, 4.5), rotation=(1.1, 0, 0.785))
scene.camera = bpy.context.object

scene.render.engine = "CYCLES"
scene.cycles.samples = 64
scene.render.resolution_x = scene.render.resolution_y = 512
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = out

prefs = bpy.context.preferences.addons["cycles"].preferences
device = "CPU"
for dev_type in ("OPTIX", "CUDA"):
    try:
        prefs.compute_device_type = dev_type
        prefs.get_devices()
        gpus = [d for d in prefs.devices if d.type == dev_type]
        if gpus:
            for d in prefs.devices:
                d.use = d.type == dev_type
            scene.cycles.device = "GPU"
            device = dev_type
            break
    except Exception as exc:  # noqa: BLE001
        print(f"{dev_type} not usable: {exc}")
print(f"DEVICE={device}")
bpy.ops.render.render(write_still=True)
print(f"RENDERED={out}")
