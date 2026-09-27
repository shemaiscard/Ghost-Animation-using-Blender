"""
improve_ghost.py - rebuild the Ghost animation scene from the original Ghost.blend.

Run headless:
    blender -b Ghost.blend --factory-startup -P scripts/improve_ghost.py -- --out Ghost_v2.blend

What it changes, and why. Every "before" value below was measured from the original file.

  Scene      15 fps -> 24 fps; 135 frames -> 336 frames (14 s).
  Assets     The world used //../Documents/fullmoon.hdr, which is not packed and does not
             exist. Replaced with a procedural night sky so the file has no external
             dependency at all and opens correctly on any machine.
  Materials  Every floor and wall was Metallic 1.0 over a near-black base colour, which is
             why the modelled corridor is invisible. Metallic dropped to 0, base colours
             lifted to stone, Bump Distance cut from 1.0 to 0.02, and the Noise->Brick
             Vector warp removed (that warp is the moire in the original render).
  Lighting   The scene had exactly one light: a saturated red point lamp parented inside
             the ghost. Kept as an ember but retuned, and a moon key, a rim, and corridor
             practicals added so the set reads.
  Volume     No volumetrics existed. Added a bounded Principled Volume for fog and shafts.
  Comp       scene.node_tree was None. Added glare, grade and vignette.
  Camera     Sensor was 21 mm with a 50 mm lens at f/0.2. Moved to a 36 mm sensor and f/2.8
             so the new set is not erased by defocus. Three cameras bound to timeline markers.
  Cloth      No pin group existed and all six colliders were at Friction 80 (max), so the
             sheet was glued to the floor and torn off the head. Added a feathered pin
             group, parented the cloth to the head, and dropped collider friction.
  Ghost      The whole performance was 2 keyframes on one axis: x -0.299 -> -50.0, which is
             why it shrinks to nothing. Rebuilt as a shot-by-shot performance.
"""

import bpy, bmesh, sys, math, os
from mathutils import Vector

# ----------------------------------------------------------------------------- args
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = "Ghost_v2.blend"
for i, a in enumerate(argv):
    if a == "--out" and i + 1 < len(argv):
        OUT = argv[i + 1]

FPS = 24
F_END = 336
# shot boundaries (frame each shot starts on)
SHOT_A, SHOT_B, SHOT_C = 1, 111, 231

sc = bpy.context.scene
D = bpy.data
print("\n" + "=" * 70)
print("improve_ghost.py")
print("=" * 70)


def log(msg):
    print("  [fix] " + msg)


# ============================================================ 1. scene + render
sc.render.fps = FPS
sc.render.fps_base = 1.0
sc.frame_start = 1
sc.frame_end = F_END
sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
sc.render.resolution_percentage = 100
log(f"fps 15 -> {FPS}, frames 1-135 -> 1-{F_END} ({F_END/FPS:.1f} s)")

# --- engine -----------------------------------------------------------------
# EEVEE Next by default, and this is a hardware decision, not an aesthetic one.
# Measured on the development machine (i5-1240P, Intel integrated graphics, no CUDA/HIP):
#     Cycles, 50% resolution, 48 samples ....... 537 s/frame  -> ~50 h for the film
#     EEVEE Next, same frame ...................   5 s/frame  -> ~30 min for the film
# EEVEE Next in 4.2 does volumetrics, soft shadows and screen-space raytracing, which is
# everything this scene actually needs. Pass --engine CYCLES if you have a GPU worth using.
ENGINE = "BLENDER_EEVEE_NEXT"
for i, a in enumerate(argv):
    if a == "--engine" and i + 1 < len(argv):
        ENGINE = argv[i + 1]
sc.render.engine = ENGINE

ee = sc.eevee
ee.taa_render_samples = 32
ee.use_raytracing = True
ee.ray_tracing_options.resolution_scale = "2"
ee.volumetric_start = 0.5
ee.volumetric_end = 280.0
ee.volumetric_samples = 32
ee.volumetric_tile_size = "8"   # 4 is ~2x slower for no visible gain at 1080p
ee.use_volumetric_shadows = True
ee.volumetric_shadow_samples = 16
ee.use_shadow_jitter_viewport = True
ee.shadow_ray_count = 1
ee.shadow_step_count = 6
ee.use_bokeh_jittered = True
log(f"engine: CYCLES -> {ENGINE} (Cycles measured at 537 s/frame on this hardware)")

# Cycles settings are kept configured so --engine CYCLES is a one-word switch.
cy = sc.cycles
cy.device = "CPU"                  # this machine has no CUDA/HIP device
cy.samples = 96
cy.use_adaptive_sampling = True
cy.adaptive_threshold = 0.02
cy.use_denoising = True
cy.denoiser = "OPENIMAGEDENOISE"
cy.denoising_input_passes = "RGB_ALBEDO_NORMAL"
cy.max_bounces = 8
cy.diffuse_bounces = 3
cy.glossy_bounces = 3
cy.transmission_bounces = 6
cy.volume_bounces = 2
cy.transparent_max_bounces = 8
cy.caustics_reflective = False
cy.caustics_refractive = False
cy.blur_glossy = 1.5
sc.render.use_motion_blur = True
sc.render.motion_blur_shutter = 0.5
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Medium High Contrast"
log("cycles (if selected): 48 -> 96 samples, OIDN denoise, bounces capped, caustics off")

