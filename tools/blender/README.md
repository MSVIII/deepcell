# Blender scenes

The rooms, lift shaft, surface, bunker, survivors, enemies, icons, logo and title shots are rendered in Blender. Every scene is built from code here: no imported models and no image textures. Nothing in this folder goes into the APK; only the exported WebP files do.

| Script | Renders |
|---|---|
| `common.py` | Shared helpers: scenes, toon materials (procedural rust/grime, banded light, rim), shapes, lights, camera, render |
| `room_shell.py` | The room box shared by all rooms (walls, floor plates, beams, pipes, lamps) |
| `room_dig.py` | `room_dig.png`, `room_dig_auto.png` (with the Drill Rig) |
| `room_farm.py` | `room_farm.png` |
| `shaft.py` | `shaft.png` (lift shaft beside each room) |
| `surface.py` | `surface.png` (sky, ruins, rubble) |
| `bunker.py` | `bunker.png` (transparent) |
| `sprites.py` | survivors, enemies, `icon_scrap`, `icon_food` (transparent) |
| `anim_sprites.py` | Animation frames: digger and farmer work loops, guard idle and fire, drone rotors, shrike wings (`*_0.png`, `*_1.png`, ...). Reuses the builders in `sprites.py` and poses them with empties |
| `vfx.py` | Effect flipbooks: `fx_explode`, `fx_dust`, `fx_spores`, `fx_sparks` |
| `icons.py` | tab, upgrade, settings and gear icons (transparent) |
| `logo.py` | `logo.png` (emblem + DEEPCELL wordmark) and `emblem.png` (launcher icon); uses `fonts/BarlowCondensed-ExtraBold.ttf` (SIL OFL) |
| `title_shots.py` | `title_surface/dig/farm.png`, portrait shots for the title slideshow |
| `render_all.py` | Runs all of the above |
| `export_to_app.py` | Resizes `out/*.png` and writes `app/src/main/res/drawable-nodpi/*.webp`; adds contact shadows under survivors, lays the bunker over the surface title shot, makes the blurred title copies, exports the animation frames and writes their `animation-list` XML (`--frames` for frames only) |

## Use

1. Open Blender (tested with 5.2). In the Text Editor, run:

   ```python
   BL_DIR = r"C:/path/to/Deepcell/tools/blender"
   exec(open(BL_DIR + "/render_all.py").read())
   ```

   Each script makes its own scene, so the default scene is not touched. Renders go to `tools/blender/out/` (not committed).
2. From the project folder (needs Python 3 with Pillow):

   ```bash
   python tools/blender/export_to_app.py
   ```

3. Rebuild the app.

To change one thing, edit its script and run just that script the same way, then export.

## Fitting the app

- Rooms are 2.5:1 and the shaft is 0.4:1, both with the same vertical frame, so the shaft landing lines up with the room floor.
- In rooms, workers stand on the left third and the labels sit in the top corners; keep those areas readable.
- The bunker's roof deck is where the Roof guards stand (`roofCrew` in `activity_game.xml`).
