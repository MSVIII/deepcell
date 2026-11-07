# Art generators

All Deepcell art is vector drawables written by these two scripts. They are tools for the team, not part of the app: they only write XML files in `app/src/main/res`. Nothing here is built into the APK.

| Script | Writes |
|---|---|
| `gen_art.py` | `res/drawable/`: bunker, skyline, rooms, props, enemies, survivors, icons, logo, launcher and notification icons |
| `gen_ui.py` | `res/drawable/` shapes (buttons, panels, tabs, progress bars, lift shaft), `res/anim/` (`work_bob`, `float_up`, `antenna_blink`), `res/values/dimens.xml` |

## Use

Requires Python 3. From the project folder:

```bash
python tools/art/gen_art.py
```

```bash
python tools/art/gen_ui.py
```

Then rebuild the app.

- The scripts **overwrite** the files they generate. If you hand-edit one of those files, make the same change in the script, or it will be lost on the next run.
- Files the scripts don't write (for example `hit_flash.xml`, `hatch_shake.xml`, `gear_spin.xml`, `colors.xml`, `themes.xml`) are edited by hand.
- To replace an image with hand-drawn art, keep the file name and stop generating it: delete its `vec(...)` call.
