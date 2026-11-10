# Paper doll hero

The hero changes as gear is found. The hero sprite is not one drawing: it is a 64 x 64 base body plus separately drawn equipment layers, all on the same 64 x 64 frame grid and the same anchors, so any combination of items composites correctly and animates in sync. NPCs and enemies stay whole 64 x 64 sprites.

Concept art for this lives on the FigCraft **Paper doll** page (`figcraft/exports/paper-doll.png`). The generator is `art/doll/doll.py`; concept stills are in `art/doll/` (`layers/`, `tiers/`, `combos/`, `doll.json`). Full idle, walk, and attack sheets for the playable test are baked by `art/doll/sheets.py` into `art/doll/hero/`. Run that test from `prototype/doll-test` (see the README).

## 1. Layers

| Order key | Slot | Concept items drawn so far | Notes |
|---|---|---|---|
| `body` | Base body | `base` | Skin, eyes, undershirt, foot wraps. Body type and skin tone are palette choices at character creation. |
| `hair` | Hair | `short`, `long` | Hidden when the head item covers it (helm, plain helm, hood, mail coif). |
| `head` | Head | `helm`, `helm_plain`, `hood`, `wizard_hat`, `goggles` | |
| `chest` | Chest | `plate`, `robe`, `vest`, `coat` | Includes sleeves and shoulder pieces. Long items (robe) cover the legs layer. |
| `legs` | Legs | `greaves`, `trousers` | |
| `feet` | Feet | `sabatons`, `boots` | |
| `hands` | Hands | `gauntlets`, `gloves` | |
| `back` | Back / cape | `cape` | Behind the body facing down and sideways, on top facing up. |
| `main` | Main hand | `sword`, `lumen_blade`, `staff`, `pistol`, `bow` | Grip sits on the main-hand anchor. |
| `off` | Off hand | `shield`, `tome`, `lantern` | Grip sits on the off-hand anchor. |

Eight equipment slots (head, chest, legs, feet, hands, back, main hand, off hand) plus body and hair. Two-handed weapons fill `main` and lock `off`.

## 2. Frame grid and anchors

- Every layer frame is a full 64 x 64 cell, origin top left, transparent outside its item. No per-item offsets, ever: alignment comes from drawing on the shared grid.
- Sprite pivot (game position) is (32, 60): feet baseline y = 60, centered. In Phaser: `setOrigin(0.5, 60 / 64)`.
- Anchors for the idle frame (they move per animation frame, and every layer follows the same per-frame anchor table):

| Anchor | Down | Up | Side (left) |
|---|---|---|---|
| Head center | (32, 19) | (32, 19) | (32, 19) |
| Neck | (32, 30) | (32, 30) | (32, 30) |
| Chest | (32, 37) | (32, 37) | (32, 37) |
| Hip | (32, 46) | (32, 46) | (32, 46) |
| Main hand grip | (19, 45) | (45, 45) | (27, 44) |
| Off hand grip | (45, 45) | (19, 45) | (37, 43) |
| Feet baseline | y = 60 | y = 60 | y = 60 |

- Each layer carries its own 1 px dark outline (tinted 20% toward the fill), so stacked layers never lose their edges.
- A 64 x 64 character is two 32 x 32 world tiles tall (see the Style Guide tile decision).

## 3. Frame sheet layout per animation

One PNG sheet per layer item, identical layout for every layer, 64 x 64 cells, 8 columns x 12 rows (512 x 768 px):

| Rows | Animation | Frames used | Speed |
|---|---|---|---|
| 0 to 3 | `idle` down, left, up, right | 4 | 6 fps |
| 4 to 7 | `walk` down, left, up, right | 8 | 12 fps |
| 8 to 11 | `attack` down, left, up, right | 6 (wind-up 2, strike 2, recover 2) | 16 fps |

- Direction order in every block: down, left, up, right.
- Right rows are drawn only when an item is asymmetric (an emblem, a side holster). Otherwise the bake script fills them by mirroring the left rows, so the runtime never has to flip individual layers.
- Unused cells stay transparent. Later animations (hurt, cast, dodge) append 4-row blocks below; old rows never move, so saved anim keys stay valid.
- Weapon layers draw the swing arc in the attack rows; slash FX come from pixelfx on top.

Status: concept stills in `art/doll/layers/` are the idle frame only (down, up, left, and right mirrored). The playable test set in `art/doll/hero/` has full sheets for 24 gear items plus the body and short and long hair: idle (4 frames), walk (8), and attack (6), in all four directions. Right rows are mirrors of left. Every layer is drawn from one shared pose table, so mixed gear stays aligned. Up-facing attack frames 1 to 3 draw the weapon in front of the body; the cape stays on top. The test wardrobe is `cap`, `mail_coif`, `helm_plain`, `tunic`, `hauberk`, `plate`, `trousers`, `mail_chausses`, `greaves`, `boots`, `mail_boots`, `sabatons`, `hand_wraps`, `gloves`, `gauntlets`, `cloak`, `quiver`, `cape`, `sword`, `bow`, `pistol`, `shield`, `tome`, and `lantern`. `mail_coif` and `helm_plain` hide hair. The bow locks the off hand.

## 4. Draw order per facing

First entry is drawn first (bottom).

| Facing | Order (bottom to top) | Why |
|---|---|---|
| down | back, body, hair, legs, feet, chest, hands, head, off, main | Cape behind, both hands and weapons in front. |
| up | main, off, body, hair, legs, feet, chest, hands, head, back | You see the back: weapons are behind the body, cape covers it. |
| left | off, back, body, hair, legs, feet, chest, hands, head, main | Far arm (shield) behind the body, near arm (weapon) in front. |
| right | same as left, frames mirrored | Uses the right rows of each sheet. |

