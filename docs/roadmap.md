# Roadmap

## Done in the base app (2026-11-07)

- Project setup: Kotlin, XML layouts, Gradle Kotlin DSL, one `app` module, minSdk 24.
- 4 activities connected with explicit Intents and extras.
- Game screen in sketch order: HUD, sky, hatch, floors, upgrades, bottom tabs.
- Handler game loop: enemies fall, spawn per wave, auto machines tick once per second.
- Tap-to-shoot, manual Dig and Harvest, tap-to-repair hatch.
- 4 enemy types and a 10-wave cycle with a boss on wave 10, loaded from `waves.json`.
- 6 upgrades in 3 tabs, loaded from `upgrades.json`.
- Automation: Auto-Turret and Drill Rig.
- Breach rule: lose 25% scrap, repeat the wave.
- SQLite save: resources, upgrade levels, automation owned/level, survivors, wave, hatch health, floor progress, last-played time, settings.
- Offline earnings from automated rooms only.
- Survivors screen: jobs and recruiting.
- Settings: sound switch, difficulty spinner, reset save, share.
- Toasts, notifications, tween animations, placeholder vector art.

## Done in the graphics/UI rework (2026-11-07)

- Our bunker drawn on the surface, with roof guards; enemies drift towards it.
- Underground rooms as a side-on cutaway with a lift shaft, floor plates, room art, working survivors, payout label, "+N" popup, and the Drill Rig machine when automated.
- Upgrade sheet that opens from the bottom tabs, with upgrade icons and level bars.
- New icons, emblem/logo, launcher icon, monochrome notification icon, button and panel styles.
- Title, Survivors and Settings screens restyled; extra text removed.

## Known gaps

- **Sound**: the Sound switch is saved, but the game has no sound effects yet. Whoever adds sounds must check `GameDatabase.SETTING_SOUND`.
- **Food**: food is only used for recruiting. The group should decide whether survivors eat.
- **Art**: all art is code-drawn vectors. It is a consistent style, but a groupmate may replace it with hand-drawn art (keep the file names).
- Not yet tested on a real phone (see `docs/testing.md`).

## Next (suggested, not agreed)

1. Sprinkler / Auto-Harvester: automates Mushroom Farm, earns food offline.
2. Repair Arm: repairs the hatch slowly by itself.
3. Lift: decide what it does (for example, a bonus to all floor payouts) before building it.
4. More floors, unlocked with scrap.
5. Different boss per 10-wave cycle.
6. Core Restored: the end goal once every machine is built.
7. Sound effects that respect the Sound switch.
8. Final art.

Add a line to `docs/decisions.md` when the group agrees on any of these.
