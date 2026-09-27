# Breakdown: what changed between Ghost.blend and Ghost_v2.blend

Every "before" number here was measured from the original `Ghost.blend`, either through
Blender's Python API or by parsing the file's SDNA blocks directly. Nothing in this document
is an impression.

---

## 1. The film had almost no animation in it

The original contains **6 F-curves and 19 keyframes** for the entire 9-second film.

```
CameraAction  location[0,1,2]      5 keys each at frames 1, 40, 80, 100, 120
SphereAction  location[0]          2 keys: x = -0.299 (f1) -> -50.0 (f100)
SphereAction  rotation_euler[2]    1 key + a Noise modifier (scale 43, strength 1.4)
```

The camera move is the most considered thing in the file: three channels, a real arc,
craning from z 9.1 up to z 18.1 while swinging y out to 4.8 and back. That was kept and
retimed.

The ghost is the problem. Its whole performance is a straight line on one axis, 49.7 units
away from a camera sitting 40 units out. Measured on the render, the subject's bounding box
falls from 1722x852 px to 375x435 px, and mean frame luma falls from 12.8 to 6.6 out of 255
while the proportion of near-black pixels climbs to **91.3%**. The film literally empties out.

**v2:** 18 keyframes on the head across location, rotation and scale, structured as beats:
settle, stir, notice (with a 12-frame dead hold), rise with an overshoot, approach,
hesitate, collapse. Travel cut from 50 units to about 26, and the camera repositioned ahead
of the ghost for shot 2 so it advances toward the lens instead of receding from it.

## 2. The ending was a frozen still

The last keyframe sits at frame 120. The scene runs to 135. Separately, the cloth point
cache also ends at frame 120. So the final 15 frames had neither animation nor simulation.

Measured: frames 125 to 130 differ by a **mean absolute pixel value of 0.01**, and 130 to
134 by 0.17. It is a freeze, not an ending.

**v2:** the film ends on a beat. The head hesitates at frame 348, then drops and scales to
near zero by 384, so the sheet falls empty and settles on the floor. The bob modifier is
restricted to frames 49 to 352 with a 16-frame blend-out so it is not fighting the collapse.

## 3. The corridor was invisible, and not because it was unlit

This was the most surprising finding. Walls, columns and three ground planes are all
modelled, with Array modifiers, and they never show up.

The obvious explanation is the lighting: the scene has exactly **one** light, a point lamp
at RGB (1.0, 0.0075, 0.0022), which is pure saturated red, parented *inside* the ghost. The
world was set to `Background Strength 0.1` pointing at an HDR that does not exist.

But the materials were the bigger problem:

```
Material.002  (grnd1, grnd3, wall 2)   Metallic 1.0,  Base Color (0.038, 0.261, 0.800)
Material.2    (grnd 2, wall 1)         Metallic 1.0,  Base Color (0.000, 0.000, 0.000),  Roughness 0.15
```

Metallic 1.0 means a surface has no diffuse response at all: it only shows what it reflects.
Over a near-black base colour in a corridor with nothing to reflect, it renders black no
matter how much light you add. A lighting rig alone would have returned nothing.

**v2:** Metallic dropped to 0 on both, base colours lifted to stone values, and a fourteen-lamp
rig added (moon key, back rim, ten practicals, bounce fill, plus the original red lamp
retuned from 100 W pure red to 52 W warm ember). The columns had no material at all and now
have one.

## 4. The ground moire was a one-metre bump and a warped vector

The floor reads as a blocky, aliased checker that crawls. Three causes, all in
`Material.002`:

- `Bump.Distance = 1.0`. That is a one-metre displacement on a floor. Now 0.02.
- `Noise Texture.Color -> Brick Texture.Vector`. Warping a brick pattern's coordinates by a
  noise texture is what makes it swim. Link removed.
- `Brick Texture.Color -> Principled.Roughness` directly, which turned the floor into a
  patchwork of mirror and matte. Now routed through a Map Range node clamped to 0.18-0.62.

## 5. The collision setup was fighting itself

All six colliders were at **Cloth Friction 80.0**, the maximum the field allows. Blender's
default is 5.0. That glued the hem of the sheet to the brick floor, so when the head
accelerated away the sheet was torn off it rather than carried along.