Per-frame exceptions (for example a sword raised above the head on an up-facing attack frame) go in a small override table `order_overrides[anim][dir][frame]`, not in the art.

## 5. Naming convention

- Layer sheet: `hero/<slot>/<item>.png`, for example `hero/chest/plate.png`, `hero/main/lumen_blade.png`.
- Concept single frames (this repo): `art/doll/layers/<slot>/<item>_<facing>.png`.
- Palette variant: `hero/palettes/<slot>/<item>/<variant>.json`, for example `hero/palettes/chest/plate/gilded.json`.
- Phaser texture key: `doll.<slot>.<item>`; baked palette texture: `doll.<slot>.<item>.<variant>`; baked full hero: `hero.<saveSlot>.<loadoutHash>`.
- Animation keys: `<anim>_<facing>`, for example `walk_down`, `attack_left`. The same key and frame index exist for every layer.
- Item data (`loot-crafting.md`) points at art with `{ slot, item, variant }`; the variant is what dye slots and rarity change.

## 6. Palette swap (recolor)

Layers are authored as **material indices**, not final colors:

| Index | Material | Index | Material |
|---|---|---|---|
| 1 | skin | 7 | metal trim |
| 2 | hair | 8 | leather |
| 3 | eye | 9 | wood |
| 4 | cloth primary | 10 | accent (Lumen Cyan by default) |
| 5 | cloth secondary | 11 | white |
| 6 | metal | 12 | gem |

- A palette is 12 base colors. The build step expands each base color into a ramp (highlight, base, shadow, deep shadow) with small hue shifts (warm light, cool shadow, hue step clamped to 0.035) and shades each material region with light from the top left. Outline color is derived from the touching material.
- Shipping format: an indexed PNG per sheet where palette index = `material * 5 + step` (step 0 outline, 1 deep shadow, 2 shadow, 3 base, 4 highlight). A variant is a 60-entry color table.
- One drawing, many items: Rusty, Steel, Gilded, Moss, Crimson and Ascended plate are the same `plate` sheet with different tables. The Paper doll page shows Knight T3 in moss and crimson.
- Character creation (skin tone, hair color, eye color) and the two dye slots per armor piece are just entries in these tables.
- Ascended (T4+) gear uses the Ascended table (frost steel, Lumen Cyan trim) and adds a 1 px cyan aura around the composite, not per layer.

## 7. Class tiers as composites

Tier looks are loadouts plus palettes (`TIERS` in `art/doll/doll.py`, mirrored in `doll.json`):

| Class | T1 | T2 | T3 | T4+ Ascended |
|---|---|---|---|---|
| Knight | vest, trousers, boots, sword, plain helm | plate, greaves, sabatons, gauntlets, sword, shield, plain helm | adds plumed helm and cape, gilded palette | T3 loadout, lumen blade, Ascended palette + aura |
| Arcanist | robe, boots, staff | adds tome and gloves | adds wizard hat and cape | Ascended palette + aura |
| Tinker | vest, trousers, boots, pistol | coat, gloves, goggles | brass plate set, lantern | adds cape, Ascended palette + aura |
| Ranger | vest, trousers, boots, bow | adds hood and gloves | coat and cape | Ascended palette + aura |

The 16 x 16 atlas sprite of each tier (`art/originals-16/`) is kept as the design reference for silhouette and color; the doll is original work drawn in code.

## 8. Phaser 4 implementation

The playable test (`prototype/doll-test`) uses mode A below: one container, the body sprite drives `animationupdate`, and the other layers copy that frame. Palette variants are baked from the indexed sheets on equip.

Two modes, same data.

**A. Container of synced sprites (default, for the player hero)**
- `hero = scene.add.container(x, y)` with one `Sprite` per drawn slot (`doll.<slot>.<item>.<variant>`).
- The body sprite plays the animation (`walk_down`). On its `animationupdate` event, every other layer calls `setFrame(frame.textureFrame)`; because all sheets share the layout, frame indices match exactly and layers never drift. (Alternative: register the same anim key per texture and start all at once, but one driver is simpler and cannot desync.)
- On facing change, reorder children with the draw-order table (`container.sort` on a per-slot depth map, or `moveTo`).
- Equip or unequip: swap one child texture. Cost: up to 10 sprites per hero, fine for one to four heroes.
- Depth sorting against the world uses the container y (feet baseline).

**B. Bake on equip (for performance: co-op, crowds, town NPCs wearing gear, mirrors in menus)**
- On equip, draw every frame of every layer in draw order into a `DynamicTexture` (RenderTexture) of 512 x 768, add the 64 x 64 frames to the texture manager, and play the normal anim keys on a single sprite.
- Palette swap is applied before the bake (CPU recolor of the indexed sheet into a cached canvas), or by a palette-lookup shader on the baked texture.
- Bake cost is one-off per equip (about 96 frames x 10 layers); cache by `loadoutHash`.
- The spike test (`PRD.md` section 3) measures both: 4 heroes as containers vs baked, and 500 baked sprites.

## 9. Prior art

The **LPC (Liberated Pixel Cup) Universal Spritesheet Character Generator** (https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator) uses the same idea: 64 x 64 layered sheets with shared frame rows per animation and direction, assembled in the browser. Its art is licensed per asset under CC-BY-SA, CC-BY, OGA-BY and GPL (some CC0), with mandatory credits for every author (CREDITS.csv) and share-alike or copyleft terms on some assets. FerVois uses it as **prior art for the system only**: no LPC images, sheets or code are used, so none of those terms apply. If a future prototype ever borrows an LPC asset, it must be logged in `art/SOURCES.md` with its license and credits, and CC-BY-SA or GPL assets need a deliberate decision first.
