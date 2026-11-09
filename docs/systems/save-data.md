# Save data

Principle: save choices and changes, not the world. The world comes back from the seed.

## Storage
- IndexedDB (via idb-keyval or a tiny wrapper), 3 save slots plus an autosave per slot. Export and import as a JSON file from the settings screen (backup, move between devices).
- Autosave on: waylamp relit, dungeon cleared, level up, crafting action, every 2 minutes, page hide.

## Shape (versioned)
```json
{
  "version": 1,
  "worldSeed": "fv-8c1d2e",
  "player": { "name": "", "class": "knight", "level": 37, "xp": 51234, "attributes": {}, "skills": {}, "ascension": {} },
  "inventory": [{ "id": "u123", "base": "longsword", "ilvl": 37, "rarity": "rare", "affixes": [], "enh": 12, "sockets": [] }],
  "stash": [],
  "regions": { "1,0": { "card": "meadow|crowfeather|festival", "lamp": true, "dungeons": { "d0": "cleared" }, "chests": [3, 7], "poi": [1] } },
  "story": { "act": 2, "flags": ["pip_word_lamp", "odo_truce"] },
  "quests": { "ashby_farm": { "step": 2 } },
  "town": { "workshop": 2, "bakery": true },
  "stats": { "playtimeSec": 0, "knockouts": 0 }
}
```
- Region deltas are small: a few ids per region. 500 explored regions stay well under 1 MB.
- Big numbers stored as strings in the Num format (doubles now, log-space later) so the format does not change when we swap.
- Migrations: `migrate[v]` functions run in order on load. Never delete an old migration.

## Cloud (later)
- Optional sign-in sync if co-op happens (open question Q2). Same JSON, last-write-wins with a conflict prompt.
