# Testing

Record each build and test here, newest first. Say plainly what was not tested.

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
