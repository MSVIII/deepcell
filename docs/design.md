# Deepcell: game design

Status of each part is in `docs/roadmap.md`. This file is the agreed concept plus the exact rules the base app uses.

## Premise

Deepcell is post-apocalyptic. A solar storm reawakened an old automated air-defense network. Its drones, together with mutated birds called Shrikes, attack anything on the surface. Survivors live in a poor underground bunker, Bunker Nine by default (the player can rename it).

## Core theme: automation

The bunker starts poor, so everything is manual:

| Manual job | Machine that automates it | In base app |
|---|---|---|
| Tap enemies to shoot | Auto-Turret | Yes |
| Tap Dig in Scrap Dig | Drill Rig | Yes |
| Tap Harvest in Mushroom Farm | Sprinkler / Auto-Harvester | Planned |
| Move resources between floors | Lift | Planned |
| Tap the hatch to repair | Repair Arm | Planned |
| (end goal) | Core Restored | Planned |

Only automated rooms earn while the app is closed.

## Screen layout (vertical phone)

Top to bottom:

1. HUD: Scrap and Food counters (icons, no labels), wave badge (skull on boss waves), and a gear button for Settings.
2. Surface: storm sky with a ruined skyline. Enemies come down from the top and drift towards our bunker, which sits on the ground at the bottom of the surface. Survivors on the Roof job stand guard on the bunker deck. A label in the top-left shows the bunker name and hatch health.
3. Underground: a side-on cutaway of the bunker. A lift shaft runs down the left side with floor plates (B1, B2). Each room shows its wall, props, the survivors working there, its payout (for example +5 scrap), and a progress bar. Tap the room itself to work it. Automated rooms show their machine and a spinning gear. Earth continues below the deepest room.
4. Bottom tabs: Defense, Supplies, Automation open an upgrade sheet over the rooms (tap the tab again or ✕ to close). Survivors opens the Survivors screen.

The art style is flat vector: soot, concrete, rust, sodium-lamp amber, toxic green. Interface text is kept to names and numbers.

## Resources

- **Scrap**: earned from killed enemies and from Scrap Dig. Pays for upgrades and repairs.
- **Food**: earned from Mushroom Farm. Pays for recruiting survivors.

No other resources.

## Survivors

Each survivor has one job:

- **Roof**: +1 damage on every manual tap on an enemy.
- **Scrap Dig** or **Mushroom Farm**: +1 progress on every manual tap in that room.

Survivors make manual work stronger; they do not earn anything while the app is closed. Survivors are never killed. A new game starts with Mara (Roof) and Tobin (Scrap Dig). Recruiting costs 15 food; new survivors start in Scrap Dig. Tap a survivor in the Survivors screen to move them to the next job.

## Enemies

| Enemy | HP | Speed (dp/s) | Hatch damage | Scrap reward |
|---|---|---|---|---|
| Scout Drone | 2 | 45 | 5 | 2 |
| Shrike | 1 | 80 | 3 | 2 |
| Bomber Drone | 6 | 25 | 20 | 6 |
| Command Drone (boss) | 40 | 12 | 60 | 50 |

The numbers live in `assets/waves.json`.

## Waves

- `waves.json` defines a 10-wave cycle. Wave 10 has the boss, so every 10th wave is a boss wave.
- Wave *n* uses cycle entry (n − 1) mod 10. Each full cycle adds 50% enemy HP (`hpScalePerCycle`).
- Difficulty multiplies enemy HP: Easy ×0.75, Normal ×1, Hard ×1.5.
- Enemies spawn one at a time, every `spawnMs`. There is a 2-second break before each wave.
- A wave is cleared when every enemy has spawned and none are left. Clearing a boss wave sends a notification.

## Combat

- **Manual shot**: tap an enemy. Damage = 1 + Sharpened Rounds level + survivors on the Roof.
- **Auto-Turret**: once per second, hits the enemy closest to the hatch. Damage = turret level.
- An enemy that reaches the bottom of the sky hits the hatch for its damage and disappears.

## Hatch and losing

- Max hatch health = 100 + 20 per Hatch Plating level. Buying plating also adds 20 to current health.
- Tap the bunker to repair the hatch: 1 scrap for +5 health.
- **Breach**: when hatch health reaches 0, the bunker loses 25% of its scrap (rounded down), the sky is cleared, the hatch is restored to full, and the same wave starts again. A notification is sent. Nothing else is lost.

## Floors

| Floor | Full bar | Pays | Manual tap adds | Machine |
|---|---|---|---|---|
| Scrap Dig | 10 | 5 scrap | 1 + Better Shovels level + diggers | Drill Rig: +level progress per second |
| Mushroom Farm | 10 | 3 food | 1 + Spore Trays level + farmers | none yet |

## Upgrades

From `assets/upgrades.json`. Price of the next level = baseCost × costGrowth^level, rounded.

| Tab | Upgrade | Effect | Base cost | Growth | Max |
|---|---|---|---|---|---|
| Defense | Sharpened Rounds | +1 tap damage | 10 | 1.6 | 10 |
| Defense | Hatch Plating | +20 max hatch health | 15 | 1.7 | 10 |
| Supplies | Better Shovels | +1 dig progress per tap | 8 | 1.5 | 10 |
| Supplies | Spore Trays | +1 farm progress per tap | 8 | 1.5 | 10 |
| Automation | Auto-Turret | auto shot each second, damage = level | 40 | 2.0 | 5 |
| Automation | Drill Rig | fills Scrap Dig, speed = level, works offline | 50 | 2.0 | 5 |

## Offline earnings

When the game screen resumes, the app counts the seconds since it was last paused (capped at 8 hours). Only automated rooms earn for that time. In the base app, that is the Drill Rig: seconds × Drill Rig level progress goes into Scrap Dig. Enemies don't attack while the app is closed.

## Feedback

- Toasts: purchases, "Not enough scrap", wave cleared, breach, offline earnings.
- Notifications: boss wave cleared, hatch breached.
- Animations: enemy flash on hit, hatch shake on damage, spinning gear on automated rooms.

## Originality

Deepcell must stay an original game. Don't copy names, art, UI, or level layouts from Fallout Shelter, Idle Miner Tycoon, Grow Castle, or other games.
