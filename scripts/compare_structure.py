#!/usr/bin/env python3
"""
List all objects in the blend file with their type and properties.
Run with: blender --background <file>.blend --python scripts/compare_structure.py
"""
import sys
try:
    import bpy
except ImportError:
    print("Must run inside Blender.")
    sys.exit(1)

print("=" * 60)
print("BLENDER SCENE STRUCTURE")
print("=" * 60)

meshes = []
empties = []
others = []

for obj in sorted(bpy.data.objects, key=lambda o: o.name):
    if obj.type == 'MESH':
        mat_names = [m.name for m in obj.data.materials] if obj.data.materials else ['(none)']
        verts = len(obj.data.vertices)
        faces = len(obj.data.polygons)
        meshes.append((obj.name, mat_names, verts, faces))
    elif obj.type == 'EMPTY':
        loc = obj.location
        rot = obj.rotation_euler
        empties.append((obj.name, f"loc=({loc.x:.1f},{loc.y:.1f},{loc.z:.1f})", f"rot=({rot.x:.2f},{rot.y:.2f},{rot.z:.2f})"))
    else:
        others.append((obj.name, obj.type))

print(f"\nMESHES ({len(meshes)}):")
print(f"{'Name':<25} {'Material':<20} {'Verts':>6} {'Faces':>6}")
print("-" * 60)
for name, mats, v, f in meshes:
    print(f"{name:<25} {mats[0]:<20} {v:>6} {f:>6}")

print(f"\nEMPTIES ({len(empties)}):")
for name, loc, rot in empties:
    print(f"  {name:<20} {loc}  {rot}")

if others:
    print(f"\nOTHER ({len(others)}):")
    for name, typ in others:
        print(f"  {name:<20} {typ}")

# Summary
print(f"\nSUMMARY:")
road = [m for m in meshes if 'ROAD' in m[0]]
kerbs = [m for m in meshes if 'KERB' in m[0]]
grass = [m for m in meshes if 'GRASS' in m[0]]
walls = [m for m in meshes if 'WALL' in m[0]]
ground = [m for m in meshes if 'GROUND' in m[0]]
print(f"  ROAD:   {len(road)} mesh")
print(f"  KERB:   {len(kerbs)} segments")
print(f"  GRASS:  {len(grass)} strips")
print(f"  WALL:   {len(walls)} segments")
print(f"  GROUND: {len(ground)} tiles")
print(f"  EMPTY:  {len(empties)} (AC markers)")

# Naming convention check
ac_start = [e for e in empties if 'AC_START' in e[0]]
ac_pit = [e for e in empties if 'AC_PIT' in e[0]]
ac_time = [e for e in empties if 'AC_TIME' in e[0]]
print(f"\n  AC_START: {len(ac_start)}")
print(f"  AC_PIT:   {len(ac_pit)}")
print(f"  AC_TIME:  {len(ac_time)}")
