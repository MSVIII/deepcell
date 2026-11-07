# Forking Deepcell

Each groupmate forks this repository and makes their own version of the game. **You only fork and build your version.** When everyone is done, Yauren combines the forks into the final game. You don't merge anything yourself. These rules make that combining possible, so please follow them.

Base repository: **https://github.com/Yauren/deepcell**
Every fork starts from the tag **`fork-base`**; all versions are compared against it.

## 1. Fork and open it

1. On GitHub, open the base repository and press **Fork** (keep the name `deepcell`).
2. Clone your fork and open the folder in Android Studio (build steps are in the README).
3. Build once and run it on a phone or emulator before you change anything.

## 2. Rules for your fork

- **Follow `AGENTS.md`.** Course modules only, Kotlin + XML, no new libraries, no filler text in the UI.
- **Write down what you changed** in `docs/forks/<your-github-username>.md` (copy `docs/forks/TEMPLATE.md`). Keep it up to date as you go; it's the first thing read when the forks are combined.
- **Small commits with clear messages**, one idea per commit ("Add Lift between floors", not "update"). Don't squash or rewrite the history that came from the base.
- **Don't move, rename or reformat existing files.** Add new files for new things where you can. Reformatting a whole file makes every line look changed and hides your real work.
- **Balance numbers go in `app/src/main/assets/*.json`, text in `strings.xml`.** Never hard-code them.
- **Saves:** never drop tables in `GameDatabase.onUpgrade`. If you add a column, add a new `if (oldVersion < N)` step, bump `DB_VERSION`, and write it in your fork notes. Several forks using version 4 is fine; it gets sorted out when combining.
- **Assets:** change art or sound by editing the scripts in `tools/` and re-running them, and say which outputs you regenerated. Don't hand-edit exported images or sounds.
- **Keep the docs true** (`docs/design.md`, `docs/roadmap.md`, `docs/testing.md`, ...) for what you change, and say plainly what you didn't test.

## 3. Prompt for your AI assistant

If you use an AI coding assistant, start its first session in your fork's folder with this prompt (fill in the two blanks):

```text
You are working on my fork of Deepcell, an Android game for our Mobile Programming group
project. My GitHub username is <your-username>. The base repository is
https://github.com/Yauren/deepcell and my fork started from its tag `fork-base`.
My fork will later be combined with my groupmates' forks by someone else, so I only
need to build my own version here; don't try to merge other forks.

Before changing anything, read AGENTS.md, README.md, FORKING.md, docs/handoff.md,
docs/design.md and docs/module-map.md. Follow AGENTS.md exactly: only the course modules,
Kotlin + XML, no new libraries, no filler text in the UI, never drop tables in
GameDatabase.onUpgrade.

What I want to build in my version: <describe your ideas here>.

How to work, so my fork is easy to combine later:
- Keep changes additive. Don't move, rename or reformat existing files; add new files
  for new features where it makes sense.
- Put balance numbers in app/src/main/assets/*.json and all text in strings.xml.
- Commit in small steps with clear messages, one feature or fix per commit.
- Keep docs/forks/<your-username>.md up to date (start from docs/forks/TEMPLATE.md):
  every feature, every balance change, every database change, every regenerated asset,
  and what was and wasn't tested.
- Update docs/design.md, docs/roadmap.md, docs/decisions.md and docs/testing.md for
  each change.
- Run gradlew assembleDebug after code changes and record the result in docs/testing.md.
  Don't claim something was tested on a phone unless it was.
- Ask me before adding any dependency, deleting features from the base, or changing the
  save format in a way that loses data.
```

## 4. When you're done

1. Push everything to your fork and check that `docs/forks/<your-username>.md` is complete.
2. Make sure your fork builds from a fresh clone.
3. Send the link to your fork to Yauren.
