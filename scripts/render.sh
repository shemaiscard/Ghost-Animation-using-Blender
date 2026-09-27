#!/usr/bin/env bash
# render.sh - render the PNG sequence and mux it with the generated audio.
#
#   ./scripts/render.sh                  full 336-frame render at 1080p
#   ./scripts/render.sh 49 120           a frame range only
#   SCALE=50 ./scripts/render.sh         half resolution, for a fast look-check
#
# Frames go to renders/v2/ as PNGs rather than straight to mp4. The original project
# rendered directly to video, which means a crash at frame 120 of 135 loses everything;
# with a sequence and --use-extension you just rerun and Blender skips what exists.
set -euo pipefail
cd "$(dirname "$0")/.."

BLEND="${BLEND:-Ghost_v2.blend}"
BIN="${BLENDER:-$HOME/.local/opt/blender/blender}"
SCALE="${SCALE:-100}"
SAMPLES="${SAMPLES:-0}"      # 0 = leave whatever the .blend says
START="${1:-}"
END="${2:-}"

mkdir -p renders/v2
ARGS=(-b "$BLEND" --factory-startup)
[[ -n "$START" ]] && ARGS+=(-s "$START")
[[ -n "$END" ]]   && ARGS+=(-e "$END")

PY=$(mktemp /tmp/ghost_render_XXXX.py)
cat > "$PY" <<EOF
import bpy
sc = bpy.context.scene
sc.render.resolution_percentage = $SCALE
if $SAMPLES:
    if sc.render.engine == 'CYCLES':
        sc.cycles.samples = $SAMPLES
    else:
        sc.eevee.taa_render_samples = $SAMPLES
sc.render.threads_mode = 'AUTO'
smp = sc.cycles.samples if sc.render.engine == 'CYCLES' else sc.eevee.taa_render_samples
print(f"rendering {sc.frame_start}-{sc.frame_end} at "
      f"{sc.render.resolution_x*sc.render.resolution_percentage//100}x"
      f"{sc.render.resolution_y*sc.render.resolution_percentage//100} "
      f"samples={smp} engine={sc.render.engine}")
EOF

time "$BIN" "${ARGS[@]}" -P "$PY" -a
rm -f "$PY"

echo "--- assembling ---"
FPS=$("$BIN" -b "$BLEND" --factory-startup \
      --python-expr 'import bpy;print("FPSVAL",bpy.context.scene.render.fps)' 2>/dev/null \
      | grep FPSVAL | awk '{print $2}')
FIRST=$(ls renders/v2/frame_*.png | head -1 | grep -oE '[0-9]+' | tail -1)

ffmpeg -y -v error \
  -framerate "$FPS" -start_number "$FIRST" -i renders/v2/frame_%04d.png \
  -i assets/audio/ghost_bed.flac \
  -map 0:v -map 1:a -shortest \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  -movflags +faststart \
  renders/ghost_v2.mp4

echo "wrote renders/ghost_v2.mp4"
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames \
        -show_entries format=duration -of default=nw=1 renders/ghost_v2.mp4
