# Workflow: tools, Blender MCP, testing

How Deepcell is built day to day, and how to set up the same tools on your PC. Everything here was used to make the base game. You only need the parts for what you change:

| You want to change | You need |
|---|---|
| Game code, layouts, balance (`assets/*.json`), text | Android Studio (section 1) |
| Art: rooms, characters, enemies, icons, title shots | + Python and Blender, ideally with the Blender MCP (sections 2 and 4) |
| Sound effects or music | + Python and ffmpeg (sections 2 and 5) |
| Interface panels, buttons, tweens | + Python (sections 2 and 6) |

The commands below are for Windows (PowerShell or Git Bash). On macOS/Linux use your package manager instead of `winget`.

## 1. Android Studio, emulator, phone

1. Install **Android Studio**, then in *Settings → Languages & Frameworks → Android SDK* install **SDK Platform 37** and the **Android Emulator**.
2. Open the project folder; Gradle sync writes `local.properties` with your SDK path.
3. *Device Manager → Create device* (any recent phone, e.g. Medium Phone) to get an emulator.
4. For your own phone: turn on *Developer options → USB debugging* (or *Wireless debugging*) and connect it.

Build and install from a terminal, which is what an AI assistant does:

```bash
./gradlew assembleDebug
adb devices                                   # lists the emulator and phones
adb -s emulator-5554 install -r app/build/outputs/apk/debug/app-debug.apk
adb -s emulator-5554 shell am start -n com.deepcell.game/.MainActivity
adb -s emulator-5554 exec-out screencap -p > shot.png
```

`adb` is in your SDK folder under `platform-tools` (on Windows `%LOCALAPPDATA%\Android\Sdk\platform-tools`). Always pass `-s <device>` when more than one device is connected, so nothing gets installed on a phone by mistake.

## 2. Python and command-line tools

| Tool | Used for | Install (Windows) |
|---|---|---|
| Git and GitHub CLI | cloning, commits, pushing, releases | `winget install Git.Git GitHub.cli` |
| Python 3.11+ | export, sound, music and UI scripts | `winget install Python.Python.3.12` |
| Python packages | Pillow (images), numpy and scipy (audio) | `pip install pillow numpy scipy` |
| ffmpeg (with libvorbis) | encoding sounds and music to OGG; frames from screen recordings | `winget install Gyan.FFmpeg` |
| Blender 5.x | rendering all art | `winget install BlenderFoundation.Blender` |
| uv | runs the Blender MCP server | `winget install astral-sh.uv` |

Open a new terminal after installing, so the new commands are on the PATH.

## 3. How a change goes (the loop we use)

1. Change the code, a JSON balance file, or an asset script.
2. If it's an asset: re-run its script, then `python tools/blender/export_to_app.py` for art.
3. `./gradlew assembleDebug`, install on the emulator, open the screen you changed, take a screenshot.
4. Update the docs (`docs/design.md`, `roadmap.md`, `decisions.md`, `testing.md`, and your `docs/forks/<you>.md`).
5. Commit with a clear message and push.

For short effects (explosions, sparks) a screenshot is too slow; record instead and pull frames:

```bash
adb -s emulator-5554 shell screenrecord --time-limit 8 /sdcard/clip.mp4
adb -s emulator-5554 pull /sdcard/clip.mp4
ffmpeg -i clip.mp4 -vf "fps=10,scale=360:-1,tile=6x3" -frames:v 1 frames.png
```

## 4. Art with Blender and the Blender MCP

All art is built by Python scripts in `tools/blender/` and rendered by Blender. The renders go to `tools/blender/out/` (not in git), then `export_to_app.py` resizes them into `app/src/main/res/drawable-*` and writes the frame-animation XML. See [`tools/blender/README.md`](../tools/blender/README.md) for what each script makes.

You can run the scripts by hand in Blender's Text Editor (the README shows how). With the **Blender MCP**, your AI assistant drives Blender directly: it runs the scripts, looks at the result and renders.

### Set up the Blender MCP

