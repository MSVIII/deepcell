# Fork notes: MSVIII

Fork: https://github.com/MSVIII/deepcell
Started from: `fork-base` (`d814c79ba6132058e5b96e633ee1c6a936f30963`)

## What I added or changed

| Change | Files | Notes |
|---|---|---|
| Document initial fork setup | `docs/forks/MSVIII.md` | 2026-11-10: cloned the personal fork, verified the starting commit, configured origin and upstream, and read the onboarding guides. No game code changed. |

Local setup: `origin` is this fork. `upstream` fetches from Yauren/deepcell and has its push URL disabled. The local Android SDK path is in ignored `local.properties`; personal paths are not committed. Android Studio's generated daemon JVM settings are ignored locally as well.

## Balance changes

None. The base balance files are unchanged.

## Database changes

None. No tables, columns, database version or save migration changed.

## Assets

None. No generation scripts or exported assets changed. At the user's request, installed Blender 5.2.4 LTS, uv 0.13.7, ffmpeg 9.0.2, and a dedicated Windows Python 3.12.16 environment with Pillow 13.0.0, NumPy 2.5.4 and SciPy 1.18.1. Installed and enabled MCP for Blender (add-on protocol 15) and configured the local Codex connection. No art or sound was regenerated.

## Removed from the base

None.

## Tested

- Verified that the GitHub repository is a fork of Yauren/deepcell and the initial checkout matches `fork-base`.
- Checked Git, Android Studio, Java, the Android SDK and Python availability.
- Baseline build: **BUILD SUCCESSFUL** on 2026-11-10 with Gradle 9.6.0, AGP 9.4.1, JDK 21 and Android SDK 37. Command: `gradlew.bat --no-daemon '-Pandroid.builder.sdkDownload=false' assembleDebug`. Existing declared dependencies were downloaded; no game dependency declarations changed. APK produced at `app/build/outputs/apk/debug/app-debug.apk`.
- Imported Pillow, NumPy and SciPy successfully; verified ffmpeg exposes the libvorbis OGG encoder. The Blender MCP server connected to Blender 5.2.4 LTS and verified add-on protocol 15. Codex needs a restart to load its new MCP configuration.
- No phone or emulator play test has been performed during this setup. No asset renders, audio listening checks or save migration tests have been performed.

## Documentation observations

Some older design, handoff and roadmap sections conflict with later entries and the code. Food upkeep, Sprinkler, Repair Arm and music already exist. Workers also contribute to offline room progress while their food lasts; machines do not consume food. Those base documents were left unchanged during onboarding.
