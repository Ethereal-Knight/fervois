"""Generate the FerVois FigCraft design file (character designs, style guide, FX, world buildings).

Same approach as Ethereal-Knight/hunt-ring: this script writes a FigCraft command script, figcraft-cli runs it.
  python3 art/build_sprites.py <parquet dir> && node art/snap.mjs && PIXELFX=/tmp/pixelfx node art/fx/render_fx.mjs
  python3 figcraft/generate_design.py
  figcraft-cli run figcraft/build/script.json
  figcraft-cli export figcraft/fervois.figcraft -o figcraft/exports/ --scale 1
Sprites are pre-scaled with nearest-neighbor (figcraft/build/px/) and placed 1:1, so exports stay crisp.
"""
import json, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
ART = os.path.join(REPO, "art"); PX = os.path.join(HERE, "build", "px"); os.makedirs(PX, exist_ok=True)
META = json.load(open(os.path.join(ART, "sprites.json")))
FXM = json.load(open(os.path.join(ART, "fx", "fx.json")))

S = []; n = [0]; manifest = []
def step(cmd, params, name=None):
    d = {"command": cmd, "params": params}
    if name: d["as"] = name
    S.append(d); return name
def ref(r): return {"$ref": r}
def uid(p="n"): n[0] += 1; return f"{p}{n[0]}"

# FerVois palette
NIGHT = "#12161F"; PANEL = "#1C2230"; LINE = "#2C3446"; PARCH = "#E9DFC7"; MUTED = "#8E97AB"
STEEL = "#9AA4B5"; GOLD = "#F2B33D"; CYAN = "#40E8FF"; ROSE = "#F2789B"; MOSS = "#6E9A45"; SPARK = "#FF7A2E"; VIOLET = "#BA55FF"
DISP = "Cinzel"; BODY = "Inter"

def rect(p, x, y, w, h, fill, r=0, stroke=None, sw=0, name="Rect", op=None):
    props = {"fill": fill, "cornerRadius": r}
    if stroke: props.update(stroke=stroke, strokeWeight=sw)
    if op is not None: props["opacity"] = op
    i = uid(); step("node.create", {"type": "rectangle", "parent": ref(p), "x": x, "y": y, "width": w, "height": h, "name": name, "props": props}, i); return i
def text(p, x, y, s, size=16, color=PARCH, style="Regular", fam=BODY, w=None, align="left", name=None, ls=None):
    props = {"fontSize": size, "fill": color, "fontFamily": fam, "fontStyle": style, "textAlign": align}
    if ls: props["letterSpacing"] = ls
    if w: props.update(width=w, textAutoResize="height")
    i = uid(); step("node.create", {"type": "text", "parent": ref(p), "x": x, "y": y, "text": s, "name": name or s[:28], "props": props}, i); return i
def img(p, x, y, path, w, h, name):
    i = uid(); step("image.place", {"path": path, "x": x, "y": y, "width": w, "height": h, "parent": ref(p), "mode": "fit"}, i)
    step("object.rename", {"ids": [ref(i)], "name": name}); return i
def px(pid, k):
    """nearest-neighbor copy of a 16x16 sprite at k x."""
    out = os.path.join(PX, f"{pid}_x{k}.png")
    Image.open(os.path.join(ART, "sprites", pid + ".png")).convert("RGBA").resize((16 * k, 16 * k), Image.NEAREST).save(out)
    return out
def sprite(p, x, y, pid, k=8, card=True, label=True, w=None):
    m = META[pid]; s = 16 * k; w = w or max(s + 24, 190)
    if card: rect(p, x, y, w, s + 24 + (86 if label else 0), PANEL, 10, LINE, 1, name="Card " + m["name"])
    img(p, x + (w - s) / 2, y + 12, px(pid, k), s, s, "Sprite " + pid)
    if label:
        src = m["source"]; tag = "COMPOSITE: " if m["composite"] else ""
        text(p, x + 10, y + s + 30, m["name"], 14, GOLD if m["composite"] else PARCH, "Bold", w=w - 20)
        if m.get("role"): text(p, x + 10, y + s + 52, m["role"], 11, MUTED, w=w - 20)
        text(p, x + 10, y + s + 84, f"{tag}atlas row {src['row_id']} \"{src['subject']}\"", 10, CYAN if not m["composite"] else ROSE, w=w - 20)
    return w
