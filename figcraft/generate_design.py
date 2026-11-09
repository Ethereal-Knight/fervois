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
DOLL = json.load(open(os.path.join(ART, "doll", "doll.json")))
import sys; sys.path.insert(0, os.path.join(ART, "doll")); import doll as D

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
    """nearest-neighbor copy of a 16x16 atlas original at k x (provenance thumbnails)."""
    out = os.path.join(PX, f"{pid}_x{k}.png")
    Image.open(os.path.join(ART, "originals-16", pid + ".png")).convert("RGBA").resize((16 * k, 16 * k), Image.NEAREST).save(out)
    return out
def pxi(im, k, name):
    """nearest-neighbor copy of any PIL image at k x."""
    out = os.path.join(PX, f"{name}_x{k}.png"); im.convert("RGBA").resize((im.width * k, im.height * k), Image.NEAREST).save(out); return out
def p64(path, k, name): return pxi(Image.open(path), k, name)
def card(p, x, y, path64, name, role, src, k=3, gold=False, w=220, ref16=None):
    """64x64 sprite card shown at k x. ref16 = atlas original id, drawn small in the corner for provenance."""
    s = 64 * k; rect(p, x, y, w, s + 24 + 100, PANEL, 10, LINE, 1, name="Card " + name)
    img(p, x + (w - s) / 2, y + 12, p64(path64, k, os.path.basename(path64)[:-4] + "_" + str(len(S))), s, s, "Sprite64 " + name)
    if ref16: img(p, x + w - 40, y + 8, px(ref16, 2), 32, 32, "Ref16 " + ref16)
    text(p, x + 10, y + s + 30, name, 14, GOLD if gold else PARCH, "Bold", w=w - 20)
    if role: text(p, x + 10, y + s + 52, role, 11, MUTED, w=w - 20)
    text(p, x + 10, y + s + 98, src, 10, ROSE if gold else CYAN, w=w - 20)
    return w
def sprite(p, x, y, pid, k=3, w=220):
    m = META[pid]; src = m["source"]
    return card(p, x, y, os.path.join(ART, "x64", pid + ".png"), m["name"], m.get("role", ""),
                ("64x64 from composite of " if m["composite"] else "64x64 from ") + f"atlas row {src['row_id']} \"{src['subject']}\"", k, m["composite"], w)
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
TIERS = ["T1 Common start", "T2 mid game", "T3 late game", "T4+ Ascended"]
NPCS = ["npc_aldric", "npc_pip", "npc_wren", "npc_hester", "npc_odo", "npc_caldus", "npc_liora", "npc_pip_awake"]
FACTIONS = [("ROGUE AUTOMATONS", "Old Archwright machines running broken orders. Defeat: sparks and a pixel burst.", CYAN, ["en_cogling", "en_scrapjaw", "en_turret", "en_cogling_elite"]),
            ("BLOOMTOUCHED BEASTS", "Animals overgrown by the Rust Bloom. Defeat: petals and spores drift off, the animal is freed.", ROSE, ["en_tusk", "en_fang", "en_mossback"]),
            ("CROWFEATHER BANDITS", "Desperate outlaw clans. Defeat: they drop and flee in a smoke poof.", SPARK, ["en_cutpurse", "en_gunner"]),
            ("IRON CHOIR + CAVE GUARDIANS", "A rival order and the dungeon wardens they woke. Defeat: disintegrate into light.", VIOLET, ["en_choir", "en_geode"])]
DT = os.path.join(ART, "doll", "tiers")

