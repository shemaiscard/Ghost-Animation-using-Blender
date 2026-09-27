# Assets and licensing

The MIT licence in [LICENSE](LICENSE) covers the **code**: the Python and shell scripts under
`scripts/`. Art assets are listed separately below, because MIT is a software licence and
applying it blanket-style to a `.blend`, a render and an audio file is not meaningful.

## What ships here

| Asset | Origin | Licence |
|---|---|---|
| `Ghost.blend` | Authored by Shema Nkindi Giscard | CC BY 4.0 |
| `assets/audio/ghost_bed.flac` | Synthesised by `scripts/make_audio.sh` | CC0 1.0 |
| `renders/ghost.mp4` | Render of `Ghost.blend` | CC BY 4.0 |
| `docs/images/*.jpg` | Stills from `renders/ghost.mp4` | CC BY 4.0 |
| `scripts/*` | This repository | MIT |

**There are no third-party art assets in this repository**, and that is deliberate.

**No environment texture.** A scene like this would normally load an HDR for its sky and
ambient light, which means shipping someone else's image file, packing it into the `.blend`,
and carrying its licence. This scene builds its night sky from a procedural Nishita Sky
Texture instead. Nothing to download, nothing to relink, nothing to attribute.

**No stock audio.** The soundtrack is generated from oscillators and filtered noise by
`scripts/make_audio.sh`. Every layer is synthesised: detuned sine drones, brown noise, band
passed pink noise, and decaying sub bursts on the picture beats. Because it is generated
rather than sampled, it carries no third-party terms at all. Re-run the script and you get
the same bed.

This matters more than it might seem. Horror and ambient beds are the easiest thing in a
student project to pull from a free-download site, and clips from those sites frequently
arrive with no author, no source and no stated licence, which makes them impossible to
redistribute honestly under any repository licence.

## Reusing this work

The scripts are MIT, so take them. For the scene and the render, CC BY 4.0 means you may
share and adapt them, including commercially, as long as you credit:

> Ghost Animation Using Cloth Physics, Shema Nkindi Giscard, Kyungdong University, 2026.
