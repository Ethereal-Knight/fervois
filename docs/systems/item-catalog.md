# Item catalog (paper-doll wardrobe)

This is the list of unique silhouettes to draw for the hero, not the list of every loot drop. Mixing these pieces is the fun of FerVois: each shape changes how the character looks and how they fight. Recolors, dyes, rarity and enhancement do not add drawings.

Status: inventory, plus a playable test. 31 keys now have full idle, walk, and attack sheets in `art/doll/hero/` and are marked **full sheet**. Keys that still only have a concept idle in `art/doll/layers/` stay **have idle**. Everything else is **to draw**. The Veris outfit is seven of those full sheets (`veris_circlet`, `veris_vest_plate`, `veris_greaves`, `veris_heeled_boots`, `veris_gauntlets`, `veris_longcoat`, `ferro_blade`) plus the hair style `hair_long_streak`, which is not a clothing silhouette. Glow pixels use the accent palette slot.

## 1. How to read this list

- One row is one art key: a unique 64 x 64 layer shape. Palettes such as Steel, Gilded, Moss, Crimson, Veris and Ascended reuse that same drawing.
- Visible slots that need art: head, chest, legs, feet, hands, back, main hand, off hand. Jewelry (belt, amulet, rings, trinket) drops as loot but has no layer yet.
- Weight sets the body feel: **Light** is faster and dodgier with less armor, **Medium** is balanced, **Heavy** is slower, sturdier and harder to stagger.
- Stance is the fighting-style hook, and pieces are meant to be mixed. Two pieces that share a stance or a family give a small echo bonus; four or more give a slightly larger one. There are no mandatory sets.
- Stance tags:
  - **Guard**: block, poise, riposte
  - **Skirmish**: attack speed, move after hits
  - **Channel**: cast speed, mana, spell power
  - **Hunt**: quiet steps, stealth, crit
  - **Rig**: gadgets, heat cap, reload
  - **Wild**: companions, nature damage
- Long chests marked **covers legs** hide the legs layer. Head pieces marked **hides hair** hide the hair layer. Weapons marked **2H** fill main hand and lock the off hand.
- Transmog at Hester's Forge changes only the look. Fighting style always comes from the real item you have equipped.
- **Found** is the earliest ring or faction where that silhouette should appear. Deeper rings keep dropping it with higher item levels.

## 2. Counts

| Slot | Full sheet | Have idle | To draw | Total |
|---|---:|---:|---:|---:|
| Head | 4 | 4 | 15 | 23 |
| Chest | 4 | 3 | 16 | 23 |
| Legs | 4 | 0 | 13 | 17 |
| Feet | 4 | 0 | 11 | 15 |
| Hands | 4 | 0 | 7 | 11 |
| Back | 4 | 0 | 7 | 11 |
| Main hand | 4 | 2 | 16 | 22 |
| Off hand | 3 | 0 | 11 | 14 |
| **Clothing subtotal** | **24** | **7** | **69** | **100** |
| **Weapons subtotal** | **7** | **2** | **27** | **36** |
| **All unique silhouettes** | **31** | **9** | **96** | **136** |

Draw clothing first (head, chest, legs, feet, then hands and back). That is the mix-and-match wardrobe. Weapons come next, because they change the basic attack. Walk and attack frames come after the idle four-facing set exists for each shape.

## 3. Head

