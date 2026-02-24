#!/usr/bin/env python3
"""Debug wall positions to find overlaps with the track."""
import sys
try:
    import bpy
except ImportError:
    sys.exit(1)

# Get road bounds
road = bpy.data.objects.get("1ROAD")
road_verts = [(road.matrix_world @ v.co) for v in road.data.vertices]

# Check wall segments 30-38
for name in ["1WALL_SUB30", "1WALL_SUB31", "1WALL_SUB32", "1WALL_SUB33", "1WALL_SUB34", "1WALL_SUB35", "1WALL_SUB36", "1WALL_SUB37", "1WALL_SUB38"]:
    obj = bpy.data.objects.get(name)
    if obj:
        verts = [(obj.matrix_world @ v.co) for v in obj.data.vertices]
        xs = [v.x for v in verts]
        ys = [v.y for v in verts]
        print(f"{name}: X[{min(xs):.1f}, {max(xs):.1f}] Y[{min(ys):.1f}, {max(ys):.1f}]")

# Also check 2WALL around the same area
for name in ["2WALL_SUB30", "2WALL_SUB31", "2WALL_SUB32", "2WALL_SUB33", "2WALL_SUB34", "2WALL_SUB35"]:
    obj = bpy.data.objects.get(name)
    if obj:
        verts = [(obj.matrix_world @ v.co) for v in obj.data.vertices]
        xs = [v.x for v in verts]
        ys = [v.y for v in verts]
        print(f"{name}: X[{min(xs):.1f}, {max(xs):.1f}] Y[{min(ys):.1f}, {max(ys):.1f}]")

# Find the crossing area - where centerline points are closest to each other
import json, os, math
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, "centerline.json")) as f:
    pts = json.load(f)

n = len(pts)
print(f"\nCenterline: {n} points")
print("\nClosest point pairs (distance < 20m, not neighbors):")
for i in range(n):
    for j in range(i+5, n):
        if abs(j - i) < 5 or abs(j - i) > n - 5:
            continue
        dx = pts[i][0] - pts[j][0]
        dy = pts[i][1] - pts[j][1]
        d = math.sqrt(dx*dx + dy*dy)
        if d < 20:
            print(f"  CP {i} ({pts[i][0]:.1f}, {pts[i][1]:.1f}) <-> CP {j} ({pts[j][0]:.1f}, {pts[j][1]:.1f}) = {d:.1f}m")
