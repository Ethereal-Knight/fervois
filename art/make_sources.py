"""Write art/SOURCES.md from art/sprites.json."""
import json, os
R = os.path.dirname(os.path.abspath(__file__)); m = json.load(open(os.path.join(R, "sprites.json")))
L = ["# Art sources", "",
     "All NPC and enemy sprites, and the design references for the hero, come from the **Pixel Art Atlas 1.4M** by Angais, https://huggingface.co/datasets/Angais/pixel-art-atlas-1.4m, license **CC0-1.0** (public domain dedication, no attribution required; credited here anyway).", "",
     "- `originals-16/` native 16 x 16 PNGs exactly as pulled from the atlas (kept for provenance), `x8/` 8x nearest-neighbor copies.",
     "- `x64/` native 64 x 64 sprites used in game for NPCs and enemies. Each is derived from the 16 x 16 original of the same id (atlas row in the table) by `upscale64.py`: Scale4x (EPX twice), 1 px outline rebuild tinted toward the fill, interior line thinning, then material shading (highlight, shadow, dither, metal glint) with clamped hue shifts. Not a nearest-neighbor upscale; no AI generation.",
     "- `doll/` the 64 x 64 paper-doll hero: base body plus equipment layers, hand-authored as material masks in code (`doll/doll.py`), FerVois original work, no atlas pixels. Class tier looks are layer loadouts plus palettes; the atlas sprite listed for each tier (ref16) was the design reference for silhouette and colors only. See docs/systems/paper-doll.md.",
     "- Composites (recolor + 1 px aura) are marked below. They were snapped with fast-pixelizer (MIT, engine of mono-pix) by `snap.mjs`.",
     "- `fx/` frames rendered from pixelfx (MIT, https://github.com/patch-gg/pixelfx) by `fx/render_fx.mjs`.",
     "- `buildings/` rendered by parametric-topdown-pixel-architecture (MIT code, https://github.com/Zengkailin/parametric-topdown-pixel-architecture). Its style atlases may contain third-party art: placeholders only until cleared.", "",
     "| id | FerVois name | atlas row_id | subject | caption | shard | composite | 64x64 |", "|---|---|---|---|---|---|---|---|"]
HERO = {"hero_base"} | {f"{c}_t{t}" for c in ("knight", "arcanist", "tinker", "ranger") for t in (1, 2, 3, 4)}
def X64(k):
    if k in HERO: return f"in game: paper doll ({'doll/layers/body/base_*.png' if k == 'hero_base' else 'doll/tiers/' + k + '_*.png'}); x64/{k}.png kept as a derived reference"
    return f"x64/{k}.png derived from this row by upscale64.py"
for k, v in m.items():
    s = v["source"]; L.append(f"| {k} | {v['name']} | {s['row_id']} | {s['subject']} | {s['caption']} | {s['shard']} | {v.get('how', '') if v['composite'] else 'no'} | {X64(k)} |")
open(os.path.join(R, "SOURCES.md"), "w").write("\n".join(L) + "\n"); print(len(m))