There were also **zero vertex groups in the entire file**, so there was no pin group, and
the cloth object was not parented to anything. Nothing attached the sheet to the ghost. The
only thing moving it was the head physically shoving it, at 0.5 units per frame against a
collision band 0.035 units thick, at Quality Steps 5.

**v2:** friction 3.0 on floors and 16.0 on the body, a feathered `PIN` group (1,470
vertices at weights 1.0 / 0.45 / 0.12), the cloth parented to the head, Quality Steps 5 to
12, Collision Quality 3 to 6, and Impulse Clamping enabled at 2.0 where it was disabled.

## 6. The collision proxy was rendering

`Sphere` was correctly set to `hide_render = True`. `Cylinder` was not. It shows up in every
frame of the original as two pale nubs poking out at the hem, which read as teeth. One
checkbox.

## 7. Depth of field at f/0.2

The camera was a 50 mm lens on a **21 mm** sensor, which is not a standard sensor size, with
depth of field enabled at **f/0.2**. Focus tracking was actually set up correctly, with the
Sphere as the focus object, so that part worked. But f/0.2 is a fraction of a stop from
nothing being in focus at all, and it would erase the new corridor entirely.

**v2:** 36 mm sensor with the lens moved to 85 mm, which preserves the original framing
exactly (50/21 and 85/36 are the same angle of view), and f/2.8.

## 8. The file did not open correctly for anyone else

```
image  'fullmoon.hdr'   packed=False  has_data=False  filepath='//../Documents/fullmoon.hdr'
sound  'Horror Sound Music (mp3cut.net) (1).mp3'      packed=False
```

Neither was committed, neither was packed, and the HDR path points outside the project using
Windows separators. A clone opened with no environment lighting and no sound. The old README
worked around this by telling the reader to download their own HDR, which documents a defect
rather than fixing it.

**v2 has no external dependencies at all.** The sky is a procedural Nishita Sky Texture, so
there is no image to find. The audio is generated by `scripts/make_audio.sh`. See
[../ASSETS.md](../ASSETS.md) for the licensing side of this.

## 9. The render was unaffordable, and that drove the engine change

Not a defect in the original so much as a constraint discovered while rebuilding. With the
new lighting rig and volumetrics in place, a single Cycles frame at **half resolution and 48
samples took 537 seconds** on the development machine. That is roughly 50 hours for a
14-second film, on a laptop with no GPU Cycles can use.

The same frame in EEVEE Next takes **5 seconds**. v2 therefore ships with EEVEE Next as the
default engine. All the Cycles settings are still configured in `improve_ghost.py`, so
`--engine CYCLES` switches back for anyone with hardware that justifies it.

One bug surfaced during this: the fog volume's Density was being driven by a ColorRamp whose
output range is 0 to 1, which silently overrode the intended 0.013 default and filled a
95 x 26 x 26 unit box with density up to 1.0. That is an opaque wall. It rendered pure black
and it was most of the 537 seconds. The fix is a Math multiply node between the ramp and the
Density socket, which is now in the script with a comment explaining why.

## 10. Things the original got right

Worth stating, because the list above is one-sided:

- **The cloth resolution.** 102x102, 10,404 vertices. Most first cloth scenes are a 10x10
  plane. The fold quality around frame 30 of the original is genuinely good and could not
  happen at low resolution.
- **The bending model** is set to Angular, not the older Linear default.
- **The camera move** is a three-channel crane with a real arc, not a slide.
- **The Noise F-modifier.** The student reached for the right tool for organic motion. It
  was mis-tuned and on one channel, which is a tuning problem, not a knowledge gap.
- **The ghost shader idea.** Mixing a Translucent BSDF against emission through a Layer
  Weight node is the correct instinct for a ghost. v2 changes `Facing` to `Fresnel` so the
  glow lands on the silhouette rather than pooling in the middle of the sheet, but the
  structure is the original's.
- **Focus tracking** was correctly bound to the Sphere.
- **Adaptive sampling and OpenImageDenoise** were both already enabled.

---

## Known limitations of v2

- Rendered on CPU. There is no GPU path on the development machine, so sample counts are
  chosen for a laptop rather than for maximum quality.
- The corridor set is still simple geometry. Nothing was remodelled; this pass was lighting,
  shading, simulation, animation and post.
- The cloth sim is deterministic given the same Blender version, but cloth solvers do change
  between releases. Pin to 4.2 LTS if you want the exact result in `renders/`.
