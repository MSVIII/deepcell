# Forking Deepcell

Each groupmate makes their own version of the game in their own fork. **You only fork and build your version.** When everyone is done, Yauren combines the forks into the final game; you don't merge anything yourself.

Base repository: **https://github.com/Yauren/deepcell**
Every fork starts from the tag **`fork-base`**; all versions are compared against it.

## The easy way: let your AI set it up

Open **Codex** (or ChatGPT, Claude Code, or another AI coding assistant that can run commands on your PC), start a new conversation, and paste the prompt below. Codex also reads `AGENTS.md` by itself once the project is on your PC.

The first conversation only sets things up and explains the game. Say what you want to build in a later message.

```text
Help me set up my fork of Deepcell, an Android game for our Mobile Programming group
project, and explain it to me. Base repository: https://github.com/Yauren/deepcell
(tag `fork-base` is where every groupmate's fork starts).

In this first conversation, only do the setup and give me the guides below. Don't change
any game code yet; I'll tell you what I want to build afterwards.

1. Get the project onto my Desktop
   - Check that git is installed. If the GitHub CLI (gh) is installed and signed in
     (or I can sign in when you run `gh auth login`), fork and clone in one step from my
     Desktop folder: `gh repo fork Yauren/deepcell --clone`. Otherwise ask me to press
     "Fork" on the GitHub page, then clone my fork to my Desktop with git.
   - The project must end up in a folder named `deepcell` on my Desktop. Show me the
     full path.
   - Make sure `origin` points to MY fork and add the base repository as `upstream`
     (read-only for me). Never push to Yauren/deepcell.

2. Read the project
   - Read AGENTS.md, README.md, FORKING.md, docs/workflow.md, docs/handoff.md,
     docs/design.md, docs/module-map.md and docs/roadmap.md.

3. Give me a proper overview, in plain words
   - What the game is: the story, how a round plays, the screens, enemies and waves,
     rooms, survivors and jobs, food and upkeep, upgrades, the tutorial.
   - How the project is built: Kotlin + XML Android app, which file does what, where the
     balance numbers are (assets/*.json), where text is (strings.xml), how the art and
     sounds are made from scripts in tools/.
   - The rules from AGENTS.md: only the course modules, no new libraries, never wipe
     player saves, keep the docs accurate.

4. Give me the guides I need (docs/workflow.md has the details)
   - How to open the project in Android Studio and run it on my phone or an emulator,
     and how to build it from the command line.
   - Which tools I need for what (Android Studio for code; Python, ffmpeg, Blender and the
     Blender MCP for art and sound). Check which ones are already installed on my PC and
     offer to install the missing ones; ask me before installing anything.
   - How to connect you to Blender with the Blender MCP (docs/workflow.md, section 4), so
     you can render art for me. Offer to set it up now or later.
   - How to ask you for changes, with three example requests that fit this game.
   - How my changes get saved and shared (see "From now on" below).
   - What I must write in docs/forks/<my-github-username>.md and why.
   - Create docs/forks/<my-github-username>.md from docs/forks/TEMPLATE.md, commit it
     and push it to my fork, so the whole setup is checked once.

From now on, in every later conversation:
- Work in the deepcell folder on my Desktop and follow AGENTS.md exactly.
- Keep changes additive: don't move, rename or reformat existing files; add new files for
  new features where it makes sense. Balance numbers go in app/src/main/assets/*.json,
  text in strings.xml.
- After each finished change: run `gradlew assembleDebug`, update docs/forks/<my-username>.md
  and the docs in docs/ (design, roadmap, decisions, testing), then commit with a clear
  message (one feature or fix per commit) and push to my fork (`origin`) automatically.
  Don't ask me before committing and pushing to my fork.
- Never push to the base repository, never force-push, never rewrite the history that came
  from the base.
- If I add a database column: bump DB_VERSION, add a non-destructive `if (oldVersion < N)`
  step in GameDatabase.onUpgrade, and note it in my fork notes.
- Ask me first before adding any dependency, removing a feature from the base, or changing
  the save format in a way that loses data.
- Don't claim something was tested on a phone unless it was.
```

## Doing it by hand

1. On GitHub, open the base repository and press **Fork** (keep the name `deepcell`).
2. Clone your fork to your Desktop and open the folder in Android Studio (build steps are in the README).
3. Build once and run it before you change anything.
4. Copy `docs/forks/TEMPLATE.md` to `docs/forks/<your-github-username>.md`.
5. For art, sound or music changes, set up the tools in [`docs/workflow.md`](docs/workflow.md) (Python, ffmpeg, Blender and the Blender MCP).

## Rules for your fork

These are what make combining the forks possible:

- **Follow `AGENTS.md`.** Course modules only, Kotlin + XML, no new libraries, no filler text in the UI.
- **Write down what you changed** in `docs/forks/<your-github-username>.md`. It's the first thing read when the forks are combined.
- **Small commits with clear messages**, one idea per commit ("Add Lift between floors", not "update"). Push them to your fork. Don't squash, force-push or rewrite the history that came from the base.
- **Don't move, rename or reformat existing files.** Add new files for new things where you can. Reformatting a whole file makes every line look changed and hides your real work.
- **Balance numbers go in `app/src/main/assets/*.json`, text in `strings.xml`.** Never hard-code them.
- **Saves:** never drop tables in `GameDatabase.onUpgrade`. If you add a column, add a new `if (oldVersion < N)` step, bump `DB_VERSION`, and write it in your fork notes. Several forks using version 4 is fine; it gets sorted out when combining.
- **Assets:** change art or sound by editing the scripts in `tools/` and re-running them, and say which outputs you regenerated. Don't hand-edit exported images or sounds.
- **Keep the docs true** (`docs/design.md`, `docs/roadmap.md`, `docs/testing.md`, ...) and say plainly what you didn't test.

## When you're done

1. Check that everything is pushed and `docs/forks/<your-username>.md` is complete.
2. Make sure your fork builds from a fresh clone.
3. Send the link to your fork to Yauren.
