#!/usr/bin/env bash
# verify_delivery.sh - check the finished render and the repo before calling the job done.
# Writes docs/RENDER_REPORT.md so the result survives a shutdown.
cd "$(dirname "$0")/.."
BIN="${BLENDER:-$HOME/.local/opt/blender/blender}"
REPORT=docs/RENDER_REPORT.md
FAIL=0
mkdir -p docs
{
echo "# Render verification report"
echo
echo "Generated $(date '+%Y-%m-%d %H:%M:%S %Z') by \`scripts/verify_delivery.sh\`."
echo
echo '## Video'
echo
} > "$REPORT"

chk() { # chk <label> <condition-result> <detail>
  if [ "$2" = "0" ]; then echo "| $1 | PASS | $3 |" >> "$REPORT"
  else echo "| $1 | **FAIL** | $3 |" >> "$REPORT"; FAIL=1; fi
}

echo '| Check | Result | Detail |' >> "$REPORT"
echo '|---|---|---|' >> "$REPORT"

MP4=renders/ghost.mp4
[ -f "$MP4" ]; chk "mp4 exists" $? "$MP4"
if [ -f "$MP4" ]; then
  SZ=$(stat -c %s "$MP4")
  [ "$SZ" -gt 500000 ]; chk "mp4 size sane" $? "$(numfmt --to=iec $SZ)"
  DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$MP4")
  NBF=$(ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -of csv=p=0 "$MP4" 2>/dev/null)
  FPS=$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 "$MP4")
  RES=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0:s=x "$MP4")
  ACODEC=$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of csv=p=0 "$MP4")
  [ "$NBF" = "336" ]; chk "frame count = 336" $? "got $NBF"
  [ "$FPS" = "24/1" ]; chk "frame rate = 24" $? "got $FPS"
  [ "$RES" = "1920x1080" ]; chk "resolution 1080p" $? "got $RES"
  [ -n "$ACODEC" ]; chk "audio track present" $? "codec ${ACODEC:-none}"
  awk -v d="$DUR" 'BEGIN{exit !(d>13.5 && d<14.5)}'; chk "duration ~14 s" $? "${DUR}s"
fi

# every PNG present and non-empty
N=$(ls renders/frames/frame_*.png 2>/dev/null | wc -l)
[ "$N" = "336" ]; chk "PNG sequence complete" $? "$N/336 files"
EMPTY=$(find renders/frames -name 'frame_*.png' -size 0 2>/dev/null | wc -l)
[ "$EMPTY" = "0" ]; chk "no zero-byte frames" $? "$EMPTY empty"

# no all-black frames: sample 12 across the film
BLACK=0
for f in $(ls renders/frames/frame_*.png 2>/dev/null | awk 'NR%28==1'); do
  M=$(ffmpeg -v error -i "$f" -vf "scale=80:45,signalstats,metadata=print:key=lavfi.signalstats.YAVG" -f null - 2>&1 | grep -oE '[0-9.]+$' | head -1)
  [ -z "$M" ] && M=$(python3 -c "
from PIL import Image;px=list(Image.open('$f').convert('L').resize((80,45)).getdata());print(sum(px)/len(px))" 2>/dev/null)
  awk -v m="${M:-0}" 'BEGIN{exit !(m<2)}' && BLACK=$((BLACK+1))
done
[ "$BLACK" = "0" ]; chk "no black frames in sample" $? "$BLACK of 12 samples near-black"

{
echo
echo '## Repository'
echo
echo '| Check | Result | Detail |'
echo '|---|---|---|'
} >> "$REPORT"
for f in Ghost.blend README.md ASSETS.md .gitignore .gitattributes \
         scripts/bake_cloth.py scripts/make_audio.sh scripts/render.sh \
         scripts/verify_delivery.sh assets/audio/ghost_bed.flac \
         docs/images/hero.jpg renders/ghost.mp4; do
  [ -s "$f" ]; chk "$f" $? "$([ -f "$f" ] && numfmt --to=iec $(stat -c %s "$f") || echo missing)"
done

# the .blend must open with zero missing external files
MISS=$("$BIN" -b Ghost.blend --factory-startup --python-expr \
  'import bpy;m=[i.filepath for i in bpy.data.images if i.source=="FILE" and not i.has_data]+[s.filepath for s in bpy.data.sounds if not s.packed_file];print("MISSINGCOUNT",len(m))' \
  2>/dev/null | grep MISSINGCOUNT | awk '{print $2}')
[ "$MISS" = "0" ]; chk "blend has no missing files" $? "${MISS:-?} missing"

{
echo
echo '## Summary'
echo
if [ "$FAIL" = "0" ]; then echo 'All checks passed.'; else echo '**One or more checks failed. See the tables above.**'; fi
echo
echo 'Nothing in this repository has been committed or pushed. The working tree holds all'
echo 'new work; run `git status` to review before committing.'
} >> "$REPORT"

cat "$REPORT"
exit $FAIL
