"""Write art/SOURCES.md from art/sprites.json."""
import json, os
R = os.path.dirname(os.path.abspath(__file__)); m = json.load(open(os.path.join(R, "sprites.json")))
L = ["# Art sources", "",
     "All character sprites come from the **Pixel Art Atlas 1.4M** by Angais, https://huggingface.co/datasets/Angais/pixel-art-atlas-1.4m, license **CC0-1.0** (public domain dedication, no attribution required; credited here anyway).", "",
     "- `sprites/` native 16 x 16 PNGs, `x8/` 8x nearest-neighbor copies.",
     "- Composites (recolor + 1 px aura) are marked below. They were snapped with fast-pixelizer (MIT, engine of mono-pix) by `snap.mjs`.",
     "- `fx/` frames rendered from pixelfx (MIT, https://github.com/patch-gg/pixelfx) by `fx/render_fx.mjs`.",
     "- `buildings/` rendered by parametric-topdown-pixel-architecture (MIT code, https://github.com/Zengkailin/parametric-topdown-pixel-architecture). Its style atlases may contain third-party art: placeholders only until cleared.", "",
     "| id | FerVois name | atlas row_id | subject | caption | shard | composite |", "|---|---|---|---|---|---|---|"]
for k, v in m.items():
    s = v["source"]; L.append(f"| {k} | {v['name']} | {s['row_id']} | {s['subject']} | {s['caption']} | {s['shard']} | {v.get('how', '') if v['composite'] else 'no'} |")
open(os.path.join(R, "SOURCES.md"), "w").write("\n".join(L) + "\n"); print(len(m))