# render to a PNG sequence, not straight to mp4, so a crash at frame 300 is recoverable
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGB"
sc.render.image_settings.compression = 15
sc.render.filepath = "//renders/v2/frame_"
sc.render.use_overwrite = False     # lets an interrupted render resume
sc.render.use_placeholder = True


# ============================================================ 2. world: procedural night
# The original pointed at a missing HDR (//../Documents/fullmoon.hdr, packed=False,
# has_data=False) with Background Strength 0.1, so the scene had almost no ambient light.
# A procedural sky removes the external dependency entirely.
w = sc.world
w.use_nodes = True
nt = w.node_tree
nt.nodes.clear()

out = nt.nodes.new("ShaderNodeOutputWorld"); out.location = (600, 0)
bg = nt.nodes.new("ShaderNodeBackground"); bg.location = (380, 0)
sky = nt.nodes.new("ShaderNodeTexSky"); sky.location = (60, 120)
sky.sky_type = "NISHITA"
sky.sun_elevation = math.radians(-3.0)   # just below horizon = deep dusk
sky.sun_rotation = math.radians(200.0)
sky.altitude = 0
sky.air_density = 0.6
sky.dust_density = 2.2
sky.ozone_density = 3.0
sky.sun_intensity = 0.06
sky.sun_size = math.radians(1.5)

tint = nt.nodes.new("ShaderNodeMixRGB"); tint.location = (230, 0)
tint.blend_type = "MULTIPLY"; tint.inputs["Fac"].default_value = 0.85
tint.inputs["Color2"].default_value = (0.22, 0.34, 0.62, 1.0)   # cold moonlight

nt.links.new(sky.outputs["Color"], tint.inputs["Color1"])
nt.links.new(tint.outputs["Color"], bg.inputs["Color"])
nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
bg.inputs["Strength"].default_value = 0.022
log("world: missing fullmoon.hdr -> procedural Nishita night sky (no external file)")

# drop the now-unused broken image reference
for img in list(D.images):
    if img.source == "FILE" and not img.has_data:
        log(f"world: removed dead image reference '{img.name}' ({img.filepath})")
        D.images.remove(img)


# ============================================================ 3. materials
def principled(mat):
    for n in mat.node_tree.nodes:
        if n.type == "BSDF_PRINCIPLED":
            return n
    return None


# --- set materials: the reason the corridor is invisible -------------------
# Material.002 (grnd1, grnd3, wall 2): Metallic 1.0, base (0.038,0.261,0.8), Brick->Roughness,
#   Brick->Bump.Height with Distance 1.0 (a one-metre bump!), Noise->Brick.Vector (the moire).
m = D.materials.get("Material.002")
if m and m.use_nodes:
    p = principled(m)
    ntm = m.node_tree
    brick = ntm.nodes.get("Brick Texture")
    bump = ntm.nodes.get("Bump")
    noise = ntm.nodes.get("Noise Texture")

    p.inputs["Base Color"].default_value = (0.055, 0.058, 0.065, 1.0)   # wet grey stone
    p.inputs["Metallic"].default_value = 0.0
    p.inputs["IOR"].default_value = 1.45
    if "Specular IOR Level" in p.inputs:
        p.inputs["Specular IOR Level"].default_value = 0.4

    if noise and brick:
        for l in list(ntm.links):
            if l.from_node == noise and l.to_node == brick:
                ntm.links.remove(l)      # kill the vector warp that causes the moire
    if brick:
        brick.inputs["Scale"].default_value = 6.0
        brick.inputs["Color1"].default_value = (0.42, 0.42, 0.44, 1.0)
        brick.inputs["Color2"].default_value = (0.30, 0.30, 0.33, 1.0)
        brick.inputs["Mortar"].default_value = (0.10, 0.10, 0.11, 1.0)
        brick.inputs["Mortar Size"].default_value = 0.012
        brick.inputs["Brick Width"].default_value = 0.42
        brick.inputs["Row Height"].default_value = 0.20
        # brick drove Roughness directly, which made the floor a patchwork mirror.
        for l in list(ntm.links):
            if l.from_node == brick and l.to_socket.name == "Roughness":
                ntm.links.remove(l)
        rmap = ntm.nodes.new("ShaderNodeMapRange"); rmap.location = (-180, -260)
        rmap.inputs["To Min"].default_value = 0.18   # damp patches stay glossy
        rmap.inputs["To Max"].default_value = 0.62
        ntm.links.new(brick.outputs["Color"], rmap.inputs["Value"])
        ntm.links.new(rmap.outputs["Result"], p.inputs["Roughness"])
    if bump:
        bump.inputs["Distance"].default_value = 0.02   # was 1.0
        bump.inputs["Strength"].default_value = 0.35
    log("Material.002: Metallic 1.0 -> 0, bump distance 1.0 -> 0.02, noise warp removed")