| Art key | Name | Family | Weight | Stance | Found | Art | Notes |
|---|---|---|---|---|---|---|---|
| `cap` | Knit Cap | Cloth | Light | Skirmish | R0 | full sheet | Shows hair. Hollowmere starter. |
| `bandana` | Wayscarf | Cloth | Light | Hunt | R1 | to draw | Face wrap, slight stealth. Shows hair. |
| `circlet` | Lumen Circlet | Cloth | Light | Channel | R1 | to draw | Shows hair. Focus and mana. |
| `veris_circlet` | Ferro Circlet | Plate | Light | Channel | R0 | full sheet | Shows hair. Thin silver band, violet stone. Optional on Veris. |
| `pilgrim_hat` | Pilgrim Hat | Cloth | Light | Hunt | R1 | to draw | Wide brim. Survey and luck. |
| `cowl` | Fade Cowl | Cloth | Light | Channel | R2 | to draw | Hides hair. Resist vs Fade elites. |
| `wizard_hat` | Starloom Hat | Cloth | Light | Channel | R2 | have idle | Hides hair. Classic arcanist point. |
| `hood` | Hunter Hood | Leather | Light | Hunt | R1 | have idle | Hides hair. Quiet and first-hit crit. |
| `leather_cap` | Leather Cap | Leather | Light | Skirmish | R1 | to draw | Shows hair. Light melee. |
| `crow_mask` | Crowfeather Mask | Leather | Light | Hunt | R3 | to draw | Hides face. Stealth, Crowfeather camps. |
| `mail_coif` | Mail Coif | Mail | Medium | Guard | R1 | full sheet | Hides hair. |
| `nasal_helm` | Nasal Helm | Mail | Medium | Guard | R2 | to draw | Open face, nose guard. |
| `helm_plain` | Plain Helm | Plate | Medium | Guard | R0 | full sheet | Open-face knight starter. |
| `kettle_hat` | Kettle Hat | Plate | Medium | Guard | R1 | to draw | Wide steel brim, face open. |
| `sallet` | Sallet | Plate | Heavy | Guard | R2 | to draw | Tail in back. Hides hair. |
| `helm` | Plumed Helm | Plate | Heavy | Guard | R2 | have idle | Hides hair. Knight T3 look. |
| `winged_helm` | Winged Helm | Plate | Heavy | Skirmish | R3 | to draw | Hides hair. Charge and presence. |
| `choir_mask` | Iron Choir Mask | Plate | Heavy | Channel | R4 | to draw | Hides face. Lumen resist and aura. |
| `bloom_wreath` | Bloom Wreath | Cloth | Light | Wild | R2 | to draw | Shows hair. Companion and nature. |
| `goggles` | Wren Goggles | Tech | Light | Rig | R1 | have idle | Shows hair. Aim, crit, heat resist. |
| `miner_lamp` | Lamp Helm | Tech | Light | Rig | R2 | to draw | Built-in light. Survey and caves. |
| `visor_helm` | Archwright Visor | Tech | Medium | Rig | R4 | to draw | Hides eyes. Ranged accuracy. |
| `rebreather` | Glasswaste Breather | Tech | Medium | Rig | R4 | to draw | Bloom and gas resist. |

## 4. Chest (shirts and armor)

| Art key | Name | Family | Weight | Stance | Found | Art | Notes |
|---|---|---|---|---|---|---|---|
| `tunic` | Homespun Tunic | Cloth | Light | Skirmish | R0 | full sheet | Hollowmere starter shirt. |
| `shirt` | Lace Shirt | Cloth | Light | Channel | R1 | to draw | Light caster shirt, sleeves showing. |
| `tabard` | Lampwarden Tabard | Cloth | Light | Guard | R1 | to draw | Emblem on a light chest. |
| `padded` | Padded Gambeson | Cloth | Medium | Guard | R1 | to draw | Quilted, the step before mail. |
| `robe` | Scholar Robe | Cloth | Light | Channel | R0 | have idle | Covers legs. |
| `choir_cassock` | Choir Cassock | Cloth | Medium | Channel | R4 | to draw | Covers legs. Lumen chant synergy. |
| `bloom_wrap` | Bloomweave Wrap | Cloth | Light | Wild | R2 | to draw | Soft layered cloth. Nature synergy. |
| `vest` | Field Vest | Leather | Light | Skirmish | R0 | have idle | Open vest, starter for three classes. |
| `jerkin` | Leather Jerkin | Leather | Light | Hunt | R1 | to draw | Closed leather, quieter than a vest. |
| `coat` | Long Coat | Leather | Medium | Skirmish | R2 | have idle | Long tails. Partial cover over legs. |
| `gunner_coat` | Gunner's Coat | Leather | Medium | Rig | R2 | to draw | Bandolier and wide skirts. |
| `crow_jerkin` | Crowfeather Jerkin | Leather | Light | Hunt | R3 | to draw | Feathered shoulders, stealth. |
| `brigandine` | Brigandine | Leather | Medium | Guard | R2 | to draw | Cloth with studded plates. |
| `hauberk` | Mail Hauberk | Mail | Medium | Guard | R1 | full sheet | Long mail, covers hips. |
| `scale` | Scale Shirt | Mail | Medium | Skirmish | R2 | to draw | More flexible than a hauberk. |
| `cuirass` | Breastplate | Plate | Medium | Guard | R2 | to draw | Chest only, more mobility than full plate. |
| `plate` | Plate Cuirass | Plate | Heavy | Guard | R1 | full sheet | Shoulders and chest. Knight T2 look. |
| `heavy_plate` | Field Plate | Plate | Heavy | Guard | R3 | to draw | Bigger shoulders and fauld. |
| `coil_vest` | Coil Vest | Tech | Light | Rig | R2 | to draw | Wired cloth, gadget slots, heat. |
| `brass_plate` | Brass Cuirass | Tech | Heavy | Rig | R3 | to draw | Tinker marshal look, split from plain plate. |
| `lumen_cuirass` | Heart-Forge Cuirass | Tech | Heavy | Channel | R5 | to draw | One cyan accent. Relic-tier look. |
| `veris_vest_plate` | Ocular Vest | Plate | Medium | Channel | R0 | full sheet | Charcoal vest, silver plate, Ocular Core. Sleeves split near/far with spiked pauldrons. |
| `surcoat` | Wayfarer Surcoat | Cloth | Light | Hunt | R1 | to draw | Travel tabard over a plain shirt. |

