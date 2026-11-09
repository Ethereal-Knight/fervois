# World generation

## Units
- Tile: 32 x 32 px (characters are 64 x 64, two tiles tall). Region: 256 x 256 tiles (8192 x 8192 px). Render chunk: 32 x 32 tiles (1024 x 1024 px, 64 per region) for culling and simulation.
- Region grid: integer coords `(rx, ry)`, Hollowmere at `(0, 0)`. Distance `d = max(|rx|, |ry|)` (rings are squares).
- Region level: `round(10 * d^1.15) + rand(-2, 2)`, clamped to at least 1. d=1: 10, d=2: 22, d=3: 35, d=5: 64, d=7: 94, d=10: 141, d=20: 313.

## Loading model (loading screens are allowed)
- Each region and each dungeon is its own scene. Crossing a region edge or entering a door shows a loading screen (0.5 to 1.5 s) with a lore line and a tip.
- Generation runs in a Web Worker: worker gets `{worldSeed, rx, ry, card, deltas}` and returns typed arrays for 3 tile layers, a collision grid, and spawn lists.
- Generated regions are cached in memory (last 4) and can be regenerated from the seed at any time, so nothing big is saved.

## Region pipeline (deterministic, seeded with `hash(worldSeed, rx, ry)`)
1. **Biome fields:** two simplex noise maps (elevation, moisture) at 3 octaves. Card biome biases the thresholds.
2. **Edges:** each side has 1 to 2 gates that line up with the neighbor region (gate positions come from a hash of the shared edge, so both sides agree).
3. **Anchors:** waylamp near the center, 2 to 4 dungeon entrances, 3 to 6 points of interest (camp, ruin, shrine, merchant, puzzle) by Poisson disc with a minimum spacing of 40 tiles.
4. **Roads:** A* on a cost grid (water and cliffs expensive) between gates, waylamp and anchors; widen to 3 tiles; place fences and signposts.
5. **Scatter:** trees, rocks, flowers, ruins by Poisson disc per biome; keep roads and anchor clearings open.
6. **Encounters:** budget = `20 + 4 * regionLevel^0.6` points; each pack costs by role (fodder 1, ranged 2, elite 6). Packs avoid roads within 10 tiles of the waylamp.
7. **Story override:** if the story needs a region (act sites), the generator stamps a hand-made 64 x 64 set piece and builds around it.

## Region cards
When a waylamp is relit, the lantern offers 3 cards for each unexplored neighbor in the facing direction. Card = `{biome, faction, modifier}` drawn from tables weighted by ring.
- Biomes: Meadow, Thornwood, Barrow Hills, Marsh, Ember Scrub, Glasswaste, Frost Steppe, Archwright Ruins.
- Factions: Automatons, Bloomtouched, Crowfeather, Iron Choir, mixed.
- Modifiers (examples): Foggy Nights (stealth bonus, lower vision), Rich Veins (more ore), Old Battlefield (more relic drops, more elites), Festival Road (merchants, fewer enemies), Lumen Storm (lightning hazards, more Lumen shards).
Ring 6+ cards also add Ascension modifiers (enemy affixes up, rewards up).

## Dungeons
- Types: Cave, Barrow, Archwright Vault, Bandit Fort, Choir Hall, Geode Hollow.
- Layout: BSP split of a 96 x 96 tile area into 3 to 12 rooms, corridors by MST plus 1 to 2 loops. 30% of rooms come from the hand-made room library (traps, shrines, treasure puzzles, set pieces).
- Clear rule: all packs in "sealed" rooms must be defeated to open the reward vault after the boss.
- Dungeon level = region level + 2. Re-entering regenerates with a new seed (except story dungeons).

## Performance notes
- Only chunks within 1 chunk of the camera simulate enemies. Others freeze.
- Tile layers rendered with Phaser 4 TilemapGPULayer. Props and enemies with SpriteGPULayer where they do not need per-object logic, normal sprites otherwise.
