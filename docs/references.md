# References: pixel art and gamedev resources

Every resource Mike has collected for pixel and 8-bit games, reviewed for FerVois on Nov 8, 2026 (repos cloned, pages read, licenses checked). "Used" means it produced something in this repo. "Referenced" means it shapes the plan but nothing in the repo came from it yet.

| # | Resource | License (checked) | Used or referenced | What it gives FerVois |
|---|---|---|---|---|
| 1 | Pixel Art Atlas 1.4M | CC0-1.0 | **Used** | Every character sheet sprite |
| 2 | mono-pix / fast-pixelizer | MIT | **Used** | Snapped all composites to a clean 16 grid |
| 3 | pixelfx | MIT | **Used** | FX page renders |
| 4 | parametric-topdown-pixel-architecture | MIT code; atlas art not cleared | **Used** | World Buildings page renders |
| 5 | Sprite Fusion pixel-art VFX | MIT | Referenced | FX reference and agent MCP |
| 6 | Kenney | CC0 | Referenced | Gray-box prototype assets |
| 7 | CraftPix freebies | CraftPix license (not CC0) | Referenced only | Style reference |
| 8 | awesome-gamedev-agent-skills | Apache-2.0 | Referenced | Agent skills for the prototype |
| 9 | Spawn | Platform terms | Referenced | Design reference |
| 10 | Paginated Report Bear | Ours | Lessons applied | Hero density, 4 directions, feel checks |

---

## 1. Pixel Art Atlas 1.4M (Angais)
- https://huggingface.co/datasets/Angais/pixel-art-atlas-1.4m
- License: **CC0-1.0**. Commercial use, no attribution required (we credit it anyway in art/SOURCES.md).
- What it is: 1,405,308 train + 4,096 validation 16 x 16 RGBA sprites, each with `caption`, `subject` and `row_id`, in 15 parquet shards of about 29 MB.
- What we found: the first shards are mostly objects (swords, helms, food, furniture). Characters show up from shard 0005 (knight, archmage, gunslinger, ranger, robot knight, clockwork automaton and many more). There are no animation frames and almost no side or back views.
- How we used it: `art/build_sprites.py` reads shards 0000 to 0005 only (about 170 MB, not the full 435 MB), picks sprites by `subject#index`, writes native 16 x 16 and 8x PNGs. The datasets-server search endpoint was failing auth during this session, so we used parquet shards directly.
- How it shapes FerVois: primary source for enemies, NPCs, items, icons and the gear-tier references for the hero. Its captions let us search by subject ("crystal golem", "wild boar"). Its lack of frames is the main art risk (PRD section 23).

## 2. mono-pix (handsupmin) and fast-pixelizer
- https://github.com/handsupmin/mono-pix (web app, React) built on https://github.com/handsupmin/fast-pixelizer (npm `fast-pixelizer` 1.3.10).
- License: **MIT** (both).
- What it does: Snap mode auto-detects the pixel grid of "fake" pixel art (blurred, anti-aliased, misaligned), rebuilds every cell with one color, keeps transparency. Clean and Detail modes pixelate any image.
- Headless on the box: yes. mono-pix itself is a browser app, but its engine runs in Node. `art/snap.mjs` calls `snap()` on every composite.
- Result: on clean 8x exports `snap()` returned exactly 16 x 16 with the source palette preserved (all 6 composites). On a soft-edged (box-blurred) 8x copy it did not recover the 16 grid (it returned 128 x 128), so 16 x 16 sprites with heavy blur are past what it can fix. Its README says the same: it works best when the source really came from a square low-res grid. Report: `art/composites/snap-report.json`.
- How it shapes FerVois: mandatory last step for any AI-generated, recolored or hand-composited sprite before it goes in the game. Keep edits on integer scales.

## 3. pixelfx (patch-gg)
- https://github.com/patch-gg/pixelfx
- License: **MIT** (the bundled Patch Pixel gallery font is not MIT; we do not use it). Adapts Sprite Fusion code (MIT) and Hollow Crown's acting (MIT).
- What it is: 244 code-driven effects in 21 categories, zero dependencies, works in canvas, Phaser and PixiJS, plus a Claude Code skill for making new effects. Options: palette, flip, angle, seed, light.
- How we used it: `art/fx/render_fx.mjs` imports the effect modules in Node, steps them, and writes 6-frame strips: laser bolt (recolored to Lumen Cyan), sword slash, shield block, disintegrate, coin drop. Shown on the FX page of the FigCraft file.
- How it shapes FerVois: our FX library. Combat: melee/sword-slash, double-slash, impacts/shield-block, bullet-impact, projectiles/laser-bolt, muzzle-pistol, muzzle-smg. Defeat without blood: spawn/disintegrate, spawn/poof, spawn/dissolve-burn (for automatons only), spawn/coin-drop. Feedback: ui/level-up, pickups/chest-open. We skip status/bleeding, shadow/grasping-hands, shadow/hex-sigil and critters/flying-skull (off tone).