def classes_block(f, x0, y0):
    text(f, x0, y0, "PLAYER HERO (PAPER DOLL) AND CLASS TIERS", 20, GOLD, "Bold", ls=2)
    rect(f, x0, y0 + 40, 300, 600, PANEL, 10, LINE, 1, name="Card hero base")
    img(f, x0 + 22, y0 + 52, pxi(D.composite({"hair": "short"}, {"*": D.BASE_PAL}, "down"), 4, "hero_base_doll"), 256, 256, "Hero base 64 down")
    for k, v in enumerate(["down", "left", "up", "right"]):
        img(f, x0 + 22 + k * 66, y0 + 320, pxi(D.composite({"hair": "short"}, {"*": D.BASE_PAL}, v), 1, f"hb_{v}"), 64, 64, "Hero base " + v)
    text(f, x0 + 16, y0 + 400, "The Lampbearer (base body)", 15, PARCH, "Bold", w=270)
    text(f, x0 + 16, y0 + 426, "64x64 base body, 4 facings. Every look on this sheet is this body plus equipment layers (see the Paper doll page). Atlas reference: adventurer, row " + str(META["hero_base"]["source"]["row_id"]) + ".", 12, MUTED, w=270)
    img(f, x0 + 16, y0 + 540, px("hero_base", 4), 64, 64, "Ref16 hero_base"); text(f, x0 + 90, y0 + 560, "16x16 atlas original (provenance)", 11, CYAN, w=190)
    gx = x0 + 340
    for t, tl in enumerate(TIERS): text(f, gx + 180 + t * 240, y0 + 40, tl, 13, CYAN if t == 3 else MUTED, "Semi Bold")
    for r, (cid, cname, blurb) in enumerate(CLASSES):
        y = y0 + 70 + r * 330
        text(f, gx, y + 60, cname, 24, PARCH, "Bold", fam=DISP); text(f, gx, y + 96, blurb, 12, MUTED, w=160)
        for t in range(4):
            tier = DOLL["tiers"][cid][t]; lo = ", ".join(v.replace("_", " ") for k, v in tier["loadout"].items() if k != "hair")
            card(f, gx + 180 + t * 240, y, os.path.join(DT, f"{cid}_t{t+1}_down.png"), f"{cname.title()} T{t+1} {tier['name']}", lo,
                 "paper doll composite" + (" + Ascended palette + 1 px aura" if t == 3 else ""), 3, t == 3, 230, ref16=tier["ref16"])
    return 70 + 4 * 330

def npc_block(f, x0, y0):
    text(f, x0, y0, "STORY CHARACTERS (WHOLE 64x64 SPRITES)", 20, GOLD, "Bold", ls=2)
    for k, pid in enumerate(NPCS): sprite(f, x0 + k * 232, y0 + 40, pid, 3, w=220)
    return 40 + 330

def enemy_block(f, x0, y0):
    text(f, x0, y0, "ENEMY FACTIONS (WHOLE 64x64 SPRITES, NO DEMONS, NO BLOOD)", 20, GOLD, "Bold", ls=2)
    x = x0; y = y0 + 40
    for fi, (name, desc, col, ids) in enumerate(FACTIONS):
        if fi == 2: x = x0; y += 72 + 330
        w = len(ids) * 232 - 12
        rect(f, x, y, w, 4, col, 2, name="Faction bar")
        text(f, x, y + 12, name, 15, col, "Bold", ls=1); text(f, x, y + 34, desc, 11, MUTED, w=w)
        for k, pid in enumerate(ids): sprite(f, x + k * 232, y + 72, pid, 3, w=220)
        x += w + 40
    return 40 + 2 * (72 + 330)

# ---------- pages
step("page.rename", {"name": "Cover"})
cov = frame(None, "Cover", 0, 0, 1440, 900)
rect(cov, 0, 0, 1440, 900, "#FFFFFF", op=0.03, name="White wash (Paginated Bear lesson)")
img(cov, 920, 230, p64(os.path.join(DT, "knight_t4_down.png"), 6, "cover_knight_t4"), 384, 384, "Title portrait knight T4 (paper doll)")
text(cov, 96, 230, "FERVOIS", 132, PARCH, "Bold", fam=DISP, ls=6)
text(cov, 100, 400, "Explore an overworld that draws itself as you walk. Clear caves and keeps of rogue machines and bloom-touched beasts. Loot, craft and climb with no level cap. Knights carry swords, shields and the odd laser rifle.", 22, MUTED, w=700)
text(cov, 100, 600, "Concept package v0.1  |  Ethereal Knight  |  Nov 2026", 16, GOLD, "Semi Bold")
text(cov, 100, 630, "Art: 64x64 paper-doll hero + 64x64 NPCs and enemies derived from the CC0 Pixel Art Atlas 1.4M (Angais)", 14, CYAN)

