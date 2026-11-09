# FerVois: FigCraft design file

Designs are built in [FigCraft](https://getartcraft.com/apps/figcraft) (open source, github.com/storytold/figcraft), never Figma. Same headless approach as Hunt Ring.

## Files
| Path | What |
|---|---|
| `figcraft/fervois.figcraft` | Native FigCraft document (images embedded) |
| `figcraft/manifest.json` | Every frame: page, name, node id, size, exported PNG |
| `figcraft/generate_design.py` | Writes the FigCraft command script that builds the file |
| `figcraft/exports/*.png` | 1x PNG exports (sprites are pre-scaled nearest-neighbor, so 1x is crisp) |

## Pages
1. **Cover:** title, pitch, Ascended Knight paper doll at 6x as the title portrait.
2. **Character Sheet:** all characters at native 64 x 64, shown at 3x and 4x. Lampbearer base body in 4 facings; Knight, Arcanist, Tinker, Ranger at T1 to T4 as paper-doll composites (loadout listed, 16 x 16 atlas reference in the card corner); 8 story characters (Aldric, Pip, Wren, Hester, Odo, Caldus, Liora, Pip Awakened) and 11 enemies in 4 faction groups as whole 64 x 64 sprites derived from atlas rows (row_id and subject on every card).
3. **Style Guide:** 10-color palette (also saved as paint styles `FerVois/*`), sprite rule (characters 64 x 64), world tile decision (32 x 32), paper-doll hero rule, medieval + tech-pop rule, tier and ring rules, no-gore rule, backgrounds, type, and the reference toolkit with used vs referenced status.
4. **Paper doll:** exploded layer stack, draw order per facing, anchor and grid chart, six example combinations (two are palette swaps), gear progression strip, palette swap and Phaser notes, LPC prior art.
5. **FX:** pixelfx renders: laser bolt (Lumen Cyan), sword slash, shield block, disintegrate, coin drop.
6. **World Buildings:** keep, forge, tavern, watchtower and Archwright outpost from parametric-topdown-pixel-architecture.

## Rebuild
```sh
# FigCraft CLI
git clone https://github.com/storytold/figcraft && cd figcraft && cargo build --release -p figcraft-cli
# sprites (needs atlas shards train-0000..0005.parquet in <dir>) and art helpers
python3 -m pip install pyarrow pillow numpy
python3 art/build_sprites.py <dir>
(cd art && npm install && node snap.mjs)
git clone --depth 1 https://github.com/patch-gg/pixelfx /tmp/pixelfx && (cd art && PIXELFX=/tmp/pixelfx node fx/render_fx.mjs)
python3 art/upscale64.py      # 64x64 NPCs and enemies from art/originals-16
python3 art/doll/doll.py      # paper-doll layers, tiers, combos
python3 art/make_sources.py
# design file and exports
python3 figcraft/generate_design.py
figcraft-cli run figcraft/build/script.json
for p in Cover "Character Sheet" "Style Guide" "Paper doll" FX "World Buildings"; do figcraft-cli export figcraft/fervois.figcraft -o figcraft/exports/ --scale 1 --page "$p"; done
```
Building renders: `node cli/tb.js render gothic fortress --size 256 --no-aa --outline-silhouette 1 --seed 7 -o art/buildings/keep.png` (and forge, tavern, watchtower, mage_tower) from a clone of parametric-topdown-pixel-architecture.
