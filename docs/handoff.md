# Handoff

Where Deepcell stands and what the next person (or agent) needs to know. Last updated 2026-11-07. Read with `AGENTS.md`, `docs/design.md` and `docs/roadmap.md`.

## State

- Playable base game: four Activities (title, game, survivors, settings), SQLite save, JSON balance, offline earnings, notifications. See `docs/roadmap.md` for done/next.
- Art: everything visible in play is a Blender render made from code (`tools/blender/`), exported as WebP to `res/drawable-nodpi/`. Panels and buttons are 9-patches from `tools/art/gen_ui.py`. Small inline icons (scrap, food, back, close, skull), notification icon and legacy launcher are vectors from `tools/art/gen_art.py`.
- Font: Barlow Condensed (`res/font/barlow.xml`, SIL OFL licence in `docs/licenses/`).
- Title screen: `ui/TitleSlideshow.kt` pans three camera shots and dips through pre-blurred copies between them. First try; the user was unsure about the idea and hasn't judged it yet.
- Commits so far: base app → graphics rework → rename to Deepcell → art scripts → Blender rework (`d7d12dd`) → lighting/frames/icons/logo/title pass (`c4319f0`). No remote.

## Art pipeline

1. Edit a script in `tools/blender/` (`room_dig.py`, `room_farm.py`, `shaft.py`, `surface.py`, `bunker.py`, `sprites.py`, `icons.py`, `logo.py`, `title_shots.py`; shared helpers in `common.py` and `room_shell.py`).
2. Run it in Blender with `BL_DIR` set to the folder (see `tools/blender/README.md`). With the Blender MCP connector: `execute_blender_code` with `BL_DIR = r"C:/Users/Acer/Desktop/Deepcell/tools/blender"` then `exec(open(BL_DIR + "/room_dig.py").read())`.
3. `python tools/blender/export_to_app.py` (Pillow). It also adds survivor contact shadows, puts the bunker on the surface title shot and makes the blurred title copies.
4. Interface drawables: `python tools/art/gen_ui.py`; vectors: `python tools/art/gen_art.py`. Both overwrite their files, so edit the scripts, not the outputs.
5. `gradlew assembleDebug`, install on the emulator, screenshot, record in `docs/testing.md`.

Look rules that came from the user's feedback:
- Dark, lamp-lit, few strong light sources with visible cones; areas between lamps stay dark. Focus matters more than detail.
- Everything at eye level / front-on (rooms, bunker, surface). No top-down views.
- Exterior is dusk: dark silhouettes with a warm rim from the sun behind; objects are lit by their own lamps, not daylight.
- Each cell (room, shaft segment) has a black frame. Characters need contact shadows.
- Stylized: chunky bevelled shapes, banded toon light, dark outlines, cool rim light. No pixel art (the user ruled it out).

## Gotchas

- Each Blender script builds its own scene and calls `base_materials()`. Materials are shared by name across scenes, so always re-run the script you are rendering; don't render an old scene in a saved file.
- Room renders are 2.5:1, the shaft 0.4:1, with the same vertical frame so the landing meets the room floor. Workers stand on the left third; labels sit in the top corners.
- Bunker deck is at about 47% of the image height; `roofCrew` marginTop (21dp) and the sky's bottom margin (80dp) depend on it. Re-check both if the bunker changes.
- `room_dig_auto` is the same room with the Drill Rig; the adapter swaps images when the room is automated.
- The Blender MCP addon was one protocol version behind (works; update with `uvx mcp-for-blender install-addon`). The asset libraries and 3D generators are off; all models are code-built.
- Windows / Git Bash: run adb with `-s emulator-5554` (the user's Pixel 7 is also connected over wireless debugging). Use `MSYS_NO_PATHCONV=1` for `adb shell` paths. Long heredocs in Bash sometimes fail; write a script file and run it instead.
- Emulator AVD: `Medium_Phone` (API 37). `svc power stayon true` keeps it awake for screenshots.

## User preferences

- **Do not install on the user's phone unless they ask.** They asked once (the Blender rework build); the latest build is only on the emulator.
- Each round of feedback becomes its own commit.
- No taglines, filler text or fake features in the UI.
- Show work as screenshots; be honest about what wasn't checked.

## Not verified / open

- Settings screen in the new style, Drill Rig room in play, boss sprite in play, launcher icon on a home screen, Android 7 (font fallback below API 26), small screens.
- Characters are simple and only tween-animated (hop, sway). Organic shapes (creatures, faces) are the weak spot of code-built models.
- Mushroom Farm automation, Lift, more floors: see `docs/roadmap.md`.
