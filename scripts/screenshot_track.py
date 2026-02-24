#!/usr/bin/env python3
"""
Render a top-down screenshot of the track for visual verification.

Run with: blender --background casaluce.blend --python scripts/screenshot_track.py
"""

import os
import sys
import math

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_PATH = os.path.join(ROOT_DIR, "track_preview.png")

try:
    import bpy
    from mathutils import Vector, Euler
except ImportError:
    print("ERROR: Must run inside Blender.")
    sys.exit(1)


def main():
    print("Rendering top-down track preview...")

    # Compute bounding box from all mesh objects
    min_x, max_x = float('inf'), float('-inf')
    min_y, max_y = float('inf'), float('-inf')

    for obj in bpy.data.objects:
        if obj.type == 'MESH' and 'ROAD' in obj.name:
            for v in obj.data.vertices:
                co = obj.matrix_world @ v.co
                min_x = min(min_x, co.x)
                max_x = max(max_x, co.x)
                min_y = min(min_y, co.y)
                max_y = max(max_y, co.y)

    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2
    sx = max_x - min_x
    sy = max_y - min_y
    size = max(sx, sy) * 1.3  # margin

    print(f"  Track bounds: X[{min_x:.0f}, {max_x:.0f}] Y[{min_y:.0f}, {max_y:.0f}]")
    print(f"  Center: ({cx:.0f}, {cy:.0f}), Size: {size:.0f}m")

    # Create orthographic camera
    cam_data = bpy.data.cameras.new("ScreenshotCam")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = size
    cam_obj = bpy.data.objects.new("ScreenshotCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)

    # Position camera above, looking down
    cam_obj.location = (cx, cy, 100)
    cam_obj.rotation_euler = (0, 0, 0)  # top-down

    bpy.context.scene.camera = cam_obj

    # Render settings
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.scene.render.resolution_x = 1024
    bpy.context.scene.render.resolution_y = 768
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = OUTPUT_PATH
    bpy.context.scene.render.film_transparent = True

    # Add a sun light for visibility
    light_data = bpy.data.lights.new("Sun", type='SUN')
    light_data.energy = 3.0
    light_obj = bpy.data.objects.new("Sun", light_data)
    light_obj.location = (0, 0, 50)
    light_obj.rotation_euler = (math.radians(30), 0, math.radians(30))
    bpy.context.collection.objects.link(light_obj)

    # Render
    print(f"  Rendering to {OUTPUT_PATH}...")
    bpy.ops.render.render(write_still=True)

    # Cleanup temp objects
    bpy.data.objects.remove(cam_obj)
    bpy.data.objects.remove(light_obj)

    print(f"  Done! Preview saved to track_preview.png")


if __name__ == "__main__":
    main()
