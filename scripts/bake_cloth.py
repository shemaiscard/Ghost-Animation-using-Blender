"""
Bake the cloth point cache to disk.

    blender -b Ghost_v2.blend --factory-startup -P scripts/bake_cloth.py -- [--end N]

Two things make a headless cloth bake fail silently, and both bit this project:

1. bpy.ops.ptcache.bake() no-ops in background mode. You have to step the timeline and
   force a depsgraph evaluation per frame instead.
2. The original Ghost.blend shipped with point_cache.is_baked = True but no actual cache
   data (totpoint 0, memory-only). Blender trusts that flag and serves the stale cache
   rather than simulating, so every frame comes back identical. free_bake() clears it.

Cloth is a sequential solver: frames must be visited in order, one at a time. Jumping
from frame 5 to frame 15 does not simulate the ten frames in between, it just holds.
"""
import bpy, sys, time

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
end = None
for i, a in enumerate(argv):
    if a == "--end" and i + 1 < len(argv):
        end = int(argv[i + 1])

sc = bpy.context.scene
ob = bpy.data.objects["CLOTH"]
cm = next(m for m in ob.modifiers if m.type == "CLOTH")
pc = cm.point_cache
pc.use_disk_cache = True
if end:
    pc.frame_end = end

bpy.context.view_layer.objects.active = ob
ob.select_set(True)
with bpy.context.temp_override(point_cache=pc):
    bpy.ops.ptcache.free_bake()          # clear the inherited stale "baked" flag

lo, hi = pc.frame_start, pc.frame_end
print(f"baking cloth {lo}-{hi}  quality={cm.settings.quality} "
      f"coll_q={cm.collision_settings.collision_quality} verts={len(ob.data.vertices)}", flush=True)

t0 = time.time()
for f in range(lo, hi + 1):              # strictly sequential
    sc.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()                    # forces the modifier stack to actually evaluate
    if f % 24 == 0 or f == hi:
        zs = [v.co.z for v in me.vertices]
        el, done = time.time() - t0, f - lo + 1
        print(f"  f{f:4d}/{hi}  {el:6.1f}s  {el/done:5.2f}s/f  "
              f"eta {(hi-f)*el/done/60:5.1f}min  z {min(zs):6.2f}/{max(zs):6.2f}", flush=True)
    ev.to_mesh_clear()

dt = time.time() - t0
print(f"BAKE DONE {dt/60:.1f} min for {hi-lo+1} frames = {dt/(hi-lo+1):.2f}s/frame", flush=True)
bpy.ops.wm.save_mainfile()