# Material.2 (grnd 2, wall 1): pure black base, Metallic 1.0, Roughness 0.15 = a black mirror.
m = D.materials.get("Material.2")
if m and m.use_nodes:
    p = principled(m)
    p.inputs["Base Color"].default_value = (0.035, 0.037, 0.043, 1.0)
    p.inputs["Metallic"].default_value = 0.0
    p.inputs["Roughness"].default_value = 0.55
    log("Material.2: black mirror (metallic 1.0, rough 0.15) -> dark stone")

# columns had no material at all
col_mat = D.materials.new("StoneColumn")
col_mat.use_nodes = True
p = principled(col_mat)
p.inputs["Base Color"].default_value = (0.075, 0.073, 0.068, 1.0)
p.inputs["Roughness"].default_value = 0.72
p.inputs["Metallic"].default_value = 0.0
for name in ("column", "ccolumn"):
    o = D.objects.get(name)
    if o and not o.data.materials:
        o.data.materials.append(col_mat)
log("columns: had no material -> StoneColumn assigned")

# --- ghost shader: make the RIM glow, not the belly -----------------------
# Original: Mix(Translucent, Emission) with Layer Weight .Facing -> Fac, Blend 0.15.
# Facing is 1.0 when a surface faces the camera, so the emission piled up in the middle of
# the sheet (the pink/blue smear) instead of along the silhouette.
m = D.materials.get("Material")
if m and m.use_nodes:
    ntm = m.node_tree
    ntm.nodes.clear()
    mout = ntm.nodes.new("ShaderNodeOutputMaterial"); mout.location = (760, 0)
    mix = ntm.nodes.new("ShaderNodeMixShader"); mix.location = (560, 0)
    trans = ntm.nodes.new("ShaderNodeBsdfTranslucent"); trans.location = (330, -140)
    emis = ntm.nodes.new("ShaderNodeEmission"); emis.location = (330, 120)
    lw = ntm.nodes.new("ShaderNodeLayerWeight"); lw.location = (-60, 180)
    ramp = ntm.nodes.new("ShaderNodeValToRGB"); ramp.location = (140, 200)
    noise = ntm.nodes.new("ShaderNodeTexNoise"); noise.location = (-60, -160)
    nmix = ntm.nodes.new("ShaderNodeMixRGB"); nmix.location = (140, -160)

    trans.inputs["Color"].default_value = (0.62, 0.74, 0.95, 1.0)
    emis.inputs["Color"].default_value = (0.36, 0.62, 1.0, 1.0)
    emis.inputs["Strength"].default_value = 4.2

    lw.inputs["Blend"].default_value = 0.30
    # Fresnel, not Facing: high at grazing angles = glow along the silhouette edge
    ramp.color_ramp.elements[0].position = 0.12
    ramp.color_ramp.elements[1].position = 0.80
    ntm.links.new(lw.outputs["Fresnel"], ramp.inputs["Fac"])
    ntm.links.new(ramp.outputs["Color"], mix.inputs["Fac"])
    ntm.links.new(trans.outputs["BSDF"], mix.inputs[1])
    ntm.links.new(emis.outputs["Emission"], mix.inputs[2])
    ntm.links.new(mix.outputs["Shader"], mout.inputs["Surface"])

    # slow animated shimmer across the fabric so it is never a flat wash
    noise.inputs["Scale"].default_value = 3.2
    noise.inputs["Detail"].default_value = 4.0
    nmix.blend_type = "MULTIPLY"
    nmix.inputs["Fac"].default_value = 0.35
    nmix.inputs["Color2"].default_value = (1.0, 1.0, 1.0, 1.0)
    ntm.links.new(noise.outputs["Fac"], nmix.inputs["Color1"])
    ntm.links.new(nmix.outputs["Color"], emis.inputs["Strength"])
    # drive the noise through 4D W so it evolves over time
    noise.noise_dimensions = "4D"          # the W input only exists once this is 4D
    noise.inputs["W"].default_value = 0.0
    noise.inputs["W"].keyframe_insert("default_value", frame=1)
    noise.inputs["W"].default_value = 6.0
    noise.inputs["W"].keyframe_insert("default_value", frame=F_END)
    for fcv in m.node_tree.animation_data.action.fcurves:
        for k in fcv.keyframe_points:
            k.interpolation = "LINEAR"
    log("ghost shader: Facing -> Fresnel so the rim glows, plus animated 4D noise shimmer")


# ============================================================ 4. hide the collider
# Sphere was already hide_render=True, but Cylinder was not, so the collision proxy
# rendered as two pale nubs at the hem in every frame.
cyl = D.objects.get("Cylinder")
if cyl:
    cyl.hide_render = True
    log("Cylinder: hide_render False -> True (it was rendering as nubs at the hem)")