## 5. Legs (pants)

| Art key | Name | Family | Weight | Stance | Found | Art | Notes |
|---|---|---|---|---|---|---|---|
| `wraps` | Footman's Wraps | Cloth | Light | Skirmish | R0 | to draw | Almost bare, starter. |
| `hose` | Hose | Cloth | Light | Channel | R1 | to draw | Tight cloth legs for casters. |
| `trousers` | Cloth Trousers | Cloth | Light | Skirmish | R0 | full sheet | Default pants. |
| `skirted` | Robe Tails | Cloth | Light | Channel | R1 | to draw | Use with short chests when no covering robe is on. |
| `work_pants` | Workshop Pants | Cloth | Light | Rig | R1 | to draw | Apron tie and deep pockets. |
| `bloom_wraps` | Vine Wraps | Cloth | Light | Wild | R2 | to draw | Leaf-wrapped legs. |
| `leather_pants` | Leather Trousers | Leather | Light | Skirmish | R1 | to draw | Sturdier everyday pants. |
| `chaps` | Rider Chaps | Leather | Light | Hunt | R2 | to draw | Open over cloth, riding look. |
| `hunter_pants` | Thornwood Pants | Leather | Light | Hunt | R2 | to draw | Quiet, bramble-resistant. |
| `crow_trews` | Crowfeather Trews | Leather | Light | Hunt | R3 | to draw | Dark, feathered cuffs. |
| `mail_chausses` | Mail Chausses | Mail | Medium | Guard | R1 | full sheet | Mail over the thighs. |
| `greaves` | Plate Greaves | Plate | Heavy | Guard | R1 | full sheet | Knight T2 look. |
| `veris_greaves` | Ferro Greaves | Plate | Medium | Channel | R0 | full sheet | Silver thigh plates and greaves, small violet gems. |
| `tassets` | Plate Tassets | Plate | Heavy | Guard | R2 | to draw | Hanging hip plates. |
| `fluted_greaves` | Fluted Greaves | Plate | Heavy | Guard | R3 | to draw | Fancy fluting, more poise. |
| `choir_tassets` | Choir Tassets | Plate | Medium | Channel | R4 | to draw | Choir thigh plates. |
| `piston_greaves` | Piston Greaves | Tech | Medium | Rig | R4 | to draw | Kick and no-stagger on landings. |

## 6. Feet (boots)

