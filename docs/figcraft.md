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
1. **Cover:** title, pitch, Ascended Knight title portrait at 24x.
2. **Character Sheet:** Lampbearer base at 16x; Knight, Arcanist, Tinker, Ranger at tiers T1 to T3 (atlas sprites) and T4 Ascended (composite); 7 story character cards (Aldric, Pip, Wren, Hester, Odo, Caldus, Pip Awakened); 11 enemies in 4 faction groups including a Ring 4 elite recolor. Every card lists the atlas row_id and subject.
3. **Style Guide:** 10-color palette (also saved as paint styles `FerVois/*`), sprite rules, hero density question, medieval + tech-pop rule, tier and ring rules, no-gore rule, backgrounds, type, and the reference toolkit with used vs referenced status.
4. **FX:** pixelfx renders: laser bolt (Lumen Cyan), sword slash, shield block, disintegrate, coin drop.
5. **World Buildings:** keep, forge, tavern, watchtower and Archwright outpost from parametric-topdown-pixel-architecture.

## Rebuild
```sh
# FigCraft CLI
git clone https://github.com/storytold/figcraft && cd figcraft && cargo build --release -p figcraft-cli
# sprites (needs atlas shards train-0000..0005.parquet in <dir>) and art helpers
python3 -m pip install pyarrow pillow
python3 art/build_sprites.py <dir>
(cd art && npm install && node snap.mjs)
git clone --depth 1 https://github.com/patch-gg/pixelfx /tmp/pixelfx && (cd art && PIXELFX=/tmp/pixelfx node fx/render_fx.mjs)
python3 art/make_sources.py
# design file and exports
python3 figcraft/generate_design.py
figcraft-cli run figcraft/build/script.json
for p in Cover "Character Sheet" "Style Guide" FX "World Buildings"; do figcraft-cli export figcraft/fervois.figcraft -o figcraft/exports/ --scale 1 --page "$p"; done
```
Building renders: `node cli/tb.js render gothic fortress --size 256 --no-aa --outline-silhouette 1 --seed 7 -o art/buildings/keep.png` (and forge, tavern, watchtower, mage_tower) from a clone of parametric-topdown-pixel-architecture.
