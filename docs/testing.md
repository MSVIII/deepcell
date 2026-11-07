# Testing

Record each build and test here, newest first. Say plainly what was not tested.

## 2026-11-07: Blender art rework

- `gradlew assembleDebug`: **BUILD SUCCESSFUL**. `gradlew lintDebug`: 0 errors, 33 warnings (none new from the art).
- Installed on the `Medium_Phone` emulator (API 37). Title screen checked by screenshot: rendered surface and bunker, slate panel, key-chip buttons.
- Game screen checked from a screenshot of the emulator: HUD with rendered icons and wave pill, surface with bunker and roof guard, scout drone falling, Scrap Dig and Mushroom Farm renders with worker, payout labels, round tabs.
- Installed on the user's Pixel 7 over wireless debugging at the user's request, and launched. Not tested further there.
- Not checked: the upgrade sheet, Survivors and Settings screens in the new style, the Drill Rig room image, the boss and bomber sprites in play.

## 2026-11-07: renamed to Deepcell

- `gradlew assembleDebug`: **BUILD SUCCESSFUL** with package `com.deepcell.game`.
- Emulator `Medium_Phone` (API 37): the old `com.burrownine.game` build was uninstalled first. The Deepcell launch screen, title (DEEP / CELL, new emblem) and game screen show correctly. A new game starts as "Bunker Nine". No crashes in `logcat -b crash`.
- Not re-checked after the rename: Survivors, Settings, notifications (no code changed there besides the package name). Not installed on a real phone.

## 2026-11-07: graphics and UI rework

- `gradlew assembleDebug`: **BUILD SUCCESSFUL**. `gradlew lintDebug`: 0 errors (new warnings: large vector backgrounds, explained in `docs/decisions.md`).
- Installed on the `Medium_Phone` emulator (API 37). **Not installed on a real phone.**

| Check | Result |
|---|---|
| Title screen: emblem, title, field, buttons, bunker on the horizon | Pass (screenshot) |
| Game screen: HUD chips, wave badge, bunker with roof guard, enemies falling and drifting to the bunker | Pass (screenshot) |
| Rooms: B1/B2 plates, room art, worker figure, payout label, progress bar fills when the room is tapped | Pass (screenshot) |
| Defense tab opens the upgrade sheet with icons, level bars, price buttons; tab highlighted | Pass (screenshot) |
| Survivors screen: figures by job, job chips, food chip, recruit row | Pass (screenshot) |
| Settings screen: card with Switch and Spinner, Share, Reset save card | Pass (screenshot) |
| No crashes in `logcat -b crash` | Pass |

Not checked after the rework: the "+N" popup animation (it plays too fast for screenshots), the Drill Rig machine art in the room, the tab-toggle close, the boss skull icon, the new notification icon, small screens.

## 2026-11-07: base app

### Build

- `gradlew assembleDebug`: **BUILD SUCCESSFUL** (Gradle 9.6.0, AGP 9.4.1, JDK 17, Android SDK 37). APK: `app/build/outputs/apk/debug/app-debug.apk`.
- `gradlew lintDebug`: 0 errors. Remaining warnings are deliberate: platform `Switch` (Module 6) instead of SwitchCompat, portrait lock, plural suggestions, KTX `transaction {}` suggestions.

### Emulator smoke test

Installed on the Android Studio emulator `Medium_Phone` (Android API 37). **Not installed on a real phone.**

| Check | Result |
|---|---|
| Title screen, bunker name, Play starts a new game | Pass |
| Continue enabled only when a save exists; save summary shows name and wave | Pass |
| Enemies spawn, fall (Handler loop), damage the hatch; waves advance | Pass |
| Dig: progress, full bar pays scrap; survivor in Scrap Dig adds +1 per tap | Pass |
| Buy upgrade: scrap spent, level and price update | Pass |
| "Not enough scrap" Toast | Pass |
| Bottom tabs switch the upgrade list | Pass |
| Survivors screen: list, tap changes job, "Not enough food" on recruit | Pass |
| Hatch breach: lost 25% scrap (10 → 8), hatch restored, same wave repeats, notification posted | Pass |
| Drill Rig: spinning gear on Scrap Dig, bar fills by itself | Pass |
| Offline earnings: app in background ~45 s, Toast "Drill Rig dug 25 scrap" on return | Pass |
| Settings: Sound switch value kept, difficulty Spinner opens, Share opens system chooser | Pass |
| Reset save: disabled until CheckBox ticked, then returns to title with no save | Pass |
| Status bar / navigation bar don't cover the HUD or tabs (targetSdk 37 edge-to-edge) | Pass, after adding `fitsSystemWindows` |
| No crashes in `logcat -b crash` during the run | Pass |

### Not tested

- Tapping an enemy to kill it (moving targets were hard to hit with scripted taps). Enemy kills by the Auto-Turret were not checked either; the Auto-Turret was not bought.
- Boss wave (wave 10) and its notification.
- Difficulty change actually changing enemy HP.
- Android 7–12 devices, small screens, tablets, a real phone.
- Database upgrade path (there is only version 1).
