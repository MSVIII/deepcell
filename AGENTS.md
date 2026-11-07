# Deepcell: rules for AI agents

This is a school group project for a Mobile Programming course. The professor allows only what the course modules covered. Read `docs/design.md` (the game) and `docs/module-map.md` (which module each piece of code uses) before changing anything.

## Allowed

Use only topics from the 10 course modules:

1. Intro to Android
2. Android Studio
3. Kotlin
4. Application components and resources: drawable, anim, strings, colors, styles, assets
5. Activities and the activity lifecycle
6. Android UI: LinearLayout, RelativeLayout, FrameLayout, TableLayout; ListView, GridView, Button, ImageButton, TextView, EditText, CheckBox, RadioButton, Switch, ToggleButton, Spinner, ProgressBar; onClick listeners; Handler
7. Intents, explicit and implicit, with putExtra / getExtras
8. Notifications: Toast, NotificationCompat, NotificationChannel, PendingIntent
9. SQLite (SQLiteOpenHelper, ContentValues, Cursor)
10. JSON parsing with JSONObject and JSONArray

## Not allowed

- No third-party libraries. The only dependencies are `androidx.appcompat` and `androidx.core`, which a new Android Studio project already includes. Ask the group before adding any other dependency.
- No Jetpack Compose, Fragments, Room, coroutines, RecyclerView, ViewModel/LiveData, Canvas/custom drawing, SurfaceView, or game engines.
- No Java files. Kotlin only, with XML layouts.

## How to work

- Keep it simple. Prefer short, readable code with comments over clever code. Groupmates fork this base.
- Put text in `strings.xml`, colors in `colors.xml`, and balance numbers in `assets/*.json`. Don't hard-code them in Kotlin.
- No filler text, slogans, or fake features in the UI. If a control does nothing yet, say so in `docs/roadmap.md`.
- The game must stay original. Don't copy names, art, or layouts from Fallout Shelter, Idle Miner, Grow Castle, or other games.

## Player saves

- Never wipe player saves in a database upgrade. `GameDatabase.onUpgrade` must not drop tables. When you add a column, bump `DB_VERSION` and add an `ALTER TABLE ... ADD COLUMN ... DEFAULT ...` step.
- Saves that change several tables (purchases, recruiting) go in one transaction.
- Only the Reset save button in Settings and Play-over-an-existing-save (after a second tap) delete a save.

## Docs must stay accurate

Update these whenever the code changes:

- `docs/design.md`: game rules
- `docs/module-map.md`: module → code table
- `docs/roadmap.md`: what is done and what is next
- `docs/decisions.md`: why things are the way they are
- `docs/testing.md`: what was built and tested, with dates. Say plainly what was not tested.

Run `gradlew assembleDebug` after code changes and record the result in `docs/testing.md`. Don't claim something was tested on a device unless it was.
