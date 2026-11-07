# Burrow Nine

An Android game for our Mobile Programming group project. A solar storm woke up an old automated air-defense network, and its drones attack anything on the surface. You run a poor underground bunker: shoot drones by tapping, dig scrap and grow food by hand, then build machines that do those jobs for you.

Kotlin + XML layouts. No third-party libraries. See `docs/design.md` for the game and `docs/module-map.md` for which course module each part uses.

## Open in Android Studio

1. Android Studio → **File → Open** → choose this `BurrowNine` folder (the one with `settings.gradle.kts`).
2. Wait for Gradle sync to finish. Android Studio creates `local.properties` with your SDK path. That file is not committed, because the path is different on each PC.
3. Pick a phone or an emulator and press **Run**.

Requirements: Android Studio with Android SDK 37 installed (Settings → Languages & Frameworks → Android SDK). The app runs on Android 7.0 (API 24) and newer.

## Build from the command line

Windows:

```bash
gradlew.bat assembleDebug
```

macOS / Linux:

```bash
./gradlew assembleDebug
```

The APK is written to `app/build/outputs/apk/debug/app-debug.apk`. If Gradle can't find the SDK, create `local.properties` with one line, for example `sdk.dir=C\:/Users/YOU/AppData/Local/Android/Sdk`.

## Project layout

```
app/src/main/
  java/com/burrownine/game/
    MainActivity.kt        title screen: bunker name, Play, Continue
    GameActivity.kt        the game screen and the Handler game loop
    SurvivorsActivity.kt   survivor list, jobs, recruiting
    SettingsActivity.kt    sound, difficulty, reset save, share
    model/Models.kt        data classes: Upgrade, Floor, Enemy, EnemyType, Wave, Survivor, GameState
    data/GameDatabase.kt   SQLiteOpenHelper: the save file
    data/JsonLoader.kt     reads assets/upgrades.json and assets/waves.json
    ui/FloorAdapter.kt     ListView rows for underground floors
    ui/UpgradeAdapter.kt   ListView rows for upgrades
    ui/Notifier.kt         notification channel + NotificationCompat
  assets/                  upgrades.json, waves.json (game balance)
  res/                     layouts, strings, colors, themes, drawables, anim
docs/                      design, module map, roadmap, decisions, testing
AGENTS.md                  rules for AI coding assistants
```

## Working as a group

- Read `AGENTS.md`; the same rules apply to people.
- Balance changes go in `assets/*.json`; text goes in `res/values/strings.xml`.
- Never change `GameDatabase.onUpgrade` so it drops tables. It would delete everyone's saves.
- Update the docs in `docs/` with your change.