We use **MCP for Blender** (https://github.com/ahujasid/mcp-for-blender; the package used to be called `blender-mcp`).

1. Install Blender and `uv` (section 2).
2. Install the Blender add-on:
   ```bash
   uvx mcp-for-blender install-addon
   ```
   Or follow the add-on steps on the project page (*Edit → Preferences → Add-ons → Install from disk*, then enable it).
3. In Blender, open the 3D Viewport sidebar (press **N**), open the **MCP for Blender** tab and click **Connect to MCP server**. It listens on port 9876. Leave Blender open while you work.
4. Tell your AI assistant about the server.

   **Codex**: add this to `~/.codex/config.toml` (create the file if it doesn't exist), then restart Codex:
   ```toml
   [mcp_servers.blender]
   command = "uvx"
   args = ["mcp-for-blender"]
   # renders can take minutes; give tool calls time to finish
   tool_timeout_sec = 600
   ```
   **Claude Code**:
   ```bash
   claude mcp add blender -- uvx mcp-for-blender
   ```
5. Check it: ask the assistant to "get the Blender add-on status and scene info". It should answer with Blender's version.

The asset libraries and AI 3D generators in the add-on are not used: every model in Deepcell is built from code so it can be changed and re-rendered. Keep it that way.

### First render on a new clone

The renders aren't in git. `export_to_app.py` exports whatever is in `tools/blender/out/` and skips missing files, but render everything once anyway: it proves your setup matches before you change any art. Ask the assistant to run in Blender:

```python
BL_DIR = r"<full path to your clone>/tools/blender"
exec(open(BL_DIR + "/render_all.py").read())
```

This takes a while; the three title shots take minutes each. If the MCP call times out, Blender keeps rendering in the background: wait until the files in `tools/blender/out/` stop changing. You can also render the title shots one at a time by setting `TITLE_SHOTS_ONLY = ("dig",)` before running `title_shots.py`.

Then:

```bash
python tools/blender/export_to_app.py            # everything (about 15 s)
python tools/blender/export_to_app.py --frames   # only animation and effect frames
```

`git status` should show no changes to the existing images if your render matches; then you're set up.

### Changing an asset

1. Edit the script (for example `room_farm.py` or a character in `anim_sprites.py`).
2. Run that script in Blender (with `BL_DIR` set as above), look at the render, adjust.
3. Run `export_to_app.py`, build, check it in the game.
4. Write in your fork notes which script you changed and which images were regenerated.

Gotchas (more in `docs/handoff.md`):
- Each script builds its own scene. Re-run the script you're rendering; don't render an old scene left in a saved file.
- Materials are shared by name across scenes (`base_materials()` in `common.py`).
- Keep emission strengths low (about 1.0 to 1.3) or colours burn out to white.
- Object positions in the game depend on the renders: the bunker deck height, the work zones in the rooms, the turret dome. If you change those renders, check `GameActivity` (`DECK_Y`, `GUARD_SLOTS`, `DOME_Y`) and `FloorAdapter` (`HEAP_X`, `TABLES_X`).

## 5. Sound effects and music

Both are generated from code. Edit the script, run it, rebuild:

```bash
python tools/audio/gen_sfx.py     # 13 effects -> app/src/main/res/raw/sfx_*.ogg
python tools/audio/gen_music.py   # menu, gameplay, boss loops -> res/raw/music_*.ogg (about 40 s)
```

Effects are loudness-balanced in `gen_sfx.py`; per-sound volume is in `ui/Sfx.kt`. The music is written as notes (`(beat, length, MIDI note)`) in `gen_music.py`; each loop is seamless. Phone speakers barely play bass, so keep melodies and mid-range parts up front, and listen on a phone, not just headphones.

## 6. Interface drawables and tweens

```bash
python tools/art/gen_ui.py    # 9-patch panels, buttons, tab rings, tween animations
python tools/art/gen_art.py   # small vector icons
python tools/art/make_readme_images.py [screenshot folder]   # README banner and screenshots
```

These overwrite their outputs, so edit the scripts, not the generated files.

## 7. Testing tips

- **Reach a late-game state quickly** on the emulator by editing the save. Stop the app, copy the database out, edit it, push it back (piping it through `adb shell` corrupts it; use `adb push`):
  ```bash
  adb -s emulator-5554 shell am force-stop com.deepcell.game
  adb -s emulator-5554 shell "run-as com.deepcell.game cp databases/deepcell.db /data/local/tmp/dc.db"
  adb -s emulator-5554 pull /data/local/tmp/dc.db
  # edit dc.db with Python's sqlite3, e.g. UPDATE game_state SET wave=10, food=300
  adb -s emulator-5554 push dc.db /data/local/tmp/dc.db
  adb -s emulator-5554 shell "run-as com.deepcell.game sh -c 'cat /data/local/tmp/dc.db > databases/deepcell.db'"
  ```
  (On Git Bash, set `MSYS_NO_PATHCONV=1` first so the `/data/...` paths aren't rewritten.)
- Don't fire many `adb` commands in parallel or screenshot in a tight loop; it can freeze the emulator's System UI.
- An emulator started with `-no-snapshot-save` forgets app data when restarted.
- Check for crashes after every change: `adb -s emulator-5554 logcat -d -b crash`.
- Record each build in `docs/testing.md`: what you checked, on which device, and what you didn't check.

## 8. Before you push

- `./gradlew assembleDebug` succeeds.
- The screens you changed were opened and look right.
- Docs and your `docs/forks/<you>.md` are updated.
- No personal paths, keys or passwords in the files (`local.properties` is ignored by git).
