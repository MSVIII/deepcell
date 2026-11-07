# Art generators

The vector icons and interface drawables are written by these two scripts. Scenes, characters and enemies are Blender renders: see [`../blender/`](../blender/README.md). They are tools for the team, not part of the app: they only write XML files in `app/src/main/res`. Nothing here is built into the APK.

| Script | Writes |
|---|---|
| `gen_art.py` | `res/drawable/`: icons, logo, launcher and notification icons, earth footer |
| `gen_ui.py` | `res/drawable-xxhdpi/` 9-patch panels and key-chip buttons, `res/drawable/` selectors and shapes (buttons, tabs, progress bars, overlays), `res/anim/` (`work_bob`, `float_up`, `antenna_blink`, `lamp_flicker`, `idle_sway`), `res/values/dimens.xml` |

## Use

Requires Python 3 (and Pillow for `gen_ui.py`). From the project folder:

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