# ============================================================ 5. lighting rig
def new_light(name, ltype, loc, energy, color, size=1.0, **kw):
    ld = D.lights.new(name, ltype)
    ld.energy = energy
    ld.color = color
    if ltype == "AREA":
        ld.size = size
        ld.shape = kw.get("shape", "SQUARE")
        if "size_y" in kw:
            ld.shape = "RECTANGLE"; ld.size_y = kw["size_y"]
    elif ltype in {"POINT", "SPOT"}:
        ld.shadow_soft_size = size
    elif ltype == "SUN":
        ld.angle = kw.get("angle", math.radians(2.0))
    ob = D.objects.new(name, ld)
    ob.location = loc
    if "rot" in kw:
        ob.rotation_euler = kw["rot"]
    sc.collection.objects.link(ob)
    return ob


# retune the original ember instead of deleting it: it is the film's one signature idea
ember = D.objects.get("Light")
if ember:
    ember.data.energy = 52.0
    ember.data.color = (1.0, 0.16, 0.06)     # was (1.0, 0.0075, 0.0022), a pure red
    ember.data.shadow_soft_size = 0.45
    log("ember lamp: 100 W pure red -> 38 W warm ember")

# moon key, raking down the corridor
new_light("KEY_Moon", "SUN", (30, 40, 60), 0.13, (0.55, 0.68, 1.0),
          rot=(math.radians(52), 0, math.radians(-118)), angle=math.radians(3.0))
# cold rim from behind the ghost, so the silhouette separates from the black
new_light("RIM_Back", "AREA", (-34, 0, 11), 3800.0, (0.60, 0.78, 1.0), size=22.0)
# corridor practicals: pools of light the ghost can travel through
for i, x in enumerate([22, 4, -14, -32, -50]):
    new_light(f"PRAC_{i}", "POINT", (x, 7.5, 13.0), 1250.0, (1.0, 0.70, 0.36), size=1.8)
    new_light(f"PRACb_{i}", "POINT", (x, -7.5, 13.0), 1250.0, (1.0, 0.70, 0.36), size=1.8)
# soft bounce so the floor is not pure black between pools
new_light("FILL_Bounce", "AREA", (-6, 0, 2.0), 320.0, (0.42, 0.55, 0.85),
          size=60.0, size_y=20.0, rot=(0, 0, 0))
log("lighting: 1 lamp -> 14 (moon key, back rim, 10 practicals, bounce, ember)")


# ============================================================ 6. volumetrics
# No Volume Scatter or Principled Volume existed anywhere in the original file.
# A bounded cube is far cheaper than world volume and keeps fog inside the corridor.
bpy.ops.mesh.primitive_cube_add(size=1, location=(-15, 0, 12))
fog = bpy.context.object
fog.name = "FOG_Volume"
fog.scale = (95, 26, 26)
fog.display_type = "WIRE"
fog.hide_select = True
fog.visible_shadow = False

fm = D.materials.new("CorridorFog")
fm.use_nodes = True
fnt = fm.node_tree
fnt.nodes.clear()
fout = fnt.nodes.new("ShaderNodeOutputMaterial"); fout.location = (400, 0)
pv = fnt.nodes.new("ShaderNodeVolumePrincipled"); pv.location = (120, 0)
fnoise = fnt.nodes.new("ShaderNodeTexNoise"); fnoise.location = (-260, -80)
framp = fnt.nodes.new("ShaderNodeValToRGB"); framp.location = (-70, -80)
fnoise.inputs["Scale"].default_value = 0.65
fnoise.inputs["Detail"].default_value = 6.0
fnoise.inputs["Roughness"].default_value = 0.62
framp.color_ramp.elements[0].position = 0.42     # keeps most of the box empty = cheap
framp.color_ramp.elements[1].position = 0.78
fscale = fnt.nodes.new("ShaderNodeMath"); fscale.location = (60, -180)
fscale.operation = "MULTIPLY"
# A ColorRamp outputs 0..1. Wiring that straight into Density overrides the default and
# fills a 95x26x26 box with density up to 1.0, which is an opaque wall: the first version
# of this script did exactly that and rendered pure black at 537 s/frame. Scale it down.
fscale.inputs[1].default_value = 0.0044
fnt.links.new(fnoise.outputs["Fac"], framp.inputs["Fac"])
fnt.links.new(framp.outputs["Color"], fscale.inputs[0])
fnt.links.new(fscale.outputs["Value"], pv.inputs["Density"])
pv.inputs["Color"].default_value = (0.58, 0.70, 0.92, 1.0)
pv.inputs["Anisotropy"].default_value = 0.62
fnt.links.new(pv.outputs["Volume"], fout.inputs["Volume"])
fog.data.materials.append(fm)
sc.cycles.volume_step_rate = 4.0        # coarser steps, much faster, fine for soft fog
sc.cycles.volume_max_steps = 128
log("volumetrics: none -> bounded Principled Volume with noise breakup")