| Art key | Name | Family | Weight | Stance | Found | Art | Notes |
|---|---|---|---|---|---|---|---|
| `foot_wraps` | Foot Wraps | Cloth | Light | Skirmish | R0 | to draw | Starter. Body already has wraps if nothing is equipped. |
| `sandals` | Sandals | Cloth | Light | Channel | R1 | to draw | Open, slight move speed. |
| `slippers` | Scholar Slippers | Cloth | Light | Channel | R1 | to draw | Quiet indoor shoes, poor on trails. |
| `boots` | Leather Boots | Leather | Light | Skirmish | R0 | full sheet | Default boots. |
| `soft_boots` | Soft Boots | Leather | Light | Hunt | R1 | to draw | Quiet steps, stealth. |
| `tall_boots` | Tall Boots | Leather | Medium | Skirmish | R2 | to draw | Knee high, firmer stride. |
| `work_boots` | Work Boots | Leather | Medium | Rig | R1 | to draw | Heavy soles, workshop and caves. |
| `riding_boots` | Riding Boots | Leather | Medium | Hunt | R2 | to draw | Spurred, mount and move. |
| `crow_soles` | Crowfeather Soles | Leather | Light | Hunt | R3 | to draw | Soft dark soles, very quiet. |
| `root_boots` | Rootboots | Leather | Light | Wild | R2 | to draw | Nature and grove move. |
| `mail_boots` | Mail Boots | Mail | Medium | Guard | R1 | full sheet | Mail over the instep. |
| `sabatons` | Sabatons | Plate | Heavy | Guard | R1 | full sheet | Knight T2 look. |
| `veris_heeled_boots` | Heeled Ferro Boots | Plate | Medium | Channel | R0 | full sheet | Tall black heels with silver plates and a violet gem. |
| `heavy_sabatons` | Locked Sabatons | Plate | Heavy | Guard | R3 | to draw | Slower, much harder to stagger. |
| `mag_boots` | Clamp Boots | Tech | Medium | Rig | R4 | to draw | Resist knockback, cave walls. |

## 7. Hands

| Art key | Name | Family | Weight | Stance | Found | Art | Notes |
|---|---|---|---|---|---|---|---|
| `hand_wraps` | Hand Wraps | Cloth | Light | Skirmish | R0 | full sheet | Starter. |
| `wool_gloves` | Wool Gloves | Cloth | Light | Channel | R1 | to draw | Caster gloves. |
| `gloves` | Leather Gloves | Leather | Light | Skirmish | R1 | full sheet | Default gloves. |
| `archery_gloves` | Archer's Gloves | Leather | Light | Hunt | R1 | to draw | Bow and thrown accuracy. |
| `tool_gloves` | Tool Gloves | Leather | Light | Rig | R1 | to draw | Reload and gadget speed. |
| `thorn_gloves` | Bloom Thorn Gloves | Leather | Light | Wild | R2 | to draw | Nature on hit. |
| `mail_mittens` | Mail Mittens | Mail | Medium | Guard | R2 | to draw | |
| `gauntlets` | Plate Gauntlets | Plate | Heavy | Guard | R1 | full sheet | Knight T2 look. |
| `veris_gauntlets` | Ferro Gauntlets | Plate | Medium | Channel | R0 | full sheet | Silver bracers and gauntlets, split near/far, violet crystal. |
| `insulated` | Insulated Gloves | Tech | Medium | Rig | R3 | to draw | Heat cap and vent. |
| `choir_gauntlets` | Choir Gauntlets | Plate | Medium | Channel | R4 | to draw | Lumen on block or cast. |

## 8. Back

| Art key | Name | Family | Weight | Stance | Found | Art | Notes |
|---|---|---|---|---|---|---|---|
| `short_cape` | Half Cape | Cloth | Light | Skirmish | R1 | to draw | Shoulder only. |
| `cape` | Cape | Cloth | Light | Guard | R2 | full sheet | Default cape, class T3 looks. |
| `veris_longcoat` | Veris Longcoat | Cloth | Medium | Channel | R0 | full sheet | Floor-length black coat, navy rim, silver edge, three swinging tails. Eye emblem and hip chain on the back. Drapes behind the legs. |
| `cloak` | Travel Cloak | Cloth | Light | Hunt | R1 | full sheet | Weather and quiet. |
| `vine_cloak` | Bloomcloak | Cloth | Light | Wild | R2 | to draw | Leaf mantle. |
| `choir_mantle` | Choir Mantle | Cloth | Medium | Channel | R4 | to draw | Wide formal mantle. |
| `lumen_banner` | Lampwarden Banner | Cloth | Medium | Guard | R3 | to draw | Back banner, small ally aura. |
| `pack` | Traveler's Pack | Leather | Medium | Skirmish | R1 | to draw | Look plus a little carry and stamina. |
| `quiver` | Quiver | Leather | Light | Hunt | R1 | full sheet | Shown with bows. Slight bow speed. |
| `crow_cloak` | Crowfeather Cloak | Leather | Light | Hunt | R3 | to draw | Legendary power *Crowfeather Cloak* uses this shape. |
| `tool_rig` | Tool Rig | Tech | Light | Rig | R2 | to draw | Back rig for gadgets and turrets. |

