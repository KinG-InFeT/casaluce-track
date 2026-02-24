#!/usr/bin/env python3
"""Find 1WALL_SUB26 position and nearby centerline points."""
import os, sys, json, math
try:
    import bpy
except ImportError:
    sys.exit(1)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Wall position
wall = bpy.data.objects.get("1WALL_SUB26")
if wall:
    verts = [(wall.matrix_world @ v.co) for v in wall.data.vertices]
    xs = [v.x for v in verts]
    ys = [v.y for v in verts]
    cx = (min(xs)+max(xs))/2
    cy = (min(ys)+max(ys))/2
    print(f"1WALL_SUB26: center=({cx:.1f}, {cy:.1f}) X[{min(xs):.1f},{max(xs):.1f}] Y[{min(ys):.1f},{max(ys):.1f}]")

# Load centerline and find nearest CP
with open(os.path.join(ROOT, "centerline.json")) as f:
    pts = json.load(f)

n = len(pts)
print(f"\nCenterline: {n} points")

# Find CP nearest to wall center
best_i = 0
best_d = float('inf')
for i, p in enumerate(pts):
    d = math.sqrt((p[0]-cx)**2 + (p[1]-cy)**2)
    if d < best_d:
        best_d = d
        best_i = i

print(f"Nearest CP to wall: CP {best_i} ({pts[best_i][0]:.1f}, {pts[best_i][1]:.1f}) dist={best_d:.1f}m")

# Show surrounding CPs and their directions
for i in range(best_i-5, best_i+6):
    idx = i % n
    p = pts[idx]
    nxt = pts[(idx+1) % n]
    dx = nxt[0] - p[0]
    dy = nxt[1] - p[1]
    angle = math.degrees(math.atan2(dy, dx))
    marker = " <-- NEAREST" if idx == best_i else ""
    print(f"  CP {idx}: ({p[0]:7.1f}, {p[1]:7.1f}) -> heading {angle:6.1f} deg{marker}")

# Also find interpolated point index (CP * 20)
print(f"\nInterpolated index range: {best_i*20} to {(best_i+1)*20}")
print(f"For empties, use start_idx around CP {best_i} (interp idx ~{best_i*20})")

# Show current empties
print("\nCurrent empties:")
for obj in sorted(bpy.data.objects, key=lambda o: o.name):
    if obj.type == 'EMPTY':
        print(f"  {obj.name}: loc=({obj.location.x:.1f}, {obj.location.y:.1f}, {obj.location.z:.1f})")