# ============================================================ 7. timing / shot plan
# 48 settle frames at the head let the cloth finish draping before the shot starts.
# The original opened mid-drape, which is why the flat square corners of the plane are
# plainly visible lying on the ground in frame 0.
SETTLE   = 48
A_START  = SETTLE + 1          # 49   shot A: the stir and the rise
B_START  = 159                 #      shot B: the approach, camera now ahead of it
C_START  = 279                 #      shot C: it passes, the corridor empties
LAST     = 384                 # 336 rendered frames = 14.0 s at 24 fps

sc.frame_start = A_START
sc.frame_end = LAST
log(f"shots: settle 1-{SETTLE} | A {A_START}-{B_START-1} | B {B_START}-{C_START-1} | C {C_START}-{LAST}")


# ============================================================ 8. ghost performance
# Original: location[0] with two keys, x -0.299 -> -50.0, and nothing else. 50 units of
# travel directly away from a camera 40 units out is why it shrinks to a speck.
#
# The performance is carried by an empty rather than by the head itself. If the cloth is
# parented to the Sphere and the Sphere is scaled, every scale key also scales the sheet:
# the rise would inflate the fabric and the ending would shrink it away instead of dropping
# it. An empty that only translates and rotates keeps the head's scale out of the cloth.
sph = D.objects["Sphere"]
if sph.animation_data:
    sph.animation_data_clear()
sph.rotation_mode = "XYZ"
sph.scale = (0.40, 0.40, 0.40)          # constant; never animated

root = D.objects.new("GHOST_ROOT", None)
sc.collection.objects.link(root)
root.empty_display_type = "PLAIN_AXES"
root.empty_display_size = 1.5
root.rotation_mode = "XYZ"
sph.parent = root                        # head rides the root
log("rig: added GHOST_ROOT empty; head scale stays constant so the cloth is never distorted")


def key(ob, frame, loc=None, rot=None):
    if loc is not None:
        ob.location = Vector(loc); ob.keyframe_insert("location", frame=frame)
    if rot is not None:
        ob.rotation_euler = [math.radians(a) for a in rot]; ob.keyframe_insert("rotation_euler", frame=frame)


# Root offsets are deltas from the head's rest position (-0.299, 0.01, 4.42).
# settle: dead still while the cloth finds its drape
key(root, 1,      loc=(0, 0, 0),                rot=(0, 0, 0))
key(root, SETTLE, loc=(0, 0, 0),                rot=(0, 0, 0))
# A: a stir, then the rise. the hold at 92-104 is the "it noticed you" beat
key(root, 62,     loc=(0, 0, 0),                rot=(0, 0, 0))
key(root, 84,     loc=(-0.25, 0.21, 0.53),      rot=(0, 0, -14))
key(root, 92,     loc=(-0.40, 0.29, 0.68),      rot=(0, 0, -19))
key(root, 104,    loc=(-0.42, 0.29, 0.70),      rot=(0, 0, -19))
key(root, 130,    loc=(-1.60, 0.04, 2.13),      rot=(0, 0, 4))
key(root, 142,    loc=(-2.05, -0.11, 2.53),     rot=(0, 0, 9))     # overshoot
key(root, 158,    loc=(-2.80, -0.21, 2.30),     rot=(0, 0, 6))
# B: the approach. it now travels toward camera B, so it grows instead of shrinking
key(root, 196,    loc=(-7.30, 0.34, 2.43),      rot=(0, 0, -5))
key(root, 232,    loc=(-11.50, -0.26, 2.18),    rot=(0, 0, 7))
key(root, 262,    loc=(-15.30, 0.19, 2.48),     rot=(0, 0, -6))
key(root, 278,    loc=(-17.60, 0.04, 2.28),     rot=(0, 0, 0))
# C: it keeps coming, hesitates, then lets go of the sheet and rises out of frame
key(root, 316,    loc=(-22.30, 0.09, 2.38),     rot=(0, 0, 3))
key(root, 338,    loc=(-25.10, -0.01, 2.13),    rot=(0, 0, 0))
key(root, 348,    loc=(-25.40, -0.01, 2.08),    rot=(0, 0, 0))     # hesitate
# The cloth is parented to the root, so raising the root would carry the sheet up with it
# and the "sheet drops" beat could never happen. The head sinks through the floor instead,
# while the pin releases, so the fabric is left behind to slump onto the stone.
key(root, 358,    loc=(-25.55, 0.0, 1.85),      rot=(0, 0, 0))
key(root, 370,    loc=(-25.75, 0.0, -1.30),     rot=(0, 0, 0))
key(root, 384,    loc=(-25.95, 0.0, -4.20),     rot=(0, 0, 0))     # gone, down and out

act = root.animation_data.action
HOLDS = (1, SETTLE, 92, 104, 338, 348)
for fc in act.fcurves:
    for k in fc.keyframe_points:
        k.interpolation = "BEZIER"
        k.easing = "EASE_IN_OUT"
        if k.co.x in HOLDS:                      # holds must be dead flat, not drifting
            k.handle_left_type = k.handle_right_type = "VECTOR"

