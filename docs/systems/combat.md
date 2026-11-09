# Combat

## Controls
| Action | Keyboard + mouse | Gamepad |
|---|---|---|
| Move | WASD | Left stick |
| Aim | Mouse | Right stick (auto-aim assist 10 degrees) |
| Basic attack | Left click | RT |
| Secondary | Right click | LT |
| Skills 1 to 4 | 1 to 4 | A B X Y (with RB held: second bar) |
| Dodge roll | Space | LB |
| Potion | Q | D-pad up |
| Interact | E | D-pad down / A out of combat |

## Timing
- Dodge roll: 0.35 s, 0.25 s i-frames, 0.8 s cooldown (Ranger 0.6 s).
- Enemy telegraphs: 0.4 s (fodder) to 0.8 s (elite) wind-up with a ground marker in Spark Orange.
- Hit-stop: 40 ms light, 70 ms heavy, 120 ms boss stagger. Screen shake 1 to 3 px, slider in settings.
- Feel checks in CI like Paginated Bear's feel-check script: dodge i-frames, input buffer (120 ms), attack cancel windows.

## Damage
`hit = weaponBase * (1 + attributeScaling) * skillCoefficient * (1 + sum(increased%)) * prod(more multipliers) * critMult * (1 - enemyResist)`
- Types: Physical, Fire, Frost, Lightning, Lumen, Nature.
- Crit: chance and damage from rating vs level (progression.md). Base crit multiplier 1.5x.
- Armor: `damageTaken = hit * 100 / (100 + armor / (5 * attackerLevel))`.
- Status: Burn (DoT), Chill (slow, stacks to Freeze), Shock (damage taken up), Overgrown (root, Bloom), Overheat (Tinker self-status).

## Enemy roles
| Role | HP x | Damage x | Behavior |
|---|---|---|---|
| Fodder | 0.5 | 0.6 | swarm, simple chase |
| Brute | 2.5 | 1.4 | slow, big telegraphed slam |
| Ranged | 0.8 | 1.0 | keeps 6 to 9 tiles away, strafes |
| Charger | 1.2 | 1.3 | line-up, telegraphed charge, stun on wall hit |
| Support | 0.9 | 0.5 | shields or heals allies, priority target |
| Elite | 4 + 1 affix | 1.6 | role + affix |
| Boss | 30 to 60 | 2.0 | 3 phases, arena hazards |

## Defeat effects (no blood)
- Automatons: sparks + bolts scatter + pixel burst (pixelfx spawn/disintegrate, impacts/bullet-impact).
- Bloomtouched: petals and spores drift off, the animal shakes and runs away (custom, based on weather/falling-leaves).
- Crowfeather: smoke poof, they flee (spawn/poof).
- Iron Choir: dissolve into light (spawn/disintegrate in Lumen palette).
- Loot pops out with spawn/coin-drop.
- Player: "knocked out", screen fades to the lantern, wake at the last waylamp.
