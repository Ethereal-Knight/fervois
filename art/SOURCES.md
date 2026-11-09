# Art sources

All character sprites come from the **Pixel Art Atlas 1.4M** by Angais, https://huggingface.co/datasets/Angais/pixel-art-atlas-1.4m, license **CC0-1.0** (public domain dedication, no attribution required; credited here anyway).

- `sprites/` native 16 x 16 PNGs, `x8/` 8x nearest-neighbor copies.
- Composites (recolor + 1 px aura) are marked below. They were snapped with fast-pixelizer (MIT, engine of mono-pix) by `snap.mjs`.
- `fx/` frames rendered from pixelfx (MIT, https://github.com/patch-gg/pixelfx) by `fx/render_fx.mjs`.
- `buildings/` rendered by parametric-topdown-pixel-architecture (MIT code, https://github.com/Zengkailin/parametric-topdown-pixel-architecture). Its style atlases may contain third-party art: placeholders only until cleared.

| id | FerVois name | atlas row_id | subject | caption | shard | composite |
|---|---|---|---|---|---|---|
| hero_base | The Lampbearer (base) | 491640 | adventurer | idle adventurer with a short sword in high contrast | train-0005.parquet | no |
| knight_t1 | Knight T1 Squire Plate | 446802 | knight | side-view bulky knight in flat colors | train-0004.parquet | no |
| knight_t2 | Knight T2 Warden Plate | 445649 | greatsword knight | sword-planted steel greatsword knight with an oversized blade | train-0004.parquet | no |
| knight_t3 | Knight T3 Lumen Paladin | 448326 | royal knight | side-view royal knight with fluted armor | train-0004.parquet | no |
| arcanist_t1 | Arcanist T1 Hedge Caster | 462513 | battle mage | broad battle mage with a breastplate over robes in flat colors | train-0004.parquet | no |
| arcanist_t2 | Arcanist T2 Stormwright | 476860 | storm mage | top-down storm mage with a bolt-shaped staff in bright colors | train-0005.parquet | no |
| arcanist_t3 | Arcanist T3 Starloom Magus | 448023 | archmage | side-facing blue archmage with a tall crown-like hat | train-0004.parquet | no |
| tinker_t1 | Tinker T1 Scrap Apprentice | 452186 | mechanic | kneeling mechanic | train-0004.parquet | no |
| tinker_t2 | Tinker T2 Powder Gunsmith | 469491 | gunslinger | quick-drawing gunslinger with a low-slung holster in muted colors | train-0004.parquet | no |
| tinker_t3 | Tinker T3 Engine Marshal | 468801 | space engineer | top-down hunched space engineer with a scanner | train-0004.parquet | no |
| ranger_t1 | Ranger T1 Wayfinder | 443165 | ranger | watchful ranger with a longbow on the back | train-0004.parquet | no |
| ranger_t2 | Ranger T2 Thornwatch | 448118 | ranger | ranger with twin short swords in muted colors | train-0004.parquet | no |
| ranger_t3 | Ranger T3 Greenveil Hunter | 447469 | hooded archer | hooded archer with a quiver of many arrows in flat colors | train-0004.parquet | no |
| npc_aldric | Sir Aldric Thorne | 450694 | greatsword knight | front-view towering greatsword knight with a round shield | train-0004.parquet | no |
| npc_pip | Pip | 36302 | robot companion | high-tech robot companion | train-0000.parquet | no |
| npc_wren | Wren Ashby | 446561 | girl | waving girl with a teddy bear | train-0004.parquet | no |
| npc_hester | Hester Brann | 437594 | old woman | front-view knitting old woman with a backpack | train-0004.parquet | no |
| npc_odo | Odo Fenn | 438608 | merchant | top-down bowing merchant with spectacles | train-0004.parquet | no |
| npc_caldus | Caldus Thorne | 437059 | archmage | front-view bearded archmage with wide flowing sleeves | train-0004.parquet | no |
| en_cogling | Cogling | 457772 | clockwork automaton | side-view bowing orange clockwork automaton with a chest panel | train-0004.parquet | no |
| en_scrapjaw | Scrapjaw Golem | 443845 | scrap golem | lopsided scrap golem with a cracked lens eye | train-0004.parquet | no |
| en_turret | Lumen Turret | 444715 | laser turret | rotating laser turret in bright colors | train-0004.parquet | no |
| en_tusk | Bramble Tusk | 27794 | wild boar | chubby wild boar with a flower on its head | train-0000.parquet | no |
| en_fang | Bloomfang Wolf | 22859 | wolf | tiny wolf with a flower on its head | train-0000.parquet | no |
| en_mossback | Mossback | 436223 | moss golem | moss golem with flowers on its shoulders in warm colors | train-0004.parquet | no |
| en_cutpurse | Crowfeather Cutpurse | 437545 | highwayman | bowing highwayman with a tricorn hat | train-0004.parquet | no |
| en_gunner | Crowfeather Gunner | 470665 | highwayman | pointing highwayman with a flintlock pistol | train-0004.parquet | no |
| en_choir | Iron Choir Paladin | 427552 | robot knight | sword-raised robot knight in bright colors | train-0004.parquet | no |
| en_geode | Geode Warden | 17934 | crystal golem | cute crystal golem with sparkles | train-0000.parquet | no |
| knight_t4 | Knight T4 Ascended | 448326 | royal knight | side-view royal knight with fluted armor | train-0004.parquet | Recolor of knight_t3: red/orange hues rotated toward cyan, plus 1 px cyan tier aura. Snapped with fast-pixelizer. |
| arcanist_t4 | Arcanist T4 Ascended | 448023 | archmage | side-facing blue archmage with a tall crown-like hat | train-0004.parquet | Recolor of arcanist_t3: red/orange hues rotated toward cyan, plus 1 px cyan tier aura. Snapped with fast-pixelizer. |
| tinker_t4 | Tinker T4 Ascended | 468801 | space engineer | top-down hunched space engineer with a scanner | train-0004.parquet | Recolor of tinker_t3: red/orange hues rotated toward cyan, plus 1 px cyan tier aura. Snapped with fast-pixelizer. |
| ranger_t4 | Ranger T4 Ascended | 447469 | hooded archer | hooded archer with a quiver of many arrows in flat colors | train-0004.parquet | Recolor of ranger_t3: red/orange hues rotated toward cyan, plus 1 px cyan tier aura. Snapped with fast-pixelizer. |
| en_cogling_elite | Cogling, Ring 4 Elite | 457772 | clockwork automaton | side-view bowing orange clockwork automaton with a chest panel | train-0004.parquet | Hue rotate of en_cogling to violet, plus 1 px violet elite aura. Snapped with fast-pixelizer. |
| npc_pip_awake | Pip, Awakened (Act 3) | 36302 | robot companion | high-tech robot companion | train-0000.parquet | Blue accents rotated to gold, plus 1 px gold aura. Snapped with fast-pixelizer. |