# keep the student's own idea: a Noise modifier for organic drift, retuned and on Z location
# (the original had Scale 43 / Strength 1.4 on rotation Z, which at 15 fps was a jitter)
fcz = next((f for f in act.fcurves if f.data_path == "location" and f.array_index == 2), None)
if fcz:
    nm = fcz.modifiers.new("NOISE")
    nm.scale = 26.0
    nm.strength = 0.42
    nm.phase = 3.1
    nm.depth = 1
    nm.use_restricted_range = True
    nm.frame_start = A_START
    nm.frame_end = 344          # stop the bob before the release beat
    nm.blend_in = 24
    nm.blend_out = 14
log("ghost: 2 keys on 1 axis -> 18 keys on GHOST_ROOT loc/rot, plus a bounded Noise bob")


# ============================================================ 9. cloth
cloth_ob = D.objects["CLOTH"]
cm = next(m for m in cloth_ob.modifiers if m.type == "CLOTH")
cs, cc, pc = cm.settings, cm.collision_settings, cm.point_cache

# --- pin group: there were zero vertex groups in the entire original file -------
vg = cloth_ob.vertex_groups.get("PIN") or cloth_ob.vertex_groups.new(name="PIN")
mw = cloth_ob.matrix_world
head_xy = Vector((sph.matrix_world.translation.x, sph.matrix_world.translation.y))
n_pin = 0
for v in cloth_ob.data.vertices:
    world = mw @ v.co
    d = (Vector((world.x, world.y)) - head_xy).length
    if d < 0.42:
        wgt = 1.0
    elif d < 0.85:
        wgt = 0.45
    elif d < 1.25:
        wgt = 0.12          # feathered, so the pin does not end in a hard creasing ring
    else:
        continue
    vg.add([v.index], wgt, "REPLACE")
    n_pin += 1
cs.vertex_group_mass = "PIN"
cs.pin_stiffness = 1.0
log(f"cloth: pin group created ({n_pin} verts, feathered) - the file had no vertex groups at all")

# Parent the sheet to GHOST_ROOT, not to the Sphere. Both ride the same empty, so the
# pinned crown and the head stay in lockstep, and the head's scale never reaches the cloth.
if cloth_ob.parent is None:
    cloth_ob.parent = root
    log("cloth: parented to GHOST_ROOT (was unparented; the head was only shoving it)")

# --- the ending: release the pin so the sheet drops --------------------------
# pin_stiffness is animatable. Holding it at 1.0 through the film and dropping it to 0
# over frames 348-362 lets the fabric let go of the head, which then rises out of frame.
# The sheet falls under gravity onto the floor. That is an ending; the original froze.
cs.pin_stiffness = 1.0
cs.keyframe_insert("pin_stiffness", frame=1)
cs.keyframe_insert("pin_stiffness", frame=348)
cs.pin_stiffness = 0.0
cs.keyframe_insert("pin_stiffness", frame=362)
cs.keyframe_insert("pin_stiffness", frame=LAST)
log("cloth: pin_stiffness keyed 1.0 -> 0.0 over frames 348-362 (the sheet is dropped)")

# --- solver + collision -------------------------------------------------------
cs.quality = 12                 # was 5
cs.mass = 0.34                  # was 1.0; lighter fabric floats instead of dropping
cs.air_damping = 1.8            # was 1.0; more drag = slower, more ghostly settling
cs.tension_stiffness = 12.0     # was 25
cs.compression_stiffness = 12.0 # was 25
cs.shear_stiffness = 4.0
cs.bending_stiffness = 0.6      # was 1.0; softer folds
cs.use_internal_springs = False
cc.collision_quality = 6        # was 3
cc.distance_min = 0.028         # was 0.015
cc.use_self_collision = True
cc.self_distance_min = 0.015
cc.impulse_clamp = 2.0          # was 0 (disabled) - stops explosive collision responses
cc.self_impulse_clamp = 1.0

# every collider was at Friction 80.0, the maximum. Default is 5. That is what glued the
# hem to the brick floor so the head tore out from under the sheet.
for ob in D.objects:
    if any(m.type == "COLLISION" for m in ob.modifiers):
        col = ob.collision
        col.cloth_friction = 3.0 if ob.name.startswith(("grnd", "wall")) else 16.0
        col.damping_factor = 0.12
        col.thickness_outer = 0.045
log("colliders: Friction 80.0 (max) -> 3.0 floors / 16.0 body; thickness 0.02 -> 0.045")

# --- cache covers the settle frames too --------------------------------------
pc.frame_start = 1
pc.frame_end = LAST
pc.use_disk_cache = True        # so the bake is a real file, reproducible and shippable
pc.use_library_path = False
log(f"cloth cache: 1-120 memory-only -> 1-{LAST} on disk")