def frame(page, name, x, y, w, h, fill=NIGHT):
    i = uid("F"); params = {"x": x, "y": y, "width": w, "height": h, "name": name, "props": {"fill": fill, "clip": True}}
    if page: params["parent"] = ref(page)
    step("frame.create", params, i); manifest.append((page or "Cover", name, i)); return i
def page(name): i = uid("P"); step("page.add", {"name": name}, i); return i

def heading(f, x, y, title, sub=None):
    text(f, x, y, title, 44, PARCH, "Bold", fam=DISP, ls=2)
    if sub: text(f, x, y + 62, sub, 16, MUTED, w=1500)

CLASSES = [("knight", "KNIGHT", "Sword, shield, plate. Bulwark / Vanguard / Lumen Oath."),
           ("arcanist", "ARCANIST", "Staff and runes. Ember / Frost / Starloom."),
           ("tinker", "TINKER", "Guns, turrets, gadgets. Gunsmith / Engineer / Lancer."),
           ("ranger", "RANGER", "Bow, traps, beasts. Marksman / Trapper / Beastbond.")]
TIERS = ["T1 Common start", "T2 mid game", "T3 late game", "T4+ Ascended (composite)"]
NPCS = ["npc_aldric", "npc_pip", "npc_wren", "npc_hester", "npc_odo", "npc_caldus", "npc_pip_awake"]
FACTIONS = [("ROGUE AUTOMATONS", "Old Archwright machines running broken orders. Defeat: sparks and a pixel burst.", CYAN, ["en_cogling", "en_scrapjaw", "en_turret", "en_cogling_elite"]),
            ("BLOOMTOUCHED BEASTS", "Animals overgrown by the Rust Bloom. Defeat: petals and spores drift off, the animal is freed.", ROSE, ["en_tusk", "en_fang", "en_mossback"]),
            ("CROWFEATHER BANDITS", "Desperate outlaw clans. Defeat: they drop and flee in a smoke poof.", SPARK, ["en_cutpurse", "en_gunner"]),
            ("IRON CHOIR + CAVE GUARDIANS", "A rival order and the dungeon wardens they woke. Defeat: disintegrate into light.", VIOLET, ["en_choir", "en_geode"])]

def classes_block(f, x0, y0):
    text(f, x0, y0, "PLAYER HERO AND SPECIALIZATIONS", 20, GOLD, "Bold", ls=2)
    sprite(f, x0, y0 + 40, "hero_base", 16, w=300)
    text(f, x0, y0 + 460, "Every class starts from this Lampbearer base. Skin, hair, voice and starting trinket are picked at creation; class look comes from gear.", 13, MUTED, w=300)
    gx = x0 + 340
    for t, tl in enumerate(TIERS): text(f, gx + 180 + t * 210, y0 + 40, tl, 13, CYAN if t == 3 else MUTED, "Semi Bold")
    for r, (cid, cname, blurb) in enumerate(CLASSES):
        y = y0 + 70 + r * 250
        text(f, gx, y + 60, cname, 24, PARCH, "Bold", fam=DISP); text(f, gx, y + 96, blurb, 12, MUTED, w=160)
        for t in range(4): sprite(f, gx + 180 + t * 210, y, f"{cid}_t{t+1}", 8, w=190)
    return 70 + 4 * 250

def npc_block(f, x0, y0):
    text(f, x0, y0, "STORY CHARACTERS", 20, GOLD, "Bold", ls=2)
    for k, pid in enumerate(NPCS): sprite(f, x0 + k * 210, y0 + 40, pid, 8, w=190)
    return 40 + 238

def enemy_block(f, x0, y0):
    text(f, x0, y0, "ENEMY FACTIONS (NO DEMONS, NO BLOOD)", 20, GOLD, "Bold", ls=2)
    x = x0; y = y0 + 40
    for fi, (name, desc, col, ids) in enumerate(FACTIONS):
        if fi == 2: x = x0; y += 72 + 250
        w = len(ids) * 210 - 20
        rect(f, x, y, w, 4, col, 2, name="Faction bar")
        text(f, x, y + 12, name, 15, col, "Bold", ls=1); text(f, x, y + 34, desc, 11, MUTED, w=w)
        for k, pid in enumerate(ids): sprite(f, x + k * 210, y + 72, pid, 8, w=190)
        x += w + 40
    return 40 + 2 * (72 + 250)

