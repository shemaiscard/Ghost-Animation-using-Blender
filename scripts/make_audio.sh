#!/usr/bin/env bash
# make_audio.sh - synthesise the soundtrack from scratch with ffmpeg.
#
# The original repo shipped "Horror Sound Music (mp3cut.net) (1).mp3": an uncredited clip
# from an mp3-cutter site, unpacked (so missing on clone anyway) and distributed under this
# repo's MIT LICENSE. That is a licensing problem with no upside. Everything below is
# generated from oscillators and noise, so the result is original and carries no third-party
# terms at all.
#
# Layers:
#   drone    two detuned sines that beat against each other, plus a fifth above
#   rumble   brown noise, low-passed, the floor of the mix
#   wind     pink noise, band-passed and tremolo'd, the corridor air
#   hits     decaying sub bursts placed on the picture beats
#
# Beat times are (frame - 49) / 24, matching scripts/improve_ghost.py.
set -euo pipefail
OUT="${1:-assets/audio/ghost_bed.flac}"
DUR=14.0
mkdir -p "$(dirname "$OUT")"

hit() {  # hit <delay_ms> <freq> <gain> <decay_s>
  echo "sine=frequency=$2:duration=$4:sample_rate=48000,volume=$3,afade=t=out:st=0:d=$4,adelay=$1|$1"
}

ffmpeg -y -v error \
  -f lavfi -i "sine=frequency=55:duration=$DUR:sample_rate=48000" \
  -f lavfi -i "sine=frequency=55.35:duration=$DUR:sample_rate=48000" \
  -f lavfi -i "sine=frequency=82.5:duration=$DUR:sample_rate=48000" \
  -f lavfi -i "anoisesrc=duration=$DUR:color=brown:amplitude=0.45:sample_rate=48000" \
  -f lavfi -i "anoisesrc=duration=$DUR:color=pink:amplitude=0.55:sample_rate=48000" \
  -filter_complex "
    [0:a]volume=0.30[d1];
    [1:a]volume=0.26[d2];
    [2:a]volume=0.11,tremolo=f=0.13:d=0.55[d3];
    [d1][d2][d3]amix=inputs=3:normalize=0,lowpass=f=320[drone];

    [3:a]lowpass=f=140,volume=0.55[rumble];

    [4:a]bandpass=f=680:w=900,tremolo=f=0.17:d=0.72,volume=0.30[wind];

    $(hit 1460 70  0.55 1.1)[h1];
    $(hit 1790 96  0.30 0.7)[h2];
    $(hit 3380 48  0.85 2.2)[h3];
    $(hit 4580 120 0.34 0.5)[h4];
    $(hit 9580 120 0.34 0.5)[h5];
    $(hit 12460 62 0.45 1.4)[h6];
    $(hit 13200 38 0.95 2.6)[h7];
    [h1][h2][h3][h4][h5][h6][h7]amix=inputs=7:normalize=0[hits];

    [drone][rumble][wind][hits]amix=inputs=4:normalize=0,
      aecho=0.8:0.85:320|610:0.28|0.16,
      highpass=f=28,
      alimiter=limit=0.92,
      afade=t=in:st=0:d=1.2,
      afade=t=out:st=12.4:d=1.6,
      atrim=0:$DUR,
      loudnorm=I=-19:TP=-1.5:LRA=11
  " -ac 2 -ar 48000 "$OUT"

echo "wrote $OUT"
ffprobe -v error -show_entries format=duration,bit_rate -of default=nw=1 "$OUT"