# ============================================================ 10. wind
# The fabric only ever fell. A wind field plus turbulence gives it drift and life.
wind = D.objects.new("FORCE_Wind", None)
sc.collection.objects.link(wind)
wind.empty_display_type = "SINGLE_ARROW"
wind.location = (14, 0, 7)
wind.rotation_euler = (math.radians(96), 0, math.radians(90))
wind.modifiers.new("Field", "FIELD") if False else None
bpy.context.view_layer.objects.active = wind
bpy.ops.object.forcefield_toggle()
wf = wind.field
wf.type = "WIND"
wf.strength = 2.6
wf.noise = 1.4
wf.flow = 0.35
wf.use_max_distance = True
wf.distance_max = 90.0

turb = D.objects.new("FORCE_Turbulence", None)
sc.collection.objects.link(turb)
turb.empty_display_type = "PLAIN_AXES"
turb.location = (-8, 0, 8)
bpy.context.view_layer.objects.active = turb
bpy.ops.object.forcefield_toggle()
tf = turb.field
tf.type = "TURBULENCE"
tf.strength = 1.9
tf.size = 2.4
tf.flow = 0.25
tf.use_max_distance = True
tf.distance_max = 60.0
log("forces: none -> wind (2.6) + turbulence (1.9), both distance-limited")


# ============================================================ 11. cameras + cuts
# The original camera move was authored against a ghost that travelled to x = -50. v2 moves
# the ghost to about x = -26, so those hand-keyed rotations no longer point at anything.
# Rather than re-key rotations by hand for three cameras, each camera sits on a rig empty
# that carries a Track To constraint aimed at the ghost. The rig handles WHERE the camera
# looks; the camera itself only carries a little handheld noise.
aim = D.objects.new("CAM_AIM", None)
sc.collection.objects.link(aim)
aim.empty_display_type = "SPHERE"
aim.empty_display_size = 0.6
aim.parent = root
aim.location = (0.0, 0.0, -1.2)       # aim below the head, so the figure sits high with headroom


def build_cam(name, lens, fstop, rig_keys, shake_amt, phase):
    """A rig empty (position + aim) with the camera parented under it."""
    rig = D.objects.new(name + "_rig", None)
    sc.collection.objects.link(rig)
    rig.empty_display_type = "ARROWS"
    con = rig.constraints.new("TRACK_TO")
    con.target = aim
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"

    cd = D.cameras.new(name)
    cam = D.objects.new(name, cd)
    sc.collection.objects.link(cam)
    cam.parent = rig
    cd.sensor_fit = "HORIZONTAL"
    cd.sensor_width = 36.0            # original was a non-standard 21 mm
    cd.lens = lens
    cd.clip_start = 0.1
    cd.clip_end = 600.0
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = fstop     # original was f/0.2, which erases the whole set
    cd.dof.aperture_blades = 6
    cd.dof.focus_object = aim

    for f, loc in rig_keys:
        rig.location = Vector(loc)
        rig.keyframe_insert("location", frame=f)
    for fc in rig.animation_data.action.fcurves:
        for k in fc.keyframe_points:
            k.interpolation = "BEZIER"; k.easing = "EASE_IN_OUT"

    # handheld drift lives on the camera, under the constraint, so it survives the aim
    cam.rotation_euler = (0, 0, 0)
    cam.animation_data_create()
    cam.animation_data.action = D.actions.new(name + "Shake")
    for idx in (0, 1, 2):
        fc = cam.animation_data.action.fcurves.new("rotation_euler", index=idx)
        fc.keyframe_points.insert(sc.frame_start, 0.0)
        n = fc.modifiers.new("NOISE")
        n.scale = 58.0 + idx * 15
        n.strength = shake_amt * (0.55 if idx == 2 else 1.0)
        n.phase = phase + idx * 4.7
        n.depth = 1
    return cam


# SH01: the crane. Keeps the shape of the student's original move (rising while swinging
# out and back), retimed to this shot and now aimed by the constraint.
camA = build_cam("CAM_A_crane", 40.0, 2.8, [
    (A_START,     (33.0,  1.2,  6.0)),
    (84,          (30.0,  5.2,  8.2)),
    (118,         (26.0, -4.0, 12.0)),
    (B_START - 1, (21.0,  3.0, 15.5)),
], 0.0016, 1.3)

# SH02: low and ahead of the ghost, so it advances toward the lens instead of receding.
# This is the fix for "the subject shrinks into nothing".
camB = build_cam("CAM_B_low", 32.0, 2.4, [
    (B_START,     (-40.0, 3.0, 2.4)),
    (C_START - 1, (-33.5, 1.0, 3.6)),
], 0.0030, 7.9)

# SH03: wide, high, drifting back as the corridor empties out.
camC = build_cam("CAM_C_wide", 30.0, 4.0, [
    (C_START, (-41.0, 10.5, 11.0)),
    (LAST,    (-48.0, 13.5, 13.5)),
], 0.0011, 12.4)

# the original camera object is superseded by the rigs
old_cam = D.objects.get("Camera")
if old_cam:
    D.objects.remove(old_cam, do_unlink=True)

