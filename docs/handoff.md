# Handoff

Where Deepcell stands and what the next person (or agent) needs to know. Last updated 2026-11-07 (animation, effects and sound pass). Read with `AGENTS.md`, `docs/design.md` and `docs/roadmap.md`.

## State

- Playable base game: four Activities (title, game, survivors, settings), SQLite save, JSON balance, offline earnings, notifications. See `docs/roadmap.md` for done/next.
- Art: everything visible in play is a Blender render made from code (`tools/blender/`), exported as WebP to `res/drawable-nodpi/`. Panels and buttons are 9-patches from `tools/art/gen_ui.py`. Small inline icons (scrap, food, back, close, skull), notification icon and legacy launcher are vectors from `tools/art/gen_art.py`.
- Font: Barlow Condensed (`res/font/barlow.xml`, SIL OFL licence in `docs/licenses/`).
- Animation: survivors, guards and enemies are rendered frame loops (`AnimationDrawable`), effects are rendered flipbooks (`ui/Fx.kt` plays both). Sounds are synthesised (`tools/audio/gen_sfx.py`) and played by `ui/Sfx.kt` (SoundPool).
- Title screen: `ui/TitleSlideshow.kt` pans three camera shots and dips through pre-blurred copies between them. First try; the user was unsure about the idea and hasn't judged it yet.
- Commits so far: base app → graphics rework → rename to Deepcell → art scripts → Blender rework (`d7d12dd`) → lighting/frames/icons/logo/title pass (`c4319f0`) → animation, effects, sound, easing (`d85c019`). No remote.

## Art pipeline

1. Edit a script in `tools/blender/` (`room_dig.py`, `room_farm.py`, `shaft.py`, `surface.py`, `bunker.py`, `sprites.py`, `anim_sprites.py`, `vfx.py`, `icons.py`, `logo.py`, `title_shots.py`; shared helpers in `common.py` and `room_shell.py`).
2. Run it in Blender with `BL_DIR` set to the folder (see `tools/blender/README.md`). With the Blender MCP connector: `execute_blender_code` with `BL_DIR = r"C:/Users/Acer/Desktop/Deepcell/tools/blender"` then `exec(open(BL_DIR + "/room_dig.py").read())`.
3. `python tools/blender/export_to_app.py` (Pillow). It also adds survivor contact shadows, puts the bunker on the surface title shot, makes the blurred title copies, and writes the frame sequences plus their `animation-list` XML (`anim_*.xml`, `fx_*.xml`, frame timings live in its `ANIMS` table). `--frames` exports only the frames (the full export takes about two minutes).
4. Sounds: `python tools/audio/gen_sfx.py` (numpy, ffmpeg) writes `res/raw/sfx_*.ogg`.
5. Interface drawables and tween animations: `python tools/art/gen_ui.py`; vectors: `python tools/art/gen_art.py`. Both overwrite their files, so edit the scripts, not the outputs.
6. `gradlew assembleDebug`, install on the emulator, screenshot, record in `docs/testing.md`.

Look rules that came from the user's feedback:
- Dark, lamp-lit, few strong light sources with visible cones; areas between lamps stay dark. Focus matters more than detail.
- Everything at eye level / front-on (rooms, bunker, surface). No top-down views.
- Exterior is dusk: dark silhouettes with a warm rim from the sun behind; objects are lit by their own lamps, not daylight.
- Each cell (room, shaft segment) has a black frame. Characters need contact shadows.
- Workers work in the room's work zone (scrap heap, grow tables), not off to the side. Roof guards stand on the deck.
- Movement eases in and out; avoid constant-speed slides.
- Stylized: chunky bevelled shapes, banded toon light, dark outlines, cool rim light. No pixel art (the user ruled it out).

## Gotchas

- Each Blender script builds its own scene and calls `base_materials()`. Materials are shared by name across scenes, so always re-run the script you are rendering; don't render an old scene in a saved file.
- Room renders are 2.5:1, the shaft 0.4:1, with the same vertical frame so the landing meets the room floor. Workers stand on the left third; labels sit in the top corners.
- Bunker deck surface is at about 49% of the image height and the hatch top at about 30%; `GameActivity` (`GUARD_SLOTS`, `DECK_Y`, `HATCH_Y`) and the sky's bottom margin (84dp) depend on them. Re-check if the bunker render changes.
- Work zones are fractions of the room render (`FloorAdapter`: `HEAP_X`, `TABLES_X`). Re-check if a room render changes.
- Blender treats a trailing `.13` in an object name as a duplicate number. `anim_sprites.py` empties earlier sprite scenes before each build so part names stay exact.
- Pure emission brighter than about 1.3 renders flat white (Standard view transform); keep effect colours low to keep their hue.
- Screenshots are too slow to catch effects; use `adb shell screenrecord` and pull frames with ffmpeg.
- `room_dig_auto` is the same room with the Drill Rig; the adapter swaps images when the room is automated.
- The Blender MCP addon was one protocol version behind (works; update with `uvx mcp-for-blender install-addon`). The asset libraries and 3D generators are off; all models are code-built.
- Windows / Git Bash: run adb with `-s emulator-5554` (the user's Pixel 7 is also connected over wireless debugging). Use `MSYS_NO_PATHCONV=1` for `adb shell` paths. Long heredocs in Bash sometimes fail; write a script file and run it instead.
- Emulator AVD: `Medium_Phone` (API 37). `svc power stayon true` keeps it awake for screenshots.

## User preferences

- **Do not install on the user's phone unless they ask.** They asked once (the Blender rework build); the latest build (animation and sound) is only on the emulator.
- Each round of feedback becomes its own commit.
- Wants game-feel: animation, effects, sound, eased motion.
- No taglines, filler text or fake features in the UI.
- Show work as screenshots; be honest about what wasn't checked.

## Not verified / open

- Sounds not yet heard by the user; upgrade sheet slide and button pop not recorded; several guards or four workers at once not seen.
- Settings screen in the new style (now seen, with the Main menu button), Drill Rig room in play, boss sprite in play, launcher icon on a home screen, Android 7 (font fallback below API 26), small screens.
- Characters have short loops only (work, idle, fire); no walking. Organic shapes (creatures, faces) are the weak spot of code-built models.
- Sounds were generated without being listened to by the author; the user should judge them.
- Open design question: should workers fill the room by themselves (with the player tapping to collect the finished pile until a Collector exists)? For now tapping does both, as before.
- Mushroom Farm automation, Lift, more floors: see `docs/roadmap.md`.