P_cs = page("Character Sheet")
cs = frame(P_cs, "Character Sheet", 0, 0, 2000, 2840)
heading(cs, 60, 40, "FERVOIS CHARACTER SHEET", "Characters are native 64x64, shown at 3x and 4x, nearest-neighbor. The hero is a layered paper doll; NPCs and enemies are whole sprites derived from 16x16 CC0 Pixel Art Atlas originals (small corner thumbnails). Gold = composite or Ascended look.")
h = classes_block(cs, 60, 150)
h2 = npc_block(cs, 60, 150 + h + 40)
enemy_block(cs, 60, 150 + h + 40 + h2 + 40)

P_sg = page("Style Guide")
sg = frame(P_sg, "Style Guide", 0, 0, 1800, 1440)
heading(sg, 60, 40, "STYLE GUIDE", "Medieval first. Tech is a pop, not the base: one tech accent per sprite at most, always in Lumen Cyan.")
pal = [("Night", NIGHT), ("Panel", PANEL), ("Parchment", PARCH), ("Steel", STEEL), ("Ember Gold", GOLD), ("Lumen Cyan", CYAN), ("Bloom Rose", ROSE), ("Moss", MOSS), ("Spark Orange", SPARK), ("Elite Violet", VIOLET)]
for k, (nm, c) in enumerate(pal):
    x = 60 + k * 168; rect(sg, x, 150, 150, 90, c, 12, LINE, 1, name="Swatch " + nm); text(sg, x, 250, nm, 14, PARCH, "Semi Bold"); text(sg, x, 270, c, 12, MUTED)
for nm, c in pal: step("style.create", {"type": "paint", "name": "FerVois/" + nm, "value": [{"type": "solid", "color": c}]})
rules = [
 ("SPRITES", "Characters are 64x64 native: hero, NPCs, enemies. 1 px dark outline tinted toward the fill, 3 to 4 step ramps per material, light from the top left, no anti-aliasing, no blur. Display at integer scale only (2x to 4x). Bosses may use 96x96 or 128x128 on the same rules."),
 ("WORLD TILES", "Decision: 32x32 world tiles. A 64x64 character is 2 tiles tall, which reads well for a Diablo-like camera. Internal render 960x540, integer 2x to 1920x1080, 4x for 4K. 16x16 tiles would need a 2x tile scale and look chunkier than the characters, so they are not used."),
 ("HERO = PAPER DOLL", "Resolved PRD Q4: the hero is a 64x64 base body plus 8 equipment layers (head, chest, legs, feet, hands, back, main hand, off hand) on the same grid and anchors. Gear you find changes the sprite. Down, up, left; right mirrors left. Idle, walk, attack in all 4 directions."),
 ("MEDIEVAL + TECH POP", "Swords, shields, plate, cloth, wood, stone are the base. Lasers, guns, turrets and automatons are Archwright relics: brass and steel bodies, Lumen Cyan glow. Never neon on more than one element per sprite."),
 ("TIERS", "Class tiers are loadouts of layers plus a palette. T4 and up (Ascended) keep the T3 loadout, swap to the Ascended palette (steel to pale frost, trim to Lumen Cyan) and add a 1 px cyan aura on the composite. The aura brightens each Ascension band."),
 ("ZONE RINGS", "Enemy elites further from Hollowmere recolor by ring: Ring 1-2 natural, Ring 3 Spark Orange trim, Ring 4 Elite Violet aura, Ring 5+ Lumen Cyan aura with a pulsing outline."),
 ("NO GORE", "No blood, no demons, no skulls as decoration. Defeat = sparks, pixel dissolve, petals, smoke poof (pixelfx spawn/disintegrate, spawn/poof, spawn/coin-drop). Sprite Fusion's Blood effect is excluded."),
 ("BACKGROUNDS", "Subtle: low-contrast 32x32 ground tiles with a light white wash (2-4%) so 64 px characters pop (Paginated Bear lesson). Title screen uses a big pixel portrait."),
 ("TYPE", "Display: Cinzel (titles, logos). UI: Kenney Pixel or Kenney Mini (CC0) in game; Inter for docs. Numbers in damage pop-ups use the pixel font with Ember Gold crits."),
]
y = 330
for t, body in rules:
    text(sg, 60, y, t, 15, GOLD, "Bold", ls=1); text(sg, 300, y, body, 14, PARCH, w=1400); y += 78