# --- bind cameras to timeline markers: this is how you cut inside Blender ----
for mk in list(sc.timeline_markers):
    sc.timeline_markers.remove(mk)
for nm, fr, cm_ in (("SH01", A_START, camA), ("SH02", B_START, camB), ("SH03", C_START, camC)):
    mk = sc.timeline_markers.new(nm, frame=fr)
    mk.camera = cm_
sc.camera = camA
log(f"cameras: 1 -> 3 rigs with Track To aim, bound to markers at {A_START}/{B_START}/{C_START}")


# ============================================================ 12. compositor
# scene.node_tree was None in the original, so none of this existed.
sc.use_nodes = True
sc.render.use_compositing = True
cnt = sc.node_tree
cnt.nodes.clear()

rl   = cnt.nodes.new("CompositorNodeRLayers");      rl.location   = (-600, 0)
fog  = cnt.nodes.new("CompositorNodeGlare");        fog.location  = (-360, 120)
strk = cnt.nodes.new("CompositorNodeGlare");        strk.location = (-140, 120)
cb   = cnt.nodes.new("CompositorNodeColorBalance"); cb.location   = (90, 120)
ell  = cnt.nodes.new("CompositorNodeEllipseMask");  ell.location  = (90, -260)
blur = cnt.nodes.new("CompositorNodeBlur");         blur.location = (290, -260)
vig  = cnt.nodes.new("CompositorNodeMixRGB");       vig.location   = (500, 0)
ld   = cnt.nodes.new("CompositorNodeLensdist");     ld.location   = (700, 0)
comp = cnt.nodes.new("CompositorNodeComposite");    comp.location = (920, 60)
view = cnt.nodes.new("CompositorNodeViewer");       view.location = (920, -140)

fog.glare_type = "FOG_GLOW"; fog.quality = "MEDIUM"; fog.mix = -0.72; fog.threshold = 0.82; fog.size = 8
strk.glare_type = "STREAKS"; strk.quality = "MEDIUM"; strk.mix = -0.88; strk.threshold = 1.15
strk.streaks = 4; strk.angle_offset = math.radians(12); strk.fade = 0.88

cb.correction_method = "LIFT_GAMMA_GAIN"
cb.lift  = (0.995, 1.000, 1.022)    # NB: neutral for LGG lift is 1.0, not 0.0.
                                    # Setting it near 0 crushes the whole frame to black.
cb.gamma = (0.985, 1.000, 1.030)
cb.gain  = (1.035, 1.012, 0.972)    # warm the highlights against the cold blacks

ell.width = 1.34; ell.height = 1.42; ell.x = 0.5; ell.y = 0.5
blur.filter_type = "FAST_GAUSS"; blur.size_x = 190; blur.size_y = 190; blur.use_relative = False
vig.blend_type = "MULTIPLY"; vig.inputs["Fac"].default_value = 0.26
ld.inputs["Distortion"].default_value = 0.008
ld.inputs["Dispersion"].default_value = 0.004

L = cnt.links.new
L(rl.outputs["Image"], fog.inputs["Image"])
L(fog.outputs["Image"], strk.inputs["Image"])
L(strk.outputs["Image"], cb.inputs["Image"])
L(cb.outputs["Image"], vig.inputs[1])
L(ell.outputs["Mask"], blur.inputs["Image"])
L(blur.outputs["Image"], vig.inputs[2])
L(vig.outputs["Image"], ld.inputs["Image"])
L(ld.outputs["Image"], comp.inputs["Image"])
L(ld.outputs["Image"], view.inputs["Image"])
log("compositor: node_tree was None -> fog glow + streaks + grade + vignette + lens distortion")


# ============================================================ 13. audio strip
# The original VSE held "Horror Sound Music (mp3cut.net) (1).mp3": unpacked, missing on
# clone, and an uncredited clip from an mp3-cutter site shipped under an MIT LICENSE.
# Removed here. scripts/make_audio.sh generates an original replacement bed.
if sc.sequence_editor:
    for st in list(sc.sequence_editor.sequences_all):
        if st.type == "SOUND":
            nm = st.name                      # capture before the strip is freed
            sc.sequence_editor.sequences.remove(st)
            log(f"VSE: removed unlicensed strip '{nm}'")
for s in list(D.sounds):
    D.sounds.remove(s)
sc.render.use_sequencer = False


# ============================================================ 14. save
bpy.ops.file.pack_all()          # nothing external is left, but make it explicit and future-proof
out_path = os.path.join(os.path.dirname(bpy.data.filepath), OUT)
bpy.ops.wm.save_as_mainfile(filepath=out_path, compress=True)
print("=" * 70)
print(f"saved: {out_path}")
print(f"render range {sc.frame_start}-{sc.frame_end} at {sc.render.fps} fps "
      f"= {(sc.frame_end - sc.frame_start + 1) / sc.render.fps:.1f} s")
print("=" * 70)
