"""Build FerVois concept sprites from the CC0 Pixel Art Atlas (Angais/pixel-art-atlas-1.4m).

Usage: python art/build_sprites.py <dir with train-000N.parquet shards>
Only shards 0000-0005 are needed (about 170 MB); never download the full dataset.
Shard URL: https://huggingface.co/datasets/Angais/pixel-art-atlas-1.4m/resolve/refs%2Fconvert%2Fparquet/default/train/000N.parquet
Writes art/sprites/*.png (native 16x16), art/x8/*.png (8x nearest-neighbor), art/sprites.json.
Composites are written as *_raw.png then snapped by art/snap.mjs (fast-pixelizer, the mono-pix engine).
"""
import sys, glob, io, json, colorsys, os
import pyarrow.parquet as pq
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
picks = json.load(open(os.path.join(ROOT, "picks.json")))
shards = sorted(glob.glob(os.path.join(sys.argv[1], "train-*.parquet")))

# key = "<subject>#<n>": the n-th sprite (0 based) with that exact subject, scanning shards in order
want = {}
for pid, p in picks.items():
    s, n = p["key"].rsplit("#", 1); want.setdefault(s, {})[int(n)] = pid
seen = {s: 0 for s in want}; got = {}
for f in shards:
    pf = pq.ParquetFile(f); subj = pf.read(columns=["subject"]).to_pydict()["subject"]
    hits = []
    for i, s in enumerate(subj):
        if s in want:
            if seen[s] in want[s]: hits.append((i, want[s][seen[s]]))
            seen[s] += 1
    if hits:
        t = pf.read(columns=["image", "caption", "subject", "row_id"])
        for i, pid in hits:
            got[pid] = dict(row_id=t["row_id"][i].as_py(), subject=t["subject"][i].as_py(),
                            caption=t["caption"][i].as_py(), shard=os.path.basename(f),
                            img=Image.open(io.BytesIO(t["image"][i].as_py()["bytes"])).convert("RGBA"))
    if len(got) == len(picks): break
missing = set(picks) - set(got)
assert not missing, missing

def save(pid, im):
    im.save(f"{ROOT}/sprites/{pid}.png"); im.resize((128, 128), Image.NEAREST).save(f"{ROOT}/x8/{pid}.png")

def recolor(im, fn):
    out = im.copy(); px = out.load()
    for y in range(16):
        for x in range(16):
            r, g, b, a = px[x, y]
            if a: px[x, y] = fn(r, g, b) + (a,)
    return out

def hue(r, g, b, shift, sat=1.0, val=1.0, only=None):
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    if only and not only(h, s, v): return (r, g, b)
    h = (h + shift) % 1; s = min(1, s * sat); v = min(1, v * val)
    return tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v))

def aura(im, color):
    """1 px tier aura: fill transparent cells that touch the sprite."""
    out = im.copy(); src = im.load(); px = out.load()
    for y in range(16):
        for x in range(16):
            if src[x, y][3]: continue
            if any(0 <= x + dx < 16 and 0 <= y + dy < 16 and src[x + dx, y + dy][3] > 0
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                px[x, y] = color
    return out

meta = {}
for pid, p in picks.items():
    g = got[pid]; save(pid, g["img"])
    meta[pid] = dict(name=p["name"], role=p.get("role", ""), source=dict(row_id=g["row_id"], subject=g["subject"],
                     caption=g["caption"], shard=g["shard"]), composite=False)

# Composite 1: T4 "Ascended" look for every class = T3 sprite, warm accent hues rotated to Lumen cyan, plus a 1 px cyan
# tier aura. This is the visual rule for gear past tier 3 (gear never caps, the aura brightens per Ascension band).
for cls, title in [("knight", "Knight T4 Ascended"), ("arcanist", "Arcanist T4 Ascended"),
                   ("tinker", "Tinker T4 Ascended"), ("ranger", "Ranger T4 Ascended")]:
    base = got[f"{cls}_t3"]
    im = recolor(base["img"], lambda r, g, b: hue(r, g, b, 0.5, 1.2, 1.1, only=lambda h, s, v: s > 0.35 and (h < 0.12 or h > 0.9)))
    aura(im, (64, 232, 255, 255)).save(f"{ROOT}/composites/{cls}_t4_raw.png")
    meta[f"{cls}_t4"] = dict(name=title, role="Ascension tier look (tier 4 and up)",
        source=dict(row_id=base["row_id"], subject=base["subject"], caption=base["caption"], shard=base["shard"]),
        composite=True, how=f"Recolor of {cls}_t3: red/orange hues rotated toward cyan, plus 1 px cyan tier aura. Snapped with fast-pixelizer.")
# Composite 2: Cogling Ring 4 elite = orange body to violet, keeps outline
ce = recolor(got["en_cogling"]["img"], lambda r, g, b: hue(r, g, b, 0.72, 1.0, 1.0, only=lambda h, s, v: s > 0.3))
ce = aura(ce, (186, 85, 255, 255))
ce.save(f"{ROOT}/composites/en_cogling_elite_raw.png")
meta["en_cogling_elite"] = dict(name="Cogling, Ring 4 Elite", role="Same enemy, further out: recolor + aura",
    source=dict(row_id=got["en_cogling"]["row_id"], subject="clockwork automaton", caption=got["en_cogling"]["caption"], shard=got["en_cogling"]["shard"]),
    composite=True, how="Hue rotate of en_cogling to violet, plus 1 px violet elite aura. Snapped with fast-pixelizer.")
# Composite 3: Pip awakened (Act 3) = Pip with gold core
pa = recolor(got["npc_pip"]["img"], lambda r, g, b: hue(r, g, b, -0.45, 1.3, 1.05, only=lambda h, s, v: s > 0.3 and 0.45 < h < 0.75))
pa = aura(pa, (255, 196, 64, 255))
pa.save(f"{ROOT}/composites/npc_pip_awake_raw.png")
meta["npc_pip_awake"] = dict(name="Pip, Awakened (Act 3)", role="Pip after the Heart Engine memory returns",
    source=dict(row_id=got["npc_pip"]["row_id"], subject="robot companion", caption=got["npc_pip"]["caption"], shard=got["npc_pip"]["shard"]),
    composite=True, how="Blue accents rotated to gold, plus 1 px gold aura. Snapped with fast-pixelizer.")
json.dump(meta, open(f"{ROOT}/sprites.json", "w"), indent=1)
print(len(meta), "sprites")