## 9. Main hand (weapons)

Each weapon class sets the basic attack animation, range and timing. That is the strongest fighting-style change in the catalog.

| Art key | Name | Class | Hands | Stance | Found | Art | Notes |
|---|---|---|---|---|---|---|---|
| `dagger` | Side Blade | Slash, fast | 1H | Hunt | R0 | to draw | Short range, high speed. |
| `sword` | Arming Sword | Slash | 1H | Guard | R0 | full sheet | Default knight blade. |
| `ferro_blade` | Ferro Blade | Slash, lumen | 1H | Channel | R0 | full sheet | Angular silver sword with a violet edge. Uses the arming-sword swing. |
| `longsword` | Longsword | Slash | 1H | Skirmish | R1 | to draw | Longer reach than the arming sword. |
| `greatsword` | Greatsword | Slash, heavy | 2H | Skirmish | R2 | to draw | Wide slow swings. |
| `hand_axe` | Hand Axe | Slash | 1H | Skirmish | R1 | to draw | Bleed-on-hit feel, no blood: spark chips. |
| `battle_axe` | Battle Axe | Slash, heavy | 2H | Skirmish | R2 | to draw | |
| `mace` | Mace | Strike | 1H | Guard | R1 | to draw | Stagger on hit. |
| `war_hammer` | War Hammer | Strike, heavy | 1H | Guard | R2 | to draw | Bigger stagger, slower. |
| `spear` | Spear | Thrust | 1H | Skirmish | R1 | to draw | Long reach, linear lunges. |
| `poleaxe` | Poleaxe | Thrust and slash | 2H | Guard | R3 | to draw | Reach plus heavy hits. |
| `staff` | Scholar Staff | Cast | 1H | Channel | R0 | have idle | Default arcanist focus. |
| `war_staff` | War Staff | Cast and strike | 2H | Channel | R2 | to draw | Melee poke plus spells. |
| `lumen_blade` | Lumen Blade | Slash, lumen | 1H | Channel | R3 | have idle | Tech-pop sword, cyan edge. |
| `bow` | Hunter Bow | Bow | 2H | Hunt | R0 | full sheet | Default ranger bow. |
| `longbow` | Longbow | Bow | 2H | Hunt | R2 | to draw | Longer range, slower draw. |
| `crossbow` | Crossbow | Bow | 2H | Hunt | R2 | to draw | Slow reload, heavy bolts. |
| `pistol` | Flintlock | Firearm | 1H | Rig | R0 | full sheet | Default tinker gun, medieval look. |
| `scattergun` | Scattergun | Firearm | 1H | Rig | R2 | to draw | Short range cone. |
| `pulse_pistol` | Pulse Pistol | Firearm, lumen | 1H | Rig | R4 | to draw | Relic. Unique mechanic. |
| `laser_lance` | Laser Lance | Beam | 2H | Rig | R4 | to draw | Relic. Tinker Lancer tech pop. |
| `wrench` | Workshop Wrench | Strike | 1H | Rig | R1 | to draw | Melee and turret repair. |

The wrench and the ferro blade make this slot 22 rows. The wrench stays in the first weapons pass because the Engineer tree needs a visible melee tool.

## 10. Off hand

