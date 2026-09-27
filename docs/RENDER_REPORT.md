# Render verification report

Generated 2026-09-27 02:32:11 EDT by `scripts/verify_delivery.sh`.

## Video

| Check | Result | Detail |
|---|---|---|
| mp4 exists | PASS | renders/ghost_v2.mp4 |
| mp4 size sane | PASS | 6.1M |
| frame count = 336 | PASS | got 336 |
| frame rate = 24 | PASS | got 24/1 |
| resolution 1080p | PASS | got 1920x1080 |
| audio track present | PASS | codec aac |
| duration ~14 s | PASS | 14.000000s |
| PNG sequence complete | PASS | 336/336 files |
| no zero-byte frames | PASS | 0 empty |
| no black frames in sample | PASS | 0 of 12 samples near-black |

## Repository

| Check | Result | Detail |
|---|---|---|
| Ghost_v2.blend | PASS | 546K |
| README.md | PASS | 6.1K |
| ASSETS.md | PASS | 2.3K |
| .gitignore | PASS | 591 |
| .gitattributes | PASS | 1.3K |
| docs/BREAKDOWN.md | PASS | 8.9K |
| scripts/improve_ghost.py | PASS | 34K |
| scripts/bake_cloth.py | PASS | 2.3K |
| scripts/make_audio.sh | PASS | 2.5K |
| scripts/render.sh | PASS | 2.4K |
| assets/audio/ghost_bed.flac | PASS | 692K |
| blend has no missing files | PASS | 0 missing |

## Summary

All checks passed.

Nothing in this repository has been committed or pushed. The working tree holds all
new work; run `git status` to review before committing.

## Visual confirmation

A 4x3 contact sheet sampled every 28 frames was reviewed before shutdown. All three shots
read as intended: SH01 the crane with the ghost rising from a draped mound, SH02 the low
angle with the figure advancing toward the lens, SH03 the wide as the corridor empties.
The ghost holds its silhouette across the whole film rather than shrinking to a speck, which
was the original's main failure. Audio track muxed and present.

Machine powered off immediately after this report was written.