text(sg, 60, y + 10, "REFERENCE TOOLKIT  (full notes: docs/references.md)", 15, GOLD, "Bold", ls=1)
refs = [("Pixel Art Atlas 1.4M", "CC0", "USED: 16x16 originals behind every NPC and enemy 64x64, hero references", CYAN),
        ("mono-pix / fast-pixelizer", "MIT", "USED: snapped all composites to a clean 16 grid", CYAN),
        ("LPC Universal Spritesheet Generator", "CC-BY-SA / GPL / OGA-BY per asset", "Prior art only: 64x64 layered paper doll. No LPC art used", SPARK),
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

P_pd = page("Paper doll")
pd = frame(P_pd, "Paper doll", 0, 0, 2000, 2060)
heading(pd, 60, 40, "PAPER DOLL HERO", "The hero changes as gear is found. One 64x64 base body plus separately drawn equipment layers, all on the same 64x64 frame grid and anchors, so any combination composites correctly and animates in sync. Full spec: docs/systems/paper-doll.md.")
# 1. layer stack (exploded) for Knight T3, facing down
lo3, pal3, _ = D.TIERS["knight"][2]
text(pd, 60, 160, "1. LAYER STACK  (Knight T3, facing down, bottom to top)", 18, GOLD, "Bold", ls=1)
x = 60
for k, (slot, it, im) in enumerate(D.exploded(lo3, pal3, "down")):
    rect(pd, x, 200, 140, 190, PANEL, 8, LINE, 1, name="Layer " + slot)
    img(pd, x + 6, 206, pxi(im, 2, f"ex_{slot}_{it}"), 128, 128, f"Layer {slot}:{it}")
    text(pd, x + 8, 340, f"{k+1}. {slot}", 13, PARCH, "Bold"); text(pd, x + 8, 362, it, 11, CYAN); x += 150
text(pd, x + 10, 280, "=", 40, GOLD, "Bold")
img(pd, x + 50, 200, p64(os.path.join(DT, "knight_t3_down.png"), 3, "pd_k3"), 192, 192, "Composite knight T3")
# 2. draw order per facing
text(pd, 60, 440, "2. DRAW ORDER PER FACING  (left is bottom; right facing = mirrored left frames, same order)", 18, GOLD, "Bold", ls=1)
for r, v in enumerate(["down", "up", "left", "right"]):
    y = 480 + r * 150
    img(pd, 60, y, p64(os.path.join(DT, f"knight_t3_{v}.png"), 2, f"pd_dir_{v}"), 128, 128, "Knight T3 " + v)
    text(pd, 210, y + 10, v.upper(), 16, PARCH, "Bold")
    order = D.ORDER["left" if v == "right" else v]
    text(pd, 210, y + 40, "  >  ".join(order), 14, CYAN, w=900)
    note = {"down": "Cape behind the body, weapons in front.", "up": "Weapons behind the body, cape on top: you see the back.",
            "left": "Off hand (shield) behind the body, main hand in front.", "right": "Not drawn separately: flipX of the left frames. Asymmetric emblems are kept off side views."}[v]
    text(pd, 210, y + 70, note, 12, MUTED, w=900)
# 3. anchors and grid
text(pd, 1240, 440, "3. ANCHORS AND GRID", 18, GOLD, "Bold", ls=1)
ac = D.anchor_chart(6); acp = os.path.join(PX, "anchor_chart.png"); ac.save(acp)
img(pd, 1240, 480, acp, 384, 384, "Anchor chart")
rules = ["Frame 64x64, origin top left. Feet baseline y=60, sprite pivot (32, 60).", "Head anchor (32,19). Neck (32,30). Chest (32,37). Hip (32,46).",
         "Main hand (19,45) down, (27,44) side. Off hand (45,45) down, (37,43) side.", "Guides every 8 px; bold lines every 32 px (one world tile).",
         "Every layer is a full 64x64 frame, transparent outside its item. No per-item offsets.", "Each layer carries its own 1 px outline, so layers stack cleanly."]
for k, rl in enumerate(rules): text(pd, 1640, 480 + k * 62, rl, 12, PARCH, w=320)
# 4. combinations
text(pd, 60, 1100, "4. EXAMPLE COMBINATIONS  (any item fits any slot; the last two are palette swaps of the same Knight T3 loadout)", 18, GOLD, "Bold", ls=1)
for k, c in enumerate(DOLL["combos"]):
    x = 60 + k * 300; rect(pd, x, 1140, 280, 330, PANEL, 10, LINE, 1, name="Combo " + c["name"])
    img(pd, x + 12, 1152, p64(os.path.join(ART, "doll", "combos", c["name"] + ".png"), 4, "combo_" + c["name"]), 256, 256, c["name"])
    text(pd, x + 12, 1414, c["name"].replace("_", " "), 13, ROSE if c["name"].startswith("recolor") else PARCH, "Bold", w=256)
    text(pd, x + 12, 1436, ", ".join(f"{a}:{b}" for a, b in c["loadout"].items()), 10, MUTED, w=256)
# 5. gear progression strip + palette swap
text(pd, 60, 1520, "5. GEAR FOUND = VISIBLE CHANGE  (Knight path, one slot at a time)", 18, GOLD, "Bold", ls=1)
steps = [{"hair": "short"}]; labels = ["start"]
for slot, it in [("feet", "boots"), ("legs", "trousers"), ("chest", "vest"), ("main", "sword"), ("off", "shield"), ("head", "helm_plain"), ("chest", "plate"), ("hands", "gauntlets"), ("back", "cape")]:
    nx = dict(steps[-1]); nx[slot] = it; steps.append(nx); labels.append("+ " + it.replace("_plain", ""))
for k, lo in enumerate(steps):
    pth = os.path.join(PX, f"prog_{k}.png"); D.composite(lo, {"*": D.STEEL}, "down").save(pth)
    img(pd, 60 + k * 180, 1560, p64(pth, 2, f"prog_{k}"), 128, 128, f"Step {k}")
    text(pd, 60 + k * 180, 1696, labels[k], 12, MUTED)
text(pd, 60, 1760, "PALETTE SWAP: each layer is stored as material indices (skin, hair, eye, cloth, cloth 2, metal, trim, leather, wood, accent, white, gem). An item variant is a 12-color palette, so Rusty, Steel, Gilded, Moss, Crimson and Ascended plates share one drawing. In Phaser: a palette-lookup shader, or bake the swap into the layer texture on equip.", 13, PARCH, w=1860)
text(pd, 60, 1840, "PHASER: a Container of synced sprites (one per layer) all playing the same animation key (for example walk_down) with the same frame index; setDepth order per facing from the table above. For crowds or many heroes, bake the composite into a RenderTexture on equip and play that single sheet.", 13, PARCH, w=1860)
text(pd, 60, 1920, "PRIOR ART: the LPC Universal Spritesheet Character Generator (64x64 layered, licensed CC-BY-SA / GPL / OGA-BY per asset). Studied for the layering approach only; no LPC art or code is used in FerVois.", 13, SPARK, w=1860)

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
