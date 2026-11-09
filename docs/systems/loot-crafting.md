# Loot, missions, crafting

## Rarity
| Rarity | Color | Affixes | Drop weight (Ring 1) | Note |
|---|---|---|---|---|
| Common | white | 0 | 60 | salvage fodder |
| Fine | green | 1 | 28 | |
| Rare | blue | 2 | 10 | |
| Heroic | violet | 4 | 1.8 | |
| Legendary | gold | 4 + 1 legendary power | 0.2 | build-defining |
| Relic | cyan | unique fixed | 0.02 | Archwright tech-pop items with unique mechanics (laser lance, pulse pistol, shield emitter) |
Deeper rings shift the weights: each ring multiplies Heroic+ weights by 1.25. Luck adds `luck / (luck + 200)` up to +100% relative.

## Slots
Weapon, off-hand (shield, tome, pistol, quiver), helm, chest, gloves, boots, belt, amulet, 2 rings, trinket. Visible on the sprite: helm, chest, weapon, off-hand, back.

## Affixes (examples)
- Prefixes: Sharpened (+% physical), Kindled (+fire), Rimed (+frost), Storm-wired (+lightning), Lumen-forged (+lumen), Thorned (+nature), Stalwart (+armor), Swift (+attack speed).
- Suffixes: of the Bear (+Grit), of the Hawk (+Finesse), of the Scholar (+Focus), of the Bull (+Might), of Fortune (+luck), of Echoes (+cooldown), of the Waylamp (+health regen), of the Fade (+damage vs elites).
- Values roll in tiers by item level: `value = tierBase * 1.07^ilvl * roll(0.8..1.2)` for flat stats, rating for percent stats.

## Legendary powers (examples)
- Aldric's Oath (Knight shield): blocking stores Resolve; full Resolve releases a Lumen shockwave.
- Kindlewick (Arcanist staff): every 5th fireball splits into 3.
- Duchess's Bridle (trinket): dodge leaves a decoy mule. Yes, a mule.
- Crowfeather Cloak (Ranger): first shot from stealth crits and poofs you back into stealth.
- Cantor's Coil (Tinker): turrets sing; each turret nearby gives +10% fire rate.

## Missions (Odo's board)
- 3 contracts on the board, refresh when you return from a region.
- Types: Clear (a named dungeon), Hunt (a named elite with a nickname), Recover (a relic deep in a dungeon), Escort (a merchant cart to a waylamp), Defend (a camp for 3 waves), Survey (relight a waylamp in a new region).
- Reward: **targeted gear**: you pick the slot before accepting; item level = mission level; rarity at least Rare, Heroic chance 25%. Plus materials and gold.
- Mission level = target region level, so missions also pull you outward.

## Materials
Scrap (automatons), Hide (beasts), Cloth (bandits), Ore (veins), Bloom Resin (Bloomtouched), Lumen Shards (Ring 3+ vaults), Deep Shards (Ring 6+), Runestones (Choir halls, Arcanist).

## Stations
| Station | Who | Does |
|---|---|---|
| Hester's Forge | Hester | Craft weapons and armor from blueprints, Enhance +N, Reforge one affix, Transmog |
| Wren's Workshop | Wren (after Act 1) | Guns, gadgets, turret parts, Socket mods, Ascend (T3 to T4+ look and band) |
| Rune Loom | (Act 2, Starloom ruin) | Craft and inscribe spell runes |
| Salvage bench | anyone | Break items into materials; Legendary salvage gives an Essence used for rerolling powers |

## Operations
- **Craft:** blueprint + materials, item level = your level or the blueprint's ring, whichever is lower.
- **Salvage:** returns 40% to 80% of materials by rarity.
- **Reforge:** reroll one affix, cost doubles each time on the same item (resets on enhance).
- **Socket:** add a socket (max 1 per 50 item levels, no hard cap), fill with gems or mods.
- **Enhance:** +N with no cap (progression.md).
- **Ascend:** turns a T3 item into a T4+ Ascended item: new look rule (cyan aura), +1 affix slot each Ascension band (every 100 item levels).
