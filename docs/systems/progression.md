# Progression math (no caps)

Goal: numbers can go up forever, the game stays playable, and every upgrade still matters.

## Levels
- XP to next level: `xp(L) = 50 * L^2` for L <= 100, then `50 * L^2 * 1.01^(L-100)`.
  - L1: 50, L10: 5,000, L50: 125,000, L100: 500,000, L200: 5.4M, L500: 669M, L1000: 3.9e11.
- Enemy XP: `xpKill = 0.8 * Lenemy^2 * roleMult`. About 60 at-level fodder kills per level up to L100 (fewer with elites and quests), rising slowly after that because of the 1.01 term.
- Per level: +5 attribute points, +1 skill point. After L100 also +1 Ascension point.
- Level difference: XP and loot penalty if the enemy is more than 10 levels below you (`max(0.1, 1 - 0.07 * (gap - 10))`). Pushes players outward without blocking.

## Power curve (the balance trick)
Enemy power and gear power use the same exponential base so the ratio holds forever:
- Enemy HP: `hp(L) = 40 * 1.07^L * roleMult`
- Enemy damage: `dmg(L) = 6 * 1.07^L * roleMult`
- Item base stats: `base(ilvl) = k_slot * 1.07^ilvl`
- Player health from Grit and gear scales with the same 1.07^L.
Because both sides grow 7% per level, an even-level fight at L30 and at L3000 takes the same number of hits. The player's real edge comes from: enhancement, skill points and Endless nodes, Ascension points, item affixes and build synergy. Those are what "uncapped growth" buys you.

Worked example (Knight, at-level Rare sword, no enhancement):
| Level | Enemy fodder HP | Sword base dmg | Hits to kill fodder |
|---|---|---|---|
| 10 | 39 | 12 | 3 to 4 |
| 50 | 589 | 176 | 3 to 4 |
| 100 | 17,300 | 5,200 | 3 to 4 |
| 1000 | 4.6e30 | 1.4e30 | 3 to 4 |
Add +20 enhancement and 30 skill points and it drops to 1 to 2 hits. Walk one ring further and it goes back up. That is the loop.

## Percent stats saturate (soft caps without hard caps)
Crit chance, dodge, cooldown reduction, block chance and resistances use rating vs level:
`pct = cap * r / (r + k * Lenemy)`
| Stat | cap | k |
|---|---|---|
| Crit chance | 75% | 20 |
| Dodge | 50% | 30 |
| Cooldown reduction | 60% | 25 |
| Block chance (Knight) | 75% | 20 |
| Resistances | 85% | 15 |
More rating always helps, never reaches the cap, and deeper rings (higher Lenemy) need more rating. Crit damage and attack speed are flat additive with diminishing returns: `bonus = 2 * (1 - 1/(1 + r/1000))`, unbounded variant for deep Ascension: `+0.01 * log2(1 + r/1000)` per tier.

## Enhancement (+N, no cap)
- Stat bonus of +1 at level N: `step(N) = 0.10 / (1 + N/20)`. Total bonus `B(N) = sum step(n)` grows like `2 * ln(1 + N/20)`: +10 gives about +79%, +20 about +136%, +50 about +247%, +100 about +354%, +1000 about +782%. Never stops, always slower.
- Cost: `gold = 100 * 1.12^N * itemRarityMult`, materials: N <= 15 common mats, 16 to 30 Lumen Shards (Ring 3+), 31+ Deep Shards (Ring 6+). Ties enhancement to exploring further.
- No failure, no item loss, no downgrades.

## Skill ranks
- Skills rank up with points. Effect per rank: `+8% / (1 + rank/10)`. No max rank.
- Endless nodes (end of each tree): each point `+1% / (1 + n/25)` of their stat.

## Ascension (after level 100)
- One point per level. Boards: Might, Focus, Grit, Finesse, Fortune.
- Small linear nodes (+0.5% damage, +1% health) with no cap, and utility nodes with soft caps (+0.3% move speed per point, saturating at +30% via `30% * p / (p + 100)`).

## Rekindle (optional prestige, open question Q6)
- At level 150+, you may Rekindle: rings reset to explored but unlit, levels reset to 1, you keep gear looks, Ascension and a permanent Lantern multiplier `+10% XP and +5% damage per Rekindle`.

## Big numbers
- JS doubles are exact to 2^53 and reach 1.8e308. Level 1000 values are about 1e30, so doubles work until roughly level 10,400, where 1.07^L overflows.
- Display: 12.3K, 4.56M, 7.89B, then scientific (1.23e15) with a setting for letter suffixes.
- Plan for deep Ascension: switch stored HP and damage to log-space (`log10 value`) or break_infinity.js (MIT) behind a tiny Num module, from day one in the code so the swap is cheap.
- Balance tests: a script simulates a player and at-level enemies from L1 to L10,000 and fails CI if time-to-kill drifts more than 25%.