| Art key | Name | Kind | Stance | Found | Art | Notes |
|---|---|---|---|---|---|---|
| `buckler` | Buckler | Shield | Skirmish | R1 | to draw | Small, parry window, little cover. |
| `shield` | Heater Shield | Shield | Guard | R0 | full sheet | Default knight shield. |
| `kite_shield` | Kite Shield | Shield | Guard | R2 | to draw | Taller, more missile cover. |
| `tower_shield` | Tower Shield | Shield | Guard | R3 | to draw | Huge cover, slower move and attack. |
| `lumen_ward` | Aldric's Oath | Shield, unique | Guard | Story | to draw | Legendary: blocking stores Resolve, then a Lumen shockwave. |
| `tome` | Tome | Focus | Channel | R1 | full sheet | Default arcanist off hand. |
| `focus_orb` | Focus Orb | Focus | Channel | R2 | to draw | Faster casts, less defense. |
| `rune_tablet` | Rune Tablet | Focus | Channel | R3 | to draw | Starloom rune slots. |
| `lantern` | Waylamp Lantern | Lamp | Channel | R0 | full sheet | Aldric's gift can use this shape or `aldric_lantern` below. |
| `hand_lamp` | Hand Lamp | Lamp | Hunt | R1 | to draw | Common cave light, weaker than the story lantern. |
| `parry_dagger` | Parrying Dagger | Blade | Hunt | R1 | to draw | Parry and a short riposte. |
| `sidearm` | Side Pistol | Firearm | Rig | R2 | to draw | Off-hand gun, pairs with a main pistol or wrench. |
| `toolkit` | Toolkit | Gadget | Rig | R1 | to draw | Reload, repair, gadget cooldown. |
| `shield_emitter` | Shield Emitter | Relic | Rig | R4 | to draw | Relic. A projected barrier instead of a wood shield. |

If the story lantern needs its own silhouette, add `aldric_lantern` during the weapons pass and keep `lantern` as the common lamp. Until then, `lantern` covers both.

## 11. Jewelry (no layer yet)

These slots exist in loot and do not need paper-doll art for this pass: belt, amulet, two rings, trinket. They roll affixes like any other item. Named examples already in the design, still with no sprite:

| Name | Slot | Note |
|---|---|---|
| Duchess's Bridle | Trinket | Legendary: dodge leaves a decoy mule. |
| Cantor's Coil | Trinket | Legendary: each nearby turret gives fire rate. |
| Valor Token | Trinket | Side quest "The Smallest Knight". |
| Waylamp Amulet | Amulet | Hollowmere and Lampwarden drops. |
| Signet of the Road | Ring | Luck and move. |
| Bloomheart Ring | Ring | Nature and companions. |
| Hester's Clasp | Belt | Crafting and enhance cost later, or a simple armor belt. |

A thin `belt` layer can be added later if waist items should show. Do not block the clothing pass on it.

## 12. What we already have

These keys have full idle, walk, and attack sheets under `art/doll/hero/`:

`cap`, `mail_coif`, `helm_plain`, `veris_circlet`, `tunic`, `hauberk`, `plate`, `veris_vest_plate`, `trousers`, `mail_chausses`, `greaves`, `veris_greaves`, `boots`, `mail_boots`, `sabatons`, `veris_heeled_boots`, `hand_wraps`, `gloves`, `gauntlets`, `veris_gauntlets`, `cloak`, `quiver`, `cape`, `veris_longcoat`, `sword`, `ferro_blade`, `bow`, `pistol`, `shield`, `tome`, `lantern`.

Hair styles with full sheets, not counted as clothing silhouettes: `short`, `long`, `hair_long_streak`.

These keys still have only an idle concept frame under `art/doll/layers/`:

`helm`, `hood`, `wizard_hat`, `goggles`, `robe`, `vest`, `coat`, `lumen_blade`, `staff`.

Class tier loadouts in `art/doll/doll.json` keep using these keys. New keys slot in beside them. Brass plate for the Tinker T3 look should move from reused `plate` onto `brass_plate` once that layer exists.

## 13. Build order

1. This catalog (done as a list, open to edits).
2. Draw idle frames, all four facings, for the 78 missing clothing shapes, in this order: chest, legs, feet, head, then hands and back. Chest and legs do the most for mix-and-match.
3. Draw idle frames for the 27 missing weapon and off-hand shapes.
4. Author walk and attack frames, on the shared 8 by 12 sheet, for every key that is in use. The 24-key playable test already has those frames. Clothing layers share body motion; weapon layers need their own swing or aim arcs.
5. Hand-polish the hero body, the most used clothing, and the starting weapons.

Palette variants are a data pass, not an art pass: Rusty, Steel, Gilded, Moss, Crimson, faction colors and Ascended all ride the same sheets.

## 14. Open calls in this catalog

- The wrench brings main-hand keys to 21. Keep it or fold repair into the toolkit only.
- Whether `lantern` and Aldric's lantern share one shape.
- Whether a visible `belt` layer is worth adding after clothing.
- Whether long `coat` tails should hide the legs layer the same way `robe` does (current note: partial cover, legs still draw).