# ---------- pages
step("page.rename", {"name": "Cover"})
cov = frame(None, "Cover", 0, 0, 1440, 900)
rect(cov, 0, 0, 1440, 900, "#FFFFFF", op=0.03, name="White wash (Paginated Bear lesson)")
img(cov, 920, 230, px("knight_t4", 24), 384, 384, "Title portrait knight_t4")
text(cov, 96, 230, "FERVOIS", 132, PARCH, "Bold", fam=DISP, ls=6)
text(cov, 100, 400, "Explore an overworld that draws itself as you walk. Clear caves and keeps of rogue machines and bloom-touched beasts. Loot, craft and climb with no level cap. Knights carry swords, shields and the odd laser rifle.", 22, MUTED, w=700)
text(cov, 100, 600, "Concept package v0.1  |  Ethereal Knight  |  Nov 2026", 16, GOLD, "Semi Bold")
text(cov, 100, 630, "Art: CC0 Pixel Art Atlas 1.4M (Angais) + FerVois composites", 14, CYAN)

P_cs = page("Character Sheet")
cs = frame(P_cs, "Character Sheet", 0, 0, 1600, 2300)
heading(cs, 60, 40, "FERVOIS CHARACTER SHEET", "Initial character designs. 16x16 sprites from the CC0 Pixel Art Atlas at 8x and 16x, nearest-neighbor. Gold names are FerVois composites (recolor + tier aura, snapped with fast-pixelizer).")
h = classes_block(cs, 60, 150)
h2 = npc_block(cs, 60, 150 + h + 40)
enemy_block(cs, 60, 150 + h + 40 + h2 + 40)

P_sg = page("Style Guide")
sg = frame(P_sg, "Style Guide", 0, 0, 1800, 1500)
heading(sg, 60, 40, "STYLE GUIDE", "Medieval first. Tech is a pop, not the base: one tech accent per sprite at most, always in Lumen Cyan.")
pal = [("Night", NIGHT), ("Panel", PANEL), ("Parchment", PARCH), ("Steel", STEEL), ("Ember Gold", GOLD), ("Lumen Cyan", CYAN), ("Bloom Rose", ROSE), ("Moss", MOSS), ("Spark Orange", SPARK), ("Elite Violet", VIOLET)]
for k, (nm, c) in enumerate(pal):
    x = 60 + k * 168; rect(sg, x, 150, 150, 90, c, 12, LINE, 1, name="Swatch " + nm); text(sg, x, 250, nm, 14, PARCH, "Semi Bold"); text(sg, x, 270, c, 12, MUTED)
for nm, c in pal: step("style.create", {"type": "paint", "name": "FerVois/" + nm, "value": [{"type": "solid", "color": c}]})
rules = [
 ("SPRITES", "Base grid 16x16, 1 px dark outline, no anti-aliasing. Render at integer scale only (camera 4x on a 480x270 base). Atlas sprites are front or three-quarter views."),
 ("HERO DENSITY", "Open question: the Paginated Bear lesson says the player needs 4 facing directions and more pixels (it used 28x32). Proposal: keep 16x16 for enemies and NPCs, redraw the hero at 32x32 with down/up/left/right walk, idle, attack, and keep the 16x16 atlas sprite as the gear-tier reference."),
 ("MEDIEVAL + TECH POP", "Swords, shields, plate, cloth, wood, stone are the base. Lasers, guns, turrets and automatons are Archwright relics: brass and steel bodies, Lumen Cyan glow. Never neon on more than one element per sprite."),
 ("TIERS", "T1 to T3 are different atlas sprites. T4 and up (Ascended) keep the T3 silhouette, rotate warm accents toward cyan and add a 1 px aura. The aura brightens each Ascension band, so infinite gear still reads at a glance."),
 ("ZONE RINGS", "Enemy elites further from Hollowmere recolor by ring: Ring 1-2 natural, Ring 3 Spark Orange trim, Ring 4 Elite Violet aura, Ring 5+ Lumen Cyan aura with a pulsing outline."),
 ("NO GORE", "No blood, no demons, no skulls as decoration. Defeat = sparks, pixel dissolve, petals, smoke poof (pixelfx spawn/disintegrate, spawn/poof, spawn/coin-drop). Sprite Fusion's Blood effect is excluded."),
 ("BACKGROUNDS", "Subtle: low-contrast ground tiles with a light white wash (2-4%) so 16 px characters pop (Paginated Bear lesson). Title screen uses a big pixel portrait."),
 ("TYPE", "Display: Cinzel (titles, logos). UI: Kenney Pixel or Kenney Mini (CC0) in game; Inter for docs. Numbers in damage pop-ups use the pixel font with Ember Gold crits."),
]
y = 330
for t, body in rules:
    text(sg, 60, y, t, 15, GOLD, "Bold", ls=1); text(sg, 300, y, body, 14, PARCH, w=1400); y += 78
