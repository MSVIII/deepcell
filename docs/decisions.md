# Decisions

Why the base app is built the way it is. Add a dated entry when the group decides something.

## 2026-11-07: base app

- **Course modules only.** The professor said to use only what the modules covered. See `AGENTS.md` and `docs/module-map.md`.
- **Dependencies: only `androidx.appcompat` and `androidx.core`.** Both are in every new Android Studio project. `androidx.core` provides `NotificationCompat`, which Module 8 uses. No other libraries.
- **Android Gradle Plugin 9.4.1, Gradle 9.6.0, compileSdk/targetSdk 37, minSdk 24.** AGP 9 compiles Kotlin by itself, so there is no separate Kotlin plugin. These versions match the SDK installed on the setup PC. If a groupmate's Android Studio is older, update Android Studio rather than downgrading the project.
- **Views move with `translationY`, driven by a `Handler`.** The modules don't cover Canvas or SurfaceView, so enemies are ImageViews inside a FrameLayout. The loop runs about every 33 ms. This is fine for a few dozen enemies; don't spawn hundreds.
- **One loop, two speeds.** Movement and spawning run every frame. Machines (Auto-Turret, Drill Rig) run once per second, so their strength is easy to read: "level = damage per second" or "level = progress per second".
- **Save in `onPause`, load in `onResume`.** Survivors and Settings write straight to SQLite, so the game screen reloads everything when it comes back. Purchases also save immediately.
- **Offline earnings use the last-pause time.** The same time is used when coming back from the Survivors or Settings screen, so automation keeps working for those few seconds too. Offline time is capped at 8 hours.
- **Enemies on screen are not saved.** If Android closes the app, the current wave restarts from the beginning. This keeps the save simple.
- **Breach keeps it simple.** Lose 25% scrap, restore the hatch, repeat the wave. Survivors are never killed.
- **Survivors only boost manual work.** This keeps the automation theme clear: only machines earn while you're away.
- **Reset save needs a CheckBox.** Deleting a save can't happen with one accidental tap. Play over an existing save needs a second tap for the same reason.
- **Settings are stored in SQLite, not SharedPreferences.** SharedPreferences isn't in the modules; a small `settings` table is. Reset save keeps the settings.
- **`POST_NOTIFICATIONS` permission request.** Not a module topic, but on Android 13+ notifications don't show without it. It is one call in `MainActivity`.
- **Platform `Switch` instead of `SwitchCompat`.** Module 6 teaches `Switch`.
- **Portrait only.** The layout follows the vertical sketch.
