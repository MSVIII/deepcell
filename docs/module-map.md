# Module map

Where the code uses each course module. Keep this table current when you add code.

| Module | Topic | Where it is used |
|---|---|---|
| 1 | Intro to Android | `AndroidManifest.xml`: app, 4 activities, launcher activity, permission |
| 2 | Android Studio | Standard Gradle project (Kotlin DSL): `settings.gradle.kts`, `build.gradle.kts`, `app/build.gradle.kts`, Gradle wrapper |
| 3 | Kotlin | All code. Data classes in `model/Models.kt` (`Upgrade`, `Floor`, `EnemyType`, `Enemy`, `Wave`, `Survivor`, `GameState`); `object` singletons (`JsonLoader`, `Notifier`, `DbContract`); lambdas for adapter callbacks; `when`, collections, null safety |
| 4 | Components and resources | `res/values/strings.xml` (all UI text, string-array for difficulty), `colors.xml`, `themes.xml` (dark theme + text styles), `res/drawable/` (vector placeholders, gradient/selector/layer-list shapes), `res/drawable-v26/ic_launcher.xml` (adaptive icon), `res/anim/` (`hit_flash`, `hatch_shake`, `shake_cycle`, `gear_spin`), `assets/` (`upgrades.json`, `waves.json`) |
| 5 | Activities and lifecycle | `MainActivity`, `GameActivity`, `SurvivorsActivity`, `SettingsActivity`. `GameActivity.onResume` loads the save, adds offline earnings and starts the Handler loop; `onPause` stops the loop and saves; `onDestroy` closes the database. `MainActivity.onResume` refreshes the Continue button |
| 6 | Android UI | Layouts: LinearLayout (all screens), RelativeLayout (game HUD), FrameLayout (sky, floor icon + gear), TableLayout (settings). Widgets: ListView (floors, upgrades, survivors), Button, ImageButton (bottom tabs, gear), ImageView (enemies, hatch), TextView, EditText (bunker name, recruit name), CheckBox (reset confirm), Switch (sound), Spinner (difficulty), ProgressBar (hatch health, floor progress). onClick listeners throughout. `Handler` + `Runnable` game loop in `GameActivity` |
| 7 | Intents | Explicit: Main → Game (`EXTRA_NEW_GAME`, `EXTRA_BUNKER_NAME`), Game → Survivors (`EXTRA_BUNKER_NAME`), Game → Settings (`EXTRA_BUNKER_NAME`, `EXTRA_WAVE`), Settings → Main after reset. Extras read with `intent.extras`. Implicit: Share button in `SettingsActivity` uses `ACTION_SEND` with a chooser |
| 8 | Notifications | Toasts in all activities. `ui/Notifier.kt`: `NotificationChannel` (API 26+), `NotificationCompat.Builder`, `PendingIntent` back to `GameActivity`, `NotificationManagerCompat.notify`. Sent on boss wave cleared and hatch breached |
| 9 | SQLite | `data/GameDatabase.kt`: `DbContract` contract object, `SQLiteOpenHelper`, tables `game_state`, `upgrades`, `automation`, `survivors`, `settings`; `ContentValues`, `insert`, `insertWithOnConflict`, `update`, `delete`, `query`, `Cursor`; transactions for multi-table saves |
| 10 | JSON parser | `data/JsonLoader.kt` reads `assets/upgrades.json` and `assets/waves.json` with `JSONObject` / `JSONArray` |

## Used but not a module topic

These are small, needed by Android itself, and explained in `docs/decisions.md`:

- `AppCompatActivity` and `Theme.AppCompat` (from the default Android Studio template).
- `BaseAdapter` for the floor and upgrade rows, and `ArrayAdapter` for the survivor list and Spinner. These are how a ListView or Spinner gets its rows.
- Android 13+ `POST_NOTIFICATIONS` runtime permission request in `MainActivity`. Without it, notifications don't appear on new phones.
- `Animation` / `AnimationUtils.loadAnimation` to play the `res/anim` tweens.
- `kotlin.random.Random` for the enemy spawn position.