text(sg, 60, y + 10, "REFERENCE TOOLKIT  (full notes: docs/references.md)", 15, GOLD, "Bold", ls=1)
refs = [("Pixel Art Atlas 1.4M", "CC0", "USED: every sprite on these pages", CYAN),
        ("mono-pix / fast-pixelizer", "MIT", "USED: snapped all composites to a clean 16 grid", CYAN),
        ("pixelfx", "MIT", "USED: FX page renders (laser, slash, shield, dissolve, coins)", CYAN),
        ("parametric-topdown-pixel-architecture", "MIT code, atlas art unclear", "USED: World Buildings page renders", CYAN),
        ("Sprite Fusion pixel-art VFX", "MIT", "Referenced: origin of pixelfx sim; MCP for agents", MUTED),
        ("Kenney", "CC0", "Referenced: gray-box tiles, UI, fonts, audio for the prototype", MUTED),
        ("CraftPix freebies", "Custom, not CC0, no AI use", "Referenced only. Per-pack check before shipping", SPARK),
        ("awesome-gamedev-agent-skills", "Apache-2.0", "Referenced: procedural-gen, rpg, save-systems, phaser skills", MUTED),
        ("Spawn", "Platform ToS", "Referenced: design inspiration; do not prototype there to ship elsewhere", SPARK),
        ("Paginated Report Bear", "Ours", "Lessons: 4 directions, denser hero, big title portrait, white wash", MUTED)]
for k, (a, lic, use, c) in enumerate(refs):
    yy = y + 46 + k * 30; text(sg, 60, yy, a, 13, PARCH, "Semi Bold"); text(sg, 440, yy, lic, 12, MUTED); text(sg, 720, yy, use, 12, c)

P_fx = page("FX")
fx = frame(P_fx, "FX Samples", 0, 0, 1800, 980)
heading(fx, 60, 40, "FX SAMPLES (pixelfx, MIT)", "Rendered headless from patch-gg/pixelfx with art/fx/render_fx.mjs. Six frames per effect across its duration. Laser recolored to Lumen Cyan.")
y = 150
for e in FXM:
    path = os.path.join(ART, "fx", e["file"]); im = Image.open(path); k = 2 if im.width * 2 <= 1680 else 1
    big = os.path.join(PX, "fx_" + e["file"]); im.resize((im.width * k, im.height * k), Image.NEAREST).save(big)
    text(fx, 60, y, e["label"] + f"   ({e['id']})", 15, GOLD, "Bold"); img(fx, 60, y + 28, big, im.width * k, im.height * k, e["id"]); y += im.height * k + 52

P_wb = page("World Buildings")
wb = frame(P_wb, "World Buildings", 0, 0, 1800, 620)
heading(wb, 60, 40, "WORLD BUILDINGS (parametric-topdown-pixel-architecture)", "Rendered with node cli/tb.js (MIT code). Style atlases may include third-party art: treat as placeholders until each atlas is cleared or replaced.")
B = [("keep", "Lampwarden Keep", "gothic fortress"), ("blacksmith", "Hester's Forge", "nordic forge"), ("tavern", "The Lantern Tavern", "forest tavern"),
     ("watchtower", "Ring Watchtower", "gothic watchtower"), ("tech-outpost", "Archwright Outpost", "steamworks mage_tower")]
for k, (f, nm, cmd) in enumerate(B):
    x = 60 + k * 340; rect(wb, x, 160, 310, 400, PANEL, 10, LINE, 1, name="Card " + nm)
    img(wb, x + 27, 172, os.path.join(ART, "buildings", f + ".png"), 256, 256, f)
    text(wb, x + 14, 440, nm, 16, PARCH, "Bold"); text(wb, x + 14, 466, "tb.js render " + cmd, 12, CYAN); text(wb, x + 14, 490, "256 px, no AA, 1 px silhouette outline", 11, MUTED)

step("file.save", {"path": os.path.join(HERE, "fervois.figcraft")})
json.dump(S, open(os.path.join(HERE, "build", "script.json"), "w"))
json.dump([{"page": p, "frame": nm, "ref": r} for p, nm, r in manifest], open(os.path.join(HERE, "build", "frames.json"), "w"), indent=1)
print(len(S), "steps")