## 4. parametric-topdown-pixel-architecture (Zengkailin)
- https://github.com/Zengkailin/parametric-topdown-pixel-architecture
- License: the repo LICENSE is **MIT** (GitHub shows NOASSERTION because of an extra note). The note says it is a web port of the Godot plugin `hd2d_scene_tools` and asks users to also follow that plugin's license, and that **atlas art may involve third-party copyright; confirm licensing before use or redistribution**.
- What it is: offline browser tool plus zero-dependency Node CLI (`node cli/tb.js`). 10 styles (jiangnan, forest, desert, machiya, nordic, harbor, palace, gothic, steamworks, jiangnan_pixel), 46 building types (inn, tavern, forge, weaponsmith, watchtower, fortress, mage_tower, mine, ruins and more), 1/2/4/8 directions, sprite sheets, recipe embedded in the PNG.
- How we used it: rendered 5 buildings at 256 px, no AA, 1 px silhouette outline: gothic fortress (Lampwarden Keep), nordic forge (Hester's Forge), forest tavern, gothic watchtower, steamworks mage_tower (Archwright Outpost). About 0.4 s each. In `art/buildings/` and the World Buildings page.
- How it shapes FerVois: layout studies and placeholders for towns, keeps and tech outposts in the prototype. Before shipping: either clear each style atlas's license or make our own style atlas (`styles create --palette ...` or `--atlas`) from CC0 textures, which the CLI supports.

## 5. Sprite Fusion pixel-art VFX
- https://www.spritefusion.com/pixel-art-vfx
- License: **MIT**, free for commercial games.
- What it is: 25 open-source effects as TypeScript files (explosion, impact, slash, muzzle flash, blood, dash and blink, fire, lightning, ice, poison, energy, shield, black hole, holy light, heal and mana, power up, pickup, sparkle, rain, snow, fog, embers, fireflies, leaves, bubbles) and an MCP server for agents (`https://www.spritefusion.com/mcp`).
- How it shapes FerVois: the source pixelfx builds on; use it for weather (fog in the Fade, embers on the Ember Line, falling leaves for Bloom defeats) and holy light (Lumen Oath). **Exclude the Blood effect.** We did not connect the MCP in this session.

## 6. Kenney
- https://kenney.nl/assets
- License: **CC0** for all asset-page assets. Attribution optional ("Kenney"), do not use their logo.
- How it shapes FerVois: gray-box prototype per Mike's process. Tiny Dungeon / Tiny Town style tiles, UI pack (RPG), input prompts (keyboard and gamepad glyphs), Kenney Pixel and Mini fonts, RPG and impact audio. All replaceable later. Not downloaded yet.

## 7. CraftPix freebies
- https://craftpix.net/freebies/ , license page https://craftpix.net/file-licenses/
- License: **CraftPix license, not CC0.** Freebies allow use in personal and commercial games without attribution, but forbid reselling or redistributing the art (including in a way users could extract), and section 3 forbids using any CraftPix asset to train, fine-tune, develop, test or improve AI systems.
- How it shapes FerVois: reference only (tileset composition, UI layout ideas). Do not ship a pack without a per-pack license check, and do not feed CraftPix art into any AI tool (that includes snapping it with an AI-adjacent pipeline or using it as an image-generation reference).

## 8. awesome-gamedev-agent-skills
- https://github.com/gamedev-skills/awesome-gamedev-agent-skills
- License: **Apache-2.0**. 77 portable SKILL.md files with a router.
- Relevant for FerVois (load during the spike and prototype): `web-engines/phaser-core` and `phaser-arcade-physics` (both written for Phaser 4), `disciplines/procedural-gen` (seeded RNG, noise, BSP, WFC, loot tables), `genres/rpg` (stats, inventory, quests, save), `disciplines/save-systems` (versioning, atomic writes, autosave), `disciplines/performance-optimization` (pooling, batching, GC), `disciplines/game-ai` (FSM, steering, A*), `disciplines/game-feel`, `disciplines/dialogue-systems` (Ink or Yarn), `disciplines/game-ui-ux`, `workflows/prototype-fast`. Godot skills only if Q10 picks Godot.

## 9. Spawn
- https://www.spawn.co
- Terms: games made there live there. Its rules say you cannot use Savi to build for other engines or platforms, or prototype on Spawn to ship somewhere else.
- How it shapes FerVois: design reference only. Ideas we borrow: Places (separate areas joined by doors and portals, which matches our region and dungeon scenes with loading screens), instances for groups, "building is a conversation" (small playable steps), loot-balancer style tools. If Mike ever wants a Spawn version, that would be a separate Spawn-native game, not our prototype.

## 10. Lessons from Paginated Report Bear (Ethereal-Knight/paginated-bear)
- Engine: Phaser 3 + Vite + TypeScript, same deploy path (Pages + Fabric). FerVois moves to Phaser 4 for GPU sprite and tilemap layers.
- Character density: the bear is 28 x 32 with front, back, left, right and diagonal views, idle 4, walk 8, jump 5 frames. FerVois heroes need the same: 4 facing directions at a higher density than 16 x 16 (open question Q4).
- Big pixel title portrait (96 x 112 drawn at 2x): FerVois Cover uses a 24x Ascended Knight; the real title should get a hand-made portrait.
- Subtle backgrounds with a white-wash overlay so the character pops: in the style guide.
- Movement feel: coyote time and jump buffer there; for FerVois the same idea is dodge i-frames, a 120 ms input buffer and cancel windows, checked by a feel-check script in CI.
- Sprites generated by code (`make_bear.py`), not hand-edited PNGs: we follow that with `art/build_sprites.py` and `figcraft/generate_design.py`.
