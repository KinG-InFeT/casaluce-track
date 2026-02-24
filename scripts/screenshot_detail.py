#!/usr/bin/env python3
"""
Render detailed top-down screenshots of the track with curbs highlighted.

Run with: blender --background casaluce.blend --python scripts/screenshot_detail.py
"""

import os
import sys
import math

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

try:
    import bpy
    from mathutils import Vector, Euler
except ImportError:
    print("ERROR: Must run inside Blender.")
    sys.exit(1)


def render_view(name, cx, cy, size, res_x=1920, res_y=1080):
    """Render a top-down view at given position and size."""
    output = os.path.join(ROOT_DIR, f"preview_{name}.png")

    # Create camera
    cam_data = bpy.data.cameras.new(f"Cam_{name}")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = size
    cam_obj = bpy.data.objects.new(f"Cam_{name}", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = (cx, cy, 100)
    cam_obj.rotation_euler = (0, 0, 0)
    bpy.context.scene.camera = cam_obj

    # Render settings
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.scene.render.resolution_x = res_x
    bpy.context.scene.render.resolution_y = res_y
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = output
    bpy.context.scene.render.film_transparent = False

    # White background
    bpy.context.scene.world.use_nodes = True
    bg = bpy.context.scene.world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value = (0.95, 0.95, 0.95, 1.0)
        bg.inputs['Strength'].default_value = 1.0

    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam_obj)
    print(f"  Saved: {output}")


def main():
    print("Rendering detailed track previews...")

    # Add sun light
    light_data = bpy.data.lights.new("Sun", type='SUN')
    light_data.energy = 5.0
    light_obj = bpy.data.objects.new("Sun", light_data)
    light_obj.location = (0, 0, 50)
    light_obj.rotation_euler = (math.radians(45), 0, math.radians(30))
    bpy.context.collection.objects.link(light_obj)

    # Full track overview (high-res)
    render_view("full", 15, 10, 350, 1920, 1080)

    # Detail views of curb areas
    # Left hairpin (CP 9-12)
    render_view("hairpin_left", -115, 15, 60, 1024, 768)

    # Right U-turn (CP 34-39)
    render_view("uturn_right", 145, -25, 70, 1024, 768)

    # Top crossing (CP 52-54)
    render_view("crossing_top", -5, 60, 70, 1024, 768)

    # Inner hairpin (CP 69-71)
    render_view("hairpin_inner", -80, 0, 60, 1024, 768)

    bpy.data.objects.remove(light_obj)
    print("\nAll previews rendered!")


if __name__ == "__main__":
    main()
